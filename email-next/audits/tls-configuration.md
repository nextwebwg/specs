---
title: TLS configuration audit
sectionNav: true
---

# TLS configuration audit

RFC9325 shows why a TLS1.2 minimum alone does not establish a secure HTTPS service. Its current metadata lists two later updates, RFC9852 and RFC10015. The first updates new-protocol requirements to support and default to TLS1.3, while allowing TLS1.2 as an additional nondefault deployment option. Both updates have completed base reviews, as does the current [TLS 1.3 specification](tls13.md). Applicable source dependencies and implementation evidence remain separately scoped.

## Service consequences

Use authenticated HTTPS without cleartext fallback. Verify the intended action-service hostname and full certificate chain; SNI or a valid certificate for another endpoint is insufficient. Support ALPN/SNI and enforce protocol/name boundaries across the service fleet. Reusing HTTP requires the selected HTTP protocol's ALPN behavior, not a new Email/2 ALPN identifier. A proxy or alternate backend must not weaken the service's security.

TLS1.2 compatibility requires additional controls: renegotiation_info and extended_master_secret support, safe cipher/key selection, no TLS record compression, secure AESGCM nonces and session-ticket lifecycle. The source recommends ECDHE_RSA/ECDHE_ECDSA with AES128/256GCM and forward secrecy; the [RFC10015 review](tls-legacy-key-exchange.md) records the strengthened key-exchange prohibitions. TLS1.3 removes renegotiation and record compression, but resumption, certificate validation, key usage and early-data replay remain relevant. Certificate compression is a different mechanism and is not prohibited merely because record compression is unsafe.

The [selected HTTPS service profile](../service-answers.md#establish-the-protected-connection) requires TLS1.3, defines no TLS1.2 mode and disables early data. The [mail submission/access adapter](../transport.md#connection-confidentiality-indications) separately defines restricted TLS1.2 compatibility and also disables early data. These are profile selections, not a claim that9325 bans allHTTP earlydata: §3.10 refers HTTP to8470. Business deduplication alone is not evidence that early bearer disclosure/replay is safe. A failed early attempt cannot silently produce a fresh submission identity.

Tickets require encryption/authentication, sufficiently strong protection, regular keyrotation and old-key destruction, bounded validity andcare with long-lived1.2 sessions. Example durations in the source are not user constraints or universal fixedlimits.1.3 ECDHE resumption is recommended to retain forward secrecy. TLS implementations must have a revoked-certificate distrust strategy; the source does not establish perfect/immediate global revocation. TLS forwardsecrecy is separate from MLS lifecycle and retained server plaintext.

## Coverage

All1994 lines/34pages of base text, including full references and AppendixA, read in five bounded chunks. Official metadata reviewed. The captured errata set is empty; the live all-status listing on 20 October 2026 explicitly reports no matching errata, and current metadata matches the retained update relationships. No TLS configuration, handshake or deployment tests performed. The listed updates now have separate completed base reviews; transitive dependency closure remains pending.

| Section | Disposition |
| --- | --- |
| front | Complete status, abstract, copyright andcontents read. |
| 1 | Scope, migration rationale, minimum-not-ceiling guidance, and5288/6066 updates read. Historical PQ/ECH deployment statements are not current status claims. |
| 2 | Security terminology and BCP14 reviewed. |
| 3 | General recommendations introduction read. |
| 3.1 | Version hierarchy reviewed. |
| 3.1.1 | SSL2/3 andTLS1.0/1.1 prohibited; baseTLS1.2 MUST/TLS1.3 SHOULD and newer-preference reviewed. The completed9852 review supplies the updated new-protocol rule. |
| 3.1.2 | DTLS versions reviewed; no DTLS transport selected for service. |
| 3.1.3 | No fallback below1.2; obsolete SCSV distinct from1.3 negotiation protection. |
| 3.2 | Strict protected channel, implicitTLS preference and HTTP HSTS support/use requirements read; no bearer cleartext fallback. |
| 3.3 | TLS1.2 compression discouraged; removed in1.3. Higher-layer compression still a separate risk. |
| 3.3.1 | Certificate compression distinct from CRIME-sensitive record compression;1.3 extension conditional dependency. |
| 3.4 | Resumption authenticated/encrypted; ticket cipher/key rotation/destruction/lifetime;1.2 old-session limits;1.3 ECDHE resumption preference and privacy reviewed. Example rotation durations not universal quotas. |
| 3.5 | TLS1.2 renegotiation_info support and client acknowledgement enforcement; extended_master_secret support mandatory. NotTLS1.3 features. |
| 3.6 | Post-handshake auth/multiplexing boundary andHTTP2 guidance reviewed. |
| 3.7 | HTTPS SNI support; unknown-name refusal and mismatch handling; historical ECH note does not establish present deployment status. |
| 3.8 | ALPN support required; no-common-protocol fatal outcome and client-selection check; HTTP endpoint reuses HTTP ALPN, no new application token inferred. |
| 3.9 | Both cross-protocol and inconsistent same-service backend threats reviewed; equivalent fleet security and ALPN. |
| 3.10 | Early-data risks andHTTP8470/QUIC9001 guidance reviewed; the selected service disables early data and defines no replay-safe early-data binding. |
| 4 | Cipher selection context read. |
| 4.1 | All cipher prohibitions/preferences reviewed; forward secrecy, noNULL/RC4/sub112, avoidstaticRSA/staticDH/DHE; see the RFC10015 review for strengthened prohibitions. |
| 4.2 | Four ECDHE RSA/ECDSA AESGCM suites, CBC encrypt_then_mac caveat, ECDSA determinism/fault concerns reviewed. |
| 4.2.1 | Suite preference, oldMTI discouragement, P256/X25519 anduncompressed pointformat reviewed. |
| 4.3 | TLS1.3 cipher recommendations delegated to8446§9.1; see the current [RFC9846 review](tls13.md). |
| 4.4 | Confidentiality/integrity record limits, TLS fail-first vsDTLS, keyupdate guidance andnumerical recommendations reviewed. |
| 4.5 | Public key strengths, DHE2048/ECDH224 minima, RSA2048, SHA256 andnoSHA1/MD5 requirements reviewed;RFC10015 supersedes affected older key-exchange allowances. |
| 4.6 | TruncatedHMAC forbidden. |
| 5 | Web/mail/etc applicability;existing protocol MTI not silently rewritten;QUIC/constrained networks outside direct scope. |
| 5.1 | Confidentiality/integrity/endpoint authentication goals; bearerHTTPS fits, opportunistic unauthenticatedTLS does not. |
| 5.2 | Opportunistic compatibility exception context read; not selected for credentialed service. |
| 6 | NoIANA actions. |
| 7 | Security introduction andbaseTLS dependency scope read. |
| 7.1 | Validate intended hostname separately from chain; insecurely discovered host not automatic reference identifier. |
| 7.2 | AESGCM security reference reviewed. |
| 7.2.1 | TLS1.2 sequence-number nonce recommendation strengthens5288;1.3 deterministic construction differs. |
| 7.3 | Full compromise-source list andforward-secrecy explanation reviewed; no endpoint/archive guarantee follows. |
| 7.4 | DH exponentreuse threats, group/curve validation andsafe-curve recommendations reviewed. |
| 7.5 | Full revocation discussion read: strategy required, stapling limits, noinstant universal solution; historical deployment claims not refreshed here. |
| 8 | Complete reference lists read. |
| 8.1 | All normative citations read; full dependency contents not recursively reviewed. |
| 8.2 | All informative citations read; draft references andregistry state remain separately scoped. |
| A | Every listed normative difference from7525 read. |
| Acknowledgments | Complete acknowledgments read. |
| Authors | All three author records andend matter read. |

## Updates and remaining work

The base's new-application dual-version requirement is superseded by RFC9852 §§4–5: TLS1.3 support/default required; TLS1.2 optional as an additional nondefault option for deployment considerations. The complete [RFC9852 review](tls-new-protocols.md) records that update. The complete [RFC10015 review](tls-legacy-key-exchange.md) records strengthened restrictions on older TLS1.2/DTLS1.2 key-exchange methods; these are not a general prohibition on RSA signatures or TLS1.3 finite-field groups. RFC9852 references RFC9846 as the currentTLS1.3 specification; its [complete review](tls13.md) distinguishes current implementation requirements from the earlier8446 text.

Remaining work distinguishes applicable extension/cipher/certificate source dependencies from actual library configuration and acceptance evidence. The current owners select the service and mail-adapter profiles; a completed source review does not prove their implementation. QUIC/HTTP3 transport review is separate. Historical source remarks about ECH, postquantum work, CRLite or browser deployment are not adopted as present-day factual claims.

Sources: https://www.rfc-editor.org/rfc/rfc9325.html ; https://www.rfc-editor.org/rfc/rfc9325.json ; https://www.rfc-editor.org/info/rfc9852/ .
