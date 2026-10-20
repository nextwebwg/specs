"""Private Unicode17 provider for configured identifier consumers; shared modules remain untouched."""
import ctypes as C
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import uuid

HERE=Path(__file__).resolve().parent
class ProviderError(ValueError): pass
class ICU17:
    unidata_version='17.0.0'
    def __init__(self, manifest):
        cfg=manifest
        if bytes(C.c_uint16(0x1234))!=(0x1234).to_bytes(2,sys.byteorder):raise ProviderError('Native byte order mismatch')
        if not isinstance(cfg.get('libraries'),dict) or cfg.get('library') not in cfg['libraries']:raise ProviderError('Loaded library must be hash-pinned')
        library=Path(cfg['library']).resolve()
        if str(library)!=cfg['library']:raise ProviderError('Expected canonical library path')
        for p,h in cfg['libraries'].items():
            if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h: raise ProviderError('ICU hash mismatch')
        self.lib=C.CDLL(cfg['library'])
        def f(name,restype,args):
            fn=getattr(self.lib,name+'_78');fn.restype=restype;fn.argtypes=args;return fn
        self._f=f
        for name,expected in [('u_getVersion',[78,3,0,0]),('u_getUnicodeVersion',[17,0,0,0])]:
            a=(C.c_uint8*4)();f(name,None,[C.POINTER(C.c_uint8)])(a)
            if list(a)!=expected:raise ProviderError('ICU version mismatch')
        self._cat=f('u_charType',C.c_int8,[C.c_int32]);self._ccc=f('u_getCombiningClass',C.c_uint8,[C.c_int32]);self._bidi=f('u_charDirection',C.c_int,[C.c_int32])
        self._name=f('u_charName',C.c_int32,[C.c_int32,C.c_int,C.c_char_p,C.c_int32,C.POINTER(C.c_int32)])
        self._norm=f('unorm2_normalize',C.c_int32,[C.c_void_p,C.POINTER(C.c_uint16),C.c_int32,C.POINTER(C.c_uint16),C.c_int32,C.POINTER(C.c_int32)])
        self._fold=f('u_strFoldCase',C.c_int32,[C.POINTER(C.c_uint16),C.c_int32,C.POINTER(C.c_uint16),C.c_int32,C.c_uint32,C.POINTER(C.c_int32)])
        self.normalizers={}
        for form in ['NFC','NFD','NFKC','NFKD']:
            e=C.c_int32();p=f('unorm2_get'+form+'Instance',C.c_void_p,[C.POINTER(C.c_int32)])(C.byref(e));self.check(e)
            if not p:raise ProviderError('Missing normalizer')
            self.normalizers[form]=p
    @staticmethod
    def check(e):
        if e.value>0:raise ProviderError('ICU error '+str(e.value))
    def category(self,c):return 'Cn Lu Ll Lt Lm Lo Mn Me Mc Nd Nl No Zs Zl Zp Cc Cf Co Cs Pd Ps Pe Pc Po Sm Sc Sk So Pi Pf'.split()[self._cat(ord(c))]
    def combining(self,c):return self._ccc(ord(c))
    def bidirectional(self,c):return 'L R EN ES ET AN CS B S WS ON LRE LRO AL RLE RLO PDF NSM BN FSI LRI RLI PDI'.split()[self._bidi(ord(c))]
    def name(self,c):
        b=C.create_string_buffer(256);e=C.c_int32();n=self._name(ord(c),0,b,256,C.byref(e));self.check(e)
        if not n:raise ValueError('Unnamed character')
        return b.value.decode('ascii')
    def transform(self,s,form=None):
        # Experiment allocation guard, not a protocol limit.
        encoding='utf-16-le' if sys.byteorder=='little' else 'utf-16-be'
        raw=s.encode(encoding,'strict');n=len(raw)//2
        if n>1048576:raise ProviderError('Experiment input capacity exceeded')
        src=(C.c_uint16*max(n,1))();C.memmove(src,raw,len(raw));e=C.c_int32()
        def call(dst,cap):
            return self._norm(self.normalizers[form],src,n,dst,cap,C.byref(e)) if form else self._fold(dst,cap,src,n,0,C.byref(e))
        size=call(None,0)
        if e.value not in (0,15) and e.value>0:self.check(e)
        if size<0 or size>8388608:raise ProviderError('Experiment output capacity exceeded')
        dst=(C.c_uint16*(size+1))();e.value=0;actual=call(dst,size+1);self.check(e)
        if actual!=size:raise ProviderError('ICU length changed')
        return bytes(dst)[:size*2].decode(encoding,'strict')
    def normalize(self,form,s):return self.transform(s,form)
    def casefold(self,s):return self.transform(s)

def isolated_idna(provider,cfg):
    root=Path(cfg['idna_root'])
    for rel,h in cfg['idna_files'].items():
        if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=h:raise ProviderError('IDNA source hash mismatch')
    required={'idna/__init__.py','idna/core.py','idna/idnadata.py','idna/intranges.py','idna/package_data.py'}
    if not required.issubset(cfg['idna_files']):raise ProviderError('Incomplete source hash manifest')
    name='_email_next_private_idna17_'+uuid.uuid4().hex
    try:
        spec=importlib.util.spec_from_file_location(name,root/'idna/__init__.py',submodule_search_locations=[str(root/'idna')]);pkg=importlib.util.module_from_spec(spec);sys.modules[name]=pkg;spec.loader.exec_module(pkg)
        core=sys.modules[name+'.core'];data=sys.modules[name+'.idnadata']
        if data.__version__!='17.0.0':raise ProviderError('IDNA data version mismatch')
        core.unicodedata=provider
        return core,data
    except BaseException:
        for key in list(sys.modules):
            if key==name or key.startswith(name+'.'):del sys.modules[key]
        raise
