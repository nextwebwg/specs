import {test} from 'node:test';
import assert from 'node:assert/strict';
import {isObjectId,newObjectId,isEventReference} from './event-identifiers.mjs';
const id='0123456789abcdef0123456789abcdef';
test('exact lowercase ASCII encoding is required',()=>{
 assert.ok(isObjectId(id));
 for(const bad of [id.toUpperCase(),' '+id,id+'\n',id.slice(1),id+'0','0'.repeat(32),123,null,{},'０'.repeat(32)]) assert.equal(isObjectId(bad),false);
});
test('generator produces valid identifiers without semantic fields',()=>{
 for(let i=0;i<32;i++)assert.ok(isObjectId(newObjectId()));
 // This finite check is not an entropy assessment or a proof of uniqueness.
});
test('reference needs exact shape and separately accepted principal',()=>{
 const ref={principal:'fixture-principal',event:id,conversation:id};
 const accepts=p=>p==='fixture-principal';
 assert.ok(isEventReference(ref,accepts));
 assert.equal(isEventReference(ref,()=>false),false);
 for(const bad of [null,[],{...ref,extra:true},{...ref,event:null},{event:id,conversation:id},{...ref,principal:null}]) assert.equal(isEventReference(bad,accepts),false);
});
