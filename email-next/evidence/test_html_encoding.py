import unittest
from html_tree import project_tree

def parse(text,charset='utf-8'):
    return project_tree(text.encode('utf-8'),mime_charset=charset,max_bytes=4096,max_nodes=100,max_depth=20)
class EncodingTests(unittest.TestCase):
    def test_explicit_mime_utf8_is_required(self):
        for charset in [None,'','windows-1252','utf8']:
            with self.assertRaises(ValueError):parse('<p>x</p>',charset)
        self.assertEqual(parse('<p>x</p>','UTF-8')['encodingState'],'consistent')
    def test_matching_meta_and_conflicting_meta_are_distinct(self):
        self.assertEqual(parse('<meta charset="utf-8"><p>世界</p>')['encodingState'],'consistent')
        result=parse('<meta charset="windows-1252"><p>世界</p>')
        self.assertEqual(result['encodingState'],'nonconforming')
        self.assertEqual(result['tree'][0]['children'],['世界'])
    def test_http_equiv_and_extra_metadata_do_not_enable_activation(self):
        for meta in ['<meta http-equiv="content-type" content="text/html;charset=utf-8">','<meta charset="utf-8" name="x">']:
            self.assertEqual(parse(meta+'<p>x</p>')['encodingState'],'nonconforming')
    def test_duplicate_charset_does_not_gain_first_value_authority(self):
        result=parse('<meta charset="utf-8" charset="windows-1252"><p>x</p>')
        self.assertEqual(result['encodingState'],'nonconforming')
        self.assertIn('duplicate-source-attribute',result['diagnostics'])
if __name__=='__main__':unittest.main()
