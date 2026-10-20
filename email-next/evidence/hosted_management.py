"""Direct configured management transport and local receipt provenance.

Evidence IDs authorize only local inspection of the trusted application database.
They are not transferable TLS proofs. TLS/IDNA/revocation helper limits remain.
"""
from http_framing import read_fixed_response
import hashlib
import http.client
import json
import socket
import re
import uuid
from urllib.parse import urlsplit
from event_encoding import decode_event
from hosted_access import parse
from service_tls import wrap_http11_socket,validate_reference_host

class HostedManagementClient:
    def __init__(self,sender,*,ca_file,address):
        self.sender=sender;self.ca=ca_file;self.address=address
        origin=urlsplit(sender.vault.service)
        if origin.scheme!='https' or origin.path or origin.query or origin.fragment or origin.username or origin.password:
            raise ValueError('configured origin')
        self.host=validate_reference_host(origin.hostname);self.port=origin.port or 443
        if sender.vault.service!='https://'+self.host+(':'+str(self.port) if self.port!=443 else ''):raise ValueError('origin spelling')
        with sender.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS management_evidence(id TEXT PRIMARY KEY,operation TEXT,grant_id TEXT,purpose TEXT,request_digest TEXT,endpoint TEXT,method TEXT,receipt BLOB,state TEXT)')
    def request(self,operation,token,*,lookup=False):
        if not lookup:
            with self.sender.db() as db:
                if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hosted_disclosure_grants'").fetchone() and db.execute('SELECT 1 FROM hosted_disclosure_grants WHERE create_operation=?',(operation,)).fetchone():raise ValueError('Use source-bound management')
        return self._request(operation,token,lookup=lookup)

    def _request(self,operation,token,*,lookup=False):
        if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9._~+/-]+=*',token):raise ValueError('credential grammar')
        raw=self.sender.load(operation)
        value=decode_event(raw)['value'];purpose=value.get('purpose');req=parse(raw,purpose)
        if purpose not in ('hosted-grant-create','hosted-grant-revoke'):raise ValueError('management purpose')
        if purpose=='hosted-grant-create' and req['version']=='1':
            from hosted_reply_admission import template_limit
            with self.sender.db() as db:template=self.sender.vault.get(db,'observer-template:'+operation,'hosted-observer-template',req['grant'])
            if str(template_limit(template))!=req['replyTextLimit']:raise ValueError('missing template admission binding')
        path='/v0/operations/'+operation if lookup else '/v0/grants' if purpose=='hosted-grant-create' else '/v0/grants/'+req['grant']+'/revoke'
        method='GET' if lookup else 'POST'
        status,body=self._exchange(method,path,raw if not lookup else None,token)
        if status!=200:return {'http':status,'evidence':None}
        receipt=decode_event(body)['value']
        expected=dict(version='0',purpose='hosted-management-result',service=self.sender.vault.service,owner=self.sender.vault.owner,operation=operation,grant=req['grant'],requestDigest=hashlib.sha256(raw).hexdigest(),outcome='confirmed',reason='created' if purpose=='hosted-grant-create' else 'revoked')
        # Persist contradictions only after exact schema and request/authority binding.
        if not isinstance(receipt,dict) or set(receipt)!=set(expected) or receipt.get('outcome')!='confirmed' or receipt.get('reason') not in ('created','revoked') or any(receipt.get(k)!=v for k,v in expected.items() if k!='reason'):raise ValueError('management receipt mismatch')
        contradictory=receipt['reason']!=expected['reason']
        identity=uuid.uuid4().hex
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE')
            previous=db.execute('SELECT receipt FROM management_evidence WHERE operation=?',(operation,)).fetchall()
            conflict=contradictory or any(decode_event(row[0])['value']!=receipt for row in previous)
            if conflict:db.execute("UPDATE management_evidence SET state='conflict' WHERE operation=?",(operation,))
            db.execute('INSERT INTO management_evidence VALUES(?,?,?,?,?,?,?,?,?)',(identity,operation,req['grant'],purpose,expected['requestDigest'],self.sender.vault.service+path,method,body,'conflict' if conflict else 'observed'))
        return {'http':200,'evidence':identity,'state':'conflict' if conflict else 'observed'}


    def _exchange(self,method,path,raw,token,*,max_octets=1048576):
        if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9._~+/-]+=*',token):raise ValueError('credential grammar')
        conn=http.client.HTTPConnection(self.host,self.port,timeout=5)
        sock=socket.create_connection(self.address,timeout=5)
        try:
            conn.sock=wrap_http11_socket(sock,reference_host=self.host,trusted_ca_file=self.ca)
            conn.request(method,path,body=raw,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','Accept':'application/json','Cache-Control':'no-store','Connection':'close'})
            response=conn.getresponse()
            body=read_fixed_response(response,max_octets)
            if len(body)>max_octets:raise ValueError('response bound')
            if response.status!=200:return response.status,body
            if response.getheader('Content-Type')!='application/json' or response.getheader('Cache-Control')!='no-store':raise ValueError('response headers')
            return response.status,body
        finally:conn.close();sock.close()
