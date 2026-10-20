---
title: MIME body-format audit
sectionNav: true
---

# MIME body-format audit

MIME already separates content type, character encoding and transfer encoding. Email Next retains those layers and adds a versioned content contract. Its version is independent of MIME-Version.

**Coverage:** complete RFC 2045 text and collected grammar, plus all five retrieved errata records, read and assessed on 19 October 2026. This completes the base-document review. Parameter/internationalization updates, MIME companion documents and current registration rules remain open; in particular, do not extrapolate the original composite-encoding prohibition past later updates without review.

Sources: [RFC 2045](https://www.rfc-editor.org/rfc/rfc2045.html), [metadata](https://www.rfc-editor.org/rfc/rfc2045.json), [errata](https://www.rfc-editor.org/errata/rfc2045).

## Section dispositions

| Section | Disposition and consequence |
| --- | --- |
| 1 — Introduction | Inherited complementary body-format model; verified erratum 2586 removes misleading Content-Disposition exception. Header comments are not capability data. |
| 2 — Definitions, Conventions, and Generic BNF Grammar | Inherited lexical conventions: type/subtype/parameter names case-insensitive; parameter values depend on their definition. Historical grammar dependencies require explicit reconciliation. |
| 2.1 — CRLF | Inherited CRLF octets 13 then 10. |
| 2.2 — Character Set | Inherited charset as octet-to-character mapping; no external guesswork in the definition of a named charset. |
| 2.3 — Message | Inherited top-level and encapsulated message distinction. |
| 2.4 — Entity | Inherited MIME entity scope; Content-* fields have MIME meaning without erasing ordinary message-header semantics. Verified typo 7120 applied. |
| 2.5 — Body Part | Inherited body-part definition; do not confuse a part with an independently authored message. |
| 2.6 — Body | Inherited recursive body definition; parser limits are implementation policy, not new source requirements. |
| 2.7 — 7bit Data | Inherited 7bit domain: short CRLF-delimited lines, no NUL/high-bit octets. |
| 2.8 — 8bit Data | Inherited 8bit domain: high-bit octets permitted, but short lines, CRLF and no NUL still apply. |
| 2.9 — Binary Data | Inherited unrestricted binary octet domain; it requires transport-safe encoding or negotiated transport. |
| 2.10 — Lines | Inherited distinction between wire lines and visual lines; do not infer paragraph boundaries before transfer decoding. |
| 3 — MIME Header Fields | Inherited MIME fields at message/part levels; grammar listing does not impose header order. Non-Content part headers are not a portable metadata channel. |
| 4 — MIME-Version Header Field | Inherited MIME-Version 1.0, comments and top-level scope. Version rich content separately; non-MIME messages require cautious local interpretation, not a false ASCII certainty. |
| 5 — Content-Type Header Field | Inherited type/subtype/parameter role and unknown-parameter ignoring; required interaction semantics cannot rely solely on an unknown optional MIME parameter. |
| 5.1 — Syntax of the Content-Type Header Field | Inherited mandatory subtype, quoted parameter syntax and case distinctions; verified 512 repairs missing grammar separator. Registration rules require current successor review. |
| 5.2 — Content-Type Defaults | Inherited text/plain US-ASCII default, qualified by non-MIME uncertainty; no type sniffing that activates rich actions. |
| 6 — Content-Transfer-Encoding Header Field | Inherited transfer encoding separates transport representation from content meaning. |
| 6.1 — Content-Transfer-Encoding Syntax | Inherited encoding tokens and default 7bit; casing of the encoding label is insignificant. |
| 6.2 — Content-Transfer-Encodings Semantics | Inherited single-valued decoding and accurate domain labels; multiple encoded forms may represent identical octets. Later binary transport standards supersede the historical absence of binary SMTP. |
| 6.3 — New Content-Transfer-Encodings | Inherited discouragement of new transfer encodings; Email Next introduces no new one. Current registration process remains under review. |
| 6.4 — Interpretation and Use | Inherited entity-local decoding, composite encoding restrictions and opaque handling of unknown encoding. RFC 6532’s update concerning message media types must be reviewed before asserting a universal composite ban. |
| 6.5 — Translating Encodings | Inherited QP/base64 translation preserves canonical octets; hard line breaks and binary bytes need distinct treatment. |
| 6.6 — Canonical Encoding Model | Canonicalization dependency: RFC 2049 supplies the full model; not yet reviewed. |
| 6.7 — Quoted-Printable Content-Transfer-Encoding | Inherited quoted-printable upper-case hex, trailing whitespace handling, hard/soft breaks, 76-character line limit and boundary avoidance. Recovery suggestions are not cryptographic canonicalization. |
| 6.8 — Base64 Content-Transfer-Encoding | Inherited MIME base64 alphabet, padding, line length and ignoring nonalphabet material when decoding. Encoding correctness is not authentication; the application may withhold structured execution for damaged representations. |
| 7 — Content-ID Header Field | Inherited globally unique Content-ID and external-body requirement; alternative semantics require RFC 2046 review. Content-ID is not authority to fetch remote content. |
| 8 — Content-Description Header Field | Inherited optional human description and encoded-word support; description must not carry hidden commands. Held spelling correction has no protocol effect. |
| 9 — Additional MIME Header Fields | Extension opportunity through Content-* fields; no invented names are registered by this draft. |
| 10 — Summary | Summary reviewed; body extensions preserve transport/message-format boundaries. |
| 11 — Security Considerations | Security treatment delegated to RFC 2046; security review remains incomplete until that document and relevant updates are assessed. |
| 12 — Authors' Addresses | Author information reviewed; no protocol requirement. |
| Appendix A — -- Collected Grammar | Collected grammar reviewed against prose, including quoted-printable productions and referenced legacy grammar. Verified separator correction must also be reflected in generated grammar fixtures. |

## Errata dispositions

| Erratum | Status | Consequence |
| --- | --- | --- |
| [2586](https://www.rfc-editor.org/errata/eid2586) | Verified | Verified: remove the nonexistent exception from comment handling. |
| [512](https://www.rfc-editor.org/errata/eid512) | Verified | Verified: restore the missing alternative separator in tspecials. |
| [3442](https://www.rfc-editor.org/errata/eid3442) | Held for Document Update | Held: example spelling only; no behavior change. |
| [3950](https://www.rfc-editor.org/errata/eid3950) | Rejected | Rejected: internal comment in MIME-Version remains permitted; do not narrow parsing. |
| [7120](https://www.rfc-editor.org/errata/eid7120) | Verified | Verified: entity-definition typo; no semantic change. |

## Proposed consequences and evidence needed

The [MIME receiver contract](../messages.md#mime-decoding-boundary) separates safe legacy presentation from activating structured interactions. Required fixtures include folded/commented MIME fields; case-sensitive boundaries; absent types and encodings; equivalent transfer encodings; hard versus soft quoted-printable breaks; padded base64; unknown encodings; and malformed encoded bodies. Cryptographic validation must operate on the exact representation selected by its security profile, not a prettified display string.

These are test requirements. No decoder implementation or interoperability result is claimed.
