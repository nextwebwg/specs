---
title: No-mail-service signaling audit
sectionNav: true
---

# No-mail-service signaling audit

Email Next preserves explicit no-mail-service failures. They must not become discovery invitations, encryption downgrade triggers or repeated attempts to contact a nonexistent mailbox.

**Coverage:** complete RFC 7504 and RFC 7505 texts, references and metadata reviewed on 19 October 2026. Neither has an erratum in the consulted datasets. Both are Proposed Standards; retrieved metadata lists no subsequent updates or replacements. Dependency and current-registry review remain open.

## RFC 7504

[Source](https://www.rfc-editor.org/rfc/rfc7504.html) · [Metadata](https://www.rfc-editor.org/rfc/rfc7504.json)

| Section | Disposition and consequence |
| --- | --- |
| 1 | Inherited scope: 521 concerns a server that never accepts mail; 556 reports a destination determined not to accept mail. Neither describes rich-client support. |
| 1.1 | Inherited SMTP and requirement terminology. |
| 2 | Inherited rationale: explicit failure avoids pointless queued retries following connection timeouts. |
| 3 | Inherited 521 at connection opening. A dummy server may repeat 521 or close after subsequent non-QUIT commands; this is a specific exception to ordinary session behavior. |
| 4 | Inherited 556 for a destination known not to accept mail, without opening a connection to that destination. Handle as a permanent negative reply to the affected command. |
| 5 | Amendment bookkeeping reviewed. |
| 5.1 | Incorporate 521/556 into RFC 5321 §§4.2.2–4.2.3; add 521 to connection establishment and 556 to RCPT in §4.3.2. |
| 5.2 | RFC 1846's 521 experiment is concluded by standardization; its other operational discussion is outside this update. |
| 6 | Inherited enhanced-status associations: 521 with X.3.2; null-MX 556 with X.1.10. No basic-code registry is asserted by this document. |
| 7 | Inherited security scope; codes provide delivery information, not authenticated endpoint identity. |
| 8 | References reviewed; dependency closure remains open. |
| 8.1 | RFC 5321 reviewed; RFC 2119 and current enhanced-status registry still require scoped review. |
| 8.2 | RFC 1846 is historical experiment context; RFC 7505 is assessed below. |

Acknowledgements and author information were read and impose no protocol behavior.

## RFC 7505

[Source](https://www.rfc-editor.org/rfc/rfc7505.html) · [Metadata](https://www.rfc-editor.org/rfc/rfc7505.json)

| Section | Disposition |
| --- | --- |
| 1 | Inherit explicit no-service signaling instead of implicit address-record fallback. |
| 2 | Inherit requirement and envelope/header terminology. |
| 3 | Inherit sole MX record: preference zero, exchange root label. No additional MX records permitted. |
| 4 | Benefits reviewed. |
| 4.1 | Recipient rejection uses recommended 556/5.1.10; sender-domain rejection uses 550/5.7.27. |
| 4.2 | Avoid null MX on sending domains; it does not replace null reverse-path. |
| 5 | Ordinary DNS security applies; DNSSEC can protect the record. |
| 6 | Enhanced-status registrations reviewed; current registry verification pending. |
| 7 | References reviewed. |
| 7.1 | DNS, requirement notation and SMTP dependencies remain tracked. |
| 7.2 | SRV precedent, architecture and SPF references remain distinct from null-MX semantics. |

Acknowledgements and author information reviewed. Proposed consequence: no-mail-service evidence must not manufacture a recipient key, hidden-control route or alternative identity.

## Required validation

Test a 521 greeting separately from a recipient's 556 rejection. Preserve outcomes for other destinations. Distinguish a DNS timeout from a valid no-service result. Verify that neither failure sends a key request, changes a trusted identity or substitutes plaintext.
