---
title: DMARC aggregate reporting audit
sectionNav: true
---

# DMARC aggregate reporting audit

The complete [RFC9990](https://www.rfc-editor.org/rfc/rfc9990.html), all fourteen nested content tables, the complete XML schema, sample, references and end matter have been read. The captured full RFC Editor errata corpus contains no entries for RFC9990; this is not a fresh live-status assertion. Normative dependency and live registry closure remain open.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Aggregate domain authentication feedback, not person or endpoint-key authentication. |
| 1.1 | Terminology | Requirement keywords reviewed. |
| 1.1.1 | Notation | Imported mail notation and ABNF dependencies identified. |
| 1.1.2 | DMARC Terminology | All referenced DMARC roles distinguished. |
| 2 | Document Status | Together with RFC9989/9991 replaces RFC7489; reporting is now separate. |
| 3 | DMARC Feedback | Feedback supports domain operations, not conversation state changes. |
| 3.1 | Aggregate Reports | One policy domain per report; passing and failing traffic included; one reported configuration may describe mixed-policy observations. |
| 3.1.1 | Description of the Content of the XML File | All format tables, multiplicities and language attributes read; invalid format normally discarded. |
| 3.1.1.1 | XML Root Element | Feedback root uses DMARC namespace. |
| 3.1.1.2 | First Level Elements | Ordered top-level elements; optional version must be 1.0; at least one record. |
| 3.1.1.3 | Report Generator Metadata | All metadata fields reviewed; report ID scope and optional error/generator fields retained. |
| 3.1.1.4 | Contents of the "date_range" Element | Period boundaries are not first/last message times; periods SHOULD NOT overlap. |
| 3.1.1.5 | Contents of the "policy_published" Element | Observed/default policy, discovery method and testing state reviewed. |
| 3.1.1.6 | Contents of the "extension" Element | File extensions must be namespaced; namespace is not fetch authority. |
| 3.1.1.7 | Contents of the "record" Element | Record tuple and mandatory element order reviewed; record extensions follow auth results. |
| 3.1.1.8 | Contents of the "row" Element | Connecting IP/count/disposition require semantic checks beyond XSD. |
| 3.1.1.9 | Contents of the "policy_evaluated" Element | Aligned results are not rewritten by local overrides; reason required for specified mismatch. |
| 3.1.1.10 | Contents of the "identifiers" Element | Header/envelope domains distinct; null reverse-path permits empty envelope_from. |
| 3.1.1.11 | Contents of the "auth_results" Element | Raw authentication results distinct from alignment; attempted DKIM results subject to stated bounds. |
| 3.1.1.12 | Contents of the "dkim" Element | DKIM domain, selector and result required; human text optional. |
| 3.1.1.13 | Contents of the "spf" Element | SPF scope only mfrom; XSD policy result discrepancy recorded below. |
| 3.1.1.14 | Contents of the "reason" Element | Override type required, comment optional. |
| 3.1.2 | Handling Domains in Reports | Separate reports by policy domain, separate records for author domains; example reviewed. |
| 3.1.3 | DKIM Signatures in Aggregate Reports | Priority strict-pass, relaxed-pass, other-pass, non-pass; SHOULD at most 100 signatures per row. |
| 3.1.4 | Unique Identifiers in Aggregate Reporting | Report-ID and filename unique-id must agree when used; grammar mismatch recorded. |
| 3.1.5 | Error Element | Error strings unbounded in format, operationally terse; not permission for unlimited memory. |
| 3.1.6 | Policy Override Reason | All five override reason values reviewed. |
| 3.2 | Extensions | Optional extensions should not themselves cause processing errors. |
| 3.3 | Changes in Policy During a Reporting Period | Policy changes can produce mixed observations or split reports; not an immutable per-message policy snapshot. |
| 3.4 | Report Request Discovery | rua discovery is reporting configuration, not capability discovery. |
| 3.5 | Report Delivery | Evaluate destinations in order; attempt supported valid destinations within receiver limits; secure transport recommended. |
| 3.5.1 | Definition of Report-ID | Report-ID unique among reports to same domain; dot-atom grammar reviewed. |
| 3.5.2 | Email | MIME XML/gzip attachment, filename, subject and aligned DMARC requirement reviewed; same filename on resend. |
| 3.5.3 | Other Methods | Future registered URI methods possible, not already supported universally. |
| 3.5.4 | Handling of Duplicates | Duplicate handling receiver-dependent; partial overlapping periods cannot be exactly disentangled. |
| 4 | Verifying External Destinations | All nine external authorization steps, same-host override, length/error outcomes, wildcard consent and TTL withdrawal reviewed. |
| 5 | Extensible Reporting | File/record extension positions and unknown-extension handling reviewed; examples hypothetical. |
| 6 | IANA Considerations | Both XML registry registrations read; live reconciliation remains open. |
| 6.1 | Registration for the DMARC Namespace | Namespace urn:ietf:params:xml:ns:dmarc-2.0. |
| 6.2 | Registration for the DMARC XML Schema | Schema registration separate from namespace; full XSD read. |
| 7 | Privacy Considerations | All privacy subsections read together with RFC9989. |
| 7.1 | Report Recipients | Third-party recipients and traffic analysis require separate privacy consideration. |
| 7.2 | Data Contained Within Reports | No-personal-information assurances do not eliminate small-domain inference and extension risks identified elsewhere. |
| 7.3 | Feedback Leakage | All three PSD cases read; PSD feedback limited to aggregate reports. |
| 8 | Security Considerations | Security and privacy sections apply together. |
| 8.1 | Report Content as an Attack | Decompression and XML resource exhaustion are explicit threats. |
| 8.2 | False Information | Reports can contain forged claims and distort policy/architecture decisions. |
| 8.3 | Disclosure of Filtering Information | Filtering-placement extensions discouraged because they reveal receiver behavior. |
| 9 | Operational Considerations | All operational guidance read. |
| 9.1 | Report Generation | Terse useful diagnostics; no specified numeric limits adopted as Email Next defaults. |
| 9.2 | Report Evaluation | Malformed reports may be sidelined; aggregation requires trustworthy interpretation. |
| 9.3 | Report Storage | Storage/retention left to receiver; no automatic conversation-history authority. |
| 10 | References | All references reviewed. |
| 10.1 | Normative References | Gzip/XML/URI/IDNA/grammar and registry dependency closure remains open. |
| 10.2 | Informative References | UUID, surveillance and failure-report dependencies identified. |
| Appendix A | DMARC XML Schema | Entire XSD read; schema validation does not enforce all prose and semantic requirements. |
| Appendix B | Sample Report | Complete sample read and validated with published schema using xmllint. |
| Appendix C | Differences from RFC 7489 | All changes and end matter read: split documents, extensions, PSD and required DKIM selector. |

## Schema experiment

The published Appendix A schema and Appendix B sample were extracted with only their common text indentation removed. Local `xmllint --nonet --noout --schema` accepted the original sample. It also accepted each of three independent mutations: version 2.0, source IP `not-an-ip`, and message count -1. These results establish that schema validity alone is insufficient, not that those values conform to the protocol.

The schema declares version as an unrestricted decimal, IP as a string and count as an integer. Additional semantic validation is necessary. The experiment does not implement secure decompression, a production XML parser, report authentication, external destination authorization or complete conformance checks. Extracted source files remain scratch evidence; redistribution would require the applicable IETF code-component notice.

## Unresolved format questions

Section 3.1.4 requires identical Report-ID and filename unique-id when both are used, but their grammars differ: Report-ID permits dot-atom punctuation and an optional at-sign component, while filename unique-id permits only letters and digits. A generator can choose their intersection, or omit the optional filename identifier, but cannot assume every valid Report-ID is filename-compatible. The UUID suggestion also needs a representation compatible with the filename grammar.

The SPF schema includes a policy result absent from the referenced RFC8601 SPF result vocabulary. Extension wildcards use lax processing without directly enforcing the prose namespace restrictions. These are recorded source inconsistencies or schema gaps, not silently repaired standard requirements. Section 4 describes URI authority extraction even though ordinary mailto URIs need scheme-specific mailbox-domain handling; a generic URL hostname accessor is insufficient.

## Consequences for Email Next

The [discovery contract](../capability-discovery.md) keeps external-report acceptance separate from key-discovery delegation. The [security contract](../security.md) requires semantic checks, bounded processing and no network fetch based solely on an extension namespace. Report metadata remains potentially sensitive: Section 7.2's broad assurances must be read alongside traffic-analysis and PSD leakage risks in Sections 7.1/7.3 and small-organization risks in RFC9989 Section 10.1.

Reports may contain mixed policy observations, partial signature lists and duplicate or overlapping periods. They cannot establish complete delivery history, immutable per-message policy, participant membership or encryption readiness. Aligned DMARC authentication of a report does not establish the truth of its contents.
