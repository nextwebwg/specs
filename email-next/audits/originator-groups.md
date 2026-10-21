---
title: Originator groups audit
sectionNav: true
---

# Originator groups audit

A syntactically valid `From` field does not necessarily identify a mailbox. RFC 6854 permits groups, including empty groups, in originator fields for limited use. Email/2 must receive these messages without treating a group label as a key-discovery address.

**Coverage:** complete text, references and metadata reviewed on 19 October 2026. The retrieved errata dataset contains no RFC 6854 records. Metadata labels this document Proposed Standard and lists no subsequent updates or replacements. This is a document review, not a current-client compatibility test.

Sources: [RFC 6854](https://www.rfc-editor.org/rfc/rfc6854.html), [RFC Editor metadata](https://www.rfc-editor.org/rfc/rfc6854.json). See the [base message-format audit](message-format.md) and [receiver contract](../messages.md#receiving-existing-message-formats).

## Section dispositions

| Section | Disposition and consequence |
| --- | --- |
| 1 | Inherited rationale: empty groups support originators with no replyable address. Historical client observations are not evidence about present deployments. |
| 1.1 | Inherited notation from RFC 5322. |
| 1.1.1 | Inherited requirement terminology; RFC 2119 dependency remains under review. |
| 1.1.2 | Inherited ABNF and case-insensitive literals; RFC 5234 dependency remains under review. |
| 2 | Inherited precise amendment: replace RFC 5322 §3.6.2; replace only the specified resent productions in §3.6.6. Other resent semantics remain. |
| 2.1 | Inherited From address-list and Sender single-address syntax. Count mailboxes inside groups when deciding whether Sender is required. A Sender group cannot contain more than one mailbox. Preserve separate author, transmitter and reply-destination semantics. |
| 2.2 | Inherited updated Resent-From and Resent-Sender grammar; no replacement of remaining resend behavior. |
| 3 | Inherited limited-use applicability and recommendation against outgoing originator groups in user agents. Do not make groups the normal Email/2 author encoding. |
| 4 | Informative empty and nonempty group examples reviewed; group labels do not prove authorship or replyability. |
| 5 | Inherited security considerations: empty originators affect domain-based validation and deliverability; group syntax can expose parsing bugs. Authentication failure handling is separate from syntax acceptance. |
| 6 | Inherited references for existing registered fields; no new Email/2 field registration implied. |
| 7 | References reviewed; dependency treatment below. |
| 7.1 | RFC 5322 base review complete. RFCs 2026, 2119 and 5234 supply limited-use meaning, requirements and grammar notation; applicable portions still require review. |
| 7.2 | RFC 822 is historical context, not a replacement grammar. RFC 5617 is cited as a historical authentication example, not selected as Email/2's authentication protocol. RFC 6530 enters the internationalization audit. |

## Proposed processing consequences

1. Expand a parsed originator group only into the mailbox members actually present. An empty group produces zero mailbox identities; never invent an address from its display label.
2. If there is more than one author mailbox, require a separate authenticated interpretation of each author's authority before attributing an interaction to all of them. A valid Sender field identifies the transmitting role; it does not establish delegation cryptographically.
3. When there is no usable reply destination, show the message without an active reply action. This is distinct from hiding or discarding the message.
4. Keep outgoing ordinary mailbox syntax as the default. Use of limited originator groups requires a documented reason consistent with the inherited applicability statement.

These consequences are proposed design constraints. Exact authenticated delegation and multiple-author event encoding remain to be specified.

## Required fixtures

Cover empty From groups; one- and two-member From groups; multiple From groups; empty Sender groups; prohibited two-member Sender groups; a separate Reply-To; and the corresponding resent forms. Verify that parsing, reply availability and cryptographic attribution are independent outcomes. No fixture execution is claimed here.
