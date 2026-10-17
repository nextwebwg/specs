---
title: Language & Semantics
order: 1
blurb: syntax · meaning · HTML guidance
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Language & Semantics

````md
---
id: deployment-guide
title: "Deploying **safely**"
tags: [deployment, operations]
---

:::: warning [Before deploying] {#deployment-check}

Back up the database first.

::: tip [Check the backup]
Try restoring it in a separate environment.
:::

::::

| Check the release.
| Deploy the change.
|
| Verify the result.
````

Read this chapter for source rules and meaning. The [AST reference](/expressive-markdown/ast) defines the shared document data.

## Conformance and scope

The normative language contract defines source parsing, meaning, AST data and
preservation. “Must” denotes a requirement, “should” a recommendation and “may”
an option. **Every HTML mapping in this draft is informative:** producing HTML
is not required for language conformance. Suggested colors, icons and labels
are renderer choices.

The base is [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) with the
[GFM extensions](https://github.github.com/gfm/) for tables, task-list items,
strikethrough and extended autolinks. Rules below override that base where
specified. They do not introduce JavaScript execution or require a browser to
parse Markdown. Framework-specific source languages have separate contracts.

This is an Unofficial Editor's Draft at Stage 0, not a published parser contract.

A parser produces the AST in [ast.md](/expressive-markdown/ast). A writer accepts that contract
and produces equivalent Expressive Markdown. A renderer consumes the AST and
documents its presentation profile. Recognizing a custom type's structure does
not claim understanding of that type's meaning.

## Syntax and semantics

### Parsing order

Normalize CRLF and CR line endings to LF for parsing. Source offsets refer to
the original input when source locations are retained. Recognize an optional
frontmatter block first, then CommonMark block structure, fenced containers,
leaf directives, tables and line blocks in their enclosing block context.
Parse inline content after identifying block boundaries.

Code spans, fenced/indented code and raw HTML blocks keep their own lexical
rules. Their contents do not open directives or line blocks. A table row already
recognized by the GFM table grammar takes precedence over a leading pipe.
Escaped structural punctuation is literal.

### Recognized semantic subtypes

A structural family describes how content fits in the document. Its `subType`
describes what that construct means. These recognized semantic subtypes have
shared definitions in this draft:

| AST family | Recognized `subType` values | Semantic role |
| --- | --- | --- |
| `container` | `note`, `tip`, `warning`, `danger` | Supplemental context, practical advice, caution and maximum-attention information, respectively. |
| `container` | `details` | Content presented through an authored disclosure/summary. |
| `container` | `figure` | Self-contained content with an optional caption. |
| `container` | `tabs` | Labelled alternative panels of document content. |
| `container` | `code-group` | Related code examples presented as a selectable group. |
| `inline` | `chip` | Compact category/status label. |
| `inline` | `mention` | Reference to an entity with an authored readable label. |
| `container` | `toc` | Authored heading-navigation content that tools may refresh from document headings. |

Their syntax, attributes, defaults and recommended HTML are defined in the
feature sections below. A semantic processor claiming support for a recognized
subtype uses that meaning; a renderer can customize its visual treatment.
An `inline` node belongs in phrasing content but does not prescribe CSS display.
For example, a mention carries an entity reference even when its rendering is
plain text. A styled generic span without such meaning is a separate construct.

The vocabulary is open and case-insensitive. Unlisted subtypes remain valid;
canonical AST spellings are lowercase. Recognizing their structure does not
supply an undocumented semantic contract. For custom types, preserve the label,
attributes and content and provide a generic fallback or an explicit handler.
Names such as `info` and `important` can be custom subtypes; they are not aliases
for one of this draft's four recognized callouts. Code languages such as
`mermaid` and optional math extensions likewise have their own profile contracts
rather than silently joining this registry.

### YAML frontmatter

```yaml
---
id: deployment-guide
title: "Deploying **safely**"
description: "A guide to *repeatable* deployments."
tags: [deployment, operations]
custom:
  owner: platform
  reviewed: true
---
```

Frontmatter is an opening document block between unindented `---` delimiter
lines. The proposed boundary rule accepts a leading Unicode byte-order mark
but no preceding content or blank line. Horizontal whitespace after a delimiter
is accepted. Frontmatter is optional and emits no document-body HTML.

Its top-level value is a mapping with string keys. Empty frontmatter means an
empty mapping. Use YAML 1.2 Core scalar interpretation and JSON-compatible
values: strings, finite numbers, booleans, null, lists and string-keyed objects.
Words such as `yes` and `on` remain strings; quoted scalars remain strings.
Explicit YAML tags, cyclic aliases, non-string keys and non-finite numbers do
not belong to this value profile. Acyclic aliases may resolve to ordinary values;
alias identity is not part of the AST contract.

Keys are case-sensitive. Standard keys have defined contracts; custom keys and
their supported values survive reading and writing. The proposed YAML recovery
default diagnoses duplicate exact keys and uses the final value. This is
recovery from invalid YAML, not a claim that YAML permits duplicate mapping keys.
An unsupported value or invalid YAML block is retained as recoverable source;
it must not be silently discarded or converted to a guessed value.

| Source field | Meaning and AST mapping |
| --- | --- |
| `id` | String document identity → `document.id`, unchanged. |
| `title` | YAML string parsed as inline Markdown → `document.title`, a `title` node. |
| `description` | String containing inline Markdown → `document.metadata.description`; interpret its formatting when deriving display or plain text. |
| `tags` | List of strings → `document.metadata.tags`. No implicit comma splitting. |
| Other keys | Preserved under `document.metadata` with their exact key spelling. |

Each field has one canonical home. `metadata.title` and `metadata.id` do not
duplicate their designated root fields. A custom YAML key named `version`,
`type`, `body` or `metadata` remains a metadata entry; it cannot replace an AST
structural field. For example, YAML `version: product-v2` becomes
`document.metadata.version`, while `document.version` remains integer `1`.

For plain-text projection of title/description, concatenate readable inline
text, use link labels and image alternative text, preserve code text and replace
inline breaks with spaces. Formatting delimiters are not part of that plain
text. The description remains a metadata string, not a hidden AST subtree;
generic content traversal does not visit metadata as nodes.

Prior art: [YAML 1.2.2](https://yaml.org/spec/1.2.2/),
[Jekyll frontmatter](https://jekyllrb.com/docs/front-matter/) and
[Quarto frontmatter](https://quarto.org/docs/authoring/front-matter.html).

### Named constructs

Colon count identifies the authoring scope:

| Form | Scope | AST |
| --- | --- | --- |
| `:type[label]{attributes}` | Inline content | `inline`, with semantic `subType`. |
| `::type{attributes}` | Standalone block without a body | `leaf`, with semantic `subType`. |
| `::: type [Title] {attributes}` … `:::` | Block content | `container`, with semantic `subType`. |

The optional inline/leaf label is inline Markdown. An inline directive needs a
label or attributes so that ordinary punctuation such as `:word` stays text.
Leaf directives occupy their own line. For a container, a title is optional,
and the body starts on the following line. Unknown types are valid and retain
their type, title/label, attributes and content.

The proposed identifier grammar is an ASCII letter followed by zero or more
ASCII letters, digits, `_` or `-`. Types and attribute names use ASCII lowercase
for matching and canonical AST spelling. This places no limit on the number of
defined types; human text, IDs and values retain Unicode. It also avoids an
implementation-dependent Unicode case-folding rule for identifiers.

Container markers may be indented zero to three spaces relative to the current
CommonMark block context. Optional spaces/tabs are accepted after the colon run
and between the type, title and attributes. These parts remain on one source
line. The type is first; title and attributes may follow in either order.

```md
:::warning[Before deploying]{#check}
::: warning {#check} [Before deploying]
```

Both have the same meaning. Writers use a space after the fence, then the type,
title and attributes in that order. They use square brackets for titles.
Unbracketed legacy container titles are not part of the core grammar.

Title brackets and attribute braces have no interior padding. Internal spaces
between words or attributes are meaningful. Backslash escapes protect literal
brackets, braces and backslashes. Balanced brackets in inline links/code are
handled by the inline grammar; they do not prematurely close the outer label.

**Nested containers**

````md
:::: note [Outer]

::: warning [Inner]
Check the configuration.
:::

::::
````

A container starts with at least three colons. A directly nested container uses
fewer colons than its enclosing container, still at least three. A closing
marker contains only its matching run of colons and optional horizontal
whitespace; it closes the active container with that fence length. Markers
inside code stay code. This draft uses explicit fence matching.

Writers choose `3 + maximum descendant container depth` colons for an outer
container and recalculate within its body. They must also avoid accidental
delimiter lines in literal content by escaping those lines. Ordinary nested
lists, quotes and code blocks remain valid inside containers.

Blank lines adjacent to the opening/closing fence are readable source spacing,
not visible blank lines. Repeated title wrappers are malformed; repeated
attribute lists concatenate in source order before duplicate resolution.
Unclosed or mismatched fences preserve source through the recovery rules.

Prior art: [Docusaurus admonitions](https://docusaurus.io/docs/markdown-features/admonitions),
[remark directives](https://github.com/remarkjs/remark-directive) and
[MyST directives](https://mystmd.org/guide/syntax-overview).

### Attributes and identity

```md
{#deployment-check open audience=admin label="Before deploying"}
```

Attribute entries are separated by spaces or tabs. Values may be unquoted,
single-quoted or double-quoted. Quoting does not change their value type.
Backslash escapes the active quote delimiter or backslash in quoted values;
other backslashes retain their literal meaning. Unquoted values are nonempty
and end before whitespace or `}`; quote values containing whitespace, braces
or quote delimiters. An empty assigned value uses `key=""`; `key=` is malformed.

| Source | Effective AST value |
| --- | --- |
| `open` | Boolean `true`. |
| `!open` | Boolean `false`. |
| `open=foo` | String `"foo"`. |
| `open=false` | String `"false"`. |
| `open="false"` | String `"false"`. |
| `#check` or `id=check` | String node ID `"check"`. |

Assigned values are never coerced into booleans, numbers or null. Names are
case-insensitive; values and IDs are preserved. Duplicate/conflicting entries
are **well-formed, last occurrence wins**. A diagnostic is recommended. This
rule applies equally to shorthand and assigned IDs.

Store ordinary entries in `attributes`. Store the effective ID once in the
node's optional string `id` field. Every AST node may carry an ID; that does not
add ID authoring syntax to every inline text fragment or require ID generation.

Attributes attach to directives, ATX headings and images in the forms shown in
this draft. `class="one two"` and `style="…"` carry presentation data. The core
does not add `.class` shorthand. Unknown names remain preserved. A standard
feature interprets its supported values during conversion, with explicit
defaults; an arbitrary flag has no implied native HTML behavior.

Recommended HTML maps `id`, `class`, `style` and supported native attributes to
their native equivalents. Other string attributes map to `data-*`; custom true
flags map to a present empty `data-*` attribute and false flags omit it. Preserve
already-prefixed `data-*` names without adding another prefix. Native boolean
attributes use presence for true or any assigned string, and omission for false.
A string such as `"false"` remains a string in the AST; HTML presence still
enables the native boolean state. Conversion-owned
`data-type` identifies the construct; a colliding authored value remains in the
AST and produces a conversion diagnostic instead of changing that identity.

**Attribute attachment in ordinary Markdown**

In addition to named constructs, these source forms have explicit attachment
rules:

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 placement=center responsive}
[Release notes](release.md){class="release-link"}
```

A heading's final whitespace-separated attribute list attaches to the heading
and is excluded from its inline title content. An attribute list immediately
after a completed image/link attaches to that image/link. Lists must be on the
same source line as their target; whitespace inside inline code is not an
attachment. Escape an opening brace to keep a would-be attachment literal.
Multiple adjacent attachment lists resolve in source order. Malformed attachment
syntax remains literal rather than consuming unrelated content.

A code fence's info string may include a named attribute list such as `{#sample}`.
A brace group containing only the documented numeric line-range grammar instead
sets highlighted lines. Preserve unknown info tokens as code `meta`. Ordinary
paragraph/block styling and attributes without a defined shorthand use native
HTML; generic AST field availability does not silently introduce postfix syntax
for every text fragment.

IDs are opaque strings. The language does not lowercase, trim, generate or
renumber authored IDs. Preserve duplicate authored IDs and recommend a warning.
HTML-specific validity diagnostics belong to conversion, without silently
changing the AST's identity.

Prior art: [Pandoc attributes](https://pandoc.org/MANUAL.html#extension-header_attributes),
[Kramdown attribute lists](https://kramdown.gettalong.org/syntax.html#inline-attribute-lists)
and [HTML attribute syntax](https://html.spec.whatwg.org/multipage/syntax.html#attributes-2).

### Leading-pipe line blocks

```md
| First line
| Second line
|
| Fourth line
```

A line starting with `| ` or a pipe followed by a tab starts a represented line.
A bare `|` explicitly represents an empty line. `|Text` stays ordinary text.
Allow the same zero-to-three-space block-relative indentation as other markers.
Remove marker separation and additional leading spaces/tabs from represented
text; source indentation is not visual indentation.

Adjacent pipe lines form one `lineBlock`. An ordinary blank source line between
two pipe lines contributes one empty represented line. Thus one internal blank
line and one bare pipe have the same empty-line meaning. Blank lines at a
container boundary, before ordinary following Markdown or at end-of-document
are ordinary spacing; use a bare pipe to request an explicit boundary empty line.

A nonempty indented line immediately following a nonempty represented line may
continue it without another pipe. Strip that continuation indentation and join
with one space. It adds no represented line break. A nonempty unindented line
without a marker ends the block, even without a blank separator. A blank source
line interrupts eligibility for an unmarked wrapped continuation.

```md
| This is one sentence wrapped
  across two source lines.
| This is the second represented line.
```

Parse inline content across represented lines. Emphasis/strong emphasis may
span them; explicit boundaries remain `break` nodes within that formatting.
An inline code span must fit within one represented line. Block code is outside
this inline parsing scope. Literal pipes can be escaped or shown in code.

The AST uses inline content in `lineBlock.children` and a `break` for each
represented boundary; a one-line plain block may use `value`. Consecutive breaks
preserve empty lines. A leading/trailing break preserves an explicit leading/
trailing empty line. A single bare pipe has empty string `value` and represents
one empty line.

Recommended HTML is `<p>` with `<br>` for represented boundaries. For terminal
empty lines, append one final layout `<br>` so HTML does not absorb the last
requested line. That extra layout break is not another AST break. An entirely
empty one-line block also needs one layout `<br>`. Preserve the formatting
wrappers around breaks. Explicit empty lines add to ordinary paragraph spacing.

CommonMark's existing trailing-space and trailing-backslash hard breaks remain
accepted for compatibility and map to `break`. Canonical Expressive writing
uses leading-pipe line blocks for intentionally preserved lines/empty lines.
The reason is source readability: trailing spaces are invisible, and a trailing
backslash forces a break where languages such as Python use it to continue a
line. That is a design preference, not a claim that CommonMark is ambiguous.

Prior art: [Pandoc line blocks](https://pandoc.org/MANUAL.html#line-blocks),
[CommonMark hard breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks),
[Python explicit line joining](https://docs.python.org/3/reference/lexical_analysis.html#explicit-line-joining)
and [HTML line breaks](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-br-element).

### Ordinary Markdown segments

The base specifications define ordinary source delimiters and escaping. These
AST mappings use Expressive's generic fields; `value` is already parsed literal
content, never a string requiring another Markdown parse.

| Segment | AST content and meaning | Recommended HTML |
| --- | --- | --- |
| Text | `text.value`, string literal text. | Escaped text. |
| Paragraph | `paragraph.value` or inline `children`. | `<p>`. |
| Heading | `heading`, integer `level` 1–6, `value` or inline `children`. | Corresponding `<h1>`–`<h6>`. |
| Emphasis / strong | `emphasis` / `strong`, `value` or inline `children`; semantic emphasis. | `<em>` / `<strong>`. |
| Strikethrough | `delete`, `value` or inline `children`; removed/no-longer-current content. | `<del>`. |
| Inline code | `inlineCode.value`, literal string. | Escaped `<code>`. |
| Hard break | `break`, no content field. | `<br>`. |
| Soft break | `softBreak`, no content field; ordinary source line wrapping. | A newline/space with normal inline layout. |
| Horizontal rule | `horizontalRule`, no content field; separates sections of document content. | `<hr>`. |
| Block quote | `blockquote.body`, ordered blocks. | `<blockquote>`. |
| List | `list.children`, ordered `listItem` nodes; `ordered`, optional `start`, `tight`. | `<ul>` or `<ol start="…">`. |
| List item | `listItem.body`, blocks; optional boolean `checked` for task state. | `<li>`; a task item includes a disabled, labelled checkbox. |
| Link | `link.url`, `value` or inline `children` for label; optional string tooltip `title`. | `<a href="…" title="…">`. |
| Image | `image.url`, string `alt`, optional string tooltip `title`, optional `attributes`. | `<img src="…" alt="…">`. |
| Raw HTML | `html.value`, original markup; `display` is `inline` or `block`. | Authored HTML, subject to the declared host rendering policy. |

Link URLs may be relative or absolute. Reference-style links/images resolve
against CommonMark definitions into the same semantic nodes; canonical writers
may emit inline destinations. Reference spellings/definitions are lexical
provenance when exact source preservation is requested. Unresolved reference
syntax follows ordinary CommonMark literal fallback.

An isolated image remains an image in its paragraph; it does not automatically
become a captioned figure. Explicit figures keep image alternative text distinct
from the figure's visible caption. `width`/`height` attributes are positive
integer CSS-pixel strings. `placement` accepts `center`, `wrap-left` or
`wrap-right`; absence means ordinary flow. `responsive` is a flag permitting
host renditions. Responsive URL selection, loading and delivery belong to the
renderer, not authored identity.

`<u>` and `<mark>` spans can map to `underline` and `highlight` nodes with
`value` or inline `children`; preserve their attributes. These express the
ordinary underlining/highlighting available in rich editors. Other HTML can
remain opaque `html` data. A renderer policy that removes markup reports that
loss separately from parsing; preserving document data does not require executing
scripts or arbitrary components.

Prior art: [CommonMark](https://spec.commonmark.org/0.31.2/),
[GFM](https://github.github.com/gfm/) and [mdast node documentation](https://github.com/syntax-tree/mdast).

### Tables

```md
| Item | Status |
| :--- | ---: |
| API | Ready |
```

Use GFM syntax for a header row, column alignment and inline cell content.
The AST is `table.children` → `tableRow.children` → `tableCell` content.
Rows distinguish headers through cell `header` booleans. A simple cell uses
`value` or inline `children`; a rich cell uses block `body`. Keep these content
fields mutually exclusive. Store column alignment on `table.align` as an array
of `left`, `center`, `right` or null values.

**Cell merging**

A cell whose entire unescaped source, after trimming spaces/tabs, is `>` merges
with the next cell to its right. Consecutive `>` cells merge into the next
ordinary cell. A cell containing only `^` continues the cell above it. These
markers are recognized before inline parsing, only inside an established table.
Both tight `|>`/`|^` and spaced `| >`/`| ^` spellings are accepted. Empty cells
remain empty cells: absence of text never requests a merge. Write `\>` or
`\^`, or inline code, to display a marker literally.

```md
| First | Second | Status |
| --- | --- | --- |
| > | Release checks | Ready |
| ^ | ^ | Verified |
```

“Release checks” occupies the first two columns and two body rows. Its source
text is in the rightmost slot on its first row; its AST cell represents the
whole rectangle at the rectangle's top-left position. The resulting cell has
`colSpan: 2` and `rowSpan: 2`. Neither marker becomes a text or empty cell node.

Resolve horizontal runs first, then vertical continuations on the original
column grid. A `>` run must terminate in an ordinary cell in the same row, not
another row or a `^`. Every column of a horizontally merged cell must contain
`^` on each continuation row. Repeated continuation rows extend the same
originating cell. Merges must form rectangles and cannot overlap, consume
non-marker content, or cross the header/body boundary. The delimiter row does
not count as a table row and cannot contain merge markers. Merged cells inherit
alignment from their leftmost column unless a cell attribute overrides it.

A table using merge markers must explicitly supply the same number of column
slots in every source row, including slots covered by spans. Detect that count
before ordinary GFM padding/truncation. A dangling marker, partial-width vertical
continuation, inconsistent width or other invalid merge preserves the whole
table as a block `literal` recovery node and recommends a diagnostic. This
avoids guessing a merge or losing cell content. Ordinary GFM tables without
merge markers retain ordinary GFM row-width behavior.

In the AST, `tableRow.children` contains only originating cells in column order.
`colSpan` and `rowSpan` are positive integers, default 1 when absent; canonical
serialization omits either default. Place each cell at the first unoccupied
column, skipping coverage from earlier row spans. Numeric span fields describe
structure; they are not assigned-attribute value coercion. A native HTML importer
maps valid `colspan`/`rowspan` to these fields, without duplicating them in
`attributes`. Unrepresentable HTML span behavior remains HTML with a diagnostic.

**Rich cell content and conversion**

Rich tables preserve widths, backgrounds and classes through `attributes`, and
block content through cell `body`. Presentation attributes remain strings/flags.
Use native HTML table markup for features outside pipe-table syntax. A reader
may retain it as opaque HTML; a rich-editor profile that claims editable rich
tables maps its supported subset to the structured table AST. Writers use pipe
syntax, including merge markers, when it expresses all information; otherwise
they use native HTML or report an unsupported conversion.

For canonical pipe output, emit `>` in the slots before a horizontally merged
cell's content, and `^` in every occupied slot below its first row. Canonical
writers must escape literal marker-only cell content. Preserve each cell's
identity once; do not fabricate placeholder cell IDs.

Recommend `<table>` with `<thead>`/`<tbody>`, `<tr>`, `<th>` and `<td>`, emitting
`colspan`/`rowspan` for non-default spans and preserving alignment and supported
presentation attributes. The example body becomes:

```html
<tbody>
  <tr><td colspan="2" rowspan="2">Release checks</td><td>Ready</td></tr>
  <tr><td>Verified</td></tr>
</tbody>
```

The renderer must not silently flatten a merged/rich table into an unmerged
representation. Preserve authored header information; don't guess complex
accessible header associations solely from visual position.

Prior art: [UMD's table-spanning documentation](https://docs.rs/crate/umd/0.2.0/source/README.md)
and [implementation](https://docs.rs/crate/umd/0.2.0/source/src/extensions/table/umd/cell_spanning.rs).
Expressive adopts the compact directional marker idea, with the explicit grid
and recovery rules above; it does not claim identical UMD parsing behavior.

### Code blocks and presentation metadata

````md
```ts title="deploy.ts" {1,3-4} :line-numbers
const mode = "safe";
await check();
await deploy();
```
````

A `code` node keeps original code in string `value` and an optional `language`.
Its optional caption is a literal string `title`, such as a filename.
It is not parsed as inline Markdown, so code remains a literal leaf. Recognized
fence metadata maps to `attributes`:

| Source metadata | Effective attribute |
| --- | --- |
| `{1,3-4}` | `highlight-lines: "1,3-4"`. Lines are one-based inclusive ranges. |
| `:line-numbers`, `showLineNumbers` | `line-numbers: true`. |
| `:no-line-numbers` | `line-numbers: false`. |
| `showLineNumbers=3` | `line-numbers: true`, `line-start: "3"`. |
| `title="deploy.ts"` | `code.title`, not a duplicated ordinary attribute. |

Preserve unrecognized fence metadata as string `meta`. It contains only
uninterpreted tokens; source provenance can retain the original whole info
string. Canonical writers regenerate known metadata from current AST fields and
append preserved unknown tokens. Line-number omission uses the renderer's
default. An explicit flag overrides it.

Code annotation comments remain in AST `value` so editor/source round-trips
retain them. A code presentation pass may recognize `[!code highlight]` and
`[!code highlight:N]` comment markers, or the `highlight-next-line`,
`highlight-start` and `highlight-end` spellings. It derives highlighted source
lines before removing marker-only lines from display. A trailing marker affects
its own line; a marker-only line affects the following line/range. Ranges never
include the marker-only line itself. Preserve source-to-display line mapping;
line metadata and marker comments refer to original code lines. Escaping the
marker suppresses interpretation. Custom annotations remain profile data.

Recommended HTML is `<pre><code class="language-…">…</code></pre>`, optionally
with a caption wrapper and per-line spans. Code is escaped; highlighting does
not execute it. A copy action copies display code without annotation comments
or line-number labels. Exact syntax colors, action buttons and line styling are
presentation choices. The document retains source even when a profile cannot
render an annotation.

Code fences are longer than any conflicting delimiter run in their literal
content. Both backtick and tilde fences follow CommonMark. Diagram/math code
languages retain their source and may receive a specialized renderer; a literal
code fallback remains available.

Prior art: [Docusaurus code blocks](https://docusaurus.io/docs/markdown-features/code-blocks)
and [Shiki notation transformers](https://shiki.style/packages/transformers#transformernotationhighlight).

## Recognized container semantics

The vocabulary is open. These entries define shared meanings, not a closed
parser allowlist. Every `:::` type, including the following types, remains in
the same `container` AST family.

| Type | Meaning | Recommended HTML and presentation |
| --- | --- | --- |
| `note` | Contextual information worth noticing. | `<section data-type="note">`; subdued label/icon/color if useful. |
| `tip` | Helpful advice for performing the documented task. | `<section data-type="tip">`; helpful-advice label/icon/color. |
| `warning` | A potential problem requiring caution. | `<section data-type="warning">`; prominent caution treatment. |
| `danger` | Critical information warranting maximum attention. | `<section data-type="danger">`; strongest alert treatment, without inferring a particular consequence. |
| `details` | Content that can be disclosed or collapsed. | Native `<details>` with `<summary>`. |
| `figure` | Self-contained content presented as one unit, optionally captioned. | `<figure>` and authored `<figcaption>`. |
| `tabs` | Alternative labelled panels of related content. | Sequential labelled sections; an interactive profile may enhance to accessible tabs. |
| `code-group` | Alternative code panels, usually languages or package managers. | Labelled code sections; an interactive profile may enhance them as tabs. |
| `toc` | Authored navigation entries linking to document sections; tools may refresh them. | `<nav>` with its readable title/body. |

For section-based containers, an authored title recommends a `<header>` with
its converted inline content. It does not acquire an arbitrary heading rank.
An accessible name may use a converter-generated label ID. Static warning/danger
content does not automatically acquire the live-region `alert` role. An absent
title stays absent; a renderer may separately display a type label.

Unknown containers recommend `<section data-type="custom-type">`, preserving
title, body and attributes. There is no format-branded output tag or attribute.
Legacy names such as `info`, `important` and `caution` remain valid custom
types. A presentation profile can recognize their established treatment without
silently renaming the AST or expanding the four standard callout meanings.

### Details

```md
::: details [Show the full log] {open}
The build finished successfully.
:::
```

Omission defaults to collapsed. The `open` flag expands and `!open` explicitly
collapses. Assigned values such as `open=foo` and `open="false"` remain strings
in the AST. Recommended HTML conversion follows native attribute presence:
any string assignment emits the attribute and opens the disclosure; boolean
false omits it. This does not coerce the stored string into a boolean. The
JavaScript advisory for boolean-looking assignments is described below.

Recommend native `<details open><summary>…</summary>…</details>`. An absent
authored title may use the renderer fallback “Details” as a control label,
without adding that title to the AST.

### Figure

```md
::: figure [Deployment overview]
![Services and connections](deployment.svg)
:::
```

The bracketed title is the caption, with inline formatting. The body can contain
images, tables, diagrams or code. Recommend an authored `<figcaption>` after
the converted body. An image's `alt` remains its alternative text, not a copied
caption. Numbering is optional renderer behavior; default conversion adds no
“Figure 1” prefix. Caption layout is a styling choice.

Prior art: [HTML figure](https://html.spec.whatwg.org/multipage/grouping-content.html#the-figure-element),
[MyST figures](https://mystmd.org/guide/figures) and
[Quarto figure divs](https://quarto.org/docs/authoring/figures-and-layout.html#figure-divs).

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

Inside `tabs` or `code-group`, a block-level `== Label` or `== [Label]` starts a
panel. The label is inline Markdown; an optional attribute list can set its
selection `value`. Markers inside code do not split panels. Panel bodies support
ordinary blocks and nested containers using the fence rules above. `==` lines
outside these constructs have their ordinary Markdown meaning.

A panel is `type: "panel"` with a `title` node, block `body` and optional
`attributes.value` string. Its stable selection value is that attribute or,
when absent, the title's plain text. The outer construct's `group` attribute
names a related selection group; its bracketed title is a display title, not
an implicit synchronization key. `default` identifies an initial panel value.
Unknown/default-missing values select the first panel and recommend a diagnostic.
Duplicate values preserve all panels; the first matching panel wins selection.

For a `code-group` containing consecutive code fences without explicit panel
markers, derive panel labels from code captions, then language, then a localized
fallback. Keep the original code nodes in `body`; inferred panels are a
presentation view, not duplicated authored AST content. Writers can retain code
fences or emit explicit panels when labels/settings require them.

Recommended baseline HTML displays all panels as labelled sections, preserving
content without JavaScript. An interactive profile supplies proper tab roles,
keyboard operation and relationships, keeping inactive panels available through
their controls. `group`, `default`, `lazy` and `query-string` attributes carry
selection/presentation intent. A `query-string` flag uses `group` as its parameter
name; a string supplies an explicit name. A query selection takes precedence
over a stored group selection, then the authored default. Persistence is a
profile behavior, not mutation of the document AST.

Prior art: [Docusaurus tabs](https://docusaurus.io/docs/markdown-features/tabs)
and [ARIA tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).

### Chips and mentions

```md
Status: :chip[Ready]{tone=green}.
Thanks, :mention[Ada Lovelace]{ref=user-123}.
```

`chip` means a compact category/status label. Its inline content is `value` or
`children`; `tone` suggests a hue. Known hues are neutral, blue, green, yellow,
red and purple. Preserve other values; a renderer without a matching treatment
uses its neutral style. Recommend `<span data-type="chip">` with the converted
label and presentation attributes. Color does not replace the label's meaning.

`mention` refers to an entity using string `attributes.ref`; its label remains
authored content. `id` is always the mention node's own identity, not its entity
target. Optional `url` supplies a navigable target; resolving an application
entity is the host's responsibility. Without a reference, preserve the label
and diagnose an incomplete mention. Recommend a labelled `<span>` or `<a>` when
a URL is available. A renderer may present a prefix without adding it to the
authored label. Existing product-specific entity identifiers require explicit
import mappings rather than overloading generic node identity.

### Table of contents

```md
::: toc [On this page] {depth=3 format=bulleted}
- [Installation](#installation)
- [Configuration](#configuration)
:::
```

`toc` identifies its body as a table of contents: readable navigation entries
linking to sections of a document. It is a `container`, with optional structured
`title` and an authored block `body`. The standard body is a Markdown list of
links, optionally nested to express heading hierarchy. A plain format may use
paragraph/link content. The saved source includes the actual readable entries;
a bodyless `::toc` placeholder is not the recognized semantic form.

Editors and converters may generate or refresh the entries from document
headings when configured to do so. They write the resulting list back into the
source/AST body; generated content does not disappear from the human-readable
Markdown. Without an explicit update operation or configured policy, preserve
the authored entries. Mere rendering converts the existing body rather than
silently replacing it with another document scan.

For tools that refresh entries, `depth` is a string interpreted as a maximum
heading level 1–6, default 3. `format` is `plain`, `bulleted` or `numbered`,
default `bulleted`. Invalid settings remain preserved, recommend a diagnostic
and use the update default. The existing body's list markers remain meaningful
content; a setting does not silently rewrite them until an update is requested.
A refresh uses readable heading text, document order and heading hierarchy.
It omits headings inside the TOC itself. Optional scope/minimum-level settings
remain profile extensions.

A refresh must produce links to actual output anchors or authored IDs. It may
use the recommended anchor algorithm below when no authored target exists;
that does not insert implicit IDs into unrelated authored AST nodes. Converters
that change heading targets keep TOC links consistent in their output. A tool
must report unresolved targets instead of promising working navigation.

An empty TOC body is incomplete semantic content. Preserve it during editing
and recommend a diagnostic; do not treat it as an invisible request to fabricate
content. A source writer publishing a refreshed TOC includes its entries.

Recommend `<nav>` containing the converted title and authored body. An authored
title can label the navigation through `aria-labelledby`; otherwise a converter
may supply `aria-label="Table of contents"`. Render the list and links as written.
The title is a navigation label, not an automatically ranked heading.

### Text styling, diagrams and math

Images, table cells and raw HTML preserve authored classes and styles. Source
semantics do not prescribe a component framework or a CSS library. Both target
profiles must expose these values to their renderers and report unsupported
presentation rather than silently discarding it.

Diagram source can use a `mermaid` code fence. Mathematical source can use a
`math` code fence, or an inline extension such as ``:math[`x_1^2`]`` that keeps
literal notation in an inline-code child. These carry enough source for a
specialized profile to render diagrams/math and for a basic renderer to show
escaped notation. They do not require the core parser to execute a diagram
language, evaluate expressions or implement a typesetting engine.

Prior art: [Docusaurus diagrams](https://docusaurus.io/docs/markdown-features/diagrams)
and [math support](https://docusaurus.io/docs/markdown-features/math-equations).
See [presentation coverage](/expressive-markdown/presentation) for the complete matrix.

## Recommended output anchors

This algorithm recommends output IDs; it grants no implicit identity in source
or AST data. An implementation can support navigation using another documented
algorithm without changing language conformance.

1. Reserve every authored ID in the output document first.
2. Derive readable text from a title/heading and normalize that derived text to
   Unicode NFC, then lowercase it.
3. Retain Unicode letters, numbers and combining marks. Replace every other run
   with one hyphen and trim boundary hyphens.
4. Use `section` if the result is empty.
5. In document order, use the first free candidate, then `-1`, `-2`, and so on,
   skipping authored and previously generated IDs.

For example, `Über setup` can produce `über-setup`. URL serialization can
percent-encode the fragment while retaining the identifier. Preserve authored
duplicates and diagnose them; only generated candidates receive collision
suffixes. Label/control IDs produced for HTML use the same collision allocator
without writing them back as authored document IDs.

## Recovery and diagnostics

Markdown remains forgiving. Unknown semantic types and unknown metadata keys
are valid. Duplicate attributes are valid with final-occurrence precedence.
Invalid marker structure is a different category and must preserve its source.

The proposed recovery policy is local: keep an invalid directive opener as
literal text; do not consume the rest of the document looking for its intended
meaning. An unclosed otherwise valid container retains its unmatched region as
a `literal` recovery node through the end of its enclosing block context. A
mismatched nesting region is preserved in the same way. A fenced/indented code
region still takes lexical precedence while locating recovery boundaries.

If an opening `---` has no closing frontmatter delimiter, it is ordinary
Markdown rather than an indefinitely open metadata block. If delimiters exist
but the YAML/value profile is invalid, retain the entire delimited source as a
`literal` recovery node and produce no guessed metadata projection.

Diagnostics are a separate result, not inserted body content. A useful record
contains `code`, severity, message, optional source position and optional node
ID. This diagnostic API is tooling guidance rather than a mandatory parser API.
Recommend warnings for duplicate attributes/IDs and invalid feature values.

The JavaScript tool additionally warns about likely boolean intent in unquoted
`open=true`/`open=false`, suggesting `{open}`/`{!open}`. Quoting suppresses that
advisory; assigned values remain strings. This is tool behavior, not a new
language-validity rule. See [tooling notes](/expressive-markdown/language#recovery-and-diagnostics).

A recovery `literal` node contains original source as string `value` and a
`display` context. Recommend escaped text for inline recovery, and escaped text
with visible source-line breaks for block recovery. Recovery preserves source
even where the input is outside valid grammar. It is not a hidden raw-HTML or
executable-content mechanism.

## Writing and preservation

The proposed baseline guarantee is semantic round-tripping of conforming source:
preserve meaning, ordered content, explicit line divisions, authored IDs,
unknown semantic types, supported metadata and authored presentation values.
Byte-identical source is a separate optional capability. It needs lexical
provenance for quote choice, whitespace, overwritten attributes, reference-link
spelling and code/frontmatter delimiters.

Writers produce these canonical forms:

- Lowercase directive/attribute names; preserve values and metadata key casing.
- A space after a container fence; bracketed title before attributes; no wrapper
  padding; one readable blank line around a container body.
- Nested fence lengths chosen from container depth; code fences safe for their
  literal content. Escape literal structural punctuation when needed.
- Double-quoted assigned strings when quoting is needed; `{name}`/`{!name}` for
  booleans, including an explicit false that differs from omission/default.
- Leading-pipe blocks for explicitly preserved lines; bare pipes for empty lines.
- Pipe-table merge placeholders regenerated from numeric cell spans; literal
  marker-only cell contents escaped.
- YAML strings for document title/ID, a list of strings for tags, and custom
  metadata preserved. Quote strings that YAML would otherwise type differently.

Parsers should prefer compact `value` for wholly literal inline content.
Structured `children` containing only text is also valid. AST normalization must
not collapse child nodes and lose their IDs, attributes or provenance. No
automatic `value`/`children` rewrite is required for supplied ASTs.

AST JSON accepts null for absent optional fields and normalizes absence to
omission. Actual null metadata remains data. Root `version` is required;
unsupported versions stop conversion with a clear error. See [ast.md](/expressive-markdown/ast).

## Prior-art comparison

| Format/convention | Adopted idea | Expressive distinction |
| --- | --- | --- |
| CommonMark/GFM | Ordinary Markdown and established table/list/link behavior. | Named semantic constructs, frontmatter and explicit line blocks have additional contracts. |
| Docusaurus | Bracketed callout titles, nested colon fences, rich documentation presentation. | Framework-independent syntax/data; open semantic types; optional spacing; no MDX runtime requirement. |
| remark directives | Inline/leaf/container scope and an open named vocabulary. | Standard meanings, generic AST fields and a defined flag/string distinction. |
| UMD | Compact `>`/`^` table-merge markers. | Defined rectangular grid, structural span fields and loss-preserving recovery; no claim of parser equivalence. |
| Pandoc | Attribute IDs and leading-pipe line blocks. | Inline/line boundaries survive without preserving source indentation as visual indentation. |
| MyST/Quarto | Structured documentation and figures with captions. | The shared container family uses `subType`; language meaning and HTML guidance are separate. |
| mdast/unist | Documented node meanings and predictable tree tooling. | Independent `title`/`body`/`children`/`value` contract; compact literal nodes; no adapter commitment. |
| Rich editors | Stable identities and content/presentation preservation. | Generic IDs are separate from entity references and renderer-generated control IDs. |

This comparison identifies reusable ideas, not a claim of complete source
compatibility. Product-specific JSX, scripts, source aliases and theme APIs
require their own integration contracts. Continue with the
[AST reference](/expressive-markdown/ast),
[presentation coverage](/expressive-markdown/presentation) and
[publishing profile](/expressive-markdown/publishing).
