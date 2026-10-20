import {test} from 'node:test';
import assert from 'node:assert/strict';
import {interpretPlainText as parse} from './flowed-text.mjs';
const flowed=(s,extra={})=>parse(s,{format:'flowed',...extra});
test('missing and unknown format preserve fixed lines',()=>{
 for(const options of [{},{format:'unknown',delsp:'yes'}]) assert.deepEqual(parse('a \r\nb',options).map(x=>x.text),['a ','b']);
});
test('DelSp no joins while retaining separating space',()=>{
 assert.equal(flowed('hello \r\nworld')[0].text,'hello world');
});
test('DelSp yes removes exactly one flow-marker space',()=>{
 assert.equal(flowed('hello  \r\nworld',{delsp:'YES'})[0].text,'hello world');
 assert.equal(flowed('日 \r\n本',{delsp:'yes'})[0].text,'日本');
});
test('unknown DelSp uses no behavior',()=>{
 assert.equal(flowed('a \nb',{delsp:'maybe'})[0].text,'a b');
});
test('quote detection precedes unstuffing',()=>{
 const a=flowed(' >literal\r\n> >nested-looking\r\n>> depth two');
 assert.deepEqual(a.map(x=>[x.depth,x.text]),[[0,'>literal'],[1,'>nested-looking'],[2,'depth two']]);
});
test('quote-depth change terminates malformed flowed paragraph',()=>{
 const a=flowed('> question \r\nanswer');
 assert.equal(a.length,2);assert.equal(a[0].depth,1);assert.equal(a[1].depth,0);
 assert.deepEqual(a[0].diagnostics,['flow-before-depth-change']);
});
test('signature separator remains independent even after flowed line',()=>{
 const a=flowed('text \r\n-- \r\nanswer');
 assert.deepEqual(a.map(x=>x.kind),['paragraph','signature','fixed']);
 assert.equal(a[1].text,'-- ');
});
test('quoted stuffed signature is recognized',()=>{
 assert.equal(flowed('>> -- ')[0].kind,'signature');
});
test('empty fixed line terminates paragraph and retains source mapping',()=>{
 const a=flowed('a \r\n\r\nb');
 assert.equal(a[0].text,'a ');assert.deepEqual(a[0].sourceLines,[0,1]);
 assert.deepEqual(a[1].sourceLines,[2]);
});
test('body end terminates flowed paragraph with diagnostic',()=>{
 assert.deepEqual(flowed('a ')[0].diagnostics,['flow-at-end']);
});
test('terminal CRLF does not fabricate a new blank paragraph',()=>{
 assert.equal(flowed('a\r\n').length,1);assert.equal(flowed('a\r\n\r\n').length,2);
 assert.deepEqual(flowed(''),[]);
});
test('space stuffing removes only one space',()=>{
 assert.equal(flowed('  indented')[0].text,' indented');
 assert.equal(flowed(' From sender')[0].text,'From sender');
});
