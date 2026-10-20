import {ClosureParser as IncrementalParser} from './parser.mjs';

// Apply parser deltas at completed token boundaries. Rebuilding the output at
// each checkpoint would erase script mutations and repeat connected callbacks.
export class LiveDOMParser {
 constructor(document,{executeScripts=true}={}) {
  this.document=document;
  this.nodes=new Map();
  this.previous=new Map();
  this.pending=[];
  this.executed=new Set();
  this.writing=false;
  this.writingIsolated=false;
  document.replaceChildren();
  this.parser=new IncrementalParser({
   onToken:()=>this.flush(),
   onScript:(node,p)=>{if(executeScripts){p.pause();this.pending.push(node);}},
  });
  this.nodes.set(this.parser.document,document);
 }
 create(node){
  const d=this.document;
  if(node.tagName){
   const element=d.createElementNS(node.namespaceURI,node.tagName);
   for(const attr of node.attrs)element.setAttributeNS(attr.namespace??null,attr.prefix?`${attr.prefix}:${attr.name}`:attr.name,attr.value);
   // Scripts are activated exactly once, at the parser's end-tag checkpoint.
   if(node.tagName==='script')element.type='application/x-next-pending';
   return element;
  }
  if(node.nodeName==='#text')return d.createTextNode(node.value);
  if(node.nodeName==='#comment')return d.createComment(node.data);
  if(node.nodeName==='#documentType')return d.implementation.createDocumentType(node.name,node.publicId,node.systemId);
  return d.createDocumentFragment();
 }
 flush(){
  if(this.parser.profileEnabled&&!this.writingIsolated){
   this.writingIsolated=true;
   for(const method of ['write','writeln','open'])Object.defineProperty(this.document,method,{
    configurable:true,value:()=>{throw new this.document.defaultView.DOMException('Legacy document writing is isolated from the Next parser','NotSupportedError');},
   });
  }
  const next=new Map();
  const visit=(node,parent=null,nextSibling=null,insertionAnchor=nextSibling)=>{
   const key=node.recognitionNode;
   let dom=this.nodes.get(key);
   if(!dom){dom=this.create(node);this.nodes.set(key,dom);}
   const old=this.previous.get(key);
   const record={parent:parent?.recognitionNode,next:nextSibling?.recognitionNode,value:node.value,attrs:node.attrs?.map(a=>({...a}))};
   next.set(key,record);
   if(parent && (!old || old.parent!==record.parent || old.next!==record.next)){
    const target=this.nodes.get(record.parent);
    const anchor=this.nodes.get(insertionAnchor?.recognitionNode);
    const placedAnchor=anchor?.parentNode===target?anchor:null;
    const requiresMove=!old || old.parent!==record.parent || (placedAnchor && dom.parentNode===target && !(dom.compareDocumentPosition(placedAnchor)&4));
    if(requiresMove)target.insertBefore(dom,placedAnchor);
   }
   if(old && node.nodeName==='#text' && old.value!==node.value){
    // Parser text coalescing adds a suffix; preserve application text edits.
    if(node.value.startsWith(old.value))dom.appendData(node.value.slice(old.value.length));
    else dom.data=node.value;
   }
   if(old && node.attrs)for(const attr of node.attrs){
    if(!old.attrs?.some(a=>a.name===attr.name&&a.namespace===attr.namespace&&a.value===attr.value))dom.setAttributeNS(attr.namespace??null,attr.prefix?`${attr.prefix}:${attr.name}`:attr.name,attr.value);
   }
   if(node.content){
    this.nodes.set(node.content.recognitionNode,dom.content);
    visit(node.content);
   }
   for(const child of node.childNodes??[])if(!this.nodes.has(child.recognitionNode))this.nodes.set(child.recognitionNode,this.create(child));
   const children=node.childNodes??[];
   for(let i=0;i<children.length;i++){
    // Foster recovery can expose several new siblings in one token. A new
    // immediate sibling is not yet an insertion anchor; use the first later
    // sibling already attached to this output parent.
    const anchor=children.slice(i+1).find(child=>this.nodes.get(child.recognitionNode)?.parentNode===dom);
    visit(children[i],node,children[i+1],anchor);
   }
  };
  visit(this.parser.output());
  for(const [key,old] of this.previous){
   // Remove only the root of a parser-removed subtree, and only from its last
   // parser-owned parent. Descendants retain ownership inside a detached tree;
   // nodes moved elsewhere by script must not be collected as parser removals.
   if(!next.has(key)&&old.parent&&next.has(old.parent)){
    const dom=this.nodes.get(key);
    if(dom?.parentNode===this.nodes.get(old.parent))dom.remove();
   }
  }
  this.previous=next;
 }
 async execute(node){
  if(this.executed.has(node))return;
  this.executed.add(node);
  const placeholder=this.nodes.get(node);
  // Template contents are inert. Only connected HTML classic scripts are in
  // this first prototype's execution contract; modules need a separate queue.
  if(!placeholder?.isConnected || node.namespaceURI!=='http://www.w3.org/1999/xhtml')return;
  const attrs=Object.fromEntries(node.attrs.map(a=>[a.name,a.value]));
  if(attrs.type && !['text/javascript','application/javascript'].includes(attrs.type))return;
  const script=this.document.createElement('script');
  for(const attr of node.attrs)script.setAttribute(attr.name,attr.value);
  script.async=false;
  script.textContent=node.childNodes.map(n=>n.value??'').join('');
  const loaded=attrs.src?new Promise((resolve,reject)=>{script.onload=resolve;script.onerror=()=>reject(new Error(`Script failed: ${attrs.src}`));}):null;
  this.nodes.set(node,script);
  placeholder.replaceWith(script);
  if(loaded)await loaded;
 }
 async write(chunk,last=false){
  if(this.writing)throw new this.document.defaultView.DOMException('Concurrent or reentrant input is unsupported','InvalidStateError');
  this.writing=true;
  try{
   this.parser.write(chunk,last);
   while(this.pending.length){
    await this.execute(this.pending.shift());
    // A microtask checkpoint before resuming is observable by custom elements
    // and MutationObservers. This scheduling is explicit prototype behavior.
    await Promise.resolve();
    this.parser.resume();
   }
  }finally{this.writing=false;}
 }
}
