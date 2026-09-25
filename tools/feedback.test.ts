// The feedback routing stays in step with the chapters: every chapter is offered by its issue
// form, every offered answer resolves to a label, and pull requests get the same label. Both forms
// offer the same types, each resolving to a label.
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { test } from "node:test";
import { parse } from "yaml";
import { chapterLabels, labelsFor, typeLabels } from "../.github/scripts/chapter-label.mjs";

const options = (form: string, id = "chapter"): string[] =>
  parse(readFileSync(`.github/ISSUE_TEMPLATE/${form}.yml`, "utf8")).body.find((f: { id?: string }) => f.id === id).attributes.options;
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
  assert.deepEqual(labelsFor("### Chapter\n\nReactivity & Data\n\n### Feedback\n\n…"), ["chapter: reactivity"]);
  assert.deepEqual(labelsFor("### Chapter\n\nQUERY forms\n\n### Feedback"), ["chapter: query-forms"]);
  assert.deepEqual(labelsFor("### Chapter\n\nSeveral chapters or not sure\n"), []);
});

test("every type an issue form offers resolves to a label", () => {
  for (const form of ["declarative-components", "html-forms"]) {
    assert.deepEqual(options(form, "type"), [...typeLabels.keys(), "Not sure"], form);
  }
  const body = "### Chapter\n\nType System\n\n### Type\n\nSubstantive (what the proposal requires, allows, or defines)\n\n### Feedback";
  assert.deepEqual(labelsFor(body), ["chapter: types", "substantive"]);
  assert.deepEqual(labelsFor("### Chapter\n\nQUERY forms\n\n### Type\n\nNot sure\n"), ["chapter: query-forms"]);
});

test("pull requests are labeled by the chapter files they change", () => {
  const labeler = parse(readFileSync(".github/labeler.yml", "utf8"));
  for (const file of readdirSync("html-next").filter((f) => f.endsWith(".md"))) {
    const label = `chapter: ${file === "index.md" ? "front-page" : file.replace(/\.md$/, "")}`;
    assert.deepEqual(labeler[label], [{ "changed-files": [{ "any-glob-to-any-file": `html-next/${file}` }] }], label);
  }
});
