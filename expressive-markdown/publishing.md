---
title: Publishing & Navigation
order: 5
blurb: navigation labels · hidden pages
eyebrow: Expressive Markdown · Optional profile
status: Unofficial Editor's Draft · Stage 0
---

# Publishing & Navigation

The optional publishing profile gives documentation sites two shared navigation
settings: a shorter label and whether to include a page in generated navigation.

## Navigation frontmatter

```yaml
---
title: Installing Expressive Markdown
navigation:
  label: Installation
  hidden: false
---
```

The page title stays **Installing Expressive Markdown**; its sidebar or menu
entry can read **Installation**.

::: {.render title="Navigation label and page title" height="240"}
```html
<nav aria-label="Documentation"><a href="/installation">Installation</a></nav><article><h1>Installing Expressive Markdown</h1></article>
```
:::


| Field | Type | Meaning and default |
| --- | --- | --- |
| `navigation` | Mapping | Optional metadata, stored in `document.metadata.navigation`. |
| `navigation.label` | Plain-text string | Generated navigation label. Omission uses the document title's readable text; without a title, the publisher uses its documented fallback. |
| `navigation.hidden` | Boolean | Omit this page from generated navigation. Default `false`. |

> [!note] Hidden means unlisted
> Setting `hidden: true` removes a navigation entry. It does not make the page
> private, remove its content or stop people from reaching its address.

The label does not replace the page title or rewrite authored links. A page's
table of contents remains separate, readable document content.

## Reading and preserving settings

Core parsers retain this metadata without having to generate navigation.
Publishers using the profile apply the types above:

- Preserve invalid values and recommend a diagnostic; do not coerce strings to
  booleans or other values.
- Preserve unknown keys inside `navigation`.
- Preserve metadata `null` as data, even where the profile expects another type.

Routes, redirects and routing aliases belong to the publishing application.
They are not fields defined by this profile. See [YAML frontmatter](/expressive-markdown/language#yaml-frontmatter)
for the general metadata syntax and [rendering recommendations](/expressive-markdown/presentation)
for presenting document content.
