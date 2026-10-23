---
title: Encrypted messages over ordinary email
order: 6.05
blurb: standard MLS object · opaque MIME attachment · unchanged SMTP
sectionNav: true
---

# Encrypted messages over ordinary email

An encrypted conversation message travels through ordinary email as one opaque attachment. The actual writing, subject, personal-address record, reply relationships and resources are inside the encryption. An older client can show a short notice; that notice is not a readable copy of the conversation.

> [!ex] The same message, two views
> A compatible client accepts the encrypted contribution and displays its author and writing in the conversation. An older client sees only a generic encrypted-message notice. It cannot obtain the writing from another MIME alternative or an automatically fetched link.

This chapter supplies the proposed ordinary-mail application binding for [mail-conversation-v2](suite-profile.md#asynchronous-protected-agreement). It does not change MLS, introduce another agreement identifier or replace the separate sealed-control carrier. Implementation and real-provider acceptance remain required; earlier opaque-attachment experiments do not implement this binding.

## Encrypt the content before making the email

Construct and validate the complete inner mime-suite-v2 entity under the [selected suite](suite-profile.md#asynchronous-protected-agreement). Encrypt it as MLS application content. The result carried here is one complete serialized RFC9420 `MLSMessage`, including its embedded protocol version and `PrivateMessage` wire-format selector. It is not a bare AEAD ciphertext, a JSON/base64 wrapper around MLS, a concatenation of messages or a sealed-control body.

The MIME label is the registered [message/mls](https://www.iana.org/assignments/media-types/message/mls), defined by [RFC9420 §17.10](https://www.rfc-editor.org/rfc/rfc9420.html#section-17.10). This binding selects encrypted application messages only. A PublicMessage, Welcome, KeyPackage, Commit or proposal does not become an application contribution because it carries that label. Invitations and membership controls retain their independently selected confidential carriers.

Commit the native successor and exact ciphertext together with the non-releasable prepared delivery. Retain the exact final email representation and its envelope under the [handoff](first-contact-setup.md#finish-setup-for-one-intended-send), [mail-version](event-identifiers.md#map-contributions-to-ordinary-mail) and [transport release](transport.md#local-authorization-and-release) contracts. A retry retrieves those bytes; it does not encrypt again or generate another Message-ID.

## The ordinary-email wrapper

The direct-account form contains a generic notice and one encrypted attachment. Relay delivery uses its existing opaque wrapper, as specified separately below. Neither exposes a readable copy of the writing.

::: {.details summary="Direct-account MIME placement and transfer decoding"}

The outgoing message has exactly one `MIME-Version: 1.0` and one top-level `Content-Type: multipart/mixed` with its required boundary parameter. It has exactly two direct children in the following order. No preamble, epilogue, additional part, nested activation candidate or content-bearing top-level transfer encoding is generated.

| Part | Required representation |
| --- | --- |
| Notice | `Content-Type: text/plain; charset=utf-8`, `Content-Transfer-Encoding: 7bit`, no Content-Disposition or Content-ID. Its body is exactly the ASCII text `This message is encrypted.` followed by CRLF. |
| Encrypted object | `Content-Type: message/mls`, `Content-Transfer-Encoding: base64`, `Content-Disposition: attachment`, no filename, Content-ID or other disposition parameter. Its transfer-decoded body is exactly the one serialized MLSMessage. |

Generators omit the optional message/mls `version` parameter. Receivers may accept that registered parameter as a nonauthoritative hint, but the embedded MLS protocol version takes precedence as RFC9420 requires. A hint cannot select a different decoder or override unsupported native version handling. No other parameter is selected on that part. Duplicate singleton MIME fields, ambiguous parameters, missing fields, additional children or malformed multipart framing fail this binding's selection.

Use MIME base64 with canonical alphabet/padding and CRLF line folding at no more than 76 encoded characters per line. Decoders may accept different legal MIME folding; after removing permitted folding whitespace, the encoded data must equal canonical base64 of the complete decoded bytes. Reject invalid alphabet/padding, trailing encoded data and incomplete input. Preserve decoded octets exactly: do not apply text charset conversion, newline normalization or recursive MIME-message parsing to the encrypted object.

[RFC6532 §3.5](https://www.rfc-editor.org/rfc/rfc6532.html#section-3.5) allows newly defined message subtypes to permit non-identity transfer encodings; it does not blanket-permit them for every older subtype. This application binding selects MIME base64 for the binary MLSMessage represented by message/mls. The registration’s binary encoding consideration describes unrestricted content octets, not a requirement to use `Content-Transfer-Encoding: binary`. The selected base64 representation is 7-bit safe without requiring BINARYMIME. It does not waive SMTPUTF8 when an independently selected outer address/header requires it. Bound outer headers, encoded and decoded bodies, MIME depth/parts and total work before allocation; the selected inner-record and native-message limits apply independently. A processing limit yields an explicit limitation, never acceptance of a prefix.

The outer wrapper contains no readable alternative to the protected writing, clear event record, resource, original filename or content-derived notification. A separately authorized ordinary or hosted copy follows [delivery policy](delivery-policy.md); it is not an extra MIME part beside this ciphertext. This short notice is transport explanation, not a text fallback for Email/2 rendering.

:::

## Relay wrapping

A selected relay does not change the encrypted object. It places the same exact MLSMessage bytes inside the already defined opaque relay wrapper. This is a separate, explicit receiving path, not a fallback from a failed direct wrapper.

::: {.details summary="Existing opaque relay layout and application handoff"}

When the selected [provider-issued route](relay-routes.md) uses its retained [opaque-v0 layout](relay-routes-compatibility.md), preserve that layout exactly: its generic `Protected Email/2 delivery.` notice, application/octet-stream attachment and fixed message.bin filename remain unchanged. Do not relabel that attachment message/mls or replace its notice with the direct-account notice. This chapter selects the complete serialized MLSMessage as the opaque application payload; sealed controls retain their own distinct exact binary payload and owning admission path.

The relay adapter validates the complete selected route/account/service scope, exact opaque layout and committed payload bytes under the route contract. It hands those exact decoded MLSMessage bytes to the same application-only native receive boundary below. The direct MIME selector is not applied a second time to that binary object. An application carrier cannot contain a sealed-control frame or request a switch to a control decoder after application parsing fails. A valid route proof does not replace native membership, sender or application validation.

The receiving path must be independently selected under the actual account’s supported transport and routing configuration. An arbitrary application/octet-stream attachment, filename, relay-looking address, incoming capability claim or route-proof candidate cannot select trusted routing or activate application processing. Unknown/missing route evidence retains its owning hold or failure; do not reinterpret the message as direct-account carriage to bypass it.

:::

## Routing headers remain transport evidence

Generate the ordinary required Date, From and Message-ID under the selected account's actual origination authority. Use Subject `Encrypted conversation`. Do not copy the protected subject, author-stated date, personal-address record or content into that subject or notice. The independent opaque Message-ID follows the existing prepared-mail allocator and is retained with exact retries.

The authorized envelope and visible routing projection follow their owning policy. A direct, unmasked send may expose personal routing addresses; it does not claim sender or recipient masking. A fully or partially masked send follows the exact [private-routing projection](private-routing.md#release-with-minimal-outer-metadata), including provider-owned origination, aliases, bounce mapping and omitted fields where required. This MIME layout creates no routing grant and does not permit inventing a relay From.

Do not generate an outer In-Reply-To or References chain for this protected representation. Authenticated reply relationships remain inside the contribution. Do not request an automatic disposition/read response. Receipt of this attachment cannot enable a generic automatic reply, setup exchange, external resource fetch or hidden-message deletion. Outer headers and a provider signature do not authenticate the inner author or establish endpoint readiness.

## Receiving and conversation assembly

The client retains the email, extracts its encrypted object through the selected carrier, then authenticates the actual message before assembling the conversation. The outside cannot choose a trusted author or change group membership.

::: {.details summary="Application-only native receive and durable assembly"}

1. Retain the original received mail and transport evidence. Under finite parser budgets, validate the independently selected direct-account MIME placement or the explicit relay adapter above, and obtain its complete exact MLSMessage bytes. Do not trial another carrier after a selected-path validation failure. A filename, subject or media label alone never enables an interaction or reserves an event identity.
2. Parse exactly one complete MLSMessage without trailing objects. Require the selected native version and PrivateMessage framing. A visible native GroupId is a routing hint into locally held state, not authenticated conversation authority or permission for a network lookup.
3. Use a dedicated application-only durable native receive boundary. Native authentication may identify the encrypted content type, but this path MUST NOT install or retain a proposal, Commit, group epoch/roster change or handshake effect. A PrivateMessage containing non-application content is rejected without those effects; it is not dispatched to a handshake-installation path. A maintained MLS parser may classify authenticated content in isolated provisional state, but that classification cannot commit handshake effects. For an authenticated application message, validate actual membership, sender and epoch, and retain its consumed application receive state and any authenticated application rejection atomically as the owning contract requires. Failure of later application validation cannot justify restoring consumed application receive state or trying another protocol against the same bytes.
4. After native authentication, require application content and the independently selected current agreement/context. Validate the complete inner mime-suite-v2, envelope6, authored0, accepted scope/slot mappings, source identities and resources in their defined order. Missing evidence, unsupported content and malformed content retain their owning distinct outcomes.
5. Only after application acceptance, assemble the contribution using its authenticated identity and relationships. Repeated mailbox copies, alternate legal base64 folding and changed outer headers cannot create another contribution or repeat an interaction. Preserve original source and prior receipt evidence; an outer Message-ID is not an authenticated deduplication key.

An undecryptable, unsupported or incomplete message remains inspectable with its actual reason. It cannot borrow a contact's display identity from an untrusted inner field, disappear as supposedly hidden control traffic, or authorize a plaintext retry. A missing setup path or changed route follows the existing per-recipient uncertainty and delivery policy.

:::

## Acceptance required

Acceptance needs actual maintained MLS encryption, MIME transmission and durable reception, not a base64 round trip alone. Exercise exact-byte retry after restart; equivalent legal folding; truncated, concatenated or wrong-version native objects; PublicMessage/control substitution and a genuine PrivateMessage Commit/proposal through each carrier path, with no epoch/roster/proposal installation; duplicate MIME fields and extra readable parts; malformed base64 and limits; DATA dot transparency and BDAT counted octets; unrelated or misleading outer headers; duplicate delivery after final-ack loss; and failure after native acceptance but before application commitment.

For direct and each supported masking combination, capture actual submission, provider origination and retrieval bytes, including the unchanged opaque-v0 relay wrapper and exact native/application handoff and verify the declared disclosure. A provider that re-encodes MIME must preserve the complete decoded MLSMessage; body or protected-resource changes cannot retain their previous integrity claim. Same-code peers and loopback transport demonstrate only their recorded integration scope. Independent implementations, actual provider carriage and the complete client acceptance journey remain separate evidence.
