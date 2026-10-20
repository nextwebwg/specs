---
title: Delivery-status report format audit
sectionNav: true
---

# Delivery-status report format audit

**Coverage:** complete 40-page [RFC 3464](https://www.rfc-editor.org/rfc/rfc3464.html), both diagrams, collected grammar, all appendices, examples and end matter; both matching errata in the retrieved dataset reviewed. Current dependencies and implementation validation remain open.

| Section | Disposition |
| --- | --- |
| 1 | Scope is notification format, not SMTP request protocol. |
| 1.1 | All seven purposes reviewed; correlation and list maintenance do not establish authenticated authority. |
| 1.2 | Human/machine and foreign-system preservation requirements reviewed. |
| 1.3 | All MTA roles and diagram reviewed; original and final addresses serve different purposes. |
| 2 | Multipart structure, envelope destination, null reverse-path and optional simulated returned headers reviewed. One report concerns one message but can include multiple recipients. |
| 2.1 | Legacy machine part uses7bit and blank-line-separated recipient blocks; global update separately audited. |
| 2.1.1 | Case-insensitive fields, folding, comments and encoded words in comments reviewed; parsing must respect field grammar. |
| 2.1.2 | Type tokens case-insensitive; registrations and historical experimental namespace reviewed. |
| 2.1.3 | Imported lexical tokens and date grammar reviewed; dependency closure open. |
| 2.2 | Per-message singletons and collected field grammar reviewed. |
| 2.2.1 | Envelope ID preserves case/spelling and differs from Message-ID; source-presence constraints reviewed. |
| 2.2.2 | Required Reporting-MTA denotes underlying attempt, not necessarily translating gateway; diagram and name preservation reviewed. |
| 2.2.3 | DSN-Gateway required iff translated foreign report. |
| 2.2.4 | Received-From identifies prior hop; names/comments are reported evidence, not authentication. |
| 2.2.5 | Arrival-Date means arrival at reporting MTA; numeric timezone required. |
| 2.3 | Recipient block grammar reviewed; required final recipient, action and status. |
| 2.3.1 | Original recipient only from available original envelope evidence; do not fabricate from current address. |
| 2.3.2 | Final recipient as accepted by reporting MTA; preserve case and malformed source syntax except forbidden field characters. |
| 2.3.3 | All five actions reviewed; temporary4status valid with terminal failed action; expanded nonterminal. Prose failure/XXX are not valid wire values. |
| 2.3.4 | Status grammar and semantic classes reviewed; no internal whitespace/comments or leading zeros. |
| 2.3.5 | Remote-MTA absent if no remote involved; SMTP-specific requirements from3461 also apply. |
| 2.3.6 | Diagnostic retains transport-specific cause; remote/reporting origin distinguished. Not authorization. |
| 2.3.7 | Last-Attempt-Date not outer Date; omit if actual attempt time unavailable. |
| 2.3.8 | Final log identifier diagnostic only. |
| 2.3.9 | Will-Retry-Until only delayed reports and expresses expectation, not guarantee. |
| 2.4 | All extension categories and historical registration rules reviewed; diagnostic extensions do not define new application authority. |
| 3 | Minimal format conformance differs from SMTP-specific generation obligations; aliases/lists and source availability reviewed. |
| 4 | Security scope reviewed. |
| 4.1 | All six forgery examples reviewed; positive and negative reports equally need evidence limits. |
| 4.2 | All six confidentiality mechanisms and optional-field omission reviewed; nonconforming downstream header-based replies can still leak addresses. |
| 4.3 | Genuine failed DSN cannot prove nonreceipt; lost final acknowledgment can yield delivered and failed duplicate attempts. |
| 5 | All normative references read; historical successors and dependency closure remain tracked separately. |
| 6 | Acknowledgments read. |
| A | Every collected grammar production read and compared with field descriptions; receiver ordering/duplicate profile still needed. |
| B | Both gateway directions reviewed; nonbinding guidance, preserve original/final/foreign diagnostics where available and mark translating gateway. |
| C | List guidance reviewed: no deletion for delay or isolated failure; heuristic address matching can falsely match. Not authority for secure-group membership. |
| D | All three registration forms reviewed; verified8285 corrects diagnostic-type heading text. |
| E | Examples explicitly nonnormative; all four read. Verified2965 repairs first example headers. Gateway example lacks required DSN-Gateway; ordering/spacing and placeholders preclude direct fixtures. |
| F | Every change from1894 read. |
| Authors | Author material read. |
| Copyright | Copyright and final acknowledgment read. |

## Errata and example treatment

Verified erratum2965 restores the first example's accidentally collapsed message headers. Verified erratum8285 corrects the diagnostic-type registration form's introductory label. Neither changes the delivery action model.

Appendix E explicitly gives protocol definitions precedence over examples. Its gateway example omits the DSN-Gateway field required for translated reports. Some examples order fields differently from the collected grammar, contain formatting artifacts or replace returned content with placeholders. They are explanatory evidence, not validated wire fixtures. A receiving profile still needs explicit ordering, duplicate-field and malformed-input rules.

## Security consequences

Section4.3 resolves a critical distinction: an authentic failed report is not proof of nonreceipt. A completed transfer with a lost acknowledgment can cause retransmission; one copy can succeed while another attempt fails. Email Next must preserve contribution identity across retry, retain conflicting delivery observations and avoid automatic duplicate actions.

Optional diagnostic information can be omitted for confidentiality, but this does not waive stronger requirements in an applicable SMTP profile. A provider must select a valid forwarding/reporting arrangement rather than simply deleting arbitrary required fields. Nonconforming downstream systems may still expose forwarding addresses through header-based responses; the specification cannot promise secrecy across such systems.

List-maintenance heuristics are not cryptographic membership rules. Repeated failures may justify a delivery-service policy, but they do not prove key revocation, address reassignment or permission to remove a person from an authenticated conversation.

The [transport contract](../transport.md) incorporates the action/status, role, timing and nonreceipt boundaries. RFC4865 and RFC6533 updates have separate reviews. Registry closure, current status-code dependencies, a complete parser and interoperable report fixtures remain unfinished.
