import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEnvelopeShape,checkEnvelopeContext} from './event-envelope.mjs';
const principal=p=>['alice','bob','mallory'].includes(p);
const fixture=()=>({version:'0',purpose:'contribution',event:'1'.repeat(32),conversation:'2'.repeat(32),principal:'alice',audience:['alice','bob'],operation:{kind:'form',form:'3'.repeat(32),title:'Question',fields:[],supersedes:[]}});
const context=e=>({status:'verified',version:e.version,purpose:e.purpose,conversation:e.conversation,principal:e.principal,audience:[...e.audience]});
test('exact envelope shape and operation required',()=>{
 const e=fixture();assert.equal(validateEnvelopeShape(e,principal),true);
 for(const key of Object.keys(e)){const v={...e};delete v[key];assert.equal(validateEnvelopeShape(v,principal),false);}
 assert.equal(validateEnvelopeShape({...e,extra:true},principal),false);
 assert.equal(validateEnvelopeShape({...e,operation:{kind:'execute'}},principal),false);
});
test('unknown version and noncontribution purposes remain inactive',()=>{
 for(const patch of [{version:'1'},{purpose:'draft'},{purpose:'key-update'}])assert.equal(validateEnvelopeShape({...fixture(),...patch},principal),false);
});
test('audience includes author and unique profile-valid principals',()=>{
 for(const audience of [[],['bob'],['alice','alice'],['alice','unknown']])assert.equal(validateEnvelopeShape({...fixture(),audience},principal),false);
});
test('audience order is semantic set order, not an authorization change',()=>{
 const e=fixture(),c=context(e);c.audience.reverse();assert.equal(checkEnvelopeContext(e,c,principal),'context-matched');
});
test('unverified data cannot supply protection context',()=>{
 const e=fixture();assert.equal(checkEnvelopeContext(e,null,principal),'unverified');
 assert.equal(checkEnvelopeContext(e,{...context(e),status:'claimed'},principal),'unverified');
});
test('author conversation purpose version and audience substitution fail',()=>{
 const e=fixture();for(const patch of [{principal:'bob'},{conversation:'4'.repeat(32)},{purpose:'draft'},{version:'1'},{audience:['alice']},{audience:['alice','bob','mallory']},{audience:['alice','alice']}])assert.equal(checkEnvelopeContext(e,{...context(e),...patch},principal),'context-mismatch');
});
test('v1 disclosure union is exact ordered and omits hidden recipient metadata',()=>{
 const e={...fixture(),version:'1',disclosures:[]};
 const plain={kind:'plaintext-email'},host=service=>({kind:'provider-hosted',service,model:'bearer'});
 for(const disclosures of [[],[plain],[host('https://a.example')],[plain,host('https://a.example'),host('https://b.example')]])assert.equal(validateEnvelopeShape({...e,disclosures},principal),true);
 for(const disclosures of [null,{},[plain,plain],[host('https://a.example'),plain],[host('https://b.example'),host('https://a.example')],[host('https://a.example'),host('https://a.example')],[{...plain,count:1}],[{...host('https://a.example'),recipient:'bob'}],[host('https://A.example')],[{kind:'provider-hosted',service:'https://a.example',model:'password'}]])assert.equal(validateEnvelopeShape({...e,disclosures},principal),false);
 assert.equal(validateEnvelopeShape({...fixture(),disclosures:[]},principal),false);
});
test('hosted observation shape is version1 only and does not itself grant effects',()=>{
 const operation={kind:'hosted-holder-observation',text:'A holder replied.',target:{principal:'alice',conversation:'2'.repeat(32),event:'4'.repeat(32)},service:'https://a.example',attribution:'grant-holder'};
 assert.equal(validateEnvelopeShape({...fixture(),operation},principal),false);
 assert.equal(validateEnvelopeShape({...fixture(),version:'1',disclosures:[],operation},principal),true);
});
