# Self-closing HTML: source-authorized placement

**Read source with existing HTML rules; place ordinary `/>` elements as empty elements.** Before exposing output, check that its elements and protected contents are authorized by what the source reader recognized.

The [plain-language parsing rules](https://nextwebwg.org/self-closing-html/parsing) show existing HTML, normal shorthand and the security counterexample side by side. The [issue checklist](https://nextwebwg.org/self-closing-html/security) maps problems to mechanisms, evidence and remaining work.

## Implementation

1. `parser.mjs` retains an ordinary parse5 source tree, tokenizer state, formatting records, form pointer and recovery state. A closing slash does not remove the source-reader entry.
2. `placement.mjs` sends cloned already-tokenized input to a separate tree builder. Eligible starts receive normal opening and closing actions there. It never lexes character-token strings.
3. Planned elements must map to source-reader identities with the same namespace/attributes, each at most once. Written identities use source offsets; implied identities use the causing token's offset. Template ownership, foreign ancestry and actual text/code-owner contents must agree.
4. If ordinary placement fails, try the recognition-based projection: eligible marked elements become empty and their recognized children follow them. Check that output too. If it fails, copy the authoritative source tree. `lastDecision` reports the selected path and rejection reason.
5. `live-dom.mjs` reconciles parser-owned changes with application-owned DOM mutations. It exposes completed output checkpoints before parser-triggered execution. Nodes are created in a document without a browsing context before insertion; pending scripts use their live attributes/text when execution begins.

`parsePlacement()` selects this experimental core explicitly. Navigation/header/profile API integration is not implemented here. `parseRecognition()` retains the first pure-projection candidate as a source-reader/recovery component.

The result may omit source-reader formatting-repair nodes and alter ordinary parentage/order. It must preserve source authorization and protected ownership, not total payload order. Both candidate paths are checked. Recovery code itself cannot authorize different code/text.

## Real-closing-tag boundaries

| Boundary | Reason |
| --- | --- |
| Starts that enter special text-reading states | Ending those states can expose text as markup. The actual tokenizer transition decides the category. |
| Template owners | Contents remain in the inactive content document. Shorthand can operate within it. |
| Form/select | Source reading can suppress a later nested form or select start. Empty-pair placement would otherwise create elements the source reader ignored. |
| Html/head/body/frameset | These own document construction and insertion modes. |

Native void and SVG/MathML acknowledged slash rules retain their handling. Formatting, ordinary wrappers, custom hosts and table rows/cells use the ordinary placement path when the source-authority checks pass. Attributes apply to the resulting DOM; attribute names do not choose a different shorthand rule.

## Current evidence

| Record | What it establishes |
| --- | --- |
| `*.test.mjs` | 88 component and placement tests: recovery, text ownership, streaming splits, forms/select, tables, formatting, script checkpoints/mutations and rejected faulty recovery. |
| `placement-check.mjs`, `placement-results.json` | 120,000 generated comparisons: 10,000 seeded inputs × two scripting flags × six document/fragment contexts. 20,504 checkpoint audits. No recorded failures. `audit-placement.mjs` independently checks source identities, namespaces/attributes, duplicate origins and protected/code contexts. |
| `placement-initial-results.json` | Retained initial failures: reconstructed nodes inside text/code owners. Fixed by keeping those subtrees unchanged in recovery; witnesses remain regression tests. |
| `dx-check.mjs`, `dx-results.json` | 4,000 structured authored examples and 1,000 table examples match explicit empty pairs. The first pure projection differed in 1,777 structured examples. Named boundary examples are checked against their documented ordinary-HTML handling instead. |
| `browser-runner.mjs`, `browser-results.json` | 16 cases per engine: Chromium 156.0.8078.4, Firefox 157.0 and WebKit 26.5. Shared source reader; native DOM/script/resource/layout behavior. Tested text/template attacks stay inactive; only the positive resource control is requested. Also exercises native table geometry/APIs, same-name wrappers, formatting, LF and live script/mutation behavior. |
| `Placement.lean`, `placement-proof-results.json`, `placement-proof.log` | Five compiled abstract theorems about source-receipt authorization and unique output identities. Lean 4.35.0; source/compiler hashes recorded. Unique output identities assume unique source identities. Not a JavaScript/HTML/native refinement proof. |
| `check.mjs`, `results.json`, `parser.test.mjs` | First-candidate recognition/projection component coverage retained separately. Its inventory counts and payload-order theorem are not proof of the current normal placement path. |

The pinned parse5 8.0.1 source reader predates the current customizable-select parsing rules. Its image-suppression tests describe that reader; the nested-select start witness also follows the current HTML rule. Updating the source reader and comparing against native recognition remain required.

These are finite results against shared parse5 reading, not universal browser security or native navigation-parser interoperability. A source-recognized handler is not removed by this parser.

## Proof in plain language

An abstract source receipt records an element's identity, payload (namespace/attributes), protected ancestor identities and owned code/text. A proposed output is accepted only when its receipts occur in the source and its identities do not repeat. The same test applies to recovery. Source receipts are the final choice.

`Placement.lean` proves the selection rule always returns authorized receipts. `check_sound`, `choose_authorized`, `choose_unique`, `receipt_from_source` and `selected_receipt_from_source` compiled without warnings or unfinished proofs; reported axioms contain only `propext`. This proves the abstract rule, not the receipt extraction or JavaScript implementation. The older `../Projection.lean` concerns the component forest projection only.

## Reproduce

From `self-closing-html/evidence`, with its pinned dependencies:

```bash
npm ci --ignore-scripts --no-audit --no-fund
node --test recognition/*.test.mjs
node recognition/placement-check.mjs
node recognition/dx-check.mjs
node recognition/browser-runner.mjs
lean recognition/Placement.lean
```

The proof command requires the recorded Lean version. CI reruns JavaScript tests, generated audits and authored comparisons; it does not currently rerun Lean or the three browser engines. Browser executable overrides are `CHROMIUM_EXECUTABLE`, `FIREFOX_EXECUTABLE` and `WEBKIT_EXECUTABLE`. The runner uses one engine at a time and closes its browsers/server.

## Remaining integration

Native form association, declarative shadow-root ownership, modules/scheduling, encoding restarts, speculative loading and arbitrary parser/script interleavings need native implementation and review. Legacy document writing needs rejection/isolation or a defined integration with both states. Full-tree snapshots and checking are a correctness prototype, not a demonstrated production cost. Changed ancestry can affect application code, events, CSS and accessibility.

The older native patches implement other algorithms. Their counts must not be attributed to this one.
