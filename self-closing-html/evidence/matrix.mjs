import fs from 'node:fs';
import createDOMPurify from 'dompurify';
import {JSDOM} from 'jsdom';
import sanitizeHtml from 'sanitize-html';
import {run, contextElement} from './model.mjs';
const {window}=new JSDOM(''); const purify=createDOMPurify(window);
const seeds=[
 '<style/><img src onerror="probe()"><style></style>',
 '<textarea/><img src onerror="probe()"><textarea></textarea>',
 '<x-box/><svg></x-box><style><img src onerror="probe()"></style></svg>',
 '<div/><svg></div><style><img src onerror="probe()"></style></svg>',
 '<math><mtext><x-box/><mglyph><style><img src onerror="probe()"></style></mglyph></mtext></math>',
 '<noscript><style></noscript><img src=x onerror="probe()">',
 '<div/><span>following</span>', '<x-box a="b"/><span>following</span>',
 '<table><x-box/><tr><td>text</td></tr></table>',
 '<svg><foreignObject><x-box/><style><img src onerror="probe()"></style></foreignObject></svg>'
];
const parts=['<div/>','</div>','<x-box/>','</x-box>','<svg>','</svg>','<math>','</math>','<mtext>','</mtext>','<mglyph>','</mglyph>','<style>','</style>','<textarea>','</textarea>','<table>','</table>','<form>','</form>','<template>','</template>','<noscript>','</noscript>','<img src onerror="probe()">'];
let state=0x51e1f00d; const rand=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
for(let i=0;i<3000;i++){let s='';for(let j=0,n=3+rand()%12;j<n;j++)s+=parts[rand()%parts.length];seeds.push(s);}
const configs=[
 ['DOMPurify-default',s=>purify.sanitize(s)],
 ['DOMPurify-custom-elements',s=>purify.sanitize(s,{CUSTOM_ELEMENT_HANDLING:{tagNameCheck:/^x-/,attributeNameCheck:/^data-/,allowCustomizedBuiltInElements:false}})],
 ['sanitize-html-default',s=>sanitizeHtml(s)],
 ['sanitize-html-styles-custom',s=>sanitizeHtml(s,{allowedTags:[...sanitizeHtml.defaults.allowedTags,'style','x-box','svg','math','mtext','mglyph','foreignObject','img'],allowedAttributes:{'*':['class','id','data-probe'],img:['src'],a:['href']},allowVulnerableTags:true})]
];
const contexts=['div','table','template','select'];
const report={seed:'0x51e1f00d',versions:{parse5:'8.0.1',dompurify:purify.version,jsdom:'30.1.3',sanitizeHtml:'2.18.1'},inputs:seeds.length,contexts,profiles:['all','text-excluded','text-and-foreign-excluded'],pipelines:[],counterexamples:[],activationExamples:[],caveats:['parse5 prototype is not a browser implementation or an independent security proof','signals are event-handler attributes, script elements, and dangerous URL schemes; this is not a complete XSS oracle','no handlers or scripts execute','parse5 8 has legacy select behavior that differs from current Chromium','DOMPurify/jsdom and sanitize-html configurations are specific tested versions; no universal library claim']};
for(const [name,sanitize] of configs){const stats={name,inputs:0,comparisons:0,newSignals:0,activations:0,baselineSignals:0,treeChanges:0,errors:0};
 for(const input of seeds){let clean;try{clean=sanitize(input);}catch{stats.errors++;continue;}stats.inputs++;
  for(const context of contexts){const base=run(clean,'legacy',contextElement(context));const baseCount=base.signals.handlers.length+base.signals.scripts.length+base.signals.urls.length;stats.baselineSignals+=baseCount;
   for(const profile of report.profiles){const next=run(clean,profile,contextElement(context));const nextCount=next.signals.handlers.length+next.signals.scripts.length+next.signals.urls.length;stats.comparisons++;stats.activations+=next.activations.length;
    if(base.serialized!==next.serialized) stats.treeChanges++;
    if(next.activations.length && report.activationExamples.length<20)report.activationExamples.push({name,input,clean,context,profile,baseline:base.signals,next:next.signals,activations:next.activations});
    if(nextCount>baseCount){stats.newSignals++;if(report.counterexamples.length<20)report.counterexamples.push({name,input,clean,context,profile,baseline:base.signals,next:next.signals,activations:next.activations});}
   }
  }
 }
 report.pipelines.push(stats);
}
fs.writeFileSync('matrix-results.json',JSON.stringify(report,null,2)+'\n'); console.log(JSON.stringify(report.pipelines,null,2)); window.close();
