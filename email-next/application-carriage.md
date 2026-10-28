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

Before sending, obtain each selected device's signed promise that it can receive this attachment format. A familiar encryption key or inner conversation format is insufficient. The [receiving bundle](#obtain-authenticated-carrier-support) carries that promise with the device's original setup, including through private first-contact discovery. Other recipients may stay pending while an independently ready delivery proceeds.

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

A pending application outcome is already authenticated native consumption. If native processing completed within the original receiving window and that consumption and pending outcome were durably retained, later application admission does not acquire a new decoder lease or decrypt the ciphertext again. It may finish after that receiving window expires, while independently rechecking current account, identity, role, scope and application authority. Publication expiry or withdrawal does not retroactively invalidate timely retained native consumption. A native processing attempt that crosses its receiving or epoch-retention deadline retains the consumed successor under a non-admitted outcome; it cannot use the pending-outcome rule to admit late decryption.

The selected own mailbox is also an application binding. For a protected recipient, compare it with that recipient's actual per-message slot/address mapping; for an own-sender copy, compare it with the protected author/from mapping. An old scope invitation, outer address or another alias of the same authenticated principal/device cannot substitute for current support and authority for the selected account. Retain the original reader provenance for each physical carrier, separately from any earlier acceptance of the same native object through another explicit profile.

An undecryptable or incomplete message remains inspectable under its actual reason. It cannot borrow a contact's identity from an untrusted field, disappear as supposedly hidden control traffic, activate a setup exchange or authorize an automatic clear retry. Mailbox arrival, native acceptance, application acceptance and human reading remain separate states.

:::

## Present the protection of the actual copy

The fixed outer notice is untrusted transport explanation. A compatible client derives the conversation view and its protection status from the accepted inner application, never by joining that notice to the protected writing as a second message body.

The [security profile](security-profile.md#relationship-to-encrypted-email-guidance) explains how MLS supplies authentication inside encryption and protects semantic presentation fields without claiming PGP/MIME, S/MIME or RFC9788 wire compatibility. The deliberate departure from [RFC9787 §3.2](https://www.rfc-editor.org/rfc/rfc9787.html#section-3.2) for separately authorized mixed-protection copies belongs to the [mixed-delivery policy](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status). Successful decryption of this copy cannot imply that every other delivery was encrypted or undo an authorized disclosure elsewhere.

Earlier explicitly selected experimental carriers retain their original bytes, identities, uncertainty and recorded scope. A software update or familiar native context does not relabel those experiments as current acceptance evidence. Retained legacy encrypted-mail profiles keep their own composition and decoder rules; neither is an automatic fallback from this binding.

## Acceptance required

Exercise actual maintained MLS encryption, MIME transmission and durable application reception: exact retry after restart; legal transfer-folding equivalence; truncated, concatenated, wrong-version and non-application native objects; genuine encrypted Commit/proposal substitution without handshake installation; duplicate MIME fields and additional readable parts; malformed base64 and processing limits; DATA dot transparency and BDAT counted octets; unrelated outer fields; final-ack loss and repeated mailbox delivery; Message-ID collision/storage failure; and failure after native authentication before application commitment.

For direct and each offered masking combination, capture the real submission, provider origination and retrieval bytes. Verify the declared disclosure and exact native/application handoff. Re-encoding may preserve the complete decoded object; replacing protected bytes cannot preserve its integrity claim. Same-code peers and controlled transport prove only their recorded scope. Independent implementations, real-provider carriage, the required HTML/CSS presentation and the complete current-client journey remain separate acceptance obligations.

## Obtain authenticated carrier support

Alice need not send Bob a readable first message to learn this format. An authorized provider exchange or private directory can return Bob's signed setup and attachment support together. Her client checks both, obtains any real one-use package, and only then prepares the encrypted message. A service cannot announce software support for Bob's device on his behalf.

These records add a transport capability to the existing native agreement. They do not change assertion10, context10, authored0/envelope6, mime-suite-v2 or native admission. An old offer, including the earlier direct-account experiment, does not promise this format.

::: {.details summary="Device-signed carriage-offer0 and receiving-bundle0"}

### Device receiving promise

The strict UTF-8 carriage-offer0 payload has exactly these members. Apply the existing strict JSON, original-byte signature, identifier and canonical time rules. No number, null, unknown or duplicate member is admitted.

| Member | Required value |
| --- | --- |
| `version`, `purpose` | Strings `"0"`, `"application-carriage-offer"`. |
| `record` | Fresh nonzero ObjectId, retained for exact retries. |
| `advertisement` | Canonical padded base64 of one complete original assertion10 wrapper, including its independent signature and identity evidence. |
| `carriages` | Exactly `["opaque-mls-application-v0"]`. This names the application MIME binding in this chapter. |
| `controls` | Either `[]` or exactly `["sealed-control-v3"]`, the separately selected mailbox-response binding below. |
| `notBefore`, `notAfter` | Canonical uint64 decimal Unix-second strings; start inclusive, end exclusive, with notBefore strictly less than notAfter. |
| `receiveUntil` | Canonical uint64 receiving deadline, no earlier than notAfter. |

The wrapper is exactly `{payload,signature}`: canonical padded base64 original payload bytes and lowercase hex of 64 Ed25519 signature octets. Signature input is ASCII `mail/application-carriage-offer/v0`, NUL, U32BE original payload length and those original bytes. Use the independently authenticated device key from the embedded assertion; an incoming identity bundle cannot appoint its own trust anchor.

Validate the embedded assertion under its complete original grammar/domain, identity/Receive authority and independently established canonical mailbox/account association. The offer signer is that same authenticated device and binding, not its provider or another administrator. Retain both original records and their distinct identity-state ancestry. A new state digest alone proves neither continuous authority nor software support.

The whole offer publication interval fits the embedded assertion and its issuer's accepted receiving authority. For an offered sealed3 response, it also fits the exact embedded controlKey's publication interval, and receiveUntil cannot exceed that key's original receiveUntil. An offer cannot extend a native package, control key, epoch or retired identity. Those owning bounds and safety stops remain independently required.

Before publication, durably retain the locally issued original offer, actual supported receiving implementation, its assertion/key ownership and receiving promise. Keep the selected reader and applicable receiving material through receiveUntil under their owning lifecycle. Publication expiry stops new selection/release; it does not alone erase a retained receiving promise. Accepted key withdrawal, retirement or identity/role barriers retain their independent effect; no offer revives retired keys.

Offer identity is `(authenticated principal, authenticated device, record)`. Equal original payload bytes are duplicates. Independently authenticated unequal payloads under that identity conflict; arrival order chooses no winner. Invalid candidates cannot reserve it. Other offer IDs do not silently replace previously retained evidence or extend its deadlines.

### Complete receiving bundle

Receiving-bundle0 is exactly the object below. The bundle adds no service signature or new identity authority.

| Member | Required value |
| --- | --- |
| `version`, `purpose` | Strings `"0"`, `"application-receiving-bundle"`. |
| `advertisement` | Canonical padded base64 of the actual complete original assertion10 selected for acquisition/admission. |
| `carriage` | Canonical padded base64 of one complete original carriage-offer0 wrapper. |

Normally the offer's embedded advertisement is byte-identical to the bundle's advertisement. The only other permitted relation is the [exact offline package join](#join-an-offline-package-with-its-support-proof). Merely matching fields, addresses or device names is insufficient.

The containing acquisition record commits the complete original bundle bytes. Decode each layer canonically and check its existing owning byte/depth ceilings before allocation. Encoded original records count toward every enclosing aggregate limit. A complete combination must fit all those bounds; no maximum-sized child earns an exemption. Report incomplete or unsupported size rather than truncate a proof, accept a prefix or follow a spillover URL.

:::

::: {.details summary="Exact offline allocation join and current release checks"}

### Join an offline package with its support proof

A private directory publishes package-free static setup. A separately authorized [package allocator](package-allocation.md#install-the-static-assertion) can later provide one real package without requiring a new software-support signature for every package. Perform all of these checks; equality of a capability projection is only one of them.

1. Retain the exact complete static assertion10 wrapper embedded in the signed offer. Compute its original **payload** digest and require the independently validated static installation/authorization namespace and that exact digest. Do not confuse it with the digest of the wrapper or a reserialization.
2. Validate the original signed package-publication payload and exact original publication request bytes. Its staticAssertionDigest names that same static payload. Its advertisementDigest hashes the actual package-bearing assertion's original payload. Validate the original device signature, actual authorization, account/incarnation/link, original intervals and current accepted state under the allocator owner.
3. Validate the original signed allocation result for the locally retained exact request. requestDigest names that original request payload; authorizationDigest and staticAssertionDigest match its original selection. For state allocated, publication/publicationDigest name the exact selected publication ID and original publication payload. packageReference equals both that publication and the maintained implementation's reference for the genuine native package.
4. Canonically decode publicationBundle and require the exact complete original package-publication request bytes, including its record, advertisement and identity. Its record/payload/digests and actual package-bearing advertisement must be the same objects validated above. A copied response, a result alone or independently similar advertisement cannot fill a missing request/publication dependency. Depleted, missing, canceled, uncertain or expired outcomes supply no package.
5. Apply the existing allocator's full static/package projection and interval rules. The actual package-bearing assertion and offer's embedded static assertion resolve to the same authenticated principal/device/binding and current Receive authority through independently accepted continuous ancestry. Their mailbox, features, applications, orderingExchanges and public controlKey match exactly as that owner requires; the package-bearing interval is contained in the static interval. Distinct signed record IDs and original state anchors remain distinct. Validate actual package cryptography, private custody/allocation promises and consumed/withdrawn state independently.

Only after that complete join may the receiving bundle pair the actual allocated advertisement with the retained original carriage offer. Constructing this local bundle creates no allocation, new signature, membership or fresh timestamp. Retain the exact request/result/publication/static/offer evidence and current validation together with the owning acquisition outcome. Existing allocator0 schemas and signatures remain unchanged.

### Select one actual delivery

For every actual target device, including participating sender devices, select a valid original bundle for the actual chosen mailbox/account namespace and complete native application/ordering. Check independent signature, current identity/Receive authority, association, credible time, publication bounds, package/allocation and required control support. Do not infer account-wide support, substitute another alias/device or silently drop a frozen target. Pending intended slots remain outside a ready actual cohort under the existing progression policy.

Freeze that exact evidence with the local intent revision, native cohort, selected carrier and mail version. Before native admission and final content release, repeat all current owning checks. A projection computes no release and grants no credentials. A successful provider response or parser is not readiness. Missing, conflicted, expired or old-carrier-only evidence remains unknown/held; it neither proves lack of encryption nor authorizes ordinary delivery.

On delayed receipt, enforce the retained original receiveUntil and independently applicable native/key receiving rules separately from publication/release eligibility. Retain exact own issuance/custody evidence. A sender-stated creation time is not a trusted historical timestamp. Arrival after expiry may remain unresolved; it cannot renew keys, regenerate setup, trigger a clear resend or borrow another offer.

For decoder eligibility, the receiver resolves an actual locally issued, durably retained promise for its exact account/device and this profile. Check that original promise through receiveUntil, plus independent current identity/role and native epoch/key checks. If several same-profile local promises are eligible, any may establish decoder eligibility; retain the exact one selected with the receipt. This cannot extend retired keys/roles or authorize membership.

There is no wire offer ID in the opaque application frame. The receiver does not claim to recover or verify the sender-selected offer or its creation time. The sender separately retains its exact preparation/release dependency. MIME, native version and familiar context alone cannot supply a missing local promise. A new genuine local promise is not a rewrite of an earlier promise or evidence of historical sender behavior.

:::

## Acquire support without exposing the private address

The complete paths are [provider3](provider-control.md#obtain-complete-mail-receiving-evidence), [bootstrap3](bootstrap.md#first-message-setup-with-carrier-support), [private snapshot1](private-snapshot.md#private-acquisition-with-carrier-support) with actual allocation, and separately enabled [mailbox setup3](mailbox-setup.md#set-up-the-opaque-application-carrier). They carry the complete original bundle, not a supported boolean or an address-specific URL to fetch later. Existing native admission extracts and validates the actual original assertion10; it separately retains the mandatory carrier proof.

Ordinary and protected publication follow [their exact placement rules](passive-discovery.md#publish-complete-mail-receiving-support). A real-address-bearing offer must stay inside the selected protected/private payload when Identity Protection or an opaque route is required. Add no clear sibling to this chapter's strict two-part frame and no personal address, address digest or private proof to its outside headers/notice. A provider/private directory does not gain permission to publish a plaintext recipient-registration map.

## Refresh a device without rewriting old mail

A device publishes a new original promise only after it actually implements the selected receiving profile and has current independent authority. An update on Alice's device cannot manufacture Bob's promise. Refresh through the same exact acquisition paths; offline evidence remains offline evidence, and a fresh response never extends an earlier promise's deadlines.

An existing group need not change native context merely to refresh transport support. Its actual membership, source, scope and current authority still validate independently. New devices require real native admission. Own-device setup can transfer its originally defined records, but old configuration data does not acquire a missing carriage proof: reacquire it under current policy before releasing new mail.

::: {.details summary="Historical prepared versions and explicit reader selection"}

### Historical prepared versions and explicit reader selection

Prepared historical mail, including the earlier direct-account experiment, keeps its exact complete bytes, Message-ID, ciphertext, native state, selected recipients, attempts and uncertainty. A software update cannot rewrap it, relabel its evidence or silently replace an uncertain attempt. A new deliberately authorized mail version follows the original mail-version/disclosure contract and retains earlier exposure; it is not an in-place migration.

Persist selected carrier provenance with every new preparation. Migrate a known old stored schema only to its actual historical owner; unknown or ambiguous restored provenance remains unresolved. A familiar context10 or inner mime-suite-v2 does not identify an outer carrier. Never manufacture a new support offer from old advertisement fields.

Reception uses an independently retained local receiving promise/source policy to permit a profile. A bounded MIME classifier may select a candidate parser, but untrusted content-type, filename or notice supplies no authority. Validate that one explicit profile completely; failed current application input cannot fall through to historical, relay or control decoding. Retain historical readers under their actual original promises and labels without treating them as current interoperability evidence.

:::

## Accept the complete acquisition journey

Exercise first-message provider3 and offline bootstrap3 without earlier human mail; private snapshot1 plus actual allocator0; actual authenticated mailbox3 request and sealed3 response; ordinary introduction and protected-attachment refresh; and current support refresh in an existing actual group. Capture per-device original signatures, all target-device choices, exact package join, current identity/account/role and each receiving promise.

Reject crossed device/binding/account/alias, substituted original assertion, wrapper/payload digest confusion, altered publicationBundle, wrong actual package reference, old result in a fresh request, partial evidence, conflicting offers, stale publication, retired keys and missing receiving custody. Preserve old94 prepared bytes and uncertain outcomes across restart; no automatic fallback or re-authoring. Actual end-to-end implementations and independent acceptance remain required, including masked routing with no real-address-bearing clear metadata.
