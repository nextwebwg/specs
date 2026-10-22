---
title: Hybrid public-key encryption
sectionNav: true
---

# Hybrid public-key encryption

[HPKE](https://www.rfc-editor.org/rfc/rfc9180.html) supplies the public-key encryption component used by the [selected MLS suite](../security-profile.md). Email/2 retains MLS's algorithm selection, Base-mode use and context binding. The [sealed-control layer](../suite-profile.md#confidential-setup-and-control) additionally selects RFC9180 single-shot Base encryption for setup metadata, with a separate key, fixed algorithm IDs and domain-separated info/aad. It does not change MLS packets or reuse MLS initialization keys for that layer. Base-mode encryption does not authenticate the sender or establish mailbox ownership; accepted device bindings, message authentication and group admission remain separate checks.

## Consequences for implementations

Preserve the library's input validation, key serialization, labeled key derivation, nonce sequencing and failure handling. A decryption failure does not authorize a plaintext retry. Application context must retain its defined binding; the application `info` parameter is distinct from the internal inputs to labeled expansion.

HPKE alone does not supply message ordering, loss recovery, replay protection or downgrade prevention. It does not provide forward secrecy against compromise of the recipient's private key. Email/2 relies on its selected MLS construction and durable application state for the applicable group and message guarantees. Its separate control container requires an accepted Ed25519 signed intent, original owning signatures and atomic replay/admission rules; HPKE alone supplies none of those authorities. The retained control key does not acquire MLS forward-secrecy guarantees. The selected suite is not post-quantum.

Auth and AuthPSK modes, alternative curves and AEADs, and export-only operation appear in the source. Their presence does not add them to the Email/2 profile. In particular, export-only operation does not encrypt email content.

## Integer and byte conversions

HPKE imports I2OSP and OS2IP from [RFC8017 section 4](https://www.rfc-editor.org/rfc/rfc8017.html#section-4). I2OSP produces exactly the requested number of bytes, most significant first, retaining leading zero bytes. An integer that does not fit is an error; truncation is not permitted. OS2IP interprets the bytes in the same order as a nonnegative integer. Protocol-defined lengths remain separate validation requirements.

This dependency selects conversion rules, not RSA encryption or signatures for the MLS suite. The selected review covers sections 4–4.2 and six captured errata; none of those captured corrections changes section 4. It is not a complete RFC8017 audit, a live errata completeness check or validation of a library implementation. Other profiles that use RSA require their own review.

## Reviewed coverage

The complete captured base text was reviewed, including all references, every Appendix A setup/encryption/export vector and the final backmatter. The [section ledger](section-ledger.json) records exact source ranges and their dispositions.

| Source | Disposition |
| --- | --- |
| Sections 1–3 | Scope, requirement language and notation |
| Section 4, including 4.1 | Primitive contracts and DHKEM |
| Section 5, including every 5.1–5.3 subsection | All four modes, contexts, encryption/decryption and export |
| Section 6 | Single-shot APIs; no implied replay protection |
| Section 7, including every 7.1–7.3 subsection | Identifiers, serialization, derivation, validation and length restrictions |
| Section 8 | Authenticated application information and errors |
| Section 9, including every 9.1–9.9 subsection | Security assumptions, guarantees and explicit non-goals |
| Sections 10–12 | Encoding, registries and both reference lists |
| Appendix A.1–A.6 | All mode setups, encryption results and exported values across the listed suites |
| Appendix A.7 | All export-only mode setups and exported values |
| End matter | Acknowledgements and author addresses |

The vectors were read, not executed or independently recomputed. Their encryption examples include sequence numbers 0, 1, 2, 4, 255 and 256. A harness must preserve the actual context sequencing. Export examples distinguish an empty context, one zero octet and `TestContext`.

## Captured errata

Eight captured records were reviewed: six Verified and two Held for Document Update. The live all-status listing checked on 20 October 2026 matches their IDs, statuses and full original/corrected text and notes.

| Erratum | Captured status | Consequence |
| --- | --- | --- |
| [7121](https://www.rfc-editor.org/errata/eid7121) | Verified | Correct the serialized X25519 private-key bytes in A.1, A.2 and A.7 to apply required clamping. Public keys are unchanged. Preserve the original source snapshot and apply the correction explicitly in fixtures. |
| [6941](https://www.rfc-editor.org/errata/eid6941) | Verified | Single-shot API text refers to all of Section 5.1, not only Base mode. |
| [7251](https://www.rfc-editor.org/errata/eid7251) | Held for Document Update | Recommends reconciling the 64-byte input recommendation with the P-521 vectors' 66-byte inputs. This is not a verified amendment or a requirement to support P-521. |
| [7790](https://www.rfc-editor.org/errata/eid7790) | Verified | Auth-mode analysis does not establish Insider-Auth security. Preserve this limitation in security claims. |
| [7932](https://www.rfc-editor.org/errata/eid7932) | Verified | Corrects the direction of a pseudocode reference. |
| [7933](https://www.rfc-editor.org/errata/eid7933) | Held for Document Update | Clarifies the initial sequence number in the context. It does not permit nonce reuse. |
| [7934](https://www.rfc-editor.org/errata/eid7934) | Verified | Distinguishes HPKE's application `info` parameter from internal expansion inputs. |
| [7937](https://www.rfc-editor.org/errata/eid7937) | Verified | Clarifies the KEM-derived suite identifier in key-pair derivation. |

## Evidence and limits

The captured metadata identifies RFC9180 as Informational, published February 2022, with no listed updates or replacements. The retained 4,810-line text has SHA-256 `f45a8b7c30231b26d668b1e8168074e5ab514b174d656b67e859895117f1f8f6`; text and metadata byte lengths and digests are in the [source inventory](source-inventory.json).

This is a base-document review, not certification of the cryptographic library, execution of its known-answer vectors, independent interoperability or primitive-dependency closure. The selected HPKE registry entries are reconciled in the [MLS audit](mls.md); other entries and independent implementation evidence remain separate. The existing MLS exchange tests do not substitute for executing the HPKE vector suite.
