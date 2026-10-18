---
title: Document AST
order: 2
blurb: nodes · fields · traversal
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Document AST

The abstract syntax tree (AST) is the JSON format tools use to read, edit and
render an Expressive document. It keeps titles, bodies and entity references
explicit, so a renderer can use them without interpreting a particular editor's
HTML. This reference defines fields and valid node shapes; the
[language chapter](/expressive-markdown/language) shows their Markdown syntax.

```json
{
  "type": "document",
  "version": 1,
  "id": "deployment-guide",
  "title": { "type": "title", "value": "Deployment guide" },
  "metadata": { "tags": ["deployment"] },
  "body": [
    { "type": "heading", "level": 2, "value": "Before deploying" },
    {
      "type": "container",
      "subType": "warning",
      "id": "deployment-check",
      "title": { "type": "title", "value": "Check the backup" },
      "body": [
        { "type": "paragraph", "value": "Back up the database first." }
      ]
    }
  ]
}
```

## Shared node contract

| Field | Type | Contract |
| --- | --- | --- |
| `type` | Nonempty string | Required structural node type; canonical built-in names below. |
| `subType` | String | Semantic type on `container`, `inline` and `leaf`; canonical lowercase. Its vocabulary is open. |
| `id` | String | Optional on every node; preserve exactly. Never generate or normalize it implicitly. |
| `title` | `TitleNode` or string, according to the node type | Optional. Document/container/table captions use a title node; code captions and link/image resource tooltips use strings. Each node type fixes its representation. |
| `body` | `Node[]` | Main block content. A title is optional, not the criterion for choosing this field. |
| `children` | `Node[]` | Inline content or structural grouping. |
| `value` | String | Literal content. Never reparse it as Markdown. |
| `attributes` | Object of string or boolean values | Authored properties/presentation. Keys use camelCase mapped from case-insensitive, dash-separated source names; `show-line-numbers` becomes `showLineNumbers`. Assigned values are strings; flags are booleans. Generic ID lives in `id`, not here. |
| `position` | `Position` | Optional original-source range, defined below. |
| `source` | JSON object | Optional lexical provenance for source preservation. It is not another semantic value or a traversable subtree. |
| `data` | JSON object | Optional application/tool annotations. Not interpreted as content by generic traversal. |

`body`, `children` and `value` are mutually exclusive. A node can have none,
such as a break. Empty strings and arrays are real values, not absence.
A title-bearing node can have its title alongside its main content field.
Literal leaf types do not contain a node-valued title or other nested content.

`source` keeps original spellings; `data` keeps tool annotations. Neither holds
traversable document content. Readers preserve unknown fields as JSON extension
data and report unsupported structure. New node-bearing fields need an explicit
contract; only the defined content fields participate in traversal.

### Attribute spelling

```md
{highlight=1,3-4 & show-line-numbers}
```

```json
{"highlight": "1,3-4", "showLineNumbers": true}
```

The JSON above is the node's `attributes` object. `&` is an optional source separator, not AST data. Assigned values remain strings; bare/negated flags become booleans. Canonical writers turn camelCase keys back into dash-separated names. Metadata keys and generic node IDs do not undergo this mapping. See [attribute normalization](/expressive-markdown/parsing#attributes-and-identity).

### Fixed field types, alternative content shapes

Both of these are valid:

```json
{ "type": "heading", "level": 2, "value": "Deployment" }
```

```json
{
  "type": "heading",
  "level": 2,
  "children": [
    { "type": "text", "value": "Deploying " },
    { "type": "strong", "value": "safely" }
  ]
}
```

A field does not change type: `value` remains a string, and `children` remains
an array. The node permits either shape. Parsers should choose the compact
form for purely literal content. Supplied ASTs need not be rewritten into that
form, particularly when text children have IDs, attributes or source records.

### Absence and normalization

Readers accept omission or null as absence for optional fields without another
defined null meaning. Canonical AST serialization omits absent fields. Normalize
that absence before checking content-field exclusion. Thus optional
`children: null` can disappear, but a required content field still needs an
actual value. Null does not satisfy required fields or become a valid attribute
entry. Null within metadata is preserved as data.

### Generic traversal

```text
visit(node)
if node.title is a node:
    walk(node.title)
for child in node.body or node.children, if present:
    walk(child)
```

Visit the title before main content, even when a renderer places its caption
after the body. Array order is meaningful. A string resource title is literal
metadata; `value` is literal content. Neither is recursively visited as nodes.
`attributes`, `metadata`, `source` and `data` are not hidden content subtrees.
Reject multiple content fields instead of silently choosing one.

### Source locations

Use `position: {start, end}` for original-source locations. A point has required one-based
`line` and `column`, with optional zero-based `offset`. Columns and offsets count
UTF-16 code units; line endings advance the line and reset its column. The end
point is exclusive. Offsets, when supplied, count the original source, including
both units in CRLF. A retained BOM counts in offsets but not the first displayed
column. Positions describe source provenance, not node identity.

An edit invalidates affected positions unless a tool recalculates them. A tool
may omit positions for generated or moved content. Do not fabricate source
coordinates or keep stale coordinates as if they describe the new source.
The point format follows [unist positions](https://github.com/syntax-tree/unist#position).

## Document and metadata

`document` requires `version: 1` and `body: Block[]`, including an empty array
for an empty document. Optional fields include `id`, structured `title`,
`metadata`, attributes and provenance. `version` is an integer AST format
version, independent of the authored YAML or converter package version.
Conversion must stop with a clear error for an unsupported version.

`metadata` is a JSON object with case-sensitive string keys and recursively
JSON-compatible values. Standard source title/ID project to root `title`/`id`;
all other keys remain in metadata. Standard `tags` is `string[]` and
`description` is an inline-Markdown-valued string. Generic traversal deliberately
does not parse metadata strings; metadata consumers use the field's declared
interpretation when deriving display/plain text.

An AST writer reconstructs YAML from the current designated fields and metadata.
Reserved structural keys in custom metadata remain metadata when writing.
Conflicting supplied `metadata.title`/`metadata.id` do not silently override
designated root fields: report the conflict, with designated fields authoritative.
The schema does not silently coerce number/boolean IDs or non-string tags.

Default HTML guidance: a document may render as an `<article>` with its title
in a `<header>` and converted body; a host may embed the body in an existing
document shell. Metadata produces no body HTML. Title rank is not inferred from
the existence of a title node.

## Content node reference

**Inline content** means exactly one of string `value` or ordered inline
`children`. **Blocks** means an ordered `body` array. All nodes also allow the
shared fields above. The following sections define required content and any
additional fields.

### Text and inline content

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `text` | String `value`. | Literal text leaf. |
| `paragraph` | Inline content. | Empty and whitespace-only content is valid AST data and must survive writing; use safe HTML when ordinary spacing would erase it. |
| `heading` | Integer `level` 1–6; inline content. | No implicit ID; authored `id` remains generic. |
| `title` | Inline content. | Used through a parent's title field; does not itself supply a heading rank. |
| `emphasis`, `strong`, `delete`, `underline`, `highlight` | Inline content. | Semantic/stylistic inline wrappers; preserve attributes. |
| `inlineCode` | String `value`. | Literal code leaf; Markdown delimiters are not part of value. |
| `break`, `softBreak` | No content field. | Explicit represented break versus ordinary source wrapping. |
| `link` | String `url`; inline content. | Optional string tooltip `title`. Nested links are invalid child content. |
| `image` | String `url`, string `alt`. | Optional string tooltip `title`; attributes preserve size, placement and delivery intent. No inline/body content field. Empty alt is permitted. |
| `inline` | String `subType`; optional inline content. | Attribute-only atomic directives may omit content. |

### Blocks

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `horizontalRule` | No content field. | Horizontal rule separating document sections; recommended HTML `<hr>`. |
| `blockquote` | Blocks. | Body contains ordinary blocks. |
| `list` | Boolean `ordered`; `children: ListItem[]`. | Optional integer `start` (default 1 when ordered), boolean `tight` (default false). `start` is nonnegative. |
| `listItem` | Blocks. | Optional boolean `checked`; absent means ordinary item. |
| `code` | String `value`. | Optional string `language`, literal string caption `title`, `attributes` and string uninterpreted `meta`. Code notation stays in value. |
| `lineBlock` | Inline content. | Boundaries use `break`, including within emphasis. `value: ""` means one empty represented line. A `value` containing an LF is not valid line-block shorthand. |
| `container` | String `subType`; blocks. | Optional structured `title`. All colon containers share this family, including nested/custom types. |
| `leaf` | String `subType`; no main content field. | Optional structured `title` for a directive label; “leaf” denotes bodyless authoring scope, not an assertion about title descendants. |

### Tables and wrappers

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `table` | `children: TableRow[]`. | Optional `align: ("left"\|"center"\|"right"\|null)[]`, structured caption `title`. |
| `tableRow` | `children: TableCell[]`. | Structural row grouping. |
| `tableCell` | Exactly one of `value`, inline `children`, or block `body`. | Optional boolean `header`, default false; positive integer `colSpan`/`rowSpan`, default 1; string/flag attributes hold widths and styling. |
| `group` | `children: Node[]`; `display: "inline"\|"block"`. | Generic structural wrapper; optional native wrapper `tag` is `span` or `div`, consistent with display. |
| `html` | String `value`; `display: "inline"\|"block"`. | Supported safe HTML after allowlist filtering; never includes discarded unsafe content. |
| `literal` | String `value`; `display: "inline"\|"block"`. | Preserved invalid/uninterpreted source for recovery, escaped for display. |
Block content admits paragraph, heading, quote, list, code, line block, table,
container, leaf, horizontal rule and block-display group/HTML/literal.
Inline content admits text, inline formatting, inline code, link, image,
break/soft break, inline directive and inline-display group/HTML/literal.
`title` is a designated title-field node, not an ordinary paragraph body child.
Lists contain list items; tables contain rows; rows contain cells. Tabs and their content share the container family. Consecutive `tab` siblings normalize into a `tabs` container, as described in the language draft. These constraints supplement the generic field exclusion.

### Recognized semantic subtypes

The [recognized semantic subtype registry](/expressive-markdown/language#recognized-semantic-subtypes)
defines the shared vocabulary: container `note`, `tip`, `warning`, `danger`,
`details`, `figure`, `tabs`, `tab`, `toc`; inline `chip`, `mention`.
A mention has an optional string `ref` field for its entity target. The shared
node families allow generic traversal; subtypes supply specific meanings.
Custom subtypes are valid but do not acquire a standard subtype's contract.

| Feature | AST shape | Content and presentation data |
| --- | --- | --- |
| Chip | `inline`, `subType: "chip"` | `value` or inline `children`; `attributes.tone` for neutral/blue/green/yellow/red/purple or a preserved custom tone. |
| Mention | `inline`, `subType: "mention"` | Authored label/handle in `value`/`children`, excluding the `@` marker. Optional string `ref` targets an entity; optional `attributes.url` supplies navigation. Label-only mentions are valid. Generic `id` identifies this occurrence. |
| Tabs | `container`, `subType: "tabs"` | `container/tab` children in `body`; optional group title and `group`, `default`, `queryString`, `lazy` attributes. Automatic groups have no authored settings/title/ID. |
| Tab | `container`, `subType: "tab"` | Structured title, block `body`; optional string `attributes.value` is selection identity, distinct from generic node ID. Code is ordinary body content. |
| Table of contents | `container`, `subType: "toc"` | Optional structured `title`; readable navigation blocks in `body`. Depth/format settings guide an optional editor/converter refresh that updates the actual body. |

```json
{
  "type": "inline",
  "subType": "chip",
  "value": "Ready",
  "attributes": {"tone": "green"}
}
```

Both mention spellings have the same structural contract:

```json
{"type": "inline", "subType": "mention", "value": "Ada Lovelace"}
```

```json
{"type": "inline", "subType": "mention", "value": "ada-lovelace"}
```

They correspond to `@[Ada Lovelace]` and `@ada-lovelace`. Neither requires a stored entity reference. Source `@[Ada Lovelace]#user-123` adds string `ref: "user-123"` directly on the node. It never becomes a generic node attribute or the node ID. The general source `{ref="…"}` alias maps to that same field, without duplication.

A formatted chip uses `children` instead of `value`, for example a `strong`
child. An unknown subtype keeps the same data shape and remains valid. See [rendering recommendations](/expressive-markdown/presentation) for HTML and
interactive presentation.

### Automatic tab groups

```json
{
  "type": "container",
  "subType": "tabs",
  "body": [
    {"type": "container", "subType": "tab", "title": {"type": "title", "value": "npm"}, "body": [{"type": "code", "language": "sh", "value": "npm install example-package"}]},
    {"type": "container", "subType": "tab", "title": {"type": "title", "value": "pnpm"}, "body": [{"type": "code", "language": "sh", "value": "pnpm add example-package"}]}
  ]
}
```

Adjacent tabs and an explicit `tabs` wrapper produce this same group structure.
Blank source lines do not split an automatic group. Explicit groups additionally
retain authored settings, title and ID, and are not wrapped again. A tab missing
its required readable title is incomplete: preserve it and recommend a diagnostic.

### Native HTML and rich editor data

HTML is filtered using a maintained sanitizer allowlist for elements, attributes
and URLs. Parsing discards `script` elements and their contents; writers never
replay discarded unsafe content. The exact sanitizer preset is still to be
selected. Report filtering losses, and exclude discarded unsafe content from
round-trip guarantees.

Map supported safe HTML to its structured nodes: paragraphs, headings, lists,
quotes, images, links, tables, details and figures. Use a `group` for a safe
`span`/`div` that supplies grouping or styling without a stronger meaning. Other
supported safe HTML may remain an `html` node.

An integration documents which safe HTML it maps and which it retains as a
string. Keeping an HTML string does not establish editable support. Preserve
supported native attributes; when ordinary Markdown cannot express them, write
supported safe HTML or report the unsupported conversion.

### Table grid

Rows contain originating cells only; merged-away slots are not nodes. Place a
cell at the first free column, skipping slots covered by row spans from preceding
rows. Its rectangle covers `colSpan` columns and `rowSpan` rows, each defaulting
to 1. Rectangles cannot overlap, extend beyond the table or cross its header/body
boundary. Every row must resolve to the same grid width. An empty `children`
array is valid for a row fully covered by spans above it.

When `align` is supplied, its length is the grid width; otherwise the first
row establishes the width. Cell header booleans describe header status, not
implicit row-span permission. Native HTML span attributes map to numeric span
fields; do not duplicate them in `attributes`. Safe HTML outside this grid model remains `html` or produces an
unsupported-import diagnostic.

For the merged body in the language example, the rows are:

```json
[
  {
    "type": "tableRow",
    "children": [
      {"type": "tableCell", "colSpan": 2, "rowSpan": 2, "value": "Release checks"},
      {"type": "tableCell", "value": "Ready"}
    ]
  },
  {"type": "tableRow", "children": [{"type": "tableCell", "value": "Verified"}]}
]
```

The preceding header row establishes three columns. Marker spelling and the
rightmost source location of horizontally merged content are lexical details;
the semantic cell starts at the rectangle's top-left position.

## Serialization, extensions and diagnostics

JSON serialization preserves every semantic field. JSON object-key order is not
semantic; node array order is. Unknown semantic `subType` values remain valid.
Unknown structural node types may be retained as extension nodes with the same
generic field rules; a converter lacking a source mapping reports unsupported
conversion instead of discarding them. Extensible structure does not authorize
arbitrary new traversable slots.

Diagnostics belong beside the document, not inside its content. Tools can return
a document together with diagnostics and optional source records; this reference
does not prescribe their API. See [expressmark](https://github.com/nextwebwg/expressmark)
for the JavaScript tooling project.

Round-tripping preserves supported semantic data, not necessarily byte-identical
Markdown. Application-only IDs without a source attachment cannot always be
written; report that limitation. Discarded unsafe HTML is never restored.
See [writer rules](/expressive-markdown/parsing#writing-and-preservation) for
canonical output and preservation boundaries.
