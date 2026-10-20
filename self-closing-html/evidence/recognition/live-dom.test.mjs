import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {LiveDOMParser} from './live-dom.mjs';

async function run(source, check) {
  const dom = new JSDOM('', {runScripts:'dangerously', url:'https://example.invalid/'});
  dom.window.trace = [];
  try {
    const parser = new LiveDOMParser(dom.window.document);
    await parser.write('<!doctype html><body>' + source, true);
    await check(dom.window, parser);
  } finally { dom.window.close(); }
}
for (const source of [
  '<style/><img src=x onerror="trace.push(\'BAD\')"></style>',
  '<div/><svg></div><style><img src=x onerror="trace.push(\'BAD\')"></style></svg>',
]) test('text never becomes an image in the live output: '+source, () => run(source, async window => {
  assert.equal(window.document.querySelectorAll('img').length, 0);
  assert.deepEqual([...window.trace], []);
}));
test('template contents keep scripts and handlers inactive', () => run(
  '<template/><small/><script>trace.push("BAD")</script><img src=x onerror="trace.push(\'BAD\')">', window => {
    assert.deepEqual([...window.trace], []);
    assert.equal(window.document.querySelectorAll('script,img').length, 0);
    const content = window.document.querySelector('template').content;
    assert.equal(content.querySelectorAll('script,img').length, 2);
    assert.equal(content.querySelector('small').childNodes.length, 0);
    assert.equal(content.querySelector('img').isConnected, false);
    assert.equal(content.querySelector('img').ownerDocument.defaultView, null);
  }));
test('ordinary following scripts execute at the right checkpoint', () => run(
  '<small id="empty"/><script>trace.push([document.getElementById("empty").childNodes.length,document.currentScript.parentNode.tagName,!!document.querySelector("span")])</script><span>tail</span>', window => {
    assert.deepEqual(JSON.parse(JSON.stringify(window.trace)), [[0,'BODY',false]]);
    assert.equal(window.document.querySelector('span').parentNode.tagName, 'BODY');
  }));
test('script mutations to a shorthand element survive following parsing', () => run(
  '<small id="empty"/><script>document.getElementById("empty").append("owned")</script><span>tail</span>', window => {
    assert.equal(window.document.getElementById('empty').textContent, 'owned');
    assert.equal(window.document.querySelector('span').parentNode.tagName, 'BODY');
  }));
