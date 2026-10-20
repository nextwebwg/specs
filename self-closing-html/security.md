---
title: Security and evidence
order: 2
blurb: sanitizer mismatch · worked solution · experiments · implementation requirements
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · security contract
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

**Self-closing syntax is not sanitization.** Trusted source can use the selected grammar directly. Untrusted HTML must be parsed and sanitized using that grammar before its nodes are inserted.

The parser processes a real closing-tag action at each self-closing marker. Formatting, controls, tables, and text elements use the same rule. The security requirement is to filter the document that this grammar actually produces.

## Issue checklist

✅ Demonstrated in the stated tests · 🟡 Partial · ⬜ Remaining work. Passing finite tests is not a universal safety guarantee.

- ✅ **Ordinary tags can use the same rule.** Parser-known names are checked against immediate empty pairs in ten contexts with scripting enabled and disabled. `plaintext` has a separate token-boundary check.
- ✅ **Attributes do not select a different algorithm.** Hidden, inert, and popover examples close normally. Visibility differences are not counted as vulnerabilities.
- ✅ **Following markup is parsed in the updated context.** Formatting, select, table, template, and text-element tests no longer depend on retaining the old open-element context.
- ✅ **Chunking preserves the tested result.** 30,000 seeded comparisons and every two-chunk boundary of selected witnesses pass.
- ✅ **The safe reference path sanitizes the selected-grammar tree.** It filters the actual nodes in place and returns nodes; 1,000 generated inputs retain none of the monitored script/handler/JavaScript-URL signals.
- ✅ **Adapter execution checkpoints have browser evidence.** 34 cases pass in each of Chromium, Firefox, and WebKit, including callbacks, mutations, external-script blocking, streamed input, and direct safe node insertion. They share a parse5 parser and do not establish native support in those engines.
- ✅ **The native experiment has separate results.** A patched Ladybird build passes 50 execution checks, 810 document comparisons, six encoding cases, and 16 existing parser regressions. A focused garbage-collection-on-every-allocation run also completes without failure. These are finite checks in one experimental engine, not a memory-safety proof.
- ⬜ **Production review and interoperability remain required.** No browser-vendor endorsement or universal security proof is reported.

[Current implementation and reproducible evidence →](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme)

## Why a legacy sanitizer is not enough

A concrete test uses a custom `sanitize-html` configuration permitting `style` and foreign structure, while disallowing event-handler attributes. It retains handler-looking source as text. Under the new grammar, an immediate close can expose that text as an image with an `onerror` handler.

Ordinary HTML produces no image or handler execution for the reduced sanitized source. The unsafe immediate-closure output produces one in Chromium, Firefox, and WebKit. This is evidence for that custom-policy mismatch, not a vulnerability claim against sanitizer defaults.

::: {.details summary="Reduced counterexample and observation method"}

The legacy-sanitized string is:

```html
<svg><mtext><style><table/><style/><img data-probe src=x onerror="probe()"></style></mtext></svg>
```

The unsafe new parser changes a boundary that kept the apparent image as text. Simply moving the same legacy sanitizer before that parser does not protect it.

The browser experiment compares ordinary source parsing with serialized experimental outputs in opaque sandbox frames. A controlled `probe()` handler records execution, image network access is blocked by CSP, and a positive control confirms the signal works. These are executions of candidate output, not a native implementation of the new grammar. The tested default sanitizer policies did not activate the new syntax, so their zero-difference results are not evidence of broad compatibility.

:::

## Parse first, sanitize the resulting nodes

The safe reference path does this:

1. Parse with the caller-selected grammar in an inert representation.
2. Construct an inert DOM and filter those same nodes with DOMPurify in place.
3. Return the sanitized document. Insert its nodes directly, without serializing and reparsing.

In the retained counterexample, this path removes the handler from the new grammar's image node before insertion. The reference uses DOMPurify's policy; it is not the native Sanitizer API and does not establish safety for arbitrary application-defined components, CSS policies, or URL policies.

Existing parsing APIs keep their legacy grammar unless they explicitly request another. The proposed safe `Document.parseHTML()` extension must apply its mandatory sanitization under the selected grammar. The unsafe variant is not a sanitizer. [HTML Feature Profiles](/html-feature-profiles/#explicit-parsing) owns that API contract.

::: {.details summary="Earlier experiments and their limits"}

Earlier experiments rearranged a legacy tree and proved properties of that rearrangement. Their Lean proof and native results remain [historical evidence](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme). They do not establish correctness of the current start-and-close algorithm. The [earlier analysis](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/closure/earlier-security-analysis.md) is preserved alongside those records.

:::

## Remaining work before browser shipment

Implementer security review, native integration of the proposed profile header and API options, broader engine conformance, arbitrary encoding restarts, and optimized look-ahead loading remain shipment work. The experiment disables the optional speculative scanner and tests recognized resource loading. Six fixed encoding cases and a completed focused memory-stress test do not establish every restart or memory behavior.

[Parsing rules →](/self-closing-html/parsing)

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [Simon Pieters: sanitizer mismatch and the style example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790), and [Keith Cirkel: updating libraries does not protect existing installations](https://github.com/whatwg/html/issues/9491#issuecomment-1623794848).
[^2]: WHATWG HTML, [Henri Sivonen: parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^3]: WHATWG HTML, [#721: existing self-closing-looking markup](https://github.com/whatwg/html/issues/721#issuecomment-186914414), and [existing hyphenated names](https://github.com/whatwg/html/issues/721#issuecomment-187737022).
[^4]: Mozilla, [CVE-2020-6802: Bleach mutation XSS in noscript handling](https://bugzilla.mozilla.org/show_bug.cgi?id=1615315).
[^5]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
