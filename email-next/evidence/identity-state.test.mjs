import test from 'node:test';
import assert from 'node:assert/strict';
import {validateIdentityState} from './identity-state.mjs';
const device=n=>'end0:'+n.repeat(64),hash='a'.repeat(64);
const genesis=()=>({version:'0',purpose:'identity-state',principal:'enp0:'+'1'.repeat(64),record:'2'.repeat(32),revision:'0',previous:[],issuedAt:'1',bindings:[{device:device('1'),digest:hash}],revoked:[],signer:device('1')});
test('genesis shape is distinct from an ordinary successor',()=>{
 const g=genesis();assert.equal(validateIdentityState(g),true);
 assert.equal(validateIdentityState({...g,revision:'1',previous:[hash]}),true);
 for(const patch of [{previous:[hash]},{signer:device('2')},{revoked:[device('2')]},{revision:'1'},{revision:'1',previous:[hash,hash]}])assert.equal(validateIdentityState({...g,...patch}),false);
});
test('rosters and revocations are unique ordered and disjoint',()=>{
 const s={...genesis(),revision:'1',previous:[hash]},one={device:device('1'),digest:hash},two={device:device('2'),digest:hash};
 assert.equal(validateIdentityState({...s,bindings:[one,two],revoked:[device('3')]}),true);
 for(const patch of [{bindings:[]},{bindings:[two,one]},{bindings:[one,one]},{revoked:[device('1')]},{revoked:[device('3'),device('2')]},{revoked:[device('2'),device('2')]}])assert.equal(validateIdentityState({...s,...patch}),false);
});
test('unknown members wrong domains and noncanonical counters are invalid',()=>{
 const g=genesis();
 for(const patch of [{extra:true},{version:'1'},{revision:'01'},{issuedAt:'18446744073709551616'},{issuedAt:1},{principal:g.signer},{signer:g.principal},{bindings:[{device:g.signer,digest:hash,roles:['enroll']}]}])assert.equal(validateIdentityState({...g,...patch}),false);
});
test('a successor signer may be removed in that successor; authority must resolve in predecessor',()=>{
 const s={...genesis(),revision:'1',previous:[hash],bindings:[{device:device('2'),digest:hash}],revoked:[device('1')]};
 assert.equal(validateIdentityState(s),true);
 // This shape result does not prove either device has administrative authority.
});
