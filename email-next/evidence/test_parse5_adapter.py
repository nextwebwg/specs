import os
import unittest
from html_tree import project_tree
from parse5_adapter import parser_adapter
MODULE=os.environ.get('EMAIL_NEXT_PARSE5_MODULE')
@unittest.skipUnless(MODULE,'set EMAIL_NEXT_PARSE5_MODULE to pinned parse5 module file URL')
class Parse5AdapterTests(unittest.TestCase):
    def parse(self,text):
        return project_tree(text.encode(),mime_charset='utf-8',max_bytes=8192,max_nodes=100,max_depth=30,parser_adapter=parser_adapter(MODULE))
    def test_template_content_is_removed_in_integrated_projection(self):
        result=self.parse('<table><template><tr><td>hidden</td></tr></template></table><p style="color:#abc">visible</p>')
        self.assertEqual(result['tree'],[{'element':'table','children':[]},{'element':'p','children':['visible'],'attributes':{'style':'color:#abc'}}])
    def test_namespaces_and_attributes_keep_filtering(self):
        result=self.parse('<svg><foreignObject><p>hidden</p></foreignObject></svg><p onclick="bad()" dir="RTL">visible</p>')
        self.assertEqual(result['tree'],[{'element':'p','children':['visible'],'attributes':{'dir':'rtl'}}])
    def test_noscript_recovery_remains_explicitly_unsupported(self):
        with self.assertRaisesRegex(ValueError,'unsupported parser context'):
            self.parse('<noscript><p>hidden</p></noscript><p>visible</p>')
    def test_body_noscript_is_removed_without_refusing_visible_content(self):
        result=self.parse('<!doctype html><html><head></head><body><noscript><p>hidden</p></noscript><p>visible</p></body></html>')
        self.assertEqual(result['tree'],[{'element':'p','children':['visible']}])
    def test_head_noscript_refusal_is_not_bypassed_by_following_markup(self):
        for tail in ['<p>visible</p>','<table><tr><td>visible</td></tr></table>']:
            with self.assertRaisesRegex(ValueError,'malformed head noscript'):
                self.parse('<noscript><p>hidden</p></noscript>'+tail)

    def test_direction_refusal_matches_common_projection_without_partial_tree(self):
        for source in ('<p>before</p><section dir="rtl">שלום</section><p>after</p>',
                       '<p><unknown dir="auto">123 שלום</unknown>tail</p>'):
            with self.subTest(source=source),self.assertRaisesRegex(ValueError,'unpreserved-direction-boundary'):
                self.parse(source)
        result=self.parse('<form dir="auto">123 שלום</form>tail')
        self.assertEqual(result['tree'][0]['attributes']['dir'],'auto')
        self.assertEqual(result['tree'][1],'tail')

    def test_duplicate_encoding_attributes_preserve_diagnostics(self):
        self.assertEqual(self.parse('<meta charset=utf-8 charset=windows-1252><p>x</p>')['encodingState'],'nonconforming')
if __name__=='__main__':unittest.main()
