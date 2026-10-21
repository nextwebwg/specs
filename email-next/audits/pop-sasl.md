---
title: POP SASL authentication audit
sectionNav: true
---

# POP SASL authentication audit

Complete twelve-page RFC5034 read. No errata in refreshed dataset checked19October2026. [Source](https://www.rfc-editor.org/rfc/rfc5034.html).

| Section | Disposition |
| --- | --- |
| 1 | History reviewed. |
| 2 | Conventions reviewed. |
| 3 | SASL capability replaces2449§6.3; STLS can change mechanisms; no unadvertised initial response. |
| 4 | AUTH state, initial response, cancellation, strict base64, limits, identity preparation, security-layer transition and TLS requirements reviewed below. |
| 5 | Case-insensitive commands; case-sensitive base64; empty response and continuation grammar reviewed. |
| 6 | All examples reviewed; illustrative mechanisms are not current recommendations. |
| 7 | Security discussion throughout reviewed. |
| 8 | Registrations reviewed. |
| 9 | Acknowledgements reviewed. |
| 10 | All nine changes reviewed. |
| 11 | Normative dependencies pending. |
| 12 | Historical TLS/mechanism references require current-policy reconciliation. |
| Closing | Contacts, copyright, IPR and funding reviewed. |

## AUTH details

- Authorization state only; success prohibits further AUTH.
- Oversized initial responses use a separate challenge round.
- Equals denotes empty initial response; asterisk cancels.
- Invalid base64 fails, unlike permissive MIME decoding.
- Failure resets authentication state; success enters transaction state.
- SASL security-layer activation discards prior peer knowledge.
- TLS wraps SASL encoding; certificate checking precedes plaintext-password use.
- Authorization username preparation is separate from mailbox identity.

## Proposed consequence

Email/2 discovery records carry their authenticated context. A session upgrade requires capability refresh; previous unauthenticated claims cannot become trusted merely because the connection is now protected. Account authentication does not prove a correspondent's end-to-end identity. Current TLS and SASL mechanism selection remains separate audit work.
