import {html} from 'parse5';
import {RecognitionParser} from './recognition-parser.mjs';

// Recognition nodes are never reparented by projection. Snapshots retain their
// identities so a live-DOM consumer can apply parser deltas without undoing
// application mutations. This is a prototype, not a native navigation parser.
export class IncrementalParser extends RecognitionParser {
 constructor({onScript=null,onToken=null,requireOptIn=false,...options}={}) {
  super({...options,profileEnabled:!requireOptIn});
  this.requireOptIn=requireOptIn;
  this.initialMode=this.insertionMode;
  this.onScriptCheckpoint=onScript;
  this.onTokenCheckpoint=onToken;
  this.depth=0;
  this.pendingScript=null;
  this.scriptHandler=script=>{this.pendingScript=script;};
 }
 write(chunk,last=false){this.tokenizer.write(chunk,last);}
 pause(){this.tokenizer.pause();}
 resume(){this.tokenizer.resume();}
 output(){
  const clone=(node,parent=null)=>{
   const result={...node,parentNode:parent,recognitionNode:node,childNodes:[]};
   if(node.content)result.content=clone(node.content);
   for(const child of node.childNodes??[]) {
    const item=clone(child,result);
    result.childNodes.push(item);
    if(child.namespaceURI===html.NS.HTML && this.shorthandOffsets.has(child.sourceCodeLocation?.startTag?.startOffset)) {
     const following=item.childNodes;item.childNodes=[];
     for(const sibling of following){sibling.parentNode=result;result.childNodes.push(sibling);}
    }
   }
   return result;
  };
  return clone(this.document);
 }
 checkpoint(method,token){
  if(this.requireOptIn && method==='onDoctype' && this.insertionMode===this.initialMode){
   this.profileEnabled=token.name==='html'&&token.publicId==='next'&&token.systemId===null&&!token.forceQuirks;
  }
  this.depth++;
  try{RecognitionParser.prototype[method].call(this,token);}
  finally{this.depth--;}
  if(this.depth)return;
  this.onTokenCheckpoint?.(token,this);
  if(this.pendingScript){
   const script=this.pendingScript;this.pendingScript=null;
   this.onScriptCheckpoint?.(script,this);
  }
 }
}
// Parser recovery sometimes calls another token handler. Only the outer token
// boundary is observable, after insertion-mode and open-element updates finish.
for(const method of ['onStartTag','onEndTag','onCharacter','onWhitespaceCharacter','onNullCharacter','onComment','onDoctype','onEof']) {
 Object.defineProperty(IncrementalParser.prototype,method,{value:function(token){this.checkpoint(method,token);}});
}
