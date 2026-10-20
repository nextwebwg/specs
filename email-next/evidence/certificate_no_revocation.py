"""RFC 9608 extension check only, using cryptography 50.0.2's X.509 API.

Does not authenticate a certificate, build a path, check validity/purpose/name,
retrieve status, or change a TLS context. No lifetime threshold is imposed.
"""
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtensionOID, ObjectIdentifier

NO_REV_AVAIL=ObjectIdentifier('2.5.29.56')


def check_no_rev_avail(certificate_der):
    """Return absent, valid-extension-exception, or invalid with a specific reason.

    Valid means this extension's syntax/combinations only. Critical noRevAvail
    records nonconforming issuance (RFC9608 section 2), not an invented relying-
    party rejection rule. Section 3 mandates rejection of forbidden combinations.
    """
    criticality_conforming=None
    def result(status,reason):
        return {'status':status,'reason':reason,'certificateValidated':False,'revocationChecked':False,'criticalityConforming':criticality_conforming}
    if not isinstance(certificate_der,bytes):return result('invalid','expected-der-bytes')
    try:
        certificate=x509.load_der_x509_certificate(certificate_der)
        if certificate.public_bytes(serialization.Encoding.DER)!=certificate_der:
            return result('invalid','nonexact-certificate-der')
        extensions=certificate.extensions
        try:extension=extensions.get_extension_for_oid(NO_REV_AVAIL)
        except x509.ExtensionNotFound:return result('absent','no-explicit-exception')
        # In the pinned API this OID remains unrecognized; its value preserves
        # extension OCTET STRING contents, not the outer OCTET STRING encoding.
        if not isinstance(extension.value,x509.UnrecognizedExtension):
            return result('invalid','unsupported-extension-representation')
        if extension.value.value!=b'\x05\x00':return result('invalid','no-rev-avail-not-der-null')
        criticality_conforming=not extension.critical
        for ext in extensions:
            if ext.oid==ExtensionOID.BASIC_CONSTRAINTS and ext.value.ca:
                return result('invalid','ca-certificate')
            if ext.oid==ExtensionOID.CRL_DISTRIBUTION_POINTS:
                return result('invalid','crl-distribution-points')
            if ext.oid==ExtensionOID.FRESHEST_CRL:
                return result('invalid','freshest-crl')
            if ext.oid==ExtensionOID.AUTHORITY_INFORMATION_ACCESS and any(
                    entry.access_method==AuthorityInformationAccessOID.OCSP for entry in ext.value):
                return result('invalid','ocsp-access-method')
        return result('valid-extension-exception','explicit-no-revocation-information')
    except (ValueError,TypeError,x509.DuplicateExtension,x509.UnsupportedGeneralNameType):
        return result('invalid','malformed-certificate-or-extensions')
