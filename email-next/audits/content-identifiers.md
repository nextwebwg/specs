---
title: Content and message URL audit
sectionNav: true
---

# Content and message URL audit

Content-ID URLs already connect HTML to MIME resources. They identify content; they do not authenticate it or grant access to other messages.

**Coverage:** entire RFC2392, including introductory material and copyright statement, and all four retrieved errata read and assessed on 19 October 2026. URL grammar updates and HTML aggregation remain separately tracked dependencies.

Sources: [RFC2392](https://www.rfc-editor.org/rfc/rfc2392.html), [errata](https://www.rfc-editor.org/errata/rfc2392).

| Section | Disposition |
| --- | --- |
| Abstract and changes from RFC2111 | Reviewed scope and corrected historical angle-bracket examples. RFC2392 replaces RFC2111. |
| 1 | Inherit distinction between a MIME body-part reference and a reference to an entire message. |
| 2 | Inherit cid and mid syntax, percent encoding, long-form mid message context, and containing-entity selection for repeated IDs in alternatives. See detailed decisions below. |
| 3 | Inherit identifier privacy concerns. IDs reveal information even when content is protected; opaque generation is proposed. Addressability supplies no authorization. |
| 4 | References reviewed; MIME and related-container audits exist. Historical RFC822 and RFC1738 dependencies require current grammar reconciliation, not blind substitution. |
| 5 | Acknowledgements reviewed; no protocol requirement. |
| 6 | Contact information reviewed; no protocol requirement. |
| 7 | Copyright statement reviewed; no protocol requirement. |

## Addressing decisions

The source requires support for long-form mid references from implementations claiming RFC2392 conformance. It also permits, but does not require, looking up cid references throughout a message store. Email/2 proposes a narrower automatic resource-loading policy: only the selected related object supplies rendered resources. This restriction does not redefine either URL scheme. A mid link can be offered as deliberate navigation subject to local access controls; it must not silently embed another message or disclose whether an inaccessible message exists.

Percent escapes are decoded once into identifier characters. The verified example correction maps `cid:foo4%25foo1@bar.net` to `<foo4%foo1@bar.net>`. Decoding again would change identifier identity. A slash inside an identifier is encoded; the unescaped slash in long-form mid separates message and content identifiers. Generated examples must preserve this distinction.

The source's repeated-ID exception uses the term multipart/alternate; the MIME subtype is multipart/alternative. Repeated identifiers in alternative representations must be resolved by the enclosing MIME selection rules, not rejected indiscriminately or resolved by first match. After applicable alternative selection, multiple eligible matches remain an error for automatic rich rendering.

The examples are not ready-to-run fixtures: they include an unquoted slash-containing type parameter, a boundary typo, a misplaced blank line, abbreviated image data and the charset spelling usascii. Use MIME grammar and registered charset names in independently constructed fixtures.

## Errata

| Record | Status | Disposition |
| --- | --- | --- |
| [454](https://www.rfc-editor.org/errata/eid454) | Verified | Correct percent-decoded Content-ID example; implement single decoding. |
| [3382](https://www.rfc-editor.org/errata/eid3382) | Held for update | Boundary example typo; generated delimiter must match the declared boundary. |
| [6176](https://www.rfc-editor.org/errata/eid6176) | Verified | Remove blank line before part headers; otherwise those lines become body text. |
| [6175](https://www.rfc-editor.org/errata/eid6175) | Held for update | Missing word in contextual indexing explanation; no behavior change. |

## Proposed acceptance cases

- A percent sign survives one decoding step; an encoded percent followed by hexadecimal characters is not decoded twice.
- An encoded slash is part of an identifier, while a literal slash separates a long-form mid reference.
- Two alternatives with the same Content-ID resolve to the selected usable representation.
- Two eligible siblings with the same identifier do not resolve by document order.
- A missing local resource does not resolve from another message, even if that message contains the same identifier.
- A mid navigation link never becomes an automatic embedded-resource fetch.

These are requirements for future fixtures, not reported implementation results.
