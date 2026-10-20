import test from 'node:test';
import assert from 'node:assert/strict';
import {validateNavigationUrl as check} from './navigation-url.mjs';
test('absolute HTTP and HTTPS normalize through URL parsing',()=>{
 assert.deepEqual(check('HTTPS://Example.test:443/a/../b?q=x#f'),{state:'destination',href:'https://example.test/b?q=x#f',origin:'https://example.test'});
 assert.equal(check('http://example.test/').state,'destination');
});
test('relative and executable schemes remain rejected',()=>{
 for(const url of ['/path','//example.test','javascript:alert(1)','data:text/html,x','mailto:a@example.test','https:example.test','https:///example.test'])assert.equal(check(url).state,'rejected');
});
test('credentials including empty userinfo are rejected',()=>{
 for(const url of ['https://a:b@example.test','https://a@example.test','https://@example.test','https://:x@example.test'])assert.equal(check(url).state,'rejected');
});
test('input controls backslashes and malformed hosts cannot normalize into accepted links',()=>{
 for(const url of [' https://example.test','https://exam\nple.test','https://example.test/\u007f','https://example.test\\@evil.test','https://[broken','https://example.test:99999','https://example.test/\ud800'])assert.equal(check(url).state,'rejected');
});
test('unicode host and encoded path remain destination data',()=>{
 assert.equal(check('https://bücher.example/a%20b').href,'https://xn--bcher-kva.example/a%20b');
 assert.equal(check('https://example.test/a%40b').state,'destination');
});
test('destination disclosure uses the parsed host, including numeric aliases',()=>{
 assert.deepEqual(check('https://exam%70le.test/'),{
  state:'destination',href:'https://example.test/',origin:'https://example.test'});
 assert.deepEqual(check('https://0x7f.1/'),{
  state:'destination',href:'https://127.0.0.1/',origin:'https://127.0.0.1'});
});
test('path normalization cannot consume query or fragment data',()=>{
 assert.equal(check('https://example.test/a/%2e%2E/b?x=/../#../').href,
  'https://example.test/b?x=/../#../');
});
test('browser-compatible parsing is distinct from strict domain and URI validation',()=>{
 assert.equal(check('https://xn--8i7caa/').href,'https://xn--8i7caa/');
 assert.equal(check('https://example.test/%s').href,'https://example.test/%s');
});
test('IPv6 destinations preserve brackets and reject malformed embedded addresses',()=>{
 assert.deepEqual(check('https://[2001:0DB8:0:0:1:0:0:1]:443/'),{
  state:'destination',href:'https://[2001:db8::1:0:0:1]/',origin:'https://[2001:db8::1:0:0:1]'});
 assert.equal(check('https://[::ffff:192.0.2.1]/').href,'https://[::ffff:c000:201]/');
 for(const value of ['https://[1::2::3]/','https://[::ffff:192.00.2.1]/',
  'https://[::ffff:192.0.2.256]/','https://[1:2:3:4:5:6:7:8:9]/']) {
  assert.equal(check(value).state,'rejected',value);
 }
});
test('UTF-8 URL serialization preserves plus and existing percent data',()=>{
 assert.equal(check("https://example.test/é?x=é+'&y=%252F#é").href,
  'https://example.test/%C3%A9?x=%C3%A9+%27&y=%252F#%C3%A9');
});
