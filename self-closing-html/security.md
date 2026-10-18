---
title: Security and evidence
order: 2
blurb: sanitizer mismatch · worked solution · experiments · implementation requirements
sectionNav: true
eyebrow: HTML Next Parsing · security contract
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

The reported text-to-markup exploit is blocked by the static reference design. The key change is to DOM containment: existing HTML still decides what is text and what is an element.

## Two objections, two rules

The 2023 WHATWG proposal already suggested a document opt-in. The objections concern what happens after opting in: old sanitizers can disagree with the parser, and a document flag can silently change a library's parsing behavior.[^1][^2]

| Objection | Proposed answer |
| --- | --- |
| A sanitizer approves text that the browser exposes as executable markup. | Preserve HTML's recognition of text and namespaces. Change only eligible containment edges. The static construction blocks this text-to-markup mechanism. |
| A library receives a different parsing grammar without requesting it. | Apply the doctype to document source only. Existing insertion APIs keep their grammar; dynamic Next parsing requires an explicit request. |

The earlier #721 discussion also raises compatibility with existing authored markup, including names containing hyphens.[^3] Plain HTML keeps its meaning. Only the explicit Next declaration selects the new document profile; custom-element registration cannot change that profile. Unsupported browsers still need a correct fallback.

> [!ex] What is resolved, and at what level?
> The reported text-to-markup mechanism is eliminated by the reference construction. The distant-mode-switch problem is excluded by the proposed API contract. A native browser implementation must still demonstrate that it obeys both rules during execution.

## Block the direct style exploit

This is the sanitizer-mismatch example from the thread:[^1]

```html
<style/><img src onerror=alert(1)><style></style>
```

Ordinary HTML ignores the slash on `style` and enters raw-text tokenization. The apparent image is character data inside the stylesheet. Expanding `<style/>` into `<style></style>` would instead leave that text container and expose an image with an event handler.

**The proposal keeps `style` exempt from self-closing.** The slash therefore cannot end its text container. The tokenizer consumes the apparent image as text, so there is no image element to load and no `onerror` handler to attach.

The same rule covers `script`, `textarea`, and the other text-sensitive names in the [eligibility table](/html-parsing/parsing#preserve-sensitive-elements). Parsing must also use the same scripting state: disagreement about `noscript` caused the Bleach mutation-XSS vulnerability.[^4]

## Recover at namespace boundaries

Exempting `style` alone does not protect a later style element whose namespace changes because of an earlier shorthand. This example shows the remaining problem:

```html
<div/><svg></div><style><img data-probe></style></svg>
```

### What naive expansion gets wrong

Expanding the first token to `<div></div>` removes the div from the parser's open-element stack before SVG begins. At the later `</div>`, the stack contains `body → svg`, with no div to close. The parser stays in SVG.

SVG `style` does not select HTML's raw-text tokenization. The apparent image is then parsed as markup. Exempting `style` from self-closing cannot fix this case: this style start tag has no slash.

### What the proposal retains

The proposal keeps two distinct things: **a recognition stack that follows ordinary HTML rules**, and **an output DOM in which eligible shorthand elements are empty**.

After `<div/>`, the div is empty in the output DOM, but its entry remains on the recognition stack. That entry still identifies the same div and its HTML namespace, and participates in ordinary scope checks. Following recognized children go after the empty div in the output; they do not determine the recognition stack.

The required trace is below. The leading `html` entry is omitted for readability.

| Input consumed | Recognition stack | Output DOM containment |
| --- | --- | --- |
| `<div/>` | `body → div` | Empty div under body. |
| `<svg>` | `body → div → svg` | SVG follows the empty div as a sibling. |
| `</div>` | `body` | The elements remain siblings; recognition has exited both SVG and div. |
| `<style>` | `body → style` | HTML style element under body; its contents use raw-text tokenization. |

At `</div>`, ordinary HTML recovery can still find the retained div in scope. It pops the intervening SVG entry and then the div entry. The next `style` is therefore an HTML element, not an SVG element.

**That is the security-relevant difference:** the tokenizer enters HTML raw-text mode before reaching `<img data-probe>`. Those characters never become an image start-tag token.

| Interpretation | Image nodes |
| --- | --- |
| Existing HTML | 0 |
| Naive start/end expansion | 1 |
| Proposed recognition-preserving model | 0 |

### When retained entries disappear

The stack follows ordinary HTML recovery throughout the parse. Entries expire when those rules pop them, including when an ancestor closes. Ignored start tags create no entry. Heading aliases, formatting state, form state, and namespace transitions retain their existing handling.

This is more than remembering a tag name. A permanent list of previously self-closed names can treat an expired entry as live and exit SVG at the wrong time. The [recorded counterexamples](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence) show that failure.

## Keep a library's parsing contract stable

The second security objection concerns a mode switch outside the code that parses an HTML string.[^2] A library calling `innerHTML` must not acquire different tokenization because its caller changed the page's doctype.

Under the proposed contract, the same string inserted through an existing HTML API uses that API's existing grammar in either document profile. `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `DOMParser`, fragment parsing, `Document.parseHTML*`, and `iframe.srcdoc` do not inherit Next from the document.

Dynamic Next parsing requires an explicit request at the parsing call. Parse and sanitize together in the actual destination context, then insert nodes directly. A doctype inside the string cannot enable Next. The [insertion rules](/html-parsing/parsing#keep-existing-insertion-apis-stable) also require rejection or isolation of document writing, rather than feeding legacy string writes into the new document grammar.

## Preserve protected containment

Preserving recognized text is necessary, but containment can affect whether an existing node becomes active or visible.

Closed dialogs, disclosure widgets, and media fallback containers are exempt. Active-browser checks found that lifting their children could expose hidden controls. Elements carrying `inert`, `hidden`, or `disabled`, template content, and foreign contexts retain their protected boundaries too.

Shadow roots keep their recognized host. A root is an ownership relationship, not a light-DOM child to move after an empty host. The browser checks preserve that edge while allowing the host's light DOM to become empty.

Parentage intentionally changes elsewhere. Application-defined components and script gadgets require their own policy; a sanitizer must not authorize hazardous content solely because an ordinary ancestor currently hides or intercepts it.[^5]

## Why recognized text cannot become markup

The static reference first recognizes ordinary HTML in the exact starting context and scripting state. It then receives a tree of already recognized nodes and changes permitted containment relationships.

That containment step receives **nodes, not HTML strings**. It does not tokenize text again, create elements, or change namespaces, attributes, or text. It preserves node identities and preorder. Protected containers remain in the ancestor chain.

Text that the recognition step classified as stylesheet content therefore stays text. There is no operation in the containment step that could turn it into an image or attach an event-handler attribute. This is the construction argument behind the reported exploit's prevention; the experiments check the implementation against it.

The prototype computes the ordinary recognized tree first, then applies containment changes. A native browser must maintain equivalent recognition state independently of output parenting and produce the specified DOM incrementally. Script, custom-element reaction, and mutation checkpoints still require native implementation and verification.

## What the experiments establish

The experiments test the reference construction and expose boundaries that a browser implementation must preserve.

| Check | Recorded result |
| --- | --- |
| Generated parsing cases | 800,000 comparisons preserved the checked recognition properties. |
| Ordinary authoring examples | 40 comparisons matched explicit pairs or the specified exemption. |
| Chromium probes | 12 inert comparisons preserved the checked node properties, including the reported text/namespace cases. |
| Serialization and reparsing | 200,000 comparisons found no new marker exposure against the legacy baseline. |
| Native containment | Sandboxed comparisons identified the native-container exemptions. |
| Shadow-root ownership | Six inert native open-root comparisons preserved root ownership and the checked containment properties. |

The [evidence README](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme) provides pinned dependencies, commands, seeds, results, and limitations.

The prototype uses parse5 8.0.1, including its older select behavior. It does not execute source scripts or implement native navigation parsing. Chromium probes cover the recorded cases, not a complete independent Next parser.

Its serializer also fails the recorded declarative shadow-root ownership case; it is not a conforming lowering tool. The separate native-root checks preserve ownership. Finite passing comparisons establish coverage, not universal browser safety.

## Requirements before browser shipment

A native implementation must construct the specified DOM incrementally and preserve its boundaries at script and custom-element reaction checkpoints. Rewriting an already active page after parsing does not implement this contract.

Define parser pauses and encoding restarts, speculative loading, script-driven mutations, and document-writing isolation before shipment. Implement and verify shadow-root ownership under native execution. The [component-placement extension](/html-parsing/#placement-extension) changes recognition itself and requires a separate safety argument.

> [!warn] Implementation status
> The static reference establishes text-to-markup preservation. Full native streaming and execution safety remain unverified. Browser implementation, Web Platform Tests, and implementer security review are required before shipment.

Editor: [Matthew Dean](https://github.com/matthew-dean). Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [Simon Pieters: sanitizer mismatch and the style example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790), and [Keith Cirkel: updating libraries does not protect existing installations](https://github.com/whatwg/html/issues/9491#issuecomment-1623794848).
[^2]: WHATWG HTML, [Henri Sivonen: parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^3]: WHATWG HTML, [#721: existing self-closing-looking markup](https://github.com/whatwg/html/issues/721#issuecomment-186914414), and [existing hyphenated names](https://github.com/whatwg/html/issues/721#issuecomment-187737022).
[^4]: Mozilla, [CVE-2020-6802: Bleach mutation XSS in noscript handling](https://bugzilla.mozilla.org/show_bug.cgi?id=1615315).
[^5]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
