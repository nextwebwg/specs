// Publishing sites can give guide pages a shared frame without copying chapter text.
import assert from "node:assert/strict";
import { test } from "node:test";
import { compileChapter, headingId, MAX_HEADING_ID_LENGTH } from "./compile.ts";

const source = `---
title: A tools guide
---
# A guide

A short introduction.

## First steps

The guide body.
`;

test("an optional publisher frame separates the header and keeps the full chapter", () => {
  const { sfc } = compileChapter(source, { chapterFrame: "ToolsPage" });
  assert.match(sfc, /import \{[^}]*ToolsPage[^}]*\} from "#components"/);
  assert.match(sfc, /<ToolsPage>\s*<template #header>\s*<PageHeader/);
  assert.match(sfc, /<\/template>\s*<Section title="First steps" id="first-steps">/);
  assert.match(sfc, /The guide body/);
  assert.match(sfc, /<Pager \/>\s*<SiteFooter \/>\s*<\/ToolsPage>/);
  assert.doesNotMatch(compileChapter(source).sfc, /ToolsPage|#header/);
});

test("every heading gets an id from its text, an explicit one wins, and repeats are numbered", () => {
  const { sfc } = compileChapter(`---
title: Ids
---
# Ids

## Requests: behavior the consumer supplies

### Who answers

## Custom {#short}

### Who answers

### 2 ways to answer
`);
  assert.match(sfc, /<Section title="Requests: behavior the consumer supplies" id="requests-behavior-the-consumer-supplies">/);
  assert.match(sfc, /<h3 id="who-answers" class="sub">Who answers<\/h3>/);
  assert.match(sfc, /<Section title="Custom" id="short">/);
  assert.match(sfc, /<h3 id="who-answers-2" class="sub">Who answers<\/h3>/);
  assert.match(sfc, /<h3 id="section-2-ways-to-answer" class="sub">/);
});

test("a heading id is a valid identifier from the text, in any script, within the length limit", () => {
  assert.equal(headingId("Asking: host.request"), "asking-host-request");
  assert.equal(headingId("Crème brûlée & café"), "crème-brûlée-café");
  assert.equal(headingId("Überblick über Komponenten"), "überblick-über-komponenten");
  assert.equal(headingId("2026 roadmap"), "section-2026-roadmap");
  assert.equal(headingId("—"), "section");
  const long = headingId("Creating components from code with a registry modeled on the custom elements registry");
  assert.ok([...long].length <= MAX_HEADING_ID_LENGTH);
  assert.equal(long, "creating-components-from-code-with-a-registry-modeled-on-the");
  assert.match(long, /^\p{L}[\p{L}\p{N}\p{M}-]*$/u);
});
