---
title: Message disposition notification audit
sectionNav: true
---

# Message disposition notification audit

**Coverage:** complete thirty-seven-page [RFC 8098](https://www.rfc-editor.org/rfc/rfc8098.html), including collected grammar, example, registrations, references, changes and end matter. No RFC 8098 errata occur in the retrieved full RFC Editor dataset. Dependency closure and deployed interoperability remain unproven.

## Finding

A disposition receipt is an optional report of a limited action, not proof of human reading, successful decryption, form acceptance or key possession. Notification routing and consent differ from ordinary delivery-failure notifications.

| Section | Disposition |
| --- | --- |
| 1 | MDNs report post-delivery disposition; distinct from delivery status. |
| 1.1 | Human interpretation, correlation and cross-system reporting purposes reviewed. |
| 1.2 | Readable and machine-processable correlation requirements do not authenticate reports. |
| 1.3 | Requirement vocabulary reviewed. |
| 2 | Request headers carry destination and optional context. |
| 2.1 | Request may be ignored; no MDN of MDN. Consent requirements for mismatched, absent Return-Path or multiple destinations. Preserve local-part case and meaningful syntax equivalence; no inferred subaddress equivalence. Subset requests need separate envelope copies. Multiple clients need coordination. |
| 2.2 | Unknown required options prevent proper generation; optional options may be ignored. Registration required; X prefix grants no special privilege. |
| 2.3 | Available ORCPT should become Original-Recipient on final delivery; this updates RFC 3461. Do not fabricate unavailable original addresses. |
| 2.4 | Inner message carries fragment-related request fields; outer fragment occurrences ignored and not copied into reassembled message. Do not use fragment handling to generate multiple receipts. Wording tension noted below. |
| 3 | Multipart/report with readable explanation, machine part and optional returned source. Returned encrypted content stays encrypted. DNT destination in both envelope/header, null sender, distinct report Message-ID. |
| 3.1 | ASCII 7bit machine part; no parameters. Field order recommended, not fixed; extensions may appear anywhere. Restriction does not apply to optional returned original. |
| 3.1.1 | Case-insensitive names, folding and grammar-appropriate comments; encoded words only where comment syntax permits. |
| 3.1.2 | Registered address/MTA types; SMTP Atom differs from message-format atom. |
| 3.2 | Required and optional content fields reviewed individually. |
| 3.2.1 | Reporting-UA recommended unless configured otherwise; minimize product detail and fingerprinting, no advertisements. |
| 3.2.2 | MDN-Gateway mandatory only for translated foreign reports, forbidden otherwise. |
| 3.2.3 | Original-Recipient included only when reliably available; duplicate-source handling permits choosing or omission, not invented certainty. |
| 3.2.4 | Final-Recipient required, case preserved; privacy alias may replace personal destination, so not identity succession evidence. |
| 3.2.5 | Original-Message-ID present exactly when original has Message-ID; correlation does not prove authenticity. |
| 3.2.6 | Disposition mandatory; values case-insensitive; action, sending mode, type and modifiers separate. |
| 3.2.6.1 | One action mode and one sending mode; defaults protect privacy. Section 6.2 permits privacy-masked manual/manual labels, not forensic click proof. |
| 3.2.6.2 | Displayed not read or understood; processed may be automated; dispatched may be printed/forwarded; deleted may already have been seen and may be restored. |
| 3.2.6.3 | Unknown modifiers may be ignored or shown without interpretation, never produce an error response. One report per recipient/message, with forwarding considerations. |
| 3.2.7 | Error text has no comment syntax or encoded-word escape. Internationalized report alternative is RFC 6533. |
| 3.3 | Extension fields require registration; foreign and implementation-specific diagnostics must not acquire endpoint authority. |
| 4 | Remember report issuance; later actions do not generate a continuing activity stream. |
| 5 | No invented original recipient from ordinary SMTP. Alias expansion can yield multiple reports. List processed receipt differs from member receipt; propagation risks subscriber disclosure. |
| 6 | Threat model includes forgery, disclosure and amplification. |
| 6.1 | Reports and requests can be forged; verify request authenticity before processing. Unsolicited reports cannot drive trusted state. |
| 6.2 | Requests may be silently ignored; optional fields omitted for privacy. Returned headers leak topology; reported modes may conceal configuration. |
| 6.2.1 | Product disclosure tradeoff does not authenticate software identity. |
| 6.2.2 | Product, language and other metadata can fingerprint a device. |
| 6.3 | No non-repudiation or guarantee of viewing; reports may be lost or bypassed. |
| 6.4 | Third-party destinations and returned content create amplification risk. General SHOULD NOT does not weaken section 2.1 confirmation requirements. |
| 7 | Complete collected ABNF read; error modifier remains explicitly present, field ordering prose also applies. No global comment stripping for unstructured text. |
| 8 | Gateway guidance is non-binding except explicit requirements; specialized mappings may differ. |
| 8.1 | Foreign translation may lose information; preserve original identifiers where available, require MDN-Gateway. |
| 8.2 | Preserve useful recipient/message correlation through translation or tunneling; do not invent exact semantics from lossy mappings. |
| 8.3 | Drop requests whose distinct notification destination cannot be represented by the foreign system; do not silently redirect to its sender field. |
| 9 | Full illustrative transcript read; abbreviated returned original is not a complete fixture, grammar wins over example. |
| 10 | Media registration and three Specification Required parameter registries reviewed; no Email/2 registration performed. |
| 10.1 | Option registration needs name, grammar, ASCII encoding and public semantic specification. |
| 10.2 | Modifier registration needs name and stable public semantics. |
| 10.3 | Extension-field registration needs grammar, encoding and semantics; copied reference to Options header is a wording concern, not alternate field placement. |
| 11 | References read; dependency closure not claimed. |
| 11.1 | DSN and IMAP MDN coordination dependencies remain separately scoped. |
| 11.2 | Internationalized reports, security services and gateway profiles require applicable independent review. |
| Appendix A | All changes reviewed: privacy consent, restored disposition grammar, removed warning/failure fields, reporting-UA syntax, whitespace, registries and comparison clarification. |

## Interpretation boundaries

Section 2.4 says to ignore request fields on individual message fragments, then describes fragment-associated fields during reassembly. Email/2 does not turn that wording into permission to emit fragment receipts: use the reassembled inner message and preserve the no-duplicate-report requirement. No retrieved erratum resolves the wording.

Section 3.2.6.3 describes extension modifiers while the grammar and section 3.2.7 retain `error`. Preserve the explicit grammar and Error-field behavior. Section 10.3's encoding instruction mentions the Options header despite discussing extension fields; this audit does not move extension data to that header.

The [transport contract](../transport.md) now preserves receipt destinations, privacy checks, reported action versus sending mode, and uncertainty. An authenticated report still carries only the meaning its profile defines. Multiple reports after alias expansion cannot establish an authenticated group roster.

## Verification still needed

Exercise forged and unsolicited reports, unknown modifiers, duplicate delivery, shared-mailbox coordination, alias privacy, encrypted returned content and foreign-destination loss. Complete RFC 3503 and internationalized report dependencies before claiming an interoperable receipt implementation.
