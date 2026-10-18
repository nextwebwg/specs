---
title: Parser & Writer Rules
order: 3
blurb: boundaries · recovery · preservation
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Parser & Writer Rules

Implementation details for the [language guide](/expressive-markdown/language): lexical boundaries, document data, recovery and canonical writing. These rules form part of the Stage 0 language contract. HTML conversion remains informative.

## Parsing order

1. Normalize CRLF/CR to LF; retained positions refer to original input.
2. Recognize optional opening frontmatter, then CommonMark blocks, containers, leaf directives, tables and line blocks in their enclosing block context.
3. Parse inline content after block boundaries.

Code spans, fenced/indented code and raw HTML blocks retain their lexical rules: their contents do not open directives or line blocks. GFM table recognition takes precedence over a leading pipe. Escaped structural punctuation stays literal.

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

Entries are separated by runs of spaces/tabs, `&`, or both, including tight forms such as `{a=1&b=2}`. `&` is a separator outside quoted values, never part of an unquoted value. Assigned values are strings, unquoted or single/double-quoted. Unquoted values are nonempty and end at whitespace, `&` or `}`; quote whitespace, ampersands, braces or quote delimiters. Use `key=""` for an empty string; `key=` is malformed. In quoted values, backslash escapes the active quote/backslash; other backslashes remain literal.

Source names are case-insensitive; AST attribute keys use camelCase. Lowercase the source name, split at hyphens, and join the nonempty parts, capitalizing the first ASCII letter of each part after the first. Digits and underscores remain unchanged. For example, `SHOW-LINE-NUMBERS` becomes `showLineNumbers`, and `query-string` becomes `queryString`. Resolve duplicate/conflicting entries after this mapping. Values and IDs remain exact. Ordinary entries live in `attributes`, the effective ID once in `id`. Every AST node may carry an ID; this does not create source attachment syntax everywhere.

> [!note] Duplicates are valid
> Repeated/conflicting attributes use **last occurrence wins**, including ID shorthand versus assignment. Recommend a warning. Authored duplicate IDs are also preserved; never normalize or renumber them.

**Attachment:**

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 placement=center responsive}
[Release notes](release.md){class="release-link"}
```

A heading's final whitespace-separated list attaches to the heading. An immediately adjacent list attaches to a completed image/link. Attachments stay on the target's source line; code-span whitespace is not attachment syntax. Multiple lists resolve in source order; malformed lists stay literal. Escape `{` to prevent attachment. Code-fence attributes are described in the [language guide](/expressive-markdown/language#code-blocks-and-presentation-metadata); other block styling uses native HTML. `.class` shorthand is not defined.

| Recommended HTML mapping | Behavior |
| --- | --- |
| `id`, `class`, `style`, supported native attributes | Native equivalents; convert camelCase attribute keys back to dash-separated source names where applicable. HTML validity diagnostics do not change AST data. |
| Other string attributes | `data-*` using the dash-separated name; retain an existing `data-` prefix (AST `dataFoo` → HTML `data-foo`). |
| Custom true/false flags | Present empty `data-*` / omitted attribute. |
| Native boolean attributes | True or any assigned string means present; false means omitted. `"false"` therefore still enables it. |
| Conversion-owned `data-type` (AST `dataType`) | Identifies the construct. Preserve a colliding authored value in the AST and diagnose instead of replacing output identity. |

Unknown attributes remain data. An arbitrary flag does not acquire native HTML behavior.

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

The AST uses `lineBlock.children` with `break` nodes; consecutive/leading/trailing breaks preserve empty lines. A single plain line may use `value`; a single bare pipe uses `value: ""`.

**Recommended HTML:** `<p>` with `<br>` boundaries and preserved inline wrappers. Append one layout `<br>` for a terminal empty line, or for an entirely empty one-line block, so HTML does not absorb it. This extra layout break is not an AST break. Explicit empty lines add to normal paragraph spacing.

> [!note] Why a leading pipe?
> It is visible and marks the line it affects. CommonMark trailing spaces are invisible; its trailing backslash forces a break where languages such as Python use one to continue a line. Both CommonMark hard-break forms remain accepted as `break`; writers prefer line blocks.

## Tables

```md
| First | Second | Status |
| --- | --- | --- |
| > | Release checks | Ready |
| ^ | ^ | Verified |
```

Start with GFM tables: headers, inline cells and column alignment. Add marker-only cells for merging:

| Marker | Meaning |
| --- | --- |
| `>` | Merge into the next ordinary cell to the right. Consecutive markers join that cell. |
| `^` | Continue the cell above. Cover every column of a horizontal span. |
| Empty cell | Empty content, never a merge. |
| `\>` / `\^`, or inline code | Literal marker text. |

Markers match the entire unescaped cell after trimming spaces/tabs; tight `|>`/`|^` forms also work. They are recognized before inline parsing, only inside established tables. The example gives “Release checks” `colSpan: 2`, `rowSpan: 2`.

**Grid rules:**

- Resolve horizontal runs first, then vertical continuations on the original columns. A `>` run must end in an ordinary cell on that row, not `^`.
- Merges form non-overlapping rectangles, consume only markers and never cross the header/body boundary. Delimiter rows cannot merge. Repeated `^` rows extend the originating cell.
- With merge markers, every source row explicitly supplies equal column slots, including covered slots, before GFM padding/truncation. Without markers, ordinary GFM row-width behavior applies.
- Invalid merges preserve the **whole table** as block `literal` source and recommend a diagnostic.

The [table AST](/expressive-markdown/ast#content-node-reference) contains originating cells only, in column order. Place each at the first unoccupied column, skipping prior row spans. Spans are positive integers, default/omitted `1`; numeric structural fields do not change the string-only assigned-attribute rule. Alignment comes from the leftmost column unless a cell attribute overrides it.

Cells use exactly one of literal `value`, inline `children` or rich block `body`. Column alignment is `table.align` (`left`, `center`, `right` or null); cell `header` is boolean. Preserve widths/backgrounds/classes in attributes. Native HTML imports map supported `colspan`/`rowspan` to structural fields, without duplicate attributes; unrepresentable behavior stays HTML with a diagnostic.

Writers use pipe syntax where it preserves everything: `>` before the content slot and `^` in every covered lower slot, escaping literal markers. Otherwise use native HTML or report unsupported conversion. Preserve each cell's identity once, without placeholder IDs.

**Recommended HTML:** `<table>`, `<thead>`/`<tbody>`, `<tr>`, `<th>`/`<td>`, with spans, alignment and supported presentation attributes. Never silently flatten merged/rich cells or infer complex accessible header associations solely from visual position.

## Code presentation

Code attributes share the ordinary string/flag grammar and camelCase key mapping. `title` maps once to `code.title`; other attributes remain in `attributes`.

- `highlight` is a comma-separated string of positive line numbers or ascending inclusive `start-end` ranges. Repeated/overlapping selections form a union. Numbers refer to original `code.value` lines, starting at 1.
- `showLineNumbers` is a boolean setting; `true` shows numbering from 1 and `false` hides it. A string assignment stays a string, not a boolean.
- Invalid feature values or out-of-bounds ranges remain in the AST, recommend a diagnostic and use the baseline default: no line emphasis or numbering. They do not make the attribute list malformed.
- Unrecognized info tokens remain uninterpreted `meta`; optional provenance retains the full original info string. Canonical writers regenerate known metadata and append unknown tokens.
- Annotation comments are literal source. Profiles may explicitly map imported conventions, but the core does not interpret Docusaurus, VitePress or Shiki spellings automatically.

Recommended HTML escapes literal code. Per-line decoration must preserve the code's text and line divisions; copied code excludes generated line-number labels. A profile that cannot display a setting preserves it and reports the unsupported presentation.

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

The planned JavaScript tool also warns on unquoted `open=true`/`open=false`, suggesting `{open}`/`{!open}`. Quoting suppresses that advisory. Assigned values remain strings regardless; this adds no language-validity rule.

## Writing and preservation

Semantic round-tripping preserves meaning, ordered content, explicit line divisions, authored IDs, unknown types, supported metadata and presentation values. Byte-identical output is optional and requires lexical provenance: whitespace, quotes, overwritten attributes, references and delimiters.

| Writers use | Preserve |
| --- | --- |
| Lowercase directive names and dash-separated attribute names from camelCase AST keys; optional ` & ` separators | Values and metadata key casing. |
| `::: type [Title] {attributes}`; no wrapper padding; one blank line around body | Content, with nested fence lengths calculated from depth. Escape literal structural punctuation. |
| Double quotes when strings need quoting; `{name}` / `{!name}` flags | Explicit false versus omission/default. |
| Leading-pipe lines and bare empty pipes | Represented line divisions. |
| Regenerated table markers; escaped literal markers | Numeric spans and originating cell IDs. |
| YAML strings for title/ID; string lists for tags | Custom metadata, quoting strings YAML would otherwise type differently. |

Code fences follow CommonMark backtick/tilde rules and exceed conflicting delimiter runs in their literal content. Parsers should prefer compact `value` for wholly literal inline content, but supplied text-only `children` remain valid. Normalization must not lose child IDs, attributes or provenance.

Optional AST fields accept null as absence and serialize as omission; null metadata stays data. Required root `version` must be supported or conversion stops with a clear error. See the [AST contract](/expressive-markdown/ast).
