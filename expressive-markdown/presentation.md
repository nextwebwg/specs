---
title: Presentation Coverage
order: 4
blurb: documentation · rich editing · preservation
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Presentation Coverage

Expressive represents documentation content and authored presentation without
requiring one editor or site generator. This matrix defines the proposed
coverage for **Docusaurus-style documentation** and **rich-document editing**.
It is an acceptance plan for future integrations, not an implementation report.
The [language draft](/expressive-markdown/language) owns syntax/meaning; the [AST](/expressive-markdown/ast)
owns data shapes. This document owns the integration coverage claims.

Full source compatibility with MDX/JSX, component APIs or legacy editor syntax is
outside the selected scope. An importer may translate those sources explicitly.
A renderer can implement the presentation using its own components and CSS.

## Coverage matrix

“Structured” requires editable AST data, not merely a visually equivalent HTML
string. “Preserved” requires retaining data even when the current renderer lacks
a matching treatment. Interactive behavior is a presentation-profile contract,
not a mutation of authored document data.

| Feature | Expressive representation | Docusaurus-style presentation | Rich-editor presentation/editing | Basic HTML fallback |
| --- | --- | --- | --- | --- |
| Headings, paragraphs, quotes, lists, links | Ordinary native AST nodes; compact or structured inline content | Documentation typography, anchors and navigation | Structured block/inline editing | Corresponding native elements |
| Task items | `listItem.checked`, absent for an ordinary item | Checked/unchecked task presentation | Editable task state; mixed ordinary/task lists preserved | Disabled checkbox plus item content |
| Emphasis, strong, deletion | Native inline wrappers | Theme typography | Structured inline marks | `<em>`, `<strong>`, `<del>` |
| Underline and highlight | `underline`/`highlight`, attributes retained | Theme treatment | Editable underline/highlight, including color | `<u>`/`<mark>` |
| Horizontal rules | `horizontalRule` | Section separator | Editable separator | `<hr>` |
| Explicit lines and empty lines | `lineBlock`, ordered inline content and `break` boundaries | Preserve requested lines with normal text styling | Preserve represented lines independently of source wrapping | `<p>` and `<br>` with terminal-line handling |
| Callouts | `container` with open `subType`; standard note/tip/warning/danger | Color/icon/explicit label by theme; formatted title | Structured title/body and presentation settings | Labelled `<section data-type="…">` |
| Other callout names | Preserved custom subtype, including `info` or `important` | Profile can register additional meanings/styles | Preserve and expose custom type | Generic section; preserve content |
| Nested callouts/containers | Container bodies containing containers | Nested treatment | Editable nested blocks | Nested native sections |
| Details | `container/details`, title and `attributes.open` | Disclosure | Editable title/body; positive/negative flag retained | `<details>`/`<summary>` |
| Figures | `container/figure`, structured caption and body | Captioned self-contained unit | Editable body/caption, image alt kept separate | `<figure>`/`<figcaption>` |
| Tabs | `container/tabs`, `panel` nodes | Tab controls, explicit defaults, group synchronization, optional URL/persistence | Editable panels, titles and stable selection values | All panels as labelled sections |
| Code groups | `container/code-group`, explicit panels or consecutive code nodes | Tabbed code variants; labels from caption/language | Editable code variants and group settings | All code blocks visible with labels |
| Fenced code | `code.value`, language, literal string caption | Syntax colors, filename, copy action | Editable literal code; source retained | Escaped `<pre><code>` and caption |
| Code highlights and numbers | String `attributes.highlight` and boolean `attributes.showLineNumbers`; comments remain literal source | Highlighted lines, configurable numbering, custom annotation treatment | Preserve attributes and literal code; imported annotation conventions need explicit mappings | Plain escaped code; optional line decoration |
| Images | URL, alt, tooltip and size/placement/responsive attributes | Responsive images, layout as requested | Editable size, placement and alternative text | Native `<img>` plus supported CSS |
| Inline chips | `inline/chip`, formatted label, tone attribute | Compact status/category label | Editable label and tone | Labelled `<span>` |
| Mentions | `inline/mention`, authored name/handle, optional node `ref` and URL | Entity label or link | Resolve host entity while retaining reference | Label or link without host resolution |
| Table of contents | `container/toc`, readable link/list body, optional title and depth/format settings | Navigation from authored entries; optional converter refresh | Readable editable entries; optional refresh updates actual body/source | `<nav>` with converted authored content |
| Ordinary tables | Table/row/cell nodes, alignment | Documentation table styling | Structured cell editing | Native table |
| Merged cells | Numeric `colSpan`/`rowSpan`; pipe markers in source | Rectangular merged table | Editable merged cell structure | Native `colspan`/`rowspan` |
| Rich cells | Cell `body`; attributes for widths/background/style/class | Structured content with supplied presentation | Block content, widths, backgrounds and alignment retained | Native table with block content |
| Custom classes/styles | Generic `attributes` and styled groups/native nodes | Exposed to theme/CSS | Preserve supported editor styling | Supported native attributes; disclose host filtering |
| Diagrams and math | Literal source in code or inline notation extension | Optional specialized rendering | Preserve editable source or specialized editor view | Escaped notation/code |
| Frontmatter | Root title/ID and JSON-compatible `metadata` | Page metadata, tags and plain-text projections | Document properties with custom keys retained | No implicit body output |
| Unknown types/attributes | Open subtype and preserved attributes | Custom handler or generic fallback | Preserve, even without a specialized control | Preserve readable content and applicable attributes |
| Unsupported HTML | Opaque `html` node with display context | Host policy declared | Preserve source; opaque data is not a claim of structured editing | Host-rendered or escaped source with a diagnostic |

## Selection, state and identity

An interactive tab profile should use the [ARIA tab pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/),
including keyboard operation, selected state and control/panel relationships.
Group synchronization matches **selection values**, not panel order or labels.
If another group has no matching value, retain that group's current choice.
A supplied valid query choice takes precedence over a stored group choice, then
the authored default; absent/invalid choices fall back to the first panel.
Persistence and lazy mounting belong to the profile. Neither can discard hidden
panel content from the document or its exported form.

Renderer-generated tab/control IDs must avoid collisions with authored IDs.
They do not become authored AST IDs. A mention's target reference likewise
remains distinct from its node identity. Application importers must map legacy
entity-ID fields explicitly; they cannot use generic `id` for two purposes.

## Presentation preservation

Store authored class/style data once in `attributes`. Native structural data
such as table spans belongs in its designated AST fields. Importers should
translate known native markup to editable nodes and disclose the exact supported
subset. Keeping an opaque HTML blob is valid preservation, but does not satisfy
an editable rich-table or formatting claim.

When a writer cannot represent data with Markdown shorthand, use supported
native HTML or return an explicit unsupported-conversion diagnostic. Never
flatten merged cells, drop panel content, replace image alt with a caption or
remove a custom semantic type just to produce simpler source.

The scope covers data and presentation capabilities. Toolbar placement, theme
colors, typography, syntax highlighting engines and framework APIs remain
integration choices. Stateful widgets need an actual interactive integration;
static HTML fallback alone does not establish feature parity.

## Required future acceptance fixtures

The future conversion package and each integration should cover these behaviors:

1. Parse, edit and write nested callouts with formatted titles, custom types,
   authored IDs, explicit false flags and duplicate-attribute resolution.
2. Round-trip plain/structured titles, frontmatter metadata and ID mappings;
   preserve custom casing, null metadata and boolean-looking assigned strings.
3. Preserve leading/trailing/internal empty line-block lines, formatting across
   represented lines, wrapped continuations and literal pipe text.
4. Import, edit and write a combined row/column merged table, repeated vertical
   continuations, rich cell bodies and cell styles. Exercise invalid grids and
   escaped marker-only cells without losing source.
5. Keep code captions, range metadata, numbering starts and annotation source;
   verify display/copy code excludes decoration without changing AST value.
6. Exercise tab default/group/query precedence, groups with different available
   values, keyboard operation and exported hidden-panel content.
7. Preserve image alt independently of caption; keep placement and responsive
   intent, chip tone, mention reference and TOC settings/entries. Verify an optional TOC refresh
   writes readable entries back into source and preserves them when refresh is off.
8. Diagnose unsupported conversion and distinguish editable native mappings from
   opaque HTML preservation. Verify host filtering reports information loss.

These are future implementation checks. They do not describe an implemented conversion package.

## Evidence and compatibility limits

Primary references, consulted 2026-10-17:

- [Docusaurus Markdown features](https://docusaurus.io/docs/markdown-features),
  [admonitions](https://docusaurus.io/docs/markdown-features/admonitions),
  [code](https://docusaurus.io/docs/markdown-features/code-blocks) and
  [tabs](https://docusaurus.io/docs/markdown-features/tabs).
- [Shiki notation transformers](https://shiki.style/packages/transformers).
- [UMD table markers](https://docs.rs/crate/umd/0.2.0/source/README.md).
- [Tiptap document model](https://tiptap.dev/docs/editor/core-concepts/introduction)
  as prior art for structured rich-document editing.

Docusaurus supports additional callout names and MDX components; Expressive's
four standard callout meanings do not pretend to cover every custom component.
Open semantic types and explicit integration mappings supply extensibility.
Likewise, representable content does not establish that either product already
imports or renders this proposed format.
