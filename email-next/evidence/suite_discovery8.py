"""Current-suite discovery proof/package checks and local issuance staging.

No complete receiving implementation or provider/mail publication is supplied.
Only current-time new-setup discovery is verified here; expired proof validation
for late Welcome processing remains a different boundary.
"""
import hashlib
import json
import math
from pathlib import Path
import time as elapsed_time

from admission_windows import issue, validate as validate_window, clock
from event_encoding import encode_event
from initial_roster import credential
from passive_discovery import decode_passive_discovery, uint64
from passive_discovery_package import inspect_package
from passive_discovery_verify import verify_passive_discovery, verify_passive_discovery_locked
from provider_mls import call
from sealed_control import native as control_native,key_descriptor


def _metadata(binary, decoded, time, maximum_lifetime):
    assertion = decoded['assertion']
    value = assertion['value']
    binding = next(b['value'] for b in decoded['identity']['bindings'] if b['digest'] == value['binding'])
    return inspect_package(assertion['key_package_octets'], principal=value['principal'], device=value['device'], accepted_signing_key=bytes.fromhex(binding['signingKey']), earliest=time['earliest'], latest=time['latest'], executable=Path(binary).with_name('inspect-discovery-package'), maximum_lifetime=maximum_lifetime)


def verify(octets, identity, binary, *, time, trust_policy, maximum_lifetime=None, maximum_control_lifetime='604800'):
    return verify_version(octets, identity, binary, time=time, trust_policy=trust_policy,
                          version='8', maximum_lifetime=maximum_lifetime,
                          maximum_control_lifetime=maximum_control_lifetime)


def verify_version(octets, identity, binary, *, time, trust_policy, version,
                   maximum_lifetime=None, maximum_control_lifetime='604800'):
    # Explicit profile dispatch; original signed bytes never change version.
    if version not in ('8', '9'):
        raise ValueError('Explicit supported assertion version required')
    decoded = decode_passive_discovery(octets)
    value = decoded['assertion']['value']
    if value['version'] != version:
        raise ValueError('Exact selected assertion version required')
    checked = verify_passive_discovery(octets, identity, time=time, trust_policy=trust_policy)
    if checked.get('status') != 'snapshot-authorized-unverified':
        return checked
    if value['controlKey'] is not None:
        key=value['controlKey']
        try:key_descriptor(key,maximum_lifetime=maximum_control_lifetime)
        except ValueError:return dict(status='setup-held',reason='control-key-lifetime-policy')
        try:control_native(Path(binary).with_name('sealed-control'),op='seal',id=key['id'],publicKey=key['publicKey'],plaintext='')
        except ValueError:return dict(status='setup-held',reason='control-key-validation')
    if decoded['assertion']['key_package_octets'] is None:
        return dict(checked, status='suite-capabilities-validated-unverified', package=None)
    package = _metadata(binary, decoded, time, maximum_lifetime)
    if package.get('status') != 'package-valid':
        return dict(status='setup-held', reason='package-validation', packageResult=package)
    if uint64(value['keyPackageReceiveUntil']) < uint64(package['notAfter']):
        return dict(status='setup-held', reason='receiving-deadline-before-package-expiry')
    if not uint64(package['notBefore']) <= uint64(value['notBefore']) <= uint64(value['notAfter']) <= uint64(package['notAfter']):
        return dict(status='setup-held', reason='assertion-exceeds-package-window')
    return dict(checked, status='suite-setup-validated-unverified', mls_validated=True, package=dict(package, receiveUntil=value['keyPackageReceiveUntil']))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def _later(time, start):
    elapsed = elapsed_time.monotonic() - start
    if elapsed < 0:
        raise ValueError('Monotonic clock rollback')
    lo = uint64(time['earliest']) + math.floor(elapsed)
    hi = uint64(time['latest']) + math.ceil(elapsed)
    if hi > 2**64 - 1:
        raise ValueError('Elapsed-time overflow')
    return dict(earliest=str(lo), latest=str(hi))


class LocalIssuance:
    """Retain validated public promises before any separate publication step.

    Device/checkpoint arguments are trusted local crypto-engine inputs, never
    decoded mail. The journal contains no private checkpoint or initialization
    key. Staging is not an actual publication, custody/erasure proof or permission
    to advertise a complete client; a real publisher needs final release checks.
    """
    def __init__(self, identity, binary):
        self.identity = identity
        self.db = identity.db
        self.binary = Path(binary)
        if self.db.in_transaction:
            raise ValueError('Initialize outside transaction')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS email2_issued_packages(reference TEXT PRIMARY KEY,owner TEXT NOT NULL,package BLOB NOT NULL,window BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS email2_issued_assertions(owner TEXT NOT NULL,id TEXT NOT NULL,payload BLOB NOT NULL,signature TEXT NOT NULL,wrapper BLOB NOT NULL,reference TEXT,PRIMARY KEY(owner,id));
        CREATE TABLE IF NOT EXISTS email2_issued_control_keys(id TEXT PRIMARY KEY,owner TEXT NOT NULL,public_key TEXT UNIQUE NOT NULL,promise BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS email2_issued_package_terminal(reference TEXT PRIMARY KEY,reason TEXT NOT NULL,at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS email2_package_allocation_realm(reference TEXT PRIMARY KEY,realm TEXT NOT NULL);''')

    def stage(self, octets, device, *, time, trust_policy, receive_delay=604800, maximum_lifetime='604800', maximum_control_lifetime='604800', crash=None):
        decoded = decode_passive_discovery(octets)
        value = decoded['assertion']['value']
        if value['version'] != '8' or any(value[k] != device[k] for k in ('principal', 'device')):
            raise ValueError('Exact own-device assertion8 required')
        if self.db.in_transaction:
            raise ValueError('Local issuance requires transaction ownership')
        selected_time = dict(time)
        start = elapsed_time.monotonic()
        owner = credential(device)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            checked = verify_passive_discovery_locked(octets, self.identity, time=selected_time, trust_policy=trust_policy)
            if checked.get('status') != 'snapshot-authorized-unverified':
                raise ValueError('Current local assertion authority required')
            binding = next(b['value'] for b in decoded['identity']['bindings'] if b['digest'] == value['binding'])
            if binding['signingKey'] != device['key']:
                raise ValueError('Actual own signing key required')
            reproduced = call(self.binary, op='sign', checkpoint=device['checkpoint'], key=device['key'], domain='email-next/passive-discovery/v8', payload=decoded['assertion']['octets'].hex())
            if reproduced['signature'] != decoded['signature'].hex():
                raise ValueError('Local signing-key possession required')
            control=value['controlKey']
            if control is not None:
                secret=device.get('controlSecret',{})
                if any(secret.get(k)!=control[k] for k in ('id','publicKey')):raise ValueError('Actual own control-key material required')
                binary=self.binary.with_name('sealed-control')
                probe=control_native(binary,op='seal',id=control['id'],publicKey=control['publicKey'],plaintext='656d61696c3220636f6e74726f6c20637573746f6479')['ciphertext']
                opened=control_native(binary,op='open',id=control['id'],publicKey=control['publicKey'],privateKey=secret.get('privateKey'),ciphertext=probe)
                if opened['plaintext']!='656d61696c3220636f6e74726f6c20637573746f6479':raise ValueError('Control-key possession')
                prior=self.db.execute('SELECT owner,public_key,promise FROM email2_issued_control_keys WHERE id=?',(control['id'],)).fetchone()
                public=(owner,control['publicKey'],_canonical(control))
                if prior and prior!=public:raise ValueError('Immutable control-key promise')
                if not prior:key_descriptor(control,maximum_lifetime=maximum_control_lifetime)
                self.db.execute('INSERT OR IGNORE INTO email2_issued_control_keys VALUES(?,?,?,?)',(control['id'],*public))
            package = decoded['assertion']['key_package_octets']
            window = None
            reference = None
            if package is not None:
                own = call(self.binary, op='inspect-owned-publication', checkpoint=device['checkpoint'], key=device['key'], identity=device['identity'], package=package.hex(), earliest=selected_time['earliest'], latest=selected_time['latest'], maximumLifetime=maximum_lifetime)
                reference = own['reference']
                if self.db.execute('SELECT 1 FROM email2_issued_package_terminal WHERE reference=?', (reference,)).fetchone():
                    raise ValueError('Package terminal; stale private snapshots cannot reissue it')
                if not uint64(own['notBefore']) <= uint64(value['notBefore']) <= uint64(value['notAfter']) <= uint64(own['notAfter']):
                    raise ValueError('Assertion must fit actual package interval')
                old = self.db.execute('SELECT owner,package,window FROM email2_issued_packages WHERE reference=?', (reference,)).fetchone()
                if old:
                    if old[:2] != (owner, package):
                        raise ValueError('Owned package reference conflict')
                    window = json.loads(old[2])
                    validate_window(window)
                else:
                    window = issue(reference, own['notBefore'], own['notAfter'], receive_delay=receive_delay)
                if value['keyPackageReceiveUntil'] != window['receiveUntil']:
                    raise ValueError('Signed deadline must match immutable local custody')
                self.db.execute('INSERT OR IGNORE INTO email2_issued_packages VALUES(?,?,?,?)', (reference, owner, package, _canonical(window)))
            current = _later(selected_time, start)
            rechecked = verify_passive_discovery_locked(octets, self.identity, time=current, trust_policy=trust_policy)
            if rechecked.get('status') != 'snapshot-authorized-unverified':
                raise ValueError('Issuance authority or validity changed before commit')
            if window is not None and uint64(current['latest']) > uint64(window['sendUntil']):
                raise ValueError('Package expired before issuance commit')
            payload = decoded['assertion']['octets']
            signature = decoded['signature'].hex()
            old = self.db.execute('SELECT payload,signature FROM email2_issued_assertions WHERE owner=? AND id=?', (owner, value['record'])).fetchone()
            if old and old != (payload, signature):
                raise ValueError('Immutable assertion identifier conflict')
            self.db.execute('INSERT OR IGNORE INTO email2_issued_assertions VALUES(?,?,?,?,?,?)', (owner, value['record'], payload, signature, octets, reference))
            if crash:
                crash('before-commit')
            self.db.execute('COMMIT')
            if crash:
                crash('after-commit')
            return dict(status='staged-only', assertion=hashlib.sha256(payload).hexdigest(), reference=reference, window=window)
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise


    def bind_allocation_realm_locked(self, reference, realm):
        """Freeze one trusted local allocation namespace before publication.

        Realm is an opaque account-adapter identity for one provider/account/
        device allocation authority, not received mail or a provider assertion
        of exclusivity. It grants no account permission, does not publish and
        cannot prove a package was never copied through passive mail.
        """
        if not self.db.in_transaction:raise ValueError('Caller publication transaction required')
        if not isinstance(realm,str) or not realm:raise ValueError('Trusted allocation realm required')
        if not self.db.execute('SELECT 1 FROM email2_issued_packages WHERE reference=?',(reference,)).fetchone():raise ValueError('Staged owned package required')
        if self.db.execute('SELECT 1 FROM email2_issued_package_terminal WHERE reference=?',(reference,)).fetchone():raise ValueError('Terminal package cannot be published')
        prior=self.db.execute('SELECT realm FROM email2_package_allocation_realm WHERE reference=?',(reference,)).fetchone()
        if prior and prior[0]!=realm:raise ValueError('Package allocation authority is immutable')
        self.db.execute('INSERT OR IGNORE INTO email2_package_allocation_realm VALUES(?,?)',(reference,realm))
        return dict(status='allocation-realm-bound-only',reference=reference,realm=realm)

    def terminal_locked(self, reference, reason, *, time):
        """Trusted post-validation lifecycle seam; not a received control record.

        The caller commits actual consumption/withdrawal and retirement intent
        with this marker. It proves no key destruction or live group revocation.
        """
        if not self.db.in_transaction or reason not in ('consumed', 'withdrawn', 'retired'):
            raise ValueError('Owned lifecycle transaction required')
        row = self.db.execute('SELECT window FROM email2_issued_packages WHERE reference=?', (reference,)).fetchone()
        if row is None:
            raise ValueError('Known issued reference required')
        lo, hi = clock(time)
        window = json.loads(row[0])
        validate_window(window)
        if reason == 'retired' and lo <= uint64(window['receiveUntil']):
            raise ValueError('Receiving window not certainly finished; early retirement is withdrawal')
        old = self.db.execute('SELECT reason FROM email2_issued_package_terminal WHERE reference=?', (reference,)).fetchone()
        if old and old[0] != reason:
            raise ValueError('Retained terminal outcome conflict')
        self.db.execute('INSERT OR IGNORE INTO email2_issued_package_terminal VALUES(?,?,?)', (reference, reason, str(hi)))
        return reason
