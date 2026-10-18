---
title: Security and evidence
order: 2
blurb: sanitizer mismatch · worked solution · experiments · implementation requirements
sectionNav: true
eyebrow: HTML Next Parsing · security contract
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

Preserve HTML's text, namespace, and containment boundaries while making eligible elements empty.

## The mismatch to prevent

A sanitizer and a browser must agree about which input is text and which input creates elements. WHATWG's self-closing discussion illustrates the problem with this source:[^1]

```html
<style/><img src onerror=alert(1)><style></style>
```

Today's HTML parser ignores the slash on `style`. The apparent image is style text. A parser that simply expands `<style/>` to `<style></style>` instead creates an image with an event handler.

**The first rule is to exempt text-mode elements.** Under this proposal, `style` retains its existing slash handling, so this source creates no image. That also explains the exemptions for `script`, `textarea`, and the other text-sensitive names in the [eligibility table](/html-parsing/parsing#preserve-sensitive-elements).

Parsing must also use the same scripting state. A disagreement about how to parse `noscript` caused the Bleach mutation-XSS vulnerability.[^2]

## Recover at namespace boundaries

Exempting text-mode names alone is insufficient: an earlier ordinary element can change how later markup is interpreted.

```html
<div/><svg></div><style><img data-probe></style></svg>
```

If `<div/>` is naively expanded into a pair, the div has already closed when the parser reaches SVG. The later `</div>` cannot close that earlier div. The parser stays in SVG, where `style` does not provide HTML's raw-text boundary, and the apparent image becomes an element.

**The second rule is to preserve recovery context after DOM containment closes.** The proposed parser handles the same source as follows:

1. `<div/>` creates an empty div in the DOM and retains the div's recognition record.
2. `<svg>` enters foreign-content parsing using ordinary HTML rules.
3. `</div>` closes the retained div record and the intervening SVG context, as ordinary HTML recovery would.
4. `style` is interpreted as HTML style text. No image node appears.

| Interpretation | Image nodes |
| --- | --- |
| Existing HTML | 0 |
| Naive start/end expansion | 1 |
| Proposed recognition-preserving model | 0 |

> [!ex] Close containment without erasing context
> The DOM gets an empty element. The parser retains the scope information needed to keep later text as text.

This is why the proposal specifies complete recovery state. A global list of previously closed names becomes stale when an ancestor closes; exact-name matching also misses heading aliases. Those simpler repairs are recorded with counterexamples in the [evidence directory](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence).

## Preserve protected containment

Preserving recognized text is necessary, but containment can affect whether an existing node becomes active or visible.

Closed dialogs, disclosure widgets, and media fallback containers are exempt. Active-browser checks found that lifting their children could expose hidden controls. Elements carrying `inert`, `hidden`, or `disabled`, template content, and foreign contexts retain their protected boundaries too.

Shadow roots keep their recognized host. A root is an ownership relationship, not a light-DOM child to move after an empty host. The browser checks preserve that edge while allowing the host's light DOM to become empty.

Parentage intentionally changes elsewhere. Application-defined components and script gadgets require their own policy; a sanitizer must not authorize hazardous content solely because an ordinary ancestor currently hides or intercepts it.[^3]

## Why recognized text cannot become markup

The static reference separates recognition from containment:

- `R(s,c)` recognizes source `s` using ordinary HTML in the exact starting context `c`.
- `P` makes eligible elements empty and moves their recognized children to following siblings within the same root.
- The resulting tree is `P(R(s,c))`.

`P` does not tokenize strings, create elements, or change namespaces, attributes, or text. It preserves node identities and preorder. Protected containers remain in the ancestor chain. Text recognized by `R` therefore cannot become newly recognized executable markup through `P`.

This addresses the text-to-markup mismatch raised in the WHATWG discussion. It is a property of the static reference function. Native execution must preserve the same boundaries at script, reaction, and mutation checkpoints.

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

| File | Purpose |
| --- | --- |
| `projection-candidate.mjs` | Static reference and generated recognition comparisons. |
| `sugar-check.mjs` | Ordinary authoring comparisons. |
| `recovery-browser.html` | Inert Chromium comparisons; marker attributes stand in for source metadata. |
| `roundtrip-check.mjs` | Serialization/reparsing comparisons. |
| `active-build.mjs` / `active-browser.html` | 32 sandboxed observations, including script mutation, custom-element reactions, and an unsupported serialization case. |
| `shadow-browser.html` | Six inert native open-root ownership comparisons. |
| `matrix.mjs` | Representative sanitizer configurations and earlier expansion variants. |

Finite tests check implementation behavior; they do not prove all inputs safe. The model uses parse5 8.0.1, whose select behavior differs from current Chromium. It does not execute source scripts or implement a native navigation parser. Chromium probes cover the recorded cases, not an independent implementation of the complete profile.

The model's serializer also fails to preserve declarative shadow-root ownership when its output is reparsed. That failure is recorded explicitly: the serializer is not a conforming lowering tool. The separate native-root experiment checks projection with root ownership preserved.

## Requirements before browser shipment

A native implementation must construct the specified DOM incrementally and preserve its boundaries at script and custom-element reaction checkpoints. Rewriting an already active page after parsing does not implement this contract.

Define parser pauses and encoding restarts, speculative loading, script-driven mutations, and document-writing isolation before shipment. Implement and verify shadow-root ownership under native execution. The [component-placement extension](/html-parsing/#placement-extension) changes recognition itself and requires a separate safety argument.

> [!warn] Implementation status
> The static reference establishes text-to-markup preservation. Full native streaming and execution safety remain unverified. Browser implementation, Web Platform Tests, and implementer security review are required before shipment.

Editor: [Matthew Dean](https://github.com/matthew-dean). Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [#9491 sanitizer-mismatch example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [concerns about parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^2]: Mozilla, [CVE-2020-6802: Bleach mutation XSS in noscript handling](https://bugzilla.mozilla.org/show_bug.cgi?id=1615315).
[^3]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
