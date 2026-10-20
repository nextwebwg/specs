import unittest
from managed_presentation import authored_date,provisional
class PresentationDisplay(unittest.TestCase):
    def test_uint64_date_never_truncates_or_orders(self):
        result=authored_date('18446744073709551615')
        self.assertEqual(result,dict(source='18446744073709551615',display='Unavailable',trustedClock=False))
        self.assertEqual(authored_date('0')['display'],'1970-01-01T00:00:00+00:00')
        self.assertEqual(authored_date('')['display'],'Not stated')
    def test_undecryptable_transport_is_only_provisional(self):
        result=provisional(b'From: forged@example.invalid\r\nSubject: outer-only\r\nReply-To: attacker@example.invalid\r\n\r\nopaque')
        self.assertEqual(result['state'],'provisional-transport');self.assertNotIn('replyAudience',result);self.assertNotIn('subject',result)
        self.assertEqual(result['transport']['fields']['Subject'],['outer-only'])
if __name__=='__main__':unittest.main()
