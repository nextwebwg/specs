import unittest
from pop_response import decode_multiline

def decode(wire,**changes):
    return decode_multiline(wire,**({'max_wire_bytes':8192,'max_message_bytes':4096}|changes))
class PopResponseTests(unittest.TestCase):
    def test_dot_stuffing_and_pipelined_remainder(self):
        result=decode(b'+OK\r\nSubject: x\r\n\r\n..line\r\n...\r\n.\r\n+OK next\r\n')
        self.assertEqual(result,{'state':'complete','message':b'Subject: x\r\n\r\n.line\r\n..\r\n','remaining':b'+OK next\r\n'})
    def test_no_partial_message_on_eof_or_limit(self):
        for wire in [b'+OK\r\nbody\r\n',b'+OK\r\nbody',b'+OK\r\nbody\n.\r\n']:
            with self.assertRaises(ValueError):decode(wire)
        with self.assertRaises(ValueError):decode(b'+OK\r\nbody\r\n.\r\n',max_message_bytes=5)
    def test_empty_message_and_negative_status_are_distinct(self):
        self.assertEqual(decode(b'+OK\r\n.\r\n')['message'],b'')
        result=decode(b'-ERR temporarily unavailable\r\n+OK next\r\n')
        self.assertEqual(result,{'state':'negative','remaining':b'+OK next\r\n'})
    def test_status_limit_does_not_truncate_message_lines(self):
        payload=b'x'*1000+b'\r\n'
        self.assertEqual(decode(b'+OK\r\n'+payload+b'.\r\n')['message'],payload)
        with self.assertRaises(ValueError):decode(b'+OK '+b'x'*507+b'\r\n.\r\n')
        with self.assertRaises(ValueError):decode(b'+ok\r\n.\r\n')
    def test_body_bytes_are_not_character_decoded(self):
        self.assertEqual(decode(b'+OK\r\n\xff\x00\r\n.\r\n')['message'],b'\xff\x00\r\n')
if __name__=='__main__':unittest.main()
