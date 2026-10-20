"""Experimental strict decoding and proof bridge; no mailbox identity assertion."""
import base64
import copy
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event
HERE=Path(__file__).resolve().parent

def pipeline(record):
    request=copy.deepcopy(record)
    for field in ['state','binding']:
        raw=base64.b64decode(record[field],validate=True)
        decoded=decode_event(raw)
        request[field]={'base64':base64.b64encode(decoded['octets']).decode('ascii'),'value':decoded['value']}
    return json.loads(subprocess.run(['node',str(HERE/'check-genesis.mjs')],input=json.dumps(request),capture_output=True,text=True,check=True).stdout)
