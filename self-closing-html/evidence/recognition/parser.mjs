import {Parser, TokenizerMode, html, serialize} from 'parse5';

// Experimental two-tree parser. The recognition tree and all parsing state use
// ordinary HTML rules. Only output containment is projected; output is never
// fed back into tokenization or error recovery.
const ROOTS = new Set(['html', 'head', 'body', 'frameset']);
// These containers establish HTML's dedicated child-placement modes. Keeping
// their boundaries avoids projecting rows/cells outside their table or losing
// the filtering/placement semantics of select content.
const CHILD_MODES = new Set(['table', 'caption', 'colgroup', 'tbody', 'thead', 'tfoot', 'tr', 'td', 'th', 'select']);
export class RecognitionPreservingParser extends Parser {
  constructor({onCheckpoint = null, onScript = null, ...options} = {}, ...args) {
    super({...options, sourceCodeLocationInfo: true}, ...args);
    this.marked = new Set();
    this.textStarts = new Set();
    this.depth = 0;
    this.onCheckpoint = onCheckpoint;
    this.pendingScripts = [];
    this.onScript = onScript;
    this.scriptHandler = node => this.pendingScripts.push(node);
  }
  onStartTag(token) {
    const offset = token.location?.startOffset;
    super.onStartTag(token);
    // Existing void/foreign handling acknowledges its own markers.
    if (token.selfClosing && !token.ackSelfClosing) this.marked.add(offset);
    // Record the actual tokenizer transition, rather than a guessed list of
    // sensitive names. Scripting state and HTML/foreign context matter here.
    if (token.selfClosing && this.tokenizer.state !== TokenizerMode.DATA) this.textStarts.add(offset);
  }
  eligible(node) {
    const offset = node.sourceCodeLocation?.startTag?.startOffset;
    return node.namespaceURI === html.NS.HTML && this.marked.has(offset) &&
      !this.textStarts.has(offset) && !ROOTS.has(node.tagName) && !CHILD_MODES.has(node.tagName) && !node.content &&
      !node.attrs?.some(attr => attr.name === 'inert');
  }
  output(root = this.document) {
    const clone = (node, parentNode = null) => {
      const out = {...node, attrs: node.attrs?.map(attr => ({...attr})), parentNode, recognitionNode: node, childNodes: []};
      if (node.content) out.content = clone(node.content);
      for (const child of node.childNodes ?? []) {
        const item = clone(child, out);
        out.childNodes.push(item);
        if (this.eligible(child)) {
          const children = item.childNodes;
          item.childNodes = [];
          for (const following of children) {
            following.parentNode = out;
            out.childNodes.push(following);
          }
        }
      }
      return out;
    };
    return clone(root);
  }
  write(source, last = false) { this.tokenizer.write(source, last); }
  pause() { this.tokenizer.pause(); }
  resume() { this.tokenizer.resume(); }
  checkpoint(method, token) {
    this.depth++;
    try { handlers[method].call(this, token); }
    finally { this.depth--; }
    if (this.depth) return;
    this.onCheckpoint?.(token, this);
    for (const node of this.pendingScripts.splice(0)) this.onScript?.(node, this);
  }
}
const methods = ['onStartTag', 'onEndTag', 'onCharacter', 'onWhitespaceCharacter', 'onNullCharacter', 'onComment', 'onDoctype', 'onEof'];
const handlers = Object.fromEntries(methods.map(method => [method, RecognitionPreservingParser.prototype[method] ?? Parser.prototype[method]]));
for (const method of methods) Object.defineProperty(RecognitionPreservingParser.prototype, method, {
  value(token) { this.checkpoint(method, token); },
});
export function parseRecognition(source, options) {
  const parser = new RecognitionPreservingParser(options);
  parser.write(source, true);
  return {parser, tree: parser.output(), html: serialize(parser.output())};
}
