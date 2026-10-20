import {test} from 'node:test';
import assert from 'node:assert/strict';
import {PackageAllocator} from './keypackage-allocation.mjs';
const pool=packages=>new PackageAllocator(packages,{device:'target-device',profile:'fixture-mls'});
const request={principal:'sender',device:'target-device',profile:'fixture-mls',request:'one'};
test('same request returns its allocation without consuming another package',()=>{
 const a=pool(['p1','p2']);
 assert.deepEqual(a.allocate(request),a.allocate(request));
 assert.equal(a.allocate({...request,request:'two'}).packageReference,'p2');
});
test('distinct request scopes cannot share an allocated package',()=>{
 const a=pool(['p1']);a.allocate(request);
 for(const field of ['principal','request'])assert.equal(a.allocate({...request,[field]:'different'}).state,'depleted');
});
test('allocated package cannot be republished after abandonment',()=>{
 const a=pool(['p1']);a.allocate(request);
 assert.throws(()=>a.publish('p1'),TypeError);
});
test('depleted retry is stable; fresh authorized request can use replenished pool',()=>{
 const a=pool([]);assert.equal(a.allocate(request).state,'depleted');a.publish('p2');
 assert.equal(a.allocate(request).state,'depleted');assert.equal(a.allocate({...request,request:'two'}).packageReference,'p2');
});
test('caller mutation cannot alter stored allocation result',()=>{
 const a=pool(['p1']);const result=a.allocate(request);result.packageReference='forged';
 assert.equal(a.allocate(request).packageReference,'p1');
});

test('a pool never returns a package for another target or profile',()=>{
 const a=pool(['p1']);
 for(const field of ['device','profile'])assert.throws(()=>a.allocate({...request,[field]:'other'}),TypeError);
 assert.equal(a.allocate(request).packageReference,'p1');
});
