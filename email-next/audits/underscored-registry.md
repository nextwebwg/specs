---
title: Underscored DNS registry audit
sectionNav: true
---

# Underscored DNS registry audit

[RFC 8552](https://www.rfc-editor.org/rfc/rfc8552.html) coordinates underscored DNS names. Email/2 would need to specify and register the applicable resource-record type and global label before publishing a DNS discovery binding. Registration prevents naming collisions; it does not establish mailbox ownership or approve the protocol's security.

## Consequences for discovery

The global label is the underscored label closest to the DNS root. Each record type needs its own registration for that label; subordinate naming belongs to the specification controlling the global label. The [discovery proposal](../capability-discovery.md) still needs to choose the record type, label, subordinate names, record syntax, validation and failure behavior. This audit does not allocate a name or supply that binding. Existing `_domainkey` records retain their DKIM meaning.

Wildcard DNS answers can create records under underscored names even when their contents were intended for another context. A future binding needs to validate the answer's defined meaning and authentication, rather than treating record presence as capability support. Registration's expert review checks the entry's clarity and uniqueness; it does not assess the surrounding protocol's technical quality. See RFC8552 §§1.4, 2 and 4.1.5.

## Coverage and evidence

All fifteen pages of the base RFC, including every section, example, table, reference and end matter, were reviewed. Official RFC Editor metadata lists Best Current Practice and no updates or obsoleting document. Nine complete records in the captured official errata corpus were reviewed. The live all-status listing on 20 October 2026 matches all nine captured records in ID, status, original/corrected text and notes; current metadata confirms the recorded relationships. The selected current entries and registration procedure are reconciled below. No Email/2 RR-type/global-label pair has been selected, so this review cannot establish availability for a new name.

| Section | Disposition |
| --- | --- |
| front | Status, abstract, copyright and contents read; BCP222 registry coordination, not a discovery protocol. |
| 1 | DNS operational naming conventions add context without changing the DNS protocol. |
| 1.1 | An underscored branch scopes record interpretation to its parent domain; preserve record-specific semantics. |
| 1.2 | Scoped branches reduce unrelated RRsets; this is an organizational benefit, not authenticated discovery. |
| 1.3 | Global means the underscored label closest to the root, normally rightmost in presentation. |
| 1.4 | Wildcard synthesis can produce an underscored answer without the intended service meaning; label.* is not a DNS wildcard. |
| 1.5 | Historical coordination gap motivates this registry and the RFC8553 companion amendments. |
| 2 | Publicly specified global labels require registration. Scope is the RR-type/name pair; subordinate namespaces belong to the global-label specification. All Table1 examples read. |
| 3 | Table2 registration template supplies RR type, global node name and specification reference. |
| 4 | Registry establishment and Enumservices cross-reference reviewed; spacing errata do not change behavior. |
| 4.1 | Expert Review; every field required, type/name pair unique, stable organizational reference and sorting rules reviewed. |
| 4.1.1 | Names recorded lowercase where case exists; each RR type requires a separate entry; specification organization controls its entry. |
| 4.1.2 | All initial Table3 entries read; these are historical seeds, not a current availability check. Reference corrections tracked below. |
| 4.1.3 | NULL _ta-* reservation is a prefix family, not DNS wildcard syntax; held erratum5665 clarifies literal prefix _ta-. |
| 4.1.4 | _example reserved across all RRsets; suitable explanatory context is not an Email/2 allocation. |
| 4.1.5 | Expert review checks entry completeness/clarity and pair uniqueness; excludes broader technical quality and RR-type review. |
| 4.2 | Enumservices registry note encourages corresponding underscored-name registration; no Email/2 Enumservice selected. |
| 5 | Source declares no new security issues; no DNS authentication, mailbox identity or capability proof follows from registration. |
| 6 | Complete reference list read; reference contents are not recursively audited here. |
| 6.1 | DNS, RR-specific and registration dependencies identified; binding-dependent review remains outstanding. |
| 6.2 | RFC8553 companion and historical SZTP draft reference read; neither selects an Email/2 binding. |
| Acknowledgements | Complete acknowledgements read. |
| Author | Author contact and final page/end matter read. |

## Errata

| Erratum | Status in captured corpus | Effect |
| --- | --- | --- |
| [7064](https://www.rfc-editor.org/errata/eid7064) | Verified | URI `_acct` reference becomes RFC7566. |
| [7065](https://www.rfc-editor.org/errata/eid7065) | Verified | URI `_iax` reference becomes RFC6315; record labels the section 4.2.1, but the affected table is §4.1.2. |
| [7066](https://www.rfc-editor.org/errata/eid7066) | Verified | URI `_dccp` reference becomes RFC4340. |
| [7067](https://www.rfc-editor.org/errata/eid7067) | Verified | Recorded correction assigns RFC4340 to URI `_sctp`. Preserve this recorded correction without inferring a new protocol meaning; the current registry repeats that reference; this review does not repair or broaden its meaning. |
| [7068](https://www.rfc-editor.org/errata/eid7068) | Verified | Recorded correction assigns RFC4340 to URI `_tcp` and `_udp`; these reserved protocol names do not define Email/2 discovery. |
| [5665](https://www.rfc-editor.org/errata/eid5665) | Held for Document Update | Clarifies that the reserved family begins with literal `_ta-`, without a literal asterisk in each name. It is not DNS wildcard syntax. |
| [6551](https://www.rfc-editor.org/errata/eid6551), [6777](https://www.rfc-editor.org/errata/eid6777) | Verified | Restore a missing space before `_ta`; no semantic change. |
| [6772](https://www.rfc-editor.org/errata/eid6772) | Verified | Correct `_service 4` to `_service4` in the example explanation. |

## Remaining dependencies

The [RFC8553 audit](underscored-dns.md) covers companion amendments. A selected DNS binding will determine which further protocol reviews apply: DNS naming and wildcard behavior (RFC1034, RFC1035 and RFC2181), SRV (RFC2782), service-name allocation (RFC6335), URI records (RFC7553), and registration procedure (RFC8126). Reading their citations here does not complete those audits. DNS authentication and recipient-key authorization remain separate design requirements.

## Selected current names and availability

The current [underscored-name registry](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#underscored-globally-scoped-dns-node-names) uses Expert Review. The selected entries checked on 20 October 2026 are:

| Record type | Global label | Registry reference |
| --- | --- | --- |
| TXT | `_domainkey` | RFC6376 |
| TXT | `_dmarc` | RFC9989 |
| `*` (all types) | `_example` | RFC8552 §4.1.4 |
| NULL | `_ta-*` prefix family | RFC8145 |

The current URI rows also incorporate the captured reference corrections: `_acct`→RFC7566, `_iax`→RFC6315, and `_dccp`/`_sctp`/`_tcp`/`_udp`→RFC4340. This is a report of registry content, not independent validation of every referenced transport or permission to reinterpret the names.

Email/2 has not selected a discovery RR type and global label. There is therefore no concrete candidate pair whose availability can be certified. Existing names above cannot be repurposed, and absence of a future candidate from a snapshot would not reserve it. Select the binding, then check its exact pair and applicable reserved families before requesting registration. No registry allocation was requested in this work.
