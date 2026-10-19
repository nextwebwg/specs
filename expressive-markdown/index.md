---
title: Expressive Markdown
order: -1
layout: proposal
eyebrow: Next Web Working Group · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Expressive Markdown

Markdown for structured, portable documents.

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

## Why Expressive Markdown

Documentation often moves between text editors, rich editors and publishing
tools. Those tools may preserve the words while losing the structure needed
for further editing.

CommonMark defines ordinary Markdown. GFM adds tables, task lists and
strikethrough.[^1] Expressive Markdown builds on these formats to address three
recurring problems in richer documents:

### Problem #1 - Conversions can lose structure

A warning can become a styled paragraph. A titled block can lose the
distinction between its title and body. Saving the result as Markdown cannot
reliably recover that information.

::::: {.two}
:::: {.example}
**Markdown source**

```md
::: warning [Before upgrading]
Back up your data.
:::
```
::::

:::: {.example}
**Rendered warning**

> [!warn] Before upgrading
> Back up your data.
::::
:::::

Expressive Markdown defines **text syntax and a shared document tree**, with
explicit fields for titles, content and attributes. Editors and publishers
have a common representation to preserve through conversion, even when
whitespace or presentation changes.

[See the warning example →](/expressive-markdown/language#named-constructs)

### Problem #2 - Tables can be hard to edit

Pipe tables work well for short values. Long rows are harder to scan and
require editing across columns. GFM cells cannot contain block content such
as paragraphs, lists or fenced code.[^7]

List-based tables let each cell read from top to bottom. Text can wrap without
aligning neighboring columns, and cells can hold ordinary Markdown blocks:

```md
::: table

- Task: Install
  Steps:
    - Download the package.
    - Run the installer.

:::
```

[Explore tables and merged cells →](/expressive-markdown/language#tables)
Traditional pipe tables remain supported for compatibility.

### Problem #3 - Extensions vary between tools

Documentation tools provide callouts, tabs and other features through
extensions. Their syntax and conventions vary, so moving a document can
require translating those features individually.[^2][^3]

CommonMark and GFM do not define a shared format for those features.
Expressive Markdown proposes consistent syntax, common meanings and document
data for them. Custom types use the same grammar.

The format is independent of a component framework or site generator.

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
[^7]: [GFM table syntax and cell contents](https://github.github.com/gfm/#tables-extension).
