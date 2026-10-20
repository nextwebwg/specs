---
title: Internationalized certificate names audit
sectionNav: true
---

# Internationalized certificate names audit

RFC 9549 updates certificate name processing to IDNA2008 and keeps internationalized domains in A-label form during validation. Unicode conversion for display is separate. RFC 9598 supplies the current internationalized certificate email-name form and matching rules.

**Review:** RFC 9549 was read completely: 475 lines, ten pages, 17 dispositions, including every replacement paragraph and references. Current metadata lists it as a March 2024 Proposed Standard, replacing RFC 8399 and updating RFC 5280, with no later successor or update listed.

## Consequences for service TLS

Certificate DNS names and domain-component attributes carry internationalized labels as A-labels. DNS equality uses a case-insensitive exact comparison of the whole name; DNS name constraints compare labels case-insensitively and preserve subtree boundaries. These certificate representation rules complement RFC 9525's selected HTTPS DNS-ID matching, including its separate wildcard rules. They do not authorize choosing a mailbox domain, subject DN or resolved address as a replacement reference identifier.

A-label-looking ASCII is not necessarily a valid IDNA2008 label. RFC 9549 §3 says CAs SHOULD ensure IDNA2008 validity; RFC 9598 §4 separately requires certificate email domains to conform without mappings. Do not equate Punycode conversion, IDNA2003 or permissive compatibility processing with full IDNA2008 validation. The current experiment's exclusion of `xn--` hosts remains an explicit limitation, not completed internationalized hostname support.

The updated email constraints support all mailboxes at an exact host or mailboxes in a domain identified by a leading dot. RFC 9549 §2.2 removes the particular-mailbox option from the base text. RFC 9598 §6 describes it as deprecated and says local-part constraints SHOULD NOT be used. This difference must not be turned into an invented rule that every legacy chain containing such a constraint is automatically invalid; record it when choosing legacy handling.

Unicode display conversion does not belong in certificate constraint comparison. RFC 9549 explicitly replaces RFC 8399's A-label-to-U-label comparison path, citing implementation complexity and vulnerabilities. This rationale does not establish that any particular current library is correct.

## Corrections and remaining work

The live errata page contains **Reported technical 9230**, concerning the Unicode code point in §1's chess-symbol example. The RFC Editor also notes that the example's UTS46 conversion claim may require correction. Preserve its Reported status; do not use that example as an authoritative executable test vector. This does not change the operative A-label processing rules.

The IDNA definitions, protocol, derived properties, contextual rules, bidirectional rules, Punycode and their updates remain distinct dependencies: RFCs 5890–5894 and 3492. Referencing them does not constitute their full review. The [DN comparison review](certificate-name-comparison.md) covers RFC 4518 and selected Stringprep/Unicode 3.2 definitions; full table/data and backend matching evidence remain separate. IRI processing (3987), ASN.1/DER and imported modules also remain explicit scope. No IDNA or certificate-name implementation was changed or tested here.

RFC 8399 has been disposed as a superseded historical reference, based on current metadata and the successor's change explanation. Its live errata page reports none. Its full historical base text was not reviewed in this pass and must not be counted as a completed base audit. RFC 8398 is similarly superseded by RFC 9598; its one Held example-OID correction is recorded separately.

Sources: [RFC 9549](https://www.rfc-editor.org/rfc/rfc9549.html), [metadata](https://www.rfc-editor.org/rfc/rfc9549.json), [errata](https://errata.rfc-editor.org/search/?rfc_number=9549). Private trace: `rfc9549-review-candidate.json` and `certificate-i18n-historical-disposition.json`. Live checks completed 20 October 2026.
