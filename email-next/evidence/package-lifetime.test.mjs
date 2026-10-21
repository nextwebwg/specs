import {test} from 'node:test';
import assert from 'node:assert/strict';
import {packageLifetime as check,DEFAULT_MAX_PACKAGE_LIFETIME} from './package-lifetime.mjs';
const base={notBefore:100n,notAfter:200n,earliestNow:150n,latestNow:150n};
test('validity includes exact interval boundaries',()=>{
 for(const now of [100n,150n,200n])assert.equal(check({...base,earliestNow:now,latestNow:now}),'valid');
});
test('definitely early and definitely expired are separate outcomes',()=>{
 assert.equal(check({...base,earliestNow:90n,latestNow:99n}),'not-yet-valid');
 assert.equal(check({...base,earliestNow:201n,latestNow:210n}),'expired');
});
test('uncertainty crossing either boundary never adds a grace period',()=>{
 for(const [earliestNow,latestNow] of [[99n,101n],[199n,201n],[0n,300n]])assert.equal(check({...base,earliestNow,latestNow}),'time-unresolved');
});
test('configured maximum is exact and reversed lifetime fails',()=>{
 assert.equal(check({...base,notAfter:100n+DEFAULT_MAX_PACKAGE_LIFETIME}),'valid');
 assert.equal(check({...base,notAfter:101n+DEFAULT_MAX_PACKAGE_LIFETIME}),'lifetime-policy-rejected');
 assert.equal(check({...base,notAfter:99n}),'invalid-lifetime');
});
test('uint64 validation avoids number precision and overflow',()=>{
 for(const notBefore of [-1n,1n<<64n,100,'100'])assert.equal(check({...base,notBefore}),'invalid-lifetime');
 const end=(1n<<64n)-1n;assert.equal(check({notBefore:end-100n,notAfter:end,earliestNow:end,latestNow:end}),'valid');
});
test('missing or inconsistent time information remains unresolved',()=>{
 for(const patch of [{earliestNow:undefined},{latestNow:149n},{latestNow:150}])assert.equal(check({...base,...patch}),'time-unresolved');
});

test('longer and shorter local policies do not rewrite the signed expiry',()=>{
 const longer={...base,notAfter:100n+2n*DEFAULT_MAX_PACKAGE_LIFETIME};
 assert.equal(check(longer),'lifetime-policy-rejected');
 assert.equal(check({...longer,maximumLifetime:2n*DEFAULT_MAX_PACKAGE_LIFETIME}),'valid');
 assert.equal(check({...base,maximumLifetime:99n}),'lifetime-policy-rejected');
 assert.equal(check({...longer,maximumLifetime:2n*DEFAULT_MAX_PACKAGE_LIFETIME,earliestNow:longer.notAfter+1n,latestNow:longer.notAfter+1n}),'expired');
 for(const maximumLifetime of [0n,-1n,1n<<64n,604800,'604800'])assert.throws(()=>check({...base,maximumLifetime}),RangeError);
});
