---
title: Email TLS version update audit
sectionNav: true
---

# Email TLS version update audit

**Coverage:** complete [RFC 8997](https://www.rfc-editor.org/rfc/rfc8997.html), including all seven replacement passages, references and end matter. No entries occur in the retrieved RFC Editor errata dataset. The [RFC 8314 base document](submission-access-tls.md) has a separate review; general TLS dependencies remain open.

## Finding

The email submission/access update raises the older TLS 1.1 baseline to TLS 1.2. A client cannot label a connection confidential under this rule unless it also validates the certificate and meets the account's minimum protection requirements. This indication describes the connection, not end-to-end message confidentiality.

| Section | Disposition |
| --- | --- |
| 1 | Raises the submission/access TLS baseline from1.1 to1.2; updates8314 rather than defining message encryption. |
| 2 | BCP14 uppercase requirement vocabulary applies. |
| 3 | All seven replacements reviewed: section heading, provider migration, obsolete ClientHello rejection example, new-user recommendation, confidentiality indication, MUA implementation/configured minimum, and new-account defaults. Preserve MUST versus SHOULD distinctions. TLS1.2 or later and certificate validation are necessary for the specified confidentiality indication; account policy can impose stronger conditions. Historical optional legacy support is not a requirement to enable it. |
| 4 | No IANA actions. |
| 5 | Security rationale depends on8996 deprecation; complete TLS algorithm/profile review remains open. |
| 6 | Reference classification reviewed; dependency review remains separate. |
| 6.1 | 8314,8996,TLS1.2,TLS1.3 and requirement-keyword dependencies identified. A version number alone does not specify cipher policy or certificate validation. |
| 6.2 | TLS1.1 is a historical informative reference, not a selected Email/2 protocol. |

| Front and end matter | Abstract, standards status, copyright, acknowledgements and author addresses reviewed. |

## Email/2 consequence

Do not import TLS 1.1 defaults from the unamended RFC 8314. The submission/access profile must apply the version update together with current certificate and algorithm guidance. A protocol-version check alone is insufficient: an invalid certificate or an unmet account policy still prevents a confidential-connection indication.

The RFC's ClientHello example is not a complete TLS version-negotiation algorithm. Use the selected TLS protocol's negotiation rules rather than implementing a custom check of one legacy field. No TLS implementation or cryptographic configuration has been validated here.

Required cases include TLS 1.1 rejection for a protected account, TLS 1.2 with failed certificate validation, TLS 1.2 below a stricter account policy, and a valid protected service connection carrying a message without end-to-end encryption. The last case may establish transport protection only.
