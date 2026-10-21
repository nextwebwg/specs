---
title: S/MIME enhanced security services audit
sectionNav: true
---

# S/MIME enhanced security services audit

The certificate-binding attributes in ESS are a live S/MIME compatibility dependency. RFC8551 Section 2.5 refers to them for receiving and sending signed messages; Section 3 also uses ESS's nested-message model. They cannot be dismissed merely because RFC8098 mentions ESS receipts as an optional alternative to ordinary disposition notifications.

**Coverage:** complete [RFC2634](https://www.rfc-editor.org/rfc/rfc2634.html) (58 pages) and its sole listed update, [RFC5035](https://www.rfc-editor.org/rfc/rfc5035.html) (17 pages), including both ASN.1 modules, examples, flowcharts, references and end matter. All eight current errata were read and reconciled with the captured records. This is source review, not CMS implementation or interoperability evidence.

## What applies

A certificate hash binds the signature to the intended certificate; it does not make the certificate issuer trustworthy or replace path, revocation, identity or application-authorization checks. RFC5035 supplies algorithm agility, including SHA-256 as the version-two default. The old SHA-1 structure is historical compatibility behavior, not a new Email/2 signing choice.

For legacy S/MIME handling, keep the inner author's signature distinct from an outer gateway or mailing-list signature. Outer attributes can have different signers and purposes. ESS does not turn a gateway signature into the original author's authority, or a signed receipt into evidence that a person understood a message.

ESS security labels, translated labels, secure list expansion and signed receipts require their own application policy. Reviewing them does not select them as Email/2 managed-group behavior. A privacy mark is not access control, a label cannot enforce confidentiality in arbitrary recipient software, and an unsolicited receipt request does not authorize an Email/2 conversation effect.

::: {.details summary="RFC2634 section dispositions"}

| Sections | Disposition |
| --- | --- |
| 1 | Four services have distinct applicability; certificate binding remains live. |
| 1.1, 1.1.1, 1.1.2 | Inner signature, encryption and outer signature bind different bytes and attributes; complete construction read. |
| 1.2 | Both detached and opaque signature wrappers considered; full layer examples read. |
| 1.3, 1.3.1–1.3.3 | Receipts, labels and list expansion use different layers; no interchangeable authority. |
| 1.3.4 | Attribute placement, single attribute/value restrictions and countersignature restrictions reviewed. |
| 1.4 | Adding a signer and wrapping a message differ; required copied attributes must not disappear. |
| 1.5 | Historical OID registration discussion; current registry state not inferred. |
| 2, 2.1 | Receipt binds a signed object, not human understanding; remember issuance and retained correlation evidence. |
| 2.2, 2.2.1, 2.2.2 | Innermost request, no receipt-of-receipt, identical requests, explicit destinations and retained validation inputs. |
| 2.3 | Authenticate before request processing; conflicting verified requests prevent receipt generation. Full policy flowchart read. |
| 2.4, 2.4.1 | Complete creation procedure, direct receipt content, digest bindings and encryption disclosure considered; expansion history stays outside the receipt. |
| 2.5, 2.6 | Destination policy and complete receipt validation reviewed; no delivery-state inference from an unverified object. |
| 2.7, 2.8 | Receipt request and receipt syntax, identifiers, destination multiplicity and version reviewed. |
| 2.9, 2.10, 2.11 | Content hints may disclose metadata; signature digest and signed references have explicit original-object bindings. |
| 3, 3.1, 3.1.1, 3.1.2 | Authenticate labels, compare verified copies, preserve unknown-policy failure handling. |
| 3.2, 3.3, 3.3.1–3.3.4 | ASN.1 components and policy-dependent classification hierarchy reviewed; numerical order and privacy marks do not define access rights. |
| 3.4, 3.4.1, 3.4.2 | Translation requires separately trusted authority and unique policy identifiers; understood original policy takes precedence. |
| 4, 4.1, 4.1.1 | List agent is a cryptographic recipient; authenticate consistent expansion history and detect loops. |
| 4.2, 4.2.1 | All layers, attributes and six expansion examples reviewed; selected MLS groups do not inherit this re-encryption service. |
| 4.2.3, 4.2.3.1–4.2.3.3 | Separate processing branches and flowchart reviewed; no invented missing Section 4.2.2. |
| 4.3, 4.4 | Complete receipt-policy combination matrix and expansion-history syntax reviewed. |
| 5, 5.1, 5.1.1–5.1.3 | Same public key in different certificates can change validation meaning. |
| 5.2, 5.2.1–5.2.3 | Hash binding limits substitution; it cannot establish CA trust or eliminate denial of service. |
| 5.3, 5.3.1, 5.3.2 | Authorization certificate and policy constraints are separate from signature arithmetic. |
| 5.4, 5.4.1 | Read with RFC5035 replacement; do not freeze the original SHA-1-only definition. |
| 6 | Receipt disclosure, label leakage, list loops and decryption-oracle risks reviewed. |
| A | Complete ASN.1 module read; replacement module is in RFC5035. |
| B, C | References and acknowledgements read; ASN.1/X.411/CMS dependencies are not implied closed. |

:::

::: {.details summary="RFC5035 section dispositions and errata"}

| Sections | Disposition |
| --- | --- |
| 1, 1.1, 1.2 | Algorithm agility and exact replacement scope reviewed. |
| 2 | Both attributes evaluated independently; four signature/hash outcomes require distinct handling. |
| 3 | Version-two certificate list, policy constraints and signed single-value attribute reviewed. |
| 4 | Entire DER certificate is hashed with the selected algorithm; apply Verified2364. |
| 5, 6 | Version-one compatibility retained; issuer/serial details do not replace the certificate hash. |
| 7 | Unsupported certificate-hash protection and conflicting version-one/version-two bindings are distinct from signature validity. |
| 8 | Certificate, CMS and UTF-8 references read; recursive closure remains open. |
| A | Entire replacement ASN.1 module, OIDs, defaults and imported types reviewed. |

RFC2634 **Rejected6562** does not replace the certificate-list rules; its verifier points to RFC5035. RFC5035 **Verified2364** corrects `certHash` to use `hashAlgorithm`, not a hardwired SHA-1 algorithm. **Held1007**, **Held2365** and **Held2366** concern joined module definitions, a section reference and version-one hash wording. **Held6566** proposes certificate-list clarification; it is not promoted to a verified replacement. **Rejected1480** and **Rejected6735** do not alter the ASN.1 tagging or default algorithm syntax.

The source has a spaced “2. 7” heading and an indented Section 4.3; both are included in the explicit review ledger. These formatting issues do not remove requirements.

:::

No certificates, signed receipts, mailing-list expansion or security-label deployment were tested. A compatibility implementation still needs concrete vectors for substituted certificates, conflicting attributes, unknown policies, mismatched hashes, distinct wrapper signers and receipt disclosure. Current CMS/certificate dependencies and ASN.1 compilation remain separate evidence requirements.
