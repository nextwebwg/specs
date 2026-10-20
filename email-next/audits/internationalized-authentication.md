---
title: Internationalized authentication audit
sectionNav: true
---

# Internationalized authentication audit

**Coverage:** complete six-page [RFC 8616](https://www.rfc-editor.org/rfc/rfc8616.html), including references and end matter. No entries occur in the retrieved RFC Editor errata dataset. Base authentication specifications, IDNA and current DMARC successors remain separate dependencies.

## Finding

DNS lookup representation and authenticated message representation have different jobs. Convert internationalized domains as required for lookup, but do not rewrite the signed header into that lookup form before verifying it. Unicode mailbox local parts are not domain labels.

| Section | Disposition |
| --- | --- |
| 1 | Internationalized mail permits U-label domains and UTF8 local parts; domain representation consistency matters for authentication. |
| 2 | IDN includes A-label or U-label names. Historical advice-only treatment of DMARC reflects7489 status at publication; current successors require separate review. |
| 3 | Convert U-label domains to A-labels for DNS lookup. Machine-oriented field names remain ASCII. DNS representation is not a blanket rewrite of authenticated message bytes. |
| 4 | EHLO IDNs use A-labels before SMTPUTF8 negotiation; MAIL FROM domains may use either. SPF validation and domain-spec macros convert domains to A-labels. Terms with s/l macros do not match when local part is non-ASCII; do not Punycode the local part. |
| 5 | Internationalized DKIM quoted-printable safe characters include valid UTF8 sequences. d/i/s domain forms can use U-labels in EAI headers, with A-labels still valid. Hash exactly the representation in the header; relaxed field-name lowercasing remains ASCII-only. Key-record format unchanged. |
| 6 | For7489 processing, convert relevant domains to A-labels; rua/ruf policy-record addresses remain conventional. Reconcile with9989/9990/9991 before calling this the final current DMARC contract. |
| 7 | No IANA actions. |
| 8 | Authentication consistency does not eliminate spoofing, phishing or other email threats. No new cryptographic identity mechanism. |
| 9 | EAI base documents reviewed separately; IDNA5890/5891,UTF8,SPF,DKIM and current DMARC dependencies remain open. |

| Front/end matter | Abstract, status, copyright and author address reviewed. |

## Email Next consequence

Maintain the original authenticated bytes separately from parsed addresses and DNS lookup names. An equivalent A-label representation may locate the same verification record, but substituting it into the signed input can invalidate the signature. Apply only the canonicalization defined by the selected authentication protocol.

Do not apply IDNA conversion to a mailbox local part, or merge two identities merely because their Unicode display strings look alike. Account-address matching, lookup normalization and human-readable display need explicit separate rules in the final discovery profile.

Required cases include the same domain in A-label and U-label form, a non-ASCII local part, an internationalized DKIM identity, a lookup-normalized but incorrectly rewritten signature input, and SPF macros containing non-ASCII local parts. No general IDNA implementation or internationalized authentication interoperability test is claimed.
