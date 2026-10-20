# Recognition-preserving self-closing parser

This candidate keeps HTML's existing recognition and recovery state, then changes output containment for eligible marked elements. It addresses the parser-created text-to-markup problem directly. It does not use a sanitizer to obtain that property.

## The algorithm

1. Feed each source token to the ordinary HTML parser without synthesizing an end tag or changing tokenizer state.
2. If an unacknowledged self-closing marker creates an eligible HTML element, mark that element for empty output. HTML's existing void and foreign-content handling remains in charge of markers it already acknowledges.
3. Keep the recognition element, stack entries, formatting records, form pointer and insertion modes under ordinary HTML recovery rules. Later real closing tags act on that state.
4. At a completed token checkpoint, project the recognition tree into output: retain each marked element, make it empty, and place its recognized children immediately after it. Apply this recursively. Preserve node identity, namespaces, attributes, text, order, template-content ownership and protected ancestry.
5. Apply only parser-owned output changes to the live DOM. Do not overwrite script mutations. Expose the completed output before a parser script runs; pause and resume recognition around that execution.

Formatting reconstruction carries a marked start token's provenance to its reconstructed elements; their output is empty too.

`parseRecognition()` explicitly invokes the candidate core; this package does not yet integrate navigation doctype/header resolution. `parser.mjs` is the incremental reference. Its actual tokenizer-state check protects text-reading starts. `live-dom.mjs` reuses the prior mutation-preserving delta reconciler and constructs nodes in a document without a browsing context, before placing them in the live output. Template descendants consequently are not created as active images first.

## Boundaries that keep their ordinary closing behavior

| Group | Reason |
| --- | --- |
| Starts that select a non-data tokenizer state, including HTML script/style/textarea | Ending that state early can turn previously recognized text into markup. Classification uses the actual parser transition, including scripting state and namespace. |
| Template elements and their content documents | Their children must not be projected into the active document. |
| Document structure: html, head, body, frameset | These are parser/document scaffolding, rather than ordinary empty output wrappers. |
| Dedicated table/select child-placement containers: table, caption, colgroup, tbody, thead, tfoot, tr, td, th, select | Their child-placement rules cannot be treated as ordinary sibling insertion. Early experiments retained recognition but produced surprising table order and select behavior. |
| An element bearing the HTML inert attribute | Preserve its descendants' explicit interaction-inert ancestry. This is a separate interaction constraint; inert does not itself disable scripts. |

Attributes such as hidden, disabled and popover do not determine eligibility. Formatting elements, including small, b, a and em, use the same output-projection rule as ordinary divs and custom-element hosts. No custom-element registration or future-token intent guess selects the rule.

## Evidence

- `parser.test.mjs` and `live-dom.test.mjs`: 61 tests. Identity, text and protected ancestry are checked at token checkpoints; every two-chunk boundary of retained witnesses is compared. Other cases cover script pause/resume, template ownership, formatting, source attributes and script-owned DOM mutations.
- `check.mjs` / `results.json`: 120,000 comparisons from 10,000 seeded inputs, both scripting flags and six document/fragment contexts. Zero recorded recognition or projection-inventory failures. This is finite coverage against the shared parse5 recognizer.
- The simple body-context authoring inventory reports 76 eligible parser-known names. Its eligible examples match the corresponding empty-pair output. This is not a percentage of all HTML, or a claim of pair equivalence in every recovery context.
- `browser-runner.mjs` / `browser-results.json`: ten cases per engine in Chromium, Firefox and WebKit. Direct and namespace text cases create no image; template scripts stay inactive and template images issue no observed request. An ordinary image request and handler supply the positive control. Other cases cover a script's projected parent/checkpoint, mutations and a custom-element callback. Engines supply native DOM/execution/resource behavior, but share parse5 recognition through the adapter.
- The existing [Projection.lean](../Projection.lean) proves payload-order and protected-ancestor preservation for the abstract forest projection operation. This candidate uses that same form of transformation. The theorem is not a machine-checked refinement of this JavaScript, its eligibility rules, HTML tokenization or browser scheduling.

## What this establishes, and what it does not

The construction does not create elements out of recognized text. Its output consists of the recognizer's nodes, with the same data and protected ancestry. In particular, a later closing tag can still cause ordinary HTML/SVG recovery even when the element has already been made empty in the output.

Output containment is intentionally different. This does not make arbitrary application code, CSS effects, form ownership, accessibility or event propagation equivalent to ordinary HTML. Formatting repair can produce output different from literal start/end source expansion. The algorithm is a containment rule, not that source expansion.

A production implementation still needs native integration and conformance review: live form association, declarative shadow roots and their ownership, modules and native scheduling, encoding restarts, speculative loading and arbitrary parser/script interleavings. The prior immediate-closure Ladybird patch does not implement or prove this replacement. Browser-adapter passes must not be described as native navigation-parser support.

## Reproduce

From `self-closing-html/evidence`, using the pinned dependencies:

```bash
npm ci --ignore-scripts --no-audit --no-fund
node --test recognition/*.test.mjs
node recognition/check.mjs
node recognition/browser-runner.mjs
```

The browser runner needs compatible Playwright browser installations. `CHROMIUM_EXECUTABLE`, `FIREFOX_EXECUTABLE` and `WEBKIT_EXECUTABLE` can select existing local installations. It uses one engine at a time and closes each browser and the local server on completion.
