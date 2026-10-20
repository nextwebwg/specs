---
title: Authentication-results audit
sectionNav: true
---

# Authentication-results audit

Complete 54-page [RFC8601](https://www.rfc-editor.org/rfc/rfc8601.html), grammar, all examples, references and end matter reviewed. All three retrieved errata are reported, not verified. Current registry reconciliation and dependent method reviews remain open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Framework reports assertions, not inherently trustworthy evidence. |
| 1.1 | Purpose | Common extensible result transport within a trust domain; presence alone insufficient. |
| 1.2 | Trust Boundary | Trust depends on producer and path; encapsulation/re-entry can lose provenance. |
| 1.3 | Processing Scope | Reports completed evaluations, not parameters sufficient to rerun them. |
| 1.4 | Requirements | No universal rejection mandate; participating providers undertake boundary obligations. |
| 1.5 | Definitions | Definitions reviewed in full. |
| 1.5.1 | Key Words | BCP14 conventions reviewed. |
| 1.5.2 | Internationalized Email | UTF8/EAI extensions reviewed. |
| 1.5.3 | Security | Route authorization and cryptographic authentication distinguished. |
| 1.5.4 | Email Architecture | All architecture roles and diagram reviewed. |
| 1.5.5 | Other Terms | Producer and consumer roles reviewed. |
| 1.6 | Trust Environment | Local-domain forged assertions must be removed at ingress; authserv-id alone supplies no integrity. |
| 2 | Definition and Format of the Header Field | Format overview reviewed. |
| 2.1 | General Description | Trace field, multiple results and repeated fields permitted. |
| 2.2 | Formal Definition | Complete ABNF read; reported6026 separator issue retained unresolved. |
| 2.3 | Property Types (ptypes) and Properties | Every property type read; unknown types must not drive handling. |
| 2.4 | The "policy" ptype | Local policy can override authentication result; arbitrary policy labels do not define cryptographic meaning. |
| 2.5 | Authentication Service Identifier Field | Identifier uniqueness, configuration and historical identifiers reviewed; not necessarily DNS name. |
| 2.6 | Version Tokens | Field and method versions independent; unsupported semantics not inferred from familiar result words. |
| 2.7 | Defined Methods and Result Values | Method-specific result contracts reviewed. |
| 2.7.1 | DKIM | All seven DKIM outcomes and signature-tag properties read; current crypto updates remain applicable. |
| 2.7.2 | SPF | All SPF outcomes read; mailfrom/helo scope, local-part omission guidance and reported6027 conflict recorded. |
| 2.7.3 | "iprev" | All reverse-DNS outcomes read; no none outcome; policy.iprev property. |
| 2.7.4 | SMTP AUTH | All AUTH outcomes and example read; smtp.auth authorization identity differs from MAIL AUTH parameter and reverse-path. |
| 2.7.5 | Other Registered Codes | All additional registered methods read; individual method specifications remain dependencies. |
| 2.7.6 | Extension Methods | Experimental methods require explicit ADMD consent; no public capability negotiation through unknown methods. |
| 2.7.7 | Extension Result Codes | Experimental results require consent; registration and consumer handling reviewed. |
| 3 | The "iprev" Authentication Method | Full reverse/forward algorithm, configurable bounds and limitations read; not endorsement as identity authentication. |
| 4 | Adding the Header Field to a Message | Producer adds own field, never appends to existing field; methods unordered; only evaluated properties reported. |
| 4.1 | Header Field Position and Interpretation | Configured trust, unsupported results/methods/types, trace order, UI testing and attachment rules reviewed. |
| 4.2 | Local Policy Enforcement | Border rejection avoids forged-origin backscatter; client filtering cannot retroactively reject SMTP. |
| 5 | Removing Existing Header Fields | All removal rules read, including EAI labels, trusted external exceptions, signature impact and unsupported versions. |
| 6 | IANA Considerations | Registry changes reviewed; current registry reconciliation remains open. |
| 6.1 | The Authentication-Results Header Field | Complete header registration read. |
| 6.2 | "Email Authentication Methods" Registry Description | Expert review and unique method/ptype/property combination reviewed. |
| 6.3 | "Email Authentication Methods" Registry Update | All updated entries and deprecated sender-id reviewed. |
| 6.3.1 | "header.a" for DKIM | DKIM header.a registration read. |
| 6.3.2 | "header.s" for DKIM | DKIM header.s registration read. |
| 6.4 | "Email Authentication Property Types" Registry Description | Property-type registration procedure and fields reviewed. |
| 6.5 | "Email Authentication Property Types" Registry Update | All property-type references updated. |
| 6.6 | "Email Authentication Result Names" Registry Description | Unique method/code, expert review and status fields reviewed. |
| 6.7 | "Email Authentication Result Names" Registry Update | All result-name updates and deprecated method results read. |
| 6.8 | SMTP Enhanced Status Codes | X.7.25 reference correction reviewed. |
| 7 | Security Considerations | All threat subsections reviewed. |
| 7.1 | Forged Header Fields | All five suggested provenance mechanisms and separate-metadata alternative read; suggestions not invented deployed extensions. |
| 7.2 | Misleading Results | Successful authentication does not imply safe content or reputable sender. |
| 7.3 | Header Field Position | Header position alone cannot establish reliable provenance. |
| 7.4 | Reverse IP Query Denial-of-Service Attacks | Bound reverse-DNS work; consuming client must understand verifier limitations. |
| 7.5 | Mitigation of Backscatter | Backscatter can target forged senders. |
| 7.6 | Internal MTA Lists | Trusted-MTA configuration must track infrastructure changes. |
| 7.7 | Attacks against Authentication Methods | Underlying authentication vulnerabilities carry through result assertions. |
| 7.8 | Intentionally Malformed Header Fields | Malformed or oversized fields require robust parsing. |
| 7.9 | Compromised Internal Hosts | Internal client is not automatically an authorized result producer. |
| 7.10 | Encapsulated Instances | Digest extraction must not promote embedded results to trusted metadata; provenance/history needed. |
| 7.11 | Reverse Mapping | Reverse mapping has limited authentication value. |
| 8 | References | All references read. |
| 8.1 | Normative References | Normative dependency closure remains open. |
| 8.2 | Informative References | All informative references read; reported6790 flags normative use of DKIM grammar. |
| Appendix A | Legacy MUAs | Legacy Priority suggestion is not a trustworthy authentication signal for Email Next. |
| Appendix B | Authentication-Results Examples | All seven complete examples and explanatory text read; abbreviated signatures are not cryptographic vectors. |
| Appendix C | Operational Considerations about Message Authentication | All six operational considerations read; evaluation time and historical key/reputation state matter. |
| Appendix D | Changes since RFC 7601 | Complete change list, earlier errata references, acknowledgments and end matter read. |
| B.1 | Example B.1 | Absent field permits no conclusion. |
| B.2 | Example B.2 | Overall none means no evaluation. |
| B.3 | Example B.3 | SPF domain-only example and unresolved6027 reviewed. |
| B.4 | Example B.4 | Single producer may combine independently scoped results. |
| B.5 | Example B.5 | Different producers retain separate fields; signature protects assertion, not generic author identity. |
| B.6 | Example B.6 | Explicitly trusted intermediary historical assertion differs from current original-signature failure. |
| B.7 | Example B.7 | All comment placements and method version grammar reviewed. |

## Errata

- [6026](https://www.rfc-editor.org/errata/eid6026), reported: changes property separators and discusses trailing CFWS. The proposed grammar is not silently substituted for the published rule.
- [6027](https://www.rfc-editor.org/errata/eid6027), reported: requests full mailbox values in SPF examples; this conflicts with the source's advice to omit unauthenticated local parts. An implementation profile needs an explicit resolution.
- [6790](https://www.rfc-editor.org/errata/eid6790), reported: DKIM is an effective grammar dependency despite placement in informative references. It remains in dependency scope.

## Proposal consequence

The [security contract](../security.md) requires configured producer trust, boundary processing, method-specific interpretation and evidence scoped to its actual message and delivery context. Provider results can improve the experience without making users handle raw headers. They cannot replace endpoint cryptographic verification or silently authorize key changes.

The source's suggested metadata and protocol extensions are prior-art directions, not established interfaces. Email Next must define and test any selected provider integration. No complete Authentication-Results parser, trusted-provider deployment or user-interface study is claimed by this audit.


## Subsequent registry procedure change

RFC9989 sections9.1 and9.2 change the Email Authentication Methods and Email Authentication Result Names registries from Expert Review to Specification Required. The RFC8601 procedure recorded above describes that base document; it is not the current registration procedure after this update. RFC9989's complete audit and live registry reconciliation remain in progress. This change does not apply automatically to the separate property-types registry.
