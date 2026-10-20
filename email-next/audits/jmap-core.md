---
title: JMAP core audit
sectionNav: true
---

# JMAP core audit

The complete captured [RFC8620](https://www.rfc-editor.org/rfc/rfc8620.html) text has been reviewed, including examples, registration entries, references and front matter. JMAP supplies mailbox synchronization mechanisms; its record identifiers, query states and push notifications do not establish authenticated conversation identity or causal order.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Generic synchronization is separate from the mail data model. |
| 1.1 | Notational Conventions | Typed objects, nullability and method notation constrain interpretation. |
| 1.2 | The Id Data Type | Provider identifiers are scoped to type and account, not authenticated authors. |
| 1.3 | The Int and UnsignedInt Data Types | Integer ranges and JSON number handling require validation. |
| 1.4 | The Date and UTCDate Data Types | Date formats do not establish causal ordering or trusted time. |
| 1.5 | JSON as the Data Encoding Format | I-JSON decoding precedes object interpretation. |
| 1.6 | Terminology | User, account and record roles remain distinct. |
| 1.6.1 | User | A service user is not automatically an Email Next principal. |
| 1.6.2 | Accounts | Shared accounts and primary accounts do not define conversation authority. |
| 1.6.3 | Data Types and Records | Records belong to account/type namespaces. |
| 1.7 | The JMAP API Model | Batched method calls and separate binary transfers are retrieval mechanisms. |
| 1.8 | Vendor-Specific Extensions | Vendor extensions require explicit capability handling. |
| 2 | The JMAP Session Resource | Session state, permissions, global/account capabilities and limits are independently scoped. |
| 2.1 | Example | Verified erratum 5791 corrects the example comma and maxConcurrentRequests spelling. |
| 2.2 | Service Autodiscovery | Discovery and redirects do not authorize credential disclosure to arbitrary origins. |
| 3 | Structured Data Exchange | Request, method and record outcomes are separate scopes. |
| 3.1 | Making an API Request | Authenticated JSON POST does not itself authenticate a conversation author. |
| 3.2 | The Invocation Data Type | Invocation identifiers correlate calls and responses, not persistent effects. |
| 3.3 | The Request Object | Capability opt-in and createdIds are request mechanisms, not replay protection. |
| 3.3.1 | Example Request | Example illustrates batching and capability declaration, not atomicity. |
| 3.4 | The Response Object | One call can produce multiple responses; session changes require reconciliation. |
| 3.4.1 | Example Response | Mixed responses and later errors must be inspected individually. |
| 3.5 | Omitting Arguments | Omission uses declared defaults; required arguments cannot be arbitrarily omitted. |
| 3.6 | Errors | Failure scopes do not imply rollback of other methods. |
| 3.6.1 | Request-Level Errors | Problem details distinguish malformed requests, unsupported capability and limits. |
| 3.6.1.1 | Example | Request-error example is illustrative, not an executable conformance vector. |
| 3.6.2 | Method-Level Errors | Partial failure requires resynchronization; unknown transport outcome is not a no-change guarantee. |
| 3.7 | References to Previous Method Results | Resolve first matching call identifier then method name; wildcard JSON pointers are not event references. |
| 3.8 | Localisation of User-Visible Strings | Localized text carries no additional authority. |
| 3.9 | Security | Reject invalid arguments under the applicable method contract. |
| 3.10 | Concurrency | Calls are ordered within a request but other requests can interleave. |
| 4 | The Core/echo Method | Echo checks service communication, not conversation capability or trust. |
| 4.1 | Example | Echo preserves arguments; example does not prove mailbox functionality. |
| 5 | Standard Methods and Naming Convention | Method families depend on the data type; not every type implements all methods. |
| 5.1 | /get | Match returned records by identity; ordering, deduplication and notFound must be handled. |
| 5.2 | /changes | Change feeds can coalesce events and return intermediate states; they are not activity logs. |
| 5.3 | /set | Per-record atomicity, patch rules and state preconditions do not create a batch transaction. |
| 5.4 | /copy | Copy and deletion are separate phases; inspect both responses and new account identities. |
| 5.5 | /query | Query state covers ordered matching identifiers, not all record content. |
| 5.6 | /queryChanges | Apply matching-state deltas; uncertain sparse positions require rebuilding under the adapter rule. |
| 5.7 | Examples | Worked examples contain omissions and inconsistencies; do not infer permissive parsing from them. |
| 5.8 | Proxy Considerations | Proxies propagate creation identifiers and resolve cross-backend result references; cross-account copy needs implementation. |
| 6 | Binary Data | Blob identifiers denote immutable bytes, not authenticated metadata or sharing permission. |
| 6.1 | Uploading Binary Data | Uploads are account-scoped, initially uploader-private and potentially evicted; retain local source. |
| 6.2 | Downloading Binary Data | Requested filename/type are not intrinsic blob properties; downloads require authenticated access. |
| 6.3 | Blob/copy | Copy results map account-scoped identifiers with per-blob failures. |
| 7 | Push | Coalesced or dropped push events are synchronization hints, not contributions. |
| 7.1 | The StateChange Object | Account/type state maps trigger authenticated retrieval. |
| 7.1.1 | Example | In-flight write optimization requires matching both prior and resulting state. |
| 7.2 | PushSubscription | HTTPS destination, verification, encryption, credential lifetime and device privacy rules apply. |
| 7.2.1 | PushSubscription/get | Subscriptions are credential-scoped; get must not expose URLs or keys. |
| 7.2.2 | PushSubscription/set | Immutable destination/keys require recreation; verify before subsequent notifications. |
| 7.2.3 | Example | Creation/verification races and server-clamped renewal are illustrated. |
| 7.3 | Event Source | Event-stream cursors and pings track service synchronization, not author identity or presence. |
| 8 | Security Considerations | Transport and service safeguards do not replace endpoint content protection. |
| 8.1 | Transport Confidentiality | TLS and certificate checks apply; current guidance dependencies require reconciliation. |
| 8.2 | Authentication Scheme | Basic authentication is discouraged; per-client revocation matters. |
| 8.3 | Service Autodiscovery | DNS and well-known discovery can expose credentials if service identity is not checked. |
| 8.4 | JSON Parsing | Complete JSON parsing and bounded resource use remain necessary. |
| 8.5 | Denial of Service | Advertised and enforced service limits mitigate amplification and resource exhaustion. |
| 8.6 | Connection to Unknown Push Server | Constrain outbound destinations, subscription count and creation rates; verification is not proof of benign service. |
| 8.7 | Push Encryption | Third-party push requires encryption and rejection of unprotected notifications; algorithm agility is external. |
| 8.8 | Traffic Analysis | Encryption does not conceal correlated request and notification timing. |
| 9 | IANA Considerations | Registration rules do not establish adoption of Email Next. |
| 9.1 | Assignment of jmap Service Name | Service-name allocation supports discovery, not endpoint trust. |
| 9.2 | Registration of Well-Known URI Suffix for JMAP | The jmap well-known suffix locates a session resource. |
| 9.3 | Registration of the jmap URN Sub-namespace | Registered JMAP URNs have a defined namespace owner and registry. |
| 9.4 | Creation of "JMAP Capabilities" Registry | Capability URI registration is administrative; review depends on intended use. |
| 9.4.1 | Preliminary Community Review | Community review is recommended for common-use capabilities. |
| 9.4.2 | Submit Request to IANA | Submission destination is specified; no Email Next registration was submitted. |
| 9.4.3 | Designated Expert Review | Expert review checks documentation, collisions and relevant IETF work. |
| 9.4.4 | Change Procedures | Changes use review procedures; entries become obsolete rather than being deleted. |
| 9.4.5 | JMAP Capabilities Registry Template | Registration template includes security/privacy and change control. |
| 9.4.6 | Initial Registration for JMAP Core | Core registration is distinct from extension capability registrations. |
| 9.4.7 | Registration for JMAP Error Placeholder in JMAP Capabilities | Error placeholder reserves a namespace, not an advertised service feature. |
| 9.5 | Creation of "JMAP Error Codes" Registry | Problem-detail error URNs and short method-error names use different forms. |
| 9.5.1 | Expert Review | Review considers syntax, behavior and unauthorized information disclosure. |
| 9.5.2 | JMAP Error Codes Registry Template | Error template describes intended use and ownership. |
| 9.5.3 | Initial Contents for the JMAP Error Codes Registry | Initial error entries retain their owning method/request/record scopes. |
| 10 | References | Reference entries have been read; dependency closure is separate. |
| 10.1 | Normative References | HTTP, TLS, JSON, URI, collation, OAuth and Web Push dependencies need current-version reconciliation. |
| 10.2 | Informative References | Immutable HTTP caching is informative and does not grant attachment access. |

## Updates and errata

The [RFC information page](https://www.rfc-editor.org/info/rfc8620/) identifies RFC8620 as Proposed Standard and lists RFC9404 and RFC9670 as updates. Their base reviews are recorded separately in [JMAP blobs](jmap-blobs.md) and [JMAP sharing](jmap-sharing.md). The transport adapter contract incorporates their capability, resource and authorization boundaries; implementation validation and dependency closure remain unfinished.

The captured errata registry contains verified [5791](https://www.rfc-editor.org/errata/eid5791), correcting a missing comma and the plural maxConcurrentRequests property in the session example. It also contains five Reported entries: [6603](https://www.rfc-editor.org/errata/eid6603) on upToId and old/new result positions, [6604](https://www.rfc-editor.org/errata/eid6604) on sparse-query invalidation, [6605](https://www.rfc-editor.org/errata/eid6605) on empty-result position, [6606](https://www.rfc-editor.org/errata/eid6606) on explicitly requesting core capability, and [6607](https://www.rfc-editor.org/errata/eid6607) on creation identifiers in update/destroy keys. They are not treated as approved corrections. The live all-status listing on 20 October 2026 matches all six captured records, including original/corrected text and notes; current metadata matches the recorded relationships.

The adapter conservatively rebuilds an uncertain sparse query view instead of retaining potentially shifted positions. This is an Email Next requirement addressing the reported issue, not silent amendment of RFC8620.

## Examples and implementation limits

The Todo whole-object patch changes a server-set estimate despite claiming equivalence to a minimal patch. Another example uses null for added despite the declared array type. Several responses are abbreviated. These examples have been read as illustrations, not validated as executable wire vectors or used to loosen the declared schemas.

The [mailbox integration chapter](../mailbox-integration.md) specifies account and principal separation, request failure scopes, synchronization, copying, attachment access and push handling. No JMAP adapter or provider interoperability has been demonstrated by this review.

## Remaining dependencies

JMAP Mail (RFC8621) is a separate data-model review. The separately reviewed RFC9404 and RFC9670 updates must be reconciled with this core review. Web Push and its encryption, EventSource, URI templates, collation, OAuth, JSON, TLS/service identity, HTTP and problem-details dependencies require reconciliation with current versions and the wider audit inventory. Reading their reference entries does not establish substantive review. Registration of a capability would not itself establish standards adoption or security assurance.
