---
title: Language & Semantics
order: 1
blurb: syntax · meaning · HTML guidance
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Language & Semantics

Write familiar Markdown, then add readable documentation features: callouts,
tabs, mentions, explicit lines and merged tables. Each feature has a shared
meaning and a documented data shape, independent of the editor or renderer.

```md
::: warning [Before deploying] {#deployment-check}
Back up the database first.
:::

Status: :chip[Ready]{tone=green}.
Thanks, @[Ada Lovelace]#user-123.
```

| Form | Use |
| --- | --- |
| `:chip[Ready]{tone=green}` | Inline content within a sentence. |
| `::type[label]{attributes}` | A standalone construct without a body. |
| `::: warning [Title] {attributes}` … `:::` | A named container holding blocks. |
| `{#check open audience=admin}` | An ID, a true flag and a string attribute. |

The [parser reference](/expressive-markdown/parsing) specifies boundaries and
recovery. The [AST reference](/expressive-markdown/ast) defines the document tree.
HTML conversions below are recommendations, not required output.

## Named constructs

These open the same warning:

```md
:::warning[Before deploying]{#check}
::: warning {#check} [Before deploying]
```

- Put the type first. Title and attributes can follow in either order.
- Keep the opening header on one source line. Spaces between parts are optional;
  brackets and braces have no padding immediately inside them.
- Titles and inline labels support inline Markdown.
- Inline constructs use `:type[label]{attributes}`; bodyless blocks use
  `::type[label]{attributes}` on their own line. An inline construct needs a label
  or attributes, so bare `:word` is ordinary text.

### Nested containers

Use a longer fence for the outer container:

```md
:::: note [Outer]

::: warning [Inner]
Check the configuration.
:::

::::
```

Fences have at least three colons. A directly nested container uses fewer than
its parent; each closing fence matches its opening length. Bodies can contain
ordinary blocks, lists, quotes and code.

> [!note] Source spacing is for readability
> Blank lines just inside the fences do not add visible empty lines. Use a
> [line block](#leading-pipe-line-blocks) when the extra line is intentional.

## Attributes and identity

```md
{#deployment-check open audience=admin label="Before deploying"}
```

| Source | Meaning |
| --- | --- |
| `open` / `!open` | Boolean true / false. |
| `open=foo` | String `"foo"`. |
| `open=false` / `open="false"` | String `"false"`, not a boolean. |
| `#check` / `id=check` | Exact node ID `"check"`. |

Whitespace and an optional `&` separate entries. These are equivalent:

```md
{highlight=1,3-4 show-line-numbers}
{highlight=1,3-4 & show-line-numbers}
```

Values can be unquoted or single/double-quoted. Quote spaces and literal
ampersands: `{label="Research & development"}`. Assigned values stay strings.
Source names are case-insensitive; dash-separated names become camelCase AST
keys, such as `show-line-numbers` → `showLineNumbers`.

Duplicate attributes are valid: **the last occurrence wins**, including ID
shorthand versus assignment. Tools should warn. Authored IDs retain their exact
spelling, even when duplicated; they are not automatically renumbered.

### Attaching attributes

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 placement=center responsive}
[Release notes](release.md){class="release-link"}
```

Heading attributes are final and whitespace-separated. Image/link attributes
are immediately adjacent. All attachments stay on the same source line.
Escape `{` to write literal text. Other block styling uses supported safe HTML.

**Recommended HTML:** use native attributes where supported; map custom
attributes to `data-*`. Custom true flags are present/empty; false flags are
omitted. Native boolean attributes follow HTML presence: an assigned string
`"false"` still enables them. See the [attribute conversion rules](/expressive-markdown/parsing#attributes-and-identity).

## YAML frontmatter

```yaml
---
id: deployment-guide
title: "Deploying **safely**"
description: "A guide to *repeatable* deployments."
tags: [deployment, operations]
custom:
  owner: platform
---
```

Optional YAML frontmatter starts the document between `---` lines. Standard
fields have shared meanings; custom fields remain valid.

| Field | Meaning |
| --- | --- |
| `id` | Exact document identity. |
| `title` | Inline-Markdown document title. |
| `description` | Inline-Markdown description. |
| `tags` | List of strings. |
| Other keys | Preserved document metadata. |

A title or description can be projected to readable text for navigation or SEO.
Use YAML 1.2 Core scalars and JSON-compatible values: `yes`/`on` remain strings;
null remains data. Frontmatter adds no body HTML. The [publishing profile](/expressive-markdown/publishing)
defines optional navigation labels and hidden pages.

## Leading-pipe line blocks

Use a leading pipe when line divisions are part of the content:

```md
| First line
| Second line
|
| Fourth line
```

`| ` starts a preserved line; a bare `|` requests an empty one. `|Text` stays
ordinary text. Source indentation is stripped, not displayed.

Long lines can wrap onto an indented continuation:

```md
| One sentence wrapped
  across source lines.
| Another represented line.
```

The continuation joins with one space. An unindented, unmarked line ends the
block. Formatting can span represented lines; inline code stays within one.

| Spacing | Result |
| --- | --- |
| Blank source line between pipe lines | One empty represented line. |
| Blank source line at a block boundary | Ordinary paragraph spacing. |
| Bare pipe at a boundary | An extra empty line in addition to ordinary spacing. |

**Recommended HTML:** a paragraph with `<br>` boundaries, retaining inline
formatting. See [terminal empty-line handling](/expressive-markdown/parsing#leading-pipe-line-blocks).

> [!note] Why a leading pipe?
> The marker is visible and sits on the affected line. CommonMark's trailing
> spaces are invisible; its trailing backslash breaks a line where languages
> such as Python use one to continue it. Both forms remain accepted for
> compatibility; Expressive writers prefer line blocks.

## Code blocks and presentation metadata

````md
```ts {title="deploy.ts" & highlight=1,3-4 & show-line-numbers}
const mode = "safe";
await check();
await deploy();
await verify();
```
````

This captions the example **deploy.ts**, highlights **line 1 and lines 3 through
4**, and shows line numbers. A comma separates selections; a hyphen means
“through.” Line highlighting is separate from syntax coloring.

| Setting | Stored data / default |
| --- | --- |
| `title="deploy.ts"` | Literal string `code.title`; no duplicate attribute. |
| `highlight=1,3-4` | String `attributes.highlight`; one-based, inclusive ranges. Default: none. |
| `show-line-numbers` | Boolean `attributes.showLineNumbers: true`. Default: hidden. |
| `!show-line-numbers` | Explicit false. |

The language follows the opening fence; named settings use the same `{…}`
attribute grammar as other features. Code remains literal text. Unknown info
string tokens remain in `meta`; annotation comments remain part of the code.
See [validation and writing rules](/expressive-markdown/parsing#code-presentation).

**Recommended HTML:** escaped `<pre><code class="language-ts">…</code></pre>`,
optionally captioned and decorated. Keep generated line numbers out of copied
code. Colors and copy controls belong to the renderer.

## Ordinary Markdown segments

CommonMark/GFM supply familiar Markdown. Parsed text values are literal content,
not Markdown to parse again.

| Segment | Recommended HTML |
| --- | --- |
| Text, paragraph, heading | Escaped text, `<p>`, `<h1>`–`<h6>`. |
| Emphasis, strong, strikethrough | `<em>`, `<strong>`, `<del>`. |
| Inline code | Escaped `<code>`. |
| Hard / soft break | `<br>` / normal inline whitespace. |
| Horizontal rule, block quote | `<hr>`, `<blockquote>`. |
| Lists and items | `<ul>` / `<ol start="…">`, `<li>`; task items add disabled labelled checkboxes. |
| Link, image | `<a href="…" title="…">`, `<img src="…" alt="…">`. |
| Safe HTML | Supported markup after filtering. |

Reference-style and inline links produce the same nodes. Unresolved references
use CommonMark's literal fallback. An isolated image stays in its paragraph;
only an explicit figure supplies a caption, separate from image alternative text.

Image `width`/`height` are positive integer CSS-pixel strings. `placement` is
`center`, `wrap-left` or `wrap-right`, with ordinary flow as the default.
`responsive` permits host-selected renditions; loading and URL selection belong
to the renderer.

HTML uses a maintained sanitizer allowlist for elements, attributes and URLs.
`script` elements **and their contents** are discarded during parsing and never
serialized again. Supported safe HTML can become structured nodes, including
`underline`/`highlight` for `<u>`/`<mark>`. Other safe markup can remain an `html`
node. Report filtering losses; unsafe discarded content is outside preservation.
The exact sanitizer preset remains to be selected.

## Tables

GFM tables support headers, alignment and inline cells. Marker-only cells add
merging:

```md
| First | Second | Status |
| --- | --- | --- |
| > | Release checks | Ready |
| ^ | ^ | Verified |
```

“Release checks” spans two columns and two rows.

| Cell | Meaning |
| --- | --- |
| `>` | Merge right into the next ordinary cell. |
| `^` | Continue the cell above. |
| Empty | Empty content, not a merge. |
| `\>` / `\^`, or inline code | Literal marker. |

Tight `|>`/`|^` forms work too. Merges must be rectangular, cover every lower slot
with `^`, and stay within the header or body. Invalid merges preserve the whole
table source instead of guessing. The AST stores numeric `colSpan`/`rowSpan`,
not placeholder cells.

**Recommended HTML:** native tables with spans and supported presentation. Rich
cells can hold blocks and styling; use supported safe HTML or report a
conversion limitation when pipe syntax is insufficient. Never flatten cells
silently. See [grid rules](/expressive-markdown/parsing#tables).

## Recognized container semantics

All these types use the same container syntax, with optional inline-formatted
title and a block body. Types are case-insensitive and open to extensions.

| Type | Meaning | Recommended HTML |
| --- | --- | --- |
| `note` | Context worth noticing. | Labelled `<section data-type="note">`. |
| `tip` | Practical advice for the task. | Labelled `<section data-type="tip">`. |
| `warning` | Potential problem requiring caution. | Labelled `<section data-type="warning">`. |
| `danger` | Critical information warranting maximum attention. | Labelled `<section data-type="danger">`. |
| `details` | Collapsible content. | `<details>` / `<summary>`. |
| `figure` | Self-contained, optionally captioned content. | `<figure>` / `<figcaption>`. |
| `tabs`, `tab` | Alternatives and their labelled content. | Labelled sections; optional interactive tabs. |
| `toc` | Authored section navigation. | `<nav>` with title and body. |
| Custom type | Meaning defined by its extension. | Generic labelled section. |

Use `<header>` for a section title without assuming a heading rank. An absent
title stays absent; a renderer can show a separate type label. Colors/icons are
renderer choices, and static warnings/dangers are not automatically live alerts.
Custom `info`, `important` or `caution` types are valid, not aliases for core types.

### Details

```md
::: details [Show the full log] {open}
The build finished successfully.
:::
```

Absent `open` or `{!open}` recommends a collapsed disclosure; `{open}` recommends
expanded. Any assigned string, including `{open="false"}`, enables native HTML
boolean presence. A missing title can use the control label “Details” without
adding a title to the AST.

### Figure

```md
::: figure [Deployment overview]
![Services and connections](deployment.svg)
:::
```

The title is a caption, distinct from image alternative text. Bodies can hold
images, tables, diagrams or code. Recommend the caption after the body; numbering
and caption styling are renderer choices, with no automatic “Figure 1” prefix.

### Tabs

Consecutive tabs automatically form a group, even with blank lines between them:

````md
::: tab [npm]
```sh
npm install example-package
```
:::

::: tab [pnpm]
```sh
pnpm add example-package
```
:::
````

Another content block ends the group. Grouping stays within one block context,
never across list items, quotes or enclosing containers. A single tab forms a
group too. Explicit neighbouring groups remain separate.

Use an outer container for shared settings:

```md
:::: tabs {group=language & default=js}
::: tab [JavaScript] {value=js}
JavaScript example.
:::
::: tab [TypeScript] {value=ts}
TypeScript example.
:::
::::
```

| Setting | Meaning/default |
| --- | --- |
| Tab `value` | String selection identity; default title's readable text. Duplicates retain all tabs; first match wins. |
| Group `group` | Synchronization name. Matching groups select the same value; a group without that value keeps its choice. |
| Group `default` | Initial selection value; otherwise first tab. Unknown values recommend a diagnostic and select the first tab. |
| Group `query-string` | True uses `group` as parameter name; a string names the parameter. Query selection precedes remembered selection, then authored default. |
| Group `lazy` | Rendering intent; every tab body remains in document data. |

A group title is optional and is not a synchronization key. Tab titles support
inline Markdown; bodies hold ordinary blocks and nested containers. Unnamed
automatic groups do not implicitly synchronize. Remembering choices across
pages belongs to the renderer.

**Recommended HTML:** labelled sections showing all content without JavaScript.
Interactive renderers supply accessible tab roles, keyboard operation and
control/content relationships. See [rendering recommendations](/expressive-markdown/presentation#selection-state-and-identity).

### Chips and mentions

```md
Status: :chip[Ready]{tone=green}.
Thanks, @[Ada Lovelace].
Thanks, @ada-lovelace#user-123.
```

A **chip** is a compact category/status label. `tone` suggests neutral, blue,
green, yellow, red or purple. Preserve custom tones; use neutral fallback when
unsupported. Recommend a labelled `<span>` where color supplements the text.

A **mention** names a person or entity. `@[Ada Lovelace]` and `@ada-lovelace` are
valid without a stored target; bracketed labels can use inline formatting.
`:mention[Ada Lovelace]` uses the general inline syntax.

```md
@[Ada Lovelace]#user-123{#acknowledgement}
```

Here `user-123` is the target (`node.ref`); `acknowledgement` identifies this
occurrence (`node.id`). The suffix is part of the mention, not a generic ID.
Use `{ref="org/user-123"}` for a target that needs more characters. An optional
`url` attribute supplies navigation. Hosts can resolve names without inventing
stored references or changing labels.

Bare handles end outside letters, numbers, combining marks, `_` and `-`.
Emails, URLs, code and escaped `\@` stay ordinary content. Recommend a labelled
span, or link when a URL is present, with an optional visible `@`.
See [complete mention boundaries](/expressive-markdown/parsing#mention-shorthand).

### Table of contents

```md
::: toc [On this page] {depth=3 format=bulleted}
- [Installation](#installation)
- [Configuration](#configuration)
:::
```

A table of contents holds readable authored links, normally a nested list.
Plain format can use paragraph/link content. Empty bodies are incomplete:
preserve them and recommend a diagnostic.

| Refresh setting | Meaning/default |
| --- | --- |
| `depth` | String maximum heading level 1–6; default `3`. |
| `format` | `plain`, `bulleted` or `numbered`; default `bulleted`. |
| Invalid value | Preserve, recommend a diagnostic, use the refresh default. |

Rendering keeps the saved entries. An explicit refresh or configured editor
policy can update them using heading text, order and hierarchy, excluding
headings inside the TOC. Refresh writes real entries back to source and AST;
settings alone do not rewrite authored list markers. Scope/minimum-level
settings are extensions.

Links must reach actual anchors. Converters keep changed targets and links
consistent and report unresolved targets. Recommend `<nav>` labelled by its
authored title, or `aria-label="Table of contents"` when absent, without imposing
a heading rank.

### Text styling, diagrams and math

Keep supported classes/styles on images, cells and HTML; report filtered or
unsupported presentation. No CSS framework is prescribed.

Extensions can use `mermaid`/`math` code fences or inline notation such as
``:math[`x_1^2`]``. Retain the notation for editing and escaped fallback. These
are extension contracts, not additional core semantic types.

## Recommended output anchors

Authored IDs stay exact. The [anchor algorithm](/expressive-markdown/parsing#recommended-output-anchors)
derives Unicode-preserving, collision-numbered output IDs without inserting
implicit IDs into the AST.

## Recovery and diagnostics

Unknown types/keys and duplicate attributes are valid. Invalid structures
preserve recoverable source; diagnostics remain separate from content.
See [recovery rules](/expressive-markdown/parsing#recovery-and-diagnostics).

## Writing and preservation

Writers preserve meaning, order, IDs, metadata, supported presentation and
explicit lines. Byte-identical output is optional. Discarded unsafe HTML is
outside preservation. See [canonical writing](/expressive-markdown/parsing#writing-and-preservation).

## Conformance and scope

The base is [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) with
[GFM](https://github.github.com/gfm/) tables, tasks, strikethrough and extended
autolinks. Expressive rules override that base where specified. “Must” is
required, “should” recommended and “may” optional. Parsing, meanings, AST data
and preservation form the contract; HTML output is informative.

### Parsing order

Parse blocks before inline content. Code/HTML retain their lexical boundaries;
their contents do not open directives. GFM tables take precedence over line
blocks. See [parser order](/expressive-markdown/parsing#parsing-order).

### Recognized semantic subtypes

| Family | Standard types |
| --- | --- |
| `container` | `note`, `tip`, `warning`, `danger`, `details`, `figure`, `tabs`, `tab`, `toc`. |
| `inline` | `chip`, `mention`. |

AST subtypes use lowercase. Unknown types retain their name, attributes and
content without claiming a recognized meaning. Inline scope does not prescribe
CSS display. JavaScript execution, MDX/JSX and framework APIs are outside the core.

## Prior-art comparison

| Prior art | Adopted idea | Expressive's contract |
| --- | --- | --- |
| [CommonMark/GFM](https://github.github.com/gfm/) | Ordinary Markdown. | Adds documented documentation features and data. |
| [Docusaurus](https://docusaurus.io/docs/markdown-features/admonitions) | Callouts and nested colon fences. | Independent of MDX, components and themes. |
| [remark directives](https://github.com/remarkjs/remark-directive) | Inline, leaf and container forms. | Shared meanings, fields and string/flag rules. |
| [Pandoc](https://pandoc.org/MANUAL.html#pandocs-markdown) | IDs and leading-pipe lines. | Defined line boundaries without visual source indentation. |
| [UMD](https://docs.rs/crate/umd/0.2.0/source/README.md) | Cell merge markers. | Rectangular grid, numeric spans and loss-preserving recovery. |
| [MyST](https://mystmd.org/guide/figures) / [Quarto](https://quarto.org/docs/authoring/figures-and-layout.html#figure-divs) | Structured figures and captions. | Shared container family with explicit subtype meanings. |
| [mdast](https://github.com/syntax-tree/mdast) / [unist](https://github.com/syntax-tree/unist) | Documented trees. | Independent title/body/children/value fields and traversal. |

Other feature references: [YAML 1.2.2](https://yaml.org/spec/1.2.2/),
[Jekyll frontmatter](https://jekyllrb.com/docs/front-matter/),
[Kramdown attributes](https://kramdown.gettalong.org/syntax.html#inline-attribute-lists),
[HTML attributes](https://html.spec.whatwg.org/multipage/syntax.html#attributes-2),
[CommonMark hard breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks),
[Python line joining](https://docs.python.org/3/reference/lexical_analysis.html#explicit-line-joining),
[Docusaurus code](https://docusaurus.io/docs/markdown-features/code-blocks),
[VitePress line highlighting](https://vitepress.dev/guide/markdown#line-highlighting-in-code-blocks)
and [Shiki annotations](https://shiki.style/packages/transformers#transformernotationhighlight).
