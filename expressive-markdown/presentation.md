---
title: Rendering Recommendations
order: 4
blurb: rendering · accessibility · safe HTML
eyebrow: Expressive Markdown · Proposal
status: Unofficial Editor's Draft · Stage 0
---

# Rendering Recommendations

Expressive defines what a document means. Renderers choose how it looks. These
recommendations show how to keep that meaning readable and accessible in HTML,
including when an interactive widget is unavailable.

## Callouts and captions {#coverage-matrix}

```md
::: warning [Before deploying]
Back up the database first.
:::
```

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

````md
```ts {title="deploy.ts" & highlight=1,3-4 & show-line-numbers}
const mode = "safe";
await check();
await deploy();
await verify();
```
````

Show the caption **deploy.ts**, highlight line 1 and lines 3–4, and display line
numbers. Keep line-number labels and other decorations out of copied code.
The code's stored text remains unchanged. Without optional decoration, escaped
`<pre><code>` is a readable fallback.

Leading-pipe line blocks preserve requested lines and empty lines with `<br>`
boundaries. Merged tables use native `colspan`/`rowspan`; do not flatten them.
Keep rich cell content, alignment and supported styling. Image size, placement
and responsive settings express layout intent; loading and rendition selection
remain renderer choices.

A table of contents renders its saved links inside `<nav>`. An optional refresh
updates the actual entries in the document and source. Rendering alone does not
replace those entries with an empty generated placeholder.

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
For data structures, see the [Document AST](/expressive-markdown/ast).
