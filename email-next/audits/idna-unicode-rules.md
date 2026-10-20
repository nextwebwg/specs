---
title: Unicode rules for domain validation
sectionNav: true
---

# Unicode rules for domain validation

A valid internationalized domain label depends on more than Punycode decoding. Its validator needs consistent normalization, case-folding and character-property data. This review explains those dependencies. The [configured experimental provider](../evidence/IDNA17.md) applies them to domain validation; it does not change authenticated message bytes.

## Normalization has a specific purpose

The [IDNA protocol](idna-protocol.md) requires a Unicode label to be in NFC. NFC recursively applies canonical decomposition, orders combining characters, then composes eligible pairs. Composition must account for exclusions, intervening characters and Hangul's arithmetic mappings. Comparing a label with its normalized result is different from silently rewriting an authenticated identifier. [Unicode17 Core§3.7,§3.11 and§3.12](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)

The [IDNA property derivation](idna-properties.md) separately tests whether NFKC, default full case folding, and NFKC again change a character. Default full folding uses the common and full mappings in `CaseFolding.txt`; it is neither simple lowercasing nor locale-sensitive casing. `NFKC_Casefold` is a different operation that also removes default-ignorable characters. It cannot replace the specified sequence. [Core§3.13.3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)

These rules do not select normalization for message text, mailbox local parts, signatures or event serialization. Domain validation remains a separate operation.

## Combining marks and shortcuts

A combining mark can have combining class zero. Consequently, the prohibition on a leading combining mark cannot be implemented by testing only for a nonzero combining class. General category `M` includes `Mn`, `Mc` and `Me`; a normalization “starter” is instead any code point whose combining class is zero. [Core§3.6.1 and§3.11.2–4](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/)

Normalization quick checks are optimizations, not replacements for the full rules. A “maybe” result requires further checking, and canonical ordering must also be checked. Normalized pieces do not necessarily remain normalized after concatenation. [UAX15 revision57,§1.4 and§9](https://www.unicode.org/reports/tr15/tr15-57.html)

## Read property data with its defaults

A property loader must preserve the versioned data's meaning, including omitted values:

- `UnicodeData.txt` uses paired `First` and `Last` records for ranges.
- Derived property listings take precedence over explanatory derivation comments.
- `@missing` records define defaults; later records can override earlier defaults for narrower ranges.
- `DerivedJoiningType.txt` supplies definitive joining values. Omitted entries in `ArabicShaping.txt` cannot all be treated as nonjoining.
- Bidirectional-class defaults vary by range. A single default for every omitted code point is insufficient.

Property aliases identify properties and values; their matching conventions do not authorize loose matching of Email Next identifiers. [UAX44 revision36,§2.1,§4.2 and§5.8](https://www.unicode.org/reports/tr44/tr44-36.html)

## Direction and joining are validation inputs

IDNA applies the [RFC5893 label conditions](idna-bidi.md) to character properties. It does not first run display reordering and validate the displayed result. `Bidi_Class` comes from normative per-character data; the category summaries have exceptions, so general category alone cannot reconstruct it. [UAX9 revision51,§3.2](https://www.unicode.org/reports/tr9/tr9-51.html)

Joining types describe cursive connections. Their left/right names refer to visual joining, while the IDNA contextual tests still inspect the specified code-point positions. ZWJ's join-causing value and ZWNJ's nonjoining value do not replace their contextual restrictions. [Unicode17 Core§9.2](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-9/)

The selected properties also retain their individual meanings: `Script` is distinct from `Script_Extensions`, and `White_Space` is distinct from segmentation-specific space classes. A validator must use the property named by IDNA. [UAX44 revision36,§5.3](https://www.unicode.org/reports/tr44/tr44-36.html)

Script assigns one property value to each code point. Its `Common` and `Inherited` values do not authorize an IDNA validator to substitute a surrounding script; text-run inheritance is a separate use. Unlisted Script values default to `Unknown`. [UAX24 revision39,§2 and§4](https://www.unicode.org/reports/tr24/tr24-39.html)

## Later IDNA reviews remain work in progress

[draft-faltstrom-unicode-18-04](https://datatracker.ietf.org/doc/draft-faltstrom-unicode-18/04/) is an active individual Internet-Draft covering Unicode12 through18. It proposes temporary review markings and different handling when creating and receiving labels. These proposals are not adopted here. The earlier [Unicode15 draft](https://datatracker.ietf.org/doc/draft-faltstrom-unicode-15/) is expired. Neither record establishes a published post12 rule change or completed review of every affected character. The18 draft separates its algorithmic comparison from the still-needed per-character examination. An unchanged derived classification does not by itself resolve visual-equivalence concerns.

## Coverage and remaining work

This is a selected review of Unicode17 Core combining, decomposition, normalization, Hangul arithmetic and default case-folding definitions; UAX15 revision57 normalization, stability, conformance and quick-check text; UAX44 revision36 data formats, defaults, aliases, selected property entries and test-data semantics; UAX9 revision51 bidirectional-class definitions; Core§9.2 joining-type definitions; and selected UAX24 revision39 Script definitions and data-file rules. Exact source hashes and reading ranges are retained privately. Illustrative graphics and the full annexes are not claimed as reviewed. No normalization vectors or IDNA property tables were executed or regenerated.

The versioned annexes identify approved stable publications, and the versioned UCD identifies final data. The version landing pages contain inconsistent preliminary-status text. The [current errata list](https://www.unicode.org/errata/), [corrections recorded after Unicode17](https://www.unicode.org/versions/Unicode18.0.0/erratafixed.html), and [corrigenda table](https://www.unicode.org/versions/corrigenda.html) identify no correction to the selected17 rules; the three recorded post17 corrections concern representative glyphs.

Unicode17 is the source pin for this review, not a selected runtime IDNA version. The remaining work includes full pinned property-data validation, resolution of applicable IDNA reviews after Unicode12, and evidence that an implementation's normalization, folding and property providers use a coherent version. The property-file review covers joining, bidi and case-folding headers/defaults, not every data row. The later IDNA draft review covers status and selected policy sections, not its complete tables or calculations. The [Unicode12 review](idna-unicode12.md) does not establish those later reviews.
