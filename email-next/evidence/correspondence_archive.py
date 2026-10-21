"""Signed archive container experiment; age encryption is delegated to age.

This module stages historical objects only. It has no live identity database,
network, billing client, filesystem extraction paths or conversation effects.
"""
import hashlib
from contextlib import contextmanager
import json
import re
import shutil
import struct
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from event_encoding import decode_event

MAGIC = b'EML2ARC0'
DOMAIN = b'email2/archive-content/v0\0'
MAX_MANIFEST = 16777216
OID = re.compile(r'[0-9a-f]{32}\Z')
DIGEST = re.compile(r'[0-9a-f]{64}\Z')
PRINCIPAL = re.compile(r'enp0:[0-9a-f]{64}\Z')
DECIMAL = re.compile(r'(?:0|[1-9][0-9]*)\Z')


def exact(value, fields):
    if type(value) is not dict or set(value) != set(fields.split()):
        raise ValueError('Exact archive object members required')


def oid(value):
    if type(value) is not str or not OID.fullmatch(value) or int(value, 16) == 0:
        raise ValueError('Archive ObjectId')


def digest(value):
    if type(value) is not str or not DIGEST.fullmatch(value):
        raise ValueError('Archive digest')


def principal(value):
    if type(value) is not str or not PRINCIPAL.fullmatch(value) or int(value[5:], 16) == 0:
        raise ValueError('Archive principal')


def uint(value):
    if type(value) is not str or len(value) > 20 or not DECIMAL.fullmatch(value):
        raise ValueError('Archive uint64')
    number = int(value)
    if number > 18446744073709551615:
        raise ValueError('Archive uint64 overflow')
    return number


def ordered(rows, field):
    if type(rows) is not list or any(type(row) is not dict or field not in row for row in rows):
        raise ValueError('Archive list')
    values = [row[field] for row in rows]
    if any(type(x) is not str for x in values) or values != sorted(set(values)):
        raise ValueError('Sorted unique archive keys')


def _validate_manifest(raw, expected_archive, *, max_entries=100000, max_objects=100000):
    value = decode_event(raw, max_octets=MAX_MANIFEST)['value']
    exact(value, 'version purpose archive snapshot sequence previous createdAt accounts coverage entries objects')
    if value['version'] != '0' or value['purpose'] != 'correspondence-archive':
        raise ValueError('Unsupported archive version/purpose')
    oid(expected_archive)
    if value['archive'] != expected_archive:
        raise ValueError('Recovery kit archive mismatch')
    oid(value['snapshot'])
    sequence = uint(value['sequence'])
    uint(value['createdAt'])
    if sequence == 0:
        if value['previous'] != '':
            raise ValueError('Genesis archive predecessor')
    else:
        digest(value['previous'])
    ordered(value['accounts'], 'id')
    if not value['accounts']:
        raise ValueError('Archive account scope')
    accounts = set()
    for account in value['accounts']:
        exact(account, 'id principal')
        oid(account['id'])
        if account['principal'] != '':
            principal(account['principal'])
        accounts.add(account['id'])
    ordered(value['entries'], 'id')
    ordered(value['objects'], 'sha256')
    if len(value['entries']) > max_entries or len(value['objects']) > max_objects:
        raise ValueError('Local archive inventory limit')
    objects = {}
    for item in value['objects']:
        exact(item, 'sha256 size')
        digest(item['sha256'])
        objects[item['sha256']] = uint(item['size'])
    entries = {}
    referenced = set()
    for entry in value['entries']:
        fields = 'id account kind object'
        if entry['kind'] == 'contribution':
            fields += ' reference resources evidence'
        elif entry['kind'] == 'original-mail':
            fields += ' contribution'
        elif entry['kind'] != 'evidence':
            raise ValueError('Archive entry kind')
        exact(entry, fields)
        oid(entry['id'])
        if entry['account'] not in accounts:
            raise ValueError('Archive entry account')
        digest(entry['object'])
        referenced.add(entry['object'])
        entries[entry['id']] = entry
        if entry['kind'] == 'contribution':
            ref = entry['reference']
            exact(ref, 'principal conversation event')
            principal(ref['principal'])
            oid(ref['conversation'])
            oid(ref['event'])
            ordered(entry['resources'], 'resource')
            for resource in entry['resources']:
                exact(resource, 'resource object')
                oid(resource['resource'])
                digest(resource['object'])
                referenced.add(resource['object'])
            evidence = entry['evidence']
            if type(evidence) is not list or any(type(x) is not str for x in evidence) or evidence != sorted(set(evidence)):
                raise ValueError('Evidence entry list')
    for entry in entries.values():
        if entry['kind'] == 'original-mail' and entry['contribution'] != '':
            related = entries.get(entry['contribution'])
            if not related or related['kind'] != 'contribution' or related['account'] != entry['account']:
                raise ValueError('Original provenance relation')
        if entry['kind'] == 'contribution':
            for item in entry['evidence']:
                related = entries.get(item)
                if not related or related['kind'] != 'evidence' or related['account'] != entry['account']:
                    raise ValueError('Historical evidence relation')
    if referenced != set(objects):
        raise ValueError('Missing or unreferenced archive objects')
    coverage = value['coverage']
    exact(coverage, 'complete omissions')
    if type(coverage['complete']) is not bool or type(coverage['omissions']) is not list:
        raise ValueError('Archive coverage')
    if coverage['complete'] != (not coverage['omissions']):
        raise ValueError('False complete archive result')
    omissions = set()
    for item in coverage['omissions']:
        exact(item, 'account entry resource reason')
        if item['account'] not in accounts or type(item['reason']) is not str or not item['reason']:
            raise ValueError('Archive omission scope')
        entry = entries.get(item['entry'])
        if item['entry'] != '' and (not entry or entry['account'] != item['account']):
            raise ValueError('Archive omission entry')
        if item['resource'] != '':
            oid(item['resource'])
            if not entry or entry['kind'] != 'contribution':
                raise ValueError('Resource omission requires a contribution')
            key = (entry['id'], item['resource'])
            if key in omissions:
                raise ValueError('Duplicate archive resource omission')
            omissions.add(key)
    return value


def validate_manifest(raw, expected_archive, **limits):
    try:
        return _validate_manifest(raw, expected_archive, **limits)
    except (KeyError, TypeError) as error:
        raise ValueError('Malformed archive schema') from error


def manifest_bytes(value):
    raw = json.dumps(value, ensure_ascii=True, separators=(',', ':')).replace('/', '\\/').encode()
    validate_manifest(raw, value['archive'])
    return raw


def write_plain(manifest, objects, signing_key, output):
    """Fixture exporter; real mailbox acquisition is intentionally not implied."""
    raw = manifest_bytes(manifest)
    header = MAGIC + struct.pack('>I', len(raw)) + raw
    h = hashlib.sha256()
    output.write(header)
    h.update(header)
    for item in manifest['objects']:
        data = objects[item['sha256']]
        if len(data) != uint(item['size']) or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Export object integrity')
        output.write(data)
        h.update(data)
    output.write(signing_key.sign(DOMAIN + h.digest()))


def stage_plain(stream, destination, *, archive, verification_key, max_total=67108864,
                max_entries=100000, max_objects=100000):
    """Validate into a fresh private historical directory, or publish nothing.

    The caller must first complete age decryption/final authentication into private
    staging. This function neither decrypts nor installs a live application state.
    """
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError('Fresh archive destination required')
    used = 0
    h = hashlib.sha256()

    def read(size, *, hashed=True):
        nonlocal used
        if size < 0 or used + size > max_total:
            raise ValueError('Local archive byte limit')
        chunks = []
        remaining = size
        while remaining:
            chunk = stream.read(min(65536, remaining))
            if not chunk:
                raise ValueError('Truncated archive')
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b''.join(chunks)
        used += len(data)
        if hashed:
            h.update(data)
        return data

    temporary = Path(tempfile.mkdtemp(prefix='.archive-stage-', dir=destination.parent))
    try:
        if read(8) != MAGIC:
            raise ValueError('Archive framing')
        length = struct.unpack('>I', read(4))[0]
        if length > MAX_MANIFEST:
            raise ValueError('Archive manifest limit')
        raw = read(length)
        manifest = validate_manifest(raw, archive, max_entries=max_entries, max_objects=max_objects)
        for item in manifest['objects']:
            remaining = uint(item['size'])
            if used + remaining + 64 > max_total:
                raise ValueError('Local archive byte limit')
            checksum = hashlib.sha256()
            with (temporary / item['sha256']).open('xb') as out:
                while remaining:
                    data = read(min(65536, remaining))
                    out.write(data)
                    checksum.update(data)
                    remaining -= len(data)
            if checksum.hexdigest() != item['sha256']:
                raise ValueError('Archive object integrity')
        signature = read(64, hashed=False)
        if stream.read(1):
            raise ValueError('Trailing archive bytes')
        try:
            Ed25519PublicKey.from_public_bytes(verification_key).verify(signature, DOMAIN + h.digest())
        except (InvalidSignature, ValueError) as error:
            raise ValueError('Archive writer signature') from error
        check_contributions(manifest, temporary)
        (temporary / 'manifest.json').write_bytes(raw)
        # No account, key, checkpoint or action data is ever installed by this path.
        temporary.rename(destination)
        return manifest
    except BaseException:
        shutil.rmtree(temporary)
        raise


def check_contributions(manifest, objects):
    sizes = {item['sha256']: uint(item['size']) for item in manifest['objects']}
    for entry in manifest['entries']:
        if entry['kind'] != 'contribution':
            continue
        path = objects / entry['object']
        if sizes[entry['object']] > 1048576:
            raise ValueError('Archived event limit')
        event = decode_event(path.read_bytes())['value']
        if any(event.get(key) != val for key, val in entry['reference'].items()):
            raise ValueError('Historical contribution reference')
        operation = event.get('operation', {})
        if type(operation) is not dict:
            raise ValueError('Historical operation shape')
        inventory = operation.get('manifest')
        if inventory is None:
            if entry['resources']:
                raise ValueError('This experiment needs an explicit resource manifest')
            continue
        if type(inventory) is not list:
            raise ValueError('Historical resource inventory')
        declared = {}
        for item in inventory:
            exact(item, 'id size sha256')
            oid(item['id'])
            digest(item['sha256'])
            uint(item['size'])
            if item['id'] in declared:
                raise ValueError('Historical duplicate resource')
            declared[item['id']] = item
        included = {item['resource']: item['object'] for item in entry['resources']}
        missing = {item['resource'] for item in manifest['coverage']['omissions']
                   if item['entry'] == entry['id'] and item['resource'] != ''}
        if set(included) & missing or set(included) | missing != set(declared):
            raise ValueError('Historical resource coverage')
        for resource, obj in included.items():
            if obj != declared[resource]['sha256'] or sizes[obj] != uint(declared[resource]['size']):
                raise ValueError('Historical resource binding')


@contextmanager
def decrypted_age(ciphertext, identity_file, parent, *, age='age',
                  max_ciphertext=67108864, max_plaintext=67108864, timeout=30,
                  expected_digest=None, expected_size=None):
    """Exercise an installed age tool; private staging completes before import.

    The only accepted identity is one native X25519 key; plugins cannot be invoked
    through an imported key file. Caller-selected paths/keys remain trusted input.
    """
    import subprocess
    parent = Path(parent)
    if not parent.is_dir():
        raise ValueError('Trusted existing staging parent required')
    with tempfile.TemporaryDirectory(prefix='.archive-decrypt-', dir=parent) as root:
        root = Path(root)
        retained = root / 'ciphertext.age'
        used = 0
        checksum = hashlib.sha256()
        with Path(ciphertext).open('rb') as source, retained.open('xb') as target:
            while data := source.read(65536):
                used += len(data)
                if used > max_ciphertext:
                    raise ValueError('Local ciphertext limit')
                target.write(data)
                checksum.update(data)
        if ((expected_digest is not None and checksum.hexdigest() != expected_digest)
                or (expected_size is not None and used != expected_size)):
            raise ValueError('Archive ciphertext descriptor mismatch')
        with retained.open('rb') as source:
            header = source.read(16385)
        if not header.startswith(b'age-encryption.org/v1\n'):
            raise ValueError('Binary age v1 required')
        stanzas = []
        ended = False
        offset = 0
        for line in header.split(b'\n'):
            offset += len(line) + 1
            if line.startswith(b'-> '):
                stanzas.append(line.split(b' ')[1])
            if line.startswith(b'--- '):
                ended = offset <= 16384
                break
        if not ended or stanzas != [b'X25519']:
            raise ValueError('One native X25519 recipient required')
        with Path(identity_file).open('rb') as source:
            identity = source.read(4097)
        if len(identity) > 4096:
            raise ValueError('Local archive identity limit')
        keys = [line for line in identity.splitlines() if line and not line.startswith(b'#')]
        if len(keys) != 1 or not re.fullmatch(rb'AGE-SECRET-KEY-1[0-9A-Z]+', keys[0]):
            raise ValueError('Native X25519 recovery identity required')
        key_file = root / 'identity'
        key_file.write_bytes(keys[0] + b'\n')
        key_file.chmod(0o600)
        plaintext = root / 'plaintext'
        try:
            result = subprocess.run([age, '--decrypt', '--identity', str(key_file),
                                     '--output', str(plaintext), str(retained)],
                                    capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            raise ValueError('Archive decryption timeout') from error
        if result.returncode:
            raise ValueError('Archive decryption/final authentication failed')
        if plaintext.stat().st_size > max_plaintext:
            raise ValueError('Local plaintext limit')
        yield plaintext, checksum.hexdigest(), used


def import_age(ciphertext, identity_file, destination, *, archive, verification_key,
               age='age', max_ciphertext=67108864, max_plaintext=67108864, timeout=30):
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError('Fresh archive destination required')
    with decrypted_age(ciphertext, identity_file, destination.parent, age=age,
                       max_ciphertext=max_ciphertext, max_plaintext=max_plaintext, timeout=timeout) as result:
        plaintext, _, _ = result
        with plaintext.open('rb') as source:
            return stage_plain(source, destination, archive=archive,
                               verification_key=verification_key, max_total=max_plaintext)
