"""Isolated PNG/JPEG-to-RGBA experiment. Caller authenticates encoded resources.

Limits are explicit local policy, not wire limits. CPU/output/wall enforcement
and a resident watchdog do not constitute a sandbox. Output excludes metadata.
"""
from dataclasses import asdict,dataclass
import json
from pathlib import Path
import sys
import io
from parser_process import ParserLimits,ParserFailure,run_parser,install_worker_limits

class DecodeError(ValueError):pass

@dataclass(frozen=True)
class DecodeLimits:
    max_encoded:int
    max_width:int
    max_height:int
    max_pixels:int
    max_output:int
    timeout_seconds:float
    cpu_seconds:int=3
    max_resident:int=268435456
    sample_seconds:float=0.02
    require_hard_memory:bool=False
    max_metadata:int=1048576
    def process_limits(self):
        return ParserLimits(wall_seconds=self.timeout_seconds,cpu_seconds=self.cpu_seconds,max_output=self.max_output+128,max_resident=self.max_resident,sample_seconds=self.sample_seconds,require_hard_memory=self.require_hard_memory)
    def validate(self):
        for key in ('max_encoded','max_width','max_height','max_pixels','max_output','max_metadata'):
            value=getattr(self,key)
            if type(value) is not int or value<=0:raise ValueError('Positive local integer limits required')
        import math
        if type(self.timeout_seconds) not in (int,float) or not math.isfinite(self.timeout_seconds) or self.timeout_seconds<=0:
            raise ValueError('Positive finite wall timeout required')
        self.process_limits().validate()

@dataclass(frozen=True)
class Pixels:
    width:int
    height:int
    rgba:bytes

def decode_image(encoded,media_type,limits):
    """Accept authenticated encoded bytes and return tightly packed RGBA8 pixels."""
    if not isinstance(limits,DecodeLimits):raise ValueError('Explicit limits required')
    limits.validate()
    if not isinstance(encoded,bytes) or len(encoded)>limits.max_encoded:raise DecodeError('encoded-size')
    if media_type not in ('image/png','image/jpeg'):raise DecodeError('unsupported-media-type')
    try:
        result=run_parser([sys.executable,str(Path(__file__).resolve()),'--worker',media_type,json.dumps(asdict(limits))],encoded,limits.process_limits())
    except ParserFailure as error:
        reason='decoder-timeout' if str(error)=='parser-timeout' else 'decoder-rejected'
        raise DecodeError(reason) from None
    output=io.BytesIO(result);header=output.readline(128)
    try:width,height=json.loads(header)
    except (ValueError,TypeError):raise DecodeError('invalid-worker-result') from None
    rgba=output.read(limits.max_output+1)
    if (type(width)is not int or type(height)is not int or not 0<width<=limits.max_width
        or not 0<height<=limits.max_height or width*height>limits.max_pixels
        or len(rgba)!=width*height*4 or len(rgba)>limits.max_output):raise DecodeError('invalid-worker-result')
    return Pixels(width,height,rgba)

def _size(width,height,limits):
    if (not 0<width<=limits.max_width or not 0<height<=limits.max_height
        or width*height>limits.max_pixels or width*height*4>limits.max_output):
        raise DecodeError('decoded-size')


def _inflate(data,bound,*,exact=None):
    """Bound expansion before allocation; reject extra streams and missing checksum."""
    import zlib
    if bound<0:raise DecodeError('metadata-size')
    decoder=zlib.decompressobj()
    value=decoder.decompress(data,bound+1)
    if len(value)>bound or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:
        raise DecodeError('compressed-data')
    if exact is not None and len(value)!=exact:raise DecodeError('scanline-size')
    return value


def _orientation(data):
    """Read primary TIFF Orientation; never borrow the thumbnail's orientation.

    Bound primary/next IFD tables and value ranges. Other camera metadata and
    sub-IFD payload semantics are not interpreted or exported.
    """
    import struct
    if len(data)<8 or data[:2]not in (b'II',b'MM'):raise DecodeError('exif-header')
    order='<' if data[:2]==b'II' else '>'
    def integer(at,size):
        if at<0 or at+size>len(data):raise DecodeError('exif-offset')
        return int.from_bytes(data[at:at+size],'little' if order=='<' else 'big')
    if integer(2,2)!=42:raise DecodeError('exif-header')
    offset=integer(4,4);seen=set();orientation=None;color=None;primary=True;exif_pointer_seen=False
    # Exif3.1 UTF-8 (129) is a byte-counted field, including unused camera
    # descriptions. Bound its storage without treating it as orientation.
    sizes={1:1,2:1,3:2,4:4,5:8,6:1,7:1,8:2,9:4,10:8,11:4,12:8,13:4,129:1}
    if not offset:raise DecodeError('exif-offset')
    def entries(offset):
        if offset<8:raise DecodeError('exif-offset')
        count=integer(offset,2);end=offset+2+count*12
        if end+4>len(data):raise DecodeError('exif-ifd')
        values=[]
        for at in range(offset+2,end,12):
            tag,kind,count=struct.unpack(order+'HHI',data[at:at+8])
            if kind not in sizes:raise DecodeError('exif-type')
            length=sizes[kind]*count;start=at+8 if length<=4 else integer(at+8,4)
            if start+length>len(data):raise DecodeError('exif-value')
            values.append((tag,kind,count,start))
        return values,integer(end,4)
    while offset:
        if offset in seen:raise DecodeError('exif-cycle')
        seen.add(offset);values,next_offset=entries(offset)
        for tag,kind,count,start in values:
            if primary and tag==274:
                if orientation is not None or kind!=3 or count!=1:raise DecodeError('exif-orientation')
                orientation=integer(start,2)
                if orientation not in range(1,9):raise DecodeError('exif-orientation')
            if primary and tag==34665:
                if exif_pointer_seen or kind!=4 or count!=1:raise DecodeError('exif-subifd')
                exif_pointer_seen=True
                exif_offset=integer(start,4)
                if exif_offset in seen:raise DecodeError('exif-cycle')
                for subtag,subkind,subcount,substart in entries(exif_offset)[0]:
                    if subtag==40961:
                        if color is not None or subkind!=3 or subcount!=1:raise DecodeError('exif-colorspace')
                        color=integer(substart,2)
        offset=next_offset;primary=False
    return orientation or 1,color


def _png_structure(encoded,limits):
    """Validate immutable input before PyPNG's unbounded internal inflate.

    Exact filtered byte counts include every Adam7 pass. A first bounded zlib
    pass validates the checksum, stream termination and expansion; PyPNG then
    reconstructs the same bytes. CPU/resident/wall bounds cover both passes.
    """
    import struct,zlib
    if encoded[:8]!=b'\x89PNG\r\n\x1a\n':raise DecodeError('png-signature')
    offset=8;chunks={};idat=[];phase=0;metadata=0
    single={b'IHDR',b'PLTE',b'IEND',b'tRNS',b'cHRM',b'gAMA',b'iCCP',b'sRGB',b'cICP',b'eXIf',b'sBIT'}
    before_palette={b'cHRM',b'gAMA',b'iCCP',b'sRGB',b'cICP',b'sBIT'}
    while offset+12<=len(encoded):
        length=int.from_bytes(encoded[offset:offset+4],'big');kind=encoded[offset+4:offset+8]
        end=offset+12+length
        if length>2147483647 or end>len(encoded):raise DecodeError('png-truncated')
        if any(not(65<=v<=90 or 97<=v<=122)for v in kind)or kind[2]&32:raise DecodeError('png-chunk-name')
        data=encoded[offset+8:end-4]
        if zlib.crc32(kind+data)!=int.from_bytes(encoded[end-4:end],'big'):raise DecodeError('png-crc')
        if kind in (b'acTL',b'fcTL',b'fdAT'):raise DecodeError('animation')
        if not chunks and kind!=b'IHDR':raise DecodeError('png-header')
        if not kind[0]&32 and kind not in (b'IHDR',b'PLTE',b'IDAT',b'IEND'):raise DecodeError('png-critical')
        if kind in single and kind in chunks:raise DecodeError('png-duplicate')
        if kind in before_palette and (b'PLTE'in chunks or phase):raise DecodeError('png-order')
        if kind in (b'PLTE',b'tRNS')and phase:raise DecodeError('png-order')
        if kind==b'tRNS' and len(chunks.get(b'IHDR',b''))==13 and chunks[b'IHDR'][9]==3 and b'PLTE'not in chunks:raise DecodeError('png-order')
        if kind[0]&32:
            metadata+=length
            if metadata>limits.max_metadata:raise DecodeError('metadata-size')
        if kind==b'IDAT':
            if phase==2:raise DecodeError('png-idat-order')
            phase=1;idat.append(data)
        elif phase==1:phase=2
        chunks[kind]=data
        if kind==b'IEND':
            if length or end!=len(encoded)or not idat:raise DecodeError('png-end')
            break
        offset=end
    else:raise DecodeError('png-end')
    if len(chunks[b'IHDR'])!=13:raise DecodeError('png-header')
    width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',chunks[b'IHDR'])
    _size(width,height,limits)
    depths={0:(1,2,4,8,16),2:(8,16),3:(1,2,4,8),4:(8,16),6:(8,16)}
    if depth not in depths.get(color,())or compression or filtering or interlace not in(0,1):raise DecodeError('png-format')
    palette=chunks.get(b'PLTE')
    if palette is not None and (not len(palette)or len(palette)%3 or len(palette)>768 or color in(0,4)
        or color==3 and len(palette)//3>2**depth):raise DecodeError('png-palette')
    if color==3 and palette is None:raise DecodeError('png-palette')
    transparent=chunks.get(b'tRNS')
    if transparent is not None:
        if color==3:
            if not transparent or len(transparent)>len(palette)//3:raise DecodeError('png-transparency')
        elif color in(0,2):
            if len(transparent)!=(2 if color==0 else 6):raise DecodeError('png-transparency')
            if any(v>=2**depth for v in struct.unpack('>'+('H'if color==0 else'3H'),transparent)):raise DecodeError('png-transparency')
        else:raise DecodeError('png-transparency')
    if b'sBIT'in chunks:
        significant=chunks[b'sBIT'];count={0:1,2:3,3:3,4:2,6:4}[color]
        if len(significant)!=count or any(not 0<v<=(8 if color==3 else depth)for v in significant):raise DecodeError('png-significant-bits')
    planes={0:1,2:3,3:1,4:2,6:4}[color];expected=0
    passes=((0,0,1,1),)if not interlace else((0,0,8,8),(4,0,8,8),(0,4,4,8),(2,0,4,4),(0,2,2,4),(1,0,2,2),(0,1,1,2))
    for x,y,dx,dy in passes:
        w=max(0,(width-x+dx-1)//dx);h=max(0,(height-y+dy-1)//dy)
        if w and h:expected+=h*(1+(w*planes*depth+7)//8)
    _inflate(b''.join(idat),expected,exact=expected)
    if b'cICP'in chunks:raise DecodeError('unsupported-color-description')
    if b'sRGB'in chunks:
        if chunks[b'sRGB']not in(b'\0',b'\1',b'\2',b'\3')or b'iCCP'in chunks:raise DecodeError('png-colorspace')
        if b'gAMA'in chunks and chunks[b'gAMA']!=struct.pack('>I',45455):raise DecodeError('png-colorspace')
        if b'cHRM'in chunks and chunks[b'cHRM']!=struct.pack('>8I',31270,32900,64000,33000,30000,60000,15000,6000):raise DecodeError('png-colorspace')
    gamma=None;chroma=None;icc=None
    if b'gAMA'in chunks:
        if len(chunks[b'gAMA'])!=4:raise DecodeError('png-gamma')
        gamma=int.from_bytes(chunks[b'gAMA'],'big')/100000
        if not gamma:raise DecodeError('png-gamma')
    if b'cHRM'in chunks:
        if len(chunks[b'cHRM'])!=32:raise DecodeError('png-chromaticity')
        chroma=[v/100000 for v in struct.unpack('>8I',chunks[b'cHRM'])]
        if any(not 0<=x<=1 or not 0<y<=1 or x+y>1.00001 for x,y in zip(chroma[::2],chroma[1::2])):raise DecodeError('png-chromaticity')
    if b'iCCP'in chunks:
        value=chunks[b'iCCP'];split=value.find(b'\0')
        if not 1<=split<=79 or value[split+1:split+2]!=b'\0':raise DecodeError('png-icc')
        name=value[:split]
        if name.startswith(b' ')or name.endswith(b' ')or b'  'in name or any(not(32<=v<=126 or 161<=v<=255)for v in name):raise DecodeError('png-icc-name')
        icc=_inflate(value[split+2:],limits.max_metadata-metadata)
    orientation,_=_orientation(chunks[b'eXIf'])if b'eXIf'in chunks else(1,None)
    return width,height,depth,color,chunks,icc,gamma,chroma,orientation


def _jpeg_structure(encoded,limits):
    """Bound marker metadata and assemble ICC only from a complete segment set."""
    if not encoded.startswith(b'\xff\xd8')or not encoded.endswith(b'\xff\xd9'):raise DecodeError('jpeg-end')
    pos=2;icc={};total=None;orientation=1;exif_seen=False;metadata=0;color=None;frame=None;jfif=False;adobe=None
    while pos<len(encoded):
        if encoded[pos]!=255:raise DecodeError('jpeg-marker')
        while pos<len(encoded)and encoded[pos]==255:pos+=1
        if pos==len(encoded):raise DecodeError('jpeg-marker')
        marker=encoded[pos];pos+=1
        if marker==217:
            if pos!=len(encoded)or frame is None:raise DecodeError('jpeg-end')
            break
        if marker in(0,216)or 208<=marker<=215:raise DecodeError('jpeg-marker')
        if pos+2>len(encoded):raise DecodeError('jpeg-segment')
        size=int.from_bytes(encoded[pos:pos+2],'big');end=pos+size
        if size<2 or end>len(encoded):raise DecodeError('jpeg-segment')
        data=encoded[pos+2:end];pos=end
        if 224<=marker<=239 or marker==254:
            metadata+=len(data)
            if metadata>limits.max_metadata:raise DecodeError('metadata-size')
        if marker in(192,193,194,195,197,198,199,201,202,203,205,206,207):
            if frame is not None or marker not in(192,194)or len(data)<6 or data[0]!=8 or data[5]not in(1,3)or len(data)!=6+3*data[5]:raise DecodeError('unsupported-jpeg-process')
            frame=(int.from_bytes(data[3:5],'big'),int.from_bytes(data[1:3],'big'),data[5]);_size(frame[0],frame[1],limits)
        if marker==224 and data.startswith(b'JFIF\0'):
            if jfif or len(data)<14 or data[5]!=1 or data[7]>2 or not int.from_bytes(data[8:10],'big')or not int.from_bytes(data[10:12],'big')or len(data)!=14+3*data[12]*data[13]:raise DecodeError('jpeg-jfif')
            jfif=True
        if marker==225 and data.startswith(b'Exif\0\0'):
            if exif_seen:raise DecodeError('exif-duplicate')
            orientation,color=_orientation(data[6:]);exif_seen=True
        if marker==238 and data.startswith(b'Adobe'):
            if adobe is not None or len(data)!=12:raise DecodeError('jpeg-adobe')
            adobe=data[11]
        if marker==226 and data.startswith(b'ICC_PROFILE\0'):
            if len(data)<14:raise DecodeError('jpeg-icc')
            sequence,count=data[12:14]
            if not 1<=sequence<=count or total is not None and total!=count or sequence in icc:raise DecodeError('jpeg-icc')
            total=count;icc[sequence]=data[14:]
        if marker==218:
            # Entropy bytes use FF00 stuffing and standalone restart markers.
            while pos<len(encoded):
                if encoded[pos]!=255:pos+=1;continue
                start=pos
                while pos<len(encoded)and encoded[pos]==255:pos+=1
                if pos==len(encoded):raise DecodeError('jpeg-entropy')
                if encoded[pos]==0 or 208<=encoded[pos]<=215:pos+=1;continue
                pos=start;break
    else:raise DecodeError('jpeg-end')
    if total is not None and set(icc)!=set(range(1,total+1)):raise DecodeError('jpeg-icc')
    if adobe not in(None,0,1)or jfif and adobe==0 and frame[2]==3:raise DecodeError('jpeg-component-color')
    profile=b''.join(icc[i]for i in range(1,(total or 0)+1))or None
    if profile is None and color not in(None,1,65535):raise DecodeError('unsupported-exif-color')
    return orientation,profile


def _managed(image,icc,gamma=None,chroma=None,*,srgb=False):
    """Public ImageCms path: full-precision transparency, then SDR8 quantization.

    PNG samples are rescaled before this transform. This loses precision and may
    band; it does not claim 16-bit CMS or print/proof fidelity. Alpha is separate.
    """
    from PIL import Image,ImageCms
    import struct,math
    if icc is not None:
        if len(icc)<132 or int.from_bytes(icc[:4],'big')!=len(icc)or icc[36:40]!=b'acsp' or icc[8]not in(2,4):raise DecodeError('icc-header')
        if icc[12:16]not in(b'scnr',b'mntr')or icc[16:20]not in(b'RGB ',b'GRAY')or icc[20:24]not in(b'XYZ ',b'Lab '):raise DecodeError('unsupported-icc')
        count=int.from_bytes(icc[128:132],'big')
        if 132+12*count>len(icc):raise DecodeError('icc-tags')
        seen=set()
        for at in range(132,132+12*count,12):
            tag=icc[at:at+4];offset,size=struct.unpack('>II',icc[at+4:at+12])
            if tag in seen or offset<132+12*count or offset%4 or size<8 or offset+size>len(icc):raise DecodeError('icc-tags')
            seen.add(tag)
        if b'ADGC'in seen:raise DecodeError('unsupported-adaptive-gain-profile')
        # A valid profile cannot authorize applying an RGB transform to gray
        # samples or the converse. Both common spaces use their native input.
        gray=icc[16:20]==b'GRAY'
        if gray and image.mode!='L' or not gray and image.mode!='RGB':raise DecodeError('icc-colorspace')
        source=ImageCms.ImageCmsProfile(io.BytesIO(icc))
        intent=int.from_bytes(icc[64:68],'big')
        if intent>3:raise DecodeError('icc-intent')
        return ImageCms.profileToProfile(image,source,ImageCms.createProfile('sRGB'),renderingIntent=intent,outputMode='RGB')
    if srgb or gamma is None and chroma is None:return image.convert('RGB')
    # gAMA is the source encoding exponent: linear light = sample**(1/gAMA).
    # cHRM maps source linear primaries through XYZ, Bradford-adapting its white
    # point to D65; absent chromaticity means sRGB primaries. A cHRM-only image
    # uses the sRGB transfer curve. No alpha sample enters these calculations.
    def inverse(m):
        a,b,c=m[0];d,e,f=m[1];g,h,i=m[2]
        determinant=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
        if not math.isfinite(determinant)or abs(determinant)<1e-12:raise DecodeError('png-chromaticity')
        return [[(e*i-f*h)/determinant,(c*h-b*i)/determinant,(b*f-c*e)/determinant],[(f*g-d*i)/determinant,(a*i-c*g)/determinant,(c*d-a*f)/determinant],[(d*h-e*g)/determinant,(b*g-a*h)/determinant,(a*e-b*d)/determinant]]
    def mul(m,v):return [sum(a*b for a,b in zip(row,v))for row in m]
    def xyz(x,y):return [x/y,1,(1-x-y)/y]
    to_srgb=[[3.2404542,-1.5371385,-0.4985314],[-0.9692660,1.8760108,0.0415560],[0.0556434,-0.2040259,1.0572252]]
    adaptation=None;matrix=None
    if chroma is not None:
        white=xyz(*chroma[:2]);columns=[xyz(*chroma[i:i+2])for i in(2,4,6)]
        matrix=list(map(list,zip(*columns)));scales=mul(inverse(matrix),white)
        matrix=[[v*scales[i]for i,v in enumerate(row)]for row in matrix]
        bradford=[[.8951,.2664,-.1614],[-.7502,1.7135,.0367],[.0389,-.0685,1.0296]]
        old=mul(bradford,white);new=mul(bradford,xyz(.3127,.3290))
        if any(abs(v)<1e-12 for v in old):raise DecodeError('png-chromaticity')
        adaptation=(bradford,inverse(bradford),[n/o for n,o in zip(new,old)])
    output=bytearray()
    for pixel in image.convert('RGB').getdata():
        rgb=[v/255 for v in pixel]
        rgb=[v**(1/gamma)if gamma is not None else(v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4)for v in rgb]
        if matrix is not None:
            value=mul(matrix,rgb);forward,back,ratios=adaptation
            value=mul(back,[v*r for v,r in zip(mul(forward,value),ratios)])
            rgb=mul(to_srgb,value)
        for v in rgb:
            v=max(0,min(1,v));encoded=12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
            output.append(max(0,min(255,int(encoded*255+.5))))
    return Image.frombytes('RGB',image.size,bytes(output))


def _decode(encoded,media_type,limits):
    from PIL import Image,ImageFile
    import struct,warnings
    ImageFile.LOAD_TRUNCATED_IMAGES=False
    Image.MAX_IMAGE_PIXELS=limits.max_pixels
    if media_type=='image/png':
        import png
        width,height,depth,color,chunks,icc,gamma,chroma,orientation=_png_structure(encoded,limits)
        reader=png.Reader(bytes=encoded);w,h,rows,info=reader.read()
        if (w,h)!=(width,height):raise DecodeError('png-size')
        planes=info['planes'];maximum=2**depth-1;rgb=bytearray();alpha=bytearray();row_count=0
        palette=chunks.get(b'PLTE');transparent=chunks.get(b'tRNS')
        key=struct.unpack('>'+('H'if color==0 else'3H'),transparent)if transparent is not None and color in(0,2)else None
        gray=color in(0,4)
        def scale(v):return (v*255+maximum//2)//maximum
        for row in rows:
            row_count+=1
            if len(row)!=width*planes or row_count>height:raise DecodeError('png-row-size')
            for at in range(0,len(row),planes):
                value=tuple(row[at:at+planes])
                if color==3:
                    index=value[0]
                    if index>=len(palette)//3:raise DecodeError('png-palette-index')
                    rgb.extend(palette[index*3:index*3+3]);alpha.append(transparent[index]if transparent is not None and index<len(transparent)else 255)
                else:
                    count=1 if gray else 3;rgb.extend(scale(v)for v in value[:count])
                    alpha.append(scale(value[-1])if color in(4,6)else(0 if key==value else 255))
        if row_count!=height:raise DecodeError('png-row-size')
        image=Image.frombytes('L'if gray else'RGB',(width,height),bytes(rgb))
        managed=_managed(image,icc,gamma,chroma,srgb=b'sRGB'in chunks)
        managed.putalpha(Image.frombytes('L',(width,height),bytes(alpha)))
    else:
        orientation,icc=_jpeg_structure(encoded,limits)
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(encoded),formats=['JPEG'])as image:
                if image.format!='JPEG' or image.mode not in('L','RGB'):raise DecodeError('format-mismatch')
                _size(image.width,image.height,limits);image.load()
                managed=_managed(image,icc).convert('RGBA')
    transforms={2:Image.Transpose.FLIP_LEFT_RIGHT,3:Image.Transpose.ROTATE_180,4:Image.Transpose.FLIP_TOP_BOTTOM,5:Image.Transpose.TRANSPOSE,6:Image.Transpose.ROTATE_270,7:Image.Transpose.TRANSVERSE,8:Image.Transpose.ROTATE_90}
    if orientation!=1:managed=managed.transpose(transforms[orientation])
    _size(managed.width,managed.height,limits)
    return Pixels(managed.width,managed.height,managed.tobytes())

if __name__=='__main__':
    try:
        if len(sys.argv)!=4 or sys.argv[1]!='--worker':raise DecodeError('worker-arguments')
        limits=DecodeLimits(**json.loads(sys.argv[3]));limits.validate()
        install_worker_limits(limits.process_limits())
        encoded=sys.stdin.buffer.read(limits.max_encoded+1)
        if len(encoded)>limits.max_encoded:raise DecodeError('encoded-size')
        pixels=_decode(encoded,sys.argv[2],limits)
        header=json.dumps([pixels.width,pixels.height],separators=(',',':')).encode()+b'\n'
        if len(header)>128 or len(pixels.rgba)>limits.max_output:raise DecodeError('output-size')
        sys.stdout.buffer.write(header);sys.stdout.buffer.write(pixels.rgba)
    except Exception:
        # No malformed source bytes, metadata or decoder traceback in logs.
        sys.exit(2)
