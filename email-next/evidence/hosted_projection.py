"""Use the authoritative readable question projection; never infer an answer."""
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event


def hosted_source_text(application):
    value=decode_event(application)['value'];kind=value.get('operation',{}).get('kind')
    if kind=='message':return value['operation']['text']
    if kind!='question':raise ValueError('Unsupported hosted source projection')
    projected=subprocess.run(['node',str(Path(__file__).with_name('project-event.mjs'))],input=application,capture_output=True,check=True,timeout=10)
    result=json.loads(projected.stdout)
    if result.get('state')!='projected' or not isinstance(result.get('text'),str):raise ValueError('Hosted question projection unavailable')
    return result['text']
