---
title: Language & Semantics
order: 1
blurb: syntax · meaning · HTML guidance
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Language & Semantics

Familiar Markdown, with named documentation constructs, shared attributes and explicit line breaks. Start with the forms below; the [AST reference](/expressive-markdown/ast) defines their document data.

```md
::: warning [Before deploying] {#deployment-check}

Back up the database first.

:::

Status: :chip[Ready]{tone=green}.
```

| Write | Meaning |
| --- | --- |
| `:chip[Ready]{tone=green}` | An inline construct with a readable label. |
| `::type{attributes}` | A standalone construct without a body. |
| `::: warning [Title] {attributes}` … `:::` | A container with block content. |
| `{#check open audience=admin}` | An ID, a true flag and a string attribute. |
| `\| First line` followed by `\| Second line` | Two explicitly preserved lines. |

> [!note] One attribute grammar
> Named attributes belong inside `{…}`. A colon introduces a named construct; it is not an alternative flag prefix. Other Markdown implementations are prior art, not additional Expressive grammars.

## Named constructs

```md
:::warning[Before deploying]{#check}
::: warning {#check} [Before deploying]
```

These open the same container. Spaces around header parts are optional; wrappers are tight inside. Keep the header on **one source line**, type first, with title and attributes in either order. Titles and labels support inline Markdown. Writers prefer `::: type [Title] {attributes}`.

Inline forms use `:type[label]{attributes}`; bodyless blocks use `::type[label]{attributes}` on their own line. Bare `:word` remains text: an inline construct needs a label or attributes.

**Nesting uses longer outer fences:**

```md
:::: note [Outer]

::: warning [Inner]
Check the configuration.
:::

::::
```

Use at least three colons, with fewer for a directly nested container. Close with the matching colon run. Lists, quotes and code may appear inside.

> [!note] Readable spacing adds no blank line
> Blank source lines immediately inside container fences are ordinary spacing. Use a [line block](#leading-pipe-line-blocks) to request visible empty lines.

[Full grammar](/expressive-markdown/parsing#named-constructs) covers identifiers, escaping, indentation and repeated wrappers.

## Attributes and identity

```md
{#deployment-check open audience=admin label="Before deploying"}
```

| Source | Meaning / AST value |
| --- | --- |
| `open` / `!open` | Boolean `true` / `false`. |
| `open=foo` | String `"foo"`. |
| `open=false` / `open="false"` | String `"false"`, never boolean. |
| `#check` / `id=check` | Exact node ID `"check"`. |

Separate entries with whitespace, an optional `&`, or both:

```md
{highlight=1,3-4 show-line-numbers}
{highlight=1,3-4 & show-line-numbers}
```

Both mean the same thing. Attribute names are case-insensitive in source; dash-separated words become camelCase AST keys: `show-line-numbers` → `showLineNumbers`. Values may be unquoted or single/double-quoted; assigned values stay strings. Quote a literal ampersand, as in `{label="Research & development"}`. Unknown attributes follow the same mapping.

> [!note] Duplicates are valid
> Repeated attributes use **last occurrence wins**, including ID shorthand versus assignment. Recommend a warning. Authored IDs are never normalized or renumbered.

Attributes attach to named constructs and code fences, or to ordinary Markdown as shown:

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 placement=center responsive}
[Release notes](release.md){class="release-link"}
```

Heading attributes are final and whitespace-separated; image/link attributes are immediately adjacent. Attachments stay on the same source line. Escape `{` for literal text. Other block styling uses native HTML; there is no `.class` shorthand.

**Recommended HTML:** map supported native attributes directly and custom attributes to `data-*`. Custom true flags are present/empty; false flags are omitted. Native boolean attributes follow HTML presence, so even an assigned string `"false"` enables them. See [quoting, AST identity and conversion details](/expressive-markdown/parsing#attributes-and-identity).

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

Optional YAML frontmatter starts the document between `---` lines. Standard fields have defined meanings; custom keys remain valid.

| Field | Meaning |
| --- | --- |
| `id` | Exact document identity. |
| `title` | Inline-Markdown title; readable text can be derived for navigation or SEO. |
| `description` | Inline-Markdown description, also usable as readable text. |
| `tags` | List of strings. |
| Other keys | Preserved document metadata. |

Use YAML 1.2 Core scalars and JSON-compatible values. `yes`/`on` remain strings; null remains data. See [boundaries, data mapping and invalid YAML](/expressive-markdown/parsing#yaml-frontmatter). Frontmatter emits no body HTML.

## Leading-pipe line blocks

```md
| First line
| Second line
|
| Fourth line
```

Start each preserved line with `| `; a bare `|` requests an empty line. `|Text` stays ordinary text. Source indentation is stripped rather than displayed.

```md
| One sentence wrapped
  across source lines.
| Another represented line.
```

An indented continuation joins the previous represented line with one space. An unindented, unmarked line ends the block. Inline formatting may span represented lines; code spans stay within one.

| Spacing | Result |
| --- | --- |
| Blank source line between pipe lines | One empty represented line. |
| Blank source line at a block boundary | Ordinary paragraph spacing. |
| Bare pipe at a block boundary | An explicit empty line **in addition to** ordinary spacing. |

**Recommended HTML:** `<p>` with `<br>` boundaries, retaining formatting. [Boundary and AST rules](/expressive-markdown/parsing#leading-pipe-line-blocks) define empty-line preservation.

> [!note] Why a leading pipe?
> It marks the affected line visibly. CommonMark's trailing spaces are invisible, and its trailing backslash breaks a line where other languages use one to continue it. Those hard-break forms remain accepted for compatibility; writers prefer line blocks.

## Code blocks and presentation metadata

````md
```ts {title="deploy.ts" & highlight=1,3-4 & show-line-numbers}
const mode = "safe";
await check();
await deploy();
await verify();
```
````

`1,3-4` means **line 1 and lines 3 through 4**. The comma separates selections; the hyphen means “through.” This highlights entire lines, separately from syntax coloring.

| Source attribute | AST | Meaning |
| --- | --- | --- |
| `title="deploy.ts"` | `code.title: "deploy.ts"` | Literal caption, not duplicated in attributes. |
| `highlight=1,3-4` | `attributes.highlight: "1,3-4"` | One-based, inclusive line selection. |
| `show-line-numbers` | `attributes.showLineNumbers: true` | Show line numbers. |
| `!show-line-numbers` | `attributes.showLineNumbers: false` | Hide line numbers. |

```json
{
  "type": "code",
  "language": "ts",
  "title": "deploy.ts",
  "value": "const mode = \"safe\";\nawait check();\nawait deploy();\nawait verify();",
  "attributes": {"highlight": "1,3-4", "showLineNumbers": true}
}
```

The language follows the opening fence; all named attributes use the shared `{…}` grammar. Code remains literal `value`. Unknown info tokens stay in `meta`; annotation comments stay in code source rather than acquiring another core grammar. Writers regenerate known fields and append unknown tokens. See [code-setting validation](/expressive-markdown/parsing#code-presentation).

**Recommended HTML:** escaped `<pre><code class="language-ts">…</code></pre>`, optionally captioned, with highlighted line wrappers and line-number labels outside copied code. Omitted settings mean no emphasized lines or line numbers in the baseline conversion. Colors and copy controls belong to the renderer. Use safe CommonMark backtick/tilde fences.

## Ordinary Markdown segments

CommonMark/GFM define these familiar segments. Their [AST fields](/expressive-markdown/ast#content-node-reference) are documented separately; parsed `value` is literal content, never Markdown to parse again.

| Segment | Recommended HTML |
| --- | --- |
| Text | Escaped text. |
| Paragraph | `<p>`. |
| Heading | Corresponding `<h1>`–`<h6>`. |
| Emphasis / strong | `<em>` / `<strong>`. |
| Strikethrough | `<del>` for removed/no-longer-current content. |
| Inline code | Escaped `<code>`. |
| Hard / soft break | `<br>` / normal inline whitespace. |
| Horizontal rule | `<hr>` separating document sections. |
| Block quote | `<blockquote>`. |
| List | `<ul>` / `<ol start="…">`. |
| List item | `<li>`; task items add a disabled, labelled checkbox. |
| Link | `<a href="…" title="…">`. |
| Image | `<img src="…" alt="…">`. |
| Raw HTML | Authored markup under the declared host policy. |

Relative/absolute and reference-style links use the same semantic nodes. Resolve CommonMark definitions; unresolved references keep CommonMark's literal fallback. Writers may use inline destinations; exact reference spellings belong to optional source provenance.

An isolated image stays in its paragraph. Only an explicit figure supplies a caption; `alt` remains distinct. Image `width`/`height` are positive integer CSS-pixel strings; `placement` is `center`, `wrap-left` or `wrap-right` (default ordinary flow); `responsive` permits host renditions. Loading and URL selection belong to rendering.

HTML `<u>`/`<mark>` may map to `underline`/`highlight` with inline content and preserved attributes. Other HTML may remain opaque `html`. Hosts declare their rendering policy and report removed presentation separately from parsing; preserving source does not require executing it.

## Tables

Use GFM tables for headers, alignment and inline cells. Marker-only cells add merging:

```md
| First | Second | Status |
| --- | --- | --- |
| > | Release checks | Ready |
| ^ | ^ | Verified |
```

| Cell | Meaning |
| --- | --- |
| `>` | Merge right into the next ordinary cell. |
| `^` | Continue the cell above. |
| Empty | Empty content, not a merge. |
| `\>` / `\^`, or inline code | Literal marker. |

“Release checks” spans two columns and two rows. Tight `|>`/`|^` forms also work. Merges must form rectangles; every covered lower slot needs `^`. Never cross the header/body boundary. Invalid merges preserve the table source rather than guessing.

The AST uses numeric `colSpan`/`rowSpan`, not placeholder cells. Rich cells can contain blocks and retain styling attributes. Use native HTML when pipe syntax cannot preserve the content; report unsupported conversions.

**Recommended HTML:** `<table>` with header/body rows, `<th>`/`<td>`, spans and supported presentation. Never silently flatten merged cells. See [grid validation and serialization](/expressive-markdown/parsing#tables).

## Recognized container semantics

Every type below shares the `container` family. Titles use inline Markdown; the body contains blocks.

| Type | Meaning | Recommended HTML |
| --- | --- | --- |
| `note` | Context worth noticing. | `<section data-type="note">`. |
| `tip` | Practical advice for the task. | `<section data-type="tip">`. |
| `warning` | Potential problem requiring caution. | `<section data-type="warning">`. |
| `danger` | Critical information warranting maximum attention. | `<section data-type="danger">`. |
| `details` | Collapsible content. | `<details>` / `<summary>`. |
| `figure` | Self-contained content, optionally captioned. | `<figure>` / `<figcaption>`. |
| `tabs`, `code-group` | Labelled alternatives. | Labelled sections; optional accessible tabs. |
| `toc` | Authored section navigation. | `<nav>` with title and body. |
| Custom type | Meaning supplied by its profile. | `<section data-type="custom-type">`. |

Section titles recommend `<header>` content, without an arbitrary heading rank. An accessible name may use a generated label ID. An absent title stays absent; a renderer may separately show a type label. Static warnings/dangers do not automatically acquire a live-region `alert` role.

Callout colors, icons and labels are suggestions for renderers. `danger` does not imply a particular consequence. Custom types need no format-branded HTML tags.

### Details

```md
::: details [Show the full log] {open}
The build finished successfully.
:::
```

| `open` form | AST | Recommended disclosure state |
| --- | --- | --- |
| Absent | Absent | Collapsed. |
| `{open}` | `true` | Expanded. |
| `{!open}` | `false` | Collapsed. |
| `{open=foo}` or `{open="false"}` | String | Expanded: native HTML boolean presence. |

Recommend `<details><summary>…</summary>…</details>`, adding `open` when enabled. A missing title may use the control label “Details” without adding an AST title.

### Figure

```md
::: figure [Deployment overview]
![Services and connections](deployment.svg)
:::
```

The title is an inline-formatted caption. Bodies may contain images, tables, diagrams or code. Recommend `<figcaption>` after the body; image `alt` remains separate. Caption styling and optional numbering belong to the renderer; default conversion adds no “Figure 1” prefix.

### Tabs and code groups

````md
::: tabs [Installation] {group=package-manager default=pnpm}
== [npm] {value=npm}
```sh
npm install example-package
```
== [pnpm] {value=pnpm}
```sh
pnpm add example-package
```
:::
````

Within `tabs`/`code-group`, block-level `== Label` or `== [Label]` starts a panel. The label is inline Markdown; optional `{value=…}` supplies selection identity. Code markers do not split panels; outside these containers, `==` keeps its ordinary Markdown meaning. Panel bodies support blocks and nested containers.

| Setting | Meaning/default |
| --- | --- |
| Panel `value` | String selection identity; default plain-text title. Duplicate values keep all panels; first match wins. |
| Container `group` | Related selection group, distinct from the display title. |
| `default` | Initial panel value. Missing/unknown defaults select the first panel; unknown values recommend a diagnostic. |
| `query-string` | True flag uses `group` as parameter name; a string supplies the name. Query selection precedes stored group selection, then authored default. |
| `lazy` | Presentation intent interpreted by the interactive profile. |

A `panel` node has structured `title` and block `body`. Consecutive code fences in a code group may infer panel labels from code caption, then language, then localized fallback. Keep code nodes in the authored body: inferred panels are a presentation view. Writers retain fences or emit explicit panels when needed.

**Recommended HTML:** labelled sections showing all content without JavaScript. Interactive profiles provide tab roles, keyboard operation and relationships; inactive panels remain reachable through controls. Persistence is profile behavior, not an AST mutation.

### Chips and mentions

```md
Status: :chip[Ready]{tone=green}.
Thanks, @[Ada Lovelace].
Thanks, @ada-lovelace.
Thanks, @[Ada Lovelace]#user-123.
Thanks, @ada-lovelace#user-123.
```

| Type | Meaning | Recommended HTML |
| --- | --- | --- |
| `chip` | Compact category/status label. `tone` suggests neutral, blue, green, yellow, red or purple; preserve custom tones and use neutral fallback when unsupported. | `<span data-type="chip">`; color supplements the label. |
| `mention` | Reference to a person or other entity, with an authored readable name/handle. | Labelled `<span>`, or `<a>` when a URL is available; optional visible `@` prefix. |

`@[Ada Lovelace]` and `@ada-lovelace` are both mentions. A bracketed label supports inline formatting; a bare handle ends at punctuation outside letters/numbers, `_` and `-`. The generic `:mention[Ada Lovelace]` form also works. All use `inline` / `mention` with `value` or inline `children`.

The optional `#user-123` suffix is part of the mention: it supplies the entity target as `node.ref`. It does not become a generic node attribute. The bracketed form produces:

```json
{
  "type": "inline",
  "subType": "mention",
  "value": "Ada Lovelace",
  "ref": "user-123"
}
```

The bare-handle form keeps `value: "ada-lovelace"` instead. Without a target, the mention remains valid and readable. Hosts may resolve names/handles without inventing stored identity or rewriting labels. An optional `url` attribute supplies navigation.

```md
@[Ada Lovelace]#user-123{#acknowledgement}
```

Here `user-123` is the entity reference and `acknowledgement` is this node's own ID. Email addresses, URLs, code and escaped `\@` remain ordinary content. See [mention boundaries and full-string references](/expressive-markdown/parsing#mention-shorthand).

### Table of contents

```md
::: toc [On this page] {depth=3 format=bulleted}
- [Installation](#installation)
- [Configuration](#configuration)
:::
```

A TOC contains readable authored links, normally a nested Markdown list; plain format may use paragraph/link content. It has optional structured `title` and block `body`. Empty bodies are incomplete: preserve and diagnose them. A bodyless `::toc` is not the recognized TOC form.

> [!note] A TOC is saved content
> Rendering preserves the authored entries. An explicit refresh or configured editor/converter policy may update them, writing actual readable entries back into source and AST.

| Refresh setting | Contract |
| --- | --- |
| `depth` | String maximum heading level 1–6; default `3`. |
| `format` | `plain`, `bulleted` or `numbered`; default `bulleted`. |
| Invalid setting | Preserve, recommend a diagnostic, use the refresh default. |

Refresh uses readable heading text, document order and hierarchy, omitting headings inside the TOC. Scope/minimum-level settings are extensions. Settings do not rewrite authored list markers until refresh.

Links must reach actual anchors or authored IDs; the [recommended algorithm](#recommended-output-anchors) can supply output targets without adding authored AST IDs. Converters keep changed targets and TOC links consistent, reporting unresolved targets.

**Recommended HTML:** `<nav>` containing the authored body. An authored title labels it through `aria-labelledby`; otherwise a converter may use `aria-label="Table of contents"`. The title is a navigation label, without an automatic heading rank.

### Text styling, diagrams and math

Preserve authored classes/styles on images, table cells and HTML. Both target profiles expose them to renderers and report unsupported presentation; no CSS library or component framework is prescribed.

Diagram/math profiles may use `mermaid`/`math` code fences. An inline math extension such as ``:math[`x_1^2`]`` retains notation in an inline-code child. These are profile contracts, not extra core semantic subtypes. Specialized rendering keeps literal source available for escaped fallback; the core need not execute diagram languages or typeset math. See [presentation coverage](/expressive-markdown/presentation).

## Recommended output anchors

Authored IDs stay exact. The [recommended algorithm](/expressive-markdown/parsing#recommended-output-anchors) derives Unicode-preserving, collision-numbered output IDs without writing implicit identity into the AST.

## Recovery and diagnostics

Unknown types/keys and duplicate attributes are valid. Invalid structures preserve recoverable source; diagnostics stay separate from body content. See the [recovery table](/expressive-markdown/parsing#recovery-and-diagnostics).

## Writing and preservation

Writers preserve meaning, order, IDs, metadata, presentation and explicit line divisions. Byte-identical output is an optional stronger guarantee. See [canonical writing rules](/expressive-markdown/parsing#writing-and-preservation).

## Conformance and scope

This Stage 0 editor's draft builds on [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) and [GFM](https://github.github.com/gfm/) tables, task lists, strikethrough and extended autolinks. Rules here override that base where specified. JavaScript execution and framework-specific source languages are outside the core.

“Must” means required, “should” recommended and “may” optional. Parsing, meaning, AST data and preservation form the language contract. Parsers produce the [document AST](/expressive-markdown/ast); writers produce equivalent source; renderers document their presentation profile.

> [!note] HTML is guidance
> All HTML mappings are informative. Colors, icons and labels belong to the renderer; HTML output is not required for language conformance. This draft does not claim an implemented conforming parser.

### Parsing order

Block structure is recognized before inline content. Code and HTML retain their own lexical rules; their contents do not open directives. GFM tables take precedence over line blocks. See [parser boundaries](/expressive-markdown/parsing#parsing-order).

### Recognized semantic subtypes

| Family | Recognized `subType` | Meaning |
| --- | --- | --- |
| `container` | `note`, `tip`, `warning`, `danger` | Context, advice, caution, maximum-attention information. |
| `container` | `details`, `figure` | Disclosure; self-contained captionable content. |
| `container` | `tabs`, `code-group` | Labelled alternative content/code panels. |
| `container` | `toc` | Authored heading navigation that tools may refresh. |
| `inline` | `chip`, `mention` | Category/status label; labelled entity reference. |

Types are **open and case-insensitive**, with lowercase AST spellings. A supported recognized subtype keeps the meaning defined below. Unknown types preserve their name, attributes and content for a generic fallback or explicit handler; parsing their structure does not imply understanding their meaning. `info`, `important` and `caution` are valid custom types, not aliases for the four standard callouts. Inline scope does not prescribe CSS display.

## Prior-art comparison

| Format/convention | Adopted idea | Expressive distinction |
| --- | --- | --- |
| [CommonMark](https://spec.commonmark.org/0.31.2/) / [GFM](https://github.github.com/gfm/) | Ordinary Markdown and established table/list/link behavior. | Named semantic constructs, frontmatter and explicit line blocks have additional contracts. |
| [Docusaurus](https://docusaurus.io/docs/markdown-features/admonitions) | Bracketed callout titles, nested colon fences, rich documentation presentation. | Framework-independent syntax/data; open semantic types; optional spacing; no MDX runtime requirement. |
| [remark directives](https://github.com/remarkjs/remark-directive) | Inline/leaf/container scope and an open named vocabulary. | Standard meanings, generic AST fields and a defined flag/string distinction. |
| [UMD](https://docs.rs/crate/umd/0.2.0/source/README.md) | Compact `>`/`^` table-merge markers. | Defined rectangular grid, structural span fields and loss-preserving recovery; no claim of parser equivalence. |
| [Pandoc attributes](https://pandoc.org/MANUAL.html#extension-header_attributes) / [line blocks](https://pandoc.org/MANUAL.html#line-blocks) | Attribute IDs and leading-pipe line blocks. | Inline/line boundaries survive without preserving source indentation as visual indentation. |
| [MyST](https://mystmd.org/guide/figures) / [Quarto](https://quarto.org/docs/authoring/figures-and-layout.html#figure-divs) | Structured documentation and figures with captions. | The shared container family uses `subType`; language meaning and HTML guidance are separate. |
| [mdast](https://github.com/syntax-tree/mdast) / [unist](https://github.com/syntax-tree/unist) | Documented node meanings and predictable tree tooling. | Independent `title`/`body`/`children`/`value` contract; compact literal nodes; no adapter commitment. |
| Rich editors | Stable identities and content/presentation preservation. | Generic IDs are separate from entity references and renderer-generated control IDs. |

This comparison identifies reusable ideas, not a claim of complete source
compatibility. Product-specific JSX, scripts, source aliases and theme APIs
require their own integration contracts. Continue with the
[AST reference](/expressive-markdown/ast),
[presentation coverage](/expressive-markdown/presentation) and
[publishing profile](/expressive-markdown/publishing).

Other source contracts: [YAML 1.2.2](https://yaml.org/spec/1.2.2/), [Jekyll](https://jekyllrb.com/docs/front-matter/) and [Quarto frontmatter](https://quarto.org/docs/authoring/front-matter.html); [Kramdown attributes](https://kramdown.gettalong.org/syntax.html#inline-attribute-lists); [HTML attributes](https://html.spec.whatwg.org/multipage/syntax.html#attributes-2), [figures](https://html.spec.whatwg.org/multipage/grouping-content.html#the-figure-element) and [line breaks](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-br-element); [CommonMark hard breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks) and [Python line joining](https://docs.python.org/3/reference/lexical_analysis.html#explicit-line-joining).

Code-presentation prior art: [Docusaurus](https://docusaurus.io/docs/markdown-features/code-blocks), [VitePress](https://vitepress.dev/guide/markdown#line-highlighting-in-code-blocks) and [Shiki annotations](https://shiki.style/packages/transformers#transformernotationhighlight). Interactive/presentation guidance: [Docusaurus tabs](https://docusaurus.io/docs/markdown-features/tabs), [ARIA tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/), [diagrams](https://docusaurus.io/docs/markdown-features/diagrams) and [math](https://docusaurus.io/docs/markdown-features/math-equations).
