---
title: Encrypted messages over ordinary email
order: 6.05
blurb: one opaque attachment · unchanged SMTP · authenticated conversations
sectionNav: true
---

# Encrypted messages over ordinary email

An encrypted conversation travels through existing email as an ordinary binary attachment. The writing, subject, personal-address record, reply relationships and resources are inside its protection. An older client sees a short notice; a compatible client authenticates the protected message and places it in the conversation.

> [!ex] One delivery, two views
> A compatible client displays the accepted author, writing and reply relationships. An older client sees `Protected Email/2 delivery.` and a `message.bin` attachment. The attachment is not a link, and the notice contains no readable copy of the writing.

This chapter binds [mail-conversation-v2](suite-profile.md#asynchronous-protected-agreement) to ordinary mail. It reuses the existing opaque attachment layout and the selected MLS protocol; it introduces no new cryptography or edition of Email/2. Implementation and independent acceptance remain separate requirements.

## Encrypt the complete message

Construct and validate the complete [protected content](suite-profile.md#asynchronous-protected-agreement), including the writing, required HTML presentation and structured relationships, then encrypt it as an MLS application message. The attachment carries that resulting object intact; transport encoding does not change the protected message.

The readable text and required HTML alternatives remain inside MLS. Neither appears beside the encrypted object as a compatibility fallback. A separately authorized ordinary or hosted copy follows [delivery policy](delivery-policy.md); that permission does not add a readable part to this protected copy.

::: {.details summary="Exact MIME layout and transfer decoding"}

The outer attachment contains exactly one complete serialized RFC9420 `MLSMessage`: version 1, `PrivateMessage`, application content. It is not a bare ciphertext, a JSON/base64 wrapper around MLS, several concatenated native objects or a sealed control. Its native protocol version is authoritative; no outer media parameter selects or overrides it.

The generated message has one `MIME-Version: 1.0` field and one top-level `Content-Type: multipart/mixed` with exactly one boundary parameter. It has exactly two direct children in this order:

| Part | Representation |
| --- | --- |
| Notice | `Content-Type: text/plain; charset=utf-8`, `Content-Transfer-Encoding: 7bit`, no Content-Disposition or Content-ID. Its body is exactly the ASCII text `Protected Email/2 delivery.` followed by CRLF. |
| Protected object | Parameter-free `Content-Type: application/octet-stream`, `Content-Transfer-Encoding: base64`, and `Content-Disposition: attachment; filename="message.bin"`. No Content-ID or other disposition parameter is permitted. Its transfer-decoded body is the complete MLSMessage. |

These are the only part headers. The root has no Content-Transfer-Encoding. Preamble and epilogue are empty apart from MIME separator line breaks. Additional children, nested multipart objects, duplicate singleton fields, ambiguous parameters, forwarded messages and external-body references fail this selection. The fixed filename is transport metadata, not an original filename, file-system path or permission to open an attachment automatically.

Use canonical MIME base64 alphabet and padding, with CRLF folding at no more than 76 encoded characters per line. A receiver may accept different legal MIME folding; after removing permitted folding whitespace, the encoded data must equal canonical base64 of all decoded bytes. Reject invalid alphabet/padding, nonzero unused bits, trailing encoded data and incomplete input. Do not apply character-set conversion, newline normalization or recursive message parsing to the protected object.

Bound original mail, header blocks, physical header lines, direct parts, encoded/decoded attachment bytes and native-message work before their corresponding allocations or processing. Apply the selected inner-envelope and authored-record bounds independently after native authentication. Processing exhaustion is an explicit incomplete outcome, never acceptance of a prefix or permission for a clear replacement.

The outer object uses the existing [application/octet-stream type](https://www.rfc-editor.org/rfc/rfc2046.html#section-4.5.1). It does not use `message/mls` with base64. [RFC6532 §3.5](https://www.rfc-editor.org/rfc/rfc6532.html#section-3.5) allows newly defined message subtypes to permit transfer encoding; this is not blanket permission for every subtype. The [registered MLS type](https://www.rfc-editor.org/rfc/rfc9420.html#section-17.10) describes binary content but does not explicitly select email base64. This baseline avoids depending on that additional permission or on existing gateways understanding a new message subtype. An alternative `message/mls` binding needs its own resolved encoding and interoperability contract; it is not a fallback decoder here.

The selected attachment is seven-bit safe for ordinary SMTP DATA. BINARYMIME is not required. Actual internationalized envelope addresses or outer headers retain their independent SMTPUTF8 requirements; attachment encoding cannot remove them.

:::

## Keep routing separate from the attachment

A direct-account send uses the person's selected sending account. Sender or recipient masking additionally requires its own eligible service and route. Reusing one MIME layout does not grant those permissions.

::: {.details summary="Account origination, relay handoff and exact retries"}

Generate the required Date, From and Message-ID under the account's actual origination authority. Use Subject `Encrypted conversation`. Do not copy the protected subject, author-stated date, personal-address record or writing into that subject or notice. The independent opaque Message-ID follows the [prepared-mail allocator](event-identifiers.md#map-contributions-to-ordinary-mail): reserve it durably with its mail version, handle local collisions, and retain it across attempts.

For this protected representation, generate no outer In-Reply-To or References chain and request no automatic disposition/read response. Authenticated reply relationships remain inside the contribution. Outer fields and a provider signature are transport evidence; neither authenticates the inner author or establishes endpoint readiness.

For direct unmasked delivery, personal routing addresses can remain visible. That send does not claim address masking. A masked send follows [private routing](private-routing.md#release-with-minimal-outer-metadata), including provider-owned origination, aliases, bounce mapping and field omission where required. A client cannot invent a relay From or gain authority over another operator's domain.

A relay uses its existing [opaque extraction layout](relay-routes.md#relay-mime-extraction) unchanged. Its payload commitment covers the exact complete MLSMessage bytes. The relay owner checks its actual route, account, service and intended scope before handing those bytes to application reception. A structural MIME parser or a route-looking address cannot perform those checks. This chapter selects neither a new route-issuance permission nor per-alias device approval.

Direct-account and relay reception are explicitly selected owning paths. The direct path does not require a relay proof merely because the layouts match; the relay path cannot omit its proof or retry the direct path after failed route validation. An arbitrary octet-stream attachment, filename or incoming capability claim selects no trusted route, identity or interaction.

Retain the native successor, exact ciphertext and non-releasable prepared delivery atomically. Retain the complete final mail and authorized envelope under the [transport release contract](transport.md#local-authorization-and-release). A retry retrieves those bytes; it must not encrypt again or generate another Message-ID. A deliberately changed wrapper, protection projection or outer origination is a newly authorized mail version under the [mail-version rules](event-identifiers.md#map-contributions-to-ordinary-mail), not an edit to an old uncertain attempt. Earlier possible disclosure and transport outcomes remain retained.

:::

## Authenticate before assembling the conversation

The receiver preserves the mail, extracts the complete protected object through its selected path, then authenticates the actual application. The outside cannot choose a trusted author, conversation or membership change.

::: {.details summary="Application-only native reception and durable acceptance"}

1. Retain the original received mail and actual transport observations. Under finite parser budgets, validate the complete selected MIME layout and obtain its exact decoded MLSMessage bytes. After a selected-path failure, do not try another carrier or control protocol. A filename, subject or media label grants no effect or namespace reservation.
2. Parse one complete native message without trailing objects. Require the selected protocol version and PrivateMessage application framing. A visible GroupId or epoch is only a hint into independently held state, not conversation authority or permission for a network lookup.
3. Use a dedicated application-only native receive boundary. It MUST NOT install or retain a proposal, Commit, epoch/roster change or other handshake effect. A maintained implementation may classify authenticated content in isolated provisional state, but this path cannot commit non-application effects. An altered visible content-type hint cannot excuse native authentication.
4. For authenticated application content, require the independently accepted epoch context and current agreement. Validate complete inner mime-suite-v2, exact envelope6/authored0, actual native sender/audience, accepted scope/slot mappings, core relationships and resource roles in their defined order. Do not infer those bindings from an outer header or a caller's verified flag.
5. Atomically retain consumed native application receive state and its accepted, rejected or pending application outcome. Later application failure cannot restore consumed receive state or authorize another protocol attempt against those bytes. Missing source, unsupported content, malformed content and processing exhaustion retain their owning distinct outcomes.
6. Assemble only from admitted contribution identity and relationships. Repeated copies, legal transfer-folding changes or different outer headers cannot create another contribution or repeat an interaction. Preserve actual originals and prior source/outcome evidence. An outer Message-ID is not an authenticated deduplication key.

An undecryptable or incomplete message remains inspectable under its actual reason. It cannot borrow a contact's identity from an untrusted field, disappear as supposedly hidden control traffic, activate a setup exchange or authorize an automatic clear retry. Mailbox arrival, native acceptance, application acceptance and human reading remain separate states.

:::

## Present the protection of the actual copy

The fixed outer notice is untrusted transport explanation. A compatible client derives the conversation view and its protection status from the accepted inner application, never by joining that notice to the protected writing as a second message body.

The [security profile](security-profile.md#relationship-to-encrypted-email-guidance) explains how MLS supplies authentication inside encryption and protects semantic presentation fields without claiming PGP/MIME, S/MIME or RFC9788 wire compatibility. The deliberate departure from [RFC9787 §3.2](https://www.rfc-editor.org/rfc/rfc9787.html#section-3.2) for separately authorized mixed-protection copies belongs to the [mixed-delivery policy](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status). Successful decryption of this copy cannot imply that every other delivery was encrypted or undo an authorized disclosure elsewhere.

Earlier explicitly selected experimental carriers retain their original bytes, identities, uncertainty and recorded scope. A software update or familiar native context does not relabel those experiments as current acceptance evidence. Retained legacy encrypted-mail profiles keep their own composition and decoder rules; neither is an automatic fallback from this binding.

## Acceptance required

Exercise actual maintained MLS encryption, MIME transmission and durable application reception: exact retry after restart; legal transfer-folding equivalence; truncated, concatenated, wrong-version and non-application native objects; genuine encrypted Commit/proposal substitution without handshake installation; duplicate MIME fields and additional readable parts; malformed base64 and processing limits; DATA dot transparency and BDAT counted octets; unrelated outer fields; final-ack loss and repeated mailbox delivery; Message-ID collision/storage failure; and failure after native authentication before application commitment.

For direct and each offered masking combination, capture the real submission, provider origination and retrieval bytes. Verify the declared disclosure and exact native/application handoff. Re-encoding may preserve the complete decoded object; replacing protected bytes cannot preserve its integrity claim. Same-code peers and controlled transport prove only their recorded scope. Independent implementations, real-provider carriage, the required HTML/CSS presentation and the complete current-client journey remain separate acceptance obligations.
