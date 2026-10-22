"""Configuration2 byte/ordinary-metadata candidates, never native readiness."""
import base64
import copy
import hashlib
import json
import unittest
from event_encoding import encode_event
import pairing_configuration_v1 as old
import pairing_configuration_v2 as new
from suite_context import validate as old_context
from suite_modules import application as old_application
from reply_suite import application as new_application
from test_suite_context import context, OWNER

A, B, C = OWNER['principal'], 'enp0:'+'8'*64, 'enp0:'+'9'*64


def selection(agreement='mail-conversation-v1', *, private=False):
    ctx = context()
    ctx['version'] = '9' if agreement == 'mail-conversation-v1' else '8'
    ctx['application'] = new_application() if ctx['version'] == '9' else old_application()
    if private:
        ctx['delivery'] = dict(kind='private-copy-v0', originator=A, recipient=B)
    raw = json.dumps(ctx, indent=2).encode()
    return dict(kind='ordinary-v0', agreement=agreement, conversation=ctx['conversation'],
                principals=[A, B], delivery=copy.deepcopy(ctx['delivery']),
                context=base64.b64encode(raw).decode(), contextDigest=hashlib.sha256(raw).hexdigest())


class Selection2Tests(unittest.TestCase):
    def inspect(self, record, *, own=A):
        return new.inspect_ordinary_selection(encode_event(record), own_principal=own)

    def test_both_agreements_preserve_original_context_bytes_without_ready_claim(self):
        for agreement in new.BINDINGS:
            value = selection(agreement); before = copy.deepcopy(value)
            result = self.inspect(value)
            self.assertEqual(result['status'], 'ordinary-selection-syntax-only')
            self.assertEqual(result['original_context'], base64.b64decode(value['context']))
            self.assertEqual(value, before)
            self.assertNotIn('ready', result)

    def test_agreement_context_and_application_cannot_be_relabelled(self):
        for agreement in new.BINDINGS:
            value = selection(agreement)
            value['agreement'] = next(a for a in new.BINDINGS if a != agreement)
            with self.assertRaises(ValueError):self.inspect(value)
        value = selection(); ctx = json.loads(base64.b64decode(value['context']))
        with self.assertRaises(ValueError):old_context(ctx)
        ctx['application'] = old_application()
        raw = encode_event(ctx); value.update(context=base64.b64encode(raw).decode(), contextDigest=hashlib.sha256(raw).hexdigest())
        with self.assertRaises(ValueError):self.inspect(value)

    def test_private_roles_are_preserved_without_adding_a_third_principal(self):
        value = selection(private=True)
        self.inspect(value, own=B)
        for change in [dict(principals=[A, B, C]),
                       dict(delivery=dict(kind='private-copy-v0', originator=B, recipient=A))]:
            with self.subTest(change=change), self.assertRaises(ValueError):self.inspect(dict(value, **change))
        with self.assertRaises(ValueError):self.inspect(value, own=C)

    def test_context_digest_commits_bytes_not_only_equivalent_json(self):
        value = selection(); ctx = json.loads(base64.b64decode(value['context']))
        value['context'] = base64.b64encode(encode_event(ctx)).decode()
        with self.assertRaises(ValueError):self.inspect(value)

    def test_old_missing_unknown_and_private_state_fields_are_not_configuration2(self):
        value = selection()
        missing = dict(value); del missing['agreement']
        for bad in [missing, dict(value, agreement='future'), dict(value, agreement=[]),
                    dict(value, kind='managed-v0')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):self.inspect(bad)
        for field in ['checkpoint', 'history', 'drafts', 'credential', 'queuedActions']:
            with self.subTest(field=field), self.assertRaises(ValueError):self.inspect(dict(value, **{field:'not allowed'}))

    def test_audience_and_context_selection_are_explicit(self):
        value = selection()
        for change in [dict(principals=[B, A]), dict(principals=[A, A]), dict(principals=[B]),
                       dict(conversation='f'*32), dict(contextDigest='0'*64)]:
            with self.subTest(change=change), self.assertRaises(ValueError):self.inspect(dict(value, **change))


class Parts2Tests(unittest.TestCase):
    def setUp(self):
        self.data = b'x'*(new.CHUNK-1)+'€'.encode()+b' tail'
        self.refs = ['1'*64, '2'*64]
        self.value = dict(version='2', purpose='pairing-configuration-manifest', bytes=str(len(self.data)),
                          sha256=hashlib.sha256(self.data).hexdigest(),
                          parts=[dict(index=str(i), reference=r) for i, r in enumerate(self.refs)])
        self.raw = encode_event(self.value)
        self.parts = [(i, self.refs[i], new.frame_chunk(i, 2, self.data[i*new.CHUNK:(i+1)*new.CHUNK])) for i in range(2)]

    def assemble(self, raw=None, parts=None, **limits):
        return new.assemble(self.raw if raw is None else raw, self.parts if parts is None else parts,
                            **(dict(max_bytes=2*new.CHUNK, max_parts=2)|limits))

    def test_reordered_complete2_parts_preserve_scalar_split_and_original_bytes(self):
        self.assertEqual(self.assemble(parts=list(reversed(self.parts))),
                         dict(status='configuration-bytes-only', original=self.data))

    def test_old_manifest_and_magic_do_not_supply2_or_reverse(self):
        with self.assertRaises(ValueError):old.manifest(self.raw, max_bytes=2*new.CHUNK, max_parts=2)
        one = encode_event(dict(self.value, version='1'))
        with self.assertRaises(ValueError):self.assemble(raw=one)
        old_part = old.frame_chunk(0, 2, self.data[:new.CHUNK])
        with self.assertRaises(ValueError):self.assemble(parts=[(0, self.refs[0], old_part), self.parts[1]])
        with self.assertRaises(ValueError):old.assemble(one, self.parts, max_bytes=2*new.CHUNK, max_parts=2)

    def test_missing_duplicate_wrong_reference_and_modified_chunk_have_no_partial_result(self):
        for parts in [self.parts[:1], [self.parts[0], self.parts[0]],
                      [(0, '3'*64, self.parts[0][2]), self.parts[1]],
                      [(0, self.refs[0], self.parts[0][2]+b'x'), self.parts[1]]]:
            with self.subTest(parts=len(parts)), self.assertRaises(ValueError):self.assemble(parts=parts)

    def test_whole_commitment_and_local_budgets_are_still_required(self):
        for change in [dict(bytes='1'), dict(sha256='0'*64), dict(extra='x')]:
            with self.subTest(change=change), self.assertRaises(ValueError):self.assemble(raw=encode_event(dict(self.value, **change)))
        for limits in [dict(max_bytes=1), dict(max_parts=1), dict(max_bytes=0)]:
            with self.subTest(limits=limits), self.assertRaises(ValueError):self.assemble(**limits)


if __name__ == '__main__':
    unittest.main()
