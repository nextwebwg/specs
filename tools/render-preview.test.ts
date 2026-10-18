import assert from "node:assert/strict";
import { test } from "node:test";
import { compileChapter } from "./compile.ts";

const chapter = (body: string) => `---\ntitle: Rendering\n---\n# Rendering\n\n## Examples\n\n${body}`;
const preview = (html: string, height = "180") => `::: {.render title="Cells and code" height="${height}"}\n\`\`\`html\n${html}\n\`\`\`\n:::`;

test("rendered illustrations preserve native cells and blocks in an isolated srcdoc", () => {
  const { sfc } = compileChapter(chapter(preview('<table><tr><td><ul><li>First</li></ul><pre><code>one\n  two</code></pre></td></tr></table>')));
  assert.match(sfc, /Rendering example/);
  assert.match(sfc, /<iframe title="Cells and code" sandbox="" loading="lazy" height="180"/);
  assert.match(sfc, /srcdoc="&lt;!doctype html&gt;/);
  assert.match(sfc, /&lt;td&gt;&lt;ul&gt;&lt;li&gt;First/);
  assert.match(sfc, /one\n  two/);
  assert.match(sfc, /default-src 'none'/);
});

test("preview HTML cannot close its frame or become Vue template code", () => {
  const { sfc } = compileChapter(chapter(preview('</iframe><script>alert(1)</script><p>{{ value }}</p>')));
  assert.equal((sfc.match(/<iframe /g) ?? []).length, 1);
  assert.equal((sfc.match(/<\/iframe>/g) ?? []).length, 1);
  assert.doesNotMatch(sfc.split("<template>")[1], /alert\(1\)<\/script>|\{\{ value \}\}/);
  assert.match(sfc, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
});

test("malformed preview bodies and heights fail chapter compilation", () => {
  assert.throws(() => compileChapter(chapter('::: {.render}\nOrdinary prose.\n:::')), /exactly one html code fence/);
  assert.throws(() => compileChapter(chapter(preview('<p>Example</p>', '12px'))), /positive integer/);
});

test("HTML source and a closed AST disclosure stay between Markdown and its rendering", () => {
  const { sfc } = compileChapter(chapter([
    '```md', '::: table {transpose}', '- Name: Ada', ':::', '```', '',
    ':::: {.render title="Vertical fields"}', '```html',
    '<table><tr><th scope="row">Name</th><td>Ada</td></tr></table>', '```', '',
    '::: {.details #vertical-fields-ast summary="AST"}', '```json',
    '{"type":"table","children":[{"type":"tableRow","children":[{"type":"tableCell","header":true,"value":"Name"},{"type":"tableCell","value":"Ada"}]}]}', '```', ':::', '::::',
  ].join('\n')));
  const markdown = sfc.indexOf('<CodeBlock :code="__code[0]"');
  const html = sfc.indexOf('<CodeBlock :code="__code[1]"');
  const ast = sfc.indexOf('<details class="spec-disclosure" id="vertical-fields-ast">');
  const json = sfc.indexOf('<CodeBlock :code="__code[2]"');
  const rendering = sfc.indexOf('<div class="render-preview">');
  assert.ok(markdown >= 0 && markdown < html && html < ast && ast < json && json < rendering);
  assert.doesNotMatch(sfc, /<details[^>]*\bopen(?:[\s>]|=)/);
});

test("tab previews enable only the publisher's fixed controller inside an opaque frame", () => {
  const html='<div data-tabs aria-label="Install"><section data-tab="npm"><h3>npm</h3><p>First</p></section><section data-tab="pnpm"><h3>pnpm</h3><p>Second</p></section></div>';
  const {sfc}=compileChapter(chapter(preview(html).replace('height="180"','height="180" interactive="tabs"')));
  assert.match(sfc,/sandbox="allow-scripts"/);
  assert.match(sfc,/script-src 'sha256-[A-Za-z0-9+/=]+'/);
  assert.match(sfc,/script-src-attr 'none'/);
  assert.doesNotMatch(sfc,/allow-same-origin|unsafe-eval/);
  assert.match(sfc,/role.*tablist/);
  assert.match(sfc,/ArrowLeft/);
});

test("unknown interactive preview modes fail instead of enabling arbitrary scripts", () => {
  assert.throws(()=>compileChapter(chapter(preview('<p>Text</p>').replace('height="180"','height="180" interactive="custom"'))),/interactive preview/);
});
