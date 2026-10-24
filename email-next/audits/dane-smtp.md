---
title: SMTP DANE audit
sectionNav: true
---

# SMTP DANE audit

The complete captured [RFC7672](https://www.rfc-editor.org/rfc/rfc7672.html) text has been reviewed, including DNS examples, references and end matter. Its transport guarantees depend on authenticated discovery and the selected TLSA usage. They do not establish a correspondent's account identity.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Incremental relay authentication does not supply endpoint encryption. |
| 1.1 | Terminology | Next-hop routing, delayed delivery and DNS validation states have distinct meanings. |
| 1.2 | Background | DNSSEC authenticates DNS data and absence; unauthenticated TLS only resists passive interception. |
| 1.3 | SMTP Channel Security | Relay policy signaling differs from mailbox identity. |
| 1.3.1 | STARTTLS Downgrade Attack | STARTTLS can be stripped before TLS; email addresses do not specify per-hop policy. |
| 1.3.2 | Insecure Server Name without DNSSEC | Insecure MX discovery undermines intended-route authentication; historical claims require context alongside later MTA-STS. |
| 1.3.3 | Sender Policy Does Not Scale | Manual peer configuration motivates discovery; historical deployment claims are not current survey evidence. |
| 1.3.4 | Too Many Certification Authorities | Broad CA trust and noninteractive operation motivate DANE's different trust model. |
| 2 | Identifying Applicable TLSA Records | Locate applicable associations before deciding authentication requirements. |
| 2.1 | DNS Considerations | Resolver validation status is security input, not merely lookup success. |
| 2.1.1 | DNS Errors, "Bogus" Responses, and "Indeterminate" Responses | Errors differ from insecure responses and absence; apply verified5395 terminology correction. |
| 2.1.2 | DNS Error Handling | TLSA lookup errors make a candidate unreachable, never policy-absent. |
| 2.1.3 | Stub Resolver Considerations | Alias expansion preserves cumulative insecurity; trusted upstream validation needs a secure channel. |
| 2.2 | TLS Discovery | Secure usable, secure unusable, insecure/absent and error outcomes require distinct behavior. |
| 2.2.1 | MX Resolution | Preserve MX preference; insecure MX cannot authenticate the intended destination domain. |
| 2.2.2 | Non-MX Destinations | Address queries precede TLSA; alias validation determines candidate base domains. |
| 2.2.3 | TLSA Record Lookup | Actual port and selected base govern queries; TLSA CNAME does not change base identity. |
| 3 | DANE Authentication | Secure TLSA supplies both TLS commitment and authentication parameters. |
| 3.1 | TLSA Certificate Usages | Usage changes authentication semantics; source recommendations are not endpoint cipher selection. |
| 3.1.1 | Certificate Usage DANE-EE(3) | DANE-EE matches leaf certificate/key, ignores certificate expiry and prohibits name checks. |
| 3.1.2 | Certificate Usage DANE-TA(2) | DANE-TA requires applicable name checks and presented trust anchor; selector affects constraints. |
| 3.1.3 | Certificate Usages PKIX-TA(0) and PKIX-EE(1) | PKIX usages are discouraged and may be unusable; submission is outside scope. |
| 3.2 | Certificate Matching | A usable secure association failing authentication prohibits relay delivery. |
| 3.2.1 | DANE-EE(3) Name Checks | Do not impose certificate-name checks on DANE-EE. |
| 3.2.2 | DANE-TA(2) Name Checks | Primary TLSA base and additional next-hop identifiers reviewed; held6283 identifies insecure-MX contradiction. |
| 3.2.3 | Reference Identifier Matching | DNS-ID precedence, historical CN fallback and wildcard rules reviewed; successor applicability remains open. |
| 4 | Server Key Management | Publish old/new associations before rotation and account for caches; DNS removal is not immediate revocation everywhere. |
| 5 | Digest Algorithm Agility | RFC7671 section9 algorithm agility is a required dependency. |
| 6 | Mandatory TLS Security | Mandatory DANE delays without usable authenticated TLS, unlike opportunistic absence handling. |
| 7 | Note on DANE for Message User Agents | MUA submission needs a separate service-discovery/security profile. |
| 8 | Interoperability Considerations | Interoperability requirements do not establish deployed support. |
| 8.1 | SNI Support | Client SNI uses TLSA base; server fallback for absent/unsupported SNI preserves interoperability. |
| 8.2 | Anonymous TLS Cipher Suites | Historical anonymous-suite advice is not adopted as a new TLS profile. |
| 9 | Operational Considerations | Operational exceptions must remain distinct from authenticated delivery. |
| 9.1 | Client Operational Considerations | Explicit audit-only/disabled policy permits reduced protection, not endpoint decryption authority. |
| 9.2 | Publisher Operational Considerations | Published TLSA prohibits selective STARTTLS; RFC7671 publisher guidance remains a dependency. |
| 10 | Security Considerations | DNSSEC compromise defeats this trust model; unreachable conditions must prohibit connection attempts. |
| 11 | References | Reference reading does not close transitive dependencies. |
| 11.1 | Normative References | DNSSEC, DANE base/guidance, TLS and certificate-identity dependencies remain open. |
| 11.2 | Informative References | DNS, SRV and opportunistic-security references need applicability review. |

## Errata and source status

[Verified technical erratum5395](https://www.rfc-editor.org/errata/eid5395) corrects the reference for the no-trust-anchor meaning of indeterminate from RFC4035 to RFC4033. Under this profile that case is insecure, whereas failure to obtain the validation data needed under RFC4035 is an error. Confusing these cases can change whether delivery is permitted.

[Technical erratum6283](https://www.rfc-editor.org/errata/eid6283) is Held for Document Update. It identifies a contradiction in section3.2.2: the opening rule always uses the TLSA base domain as the primary reference identifier, while the insecure-MX sentence names the MX hostname instead. Those names can differ after alias expansion. The proposed correction uses the TLSA base domain. It is not classified as Verified; an implementation must resolve this interpretation explicitly rather than silently copy both rules.

The live all-status errata listing and RFC metadata were reconciled on 20 October 2026. Both captured records match in ID, status, original/corrected text and notes; no update or replacement relationship changed.

## Application and remaining dependencies

The [transport chapter](../transport.md#dane-discovery-and-delivery-outcomes) distinguishes discovery outcomes, authentication usages, key rotation and enforcement exceptions. No DNS resolver or SMTP DANE adapter is validated by this review.

RFC7671 sections8,9,10.1 and13 are explicit operational dependencies. DNSSEC, the base TLSA specification, current TLS guidance, certificate identity, DNS aliasing and SRV service discovery also require applicability and successor review. The historical rationale predates MTA-STS; claims about the absence of alternative discovery mechanisms must not be repeated as current universal facts. Base-text coverage is not dependency closure or security assurance.


## Relay-authentication composition

The [transport profile](../transport.md#selecting-authentication-when-policies-overlap) selects DANE when authenticated DNS binds the destination route and a usable TLSA association. MTA-STS is then not applied, rather than counted as passed. A DANE failure cannot be rescued by retrying that candidate with MTA-STS.

For an unauthenticated MX route with enforcing MTA-STS, the profile selects MTA-STS before optional TLSA discovery. RFC7672 section2.2.1 permits, but does not require, electing DANE on that route. Selecting MTA-STS does not authorize ignoring an already-required failing lookup, relabeling relay-only authentication as destination authentication, or satisfying mandatory DANE with PKIX. Secure all-unusable TLSA records retain their TLS requirement and do not suppress applicable MTA-STS.

This is an explicit profile selection, not a claim that either RFC universally mandates this precedence. It preserves the selected mechanism's SNI rule, certificate rules and current release evidence. Implementation and independent interoperability evidence must identify the source revision tested; this audit supplies no runtime acceptance credit.
