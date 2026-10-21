---
title: Encrypting the first message
order: 7.15
blurb: setup before content · automatic response · offline admission
sectionNav: true
---

# Encrypting the first message

The first transmission to a new person can be a setup request rather than their message. The sender's client keeps the writing private, obtains the recipient's signed setup data through an enabled provider service, establishes protected delivery, and only then releases the message. The recipient does not need to write a reply to enable that exchange.

> [!ex] Start securely with someone new
> Alice writes to Bob and presses Send. Her client has no usable encryption setup for him, so it retains the draft and asks Bob's enabled provider service for setup. Bob's client automatically answers the authorized request with signed public device evidence and admission material. Alice's client validates it and establishes the encrypted conversation. The message then leaves Alice's device inside its protection envelope.
>
> Bob sees Alice's message, not an exchange of protocol emails. If the setup cannot complete, Alice's writing stays queued under its selected delivery policy.

> [!note] Defined contract; complete journey not yet implemented
> The [automatic first-contact exchange](bootstrap.md) specifies domain discovery, source-account authorization, device possession, the private control inbox, signed replies, offline publication and optional relay follow-up. Known-pair [queue grants](provider-grants.md) remain separate authority. The local bootstrap component tests part of this contract; it does not establish a working public service or complete first-message encryption journey.

## Keep the message private during setup

A client may initiate setup when the person has selected a recipient for a protected send and enabled automatic secure setup, either for this send or through a remembered policy. Receiving an arbitrary message or a URL cannot grant that permission. Do not turn address books into bulk capability probes.

The [setup-secret lifecycle](setup-secret-retirement.md) requires retirement after successful use and automatic expiry of abandoned attempts, with a proposed600-second bootstrap-request maximum. Public transcript retention does not retain private admission keys.

Retain the authored body, subject, attachment bytes, quotations and draft state locally under the [private working-state rules](security.md#drafts-are-private-working-state). None goes in a setup request, ordinary server draft or readable handshake email. Do not include a digest of draft content: predictable text could be guessed against that digest. Setup necessarily exposes addressing and control metadata to the involved services; it is not metadata-private communication.

The user-facing states are **Setting up encryption**, **Sent encrypted**, or a held state explaining the missing step. Setup success alone does not justify a sent or read indicator. Exact request retries resume the saved setup; they do not duplicate the human message. A held send does not become plaintext because of a timeout or an unsupported service.

## Ask through the provider's control service

The sender uses the recipient domain's authenticated service delegation, under the [discovery rules](provider-discovery.md), for this explicitly selected bootstrap purpose. This authorizes only the declared control location. It cannot install a login issuer for the sender, forward mailbox credentials or establish a correspondent identity. The [bootstrap descriptor and exchange](bootstrap.md) must be advertised before requests are sent; the configured pair-grant queue is not that endpoint.

The [bootstrap authorization chain](bootstrap.md#who-may-ask-for-what) distinguishes the sender's authenticated mail account, the initiating device's possession proof and the recipient's independently authorized devices. An attacker-controlled self-signature is not proof of a sender mailbox. An authenticated provider's statement about its account is not independent human verification. Providers must validate these scopes separately rather than accepting a generic `trusted:true` flag.

The recipient's service accepts automatic setup only for an account that enabled it. Account-level opt-in can authorize routine responses under a visible, revocable policy, without a per-message prompt. That permission does not enroll devices or authorize message decryption. A corresponding device policy controls which valid setup requests its client answers. Providers need finite per-sender, destination and deployment budgets, expiration and replay storage; forwarding a setup request must not become a spam or callback relay.

Ordinary email can already reveal mailbox existence through rejection behavior. Setup does not promise to erase that exposure, or hide a successful opt-in response from its authorized requester. It does restrict who may ask and what they receive: no unrestricted mailbox directory or presence lookup. Valid authorized requests return uniform pending admission, and unavailable recipients remain pending without a detailed account/device status. The [bootstrap contract](bootstrap.md) defines exact permissions, disclosure, blocks and finite deployment budgets.

## Return setup automatically

For an admitted request, there are two paths:

- **Published material is usable.** The provider returns the exact signed material the recipient device previously authorized it to publish. This can permit encrypted first contact while that device is offline.
- **Fresh material is needed.** The provider places the content-free request in its separate control queue. An enabled recipient client retrieves it, validates the request and its policy, and automatically returns one signed setup response. It needs no human-authored email.

An automatic response is bound to the exact request, nonce, intended mailbox, participating devices, purpose, selected protocol support and validity. The source advertisement and any admission package retain their own original signatures, scope and expiry. An outer provider response cannot refresh expired material or manufacture a recipient device signature. A response containing only `encryptionSupported:true` is insufficient.

Apply the [freshness contract](freshness.md) to the selected delivery. Published evidence is not a response to a fresh challenge. The sender must distinguish cached publication from a newly signed device response and apply the selected freshness policy. If the sender requires fresher evidence, it waits for that evidence rather than presenting cached data as proof that a device is online.

The recipient client durably saves a signed response and any allocated package before upload. Retrying returns the same result. The response does not elicit another setup response, and opening a received message never starts this state machine. Providers must not represent control records as ordinary mailbox messages requiring a legacy client to hide or discard them.

Private-addressing setup additionally returns an independently provider-authorized recipient alias, bound by the recipient device to this peer and routing scope. The [private-addressing contract](private-routing.md) requires personal From/To/Cc inside encryption, transport substitution before submission and separate route-use authorization. The [route authorization contract](relay-routes.md) supplies source-account permission and recipient route approval after the peer identities/setup scope are available. The [bootstrap relay follow-up](bootstrap.md#finish-private-routing-in-the-same-handshake) obtains those routes after learning the intended recipient identity and before content release when masking is required. A key package or queue credential never becomes routing permission.

## Validate, establish encryption, then send

The sender independently validates the complete evidence: exact requested mailbox, signature and purpose, accepted identity and continuity, current authorized device, freshness and clock interval, exact supported suite and usable admission package. A provider's TLS identity or account-authentication claim cannot replace those checks.

For a previously unknown identity, apply the selected [first-contact association policy](mailbox-association.md). An allow-unverified policy can establish encrypted first contact automatically with continuity from that decision onward. A require-verification policy waits for its independent verification mechanism. Neither a self-signature nor an automatically answered challenge alone defeats an active attacker substituting the first identity. A future provider-attested mailbox-verification mechanism must define its evidence and trust policy explicitly before it can satisfy the latter setting.

Once discovery is valid, use the suite's existing MLS invitation, context, membership, package single-use and admission rules. No provider-specific encryption protocol or generic setup acknowledgment substitutes for them. Invitations and other setup controls contain no human message content. The sender releases content only when the suite's protected-send preconditions are satisfied and its final authority/audience checks still pass. Asynchronous admission does not require inventing an additional online acknowledgment; readiness has the exact scope defined by the selected MLS carrier and application contract.

Package races, revocation or an unsupported suite may require fresh setup. Keep the draft and original send intent. A new request uses a new immutable request identity and explicit bounded retry policy; an old response cannot satisfy it. Retrying a protected transport submission uses the original protected contribution and its bytes, rather than creating another human message.

## Failure outcomes

| Condition | Required result |
| --- | --- |
| No bootstrap service or no enabled recipient path | Keep the protected send held; offer separately authorized ordinary introduction, compatible-client setup or a permitted fallback |
| Enabled device unavailable, usable published material present | Continue through ordinary asynchronous admission after all checks |
| Enabled device unavailable, no usable material | Wait without claiming unsupported account or online status |
| Request/response invalid, expired or inconsistent | No identity replacement, user-content release or automatic response to the invalid record |
| Already associated address advertises another identity | Existing continuity/replacement rules apply; bootstrap cannot repin it |
| Strict first-contact verification still missing | Retain setup evidence and hold content for verification |
| First protected submission outcome uncertain | Preserve its immutable contribution and resolve through the delivery/retry contract |
| User cancels before content handoff | Stop future setup retries and content release; a completed setup may already have disclosed public metadata |

## Acceptance boundary

The complete positive journey must start with no recipient association or pair grant at the sender, deliver only content-free setup traffic, automatically produce device evidence without a human reply, validate it under explicit first-contact policy, admit the selected suite and exchange the first encrypted human message. Repeat with offline published material and with no material, checking that the latter sends no content.

Negative cases include unsolicited probes, self-signed mailbox impersonation, provider-origin substitution, unsupported legacy accounts, address enumeration, forged or cached-as-fresh responses, replay, package races, changed identity, loss/restart at every durable handoff, cancellation and unknown delivery results. Inspect actual outgoing requests and mailbox contents, including subject, quoted text, attachments and draft synchronization—not just a mocked `ready` flag. Existing configured-pair evidence is not this first-contact test.
