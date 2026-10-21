"""New metadata/assurance tests plus configured real MLS/MIME carriage.

No public route, complete suite admission, renderer or full operation validator is tested.
"""
import copy
import json
import os
from pathlib import Path
import unittest

from event_encoding import encode_event, EventLimitExceeded
from private_address_presentation import APPLICATION, inspect_metadata, check_context, assurance_rows

A, B, C = ['enp0:' + x*64 for x in 'abc']


def fixture():
    return dict(version='4', purpose='contribution', event='1'*32, conversation='2'*32,
                principal=A, audience=[A,B], disclosures=[],
                operation=dict(kind='message', text='Private body', replyTo=[]),
                presentation=dict(subject='Protected subject', authoredAt='', to=[B], cc=[],
                                  addresses=dict(**{'from':'Alice+work@sender.example'},
                                                 to=[dict(principal=B, mailbox='bob@recipient.example')], cc=[])))


def context():
    # Configured selection fixture, not a complete context8 schema or admission.
    return dict(version='8', purpose='conversation-context', conversation='2'*32, application=copy.deepcopy(APPLICATION))


class AddressMetadataTests(unittest.TestCase):
    def inspect(self, event=None):
        return inspect_metadata(encode_event(fixture() if event is None else event))

    def test_exact_bytes_and_valid_roles_retained(self):
        raw=json.dumps(fixture(),indent=2).encode()
        p=inspect_metadata(raw)
        self.assertEqual(p['octets'],raw)
        self.assertEqual(p['state'],'candidate-address-metadata')
        self.assertNotEqual(raw,encode_event(p['event']))

    def test_multiple_addresses_for_one_principal_preserve_order(self):
        e=fixture();e['presentation']['addresses']['to'].append(dict(principal=B,mailbox='b+other@recipient.example'))
        self.assertEqual(self.inspect(e)['event'],e)

    def test_self_address_can_equal_from(self):
        e=fixture();e['audience']=[A];e['presentation']['to']=[A]
        e['presentation']['addresses']['to']=[dict(principal=A,mailbox=e['presentation']['addresses']['from'])]
        self.inspect(e)

    def test_disjoint_cc_and_private_copy_audience(self):
        e=fixture();e['audience'].append(C);e['presentation']['cc']=[C]
        e['presentation']['addresses']['cc']=[dict(principal=C,mailbox='c@other.example')]
        self.inspect(e)
        e['audience'].remove(C)
        with self.assertRaises(ValueError):self.inspect(e)

    def test_role_omission_order_and_outside_principal_rejected(self):
        for entries in [[],[dict(principal=C,mailbox='c@other.example')],[dict(principal=A,mailbox='alice@sender.example')]]:
            e=fixture();e['presentation']['addresses']['to']=entries
            with self.subTest(entries=entries),self.assertRaises(ValueError):self.inspect(e)
        e=fixture();e['audience']=[A,B,C];e['presentation']['to']=[B,C]
        e['presentation']['addresses']['to']=[dict(principal=C,mailbox='c@other.example'),dict(principal=B,mailbox='b@other.example')]
        with self.assertRaises(ValueError):self.inspect(e)

    def test_duplicate_and_conflicting_mailbox_bindings_rejected(self):
        e=fixture();entry=e['presentation']['addresses']['to'][0]
        e['presentation']['addresses']['to'].append(copy.deepcopy(entry))
        with self.assertRaises(ValueError):self.inspect(e)
        e=fixture();e['presentation']['addresses']['to'][0]['mailbox']=e['presentation']['addresses']['from']
        with self.assertRaises(ValueError):self.inspect(e)
        e=fixture();e['presentation']['cc']=[B]
        with self.assertRaises(ValueError):self.inspect(e)

    def test_unknown_missing_null_and_wrong_versions_are_not_extensions(self):
        for level in ['envelope','presentation','addresses','entry']:
            for mutation in ['extra','missing','null']:
                e=fixture();obj={'envelope':e,'presentation':e['presentation'],'addresses':e['presentation']['addresses'],
                                 'entry':e['presentation']['addresses']['to'][0]}[level]
                key=next(iter(obj))
                if mutation=='extra':obj['unexpected']='x'
                elif mutation=='missing':del obj[key]
                else:obj[key]=None
                with self.subTest(level=level,mutation=mutation),self.assertRaises(ValueError):self.inspect(e)
        e=fixture();del e['presentation']['addresses']
        with self.assertRaises(ValueError):self.inspect(e)
        for v in ['3','5']:
            e=fixture();e['version']=v
            with self.assertRaises(ValueError):self.inspect(e)

    def test_noncanonical_mailboxes_rejected_and_unicode_preserved(self):
        for value in ['bob@Recipient.example','bob@recipient.example.','b ob@example.org',
                      'bob@[127.0.0.1]','"bob"@example.org','b@xn--a.example',
                      'bob@example.org\r\nReply-To:mallory@example.org','mailto:bob@example.org','<bob@example.org>',
                      'a'*65+'@example.org']:
            e=fixture();e['presentation']['addresses']['to'][0]['mailbox']=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.inspect(e)
        for value in ['Bob+tag@recipient.example','用户@recipient.example','"user@desk"@recipient.example','"用 户"@recipient.example']:
            e=fixture();e['presentation']['addresses']['to'][0]['mailbox']=value
            self.assertEqual(self.inspect(e)['event']['presentation']['addresses']['to'][0]['mailbox'],value)

    def test_subject_time_and_identifiers_remain_bounded(self):
        for path,value in [('subject','x\nFrom:y'),('authoredAt','01'),('authoredAt','18446744073709551616')]:
            e=fixture();e['presentation'][path]=value
            with self.assertRaises(ValueError):self.inspect(e)
        for name,value in [('principal','enp0:'+'0'*64),('event','0'*32),('conversation','g'*32)]:
            e=fixture();e[name]=value
            with self.assertRaises(ValueError):self.inspect(e)

    def test_strict_decoder_bounds_duplicates_numbers_and_utf8(self):
        raw=encode_event(fixture())
        for bad in [raw.replace(b'"version":"4"',b'"version":"4","\\u0076ersion":"4"'),
                    b'\xef\xbb\xbf'+raw,raw+b'{}',raw.replace(b'"authoredAt":""',b'"authoredAt":1'),
                    raw.replace(b'Protected subject',b'\xff')]:
            with self.assertRaises(ValueError):inspect_metadata(bad)
        with self.assertRaises(EventLimitExceeded):inspect_metadata(b' '*(1048576+1))

    def test_context_cannot_be_selected_by_payload_sniffing(self):
        p=self.inspect();check_context(p,context(),author=A,audience=[B,A])
        for patch in [dict(version='9'),dict(conversation='3'*32),dict(application=dict(APPLICATION,payload='mime-rich-v0')),
                      dict(application=dict(APPLICATION,envelopeVersion='3')),
                      dict(application=dict(APPLICATION,operations=APPLICATION['operations'][:-1]))]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):check_context(p,dict(context(),**patch),author=A,audience=[A,B])
        from suite_modules import application
        check_context(p,dict(context(),application=application()),author=A,audience=[A,B])
        q=fixture();q['operation']={'kind':'question'}
        with self.assertRaises(ValueError):check_context(self.inspect(q),dict(context(),application=application()),author=A,audience=[A,B])
        for author,audience in [(B,[A,B]),(A,[A]),(A,[A,B,C])]:
            with self.assertRaises(ValueError):check_context(p,context(),author=author,audience=audience)

    def test_address_claim_never_supplies_contact_or_ownership(self):
        p=self.inspect();rows=assurance_rows(p,{})
        self.assertEqual(rows['author']['state'],'author-stated-address')
        self.assertEqual(rows['author']['assurance'],'none')
        self.assertNotIn('contactName',rows['author'])
        rows=assurance_rows(p,{'Alice+work@sender.example':dict(principal=A,assurance='unverified')})
        self.assertEqual(rows['author']['assurance'],'unverified')

    def test_conflicting_local_address_cannot_reattribute_principal(self):
        rows=assurance_rows(self.inspect(),{'Alice+work@sender.example':dict(principal=C,assurance='human-confirmed')})
        self.assertEqual(rows['author'],dict(principal=A,mailbox='Alice+work@sender.example',state='address-conflict',assurance='none'))

    def test_matching_local_assurance_is_separate_trusted_input(self):
        rows=assurance_rows(self.inspect(),{'bob@recipient.example':dict(principal=B,assurance='human-confirmed')})
        self.assertEqual(rows['to'][0]['assurance'],'human-confirmed')
        with self.assertRaises(ValueError):assurance_rows(self.inspect(),{'bob@recipient.example':dict(principal=B,assurance=True)})


class AddressCryptoCarriageTests(unittest.TestCase):
    def test_actual_mls_encrypted_mime_over_configured_smtp(self):
        from provider_mls import make_device,call
        from mls_receive import worker_call, FORMAT
        from mime_package import contribution_alternatives,inspect_contribution_package
        from mls_mime import package,unpack
        from smtp_loopback import roundtrip
        binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        a,b=make_device(binary,1,2),make_device(binary,3,4)
        e=fixture();e['principal']=a['principal'];e['audience']=[a['principal'],b['principal']]
        e['presentation']['to']=[b['principal']];e['presentation']['addresses']['to'][0]['principal']=b['principal']
        raw=encode_event(e);ctx=encode_event(context())
        invitation=call(binary,op='invite-fixture-context',checkpoint=a['checkpoint'],key=a['key'],identity=a['identity'],
                        package=b['package'],context=ctx.hex())
        joined=call(binary,op='join',checkpoint=b['checkpoint'],key=b['key'],welcome=invitation['welcome'],tree=invitation['tree'])
        mime=contribution_alternatives(raw,'Private body','<!doctype html><html><head><meta charset="utf-8"></head><body><p>Private body</p></body></html>').as_bytes()
        sent=call(binary,op='send',checkpoint=invitation['checkpoint'],key=a['key'],group=invitation['group'],application=mime.hex())
        wire=roundtrip(package(bytes.fromhex(sent['wire'])))
        self.assertEqual(unpack(wire),bytes.fromhex(sent['wire']))
        for marker in [b'Alice+work@sender.example',b'bob@recipient.example',b'Protected subject',b'Private body']:
            self.assertNotIn(marker,wire)
        request=dict(format=FORMAT,checkpoint=joined['checkpoint'],group=invitation['group'],wire=unpack(wire).hex())
        result=worker_call(binary.with_name('receive-staged'),request)
        self.assertEqual(result['status'],'authenticated-application')
        self.assertEqual(result['processed']['credential'],a['identity'])
        self.assertEqual(bytes.fromhex(result['snapshot']['context']),ctx)
        recovered=inspect_contribution_package(bytes.fromhex(result['application']),max_wire_bytes=1048576,max_parts=8,max_decoded_bytes=1048576)
        self.assertEqual(recovered['event']['octets'],raw)
        check_context(inspect_metadata(recovered['event']['octets']),json.loads(ctx),author=a['principal'],audience=e['audience'])
        damaged=bytearray(unpack(wire));damaged[-1]^=1
        # Restart from the pre-receive checkpoint: rejection is cryptographic, not replay.
        bad=worker_call(binary.with_name('receive-staged'),dict(request,wire=damaged.hex()))
        self.assertNotEqual(bad.get('status'),'authenticated-application')


if __name__=='__main__':unittest.main()
