---
title: IDNA bidirectional labels
sectionNav: true
---

# IDNA bidirectional labels

[RFC5893](https://www.rfc-editor.org/rfc/rfc5893.html) adds directionality checks to domain validation. These checks operate on Unicode properties in network order. They do not reorder the stored identifier or replace the separate display rules for message text.

## Validate the domain context

An RTL label contains a character with bidi class R, AL or AN. A domain containing any such label is a bidi domain. The rule then considers its LTR and ASCII labels too; checking only the visibly right-to-left label misses part of the requirement. This does not impose a new leading-digit ban on ordinary ASCII-only domain names.

For a label to satisfy the rule, its first character determines its direction: L for LTR, R or AL for RTL. Each direction permits a defined set of classes and has a required ending, optionally followed by nonspacing marks. An RTL label cannot mix EN and AN numeric classes. Final combining marks are therefore possible without accepting arbitrary starting or ending punctuation.

These checks complement, rather than replace, character validity and contextual rules. They do not prevent every mixture of scripts or digit systems, guarantee visual uniqueness across different surrounding directions, or preserve the displayed order of domain labels. Security comparisons and hashes use network order, never screen order.

## Coverage and limits

Only sections1.4 and2 are normative. The complete 17-page source was nevertheless read, including the Dhivehi, Yiddish and numeric examples, compatibility discussion, references and end matter. No example was executed as a test. The source describes limitations around digit-leading ASCII neighbors, piecemeal domain construction and display context; this audit does not turn those observations into a universal domain prohibition.

Retrieved metadata lists no update or replacement. The direct live errata listing contained no records on 20 October 2026. The selected Unicode Bidi_Class data and relevant Unicode Bidirectional Algorithm revision still need explicit provenance. Reading the RFC's Unicode5.2 references does not select that release for Email Next or complete the Unicode source review. The experimental A-label restriction remains unchanged.

Base-text SHA 256: `d7daca034781d7f43c24f28c229aaba5aecbb76a68a6a59b70a5505adc23f42d`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
