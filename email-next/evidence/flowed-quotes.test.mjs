import {test} from 'node:test';
import assert from 'node:assert/strict';
import {reconstructFlowedQuotes as reconstruct} from './flowed-quotes.mjs';
const parent = {id:'parent', text:'Which day works?\r\nWhich place?', format:'fixed'};
function check(text, parents=[parent], options={}) {
  const result=reconstruct({text,format:'flowed',...options},parents);
  const lines=text===''?[]:text.split(/\r\n|\n|\r/);
  if(/(?:\r\n|\n|\r)$/.test(text))lines.pop();
  assert.deepEqual(result.flatMap(b=>b.sourceLines),lines.map((_,i)=>i));
  return result;
}
test('wrapped quotations retain inline answers and original line mappings',()=>{
 const b=check('> Which day \r\n> works?\r\nThursday\r\n> Which place?\r\nLibrary');
 assert.deepEqual(b.map(x=>x.kind),['repeated-quote','visible','repeated-quote','visible']);
 assert.deepEqual(b[0].sourceLines,[0,1]);
 assert.deepEqual(b[0].source,{message:'parent',sourceLines:[0]});
});
test('each message applies its own DelSp semantics',()=>{
 const b=check('> 日本',[{id:'jp',text:'日 \r\n本',format:'flowed',delsp:'yes'}]);
 assert.equal(b[0].kind,'repeated-quote');
 assert.deepEqual(b[0].source.sourceLines,[0,1]);
 assert.equal(check('> 日本',[{id:'jp',text:'日 \r\n本',format:'flowed',delsp:'no'}])[0].kind,'visible');
});
test('stuffed literal quote marker cannot become quote metadata',()=>{
 assert.equal(check(' >Which day works?')[0].kind,'visible');
});
test('malformed flow at a depth transition stays visible',()=>{
 assert.equal(check('> Which day works? \nanswer',[{id:'p',text:'Which day works? '}])[0].kind,'visible');
});
test('malformed parent flow cannot justify collapse',()=>{
 assert.equal(check('> same ',[{id:'p',text:'same ',format:'flowed'}])[0].kind,'visible');
});
test('multiple sources and repeated occurrences preserve ambiguity',()=>{
 for(const parents of [[parent,{...parent,id:'other'}],[{id:'p',text:'Which place?\nWhich place?'}]])
  assert.equal(check('> Which place?',parents)[0].kind,'visible');
});
test('edited paragraph preserves the whole quoted block',()=>{
 assert.equal(check('> Which day works?\n> Changed place?')[0].kind,'visible');
});
test('nested and signature-like quotations remain visible',()=>{
 assert.ok(check('>> Which place?\n> -- ',[{id:'p',text:'Which place?\n-- '}]).every(b=>b.kind==='visible'));
});
test('empty input and final newline retain exact line coverage',()=>{
 assert.deepEqual(check(''),[]); check('> Which place?\r\n');check('answer\r\n\r\n');
});
test('fixed input cannot accidentally enter the flowed reconstruction path',()=>{
 assert.throws(()=>reconstruct({text:'> quoted',format:'fixed'},[]),TypeError);
});
