import {interpretPlainText} from './flowed-text.mjs';

// A display-only experiment. Parents are explicitly selected earlier messages.
// Each input has decoded text and its own MIME format/delsp parameters.
export function reconstructFlowedQuotes(message, parents) {
  if (String(message.format).toLowerCase() !== 'flowed') {
    throw new TypeError('This reconstruction profile requires declared flowed text');
  }
  const paragraphs = interpretPlainText(message.text, message);
  const sources = parents.map(parent => ({
    id: parent.id,
    paragraphs: interpretPlainText(parent.text, parent),
  }));
  const blocks = [];
  for (let i = 0; i < paragraphs.length;) {
    const start = i;
    const depth = paragraphs[i].depth;
    while (i < paragraphs.length && paragraphs[i].depth === depth) i++;
    const content = paragraphs.slice(start, i);
    const matches = [];
    if (depth === 1 && content.some(p => p.text.trim()) &&
        content.every(p => p.kind !== 'signature' && p.diagnostics.length === 0)) {
      for (const source of sources) {
        for (let j = 0; j + content.length <= source.paragraphs.length; j++) {
          const span = source.paragraphs.slice(j, j + content.length);
          if (span.every((p, k) => p.depth === 0 && p.kind !== 'signature' &&
              p.diagnostics.length === 0 && p.text === content[k].text)) {
            matches.push({message: source.id, sourceLines: span.flatMap(p => p.sourceLines)});
          }
        }
      }
    }
    blocks.push({
      kind: matches.length === 1 ? 'repeated-quote' : 'visible',
      paragraphs: content,
      sourceLines: content.flatMap(p => p.sourceLines),
      source: matches.length === 1 ? matches[0] : null,
    });
  }
  return blocks;
}
