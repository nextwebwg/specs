import test from 'node:test';
import assert from 'node:assert/strict';
import {checkIdentityTransition as check} from './identity-transition.mjs';
const dev=n=>'end0:'+n.repeat(64),hash=n=>n.repeat(64),principal='enp0:'+hash('a');
function fixture(){
 const binding=(device,roles,authority)=>({version:'0',purpose:'device-binding',record:'1'.repeat(32),principal,device,signingKey:hash('c'),roles,notBefore:'0',notAfter:'100',authority});
 const a=binding(dev('1'),['send','receive','enroll','revoke'],{kind:'first-contact'});
 const b=binding(dev('2'),['send','receive'],{kind:'state',digest:hash('f')});
 const previous={version:'0',purpose:'identity-state',principal,record:'2'.repeat(32),revision:'0',previous:[],issuedAt:'0',bindings:[{device:a.device,digest:hash('a')}],revoked:[],signer:a.device};
 const next={...previous,record:'3'.repeat(32),revision:'1',previous:[hash('f')],issuedAt:'1',bindings:[...previous.bindings,{device:b.device,digest:hash('b')}]};
 return {a,b,previous,next,bindings:new Map([[hash('a'),a],[hash('b'),b]])};
}
const run=f=>check(f.previous,f.next,hash('f'),f.bindings,10n);
test('authorized addition satisfies policy without claiming proof validation',()=>assert.deepEqual(run(fixture()),{status:'policy-valid'}));
test('predecessor revision account and time cannot be substituted',()=>{
 for(const patch of [{revision:'2'},{principal:'enp0:'+hash('b')},{previous:[hash('e')]}]){const f=fixture();Object.assign(f.next,patch);assert.equal(run(f).status,'invalid');}
 const f=fixture();f.previous.issuedAt='2';assert.equal(run(f).reason,'predecessor');
});
test('new signer and excessive delegation fail',()=>{
 let f=fixture();f.next.signer=dev('2');assert.equal(run(f).reason,'signer');
 f=fixture();f.b.roles.push('recover');assert.equal(run(f).reason,'delegation');
 f=fixture();f.b.authority.digest=hash('e');assert.equal(run(f).reason,'binding-authority');
});
test('removal requires revocation and retains an administrator',()=>{
 let f=fixture();f.next.bindings=f.next.bindings.slice(1);assert.equal(run(f).reason,'removal');
 f.next.revoked=[dev('1')];assert.equal(run(f).reason,'last-administrator');
 f.b.roles.push('enroll','revoke');assert.equal(run(f).status,'policy-valid');
});
test('existing revocations cannot disappear or target unknown devices',()=>{
 let f=fixture();f.previous={...f.previous,revision:'1',previous:[hash('e')],revoked:[dev('3')]};f.next.revision='2';assert.equal(run(f).reason,'revocation-rollback');
 f=fixture();f.next.revoked=[dev('3')];assert.equal(run(f).reason,'unknown-revocation');
});
test('binding substitution expiry and unresolved records fail',()=>{
 for(const mutate of [f=>{f.b.device=dev('3');},f=>{f.b.notAfter='9';},f=>{f.a.notAfter='9';},f=>{f.bindings.delete(hash('b'));}]){const f=fixture();mutate(f);assert.equal(run(f).status,'invalid');}
});
