---
title: IDNA Unicode 12 review
sectionNav: true
---

# IDNA Unicode 12 review

[RFC9233](https://www.rfc-editor.org/rfc/rfc9233.html) reviews changes from Unicode6 through Unicode12 and adds no compatibility exceptions to IDNA2008. It does not establish the behavior of later Unicode versions or choose a data version for Email Next.

## Preserve the distinction between validity and appearance

U+111C9 Sharada sandhi mark became PVALID after its category changed to a nonspacing mark. The IETF accepted that change without a backward-compatibility exception. Other property changes, including those affecting existing Georgian letters, did not change their derived IDNA status.

The review also accepts U+08A1 without an exception while acknowledging unresolved issues around visually similar combining sequences. Visual resemblance does not establish canonical equivalence. A client must not invent a mapping between such sequences.

The deployment discussion describes several incompatible approaches. It does not select IDNA2003, Nameprep or UTS46 for Email Next. RFC5895 remains optional mapping advice. Later Unicode changes follow the [separate review procedure](idna-unicode-review.md); data consistency and whole-label validation remain required.

## Evidence and remaining scope

The complete 1321-line source was reviewed, including every change-table row in appendices A–F, references and end matter. No table was independently recalculated. Retrieved metadata lists no update or replacement; the direct live errata listing contained no records on 20 October 2026.

Together with [RFC6452](idna-unicode6.md), this closes the two review records cited by the captured IANA Unicode12 registry. It does not close the selected Unicode normalization, case-folding, property-file or later-version provenance work. The experimental A-label restriction remains unchanged.

Base-text SHA 256: `cf3f2a3d2aefb37acff9434cdc3b1ca9317d7dc3d8867a821e656b9ce11063e1`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
