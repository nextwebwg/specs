---
title: Automatic responses audit
sectionNav: true
---

# Automatic responses audit

**Coverage:** full 22-page RFC3834, including examples, references and end matter; verified technical erratum223 reviewed in the refreshed RFC Editor dataset on19October2026. The [RFC5436 review](sieve-notifications.md) records the keyword registration update and live registry check; other dependencies remain open. [RFC3834](https://www.rfc-editor.org/rfc/rfc3834.html); [erratum223](https://www.rfc-editor.org/errata/eid223).

| Section | Disposition |
| --- | --- |
| 1 | Loop, amplification and unwanted-response problem applies directly to automatic discovery. |
| 1.1 | Distinguish service, personal and group responders. Email/2 negotiation requires a precisely defined service exchange, not vacation-responder heuristics. |
| 1.2 | Requirement terms and subject-message/response/recipient definitions retained. |
| 2 | Never answer every message. Suppress automatic traffic, null destinations and malformed requests; bound responses and avoid unauthenticated side effects. Seven-day advice concerns absence notices, not a universal protocol timer. Recipient-header heuristic is not reliable evidence of Bcc membership. |
| 3 | Header, body and envelope requirements apply independently. |
| 3.1 | Response headers identify the responder and causal message without authenticating either. |
| 3.1.1 | Use a configured public identity; do not derive or disclose login names, internal hosts or private aliases. Provide an operator contact appropriate to responder type. |
| 3.1.2 | Reply-To can designate an expected service reply, but requires loop prevention; it is not generic authorization to send automatic replies. |
| 3.1.3 | Single response recipient limits amplification. Never negotiate by reply-all. |
| 3.1.4 | Response Date is generation time, not subject delivery time or evidence of online presence. |
| 3.1.5 | Auto: is a human hint, not a protocol detector. Preserve encoded-word boundaries and header line limits. |
| 3.1.6 | Generate causal reply headers from Message-ID under message-format rules; these do not establish authenticated event identity. |
| 3.1.7 | Automatic direct responses carry Auto-Submitted: auto-replied. |
| 3.1.8 | Precedence is nonstandard and cannot ensure suppression or invisibility. |
| 3.2 | Keep personal/group replies short and readable; do not reflect attachments or substantial attacker content. Service payloads need their own bounded format. |
| 3.2.1 | DSNs describe delivery and MDNs disposition. Neither is a camouflage format for key exchange. |
| 3.3 | Use a loop-safe envelope, including a null reverse-path where applicable; request NOTIFY=NEVER only when DSN is supported. Suppression does not confirm delivery. |
| 4 | Generic post-delivery replies use Return-Path; pre-delivery replies use envelope reverse-path. Service-specific alternative destinations require precise specification. Do not fall back to From, Reply-To or Sender heuristics. Verified erratum223 removes accidental > before From. |
| 5 | Auto-Submitted marks automatic origin and supports filtering; it grants no deletion, hidden-delivery or authentication semantics. |
| 5.1 | At most one field; parse optional parameters and CFWS under referenced grammars. Conflicting duplicates are unsuitable for automatic activation. |
| 5.2 | Distinguish auto-generated initiation from auto-replied response and human-originated no. Unknown non-no keywords still indicate automation. Valid optional parameters must not break recognition. Experimental x- names require consenting parties; registration rules need successor review. |
| 6 | Address forgery, reflection, loops, address enumeration, activity disclosure and responder resource exhaustion remain threats. Header labels alone do not solve them. |
| 7 | Vacation example is informative. Its seven-day interval and blanket field-presence suppression are example policy, not universal negotiation rules. |
| 8 | Extension registration mechanism reviewed; RFC5436 update and current registries remain pending. |
| 9 | Historical attribution reviewed; no additional wire requirements. |
| 10 | References reviewed for dependency mapping; full dependency closure not claimed. |
| 10.1 | 2822 superseded by5322;2234 by5234;2434 ultimately8126. MIME2045/2047/2231 reviewed;3461 DSN and requirement-language dependencies remain open. |
| 10.2 | DSN3464, MDN3798 successor8098 and mailing-list2369 require separate audits. Historical gateways and common-header catalog do not define new negotiation authority. |

| Front and end matter | Status, abstract, copyright, intellectual-property notice and author information reviewed; no additional message behavior. |

## Consequence for Email/2

Ordinary messages can advertise capabilities without triggering a reply. A standalone automatic negotiation response requires a service protocol with a validated destination and bounded state transition. Return-Path and correspondent identity can differ; neither should silently substitute for the other in key binding.

A multi-step machine exchange must explicitly justify any exception to the recommendation against answering automatic messages. Unknown automatic traffic receives no negotiation response. Retries and duplicate requests must not create fresh exchanges. A terminal response must not elicit an acknowledgement through a generic responder.

Required tests: null or missing return path; forged From; list Reply-To; unknown Auto-Submitted keyword; valid optional parameters; duplicate fields; duplicate request; two responders facing one another; replay after completion; fan-out request; lost response; malformed request; no disclosure of Bcc or private aliases. Exact authenticated request format and bounded state machine remain design work, not an implementation claim.
