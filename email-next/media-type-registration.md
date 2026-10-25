---
title: Event media-type registration proposal
order: 5
blurb: candidate name · JSON suffix · registration template
sectionNav: true
---

# Event media-type registration proposal

The proposed event media type is `application/vnd.threadlabs.email-next-event+json`. It identifies one Email/2 contribution object under the [event encoding](event-encoding.md) and operation schemas. It does not identify identity bundles, MLS packets, group controls or arbitrary JSON. Those representations require their own bindings.

> [!warn] Unregistered candidate
> This is a local registration proposal, not an assigned name or a filed request. The names in this draft are not reservations or a claim that a registry will accept them. Experimental use requires explicit agreement on this draft. Contact and change-controller nominations and a stable published specification are required before submission. Public interoperability is not claimed.

## Processing contract

The subtype uses the registered +json suffix. Its payload is exactly one UTF-8 JSON contribution object, subject to the draft's duplicate-member, Unicode, value-type, schema, size and depth restrictions. Binary encoding considerations describe its octets; the email carrier applies its separately defined MIME transfer encoding. A base64 transfer encoding does not change the media type or the authenticated decoded bytes.

No required or optional media parameters are defined. In particular, neither charset nor version is a parameter of this type. Generators MUST omit parameters. Under this experimental binding, a receiver encountering any parameter MUST leave structured processing inactive and preserve the source; it must not reinterpret a charset parameter as permission to decode non-UTF-8 input. The version member inside the payload selects the supported event schema and is bound by the event's protection.

This type defines no fragment identifier syntax or semantics beyond any applicable generic +json rules. JSON Pointer is not implicitly selected. A URI fragment cannot authorize a form answer, select an audience or substitute for an exact authenticated event reference.

A generic JSON processor may inspect the representation. Only an Email/2 processor satisfying schema, protection-context, identity, membership, reference and replay checks may apply structured effects. The type name is untrusted input and cannot establish any of those checks.

## Registration template

| Field | Proposed value |
| --- | --- |
| Type name | application |
| Subtype name | vnd.threadlabs.email-next-event+json |
| Required parameters | N/A |
| Optional parameters | N/A |
| Encoding considerations | Binary; one UTF-8 JSON object. No BOM. MIME transfer encoding is supplied by the email binding. |
| Security considerations | See the analysis below and the draft's security, identity and interaction requirements. The representation supplies no confidentiality or sender authentication by itself. |
| Interoperability considerations | A restricted JSON profile with explicit versioning; generic JSON validity is insufficient. Unsupported versions, parameters and operations remain inactive. Exact authenticated bytes must survive transfer decoding. |
| Published specification | This Email/2 editor's draft, especially event encoding, identifiers, messages and the selected operation schemas. Deferred general forms are outside the first-version scope. A stable public revision URL must replace this local reference before submission. |
| Applications that use this media type | Experimental Email/2 clients and conformance tools; this description is not an exhaustive application list or evidence of deployed support. |
| Fragment identifier considerations | No additional fragment semantics; applicable generic +json rules take precedence. |
| Deprecated alias names | N/A |
| Magic numbers | N/A; JSON object syntax is not a unique magic number. |
| File extensions | N/A |
| Macintosh file type codes | N/A |
| Person and email address for further information | Unassigned; a responsible contact must be nominated before submission. |
| Intended usage | LIMITED USE during the experimental profile. |
| Restrictions on usage | Agreed experiments implementing this draft; not a general JSON, identity-record or MLS-packet carrier. |
| Author | Email/2 draft editors; the submission must identify the responsible authors. |
| Change controller | Proposed: the Threadlabs Studio project maintainer responsible for the vendor-tree registration. No appointment or registration authority is claimed by this draft. |
| Provisional registration | N/A; the RFC6838 provisional mechanism is for standards-tree registrations. |

The vendor tree accommodates noncommercial producers. A future standards-tree proposal would follow its own eligibility and review process; the project MUST NOT assume that a working-group name establishes recognition. Changes to an assigned registration must follow its change-control procedure. An incompatible replacement cannot silently reuse an established name with different semantics.

## Security and interoperability analysis

The payload contains data that can request structured interaction effects. It contains no executable program language, but treating a submit, withdrawal or edit as an action without authorization can still change state or disclose information. Parsing MUST use a data parser. Merely opening, previewing or indexing the media part must not send a response or fetch referenced resources.

The representation itself is neither encrypted nor authenticated. Protected delivery binds the exact decoded event bytes and their author, purpose, conversation and audience context. MIME headers, neighboring readable alternatives and media-type matching cannot substitute for that binding. Ordinary delivery must retain its actual unprotected status.

Parsers must enforce the event byte/depth limits, reject duplicate members before they are discarded, and preserve the original bytes. Reserialization, Unicode normalization, number coercion or first/last-member-wins parsing can produce divergent meanings or invalidate proof and duplicate-identity checks. A successful generic JSON parse does not imply a valid contribution.

This event representation defines no compression. Attachments and encrypted containers have separate bounds and security requirements. If another layer compresses content, it must enforce its own expansion limits before the event limits are evaluated. URLs, filenames, labels and resource references remain untrusted and cannot drive automatic navigation or filesystem writes.

Legacy mail clients may display an attachment or select a readable alternative. The registration cannot guarantee either behavior, conceal a control message, or advertise that all recipients support Email/2. The generated attachment-message MIME experiment uses this candidate under an explicit local profile. Fourteen tests include rejection of generic JSON, unrelated suffix types and parameters, plus acceptance of case-insensitive type spelling. The separate MLS transport still uses an opaque attachment fixture. These tests do not establish legacy-client or independent implementation interoperability.

## Basis and outstanding submission work

The [registration audit](audits/media-registration.md) and [suffix audit](audits/structured-suffixes.md) establish the applicable base rules. The [current IANA suffix entry](https://www.iana.org/assignments/media-type-structured-suffix) and RFC8259 supply the JSON encoding basis. The candidate name, parameter policy and restricted purpose are editorial choices of this draft.

Before submission: freeze the proposed registration scope to a stable event schema and MIME binding, publish that specification revision, nominate the responsible contact and change controller, confirm the candidate name through the registration process, and complete the required expert review. These are visible registration prerequisites, not claims that the protocol's broader implementation and security validation are complete.


## Ordinary source-control candidate

`application/vnd.email2.stream-control+json` is an unregistered candidate with no parameters. The [ordinary-stream contract](suite-profile.md#ordinary-protected-conversations) owns its complete source-control and signed recipient-update variants, MIME placement, bounded parsing, authorization, privacy gate and failure behavior. Registration and independent implementation remain external work. An opaque attachment fixture or the managed quorum-control type does not imply support for this candidate.


## Sealed-control candidate

`application/vnd.email2.sealed-control` is an unregistered binary candidate without parameters. The [selected container](suite-profile.md#confidential-setup-and-control) owns its HPKE suite, fixed binary framing, signed intent, exact recipient/key binding, MIME and relay placement, bounds and lifecycle. The source-control JSON type above identifies decrypted logical data; it does not permit clear current-suite transport. Registration remains external work.


## Identity-administration candidate carriers

The [state1 lifecycle](identity-state.md#concurrent-administration-and-retirement) selects proposed unregistered `application/vnd.email2.identity-bundle+json` and `application/vnd.email2.identity-repair-share+json`, without parameters. They identify exactly bundle1 and repair-share1, respectively, under that contract's strict schema, byte/depth bounds, original signatures, parent validation, direct MIME placement and inert/pending behavior. They are not contribution media types and cannot activate messages, install a pin or authorize an account merely by being labeled. Administrative relationships are privacy-sensitive public evidence; selected disclosure, confidential carriage and routing remain independent. Unsupported versions remain inactive. UTF-8 JSON uses the +json convention; the [registration inventory](registration-inventory.md) supplies their draft templates; contact/controller nomination, stable filing references and actual registry review/approval remain prerequisites. Automatic current-suite mail uses the existing sealed-control media type with exact kind `identity-admin`, without a readable proof duplicate. The two proposed JSON types identify the logical objects and deliberately selected public-evidence file exports; a failed private exchange cannot authorize such an export.


The [complete registration and extension inventory](registration-inventory.md) owns the other selected media-type templates, well-known suffix requests, MLS extension request, historical fixture disposition and application-local naming boundaries.

## Mailbox-setup candidate

`application/vnd.threadlabs.mail-setup+json` is the unregistered parameter-free strict JSON wrapper for [ordinary-mail setup](mailbox-setup.md). The initial request is public metadata under its explicitly enabled disclosure policy; the response is a logical object carried only inside sealed-control. Its purpose, signatures, request correlation, bounds, exact mail placement and automatic-response exception are owned there. The [registration inventory](registration-inventory.md) supplies the common draft filing fields; no registry approval or deployed support is implied.


## Version-neutral mail-event and mail-control candidates

The [registration inventory](registration-inventory.md) also owns the parameter-free application/vnd.threadlabs.mail-event+json and application/vnd.threadlabs.mail-control candidates. The retained reply-aware agreement uses them for envelope5 and sealed1. The current [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) uses the same candidates for envelope6 and sealed2, under its own exact context, framing, bounds and purpose rules. These are explicitly version-dispatched representations, not interchangeable aliases.

For envelope6, the media-type payload is one complete delivery object. Its authored member contains canonical base64 of one original authored0 record; that member is not another MIME alternative or permission to parse arbitrary nested content. The selected wrapper and authored bounds apply independently. The type label or a generic JSON reader does not activate either record or bypass native author/audience/slot acceptance.

For sealed2, fixed MAILCTL2 magic selects the exact container only within its independently supported control binding; the selected kind and original body still require complete owning validation. Unsupported framing remains retained and inactive without trial decryption, clear fallback or another version parser. Registration still needs the existing filing prerequisites; no name or code point has been assigned by these additions.


## Ordinary authored candidate

`application/vnd.threadlabs.mail-authored+json` is a separate unregistered
candidate for the [ordinary authored carriage](event-encoding.md#ordinary-authored-carriage).
Its decoded payload is one complete original authored0 record, not envelope6 or
arbitrary JSON. The first binding admits reaction and reaction-withdraw operations
only. It supplies no encryption, authentication, native membership or authority
to apply a structured effect.

| Registration field | Proposed value |
| --- | --- |
| Type / subtype | `application` / `vnd.threadlabs.mail-authored+json` |
| Required / optional parameters | None; generators omit all parameters and receivers leave parameterized input structurally inactive. |
| Encoding | Binary; strict UTF-8 JSON without BOM. The generated MIME binding uses base64 transfer encoding. |
| Fragment semantics | No additional syntax or semantics; JSON Pointer is not implicitly selected. |
| Purpose and bounds | Exact authored0 purpose/version, original octets, existing 1,048,576-octet and depth32 bounds, and the restricted ordinary operation binding. |
| Security | Unprotected candidate data, with complete-record disclosure authorization and no automatic effects, lookup or resource retrieval. |
| Interoperability | Unknown types, parameters or unsupported operations retain readable ordinary alternatives; no reinterpretation of a failed secured carrier. |
| Contact / change controller | Unappointed; the common registration prerequisites above apply before filing. |
| Intended usage | Limited agreed experiments; no assigned name, filing or deployed interoperability is claimed. |

The common vendor-tree, suffix, registration and change-control requirements
above also apply. The ordinary representation is distinct from
`application/vnd.threadlabs.mail-event+json`, whose current payload remains a
complete envelope6 delivery. Merely recognizing either type cannot establish
recipient capability or protection status.


## Deletion-support candidate and separate control profile

The parameter-free `application/vnd.threadlabs.mail-deletion-offer+json` candidate
identifies the exact signed receiving-offer0 owned by [deletion controls](deletion-controls.md).
Its [registration-inventory row](registration-inventory.md) and the common draft
filing fields form its template. It is read-only capability metadata, not proof
of mailbox ownership, a deletion command or a public discovery response.

The request itself remains encrypted under the version-neutral mail-control
candidate. Exact MAILDEL0 magic selects sealed-deletion-v0 only with independently
offered support and its dedicated receiving-key inventory. It does not widen
sealed-control-v2, infer another profile from a failed decryption, or permit a
clear request fallback. Bounds, original signatures, recipient and offer binding,
key custody and silent durable acceptance are owned by the deletion chapter.
Registration, external interoperability and security validation remain separate.
