---
title: DomainKeys Identified Mail audit
sectionNav: true
---

# DomainKeys Identified Mail audit

The complete 76-page [RFC 6376](https://www.rfc-editor.org/rfc/rfc6376.html), examples, appendices, references and end matter were read. All 23 retrieved errata are reconciled in the [errata record](dkim-errata.md). This is a base-document review, not a claim that dependency closure, current registry reconciliation or a complete verifier is finished.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 1.1 | DKIM Architecture Documents | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 1.2 | Signing Identity | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 1.3 | Scalability | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 1.4 | Simple Key Management | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 1.5 | Data Integrity | Domain responsibility, architecture, scale and key management reviewed; no endpoint authorship guarantee. |
| 2 | Terminology and Definitions | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.1 | Signers | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.2 | Verifiers | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.3 | Identity | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.4 | Identifier | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.5 | Signing Domain Identifier (SDID) | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.6 | Agent or User Identifier (AUID) | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.7 | Identity Assessor | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.8 | Whitespace | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.9 | Imported ABNF Tokens | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.10 | Common ABNF Tokens | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 2.11 | DKIM-Quoted-Printable | Terminology and complete grammar conventions reviewed; SDID, AUID and author remain distinct; DKIM QP is not MIME QP. |
| 3 | Protocol Elements | Protocol elements reviewed; exact tag and canonicalization semantics retained. |
| 3.1 | Selectors | Selector rotation/reuse and DNS scope reviewed; selector is not a device identity. |
| 3.2 | Tag=Value Lists | Case-sensitive tags, duplicate invalidity, unknown tags, empty values and verified5070 grammar reviewed. |
| 3.3 | Signing and Verification Algorithms | Algorithm family reviewed with current updates taking precedence. |
| 3.3.1 | The rsa-sha1 Signing Algorithm | Historical SHA1 requirement superseded by RFC8301; not adopted. |
| 3.3.2 | The rsa-sha256 Signing Algorithm | RSA-SHA256 PKCS1 v1.5 signing input reviewed. |
| 3.3.3 | Key Sizes | Historical key-size rules reviewed with RFC8301 override. |
| 3.3.4 | Other Algorithms | Unknown algorithms ignored as specified; no implicit endpoint-suite selection. |
| 3.4 | Canonicalization | All canonicalization algorithms and examples read; canonical input never replaces stored original. |
| 3.4.1 | The "simple" Header Canonicalization Algorithm | Simple header bytes remain unchanged. |
| 3.4.2 | The "relaxed" Header Canonicalization Algorithm | Relaxed field-name case, unfolding and WSP rules reviewed; verified5839 trims before CRLF, rejected7862 does not broaden WSP. |
| 3.4.3 | The "simple" Body Canonicalization Algorithm | Simple body trailing-empty-line and empty-body CRLF behavior reviewed. |
| 3.4.4 | The "relaxed" Body Canonicalization Algorithm | Relaxed body WSP, trailing-empty-line and zero-length empty-body behavior reviewed. |
| 3.4.5 | Canonicalization Examples (INFORMATIVE) | All examples read; separate executable vectors are limited evidence, not a complete verifier. |
| 3.5 | The DKIM-Signature Header Field | Every signature tag and ABNF reviewed, including l coverage, h instance order, q separator correction4810, i domain, t/x range and diagnostic z. |
| 3.6 | Key Management and Representation | Key management and representation reviewed; wrapper ambiguity remains unresolved. |
| 3.6.1 | Textual Representation | Every key tag read; empty p revokes, service/hash restrictions apply; verified4287/5137 and held3017/reported7001 distinguished. |
| 3.6.2 | DNS Binding | DNS lookup binding reviewed; no endpoint-key authority inferred. |
| 3.6.2.1 | Namespace | Selector/domain namespace reviewed. |
| 3.6.2.2 | Resource Record Types for Key Storage | Concatenate strings within a TXT record, never across records; multiple-record behavior is not uniqueness proof. |
| 3.7 | Computing the Message Hashes | Exact body/header hash sequence reviewed with verified5252; own b emptied, own final CRLF excluded, no extra body-hash append. |
| 3.8 | Input Requirements | Valid message input requirements reviewed; signatures do not validate malformed singleton headers. |
| 3.9 | Output Requirements | SUCCESS/PERMFAIL/TEMPFAIL output meanings reviewed. |
| 3.10 | Signing by Parent Domains | Parent-domain authority reviewed; administrative boundaries not inferred from name hierarchy. |
| 3.11 | Relationship between SDID and AUID | SDID output required; AUID is not a verified personal mailbox. |
| 4 | Semantics of Multiple Signatures | Multiple signatures evaluated independently. |
| 4.1 | Example Scenarios | All algorithm, coverage, list and forwarding scenarios reviewed. |
| 4.2 | Interpretation | Valid signature does not repair another; resource limits allowed; signing other signatures can be fragile. |
| 5 | Signer Actions | Signer workflow reviewed; local authorization separate from endpoint identity. |
| 5.1 | Determine Whether the Email Should Be Signed and by Whom | Signing authority and identity selection are local policy. |
| 5.2 | Select a Private Key and Corresponding Selector Information | Selector/private-key pairing and retention reviewed. |
| 5.3 | Normalize the Message to Prevent Transport Conversions | Normalize actual transmitted representation before signing; do not normalize protected input afterward. |
| 5.3.1 | Body Length Limits | l=0 leaves body unsigned; suffix cannot inherit authentication. |
| 5.4 | Determine the Header Fields to Sign | From coverage and absent-header oversigning reviewed; held6254 advice conflict retained. |
| 5.4.1 | Recommended Signature Content | All recommended/excluded header guidance read; interpretation metadata must be protected by endpoint profile. |
| 5.4.2 | Signatures Involving Multiple Instances of a Field | Repeated fields selected bottom-up in h order; example read. |
| 5.5 | Compute the Message Hash and Signature | Compute over final signed representation; verify prior signatures before modifying/re-signing as specified. |
| 5.6 | Insert the DKIM-Signature Header Field | Own signature prepended with exact signed values. |
| 6 | Verifier Actions | Verifier workflow reviewed; timing and result provenance matter. |
| 6.1 | Extract Signatures from the Message | Independent attempts, strict syntax and resource limits reviewed. |
| 6.1.1 | Validate the Signature Header Field | Required tags, i default/domain, From coverage, expiration and local rejection rules reviewed. |
| 6.1.2 | Get the Public Key | Lookup temporary failure differs from absent/revoked/malformed key; hash/key restrictions and multi-record iteration read. |
| 6.1.3 | Compute the Verification | Both body hash and header signature must verify; partial-body coverage retained. |
| 6.2 | Communicate Verification Results | Authentication-result headers require trusted provenance; incoming assertion alone grants no authority. |
| 6.3 | Interpret Results/Apply Local Policy | Filtering policy separate; cryptographic failure MUST NOT provoke SMTP4xx; display actual SDID and preserve diagnostic uncertainty. |
| 7 | IANA Considerations | All registry tables read; live registry reconciliation remains open. |
| 7.1 | Email Authentication Methods Registry | All registry tables read; live registry reconciliation remains open. |
| 7.2 | DKIM-Signature Tag Specifications | All registry tables read; live registry reconciliation remains open. |
| 7.3 | DKIM-Signature Query Method Registry | All registry tables read; live registry reconciliation remains open. |
| 7.4 | DKIM-Signature Canonicalization Registry | All registry tables read; live registry reconciliation remains open. |
| 7.5 | _domainkey DNS TXT Resource Record Tag Specifications | All registry tables read; live registry reconciliation remains open. |
| 7.6 | DKIM Key Type Registry | All registry tables read; live registry reconciliation remains open. |
| 7.7 | DKIM Hash Algorithms Registry | All registry tables read; live registry reconciliation remains open. |
| 7.8 | DKIM Service Types Registry | All registry tables read; live registry reconciliation remains open. |
| 7.9 | DKIM Selector Flags Registry | All registry tables read; live registry reconciliation remains open. |
| 7.10 | DKIM-Signature Header Field | All registry tables read; live registry reconciliation remains open. |
| 8 | Security Considerations | All threat subsections reviewed; domain signing is not end-to-end security. |
| 8.1 | ASCII Art Attacks | Relaxed whitespace can change visible ASCII-art meaning. |
| 8.2 | Misuse of Body Length Limits ("l=" Tag) | Unsigned suffix/MIME/HTML attacks reviewed; held6769 not represented as approved correction. |
| 8.3 | Misappropriated Private Key | Compromised domain signer can sign mail; endpoint key authority remains separate. |
| 8.4 | Key Server Denial-of-Service Attacks | Distributed lookup infrastructure still permits targeted denial of service. |
| 8.5 | Attacks against the DNS | DNS spoofing/chaining and query amplification reviewed; DNS dependencies remain open. |
| 8.6 | Replay/Spam Attacks | Replay preserves signature validity; authenticated application identity must prevent repeated effects. |
| 8.7 | Limits on Revoking Keys | Shared domain key revocation cannot selectively revoke one user. |
| 8.8 | Intentionally Malformed Key Records | Malformed key records require robust bounded parsing. |
| 8.9 | Intentionally Malformed DKIM-Signature Header Fields | Malformed signature fields cannot supply trusted values. |
| 8.10 | Information Leakage | Per-message selectors reveal verification lookup timing, not human reading. |
| 8.11 | Remote Timing Attacks | Private-key timing leakage considered; cryptographic implementation review remains necessary. |
| 8.12 | Reordered Header Fields | Reordering repeated headers can break otherwise legitimate signatures. |
| 8.13 | RSA Attacks | Expensive keys and floods require implementation resource controls. |
| 8.14 | Inappropriate Signing by Parent Domains | Parent-domain signing does not establish subdomain administrative consent. |
| 8.15 | Attacks Involving Extra Header Fields | Duplicate singleton headers and false content remain problematic despite valid signatures. |
| 9 | References | All references read; transitive normative closure remains open. |
| 9.1 | Normative References | All references read; transitive normative closure remains open. |
| 9.2 | Informative References | All references read; transitive normative closure remains open. |
| Appendix A | Example of Use (INFORMATIVE) | All three examples read; verified3192 body spacing and4926 header indentation corrections required; A.3 prose is not normative hash algorithm. |
| Appendix B | Usage Examples (INFORMATIVE) | All submission and delivery scenarios read; delegated selector does not cryptographically restrict local part. |
| Appendix C | Creating a Public Key (INFORMATIVE) | Key generation, SPKI example and compatibility read; g ignored, historical1024bit example not production guidance; wrapper reports unresolved. |
| Appendix D | MUA Considerations (INFORMATIVE) | All display guidance read; signer coverage must not be assigned to unsigned displayed identity. |
| Appendix E | Changes since RFC 4871 | Complete change list and earlier errata dispositions read. |
| Appendix F | Acknowledgments | Acknowledgments and author/end material read. |

## Proposal consequence

The [security contract](../security.md) retains domain-signature evidence separately from endpoint identity, audience authorization and application replay protection. DKIM supplies useful passive evidence over existing mail transport; it cannot negotiate encryption keys or authenticate every displayed control merely because a signature passes.

RFC8301, RFC8463 and RFC8616 have separate recorded reviews. RFC8553 has a separate [underscored DNS audit](underscored-dns.md). Normative DNS, architecture, RSA and IDNA dependency closure remains outstanding. The key-wrapper conflict and Appendix A prose defects are documented rather than silently resolved by inventing protocol rules.
