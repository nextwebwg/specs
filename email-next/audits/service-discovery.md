---
title: Mail service discovery audit
sectionNav: true
---

# Mail service discovery audit

**Coverage:** complete nine-page [RFC 6186](https://www.rfc-editor.org/rfc/rfc6186.html), including examples and end matter. No entries occur in the retrieved errata dataset. The [RFC 8314 update](submission-access-tls.md) and [RFC 8553 naming update](underscored-dns.md) have separate reviews. This page records the base document.

## Finding

Email already has a standard path from an address to submission and mailbox-access endpoints. That path can simplify setup, but an SRV record advertises a service endpoint, not recipient devices, message security capabilities, or permission to replace a trusted key.

| Section | Disposition |
| --- | --- |
| 1 | Submission and mailbox access use service discovery distinct from MX-based inbound SMTP routing. An email address can supply the initial service domain. |
| 2 | Requirement vocabulary and mail architecture terminology reviewed. |
| 3 | Service labels distinguish protocol and TLS initiation behavior; they do not advertise rich-message or correspondent-key support. |
| 3.1 | The submission service uses SRV host and port selection; this base document covers STARTTLS and unprotected connections. Current transport requirements require the8314 update. |
| 3.2 | IMAP and IMAPS labels distinguish STARTTLS-capable access from TLS immediately on connection. Historical optional-use language is not a modern protection policy. |
| 3.3 | POP3 and POP3S similarly distinguish STLS from immediate TLS. Neither proves message decryption capability. |
| 3.4 | Lower numeric priority is preferred across supported access protocols. At equal priority select the protocol before applying within-protocol weight selection. A dot target means the particular service is unavailable. |
| 4 | Discover from the address domain; obey SRV priority and weight; validate TLS identity. Historical authentication guidance tries full address then local part. Cache successful service configuration. On failure refresh the same protocol; do not silently switch between IMAP and POP3 because priorities changed. |
| 5 | Providers avoid ambiguous login names, provide verifiable certificates, enable SNI for multiple domains on one IP and publish appropriate records. These requirements do not constitute device enrollment authority. |
| 6 | Explicitly required transport security must succeed before authentication. Untrusted DNS can redirect clients; authenticate the intended service or use the stated user-confirmation path. Historical SSL2 prohibition is insufficient as a current TLS profile. |
| 7 | Acknowledgements reviewed; no protocol requirements. |
| 8 | Reference classification reviewed; cited standards and successors remain separate dependencies. |
| 8.1 | Dependencies include SRV selection, mailbox access, submission, TLS, SNI and service identity. Separate reviews cover the8314 and8553 updates and the9525 successor to6125; broader dependency closure remains open. |
| 8.2 | Mail architecture reference provides terminology, not cryptographic authority. |

| Front and end matter | Abstract, standards status, copyright and author address reviewed. |

## Email/2 consequence

Preserve the configured access protocol when refreshing discovery. An automatic switch from IMAP to POP3 changes mailbox behavior and is not an ordinary endpoint retry. Keep required transport protection in force across endpoint changes, and authenticate the newly selected service before releasing credentials.

A dot target is an explicit absence of the queried service. Missing records, temporary lookup failure, and an explicit unavailable service are different results. None establishes that an account lacks Email/2 capability; capability discovery needs its own scoped record and failure semantics.

Required cases include equal-priority records across protocols, weighting only within the selected protocol, changed priorities after successful setup, dot targets, temporary lookup failure, and a replacement endpoint that cannot satisfy the existing TLS policy. No resolver or authentication implementation has been tested by this audit.
