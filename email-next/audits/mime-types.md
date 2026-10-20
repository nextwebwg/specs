---
title: MIME media types audit
sectionNav: true
---

# MIME media types audit

Existing multipart alternatives support progressively richer representations. They do not guarantee identical presentation in every client, invisible control parts or authentication of embedded actions.

**Coverage:** complete RFC 2046 text, collected grammar and 14 retrieved errata reviewed on 19 October 2026. Base-document review complete; companion standards, updates, registries and actual-client behavior remain open. Source section numbering is corrected using verified erratum509.

Sources: [RFC 2046](https://www.rfc-editor.org/rfc/rfc2046.html), [metadata](https://www.rfc-editor.org/rfc/rfc2046.json), [errata](https://www.rfc-editor.org/errata/rfc2046).

## Section dispositions

| Section | Disposition and consequence |
| --- | --- |
| 1 — Introduction | Inherited extensible type/parameter model; current registration procedure remains a dependency. |
| 2 — Definition of a Top-Level Media Type | Inherited top-level definition requirements; Email Next proposes no new top-level type. |
| 3 — Overview Of The Initial Top-Level Media Types | Inherited discrete/composite distinction; historical initial list is not a current registry inventory. |
| 4 — Discrete Media Type Values | Inherited opaque discrete bodies; MIME parsing alone does not validate their internal formats. |
| 4.1 — Text Media Type | Inherited text semantics; display-only reconstruction must not interpret plain text as authored executable markup. |
| 4.1.1 — Representation of Line Breaks | Inherited canonical text CRLF; visual wrapping is media-specific, not wire-line preservation. |
| 4.1.2 — Charset Parameter | Inherited charset rules subject to RFC6657 and current registries. Reported8667 is not an adopted correction; old charset list is not exhaustive today. |
| 4.1.3 — Plain Subtype | Inherited plain-text representation; richer local presentation remains a reversible derived view. |
| 4.1.4 — Unrecognized Subtypes | Inherited unknown-text fallback conditional on supported charset; otherwise opaque. Verified6582 corrects spelling of media type. |
| 4.2 — Image Media Type | Inherited unknown-image fallback; any generic viewer inherits its supported formats’ security exposure. |
| 4.3 — Audio Media Type | Inherited basic audio definition and unknown fallback; no mandatory autoplay or codec support added. |
| 4.4 — Video Media Type | Inherited video scope, synchronized sound allowance and unknown fallback; no autoplay authorization. |
| 4.5 — Application Media Type | Extension opportunity: structured application data; active-content precedent is not permission to execute sender programs. |
| 4.5.1 — Octet-Stream Subtype | Inherited opaque-data handling; never find and execute a program from a sender-supplied parameter. |
| 4.5.2 — PostScript Subtype | Reviewed all eight PostScript risk categories: filesystem access, persistent state, device settings, native code, extensions, resource exhaustion, binary/line ambiguity and interpreter bugs. PostScript execution excluded from proposed rendering baseline. |
| 4.5.3 — Other Application Subtypes | Inherited unknown-application opaque fallback; ordinary legacy clients may expose unsupported rich data as an attachment. |
| 5 — Composite Media Type Values | Inherited composite MIME processing; no extra untyped control layer. |
| 5.1 — Multipart Media Type | Inherited part/message distinction, optional part headers, unique noncolliding boundaries and multipart transfer restrictions. Non-Content headers cannot be relied on inside parts. |
| 5.1.1 — Common Syntax | Inherited delimiter grammar, 1–70-character boundaries, attached CRLF, ignored preamble/epilogue, quoted parameters and single-part allowance. Held6776 does not add a mandatory initial extra CRLF. |
| 5.1.2 — Handling Nested Messages and Multiparts | Inherited outer-boundary recognition at any nesting depth, including truncated inner entities. Recovered structure is not authenticated structure. |
| 5.1.3 — Mixed Subtype | Inherited ordered independent mixed parts and unknown multipart fallback. |
| 5.1.4 — Alternative Subtype | Inherited equivalent alternatives, preferred-last ordering and distinct entity IDs. Verified6800 removes automatic simultaneous display of multiple alternatives; supported format selection must respect local/user choice. |
| 5.1.5 — Digest Subtype | Inherited digest default message/rfc822; corrected example date507 and spelling510. Not selected for rich contribution packaging. |
| 5.1.6 — Parallel Subtype | Inherited parallel semantics; not a synchronization protocol or guaranteed simultaneous rendering. |
| 5.1.7 — Other Multipart Subtypes | Inherited unknown multipart treated as mixed; new multipart subtype cannot guarantee hidden controls. |
| 5.2 — Message Media Type | Inherited encapsulated-message semantics and prohibition on modifying embedded headers; forwarded original remains separate from forwarding author. |
| 5.2.1 — RFC822 Subtype | Inherited message/rfc822 rules and special minimum embedded headers; later internationalized message types require separate audit. |
| 5.2.2 — Partial Subtype | Inherited partial-message identifiers, numbering and 7bit constraints; not selected for automatic rich-event fragmentation. |
| 5.2.2.1 — Message Fragmentation and Reassembly | Inherited line-boundary fragmentation and exact outer/inner header merging; reassembly does not confer author authentication. |
| 5.2.2.2 — Fragmentation and Reassembly Example | Example reviewed with verified588 correcting reassembled header order; no automatic trusted event inferred from fragments. |
| 5.2.3 — External-Body Subtype | Inherited external-body reference, phantom-body distinction and required embedded Content-ID; not selected as browser-link security mechanism. |
| 5.2.3.1 — General External-Body Parameters | Inherited mandatory access type, optional expiry/size/permission. Availability expiry is not revocation, and read-write labeling is not access authorization. |
| 5.2.3.2 — The 'ftp' and 'tftp' Access-Types | FTP/TFTP access reviewed; excluded from baseline automatic retrieval. Do not embed user credentials in MIME parameters. |
| 5.2.3.3 — The 'anon-ftp' Access-Type | Anonymous FTP reviewed; excluded from baseline automatic retrieval and implicit email-address disclosure. |
| 5.2.3.4 — The 'local-file' Access-Type | Local-file access reviewed; no authority for a received message to read local paths. |
| 5.2.3.5 — The 'mail-server' Access-Type | Mail-server access reviewed; arbitrary phantom-body commands excluded from automatic rich interactions and key discovery. |
| 5.2.3.6 — External-Body Security Issues | Inherited explicit permission before external-body resolution and separate integrity of fetched content. No rendering-triggered requests. |
| 5.2.3.7 — Examples and Further Explanations | Examples and transparent merging reviewed with verified589/7341. Same Content-ID across access methods does not prove fetched-byte integrity. |
| 5.2.4 — Other Message Subtypes | Inherited unknown-message opaque fallback; future message-type encoding guidance requires later update review. |
| 6 — Experimental Media Type Values | Historical experimental naming reviewed; defer selected media name to current registration rules rather than assuming X-prefix is current best practice. |
| 7 — Summary | Summary reviewed; no new requirements. |
| 8 — Security Considerations | Security section corrected from duplicate9 by verified509; active-content implications apply to proposed controls. |
| 9 — Authors' Addresses | Author information reviewed; no protocol behavior. |
| Appendix A — -- Collected Grammar | Collected grammar reviewed; verified508 permits trailing non-CRLF discard text. Appendix body-part shorthand must be read with detailed grammar/prose. |

## Errata dispositions

| Erratum | Status | Consequence |
| --- | --- | --- |
| [507](https://www.rfc-editor.org/errata/eid507) | Verified | Correct example weekday. |
| [508](https://www.rfc-editor.org/errata/eid508) | Verified | Correct appendix discard-text grammar. |
| [509](https://www.rfc-editor.org/errata/eid509) | Verified | Security section is8; author section remains9. |
| [510](https://www.rfc-editor.org/errata/eid510) | Verified | Spelling only. |
| [511](https://www.rfc-editor.org/errata/eid511) | Verified | Remove duplicated image overview text. |
| [588](https://www.rfc-editor.org/errata/eid588) | Verified | Preserve reassembled header ordering in example. |
| [589](https://www.rfc-editor.org/errata/eid589) | Verified | Restore missing external-body parameter separator. |
| [4609](https://www.rfc-editor.org/errata/eid4609) | Held for Document Update | Held spelling correction; no behavior change. |
| [6582](https://www.rfc-editor.org/errata/eid6582) | Verified | Correct opaque fallback media-type spelling. |
| [6583](https://www.rfc-editor.org/errata/eid6583) | Rejected | Rejected spelling report; no behavior change. |
| [6800](https://www.rfc-editor.org/errata/eid6800) | Verified | Do not automatically show multiple alternatives; choose one or offer user choice. |
| [6776](https://www.rfc-editor.org/errata/eid6776) | Held for Document Update | Held proposed initial-CRLF requirement; not adopted. |
| [7341](https://www.rfc-editor.org/errata/eid7341) | Verified | Correct access spelling. |
| [8667](https://www.rfc-editor.org/errata/eid8667) | Reported | Reported ASCII octet clarification; not adopted. |

## Design and validation consequences

Use plain, HTML and structured alternatives for one contribution, with one selected presentation. Resource-containing alternatives require the separate multipart/related audit before their nesting is finalized. Keep essential fallback content in actual body parts, not preambles. Keep automatic control processing out of external-body retrieval and mail-server commands.

Required fixtures: unknown alternatives; user preference for plain text; nested malformed parts terminated by outer boundaries; empty part headers; digest defaults; missing closing boundary; boundary prefix collisions; distinct part/container Content-IDs; external-body permission; and fragmentation header merging. These are proposed validation cases, not executed tests.
