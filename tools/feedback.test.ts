// The feedback routing stays in step with the chapters: every chapter is offered by its issue
// form, every offered answer resolves to a label, and pull requests get the same label.
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { test } from "node:test";
import { parse } from "yaml";
import { chapterLabels, labelFor } from "../.github/scripts/chapter-label.mjs";

const options = (form: string): string[] =>
  parse(readFileSync(`.github/ISSUE_TEMPLATE/${form}.yml`, "utf8")).body.find((f: { id?: string }) => f.id === "chapter").attributes.options;
const unsure = (option: string) => option.startsWith("Several ");

test("every chapter is offered by its issue form and resolves to a label", () => {
  const labels = chapterLabels();
  const offered = options("declarative-components");
  for (const file of readdirSync("html-next").filter((f) => f.endsWith(".md"))) {
    const title = readFileSync(`html-next/${file}`, "utf8").match(/^title: (.+)$/m)![1];
    assert.ok(offered.includes(title), `the Declarative HTML Components form does not offer ${title}`);
  }
  for (const option of [...offered, ...options("html-forms")].filter((o) => !unsure(o))) {
    assert.ok(labels.get(option), `no label for "${option}"`);
  }
  assert.equal(labelFor("### Chapter\n\nReactivity & Data\n\n### Feedback\n\n…"), "chapter: reactivity");
  assert.equal(labelFor("### Chapter\n\nQUERY forms\n\n### Feedback"), "chapter: query-forms");
  assert.equal(labelFor("### Chapter\n\nSeveral chapters or not sure\n"), undefined);
});

test("pull requests are labeled by the chapter files they change", () => {
  const labeler = parse(readFileSync(".github/labeler.yml", "utf8"));
  for (const file of readdirSync("html-next").filter((f) => f.endsWith(".md"))) {
    const label = `chapter: ${file === "index.md" ? "front-page" : file.replace(/\.md$/, "")}`;
    assert.deepEqual(labeler[label], [{ "changed-files": [{ "any-glob-to-any-file": `html-next/${file}` }] }], label);
  }
});
