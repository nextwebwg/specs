---
title: CSS declaration syntax audit
sectionNav: true
---

# CSS declaration syntax audit

Parse complete declarations, reject unsupported constructs, and rebuild accepted values. Splitting style text at semicolons would incorrectly promote text inside functions or blocks into new declarations.

## Selected source

The reviewed [CSS Syntax Level 3 source](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-syntax-3/Overview.bs) is pinned to `40527902c4d0840cdb7a808c8cd42302be1c3bc8`. It is an Editor’s Draft, not a Recommendation. Its declaration-list entry point differs from the 1 October 2026 Candidate Recommendation Draft. This pin supplies the candidate syntax reference for the experimental inline profile.

Source SHA-256: `e6ae53577519ff89daf15914e8ad84aeb1a61440c0fd32194e54e3bbf4bf9ff2`.

| Source lines | Reviewed scope |
| --- | --- |
| 1–312 | metadata; introduction; escaping; error recovery; parsing overview |
| 441–549 | preprocessing and tokenization contract |
| 810–1735 | token definitions and ordinary tokenizer algorithms; unicode-range lookahead read but descriptor path unselected |
| 1800–1859 | bad URL recovery and parsing introduction |
| 1994–2327 | parse result structures; token streams; normalization; generic grammar matching |
| 2436–2468 | declaration-list entry point |
| 2508–2624 | declaration and component entry points |
| 2698–3293 | at-rule, qualified rule and block recovery; declaration and component consumers |
| 3576–4070 | grammar validity; rejected stylesheet/rule contexts; serialization table; privacy/security; changes/end |

The 2,982 reviewed lines cover selected preprocessing, tokenization, declaration recovery and serialization paths. Stylesheet encoding detection, selectors, An+B, unicode-range descriptors and full referenced-module closure are outside this review.

## Processing consequences

Preprocess line endings, NUL and surrogate characters before interpreting token coordinates. Consume balanced discarded functions and at-rules without admitting their contents. Error recovery can retain valid preceding or later declarations; malformed input does not necessarily invalidate an entire style attribute.

Syntax validity is separate from the [profile’s finite property grammar](../presentation-profile.md#css). Property-name escapes and alternate numeric spellings are rejected by that profile. Keyword and hash escapes are decoded before value matching. The filter emits fresh ASCII declarations and canonical accepted values; this is not a general CSSOM serializer.

## Implementation evidence and limits

Thirteen declaration-filter tests cover the selected values, preprocessing, escaping and recovery cases. Output is checked for idempotence. The enclosing HTML path still owns input limits; the standalone CSS helper supplies no parser-time resource guarantee.

A known tokenizer difference remains: tinycss2 1.4.0 admits NBSP within identifiers where the pinned draft treats it differently. The sampled values are rejected by the profile under either tokenization, but this does not establish tokenizer equivalence. No full CSS Syntax, browser cascade, layout, accessibility or sanitizer conformance is claimed.

Selected property definitions, inheritance, the client stylesheet and actual browser composition remain separate review obligations.
