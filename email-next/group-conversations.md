---
title: Group conversations and membership
order: 11
blurb: audience · membership changes · delayed messages
sectionNav: true
---

# Group conversations and membership

An email conversation and a cryptographic group are separate objects. Replying to a changed recipient list must not silently redefine who can decrypt a protected group's history. This chapter proposes application semantics; a selected group security protocol must implement their authenticated transitions.

## Delayed decryption and retained secrets

A client may retain unconsumed MLS message secrets to receive delayed or reordered mail. It MUST apply the MLS deletion schedule to consumed secrets; retaining an old epoch is not permission to retain every key from that epoch. The [MLS deletion and security rules](https://www.rfc-editor.org/rfc/rfc9420.html#section-9.2) govern which values have been consumed.

The client’s retention policy must specify an elapsed-time limit, a storage/count limit and the maximum permitted forward jump in a sender’s message generation. An epoch-count limit alone does not bound elapsed exposure in a quiet conversation. These are explicit implementation settings, not values chosen by a received message. The client must enforce them before allowing an input to cause unbounded key derivation or retention.

When required secrets have expired or been deleted, retain the original ciphertext and report that the delayed contribution cannot be decrypted under the available state. Do not recreate an old sending checkpoint, request history automatically or downgrade the contribution to plaintext. A separately authorized history transfer follows its own disclosure rules.

Successful delayed decryption still requires the original epoch’s authenticated context and the current rules for accepting new effects. A removed member’s pending contribution does not become actionable because its target arrives later. Previously accepted history remains distinct from a newly arriving action.

Longer retention improves tolerance of delayed mail while extending exposure if retained secrets are compromised. Stored plaintext history and backups have their own exposure. Deleting a live database row does not demonstrate secure erasure of journals, backups or other copies; an implementation must state the limits of its storage mechanism.

> [!ex] A delayed message does not restore membership
> Alice removes Carol while Bob's earlier message is still in transit. Alice may decrypt Bob's message using retained secrets and its original audience. A pending reaction from Carol still remains blocked by the membership rules. Reading the older message does not put Carol back in the conversation.

The [bounded-retention experiment](evidence/README.md#bounded-secret-retention-and-delayed-application-delivery) exercises this sequence through restart, with actual library pruning and explicit time, count, storage and generation limits. Its logical database cleanup preserves public receipts and exact ciphertext retries. It does not erase backups or provide cleanup while the client is closed.



## Ordinary audience versus managed group

Ordinary email contributions have explicit per-message audiences. Their participants may reply to subsets, add recipients or forward content under their own disclosure policy. The conversation identifier groups contributions but grants no membership authority.

A managed encrypted group has an authenticated group identity, membership state and change policy. The baseline proposed here uses an explicit administrator set. Its initial state names the creator as the first administrator. An administrator can authorize adding or removing participants. Changing administrator roles requires a profile that explicitly supports that operation; the selected profiles [hold unsupported changes](ordering-exchange.md#explicit-unsupported-and-terminal-outcomes). Delegated or voting-based administration is a separate capability; receivers must not infer it from email headers or a mailing-list address.

Each member is an accepted cryptographic principal with its authorized device mapping. A mailbox string is a routing address, not a complete membership record. Group records must bind these roles through the selected identity profile.

The participant list is visible to members of this baseline managed group. Bcc recipients therefore MUST NOT be silently added as group members. A sender wanting private recipients must use a separately authorized delivery outside that group and accurately account for the resulting disclosure. A future hidden-membership group requires a separate security and privacy contract.

## Membership transitions

A transition identifies the exact prior group state, proposed new state, issuing principal and authorization evidence. The security protocol defines its cryptographic epoch and commitment rules. A timestamp or outer Message-ID cannot establish the authoritative state order.

A receiver validates the transition against the referenced prior state's administrator policy. Authorization is not evaluated against the proposed state: a sender cannot make itself an administrator merely by listing itself in its own proposed update.

Concurrent transitions from one prior state are conflicting branches until the selected protocol resolves them. The application MUST NOT invent a last-arrival-wins rule. Clients may continue reading known history while holding sends that cannot identify an agreed valid group state. Protocol-specific resolution must preserve the proposed authority checks and expose membership consequences before a conflicting operation is retried.

A profile supporting final-administrator departure must require an authorized successor or authenticated group closure. The selected profiles hold that departure rather than inventing either operation. Local closure stops this client from sending; it does not publish an authenticated group-wide transition. Reopening or moving to a separately admitted conversation requires explicit authorization; matching subjects or member lists do not merge group identities. See [unsupported and terminal outcomes](ordering-exchange.md#explicit-unsupported-and-terminal-outcomes).

## Joining and history

An invitation is a request to join, not proof that the recipient has joined or can decrypt. A successful join requires the security protocol's authenticated membership transition and endpoint setup. An ordinary email acceptance or a reaction does not substitute for that operation.

New members receive future content according to the state in which they join. They do not automatically receive earlier plaintext, historical keys, transcripts or attachments. A history share is a separately authorized disclosure identifying the included content and new recipients. The sharer cannot claim that re-encryption preserves the earlier audience restriction.

A forwarded invitation must not enroll its holder as the originally addressed principal. Acceptance binds the actual joining identity, group, invitation and allowed role. A bearer link alone cannot establish the original invitee's identity.

## Removal and delayed mail

A removal prevents future encryption to the removed principal after senders validate and apply the transition. It cannot erase received content or instantly update offline senders. The group security profile must specify how stale epochs and queued contributions are handled.

Before submitting a queued contribution, a client rechecks membership and the sender's authorization under its current accepted group state. If the queue was created under an older state, the client must not simply send stale ciphertext as though it targeted the new state. It either follows a protocol-defined safe resubmission procedure or holds the contribution for resolution. Stable application event identity prevents a resend from becoming a second answer.

A newly received contribution from a device already known locally to have lost send authority MUST NOT produce a new current-group effect merely because an earlier epoch decrypts it. Preserve the exact received object and distinguish historical cryptographic attribution from current authorization. A previously accepted contribution remains part of history; removal does not retract it. If the receiver cannot establish whether a newly arrived contribution was accepted before the authority change, mark its authorization unresolved and apply no form answer, edit, reaction or other action from it. A claimed Date, mailbox arrival time or an old MLS epoch number does not prove that a compromised key created the message before revocation. This profile does not yet define a transferable trusted acceptance receipt that would resolve that uncertainty.

Past receipt, present membership and current action authority are separate facts. A removed member's old form answer remains historical evidence; it does not grant that member authority to update group state after removal.

## Device changes

Adding a device to a member identity and adding a person to a group are different transitions. The device lifecycle profile determines who can authorize the device; the group protocol determines how that device gains the appropriate group state. A provider's device roster alone cannot add a group endpoint.

A device transfer must specify whether it includes history, pending messages or only future group state. It must not duplicate user actions when both devices synchronize the same event. Removing a device does not necessarily remove the person; removing the person excludes all devices authorized through that membership.

## Lists, aliases and provider services

A mailing list or alias can hide expansion recipients and modify messages. Its visible address therefore cannot establish that every recipient supports encryption or belongs to an approved group. An upgraded list can act as a group service only under an explicit authority and disclosure contract.

A service that receives plaintext to moderate, transform or redistribute content is an endpoint with plaintext access. The UI must include that service in the trust boundary. A relay that only transports protected objects is a different role. Neither role is inferred solely from the service's domain name.

Changing a list's membership outside the group protocol does not automatically change cryptographic membership. A bridge must reconcile both states explicitly and hold delivery when it cannot preserve the authorized audience. Sending an ordinary copy to a list follows fallback policy and counts as an ordinary disclosure even when other copies are encrypted.

## Required evidence

Conformance cases include unauthorized self-promotion, invitation forwarding, held unsupported administrator changes and final-administrator departure, explicit local closure, join without history, explicit history sharing, removed participants with delayed mail, queued sends across a transition, device enrollment and removal, hidden alias expansion and plaintext moderation. A future profile offering administrator transfer or authenticated group-wide closure must test those operations separately.

These rules select an administrator-based application model. The [experimental security profile](security-profile.md) selects MLS. The versioned application contexts and admission contracts bind these rules to MLS. The endpoint-quorum experiment below adds certified branch selection and recovery; the configured-writer profiles retain their narrower ordering model. Neither supplies a general late-message authorization proof.


## Membership ordering over mail

A cryptographic membership proposal does not itself change the authorized audience. The group security profile must specify the committed transition that changes membership and how every device identifies its predecessor. A successful SMTP submission, a received copy of one's own message, or arrival order in a mailbox MUST NOT by itself establish that a membership transition is the next accepted transition.

This distinction matters for an MLS binding: MLS epochs form a linear sequence, whereas ordinary mail can deliver competing transitions in different orders. Before sending under a new epoch, a client needs the profile's evidence that the transition is accepted. Until ordering is resolved, the client must hold affected sends rather than merge incompatible cryptographic states or silently use an older audience. The selected context determines the mechanism: older configured profiles use a designated member, while context7 uses the endpoint-quorum experiment below. A timeout cannot switch between these mechanisms.

### Pause content while a membership plan is pending

Once a device has fully validated proposals for the current MLS epoch, it MUST stop preparing or releasing application content in that epoch until an accepted Commit advances the group. This follows [RFC9420 Section 12.4](https://www.rfc-editor.org/rfc/rfc9420.html#section-12.4). A removal is the clearest example: sending more content to the old audience while its removal is being decided would defeat the purpose of the change. The same rule covers other valid proposals, not only removals.

For the selected endpoint-quorum profiles, standalone MLS Proposal messages are unsupported. A locally staged or received Commit candidate counts as an observation only after the client validates its actual MLS proposal list, exact predecessor and complete application authorization. Receiving an email wrapper or retaining candidate bytes alone does not count. Invalid, unsupported or unauthorized input cannot impose this hold merely by claiming that it contains proposals. An empty self-update Commit has no proposals and does not create this particular hold; all other send checks still apply.

Retain the validated observation durably before making the candidate or a corresponding vote available for publication. Bind it to the group and predecessor epoch. Restart, candidate abandonment, a coordinator timeout or failure to reach quorum MUST NOT clear the hold while that epoch remains active. Accepted certified epoch advancement ends the hold for the old epoch; terminal local retirement disables sending altogether. A previously prepared old-epoch message still fails the current epoch and audience checks after advancement.

Apply the hold both when preparing content and at dispatch, including the final check before SMTP DATA. Bound ordinary copies and hosted disclosures of the same protected contribution follow it as well; they are not an automatic escape route. Separately authorized ordinary conversations remain separate. Control evidence and Commit delivery can continue through their existing authorization checks so that the group can finish the transition.

Publishing material that technically enables an external join does not authorize arbitrary participants to join an Email Next conversation. Existing administrator and invitation rules still apply. Likewise, an MLS branch or reinitialization must retain the application-level distinction between a separate conversation, a parameter change and an authorized history disclosure. A new member's ability to decrypt future traffic does not grant access to past messages.

These requirements are informed by RFC9420 Sections 3.1–3.4. The MLS base audit and versioned application experiments supply separate source and implementation evidence; neither makes ordinary SMTP an MLS sequencing service.


### Endpoint quorum comparison

The [ordering-proof reference](ordering-proofs.md) defines the exact scope, candidate and certificate grammar. The [ordering-exchange contract](ordering-exchange.md) defines predecision mail, explicit wrapper support and durable retention.


A separate [endpoint quorum experiment](evidence/README.md#endpoint-quorum-ordering-experiment) tests client-held ordering witnesses, signed prepare/commit certificates and evidence-carrying coordinator changes over ordinary mail. It validates actual MLS transitions and an ordering-policy handoff under the predecessor's witness policy. It does not require an upgraded provider to act as ordering authority.

The experiment selects an explicit fault bound and witness set rather than assuming that every member is an honest voter. Its separately versioned signed initial admission now connects context7 to ordinary protected application sending and receiving. The local integration exercises a rich contribution, certified removal at retained members, and a subsequent protected reply using one shared MLS checkpoint. Identity/mailbox acquisition remains configured; proof-aware established joining now verifies an independently selected genesis anchor and certified path before actual Welcome processing. Fixed durable control/invitation release now uses current local authorization and explicit retry handling. Separate terminal and historical adapters cover removed-device notification and ordered offline catch-up. A separate recovery-only transaction handles known-revoked intermediate rosters. Restore assurance and complete distributed liveness remain unfinished. A coordinator timeout alone cannot authorize a competing branch, and a prepared value that fails current-authority checks can remain blocked. The existing designated-writer experiment is not silently upgraded by these tests.

The signed-discovery lifecycle adds assertion7, initial invitation7/roster4 and established invitation7, retaining the same context7 and application format. Every admitted device advertises exact exchange1/carrier2 support; only selected witnesses vote. Established7 preserves full authenticated supplemental assertions on every ordering-path edge. The [exchange contract](ordering-exchange.md) defines these exact additions. The earlier configured lifecycle below remains strict and supported separately.

The experimental version assignments are exact: assertion6, initial invitation6 and common roster3 select context7; established invitation6 carries a locally pinned `genesis` anchor and signed contiguous `orderingPath`. Existing event envelope3 and the rich MIME payload are reused. Older signed versions retain their meanings. Initial roster3 binds generation-zero witnesses to the admitted devices’ signing keys and accepted state/binding references; it establishes genesis rather than claiming a quorum decision.

Control carrier1 has exactly `version`, `purpose`, `candidate`, `proof` and `applicationAssertions`. Version is `"1"`; purpose remains `"quorum-control-experiment"`. Candidate and proof retain their existing exact formats. Assertions are the complete signed assertion6 wrappers for precisely the added leaves, sorted uniquely by principal and device. No-Add transitions carry an empty array. The receiver checks each assertion’s current accepted identity, resulting key and selected application, then compares its KeyPackageRef with the actual Add proposal processed by the MLS library. Missing, extra or substituted packages hold the complete transition. Incoming identity bundles cannot install trust.

The existing 1 MiB decoded control and 2 MiB MIME limits include the added evidence. The client commits support, membership episodes, the shared checkpoint and the decision together. Retries do not replace retained evidence or advance the epoch twice. A cached decision does not excuse malformed carrier fields. Carrier0 remains the earlier configured comparison.

The fixed sending adapter retains immutable bytes and exact mailbox/device selections. Before submitting an established invitation, it requires accepted SMTP handoff records for controls to every predecessor device other than the author. That orders local submissions; it does not prove that remote clients have installed the change. Authorization is checked again immediately before DATA. An uncertain attempt requires explicit retry authorization, and an accepted recipient is not automatically resubmitted. The invitation adapter requires the exact resulting decision to remain the current tip. A combined Add/Remove uses one actual Commit; its handoff dependencies include a terminal-only control for each removed predecessor device.

### Terminal notification and offline catch-up

A terminal-only control may use retained authenticated mailbox/device routing after that device loses receive authority. The selected mailbox association must remain enabled at the same generation, with unchanged, unexpired routing evidence. Current sender and local policy authorization are still required before release and before DATA. This exception authorizes only the retained control bytes; it grants no application authority or future group secrets.

The removed endpoint must authenticate the exact Commit under its predecessor state and verify the complete quorum certificate binding that Commit and its final context. Its MLS library must report self-removal. The experiment compares all public context fields reached by OpenMLS: inherited protocol version, suite and group ID, the newly computed tree hash and incremented epoch, and the exact resulting extensions. OpenMLS returns this terminal state before computing the final confirmed transcript or checking its confirmation tag. Those final values are therefore certificate-attested, not independently verified by the removed endpoint. This boundary is accepted only for an inactive terminal record; retained members still require normal complete MLS validation. Decision retention, closed membership episodes and inactivity commit together. Exact replay returns retained evidence without reopening the instance or decrypting the Commit again.

The historical adapter retrieves a complete retained certificate path from the locally accepted genesis to the current tip. It checks predecessor continuity, current witness authority and uninterrupted sender membership. A selected recipient receives only the suffix beginning at its exact retained predecessor. A continuing recipient must retain the same key throughout; a removed recipient receives controls only through its removal edge. A later rejoin does not reopen the old route. Missing history, a changed route, failed current authority or a local complete-path size limit holds the request.

Each prepared history plan retains immutable per-step MIME and submits steps in order, requiring accepted SMTP handoff for preceding steps. The existing uncertain-attempt retry rules apply. These handoffs do not prove remote installation. A receiver that already knows a revocation affecting an intermediate roster still holds ordinary per-step installation. It may use the atomic recovery path below only after selecting its required retention policy.

### Atomic quorum recovery

The recovery path processes a complete sequence of carrier1 messages for initial6, or carrier2 messages for initial7 on disposable MLS checkpoints, within one database transaction. Every edge must match its exact certified predecessor, Commit bytes and resulting context/roster. The local endpoint must remain a member throughout. Removal and later rejoining require separate admission. Current committer authority remains required; temporary additions need independently selected exact identity/key pairs, complete signed support and the actual processed Add package references. A revoked-device lookup alone does not establish its old key.

Historical witness signatures retain their original identity-state references. For recovery only, a witness may have a newer accepted identity head if the old head is demonstrably on the locally accepted chain and every intervening state retains the same binding and key without revocation. The witness must still have current send authority at the credible time. Unknown ancestry, conflict, changed binding/key or revocation holds recovery. This permits an unrelated sibling's revocation without pretending that the old head is current. Ordinary historical release and admission keep their stricter checks.

Before publication, every final member must pass current authority checks. Newly retained members need exact current assertion6 support for the older lifecycle or assertion7 for the signed-exchange lifecycle; expired historical support cannot provide that agreement. Carrier2 recovery independently validates every historical witness supplement and its exact coverage. It also requires fresh assertion7 evidence for every final witness. An assertion may name the accepted descendant head only under the unchanged-binding recovery rule above; historical evidence alone never satisfies this current check. Exact carrier2 bytes remain in recovery-only records. The client must explicitly select deletion of past epoch secrets for this recovery, accepting that late ciphertext may become unreadable. It then installs only the final checkpoint and agreement, closes removed membership episodes, and marks intermediate epochs ineligible for application effects. These changes and the retained recovery receipt commit together. A crash before commit leaves the prior checkpoint and effects unchanged; exact completed retry returns retained evidence.

Recovery-only records may support later recovery ancestry checks. They do not become ordinary forwardable history or an outbox authorization. Already accepted conversation content remains history. Logical secret retirement is not proof that filesystem journals, backups or restored storage cannot contain older secrets.

## External proposals and parameter changes

A provider or automation service may propose a group change only under an explicit, authenticated delegation. Permission to submit a proposal is distinct from permission to commit it. The group's administrator policy must be enforced when accepting the transition, including proposals to add or remove devices, change cryptographic parameters or replace group extensions. A relay's ability to deliver a public handshake does not grant it any of these permissions.

A parameter change must preserve required application policy unless an authorized transition explicitly changes it. In an MLS binding, GroupContextExtensions replaces the entire extension list; omission is not a request to retain an old value. Implementations must therefore validate the resulting complete configuration and reject accidental removal of required policy. Compatibility checks must include members added by the same transition and exclude members removed by it.

The selected profiles do not support MLS ReInit or subgroup admission. They [hold those transitions without voting or changing membership](ordering-exchange.md#explicit-unsupported-and-terminal-outcomes). A future capability offering ReInit must define authorized completion after its initiator goes offline and prevent competing Welcomes from silently splitting the conversation. A future subgroup capability must bind its intended subset and separate conversation identity without implying access to the original group's history. Starting a separately admitted conversation is not authenticated ReInit or a grant of old history access.


### Pending transitions and admission delivery

Constructing a candidate MLS commit must not install its proposed state as the current group state. The client must keep the candidate separate until the ordering mechanism establishes acceptance. Corresponding Welcome messages MUST NOT be released to new members before that acceptance. Releasing a Welcome early could admit a device to a branch that the rest of the group never accepts.

The ordering mechanism must address repeated losing proposals and abandoned candidates, not merely choose a winner in a single race. Obsolete staged secrets and candidate checkpoints must be retired once they are no longer needed; public voting safety records have a different lifetime. The [selected exchange lifecycle](ordering-exchange.md#durability-and-retention) stores candidate dependencies before publishing a vote and retires obsolete staged secrets after certified installation. It retains public safety/history records indefinitely. Optional pruning must preserve the specified proof pins and explicitly report unavailable history; logical retirement does not prove physical erasure.


## Applying account changes to an MLS group

Account identity state and conversation membership have distinct authority. An account enrollment does not automatically add a group leaf, and a conversation administrator cannot restore an account-revoked device. Both the accepted account state and the prior group's administrator policy must authorize the resulting membership. A validated account revocation is effective for local authorization checks even while its corresponding group removal is pending.

After accepting an identity successor, the client compares every affected current-epoch leaf with the account's new accepted bindings. It resolves devices by account, device identifier and signature key, then obtains their leaf indices from that exact epoch. An index cached from a previous epoch MUST NOT identify a removal target.

| Accepted identity change | Required local consequence |
| --- | --- |
| Device removed or revoked | Hold new application sends in every affected group until the leaf is excluded through an accepted group transition; reject new effects attributed to that device |
| Receive role removed | Hold new application sends while the device remains in that group's encryption roster |
| Signing key replaced | Treat the old leaf as unauthorized for future delivery; removing it and admitting the new key requires an authorized group transition |
| Send role removed while receive remains | Reject new effects originated by that device; this alone does not remove its authority to receive |
| New device enrolled | Keep it outside existing groups until group admission succeeds; enrollment grants no history transfer |
| Accepted account history becomes conflicted | Hold operations that depend on the disputed account authority; do not select a branch by arrival order |

A hold preserves reading of already authorized history. It does not silently remove the affected person from the intended audience or permit ordinary-email fallback. A client may construct an authorized removal transition while application sending is held, provided the committing device itself retains the required authority. Losing the final authorized group administrator requires the separately defined recovery or closure procedure; revocation cannot justify using the revoked key to appoint its replacement.

Before merging a candidate commit, the application validates the complete resulting roster, context and proposals against the exact predecessor. In particular, a commit cannot combine a legitimate removal with an unauthorized addition, key substitution or administrator change. Account revocation evidence does not grant an arbitrary member permission to commit changes. The selected ordering mechanism must also accept the transition before the new epoch is used or a Welcome is released.

For each queued send, the client retains the group identity, epoch and accepted identity-state digests used to authorize its target devices. At the [serialized local release decision](transport.md#local-authorization-and-release), it rechecks those dependencies against current accepted local state. A changed dependency invalidates the prepared send decision. The client holds it or reconstructs and reauthorizes a new protected delivery; it MUST NOT submit the old ciphertext under the new audience label. Revocation processing and this release decision require one serialized local boundary, so a locally accepted revocation cannot lose a race to a decision computed beforehand. Distributed offline senders remain subject to the stated freshness policy; this local rule promises no instantaneous global cutoff.

Once ciphertext has been handed to the transport, a later change cannot reliably recall it. The client records the audience and epoch actually used. A new client-controlled attempt requires current authorization; remote SMTP retries after accepted handoff are outside the client’s cancellation boundary. A user-facing delivery status must not imply that an intervening removal made the old ciphertext inaccessible.

### Removal evidence and implementation limits

The OpenMLS experiment removes the second device through a serialized commit carried over the local MIME/SMTP fixture. The creator advances its epoch and has one remaining leaf. Before learning the removal, the removed device still decrypts a delayed old-epoch message but cannot decrypt a new-epoch message. After processing the removal commit, its group becomes inactive and the library refuses a new send from that group. These are tested cryptographic state transitions, not recall guarantees.

The configured-writer experiment also connects removal to accepted account revocation and durable membership periods. It can remove a revoked recipient while application sending is held, checks the surviving roster, and prevents a pending contribution from gaining a new effect after membership removal. Already accepted contributions remain historical. A removed endpoint retains an inactive terminal record; it cannot provide the surviving group’s finalized context as catch-up evidence. See the [removal evidence](evidence/README.md#configured-removal-and-membership-periods) for tested scope. A separate [terminal-notice adapter](evidence/README.md#terminal-removal-notification) can deliver the exact removal Commit over loopback SMTP using unchanged retained routing; it grants no catch-up or future secrets. A separate [direct signed rejoin experiment](evidence/README.md#established-membership-instances-and-direct-rejoin) preserves instance boundaries. The [durable Welcome flow](evidence/README.md#durable-established-welcome-delivery) also exercises SMTP admission and same-key rejoin with a fresh package. The separate endpoint-quorum path supplies distributed ordering and recovery experiments. This configured-writer path does not provide writer succession or physical secret-erasure assurance.


## Configured ordinary-mail experiment

The local experiment exercises this sequence: decide an addition, retain its exact Commit, send it through loopback SMTP, and receive it alongside application messages using the same stored MLS state. The typed sender checks authority before release and again before DATA; a lost SMTP result remains uncertain and an explicit retry uses the same bytes. A transport result still does not establish another member's acceptance.

This [comparison experiment](evidence/README.md#group-transitions-through-ordinary-mail) uses one configured endpoint writer. Its ordinary control path requires the exact resulting context. A [separate historical adapter](evidence/README.md#historical-control-catch-up) can dispatch retained additions, self-updates and removals to continuously present surviving devices after later epochs, checking continuity and current authority. A receiver that already knows a revocation holds an intermediate Commit without consuming its message key. The atomic recovery experiment can validate the complete sequence through removal and install only its final state, as described below. The [established invitation flow](evidence/README.md#durable-established-welcome-delivery) supplies durable Welcome sending and bounded same-key rejoin. This experiment does not provide designated-writer failover. The separately selected endpoint-quorum path supplies coordinator-change and recovery evidence; a configured-writer conversation cannot silently adopt it.


## Membership in rich conversations

A rich conversation can add or remove a device without changing its agreed message format. Every added device must support the exact selected combination of envelope, rich payload, operations and membership ordering. Capability support does not authorize membership; the administrator, account-state and accepted-transition checks still apply.

The experimental context-4 profile uses designated membership ordering for these changes. A fixed-roster rich conversation remains fixed. An Add cannot silently switch formats, combine different device capabilities into a larger set, or reinterpret a plain conversation as a rich one.

> [!ex] Returning with the same key
> A removed phone receives an accepted removal notice and becomes inactive. If it returns, it needs a fresh package and a new authorized admission, even if its signing key has not changed. Its new membership does not reactivate answers or actions left pending in the old membership.

### Delivering a membership change to several devices

The local experimental ordering policy hands the exact Commit to each remote predecessor device's route before handing the Welcome to a new device. A successful SMTP result is evidence of transport handoff, not evidence that the device processed the Commit.

Several devices may share one account mailbox. They require separate target submissions, each backed by its own exact principal, device, key and selected mailbox observation. One recipient acceptance cannot satisfy two devices. The client must match the retained checked association evidence in each accepted attempt; caller-supplied device labels are insufficient. Missing or uncertain handoff holds the Welcome. These checks preserve the mailbox-association policy, including holds for conflicting principal claims.

::: {.details summary="Exact rich established-invitation contract"}

### Version and proof mapping

The established invitation uses version `"3"`, purpose `"mls-established-membership-invitation"`, profile `"mls-1-0001"` and signature domain `email-next/mls-established-membership-invitation/v3`. The signing input is that ASCII domain, one zero octet, an unsigned four-octet big-endian payload length and the exact payload bytes. The detached Ed25519 signature is 128 lowercase hexadecimal characters.

The outer wrapper is exactly `{payload,signature,identity,applicationAssertions}`. The signed payload is exactly `{version,purpose,invitation,profile,conversation,creator,target,group,previousEpoch,epoch,previousGroupContextDigest,resultGroupContextDigest,decision,keyPackageRef,keyPackageDigest,notBefore,notAfter,context,applicationContextDigest,members,welcome,applicationAssertions}`. Use the existing strict JSON encoding, original-byte retention, identifier and unsigned-decimal-string rules. Binary payloads, group/context/Welcome bytes and package references use canonical padded base64; digests are lowercase SHA-256 hexadecimal values.

`creator` is `{principal,device,state,binding}`; `target` adds `mailbox`. `members` is the sorted unique resulting device roster, each entry exactly `{principal,device,signingKey,state,binding}`. `applicationAssertions` in the signed payload is one ordered `{principal,device,digest,signature}` reference per member. The outer array contains those exact independently signed assertion-3 wrappers. The context is exactly context4, its payload is `mime-rich-v0`, and its designated ordering device is the creator. Existing established versions keep their original context/proof mapping and reject this branch.

The resulting epoch is exactly one greater than `previousEpoch`. The accepted decision is an Add of the one named target; this carrier does not silently generalize to several simultaneous established-group additions. `decision` binds the exact accepted Commit; predecessor and resulting GroupContext digests bind their respective complete MLS contexts. `applicationContextDigest` instead binds the exact application extension bytes.

### Historical selection and present authority

For existing members, the inviter attests that the referenced signed proofs were selected for the unchanged application agreement. Their original expiry does not erase that historical evidence. This is not independently verified historical group admission, and it cannot replace current account/key authority.

The target's assertion, package and binding must be current and cover the complete invitation interval. The receiver independently selects the expected exact context and allowed creator, checks current receive authority for every resulting device and send authority for the creator, then validates the actual Welcome's group, epoch, context, roster, signer and finalized GroupContext. A new member cannot verify the encrypted predecessor Commit from the Welcome alone; the signed predecessor and decision commitments retain their inviter-attested status.

### Atomic admission and rejoin

The receiver consumes the package and installs the checkpoint, immutable agreement, original proof provenance, membership period and acceptance result in one transaction. Failure leaves the package unconsumed. Exact accepted replay returns the retained result.

A returning device receives a new instance derived from its new accepted invitation. It cannot restore a historical checkpoint or reuse an ended membership period. Continuously present members keep their original uninterrupted agreement; their current authority is still checked. Previously accepted history stays historical, while pending operations remain subject to the membership period in which their ciphertext was accepted.

:::

The [rich group lifecycle experiment](evidence/README.md#rich-group-membership-and-shared-mailboxes) joins signed initial creation, actual Commit and Welcome delivery, rich resources, terminal removal and fresh-package rejoin. It retains the configured-writer boundary: distributed failover, branch reconciliation and hidden-recipient membership remain separate work.


### Catching up through a revoked member

A client may have missed an addition and its later removal. If it already knows that the intervening member was revoked, it must not expose the intervening group as a usable conversation. The configured-writer experiment processes the complete Commit sequence privately and installs the final state in one transaction. It requires a currently authorized writer, a continuously present local device, explicitly permitted additions, and current authority for every final member.

The same recovery path supports the explicitly negotiated private-copy context `5` and protected-presentation context `6`. Every intermediate roster must preserve the authenticated delivery roles and private-copy principal pair. The exact context, including the envelope, payload, operations and presentation selection, remains unchanged through the chain. A membership repair cannot turn a private copy into an ordinary conversation or silently change its presentation profile.

Any final member whose application support is not already established must supply an independently signed, currently valid assertion for the exact selected profile. The client records that confirmation at the final accepted epoch. It does not infer that the device supported earlier messages. Missing or invalid final support leaves the original conversation state intact.

> [!warn] Experimental recovery trade-off
> The pinned MLS library cannot selectively delete just the intervening epoch secrets through its public API. This experiment requires an explicit local `delete-all-past-for-remediation` choice. Recovery then preserves already accepted message history but discards the ability to decrypt late ciphertext from earlier epochs. Omitting that choice holds recovery; it does not silently change retention policy.

### Finding missing controls automatically

The local retrieval experiment scans a configured mailbox for original control messages and assembles the missing sequence. It verifies each Commit against the actual cryptographic predecessor; message arrival order and a sender’s claimed epoch do not establish ordering. A second configured source can supply missing copies, but it cannot appoint a replacement group writer.

Before final acceptance, the client holds recovery if two different authenticated successors from the authorized writer compete at one predecessor. It also holds when a message, exact addition permission, current signed application-support proof or explicit secret-retirement choice is missing. A malformed copy cannot consume the live message key or prevent a later valid copy from being considered.

The experiment uses a local mailbox populated through actual SMTP handoff. It does not yet synchronize a deployed IMAP/JMAP account or request retransmission from remote peers. Those integrations must preserve the same authority and audience checks. An unavailable designated writer is not permission to elect another writer. The separate [endpoint-quorum profile](ordering-exchange.md) supplies its own certified coordinator succession; it does not change this configured-writer recovery contract.

::: {.details summary="Atomic acceptance, retry and retained evidence"}

### Acceptance boundary

The client checks the original control carriers and each full successive GroupContext against a disposable cryptographic state. The application profile and configured writer must remain unchanged. A temporary revoked leaf grants no current account authority, application support or event effect. Removal followed by rejoin requires the separate admission path.

The final checkpoint, membership periods, current signed support, exact input receipts and recovery result commit together. Other local connections see either the original state or the final state. A crash before commit permits retry; an exact retry after commit returns the retained result without selecting replacement proofs. Recovery performs no external action and emits no Welcome or application message.

### Retrieval and restart

The receiver retains original MIME, source cursors and the exact selected recovery request. It advances a scan cursor only with the messages that cursor covers. Once selected, the carrier sequence and support proofs do not change on retry. A changed checkpoint makes the request obsolete; an authenticated branch discovered before acceptance holds it. Final acceptance commits the job receipt with the checkpoint, membership periods and support records. A crash exposes either the old state or that complete result.

Retrieval limits are adjustable local resource policies. Reaching a limit holds work without pretending that a partial scan is complete. Cancellation preserves the retained evidence and does not undo an accepted membership change. Recovery still grants no intermediate application effects and does not turn recovered controls into ordinary forwarding authority.

An exact retry of completed recovery returns its retained receipt. After past epoch secrets have been deleted, a newly arrived competing private Commit may no longer be decryptable or authenticatable. The client retains its original bytes but cannot infer writer equivocation from its outer metadata, and this experiment does not block current traffic on that basis. Detecting such historical branches would require additional independently verifiable evidence; successful recovery is not assurance that no undiscovered branch exists.

### History and forwarding

Recovery retains public evidence of the sequence, with explicit recovery-only provenance. It does not manufacture the historical authorization records used by the ordinary catch-up sender. Forwarding through these local recovery records remains held; the original writer's accepted decision history is a separate source. Intervening epochs are recorded as ineligible for new application effects within this membership instance, including effects from surviving senders. Removed senders also fail the normal current membership-period checks; later rejoin does not reopen their old period. These checks are independent of the forwarding restriction. Previously accepted history remains readable.

### Existing rejected states

Older experimental receivers persisted a rejected Commit's consumed message key. Those already affected checkpoints cannot process that same ciphertext again. Deleting the rejection receipt or restoring an old checkpoint is not supported recovery. New receivers retain the relevant intermediate control as pending without installing the staged cryptographic state, so a later complete sequence can be accepted.

This remains a configured-writer experiment. It does not provide designated-writer succession or recovery after losing the final authorized administrator. Physical secret erasure and independent interoperability remain separate assurance work; endpoint-quorum ordering has its own selected contract above.

:::
