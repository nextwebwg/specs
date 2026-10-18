// Experimental model only; see README.md for limits and browser witnesses.
import { Parser, parse, parseFragment, serialize, defaultTreeAdapter, TokenizerMode, Token, html } from 'parse5';
export const VOID = new Set('area base br col embed hr img input link meta source track wbr basefont bgsound frame keygen param'.split(' '));
export const TEXT = new Set('script style title textarea xmp iframe noembed noframes noscript plaintext'.split(' '));
export class ExperimentalParser extends Parser {
  constructor(options = {}, ...args) { super(options, ...args); this.profile = options.profile ?? 'all'; this.activations = []; }
  onStartTag(token) {
    const foreignContext = this.openElements.items.slice(0, this.openElements.stackTop + 1).some(n => n.namespaceURI && n.namespaceURI !== html.NS.HTML);
    const eligible = token.selfClosing && !VOID.has(token.tagName) && !['svg','math'].includes(token.tagName) && !this.shouldProcessStartTagTokenInForeignContent(token)
      && (this.profile === 'all' || !TEXT.has(token.tagName))
      && (this.profile !== 'text-and-foreign-excluded' || !foreignContext);
    if (!eligible) { super.onStartTag(token); return; }
    this.activations.push({tag:token.tagName,offset:token.location?.startOffset,foreignContext});
    const start = {...token, selfClosing:false, ackSelfClosing:false};
    super.onStartTag(start);
    // This DATA reset approximates explicit source expansion for the witnesses.
    // It is not a complete native algorithm for text or special elements.
    this.tokenizer.state = TokenizerMode.DATA;
    super.onEndTag({...start, type:Token.TokenType.END_TAG, attrs:[], selfClosing:false});
  }
}
export function inspectTree(tree) {
 const result = {markers:[],handlers:[],scripts:[],urls:[]};
 const walk = node => {
  if (node.tagName) {
   const attrs = Object.fromEntries((node.attrs??[]).map(a=>[a.name,a.value]));
   if ('data-probe' in attrs) result.markers.push({tag:node.tagName,ns:node.namespaceURI});
   for (const [name,value] of Object.entries(attrs)) {
    if (/^on/i.test(name)) result.handlers.push({tag:node.tagName,name,value,ns:node.namespaceURI});
    if (['href','src','xlink:href','formaction','action'].includes(name) && /^\s*(javascript|vbscript|data):/i.test(value)) result.urls.push({tag:node.tagName,name,value,ns:node.namespaceURI});
   }
   if (node.tagName === 'script') result.scripts.push({ns:node.namespaceURI,attrs});
  }
  for(const child of node.childNodes??[]) walk(child);
  if(node.content) walk(node.content);
 };
 walk(tree); return result;
}
export function run(source, profile='legacy', context=null, scriptingEnabled=true) {
 const options = {sourceCodeLocationInfo:true,scriptingEnabled,profile};
 if(profile === 'legacy') {
  const tree=context?parseFragment(context,source,options):parse(source,options);
  return {tree,serialized:serialize(tree),signals:inspectTree(tree),activations:[]};
 }
 const parser=context?ExperimentalParser.getFragmentParser(context,options):new ExperimentalParser(options);
 parser.tokenizer.write(source,true);
 const tree=context?parser.getFragment():parser.document;
 return {tree,serialized:serialize(tree),signals:inspectTree(tree),activations:parser.activations};
}
export const contextElement = (name, ns=html.NS.HTML) => defaultTreeAdapter.createElement(name,ns,[]);
