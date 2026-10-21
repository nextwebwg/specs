---
title: SMTP message tracking audit
sectionNav: true
---

# SMTP message tracking audit

**Coverage:** complete nine-page [RFC 3885](https://www.rfc-editor.org/rfc/rfc3885.html). No entries occur in the retrieved errata dataset. RFCs 3887 and 3888 and DSN dependencies remain open. Source inconsistencies below are audit observations, not accepted errata.

## Finding

Tracking retention, transport correlation and recipient disclosure are distinct concerns. Expiration of tracking information does not prove message loss. Tracking authorization must not spread automatically to every recipient produced by a list or alias expansion.

| Section | Disposition |
| --- | --- |
| 1 | Tracking queries are a last-resort mechanism dependent on3888 and3887; not presence or read receipts. The base64 production defines one alphabet character, creating a mismatch with later certifier syntax. |
| 2 | MTRK EHLO has no parameters; MAIL adds MTRK and requires ENVID support, while ORCPT remains a RCPT parameter. Command-length increases include the DSN extensions. No new SMTP verb. |
| 3 | Overview incorrectly groups ORCPT with MAIL parameters; use the explicit section2 RCPT placement and3461 contract, not a new MAIL ORCPT grammar. |
| 3.1 | Sender retains secret A and sends a hash certifier B; source describes128-bit SHA1 inconsistently. Retention is local-policy bounded, not a delivery deadline; queued messages retain tracking knowledge. Decrement lifetime across hops and remove expired MTRK. Literal certifier ABNF and Base64 padding need dependency reconciliation. |
| 3.2 | Tracking ENVID is globally nonreused and changes on user-agent resubmission, not ordinary in-system relay. Historical hashed-host encoding length is ambiguous about padding. Do not confuse ENVID with Message-ID or application event identity. |
| 3.3 | Forward unexpired tracking only to supporting peers; preserve DSN parameters on DSN-capable paths. Single-recipient redirection preserves identifiers; multi-recipient expansion permits at most one primary tracking path and lists prohibit propagation. Timeout cross-reference points incorrectly to4.1 rather than3.1. |
| 4 | Tracking has retention-resource and confidentiality concerns; it supplies no recipient encryption keys. |
| 4.1 | Database flooding can lead to shorter retention. Missing tracking knowledge is not evidence that delivery failed. |
| 4.2 | Protect unpredictable nonreused secrets, including in shared Sent stores. Operators may stop tracking at aliases to preserve identity and topology privacy. |
| 5 | Registers MTRK extension; no Email/2 registration or invisible message type. |
| 6 | Acknowledgements reviewed. |
| 7 | Reference classification reviewed; tracking dependencies remain open. |
| 7.1 | 3887 query and3888 model plus cryptographic/randomness dependencies require review before implementation; no SHA1 construction adopted for Email/2. |
| 7.2 | DSN3461 and modern MDN8098 remain pending; lifetime and randomness references identify additional dependencies. |
| 8 | Author addresses reviewed; no protocol semantics. |
| 9 | Copyright, warranty, IPR and funding end matter reviewed. |

| Front matter | Abstract, standards status and copyright notice reviewed. |

## Source inconsistencies

The text calls SHA-1 output 128 bits in section 3.1 but 160 bits in section 3.2. Its certifier ABNF names a production defined as a single alphabet character, while the prose requires an encoded hash. The 27-character host-hash example also requires reconciliation with ordinary padded Base64. Section 3 places ORCPT with MAIL in its overview despite the explicit RCPT placement in section 2. Section 3.3 points to the denial-of-service section for the timeout algorithm actually described in section 3.1.

These observations prevent treating the text as a ready-made new security profile. They do not justify changing the deployed MTRK wire format locally or claiming that a particular interpretation interoperates.

## Email/2 consequence

Keep tracking authorization and secrets out of public conversation metadata. Never use a tracking token as an encryption key or proof of authorship. Preserve the difference between a transport submission identifier, a message identifier and an application event identifier.

Do not infer group membership, a human recipient's presence, reading, decryption or response from tracking success. An unavailable or expired record leaves tracking knowledge unavailable. New rich receipt behavior requires a separately defined authenticated and privacy-aware contract.

Required cases include expiry before downstream relay, retention while locally queued, user-agent resubmission with a new envelope identifier, single-recipient forwarding, multi-recipient alias expansion, mailing-list expansion, and a shared mailbox exposing a tracking secret. No MTRK or MTQP implementation has been tested here.
