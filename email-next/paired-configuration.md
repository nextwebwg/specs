---
title: Conversation setup on a paired device
order: 9.7
blurb: trusted selections · public evidence · automatic send readiness
sectionNav: true
---

# Conversation setup on a paired device

A new device needs to know which identities and conversations you trust. It does not need your saved messages or another device's live encryption state. An approving device can transfer that setup privately, then the new device obtains fresh encryption material and joins conversations through their normal rules.

Private replies keep their original two-person roles. Managed groups still require an authorized group admission. The client performs that work automatically where permitted, keeps each contact's progress separate and does not call setup finished just because a QR code was accepted. The [reply-aware transfer](#transfer-reply-aware-conversation-setup) can carry both earlier and newer conversation agreements.

The [current Encryption baseline](suite-profile.md#current-client-baseline) uses [configuration3](#transfer-asynchronous-scope-metadata) when snapshot setup is offered, and [own-setup0](#keep-setup-current-between-your-own-devices) for ongoing transfer under fresh authority. Configuration2/1/0 retain their exact older schemas. Installed metadata is neither correspondence import nor native send readiness; complete implementation remains separately required.

## Transfer setup without transferring correspondence

:::: {.details summary="Configuration version 1, manifest and encrypted parts"}

The original conversation-selection format is `security-configuration-v1`, selected by confidential pairing-setup records version `"1"`. It extends the [version-0 setup contract](identity-lifecycle.md#confidential-security-configuration-transfer) explicitly, not by accepting additional old fields. The same [current approved pairing](identity-lifecycle.md#current-pairing-and-multiple-administrators), source `enroll`/target `send` authority, exact endpoint/recipient binding, unchanged-binding ancestry, credible intervals, cancellation and conflict rules apply. Full state1 support is required by the current suite; a state0 experiment does not supply it.

### Exact signed records

Request, response and receipt retain their version-0 member sets and add exactly `configuration:"security-configuration-v1"`, using version `"1"` and the existing `pairing-setup-request`, `pairing-setup-response`, `pairing-setup-receipt` purposes. All three signature domains are now `email2/pairing-setup/{kind}/v1` with the existing NUL/U32-original-length framing. References are SHA256 of that framed input followed by the raw signature. Payload/signature wrappers, identifiers, exact original-byte retention and complete source/target authority remain unchanged. Unknown configuration values or mixed record versions are unsupported, never silently v0.

A client offering configuration1 implements it in each source and target role it claims. The reply-aware configuration2 contract below has its own exact role requirements. The target selects it with its signed version1 request; a version1 response must reference that exact request. An unsupported source leaves configuration pending/unsupported and must not answer with version0 under that request. Timeout, an unsigned capability hint or a relay receipt cannot authorize a downgrade. A separately selected legacy version0 transfer uses a fresh request/transfer/recipient and remains explicitly contacts/defaults-only; it cannot claim the version1 conversation-selection journey completed. Neither carrier reachability nor enrollment advertises configuration support.

The target's request still binds one fresh native age X25519 recipient and the exact pairing/session/source/target. The [selected age encoding and protection rules](encrypted-archives.md#create-a-recovery-kit-before-relying-on-backup) also govern these recipient fields and files; correspondence-archive retention and recovery permissions do not carry over. A source freezes one selected consistent snapshot and all part/response bytes before releasing any. It cannot change selection, parts, recipient or interval under the same transfer. Source disclosure and new target effects recheck original deadlines and current authority; independently confirmed pairing does not authorize an unlimited future export.

The response's ciphertext now encrypts a **manifest**, not the full configuration. Its decrypted JSON is exactly `{version,purpose,bytes,sha256,parts}`: version `"1"`, purpose `"pairing-configuration-manifest"`; bytes is the positive canonical uint64 total configuration length; sha256 is SHA256 of the exact full UTF-8 configuration bytes. Parts is a nonempty ordered array of exactly `{index,reference}`, index strings `"0"` through count−1 without gaps/duplicates and reference the corresponding signed part's record reference. A manifest is at most 1048576 decoded octets/depth 32, with the owning smaller ciphertext/wrapper budgets still applying. The total byte count must be greater than `(count−1)×65536` and at most `count×65536`, where count is the actual parts-array length. Values describe expected data, not permission to allocate that size.

Each part is a new source-signed wrapper `{payload,signature}`. Its exact payload is `{version,purpose,configuration,transfer,session,pairingResult,request,index,ciphertext}`: `"1"`, `"pairing-setup-part"`, `"security-configuration-v1"`, the original request's correlations, canonical uint64 index and padded-base64 binary age file. Sign with `email2/pairing-setup/part/v1`, NUL/U32-length/original bytes. It binds to the request rather than the response, avoiding a hash cycle: the later encrypted manifest commits every signed part reference. All parts use that request's selected recipient, with a **fresh independent age file** for each encryption; no reused encryption context or copied live message secret.

A decrypted part is exactly eight ASCII octets `EML2CFG1`, U64 big-endian index, U64 big-endian total part count, U32 big-endian chunk length and the chunk bytes. Chunk length is 1–65536; there are no trailing bytes or compression. All except the last chunk are 65536 octets. Each ciphertext and its signed wrapper fit the existing setup-response limits. The manifest plus part sequence allows a selected configuration larger than one response without increasing an individual public record limit.

The [rendezvous transport](pairing-transport.md) additionally carries `PUT/GET root + "/setup-part/" + transfer + "/" + index`, with the existing owner-PUT/target-GET authorization, immutable exact-slot rules and record bounds. These routes carry the original signed JSON part wrappers, never decrypted chunks. The source publishes the complete immutable parts then its manifest response; missing/reordered parts remain pending, not partial configuration. All records are fixed before publication, so retransmission does not re-encrypt an old part. A response reference is the signed manifest-response reference; staged/installed receipts retain that reference and do not enumerate or acknowledge a partial subset.

### Complete staging, including restart

The target validates its retained request, source signature/current authority and exact response binding before decrypting the manifest. It then validates each original part wrapper, exact request/index/reference and source authority before decrypting. Recheck original validity through processing time. Chunk count/index/framing, total bytes, whole digest and strict UTF-8 must agree. Enforce positive finite local aggregate bytes/parts, staging storage, CPU/time and parser/depth budgets before allocation and during assembly. Limit failure is an explicit incomplete/unsupported-size outcome, not truncation, a new scope or proof of maliciousness.

Keep partial encrypted/private staging and completed part receipts durable under the original transfer identity. No live contact/conversation/policy is installed before the **entire** configuration has been authenticated, assembled, parsed and staged with its immutable staged receipt. Reordered/exact duplicate parts do not duplicate content. Unknown/changed authenticated bytes retain conflict evidence. A crash resumes retained original records; it does not select a new manifest or recipient. The transfer-only age secret retires only after complete authenticated staging, cancellation or expiry; it cannot be destroyed after the first part or restored from a correspondence archive. Source/target secret custody and erasure remain their own implementation obligations.

Splitting a transfer into parts grants no unlimited lease or storage guarantee. Manifest/part unavailability, expiry or cancellation keeps the whole uninstalled transfer explicit. A new attempt has a fresh transfer/request/recipient and does not erase previously installed contacts or old uncertainty.

::::

## Which setup information is transferred

:::: {.details summary="Exact configuration and conversation-selection records"}

The assembled plaintext is exactly `{contacts,defaults,advertisements,conversations}`. Contacts/defaults retain the exact v0 schemas, reconciliation and original verification provenance, using the current identity-bundle lifecycle. The extra arrays are required and may be empty. They contain selected public security evidence, not correspondence history, private package keys, MLS checkpoints, drafts, credentials, queued sends or billing state.

### Public advertisements are cached evidence

Advertisements is sorted uniquely by digest. Each entry is exactly `{digest,assertion}`: digest SHA256 of original UTF-8 assertion-wrapper bytes and assertion their canonical padded base64. Each is an exact assertion8 under its owning schema; it must name a principal/mailbox selected in contacts or the selected conversations' peer evidence. Preserve original signature bytes and source provenance.

Validate actual signature, account authority, binding, mailbox association, version/operation support, freshness and package/control-key requirements before use. Transferred publication is not a new live response, allocation or proof that an old package remains unconsumed. Never copy the approving device's private/reserved/consumed package material or grant family. The new device obtains its own current authorized allocation/setup where that owning policy requires it. Unusable/expired cached evidence schedules automatic permitted discovery instead of inventing support or asking contacts to repeat an unchanged identity comparison.

### Ordinary conversation selection

Each ordinary record is exactly `{kind,conversation,principals,delivery,context,contextDigest}`. Kind is `"ordinary-v0"`; conversation is its ObjectId; principals is the distinct ASCII-sorted accepted principal audience of the source context, including the paired account principal. Delivery is its exact ordinary/private-copy object. Context is canonical padded base64 of exact accepted context8 application-context bytes; contextDigest is SHA256 of those bytes. Validate the complete syntax, conversation, ordinary ordering, owner/administrator and delivery/roster invariants. This is application metadata, not native group state.

The source attests that this was an accepted local selection; target provenance is **source-attested own-device setup**, not an independently checked historical peer receipt or evidence of current membership. A newly enrolled target can retain it to select the same ordinary conversation and, for a private conversation, the same exact originator/recipient pair. The current author's encrypted From still follows its own source account. A private recipient-owned return stream uses this trusted selection under the [private-reply rules](private-copies.md#private-replies-in-the-current-agreement), with fresh actual admission.

### Managed conversation selection and genesis

A managed record has all ordinary-record members with kind `"managed-v0"`, context8 managed ordering, and exactly five more: `group`, `genesis`, `roster`, `proofs`, `peers`. Group is canonical padded base64 of the exact nonempty MLS GroupId. Genesis is the existing 64-hex common-roster anchor. Roster is exactly `{payload,signature}` containing the original roster5 bytes and 128-hex signature, with their canonical base64/framing. Compute the common-roster anchor under its existing domain/U64-length framing and compare genesis. Group/conversation and immutable application/administrator/delivery fields must agree with the source's accepted current context; the certified witness policy may have changed through its real ordering path.

Proofs is an array of canonical padded-base64 original assertion8 wrappers, in the exact common-roster member order. It covers every original member once, matching that member’s payload digest/signature/key/package references under the common-roster contract. Historical expiry is not refreshed and these proofs do not supply current support for new admission. Extra, missing or substituted proof dependencies hold the record.

Peers is sorted uniquely by principal, covering exactly the union of genesis/current principal rosters, with each entry exactly `{principal,anchor,head,bundle}` under the contact identity-evidence grammars. Verify complete historical identity/creator signature/proof dependencies from source-attested accepted anchors and the owning common-roster rules. This special own-device import does not turn an arbitrary standalone roster or peer self-assertion into a trust anchor. Missing/malformed proof or a conflicting existing target pin holds that conversation.

The target may retain this exact validated genesis selection as its independently supplied **expected admission anchor**, with own-device transfer provenance. It does not install native MLS state, import old Welcome private keys, grant historical access or mark the new device a member. The source-approved historical anchor remains distinct from current authority and evidence that a complete native admission actually succeeded. Existing-group invitation8 and complete certified ordering path/Welcome/current support rules still determine real admission. New evidence cannot choose a competing branch merely because its epoch number is higher.

Conversations are sorted uniquely by `(conversation,kind,group)` using ASCII comparison; group is the empty comparison key for ordinary records. An ordinary and managed record cannot select the same conversation identity. Two managed records under that identity cannot name different groups/genesis; identical duplicates are invalid. Several ordinary sources may belong to one conversation, but export one selected representative context and its provenance, not competing “latest” records. A source with an unresolved mode/private-role/native branch conflict cannot export it as ready selected setup.

### Reconcile each selection without rewriting local trust

Authenticate and validate the complete configuration, then atomically commit its private staging record and immutable staged receipt before any live installation, following the [ordered acceptance procedure](identity-lifecycle.md#accept-reconcile-and-report-readiness). A failed staging commit cannot leave a peer pin, conversation selection or default installed. Then reconcile contacts and conversation selections in distinct durable transactions under current own-device authority, original request deadline, cancellation and relevant local generation checks. Record each result and provenance. Install defaults only under the v0 conflict/explicit-local-setting rules. Do not overwrite another existing conversation mode, private role pair, managed group/genesis, peer pin, verification withdrawal, current revocation or retired local instance. Keep conflicts/unknown ancestry held for explicit owning reconciliation; source signature is no override.

Source-attested ordinary context grants no current module support or automatic history. Managed genesis selection grants no signing/voting/admin power. Locally known newer authority remains effective. An existing current accepted group needs its real transition path, not replacement by the transferred context. Only after every selected contact, conversation and default has completed its reconciliation may the installed receipt commit; it means this selected setup was installed, **not** that mailbox login, fresh packages or group admission are complete. Partial success preserves per-contact/per-conversation outcomes; it does not block an independently ready contact or claim the entire selection installed.

::::

## When only one contact needs attention

First validate and privately stage the entire selected transfer. If a part is missing, a signature fails or the selected format contains an unsupported record, keep that transfer uninstalled. A valid source signature cannot make an unknown verification method safe to interpret. Do not skip that record, install a prefix or report the selected setup as complete.

After complete staging, reconcile each contact and conversation with the new device's existing decisions. A conflicting pin, withdrawn verification or unavailable group admission holds the affected destination. It need not stop another destination whose own checks succeed. Existing independently authorized contacts also remain usable while a different transfer is incomplete; transfer failure does not erase their trust or extend it.

> [!ex] One contact is ready; another needs attention
> Alice pairs a new device and transfers valid setup for Bob and Carol. Bob's identity agrees with the device's records, so his setup can be installed and fresh encryption prepared. The device already holds a conflicting identity for Carol, so Carol stays held. The overall transfer remains staged rather than fully installed. If the transfer instead contains a verification method outside its selected schema, neither contact is installed from that transfer; their independently existing setup remains unchanged.

A source can prepare a separately authorized selection that it can represent completely, using a fresh transfer/request/recipient and the original disclosure rules. It cannot silently omit an intended contact or verification decision, downgrade that contact's policy, renew the old attempt's deadline or describe the smaller selection as completion of the original one. Supporting a future record requires a separately defined compatible transfer contract; an unknown enum value is not an extension mechanism.

## Continue automatically to usable sending

The client keeps progressing through account access, trusted setup, fresh keys and any required group admission. A wait for one group or contact must not stop an unrelated contact that is ready. Message-history synchronization can run separately; it is never a condition for future encrypted sending.

For current configuration3, use the [actual future-sending procedure](#continue-to-actual-future-sending): qualify the actual selected delivery cohort under assertion10 and the fixed readable application, while other intended recipients can remain pending. The retained configuration1 procedure below selects assertion8 and its common operation set; configuration2 applies its exact agreement rows separately. No older procedure reduces the current readable vocabulary or makes every intended slot ready before an eligible delivery can proceed.

:::: {.details summary="Retained configuration1 preparation jobs and readiness algorithm"}

For each selected contact or explicit compose/conversation intent, retain a local preparation job bound to the own account/profile/device, accepted pairing/setup provenance, exact intended principals/mailboxes, selected ordinary/managed mode, required privacy/freshness policy and any existing private/group selection. This is local work state, not a new peer request or universal background permission. Remembered setup/compose permission authorizes routine work; a received message cannot enable it.

1. **Account and identity.** Require current accepted own enrollment, actual possession of the target's own key, send/receive roles as needed and independently authorized mailbox/submission access to the paired account. Complete the selected provider/OS login and fresh provider/relay links where needed. A rendezvous token, source account password, management token for another resource or installed receipt cannot substitute. Account change invalidates affected preparation; it does not rewrite submitted bytes or reuse another account's cursor/grants.
2. **Trust and policy.** Reconcile the selected contact associations/current accepted identity and inherited verification under original scope. Preserve conflicts, local preference overrides, source withdrawals and existing revocations. Do not demand routine human re-verification of unchanged contacts. A genuine continuity break follows the owning policy and keeps only affected work held.
3. **Usable current setup.** Use valid retained evidence and automatically execute permitted discovery/bootstrap/allocation/freshness steps for every intended endpoint. Recheck package receiving promises, one-use allocation/custody and actual exact signed support. No cached boolean or transferred public assertion claims a current remote allocation/live response. Missing evidence, resource budget or a required live peer offline remains pending with bounded retries, never plaintext fallback inferred from timeout.
4. **Ordinary selection.** Select the current common operation set for the actual new source/audience under assertion8. Retain an existing trusted private pair/conversation where selected; create a fresh owner-bound source from the new device's own state. Current stream admission can proceed asynchronously from usable published material; it does not need another device's checkpoint or an ordering vote. A changed principal audience gets its real new stream. Unknown private-role provenance stays held rather than becoming an ordinary public copy.
5. **Managed admission.** Publish/stage a fresh package and automatically request/schedule the existing authorized administrator/certified membership and Welcome workflow for the actual new device, using its transferred expected genesis only as selection evidence. Reuse the current owning mail/control carriers; no generic unauthenticated join callback is introduced. Missing administrator/quorum/current support/admission evidence waits for that managed conversation; it does not switch its mode or stop other ordinary contacts.
6. **Final eligibility.** Require actual native local admission/owner preparation, current account/source/recipient associations, exact negotiated context, route/privacy/disclosure/freshness and all receiving dependencies. Record this job's ready evidence/dependency generations atomically. No test-send, automatic human message or history export is required to mark local eligibility. Ready does not claim remote delivery, remote installation or human reading; each actual send still runs the serialized preparation and immediate pre-DATA authorization checks.

Job outcomes distinguish account access pending, configuration/evidence pending, contact conflict, required setup/live peer pending, private-context pending, managed admission pending, ready, cancelled and policy/resource held. These are local categories, not new wire values or a linear global progress ladder. Persist the outstanding work and dependencies across restart. Prefer one in-flight attempt per owning operation, finite backoff/budgets and original immutable request identities. Retry must not re-enroll, extend old deadlines, consume a package twice or create a replacement service action.

A dependency change makes a previous ready observation stale for affected work. Reevaluate automatically under existing permission; source/target revocation or pairing/setup conflict cannot leave a permanently green ready flag. Source disclosure/target installation expiry and provider credential expiry retain their separate clocks. Local cancellation stops new work and applies each owning operation's uncertainty/revocation procedure; it cannot promise remote enrollment, upload or admission was undone.

Missing history is shown as unavailable history. It cannot supply an invented reply parent, answer target, source quotation or old checkpoint. A new message can use an accepted ordinary conversation selection without copying old correspondence; replying to an old exact question still needs its actual authorized evidence. The client does not create a visible duplicate conversation to disguise an unfinished managed admission. None of these protocol steps depends on a commercial storage plan.

::::

## Transfer reply-aware conversation setup

A paired device can carry over the setup needed for conversations with explicit reply policies. It preserves which agreement each conversation uses, rather than assuming that all conversations use the newest format. Older and reply-aware conversations can coexist without changing one another.

The new device still obtains its own keys, account access and conversation admission. It does not inherit another device's live encryption state or acquire old messages. Ordinary encrypted sending can become ready independently of history synchronization and of a managed group that is still waiting for admission.

::: {.details summary="Transfer format, signed records and encrypted parts"}

**Selection.** The successor is `security-configuration-v2`, selected by confidential pairing-setup request/response/receipt/part records version `"2"`. It retains version1's complete member inventories, with `configuration` exactly `"security-configuration-v2"` and each record's own version exactly `"2"`. Purposes, source/target/session/pairingResult/request/response correlations, endpoint identities, fresh native age X25519 recipient and original credible intervals remain unchanged. Signature domains are `mail/pairing-setup/request/v2`, `mail/pairing-setup/response/v2`, `mail/pairing-setup/receipt/v2` and `mail/pairing-setup/part/v2`. References retain SHA256 of the exact domain/NUL/U32-length/original-payload framing followed by the raw 64 signature octets. No signed record is rewritten or checked under a different version.

A client claiming reply-aware own-device setup implements configuration2 in each source/target role it advertises. The target's signed request selects2 and binds the independently accepted current pairing; enrollment or rendezvous access alone advertises no configuration support. An unsupported source holds that request and cannot answer with1/0. A separately authorized legacy transfer uses a fresh request, transfer and recipient, retains its original capability limits and cannot claim the reply-aware conversation selections were transferred. Do not silently omit an intended selection to report the old transfer as complete.

**Manifest and parts.** The encrypted manifest has exactly version1's `version`, `purpose`, `bytes`, `sha256`, `parts` members, with version `"2"` and the same pairing-configuration-manifest purpose. Each signed part has exactly version1's fields, correlations and index grammar, with version/configuration2 above. Its decrypted binary frame uses magic `EML2CFG2` and otherwise the same U64 index, U64 count, U32 length and chunk layout with 1–65536 octets. Every nonfinal chunk contains 65,536 octets; no compression or trailing bytes is allowed. Whole-byte/digest/UTF-8 checks, independent fresh age encryption for each file, original signed-part references, aggregate local budgets and existing individual record limits remain mandatory. Multipart carriage cannot enlarge an individual record or bypass its authority interval.

The same rendezvous setup-request/response/receipt and setup-part routes carry the original version2 wrappers. Their owner/target token authorization, exact immutable slot state and bounds remain unchanged. Transfer/request identities are not partitioned by configuration version: changing format cannot reuse an occupied slot, revive a cancelled transfer or extend an expired pairing. The complete target request selects the only permitted response/part/receipt version. There is no parser fallback to1 after a failed version2 record.

**Staging.** Validate complete original signatures, current source enroll/target send authority, accepted current pairing/binding0/state1 lineage, exact session/endpoints/recipient, all request/manifest/part references and original deadlines before accepting the assembled plaintext. The target commits complete authenticated private staging and its immutable staged receipt before any contact, default or conversation effect. Reordered parts, restart, expiry, cancellation, conflict, limits and transfer-secret retirement retain version1's exact safe outcomes. A known current revocation, verification withdrawal or identity conflict is not overwritten by valid historical transfer bytes. No source/target live signing, MLS, route, credential or archive private key is transferred.

:::

::: {.details summary="Conversation selections and supporting evidence"}

The assembled plaintext still has exactly `contacts`, `defaults`, `advertisements` and `conversations`. Contacts/defaults keep their complete version1 meaning, including original comparison/verification scope and current identity-bundle validation. The transfer contains no message history, reply text, quotations, drafts, queued actions, provider token families, old admission secrets, billing or backup entitlements.

**Advertisements.** Entries remain exactly digest/assertion, sorted uniquely by original wrapper digest. Each original wrapper is explicitly assertion8 or assertion9, with its own exact schema/domain, reference and authority. A target implementing configuration2 validates both metadata grammars; this is not a claim that it can execute every optional interaction or join every selected group. An assertion for an unknown version is unsupported, not converted to a familiar one. Current receiving support, package availability/allocation, freshness and mailbox association still need their independent checks before use. Transferred assertion8 cannot supply assertion9 support. Two wrappers around the same native package reference remain one piece of single-use admission material, not a separate allocation for each agreement.

**Conversation records.** Each ordinary or managed record has exactly its version1 member inventory plus required `agreement`. Ordinary kind remains `"ordinary-v0"`; managed kind remains `"managed-v0"`. These values describe mode, not a configuration or application version. Agreement selects exactly one of:

| `agreement` | Context in `context` | Application | Managed genesis/proofs | Actual admission/control |
| --- | --- | --- | --- | --- |
| `email2-conversation-v0` | Exact context8 | Envelope4/mime-suite-v0 and its complete operation set | Original roster5 and assertion8 wrappers | Initial8/established8, ordinary controls0 or exchange2/final carrier3, sealed-control-v0 |
| `mail-conversation-v1` | Exact context9 | Envelope5/mime-suite-v1 and its complete operation set | Original roster6 and assertion9 wrappers | Initial9/established9, ordinary controls1 or exchange3/final carrier4, sealed-control-v1 |

Both rows retain the existing MLS version/suite, full immutable context, administrator/owner, actual audience, private-pair, peer evidence, canonical address, scope, genesis/GroupId and proof requirements. ContextDigest is SHA256 of the exact original context bytes. Roster6 uses its new signature domain and original bytes; its creation anchor keeps the existing anchor0 construction. Historical proofs retain their original expiry/provenance and do not become current advertisements, unused packages or live responses. Missing or mismatched row dependencies hold that selection; no mixed8/9 proof set is accepted for one genesis.

A managed record's original group/genesis and full proof chain remain source-attested expected admission evidence, not an imported checkpoint, membership, vote, administrator privilege or independent historical peer receipt. A source signature cannot resolve an existing target's conflicting group, mode, private pair, peer pin or retired instance. Actual established admission still validates every required native Welcome/GroupInfo, ordering transition, current endpoint and exact selected tuple.

**One explicit selection per conversation.** Preserve the existing sorting/uniqueness rules and export one deliberately selected representative ordinary context, not competing “latest” records. If an ordinary conversation contains streams under both agreements, record the one selected for future composition under actual local policy. Do not choose by the highest version/epoch alone or silently substitute older support for a required reply policy. Other streams' history and authority are not merged or granted by that selection. Managed application migration remains a distinct admitted conversation; a configuration transfer cannot change a managed group's application in place.

No per-message reply intent is invented from this metadata. A device without the original message has no verified old reply target, answer/control or source quotation. It can compose a fresh authorized root where eligible. Loading the transfer does not replay earlier replies, reactions, service actions, hosted jobs or outbox entries.

:::

::: {.details summary="Reconcile, acquire current setup and report readiness"}

Keep version1's ordered private staging, per-record reconciliation and final installed receipt. Malformed or unsupported configuration2 metadata prevents complete staging; it cannot be installed through a permissive partial parser. Once the complete known schema is staged, a current trust/policy or native-admission hold remains specific to the affected selection. Reconcile each selected agreement, context and source provenance against current local generations and authority before installation. Matching a conversation ID or a newer source signature cannot override another trusted mode, private pair, genesis, revoked device or verification decision. Partial success remains per contact/conversation; unrelated ready destinations need not wait for a held group.

For each preparation job, additionally retain the exact selected agreement and required composition/reply policy as immutable dependencies. Execute the existing readiness algorithm with the table's exact row. The older row uses its original acquisition/admission bindings. The retained reply-aware row obtains original assertion9 through the [provider](provider-control.md#reply-aware-known-pair-exchanges), [bootstrap](bootstrap.md#provider-setup-for-declared-reply-policies) or [mailbox setup1](mailbox-setup.md#set-up-the-declared-reply-policy) path, selects the exact common operation tuple across all intended devices, and uses the reply-aware admission/control/carrier rules. A temporary mailbox-attempt assertion cannot become the new device's ordinary receiving publication.

Account/OS login and fresh resource-scoped account/device linking remain independently required; no password, provider grant, source session or Apple/other password synchronization enrolls the device. Independently confirmed current pairing can install the selected trust/setup so unchanged contacts need not repeat their comparison. The new device creates and retains its own live material and obtains real ordinary owner-stream preparation or managed group admission before send-ready is reported.

Missing native support, current package, admin/quorum, account access, verification or required route/freshness leaves the affected job held/pending. A stale ready observation is invalidated by dependency changes. A different agreement can be chosen only through independently authorized composition/migration preserving the actual audience, protection and required reply semantics; retry or timeout cannot perform that conversion. Every actual send still executes its current scoped-copy, revision, membership, privacy/disclosure and final-release checks. An installed receipt is neither send-ready nor remote delivery.

The same old-history boundary remains absolute: no message synchronization, archive purchase, cloud plan or transfer of another device's keys is needed merely to progress future sending. Historical reading and recovery have their own independently authorized contracts and may remain unavailable.

**Successor acceptance.** Required successor cases include mixed old/reply-aware selections in one transfer, exact agreement/context/proof mismatches, unknown version, wrong request/part/manifest domains or magic, original-byte commitments, missing/duplicate/reordered chunks, source/target revocation during staging/reconciliation, interrupted retirement and stale readiness. Exercise a new device sending to an unchanged contact, a private return stream and real managed admission without importing history. Component syntax/byte assembly is not that joined current pairing-to-send journey.

:::

## Acceptance and implementation boundary

Required cases include complete multipart setup with reordered/missing/tampered parts, exact retry/crash/expiry/cancellation, different private-role pair, unknown/newer local context, conflicting managed genesis, historical proof expiry versus current authority, restored/retired native state, cached consumed setup, mixed endpoint support, provider login denial, source revocation during reconciliation and ready-state dependency changes. Exercise actual encrypted sending from the new device to an unchanged verified contact without history copying, an Alice/private-recipient return stream and real managed fresh-device admission, alongside another contact whose setup remains pending.

The existing version-0 experiments cover actual independent pairing, signatures, age encryption, private staging and selected contact/verification installation. They do not implement the complete version1 or [reply-aware version2](#transfer-reply-aware-conversation-setup) schema/genesis/staging workflow or automatic scheduler. A codec or trusted-input assembly helper is not proof of current identity/admission, protected key custody, public rendezvous interoperability or QR-to-ready acceptance. These implementation/evidence limits do not remove the required journey or authorize a paid-history prerequisite.


## Transfer asynchronous scope metadata

A newly paired device can know who belongs to an intended conversation without receiving the old messages that established it. Configuration3 transfers those accepted setup observations privately. The new device still obtains its own current keys and actual admission; a missing old question remains missing, while an eligible new message can use the transferred scope.

This is the selected own-device setup binding for [mail-conversation-v2](suite-profile.md#asynchronous-protected-agreement), within the same Email/2 draft. It is the current configuration binding; it does not establish a complete implementation. Configuration2/1/0 retain their exact formats and claims.

::: {.details summary="Exact configuration3 records and contents"}

The format is `security-configuration-v3`. Request, response, receipt and part have exactly configuration2’s member inventories and purposes, with version `"3"` and configuration `"security-configuration-v3"`. Their signature domains are `mail/pairing-setup/request/v3`, `mail/pairing-setup/response/v3`, `mail/pairing-setup/receipt/v3` and `mail/pairing-setup/part/v3`, using the unchanged Ed25519 NUL/U32-length/original-byte framing and signed-record reference construction. The encrypted manifest has version `"3"` and its unchanged five-member inventory. Each decrypted part frame uses exact eight-octet magic `MAILCFG3`, followed by the existing U64 index/count, U32 length and 1–65536-octet chunk framing. Nonfinal chunks are full; no compression or trailing bytes is allowed.

Original approved pairing/session/result, exact same-account source/target, fresh target-only native age recipient, source enroll/target send authority, unchanged-binding ancestry, current credible intervals and source disclosure permission remain required. The complete transfer is frozen before publication and completely authenticated/staged before any live reconciliation. Unknown versions or mixed manifests/parts cannot be relabeled. Current roles, original deadlines, cancellation, conflict, transfer-secret retirement and immutable retry are not reset by a new capability or part arrival.

The complete plaintext has exactly `contacts`, `defaults`, `advertisements`, `conversations` and `scopes`. Contacts/defaults retain their existing exact schemas and verification provenance. Advertisements may be original assertion8, assertion9 or assertion10 wrappers, each under its own exact signature/schema. Cached publication is not a live response, unused package, allocation or current readiness. Complete known schema support is required before staging; a source cannot omit an unsupported selected record to report this transfer complete.

Conversation records retain configuration2’s exact ordinary/managed inventories. Agreement additionally admits `"mail-conversation-v2"`, requiring context10/envelope6/mime-suite-v2, original roster7/assertion10 managed proof dependencies, initial10/established10, ordinary controls2 or exchange4/final5 and sealed2. Earlier rows remain unchanged and cannot supply those versions. The source-attested representative context, private pair, actual audience, group/genesis, peer evidence and independent native admission boundaries still apply. The new device does not import an old stream, checkpoint, package secret, draft, queue, credential or provider token.

Scopes is an array of the records below, ordered uniquely by `(root.conversation, root.principal, root.event, origin.device, origin.id)`. Several independently attributed observations of the same scope can be retained; an identical ordering key cannot be duplicated. Each root conversation must have a selected mail-conversation-v2 conversation record. An empty array is valid and conveys no scope knowledge, rather than permission to invent it.

| Member | Required meaning |
| --- | --- |
| `root` | Exact scope-root logical reference under authored0’s grammar. |
| `definition` | Complete intended-recipients0 definition with that exact root, author slot and ordered slots. It contains no human message body, subject, quotations or per-message reply intent. |
| `creator` | Historical public identity evidence in the exact form below. |
| `bindings` | Distinct slot-sorted array of exact slot/principal objects, for retained unconflicted creator-authorized bindings. |
| `conflicts` | Distinct ASCII-sorted slot IDs with known unresolved binding conflict. Every ID belongs to the definition; none appears in bindings. |
| `rootConflict` | JSON boolean recording known conflict affecting this scope root or its accepted observation. False cannot clear another retained conflict. |
| `origin` | Exactly device/id: original own-account observation device and stable nonzero observation ObjectId. |

Creator has exactly `principal`, `anchor`, `head` and `bundles`. Principal equals root.principal. Anchor is the source’s retained creator identity anchor; head names the accepted historical author state used for its observation, not a claim of current operational authority. Bundles is a nonempty digest-sorted, duplicate-free array of exact digest/bundle objects: SHA256 of the original bundle1 UTF-8 octets and their canonical padded base64. Each bundle retains its independent size/schema/signature bounds. Together they provide the anchor/head chain, original relevant binding evidence and every locally known relevant negative branch, revocation or retirement; a bounded partial bundle cannot be called complete history. Aggregate transfer budgets remain separately enforced.

Validate that public history in isolated staging under the source-attested anchor, without manufacturing a trusted historical signing time. Preserve known negative identity evidence and existing target pins/frontiers; the selected historical head cannot overwrite them. This may supply an expected creator-anchor constraint through the approved own-device transfer, but not a mailbox association, human comparison or current receiving advertisement. Those still require their own selected contact/current-setup reconciliation.

An origin device belongs to the paired account’s accepted history; it is not the peer creator. Namespace its observation by the paired account principal, origin.device and origin.id. Allocate the ID durably when first recording the accepted setup observation, and preserve it on onward own-device transfer. Root and definition are immutable under that observation identity. The currently authorized source attests retained knowledge; an origin label is not an independent peer signature or evidence that the new device received the old message.

Origin attributes the frozen root/definition observation. It does not claim that its device learned every later binding or conflict. The currently signed transfer attests the selected aggregate knowledge; the target retains each incoming fact’s transfer/source provenance separately from the original observation.

Source observations must come from accepted live setup state or previously accepted own-device setup provenance. Reading an archive, parsing a message-shaped file or receiving an arbitrary peer object cannot create that provenance. A source exports a consistent current selected snapshot, including all locally known relevant conflict/withdrawal facts; no receipt promises global knowledge or absence of withheld remote changes.

A binding names a definition slot and one valid principal. It must agree with a nonempty expected principal; an initially unknown slot obtains a binding only from previously accepted creator-authorized resolution, not the source’s own guess from its contact list. Multiple conflicting values are summarized in conflicts rather than choosing one. Transfer cannot rename an unresolved mailbox, add a slot or grant another participant authority to resolve it.

For a private-copy conversation, the scope creator and every slot’s single expected principal must belong to its exact retained originator/recipient pair. No unresolved principal, outside participant, visible-discussion roster or public source link is admissible in that private scope definition. Bindings likewise stay within the pair. Known slot/root conflict can be transferred as held metadata without disclosing another candidate participant. Source checks this isolation before encrypting, as well as target validation before installation.

:::

::: {.details summary="Reconcile scope facts without importing messages or authority"}

First validate and privately stage the complete configuration3 under its actual approved own-device transfer. Malformed scope, unsupported record, missing public proof, wrong private pair or failed part/manifest check prevents complete staging and leaves live state unchanged. Do not install a valid prefix. Retire the transfer-only secret after the staged record and receipt commit, then reconcile under current own-device authority, original deadline and cancellation checks.

Maintain a separate scope-setup ledger. Its metadata does not reserve an accepted authored-message identity or create the root message in a conversation. For definition equality, compare the complete typed fields, ordered slots and exact decoded strings; different source serialization alone is not a different scope. Every original signed transfer record still retains its exact bytes and independent retry/conflict identity.

1. Reconcile the selected conversation’s mode/private role/genesis and relevant creator/contact evidence under their own rules. Conflicting local trust or incompatible selection remains held; source signature is not an override.
2. Merge each immutable origin observation with its transfer provenance. A different root or definition under an already retained origin identity is observation-conflict evidence. Retain variants and hold every affected scope; do not silently replace an old observation or describe this alone as two peer-signed messages.
3. Different valid definitions for one scope root hold that scope. Reuse of one creator/event across conversations also holds all affected scope roots, without exposing another conversation’s contents through the current view. Same definition from several origins is repeated knowledge, not several groups.
4. Merge expected/bound principal constraints and known conflict flags. Different unconflicted incoming knowledge versus retained knowledge marks that slot conflicted; it never selects an arrival-order or newer-source winner. Root conflict and slot-conflict knowledge survive a new source device, observation ID or transfer. Missing facts and false flags cannot clear them.
5. Commit the scope facts, provenance and resulting blocked constraints atomically. Slot conflicts hold only work requiring those slots; unaffected recipients can still progress. Root/provenance conflict holds this scope’s use without stopping unrelated contacts/scopes. Recheck dependency generations before publishing a view or preparing content from them.

### Compare creator history without changing pins {#scope-creator-history-comparison}

Keep the transferred creator `anchor`, selected `head` and original public proofs. The anchor can be an accepted successor state, as described in [contact pin preservation](identity-lifecycle.md#accept-reconcile-and-report-readiness); it need not be genesis.

When comparing that evidence with the target’s retained identity, validate the complete original history from the exact source pin and head. Derive genesis only to compare identity namespaces. Unequal source and target pins alone do not establish different genesis states. A genuinely different genesis under the same claimed principal holds the affected scope.

Preserve both accepted pins, known negative facts and separate contact-policy holds. This comparison grants no current creator authority and does not merge histories or refresh proof intervals. Independently attributed scope observations still retain their exact creator-anchor constraints and existing provenance-conflict rules.

A successfully retained conflicted fact is not usable permission. A scope’s reconciliation can complete with explicit blocked constraints; the installed receipt only reports that selected setup facts were reconciled, not that those destinations are ready. Missing/malformed or still-unreconciled records prevent the complete installed receipt. Existing contact/conversation/default rules remain unchanged, and per-destination progress never waits merely for a global receipt label.

An existing scope selection in a new authored record may resolve through this accepted own-device setup ledger even without the original human root. Provenance remains source-attested own-device setup. Validate the new native author, actual slot map and operation independently. Metadata cannot supply the old root’s text, reply policy, quoted range, answer/control target, native sender receipt or service outcome. A missing primary parent remains pending; it is not materialized from the scope reference. A deliberately composed fresh message with empty replyTo may use eligible transferred scope knowledge.

If an independently accepted creator root later arrives, compare its definition against the retained metadata. Equal typed meaning corroborates setup; disagreement retains a scope/provenance conflict. Do not rewrite the creator’s original event bytes, discard a variant or fabricate independently verified peer receipt history from the own-device statement.

:::

### Continue to actual future sending

Resolve current contact/mailbox associations, original receiving publications, actual selected device support, privacy routes and independent native admission for each actual delivery. V2 uses the fixed readable application and preserves each device’s interactions instead of an optional-block intersection. Unresolved invitees remain pending; metadata cannot manufacture their principal, key or setup. Managed and private contexts keep their real admission/role rules.

Use actual new-device keys and current authority. Installed metadata, a copied creator bundle, prior pairing or archive import cannot mark the device a member or restore a live outbox. Existing knowledge avoids repeating an unchanged comparison; missing/currently conflicting evidence holds the affected work. The protocol’s setup/readiness proof requires no old correspondence, cloud-history entitlement or recovery of another device’s live secrets. Product and account-access restrictions remain separate operational facts; they are not cryptographic authority or a prescription of provider pricing.

This transfer covers the explicitly selected approved setup snapshot. It does not claim complete knowledge of scopes learned elsewhere later. The [ongoing own-device exchange](#keep-setup-current-between-your-own-devices) obtains a newly authorized snapshot when needed. A newly encountered scope still needs independently authorized setup metadata; do not fetch or transfer its old human root automatically to obtain it. The [per-delivery provider/mailbox acquisition binding](first-contact-setup.md#acquisition-for-independently-ready-deliveries) applies to this selected snapshot. The ongoing exchange has its own current authority and carriage; joined pairing/setup-to-native-send evidence remains part of D-43 integration.



## Keep setup current between your own devices

Your phone can ask another authorized device for setup learned since pairing. It can request a fresh selected snapshot, or just the conversation definitions it needs. It receives setup metadata rather than the old messages, creates its own live encryption state and performs the normal sending checks.

Any currently eligible administrator can provide this setup; the device that originally approved pairing has no permanent special role. An enabled local policy may authorize routine own-device requests and responses without another QR scan. If no eligible source is reachable, missing setup remains pending. Other usable conversations keep working.

This selects `own-setup-v0` within the asynchronous agreement. It transfers a configuration3 snapshot or its explicitly scoped metadata projection under fresh own-device authority, not a reused pairing lease or a new enrollment. It is not correspondence synchronization, a live-key backup, a source directory or a promise that all devices know the same facts.

::: {.details summary="Current authority, selection and exact own-setup request"}

Both endpoints belong to the same independently pinned account principal and are distinct currently authorized devices. Source means the providing administrator throughout; target means the requesting device, including in responses and receipts. Each endpoint is exactly principal/device/state/binding/key under the confidential-setup endpoint grammar. Its original state/binding/key remains frozen for the transfer. Current unchanged-binding ancestry and all known negative/fork/retirement facts still apply; an unrelated accepted addition need not restart it. An incoming record or identity bundle cannot establish a new account anchor.

Source requires current enroll authority for configuration disclosure. Target requires current send authority to request/install it and receive authority for its selected receiving assertion. The source also needs a usable receiving channel to accept automatic requests; independent mailbox/relay operation permissions remain required. Administrative signing authority cannot become permission to send human application content or borrow a transport credential. A revoked, conflicted or repaired/replaced binding does not survive through an old pairing result, a same-account string or a recent signature.

Automatic own-device setup follows an explicit, adjustable local policy; an account connection or pairing flow can configure it as part of its authorized setup. A device grant alone, opening mail, observing a peer reference or receiving a request cannot enable or widen that policy. A locally selected setup/readiness job may schedule bounded requests under it. Source policy independently permits the exact current target, requested selection and disclosure; sender-controlled fields cannot grant permission. Own-device requests do not ask a correspondent to disclose metadata and never resolve another creator's unknown invitation slot by guesswork.

Before creating a request, obtain a valid original assertion10/control key for the selected own source under current pinned identity and receiving rules. Retained configuration/publication or independently enabled acquisition can supply candidates, not authority by itself. No public presence/device directory is introduced. The requesting target creates and privately persists a fresh native age X25519 recipient/secret, its own valid ordinary receiving assertion10/control key, the exact selection and finite request interval before releasing the request. Do not reuse a pairing/archive/message secret or an expired rendezvous token.

Every owning record is a payload/signature wrapper, using strict original-byte JSON/base64, scalar/depth, Ed25519 NUL/U32-length framing and signed-record reference rules of confidential setup. The signature domain is `mail/own-setup/{kind}/v0`, with kind request, response, part or receipt.

All four own-setup wrappers have an encoded UTF-8 ceiling of 4194304 octets. Each decoded signed payload is at most 2097152 octets, each original decoded advertisement wrapper at most 1048576, and each decoded binary age ciphertext at most 2097152. Wrapper, payload and every decoded advertisement/identity object independently obey depth32 and their stricter owning schema bounds. The manifest plaintext retains its separate 1048576 ceiling; a part frame is at most 65564 octets including its header. These are own-setup processing bounds, not inherited constants from older pairing experiments or per-account storage quotas. All bounds apply together; satisfying one maximum does not exempt another or promise that every combination of maximum-sized fields fits.

Before base64 allocation, enforce the encoded ceiling derived from the applicable decoded limit, then canonical decoding and the decoded limit itself. Apply the outer sealed body's 4194304 ceiling and full container limits independently. Additional finite local aggregate/CPU/storage budgets may report incomplete or unsupported size without accepting a prefix, truncating a proof or raising these wire ceilings.
 A reference is SHA256 of that complete signing input followed by its raw 64-byte signature. No original pairing record is relabeled as one of these proofs.

The request payload has exactly these members:

| Member | Required meaning |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"own-setup-request"`. |
| `configuration` | Exactly security-configuration-v3 for snapshot selection, or scope-configuration-v0 for scopes selection. |
| `transfer` | Fresh nonzero ObjectId; allocated durably by the target. |
| `nonce` | Fresh 32 random octets, as 64 lowercase hexadecimal characters. |
| `source` | Exact selected source endpoint. |
| `target` | Exact requesting target endpoint. |
| `selection` | One exact object described below. |
| `recipient` | One fresh valid native age X25519 public recipient. |
| `advertisement` | Canonical padded base64 of the target's complete original assertion10 wrapper. |
| `notBefore` | Original interval start, canonical uint64 epoch-second string. |
| `notAfter` | Original finite interval end, in the same grammar. |

Selection is exactly `{"kind":"snapshot"}` or exactly `{"kind":"scopes","roots":[...]}`. Roots is a nonempty array of distinct full scope-root logical references, ordered by conversation/principal/event. Snapshot requests the source's permitted consistent selected setup; it does not assert global account completeness. The [scopes selection example](examples/async-own-setup-selection.json) names one existing root; it is a selection object, not a signed request. Scopes requests only those roots and their necessary contact/identity/conversation/proof dependencies. It authorizes no additional scope, correspondence, action, draft, outbox or live private state. Missing root content is not requested as a substitute.

The target signs the request. Its advertisement must match the exact target endpoint, same account principal, current unchanged receive binding and original key custody/validity promises. This is its ordinary receiving assertion, not an attempt-only mailbox-setup assertion. The source verifies it independently before selecting a response key. All new processing/release must fit the original request interval, the applicable current role/binding intervals and each selected key's publication/receiving rules. Source/target enforce their finite request-lifetime, work and staging budgets; a request cannot enlarge them. Retry, another source or a fresh receiving advertisement cannot edit the original request or renew its age/recipient/deadline.

:::

::: {.details summary="Response, encrypted manifest, parts and receipts"}

The source authenticates current same-account authority and disclosure policy before reserving the transfer or preparing any response. It freezes one consistent selected snapshot or scoped projection, target recipient, response and complete part sequence. Source observations/provenance, historical public bundles, negative facts, private-pair isolation and no-correspondence rules retain configuration3's exact requirements. Own-setup authorization replaces only its original pairing/session/result authorization; the data/merge rules are not weakened.

| Record | Complete payload inventory | Signer |
| --- | --- | --- |
| Response | version, purpose, configuration, transfer, request, source, target, unavailable, ciphertext | Source |
| Part | version, purpose, configuration, transfer, request, source, target, index, ciphertext | Source |
| Receipt | version, purpose, configuration, transfer, request, response, source, target, result | Target |

Version/configuration and endpoint/transfer values equal the request. Purpose is own-setup-response, own-setup-part or own-setup-receipt respectively. Request is its exact signed-record reference, which commits the nonce, interval, selection, recipient and advertisement. Response in a receipt is the complete signed response reference. Index is canonical uint64. Result is exactly staged or installed. Unknown/missing/null/duplicate members fail; no session/pairingResult or inferred default is inserted.

Unavailable is an array of distinct scope-root references under the request's ordering. It is empty for snapshot selection; for scopes selection it is a subset of the exact requested roots. It reports only that this source cannot supply those roots through this transfer, not permanent absence or global agreement. Retain known negative facts. For each returned root, all locally known relevant observations/conflicts and required proof dependencies are included; omission cannot clear target knowledge.

Response ciphertext is canonical padded base64 of one complete native age encrypted binary manifest for the request's sole recipient. The decrypted manifest has exactly version/purpose/bytes/sha256/parts, using version `"0"` and purpose `"own-configuration-manifest"`. The positive total byte count, full original configuration digest and ordered index/reference part array use configuration3's exact multipart lengths, consistency, per-record and aggregate staging checks. Manifest size is at most 1048576 decoded octets/depth32, with all tighter enclosing limits still applying. Advertised sizes never authorize an allocation.

Each part's ciphertext encrypts exactly the configuration3 MAILCFG3/U64-index/U64-count/U32-length/chunk frame, using a fresh independent age file for that part. Chunk size remains 1–65536, nonfinal chunks full, no compression/trailing data. The signed part binds the original request/index; the encrypted manifest commits its signed reference, avoiding a reference cycle. All original age format/recipient, final authentication, immutable encryption retry and source-signature requirements remain in force. Repacking does not reset an independent deadline or key promise.

For snapshot selection, the plaintext is exactly configuration3’s five-member contacts/defaults/advertisements/conversations/scopes object and uses its full selected reconciliation. For scopes selection, scope-configuration-v0 has exactly four root members: contacts, advertisements, conversations and scopes, each using configuration3’s unchanged record grammar. Defaults is absent, not null or a placeholder; any defaults member fails before staging. The assembled scopes’ distinct roots must equal requested roots minus unavailable, and all conversation/contact/advertisement records must be necessary dependencies of those returned roots. Install no global-default value through this restricted request. Configuration/selection must match the request’s exact matrix; no trial parser or conversion between these two plaintext schemas is permitted. Neither mode installs a human root or per-message reply policy. Locally conflicting or blocked facts remain explicitly held; accepted negative facts cannot be cleared by omission, another source, a fresh transfer or false flags.

The target authenticates the response and every part under its original retained request and current unchanged source authority before decryption/staging. Require complete manifest, exact part references/indices/count/length, final authentication, total digest, strict full configuration and matching selection/coverage. No accepted live prefix, oversized partial success or guessed missing record. Parts may arrive out of order and remain bounded encrypted/private staging until complete; a receipt never acknowledges a partial subset as staged.

Commit the complete private staged configuration, original request/response/part provenance and immutable staged receipt before retiring the transfer-only age secret. Then apply configuration3's current per-record conflict/authority/dependency reconciliation and atomically retain each resulting fact/hold with its provenance. Source/target revocation, changed local generations or cancellation still stop new effects.

Installed requires successful reconciliation of every returned selected contact and conversation record, and any defaults carried by the selected configuration, under their existing rules.

Every returned selected scope fact must also complete reconciliation; a scope may complete with explicit blocked constraints as defined above. An authenticated source unavailable-root result remains a disclosure outcome, not evidence that the requested root is usable.

A still-held contact, conversation or default record, missing validation dependency, malformed or unsupported data, or unreconciled returned fact prevents installed.

Unavailable current routes, live peers or required native group admission remain separate per-destination work and do not by themselves make reconciled metadata incomplete. The receipt does not establish that another source has no newer facts or that a destination is send-ready. A target may continue another independently authorized source request for still-missing facts without undoing accepted safety state.

:::

::: {.details summary="Confidential carriage, retries, cancellation and future sending"}

Use sealed-control-v2 kinds own-setup-request, own-setup-response, own-setup-part and own-setup-receipt, each carrying exactly its original signed wrapper. They are additional explicitly selected kinds of the same unpublished asynchronous binding, not a widening of sealed0/1 or a new application operation. Requests/receipts are signed by the target under current send authority; responses/parts by the source under current enroll authority. The outer signed intent actor matches that exact body signer and its frozen endpoint. Independently validate same-account pinned identity, current owning roles and transport authorization; a generic sealed decoder cannot grant those roles.

For requests and receipts, select the source's eligible original assertion10/control key. For responses and parts, select the target's exact request advertisement/key. Match outer recipient, key owner and inner endpoint before encryption as well as receipt. Enforce the existing sealed body/plaintext/identity bounds, exact native HPKE construction, original intent and body signatures, per-key publication/receiving promise and privacy-route rules. A newer source/target assertion cannot silently change a retained encrypted preparation. No clear copies of contact/scope/proof data or personal-address-bearing setup are attached alongside the sealed body.

Existing generic sealed-control mail or an independently authorized opaque relay carries each immutable container under its actual operation permissions. No provider-control/bootstrap credential, pairing token, shared namespace or original QR scan grants this transport. Delivery to a selected own mailbox still requires actual recipient-key/endpoint binding. An upgraded client handles validated records as control traffic; older clients may show the generic notice. No legacy discard instruction, new clear header, subject matching, application-message deduplication or human-read trigger is introduced.

Request identity is own principal/target device/transfer, across all possible sources. The original source/selection/recipient/nonce is immutable. Changed authenticated request variants hold that transfer; unauthenticated input cannot poison it. Each source publishes one frozen response/part sequence; receipts staged/installed have separate exact identities. Retries return retained original records/ciphertext, preserve package/key/transport uncertainty and never select a latest-time winner. Response/part/receipt processing does not generate another request. Only the original locally authorized setup job may schedule bounded continuation, retaining source-specific unavailable results, prior uncertainty and current policy.

Cancellation is local at either endpoint; this binding defines no remote cancellation message. Stop future processing/release under the cancelled local generation, preserve safety/provenance and possible disclosure, and retire the target's transfer-only secret under its owning schedule. Original expiry stops unfinished new effects and further automatic attempts under that transfer. Neither action recalls already disclosed setup or guarantees another endpoint has stopped. The ordinary receiving control key keeps its independent published custody promise; cancelling one transfer does not destroy it. No timer restores a live secret, clears a conflict or recreates a trusted transfer from an archive.

Receiving setup does not grant native membership or authority to replay pending human content. Resolve current personal-address/account associations, actual assertion10/package allocations, required routes and admission through the [per-delivery handoff](first-contact-setup.md#acquisition-for-independently-ready-deliveries). Fresh composition can use accepted scope metadata without old correspondence. A missing reply/quotation/action target remains independently pending. Each later delivery still needs its own original disclosure authority and current final release checks; metadata cannot reconstruct an absent outbox or source message.

Required acceptance includes a newly learned scope after pairing, another eligible administrator when the original source is offline, missing human root with valid metadata, restricted-root coverage and no default mutation, wrong-account/source/role/key, fork/revocation during staging, conflicting observations across sources, invalid final part with no installed prefix, exact retries and lost receipts, expiry/cancellation/secret retirement, private-pair leakage, unsolicited response and no automatic-response loops. Cryptographic byte/schema or in-memory merge checks are component evidence; complete current identity/carriage/staging/native-ready interoperability remains independently unproven.

:::
