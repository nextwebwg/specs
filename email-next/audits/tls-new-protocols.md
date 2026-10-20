---
title: TLS for new protocols audit
sectionNav: true
---

# TLS for new protocols audit

RFC9852 supports the selected service policy: TLS1.3 is required and TLS1.2 compatibility is optional. The proposal can keep TLS1.3 as its minimum without adding TLS1.2 support. Where the library reliably negotiates the highest supported version, configure a minimum rather than unnecessarily fixing the maximum.

## Consequences and boundaries

The TLS requirement protects the HTTPS service connection. It does not establish mailbox identity, MLS admission, application authorization, certificate validation correctness, safe resumption, or early-data safety. The service minimum is a proposal selection aligned with §§4–5, not an independent requirement on ordinary email transport. DTLS is outside this update.

## Coverage

All 355 lines and 7 source pages read, including all tables/examples, references and end matter. Official metadata reviewed; no subsequent updates listed. Captured errata records: 0. The live all-status listing on 20 October 2026 explicitly reports no matching errata; current metadata confirms no subsequent updates or replacement. No implementation tests were performed.

| Section | Disposition |
| --- | --- |
| front | Abstract, status, copyright, and complete contents read. |
| 1 | New TLS protocols require 1.3; DTLS excluded. Security rationale is not deployment evidence. |
| 2 | BCP14 interpretation read. |
| 3 | PQC migration rationale; no PQ algorithm or readiness guarantee selected. TLS1.2 feature freeze reference remains separate dependency. |
| 4 | New protocols MUST default to 1.3. Deployment considerations MAY add nondefault 1.2. With reliable highest-version negotiation clients SHOULD configure minimum only. Service selection retains minimum 1.3, no 1.2 requirement. |
| 5 | Explicitly replaces 9325 new-protocol 1.3 SHOULD with MUST and 1.2 MUST with MAY; no DTLS change. |
| 6 | All renegotiation, key exchange, RC4/CBC, attack and handshake privacy discussion read. Do not substitute narrative for complete 1.2 extension controls or claim all TLS1.3 privacy risks resolved. |
| 7 | No IANA actions. |
| 8 | Full references read. |
| 8.1 | All six normative references read; 9846 and9851 require separate full review, not assumed equivalent to older TLS specs. |
| 8.2 | Every informative citation read, including10015 and attack/PQC references; cited research not independently audited. |
| Authors | All author details and end of document read. |

## Remaining scope

RFC9846 is the current TLS1.3 reference in these documents and still requires its own full review. RFC9851 feature freeze and RFC9847 registry semantics remain separate dependencies where applicable. Cipher-definition documents and DTLS are not selected for implementation by this audit. Live registry state, library settings, negotiated protocol behavior, certificate checks, backend consistency and replay protection require separate evidence.

Sources: https://www.rfc-editor.org/rfc/rfc9852.txt ; https://www.rfc-editor.org/rfc/rfc9852.json ; https://www.rfc-editor.org/errata/rfc9852
