---
title: MTA-STS audit
sectionNav: true
---

# MTA-STS audit

The complete captured [RFC8461](https://www.rfc-editor.org/rfc/rfc8461.html) text has been reviewed, including both appendices and end matter. MTA-STS can protect a delivery route between providers. It does not authenticate an Email/2 account or prevent providers from reading plaintext.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Authenticated relay transport does not protect plaintext from providers. |
| 1.1 | Terminology | Policy domain follows next-hop routing, not necessarily mailbox domain. |
| 2 | Related Technologies | MTA-STS success cannot override failing DANE validation. |
| 3 | Policy Discovery | DNS announces policy; HTTPS authenticates its contents, not recipient endpoint keys. |
| 3.1 | MTA-STS TXT Records | TXT concatenation, filtering, CNAME and change-token equality reviewed; prefix whitespace discrepancy unresolved. |
| 3.2 | MTA-STS Policies | Modes, MX patterns, A-labels, lifetime and grammar reviewed; own duplicate and extension rules apply. |
| 3.3 | HTTPS Policy Fetching | HTTPS200 only, no redirects or HTTP caching; valid cached policy survives fetch failure. |
| 3.4 | Policy Selection for Smart Hosts and Subdomains | Smart-host domain governs; no parent policy inheritance or address-literal policy mechanism. |
| 4 | Policy Validation | Validate both permitted MX and STARTTLS certificate before enforcement decision. |
| 4.1 | MX Host Validation | Wildcard matches exactly one leftmost label. |
| 4.2 | Recipient MTA Certificate Validation | Certificate SAN, expiry and trusted chain required; optional revocation reviewed. |
| 5 | Policy Application | Enforce blocks invalid candidates; testing permits delivery; none removes active policy. |
| 5.1 | Policy Application Control Flow | Preserve MX order and check policy updates before permanent failure. |
| 6 | Reporting Failures | TLSRPT diagnostics exclude none-mode failures; reports are not endpoint authentication. |
| 7 | Interoperability Considerations | Interoperability requirements do not prove current provider support. |
| 7.1 | SNI Support | Client SNI names policy host or MX; SMTP server fallback differs from strict HTTPS behavior. |
| 7.2 | Minimum TLS Version Support | Source requires TLS1.2 or TLS1.3 or higher support; current TLS guidance review remains. |
| 8 | Operational Considerations | Operational rollout must account for cached policy and DNS lifetimes. |
| 8.1 | Policy Updates | Publish HTTPS body before DNS token; preserve delivery under old policies during propagation. |
| 8.2 | Policy Delegation | Delegated hosting retains original policy-host certificate identity; proxy cache exception is distinct. |
| 8.3 | Removing MTA-STS | Publish none policy before removal; wait for all previously served policies to expire. |
| 8.4 | Preserving MX Candidate Traversal | Preserve candidate traversal and loop prevention; backup misconfiguration may remain latent. |
| 9 | IANA Considerations | Existing registrations do not allocate an Email/2 extension. |
| 9.1 | Well-Known URIs Registry | Registered well-known mta-sts.txt path reviewed. |
| 9.2 | MTA-STS TXT Record Fields | TXT v/id registry and Expert Review procedure reviewed. |
| 9.3 | MTA-STS Policy Fields | Policy version/mode/max_age/mx registry and Expert Review procedure reviewed. |
| 10 | Security Considerations | Protection depends on obtained policy and certificate trust assumptions. |
| 10.1 | Obtaining a Signed Certificate | Fraudulent valid certificate defeats authentication. |
| 10.2 | Preventing Policy Discovery | Initial discovery suppression and cache-expiry attacks remain; refresh mitigates exposure. |
| 10.3 | Denial of Service | Malicious long-lived policy can prolong denial after DNS recovery; protect tenant-controlled names. |
| 10.4 | Weak Policy Constraints | Wildcard can authorize tenant hosts with valid certificates. |
| 10.5 | Compromise of the Web PKI System | WebPKI compromise affects policy and SMTP; revocation tradeoffs remain. |
| 11 | References | Reference review does not establish transitive dependency closure. |
| 11.1 | Normative References | Normative certificate, TLS, IDNA, HTTP and URI dependencies require current applicability review. |
| 11.2 | Informative References | DANE, DNSSEC, revocation and registry dependencies remain separately applicable. |
| Appendix A | MTA-STS Example Record and Policy | Complete testing-mode example reviewed; soliciting reports is not enforcement. |
| Appendix B | Message Delivery Pseudocode | Complete pseudocode reviewed; expiry, smart-host, none-mode and certificate-argument discrepancies prevent verbatim adoption. |

## Errata and source status

The captured RFC Editor metadata lists Proposed Standard status with no updates or obsolescence relationships. The full errata capture contains four entries, all **Reported**, not approved corrections:

- [6253](https://www.rfc-editor.org/errata/eid6253): CRLF-only prose conflicts with grammar permitting bare LF.
- [6285](https://www.rfc-editor.org/errata/eid6285): exact initial TXT prefix conflicts with delimiter whitespace allowed by grammar.
- [6525](https://www.rfc-editor.org/errata/eid6525): capitalization of the expiry prohibition.
- [7282](https://www.rfc-editor.org/errata/eid7282): proposes reducing max_age digit width. A wider syntax does not itself override the semantic maximum; this proposed grammar change is not adopted as an approved correction.

The policy grammar also spells one reference `sta-policy-alphanum` rather than `sts-policy-alphanum`; no corresponding entry was found in the captured errata. The live all-status listing and current RFC metadata were reconciled on 20 October 2026: captured errata IDs, statuses, original/corrected text and notes match, with no changed metadata relationships.

## Implementation consequences

The [transport chapter](../transport.md#provider-transport-policy-and-endpoint-protection) applies the relay-versus-endpoint distinction, cache rules, rollout ordering and first-contact limits. Its inherited details are kept in a disclosure.

Appendix B is illustrative pseudocode, not a complete implementation: it declares but does not call the expiry helper; supplies a policy where its certificate helper describes a hostname argument; derives the policy domain from the recipient without the smart-host exception; and does not explicitly handle the none-mode reporting exclusions or update check before permanent failure. Implementations must follow the governing prose rather than copy this example unchanged.

This base review does not complete certificate-validation, TLS guidance, DNSSEC/DANE, IDNA, HTTP caching or well-known URI dependency review. No MTA-STS adapter or deployed-provider interoperability has been validated here.
