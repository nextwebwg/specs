---
title: Encrypting the first message
order: 7.15
blurb: setup before content · automatic response · offline admission
sectionNav: true
---

# Encrypting the first message

The first transmission to a new person can be a setup request rather than their message. The sender's client keeps the writing private, obtains the recipient's signed setup data through an enabled provider service or the [ordinary-mail setup carrier](mailbox-setup.md), establishes protected delivery, and only then releases the message. The recipient does not need to write a reply to enable that exchange.

> [!ex] Start securely with someone new
> Alice writes to Bob and presses Send. Her client has no usable encryption setup for him, so it retains the draft and asks Bob's enabled provider service for setup. Bob's client automatically answers the authorized request with signed public device evidence and admission material. Alice's client validates it and establishes the encrypted conversation. The message then leaves Alice's device inside its protection envelope.
>
> Bob sees Alice's message, not an exchange of protocol emails. If the setup cannot complete, Alice's writing stays queued under its selected delivery policy.

> [!note] Defined contract; complete journey not yet implemented
> The [automatic first-contact exchange](bootstrap.md) specifies domain discovery, source-account authorization, device possession, the private control inbox, signed replies, offline publication and direct inbox-provider route issuance. Known-pair [queue grants](provider-grants.md) remain separate authority. The local bootstrap component tests part of this contract; it does not establish a working public service or complete first-message encryption journey.

## Use the available setup carrier

With an enabled provider service, use the account/device-authorized exchange described below. Without one, compatible clients can use [ordinary-mail setup](mailbox-setup.md): one content-free, directly addressed request and an encrypted response, under explicit request/disclosure policies. That path can leave a setup notice in a legacy inbox and requires trustworthy receive authentication evidence; it cannot satisfy required address masking. Neither path requires a human-authored introduction, and neither proves independent personal identity.

## Keep the message private during setup

A client may initiate setup when the person has selected a recipient for a protected send and enabled automatic secure setup, either for this send or through a remembered policy. Receiving an arbitrary message or a URL cannot grant that permission. Do not turn address books into bulk capability probes.

The [setup-secret lifecycle](setup-secret-retirement.md) requires retirement after successful use and automatic expiry of abandoned attempts, with a 600-second bootstrap-request maximum. Public transcript retention does not retain private admission keys.

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

Private-addressing setup identifies the recipient’s already configured receiving service. After independently validating the intended identity/setup, the sender obtains accountable source permission and requests a route directly from that service under [provider-issued route1](relay-routes.md). The normal inbox provider can allocate or renew an alias while all recipient devices are offline. It needs no recipient-device approval of individual addresses. The [private-addressing contract](private-routing.md) keeps personal From/To/Cc inside encryption and performs the transport substitution before submission. Service association, active routing policy and exact route-use permission remain independent of native encryption admission. A key package or queue credential is never routing authority. Required masking holds if the current route is unavailable; routine renewal does not change the personal contact or a frozen uncertain retry.

## Validate, establish encryption, then send

The sender independently validates the complete evidence: exact requested mailbox, signature and purpose, accepted identity and continuity, current authorized device, freshness and clock interval, exact supported suite and usable admission package. A provider's TLS identity or account-authentication claim cannot replace those checks.

For a previously unknown identity, apply the selected [first-contact association policy](mailbox-association.md). An allow-unverified policy can establish encrypted first contact automatically with continuity from that decision onward. A require-verification policy waits for its independent verification mechanism. Neither a self-signature nor an automatically answered challenge alone defeats an active attacker substituting the first identity. A future provider-attested mailbox-verification mechanism must define its evidence and trust policy explicitly before it can satisfy the latter setting.

Once discovery is valid, use the suite's existing MLS invitation, context, membership, package single-use and admission rules. No provider-specific encryption protocol or generic setup acknowledgment substitutes for them. Invitations and other setup controls contain no human message content. A fully validated ordinary-mail response can satisfy [live device confirmation](freshness.md#live-confirmation-through-existing-mailboxes) under its original retained attempt and age window; a provider service is not mandatory for that evidence. The sender releases content only when the suite's protected-send preconditions are satisfied and its final authority/audience checks still pass. Asynchronous admission does not require inventing an additional online acknowledgment; readiness has the exact scope defined by the selected MLS carrier and application contract.

## Finish setup for one intended send

Receiving encryption details does not mean your message is ready to send. The app still has to prepare the conversation, finish the required key cleanup and queue the message and its planned copies. If you edit or cancel a waiting message, a late setup response must not send its old version.

::: {.details summary="Conversation evidence, draft revisions and crash-safe handoff"}

### Acquisition evidence and receiving evidence

The request and response retain their original signatures, identifiers and deadlines. They prove only their owning setup steps. Independently select original assertion10 for **every actual selected device in this delivery**, including participating creator devices. Require the fixed readable application under the chosen ordering and retain each device’s interaction list; an acquisition assertion cannot stand in for missing device support.

| Material | Permitted use |
| --- | --- |
| Dedicated initiating assertion/control key from mailbox setup | Request correlation and encrypted setup-response receipt through its fixed attempt deadline. It has no MLS package and is not the creator’s ongoing receiving publication. |
| Creator’s ordinary receiving assertion | Complete current assertion10 with an independently retained usable control key, exact selected application support and the required local issuance/custody records. Select and sign its original references into the actual roster. |
| Recipient response or allocated publication | Original independently valid assertion/package evidence for that exact device, under its request/allocation/peer restrictions. A successful fetch cannot allocate it again, widen its audience or remove its single-use requirement. |
| Accepted roster and invitation | The actual selected conversation, devices, context, keys and admission material, under initial10/roster7 or established10 for the current baseline. Other intended slots may remain pending outside this actual native cohort. Setup alone creates none of those states. |

One assertion may serve both acquisition and ordinary conversation receiving only if its exact original bytes meet **both** contracts, including current authority, application selection, disclosure and independent custody/deadlines. The dedicated mailbox-request assertion is expressly attempt-only; select a separate ordinary own-device assertion for the conversation. Do not replace its key or extend its expiry inside the previously signed request. An already valid ordinary assertion can be reused without generating another key merely because setup was performed.

Every joining device needs its own usable package. The creator’s initial self-membership does not consume a joining package; other devices of the same principal are still joiners. An ordinary creator assertion may omit a package when the selected creation contract does not need one, but it still needs a usable retained control key for its receiving role. A future return stream or new member admission obtains its own appropriate package; receiving the initial stream does not invent one.

The invited device validates the creator’s selected ordinary assertion in the invitation/roster, independently of the earlier temporary request. It must belong to the same currently accepted intended creator, with the exact roster binding, and satisfy current association and suite rules. A changed publication does not authorize a changed principal, device, audience or group. Missing or incompatible ordinary evidence holds preparation; it is not a reason to retain an obsolete temporary private key indefinitely.

### Reply-aware acquisition and handoff

For explicitly selected v1 compatibility, [mailbox-setup-v1](mailbox-setup.md#set-up-the-declared-reply-policy), [provider exchange1](provider-control.md#reply-aware-known-pair-exchanges) and [bootstrap1](bootstrap.md#provider-setup-for-declared-reply-policies) acquisition branches select the [retained reply-aware agreement](reply-intent.md#reply-aware-protected-agreement). Apply the table’s role distinctions using original assertion9 for that agreement; actual admission is initial9/roster6 or established9 with context9/envelope5/mime-suite-v1 and the current controls. Deliberately selected earlier-agreement setup uses its original assertion8 and version0 acquisition records instead, without changing those signed formats or claiming current support. The table's roles and complete validation/transaction boundaries remain unchanged. The temporary initiating assertion9 is not ordinary creator receiving evidence, and no signature or package is rewritten to change its version.

Freeze the selected agreement and required reply intent with the local send-intent revision and each copy's preparation dependencies. A response for another agreement cannot satisfy that attempt. Independently validate every intended device's support and current authority before staging. Required no-replies/private-only behavior cannot disappear during operation intersection, account changes, path switching, retries or outbox activation. Provider acquisition additionally requires its exact descriptor1/account/grant/exchange or bootstrap source/recipient authority and original agreement/descriptor commitments. The older assertion8 path cannot claim this handoff by carrying a renamed field. The source-bound joined review and actual complete acquisition/admission/handoff implementation remain acceptance obligations.

### Acquisition for independently ready deliveries

For mail-conversation-v2, the same setup-to-outbox transaction applies to each actual selected delivery. Its exact acquisition choices are:

| Path | Discovery and permission | Signed result and conversation evidence |
| --- | --- | --- |
| Known pair | [Provider descriptor2](provider-discovery.md#discover-the-asynchronous-agreement), grant2 and immutable control2 configuration | Original control2 response and assertion10 |
| First contact through providers | [Bootstrap descriptor2/source2](bootstrap.md#automatic-setup-for-independently-ready-recipients), independently authorized source/recipient operations | Original fresh response2 or allocated publication2 and assertion10 |
| Existing mailboxes | [Mailbox setup2](mailbox-setup.md#set-up-an-asynchronous-delivery), enabled direct-authenticated request/response policy | Original setup2 response, assertion10 and exact pending attempt, through sealed2 |

These branches supply candidates, not current membership or release permission. Use the [exact v2 binding](suite-profile.md#asynchronous-protected-agreement): context10/initial10/roster7/established10, ordinary controls2 or managed exchange4/final5, sealed2 and mime-suite-v2. Keep every original proof and independently validate current identity, selected mailbox/account association, verification/freshness, allocation and route authority. The acquisition/receiving table's role and custody distinctions apply using original assertion10, including the separate creator receiving assertion; an attempt-only mailbox key is not promoted.

Freeze the logical authored0 record, intended scope, reply-intent1, selected source account and exact revision before the first human delivery. Acquisition contains no human writing, authored-content digest, intended-slot list or visible roster. Each attempt is durably tied locally to that revision, exact required agreement and selected target mailbox/device. Per-message selected addresses, not an assumed invitation address, control account/delegation/acquisition lookup. A valid result cannot change the selected mailbox or resolve another creator's initially unknown scope slot.

Select evidence for **every actual device in this delivery's frozen cohort**, including participating sender devices. Validate the fixed readable application and retain independent interactions; no optional-block intersection rewrites the authored record. Originally intended unresolved slots stay explicit and pending. Their missing evidence alone does not block a ready eligible delivery when the retained plan permits independent progression. Never drop a device from an already frozen actual cohort to disguise a failed check.

Stage the original common authored bytes together with this distinct delivery's exact actual slot map, native admission, prepared representation, dependencies and non-releasable outbox. Continue the existing retirement/activation/release transaction for that delivery. Each later delivery needs eligible current evidence and its own actual admission/preparation; it retains identical common bytes and original disclosure authority. This does not permit subset emission inside a native group with a different actual audience, inherit another device's stream/outbox or send from an archive. The mode-specific admission rules still apply.

Different acquisition paths or versions do not create a new author message, scope, package realm, source permission, deadline or conflict namespace. Existing valid preparations/retries retain their exact bytes and uncertainty. Changed content, sender, recipients, reply contract or protection policy needs its owning newly authorized composition; a late result cannot send an editor's newer revision. Cancellation/expiry retains safety and possible-exposure evidence. No result or installed-setup receipt can set an unscoped ready flag or erase another recipient's pending state.

### Freeze the send intent before acquisition

On Send, retain an immutable local send intent identifying the selected sending account/principal, a local intent ID and revision, exact authored content/resources, personal audience, reply/new-conversation selection, required protection/disclosure policy and current draft selection. Its private content commitment, if used locally, never appears in acquisition traffic. These are local records, not new public event fields or a prescribed database schema.

The intent is distinct from each acquisition attempt, contribution, conversation, delivery and transport attempt. Several recipients or retries may require several acquisition records. Every such record links to the same exact local intent revision and its own original endpoint/account/nonce/deadline/evidence. A response can satisfy that record only; it cannot create a fresh intent or acquire the power to send current editor contents.

A person editing a queued, still-unreleased send supersedes that selected revision and returns its writing to editable draft state. New Send authorizes a new revision; ordinary typing must not mutate the old immutable snapshot. Changing account, audience, reply target or protection policy invalidates derived setup/preparation dependencies. Previously received public evidence may remain usable under its own policy, but the old attempt cannot authorize the new send. New incoming mail must not retarget either revision. Existing submitted or uncertain deliveries retain their original identity and outcome; editing or cancelling cannot recall them.

Freeze the authorized copy plan before materializing its contributions. Reserve each required contribution identity once when that copy’s selected author/context, audience and content snapshot can be frozen under its owning event rules. Record the complete local mapping from intent revision to copy, contribution and delivery identities durably. Repeating setup or resuming a copy’s handoff returns that mapping; it cannot allocate another event for that copy. If an authorized edit changes the contribution, use a separately authorized revision/contribution under the event rules rather than rewriting the old one. Local intent/revision names are not transmitted as invented headers or substitute EventReferences.

### One send intent can contain separately protected copies

The [private-copy contract](private-copies.md#separate-conversations-separate-authority) requires fresh conversation, event, resource and Message-ID identities for each private copy. One local intent therefore maps to a planned set of scoped contributions, not necessarily one shared event. Each copy has its own exact audience, assertion/application selection, package use, protected preparation and outbox evidence. No shared local intent or copy-correlation identifier is transmitted to connect those conversations.

Readiness and uncertainty are per copy and per delivery/recipient. The [delivery-policy progression rules](delivery-policy.md#a-waiting-delivery-is-different-from-missing-setup) own exact cohort, missing-setup, hosted-upload and aggregate-outcome boundaries. A ready visible copy does not make a private copy ready or justify an ordinary fallback for it. The effective send plan determines whether ready copies may progress independently or must wait for the whole selected plan; this chapter imposes neither a new universal all-or-none policy nor permission for unselected partial release. Record that choice before release. An empty/absent private-copy result cannot be interpreted as successful delivery or recreated as a new event.

For each copy eligible to progress, apply the staging/retirement/activation procedure below. Its transition is atomic within the owning conversation’s state and stage. Persist the parent intent’s complete planned-copy mapping and link each stage to the exact revision, so activation of one stage cannot invent or delete another. If local policy requires several copies to activate together, their coordinated activation must preserve that invariant across crash/restart; separate commits cannot claim collective atomicity. Independent progression retains separate outcomes and never reports the whole send successful from one copy’s result.

### Stage once, retire, then authorize the outbox

Use the existing serialized authority and transport procedures. A previously successful setup callback is not a current authorization snapshot.

| Boundary | Required durable decision |
| --- | --- |
| Prepare the conversation | Recheck the still-selected intent revision, own account, intended scope and exact actual delivery cohort, its identities/devices/roles, mailbox associations, policy, exact assertions/application, package allocations, routes and credible-time bounds. Missing or changed dependencies hold the affected delivery; other intended slots can remain pending under the frozen progression policy. Select ordinary versus managed membership under its owning contract. |
| Accept local creation/preparation | For this scoped copy, commit the resulting MLS checkpoint/state, exact signed roster/invitations, package reservations, immutable contribution identity and prepared representations, original dependency references, pending retirement intents and a **non-releasable** outbox stage together. Expose all or none after restart. A locally atomic reference or equivalent storage protocol may join stores; separate uncoordinated commits cannot claim this property. |
| Complete required retirement | Perform the crypto engine’s owning deletion schedule and reconcile its durable result. Store the retirement-completion observation. No unsigned callback, HTTP success or mere absence of a key row is erasure evidence. A crash or failure leaves the affected stage held and resumes retirement before release. |
| Transfer the one intent to its outbox | Under one serialization boundary, confirm retirement completion, unchanged selected intent revision and current authority/policy dependencies; atomically mark the setup/intent handoff complete and activate only this eligible copy’s exact retained contribution/delivery set, preserving the parent plan’s progression policy. A competing completion returns the same retained result; a cancelled or superseded revision cannot activate it. |
| Start each transport attempt | Apply the outbox’s existing per-delivery/recipient exclusivity and current pre-DATA checks, including renewed authority, route, time and protection checks. Track each invitation and human delivery separately. Activation is not SMTP acceptance or recipient admission. |

The staged group and prepared ciphertext remain the same objects across retries. Repeated setup completion cannot rerun an Add, spend another package, recreate a group/epoch, advance a sending ratchet twice or replace retained ciphertext. If activation is held after local creation, preserve the accepted safety state and original outbox evidence while the owning protocol selects a valid repair/new delivery. Do not roll back accepted crypto state to manufacture a cleaner retry.

A current dependency change while retirement is pending does not excuse the required retirement of already consumed/superseded secrets. Finish cleanup, hold release and re-evaluate the original staged work. Conversely, an ordinary still-authorized receiving key has its independent declared lifetime; finishing setup cannot destroy it merely because the temporary request key is no longer needed.

A completed acquisition can stop its own timer and retire attempt-only secrets. That does not authorize application release before the above barriers. An unfinished acquisition expires under its original deadline; a completed, independently authorized conversation/outbox has its own validity and retry rules. No generic `ready:true` field crosses these boundaries or substitutes for the planned copy set.

### Restart and cancellation outcomes

| Retained state | Required recovery |
| --- | --- |
| Acquisition pending, no accepted local creation | Reconcile the original attempt and deadline; keep the writing private. No absent record is proof of remote nonexecution. |
| Accepted local state with retirement pending | Resume the exact retirement and held stage. Do not rebuild from an older checkpoint or repeat package consumption. |
| Retirement complete, handoff not committed | Recheck the selected intent and current dependencies; activate the original stage once or keep it held. |
| Handoff committed, transport not started | Recover this copy’s same contribution/delivery set, parent-plan status and normal release checks. A repeated setup response cannot enqueue another set. |
| Transport submitted or outcome uncertain | Keep original per-recipient attempt evidence; use the transport retry/reconciliation rules, never a new contribution from setup. |
| Intent cancelled or superseded before release | Block activation and future release under that revision’s generation. Preserve necessary safety, allocation, retirement and uncertain-transport evidence. Any new send needs its own authorization. |

Cancellation and final release use the same local intent/dependency generation boundary. Recheck a newly installed cancellation before releasing DATA, under the existing transport fence. Cancellation after bytes have crossed the local release boundary retains the actual submitted/uncertain outcome; it is not a remote recall guarantee. History recovery can restore readable content but cannot recreate these live authority, key-consumption or outbox states from an archive.

:::

Package races, revocation or an unsupported suite may require fresh setup. Keep the draft and original send intent. A new request uses a new immutable request identity and explicit bounded retry policy; an old response cannot satisfy it. Retrying a protected transport submission uses the original protected contribution and its bytes, rather than creating another human message.

## Failure outcomes

| Condition | Required result |
| --- | --- |
| No usable provider setup | Try enabled ordinary-mail setup under its exact policy and evidence gates, or hold |
| No enabled compatible recipient path | Keep the protected send held; offer separately authorized ordinary introduction, compatible-client setup or a permitted fallback |
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
