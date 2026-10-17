---
title: Expressive Markdown
order: -1
layout: proposal
eyebrow: Next Web Working Group · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Expressive Markdown

A common language for documentation.

- [Read Language & Semantics →](/expressive-markdown/language)
- [Explore the Document AST →](/expressive-markdown/ast)
- [Browse Chapters ↓](#chapters)

Editors
: [Matthew Dean](https://github.com/matthew-dean)

Feedback
: [GitHub issues](https://github.com/nextwebwg/specs/issues/new/choose) · [contribution terms](https://github.com/nextwebwg/.github/blob/main/CONTRIBUTING.md)

Status
: Unofficial Editor's Draft · Stage 0. Not a W3C or WHATWG deliverable.

## Status of this document {.sotd}

This proposal is an unofficial editor's draft for discussion. It defines a
Markdown document format, its meanings and an independent data representation.
It does not require browsers to parse Markdown and does not represent the
position of the W3C, WHATWG or a browser vendor. No conforming parser or editor
integration is claimed by this draft.

## Abstract

Expressive Markdown adds named documentation constructs to familiar Markdown
and defines the document data that editors and renderers exchange. The aim is
readable source with shared meaning: a warning remains a warning, an entity
mention retains its reference, and a table of contents contains readable links.
Presentation can vary without losing those meanings.

````md
:::: warning [Before deploying] {#deployment-check}

Back up the database first.

::: tip [Check the backup]
Try restoring it in a separate environment.
:::

::::

Status: :chip[Ready]{tone=green}.
````

The warning and tip share the `container` AST family, with recognized semantic
subtypes. The chip belongs to inline content. Their type names convey meaning;
colors, icons and layout remain renderer choices.

## What the proposal defines

::: targets
Readable source
: CommonMark/GFM foundations, bracketed titles, named constructs, frontmatter,
  explicit line blocks and merged table cells.

Shared meanings
: Recognized semantic subtypes with documented attributes, defaults and suggested
  HTML conversions, alongside an open vocabulary for extensions.

Document data
: A JSON AST with named title/body roles, compact literal content, stable authored
  identities and predictable traversal.

Presentation coverage
: Documentation and rich-editor features, an optional publishing profile, and a
  survey of this site's presentation patterns for future publishing integration.
:::

## Chapters

::chapter-index

## Prior art

CommonMark and GFM supply the ordinary Markdown foundation.[^1] Docusaurus
informs documentation presentation and nested callouts.[^2] Remark directives
provide the inline, bodyless-block and container scopes.[^3] Pandoc provides
prior art for IDs and leading-pipe line blocks.[^4] UMD contributes compact
cell-merging markers.[^5] mdast and unist inform the documented-tree approach;
Expressive defines its own named content fields and traversal.[^6]

Each feature chapter identifies the convention it adopts and its compatibility
limits. Full MDX/JSX source compatibility and a JavaScript component runtime are
outside this language contract.

## References

[^1]: [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) and [GitHub Flavored Markdown](https://github.github.com/gfm/).
[^2]: [Docusaurus Markdown features](https://docusaurus.io/docs/markdown-features) and [admonitions](https://docusaurus.io/docs/markdown-features/admonitions).
[^3]: [remark-directive](https://github.com/remarkjs/remark-directive).
[^4]: [Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown).
[^5]: [UMD 0.2.0 source and table-spanning documentation](https://docs.rs/crate/umd/0.2.0/source/README.md).
[^6]: [mdast](https://github.com/syntax-tree/mdast) and [unist](https://github.com/syntax-tree/unist).
