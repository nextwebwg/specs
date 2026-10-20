"""Synthetic codec fixtures; no content authentication or browser rendering claim."""
from dataclasses import replace
import io
import unittest
import sys
from unittest.mock import patch
import struct
import zlib
from PIL import Image,PngImagePlugin
from image_decode import decode_image,DecodeError,DecodeLimits
LIMITS=DecodeLimits(max_encoded=100000,max_width=64,max_height=64,max_pixels=4096,max_output=16384,timeout_seconds=5)

def fixture(format='PNG',size=(3,2),**kw):
    stream=io.BytesIO();Image.new('RGB',size,(10,20,30)).save(stream,format=format,**kw);return stream.getvalue()

class ImageDecodeTests(unittest.TestCase):
    def test_png_exact_inert_pixels(self):
        pixels=decode_image(fixture(),'image/png',LIMITS)
        self.assertEqual((pixels.width,pixels.height),(3,2));self.assertEqual(pixels.rgba,bytes([10,20,30,255])*6)
    def test_jpeg_decodes_rgba(self):
        pixels=decode_image(fixture('JPEG'),'image/jpeg',LIMITS)
        self.assertEqual(len(pixels.rgba),24);self.assertEqual(pixels.rgba[3::4],bytes([255])*6)
    def test_metadata_not_returned(self):
        info=PngImagePlugin.PngInfo();info.add_text('Comment','https://untrusted.invalid/not-fetched')
        pixels=decode_image(fixture(pnginfo=info),'image/png',LIMITS)
        self.assertEqual(set(vars(pixels)),{'width','height','rgba'});self.assertEqual(len(pixels.rgba),24)
    def test_format_mismatch_and_unsupported(self):
        for encoded,mime in [(fixture(),'image/jpeg'),(fixture('JPEG'),'image/png'),(fixture(),'image/gif')]:
            with self.assertRaises(DecodeError):decode_image(encoded,mime,LIMITS)
    def test_animation_rejected_including_single_frame_apng(self):
        for count in (1,2):
            stream=io.BytesIO();first=Image.new('RGB',(2,2),'red')
            first.save(stream,format='PNG',save_all=True,append_images=[Image.new('RGB',(2,2),'blue')]*(count-1),duration=10,loop=0)
            encoded=stream.getvalue()
            if count==1:
                def chunk(kind,payload):
                    return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload))
                control=chunk(b'acTL',struct.pack('>II',1,0))+chunk(b'fcTL',struct.pack('>IIIIIHHBB',0,2,2,0,0,1,100,0,0))
                encoded=encoded[:33]+control+encoded[33:]
                with Image.open(io.BytesIO(encoded)) as image:self.assertEqual(image.n_frames,1)
            self.assertIn(b'acTL',encoded)
            with self.assertRaises(DecodeError):decode_image(encoded,'image/png',LIMITS)
    def test_malformed_truncated_and_trailing(self):
        png=fixture();bad=bytearray(png);bad[-5]^=1
        for encoded,mime in [(b'garbage','image/png'),(png[:-5],'image/png'),(bytes(bad),'image/png'),(png+b'extra','image/png'),(fixture('JPEG')[:-4],'image/jpeg')]:
            with self.assertRaises(DecodeError):decode_image(encoded,mime,LIMITS)
    def test_adjustable_encoded_dimensions_pixels_output_limits(self):
        encoded=fixture()
        for limits in [replace(LIMITS,max_encoded=1),replace(LIMITS,max_width=2),replace(LIMITS,max_height=1),replace(LIMITS,max_pixels=5),replace(LIMITS,max_output=23)]:
            with self.assertRaises(DecodeError):decode_image(encoded,'image/png',limits)
        self.assertEqual(len(decode_image(encoded,'image/png',replace(LIMITS,max_pixels=6,max_output=24)).rgba),24)
    def test_decompression_size_and_invalid_policy(self):
        with self.assertRaises(DecodeError):decode_image(fixture(size=(64,64)),'image/png',replace(LIMITS,max_pixels=16))
        for limits in [replace(LIMITS,max_pixels=0),replace(LIMITS,timeout_seconds=float('nan')),replace(LIMITS,max_output=True)]:
            with self.assertRaises(ValueError):decode_image(fixture(),'image/png',limits)
    def test_process_policy_compatibility_and_validation_before_spawn(self):
        compatible=DecodeLimits(100000,64,64,4096,16384,5)
        self.assertEqual(decode_image(fixture(),'image/png',compatible).rgba,bytes([10,20,30,255])*6)
        with patch('image_decode.run_parser',side_effect=AssertionError('must not spawn')):
            for limits in (replace(LIMITS,cpu_seconds=0),replace(LIMITS,max_resident=True),replace(LIMITS,sample_seconds=float('nan')),replace(LIMITS,require_hard_memory=1)):
                with self.assertRaises(ValueError):decode_image(fixture(),'image/png',limits)
    def test_actual_resource_failure_and_malformed_preheader(self):
        with self.assertRaises(DecodeError):decode_image(fixture(),'image/png',replace(LIMITS,timeout_seconds=.001))
        with self.assertRaises(DecodeError):decode_image(fixture(),'image/png',replace(LIMITS,max_resident=1))
        # Large input without any valid image header still crosses the limited worker.
        with self.assertRaises(DecodeError):decode_image(b'x'*99999,'image/png',LIMITS)
        if sys.platform=='darwin':
            with self.assertRaises(DecodeError):decode_image(fixture(),'image/png',replace(LIMITS,require_hard_memory=True))
if __name__=='__main__':unittest.main()
