import unittest
from html_tree import project_tree,_project_tree_local
from parser_process import ParserFailure
from html_serialize import serialize_preview
import html5lib

def project(source):
    return project_tree(source.encode(),mime_charset='utf-8',max_bytes=8192,max_nodes=100,max_depth=30)
class RecoveryTests(unittest.TestCase):
    def assert_unsupported_context(self,source):
        # Check the semantic rejection separately from the isolated worker API.
        with self.assertRaisesRegex(ValueError,'unsupported parser context'):
            _project_tree_local(source.encode(),mime_charset='utf-8',max_bytes=8192,max_nodes=100,max_depth=30)
        with self.assertRaisesRegex(ParserFailure,'parser-worker-rejected'):
            project(source)
    def test_template_relocation_never_returns_a_successful_projection(self):
        for source in ['<template><p>hidden</p></template><p>visible</p>',
                       '<table><template><tr><td>hidden</td></tr></template></table><p>visible</p>']:
            self.assert_unsupported_context(source)
    def test_noscript_recovery_is_explicitly_unsupported(self):
        self.assert_unsupported_context('<noscript><p>hidden</p></noscript><p>visible</p>')
    def test_foreign_html_integration_point_does_not_export_descendants(self):
        result=project('<svg><foreignObject><p>hidden</p></foreignObject></svg><p>visible</p>')
        self.assertEqual(result['tree'],[{'element':'p','children':['visible']}])
    def test_malformed_foreign_content_has_no_executable_reparse(self):
        source='<math><mtext><table><mglyph><style><!--</style><img title="--><img src=x onerror=bad()>">'
        result=project(source)
        parsed=html5lib.parse(serialize_preview(result['tree']))
        for node in parsed.iter():
            self.assertFalse(any(str(key).startswith('on') for key in node.attrib))
            self.assertNotIn('src',node.attrib)
if __name__=='__main__':unittest.main()
