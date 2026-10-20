---
title: Event media-type registration proposal
order: 5
blurb: candidate name · JSON suffix · registration template
sectionNav: true
---

# Event media-type registration proposal

The proposed event media type is `application/vnd.threadlabs.email-next-event+json`. It identifies one Email Next contribution object under the [event encoding](event-encoding.md) and operation schemas. It does not identify identity bundles, MLS packets, group controls or arbitrary JSON. Those representations require their own bindings.

> [!warn] Unregistered candidate
> This is a local registration proposal, not an assigned name or a filed request. The IANA media-type list had no matching entry when checked on 19 October 2026; absence is not a reservation. Experimental use requires explicit agreement on this draft. Contact and change-controller nominations and a stable published specification are required before submission. Public interoperability is not claimed.

## Processing contract

The subtype uses the registered +json suffix. Its payload is exactly one UTF-8 JSON contribution object, subject to the draft's duplicate-member, Unicode, value-type, schema, size and depth restrictions. Binary encoding considerations describe its octets; the email carrier applies its separately defined MIME transfer encoding. A base64 transfer encoding does not change the media type or the authenticated decoded bytes.

No required or optional media parameters are defined. In particular, neither charset nor version is a parameter of this type. Generators MUST omit parameters. Under this experimental binding, a receiver encountering any parameter MUST leave structured processing inactive and preserve the source; it must not reinterpret a charset parameter as permission to decode non-UTF-8 input. The version member inside the payload selects the supported event schema and is bound by the event's protection.

This type defines no fragment identifier syntax or semantics beyond any applicable generic +json rules. JSON Pointer is not implicitly selected. A URI fragment cannot authorize a form answer, select an audience or substitute for an exact authenticated event reference.

A generic JSON processor may inspect the representation. Only an Email Next processor satisfying schema, protection-context, identity, membership, reference and replay checks may apply structured effects. The type name is untrusted input and cannot establish any of those checks.

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
| Published specification | This Email Next editor's draft, especially event encoding, identifiers, messages and form operations. A stable public revision URL must replace this local reference before submission. |
| Applications that use this media type | Experimental Email Next clients and conformance tools; this description is not an exhaustive application list or evidence of deployed support. |
| Fragment identifier considerations | No additional fragment semantics; applicable generic +json rules take precedence. |
| Deprecated alias names | N/A |
| Magic numbers | N/A; JSON object syntax is not a unique magic number. |
| File extensions | N/A |
| Macintosh file type codes | N/A |
| Person and email address for further information | Unassigned; a responsible contact must be nominated before submission. |
| Intended usage | LIMITED USE during the experimental profile. |
| Restrictions on usage | Agreed experiments implementing this draft; not a general JSON, identity-record or MLS-packet carrier. |
| Author | Email Next draft editors; the submission must identify the responsible authors. |
| Change controller | Proposed: the Threadlabs Studio project maintainer responsible for the vendor-tree registration. No appointment or registration authority is claimed by this draft. |
| Provisional registration | N/A; the RFC6838 provisional mechanism is for standards-tree registrations. |

The vendor tree accommodates noncommercial producers. A future standards-tree proposal would follow its own eligibility and review process; the project MUST NOT assume that a working-group name establishes recognition. Changes to an assigned registration must follow its change-control procedure. An incompatible replacement cannot silently reuse an established name with different semantics.

## Security and interoperability analysis

The payload contains data that can request structured interaction effects. It contains no executable program language, but treating a submit, withdrawal or edit as an action without authorization can still change state or disclose information. Parsing MUST use a data parser. Merely opening, previewing or indexing the media part must not send a response or fetch referenced resources.

The representation itself is neither encrypted nor authenticated. Protected delivery binds the exact decoded event bytes and their author, purpose, conversation and audience context. MIME headers, neighboring readable alternatives and media-type matching cannot substitute for that binding. Ordinary delivery must retain its actual unprotected status.

Parsers must enforce the event byte/depth limits, reject duplicate members before they are discarded, and preserve the original bytes. Reserialization, Unicode normalization, number coercion or first/last-member-wins parsing can produce divergent meanings or invalidate proof and duplicate-identity checks. A successful generic JSON parse does not imply a valid contribution.

This event representation defines no compression. Attachments and encrypted containers have separate bounds and security requirements. If another layer compresses content, it must enforce its own expansion limits before the event limits are evaluated. URLs, filenames, labels and resource references remain untrusted and cannot drive automatic navigation or filesystem writes.

Legacy mail clients may display an attachment or select a readable alternative. The registration cannot guarantee either behavior, conceal a control message, or advertise that all recipients support Email Next. The generated attachment-message MIME experiment uses this candidate under an explicit local profile. Fourteen tests include rejection of generic JSON, unrelated suffix types and parameters, plus acceptance of case-insensitive type spelling. The separate MLS transport still uses an opaque attachment fixture. These tests do not establish legacy-client or independent implementation interoperability.

## Basis and outstanding submission work

The [registration audit](audits/media-registration.md) and [suffix audit](audits/structured-suffixes.md) establish the applicable base rules. The [current IANA suffix entry](https://www.iana.org/assignments/media-type-structured-suffix) and RFC8259 supply the JSON encoding basis. The candidate name, parameter policy and restricted purpose are editorial choices of this draft.

Before submission: complete the event operation set and MIME binding, publish a stable specification revision, nominate the responsible contact and change controller, confirm the candidate name through the registration process, and complete the required expert review. These are visible registration prerequisites, not claims that the protocol's broader implementation and security validation are complete.
