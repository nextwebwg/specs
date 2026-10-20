import createDOMPurify from 'dompurify';
import {parse as parseLegacy} from 'parse5';
import {parseClosure} from './parser.mjs';
import {resolveAPIProfile} from '../../../html-feature-profiles/evidence/resolver.mjs';

// Inert reference pipeline: parse with the selected grammar, construct nodes in
// a document without a browsing context, sanitize those same nodes in place.
// Never serialize the untrusted candidate tree and parse it with another grammar.
// This demonstrates the composition; it does not implement the native Sanitizer API.
export function createDOMSafeParser(window,{callerProfile=null}={}){
 const purify=createDOMPurify(window);
 const legacyProfile=resolveAPIProfile(undefined,{});
 const context={caller:callerProfile??legacyProfile,supported:{'self-closing':['1']},manifest:{revision:'closure-reference-1',next:['self-closing'],registry:{'self-closing':{revision:'1'}}}};
 function parse(source,{profile}={}){
  const selected=resolveAPIProfile(profile,context);
  if(typeof source==='symbol')throw new TypeError('A symbol cannot convert to DOMString');
  source=String(source);
  const ast=selected.features.includes('self-closing')?parseClosure(source).tree:parseLegacy(source);
  const document=window.document.implementation.createHTMLDocument('');
  while(document.firstChild)document.firstChild.remove();
  function create(node){
   if(node.nodeName==='#text')return document.createTextNode(node.value);
   if(node.nodeName==='#comment')return document.createComment(node.data);
   if(node.nodeName==='#documentType')return document.implementation.createDocumentType(node.name,node.publicId,node.systemId);
   let element;
   try{element=document.createElementNS(node.namespaceURI,node.tagName);}catch{
    // HTML error recovery can recognize names rejected by DOM construction
    // APIs. Unwrap those names as nodes, never reparse their child text.
    const fragment=document.createDocumentFragment();
    for(const child of node.childNodes??[])fragment.append(create(child));
    return fragment;
   }
   for(const attr of node.attrs??[]){
    try{
     if(attr.namespace)element.setAttributeNS(attr.namespace,attr.prefix?`${attr.prefix}:${attr.name}`:attr.name,attr.value);
     else element.setAttribute(attr.name,attr.value);
    }catch{ /* Invalid DOM attribute names are omitted, not interpreted as markup. */ }
   }
   const parent=node.content?element.content:element;
   for(const child of (node.content??node).childNodes??[])parent.append(create(child));
   return element;
  }
  for(const child of ast.childNodes??[])document.append(create(child));
  const root=document.documentElement;
  purify.sanitize(root,{IN_PLACE:true,WHOLE_DOCUMENT:true});
  return {document,root,profile:selected};
 }
 return {parse,version:purify.version};
}
