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
    def process_limits(self):
        return ParserLimits(wall_seconds=self.timeout_seconds,cpu_seconds=self.cpu_seconds,max_output=self.max_output+128,max_resident=self.max_resident,sample_seconds=self.sample_seconds,require_hard_memory=self.require_hard_memory)
    def validate(self):
        for key in ('max_encoded','max_width','max_height','max_pixels','max_output'):
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

def _png_structure(encoded):
    # Detect even a one-frame APNG; is_animated alone need not reject that case.
    if encoded[:8]!=b'\x89PNG\r\n\x1a\n':raise DecodeError('png-signature')
    offset=8
    while offset+12<=len(encoded):
        length=int.from_bytes(encoded[offset:offset+4],'big');kind=encoded[offset+4:offset+8]
        end=offset+12+length
        if end>len(encoded):raise DecodeError('png-truncated')
        if kind==b'acTL':raise DecodeError('animation')
        if kind==b'IEND':
            if length or end!=len(encoded):raise DecodeError('png-trailing')
            return
        offset=end
    raise DecodeError('png-end')

def _decode(encoded,media_type,limits):
    import io,warnings
    from PIL import Image,ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES=False
    Image.MAX_IMAGE_PIXELS=limits.max_pixels
    if media_type=='image/png':_png_structure(encoded)
    elif not encoded.endswith(b'\xff\xd9'):raise DecodeError('jpeg-end')
    expected={'image/png':'PNG','image/jpeg':'JPEG'}[media_type]
    def inspect(image):
        if image.format!=expected:raise DecodeError('format-mismatch')
        if getattr(image,'is_animated',False) or getattr(image,'n_frames',1)!=1:raise DecodeError('animation')
        width,height=image.size
        if width<=0 or height<=0 or width>limits.max_width or height>limits.max_height or width*height>limits.max_pixels or width*height*4>limits.max_output:
            raise DecodeError('decoded-size')
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(encoded),formats=['PNG','JPEG'])as image:
            inspect(image);image.verify()
        with Image.open(io.BytesIO(encoded),formats=['PNG','JPEG'])as image:
            inspect(image);image.load()
            rgba=image.convert('RGBA').tobytes()
            return Pixels(image.width,image.height,rgba)

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
