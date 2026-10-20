import unittest
from html_tree import project_tree

def project(text,**overrides):
    return project_tree(text.encode(),mime_charset="utf-8",**({'max_bytes':4096,'max_nodes':100,'max_depth':20}|overrides))
class TreeTests(unittest.TestCase):
    def test_allowed_elements_are_fresh_attribute_free_data(self):
        result=project('<p onclick="bad()" style="color:red">Hello <b>world</b>!</p>')
        self.assertEqual(result['tree'],[{'element':'p','children':['Hello ',{'element':'b','children':['world']},'!']}])
    def test_prohibited_and_foreign_subtrees_drop_but_tails_survive(self):
        result=project('<p>A<script>bad()</script>B<svg><text>hidden</text></svg>C</p>')
        self.assertEqual(result['tree'],[{'element':'p','children':['A','B','C']}])
    def test_unknown_wrappers_keep_filtered_children(self):
        self.assertEqual(project('<section>A<em>B</em>C</section>')['tree'],['A',{'element':'em','children':['B']},'C'])
    def test_table_parser_inserts_body(self):
        tree=project('<table><tr><td>x</td></tr></table>')['tree']
        self.assertEqual(tree[0]['children'][0]['element'],'tbody')
    def test_image_candidates_remain_inert_and_missing_alt_is_reported(self):
        from html_serialize import serialize_preview
        result=project('<img src="https://tracker.example/pixel?a=1&amp;b=2"><img src="cid:logo" alt="">')
        self.assertEqual(result['tree'][0]['imageCandidate'],'https://tracker.example/pixel?a=1&b=2')
        self.assertEqual(result['diagnostics'].count('missing-image-alt'),1)
        self.assertEqual(result['tree'][1]['attributes']['alt'],'')
        preview=serialize_preview(result['tree'])
        self.assertNotIn('src=',preview)
        self.assertNotIn('tracker.example',preview)
        self.assertNotIn('cid:logo',preview)
    def test_form_direction_preserves_one_boundary_and_tail(self):
        result=project('<form dir="auto">123 <bdi>Latin</bdi> שלום</form>tail')
        wrapper=result['tree'][0]
        self.assertEqual(wrapper['element'],'div')
        self.assertEqual(wrapper['attributes'],{'dir':'auto'})
        self.assertNotIn('attributes',wrapper['children'][1])
        self.assertEqual(result['tree'][1],'tail')
    def test_document_directions_are_message_only_boundaries(self):
        result=project('<html dir="auto"><head><title>Client-independent Latin</title></head><body dir="rtl"><p>שלום</p></body></html>')
        outer=result['tree'][0]
        self.assertEqual(outer['attributes'],{'dir':'auto'})
        self.assertEqual(outer['children'][0]['attributes'],{'dir':'rtl'})
        self.assertNotIn('Latin',str(result['tree']))
    def test_unsupported_direction_wrapper_is_diagnosed(self):
        result=project('<section dir="rtl">שלום</section>')
        self.assertIn('unpreserved-direction-boundary:section',result['diagnostics'])
    def test_title_inheritance_survives_unwrapped_and_document_boundaries(self):
        result=project('<html title="document"><body title="body"><section title="section">A<b>B</b><span title="">C<em>D</em></span></section><p>E</p></body></html>')
        tree=result['tree']
        self.assertEqual(tree[0],{'element':'span','attributes':{'title':'section'},'children':['A']})
        self.assertEqual(tree[1]['attributes']['title'],'section')
        self.assertEqual(tree[2]['attributes']['title'],'')
        self.assertEqual(tree[2]['children'][1]['attributes']['title'],'')
        self.assertEqual(tree[3]['attributes']['title'],'body')
        self.assertEqual(project('<html title="document"><body><p>x</p></body></html>')['tree'][0]['attributes']['title'],'document')
    def test_title_empty_removed_override_tails_and_dropped_subtrees(self):
        tree=project('<div title="outer"><section title="">A<b>B</b></section>tail<script title="secret">bad</script><em>C</em></div>')['tree'][0]
        self.assertEqual(tree['children'][0]['attributes']['title'],'')
        self.assertEqual(tree['children'][1]['attributes']['title'],'')
        self.assertEqual(tree['children'][2],'tail')
        self.assertEqual(tree['children'][3]['attributes']['title'],'outer')
        self.assertNotIn('secret',str(tree))
    def test_title_table_context_and_preview_roundtrip(self):
        from html_serialize import serialize_preview
        source='<html title="doc"><body title=""><table title="grid"> <tbody><tr><td><section title="cell">x</section></td></tr></tbody></table><form dir="rtl" title="form"><b>x</b></form></body></html>'
        tree=project(source)['tree']
        self.assertIsInstance(tree[0]['children'][0],str)
        self.assertEqual(tree[1]['attributes'],{'dir':'rtl','title':'form'})
        self.assertEqual(project(serialize_preview(tree),max_bytes=20000)['tree'],tree)
    def test_limits_and_invalid_utf8_fail(self):
        for limits in [{'max_bytes':1},{'max_nodes':1},{'max_depth':1}]:
            with self.assertRaises(ValueError):project('<p>hello</p>',**limits)
        with self.assertRaises(UnicodeDecodeError):project_tree(b'\xff',mime_charset='utf-8',max_bytes=1,max_nodes=10,max_depth=10)
if __name__=='__main__':unittest.main()
