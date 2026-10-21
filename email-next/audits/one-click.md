---
title: One-click unsubscribe audit
sectionNav: true
---

# One-click unsubscribe audit

**Coverage:** complete nine-page [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058.html), including all examples and end matter. Verified errata 5117, 8927 and 5559 and rejected erratum 5558 reviewed in the retrieved RFC Editor dataset. DKIM, list-header, HTTP and form-encoding dependencies remain open.

## Finding

A mail client can offer a deliberate action without making ordinary link retrieval perform that action. The standard achieves this for one narrow operation with signed action headers, a fixed POST body, no ambient browser credentials and user consent. It is useful prior art for rich interactions, not a general authorization protocol for forms.

| Section | Disposition |
| --- | --- |
| 1 | Separates scanner fetches from intentional unsubscribe POSTs. Supports an action within the mail UI, not arbitrary execution of HTML forms. |
| 2 | Uppercase requirement vocabulary reviewed. |
| 3 | Sender and receiver responsibilities are separate; no general form-submission facility. |
| 3.1 | Exactly one List-Unsubscribe and one List-Unsubscribe-Post field; one HTTPS URI with optional non-HTTP alternatives. Fixed action value, signed headers, recipient/list encoded in URI, no cookies/HTTP authorization/context, opaque unforgeable component recommended, no HTTPS redirects. Ordinary2369 behavior remains unchanged. |
| 3.2 | Receiver POSTs the fixed pair only with user consent; consent acquisition is unspecified. Multipart/form-data recommended, URL-encoded body permitted. Do not treat lack of a second website confirmation as lack of consent. |
| 4 | At least one valid DKIM signature covers both list headers in h=. Without it receivers SHOULD NOT offer one-click. Domain authentication does not prove a human submitted a form. |
| 5 | Fixed header ABNF imports5322 productions; no arbitrary POST arguments or general action grammar. |
| 6 | Message access transfers unsubscribe capability; opaque URI is not identity binding. Fixed payload constrains arbitrary-form attacks; no ambient web context. Requests can disclose address activity. |
| 7 | Registers List-Unsubscribe-Post; no Email/2 generic action registration. |
| 8 | Examples reviewed as fragments, not complete authenticated messages. |
| 8.1 | Simple URL-encoded POST uses26-byte fixed payload; complete DKIM evidence omitted from snippet. |
| 8.2 | Mailto alternative and HTTPS query example preserve selected HTTPS target and fixed body. |
| 8.3 | Verified5117/8927 correct boundary parameter; Verified5559 removes spurious equals sign from request target. Rejected5558 does not change124-byte body to126; final CRLF changes actual length. Generate framing from actual bytes. |
| 9 | 2369,6376,HTTP and7578 dependencies remain open;5322 base review exists. |

| Front and end matter | Abstract, standards status, copyright and author addresses reviewed. |

## Email/2 consequence

Preserve one-click unsubscribe as its own existing operation. Do not reinterpret List-Unsubscribe-Post as permission to submit arbitrary fields, follow redirects or reuse browser cookies. A valid DKIM signature authenticates the relevant domain-signed headers; it does not turn the holder of a forwarded unsubscribe link into a verified human author.

Inline answers are new contributions under the interaction contract. Rendering, prefetching, scanning and focusing a control must not create them. A deliberate submission identifies the exact form revision, values and audience and applies current authorization before transmission. Any future external-action profile needs its own destination binding, payload limits, credential rules and redirect policy.

Required cases include automatic GET scans, no user consent, uncovered action headers, duplicate fields, a forwarded bearer URL, a redirect response, ambient cookies and a malicious arbitrary POST body. Full DKIM and HTTP behavior has not been implemented or tested by this audit.
