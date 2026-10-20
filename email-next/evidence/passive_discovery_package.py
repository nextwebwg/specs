"""Package-only adapter for use after a separate discovery/identity decision.

The caller MUST obtain accepted_signing_key from accepted identity evidence, not
an unchecked advertisement. No successful result authenticates that caller input,
refreshes an identity snapshot, validates a mailbox, or authorizes admission.
"""
import json
from pathlib import Path
import subprocess
from passive_discovery import hexadecimal, uint64
from event_encoding import MAX_EVENT_OCTETS


def validate_package(package_octets, *, principal, device, accepted_signing_key,
                     earliest, latest, executable):
    """executable is a trusted local build path, never supplied by received mail.

    Pass the parsed assertion's exact key_package_octets, identifiers and time
    only after verify_passive_discovery succeeds; recheck identity at release.
    """
    if not isinstance(package_octets, bytes):
        raise TypeError('Expected exact package bytes')
    if len(package_octets) > MAX_EVENT_OCTETS:
        return {'status':'rejected','reason':'size'}
    for value,prefix in [(principal,'enp0:'),(device,'end0:')]:
        if not isinstance(value,str) or not value.startswith(prefix) or not hexadecimal(value[5:],64) or value[5:]=='0'*64:
            raise ValueError('Invalid identifier')
    if not isinstance(accepted_signing_key,bytes) or len(accepted_signing_key)!=32:
        raise ValueError('Expected accepted Ed25519 key bytes')
    uint64(earliest);uint64(latest)
    output=subprocess.run([str(Path(executable).resolve()),principal[5:],device[5:],accepted_signing_key.hex(),earliest,latest],
                          input=package_octets,capture_output=True,timeout=15)
    if output.returncode not in (0,1):
        raise RuntimeError('Package validator failed')
    result=json.loads(output.stdout)
    if result=={'status':'package-valid'} and output.returncode==0:
        return result
    if output.returncode==1 and set(result)=={'status','reason'} and result['status']=='rejected' and isinstance(result['reason'],str):
        return result
    raise RuntimeError('Unexpected package validator result')
