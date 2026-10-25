---
title: Delivery protection and fallback
order: 12
blurb: encrypted delivery · ordinary copies · hosted access
sectionNav: true
navGroup: guide
---

# Delivery protection and fallback

The sender decides what should happen when someone cannot receive an encrypted contribution: send ordinary email, offer access through a hosted page, or hold delivery until a compatible endpoint is available. A client can remember that choice so routine sending does not require repeated dialogs.

> [!ex] Bob can decrypt; Carol cannot
> Alice sends one answer to Bob and Carol. If she permits ordinary email, Bob can receive an encrypted copy and Carol a readable ordinary copy. Alice's history shows that mixed protection. If Alice requires encrypted endpoints for both, the app waits for the setup required by each planned protected copy. A ready, separately authorized copy can proceed while another waits; the app cannot silently remove Carol from a shared protected audience.
>
> A hosted link is a third choice with its own access rules. Failure to encrypt does not automatically authorize either fallback.

The policy applies to this contribution and its intended audience. An encrypted copy does not make every other copy confidential.

The [encryption journey](encryption-journey.md) applies these permissions to first contact, mixed recipients, device changes and recovery without requiring repeated routine decisions.

The [module framework](modules.md) also treats content encryption, sender masking, recipient masking and identity verification independently. Remembered address-privacy requirements can hold an otherwise encrypted copy; permitted automatic upgrades select newly available protection without asking the person to edit addresses. The [swap sequence](private-routing.md#when-the-addresses-change) defines the exact composition, encryption, outer origination and receive-display boundaries.

## Per-recipient outcomes

| Effective permission | Compatible authenticated endpoint available | No compatible endpoint available |
| --- | --- | --- |
| Require encrypted endpoint | Encrypt using the selected profile | Hold that delivery and show what capability or identity evidence is missing |
| Permit ordinary copy | Prefer protected delivery where supported | Send readable ordinary email under the remembered permission |
| Permit hosted access | Prefer protected delivery where supported | Use the approved hosted service and explicitly identified access model |

A permission to send an ordinary copy does not authorize publishing it at a new hosted service. A permission to use hosted access does not authorize a plaintext attachment after that service fails. The sender may explicitly permit more than one fallback; their order must be part of the effective policy.

Under the retained mail-conversation-v1 copy contract, the sender may deliver an independently ready, authorized copy while another remains pending. The sent record distinguishes partial progress from delivery to everyone. An exact retry within an unchanged copy retains its original contribution, audience and prepared bytes; a newly scoped contribution for a different protected audience has its own identity. Neither path resends successful copies merely because another is waiting.

If a recipient's identity evidence changes after planning but before submission, re-evaluate that recipient. A transport failure does not by itself justify a weaker mode. Once a copy has been accepted for delivery, switching mode is an additional disclosure, not cancellation of the earlier copy.

## A waiting delivery is different from missing setup

The following frozen-copy planning rules retain the v1 contract and its shared transport/exposure safeguards. The current asynchronous agreement below uses its own intended-slot plan and actual delivery cohorts to retain one common authored message. A selected actual preparation still cannot omit a required device to hide a failed check.

When a complete protected copy is ready, delivery to one mailbox can proceed while another mailbox temporarily fails. Both deliveries still carry the same authorized copy. When someone’s required encryption setup is missing, the client cannot create that shared protected copy by leaving them out.

> [!ex] Why a copy is waiting
> Bob and Carol are both admitted to the same protected copy. Bob’s server accepts it; Carol’s server temporarily refuses it. The client keeps Carol’s original delivery pending without sending Bob another message.
>
> If Carol has no usable setup yet, a copy whose protected audience includes her is not ready. Alice can wait, or use a separately authorized copy plan with independent contribution identities. That split does not create one shared question/answer state across the copies.

::: {.details summary="Frozen copies, progression policy and aggregate outcomes"}

### Freeze the exact copy plan

Use the [setup handoff](first-contact-setup.md#finish-setup-for-one-intended-send) to bind one local intent revision to its full planned copy/contribution/delivery mapping. A protected copy fixes its actual intended principals/devices, conversation/context, author, application, content/resources, disclosure projection and exact preparation. Every selected device’s setup and authority must satisfy that copy’s owning rules. A network-ready mailbox is not enough.

A partial transport result changes the outcome for the original delivery/recipient; it does not change the copy. Missing intended device evidence, an incompatible operation, incomplete roster or unavailable required address protection holds the entire affected protected preparation. Do not synthesize a smaller audience, reuse a group without the missing member or declare a recipient compatible from another person’s evidence.

A policy may authorize separate audiences. Then prepare independent copies under their actual contracts, including fresh contribution/context/resource/mail identities where required by [private copies](private-copies.md#separate-conversations-separate-authority) or the [event namespace](event-identifiers.md). Locally correlate their outcomes through the private send plan. Do not merge question/answer, reaction or reply authority across those contributions merely because their wording or subject matches. An explicitly authorized established-membership change has its own admission and contribution rules; it is not an exact retry of a differently scoped event.

### Choose how ready copies progress

The effective local policy selects and retains one of the following behaviors for the frozen activation cohort. These are local planning semantics, not new wire fields, a universal default or a promise of atomic remote delivery.

| Progression | Required behavior |
| --- | --- |
| Independent copies | A ready copy may progress after its own authority, disclosure, retirement and release checks. Another copy remains pending with its own original result. |
| Wait for the selected copies together | Before their first activation, every copy in the retained cohort must pass its preparation/retirement/dependency gates. Activate them through a coordinated local transaction or equivalent protocol. Missing/held copies prevent claiming that collective barrier succeeded. |

The cohort is the exact retained selected set, not whichever rows happen to be ready now. A restart cannot replace it with the surviving subset. A later policy change uses a new authorized local revision/cohort and preserves the earlier copies’ bytes, identities and results. It does not reactivate already handed-off copies.

Collective activation controls local release eligibility. It cannot make SMTP acceptance, host storage or recipient admission simultaneous. Current checks still apply immediately before each actual release. A new hold can stop an unreleased copy after others crossed their boundaries; preserve and display that partial result. Cancellation cannot recall another copy or undo a host’s access to content.

A hosted copy’s content-release boundary includes uploading plaintext or decryption-capable material, not merely sending its link notification. A policy that waits for copies together must gate that upload as well. Creating a grant with content is already exposure even when every notification later fails.

Once an upload releases content or decryption-capable material, a lost response leaves possible exposure even without a grant receipt. A rejected notification, absent grant record or negative creation result is not proof that the host never received the submitted bytes. Content-free acquisition/preparation retains its separately authorized metadata boundaries; it is not evidence that the human message was sent.

### Aggregate only a complete, consistent local snapshot

Derive the local summary from the frozen planned-copy inventory and each copy’s retained delivery/recipient evidence. Missing rows, incomplete processing, conflicts or unavailable provenance yield an explicit incomplete/held view; they are not empty successful copies. Preserve the exact account, intent/revision, copy, contribution, delivery and attempt scope. These local identifiers and counts never become a public Bcc manifest.

| Evidence | Permitted summary |
| --- | --- |
| Some selected deliveries have confirmed handoff; others are pending/held | Partial progress, with the remaining scope/reason available |
| Any relevant attempt is uncertain | Preserve that uncertainty even if another attempt/copy has accepted evidence; do not automatically resend it |
| Every selected delivery has matching handoff evidence and no unresolved outcome/conflict | Handoff confirmed for the planned set; still not recipient decryption, application acceptance or human reading |
| A later correlated failure qualifies an accepted delivery | Keep both the earlier handoff and the later failure; do not erase another copy’s result |
| A hosted grant exists but notification is pending or failed | Content exposed to that host under its access model; notification outcome separate |
| Content upload started but its result is unknown | Possible host exposure, with the original upload/operation uncertainty retained; failed notification or missing receipt cannot establish confidentiality |

Keep readiness, transport observations, hosted effects and content exposure as separate axes. An accepted copy can later have a revoked dependency; its historical acceptance remains true while new release is held. A prior uncertain attempt does not disappear because a retry was accepted. No aggregate check may allocate a new attempt, switch mode, replace a contribution or silently retry an uncertain effect. The owning transport/action contracts decide any explicit reconciliation or retry.

:::

## Start a group while invitees are pending

People must be able to begin a group conversation before every intended participant has completed secure setup. Show the invited people and their pending delivery state; let eligible recipients receive independently. Do not silently remove a pending person from the intended discussion or claim that everyone received the message.

One authored message can need separately secured deliveries at different times. The conversation view needs an authenticated connection between those deliveries, not a guess from matching subjects, dates or quoted text. A later delivery must not create another visible message for someone who already received it, and a retry must not resend successful deliveries merely because another person is still pending.

> [!note] Selected asynchronous agreement
> The [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) binds one authored message to separately authenticated deliveries. The [pending-delivery lifecycle](#complete-a-pending-delivery) below defines their continuation, cancellation and assembly. These are the current `mail-conversation-v2` contracts. They do not enable these semantics in retained v1 or earlier copies; independently scoped old-format records cannot be merged by guesswork. Complete current implementation remains separate from the selected design.

Pending delivery is distinct from a new participant joining later. A person originally intended to receive a message may have that exact message queued for completion under its original scope and current eligibility checks. Adding a new person is a new disclosure decision; it must not automatically release earlier conversation history. The same rule applies when composing a reply to a legacy chain: [limit the readable body to the response and its immediate parent](messages.md#replying-to-a-legacy-chain-without-carrying-its-history), omit the parent's older chain, and reassess copied passages and resources when the audience or protection changes. The final binding must preserve that distinction across restart, cancellation, changed addresses or identities, expiry and uncertain submission.

Private follow-ups and blind copies retain their separate disclosure boundaries. A common identifier must not reveal their existence or link them to the visible group. A lock on one delivered copy cannot imply that every pending recipient is ready or that all other copies have the same protection.

### One message, several deliveries

Alice invites Bob and Carol. Bob is ready; Carol is still setting up. Bob receives Alice’s question and answers it. Later, Carol’s client receives both contributions, possibly in reverse order. It keeps the answer’s parent unresolved until Alice’s question arrives, then displays one question and its answer. It does not need a transcript copied into either email.

| Object | What stays the same |
| --- | --- |
| Authored message | Its author, logical identity, exact original content, resource commitments and intended visible discussion. |
| Secured delivery | Its actual admitted recipients and devices, protection context, prepared bytes and delivery identity. Another recipient may need a different delivery of the same authored message. |
| Transport attempt | It retries that delivery’s frozen preparation; it does not create another message or repeat a successful recipient’s delivery. |

These objects use the selected [authored-record and delivery-envelope components](event-encoding.md#asynchronous-authored-records-and-deliveries), with the complete negotiated native and carrier binding in the asynchronous agreement. They do not change the current envelope’s schema or authorize advertising an incomplete implementation.

::: {.details summary="Authorship, logical references and deterministic assembly"}

**Each delivery proves authorship.** The selected construction uses the owning native application authentication over the entire shared authored record and its delivery binding. In the MLS binding, use the processed sender’s actual epoch credential and key, accepted device-to-principal authority, and complete application/context validation. Require the authenticated publishing principal to equal the logical author principal. Carrying a copy of an old signature, a matching digest, a recognizable From address or another participant’s valid MLS sender is insufficient.

No separate reusable application-signature token or new signing key is selected for this construction. The selected envelope6 carries the complete original authored record inside the native-authenticated mime-suite-v2 application content. This rule preserves empty MLS authenticated_data and does not insert fields into envelope5.

**A new device can deliver the same retained message.** Another currently authorized device of the same author may prepare a late delivery using the identical original authored record. It must possess that content and independently eligible pending-send/disclosure authority. It does not take over another device’s ordinary stream or obtain its keys. Use its own eligible stream/admission, or the independently authorized managed-group path. A changed principal cannot continue the old author’s logical namespace. Pairing metadata and correspondence archives do not restore an active outbox.

**References identify the authored contribution.** A reply, quotation source, answer, reaction or correction under this binding targets the logical author, conversation and message identity, rather than an arrival-selected secured delivery. Delivery IDs identify actual receipt and retry evidence. A reference does not grant access to missing content, authorize a different audience or make a pending invitee an admitted native member. The asynchronous agreement selects these exact operation/reference schemas; older EventReference fields retain their owning meanings.

**Assembly is independent of arrival order.** Apply this procedure only after complete native, author, scope, operation and resource-binding acceptance; a sender-supplied flag cannot manufacture that boundary.

1. Look up the authored principal and logical message identity in the durable local namespace, including records retained under other conversations.
2. Identical original authored-record bytes and committed meaning identify one message. Retain each delivery’s authentication, actual audience and outcome as separate provenance. Another valid device attestation or ciphertext does not create a second message or repeat an effect.
3. Different authenticated authored records under that same identity are conflicts, including reuse in another conversation. Retain the variants, invalidate affected derived relationships and hold new dependent effects. Do not choose by arrival order, date or device. An unauthenticated claim cannot poison the namespace.
4. Resolve a relationship only through its exact logical target and independently accepted source permission. A missing target remains pending. A conflicted or forbidden target remains explicitly unresolved or rejected; matching words cannot supply it. Construct the permission-checked graph before cycle processing.
5. Atomically retain the accepted authored record, original authentication/delivery evidence and replay facts with its effect or durable pending dependency. Restart and duplicate deliveries must not create another answer, reaction or action submission.

This local transaction does not make remote HTTP effects atomic. Service operations retain their own original operation identities and uncertainty rules. A new delivery of a question or receipt cannot repeat an accepted or uncertain service submission.

Private and blind copies use independently scoped logical identities and representations. This common visible-discussion namespace must not export hidden membership, private reply activity, copy counts or links to another disclosure scope. A recipient’s assembled view describes only its own authorized available content; it cannot claim that every other participant has the same history.

:::

### An invitation is not yet an encryption identity

A pending person has a stable place in the invitation, called a **recipient slot**. That slot names the selected mailbox and, when already known, the expected principal. It does not pretend that the person has joined an encrypted group.

The invitation’s author resolves an unknown slot. Alice can authenticate Carol’s principal after secure setup and communicate that binding to Bob. Bob separately checks Carol’s current identity, capabilities and his own permission to send. Alice’s confirmation cannot weaken Bob’s protection policy or give him access to Carol’s keys.

Bob can send his reply to ready participants while retaining Carol’s delivery as pending. If Alice has not yet authenticated Carol’s binding, Bob cannot complete that particular delivery merely because he found an account at a similarly named address. This is a dependency of the unresolved invitation, not a barrier to starting the discussion.

::: {.details summary="Intended-recipient scope and resolution record"}

The following version0 components are selected for the complete asynchronous agreement under D-43. They use the current complete envelope6/native/carrier binding. They are not optional extra fields in envelope5 or an enabled operation in mail-conversation-v1. Missing negotiation must hold these semantics rather than silently discard them.

**Scope identity.** One newly authored root defines an intended-recipient scope. Its identity is that root’s full logical reference: author principal, conversation and logical event. A logical reference has exactly the string members `principal`, `conversation` and `event`, under their existing identifier grammars. Under the successor binding, the event names the authored message, not a secured-delivery event. Current EventReference processing is unchanged until that complete agreement is selected.

**Scope definition.** The object has exactly these required members. Common strict UTF-8/JSON, duplicate-name, byte/depth and unknown-member rules apply; no number, null or optional extension is admitted.

| Member | Requirement |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"intended-recipients"`. |
| `root` | The exact logical reference of the enclosing authored root. Its principal is the scope creator. The root cannot create a scope attributed to someone else. |
| `author` | The slot ID for the root author, present in `slots`. |
| `slots` | Nonempty array of slot objects, uniquely ordered by slot ID in ascending ASCII order. |

Each slot object has exactly three members:

| Member | Requirement |
| --- | --- |
| `slot` | Nonzero lowercase 128-bit ObjectId. Unique within this scope; its namespace includes the full scope root. |
| `mailbox` | One canonical bare mailbox under the [mailbox-address contract](mailbox-addresses.md). Compare decoded canonical values exactly; no alias guessing, local-part normalization or visual matching. Each mailbox occurs once in the scope. |
| `expected` | An array containing zero or one valid principal string. Empty means the creator has not bound this slot’s principal. One entry fixes that expected principal. The author slot contains exactly the root principal. |

The creator must preserve already selected identity expectations and existing pins when preparing the scope; clearing a known principal to obtain an apparently unresolved invitation is not a permitted repair. Several separately selected mailbox slots may concern the same principal, but no slot or address alone grants a route, native membership or role. Root and slot identifiers are fresh within their owning namespaces and retained across every exact delivery/retry.

The [per-message protected addresses](event-encoding.md#asynchronous-authored-records-and-deliveries) select actual personal To/Cc mailboxes for that contribution. A bound person’s current eligible alias can differ from the invitation mailbox; that choice neither changes the principal nor lets another author resolve an unknown slot. Scope metadata alone does not route mail.

The root’s complete authored bytes commit this definition. A later resolution does not fill in or rewrite its empty expected array. A changed definition under the same authored root is a message conflict. A deliberately revised invitation uses a fresh root/scope and its own disclosure/admission decisions; it cannot replay an earlier uncertain delivery as a new send.

**Resolution operation.** A recipient-resolution operation has exactly `kind`, `scope`, `slot` and `principal`. `kind` is `"recipient-resolution"`; `scope` is the exact scope-root logical reference; `slot` names a slot in its independently accepted definition; `principal` is one valid principal. It is a control effect: it does not produce a visible conversation message, written-reply affordance, answer submission or implied acknowledgement. The successor agreement must select it explicitly as a required operation and bind its complete authenticated carrier. Recognizing this shape cannot enable it in an older dispatcher.

The operation’s actual authenticated publishing principal must equal the scope creator. Any independently eligible device of that principal can publish it; no primary device or additional administrator role is invented. Ordinary sending authority, accepted device evidence, source account, confidential carrier, disclosure permission and current release checks remain required. The creator must independently validate the selected mailbox-to-principal association before publishing. Discovery success alone cannot supply that authority.

A successor root delivery may instead supply resolution through its explicitly authenticated slot-to-actual-principal map, when its native sender is the scope creator and the full root/scope is accepted. The mapping must be an explicit part of the completed delivery binding. Membership in a native roster, receipt at a mailbox or an inferred To address does not supply it. A replying author’s map cannot resolve someone else’s scope.

For each slot, retain the expected principal and every valid creator resolution in a durable scope-local binding ledger. Matching values are repeated evidence of one binding, not new invitations. Different valid values are a binding conflict: retain the variants, hold affected new disclosure and derived group relationships, and do not select a device, arrival-order or date winner. An unauthenticated resolution cannot reserve the slot or poison accepted state. A missing definition remains a pending dependency and cannot activate the control effect.

Commit the first local binding and dependent pending-send facts before releasing content that relies on it. Concurrent creator devices can produce contradictory authenticated evidence; receivers detect and retain that conflict rather than claiming a distributed first-writer guarantee. Previously recorded transport or service outcomes remain historical facts and cannot be undone by discovering conflict.

An initially unknown slot is a mailbox claim. Its first eligible resolution supplies the selected first-contact assurance, not proof of a particular human identity or that the mailbox never changed owner while waiting. Retained reassignment, pin or continuity conflicts still hold release; absence of that evidence is not proof that no change occurred.

A previously accepted binding identifies the intended principal; it is not a perpetual device credential, current mailbox-association proof, subscription, native admission or history grant. Before every new delivery, recheck current identity, address association, key/capability, native context and disclosure authority. A key change within eligible continuing identity does not change the slot. A different principal, account reassignment, identity conflict or unmet verification requirement holds the pending delivery. It cannot overwrite the binding. A newly received stale creator proof still follows the owning current-authority acceptance rules; it does not acquire a trusted historical signing time.

:::

### Invited people and reply recipients are different sets

The scope provides stable names for the original invitation. Each authored message separately selects the slots actually intended to receive that contribution, its To/Cc roles and its explicit discussion-reply set. A Cc slot outside that discussion set is not added to later replies. The reply’s intended slots must equal its accepted source’s declared discussion slots; actual secured deliveries may cover eligible subsets of that intended set while the rest remain pending.

A discussion continuation keeps the exact scope root and slot definitions. Its author must be independently bound to its selected author slot. A reference to the scope cannot change that binding, add a person or convert a copied observer into a discussion participant. A recipient without the independently accepted root/resolution evidence can retain valid incoming authored content while its claimed discussion relationship remains pending. The person must not be shown a falsely verified group relationship merely because another sender supplied a familiar roster.

Show the selected recipients for the contribution being read or composed, rather than presenting every slot in the original invitation as a current recipient. Preserve To/Cc choices. Do not turn a recipient into To, move them to Cc, choose a different mailbox, or widen a reply merely to make a principal-role projection fit a carrier. Hold the affected preparation or obtain an independently authorized new composition revision, preserving earlier deliveries and uncertainty.

Only the sender’s own complete delivery ledger can establish which of its planned deliveries remain pending. A recipient may know that Carol is absent from its actual cryptographic copy; it cannot infer that she is offline, unconfigured, excluded from every other copy or awaiting delivery everywhere. A scope entry is invitation evidence, not a public presence or delivery-status feed.

Private replies and Bcc copies create independently scoped roots and slot identities. They do not reuse the visible scope root, export its roster or report private activity into its delivery ledger. Adding someone later likewise requires a deliberately new scope and the applicable context/disclosure choices; a newly admitted device or a matching mailbox cannot make that person an originally pending recipient.

## Complete a pending delivery

A pending recipient can receive the original message later, after their setup succeeds. The sender keeps that message and its remaining delivery work; it does not rebuild the message from the conversation on screen. People who already received it do not receive a new message just because somebody else becomes ready.

This continuation has limits. Stopping the remaining work cannot recall sent copies. A changed identity or a newly enlarged encryption group can make a late copy unsafe. The client must explain the hold rather than silently share old content with new people.

> [!ex] Carol becomes ready later
> Alice’s question and Bob’s answer each retain their own pending delivery to Carol. Alice’s setup confirmation can resolve Carol’s invitation slot, but Bob still needs his own permission and secure setup to send his answer. Carol may receive the answer first. Her client retains its missing-parent relationship, then joins it to the question when that arrives. Repeated deliveries add receipt evidence, not another question or answer.

::: {.details summary="Retained send authority, retries, expiry and cancellation"}

### Retain the message and the remaining obligations

These requirements apply to the selected asynchronous agreement. They are local lifecycle rules, not additional wire fields or operations.

Before preparing a delivery, retain the authorized source account and intent revision, complete original authored-record and resource bytes, selected protection/disclosure and progression policy, intended recipient slots and per-message mailboxes, and every remaining delivery obligation. Retain any chosen release deadline. A digest, rendered transcript or reconstructed JSON record cannot replace the original bytes. Configuration transfers and correspondence archives do not restore an active outbox or its authority.

An obligation names a selected slot and its frozen personal mailbox, not just a principal. Two addressed aliases of the same principal remain separate delivery obligations even though the native audience deduplicates that principal. One prepared copy may cover several obligations only when its actual slot map, audience and carrier permit them. Keep each envelope recipient’s transport result. Including the author’s slot in the authenticated map does not itself request an SMTP copy to the author.

Keep the following facts separately:

| Fact | What it establishes |
| --- | --- |
| Accepted invitation binding | Which principal owns the slot; not current setup or permission to send |
| Current selected device cohort | Which devices must pass admission and preparation checks for this copy |
| Prepared delivery | Exact bytes, actual audience, dependencies and retirement/release state |
| Transport observation | A result for this delivery, attempt and envelope-recipient scope |
| Remaining obligation | Work still authorized under the retained logical intent |

Missing rows cannot mean success. A device joining a principal does not automatically create an obligation to backfill already completed messages. A new pending preparation may select currently eligible devices under the retained policy; it cannot silently remove a failed device from an already frozen preparation.

### Recheck authority before preparing or releasing

Resolve an unknown slot only through the scope creator’s accepted binding. For each late preparation, independently check the author’s current device authority, original source account, slot binding and selected mailbox association, recipient setup, native context, routes, protection/disclosure permission and live send intent. Another author’s successful setup or resolution cannot authorize this author’s content release.

Use the identical original authored record and committed resources, with a fresh delivery identity for a new preparation. A different authorized device of the same principal needs both those bytes and independently eligible pending-send authority. Another participant cannot republish the message as its author. If no eligible author device retains them, keep the work held; do not reconstruct or delegate authorship. An already prepared copy remains subject to its own release checks.

Apply the [transactional preparation and final release rules](transport.md#local-authorization-and-release): commit advanced native state with exact ciphertext; satisfy secret retirement; serialize current dependencies and worker ownership; and recheck immediately before body release. A restart cannot roll back native state, forget possible exposure or treat a lease timeout as proof that an old worker stopped transmitting.

### Retry a delivery or prepare its replacement

An exact retry retains the original delivery identity, prepared representation and dependencies. It may address only eligible, unfulfilled envelope recipients from that preparation. Do not resend recipients with confirmed handoff merely because another recipient is pending. An uncertain result follows the transport reconciliation rules rather than becoming an automatically unsent job.

Changing the preparation’s actual audience, slot map, publishing device, native epoch, resource representation, sender-prepared carrier bytes or opaque destination requires a newly authorized preparation with a fresh delivery identity and the appropriate fresh prepared Message-ID. Preserve the original authored bytes when this is still the same logical message. Retain the relationship to the replaced delivery, including all earlier uncertainty and exposure; a replacement cannot reset those facts or create another human action. A connection or service-discovery refresh that leaves the authorized preparation and envelope destinations unchanged need not create a new delivery. Relay-added trace fields do not rewrite the sender’s authored record.

A newly observed epoch does not itself rewrite a frozen delivery. The owning native and transport checks decide whether its original ciphertext remains eligible or must be held; only an independently authorized replacement changes its prepared epoch. Confirmed server handoff is not an invitation to submit a replacement. Where reconciliation permits a new delivery after an uncertain attempt, the receiver may encounter both: common authored-record deduplication remains mandatory.

### Do not widen a managed group to complete an old message

Suppose Alice intended her message for Alice, Bob and Carol. Before Carol becomes ready, Dave joins the managed native group. A delivery encrypted to a native audience that includes Dave would disclose the old message to someone outside its intended slots. Omitting Dave from the envelope’s declared audience cannot hide his actual access. Hold that preparation.

Do not silently change the conversation’s managed mode, invent a different group genesis or use an ordinary stream to bypass its governance. A later eligible native context may permit the original pending delivery. Otherwise a new composition or independently authorized history disclosure must follow its own contract. Adding a participant never authorizes old history by itself.

### Expiry and stopping remaining work

A setup request’s expiry and a human message’s release deadline are different. Expiring one setup attempt does not change the message or renew its permission; another bounded, authorized setup attempt may serve the still-live intent. New setup never extends a sender-selected release deadline. This contract sets no universal message lifetime: every late preparation still needs current material and retained authority, and implementations may stop work under their disclosed retention policy. Losing the retained bytes or authority leaves an explicit hold, not permission to recreate them.

Stopping remaining work changes the author’s local intent generation and blocks further unreleased jobs under it. Preserve completed and uncertain attempts, native state advances, delivery identities and replay/conflict records. Stopping Alice’s remaining copy does not revoke Carol’s invitation, cancel Bob’s independently authorized answer, recall received content or remove somebody else’s history. This agreement defines no global invitation-cancellation operation.

Editing text after partial delivery cannot replace the original bytes under the old logical identity. If the authorized edit choice stops pending original copies, retain that stop and apply the edit’s own new-event and dependency rules. Do not silently deliver old text merely to make an edit applicable, or claim a replacement was validated without its required target. Likewise, stopping a reaction’s local delivery is not a remote withdrawal; an accepted reaction uses the separate withdrawal operation.

### Commit assembly and effects once

After complete native, author, scope, operation, reference and resource acceptance, atomically retain the original authored record and its namespace decision, delivery/replay evidence, and either its local effect or durable pending dependency. Apply the [two typed namespace ledgers](event-identifiers.md#keep-delivery-identity-separate-from-message-identity) in that same transaction; do not deduplicate by delivery key before checking independently validated authored bytes. Identical authenticated authored bytes add provenance. Different authenticated bytes under the same author and logical identity are conflicts, including across conversations; unauthenticated claims cannot reserve that namespace.

An accepted scope definition from own-device metadata can enable fresh composition without the old human root. It does not supply missing quoted content, question, reply permission or action target. Keep those exact dependencies pending rather than guessing them from a transcript.

Another secured delivery, history import or restart must not repeat an answer, reaction or service submission. Remote HTTP effects retain their original operation identity, retry and uncertainty contract; a local transaction cannot make them atomic with mailbox receipt.

Derive sender progress from the complete frozen obligation inventory and every linked delivery/recipient outcome. Preserve partial progress, stopped work and possible exposure. A recipient can report only its own accepted content and evidence, not everybody else’s history or readiness. Private and blind copies keep independent identities and cannot export hidden obligations or correlation into this visible scope.

:::

## Contribution-wide exposure

A client must distinguish **“this copy was encrypted”** from **“every copy was encrypted.”** If Alice permits an ordinary copy for Carol, the contribution MUST NOT be labeled “end-to-end encrypted for everyone,” even though Bob's copy is encrypted.

The sender's history shows mixed protection and distinguishes protected copies, ordinary copies authorized, hosted access authorized and pending deliveries. An upgraded recipient's authenticated contribution metadata MUST indicate an intentional disclosure outside endpoint encryption, without revealing hidden recipient identities or counts. The exact encoding belongs in the message profile. A recipient reports only the evidence it possesses; successful decryption cannot prove that no other disclosure occurred.

Plaintext exposure is not reversed by later encryption. Removing someone from a later reply does not remove their earlier copies. Quoted history enters the new reply only when deliberately selected, with its exposure evaluated for the new audience.

A readable fallback can disclose more than the new operation itself. An answer may repeat a question and its selected label; a reaction may carry a reference to an earlier message. The sender's effective permission must cover those exact copied fields for the actual recipients. Prior access by the protected group does not authorize disclosure to someone outside it. The same rule applies to structured alternatives and metadata, including audience identifiers; hiding a field from the visible body does not make it private.

> [!ex] Answering does not automatically share the question
> Bob selects “Friday” in Alice's protected question. If his ordinary copy to Carol would include Alice's question text, his client must evaluate that text as part of the disclosure. Remembered permission can cover it; otherwise the copy waits. The client does not append the rest of Alice's conversation.

Readable alternatives of a protected copy belong inside its protection envelope. A plaintext alternative beside ciphertext in the same message would expose the content and MUST NOT be used as compatibility fallback. Hosted access must likewise identify who can read the content; a bearer link does not establish endpoint-only encryption.

:::: {.details summary="Why this differs from existing encrypted-email guidance"}

### Mixed delivery and the message's confidentiality status

[RFC9787 Section 3.2](https://www.rfc-editor.org/rfc/rfc9787.html#section-3.2) recommends avoiding copies of one message with different end-to-end protection. Email/2 deliberately permits sender-selected fallbacks for incremental adoption. This is a scoped departure from that recommendation, not a claim that mixed delivery provides uniform confidentiality.

[Section 9.6](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.6) explains the downstream problem: a recipient who receives an encrypted copy may assume that a reply to everyone can also be encrypted. Email/2 makes the fallback permission explicit and carries the contribution's broader disclosure status to upgraded recipients. It also composes replies as new contributions, without automatically quoting earlier content. This permits gradual adoption while retaining encryption on compatible deliveries. It does not recover confidentiality lost through an ordinary copy, and a legacy recipient may not understand the structured disclosure indication.

A reply therefore gets its own recipient plan. The original sender's fallback permission is not permission on behalf of the replying person. If that person's effective policy requires encryption, an unavailable recipient remains pending; receipt of a mixed-protection message does not weaken that policy. Deliberately including earlier protected content still requires evaluating its disclosure to the new audience.

Before sending, the interface MUST distinguish endpoint-encrypted delivery, provider-hosted access and ordinary plaintext delivery in the recipient plan. A local lock icon cannot replace the authenticated disclosure indication required above. If any copy is plaintext, the contribution MUST NOT be summarized as confidential to the encrypted recipients. The interface may describe that particular copy as encrypted alongside the broader disclosure status.

These permissions do not authorize weakening an enforced-encryption plan or disclosing an earlier protected message in a reply.

::::

## Freeze disclosure before releasing content

A protected copy describes the sharing its author planned when that copy was prepared. That statement is part of its immutable authenticated bytes. It cannot be rewritten later because another route failed or a broader fallback was selected.

::: {.details summary="Planned fallbacks, new exposure and immutable events"}

The effective plan names the exact reachable fallback modes/services/access models selected for each copy. Remembered permission may select them without a repeated dialog; a broad preference alone is not a prepared copy or a hosted grant. Before any selected content release, each affected protected contribution includes the applicable existing disclosure descriptors for its intentionally planned ordinary, hosted or separately protected sharing. A selected fallback that has not yet been used still describes planned exposure, not completed delivery.

The disclosure check covers exact authored content, deliberately included quotations, resource bytes and metadata. It applies before protected-mail release **and before** uploading content to a host or another disclosure endpoint. If that planned exposure cannot be represented and authorized by the current contribution’s descriptors, hold it rather than emit a misleading protected declaration.

After an event is frozen, changing its audience, operation, authenticated disclosure array or other authenticated meaning requires a fresh contribution identity under the owning rules. Reserializing the event under its old identity is a conflict, even when the visible words are unchanged. Changing only an otherwise permitted outer mail representation may instead create a new prepared mail version as specified by the identifier contract; that does not authorize changing the original event.

A later broader permission not covered by the frozen plan needs a newly authorized revision/copy with the correct new event/disclosure binding where required. Retain the previous delivery success or uncertainty. An additional ordinary/hosted copy is additional exposure; it cannot be described as cancelling an earlier protected submission or used to resolve that submission’s unknown outcome. It cannot retroactively amend what an earlier recipient received.

An already declared and still-authorized fallback retains its original plan and identity/projection rules. A transport error, missing key response or elapsed timer supplies no new permission and does not authenticate a lack of recipient support. It may satisfy an explicitly retained fallback condition only within the modes, services, access models and disclosure scope already authorized for that revision. For example, a remembered rule may permit an ordinary copy when enabled setup ends without usable evidence; an encryption-required rule still holds. Apply current authority/disclosure checks and original uncertainty handling before any new release. An accepted or uncertain content submission is not an unattempted setup failure; switching its mode remains an additional disclosure with its own authorization and duplicate-risk handling.

Recipients interpret disclosure metadata as the authenticated plan for those original bytes. It is not a live global publication ledger, proof that every planned copy was delivered, or a promise that no future authorized forwarding can occur. The author’s local history can show later copy/permission changes using retained local lineage, without pretending that old recipients automatically received an authenticated update. This profile defines no implicit disclosure-update event or guaranteed notification of future sharing. A reply makes its own audience and exposure decision.

:::

## Choosing a sending account

A sender picker selects an account and its sending authority. It does not allow arbitrary From text. A compact address button may expose that choice without repeating it throughout the composer.

Before preparing a protected reply, resolve the selected account's cryptographic identity, authorized device and current conversation permissions. A mailbox alias does not establish a new identity or grant membership. If the selected identity cannot perform the operation, hold it and explain the missing authority. An edit still requires its original author's authority; selecting another account cannot bypass that rule.

Changing accounts also re-evaluates the recipient plan and the selected sender's fallback policy. Permission retained for another sender does not transfer automatically. Previously prepared or sent contributions retain their original identity and account binding: account switching must not rewrite signed events, queued retries or disclosure grants.

Changing the sender or final protection permission does not change draft-storage permission. Apply the [account-switch procedure](client-behavior.md#change-the-sender-without-changing-who-can-read-the-draft) before preparation or any account-triggered remote save. A still-unreleased plan is superseded when these dependencies change; previously possible/submitted disclosures and their retries retain their original account and immutable identities. A newly permitted weaker mode is a new authorized send plan, not evidence that an earlier protected attempt failed.

> [!ex] Personal and work accounts
> Carol opens a reply from her personal account, then chooses her work address. The thread can remain visible while the client checks the work account's authority and delivery policy. If it cannot send a protected reply there, the client holds that mode or offers an independently authorized alternative. It does not silently borrow the personal account's key.

## Remembered policy and the send plan

A client MAY remember a user's policy for a correspondent or conversation. It MUST expose the effective policy before sending and let the user change it. This specification does not require a confirmation dialog on every send or select a universal default.

Before submitting any copy, the client constructs a send plan containing:

- The immutable local intent revision, complete planned scoped contributions/copies and intended recipients, including private delivery recipients.
- Each copy’s exact protected audience/application and its retained independent or collective activation policy/cohort.
- The chosen route and protection mode for each recipient.
- The identity and capability evidence supporting that route, with its freshness and scope.
- Any hosted-access service and its access model.
- The effective fallback permissions and the scope in which the user set them.

The plan is local authorization state, not a public recipient manifest. It MUST NOT disclose Bcc recipients, private device lists or recipient-specific access credentials to other recipients.

Changes to audience, content, hosting service or protection mode require re-evaluation before the affected copy is submitted. A remembered policy may authorize a fallback without another prompt, but the composer and sent record must accurately reflect the resulting exposure. Failure to obtain capabilities MUST NOT silently amend a policy requiring encryption.

## Hosted-access models

A hosted fallback record identifies which of these models it implements. These names describe trust boundaries, not interchangeable security badges.

| Model | Who can gain access | Provider boundary |
| --- | --- | --- |
| Bearer access | Anyone possessing the access credential | Hosting service may hold plaintext or keys; email readers may obtain the credential |
| Account-bound access | An authenticated account satisfying the host's authorization policy | Host authentication and recovery are trusted; address ownership is not necessarily cryptographic identity continuity |
| Independently authorized cryptographic endpoint | An endpoint authorized under the selected end-to-end profile | Requires separately specified key authorization and browser-code trust; merely loading a web page does not establish this model |

The [hosted bearer-access candidate](hosted-access.md) defines credential generation, exact request/receipt objects, deliberate retrieval and revocation. Its credential profile uses 32 random octets encoded as unpadded base64url. The historical configured bearer flow has a joined local implementation. The [public management profile](hosted-access.md#connect-a-hosting-account) separately specifies native account authorization, current principal linking, owner-bound creation, read/revoke authority and reply discovery. Its full implementation and production hosting integration remain unproven. Account-bound recipient hosting and a separately authorized cryptographic endpoint are outside that selected bearer profile and cannot be advertised as implemented equivalents.

Each recipient receives a separate hosted grant. Shared links among recipients are outside this baseline because they prevent recipient-specific revocation and complicate disclosure accounting. Forwarding a bearer link still transfers its authority; a separate grant does not make a bearer link identity-bound.

The notification contains minimal invitation text and the access link. It MUST NOT include private answers, quoted history or the protected contribution as an email preview merely to make the notification look richer. An email subject may itself disclose information and must follow the selected metadata policy.

> [!ex] A forwarded link is still a bearer link
> Carol forwards her access email to Dave. If possession of the link is enough to open it, Dave can use it too. A separate link for each recipient helps revoke grants independently; it does not prove who opened the page or who wrote a reply.

## Link access, previews and replies

Fetching a link MUST NOT submit an answer, send a read receipt, accept an invitation, consume a one-time grant or change conversation state. Email scanners and preview services may follow links without user intent. Any state-changing operation requires explicit interaction after the access page has loaded and a fresh authorization check.

The access page MUST NOT send credentials or message content to third-party analytics, remote fonts, embedded resources or outbound-link referrers. Credentials must be excluded from routine application logs and error reports. This requirement does not make the hosting operator unable to inspect the delivered page or its content.

:::: {.details summary="Secret links and redirects"}

### Hosted credential navigation

A fragment-held credential is absent from the initial HTTP request target, but remains available to scripts in the loaded page. It is not automatically confined to the original origin. [RFC9110 Section 10.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.2) requires a redirect target without its own fragment to inherit the original fragment. A page reached through that redirect can therefore receive the secret in its URL even though the preceding server did not receive it as request content.

The initial hosted-access profile MUST use a direct HTTPS grant-entry URL and serve that entry page without an HTTP redirect. Do not put a URL shortener, tracking redirect or canonical-host redirect in front of a secret-bearing grant URL. This is a proposed deployment constraint to prevent credential transfer before the access application's code can run. It does not establish protection from the original hosting service or its page scripts.

After loading, any navigation to a login service or another origin MUST exclude the grant credential and protected content from the destination URL, including its fragment, and from redirect state and referrers. Preserve the grant only within the authorized access flow. A future redirect-capable profile must define its destination authorization and secret-removal behavior explicitly; an arbitrary Location response is not permission to disclose the credential.

Acceptance cases must exercise missing, empty and replacement redirect fragments, same-origin and cross-origin redirects, and login return paths. Test the browser's resulting URL and what destination scripts can read, not merely what appears in server access logs. This profile has not yet been verified in a hosted browser implementation.

::::

A bearer link alone MUST NOT authorize a reply attributed as a verified mailbox owner's act. The host must either authenticate the replying identity under its stated model or label the reply as originating from the holder of a particular grant, without upgrading that evidence to cryptographic authorship. Structured answers follow the same attribution rule.

Replying through the host creates a new contribution with its own audience and protection policy. The host MUST NOT expose earlier conversation history to new recipients automatically. It must not convert a recipient's response into an ordinary-email copy merely because the original invitation arrived through email.

## Expiry, revocation and failure

A hosted grant has an explicit expiry policy, either a timestamp or an explicit no-expiry setting. The sender can inspect it before disclosure. Revocation prevents future authorized retrieval through that grant after enforcement takes effect; it cannot erase downloads, screenshots, caches or previously obtained decryption material.

An expired, revoked or unavailable grant shows a clear access failure without automatically emailing the content or issuing a replacement grant. Renewal follows the sender's authorization policy and preserves an audit record. Reassigned accounts, changed identities and recovery require fresh authorization appropriate to the model.

The sender's record keeps separate facts for grant creation, notification submission, retrieval evidence, reply creation and revocation. None of these alone proves that the intended human read the contribution. A network request from a link scanner is not a read receipt.

## Scheduled submission and accepted holds

A locally scheduled draft remains subject to audience, identity and protection checks before submission. A message already accepted by a provider for future release has crossed that boundary. Show these states separately; do not present an accepted hold as a locally cancellable draft without a provider cancellation contract.

FUTURERELEASE does not define cancellation, ciphertext replacement or a fresh recipient-key check at release time. A sender requiring authorization to be rechecked at the scheduled instant must retain the contribution at an authorized endpoint capable of doing so. Do not delegate decryption to an ordinary relay to simulate that property. If the required scheduling mechanism is unavailable, hold or fail visibly rather than silently sending early.

A requested release time is not a guaranteed arrival time. Do not rewrite message history or trace fields to imply otherwise. The [future-release audit](audits/future-release.md) records existing timing rules and outstanding implementation dependencies.

## Replies and private recipients

A new reply has a new audience. Adding someone does not automatically share earlier history, confidential subjects or private recipient information. A blind-copy recipient must be able to see when replying would reveal their participation.

:::: {.details summary="Blind-copy generation and historical alternate addresses"}

### Blind-copy representations

For generated copies, do not include a Bcc field in copies intended for To or Cc recipients. A blind recipient's copy may omit Bcc, contain an empty Bcc field, or contain only that recipient's own address. Never expose the other blind recipients through shared structured metadata, control replies or encryption recipient descriptions. This proposed profile follows the clarified blind-copy handling in the pending emailcore message-format revision, while preserving legacy source messages for reading.

The absence of a Bcc field does not prove that no blind recipients existed. A client that knows the current user received a blind copy should make the disclosure consequence of replying to visible recipients apparent before sending. It must not infer a hidden recipient roster from missing header information.

### Why the managed-group model differs from RFC 9787

[RFC 9787 §9.4.1](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.4.1) offers a certificate-based construction: one main copy and a separate copy for each blind recipient, with that separate copy also decryptable by the named recipients. Its cryptographic payload contains no Bcc field, and blind-recipient certificates are not distributed with the message.

Email/2's managed MLS group has a member-visible roster. Adding a blind recipient to that group would disclose their membership, so this profile prohibits doing so. A private recipient instead needs a separately authorized delivery under the selected policy. This is a structural difference from the certificate-based construction, not evidence that MLS hides recipients. Creating a separate group with all named recipients would still reveal its membership to those members.

The ordinary-header alternatives above do not override the stricter no-Bcc-payload rule when implementing RFC 9787's certificate-based construction. Likewise, a hidden delivery must not leak through shared event audiences, device advertisements or history. A fresh reply needs its own audience and protection decision; a blind copy does not establish that its recipient can reply through the visible MLS group.

The [protected private-copy binding](private-copies.md) defines an experimental separate sender/recipient group, independent contribution identities and authenticated private-reply role. Its exact capability and disclosure versions must be supported before use; otherwise hold the protected delivery or use an explicitly permitted alternative. It never hides members inside the visible MLS group.

### Historical alternate addresses

A receiver MUST NOT transfer recipient identity, verified keys or capability history to an ASCII address merely because an RFC5335-era header presents it as an alternate. New delivery uses current SMTPUTF8 and internationalized-header rules. Any alternate destination requires its own identity and delivery-policy evaluation; it cannot silently receive content protected for the original recipient. Historical display recovery MUST NOT automatically add the recovered alternate to reply or reply-all targets. See the [historical internationalized-header audit](audits/internationalized-header-history.md).

::::

:::: {.details summary="Preserving confidential headers in replies"}

### Replies preserve protected header confidentiality

For an RFC9788 message, reply and reply-all recipients MUST be derived from the protected header fields. An outer Reply-To, Cc or other recipient hint MUST NOT add an audience member, even when the client knows an encryption key for that address. The From display exception for an unbound inner sender does not authorize replying to the outer address.

Confidential header values remain confidential when used to compose a reply or forward. This includes derived values such as a reply subject, references derived from a protected Message-ID, and addresses copied into a new destination field. Applying the client's default header policy alone is insufficient: the client must account for the referenced message's protected record of what its author exposed. It MUST NOT infer that record from mutable outer headers.

User editing does not automatically remove this provenance. Adding a reply prefix or changing part of a confidential subject must not cause the rest of that subject to appear in cleartext because an exact-value lookup no longer matches. A transition to plaintext delivery requires the existing explicit disclosure decision to cover the inherited confidential header values as well as the body. The draft must show the resulting audience and exposure before that decision is applied.

These requirements follow [RFC9788 Sections 6.1–6.2](https://www.rfc-editor.org/rfc/rfc9788.html#section-6). Its ReferenceHCP algorithm supplies a starting point for automatically generated fields; the implementation must also track derivation through subsequent edits. The [base audit and section ledger](audits/header-protection.md) are complete; dependency review remains in progress.


For the RFC9788 composition path, compute the final outer-header values, including inherited reply confidentiality, before constructing legacy display elements. Derive the decorative list from the final fields that were removed or obscured, and include it only in eligible main body parts inside encryption. This resolves the difference between RFC9788's local-policy-only list construction and its Appendix D.2.2.1 worked reply; the [audit evidence](audits/header-vector-checks.md) records that interpretation separately from the source text.

::::

## Delivery reports do not change permission

A refusal or missing receipt does not prove that someone lacks encryption support. It cannot authorize plaintext, hosted access or a different recipient. Keep each recipient's delivery result separate and apply the sender's existing policy.

:::: {.details summary="Rejections, retries and legacy receipt semantics"}

### Rejection is not downgrade authority

An SMTP/LMTP refusal, Sieve rejection, DSN or MDN MUST NOT by itself authorize changing an intended principal or sending previously protected content through plaintext or hosted fallback. Apply the sender's existing policy and its required visible transition rules. Diagnostic reason text MUST NOT be interpreted as an executable instruction or an authenticated capability advertisement. Temporary 4xx responses retain retry semantics and do not prove that an endpoint lacks encryption support. Track recipient-specific outcomes without converting mixed delivery into universal success or failure. See the [Sieve rejection audit](audits/sieve-rejection.md).

### Historical receipt semantics

A legacy disposition report MUST NOT establish reading comprehension, consent, structured-answer submission, device-key possession or irreversible deletion. Its absence MUST NOT trigger an encryption downgrade or be treated as proof of client incompatibility. Manual message action and manual permission to send a report are distinct report modes, not authorization for an Email/2 operation.

Use RFC8098 for current MDN generation rather than copying contradictory removed disposition values from RFC3798. Preserve unknown historical reports for inspection without synthesizing actions or error-response loops. See the [historical MDN audit](audits/mdn-history.md).

::::

## Deletion requests and local deletion

A sender can ask recipients to delete a message already delivered. A compatible
recipient system that honors the request removes the message silently: it MUST
NOT insert a deletion marker, issue a deletion notification or add an announcement
to the recipient's conversation. The sender sees a local deletion marker in place
of their original message. That marker records the sender's action; it is not
confirmation that every recipient deleted every copy.

| Action | What it changes |
| --- | --- |
| Cancel pending delivery | Stops copies that have not crossed their actual release boundary. |
| Delete for me | Removes the person's own selected copy under their account's deletion and retention policy. |
| Request deletion | Asks the original recipients to remove their copies. The sender retains a local marker; recipients that honor it remove the message silently. |

A deletion request does not require a recipient acknowledgement. Clients MUST NOT
request or infer reading status, device activity or retention-policy details as
part of this operation. Failure to receive a response proves neither removal nor
refusal. Sending a request is not proof that its target was unseen or erased from
exports, backups, forwarded messages or other retained copies.

> [!ex] One deletion, different local views
> Alice requests deletion of her message. Her conversation shows a local “Deleted”
> marker. Bob's compatible system honors the request and removes the message
> without a marker or notification. Carol's unsupported client might retain its
> copy. Alice's marker does not claim that Carol's copy disappeared.

:::: {.details summary="Authorization, silent removal and delivery boundaries"}

### Authenticate the request and preserve its scope

A native deletion request must identify the exact original authored contribution,
its conversation and its author principal. Its authenticated authority must be
checked against that original author under the owning identity and lifecycle
rules. A matching subject, display name or unauthenticated `Message-ID` is not
sufficient. A sender cannot delete another participant's contribution, a whole
conversation or copies outside the original authorized recipient scope.

The request must travel under the applicable protection and audience rules;
it must not expose protected identifiers through an ordinary-mail fallback.
Recipients apply their own deletion and retention policy. Honoring a request
removes the targeted content from the recipient's ordinary conversation view
without a placeholder, notification or announcement. It does not automatically
delete independently authored replies or quotations in other messages.

The sender's local marker MUST NOT be transmitted as replacement message content.
A recipient MUST NOT convert a successfully handled request into a visible
conversation message. Silence does not require erasing security records or
prevent an account owner from inspecting an explicitly opened administrative or
security audit view.

### Identify the exact request and original message

A deletion request names one original message, not an entire conversation. It
also commits the original writing's digest, so matching an identifier alone cannot
select a conflicting version or a replacement delivery. The digest identifies
bytes; it does not prove that the recipient accepted those bytes.

The [signed deletion-request0 record](deletion-controls.md#request-removal-of-one-exact-message)
commits the complete original authored reference, byte digest and scope. Its
[dedicated receiving offer and protected carrier](deletion-controls.md) define
optional support without changing the baseline conversation vocabulary. A parser
or a supplied-key signature check cannot advertise complete remote-deletion
support.

### Keep requests durable without producing receipts

Persist the exact request identity and target before release. Offline queuing,
retries and restart retain that identity; repeated delivery has one deletion
effect. Retain minimal authenticated suppression records so a late original or
an exact transport retry cannot restore content after its deletion request was
honored. A request received before its target needs authenticated origin and
scope validation before it can suppress that target. Unvalidated requests cannot
poison message identities or hide future messages.

A failed or uncertain submission remains a local delivery outcome. It MUST NOT
be turned into a claim about the recipient's deletion decision. No automatic
recipient success/failure receipt is required by this design. Provider-specific
recall reports, if an integration already supplies them, remain scoped evidence;
they MUST NOT generate recipient-side deletion announcements or become a promise
of universal erasure.

### Check the original author and recipients

A request from a different device of the original author is not automatically a
forgery. It needs that device's current accepted authority for the same principal,
including the owning identity history and any applicable retirement or conflict
checks. Possession of an old signing key, a restored mailbox or the same personal
address does not supply that authority. A reassigned address cannot delete its
previous owner's contributions.

The target is the complete logical authored reference, not one delivery event.
The request cannot broaden the original contribution's intended recipients or
turn an undisclosed private copy into part of a visible discussion. Each private
copy retains its own independent identity and scope. Do not obtain a deletion
recipient list by taking the current conversation roster or every historical
participant. A recipient that never received an eligible original gains no right
to its content from receiving a request.

### Keep removal effective when deliveries arrive out of order

The recipient's system distinguishes these outcomes internally; none is a
recipient-facing message or an automatic response to the sender.

| Available evidence | Recipient-system behavior |
| --- | --- |
| Invalid author, scope or request | No deletion effect and no reservation of the claimed target's identity. |
| Authenticated request, but target evidence needed for authorization is missing | Retain a bounded pending dependency. Do not hide a claimed target merely because its identifier appears in the request. |
| Complete authority and target checks, but recipient policy does not honor deletion | Retain the message under that policy; emit no automatic decision receipt. |
| Complete checks and recipient policy honors deletion | Commit suppression and removal from ordinary presentation together. Later eligible copies of that same logical message remain suppressed. |

Target-dependent validation must compare independently accepted original evidence
with the request's author, conversation and recipient scope. The request's own
claims cannot supply the missing original. Request and original arrival order
MUST NOT select different authorized outcomes when the same valid evidence is
available. Concurrent acceptance, local rendering and deletion serialize through
the recipient's durable state owner. A stale projection cannot reinstall removed
content after that owner commits the deletion. Retaining a pending request does
not extend its original acceptance deadlines or supply authority after expiry.

### Retain suppression for as long as the original can return

A request's release deadline and the lifetime of an honored deletion are different
things. Expiring the request, rotating a key, changing a relay route or completing
one transport attempt does not cancel an already honored deletion. A newly
prepared delivery of the same original authored bytes remains the same logical
message, even with a fresh delivery identifier or encryption epoch.

The recipient's system MUST retain enough protected local evidence to bind the
honored disposition to the exact target, the accepted authorization and the
existing replay/conflict records. This does not require retaining the target's
readable body merely to hide it. Unavailable original bytes do not prove a later
variant equal, erase an existing conflict or make its identifier unused. The
[identity ledgers](event-identifiers.md#keep-delivery-identity-separate-from-message-identity)
continue to govern those decisions.

Suppression MUST NOT be evicted merely because a timer or storage threshold was
reached while that target could still be accepted through live delivery, mailbox
rescan or restoration into ordinary presentation. An implementation may compact
records while preserving those checks. If its configured storage or processing
budget cannot safely retain the needed evidence, it holds the affected acceptance
or restoration work; it must not silently forget the disposition and redisplay
the content. Local budgets are implementation policy, not a new universal quota.

Historical archive inspection remains distinct from ordinary conversation
presentation. Restoring an older archive cannot override a deletion disposition
that the recipient's system still retains. If independent evidence shows that
required suppression or replay state is missing or inconsistent, hold promotion
into the ordinary view rather than treating the imported target as unseen.
An archive can still contain readable historical copies, and a complete rollback
of all independent evidence may be undetectable. Neither deletion nor restoration
promises erasure of already exported history or resistance to such a rollback.

### Stop unreleased work durably

Cancellation and release MUST serialize at the owning outbox boundary. Persist
cancellation and invalidate the queued release generation before reporting local
cancellation; restart or an offline retry MUST NOT release cancelled work. No
cancellation operation extends an original setup, identity, encryption or
human-send deadline.

If release may already have happened, retain that copy's accepted or uncertain
outcome. Cancelling remaining copies cannot turn it into “not sent.” Where a
provider owns the queue, await its authenticated cancellation result or keep the
outcome unresolved. See the [transport release boundary](transport.md).

### Keep local deletion separate

Deleting a local or own-mailbox copy MUST NOT emit a remote deletion request,
withdraw an answer or delete another participant's contribution. Preserve the
minimal replay, conflict and cryptographic-continuity records required by the
owning contracts. A retained reply to a missing or removed parent keeps its exact
reference; do not invent a replacement parent or fetch history automatically.
Recipient presentation must not reconstruct the removed content as a deletion
marker through that missing-parent reference.

### Existing service precedent and implementation boundary

[Exchange Online recall](https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/work-with-cloud-based-message-recall)
provides precedent for asking a recipient service to remove delivered mail within
supported administrative boundaries. Email/2's proposed native behavior differs:
it requires no recipient deletion report and no recipient-facing deletion marker.
A request cannot revoke knowledge of plaintext or make a disclosed key secret.

A provider adapter must establish its actual supported mechanism and authority;
SMTP acceptance is not recall support. Microsoft's [Graph recall method](https://learn.microsoft.com/en-us/graph/api/message-recall?view=graph-rest-beta)
is documented as beta, unsuitable for production use. Its request acknowledgement
does not establish removal.

**Native implementation remains to be qualified.** The [deletion-control binding](deletion-controls.md)
selects the signed receiving offer, dedicated HPKE key and protected delivery of
the exact request. Its complete current-authority, target, replay and durable
recipient transactions remain required before support can be advertised. The
closed conversation-operation and sealed-control-v2 vocabularies stay unchanged.
Implementations MUST NOT substitute an edit, reaction withdrawal, setup control
or unknown operation. Existing provider recall is a separate adapter capability,
not proof of this native protocol.

::::

## Required verification

Conformance fixtures must cover remembered policy, a stripped advertisement, mixed recipients, Bcc grants, partial transport acceptance, retries after key changes, host failure, link forwarding, scanner prefetch, expiry, revocation, account recovery, forged bearer replies and quoting old content into a new audience. Test evidence must identify which access model and security profile were exercised.

Deletion fixtures must cover forged and wrong-author requests, request-before-
original ordering, duplicate requests, restart, late original delivery, retention
policy, unsupported recipients and mixed local outcomes. Verify that honoring a
request creates no recipient marker, notification, conversation announcement or
automatic receipt; the sender's local marker must not imply remote confirmation.
Deletion acceptance must also exercise same-principal device replacement, retired
keys, reassigned addresses, concurrent original/request acceptance, refreshed
delivery identities, budget exhaustion and restoration of an older archive.
Verify that a missing target remains pending without hiding an unauthenticated
claim, and that a committed suppression survives request expiry and key rotation.
Cancellation fixtures must cover the cancel/release race and already uncertain
submission. Test actual provider integrations separately; mocks do not establish
Exchange interoperability or native deletion support.

This chapter owns policy and disclosure behavior. The [security profile](security-profile.md), [hosted-access contract](hosted-access.md) and [protected private-copy contract](private-copies.md) own the selected algorithms, wire formats and access boundaries. Implementers must name the profiles they support and their tested limits; the policy alone is not a complete secure-delivery implementation.
