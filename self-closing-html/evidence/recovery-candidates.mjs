import fs from 'node:fs';
import {html} from 'parse5';
import {ExperimentalParser, run} from './model.mjs';
const NS=html.NS.HTML;
const STATEFUL=new Set('html head body frameset frame table caption colgroup col tbody tfoot thead tr td th template select option optgroup form button a b big code em font i nobr s small strike strong tt u p pre listing'.split(' '));
class RecoveryParser extends ExperimentalParser {
  constructor(options={}) {super({...options,profile:'text-and-foreign-excluded'});this.recovery=options.recovery;this.closedNames=new Set();this.repairs=[];}
  onStartTag(token) {
    const count=this.activations.length;
    super.onStartTag(this.recovery.endsWith('-stateful-excluded') && STATEFUL.has(token.tagName) ? {...token,selfClosing:false} : token);
    if(this.activations.length>count) this.closedNames.add(token.tagName);
  }
  onEndTag(token) {
    const stack=this.openElements.items.slice(0,this.openElements.stackTop+1);
    const hasForeignMatch=stack.slice().reverse().some(n=>n.namespaceURI!==NS&&n.tagName?.toLowerCase()===token.tagName);
    const shouldRepair=this.currentNotInHTML&&!hasForeignMatch&&(this.recovery.startsWith('all-stray') || this.closedNames.has(token.tagName));
    if(shouldRepair){
      this.repairs.push({name:token.tagName,offset:token.location?.startOffset});
      while(this.openElements.stackTop>0&&this.openElements.current.namespaceURI!==NS)this.openElements.pop();
      this._resetInsertionMode();
    }
    super.onEndTag(token);
    this.closedNames.delete(token.tagName);
  }
}
function parse(source,recovery){const p=new RecoveryParser({sourceCodeLocationInfo:true,recovery});p.tokenizer.write(source,true);return {tree:p.document,activations:p.activations,repairs:p.repairs};}
function markers(tree){let out=[];function visit(n,inert=false){inert ||= n.tagName==='template'&&n.namespaceURI===NS;if(n.tagName==='img'&&n.attrs?.some(a=>a.name==='data-probe'))out.push({offset:n.sourceCodeLocation?.startOffset,ns:n.namespaceURI,inert});for(const c of n.childNodes??[])visit(c,inert);if(n.content)visit(n.content,true);}visit(tree);return out;}
export {parse as parseRecovery};
if (process.argv[1]?.endsWith('recovery-candidates.mjs')) {
const seeds=[
 '<style/><img data-probe><style></style>',
 '<textarea/><img data-probe><textarea></textarea>',
 '<math><mtext><x-box/><mglyph><style><img data-probe></style></mglyph></mtext></math>',
 '<x-box/><svg></x-box><style><img data-probe></style></svg>',
 '<div/><svg></div><style><img data-probe></style></svg>'
];
const parts=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<p/>','</p>','<b/>','</b>','<form/>','</form>','<table/>','</table>','<select/>','</select>','<template/>','</template>','<svg>','</svg>','<math>','</math>','<mtext>','</mtext>','<mglyph>','</mglyph>','<style>','</style>','<textarea>','</textarea>','<noscript>','</noscript>','<foreignObject>','</foreignObject>','<img data-probe>'];
let state=0x52455041;function rand(){state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;}
for(let i=0;i<100000;i++){let source='';for(let j=0,n=3+rand()%22;j<n;j++)source+=parts[rand()%parts.length];seeds.push(source);}
const report={seed:'0x52455041',inputs:seeds.length,results:[],caveats:['Incomplete experimental parser, not native engine proof','Counts added or differently classified markers in either direction, not proven new hazards','Raw input witnesses are not sanitizer bypasses']};
for(const recovery of (process.argv.includes('--base') ? ['closed-name','all-stray'] : ['closed-name-stateful-excluded','all-stray-stateful-excluded'])){
 const stats={recovery,witnesses:[],changedMarkerInterpretations:0,repairs:0,seeds:[]};
 for(let i=0;i<seeds.length;i++){
 const source='<!doctype html><body>'+seeds[i];const legacy=markers(run(source).tree);const next=parse(source,recovery);const result=markers(next.tree);stats.repairs+=next.repairs.length;
 const old=new Set(legacy.map(x=>JSON.stringify(x)));const added=result.filter(x=>!old.has(JSON.stringify(x)));
 if(i<5)stats.seeds.push({input:seeds[i],legacy,next:result,repairs:next.repairs});
 if(added.length){stats.changedMarkerInterpretations++;if(stats.witnesses.length<15)stats.witnesses.push({input:seeds[i],legacy,next:result,repairs:next.repairs,activations:next.activations});}
 }
 report.results.push(stats);
}
fs.writeFileSync(process.argv.includes('--base') ? 'recovery-results.json' : 'recovery-stateful-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));

}
