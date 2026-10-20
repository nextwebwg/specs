"""Real local TLS handshakes. Requires installed cryptography; no skip fallback."""
import datetime
import socket
import ssl
import tempfile
import threading
import unittest
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from service_tls import service_context, validate_reference_host, wrap_service_socket


class ServiceTLSTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.now = datetime.datetime.now(datetime.timezone.utc)
        cls.ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Loopback test CA')])
        cls.ca = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                  .public_key(cls.ca_key.public_key()).serial_number(x509.random_serial_number())
                  .not_valid_before(cls.now-datetime.timedelta(days=1))
                  .not_valid_after(cls.now+datetime.timedelta(days=1))
                  .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
                  .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
                  .add_extension(x509.SubjectKeyIdentifier.from_public_key(cls.ca_key.public_key()), critical=False)
                  .sign(cls.ca_key, hashes.SHA256()))
        cls.ca_file = cls.root/'ca.pem'
        cls.ca_file.write_bytes(cls.ca.public_bytes(serialization.Encoding.PEM))
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def leaf(self, san, cn='unrelated.example', untrusted=False):
        type(self).counter += 1
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        issuer_key = key if untrusted else self.ca_key
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        builder = (x509.CertificateBuilder().subject_name(name)
                   .issuer_name(name if untrusted else self.ca.subject)
                   .public_key(key.public_key()).serial_number(x509.random_serial_number())
                   .not_valid_before(self.now-datetime.timedelta(hours=1))
                   .not_valid_after(self.now+datetime.timedelta(hours=1))
                   .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                   .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()), critical=False))
        if san is not None:
            builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(san)]), critical=False)
        cert = builder.sign(issuer_key, hashes.SHA256())
        certfile, keyfile = self.root/f'{self.counter}.pem', self.root/f'{self.counter}.key'
        certfile.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        keyfile.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        return certfile, keyfile

    def handshake(self, san, *, host='api.service.example', cn='unrelated.example', untrusted=False, old=False):
        cert, key = self.leaf(san, cn, untrusted)
        server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server.load_cert_chain(cert, key)
        server.minimum_version = ssl.TLSVersion.TLSv1_2 if old else ssl.TLSVersion.TLSv1_3
        if old:
            server.maximum_version = ssl.TLSVersion.TLSv1_2
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(3)
        errors = []
        def serve():
            try:
                with listener.accept()[0] as connection:
                    connection.settimeout(3)
                    with server.wrap_socket(connection, server_side=True):
                        pass
            except ssl.SSLError:
                pass  # Expected peer rejection in negative fixtures.
            except Exception as exc:
                errors.append(exc)
        thread = threading.Thread(target=serve)
        thread.start()
        try:
            with socket.create_connection(listener.getsockname(), timeout=3) as sock:
                with wrap_service_socket(sock, reference_host=host, trusted_ca_file=str(self.ca_file)) as secured:
                    return secured.version()
        finally:
            thread.join(timeout=4)
            listener.close()
            self.assertFalse(thread.is_alive(), 'loopback server did not finish')
            self.assertEqual(errors, [])

    def test_valid_san(self):
        self.assertEqual(self.handshake('api.service.example'), 'TLSv1.3')

    def test_mismatch(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.handshake('other.service.example')

    def test_cn_only_rejected(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.handshake(None, cn='api.service.example')

    def test_untrusted_rejected(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.handshake('api.service.example', untrusted=True)

    def test_old_tls_rejected(self):
        with self.assertRaises(ssl.SSLError):
            self.handshake('api.service.example', old=True)

    def test_wildcard(self):
        self.assertEqual(self.handshake('*.service.example'), 'TLSv1.3')
        for host in ['service.example', 'nested.api.service.example']:
            with self.subTest(host=host), self.assertRaises(ssl.SSLCertVerificationError):
                self.handshake('*.service.example', host=host)

    def test_partial_wildcard_rejected(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.handshake('a*.service.example')

    def test_context_and_reference_boundary(self):
        context = service_context(trusted_ca_file=str(self.ca_file))
        self.assertEqual(context.minimum_version, ssl.TLSVersion.TLSv1_3)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        self.assertFalse(context.hostname_checks_common_name)
        for host in ['127.0.0.1', 'xn--bcher-kva.example', 'API.example', 'api.example.', '*.example', 'api..example', 'bücher.example']:
            with self.subTest(host=host), self.assertRaises(ValueError):
                validate_reference_host(host)


if __name__ == '__main__':
    unittest.main()
