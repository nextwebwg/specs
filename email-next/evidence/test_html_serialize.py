import unittest
import html5lib
from html_tree import project_tree,HTML
from html_serialize import serialize_preview

def tree(source):
    return project_tree(source.encode(),mime_charset='utf-8',max_bytes=8192,max_nodes=200,max_depth=30)['tree']
class SerializationTests(unittest.TestCase):
    def test_text_and_attribute_injection_stay_data(self):
        source='<p title="&quot;&gt;&lt;script&gt;bad()&lt;/script&gt;">&lt;img src=x onerror=bad()&gt;</p>'
        serialized=serialize_preview(tree(source))
        parsed=html5lib.parse(serialized)
        self.assertEqual(list(parsed.iter(HTML+'script')),[])
        self.assertEqual(list(parsed.iter(HTML+'img')),[])
        self.assertEqual(parsed.find('.//'+HTML+'p').text,'<img src=x onerror=bad()>')
    def test_second_parse_retains_filtered_body_structure(self):
        projected=tree('<table><tr><th scope="row">Title<td><b>Value</b></table>')
        self.assertEqual(tree(serialize_preview(projected)),projected)
    def test_character_reference_cr_preserves_text_and_attributes(self):
        projected=tree('<p title="a&#13;&#10;&amp;#13;">a&#13;&#10;&amp;#13;</p>')
        self.assertEqual(projected[0]['children'],['a\r\n&#13;'])
        self.assertEqual(projected[0]['attributes']['title'],'a\r\n&#13;')
        serialized=serialize_preview(projected)
        self.assertIn('a&#13;\n&amp;#13;',serialized)
        self.assertNotIn('\r',serialized)
        self.assertEqual(tree(serialized),projected)
    def test_pre_leading_linefeed_roundtrip(self):
        for source in ['<pre>\n\nhello</pre>', '<pre>\n\n\nhello</pre>',
                       '<pre>hello</pre>', '<pre><b>\nhello</b></pre>',
                       '<pre><br>\nhello</pre>', '<p>\nhello</p>']:
            with self.subTest(source=source):
                projected=tree(source)
                self.assertEqual(tree(serialize_preview(projected)),projected)
        self.assertIn('<pre>\n\nhello</pre>',serialize_preview(tree('<pre>\n\nhello</pre>')))
    def test_raw_navigation_and_image_loading_are_not_serialized(self):
        serialized=serialize_preview(tree('<a href="https://example.test">Open</a><img alt="Image" src="https://tracker.test">'))
        self.assertNotIn('href=',serialized);self.assertNotIn('src=',serialized)
        self.assertIn('alt="Image"',serialized)
    def test_unknown_nodes_and_attributes_are_refused(self):
        for value in [[{'element':'script','children':[]}],[{'element':'p','attributes':{'onclick':'bad()'},'children':[]}]]:
            with self.assertRaises(ValueError):serialize_preview(value)
if __name__=='__main__':unittest.main()
