---
title: Identity continuity and device lifecycle
order: 9
blurb: first contact · key changes · recovery · devices
sectionNav: true
---

# Identity continuity and device lifecycle

Automatic encryption must work without requiring people to administer keys for every conversation. It must also distinguish a newly observed key from an established correspondent. This chapter defines proposed authorization behavior. The [security profile](security-profile.md) supplies device-binding records and proof constructions; [identity-state records](identity-state.md) define the roster and ordinary transitions. Integrated validation, freshness and recovery remain unfinished.

The [encryption journey](encryption-journey.md) specifies the person-facing flow for these transitions, including the unavailable emergency-recovery and encrypted-backup paths.

## Keep evidence separate from policy

A correspondent record identifies the exact mailbox being contacted and a history of identity evidence. It does not normalize local parts using provider guesses. A cryptographic principal is a profile-defined identity, not simply the mailbox string or the newest key attached to it.

The record contains separate facts:

| Fact | Meaning |
| --- | --- |
| Observed key | Key material was received through a recorded channel |
| Proof of possession | An endpoint demonstrated possession under a specific protocol and context |
| Continuity | New material was authorized by an already accepted identity under its transition rules |
| Verification | A recorded mechanism established the identity binding at a stated assurance level |
| Revocation | An authorized revocation applies to a stated key, device or identity |
| Conflict | Competing claims cannot be resolved under the accepted authority rules |
| Capability freshness | A feature assertion is currently usable within its own validity interval |

These facts MUST NOT collapse into one trusted/untrusted flag. Proof of possession does not prove who owns an email address. A provider's account assertion does not prove continuity with a previously verified endpoint. Expiry of a capability does not revoke a key or erase a policy requiring encrypted delivery.

Verification records identify the mechanism and its scope. A user comparison, authenticated introduction, provider assertion and transparency observation are distinct evidence types. The UI may summarize them, but must not label all of them as equivalent verification.

## First contact

A client may record advertisements from ordinary mail as observations without responding automatically. Before using a candidate key, it validates the key's structure, applicable algorithm policy, expiry and available revocation evidence under the selected profile. Invalid key material cannot become a delivery capability merely because its MIME wrapper is valid.

A remembered first-contact policy may allow encryption to an observed, unverified identity. If used, the client labels this as encryption without verified correspondent identity and retains the initial evidence for later continuity checks. This mode protects against some observers but MUST NOT be presented as resistance to an active first-contact substitution attack.

A stricter policy may require verification before sending sensitive content. Absence of verification does not authorize ordinary email unless that fallback was separately permitted. Existing legacy recipients remain reachable under the sender's selected fallback policy; they are not silently enrolled in a cryptographic identity.

## Key transitions

A transition identifies the prior principal state, the newly authorized material, its intended role and scope, and the authorization evidence. The selected profile defines exact serialization, signatures and freshness checks. A generic signature by any old key is insufficient if that key lacked transition authority or has been revoked.

On receiving a transition, a client MUST:

1. Resolve the prior identity state and the authority permitted to change it.
2. Validate the transition proof, validity interval and applicable revocations.
3. Check that the new material has the required capabilities and proof of possession where the protocol requires it.
4. Record the transition without deleting the earlier evidence or historical message attribution.
5. Re-evaluate pending deliveries against the new state before submission.

An unlinked new key creates a competing claim, not an automatic replacement. A later timestamp, newer email, successful account login or provider directory response cannot alone resolve the conflict. A user may deliberately establish a new identity after reviewing the change; the client records a continuity break instead of rewriting the old history as though the new key had always been trusted.

Concurrent authorized transitions require the selected profile's branch-resolution rule. Without such a rule, preserve both and hold affected deliveries. Do not choose by delivery order. Duplicate transition records are idempotent; replay of a superseded state cannot roll the record backward.

## Device enrollment

An identity may authorize several devices. The device authorization record specifies the device key, permitted roles, validity and authorizing identity state. The client distinguishes a device authorized to receive messages from one authorized to add devices or recover the account.

Mailbox access alone MUST NOT enroll a new device into an established end-to-end identity. Enrollment requires an existing authorized device, a previously configured recovery authority, or an explicit new-identity procedure. The routine experience can be a device approval or authenticated transfer; it need not expose raw keys to the user.

A newly enrolled device receives only the state and history explicitly authorized for transfer. Permission to receive future messages does not imply permission to recover every historical key. State transfer must use the selected profile's protected channel and bind the receiving device, account and purpose to prevent an approval being reused for another enrollment.

The sender's encryption target set is the authorized device set supported by the chosen security profile at send time. The service must not silently append a device solely because it can access the mailbox. Legacy clients sharing that mailbox may display encrypted objects they cannot read; capability discovery must not claim otherwise.

## Finding and synchronizing your own devices

A client can synchronize the public evidence for an account without sharing private device keys. The local experiment starts with an explicitly trusted account anchor on each device. An existing administrator approves the exact new binding; the normal signed successor rules then determine whether enrollment is authorized. Mailbox login and provider device lists cannot supply that approval.

Each device publishes its own current capabilities. After an identity change, an older advertisement is stale even if its device remains authorized. The inventory distinguishes authorized receiving devices from devices with currently usable capability evidence. Missing evidence remains visible instead of silently dropping a device from an all-device delivery plan.

> [!note] Completeness has a scope
> A complete inventory is complete relative to the locally accepted identity head. It is not proof that no newer revocation exists, that every device is online, or that an admission package remains available. Package validation and single-use checks still occur at admission. A displayed inventory never authorizes sending by itself.

::: {.details summary="Local approval, publication and synchronization experiment"}

### Trusted setup and approval

Local configuration binds the account identifier, principal, local device and exact mailbox spellings. This is configured routing information, not independently verified provider ownership. The public-evidence coordinator requires a trusted anchor handoff. The [two-device pairing experiment](#pairing-another-device) supplies an explicit independent-channel handoff and public relay; it is not a standardized or deployed pairing service.

An approval names the exact proposed binding and predecessor. Accepting enrollment, consuming that approval and retaining the public publication record happen in one transaction. A changed predecessor requires renewed approval. A receive-only device cannot grant enrollment authority, and a simultaneous authorized successor is handled by the ordinary conflict rules.

### Public evidence and local settings

Publication is off until explicitly enabled through local settings. Receiving a record cannot enable it. The local channel carries only original signed identity bundles and ordinary-mail capability evidence; it carries no private device keys, MLS checkpoints or historical content. Exact publication retries preserve bytes. A stale advertisement is held from new publication while historical identity records remain available for chain resolution.

The reference channel is a local public-record spool. Source cursors advance with retained evidence and accepted state in the same transaction. Per-device statements retain their own signature and current authority checks. Resource limits are adjustable local policies; failure preserves the prior cursor and state. Live provider synchronization remains separate; the pairing experiment below exercises the remote public-evidence exchange against a local HTTP relay.

### Delivery and history

The joined experiment enrolls a second device, synchronizes two independent stores, and delivers a new protected conversation through SMTP. Each device still receives its own authenticated admission. Preparation and release recheck the actual identity and routing dependencies; a revocation learned after preparation can stop DATA submission.

Enrollment does not join existing groups or reveal old ciphertext. Existing conversations require their own authorized membership transition, and history transfer requires a separately scoped disclosure. The public synchronization path does not implement key backup, protected history transfer, branch merging or account recovery. Restored historical evidence cannot roll back an accepted revocation.

:::

## Pairing another device

To add a new device, scan the existing device's pairing code on the new device, then scan the new device's code back on the existing one. Review the account and permissions before approving. The full comparison value remains available as an accessibility alternative over an independently authenticated channel. A code delivered through the same untrusted relay or unexpected email does not supply that confirmation.

The new device creates its own private keys. The exchange carries only public account evidence, the proposed public device binding, proof of possession and the signed enrollment result. It transfers no mailbox password, private identity key, live conversation checkpoint or message history. Mailbox login cannot replace the existing device's enrollment authority.

> [!note] Two different expiry dates
> The pairing session expires quickly according to local client policy. The approved device authorization has its own validity period, bounded by the authorizing device's authority. Finishing a short pairing session does not mean the new device expires with that session.

After approval, the interface distinguishes enrollment accepted on the existing device, enrollment received on the new device, and readiness for protected mail. Publication remains a separate local setting. New capability evidence and normal invitation checks are still required before protected delivery.

### Finish pairing with usable encrypted sending

QR pairing is the normal add-device path. The existing authorized device approves the new device, which creates and keeps its own private keys. The client MUST continue automatically from enrollment through account connection, trusted-contact setup and encryption preparation. Enrollment alone MUST NOT be presented as completed setup.

The approval distinguishes permission to send and receive from permission to administer other devices. An account may have multiple administrator devices; no primary administrator is required. A device granted ordinary participation does not thereby gain enrollment or revocation authority.

Before reporting the new device ready, the client MUST:

1. Accept the exact signed enrollment on both devices, retaining the mutually confirmed pairing commitments and current account identity. The new device must possess its own enrolled key.
2. Connect the approved mailbox and sending service under a separately valid account authorization. Reuse an existing authorized account connection flow where possible. A QR enrollment signature is not a provider access token, and a provider password is not enrollment authority.
3. Transfer the approving device's selected contact associations, accepted peer identity anchors, current public evidence, scoped verification decisions and disclosure/freshness preferences through a confidential, authenticated own-device setup transfer bound to this pairing and its exact new device. This is security configuration, not correspondence history. The new device MUST NOT require routine re-verification of unchanged contacts merely because it is new.
4. Validate the transferred evidence, preserve its original trust scope and dates, and recheck current authority and known revocations. A previously unverified contact remains unverified. A preexisting conflicting pin or newer revocation on the new device holds that contact; the transfer cannot overwrite it. The transfer cannot reset a pending challenge, revive an expired package or copy a one-use private package key.
5. Publish the new device's own support and admission material where enabled, and automatically prepare protected delivery to existing contacts using current valid public material or the content-free setup exchange. Each message still passes its normal audience, agreement, package and release checks. No additional human contact-by-contact approval is required unless an actual conflict, changed trust or the selected policy calls for it.

> [!ex] A new laptop
> You scan its pairing code using your already authorized phone and approve the account and permissions. Setup brings across your trusted contacts and prepares encryption using the laptop's new keys. You can write an encrypted email to a known contact without asking that person to verify you again. Their compatible client validates your account's signed device addition when it accepts the new setup.

Newly established protected conversations do not require possession of old message keys. Existing cryptographic groups still require authenticated device admission; the client MUST schedule that work automatically and preserve the draft while it finishes. A new cryptographic context cannot be presented as authenticated continuation of an old group without that group's continuation authorization. Do not create a visible duplicate conversation merely to hide an unfinished admission.

Readiness is scoped: account sending ready, contact setup pending, or contact ready for protected sending. A contact that is temporarily unreachable or lacks usable published setup material can remain pending without preventing sends to other ready contacts. The interface must identify the remaining wait without asking the person to manage keys. It MUST NOT show a general ready state while all protected sends are still held.

Correspondence history transfer and synchronization are separate capabilities. Pairing does not require copying saved messages, a message archive, an old MLS checkpoint, consumed secrets, queued sends or an administrator's private key. A supported history service may run separately under its own authorization; its absence cannot disable future encrypted sending after setup.

After enrollment, the new device requests an encrypted copy of the selected contact security setup. The approving device signs it for that exact request and new device. The new device checks the entire transfer before reconciling it with any security decisions it already holds. An unchanged contact should work without another manual comparison; a conflicting identity must remain visibly unresolved.

The [confidential setup binding](#confidential-security-configuration-transfer) defines that exchange and the required reconciliation procedure. Local experiments join actual pairing, device signatures, age encryption, durable private staging and installation into the reference contact/verification stores. The installed trust supports the existing verified-contact lookup without another comparison. Deployed mailbox connection, automatic acquisition of usable peer setup, existing-group admission and the complete send-ready journey remain unfinished.

::: {.details summary="Experimental pairing binding and durable result"}

### Independent confirmation

The offer binds the account principal, accepted predecessor, authorizing device, exact public anchor bundle digest, configured mailbox spellings, requested roles, session interval and separate device-grant interval. A fresh random session identifier distinguishes concurrent attempts. The request binds that exact offer commitment and the original device-binding bytes with the existing possession proof. Both full commitments are checked through trusted local confirmation input; receiving either record cannot confirm it.

The experimental commitment is SHA-256 over the ASCII purpose prefix, a NUL separator and the original encoded bytes. The prefixes are `email-next/pairing-offer-experiment/v0` and `email-next/pairing-request-experiment/v0`. Comparison uses all 256 bits, never a shortened code. Existing enrollment signature framing remains unchanged.

The local transfer objects use version `0`. The offer has exactly `{version,purpose,session,principal,head,authorizer,anchorBundleDigest,mailboxes,roles,notBefore,notAfter,grantNotBefore,grantNotAfter}` with purpose `own-device-pairing-offer`. The request is exactly `{version,purpose,session,offerDigest,binding,possession}`, with purpose `own-device-pairing-request`; binding bytes use canonical padded base64 and possession uses the existing signature encoding. The result is exactly `{version,purpose,session,requestDigest,head,bundle}` with purpose `own-device-pairing-result` and canonical base64 public bundle. Times retain the exact unsigned-decimal-string rules. Roles are an explicit sorted subset of the authorizer's roles; mailbox strings retain exact spelling. These are experimental transfer objects, not changes to identity-state or device-binding versions.

### Enrollment and receipt

The authorizing device rechecks the current conflict-free head, enrollment role, exact approved binding and whole credible time interval in the enrollment transaction. Both session and device-grant intervals must fit its binding validity. Accepted successor, consumed approval, public publication record and immutable result commit together. The new device verifies from its independently confirmed anchor and atomically records the accepted successor and receipt. A preexisting different account pin is a conflict.

A changed head requires a new offer and confirmation; signed bindings are not automatically rebased. A failed transaction leaves enrollment unaccepted. Retrying an already committed exact request retrieves the original result, including after a response was lost. That historical receipt does not override current revocation or authorize sending.

Withdrawal before commit prevents enrollment. After commit, removing the device requires ordinary signed revocation; deleting a relay record is not rollback. A cancellation on the new device stops its pending acceptance but cannot promise that a remote approval has not already committed. Competing authorized successors retain the ordinary identity conflict rules.

### Relay and demonstration scope

The reference relay is a fixed-origin loopback HTTP service carrying public records. Relay access is not account authority. It may observe metadata, withhold messages or duplicate them; swapped records fail the independently confirmed commitments and normal signatures. Production relay authentication, privacy, abuse controls and deployed provider integration remain separate work.

The local two-device interface displays both QR codes and offers full-value entry. Automated browser checks exercise the full-comparison route, actual signed enrollment, protected SMTP receipt and a later revocation stopping DATA. They do not establish camera scanning, assistive-technology coverage or the trustworthiness of a user's independent channel. Existing conversation membership, old ciphertext access and account recovery remain separate from pairing.

:::

## Confidential security-configuration transfer

This is an authorized own-device setup operation, separate from a correspondence archive. Its permission comes from the independently confirmed pairing and current device authority. An arbitrary imported file, mailbox login, signed peer email or archive-recovery kit cannot initiate it or install trust.

::: {.details summary="Setup records, encrypted contents and reconciliation algorithm"}

### Bind the transfer to the approved devices

Use the exact locally retained accepted pairing offer, request and result. The source is the offer’s authorizing device; the target is the newly enrolled device in the confirmed request. Resolve both bindings from the accepted enrollment result. Endpoint references have exactly `{principal,device,state,binding,key}`, using that result’s head and the existing identifier/key/digest grammars. Both belong to the same account principal and are distinct devices.

For every new effect, require current source `enroll` authority and target `send` authority throughout the credible clock interval, with unchanged accepted binding ancestry back to the enrollment result. Apply the [retained-authority checks](provider-grants.md#retain-an-unchanged-device-binding); an unrelated accepted device addition need not restart setup. A known revocation, changed binding, missing ancestry or authorized fork holds the affected operation. The pairing result alone is not permanently usable authority.

The new device generates a fresh native age X25519 identity for this transfer and protects its private part locally. That private part never goes to the approving device or relay. Its signed request binds the corresponding public recipient to the accepted pairing result. Validate the native recipient’s checksum and encoding through the selected age implementation. Do not reuse an identity-unlocking credential or the archive recovery key for this operation.

Each control wrapper is exactly `{payload,signature}`. Payload is canonical padded base64 of the original strict UTF-8 JSON payload; signature is 128 lowercase hexadecimal characters. JSON uses the event scalar, duplicate-name and depth rules. A record signature is Ed25519 over ASCII `email2/pairing-setup/{kind}/v0`, one NUL octet, the four-octet unsigned big-endian original payload length, then the exact original payload. Kind is `request`, `response` or `receipt`; ordinary Ed25519 is selected, not Ed25519ph. The record reference is SHA256 of this framed input followed by the raw 64-byte signature. Original bytes, not a reserialization, determine verification and references.

The exact payloads are:

| Kind | Members and authority |
| --- | --- |
| Request | `{version,purpose,transfer,session,pairingResult,source,target,recipient,notBefore,notAfter}`; signed by the target |
| Response | `{version,purpose,transfer,session,pairingResult,request,ciphertext}`; signed by the source |
| Receipt | `{version,purpose,transfer,session,pairingResult,request,response,result}`; signed by the target |

Version is `"0"`; purpose is `pairing-setup-` followed by kind. Transfer is a fresh nonzero ObjectId. Session is the pairing session identifier; pairingResult is SHA256 of the exact retained pairing-result bytes. Source/target are the endpoint references above. Recipient is one valid native age X25519 public recipient. Request/response are the complete signed-record references defined above. Ciphertext is canonical padded base64 of the complete binary encrypted file. Result is `staged` or `installed`; neither means mailbox connected or sending ready.

Request start/end use canonical unsigned-64 decimal seconds. Start cannot precede the accepted enrollment state’s issuance, and the entire interval must fit both source and target binding validity. The client selects a finite short setup interval; it is independent of device-authorization lifetime. Persist its original interval and local attempt anchor before release. Whole credible time must remain inside it at source disclosure and new target acceptance. Retry, restart, new capability evidence and receipt retrieval do not restart the timer. A new attempt needs a new transfer identifier and fresh recipient key.

### Freeze and encrypt selected security configuration

Select a consistent snapshot from the approving device’s accepted contact/security records. Do not derive trust from an incoming peer advertisement, or export a concurrent mixture that silently changes a contact’s identity or verification decision. The plaintext is exactly `{contacts,defaults}`. No other top-level members are permitted.

Defaults and each contact policy have exactly `{trust,ordinary,hosted,freshness,maximumAge,maximumUncertainty}`. Trust is `allow-unverified` or `require-verification`. Ordinary and hosted are booleans recording disclosure preferences, not usable hosting credentials or authorization for a new service. Freshness is `cached-continuity`, `recent-checkpoint` or `live-confirmation`, with the meanings in [freshness](freshness.md). MaximumAge is empty for cached continuity and otherwise a positive uint64 decimal duration; maximumUncertainty is empty when no narrower local bound was selected, otherwise a uint64 decimal duration. These preferences cannot waive an independent send requirement.

Contacts are sorted by exact canonical mailbox spelling, without duplicates. Each is exactly `{mailbox,principal,anchor,head,bundle,generation,enabled,verification,policy}`. Mailbox follows [mailbox addresses](mailbox-addresses.md). Principal uses the existing principal grammar. Anchor is the source’s retained identity trust anchor; head is its accepted peer head. Bundle is canonical padded base64 of the required public identity evidence, including both anchor and head and the necessary chain/proofs. Generation is the source’s association-generation uint64 string, namespaced to the source decision record; it does not replace the new device’s local generation. Enabled is boolean. Policy is scoped to this exact mailbox/principal. A disabled association remains disabled.

Verification is a list sorted by `(originDevice,id)`, without duplicate pairs. Id is a nonzero ObjectId; originDevice uses the existing nonzero device grammar and identifies the device on which the original comparison decision was made. Each entry is exactly `{id,originDevice,mechanism,anchor,notBefore,notAfter,continuity,status,revision}`. This transfer selects mechanism `human-comparison-v0`; the source must have retained that actual decision or its previously authorized own-device transfer provenance. A device re-exporting inherited verification preserves the original originDevice, id, scope, dates, status and revision. Namespace a decision by the own account principal, originDevice and id; pairing a third device cannot make a prior withdrawal look like a different decision. Anchor names the compared accepted peer state present in the bundle. Times preserve the original ordered uint64 validity interval. Continuity is `anchor-only` or `ordinary-authorized-descendants`; status is `accepted` or `withdrawn`; revision is the original uint64 decision revision. Empty verification means no transferred independent verification, not a request to remove the target’s independently retained evidence. Unknown mechanisms hold that contact instead of being relabeled as this one. The currently approving device attests this retained evidence; originDevice attributes the original comparison. Neither attribute alone is independent proof of a human comparison, and inherited verification must not be described as a comparison performed on the new device.

Exclude message bodies, attachments, drafts, conversation/MLS checkpoints, private device or package keys, consumed secrets, account passwords, access/refresh tokens, billing state, queued sends and pending challenges. Transfer only public peer evidence and the selected scoped decisions/preferences. An archive container is not accepted as this plaintext and cannot activate live trust.

An original comparison decision is immutable in mailbox, principal, compared anchor, validity interval and continuity scope. Changing those facts requires a new comparison identifier. A valid own-device withdrawal is terminal for that origin decision: retain withdrawn status even when another device has a larger accepted bookkeeping revision. Merge its revision by the greater numeric value; never wrap, reset its validity or restore accepted status through a later import. Local withdrawal increments the uint64 revision unless already at its maximum; at that maximum it still records terminal withdrawal without wrapping. The withdrawal flag takes precedence over an accepted record at the same revision. Keep original local comparison provenance and separately retain imported update evidence.

Encrypt the complete plaintext using the existing [C2SP age v1.1.0 binary format](https://c2sp.org/age@v1.1.0), with one native X25519 recipient stanza for the target’s request recipient. Armor, password recipients, plugins, additional recipients and archive-kit recipients are outside this binding. Use an age implementation and complete final authentication; do not construct a replacement cipher. This is not a post-quantum claim. The source signature separately authenticates the ciphertext and exact request; anyone knowing a public encryption recipient could otherwise encrypt replacement data.

Persist the original request, frozen selection and exact signed response before releasing it. An exact retry returns those bytes; changing the selection, recipient or validity under that transfer identity conflicts. A failed precommit attempt has no released result and may be retried. Once disclosed, cancellation cannot recall the configuration from its intended device.

The u32 signature framing bounds a payload to 4294967295 octets. Implementations must additionally declare finite input, plaintext, header, processing-time and staging limits before allocation; these are processing limits, not contact-count or account-plan quotas. Exceeding one is an explicit incomplete/resource-held setup outcome. Do not truncate a selection, activate a prefix or report full readiness from incomplete processing. The local experiment has smaller disclosed budgets; it does not establish support for arbitrarily large contact collections.

### Accept, reconcile and report readiness

1. Require an active locally retained request created by this newly enrolled device after the accepted pairing. Match the transfer, session, pairing-result digest, source/target and request reference exactly. Validate the source signature and current unchanged authority before decrypting. A valid unsolicited response cannot create its own request or trust anchor.
2. Use the locally protected fresh identity whose public recipient equals the signed request. Require the selected one-recipient binary age format, complete decryption and final authentication in private staging. Unknown members, malformed records, wrong keys, truncation or an exceeded limit leave live state unchanged. Do not render or activate partially decrypted data.
3. Validate each peer’s complete identity/binding proofs and accepted-chain relationships. Where the target has no peer pin, the authorized own-device transfer supplies the source’s exact retained anchor; the peer’s self-assertion alone does not. Historical proof checks do not grant an expired binding current send authority. Record the own-device transfer as the pin’s provenance. Validate historical proof relationships in an isolated staging context before mutating a live peer pin. The currently authorized own-device source attests that this was its accepted history; checking a state at its declared issuance does not establish independent signing time, present validity, peer presence or absence of withheld later revocations. An ordinary incoming peer bundle cannot obtain this special snapshot-import authority.
4. Reconcile with current local evidence. A different existing pin holds that contact. A target already holding a later accepted descendant retains it; an incoming descendant can advance only through the ordinary authorized transition rules. Neither missing evidence nor a fork selects a winner. Preserve known revocations, conflict evidence and historical attribution. The transfer cannot roll back a newer head, resurrect a revoked device or reset package consumption.
5. Preserve verification scope, original dates, revision and source decision provenance. A known withdrawal or conflicting local verification cannot be undone by an earlier source record. An unverified association cannot become independently verified merely because this transfer is signed. Apply transferred defaults to unconfigured setup; preserve explicit local preferences. An explicit local default remains applicable when there is no existing local per-contact override; a transferred weaker or different preference cannot silently replace it. Conflicting selections hold the affected sending decision rather than silently weaken it.
6. After complete authenticated staging, reconcile each selected contact in its own transaction, rechecking own-device authority, cancellation, original deadline and the relevant local heads/generations. Commit that contact’s association, eligible verification, selected policy and transfer provenance together. A failure rolls back that contact’s activation and retains an actionable held outcome; it cannot leave a half-installed pin or verification decision. Preserve per-contact outcomes durably. Different authenticated bytes under an accepted transfer identity retain a transfer conflict and hold further activation and new use of associations/verification derived solely from that transfer; unauthenticated junk cannot poison it. Preserve the underlying records and attribution rather than destructively erasing them. An exact accepted retry returns its stored result without applying it again.
7. Commit an immutable `staged` receipt with the complete authenticated private staging record. Retire the transfer-only secret recipient after that commit, cancellation or expiry; duplicate response handling uses retained evidence without decrypting again. Later contact reconciliation does not need that secret. Issue an `installed` receipt only after every selected contact and the selected defaults have completed reconciliation; a partial selection retains staged/held status and its durable per-contact outcomes. Neither receipt authorizes a human-message send. Recheck current contact/device support, fresh packages, selected agreement and ordinary release gates. Production secret custody and physical storage erasure need their own evidence.

A target may later issue the `installed` receipt for the same request/response after successful reconciliation. It has a different signed-record reference from `staged`; this is the only selected receipt progression, and it cannot move backward or bind a different response. A duplicate receipt has no effects. The local experiment implements only the staged result.

Contacts may have individual pending/conflict outcomes. One held contact does not prevent a ready one from sending; the application must retain the remaining work and cannot claim the entire selection installed while part is missing. A request can be explicitly cancelled locally; deleting a relay copy cannot undo remote enrollment or an already committed installation. A remotely delivered cancellation protocol is not selected by these records.

### Provider connection and existing conversations

The new device connects the same mailbox using the provider’s normal supported account-access authorization. For upgraded control services, use [native registration/browser authorization](provider-discovery.md) and a fresh [account/device link](provider-grants.md#connect-the-account-and-its-device) for this exact enrolled device and OAuth family. Validate the returned account and provider-authorized mailbox against the paired account selection. An incoming setup field cannot select a login origin or reset a provider-linked principal. The control-service management scope is not itself an IMAP/JMAP or submission credential; obtain the mailbox adapter’s required authorization separately.

A provider or OS account broker may streamline its own login/consent flow. No transferable mailbox token or universal invisible account handoff is defined here. If the provider requires login, keep it in the setup journey. If the required account connection is unavailable, report account connection pending and retain the draft; do not present enrollment or installed contact configuration as usable email access.

For each existing managed conversation, prepare a fresh package for the new device and schedule the existing authorized membership/Welcome path. Do not copy the approving device’s live checkpoint or impersonate it. If that group’s authority or required witnesses are unavailable, show the contact/conversation wait; a separately established fresh group cannot silently inherit the old group’s continuity claim. The complete automatic discovery/admission scheduler and send-ready gate remain required implementation work.

### Evidence boundary

The [confidential setup experiment](evidence/README.md#confidential-pairing-setup) joins actual accepted remote pairing, signed endpoint-bound requests/responses, age encryption and atomic private staging/receipt. It tests revocation, expiry, cancellation, ciphertext/signature substitution, immutable retries and crash/reopen.

The separate [contact-store integration](evidence/README.md#paired-contact-store-installation) exports the reference store’s accepted public identity paths, actual scoped comparison decisions and selected policy. It validates history before per-contact pin/association/verification installation, preserves conflicting or newer local evidence, and emits `installed` only after the entire selected scope and defaults commit. Local cases exercise a configured old-device comparison, encrypted transfer, new-device verified lookup and target preparation after a subsequently received valid advertisement, with no comparison session on the new device. Onward export preserves the original comparison identity, and native storage preserves uint64 revisions exactly. These are reference-store integration results, not native OS UI, a physical human comparison test or a full mail-client implementation.

A portable authenticated own-device carrier binding and deployed account integration, production secret custody/erasure, automatic current-setup acquisition, existing-group admission/scheduling and whole send-ready acceptance remain required. Neither a staged nor installed configuration receipt establishes those outcomes.

:::

## Removal and revocation

Device removal updates the authorized target set for future sends after the sender learns and validates the update. It cannot erase content already delivered to that device. Cached or offline senders may act on older valid state; the security profile must define validity windows and acceptable stale-state behavior rather than promising instantaneous global revocation.

A revocation identifies its authority, scope and effective semantics. Revoking a device does not automatically revoke the whole correspondent identity. Revoking an identity does not automatically prove which replacement identity belongs to the same person.

Historical signatures retain their original verification evidence, but may need a changed warning when compromise information becomes available. A client must distinguish “verified when received,” “currently accepted,” and “compromise affects this attribution.” Re-evaluating evidence must not destroy the stored original or silently transfer authorship to a replacement key.

## Recovery and account reassignment

Recovery has two distinct outcomes: continuity-preserving recovery through a previously authorized mechanism, or creation of a new identity after continuity is lost. The client MUST state which occurred. Provider password reset is not automatically continuity-preserving recovery for endpoint keys.

The [encrypted archive profile](encrypted-archives.md) specifies recoverable history separately from live identity. The initial suite selects surviving-device enrollment or an explicit new identity after total device loss; it does not enable an emergency recovery override merely because a binding contains the recover role. Before enabling recoverable history, the user is told who or what can recover it and whether that authority can decrypt past messages. Recoverable archives and retained keys change the protection offered by key deletion. Recovery credentials must not be silently included in ordinary email notifications.

An email address can be reassigned. Control of the same address at a later date does not entitle its new owner to old conversation history. A new identity at that address follows the continuity-break procedure, and historical content is not automatically quoted, re-encrypted or reissued to it.

## Mailbox ownership checks

A provider's mailbox ownership check is delivery evidence, not proof of endpoint-key continuity. A successful check MUST NOT authorize identity replacement, device enrollment, history recovery or a new group member. An unknown result MUST NOT be shown as verified continuity. An ownership-change result requires reassessment of the affected delivery; it does not authorize disclosing the old conversation to the new account holder.

[RFC 7293](https://www.rfc-editor.org/rfc/rfc7293.html) supplies an optional RRVS delivery check. Its SMTP form and header tunnel have different failure and privacy properties; the header can expose recipient addresses and relationship timestamps. Neither form establishes possession of the correspondent's encryption key. Role addresses, mailing lists and forwarding also have special handling, so acceptance cannot establish the identity of every eventual reader.

Email/2 implementations MUST NOT automatically retry a failed required ownership check with that check removed. Any permitted change follows the sender's delivery policy, while continuity and history-access requirements continue to apply. The [recipient ownership audit](audits/recipient-ownership.md) records forwarding exceptions, header privacy constraints and required integration tests.

## Distributed discovery and witnesses

A provider or delegated service can publish identity material, but publication authority and endpoint authorization remain distinct. Delegation must identify the mailbox scope, service role and validity, and be authenticated under the selected discovery profile. A service change cannot silently replace the correspondent's pinned identity.

Independent witnesses may provide evidence about consistency of publication. Consistency alone does not prove that a key belongs to the intended human. The witness profile must specify its log or observation model, checkpoint freshness, disagreement handling and privacy costs before clients depend on it.

A disagreement between discovery sources is preserved as evidence. A majority vote among arbitrary servers is not a defined trust mechanism. Clients should allow continued reading and deliberate user action while holding automatic sensitive delivery whose identity authority remains unresolved.

## Acceptance cases

Required tests cover first contact under permissive and strict policies, forged advertisements, proof of possession with a wrong mailbox claim, duplicate and replayed transitions, concurrent rotations, revoked transition authorities, enrollment through a malicious provider, restricted device roles, offline revocation, lost-device recovery, account reassignment, history transfer and disagreeing witnesses.

This chapter defines the authorization decisions those tests must exercise. The [security profile](security-profile.md) and [identity-state records](identity-state.md) select candidate credential, proof and roster formats. Group consequences of accepted account changes are defined in [group conversations](group-conversations.md#applying-account-changes-to-an-mls-group). Recovery, stronger freshness services and complete cross-layer integration remain required for an interoperable profile.

## Address equivalence is not identity continuity

Preserve mailbox local-parts, including case and provider-specific delimiters, when addressing a contribution. A client MUST NOT merge pinned identities, recovery authority or conversation access merely because two addresses differ only by case, dots or a plus suffix. Provider-specific delivery equivalence requires evidence from the responsible domain; even that equivalence does not itself prove continuity of endpoint keys.

A user interface may suggest that addresses could refer to the same mailbox, but the suggestion must not silently alter the protected recipient set. Syntax validation, mailbox delivery, account ownership and cryptographic identity are separate checks. A web form's acceptance or rejection of an address does not settle any of the other checks.

## Address correction is not identity succession

SMTP forwarding information, including 251 and 551 replies, is a routing observation. It MUST NOT by itself replace a pinned participant identity, authorize a key transition, enroll a new group member or release conversation history. A client may present a suggested address correction, but any subsequent delivery must satisfy the selected disclosure policy and the new destination's applicable identity checks.

An existing authorized alias may continue to route opaque ciphertext without revealing its expansion to the sender. That routing does not establish that every eventual destination can decrypt it. A compatibility failure does not authorize decrypting and forwarding plaintext to the suggested address.

VRFY and EXPN results are diagnostic information. A successful result is not a proof of endpoint key possession; an EXPN list is not an authenticated group roster. Clients MUST NOT use these commands as a substitute for capability discovery, identity continuity or group admission. A refusal or 252 result must not be interpreted as absence of an account or absence of Email/2 support.

These distinctions follow the separation between routing and endpoint authority. The [SMTP revision](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5321bis-44/) sections 3.4–3.5 describe forwarding privacy, alias/list behavior and the limits of diagnostic expansion; the [revision audit](audits/smtp-revision.md) records its full-text review and unresolved dependencies.


## Binding protocol clients to devices

A cryptographic protocol's internal member identifier is not a stable device identity. In an MLS binding, a leaf index is meaningful only within its group epoch and may later identify another member. Implementations MUST bind operations such as device removal to the authenticated device and the relevant group state, rather than reuse a cached leaf index across epochs.

Several devices may legitimately present the same account identifier. The device authorization record must distinguish those devices without treating a repeated account address as an identity collision. Conversely, an MLS application_id value is not proof that the authentication service authorized that device: RFC9420 explicitly excludes that inference. Duplicate or conflicting application identifiers must not silently transfer authority between devices.

A new credential must be checked both against the intended correspondent identifier and, when replacing a credential, against the authorized succession rules. Possession of a new key or a syntactically valid basic credential does not establish continuity. Expiry, revocation and historical-message verification remain distinct decisions; accepting an expired credential for an authorized renewal or a historical signature must not restore its authority for unrelated new operations.

These requirements carry RFC9420 Section 5.3's application responsibilities into Email/2. Credential encoding, authentication-service binding and historical validation policy remain decisions for the complete cryptographic profile.


## Distributed authentication roles

The authentication service is a role, not a requirement for a central identity provider. RFC9750 allows its functions to be distributed among clients, credential issuers and user verification procedures. Email/2 must specify how a device establishes and checks the binding between the intended account identifier and its signing keys, regardless of which component supplies the evidence.

A provider-assisted path and a client-managed path must expose their different trust assumptions. Neither may silently treat delivery of a credential as verification of its account binding. Federation requires compatible identity and payload rules in addition to a common cryptographic protocol. A peer-to-peer delivery path still needs the ordering and recovery guarantees required by the chosen group profile.


## Disabling, deletion and restored state

Disabling automatic protected sending MUST NOT itself erase the user's local identity, historical decryption access or recovery material. The interface must distinguish that setting from a separate destructive operation that removes access to encrypted history. Disabling a local client also MUST NOT publish a device revocation unless the user selected removal or the established lifecycle policy requires it.

Restoring a backup MUST NOT roll back accepted revocations, restore a removed device to an authorized roster, or override a newer established identity merely because the backup decrypts successfully. Restored state is historical input. Before new delivery, the client must reconcile it with authenticated current state under the profile's recovery rules. If reconciliation is unavailable, it may permit local historical reading but MUST hold operations requiring unresolved current authority.

A restore interface must identify the account and device being restored and whether the operation recovers historical access, enrolls a device, or establishes a new identity. A message's apparent sender and a successful mailbox login cannot substitute for recovery authorization. These are Email/2 lifecycle requirements informed by the [Autocrypt audit](audits/autocrypt.md), not claims that Autocrypt defines this recovery protocol.


### Import history, then reconnect

The managed restore path opens old messages as **imported history** in a separate archive. It does not resume the backed-up device. Replies and other actions stay unavailable until a fresh device has current authority.

If another authorized device survives, the new device generates its own key and uses [independently confirmed pairing](#pairing-another-device). That enrollment preserves the account identity without copying the old device's private key or MLS state. Existing conversations still require authorized admission; pairing does not recover their old message keys.

If no authorized device or previously selected recovery authority remains, the available path is an explicitly new identity. The interface MUST say that continuity was not recovered. Correspondents with an existing association must explicitly accept the identity change before using it. Mailbox login, imported messages and a `recover` role without a defined recovery operation do not authorize replacing the old identity.

::: {.details summary="Managed restore boundary and experiment"}

### Separate historical reading from live authority

An import MUST NOT install source identity pins, private keys, MLS checkpoints, queued deliveries, votes or pending actions into the live account. Imported records are not newly authenticated messages and MUST NOT trigger conversation effects. The client must label their provenance and keep them separate from newly accepted traffic.

Fresh activation must check the actual enrollment receipt, exact new credential and key, and current device authority in the same local transaction. Failed or interrupted activation leaves sending unavailable. A new-identity choice requires separate explicit confirmation and must not be used to self-authorize an existing account identifier.

### Local implementation boundary

The [restore experiment](evidence/README.md#managed-archive-import-and-fresh-reconnection) imports contribution records from an explicitly selected local database into a separate history database. It preserves exact event bytes and displays inert text; it does not import attachment resources or render imported rich HTML. It reads only the expected ordinary table under read-only, query-only restrictions, rejects views and virtual tables, and applies adjustable local row, byte and time budgets.

This is a managed import path, not detection of arbitrary rollback of the entire application or machine. The [archive contract](encrypted-archives.md) now selects an encrypted portable format and a standalone container experiment; it does not add those features to this older database-import path. Neither path recovers live private keys. The separate [history-transfer contract](history-transfer.md) now binds a recipient-specific fresh archive to exact participant authority and deliberate disclosure. Its local control/import experiment is not integrated into this older restore demo. Existing transport forward-secrecy claims do not protect an accessible plaintext archive.

:::


## Associating an address with an identity

The [mailbox-association contract](mailbox-association.md) separates accepted identity evidence from the local decision to use that identity for an address. It defines ambiguous first contact, continuity breaks, alias handling and generation checks for queued operations. Its reference storage design does not provide independent ownership verification or complete transport-release integration.
