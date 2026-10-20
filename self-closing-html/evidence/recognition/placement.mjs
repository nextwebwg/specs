import {Parser, Token, TokenizerMode, defaultTreeAdapter, html, serialize} from 'parse5';
import {RecognitionPreservingParser} from './parser.mjs';

const OWNERS = new Set(['html','head','body','frameset','template','form','select']);
function recorder(adapter, clock, births) {
  return {...adapter, createElement(...args) {
    const node = adapter.createElement(...args);
    births.set(node, clock.offset);
    return node;
  }};
}
function dataKey(node, births) {
  const start = node.sourceCodeLocation?.startTag?.startOffset;
  return JSON.stringify([node.tagName,node.namespaceURI,
    start === undefined ? ['implied',births.get(node)] : ['source',start],
    (node.attrs ?? []).map(a=>[a.name,a.namespace??null,a.prefix??null,a.value])]);
}
function content(node) {
  return JSON.stringify([node.nodeName,node.namespaceURI,node.attrs?.map(a=>[a.name,a.namespace??null,a.value]),
    node.value,node.data,(node.childNodes??[]).map(content),node.content?content(node.content):null]);
}
class PlacementBuilder extends Parser {
  constructor({canClose,...options} = {}, ...args) { super(options,...args); this.canClose = canClose; }
  onStartTag(token) {
    super.onStartTag(token);
    if (!this.canClose(token)) return;
    super.onEndTag({...token,type:Token.TokenType.END_TAG,attrs:[],selfClosing:false});
  }
}

// The source reader decides WHAT exists. This second builder chooses WHERE it
// goes using ordinary HTML closing/placement rules. It receives tokens, never
// strings; a CHARACTER token containing '<img>' cannot become a start tag.
export class PlacementParser extends RecognitionPreservingParser {
  constructor({onCheckpoint,...options} = {}, ...args) {
    const adapter = options.treeAdapter ?? defaultTreeAdapter;
    const clock = {offset:-1};
    const births = new WeakMap();
    super({...options,treeAdapter:recorder(adapter,clock,births),onCheckpoint:(_t,p)=>p.afterRecognition()},...args);
    this.userCheckpoint = onCheckpoint;
    this.clock = clock;
    this.births = births;
    this.planBirths = new WeakMap();
    this.rawOwners = new WeakSet();
    this.lastDecision = null;
    this.textIdentities = new Map();
    const plannerOptions = {...options,onParseError:undefined,sourceCodeLocationInfo:true,
      treeAdapter:recorder(adapter,clock,this.planBirths),canClose:token=>this.canClose(token)};
    this.planner = args[1] ? PlacementBuilder.getFragmentParser(args[1],plannerOptions) : new PlacementBuilder(plannerOptions);
  }
  canClose(token) {
    return this.marked.has(token.location?.startOffset) && !this.textStarts.has(token.location?.startOffset) && !OWNERS.has(token.tagName);
  }
  eligible(node) {
    const offset = node.sourceCodeLocation?.startTag?.startOffset;
    return !this.sourcePaths?.get(node)?.some(owner=>this.rawOwners.has(owner)||['script','style'].includes(owner.tagName)) &&
      node.namespaceURI === html.NS.HTML && this.marked.has(offset) && !this.textStarts.has(offset) && !OWNERS.has(node.tagName) && !node.content;
  }
  checkpoint(method, token) {
    if (!this.depth) {
      this.sourceMethod = method;
      this.sourceToken = structuredClone(token);
      this.clock.offset = token.location?.startOffset ?? this.clock.offset;
    }
    return super.checkpoint(method,token);
  }
  afterRecognition() {
    if (this.sourceMethod === 'onStartTag' && this.tokenizer.state !== TokenizerMode.DATA) {
      const node = this.openElements.current;
      if (node?.sourceCodeLocation?.startTag?.startOffset === this.sourceToken.location?.startOffset) this.rawOwners.add(node);
    }
    this.planner[this.sourceMethod](this.sourceToken);
    this.userCheckpoint?.(this.sourceToken,this);
  }
  getFragment() {
    const root = super.getFragment();
    this.planFragment = this.planner.getFragment();
    return root;
  }
  boundary(node) {
    return Boolean(node.content || (node.namespaceURI && node.namespaceURI !== html.NS.HTML) || this.rawOwners.has(node) || ['script','style'].includes(node.tagName));
  }
  stableText(root) {
    const walk = node => {
      if (node.nodeName === '#text' && node.sourceCodeLocation?.startOffset !== undefined) {
        const offset = node.sourceCodeLocation.startOffset;
        if (!this.textIdentities.has(offset)) this.textIdentities.set(offset,{});
        node.recognitionNode = this.textIdentities.get(offset);
      }
      for (const child of node.childNodes??[]) walk(child);
      if (node.content) walk(node.content);
    };
    walk(root);
    return root;
  }
  output(root = this.document) {
    const plan = root === this.document ? this.planner.document : this.planFragment;
    const available = new Map();
    const doctypes = [];
    const paths = new Map();
    const collect = (node,path=[]) => {
      paths.set(node,path);
      if (node.nodeName === '#documentType') doctypes.push(node);
      if (node.tagName) {
        const key = dataKey(node,this.births);
        if (!available.has(key)) available.set(key,[]);
        available.get(key).push(node);
      }
      const inside = this.boundary(node) ? [...path,node] : path;
      for (const child of node.childNodes??[]) collect(child,inside);
      if (node.content) collect(node.content,inside);
    };
    collect(root);
    this.sourcePaths = paths;
    const used = new Set();
    const build = (node,parentNode=null,path=[],forced=null) => {
      let source = forced;
      if (node.tagName && !source) {
        source = available.get(dataKey(node,this.planBirths))?.find(candidate=>!used.has(candidate));
        if (!source) throw new Error(`unrecognized element ${node.tagName}`);
        used.add(source);
      }
      if (!source && node.nodeName === '#documentType') {
        source = doctypes.find(n=>n.name===node.name&&n.publicId===node.publicId&&n.systemId===node.systemId);
        if (!source) throw new Error('unrecognized document type');
      }
      if (source) {
        const expected = paths.get(source);
        if (!expected || expected.length !== path.length || expected.some((n,i)=>n!==path[i])) throw new Error(`protected context ${node.tagName??node.nodeName}`);
        if ((this.rawOwners.has(source)||['script','style'].includes(source.tagName)) && content(source)!==content(node)) throw new Error(`changed text owner ${source.tagName}`);
      }
      const basis = source ?? node;
      const out = {...basis,attrs:basis.attrs?.map(a=>({...a})),parentNode,recognitionNode:basis,childNodes:[]};
      const inside = source && this.boundary(source) ? [...path,source] : path;
      for (const child of node.childNodes??[]) out.childNodes.push(build(child,out,inside));
      if (node.content) out.content = build(node.content,null,inside,source.content);
      return out;
    };
    const certify = output => {
      if (output.recognitionNode !== root) throw new Error('changed source root');
      const seen = new Set();
      const walk = (node,path=[]) => {
        const origin = node.recognitionNode;
        if (node.tagName || node.nodeName === '#documentType' || node.nodeName === '#document-fragment') {
          if (!paths.has(origin) || seen.has(origin)) throw new Error('unrecognized or repeated source node');
          seen.add(origin);
          if (node.tagName !== origin.tagName || node.namespaceURI !== origin.namespaceURI || JSON.stringify(node.attrs) !== JSON.stringify(origin.attrs)) throw new Error('changed source payload');
          const expected = paths.get(origin);
          if (expected.length !== path.length || expected.some((n,i)=>n!==path[i])) throw new Error('changed protected context');
          if ((this.rawOwners.has(origin)||['script','style'].includes(origin.tagName)) && content(node)!==content(origin)) throw new Error('changed owned code/text');
          if (node.content && node.content.recognitionNode !== origin.content) throw new Error('changed inactive content owner');
        }
        const inside = paths.has(origin) && this.boundary(origin) ? [...path,origin] : path;
        for (const child of node.childNodes??[]) walk(child,inside);
        if (node.content) walk(node.content,inside);
      };
      walk(output);
      return output;
    };
    let rejected;
    try {
      const result = certify(build(plan,null,[],root));
      this.lastDecision = {placement:'normal-html',reason:null};
      return this.stableText(result);
    } catch (error) { rejected = error.message; }
    try {
      const result = certify(super.output(root));
      this.lastDecision = {placement:'recognition-recovery',reason:rejected};
      return this.stableText(result);
    } catch (error) {
      // The recognition snapshot is the final authority. Even a defect in the
      // projected-recovery implementation must not authorize different code.
      const copy = (node,parentNode=null) => {
        const out = {...node,attrs:node.attrs?.map(a=>({...a})),parentNode,recognitionNode:node,childNodes:[]};
        for (const child of node.childNodes??[]) out.childNodes.push(copy(child,out));
        if (node.content) out.content = copy(node.content);
        return out;
      };
      const result = certify(copy(root));
      this.lastDecision = {placement:'source-recovery',reason:`${rejected}; ${error.message}`};
      return this.stableText(result);
    }
  }
}
export function parsePlacement(source, options) {
  const parser = new PlacementParser(options);
  parser.write(source,true);
  const tree = parser.output();
  return {parser,tree,html:serialize(tree)};
}
