---
title: Email applicability guidance audit
sectionNav: true
---

# Email applicability guidance audit

**Coverage:** complete thirty-page [draft-ietf-emailcore-as-30](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-as-30/), including references, all 31 revision-history subsections and end matter. The retrieved draft is dated 26 August 2026. Datatracker evidence inspected on 19 October places it under IESG evaluation; it is not a published RFC. This audit is separate from the published RFC inventory.

## Finding

The draft supports incremental deployment while distinguishing syntactic validity, practical interoperability and security policy. It gives no basis for treating a server upgrade, successful delivery or mailbox-name similarity as authenticated endpoint capability.

## Section dispositions

Ranges group closely related sections; they do not claim that each referenced dependency has been audited.

| Sections | Topic | Disposition |
| --- | --- | --- |
| 1–1.1 | Scope and conventions | Guidance supplements core transport and message syntax. Requirement words describe this draft’s proposed applicability profile; they do not establish publication. |
| 2–2.3 | SMTP names and literals | EHLO name resolution mismatch may inform policy. Address literals and single-label domains can be syntactically valid yet unreliable in deployment; do not confuse syntax acceptance with reachability. |
| 2.4 | Extension support | Proposes mandatory STARTTLS and 8BITMIME support, recommended PIPELINING and SMTPUTF8. DSN requests differ from DSN/report formats; request support cannot be presumed. Enhanced status codes remain useful without being universal. |
| 3–3.1 | Message syntax and empty strings | Empty quoted local parts and Received tokens have interoperability problems. Empty display names are a different case. The guidance does not amend the grammar to prohibit every empty quoted string. |
| 3.2–3.2.2 | Trace generation and consumption | Avoid FOR on multiple-recipient copies; otherwise copy the relevant RCPT address exactly. Selective omission can itself reveal blind recipients. Received fields are diagnostic observations, not trusted endpoint assertions. |
| 3.3 | Groups | Legal group syntax is not universally implemented. A syntactic group is neither an authenticated membership roster nor a key-distribution mechanism. |
| 4–4.1 | Mailbox equivalence | Preserve local-part case. Case folding, plus stripping and dot removal depend on the receiving domain. Likely delivery equivalence is insufficient to merge cryptographic identity or access rights. |
| 4.2 | Internationalized addresses | SMTPUTF8 governs non-ASCII addresses. Do not apply IDNA to local parts or URI percent encoding to raw addresses. Local mappings do not establish universal identity equivalence. |
| 4.3 | Validation | Use the appropriate mail grammar rather than assuming HTML form validation matches it. Normalization advice is not permission to modify signed bytes or infer a new authenticated address. |
| 5 | MIME | Modern messages require MIME-aware processing. MIME support does not imply support for an Email/2 structured part or encryption suite. |
| 6–6.1.1 | Security layers and TLS | Separate hop confidentiality, server authentication, message authentication and endpoint confidentiality. The completed [TLS1.3](tls13.md) and [TLS configuration](tls-configuration.md) base reviews cover RFC9846 and RFC9325; applicable dependencies and runtime enforcement remain separate. |
| 6.1.2–6.1.3 | Opportunistic and enforced transport | Opportunistic transport can fall back under its policy. Enforced confidentiality and authenticated receiving-server policy have different failure behavior. Neither independently protects content from mailbox providers. |
| 6.2 | Message authentication | SPF, DKIM, DMARC and ARC answer different authentication or handling questions. None automatically authenticates an Email/2 participant’s endpoint key. The cited older DMARC RFC does not replace review of its successors. |
| 6.3 | SMTP authentication | The proposed modern profile prohibits cleartext credentials without TLS and effective confidentiality. Keep that requirement distinct from historical mechanism-specific exceptions and from message-author authentication. |
| 6.4 | Message confidentiality | S/MIME and OpenPGP provide prior art. Header protection, including RFC 9788, needs separate review; transport protection is insufficient to claim endpoint confidentiality. |
| 6.5 | Confidentiality policy | Senders must use confidentiality when available and accepted under this draft. Receiver implementation capability and local acceptance policy are distinct. Receiving plaintext capability does not authorize overriding a sender’s required protection. |
| 7 | Acknowledgments | Reviewed; no additional protocol requirements. |
| 8 | IANA considerations | No direct registry action. The [SMTP registry cleanup review](registry-cleanup.md) covers the referenced draft; its proposals are not published registry amendments. |
| 9 | Security considerations | Store-and-forward intermediaries can see unprotected content. Availability and local transport policy do not eliminate the need for explicit endpoint protection and downgrade rules. |
| 10–10.2 | References | Both reference lists reviewed. Reference enumeration is not full dependency review. Completed [SMTP revision](smtp-revision.md), [TLS configuration](tls-configuration.md) and [registry cleanup](registry-cleanup.md) base reviews have separate dependency and implementation boundaries. |
| A.1–A.31 | Revision history | All 31 change-log subsections read. Historical edits do not override the current body. Version 29 removed the discussion of reusing messages as outside MUA scope; version 30 updates TLS, security wording and reference classification. Do not inherit removed advice as a current requirement. |

## Changes to Email/2

The [transport contract](../transport.md) now prevents another recipient’s address from appearing in a shared copy’s Received FOR clause. This is an expressly proposed Email/2 privacy requirement, stricter than the draft’s recommendation against FOR on multiple-recipient copies. The [identity lifecycle](../identity-lifecycle.md) keeps delivery-address equivalence separate from cryptographic continuity.

Required endpoint encryption remains required when transport negotiation or compatibility discovery fails. A user’s selected plaintext or hosted-link fallback policy is a separate authorization; general opportunistic SMTP practice does not supply that authorization.

## Outstanding work

Reconcile applicable transitive dependencies and changes to the applicability draft before publication. The linked SMTP revision, TLS and registry-cleanup base reviews are complete at their recorded versions; that does not establish full dependency closure or applied external registry changes. This textual audit establishes neither deployed interoperability nor independent security validation.
