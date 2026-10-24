// Synthetic original-record/signature checks only. Objects are constructed test
// data, not a strict JSON decoder, accepted identity store or provider service.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash,createPublicKey,generateKeyPairSync,sign,verify} from 'node:crypto';
const fixture=JSON.parse(readFileSync(new URL('../examples/provider-route-records.json',import.meta.url),'utf8'));
const fields={
 certificate:'version purpose certificate domain issuer serviceSigningKey routeSigningKey notBefore notAfter',
 authorization:'version purpose authorization preparation request nonce domain issuer delegation recipient incarnation serviceSigningKey notBefore notAfter maxRouteSeconds maxCarrierBytes',
 request:'version purpose request nonce issuer delegation recipient sender conversation sourceDomain sourceService sourcePermission sourceDigest notBefore notAfter maxCarrierBytes',
 inspection:'version purpose issuer issuance requestDigest nonce notBefore notAfter',
 issuance:'version purpose issuance request nonce issuer delegation authority route alias recipient sender conversation sourceDomain sourceService sourcePermission sourceDigest routeKey notBefore notAfter maxCarrierBytes',
};
const purposes={certificate:'relay-route-certificate',authorization:'relay-receiving-service',request:'relay-route-request',inspection:'relay-route-request-inspect',issuance:'relay-route-issued'};
const domains={certificate:'mail/relay/route-certificate/v1',authorization:'mail/relay/receiving-service/v1',request:'mail/relay/route-request/v1',inspection:'mail/relay/route-request-inspect/v1',issuance:'mail/relay/route-issuance/v1'};
const decoded=w=>JSON.parse(Buffer.from(w.payload,'base64').toString('utf8'));
const hash=b=>createHash('sha256').update(b).digest('hex');
const digest=w=>hash(Buffer.from(w.payload,'base64'));
function exact(v,inventory){assert.deepEqual(Object.keys(v).sort(),inventory.split(' ').sort());}
function hex(v,n=64){assert.equal(typeof v,'string');assert.match(v,new RegExp('^(?!0+$)[0-9a-f]{'+n+'}$'));}
function integer(v,positive=false){assert.equal(typeof v,'string');assert.match(v,/^(0|[1-9][0-9]*)$/);const n=BigInt(v);assert.ok(n<2n**64n&&n>=BigInt(positive));return n;}
function interval(v,time){const a=integer(v.notBefore),b=integer(v.notAfter);assert.ok(a<=b);if(time)assert.ok(a<=BigInt(time[0])&&BigInt(time[0])<=BigInt(time[1])&&BigInt(time[1])<=b);}
function endpoint(v){exact(v,'principal device state binding key');assert.match(v.principal,/^enp0:(?!0+$)[0-9a-f]{64}$/);assert.match(v.device,/^end0:(?!0+$)[0-9a-f]{64}$/);for(const k of ['state','binding','key'])hex(v[k]);}
function shape(kind,v){
 exact(v,fields[kind]);assert.equal(v.version,'1');assert.equal(v.purpose,purposes[kind]);interval(v);
 for(const [name,x] of Object.entries(v)){
  if(name==='sender'||(name==='recipient'&&kind==='authorization')){endpoint(x);continue;}
  assert.equal(typeof x,'string');
  if(['notBefore','notAfter','maxRouteSeconds','maxCarrierBytes'].includes(name))integer(x,name.startsWith('max'));
  if(['certificate','authorization','preparation','request','conversation'].includes(name))hex(x,32);
  if(['nonce','delegation','incarnation','serviceSigningKey','routeSigningKey','sourcePermission','sourceDigest','requestDigest','authority','routeKey','route','issuance'].includes(name))hex(x);
  if(name==='recipient')assert.match(x,/^enp0:(?!0+$)[0-9a-f]{64}$/);
 }
}
function input(domain,bytes){const n=Buffer.alloc(4);n.writeUInt32BE(bytes.length);return Buffer.concat([Buffer.from(domain+'\0'),n,bytes]);}
function signature(w,key,domain){
 exact(w,'payload signature');hex(w.signature,128);hex(key);
 const b=Buffer.from(w.payload,'base64');assert.equal(b.toString('base64'),w.payload);assert.ok(b.length<=262144);
 const publicKey=createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),Buffer.from(key,'hex')]),format:'der',type:'spki'});
 assert.equal(verify(null,input(domain,b),publicKey,Buffer.from(w.signature,'hex')),true);
}
const pair=()=>{const p=generateKeyPairSync('ed25519');return {...p,hex:p.publicKey.export({type:'spki',format:'der'}).subarray(-32).toString('hex')};};
function signed(kind,v,k){const b=Buffer.from(JSON.stringify(v));return {payload:b.toString('base64'),signature:sign(null,input(domains[kind],b),k.privateKey).toString('hex')};}
function prefix(v){const b=Buffer.from(v),n=Buffer.alloc(2);assert.ok(b.length<=65535);n.writeUInt16BE(b.length);return Buffer.concat([n,b]);}
function issuanceId(w){const r=decoded(w);return hash(Buffer.concat([Buffer.from('mail/relay/issuance/v1\0'),prefix(r.issuer),prefix(r.sourceService),Buffer.from(r.sourcePermission,'hex'),Buffer.from(r.request,'hex'),Buffer.from(digest(w),'hex')]));}
const expected={issuer:'https://inbox.example',domain:'inbox.example',principal:decoded(fixture.authorization).recipient.principal,recipientKey:decoded(fixture.authorization).recipient.key,serviceKey:fixture.descriptor.serviceSigningKey};
function check(f,time=['215','216'],e=expected){
 const a=decoded(f.authorization),c=decoded(f.certificate),r=decoded(f.request),i=decoded(f.issuance),q=decoded(f.inspection),s=decoded(f.source);
 for(const [kind,v] of Object.entries({authorization:a,certificate:c,request:r,issuance:i,inspection:q})){shape(kind,v);interval(v,time);}
 signature(f.authorization,e.recipientKey,domains.authorization);signature(f.certificate,e.serviceKey,domains.certificate);signature(f.request,s.sender.key,domains.request);signature(f.issuance,c.routeSigningKey,domains.issuance);signature(f.inspection,s.routeKey,domains.inspection);signature(f.source,s.sender.key,'email2/relay/source-permission/v0');
 for(const v of [a,c]){assert.equal(v.domain,e.domain);assert.equal(v.issuer,e.issuer);assert.equal(v.serviceSigningKey,e.serviceKey);}
 for(const v of [r,i,q])assert.equal(v.issuer,e.issuer);
 assert.equal(a.recipient.principal,e.principal);for(const v of [r,i,s])assert.equal(v.recipient,e.principal);
 assert.equal(i.authority,digest(f.authorization));assert.equal(r.sourceDigest,digest(f.source));assert.equal(i.issuance,issuanceId(f.request));assert.equal(q.issuance,i.issuance);assert.equal(q.requestDigest,digest(f.request));assert.equal(i.request,r.request);assert.equal(i.nonce,r.nonce);
 for(const k of ['sourceDomain','sourceService','sourcePermission','sourceDigest','conversation','recipient'])assert.equal(i[k],r[k]);
 assert.equal(s.domain,r.sourceDomain);assert.equal(s.issuer,r.sourceService);assert.equal(s.permission,r.sourcePermission);assert.equal(s.targetService,e.issuer);assert.equal(s.conversation,i.conversation);assert.deepEqual(i.sender,s.sender);assert.deepEqual(r.sender,s.sender);assert.equal(i.routeKey,s.routeKey);
 assert.equal(i.delegation,r.delegation);assert.equal(r.delegation,hash(Buffer.from(JSON.stringify(f.descriptor))));
 assert.equal(f.descriptor.domain,e.domain);assert.equal(f.descriptor.service,e.issuer);assert.equal(f.descriptor.serviceSigningKey,e.serviceKey);assert.ok(f.descriptor.roles.includes('recipient-mask'));assert.equal(i.alias.split('@')[1],e.domain);assert.match(i.alias,/^r-(?!0+@)[0-9a-f]{32}@/);
 for(const v of [a,c,s,r]){assert.ok(BigInt(i.notBefore)>=BigInt(v.notBefore));assert.ok(BigInt(i.notAfter)<=BigInt(v.notAfter));}
 assert.ok(BigInt(i.notAfter)-BigInt(i.notBefore)<=BigInt(a.maxRouteSeconds));for(const v of [a,s,r])assert.ok(BigInt(i.maxCarrierBytes)<=BigInt(v.maxCarrierBytes));
 return 'synthetic-original-signatures-and-scope-valid';
}
test('actual recipient, source, service, certified issuance and route-key signatures bind original records',()=>assert.equal(check(fixture),'synthetic-original-signatures-and-scope-valid'));
test('every record inventory rejects omitted and additional members',()=>{
 for(const kind of Object.keys(fields)){
  for(const key of fields[kind].split(' ')){const v=decoded(fixture[kind]);delete v[key];assert.throws(()=>shape(kind,v));}
  assert.throws(()=>shape(kind,{...decoded(fixture[kind]),extension:{}}));
 }
});
test('service association contains no alias, conversation, peer list, contact policy or token',()=>{
 for(const key of ['alias','conversation','peers','contacts','admission','token']){const a=decoded(fixture.authorization);assert.equal(Object.hasOwn(a,key),false);assert.throws(()=>shape('authorization',{...a,[key]:[]}));}
});
test('one unchanged service association permits provider-certified issuance-key rotation without alias approval',()=>{
 const service=pair(),recipient=pair(),a={...decoded(fixture.authorization),serviceSigningKey:service.hex};a.recipient.key=recipient.hex;
 const original=signed('authorization',a,recipient),saved=JSON.stringify(original);signature(original,recipient.hex,domains.authorization);
 for(const route of [pair(),pair()]){const c={...decoded(fixture.certificate),serviceSigningKey:service.hex,routeSigningKey:route.hex};signature(signed('certificate',c,service),service.hex,domains.certificate);assert.equal(c.serviceSigningKey,a.serviceSigningKey);assert.equal(JSON.stringify(original),saved);}
});
test('independently selected recipient and provider authority reject self-consistent foreign keys',()=>{
 assert.throws(()=>check(fixture,undefined,{...expected,serviceKey:pair().hex}));assert.throws(()=>check(fixture,undefined,{...expected,recipientKey:pair().hex}));
 for(const key of ['issuer','domain','principal'])assert.throws(()=>check(fixture,undefined,{...expected,[key]:'foreign'}));
});
test('original-byte changes, reserialization and cross-purpose signatures fail',()=>{
 for(const kind of Object.keys(fields)){
  const w=fixture[kind],key=kind==='certificate'?expected.serviceKey:kind==='authorization'?expected.recipientKey:kind==='request'?decoded(fixture.source).sender.key:kind==='inspection'?decoded(fixture.source).routeKey:decoded(fixture.certificate).routeSigningKey;
  const altered={...w,payload:Buffer.from(JSON.stringify(decoded(w),null,2)).toString('base64')};assert.notEqual(altered.payload,w.payload);assert.throws(()=>signature(altered,key,domains[kind]));
  for(const other of Object.keys(fields))if(other!==kind)assert.throws(()=>signature(w,key,domains[other]));
 }
});
test('complete credible-time interval must fit all original finite authorities',()=>{
 assert.equal(check(fixture,['220','220']),'synthetic-original-signatures-and-scope-valid');for(const time of [['99','100'],['219','221'],['216','215'],['900','901']])assert.throws(()=>check(fixture,time));
});
test('uint64 fields reject numbers, noncanonical spelling, negative values and overflow',()=>{
 for(const kind of Object.keys(fields))for(const key of fields[kind].split(' ').filter(x=>['notBefore','notAfter','maxRouteSeconds','maxCarrierBytes'].includes(x)))for(const bad of [1,'01','-1','18446744073709551616',...(key.startsWith('max')?['0']:[])]){const v=decoded(fixture[kind]);v[key]=bad;assert.throws(()=>shape(kind,v));}
});
test('issuance handle commits original source, request bytes and origin boundaries',()=>{
 assert.equal(issuanceId(fixture.request),decoded(fixture.issuance).issuance);
 for(const key of ['issuer','sourceService','sourcePermission','request']){const r=decoded(fixture.request);r[key]+='1';const w={...fixture.request,payload:Buffer.from(JSON.stringify(r)).toString('base64')};assert.notEqual(issuanceId(w),decoded(fixture.issuance).issuance);}
});
test('substituted original authority, certificate, scope or inspection cannot validate',()=>{
 for(const kind of Object.keys(fields)){const f=structuredClone(fixture),v=decoded(f[kind]);v.purpose+='-changed';f[kind].payload=Buffer.from(JSON.stringify(v)).toString('base64');assert.throws(()=>check(f));}
});
test('retained device-approved route0 cannot be parsed as current issued route1',()=>assert.throws(()=>shape('issuance',{...decoded(fixture.issuance),version:'0',purpose:'relay-route-approval',preparation:'1'.repeat(32),recipient:decoded(fixture.authorization).recipient})));
