import unittest
from email.message import EmailMessage
from email import policy
from discovery_mime import extract_discovery, MEDIA_TYPE

def message(payload=b'{"not":"authenticated"}'):
    root=EmailMessage()
    root.set_content('An ordinary human message.')
    root.add_attachment(payload,maintype='application',subtype=MEDIA_TYPE.split('/')[1],
                        filename='email-next-discovery.json',cte='base64')
    return root

def extract(root,**limits):
    return extract_discovery(root.as_bytes(policy=policy.SMTP),
                             **({'max_wire_bytes':2000000,'max_parts':10}|limits))

class DiscoveryMimeTests(unittest.TestCase):
    def test_exact_decoded_bytes_survive_mime_refolding(self):
        raw=b' { "signed": "bytes", "escaped": "\\u0061" }\n'
        root=message(raw);part=list(root.iter_parts())[1]
        encoded=part.get_payload().replace('\n','')
        part.set_payload('\r\n'.join(encoded[i:i+12] for i in range(0,len(encoded),12)))
        self.assertEqual(extract(root),{'state':'candidate','octets':raw})
    def test_forwarded_and_nested_discovery_is_not_activated(self):
        root=EmailMessage();root.set_content('Forwarded');root.add_attachment(message())
        self.assertEqual(extract(root),{'state':'absent'})
        root=EmailMessage();root.set_content('Nested');root.make_mixed();root.attach(message())
        self.assertEqual(extract(root),{'state':'absent'})
    def test_filename_does_not_select_a_candidate(self):
        root=message();part=list(root.iter_parts())[1]
        part.replace_header('Content-Type','application/json')
        self.assertEqual(extract(root),{'state':'absent'})
        part.replace_header('Content-Type',MEDIA_TYPE)
        part.replace_header('Content-Disposition','attachment; filename="other.json"')
        self.assertEqual(extract(root)['state'],'candidate')
    def test_multiple_candidates_and_ambiguous_headers_stay_inactive(self):
        root=message();root.attach(list(message().iter_parts())[1])
        self.assertEqual(extract(root),{'state':'ambiguous'})
        root=message();raw=root.as_bytes(policy=policy.SMTP)
        field=('Content-Type: '+MEDIA_TYPE+'\r\n').encode()
        raw=raw.replace(field,field+field,1)
        self.assertEqual(extract_discovery(raw,max_wire_bytes=2000000,max_parts=10),{'state':'invalid'})
    def test_parameters_bad_encoding_and_limits_do_not_release_bytes(self):
        for header,value in [('Content-Type',MEDIA_TYPE+'; charset=utf-8'),
                             ('Content-Transfer-Encoding','8bit'),
                             ('Content-Disposition','inline')]:
            root=message();list(root.iter_parts())[1].replace_header(header,value)
            self.assertEqual(extract(root),{'state':'invalid'})
        root=message();list(root.iter_parts())[1].set_payload('Zh==')
        self.assertEqual(extract(root),{'state':'invalid'})
        self.assertEqual(extract(message(),max_parts=1),{'state':'limit-exceeded'})
        self.assertEqual(extract(message(),max_wire_bytes=1),{'state':'limit-exceeded'})
