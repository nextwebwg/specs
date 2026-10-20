---
title: Internationalized delivery and disposition reports
sectionNav: true
---

# Internationalized delivery and disposition reports

**Coverage:** complete 19-page [RFC 6533](https://www.rfc-editor.org/rfc/rfc6533.html), including all grammar, registrations, references, appendices and end matter. No matching errata occur in the retrieved full dataset. Metadata lists no updates or replacements. This review does not close its DSN, Unicode or language-tag dependencies.

| Section | Disposition |
| --- | --- |
| 1 | Scope and correlation rationale reviewed; experimental alternate-address syntax is removed. |
| 2 | Requirement vocabulary reviewed. |
| 3 | Three UTF-8 address representations, capability-dependent ORCPT constraints, unitext escapes and complete ABNF reviewed. Preserve malformed labeled addresses as specified when copying diagnostics; do not treat them as verified identities. Grammar discrepancies remain recorded below. |
| 4 | Human-readable, machine-readable and optional returned-content parts retain distinct functions. |
| 4.1 | UTF-8 address and diagnostic extensions, per-recipient grammar and distinct language tags reviewed. Diagnostic prose and ABNF disagree; see open issue below. |
| 4.2 | Returned complete messages use message/global with RFC6532 semantics. |
| 4.3 | Returned header-only parts end before the first blank line and contain no original body. |
| 4.4 | All combinations of legacy/global report parts must be accepted; lossless ASCII representation may use legacy types. New message subtypes permit transfer encoding. |
| 4.5 | Returning an undeliverable SMTPUTF8 message through a return-path server without SMTPUTF8 requires seven-bit transfer encoding of the encapsulated content and headers. |
| 5 | Global MDN type, UTF-8 recipient fields, delivery-time Original-Recipient conversion and DNT address syntax reviewed. Historical failure/warning fields require reconciliation with RFC8098. |
| 6 | No new registry; registrations and updates reviewed individually. |
| 6.1 | UTF-8 address registration recognizes three forms, only the xtext-named form seven-bit safe. |
| 6.2 | SMTP diagnostic numeric codes unchanged; global report diagnostic text may contain UTF-8. |
| 6.3 | Global-headers registration requires UTF-8, no charset parameter; transfer encoding permits seven-bit transport. All registration fields reviewed. |
| 6.4 | Global-delivery-status registration requires 8bit except seven-bit environment may require quoted-printable/base64; legacy clients need updated parsing. All registration fields reviewed. |
| 6.5 | Global-disposition-notification registration has equivalent encoding constraints and is the report's second part. All registration fields reviewed. |
| 7 | Forged positive/negative reports, parser attacks, blowback and correlation risks reviewed. Message-ID correlation is not authentication. |
| 8 | Reference structure reviewed. |
| 8.1 | Normative references reviewed; dependency closure remains open. |
| 8.2 | Informative references reviewed, including superseded experimental RFC5337. |
| A | All changes from RFC5337 read; removed embedded alternate ASCII address and downgrade references are not restored. |
| B | Acknowledgments read. |
| Authors | Author and end matter read. |

## Existing extension points

The standard already defines UTF-8 delivery and disposition reports. An internationalized address can survive a seven-bit reporting path through the specified `\x{…}` unitext representation. Despite the name `utf-8-addr-xtext`, this is not RFC3461's ordinary plus-hex xtext encoding. Escaping an address for a report does not make an internationalized delivery mailbox usable by a server without SMTPUTF8.

Report containers permit combinations of legacy and global media types. The global report and returned-message parts can be transfer encoded for seven-bit infrastructure. A receiver must decode the part before parsing it, preserve each part's declared semantics and avoid inventing ASCII aliases. A plain explanation remains useful to an older client; structured report interpretation is not guaranteed there.

## Unresolved source discrepancies

Section 3 says HEXPOINT has two to six digits, but its final ABNF alternative uses `4*HEXDIG` after `10`, permitting more than four trailing digits. The alternatives described as encoding all ASCII controls also omit some such values. These are observations from the text, not accepted errata. Email Next must not manufacture valid Unicode scalars or mailbox identities from malformed escapes. Exact parser treatment requires a bounded Unicode/grammar reconciliation and test vectors.

Sections 4.1 and 6.2 explicitly permit UTF-8 Diagnostic-Code text, but section 4.1's production uses `*text-fixed`, which admits only ASCII. The difference is recorded rather than silently described as resolved. A proposed Email Next receiving profile should preserve UTF-8 diagnostics as inert text; a strict interoperable generation/validation rule remains to be specified.

Section 5 updates historical RFC3798 Failure, Error and Warning fields. The current RFC8098 review removes historical failure/warning machinery; this audit does not revive those fields as required current output. Current global-MDN grammar needs an explicit combined profile.

## Security and proposal consequences

Report correlation helps identify which attempted delivery a report concerns. It does not authenticate the report, prove human reading or establish possession of an encryption key. Neither a positive report nor a forged negative report may change trusted membership, key continuity or fallback authorization. Optional returned content remains subject to the original protection policy.

The [transport contract](../transport.md) carries these boundaries. Remaining work includes exact unitext parsing, current MDN grammar reconciliation, DSN dependency review, forged-report tests and global/legacy multipart combinations. No provider interoperability or parser implementation is claimed by this document.


## Historical report experiment

The [RFC5337 audit](internationalized-report-history.md) records the superseded experiment, its four captured errata and syntax inconsistencies. Those historical forms do not create an alternate current generation profile or authorize recipient/key substitution. Report correlation remains distinct from authenticated conversation actions.
