"""Strict framing for configured one-request HTTP/1.1 fixtures, not full HTTP support."""
import re
from http.server import BaseHTTPRequestHandler

TOKEN=re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")
SINGLE={'host','content-length','transfer-encoding','content-encoding','content-type','authorization','expect'}

def fields(headers):
    if getattr(headers,'defects',[]):raise ValueError('Malformed fields')
    result={}
    for key,value in headers.raw_items():
        if not TOKEN.fullmatch(key) or any(ord(c)<32 and c!='\t' or ord(c)==127 for c in value):raise ValueError('Invalid field')
        key=key.lower()
        if key in SINGLE and key in result:raise ValueError('Duplicate framing/authority field')
        result[key]=value.strip(' \t')
    return result

def request_length(headers,method):
    values=fields(headers)
    if 'transfer-encoding' in values or 'expect' in values or 'content-encoding' in values:raise ValueError('Unsupported coding/expectation')
    raw=values.get('content-length')
    if raw is not None and not re.fullmatch('[0-9]+',raw):raise ValueError('Invalid Content-Length')
    if raw is not None and len(raw)>20:raise ValueError('Content-Length capacity')
    length=int(raw) if raw is not None else 0
    if method in ('GET','HEAD') and length:raise ValueError('Unexpected request body')
    return length

class FixedHTTPHandler(BaseHTTPRequestHandler):
    def handle_expect_100(self):
        self.send_error(400,'Expect unsupported');return False
    def send_error(self,code,message=None,explain=None):
        body=b'{"error":"invalidHttp"}'
        self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('Connection','close');self.end_headers()
        if getattr(self,'command',None)!='HEAD':self.wfile.write(body)
        self.close_connection=True
    def parse_request(self):
        if not super().parse_request():return False
        try:
            if self.request_version!='HTTP/1.1' or not re.fullmatch(rb'[A-Z]+ /[^\x00-\x20\x7f]* HTTP/1\.1\r\n',self.raw_requestline):raise ValueError('Request line')
            # BaseHTTPRequestHandler collapses leading // for browser redirects.
            # These configured endpoints require the original origin-form path.
            self.path=self.raw_requestline.split(b' ',2)[1].decode('iso-8859-1')
            values=fields(self.headers)
            if values.get('host')!=self.expected_authority():raise ValueError('Host authority')
            request_length(self.headers,self.command)
        except ValueError:
            self.send_error(400);return False
        return True

def read_fixed_response(response,limit):
    values=fields(response.headers)
    if 'transfer-encoding' in values or 'content-encoding' in values:raise ValueError('Unsupported response coding')
    raw=values.get('content-length')
    if raw is None or not re.fullmatch('[0-9]+',raw) or len(raw)>20:raise ValueError('Response Content-Length required')
    length=int(raw)
    if length>limit:raise ValueError('Oversized response')
    body=response.read(length+1)
    if len(body)!=length:raise ValueError('Incomplete response')
    return body
