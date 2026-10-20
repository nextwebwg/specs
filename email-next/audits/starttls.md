---
title: SMTP STARTTLS audit
sectionNav: true
---

# SMTP STARTTLS audit

**Coverage:** complete nine-page RFC3207, including example, appendix and end matter; verified erratum324 and rejected erratum4442 reviewed. [RFC3207](https://www.rfc-editor.org/rfc/rfc3207.html); [errata](https://www.rfc-editor.org/errata/rfc3207). RFC7817 and modern TLS policy dependencies remain open.

| Section | Disposition |
| --- | --- |
| 1 | TLS protects the SMTP connection; historical SSL terminology and TLS1.0 reference are not current algorithm recommendations. |
| 1.1 | Requirement vocabulary reviewed. |
| 2 | STARTTLS advertises an argument-free EHLO capability and adds an argument-free command. |
| 3 | Advertisement means current ability to negotiate, not endpoint identity or downstream protection. |
| 4 | 220 begins TLS before further SMTP;501 rejects parameters;454 follows local transport policy. STARTTLS ends a pipeline group. Base public-MX interoperability rule differs from submission/relay authentication policy; later transport-policy standards require separate audit. |
| 4.1 | Evaluate achieved authentication and privacy before continuing. Insufficient protection leads to termination/refusal, not a protection badge. Historical certificate guidance is updated by7817 and later identity standards. |
| 4.2 | Reset SMTP state after handshake; discard pre-TLS peer/session knowledge and issue fresh EHLO. Capabilities may change. Do not advertise or invoke STARTTLS inside an active TLS session. |
| 4.3 | Submission can use STARTTLS; current submission/TLS recommendations require separate audit. |
| 5 | Example correctly issues a new EHLO after TLS and removes STARTTLS from the new advertisement. |
| 6 | Hop TLS is not end-to-end confidentiality or message authorship. Stripping/altering STARTTLS is an active attack; required-TLS configuration must resist fallback. Enforce actual negotiated policy and discard insecure session observations. |
| 7 | Verified erratum324 supplies missing1847 MIME-SEC reference. Current SMTP5321 reviewed; SASL,AUTH,submission,TLS and identity updates remain dependencies. |
| Appendix | Change-list section numbers refer to prior2487. Rejected4442 concerns a non-authoritative HTML cross-link, not an accepted textual correction. |

| Front/end matter | Status, abstract, copyright, author contact and acknowledgement reviewed. |

## Email Next consequence

Maintain independent transport-security and message-security records. A protected SMTP connection cannot establish that the recipient decrypted a message or that its claimed author signed it. Transport policy may require TLS even when message content is already encrypted, because routing and submission metadata remain relevant.

After TLS, re-negotiate SIZE, PIPELINING, 8BITMIME and other session capabilities. A pre-TLS value cannot authorize a post-TLS operation simply because the socket is now encrypted. Independently authenticated correspondent records remain under their own evidence rules; SMTP reset does not delete pinned identity history.

Required cases: stripped advertisement,454 under required policy, failed handshake, changed post-TLS capabilities, stale authentication advertisement, nested STARTTLS attempt and successful hop TLS carrying an unauthenticated message. No TLS connection has been tested by this audit.
