---
title: Internationalized mailbox names in certificates audit
sectionNav: true
---

# Internationalized mailbox names in certificates audit

RFC 9598 defines the current `SmtpUTF8Mailbox` certificate name form. It matters to certificate email identities and their constraints; it does not replace the DNS-ID used to authenticate an Email Next HTTPS endpoint or establish an Email Next device identity.

**Review:** Complete 590-line, 12-page document read, including the name-form table, constraint diagram, normative ASN.1 module and full DER example; 17 dispositions. Current metadata identifies a May 2024 Proposed Standard replacing RFC 8398 and updating RFC 5280, with no later update or replacement. The official live errata search reports none.

## Name encoding and matching

An ASCII-only local part uses `rfc822Name`, even when its domain is internationalized. A non-ASCII local part uses `SmtpUTF8Mailbox` in `otherName`, OID `1.3.6.1.5.5.7.8.9`, encoded as UTF8String without a byte-order mark. Domains use lowercase valid A-labels and NR-LDH labels; U-labels are not stored in the value. These are mailbox values, without display names, comments or angle brackets.

Valid `SmtpUTF8Mailbox` values compare octet for octet. When comparing with an address from another source, parse the mailbox, convert domain U-labels to A-labels and lowercase domain labels. Validate the UTF-8 local part, but do not case-fold or normalize it. No characters are wildcards in this comparison. Valid `rfc822Name` and `SmtpUTF8Mailbox` values cannot match each other because their local-part character requirements differ. See §§3–5.

These certificate matching rules do not silently redefine every Email Next identifier, account normalization rule or displayed address. A certificate-email authentication feature would need an explicit binding and acceptance contract before adopting them.

## Constraints still matter to HTTPS certificates

An HTTPS reference identifier remains a DNS-ID. However, choosing DNS-ID for the application does not authorize a path validator to ignore applicable constraints on other subject names carried in the certificate. RFC 9598 extends existing `rfc822Name` constraints across the email namespace to `SmtpUTF8Mailbox`; this prevents a legacy constrained issuer escaping its domain restriction by using the newer name form.

For email constraints, an exact-host constraint matches that host only; a leading-dot constraint matches a subordinate domain suffix including the dot. This differs from the base DNS-name subtree rule and must not be reused indiscriminately. Domains are compared as lowercase A-label/NR-LDH labels, not decoded Unicode. The local part is removed for these host/domain constraints. See §6 and RFC 9549 §2.2.

Section 6's issuer paragraph says “rfc822Name subject alternative names” while discussing issuing email name constraints. Read it in the surrounding name-constraint context; it is not a reason to place constraints in the SAN extension. Constraints use the existing rfc822Name form and IDNA2008 domains. Particular-mailbox constraints are deprecated; the companion candidate records the wording difference with RFC 9549.

A validator unable to process an applicable critical constraint must follow the base reject-or-process rule. The existing TLS handshake experiment does not test SmtpUTF8Mailbox, constraint coverage, Unicode local parts or malformed A-labels. No such support is claimed.

## Historical and dependency disposition

RFC 8398 is superseded. Current encoding, matching and constraint algorithms use A-label domains throughout; do not restore its conditional U-label handling as a fallback. Its current errata page contains Held technical 5418 concerning the old Appendix B OID. The current RFC 9598 example uses the specified `1.3.6.1.5.5.7.8.9` OID. Historical metadata and the full errata record were read, but the historical base document was not fully reviewed in this pass.

The full IDNA2008 and Punycode dependency review remains open, as do ASN.1/DER and RFC 5912 module imports. SMTPUTF8 grammar dependencies and current Unicode display practices remain distinct from certificate matching. Visual similarity never proves byte identity; the RFC expressly preserves exact local-part bytes despite possible interoperability differences.

Sources: [RFC 9598](https://www.rfc-editor.org/rfc/rfc9598.html), [metadata](https://www.rfc-editor.org/rfc/rfc9598.json), [errata](https://errata.rfc-editor.org/search/?rfc_number=9598). Private trace: `rfc9598-review-candidate.json`; historical disposition in `certificate-i18n-historical-disposition.json`. Live checks completed 20 October 2026.
