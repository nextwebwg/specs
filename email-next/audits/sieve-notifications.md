---
title: Sieve mail notifications audit
sectionNav: true
---

# Sieve mail notifications audit

**Coverage:** complete 12-page RFC5436, including examples, references and front/end matter; no matching errata in refreshed dataset checked19October2026. [RFC5436](https://www.rfc-editor.org/rfc/rfc5436.html).

| Section | Disposition |
| --- | --- |
| 1 | Sieve notification profile scope, not a universal mail control channel. |
| 1.1 | Notification framework selects mechanisms through URIs; this mechanism sends ordinary email. |
| 1.2 | Sieve notation and requirement vocabulary retained. |
| 2 | Notification is a new message caused by a triggering message, not a replacement for it. |
| 2.1 | Distinguish mailto URI headers from delivered message headers; current mailto successor requires separate audit. |
| 2.2 | Online yes/no requires certainty; otherwise maybe. Email delivery or a notification does not establish device presence. |
| 2.3 | Configured :from affects message identity and may affect envelope; neither authenticates a correspondent key. |
| 2.4 | Importance is implementation-defined and conveys no protocol priority or trust. |
| 2.5 | :options is unused by this mechanism. |
| 2.6 | :message supplies subject before other sources; truncation policy does not alter event identity. |
| 2.7 | Prevent loops, suppress non-no automatic triggers, permit null-sender triggers, preserve null envelope on resulting notification. Submit once after successful submission; avoid duplicate notifications. Enforce protected header precedence; ignore URI overrides for From, Auto-Submitted, Received, Date and Message-ID. Generate new Date/Message-ID, optionally retain causal References and bounded body. This is notification forwarding to configured recipients, not replying to a null sender. |
| 2.7.1 | auto-notified requires owner-email or owner-token, placed above retained original Received fields. Trace segmentation is not authentication; owner-token is an administrative lookup handle, not a secret capability. |
| 3 | Examples illustrate fresh message identity and retained trace boundary. The prose calls owner-email optional because owner-token is an alternative; at least one remains mandatory. |
| 4 | Internationalization delegated to Sieve and notification framework; no new Unicode identity normalization. |
| 5 | Forwarded content can leak confidential information; administrative complaint and loop-remediation mechanisms required. Rate example30/hour is illustrative, not an Email/2 limit. Gateways may strip loop markers. Reassigned or mistyped notification addresses remain a risk. |
| 6 | Registrations change extension governance without changing visibility guarantees. |
| 6.1 | Registers mailto notification mechanism; original2368 reference needs6068 successor review. |
| 6.2 | Creates Auto-Submitted keyword registry with Specification Required policy, superseding3834 IETF Consensus requirement for keywords. Does not create an unrestricted negotiation-header namespace. |
| 6.3 | Initial no, auto-generated, auto-replied and auto-notified values match live IANA registry checked19October2026; no extra negotiation keyword registered. |
| 7 | Reference sections reviewed; dependency audits still incomplete. |
| 7.1 | 5435,5228, current mailto6068 and registration8126 dependencies remain open;3834/5322 base reviews recorded. |
| 7.2 | 5321 base reviewed; Sieve variables5229 remains a dependency for implementations using interpolation. |

| Front/end matter | Status, abstract, copyright and author contacts reviewed; no additional wire requirements. |

## Registry check

The [IANA Auto-Submitted registry](https://www.iana.org/assignments/auto-submitted-keywords/) was checked19October2026. It lists four keywords and uses Specification Required. This closes the specific keyword-registry check, not all registration or dependency work.

## Email/2 consequences

A Sieve notification is not a hidden negotiation channel. Its configured destination can be different from both the original author and the envelope sender. A notification that quotes or references a structured event must not be processed as a fresh authenticated event merely because it includes familiar fields.

A null reverse-path on a triggering message does not universally mean “never send any new message”: this notification service permits it and propagates a null reverse-path to prevent bounce loops. This exception does not permit sending a reply to a null destination.

Presence discovery must remain an independently authorized capability. A successful SMTP transaction, generated notification or retained trace timestamp cannot replace an authenticated, fresh device-presence statement. Even that statement does not imply that a human is reading or available.

Required cases include null-sender notification, attempted URI overrides of protected headers, preserved trace boundary, owner-token without owner-email, missing both owner parameters, duplicate submission prevention, auto-notified trigger suppression, and a gateway that strips the marker. No deployment test is claimed here.
