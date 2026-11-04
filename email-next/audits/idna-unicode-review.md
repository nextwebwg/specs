---
title: IDNA Unicode version review
sectionNav: true
---

# IDNA Unicode version review

[RFC8753](https://www.rfc-editor.org/rfc/rfc8753.html) clarifies how IDNA handles new Unicode versions. It distinguishes the normative calculation and contextual rules from IANA's convenient derived tables. An older published table does not, by itself, prohibit use of a later Unicode version.

## Use a consistent data version

Derived properties must correspond to the Unicode version used for the other relevant application or library checks. Copying one release's allowed-character table while using another release's normalization or bidi data does not establish that consistency.

New major Unicode versions normally receive two reviews: an algorithmic comparison with earlier derived properties, and an expert-team analysis of new or problematic characters. Characters marked under review remain unsafe pending resolution. The default is to preserve existing validity through exceptions unless strong evidence supports a change; incompatible later decisions need their own Standards Track record.

These are standards-maintenance duties, not authority for an application to invent exceptions. Registry operators also retain responsibility for narrower registration policies. Client validation does not guarantee that a name can be registered or that its holder owns any mailbox.

## Apply the contextual correction

Section6 incorporates verified erratum3312 for RFC5892. Every occurrence of a contextual character must independently satisfy its rule. The ZWNJ expression must refer to the particular occurrence being checked. This correction is part of validation even when a copied registry expression still uses the earlier wording.

## Evidence and remaining scope

The complete 697-line source, both appendices, references and end matter were reviewed. Retrieved metadata lists an update to RFC5892 and no later update or replacement. The direct live errata listing contained no records on 20 October 2026.

The captured [IANA registry](https://www.iana.org/assignments/idna-tables) redirects to its Unicode12.0.0 edition and cites RFC6452 and RFC9233 alongside RFC5892/RFC8753. Its maintenance timestamp is 26 April 2024. The additional records are reviewed in [Unicode6](idna-unicode6.md) and [Unicode12](idna-unicode12.md); Email/2 selects coherent Unicode17 data, as specified in [mailbox addresses](../mailbox-addresses.md) and exercised by the [configured provider](../evidence/IDNA17.md). The older IANA table does not impose a Unicode12 ceiling. Formal standards-maintenance review of later new characters remains distinct from the implemented derivation and validation rules. The registry's derived table was not independently recalculated. Its contextual entries were inspected, including the ZWNJ source discrepancy described in the [character-rules audit](idna-properties.md).

Base-text SHA 256: `0a84789569881678418a507a3952379d7c60f2cfc9fc0e40d2d958e983a6ecc4`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
