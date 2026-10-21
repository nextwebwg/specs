---
title: Message-format revision audit
sectionNav: true
---

# Message-format revision audit

**Coverage:** complete fifty-nine-page [draft-ietf-emailcore-rfc5322bis-12](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5322bis-12/), including grammar, tables, every example, change lists and end matter. This is a revision audit, separate from the published RFC inventory. Datatracker records inspected on 19 October 2026 place the document in the RFC Editor queue with outstanding publication work. No numbered replacement RFC is claimed.

## Finding

The revision retains the distinction between strict generation and legacy interpretation. Its notable changes include clearer blind-copy representations, broader trace grouping and corrections to legacy grammar. None makes transport headers proof of endpoint identity or conversation membership.

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Introduction distinguishes revision from published baseline. |
| 1.1 — Scope | Content syntax, not envelope, storage or UI; MIME/EAI extensions remain separate. |
| 1.2 — Notational Conventions | Notation overview reviewed. |
| 1.2.1 — Requirements Notation | BCP14 uppercase requirement vocabulary. |
| 1.2.2 — Syntactic Notation | ABNF literals case-insensitive unless specified; decimal character values. |
| 1.2.3 — Structure of This Document | Generation excludes obsolete forms; interpretation includes them for archives. Examples do not override grammar. |
| 2 — Lexical Analysis of Messages | Lexical layer precedes semantic interpretation. |
| 2.1 — General Description | ASCII1–127 baseline, CRLF, optional body after empty line; MIME/6532 extend repertoire. |
| 2.1.1 — Line Length Limits | 998-character physical limit,78 recommendation excluding CRLF; unfolded fields not bounded by these values. |
| 2.2 — Header Fields | ASCII field names exclude space/colon; body grammar controls folding. |
| 2.2.1 — Unstructured Header Field Bodies | Unstructured text is not subject to structured comment removal. |
| 2.2.2 — Structured Header Field Bodies | Structured grammar determines where comments and whitespace apply. |
| 2.2.3 — Long Header Fields | Fold only where FWS allowed, prefer high-level breaks; unfold removes CRLF before WSP, not all whitespace. |
| 2.3 — Body | Baseline body CRLF-only and line limits; MIME extensions separate. |
| 3 — Syntax | Formal generation and interpretation grammar reviewed. |
| 3.1 — Introduction | obs productions excluded when generating, included when interpreting. |
| 3.2 — Lexical Tokens | Lexical grammar composes into higher-level forms; do not split addresses with naive punctuation rules. |
| 3.2.1 — Quoted characters | Backslash is semantically invisible only in quoted-pair positions, not globally. |
| 3.2.2 — Folding White Space and Comments | Nested comments, FWS and CFWS grammar; no whitespace-only folding lines in generated form; inter-token CFWS interpreted as space. |
| 3.2.3 — Atom | Atoms/dot-atoms exclude outer CFWS; internal periods have grammar constraints. |
| 3.2.4 — Quoted Strings | Quoted strings retain semantic contents, discard delimiters/outer CFWS and quoted-pair escaping; empty string not newly prohibited. |
| 3.2.5 — Miscellaneous Tokens | word/phrase/unstructured distinct productions. |
| 3.3 — Date and Time Specification | Valid calendar/weekday/time and zone minutes required; leap second allowed; -0000 conveys unknown local zone, not evidence of local UTC. |
| 3.4 — Address Specification | Mailbox/group syntax, display names separate from unspecified comments; empty group reveals no member list. |
| 3.4.1 — Addr-Spec Specification | Local-part domain-dependent; liberal header domain syntax does not override SMTP/DNS destination constraints. |
| 3.5 — Overall Message Syntax | Header/body syntax and discouraged controls; parser acceptance does not permit control execution. |
| 3.6 — Field Definitions | Cardinality table reviewed; trace/resent ordering preserved, other field order not reliable; Date and From required by base grammar. |
| 3.6.1 — The Origination Date Field | Date records readiness for submission, not actual network transmission or receipt. |
| 3.6.2 — Originator Fields | From authors, Sender transmitter, Reply-To suggested reply addresses; multi-author Sender requirement; syntax not identity proof. |
| 3.6.3 — Destination Address Fields | Bcc removed from To/Cc copies; blind copies absent/empty/own-address-only. Reply-all details partly implementation-defined; do not leak blind recipients. |
| 3.6.4 — Identification Fields | Message-ID identifies semantic version, not byte hash; trace/resent additions retain original. Multiple In-Reply-To parents possible; multiple-parent References algorithm undefined. |
| 3.6.5 — Informational Fields | Subject/Comments unstructured, Keywords phrases; one Re prefix recommended when used, no thread identity guarantee. |
| 3.6.6 — Resent Fields | Resent blocks newest first, Date/From required; original fields retained; resent fields informational and not normal reply targets. Distinct from forwarding new content or transport forwarding. |
| 3.6.7 — Trace Fields | Trace may include separately defined optional fields; Return-Path without Received allowed. Operational rules delegated, no inherent authentication. |
| 3.6.8 — Optional Fields | Optional fields cannot reuse core names; field-name grammar1*ftext.77-character comment tied to78 recommendation, not a hard ABNF limit. |
| 4 — Obsolete Syntax | Legacy interpretation required; malformed forms outside grammar must not crash or irretrievably lose source. |
| 4.1 — Miscellaneous Obsolete Tokens | Legacy controls/NUL/bareCR/LF and phrase periods parsed; preserve source, inert display. |
| 4.2 — Obsolete Folding White Space | Legacy FWS permits leadingCRLF and whitespace-only continuation lines. |
| 4.3 — Obsolete Date and Time | Two-digit years00–49→2000–2049,50–99→1950–1999; three-digit+1900. Unknown/military zones treated as -0000 absent external knowledge. |
| 4.4 — Obsolete Addressing | Legacy routes, mixed quoted local parts, null list members and domain-literal escapes; route ignored for interpretation. |
| 4.5 — Obsolete Header Fields | Duplicate field interpretation unspecified except destination lists; out-of-block trace/resent interpretation unspecified. |
| 4.5.1 — Obsolete Origination Date Field | Legacy whitespace beforeDate colon accepted, not generated. |
| 4.5.2 — Obsolete Originator Fields | Legacy originator whitespace accepted; does not resolve duplicate author ambiguity. |
| 4.5.3 — Obsolete Destination Address Fields | Repeated destination occurrences should combine lists of same field; preserve To/Cc/Bcc distinction. |
| 4.5.4 — Obsolete Identification Fields | Ignore phrases in legacy reply/reference fields; internal optional CFWS excluded from semantic ID components. |
| 4.5.5 — Obsolete Informational Fields | Legacy informational field syntax retained for reading. |
| 4.5.6 — Obsolete Resent Fields | Resent-Reply-To remains informational only, not a reply routing override. |
| 4.5.7 — Obsolete Trace Fields | Legacy trace templates allow optional date; full SMTP semantics separate. |
| 4.5.8 — Obsolete optional fields | Legacy optional-field whitespace before colon accepted. |
| 5 — Security Considerations | Terminal escape hazards require inert display without indiscriminate charset corruption; blind-copy replies can reveal receipt. |
| 6 — IANA Considerations | Registration changes do not establish wire authentication. |
| 6.1 — Message Header Field Registry Changes | Trace column binary for mail, otherwise inapplicable; existing unlisted entries initially empty, not explicitly no. |
| 6.2 — Updates to the Permanent Message Header Field Registry | All listed registrations reviewed: Received/Return-Path trace yes; other listed fields no; update references in related registries. |
| 7 — References | References reviewed, dependency closure not claimed. |
| 7.1 — Normative References | ASCII,BCP14,host requirements,DNS andABNF dependencies remain separately scoped. |
| 7.2 — Informative References | MIME/EAI,registration,SMTP revision andemailcore applicability statement dependencies; pinned cited SMTP29 differs from retrievedcurrent44. |
| A — Example Messages | Examples explanatory; grammar takes precedence if conflict. |
| A.1 — Addressing Examples | Address examples reviewed. |
| A.1.1 — A Message from One Person to Another with Simple Addressing | Single author and distinct transmitting secretary illustrate From/Sender. |
| A.1.2 — Different Types of Mailboxes | Quoted punctuation and legal atom question mark; missing display names valid. |
| A.1.3 — Group Addresses | Nonempty and empty groups do not imply hidden roster knowledge. |
| A.2 — Reply Messages | Three-message reference chain and Reply-To routing reviewed. |
| A.3 — Resent Messages | Resent addition preserves originalMessage-ID and reply author; successive blocks prepend. |
| A.4 — Messages with Trace Fields | Trace chronology and folding examples reviewed, no trust inferred. |
| A.5 — White Space, Comments, and Other Oddities | Nested/escaped comments and folding valid despite unusual appearance. |
| A.6 — Obsoleted Forms | Legacy examples must not be copied as newly generated syntax. |
| A.6.1 — Obsolete Addressing | Unquoted nameperiod, source route, empty list member and internal domain whitespace. |
| A.6.2 — Obsolete Dates | Two-digit year andGMT legacy; optional weekday not exclusively legacy. |
| A.6.3 — Obsolete White Space and Comments | Whitespace-only continuation represented by underscores in explanation; do not copy literal underscores. |
| B — Differences from Earlier Specifications | All29+20 historical and26 current change entries reviewed; current delta and deferred errata discussed below. |
| C — Acknowledgements | Acknowledgements reviewed; author/end matter read. |

## Changes and unresolved points

Appendix B records 26 changes from RFC 5322, including corrected obsolete whitespace/body grammar, Received parsing, timezone wording, internal message-ID grammar, trace grouping and Bcc behavior. This review checks those changes against the body; it does not assume every predecessor erratum was incorporated.

Two held errata are explicitly left unimplemented: 2950's resent repetition change and 3135's prohibition on an empty quoted string. The appendix says a repetition change would not guarantee an unambiguous parse, and defers the empty-string discussion to applicability guidance. Treat those as unresolved dependencies, not silently adopted corrections.

The appendix describes field names as unable to exceed 77 characters, while the body connects 77 to the recommended 78-character line length and retains `1*ftext`. Email/2 does not promote that recommendation to a universal rejection limit based on the appendix alone. Its own new fields can use short names without rejecting longer legacy names on this rationale.

The revision's From and Sender grammar remains mailbox-based. The separately reviewed RFC 6854 extension must still be considered; this revision does not justify dropping applicable extension behavior merely because it does not repeat it.

## Email/2 consequences

The [rendering contract](../rendering.md) preserves raw source, duplicate ambiguity, resent history and multiple reply parents. The [delivery policy](../delivery-policy.md) uses the clarified Bcc representations for generated copies and prevents leaks through structured metadata. The [baseline](../baseline.md) distinguishes current registry actions from final RFC publication.

The SMTP revision and emailcore applicability statement remain dependencies. No independent parser conformance, real-client compatibility or cryptographic validation is established by this textual review.
