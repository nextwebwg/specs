"""Signed multi-file collection acceptance; never installs live account authority."""
import hashlib
import json
import shutil
import struct
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from correspondence_archive import (MAX_MANIFEST, decrypted_age, digest, exact,
                                    oid, ordered, principal, stage_plain, uint)
from event_encoding import decode_event

MAGIC = b'EML2SET0'
DOMAIN = b'email2/archive-set/v0\0'
INDEX_DOMAIN = b'email2/archive-set-index/v0\0'


def account_index(entries):
    h = hashlib.sha256(INDEX_DOMAIN)
    for entry in sorted(entries, key=lambda item: item['id']):
        raw = json.dumps(entry, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')
        h.update(struct.pack('>Q', len(raw)))
        h.update(raw)
    return h.hexdigest()



def validate_scopes(accounts):
    ordered(accounts, 'id')
    if not accounts:
        raise ValueError('Archive-set account scope')
    identifiers = set()
    for account in accounts:
        exact(account, 'id principal selection mode cutoff entries digest')
        oid(account['id'])
        oid(account['selection'])
        if account['principal'] != '':
            principal(account['principal'])
        if account['mode'] not in ('all-retained', 'selected'):
            raise ValueError('Archive selection mode')
        uint(account['cutoff'])
        uint(account['entries'])
        digest(account['digest'])
        identifiers.add(account['id'])
    return identifiers

def validate_catalog(value, archive):
    try:
        exact(value, 'version purpose archive set generation previous firstSequence previousPart accounts parts complete omissions')
        if value['version'] != '0' or value['purpose'] != 'correspondence-archive-set' or value['archive'] != archive:
            raise ValueError('Archive-set version/purpose/identity')
        oid(archive)
        oid(value['set'])
        for counter, previous in [('generation', 'previous'), ('firstSequence', 'previousPart')]:
            if uint(value[counter]) == 0:
                if value[previous] != '':
                    raise ValueError('Genesis archive-set predecessor')
            else:
                digest(value[previous])
        accounts = validate_scopes(value['accounts'])
        if type(value['parts']) is not list or not value['parts']:
            raise ValueError('Nonempty archive-set parts required')
        snapshots, ciphertexts = set(), set()
        first = uint(value['firstSequence'])
        for offset, part in enumerate(value['parts']):
            exact(part, 'snapshot sequence ciphertext size')
            oid(part['snapshot'])
            digest(part['ciphertext'])
            uint(part['size'])
            sequence = uint(part['sequence'])
            if sequence != first + offset or part['snapshot'] in snapshots or part['ciphertext'] in ciphertexts:
                raise ValueError('Archive-set sequence or duplicate part')
            snapshots.add(part['snapshot'])
            ciphertexts.add(part['ciphertext'])
        if type(value['complete']) is not bool or type(value['omissions']) is not list:
            raise ValueError('Archive-set completeness')
        for item in value['omissions']:
            exact(item, 'account reason')
            if item['account'] not in accounts or type(item['reason']) is not str or not item['reason']:
                raise ValueError('Archive-set omission')
        return value
    except (TypeError, KeyError) as error:
        raise ValueError('Malformed archive-set schema') from error


def signed_catalog(value, signer):
    validate_catalog(value, value['archive'])
    raw = json.dumps(value, ensure_ascii=True, separators=(',', ':')).encode()
    if len(raw) > MAX_MANIFEST:
        raise ValueError('Archive-set manifest limit')
    body = MAGIC + struct.pack('>I', len(raw)) + raw
    return body + signer.sign(DOMAIN + hashlib.sha256(body).digest())


def read_catalog(source, archive, verifier):
    raw = source.read(MAX_MANIFEST + 77)
    if len(raw) < 76 or raw[:8] != MAGIC:
        raise ValueError('Archive-set framing')
    length = struct.unpack('>I', raw[8:12])[0]
    if length > MAX_MANIFEST or len(raw) != 12 + length + 64:
        raise ValueError('Archive-set length/trailing bytes')
    try:
        Ed25519PublicKey.from_public_bytes(verifier).verify(raw[-64:], DOMAIN + hashlib.sha256(raw[:-64]).digest())
    except (InvalidSignature, ValueError) as error:
        raise ValueError('Archive-set writer signature') from error
    value = decode_event(raw[12:-64], max_octets=MAX_MANIFEST)['value']
    return validate_catalog(value, archive), raw


def restore_set(catalog_file, identity_file, parts, destination, *, archive,
                verification_key, known_head=None, expected_catalog=None, max_bytes=268435456,
                max_entries=1000000, before_publish=None):
    destination = Path(destination)
    if not destination.parent.is_dir():
        raise ValueError('Trusted restore parent required')
    if expected_catalog is not None:
        exact(expected_catalog, 'archive set accounts complete ciphertext size')
        validate_scopes(expected_catalog['accounts'])
        digest(expected_catalog['ciphertext'])
        uint(expected_catalog['size'])
    with decrypted_age(catalog_file, identity_file, destination.parent,
                       max_ciphertext=min(67108864, max_bytes),
                       max_plaintext=min(67108864, max_bytes),
                       expected_digest=expected_catalog['ciphertext'] if expected_catalog else None,
                       expected_size=uint(expected_catalog['size']) if expected_catalog else None) as result:
        catalog_plain, catalog_digest, catalog_size = result
        with catalog_plain.open('rb') as source:
            catalog, catalog_raw = read_catalog(source, archive, verification_key)
        if expected_catalog is not None and any(catalog[key] != expected_catalog[key]
                                                for key in ('archive', 'set', 'accounts', 'complete')):
            raise ValueError('Transfer grant/catalog mismatch')
    receipt = dict(archive=archive, set=catalog['set'], generation=catalog['generation'],
                   ciphertext=catalog_digest, size=str(catalog_size))
    if known_head is not None:
        exact(known_head, 'archive set generation ciphertext size')
        if known_head['archive'] != archive:
            raise ValueError('Known head archive mismatch')
        oid(known_head['set'])
        uint(known_head['size'])
        old, new = uint(known_head['generation']), uint(catalog['generation'])
        digest(known_head['ciphertext'])
        if new < old or (new == old and receipt != known_head):
            raise ValueError('Known archive-set rollback or conflict')
        if new > old and (new != old + 1 or catalog['previous'] != known_head['ciphertext']):
            raise ValueError('Archive-set predecessor proof unavailable')

    def already_accepted():
        if not destination.exists():
            return False
        try:
            retained = json.loads((destination / 'completion.json').read_bytes())
        except (OSError, ValueError) as error:
            raise ValueError('Existing historical destination is not this completed set') from error
        if retained != receipt:
            raise ValueError('Existing archive-set completion conflict')
        return True

    if already_accepted():
        return receipt
    budget = catalog_size
    for part in catalog['parts']:
        budget += uint(part['size'])
        if budget > max_bytes:
            raise ValueError('Local collection ciphertext budget')
    staging = Path(tempfile.mkdtemp(prefix='.archive-set-', dir=destination.parent))
    try:
        scopes = {item['id']: item for item in catalog['accounts']}
        entries = {account: [] for account in scopes}
        seen_entries, declared_accounts = set(), set()
        prior = catalog['previousPart']
        complete = not catalog['omissions']
        total_entries = 0
        for part in catalog['parts']:
            if part['ciphertext'] not in parts:
                raise ValueError('Missing archive-set member')
            with decrypted_age(parts[part['ciphertext']], identity_file, staging,
                               expected_digest=part['ciphertext'], expected_size=uint(part['size'])) as result:
                plaintext, _, _ = result
                with plaintext.open('rb') as source:
                    manifest = stage_plain(source, staging / part['snapshot'], archive=archive,
                                           verification_key=verification_key)
            if (manifest['snapshot'] != part['snapshot'] or manifest['sequence'] != part['sequence']
                    or manifest['previous'] != prior):
                raise ValueError('Archive-set member binding')
            prior = part['ciphertext']
            complete = complete and manifest['coverage']['complete']
            for account in manifest['accounts']:
                if account['id'] not in scopes or account['principal'] != scopes[account['id']]['principal']:
                    raise ValueError('Archive-set account/principal mismatch')
                declared_accounts.add(account['id'])
            for entry in manifest['entries']:
                total_entries += 1
                if total_entries > max_entries:
                    raise ValueError('Local collection entry budget')
                if entry['id'] in seen_entries:
                    raise ValueError('Duplicate collection entry ID')
                seen_entries.add(entry['id'])
                entries[entry['account']].append(entry)
        if declared_accounts != set(scopes) or complete != catalog['complete']:
            raise ValueError('Archive-set completeness mismatch')
        for account, records in entries.items():
            if len(records) != uint(scopes[account]['entries']) or account_index(records) != scopes[account]['digest']:
                raise ValueError('Frozen selection inventory mismatch')
        (staging / 'catalog.bin').write_bytes(catalog_raw)
        (staging / 'completion.json').write_text(json.dumps(receipt))
        if before_publish is not None:
            before_publish()
        if already_accepted():
            return receipt
        # All accepted part directories remain private until this one publication.
        # Process-exit atomicity is exercised; power-loss durability is not claimed.
        staging.rename(destination)
        return receipt
    finally:
        if staging.exists():
            shutil.rmtree(staging)
