---
title: MIME conformance audit
sectionNav: true
---

# MIME conformance audit

MIME conformance includes safe handling of unsupported content; it does not require every viewer to understand every format. Email Next adds a defined rich-content profile while retaining the MIME baseline.

**Coverage:** complete RFC 2049, all appendices and both retrieved errata reviewed on 19 October 2026. Dependencies, later updates and implementation testing remain open.

Source: [RFC 2049](https://www.rfc-editor.org/rfc/rfc2049.html), [metadata](https://www.rfc-editor.org/rfc/rfc2049.json), [errata](https://www.rfc-editor.org/errata/rfc2049).

## Section dispositions

| Section | Disposition |
| --- | --- |
| 1 | Inherit purpose: minimum interoperability and canonicalization; no requirement to implement all media types. |
| 2 | Inherit all ten conformance items, detailed below. “Safe” in this document is format-handling compatibility, not modern security certification. |
| 3 | Review all eight transport hazards: encoding translation, local newlines, NUL, tabs, long lines, trailing whitespace, charset translation, and dot/From-line corruption. They motivate robust encoding; they do not authorize relays to corrupt content. |
| 4 | Inherit four-stage model: local representation, media-specific canonical form, transfer encoding, MIME insertion. Optimized implementations must produce equivalent results. Reversing the model need not reproduce identical local storage. |
| 5 | Summary reviewed; no additional contract. |
| 6 | Security delegates to RFC 2046, already reviewed at base-document level. |
| 7 | Author information reviewed; no protocol behavior. |
| 8 | Acknowledgements reviewed; no protocol behavior. |
| Appendix A | Complex example reviewed: nested mixed/parallel content and encapsulated message. Illustrative placeholders and pagination must not become executable test bytes. |
| Appendix B | All 32 historical changes reviewed against current base rules: grammar, boundary ownership, fragmentation, charset/encoding, fallback, registrations and external-body security. Historical summary does not supersede operative text. |
| Appendix C | References reviewed. Current core MIME dependencies remain in scope; historical transports, media-specific manuals and superseded registration/crypto sources require explicit scoped dependency dispositions. |

## Section 2 conformance items

| Item | Inherited behavior and proposal consequence |
| --- | --- |
| 1 | Generate MIME-Version 1.0; rich profile versioning stays separate. |
| 2 | Recognize identity encodings and decode quoted-printable/base64; label and encode appropriately for the negotiated transport. |
| 3 | Unknown transfer encoding makes the entity opaque; it does not permit rich execution. |
| 4 | Interpret Content-Type and support sending plain text with necessary charset labeling; do not display arbitrary binary as text. |
| 5 | Ignore unknown parameters; required rich semantics need an independently validated profile. |
| 6 | Support stated text behavior, opaque unsupported media, decoded application export, mixed/alternative/digest structure, unknown-multipart mixed fallback, recursive message/rfc822 display and unknown-message opaque fallback. Unknown charset is not guessed for authenticated processing. |
| 7 | Unrecognized Content-Type falls back to opaque data. User-directed export is distinct from automatic execution. |
| 8 | Nonstandard non-MIME charset recovery is receive-only; generated messages retain proper MIME labeling. |
| 9 | Encoded-word-shaped tokens in specified header contexts must be valid encoded words. |
| 10 | Recognize encoded words in permitted contexts and support B/Q for supported charsets; verified erratum3933 directs recognition to RFC2047 §6. |

## Errata dispositions

| Erratum | Status | Consequence |
| --- | --- | --- |
| [5470](https://www.rfc-editor.org/errata/eid5470) | Held for Document Update | Clarifies that unknown transfer-encoding handling applies to the MIME entity. No new decoding mechanism. |
| [3933](https://www.rfc-editor.org/errata/eid3933) | Verified | Correct encoded-word recognition reference; RFC2047 review remains required. |

## Validation consequences

Round-trip fixtures must compare canonical decoded content, not assume identical local newline/storage representations. Separately verify emitted MIME bytes, unknown-content fallback and security-profile input. Test long lines, trailing spaces, tabs, binary zero bytes, non-ASCII characters, literal dot-only lines and lines beginning with From plus a space. No test execution is claimed here.
