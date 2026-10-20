---
title: Historical disposition notification audit
sectionNav: true
---

# Historical disposition notification audit

The complete base text of [RFC3798](https://www.rfc-editor.org/rfc/rfc3798.html), including grammar, examples, appendices and end matter, has been reviewed with both captured errata. RFC8098 supersedes this historical specification and remains the current generation reference. This review does not establish dependency or registry closure.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Historical post-delivery disposition reports, not delivery acknowledgments or interaction consent. |
| 1.1 | Purposes | Human/machine correlation and gatewaying goals reviewed; no proof of user comprehension. |
| 1.2 | Requirements | Correlation, language independence and extensibility requirements reviewed. |
| 1.3 | Terminology | Requirement vocabulary and imported grammar reviewed; current successor is authoritative for generation. |
| 2 | Requesting Message Disposition Notifications | Request and original-recipient headers reviewed as optional report inputs, not capability negotiation. |
| 2.1 | The Disposition-Notification-To Header | Requests may be silently ignored; no report-on-report loops; one MDN per recipient; consent and destination checks apply. Removed denied value survives in prose and is not adopted. |
| 2.2 | The Disposition-Notification-Options Header | Required/optional extension handling is historically contradictory because failed was removed from grammar; no new generation behavior derived from it. |
| 2.3 | The Original-Recipient Header | Original recipient can be supplied by delivery MTA from ORCPT; correlation is not endpoint authentication. |
| 2.4 | Use with the Message/Partial Content Type | Fragment headers and enclosed-message headers have different report targets; reassembly must not copy outer request headers into the inner message. |
| 3 | Format of a Message Disposition Notification | Report layout, null envelope sender, distinct Message-ID, one-message/recipient scope and encrypted-original retention reviewed. |
| 3.1 | The message/disposition-notification content-type | Historical 7bit message/disposition-notification registration and field order reviewed; internationalized/current reports remain separately specified. |
| 3.1.1 | General conventions for fields | Folding, comments, case-insensitive names and encoded-word comments reviewed; parsing is field-specific. |
| 3.1.2 | "*-type" subfields | Address and MTA type tags are case-insensitive; labels select syntax, not trust. |
| 3.2 | Message/disposition-notification Fields | All report fields reviewed individually below. |
| 3.2.1 | The Reporting-UA field | Reporting-UA is optional implementation metadata, not authenticated device discovery. |
| 3.2.2 | The MDN-Gateway field | Gateway field required only for translated reports; smtp recommendation conflicts with earlier dns naming example and is not copied as current guidance. |
| 3.2.3 | Original-Recipient field | Original-Recipient requires available original information; duplicate-header choice is historical, not permission to resolve endpoint identity ambiguously. |
| 3.2.4 | Final-Recipient field | Final recipient may differ after forwarding; preserve address case and distinguish it from original recipient. |
| 3.2.5 | Original-Message-ID field | Original-Message-ID correlates reports and is required when present originally; no event authority follows. |
| 3.2.6 | Disposition field | Grammar permits displayed/deleted with action/sending modes; surrounding historical prose has removed-value inconsistencies. |
| 3.2.6.1 | Disposition modes | Manual action and manual report permission are separate dimensions; neither supplies structured action authorization. |
| 3.2.6.2 | Disposition types | Displayed does not guarantee read/understood; deleted does not prove unseen or irrecoverably erased. |
| 3.2.6.3 | Disposition modifiers | Unknown modifiers cause no error response; one-report rule remains, while dispatched prose is a recorded historical inconsistency. |
| 3.2.7 | Failure, Error, and Warning fields | Failure/error/warning prose conflicts with removed dispositions; verified692 removes warning references, rejected691 requires successor cleanup for wider problems. |
| 3.3 | Extension-fields | Extension-field registration and foreign diagnostics reviewed; an extension is not a covert control service. |
| 4 | Timeline of events | Full timeline reviewed; references to removed dispositions are historical contradictions, not additional valid generation values. |
| 5 | Conformance and Usage Requirements | Original recipient provenance and alias/list expansion reviewed; historical processed advice conflicts with grammar. List receipts can disclose subscribers. |
| 6 | Security Considerations | All security subsections reviewed; reports remain optional and forgeable without separate protection. |
| 6.1 | Forgery | Forged and unsolicited reports must not authorize actions or establish device identity. |
| 6.2 | Privacy | Reports can reveal reading habits, list membership, network headers and encrypted-message metadata; optional fields may be omitted. |
| 6.3 | Non-Repudiation | No guarantee of seeing or not seeing a message, and no nonrepudiation; report absence is inconclusive. |
| 6.4 | Mail Bombing | Forged destinations can amplify mail; destination checks and consent are not optional key-exchange substitutes. |
| 7 | Collected Grammar | Complete collected grammar checked against prose; displayed/deleted only and error/extension modifiers expose the documented inconsistencies. |
| 8 | Guidelines for Gatewaying MDNs | Gateway recommendations are nonbinding and may lose information. |
| 8.1 | Gatewaying from other mail systems to MDNs | Preserve available original identity/correlation fields; gateway provenance remains distinct from original author. |
| 8.2 | Gatewaying from MDNs to other mail systems | Foreign conversion and tunneling do not strengthen report meaning or authentication. |
| 8.3 | Gatewaying of MDN-requests to other mail systems | Drop requests where a gateway cannot preserve a distinct notification destination; do not redirect silently. |
| 9 | Example | Full example reviewed as explicitly nonnormative; readable and machine parts describe display, not comprehension. |
| 10 | IANA Considerations | Historical registration procedures reviewed; no Email Next registrations result from this audit. |
| 10.1 | Disposition-Notification-Options header parameter names | Option registration requires syntax, encoding and semantics; no implicit new option chosen. |
| 10.2 | Disposition modifier names | Modifier registration requirements reviewed separately from live registry state. |
| 10.3 | MDN extension field names | Extension registration requirements reviewed; reference to encoding in an options header appears copied from the parameter template and is not a new wire rule. |
| 11 | Acknowledgments | Acknowledgments reviewed; no additional behavior. |
| 12 | References | Complete reference list and copyright/IPR/author end matter reviewed. |
| 12.1 | Normative References | Normative MIME, message, SMTP, DSN and requirement dependencies separately scoped. |
| 12.2 | Informative References | S/MIME security-services reference is informative, not proof MDNs offer nonrepudiation. |
| Appendix A | - Changes from RFC 2298 | Removed dispositions/modifiers and editorial changes checked against remaining text; contradictions explicitly recorded. |

## Errata and historical contradictions

Verified erratum692 removes references to the warning modifier. Rejected erratum691 documents broader contradictions: the grammar permits only displayed and deleted, while surrounding prose still recommends denied, failed, dispatched and processed. The rejection explains that a replacement RFC, rather than errata, is needed. Rejection does not make those contradictory examples valid generation instructions. This audit therefore preserves the historical evidence and defers current behavior to RFC8098.

The gateway discussion recommends smtp as an MTA-name type despite the earlier dns example. The extension registration template also refers to encoding extension-field values in an options header. These are recorded source discrepancies, not newly approved errata.

## Email Next boundary

A request for a receipt is not permission to negotiate keys, establish online presence or execute a structured response. A displayed report proves neither comprehension nor consent; a deleted report proves neither non-reading nor cryptographic erasure. A missing report is not evidence of incompatibility or loss of encryption support.

Never send report-on-report responses, use unknown modifiers to trigger error mail, or return decrypted original text in an unprotected report. Reports can reveal confidential recipients and reading activity, so transport correlation must remain distinct from authenticated conversation membership and user-authorized interaction state.
