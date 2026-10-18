---
title: Parser & Writer Rules
order: 3
blurb: boundaries · recovery · preservation
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Parser & Writer Rules

Use these rules to implement a parser or writer: recognize source boundaries,
build the [document AST](/expressive-markdown/ast), recover invalid input and
write equivalent Markdown. Each section defines one feature's exact behavior.
For author-facing examples, start with [Language & Semantics](/expressive-markdown/language).
HTML conversion recommendations are informative.

## Parsing order

1. Normalize CRLF/CR to LF; retained positions refer to original input.
2. Recognize optional opening frontmatter, then CommonMark blocks, containers, leaf directives, tables and line blocks in their enclosing block context.
3. Parse inline content after block boundaries.

Code spans, fenced/indented code and HTML blocks retain their lexical boundaries;
their contents do not open directives or line blocks. GFM tables take precedence
over leading-pipe line blocks. Escaped structural punctuation stays literal.
Apply the [safe HTML policy](#safe-html) when importing HTML and before writing it.

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

Frontmatter is optional. Its unindented `---` delimiters must start the document, apart from an optional Unicode byte-order mark; no preceding blank line. Trailing horizontal whitespace on delimiters is accepted. An empty block means an empty mapping and produces no body HTML.

| Field | Contract and AST destination |
| --- | --- |
| `id` | String → `document.id`, unchanged. |
| `title` | String parsed as inline Markdown → structured `document.title`. |
| `description` | Inline-Markdown string → `document.metadata.description`. |
| `tags` | List of strings → `document.metadata.tags`; no comma splitting. |
| Other keys | Exact key spelling and supported value → `document.metadata`. |

Use YAML 1.2 Core interpretation with JSON-compatible values: strings, finite numbers, booleans, null, lists and string-keyed objects. Keys are case-sensitive; `yes`/`on` and quoted scalars stay strings. Explicit tags, cyclic aliases, non-string keys and non-finite numbers are unsupported. Acyclic aliases resolve to ordinary values without preserving alias identity.

Each field has one home: no duplicate root ID/title in metadata. Custom keys cannot replace AST structure: YAML `version: product-v2` becomes `metadata.version`; root `version` remains integer `1`. Description stays a metadata string, outside generic node traversal.

Plain-text projection concatenates readable inline text, link labels, image alternative text and code text; breaks become spaces and formatting delimiters disappear. Duplicate exact YAML keys are invalid YAML: diagnose and recover using the final value. Preserve other invalid/unsupported blocks as recoverable source; never guess or discard their values.

## Named constructs

```md
:::warning[Before deploying]{#check}
::: warning {#check} [Before deploying]
```

Both open the same container. The type comes first; optional title and attributes may follow in either order on **one source line**. Writers use `::: type [Title] {attributes}`. Unbracketed container titles are outside the core.

| Rule | Accepted form |
| --- | --- |
| Identifier | ASCII letter, then ASCII letters, digits, `_` or `-`. Types become lowercase; attribute names use the mapping below. Text, values and IDs retain Unicode. |
| Container spacing | Zero–three spaces of block-relative indentation; optional spaces/tabs after colons and between header parts. |
| Wrappers | No padding inside the outer `[…]` or `{…}`; internal word/attribute separation remains meaningful. |
| Label/title | Inline Markdown. Escapes protect brackets, braces and backslashes; balanced inline link/code syntax does not close the label early. |
| Inline/leaf scope | `:type[label]{attributes}` / `::type[label]{attributes}`. Inline needs a label or attributes, so bare `:word` stays text. Leaf occupies its own line. |
| Repetition | Multiple attribute lists concatenate in source order. Repeated container title wrappers are malformed. |

**Nesting uses longer outer fences:**

```md
:::: note [Outer]

::: warning [Inner]
Check the configuration.
:::

::::
```

A fence has at least three colons. Direct children use fewer than their parent; closing lines contain only the matching colon run and optional horizontal whitespace. Code markers stay code; nested lists, quotes and code remain valid.

Writers use `3 + maximum descendant container depth` colons, recalculating within each body, and escape accidental delimiter lines in literal content. Unclosed/mismatched regions follow [recovery rules](#recovery-and-diagnostics).

> [!note] Readable spacing adds no blank line
> Blank source lines immediately inside container fences are ordinary spacing. They do not request visible empty lines; use a [line block](/expressive-markdown/language#leading-pipe-line-blocks) for those.

## Attributes and identity

```md
{#deployment-check open audience=admin label="Before deploying"}
```

| Source | AST value |
| --- | --- |
| `open` / `!open` | Boolean `true` / `false`. |
| `open=foo` | String `"foo"`. |
| `open=false` / `open="false"` | String `"false"`, never boolean. |
| `#check` / `id=check` | Node `id: "check"`. |

- Separate entries with spaces/tabs, `&`, or both. Tight `{a=1&b=2}` is valid.
- Outside quotes, `&` is a separator. Unquoted values are nonempty and end at
  whitespace, `&` or `}`.
- Assigned values stay strings, whether unquoted or single/double-quoted. Quote
  whitespace, ampersands, braces or quote delimiters.
- `key=""` is an empty string; `key=` is malformed.
- In quotes, backslash escapes the active quote/backslash; other backslashes
  remain literal.

Source names are case-insensitive; AST attribute keys use camelCase. Lowercase the source name, split at hyphens, and join the nonempty parts, capitalizing the first ASCII letter of each part after the first. Digits and underscores remain unchanged. For example, `SHOW-LINE-NUMBERS` becomes `showLineNumbers`, and `query-string` becomes `queryString`. Resolve duplicate/conflicting entries after this mapping. Values and IDs remain exact. Ordinary entries live in `attributes`, the effective ID once in `id`. Every AST node may carry an ID; this does not create source attachment syntax everywhere.

> [!note] Duplicates are valid
> Repeated/conflicting attributes use **last occurrence wins**, including ID shorthand versus assignment. Recommend a warning. Authored duplicate IDs are also preserved; never normalize or renumber them.

**Attachment:**

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 placement=center responsive}
[Release notes](release.md){class="release-link"}
```

A heading's final whitespace-separated list attaches to the heading. An immediately adjacent list attaches to a completed image/link. Attachments stay on the target's source line; code-span whitespace is not attachment syntax. Multiple lists resolve in source order; malformed lists stay literal. Escape `{` to prevent attachment. Code-fence attributes are described in the [language guide](/expressive-markdown/language#code-blocks-and-presentation-metadata); other block styling uses supported safe HTML.

| Recommended HTML mapping | Behavior |
| --- | --- |
| `id`, `class`, `style`, supported native attributes | Supported safe native equivalents; convert camelCase keys back to dash-separated names where applicable. Filtering is reported. |
| Other string attributes | `data-*` using the dash-separated name; retain an existing `data-` prefix (AST `dataFoo` → HTML `data-foo`). |
| Custom true/false flags | Present empty `data-*` / omitted attribute. |
| Native boolean attributes | True or any assigned string means present; false means omitted. `"false"` therefore still enables it. |
| Conversion-owned `data-type` (AST `dataType`) | Identifies the construct. Preserve a colliding authored value in the AST and diagnose instead of replacing output identity. |

Unknown attributes remain data. An arbitrary flag does not acquire native HTML behavior.

## Automatic tab grouping

After block parsing, normalize each document/container/quote/list-item/cell block array independently. Replace each maximal run of `container/tab` siblings with one `container/tabs` whose `body` contains the original tabs in order. Blank source lines produce no separating content node. A non-tab node ends the run; groups never cross a block-context boundary. A single tab is a one-item group.

When normalizing an explicit `tabs` body's direct children, retain its tab children directly rather than introducing another implicit group. Preserve nested groups inside each tab's body normally. Explicit neighbouring `tabs` groups remain separate. Derived groups have no authored ID, title or attributes. Source positions may cover the run; they do not create authored identity.

Canonical writers omit the group wrapper when no authored group settings, title or ID need representation and doing so preserves group boundaries. Keep an explicit wrapper where adjacent groups would otherwise merge. Otherwise write a normal `tabs` container with nested `tab` containers and matching fence lengths. A tab's title is inline Markdown and its selection value is string `attributes.value` or its title's plain text.

## Mention shorthand

| Source | AST content |
| --- | --- |
| `@[Ada Lovelace]` | `inline`, `subType: "mention"`, `value: "Ada Lovelace"`. |
| `@ada-lovelace` | Same family/subtype, `value: "ada-lovelace"`. |
| `@[Ada Lovelace]#user-123` | Same label, plus node `ref: "user-123"`. |
| `@ada-lovelace#user-123` | Bare handle label plus the same node `ref`. |
| `:mention[Ada Lovelace]` | Equivalent generic named form. |

The `@` marker is syntax, not part of the label value. A bracketed mention uses the ordinary inline label grammar and optional immediately adjacent attribute lists. A bare handle starts with a Unicode letter, number or `_`; it continues through Unicode letters, combining marks, numbers, `_` and `-`. Preserve label casing and Unicode exactly. Bare handles also accept immediately adjacent attribute lists.

Recognize shorthand only when `@` is not immediately preceded by a letter, combining mark, number, `_`, `-`, `.`, `/` or another `@`. Escaped markers, code, raw HTML and link destinations retain their lexical rules; existing CommonMark/GFM email/URL recognition takes precedence. Invalid bracket/handle structure stays literal under local recovery.

An immediately adjacent `#reference` suffix belongs to the mention, before optional attribute lists. Its token uses the same characters as a bare handle; sentence punctuation such as the final `.` is excluded. A `#` without a valid reference token stays literal after the otherwise valid mention. The suffix maps to the optional string field `ref`, not `id` or `attributes.ref`. It is an opaque entity reference, not implicitly a URL fragment.

For references containing other characters, the general form `:mention[Ada Lovelace]{ref="org/user-123"}` or `@[Ada Lovelace]{ref="org/user-123"}` remains available. The recognized string `ref` attribute is promoted to the node field, not duplicated in `attributes`. A suffix followed by a `ref` assignment resolves in source order, last occurrence wins. Unsupported non-string `ref` values preserve recoverable source and recommend a diagnostic rather than inventing a target.

A missing target is valid. Host resolution does not implicitly populate `id` or `ref`. Generic `{#id}` still identifies this occurrence independently. Writers prefer `@[label]#reference{attributes}` when a reference fits the suffix grammar, the full-string attribute form otherwise, and omit absent parts. Optional provenance may retain bare spelling.

## Leading-pipe line blocks

```md
| First line
| Second line
|
| Fourth line
```

Each `| ` or pipe-plus-tab starts a represented line; a bare `|` requests an empty line. `|Text` stays ordinary text. Allow zero–three spaces of block-relative indentation; strip marker separation and additional leading whitespace. Indentation is not visual indentation.

| Source situation | Meaning |
| --- | --- |
| Adjacent pipe lines | One `lineBlock`, preserving divisions. |
| Blank line between pipe lines | One empty represented line, equivalent to a bare pipe. |
| Blank line before following Markdown, at a container boundary or at document end | Ordinary spacing. A bare pipe explicitly adds an empty line there. |
| Nonempty indented continuation after a nonempty represented line | Strip indentation and join with one space; no new represented line. A blank source line interrupts this eligibility. |
| Nonempty unindented line without a marker | Ends the line block, even without a blank separator. |

```md
| One sentence wrapped
  across source lines.
| Another represented line.
```

Inline formatting may span represented lines; boundaries remain `break` nodes within that formatting. Inline code spans fit within one represented line. Escape a literal pipe or put it in code.

Parse the payload of each represented line as inline content, never as another
block. Thus `| 1. item`, `| - item` and `| # item` contain literal block markers;
they do not create lists or headings. Inline escapes remain valid within the
payload, but escaping those block markers is unnecessary.

Recognize a GFM table only when its header and delimiter row meet the table
grammar. A trailing pipe alone does not establish a table. For example,
`| - one item |` followed by `| - second item |` is a line block, with each
trailing pipe retained as text. Once a table is established, its pipes delimit
cells and cannot also serve as line-block markers inside those cells.

The AST uses `lineBlock.children` with `break` nodes; consecutive/leading/trailing breaks preserve empty lines. A single plain line may use `value`; a single bare pipe uses `value: ""`.

**Recommended HTML:** `<p>` with `<br>` boundaries and preserved inline wrappers. Append one layout `<br>` for a terminal empty line, or for an entirely empty one-line block, so HTML does not absorb it. This extra layout break is not an AST break. Explicit empty lines add to normal paragraph spacing.

> [!note] Why a leading pipe?
> It is visible and marks the line it affects. CommonMark trailing spaces are invisible; its trailing backslash forces a break where languages such as Python use one to continue a line. Both CommonMark hard-break forms remain accepted as `break`; writers prefer line blocks.

## Tables

The preferred source forms for all tables are list-based rows within a
`table` container. A named first record establishes titled columns and supports
later named or positional rows. An unnamed first row uses positional cell lists.
Traditional GFM pipe syntax remains accepted. All forms normalize to `table`
→ `tableRow` → `tableCell`, not generic containers or structural list nodes.

### Named fields and column identity

```md
::: table

- Task: Install
  Instructions:
    1. Download the package.
    2. Run the installer.

- Notes: Check the version.
  Task: Verify

:::
```

::: {.render title="Resolved named columns" height="280"}
```html
<table><thead><tr><th scope="col">Task</th><th scope="col">Instructions</th><th scope="col">Notes</th></tr></thead><tbody><tr><td>Install</td><td><ol><li>Download the package.</li><li>Run the installer.</li></ol></td><td></td></tr><tr><td>Verify</td><td></td><td>Check the version.</td></tr></tbody></table>
```
:::


A named record is an outer unordered-list item beginning with a field label
and `:` followed by whitespace or the end of the line. Additional field labels
align with the start of the first label, relative to that list item. A field
body starts after its separator or on indented continuation lines. Writers
indent continuation blocks two spaces beyond the label column. Blank lines
within a field do not end the record. A line at label indentation must start
a field; deeper lists, fenced code and colon-bearing text remain cell content.
Lexical code boundaries take precedence over field recognition.

Labels are nonempty plain-text strings on one line, ending at the first
unescaped `:` followed by whitespace or line end. Backslash escapes protect
literal punctuation in a label. Decode those escapes and trim surrounding
horizontal whitespace; otherwise compare exact Unicode strings, without case
folding or Unicode normalization. Labels are not YAML, inline Markdown, or
namespaced attributes. Values use ordinary Markdown block parsing, with no
YAML scalar typing.

Build one ordered column registry over the entire container:

1. The first named record establishes columns in field order. A name's first
   appearance defines its index. The original label becomes header-cell text.
2. In every named record, assign by **name**, never assignment order. An existing
   name always selects its registered column. A new name appends a column.
3. Omitted fields are empty cells. An explicit label with no body also assigns
   an empty cell. New columns add empty cells to preceding records; they never
   shift earlier column indices.
4. A later positional row assigns by index in the registry order. Omitted
   trailing positions are empty; interior omissions need explicit empty items.
   More positional cells than columns established at that point is malformed,
   not permission to invent column names. A table beginning with unnamed
   positional data cannot acquire named records later; establish names first.
5. A duplicate assignment to the same name within one record is malformed.
   Preserve the whole table as recoverable literal source rather than discard
   one value or fabricate another column.

Compilers may warn about similar names such as `Instruction` and `Instructions`.
This is an advisory about **two distinct columns**, never authorization to merge
or rename them, fail an otherwise valid table, or fall back to matching by
position. Diagnostics should identify both names and source locations.

After discovering all columns, prepend one header row containing their labels
and place each record's values in registry order. This is the named form's
implicit header; `header` is redundant and `!header` is malformed for that form.
For untitled columns, use the positional form instead. The resolved names are
header content, not a second schema or a second renderer matching operation.

### Structural lists and cell bodies

```md
::: table

- - First cell
  -
    - A bullet inside the second cell.
    - Another bullet in that same cell.

:::
```

1. Parse the container body using CommonMark list indentation and block rules.
   An empty body produces an empty table. Otherwise it contains one unordered
   outer list, with no other sibling blocks. Its items define source records
   or positional rows; recognize the first item's named/positional form before
   interpreting its body.
2. Each positional row contains exactly one unordered nested list, whose items
   define cells. Row and cell list items are unchecked structural items. A missing cell
   list or other direct row content is malformed, rather than guessed to be a
   cell. Blank lines are ordinary source spacing, not additional rows or cells.
3. Consume **exactly these two structural list levels**. Every cell item's body
   is parsed as ordinary Markdown blocks, including deeper lists, multiple
   paragraphs, quotes, line blocks, fenced code and nested tables. A blank cell
   item is an empty cell. Do not consume a deeper list as more table structure.
4. Nesting depends on block-relative list indentation, not absolute document
   columns or alignment with cells in other rows. The common `- - value` form
   opens a row and its first cell on one line. Writers use `-` markers and
   two-space increments for the structural levels; cell blocks use ordinary
   list-item continuation indentation. Code retains its lexical boundaries.

Recognize whole-cell merge markers from their unescaped cell source before
interpreting them as ordinary block content. This special case never consumes
a marker inside a code span, fence, quote body or a larger cell value.

A cell can use compact `value` or inline `children` for one ordinary paragraph
when no paragraph identity or supported data would be lost. Otherwise retain
its blocks in `body`. Preserve deeper lists and code as blocks, never joined
text. Literal paragraphs beginning with list markers use the usual escapes;
there is no user-supplied serialization flag.

For a wholly unnamed positional table without merges, the source width is the
largest cell count. Pad shorter rows with empty cells; do not discard extra
cells. Named tables instead use their registry and mixed-row rules above.
With merge markers, positional rows must explicitly provide every grid slot,
including covered slots. Named records resolve to their full registry width,
including empty cells for omitted fields, before merge processing. The table
caption and ID come from the container title and attributes normally.

### Header, transpose and alignment settings

| Container setting | Source interpretation | Normalized AST |
| --- | --- | --- |
| `header` | Positional form: first source row contains header cells; default false. Named form: implicit header row; true is redundant, false is malformed. | `tableCell.header: true` on those originating cells. |
| `transpose` | Boolean flag; swap source rows and columns after merges. Default false. | Actual transposed `tableRow`/`tableCell` placement, with swapped spans. |
| `align="left,right"` | Comma-separated displayed-column alignments, applied after transposition. | `table.align`, using null for `-`. |

An omitted or negated `transpose` means false. Positional `header` defaults to
false; named records supply their implicit header without that flag and cannot
negate it. Assigned strings are not boolean flags;
invalid `header`/`transpose` values are malformed table settings. Alignment
entries are `left`, `center`, `right` or `-`, with optional surrounding spaces.
One entry applies to all displayed columns; otherwise the count must match the
nonempty displayed width. Omitted alignment means the default. Invalid tokens
or counts are malformed, not silently truncated.

Generate the named header row, or apply positional header status in source
coordinates, then resolve merges, transpose if requested and apply
displayed-column alignment. Thus `{header transpose}`
places headers in the first displayed column. Transposition moves complete
cells and swaps `rowSpan`/`colSpan`; it never reparses content or changes list
semantics. It preserves every cell ID exactly once. Source-control settings
`header`, `transpose` and `align` are consumed into these semantic fields, not
stored as duplicate table attributes that a renderer would apply again.
Optional source provenance may retain the original orientation and settings.
Other supported table attributes remain ordinary attributes.

Named field labels define column identity at parsing time. Positional header
content does not: preserve duplicate or empty labels as authored. With
positional `header`, padded empty cells in the first source row are header
cells too. Do not accept named records in a wholly positional table by guessing
keys from its header content.

### Merge grid

Positional cell lists and traditional pipe tables recognize these marker-only
cells. In named assignments, marker-looking values remain ordinary content:

| Marker | Meaning in the source grid |
| --- | --- |
| `>` | Merge into the next ordinary cell to the right. Consecutive markers join that cell. |
| `^` | Continue the cell above. Cover every column of a horizontal span. |
| Empty cell | Empty content, never a merge. |
| `\>` / `\^`, or inline code | Literal marker text. |

Markers match the entire unescaped cell after trimming source spacing. Resolve
horizontal runs first, then vertical continuations on the original columns.
A `>` run must end in an ordinary cell on that row, not `^`.

Merges form non-overlapping rectangles, consume only marker slots and never
cross the header/body boundary. In pipe syntax, delimiter rows cannot merge.
Repeated `^` rows extend the originating cell. Invalid merges or malformed
list-table structure/settings preserve the **whole table** as block `literal`
source and recommend a diagnostic; do not partially transpose or drop content.

The AST contains originating cells only, in displayed row and column order.
Place each at the first unoccupied column, skipping prior row spans. Spans are
positive integers, default/omitted `1`. Caption, ID, cell content and supported
metadata survive normalization. Numeric structural fields do not change the
string-only assigned-attribute rule.

### Traditional pipe compatibility

```md
| First | Second | Status |
| --- | --- | --- |
| > | Release checks | Ready |
| ^ | ^ | Verified |
```

GFM supplies header/delimiter recognition, inline cells, alignment and ordinary
row-width behavior. Tight `|>`/`|^` merge forms also work. Merge markers use the
grid rules above and require explicit equal slot counts before GFM
padding/truncation. The pipe form's inline parsing is a source-format
restriction, not a restriction on the Expressive table model.

### Writing tables

Prefer list-based forms for all representable tables, including short values.
Named rows are suitable for unique, nonempty plain-text headers without merges;
write fields in column order and omit empty fields or assign explicit empty
bodies. Positional cell lists support untitled or complex headers and merges.
Both forms use ordinary Markdown inside each cell.
Indent every continuation line for its cell; choose container fences longer
than nested container fences. An empty cell uses an empty structural item.
Escape literal whole-cell merge markers and any ordinary block punctuation
that would change a literal paragraph into another block.

Writers can preserve a transposed source orientation when provenance records
it. In that case, write the inverse grid and appropriate source form, then
emit `transpose`; never emit the flag on an already transposed source grid.
The resulting AST and displayed layout must stay the same. Without source
preference, row-oriented source is the canonical default. Named output derives
labels from the header cells and values from their columns; it must not rematch
cells or retain a stale registry after a header edit. Use `header` only
when the originating header cells are exactly the first source row; do not
invent, remove or infer header status from text formatting.

When only the first displayed column contains headers, a writer can use
`{header transpose}` and the inverse grid to preserve that pattern even without
source provenance. A header pattern that neither orientation expresses uses
the preservation fallback below.

Pipe output remains permitted for compatibility, provided it preserves content,
headers, alignment, spans and identities. When table/row/cell identities,
header patterns or supported presentation cannot be expressed in a chosen
form, use supported safe HTML or report unsupported conversion. Never flatten
rich cells or erase metadata merely to fit shorthand syntax.

**Recommended HTML:** native `<table>`, `<tr>` and `<th>`/`<td>`, with suitable
header/body grouping, spans, alignment and supported presentation attributes.
Keep header cells semantic when transposed into a column. Do not infer complex
accessible header associations solely from visual position.

## Code presentation

Code attributes share the ordinary string/flag grammar and camelCase key mapping. `title` maps once to `code.title`; other attributes remain in `attributes`.

- `highlight` is a comma-separated string of positive line numbers or ascending inclusive `start-end` ranges. Repeated/overlapping selections form a union. Numbers refer to original `code.value` lines, starting at 1.
- `showLineNumbers` is a boolean setting; `true` shows numbering from 1 and `false` hides it. A string assignment stays a string, not a boolean.
- Invalid feature values or out-of-bounds ranges remain in the AST, recommend a diagnostic and use the baseline default: no line emphasis or numbering. They do not make the attribute list malformed.
- Unrecognized info tokens remain uninterpreted `meta`; optional provenance retains the full original info string. Canonical writers regenerate known metadata and append unknown tokens.
- Annotation comments are literal source. Profiles may explicitly map imported conventions, but the core does not interpret Docusaurus, VitePress or Shiki spellings automatically.

Recommended HTML escapes literal code. Per-line decoration must preserve the code's text and line divisions; copied code excludes generated line-number labels. A profile that cannot display a setting preserves it and reports the unsupported presentation.

## Safe HTML

HTML import and output use a maintained sanitizer allowlist for elements,
attributes and URLs, rather than a hand-written blacklist. The exact preset
remains to be selected.

- Discard `script` elements **and their contents** during parsing. They never
  appear in the semantic document or subsequent Markdown output.
- Map supported safe HTML to structured nodes where possible. Other supported
  safe markup may remain an `html` node with its inline/block display context.
- Apply the policy to supplied AST HTML and presentation attributes when writing;
  do not trust them merely because they arrived as document data.
- Report filtering and unsupported conversion. Never replay discarded unsafe
  content from provenance, recovery or source-preservation records.

The policy does not alter literal code examples: HTML written inside a code
span or code block remains inert code text. A preserved `literal` recovery node
is escaped text, not executable HTML.

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

| Input | Recovery |
| --- | --- |
| Unknown type/key | Valid; preserve it. |
| Duplicate attributes | Valid; final occurrence wins. Recommend a warning. |
| Invalid directive opener/attachment | Local literal text; do not consume unrelated following content. |
| Unclosed container or mismatched nesting | `literal` node preserving the region through its enclosing block context; code retains lexical precedence when locating boundaries. |
| Opening `---` without a close | Ordinary Markdown. |
| Delimited but invalid/unsupported frontmatter | Entire block as `literal`; no guessed metadata. |
| Invalid merged table | Whole table as block `literal`. |

Recovery nodes keep original source in `value` and a `display` context. Recommend escaped inline text or block text with visible source-line breaks. Recovery is not an executable-content mechanism.

Diagnostics remain separate from document content. Suggested records contain code, severity, message, optional position and node ID; this is tooling guidance, not a mandatory API. Recommend warnings for duplicate attributes/IDs and invalid feature values.

Tools may warn on unquoted `open=true`/`open=false` and suggest `{open}`/`{!open}`.
Quoting suppresses this advisory. Assigned values remain strings either way.

## Writing and preservation

Round-tripping preserves meaning, order, explicit lines, authored IDs, unknown
types, supported metadata and presentation. Discarded unsafe HTML is excluded
and must never be restored from source records. Byte-identical output is
optional; it needs original whitespace, quotes, overwritten attributes, link
references and delimiters.

| Writers use | Preserve |
| --- | --- |
| Lowercase directive names and dash-separated attribute names from camelCase AST keys; optional ` & ` separators | Values and metadata key casing. |
| `::: type [Title] {attributes}`; no wrapper padding; one blank line around body | Content, with nested fence lengths calculated from depth. Escape literal structural punctuation. |
| Double quotes when strings need quoting; `{name}` / `{!name}` flags | Explicit false versus omission/default. |
| Leading-pipe lines and bare empty pipes | Represented line divisions. |
| Regenerated table markers; escaped literal markers | Numeric spans and originating cell IDs. |
| YAML strings for title/ID; string lists for tags | Custom metadata, quoting strings YAML would otherwise type differently. |

### Text and formatting boundaries

Literal AST text must stay literal after reparsing. For example, write an AST
value containing the six characters `&copy;` as `&amp;copy;`, so it does not
become ©. This does not change CommonMark entity interpretation in authored source.

Preserve whitespace inside formatting, adjacent/nested formatting boundaries,
and empty or whitespace-only paragraphs. Use supported safe HTML when Markdown
delimiters or blank source lines would change that content:

```md
<strong>Hello </strong>@[Ada]#user-123

<p></p>

Use &amp;copy; literally.
```

These forms parse back into the same structured nodes. Ordinary bold text still
uses `**bold**`; extra blank source lines remain ordinary paragraph spacing.

### Literal block markers

Writers determine syntax from the final node type and its enclosing context.
They must not infer a list solely from text beginning with a list marker, or
require a user-supplied serialization flag.

| Node and literal content | Source example | Reparsed node |
| --- | --- | --- |
| Ordered list with item “item” | `1. item` | Ordered `list`. |
| Bullet list with item “item” | `- item` | Unordered `list`. |
| Level-three heading “1. item” | `### 1. item` | `heading`, level 3. |
| One represented line “1. item” | `\| 1. item` | `lineBlock`. |
| Two represented lines “- one item”, “- second item” | `\| - one item` followed by `\| - second item` on the next source line | One `lineBlock` with a `break`. |
| Ordinary paragraph “1. item” | `1\. item` | `paragraph`. |
| Ordinary paragraph “- item” | `\- item` | `paragraph`. |
| Paragraph “1. item” or “- item” in a rich cell body | `1\. item` / `\- item`, within that body | `paragraph`. |

For line blocks, prefer the leading-pipe form without redundant escapes of list
or heading markers. Preserve inline Markdown escaping where needed. For ordinary
paragraphs, escape punctuation that would otherwise start a different block,
including the period in a leading ordered-list marker. Do not silently change a
`paragraph` into a `lineBlock`: the latter also records explicit line divisions.
An editor adapter that maps a deliberately literal line to `lineBlock` makes
that choice before serialization. Reversing an editor's automatic formatting
must survive export and import as literal content.

Rich cell bodies preserve list nodes and literal paragraph text under the same
rules as other block bodies. In compact pipe source, the pipes that delimit
cells cannot also act as line-block prefixes. List-based forms delimit a rich
cell before parsing its block content, so a line block inside that cell remains
valid ordinary Markdown.

Code fences follow CommonMark backtick/tilde rules and exceed conflicting delimiter runs in their literal content. Parsers should prefer compact `value` for wholly literal inline content, but supplied text-only `children` remain valid. Normalization must not lose child IDs, attributes or provenance.

Optional AST fields accept null as absence and serialize as omission; null metadata stays data. Required root `version` must be supported or conversion stops with a clear error. See the [AST contract](/expressive-markdown/ast).
