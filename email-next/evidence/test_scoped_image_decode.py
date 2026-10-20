import copy
import hashlib
import io
import unittest
from unittest.mock import patch
from PIL import Image
from image_decode import DecodeLimits
from scoped_image_decode import resolve_and_decode_image
EVENT='1'*32
ID='2'*32
CID=ID+'.'+EVENT+'@resources.email-next.invalid'
LIMITS=DecodeLimits(100000,64,64,4096,16384,5)
class ScopedImageTests(unittest.TestCase):
    def setUp(self):
        stream=io.BytesIO();Image.new('RGB',(3,2),(10,20,30)).save(stream,format='PNG')
        self.bytes=stream.getvalue();self.parts=[dict(contentId=CID,mediaType='image/png',bytes=self.bytes)]
        self.manifest=[dict(id=ID,size=str(len(self.bytes)),sha256=hashlib.sha256(self.bytes).hexdigest())]
    def run_image(self,candidate='cid:'+CID,**kwargs):
        args=dict(alt='Original alt text',resource_limits={'maxBytes':100000,'maxChunks':1,'maxInputBytes':100000},decode_limits=LIMITS,bridge_max_bytes=300000)
        args.update(kwargs)
        return resolve_and_decode_image(candidate,EVENT,self.manifest,self.parts,**args)
    def test_real_binding_then_png_and_jpeg_pixels(self):
        self.assertEqual(self.run_image()['pixels'].rgba,bytes([10,20,30,255])*6)
        stream=io.BytesIO();Image.new('RGB',(3,2),'blue').save(stream,format='JPEG')
        data=stream.getvalue();self.parts[0].update(bytes=data,mediaType='image/jpeg')
        self.manifest[0].update(size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())
        result=self.run_image();self.assertEqual(result['state'],'pixels');self.assertEqual(len(result['pixels'].rgba),24)
    def test_bad_hash_cross_event_and_remote_source_never_decode(self):
        with patch('scoped_image_decode.decode_image',side_effect=AssertionError('No decoder call')):
            for source in ('https://example.invalid/pixel','data:image/png;base64,AA==','cid:'+CID.replace(EVENT,'3'*32)):
                self.assertEqual(self.run_image(source)['state'],'alt')
            self.manifest[0]['sha256']='0'*64
            self.assertEqual(self.run_image()['reason'],'digest-mismatch')
    def test_media_mismatch_never_reaches_decoder(self):
        with patch('scoped_image_decode.decode_image',side_effect=AssertionError('No decoder call')):
            self.parts[0]['mediaType']='image/jpeg';self.assertEqual(self.run_image()['reason'],'media-type-mismatch')
            self.parts[0]['mediaType']='image/svg+xml';self.assertEqual(self.run_image()['reason'],'unsupported-media-type')
    def test_missing_duplicate_and_foreign_compound_parts(self):
        with patch('scoped_image_decode.decode_image',side_effect=AssertionError('No decoder call')):
            original=self.parts;self.parts=[];self.assertEqual(self.run_image()['reason'],'missing')
            self.parts=original*2;self.assertEqual(self.run_image()['reason'],'ambiguous')
            self.parts=copy.deepcopy(original);self.parts[0]['contentId']=CID.replace(EVENT,'3'*32)
            self.assertEqual(self.run_image()['reason'],'missing')
    def test_authenticated_but_malformed_image_returns_alt(self):
        data=self.bytes[:16];self.parts[0]['bytes']=data
        self.manifest[0].update(size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())
        result=self.run_image();self.assertEqual(result,{'state':'alt','alt':'Original alt text','reason':'decode-rejected'})
    def test_binding_and_bridge_limits_return_alt_without_decoding(self):
        with patch('scoped_image_decode.decode_image',side_effect=AssertionError('No decoder call')):
            self.assertEqual(self.run_image(resource_limits={'maxBytes':1,'maxChunks':1,'maxInputBytes':100000})['reason'],'limit-exceeded')
            self.assertEqual(self.run_image(bridge_max_bytes=1)['reason'],'bridge-input-size')
if __name__=='__main__':unittest.main()
