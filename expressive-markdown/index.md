---
title: Expressive Markdown
order: -1
layout: proposal
eyebrow: Next Web Working Group · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Expressive Markdown

Keep your docs when your tools change.

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

You write a guide. Add a warning. Put a checklist in a table. Then move it to
another tool.

**Your document should arrive with its meaning intact.**

CommonMark defines the basics. GFM adds tables and task lists.[^1]
Expressive Markdown builds on them so richer documents can move between tools.

### Conversions should preserve meaning

A warning can become a styled paragraph. A block can lose its title.
Converting it back cannot restore what was discarded.

::::: {.two}
:::: {.example}
**Write it as Markdown**

```md
::: warning [Before upgrading]
Back up your data.
:::
```
::::

:::: {.example}
**Keep it as a warning**

> [!warn] Before upgrading
> Back up your data.
::::
:::::

Expressive Markdown defines **text syntax and document structure** together,
so editors and publishers can preserve the warning’s title, body and meaning. [See the warning example →](/expressive-markdown/language#named-constructs)

### Tables should be easy to read and type

Long pipe-table rows are hard to scan and awkward to edit. Their cells cannot
hold lists or other block content.[^7]

Write each row as a list instead. No column padding. Room for paragraphs,
lists and code:

```md
::: table

- Task: Install
  Steps:
    - Download the package.
    - Run the installer.

:::
```

[Explore tables and merged cells →](/expressive-markdown/language#tables)
Traditional pipe tables remain supported.

### Extensions need shared rules

A callout here, a tab group there. Different tools use different syntax and
conventions.[^2][^3] Moving your docs can mean rewriting them.

CommonMark and GFM leave those features open. Expressive Markdown proposes
**shared syntax and meanings** for richer content, with room for custom types.

Your content stays independent of a component framework or site generator.
**Choose your tools. Keep your docs.**

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
