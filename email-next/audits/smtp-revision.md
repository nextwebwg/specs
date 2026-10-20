---
title: SMTP revision audit
sectionNav: true
---

# SMTP revision audit

**Coverage:** complete 125-page [SMTP revision 44](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5321bis-44/), including every appendix, transcript, change list and end matter. Ranges below group related sections. This is a revision review, separate from the published RFC inventory; it does not claim publication or complete dependency review.

## Dispositions

| Sections | Disposition |
| --- | --- |
| 1–1.4 | Revision consolidates 5321, 1846, 7504 and 7505; applicability guidance remains separate. Draft status is not final publication. Historical example names are illustrative. |
| 2–2.1 | Final positive DATA reply transfers responsibility. Submission, relay and delivery roles differ; acceptance is not reading or endpoint processing. |
| 2.2–2.2.1 | EHLO extension framework preserves legacy HELO compatibility. Server upgrade alone establishes no endpoint capability. |
| 2.2.2 | Register advertised keywords; ignore unknown parseable advertisements, terminate when EHLO cannot be reliably parsed. Registration is not technical endorsement. |
| 2.2.3 | Downstream extension failure can trigger retry or alternate routing. Generic fallback advice does not authorize weakening required protection. |
| 2.3–2.3.4 | Envelope and content are separate. Sender/receiver describe hop roles; MUA/MTA boundaries do not establish cryptographic authority. |
| 2.3.5 | Qualified domain requirements and submission exceptions; relay must not infer local aliases. Postmaster exception retained. |
| 2.3.6–2.3.9 | Stateful buffers, numeric replies and strict CRLF framing. Message content includes headers; unextended transport is ASCII. |
| 2.3.10–2.3.12 | Relay preservation differs from gateway transformation. Local-part semantics belong to destination domain. Sessions contain separate transactions. |
| 2.4 | Preserve local-part case; 8BITMIME does not permit binary data or internationalized envelopes. Prose constrains ABNF. |
| 3–3.2 | Greeting, 521 no-service behavior and EHLO/HELO initiation reviewed. Protocol fallback cannot waive required protection. |
| 3.3 | MAIL then RCPT then DATA; send content only after 354. Late failure does not encode per-recipient outcomes. Resent-field cardinality is not a rejection basis. |
| 3.4–3.4.1 | Silent forwarding and optional 251/551 correction can conceal or reveal destinations. Routing correction does not establish identity succession. |
| 3.4.2–3.4.2.2 | Aliases preserve reverse-path; lists change error routing. Extensive list modifications constitute new submission. Expansion is not authenticated group membership. |
| 3.5–3.5.4 | VRFY/EXPN are diagnostic, not key discovery. Syntax-only success is invalid; 252 preserves uncertainty. Source expansion for deduplication is discouraged. |
| 3.6–3.6.2 | Relays preserve content except allowed trace/loop handling; failure notifications use null reverse-path. Limited clients should use submission. |
| 3.7–3.7.6 | Gateway transformations must respect layering, preserve existing Received fields and avoid envelope leakage. Foreign-system translation can lose information. |
| 3.8 | QUIT, shutdown and timeout rules; unexpected loss is temporary handling, not recall of accepted mail. |
| 4–4.1.1 | Command syntax and buffers reviewed. No invented parameters on DATA, RSET or QUIT without extension support. |
| 4.1.1.1 | Latest successful EHLO capabilities govern; keywords case-insensitive. Extra client identification text after argument prohibited. |
| 4.1.1.2–4.1.1.3 | MAIL starts a transaction; RCPT appends recipients. Advertised parameter requirements and case-insensitive Postmaster exception retained. |
| 4.1.1.4 | Strict DATA termination; no extra empty line, no bare-LF terminator. Final reply applies to transaction, partial later failure uses notification. |
| 4.1.1.5–4.1.1.10 | RSET cancels pending state; VRFY/EXPN/HELP/NOOP do not modify message buffers. QUIT does not undo completed transactions. |
| 4.1.1.11 | 555 unsupported parameters differs from 455 temporary inability. This body section is absent from the contents listing; coverage uses the body. |
| 4.1.2 | Nonempty quoted local-part grammar, equivalent quoting and preserved internal spaces. No global whitespace reduction; extension-dependent character repertoire. |
| 4.1.3 | IPv6 literal grammar revised; generation and acceptance require reconciliation with RFC 5952 and related address standards. |
| 4.1.4 | Transaction sequencing, successful reset and rejected-EHLO state preservation. New commands must define state effects. |
| 4.2–4.2.1 | Recognized full and supplementary codes precede severity fallback. Reply prose is not a capability channel. Multiline codes agree; tolerate final bare code. |
| 4.2.2–4.2.3 | Both complete code tables reviewed; 4xx temporary and 5xx permanent meaning persists despite descriptive wording. |
| 4.2.4–4.2.4.3 | 502 recognized but unimplemented; 521 host/no service and 556 domain/no service differ. Negative final DATA forbids subsequent server delivery. |
| 4.3–4.3.2 | One reply per command even with pipelining; all command/reply tables reviewed. Unknown valid codes handled by severity. |
| 4.4–4.4.1 | Prepend Received without modifying existing trace; FOR contains at most one path. Privacy profile additionally prevents other-recipient disclosure. |
| 4.4.2–4.4.3 | Return-Path represents error routing, with delivery and gateway handling exceptions. It is not an author identity assertion. |
| 4.4.4–4.4.5 | Additional trace registration and full trace grammar reviewed. Trace classification does not authenticate its contents. |
| 4.5–4.5.1 | Minimum commands and Postmaster requirements reviewed; no-service wording retains a legacy 554 reference that needs careful interpretation. |
| 4.5.2 | Dot transparency and reversible storage transformations preserve content; neither defines signature canonicalization. |
| 4.5.3–4.5.3.1.9 | All size subsections reviewed: local-part 64, domain 255, path 256, command/reply 512 and text 1000 octets; extension exceptions apply. At least 64K message support and 100 recipient buffering are not universal maximums. |
| 4.5.3.1.10 | 452 for recipient-buffer exhaustion. Historical 552 reinterpretation advice removed; site-policy limits remain distinct. |
| 4.5.3.2–4.5.3.2.7 | All timeout values reviewed: greeting/MAIL/RCPT five minutes, DATA start two, block three, completion ten; server wait five. Configurable per-command timing, not chat-speed timeout. |
| 4.5.4–4.5.4.2 | Queues preserve envelope; delayed configurable retries and destination-aware backoff. Do not cache MAIL 5xx for later messages. Incoming host traffic is not user presence. |
| 4.5.5 | Null reverse-path prevents notification loops. Specific MDN destination rules override the broad notification summary; see reconciliation below. |
| 5–5.1 | Explicit versus implicit MX, transient DNS retry, preference sorting, self-loop pruning and tie randomization reviewed. Misconfigured MX-to-CNAME remains discouraged but this revision recommends processing observed CNAME responses. |
| 5.2 | IPv4/IPv6 and multihomed routing require applicable local capability and ordered alternatives; no endpoint trust inference. |
| 6–6.1 | Acceptance requires durable preservation and later failure handling. Final-reply loss permits duplicate delivery; application effects need independent deduplication. |
| 6.2 | Exceptional hostile-message disposal and backscatter prevention mean silence is not proof of delivery. |
| 6.3 | Loop detection required; typical Received-count threshold at least 100. Control exchange needs separate loop bounds. |
| 6.4 | Submission repair has scoped authority; intermediate relay cannot repair headers. Protected content changes require explicit authorized semantics. |
| 7–7.1 | Hop authentication differs from endpoint message authentication; legitimate delegated sending must remain possible. |
| 7.2–7.3 | Do not infer header audiences from envelope recipients. Disabled VRFY/EXPN returns uncertainty, not fabricated verification. |
| 7.4–7.7 | Authenticate routing suggestions, assess greeting/version and trace disclosure; sensitive forwarding targets need protection. |
| 7.8–7.9 | Operational abuse defenses and refusal policy can depart normal behavior; they do not establish application outcomes or permission to downgrade. |
| 8–8.1.1.1 | IETF and FCFS registration models differ in review and change control; neither allocates Email Next identifiers automatically. |
| 8.1.1.2 | All twelve template fields reviewed. None differs from Not supplied; command-length increments and submission applicability are explicit. Legacy updates prohibited; FCFS transition follows specified process. |
| 8.1.2–8.1.4 | Literal tags require Standards Action; via/with RFC Required; additional Received clauses IETF Review. Registry categories must not be conflated. |
| 8.2–8.3.2 | Registry regrouping, stable old URLs and parameter-registry closure reviewed. Unchanged registries remain unchanged. |
| 8.3.3–8.3.3.3 | Field migration/defaults and new VRFY entry reviewed. Submission defaults need reconciliation with source specifications and cleanup work. |
| 8.3.4–8.4 | Transmission registry changes, updated references and removal of X-prefix registration restriction reviewed; live registry state is separate evidence. |
| 9–10.2 | Acknowledgments, all normative and informative references read. Referenced documents are not thereby audited; dependency closure remains open. |
| A | Eight-bit TCP transport does not authorize unnegotiated binary content. |
| B | Separate submission envelope preferred. Header-derived submission fallback is not authorization for header-only foreign gatewaying or rewriting compliant protected mail. |
| C–C.4 | All four transcripts reviewed: mixed recipients, abort, relay and verification. Illustrative abbreviated messages are not complete conformance fixtures. |
| D–D.6 | All deprecated features reviewed: TURN, source routes, HELO, numeric literals, old dates and terminal delivery. None provides invisible legacy control delivery. |
| E–E.2 | All ten change items and individual errata decisions compared with the existing RFC audit. Incorporation does not change an erratum’s original status. |
| F–F.15 | All fifteen revision logs read; removed proposals and historical notes do not override final body text. |
| G and end matter | Editorial notes, index and author material read; no additional protocol requirements. |

## Errata reconciliation

Appendix E addresses 1543, 1683, 1851, 2578, 4198, 4315, 5414 and 5711. It addresses the concern behind rejected 1820 with a different change and removes the sentence discussed by rejected 4055. It records no change for 3447, 4079, 4265 and 6561; 4315 revisits the IPv6 issue associated with 2467. The [published SMTP audit](smtp.md) retains each original status. A change in this revision does not retroactively make a rejected erratum verified.

## Specific rules and unresolved discrepancies

RFC 8098 requires MDNs to use Disposition-Notification-To destinations, with Return-Path serving the automatic-send privacy comparison. The broad reverse-path summary in revision §4.5.5 must not override those specific rules. The [transport contract](../transport.md) preserves this distinction. Full MDN review remains pending.

The [live SMTP registry](https://www.iana.org/assignments/smtp), inspected on 19 October 2026, already exposes IETF/FCFS registration models and expanded fields while referring to an unnumbered revision-43 reference. Its submission-use entries include inconsistencies addressed by the proposed [registry cleanup](registry-cleanup.md); BURL’s column and submission-only note disagree. Registry deployment does not prove final RFC publication or validate this proposal.

The revision retains a legacy 554 reference in its Postmaster exception despite its newer 521 discussion. Its final change-log date also differs from the preceding version’s heading. These observations are recorded without inventing a new protocol rule or publication date.

## Consequences for Email Next

The transport and identity chapters now distinguish server capability from endpoint support, routing correction from identity succession, transaction acceptance from recipient outcomes, and retry from a new contribution. Required protection survives alternate routes and compatibility failures. No Email Next SMTP keyword has been registered.

Remaining work includes verification of proposed registry corrections, applicable dependency audits and implementation-level interoperability validation. This textual review is not a security certification.
