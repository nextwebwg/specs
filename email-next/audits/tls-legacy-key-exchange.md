---
title: Legacy TLS key exchange audit
sectionNav: true
---

# Legacy TLS key exchange audit

RFC10015 strengthens obsolete TLS1.2 key-exchange prohibitions. The selected service already requires TLS1.3, so this update does not require adding a TLS1.2 implementation or banning TLS1.3 finite-field groups. It matters when describing legacy compatibility and when reviewing other endpoints that share keys or infrastructure.

## Consequences and boundaries

For any separately selected TLS1.2 compatibility profile, clients must not offer and servers must not select static finite-field DH, ephemeral finite-field DH, or RSA key exchange. Static ECDH remains discouraged, as do fixed-DH client certificate types. RSA authentication is distinct from RSA key exchange. Registry D markings do not erase these normative differences. Shared-key cross-protocol risks warrant fleet review even where this service itself uses TLS1.3.

## Coverage

All 1082 lines and 21 source pages read, including all tables/examples, references and end matter. Official metadata reviewed; no subsequent updates listed. Captured errata records: 0. The live all-status listing on 20 October 2026 explicitly reports no matching errata; current metadata confirms no subsequent updates or replacement. No implementation tests were performed.

| Section | Disposition |
| --- | --- |
| front | Abstract, status, copyright, and complete contents read. |
| 1 | Full scope and attack/interoperability rationale read. Deprecations apply to (D)TLS1.2, not TLS1.3 algorithms generally. |
| 1.1 | BCP14 requirements language read. |
| 2 | 1.2 static FFDH MUST NOT; static ECDH SHOULD NOT; fixed DH certificate types SHOULD NOT. No inference banning RSA signatures. |
| 3 | 1.2 FFDHE MUST NOT; 1.3 FFDHE MAY be offered because relevant configuration weaknesses differ. Service does not thereby select an FFDHE group. |
| 4 | 1.2 RSA key exchange MUST NOT. Does not prohibit RSA signing certificates or ECDHE_RSA authentication. |
| 5 | Registry D category references9847; no new Email Next registration. |
| 5.1 | Entire Table1 static DH suite list read; D registry changes reflect 1.2 prohibition. |
| 5.2 | Entire Table2 static ECDH list read; D registry marker does not strengthen SHOULD NOT into MUST NOT. |
| 5.3 | Entire Table3 DHE suite list, including PSK_DHE names, read; 1.2 prohibition. |
| 5.4 | Entire Table4 RSA and RSA_PSK suite list read; 1.2 prohibition. |
| 5.5 | All four fixed certificate entries and values read:3,4,65,66. SHOULD NOT usage from section2. |
| 6 | All Table6 updates read: staticFFDH/DHE/staticRSA strengthen to MUST NOT, staticECDH unchanged, fixed certificates newly SHOULD NOT. |
| 7 | Registry instructions fully read; live IANA registry independently unreconciled. |
| 8 | All Raccoon, curve, sidechannel, fault and customgroup attack examples read; forward secrecy and keyreuse limitations understood. No new cryptographic implementation promised. |
| 9 | Full references read. |
| 9.1 | Every normative citation read. Cipher definitions,9846,9847 andDTLS dependencies are not recursively audited. |
| 9.2 | All research and registry citations read; source references do not prove present fleet configuration. |
| Acknowledgments | Complete acknowledgments read. |
| Authors | All author details and end of document read. |

## Remaining scope

RFC9846 is the current TLS1.3 reference in these documents and still requires its own full review. RFC9851 feature freeze and RFC9847 registry semantics remain separate dependencies where applicable. Cipher-definition documents and DTLS are not selected for implementation by this audit. Live registry state, library settings, negotiated protocol behavior, certificate checks, backend consistency and replay protection require separate evidence.

Sources: https://www.rfc-editor.org/rfc/rfc10015.txt ; https://www.rfc-editor.org/rfc/rfc10015.json ; https://www.rfc-editor.org/errata/rfc10015
