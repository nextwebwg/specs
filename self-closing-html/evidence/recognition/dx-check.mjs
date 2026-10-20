import fs from 'node:fs';
import {parse, serialize} from 'parse5';
import {parsePlacement as parseRecognition} from './placement.mjs';
import {parseRecognition as parsePrevious} from './parser.mjs';
// Structured authoring examples complement deliberately malformed security cases.
let seed = 0x44584332;
const random = () => { seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; return seed >>> 0; };
const pick = values => values[random() % values.length];
const inline = ['span','small','b','strong','em','i','u','s','code','mark','sub','sup','abbr','cite','q','x-chip'];
const blocks = ['div','section','article','aside','nav','blockquote','figure'];
const element = (tag, children = [], empty = false) => ({tag, children, empty});
function phrasing(depth) {
  if (depth === 0 || random() % 3 === 0) return 'text';
  const empty = random() % 3 === 0;
  return element(pick(inline), empty ? [] : Array.from({length:1 + random() % 3}, () => phrasing(depth - 1)), empty);
}
function flow(depth) {
  if (depth === 0) return phrasing(2);
  switch (random() % 4) {
    case 0: {
      const empty = random() % 3 === 0;
      return element(pick(blocks), empty ? [] : Array.from({length:1 + random() % 3}, () => flow(depth - 1)), empty);
    }
    case 1: return element(pick(['p','h1','h2']), Array.from({length:1 + random() % 3}, () => phrasing(depth)));
    case 2: return element(pick(['ul','ol']), Array.from({length:1 + random() % 3}, () => {
      const empty = random() % 3 === 0;
      return element('li', empty ? [] : [flow(depth - 1)], empty);
    }));
    default: return phrasing(depth);
  }
}
function print(node, expand = false) {
  if (typeof node === 'string') return node;
  if (node.empty) return expand ? `<${node.tag}></${node.tag}>` : `<${node.tag}/>`;
  return `<${node.tag}>${node.children.map(child => print(child, expand)).join('')}</${node.tag}>`;
}
const report = {seed:'0x44584332',generated:4000,generatedMismatches:0,previousProjectionMismatches:0,examples:[],improvements:[],tableCases:1000,tableMismatches:0,targeted:[],scope:'Structured flow/phrasing/list authoring cases; a DX check, not universal HTML conformance.'};
function compare(name, source, expanded) {
  const current = parseRecognition('<!doctype html><body>' + source);
  const actual = current.html;
  const previous = parsePrevious('<!doctype html><body>' + source).html;
  const expected = serialize(parse('<!doctype html><body>' + expanded));
  return {name,source,expanded,matches:actual===expected,previousMatches:previous===expected,placement:current.parser.lastDecision.placement,...(actual===expected?{}:{actual,expected})};
}
for (let i = 0; i < report.generated; i++) {
  const tree = element('div', Array.from({length:1 + random() % 4}, () => flow(3)));
  const result = compare(`generated ${i}`, print(tree), print(tree,true));
  if (!result.previousMatches) { report.previousProjectionMismatches++; if(result.matches&&report.improvements.length<4)report.improvements.push(result); }
  if (!result.matches) { report.generatedMismatches++; if (report.examples.length < 10) report.examples.push(result); }
}
for (let i = 0; i < report.tableCases; i++) {
  const rows = Array.from({length:1 + random()%4}, () => {
    const empty = random()%4 === 0;
    return element('tr',empty?[]:Array.from({length:1+random()%4},()=>{
      const cellEmpty=random()%3===0;
      return element('td',cellEmpty?[]:[phrasing(2)],cellEmpty);
    }),empty);
  });
  const empty=random()%5===0;
  const tree=element('div',[element('table',empty?[]:[element('tbody',rows)],empty),element('p',['tail'])]);
  const result=compare(`table ${i}`,print(tree),print(tree,true));
  if(!result.matches){report.tableMismatches++;if(report.examples.length<10)report.examples.push(result);}
}
for (const args of [
  ['formatting siblings','<small/><em>tail</em>','<small></small><em>tail</em>'],
  ['formatting in a paragraph','<p><strong><em/><span>tail</span></strong></p>','<p><strong><em></em><span>tail</span></strong></p>'],
  ['repeated custom hosts','<x-card/><x-card/><p>tail</p>','<x-card></x-card><x-card></x-card><p>tail</p>'],
  ['list items','<ul><li/><li>two</li></ul>','<ul><li></li><li>two</li></ul>'],
  ['adjacent forms','<form/><form><input></form>','<form></form><form><input></form>'],
  ['pre newline','<pre/>\n<span>tail</span>','<pre></pre>\n<span>tail</span>'],
  ['listing newline','<listing/>\n<span>tail</span>','<listing></listing>\n<span>tail</span>'],
  ['invalid block within formatting','<b><div/><span>tail</span></b>','<b><div></div><span>tail</span></b>'],
]) report.targeted.push(compare(...args));
for(const item of report.targeted){
  item.expectedHandling=item.name==='adjacent forms'?'ordinary form boundary':'empty-pair placement';
  item.passes=item.matches||(item.name==='adjacent forms'&&parseRecognition(item.source).html===serialize(parse(item.source)));
}
fs.writeFileSync(new URL('./dx-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({generated:report.generated,generatedMismatches:report.generatedMismatches,previousProjectionMismatches:report.previousProjectionMismatches,tableCases:report.tableCases,tableMismatches:report.tableMismatches,examples:report.examples.slice(0,1),targeted:report.targeted.map(({name,matches})=>({name,matches}))},null,2));

if(report.generatedMismatches||report.tableMismatches||report.targeted.some(item=>!item.passes))process.exitCode=1;
