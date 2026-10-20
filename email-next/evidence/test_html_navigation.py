import json
from pathlib import Path
import subprocess
import unittest
from html_tree import project_tree

def pipeline(source):
    parsed=project_tree(source.encode(),mime_charset='utf-8',max_bytes=4096,max_nodes=100,max_depth=20)
    output=subprocess.run(['node',str(Path(__file__).with_name('check-html-navigation.mjs'))],input=json.dumps(parsed['tree']),text=True,capture_output=True,check=True)
    return json.loads(output.stdout)
class NavigationIntegrationTests(unittest.TestCase):
    def test_html_entities_are_decoded_once_before_url_validation(self):
        result=pipeline('<a href="https://example.test/?a=1&amp;b=2">Open</a>')
        link=result['tree'][0]
        self.assertEqual(link['navigation']['href'],'https://example.test/?a=1&b=2')
        self.assertNotIn('navigationCandidate',link)
        self.assertNotIn('href',link.get('attributes',{}))
    def test_rejected_links_preserve_text_without_destination(self):
        for href in ['javascript:bad()','//example.test','https://a@example.test','https://exam&#10;ple.test']:
            result=pipeline('<a href="'+href+'">Visible</a>')
            self.assertEqual(result['tree'][0]['children'],['Visible'])
            self.assertNotIn('navigation',result['tree'][0])
            self.assertIn('rejected-navigation',result['diagnostics'])
    def test_sender_target_and_tracking_attributes_do_not_survive(self):
        link=pipeline('<a href="https://example.test" target="_top" ping="https://tracker.test" onclick="bad()">Open</a>')['tree'][0]
        self.assertEqual(link['navigation']['origin'],'https://example.test')
        self.assertFalse(link.get('attributes'))
if __name__=='__main__':unittest.main()
