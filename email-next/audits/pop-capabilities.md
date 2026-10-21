---
title: POP capability negotiation audit
sectionNav: true
---

# POP capability negotiation audit

The complete base text of [RFC2449](https://www.rfc-editor.org/rfc/rfc2449.html), including grammar, examples, registrations, references and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. POP base behavior, later extensions and live registry closure remain separately scoped.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | CAPA advertises optional server behavior; it does not discover recipient encryption or rendering support. |
| 2 | Conventions Used in this Document | Requirement keywords and example directions reviewed. |
| 3 | General Command and Response Grammar | Command/response grammar reviewed; printed ASCII ranges include DEL despite printable comments, and greeting grammar omits conventional spaces. These discrepancies are not adopted as new Email/2 syntax. |
| 4 | Parameter and Response Lengths | CAPA-supporting servers accept commands up to 255 octets including CRLF, or larger supported-extension limits; first response line remains 512 octets. |
| 5 | The CAPA Command | CAPA works before and after authentication; tags are case-insensitive, values can change by state, and integrity-protected authentication calls for rechecking capabilities against active downgrades. |
| 6 | Initial Set of Capabilities | Initial capabilities reviewed; APOP uses the greeting challenge rather than a duplicate CAPA tag. |
| 6.1 | TOP capability | TOP means optional header/body-prefix retrieval support, not complete-message validation. |
| 6.2 | USER capability | USER advertises USER/PASS support without promising availability for every account. |
| 6.3 | SASL capability | SASL advertises AUTH mechanisms and initial-response support; historical mechanisms are not a present security recommendation. |
| 6.4 | RESP-CODES capability | RESP-CODES marks bracket-prefixed response text as machine-readable protocol status. |
| 6.5 | LOGIN-DELAY capability | LOGIN-DELAY gives seconds since successful authentication; preauthentication value is the largest possible account value, with USER indicating a useful authenticated refresh. |
| 6.6 | PIPELINING capability | Pipelined commands execute and match responses in order; blocking writes must respect transport windows. This does not order conversation events across devices. |
| 6.7 | EXPIRE capability | EXPIRE gives minimum retention, with deliberately imprecise starting time; zero permits implicit deletion of RETR messages on UPDATE. Preauthentication value is the smallest possible retention. |
| 6.8 | UIDL capability | UIDL advertises optional retrieval identifiers; it does not supply endpoint-authenticated event IDs. |
| 6.9 | IMPLEMENTATION capability | IMPLEMENTATION is diagnostic identification; clients must not select behavior from this string. |
| 7 | Future Extensions to POP3 | POP remains download-and-delete; mailbox/upload extensions are discouraged. Basic retrieval cannot depend on arbitrary additional capabilities. |
| 8 | Extended POP3 Response Codes | Hierarchical case-insensitive response codes permit unknown detail to be ignored; human-readable text is not a recipient-capability channel. |
| 8.1 | Initial POP3 response codes | Initial failure classifications reviewed separately from cryptographic policy. |
| 8.1.1 | The LOGIN-DELAY response code | LOGIN-DELAY on USER can disclose account existence and should be avoided under the described conditions. |
| 8.1.2 | The IN-USE response code | IN-USE means authentication succeeded but the maildrop is busy; it is not evidence of lost encryption support. |
| 9 | IANA Considerations | Capability and response-code registration requirements reviewed; no Email/2 POP capability is registered by this draft. |
| 10 | Security Considerations | Capability disclosure can aid attack selection; stronger-mechanism discovery can improve security, but does not authenticate peer devices. |
| 11 | Acknowledgments | Acknowledgments reviewed; no protocol requirements. |
| 12 | References | Complete reference list reviewed; historical authentication, ABNF, SMTP, IMAP and registration dependencies need independent applicability review. |
| 13 | Authors' Addresses | Author end matter reviewed; no protocol requirements. |
| 14 | Full Copyright Statement | Copyright and warranty terms reviewed; this audit summarizes rather than replaces the RFC. |

## Upgrade boundary

CAPA is useful prior art for state-sensitive negotiation. It advertises the server on this connection, not the software or keys belonging to another email recipient. A failed CAPA command permits ordinary legacy probing; it cannot authorize plaintext fallback for an established encrypted conversation. A changed list after protected authentication must be interpreted in its protocol state rather than merged indiscriminately with an unauthenticated cache.

## Retention and retrieval

EXPIRE is not an exact per-message expiry timestamp. In particular, EXPIRE 0 permits the server to treat retrieved messages as deleted when entering UPDATE. An upgraded client must durably retain downloaded bytes and processing state before ending a session that can remove its only server copy. TOP previews are insufficient for whole-message authentication, and UIDL is retrieval bookkeeping rather than an authenticated event identity.

## Source discrepancies

Section 3 describes several ASCII ranges as printable while including DEL. Its greeting grammar also lacks ordinary space characters around the response text. Several capability tables use AUTHENTICATION where the protocol state is called AUTHORIZATION elsewhere. These are recorded source discrepancies, not approved errata or permissions to invent a replacement POP grammar. Current POP interoperability and successor requirements must be resolved in the transport adapter independently.
