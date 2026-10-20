import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseSizeAdvertisement,sizeDeclaration,stuffData,exceedsAdvertisedLimit} from './smtp-size.mjs';
test('zero and omitted limit remain distinct',()=>{
 assert.deepEqual(parseSizeAdvertisement(undefined),{kind:'unknown'});
 assert.deepEqual(parseSizeAdvertisement('0'),{kind:'unbounded-fixed-limit'});
});
test('large decimal limits retain exact integer precision',()=>{
 assert.equal(parseSizeAdvertisement('9007199254740993').maximum,9007199254740993n);
 for(const bad of ['', '-1','1.5','1e6',' 10','10 '])assert.throws(()=>parseSizeAdvertisement(bad));
});
test('SIZE excludes stuffing and terminator but includes content CRLF',()=>{
 const message=Buffer.from('Subject: test\r\n\r\n.\r\n..text\r\n');
 const wire=stuffData(message);
 assert.equal(sizeDeclaration(message),BigInt(message.length));
 assert.equal(wire.length,message.length+2+3);
 assert.ok(wire.includes(Buffer.from('\r\n..\r\n...text\r\n')));
});
test('exact boundary passes while one byte above fails preflight',()=>{
 const message=Buffer.from('X: y\r\n\r\nz\r\n');
 assert.equal(exceedsAdvertisedLimit(message,String(message.length)),false);
 assert.equal(exceedsAdvertisedLimit(message,String(message.length-1)),true);
 assert.equal(exceedsAdvertisedLimit(message,undefined),false);
});
test('final encoded Q&A fixture size includes all MIME alternatives and headers',()=>{
 for(const name of ['question.eml','answer.eml']) {
  const message=readFileSync(new URL('../examples/'+name,import.meta.url));
  assert.equal(sizeDeclaration(message),BigInt(message.byteLength));
  assert.equal(exceedsAdvertisedLimit(message,'1'),true);
  assert.ok(stuffData(message).subarray(-3).equals(Buffer.from('.\r\n')));
 }
});
test('noncanonical fixture line endings are rejected rather than silently rewritten',()=>{
 for(const text of ['a\nb\n','a\rb\r','a'])assert.throws(()=>sizeDeclaration(Buffer.from(text)));
});
