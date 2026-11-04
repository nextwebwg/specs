import unittest
import hashlib
import io
import subprocess
from PIL import Image
from unittest.mock import patch
from rich_presentation import project
class RichPresentation(unittest.TestCase):
    def operation(self,body,text='Title Description'):
        return dict(html='<!doctype html><html><head><meta charset="utf-8"></head><body>'+body+'</body></html>',text=text,embedded=[dict(resource='c'*32,mediaType='image/png')],manifest=[])
    def test_description_and_decorative_alt_are_distinct(self):
        src='cid:'+'c'*32+'.'+'a'*32+'@resources.email-next.invalid'
        for alt in ('Description',''):
            result=project(self.operation('<h2>Title</h2><img alt="'+alt+'" src="'+src+'">'),'a'*32,authoring=True)
            self.assertEqual(result['state'],'rich');self.assertEqual(next(iter(result['images'].values()))['state'],'alt')
        with self.assertRaises(ValueError):project(self.operation('<img src="'+src+'">'),'a'*32,authoring=True)
    def test_foreign_scope_remote_url_script_and_missing_readable_text_hold(self):
        for body in ('<img alt="Description" src="https://example.invalid/pixel">','<img alt="Description" src="cid:'+'c'*32+'.'+'b'*32+'@resources.email-next.invalid">','<script>alert(1)</script>','<p>Omitted secret text</p>'):
            with self.assertRaises(ValueError):project(self.operation(body),'a'*32,authoring=True)
    def test_bad_image_scope_keeps_rich_text_and_alt_without_resolver(self):
        for source in ('https://example.invalid/pixel', 'data:image/png;base64,AA==',
                       'cid:'+'c'*32+'.'+'b'*32+'@resources.email-next.invalid',
                       'cid:'+'d'*32+'.'+'a'*32+'@resources.email-next.invalid'):
            with self.subTest(source=source), patch('rich_presentation.resolve_and_decode_image',
                                                  side_effect=AssertionError('Rejected image must not reach resolver')):
                result = project(self.operation('<h2>Title</h2><img alt="Description" src="'+source+'">'),'a'*32)
                self.assertEqual(result['state'], 'rich')
                self.assertIn('image-role-or-scope', result['diagnostics'])
                self.assertEqual(list(result['images'].values()), [dict(state='alt', reason='image-role-or-scope')])
                self.assertTrue(any(n.get('element') == 'h2' for n in result['tree'] if isinstance(n,dict)))
                image = next(n for n in result['tree'] if isinstance(n,dict) and n.get('element') == 'img')
                self.assertEqual(image['attributes']['alt'], 'Description')
                self.assertNotIn('src', image['attributes'])
                self.assertNotIn('imageCandidate', image)

    def test_missing_eligible_image_keeps_other_rich_content(self):
        source = 'cid:'+'c'*32+'.'+'a'*32+'@resources.email-next.invalid'
        operation = self.operation('<h2>Title</h2><img alt="Description" src="'+source+'">')
        operation['manifest'] = [dict(id='c'*32, size='3', sha256='0'*64)]
        result = project(operation, 'a'*32, parts=[])
        self.assertEqual(result['state'], 'rich')
        self.assertEqual(list(result['images'].values()), [dict(state='alt', reason='missing')])

    def test_image_count_limit_stops_projection_before_resolution(self):
        source = 'cid:'+'c'*32+'.'+'a'*32+'@resources.email-next.invalid'
        operation = self.operation('<h2>Title</h2>'+('<img alt="Description" src="'+source+'">')*17)
        with patch('rich_presentation.resolve_and_decode_image', side_effect=AssertionError('No image work before count gate')):
            result = project(operation, 'a'*32)
        self.assertEqual(result['state'], 'plain-only')
        self.assertEqual(result['diagnostics'], ['image-processing-limit'])
        self.assertNotIn('tree', result)

    def test_aggregate_pixels_bound_real_decode_and_keep_remaining_alt(self):
        source = 'cid:'+'c'*32+'.'+'a'*32+'@resources.email-next.invalid'
        operation = self.operation('<h2>Title</h2>'+('<img alt="Description" src="'+source+'">')*2)
        stream = io.BytesIO(); Image.new('RGB', (3,2), 'blue').save(stream, format='PNG')
        data = stream.getvalue()
        operation['manifest'] = [dict(id='c'*32, size=str(len(data)), sha256=hashlib.sha256(data).hexdigest())]
        parts = [dict(contentId=source[4:], mediaType='image/png', bytes=data)]
        from scoped_image_decode import resolve_and_decode_image
        with patch('rich_presentation.resolve_and_decode_image', wraps=resolve_and_decode_image) as resolver:
            result = project(operation, 'a'*32, parts=parts, max_total_pixels=6)
        self.assertEqual(result['state'], 'rich')
        images = list(result['images'].values())
        self.assertEqual((images[0]['state'], images[0]['width'], images[0]['height']), ('pixels',3,2))
        self.assertEqual(images[1], dict(state='alt', reason='image-pixel-budget'))
        self.assertEqual(resolver.call_count, 1)
        self.assertEqual(resolver.call_args.kwargs['decode_limits'].max_pixels, 6)

    def test_navigation_binding_timeout_keeps_only_inert_text(self):
        operation = self.operation('<h2>Title</h2>', text='Title')
        real_run = subprocess.run
        def fail_navigation(command, *args, **kwargs):
            if command[0]=='node' and '-e' in command:
                raise subprocess.TimeoutExpired('configured-navigation-binding',10)
            return real_run(command,*args,**kwargs)
        with patch('rich_presentation.subprocess.run', side_effect=fail_navigation):
            result = project(operation, 'a'*32)
        self.assertEqual(result, dict(state='plain-only',text='Title',diagnostics=['navigation-binding-failure']))
        self.assertNotIn('tree',result)
        with patch('rich_presentation.subprocess.run', side_effect=fail_navigation):
            with self.assertRaises(subprocess.TimeoutExpired):project(operation,'a'*32,authoring=True)

    def test_untyped_src_diagnostic_not_hidden(self):
        result=project(self.operation('<p src="https://example.invalid">Title</p>'),'a'*32)
        self.assertEqual(result['state'],'plain-only')
