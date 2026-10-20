---
title: Historical DMARC audit
sectionNav: true
---

# Historical DMARC audit

[RFC7489](https://www.rfc-editor.org/rfc/rfc7489.html) explains the original DMARC deployment model and older reports that clients may encounter. It is obsolete: current policy, aggregate reporting and failure reporting belong to [RFC9989](dmarc.md), [RFC9990](dmarc-aggregate.md) and [RFC9991](dmarc-failure.md). Reading historical behavior does not adopt it as the Email Next baseline.

The complete 73-page base text, examples, XML schema, references and end matter have been read. All twenty RFC7489 entries in the captured errata corpus were reviewed, including proposed replacements and verifier notes. These statuses describe that corpus; current live errata reconciliation and dependency closure remain open. The [official status page](https://www.rfc-editor.org/info/rfc7489/) identifies the three successors and earlier updates RFC8553 and RFC8616.

## Keep historical and current processing separate

| Area | Historical behavior | Current integration boundary |
| --- | --- | --- |
| Domain discovery | Public suffix list and author/organizational-domain lookup | Use RFC9989's bounded DNS tree walk for the current profile. Historical results retain their discovery provenance. |
| Gradual rollout | pct sampling and weaker treatment for sampled-out messages | Do not revive pct as an Email Next adoption control; use the current DMARC testing semantics and separately defined client/provider rollout. |
| Report delivery | URI size suffix, requested reporting interval and transport-error reports | Follow current reporting documents; old record syntax is not a fresh reporting mandate. |
| Aggregate format | Original namespace, field multiplicities and schema | Use the selected report version's schema and semantic checks; a historical XML document is not a current-format report. |
| Identity-Alignment | Section 7.3.1 lists mechanisms that produced aligned identities; none means none did | RFC9991 describes failed mechanisms instead. Preserve source-profile information; do not silently reinterpret old reports with the opposite meaning. Unidentified provenance remains ambiguous. |
| Header internationalization | Original ASCII-oriented handling | Reconcile RFC8616 and current successor rules; do not substitute display strings for parsed domains. |

These differences matter to report importers and migration tests. They do not alter the distinction between domain authentication and authenticated conversation authorship.

## Section review

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Domain policy and feedback support deployment; passing authentication never guarantees delivery. |
| 2 | Requirements | Goals and exclusions reviewed as historical scope. |
| 2.1 | Goals | Incremental adoption needs operational feedback and legitimate-mail compatibility. |
| 2.2 | Exclusions | Person identity, message content and display-name legitimacy are outside this mechanism. |
| 2.3 | Scalability | DNS publication avoids bilateral sending agreements; third-party service delegation remains possible. |
| 2.4 | Anti-phishing | Exact-domain defenses do not defeat lookalike domains or display-name impersonation. |
| 3 | Terminology | Author domain, operator roles and authenticated identifiers are not endpoint principals. |
| 3.1 | Alignment | Domain alignment depends on successful underlying authentication, not visible similarity. |
| 3.1.1 | DKIM alignment | d= alignment is separate from canonicalization; one passing aligned signature suffices. |
| 3.1.2 | SPF alignment | MAIL FROM identity applies, including null-path rules; unrelated HELO success is insufficient. |
| 3.1.3 | Extensions | Future mechanisms require a defined domain extraction/alignment rule. |
| 3.2 | Organizational domain | Historical public-suffix heuristic is superseded for current processing; list variation explains old differences. |
| 4 | Overview | Policy, authentication, disposition and feedback remain distinct operations. |
| 4.1 | Mechanisms | Only specified DKIM/SPF results supply authenticated domains here. |
| 4.2 | Concepts | No local-part authentication or content-legitimacy guarantee. |
| 4.3 | Flow | Full flow and diagram reviewed; intermediate delivery stages do not imply endpoint authentication. |
| 5 | From choice | User-visible author domain is the focus; malformed and multiple-author handling needs profile-specific interpretation. |
| 6 | Policy | Domain requests allow receiver exceptions; exceptions do not turn failure into success. |
| 6.1 | DNS records | Concatenate TXT strings within one record, not distinct records; _dmarc label is required. |
| 6.2 | URIs | Historical delimiter escaping and size suffix reviewed; recipient limits are not conversation payload limits. |
| 6.3 | Tags | All eleven tags, defaults, scope and unknown-tag handling read. Deprecated controls are not adopted for new profiles. |
| 6.4 | Grammar | Full ABNF read, including version case, separator, numeric bounds and binary size multipliers. Semantic limits exceed syntax alone. |
| 6.5 | Domain owner | A DNS record alone is insufficient for useful deployment without aligned authentication or operational feedback. |
| 6.6 | Receiver | Algorithm is historical; current processing follows RFC9989. |
| 6.6.1 | Author extraction | A-label conversion and all exceptional From cases reviewed; multi-domain handling is not guessed from the first address. |
| 6.6.2 | Handling | Authentication, alignment and disposition are separate; temporary errors cannot be labeled permanent failure. |
| 6.6.3 | Discovery | Original two-location lookup, filtering and invalid-policy fallback read; do not reuse as current tree walk. |
| 6.6.4 | Sampling | Historical pct affects enforcement, not report population. No new Email Next sampling quota is derived. |
| 6.6.5 | Stored results | Operational feedback records are not conversation events. |
| 6.7 | Enforcement | Receiver can accept failures or reject passes. Local policy must not masquerade as cryptographic verification. |
| 7 | Feedback | Feedback supports safer deployment, not delivery receipts or capability exchange. |
| 7.1 | External destinations | Full authorization and same-host override algorithm read; consent to receive reports is not consent to disclose protected conversation content. |
| 7.2 | Aggregate reports | Passing/failing observations, policy changes and report boundaries reviewed; one policy field can describe mixed observations. |
| 7.2.1 | Transport | Historical size checks include encoding/compression; unsupported destinations do not authorize another disclosure path. |
| 7.2.1.1 | Email | XML/gzip MIME, names, subject and authentication rules read; filename and Report-ID examples have corrections/issues below. |
| 7.2.1.2 | Other transport | Extensibility does not mean arbitrary URI schemes are deployed. |
| 7.2.2 | Error reports | All six fields reviewed; diagnostic URIs are data, not executable commands or endpoint enrollment. |
| 7.3 | Failure reports | Can disclose full content and amplify traffic; consolidation and privacy policy remain necessary. |
| 7.3.1 | ARF update | Historical Identity-Alignment semantics differ from RFC9991; preserve report-profile context. |
| 8 | Minimum implementation | Daily/mailto/size provisions describe this historical profile, not generic Email Next implementation thresholds. |
| 9 | Privacy | Reports can reveal more than the original delivery's intended exposure. |
| 9.1 | Data exposure | Full messages, destinations and hidden forwarding relationships may leak. |
| 9.2 | Recipients | Third-party analysis and traffic correlation require independent consideration. |
| 10 | Other topics | Deployment rationale read without adopting old algorithms as current requirements. |
| 10.1 | SPF | Broad authorizations and early SPF rejection can undermine intended DMARC behavior. |
| 10.2 | DNS caching | TTL trades freshness against query load; no universal Email Next TTL follows. |
| 10.3 | Rejection | SMTP success does not establish inbox delivery; synchronous rejection, discard and backscatter have different consequences. |
| 10.4 | Alignment risk | Delegated subdomains can pass relaxed alignment for organizational-domain mail; not proof of a person's intent. |
| 10.5 | Interoperability | Forwarders and lists may break alignment while still performing legitimate operations. |
| 11 | Registrations | Historical registry actions read; current registry state requires separate reconciliation. |
| 11.1 | Method | dmarc/header.from identifies a domain evaluation, not a user credential. |
| 11.2 | Results | none/pass/fail/temperror/permerror retain distinct meanings; no binary trust badge. |
| 11.3 | Feedback field | Historical Identity-Alignment registration read with successor semantic difference recorded. |
| 11.4 | Tags | Extension and status rules reviewed; old current-status labels are not fresh registry evidence. |
| 11.5 | Formats | Historical AFRF registration does not settle current report profile. |
| 12 | Security | Reporting, DNS and authentication dependencies remain independently scoped. |
| 12.1 | Underlying mechanisms | DMARC inherits their limitations; a review here does not close those dependencies. |
| 12.2 | Reporting attacks | Flooding, malformed reports and fabricated observations require defensive processing. |
| 12.3 | DNS | DNS integrity affects policies and report destinations; it does not authenticate endpoint keys. |
| 12.4 | Display names | Suggested mitigations have bypasses; no verified-person claim follows from a pass. |
| 12.5 | External reporting | DNS abuse and sensitive failure content reviewed; current destination authorization follows successor reporting rules. |
| 12.6 | Secure transport | Reports must not expose decrypted originals merely because report transport is encrypted. |
| 13 | References | Complete lists read; each dependency still needs its own scope/status review. |
| 13.1 | Normative references | DNS, URI, IDNA, ARF and authentication dependencies identified. |
| 13.2 | Informative references | Historical deployment rationale and replaced documents are not automatic current requirements. |
| Appendix A | Design choices | Full rejected-alternative discussion read as historical rationale. |
| A.1 | S/MIME | Domain accountability differs from user-to-user protection; historical adoption claims are not current market evidence. |
| A.2 | Method exclusion | No per-method exclusion control was selected; a missing record is not an Email Next capability signal. |
| A.3 | Sender | Sender/From have different roles; do not substitute one to obtain a convenient policy result. |
| A.4 | Existence | Absence of MX/A/AAAA alone was rejected as a domain-existence test. |
| A.5 | ADSP | Subdomains, rollout and alignment motivated DMARC; not endorsement of obsolete ADSP deployment. |
| A.6 | Discovery rationale | Unbounded tree walking risk motivated old lookup; current bounded algorithm supersedes this tradeoff. |
| A.6.1 | Suffix lists | Different lists can yield different historical results. |
| Appendix B | Examples | All examples read; illustrative syntax does not establish validated wire fixtures. |
| B.1 | Alignment examples | Underlying success is assumed rather than cryptographically demonstrated. |
| B.1.1 | SPF examples | Three domain relationships reviewed; rejected erratum4907 does not change example.net/example.com separation. |
| B.1.2 | DKIM examples | Three alignments reviewed; ellipses are not executable signatures. |
| B.2 | Owner examples | Deployment staging rationale remains useful, while obsolete wire controls do not. |
| B.2.1 | Monitoring | Reporting-only publication enables observation without requesting new disposition. |
| B.2.2 | Failure reports | Optional detailed reports are not guaranteed telemetry. |
| B.2.3 | External failure reports | Authorization example requires corrected terminating semicolon under historical grammar. |
| B.2.4 | Sampling example | Historical pct and size suffix; example mailbox names differ between prose and record. |
| B.3 | Receiver example | Requires authentication and feedback collection at appropriate processing stages. |
| B.3.1 | SMTP processing | DATA-time result, receiver override and deferred retry are separate outcomes. |
| B.4 | Feedback use | Operational diagnosis benefits from both passing and failing streams; reports are not complete authoritative logs. |
| B.5 | Mail transport example | Placeholder payload, incomplete signature, wrapped filename and old extension prevent copying as a passing fixture. |
| Appendix C | XML schema | Every type, field, occurrence rule and enum read; namespace/type references and IP patterns need correction/validation before reuse. |

## Errata dispositions

Statuses below are from the captured corpus. Held proposals are not silently promoted to verified corrections; rejected reports do not amend the source.

| Erratum | Status | Disposition |
| --- | --- | --- |
| [4907](https://www.rfc-editor.org/errata/eid4907) | Rejected | Parent-domain claim confuses example.net with example.com; retain example distinction. |
| [7099](https://www.rfc-editor.org/errata/eid7099) | Held for Document Update | Duplicate filename-extension issue; verified5365 supplies correction. |
| [7100](https://www.rfc-editor.org/errata/eid7100) | Held for Document Update | Same filename-extension issue; do not count as another protocol change. |
| [5221](https://www.rfc-editor.org/errata/eid5221) | Held for Document Update | IP pattern lacks compressed IPv6 forms; proposed replacement is not a verified XSD validator. |
| [5495](https://www.rfc-editor.org/errata/eid5495) | Held for Document Update | Discovery wording omits _dmarc label that Section 6.1 specifies. |
| [5151](https://www.rfc-editor.org/errata/eid5151) | Held for Document Update | Introductory grammar repair; no wire behavior change. |
| [5220](https://www.rfc-editor.org/errata/eid5220) | Rejected | Organizational top-level-domain design change is future work, not an erratum. |
| [5229](https://www.rfc-editor.org/errata/eid5229) | Held for Document Update | Optional policy fields versus report multiplicity need explicit semantics; proposed XML is not copied unchecked. |
| [5365](https://www.rfc-editor.org/errata/eid5365) | Verified | Compressed filename example ends in .xml.gz, not .gz alone. |
| [5370](https://www.rfc-editor.org/errata/eid5370) | Rejected | Duplicate of verified5365; rejection does not make the old filename correct. |
| [5371](https://www.rfc-editor.org/errata/eid5371) | Verified | GZIP format reference is RFC1952. |
| [5440](https://www.rfc-editor.org/errata/eid5440) | Verified | Add required separator to historical v=DMARC1-only authorization records/examples. |
| [5552](https://www.rfc-editor.org/errata/eid5552) | Rejected | Claimed ban on SMTP rejection relies on an inapplicable quoted role. |
| [5773](https://www.rfc-editor.org/errata/eid5773) | Rejected | Proposed report-field redesign is not an erratum. |
| [5774](https://www.rfc-editor.org/errata/eid5774) | Held for Document Update | Removing explicit minOccurs=1 is editorial; default occurrence remains one. |
| [6439](https://www.rfc-editor.org/errata/eid6439) | Verified | External-report example compares organizational domains, not bare host names. |
| [6485](https://www.rfc-editor.org/errata/eid6485) | Held for Document Update | Example Report-ID does not satisfy imported msg-id grammar; successor report-ID contract applies to current reports. |
| [6729](https://www.rfc-editor.org/errata/eid6729) | Held for Document Update | Public/private suffix-list scope dispute; current tree-walk selection avoids adopting this proposed patch. |
| [7835](https://www.rfc-editor.org/errata/eid7835) | Held for Document Update | Verifier notes preserve filtering after each lookup; do not implement proposed deletion of the second filter. |
| [7865](https://www.rfc-editor.org/errata/eid7865) | Held for Document Update | Unescaped IPv4 separator matches non-dot characters; schema success is insufficient address validation. |

## Integration and evidence limits

The [security contract](../security.md) uses current DMARC evaluation as domain evidence only. Its [historical-report interpretation rules](../security.md#historical-report-interpretation) preserve the distinction between the two Identity-Alignment meanings. Legacy aggregate and failure reports must retain their original bytes, source format and uncertain provenance. They cannot enroll endpoint keys, authorize conversation changes, prove message delivery or expose decrypted content automatically.

No historical DMARC evaluator, XML schema compiler, DNS lookup fixture or report consumer was exercised in this review. The earlier [underscored-name update](underscored-dns.md) registers the relevant DNS namespace without changing DMARC processing; the [internationalized-authentication update](internationalized-authentication.md) separates lookup-domain conversion from original authenticated bytes. Their base reviews are recorded, while dependency closure, live registry/errata reconciliation and importer tests distinguishing old and current report semantics remain open. Existing successor reviews do not automatically validate every historical migration path.
