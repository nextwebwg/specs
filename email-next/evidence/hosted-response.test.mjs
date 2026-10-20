import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const context=vm.createContext({TextDecoder});vm.runInContext(readFileSync(new URL('./hosted-response.js',import.meta.url),'utf8'),context);
const parse=context.parseHostedJSON;
assert.equal(parse('{"a":"ok","array":["x"]}').a,'ok');
for(const bad of ['{"a":"x","\\u0061":"y"}','{"a":null}','{"a":true}','{"a":1}','{"a":"\\ud800"}','["x",]','{}{}','['.repeat(34)+'"x"'+']'.repeat(34)])assert.throws(()=>parse(bad));
assert.equal(parse('{"__proto__":"text"}').__proto__,'text');
console.log('Hosted strict JSON checks passed');
