"""Assertion9 signature/accepted-identity/native-package candidate verification.

Not local issuance/custody, publication, association, admission or release. Older
assertion8 callers retain their exact version and cannot select9 implicitly.
"""
from suite_discovery8 import verify_version


def verify(octets, identity, binary, *, time, trust_policy,
           maximum_lifetime=None, maximum_control_lifetime='604800'):
    return verify_version(octets, identity, binary, time=time, trust_policy=trust_policy,
                          version='9', maximum_lifetime=maximum_lifetime,
                          maximum_control_lifetime=maximum_control_lifetime)
