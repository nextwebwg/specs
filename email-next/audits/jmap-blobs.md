---
title: JMAP blob management audit
sectionNav: true
---

# JMAP blob management audit

The complete base text of [RFC9404](https://www.rfc-editor.org/rfc/rfc9404.html), including every example, property, registration table, reference and end-matter section, has been reviewed. No entries for this RFC occur in the captured full errata corpus. The [core JMAP base audit](jmap-core.md) is recorded separately; dependency and live registry closure remain unfinished.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Inline blob methods reduce round trips and add reverse lookup; they do not authenticate message resources. |
| 2 | Conventions Used in This Document | Core JMAP types and requirement conventions reviewed. |
| 3 | Addition to the Capabilities Object | Blob capability has session and per-account placement. |
| 3.1 | urn:ietf:params:jmap:blob | Creation-size/source-count limits and supported types/digests are account capabilities; at least64 sources supported. Null size limit does not guarantee resource availability or remove client bounds. |
| 3.1.1 | Capability Example | Capability example reviewed; server digest preference is not Email/2 cryptographic algorithm policy. |
| 4 | Blob Methods | Blob/copy remains core; blobs are arbitrary octet sequences. |
| 4.1 | Blob/upload | Upload concatenates ordered sources; invalid ranges/data fail the creation without guessing. Created IDs support later methods; expiry semantics remain core JMAP. Media type is a hint. |
| 4.1.1 | Blob/upload Simple Example | Wrapped base64 is a publication convenience, not wire whitespace permission. |
| 4.1.2 | Blob/upload Complex Example | Concatenation/backreferences reviewed; example omits required accountId inputs and includes oldState despite stateless prose. Do not use as a complete request fixture unchanged. |
| 4.2 | Blob/get | Get permits short ranges with isTruncated; size is whole-blob size, while digest is selected returned octets. Invalid UTF-8 yields encoding diagnostics and base64 where requested. |
| 4.2.1 | Blob/get Simple Example | Full and ranged published SHA1 digests plus ranged SHA256 digest independently reproduced from literal example bytes; this is not an authentication check. |
| 4.2.2 | Blob/get Example with Range and Encoding Errors | Range/encoding examples reviewed; explicit text-error response omits required null text field and upload type results appear inconsistent with supplied hints. Normative rules govern fixtures. |
| 4.3 | Blob/lookup | Reverse lookup respects account/type capabilities; inaccessible or nonexistent blobs yield indistinguishable empty matches. Containment is directional, not arbitrary graph reachability. |
| 4.3.1 | Blob/lookup Example | Example uses notFound despite earlier indistinguishable empty-array rule; record conflict and do not adopt an existence-leaking response distinction. |
| 5 | Security Considerations | Apply access control to lookup, distrust supplied media types, scan composed results where applicable and bound digest costs; these are provider controls, not endpoint authentication. |
| 6 | IANA Considerations | Capability, error and data-type registrations reviewed separately from current registry state. |
| 6.1 | JMAP Capability Registration for "blob" | Registers blob capability. |
| 6.2 | JMAP Error Codes Registration for "unknownDataType" | UnknownDataType covers unknown names or missing required capability. |
| 6.3 | Creation of "JMAP Data Types" Registry | Creates specification-required data-type registry with blob/state-change flags; initial table is not a live registry snapshot. |
| 7 | References | Complete reference lists, acknowledgments and author end matter reviewed. |
| 7.1 | Normative References | Core JMAP, base64, digest and requirement references remain separately scoped; digest-registry successor applicability requires review. |
| 7.2 | Informative References | IMAP literal, registration, JMAP Mail and MDN references do not define Email/2 resource manifests. |

## Source inconsistencies

The upload type description includes application/octet-string, while examples use application/octet-stream. Several abbreviated requests omit accountId. The complex upload response includes oldState despite the stateless-method description. The encoding-error example omits data:asText:null where the normative text requires it, and the lookup example returns notFound rather than the required indistinguishable empty matches for inaccessible or absent blobs. These are recorded discrepancies, not approved errata. A production adapter must resolve them explicitly and preserve the normative access-control boundary.

## Example calculation

The literal45-octet sentence in Section4.2.1 reproduces its full SHA1 value. Its9-octet range at offset4 reproduces both published SHA1 and SHA256 values. These calculations validate those example bytes only; they do not recommend SHA1 for Email/2 authentication or verify the other examples as complete executable API exchanges.

## Resource binding

A blob ID identifies storage within a service context; it is not a globally authenticated content identity. Blob/get size describes the whole stored blob, while a returned digest describes the selected returned bytes. A partial response must not satisfy a full-resource manifest check. Lookup permission and a server-supplied digest likewise do not establish who authored the bytes.

Provider upload composition may be useful for assembly, but scanning input pieces does not establish safety of their concatenation. For encrypted attachments the provider cannot be assumed to inspect plaintext; endpoints must enforce authenticated resource binding and renderer limits independently.


The [transport adapter contract](../mailbox-integration.md#optional-blob-and-sharing-capabilities) incorporates these extension boundaries alongside the core protocol. This documents the mapping; it does not establish a tested provider implementation.
