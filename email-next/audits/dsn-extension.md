---
title: SMTP delivery-status extension audit
sectionNav: true
---

# SMTP delivery-status extension audit

**Coverage:** complete 38-page [RFC 3461](https://www.rfc-editor.org/rfc/rfc3461.html), all examples, registrations, appendices and end matter, plus all eight matching records in the retrieved errata dataset. This is a base-document audit; current format, status-code and update dependency closure remains open.

| Section | Disposition |
| --- | --- |
| 1 | Delivery-report objectives reviewed; reliability goals do not supply authentication or proof of reading. |
| 2 | DSN EHLO has no parameters and adds four MAIL/RCPT parameters, no verbs. Internal section references are stale. |
| 3 | Original-recipient and envelope correlation survive appropriate relay; RCPT acceptance alone is not completed DATA transfer. |
| 4 | xtext encodes octets with uppercase plus-hex; parentheses are literal, not comments. RFC6533 supplies a distinct UTF-8 address representation. |
| 4.1 | NEVER exclusive; tokens case insensitive; DELAY permission not guarantee; omitted NOTIFY permits failure or failure+delay behavior. |
| 4.2 | Initial ORCPT matches submitted RCPT; list redistribution uses subscriber address; registered type does not require syntactically valid address. Apply verified reference/editorial corrections and RFC6533 update. |
| 4.3 | RET FULL/HDRS applies to failure reports; omitted RET can return full message. It is not a confidentiality mechanism. |
| 4.4 | ENVID is opaque sender correlation data, not contribution identity or authentication; encoded parameter bound reviewed. |
| 4.5 | No repeated parameters; SHOULD501 here differs from MAIL MUST501 in5.1; preserve scope. |
| 5 | Roles and conformance apply to submission clients and relay/server behavior separately. |
| 5.1 | Valid parameter non-discrimination and malformed/duplicate handling reviewed; held4222 local filtering exception remains a proposed correction. |
| 5.2 | No DSN for null reverse-path, even if header sender exists; local non-looping diagnostics permitted. Verified269 reference correction applied. |
| 5.2.1 | Preserve supplied ENVID/RET/NOTIFY presence and value; preserve ORCPT identically including case. Missing ORCPT may be added from received RCPT. |
| 5.2.2 | No DSN parameters to unsupported next hop; requested relay/failure reporting and optional separate null-return NEVER transaction reviewed. RCPT-success wording needs final-acceptance reconciliation. |
| 5.2.3 | Delivered means mailbox-service or list-processor availability, not retrieval or distribution. |
| 5.2.4 | Gateway reporting and content-return preservation are best effort under specified conditions, not end-to-end guarantees. |
| 5.2.5 | Delay reports discretionary; explicit omission of DELAY suppresses them; default permits them. |
| 5.2.6 | Failure reporting depends on requested/default behavior; dead-letter/postmaster storage remains failure for intended recipient. |
| 5.2.7 | Aliases preserve envelope return address; mailing lists replace it and reset reporting context. |
| 5.2.7.1 | List submission final delivery; prevent contradictory MTA/list DSNs. Redistributed DSN parameters not derived from original; rejection may use ordinary notification. |
| 5.2.7.2 | Single-target alias normally propagates parameters without intermediate DSN. |
| 5.2.7.3 | All three permitted multi-target policies reviewed: strip/report relay, propagate exactly one, or expand/remove success request downstream. |
| 5.2.7.4 | Confidential forwarding may use list-style envelope/report separation; downstream addresses must not leak through original sender's reports. |
| 5.2.8 | Combined reports should not expose recipients whose notifications were not otherwise due. |
| 5.3 | Local submission notification directives embedded in message must be removed before SMTP transmission; gateway translation reviewed. |
| 5.4 | Individual parameter bounds, short originating ENVID recommendation and combined-line requirement reviewed. Published1036 conflicts with512+530=1042; unresolved arithmetic noted below. |
| 6 | Notification MIME framework and current successor dependencies reviewed. |
| 6.1 | DSN null return path; destination from original envelope sender; no RET; NOTIFY only NEVER; new ENVID and ORCPT permitted. |
| 6.2 | Multipart report structure and return-content limits reviewed; FULL may be truncated to headers by size policy; current RFC6522/6533 updates apply. |
| 6.3 | All per-message/per-recipient fields reviewed; decode ENVID xtext, do not invent missing originals; required remote/diagnostic fields for SMTP relay outcomes. RFC6533 updates address types. |
| 7 | Acknowledgments read. |
| 8 | Parser complexity and receipt storms reviewed; base security dependencies remain open. |
| 9 | All type-name registration material reviewed. |
| 9.1 | Preserve envelope-derived address, do not rewrite into valid syntax; historical grammar is not a new mailbox-generation profile. |
| 9.2 | Single-line reply transcription and folded multiline diagnostics reviewed; grammar3*DIGIT is broader than current three-digit SMTP replies. |
| 9.3 | DNS name/address-literal registration reviewed; held6422 identifies IPv4-only limitation, not a ratified new grammar. |
| 10 | Overall scenario and printed command continuation convention reviewed; examples are not directly executable fixtures. |
| 10.1 | All recipient-specific submission choices and complete DATA exchange reviewed. |
| 10.2 | Conforming relay preserves parameters and completes DATA exchange. |
| 10.3 | Mixed RCPT failure/success and reporting responsibility reviewed. |
| 10.4 | Legacy hop receives separate null-return NEVER transaction without extension parameters. |
| 10.5 | Forwarded address differs from original recipient; NOTIFY change and inconsistent hostnames recorded, rejected4218 not applied. |
| 10.6 | Delivered report example read; abbreviated original content is not a complete fixture. |
| 10.7 | Failure report example read; missing Remote-MTA conflicts with6.3(h), so example is not normative validation oracle. |
| 10.8 | Gateway relayed report explicitly lacks final-delivery confirmation. |
| 10.9 | Forwarding failure example read; untyped Reporting-MTA and failure after prior SUCCESS-only request are inconsistencies, not adopted behavior. RFC3464 section2.3.3 explicitly permits temporary status with terminal failed action. |
| 11 | All changes from1891 read. |
| 12 | Reference structure read. |
| 12.1 | Normative references reviewed; current DSN format/status and dependency closure pending. |
| 12.2 | Informative references reviewed. |
| 13 | Author material read. |
| 14 | Copyright and final acknowledgment read. |

## Errata dispositions

| Record | Status in retrieved evidence | Treatment |
| --- | --- | --- |
| 269 | Verified | Correct RFC1123 reference to section5.3.3. |
| 686 | Verified | ORCPT encoding refers to section4. |
| 5575 | Verified | Remove stray closing parenthesis. |
| 8224 | Verified | Correct “when” to “which” in encoding prose. |
| 4222 | Held for Document Update | Local-policy exception to parameter acceptance is recorded, not represented as a verified replacement. |
| 6386 | Held for Document Update | Correctly interpret the misspelled esmtp-value term; no wire change. |
| 6422 | Held for Document Update | IPv4-only literal limitation remains an open registration/grammar issue. |
| 4218 | Rejected | Do not apply the proposed NOTIFY example correction as accepted errata. The example remains unsuitable as a normative oracle. |

## Reconciliation required before implementation

Section5.4 states a 1036-character command minimum while describing a 530-character extension to a 512-character baseline. The stated addition is 1042. This audit does not silently replace the published requirement or assert that all parameter-length conventions are resolved. The exact command-size profile needs reconciliation with current SMTP extension registries and boundary vectors.

Section5.2.2 ties a relayed success notification to RCPT success, before the final DATA outcome is known. The Email Next interface must not report completed relay from recipient acceptance alone. A server implementation needs a documented reconciliation of that wording with SMTP transaction completion, rather than a test that assumes the example defines every failure path.

The section10.5 transcript changes a FAILURE request to SUCCESS without explaining the exception, while section10.9 later sends a failure report. Rejected erratum4218 does not resolve this scenario into a trustworthy fixture. The transcript also mixes hostnames. Section10.7 omits the Remote-MTA field required by section6.3(h); section10.9 supplies an untyped Reporting-MTA. Abbreviated returned-message parts are illustrative. Preserve these as source findings rather than copying them into passing examples.

The diagnostic grammar uses `3*DIGIT`, which permits more than three digits. Email Next must not treat arbitrary diagnostic text matching that loose grammar as a valid SMTP response or authorization. Exact diagnostic parsing still requires a receiving profile. The action/status relationship is resolved by RFC3464 section2.3.3: a temporary error can accompany a terminal failed action after the MTA abandons retries. This part of the example is valid.

## Consequences for Email Next

The [transport contract](../transport.md) distinguishes delivery from retrieval, relay from final delivery, and envelope correlation from identity proof. It now also preserves list/alias reporting boundaries and keeps private forwarding addresses out of shared conversation state. The existing DSN extension supplies useful correlation, not invisible control delivery, recipient presence, key possession or authorization to downgrade encryption.

Current update reviews include RFC3885, RFC6533 and RFC8098. Historical update lineage and referenced standards remain separately tracked. No complete DSN parser, provider interoperability or authenticated-receipt protocol is claimed.
