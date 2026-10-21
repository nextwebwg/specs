---
title: Authenticated encryption interface
sectionNav: true
---

# Authenticated encryption interface

[RFC5116](https://www.rfc-editor.org/rfc/rfc5116.html) defines the AEAD interface used by the [selected HPKE and MLS suite](../security-profile.md). Associated data is authenticated but remains readable. Successful decryption establishes integrity under a key; it does not establish mailbox ownership, access authorization or replay protection.

## Consequences for Email/2

An authenticated decrypt operation returns plaintext or failure. Invalid lengths and authentication failures must not expose partially decrypted data. Structured associated data and plaintext must have an unambiguous interpretation that does not depend on unauthenticated parsing information. The enclosing MLS and application encodings remain authoritative.

Each encryption invocation needs a nonce unique for its key. Sharing a key across devices, restarting a process or restoring old state must not repeat nonce use. Section 3.1's checkpoint guidance requires preserving future nonce state before using the corresponding range. Section 8 explicitly identifies virtual-machine rollback as a risk; existing local crash tests do not prove resistance to restoring an old database or machine snapshot.

The generic interface permits zero-length nonces only for algorithms designed to support them. This is not an escape from the selected AES-GCM requirements. Keep the nonce derivation of MLS and HPKE rather than replacing it with the document's illustrative fixed/counter format. Retransmitting retained ciphertext and attempting decryption again are distinct from performing another encryption with a reused nonce.

The selected AES-128-GCM interface uses a 16-byte key, a 12-byte nonce and a 16-byte authentication tag appended to the ciphertext. A repeated encryption nonce/key can expose plaintext relationships and undermine authentication under that key. AES-256-GCM and both CCM definitions were reviewed without adding them to the selected MLS suite.

## Coverage and corrections

The complete 22-page source, including both nonce diagrams, the ESP example, all algorithm definitions, references and final legal text, was read. Exact ranges and dispositions appear in the [section ledger](section-ledger.json). This review executed no cryptographic vectors.

The [live errata listing](https://errata.rfc-editor.org/search/?rfc_number=5116) matches the six captured records:

| Erratum | Status | Disposition |
| --- | --- | --- |
| [4008](https://www.rfc-editor.org/errata/eid4008) | Verified | Decryption's descriptive input list names ciphertext C, not plaintext P. |
| [4268](https://www.rfc-editor.org/errata/eid4268) | Verified | Clarifies saving the next nonce range before using it; the example does not permit reuse. |
| [4338](https://www.rfc-editor.org/errata/eid4338) | Reported | Proposes changing the partially implicit nonce diagram and ESP explanation; not adopted as a correction. |
| [5219](https://www.rfc-editor.org/errata/eid5219) | Reported | Flags a one-byte discrepancy in the GCM plaintext maximum against SP800-38D. The [GCM source review](gcm.md#limits-and-nonce-lifecycle) records the primitive maximum of 2³⁶−32 octets; this reported erratum remains unverified. |
| [5233](https://www.rfc-editor.org/errata/eid5233) | Reported | Proposes changing CCM tag overhead; not adopted. CCM is outside the selected suite. |
| [6415](https://www.rfc-editor.org/errata/eid6415) | Reported | Proposes changing the recommended counter/fixed-field sizes; not adopted. |

## Evidence and remaining scope

The captured metadata identifies Proposed Standard status and lists no updates or successors. It gives February 2008 as publication date; the source header says January 2008. Both snapshots are retained without normalizing away that difference. The 1,235-line source SHA-256 is `8762fee7c85e682fce609c75e0f5040ee7efa8fca96969ffd85df37585e0eda1`.

The selected SP800-38D primitive is covered by the [GCM audit](gcm.md). This interface review does not certify its implementation, key generation, key lifecycle, side-channel behavior or durable nonce handling. CCM and ESP material does not make those protocols implementation requirements. Registry registration is not security endorsement, and live registry reconciliation is separate from this base-source review.
