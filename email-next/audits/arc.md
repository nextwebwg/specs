---
title: ARC audit
sectionNav: true
---

# ARC audit

The complete captured [RFC8617](https://www.rfc-editor.org/rfc/rfc8617.html) text has been reviewed, including both appendices, examples and end matter. ARC preserves assertions about mail handling. Chain validity does not prove assertion accuracy, content safety, freshness or endpoint identity.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Intermediaries can break domain authentication; ARC conveys assessments, not endpoint authority. |
| 2 | General Concepts | Custody analogy does not establish a trust framework. |
| 2.1 | Evidence | Authentication assertions are verifiable testimony, not independently reproducible evidence. |
| 2.2 | Custody | Custody records handler processing and assessment. |
| 2.3 | Chain of Custody | Chain covers ARC-participating custody, not necessarily every hop. |
| 2.4 | Validation of Chain of Custody | Chain validation and trust in custodians are separate decisions. |
| 3 | Terminology and Definitions | Architecture, DKIM, authentication-results and ABNF dependencies apply. |
| 3.1 | ARC Set | One set contains three related fields. |
| 3.2 | Authenticated Received Chain (ARC) | Ordered sets represent successive assessments. |
| 3.3 | Internet Mail Handlers / Intermediaries | Handlers include gateways and mailing lists. |
| 3.4 | Authentication Assessment | Payload accuracy and syntax do not determine chain integrity. |
| 3.5 | Signing vs. Sealing | Signing a field differs from sealing a complete set. |
| 3.6 | Sealer | Sealer asserts custody and assessment, not user consent. |
| 3.7 | Validator | Validator evaluates chain under the specified algorithm. |
| 3.8 | Imported ABNF Tokens | Imported tokens retain their source semantics. |
| 3.9 | Common ABNF Tokens | Instance and status grammar reviewed; semantic instance range is ARC-specific. |
| 4 | Protocol Elements | Protocol fields specialize inherited syntax. |
| 4.1 | ARC Header Fields | Three fields have distinct protection roles. |
| 4.1.1 | ARC-Authentication-Results (AAR) | One combined assessment payload per set. |
| 4.1.2 | ARC-Message-Signature (AMS) | AMS excludes ARC and Authentication-Results fields; instance replaces DKIM AUID; reported grammar issue remains. |
| 4.1.3 | ARC-Seal (AS) | Seal covers selected headers, not body; relaxed canonicalization and restricted tags apply. |
| 4.1.4 | Internationalized Email (EAI) | EAI inherits UTF-8 and internationalized authentication rules. |
| 4.2 | ARC Set | AAR, AMS and AS share instance identity. |
| 4.2.1 | Instance Tags | Continuous instances1–50 and exact field membership; multi-algorithm dependency remains. |
| 4.3 | Authenticated Received Chain | Message integrity and assertion-chain integrity are distinct. |
| 4.4 | Chain Validation Status | None/fail/pass are chain states, not account verification states. |
| 5 | Protocol Actions | Inbound validation and outbound sealing inform local disposition. |
| 5.1 | Sealer Actions | Modify before sealing; stop on prior fail; generate complete next set. |
| 5.1.1 | Header Fields to Include in ARC-Seal Signatures | Hash ascending instances and AAR/AMS/AS order, not physical header order. |
| 5.1.2 | Marking and Sealing "cv=fail" (Invalid) Chains | Failure seal covers only its newly created set. |
| 5.1.3 | Only One Authenticated Received Chain per Message | Broken chain cannot be restarted as continuous custody. |
| 5.1.4 | Broad Ability to Seal | Any handler may seal, including without content changes. |
| 5.1.5 | Sealing Is Always Safe | Sealing claims do not eliminate resource or privacy risks. |
| 5.2 | Validator Actions | Validate structure, latest AMS and every seal; older AMS checks optional; failed chain gives no ARC benefit. |
| 5.2.1 | All Failures Are Permanent | All ARC validation errors yield permanent chain failure; do not confuse with transport retry rules. |
| 5.2.2 | Responding to ARC Validation Failures during the SMTP | Optional SMTP failure signaling, not mandatory rejection of all failing chains. |
| 6 | Communication of Validation Results | Record arc status and available remote-ip/oldest-pass; zero means all AMS pass. |
| 7 | Use Cases | Use cases illustrate assessment transport, not endpoint authorization. |
| 7.1 | Communicate Authentication Assessment across Trust Boundaries | Cross-boundary use depends on trust in reporting handlers. |
| 7.1.1 | Message-Scanning Services | Scanner testimony cannot authorize rewriting protected events. |
| 7.1.2 | Multi-tier MTA Processing | Internal-tier assessment transport is not user authentication. |
| 7.1.3 | Mailing Lists | Lists convey pre-reposting assessment, not original recipient consent. |
| 7.2 | Inform Message Disposition Decisions | Disposition may use evidence without changing underlying check results. |
| 7.2.1 | DMARC Local Policy Overrides | Local DMARC override is distinct from endpoint authentication. |
| 7.2.2 | DMARC Reporting | Reporting example preserves failed SPF/DKIM despite accepted disposition; multiple reports need not mean multiple messages. |
| 8 | Privacy Considerations | Domains and addresses can expose personal routing information. |
| 9 | Security Considerations | Sealing-domain assertions make no semantic content-safety claim. |
| 9.1 | Increased Header Field Size | Header growth can impair legacy delivery. |
| 9.2 | DNS Operations | DNS work, timing visibility and slow-query denial require resource handling. |
| 9.3 | Message Content Suspicion | Valid chains do not exempt content from safety checks. |
| 9.4 | Message Sealer Suspicion | Authenticated sealer identity does not establish trustworthiness. |
| 9.5 | Replay Attacks | Intact chains can replay; deduplication and freshness remain independent. |
| 10 | IANA Considerations | Existing ARC registrations allocate no Email/2 extensions. |
| 10.1 | Update to Email Authentication Result Names Registry | Arc none/pass/fail result registration reviewed. |
| 10.2 | Update to Email Authentication Methods Registry | Remote-ip and oldest-pass property registrations reviewed. |
| 10.3 | New Header Fields in Permanent Message Header Field Registry | Permanent-registry entries remain experimental in status. |
| 10.4 | New Status Code in Enumerated Status Codes Registry | X.7.29 uses550; signaling remains optional. |
| 11 | Experimental Considerations | Experimental evaluation requires deployed evidence. |
| 11.1 | Success Consideration | Delivery improvement criterion is not proof it has been achieved. |
| 11.2 | Failure Considerations | Abuse criterion does not remove inherited replay risks. |
| 11.3 | Open Questions | Historical research questions do not relax processing requirements. |
| 11.3.1 | Value of the ARC-Seal (AS) Header Field | Question about seal value does not permit omitting required seals. |
| 11.3.2 | Usage and/or Signals from Multiple Selectors and/or Domains in | Selector/domain flexibility carries no device-identity semantics. |
| 11.3.3 | DNS Overhead | DNS overhead requires measurement; operational limit discussion does not replace protocol bound. |
| 11.3.4 | What Trace Information Is Valuable? | Trace utility varies; no universal reputation policy selected. |
| 12 | References | References reviewed without claiming dependency closure. |
| 12.1 | Normative References | DKIM, EAI, authentication-results and grammar dependencies remain applicable. |
| 12.2 | Informative References | ARC-MULTI and ARC-USAGE drafts and DMARC successors need status/applicability review. |
| Appendix A | Design Requirements | Design goals reviewed; no originator changes and cross-boundary testimony are not assurance. |
| Appendix B | Example Usage | Complete three-set example read; historical SHA-1/512-bit claims are not acceptable modern algorithm defaults or verified vectors. |
| A.1 | Primary Design Criteria | Internet-scale and verifiable-custody goals are not deployment evidence. |
| A.2 | Out of Scope | ARC explicitly is not a trust framework. |

## Source status and errata

The retrieved RFC information page confirms Experimental status. The captured full errata records contain two Reported technical entries: [7910](https://www.rfc-editor.org/errata/eid7910) proposes changing AMS grammar from CFWS to FWS to match inherited DKIM syntax; [8357](https://www.rfc-editor.org/errata/eid8357) requests a missing SMTP citation. Neither is treated as an approved correction. The live all-status listing on 20 October 2026 matches both captured records, including their original/corrected text and notes; current metadata retains Experimental status.

Appendix B contains historical SHA-1 and512-bit signature assertions. These illustrate message handling, not current acceptable cryptography. The embedded signatures have not been verified as executable test vectors.

## Application and remaining work

The [security chapter](../security.md#authentication-history-through-forwarding) separates chain integrity, sealer trust, interpretation of assessments and endpoint authentication. It also keeps replay processing and private-content disclosure independent of ARC results.

ARC-MULTI and ARC-USAGE are work-in-progress references in this source; their current status and applicability require review. DMARC reporting successors, DKIM algorithm updates, EAI and authentication-results dependencies also require reconciliation. This base review does not validate an ARC implementation, deployed interoperability, reputation policy or dependency closure.
