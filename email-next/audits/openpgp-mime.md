---
title: OpenPGP MIME audit
sectionNav: true
---

# OpenPGP MIME audit

**Coverage:** full15-page RFC3156, including examples, registrations and end matter. One rejected editorial erratum3443 reviewed. [RFC3156](https://www.rfc-editor.org/rfc/rfc3156.html); [erratum3443](https://www.rfc-editor.org/errata/eid3443). Current OpenPGP algorithms are covered by the [format audit](openpgp-format.md); selected media registrations are reconciled below, while implementation and remaining dependencies stay separate.

| Section | Disposition |
| --- | --- |
| 1 | Defines OpenPGP MIME control, signature and public-key types; updates2015. Packaging does not select modern algorithms or identity policy. |
| 2 | ASCII armor required for transfer; message/partial preferred to multipart armor if fragmentation is needed. Email Next has not adopted automatic fragmentation. |
| 3 | Signed content, including signed-then-encrypted, constrained to7bit after MIME encoding and no unprotected trailing whitespace. Preserve meaningful spaces through encoding; whitespace-only headers must not become accidental header/body separators. From-space protection recommended. Encryption-only allowance is distinct. Accepting received encodings does not authorize canonical-byte guessing. |
| 4 | Encryption wraps canonical MIME entity; exactlytwo parts, quoted application/pgp-encrypted protocol, Version:1 control and application/octet-stream ciphertext. Historical cipher example is not an approved generation vector. |
| 5 | Signed container uses application/pgp-signature, exactlyone pgp-prefixed micalg and twoparts. Canonicalize content then transfer-encode then include MIMEheaders. Detachedsignature coversheadersandencodedbody. Boundary-precedingCRLF belongsdelimiter,notautomaticallysigneddata; absentfinalCRLFmustnotbeinvented. Historic hash list is not adopted as modern policy. |
| 6 | Two sign-then-encrypt compositions are permitted; exact selected profile must specify which generation path and which receive paths apply. |
| 6.1 | Nestedmultipart/signed insideencryptedentity supportsforwarding; prose multipart/signature is inconsistentwithactualdefinedmultipart/signed/example and mustnotbeimplementedasnewtype. |
| 6.2 | CombinedOpenPGP signing/encryption allowed withsamecanonicalization. Decryptingtoanewmultipart/signed representation isallowedbybaseprofile but is a new plaintextdisclosure requiring userpolicy; not an automaticforwardingpermission. |
| 7 | application/pgp-keys carriesarmoredtransferablepublickeys. Importingkeymaterial doesnotverifyitsmailboxbinding,trust,revocationfreshnessorcapability. |
| 8 | Historicalcanonical-textsignaturewhitespacewarning reviewed. CurrentOpenPGP9580behaviorandalgorithmrestrictionsrequireseparateaudit; do not generalize2001wordingintonewsecurityclaims. |
| 9 | Three media registrations and their live templates reconciled below. |
| 9.1 | Encryptedcontrolregistrationhasnoparametersand7bittext;notciphertextmedia. |
| 9.2 | Signatureregistrationhasnoparametersand7bitarmoredtext;filenameextensionsarenotvalidation. |
| 9.3 | Keyregistrationhasnoparametersand7bitarmoredtext;keyownershipnotassertedbytype. |
| 10 | Trademarknotereviewed;nowireeffect. |
| 11 | Historicalacknowledgementsreviewed;2440referenceisnotcurrentalgorithmselection. |
| 12 | Contactsreviewed;noadditionalrequirements. |
| References | 1847/2046baseaudited;2480gatewayandcurrentOpenPGP9580dependenciesopen;historical1848/1991/2015notadoptedasnewsecuritysuite. |

| Front/end matter | Status, abstract, copyright and acknowledgement reviewed. |

## Errata and source ambiguities

Erratum3443 proposes changing the capitalization of MIME-Version in an example. It was rejected because field names are case-insensitive. Receivers must not reject valid capitalization variants.

Section6.1 calls the signed body multipart/signature, while the defined type and example are multipart/signed. The audit uses the defined type; no registered multipart/signature behavior is inferred. Example armor and obsolete hashes are historical illustrations, not new-profile test vectors.

## Proposed implementation boundary

The MIME profile can be reused without reproducing its historical key-management user experience. Automatic discovery would still need a separately authenticated identity binding, continuity and revocation policy. A public-key attachment supplies material, not authorization to replace a known key.

The signed bytes differ from display bytes: MIME headers and encoded body participate, while the CRLF introducing a boundary is a delimiter. Any implementation experiment must include final-line and transfer-encoding vectors before reporting signature interoperability. Reflowed, sanitized or repaired text must not substitute for this representation.

Required cases include missing Version control, wrong control type, signature/algorithm mismatch, header folding, absent final CRLF, delimiter CRLF, encoded trailing spaces, whitespace-only header lines, From-space transport changes and a key attachment claiming an existing identity. No cryptographic experiment has been completed here.

## Selected current media registrations

The current [IANA application registry](https://www.iana.org/assignments/media-types/media-types.xhtml#application) lists `application/pgp-encrypted`, `application/pgp-signature` and `application/pgp-keys`, each referencing RFC3156. All three registration templates specify no required or optional parameters and 7bit text. The encrypted type is the control part, not the ciphertext itself. The signature template lists `asc`/`sig` extensions and the key template `asc`; filenames do not authenticate those contents.

The templates retain historical RFC2440 security references. Registration currency does not revive obsolete algorithm policy or establish mailbox ownership. The 20 October 2026 check covers these three entries and their templates, not every OpenPGP or media-type registration.
