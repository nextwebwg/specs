"""Trusted internal MLS bridge, not a network authentication interface.

Processed metadata and epoch snapshots must come from accepted library state.
The returned projection result grants neither current account authority nor effects.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
from event_encoding import decode_event,MAX_EVENT_OCTETS


def check(octets,group,epoch,sender,credential,aad,snapshot_group,snapshot_epoch,context,members,*,identity_store=None,time=None,trust_policy=None,configured_endpoint_ordering=False,configured_quorum_ordering=False,configured_application=None):
    if aad!='':return 'unsupported-aad'
    if group!=snapshot_group or epoch!=snapshot_epoch:return 'epoch-context-mismatch'
    if not re.fullmatch('[0-9a-f]+',group) or len(group)%2:return 'invalid-group'
    if not re.fullmatch('0|[1-9][0-9]*',epoch) or int(epoch)>2**64-1:return 'invalid-epoch'
    roster=[];indices=set();pairs=set();selected=None
    for item in members:
        parts=item.split(':')
        if len(parts)!=3:return 'invalid-roster'
        index,identity,key=parts
        if (not re.fullmatch('0|[1-9][0-9]*',index) or int(index)>2**32-1
                or not re.fullmatch('[0-9a-f]{170}',identity) or not re.fullmatch('[0-9a-f]{64}',key)
                or index in indices or identity in pairs):return 'invalid-roster'
        indices.add(index);pairs.add(identity);roster.append(identity)
        if index==sender:selected=(identity,key)
    if selected is None:return 'sender-not-member'
    if selected[0]!=credential:return 'sender-credential-mismatch'
    # selected[1] is the authenticated epoch leaf key. It is not an independently
    # accepted account binding; callers still need current IdentityStore authority.
    if identity_store is not None:
        authority=identity_store.check_device(bytes.fromhex(credential),bytes.fromhex(selected[1]),
            role='send',time=time,trust_policy=trust_policy)
        if authority.get('status')!='authorized-unverified':return 'identity-'+authority['status']
    event=decode_event(octets)['value']
    context=decode_event(bytes.fromhex(context))['value']
    result=subprocess.run(['node',str(Path(__file__).with_name('check-mls-contribution.mjs'))],
        input=json.dumps({'event':event,'credential':credential,'context':context,'members':roster,'configuredEndpointOrdering':configured_endpoint_ordering,'configuredQuorumOrdering':configured_quorum_ordering,'configuredApplication':configured_application}),
        text=True,capture_output=True,check=True,timeout=10)
    return result.stdout

if __name__=='__main__':
    sys.stdout.write(check(sys.stdin.buffer.read(MAX_EVENT_OCTETS+1),*sys.argv[1:9],sys.argv[9:]))
