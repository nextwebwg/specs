"""RFC5869 known-answer evidence for cryptography, not a production KDF API."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re

import cryptography
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand

SOURCE_SHA256 = '7a40eb3835b35fc947eb12a2ed614db079d43b26e50dbc537c31fba16397089c'
FIXTURE = Path(__file__).with_name('hkdf-rfc5869-vectors.json')


def extract_source(raw):
    """Reproduce fixture data from the pinned RFC text, without computing outputs."""
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('RFC5869 source snapshot differs')
    text = raw.decode('ascii')
    cases = []
    for number in range(1, 8):
        start = text.index(f'A.{number}.  Test Case {number}')
        end = text.index(f'A.{number + 1}.  Test Case {number + 1}', start) if number < 7 else text.index("Authors' Addresses", start)
        block = text[start:end]
        row = {'case': number, 'hash': re.search(r'Hash = (SHA-\d+)', block)[1], 'length': int(re.search(r'L    = (\d+)', block)[1])}
        for field in ('IKM', 'salt', 'info', 'PRK', 'OKM'):
            match = re.search(r'^   ' + field + r'\s*= (.*)', block, re.M)
            value = match[1]
            if value.startswith('not provided'):
                row[field] = None
            elif value.startswith('(0 octets)'):
                row[field] = ''
            else:
                tail = block[match.start():]
                value = re.match(r'^   \w+\s*= 0x([0-9a-f]+(?:\n          [0-9a-f]+)*) \((\d+) octets\)', tail)
                if value is None:
                    raise ValueError(f'Unsupported vector field {number}/{field}')
                hex_value = ''.join(value[1].split())
                if len(bytes.fromhex(hex_value)) != int(value[2]):
                    raise ValueError('Source vector length disagrees')
                row[field] = hex_value
        cases.append(row)
    return cases


def load_vectors():
    fixture = json.loads(FIXTURE.read_text())
    if fixture['source_sha256'] != SOURCE_SHA256 or [v['case'] for v in fixture['vectors']] != list(range(1, 8)):
        raise ValueError('Unexpected fixture provenance or case set')
    return fixture['vectors']


def check_vector(v):
    algorithm = {'SHA-256': hashes.SHA256, 'SHA-1': hashes.SHA1}[v['hash']]()
    ikm, info = bytes.fromhex(v['IKM']), bytes.fromhex(v['info'])
    salt = None if v['salt'] is None else bytes.fromhex(v['salt'])
    # Extract's default is HashLen zero octets; HMAC is the established library API.
    extractor = hmac.HMAC(bytes(algorithm.digest_size) if salt is None else salt, algorithm)
    extractor.update(ikm)
    prk = extractor.finalize()
    if prk != bytes.fromhex(v['PRK']):
        raise AssertionError(f"Case {v['case']}: PRK mismatch")
    expected = bytes.fromhex(v['OKM'])
    expanded = HKDFExpand(algorithm, v['length'], info).derive(prk)
    # Keep salt=None distinct from explicit b'' at the public HKDF API boundary.
    combined = HKDF(algorithm, v['length'], salt=salt, info=info).derive(ikm)
    if expanded != expected or combined != expected:
        raise AssertionError(f"Case {v['case']}: OKM mismatch")


def check_sha256_boundaries():
    # This is the per-Expand primitive bound, not an email/application size limit.
    prk, ikm, salt, info = bytes(range(32)), b'fixture input', b'fixture salt', b'fixture context'
    for length in (0, 1, 8159, 8160):
        if len(HKDFExpand(hashes.SHA256(), length, info).derive(prk)) != length:
            raise AssertionError('Expand output length mismatch')
        if len(HKDF(hashes.SHA256(), length, salt=salt, info=info).derive(ikm)) != length:
            raise AssertionError('HKDF output length mismatch')
    for factory in (lambda: HKDFExpand(hashes.SHA256(), 8161, info), lambda: HKDF(hashes.SHA256(), 8161, salt=salt, info=info)):
        try:
            factory()
        except ValueError:
            continue
        raise AssertionError('Over-limit construction was not rejected')


def run(source=None):
    vectors = load_vectors()
    if source is not None and extract_source(Path(source).read_bytes()) != vectors:
        raise AssertionError('Fixture differs from pinned source')
    for vector in vectors:
        check_vector(vector)
    check_sha256_boundaries()
    return {'python': platform.python_version(), 'cryptography': cryptography.__version__,
            'backend': backend.openssl_version_text(), 'source_sha256': SOURCE_SHA256,
            'source_rechecked': source is not None, 'known_answer_cases': 7,
            'checks_per_case': ['HMAC PRK', 'HKDFExpand OKM', 'HKDF OKM'],
            'sha256_expand_lengths_accepted': [0, 1, 8159, 8160], 'sha256_expand_length_rejected': 8161,
            'scope': 'cryptography library evidence; not the pinned OpenMLS implementation or end-to-end conformance'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Optional pinned RFC5869 text for exact fixture reproduction')
    args = parser.parse_args()
    print(json.dumps(run(args.source), indent=2))
