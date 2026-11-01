---
title: Delivering deletion requests
order: 12.6
blurb: advertised support · dedicated receiving keys · encrypted requests · silent handling
sectionNav: true
---

# Delivering deletion requests

A deletion request asks a recipient's system to remove one message. It does not
replace that message with new content, cancel someone's reply or prove that
anyone forgot what they read. The [delivery policy](delivery-policy.md#deletion-requests-and-local-deletion)
defines the sender's local marker and the recipient's silent removal policy.
This chapter defines how compatible devices exchange the request securely.

The exchange has three steps:

1. During an otherwise authorized message exchange, a receiving device can
   advertise a dedicated, expiring key for deletion requests.
2. When the author requests deletion, their device encrypts a signed request
   for each eligible recipient device. The request identifies the exact original
   message and its bytes; an address or subject is insufficient.
3. The recipient's system checks the author, original message, scope and local
   policy. If it honors the request, it removes the message silently and retains
   enough safety state to stop a late copy from bringing it back.

Receiving an advertisement does not start an exchange or send a response. Sending
a request supplies no deletion receipt. A missing advertisement leaves remote
deletion unavailable for that device; it does not prevent an ordinary message,
authorize a readable deletion command or change the sender's local marker into
a claim of remote success.

> [!ex] Support learned during an ordinary exchange
> Bob's device includes its signed deletion-support offer when he replies to
> Alice. Later, Alice asks to delete one of her own messages. Her device uses
> Bob's still-eligible offer to encrypt the request. Bob's system may honor it
> silently. Alice sees her own local marker, without learning Bob's decision.

> [!warn] Draft protocol and implementation boundary
> The formats below are proposed bindings within this specification, not
> registered names or evidence of deployed support. A request-record parser is
> not a complete implementation. Support requires the receiving offer, dedicated
> key custody, protected carrier, accepted-authority checks and durable recipient
> transactions together. Independent implementation and security review remain
> separate requirements.

## Advertise support without sending control-only mail

A device advertises only support it actually implements. The offer names that
device, one of its authorized personal mailboxes and a fresh key dedicated to
this module. It does not promise that every client connected to the mailbox
supports deletion. A mailbox provider, discovery index or forwarding alias cannot
make the offer on the device's behalf.

The offer may accompany an independently authorized human message under the
publication and disclosure policy. It MUST NOT cause a separate automatic email,
probe, acknowledgement, URL fetch or answer to another offer. Its acquisition
does not extend the original human-send deadline.

:::: {.details summary="Receiving-offer schema, original signatures and key custody"}

### Signed receiving-offer0

The payload is one strict UTF-8 JSON object with exactly eight required members.
Apply the existing duplicate-name, Unicode, scalar and unknown-member rules.
There are no JSON numbers or null values.

| Member | Required value |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"deletion-receiving-offer"`. |
| `record` | Fresh nonzero ObjectId, retained for exact retries. |
| `actor` | Exactly `principal`, `device`, `state`, `binding`, using the existing actor-claim grammars. |
| `mailbox` | One canonical personal address under the [mailbox-address contract](mailbox-addresses.md), independently authorized for this actor. |
| `key` | Exactly `id`, `publicKey`, `receiveUntil`, defined below. |
| `notBefore` | Canonical uint64 decimal string, inclusive publication start. |
| `notAfter` | Canonical uint64 decimal string, exclusive publication end, greater than notBefore. |

Key `id` is a fresh random nonzero ObjectId; `publicKey` is the canonical
32-octet X25519 public key in lowercase hex; `receiveUntil` is a canonical uint64
decimal string no earlier than notAfter. The publication interval must fit the
issuer's accepted device binding at issuance. Validate X25519 through the
selected HPKE implementation, including rejection of invalid or all-zero
shared-secret inputs; do not repair noncanonical public keys.

The signed wrapper has exactly `payload` and `signature`: canonical padded
base64 original payload octets and lowercase hex of exactly64 Ed25519 signature
octets. Sign ASCII `mail/deletion-receiving/v0`, NUL, U32 big-endian original
payload length, then the original payload. Apply the existing strict application
signature checks using the independently accepted device key. Payload and wrapper
bounds are respectively 1,048,576 and 4,194,304 octets; each has maximum container
depth32. Check encoded length before decoding, and decoded bounds before building
a tree. These reuse the request-record allowances, not storage quotas.

Retain the exact signed wrapper and original payload. The offer identity is
`(actor principal, actor device, record)`. Equal authenticated original payload
bytes are duplicates; different independently authenticated payload bytes under
that identity conflict. Neither arrival order nor reserialization selects a
winner. Invalid candidates cannot occupy the identity. Conflicted offers are
unusable for a new preparation pending the owning safety resolution.

### Separate the key from conversation and backup keys

Generate independent material and a fresh ID. Do not reuse an assertion's
control key, MLS key, signing key, route key, pairing key or archive key. The
receiving offer promises only the sealed-deletion-v0 profile below. Conversely,
an assertion10 control key does not promise this profile. Keep IDs unambiguous
across the device's retained control-key inventory; a collision holds affected
publication and input instead of trying several keys.

Before publication, verify possession through the selected local cryptographic
store and durably retain the original offer, key ownership and private-key
custody. Apply the [control-key lifetime policy](suite-profile.md#confidential-setup-and-control)
to selecting configurable publication and receiving periods. This module adds
no fixed rotation frequency. Retain the original receiving promise through
receiveUntil unless explicitly withdrawn or retired under accepted lifecycle
policy; restart enforces the original dates. Renewal uses new material and a
new offer. Republishing an existing key never extends its original deadlines.

A signature does not establish mailbox ownership, accepted identity or current
Receive authority. The observer must independently accept those facts under the
existing association, lifecycle, continuity and first-contact policy. The actual
publisher needs Send authority for the human message and permission to disclose
the offer to its audience. Observation alone installs no identity, device,
account, namespace reservation or receiving secret.

An own-device configuration or archive import does not enroll this key. Existing
configuration3 advertisement inventories remain unchanged; they cannot silently
carry a new offer type or live secret. An implementation may reacquire a foreign
offer through the carriers below or retain it in protected local state. Missing
material holds only this optional operation, not baseline conversation delivery.

::::

:::: {.details summary="Exact offer placement in ordinary and protected messages"}

### Ordinary message metadata

The proposed parameter-free media type is
`application/vnd.threadlabs.mail-deletion-offer+json`. A sending client may append
one direct child after the readable body of the outer `multipart/mixed`, using
base64 transfer encoding and attachment disposition with advisory filename
`mail-deletion-offer.json`. Apply the [passive-discovery MIME rules](passive-discovery.md#sending-and-recognizing-an-advertisement)
for unambiguous headers, MIME-Version1.0, 76-column base64, strict transfer
decoding and direct-child scanning. This is a separate metadata child, not an
extra field in the discovery wrapper or an alternative rendering of the prose.

At most one direct child of this type is a candidate. Multiple such children
leave offer acquisition inactive for that message without erasing prior evidence
or blocking readable mail. Do not activate nested forwarded messages, archives,
related resources, quoted HTML or filenames that merely resemble the offer.
Require the sole parsed From mailbox to match the signed mailbox before treating
it as a first-contact association candidate. That match still does not prove
ownership or authenticate the surrounding email.

Publication is deliberate under the ordinary-mail disclosure policy: the offer
reveals its address and device relationship. Never move a private offer outside
encryption to make this placement fit. A legacy client may show an attachment;
this specification cannot make it discard the part. A newly composed forward
should omit the locally generated offer and may publish the forwarder's own
eligible offer. Other clients can copy the original bytes; copying does not
transfer its authority.

### Protected message attachment

The same original signed wrapper may be an independent attachment in an otherwise
authorized attachment-message, rich-message or reply-message. The original
authored operation must commit the resource's exact length and digest and its
attachment description must carry the exact proposed media type. The selected
mime-suite-v2 compound object must contain those bytes under that operation's
resource identity, within the same protected boundary. Do not add a hidden
unlisted part, unknown operation member or extra envelope6 alternative.

Only a fully accepted human message can supply this acquisition path. The offer
actor must be its actual publishing principal/device; its mailbox must have the
required accepted association. The signed offer state need not equal the latest
head when the existing purpose-specific unchanged-key/role continuity is valid.
At most one independent attachment with this authenticated media type is an
offer candidate; multiple candidates leave this acquisition inactive without
invalidating the human message or discarding earlier accepted evidence.
Unknown resources remain ordinary opaque attachments. A receiver that lacks this
module does not activate the offer by sniffing its bytes. A plain message has no
attachment resources; a generator needing this path selects a valid attachment
operation before freezing authored bytes.

Receiving a valid offer is read-only capability observation, not a human-message
effect. No automatic response, fetch or key allocation follows. The new metadata
is subject to the same original audience and disclosure constraints as its
human message. An ordinary projection cannot silently export private claims.
If disclosure of the committed offer is not authorized, hold that projection
or compose a separately authorized human message without it, under a fresh
authored identity and the existing delivery rules. Do not remove a committed
resource while claiming the same authored record or silently drop another
authored attachment. Prefer choosing the permitted attachment inventory before
freezing the original authored bytes.

No additional Directory, provider or setup HTTP endpoint is selected here.
Those services cannot widen their closed schemas to insert an offer. A copied
or cached candidate is usable only after the same current independent checks;
a public boolean such as “supports encryption” cannot substitute for it.

::::

## Request removal of one exact message

This binding targets accepted authored0 records under the current asynchronous
agreement. It does not assign authored identities to legacy email, reinterpret
an older envelope as authored0 or infer a native target from Message-ID. Legacy
service recall remains a separately authenticated adapter capability.

The original author can issue a request from a currently authorized device of
the same principal. The system selects only recipients within the original
message's authorized scope. It does not take every current group member or
every person in the account's address book.

The request carries no quoted body or replacement prose. Its exact signed record
is defined below. The encrypted carrier binds that original record to a selected
recipient device and the exact offer used to reach it.

::: {.details summary="Signed deletion-request0: exact message, author and scope"}

The request payload is a strict UTF-8 JSON object with exactly these nine members.
The existing duplicate-name, Unicode, unknown-member and scalar restrictions
apply. The payload is at most 1,048,576 octets with container depth at most32.
These reuse the authored-record processing allowance; they are not storage quotas.

| Member | Required value |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"deletion-request"`. |
| `record` | Fresh nonzero ObjectId for this device's request; exact retries retain it. |
| `actor` | Exact four-member object: `principal`, `device`, `state`, `binding`. |
| `target` | Complete logical authored reference: `principal`, `conversation`, `event`. Never a delivery identifier. |
| `targetDigest` | Lowercase SHA-256 hex digest of the complete original authored UTF-8 octets. |
| `scope` | Complete logical reference to that original contribution's scope root. |
| `notBefore` | Canonical uint64 decimal string of the inclusive acceptance start. |
| `notAfter` | Canonical uint64 decimal string of the exclusive acceptance end, greater than notBefore. |

Actor principal/device use the existing `enp0`/`end0` grammars. State and binding
are lowercase 32-octet hex digests naming the original claimed identity state and
device binding; they supply no trust anchor. Target principal MUST equal actor
principal. Scope and target MUST name the same conversation; the scope creator
need not be the target author. A matching personal mailbox is not a substitute
for any of these bindings.

The signed wrapper has exactly `payload` and `signature`. Payload is canonical
padded base64 of the complete original payload octets; signature is lowercase hex
of exactly64 Ed25519 signature octets. The wrapper is at most 4,194,304 octets,
reusing the sealed-control body allowance, with container depth at most32. Check
encoded payload length before allocating decoded bytes, then enforce its decoded
bound and complete strict schema. No null, numeric JSON values, extra members,
partial payload, alternate alphabet or noncanonical padding is accepted. Keep
original wrapper and payload bytes; reserialization is not a retry.

Sign ASCII `mail/deletion-request/v0`, one NUL octet, the unsigned U32 big-endian
original payload length, then those exact original payload octets. Apply the
existing [strict application-signature rules](security-profile.md) under the
actor's independently accepted device key. The supplied signature key is not
selected by the payload or its digests. A valid signature alone does not supply
current Send authority, an original message, accepted scope, actual recipient
membership, negotiated support or permission to disclose the request.

Before any effect, the recipient's system independently obtains the accepted
original authored record and compares its full reference, complete-byte digest
and exact scope root. Eligible targets are message, attachment-message,
rich-message, reply-message, question, service-question, answer, edit and
hosted-holder-observation. A reaction, withdrawal, recipient-resolution or another
protocol control is not a human-message deletion target. This operation neither
withdraws an answer nor reverses an external service effect. Apply the existing
rules for retained independent replies and quotations.

Missing original evidence remains pending. A conflicting or invalid target does
not become eligible by matching one claimed digest. Preserve all independently
authenticated conflict evidence. An already honored disposition is not undone by
later conflict discovery or by expiry of this request. For first acceptance,
the entire credible current interval must fit within `[notBefore, notAfter)`;
checking the claimed timestamp alone is insufficient.

Retain request identity as `(actor principal, actor device, record)` with its
exact original signed payload. Equal original signed payload bytes under that
identity have one request effect, even if a protected carrier is independently
re-encrypted. Different independently authenticated payload bytes under that
identity are a request conflict; do not choose by arrival order. Invalid or
unauthenticated candidates cannot reserve that identity. Another authorized
device can issue its own fresh request for the same original target; it cannot
reuse the first device's request identity. Multiple valid requests do not create
multiple visible removals or acknowledgements.

The protected delivery below binds this exact request to independently advertised
receiving support. This record alone is neither an authored0 operation nor a new
sealed-control-v2 kind.

:::

## Encrypt and retain the exact delivery

:::: {.details summary="Sealed-deletion-v0: framing, signed intent and release"}

This is a separate optional control profile under
`application/vnd.threadlabs.mail-control`, without parameters. It does not add an
authored0 operation, an assertion10 interaction or a sealed-control-v2 kind.
Existing context10, envelope6, assertion10 and the twelve contribution-operation
vocabulary remain unchanged. A generic mail-control media label supplies no
profile selection or receiving permission.

Reuse the [sealed-control construction](suite-profile.md#confidential-setup-and-control)
only with these exact replacements:

| Component | Sealed-deletion-v0 value |
| --- | --- |
| Outer eight-octet magic | ASCII `MAILDEL0`. |
| Encrypted-frame eight-octet magic | ASCII `MAILDCI0`. |
| HPKE info domain | ASCII `mail/deletion-control/v0`. |
| Intent signature domain | ASCII `mail/deletion-control-intent/v0`. |
| Intent version / purpose | `"0"` / `"sealed-deletion-intent"`. |
| Eligible key | The dedicated key in an independently accepted receiving-offer0. |
| Kind | Exactly `"deletion-request"`. |
| Body | Complete original signed deletion-request0 wrapper. |

Use RFC9180 single-shot HPKE Base mode with DHKEM X25519/HKDF-SHA256, HKDF-SHA256
and AES-128-GCM. Preserve the exact outer layout: magic8, key ID16, encapsulated
key32, U32 big-endian ciphertext length, then complete ciphertext including the
16-octet tag. There are no trailing bytes. Info is the new domain, NUL, raw key
ID16 and public key32. AAD is magic8, key ID16 and ciphertext length4. Each new
encryption uses a fresh maintained-library encapsulation, never a reused context.

The encrypted frame is magic8, U32 intent length, original strict UTF-8 intent,
Ed25519 signature64, U32 identity-bundle length, original bundle JSON. Its maximum
plaintext is 8,388,608 octets; body and identity-bundle bounds remain 4,194,304 and
1,048,576. Complete framing and all encoded/decoded bounds apply before allocation
and parsing. The intent has maximum container depth32. The bundle supplies
candidate evidence, not a trust anchor.

The intent has exactly these eleven required members:

| Member | Required value |
| --- | --- |
| `version`, `purpose` | The exact values above. |
| `record` | Fresh nonzero ObjectId for this device's carrier preparation. |
| `sender` | Exactly `principal`, `device`, `state`, `binding`; identical to the original request's actor. |
| `recipient` | Exactly the independently selected `principal`, `device`. |
| `key` | Dedicated receiving-offer key ID. |
| `offer` | Lowercase SHA-256 hex of the complete original signed receiving-offer wrapper octets. |
| `kind` | Exactly `"deletion-request"`. |
| `body` | Canonical padded base64 of the complete original signed request wrapper. |
| `notBefore`, `notAfter` | Canonical uint64-string creation/release bounds, positive half-open interval. |

Apply the same strict scalar and unknown-member rules as the request. Sign the
original intent with the new signature domain, NUL, U32 original intent length,
then original bytes, under the independently accepted sender device key.

Before encryption, match the intended recipient to the accepted offer actor,
mailbox association, key owner and actual original recipient scope. Require
current Send authority for the request actor and current Receive authority for
that recipient. An arbitrary provider, forwarding party or another group member
cannot sign as the original author. No terminal-retirement exception from
identity administration applies to a deletion request.

The full credible creation/release interval must fit the intent, request,
original offer publication and required authority intervals. The intent interval
must lie within the original request interval; the request acceptance end must
not exceed the key's original receiveUntil. Preserve all earlier owning deadlines.
These checks include time spent waiting, encrypting, queueing and releasing bytes.

Atomically retain the exact intent, signatures, original offer, current authority
and scope dependencies, ciphertext and outbox identity before release. Exact
retries use that ciphertext and retain prior accepted or uncertain outcomes.
Before every bounded output and final flush, repeat the owning current checks,
including any transport, account, route and disclosure permission. SMTP acceptance
remains transport evidence, never evidence that a deletion was honored.

A fresh eligible offer may permit a separately authorized new preparation for
the same still-valid original request. It uses a new intent record and ciphertext
and retains prior uncertainty; it cannot change the request identity, target,
original bytes or acceptance deadline. A different author device issues its own
fresh request rather than forwarding the first device's signed body as its own.

::::

:::: {.details summary="Mail carriage, profile dispatch and recipient acceptance"}

### Exact opaque mail carriage

Use the existing sealed-control MIME shape with the new exact binary profile:
outer `multipart/mixed`, first a base64 UTF-8 `text/plain` notice containing exactly
`Encrypted conversation control.`, then an unnamed base64 attachment of the
parameter-free mail-control media type. Preserve the selected sealed-control
header, two-part, line-folding and transfer-decoding rules. No clear offer,
request, identity proof, target, personal-address duplicate or fallback command
is added outside the ciphertext. Ordinary SMTP routing still has its actual
metadata exposure; encryption alone does not mask outer addresses.

Dispatch only to the independently supported profile selected by exact magic and
the device's original issued-key inventory. A sealed2 parser must not accept this
as a new kind, trial-decrypt it under an assertion control key or reinterpret a
failure as clear JSON. Unknown magic, missing keys and unsupported versions stay
inert and produce no automatic reply. Legacy clients may display an opaque
control attachment; no MIME label can require them to hide it.

The existing opaque relay projection may carry these exact encrypted carrier
bytes only under actual route/account permission for the intended peer and scope.
For opaque-v0, the committed carrier is the exact sealed binary, not a nested
ordinary-mail MIME entity; the relay retains its existing octet-stream layout.
Its delivery proof commits those exact binary bytes. All privacy, current route and
account checks remain required. No new relay grant scope, provider API or HTTP
operation is implicitly selected. If the available route cannot authorize this
delivery, hold it; do not expose protected claims through a weaker route.

### Accept through the recipient's durable owner

Bound the complete binary before cryptography. Select exactly one original
locally issued offer and dedicated key by ID; require its unwithdrawn ownership
and actual receiving interval. An imported foreign offer is not a locally issued
key. Authenticate the entire ciphertext before parsing or presenting its body.

Validate exact frame, intent, signature, original offer digest, recipient and key
owner, original request and actor equality. The request must pass its own signature
check under independently accepted authority; the outer signature does not
replace it. Validate current author Send and recipient Receive authority,
accepted identity history, actual local delivery scope and all original deadline
dependencies. The original offer's publication may have ended during transit;
its unchanged receiving promise and original valid creation bounds still apply.
Continuous same-key/role renewal follows the existing
[purpose-specific continuity rule](provider-grants.md#continuity-and-freshness-have-different-scopes).
A revocation, role or key gap holds acceptance, even with a plausible old timestamp.

Only after those checks may a capable recipient classify the carrier as protocol
traffic rather than a human message. Do not generate a message notification,
deletion announcement or automatic response. Missing original target evidence
remains a protected pending dependency; it does not reserve or suppress that
target. Later target arrival reruns the full live authorization, interval, scope
and conflict checks, rather than trusting the earlier pending classification.

Before removing content, independently obtain the accepted original authored
record and compare its reference, complete-byte digest, scope root and eligible
operation. A matching digest cannot select an unresolved conflict winner or
authorize a newly added audience. Apply the [recipient deletion transaction and
retention rules](delivery-policy.md#keep-removal-effective-when-deliveries-arrive-out-of-order).
Commit the authenticated request/replay provenance, accepted disposition,
suppression and ordinary-presentation removal through that same durable owner.
Serialize original acceptance, deletion, rendering and restoration. A crash
cannot leave removal reported committed while its durable suppression is absent.

Retain intent identity as `(sender principal, sender device, record)` and original
signed intent bytes under the same authenticated duplicate/conflict discipline.
Different valid intents may carry the same request; the original request identity
still has one effect. Invalid candidates cannot reserve either namespace.
Suppression is keyed by the original logical target and accepted disposition,
not its transport delivery, key ID or a temporary carrier. Request/key expiry
does not undo an honored disposition. Budget exhaustion holds affected work;
it cannot erase suppression or restart an uncertain delivery as a new effect.

Persist the accepted policy decision with the request's replay evidence before
reporting a completed local disposition. Exact delivery retries recover that
decision rather than reevaluating a completed request as a fresh remote effect.
A later deliberate local policy action remains local; it does not send a report
or make the original request new.

Recipient policy may decline removal silently. Honoring it silently removes
ordinary content without deleting independently authored replies or quotations.
Preserve audit, replay and continuity evidence under the existing policy; raw
inspection remains separate from ordinary conversation presentation. Neither
path sends a decision receipt, read status or retention-policy report. Ordinary
transport errors can update the sender's delivery uncertainty only.

::::

## Required verification

Exercise the complete joined path, not only a supplied-key signature check:

- Publish an eligible offer through actual ordinary mail and a separately
  accepted protected resource. Reject wrong actor/mailbox, nested or multiple
  candidates, parameters, malformed encoding, unknown members and excess bounds.
- Use real independent signing and dedicated HPKE keys. Reject an assertion
  control key, wrong offer digest, wrong recipient, cross-profile magic/domain,
  invalid final tag and valid outer intent with an invalid inner request.
- Check publication expiry before release, receiving expiry during processing,
  withdrawal, role/key gaps, accepted continuity and a reassigned mailbox.
- Retain exact queued bytes across restart and response loss. A replacement
  preparation retains request identity and deadline; replay cannot renew either.
- Deliver a valid request before its original, concurrently with it and after
  a separately encrypted duplicate. Reject forged target reservation. Test
  same-identity conflicting requests and intents without arrival-order winners.
- Crash before and after the recipient transaction, rescan, rotate keys and
  restore old history. Verify persistent suppression, independent replies and
  budget refusal without recipient markers, notifications or decision receipts.
- Exercise mixed recipient-device support and actual masked relay carriage
  separately. Unsupported devices and legacy clients are not silent-removal
  passes. No automatic setup, offer or deletion-response loop is permitted.

Record exact tested sources, adapters and outcomes. Same-code peers can exercise
state isolation and real transports; they do not establish independent
implementation interoperability or complete security review.
