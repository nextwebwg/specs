---
title: Submission and access TLS audit
sectionNav: true
---

# Submission and access TLS audit

**Coverage:** complete twenty-six-page [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314.html), including ABNF, registrations, references, Appendix A and end matter. Reported erratum 5326 reviewed without treating it as accepted. The [RFC 8997 update](tls-version-update.md) supplies the amended TLS version thresholds. General TLS and certificate dependencies remain open.

## Finding

Automatic setup can prefer protected services while respecting existing account policy. A server's advertised priority does not override the client's minimum confidentiality requirements. Submission, mailbox access and relay delivery are separate services; transport protection does not establish message authorship or end-to-end confidentiality.

| Section | Disposition |
| --- | --- |
| 1 | Submission/access confidentiality, implicit TLS preference and cleartext deprecation; excludes relay transport and explicitly does not replace end-to-end encryption. |
| 1.1 | Updates POP, IMAP, submission, older TLS guidance and SRV configuration; apply8997 to historical version thresholds. |
| 2 | Implicit TLS, account, provider and configuration terms reviewed; ABNF and requirement vocabulary defined. |
| 3 | Prefer TLS immediately on connection for client/provider services; this is not an SMTP relay-port change. |
| 3.1 | POP3S port995 begins TLS immediately; after greeting both peers enter AUTHORIZATION even with a client certificate. |
| 3.2 | IMAPS port993 begins TLS immediately; acceptable client certificate may lead to PREAUTH, otherwise OK enters NOT AUTHENTICATED. |
| 3.3 | Submissions port465 begins TLS immediately and retains MSA authentication requirements.587 STARTTLS remains a transition mechanism; correctly required TLS has comparable security properties. No fixed new sunset date is inferred. |
| 3.4 | Prefer TLS close alerts before TCP termination; client may close after sending its alert without waiting for the peer alert. |
| 4 | Providers support TLS, prefer implicit TLS, advertise usable services, migrate cleartext users, support1.2+, record cipher information and apply current cipher guidance. Apply8997 to obsolete1.1 migration language. |
| 4.1 | After cleartext access revocation, valid and invalid credentials receive the same denial; avoid a credential-validity oracle. Consider rotation of exposed passwords. Apply8997 version updates. |
| 4.2 | Request client certificates only when usable for account authentication; accepted authorization enables SASL EXTERNAL, with IMAPS PREAUTH alternative. |
| 4.3 | Received tls clause records registered cipher name or0x plus four hex digits; optional group follows immediately. Trace text is not end-to-end authentication or proof of every hop. |
| 4.4 | Maintain valid service certificates; multiple-domain deployments use appropriate certificates/endpoints/SNI and support post-SRV hostname interoperability. |
| 4.5 | DNS guidance covers discovery and trust configuration, not recipient device capabilities. |
| 4.5.1 | MX and DNSSEC recommendation concerns inbound delivery; relay handling remains outside this document. |
| 4.5.2 | Advertise SRV and prefer implicit TLS over cleartext or STARTTLS. |
| 4.5.3 | Sign service-discovery DNS records when the parent zone supports DNSSEC. |
| 4.5.4 | TLSA advertisement is recommended as additional trust evidence but forbidden here without DNSSEC signing. |
| 4.6 | Replacing public-facing servers, including filters, generally preserves or improves supported TLS version. |
| 5 | Clients support discovery, per-account minimum protection, validated certificates and accurate indicators. Apply8997 version thresholds; detect upgrades for legacy accounts without silently weakening protected ones. |
| 5.1 | Adds _submissions._tcp; filter services below minimum protection before ranking. Credential testing must respect the minimum; insecure setup requires explicit warning. Do not rediscover on every connection without validated DNSSEC. Periodic change detection is allowed. |
| 5.2 | Default per-account protection validates certificates;8997 raises recommended version to1.2. Until minimum is met allow only capability discovery or STARTTLS. Avoid routine click-through bypass. Explicit reconfiguration is distinct from transient connection failure. |
| 5.3 | Validate using7817 and PKIX; DANE is optional. Exception pinning alone does not satisfy the specified minimum confidentiality. |
| 5.4 | Exception pinning is setup-only, account-scoped and revocable; not offered on validation failure for an existing account. Distinguish this from authenticated key continuity and HTTP pinning. |
| 5.5 | Client certificates require account-specific authorization and a server request. Installing one for another account is not permission to disclose it. Supporting clients implement SASL EXTERNAL. |
| 6 | Intermediary scanners must meet the same transport requirements. End-to-end encryption limits server-side content scanning; this does not authorize decryption or silent fallback. |
| 7 | Registration changes are specified in the following subsections; no Email/2 registration is established. |
| 7.1 | Updates TCP pop3s995 registration. |
| 7.2 | Updates TCP imaps993 registration; no UDP registration changes. |
| 7.3 | Registers TCP submissions465 as an alternate use. Reported erratum5326 clarifies historical smtps wording and submission/relay distinction; not an accepted normative correction. |
| 7.4 | Registers Received tls and group clauses with section4.3 syntax. |
| 8 | Targets external network interception, not compromised providers. Client certificate disclosure has privacy consequences; historical TLS1.3 draft discussion is not current protocol guidance. |
| 9 | References reviewed; dependency closure not claimed. |
| 9.1 | TLS/cipher guidance, PKIX,DANE,SASL and underlying protocol dependencies remain separate audits; reviewed8997 updates apply. |
| 9.2 | Historical drafts and informational sources are not final current profiles; TLS1.3 and MTA-STS have published replacements. |
| Appendix A | Non-normative deployment rationale prefers simpler implicit TLS and documents465 practice; does not declare all correctly implemented STARTTLS insecure. |

| Front and end matter | Abstract, standards status, copyright, acknowledgements and author addresses reviewed. |

## Email/2 consequence

Filter discovered services against the account's security requirements before ranking eligible endpoints. Do not send credentials merely to test whether a discovered configuration works when its connection fails the configured minimum. A connection failure does not amend account policy or enable ordinary-mail fallback.

Prefer implicit TLS for submission and mailbox access. Retain correctly enforced STARTTLS compatibility; the message transport does not require a new SMTP relay port. Apply the version update and the authenticated service-discovery rules together.

A setup exception that remembers an otherwise invalid server certificate is not verified provider identity. Scope such exceptions to their account, make them revocable and do not offer replacement pinning as a routine response to an existing account's validation failure. This server-certificate behavior is separate from correspondent key continuity.

Required cases include a higher-priority insecure endpoint, credential testing below the configured minimum, invalid certificates, revoked cleartext access without a credential oracle, a certificate requested for an unauthorized account, POP versus IMAP authentication states after client-certificate TLS, and a TLS trace header in an otherwise unauthenticated message. No complete mail client or TLS stack has been tested by this audit.
