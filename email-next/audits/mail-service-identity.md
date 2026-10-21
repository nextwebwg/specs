---
title: Mail service identity audit
sectionNav: true
---

# Mail service identity audit

**Coverage:** complete thirteen-page [RFC 7817](https://www.rfc-editor.org/rfc/rfc7817.html), including all examples, references, Appendix A and end matter. No RFC 7817 entries occur in the retrieved RFC Editor errata dataset. Certificate-validation and discovery dependencies remain open; [RFC 9525](https://www.rfc-editor.org/info/rfc9525) supersedes the RFC 6125 general identity procedure referenced here.

## Finding

Authenticated mail-service discovery can remove manual server configuration, but its authority is limited to the service being authenticated. A valid provider certificate does not prove a correspondent's device identity, possession of a message-decryption key, or continuity with a previously trusted key. RFC 7817 applies to submission and account-access clients, not SMTP relay-to-relay authentication.

| Section | Disposition |
| --- | --- |
| 1 | Applies to client submission, IMAP, POP and ManageSieve; explicitly excludes MTA-to-MTA SMTP. Keep relay authentication policy separate. |
| 2 | Reference identifiers are expected service identities. DNS-ID, SRV-ID, URI-ID and historical CN-ID are distinct certificate identifier types. |
| 3 | Validate the certificate path before service-name matching. Reference names come from configured email domain, connection hostname without CNAME canonicalization, or securely derived names. DNS-ID support is required; RFC6186 discovery also requires SRV-ID support and an email-domain reference. URI-ID is prohibited here. Historical CN-ID fallback is optional. Wildcards occupy the whole leftmost label, not a fragment. Reconcile with the successor to RFC6125 before selecting a modern profile. |
| 4 | CA checklist requires DNS-ID and email SRV-ID issuance support and historical CN-ID compatibility; leftmost wildcard issuance is optional. These are source requirements, not evidence of actual CA support. |
| 4.1 | Delegated service authorization must cover every requested domain. A CA unable to verify that authority must not issue the email service identifiers. DNSSEC and certificates binding the original service domain are possible delegation evidence; plain redirection alone is insufficient. |
| 5 | CSR guidance includes service host DNS-IDs, recommends email-domain DNS-IDs, and requires applicable SRV-IDs for RFC6186 discovery. Historical CN and wildcard guidance is recorded without making it the new profile. |
| 5.1 | Multiple-domain strategies include pinned or DNSSEC-authenticated delegation, multi-name certificates, separate endpoints and SNI. Each has operational costs. SNI selects a certificate; it does not itself authorize the delegation. The RFC leaves large-scale hosting issues unresolved. |
| 6 | Examples distinguish host and email-domain DNS-IDs from service-qualified SRV-IDs; SRV-IDs omit the DNS SRV _tcp component. A shared certificate may cover several services. Examples are illustrative and do not strengthen section5 SHOULD requirements to MUST. |
| 7 | Operational guidance refers to certificate issuance and multi-domain hosting; no additional capability or key-discovery protocol is defined. |
| 8 | Trusted reference names are essential. Manually configured names, explicit confirmation and authenticated discovery are different provenance paths. DANE integration is outside this RFC. |
| 9 | References and their normative/informative classification reviewed. Base review does not close their dependencies. |
| 9.1 | Certificate path validation, identifier matching, service discovery, SNI and submission dependencies require their own review. RFC6125 has successor RFC9525; do not adopt historical CN fallback without reconciliation. |
| 9.2 | DNSSEC, URI syntax, DANE and POSH references identify relevant discovery mechanisms; citation alone does not select any for Email/2. |
| Appendix A | Replaces identity-check passages in2595,3501,3207 and5804. The3207 replacement is explicitly for Submission. ManageSieve retains its IP-address comparison reference; no general email-account identity proof is created. |

| Front and end matter | Abstract, standards status, copyright, acknowledgements and author address reviewed. |

## Email/2 consequence

Discovery records need to preserve the original expected service identity, the discovered endpoint, and the evidence authorizing any delegation. An unauthenticated DNS answer cannot replace the expected identity with an attacker-selected hostname merely because that hostname has a valid certificate. Select the SNI name according to the applicable service profile, then validate the returned certificate against authorized reference identifiers.

Keep provider-service authentication separate from correspondent-key authentication in the identity lifecycle. A provider may supply a key advertisement, but the client still applies possession, continuity, revocation and conflict checks. A changed provider endpoint does not authorize replacing an established correspondent key.

Required cases include untrusted SRV redirection to a valid attacker certificate, an authorized delegated service, CNAME canonicalization changing the expected name, a partial-label wildcard, a service-type mismatch, a valid provider connection delivering a conflicting correspondent key, and certificate failure under required protection. These cases are review obligations; this audit does not claim a working certificate verifier or deployment test.
