---
title: Reply intent and destinations
order: 1.3
blurb: discussion · private replies · no replies · explicit audiences
sectionNav: true
---

# Reply intent and destinations

A message can invite a discussion, invite a private response or invite no written response. The sender declares that intent separately from To/Cc. A person copied on one message does not automatically become a participant in later discussion.

> [!ex] An announcement with a useful action
> Alice sends Bob and Carol an appointment notice with no written replies and a Confirm button. Neither reader gets Reply or Reply all for that notice. The button still follows its own authenticated action contract. Alice can use her normal address; a special `no-reply` mailbox is unnecessary.

This chapter owns written-reply intent and destination behavior. The [client chapter](client-behavior.md#declared-reply-intent) owns its observable presentation. The current agreement uses [slot reply-intent1 inside authored0](event-encoding.md#asynchronous-authored-records-and-deliveries): discussion membership covers intended slots even while some deliveries wait. The principal-based intent0/envelope5 and exact v1 receiving agreement below remain their own compatibility definitions. Their shared behavioral rules apply only through the current binding's explicit slot/reference adaptation; no parser infers one version from the other. A schema implementation alone must not advertise negotiated support.

## Choose who is being invited to answer

**Discussion** names the complete intended discussion audience, including the author. A person in that set gets a normal group reply. A recipient outside that set can reply privately only when the author permits private responses; otherwise there is no written reply action. To and Cc remain visible addressing roles, not a substitute for this explicit set.

**Private replies** offers a response to the contribution's authenticated author. This initial record does not delegate replies to an arbitrary third-party address or endpoint. The client resolves the author's currently eligible personal identity and route; it never replies to an outer relay address merely because it appears in From or Reply-To.

**No replies** offers no written reply action for that contribution. It does not disable previous contributions, remove group members, revoke mailbox access or prevent deliberate independent composition. Independently authorized questions, reactions, corrections and service actions keep their own semantics and permissions. Disabling free-text replies neither grants nor revokes those permissions.

The contract covers one immutable contribution. A copied recipient receives only messages addressed to them; there is no automatic observer subscription. An ongoing audience/subscription feature would need its own explicit disclosure and lifecycle contract. A later message can carry different reply intent, but cannot silently retarget an existing draft.

## Private responses are separate exchanges

A private response has exactly two principals: its author and the person being contacted, or one principal when a person deliberately contacts themself. It uses an independently authorized private context and fresh root contribution. Do not transplant the group message's reply parent, cryptographic membership, question controls, subject, participant list or resources into that context. The existing two-distinct-principal private-copy profile is not a self-conversation profile.

A local source connection can help a reader find the message that prompted their private response. It is not transmitted by default. Any deliberately included context follows the existing quotation and disclosure rules. Subsequent responses in the private exchange use their actual authors and audiences; a response to Alice's group announcement cannot keep directing Alice's later response back to Alice.

A client can show a personal conversation or a visibly separate private branch. In either layout, its audience heading, composer and continuation remain distinct from the shared timeline. Someone outside the private audience receives no message, private activity placeholder, reply count or read-status event about that exchange. See [private exchange presentation](client-behavior.md#private-exchanges-beside-a-group-discussion).

## Exact reply-intent record

The retained intent0 record is an object with one of the exact member sets below; current slot intent1 is defined in the authored-record owner. No omitted, additional, duplicate or null members are admitted. Common [strict event encoding](event-encoding.md) and byte/depth bounds apply. `version` is always the string `"0"`.

| `kind` | Complete members | Meaning |
| --- | --- | --- |
| `discussion` | `version`, `kind`, `participants`, `privateReplies` | `participants` is a nonempty, distinct, ASCII-sorted array of nonzero principal identifiers. It includes the contribution author and is a subset of the contribution's authenticated audience. `privateReplies` is a JSON boolean. |
| `private` | `version`, `kind` | Written replies go privately to the contribution author. |
| `none` | `version`, `kind` | Neither private nor discussion composition is offered as a response. |
| `not-applicable` | `version`, `kind` | This operation is not a primary written-reply target. It does not gain a new composer through reply intent. |

The first three kinds apply to `message`, `attachment-message`, `rich-message`, `reply-message`, `question`, `service-question` and `hosted-holder-observation`. Only `not-applicable` applies to `answer`, `reaction`, `reaction-withdraw` and `edit`. The selected application must independently permit the operation. A hosted observation's author is its authenticated observer, not a verified identity for its link holder. Private composition contacts that observer; it does not discover or impersonate the holder.

Examples with no principal placeholders are:

```json
{"version":"0","kind":"private"}
```

```json
{"version":"0","kind":"none"}
```

::: {.details summary="Successor contribution envelope and immutable record"}

Envelope5 has exactly the envelope4 root members plus required `replyIntent`, with root `version` equal to `"5"`. Its complete member inventory is `version`, `purpose`, `event`, `conversation`, `principal`, `audience`, `operation`, `disclosures`, `presentation` and `replyIntent`. The original nine members retain the envelope4 types, personal-address/role/audience equality, operation selection, resource, disclosure and authority constraints, except for that explicit root version change. Presentation still has exactly five members; reply intent is not an extra presentation member or an outer mail header.

Every operation carries a record, including the explicit `not-applicable` record where required. Missing intent cannot acquire an inferred default. Unknown operation, kind or version is unsupported/invalid under its owning acceptance boundary, not the nearest familiar behavior. The receiving client must independently validate the entire selected envelope, operation, carrier, current identity/context and audience before enabling reply affordances. A valid record does not authenticate its enclosing author.

The exact reply-intent bytes are part of the authenticated event representation and immutable retry identity. Reordering a participant array, changing a boolean or removing the record cannot preserve the old event's identity. The existing plain-message edit operation changes text only; it cannot mutate this record. To issue different intent, author a new contribution with a fresh event identity and the deliberately selected context. That does not retroactively change an earlier message or an already authorized draft.

No existing assertion8/context8/envelope4 agreement admits envelope5. The reply-aware protected agreement below binds envelope5, this record version, operation set and carrier support at every intended device. Old signed evidence cannot be rewritten or combined into receiving support. Until that agreement is actually implemented and selected, retain unavailable explicit reply-intent support rather than send an unnegotiated record or silently strip a no-replies restriction.

:::

## Reply-aware protected agreement

This section retains the exact reply-aware `mail-conversation-v1` agreement for compatibility. New Encryption claims use the [current asynchronous baseline](suite-profile.md#current-client-baseline), with authored0, envelope6 and slot reply-intent1. Implementing the v1 agreement below does not satisfy that current claim.

Before sending, every intended device must agree that it understands the message's reply policy. They can support different extras, such as reactions or answer buttons, while still agreeing on who may reply and who receives the response. Choosing fewer extras must not remove that policy.

An earlier client cannot be assumed to understand these rules. If the intended devices cannot agree, keep the draft waiting with its chosen policy. Sending a deliberately revised message through an older agreement is a separate composition choice; the app must not silently turn a private-only or no-replies message into an unrestricted discussion.

::: {.details summary="Exact application, assertion and admission selection"}

**Agreement.** The reply-aware agreement is `mail-conversation-v1`, within the same Email/2 specification. It requires reply-intent0/envelope5 in every contribution. Its core operations and five independent interaction blocks are exactly those of the [protected operation selection](suite-profile.md#module-agreement-and-common-operation-selection). Reply intent is a required feature of this agreement, not a sixth interaction block or a flag that can disappear when optional modules are intersected. A device may implement both agreements, but assertion8/context8/envelope4 support does not imply support for this one.

**Application.** The application object has exactly `envelopeVersion`, `payload` and `operations`. Values are `"5"`, `"mime-suite-v1"` and the ASCII-sorted core plus zero or more complete optional blocks. The four core operations remain attachment-message, message, reply-message and rich-message. The Answers, Reactions, Corrections, Service actions and Hosted replies blocks retain their existing paired/independent semantics. There are thirty-two operation sets per ordering, not a new operation set for each reply mode.

**Context9.** Context9 has exactly context8's eight members: `version`, `purpose`, `conversation`, `profile`, `administrators`, `application`, `ordering` and `delivery`. Version is `"9"`; purpose and MLS profile remain `"conversation-context"` and `"mls-1-0001"`. Its application is the object above. Ordinary owner/stream and managed endpoint-quorum ordering, administrator, private-copy/delivery and fixed-audience constraints remain unchanged. No context8 application can be edited into context9. Complete GroupContext bytes bind the selected context as before.

**Assertion9.** Assertion9 has exactly assertion8's field inventory, including required `keyPackageReceiveUntil` and `controlKey` and their schema-defined null exceptions. Its version is `"9"`, signature domain is `mail/passive-discovery/v9`, and its applications contain only the reply-aware tuples above, each additionally containing its exact `ordering` string. Its required feature list remains exactly `["mls-1-0001"]`; the tuple, rather than an unauthenticated feature boolean, implies complete reply-intent and both rendering profiles. Use the same per-ordering subset closure, ASCII ordering and required ordinary support. At most sixty-four tuples are possible. `orderingExchanges` contains exactly `{"format":"sender-stream-control","version":"1"}` and, when managed tuples are offered, `{"format":"quorum-exchange-experiment","version":"3"}`, sorted by format.

Each device publishes its own independently signed assertion9. Its original identity evidence, canonical mailbox, package validity/cryptography, control-key custody, receiving deadlines, maximum lifetime and freshness checks remain required. Old and new assertions cannot share an allocation merely to create extra single-use admission material: the original package reference and allocation realm remain unique under their owning rules. Publishing both versions does not make a consumed reference reusable. An assertion9 parser never accepts a mixed envelope4/envelope5 offer array or synthesizes a missing version from cached booleans.

**Selection.** For this v1 agreement, resolve one exact assertion9 for every intended device, including participating sender devices. Select the ordering from independently authorized compose intent, then intersect only its optional operation blocks across those original assertions. Require the exact resulting tuple in each assertion. Freeze all original evidence, full application and intended principal/device audience before admission. Absence, invalidity or unsupported version is a hold; it is not an empty optional set. The original package and control-key receiving windows apply independently to every chosen device.

**Admissions.** Initial invitation9, common roster6 and established invitation9 have exactly the corresponding invitation8/roster5 field sets, with their own versions `"9"`, `"6"` and `"9"`. They require context9/assertion9 and the reply-aware application. Signature domains are respectively `mail/mls-new-conversation-invitation/v9`, `mail/mls-initial-roster/v6` and `mail/mls-established-membership-invitation/v9`. Use the same Ed25519 NUL/U32-length/original-payload framing. Creation anchors remain version0 and commit the original new roster bytes; no version-number rewriting preserves a signature or digest.

All native Welcome, GroupInfo, creator/source-owner, full actual roster, private-return-role, package-consuming transaction, receipt/checkpoint and setup-secret retirement rules remain required. Established paths retain their exact mode-specific edge shapes, using the successor controls below and assertion9 evidence. Late receiving changes neither the original creation authorization nor the recorded receiveUntil. Same-key continuity cannot bypass revocation, role gaps, algorithm support or known conflicts.

:::

::: {.details summary="Successor control records and confidential framing"}

The ordinary source transition, source-control carrier and recipient-update payload use version `"1"`, with exactly their version0 field inventories, purposes and atomic lifecycle rules. Embedded contexts are context9 and all application assertions are assertion9. A transition's signature domain is `mail/stream-transition/v1`; its ID hash domain is `mail/stream-transition-id/v1`; recipient-update signatures use `mail/stream-recipient-update/v1`. The signature and transition-ID constructions retain their original NUL/U32 framing and exact original bytes. A different domain produces different signed/identified material; an old transition cannot be relabeled.

The managed exchange uses version `"3"` with exchange2's complete inventory, and the final carrier uses version `"4"` with carrier3's complete inventory. They use context9/assertion9 evidence. Their proof, candidate, scope, vote, certificate and witness-policy encodings remain unchanged: those already commit complete original GroupContext and candidate bytes. Retain exact witness/application assertion coverage, immutable membership/application/delivery and atomic installation. Supplemental evidence cannot change consensus identity or make a non-witness a voter.

These invitation/ordinary/managed controls select `sealed-control-v1`. It uses the same HPKE suite, bounded lengths, key-descriptor grammar, immutable custody/retirement deadlines and complete pre-encryption actor/recipient/route checks as sealed-control-v0. Its outer binary magic is exactly `EML2CTL1`, encrypted inner frame magic is `EML2CIN1`, intent `version` is `"1"` and purpose remains `"sealed-control-intent"`. Its HPKE info domain is `mail/sealed-control/v1`; its intent signature domain is `mail/sealed-control-intent/v1`. Apply the unchanged NUL/raw-key-ID/public-key info suffix and magic/key-ID/ciphertext-length AAD construction to those new bytes. Intent and bundle framing/member inventories, size limits and identity-bound original body remain unchanged. No trial decryption or parser fallback between magic/profile versions is permitted.

The permitted kinds for these successor controls are initial-invitation, established-invitation, stream-control, stream-recipient-update, quorum-exchange and quorum-control. The [mailbox-setup-v1 binding](mailbox-setup.md#set-up-the-declared-reply-policy) additionally selects mailbox-setup-response as the seventh kind, with its exact version1/required-agreement correlation. Identity administration and history protocols retain their separately selected existing records and sealed-control-v0 carriage; this agreement does not silently version them. An assertion9 control-key publication promises reception of both these precisely scoped control profiles, never arbitrary substitution of a kind's body.

The proposed logical outer media type is `application/vnd.threadlabs.mail-control`, with no parameters, canonical MIME base64, generic notice and exact two-part placement inherited from sealed control. Distinct fixed magic selects the profile before key use. For an authorized opaque relay route, the committed object remains the exact selected sealed binary under that relay's octet-stream arrangement; no readable assertion or personal address copy is added. Receiving v0 history/control traffic cannot change a context9 application or authorize a reply-aware group transition.

:::

::: {.details summary="MIME dispatch, graph and migration"}

`mime-suite-v1` has the exact direct MIME shape, leaf projections, resource roles, limits and acceptance stages of mime-suite-v0. Its required event alternative instead has media type `application/vnd.threadlabs.mail-event+json`, with no parameters, and contains exact envelope5 bytes. The authenticated context9 agreement selects this carrier; MIME label or recognizable JSON alone does not. Body projections depend only on the operation; reply intent is shown in client-owned chrome after complete acceptance and cannot be overridden by sender HTML or a compatibility alternative.

Every permitted operation validates its required reply-intent record in addition to the complete inherited envelope/address/operation/resource gates. No-replies cannot be silently inferred from absent record, an empty parent list or a mailbox spelling. The successor graph adds the explicit discussion-permission/exact-audience check from the receiving procedure below before installing a primary edge. Preserve original content and requested relationships when that check cannot establish an edge.

A readable contribution from an older agreement has no implicit reply-intent record. Do not label it no-replies, unrestricted discussion or private-only merely because a new view contains it. Keep its earlier reply behavior and actual recipients inspectable. A deliberately composed new successor root can concern that older mail under current audience/disclosure authority; it cannot claim that an absent old contract authorized a successor discussion edge. An unsupported old source is distinct from a missing source that may arrive later.

An existing stream/group remains under its original complete agreement. To use reply-aware composition, establish a fresh ordinary stream with fresh stream/group identity, or a separately admitted managed conversation. Retaining an ordinary visible conversation identifier follows independently selected grouping/disclosure authority and the existing private-pair restrictions; it grants no old keys or history. A private response to a source outside that private context begins a fresh root, not a manufactured cross-context parent. Missing reply-aware support retains the draft and its required intent. Old in-flight or uncertain sends keep their original identities, bytes and outcomes; migration cannot replay them as new events.

:::

The protected receiving/admission/control/carrier selection above is defined separately from evidence that it is implemented. The [ordinary-mail setup1 binding](mailbox-setup.md#set-up-the-declared-reply-policy) preserves exact assertion9 and the requested agreement. Public acquisition uses [provider descriptor1](provider-discovery.md#reply-aware-queue-discovery), [queue grants1](provider-grants.md#reply-aware-account-and-pair-permissions) and [exchange1](provider-control.md#reply-aware-known-pair-exchanges), or the independently authorized [bootstrap1 binding](bootstrap.md#provider-setup-for-declared-reply-policies). Their original assertion8-only schemas remain unchanged. Full source-bound cross-contract review and joined implementation/acceptance remain required before support is advertised. A securely obtained assertion9 can be checked as receiving evidence; it does not prove that any automatic acquisition path exists.

The current [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) uses slot-based intent1 inside authored0, with actual delivery-envelope6/context10. Its fixed readable vocabulary allows a simpler client to read an optional interaction and use independently permitted written replies. The earlier intent0/envelope5 agreement above is unchanged; no-replies/private restrictions remain mandatory in both. The current acquisition, pending-delivery and own-device setup contracts are selected in their owners.

## A newly paired device

Current snapshot setup uses [configuration3](paired-configuration.md#transfer-asynchronous-scope-metadata), including the accepted scope metadata needed for future asynchronous participation without old messages. Later refreshes use [own-setup0](paired-configuration.md#keep-setup-current-between-your-own-devices) under fresh current authority, rather than a permanent pairing lease. The retained [configuration2 transfer](paired-configuration.md#transfer-reply-aware-conversation-setup) carries reply-aware and earlier selections; configuration1 remains assertion8/context8-only. Each exact agreement/context/genesis row determines its own setup and admission requirements; older metadata is not widened or relabeled. Installed metadata cannot manufacture a missing old message's reply policy or target, activate past actions or claim native membership/send readiness. Unchanged contacts need not repeat verification merely because the device is new; original verification scope, current identity and complete admission still apply.

## Resolve a reply destination

Apply this procedure only to an independently accepted contribution, its exact record, and the reader's independently authenticated sending principal. A missing, conflicted or unavailable source remains unavailable. Cached UI state or a sender-supplied verified flag cannot supply acceptance.

1. Revalidate the record's complete shape, operation applicability and participant/audience relation. The reader must belong to the source's authenticated audience. A malformed contract produces no reply action through this contract; preserve the original readable contribution with its diagnostic.
2. For `none` or `not-applicable`, offer no written response. For `private`, offer the private action. For `discussion`, offer the discussion action only to a reader in `participants`, and offer the separate private action only when `privateReplies` is true. An audience-only recipient never inherits discussion membership from To/Cc or local history.
3. A discussion action resolves exactly to `participants`, including the replier. Under current slot intent1, preserve those complete intended slots and their exact scope root, even when some setup remains pending; independently bind the replier to an included author slot. Do not collapse distinct alias slots to a principal set or remove a waiting person. Each actual delivery separately requires eligible native membership, associations, routes and slot mappings. Earlier intent0 resolves its principal set instead. A private action resolves to the replier and original author under a new independently scoped root. No other historical participant, copied person, alias expansion or blind recipient is added.
4. Before opening a composer, retain the selected source event identity, exact record/event commitment, action, sending account/principal and resulting audience as draft dependencies. Show its actual destination. Discussion composition keeps the source parent only when the existing same-conversation and audience rules permit it. Private composition follows the separate-root rules above.
5. Retain that destination while the person writes. New arrivals, navigation and draft restoration cannot change it. Switching the sending account invalidates derived authority: recompute using its actual principal and require a deliberate new destination choice if that changes the result. Do not preserve an attractive label while changing the actual audience.
6. At preparation and final content release, recheck the source's accepted/conflict state, the frozen action and audience, current identity, account, context/membership, associations, route and disclosure authority under their owning rules. A changed source dependency or unavailable authority holds the draft; it does not broaden the audience, bypass no-replies or select an alternative account/channel. Retries retain the original contribution and transport identities.

The source contract authorizes a client reply action, not a new cryptographic group or a permission to forward historical content. A declared discussion set narrower than an existing managed group's audience requires a suitably authorized context; it cannot send narrower-looking metadata through a wider decrypting roster. A fresh ordinary stream follows its existing fixed-audience admission rules. These modes do not make delivery remotely atomic or guarantee that another client honored the author's preference.

## Change the audience while writing

Adding someone changes who receives the new writing; it does not automatically authorize sharing the source message or earlier conversation. Keep newly authored writing when possible, but reevaluate every included quotation, attachment, participant label and other source-derived context against the new audience. Show what will actually be included before sending. Existing disclosure policy can authorize that selection; merely editing To/Cc cannot supply the missing authority.

An Alice–Bob discussion reply cannot keep its authorized discussion edge after Carol is added: its audience no longer equals the source's declared discussion set. Hold that reply or let its author deliberately start a new, independently admitted contribution for the new audience. A `rich-message` root with empty `replyTo` can include explicitly shared, readable inert quotation; it must identify the current sender as the author of the new contribution. Bob's quoted words do not become a new Bob-to-Carol message. Indexed reply content still requires its own valid parent and source rules; quotation does not create one.

Sharing old content, admitting a new principal and retaining a local grouping are separate decisions. Apply the [membership-evidence disclosure rules](group-conversations.md#membership-evidence-is-also-a-disclosure) to admission and the [forwarding rules](messages.md#conversation-history-and-forwarding) to included content. Starting a wider conversation cannot silently widen an existing private exchange or reveal its activity to outsiders.

## Receive unexpected replies and legacy mail

Retain independently valid incoming content even when its author ignored a source's no-replies preference or addressed a different audience. Do not delete mail, fabricate consent or execute an action merely because its text looks like a reply. A primary relationship through this contract is established only when its independently accepted source permits the requested discussion action for that author. In the [current asynchronous agreement](event-encoding.md#asynchronous-authored-records-and-deliveries), require the same exact scope root, the complete reply intended-slot set equal to the source's discussion slots, and the author independently bound to an included author slot. Independently validate each actual delivery's native audience and slot map; pending intended recipients do not invalidate the relationship. Earlier principal-based agreements instead require the reply's authenticated audience to equal the source's declared principal discussion set. Otherwise retain an out-of-contract relationship diagnostic rather than a falsely authorized discussion edge. Private responses use their own root/context; their local source connection is not a cross-conversation graph edge.

This additional relationship check belongs before installing a successor-profile primary-reply projection. Missing source or incomplete validation remains pending, not a guessed root or fallback to old graph semantics. A validated rejection of reply intent affects the relationship/affordance, not independently valid authored content. Structured answers, reactions and edits still resolve their owning references separately; no-replies does not itself invalidate them.

For legacy mail, preserve inspectable Reply and Reply all destinations without inferring an authenticated discussion contract. An explanatory readable notice can communicate intent, but cannot guarantee a legacy client suppresses its controls. Do not hide a source address or invent a `no-reply` address to simulate interoperable enforcement. Conversion to an older representation requires an explicitly authorized composition/disclosure choice; failure to negotiate is not permission to strip a restriction silently.

## Acceptance boundaries

Exercise all three written modes plus not-applicable operations, copied readers inside/outside the declared discussion set, private continuations, self-addressing, current source conflicts, stale projections and changed accounts. Test exact JSON fields/types, null/duplicates, outside principals, omitted author, noncanonical participant order, forged boolean strings and operation/mode mismatch. Preserve exact original event bytes across retries.

Joined evidence must additionally exercise authenticated successor negotiation, actual private and discussion delivery, managed/ordinary audience enforcement, graph installation and restart, composer destinations, no outsider activity leakage and independent action permissions. A record/destination test does not establish these outcomes. [Current evidence](evidence/README.md#reply-intent-record-and-destination-selection) reports its narrower component scope.
