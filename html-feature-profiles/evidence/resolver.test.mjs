import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveAPIProfile,resolveNavigationProfile,parseSelector} from './resolver.mjs';
const fixture=()=>({
 manifest:{revision:'fixture-new',next:['self-closing','flexible-nesting'],registry:{
  'self-closing':{revision:'s1'},'flexible-nesting':{revision:'f1'},
  'dependent-feature':{revision:'d1',requires:['self-closing']},
 }},
 supported:{'self-closing':['s1'],'flexible-nesting':['f1'],'dependent-feature':['d1']},
 caller:{requested:'next',features:['self-closing'],featureRevisions:{'self-closing':'s1'},preset:'next',revision:'fixture-old',source:'doctype',status:'active'},
});
const fails=(fn,name)=>assert.throws(fn,error=>error.name===name);

test('omission and explicit undefined retain ordinary parsing without consulting caller or preset',()=>{
 const poison={get caller(){throw Error('ambient caller read')},get manifest(){throw Error('ambient preset read')}};
 assert.deepEqual(resolveAPIProfile(undefined,poison).features,[]);
 assert.equal(resolveAPIProfile(undefined,poison).status,'legacy');
});
test('named parsing works from a legacy caller and ignores its doctype/preset',()=>{
 const c=fixture();c.caller={features:[],featureRevisions:{},revision:null,status:'legacy'};
 assert.deepEqual(resolveAPIProfile('self-closing',c).features,['self-closing']);
 assert.deepEqual(c.caller.features,[]);
});
test('inherit copies the earlier resolved snapshot while next resolves the current preset',()=>{
 const c=fixture(), inherited=resolveAPIProfile('inherit',c), next=resolveAPIProfile('next',c);
 assert.deepEqual(inherited.features,['self-closing']);assert.equal(inherited.revision,'fixture-old');
 assert.deepEqual(next.features,['flexible-nesting','self-closing']);assert.equal(next.revision,'fixture-new');
 assert.equal(inherited.source,'api');
});
test('inherit from ordinary HTML stays ordinary and never enables next implicitly',()=>{
 const c=fixture();c.caller={features:[],featureRevisions:{},revision:null,preset:null,status:'legacy'};
 assert.equal(resolveAPIProfile('inherit',c).status,'legacy');
 assert.deepEqual(resolveAPIProfile('inherit',c).features,[]);
});
test('resolved records are immutable independent snapshots',()=>{
 const c=fixture(), result=resolveAPIProfile('inherit',c);
 c.caller.features.push('flexible-nesting');c.caller.featureRevisions['self-closing']='changed';c.manifest.next=[];
 assert.deepEqual(result.features,['self-closing']);assert.equal(result.featureRevisions['self-closing'],'s1');
 fails(()=>result.features.push('other'),'TypeError');fails(()=>{result.featureRevisions['self-closing']='changed'},'TypeError');
 assert.equal(resolveAPIProfile('next',fixture()).revision,'fixture-new');
});
test('selection order and surrounding whitespace do not give feature priority',()=>{
 for(const selector of ['self-closing, flexible-nesting','flexible-nesting,self-closing',' \tself-closing\r\n,\fflexible-nesting '])
  assert.deepEqual(resolveAPIProfile(selector,fixture()).features,['flexible-nesting','self-closing']);
});
for(const selector of ['',',','self-closing,',',self-closing','self-closing,self-closing','Self-Closing','next,self-closing','inherit,next','self closing','self-closing;mode=1'])
 test(`reject malformed API selector ${JSON.stringify(selector)}`,()=>fails(()=>resolveAPIProfile(selector,fixture()),'SyntaxError'));
for(const selector of ['future-feature',null])
 test(`reject unsupported selector ${JSON.stringify(selector)} without downgrade`,()=>fails(()=>resolveAPIProfile(selector,fixture()),'NotSupportedError'));
test('normal string conversion applies, symbols fail conversion',()=>{
 assert.deepEqual(resolveAPIProfile({toString:()=> 'self-closing'},fixture()).features,['self-closing']);
 fails(()=>resolveAPIProfile(Symbol('self-closing'),fixture()),'TypeError');
});
test('dependencies are explicit and unsupported dependencies fail the whole request',()=>{
 assert.deepEqual(resolveAPIProfile('dependent-feature',fixture()).features,['dependent-feature','self-closing']);
 const c=fixture();delete c.supported['self-closing'];fails(()=>resolveAPIProfile('dependent-feature',c),'NotSupportedError');
});
test('individually supported features do not imply support for their composition',()=>{
 const c=fixture();c.compatible=features=>features.length<2;
 assert.deepEqual(resolveAPIProfile('self-closing',c).features,['self-closing']);
 fails(()=>resolveAPIProfile('next',c),'NotSupportedError');
 fails(()=>resolveAPIProfile('self-closing,flexible-nesting',c),'NotSupportedError');
});
test('unsupported inherited revisions are rejected rather than re-resolved',()=>{
 const c=fixture();c.caller.featureRevisions['self-closing']='old-unsupported';
 fails(()=>resolveAPIProfile('inherit',c),'NotSupportedError');
});
test('response header wins over a conflicting doctype and is the recorded source',()=>{
 const r=resolveNavigationProfile({header:'self-closing',doctype:'flexible-nesting'},fixture());
 assert.deepEqual(r.features,['self-closing']);assert.equal(r.source,'header');
});
test('invalid or unsupported headers never fall back to a valid doctype',()=>{
 for(const [header,error] of [['','SyntaxError'],['next,self-closing','SyntaxError'],['future-feature','NotSupportedError']])
  fails(()=>resolveNavigationProfile({header,doctype:'self-closing'},fixture()),error);
});
test('doctype only applies in the absence of the header',()=>{
 assert.equal(resolveNavigationProfile({doctype:'self-closing'},fixture()).source,'doctype');
 assert.equal(resolveNavigationProfile({},fixture()).status,'legacy');
});
for(const header of ['"self-closing"','(self-closing)','self-closing;v=1','?1','1','self-closing\n','self-closing,','self-closing,,flexible-nesting'])
 test(`reject non-token or malformed structured header ${JSON.stringify(header)}`,()=>fails(()=>resolveNavigationProfile({header},fixture()),'SyntaxError'));
test('API-only inheritance cannot be requested through header or doctype',()=>{
 for(const source of ['header','doctype'])fails(()=>resolveNavigationProfile({[source]:'inherit'},fixture()),'NotSupportedError');
});
test('all two-feature permutations normalize to one result without modifying inputs',()=>{
 for(const a of ['self-closing','flexible-nesting'])for(const b of ['self-closing','flexible-nesting']){
  if(a===b)continue;const c=fixture(), before=structuredClone(c);
  assert.deepEqual(resolveAPIProfile(`${a}, ${b}`,c).features,['flexible-nesting','self-closing']);assert.deepEqual(c,before);
 }
});
test('DOMString conversion runs once and the record matches the selected request',()=>{
 let calls=0;const input={toString(){return ++calls===1?'self-closing':'next'}};
 const result=resolveAPIProfile(input,fixture());assert.equal(calls,1);assert.equal(result.requested,'self-closing');
 assert.deepEqual(result.features,['self-closing']);
});
