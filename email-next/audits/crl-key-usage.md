---
title: Authorizing a CRL signing key audit
sectionNav: true
---

# Authorizing a CRL signing key audit

RFC 10007 closes a gap in RFC 5280's CRL validation algorithm: for a version 3 CRL issuer certificate, the validator must check that Key Usage exists **and** asserts `cRLSign`. Checking the bit only when the extension happens to be present is insufficient.

**Review:** Complete 267-line, six-page document read, including the five-step attack example, exact algorithm replacement, references and multilingual end matter; ten dispositions recorded. Current metadata identifies a June 2026 Proposed Standard updating RFC 5280, with no later update or replacement listed. The official live errata search returned no matching records.

## Service TLS consequences

When a service client uses CRLs, apply RFC 5280 §6.3.3(f) as replaced by RFC 10007 §4. Validate the CRL issuer's certificate path to the **same trust anchor** used for the target certificate. If the CRL issuer certificate is version 3, require the Key Usage extension and its `cRLSign` bit before accepting that signing key for the CRL. The remaining CRL signature, freshness, scope and reason-coverage checks still apply.

The update explicitly excludes version 1 and version 2 certificates from this extension-presence check because those versions have no extension field. That exception does not waive path or signature validation, and it does not force an application to accept all legacy certificates. Do not generalize this update into a rule that every HTTPS leaf certificate must carry `cRLSign` or even into a universal Key Usage presence rule for every certificate role.

The motivating attack uses two certificates with the same subject DN: one authorizes key A for CRL signing; another carries key B without Key Usage. The old conditional check could let key B authenticate a substituted indirect CRL. Matching the subject name, or successfully verifying its signature with some certified key, therefore does not establish CRL-signing authorization. See §3.

## Client versus issuer guidance

The amended validation check is client behavior. Section 5 separately RECOMMENDS that CAs include Key Usage in CRL issuer certificates and says the affected PKI's policy authority SHOULD distinguish DNs by purpose if the issuer profile cannot be updated. That naming mitigation is not an exception permitting an updated client to accept a version 3 signer with missing Key Usage.

Existing nonconforming signer certificates may cause verification failures after the update. This is an interoperability consequence to document, not a reason to silently restore the old acceptance rule.

## Evidence and remaining dependencies

No implementation changed. The TLS helper supplies no CRL and has no tests for a missing Key Usage extension, an unset `cRLSign` bit, a distinct CRL trust anchor or substituted indirect CRLs. It does not prove this update is implemented. A future CRL acceptance experiment should include those negative cases plus an authorized signer, while preserving freshness and scope checks.

This update selects no new revocation transport or OCSP behavior. The [base audit](certificate-path.md) links current update reviews; the selected revocation mechanism’s dependencies and implementation remain open. The [policy audit](policy-validation.md) covers RFC9618.

Sources: [RFC 10007](https://www.rfc-editor.org/rfc/rfc10007.html), [metadata](https://www.rfc-editor.org/rfc/rfc10007.json), [live errata](https://errata.rfc-editor.org/search/?rfc_number=10007). Private ledger `rfc10007-review-candidate.json` records exact source spans and SHA-256. Metadata and errata checked on 20 October 2026.
