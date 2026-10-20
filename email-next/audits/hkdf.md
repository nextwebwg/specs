---
title: HKDF key derivation
sectionNav: true
---

# HKDF key derivation

[RFC5869](https://www.rfc-editor.org/rfc/rfc5869.html) defines the extract-and-expand key derivation used by the [selected HPKE and MLS suite](../security-profile.md). Email Next preserves those protocols' key schedules, labels and context inputs. The general HKDF interface does not authorize changing a salt, skipping a stage or substituting a different hash in an existing protocol.

## Consequences for implementations

Extract computes HMAC with the salt as its key and the input keying material as its message. If the salt is omitted, the definition substitutes HashLen zero octets. Expand takes a pseudorandom key of at least HashLen octets, binds the `info` input and produces at most 255 × HashLen output octets. For SHA-256 this is 8,160 octets per Expand call; it is an algorithm limit, not an Email Next message-size limit.

Preserve the exact labels and encoded context selected by MLS and HPKE. The generic interface permits empty `info`, but removing context from a protocol that defines it would change that protocol's key derivation. The source advises against skipping extraction for a Diffie–Hellman value and against using the extraction result directly as output when that would omit expansion's context binding.

HKDF concentrates existing entropy; it cannot create entropy or provide the deliberate computational slowdown used to resist password guessing. This profile does not select HKDF as a password-hardening mechanism. Salt independence, key-material quality and authenticated key exchange remain assumptions of the enclosing construction, not guarantees obtained by calling a KDF.

## Coverage and errata

The complete 14-page source was read, including both stages' formulas, all usage guidance, references, all seven Appendix A vectors and both author addresses. The [section ledger](section-ledger.json) records exact ranges and dispositions.

The SHA-256 vectors cover basic inputs, longer inputs/outputs and empty salt/context. The SHA-1 vectors and omitted-salt case were also read; this does not select SHA-1. The source review itself did not execute the vectors. The separate [known-answer harness](../evidence/hkdf-vectors.md) subsequently reproduced all seven using cryptography 50.0.2, with exact fixture reproduction from the pinned source. That harness does not exercise the selected OpenMLS implementation.

The [live errata listing](https://errata.rfc-editor.org/search/?rfc_number=5869) matches the single captured record, [5161](https://www.rfc-editor.org/errata/eid5161), which remains Reported. It proposes spelling out the counter octet's value. It is not a verified correction and does not permit expansion beyond the existing 255-block limit or counter wraparound.

## Evidence and remaining scope

The captured metadata identifies Informational status, publication in May 2010, and no listed updates or successors. The 787-line text SHA-256 is `7a40eb3835b35fc947eb12a2ed614db079d43b26e50dbc537c31fba16397089c`. Snapshot lengths and metadata digest are retained in the [source inventory](source-inventory.json).

HMAC and the selected secure hash remain primitive dependencies; the source's FIPS180-3 reference requires current-source reconciliation. Informative examples of IKE, PANA and password-based derivation do not make those protocols part of Email Next. This review does not certify library correctness, side-channel behavior, entropy sources, independent interoperability or complete cryptographic dependency coverage.
