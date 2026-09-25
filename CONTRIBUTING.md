# Writing a chapter

Chapters are CommonMark with GitHub tables, plus a small set of conventions borrowed from
GitHub, Obsidian, Pandoc, and markdown-it. Every construct below becomes one element or
component on the published page, so what you write is what readers see. Raw HTML is not
accepted, apart from the three inline elements Markdown has no syntax for.

[`tools/compile.ts`](./tools/compile.ts) is the reference implementation; `corepack pnpm check`
runs it over every chapter and fails on anything it cannot place.

## Page structure

Each file starts with YAML frontmatter, then its title and lede:

```md
---
title: Reactivity & Data          # the name in navigation and the page title
order: 5                          # position among the chapters
blurb: state · computed · data    # the line under the name in the chapter index
eyebrow: Declarative HTML Components Level 1 · proposed shapes
status: Stage 0 · Level 1 proposal
---

# Reactivity & Data

The first paragraph after the title is the lede.

## A section

### A subsection
```

| Key | Meaning |
| --- | --- |
| `navGroup: guide` | List the page under "Start here" (Overview, Examples) instead of the numbered chapters. |
| `pager: false` | Omit the previous/next links (a standalone proposal). |
| `layout: proposal` | The proposal's front page; see below. |

`##` starts a section and `###` a subsection. A section runs until the next `##`; a thematic
break (`---`) ends it early, for the rare block that sits between two sections. Give a heading
an anchor with `{#name}`: `## Constraint validation {#validation}`.

## Blocks

| Write | For |
| --- | --- |
| `> [!note] Title` | A callout. Kinds: `note`, `ex` (example), `norm` (normative), `warn` (open or cautionary). The body follows on `>` lines. |
| ```` ```html title="button.html" ```` | A code sample, optionally with its file name. HTML is the default language; others are `css`, `js`, `ts`, `json`, `bash`, `text`. |
| A GitHub table | A table. |
| `1. step` followed by `{.algo}` on the next line | Numbered algorithm steps. |
| A paragraph ending in `{.lede}` | A lede paragraph inside a section. |
| `::: two` … `:::` | Two blocks side by side, such as two callouts or two code samples. |
| `::: {#name}` … `:::` | An anchor around a section, for links into it. |
| `::chapter-index` | The generated list of chapters (front page). |

### Element entries

An element reference entry is a fenced div with the element's name and role, holding a
definition list:

```md
::: {.entry name="<data> · <param>" role="declared reactive resource"}
Attributes
: `name`, `src`, `method?` · `<param name :value>`

Level
: [L1]{.pill .l1}
:::
```

Quote a name that contains `"` with single quotes: `name='<link rel="component">'`.

### Front-page blocks

| Write | For |
| --- | --- |
| `::: targets` with a definition list | A grid of labelled cards (a term and its description). |
| `::: flow` with a list | A left-to-right flow; mark the highlighted step with a trailing `{.acc}`. |
| `::: fix` with `### Title`, a subtitle paragraph, then `##### Why it's broken` and `##### <answer label>` each with a list | A numbered problem-and-answer card. Consecutive cards number themselves. |
| `::: record` with `#### Label`, a claim paragraph, and a body paragraph per item | The evidence record. |

## Inline

| Write | For |
| --- | --- |
| `` `code` ``, `**strong**`, `*emphasis*` | As usual. |
| `[text](/html-next/types)` | A link. Site paths navigate within the site; `#name` and full URLs are ordinary links. |
| `[^3]` | A citation of reference 3. |
| `[^3]: Author, [title](https://…).` | Reference 3. References are numbered from 1, in order, usually under `## Sources` or `## References`. |
| `[must]{.kw}` | An RFC 2119 keyword (`must`, `must not`, `should`, `may`, …). |
| `[L1]{.pill .l1}` | A Level pill: `l1` (Level 1), `inc` (in progress or later Level), `soon` (future Level). |
| `[term]{.dfn}` | A defined term. |
| `<var>name</var>` inside `<code>…</code>` | A variable within code: `<code>host.refs.<var>name</var></code>`. |
| `<br>` | A line break inside a table cell. |
| `&nbsp;` | A non-breaking space, as in `Level&nbsp;1` or `RFC&nbsp;6570`. |

Escape a character that Markdown would otherwise read as syntax with a backslash, as in `\*`.

## The proposal front page

`html-next/index.md` uses `layout: proposal`. Its masthead is generated from the frontmatter
and the lines before the first `##`, the way specification tools generate a document header:

```md
---
layout: proposal
title: Declarative HTML Components
order: -1
eyebrow: HTML Next · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Declarative HTML Components Level 1

The tagline.

- [Start with Overview →](/html-next/overview)

Editors
: Next Web Working Group

## Status of this document {.sotd}
```

The list becomes the reading paths, the definition list the document metadata (after a generated
"Latest snapshot" row), and the `{.sotd}` section the status of this document.
