"""Encrypted collection acceptance and process-exit publication boundaries."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from archive_set import INDEX_DOMAIN, account_index, restore_set, signed_catalog
from correspondence_archive import write_plain


@unittest.skipUnless(shutil.which('age') and shutil.which('age-keygen'), 'Installed age tools required')
class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.signer = Ed25519PrivateKey.generate()
        self.verifier = self.signer.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.archive = 'a' * 32
        self.account = 'b' * 32
        self.key = self.root / 'identity'
        subprocess.run(['age-keygen', '-o', str(self.key)], capture_output=True, check=True)
        self.recipient = subprocess.run(['age-keygen', '-y', str(self.key)], capture_output=True, check=True).stdout.strip().decode()
        self.manifests, self.objects, self.parts, self.sources = [], [], [], {}
        previous = ''
        for i in range(2):
            event = dict(version='0', purpose='contribution', principal='enp0:' + 'c' * 64,
                         audience=['enp0:' + 'c' * 64], conversation='d' * 32, event=f'{i + 1:032x}',
                         operation=dict(kind='message', text=f'Historical contribution {i}', replyTo=[]))
            data = json.dumps(event).encode()
            digest = hashlib.sha256(data).hexdigest()
            entry = dict(id=f'{i + 1:032x}', account=self.account, kind='contribution', object=digest,
                         reference={k: event[k] for k in ('principal', 'conversation', 'event')}, resources=[], evidence=[])
            manifest = dict(version='0', purpose='correspondence-archive', archive=self.archive,
                            snapshot=f'{i + 10:032x}', sequence=str(i), previous=previous, createdAt='0',
                            accounts=[dict(id=self.account, principal='')],
                            coverage=dict(complete=True, omissions=[]), entries=[entry],
                            objects=[dict(sha256=digest, size=str(len(data)))])
            self.manifests.append(manifest)
            self.objects.append({digest: data})
            part = self.encrypt_part(i)
            self.parts.append(part)
            previous = part['ciphertext']
        frozen = [entry for manifest in self.manifests for entry in manifest['entries']]
        self.catalog = dict(version='0', purpose='correspondence-archive-set', archive=self.archive,
                            set='e' * 32, generation='0', previous='', firstSequence='0', previousPart='',
                            accounts=[dict(id=self.account, principal='', selection='f' * 32,
                                           mode='all-retained', cutoff='2', entries='2', digest=account_index(frozen))],
                            parts=copy.deepcopy(self.parts), complete=True, omissions=[])
        self.target = self.root / 'completed-history'
        self.live = self.root / 'live.sqlite'
        self.live.write_bytes(b'current authority and actions')

    def encrypt(self, raw):
        return subprocess.run(['age', '-r', self.recipient], input=raw, capture_output=True, check=True).stdout

    def encrypt_part(self, number):
        output = io.BytesIO()
        write_plain(self.manifests[number], self.objects[number], self.signer, output)
        raw = self.encrypt(output.getvalue())
        digest = hashlib.sha256(raw).hexdigest()
        path = self.root / digest
        path.write_bytes(raw)
        self.sources[digest] = path
        return dict(snapshot=self.manifests[number]['snapshot'], sequence=self.manifests[number]['sequence'],
                    ciphertext=digest, size=str(len(raw)))

    def catalog_file(self, catalog=None, signer=None):
        path = self.root / 'catalog.age'
        path.write_bytes(self.encrypt(signed_catalog(catalog or self.catalog, signer or self.signer)))
        return path

    def restore(self, catalog=None, **kwargs):
        return restore_set(self.catalog_file(catalog), self.key, self.sources, self.target,
                           archive=self.archive, verification_key=self.verifier, **kwargs)

    def assert_no_publish(self):
        self.assertFalse(self.target.exists())
        self.assertEqual(self.live.read_bytes(), b'current authority and actions')
        self.assertEqual(list(self.root.glob('.archive-set-*')), [])
        self.assertEqual(list(self.root.glob('.archive-decrypt-*')), [])

    def test_all_encrypted_members_publish_together(self):
        receipt = self.restore()
        self.assertEqual(receipt['set'], self.catalog['set'])
        for manifest, objects in zip(self.manifests, self.objects):
            for digest, data in objects.items():
                self.assertEqual((self.target / manifest['snapshot'] / digest).read_bytes(), data)
        self.assertEqual(self.live.read_bytes(), b'current authority and actions')

    def test_missing_member_does_not_publish_earlier_valid_part(self):
        self.sources.pop(self.parts[1]['ciphertext'])
        with self.assertRaises(ValueError):
            self.restore()
        self.assert_no_publish()

    def test_substituted_encrypted_part(self):
        self.sources[self.parts[1]['ciphertext']] = self.sources[self.parts[0]['ciphertext']]
        with self.assertRaises(ValueError):
            self.restore()
        self.assert_no_publish()

    def test_omitted_descriptor_cannot_change_frozen_inventory(self):
        catalog = copy.deepcopy(self.catalog)
        catalog['parts'].pop()
        with self.assertRaises(ValueError):
            self.restore(catalog)
        self.assert_no_publish()

    def test_duplicate_entry_across_individually_valid_archives(self):
        self.manifests[1]['entries'][0]['id'] = self.manifests[0]['entries'][0]['id']
        self.catalog['parts'][1] = self.encrypt_part(1)
        with self.assertRaises(ValueError):
            self.restore()
        self.assert_no_publish()

    def test_bad_index_and_counter_overflow(self):
        catalog = copy.deepcopy(self.catalog)
        catalog['accounts'][0]['digest'] = '0' * 64
        with self.assertRaises(ValueError):
            self.restore(catalog)
        self.assert_no_publish()
        catalog = copy.deepcopy(self.catalog)
        catalog['parts'][1]['sequence'] = '18446744073709551616'
        with self.assertRaises(ValueError):
            self.restore(catalog)
        self.assert_no_publish()

    def test_independent_catalog_verifier_rejects_forged_origin(self):
        path = self.catalog_file(signer=Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):
            restore_set(path, self.key, self.sources, self.target, archive=self.archive,
                        verification_key=self.verifier)
        self.assert_no_publish()

    def test_exact_retry_is_idempotent(self):
        source = self.catalog_file()
        first = restore_set(source, self.key, self.sources, self.target, archive=self.archive,
                            verification_key=self.verifier)
        for path in self.sources.values():
            path.unlink()
        self.assertEqual(restore_set(source, self.key, {}, self.target, archive=self.archive,
                                    verification_key=self.verifier), first)
        self.assertEqual(len([p for p in self.target.iterdir() if p.is_dir()]), 2)

    def test_reencrypted_catalog_under_same_set_is_a_conflict(self):
        self.restore()
        with self.assertRaises(ValueError):
            self.restore()
        self.assertTrue(self.target.exists())

    def test_known_head_rollback_and_missing_predecessor(self):
        head = dict(archive=self.archive, set='1' * 32, generation='1', ciphertext='2' * 64, size='100')
        with self.assertRaises(ValueError):
            self.restore(known_head=head)
        catalog = copy.deepcopy(self.catalog)
        catalog['generation'] = '3'
        catalog['previous'] = head['ciphertext']
        with self.assertRaises(ValueError):
            self.restore(catalog, known_head=head)
        self.assert_no_publish()

    def test_declared_collection_omission_is_not_complete(self):
        catalog = copy.deepcopy(self.catalog)
        catalog['complete'] = False
        catalog['omissions'] = [dict(account=self.account, reason='Only retained local history available')]
        self.restore(catalog)
        from archive_set import read_catalog
        with (self.target / 'catalog.bin').open('rb') as source:
            accepted, _ = read_catalog(source, self.archive, self.verifier)
        self.assertFalse(accepted['complete'])

    def test_resource_budget_failure_is_not_partial_success(self):
        with self.assertRaises(ValueError):
            self.restore(max_bytes=100)
        self.assert_no_publish()

    def test_real_process_exit_before_publication(self):
        source = self.catalog_file()
        script = '''import json,os,sys
from archive_set import restore_set
restore_set(sys.argv[1],sys.argv[2],json.loads(sys.argv[3]),sys.argv[4],archive=sys.argv[5],verification_key=bytes.fromhex(sys.argv[6]),before_publish=lambda:os._exit(71))
'''
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).parent.resolve()))
        result = subprocess.run([sys.executable, '-c', script, str(source), str(self.key),
                                 json.dumps({k: str(v) for k, v in self.sources.items()}), str(self.target),
                                 self.archive, self.verifier.hex()], env=env, capture_output=True)
        self.assertEqual(result.returncode, 71, result.stderr.decode())
        self.assertFalse(self.target.exists())
        self.assertEqual(self.live.read_bytes(), b'current authority and actions')
        stages = list(self.root.glob('.archive-set-*'))
        self.assertEqual(len(stages), 1)
        self.assertEqual(stages[0].stat().st_mode & 0o777, 0o700)
        # A later explicit retry revalidates the original files; abandoned staging
        # does not count as acceptance or prevent the legitimate collection.
        self.assertEqual(restore_set(source, self.key, self.sources, self.target,
                                     archive=self.archive, verification_key=self.verifier)['set'], self.catalog['set'])


class IndexVectorTests(unittest.TestCase):
    def test_exact_length_prefixed_ascii_index_and_order(self):
        records = [dict(id='2' * 32, account='a' * 32, kind='evidence', object='b' * 64),
                   dict(id='1' * 32, account='a' * 32, kind='evidence', object='c' * 64)]
        expected = hashlib.sha256(INDEX_DOMAIN)
        for raw in [b'{"account":"' + b'a' * 32 + b'","id":"' + b'1' * 32 + b'","kind":"evidence","object":"' + b'c' * 64 + b'"}',
                    b'{"account":"' + b'a' * 32 + b'","id":"' + b'2' * 32 + b'","kind":"evidence","object":"' + b'b' * 64 + b'"}']:
            expected.update(struct.pack('>Q', len(raw)) + raw)
        self.assertEqual(account_index(records), expected.hexdigest())
        self.assertEqual(account_index(list(reversed(records))), expected.hexdigest())
        self.assertEqual(account_index([]), hashlib.sha256(INDEX_DOMAIN).hexdigest())


if __name__ == '__main__':
    unittest.main()
