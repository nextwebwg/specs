import {LiveDOMParser as PreviousLiveDOMParser} from '../live-dom.mjs';
import {PlacementParser} from './placement.mjs';

// Reuse the existing mutation-preserving DOM delta reconciler, with the new
// eligibility rule. This adapter is evidence, not a native HTML implementation.
export class LiveDOMParser extends PreviousLiveDOMParser {
  constructor(document, {executeScripts = true, ParserClass = PlacementParser} = {}) {
    super(document, {executeScripts});
    this.inertDocument = document.implementation.createHTMLDocument('');
    this.scriptTypes = new WeakMap();
    this.parser = new ParserClass({
      onCheckpoint: () => this.flush(),
      onScript: (node, parser) => {
        if (executeScripts) { parser.pause(); this.pending.push(node); }
      },
    });
    this.parser.profileEnabled = true;
    this.nodes = new Map([[this.parser.document, document]]);
  }
  create(node) {
    // Attribute setup happens without a browsing context. Insertion adopts
    // active output nodes into the destination; template contents stay inert.
    // Creating img[src] in the live document first could start a request before
    // the node is placed in its template, defeating the intended boundary.
    const document = this.inertDocument;
    if (node.tagName) {
      const element = document.createElementNS(node.namespaceURI, node.tagName);
      for (const attr of node.attrs) element.setAttributeNS(attr.namespace ?? null,
        attr.prefix ? `${attr.prefix}:${attr.name}` : attr.name, attr.value);
      if (node.tagName === 'script') {
        this.scriptTypes.set(element, element.getAttribute('type'));
        element.type = 'application/x-next-pending';
      }
      return element;
    }
    if (node.nodeName === '#text') return document.createTextNode(node.value);
    if (node.nodeName === '#comment') return document.createComment(node.data);
    if (node.nodeName === '#documentType') return document.implementation.createDocumentType(node.name, node.publicId, node.systemId);
    return document.createDocumentFragment();
  }
  async execute(node) {
    if (this.executed.has(node)) return;
    this.executed.add(node);
    const placeholder = this.nodes.get(node);
    if (!placeholder?.isConnected || node.namespaceURI !== 'http://www.w3.org/1999/xhtml') return;
    // Read live attributes and text. A script/app can have changed the pending
    // element between streamed chunks; frozen source attributes are not an
    // authority to override a later switch to a non-executable script type.
    const attrs = Object.fromEntries([...placeholder.attributes].map(attr=>[attr.name,attr.value]));
    if (attrs.type === 'application/x-next-pending') {
      const declared = this.scriptTypes.get(placeholder);
      if (declared === null) delete attrs.type;
      else attrs.type = declared;
    }
    if (attrs.type && !['text/javascript','application/javascript'].includes(attrs.type)) return;
    const script = this.document.createElement('script');
    for (const [name,value] of Object.entries(attrs)) script.setAttribute(name,value);
    script.async = false;
    script.textContent = placeholder.textContent;
    const loaded = attrs.src ? new Promise((resolve,reject)=>{
      script.onload = resolve;
      script.onerror = ()=>reject(new Error('External script failed'));
    }) : null;
    this.nodes.set(node,script);
    placeholder.replaceWith(script);
    if (loaded) await loaded;
  }

}
