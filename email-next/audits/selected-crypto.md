---
title: Selected TLS and archive cryptography
sectionNav: true
---

# Selected TLS and archive cryptography

Email/2 uses different cryptographic bindings for connections and stored files. TLS protects a connection. The selected age format protects an archive, transferred history or device configuration. Sharing an algorithm does not make their keys, nonces, framing or authentication interchangeable.

This review establishes source coverage and the consequences for the selected profiles. It does not establish that a library, client, server or deployment implements them correctly.

## Keep the protocol boundaries explicit

| Use | Selected binding | Consequence |
| --- | --- | --- |
| Newly defined HTTPS services | Current TLS 1.3 requirements in RFC9846 | Keep the TLS 1.3 minimum and application restrictions on early data. |
| Existing submission and mailbox access | TLS 1.3 preferred; restricted TLS 1.2 when account policy permits | TLS 1.2 uses exactly the four ECDHE/AES-GCM suites in the transport profile, with negotiated extended master secret and secure-renegotiation acknowledgement. |
| TLS 1.3 additional cipher support | AES256-GCM/SHA384 and ChaCha20-Poly1305 are recommended alongside the required baseline | Implementation support does not prove negotiation or use. These recommendations do not select TLS 1.2 ChaCha suites. |
| Archives, history transfer and device configuration | Pinned age v1.1.0 native X25519 binding | ChaCha20-Poly1305 is a required dependency of these selected operations, rather than merely an optional TLS algorithm. |

These client-adapter choices do not redefine opportunistic MX relay policy. They do not select DTLS, anonymous authentication, static key exchange, finite-field DHE, PSK suites, supplemental authorization or mandatory client certificates.

## TLS 1.2 compatibility still has a complete handshake

The selected suites are `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`, `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`, `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` and `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` (RFC5289 §3.2). The suffix selects the TLS 1.2 PRF hash. It does not select the handshake signature's hash.

The adapter inherits RFC5246's applicable record and handshake requirements. It must verify the peer's Finished and complete the authenticated handshake before releasing account credentials or operations. Handshake messages can cross records, and records can carry multiple messages; their boundaries do not delimit SMTP, IMAP or POP operations.

::: {.details summary="State, signatures, records and resumption"}

| Source | Selected consequence |
| --- | --- |
| RFC5246 §§4–6; RFC5288 §§3–4,6 | Preserve byte-length framing, directional current/pending states, exact PRF labels, AEAD inputs and record limits. TLS 1.2 GCM uses a 4-byte implicit salt, 8-byte explicit nonce and 16-byte tag. The nonce must remain unique per key; the format alone does not guarantee uniqueness. |
| RFC8422 selected ECDHE clauses | Authenticate the ephemeral parameters, validate the peer's group/public value and preserve the specified shared-secret encoding. Fixed-width NIST x-coordinates retain leading zeros; the finite-field DH stripping rule is not their encoding. |
| RFC9155 §§2–5 | Offer and check mapped signature algorithms; do not fall back to MD5 or SHA1 when the extension is absent. RSA PKCS#1 v1.5 handshake signatures remain a TLS 1.2 option, distinct from TLS 1.3 CertificateVerify. |
| RFC7627 selected full/resumed-handshake clauses | Require negotiated extended master secret and retain that state on resumption. Renaming the extension does not change its code point or derivation label. |
| RFC5746 selected initial/renegotiated-handshake clauses | Require initial secure-renegotiation acknowledgement. This does not require enabling renegotiation. If enabled, verify the previous Finished binding on every renegotiation. |
| RFC5246 §§7.2–7.4,8 | Enforce legal message order, cipher-state transitions, transcript verification and error handling. A fatal alert invalidates the failed TLS session; it does not erase uncertainty about application bytes already released. |
| RFC5246 §7.2.1 | TLS 1.2 close_notify closes both directions, unlike TLS 1.3 half-close. Neither close_notify nor transport EOF proves that SMTP accepted a message. |

RFC5246 §9 expressly allows an application profile to replace its historical mandatory suite. Its obsolete static-RSA/CBC default does not require adding that suite to this restricted profile. Current RFC10015 prohibitions and RFC9325 controls still apply.

The selected algorithm dependencies also distinguish AES256's key schedule and SHA384's initial state from their shorter-key/output relatives. SHA384 uses SHA512 processing with its own initial values; it is not a truncation of ordinary SHA512. Existing AES/GCM, SHA, HMAC and certificate-source reviews remain separate owners.

:::

### Tickets preserve authentication, not unlimited authority

RFC5077 supplies the retained TLS 1.2 ticket protocol. A client treats the ticket as opaque, protects its associated secret state and preserves the service, account, EMS and certificate-status constraints. A rejected ticket can lead to a full handshake under the same protection policy.

::: {.details summary="TLS 1.2 ticket encoding and lifetime"}

The SessionTicket extension is 35; its extension data is the ticket itself, without RFC4507's redundant inner length. NewSessionTicket is handshake type 4, occurs before ChangeCipherSpec and participates in the Finished transcript. The client cannot treat it as valid before verifying the server's Finished. When a ticket is presented, the server must not instead try stateful Session-ID resumption (RFC5077 §§3.2–3.4 and AppendixA).

The outer ticket vector is at most 65535 bytes. Its uint32 lifetime hint counts seconds from receipt; zero means unspecified. The client applies its own bounded retention policy, and the server controls actual validity. Neither the historical 24-hour suggestion nor TLS 1.3's seven-day wire limit becomes a universal TLS 1.2 ticket duration.

RFC5077 §4 recommends a server-private AES-CBC/HMAC format, but explicitly forbids clients from assuming that structure. That recommendation does not enable CBC record ciphers. The maintained backend's actual ticket format, key protection and serialization bounds need their own evidence. Reported erratum4800 identifies nested maximum sizes that cannot all fit the outer vector; it is not a published correction or permission to enlarge that vector.

:::

The reviewed updates prohibit SSL2, SSL3 and RC4; current version policy also excludes TLS 1.0/1.1. RFC7507's fallback signal was superseded and obsoleted by RFC8996. Keep TLS 1.3's independent downgrade protection. Optional ClientHello padding, if used, contains only zero bytes and must not be echoed. RFC5878 supplemental authorization, RFC7905 TLS 1.2 ChaCha and RFC7919 finite-field negotiation remain unselected branches.

## The archive format owns its own keys and nonces

The age binding uses a fresh file key, separate wrapping and payload keys, and an authenticated header. A valid encrypted file alone does not identify its writer; the surrounding archive/configuration signature remains necessary.

::: {.details summary="Pinned age v1.1.0 and ChaCha20-Poly1305 binding"}

| Part | Required distinction |
| --- | --- |
| X25519 recipient wrap | Fresh ephemeral secret; reject an all-zero shared secret. The recipient and ephemeral share bind HKDF-SHA256 key derivation. A zero 12-byte AEAD nonce belongs only to this fresh wrapping-key contract. |
| Header | Independently derived HMAC-SHA256 authenticates the header. Preserve the canonical file encoding. |
| Payload | A fresh 16-byte value is the HKDF salt, not the AEAD nonce. A derived 32-byte key protects 64KiB chunks with an 88-bit counter and final-chunk flag. Require final authentication and EOF; reject truncation and trailing bytes. |
| Application acceptance | Stage the complete file privately before installation or archive acceptance. Successful prefix decryption is insufficient. Changed plaintext requires a newly encrypted file. |

The selected bindings use the IETF ChaCha20-Poly1305 construction: 32-byte key, 12-byte nonce and 16-byte tag. Age's published reference to RFC7539 reaches the corrected successor RFC8439 without changing age's file format. Selected primary implementation source corroborates empty associated data for the wrap and payload; source inspection is not an executed conformance test. TLS record associated data and XOR nonces are not age inputs.

Native X25519 recipients use original Bech32 with HRP `age` and 62 characters; secret identities use `AGE-SECRET-KEY-` and 74 characters. Both carry 32 decoded bytes. These are not stanza raw-base64 fields. Enforce the checksum, case and conversion-padding rules; reject mixed case and nonzero or excess padding. BIP350's Bech32m migration for Bitcoin witness versions does not change age's checksum. The fixed native lengths also exclude the known variable-length insertion weakness discussed there.

Canonical serialized recipient strings are lowercase and secret identity strings uppercase. A separate human-input adapter may accept checksum-valid uniform case and canonicalize it before freezing a new object; it must not rewrite already signed bytes or infer that checksum validity authenticates an identity.

:::

## What was read

| Source | Coverage | Errata and version boundary |
| --- | --- | --- |
| RFC5246 | Complete 104-page base: all figures, structures, appendices, references and end matter | All 22 records read:10 Verified,5 Held,7 Rejected. Obsoleted by8446/9846; the restricted TLS 1.2 compatibility binding is explicit. |
| RFC5077 | Complete 20-page base, all four flows and AppendixA encoding examples | Sole record4800 is Reported. Updated by8447; obsoleted by8446/9846. Do not substitute TLS 1.3 ticket semantics. |
| RFC5289 | Complete 6-page base, including adjacent unselected suites | No matching records in the explicit all-status capture. Current metadata lists10015 as an update. |
| RFC5288,8422,5746,7627,9155 | Selected applicable algorithm, encoding, negotiation and security ranges | Selected review only; does not claim each complete base or every optional feature. |
| RFC8439 | Selected primitive, AEAD and security ranges; not the full 44-page base or all vectors | All 8 records read: Verified5689/5989/7880/6025/6257; Held6569; Rejected5675/6989. |
| age v1.1.0 | Selected conventions, file/header/payload and native X25519 ranges | Other recipient types are not selected or claimed reviewed. |
| BIP173; BIP350 | Selected Bech32 rules/vectors and correction context | No full BIP350 review or independent checksum proof. The selected age format remains Bech32. |

For RFC5246, apply verified vector/grammar corrections 1585,2864,2865,3122,3123,4109,4507,4750 and4912 where reached. Verified 2643 concerns the unselected SSL2 rollback branch. Held 4007 records a CCS-ordering explanation; published state/order requirements already apply. Held 2165/6244 concern unselected CBC text, 2390 generic AEAD padding and 4885 indentation. Rejected records 4382,5036,5352,5409,5535,6572 and3191 do not amend the selected protocol. Held or Reported text is never silently promoted to a published correction.

RFC5288 Verified 4694 corrects a misleading nonce-uniqueness assurance. RFC8422 Verified 5703 corrects its RSA reference; 6002 concerns unselected DTLS registration. Held 5466/5468 remain editorial qualifications, and Reported 8179 is not an accepted framing amendment. Read selected ECDHE framing alongside RFC5246 and the maintained implementation.

These are source observations from the recorded review snapshots. They do not certify an installed backend, prove secure erasure or randomness, execute the age test kit, or establish complete recursive coverage of every citation.

The [source inventory](source-inventory.json) retains the three complete bases' original text and metadata hashes, byte lengths and current update relationships. The [section ledger](section-ledger.json) records individual dispositions, including unselected branches. Complete reading is a separate observation; hashes and page counts do not prove it.

::: {.details summary="Selected-source ranges, kept separate from complete-base coverage"}

Ranges below are inclusive physical LF lines of the pinned original captures. They are evidence locators, not a requirement that implementers use those text files.

| Source | SHA256 | Ranges |
| --- | --- | --- |
| RFC5288 | `f68375c3f1948802240ca5b21f3aa44311ea02f877e4e240d1fc70927ecf1307` | 90–300 |
| RFC8422 | `cac45754399e5115342cf1d773a51ac5a77ad221e9336e43ceadd8f294712350` | 322–353, 600–1088, 1189–1251, 1334–1425, 1490–1539 |
| RFC5746 | `fb894a464bffd123ef7be802b63d7309b7af2bc34091683873c311556de2036d` | 215–466, 627–687 |
| RFC7627 | `3e908b1a511f5894b64b2c7867c5e0e8db43896add4d99a340fe67a07ee11a59` | 258–493, 575–651 |
| RFC8439 | `25bef70fbf7a07ff45c2fe4cb7c6ce954eac687413d8610603268b4e4415324c` | 268–647, 755–902, 975–1257, 1369–1493 |
| RFC9155 | `87c859e927ab6bbf245f4f3cd909852b28c5d253e2305cbdd715e93aa79db7d2` | 80–245 |
| age v1.1.0 | `573966238133f2a3f9243c15875c4cb69015d370a67549097accbdd87283fece` | 9–170, 236–296, 446–464 |
| BIP173 current pin | `b19eab06b264bbd15ad7f7d640fa34de8f4a8809fba8a6ecc3e165545b27a543` | 1–240, 277–344 |
| BIP350 current pin | `63634b06aa8bae88b31929674736e74964c4598684269ac2b0b140c43a7a0dec` | 1–125 |

BIP173's recorded current commit is `24e96e870fffaa257b465ce1f0370c14aac588e8`; its age-publication comparison pin is `7a104491862379e88662a39d1a2b613c907e503e`. The compared Bech32 body was unchanged; newer metadata alone does not select Bech32m. Keep the maintained age implementation inspection and its version separate from the age v1.1.0 format pin.

:::
