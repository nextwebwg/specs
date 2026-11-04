---
title: The encryption journey
order: 7.1
blurb: first contact · everyday sending · devices · recovery · failure cases
sectionNav: true
navGroup: guide
---

# The encryption journey

A person should be able to use an existing email address, start a conversation and let their client handle encryption. They should not need to exchange keys manually, choose cryptographic algorithms or repeat a security decision on every reply. When the client cannot preserve the selected protection, it keeps the writing and explains the next available step.

The app checks who a message is for, which devices may receive it, and whether it can protect every intended copy. You see the outcome and any decision you need to make; the app handles the mechanics.

> [!note] A draft, not a finished service
> This describes the intended experience. Some parts have local demonstrations; the complete journey still needs implementation and independent evaluation. The architecture and acceptance details below identify those gaps.

## Write normally

Use your existing address and choose the people you want to reach. If they have compatible encryption setup, your app prepares a protected conversation before sending your writing. You do not exchange a password or paste a key into an email.

Compatible apps can [exchange content-free setup emails](mailbox-setup.md) before sending your writing. A legacy app may show a setup notice. An upgraded provider can instead ask for the recipient's public setup information without sending setup mail to the inbox. The recipient's enabled app can answer automatically, or its provider can supply information the device has already authorized for that purpose. The person does not need to write a reply just to enable encryption.

If the required information is unavailable, that delivery waits. A clear waiting state tells you what has not finished. A network failure does not turn your private message into ordinary email.

## Choose what happens with an older app

You can require encryption, allow ordinary delivery, or allow a particular hosted-link arrangement. The app remembers your choice and makes the actual result clear. A hosted link is a different arrangement with its own access risks; it is not automatically equivalent to encryption between two email apps.

For a group, ready people can receive your message while others are still setting up. Everyone remains in the intended discussion, and the app shows who is pending. When a later delivery becomes possible, it carries the same authored message; it does not add a second copy to the conversation or repeat an answer or reaction. Each author still needs permission and retained content for their own late deliveries.

Different people may support different interactions. A compatible simpler app can read a question and send a normal reply while another app offers answer buttons. The app accounts for every intended delivery; someone awaiting setup cannot cause an unauthorized ordinary copy to be sent.

## Reply without repeating setup

Once the conversation is established, you reply normally. The app remembers the contact and handles the changing encryption keys. It also remembers exactly which message you are answering.

Setup keys have an expiry, and the app prepares replacements automatically. The default lifetime can be changed; everyone does not have to rotate on the same schedule. If valid replacement material is unavailable when needed, sending waits. Expiring a setup key does not delete your old messages. The [architecture explains which keys expire](security-profile.md#experimental-admission-lifetime) and [how replacements are published without disturbing mail already in transit](security-profile.md#publish-replacements-without-disturbing-in-flight-mail).

You do not have to open a message before a setup key expires. An enabled app can process incoming mail privately and keep it unread. Once retained as correspondence, it follows your history settings. If every eligible device remains offline past the necessary keys’ receiving windows, the old delivery may need an authorized historical copy from another device or the sender. Fresh setup alone cannot recover it. The [offline and recovery contract](suite-profile.md#unread-mail-and-long-offline-periods) defines those distinct outcomes.

A recipient can be offline when you write. The design uses email's ability to carry messages later; routine encryption does not require both people to be present at once. Where setup or a required security check needs a device that is unavailable, the app preserves your draft and explains the wait.

Encryption and identity verification are different. A message may be encrypted to a remembered contact whose real-world identity you have never independently checked. If you choose stronger verification, the app offers an independent comparison and remembers its scope. It must not display an unverified person as verified.

## Scan to add a device

Approve a QR pairing request on an authorized device. The new device makes its own keys. The app brings across the contact security setup, connects the account and automatically prepares encrypted sending; unchanged contacts do not need to verify you again.

A device can be allowed to send and receive without being allowed to add or remove other devices. More than one device can have that administrative permission.

Your saved messages are separate. Copying them is not a prerequisite for future encrypted sending. Existing encrypted groups still need to accept the new device through the protocol; the app handles that work and shows any remaining wait rather than leaving you to manage it.

## Remove a lost device

Use another authorized device to remove it. Once a sender learns and validates that change, future sends must exclude it. Removal cannot erase messages already on the lost device, and an offline sender may not have learned the change yet.

## Recover correspondence without reviving old keys

An encrypted archive can preserve readable messages and their attachments. Set up its recovery material somewhere you can still reach if the original device is lost. Neither an email password reset nor a billing receipt can decrypt such an archive.

Restoring correspondence does not authorize a replacement device to act as you. If a device with current enrollment authority survives, pair from it. A send-and-receive-only device cannot approve a replacement. If every authorized device is lost, the current design starts a new identity rather than secretly overriding the old one. The app must explain that boundary before you rely on recovery.

## Architecture and implementation

::: {.details summary="Architecture, required behavior and acceptance cases"}

### Set up once

The person connects their email account and chooses how incompatible recipients should be handled. The client remembers the effective policy in a visible, changeable setting: require an encrypted endpoint, allow ordinary email, or allow a particular hosted-access model. There is no automatic permission to use an unselected fallback. A product may offer a starting policy, but it must disclose and record that choice; this draft does not select a universal default.

The client creates a device identity and retains its secrets locally under the endpoint's storage protections. The [first-device procedure](identity-lifecycle.md#set-up-the-first-device) saves one crash-safe setup result before activation. First-device genesis establishes the initial identity authority; mailbox login supplies account access, not proof of continuity with an existing identity. If the account already has an accepted identity, use enrollment instead of silently creating a replacement. Publishing public device evidence is a separately enabled setting, not a side effect of reading an email.

Setup also establishes the first-contact policy: permit an unverified address-to-identity association, or require independent verification. These choices are separate from ordinary-email fallback. The former can make routine encryption automatic without claiming to defeat an active attacker who substitutes the first identity. The latter can hold an otherwise encrypted send until the binding is verified.

The setup view identifies where keys and plaintext are processed. A service that decrypts is an endpoint with content access. Browser-local keys do not by themselves establish protection against whoever can replace the browser code. Drafts follow the [private working-state rules](security.md#drafts-are-private-working-state); they must not leak into ordinary server drafts merely because sending has not started.

### Start a conversation

### No usable recipient evidence yet

The person writes normally. Before releasing content, the client constructs a recipient-specific send plan. Without compatible evidence, it cannot promise an encrypted first message.

If ordinary delivery is permitted, the composer identifies that outcome before send. The human-authored mail may include the sender's signed passive advertisement. A later human reply may carry the recipient's advertisement. Neither advertisement retroactively protects the earlier messages. The client does not send secret content in a probe or assume that an older client will discard protocol mail. An ordinary human introduction is one compatibility option, not a requirement for either enabled automatic setup carrier.

If encryption is required, the draft waits with a compact **Waiting for encryption** state. The client may use evidence already retained, enabled [ordinary-mail setup](mailbox-setup.md), or an explicitly configured, authorized discovery service. Otherwise the person can arrange an ordinary introduction separately, verify through an independent channel, or change the applicable delivery permission. A waiting encrypted send must not automatically become that ordinary introduction.

The [automated first-contact flow](first-contact-setup.md) keeps the human message local while a content-free provider request obtains signed device evidence, automatically from an enabled client or from valid recipient-published material. The client establishes protected delivery and then sends the human message. The [bootstrap wire contract](bootstrap.md) defines the separate account/device-authorized exchange; its complete joined implementation remains required. The configured known-pair exchange does not implement it.

Receipt of a passive advertisement does not trigger an automatic email response. Passive carriage uses human mail. The separately enabled [mailbox setup protocol](mailbox-setup.md) has exact request/response, domain-authentication and loop rules; the provider-assisted journey instead uses a separate control queue and explicit setup policy. It does not depend on legacy clients hiding handshake emails or a person replying to activate encryption. [Temporary setup secrets](setup-secret-retirement.md) retire after use, cancellation or fixed expiry; readable correspondence uses separate historical protection.

### A candidate identity is available

The client validates the advertisement, exact mailbox spelling, device binding, current authority, freshness and applicable revocations. It retains the source evidence. Under the configured allow-unverified policy, a sole eligible candidate can be selected through the association transaction. Multiple eligible principals remain ambiguous; the client cannot choose the newest or first arrival.

Once selected, that identity becomes the continuity anchor for the address. Routine valid successors retain their assurance level; encryption does not silently turn an unverified association into a verified one. A compact protection indicator can expose the fuller explanation on inspection. It must distinguish encryption to the selected identity from independent verification of the correspondent.

Independent human comparison is optional under the permissive policy and necessary when the chosen policy requires evidence it can supply. The comparison must use the full selected value and an independently trusted channel. A code copied from the same suspect email is not independent evidence. Successful comparison records its exact scope; it does not enroll devices or grant mailbox delivery authority.

### Establish protected delivery

The client checks the exact mutually supported application tuple, current authorized target devices, acceptable mailbox associations, admission packages and selected ordering mechanism. It constructs the MLS conversation and its authenticated invitation under the owning profile. Ordinary two-person and multi-person correspondence use independently owned sending streams. Managed groups explicitly select their separate shared-membership and quorum contract.

Validated discovery is an input, not completed encryption. A signature on an advertisement, a successful control-service response and SMTP acceptance do not replace MLS admission, authentication and application acceptance. The sender may report a protected copy submitted under the selected rules; it cannot claim every device decrypted or read it.

A missing or already consumed admission package, unsupported tuple, stale identity state or unresolved ordering leaves the affected delivery held. Re-evaluate before release. Do not choose an older or different tuple merely because it happens to parse.

### Continue without repeated decisions

The person replies, selects a predefined answer or reacts. The client retains the exact target, checks current sending authority, and applies the remembered policy. It does not ask for keys or a password on every contribution. New content and deliberately included quotations stay inside the protection envelope; a readable plaintext alternative beside ciphertext would disclose the same content.

An offline recipient does not need to be present if valid published admission material or an established usable conversation is available. Without it, the affected send waits. Simultaneous online presence can accelerate an authorized exchange but is not a requirement for ordinary asynchronous delivery.

On restart, the client resumes retained immutable sends and pending transitions. A retry uses the original contribution identity and authenticated bytes. Duplicate receipt does not duplicate an answer, reaction or external effect. Delivery uncertainty remains visible rather than being resolved by generating another contribution or weakening protection.

Opening a message, reconstructing a thread or refreshing capabilities does not send a receipt, submit an answer or disclose history. Reading and transport handoff are distinct states.

### Include someone who cannot decrypt

The client calculates the result for every intended recipient. Ready protected copies may proceed while others remain held, when the selected policy permits partial delivery. The sent view distinguishes that partial result from delivery to everyone.

Ordinary delivery exposes the reviewed content to that delivery path. Hosted access identifies its service and access model. A bearer link gives access to whoever possesses it and does not prove the named person is reading. Hosted notifications contain minimal invitation text, not the protected body or quoted history in previews. Automatic scanners and page opening do not submit an answer.

A contribution with an authorized ordinary or hosted disclosure is not summarized as confidential to encrypted endpoints alone. The contribution-wide exposure indication and the local delivery results remain distinct. Changing the fallback for an already submitted copy is an additional disclosure, not recall.

Every reply gets its own policy and audience check. The original sender's permission does not authorize fallback on the replying person's behalf. Forwarding or quoting an earlier protected passage requires authorization for the actual new audience. A new participant does not receive old history simply by joining.

### Add a second device

The person connects the mailbox on the new device and approves enrollment from an existing device with enrollment authority. The selected pairing experiment uses reciprocal scans of full commitments, with full-value independent comparison as an accessible alternative. The client shows the account and requested permissions before approval; routine users need not inspect cryptographic keys.

The new device generates its own secrets. Exact offer/request commitments, possession proof, the current predecessor and signed enrollment determine what was approved. A changed predecessor requires a fresh approval. A lost response retrieves the original durable result; it does not enroll twice.

The [send-ready pairing contract](identity-lifecycle.md#finish-pairing-with-usable-encrypted-sending) requires the client to continue from QR enrollment through account connection, authenticated contact/security-configuration transfer and automatic encryption preparation. An unchanged contact does not need routine human re-verification on the new device. The interface distinguishes approval committed, enrollment received, account ready and per-contact protected-send readiness. New capability evidence and authorized admission to existing groups remain required and are scheduled automatically. Mailbox login or appearing in a provider's device list does not supply them. Message-history synchronization is separate and is not a prerequisite for future encrypted sending.

Camera scanning, production relay setup and protected history transfer are not demonstrated by the local pairing experiment. The separate [history-transfer contract](history-transfer.md) now defines recipient-specific encrypted history and its source approval; its local experiment does not make it part of pairing automatically. A client must not hide those limitations behind a successful enrollment badge.

### Remove or lose a device

From an authorized surviving device, the person removes the lost device. The client commits the signed revocation, distributes it through the configured authorized paths, stops local release to the revoked target, and performs the required group membership transitions. It preserves affected sends while membership ordering is unresolved. Pending valid membership proposals do not permit continuing to send under the old audience.

The result is future exclusion under the accepted state, not remote erasure. The lost device may retain delivered plaintext, old archive data or already obtained secrets. Offline senders may not yet know the revocation. The client reports the scope of completion rather than claiming instant global removal.

If an administrator, ordering participant or necessary peer is unavailable, use only the selected profile's defined recovery path. A timeout is not permission to invent a new quorum, skip an authorization or switch ordering protocols. The reader keeps accessible history while affected live sends remain held.

### Recover after every authorized device is lost

The first question is whether an existing, previously authorized recovery construction can preserve continuity. The current identity configuration names a recover role but does not define the emergency recovery operation, protected state transfer and conflict resolution needed to use it. That route is therefore unavailable in this baseline; a client must not present it as an implemented password-reset recovery feature.

The defined available route is an explicitly new identity. Explain **This restores your ability to start new protected conversations; it does not recover your previous encryption identity.** The person confirms the continuity break. Established correspondents retain their earlier association and must accept the change through their replacement procedure before using the new principal. Ordinary mailbox access alone cannot enter old groups or recover their history.

If a device with the required current enrollment/delegation authority survives, use enrollment. A surviving send-and-receive-only device cannot authorize its own promotion or a replacement. If administrative devices are only unavailable, wait or use the separately deliberate [new-identity path](identity-lifecycle.md#when-administrative-devices-are-unavailable); a timeout cannot infer permanent loss. If an independently supported recovery extension is later added, its exact authority and history access must be disclosed before enabling it, not invented after loss.

### Reading an archive is a separate operation

The managed restore path imports selected history into an inert historical store and reconnects through fresh authorized enrollment or an explicit new identity. Import does not install old pins, private keys, live MLS checkpoints, queued sends, votes or actions. Opening imported messages cannot replay conversation effects.

To restore a backup, the reader uses its independent unlock material, authenticates the [archive](encrypted-archives.md) and [collection catalog](archive-sets.md), and checks every required part and resource before publishing the historical import. Missing files remain an incomplete restore; neither a cloud listing nor a recent filename proves that a backup contains the unavailable message. Restoring correspondence does not recover the former identity or join a live conversation. Full-client export/import integration remains required; transport forward secrecy does not protect plaintext archives.

For a deliberately approved device-to-device copy, [history transfer](history-transfer.md#carriage-and-file-retrieval) encrypts the request/grant/result controls as well as the selected archive files. Its authenticated import result reports a historical operation, not human reading or future sending readiness. If the return route or recipient key is no longer eligible, the report stays undelivered; the client never exposes its control metadata as a clear email attachment to force completion.

The [post-restore composition procedure](encrypted-archives.md#replying-after-restoration) keeps old actions inert. Current account authority alone does not authenticate an imported reply target. A newly composed message can include deliberately selected history under current audience/disclosure checks; it does not replay an old queued action or automatically continue the old identity.

### Handle changed identity, address or account

An authorized successor follows the selected transition proof and preserves prior attribution. An unrelated new identity claiming a familiar address does not replace or suspend the established association. An actual authorized identity fork holds affected operations and preserves both branches. The client distinguishes these cases rather than showing a generic key-change warning for every unsolicited attachment.

If the person deliberately accepts a new principal, record a continuity break, invalidate queued association decisions and perform fresh admission. Do not relabel old messages as authored by the replacement. A reassigned email address does not entitle its new owner to old history.

Changing the sending account rechecks the local identity, membership, routes and effective policy while retaining the draft. Aliases do not create enrollment authority. A provider password reset changes account access; it does not establish endpoint-key continuity.

### Interruptions and concise explanations

Protection status is a set of facts, not a single lock bit. Retain separately: content encryption, author authentication, address-binding assurance, contribution-wide exposure, delivery outcome and current ability to send. A held future send does not remove the protection of a previously accepted message; an encrypted copy does not hide another copy's exposure.

| Situation | Example concise state | Next available action |
| --- | --- | --- |
| No usable recipient material | Waiting for encryption | Keep draft; obtain a supported introduction or choose an already permitted alternative |
| Verification required by policy | Verify this contact | Use the independent verification path; keep protected send held |
| First-use identity accepted without independent verification | Encrypted, with identity details available | Continue under configured policy; verify independently if desired |
| Valid device change awaiting group admission | Finishing device setup | Resume retained enrollment/admission; do not resend approval blindly |
| Conflicting authorized identity state | Identity change needs attention | Inspect preserved evidence; use an expressly defined resolution |
| Some recipients pending | Sent to some recipients | Inspect per-recipient status; retry only pending authorized copies |
| Hosted bearer copy | Link access | Inspect who may access it and which service processes the content |
| Ordinary copy | Ordinary email | Inspect exposure; no implied endpoint confidentiality |
| All-device loss | Start a new encryption identity | Explain continuity break and unavailable historical recovery before proceeding |
| Archive imported | Imported history | Read inert history; separately establish current sending authority |

These phrases illustrate the required distinctions, not mandatory English strings. Use compact controls with accessible names and details, preserving the [client behavior contract](client-behavior.md). Routine successful transitions do not need repeated confirmation dialogs. Decisions that grant new enrollment, replacement identity, history disclosure or weaker delivery authority must be backed by the corresponding explicit authorization; receipt of a message cannot grant them.

### Mechanism coverage and release gates

“Defined” means the owning chapter specifies a contract. “Local evidence” means selected experiments exist, not deployed interoperability or whole-journey assurance. The gates below must be met before claiming the corresponding journey works end to end.

| Journey step | Precise mechanism owner | Current coverage and release gate |
| --- | --- | --- |
| First-device creation | [Identity genesis](identity-state.md#genesis-and-first-contact), [device credentials](security-profile.md) | Defined experimental records; production account onboarding, endpoint secret storage and runtime trust need joined evaluation |
| Remember policy and prepare copies | [Send plan](delivery-policy.md#remembered-policy-and-the-send-plan) | Defined; integrate the actual composer, account settings and atomic release checks |
| Discover through human email | [Passive carrier and assertions](passive-discovery.md), [mailbox selection](mailbox-association.md) | Local signed/onboarding evidence; real-client carriage, supported mailbox limits and first-contact substitution remain material boundaries |
| Acquire setup before the first human message | [Ordinary-mail request/encrypted response](mailbox-setup.md), [provider bootstrap/publication](bootstrap.md), [local handoff](first-contact-setup.md#finish-setup-for-one-intended-send) | Both carriers have explicit permission, deadline, correlation and failure rules. Record/signature/HPKE/journal components are narrower evidence; actual receive-authentication, account/policy, admission/retirement and first-content release need the complete joined case. A legacy setup notice is possible only on the declared ordinary-mail path. |
| Refresh while both endpoints are available | [Configured provider exchange](provider-control.md), [negotiation lifecycle](provider-negotiation.md) | Local configured HTTPS-to-MLS path; domain discovery/native registration now specified separately; public queue-grant issuance and automatic unknown-peer bootstrap have separate owning wire contracts; their joined implementation and deployed integration remain unfinished |
| Independently verify a correspondent | [Full-value human comparison](mailbox-association.md#optional-human-comparison) | Local strict-delivery integration; real independent-channel usability and accessibility need evaluation |
| Send the first protected contribution | [MLS profile](security-profile.md), [invitations](mls-invitations.md), [release](transport.md) | Local joined admission and delivery; independent clients and account integrations still needed; valid discovery alone is insufficient |
| Start while someone is still joining | [Intended scope and creator resolution](delivery-policy.md#an-invitation-is-not-yet-an-encryption-identity), [pending deliveries and assembly](delivery-policy.md#complete-a-pending-delivery), [logical authored/delivery identity](event-encoding.md#asynchronous-authored-records-and-deliveries) | Current contracts define independently ready deliveries, retained full intended slots, same authored bytes, separate private copies and one logical effect. Candidate codecs, claim ledgers and archive probes remain narrower than complete native admission, durable receiving and final release. |
| Continue offline and after restart | [Group state and delayed mail](group-conversations.md), [transport](transport.md) | Local durable receive, retry and bounded catch-up; deployed synchronization and distributed liveness unproven |
| Add a device | [Pairing](identity-lifecycle.md#pairing-another-device), [own-device synchronization](identity-lifecycle.md#finding-and-synchronizing-your-own-devices) | Local independent stores and signed enrollment; [portable carriage](pairing-transport.md) and [configuration/readiness](paired-configuration.md) are specified, but their complete current-suite implementation, camera and production setup remain unverified; [history transfer](history-transfer.md) is separate |
| Remove a device | [Revocation](identity-lifecycle.md#removal-and-revocation), [membership ordering](group-conversations.md#membership-ordering-over-mail) | Local removal/catch-up evidence; independent stale-state and unavailable-orderer behavior must be exercised |
| Send to mixed recipients | [Per-recipient and exposure rules](delivery-policy.md), [private copies](private-copies.md) | Selected local joined paths; complete mixed-account release and accurate recipient-visible exposure need whole-client tests |
| Offer hosted access | [Bearer protocol](hosted-access.md) | Local joined retrieval/reply; public management authorization is specified; joined account/identity/feed integration, deployment and browser-code trust remain unproven; other hosted models lack bindings |
| Recover all-device loss | [Recovery boundary](identity-state.md#freshness-and-recovery-boundary), [new-identity restore](identity-lifecycle.md#import-history-then-reconnect) | New identity, inert import and the [signed encrypted archive container](encrypted-archives.md) have local evidence; full rich restore and managed storage need integration; emergency continuity recovery is outside the selected initial suite |
| Resolve a competing identity or reassigned address | [Association transitions](mailbox-association.md#state-and-transition-behavior), [identity changes](identity-lifecycle.md#key-transitions) | Defined ordinary transitions and deliberate continuity break; the selected state1 repair requires its actual shared-authorizer proofs and complete implementation; universal ownership verification is not supplied |
| Protect rich/indexed replies | [Rich carrier](rich-messages.md), [reply-content integration](reply-content.md#integration-and-acceptance) | Existing rich path has local evidence; new indexed reply operation has an [exact suite binding](suite-profile.md) and needs its implementation and joined acceptance |

### Acceptance journeys and failure cases

The [whole-client acceptance inventory](acceptance-inventory.md) allocates these journeys across current contract dependencies and module combinations. Each case needs two independently running endpoint stores, retained originals and before/after snapshots of identity, policy, conversation state, queued sends and effects. Independent interoperability additionally requires independently developed implementations. Tests must check visible meaning and actual protected bytes; a badge or successful HTTP response alone is insufficient.

| Case | Exercise | Required outcome |
| --- | --- | --- |
| EJ-01 | Connect a mailbox with no prior endpoint identity | Explicit first-device setup; durable local authority; account login is not reported as correspondent verification |
| EJ-02 | Compose for an unknown recipient under enforced encryption; exercise enabled ordinary-mail setup, provider setup and no usable path | Human content stays private until validated setup, current-suite admission, retirement and final release succeed. Only the chosen authorized content-free carrier runs; no ordinary human-message or hosted fallback under an encryption-required policy. No usable path leaves the draft held. |
| EJ-03 | Exchange human emails under permitted ordinary delivery | At most the selected passive advertisement accompanies each send; no automatic reply loop; earlier messages remain ordinary |
| EJ-04 | Present one eligible unverified identity under each first-contact policy | Record an unverified selection only when policy allows; strict policy holds; no verified-person claim |
| EJ-05 | Present two eligible initial principals in either arrival order | Same ambiguous result; no automatic winner and no premature admission |
| EJ-06 | Forward a signed advertisement, alter a carrier, expire it or use an unsupported mailbox spelling | Retain appropriate evidence; do not infer ownership or install a usable candidate from invalid input |
| EJ-07 | Complete independent comparison, then replay it for a different principal or purpose | Original scope only; no association replacement, enrollment or history grant from replay |
| EJ-08 | Establish MLS with valid evidence, then try an unsupported tuple, consumed package or attempt-only creator receiving key | Select every actual delivery device’s exact ordinary receiving assertion and fixed readable application, retaining other intended slots as pending; reject attempt-key substitution. Valid path delivers exact protected content; invalid paths hold without profile guessing or partial audience. |
| EJ-09 | Keep every recipient device offline past original control/package windows, lose the original keys, then reconnect and restart | Original ciphertext remains unavailable; fresh setup does not decrypt it. Recover only retained history or a separately approved exact delivery-selected historical copy from an independently known source. Unknown source, missing mapping or missing content stays unavailable; no live-state/action replay, presence or read claim. |
| EJ-10 | Interrupt setup handoff before/after local creation, retirement and activation; edit/cancel the pending revision; lose submission response and repeat receive | Recover original checkpoints, planned per-copy contribution/delivery identities and cleanup barriers. An old revision cannot activate; exact retries do not repeat Add/encryption/effects or resend successful copies. Preserve unresolved delivery. |
| EJ-11 | Expire evidence, revoke authority or change association after preparation | Use-time release stops or replans before affected submission; remembered encryption policy survives |
| EJ-12 | Finish or timeout a provider challenge, offer an unconfigured URL, and test a separately enabled mailbox-setup policy | Provider credentials remain bound to the exact authorized service/operation. No diagnostic URL or failure creates authority for another path. A separately enabled mailbox carrier uses its own immutable attempt and disclosure bounds; required masking or verification still holds. |
| EJ-13 | Pair a new device, swap either commitment and lose the approval response | Exact independently approved binding only; mismatch rejected; committed retry returns same result |
| EJ-14 | Log into the mailbox from a new device without enrollment | Mailbox readable as allowed; protected identity, existing groups and old keys not silently inherited |
| EJ-15 | Enroll a valid device without history-transfer authorization | Future readiness follows admission; old history and private keys are not automatically copied |
| EJ-16 | Revoke a device, keep one sender stale and interrupt membership ordering | Current local release stops; stale-state limits disclosed; pending transition does not send to the old audience |
| EJ-17 | Lose every device, or retain only a send/receive device after losing enrollment authority | Unavailable approval waits; deliberately accepted loss offers a new identity with no continuity claim. No mailbox-password or archive override; correspondents retain prior pins |
| EJ-18 | Import old history containing queued actions, revoked state and rich resources; then compose from it | Inert history only; no live rollback or action replay. New sending needs current authority/audience; imported content alone cannot validate an active target or inherit old-author privileges; unsupported archive coverage identified |
| EJ-19 | Send to compatible, ordinary and held recipients, including a private copy; vary independent/collective activation and lose a hosted upload response | Missing setup cannot remove intended slots or silently drop a device from a frozen actual cohort. An independently ready cohort may proceed under the frozen progression policy while other intended slots remain pending. Preserve the complete planned-copy mapping, old disclosure bytes, partial/uncertain outcomes and known or possible host exposure before notification. Only preauthorized conditions select fallback; required protection still holds. No private correlation leakage or duplicate successful copy. |
| EJ-20 | Open, preview, forward and revoke a hosted bearer link | Opening performs no submission; bearer transfer risk is visible; revocation stops future retrieval without promising recall |
| EJ-21 | Add a participant and quote old content in a new audience | Admission and disclosure evaluated separately; no automatic history transfer |
| EJ-22 | Inject an unrelated identity claim, an authorized fork and an actual address reassignment | Three distinct outcomes; no attacker-triggered replacement, arrival-order fork resolution or historical reattribution |
| EJ-23 | Change sending account and protection permission with an unsent reply | Preserve writing and exact target; reevaluate authority and disclosure; no session or policy borrowed from the previous account |
| EJ-24 | Run a browser or hosted deployment with operator-accessible keys or replaceable code | Claims match actual endpoint/runtime trust; local encryption is not automatically described as provider-blind |
| EJ-25 | Restore an older application snapshot after revocation | Do not claim rollback resistance from ordinary transaction tests; unproven whole-machine rollback protection remains a release limitation |
| EJ-26 | Read malformed protected content or lose an embedded resource | Preserve the original and safe diagnostics. Required carrier/operation failure prevents activation; a resource or later rendering failure alone preserves accepted meaning and independently valid effects under the owning failure matrix. Never fetch an unprotected replacement or weaken security. |
| EJ-27 | Send an indexed reply under an older immutable application tuple | Unsupported operation held; no widening of that tuple; valid new binding must be tested separately |
| EJ-28 | Turn off the network during routine reply, pairing, revocation and hosted submission | Preserve draft or exact pending transaction; show the operation-specific outcome; reconnect never repeats a completed effect or grants weaker authority |

### What must be settled before the baseline is frozen

The current baseline selects its protocol bindings. The remaining gates below concern complete implementation, appropriate acceptance and external evaluation; they do not imply that missing production adapters are unspecified protocol mechanisms. Newly found internal contradictions still require correction in their owning chapters.

The [required conversation suite](suite-profile.md) defines the exact joined profile, including indexed replies. Its implementation and acceptance run through real accounts remain required. Public provider onboarding is a separate path, not a prerequisite for passive human-email introduction or explicitly enabled [ordinary-mail setup](mailbox-setup.md). Universal first-message protection is not implied: the selected recipient path, current evidence, authority and policy must actually permit completion.

Recovery has an explicit protocol boundary: eligible surviving-device enrollment, or a separately chosen new identity when usable enrollment authority is lost. The [archive profile](encrypted-archives.md) defines historical recovery and still needs full client integration. The initial suite deliberately offers no emergency identity override; any future continuity-preserving recovery protocol needs separate definition and evaluation. The absence of those features must be explained during setup, before someone relies on recoverability.

Finally, test whether ordinary people can complete first contact, interpret an unverified encrypted identity, add a device and understand total loss without learning key terminology. Protocol fixtures establish mechanisms; usability studies, native accessibility checks, independent security review and real-provider trials establish whether the joined experience is usable and dependable.


:::


## Sending from another enrolled device

Another approved device can send using its own keys without first copying your old messages. The app handles the setup and shows any remaining wait.

::: {.details summary="Sending streams, confidential setup and administrator conflicts"}

For an ordinary protected conversation, the [sending-stream contract](suite-profile.md#ordinary-protected-conversations) lets an enrolled device establish its own fresh stream using current valid public setup for the selected recipients. It does not wait for their ordering votes, copy another device's live state or download old correspondence. Missing required setup still holds delivery. Exact reply references require their retained evidence; without it, a device can compose a new root contribution.

Each stream keeps its exact owner and membership evidence. Current revocation, recipient repair and key-retention rules still apply. Managed groups keep their distinct shared membership/ordering procedure. A new ordinary stream is not a way to bypass a managed-group hold or acquire its history.


Invitations, updates and setup responses are confidential too: the sender [seals those controls](suite-profile.md#confidential-setup-and-control) for the intended device before mail transport. The receiver decrypts and checks the original signatures and identity/recipient evidence before joining or changing state. The initial public [mailbox request](mailbox-setup.md) is the explicitly enabled exception; it contains no human writing and cannot satisfy required address masking. Missing material waits; a relay, decryption success or SMTP acceptance is not proof that setup completed.


### When two administrator devices update at once

The client can pause affected activity to reconcile conflicting account updates. It preserves all revocations and collects the required surviving administrators' approvals for one exact repaired roster. Same-key renewal does not require arbitrarily choosing one device's longer expiry. Missing approvals remain visible; a timeout cannot restore a revoked administrator. The [state1 lifecycle](identity-state.md#concurrent-administration-and-retirement) defines proof collection, installation, explicit cleanup and the new-identity outcome when no qualifying authority survives. Repaired identity, refreshed delivery permission, submitted content and read history remain separate outcomes.

:::

Continue with [delivery choices when someone is not ready](delivery-policy.md#per-recipient-outcomes). For implementation, use [client behavior](client-behavior.md), the [adoption paths](adoption.md), or the [architecture and acceptance cases above](#architecture-and-implementation).
