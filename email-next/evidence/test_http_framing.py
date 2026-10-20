import http.client
import io
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer
from http_framing import FixedHTTPHandler,read_fixed_response

class FakeSocket:
 def __init__(self,raw):self.raw=raw
 def makefile(self,*args):return io.BytesIO(self.raw)
class FramingTests(unittest.TestCase):
 def response(self,headers,body=b'{}'):
  r=http.client.HTTPResponse(FakeSocket(b'HTTP/1.1 200 OK\r\n'+headers+b'\r\n\r\n'+body));r.begin();return r
 def test_length_complete_only(self):
  self.assertEqual(read_fixed_response(self.response(b'Content-Length: 2'),10),b'{}')
  for h,b in [(b'Content-Length: 3',b'{}'),(b'Content-Length: -1',b'{}'),(b'',b'{}'),(b'Content-Length: 2\r\nContent-Length: 2',b'{}'),(b'Content-Length: 2\r\nTransfer-Encoding: chunked',b'0\r\n\r\n'),(b'Transfer-Encoding:',b'{}')]:
   with self.subTest(h=h),self.assertRaises((ValueError,http.client.IncompleteRead)):read_fixed_response(self.response(h,b),10)
 def test_rejected_before_handler(self):
  calls=[]
  class Handler(FixedHTTPHandler):
   protocol_version='HTTP/1.1'
   def log_message(self,*args):pass
   def expected_authority(self):return 'service.example'
   def do_POST(self):
    calls.append(self.path);self.send_response(200);self.send_header('Content-Length','0');self.send_header('Connection','close');self.end_headers();self.close_connection=True
   do_GET=do_POST
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever);thread.start()
  try:
   cases=[b'Content-Length: 0\r\n',b'Host: other\r\n',b'Host: service.example\r\nHost: service.example\r\n',b'Host: service.example\r\nTransfer-Encoding:\r\n',b'Host: service.example\r\nContent-Length: 0\r\nContent-Length: 0\r\n',b'Host: service.example\r\nContent-Length : 0\r\n',b'Host: service.example\r\nX-Fold: a\r\n b\r\n',b'Host: service.example\r\nExpect: 100-continue\r\n',b'Host: service.example\r\nContent-Length: 1\r\n']
   requests=[b'GET / HTTP/1.1\r\n'+headers+b'\r\n' for headers in cases]
   for request in requests:
    with self.subTest(request=request),socket.create_connection(server.server_address,timeout=2) as conn:
     conn.sendall(request);reply=b''
     while part:=conn.recv(4096):reply+=part
     self.assertTrue(reply.startswith(b'HTTP/1.1 400'),reply);self.assertIn(b'Cache-Control: no-store',reply)
   self.assertEqual(calls,[])
   for target in (b'//submit',b'///submit'):
    with socket.create_connection(server.server_address,timeout=2) as conn:
     conn.sendall(b'GET '+target+b' HTTP/1.1\r\nHost: service.example\r\n\r\n')
     while conn.recv(4096):pass
   self.assertEqual(calls,['//submit','///submit'])
  finally:server.shutdown();thread.join();server.server_close()
if __name__=='__main__':unittest.main()
