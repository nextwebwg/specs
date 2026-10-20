"""Direct configured HTTP/1.1 adapter, no redirects/proxies/ambient credentials.

Loopback routing is an explicit fixture capability, not message-selected DNS.
TLS helper limitations (including revocation and IDNA) still apply.
"""
import http.client
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http_framing import FixedHTTPHandler,read_fixed_response
from urllib.parse import urlsplit
from service_tls import wrap_http11_socket, require_http11_protocol

LIMIT = 1048576

class ServiceHTTPSClient:
    def __init__(self, journal, *, host, port, ca_file, submit_path, status_prefix, address, not_before, retry_until, credible_time):
        if type(not_before) is not int or type(retry_until) is not int or not 0 <= not_before <= retry_until < 2**64:
            raise ValueError('invalid configured time bounds')
        self.journal = journal
        self.host, self.port, self.ca = host, port, ca_file
        self.submit_path, self.status_prefix, self.address = submit_path, status_prefix, address
        self.not_before, self.retry_until, self.credible_time = not_before, retry_until, credible_time
        self.lock = threading.Lock()  # Single-process client, deliberately serial.

    def request(self, identity, token, *, status=False):
        with self.lock:
            raw, service = self.journal.db.execute('SELECT raw,service FROM requests WHERE id=?', (identity,)).fetchone()
            expected = 'https://' + self.host + (':' + str(self.port) if self.port != 443 else '')
            if service != expected: raise ValueError('configured service mismatch')
            if not token or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~+/=' for c in token):
                raise ValueError('invalid bearer grammar')
            if not status:
                low, high = self.credible_time()
                if type(low) is not int or type(high) is not int or not self.not_before <= low <= high <= self.retry_until:
                    return {'http': None, 'state': self.journal.state(identity), 'attempt': 'time-held'}
            path = self.status_prefix + identity if status else self.submit_path
            conn = http.client.HTTPConnection(self.host, self.port, timeout=5)
            sock = socket.create_connection(self.address, timeout=5)
            try:
                conn.sock = wrap_http11_socket(sock, reference_host=self.host, trusted_ca_file=self.ca)
                conn.request('GET' if status else 'POST', path, body=None if status else raw,
                             headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'application/json', 'Cache-Control': 'no-store', 'Connection':'close'})
                response = conn.getresponse()
                receipt = read_fixed_response(response,LIMIT)
                if response.status not in (200, 202): return {'http': response.status, 'state': self.journal.state(identity), 'attempt': 'unconfirmed'}
                if response.getheader('Content-Type') != 'application/json' or response.getheader('Cache-Control') != 'no-store':
                    raise ValueError('response metadata')
                from service_answer import bind_result
                value = bind_result(receipt, raw, expected_service=service)['value']
                if (response.status == 202) != (value['outcome'] == 'pending'): raise ValueError('status outcome mismatch')
                return {'http': response.status, 'state': self.journal._observe_direct_response(identity, receipt)}
            finally:
                conn.close()
                sock.close()

def make_server(store, tls_context, *, drop_after_commit=False, response_transform=None):
    """Fault hooks belong solely to the local server fixture, never request data."""
    tls_context.set_alpn_protocols(['http/1.1'])
    class Handler(FixedHTTPHandler):
        def handle(self):
            try: require_http11_protocol(self.connection)
            except ValueError: return
            super().handle()
        def expected_authority(self):return urlsplit(store.action()['service']).netloc
        protocol_version = 'HTTP/1.1'
        def log_message(self, *args): pass
        def handle_request(self):
            self.connection.settimeout(5)
            action = store.action()
            auth = self.headers.get_all('Authorization', [])
            token = auth[0][7:] if len(auth) == 1 and auth[0].startswith('Bearer ') else ''
            if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Encoding'):
                code, body = 400, b''
            elif self.command == 'POST' and self.path == action['submitPath']:
                sizes = self.headers.get_all('Content-Length', [])
                if len(sizes) != 1 or not sizes[0].isdigit() or int(sizes[0]) > LIMIT or self.headers.get('Content-Type') != 'application/json':
                    code, body = 400, b''
                else:
                    raw = self.rfile.read(int(sizes[0]))
                    code, body = store.submit(raw, token) if len(raw) == int(sizes[0]) else (400, b'')
                    if drop_after_commit and code == 200:
                        self.close_connection = True
                        return
            elif self.command == 'GET' and self.path.startswith(action['statusPrefix']):
                import re
                identity = self.path[len(action['statusPrefix']):]
                if re.fullmatch('[0-9a-f]{32}', identity) and not self.headers.get('Content-Length'):
                    code, body = store.status(identity, token)
                else: code, body = 400, b''
            else: code, body = 404, b''
            if response_transform: code, body = response_transform(code, body)
            self.send_response(code)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Type', 'application/json')
            _, auth_status = store.authorized(token, action, 'submit' if self.command == 'POST' else 'status')
            if code in (401, 403) and auth_status != 200:
                challenge = 'Bearer realm="fixture"'
                if token: challenge += ', error="' + ('invalid_token' if auth_status == 401 else 'insufficient_scope') + '"'
                self.send_header('WWW-Authenticate', challenge)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
        do_POST = handle_request
        do_GET = handle_request
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.socket = tls_context.wrap_socket(server.socket, server_side=True)
    return server
