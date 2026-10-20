---
title: Security and evidence
order: 2
blurb: text recognition · inactive boundaries · tested results · remaining work
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · security properties
status: "Unofficial Editor's Draft · Stage 0"
---

# Security and evidence

**The output must not introduce executable markup that the source reader treated as text or ignored.** The proposed algorithm keeps HTML's source interpretation authoritative while allowing ordinary empty-element placement.

## The security case, directly

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

If the parser immediately forgets div at the slash, the later closing div can no longer recover out of SVG in the same way. That can change the following style's namespace and expose an image handler.

In the proposed parser, the source reader retains div. The later closing div exits SVG, and the HTML style reads the apparent image as text. A separate builder proposes where recognized nodes go. Its conflicting namespace result is rejected; checked recovery keeps the style text intact.

For `<style/><img src=x onerror="attack()"></style>`, style's ordinary text-reading boundary remains in force. The apparent image is also text. **Neither case requires an image to be created and then cleaned up.**

[See the paired flow diagrams →](/self-closing-html/parsing#why-remembering-the-element-matters)

## What every output element must retain

The reference checks each output element against an actual source-reader element:

- The same source identity, namespace and attributes, used at most once.
- The same template owner and foreign-namespace ancestors.
- The same script, style or special text-reading owner, with that owner's contents unchanged.

Normal parentage can change: that is the intended shorthand. An output path that fails these checks is rejected. The same checks apply to recognition-based recovery; the final fallback is the source tree itself.

These are proposed parser invariants, supported by an implementation, finite audits and an abstract selection proof. They do not establish that arbitrary application code behaves identically after parentage changes.

## Issue checklist

✅ Demonstrated within the stated scope · ⬜ Remaining implementation work.

| Issue | Mechanism and evidence |
| --- | --- |
| Text becomes a tag after a self-closing change. | ✅ Existing source reading and unchanged text-owner contents. Direct style/textarea cases and namespace-recovery attacks stay text in reference and three-engine adapter tests. |
| Placement creates a source-reader-ignored element. | ✅ Each output element requires a source identity. Form/select counterexamples demonstrate why those boundaries remain. |
| Template contents or foreign code cross an active boundary. | ✅ Protected ownership/ancestry and code contents are checked on both output paths. Tested template scripts/handlers remain inactive, and template images issue no observed request. |
| Useful HTML requires broad exceptions. | ✅ Formatting, wrappers and table rows/cells use normal placement. 4,000 structured authoring cases and 1,000 table cases match explicit empty pairs. The earlier pure projection differed in 1,777 of those structured cases. |
| Malformed input bypasses a rejected placement. | ✅ Both choices are checked, with source-tree fallback. The initial failed fuzz witnesses are retained as regressions; an injected faulty recovery is also rejected. |
| Streaming changes the result. | ✅ Every two-chunk split of retained authoring examples and attack witnesses is checked. The generated audit covers 120,000 document/fragment cases and 20,504 token checkpoints. |
| Parser updates lose application changes or execute the wrong script. | ✅ Targeted adapter tests preserve owned mutations, honor a pending script's live text/type changes, and expose completed checkpoints before execution. These are finite tests. |
| Native table layout agrees with the output DOM. | ✅ Adapter tests check table row/cell APIs and geometry in Chromium, Firefox and WebKit. |
| The adapter briefly activates template resources during construction. | ✅ Nodes are created in a document without a browsing context. Request traces include an active positive control and no tested template/attack request. |
| Complete native integration and production cost. | ⬜ Native parser implementation, form association, declarative shadow roots, modules/scheduling, encoding restarts, speculative loading, arbitrary script interleavings and performance remain to be verified. |

## Evidence and reproduction

From the evidence package with its pinned dependencies:

```bash
node --test recognition/*.test.mjs
node recognition/placement-check.mjs
node recognition/dx-check.mjs
node recognition/browser-runner.mjs
```

The current records contain **88 component and placement test passes**, **120,000 generated comparisons**, **20,504 checkpoint audits**, **5,000 authored-output comparisons**, and **16 targeted cases per browser adapter engine**. The browser runner uses one engine at a time.

[Implementation, reports and exact scope →](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/recognition#readme)

The three adapters share parse5 8.0.1 source reading, including its older select recovery. The nested-select boundary also follows the current HTML rule; the reference is not a complete implementation of the latest HTML Standard. Source-reader updates and native baseline comparisons remain required.

 Chromium, Firefox and WebKit independently provide DOM, script, custom-element and resource behavior. This is not native navigation-parser interoperability.

::: {.details summary="What the machine-checked proof means"}

Imagine each source element has a receipt recording its identity, namespace/attributes, protected ancestors and owned code/text. An output element must present a receipt from the source reader. Both proposed placement and recovery are checked; if both fail, the algorithm uses the source receipts themselves.

[Placement.lean](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/Placement.lean) proves that this abstract choice always returns source-authorized receipts. Assuming unique source identities, it also proves that selected identities are unique. Five named theorems compiled in Lean 4.35.0; the compiler/source hashes and log are recorded alongside the file.

The theorem verifies the abstract selection rule. It does not prove that the JavaScript implements it correctly, that parse5 implements all HTML rules, or that browser scheduling is secure. The earlier forest-projection proof concerns a component recovery transformation, not this complete placement algorithm or its output order.

:::

## Limits of the claim

Recognized event handlers and scripts remain active where ordinary HTML recognizes them. The checks prevent the specified parser-created text/ignored-element and protected-context changes; they do not turn arbitrary HTML into safe application content.

Changed parentage can change CSS, event propagation, accessibility, form ownership and application-defined behavior. Attributes apply to the resulting DOM. A visibility or interaction change alone is not evidence of an execution vulnerability.

Native integration and independent implementer review remain necessary before shipping. The prototype's full-tree checking also needs a production performance design. Safe parsing APIs retain their normal handling of untrusted HTML; that separate application protection is not the basis of this algorithm's argument.

::: {.details summary="Earlier experiments"}

The [immediate-closure experiment](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme) changed source recognition and retains an activation counterexample. Its earlier Ladybird results do not implement this candidate.

The first recognition-only projection protected source reading but gave unexpected authored results for nested same-name wrappers and reconstructed formatting. Its tests remain component evidence. The current placement builder and independent source checks address those DX failures while retaining authoritative source interpretation.

:::

[Parsing rules →](/self-closing-html/parsing)
