"""Generated signed certificates test extension rules, not certificate trust."""
import datetime
import unittest
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import AuthorityInformationAccessOID,NameOID
from certificate_no_revocation import check_no_rev_avail,NO_REV_AVAIL

class NoRevocationExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.key=ec.generate_private_key(ec.SECP256R1())
    def certificate(self,value=b'\x05\x00',*,critical=False,extras=(),days=1):
        now=datetime.datetime.now(datetime.timezone.utc)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'extension-test.invalid')])
        builder=(x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(self.key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=days)))
        if value is not None:builder=builder.add_extension(x509.UnrecognizedExtension(NO_REV_AVAIL,value),critical)
        for ext in extras:builder=builder.add_extension(ext,False)
        return builder.sign(self.key,hashes.SHA256()).public_bytes(serialization.Encoding.DER)
    def test_explicit_exception_and_absence_are_distinct(self):
        result=check_no_rev_avail(self.certificate(extras=[x509.BasicConstraints(False,None)]))
        self.assertEqual(result['status'],'valid-extension-exception')
        self.assertTrue(result['criticalityConforming'])
        self.assertFalse(result['certificateValidated']);self.assertFalse(result['revocationChecked'])
        self.assertEqual(check_no_rev_avail(self.certificate(None))['status'],'absent')
    def test_null_must_be_exact_der(self):
        for raw in (b'',b'\x04\x00',b'\x05\x01\x00',b'\x05\x80\x00\x00',b'\x05\x00\x00'):
            self.assertEqual(check_no_rev_avail(self.certificate(raw))['reason'],'no-rev-avail-not-der-null')
    def test_critical_records_issuance_nonconformance_without_hiding_ca_violation(self):
        self.assertEqual(check_no_rev_avail(self.certificate(extras=[x509.BasicConstraints(True,None)]))['reason'],'ca-certificate')
        critical=check_no_rev_avail(self.certificate(critical=True))
        self.assertEqual(critical['status'],'valid-extension-exception')
        self.assertFalse(critical['criticalityConforming'])
        forbidden=check_no_rev_avail(self.certificate(critical=True,extras=[x509.BasicConstraints(True,None)]))
        self.assertEqual(forbidden['status'],'invalid');self.assertEqual(forbidden['reason'],'ca-certificate')
        self.assertFalse(forbidden['criticalityConforming'])
    def test_distribution_point_extensions_are_forbidden(self):
        point=x509.DistributionPoint([x509.UniformResourceIdentifier('https://example.invalid/status')],None,None,None)
        for extension,reason in [(x509.CRLDistributionPoints([point]),'crl-distribution-points'),(x509.FreshestCRL([point]),'freshest-crl')]:
            self.assertEqual(check_no_rev_avail(self.certificate(extras=[extension]))['reason'],reason)
            self.assertEqual(check_no_rev_avail(self.certificate(None,extras=[extension]))['status'],'absent')
    def test_aia_issuer_allowed_but_ocsp_anywhere_forbidden(self):
        issuer=x509.AccessDescription(AuthorityInformationAccessOID.CA_ISSUERS,x509.UniformResourceIdentifier('https://example.invalid/issuer'))
        ocsp=x509.AccessDescription(AuthorityInformationAccessOID.OCSP,x509.UniformResourceIdentifier('https://example.invalid/ocsp'))
        self.assertEqual(check_no_rev_avail(self.certificate(extras=[x509.AuthorityInformationAccess([issuer])]))['status'],'valid-extension-exception')
        for descriptions in ([ocsp],[issuer,ocsp],[ocsp,issuer]):
            self.assertEqual(check_no_rev_avail(self.certificate(extras=[x509.AuthorityInformationAccess(descriptions)]))['reason'],'ocsp-access-method')
    def test_no_invented_lifetime_limit(self):
        for days in (1,3650):self.assertEqual(check_no_rev_avail(self.certificate(days=days))['status'],'valid-extension-exception')
    def test_invalid_certificate_and_trailing_bytes(self):
        for data in (None,'text',b'not DER',self.certificate()+b'extra'):
            self.assertEqual(check_no_rev_avail(data)['status'],'invalid')
    def test_malformed_other_extension_is_not_an_exception(self):
        bad=x509.UnrecognizedExtension(x509.ExtensionOID.BASIC_CONSTRAINTS,b'\x05\x00')
        self.assertEqual(check_no_rev_avail(self.certificate(extras=[bad]))['status'],'invalid')
if __name__=='__main__':unittest.main()
