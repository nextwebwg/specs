import {LiveDOMParser as PreviousLiveDOMParser} from '../live-dom.mjs';
import {RecognitionPreservingParser} from './parser.mjs';

// Reuse the existing mutation-preserving DOM delta reconciler, with the new
// eligibility rule. This adapter is evidence, not a native HTML implementation.
export class LiveDOMParser extends PreviousLiveDOMParser {
  constructor(document, {executeScripts = true} = {}) {
    super(document, {executeScripts});
    this.inertDocument = document.implementation.createHTMLDocument('');
    this.parser = new RecognitionPreservingParser({
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
      if (node.tagName === 'script') element.type = 'application/x-next-pending';
      return element;
    }
    if (node.nodeName === '#text') return document.createTextNode(node.value);
    if (node.nodeName === '#comment') return document.createComment(node.data);
    if (node.nodeName === '#documentType') return document.implementation.createDocumentType(node.name, node.publicId, node.systemId);
    return document.createDocumentFragment();
  }
}
