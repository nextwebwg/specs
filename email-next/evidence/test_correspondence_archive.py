"""Archive integrity/authority tests; crypto interoperability uses installed age."""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from correspondence_archive import (DOMAIN, MAGIC, import_age, manifest_bytes,
                                    stage_plain, validate_manifest, write_plain)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.signer = Ed25519PrivateKey.generate()
        self.verifier = self.signer.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.archive = 'a' * 32
        self.account = '1' * 32
        self.entry = '2' * 32
        def png_chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
        resource = (b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0))
                    + png_chunk(b'IDAT', zlib.compress(b'\0\x01\x02\x03\xff')) + png_chunk(b'IEND', b''))
        original = b'From: person@example.test\r\n\r\nHistorical mail\r\n'
        event = dict(version='3', purpose='contribution', principal='enp0:' + 'b' * 64,
                     conversation='c' * 32, event='d' * 32, audience=['enp0:' + 'b' * 64],
                     disclosures=[], presentation=dict(subject='Historical example', authoredAt='0', to=[], cc=[]),
                     operation=dict(kind='rich-message', text='Historical rich content',
                                    html='<!doctype html><html><head><meta charset="utf-8"></head><body><p>Historical rich content</p></body></html>',
                                    presentation='html-css-v0', replyTo=[],
                                    embedded=[dict(resource='3' * 32, mediaType='image/png')], attachments=[],
                                    manifest=[dict(id='3' * 32, size=str(len(resource)),
                                                   sha256=hashlib.sha256(resource).hexdigest())]))
        raw = json.dumps(event).encode()
        self.objects = {hashlib.sha256(x).hexdigest(): x for x in (raw, resource, original)}
        self.manifest = dict(version='0', purpose='correspondence-archive', archive=self.archive,
                             snapshot='e' * 32, sequence='0', previous='', createdAt='0',
                             accounts=[dict(id=self.account, principal='')],
                             coverage=dict(complete=True, omissions=[]),
                             entries=[dict(id=self.entry, account=self.account, kind='contribution',
                                           object=hashlib.sha256(raw).hexdigest(),
                                           reference={k: event[k] for k in ('principal', 'conversation', 'event')},
                                           resources=[dict(resource='3' * 32,
                                                           object=hashlib.sha256(resource).hexdigest())], evidence=[]),
                                      dict(id='4' * 32, account=self.account, kind='original-mail',
                                           object=hashlib.sha256(original).hexdigest(), contribution=self.entry)],
                             objects=[dict(sha256=h, size=str(len(data)))
                                      for h, data in sorted(self.objects.items())])

    def plain(self, manifest=None, objects=None, signer=None):
        output = io.BytesIO()
        write_plain(manifest or self.manifest, objects or self.objects, signer or self.signer, output)
        return output.getvalue()

    def import_plain(self, data, **kwargs):
        return stage_plain(io.BytesIO(data), self.root / 'history', archive=self.archive,
                           verification_key=self.verifier, **kwargs)

    def assert_rejected(self, data, **limits):
        with self.assertRaises(ValueError):
            self.import_plain(data, **limits)
        self.assertFalse((self.root / 'history').exists())
        self.assertEqual(list(self.root.glob('.archive-stage-*')), [])

    def forged_manifest(self, manifest):
        raw = json.dumps(manifest, separators=(',', ':')).encode()
        body = MAGIC + struct.pack('>I', len(raw)) + raw
        body += b''.join(self.objects[item['sha256']] for item in self.manifest['objects'])
        return body + self.signer.sign(DOMAIN + hashlib.sha256(body).digest())

    def test_roundtrip_retains_exact_objects_and_originals(self):
        accepted = self.import_plain(self.plain())
        self.assertEqual(accepted, self.manifest)
        for h, data in self.objects.items():
            self.assertEqual((self.root / 'history' / h).read_bytes(), data)
        self.assertEqual(set(p.name for p in (self.root / 'history').iterdir()),
                         set(self.objects) | {'manifest.json'})

    def archive_with_event(self, event):
        value=copy.deepcopy(self.manifest);objects=dict(self.objects)
        old=value['entries'][0]['object'];del objects[old]
        raw=json.dumps(event).encode();h=hashlib.sha256(raw).hexdigest()
        objects[h]=raw;value['entries'][0]['object']=h
        value['objects']=[dict(sha256=digest,size=str(len(data))) for digest,data in sorted(objects.items())]
        return value,objects,raw

    def test_unknown_operation_manifest_is_preserved_without_interpretation(self):
        original=json.loads(self.objects[self.manifest['entries'][0]['object']])
        original['operation']=dict(kind='future-operation',manifest=dict(format='future-specific-index'),payload='Opaque original')
        value,objects,raw=self.archive_with_event(original)
        accepted=self.import_plain(self.plain(value,objects))
        self.assertEqual(accepted,value)
        self.assertEqual((self.root/'history'/value['entries'][0]['object']).read_bytes(),raw)
        self.assertEqual(set(p.name for p in (self.root/'history').iterdir()),set(objects)|{'manifest.json'})

    def test_unknown_envelope_cannot_select_known_manifest_rules(self):
        original=json.loads(self.objects[self.manifest['entries'][0]['object']])
        original['version']='99';original['operation']['manifest']=dict(format='different-future-envelope')
        value,objects,raw=self.archive_with_event(original)
        self.assertEqual(self.import_plain(self.plain(value,objects)),value)
        self.assertEqual((self.root/'history'/value['entries'][0]['object']).read_bytes(),raw)

    def test_unknown_reply_version_remains_opaque(self):
        original=json.loads(self.objects[self.manifest['entries'][0]['object']])
        original['operation']=dict(kind='reply-message',version='99',manifest=dict(format='future-reply'))
        value,objects,raw=self.archive_with_event(original)
        self.assertEqual(self.import_plain(self.plain(value,objects)),value)
        self.assertEqual((self.root/'history'/value['entries'][0]['object']).read_bytes(),raw)

    def test_export_preflight_rejects_before_writing_any_bytes(self):
        for problem in ('object-bytes', 'reference', 'resource-binding'):
            with self.subTest(problem=problem):
                value = copy.deepcopy(self.manifest)
                objects = dict(self.objects)
                if problem == 'object-bytes':
                    objects[value['objects'][-1]['sha256']] = b'Changed retained bytes'
                elif problem == 'reference':
                    value['entries'][0]['reference']['event'] = 'f' * 32
                else:
                    value['entries'][0]['resources'][0]['object'] = value['entries'][1]['object']
                    original = self.manifest['entries'][0]['resources'][0]['object']
                    value['entries'].append(dict(id='5' * 32, account=self.account,
                                                kind='evidence', object=original))
                output = io.BytesIO()
                with self.assertRaises(ValueError):
                    write_plain(value, objects, self.signer, output)
                self.assertEqual(output.getvalue(), b'')

    def test_export_uses_frozen_objects_after_output_callback(self):
        value = copy.deepcopy(self.manifest)
        objects = dict(self.objects)
        expected = self.plain(value, objects)
        class MutatingOutput(io.BytesIO):
            def write(output, data):
                if output.tell() == 0:
                    objects.clear()
                    value['objects'].clear()
                return super().write(data)
        output = MutatingOutput()
        write_plain(value, objects, self.signer, output)
        self.assertEqual(output.getvalue(), expected)

    def test_no_live_state_installed(self):
        live = self.root / 'live.sqlite'
        live.write_bytes(b'live authority and queues unchanged')
        self.import_plain(self.plain())
        self.assertEqual(live.read_bytes(), b'live authority and queues unchanged')
        self.assertFalse((self.root / 'history' / 'live.sqlite').exists())

    def test_tampered_blob(self):
        data = bytearray(self.plain())
        start = 12 + struct.unpack('>I', data[8:12])[0]
        data[start] ^= 1
        self.assert_rejected(bytes(data))

    def test_truncated_and_trailing(self):
        for data in (self.plain()[:-1], self.plain()[:9], self.plain() + b'junk'):
            self.assert_rejected(data)

    def test_untrusted_writer_cannot_replace_archive(self):
        self.assert_rejected(self.plain(signer=Ed25519PrivateKey.generate()))

    def test_wrong_archive_recovery_kit(self):
        value = copy.deepcopy(self.manifest)
        value['archive'] = 'f' * 32
        self.assert_rejected(self.plain(value))

    def test_oversized_manifest_and_local_budget(self):
        self.assert_rejected(MAGIC + struct.pack('>I', 16777217))
        self.assert_rejected(self.plain(), max_total=32)

    def test_unknown_members_and_private_state_rejected(self):
        for key in ('privateKey', 'mlsCheckpoint', 'queuedActions'):
            value = copy.deepcopy(self.manifest)
            value[key] = 'not history'
            self.assert_rejected(self.forged_manifest(value))

    def test_duplicate_json_names(self):
        raw = manifest_bytes(self.manifest)
        raw = raw.replace(b'"version":"0"', b'"version":"0","version":"0"')
        self.assert_rejected(MAGIC + struct.pack('>I', len(raw)) + raw + b'\0' * 64)

    def test_unsafe_lengths(self):
        for size in ('-1', '01', '18446744073709551616', '9' * 1000):
            value = copy.deepcopy(self.manifest)
            value['objects'][0]['size'] = size
            self.assert_rejected(self.forged_manifest(value))

    def test_duplicate_and_unreferenced_objects(self):
        value = copy.deepcopy(self.manifest)
        value['objects'].append(value['objects'][0])
        self.assert_rejected(self.forged_manifest(value))
        value = copy.deepcopy(self.manifest)
        value['objects'].append(dict(sha256='f' * 64, size='0'))
        value['objects'].sort(key=lambda item: item['sha256'])
        self.assert_rejected(self.forged_manifest(value))

    def test_reference_mismatch(self):
        value = copy.deepcopy(self.manifest)
        value['entries'][0]['reference']['event'] = 'f' * 32
        self.assert_rejected(self.forged_manifest(value))

    def test_resource_binding_mismatch(self):
        value = copy.deepcopy(self.manifest)
        value['entries'][0]['resources'][0]['object'] = value['entries'][1]['object']
        # Retain closure through a separate historical evidence entry.
        original_resource = self.manifest['entries'][0]['resources'][0]['object']
        value['entries'].append(dict(id='5' * 32, account=self.account, kind='evidence', object=original_resource))
        self.assert_rejected(self.forged_manifest(value))

    def test_false_complete_and_valid_incomplete_snapshot(self):
        value = copy.deepcopy(self.manifest)
        resource = value['entries'][0]['resources'].pop()['object']
        value['objects'] = [item for item in value['objects'] if item['sha256'] != resource]
        value['coverage']['omissions'] = [dict(account=self.account, entry=self.entry,
                                              resource='3' * 32, reason='Not retained')]
        self.assert_rejected(self.forged_manifest(value))
        value['coverage']['complete'] = False
        accepted = self.import_plain(self.plain(value))
        self.assertFalse(accepted['coverage']['complete'])

    def test_path_traversal_and_scope_mismatch(self):
        value = copy.deepcopy(self.manifest)
        value['entries'][0]['id'] = '../outside'
        self.assert_rejected(self.forged_manifest(value))
        value = copy.deepcopy(self.manifest)
        value['entries'][0]['account'] = 'f' * 32
        self.assert_rejected(self.forged_manifest(value))

    @unittest.skipUnless(shutil.which('age') and shutil.which('age-keygen'), 'Installed age tools required')
    def test_age_encrypt_offline_restore_and_negative_crypto(self):
        key = self.root / 'identity'
        subprocess.run(['age-keygen', '-o', str(key)], capture_output=True, check=True)
        recipient = subprocess.run(['age-keygen', '-y', str(key)], capture_output=True, check=True).stdout.strip().decode()
        plain = self.plain()
        encrypted = subprocess.run(['age', '-r', recipient], input=plain, capture_output=True, check=True).stdout
        source = self.root / 'snapshot.age'
        source.write_bytes(encrypted)
        accepted = import_age(source, key, self.root / 'history', archive=self.archive,
                              verification_key=self.verifier)
        self.assertEqual(accepted, self.manifest)
        for label, data in [('truncated', encrypted[:-1]), ('changed', encrypted[:-1] + bytes([encrypted[-1] ^ 1]))]:
            source.write_bytes(data)
            with self.assertRaises(ValueError):
                import_age(source, key, self.root / label, archive=self.archive,
                           verification_key=self.verifier)
            self.assertFalse((self.root / label).exists())
        # An attacker with only the public recipient can encrypt replacement content,
        # but cannot supply the independently pinned archive-writer signature.
        forged = subprocess.run(['age', '-r', recipient],
                                input=self.plain(signer=Ed25519PrivateKey.generate()),
                                capture_output=True, check=True).stdout
        source.write_bytes(forged)
        with self.assertRaises(ValueError):
            import_age(source, key, self.root / 'forged', archive=self.archive,
                       verification_key=self.verifier)
        self.assertFalse((self.root / 'forged').exists())
        second = self.root / 'other-key'
        subprocess.run(['age-keygen', '-o', str(second)], capture_output=True, check=True)
        source.write_bytes(encrypted)
        with self.assertRaises(ValueError):
            import_age(source, second, self.root / 'wrong-key', archive=self.archive,
                       verification_key=self.verifier)
        self.assertFalse((self.root / 'wrong-key').exists())
        second_recipient = subprocess.run(['age-keygen', '-y', str(second)], capture_output=True, check=True).stdout.strip().decode()
        mixed = subprocess.run(['age', '-r', recipient, '-r', second_recipient], input=plain,
                               capture_output=True, check=True).stdout
        source.write_bytes(mixed)
        with self.assertRaises(ValueError):
            import_age(source, key, self.root / 'extra-recipient', archive=self.archive,
                       verification_key=self.verifier)
        source.write_bytes(encrypted)
        plugin = self.root / 'plugin-identity'
        plugin.write_bytes(b'AGE-PLUGIN-UNTRUSTED-1NOTANATIVEIDENTITY\n')
        with self.assertRaises(ValueError):
            import_age(source, plugin, self.root / 'plugin', archive=self.archive,
                       verification_key=self.verifier)
        self.assertEqual(list(self.root.glob('.archive-decrypt-*')), [])


if __name__ == '__main__':
    unittest.main()
