---
title: MLS errata reconciliation
sectionNav: true
---

# MLS errata reconciliation

All five RFC9420 entries in the captured full RFC Editor corpus have been read, including their original text, proposed corrections and verifier notes. Statuses below describe that snapshot, not a newly checked live registry. The complete base text has also been read; section dispositions are recorded in the [base audit](mls.md); dependency closure remains unfinished.

| Erratum | Status | Disposition |
| --- | --- | --- |
| [8031](https://www.rfc-editor.org/errata/eid8031) | Verified, editorial | Capitalizes the sentence introducing original_sibling_tree_hash. No cryptographic behavior changes. |
| [8032](https://www.rfc-editor.org/errata/eid8032) | Rejected, technical | Retain D, not C, in the parent-hash resolution comparison. The verifier explains that the proposed replacement does not express the intended agreement about unmerged leaves. |
| [8211](https://www.rfc-editor.org/errata/eid8211) | Reported, editorial | Identifies the obsolete leaf_secret derivation in Section 7.4 and Figure 14. The preceding algorithm starts from freshly sampled path_secret[0]. Keep the inconsistency visible; do not treat the report as an approved correction. |
| [8745](https://www.rfc-editor.org/errata/eid8745) | Reported, technical | Proposes explicit capability compatibility checks when updating a leaf, as well as when adding one. Email/2 independently requires continued compatibility with group requirements; that application requirement does not imply this erratum is verified. |
| [8815](https://www.rfc-editor.org/errata/eid8815) | Reported, technical | Proposes explicit rejection of a commit referring to a proposal not previously received. Email/2 must resolve and validate referenced proposals before installing state; bounded delayed-dependency handling remains a profile decision. The proposal does not establish a new approved MLS rule. |

## Additional reconciliation work

The base reading identified issues not settled by these five entries: implicit default capabilities versus generic explicit-list checks; path-required checks stated differently across commit sections; stale field names in commit-creation prose; resynchronization advice mentioning a reinit PSK despite context restrictions; and the distinction between the referenced hash and KDF in hash-reference prose. These need reconciliation with current implementation behavior, applicable updates and protocol maintainers before claiming a complete interoperable binding.

Appendix D's illustrative linked-tree routines also need boundary handling before production use. Internal tree representation is not mandated by MLS, and copying those examples is not necessary for Email/2 conformance. The audit will not equate successful document compilation with cryptographic correctness.
