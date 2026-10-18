---
title: Expressive Markdown
order: -1
layout: proposal
eyebrow: Next Web Working Group · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Expressive Markdown

Familiar Markdown for documentation that keeps its meaning when it moves
between editors and publishing tools.

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

Your documentation should survive a change of tools. A warning should keep its
title and body. A table should keep the lists inside its cells. Editing a
page as rich text and saving it as Markdown should preserve that structure.

CommonMark makes ordinary Markdown predictable: headings, links, lists and
other familiar constructs have defined parsing rules. GFM adds useful features
such as pipe tables, task lists and strikethrough.[^1] Expressive Markdown
builds on that foundation, addressing three gaps for richer documents.

### Conversions should preserve meaning

A document can look right after conversion while losing information needed
for its next edit. A warning may become a styled paragraph; a titled block may
lose the distinction between its title and body. Converting that result back
to Markdown cannot reliably recover what was discarded.

Expressive Markdown defines both a text syntax and a shared document tree,
with explicit fields for content, titles, attributes and identity. The aim is
to preserve meaning as content moves between text editors, rich editors and
publishing tools, even when formatting or presentation changes.

For example, this warning has a name, a title and a body:

```md
::: warning [Before upgrading]
Back up your data before installing the new version.
:::
```

An editor can offer the title as an editable field and write it back to the
same construct. A publisher can choose the colors and icon. The
[warning example](/expressive-markdown/language#named-constructs) shows its
Markdown, HTML, document data and rendering together.

### Tables should be easy to read and type

Pipe tables work well for short values. Long cells make rows hard to scan,
and keeping columns visually aligned takes editing effort. GFM table cells
also cannot contain block content such as paragraphs, lists or fenced code
blocks.[^7]

Expressive Markdown uses lists for table authoring. Each row reads from top to
bottom, with named fields or positional cells. You can wrap text and include
ordinary Markdown blocks inside a cell, without padding neighboring columns:

```md
::: table

- Task: Install
  Instructions: Download the package and run the installer.

- Task: Verify
  Instructions: Check the version before continuing.

:::
```

[Tables](/expressive-markdown/language#tables) also support row and column spans.
Traditional pipe tables remain supported for compatibility.

### Extensions need shared rules

Documentation tools already offer callouts, tabs and other richer content.
Their extensions use different syntax and conventions, so moving a document
can mean translating its features one by one.[^2][^3]

CommonMark and GFM do not define a shared format for those features.
Expressive Markdown proposes a consistent grammar for named blocks and inline
content, shared attributes, and defined meanings for common documentation
constructs. Custom types use the same grammar, so an extension need not invent
another syntax.

The proposal keeps content independent of a particular component framework or
site generator. Authors get readable files they can keep when their tools
change; implementers get a common format to parse, edit and write. The
[language reference](/expressive-markdown/language) shows the syntax and its
document representations side by side.

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
