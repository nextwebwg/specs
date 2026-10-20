---
title: Internationalized headers audit
sectionNav: true
---

# Internationalized headers audit

UTF-8 headers are an existing upgrade capability. Rich message content can use encoded MIME over older infrastructure, while internationalized envelope addresses and native UTF-8 headers require the appropriate transport support.

**Coverage:** complete eleven-page RFC6532 and both retrieved errata read and individually assessed on 19 October 2026. RFC6530/6531, Unicode normalization and access-protocol handling remain separate dependencies.

Sources: [RFC6532](https://www.rfc-editor.org/rfc/rfc6532.html), [errata](https://www.rfc-editor.org/errata/rfc6532).

| Section | Disposition |
| --- | --- |
| 1 | Inherit native UTF-8 header model and distinction between embedded encoding and SMTP transport authorization. Replaces5335. |
| 2 | Terminology and requirements reviewed; 8bit means octets above7F, not arbitrary malformed UTF-8. |
| 3 | Only stated grammar rules extended; field names remain ASCII. SMTP transmission requires SMTPUTF8. |
| 3.1 | Inherit valid UTF-8 per3629, NFC SHOULD and NFKC SHOULD NOT. Do not normalize received signed bytes or silently collapse mailbox identities. |
| 3.2 | Inherit UTF-8 extensions to VCHAR, ctext, atext, qtext, text and dtext; do not automatically extend every MIME token. Reported6036 remains unadopted. |
| 3.3 | ASCII Message-ID generation is permitted and advantageous in mixed threads; new profile selects it for generation without rejecting valid received UTF-8 IDs. |
| 3.4 | Inherit998octet hard line limit excludingCRLF and78character recommendation. Count separately, never truncate an address to fit. |
| 3.5 | MIME message subtypes may newly permit transfer encodings; message/global explicitly does. This is not blanket permission to base64 existing message/rfc822. Nested encoding can arise and needs bounded processing. |
| 3.6 | For messages using this extension, avoid encoded-word generation; conversion of imported text must preserve valid field syntax. Decoded punctuation cannot be reparsed as new identities. |
| 3.7 | Full registration reviewed: message/global has no parameters, permits anyCTE, recommends identity encoding where transport permits, and is opaque to unaware clients. Embedded protected or encoded content does not itself make an internationalized envelope routable. |
| 4 | Inherit full-length comparisons, storage/overflow concerns, Unicode similarity and certificate identity issues. Verified3153 points signature discussion to6530section13. |
| 5 | Registration reviewed; no new media-type request needed for forwarded internationalized messages. |
| 6 | Acknowledgements reviewed; no protocol behavior. |
| 7 | References reviewed. |
| 7.1 | Normative UTF-8/normalization/SMTPUTF8 dependencies remain separately tracked. |
| 7.2 | Informative MIME/crypto/historical references reviewed; cryptographic binding not specified here. |
| Authors | Contact information reviewed; no protocol behavior. |
| Front matter | Abstract, status and copyright reviewed; licensing boilerplate does not define wire behavior. |

## Errata

| Record | Status | Disposition |
| --- | --- | --- |
| [3153](https://www.rfc-editor.org/errata/eid3153) | Verified | Signature discussion is RFC6530 §13. |
| [6036](https://www.rfc-editor.org/errata/eid6036) | Reported | Proposed MIME token extension is not an adopted rule. Keep field-specific syntax distinctions explicit. |

## Proposed profile decisions

Generate ASCII Message-IDs for interoperability. Accept valid internationalized identifiers when receiving them, with exact identity and references preserved. Do not transliterate a recipient mailbox or invent an ASCII alias because a route lacks SMTPUTF8.

Use native UTF-8 headers only on a delivery path authorized for them. ASCII envelope addresses alone are insufficient: UTF-8 header values, including MIME body-part headers, can also require the extension. UTF-8 body text encoded with ordinary MIME is a different case and does not by itself require SMTPUTF8.

Forwarded internationalized messages can use message/global with suitable transfer encoding inside a compatible outer message. This preserves an embedded original; it does not make the original's non-ASCII recipient routable through an ASCII-only server. Unknown recipients may see an opaque attachment. Do not promise seamless legacy rendering from this mechanism alone.

Proposed acceptance cases include multibyte lines exceeding octet limits while under character limits, ASCII addresses with UTF-8 Subject, a UTF-8 body-part header, ASCII headers with encoded UTF-8 body, unsupported internationalized recipient without alias guessing, and message/global carried in an ASCII outer message. Signature verification uses original protected bytes, not normalized display text. No implementation result is claimed.


## Historical experiment

The [RFC5335 audit](internationalized-header-history.md) closes the superseded base-text review and its two captured verified errata. Its alternate-address syntax and ASCII-only message-ID limitation are not current RFC6532 requirements. A historical paired address is not evidence that two delivery destinations share a principal or encryption key.
