"""Actual service-context handshakes; generation and handshake failures stay distinct."""
import datetime,socket,ssl,tempfile,threading,unittest
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa,ec,ed25519,ed448,padding
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID
from service_tls import wrap_service_socket

class CertificateBackendTests(unittest.TestCase):
 def run_chain(self,kind='ec',*,bad=None,leaf_kind=None,mutation=None,pss=False,dn=None,inspect_chain=None,raw_backend=False):
  factory={'rsa':lambda:rsa.generate_private_key(public_exponent=65537,key_size=2048),'ec':lambda:ec.generate_private_key(ec.SECP256R1()),'ed':ed25519.Ed25519PrivateKey.generate,'ed448':ed448.Ed448PrivateKey.generate,'p384':lambda:ec.generate_private_key(ec.SECP384R1())}
  ca=factory[kind]();leaf=factory[leaf_kind or kind]();now=datetime.datetime.now(datetime.timezone.utc)
  name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Fixture CA')]);subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'service')])
  h=None if kind in ('ed','ed448') else hashes.SHA256()
  root=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(ca.public_key()).serial_number(1).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=1)).add_extension(x509.BasicConstraints(bad!='ca',0 if bad!='ca' else None),True).add_extension(x509.KeyUsage(False,False,False,False,False,bad!='keyusage',True,False,False),True).add_extension(x509.SubjectKeyIdentifier.from_public_key(ca.public_key()),False))
  if bad=='constraint':root=root.add_extension(x509.NameConstraints(None,[x509.DNSName('service.example')]),True)
  root=root.sign(ca,h)
  intermediate=None
  if bad=='pathlen':
   ik=factory[kind]();iname=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Intermediate')])
   intermediate=(x509.CertificateBuilder().subject_name(iname).issuer_name(name).public_key(ik.public_key()).serial_number(3).not_valid_before(now-datetime.timedelta(hours=1)).not_valid_after(now+datetime.timedelta(hours=1)).add_extension(x509.BasicConstraints(True,0),True).add_extension(x509.KeyUsage(False,False,False,False,False,True,True,False,False),True).add_extension(x509.SubjectKeyIdentifier.from_public_key(ik.public_key()),False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca.public_key()),False).sign(ca,h))
   ca=ik;name=iname
  if dn:name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,dn)])
  cert=(x509.CertificateBuilder().subject_name(subject).issuer_name(name).public_key(leaf.public_key()).serial_number(2).not_valid_before(now-datetime.timedelta(days=2)).not_valid_after(now-datetime.timedelta(days=1) if bad=='expired' else now+datetime.timedelta(hours=1)).add_extension(x509.BasicConstraints(False,None),True).add_extension(x509.SubjectAlternativeName([x509.DNSName('service.example')]),False).add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca.public_key()),False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH if bad=='eku' else ExtendedKeyUsageOID.SERVER_AUTH]),False))
  if bad=='critical':cert=cert.add_extension(x509.UnrecognizedExtension(x509.ObjectIdentifier('1.2.3.4.5'),b'\x05\x00'),True)
  cert=cert.sign(ca,h,**({'rsa_padding':padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32)} if pss else {}))
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'ca').write_bytes(root.public_bytes(serialization.Encoding.PEM));(p/'cert').write_bytes(cert.public_bytes(serialization.Encoding.PEM));
   if mutation:
    from certificate_der_fixture import mutate_signed,pem
    (p/'cert').write_bytes(pem(mutate_signed(cert.public_bytes(serialization.Encoding.DER),ca,kind,mutation)))
   if intermediate:
    with (p/'cert').open('ab') as out:out.write(intermediate.public_bytes(serialization.Encoding.PEM))
   (p/'key').write_bytes(leaf.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
   context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3;context.load_cert_chain(p/'cert',p/'key')
   with socket.socket() as listener:
    listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(3)
    errors=[]
    def serve():
     try:
      with listener.accept()[0] as sock:
       sock.settimeout(3)
       with context.wrap_socket(sock,server_side=True):pass
     except ssl.SSLError:pass
     except Exception as e:errors.append(e)
    t=threading.Thread(target=serve);t.start()
    try:
     with socket.create_connection(listener.getsockname(),timeout=3) as sock:
      from service_tls import service_context
      selected=service_context(trusted_ca_file=str(p/'ca')).wrap_socket(sock,server_hostname='service.example') if raw_backend else wrap_service_socket(sock,reference_host='service.example',trusted_ca_file=str(p/'ca'))
      with selected as secured:
       if inspect_chain:inspect_chain(secured,(p/'cert').read_bytes())
       return secured.version()
    finally:t.join(4);self.assertFalse(t.is_alive());self.assertEqual(errors,[])
 def test_rsa_and_p256_targets(self):
  for kind in ('rsa','ec'):
   with self.subTest(kind=kind):self.assertEqual(self.run_chain(kind),'TLSv1.3')
 def test_additional_ed25519_accepted(self):self.assertEqual(self.run_chain('ed'),'TLSv1.3')
 def test_validly_signed_requirement_violations(self):
  for bad in ('expired','eku','critical','constraint','ca','keyusage'):
   with self.subTest(bad=bad):
    with self.assertRaises(ssl.SSLCertVerificationError):self.run_chain(bad=bad)

 def test_mixed_and_additional_algorithms(self):
  for ca,leaf in [('rsa','ec'),('ec','rsa'),('p384','p384'),('ed448','ed448')]:
   with self.subTest(ca=ca,leaf=leaf):self.assertEqual(self.run_chain(ca,leaf_kind=leaf),'TLSv1.3')

 def test_directory_name_matching_and_path_length(self):
  self.assertEqual(self.run_chain(dn='  FIXTURE   ca  '),'TLSv1.3')
  with self.assertRaises(ssl.SSLCertVerificationError):self.run_chain(dn='Different CA')
  with self.assertRaises(ssl.SSLCertVerificationError):self.run_chain(bad='pathlen')
 def test_rsa_pss_certificate_signature(self):
  self.assertEqual(self.run_chain('rsa',pss=True),'TLSv1.3')

 def test_pss_declared_salt_mismatch_rejected(self):
  with self.assertRaises(ssl.SSLCertVerificationError):self.run_chain('rsa',pss=True,mutation='pss-salt-mismatch')

 def test_resigned_forbidden_signature_parameters_rejected(self):
  for kind in ('ec','ed'):
   with self.subTest(kind=kind):
    with self.assertRaisesRegex(ValueError,'parameters must be absent'):self.run_chain(kind,mutation='signature-null')
 def test_missing_chain_api_and_malformed_shape(self):
  from certificate_algorithms import check_verified_chain
  with self.assertRaisesRegex(RuntimeError,'unavailable'):check_verified_chain(object())
  class Fake:
   def __init__(self,value):self.value=value
   def get_verified_chain(self):return self.value
  for value in (None,[],[None],[b''],[b'\x30\x80'],[b'\x30\x00junk']):
   with self.subTest(value=value):
    with self.assertRaises(ValueError):check_verified_chain(Fake(value))
  for limit in (True,0,-1,float('nan'),1.5):
   with self.assertRaises(ValueError):check_verified_chain(Fake([]),max_certificate_bytes=limit)

 def test_backend_violation_fixture_preserves_original_der(self):
  for kind in ('ec','ed'):
   def inspect(sock,pem):
    original=ssl.PEM_cert_to_DER_cert(pem.decode())
    self.assertEqual(sock.get_verified_chain()[0],original)
    self.assertEqual(sock.get_unverified_chain()[0],original)
   with self.subTest(kind=kind):self.assertEqual(self.run_chain(kind,mutation='signature-null',raw_backend=True,inspect_chain=inspect),'TLSv1.3')
