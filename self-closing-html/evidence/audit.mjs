import {Parser,html} from 'parse5';
import {VOID,contextElement,run} from './model.mjs';
export class LegacyAuditor extends Parser {
 constructor(options={},...args){super(options,...args);this.activations=[];}
 onStartTag(token){
  if(token.selfClosing&&!VOID.has(token.tagName)&&!['svg','math'].includes(token.tagName)&&!this.shouldProcessStartTagTokenInForeignContent(token))this.activations.push({tag:token.tagName,offset:token.location?.startOffset});
  super.onStartTag(token);
 }
}
export function audit(source,context=null,scriptingEnabled=true){
 const options={sourceCodeLocationInfo:true,scriptingEnabled};
 const p=context?LegacyAuditor.getFragmentParser(context,options):new LegacyAuditor(options);
 p.tokenizer.write(source,true);return p.activations;
}
