"""Provider delegation/registration validation and durable local acceptance.

FetchFacts are trusted transport-adapter output, never decoded response fields.
No DNS, TLS, OAuth server, token minting or peer-grant implementation is supplied.
The socket adapter must enforce the network boundary before producing these facts.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit

from provider_control import node
from service_authorization import oauth_json

SCOPES = ['email2.provider.link', 'email2.provider.manage']
CALLBACKS = ['http://127.0.0.1:1/email2/provider/callback', 'http://[::1]:1/email2/provider/callback']
FIELDS = set('version purpose domain publication generation service controlPrefix managementPrefix notBefore notAfter'.split())


def uint(value, *, positive=False):
    if type(value) is not str or not re.fullmatch(r'0|[1-9][0-9]{0,19}', value) or not int(positive) <= int(value) < 2**64:
        raise ValueError('Canonical uint64 required')
    return int(value)


def bounded(raw):
    if type(raw) is not bytes or len(raw) > 65536:
        raise ValueError('Discovery representation budget')
    value = oauth_json(raw)
    def walk(v, depth):
        if isinstance(v, (dict, list)):
            if depth > 16:
                raise ValueError('Discovery depth budget')
            children = list(v.keys()) + list(v.values()) if isinstance(v, dict) else v
            for child in children:
                walk(child, depth + 1 if isinstance(child, (dict, list)) else depth)
        elif isinstance(v, str):
            v.encode('utf-8')
    walk(value, 1)
    if not isinstance(value, dict):
        raise ValueError('Object required')
    return value


def urls(service, endpoints=(), prefixes=()):
    module = Path(__file__).with_name('service-question.mjs').as_uri()
    script = f"import{{isServiceOrigin,isServiceEndpoint}}from {json.dumps(module)};let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);process.stdout.write(JSON.stringify(isServiceOrigin(v.service)&&v.endpoints.every(x=>isServiceEndpoint(x,v.service))&&v.prefixes.every(x=>isServiceEndpoint(x,v.service,{{prefix:true}}))));"
    if not node(script, dict(service=service, endpoints=list(endpoints), prefixes=list(prefixes))):
        raise ValueError('Canonical same-origin locations required')


def domain_name(domain):
    if type(domain) is not str:
        raise ValueError('Selected account domain required')
    # Reuse the suite's DNS/validated-A-label grammar. A-label support is held
    # unless the configured coherent Unicode provider validates it upstream.
    urls('https://' + domain)
    if urlsplit('https://' + domain).netloc != domain or ':' in domain or '/' in domain:
        raise ValueError('Account domain spelling')


@dataclass(frozen=True)
class FetchFacts:
    url: str
    status: int = 200
    content_type: str = 'application/json'
    content_coding: str = 'identity'
    tls_authenticated: bool = True
    redirected: bool = False
    network_allowed: bool = True
    ambient_credentials: bool = False
    no_store: bool = True


def fetched(raw, facts, expected, *, status=200):
    if not isinstance(facts, FetchFacts) or facts.url != expected or facts.status != status or type(facts.status) is not int:
        raise ValueError('Exact fetch/response required')
    if facts.content_type != 'application/json' or facts.content_coding != 'identity' or facts.tls_authenticated is not True or facts.redirected is not False or facts.network_allowed is not True or facts.ambient_credentials is not False or facts.no_store is not True:
        raise ValueError('Trusted transport boundary required')
    return bounded(raw)


def current(value, time):
    if type(time) is not tuple or len(time) != 2 or any(type(x) is not int or not 0 <= x < 2**64 for x in time):
        raise ValueError('Credible full clock interval required')
    before, after = uint(value['notBefore']), uint(value['notAfter'])
    if not before <= time[0] <= time[1] <= after:
        raise ValueError('Delegation not current')


def descriptor(raw, domain, facts, *, time):
    domain_name(domain)
    value = fetched(raw, facts, 'https://' + domain + '/.well-known/email2-provider')
    if set(value) != FIELDS or value['version'] != '0' or value['purpose'] != 'provider-service-discovery' or value['domain'] != domain:
        raise ValueError('Exact delegation schema/domain')
    if type(value['publication']) is not str or not re.fullmatch(r'[0-9a-f]{32}', value['publication']) or value['publication'] == '0' * 32:
        raise ValueError('Publication identifier')
    uint(value['generation'], positive=True)
    current(value, time)
    urls(value['service'], prefixes=[value['controlPrefix'], value['managementPrefix']])
    a, b = value['controlPrefix'], value['managementPrefix']
    if a.startswith(b) or b.startswith(a):
        raise ValueError('Nonoverlapping protocol prefixes required')
    return value


def string_list(value):
    if type(value) is not list or any(type(x) is not str or not re.fullmatch(r'[\x20-\x7e]+', x) for x in value) or len(set(value)) != len(value):
        raise ValueError('Distinct nonempty ASCII list required')
    return value


def metadata(raw, delegation, facts, *, purpose='account-setup'):
    if purpose != 'account-setup':
        raise ValueError('Recipient bootstrap cannot acquire management authorization')
    service = delegation['service']
    value = fetched(raw, facts, service + '/.well-known/oauth-authorization-server')
    if value.get('issuer') != service or value.get('authorization_response_iss_parameter_supported') is not True:
        raise ValueError('Issuer binding required')
    endpoint_keys = ['authorization_endpoint', 'token_endpoint', 'registration_endpoint', 'revocation_endpoint']
    try:
        endpoints = [value[k] for k in endpoint_keys]
        urls(service, endpoints=endpoints)
        if len(set(endpoints)) != 4:
            raise ValueError('Distinct OAuth endpoints required')
        for key, required in [('response_types_supported', ['code']), ('grant_types_supported', ['authorization_code', 'refresh_token']), ('token_endpoint_auth_methods_supported', ['none']), ('code_challenge_methods_supported', ['S256']), ('scopes_supported', SCOPES)]:
            if not set(required) <= set(string_list(value[key])):
                raise ValueError('Required public native authorization capability')
    except (KeyError, TypeError) as error:
        raise ValueError('Required authorization metadata') from error
    return value


def registration_request():
    return dict(redirect_uris=CALLBACKS[:], grant_types=['authorization_code', 'refresh_token'],
                response_types=['code'], token_endpoint_auth_method='none', scope=' '.join(SCOPES))


def registration_response(raw, selected_metadata, facts):
    value = fetched(raw, facts, selected_metadata['registration_endpoint'], status=201)
    if {'client_secret', 'client_secret_expires_at', 'registration_access_token', 'registration_client_uri'} & set(value):
        raise ValueError('Unmanaged public client required')
    expected = registration_request()
    for key, required in expected.items():
        if key == 'scope':
            actual = value.get(key)
            if type(actual) is not str or actual.split(' ') not in [SCOPES, SCOPES[::-1]]:
                raise ValueError('Exact scope set required')
        elif value.get(key) != required:
            raise ValueError('Registered native metadata changed')
    if type(value.get('client_id')) is not str or not re.fullmatch(r'[\x21-\x7e]{1,256}', value['client_id']):
        raise ValueError('Opaque public client identifier required')
    issued = value.get('client_id_issued_at')
    if type(issued) is not int or not 0 <= issued <= 9007199254740991:
        raise ValueError('Client issuance time required')
    return value


class DelegationStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS pd_current(domain TEXT, purpose TEXT, decision INTEGER, raw BLOB, PRIMARY KEY(domain,purpose));
        CREATE TABLE IF NOT EXISTS pd_decisions(domain TEXT, purpose TEXT, decision INTEGER, raw BLOB, PRIMARY KEY(domain,purpose,decision));''')

    def close(self):
        self.db.close()

    def snapshot(self, domain, purpose='account-setup'):
        row = self.db.execute('SELECT decision,raw FROM pd_current WHERE domain=? AND purpose=?', (domain,purpose)).fetchone()
        return None if row is None else dict(decision=row[0], raw=row[1], digest=hashlib.sha256(row[1]).hexdigest())

    def accept(self, raw, domain, facts, *, time, expected_decision, setup_authorized=False, confirmed_service=None, reset=False, purpose='account-setup'):
        # Caller owns account-setup authorization, trusted fetch facts and clock.
        # CAS protects concurrent local decisions, not whole-machine rollback.
        if purpose not in ('account-setup', 'recipient-bootstrap'):
            raise ValueError('Explicit discovery purpose required')
        value = descriptor(raw, domain, facts, time=time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.snapshot(domain, purpose)
            actual = old['decision'] if old else None
            if actual != expected_decision or setup_authorized is not True:
                raise ValueError('Current local setup permission/decision required')
            if old:
                previous = bounded(old['raw'])
                if value['publication'] != previous['publication']:
                    if reset is not True or confirmed_service != value['service']:
                        raise ValueError('Explicit publication reset required')
                else:
                    if reset is not False:
                        raise ValueError('Reset requires a new publication')
                    generation, retained = uint(value['generation']), uint(previous['generation'])
                    if generation < retained:
                        raise ValueError('Delegation rollback')
                    if generation == retained:
                        if raw != old['raw']:
                            raise ValueError('Generation conflict')
                        self.db.execute('COMMIT')
                        return old
                    if purpose == 'account-setup' and value['service'] != previous['service'] and confirmed_service != value['service']:
                        raise ValueError('New service confirmation required')
            elif reset is not False or (purpose == 'account-setup' and confirmed_service != value['service']):
                raise ValueError('Initial service confirmation required')
            decision = (actual or 0) + 1
            if decision >= 2**63:
                raise ValueError('Local decision counter exhausted')
            self.db.execute('INSERT INTO pd_decisions VALUES(?,?,?,?)', (domain, purpose, decision, raw))
            self.db.execute('INSERT INTO pd_current VALUES(?,?,?,?) ON CONFLICT(domain,purpose) DO UPDATE SET decision=excluded.decision,raw=excluded.raw', (domain, purpose, decision, raw))
            self.db.execute('COMMIT')
            return self.snapshot(domain, purpose)
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise
