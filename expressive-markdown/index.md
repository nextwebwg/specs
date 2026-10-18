---
title: Expressive Markdown
order: -1
layout: proposal
eyebrow: Next Web Working Group · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Expressive Markdown

A common language for documentation.

- [Learn the syntax →](/expressive-markdown/language)
- [Implement a parser or writer →](/expressive-markdown/parsing)
- [Browse Chapters ↓](#chapters)

Editors
: [Matthew Dean](https://github.com/matthew-dean)

Feedback
: [GitHub issues](https://github.com/nextwebwg/specs/issues/new/choose) · [contribution terms](https://github.com/nextwebwg/.github/blob/main/CONTRIBUTING.md)

Status
: Unofficial Editor's Draft · Stage 0. Not a W3C or WHATWG deliverable.

## Status of this document {.sotd}

Expressive Markdown is a proposed Markdown language and document format. This
unofficial editor's draft is open for discussion. It does not represent the
W3C, WHATWG or a browser vendor, or require browsers to parse Markdown.

## Abstract

Start a heading with `#`, make text bold with `**text**`, create a link with
`[label](url)`, or start a list item with `-`. For example:

```md
# Installation

Install the package, then **check the version**.

- Download the package.
- Run the installer.
```

Use callouts to highlight important notes, tabs to offer alternative
instructions, and tables to compare information. The
[language reference](/expressive-markdown/language) explains each form with its
syntax, HTML representation, AST data and rendering examples.

The same document can move between a text editor, a rich editor and a
documentation site. A warning keeps its meaning and a mention keeps its target;
renderers choose their own colors and layout.

## What the proposal defines

::: targets
Readable Markdown
: Familiar CommonMark/GFM, extended with named blocks and inline content,
  shared attributes, YAML frontmatter, explicit lines and merged table cells.

Shared meanings
: Standard documentation features with suggested HTML conversions. Custom
  types remain valid, so the vocabulary can grow without a new grammar.

Document data
: An independent JSON abstract syntax tree (AST), with named title/body fields,
  compact text values, authored IDs and predictable traversal.

Publishing
: Rendering recommendations and optional navigation metadata, without requiring
  a component framework, CSS library or site generator.
:::

## Chapters

::chapter-index

## Tools

[expressmark](https://github.com/nextwebwg/expressmark) is the JavaScript tooling
project for Expressive Markdown, with releases on
[npm](https://www.npmjs.com/package/expressmark). Its repository documents the
available APIs and implementation status. The language and AST remain independent of that
package.

## Prior art

Expressive builds on established Markdown conventions:

- **CommonMark and GFM:** ordinary Markdown, tables, task lists and strikethrough.[^1]
- **Docusaurus and remark:** documentation callouts, nested colon fences and named constructs.[^2][^3]
- **Pandoc:** attribute IDs and leading-pipe line blocks.[^4]
- **UMD:** compact markers for merged table cells.[^5]
- **mdast and unist:** documented tree structures; Expressive uses its own named content fields.[^6]

These influences do not imply full source compatibility. MDX/JSX, JavaScript
execution and framework component APIs are outside the language.

## References

[^1]: [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) and [GitHub Flavored Markdown](https://github.github.com/gfm/).
[^2]: [Docusaurus Markdown features](https://docusaurus.io/docs/markdown-features) and [admonitions](https://docusaurus.io/docs/markdown-features/admonitions).
[^3]: [remark-directive](https://github.com/remarkjs/remark-directive).
[^4]: [Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown).
[^5]: [UMD table-spanning documentation](https://docs.rs/crate/umd/0.2.0/source/README.md).
[^6]: [mdast](https://github.com/syntax-tree/mdast) and [unist](https://github.com/syntax-tree/unist).
