// Constructive model: preserve legacy recognition/recovery; change only output containment.
import fs from 'node:fs';
import {html,serialize} from 'parse5';
import {VOID,TEXT,contextElement} from './model.mjs';
const NS=html.NS.HTML;
export {STATEFUL} from './recognition-parser.mjs';
import {STATEFUL,RecognitionParser,PROTECTED_ATTRIBUTES} from './recognition-parser.mjs';
function signature(tree, identities) {
 const result = [];
 function visit(node, inTemplate = false, barriers = []) {
  if (!identities.has(node)) identities.set(node, identities.size);
  const id = identities.get(node);
  inTemplate ||= node.tagName === 'template' && node.namespaceURI === NS;
  const protectedNode = node.tagName && (
   node.namespaceURI !== NS || TEXT.has(node.tagName) || STATEFUL.has(node.tagName) ||
   node.attrs?.some(attr => PROTECTED_ATTRIBUTES.has(attr.name))
  );
  if (protectedNode) barriers = [...barriers, id];
  result.push({id, type:node.nodeName, ns:node.namespaceURI, attrs:node.attrs,
   text:node.value ?? node.data, inTemplate, barriers});
  for (const child of node.childNodes ?? []) visit(child, inTemplate, barriers);
  if (node.content) visit(node.content, true, barriers);
 }
 visit(tree);
 return JSON.stringify(result);
}
function project(parent,offsets,activations){
 const list=parent.childNodes??[];const output=[];
 for(const node of list){
  project(node,offsets,activations);if(node.content)project(node.content,offsets,activations);
  output.push(node);node.parentNode=parent;
  if(node.namespaceURI===NS&&offsets.has(node.sourceCodeLocation?.startTag?.startOffset)){
   const children=node.childNodes;node.childNodes=[];activations.push({tag:node.tagName,offset:node.sourceCodeLocation.startTag.startOffset});
   for(const child of children){child.parentNode=parent;output.push(child);}
  }
 }
 parent.childNodes=output;
}
export function parseProjected(source,context=null,scriptingEnabled=true){
 const options={sourceCodeLocationInfo:true,scriptingEnabled};const p=context?RecognitionParser.getFragmentParser(context,options):new RecognitionParser(options);p.tokenizer.write(source,true);const tree=context?p.getFragment():p.document;
 const identities=new Map();const before=signature(tree,identities);const activations=[];project(tree,p.shorthandOffsets,activations);
 return {tree,html:serialize(tree),sameRecognition:before===signature(tree,identities),activations};
}
if (process.argv[1]?.endsWith('projection-candidate.mjs')) {
const examples=[
 '<div/><span>Following</span>',
 '<x-box/><x-box/>text',
 '<style/><img data-probe><style></style>',
 '<textarea/><img data-probe><textarea></textarea>',
 '<math><mtext><x-box/><mglyph><style><img data-probe></style></mglyph></mtext></math>',
 '<x-box/><svg></x-box><style><img data-probe></style></svg>',
 '<div/><svg></div><style><img data-probe></style></svg>',
 '<h1/><svg></h2><style><img data-probe></style></svg>',
 '<div><x-box/></div><svg></x-box><title><style></title><img data-probe></style>',
 '<div inert/><img data-probe>',
 '<div popover/><button>control</button>',
 '<template/><img data-probe>',
 '<select/><img data-probe>'
];
const parts=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<p/>','</p>','<b/>','</b>','<form/>','</form>','<table/>','</table>','<select/>','</select>','<template/>','</template>','<svg>','</svg>','<math>','</math>','<mtext>','</mtext>','<mglyph>','</mglyph>','<style>','</style>','<textarea>','</textarea>','<noscript>','</noscript>','<foreignObject>','</foreignObject>','<img data-probe>','<script>','</script>','<!--','-->','<title>','</title>','<iframe>','</iframe>','<plaintext>','<xmp>','<div inert/>','<div popover/>','<details/>','</details>','<dialog/>','</dialog>','<datalist/>','</datalist>','<audio/>','</audio>','<video/>','</video>','<canvas/>','</canvas>','<object/>','</object>'];
let state=0x50524f4a;function rand(){state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;}
const report={seed:'0x50524f4a',inputs:100000,contexts:['document','div','table','template'],scripting:[true,false],comparisons:0,recognitionChanges:0,activations:0,examples:examples.map(source=>({source,...parseProjected('<!doctype html><body>'+source),tree:undefined})),failures:[],limits:['Static containment projection, not a production streaming algorithm','Recognition equality includes preorder node identities, namespace, attributes, text, template inertness and designated containment barriers; not all browser execution behavior','Excludes stateful names; does not implement declarative shadow roots, custom element execution or script scheduling']};
for(let i=0;i<report.inputs;i++){let source='';for(let j=0,n=1+rand()%20;j<n;j++)source+=parts[rand()%parts.length];for(const name of report.contexts)for(const scripting of report.scripting){const context=name==='document'?null:contextElement(name);const r=parseProjected(source,context,scripting);report.comparisons++;report.activations+=r.activations.length;if(!r.sameRecognition){report.recognitionChanges++;if(report.failures.length<10)report.failures.push({source,name,scripting,html:r.html});}}}
fs.writeFileSync('projection-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,examples:report.examples,failures:report.failures},null,2));if(report.recognitionChanges)process.exitCode=1;

}
