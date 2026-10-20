"""Real TLS SNI/ALPN observations, separate from HTTP and PKIX conformance."""
import socket
import ssl
import threading
import unittest
from service_tls import service_context,wrap_http11_socket,require_http11_protocol
import test_service_tls as tls_fixture

class ProtocolTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):tls_fixture.ServiceTLSTest.setUpClass();cls.fixture=tls_fixture.ServiceTLSTest()
 @classmethod
 def tearDownClass(cls):tls_fixture.ServiceTLSTest.tearDownClass()
 def exchange(self,server_protocols,*,client_protocols=None,san='api.service.example'):
  cert,key=self.fixture.leaf(san);context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3;context.load_cert_chain(cert,key)
  if server_protocols is not None:context.set_alpn_protocols(server_protocols)
  ready=threading.Event();names=[];seen=[];errors=[];context.sni_callback=lambda sock,name,ctx:names.append(name)
  listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen();listener.settimeout(3)
  def serve():
   try:
    with listener.accept()[0] as raw:
     raw.settimeout(3)
     with context.wrap_socket(raw,server_side=True) as secured:
      seen.append(secured.selected_alpn_protocol());ready.set()
      try:seen.append(secured.recv(1))
      except ConnectionResetError:seen.append(b'')
   except ssl.SSLError:pass
   except Exception as exc:errors.append(exc)
  thread=threading.Thread(target=serve);thread.start()
  try:
   with socket.create_connection(listener.getsockname(),timeout=3) as raw:
    if client_protocols is None:secured=wrap_http11_socket(raw,reference_host='api.service.example',trusted_ca_file=str(self.fixture.ca_file))
    else:
     client=service_context(trusted_ca_file=str(self.fixture.ca_file));client.set_alpn_protocols(client_protocols);secured=client.wrap_socket(raw,server_hostname='api.service.example')
    with secured:
     self.assertTrue(ready.wait(3),'server handshake did not finish')
     selected=require_http11_protocol(secured)
     secured.sendall(b'X')
     return selected,names,seen
  finally:
   thread.join(4);listener.close();self.last_seen=seen;self.assertFalse(thread.is_alive());self.assertEqual(errors,[]);self.assertEqual(names,['api.service.example'])
 def test_negotiated_http11_and_actual_sni(self):
  selected,names,seen=self.exchange(['http/1.1']);self.assertEqual(selected,'http/1.1');self.assertEqual(seen,['http/1.1',b'X'])
 def test_absent_alpn_explicit_fallback(self):
  selected,names,seen=self.exchange(None);self.assertIsNone(selected);self.assertEqual(seen,[None,b'X'])
 def test_different_selected_protocol_no_application_bytes(self):
  with self.assertRaisesRegex(ValueError,'negotiated protocol'):self.exchange(['h2'],client_protocols=['h2','http/1.1'])
  self.assertEqual(self.last_seen,['h2',b''])
 def test_sni_does_not_replace_identity_check(self):
  with self.assertRaises(ssl.SSLCertVerificationError):self.exchange(['http/1.1'],san='wrong.example')

if __name__=='__main__':unittest.main()
