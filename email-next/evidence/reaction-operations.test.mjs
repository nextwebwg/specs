import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import {createHash} from 'node:crypto';
import {validateReactionOperation} from './reaction-operations.mjs';
const principal=s=>s==='alice';const target={principal:'alice',conversation:'1'.repeat(32),event:'2'.repeat(32)};
test('pinned Unicode derivation and source/license hashes agree',()=>{
 const base=new URL('./unicode-17/',import.meta.url),source=readFileSync(new URL('emoji-test.txt',base));
 const manifest=JSON.parse(readFileSync(new URL('sources.json',base)));
 assert.equal(createHash('sha256').update(source).digest('hex'),manifest.sha256);
 assert.equal(createHash('sha256').update(readFileSync(new URL('LICENSE.txt',base))).digest('hex'),manifest.licenseSha256);
 const derived=source.toString().split('\n').filter(l=>l.split(';')[1]?.trim().startsWith('fully-qualified '))
  .map(l=>String.fromCodePoint(...l.split(';')[0].trim().split(/\s+/).map(c=>parseInt(c,16))));
 assert.deepEqual(JSON.parse(readFileSync(new URL('fully-qualified.json',base))),derived);assert.equal(derived.length,manifest.count);
});
test('exact emoji membership preserves variation, ZWJ, modifiers and flags',()=>{
 for(const emoji of ['👍','👍🏽','☹️','👩‍💻','🇨🇦'])assert.equal(validateReactionOperation({kind:'reaction',target,emoji},principal),true,emoji);
 for(const emoji of ['','ok','👍 👍','☹','🏽','\ud800','👍\n'])assert.equal(validateReactionOperation({kind:'reaction',target,emoji},principal),false,emoji);
 assert.equal(validateReactionOperation({kind:'reaction',target,emoji:'👍',text:'extra'},principal),false);
});
test('withdrawal has exact distinct nonempty references and its own kind',()=>{
 const r={...target,event:'3'.repeat(32)};
 assert.equal(validateReactionOperation({kind:'reaction-withdraw',target,reactions:[r]},principal),true);
 for(const reactions of [[],[r,r],[{...r,principal:'other'}]])assert.equal(validateReactionOperation({kind:'reaction-withdraw',target,reactions},principal),false);
 assert.equal(validateReactionOperation({kind:'withdraw',target,reactions:[r]},principal),false);
});
