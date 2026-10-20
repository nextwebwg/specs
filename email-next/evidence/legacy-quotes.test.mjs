import {test} from 'node:test';
import assert from 'node:assert/strict';
import {reconstructQuotes} from './legacy-quotes.mjs';
const parent={id:'p',text:'Which day?\nWhich place?'};
function check(text,parents=[parent]) {
 const blocks=reconstructQuotes(text,parents);
 assert.deepEqual(blocks.flatMap(x=>x.lines),text.split(/\r\n|\n|\r/),'every original line survives in order');
 return blocks;
}
test('inline answers remain visible beside individually matched quotations',()=>{
 const b=check('> Which day?\nThursday\n> Which place?\nLibrary');
 assert.deepEqual(b.map(x=>x.kind),['repeated-quote','visible','repeated-quote','visible']);
 assert.deepEqual(b.filter(x=>x.kind==='visible').flatMap(x=>x.lines),['Thursday','Library']);
});
test('edited quotation stays visible in full',()=>{
 assert.equal(check('> Which day?\n> Actually Friday?')[0].kind,'visible');
});
test('unmarked copied text is not hidden as a quote',()=>{
 assert.equal(check('Which day?')[0].kind,'visible');
});
test('same text in two possible parents is ambiguous',()=>{
 assert.equal(check('> Which day?',[parent,{...parent,id:'other'}])[0].kind,'visible');
});
test('repeated match inside one parent is ambiguous',()=>{
 assert.equal(check('> same',[{id:'p',text:'same\nsame'}])[0].kind,'visible');
});
test('nested quotations and localized markers remain visible',()=>{
 assert.ok(check('>> Which day?\n| Which place?').every(x=>x.kind==='visible'));
});
test('signature-like answers and whitespace changes are retained',()=>{
 assert.ok(check('-- \nThursday\n> Which day? ').every(x=>x.kind==='visible'));
});
test('empty quotes do not match empty lines automatically',()=>{
 assert.equal(check('> ',[{id:'p',text:''}])[0].kind,'visible');
});
test('CRLF and final newline preserve all source lines',()=>{
 check('> Which day?\r\nThursday\r\n');
});
test('localized attribution labels remain visible and do not define quote boundaries',()=>{
 for(const label of ['Am 20. Oktober schrieb Alice:','2026年10月20日、Alice さんは書きました:','في 20 أكتوبر، كتب Alice:']){
  const result=check(label+'\n> Which day?\nTuesday\n> Which place?\nLibrary');
  assert.deepEqual(result.map(x=>x.kind),['visible','repeated-quote','visible','repeated-quote','visible']);assert.equal(result[0].lines[0],label);
  assert.ok(check(label+'\nWhich day?').every(x=>x.kind==='visible'));
 }
});
