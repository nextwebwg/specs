---
title: Parsing rules
order: 1
blurb: source reading · empty-element placement · recovery · boundaries
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · proposed rules
status: "Unofficial Editor's Draft · Stage 0"
---

# Parsing rules

**Read the source with HTML's existing rules. Place eligible `/>` elements as empty elements.** The proposed parser keeps these two jobs separate so an empty-element shorthand cannot change previously recognized text into a tag.

## What the slash does in existing HTML

```html
<div /><p>Hello</p>
```

HTML's **tokenizer** reads characters and recognizes the self-closing marker on `div`. Its **tree builder** decides where nodes go. For an ordinary non-void HTML element, existing tree-building rules leave the element open despite that marker. The paragraph becomes its child.[^1]

::::: two
:::: {.parser-path}
### Existing HTML

::: flow
- Read a div start tag with a self-closing marker
- Open div; retain it in HTML's recovery records
- Read a paragraph start tag and its text
- Place the paragraph inside div {.acc}
:::

```text
body
└─ div
   └─ p
      └─ "Hello"
```
::::
:::: {.parser-path}
### Proposed opt-in

::: flow
- Read the same div start tag and marker
- Retain div in the source reader's recovery records
- The placement builder opens and closes div
- Place the recognized paragraph after div {.acc}
:::

```text
body
├─ div
└─ p
   └─ "Hello"
```
::::
:::::

## The distinction: reading and placement have separate state

The **source reader** determines which characters are tags, which are text, and which namespace and attributes each element has. It follows existing HTML recovery, including its open-element and formatting records.

The **placement builder** receives those already-read tokens. For an eligible `/>`, it performs the normal opening action followed by the normal closing action. That gives authors ordinary empty-element placement, including formatting and table rules.

**A placement action cannot authorize a different interpretation of the source.** Before output is exposed, each output element must correspond to an actual source-reader element with the same namespace and attributes. Template ownership, foreign-namespace ancestry, and script/style/text contents must also agree. If they do not, the parser uses the source reader's recovery result, as described below.

This is the added mechanism beyond simply treating `/>` as an immediate end tag. The source reader retains the context needed to keep text as text, while the placement builder gives ordinary shorthand its expected result.

### Ordinary nesting and tables

```html
<nav><nav /></nav><p>Outside both navs</p>
<table><tr><td /><td>Second cell</td></tr></table>
```

The inner nav is empty; the real `</nav>` closes the outer nav. The paragraph follows both. The table has one row and two cells, with the first cell empty. Both examples produce the same tree as spelling out the empty element's start and end tags. Table rows and cells use HTML's normal table-placement rules.

## Why remembering the element matters

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

The security question is whether the apparent image stays stylesheet text or becomes an element with executable code. Closing div in the **source reader** too early changes how the later `</div>` recovers from SVG.[^2]

::::: two
:::: {.parser-path}
### If the source reader immediately closes div

::: flow
- Open div and immediately remove its recovery entry
- Read svg; enter SVG context
- The later closing div has no matching entry {.acc}
- Interpret the following style in SVG context
- Recognize an image with an event handler
:::
::::
:::: {.parser-path}
### Proposed reader and checked placement

::: flow
- Place an empty div; retain its source-reader entry
- Read svg with existing HTML rules
- The later closing div exits SVG and div {.acc}
- Read the following HTML style and its text
- Reject conflicting placement; keep the apparent image as text
:::
::::
:::::

The placement builder receives a **text token** containing the apparent image. It never reads that string as HTML again. In this malformed example its attempted namespace placement conflicts with the source reader, so the checked recovery path preserves the HTML style and its contents. There is no image element or handler to activate.

The parser uses the actual recovery records at that point. It does not infer intent from a future tag name or keep a stale closing target after HTML has removed it.

## Boundaries that require a real closing tag

```html
<style/><img src=x onerror="attack()"></style>
```

Existing HTML reads the apparent image as stylesheet text. The proposal retains style's text-reading boundary, so that remains text. Similarly, `<script />` opens a script and requires `</script>`; an external script is written `<script src="app.js"></script>`.

| Boundary | Handling and reason |
| --- | --- |
| A start that enters a special text-reading state, such as HTML `script`, `style` or `textarea` | Keep ordinary closing behavior. An early close would expose text as markup. The actual tokenizer transition determines this category. |
| `template` | Keep its content document and ordinary closing behavior. Its contents must remain in their inactive owner. Eligible shorthand inside that content document still works. |
| `form` and `select` | Keep ordinary closing behavior. These parser-owned contexts can suppress subsequent elements: after `<form/>`, a second form start may be ignored; after `<select/>`, a second select start may be ignored. Emptying these contexts would require a different source interpretation. |
| `html`, `head`, `body`, `frameset` | Keep document-construction handling. These elements govern the document's structure and parser mode. |

Void elements and SVG/MathML elements use HTML's existing acknowledged self-closing handling. For other eligible elements, attributes apply to the resulting DOM in the usual way. Following siblings consequently do not acquire an empty element's attributes or ancestry.

## Recovery when the two jobs disagree

Ordinary shorthand uses ordinary opening-and-closing placement. Malformed input can request a node, namespace, or protected context the source reader did not recognize. The proposed recovery is deterministic:

1. **Try ordinary placement.** Accept it only if every output element has a matching source-reader identity, namespace, attributes and protected context, with unchanged code/text-owner contents. Each source element can appear at most once.
2. **Try recognition-based placement.** Keep eligible marked elements empty and move their recognized children immediately after them, recursively. Keep text/code owners and protected boundaries intact. Check this result against the same requirements.
3. **Use the source tree if that check fails too.** HTML's source interpretation is the final authority, even when retaining it means the malformed shorthand does not produce an empty element.

A completed token checkpoint selects one valid result before a parser-triggered script observes output. Implementations must preserve application-owned DOM changes across later parser updates.

**The normal authoring rule is an empty element; the recovery rule is source interpretation first.** The reference matches explicit empty pairs in 4,000 structured authoring cases and 1,000 generated table cases. It does not promise pair equivalence for arbitrary malformed HTML.

::: {.details summary="Implementation and proof details"}

[placement.mjs](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/placement.mjs) uses an ordinary parse5 source reader and a separate tree builder receiving cloned tokens. It associates written elements with source offsets, and implied elements with the token that caused their creation. Both normal placement and projected recovery are checked before selection.

The final check preserves element identity, namespace, attributes, template-content ownership, foreign ancestry and actual text/code-owner contents. It permits changes in ordinary parentage, order and formatting-repair output. It does not require the earlier projection design's total payload order.

[Placement.lean](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/Placement.lean) checks the abstract selection rule: every selected element carries information authorized by the source, even when the first two choices fail. This is not a verified translation of the JavaScript or a complete browser parser proof.

The [live adapter](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/live-dom.mjs) reconciles parser-owned output with application mutations. It constructs nodes in a document without a browsing context before insertion, preserving inactive template resources in the tested cases. Full-tree snapshots and checks are a correctness prototype; their cost has not been established as suitable for a production parser.

:::

## Opt in explicitly

Use either declaration:

```html
<!DOCTYPE html PUBLIC "self-closing">
```

Or:

```html
<!DOCTYPE html PUBLIC "next">
```

`self-closing` selects this feature. `next` selects the current and future HTML Next family supported by the implementation. [HTML Feature Profiles](/html-feature-profiles/) owns selection, the proposed response header and explicit API options. Existing documents keep their existing interpretation.

The slash must be a marker rather than part of an unquoted value:

```html
<div data-path=assets/ /> <!-- Marker; value is assets/ -->
<div data-path=assets/>  <!-- No marker; value is assets/ -->
```

### Explicit parsing and insertion APIs

Existing string-parsing APIs keep their existing behavior. The shared profile proposal defines explicit selection for proposed `Document.parseHTML()` and `Document.parseHTMLUnsafe()` options. A fetched string can be parsed with an explicit selection independently of its caller's document; a response header does not remain attached to a `.text()` string.

Safe parsing methods still perform their normal sanitization for untrusted HTML. That is a separate API protection, not the reason this algorithm preserves text recognition. Inserting the resulting nodes does not switch the destination document's parsing mode.

Legacy document writing must be rejected or isolated in an opted-in navigation until an implementation specifies how writes participate in both recognition and output state. Native profile API integration and execution review remain implementation work.

[Security properties, tests and remaining work →](/self-closing-html/security)

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state), [trailing solidus parse error](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus), [tree construction](https://html.spec.whatwg.org/multipage/parsing.html#tree-construction) and [foreign content](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign).
[^2]: WHATWG HTML, [#9491: sanitizer mismatch](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [parsing-mode changes at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
:::
