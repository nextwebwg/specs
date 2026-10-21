"""Signed history disclosure/acceptance experiment, not a transport or enrollment service.

Authority checks can join the caller's identity-store transaction. They are only
snapshots when called alone; a real sender must serialize its final handoff and
persist the approved immutable outbox. Admission objects must be journaled before
use in a production receiver. No incoming record installs identity anchors.
"""
import base64
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from archive_set import restore_set, validate_scopes
from correspondence_archive import digest, exact, oid, principal, uint
from event_encoding import decode_event, encode_event
from identity_bundle import decode_identity_bundle

FIELDS = {
    'request': 'version purpose transfer source target recipient accounts receipt notBefore notAfter',
    'grant': 'version purpose transfer request source target scope archive set verificationKey catalog complete notBefore notAfter',
    'receipt': 'version purpose transfer grant source target catalog result notBefore notAfter',
    'cancel': 'version purpose transfer request grant source target by notBefore notAfter',
}
RECIPIENT = re.compile(r'age1[023456789acdefghjklmnpqrstuvwxyz]{58}\Z')


def endpoint(ref):
    exact(ref, 'principal device state binding key')
    principal(ref['principal'])
    device = ref['device']
    if type(device) is not str or not re.fullmatch(r'end0:[0-9a-f]{64}', device) or int(device[5:], 16) == 0:
        raise ValueError('History device identifier')
    for key in ('state', 'binding', 'key'):
        digest(ref[key])


def validate(value, kind):
    try:
        exact(value, FIELDS[kind])
        if value['version'] != '0' or value['purpose'] != 'history-transfer-' + kind:
            raise ValueError('History-transfer version/purpose')
        oid(value['transfer'])
        endpoint(value['source'])
        endpoint(value['target'])
        if (value['source']['principal'], value['source']['device']) == (value['target']['principal'], value['target']['device']):
            raise ValueError('Distinct history endpoints required')
        if uint(value['notAfter']) < uint(value['notBefore']):
            raise ValueError('History-transfer interval')
        if kind == 'request':
            if type(value['recipient']) is not str or not RECIPIENT.fullmatch(value['recipient']):
                raise ValueError('Native X25519 recipient required')
            if value['receipt'] != 'import-result' or type(value['accounts']) is not list:
                raise ValueError('History request accounts/result')
            for account in value['accounts']:
                oid(account)
            if value['accounts'] != sorted(set(value['accounts'])):
                raise ValueError('Sorted unique requested accounts')
        elif kind == 'grant':
            digest(value['request'])
            validate_scopes(value['scope'])
            oid(value['archive'])
            oid(value['set'])
            digest(value['verificationKey'])
            exact(value['catalog'], 'sha256 size')
            digest(value['catalog']['sha256'])
            uint(value['catalog']['size'])
            if type(value['complete']) is not bool:
                raise ValueError('History grant completeness')
        elif kind == 'cancel':
            digest(value['request'])
            if value['grant'] != '':
                digest(value['grant'])
            if value['by'] not in ('source', 'target'):
                raise ValueError('History cancellation actor')
        else:
            digest(value['grant'])
            digest(value['catalog'])
            if value['result'] not in ('imported', 'imported-incomplete'):
                raise ValueError('History import result')
    except (KeyError, TypeError) as error:
        raise ValueError('Malformed history-transfer schema') from error
    return value


def frame(kind, raw):
    return ('email2/history-transfer/' + kind + '/v0').encode() + b'\0' + struct.pack('>I', len(raw)) + raw


def unpack(wrapper, kind):
    if isinstance(wrapper, bytes):
        wrapper = decode_event(wrapper, max_octets=2097152)['value']
    exact(wrapper, 'payload signature')
    encoded, signature = wrapper['payload'], wrapper['signature']
    if type(encoded) is not str or len(encoded) > 1398104 or type(signature) is not str or not re.fullmatch(r'[0-9a-f]{128}', signature):
        raise ValueError('History-transfer proof encoding')
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('History-transfer base64') from error
    if base64.b64encode(raw).decode() != encoded:
        raise ValueError('Canonical history-transfer base64')
    value = validate(decode_event(raw)['value'], kind)
    signature = bytes.fromhex(signature)
    return raw, signature, value, hashlib.sha256(frame(kind, raw) + signature).hexdigest()


def sign_record(kind, raw, signer):
    validate(decode_event(raw)['value'], kind)
    return dict(payload=base64.b64encode(raw).decode(), signature=signer.sign(frame(kind, raw)).hex())


@contextmanager
def authority_snapshot(store):
    owned = not store.db.in_transaction
    if owned:
        store.db.execute('BEGIN IMMEDIATE')
    try:
        yield
        if owned:
            store.db.execute('COMMIT')
    except BaseException:
        if owned and store.db.in_transaction:
            store.db.execute('ROLLBACK')
        raise


def authorize(store, ref, role, time, trust_policy):
    """Retained endpoint authorization, not a new head/context or freshness proof.

    Caller holds authority_snapshot through its state mutation. Walk only locally
    accepted history, checking the same binding at every step, including anchor.
    """
    checked = store._check_device_locked(ref['principal'], ref['device'], bytes.fromhex(ref['key']),
                                         role, time, trust_policy)
    if checked['status'] != 'authorized-unverified' or checked['binding'] != ref['binding']:
        raise ValueError('History endpoint not currently authorized: ' + checked['status'])
    current = checked['head']
    seen = set()
    for _ in range(1024):
        if current in seen:
            raise ValueError('Retained authority ancestry cycle')
        seen.add(current)
        transition = store.db.execute('SELECT previous,bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',
                                      (ref['principal'], current)).fetchone()
        if transition:
            bundle = decode_identity_bundle(transition[1])
            state = next(item['value'] for item in bundle['states'] if item['digest'] == current)
            bindings = {item['digest']: item['value'] for item in bundle['bindings']}
        else:
            # A claim is an anchor only if it is the locally pinned genesis.
            pin = store.db.execute('SELECT digest FROM pins WHERE principal=?', (ref['principal'],)).fetchone()
            if pin is None or pin[0] != current:
                break
            row = store.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',
                                   (ref['principal'], current)).fetchone()
            if row is None:
                break
            record = json.loads(row[0])
            state = decode_event(base64.b64decode(record['state'], validate=True))['value']
            raw = base64.b64decode(record['binding'], validate=True)
            bindings = {hashlib.sha256(raw).hexdigest(): decode_event(raw)['value']}
        selected = next((item for item in state['bindings'] if item['device'] == ref['device']), None)
        binding = bindings.get(ref['binding'])
        if (ref['device'] in state['revoked'] or selected is None or selected['digest'] != ref['binding']
                or binding is None or binding['signingKey'] != ref['key'] or role not in binding['roles']):
            raise ValueError('Retained authority binding changed along accepted ancestry')
        if current == ref['state']:
            return dict(head=checked['head'], before=uint(binding['notBefore']), after=uint(binding['notAfter']))
        if transition is None:
            break
        current = transition[0]
    raise ValueError('History endpoint state is not an available accepted ancestor')


def verify_record(wrapper, kind, store, *, time, trust_policy):
    if trust_policy not in ('allow-unverified', 'require-verification'):
        raise ValueError('Explicit current identity policy required')
    raw, signature, value, reference = unpack(wrapper, kind)
    earliest, latest = uint(time['earliest']), uint(time['latest'])
    if earliest > latest or earliest < uint(value['notBefore']) or latest > uint(value['notAfter']):
        raise ValueError('History-transfer validity or uncertain time')
    with authority_snapshot(store):
        refs = (value['by'],) if kind == 'cancel' else ('target',) if kind == 'receipt' else ('source', 'target')
        authorities = {name: authorize(store, value[name], 'send' if name == 'source' else 'receive', time, trust_policy)
                       for name in refs}
        if any(uint(value['notBefore']) < authority['before'] or uint(value['notAfter']) > authority['after']
               for authority in authorities.values()):
            raise ValueError('History interval exceeds endpoint authority')
        signer = value[value['by']] if kind == 'cancel' else value['source'] if kind == 'grant' else value['target']
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(signer['key'])).verify(signature, frame(kind, raw))
        except (ValueError, InvalidSignature) as error:
            raise ValueError('History-transfer signature') from error
    return dict(raw=raw, value=value, reference=reference, sourceHead=authorities.get('source', {}).get('head', ''),
                targetHead=authorities.get('target', {}).get('head', ''))


def correlate(request, grant):
    r, g = request['value'], grant['value']
    if g['request'] != request['reference'] or any(r[key] != g[key] for key in ('transfer', 'source', 'target')):
        raise ValueError('Grant does not match retained request')
    if uint(g['notBefore']) < uint(r['notBefore']) or uint(g['notAfter']) > uint(r['notAfter']):
        raise ValueError('Grant expands request interval')
    if r['accounts'] and not {scope['id'] for scope in g['scope']}.issubset(r['accounts']):
        raise ValueError('Grant expands requested accounts')


def check_recipient(recipient, *, age='age'):
    if type(recipient) is not str or not RECIPIENT.fullmatch(recipient):
        raise ValueError('Native X25519 recipient required')
    result = subprocess.run([age, '-r', recipient], input=b'', capture_output=True, timeout=5)
    if result.returncode:
        raise ValueError('Invalid X25519 recipient encoding')


def approve_grant(request_wrapper, grant_raw, signer, store, *, time, trust_policy, approved_payload_digest):
    """Approval digest is trusted UI/policy input, never obtained from a message."""
    if hashlib.sha256(grant_raw).hexdigest() != approved_payload_digest:
        raise ValueError('Missing exact source disclosure approval')
    with authority_snapshot(store):
        request = verify_record(request_wrapper, 'request', store, time=time, trust_policy=trust_policy)
        check_recipient(request['value']['recipient'])
        wrapper = sign_record('grant', grant_raw, signer)
        grant = verify_record(wrapper, 'grant', store, time=time, trust_policy=trust_policy)
        correlate(request, grant)
    return wrapper


def check_release(request_wrapper, grant_wrapper, store, *, time, trust_policy, prepared_reference):
    """Local snapshot only; actual file transport must serialize its final handoff."""
    with authority_snapshot(store):
        request = verify_record(request_wrapper, 'request', store, time=time, trust_policy=trust_policy)
        grant = verify_record(grant_wrapper, 'grant', store, time=time, trust_policy=trust_policy)
        correlate(request, grant)
        if grant['reference'] != prepared_reference:
            raise ValueError('Grant has no current prepared disclosure permission')
    return grant['reference']


@dataclass(frozen=True)
class AcceptedGrant:
    request: bytes
    grant: bytes
    reference: str
    source_head: str
    target_head: str


def admit_grant(request_wrapper, grant_wrapper, store, *, time, trust_policy, expected_grant_reference):
    with authority_snapshot(store):
        request = verify_record(request_wrapper, 'request', store, time=time, trust_policy=trust_policy)
        grant = verify_record(grant_wrapper, 'grant', store, time=time, trust_policy=trust_policy)
        correlate(request, grant)
        if grant['reference'] != expected_grant_reference:
            raise ValueError('Unexpected proposal/grant acceptance')
        return AcceptedGrant(request['raw'], grant['raw'], grant['reference'], grant['sourceHead'], grant['targetHead'])


@dataclass(frozen=True)
class CompletedImport:
    admission: str
    receipt: bytes
    destination: str


def import_history(admission, catalog_file, identity_file, part_files, destination):
    """The caller must persist authenticated admission before receiving/importing."""
    if not isinstance(admission, AcceptedGrant):
        raise ValueError('Locally accepted grant required')
    request = decode_event(admission.request)['value']
    grant = decode_event(admission.grant)['value']
    # Derive the public recipient from a sanitized local key copy, never a plugin.
    with Path(identity_file).open('rb') as source:
        raw = source.read(4097)
    keys = [line for line in raw.splitlines() if line and not line.startswith(b'#')]
    if len(raw) > 4096 or len(keys) != 1 or not re.fullmatch(rb'AGE-SECRET-KEY-1[0-9A-Z]+', keys[0]):
        raise ValueError('Native target transfer identity required')
    with tempfile.TemporaryDirectory(prefix='.history-key-', dir=Path(destination).parent) as root:
        retained = Path(root) / 'identity'
        retained.write_bytes(keys[0] + b'\n')
        retained.chmod(0o600)
        result = subprocess.run(['age-keygen', '-y', str(retained)], capture_output=True, timeout=5)
        if result.returncode or result.stdout.strip().decode() != request['recipient']:
            raise ValueError('Wrong request-specific archive identity')
        expected = dict(archive=grant['archive'], set=grant['set'], accounts=grant['scope'],
                        complete=grant['complete'], ciphertext=grant['catalog']['sha256'], size=grant['catalog']['size'])
        result = restore_set(catalog_file, retained, part_files, destination, archive=grant['archive'],
                             verification_key=bytes.fromhex(grant['verificationKey']), expected_catalog=expected)
        return CompletedImport(admission.reference, json.dumps(result).encode(), str(Path(destination).resolve()))


def receipt_for_import(admission, completion, target_signer, store, *, time, trust_policy):
    grant = decode_event(admission.grant)['value']
    if not isinstance(completion, CompletedImport) or completion.admission != admission.reference:
        raise ValueError('Locally completed transfer token required')
    completion = json.loads(completion.receipt)
    if any(completion.get(key) != grant[key] for key in ('archive', 'set')) or completion.get('ciphertext') != grant['catalog']['sha256']:
        raise ValueError('Receipt requires exact locally completed import')
    value = dict(version='0', purpose='history-transfer-receipt', transfer=grant['transfer'], grant=admission.reference,
                 source=grant['source'], target=grant['target'], catalog=grant['catalog']['sha256'],
                 result='imported' if grant['complete'] else 'imported-incomplete',
                 notBefore=grant['notBefore'], notAfter=grant['notAfter'])
    wrapper = sign_record('receipt', encode_event(value), target_signer)
    verify_record(wrapper, 'receipt', store, time=time, trust_policy=trust_policy)
    return wrapper


def retained_parent(wrapper, kind):
    """Check retained bytes for corruption; this does not establish a trust anchor."""
    raw, signature, value, reference = unpack(wrapper, kind)
    signer = value['target'] if kind == 'request' else value['source']
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(signer['key'])).verify(signature, frame(kind, raw))
    except (ValueError, InvalidSignature) as error:
        raise ValueError('Retained parent signature') from error
    return dict(raw=raw, value=value, reference=reference)


def check_receipt(request_wrapper, grant_wrapper, receipt_wrapper, store, *, time, trust_policy):
    """Parents are previously accepted source-outbox records, never message claims."""
    with authority_snapshot(store):
        request = retained_parent(request_wrapper, 'request')
        grant = retained_parent(grant_wrapper, 'grant')
        result = verify_record(receipt_wrapper, 'receipt', store, time=time, trust_policy=trust_policy)
        correlate(request, grant)
        value, g = result['value'], grant['value']
        if (value['grant'] != grant['reference'] or value['catalog'] != g['catalog']['sha256']
                or any(value[key] != g[key] for key in ('transfer', 'source', 'target'))
                or value['result'] != ('imported' if g['complete'] else 'imported-incomplete')
                or uint(value['notBefore']) < uint(g['notBefore']) or uint(value['notAfter']) > uint(g['notAfter'])):
            raise ValueError('Receipt does not match retained grant')
    return result['reference']


def check_cancel(retained_request, retained_grant, cancel_wrapper, store, *, time, trust_policy):
    """Parents must come from the caller's authenticated journal, not this message."""
    parent = retained_parent(retained_request, 'request')
    request, request_ref = parent['value'], parent['reference']
    with authority_snapshot(store):
        cancel = verify_record(cancel_wrapper, 'cancel', store, time=time, trust_policy=trust_policy)
        value = cancel['value']
        if (value['request'] != request_ref or any(value[key] != request[key] for key in ('transfer', 'source', 'target'))
                or uint(value['notBefore']) < uint(request['notBefore'])
                or uint(value['notAfter']) > uint(request['notAfter'])):
            raise ValueError('Cancellation does not match retained request')
        if value['grant'] != '':
            if retained_grant is None or value['grant'] != retained_parent(retained_grant, 'grant')['reference']:
                raise ValueError('Cancellation does not match retained grant')
    return cancel['reference']
