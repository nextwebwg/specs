import base64
import hashlib
import json
import os
import ssl
import threading
import sys
from test_hosted_access import HostedTests
from test_service_tls import ServiceTLSTest
from hosted_https import make_hosted_server
from cryptography import x509
from cryptography.hazmat.primitives import serialization
fixture=HostedTests();fixture.setUp();ServiceTLSTest.setUpClass()
try:
    cert,key=ServiceTLSTest('test_valid_san').leaf('host.example')
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3;context.load_cert_chain(cert,key)
    server=make_hosted_server(fixture.store,context)
    origin='https://host.example:'+str(server.server_port)
    fixture.store.service=origin;fixture.store.management_grant['service']=origin
    fixture.store.vault.service=origin;fixture.store.reply_vault.service=origin
    question_mode=os.environ.get('EMAIL_NEXT_HOSTED_QUESTION')=='1'
    if question_mode:
        from hosted_projection import hosted_source_text
        from event_encoding import encode_event
        question=dict(version='1',purpose='contribution',event='3'*32,conversation='2'*32,principal='enp0:'+'1'*64,audience=['enp0:'+'1'*64],disclosures=[dict(kind='provider-hosted',service=origin,model='bearer')],operation=dict(kind='question',text='CONFIDENTIAL_CONTENT_MARKER 日本語',options=[dict(id='4'*32,label='<img src=x onerror=alert(1)> 朝'),dict(id='5'*32,label='Evening & late')]))
        fixture.configuration['content']['text']=hosted_source_text(encode_event(question))
        fixture.raw=encode_event(fixture.req)
    fixture.create()
    spki=x509.load_pem_x509_certificate(cert.read_bytes()).public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    print(json.dumps(dict(question=question_mode,origin=origin,url=origin+'/g/'+'7'*32+'#'+fixture.secret,spki=base64.b64encode(hashlib.sha256(spki).digest()).decode())),flush=True)
    for line in sys.stdin:
        if line.strip()=='stop':break
finally:
    if 'server' in globals():server.shutdown();server.server_close();thread.join(2)
    ServiceTLSTest.tearDownClass();fixture.doCleanups()
