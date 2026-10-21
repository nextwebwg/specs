---
title: DMARC audit
sectionNav: true
---

# DMARC audit

The complete 69-page [RFC9989](https://www.rfc-editor.org/rfc/rfc9989.html), including all nested appendix examples, change descriptions, references and end matter, has been read. It obsoletes RFC7489 and RFC9091. All three entries in the captured RFC Editor errata corpus were read in full. This is a base-document review, not a tested DMARC implementation or completed normative-dependency audit.

## Errata reconciliation

| Erratum | Status in captured corpus | Disposition |
| --- | --- | --- |
| [8995](https://www.rfc-editor.org/errata/eid8995) | Reported, technical | Proposes recognizing DNSSEC compact denial with NXNAME under RFC9824 rather than relying solely on NXDOMAIN. Not an approved correction. DNSSEC and RFC9824 dependency review remains open. |
| [9150](https://www.rfc-editor.org/errata/eid9150) | Verified, editorial | External-report authorization references in 11.6, B.2.3 and B.2.4 point to RFC9990 Section 4, not Section 3. Apply corrected pointer. |
| [9025](https://www.rfc-editor.org/errata/eid9025) | Verified, editorial | B.2.5 RFC53322.From is RFC5322.From. Apply correction. |

The live all-status listing on 20 October 2026 matches all three captured records in ID, status, original/corrected text and notes. Current metadata matches the retained update and replacement relationships.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Domain-level validation and handling preferences; not endpoint encryption. |
| 2 | Requirements | Requirements and exclusions read in full. |
| 2.1 | High-Level Goals | Owner feedback and consistent domain authentication are goals. |
| 2.2 | Anti-Phishing | Anti-phishing scope is limited to domain use. |
| 2.3 | Scalability | DNS-based scalability does not establish endpoint trust. |
| 2.4 | Out of Scope | Local-part authenticity, content safety and delivery guarantees excluded. |
| 3 | Terminology and Definitions | All terminology read. |
| 3.1 | Conventions Used in This Document | Requirement keywords and imported terminology reviewed. |
| 3.2 | Definitions | All definitions and their algorithm references reviewed. |
| 3.2.1 | Authenticated Identifiers | Successful underlying method yields a domain identifier, not a person. |
| 3.2.2 | Author Domain | Author Domain comes from From, subject to syntax/single-domain scope. |
| 3.2.3 | DKIM Signing Domain | DKIM domain is d=, not local-part or display name. |
| 3.2.4 | SPF Domain | SPF MAIL FROM identity, including null-path handling, applies. |
| 3.2.5 | DMARC Policy Domain | Policy domain is distinct from organizational boundary. |
| 3.2.6 | DMARC Policy Record | Policy record syntax and discovery governed by Section 4. |
| 3.2.7 | Domain Owner | Domain owner is administrative actor, not necessarily correspondent. |
| 3.2.8 | Domain Owner Assessment Policy | Assessment policy expresses preference rather than endpoint authority. |
| 3.2.9 | Enforcement | Enforcement policies remain subject to receiver handling rules. |
| 3.2.10 | Identifier Alignment | Alignment binds domains only. |
| 3.2.10.1 | Relaxed Alignment | Relaxed alignment uses same Organizational Domain, not arbitrary suffix matching. |
| 3.2.10.2 | Strict Alignment | Strict alignment requires identical domains under DNS case rules. |
| 3.2.11 | Mail Receiver | Receiver role distinguished from author and report consumer. |
| 3.2.12 | Monitoring Mode | Monitoring does not turn failed validation into pass. |
| 3.2.13 | Non-Existent Domains | Existence semantics depend on DNS; reported8995 remains unresolved. |
| 3.2.14 | Organizational Domain | Organizational Domain is determined by specified tree walk. |
| 3.2.15 | Public Suffix Domain (PSD) | PSD boundary is not an endpoint identity boundary. |
| 3.2.16 | Public Suffix Operator (PSO) | PSO role and authority scope reviewed. |
| 3.2.17 | PSO-Controlled Domain Names | PSO-controlled names distinguished from registrants. |
| 3.2.18 | Report Consumer | Report consumer receives separate disclosures, not conversation membership. |
| 4 | Overview and Key Concepts | Complete operational model read. |
| 4.1 | DMARC Basics | Aligned authentication, owner policy and receiver disposition are separate. |
| 4.2 | Use of RFC5322.From | Single valid From scope; malformed/repeated fields cannot be repaired to force pass. |
| 4.3 | Authentication Mechanisms | Underlying authentication is necessary but insufficient without alignment. |
| 4.4 | Identifier Alignment Explained | All alignment paths and examples read. |
| 4.4.1 | DKIM-Authenticated Identifiers | Any valid aligned DKIM signature may support pass; unrelated signatures do not negate it. |
| 4.4.2 | SPF-Authenticated Identifiers | SPF MAIL FROM path only; independent HELO pass is not substitute. |
| 4.4.3 | Alignment and Extension Technologies | Future methods require aligned identifiers, not arbitrary success flags. |
| 4.5 | DMARC Policy Record Explained | TXT strings concatenate within a record; policy is not application capability. |
| 4.6 | DMARC Reporting URIs | Report SHOULD reach each listed URI; separate authorization and privacy rules apply. |
| 4.7 | DMARC Policy Record Format | All tags/defaults read; p/np ambiguities recorded below; obsolete size suffix ignored. |
| 4.8 | Formal Definition | Complete ABNF and table read; version first and case-sensitive DMARC1; unknown tags ignored as specified. |
| 4.9 | Flow Diagram | Complete flow diagram read with normative algorithms. |
| 4.10 | DNS Tree Walk | Bounded eight-query walk, full name then rightmost seven labels, duplicate-record discard and psd stops reviewed. |
| 4.10.1 | DMARC Policy Discovery | Author/organizational/PSD policy selection; organizational policy blocks PSD report inheritance; p/np source tensions retained. |
| 4.10.2 | Identifier Alignment Evaluation | Organizational boundary separate from policy; strict/equal-domain shortcuts and psd=n/y handling read. |
| 5 | DMARC Participation | Both publisher and receiver participation reviewed. |
| 5.1 | Domain Owner Actions | All deployment steps read; operational guidance not invented user constraints. |
| 5.1.1 | Publish an SPF Record for an Aligned Domain | Aligned SPF publication does not authenticate local users. |
| 5.1.2 | Configure Sending System for DKIM Signing Using an Aligned | Aligned DKIM signing remains domain-level evidence. |
| 5.1.3 | Set Up a Mailbox to Receive Aggregate Reports | Report mailbox requires access and privacy controls. |
| 5.1.4 | Publish a DMARC Policy Record for the Author Domain and | Author and organizational publication considered separately. |
| 5.1.5 | Collect and Analyze Reports | Report analysis does not yield complete delivery history. |
| 5.1.6 | Remediate Unaligned or Unauthenticated Mail Streams | Repair legitimate streams before changing enforcement. |
| 5.1.7 | Decide Whether to Update Domain Owner Assessment Policy to | Enforcement choices and interoperability consequences reviewed. |
| 5.1.8 | A Note on Large, Complex Organizations and Decentralized DNS | Deep names and skipped zone cuts can affect tree-walk policy visibility. |
| 5.2 | PSO Actions | PSO publication and multi-organization privacy boundaries read. |
| 5.3 | Mail Receiver Actions | All receiver stages read. |
| 5.3.1 | Extract Author Domain | Multiple author domains ordinarily terminate; optional bounded processing addressed in 11.5. |
| 5.3.2 | Determine If the DMARC Mechanism Applies | Policy discovery establishes applicability, not endpoint support. |
| 5.3.3 | Determine If Authenticated Identifiers Exist | Preserve underlying SPF outcomes and each DKIM signature/domain result. |
| 5.3.4 | Conduct Identifier Alignment Checks If Necessary | Alignment evaluated under applicable record and algorithm. |
| 5.3.5 | Determine DMARC "Pass" or "Fail" | An aligned passing method suffices; uncertainty is not success. |
| 5.3.6 | Apply Policy If Appropriate | Required DNS errors yield neither pass nor fail and no assessment-policy application. |
| 5.3.7 | Store Results of DMARC Processing | Stored results need provenance, context and privacy controls. |
| 5.3.8 | Send Aggregate Reports | Aggregate format/delivery requires separate RFC9990 audit. |
| 5.3.9 | Optionally Send Failure Reports | Optional failure reporting requires separate RFC9991 audit. |
| 5.4 | Policy Enforcement Considerations | Receiver disposition distinct from validation; p=none must not alter existing handling. |
| 6 | DMARC Feedback | Feedback separates aggregate and message-specific reporting. |
| 7 | Other Topics | All interoperability topics read. |
| 7.1 | Issues Specific to SPF | Pre-DATA SPF rejection may preclude Author Domain knowledge and reporting. |
| 7.2 | Rejecting Messages | Rejection/deferral and SMTP status handling do not prove person identity. |
| 7.3 | Interoperability Issues | Forwarding and lists can break domain authentication without malicious authorship. |
| 7.4 | Interoperability Considerations | Sole DMARC-failure rejection prohibited as specified; general-purpose domains advised against p=reject. |
| 8 | Conformance Requirements for Full DMARC Participation | Full participation requires publisher SPF and DKIM plus reporting, although one aligned pass can suffice per message. |
| 9 | IANA Considerations | All registry changes and tables read; live registry reconciliation remains open. |
| 9.1 | Email Authentication Methods Registry Update | Authentication methods move to Specification Required; policy.dmarc added. |
| 9.2 | Email Authentication Result Names Registry Update | Authentication result names move to Specification Required. |
| 9.3 | DMARC Tags Registry Update | All tag statuses reviewed; pct/rf/ri historic; new tags cannot change existing semantics. |
| 9.4 | DMARC Report Formats Registry Update | Report formats registry procedure/status reviewed; afrf active, RFC6591 dependency open. |
| 9.5 | Underscored and Globally Scoped DNS Node Names Registry Update | TXT _dmarc reference updated; not a generic endpoint discovery label. |
| 10 | Privacy Considerations | All privacy considerations read. |
| 10.1 | Aggregate Report Considerations | Aggregate data can reveal small-organization communication patterns. |
| 10.2 | Failure Report Considerations | Failure reports may expose content; multi-organizational PSD MUST NOT publish ruf. |
| 11 | Security Considerations | All security considerations read. |
| 11.1 | Authentication Methods | Permissive authorized senders may pass without intended domain-owner authorization. |
| 11.2 | Attacks on Reporting URIs | Report addresses face flooding, malformed input and fabricated claims. |
| 11.3 | DNS Security | DNS snooping/blocking/forgery affect confidentiality and results; secure DNS dependencies remain open. |
| 11.4 | Display Name Attacks | Display-name impersonation is outside DMARC scope. |
| 11.5 | Denial of DMARC Processing Attacks | Multi-domain processing must be bounded; omitted domains mean incomplete evaluation. |
| 11.6 | External Reporting Addresses | External report authorization uses RFC9990 Section 4 under verified9150, not printed Section 3. |
| 11.7 | Secure Protocols | Originally encrypted content can leak via reports; secure transport encouraged. |
| 11.8 | Relaxed Alignment Considerations | Relaxed alignment permits delegated-subdomain impersonation; organizational-boundary mistakes matter. |
| 12 | References | All references read; no claim of complete dependency closure. |
| 12.1 | Normative References | Reporting, DNS, grammar, URI and authentication dependencies tracked separately. |
| 12.2 | Informative References | Historical protocols and deployment guidance are not automatic new requirements. |
| Appendix A | Technology Considerations | All A.1–A.6 reviewed: S/MIME scope, method exclusion, Sender, existence, tree walk and pct replacement. |
| Appendix B | Examples | All B.1–B.5 and nested examples reviewed, including deep/PSD tree walks and external overrides; verified9025/9150 applied. |
| Appendix C | Changes from RFC 7489 | All C.1–C.10 and fifteen C.9 errata summaries read; summaries do not replace full historical errata review. |

## Consequences and unresolved source questions

The [security contract](../security.md) separates domain alignment, receiver disposition and endpoint identity. It also prevents automatic reports from exposing decrypted content, private recipient lists or access secrets. This is an Email/2 proposal, not a claim that existing DMARC universally enforces those protections.

Section 4.7 describes an omitted p tag with a default of none, while 4.10.1 conditions fallback for a missing or invalid p on a valid rua destination. The np fallback wording also differs: 4.7 references sp before p, whereas 4.10.1 describes p. These tensions require explicit parser/algorithm reconciliation before an executable DMARC profile is claimed; no erratum in the captured set settles them. B.2.5 also uses differing example mailbox names in its prose and zone text. The examples are not copied as canonical test vectors.

RFC9990 and RFC9991 reporting audits remain necessary, including external-destination verification and overrides. RFC9824, secure DNS, IDNA, URI/ABNF dependencies, historic RFC7489 errata and live IANA registry checks remain open. Changes to registry procedures in RFC8601 are recorded in the [authentication-results audit](authentication-results.md). Source-specific eight-query limits are not silently reused as Email/2 discovery quotas.
