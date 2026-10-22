---
title: Implementation claims and acceptance
order: 15.5
blurb: supported profiles · dependencies · reproducible results
sectionNav: true
---

# Implementation claims and acceptance

An implementation supports the Email/2 base and named modules in particular roles, under the exact wire encodings those contracts select. It does not become universally compatible by recognizing one attachment, displaying a button or passing a parser test. A support claim identifies the implemented profile revision, its dependencies and the behavior that has actually been checked. Own-account provider/relay/bootstrap roles additionally exercise the [shared native binding](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions): every claimed requested subset, three-scope response reordering, extra/missing/duplicate or cross-module scopes, shared-callback one-time attempt isolation, credential isolation and changed-metadata holds. Require independently advertised public-client authentication at both token and revocation endpoints: omission, Basic-only support or a malformed list at either endpoint makes the profile unavailable, even when the other endpoint supports `none`. Pure metadata/registration tests do not establish browser/token/family integration. Shared account-link claims additionally test the [module/account/descriptor subset](provider-grants.md#shared-account-links-separate-module-authority), same-origin cross-module proof attempts, relay contact labels versus mailbox-domain delegation, module-local reset/deletion and no cross-module state effects. Signature-only validation cannot prove account membership or atomic challenge consumption. Conversation reconstruction additionally exercises the [complete primary-reply procedure](reply-content.md#assemble-the-conversation-from-contributions): all four primary message kinds, exact target eligibility, late parents, every cycle member with noncyclic incoming replies, namespace conflicts and stale/incomplete projection holds. Topology-only results cannot prove carrier authentication or atomic source-snapshot installation.

> [!ex] A provider carries protected mail
> A provider can preserve a protected message through submission and retrieval without implementing its encryption. Its report demonstrates carriage. It cannot advertise that every device using the mailbox can decrypt that message.

This chapter defines proposed claim and evidence rules. There is no certification program or completed whole-protocol conformance suite. The [validation record](validation.md) describes current local evidence; the [adoption plan](adoption.md) describes participation and tooling.

## Reading requirements

Uppercase MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL use the meanings in [BCP 14 (RFC2119 and RFC8174)](audits/requirement-language.md). Lowercase words retain their ordinary meaning. Requirements can also be stated directly without uppercase keywords.

These are requirements of the proposed profile, not evidence that it has been adopted by a standards body. An optional capability may be omitted, but its specified fallback and rejection rules still apply. A SHOULD exception requires understanding its consequences; it cannot override an independent MUST.

## State the role and scope

A claim must identify the implementation and version, the exact profile revision, the acting role and the tested configuration. A client, renderer, submitting service, retrieving service and discovery service have different obligations. One product can perform several roles, but evidence for one does not establish another.

| Claim | Necessary boundary |
| --- | --- |
| Conversation reconstruction | Original content remains available; uncertain attribution stays visible; no distinct response disappears |
| Structured contributions | Supported operations, exact references, authentication prerequisites, replay handling and readable alternatives |
| Presentation | Complete selected vocabulary, rejection behavior, resource isolation and accessibility requirements |
| Protected conversation | Identity and device authority, protocol processing, durable lifecycle, policy and disclosure behavior, including [setup-secret retirement](setup-secret-retirement.md) and accurate memory/storage erasure claims |
| Provider carriage | Actual submission/storage/retrieval paths and any transformations of protected bytes |
| Provider control | Exact configured service contract, authorization, expiry, retries and resource limits; optional [public discovery](provider-discovery.md) requires its exact domain/issuer/registration and durable publication rules, the separate [public grant profile](provider-grants.md) requires account/device linking, exact pair approval, role issuance and serialized revocation, and [Auto setup](bootstrap.md) requires independently authorized source accounts, exact exchange/device proofs and their bounded replay limits, recipient opt-in, bounded disclosure and full first-message acceptance; component tests do not establish implemented integration |
| Service interaction | Accepted question and chosen option, independently trusted destination, account authorization, durable request identity and authenticated outcome |
| Own-device enrollment | Independent confirmation of the new device, current enrollment authority, exact permissions, replay prevention and atomic acceptance |
| Archive and collection reader | Independent recovery kit, complete file authentication, writer signatures, exact inventories, atomic history-only acceptance and honest completeness/freshness outcomes under [archives](encrypted-archives.md) and [collections](archive-sets.md) |
| History transfer | Accepted endpoint authority, exact source disclosure decision, recipient-specific files, request/grant/cancel correlation, historical import and terminal result under [history transfer](history-transfer.md) |
| Group ordering | Selected ordering policy, authorized membership change, sufficient decision evidence, atomic installation and behavior when progress is impossible |

A limitation must not contradict a mandatory requirement while retaining a claim for the affected module. A provider or client may omit optional modules and report its supported module list. The [module framework](modules.md) distinguishes omitted modules from incomplete implementation of a claimed module; none requires a separate edition of Email/2.

## Protected conversation agreement

A new Encryption implementation claim requires [mail-conversation-v2 and its protected core](suite-profile.md#current-client-baseline), including its exact signed application/ordering agreement and both required rendering profiles. The separately claimed complete conversation bundle additionally implements Answers, Reactions and Corrections. Encryption alone requires safe reading of their known contributions, not those interaction controls. Service actions and Hosted replies are separately declared. Base clients and providers need not implement that entire bundle. Clients SHOULD implement the [compatible-client transition](suite-profile.md#joining-with-a-simpler-client). A claim for that behavior requires preserved protection and intended audience, authorized readable composition, immutable retries and the owning admission/migration outcomes. Fewer optional interactions alone do not require a new stream under the current fixed readable application; an actual cohort change, a new sending stream or an earlier-agreement transition still needs its exact admission. A fixed application or candidate parser alone is insufficient. Existing component results do not establish joined module support. [Design resolutions](design-resolution.md) distinguishes remaining protocol work from implementation and external evidence.

An implementation supporting only an older agreement reports that exact compatibility scope. Passing older assertions, contexts or native experiments cannot be relabeled as the current Encryption baseline. Validate current authored0/envelope6/context10/assertion10, fixed readable vocabulary, both rendering profiles, immutable controls/admission, slot reply-intent1, state1 lifecycle and every claimed interaction together before advertisement. Earlier conversation decoding remains separately scoped; its fields and signatures are not rewritten to make it current.

## Private reply presentation

A current Encryption client must test all three [declared intents](client-behavior.md#declared-reply-intent), including no-replies suppressing both private and group composition while separately authorized actions retain their own behavior. The earlier envelope4 agreement has no reply-contract field and does not satisfy the current claim; older profile or topology checks do not prove support. The [exact record and destination acceptance cases](reply-intent.md#acceptance-boundaries) apply through the current slot intent1/logical-reference binding, including copied readers, current account/source changes, operation applicability and preserved original bytes.

Exercise private replies from an apparent group discussion with at least three people. Whether the interface opens a separate conversation or a private branch, verify that the composer and every private continuation identify the actual audience. Arrival of a group message, draft restoration and navigation must not retarget the private draft. A recipient outside that audience must receive neither the private contribution nor a synthetic activity placeholder. An interface that labels a mixed timeline “Private” without separating its composer and continuation does not establish this behavior.

Exercise the existing same-conversation reply constraint separately: a new private conversation cannot reuse the group's primary EventReference as its own ordinary reply parent. Keep a local source connection separate from transmitted content, and test that unauthorized group context, recipient lists, resources and controls are not automatically copied. A topology test alone cannot prove audience isolation, delivery behavior or the client interface. Multiple legacy To/Cc addresses must not activate an inferred protected group or a claim of enforced Reply all suppression.

A current [mailbox-setup-v2](mailbox-setup.md#set-up-an-asynchronous-delivery) claim additionally exercises the exact required agreement, original assertion10 commitments and independent signatures, separate attempt/ordinary-creator keys, complete-body/exact-domain DKIM and trusted actual-envelope evidence, sealed2 response binding, complete actual selected-device evidence and full crash-safe handoff. Old-version or different-agreement responses must not complete an attempt or authorize a rewritten human message. Exercise actual outgoing request/response MIME, no-loop policy, multiple devices, package allocation, cancellation, strict verification, uncertain delivery and final content-release checks. Signed-record/native-package candidates do not establish these mailbox or durable-state outcomes.

A current public provider claim additionally exercises exact descriptor2 transport/retained-generation acceptance, immutable grant2/configuration2 and separate role issuance, control2 original signed agreement/target state, and current account/family/device revocation at queue mutation. A bootstrap2 claim exercises original source and target descriptor commitments, all seven kind-specific signed records, source inspection, recipient opt-in, uniform pending disclosure, fresh response versus publication allocation and current route activation. Protocol changes must not clear account blocks, reset budgets/replay identities, duplicate one package allocation or permit old-version results to finish a new attempt. Exercise actual first-message handoff with every actual selected device’s assertion10; wire/signature/correlation candidates cannot establish these source/service/admission outcomes.

Hosted holder replies additionally exercise [durable intent without a persistent browser bearer](hosted-access.md#a-pending-hosted-reply-survives-a-restart): saved exact operation/request before POST, visible pending/unknown result, restart awaiting the original matching credential, deliberate resume and original-ID status/retry. A server receipt confirms storage, not conversation delivery. Lost local state or denied status cannot prove non-commit or create a replacement action. Test management lookup/reply/export authorization at its serialized read snapshot, including actual connection/lock waits through expiry; fixture scope changes are not proof of deployed account revocation.

A [configuration3 own-device claim](paired-configuration.md#transfer-asynchronous-scope-metadata) additionally exercises mixed old/reply-aware conversation selections, exact agreement/context/genesis/assertion row, no private-pair expansion and original byte commitments. Exercise the target-selected version3 request, source/target authority, all signed encrypted parts, whole manifest, staged-before-live-install transaction, conflict-preserving per-record reconciliation and current actual admission. Unknown/malformed metadata cannot be installed by a partial parser; a later policy/admission wait affects only its validly staged selection. Receipt installed remains distinct from ready, and no history/credentials/old checkpoints/actions are imported. Chunk and ordinary-context syntax cases alone cannot prove that full journey.

## Dependencies are part of the claim

A profile's mandatory dependencies must be implemented in the role where they apply. Passing schema validation does not establish authenticated authorship; decrypting a packet does not establish current authority to perform an action. An account capability cannot substitute for a receiving device's capability.

Unknown or unsupported profile revisions must follow the owning contract's fallback or rejection rules. They must not be interpreted as the nearest familiar version. A failed check cannot authorize weaker protection unless the sender's independently established policy allows that outcome.

Experimental identifiers and private-use formats remain experimental even when two implementations agree on them. Registration, standardization and implementation support are separate facts.

### Character-data and parser dependencies

Record the data versions actually used by each decision, not only the library’s package version. Domain validation can depend on separate normalization, case-folding, character-property and IDNA tables. Those providers must agree with the selected profile. A newer table combined with an older host-runtime normalizer is not evidence of support for the newer Unicode version.

A declared version is necessary but insufficient. Check the selected normalization corpus, applicable property defaults and ranges, contextual rules and derived classifications against the pinned sources. Report any differences and their disposition before enabling that profile. A provider mismatch holds the affected validation; it must not silently select another version, rewrite the address or accept an unchecked encoded label.

The same principle applies to HTML/CSS parsing and cryptographic adapters: identify the parser or library, its configuration and the rules supplied by the application. A library’s supported feature set does not prove that the application selected or enforced those rules. Test the integrated boundary as well as the underlying component.

### Key expiry and renewal policy

A protected-conversation report records the configured [maximum setup-key lifetime](security-profile.md#experimental-admission-lifetime), issuance defaults and any additional library limits. Seven days is a configurable default, not evidence that automatic renewal works. Test a shorter interval and a longer configured interval; the same signed package must still fail for new creation after its original publication expiry. Separately exercise already-prepared receipt under the current original receiving-window/custody contract, including acceptance after publication expiry but before that receiving deadline and rejection after the receiving deadline. Retained older agreements keep their own receipt-time expiry rule. Include uncertain time, malformed local policy, revocation before expiry, consumed-package retry, restart, and a publication or invitation attempting to outlive its underlying authority.

A complete automatic-renewal claim also requires fresh replacement keys and references, authenticated publication, unchanged-contact continuity, an interrupted renewal with preserved drafts, and retirement of unused expired secrets. Historical reading must remain available without reactivating consumed transport keys. Component lifetime checks do not establish these joined outcomes or a universal rotation schedule.

## Report observable outcomes

Each acceptance case identifies its governing requirement, input, setup and expected observable result. Reports retain the implementation versions, profile revision, relevant configuration, source/fixture digests and whether execution used one implementation or independent peers. Secrets and live credentials do not belong in reports.

| Outcome | Meaning |
| --- | --- |
| Pass | The stated check ran and its expected result was observed |
| Fail | The check ran and contradicted its expected result, or failed to execute successfully |
| Unsupported | The implementation explicitly does not implement the named capability |
| Not tested | The check did not establish an outcome, including missing adapters and skipped tests |

Unsupported and not-tested cases never count as passes. A complete report has no unpassed mandatory cases for its stated scope. Even a complete report proves only that case set: it does not establish omitted requirements, independent interoperability or security review.

### Keep separately authorized steps visible

A joined test must exercise the actual transitions between components. For a service button, receiving an authenticated question, linking a service account, authorizing an option and retaining a service receipt are separate checks. A preconfigured token-to-principal mapping cannot demonstrate account linking. A receipt for a service effect cannot demonstrate that a conversation reply was delivered.

For a new device, enrollment, confidential security-configuration staging, live trust reconciliation, mailbox connection, publication of supported profiles and admission to a conversation are separate transitions. The [current configuration transfer and readiness contract](paired-configuration.md) requires exact current configuration3 and own-setup0 source/target support for the claimed role; earlier configuration1/2 remain exact compatibility claims. It requires complete multipart staging atomically committed with its immutable staged receipt before any live installation, per-record contact/conversation reconciliation and actual current acquisition/admission before a send-ready claim. Installed configuration alone is insufficient. Version0 contacts/defaults evidence cannot supply version1/2 conversation selection, and configuration1 cannot carry reply-aware context9 by relabeling it. Test conflicting existing pins, newer revocations, withdrawn verification, original evidence expiry, a locally stronger policy, a cancelled or expired request and a crash before activation; a staged plaintext file cannot count as those outcomes. A paired device does not acquire old message keys merely because its enrollment succeeded. Exercise [administrative loss](identity-lifecycle.md#when-administrative-devices-are-unavailable) with a surviving send/receive-only device: it cannot enroll or promote itself, temporary approval loss remains pending, and an explicit new identity does not retire the old one. Test [composition after historical restore](encrypted-archives.md#replying-after-restoration), including unvalidated parents, foreign authors and old service/outbox actions; new account readiness alone cannot activate them. For a membership change, a valid ordering decision does not by itself prove that the application installed it without losing newer message-processing state. Test the shared durable state at that boundary, including a crash or intervening message.

Manual evidence must identify the method and observed result. An accessibility-tree snapshot is not a screen-reader test; a MIME inspection is not an ordinary client's rendered display. Record these distinctions rather than treating automation as a substitute for the intended observation.

## Exercise failures and mixed deployments

Acceptance must include invalid input, missing dependencies, duplicate and reordered delivery, restart and failed persistence wherever the profile can change durable state. A failure case checks both the visible outcome and the absence of prohibited effects. An error message alone does not prove that a package was not consumed, a recipient was not added or an external action was not submitted.

Mixed-client cases retain ordinary replies and readable alternatives. Mixed-protection cases check the disclosed exposure and the sender's selected policy. Independent client/server runs identify the actual topology; a local SMTP loopback remains a local experiment.

The [whole-client acceptance inventory](acceptance-inventory.md) allocates current requirements to roles, contract families, module combinations and interruption cases. Its clause-level traceability rules apply alongside the [interoperability scenarios](interoperability.md#proposed-acceptance-scenarios) and each owning profile’s acceptance requirements. This chapter does not replace their schemas or algorithms.

## Service actions in the current agreement

A Service actions claim requires the [current protected service binding](service-answers.md#current-protected-service-agreement), not only successful account login or a historical service-question parser. Exercise each device's signed per-ordering `service-actions` declaration, the fixed readable application, exact authored0/envelope6/mime-suite-v2/descriptor binding, personal-address and source/relay confidentiality, native action-account authorization, safe ordinary reply/quote/reaction, independent copy allocation and immutable uncertain submission/status behavior. Omitted support leaves the operation unavailable without converting it into an ordinary answer. Receiving/opening produces no endpoint request or automatic sign-in. Endpoint bearer/access/runtime limits remain separate from message encryption.

## Required encrypted personal addresses

Encryption receiving support includes the [personal-address contract](private-address-presentation.md): authored0 presentation, envelope6 actual audience/slot binding and assurance/display behavior under the one required suite agreement. Address metadata alone does not authorize routes or independently verify mailbox ownership. A full transport-address privacy claim additionally requires the [relay lifecycle and transport projection](private-routing.md), the [source/route/proof contract](relay-routes.md), actual provider/SMTP/mailbox integration and all required control-carrier protection; configured encrypted-carriage evidence does not establish that lifecycle or opaque SMTP delivery.

## Delayed initial admission

Current-suite Encryption receiving support includes assertion10 `keyPackageReceiveUntil`, initial invitation10 `receiveUntil`, immutable local package custody, explicit late-admission validation and retirement. Exercise normal and delayed acceptance, expired outbound rejection, shorter local policy, substituted references, source-proposed deadline extension, uncertain clocks, current role/identity conflict, missing/withdrawn keys, actual expired-leaf validation, exact consumed replay and restart around custody/admission/retirement. Include an assertion whose publication expiry is later than its package expiry. Check the package receiving deadline against the actual signed package expiry, not against the assertion expiry. Before the package expires, a complete otherwise eligible admission can proceed; afterward, an unexpired assertion does not permit a new Add. A structural parser without native package validation must not invent a relationship between those two expiry fields. A retained key or successful primitive Welcome join alone does not establish complete admission or platform erasure.


## Ordinary stream and managed-mode separation

Encryption receiving support includes the exact [ordinary-stream agreement](suite-profile.md#ordinary-protected-conversations), not only managed quorum support. Exercise independent owner laptop/phone/peer streams, offline first submission from an enrolled phone, complete signed source/update/admission records, current role renewal and revocation, actual recipient Update recovery, simultaneous compatible Updates, conflicting requests for one leaf, removal of an updated leaf with a retained disposition, one-use package/Update custody, source equivocation, missing/pruned ancestry and crash/restart at each atomic boundary. A different member, including another device of the owner principal, cannot author application data or take over that stream.

Check the current fixed readable application, per-ordering interaction lists and no cross-mode capability combination; ordinary-mode simpler late clients; retain exact module-closure checks only for earlier v1/v0 compatibility; same-event duplicate/conflicting carriers in the global reply graph; changed-audience/private-copy isolation; managed-to-ordinary relabeling attempts; and any personal address in an exposed control proof. Required masking must hold when the selected control carrier does not protect it. Current configured source/mail experiments supply partial historical-format evidence, not complete current-suite receiving support or independent security assurance.


## Sealed control and address privacy

Exercise the [sealed-control container](suite-profile.md#confidential-setup-and-control) with actual HPKE, accepted intent signatures and unchanged original body bytes. Include wrong target/key/account, original-body substitution, malformed/truncated/trailing binary, invalid encapsulation, known source/recipient revocation, unknown identity, mixed kind/mode, immutable key promises, late receiving versus expired creation, deadline consumption during work, exact replay/conflicts and restart around custody/owning effects. Inspect outer mail and relay bytes for personal addresses and proof copies. A configured opaque attachment or primitive round trip is not full current-suite privacy acceptance.


## Unread and offline availability

The [offline delivery contract](suite-profile.md#unread-mail-and-long-offline-periods) is part of Encryption client behavior. Check that authenticated background processing does not mark mail read or emit a receipt; retained unread correspondence survives setup/transport-key expiry; actual undecoded mail respects each independent deadline; restart and uncertainty cannot reopen retired keys; and protected archives/history transfers preserve provenance without live effects. Exercise a backup made before the unavailable message and a source that no longer has the content: neither can report successful recovery. A source or target revocation blocks new historical release under the transfer contract. New setup protects new traffic without being reported as recovery of the old ciphertext. Platform execution limits and all-devices-offline availability limits must remain visible in the implementation claim.


## Identity continuity by purpose

Exercise the [purpose-specific state-anchor contract](provider-grants.md#continuity-and-freshness-have-different-scopes), rather than requiring all signed evidence to name one current head. Keep an original assertion10 and bootstrap2 offline publication usable after an accepted unrelated state advance with the exact unchanged binding; retain their bytes, allocation, deadlines and current accepted head separately. Reject an anchor preceding that device's enrollment, missing accepted ancestry, authorized forks, changed keys/bindings and known revocation. Recompute current-head recent-checkpoint age; reject an old target-head live response and preserve the old attempt's age on source continuity. For delayed sealed controls, test actual signature/decryption through continuous same-key/role renewal while the original publication is expired; reject role/interval gaps and keep all original receiving bounds. The same renewal must not preserve a changed-binding provider/history grant. Earlier exact-head encodings and fixed QR/MLS predecessor contracts remain unchanged. Joined final release and installation must recheck these decisions under their own serialized boundary.


## Complete identity administration

Current Encryption claims require the full [state1 lifecycle](identity-state.md#concurrent-administration-and-retirement), not merely a repair-candidate result. Test strict bundle/state/share versions and original/canonical bytes; genesis/upgrades/ordinary updates; deterministic parent order and complete known frontier; all shared-authorizer and derived-binding proofs; revocation preservation, role/interval/key conflicts and no ancestor override; revocation-only cleanup; explicit retirement and no successor; stale/hidden branches, replay/collisions, crash/concurrent installation and invalid-proof non-poisoning. Exercise actual proof carriage with selected confidentiality/masking and no response loops. After repair, test fresh setup, pairing, provider links/grants, routes, freshness and MLS release without single-parent authority shortcuts or automatic historical access. State0-only stores and the first-repair derivation component do not pass this joined lifecycle. Independent interoperability/security evidence remains unproven.


## Concurrent renewal and publication

Exercise the [renewal/publication contract](security-profile.md#publish-replacements-without-disturbing-in-flight-mail): independent actual native package references under one current device key; immutable original custody/promises; one independent allocation realm per package; local rollback/reopen and separate connections; uncertain upload idempotence; no cross-provider reassignment or passive-copy exclusivity claim; overlapping publications without a latest-record overwrite; consumed/withdrawn snapshot replay; original receiving bounds and uncertain DATA release; explicit binding replacement versus provider-only deletion; known compromise and unavailable/expired administration. Failed renewal holds without plaintext, a new human event, an extended deadline or automatic unbounded retries. Component staging is not publication or complete renewal conformance.

## Hosted replies in the current agreement

A Hosted replies claim requires the [complete protected observation binding](hosted-access.md#protected-observations-of-hosted-replies). Exercise the observer device’s signed per-ordering `hosted-replies` declaration, authored0/envelope6/mime-suite-v2 and exact roles, explicit observer-versus-holder attribution, exact accepted target/audience, current owner-bound exports and immutable concurrent/restart deduplication, account changes, expired grants versus sending authority, held release, private-copy confidentiality and missing/conflicted targets. Holder words never become participant-authored answers or verified identities. Receiving/rendering creates no hosting request. Legacy observer mechanics and negotiation tests do not establish complete current integration; operating a hosting service is a distinct claim.

## Confidential historical transfer

Long-offline recovery with no usable original setup keys uses the [opaque-delivery request selection](history-transfer.md#recover-an-unopened-delivery). Verify exact decoded-binary descriptors, current independently known source/target, source-owned original recipient/content mapping, all-requested selection, constrained export and historical provenance. A copied ciphertext, outer From/relay alias, fresh same-mailbox identity, missing mapping or fresh handshake must not authorize old content or install live state. Include no-source/no-content outcomes and eventual original arrival after import.

A current history-transfer claim implements the [five exact sealed history-control bindings and ciphertext-file carrier](history-transfer.md#carriage-and-file-retrieval), not the older clear JSON mail attachment. Check original/outer actor and intended recipient before encryption, original signature and immutable request/grant parents after opening, purpose/role/cancellation direction, current authority and bounded deadlines, duplicate capsules versus original transfer identity, and missing/retired return control keys. Inspect actual mail/relay bytes for participant, account-scope, archive verifier and reference leakage. File receipt accepts only exact independently admitted catalog/part ciphertext descriptors, never names/headers as authority. Actual serialized source handoff, atomic import/result journals, route/account changes, crash/uncertainty and incomplete history need separate evidence; a candidate-only HPKE roundtrip does not establish them.

### Account-reset response loss

For every module inheriting account linking, exercise a lost completion response followed by fresh native authorization, current-account inspection and inspection of the original reset preparation. Check each retained outcome, completion racing an inspection, subsequent resets, expired original families, response loss and restart, and garbage-collected records. A missing result must preserve uncertainty; it cannot trigger another reset. Reassignment must prevent the new owner from reading the earlier owner’s preparations. Parser-only fixtures do not establish transaction, authentication or owner-isolation behavior.

### First-message setup over existing mail

Implement [mailbox-setup-v2](mailbox-setup.md#set-up-an-asynchronous-delivery) as the current separately declared carrier, not as an automatic reply to passive discovery. Exercise its complete no-provider, no-prior-association first-encrypted-message journey and negative/restart matrix. Signature/HPKE components alone cannot establish trusted envelope/DKIM coverage, disclosure admission, durable response reservation, bounded transport retry, package consumption or final human-content release. Include multiple recipient devices, unsupported legacy display and required address-masking holds.

### Setup-to-outbox handoff

Apply the [common handoff matrix](first-contact-setup.md#finish-setup-for-one-intended-send) to both setup carriers. Test request-only versus ordinary receiving assertions; creator self-membership versus same-principal joiners; exact application reselection; edit/account/audience/reply/policy changes; concurrent completion/cancellation; and process exit before/after local crypto acceptance, retirement intent, retirement completion and outbox activation. Restart must recover all-or-none checkpoint/prepared bytes, the original planned copy/contribution/delivery mapping and each copy’s exact held or release-eligible state. Include visible/private copies with independent outcomes and a plan requiring collective activation; one copy cannot activate another or expose their private correlation. Actual key deletion and MLS/SMTP behavior need evidence at those boundaries; a local journal test cannot establish them.

### Frozen copy progression and exposure

Exercise [delivery-policy progression](delivery-policy.md#a-waiting-delivery-is-different-from-missing-setup) with a complete admitted audience and partial SMTP outcomes versus an audience whose selected setup is missing. An incomplete audience must not silently shrink. Test independent/coordinated activation, missing planned rows, changed cohorts, known or uncertain host-content exposure before failed notification, including missing creation receipts, uncertain plus accepted attempts, later correlated failure and preserved per-copy state. Verify original disclosure bytes before any release; a later new mode/service/audience cannot rewrite an existing event or reconcile unknown delivery by exposing another copy. Include both a preauthorized setup-timeout fallback and an encryption-required hold, without treating timeout as authenticated incompatibility or new permission. Status derivation alone does not establish authorization, durability, crypto or actual transport behavior.

### Offline answers, reactions and service buttons

Exercise the [shared interaction queue and status contract](client-behavior.md#a-pressed-button-keeps-its-sending-status) for conversation answers, reactions/withdrawals and HTTPS service actions when their modules are selected. Check immediate selected-state feedback; local persistence failure; offline activation and restart; reconnect without another press; repeated activation while pending; partial mail delivery; lost POST response after an applied effect; matching pending/confirmed/rejected receipts; incompatible terminal results; cancellation before and after possible submission; and expiry during an offline wait. Changed account, authority or destination must hold original work rather than retarget it. A service POST retry retains its original identity and exact bytes and causes no second effect. Verify accessible progress/failure cues beside the control, pending state separate from accepted reaction counts, and no read/remote-acceptance claim from transport submission. Existing component queue/idempotency tests do not establish this complete offline interface and durable lifecycle.

### Changes while waiting to release content

Check the [final body-release decision](transport.md#the-final-body-release-decision) independently of the preliminary worker claim. Install revocation, policy/cancellation or mailbox-association changes on another connection while SMTP waits for 354, then verify no body bytes leave. Advance credible time past an original assertion/key/grant deadline during that wait; retained queue time cannot authorize release. Check successful unchanged delivery, exact bytes and recipient scope, durable final-authorization evidence, process exit around the decision, uncertain final reply and original-payload retries. Cover each supported DATA/BDAT/BURL/API release path under its own framing; HTTP service/host tests also require remote execution-time checks. Local ordering does not prove global revocation, real-provider behavior or remote recall.

### Current pairing with multiple administrators

Apply the [exact current pairing binding and acceptance matrix](identity-lifecycle.md#current-pairing-and-multiple-administrators). Verify bundle1/state1 enrollment under unchanged original pairing record commitments, one authorized admin without a primary designation, exact single-device delta, local predecessor races and distributed sibling conflict/repair. Lost-result recovery returns original committed bytes but cannot reinstall superseded authority, allocate another enrollment, bypass target cancellation or activate configuration/history/actions. Separate proof-valid candidate evidence from complete durable state1 acceptance and independent QR/camera transport verification.

### Revocation across ordinary and managed conversations

Exercise the [device-versus-audience removal matrix](group-conversations.md#removal-and-delayed-mail). Accept a real signed revocation on one endpoint while another remains stale, and interrupt/restart the applicable transition. Known revoked receive authority holds new affected ordinary-source content even before a membership transition completes; validated proposal observations survive restart and prevent old-epoch application release. A remaining authorized same-principal device needs actual admission, not copied old state. Source-device removal cannot transfer stream ownership. A changed ordinary principal audience requires a fresh authorized stream, without implying a new visible grouping or removal from another owner's stream. Check managed certificate/administrator constraints separately. Preserve prior accepted/pending/uncertain history and prevent delayed target resolution from reviving a removed author's action. Inspect real cryptographic inability of the removed endpoint to decrypt post-removal traffic; local status alone does not prove a global cutoff or remote erasure.

### To, Cc and blind-copy distinctions

Check the [recipient-role contract](private-address-presentation.md#to-cc-and-bcc-remain-different): preserve authenticated To/Cc arrays and associated mailbox entries without relabeling Cc as To, distinguish reply-to-author from the selected visible reply audience, and keep Bcc only in the sender's private plan. Inspect separate protected copies for fresh identities, exact private pairs, no original visible recipient list and no other blind recipient leakage. A private reply cannot join the visible audience or manufacture a shared answer/reaction. Names from earlier messages, copied receipts or private delivery records cannot silently expand the draft audience. These presentation and disclosure requirements do not define a universal default Reply/Reply-all action.

### Unsupported records in restored history

Exercise [restoration outcomes](encrypted-archives.md#restored-does-not-always-mean-understood) with unknown envelope, operation kind and operation version, including a future field named manifest with different semantics. Retain exact signed-container/object bytes and inert archive-writer resource associations without invoking the current manifest parser or acquiring projection/actions. Known resource mismatches and invalid archive proofs must still reject. Distinguish complete byte coverage, omissions, unsupported rendering, historical provenance and independently accepted live target evidence. When composing from history without exact original-source validation, preserve deliberate disclosure as unattributed quotation/new writing, without a false matched source or automatic old reply/answer/action. Test imported pending jobs, revoked identity data and repeated import without live-state or external effects.

## Adding people and sharing context

Exercise adding a new principal separately from adding a device of an existing principal. Inspect the actual established-admission proof bundle: original roster, contiguous path and required supplemental assertions. Include a former member or witness whose identity/mailbox claim remains in those proofs. Verify that the add-person flow exposes the necessary metadata disclosure, that a denying policy holds release, and that uncertain prior delivery remains possibly disclosed. A policy-approved fresh conversation must have a fresh genesis, its actual audience and no fabricated old continuity. An ordinary stream cannot add a new principal to its fixed audience; a private-copy pair cannot become a group in place.

Change an Alice–Bob reply draft to include Carol while it contains Bob's quotation and an original file with nonvisible metadata. Preserve the author's new writing, but reevaluate included context and admission independently. Do not retain the old discussion edge, import the transcript, reactivate copied buttons or describe the original file as metadata-free. Exercise an explicitly authorized new root with inert visible quotation and correctly committed resource bytes, plus denial, missing source, changed proof bundle, restart and final-release policy change. A sender's signature on a quotation must not impersonate the quoted author. Component record validation alone does not establish the complete admission/composer/disclosure behavior.

## Exact history disclosure selection

Select one reply from a retained multi-message conversation containing originals, evidence, a quoted predecessor, files and private-recipient metadata. Verify that selection does not recursively include predecessors, unrelated originals, later traffic or all locally available resources. Missing required archive-entry dependencies must hold the proposal or be deliberately resolved under the exact disclosure scope; an unselected original may not be appended through a reverse association. Exercise an opaque record whose unfamiliar fields resemble active controls, and a narrower forward that is newly attributed rather than a modified original.

Reject changed object bytes, mismatched contribution references and supported resource digest/size errors at source preflight before any archive bytes reach the encryption/output adapter. Retain receiver-side rejection tests using independently constructed invalid signed archives; a stricter exporter must not make those negative fixtures impossible to exercise. Race an output adapter against mutations of the caller's source inventory and require the exact frozen bytes. These checks do not establish actual source approval, current identity authority, a full mailbox selector, rendering or final transport release.

## Identity claims across protocol upgrades

Exercise an unrelated claim after pinning, two valid conflicting successors of the accepted authority, and deliberate address replacement as three distinct outcomes. An unrelated claim cannot suspend the pin; an authorized fork holds affected work; replacement advances the association generation with a continuity break. Preserve historical attribution and verification provenance, and keep old queued drafts from targeting the new principal automatically.

Acquire current assertion10 and any additionally supported assertion8/9 observations under their exact selected acquisition bindings. Neither an agreement upgrade nor a different delivery channel resets first-contact, disabled state, identity conflict, verification scope, authenticated record collisions or package allocations. Include different valid signed payloads with the same principal/device/record across versions: hold that record while retaining the established association and identity, then require an independently valid fresh publication for operational selection. Do not claim this from an unsigned synthetic verified flag. Configured signature/package/store tests are narrower than actual mailbox/provider acquisition, state1 repair, final release or client presentation.

## Sender changes and draft storage

Switch an unsent private reply between two accounts with different principals, then between aliases of one principal. Preserve writing but independently reevaluate source audience/reply permission, actual From association, membership, comparison scope, routes, keys and per-sender protection policy. An outside principal cannot inherit the original discussion edge. A deliberately chosen new root may contain only independently authorized context; same-person account control is not protocol membership.

Observe account-triggered autosave and synchronization traffic. Changing From or allowing ordinary final delivery must not upload protected draft text, subject, source identifiers, attachments or old revisions to the new provider/devices. With no independently authorized encrypted synchronization profile, retain locally. Imported historical archives or transport group keys cannot substitute for that profile. Include storage failure, restart, missing sync keys and switching back to the original account.

Change protection/account while setup is pending, after staging/retirement, after activation but before release, and after a possible body handoff. Late callbacks cannot activate the new draft or restore a superseded revision. Preserve cleanup duties, exact prepared bytes and old uncertainty. A newly authorized ordinary or hosted send remains separate from retrying the original contribution. Exercise mixed-copy outcomes without treating one successful copy as full-send completion. Component destination and opaque journal checks do not prove these complete account/storage/release flows.

## Endpoint deployment and protection claims

Exercise ciphertext-only carriage, provider-side decrypting/signing endpoints, browser-local cryptography with operator-supplied code, ordinary readable bearer hosting, and a host reply later returned as a protected observation. Inspect actual key/plaintext/code authority and the displayed copy's acceptance state. A valid protected event can coexist with known service access; ordinary HTTPS or an opaque attachment alone cannot produce an Email/2 Encryption achievement. Unknown remote deployment must not become an affirmative operator-exclusion claim.

Keep correspondent verification and address masking independent. Inject sender HTML and signed feature advertisements that claim operator exclusion: neither may restyle client-owned protection state or supply a nonexistent attestation. Under a local policy requiring a specific operator's exclusion, missing or changed applicable evidence holds new release without probing, downgrading or switching peers. Preserve accepted historical cryptography and earlier possible/known disclosure after a later runtime change or link revocation. Source review, a capability fixture or a local decryption test alone does not prove deployed runtime integrity, remote operator exclusion or physical erasure.

## Restored operational state and rollback claims

Distinguish an ordinary restart from explicit restore, detected rollback, missing expected continuity evidence and unresolved device migration. Persist the recovery hold before restored cryptographic generation, voting, outgoing queue release, automatic responses or live incoming effects. Retain original bytes and historical reading; do not clear the hold by reopening/recreating the store, receiving a directory response or moving the clock forward. Exercise fresh independent enrollment/admission and the no-surviving-administrator new-identity outcome, with old uncertain actions still unresolved.

Snapshot the complete authority store before an actual signed revocation, accept the revocation, then restore the old store in isolation. Show that old signatures and internally consistent storage alone can again report the removed device as authorized. Compare separately retained authentic revocation to that view without claiming a universal latest-state oracle. Keep this limitation test distinct from ordinary old-record replay into the current store, which must retain the removal. For a stronger rollback claim, require evidence outside the restored state and test each claimed authority/ratchet/allocation/vote/action/outbox boundary. No general gate or managed-history test supplies that assurance.

## Rich-image failure scope and aggregate work

Place a heading and authored text beside an unavailable image, foreign-event CID, undeclared resource role, remote URL and data URL. Retain accepted rich text and image alternative text without fetching or passing a rejected source to a decoder. Keep image failure separate from invalid carrier/operation/index acceptance; text readability cannot repair those earlier failures or activate a copied control. Authoring must still reject nonconforming image sources.

Exceed a configured image count and require the projection's processing diagnostic before image resolution begins, without a partial rich tree. Then exhaust a small aggregate pixel allowance with real decoded content: the next image receives only the remaining budget, or stays alternative text without decoding when none remains. Include repeated placements and confirm that actual retained output cannot escape accounting through shared identifiers. Report local budgets and containment limitations rather than claiming whole-renderer, host-memory or current cryptographic conformance from a decoder test.

## Indexed replies and immutable older agreements

Place annotated reply HTML in an older raw-event, ordinary MIME or rich MIME agreement whose exact operation set lacks `reply-message`. It must not enable indexed sending, receiving acceptance or a source map. Recognizable HTML, a fresh feature flag or another device's new support cannot amend the authenticated context or old signed capability. Test the selected new agreement independently; a tuple grammar check is not native admission/carrier/index integration.

Preserve a blocked draft and its source/protection policy. Exercise separately admitted ordinary-stream and managed-conversation migration, including an older source lacking reply intent, an unavailable primary target and a valid explicit new rich root with inert quotation. No indexed version0 operation may become a root by omitting its required parent. Deliberate readable recomposition has a fresh contribution identity and independently authorized exposure; it must not silently strip a required no-replies/private-only policy or change the audience. Retain all original submitted/uncertain outcomes across migration and restart.

## Current baseline and explicit compatibility

For a new Encryption claim, require mail-conversation-v2 end to end: assertion10/context10/authored0/envelope6, fixed readable vocabulary, slot reply-intent1, both rendering profiles, state1 lifecycle, selected native admission and current control/carrier binding. An implementation that only understands assertion8/context8/envelope4 reports earlier compatibility; it cannot advertise the current module. A provider carrying ciphertext does not acquire this client obligation merely by claiming carriage.

Exercise fresh selection among current peers, a peer offering only earlier support, existing earlier contexts, optional earlier compatibility and an unsupported required reply policy. Never convert an old signature, mix versions, mutate the old context or remove required semantics automatically. Current setup claims use matching version2 mailbox/provider/bootstrap bindings, configuration3 and ongoing own-setup0 when that transfer is offered. Earlier records and results retain their actual versions and may remain readable/usable only through independently implemented compatibility. A successful older test is not a current-baseline pass.

## Offline operation distinctions

Disconnect during reply authoring/setup, pairing before and after commit, device-removal request/publication, service submission and hosted-holder reply. Restart at each boundary. Preserve exact operation/account/target and independently held versus ready work; a queued label requires durable local saving. Reconnect may retry only the original eligible work, never extend a lease/deadline, duplicate a completed effect or silently lower protection.

For removal requested offline, persist the local outgoing release hold before showing it saved. Race the choice against queued preparation and the final body-release gate; hold the full affected decrypting copy without silently dropping a member. Keep that hold distinct from a valid locally committed state1 revocation, pending group transitions and remote propagation. Missing role/time/proof waits without manufacturing authority. Cancellation before commit does not automatically clear the hold; after commit it cannot undo removal. Preserve uncertain prior disclosures and test unrelated-copy progress independently.

For pairing, an expired route cannot return an assumed negative enrollment result; a retained actual commit still needs current acceptance/readiness. For HTTPS, lost response is not a new button press. A restarted bearer page cannot resume from a credential hash or persisted secret token. Local storage failure, unknown status, revoked authority, changed account, offline administrator and missing original invitation each need their own truthful outcome. Component tests for these mechanisms do not prove the combined current client or the newly specified local device-release-hold integration.

Encryption-device removal must not be presented as revocation of every mailbox password, provider session, downloaded copy or bearer grant. Exercise actual service-bound identity checks separately from generic account-session revocation. A preexisting ordinary/hosted fallback permission cannot silently bypass a local device-specific release hold when that route may still expose content to the held device. Any deliberately broader new disclosure keeps its real access scope visible.


## First-device installation and first-contact selection

Interrupt first-device creation before and after private-key retention and authority installation. Resume the same attempt, including when the keystore and authority database cannot share a transaction. No partial installation may send or publish; a missing committed key must hold rather than regenerate under the old identifier. Race two local setup attempts and an enrollment/account change against installation. At most one still-authorized own-account selection activates. A known old identity, unavailable provider or offline administrator cannot be treated as permission for replacement. Confirm separate publication consent and distinguish identity installed from mailbox connected, correspondent verified and protected-send ready. A fully restored store follows its actual rollback limits, not a synthetic assurance from these tests.

For first contact, present two independently eligible principals before selection in each arrival order, both in one batch and in separate retained observations. Both policies must preserve ambiguity until separately authorized resolution; a cached candidate cannot bypass the final snapshot. Contrast that with a sole eligible unverified selection followed by a later unlinked claim: preserve the pin without claiming the first claim was verified. Exercise exact retries, changed generations, strict policy, missing identity dependencies and no usable candidate. The reference association store and signature tests cover narrower older-format components; they do not implement the current first-device keystore/authority installation procedure or the complete current assertion10 acquisition/client path.


## Discovery and comparison retain their original authority

Receive ordinary mail, nested forwards and a copied discovery part moved to the recognized outer position. Receiving alone performs no outgoing mail or HTTP request. A valid original signature cannot repair a mismatched outer From, expired assertion, unsupported address parser, absent identity dependency or changed binding. MIME refolding that preserves decoded bytes remains valid; altered signed bytes or purpose does not. Preserve the readable ordinary contribution without a later protected label. A separately authorized ordinary send includes no more than its one permitted advertisement.

Distinguish current assertion10 and retained assertion8/9 cached ancestry from an exact current live response. An unrelated device addition may leave the exact advertised binding usable; a replacement binding, repair, role loss, deadline failure or missing accepted path holds it. Earlier assertion encodings retain their exact-head behavior. Neither cached exception renews verification or grants a new package allocation.

Compare the exact original local-session object, then substitute purpose, principal, mailbox, state, version, account or session. No mismatch may partially install a pin, association or verification record. After a valid comparison is withdrawn or expires, replay its exact decision and confirm that new sends still fail their fresh verification check. Test anchor-only and authorized-descendant policies separately, including state1 update/prune paths and a repair boundary that must not be traversed. Existing human-comparison code follows state0 ordinary paths only; the full current state1 continuation and current assertion10 acquisition require separate implementation evidence.


## Account access, historical recovery and bearer forwarding

Exercise mailbox login without enrollment, valid enrollment without history permission, an archive restored after all devices are lost, and a surviving send/receive-only device with no usable administrator. Check each visible status against the actual authority: ordinary mailbox access is not endpoint enrollment; installed configuration is not imported correspondence; historical import is not live membership. No timer, subscription, password reset, kit or incoming record supplies missing administration. A temporarily unavailable qualifying administrator remains a pending operation. Any deliberate new identity retains old pins and pending-send provenance without claiming retirement or continuity of the abandoned principal.

Forward a bearer invitation between independently operated holder sessions. The same credential grants the same original access while valid, without proving either holder's identity. Neither opening nor preview initialization submits a reply. Confirm that a holder reply remains attributed to the grant holder, management rights are not conveyed, and committed revocation blocks later authorization from both copies. Previously retrieved content remains outside recall. A recognized invitation included in a forward must not be described as an inert preview; no automatic content fetch is needed for that disclosure explanation. Public hosting-account authorization and full browser/device integrations remain separate acceptance obligations from the configured store and page components.


## Reply permissions precede graph topology

Apply current source reply intent and the actual reply audience before adding a candidate primary edge. Compare missing source, known unsupported source agreement, forbidden reply, source conflict and eligible discussion. Keep accepted writing and the original requested parent in each case; do not turn a rejected edge into a root or destroy an otherwise valid content map. Private responses still use independently authorized roots/contexts rather than cross-context discussion edges.

Construct a would-be cycle with one forbidden or unresolved edge. Exclude that edge before finding cycles, so other individually permitted edges are not falsely marked cyclic. A permission result cannot replace exact reference, namespace, same-conversation or target-kind checks. Recompute against the same current accepted-source snapshot; a stale permission result cannot install a graph after policy/authority changes. Separately fail fresh rendering after a complete map and confirm that authored text/source labels survive, while failed required source parsing never produces a map. A trusted callback test proves graph ordering only, not authentication, reply-intent validation, atomic snapshot installation or current carrier support.


## Mailbox live confirmation without a provider service

Use an actual current mailbox-setup2 signed request/response with original assertion10 and sealed2 carriage, no provider setup service, and an independently retained live policy/send attempt. Validate the request/capsule/account/association and all current device evidence before checking freshness. Test exact original nonce/digest/agreement/actor, current target head rather than cached ancestor, original creation-age boundary and full clock interval. Receipt time, replay, cancellation, completed unrelated sends or changed local policy cannot create a fresh attempt. A second receiving device remains unavailable until its own eligible response exists.

An established context need not consume the response package merely to check freshness. Preserve its original admission/key state and independently recheck final release. Full mailbox authentication, key custody, durable attempt/cancellation, current state1 association, sealed2 and outbox integration require joined evidence. A signed-response/age helper is a candidate check only.


## Shared reset shape, distinct signed branches

Select the account-link/reset record profile from the authenticated module and accepted descriptor before decoding. Current queue descriptor2 requires grant2 and its account-link domain; retained queue descriptor1 requires grant1. Relay/setup retain their exact selected grant0 subset even with bootstrap descriptor2. A shared callback, same-origin endpoint, valid signature under another branch or copied OAuth scope cannot switch this selection. Test the signed descriptor digest and module/account/family/incarnation together, with unsupported branch held rather than a fallback parser.

The reset confirmation names the actual module and revoked permissions; it must not promise endpoint-identity revocation, destruction of old ciphertext or another module's reset. Race reset/disconnect with new link/credential/queue or route mutation at the owning serialization boundary. Preserve completed reset evidence and lost-result uncertainty across reconnect, but never install a historical resulting incarnation as current. A different account owner after reassignment cannot inspect the old owner's outcome. Configured grant/link proofs do not establish the public reset UI, current grant2 service, owner-generation store or cross-module revocation integration.


## Provider routing survives offline devices and interruptions

Connect the recipient’s normal inbox service once, then stop every recipient device process. Obtain eligible original published encryption setup and complete direct route1 issuance, live inspection and real protected delivery without an alias-approval request or signature. Repeat with automatic renewal to fresh aliases/keys while personal contacts and history remain stable. The service’s private admission/contact policy and blocks remain private; an invitation cannot contain a peer list.

Interrupt after source permission activation, after public request acceptance, after provider allocation and before the sender retains its result. Reopen actual stores and reconcile the original issuance handle/request/key/result rather than creating another alias. An authenticated duplicate returns its original receipt, invalid proof cannot poison the namespace, and changed authenticated bytes conflict across supported versions. Uniform pending admission is not readiness, and a signed issuance is not live activation.

Rotate the provider route key through a valid finite certificate under its unchanged stable service key, without a recipient-device signature or reset of eligible original authorizations. Reject wrong certificate keys/domains/origins, withdrawn/expired certificates, changed stable authority without reconnection, route limits outside original authority and attempts to restart a deadline through descriptor refresh. Existing accepted duplicates can retain prior success without new delivery; old uncertain retries cannot switch routes in place.

Race account/family/reset, recipient authorizing-binding revocation/repair, source withdrawal, blocks and local route/certificate withdrawal against allocation, disclosure, acceptance and release. Hold stale work and preserve uncertainty and actual remote effects. Missing recipient availability alone is no barrier when setup and service authority remain eligible; missing cryptographic/current evidence still is. The retained device-approved route0/bootstrap child experiment keeps its exact historical scope and does not prove this current route1 journey. Synthetic signature/shape cases do not replace the public OAuth, current-authority, network, mailbox or crash tests.


## A stored message must match the intended import

Exercise alreadyExists with the same Message-ID but a different valid authenticated contribution, a changed event/resource commitment, missing inaccessible raw bytes and a provider preview that appears to match. None completes the expected import. A receive-valid contribution with an unavailable required-to-store resource is likewise not complete storage. Exact independently retained opaque raw bytes can prove storage preservation without claiming that their unsupported application content was understood. Contrast exact permitted bytes and a protection-preserving transformation explicitly allowed by the selected profile; a generic repair or matching visible text supplies no such permission.

Retain expected local operation/account/copy and source provenance across lost results, generation changes and restart. A matched record completes only storage, never submission or recipient acceptance. Preserve the old submission identity/uncertainty and do not resend, delete the collision or install structured effects merely because import succeeded. Current address acceptance exercises assertion10/initial10/roster7/authored0/envelope6, while older fixture results remain at their declared versions. Full IMAP/JMAP network import, provider repair and cross-profile equality/transaction behavior require actual adapter evidence.


## Confidential repair recipients during a conflict

Create an independently pinned identity conflict with a healthy receiving administrator on every known branch. Exercise an original control-key publication retained through same-key, continuous receive-role renewals and confirm that only identity-admin proof circulation can select that key. Require every frontier path, original publication/receiving deadline and local custody; receiving-only key retention does not permit new encryption.

Contrast a branch revocation, key change, missing/branch-only device, role or validity gap, prior repair boundary and late newly learned branch. Hold confidential delivery without granting ordinary setup, enrollment, provider grants, history or a route override. Missing eligible receiving authority is not permission to omit a required repair signer or expose the share publicly. Decrypt/stage a proof without installing the repaired roster; installation still needs all candidate/certificate/frontier checks. Existing shape/candidate/HPKE primitives do not implement this full branch-scoped carriage selection.


## Repair proof validation is not ordinary enrollment

Derive a same-key renewal repair from independently validated competing parent snapshots. Require each derived binding's exact deterministic bytes, including the ASCII-first parent authority digest, while the primary repair signer and complete approval set are derived across all parents. Replacing that authority digest with another parent and re-signing the changed binding is not an equivalent repair. A referenced parent's historical state signer cannot replace the derived primary authorizer.

Valid binding authorization and possession without the complete repair certificate remain staged and grant no role. Test missing approval, substituted possession, incomplete parent evidence, changed frontier before installation and atomic failure before commit. Ordinary enrollment against those same conflicted parents remains held. The existing first-repair candidate tests cover deterministic bytes and proof binding using trusted state0 parent snapshots; they do not establish complete state1 parent validation, staging persistence or atomic installation.

Collect a primary authorizer's binding proof and another device's possession proof in a share assembled by a third eligible device. Each forwarded proof must retain its actual signer and purpose. A nonempty top-level proof from a device other than `by`, a substituted proof domain or a sealed source different from `by` must fail the applicable validation. An unsigned public `by` label cannot authenticate the assembler. Compare authentic but unresolved-time evidence with a currently usable approval; neither a claimed old signing time nor an embedded parent bundle may bypass the independent history and current-authority checks. Reject malformed framing before any proof is staged. Combining otherwise valid partial shares cannot install the repair, send an automatic response or increase any device's permissions.


## Retirement does not depend on notice delivery

Prepare a terminal-only bundle and each exact signed/ciphertext notice under the current operational predecessor. Interrupt before and after atomic terminal/outbox commit: uncommitted bytes cannot release, committed retirement stays terminal without acknowledgements, and restart resumes original eligible ciphertext without restoring signing keys. Cancellation of a notice cannot reverse retirement. Show retirement and delivery/uncertainty separately.

At final release race recipient revocation, key/intent deadline, policy, source account access and route retirement. Only operational sender eligibility is replaced by the committed terminal-only permission. A disabled identity-derived route remains disabled; a separately valid mailbox submission permission is not itself an identity permission. Required masking never becomes readable fallback, and an expired key cannot be replaced by creating another post-retirement notice.

On receipt, require exact terminal bundle dependencies, pinned principal, original predecessor/signer/binding, actual terminal and sealed signatures, intended recipient and original receiving/creation bounds. Reject or hold unrelated content, repair shares, other kinds, omitted dependencies, unrelated revocation, stale/competing authority and substituted sender bindings. An old claimed signing time cannot excuse expired authority. A valid terminal proof must not expose intermediate operational heads or trigger automatic replies, setup, grants or history effects. Full frozen-notice persistence/release/receipt integration is not established by shape or generic HPKE component tests.


## Transfer rejection versus per-contact reconciliation

Place a supported contact before another contact carrying an unknown verification mechanism in an otherwise correctly signed and encrypted configuration. Reject complete staging with no staged receipt, installed prefix or default changes. Repeat with missing multipart data, malformed schema and invalid proof. Existing independent trust remains intact. A valid source signature cannot authorize ignoring the unknown record or using a new name for human comparison.

Contrast a fully supported, authenticated and durably staged configuration whose second contact conflicts with the target's existing pin. Reconcile the independently eligible first contact while retaining the second hold and the overall staged result. Installed receipt still requires every selected result; native send readiness remains a separate gate. A fresh deliberately scoped selection uses fresh transfer/request/recipient identities and cannot reset the old outcome, silently weaken verification or claim the original selection completed. The version0 encrypted negative fixture and existing contact reconciliation fixtures do not establish the complete current configuration3 or ongoing own-setup0 workflow; retained configuration2 needs its own exact evidence.


## History authority changes are phase-specific

An unrelated accepted head advance retaining each endpoint's exact binding/key/role may preserve the original transfer. Contrast same-key binding replacement, repair with an unchanged binding retained on one or all parents, revocation, retirement and unavailable ancestry. New grant approval/admission and file handoff must hold old authority; a complete repair cannot be traversed by choosing one parent. A fresh authorized transfer has new request/recipient/identity and cannot rewrite old evidence or reset old uncertainty.

Allow local completion from exact already-admitted and retained files without new disclosure, while unavailable bytes and revoked retrieval remain unavailable. A new result/cancel checks its actual actor's unchanged authority, not fresh permission from a revoked peer; confidential delivery may still be held. Own-actor repair cannot rewrite frozen endpoint references. Preserve an undelivered local result/stop without claiming remote acknowledgement or deleting history. The current state0 renewal fixture demonstrates changed-binding rejection only; it does not validate full state1 repair traversal or public storage/control integration.


## Asynchronous groups retain one authored message

The [selected asynchronous architecture](delivery-policy.md#one-message-several-deliveries) requires more than a successful retry or a locally grouped timeline. Alice’s question and Bob’s answer must reach an originally pending Carol as the same authored contributions, even if her deliveries arrive answer-first or contain duplicates. Hold the missing parent, then resolve it without another visible message or repeated interaction effect. The selected asynchronous agreement and pending-delivery lifecycle define these cases; complete implementation and independent acceptance remain distinct from the selected design. They do not widen earlier envelope5 support.

Reject an otherwise valid delivery authored by Bob that claims to publish Alice’s logical message. Accept a new authorized Alice device’s delivery only with the identical retained authored record, actual current authority, eligible independent native admission and pending disclosure. Exercise missing source content, lost pending-send authority, identity replacement, changed intended scope and a conflicting authenticated authored record. A forwarded old signature or imported archive cannot supply current publishing authority.

Observe the durable authored-message namespace, per-delivery evidence, unresolved graph dependencies and actual side effects across interruption and restart. Test the same logical identity in another conversation, different valid ciphertext for equal authored bytes, invalid input before namespace reservation, duplicates after an uncertain service action, and private/Bcc correlation attempts. No arrival-order winner, content-text deduplication, shared membership inference or sender-controlled verified flag satisfies this acceptance boundary.


### Two typed conflict ledgers

Exercise the [delivery/authored conflict matrix](event-identifiers.md#keep-delivery-identity-separate-from-message-identity) in both arrival orders and after restart. Include one delivery key with identical authored bytes but different native preparations; the same delivery key with unequal bytes under one authored key; different authored keys sharing a delivery key; cross-conversation reuse under the same principal; identical random spellings in the two namespaces; and a rejected second candidate attempting to reserve either key.

Observe both retained variant ledgers and exact authored effect counts. No early delivery-ID deduplication may hide authenticated authored equivocation. A delivery conflict alone cannot retract independently accepted content, manufacture an authored conflict, repeat an answer or reset an uncertain transport result. Check independently correlated outcomes against exact retained preparations, not a now-ambiguous delivery key. A trusted-input in-memory ledger supplies comparison/state evidence only; it does not prove native validation, durable transactions, effect execution or transport reconciliation.

## Pending recipient bindings are creator-authorized

For the [intended-recipient scope](delivery-policy.md#an-invitation-is-not-yet-an-encryption-identity), validate exact field sets, ObjectId/principal/mailbox grammars, author-slot binding, empty-versus-single expected principal, slot order, duplicate slots/mailboxes, null/unknown members and scope-root equality. A received definition cannot clear a known expected principal or mutate the already accepted root.

Alice creates a scope with Carol unresolved; Bob’s ordinary reply to the ready discussion proceeds while its Carol delivery remains pending. Bob’s own resolution of Alice’s Carol slot cannot activate it. After independently authenticated Alice resolution and Bob’s independent current recipient/policy checks, only Carol’s original pending delivery becomes eligible. Losing Alice’s availability before resolution does not stop Bob’s other deliveries or authorize a guessed binding.

Exercise resolution-before-root, reply-before-root, matching repeated resolution, a conflicting resolution from a second eligible Alice device, unauthenticated attempted poisoning, current revocation, changed mailbox ownership and same-principal device/key renewal. Preserve conflicts across restart and ensure old acceptance does not import live device or disclosure authority. The recipient view must distinguish invited people from the message’s actual intended recipients, and lack of local delivery evidence from universal pending/offline status. Neither a To/Cc role nor a scope entry subscribes a copied observer to future discussion. These are required successor acceptance cases; no current native/control implementation is established by schema text.


## Authored records are independent of delivery envelopes

The [authored0/envelope6 components](event-encoding.md#asynchronous-authored-records-and-deliveries) require strict separate parsing and exact original authored bytes. Verify the seven-field slot presentation, intent1 applicability, creating-versus-existing scope, body and wrapper bounds, canonical base64, native author/conversation equality and exact native-audience/slot-map equality. Unsupported current contexts cannot activate these records. Slot grammar does not prove native membership or mailbox ownership.

Exercise two validly admitted preparations of one authored record, a changed ciphertext with a fresh delivery identity, exact prepared retry, old delivery identity reused for changed native preparation, altered original JSON whitespace, different authenticated content under the same logical identity and identical random identifiers in the separately typed delivery/logical namespaces. Logical parents, button questions, replacements, reactions, corrections, service self-references and resources must never be retargeted to the outer delivery event. Inactive candidates cannot poison the accepted namespace.

The [synthetic Alice/Bob/Alice samples](examples/async-exchange.json) check record consistency and exact repeated authored octets. They do not authenticate native senders, execute a receive/store queue, implement conflict transactions, perform network interchange or establish successor support. Full acceptance still needs the complete selected agreement, actual native author/scope/admission proofs, per-copy release and restart/effect observations, including Carol’s reply-before-root arrival. A static fixture check cannot substitute for these outcomes.


## A simpler reader can remain in the asynchronous discussion

Under the selected [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement), validate the fixed full twelve-kind application, assertion10’s one required ordinary offer and optional managed offer, complete sorted interactions lists, exact context10 and selected admission/control versions. An empty interactions list is valid; omission, duplicates, unknown names, mixed versions, a reduced readable vocabulary or old subset-closure offers cannot satisfy it.

Deliver the identical authored question to Bob with Answers support and Carol with no interactive capabilities. Both must validate/read the known question and mandatory reply intent. Bob can use his independently implemented/authorized answer control; Carol can compose a permitted ordinary reply with the same logical parent. No optional-module intersection may strip or replace the question, hold the entire ready group or manufacture interaction permission. No-replies still suppresses written composition, including for Carol; service/holder/correction data must not activate credentials, HTTP requests, managed history or replacement effects through passive reading.

Complete native evidence must additionally prove actual credential/roster/slot audience equality, current scope creator resolution, initial10/roster7 or established10 admission, ordinary2 or managed4/final5 transitions, sealed2 exact magic/domain/framing and canonical mime-suite-v2 resource selection by logical event. A matching application fixture does not establish those cryptographic or stateful outcomes. Earlier context9/assertion9 carriers cannot be widened or sniffed into this agreement. Automatic setup, paired metadata and the pending-send lifecycle have selected contracts. Joined implementation acceptance remains required for an implementation claim.


## Paired scope observations are setup rather than correspondence

[Configuration3](paired-configuration.md#transfer-asynchronous-scope-metadata) requires approved current own-device request/source/target roles, exact version/domain/magic/manifest/part binding and complete staging before effects. Exercise source/target changes during processing, malformed creator public evidence, unknown fields or versions, a valid prefix followed by a bad scope and private-pair leakage. The expected result is no partial installation or secret-retirement extension.

A new device with accepted scope metadata can select eligible future content while the old human root and parent messages remain absent. It must not create those messages, inherit their reply policies, manufacture actor credentials or make an archived action live. Observe separate setup and authored-message ledgers. Conflicting origin definitions, creator/event reuse across conversations, local/current peer disagreement, binding forks and negative flags survive re-export from another own device. Unaffected ready slots stay usable for independent work. Scope metadata is not actual sending readiness.

Keep invitation mailboxes separate from a new contribution’s chosen protected To/Cc addresses. Test a currently eligible alias for the same bound principal without changing scope membership, an alias owned by another principal, an unresolved slot with no creator binding and an attempted changed mailbox in a frozen retry. Role order and actual alias remain inspectable; an address change cannot silently add a person or bypass current association/route policy.

Typed in-memory merge evidence alone cannot establish wire/identity/signature/current-role validation, persistent transactions, actual native admission or a mail client. A trusted-input model must identify its assumed validation boundary; it cannot accept a peer-supplied validated flag as that boundary. The joined acceptance requirements remain independently necessary.


## Acquire setup without stopping ready recipients

Exercise the three asynchronous acquisition paths with the exact required agreement, not a service's generic claim of encryption support. Alice must be able to prepare an eligible delivery to Bob while Carol's valid request remains pending, under the frozen send plan.

::: {.details summary="Asynchronous acquisition acceptance cases"}

| Boundary | Required cases |
| --- | --- |
| Discovery and account permission | Descriptor2 exact schema/commitment; rejected rollback and overlapping version prefixes; fresh exact grant2/configuration/role using an eligible retained link without unlinking a healthy family; relabeled link proof, old token, reset family, wrong module/origin and altered approval rejected. |
| Known pair | Control2 signed original request/response; assertion10 identity/mailbox/head/binding matches; wrong agreement/domain/purpose/requestHash/nonce and target-head changes fail. |
| First contact | Bootstrap2 exact source/target descriptor commitments, source inspection, uniform pending and original version2 result; live/offline results remain distinct; no human content or group roster in acquisition traffic. |
| Ordinary mail | Setup2 dedicated assertion/key, exact direct authenticated request, sealed2 response for the retained attempt, no response loop or other recipients; older/mixed records and address/advertisement substitution fail. |
| Selection | Same full readable application across devices with differing interactions, including an empty list; older subset closure cannot strip authored content or replace missing assertion10. |
| Per-delivery progress | Bob eligible/Carol pending; late setup retains original intent/scope/content and current separate release checks; changed or cancelled revision cannot activate from a late result. |
| Shared negative state | Cross-version duplicate package allocation, replay, reset/block/budget bypass and restored uncertainty fail; exact retry never refreshes a deadline or erases prior uncertain disclosure. |
| Address and privacy | Selected eligible same-principal alias uses its own exact account/delegation/grant/allocation namespace; unknown slot remains unresolved; unavailable required masking holds rather than leaking private scope through a fallback. |

Unsigned descriptor examples and signed-record byte/schema tests can establish their stated component properties. They do not establish public OAuth/provider deployment, complete assertion10/native admission, durable handoff, user-interface behavior or a full current-suite client. Each claimed implementation must exercise its actual authority and carriage boundaries; independent implementations/security review remain separate evidence.

:::


## Refresh setup from another own device

An enabled device can obtain newly learned setup from any eligible current own-account administrator, independently of old message history or the original pairing source. The [own-setup exchange](paired-configuration.md#keep-setup-current-between-your-own-devices) defines its exact request, encrypted snapshot, staging and restricted-root reconciliation.

::: {.details summary="Ongoing own-device setup acceptance"}

Exercise a scope learned after pairing, original administrator offline and another eligible administrator responding; missing human root with accepted metadata; restricted-root coverage/unavailable results with no global-default installation; snapshot reconciliation; current role/binding/anchor conflict; target receiving-key substitution and wrong account; mixed old pairing/own-setup proof; final-part failure without an installed prefix; source revocation, cancellation and expiry during staging; exact ciphertext/receipt retries; private-pair isolation; no response-to-response request loop; and future native sending with actual new-device keys and current delivery authority.

Metadata cannot supply a missing reply/quotation/action target, independent human verification, native membership, an outbox or a released live key. A transferred observation resolves the scope-definition dependency only. Test source/recipient binding before encryption as well as after receipt, and enforce the separate custody lifetime of ordinary control keys versus the transfer-only age secret. Returned unavailable facts do not prove global absence or clear older conflict evidence.

:::


## Preserve pending-message identity and authority

A client claiming the selected asynchronous lifecycle exercises the [pending-delivery contract](delivery-policy.md#complete-a-pending-delivery), rather than treating a queue demonstration as proof of native authentication.

::: {.details summary="Late-delivery lifecycle acceptance cases"}

| Scenario | Required result |
| --- | --- |
| Bob ready, Carol pending; Carol receives answer first | Retain each author's independent original send authority; hold the exact missing parent, then assemble one question and answer. |
| Same principal at two selected mailbox slots | Deduplicate the native principal without collapsing the two mailbox obligations or claiming both from one scoped handoff. |
| Restart before preparation or after uncertain release | Preserve original content, revision, dependencies and uncertainty; do not reconstruct content, reset native state or create a fresh human action. |
| Exact retry versus changed audience, epoch, device or route | Retry retained eligible bytes under their original delivery identity; replacement preparation gets a fresh identity and keeps prior exposure evidence. Successful recipients are not retried. |
| Dave joins the managed group while Carol waits for an older message | Hold a preparation that would disclose the old message to Dave; no false audience declaration or mode switch. |
| Setup expires while original send intent remains live | End the original setup attempt; a separately authorized bounded attempt may continue without changing the authored message or extending its release deadline. |
| Alice stops her remaining copy | Stop her unreleased work, retaining handoff and uncertainty; do not cancel Bob's answer or claim global invitation revocation or recall. |
| Edit after partial delivery | Retain the original immutable identity and any deliberate stop; apply the edit's independent target and new-event rules without sending old text merely to satisfy its dependency. |
| Two valid deliveries of one operation | Commit one local effect or pending dependency with original evidence; preserve a remote service operation's original identity and uncertain result. |
| Accepted scope metadata but missing human target | Permit eligible fresh composition; do not manufacture a reply permission, quoted source or question from that metadata. |

These are required acceptance cases, not a report that every stateful path has an implementation. Candidate record parsing cannot establish current roles, native membership, transactional persistence, worker fencing or remote effects.

:::


## Restore and migrate asynchronous correspondence

The [authored-history mapping](encrypted-archives.md#preserve-messages-that-have-several-deliveries) and [migration procedure](suite-profile.md#migration-and-remaining-integration) preserve exact content without reviving authority.

::: {.details summary="Authored history and migration acceptance cases"}

| Scenario | Required result |
| --- | --- |
| One authored record, two envelope6 deliveries | One historical message projection, distinct retained delivery provenance, original logical reference and complete collection entry counts. |
| Delivery ID used as a contribution reference | Reject the known mapping mismatch; do not relabel the original authored record. |
| Answer selected without its question or scope root | Preserve missing dependencies; no automatic history expansion, invented label or live effect. |
| Supported authored0 with bad resource bindings | Reject known invalid mapping before disclosure and on import. An older reader may instead preserve the genuinely unsupported record as opaque without claiming these semantics. |
| Imported root, resolution or conflicting author claim | Historical writer provenance only; no live slot binding, namespace poisoning, native admission or outbox restoration. |
| Genuine native delivery arrives after history import | Independently validate it; retain both provenances and once-only live effects without replaying imported actions. |
| Older message appears beside new authored0 traffic | Keep each exact grammar and context. No inferred cross-version parent, slot mapping or interaction authority. |
| Upgrade during a queued or uncertain old send | Preserve its original delivery and outcome; no automatic fresh authored0 duplicate. |
| Ordinary versus managed migration | Fresh native admission in both; authorized ordinary grouping may retain its visible conversation identity, while managed migration has a separate conversation. |
| Older receiving material expires after upgrade | Preserve unavailability and original exposure; do not renew secrets or interpret old ciphertext through a new parser. |
| Same principal reuses an accepted old event ID in authored0 | Retain an authenticated namespace conflict; a version change is not another namespace. Untrusted archive claims cannot create this evidence. |

Archive byte-preservation evidence does not establish authored0 semantic parsing, full resource validation, native revalidation or transactional live effects. Tests and reports must identify which of these boundaries they actually exercise.

:::

## Authenticate existing mail services without weakening account policy

The [submission/access profile](transport.md#authenticate-the-discovered-service) must authenticate the intended account service before disclosing credentials. A successful connection still says nothing about a correspondent's message-encryption support.

::: {.details summary="Mail service identity and TLS acceptance cases"}

| Scenario | Required result |
| --- | --- |
| Existing TLS1.2 service, permitted ECDHE/AES-GCM suite, valid service certificate and compatible account minimum | Connection permitted after all checks; no end-to-end protection inference. |
| Same service with an account minimum of TLS1.3 | Hold account operations; do not lower the minimum or try credentials elsewhere. |
| TLS1.2 peer offers only static RSA, DHE, CBC, or lacks required EMS/secure renegotiation | Fail the restricted compatibility profile despite an otherwise valid certificate. |
| TLS1.2 client omits required `signature_algorithms`, or a permitted AES-GCM suite is followed by an MD5/SHA-1 handshake signature or invalid signature encoding | Reject; the suite's PRF hash and a valid certificate cannot excuse the handshake failure. |
| Unsigned SRV target presents a valid certificate only for the target | Fail unless that target was independently authorized as a reference; routing and SNI do not authorize it. |
| Discovered IMAPS service presents the original-domain DNS-ID or correct `_imaps` SRV-ID | Either independently permitted matching reference can authenticate it after path/status checks. A wrong service label cannot match the SRV reference. |
| Hostname delegation is authenticated; another hostname appears only through CNAME | Only the authorized delegation can add its DNS-ID. Do not use the CNAME to expand references. |
| Directly configured IP literal versus an address returned by DNS | Only the former can supply an IP-ID reference. Omit IP-literal SNI; no reverse-DNS substitution. |
| CN-only, partial-label wildcard or multiple-label wildcard certificate | Reject the invalid name match. A separate valid permitted SAN match remains independently evaluated. |
| Authorized STARTTLS succeeds after different pre-TLS EHLO capabilities | Apply the same account policy, obtain fresh EHLO capabilities and do not reuse pre-TLS advertisements. |
| TLS1.2 mail compatibility exists beside an Email/2 HTTPS action service | HTTPS still requires TLS1.3. No cross-account credentials, certificate exception or early-data permission follows. |
| Account TLS policy is mistakenly applied to a DANE-EE relay | Preserve the relay's own TLSA rules rather than substituting account Web PKI name/expiry checks. |
| Reused connection or resumed session has expired validation, missing required staple or newly learned distrust | Revalidate or hold/full-handshake as specified; resumption cannot refresh evidence by itself. |

Verify the [common TLS1.3 capabilities](service-answers.md#tls-1-3-implementation-capabilities) through the selected backend, including required cipher/group/signature support, cookie handling and certificate-signature extension support. Test conditional extension placement and rejected malformed handshakes rather than requiring every extension in every message. No client certificate or account credential is released by a capability test.

Use actual maintained TLS and certificate backends for claims about negotiation, wire extensions, status and credential withholding. A reference-name table or mocked version value does not establish those behaviors. Existing HTTPS fixtures do not by themselves prove the mail adapter's SRV-ID, TLS1.2 or STARTTLS integration.

:::


## Public registration and revocation outcomes

Exercise the [selected provider authorization binding](provider-discovery.md#register-and-sign-in-through-the-selected-service) through actual registration and token-family storage before claiming joined provider support. Registration HTTP400, HTTP401, malformed errors, substituted successful metadata and lost responses must not install authority, navigate to error-provided URLs, disclose a developer secret or silently change callbacks or scopes.

Revocation cases include a recognized refresh token with its original client, a recognized token with another valid client, an unknown client, and an unknown or already-invalid token. Only the authorized recognized grant changes; a matching client identifier alone cannot revoke another family. Verify the serialized cascade to derived queue reads and writes. Test ignored or misleading hints, bounded lookup work, arbitrary inert HTTP200 bodies, HTTP503 with Retry-After, and lost success responses. Uncertain results leave local use disabled and retain only the exact original bounded retry binding. None can authorize a new endpoint or authentication method. Component metadata checks do not establish these server and queue effects.


## Selected age file and key encodings

Archive and own-device configuration claims exercise the [selected age binding](encrypted-archives.md#create-a-recovery-kit-before-relying-on-backup). Test canonical public and secret Bech32 forms, mixed case, Bech32m substitution, bad checksum, incorrect decoded length, nonzero or excess padding, and any supported human-entry canonicalization before signing. Invalid encodings must not become encryption recipients or recovery identities.

Exercise independent X25519 wrapping keys, all-zero shared-secret rejection, tampered header or wrapped file key, payload chunk boundaries, modified final flags, truncation, trailing bytes and an empty final chunk after a nonempty payload. Test both empty and multi-chunk plaintexts. No valid prefix may install archive or configuration state. These tests must use the actual selected age implementation; a hand-built compatible-looking container or a library name alone does not establish file-format acceptance.
