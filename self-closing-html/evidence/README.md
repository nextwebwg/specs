# Opt-in Self-Closing HTML: reproducible evidence

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

## Incremental construction and live execution (19 October 2026)

The new incremental model retains the same recognition parser while input arrives in chunks. `streaming.test.mjs` enumerates every two-chunk boundary of 12 selected witnesses, checks code-point feeding, script checkpoint pause/resume, and exact initial doctype selection. `streaming-check.mjs` records 60,000 comparisons (10,000 generated sources × three chunk schedules × two scripting states), seed `0x5354524d`. `streaming-results.json` records zero final-output differences from the shared static reference. This tests chunk invariance; shared recognition code means it is not an independent proof of HTML parsing correctness.

`live-dom.mjs` applies changes at token boundaries to actual DOM nodes, preserving application mutations rather than replacing a completed document. `execution-browser.mjs` tests script checkpoints under four input schedules, callback construction and upgrade, observer and microtask timing, detached ancestors, moved shorthand elements, legacy innerHTML, raw-text/namespace boundaries, external classic-script blocking, rejection of document.write/writeln/open, reentrant-input rejection, streamed UTF-8, and a connected-image request control. `execution-results.json` records 20 passing targeted execution cases plus 500 generated recovery/refinement cases each in Chromium 156.0.8078.4, Firefox 157.0, and WebKit 26.5. The request log contains the image positive control and excludes the namespace witness's apparent image.

The streamed source arrives through a local HTTP response. The server deliberately splits a four-byte UTF-8 character; the client incrementally decodes network bytes before feeding the parser. This demonstrates the prototype's UTF-8 input path, not native encoding sniffing or navigation restart.

The adapter activates connected HTML classic scripts at end-tag checkpoints and explicitly performs a microtask checkpoint before resuming. It uses dynamic browser script elements. Native parser-inserted flags, modules/async/defer queues, stylesheets blocking scripts, CSP/Trusted Types integration, declarative shadow roots, customized built-ins, and speculative scanning are not implemented by this adapter. Existing static native-root tests remain separate. Its document-writing rejection and concurrent-input rejection are concrete experimental contracts, not evidence that browser engines already implement those restrictions.

Reproduce sequentially with an accepted Node version:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run test:streaming
npm run streaming
npx playwright install chromium firefox webkit
npm run execution
```

Playwright 1.62.1 is pinned. `CHROMIUM_EXECUTABLE`, `FIREFOX_EXECUTABLE`, and `WEBKIT_EXECUTABLE` may select existing compatible test binaries; the recorded versions identify the binaries actually used. `PLAYWRIGHT_MODULE` optionally selects an existing shared Playwright installation. No test starts more than one browser at once, and the local HTTP server is closed in the runner's finalizer.

## Mechanized static proof

`Projection.lean` models a forest of immutable recognized-node payloads with eligibility and protected-container flags. Structural induction proves preservation of the complete payload preorder and each node's protected-ancestor path. Payloads can include identity, namespace, attributes and text. Protected roots must be represented as barriers by the caller. This is an abstract model of the selected pure transformation, not verified HTML tokenization or a proved refinement of the JavaScript, Rust, DOM, or browser implementations.

Run with Lean 4.35.0:

```sh
lean Projection.lean
```

`formal-results.json` records compiler identity, source SHA-256, successful exit, and Lean's reported axiom dependency (`propext`). The two proofs contain no admitted holes. The compiler distribution used was the official `lean-4.35.0-darwin_aarch64.tar.zst`, verified against release SHA-256 `c0c6f34f35ba1dcc5c4a5fd106fefab9eb5e8469712624dd2c868d51b63177c2`.

The proposal's security chapter maps every proof method to its supported claim and limit. Construction arguments, mechanized universal statements about the abstract model, exhaustive partitions of selected strings, generated comparisons, independent inert native observations, live execution, and counterexample/positive controls are deliberately distinct evidence.

### Recovery counterexample found by live refinement

The generated DOM-refinement check uses seed `0x444f4d52`, 500 sources per engine. It compares actual DOM node kind, namespace, attributes, text, order, and template contents with the incremental output model. All 1,500 current comparisons pass. This checks the adapter’s output correspondence in those cases; recognition is still shared.

The initial adapter failed `<body><table>text<div/>`: foster recovery exposes both a new text node and a new div before an existing table in a single token checkpoint. Using the not-yet-connected div as the text insertion anchor appended the text after the table. `live-dom.test.mjs` first reproduced `DIV, TABLE, #text` instead of `#text, DIV, TABLE`; the fix locates the next already-connected parser sibling. The focused regression and the three-engine generated corpus then passed. This is an output-order bug, not a demonstrated sanitizer exploit, and the counterexample remains in the suite.

The live adapter creates inert script placeholders and replaces each with a dynamic script at its activation checkpoint. That differs from native parser-inserted script identity and mutation records. Its execution tests do not transfer the static model's node-identity theorem to these placeholder DOM nodes. Native parser identity, parser-inserted script flags and scheduling are separate obligations for the engine prototype.

A second mutation counterexample uses an implicit body containing a hidden input. Script moves the input into the head; a following frameset replaces the implicit body. The first adapter removed every node no longer reachable in its recognition snapshot, wrongly deleting the moved input and detaching descendants individually from the removed body. The regression first verifies that frameset recovery actually happened, then checks preservation of the moved input and the detached script's parent. Removal now applies only to a removed subtree's root under its previous parser-owned parent. The focused test failed before this fix and passed after it. This tests mutation ownership, not equivalence of arbitrary script effects to legacy HTML.

### Native popover boundary

The containment audit found that `popover` was missing from the protected global attributes. Before the fix, `<div popover/><button>control</button>` lifted the button outside the closed popover. Empty and invalid attribute values each exposed a rendered button in Chromium, Firefox, and WebKit; five of the six recorded focus attempts also focused it. `popover-counterexample-results.json` preserves those failures. The shared recognition eligibility and protected-ancestor signature now treat `popover` as a barrier alongside `inert`, `hidden`, and `disabled`. The focused static test was observed failing before the fix and passing after. Browser regressions check containment, closed-state geometry/focus and an open-state visibility control. These are native visibility/ownership observations, not demonstrated sanitizer exploits.

The relevant platform contract is [HTML's popover state](https://html.spec.whatwg.org/multipage/popover.html) and [rendering rule](https://html.spec.whatwg.org/multipage/rendering.html): closed popovers are not rendered; an invalid `popover` value selects the Manual state rather than removing the boundary. This also illustrates the mechanized theorem's classification premise: proving preservation of designated barriers does not prove that an implementation has designated every necessary barrier.

Focus checks explicitly close open popovers, blur, remove each frame and await a rendering checkpoint before the next case. A Firefox invalid-value focus assertion passed in isolation but initially failed after earlier frames; explicit teardown removed that cross-case interference. Each popover case also compares focus behavior with an independently constructed native control using the same hidden-before-open call history. The closed-state containment/visibility assertions remain unconditional.

Execution reports include source SHA-256 digests and a `caseFilter` field. `BROWSER_ENGINES` and `EXECUTION_CASE` support focused diagnosis; filtered runs are not complete three-engine evidence. The recorded full result has a null filter and all three engines.

## Native navigation implementation

`native-ladybird.patch` implements the experimental profile in Ladybird at the exact upstream commit in `native-results.json`. It preserves the native recognition stack and routes output insertion through recorded sibling boundaries. Navigation alone can select the profile; existing DOM parsing APIs retain legacy behavior. The native document rejects `write`, `writeln`, and the document-writing `open` overload. The optional speculative scanner is disabled for Next documents.

The final native run passes both suites: 31 targeted checks and 200 differential inputs, 214 activations, zero baseline disagreements and zero mismatches. See the security chapter's six-obligation matrix for tested behavior and limits. `native-final-test.log` records the actual runner result. `native-initial-routing.patch`, `native-initial-execution-results.txt`, and `native-initial-refinement-results.json` retain the first executed failure: 30/31 targeted checks and 23/200 differential mismatches. Eligibility must be frozen before foreign recovery; output insertion boundaries must track live siblings rather than stale numeric offsets. These corrections pass the retained corpus, not all HTML.

To reproduce, check out the pinned upstream commit, apply `native-ladybird.patch`, and copy `native-corpus.json` to `Tests/LibWeb/Text/input/HTML/next-parsing-corpus.json`. Follow Ladybird's build prerequisites and pinned vcpkg baseline. This run used Rust 1.98.0, CMake 4.4.4, Ninja 1.13.2, Apple Clang 21, Qt from Homebrew, and the Release preset with GUI targets enabled, LTO and Cranelift disabled. The vcpkg baseline was `20ceb8adbf0504d4b0d5e4058a32f9d4fc896391`. With that checkout bootstrapped and Rust 1.98.0 on PATH, configure and build:

```sh
cmake --preset Release -DENABLE_GUI_TARGETS=ON -DENABLE_LTO_FOR_RELEASE=OFF -DENABLE_LAGOM_CCACHE=OFF -DENABLE_CRANELIFT_JIT=OFF -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qtbase -DRUST_RUSTC="$(command -v rustc)" -DRUST_CARGO="$(command -v cargo)"
cmake --build Build/release --target test-web --parallel 8
```

These are the recorded macOS settings, not portable build requirements. Build settings are not included in the algorithm patch. The patch also exposes bundled fonts to the test application, necessary for this machine's test startup.

```sh
LADYBIRD_SOURCE_DIR="$PWD" Build/release/bin/test-web --test-concurrency 1 --per-test-timeout 180 --filter 'Text/input/HTML/next-parsing-*.html' --results-dir /tmp/next-native-results -v -v
```

Use `--collect-garbage-on-every-allocation` for the separate GC stress run. Native baseline DOMParser output is first checked against parse5; disagreements are counted separately rather than silently accepted. The bounded native comparison is independent recognition evidence, whereas the adapter's refinement check shares recognition code. Neither proves universal implementation refinement. Ladybird's existing encoding-change path does not implement arbitrary byte-prefix restart; that is an explicit remaining obligation. No production browser adoption or security approval is implied.

The extra allocation-by-allocation GC stress run is **inconclusive**: the refinement test reached its 180-second timeout without completing; the remaining execution stress test was interrupted after that timeout. `native-gc-test.log` and `native-results.json` record the attempt. The ordinary passing suites do not imply memory safety or a passing GC stress run.

A separate existing upstream parser regression selection (`Text/input/HTML/parser-*.html`) passes all 16 tests with the patch. `native-legacy-test.log` records that bounded regression run; it is not the full upstream suite.
