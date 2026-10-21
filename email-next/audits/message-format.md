---
title: Internet message format audit
sectionNav: true
---

# Internet message format audit

RFC 5322 provides the existing message grammar. Email/2 can extend message contents and presentation without replacing that grammar. Author, sender, reply destination, transport trace and conversation relationships remain distinct.

**Coverage:** the complete RFC 5322 text, including appendices and references, and all 31 errata in the retrieved snapshot were read and individually assessed on 19 October 2026. This completes the base-document review; dependency, internationalization, registry and deployment audits remain open. RFC 6854 updates originator and resent grammar and is tracked separately. RFC Editor metadata identifies RFC 5322 as Draft Standard; this is its standards maturity label, not an Internet-Draft.

Sources: [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322.html), [metadata](https://www.rfc-editor.org/rfc/rfc5322.json), [errata](https://www.rfc-editor.org/errata/rfc5322), [RFC 6854](https://www.rfc-editor.org/rfc/rfc6854.html).

## Proposal consequences

The [message contract](../messages.md#receiving-existing-message-formats) preserves generation/receiving distinctions and field roles. The [security model](../security.md) must bind cryptographic identity independently of routing fields. The [renderer](../rendering.md) must retain originals and safely expose legacy content. These are editorial proposal requirements, not claims of standards adoption or measured interoperability.

## Section dispositions

Each numbered source section is accounted for below, including informative appendices. “Inherited” means no semantic replacement is proposed here; applicable updates still control. Parent-section entries apply to introductory prose, with child entries recording more specific consequences.

| Source section | Disposition and consequence |
| --- | --- |
| 1 — Introduction | Inherited scope: message contents; transport envelopes and local presentation have separate contracts. |
| 1.1 — Scope | Inherited boundary: MIME, transport, and internationalization require separate sources. |
| 1.2 — Notational Conventions | Inherited notation; prose and grammar are read together. |
| 1.2.1 — Requirements Notation | Inherited requirement meanings; draft proposal requirements do not imply adoption. |
| 1.2.2 — Syntactic Notation | Inherited ABNF notation; RFC 5234 dependency audit remains pending. |
| 1.2.3 — Structure of This Document | Inherited separation of current generation and obsolete receiving syntax. |
| 2 — Lexical Analysis of Messages | Inherited lexical model; visual reconstruction does not rewrite the received original. |
| 2.1 — General Description | Inherited CRLF structure and ASCII baseline, subject to internationalization updates. |
| 2.1.1 — Line Length Limits | Inherited 998-character maximum and 78-character recommendation excluding CRLF; transport octet limits are separate. |
| 2.2 — Header Fields | Inherited field-name/colon/body structure; header names cannot contain folding whitespace. |
| 2.2.1 — Unstructured Header Field Bodies | Inherited unstructured-field treatment; displayed prose is not an interaction command. |
| 2.2.2 — Structured Header Field Bodies | Inherited structured parsing; delimiters inside quoted strings or comments require grammar-aware handling. |
| 2.2.3 — Long Header Fields | Inherited folding/unfolding; no invented total unfolded-field limit attributed to this RFC. |
| 2.3 — Body | Inherited body boundary and line rules; MIME and UTF-8 updates remain separate audits. |
| 3 — Syntax | Inherited current syntax; generated messages exclude obsolete productions. |
| 3.1 — Introduction | Inherited grammar plus semantic restrictions; parser acceptance alone is insufficient validation. |
| 3.2 — Lexical Tokens | Inherited lexical productions; parsing must preserve semantic distinctions. |
| 3.2.1 — Quoted characters | Inherited quoted-pair semantics; escaping is context dependent. |
| 3.2.2 — Folding White Space and Comments | Inherited nested comments and FWS/CFWS; bounded parsing must guarantee progress. |
| 3.2.3 — Atom | Inherited atom/dot-atom rules; consecutive dots are not licensed by erratum 1766. |
| 3.2.4 — Quoted Strings | Inherited quoted strings; held erratum 3135 does not create a new empty-string prohibition. |
| 3.2.5 — Miscellaneous Tokens | Inherited word/phrase/unstructured distinctions; do not use one generic token splitter. |
| 3.3 — Date and Time Specification | Inherited date validity, optional seconds, leap seconds and timezone semantics; apply verified erratum 6639. |
| 3.4 — Address Specification | Inherited mailbox/group distinction; a valid address list need not identify a single replyable mailbox. |
| 3.4.1 — Addr-Spec Specification | Inherited local-part/domain semantics; SMTP and DNS constraints have separate dependencies. No global plus/dot/local-case normalization. |
| 3.5 — Overall Message Syntax | Inherited field/body grammar; message-format acceptance is distinct from SMTP framing requirements. |
| 3.6 — Field Definitions | Inherited cardinalities and ordering exceptions; Date and originator fields required, Message-ID recommended, not universally present. |
| 3.6.1 — The Origination Date Field | Inherited origination time; not receipt evidence or a total event ordering. |
| 3.6.2 — Originator Fields | Updated by RFC 6854: distinguish author, sending agent and reply destination. No automatic key ownership inference. |
| 3.6.3 — Destination Address Fields | Inherited To/Cc/Bcc roles and Bcc variants; recipient-specific copies may differ without revealing hidden recipients. |
| 3.6.4 — Identification Fields | Inherited message-version identity and reply references; multi-parent References construction requires an explicit projection decision. |
| 3.6.5 — Informational Fields | Inherited human-readable Subject/Comments/Keywords; they do not authorize actions or identify authenticated threads. |
| 3.6.6 — Resent Fields | Inherited resend blocks, with RFC 6854 grammar update. Resending is distinct from forwarding; resent fields do not control normal replies. |
| 3.6.7 — Trace Fields | Inherited trace syntax, with verified erratum 3979; SMTP defines operational semantics. Trace is not end-user authentication. |
| 3.6.8 — Optional Fields | Extension opportunity: optional fields; their permitted presence does not establish trust or invisible delivery. |
| 4 — Obsolete Syntax | Inherited receive-only compatibility; do not generate obsolete syntax. |
| 4.1 — Miscellaneous Obsolete Tokens | Inherited obsolete tokens with verified erratum 1905; render controls safely and preserve source bytes. |
| 4.2 — Obsolete Folding White Space | Inherited obsolete folding with verified erratum 1908; retain receiving support without emitting these forms. |
| 4.3 — Obsolete Date and Time | Inherited legacy year and timezone interpretation; ambiguous military zones have unknown local offset. |
| 4.4 — Obsolete Addressing | Inherited obsolete routes and list members; routes are ignored for message-address interpretation, not treated as authorization. |
| 4.5 — Obsolete Header Fields | Inherited obsolete field parsing; repeated non-destination fields do not acquire invented first/last-wins semantics. |
| 4.5.1 — Obsolete Origination Date Field | Inherited receive-only whitespace before colon and obsolete date syntax. |
| 4.5.2 — Obsolete Originator Fields | Inherited receive-only originator syntax; ambiguity blocks automated identity attribution. |
| 4.5.3 — Obsolete Destination Address Fields | Inherited combination of repeated To/Cc/Bcc fields using comma separation; preserve Bcc confidentiality. |
| 4.5.4 — Obsolete Identification Fields | Inherited obsolete identification parsing; ignore non-identifier phrases for reply-reference semantics. |
| 4.5.5 — Obsolete Informational Fields | Inherited obsolete informational fields; display safely without treating them as protocol controls. |
| 4.5.6 — Obsolete Resent Fields | Inherited obsolete resent syntax; obsolete Resent-Reply-To does not authorize an automated reply. |
| 4.5.7 — Obsolete Trace Fields | Inherited obsolete trace syntax with verified erratum 3979; held erratum 5867 tracked separately. |
| 4.5.8 — Obsolete optional fields | Inherited obsolete optional-field spacing for receiving only. |
| 5 — Security Considerations | Inherited warnings about terminal controls and Bcc leakage; proposal requires safe presentation and audience isolation. |
| 6 — IANA Considerations | Inherited registration record; new field names require registry review, not assumed availability. |
| Appendix A — Example Messages | Informative examples; check corrected examples against grammar, not the reverse. |
| Appendix B — Differences from Earlier Specifications | Historical differences reviewed; not a separate current wire grammar. |
| Appendix C — Acknowledgements | Acknowledgements reviewed; no protocol behavior to inherit. |
| 7 — References | Dependency inventory reviewed; dependency audits remain open. |
| 7.1 — Normative References | Normative dependencies identified: RFCs 1034, 1035, 1123, 2119, 5234 and ASCII standard. Track inherited lexical/DNS boundaries. |
| 7.2 — Informative References | Informative predecessors and MIME/SMTP context identified; historical references do not replace current sources. |
| A.1 — Addressing examples | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.1.1 — A Message from One Person to Another with Simple Addressing | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.1.2 — Different Types of Mailboxes | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.1.3 — Group Addresses | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.2 — Reply Messages | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.3 — Resent Messages | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.4 — Messages with Trace Fields | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.5 — White Space, Comments, and Other Oddities | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.6 — Obsoleted Forms | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.6.1 — Obsolete Addressing | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.6.2 — Obsolete Dates | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |
| A.6.3 — Obsolete White Space and Comments | Informative example reviewed; receiving/generation distinction and relevant verified corrections apply. |

## Errata dispositions

Verified corrections inform the audited reading. Held and rejected reports do not independently amend the published requirements. Review conclusions below concern proposal impact; they do not claim authority to adjudicate RFC Editor errata.

| Erratum | Section | Recorded status | Audit consequence |
| --- | --- | --- | --- |
| [3400](https://www.rfc-editor.org/errata/eid3400) | 3.5. | Rejected | Rejected: do not add mandatory terminal CRLF to the message-format grammar. |
| [1766](https://www.rfc-editor.org/errata/eid1766) | 3.4.1 | Verified | Verified editorial correction; dot-atom still excludes consecutive dots. |
| [1905](https://www.rfc-editor.org/errata/eid1905) | 4.1 | Verified | Verified obsolete-unstructured grammar correction prevents delimiter consumption. |
| [1906](https://www.rfc-editor.org/errata/eid1906) | 4.1 | Held for Document Update | Held grammar simplification; retain published/verified grammar. |
| [1908](https://www.rfc-editor.org/errata/eid1908) | 4.2 | Verified | Verified obsolete FWS correction. |
| [2104](https://www.rfc-editor.org/errata/eid2104) | 4.1 | Rejected | Rejected alternative to verified 1905. |
| [2515](https://www.rfc-editor.org/errata/eid2515) | Appendix A.5 | Verified | Verified correction to example comments around @. |
| [2579](https://www.rfc-editor.org/errata/eid2579) | Appendix A.5 | Verified | Verified correction to example comments around @. |
| [2619](https://www.rfc-editor.org/errata/eid2619) | 3.4.1 | Rejected | Rejected new normative MUST; no new requirement. |
| [2620](https://www.rfc-editor.org/errata/eid2620) | 3.4.1 | Rejected | Rejected header/SMTP conversion change; conversion remains separate. |
| [2726](https://www.rfc-editor.org/errata/eid2726) | 3.3 | Held for Document Update | Held UTC/GMT terminology cleanup. |
| [2816](https://www.rfc-editor.org/errata/eid2816) | 3.6.2 | Rejected | Rejected narrowing of Reply-To; groups remain permitted. |
| [2950](https://www.rfc-editor.org/errata/eid2950) | 3.6 | Held for Document Update | Held nullable-repetition correction; parser progress still required as implementation safety. |
| [3048](https://www.rfc-editor.org/errata/eid3048) | 3.6.6.  Rese | Held for Document Update | Held sent/set wording clarification. |
| [3088](https://www.rfc-editor.org/errata/eid3088) | 3.3 | Rejected | Rejected narrowing of trailing CFWS; comments remain permitted. |
| [3134](https://www.rfc-editor.org/errata/eid3134) | Appendix A.5 | Rejected | Rejected reversal of verified example corrections. |
| [3135](https://www.rfc-editor.org/errata/eid3135) | 3.2.4 | Held for Document Update | Held empty quoted-string restriction; do not promote to normative prohibition. |
| [3675](https://www.rfc-editor.org/errata/eid3675) | 3 | Rejected | Rejected grammar-only interpretation; prose restrictions apply. |
| [3979](https://www.rfc-editor.org/errata/eid3979) | 3.6.7; 4.5.7 | Verified | Verified Received CFWS correction in current and obsolete productions. |
| [4692](https://www.rfc-editor.org/errata/eid4692) | 3.2.4 | Held for Document Update | Held SPACE terminology correction; do not silently change qtext. |
| [5035](https://www.rfc-editor.org/errata/eid5035) | 3.3 | Rejected | Rejected zone-whitespace proposal; use later verified 6639. |
| [5712](https://www.rfc-editor.org/errata/eid5712) | 3.2.2 | Rejected | Rejected mandatory folding CRLF; FWS may be unfolded whitespace. |
| [5867](https://www.rfc-editor.org/errata/eid5867) | 4.5.7 | Held for Document Update | Held obsolete Received date proposal; do not silently substitute it. |
| [5905](https://www.rfc-editor.org/errata/eid5905) | 3.3 | Held for Document Update | Held daylight-saving wording clarification; do not infer elapsed duration from wall time. |
| [5918](https://www.rfc-editor.org/errata/eid5918) | 2.2 | Held for Document Update | Held field-name limit question; no new 77-character requirement. |
| [6639](https://www.rfc-editor.org/errata/eid6639) | 3.3 | Verified | Verified optional FWS before obsolete zone. |
| [6921](https://www.rfc-editor.org/errata/eid6921) | 2.1 | Held for Document Update | Held numerical codepoint clarification. |
| [6920](https://www.rfc-editor.org/errata/eid6920) | 2.1 | Verified | Verified ASCII terminology correction. |
| [7382](https://www.rfc-editor.org/errata/eid7382) | 3.2.3 | Rejected | Rejected removal of recursive comments; nested comments remain valid. |
| [8464](https://www.rfc-editor.org/errata/eid8464) | 4.4 | Rejected | Rejected optional obsolete-route change; route-free addresses already covered. |
| [8453](https://www.rfc-editor.org/errata/eid8453) | 3.2.2, 3.2.4 | Rejected | Rejected obsolete local-part whitespace change; no new canonicalization rule. |

## Required experiment cases

1. Parse folded fields, nested comments, quoted delimiters and obsolete whitespace without confusing header boundaries or hanging on empty productions.
2. Distinguish author, Sender and Reply-To; disable automated key attribution for ambiguous authors, repeated originator fields and empty originator groups.
3. Preserve missing Message-ID and multi-parent replies without manufacturing authenticated identity or causal order.
4. Keep resend blocks in order, distinguish them from forwarding, and never use Resent-Reply-To as automatic response authority.
5. Combine repeated destination fields according to obsolete receiving rules while preserving recipient-specific Bcc privacy.
6. Display control characters safely; retain the original even when parsing or local resource limits prevent rich reconstruction.
7. Exercise verified errata 1905, 1908, 3979 and 6639 as positive grammar fixtures; include rejected changes as regression cases where they would narrow accepted syntax.

These cases are a validation backlog. No test execution is claimed by this audit.
