---
title: Header registration audit
sectionNav: true
---

# Header registration audit

**Coverage:** complete seventeen-page [RFC 3864](https://www.rfc-editor.org/rfc/rfc3864.html), including templates, references and end matter. No matching errata appear in the retrieved RFC Editor dataset. The current registry was inspected on 19 October 2026; its referenced emailcore message-format revision is covered by a separate audit.

## Finding

Registration identifies a field's name, protocol, status and defining document. It does not authenticate a received value, prescribe a universal parser, or confer endorsement on a provisional proposal. Email/2 must define its fields precisely and distinguish proposed registrations from completed ones.

| Section | Disposition |
| --- | --- |
| 1 | Central discovery and collision avoidance across protocols; not replacement for protocol-specific registries such as SIP. |
| 1.1 | Document organization reviewed. |
| 1.2 | Requirement vocabulary reviewed. |
| 2 | Header registration scope, not a wire parser definition. |
| 2.1 | Permanent versus provisional distinguishes publication/review status. Original Specification Required and Private Use policies are historical; current IANA permanent policy differs. Registry does not define field-value syntax itself. |
| 2.2 | Referenced field-defining documents reviewed as dependency list, not all independently audited. |
| 2.2.1 | Same name may have different protocol definitions; permanent name/protocol pair unique. Do not apply HTTP date parsing to mail solely by name. |
| 2.2.2 | MIME objects have protocol-independent MIME field meanings; similar HTTP fields historically require separate registration. Content-* names should not be reused with merely similar semantics. |
| 3 | RFCs defining fields require templates in IANA considerations. Registration otherwise not universally required absent protocol mandate; this does not authorize collision or claim registration. |
| 4 | Specify field, prepare template, submit registration; drafting alone completes none of the external review. |
| 4.1 | Syntax/semantics/intended use required; permanent published RFC/Open Standard in original process. Dot reserved; recommended letters,digits,hyphen,underscore with letter/underscore first. Current revision dependency must be checked. |
| 4.2 | Templates can be in defining document or separate. |
| 4.2.1 | Permanent template: name, protocol, status, controller, specification and optional related information; uniqueness scoped to protocol. Original publication rule not asserted as full current procedure. |
| 4.2.2 | Provisional entry requires citable accessible specification and no corresponding permanent pair; no endorsement. Controller/contact and provisional status defined. |
| 4.3 | Original RFC publication path or discussion at least two weeks then submission, expert checks; permanent entry removes matching provisional entry. No message or registration sent by this audit. |
| 4.4 | Technical disagreement alone not ground to refuse provisional listing; harmful/frivolous/misleading/conflicting requests may be refused; IESG final arbiter. |
| 4.5 | Change control follows original registration conditions; provisional removal possible when source disappears after contact attempt. Permanent name/protocol pair must not be repurposed. |
| 4.6 | Comments go to designated list in source; current process/contact must be checked before external submission. |
| 4.7 | Historical registry URL superseded by current IANA landing page; current page inspected separately. |
| 5 | Creates two registries and expert role, no initial entries. |
| 6 | Registration adds no independent security guarantees; received header content remains untrusted absent applicable proof. |
| 7 | Acknowledgements reviewed. |
| 8 | References reviewed, closure not claimed. |
| 8.1 | Standards-process and IANA-policy successors need review;5322 message-format baseline reviewed separately,5322bis revision newly identified. |
| 8.2 | Broad cross-protocol field examples are informative sources, not automatic Email/2 dependencies or current behavior claims. |
| 9 | Author details reviewed. |
| 10 | Copyright, IPR and funding notices reviewed. |

| Front matter | Abstract, status and copyright notice reviewed. |

## Current registry and revision dependency

The [IANA registry](https://www.iana.org/assignments/message-headers) lists Expert Review for permanent fields, includes a Trace column, and references the emailcore message-format revision alongside RFC 3864. It states that HTTP fields moved to a separate registry under RFC 9110. These observed changes prevent treating RFC 3864's original procedure as complete current guidance.

The linked [rfc5322bis-12 revision](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5322bis-12/) is presented by Datatracker as an Internet-Draft with conditional replacement/update language. Datatracker API state checked on 19 October 2026 places both rfc5322bis-12 and rfc5321bis-44 in the RFC Editor queue, with RFC Editor state Blocked and IANA action state RFC-Ed-Ack. No numbered RFC was supplied by those document records. This explains why registry actions can appear before final publication; it does not establish a new published baseline. Full revision audits remain required. An IANA reference label is not, by itself, evidence of a numbered RFC publication. This dependency is additional to the RFC inventory's metadata successor checks.

## Email/2 consequence

The [baseline](../baseline.md) requires protocol scope, syntax, cardinality, duplicate handling, authority, forwarding behavior, exposure and protection coverage for each new field. Keep mail, MIME and HTTP definitions distinct. Publish a stable specification and prepare accurate templates before requesting registration; this audit submits nothing externally.

No name availability, registration acceptance, parser interoperability or header preservation across providers is established by this review.

## Revision sections reviewed so far

Sections 6.1–6.2 of rfc5322bis-12 request a Trace classification for mail fields and update the existing registrations. The classification is yes/no for mail, inapplicable to other protocols, and initially empty for pre-existing entries not listed by the draft. An empty registry value therefore must not be interpreted as an explicit no. Received and Return-Path are classified as trace; the listed author, destination, informational and resent fields are not. Classification does not authenticate a field's contents.

These sections establish the Trace change. They do not, by themselves, establish the reason for the registry's separately observed Expert Review policy. Keep that policy's provenance open rather than attributing every registry change to this revision. The [message-format revision](message-format-revision.md) now has a full-text review. The [SMTP revision](smtp-revision.md) has a separate source review.
