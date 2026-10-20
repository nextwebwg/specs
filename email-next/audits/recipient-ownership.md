---
title: Recipient ownership continuity audit
sectionNav: true
---

# Recipient ownership continuity audit

**Coverage:** complete twenty-four-page [RFC 7293](https://www.rfc-editor.org/rfc/rfc7293.html), including examples, privacy, security, registrations and end matter. No RFC 7293 errata occur in the retrieved RFC Editor errata dataset. Dependency closure remains open.

## Finding

RRVS is a useful provider-side misdelivery check. It cannot establish encryption-key continuity or authorize history recovery. Forwarding and list handling can deliberately end the original check, and role addresses are exempt. A successful delivery therefore cannot prove the identity of every eventual reader.

| Section | Disposition |
| --- | --- |
| 1 | Address reassignment can deliver sensitive content to a different person; transactional mail is primary, address books are another possible use. |
| 2 | Architecture reference and requirement vocabulary reviewed. |
| 3 | Sender supplies last confirmed ownership time; extension enforcement and header tunneling differ. Neither proves endpoint-key possession. |
| 3.1 | EHLO RRVS has no parameters; RCPT RRVS=date-time forbids fractional seconds, optional ;R default or ;C. No MAIL change; RCPT allowance grows33 characters. |
| 3.2 | Header carries addr-spec and timestamp, not an inferred To/Cc target. |
| 3.3 | Header date uses mail syntax; SMTP parameter uses RFC3339. Do not share one timestamp serializer blindly. |
| 4 | Prefer SMTP extension. Header MUST NOT be used without specific knowledge of processing support and SHOULD NOT be used for multiple recipients; it leaks relationships and lacks hop assurance. |
| 5 | Envelope parameter takes precedence for its recipient. Temporary lookup errors use transient failure. Missing historical data permits a justified latest-possible substitute; absent a reasonable substitute reject. |
| 5.1 | Known role accounts are exempt. Negative continuous-ownership check rejects RCPT with550 before delivery. |
| 5.1.1 | Relays preserve action. Unsupported next hop with default/R requires rejection: synchronous DATA550 or DSN and stop. Do not silently convert strict protection. |
| 5.2 | Only valid, locally handled, current-envelope matching header targets without corresponding RRVS are checked; role accounts excluded. Recommended removal at local delivery, or removal of applicable checked fields when forwarding. |
| 5.2.1 | Forwarding controlled by same owner can satisfy original check; remaining original-address header is inapplicable at new mailbox. Header and envelope need not otherwise match. |
| 5.3 | Both parties must synchronize clocks using a standard protocol; clock error can misclassify ownership. |
| 6 | Failure is preferred for unsupported onward relay. Header downgrade or dropping requires the permissive action and careful risk knowledge; not an override of5.1.1. |
| 6.1 | Header-to-extension conversion SHOULD remove header; reverse conversion requires rejection declined and prior knowledge of downstream processing, plus privacy restrictions. |
| 7 | One failed header check can fail all recipients at DATA; acceptance followed by per-recipient DSNs is alternative. Forwarding convergence and timestamp fanout are privacy/diagnostic hazards. |
| 8 | Special address handlers SHOULD NOT invent RRVS when absent inbound. |
| 8.1 | List delivery checks list continuity, then strips RRVS before handoff; subscriber distribution is a new message. |
| 8.2 | Alias continuity is checked locally. If destination ownership was confirmed, use later inbound/confirmation time onward; without destination records omit onward RRVS and remove local header. |
| 8.3 | Expanding alias applies single-destination choices separately per new recipient. |
| 8.4 | Confidential forwarding can use list-like termination and remove RRVS to avoid revealing ultimate destination through failures. |
| 8.5 | Lists may track subscription confirmation times and stop distribution after ownership failures; remove incoming header before redistribution. |
| 9 | Continuous ownership permits suspension, excludes delivery to another owner. Yes/no/unknown; domain transfer or unavailable data may make history unknown. Single-owner accounts should pass even earlier timestamps to avoid age disclosure. |
| 10 | RRVS header MUST NOT be covered by digital signatures. Section describes removal as mandated although5.2 explicitly makes it recommended; preserve this wording discrepancy. |
| 11 | none/unknown/temperror/permerror/pass/fail are distinct; per-recipient results possible. Trusted result handling depends on Authentication-Results baseline. |
| 12 | Examples use SMTP C/S and implicit CRLF; not live interoperability evidence. |
| 12.1 | RCPT rejection example uses5505.7.17 for changed mailbox ownership. |
| 12.2 | Header-based check happens after DATA with mail-format date; same ownership failure code. |
| 12.3 | Authentication-Results binds rrvs=pass to smtp.rcptto without exposing timestamp; no endpoint identity proof. |
| 13 | Security depends on trusted processing, abuse control and recycling practice. |
| 13.1 | Timestamp probing can reveal account age; countermeasures recommended. Example silent discard is abuse defense, not a generic invisible-mail request. |
| 13.2 | Single-owner/nonexistent-before-date cases should ignore field to avoid disclosure; restrict use to known receivers. Domain transfer can make ownership history unknown. |
| 13.3 | Receiver may ignore request, misimplement or override for local/legal policy; RRVS cannot guarantee secrecy or replace end-to-end encryption. |
| 13.4 | Reassignment is dangerous; substantial no-mail interval recommended, no numeric duration supplied. |
| 14 | Privacy tradeoffs apply even when message body is not exposed. |
| 14.1 | Relationship-time disclosure is traded against misdelivery of sensitive transactional content; not universal consent for exposing timestamps. |
| 14.2 | Rate/abuse controls needed against repeated historical probes. |
| 14.3 | Header can expose envelope recipients absent from To/Cc; avoid multi-recipient tunnel and Bcc disclosure. |
| 14.4 | Unremoved fields can leak on forwarding and signal valuable content. |
| 15 | Existing registrations reviewed; no new Email Next registration claimed. |
| 15.1 | RRVS SMTP registration points to3.1. |
| 15.2 | Permanent mail header registered; changes require review. |
| 15.3 | X.7.17 mailbox owner change, X.7.18 domain owner change, X.7.19 test unavailable; associated5XX. These are not cryptographic revocation events. |
| 15.4 | Registers rrvs method, smtp.rcptto property and six result values. |
| 16 | Acknowledgments reviewed. |
| 17 | References reviewed; baseline review is not dependency closure. |
| 17.1 | Role accounts2142, timestamp3339, clock5905 and grammar/registration dependencies remain separate;5321/5322 already reviewed. |
| 17.2 | Authentication-Results7001 successors, DSN3461/3464, architecture5598 and status3463 remain separate dependency audits. |

| Front/end matter | Abstract, status, copyright and author addresses reviewed. |

## Email Next integration

The [identity lifecycle](../identity-lifecycle.md) keeps delivery evidence separate from endpoint authorization. A required failed check must not be removed automatically on retry. Header tunneling must not expose another recipient's address or confirmation timestamp, including Bcc recipients.

The default rejection action is distinct from the permissive continue action. The broad options in section 6 do not waive the explicit strict-action requirement in section 5.1.1. Forwarding termination is also distinct from a transport implementation silently ignoring the requirement.

Section 10 calls header removal mandatory, while section 5.2 explicitly recommends it and acknowledges exceptions. This audit records the source inconsistency; it does not invent an accepted erratum. Excluding the tunnel header from signature coverage is explicit, and does not authorize modifying unrelated signed message content.

## Required verification

Exercise default/R and C relay behavior; header and parameter precedence; both timestamp syntaxes; missing versus transient historical data; roles; single/multiple aliases; private forwarding; mailing lists; multi-recipient DATA rejection; header removal; untrusted Authentication-Results; probing; and account/domain reassignment. No live RRVS implementation or provider interoperability test is claimed.
