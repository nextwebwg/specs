---
title: SMTP message size audit
sectionNav: true
---

# SMTP message size audit

**Coverage:** complete nine-page RFC1870, including example and front/end matter. Zero matching errata in refreshed dataset checked19October2026. [RFC1870](https://www.rfc-editor.org/rfc/rfc1870.html).

| Section | Disposition |
| --- | --- |
| 1 | Size declaration enables early rejection, not guaranteed acceptance. |
| 2 | Large MIME objects motivate resource negotiation; this does not define application content limits. |
| 3 | SIZE advertisement may omit its decimal limit. Zero means no fixed maximum; omission means unknown maximum. MAIL SIZE has1–20 digits and occurs once; command-line allowance grows26 characters. |
| 4 | Advertised fixed limits permit early permanent rejection. Temporary storage limits remain possible. |
| 5 | Count message octets including headers and CRLF, excluding DATA terminator and extra dot-stuffing octets. Count encoded transmitted representation, not decoded attachment size. |
| 6 | Declared size is ideally exact, otherwise a generally conservative estimate. It MUST NOT delimit DATA. |
| 6.1 | 452 means temporary storage shortage;552 means fixed-size excess. Server may accept an underestimated message but need not. |
| 6.2 | Reset or quit after rejection; retry temporary failure later, report permanent failure. MAIL250 does not guarantee DATA or final acceptance. |
| 6.3 | An underestimated message may fail after transfer. An accepted declaration should not later receive size-based552 unless actual size exceeds declaration. |
| 6.4 | Size failures can be per recipient. Requeue452 recipients, not permanent552 recipients, while preserving successful recipients. |
| 7 | Minimal client may compare advertised size only. Minimal server still accepts extended MAIL. An omitted advertised limit requires resource checking before positive response to declared size. |
| 8 | Example exercises mixed recipient outcomes and later DATA acceptance; no all-recipient success inference. |
| 9 | Resource declarations can facilitate denial of service; enforce actual consumption limits independently of claims. |
| 10 | Acknowledgements reviewed. |
| 11 | Historical SMTP/message/MIME references map to reviewed modern base documents; DNS and complete dependency closure remain open. |
| 12 | Author contact information reviewed. |

## Email/2 consequence

A rich contribution's size is its final transmitted MIME representation, including encoding and protection overhead. Splitting deliveries by recipient may produce different sizes. A size rejection does not authorize removing encryption, dropping content, moving attachments to a host or changing the audience.

An authorized smaller representation is a new delivery-plan decision, not a transport retry that silently changes meaning. Preserve immutable event semantics and explain any changed disclosure. Large decimal declarations must be parsed without integer overflow or allocating the claimed amount.

Required cases: no SIZE advertisement, bare SIZE, SIZE0, exact boundary, underestimated body, base64 overhead, dot stuffing, mixed recipient failures and rejection after MAIL acceptance. No SMTP server has been tested here.

The [size accounting experiment](../evidence/README.md#smtp-size-accounting-experiment) supplies six finite checks for octet counting and limit parsing. It does not exercise SMTP acceptance or retry behavior.
