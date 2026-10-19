import {test} from 'node:test';
import assert from 'node:assert/strict';
import {serialize} from 'parse5';
import {parseProjected} from './projection-candidate.mjs';
import {IncrementalParser} from './streaming-parser.mjs';

const inputs = [
 '<div/><span>Following &amp; text</span>',
 '<x-box/><x-box/>text',
 '<div/><svg></div><style><img data-probe></style></svg>',
 '<h1/><svg></h2><style><img data-probe></style></svg>',
 '<div><x-box/></div><svg></x-box><title><style></title><img data-probe></style>',
 '<table><div/>hello<tr><td>cell</table>',
 '<b><div/>a</b>b',
 '<template><div/><span>inert</span></template>',
 '<div hidden/><img data-probe>',
 '<textarea/>\r\n&notin; <x-box/></textarea>',
 '<!-- x -->\ud83d\ude00<div data-a="a>b"/>tail',
 '<script>const x="<div/>";</script><div/>tail',
];
for (const body of inputs) test(`every two-chunk boundary: ${body}`, () => {
 const source='<!doctype html PUBLIC "next"><body>'+body;
 const expected=parseProjected(source).html;
 for(let split=0;split<=source.length;split++) {
  const parser=new IncrementalParser();
  parser.write(source.slice(0,split));
  parser.write(source.slice(split),true);
  assert.equal(serialize(parser.output()),expected,`split ${split}`);
 }
 const parser=new IncrementalParser();
 for (const character of source) parser.write(character);
 parser.write('',true);
 assert.equal(serialize(parser.output()),expected);
});

test('script checkpoint precedes following tokens and supports pause/resume',()=>{
 const observations=[];
 const parser=new IncrementalParser({onScript(script,p){
  observations.push(serialize(p.output()));
  p.pause();
 }});
 parser.write('<body><div/><script>checkpoint()</script><span>later</span>',true);
 assert.equal(observations.length,1);
 assert.match(observations[0],/<div><\/div><script>/);
 assert.doesNotMatch(observations[0],/<span>/);
 assert.doesNotMatch(serialize(parser.output()),/<span>/);
 parser.resume();
 assert.match(serialize(parser.output()),/<span>later<\/span>/);
});

test('document profile requires the exact initial opt-in',()=>{
 for(const [doctype,enabled] of [
  ['<!doctype html PUBLIC "next">',true],
  ['<!DOCTYPE HTML PUBLIC "next">',true],
  ['<!doctype html>',false],['',false],
  ['<!doctype html PUBLIC "Next">',false],
  ['<!doctype html PUBLIC "next" "system">',false],
  ['<!doctype html><!doctype html PUBLIC "next">',false],
  ['<div></div><!doctype html PUBLIC "next">',false],
 ]){
  const parser=new IncrementalParser({requireOptIn:true});
  parser.write(doctype+'<body><div/><span>tail</span>',true);
  const output=serialize(parser.output());
  assert.equal(output.includes('<div></div><span>'),enabled,doctype);
 }
});

test('popover attributes retain their native containment boundary',()=>{
 for(const value of ['', 'invalid']){
  const result=parseProjected(`<body><div popover="${value}"/><button>control</button>`);
  assert.ok(result.html.includes(`<div popover="${value}"><button>control</button></div>`));
 }
});
