---
title: IDNA character and context rules
sectionNav: true
---

# IDNA character and context rules

[RFC5892](https://www.rfc-editor.org/rfc/rfc5892.html) defines which Unicode characters can participate in a domain label. A label made entirely of permitted characters still needs the [protocol's whole-label checks](idna-protocol.md), including NFC, hyphen placement and [bidi validation](idna-bidi.md).

## Preserve the order of the rules

The derived-property algorithm applies exceptions and compatibility overrides before its general character tests. Join controls receive contextual status before the rules that would otherwise reject them. Replacing this calculation with “letters and digits are allowed” loses required exclusions and exceptions.

The NFKC and case-fold operations in the character-stability test classify characters. They do not instruct a receiver to rewrite a domain label, an email local part or authenticated message bytes. Label NFC validation remains a separate requirement.

## Check context at each occurrence

Some characters are permitted only in specific surroundings. For example, a middle dot needs lowercase `l` on both sides; the Greek lower numeral sign needs a following Greek-script character. Hebrew geresh and gershayim need a preceding Hebrew-script character. Katakana middle dot needs another character with Hiragana, Katakana or Han script. Arabic-Indic and extended Arabic-Indic digit sets cannot be mixed.

Join controls have their own rules: ZWJ requires a preceding virama; ZWNJ permits that context or the specified joining-type context. Each occurrence must pass independently. An undefined boundary lookup does not establish validity. The correction in [RFC8753 §6](https://www.rfc-editor.org/rfc/rfc8753.html#section-6) prevents a valid occurrence elsewhere in the label from excusing an invalid one.

Registration and lookup have different contextual requirements, as described in the protocol audit. Email/2's full validated-label contract must not be weakened to whichever inputs a resolver happens to accept.

## Data that still needs a pinned validation profile

A complete validator needs consistent versions of general category, default-ignorable, whitespace, noncharacter, block, join-control, Hangul-syllable-type, canonical-combining-class, joining-type, script and bidi-class properties, together with normalization and case-fold definitions. The derived-property rules, contextual rules and applicable compatibility exceptions also need identified revisions.

The RFC's large Appendix B is an illustrative Unicode5.2 result, not a normative current table. The [Unicode review procedure](idna-unicode-review.md) explains how later versions are handled. This audit selects no IDNA data release and changes no runtime normalization or current experimental refusal of A-label hosts. [Punycode](punycode.md) and the [Unicode6](idna-unicode6.md)/[Unicode12](idna-unicode12.md) review records are reviewed separately. The selected Unicode normalization/property sources and any later applicable review decisions remain open.

## Coverage and source qualifications

The complete 70-page text, including every Appendix B table row, references and end matter, was read. The table was not recalculated and no validator tests were run. Metadata lists RFC8753 as its update; that complete source was reviewed separately.

Verified erratum3312 is the sole record in the captured and direct live full-record listing checked on 20 October 2026. RFC8753 incorporates it. The captured IANA context registry still prints the older ZWNJ expression while citing RFC8753; implementations must apply the published correction, including its per-occurrence requirement. This mismatch is not permission to relax validation.

Base-text SHA 256: `606dd3619e1d17b3625ef323ac44b0aad272712d067692185d1e417416b66c70`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
