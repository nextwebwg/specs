"""Synthetic local mail collection: real SMTP seed/reply and HTTP isolation."""
import http.client,json,threading,unittest,queue
from email import policy
from email.parser import BytesParser
from client_flow_server import serve

class ThreadCollectionTests(unittest.TestCase):
 def test_collection_selection_reply_isolation_and_order(self):
  ready=queue.Queue()
  def run():
   server,demo=serve();ready.put((server,demo))
   try:server.serve_forever()
   finally:server.server_close();demo.close()
  worker=threading.Thread(target=run);worker.start();server,demo=ready.get(timeout=30)
  try:
   def request(method,path,value=None,thread=None):
    c=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=10)
    headers={}
    if value is not None:
     headers={'Content-Type':'application/json','Origin':f'http://127.0.0.1:{server.server_port}','X-Client-Session':demo.nonce}
     if thread is not None:headers['X-Conversation-ID']=thread
    c.request(method,path,None if value is None else json.dumps(value),headers);r=c.getresponse();body=r.read();status=r.status;c.close();return status,body
   status,body=request('GET','/state');state=json.loads(body)
   self.assertEqual(status,200);self.assertEqual(state['selectedThread']['id'],'project')
   self.assertEqual([x['activity'] for x in state['threads']],sorted([x['activity'] for x in state['threads']],reverse=True))
   other=json.loads(request('GET','/state?thread=other')[1]);self.assertFalse(other['selectedThread']['contact']);self.assertTrue(any(not x['contact'] for x in other['selectedThread']['participants']))
   maya=json.loads(request('GET','/state?thread=maya')[1]);self.assertTrue(maya['selectedThread']['contact']);self.assertEqual(maya['selectedThread']['title'],'Maya Chen')
   raw=request('GET','/original/'+maya['timeline'][0]['id']+'.eml')[1];mail=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertEqual(mail['From'],'maya@example.invalid');self.assertEqual(mail.get_content(),maya['timeline'][0]['text'])
   self.assertEqual(request('POST','/answer',{'action':'x','option':'x','token':'x'},'maya')[0],409)
   status,body=request('POST','/reply',{'text':'Yes, noon works.'},'maya');updated=json.loads(body)
   self.assertEqual(status,200);self.assertEqual(updated['threads'][0]['id'],'maya');self.assertEqual(updated['timeline'][-1]['sender'],'Carol');self.assertFalse(updated['timeline'][-1]['protected'])
   raw=request('GET','/original/'+updated['timeline'][-1]['id']+'.eml')[1];reply=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertEqual(updated['replyTargets'][-1]['parent'],maya['replyTargets'][0]['id']);self.assertEqual(reply['In-Reply-To'],maya['legacyQuestion']['id']);self.assertEqual(reply['To'],'maya@example.invalid')
   # Default follows the latest actual received message; an explicit earlier
   # target is stable and cannot be borrowed from another conversation.
   first_target=maya['replyTargets'][0]['id'];latest=updated['replyTargets'][-1]['id']
   again=json.loads(request('POST','/reply',{'text':'Latest reply'},'maya')[1])
   raw=request('GET','/original/'+again['timeline'][-1]['id']+'.eml')[1];last=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertEqual(again['replyTargets'][-1]['parent'],latest);self.assertEqual(last['In-Reply-To'],reply['Message-ID']);self.assertEqual(again['timeline'][-1]['parentText'].strip(),'Yes, noon works.')
   earlier=json.loads(request('POST','/reply',{'text':'Earlier reply','replyTo':first_target},'maya')[1])
   raw=request('GET','/original/'+earlier['timeline'][-1]['id']+'.eml')[1];self.assertEqual(BytesParser(policy=policy.default).parsebytes(raw)['In-Reply-To'],mail['Message-ID'])
   self.assertEqual(earlier['replyTargets'][-1]['parent'],first_target)
   self.assertEqual(request('POST','/reply',{'text':'Cross thread','replyTo':first_target},'sam')[0],409)
   self.assertEqual(request('POST','/reply',{'text':'New','replyTo':None},'maya')[0],409)
   fresh=json.loads(request('POST','/reply',{'text':'Only this new text','replyTo':None,'subject':'A new topic'},'maya')[1])
   self.assertNotEqual(fresh['selectedThread']['id'],'maya');self.assertEqual(fresh['selectedThread']['title'],'Maya Chen');self.assertEqual(len(fresh['replyTargets']),1)
   raw=request('GET','/original/'+fresh['timeline'][0]['id']+'.eml')[1];newmail=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertIsNone(newmail['In-Reply-To']);self.assertIsNone(newmail['References']);self.assertEqual(newmail['Subject'],'A new topic');self.assertEqual(newmail.get_content(),'Only this new text\r\n')
   self.assertIsNone(fresh['replyTargets'][0]['parent'])
   self.assertNotIn(b'Would noon',raw)
   # Account IDs resolve trusted local grants; the browser cannot set From.
   work=json.loads(request('POST','/reply',{'text':'From work','account':'work'},'maya')[1])
   raw=request('GET','/original/'+work['timeline'][-1]['id']+'.eml')[1];workmail=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertEqual(workmail['From'],'carol@work.example.invalid');self.assertEqual(workmail['To'],'maya@example.invalid');self.assertFalse(work['timeline'][-1]['protected'])
   self.assertEqual(request('POST','/reply',{'text':'Spoof','account':'attacker@example.invalid'},'maya')[0],409)
   self.assertEqual(request('POST','/reply',{'text':'Spoof','address':'attacker@example.invalid'},'maya')[0],409)
   demo.sender_accounts['work']['enabled']=False
   self.assertEqual(request('POST','/reply',{'text':'Withdrawn grant','account':'work'},'maya')[0],409)
   demo.sender_accounts['work']['enabled']=True

   project=json.loads(request('GET','/state')[1]);self.assertEqual(project['timeline'],state['timeline'])
   self.assertEqual(request('GET','/state?thread=unknown')[0],404)
   self.assertEqual(request('GET','/state?thread=maya&thread=sam')[0],404)
   answered=json.loads(request('POST','/answer',{'action':'answerForTarget','option':project['question']['options'][0]['id'],'token':project['token']})[1])
   self.assertEqual(answered['timeline'][-1]['replyTarget'],answered['replyTargets'][-1]['id']);self.assertTrue(answered['timeline'][-1]['protected'])
   self.assertEqual(answered['replyTargets'][-1]['parent'],answered['questionReplyTarget'])
   self.assertEqual(request('POST','/reply',{'text':'Project reply'})[0],200)
   self.assertEqual(json.loads(request('GET','/state')[1])['threads'][0]['id'],'project')
  finally:server.shutdown();worker.join()
