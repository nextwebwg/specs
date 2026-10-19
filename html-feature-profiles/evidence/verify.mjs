import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const dir=new URL('.',import.meta.url);
const run=spawnSync(process.execPath,['--test','--test-reporter=tap',new URL('resolver.test.mjs',dir).pathname],{encoding:'utf8'});
if(run.status!==0){process.stdout.write(run.stdout);process.stderr.write(run.stderr);process.exit(run.status??1)}
const count=name=>Number(run.stdout.match(new RegExp(`^# ${name} (\\d+)$`,'m'))?.[1]);
const digests=Object.fromEntries(['resolver.mjs','resolver.test.mjs','verify.mjs','browser-baseline.mjs'].map(file=>[file,createHash('sha256').update(readFileSync(new URL(file,dir))).digest('hex')]));
const browser=JSON.parse(readFileSync(new URL('browser-baseline-results.json',dir),'utf8'));
assert.equal(browser.sourceSHA256,digests['browser-baseline.mjs']);
const available=browser.reports.flatMap(r=>r.cases.filter(c=>c.available).map(c=>({...c,engine:r.engine})));
for(const c of available){
 assert.equal(c.baselineParent,'DIV');assert.equal(c.sourceScriptExecuted,false);
 if(c.method==='parseHTML')for(const key of ['scriptElements','eventAttributes','javascriptURLs'])assert.equal(c[key],0);
}
const report={runtime:process.version,recordedAt:new Date().toISOString(),sourceDigests:digests,
 contractModel:{tests:count('tests'),passed:count('pass'),failed:count('fail'),scope:'Executable selector/precedence/snapshot model and authored contract vectors; not native HTML parsing, sanitization, layout, or full Structured Fields conformance.'},
 browserBaseline:{engines:browser.reports.map(r=>({engine:r.engine,version:r.version})),availableMethods:available.length,profileOptionReadByAny:available.some(c=>c.profileGetterReads!==0),hasResolvedRecord:available.some(c=>c.hasResolvedProfileRecord),scope:'Unmodified browser observations. Success with an unknown option does not establish support.'},
 correctedCounterexample:{case:'Stateful DOMString conversion',before:{conversions:2,expected:1},after:'Convert once before selector validation and record construction; retained regression passes.'},
 remaining:['Native profile dictionary integration and WebIDL error ordering','Safe/unsafe sanitizer composition under each selected grammar','Native header selection, preset manifests, and inherited/cross-realm records','HTTP intermediary/cache behavior and full Structured Fields integration','Flexible-nesting recognition, composed layout, accessibility, and combined-feature security']};
assert.equal(report.contractModel.failed,0);assert.ok(report.contractModel.tests>0);
writeFileSync(new URL('verification-results.json',dir),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
