---
title: 8-bit MIME transport audit
sectionNav: true
---

# 8-bit MIME transport audit

**Coverage:** full seven-page RFC6152, including example, references and front/end matter. Rejected technical erratum5646 reviewed. [RFC6152](https://www.rfc-editor.org/rfc/rfc6152.html); [erratum5646](https://www.rfc-editor.org/errata/eid5646).

| Section | Disposition |
| --- | --- |
| 1 | 8BITMIME carries octets with the high bit set but retains SMTP line constraints; it is not binary transport. |
| 2 | EHLO advertises 8BITMIME without arguments. MAIL BODY accepts 7BIT or 8BITMIME; no new verbs. |
| 3 | Negotiate before sending 8-bit content and use one BODY parameter. Preserve every bit, apply dot stuffing, and retain the final content CRLF. Without support, use a lossless valid 7-bit MIME transformation or permanent failure; never send unsupported 8-bit content anyway. Protected objects impose additional conversion constraints. |
| 4 | Example demonstrates negotiation and DATA, not rich capability or end-to-end security. Its QUIT response uses250 rather than the5321-defined221; generators follow5321, not that illustrative line. |
| 5 | Negotiation retains existing mail threats. No added confidentiality or author authentication is provided. |
| 6 | Registration context reviewed. |
| 6.1 | Registers SMTP and submission capability; live registry check remains separate. |
| 7 | Acknowledgements reviewed. |
| 8 | MIME2045/2046 and SMTP/message-format5321/5322 base audits recorded; ABNF and full dependency closure remain open. |

| Front/end matter | Abstract, status, copyright and author contacts reviewed. |

## Erratum disposition

Erratum5646 incorrectly proposes reversing the meaning of the dot-stuffing explanation. It was rejected: stuffing protects content lines that would otherwise look like the DATA terminator. Implementations must not apply the proposed correction.

## Email Next consequence

8BITMIME is a connection capability. It does not promise downstream support, SMTPUTF8 headers, binary transport, rich interaction or encrypted endpoints. A sender can choose 7-bit-safe MIME before protection to avoid later re-encoding. A relay must not rewrite a signed object and preserve its former integrity claim.

Required cases: absent advertisement, duplicate BODY parameter, 8-bit content under 7BIT, long lines, leading dot, dot-only line, final CRLF, later-hop failure and protected content that cannot be converted. No SMTP implementation was exercised here.
