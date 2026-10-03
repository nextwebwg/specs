// Publishing sites can give guide pages a shared frame without copying chapter text.
import assert from "node:assert/strict";
import { test } from "node:test";
import { compileChapter } from "./compile.ts";

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
  assert.match(sfc, /<\/template>\s*<Section title="First steps">/);
  assert.match(sfc, /The guide body/);
  assert.match(sfc, /<Pager \/>\s*<SiteFooter \/>\s*<\/ToolsPage>/);
  assert.doesNotMatch(compileChapter(source).sfc, /ToolsPage|#header/);
});
