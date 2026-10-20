import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parse, serialize, html} from 'parse5';
import {RecognitionPreservingParser, parseRecognition} from './parser.mjs';

function inventory(root, projected = false) {
  const entries = [];
  const walk = (node, barriers = []) => {
    const key = projected ? node.recognitionNode : node;
    entries.push({key, name: node.nodeName, ns: node.namespaceURI,
      attrs: node.attrs?.map(a => ({...a})), value: node.value, data: node.data,
      barriers: [...barriers]});
    const boundary = node.content || (node.namespaceURI && node.namespaceURI !== html.NS.HTML) || node.attrs?.some(a => a.name === 'inert');
    const inside = boundary ? [...barriers, key] : barriers;
    for (const child of node.childNodes ?? []) walk(child, inside);
    if (node.content) walk(node.content, inside);
  };
  walk(root);
  return entries;
}
function verify(parser) {
  const before = inventory(parser.document);
  const serialized = serialize(parser.document);
  const output = parser.output();
  const after = inventory(output, true);
  assert.equal(after.length, before.length);
  for (let i = 0; i < before.length; i++) {
    assert.equal(after[i].key, before[i].key, `node identity/order at ${i}`);
    assert.deepEqual({...after[i], key: null, barriers: []}, {...before[i], key: null, barriers: []});
    assert.deepEqual(after[i].barriers, before[i].barriers, `protected ancestors at ${i}`);
  }
  assert.equal(serialize(parser.document), serialized, 'output leaves recognition unchanged');
  return output;
}
const witnesses = [
  '<small/><span>tail</span>', '<b/><p>one</p>two', '<a/><b/>tail',
  '<style/><img src=x onerror=attack()></style>',
  '<script/>attack()</script><p>tail</p>',
  '<textarea/><img src=x onerror=attack()></textarea>',
  '<div/><svg></div><style><img src=x onerror=attack()></style></svg>',
  '<div><x-box/></div><svg></x-box><title><style></title><img src=x onerror=attack()></style>',
  '<h1/><svg></h2><style><img src=x onerror=attack()></style></svg>',
  '<svg><mtext><style><table/><style/><img src=x onerror=attack()></style></mtext></svg>',
  '<template/><script>attack()</script><img src=x onerror=attack()>',
  '<template><small/><img src=x onerror=attack()></template>',
  '<div inert/><button onclick=attack()>go</button>',
  '<table/><p>tail</p>', '<table><tr/><td>cell</td></table>',
  '<select/><option>one</option><img src=x onerror=attack()>',
  '<form/><input name=x>', '<div hidden/><span>tail</span>',
  '<noscript/><img src=x onerror=attack()></noscript>',
  '<plaintext/><img src=x onerror=attack()>', '<div data-path=assets/>tail',
];
for (const scriptingEnabled of [true, false]) for (const body of witnesses) {
  test(`identity, text, and protected ancestry: scripting=${scriptingEnabled} ${body}`, () => {
    const source = '<!doctype html><body>' + body;
    const parser = new RecognitionPreservingParser({scriptingEnabled, onCheckpoint(_t,p) { verify(p); }});
    parser.write(source, true);
    assert.equal(serialize(parser.document), serialize(parse(source, {scriptingEnabled})));
    verify(parser);
  });
}
for (const name of ['small','b','em','a','p','form','button','fieldset','div','x-box']) {
  test(`broad shorthand: ${name} closes in output`, () => {
    const source = '<!doctype html><body>';
    const actual = parseRecognition(source + `<${name}/><span>tail</span>`).html;
    const expected = serialize(parse(source + `<${name}></${name}><span>tail</span>`));
    assert.equal(actual, expected);
  });
}
test('source chunks never change recognition or the projected result', () => {
  for (const body of witnesses) {
    const source = '<!doctype html><body>' + body + '😀&amp;';
    const expected = parseRecognition(source).html;
    for (let split = 0; split <= source.length; split++) {
      const parser = new RecognitionPreservingParser();
      parser.write(source.slice(0, split)); verify(parser);
      parser.write(source.slice(split), true); verify(parser);
      assert.equal(serialize(parser.output()), expected, `${body} split ${split}`);
    }
  }
});
test('scripts checkpoint the projected DOM before reading following source', () => {
  let observed;
  const parser = new RecognitionPreservingParser({onScript(_node,p) {
    observed = serialize(verify(p)); p.pause();
  }});
  parser.write('<body><small/><script>checkpoint()</script><span>tail</span>', true);
  assert.match(observed, /<small><\/small><script>/);
  assert.doesNotMatch(observed, /<span>/);
  parser.resume();
  assert.match(serialize(verify(parser)), /<span>tail<\/span>/);
});
export {inventory, verify, witnesses};

test('dedicated child-placement containers keep their boundaries', () => {
  for (const source of ['<table/><p>tail</p>', '<select/><option>one</option>', '<table><tr><td/><span>cell</span></table>']) {
    const result = parseRecognition(source);
    assert.equal(result.html, serialize(parse(source)));
  }
});

test('negative control: immediate closing activates the retained namespace witness', async () => {
  const {parseClosure} = await import('../closure/parser.mjs');
  const source = '<!doctype html><body><div/><svg></div><style><img src=x onerror="attack()"></style></svg>';
  const images = root => {
    const found = [];
    const walk = node => { if (node.tagName === 'img') found.push(node); for (const child of node.childNodes ?? []) walk(child); if (node.content) walk(node.content); };
    walk(root); return found;
  };
  assert.equal(images(parseClosure(source).tree).length, 1);
  assert.equal(images(parseRecognition(source).tree).length, 0);
});
