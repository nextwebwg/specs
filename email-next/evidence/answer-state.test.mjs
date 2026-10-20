import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deriveAnswers } from './answer-state.mjs';
const ref = (id, author='alice') => ({author,id});
const key = (id, author='alice') => JSON.stringify([author,id]);
const answer = (id, targets=[], extra={}) => ({id,author:'alice',kind:'answer',form:'f',revision:'r1',targets:targets.map(x=>typeof x==='string'?ref(x):x),fixtureIdentity:id,...extra});
function* permutations(xs) {
  if (!xs.length) { yield []; return; }
  for (let i=0;i<xs.length;i++) for (const rest of permutations(xs.filter((_,j)=>i!==j))) yield [xs[i],...rest];
}
const cases = [
 ['duplicate delivery',[answer('a'),answer('a')],['a']],
 ['concurrent answers',[answer('a'),answer('b')],['a','b']],
 ['explicit resolution',[answer('a'),answer('b'),answer('c',['a','b'])],['c']],
 ['pending replacement',[answer('a'),answer('c',['missing'])],['a']],
 ['withdraw predecessor only',[answer('a'),answer('b',['a']),answer('w',['a'],{kind:'withdraw'})],['b']],
 ['withdraw current answer',[answer('a'),answer('b',['a']),answer('w',['b'],{kind:'withdraw'})],[]],
 ['self reference',[answer('a',['a'])],[]],
 ['cycle',[answer('a',['b']),answer('b',['a'])],[]],
 ['cross revision replacement',[answer('a'),answer('b',['a'],{revision:'r2'})],['a']],
 ['identity conflict',[answer('a'),answer('a',[],{fixtureIdentity:'different'}),answer('b',['a'])],[]],
 ['cross author replacement',[answer('a'),answer('b',[ref('a')],{author:'bob'})],['a']],
];
for (const [name, records, expected] of cases) test(name+' converges under every delivery order',()=>{
 const result=deriveAnswers(records);
 assert.deepEqual(result.current,expected.map(x=>key(x)).sort());
 for(const order of permutations(records)) assert.deepEqual(deriveAnswers(order),result);
});
test('another author cannot reserve the same event identity',()=>{
 assert.deepEqual(deriveAnswers([answer('a'),answer('a',[],{author:'bob'})]).current,[key('a'),key('a','bob')]);
});
test('pending replacement becomes valid when its predecessor arrives',()=>{
 const b=answer('b',['a']);
 assert.equal(deriveAnswers([b]).status[key('b')],'pending');
 assert.deepEqual(deriveAnswers([b,answer('a')]).current,[key('b')]);
});
test('conflicting predecessor removes dependent attribution without choosing a winner',()=>{
 const records=[answer('a'),answer('b',['a'])];
 assert.deepEqual(deriveAnswers(records).current,[key('b')]);
 const result=deriveAnswers([...records,answer('a',[],{fixtureIdentity:'conflict'})]);
 assert.equal(result.status[key('a')],'conflict');
 assert.equal(result.status[key('b')],'invalid');
 assert.deepEqual(result.current,[]);
});
