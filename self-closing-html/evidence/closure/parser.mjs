import {Parser,Token,TokenizerMode,serialize} from 'parse5';

// Void HTML elements already finish at the start tag. Foreign-content starts
// keep the parser's existing self-closing handling. No authoring-name blacklist.
const VOID=new Set('area base br col embed hr img input link meta param source track wbr basefont bgsound frame keygen'.split(' '));
export class ClosureParser extends Parser {
 constructor({onScript=null,onToken=null,...options}={},...args){
  super({sourceCodeLocationInfo:true,...options},...args);
  this.profileEnabled=true;this.activations=[];this.syntheticStarts=new WeakSet();this.tokenDepth=0;
  this.pendingScripts=[];this.onScriptCheckpoint=onScript;this.onTokenCheckpoint=onToken;
  this.scriptHandler=node=>this.pendingScripts.push(node);
 }
 _startTagOutsideForeignContent(token){
  if(!token.selfClosing||VOID.has(token.tagName)||this.syntheticStarts.has(token))return super._startTagOutsideForeignContent(token);
  // Reprocessing can pass this token through several insertion modes. Strip
  // the slash once, then deliver exactly one end tag after start processing.
  const start={...token,selfClosing:false,ackSelfClosing:false};this.syntheticStarts.add(start);
  const oldState=this.tokenizer.state;
  super._startTagOutsideForeignContent(start);
  const end={...start,type:Token.TokenType.END_TAG,attrs:[],selfClosing:false};
  super.onEndTag(end);
  // A text-element start may have selected RAWTEXT/RCDATA/SCRIPT/PLAINTEXT.
  // The synthetic end is processed before another source character arrives.
  // Attribute parsing and literal tag-like text in real strings are untouched.
  if(this.tokenizer.state!==oldState)this.tokenizer.state=TokenizerMode.DATA;
  token.ackSelfClosing=true;
  this.activations.push({tag:token.tagName,offset:token.location?.startOffset});
 }
 checkpoint(method,token){
  this.tokenDepth++;
  try{Parser.prototype[method].call(this,token);}finally{this.tokenDepth--;}
  if(this.tokenDepth)return;
  this.onTokenCheckpoint?.(token,this);
  for(const script of this.pendingScripts.splice(0))this.onScriptCheckpoint?.(script,this);
 }
 write(chunk,last=false){this.tokenizer.write(chunk,last);}
 pause(){this.tokenizer.pause();}
 resume(){this.tokenizer.resume();}
 output(){
  const clone=(node,parent=null)=>{
   const out={...node,parentNode:parent,recognitionNode:node,childNodes:[]};
   if(node.content)out.content=clone(node.content);
   for(const child of node.childNodes??[])out.childNodes.push(clone(child,out));
   return out;
  };
  return clone(this.document);
 }
}
for(const method of ['onStartTag','onEndTag','onCharacter','onWhitespaceCharacter','onNullCharacter','onComment','onDoctype','onEof']){
 ClosureParser.prototype[method]=function(token){this.checkpoint(method,token);};
}
export function parseClosure(source,{context=null,...options}={}){
 const parser=context?ClosureParser.getFragmentParser(context,options):new ClosureParser(options);
 parser.write(source,true);const tree=context?parser.getFragment():parser.document;
 return {tree,html:serialize(tree),activations:parser.activations};
}
export {VOID};
