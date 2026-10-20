---
title: Internationalized email framework audit
sectionNav: true
---

# Internationalized email framework audit

**Coverage:** complete RFC6530, 26 pages. No records for this RFC in the fresh RFC Editor errata dataset checked19October2026. Dependency closure remains open.

Source: [RFC6530](https://www.rfc-editor.org/rfc/rfc6530.html).

| Section | Disposition |
| --- | --- |
| 1 | Display names are not envelope identities; historic downgrade specifications superseded. |
| 2 | Framework composes transport, headers and access. |
| 3 | Consistent identity handling across subsystems required. |
| 4 | Terminology reviewed. |
| 4.1 | Final delivery controls local-part interpretation. |
| 4.2 | ASCII and non-ASCII sets distinguished. |
| 4.3 | Address appearance does not establish capability. |
| 4.4 | Message audience defined. |
| 4.5 | Redistributing lists are distinct agents. |
| 4.6 | Conventional and internationalized messages distinguished. |
| 4.7 | Rejection versus subsequent notification distinguished. |
| 5 | Dependency plan reviewed. |
| 6 | Unauthenticated alias pairing and downgrade complexity documented. |
| 7 | Extension composition reviewed. |
| 7.1 | Negotiated transport; UTF-8 and access requirements. |
| 7.2 | Consistent UTF-8 presentation encouraged. |
| 7.3 | Internationalized DSNs required with combined advertisement. |
| 8 | Endpoint transformations distinguished from relaying. |
| 8.1 | Submission guidance explicitly nonnormative. |
| 8.2 | Preserve recoverable originals after delivery. |
| 9 | No in-transit local-part transformation. |
| 10 | Configuration guidance reviewed. |
| 10.1 | Destination-controlled aliases; normalization advice is not global equivalence. |
| 11 | Additional issues reviewed. |
| 11.1 | URI/IRI dependencies open. |
| 11.2 | Identifier uses need separate review. |
| 11.3 | Transformations can break signatures; legacy decoding persists. |
| 11.4 | Local parts cannot generically become DNS labels. |
| 11.5 | Archive formats need UTF-8-aware processing. |
| 12 | Experimental in-transit downgrade removed. |
| 13 | Confusables, alias authentication and parser disagreement reviewed. |
| 14 | Acknowledgements reviewed. |
| 15 | References reviewed. |
| 15.1 | Normative dependency closure pending. |
| 15.2 | Historical draft successors require mapping. |
| Front matter and authors | Status, copyright, abstract and contacts reviewed. |

## Proposed application to Email Next

The sender's fallback policy remains a first-class choice. Ordinary mail, hosted access and enforced endpoint encryption are distinct delivery modes with separate protection claims. The transport must not switch among them merely because an intermediate server cannot process a feature.

Any alternate-address binding used for automatic delivery must have evidence appropriate to the selected security mode. A resemblance between addresses, a display name or an unverified claim in a message is insufficient to transfer a pinned key or authorize disclosure. A user can explicitly select a different destination, but the application must treat that as a destination change until its binding is established.

Separate account routing, device support and display capability. A provider accepting a message does not prove every device can interpret it. Retain original source for verification while producing derived legacy views. These are proposed design choices; this source does not specify the Email Next security protocol.
