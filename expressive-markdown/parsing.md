---
title: Parser & Writer Rules
order: 2
blurb: boundaries · recovery · preservation
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Parser & Writer Rules

Use these rules to implement a parser or writer: recognize source boundaries,
build the [document AST](/expressive-markdown/parsing#shared-ast-contract), recover invalid input and
write equivalent Markdown. Each section defines one feature's exact behavior.
For author-facing examples, start with [Language & Semantics](/expressive-markdown/language).
HTML conversion recommendations are informative.

## Parsing order

1. Normalize CRLF/CR to LF; retained positions refer to original input.
2. Recognize optional opening frontmatter, then Markdown blocks by the [Markdown rules](#markdown-rules), [HTML elements](#html-elements), containers, leaf directives, footnote definitions, definition lists, tables and line blocks in their enclosing block context.
3. Parse inline content and titles after block boundaries, once every footnote label is known.

Code spans, fenced code and raw-text HTML retain their lexical boundaries;
their contents do not open directives or line blocks. GFM tables take precedence
over leading-pipe line blocks. Escaped structural punctuation stays literal.
Apply the [safe HTML policy](#safe-html) when importing HTML and before writing it.

## Markdown rules

Expressive Markdown reads CommonMark 0.31.2 and GFM's blocks and inline content
with these rules, so that each line reads as it looks. Where a rule differs from
CommonMark or GFM, a callout shows their reading of the same example and why
Expressive Markdown reads it this way.

### Indentation and code

Code is fenced, with ```` ``` ```` or `~~~`. Indentation never makes code: an
indented line reads as it would unindented, at the top level and in list
items, containers and HTML elements.

```md
    const x = 1;

    # Title
```

```html
<p>const x = 1;</p>
<h1>Title</h1>
```

> [!note] CommonMark
> **CommonMark:** four columns of indentation make indented code, so the
> example renders as `<pre><code>const x = 1;</code></pre>` followed by a
> second code block. Indentation then changes meaning by accident, inside
> lists, containers and HTML. Fenced code says explicitly that it is code, and
> it is what authors use today.

### Headings

A heading starts with one to six `#`. A `---` line under a paragraph is a
thematic break, and a `===` line is paragraph text:

```md
Title
---

Title
===
```

```html
<p>Title</p><hr>
<p>Title
===</p>
```

> [!note] CommonMark
> **CommonMark:** a `---` line under a paragraph makes it a level-2 heading,
> `<h2>Title</h2>`, and a `===` line a level-1 heading. A `---` meant as a
> divider then silently turns the paragraph above it into a heading. With `#`
> as the only way to write a heading, `---` is always a divider.

### Hard breaks

A trailing `\` or a `<br>` breaks a line. Trailing spaces are insignificant:

```md
one␠␠
two

one\
two
```

```html
<p>one
two</p>
<p>one<br>
two</p>
```

(`␠` marks a space.)

> [!note] CommonMark
> **CommonMark:** two or more trailing spaces also make a hard break, so the
> first example renders as `<p>one<br>two</p>`. Invisible whitespace then
> changes the output, and editors strip it. `\` and `<br>` are visible.

### Code spans in table cells

A code span inside a table cell is literal, its pipes included. Outside code,
`\|` writes a pipe:

```md
| Expression | Reads |
| --- | --- |
| `a || b` | or |
| x \| y | either |
```

```html
<table>
<tr><th>Expression</th><th>Reads</th></tr>
<tr><td><code>a || b</code></td><td>or</td></tr>
<tr><td>x | y</td><td>either</td></tr>
</table>
```

> [!note] GFM
> **GFM:** a `|` splits the cell inside a code span too, so `` `a || b` `` fills
> three cells unless each pipe is written `\|`. A code span is literal
> everywhere else, so a `|` inside one splitting the cell is inconsistent.

### Quotes and continuation lines

Every line of a block quote carries its own `>`, so a line without one ends the
quote. A list item's continuation lines are indented under it, so an unindented
line ends the list:

```md
> quoted
not quoted

- item
not item
```

```html
<blockquote><p>quoted</p></blockquote><p>not quoted</p>
<ul><li>item</li></ul><p>not item</p>
```

> [!note] CommonMark
> **CommonMark:** a paragraph continues lazily onto a line without the quote
> marker or the list indentation, so `not quoted` joins the quote's paragraph
> and `not item` the item's. The source then reads differently from how it
> renders. A line without `>` does not look quoted, so it is not quoted.

### Lists

**Markers.** A list continues when its bullet changes among `-`, `*` and `+`,
or its delimiter between `.` and `)`:

```md
- a
* b
+ c

1. one
2) two
```

```html
<ul><li>a</li><li>b</li><li>c</li></ul>
<ol><li>one</li><li>two</li></ol>
```

> [!note] CommonMark
> **CommonMark:** changing the bullet character or delimiter starts a new list,
> giving three lists and two. A different bullet looks like the same list to a
> reader, so it stays one list.

**Nesting** is relative. A line indented more than the list item above it
belongs to that item, by any amount: one space, two spaces or a tab. Equal
indentation makes a sibling, and less indentation closes items back to the
matching level:

```md
- a
 - b
- c
```

```html
<ul><li>a<ul><li>b</li></ul></li><li>c</li></ul>
```

A line is deeper when its leading whitespace starts with the item's and has
more after it. When neither starts with the other, as when tabs and spaces mix,
a tab advances to the next multiple of four columns; recommend a warning.

> [!note] CommonMark
> **CommonMark:** a line belongs to an item when it is indented to the item's
> content column, two columns for `- `, so ` - b` is a sibling item. The
> author's intent is "deeper than the item above", and aligning content to a
> column is invisible bookkeeping.

**Blank lines.** A blank line between two items at the same level ends the
list, and the next item starts a new one; an ordered list carries its
numbering into the new list's `start`. A blank line followed by indented
content continues the current item, and an item holding blank-line-separated
blocks gives them `<p>`, as an HTML element's blank lines do. Its siblings keep
theirs:

```md
- a
- b

- c

- a

  more
- b

1. one
2. two

3. three
```

```html
<ul><li>a</li><li>b</li></ul><ul><li>c</li></ul>
<ul><li><p>a</p><p>more</p></li><li>b</li></ul>
<ol><li>one</li><li>two</li></ol><ol start="3"><li>three</li></ol>
```

A list's `tight` is `true`; an item holding blank-line-separated blocks has
`tight: false`.

> [!note] CommonMark
> **CommonMark:** a blank line between items keeps one list and makes it
> loose, giving every item `<p>`: `<ul><li><p>a</p></li><li><p>b</p></li><li><p>c</p></li></ul>`.
> A single blank line then changes the spacing of every item in the list.
> Here, blank lines separate things, the same as inside HTML elements.

### Link targets

A link or image target may hold spaces. It runs to the `)` that balances the
opening `(` on the same line, and a final quoted title, after a space, is the
title. A target without spaces, or in `<…>`, reads as CommonMark reads it:

```md
[Notes](my notes.md)
[Draft](notes (draft).md "Draft") and [Next](next.md)
![Chart](my chart.png)
```

```html
<p><a href="my%20notes.md">Notes</a>
<a href="notes%20(draft).md" title="Draft">Draft</a> and <a href="next.md">Next</a>
<img src="my%20chart.png" alt="Chart"></p>
```

> [!note] CommonMark
> **CommonMark:** a destination with spaces needs `<…>`, so `[Notes](my notes.md)`
> stays text. File names contain spaces, and the target is unambiguous within
> the parentheses.

### Duplicate link definitions

When a link reference label is defined more than once, the last definition is
its target. Recommend a diagnostic:

```md
[x]

[x]: /one
[x]: /two
```

```html
<p><a href="/two">x</a></p>
```

> [!note] CommonMark
> **CommonMark:** the first definition wins, so the link goes to `/one`. Last
> wins matches how duplicate keys and attributes resolve everywhere else in
> Expressive Markdown.

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

Plain-text projection concatenates readable inline text, link labels, image and image-reference alternative text and code text; breaks become spaces and formatting delimiters disappear. Duplicate exact YAML keys are invalid YAML: diagnose and recover using the final value. Preserve other invalid/unsupported blocks as recoverable source; never guess or discard their values.

## Named constructs

```md
:::warning[Before deploying]{#check}
::: warning {#check} [Before deploying]
```

Both open the same container. The type comes first; optional title and attributes may follow in either order on **one source line**. Writers use `::: type [Title] {attributes}` unless the title was authored unbracketed.

**Unbracketed titles.** A container header also supports a title without brackets, as Docusaurus, VitePress and markdown-it-container write it: `::: warning Before you upgrade`. After the type and any attribute lists, text that starts with neither `[` nor `{` is the title: the rest of the line, up to trailing attribute lists, read as inline Markdown.

| Case | Rule |
| --- | --- |
| Trailing attributes | Whitespace-separated attribute lists that end the line attach to the container, as on a heading: `::: details Show the output {open}`. A final `{…}` that is not a valid attribute list is title text. |
| `[`, `]`, `{`, `}` in the text | Literal title text. A title that starts with `[` uses the bracket form, so `\[` or `\{` starts an unbracketed title with a literal bracket or brace. |
| Whitespace | Trimmed from both ends; inner spacing is kept. |
| With a bracket form | One title per header. `[Title]` followed by more words is an unreadable header; see below. |
| `::: tabs Install` | The group's title, by the same rule as every type. A group's shared selection name is `{group=name}`; converters that know a tool's own `tabs name` convention map it once. |

The AST records `titleSpelling: "unbracketed"`; absent or `"bracketed"` means the bracket form. Writers write the recorded spelling, and the bracket form for new titles. An unbracketed writer protects an opening bracket or brace, and a final list that would read as attributes. Leaf directives keep bracketed labels.

**Every colon fence opens a container.** A line of three or more colons, at
any block-relative indentation, opens a container whatever its header holds,
and it may interrupt a paragraph.

| Header | Container |
| --- | --- |
| `::: note [Title] {attributes}` | `subType: "note"`, with its title and attributes. |
| `::: {.render title="x"}`, `::: [Title]`, bare `:::` | A **generic container**: no `subType`, with any title and attributes. |
| An unreadable header, such as `::: note [unclosed` or `::: [Title] more` | A container with the type the header names, `note` here, or a generic container when it names none. `source.rest` keeps the remainder after the type, and writers write the type and that remainder back as authored. Recommend an `invalid-container-header` warning. |

A generic container groups blocks without a semantic type; its
[recommended HTML](/expressive-markdown/presentation#generic-containers-and-spans)
is a `<div>` carrying its attributes. Closing and nesting work as for every
container: the closing line holds only the opening's colon run, and a direct
child uses fewer colons than its parent. Inside a container, a bare colon line
of the parent's length closes it; a shorter one opens or closes a nested
container.

| Fence situation | Reading |
| --- | --- |
| Bare `:::` whose closing line follows before any other opening fence of its length or longer | A generic container. |
| Bare `:::` with no such closing line | A **stray fence**: a `strayFence` node whose `value` is the fence line's colon run. Its rendering is empty; it writes back as authored and recommends a `stray-fence` warning. The lines after it read as they would without it. |
| Typed, titled or attributed opener with no closing line | A container running to the end of its enclosing block, or to the line before a longer closing fence, which it leaves to its parent. Recommend an `unclosed-container` warning. Writers add the closing line. |

**Enclosing block.** A container ends with its enclosing block: in a list item
or quote, its last line comes before the first nonblank line indented less than
that block, and a typed opener without a closing line runs to that point.

| Rule | Accepted form |
| --- | --- |
| Identifier | ASCII letter, then ASCII letters, digits, `_` or `-`. Types become lowercase; attribute names use the mapping below. Text, values and IDs retain Unicode. |
| Container spacing | Any block-relative indentation; optional spaces/tabs after colons and between header parts. |
| Wrappers | No padding inside the outer `[…]` or `{…}`; internal word/attribute separation remains meaningful. |
| Label/title | Inline Markdown. Balanced brackets and matched code spans do not close the label early. Escape a literal bracket where it would close or unbalance the label. |
| Inline/leaf scope | `:type[label]{attributes}` / `::type[label]{attributes}`. Inline needs a label or attributes, so bare `:word` stays text. Leaf occupies its own line. |
| Repetition | Multiple attribute lists concatenate in source order. Repeated container title wrappers are malformed. |

An unmatched backtick run stays literal and does not hide the label's closing
bracket. Within a matched code span, backslashes are literal code characters;
they do not escape the closing code delimiter.

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

### Alerts

```md
> [!note] Optional title
> Body.
```

A block quote is an alert when its first line starts with `[!type]` followed
by a space, a tab or the line end. `type` is an identifier, matched
case-insensitively and stored lowercase as `subType`; writers keep its authored
case, so `> [!NOTE]` stays `> [!NOTE]`. The rest of that line,
trimmed, is the inline-Markdown title; when it is empty the alert has no title.
The quote's remaining content is the body, read as ordinary blocks. The result
is a `container` with `spelling: "alert"`.

- The marker is recognized only at the start of a quote's first line. There it
  takes precedence over a link reference definition with the same label, so
  `[!note]: url` defines a link and `[!note]` elsewhere keeps its ordinary
  meaning.
- `[!note]x` and `[!note]-` are not markers; the quote stays a `blockquote`.
- A marker naming `details`, `figure`, `layout`, `tabs`, `tab`, `toc` or
  `table` leaves an ordinary `blockquote`. Those types use the colon form.

**Writing.** Write a container with `spelling: "alert"` as an alert:
`> [!type]`, then ` Title` when present, then the body on following `> `
lines. Start the body after a `>` line when its first block is not a
paragraph. An alert has no attribute syntax:
write an alert with an ID, attributes or a structural type in the colon form
and recommend a diagnostic. Without a recorded spelling, write the colon form.
In an ordinary block quote, protect literal text that would open an alert.

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
| `.render` | Adds `render` to string `attributes.class`. |

- `#id` and `id=…` set the ID; `.name` adds a class. Class shorthands
  accumulate in source order, space-separated, so `{.render .wide}` gives
  `class: "render wide"`. An assigned `class=…` replaces the value gathered so
  far, by last occurrence wins, and later shorthands add to it. The longhand
  `{class="render wide" id="intro"}` works the same as `{.render .wide #intro}`. A class
  shorthand is an ASCII letter, `_` or `-`, then letters, digits, `_` or `-`.
  A class stays a class: `::: {.render}` is a generic container
  with `class: "render"`.
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
![Service diagram](services.svg){width=640 responsive}
[Release notes](release.md){.release-link}
```

A heading's final whitespace-separated list attaches to the heading. An immediately adjacent list attaches to a completed image/link, and to a bracket that forms no link as a [bracketed span](#bracketed-spans). Attachments stay on the target's source line; code-span whitespace is not attachment syntax. Multiple lists resolve in source order; malformed lists stay literal. Escape `{` to prevent attachment. Code-fence attributes are described in the [language guide](/expressive-markdown/language#code-blocks-and-presentation-metadata); other block styling uses supported safe HTML.

| Recommended HTML mapping | Behavior |
| --- | --- |
| `id`, `class`, `style`, supported native attributes | Supported safe native equivalents; convert camelCase keys back to dash-separated names where applicable. Filtering is reported. |
| Other string attributes | `data-*` using the dash-separated name; retain an existing `data-` prefix (AST `dataFoo` → HTML `data-foo`). |
| Custom true/false flags | Present empty `data-*` / omitted attribute. |
| Native boolean attributes | True or any assigned string means present; false means omitted. `"false"` therefore still enables it. |
| Conversion-owned `data-type` (AST `dataType`) | Identifies the construct. Preserve a colliding authored value in the AST and diagnose instead of replacing output identity. |

Unknown attributes remain data. An arbitrary flag does not acquire native HTML behavior.

## Bracketed spans

```md
[word]{.kw}
[word]{.kw #w key="v"}
```

A bracket followed immediately by one or more attribute lists is a bracketed
span: an `inline` node without a `subType`, holding the bracket's inline
Markdown and the lists' ID and attributes. An empty list `{}` also forms a span.

| Source | Reading |
| --- | --- |
| `[w](url){…}`, `[w][ref]{…}`, or `[w]{…}` when `w` resolves | The link or reference; the list attaches to it. |
| `[w]{…}` with no matching definition | A span. |
| `![a]{…}` | Image syntax: the image when it forms, otherwise text. |
| `@[a]{…}` | Mention syntax: the mention when it forms, otherwise text. |
| `:name[a]{…}` | Inline-type syntax: the typed inline when it forms, otherwise text. |
| `[^n]{…}` | Footnote syntax: the reference and literal `{…}` when `n` is defined, otherwise text. |
| `[w][]{…}`, `[w][label]{…}` | Reference syntax: the reference when it resolves, otherwise text. |
| `\![a]{…}`, `\@[a]{…}`, `\:name[a]{…}` | An escaped marker is text, and the bracket that follows is a span. |
| A span inside link text, `[a [b]{.x}](/u)` | The link, holding the span. |
| `` `[a]{…}` ``, `\[a]{…}` | Code and escaped text. |
| `[a] {…}` | Text: the list must follow the bracket immediately. |

Classes stay classes: `[w]{.kw}` is a span with the class `kw`. Writers write a typeless `inline` as
`[content]{attributes}`, writing `{}` when it has no attributes, and protect
literal text that would read as a span.

## Automatic tab grouping

After block parsing, normalize each document/container/quote/list-item/cell block array independently. Replace each maximal run of `container/tab` siblings with one `container/tabs` whose `body` contains the original tabs in order. Blank source lines produce no separating content node. A non-tab node ends the run; groups never cross a block-context boundary. A single tab is a one-item group.

When normalizing an explicit `tabs` body's direct children, retain its tab children directly rather than introducing another implicit group. Preserve nested groups inside each tab's body normally. Explicit neighbouring `tabs` groups remain separate. Derived groups have no authored ID, title or attributes. Source positions may cover the run; they do not create authored identity.

Canonical writers omit the group wrapper when no authored group settings, title or ID need representation and doing so preserves group boundaries. Keep an explicit wrapper where adjacent groups would otherwise merge. Otherwise write a normal `tabs` container with nested `tab` containers and matching fence lengths. A tab's title is inline Markdown and its selection value is string `attributes.value` or its title's plain text.

## Mentions

| Source | AST content |
| --- | --- |
| `@[Ada Lovelace]` | `inline`, `subType: "mention"`, `value: "Ada Lovelace"`. |
| `@ada-lovelace` | Same family/subtype, `value: "ada-lovelace"`. |
| `@[Ada Lovelace]#user-123` | Same label, plus node `ref: "user-123"`. |
| `@ada-lovelace#user-123` | Bare handle label plus the same node `ref`. |

The `@` marker is syntax, not part of the label value. A bracketed mention uses the ordinary inline label grammar and optional immediately adjacent attribute lists. A bare handle starts with a Unicode letter, number or `_`; it continues through Unicode letters, combining marks, numbers, `_` and `-`. Preserve label casing and Unicode exactly. Bare handles also accept immediately adjacent attribute lists.

Recognize a mention only when `@` starts the inline source being parsed or
immediately follows whitespace: a space, tab, line ending or Unicode whitespace.
This boundary applies to both bare handles and bracketed labels. A preceding
punctuation mark or formatting delimiter does not establish a boundary.
For example, `@ada`, `Thanks, @ada` and a line beginning with `@[Ada]` contain
mentions; `a@word`, `a@[Ada]`, `(@ada)` and `/@ada` are ordinary text and need
no escape. A boundary alone is insufficient: the following label or handle must
also be valid.

Escaped markers, code, raw HTML and link destinations retain their lexical
rules; existing CommonMark/GFM email/URL recognition takes precedence. Invalid
bracket/handle structure stays literal under local recovery.

Markdown mentions use the `@` syntax exclusively. The name `mention` is excluded from
generic colon-prefixed inline directives: `:mention[...]` and its attribute-only
form remain ordinary text, including case variants of the name.

An immediately adjacent `#reference` suffix belongs to the mention, before optional attribute lists. Its token uses the same characters as a bare handle; sentence punctuation such as the final `.` is excluded. A `#` without a valid reference token stays literal after the otherwise valid mention. The suffix maps to the optional string field `ref`, not `id` or `attributes.ref`. It is an opaque entity reference, not implicitly a URL fragment.

For references containing other characters, use `@[Ada Lovelace]{ref="org/user-123"}`. The recognized string `ref` attribute is promoted to the node field, not duplicated in `attributes`. A suffix followed by a `ref` assignment resolves in source order, last occurrence wins. Unsupported non-string `ref` values preserve recoverable source and recommend a diagnostic rather than inventing a target.

A missing target is valid. Host resolution does not implicitly populate `id` or `ref`. Generic `{#id}` still identifies this occurrence independently. Writers prefer `@[label]#reference{attributes}` when a reference fits the suffix grammar, the full-string attribute form otherwise, and omit absent parts. Optional provenance may retain bare spelling.

An AST may place a semantic mention next to non-whitespace text or inside
formatting where the Markdown spelling would have no valid boundary. Writers
preserve that occurrence with supported semantic HTML rather than adding spaces
or broadening mention recognition. For example,
`(<span data-type="mention">Ada</span>)` preserves a mention inside parentheses;
`(@Ada)` remains literal text.

## Leading-pipe line blocks

```md
| First line
| Second line
|
| Fourth line
```

Each `| ` or pipe-plus-tab starts a represented line; a bare `|` requests an empty line. `|Text` stays ordinary text. Allow any block-relative indentation; strip marker separation and additional leading whitespace. Indentation is not visual indentation.

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

Inline formatting may span represented lines; boundaries remain `break` nodes
within that formatting. Inline code spans fit within one represented line.
The line's initial pipe is structural; ordinary pipes within its payload are
literal and need no escape.

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

### Hard breaks in paragraphs

A trailing backslash is a `break` node within a paragraph, as the
[Markdown rules](#hard-breaks) state; its lexical boundaries follow
[CommonMark hard line breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks).
The [language examples](/expressive-markdown/language#hard-breaks-in-paragraphs)
show the source, HTML and AST. Leading pipes are the preferred authoring form
for line blocks; a hard break does not change a paragraph into a
`lineBlock`. Writers preserve that distinction under the [writer contract](#writing-and-preservation).

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

:::: {.render title="Resolved named columns" height="280"}
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Instructions</th>
      <th scope="col">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Install</td>
      <td><ol><li>Download the package.</li><li>Run the installer.</li></ol>
      </td>
      <td>
      </td>
    </tr>
    <tr>
      <td>Verify</td>
      <td>
      </td>
      <td>Check the version.</td>
    </tr>
  </tbody>
</table>
```

::: {.details summary="AST"}
```json
{
  "type": "table",
  "children": [
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "header": true,
          "value": "Task"
        },
        {
          "type": "tableCell",
          "header": true,
          "value": "Instructions"
        },
        {
          "type": "tableCell",
          "header": true,
          "value": "Notes"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Install"
        },
        {
          "type": "tableCell",
          "body": [
            {
              "type": "list",
              "ordered": true,
              "tight": true,
              "children": [
                {
                  "type": "listItem",
                  "body": [
                    {
                      "type": "paragraph",
                      "value": "Download the package."
                    }
                  ]
                },
                {
                  "type": "listItem",
                  "body": [
                    {
                      "type": "paragraph",
                      "value": "Run the installer."
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          "type": "tableCell",
          "value": ""
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Verify"
        },
        {
          "type": "tableCell",
          "value": ""
        },
        {
          "type": "tableCell",
          "value": "Check the version."
        }
      ]
    }
  ]
}
```

See the [feature definitions](/expressive-markdown/language) for node constraints.
:::
::::


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
| `align="start,end"` | Comma-separated displayed-column alignments, applied after transposition. | `table.align`, using null for `-`. |

An omitted or negated `transpose` means false. Positional `header` defaults to
false; named records supply their implicit header without that flag and cannot
negate it. Assigned strings are not boolean flags;
invalid `header`/`transpose` values are malformed table settings. Alignment
entries are `start`, `center`, `end` or `-`, with optional surrounding spaces.
One entry applies to all displayed columns; otherwise the count must match the
nonempty displayed width. Omitted alignment means the default. Invalid tokens
or counts are malformed, not silently truncated. Physical `left` and `right`
values are invalid. Render logical alignment using each cell’s text direction,
with the semantics of CSS `text-align: start`, `center` and `end`.

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

Normalize delimiter alignment markers `:---`, `:---:` and `---:` to
`start`, `center` and `end`, respectively; an unmarked delimiter yields null.
The normalized AST uses logical directions for every table source form.

```md
| Session | Activity |
| --- | --- |
| Morning | Breakfast |
| ^ | Workshop |
| Afternoon | Review |
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

## Footnotes

```md
Text with a note[^note].

[^note]: The note's first paragraph.

    A continuation paragraph.
```

A label uses the bare-handle token from [mentions](#mentions): a Unicode
letter, number or `_`, then Unicode letters, combining marks, numbers, `_` and
`-`. Labels match exactly, including case.

**Definitions.** A line starting `[^label]:`, after any block-relative
indentation, opens a `footnoteDefinition`. Its content starts
after the colon and optional spaces or tabs, and continues on lines indented
more than the marker, by any amount, as [list nesting](#lists) is relative.
Read that content as blocks, as a list item's content is read: a nonblank line
indented no more than the marker ends the definition. A definition may
interrupt a paragraph.

```md
[^a]: First.

  Second.
After.
```

The note holds two paragraphs, and `After.` follows it in the document. It is recognized in every
block context: the document, containers, quotes, list items, cell bodies and
other definitions. `[^text]:` whose text is not a label follows CommonMark,
which reads a valid line as a link reference definition.

**References.** `[^label]` is a `footnoteReference` when the document defines
that label anywhere, before or after the reference, including in titles.
Collect definition labels during the block pass, before inline content and
titles are parsed. Otherwise the characters remain text. A reference takes
precedence over link syntax opening at the same bracket. Code, HTML and link
destinations retain their lexical rules.

**Placement.** Each definition stays in its enclosing block array at its source
position. Parsers and writers do not move, merge or remove definitions,
including unused and duplicate ones. A tool that adds a footnote appends its
definition to the document body; editing a note changes only that node.

**Notes and numbering.** A label's note is its first definition in document
order. Number notes as follows:

1. Walk the document in [traversal order](#generic-traversal), skipping
   footnote definitions. Each label with a note receives the next number at its
   first reference.
2. Then walk each numbered note's body, in number order. A label first
   referenced there receives the next number and joins the walk.

| Input | Result |
| --- | --- |
| Reference without a definition | Text. Recommend an `undefined-footnote` warning. |
| Definition never referenced | Kept; renders nothing. Recommend an `unused-footnote` warning. |
| Later definition of a defined label | Kept; renders nothing. Recommend a `duplicate-footnote` warning. |

**Writing.** Write a reference as `[^label]` and a definition where it sits in
the tree: `[^label]:`, a space, then the first block. Indent every later
nonblank line four spaces; blank lines stay empty. An empty body writes
`[^label]:` alone. Protect literal `[^label]` text when the document defines
that label, and a literal `[^text]:` at the start of a line. A supplied
reference without a definition writes the reference form, reads back as text,
and recommends a diagnostic. Footnote nodes have no attribute attachment;
report an ID or attributes on one as unsupported conversion.

**Recommended HTML.** Each referenced note renders once, in a list at the end
of the document; definitions render nothing in place:

```html
<p>Text with a note<sup><a href="#fn:note" id="fnref:note" data-footnote-ref>1</a></sup>.</p>
<section data-footnotes aria-label="Footnotes"><ol>
  <li id="fn:note"><p>The note's first paragraph.</p><p>A continuation paragraph. <a href="#fnref:note" data-footnote-backref aria-label="Back to reference 1">↩</a></p></li>
</ol></section>
```

- A reference is `<sup><a>` holding its note's number. The first reference to
  a note has `id="fnref:label"`; the second `fnref:label:2`, and so on.
- The note is `<li id="fn:label">` in number order. Its back-links follow its
  last paragraph's content, each after a space: `↩` for the first reference,
  then `↩<sup>2</sup>` and onward, labelled `Back to reference N` and
  `Back to reference N-2`. A note whose last block is not a paragraph gets a
  new paragraph holding its back-links.
- The colon keeps these IDs apart from [generated anchors](#recommended-output-anchors),
  which contain letters, numbers, marks and hyphens.
- `aria-label="Footnotes"` names the notes region without imposing a heading rank.
- An unresolved supplied reference renders as its literal text.

## Definition lists

```md
Term
: First description,
  continued.
: Second description.

Next term
: Its description.
```

```html
<dl>
<dt>Term</dt>
<dd>First description, continued.</dd>
<dd>Second description.</dd>
<dt>Next term</dt>
<dd>Its description.</dd>
</dl>
```

> [!note] CommonMark
> **CommonMark:**
>
> ```html
> <p>Term
> : First description,
> continued.
> : Second description.</p>
> <p>Next term
> : Its description.</p>
> ```

**Terms.** A **marker line** is a line that starts, after any block-relative
indentation, with one `:` followed by a space, a tab or the line end. A
**term line** is the first line of a paragraph whose next line is a marker
line. A term line opens a `definitionList`; trimmed, it is a `definitionTerm`
holding inline Markdown. Definition lists are recognized in every block
context: the document, containers, quotes, list items, footnote definitions,
cell bodies and other descriptions.

**Descriptions.** A marker line opens a `definitionDescription`. Its content
starts after the colon and optional spaces or tabs, and continues on lines
indented more than the marker, by any amount, as [list nesting](#lists) is
relative. Read that content as blocks, as a list item's content is read: a
nonblank line indented no more than the marker ends the description. A
description holding blank-line-separated blocks has `tight: false`. A marker
followed only by whitespace, with no indented content, gives `body: []`.

**Continuing the list.** After a description, the list continues, after any
blank lines, with:

- a marker line, which adds a description to the same term;
- a term line, which starts the next term.

Any other nonblank line ends the list, and so does the end of its enclosing
block.

**Where a definition starts.** Only the term-line shape above starts a
definition list, so every other line keeps its reading:

| Source | Reading |
| --- | --- |
| `Term`<br>`: Description` | A definition list. |
| `Term`<br>`:Description` | One paragraph: the marker needs a space, a tab or the line end after it. |
| `Term`<br>`:kw[must] apply` | One paragraph holding an inline directive. |
| `Term`<br>`::page-break` / `:::` | The leaf directive or colon fence reads by its own rules. |
| `Term`<br>`\: Description` | One paragraph: the escaped colon is literal. |
| `Term`<br>`~ Description` | One paragraph. |
| `First line`<br>`Term`<br>`: Description` | One paragraph: its later lines continue it. |
| `Term`, a blank line, `: Description` | Two paragraphs. |
| `## Term`<br>`: Description` | A heading, then a paragraph. |
| `- Term`<br>`: Description` | A list, then a paragraph: the unindented line ends the item. |
| `- Term`, then `: Description` indented under it | A list item holding a definition list. |
| `> Term`<br>`> : Description` | A quote holding a definition list. |
| `> [!note] Term`<br>`> : Description` | A callout titled “Term”, whose body is a paragraph. |
| `::: note [Term]`<br>`: Description` | A container whose body starts with a paragraph. |
| `\| Term`<br>`: Description` | A line block, then a paragraph. |
| `Term`<br>`: Description`, then `: More` indented under it | A description whose content is itself a definition list, with the term `Description`. |
| `Term`<br>`: Description`<br>`continued` | A definition list, then the paragraph `continued`. |

Code spans, fenced code and raw-text HTML keep their lexical boundaries, and
block boundaries come first: a code span cannot join a term line to its marker
line. In a [named table record](#named-fields-and-column-identity), a line at
label indentation starts a field; a definition list sits inside a field body.

**Writing.** Write a definition list where it sits in the tree. Write each
term on its own line, then each of its descriptions: `:`, a space, then the
first block, with every later nonblank line indented two spaces; blank lines
stay empty. Separate a `tight: false` description's blocks with a blank line.
An empty description writes `:` alone. Put one blank line before each term
after the first, and no blank line between a term and its descriptions.

- In a paragraph, protect a `:` that would start a marker line directly after
  the paragraph's first line: write `\:`.
- Protect a term whose text would start another block, as for
  [literal block markers](#literal-block-markers).
- Definition list nodes have no attribute attachment; report an ID or
  attributes on one as unsupported conversion.
- Report unsupported conversion for a term holding a `break` or `softBreak`,
  and for two adjacent `definitionList` siblings, which read back as one list.

**Recommended HTML.** A `definitionList` renders as `<dl>`, each term as
`<dt>` and each description as `<dd>`, in source order. A description renders
its blocks as a list item does: with `tight: false`, each paragraph is a `<p>`;
otherwise paragraph content sits directly in the `<dd>`. An empty description
renders as `<dd></dd>`.

**Diagnostics.**

| Input | Result |
| --- | --- |
| A paragraph whose later line starts with `:` or `~` followed by a space, a tab or the line end | Paragraph text. Recommend an `unattached-definition-marker` warning. |
| A paragraph starting with such a `:` or `~`, after a one-line paragraph and a blank line | Paragraph text. Recommend an `unattached-definition-marker` warning. |
| Mixed tabs and spaces in description indentation | Read as for [list nesting](#lists); recommend a warning. |
| A supplied list that starts with a description, ends with a term or is empty | Invalid structure; report it. |

## Link references

```md
[Setup guide][guide], the [FAQ][] and the [changelog].

[guide]: /docs/setup "Setup guide"
```

CommonMark decides what is a link reference definition and what is a
reference link: its [link reference definitions](https://spec.commonmark.org/0.31.2/#link-reference-definitions)
and its full, collapsed and shortcut [reference links](https://spec.commonmark.org/0.31.2/#reference-link),
for links and images. Expressive Markdown keeps both in their authored form.

| Source | AST |
| --- | --- |
| `[label]: url "title"` | `definition` with the authored `label`, `url` and optional `title`, at its source position. |
| `[text][label]` | `linkReference`, `referenceType: "full"`, `label` from the second brackets, inline content from the first. |
| `[text][]` / `[text]` | `linkReference`, `referenceType: "collapsed"` / `"shortcut"`, `label` holding the bracketed source text. |
| `![alt][label]`, `![alt][]`, `![alt]` | `imageReference` with the same `label` and `referenceType`, and string `alt`. |

- Labels match as CommonMark matches them: after trimming, collapsing
  whitespace and Unicode case folding. `label` keeps the authored spelling.
- A label's target is its last definition in document order, as the
  [Markdown rules](#duplicate-link-definitions) state. Every definition stays in
  place.
- A reference whose label has no definition remains text, using CommonMark's
  literal fallback.
- Definitions are recognized in every block context and stay in their
  enclosing block array. Parsers and writers do not move, merge or remove them.

**Rendering.** Resolve each reference to its label's definition when rendering:
a `linkReference` renders as a link and an `imageReference` as an image, with
the definition's `url` and `title`. A definition renders nothing in place. A
supplied reference with no definition renders as its literal source text.

**Writing.** Write each definition where it sits in the tree, as
`[label]: destination` and an optional quoted title, using the inline-link
destination rules. Write a reference in its `referenceType` form:

- `collapsed` and `shortcut` name their label with their text. When the
  written text no longer matches the label, write the `full` form.
- When the characters after a `shortcut` would extend it, such as `(`, `[` or
  `:`, write the `collapsed` form.
- Protect literal bracketed text that names a defined label, so it stays text.
- A supplied reference with no definition writes its form, reads back as text,
  and recommends a diagnostic.

A tool that changes a link's target or title updates its definition in place.
Definitions have no attribute attachment; report an ID or attributes on one as
unsupported conversion.

## Code presentation

Code attributes share the ordinary string/flag grammar and camelCase key mapping. `title` maps once to `code.title`; other attributes remain in `attributes`.

- `highlight` is a comma-separated string of positive line numbers or ascending inclusive `start-end` ranges. Repeated/overlapping selections form a union. Numbers refer to original `code.value` lines, starting at 1.
- `showLineNumbers` is a boolean setting; `true` shows numbering from 1 and `false` hides it. A string assignment stays a string, not a boolean.
- Invalid feature values or out-of-bounds ranges remain in the AST, recommend a diagnostic and use the baseline default: no line emphasis or numbering. They do not make the attribute list malformed.
- Unrecognized info tokens remain uninterpreted `meta`; optional provenance retains the full original info string. Canonical writers regenerate known metadata and append unknown tokens.
- Annotation comments are literal source. Profiles may explicitly map imported conventions, but the core does not interpret Docusaurus, VitePress or Shiki spellings automatically.

Recommended HTML escapes literal code. Per-line decoration must preserve the code's text and line divisions; copied code excludes generated line-number labels. A profile that cannot display a setting preserves it and reports the unsupported presentation.

## HTML elements

Expressive Markdown reads HTML elements as HTML matches tags, and reads
Markdown inside them:

```md
<div class="entry">
Some **bold** text.
</div>
```

```html
<div class="entry">Some <strong>bold</strong> text.</div>
```

> [!note] CommonMark
> **CommonMark:** an HTML block starts at a line that meets one of seven
> conditions: `<script`, `<pre`, `<style` or `<textarea`; a comment; a
> processing instruction; a declaration; CDATA; one of a list of block-level tag
> names; or any complete tag alone on its line. The first five run to their end
> marker and the last two to a blank line, and the HTML inside stays raw text,
> so the example above renders as written, with `**bold**` unread. CommonMark
> decides from a block's first line without matching closing tags, so a
> tag-name list and blank lines stand in for real element boundaries. Matching
> tags as HTML does gives every element the same behavior, and Markdown works
> inside elements. Line breaks inside an element carry no meaning, as in HTML.

### Content

A start tag at the start of a line opens a block element. It runs to its
matching end tag, counting nested elements of the same name, or to where HTML
closes it otherwise. Its content is Markdown, read as a block context of its
own. Code is opaque: a tag inside a code span or a fenced code block never
counts when finding where an element ends.

```md
<details>
Use `</details>` to close it.
</details>
```

```html
<details>Use <code>&lt;/details&gt;</code> to close it.</details>
```

Line breaks and indentation inside an element carry no meaning: the element's
common indentation is removed, and indentation never makes code. These three
read alike:

```md
<div>Some **bold**</div>

<div>
Some **bold**
</div>

<div>
  Some **bold**
</div>
```

```html
<div>Some <strong>bold</strong></div>
```

Blank lines between an element's blocks give its paragraphs `<p>`, as in a
list item. Without them, its paragraphs take none:

```md
<div>

A

B

</div>
```

```html
<div><p>A</p><p>B</p></div>
```

Every element's content is read the same way, whatever the element:

```md
<span># tag</span>
```

```html
<span><h1>tag</h1></span>
```

### Elements and lines

An element followed by text on its line is inline content of a paragraph,
matched by the same tag rules within the paragraph:

```md
<kbd>Ctrl</kbd>+<kbd>C</kbd> copies **x**
```

```html
<p><kbd>Ctrl</kbd>+<kbd>C</kbd> copies <strong>x</strong></p>
```

Elements separated only by whitespace on a line are each a block:

```md
<details><summary>Notes</summary><div>

Body

</div></details>
```

```html
<details><summary>Notes</summary><div><p>Body</p></div></details>
```

An element interrupts a paragraph when it runs past its first line or its
start tag ends the line. A one-line element and a void element continue the
paragraph's text:

```md
Text
<a href="/x">link</a>

Text
<div>
Block
</div>
```

```html
<p>Text
<a href="/x">link</a></p>
<p>Text</p><div>Block</div>
```

An element without its end tag ends at its first blank line outside code, or
with its enclosing block, such as a list item, if that ends first; inline, it
ends with its paragraph. Recommend a diagnostic.

```md
<div>
open

After
```

```html
<div>open</div><p>After</p>
```

### Raw text

`script`, `style`, `textarea`, `title` and `pre` hold their content as written
through their end tag, at block level and inside a paragraph alike. A comment (`<!-- … -->`), processing instruction,
declaration or CDATA section runs to its terminator and takes the rest of that
line:

```md
<pre>
**raw**

text
</pre>
```

```html
<pre>
**raw**

text
</pre>
```

```md
Run <script>if (a **b** c) `x`</script> now.
```

```html
<p>Run <script>if (a **b** c) `x`</script> now.</p>
```

### Tags

**Void elements** are HTML's: `area`, `base`, `br`, `col`, `embed`, `hr`, `img`,
`input`, `link`, `meta`, `source`, `track` and `wbr`. They take no end tag, and
`<img src="a.png">` and `<img src="a.png" />` are the same element.

**`/>` closes every element.** `<x-embed video="1" />` is a complete, empty
element, at block level and inline, and HTML output writes it as
`<x-embed video="1"></x-embed>`. Writers keep the authored `/>`.

```md
<div><x-a /><p>b</p></div>
```

```html
<div><x-a></x-a><p>b</p></div>
```

> [!note] HTML
> **HTML:** `/>` on a non-void element is ignored, so `<x-embed />` stays open
> until `</x-embed>` or its parent closes it. Markdown favors convenient
> authoring, and Expressive Markdown produces HTML, so it writes the complete
> element. The [Self-Closing HTML proposal](https://nextwebwg.org/self-closing-html/)
> is related work.

A tag is self-closing only as HTML's tokenizer reads it: `/` right before `>`,
outside an attribute value. `<a href=/docs/>Docs</a>` is an ordinary start tag
whose `href` is `/docs/`.

**Optional end tags** close as HTML defines them: `li`, `dt`, `dd`, `p`, `rt`,
`rp`, `optgroup`, `option`, `thead`, `tbody`, `tfoot`, `tr`, `td` and `th` close
before the start tags HTML's
[optional tags](https://html.spec.whatwg.org/multipage/syntax.html#optional-tags)
rules list for them, or at the end of their parent's content, and a heading's
start tag closes an open heading.

```md
<ul><li>a<li>b</ul>

<table>
<tr><td>a<td>b
<tr><td>c
</table>
```

```html
<ul><li>a</li><li>b</li></ul>
<table><tr><td>a</td><td>b</td></tr><tr><td>c</td></tr></table>
```

**A stray end tag**, one that closes no open element, is ignored. Recommend a
diagnostic. `</br>` is a `<br>`; recommend a warning that suggests `<br>`.

```md
a </span> b

line one</br>
line two
```

```html
<p>a  b</p>
<p>line one<br>
line two</p>
```

> [!note] HTML
> **HTML:** `</p>` with no open `p` creates an empty `p` element. A closing tag
> never creates an element. `</br>` keeps HTML's reading because authors write
> `</br>` to mean a line break.

### AST

An element is an `htmlElement` node with `display`, its `tag` name, `open`,
its start tag as written, and `close`, its end tag as written, absent when the
element closes otherwise. A block element holds `body` blocks, with
`tight: false` when blank lines separate them; an inline element holds inline
content; a raw-text element holds its content as `value`; a void or
self-closing element holds none. Comments and declarations are `html` nodes, as
is a stray end tag, kept for writing and rendering nothing.

## Safe HTML

HTML import and output use a maintained sanitizer allowlist for elements,
attributes and URLs, rather than a hand-written blacklist. The exact preset
remains to be selected.

- Show an authored element the policy disallows as text, its raw-text content
  included, as GitHub's tag filter shows it, and report it:
  `<input type="checkbox">` renders as `&lt;input type="checkbox"&gt;`.
- Filter the attributes and URLs of each element the policy allows.
- Apply the policy to supplied AST HTML and presentation attributes when writing;
  do not trust them merely because they arrived as document data.
- Report filtering and unsupported conversion. Never replay discarded unsafe
  content from provenance, recovery or source-preservation records.

The policy does not alter literal code examples: HTML written inside a code
span or code block remains inert code text. A preserved `literal` recovery node
is escaped text, not executable HTML.

### Trusted host profile

The safe profile is the default. A host whose content only its own authors
write, such as a documentation site's pages, may choose a trusted host profile
explicitly, so components and page styles written in Markdown reach its output.

- Parsing keeps each element's tags as written, unfiltered, in its
  `htmlElement` node, and comments and declarations in `html` nodes.
- Writers write those nodes back verbatim.
- Rendering still applies the safe profile, extended by the host's allowlist of
  elements, attributes, style properties and URL schemes, to all output: raw
  HTML, built-in mappings and extension output alike.
- Event-handler attributes and script URLs stay blocked unless the host names
  them individually; both grant the content script access.

**Trust boundary:** the trusted profile is for content the host's own authors
write. User-submitted, imported and third-party content uses the safe profile.

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
| Invalid inline or leaf directive opener, or attachment | Local literal text; do not consume unrelated following content. |
| Unreadable container header | Container with the type it names, keeping the remainder in `source.rest`. Recommend a warning. |
| Unclosed container | Container running to the end of its enclosing block, or to a longer closing fence; code retains lexical precedence when locating boundaries. Recommend a warning. |
| Bare fence without a closing line | `strayFence` node. Recommend a warning. |
| Opening `---` without a close | Ordinary Markdown. |
| Delimited but invalid/unsupported frontmatter | Entire block as `literal`; no guessed metadata. |
| Invalid merged table | Whole table as block `literal`. |
| Footnote reference without a definition | Text. Recommend a warning. |
| Unused or repeated footnote definition | Kept in place; renders nothing. Recommend a warning. |
| Link reference without a definition | Text, using CommonMark's literal fallback. |
| Definition marker without a term line | Paragraph text. Recommend a warning. |

Recovery nodes keep original source in `value` and a `display` context. Recommend escaped inline text or block text with visible source-line breaks. Recovery is not an executable-content mechanism.

Diagnostics remain separate from document content. Suggested records contain code, severity, message, optional position and node ID; this is tooling guidance, not a mandatory API. Recommend warnings for duplicate attributes/IDs and invalid feature values.

Tools may warn on unquoted `open=true`/`open=false` and suggest `{open}`/`{!open}`.
Quoting suppresses this advisory. Assigned values remain strings either way.

## Writing and preservation

Round-tripping preserves meaning, order, explicit lines, authored IDs, unknown
types, supported metadata and presentation. Discarded unsafe HTML is excluded
and must never be restored from source records. Content stays where it was
written: writers keep each block, including footnote and link reference
definitions, at its place in the tree, and write each construct in its
[authored form](#authored-forms).

**Exact writing.** An unedited document is written back byte for byte, spacing
between blocks and line endings included. A parser records the source text and
each top-level block's range in the document's `source`, with a way to
recognize the block unedited, such as a hash of its data. A writer writes each
unedited block from its range, and the source's spacing between two unedited
neighbours. An edited or new block is written canonically: whitespace inside
constructs, character escapes and overwritten duplicate attributes are
normalized. Source the safe profile filters is never written from the record.

The table lists the preferred forms, which writers use for content without a
recorded authored form, such as content a tool inserts.

| Writers use | Preserve |
| --- | --- |
| Lowercase directive names and dash-separated attribute names from camelCase AST keys; optional ` & ` separators | Values and metadata key casing. |
| `::: type [Title] {attributes}`; no wrapper padding; one blank line around body | Content, with nested fence lengths calculated from depth. Escape punctuation where it would acquire structural meaning. |
| `> [!type] Title` for a callout with `spelling: "alert"` | The authored spelling of each callout. |
| Double quotes when strings need quoting; `{name}` / `{!name}` flags | Explicit false versus omission/default. |
| Leading-pipe lines and bare empty pipes | Represented line divisions. |
| Regenerated table markers; escaped literal markers | Numeric spans and originating cell IDs. |
| YAML strings for title/ID; string lists for tags | Custom metadata, quoting strings YAML would otherwise type differently. |
| `[^label]` and `[^label]:` with four-space continuation | Each footnote definition at its place in the tree. |
| Reference links in their authored form; `[label]: destination "title"` | Each definition at its place in the tree. |
| A term line, then `: ` descriptions with two-space continuation; one blank line before each later term | Each term's descriptions and each description's `tight`. |

### Authored forms

Where the language accepts more than one spelling for the same thing, the AST
records which one the author used and writers write it back. The record lives
in the node's `source` provenance: it never changes the node's meaning, and
generic traversal ignores it. Parsers record only spellings that differ from
the preferred form, so a document written in preferred forms carries none.

```md
* Use _care_.
```

```json
{
  "type": "list", "ordered": false, "tight": true,
  "source": { "marker": "*" },
  "children": [{ "type": "listItem", "body": [{ "type": "paragraph", "children": [
    { "type": "text", "value": "Use " },
    { "type": "emphasis", "source": { "marker": "_" }, "value": "care" },
    { "type": "text", "value": "." }
  ] }] }]
}
```

| Construct | Spellings | Preferred | Recorded |
| --- | --- | --- | --- |
| Emphasis, strong | `*a*` / `_a_`, `**a**` / `__a__` | `*`, `**` | `marker: "_"` |
| Bullet list | `-`, `*`, `+`, each item its own | `-` | `marker`; `bullet` on an item whose bullet differs from its list's |
| Ordered list | `1.` / `1)`, each item its own; incrementing or repeated numbers | `.`, incrementing | `marker: ")"`, `numbering: "same"`; `bullet` on an item whose delimiter differs |
| Task marker | `[x]` / `[X]` | `[x]` | `marker: "X"` |
| Heading | ATX, ATX with closing hashes | ATX | `closing` |
| Code block | Backtick or tilde fence of any length | Shortest backtick fence | `fence` |
| Code span | Backtick runs of any length | Shortest run | `fence` |
| Thematic break | `---`, `***`, `___`, spaced or longer | `---` | `marker` |
| Autolink | `<url>`, bare URL, `[url](url)` | `[text](url)` | `form: "angle"` or `"bare"` |
| Link target | Destination with or without `<…>`, or holding spaces; `"`, `'` or `(…)` title | Canonical destination, `"` title | `target` |
| Link reference definition | As authored | `[label]: destination "title"` | `markdown` |
| Link reference | Full, collapsed, shortcut | As authored | `referenceType` |
| Callout | Colon container; alert, with the type in any case | Colon container, lowercase type | `spelling: "alert"`; `type` for an alert type not written in lowercase |
| Container title | `[Title]`; unbracketed | `[Title]` | `titleSpelling: "unbracketed"` |
| Container header | Type case, spacing, part order, attribute spelling | `type [Title] {attributes}` | `header` |
| Container fence | Any length longer than its contents' | 3 plus nesting depth | `fence` |
| Tab group | Adjacent tabs; explicit `tabs` container | Adjacent tabs | `form: "explicit"` |
| Table | Named list fields; positional list rows; GFM pipes | Named fields | `form: "positional"`; `form: "pipe"` with `markdown` |
| Mention | `@[label]`; bare `@handle` | `@[label]` | `form: "bare"` |
| Attribute list | `#id` / `id=…`, `.class` / `class=…`, quoting, `&` separators, order | `.class`, `#id`, double quotes, spaces | `attributes` |
| Fence info | Setting order, separators, quoting | Language, attributes, meta | `info` |
| Line block | Marker spacing, indentation, continuation lines | `\| ` lines | `markdown` |
| Definition list | Marker spacing and indentation, continuation indentation, blank lines between terms | `: `, two-space continuation, one blank line before each later term | `markdown` |
| Frontmatter | YAML as authored | Generated YAML | `frontmatter` on the document |

`referenceType`, `spelling` and `titleSpelling` are node fields because the
choice also shapes how the node is read: a reference names its label through
its form. All other spellings use `source`.

**Writing.** Write each recorded spelling while it still applies to the node,
and the preferred form otherwise:

- An enum spelling applies while the construct can carry it: `_` emphasis at
  word boundaries, a bare URL or mention the reader links again.
- A raw spelling (`header`, `attributes`, `info`, `target`, `markdown`,
  `frontmatter`) applies while reading it gives the node's current data.
  Editing the data writes the preferred form.
- A fence keeps its recorded length while it exceeds its contents' fences, and
  lengthens otherwise.

**Exceptions.** Conflict and safety rules are not spellings and stay as
defined: duplicate attributes and YAML keys resolve by last occurrence and are
written resolved, and unsafe URLs and `script` elements are removed.

### Text and formatting boundaries

Literal AST text must stay literal after reparsing. For example, write an AST
value containing the six characters `&copy;` as `&amp;copy;`, so it does not
become ©. This does not change CommonMark entity interpretation in authored source.

Canonical writers preserve readable literal punctuation. Escape or encode text
when its actual source context would interpret it as syntax or change its
value; do not escape a character solely because it can introduce syntax
elsewhere. Account for the enclosing block, inline delimiters, attachments and
adjacent nodes. Text-node boundaries do not separate source characters.

| Literal content and context | Writing behavior |
| --- | --- |
| Paragraph prose `[-1, 1]`, `{name}`, `x < 5`, `x > 2`, `a * b`, `~5` or `left \| right` | Keep the punctuation. None of these examples forms syntax. |
| `a@word`, `a@[Ada]`, `(@ada)` or a standalone `@` | Keep `@`; no valid mention begins there. |
| Unmatched backtick or emphasis delimiter | Keep it unless neighbouring source would complete a delimiter or change a surrounding construct. |
| Paragraph starting `#hashtag`, `+5`, `-5` or `=value` | Keep the prefix; these are not heading/list/underline markers. |
| Literal `*text*`, `[label](target)`, `:chip[Ready]` or a valid `@ada` in a paragraph | Protect the syntax opener or delimiters so the content remains text. |
| Heading ending with literal `{name}` or ` #` | Protect the attachment opener or closing heading marker. |
| Literal `[x] task` at the beginning of a list item | Protect the task marker; the same text outside a list needs no such escape. |
| Literal pipe in a list-form table cell | Keep it unless the cell content itself forms another Markdown construct. Pipe-table delimiters have their own rules. |

For example, a literal colon followed by a link node must not combine into an
inline directive, and an unmatched bracket must not consume a surrounding
label's delimiter. Apply these checks to the resulting source, including
characters contributed by other nodes. Protect literal URLs/emails that would
become autolinks while leaving actual link nodes as links.

Writer verification must check readable source output as well as semantic
round trips. A round-trip assertion alone cannot detect unnecessary escaping.

Preserve whitespace inside formatting, adjacent/nested formatting boundaries,
and empty or whitespace-only paragraphs. Use supported safe HTML when Markdown
delimiters or blank source lines would change that content:

```md
<strong>Hello </strong><span data-type="mention" data-ref="user-123">Ada</span>

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

Optional AST fields accept null as absence and serialize as omission; null metadata stays data. Required root `version` must be supported or conversion stops with a clear error. See the [AST contract](/expressive-markdown/parsing#shared-ast-contract).


## Shared AST contract

The abstract syntax tree (AST) is the JSON document format. Feature-specific
node shapes are disclosed beside their [Markdown examples](/expressive-markdown/language).
These shared rules apply to every node.

| Field | Type | Contract |
| --- | --- | --- |
| `type` | Nonempty string | Required structural node type; canonical built-in names are defined beside their feature examples. |
| `subType` | String | Semantic type on `container`, `inline` and `leaf`; canonical lowercase. Its vocabulary is open. |
| `id` | String | Optional on every node; preserve exactly. Never generate or normalize it implicitly. |
| `title` | `TitleNode` or string, according to the node type | Optional. Document/container/table captions use a title node; code captions and link/image resource tooltips use strings. Each node type fixes its representation. |
| `body` | `Node[]` | Main block content. A title is optional, not the criterion for choosing this field. |
| `children` | `Node[]` | Inline content or structural grouping. |
| `value` | String | Literal content. Never reparse it as Markdown. |
| `attributes` | Object of string or boolean values | Authored properties/presentation. Keys use camelCase mapped from case-insensitive, dash-separated source names; `show-line-numbers` becomes `showLineNumbers`. Assigned values are strings; flags are booleans. Generic ID lives in `id`, not here. |
| `position` | `Position` | Optional original-source range, defined below. |
| `source` | JSON object | Optional lexical provenance for source preservation, including each [authored form](#authored-forms). It is not another semantic value or a traversable subtree. |
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

### Content shapes

**Inline content** means exactly one of string `value` or ordered inline
`children`. **Blocks** means an ordered `body` array. All nodes also allow the
shared fields above. Each feature disclosure defines its required content and additional fields.

Block content admits paragraph, heading, quote, list, code, line block, table,
container, leaf, horizontal rule, footnote definition, definition list, link
reference definition, stray fence and block-display group/HTML element/HTML/literal. Inline content admits text,
inline formatting, inline code, link, image, link and image reference, footnote
reference, break/soft break, inline directive and
inline-display group/HTML element/HTML/literal.
`title` is a designated title-field node, not an ordinary paragraph body child.
Lists contain list items; definition lists contain terms and descriptions; tables contain rows; rows contain cells. Tabs and their content share the container family. Consecutive `tab` siblings normalize into a `tabs` container, as described in the language draft. These constraints supplement the generic field exclusion.


### Serialization, extensions and diagnostics

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

Round-tripping preserves supported semantic data, and an unedited document's
Markdown byte for byte. Application-only IDs without a source attachment cannot always be
written; report that limitation. Discarded unsafe HTML is never restored.
See [writer rules](/expressive-markdown/parsing#writing-and-preservation) for
canonical output and preservation boundaries.
