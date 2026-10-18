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
  assert.doesNotMatch(sfc, /alert\(1\)<\/script>|\{\{ value \}\}/);
  assert.match(sfc, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
});

test("malformed preview bodies and heights fail chapter compilation", () => {
  assert.throws(() => compileChapter(chapter('::: {.render}\nOrdinary prose.\n:::')), /exactly one html code fence/);
  assert.throws(() => compileChapter(chapter(preview('<p>Example</p>', '12px'))), /positive integer/);
});
