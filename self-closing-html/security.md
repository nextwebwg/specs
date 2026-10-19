---
title: Security and evidence
order: 2
blurb: sanitizer mismatch · worked solution · experiments · implementation requirements
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · security contract
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

Self-closing syntax must not turn harmless text into running code, expose hidden controls, or silently change how a library reads HTML. The proposal addresses these problems by keeping HTML’s existing decisions about text and tags, preserving sensitive containers, and requiring an explicit request for the new parsing behavior.

**There is a working experimental browser implementation, but this is not ready for browser shipment.** The tests below demonstrate specific fixes. Encoding restarts, broader conformance, and implementer security review remain open.

## Issue checklist

A checked item means the stated fix has evidence at the level described. It does not mean every possible browser input has been proved safe.

- [x] **Apparent tags inside text stay text.** Do not let the slash close `style` or other text-sensitive elements. Keep HTML’s normal interpretation of later text and SVG boundaries. The mathematical proof checks the rearrangement rule; browser examples check selected parsing cases.
- [x] **Hidden controls keep their protection in the tested cases.** Preserve sensitive containers and attributes, including a `popover` protection added after a test exposed a bug.
- [x] **Existing library parsing calls keep their meaning.** The proposed contract requires an explicit request for new string-parsing behavior; the prototype tests check isolation.
- [x] **Streaming, scripts, callbacks, pauses, and mutations work in the recorded native cases.** The experimental browser passes 31 targeted checks and 200 reference comparisons. This is evidence from one native engine, not production support.
- [x] **Shadow roots stay with their hosts in the tested native cases.** A separate serialization shortcut failed and is not a general conversion method.
- [ ] **Ignored slashes can mislead authors.** `<script />` still starts a script; following valid JavaScript can execute. Keeping existing parsing does not eliminate that authoring hazard. Tool diagnostics and author understanding remain unverified.
- [ ] **Serialization is not generally proved safe.** Generated tests found no new monitored exposure, but do not remove the known conversion limitation.
- [ ] **Fast look-ahead loading remains incomplete.** The native prototype disables that optimization rather than proving an optimized loader correct.
- [ ] **Encoding restarts, memory stress, broader conformance, and security review remain open.** A timed-out stress run is not a pass.
- [ ] **The newer profile selectors and parsing options need native implementation.** The native experiment tests only the earlier literal `PUBLIC "next"` opt-in.

[Read each issue’s solution, evidence, and limits →](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme)

## The two main risks

The 2023 WHATWG proposal already suggested a document opt-in. The objections concern what happens after opting in: old sanitizers can disagree with the parser, and a document flag can silently change a library's parsing behavior.[^1][^2]

| Objection | Proposed answer |
| --- | --- |
| A sanitizer approves text that the browser exposes as executable markup. | Keep HTML’s decision about what is text and what is a tag. Change only where eligible nodes sit in the document tree. |
| A library receives a different parsing grammar without requesting it. | Keep existing string-insertion calls on their current rules. New parsing behavior requires an explicit request. |

The earlier #721 discussion also raises compatibility with existing authored markup, including names containing hyphens.[^3] Plain HTML keeps its meaning. Only the explicit Next declaration selects the new document profile; custom-element registration cannot change that profile. Unsupported browsers still need a correct fallback.

> [!ex] What is resolved, and at what level?
> The rearrangement algorithm keeps parsed text as text. The proposed API rules keep existing library calls on their original behavior. The native prototype tests selected examples of both; that does not establish safety for every possible page.

## Block the direct style exploit

This is the sanitizer-mismatch example from the thread:[^1]

```html
<style/><img src onerror=alert(1)><style></style>
```

Ordinary HTML ignores the slash on `style`. The apparent image is text inside the stylesheet. Expanding `<style/>` into `<style></style>` would instead leave that text container and expose an image with an event handler.

**The proposal keeps `style` exempt from self-closing.** The slash therefore cannot end its text container. The parser reads the apparent image as text, so there is no image element to load and no `onerror` handler to attach.

The same rule covers `script`, `textarea`, and the other text-sensitive names in the [eligibility table](/self-closing-html/parsing#preserve-sensitive-elements). Parsing must also use the same scripting state: disagreement about `noscript` caused the Bleach mutation-XSS vulnerability.[^4]

## Recover at namespace boundaries

Exempting `style` alone does not protect a later style element whose namespace changes because of an earlier shorthand. This example shows the remaining problem:

```html
<div/><svg></div><style><img data-probe></style></svg>
```

The safe result is that the apparent image stays text. Merely replacing `<div/>` with `<div></div>` can break that result: the later closing tag no longer ends the same HTML/SVG context.

The proposed parser remembers the div until ordinary HTML rules close it, even though the div is already empty in the output. That lets the later `</div>` exit SVG correctly. The following `style` is then read as an HTML stylesheet, keeping the apparent image as text.

::: {.details summary="Technical walkthrough: HTML/SVG recovery, step by step"}

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

:::

## Keep a library's parsing contract stable

The second security objection concerns a mode switch outside the code that parses an HTML string.[^2] A library calling `innerHTML` must not acquire different tokenization because its caller changed the page's doctype.

Under the proposed contract, the same string inserted through an existing HTML API uses that API's existing grammar in either document profile. `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `DOMParser`, fragment parsing, `Document.parseHTML*`, and `iframe.srcdoc` do not inherit Next from the document.

Dynamic Next parsing requires an explicit request at the parsing call. Parse and sanitize together in the actual destination context, then insert nodes directly. A doctype inside the string cannot enable Next. The [insertion rules](/self-closing-html/parsing#keep-existing-insertion-apis-stable) also require rejection or isolation of document writing, rather than feeding legacy string writes into the new document grammar.

## Preserve protected containment

Preserving recognized text is necessary, but containment can affect whether an existing node becomes active or visible.

Closed dialogs, disclosure widgets, popovers, and media fallback containers are exempt. Active-browser checks found that lifting their children could expose hidden controls. Elements carrying `inert`, `hidden`, `disabled`, or `popover`, template content, and foreign contexts retain their protected boundaries too.

A cross-browser counterexample added the `popover` attribute to this boundary: lifting a button out of a closed popover made it visible in all six recorded observations, and focused it in five. The [before-fix record](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/popover-counterexample-results.json) and passing regression preserve that distinction from a demonstrated sanitizer exploit. Empty and invalid attribute values both select a popover state under the [HTML Standard](https://html.spec.whatwg.org/multipage/popover.html).

Shadow roots keep their recognized host. A root is an ownership relationship, not a light-DOM child to move after an empty host. The browser checks preserve that edge while allowing the host's light DOM to become empty.

Parentage intentionally changes elsewhere. Application-defined components and script gadgets require their own policy; a sanitizer must not authorize hazardous content solely because an ordinary ancestor currently hides or intercepts it.[^5]

## The rearrangement keeps text as text

The proposed algorithm changes where already-parsed nodes sit. It does not read their contents as HTML again. If HTML identified `<img ...>` as stylesheet text, moving nodes cannot turn that text into an image element.

**What was proved:** a mathematical description of this rearrangement preserves node contents, order, and designated protected containers. The proof assumes the parser correctly identified those nodes and containers.

**What a browser must do:** implement that rule correctly while parsing and running scripts. The prototypes pass the recorded tests; the proof does not cover a complete browser.

::: {.details summary="Technical details: the model, theorems, and proof limits"}

The [Lean model](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/Projection.lean) describes a document as a collection of trees, called a *forest*. Each tree node carries a *payload*: the identity and information that the rearrangement must preserve. The model takes as inputs which wrappers may use self-closing syntax and which containers are protected. It does not establish whether those input classifications are correct.

Lean is a proof checker. Version 4.35.0 verifies that the following claims hold for every finite tree collection described by this model, rather than only for a generated set of examples:

- `preorder_project`: visiting the nodes in document order produces exactly the same sequence of payloads before and after rearrangement. When the payload includes a node’s namespace, attributes, and text, those values are preserved too.
- `protectedPaths_project`: each node has exactly the same sequence of protected ancestors before and after rearrangement. An ancestor is a container surrounding that node; this claim prevents the rearrangement from moving a node across a protected boundary.

The proofs establish the claims for individual nodes and show that combining those nodes into larger trees preserves them. This technique is called *structural induction*. Lean reports `propext`, its principle for treating logically equivalent propositions as equal, as an axiom dependency. There are no admitted proof holes: no step is left as an unchecked assertion.

The [verification record](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/formal-results.json) identifies the compiler and the exact source checked. The proof does not cover reading HTML source, choosing eligible wrappers or protected containers, matching browser code to this mathematical model, script execution, or sanitization. Those require separate arguments and implementation tests.

:::

The static prototype rearranges a completed tree. The native prototype builds the result as HTML arrives, with tests at script and callback boundaries. Its tests are separate evidence from the mathematical proof.

## Detailed test records

The [issue checklist](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme) translates the findings into problems and answers. Expand this section for counts, methods, and the native implementation’s precise limits.

::: {.details summary="Technical evidence: test methods, counts, native coverage, and failed attempts"}

### What the experiments establish

The experiments test the reference construction and expose boundaries that a browser implementation must preserve. They use the earlier literal `PUBLIC "next"` opt-in. The proposed named selectors and preset-resolution contract in [HTML Feature Profiles](/html-feature-profiles/) are not implemented or proved by these results.

| Check | Recorded result |
| --- | --- |
| Generated parsing cases | 800,000 comparisons preserved the checked recognition properties. |
| Earlier expansion/sanitizer candidates | 144,480 sanitizer comparisons and 160,000 recognition audits characterize the rejected approaches; configuration-dependent inactivity and finite signal coverage prevent a universal sanitizer claim. |
| Ordinary authoring examples | 40 comparisons matched explicit pairs or the specified exemption. |
| Chromium probes | 12 inert comparisons preserved the checked node properties, including the reported text/namespace cases. |
| Serialization and reparsing | 200,000 comparisons found no new marker exposure against the legacy baseline. |
| Native containment | Sandboxed comparisons identified the native-container exemptions. |
| Shadow-root ownership | Six inert native open-root comparisons preserved root ownership and the checked containment properties. |
| Incremental reference parsing | 60,000 seeded comparisons preserved final output across code-unit and randomized chunk schedules, with scripting recognition enabled and disabled. |
| Boundary enumeration | Every two-chunk split of 12 selected authoring and recovery witnesses matches the static reference; focused tests also exercise pause/resume and exact initial opt-in. |
| Live browser execution | 20 execution cases pass separately in Chromium, Firefox, and WebKit: scripts, reactions, upgrades, microtasks, observers, mutation, writing isolation, external-script blocking, and streamed input. |
| Live-DOM refinement | 500 generated recovery cases per engine (1,500 comparisons) match the incremental model’s final tree; foster-parenting and mutation-ownership counterexamples drove passing regression tests. |
| Native Ladybird navigation | 31 targeted execution checks pass; 200 independent native/reference comparisons agree, with 214 shorthand activations and no baseline disagreements. |
| Resource side effects | Each engine records the connected-image positive control and no image request from the namespace/raw-text witness. |

The [evidence README](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme) provides pinned dependencies, commands, seeds, results, and limitations.

The static prototype uses parse5 8.0.1, including its older select behavior. The incremental prototype shares that recognition implementation. Its live-DOM adapter executes connected classic scripts in real browser frames and applies parser changes without rebuilding the active tree. It is not a patched native navigation parser. The three engines independently supply DOM operations, custom-element reactions, script execution, and resource requests; they do not independently recognize Next source in these adapter tests.

### What each method establishes

| Method | Claim it supports | Boundary |
| --- | --- | --- |
| Construction argument and mechanized induction | Pure projection preserves recognized payloads, order, and protected ancestry. | Requires correct recognized input and eligibility/barrier classification. |
| Exhaustive split enumeration for selected inputs | Those witnesses are invariant at every tested two-chunk boundary. | Exhaustive over partitions of the selected strings, not all HTML. |
| Seeded generated comparisons | Checked invariants survive the recorded generated corpus and chunk schedules. | Shared parser code and finite input coverage are explicit dependencies. |
| Independent native recognition probes | Selected recovery and root-ownership behavior agrees with native Chromium. | Inert recognition and containment observations do not establish execution timing. |
| Live execution in three browser engines | The incremental adapter exhibits the recorded callback, mutation, pause, and resource behavior. | Its tokenizer is parse5, and its classic-script scheduling is an explicit prototype contract. |
| Positive and negative controls | Monitored effects are observable, and rejected designs expose the recorded failures. | A monitored signal is not a complete definition of security. |
| Patched native engine execution and differential testing | Actual navigation exercises incremental network input, parser-inserted classic/module scheduling, reactions, pauses, mutation, CSP, shadow ownership, and API isolation; 31 checks and 200 comparisons pass. | One experimental engine and a finite corpus; speculative scanning is disabled for Next documents. |

Its serializer also fails the recorded declarative shadow-root ownership case; it is not a conforming lowering tool. The separate native-root checks preserve ownership. Finite passing comparisons establish coverage, not universal browser safety.

### Native execution coverage and limitations

The [native patch](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/native-ladybird.patch), [pinned results](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/native-results.json), and evidence README make the native experiment reproducible. This is actual native navigation parsing, independently compared with the parse5 model, rather than the live-DOM adapter.

| Obligation | Native evidence | Remaining boundary |
| --- | --- | --- |
| Streaming | Script runs before response EOF; parsing resumes after a blocked network chunk containing Unicode text. | Not an exhaustive encoding or network-boundary proof. |
| Script execution | Classic, failed external, async, defer, inline modules, external module graph, stylesheet blocking, and CSP checks pass. | Finite scheduling witnesses; arbitrary script effects remain unproved. |
| Custom-element reactions | Construction and upgrade execute against the incremental output DOM. | Exhaustive reaction reentrancy and lifecycle combinations remain unproved. |
| Parser pauses | Blocking external scripts stop later source; async source proceeds; native resume passes. | Encoding restart behavior needs separate implementation and tests. |
| Speculative loading | Request records show no speculative image fetch while a prior script is blocked, followed by the ordinary fetch after release. | The optional speculative scanner is disabled for Next documents; no optimized scanner equivalence claim. |
| Script-driven mutations | Removed recognition ancestors, moved shorthand elements, fixed profile after doctype mutation, writing isolation, and shadow ownership pass. | Not equivalence for every possible mutation or a universal security proof. |

The first native routing attempt passed 30 of 31 execution checks but disagreed with 23 of 200 generated reference outputs. The retained initial results show why compilation was insufficient. Freezing eligibility before foreign-content recovery and replacing stale child offsets with live sibling boundaries corrected the recorded cases. The final normal run passes both suites without skipping a baseline disagreement. A separate allocation-by-allocation GC stress attempt timed out at 180 seconds without completing refinement; the remaining stress test was stopped. That attempt is inconclusive and supplies no passing memory-safety evidence. The initial patch and results remain evidence of falsification and regression, not current conformance claims. A separate existing upstream parser selection passes 16 tests with the patch; the full upstream suite was not run.


:::

## Ready for discussion is different from ready to ship

This draft can be discussed as an incubation proposal: it identifies the authoring problem, describes a concrete parser change, provides runnable experiments, and lists its tradeoffs. It is not a completed browser feature or an approved security design. The exception set is a proposed conservative boundary; its usability and completeness need review.

### Work plan before browser shipment

Before shipment: review the exceptions, integrate profile selection, handle encoding restarts, expand native execution and memory tests, and obtain implementer security review. None of those gaps is closed by a passing documentation check.

::: {.details summary="Shipment checklist: required work and completion evidence"}

Complete the design review first, then implement the missing behavior, expand the tests, and seek independent engine review. These are proposed completion criteria, not promises that the work is already funded or assigned.

| Work | What must be done | What would establish completion |
| --- | --- | --- |
| Exception policy and author mistakes | Review the excluded elements and contexts; define useful diagnostics for ignored slashes; evaluate whether authors understand the scope. | An agreed eligibility contract, positive and negative conformance cases, implemented diagnostic behavior where specified, and author research that evaluates the benefit and exception cost. |
| Profile integration | Implement named selection, response headers, and explicit parsing options under HTML Feature Profiles. | Native tests of precedence, unsupported requests, independent parsing, and existing API isolation. Passing tests of the old literal `next` selector do not satisfy this. |
| Encoding restarts | Define how recognition and output state are discarded or rebuilt when the browser rereads bytes in another encoding. | Native restart tests across affected source boundaries, showing no duplicated nodes or execution and the intended final document. Existing network-chunk tests do not satisfy this. |
| Loading and execution | Extend the passing script, callback, pause, mutation, and shadow-root cases to the complete browser contract. Keep look-ahead loading disabled unless its behavior is verified. | Shared conformance tests for native scheduling and root ownership; request traces showing any enabled look-ahead loader respects the same boundaries. |
| Broader regression and memory testing | Run relevant engine suites, retain discovered failures as regressions, and finish garbage-collection stress testing. | Completed result records with failures resolved or explicitly dispositioned. A timeout supplies no passing evidence; a passing run is still not a universal memory-safety proof. |
| Security and interoperability review | Have browser implementers review the parsing, protected-container policy, sanitizer boundary, and implementation. Develop Web Platform Tests usable by independent implementations. | Published review outcomes and interoperable test results, with remaining risks explicitly accepted through the standards process. No vendor commitment or endorsement is reported here. |

:::

[Flexible HTML Nesting](/flexible-html-nesting/) is separate. Its layout and containment behavior needs its own implementation and evidence; these self-closing proofs do not establish it.

> [!warn] Implementation status
> The reference model proves a limited rearrangement property. An experimental Ladybird build passes bounded streaming and execution tests. The work above remains required before shipment; the evidence does not establish universal execution safety.

Editor: [Matthew Dean](https://github.com/matthew-dean). Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [Simon Pieters: sanitizer mismatch and the style example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790), and [Keith Cirkel: updating libraries does not protect existing installations](https://github.com/whatwg/html/issues/9491#issuecomment-1623794848).
[^2]: WHATWG HTML, [Henri Sivonen: parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^3]: WHATWG HTML, [#721: existing self-closing-looking markup](https://github.com/whatwg/html/issues/721#issuecomment-186914414), and [existing hyphenated names](https://github.com/whatwg/html/issues/721#issuecomment-187737022).
[^4]: Mozilla, [CVE-2020-6802: Bleach mutation XSS in noscript handling](https://bugzilla.mozilla.org/show_bug.cgi?id=1615315).
[^5]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
