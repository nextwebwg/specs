"""Explicit test-only fresh owner provisioning; never imports legacy writer keys."""
from pathlib import Path
from vault_key_owner import VaultKeyOwner

def owner_for(path):
    return VaultKeyOwner(Path(path).resolve().parent/'fixture-writer-owner.sqlite')

def fresh_key(path):
    return owner_for(path).provision()

def HostedSender(path, **kwargs):
    from hosted_sender import HostedSender as Real
    return Real(path, writer_owner=owner_for(path), **kwargs)

def HostedStore(path, **kwargs):
    from hosted_access import HostedStore as Real
    return Real(path, writer_owner=owner_for(path), **kwargs)

from hosted_access import HostedStore as _Store
HostedStore.provision = _Store.provision

def NativeAuthorization(path, registration_bytes, **kwargs):
    from service_authorization_client import NativeAuthorization as Real
    return Real(path, registration_bytes, writer_owner=owner_for(path), **kwargs)
