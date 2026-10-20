---
title: Security and evidence
order: 2
blurb: text recognition · inactive boundaries · tested results · remaining work
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · security properties
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

**The parsing algorithm must not create executable markup out of characters HTML already treats as text.** The current candidate preserves recognition and protected containment, then changes ordinary output parentage. Its security argument is about that operation itself.

## The problem the algorithm addresses

```html
<style/><img src=x onerror="attack()"></style>
```

Existing HTML reads the apparent image as stylesheet text. Immediately ending style at its slash would create an image with an event handler. The proposed algorithm keeps this text-reading boundary: there is no image element or handler to activate.

A more subtle case changes the namespace of a later style element:

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

Making div empty in the output does not remove its internal recovery entry. The later `</div>` still exits SVG under ordinary HTML rules; the following HTML style reads the apparent image as text.

[Follow both algorithms step by step →](/self-closing-html/parsing#why-remembering-the-element-matters)

## The preservation argument

The output operation takes the HTML parser's existing nodes. It changes containment for eligible elements while preserving:

- Each node's identity, namespace, attributes and text.
- The recognized node order.
- Template-content ownership and foreign-namespace ancestry.
- Explicit interaction-inert ancestry for an element with the HTML inert attribute.

**It never turns a text node's contents into a new tag token.** It also keeps template contents in their inactive document. The tokenizer and recognition stack are not replaced by the output tree.

The existing [Lean projection theorem](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/Projection.lean) proves payload-order and protected-ancestor preservation for this abstract kind of forest transformation. Eligibility and barrier classification are inputs to that theorem. It is not a proof that the JavaScript implements every HTML rule or that arbitrary browser execution is safe.

## Issue checklist

✅ Demonstrated in the stated tests · ⬜ Remaining work. Test passes have the scope stated beside them.

| Issue | Status, mechanism and evidence |
| --- | --- |
| A self-closing change exposes apparent image source as markup. | ✅ Text-reading starts retain ordinary handling. Direct style and textarea cases create no image in reference and browser-adapter tests. |
| An earlier shorthand changes later HTML/SVG recovery. | ✅ Recognition state follows ordinary HTML rules. Live-entry, expired-entry and heading-alias witnesses retain text classification. |
| Template contents become active. | ✅ Template boundaries remain intact. In all three adapter engines, the tested template script/handler stays inactive and its image issues no observed request. An ordinary image handler/request supplies a positive control. |
| Ordinary and formatting elements need broad exclusions. | ✅ Small, links, emphasis, buttons, forms and ordinary wrappers use one projection rule. The simple body-context inventory reports 76 eligible parser-known names, with no empty-pair output differences in those eligible examples. |
| Chunks change recognition or projection. | ✅ Every two-chunk boundary of retained witnesses is checked. The generated corpus checks 120,000 document/fragment cases with both scripting flags and no recorded inventory failure. |
| Scripts see incomplete output or lose their mutations. | ✅ Focused tests exercise a completed output checkpoint before a following script, pause/resume, its parent, later-source visibility and a script-owned child surviving further parsing. This is finite adapter coverage. |
| A DOM adapter activates a template image while constructing it. | ✅ Nodes are created in a document without a browsing context before insertion. Browser request traces include the active positive control and no tested template/attack request. |
| Native execution, form association and declarative shadow-root ownership. | ⬜ Require a native implementation and review of this algorithm. Earlier immediate-closure native results do not transfer. |
| All scheduling, encoding restarts, speculative loading and arbitrary script interleavings. | ⬜ Remain native conformance and security work. |

[Reference implementation, exact tests and recorded results →](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/recognition#readme)

## Reproduce the evidence

From the evidence package with its pinned dependencies:

```bash
node --test recognition/*.test.mjs
node recognition/check.mjs
node recognition/browser-runner.mjs
```

The current records contain 61 focused test passes, 120,000 generated comparisons, and ten targeted cases per adapter engine. The browser runner uses one engine at a time. Its [report](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/browser-results.json) records versions, case results and request controls.

The adapters share parse5 recognition. Chromium, Firefox and WebKit independently provide DOM, script, custom-element and resource behavior; these passes are not native navigation-parser interoperability.

## Limits of the claim

Preserving recognition addresses text-to-markup activation. It does not make all consequences of changed parentage harmless. Application-defined behavior, event propagation, form ownership, CSS and accessibility can depend on ancestry. Native parser associations and declarative shadow-root ownership need explicit integration before shipment.

Untrusted HTML still requires normal application safety measures. A safe parsing API may sanitize its result; that separate operation is not the proof of recognition preservation. Opt-in selection also does not establish the property by itself: the algorithm must maintain it.

::: {.details summary="Earlier algorithms and their evidence"}

The earlier restricted projection preserved recognition but excluded many names and attributes. This candidate broadens its ordinary-element rule, keeps concrete text/inactive/structure boundaries and adds new tests.

The later immediate-closure experiment instead delivered a synthetic end-tag action before reading more source. It broadened syntax support but changed recognition. Its native Ladybird results, safe-parser composition and retained activation counterexample remain [versioned experiment evidence](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme). They do not prove this replacement.

:::

[Parsing rules →](/self-closing-html/parsing)
