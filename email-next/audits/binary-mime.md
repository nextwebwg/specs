---
title: Chunking and binary MIME audit
sectionNav: true
---

# Chunking and binary MIME audit

**Coverage:** complete twelve-page [RFC 3030](https://www.rfc-editor.org/rfc/rfc3030.html), including examples, appendix and end matter. Verified erratum 349 reviewed. This audit does not claim a working SMTP implementation.

## Finding

Upgraded transport peers can send MIME more efficiently without defining a new conversation protocol. CHUNKING changes message framing; BINARYMIME separately permits arbitrary binary content. Each is negotiated for the current hop. Neither proves downstream support or end-to-end protection.

| Section | Disposition |
| --- | --- |
| 1 | CHUNKING avoids DATA sentinel scanning; BINARYMIME separately avoids transport-encoding overhead. Neither changes application semantics or authentication. |
| 2 | CHUNKING advertises BDAT, which counts exact canonical message octets and sends data immediately. Collect MAIL/RCPT outcomes first. Each chunk has a reply; zero-length LAST allowed. Failure requires consuming/discarding the declared chunk and already-pipelined chunks, stopping new chunks and RSET. Do not mix DATA/BDAT in one transaction. DATA support remains required. Incorrect lengths desynchronize parsing. |
| 3 | BINARYMIME requires CHUNKING and BODY=BINARYMIME; preserve every content octet. DATA is forbidden for this body mode. MIME text canonicalization still applies. Unsupported downstream binary requires lossless valid conversion or permanent failure; no nested transfer encodings. The source explicitly says accept improperly declared Binary CTE then recommends a DSN; this is not permission to send unnegotiated binary. Protected-byte changes remain constrained by the selected security profile. |
| 4 | Examples are illustrative transport dialogues, not full interoperability fixtures. |
| 4.1 | The86-byte bodyless pseudo-message illustrates one LAST chunk; do not treat missing normal message fields as a complete5322 fixture. |
| 4.2 | Verified349 corrects first chunk description from10000 to100000 octets; total100324 and zero-byte LAST remain consistent. Multiple replies correspond to chunks, not distinct application events. |
| 5 | Historical statement of no additional known security issues does not remove current framing, resource or protected-byte obligations. |
| 6 | MIME,SMTP,pipelining and8BITMIME successors reviewed separately; submission and remaining dependencies open. |
| 7 | Author address reviewed; no protocol behavior. |
| Appendix A | Changes from1830 include example count correction and zero-byte LAST illustration; no independent new requirements. |
| End matter | Status,abstract,working-group history,conventions,copyright,warranty and funding acknowledgement reviewed. |

## Email/2 consequence

Count the final transmitted message octets for every BDAT chunk. Do not add DATA dot-stuffing or a DATA terminator. Chunk boundaries do not divide application events, and a positive reply to an intermediate chunk does not establish final message acceptance.

On a chunk failure, do not append more newly generated chunks or switch to DATA within the failed transaction. Drain already-sent chunks according to the transport protocol and reset before another transaction. A lost final acknowledgement still requires the application's duplicate-safe delivery behavior.

Keep a baseline MIME representation that can travel over older infrastructure. Server upgrades may remove encoding overhead only where doing so preserves the selected signature/encryption representation. A downstream capability failure does not authorize decrypting content or rewriting authenticated bytes. If no permitted conversion preserves the protected object, report delivery failure under the existing policy.

Required cases include CHUNKING without BINARYMIME, binary mode without CHUNKING, zero-byte LAST, incorrect byte counts, chunk failure with data already in flight, DATA/BDAT mixing, intermediate success followed by final failure, and a downstream server unable to carry the protected representation.
