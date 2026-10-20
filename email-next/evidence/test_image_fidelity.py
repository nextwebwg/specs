"""Synthetic format and color vectors; no codec certification claim."""
from dataclasses import replace
import io
import struct
import unittest
import zlib
from PIL import Image, ImageCms
from image_decode import decode_image, DecodeError
from test_image_decode import LIMITS


def chunk(kind, value):
    return struct.pack('>I',len(value))+kind+value+struct.pack('>I',zlib.crc32(kind+value))


def png(rows, width, height, depth=8, color=2, before=(), after=(), interlace=0):
    header=struct.pack('>IIBBBBB',width,height,depth,color,0,0,interlace)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+b''.join(chunk(*c) for c in before)+chunk(b'IDAT',zlib.compress(rows))+b''.join(chunk(*c) for c in after)+chunk(b'IEND',b'')


def exif(orientation, extras=()):
    entries=[(274,3,1,struct.pack('<H',orientation)+b'\0\0'),*extras]
    return b'II*\0\x08\0\0\0'+struct.pack('<H',len(entries))+b''.join(struct.pack('<HHI',tag,typ,count)+value for tag,typ,count,value in entries)+b'\0'*4


def icc_v2_srgb():
    """Build an ICCv2 matrix profile with v2 curve/description/text types.

    Re-labeling a v4 parametric-curve profile as v2 would be a malformed fixture.
    XYZ colorants/white point come from LittleCMS's public sRGB profile.
    """
    original=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();entries={}
    for at in range(132,132+12*int.from_bytes(original[128:132],'big'),12):
        tag=original[at:at+4];offset,size=struct.unpack('>II',original[at+4:at+12]);entries[tag]=original[offset:offset+size]
    values=[]
    for index in range(4096):
        v=index/4095;values.append(round((v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4)*65535))
    curve=b'curv'+b'\0'*4+struct.pack('>I',len(values))+struct.pack('>'+str(len(values))+'H',*values)
    tags={tag:entries[tag]for tag in(b'wtpt',b'rXYZ',b'gXYZ',b'bXYZ')}
    tags.update({tag:curve for tag in(b'rTRC',b'gTRC',b'bTRC')})
    text=b'Synthetic sRGB ICCv2\0'
    tags[b'desc']=b'desc'+b'\0'*4+struct.pack('>I',len(text))+text+b'\0'*78
    tags[b'cprt']=b'text'+b'\0'*4+b'Synthetic test vector\0'
    header=bytearray(original[:128]);header[8:12]=b'\2\x40\0\0';header[84:100]=b'\0'*16
    offset=132+12*len(tags);table=bytearray();body=bytearray()
    for tag,value in tags.items():
        table.extend(tag+struct.pack('>II',offset+len(body),len(value)));body.extend(value);body.extend(b'\0'*(-len(body)%4))
    profile=header+struct.pack('>I',len(tags))+table+body;profile[:4]=struct.pack('>I',len(profile));return bytes(profile)


class FidelityTests(unittest.TestCase):
    def decode(self, data, mime='image/png', limits=LIMITS):
        return decode_image(data,mime,limits)

    def test_gray16_rescales_instead_of_clamping(self):
        data=png(b'\0'+struct.pack('>4H',0,257,32768,65535),4,1,16,0)
        self.assertEqual(self.decode(data).rgba,bytes([0,0,0,255,1,1,1,255,128,128,128,255,255,255,255,255]))

    def test_rgb16_transparent_color_compares_before_rounding(self):
        key=(32768,16384,65535)
        data=png(b'\0'+struct.pack('>6H',*key,32769,16384,65535),2,1,16,2,[(b'tRNS',struct.pack('>3H',*key))])
        self.assertEqual(self.decode(data).rgba,bytes([128,64,255,0,128,64,255,255]))

    def test_gray16_transparent_color_compares_before_rounding(self):
        data=png(b'\0'+struct.pack('>2H',32768,32769),2,1,16,0,[(b'tRNS',struct.pack('>H',32768))])
        self.assertEqual(self.decode(data).rgba,bytes([128,128,128,0,128,128,128,255]))

    def test_gray_alpha16_preserves_opacity(self):
        data=png(b'\0'+struct.pack('>4H',32768,16384,65535,32768),2,1,16,4)
        self.assertEqual(self.decode(data).rgba,bytes([128,128,128,64,255,255,255,128]))

    def test_gamma_conversion_changes_color_not_alpha(self):
        data=png(b'\0\x80\x80\x80\x40',1,1,8,6,[(b'gAMA',struct.pack('>I',100000))])
        p=self.decode(data).rgba
        for c in p[:3]:self.assertAlmostEqual(c,188,delta=1)
        self.assertEqual(p[3],64)

    def test_chromaticity_without_gamma_uses_srgb_curve(self):
        chrm=struct.pack('>8I',31270,32900,64000,33000,30000,60000,15000,6000)
        data=png(b'\0\x80\x40\x20',1,1,before=[(b'cHRM',chrm)])
        self.assertEqual(self.decode(data).rgba,bytes([128,64,32,255]))

    def test_icc_rgb_v2_v4_and_precedence(self):
        for profile in (icc_v2_srgb(),ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()):
            data=png(b'\0\x80\x40\x20',1,1,before=[(b'gAMA',struct.pack('>I',100000)),(b'iCCP',b'sRGB\0\0'+zlib.compress(bytes(profile)))])
            p=self.decode(data).rgba
            for actual,expected in zip(p,[128,64,32,255]):self.assertAlmostEqual(actual,expected,delta=1)

    def test_unsupported_cicp_and_invalid_profiles_are_explicit_fallbacks(self):
        for meta in [[(b'cICP',bytes([9,16,0,1]))],[(b'iCCP',b'bad\0\0'+zlib.compress(b'bad'))],[(b'gAMA',b'\0'*4)],[(b'sRGB',b'\x04')]]:
            with self.assertRaises(DecodeError):self.decode(png(b'\0\x80\x40\x20',1,1,before=meta))

    def test_srgb_and_icc_are_contradictory(self):
        profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
        with self.assertRaises(DecodeError):self.decode(png(b'\0\x80\x40\x20',1,1,before=[(b'sRGB',b'\0'),(b'iCCP',b'p\0\0'+zlib.compress(profile))]))

    def test_all_orientation_values_apply_once(self):
        # Distinct lossless pixels identify reflected and rotated positions.
        expected={1:[1,2,3,4,5,6],2:[3,2,1,6,5,4],3:[6,5,4,3,2,1],4:[4,5,6,1,2,3],5:[1,4,2,5,3,6],6:[4,1,5,2,6,3],7:[6,3,5,2,4,1],8:[3,6,2,5,1,4]}
        rows=b'\0'+b''.join(bytes([v,v,v])for v in (1,2,3))+b'\0'+b''.join(bytes([v,v,v])for v in (4,5,6))
        for orientation in range(1,9):
            p=self.decode(png(rows,3,2,before=[(b'eXIf',exif(orientation))]))
            self.assertEqual(list(p.rgba[::4]),expected[orientation]);self.assertEqual((p.width,p.height),(3,2)if orientation<5 else(2,3))

    def test_orientation_rechecks_dimensions(self):
        data=png(b'\0'+bytes([1,2,3])*3+b'\0'+bytes([1,2,3])*3,3,2,before=[(b'eXIf',exif(6))])
        with self.assertRaises(DecodeError):self.decode(data,limits=replace(LIMITS,max_height=2))

    def test_malformed_duplicate_primary_orientation_rejected(self):
        for metadata in (exif(0),exif(9),exif(1,[(274,3,1,b'\1\0\0\0')]),b'II*\0\xff\xff\xff\xff'):
            with self.assertRaises(DecodeError):self.decode(png(b'\0\1\2\3',1,1,before=[(b'eXIf',metadata)]))

    def test_jpeg_exif_orientation_and_progressive(self):
        source=Image.new('RGB',(3,2),(123,45,67))
        for progressive in (False,True):
            stream=io.BytesIO();source.save(stream,'JPEG',progressive=progressive,exif=b'Exif\0\0'+exif(6))
            p=self.decode(stream.getvalue(),'image/jpeg');self.assertEqual((p.width,p.height),(2,3));self.assertEqual(p.rgba[3::4],b'\xff'*6)

    def test_idat_extra_stream_output_and_unknown_critical_rejected(self):
        for data in (png(b'\0\1\2\3'+b'\0'*100,1,1),png(b'\0\1\2\3',1,1,before=[(b'ABCD',b'')])):
            with self.assertRaises(DecodeError):self.decode(data)

    def test_every_static_png_color_depth_and_both_interlace_modes(self):
        import png as codec
        for color,depths in {0:(1,2,4,8,16),2:(8,16),3:(1,2,4,8),4:(8,16),6:(8,16)}.items():
            for depth in depths:
                for interlace in (False,True):
                    planes={0:1,2:3,3:1,4:2,6:4}[color];maximum=(1<<depth)-1
                    row=[(x*17+y*3)% (maximum+1)for x in range(5)for y in range(planes)]
                    options=dict(width=5,height=3,bitdepth=depth,interlace=interlace)
                    if color==3:options['palette']=[(0,0,0,0),(10,20,30,128)]+[(i,i,i,255)for i in range(2,maximum+1)]
                    else:options.update(greyscale=color in(0,4),alpha=color in(4,6))
                    stream=io.BytesIO();codec.Writer(**options).write(stream,[row]*3)
                    p=self.decode(stream.getvalue());self.assertEqual((p.width,p.height),(5,3))
                    expected=bytearray()
                    for at in range(0,len(row),planes):
                        values=row[at:at+planes]
                        if color==3:expected.extend(options['palette'][values[0]])
                        else:
                            scale=lambda v:(v*255+maximum//2)//maximum
                            rgb=[scale(v)for v in values[:1 if color in(0,4)else 3]]
                            if len(rgb)==1:rgb*=3
                            expected.extend(rgb+[scale(values[-1])if color in(4,6)else 255])
                    self.assertEqual(p.rgba,bytes(expected)*3,(color,depth,interlace))

    def test_all_png_filters(self):
        first=bytes([10,20,30,40,50,60]);second=bytes([20,40,60,80,100,120]);unit=3
        for filter_type in range(5):
            filtered=bytearray()
            for at,value in enumerate(second):
                a=second[at-unit]if at>=unit else 0;b=first[at];c=first[at-unit]if at>=unit else 0
                if filter_type==0:predict=0
                elif filter_type==1:predict=a
                elif filter_type==2:predict=b
                elif filter_type==3:predict=(a+b)//2
                else:
                    pred=a+b-c;distances=[abs(pred-v)for v in(a,b,c)];predict=(a,b,c)[distances.index(min(distances))]
                filtered.append((value-predict)%256)
            p=self.decode(png(b'\0'+first+bytes([filter_type])+filtered,2,2))
            self.assertEqual(p.rgba,bytes([10,20,30,255,40,50,60,255,20,40,60,255,80,100,120,255]))

    def test_metadata_budget_and_zlib_stream_termination(self):
        profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
        data=png(b'\0\1\2\3',1,1,before=[(b'iCCP',b'p\0\0'+zlib.compress(profile))])
        with self.assertRaises(DecodeError):self.decode(data,limits=replace(LIMITS,max_metadata=100))
        for value in (zlib.compress(b'\0\1\2\3')+zlib.compress(b''),zlib.compress(b'\0\1\2\3')[:-1]):
            header=chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))
            with self.assertRaises(DecodeError):self.decode(b'\x89PNG\r\n\x1a\n'+header+chunk(b'IDAT',value)+chunk(b'IEND',b''))

    def test_jpeg_icc_reordering_and_missing_duplicate_segments(self):
        stream=io.BytesIO();Image.new('RGB',(2,1),(128,64,32)).save(stream,'JPEG',quality=100,subsampling=0)
        original=stream.getvalue();profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();split=len(profile)//2
        def segment(number,count,data):
            value=b'ICC_PROFILE\0'+bytes([number,count])+data
            return b'\xff\xe2'+struct.pack('>H',len(value)+2)+value
        parts=[segment(1,2,profile[:split]),segment(2,2,profile[split:])]
        p=self.decode(original[:2]+b''.join(reversed(parts))+original[2:],'image/jpeg')
        for v,expected in zip(p.rgba[:3],(128,64,32)):self.assertAlmostEqual(v,expected,delta=2)
        for chunks in (parts[:1],parts+[parts[0]],[parts[0],segment(2,3,profile[split:])]):
            with self.assertRaises(DecodeError):self.decode(original[:2]+b''.join(chunks)+original[2:],'image/jpeg')

    def test_gray_icc_profile_and_alpha(self):
        original=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
        entries={}
        for at in range(132,132+12*int.from_bytes(original[128:132],'big'),12):
            tag=original[at:at+4];offset,size=struct.unpack('>II',original[at+4:at+12]);entries[tag]=original[offset:offset+size]
        selected={b'wtpt':entries[b'wtpt'],b'kTRC':entries[b'rTRC'],b'desc':entries[b'desc'],b'cprt':entries[b'cprt']}
        header=bytearray(original[:128]);header[16:20]=b'GRAY';offset=132+12*len(selected);table=bytearray();body=bytearray()
        for tag,value in selected.items():
            table.extend(tag+struct.pack('>II',offset+len(body),len(value)));body.extend(value);body.extend(b'\0'*(-len(body)%4))
        profile=header+struct.pack('>I',len(selected))+table+body;profile[:4]=struct.pack('>I',len(profile))
        data=png(b'\0\x80\x40',1,1,8,4,before=[(b'iCCP',b'gray\0\0'+zlib.compress(profile))])
        p=self.decode(data).rgba
        for value in p[:3]:self.assertAlmostEqual(value,128,delta=1)
        self.assertEqual(p[3],64)

    def test_icc_lut8_lut16_mab_and_mpet_real_color_conversion(self):
        original=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();entries={}
        for at in range(132,132+12*int.from_bytes(original[128:132],'big'),12):
            tag=original[at:at+4];offset,size=struct.unpack('>II',original[at+4:at+12]);entries[tag]=original[offset:offset+size]
        def profile(tags,version):
            header=bytearray(original[:128]);header[8:12]=(b'\2\x40\0\0'if version==2 else b'\4\x40\0\0');header[84:100]=b'\0'*16
            offset=132+12*len(tags);table=bytearray();body=bytearray()
            for tag,value in tags.items():
                table.extend(tag+struct.pack('>II',offset+len(body),len(value)));body.extend(value);body.extend(b'\0'*(-len(body)%4))
            result=header+struct.pack('>I',len(tags))+table+body;result[:4]=struct.pack('>I',len(result));return result
        # A linear RGB input space with D50-adapted sRGB colorants. Half-range
        # PCS XYZ encoding in LUT8/16 is deliberate (unlike float mpet XYZ).
        matrix=((.4360747,.3850649,.1430804),(.2225045,.7168786,.0606169),(.0139322,.0971045,.7141733))
        transforms=[]
        for kind in(b'mft1',b'mft2'):
            lut=bytearray(kind+b'\0'*4+bytes([3,3,2,0])+struct.pack('>9i',65536,0,0,0,65536,0,0,0,65536))
            if kind==b'mft2':lut.extend(struct.pack('>HH',2,2));lut.extend(struct.pack('>6H',0,65535,0,65535,0,65535))
            else:lut.extend(bytes(range(256))*3)
            for r in(0,1):
                for g in(0,1):
                    for b in(0,1):
                        xyz=[sum(a*v for a,v in zip(row,(r,g,b)))for row in matrix]
                        if kind==b'mft1':lut.extend(bytes(round(v*128)for v in xyz))
                        else:lut.extend(struct.pack('>3H',*[round(v*32768)for v in xyz]))
            if kind==b'mft2':lut.extend(struct.pack('>6H',0,65535,0,65535,0,65535))
            else:lut.extend(bytes(range(256))*3)
            text=b'Synthetic LUT\0'
            tags={b'wtpt':entries[b'wtpt'],b'A2B0':bytes(lut),b'desc':b'desc'+b'\0'*4+struct.pack('>I',len(text))+text+b'\0'*78,b'cprt':b'text'+b'\0'*4+b'Synthetic vector\0'}
            transforms.append((profile(tags,2),False))
        identity=b'curv'+b'\0'*4+struct.pack('>I',0)
        lut=b'mAB '+b'\0'*4+bytes([3,3,0,0])+struct.pack('>5I',32,68,116,0,0)+identity*3+struct.pack('>12i',*[round(v*32768)for row in matrix for v in row],0,0,0)+identity*3
        tags[b'A2B0']=lut;transforms.append((profile(tags,4),False))
        element=b'matf'+b'\0'*4+struct.pack('>HH',3,3)+struct.pack('>12f',*[v for row in matrix for v in row],0,0,0)
        mpet=b'mpet'+b'\0'*4+struct.pack('>HHI',3,3,1)+struct.pack('>II',24,len(element))+element
        tags=dict(entries);tags[b'D2B0']=mpet;transforms.append((profile(tags,4),False))
        tags[b'D2B0']=mpet[:24]+b'XXXX'+mpet[28:];transforms.append((profile(tags,4),True))
        for value,reject in transforms:
            data=png(b'\0\x80\x80\x80\x40',1,1,8,6,before=[(b'iCCP',b'LUT\0\0'+zlib.compress(value))])
            if reject:
                with self.assertRaises(DecodeError):self.decode(data)
            else:
                decoded=self.decode(data).rgba
                for v in decoded[:3]:self.assertAlmostEqual(v,188,delta=2)
                self.assertEqual(decoded[3],64)

    def test_jpeg_gray_exif_first_and_orientation_positions(self):
        values=[0,40,80,120,160,200];source=Image.frombytes('L',(3,2),bytes(values))
        expected={1:[0,1,2,3,4,5],2:[2,1,0,5,4,3],3:[5,4,3,2,1,0],4:[3,4,5,0,1,2],5:[0,3,1,4,2,5],6:[3,0,4,1,5,2],7:[5,2,4,1,3,0],8:[2,5,1,4,0,3]}
        for orientation in range(1,9):
            stream=io.BytesIO();source.save(stream,'JPEG',quality=100,progressive=True,exif=b'Exif\0\0'+exif(orientation));data=stream.getvalue()
            # Exif-first interchange is legal without a JFIF APP0 segment.
            if data[2:4]==b'\xff\xe0':data=data[:2]+data[4+int.from_bytes(data[4:6],'big'):]
            self.assertEqual(data[2:4],b'\xff\xe1')
            p=self.decode(data,'image/jpeg')
            for actual,index in zip(p.rgba[::4],expected[orientation]):self.assertAlmostEqual(actual,values[index],delta=2)

    def test_palette_order_and_bad_exif_ifd_cycle(self):
        data=png(b'\0\0',1,1,1,3,before=[(b'tRNS',b'\0'),(b'PLTE',b'\0\0\0')])
        with self.assertRaises(DecodeError):self.decode(data)
        data=bytearray(exif(1));data[-4:]=struct.pack('<I',8)
        with self.assertRaises(DecodeError):self.decode(png(b'\0\1\2\3',1,1,before=[(b'eXIf',bytes(data))]))

    def test_rgba16_quantization_and_invalid_profile_bounds(self):
        data=png(b'\0'+struct.pack('>4H',32768,16384,65535,257),1,1,16,6)
        self.assertEqual(self.decode(data).rgba,bytes([128,64,255,1]))
        profile=bytearray(ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes())
        profile[136:140]=struct.pack('>I',len(profile)+4)
        for name,value in ((b'p',bytes(profile)),(b' bad',ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes())):
            with self.assertRaises(DecodeError):self.decode(png(b'\0\1\2\3',1,1,before=[(b'iCCP',name+b'\0\0'+zlib.compress(value))]))
        for maximum in (0,True):
            with self.assertRaises(ValueError):self.decode(png(b'\0\1\2\3',1,1),limits=replace(LIMITS,max_metadata=maximum))

    def test_wide_gamut_chromaticity_has_effect(self):
        # Display-P3 D65 primaries, sRGB transfer. Reference conversion via
        # CSSColor4's published P3→XYZ→sRGB matrices gives approximately138,59,21.
        chroma=struct.pack('>8I',31270,32900,68000,32000,26500,69000,15000,6000)
        p=self.decode(png(b'\0\x80\x40\x20',1,1,before=[(b'cHRM',chroma)]))
        for actual,expected in zip(p.rgba,[138,59,21,255]):self.assertAlmostEqual(actual,expected,delta=1)

    def test_unimplemented_adaptive_gain_profile_returns_fallback(self):
        # The adapter deliberately does not claim the2025ADGC construction.
        original=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes();entries={}
        for at in range(132,132+12*int.from_bytes(original[128:132],'big'),12):
            tag=original[at:at+4];offset,size=struct.unpack('>II',original[at+4:at+12]);entries[tag]=original[offset:offset+size]
        entries[b'ADGC']=b'adgc'+b'\0'*4
        offset=132+12*len(entries);table=bytearray();body=bytearray()
        for tag,value in entries.items():
            table.extend(tag+struct.pack('>II',offset+len(body),len(value)));body.extend(value);body.extend(b'\0'*(-len(body)%4))
        profile=bytearray(original[:128])+struct.pack('>I',len(entries))+table+body;profile[:4]=struct.pack('>I',len(profile))
        with self.assertRaises(DecodeError):self.decode(png(b'\0\1\2\3',1,1,before=[(b'iCCP',b'gain\0\0'+zlib.compress(profile))]))

    def test_exif31_utf8_description_does_not_control_orientation(self):
        text='Grüße aus Köln'.encode('utf-8')+b'\0'
        # Two primary entries plus next-IFD pointer end at byte38.
        metadata=exif(6,[(270,129,len(text),struct.pack('<I',38))])+text
        source=png(b'\0'+bytes([10,20,30])*3+b'\0'+bytes([40,50,60])*3,3,2,before=[(b'eXIf',metadata)])
        self.assertEqual((self.decode(source).width,self.decode(source).height),(2,3))
        stream=io.BytesIO();Image.new('RGB',(3,2),(100,120,140)).save(stream,'JPEG',exif=b'Exif\0\0'+metadata)
        p=self.decode(stream.getvalue(),'image/jpeg');self.assertEqual((p.width,p.height),(2,3))
        for count,offset in ((len(text),38+len(text)),(4294967295,38)):
            bad=exif(6,[(270,129,count,struct.pack('<I',offset))])+text
            with self.assertRaises(DecodeError):self.decode(png(b'\0\1\2\3',1,1,before=[(b'eXIf',bad)]))

if __name__=='__main__':unittest.main()
