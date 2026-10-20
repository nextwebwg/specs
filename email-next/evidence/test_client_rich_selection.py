import unittest
from client_flow_server import Demo
class RichSelection(unittest.TestCase):
    def test_malformed_or_unretained_selection_cannot_reach_renderer(self):
        demo=Demo.__new__(Demo);demo.rich_selections={}
        for value in ({'selection':[]},{'selection':{}},{'selection':None},{'selection':1},{'selection':'missing'},[],{}):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'Unknown rich selection'):demo.rich(value)
