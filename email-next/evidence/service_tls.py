"""Bounded HTTPS TLS experiment, not complete PKIX/IDNA or HTTP conformance.

Caller supplies independently authorized DNS host and trusted CA file. No incoming
message may choose the trust file. A successful handshake is not action authority.
"""
import ipaddress
import re
import ssl
from certificate_algorithms import check_verified_chain


def service_context(*, trusted_ca_file=None):
    """Create a verifying context; explicit CA file replaces default root loading."""
    context = ssl.create_default_context(cafile=trusted_ca_file)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    if not hasattr(context, 'hostname_checks_common_name'):
        raise RuntimeError('runtime lacks explicit SAN-only hostname verification')
    context.hostname_checks_common_name = False
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


def validate_reference_host(host):
    """Restricted ASCII DNS reference; A-labels require configured IDNA17 validation."""
    if not isinstance(host, str) or not host.isascii() or len(host) > 253:
        raise ValueError('invalid reference host')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP reference unsupported')
    labels = host.split('.')
    if len(labels) < 2 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in labels):
        raise ValueError('invalid reference host')
    if any(label.startswith('xn--') for label in labels):
        from idna17_acceptance import validate_domain
        if not validate_domain(host):raise ValueError('A-label validation unsupported')
    return host


def wrap_service_socket(sock, *, reference_host, trusted_ca_file=None, max_chain_certificates=32, max_certificate_bytes=1024*1024):
    """Authenticate the supplied connected socket against the authorized host.

    Does not authorize its destination, send HTTP, acquire credentials, override
    verification errors, or validate revocation. Caller owns socket timeout/close.
    """
    host = validate_reference_host(reference_host)
    secured=service_context(trusted_ca_file=trusted_ca_file).wrap_socket(sock,server_hostname=host)
    try:
        check_verified_chain(secured,max_chain_certificates=max_chain_certificates,max_certificate_bytes=max_certificate_bytes)
        return secured
    except BaseException:
        secured.close()
        raise


def require_http11_protocol(sock):
    """Return negotiated protocol; None explicitly means configured HTTPS/1.1 fallback."""
    selected = sock.selected_alpn_protocol()
    if selected not in (None, 'http/1.1'):
        raise ValueError('negotiated protocol is not HTTP/1.1')
    return selected


def wrap_http11_socket(sock, *, reference_host, trusted_ca_file=None, max_chain_certificates=32, max_certificate_bytes=1024*1024):
    """Verify DNS service identity and protocol before sending any HTTP bytes."""
    host = validate_reference_host(reference_host)
    context = service_context(trusted_ca_file=trusted_ca_file)
    context.set_alpn_protocols(['http/1.1'])
    secured = context.wrap_socket(sock, server_hostname=host)
    try:
        check_verified_chain(secured,max_chain_certificates=max_chain_certificates,max_certificate_bytes=max_certificate_bytes)
        require_http11_protocol(secured)
        return secured
    except Exception:
        secured.close()
        raise
