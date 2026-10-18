# HTML Next Parsing: reproducible evidence

The reference model preserves ordinary HTML recognition, then changes eligible containment edges. An empty element remains in the tree; its recognized children become following siblings. These experiments check that construction and identify boundaries a native implementation must preserve. Recorded 18 October 2026 in a Chromium-based Brave browser and Node 22.23.3.

## What the evidence establishes

| Check | Recorded result | Scope |
| --- | --- | --- |
| `projection-candidate.mjs` | 800,000 comparisons; no checked recognition changes | Node identity, preorder, namespaces, attributes, text, template membership, designated container ancestry |
| `sugar-check.mjs` | 40 matches | Explicit-pair counterparts or unchanged handling for exempt tokens |
| `recovery-browser.html` | 12 matches | Inert native Chromium recognition and containment projection |
| `roundtrip-check.mjs` | 200,000 comparisons; no new marker exposure or classification changes | Legacy serialize/reparse baseline versus projected serialize/reparse |
| `active-browser.html` | 32 sandboxed observations | Text/namespace cases, native containment exemptions, script mutation, custom-element reactions, and a known unsupported shadow-root lowering |
| `shadow-browser.html` | Six matches | Inert native recognition preserves open-root identity, ownership, and protected-root membership |

The structural argument is separate from these finite tests: projection does not tokenize strings, create elements, or change namespaces, attributes, or text. Exempt containers remain in the ancestor chain. Thus text recognized by the reference parser cannot become newly recognized markup through projection. This proves that property of the static function, not complete browser execution safety.

Calling the reference function selects the experimental profile. It does not implement native browser doctype handling, streaming, or script checkpoints. Existing HTML insertion APIs retain their grammar in the proposal.

## Reproduce

Use a Node version accepted by `package.json`. In this directory:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run projection
npm run sugar
npm run roundtrip
npm run active:build
node active-build.mjs --without-native-exemptions
python3 -m http.server 4174 --bind 127.0.0.1
```

Open these local pages in a browser:

- `http://127.0.0.1:4174/recovery-browser.html`
- `http://127.0.0.1:4174/shadow-browser.html`
- `http://127.0.0.1:4174/active-browser.html`
- `http://127.0.0.1:4174/active-unprotected-browser.html`

The active pages run sequential sandboxed, opaque-origin frames with scripts enabled. They use harmless local signals and data URLs, without fetching external resources. Keep the page open until its status says `COMPLETE`; the JSON below it is the recorded result format. The shadow and recovery pages never insert parsed content into their active document. Stop the local server after inspection.

Commands overwrite the corresponding generated HTML or JSON in this directory. Run sequentially. Dependencies are pinned in `package-lock.json`; these experiments add no site runtime dependencies.

## Recognition and recovery

`projection-candidate.mjs` uses parse5 8.0.1 for ordinary HTML recognition and complete recovery state. Projection then changes only selected output edges. Protected names and attributes are explicit in its eligibility check. HTML special elements are also exempt while an active formatting scope is present, because formatting reconstruction can otherwise spoil the promised shorthand result.

Seed `0x50524f4a` generates 100,000 token sequences × four contexts (`document`, `div`, `table`, `template`) × two scripting states = 800,000 comparisons. `projection-results.json` records the corpus parameters, activations, examples, failures, and limits. The recognition signature includes designated container ancestor identities; matching text alone would miss an escape from an inert container.

`sugar-check.mjs` checks four element names across ten wrappers. `sugar-results.json` records all 40 comparisons. Ordinary div/custom-element examples produce empty following siblings; exempt cases retain ordinary handling. This is bounded authoring coverage, not complete equivalence with expanded HTML on malformed inputs.

`recovery-browser.html` uses marker attributes as a substitute for source-token metadata. Its 12 native Chromium comparisons include the raw-text/namespace witnesses, heading aliases, expired recovery records, templates, and explicit inert containment. `recovery-chromium-results.json` records them. It is an independent native recognition check for those cases, not an independent complete Next parser.

## Native containment and execution checkpoints

`active-build.mjs` generates `active-browser.html` from the current model. The page compares 16 original document sources with their serialized projections. `active-chromium-results.json` records the resulting 32 observations.

A positive control produces an actual image-error signal, verifying that the sandbox can run the monitored handler. Six cases check controls inside `details`, `dialog`, `datalist`, `audio`, `video`, and `canvas`. With those containers exempt, visibility and focus observations match their legacy counterparts. `active-unprotected-browser.html` repeats the test with the native-container exemptions removed; `active-unprotected-chromium-results.json` records those 32 observations. All six previously hidden controls become visible. Five also become the active focus target; the canvas fallback control was already programmatically focusable. These results justify preserving native containment. They are not six demonstrated sanitizer bypasses. Event-handler signal counts alone missed these changes, so the fixtures also record visibility and the active focus target.

The script-mutation case observes an empty div, a following script running under `BODY`, an explicitly appended child retained in that div, and a following span under `BODY`. The custom-element case observes the connected callback under the intended output parent. Those are useful execution fixtures for a future native parser, but serialization followed by ordinary navigation cannot validate native parser checkpoints or arbitrary mutation interleavings.

### Shadow roots: preserve ownership, not serialized templates

The active shadow case deliberately exposes an unsupported lowering: parse5 does not construct a declarative shadow root. Moving its template carrier to the body and reparsing attaches the root to `BODY` rather than the authored host. This is a recorded failure, not a passing security result. The model's serializer is not a conforming Next-to-HTML lowering tool.

The proposed native rule instead selects the declarative host using retained recognition state and preserves the host/root edge. Only light-DOM containment changes. `shadow-browser.html` starts with native `Document.parseHTMLUnsafe`, which recognizes open declarative roots in an inert document, then projects light-DOM edges without moving roots. Six cases preserve root identity and host ownership, including nested shorthand, an inert template inside a root, a hidden host, and foreign ancestry. `shadow-chromium-results.json` records the passing checks.

This open-root check does not establish closed-root handling, scoped-registry behavior, script-driven root changes, constructor timing, or streaming integration. Those require native conformance cases.

## Serialization and reparsing

`roundtrip-check.mjs` uses seed `0x52545250`: 20,000 inputs × five contexts × two scripting states = 200,000 comparisons. It compares marker exposure after legacy serialization/reparsing with marker exposure after projection and serialization/reparsing. Unique marker values distinguish individual images. No new active marker, marker namespace, or template-membership change was found in this corpus; `roundtrip-results.json` records the results.

This is a finite search for the selected mechanism, not a proof that serialization is safe. In particular, it does not negate the separately demonstrated shadow-root lowering failure. Serialization carries no parser-state or sanitization provenance.

## Earlier expansion experiments

These files document why simple expansion and name-based repairs are insufficient. They do not define the selected profile.

```sh
npm run probe
npm run matrix
npm run normal-form
npm run recovery:base
npm run recovery
```

- `browser.html` compares five inert source pairs using native `DOMParser`. Each original contains zero image markers; expanding one slash produces one. The cases cover style, textarea, a MathML integration point, and HTML/custom ancestors before SVG. `chromium-results.json` records them. These demonstrate parser mismatches, without executing handlers or demonstrating a current sanitizer bypass.
- `model.mjs` models synthetic start/end expansion, with variants excluding text names or excluding text plus foreign ancestry. Its special-element behavior is incomplete. Those variants are experimental counterexamples, not a normative browser algorithm.
- `matrix.mjs`, seed `0x51e1f00d`, tests ten fixed inputs plus 3,000 generated sequences against four sanitizer configurations × four contexts × three variants: 144,480 comparisons. DOMPurify default/custom and sanitize-html default each have 36,120 comparisons with no branch activation. The deliberately permissive sanitize-html policy has 726 activations, 27 changed trees, and no selected signal increases. Nine baseline signal occurrences are not new or proven exploits. Configuration and results are recorded in source and `matrix-results.json`.
- `audit.mjs` independently observes eligible tokens on the legacy trace. `normal-form.mjs`, seed `0x4e4f524d`, performs 160,000 audits; all 99,549 eligible-free traces match the expansion model. This checks a conditional transition-equivalence argument, without proving its precondition for all sanitizer outputs.
- `recovery-candidates.mjs` records rejected repairs. A set of previously closed names can become stale after an ancestor closes; treating a later matching closing tag as live can exit SVG incorrectly and expose an image. Heading aliases defeat exact-name matching too. Changed-marker counts include changes in either direction, not exploit counts. The selected reference retains complete recognition state.

## Limits

The Node model and DOMPurify's jsdom backend share parse5, so those comparisons are not independent browser engines. parse5 8.0.1 also has older select behavior than current Chromium; each model preserves its own baseline recognition. Native fragment state, declarative roots, scripting, custom-element registries, encoding restarts, speculative loading, and document writing are not fully modeled.

Selected event-handler, script, URL, and marker signals can miss CSS effects, DOM clobbering, application-defined components, and indirect execution. Parentage intentionally changes; arbitrary application behavior cannot be assumed equivalent. Sanitization must use the intended grammar and destination context.

No complete native-browser security proof or browser-vendor endorsement follows from these experiments. The proposal's text-to-markup construction argument, tested cases, failed lowerings, and remaining implementation obligations are separate claims.
