---
title: Parsing rules
order: 1
blurb: opt-in · closure · recovery · insertion APIs
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · proposed rules
status: "Unofficial Editor's Draft · Stage 0"
---

# Parsing rules

**The change is what the parser does with the slash in `/>`.** Today, an ordinary HTML opening tag stays open despite that slash. With the proposed opt-in, the parser processes the opening tag and its matching closing action together.

## How HTML parses this today

Assume the parser is inside the document's `body`:

```html
<div class="badge" />
<p>Hello</p>
```

HTML parsing has two cooperating parts. The **tokenizer** reads characters and identifies tags or text. The **tree builder** creates elements and remembers which elements are open, so it knows where to put the next node.

For `<div />`, today's tokenizer recognizes the slash and marks the opening-tag token as self-closing. The HTML tree builder creates the `div`, but ignores that marker for an ordinary non-void HTML element. This is a parse error with a defined recovery: continue with the `div` open.[^4]

## Follow the same source through both algorithms

::::: two
:::: {.parser-path}
### HTML today

::: flow
- Read `<div class="badge" />`
- Create the `div`; ignore its self-closing marker {.acc}
- Keep `div` as the current parent
- Read `<p>`; insert it inside `div`
:::

```text
body
└─ div.badge
   └─ p
      └─ "Hello"
```
::::
:::: {.parser-path}
### With the proposed opt-in

::: flow
- Read `<div class="badge" />`
- Process the normal `div` opening action
- Process its matching closing action {.acc}
- Read `<p>`; insert it inside `body`
:::

```text
body
├─ div.badge
└─ p
   └─ "Hello"
```
::::
:::::

| Step | HTML today | Proposed behavior |
| --- | --- | --- |
| Read `<div class="badge" />` | Create `div`. It becomes the current parent. | Create `div`. It becomes the current parent. |
| Handle the self-closing marker | Recover from the parse error by leaving `div` open. | Process the matching `div` closing action. The current parent becomes `body`. |
| Read `<p>` | Create `p` inside `div`. | Create `p` inside `body`. |
| Read `Hello`, then `</p>` | Put the text in `p`, then close `p`. The current parent is `div`. | Put the text in `p`, then close `p`. The current parent is `body`. |
| Reach the end of the source | Finish with the DOM already built: `p` remains inside `div`. | Finish with the DOM already built: `p` follows the empty `div`. |

The recovery step is deliberate browser behavior. Today's parser accepts the malformed shorthand and continues; it does not infer the author's intended empty `div`.

## Why parser context matters

Some opening tags also change how following characters are read. For example:

```html
<style />
<p>Hello</p>
```

::::: two
:::: {.parser-path}
### HTML today

::: flow
- Open `style`; ignore its self-closing marker
- Read following characters as stylesheet text
- Keep `<p>Hello</p>` inside `style` as text
:::
::::
:::: {.parser-path}
### With the proposed opt-in

::: flow
- Open `style`
- Process its closing action; return to reading HTML markup {.acc}
- Read `<p>Hello</p>` as a paragraph
:::
::::
:::::

This changes both the element boundary and the context used to read the next characters. The same principle applies to `script` and `textarea`. A self-closing external script still loads and executes according to its normal script rules.

## The proposed operation

For a non-void HTML opening-tag token marked self-closing:

1. Process its ordinary opening action once.
2. Process a matching closing-tag token in the resulting parser state.
3. Finish the resulting parser work, including any change out of a text-reading context, before reading more source.

Formatting, tables, forms, and templates use their existing opening, closing, and recovery rules at those steps. Attributes follow ordinary parsing. For example, `<table />` starts and ends the table before the following source is read.

HTML void elements such as `img` already finish at their opening tag. Their behavior stays the same. SVG and MathML retain their existing foreign-content self-closing rules. HTML recovery still governs invalid contexts and document roots: `<html />` does not permit siblings outside the document root. `plaintext` ends at the token boundary under this proposal; today's literal `</plaintext>` would itself be read as plaintext.

## Select this behavior

Use either declaration:

```html
<!DOCTYPE html PUBLIC "self-closing">
```

Selects this feature.

```html
<!DOCTYPE html PUBLIC "next">
```

Opts into the current and future HTML Next family supported by the browser, including this feature. [HTML Feature Profiles](/html-feature-profiles/) defines the declarations, proposed HTTP header, and explicit parsing options. A later doctype mutation does not switch a running parser.

### Preserve normal attribute parsing

The slash must be a self-closing marker, not part of an unquoted value:

```html
<div data-path=assets/ /> <!-- Self-closing; value is assets/ -->
<div data-path=assets/>  <!-- Not self-closing; value is assets/ -->
```

Quoted strings, comments, and text already inside a script or stylesheet are not searched and rewritten for slash syntax.

::: {.details summary="Implementation contract: token processing and checkpoints"}

When an HTML start-tag token carries the self-closing flag, process its ordinary start-tag action once, then process the matching end-tag token in the resulting parser state. Reprocessing the start through insertion modes must not duplicate the synthetic end tag. Existing void handling and native foreign-element handling remain intact, including transitions back into HTML processing.

Complete the synthetic end and restore the appropriate source-tokenizer state before consuming more characters. Clear a pending initial-newline suppression when that text element has already ended. HTML formatting recovery, form state, table placement, template insertion modes, and namespace transitions use the resulting parser state.

Before running a parser-triggered script or delivering a callback, expose the DOM for completed processing. A self-closing external script keeps the normal blocking/async/defer/module rules; the slash does not make it inert. Preserve script mutations and normal pause/resume behavior. Declarative shadow-root host selection follows ordinary HTML placement; do not attach a following declaration to an already closed host.

The reference implementation is in [closure/parser.mjs](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/closure/parser.mjs). Its scope and browser-adapter limits are in the [current evidence](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme).

:::

## Untrusted HTML and the separate safe parsing API

**Loading an opted-in page does not sanitize its HTML.** The parsing rule above constructs the document, including authored scripts and event-handler attributes.

Sanitization is a separate operation for untrusted content. A safe parsing method first creates elements, text nodes, and attributes using the selected grammar, then removes unsafe content from those nodes. For example, it can remove an `onerror` attribute from an image before the caller inserts it.

This order matters because changing the grammar can turn apparent text into an element. A string filtered under today's HTML rules can therefore become unsafe under the new rules. The proposed safe method filters the selected grammar's resulting nodes and returns them for direct insertion.

[HTML Feature Profiles](/html-feature-profiles/#explicit-parsing) proposes a `profile` option for `Document.parseHTML()` and `Document.parseHTMLUnsafe()`. The safe method retains its mandatory safety protections under the selected grammar; the unsafe method is not a sanitizer. These are proposed native API extensions, not currently supported options.

The [safe reference parser](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/closure/safe-dom.mjs) demonstrates grammar-first parsing and in-place DOMPurify filtering. It is not a native Sanitizer API implementation or a proof that arbitrary sanitizer configurations are safe.

### Parse independently of the caller's document

Explicitly selecting `self-closing` for fetched HTML does not require the caller's document to opt in. Omitting `profile` keeps existing behavior; `inherit` explicitly copies the relevant document's selection, and `next` selects the supported HTML Next family. The shared profile proposal owns normalization and failure rules.

A fetched response's headers do not remain attached to a `.text()` string. Forward a selection explicitly when intended. Inserting nodes does not switch the destination document's parser profile or reparse their text. Full-document parsing does not supply a table-context fragment API; a fragment operation also needs its actual context.

### Keep existing insertion APIs stable

`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `DOMParser`, existing fragment operations, and `iframe.srcdoc` retain their current grammar. Source text cannot change a legacy API's mode by embedding a doctype. Legacy `document.write`, `writeln`, and document-writing `open` must be rejected or explicitly isolated in an opted-in navigation rather than silently mixing grammars.

[Security and evidence →](/self-closing-html/security)

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
[^2]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags).
[^3]: WHATWG HTML, [tree construction](https://html.spec.whatwg.org/multipage/parsing.html#tree-construction), [parsing elements that contain only text](https://html.spec.whatwg.org/multipage/parsing.html#parsing-elements-that-contain-only-text), and [foreign-content rules](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign). Inert Chromium comparison recorded 18 October 2026; no event handlers were executed.
[^4]: WHATWG HTML, [trailing solidus on non-void elements](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^5]: WHATWG HTML, [#9491 sanitizer-mismatch example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [concerns about parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^6]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
