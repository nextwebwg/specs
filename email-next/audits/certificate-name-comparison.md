---
title: Certificate distinguished-name comparison audit
sectionNav: true
---

# Certificate distinguished-name comparison audit

Certificate chain names need their own comparison rules. They are neither mailbox identifiers nor HTTPS DNS names. Applying the experiment's Unicode 17 domain validator to a certificate distinguished name would select the wrong algorithm.

## What the certificate validator must compare

[RFC 5280 section 7.1](https://www.rfc-editor.org/rfc/rfc5280.html#section-7.1) requires support for UTF8String and PrintableString distinguished-name attributes and case-insensitive matching using [RFC 4518](https://www.rfc-editor.org/rfc/rfc4518.html). For the selected DirectoryString comparison, both sides are treated as stored values. Preparation consists of transcoding, mapping, Unicode 3.2 NFKC normalization, prohibited-character checks and insignificant-space handling. The bidi step adds no restriction in this profile.

Case folding uses the fixed Stringprep B.2 table, not ordinary lowercasing or the domain validator's current full-fold provider. NFKC can remove compatibility distinctions. Preparation failure does not establish a match. These transformations apply to comparison values; they do not rewrite signed certificate bytes or email content.

The insignificant-space rule is more precise than trimming arbitrary whitespace. Earlier mapping reduces selected separators to SPACE; a SPACE followed by combining marks is not an insignificant space under this rule. Stored values with content receive one leading/trailing space and two spaces for each internal run. An all-space value becomes two spaces. The specification's fixed combining-mark table controls this behavior.

Matching also preserves certificate structure: attribute types must match, each RDN must contain matching attributes, and the DN's RDN order matters. Directory-name subtree constraints compare the corresponding ordered prefix. A display string assembled by joining name components is not a substitute. Domain-component attributes have separate rules.

## Corrections and version boundaries

Five verified RFC 4518 errata were reviewed. [Erratum 860](https://errata.rfc-editor.org/eid860/) corrects the variation-selector deletion range to FE00–FE0F. Errata 1757 and 1758 correct the substring branch and its example; certificate comparison selects stored values instead. Errata 7213 and 9048 are editorial.

The selected Stringprep review covers mapping, normalization, prohibited categories, stored-value versioning and security definitions, including the reached C.3/C.4/C.5/C.8 tables. [Verified erratum 806](https://errata.rfc-editor.org/eid806/) clarifies that prohibition tables contain ranges as well as individual code points. Held erratum 4577 questions deletion of U+1806; it does not replace RFC 4518's explicit mapping rule. Held erratum 2686 is editorial.

RFC 3454 has been superseded by the PRECIS work, but RFC 4518's captured metadata lists no replacement or update. A newer general framework is not permission to substitute a different certificate comparison profile. The selected normalization source is [UAX 15 revision 22 for Unicode 3.2](https://www.unicode.org/reports/tr15/tr15-22.html), whose compatibility decomposition and canonical composition definitions were reviewed. This does not change the separate modern-domain baseline.

## Evidence and remaining work

The full RFC 4518 base text and its captured live errata were read. RFC 3454 and the older normalization source were reviewed only for the selected definitions described above; exact hashes and LF ranges are recorded privately. This scoped integration does not change aggregate audit counts.

The complete A.1/B.2 tables, selected Unicode 3.2 data definitions, composition exclusions, Hangul description and normalization corrigenda have now been reviewed. A separate structural inspection parsed all 13,874 UnicodeData rows and 1,371 B.2 mappings, checked decomposition targets and cycles, and confirmed A.1 against the expanded Unicode 3.2 repertoire. The 16,992 normalization test rows were subsequently executed against CPython 3.14.0’s explicit `unicodedata.ucd_3_2_0` reference API: all 339,840 listed NFC/NFD/NFKC/NFKD comparisons passed. The ambient Unicode 16 database was not used. Separate probes confirmed the incorporated FB1D/F951 corrections and the five older CJK outputs that precede Corrigendum 4. This is reference-library evidence, not OpenSSL, certificate matching or full normalization conformance: the additional unlisted-code-point identity sweep was not executed.

[Corrigenda 2](https://www.unicode.org/versions/corrigendum2.html) and [3](https://www.unicode.org/versions/corrigendum3.html) are incorporated in the captured 3.2 data. [Corrigendum 4](https://www.unicode.org/versions/corrigendum4.html) changes five CJK mappings in Unicode 4.0; a modern ambient normalizer cannot be assumed to reproduce the pinned profile. The old annex’s illustrative Hangul code is not adopted as an implementation. Backend testing must cover Hangul composition boundaries, compatibility mappings, prohibited/unassigned characters and the stored-value whitespace rules. No custom DN matcher was implemented. Existing TLS handshake tests do not establish that the configured TLS backend performs every required internationalized DN comparison or directory-name constraint correctly. Optional equality rules and legacy string encodings are not newly enabled by this audit.
