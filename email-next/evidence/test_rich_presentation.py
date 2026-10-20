import unittest
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
    def test_untyped_src_diagnostic_not_hidden(self):
        result=project(self.operation('<p src="https://example.invalid">Title</p>'),'a'*32)
        self.assertEqual(result['state'],'plain-only')
