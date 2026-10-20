---
title: Parsing rules
order: 1
blurb: opt-in · closure · recovery · insertion APIs
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · proposed rules
status: "Unofficial Editor's Draft · Stage 0"
---

# Parsing rules

**For an HTML element, `/>` finishes its opening tag and immediately processes its closing tag, before the parser reads more source.** There is no blacklist of formatting, control, or table elements.

```html
<small />
<button />
<table />
<select />
<script src="app.js" />
<p>Following content</p>
```

The same HTML recovery rules apply as for explicit opening/closing pairs. Attributes do not select a different parsing rule.

## Select the grammar

Request `self-closing` through [HTML Feature Profiles](/html-feature-profiles/):

```html
<!DOCTYPE html PUBLIC "self-closing">
```

The shared proposal also defines the HTTP response header, the `next` family opt-in, and explicit parsing options. Plain HTML and existing string-parsing APIs keep their current behavior unless they explicitly select the new grammar. A later doctype mutation cannot switch a running parser.

## One operation, with existing HTML behavior

| Input | Processing |
| --- | --- |
| `<small />` | Process `<small>`, then an end-tag token for `small`. |
| `<script />` | Process the script start and end before reading following source. It does not swallow the rest of the page. |
| `<textarea />` | Finish the element before reading more source; following source is ordinary markup. |
| `<img />` | Existing void-element behavior; do not invent `</img>`. |
| `<svg><path /></svg>` | Existing foreign-content self-closing behavior. |

HTML's void elements remain `area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, and `wbr`. Obsolete elements retain their existing parser behavior.

This shorthand does not override HTML recovery. A tag ignored in an invalid context remains subject to those rules. Document roots still follow HTML's document structure; `<html />` cannot create siblings outside the document root. `plaintext` closes at the token boundary; a literal legacy `</plaintext>` is not an equivalent source spelling because legacy plaintext consumes it as text.

### Preserve normal attribute parsing

The slash must be a self-closing marker, not part of an unquoted value:

```html
<div data-path=assets/ /> <!-- Self-closing; value is assets/ -->
<div data-path=assets/>  <!-- Not self-closing; value is assets/ -->
```

Quoted strings, comments, and text already inside a script or stylesheet are not searched and rewritten for slash syntax.

::: {.details summary="Implementation contract: token processing and checkpoints"}

When an HTML start-tag token carries the self-closing flag, process its ordinary start-tag action once, then process the matching end-tag token in the resulting parser state. Reprocessing the start through insertion modes must not duplicate the synthetic end tag. Existing void handling and native foreign-element handling remain intact, including transitions back into HTML processing.

Complete the synthetic end and restore the appropriate source-tokenizer state before consuming more characters. Clear a pending initial-newline suppression when that text element has already ended. HTML formatting recovery, form state, table placement, template insertion modes, and namespace transitions use the resulting state rather than a separate legacy recognition tree.

Before running a parser-triggered script or delivering a callback, expose the DOM for completed processing. A self-closing external script keeps the normal blocking/async/defer/module rules; the slash does not make it inert. Preserve script mutations and normal pause/resume behavior. Declarative shadow-root host selection follows ordinary HTML placement; do not attach a following declaration to an already closed host.

The reference implementation is in [closure/parser.mjs](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/closure/parser.mjs). Its scope and browser-adapter limits are in the [current evidence](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme).

:::

## Parse and sanitize using the same grammar

Self-closing syntax changes parsing. **A string sanitized for legacy HTML is not automatically safe when reparsed under this grammar.** Parse with the intended grammar, sanitize that resulting tree, and insert the sanitized nodes without a string round trip.

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
