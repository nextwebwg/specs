// Shared recognition policy for static and incremental evidence models.
import {Parser,html} from 'parse5';
import {VOID,TEXT} from './model.mjs';
const NS=html.NS.HTML;
export const PROTECTED_ATTRIBUTES=new Set(['inert','hidden','disabled','popover']);
export const STATEFUL=new Set('html head body frameset frame table caption colgroup col tbody tfoot thead tr td th template select option optgroup form fieldset button details dialog datalist audio video canvas object applet a b big code em font i nobr s small strike strong tt u p pre listing'.split(' '));
export class RecognitionParser extends Parser {
 constructor(options={},...args){super({...options,sourceCodeLocationInfo:true},...args);this.shorthandOffsets=new Set();this.profileEnabled=options.profileEnabled??true;}
 onStartTag(token){
  const foreign=(this.fragmentContext && this.fragmentContext.namespaceURI!==NS) || this.openElements.items.slice(0,this.openElements.stackTop+1).some(n=>n.namespaceURI!==NS);
  const protectedAttribute=token.attrs.some(a=>PROTECTED_ATTRIBUTES.has(a.name));
  const formattingScope=this.activeFormattingElements.entries.some(e=>e.element);
  const specialFormattingContext=formattingScope && html.SPECIAL_ELEMENTS[NS].has(token.tagID);
  if(this.profileEnabled&&token.selfClosing&&!specialFormattingContext&&!protectedAttribute&&!VOID.has(token.tagName)&&!TEXT.has(token.tagName)&&!STATEFUL.has(token.tagName)&&!['svg','math'].includes(token.tagName)&&!foreign&&!this.shouldProcessStartTagTokenInForeignContent(token))this.shorthandOffsets.add(token.location.startOffset);
  super.onStartTag(token);
 }
}
