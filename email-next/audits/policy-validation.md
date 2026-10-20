---
title: Bounded certificate-policy validation audit
sectionNav: true
---

# Bounded certificate-policy validation audit

RFC 9618 replaces RFC 5280's potentially exponential policy tree with a policy graph. It preserves certification-path validity and the policies valid for that path while changing the representation and output. This matters to clients validating HTTPS server certificates as well as servers validating client certificates.

**Review:** All 927 lines, 19 pages, algorithm replacements, diagrams, examples, references and end matter read; 31 explicit dispositions recorded. Current metadata identifies an August 2024 Proposed Standard updating RFC 5280, with no later update or replacement listed. The live official errata search returned no matching records.

## Service TLS consequences

The service profile should reference RFC 5280 policy processing **as updated by RFC 9618**, without demanding construction or exposure of the original policy tree. Validators SHOULD use the policy graph; they SHOULD NOT output the full exponential tree, and SHOULD instead return authority-constrained and/or user-constrained policy sets. Policy qualifiers MAY be omitted from output when not needed. The updated success condition retains the explicit-policy check and uses a nonempty user-constrained policy set where required. See §§4–5.

The graph merges duplicate policy nodes at each depth and permits multiple parents. Its size is bounded linearly by the number of policy entries and mappings in the input. That is not a guarantee that arbitrary certificates consume negligible resources. A caller must not reconstruct every graph path merely to retain an old tree-shaped result; doing so restores the original risk. Legacy tree output is deprecated and NOT RECOMMENDED, and implementations that require it SHOULD mitigate its cost. See §§4.1–4.2 and 5.6.

If graph processing is unavailable, alternative mitigations SHOULD be applied. Verify signatures before or alongside policy checking; signature-first alone does not eliminate attacks by entities controlling otherwise trusted, insufficiently constrained intermediates. Depth/size limits and policy-mapping inhibition have compatibility consequences. The RFC specifies no numerical resource limits for Email Next, and this review adds none. See §§6–6.4.

**Disabling policy checking is not permission to ignore critical policy extensions.** Section 6.5 requires critical policy-related extensions, notably policy constraints, to be treated as unrecognized and rejected in that configuration. A successful ordinary TLS handshake does not verify this behavior.

## Client versus issuer guidance

The graph/output recommendations and critical-extension handling apply to validators. Section 6.4 separately says CAs SHOULD NOT issue certificates with policy mappings and RECOMMENDS that applications managing trust-anchor policies forbid that extension in participating CAs. This does not automatically make every mapped chain invalid for every client. If Email Next selects mapping inhibition or a trust-program prohibition, state that choice and its compatibility effect separately.

## Evidence and remaining dependencies

No implementation changed. The current TLS experiment does not exercise policy mappings, explicit-policy requirements, graph outputs, critical policy-extension rejection or hostile policy-growth inputs. It cannot substantiate a policy-validation or denial-of-service-resistance claim. A bounded future test could compare allowed/denied policy sets and rejection behavior on small synthetic chains; it should not deliberately exhaust resources.

The RFC's normative dependencies are RFC 5280 and BCP 14. Its X.509 and CVE references were read as references, not independently audited. The [base audit](certificate-path.md) links the other current update reviews. The [CRL signer audit](crl-key-usage.md) covers RFC10007. These reviews do not establish implementation coverage.

Sources: [RFC 9618](https://www.rfc-editor.org/rfc/rfc9618.html), [metadata](https://www.rfc-editor.org/rfc/rfc9618.json), [live errata](https://errata.rfc-editor.org/search/?rfc_number=9618). Exact reading ranges, source SHA-256 and section dispositions are in `rfc9618-review-candidate.json`. Metadata and errata checked on 20 October 2026.
