---
title: Language & Semantics
order: 1
sectionNav: true
blurb: syntax · meaning · HTML guidance
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Language & Semantics

Start a heading with `#`, make text bold with `**text**`, create a link with
`[label](url)`, or start a list item with `-`. Use callouts for important notes,
tabs for alternative instructions, and tables to compare information.

```md
# Installation

Install the package, then **check the version**.

- Download the package.
- Run the installer.
```

The examples keep their use case, Markdown, HTML representation and AST data
together. Open an **AST** disclosure when you need the JSON shape and node
constraints. Rendering examples show common possibilities where appearance
helps; metadata and straightforward variations can explain their result.

For implementation details, see the [parser and writer rules](/expressive-markdown/parsing)
and the [shared AST contract](/expressive-markdown/parsing#shared-ast-contract).

## Text, headings and lists

These forms follow CommonMark and GFM. Each is explained below, including its
source syntax, HTML, AST and rendering.

### Paragraphs and headings

Separate paragraphs with a blank line. Start a heading with one to six `#`
characters followed by a space: `#` is level one, `##` is level two, and so on.
Use headings to organize the document:

```md
A paragraph about installation.

## Installation
```

:::: {.render title="Paragraph and heading" height="160"}
```html
<p>A paragraph about installation.</p>
<h2>Installation</h2>
```

::: {.details #inline-content-ast summary="AST"}
```json
[
  {
    "type": "paragraph",
    "value": "A paragraph about installation."
  },
  {
    "type": "heading",
    "level": 2,
    "value": "Installation"
  }
]
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `text` | String `value`. | Literal text leaf. |
| `paragraph` | Inline content. | Empty and whitespace-only content is valid AST data and must survive writing; use safe HTML when ordinary spacing would erase it. |
| `heading` | Integer `level` 1–6; inline content. | No implicit ID; authored `id` remains generic. |

Parsed text values are literal content, not Markdown to parse again.
:::
::::

### Inline formatting and code

Wrap text in `*` for emphasis, `**` for strong emphasis (usually bold), or `~~`
for strikethrough. Wrap literal code in backticks:

```md
Use *care*, **check twice**, and replace ~~old~~ with `new`.
```

:::: {.render title="Inline formatting and code" height="105"}
```html
<p>Use <em>care</em>, <strong>check twice</strong>, and replace <del>old</del> with <code>new</code>.</p>
```

::: {.details summary="AST"}
```json
{
  "type": "paragraph",
  "children": [
    {
      "type": "text",
      "value": "Use "
    },
    {
      "type": "emphasis",
      "value": "care"
    },
    {
      "type": "text",
      "value": ", "
    },
    {
      "type": "strong",
      "value": "check twice"
    },
    {
      "type": "text",
      "value": ", and replace "
    },
    {
      "type": "delete",
      "value": "old"
    },
    {
      "type": "text",
      "value": " with "
    },
    {
      "type": "inlineCode",
      "value": "new"
    },
    {
      "type": "text",
      "value": "."
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `emphasis`, `strong`, `delete`, `underline`, `highlight` | Inline content. | Semantic/stylistic inline wrappers; preserve attributes. |
| `inlineCode` | String `value`. | Literal code leaf; Markdown delimiters are not part of value. |
:::
::::

### Wrapping, breaks and separators

Ordinary source wrapping joins prose within the same paragraph:

```md
An ordinary source wrap
continues the same paragraph.
```

:::: {.render title="Ordinary source wrapping" height="105"}
```html
<p>An ordinary source wrap continues the same paragraph.</p>
```

::: {.details summary="AST"}
```json
{
  "type": "paragraph",
  "children": [
    { "type": "text", "value": "An ordinary source wrap" },
    { "type": "softBreak" },
    { "type": "text", "value": "continues the same paragraph." }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `softBreak` | No content field. | Ordinary source wrapping within inline content. |
:::
::::

Use [leading-pipe line blocks](#leading-pipe-line-blocks) when line divisions
are part of the content.

Use `---` on its own, separated from surrounding paragraphs by blank lines,
for a thematic break. Its **HTML representation** is `<hr>` and its **AST** is
[`horizontalRule`](/expressive-markdown/language#container-ast); it normally renders as a
horizontal separator. It is distinct from opening YAML frontmatter or a
Setext heading underline in the CommonMark contexts that recognize those forms.

### Quotations

Start quoted lines with `> ` to distinguish them from surrounding prose:

```md
> Keep a backup before continuing.
```

:::: {.render title="Block quotation" height="105"}
```html
<blockquote><p>Keep a backup before continuing.</p></blockquote>
```

::: {.details summary="AST"}
```json
{
  "type": "blockquote",
  "body": [
    {
      "type": "paragraph",
      "value": "Keep a backup before continuing."
    }
  ]
}
```
:::
::::

### Links and images

Use `[label](url)` to link to a resource. Use `![description](image-url)` to
embed an image with alternative text. An optional quoted title supplies a tooltip:

```md
[Release notes](release.md "Changes in this release")

![Service diagram](services.svg "Deployment services")
```

**HTML representation**

```html
<p><a href="release.md" title="Changes in this release">Release notes</a></p>
<p><img src="services.svg" alt="Service diagram" title="Deployment services"></p>
```

::: {.details summary="AST"}
```json
[
  {
    "type": "paragraph",
    "children": [
      {
        "type": "link",
        "url": "release.md",
        "title": "Changes in this release",
        "value": "Release notes"
      }
    ]
  },
  {
    "type": "paragraph",
    "children": [
      {
        "type": "image",
        "url": "services.svg",
        "alt": "Service diagram",
        "title": "Deployment services"
      }
    ]
  }
]
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `link` | String `url`; inline content. | Optional string tooltip `title`. Nested links are invalid child content. |
| `image` | String `url`, string `alt`. | Optional string tooltip `title`; attributes preserve size and delivery intent. No inline/body content field. Empty alt is permitted. |
:::

Both keep `url` and optional tooltip `title`; a link holds inline content,
while an image holds string `alt`. The result is a labelled link and the supplied
image; no separate asset preview is needed here.

Reference-style and inline links produce the same nodes. Unresolved references
use CommonMark's literal fallback. An isolated image stays in its paragraph;
only an explicit figure supplies a caption, separate from image alternative text.

### Lists and literal markers

Start a line with `1. ` for a numbered list or `- ` for a bullet list. Put a
space after the marker; no extra leading space is required. Use `[ ]` or `[x]`
after a bullet marker for an unchecked or checked task. Block context matters: `### 1. item` is a
level-three heading whose text is “1. item”. Its HTML is `<h3>1. item</h3>`
and its AST is `{"type":"heading","level":3,"value":"1. item"}`. The number
is part of the heading text.

Task items are **read-only by default**: they display the document's checked or
unchecked state. A platform or renderer may make them interactive when toggling
an item updates its `checked` value in the document and preserves that change in
the Markdown source. A visual toggle alone does not change the authored task.

In either mode, present a clear checkmark for a checked task and a clearly
visible empty box for an unchecked task. Keep both states legible against their
background; read-only tasks should not fade into the surrounding content.

Here, “read-only” describes behavior. HTML's `readonly` attribute
[does not apply to checkboxes](https://html.spec.whatwg.org/multipage/input.html#the-readonly-attribute).
An HTML renderer can use `disabled` to prevent changes and style the checkbox
for clarity. An interactive renderer should expose a labelled, keyboard-operable
control that writes the change back to the document.

```md
1. Download the package.
2. Run the installer.

- Keep a backup.
- Check the version.

- [x] Downloaded
- [ ] Verified
```

:::: {.render title="Numbered, bullet and task lists" height="300"}
```html
<ol><li>Download the package.</li><li>Run the installer.</li></ol>
<ul><li>Keep a backup.</li><li>Check the version.</li></ul>
<ul>
  <li><label><input type="checkbox" checked disabled> Downloaded</label></li>
  <li><label><input type="checkbox" disabled> Verified</label></li>
</ul>
```

::: {.details #list-ast summary="AST"}
```json
[
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
  },
  {
    "type": "list",
    "ordered": false,
    "tight": true,
    "children": [
      {
        "type": "listItem",
        "body": [
          {
            "type": "paragraph",
            "value": "Keep a backup."
          }
        ]
      },
      {
        "type": "listItem",
        "body": [
          {
            "type": "paragraph",
            "value": "Check the version."
          }
        ]
      }
    ]
  },
  {
    "type": "list",
    "ordered": false,
    "tight": true,
    "children": [
      {
        "type": "listItem",
        "checked": true,
        "body": [
          {
            "type": "paragraph",
            "value": "Downloaded"
          }
        ]
      },
      {
        "type": "listItem",
        "checked": false,
        "body": [
          {
            "type": "paragraph",
            "value": "Verified"
          }
        ]
      }
    ]
  }
]
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `list` | Boolean `ordered`; `children: ListItem[]`. | Optional integer `start` (default 1 when ordered), boolean `tight` (default false). `start` is nonnegative. |
| `listItem` | Blocks. | Optional boolean `checked`; absent means ordinary item. |
:::
::::

Editors may turn typed Markdown shortcuts into lists or headings. Editors that
offer this behavior should let Escape immediately reverse the automatic
formatting and restore the literal characters. Export uses the resulting
document structure automatically; people should not have to choose a storage
mode or add escapes themselves. An editor adapter can represent deliberately
literal lines as `lineBlock` nodes and write the readable pipe form above.
See the [writer rules](/expressive-markdown/parsing#literal-block-markers) for
preserving ordinary paragraph nodes and table cells.

> [!note] Writers preserve the document
> Exports may use safe HTML such as `<strong>Hello </strong>` or `<p></p>` when
> Markdown alone would lose formatted whitespace or an empty paragraph. Literal
> entity text is escaped too. See [writer preservation rules](/expressive-markdown/parsing#text-and-formatting-boundaries).

Image `width`/`height` are positive integer CSS-pixel strings. `responsive`
permits host-selected renditions; loading and URL selection belong to the renderer.
Use a [layout container](#layout) to align or float an image, caption or any other
group of blocks. Positioning belongs to the group, rather than to images alone.
Earlier image `placement` attributes remain preservable authored data; they do
not define the layout container's behavior.

### Safe HTML and additional styling

Keep native content and supported styling when Markdown shorthand has no
matching form:

```md
<u>Underlined</u> and <mark>highlighted</mark> text.
```

:::: {.render title="Native underline and highlight" height="105"}
```html
<p><u>Underlined</u> and <mark>highlighted</mark> text.</p>
```

::: {.details #native-html-ast summary="AST"}
```json
{
  "type": "paragraph",
  "children": [
    {
      "type": "underline",
      "value": "Underlined"
    },
    {
      "type": "text",
      "value": " and "
    },
    {
      "type": "highlight",
      "value": "highlighted"
    },
    {
      "type": "text",
      "value": " text."
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `group` | `children: Node[]`; `display: "inline"\|"block"`. | Generic structural wrapper; optional native wrapper `tag` is `span` or `div`, consistent with display. |
| `html` | String `value`; `display: "inline"\|"block"`. | Supported safe HTML after allowlist filtering; never includes discarded unsafe content. |
| `literal` | String `value`; `display: "inline"\|"block"`. | Preserved invalid/uninterpreted source for recovery, escaped for display. |

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
:::
::::

HTML uses a maintained sanitizer allowlist for elements, attributes and URLs.
`script` elements **and their contents** are discarded during parsing and never
serialized again. Supported safe HTML can become structured nodes, including
`underline`/`highlight` for `<u>`/`<mark>`. Other safe markup can remain an `html`
node. Report filtering losses; unsafe discarded content is outside preservation.
The exact sanitizer preset remains to be selected.


## Named constructs

Put `::: warning` before an important note and close it with `:::` on its own
line. Add `[Title]` after `warning` to give the note a title:

```md
::: warning [Before deploying]
Back up the database first.
:::
```

:::: {.render title="Warning callout" height="155"}
```html
<section data-type="warning" class="callout">
  <header>Before deploying</header>
  <p>Back up the database first.</p>
</section>
```

::: {.details #container-ast summary="AST"}
```json
{
  "type": "container",
  "subType": "warning",
  "title": {
    "type": "title",
    "value": "Before deploying"
  },
  "body": [
    {
      "type": "paragraph",
      "value": "Back up the database first."
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `container` | String `subType`; blocks. | Optional structured `title`. All colon containers share this family, including nested/custom types. |
| `leaf` | String `subType`; no main content field. | Optional structured `title` for a directive label; “leaf” denotes bodyless authoring scope, not an assertion about title descendants. |

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `title` | Inline content. | Used through a parent's title field; does not itself supply a heading rank. |
:::
::::


- Put the type first. Title and attributes can follow in either order.
- Start with the name; add a title or [attributes](#attributes-and-identity) when needed.
- Keep the opening header on one source line. Spaces between parts are optional;
  brackets and braces have no padding immediately inside them.
- Titles and inline labels support inline Markdown.
- Inline constructs use `:type[label]{attributes}`; bodyless blocks use
  `::type[label]{attributes}` on their own line. An inline construct needs a label
  or attributes, so bare `:word` is ordinary text.

For a custom bodyless block, `::page-break` produces a `leaf` node with
`subType: "page-break"`. Its extension defines the HTML and visible behavior;
core renderers need not invent a widget. The [block node contract](/expressive-markdown/language#container-ast)
defines this shape. The [chips and mentions](#chips-and-mentions) examples show
the inline form with standard meanings.

::: {.details summary="AST"}
```json
{"type":"leaf","subType":"page-break"}
```

A leaf has no main content field. Its optional label is a structured `title`,
so traversal still visits that title's descendants.
:::

### Nested containers

Use a longer fence for the outer container:

```md
:::: note [Outer]

::: warning [Inner]
Check the configuration.
:::

::::
```

:::: {.render title="Nested callout" height="180"}
```html
<section data-type="note" class="callout">
  <header>Outer</header>
  <section data-type="warning" class="callout">
    <header>Inner</header>
    <p>Check the configuration.</p>
  </section>
</section>
```

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "note",
  "title": {
    "type": "title",
    "value": "Outer"
  },
  "body": [
    {
      "type": "container",
      "subType": "warning",
      "title": {
        "type": "title",
        "value": "Inner"
      },
      "body": [
        {
          "type": "paragraph",
          "value": "Check the configuration."
        }
      ]
    }
  ]
}
```
:::
::::


Fences have at least three colons. A directly nested container uses fewer than
its parent; each closing fence matches its opening length. Bodies can contain
ordinary blocks, lists, quotes and code.

> [!note] Source spacing is for readability
> Blank lines just inside the fences do not add visible empty lines. Use a
> [line block](#leading-pipe-line-blocks) when the extra line is intentional.

## Attributes and identity

Use attributes for identity and settings without changing a node's content.
For example, `::: warning [Before deploying] {#check}` adds an ID to the warning
above. The compact `:::warning[Before deploying]{#check}` and reordered
`::: warning {#check} [Before deploying]` spellings have the same meaning.

The general attribute notation is:

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

**HTML representation:** attributes attach to the element representing their
node; `{#deployment-check open audience=admin}` on a disclosure becomes
`<details id="deployment-check" open data-audience="admin">…</details>`.
An unattached attribute example is notation, not a standalone rendered block.
::: {.details #attributes-ast summary="AST"}
```json
{
  "id": "deployment-check",
  "attributes": {
    "open": true,
    "audience": "admin",
    "label": "Before deploying"
  }
}
```

This is the identity/settings fragment, not a standalone node.
See the [shared AST fields](/expressive-markdown/parsing#shared-ast-contract) for the full contract.
:::

### Attaching attributes

Attach identity or presentation to the content it describes:

```md
## Deployment {#deployment}
![Service diagram](services.svg){width=640 responsive}

[Release notes](release.md){class="release-link"}
```

**HTML representation**

```html
<h2 id="deployment">Deployment</h2>
<p><img src="services.svg" alt="Service diagram" width="640" data-responsive></p>
<p><a href="release.md" class="release-link">Release notes</a></p>
```

::: {.details summary="AST"}
```json
[
  {
    "type": "heading",
    "level": 2,
    "id": "deployment",
    "value": "Deployment"
  },
  {
    "type": "paragraph",
    "children": [
      {
        "type": "image",
        "url": "services.svg",
        "alt": "Service diagram",
        "attributes": {
          "width": "640",
          "responsive": true
        }
      }
    ]
  },
  {
    "type": "paragraph",
    "children": [
      {
        "type": "link",
        "url": "release.md",
        "value": "Release notes",
        "attributes": {
          "class": "release-link"
        }
      }
    ]
  }
]
```
:::
The heading and link render normally; the image retains its authored width and
responsive setting. See [layout](#layout) for grouping and positioning content.

Heading attributes are final and whitespace-separated. Image/link attributes
are immediately adjacent. All attachments stay on the same source line.
Escape `{` to write literal text. Other block styling uses supported safe HTML.

**Rendering semantics:** use native attributes where supported; map custom
attributes to `data-*`. Custom true flags are present/empty; false flags are
omitted. Native boolean attributes follow HTML presence: an assigned string
`"false"` still enables them. See the [attribute conversion rules](/expressive-markdown/parsing#attributes-and-identity).

## YAML frontmatter

Keep document identity and publishing metadata separate from the body:

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

**HTML representation:** frontmatter produces no body element. A publisher may
use its title or description in the page shell; see the
[navigation example](/expressive-markdown/publishing#navigation-frontmatter).
::: {.details #document-ast summary="AST"}
The root is a `document`, even when its body is empty.

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

For the frontmatter above (with no body content):

```json
{
  "type": "document",
  "version": 1,
  "id": "deployment-guide",
  "title": {
    "type": "title",
    "children": [
      {
        "type": "text",
        "value": "Deploying "
      },
      {
        "type": "strong",
        "value": "safely"
      }
    ]
  },
  "metadata": {
    "description": "A guide to *repeatable* deployments.",
    "tags": [
      "deployment",
      "operations"
    ],
    "custom": {
      "owner": "platform"
    }
  },
  "body": []
}
```
:::

## Leading-pipe line blocks

Use a leading pipe when line divisions are part of the content, such as in a
postal address:

```md
| Morgan Lee
| 42 Example Street
| Bristol BS1 1AA
| United Kingdom
```

:::: {.render title="Postal address" height="150"}
```html
<p>Morgan Lee<br>42 Example Street<br>Bristol BS1 1AA<br>United Kingdom</p>
```

::: {.details #line-block-ast summary="AST"}
```json
{
  "type": "lineBlock",
  "children": [
    {
      "type": "text",
      "value": "Morgan Lee"
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "42 Example Street"
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "Bristol BS1 1AA"
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "United Kingdom"
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `lineBlock` | Inline content. | Boundaries use `break`, including within emphasis. `value: ""` means one empty represented line. A `value` containing an LF is not valid line-block shorthand. |
:::
::::


`| ` starts a preserved line; a bare `|` requests an empty one. `|Text` stays
ordinary text. Source indentation is stripped, not displayed.

The content after the pipe uses inline Markdown. A list marker there stays text:

```md
| 1. item
| - one item
| - second item
```

:::: {.render title="Literal numbered and bullet lines" height="125"}
```html
<p>1. item<br>- one item<br>- second item</p>
```

::: {.details summary="AST"}
```json
{
  "type": "lineBlock",
  "children": [
    {
      "type": "text",
      "value": "1. item"
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "- one item"
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "- second item"
    }
  ]
}
```
:::
::::


These are three represented lines, with no list. Backslash escapes are also
valid: `1\. item` and `\- item` prevent list recognition in an ordinary paragraph.
Pipes make a run of deliberate lines easier to read; escapes work wherever
ordinary inline Markdown accepts them. Inline formatting such as `**bold**`
still works inside a line block.

An established [table](#tables) takes precedence over a line block. For example,
this is a one-column table, including its required header separator:

```md
| Item |
| --- |
| First item |
| Second item |
```

The outer pipes delimit cells; they do not provide the line-block form inside a
cell. Full block content belongs to the cell itself; see [tables](#tables).
Without a valid table header and separator, leading-pipe lines remain a line
block, even when they end with another pipe.

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

**Rendering semantics:** a paragraph with `<br>` boundaries, retaining inline
formatting. See [terminal empty-line handling](/expressive-markdown/parsing#leading-pipe-line-blocks).

> [!note] Why a leading pipe?
> The marker is visible and sits at the start of the affected line. It makes
> intentional line divisions easy to distinguish from ordinary source wrapping.

### CommonMark compatibility

Existing CommonMark text can use a trailing backslash before a newline to
request a hard break within a paragraph. Expressive Markdown accepts this
form for compatibility; use leading pipes when authoring line blocks.

A trailing backslash commonly means **explicit continuation** in programming
languages: the next source line continues the same logical line, as in
[Python's line joining](https://docs.python.org/3/reference/lexical_analysis.html#explicit-line-joining).
CommonMark uses it for an **explicit break**, reversing that expectation. Leading
pipes make the intended displayed line boundaries visible instead.

```md
An ordinary source wrap
continues the same paragraph.\
This starts a new displayed line.
```

:::: {.render title="CommonMark hard-break compatibility" height="130"}
```html
<p>An ordinary source wrap continues the same paragraph.<br>This starts a new displayed line.</p>
```

::: {.details summary="AST"}
```json
{
  "type": "paragraph",
  "children": [
    {
      "type": "text",
      "value": "An ordinary source wrap"
    },
    {
      "type": "softBreak"
    },
    {
      "type": "text",
      "value": "continues the same paragraph."
    },
    {
      "type": "break"
    },
    {
      "type": "text",
      "value": "This starts a new displayed line."
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `break`, `softBreak` | No content field. | Explicit represented break versus ordinary source wrapping. |
:::
::::

Two or more trailing spaces before a newline have the same hard-break meaning.
Neither form adds a break at the end of a block, nor inside a code span or HTML
tag. These rules follow [CommonMark hard line breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks).

Both forms produce a `break` inside a `paragraph`, not a `lineBlock`. They can
render alike, but writers must preserve the node type: keeping a paragraph's
hard break must not silently turn it into a line block. See the
[writer rules](/expressive-markdown/parsing#writing-and-preservation).

## Code blocks and presentation metadata

Keep code literal while adding a caption, line highlights or line numbers:

````md
```ts {title="deploy.ts" & highlight=1,3-4 & show-line-numbers}
const mode = "safe";
await check();
await deploy();
await verify();
```
````

:::: {.render title="Captioned code with highlighted lines" height="235"}
```html
<figure><figcaption>deploy.ts</figcaption><div style="display:grid;grid-template-columns:auto 1fr;gap:12px"><pre aria-hidden="true" style="user-select:none">1
2
3
4</pre><pre><code><mark>const mode = &quot;safe&quot;;</mark>
await check();
<mark>await deploy();</mark>
<mark>await verify();</mark>
</code></pre></div></figure>
```

::: {.details #code-ast summary="AST"}
```json
{
  "type": "code",
  "language": "ts",
  "title": "deploy.ts",
  "attributes": {
    "highlight": "1,3-4",
    "showLineNumbers": true
  },
  "value": "const mode = \"safe\";\nawait check();\nawait deploy();\nawait verify();"
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `code` | String `value`. | Optional string `language`, literal string caption `title`, `attributes` and string uninterpreted `meta`. Code notation stays in value. |
:::
::::


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

**Rendering semantics:** escaped `<pre><code class="language-ts">…</code></pre>`,
optionally captioned and decorated. Keep generated line numbers out of copied
code. Colors and copy controls belong to the renderer.


## Tables

Use list-based forms inside `::: table` for **all tabular content**, including
short values. This is an intentional departure from table syntax in other
Markdown formats, chosen to make the source easier to read for both authors
and readers. Traditional pipe tables remain supported for compatibility.

Tabular data has historically been one of Markdown's less readable source
forms: dense rows of pipes and long values make cells difficult to follow.
List-based forms let each cell read from top to bottom without aligning
columns or padding neighbouring values. Each outer item is a row. Named
fields assign cells by column name; nested cell lists assign them by position.

For positional rows, only the first two list levels define table structure.
**Relative indentation determines nesting**, using ordinary Markdown list rules.
For named rows, field labels begin cells and indented content belongs to those
cells. Lists inside a cell remain content; they do not create extra rows or
cells. Columns do not need to line up horizontally.

### Untitled columns

No header setting is needed for a table without column titles:

```md
::: table

- - Install
  - Download the package.

- - Verify
  - Open the application.

:::
```

:::: {.render title="Untitled columns" height="140"}
```html
<table>
  <tbody>
    <tr>
      <td>Install</td>
      <td>Download the package.</td>
    </tr>
    <tr>
      <td>Verify</td>
      <td>Open the application.</td>
    </tr>
  </tbody>
</table>
```

::: {.details #table-ast summary="AST"}
```json
{
  "type": "table",
  "children": [
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Install"
        },
        {
          "type": "tableCell",
          "value": "Download the package."
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
          "value": "Open the application."
        }
      ]
    }
  ]
}
```

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `table` | `children: TableRow[]`. | Optional `align: ("left"\|"center"\|"right"\|null)[]`, structured caption `title`. |
| `tableRow` | `children: TableCell[]`. | Structural row grouping. |
| `tableCell` | Exactly one of `value`, inline `children`, or block `body`. | Optional boolean `header`, default false; positive integer `colSpan`/`rowSpan`, default 1; string/flag attributes hold widths and styling. |

Named fields, positional cell lists and traditional pipe source normalize to
the table nodes above. Named fields resolve column identity by exact name and
first appearance, synthesizing header cells; missing assignments become empty
cells. Positional lists consume two structural list levels; deeper lists remain
cell block content. Mixed positional rows use already-established named column
order. No field registry remains for a renderer to match again. A source
`transpose` flag is resolved into actual row/cell placement and swapped spans, not retained as a
second rendering operation. Header flags become cell `header` values and
alignment becomes `table.align`. Optional `source` provenance may remember the
source orientation without changing the semantic tree. See the
[table rules](/expressive-markdown/parsing#tables).
:::
::::


This makes two rows and two columns, with no header cells.

### Titled columns

The examples render semantic headers in bold on a light grey background.
Their AST stores header meaning, without redundant strong wrappers or color
attributes; a renderer supplies this default appearance.

Name the fields to establish titled columns:

```md
::: table

- Task: Install
  Instructions: Run the installer.

- Task: Verify
  Instructions: Check the version.

:::
```

:::: {.render title="Named columns" height="180"}
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Instructions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Install</td>
      <td>Run the installer.</td>
    </tr>
    <tr>
      <td>Verify</td>
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
          "value": "Run the installer."
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
          "value": "Check the version."
        }
      ]
    }
  ]
}
```
:::
::::


Field names are authoritative. The first appearance of a name establishes its
column, and columns keep that order. Later assignments to that name reuse the
column, even if fields appear in a different order. Missing fields leave empty
cells. A new name adds a column; earlier rows receive an empty cell there.

```md
::: table

- Task: Install
  Instructions: Run the installer.

- Notes: Check the version.
  Task: Verify

:::
```

:::: {.render title="New named field and reordered assignments" height="220"}
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
      <td>Run the installer.</td>
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
          "value": "Run the installer."
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
:::
::::


This has columns “Task”, “Instructions” and “Notes”. “Verify” still belongs to
“Task”, even though it is the second assignment in its record. `Instructions:`
with no body explicitly assigns an empty cell; omitting it also leaves that
cell empty.

Names match exactly: `Instruction` and `Instructions` are different columns.
A compiler may warn about a likely typo, but must preserve both columns and
their values. Never silently merge names or fall back to positional matching
for a named assignment.

```md
::: table

- Task: Install
  Instructions: Run the installer.

- Task: Verify
  Instruction: Check the version.

:::
```

:::: {.render title="Distinct columns for differing names" height="240"}
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Instructions</th>
      <th scope="col">Instruction</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Install</td>
      <td>Run the installer.</td>
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
          "value": "Instruction"
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
          "value": "Run the installer."
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
:::
::::


Table captions are separate: `::: table [Checklist]` captions the whole table.
For complex or untitled header cells, the positional form also accepts
`{header}` to mark its first row as headers. Header formatting does not define
column identity; named field labels are plain text.

### Positional rows after named columns

Once names establish the columns, subsequent rows may use positions:

```md
::: table

- Task: Install
  Instructions: Run the installer.

- - Verify
  - Check the version.

:::
```

:::: {.render title="Named and positional rows" height="180"}
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Instructions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Install</td>
      <td>Run the installer.</td>
    </tr>
    <tr>
      <td>Verify</td>
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
          "value": "Run the installer."
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
          "value": "Check the version."
        }
      ]
    }
  ]
}
```
:::
::::


The positional row follows the established order: “Task”, then “Instructions”.
Named rows can still reorder assignments or add columns later. A new name
appends its column; it never shifts existing positions. Missing trailing cells
are empty. To leave an interior position empty, retain an empty cell item.
A positional row with more cells than the established columns is malformed;
it cannot invent names. Named columns must be established before mixing these
forms, rather than retroactively guessing names for earlier positional data.

### Vertical fields

Add `{transpose}` to swap rows and columns:

```md
::: table {transpose}

- Name: Ada
  Role: Engineer

- Name: Grace
  Role: Reviewer

:::
```

:::: {.render title="Transposed named fields" height="140"}
```html
<table>
  <tbody>
    <tr>
      <th scope="row">Name</th>
      <td>Ada</td>
      <td>Grace</td>
    </tr>
    <tr>
      <th scope="row">Role</th>
      <td>Engineer</td>
      <td>Reviewer</td>
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
          "value": "Name"
        },
        {
          "type": "tableCell",
          "value": "Ada"
        },
        {
          "type": "tableCell",
          "value": "Grace"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "header": true,
          "value": "Role"
        },
        {
          "type": "tableCell",
          "value": "Engineer"
        },
        {
          "type": "tableCell",
          "value": "Reviewer"
        }
      ]
    }
  ]
}
```
:::
::::


The first displayed column contains the field names “Name” and “Role”, with
Ada's and Grace's values in the next two columns. Each source record supplies
a displayed column. Transposition happens after resolving names and positions;
it changes placement, not content or field matching.

The untitled positional form also accepts `{transpose}`. With positional
`{header transpose}`, the first source row becomes a displayed header column.

### Alignment

Optional `align="left,right"` sets alignment by **displayed column**, after any
transposition. Use `left`, `center`, `right` or `-` for the default. One entry
applies to every column; multiple entries match the displayed column count.
For example, `::: table {header align="left,right"}` aligns labels left and
amounts right. Cell width and wrapping remain renderer choices.

```md
::: table {header align="left,right"}

- - Item
  - Amount

- - Package
  - 24

:::
```

:::: {.render title="Aligned positional header row" height="140"}
```html
<table>
    <thead>
  <tr>
    <th scope="col">Item</th>
    <th scope="col" style="text-align:right">Amount</th>
  </tr>
</thead>
  <tbody>
<tr>
  <td>Package</td>
  <td style="text-align:right">24</td>
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
          "value": "Item"
        },
        {
          "type": "tableCell",
          "header": true,
          "value": "Amount"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Package"
        },
        {
          "type": "tableCell",
          "value": "24"
        }
      ]
    }
  ],
  "align": [
    "left",
    "right"
  ]
}
```
:::
::::

### Lists and blocks inside cells

A cell contains ordinary Markdown blocks, including paragraphs, lists, quotes,
line blocks, nested tables and complete fenced code blocks:

````md
::: table

- - Install
  -
    - Download the package.
    - Run the installer.

    ```sh
    pnpm install
    ```

:::
````

:::: {.render title="A list and code in a table cell" height="200"}
```html
<table>
  <tbody>
    <tr>
      <td>Install</td>
      <td><ul><li>Download the package.</li><li>Run the installer.</li></ul><pre><code>pnpm install</code></pre>
      </td>
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
          "value": "Install"
        },
        {
          "type": "tableCell",
          "body": [
            {
              "type": "list",
              "ordered": false,
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
            },
            {
              "type": "code",
              "value": "pnpm install"
            }
          ]
        }
      ]
    }
  ]
}
```
:::
::::


This is one row with two cells. The second cell contains a bullet list followed
by a code block. With the two-space style above, the outer list defines a row,
its nested list defines cells, and the deeper list belongs to cell content.
Blank lines can separate blocks inside a cell; they do not start another row.

Named fields support the same cell bodies:

````md
::: table

- Task: Install
  Instructions:
    1. Download the package.
    2. Run:

       ```sh
       pnpm install
       ```

:::
````

:::: {.render title="Named field with a list and fenced code" height="290"}
```html
<table>
  <thead>
    <tr>
      <th scope="col">Task</th>
      <th scope="col">Instructions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Install</td>
      <td><ol><li>Download the package.</li><li>Run:<pre><code>pnpm install</code></pre></li></ol>
      </td>
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
                      "value": "Run:"
                    },
                    {
                      "type": "code",
                      "value": "pnpm install"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```
:::
::::


To keep a list marker as literal paragraph text inside a cell, use the usual
escape: `1\. item` or `\- item`. Exporters do this automatically from the
stored document structure. The `-` markers that define rows and cells are
structural; an additional list inside a cell is normal content.

Pipes inside a list-form cell do not delimit neighbouring cells, so ordinary
text such as `left | right` needs no table-specific escape. A complete nested
pipe table still follows its own table rules inside that cell.

### Optional merged cells

The positional list and pipe forms use the same marker-only cells:

| Cell source | Meaning before transposition |
| --- | --- |
| `>` | Merge right into the next ordinary cell. |
| `^` | Continue the cell above. |
| Empty | Empty content, not a merge. |
| `\>` / `\^`, or inline code | Literal marker. |

### Spanning columns

A section label can span both columns above the individual task/status rows.
Put `>` immediately to the left of the cell whose content spans the columns:

```md
::: table {header}

- - Task
  - Status

- - >
  - Release checks

- - Install
  - Ready

- - Verify
  - Pending

:::
```

:::: {.render title="Cell spanning two columns" height="220"}
```html
<table>
  <thead><tr><th scope="col">Task</th><th scope="col">Status</th></tr></thead>
  <tbody>
    <tr><td colspan="2">Release checks</td></tr>
    <tr><td>Install</td><td>Ready</td></tr>
    <tr><td>Verify</td><td>Pending</td></tr>
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
          "value": "Status"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "colSpan": 2,
          "value": "Release checks"
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
          "value": "Ready"
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
          "value": "Pending"
        }
      ]
    }
  ]
}
```
:::
::::

“Release checks” occupies both columns. The Install and Verify rows each retain
two separate cells, so the horizontal span is visible above them.

### Spanning rows

One session can contain several activities. Put `^` below “Morning” to continue
that cell through the Breakfast and Workshop rows; Afternoon starts a new cell:

```md
::: table {header}

- - Session
  - Activity

- - Morning
  - Breakfast

- - ^
  - Workshop

- - Afternoon
  - Review

:::
```

:::: {.render title="Cell spanning two rows" height="220"}
```html
<table>
  <thead><tr><th scope="col">Session</th><th scope="col">Activity</th></tr></thead>
  <tbody>
    <tr><td rowspan="2">Morning</td><td>Breakfast</td></tr>
    <tr><td>Workshop</td></tr>
    <tr><td>Afternoon</td><td>Review</td></tr>
  </tbody>
</table>
```

::: {.details #table-grid-ast summary="AST"}
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
          "value": "Session"
        },
        {
          "type": "tableCell",
          "header": true,
          "value": "Activity"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "rowSpan": 2,
          "value": "Morning"
        },
        {
          "type": "tableCell",
          "value": "Breakfast"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Workshop"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Afternoon"
        },
        {
          "type": "tableCell",
          "value": "Review"
        }
      ]
    }
  ]
}
```
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
:::
::::

“Morning” is one cell beside two distinct activity rows. Its left column has
no divider between Breakfast and Workshop; both columns divide before Afternoon.

A marker must be the cell's entire unescaped content; `> A quotation` is
ordinary block content. Horizontal and vertical spans can combine, but merges
must form rectangles and stay within the header or body. Resolve merges in the
source grid first; `{transpose}` then swaps their row and column spans.
Merging is optional. In a named assignment, `>` and `^` remain ordinary content;
use positional rows or the pipe form when expressing merges.

### Traditional pipe tables

GFM pipe tables remain valid, including headers, column alignment and the merge
markers above. This is the same session/activity table with a vertical span:

```md
| Session | Activity |
| --- | --- |
| Morning | Breakfast |
| ^ | Workshop |
| Afternoon | Review |
```

:::: {.render title="Traditional pipe table with a row span" height="220"}
```html
<table>
  <thead><tr><th scope="col">Session</th><th scope="col">Activity</th></tr></thead>
  <tbody>
    <tr><td rowspan="2">Morning</td><td>Breakfast</td></tr>
    <tr><td>Workshop</td></tr>
    <tr><td>Afternoon</td><td>Review</td></tr>
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
          "value": "Session"
        },
        {
          "type": "tableCell",
          "header": true,
          "value": "Activity"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "rowSpan": 2,
          "value": "Morning"
        },
        {
          "type": "tableCell",
          "value": "Breakfast"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Workshop"
        }
      ]
    },
    {
      "type": "tableRow",
      "children": [
        {
          "type": "tableCell",
          "value": "Afternoon"
        },
        {
          "type": "tableCell",
          "value": "Review"
        }
      ]
    }
  ]
}
```
:::
::::

This compact compatibility form uses inline cells. It does not limit what an
Expressive table cell can contain; use the list form for full block content.
Both forms produce the same table, row and cell node types.

**Rendering semantics:** native tables with spans and supported presentation. Rich
cells retain their blocks and styling. Renderers should adapt list indentation,
block spacing and wrapping to cell widths while preserving content, list
markers and nesting. See [table rendering](/expressive-markdown/presentation#table-cell-layout)
and the [parser and writer rules](/expressive-markdown/parsing#tables).

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
| `layout` | Align or float a group of blocks. | A `<div data-type="layout">` with logical layout styles. |
| `tabs`, `tab` | Alternatives and their labelled content. | Labelled sections; optional interactive tabs. |
| `toc` | Authored section navigation. | `<nav>` with title and body. |
| Custom type | Meaning defined by its extension. | Generic labelled section. |

Use `<header>` for a section title without assuming a heading rank. An absent
title stays absent; a renderer can show a separate type label. Colors/icons are
renderer choices, and static warnings/dangers are not automatically live alerts.
Custom `info`, `important` or `caution` types are valid, not aliases for core types.

### Layout

Center a group of blocks and their text together:

````md
::: layout {align=center}
```text
Client → API → Queue
```

Services communicate through a shared queue.
:::
````

:::: {.render title="Centered layout: blocks and text" height="180"}
```html
<div data-type="layout" data-align="center" style="display:flow-root;text-align:center;border:1px dashed GrayText;padding:16px">
  <div style="inline-size:fit-content;max-inline-size:100%;margin-inline:auto"><pre><code>Client → API → Queue</code></pre></div>
  <div style="inline-size:fit-content;max-inline-size:100%;margin-inline:auto"><p>Services communicate through a shared queue.</p></div>
</div>
```
::::

The code block and caption paragraph are centered, and their text is centered.
The body accepts any block content, including figures, quotations, code, lists,
tables and nested layouts. A layout supplies presentation, not new document
meaning or a heading level.

| Attribute | Values | Meaning and default |
| --- | --- | --- |
| `align` | String `start`, `center` or `end`. | Align child blocks within the group and provide their default text alignment. Inherit the enclosing layout's alignment; otherwise use `start`. |
| `float` | String `start` or `end`. | Float the whole group at the containing flow's inline edge, allowing surrounding text to flow around it. Omitted means ordinary block flow; floating is not inherited. |
| `dir` | Native HTML `ltr`, `rtl` or `auto`. | Set the group's text direction; otherwise inherit it from the document. `lang` labels the language but does not itself set direction. |

`start` and `end` are logical directions. For horizontal Arabic or Hebrew with
`dir=rtl`, start is the right edge and end is the left edge. For `dir=ltr`,
the mapping reverses. Center does not depend on direction. Resolve block
placement against the containing layout's inline direction, text alignment
against the text's own direction, and floating against the containing flow's
direction. A nested group's explicit `dir` can change its text without changing
which edge its parent calls start.

A nested layout's explicit `align` overrides the enclosing layout for its own
placement and contents. Explicit child text styling overrides inherited text
alignment. Omitted attributes stay omitted in the AST; renderers do not write
computed defaults into the document. Preserve unrecognized values as authored
data, recommend a diagnostic, and use the corresponding omitted-value behavior.
Physical `left`/`right` values have no layout meaning.

Float a quotation and its attribution together, without making either an image:

```md
::: layout {float=end & align=center & style="inline-size:12rem"}
> A small example is easier to understand.

— The editor
:::

This paragraph flows beside the quotation when there is enough room. The quote
and its attribution stay together as one group, while this text continues in
normal reading order. A layout can hold any group of blocks, so a sidebar does
not need to be an image.

As the paragraph grows beyond the group's height, its remaining lines use the
full available width. The following paragraph stays in the same document flow.
Use this pattern for a short aside or a compact group of supporting content;
keep longer material in the main flow so it remains comfortable to read.
```

:::: {.render title="Floating layout: text flows around the group" height="330"}
```html
<article style="display:flow-root">
  <div data-type="layout" data-float="end" data-align="center" style="float:inline-end;display:flow-root;box-sizing:border-box;inline-size:12rem;max-inline-size:100%;margin-inline-start:16px;margin-block-end:12px;padding:14px;border-inline-start:4px solid LinkText;background:color-mix(in srgb,LinkText 8%,Canvas);text-align:center">
    <blockquote style="margin:0"><p>A small example is easier to understand.</p></blockquote>
    <p>— The editor</p>
  </div>
  <p>This paragraph flows beside the quotation when there is enough room. The quote and its attribution stay together as one group, while this text continues in normal reading order. A layout can hold any group of blocks, so a sidebar does not need to be an image.</p>
  <p>As the paragraph grows beyond the group's height, its remaining lines use the full available width. The following paragraph stays in the same document flow. Use this pattern for a short aside or a compact group of supporting content; keep longer material in the main flow so it remains comfortable to read.</p>
</article>
```
::::

The group retains its source position and internal reading order. Floating
does not reorder its children or turn them into columns. A renderer may keep
the group in ordinary flow when the target cannot float content or when the
available space is insufficient. Keep all content readable and in source order.

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "layout",
  "attributes": {"align": "start", "float": "end", "dir": "rtl", "lang": "ar"},
  "body": [{"type": "paragraph", "value": "مرحبًا بالعالم"}]
}
```

This uses the shared container shape. `align` and `float` remain string
attributes; no new structural node fields or parser extension are required.
:::

For HTML and right-to-left examples, see [layout rendering](/expressive-markdown/presentation#layout).

### Details

Keep supplementary content available without taking up the whole page:

```md
::: details [Show the full log] {open}
The build finished successfully.
:::
```

:::: {.render title="Expanded disclosure" height="145"}
```html
<details open><summary>Show the full log</summary><p>The build finished successfully.</p></details>
```

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "details",
  "attributes": {
    "open": true
  },
  "title": {
    "type": "title",
    "value": "Show the full log"
  },
  "body": [
    {
      "type": "paragraph",
      "value": "The build finished successfully."
    }
  ]
}
```
:::
::::


Absent `open` or `{!open}` recommends a collapsed disclosure; `{open}` recommends
expanded. Any assigned string, including `{open="false"}`, enables native HTML
boolean presence. A missing title can use the control label “Details” without
adding a title to the AST.

### Figure

Group an illustration with its caption while keeping alternative text separate:

```md
::: figure [Deployment overview]
![Services and connections](deployment.svg)
:::
```

**HTML representation**

```html
<figure>
  <p><img src="deployment.svg" alt="Services and connections"></p>
  <figcaption>Deployment overview</figcaption>
</figure>
```

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "figure",
  "title": {
    "type": "title",
    "value": "Deployment overview"
  },
  "body": [
    {
      "type": "paragraph",
      "children": [
        {
          "type": "image",
          "url": "deployment.svg",
          "alt": "Services and connections"
        }
      ]
    }
  ]
}
```
:::

The rendering is the supplied image with “Deployment overview” beneath it.

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

:::: {.render title="Choose an installation command" height="180" interactive="tabs"}
```html
<div data-tabs aria-label="Package manager">
  <section data-tab="npm"><h3>npm</h3><pre><code>npm install example-package</code></pre></section>
  <section data-tab="pnpm"><h3>pnpm</h3><pre><code>pnpm add example-package</code></pre></section>
</div>
```

::: {.details #tabs-ast summary="AST"}
```json
{
  "type": "container",
  "subType": "tabs",
  "body": [
    {
      "type": "container",
      "subType": "tab",
      "title": {
        "type": "title",
        "value": "npm"
      },
      "body": [
        {
          "type": "code",
          "language": "sh",
          "value": "npm install example-package"
        }
      ]
    },
    {
      "type": "container",
      "subType": "tab",
      "title": {
        "type": "title",
        "value": "pnpm"
      },
      "body": [
        {
          "type": "code",
          "language": "sh",
          "value": "pnpm add example-package"
        }
      ]
    }
  ]
}
```


Adjacent tabs and an explicit `tabs` wrapper produce this same group structure.
Blank source lines do not split an automatic group. Explicit groups additionally
retain authored settings, title and ID, and are not wrapped again. A tab missing
its required readable title is incomplete: preserve it and recommend a diagnostic.
:::
::::


Select npm or pnpm to switch commands. Use Left/Right Arrow, Home or End while
focused on a tab; Tab moves to its panel. Without JavaScript, both labelled
sections remain visible. These are authored rendering illustrations; the
preview's controls are not additional Expressive Markdown syntax.

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

:::: {.render title="Tabs with explicit selection settings" height="180" interactive="tabs"}
```html
<div data-tabs data-group="language" data-default="js" aria-label="Example language">
  <section data-tab="js"><h3>JavaScript</h3><p>JavaScript example.</p></section>
  <section data-tab="ts"><h3>TypeScript</h3><p>TypeScript example.</p></section>
</div>
```

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "tabs",
  "attributes": {"group": "language", "default": "js"},
  "body": [
    {"type": "container", "subType": "tab", "title": {"type": "title", "value": "JavaScript"}, "attributes": {"value": "js"}, "body": [{"type": "paragraph", "value": "JavaScript example."}]},
    {"type": "container", "subType": "tab", "title": {"type": "title", "value": "TypeScript"}, "attributes": {"value": "ts"}, "body": [{"type": "paragraph", "value": "TypeScript example."}]}
  ]
}
```

Tabs use `container/subType: "tabs"` with `container/tab` nodes in `body`.
A tab's selection identity is string `attributes.value`; it is distinct from
its generic node `id`. Titles are structured nodes. Group settings live in
`attributes`; automatic groups have no authored settings, title or ID.
:::
::::

The JavaScript panel starts selected because its value matches `default=js`.
Switching panels leaves both bodies in the document. The labelled sections
are also the no-JavaScript fallback.

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

**Rendering semantics:** labelled sections showing all content without JavaScript.
Interactive renderers supply accessible tab roles, keyboard operation and
control/content relationships. See [rendering recommendations](/expressive-markdown/presentation#selection-state-and-identity).

### Chips and mentions

Use chips for compact labels and mentions for people or other entities.


```md
Status: :chip[Ready]{tone=green}.

Thanks, @[Ada Lovelace].

Thanks, @ada-lovelace#user-123.
```

:::: {.render title="Status chip and unresolved mentions" height="165"}
```html
<p>Status: <span class="chip">Ready</span>.</p><p>Thanks, <span class="mention">Ada Lovelace</span>.</p><p>Thanks, <span class="mention">@ada-lovelace</span>.</p>
```

::: {.details #semantic-inline-ast summary="AST"}
```json
[
  {
    "type": "paragraph",
    "children": [
      {
        "type": "text",
        "value": "Status: "
      },
      {
        "type": "inline",
        "subType": "chip",
        "value": "Ready",
        "attributes": {
          "tone": "green"
        }
      },
      {
        "type": "text",
        "value": "."
      }
    ]
  },
  {
    "type": "paragraph",
    "children": [
      {
        "type": "text",
        "value": "Thanks, "
      },
      {
        "type": "inline",
        "subType": "mention",
        "value": "Ada Lovelace"
      },
      {
        "type": "text",
        "value": "."
      }
    ]
  },
  {
    "type": "paragraph",
    "children": [
      {
        "type": "text",
        "value": "Thanks, "
      },
      {
        "type": "inline",
        "subType": "mention",
        "value": "ada-lovelace",
        "ref": "user-123"
      },
      {
        "type": "text",
        "value": "."
      }
    ]
  }
]
```

The [recognized semantic subtype registry](/expressive-markdown/language#recognized-semantic-subtypes)
defines the shared vocabulary: container `note`, `tip`, `warning`, `danger`,
`details`, `figure`, `layout`, `tabs`, `tab`, `toc`; inline `chip`, `mention`.
A mention has an optional string `ref` field for its entity target. The shared
node families allow generic traversal; subtypes supply specific meanings.
Custom subtypes are valid but do not acquire a standard subtype's contract.

| Feature | AST shape | Content and presentation data |
| --- | --- | --- |
| Chip | `inline`, `subType: "chip"` | `value` or inline `children`; `attributes.tone` for neutral/blue/green/yellow/red/purple or a preserved custom tone. |
| Mention | `inline`, `subType: "mention"` | Authored label/handle in `value`/`children`, excluding the `@` marker. Optional string `ref` targets an entity; optional `attributes.url` supplies navigation. Label-only mentions are valid. Generic `id` identifies this occurrence. |

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

| Type | Required fields/content | Additional fields and constraints |
| --- | --- | --- |
| `inline` | String `subType`; optional inline content. | Attribute-only atomic directives may omit content. |
:::
::::


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

Save readable navigation alongside the document it describes:

```md
::: toc [On this page] {depth=3 format=bulleted}
- [Installation](#installation)
- [Configuration](#configuration)
:::
```

:::: {.render title="Saved table of contents" height="145"}
```html
<nav aria-label="On this page"><header><strong>On this page</strong></header><ul><li><a href="#installation">Installation</a></li><li><a href="#configuration">Configuration</a></li></ul></nav>
```

::: {.details summary="AST"}
```json
{
  "type": "container",
  "subType": "toc",
  "attributes": {
    "depth": "3",
    "format": "bulleted"
  },
  "title": {
    "type": "title",
    "value": "On this page"
  },
  "body": [
    {
      "type": "list",
      "ordered": false,
      "tight": true,
      "children": [
        {
          "type": "listItem",
          "body": [
            {
              "type": "paragraph",
              "children": [
                {
                  "type": "link",
                  "url": "#installation",
                  "value": "Installation"
                }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "body": [
            {
              "type": "paragraph",
              "children": [
                {
                  "type": "link",
                  "url": "#configuration",
                  "value": "Configuration"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```
:::
::::


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
are extension contracts, not additional core semantic types. A `mermaid` or
`math` fence uses the [code AST](#code-ast) with that `language`; the inline
example uses `{"type":"inline","subType":"math","children":[{"type":"inlineCode","value":"x_1^2"}]}`.
Its HTML fallback is escaped code; an extension can additionally render a
diagram or equation. The visual result depends on that extension.

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
| `container` | `note`, `tip`, `warning`, `danger`, `details`, `figure`, `layout`, `tabs`, `tab`, `toc`. |
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
