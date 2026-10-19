---
title: Rendering Recommendations
order: 3
blurb: rendering · accessibility · safe HTML
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Rendering Recommendations

Expressive defines what a document means. Renderers choose how it looks. These
rendering examples and recommendations show how to keep that meaning readable and accessible in HTML,
including when an interactive widget is unavailable.

## Callouts and captions {#coverage-matrix}

Draw attention to information while retaining a readable title and body:

```md
::: warning [Before deploying]
Back up the database first.
:::
```


:::: {.render title="Warning callout" height="155"}
```html
<section class="callout"><header>Before deploying</header><p>Back up the database first.</p></section>
```

::: {.details summary="AST"}
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

See the [feature definitions](/expressive-markdown/language) for node constraints.
:::
::::

Show this as a warning with a visible title and body. A border, color or icon can
help, but the meaning should remain understandable without color.

| Content | Recommended HTML |
| --- | --- |
| `note`, `tip`, `warning`, `danger` or a custom container | A labelled `<section data-type="…">`. |
| Container title | `<header>` content; do not assign an arbitrary heading level. |
| `details` | `<details>` with a `<summary>` title. |
| `figure` | `<figure>` with its caption in `<figcaption>`. |
| `chip` or a mention without a URL | A labelled `<span>`. |
| Mention with a URL | A link using the authored label. |

A static warning is not automatically an ARIA live alert. Keep an image's
alternative text separate from its figure caption. Preserve custom types even
when the renderer can offer only a generic section.

## Tabs and saved content {#selection-state-and-identity}

Offer alternative instructions without losing any alternative's content:

```md
::: tab [npm]
Run `npm install`.
:::

::: tab [pnpm]
Run `pnpm install`.
:::
```

Adjacent tabs form one group; blank lines do not split it. An interactive
renderer can show one at a time. A static export should show both as labelled
sections, keeping every tab's content.


:::: {.render title="Static tab fallback" height="200"}
```html
<section><header><strong>npm</strong></header><p>Run <code>npm install</code>.</p></section><section><header><strong>pnpm</strong></header><p>Run <code>pnpm install</code>.</p></section>
```

::: {.details summary="AST"}
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
          "type": "paragraph",
          "children": [
            {
              "type": "text",
              "value": "Run "
            },
            {
              "type": "inlineCode",
              "value": "npm install"
            },
            {
              "type": "text",
              "value": "."
            }
          ]
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
          "type": "paragraph",
          "children": [
            {
              "type": "text",
              "value": "Run "
            },
            {
              "type": "inlineCode",
              "value": "pnpm install"
            },
            {
              "type": "text",
              "value": "."
            }
          ]
        }
      ]
    }
  ]
}
```

See the [feature definitions](/expressive-markdown/language) for node constraints.
:::
::::

An outer `tabs` container can supply settings such as
`{group=language & default=js}`. Related groups synchronize by tab selection
value. A group without the chosen value keeps its current selection. A valid
query selection takes precedence over a remembered choice, then the authored
default; otherwise select the first tab.

Use the [ARIA tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/),
including keyboard controls, selected state and control/content relationships.
Generated control IDs must not collide with authored IDs. Remembering choices
and delaying inactive content's display belong to the renderer; neither removes
content from the document or export.

## Code, lines and tables

Help readers find the important lines while preserving the code they copy:

````md
```ts {title="deploy.ts" & highlight=1,3-4 & show-line-numbers}
const mode = "safe";
await check();
await deploy();
await verify();
```
````


:::: {.render title="Code caption and highlights" height="235"}
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

::: {.details summary="AST"}
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

See the [feature definitions](/expressive-markdown/language) for node constraints.
:::
::::

Show the caption **deploy.ts**, highlight line 1 and lines 3–4, and display line
numbers. Keep line-number labels and other decorations out of copied code.
The code's stored text remains unchanged. Without optional decoration, escaped
`<pre><code>` is a readable fallback.

Leading-pipe line blocks preserve requested lines and empty lines with `<br>`
boundaries. Merged tables use native `colspan`/`rowspan`; do not flatten them.
Keep rich cell content, alignment and supported styling. Image size and responsive
settings preserve asset intent; layout containers express grouping and placement.
Loading and rendition selection remain renderer choices.

A table of contents renders its saved links inside `<nav>`. An optional refresh
updates the actual entries in the document and source. Rendering alone does not
replace those entries with an empty generated placeholder.

### Table-cell layout

Table cells can contain full block content, including lists, multiple paragraphs
and fenced code blocks. Keep those structures when rendering. Cell width is a
presentation constraint, not a reason to remove a supported kind of content.


````md
::: table

- Task: Install
  Instructions:
    1. Download the package.
    2. Run the installer.

    ```sh
    pnpm install
    ```

:::
````

:::: {.render title="Compact table cell with a list and code" height="235"}
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
      <td><ol><li>Download the package.</li><li>Run the installer.</li></ol><pre><code>pnpm install</code></pre>
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

See the [feature definitions](/expressive-markdown/language) for node constraints.
:::
::::

Semantic header cells can use bold text and a neutral background by default.
These examples use light grey in the light theme. Their source and AST retain
header semantics without extra bold marks or stored cell colors. Custom
formatting remains separate authored data.

Renderers should adapt page-level styles to the available cell space:

- Prefer compact list indentation and block spacing. A list need not receive
  the same inset or outer margins as one in the main document. Keep markers
  visible and nested levels distinguishable.
- Choose text wrapping for the cell width instead of inheriting the main
  document's width and wrapping policy unchanged. Preserve authored line
  boundaries where they carry meaning.
- Code may wrap visually or scroll within its cell. Preserve its stored
  whitespace and line divisions exactly; copying code must return the original
  text, without visual wrap breaks, line numbers or other decoration.

Use semantic HTML lists and code blocks within native table cells. Changing
their spacing or visual wrapping must not flatten their document structure.

## Layout

Align a group's child blocks and their text together. Use logical directions so
the same document can be read in left-to-right and right-to-left contexts:

```md
::: layout {align=start dir=rtl lang=ar}
بداية السطر
:::

::: layout {align=center dir=rtl lang=ar}
وسط السطر
:::

::: layout {align=end dir=rtl lang=ar}
نهاية السطر
:::
```

:::: {.render title="RTL layout: start, center and end" height="220"}
```html
<div dir="rtl" lang="ar">
  <div data-type="layout" data-align="start" style="display:flow-root;text-align:start;border-block-end:1px dashed GrayText">
    <div style="inline-size:fit-content;max-inline-size:100%;margin-inline-start:0;margin-inline-end:auto"><p>بداية السطر</p></div>
  </div>
  <div data-type="layout" data-align="center" style="display:flow-root;text-align:center;border-block-end:1px dashed GrayText">
    <div style="inline-size:fit-content;max-inline-size:100%;margin-inline:auto"><p>وسط السطر</p></div>
  </div>
  <div data-type="layout" data-align="end" style="display:flow-root;text-align:end;border-block-end:1px dashed GrayText">
    <div style="inline-size:fit-content;max-inline-size:100%;margin-inline-start:auto;margin-inline-end:0"><p>نهاية السطر</p></div>
  </div>
</div>
```
::::

Here start is the right edge. With `align=end`, the group aligns its content to
the left edge; center stays centered. Hebrew follows the same direction rules.
The [layout contract](/expressive-markdown/language#layout) defines inheritance,
child overrides, floating and the shared AST shape.

Native CSS can supply this behavior without a layout runtime. For example, a
normal-flow `<div data-type="layout">` can use `text-align:start`, with
shrink-to-fit item wrappers positioned by logical inline margins. Keep an item's
placement wrapper in the parent's direction when the item has its own `dir`.
Its text still follows its own direction. Preserve safe explicit child styling.

Use a new block formatting context, such as `display:flow-root`, to contain
floats within the group. A floated layout itself can use `float:inline-start`
or `float:inline-end`, with a bounded inline size. The group floats as a whole,
including any title, figure, quotation or code inside it. Following text flows
around that group; the floated content does not wrap itself. A layout inside a
host flex/grid formatting context follows native float rules there.

For a bounded floating sidebar:

```md
::: layout {float=start & align=center & dir=rtl & lang=he & style="inline-size:12rem"}
> הערה קצרה

מידע נוסף
:::

הטקסט שמסביב ממשיך לזרום לצד הקבוצה.
```

Floating follows the containing flow's direction, so this group floats at the
start edge of an RTL document and at the start edge of an LTR document even
though its internal text is Hebrew. Test both document directions and explicit
nested direction changes. `lang` alone does not establish RTL layout.

Constrain the group and responsive images to the available inline size. Retain
normal document order and readable in-flow fallback when there is insufficient
room or the output target lacks layout support. Do not use a layout group as a
substitute for the data relationships of a semantic table.

## Safe HTML and editing {#presentation-preservation}

HTML passes through a maintained sanitizer allowlist for elements, attributes
and URLs. A `script` element and its contents are discarded during parsing and
never written back out. The exact sanitizer preset remains to be selected.

> [!note] Preserve supported content
> Preservation covers safe, supported document data. Unsafe content discarded
> by the HTML policy is outside that guarantee. Report filtering or unsupported
> conversions rather than silently claiming a complete export.

Editors should map supported HTML to editable nodes and keep supported
class/style data, even when the current theme does not show it. An HTML string
that merely looks like a table does not establish editable table support.
When Markdown shorthand cannot express supported content, use supported safe
HTML or report the conversion limitation.

Fonts, themes, toolbar placement and highlighting engines are renderer choices.
Diagram/math extensions should retain their literal notation for editing and
fallback display. No JavaScript runtime or CSS framework is required.

For exact syntax and defaults, see [Language & Semantics](/expressive-markdown/language).
For data structures, open the AST disclosures beside the [feature examples](/expressive-markdown/language).
