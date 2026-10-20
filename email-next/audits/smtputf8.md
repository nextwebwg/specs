---
title: SMTPUTF8 transport audit
sectionNav: true
---

# SMTPUTF8 transport audit

SMTPUTF8 is useful prior art for an incremental server upgrade: a peer advertises support, a transaction explicitly uses it, and unsupported downstream delivery can still fail. It is not evidence that a recipient supports rich content or encryption.

**Coverage:** all eighteen pages of RFC6531 and both retrieved errata read and individually assessed on 19 October 2026. A truncated initial tool output was supplemented by rereading the omitted §§3.5–3.6 and surrounding text. Framework, status notifications, DNS and current registry dependencies remain open.

Sources: [RFC6531](https://www.rfc-editor.org/rfc/rfc6531.html), [errata](https://www.rfc-editor.org/errata/rfc6531).

| Section | Disposition |
| --- | --- |
| 1 | Scope and required framework understanding reviewed. |
| 1.1 | UTF-8 and ABNF terminology inherited; non-ASCII is not arbitrary8bit bytes. |
| 1.2 | Extension of base syntax, not unconditional replacement. Requires8BITMIME advertisement; body-mode selection qualified by3.6. Replaces5336. |
| 2 | SMTPUTF8 token identifies internationalized transport, not rich interactions or encryption. |
| 3 | Transport framework reviewed. |
| 3.1 | All11items reviewed: valueless EHLO/MAIL/VRFY/EXPN tokens, unknown EHLO parameters ignored, MAIL line allowance+10,8BITMIME requirement, envelope/header extension, submission/LMTP applicability. No new SMTP verbs. |
| 3.2 | Negotiate before sending. Local-part delimiters unchanged; DNS uses IDNA processing. No unsupported UTF-8 envelope/headers. MSA transformations are source-permitted but outside its scope; relay rejection/DSN or justified retry/alternateMX apply. DSN advertisement entails6533. |
| 3.3 | Extend sub-domain with U-label, atext/qtextSMTP/esmtp-value with valid UTF8-non-ascii. Verified7580 corrects extends wording. Held4996 is not adopted; do not prohibit the UTF-8 octets the grammar permits. |
| 3.4 | Supply MAIL SMTPUTF8 when needed, no value; omit when known unnecessary. Hop advertisement does not promise downstream support. |
| 3.5 | Address failures use550 MAIL/553 RCPT withX.6.7; end-DATA UTF-8 header failure uses554/X.6.9 in prose. Prefer early RCPT detection. Registry table4.2 lists550 forX.6.9; RFC5248 makes basic-code associations non-exclusive, so this does not contradict the explicit554 rule. |
| 3.6 | Parameter presence is not proof message contains non-ASCII; accurate classification requires headers at all MIME levels. BODY mode reflects content and advertised8BITMIME/BINARYMIME capabilities. |
| 3.7 | Mailbox/domain contexts reviewed; domain representation does not authorize local-part rewriting. |
| 3.7.1 | EHLO domain and response domains remain ASCII LDH/A-label, before support is known. |
| 3.7.2 | Uniform support across MX hosts recommended; mixed support can cause route-specific failures. |
| 3.7.3 | Trace formatting follows transaction use, not merely server capability. Registered WITH values record protocol use, not end-to-end security. |
| 3.7.4 | UTF-8 reply permission is scoped to stated commands and conditions. |
| 3.7.4.1 | MAIL SMTPUTF8 permits internationalized251/551 addresses; without it use ASCII250/550 alternative replies. |
| 3.7.4.2 | VRFY/EXPN parameter grants UTF-8 reply permission for that command only. Without permission use252/550 andX.6.8 where applicable. No general localized SMTP reply permission. |
| 4 | Registration material reviewed; current registry snapshot reconciliation remains open. |
| 4.1 | SMTPUTF8 keyword registration inherited. |
| 4.2 | X.6.7/.8/.9 reviewed;X.6.10 duplicate deprecated. Basic-code associations are non-exclusive under RFC5248. |
| 4.3 | All8SMTP/LMTP WITH variants reviewed; AUTH and STARTTLS records are not recipient-device cryptographic evidence. |
| 5 | Unicode-safe logs and incident investigation required; logging representations must preserve identity without silent truncation. Ownership tooling requirement does not supply a key-discovery protocol. |
| 6 | Acknowledgements reviewed; no protocol behavior. |
| 7 | References reviewed. |
| 7.1 | Normative dependencies including6530/6533,IDNA,DSN,submission and8BITMIME tracked separately. |
| 7.2 | Informative LMTP/BINARYMIME/TLS/AUTH/history dependencies tracked separately. |
| Authors and front matter | Contact, abstract, status and copyright reviewed; no additional wire requirement. |

## Errata and reply-code interpretation

[7580](https://www.rfc-editor.org/errata/eid7580) is Verified: the specification extends grammar when negotiated; it does not formally update RFC5321 for every transaction. [4996](https://www.rfc-editor.org/errata/eid4996) is Held for Document Update. Its proposed replacement concerning “Extended ASCII” is not adopted; valid UTF-8 grammar remains controlling.

Section 3.5 specifies `554` for rejection after DATA because a recipient cannot process UTF-8 headers. The X.6.9 registration table lists `550` as an associated basic code. [RFC 5248 §2.1](https://www.rfc-editor.org/rfc/rfc5248.html#section-2.1) explicitly makes these associations non-exclusive, so that table does not contradict or replace the protocol's `554` requirement. Server generation follows §3.5. A sending client preserves either received permanent-failure diagnostic without using it as permission for an unprotected retry. No standards clarification is required merely to reconcile this non-exclusive association. See the [registry audit](status-registry.md).

## Proposed transport decisions

Track SMTPUTF8 separately from recipient rich-content and encryption support. A failed UTF-8 route preserves the prepared delivery's confidentiality policy. An alternateMX attempt must negotiate independently and must not remove encryption or transliterate the mailbox.

A submission service can offer a transformed compatible message only when it has an explicitly established alternative address and can produce a valid delivery under the sender's policy. The original protected contribution must not be silently modified. The source's broad MSA latitude is not proof that arbitrary transformations preserve meaning or signatures.

Acceptance cases include SMTPUTF8 absent, present with ignored EHLO parameters, MAIL token with an invalid value, mixed-capabilityMX hosts, ASCII-only message without unnecessary token, non-ASCII MIME-part headers, transaction-scoped trace/reply behavior, and permanent post-DATA rejection with no application effect. These cases remain to be implemented.

## Command length reconciliation

The [registry cleanup draft audit](registry-cleanup.md) distinguishes SMTPUTF8's actual nine-octet addition (one space and the eight-character valueless token) from RFC 6531 §3.1's published ten-character increase in the MAIL command limit. Measure the complete encoded command, including CRLF and UTF-8 address octets. Do not treat a proposed registry correction as permission to reject a command that fits the applicable published allowance. This calculation does not establish the interaction of every simultaneously negotiated extension.
