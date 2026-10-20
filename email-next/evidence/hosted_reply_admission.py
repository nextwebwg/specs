"""Exact serialized-text admission. Shape validation is not author/MLS authorization."""
import copy
import json
from pathlib import Path
import subprocess
from event_encoding import serialize_json,decode_event,MAX_EVENT_OCTETS
from hosted_access import parse
from service_answer import identifier


def template_limit(template):
    value=decode_event(template)['value']
    if value.get('version')!='1' or value.get('operation',{}).get('kind')!='hosted-holder-observation' or value['operation'].get('text')!='':raise ValueError('observer template')
    if value['operation']['target'].get('conversation')!=value.get('conversation'):raise ValueError('target conversation')
    probe=copy.deepcopy(value);probe['operation']['text']='x'
    check=subprocess.run(['node',str(Path(__file__).with_name('check-decoded-envelope.mjs'))],input=serialize_json(probe),capture_output=True,check=True)
    if json.loads(check.stdout)!={'shapeValid':True}:raise ValueError('observer template shape')
    if template!=serialize_json(value):raise ValueError('template serialization')
    limit=MAX_EVENT_OCTETS-len(template)+2
    if not 3<=limit<=MAX_EVENT_OCTETS:raise ValueError('no reply capacity')
    return limit


def retain_template(sender,create_operation,template):
    limit=template_limit(template);value=decode_event(template)['value']
    with sender.db() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT grant_id,purpose FROM outgoing WHERE operation=?',(create_operation,)).fetchone()
        if not row or row[1]!='hosted-grant-create':raise ValueError('create required')
        req=parse(sender.vault.get(db,create_operation,row[1],row[0]),row[1])
        if req['version']!='1' or req['replyTextLimit']!=str(limit) or value['principal']!=sender.vault.owner or value['operation']['target']!=req['contribution'] or value['operation']['service']!=sender.vault.service:raise ValueError('template/create binding')
        sender.vault.put(db,'observer-template:'+create_operation,'hosted-observer-template',row[0],template)
    return limit


def fill_template(template,text,event):
    limit=template_limit(template)
    if not identifier(event) or not isinstance(text,str) or not text.strip() or len(serialize_json(text))>limit:raise ValueError('reply admission')
    value=decode_event(template)['value'];value['operation']['text']=text;value['event']=event
    raw=serialize_json(value);decode_event(raw)
    return raw
