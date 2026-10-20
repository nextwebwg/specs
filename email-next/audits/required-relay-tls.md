---
title: Required relay TLS audit
sectionNav: true
---

# Required relay TLS audit

**Coverage:** complete [RFC 8689](https://www.rfc-editor.org/rfc/rfc8689.html), including both examples, references and end matter. Reported erratum 7705 and rejected erratum 8593 reviewed. The reported DANE certificate-name issue remains unresolved pending the DANE audit.

## Finding

Sender-selected relay protection already has an SMTP extension. It requires participating relays and authenticated routing, but trusts those relays and is not end-to-end encryption. The separate TLS-Required: No header requests weaker transport handling; it is not an alternative spelling of the requirement.

| Section | Disposition |
| --- | --- |
| 1 | Two opposite mechanisms: REQUIRETLS requires authenticated protected relay; TLS-Required:No requests relaxing recipient transport policy. Neither is end-to-end encryption. |
| 1.1 | Requirement vocabulary and ABNF reviewed. |
| 2 | Argument-free REQUIRETLS EHLO and MAIL parameter; adds11 octets; applies relay/submission/LMTP. Requires TLS, authenticated MX via DNSSEC orMTA-STS, validated certificate viaPKIX orDANE, and fresh postTLS capability. |
| 3 | Only TLS-Required:No is defined, at most once. Requests best-effort delivery despite recipient policy, while still preferring available STARTTLS. No Yes header equivalent exists. |
| 4 | Message tagging propagates selected transport handling. |
| 4.1 | MAIL REQUIRETLS overrides a conflicting header. Alias redistribution tags all resulting instances identically. |
| 4.2 | Distinguishes required and optional transport paths. |
| 4.2.1 | Authenticate routing and TLS, require postTLS capability, try remaining MX hosts on failure, otherwise fail without transmitting. Reports5.7.30 or5.7.10. Reported7705 identifies DANE/name-check tension; unresolved pending DANE audit, not silently accepted. |
| 4.2.2 | TLS-Required:No requests trying delivery despite unsuccessful policy/TLS checks, but cannot force a server to accept without TLS. Unsupported hops need not honor it uniformly. |
| 4.3 | Originator policy may select requirement without per-message prompting. Requirement uses SMTP negotiation; optional override uses header. Neither implies recipient device support. |
| 4.4 | Access/delivery agents should follow8314; relay requirement alone does not prove protected end-user access. |
| 5 | Bounces generally inherit REQUIRETLS and suppress original body as RET=HDRS even if RET=FULL requested. Empty-return-path bounce exception says lack of downstream REQUIRETLS should not itself cause discard; lost reports and metadata leakage remain possible. |
| 6 | Reoriginators should preserve requirements to extent feasible; user-side mediators may lack envelope policy. No universal propagation guarantee or permission to decrypt. |
| 7 | Registers REQUIRETLS, TLS-Required andX.7.30; status code checked in preceding live registry review. |
| 8 | Threat model separates network protection from compromised relays. |
| 8.1 | Passive resistance depends on actual TLS security. |
| 8.2 | Required TLS resists stripping and certificate substitution; MX authentication resists redirection to a valid attacker certificate. |
| 8.3 | Malicious relays can lie or strip requirements; content remains visible absent end-to-end encryption. |
| 8.4 | Optional override can ignore advertised DANE/MTA-STS policy, but server enforcement remains decisive. Rejected8593 does not restrict mechanism to misconfiguration reports only. |
| 9 | References reviewed; general TLS/DNSSEC/DANE/MTA-STS/DSN dependencies remain open. |
| 9.1 | Previously reviewed SMTP,STARTTLS,message format and8314 are not dependency closure. Historical6125/7525 require successor reconciliation. |
| 9.2 | Mediator,access,submission and content-encryption references do not specify complete Email Next behavior. |
| Appendix A | Informative examples reviewed; not copied as executable SMTP fixtures. |
| A.1 | Example lacks numeric220 before TLS and shows an extra posthandshake greeting; use3207 state rules rather than copying this dialogue. |
| A.2 | Demonstrates No override; not the default absence of a transport requirement. |

| Front/end matter | Abstract, status, copyright, acknowledgements and author address reviewed. |

## Email Next consequence

Treat transport policy as independent from content-encryption fallback. Permission for an ordinary readable copy does not authorize inserting TLS-Required: No. Requiring end-to-end encryption does not by itself prove that relay metadata is protected. Record both policies in the send plan.

A provider offering REQUIRETLS must preserve the message's envelope requirement through its queues and alias expansion. User-side reorigination may not have that evidence; do not invent it from a message's appearance. Explicitly track newly originated replies and forwards under their own policies.

Account for failure-report exposure. The standard suppresses returned bodies for REQUIRETLS bounces, but headers and diagnostics can still be sensitive. Its empty-return-path exception and potentially lost bounces prevent an unconditional claim that every associated report followed the same protected path. A stricter Email Next metadata profile needs an explicit redaction/failure contract.

Required cases: stripped capability, invalid routing evidence, failed certificate validation, alternative MX success, conflicting No header and MAIL parameter, alias expansion, header-only bounce, unavailable protected return path, and a malicious relay. No live REQUIRETLS deployment test is claimed.
