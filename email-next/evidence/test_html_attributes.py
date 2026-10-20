import unittest
from html_attributes import filter_attributes
from html_tree import project_tree
class AttributeTests(unittest.TestCase):
    def test_element_specific_bounds(self):
        self.assertEqual(filter_attributes('td',{'rowspan':'0','colspan':'1001'})[0],{})
        self.assertEqual(filter_attributes('th',{'rowspan':'001','scope':'ROW'})[0],{'rowspan':'1','scope':'row'})
        self.assertEqual(filter_attributes('li',{'value':'-2147483648'})[0],{'value':'-2147483648'})
        self.assertEqual(filter_attributes('li',{'value':'2147483648'})[0],{})
    def test_language_is_preserved_without_network_attributes(self):
        accepted,rejected=filter_attributes('a',{'href':'https://example.test','lang':'en','onclick':'bad()','title':'Meaning'})
        self.assertEqual(accepted,{'lang':'en','title':'Meaning'});self.assertEqual(len(rejected),2)
    def test_css_integration_and_entity_decoding(self):
        result=project_tree(b'<p dir="RTL" style="color:&#35;abc;background-image:url(https://example.test);font-weight:bold" onclick="bad()">x</p>',mime_charset='utf-8',max_bytes=4096,max_nodes=100,max_depth=20)
        self.assertEqual(result['tree'][0]['attributes'],{'dir':'rtl','style':'color:#abc;font-weight:bold'})
    def test_boolean_and_image_metadata(self):
        self.assertEqual(filter_attributes('ol',{'reversed':'false'})[0],{'reversed':''})
        self.assertEqual(filter_attributes('img',{'alt':'','width':'4097','height':'20','src':'cid:x'})[0],{'alt':'','height':'20'})
    def test_unknown_and_empty_language_do_not_become_inherited_language(self):
        from html_serialize import serialize_preview
        source=b'<div lang="en"><span lang="">Unknown</span><span lang="not_a_tag&amp;quot;">Label</span></div>'
        result=project_tree(source,mime_charset='utf-8',max_bytes=4096,max_nodes=100,max_depth=20)
        children=result['tree'][0]['children']
        self.assertEqual(children[0]['attributes']['lang'],'')
        self.assertEqual(children[1]['attributes']['lang'],'not_a_tag&quot;')
        preview=serialize_preview(result['tree'])
        self.assertIn('lang=""',preview)
        self.assertIn('lang="not_a_tag&amp;quot;"',preview)
    def test_wrapper_language_and_tail_scope_survive_projection_and_reparse(self):
        import html5lib
        from html_serialize import serialize_preview
        source=b'<html lang="en"><body><section lang="fr">Bonjour <em>ami</em></section> English <section lang="">Unknown</section><p lang="de">Hallo</p></body></html>'
        result=project_tree(source,mime_charset='utf-8',max_bytes=4096,max_nodes=100,max_depth=20)
        reparsed=html5lib.parse(serialize_preview(result['tree']),namespaceHTMLElements=False)
        actual=[]
        def visit(node,inherited=''):
            language=node.attrib.get('lang',inherited)
            if node.text and node.text.strip():actual.append((node.text.strip(),language))
            for child in node:
                visit(child,language)
                if child.tail and child.tail.strip():actual.append((child.tail.strip(),language))
        visit(reparsed.find('body'))
        self.assertEqual(actual,[('Bonjour','fr'),('ami','fr'),('English','en'),('Unknown',''),('Hallo','de')])
    def test_language_propagation_does_not_insert_table_whitespace_spans(self):
        source=b'<html lang="fr"><table>\n<tr>\n<td>Bonjour</td></tr></table></html>'
        result=project_tree(source,mime_charset='utf-8',max_bytes=4096,max_nodes=100,max_depth=20)
        table=result['tree'][0]
        self.assertEqual(table['attributes']['lang'],'fr')
        self.assertTrue(isinstance(table['children'][0],str) and table['children'][0].isspace())
if __name__=='__main__':unittest.main()
