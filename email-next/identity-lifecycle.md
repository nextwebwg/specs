---
title: Identity continuity and device lifecycle
order: 9
blurb: first contact · key changes · recovery · devices
sectionNav: true
---

# Identity continuity and device lifecycle

Automatic encryption must work without requiring people to administer keys for every conversation. It must also distinguish a newly observed key from an established correspondent. This chapter defines proposed authorization behavior. The [security profile](security-profile.md) supplies device-binding records and proof constructions; [identity-state records](identity-state.md) define the roster and ordinary transitions. Integrated validation, freshness and recovery remain unfinished.

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

## Removal and revocation

Device removal updates the authorized target set for future sends after the sender learns and validates the update. It cannot erase content already delivered to that device. Cached or offline senders may act on older valid state; the security profile must define validity windows and acceptable stale-state behavior rather than promising instantaneous global revocation.

A revocation identifies its authority, scope and effective semantics. Revoking a device does not automatically revoke the whole correspondent identity. Revoking an identity does not automatically prove which replacement identity belongs to the same person.

Historical signatures retain their original verification evidence, but may need a changed warning when compromise information becomes available. A client must distinguish “verified when received,” “currently accepted,” and “compromise affects this attribution.” Re-evaluating evidence must not destroy the stored original or silently transfer authorship to a replacement key.

## Recovery and account reassignment

Recovery has two distinct outcomes: continuity-preserving recovery through a previously authorized mechanism, or creation of a new identity after continuity is lost. The client MUST state which occurred. Provider password reset is not automatically continuity-preserving recovery for endpoint keys.

Before enabling recoverable history, the user is told who or what can recover it and whether that authority can decrypt past messages. Recoverable archives and retained keys change the protection offered by key deletion. Recovery credentials must not be silently included in ordinary email notifications.

An email address can be reassigned. Control of the same address at a later date does not entitle its new owner to old conversation history. A new identity at that address follows the continuity-break procedure, and historical content is not automatically quoted, re-encrypted or reissued to it.

## Mailbox ownership checks

A provider's mailbox ownership check is delivery evidence, not proof of endpoint-key continuity. A successful check MUST NOT authorize identity replacement, device enrollment, history recovery or a new group member. An unknown result MUST NOT be shown as verified continuity. An ownership-change result requires reassessment of the affected delivery; it does not authorize disclosing the old conversation to the new account holder.

[RFC 7293](https://www.rfc-editor.org/rfc/rfc7293.html) supplies an optional RRVS delivery check. Its SMTP form and header tunnel have different failure and privacy properties; the header can expose recipient addresses and relationship timestamps. Neither form establishes possession of the correspondent's encryption key. Role addresses, mailing lists and forwarding also have special handling, so acceptance cannot establish the identity of every eventual reader.

Email Next implementations MUST NOT automatically retry a failed required ownership check with that check removed. Any permitted change follows the sender's delivery policy, while continuity and history-access requirements continue to apply. The [recipient ownership audit](audits/recipient-ownership.md) records forwarding exceptions, header privacy constraints and required integration tests.

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

VRFY and EXPN results are diagnostic information. A successful result is not a proof of endpoint key possession; an EXPN list is not an authenticated group roster. Clients MUST NOT use these commands as a substitute for capability discovery, identity continuity or group admission. A refusal or 252 result must not be interpreted as absence of an account or absence of Email Next support.

These distinctions follow the separation between routing and endpoint authority. The [SMTP revision](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5321bis-44/) sections 3.4–3.5 describe forwarding privacy, alias/list behavior and the limits of diagnostic expansion; the [revision audit](audits/smtp-revision.md) records its full-text review and unresolved dependencies.


## Binding protocol clients to devices

A cryptographic protocol's internal member identifier is not a stable device identity. In an MLS binding, a leaf index is meaningful only within its group epoch and may later identify another member. Implementations MUST bind operations such as device removal to the authenticated device and the relevant group state, rather than reuse a cached leaf index across epochs.

Several devices may legitimately present the same account identifier. The device authorization record must distinguish those devices without treating a repeated account address as an identity collision. Conversely, an MLS application_id value is not proof that the authentication service authorized that device: RFC9420 explicitly excludes that inference. Duplicate or conflicting application identifiers must not silently transfer authority between devices.

A new credential must be checked both against the intended correspondent identifier and, when replacing a credential, against the authorized succession rules. Possession of a new key or a syntactically valid basic credential does not establish continuity. Expiry, revocation and historical-message verification remain distinct decisions; accepting an expired credential for an authorized renewal or a historical signature must not restore its authority for unrelated new operations.

These requirements carry RFC9420 Section 5.3's application responsibilities into Email Next. Credential encoding, authentication-service binding and historical validation policy remain decisions for the complete cryptographic profile.


## Distributed authentication roles

The authentication service is a role, not a requirement for a central identity provider. RFC9750 allows its functions to be distributed among clients, credential issuers and user verification procedures. Email Next must specify how a device establishes and checks the binding between the intended account identifier and its signing keys, regardless of which component supplies the evidence.

A provider-assisted path and a client-managed path must expose their different trust assumptions. Neither may silently treat delivery of a credential as verification of its account binding. Federation requires compatible identity and payload rules in addition to a common cryptographic protocol. A peer-to-peer delivery path still needs the ordering and recovery guarantees required by the chosen group profile.


## Disabling, deletion and restored state

Disabling automatic protected sending MUST NOT itself erase the user's local identity, historical decryption access or recovery material. The interface must distinguish that setting from a separate destructive operation that removes access to encrypted history. Disabling a local client also MUST NOT publish a device revocation unless the user selected removal or the established lifecycle policy requires it.

Restoring a backup MUST NOT roll back accepted revocations, restore a removed device to an authorized roster, or override a newer established identity merely because the backup decrypts successfully. Restored state is historical input. Before new delivery, the client must reconcile it with authenticated current state under the profile's recovery rules. If reconciliation is unavailable, it may permit local historical reading but MUST hold operations requiring unresolved current authority.

A restore interface must identify the account and device being restored and whether the operation recovers historical access, enrolls a device, or establishes a new identity. A message's apparent sender and a successful mailbox login cannot substitute for recovery authorization. These are Email Next lifecycle requirements informed by the [Autocrypt audit](audits/autocrypt.md), not claims that Autocrypt defines this recovery protocol.


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

This is a managed import path, not detection of arbitrary rollback of the entire application or machine. It does not select an encrypted backup format, recover private keys, or transfer protected history between devices. Those require separate confidentiality and disclosure contracts. Existing transport forward-secrecy claims do not protect an accessible plaintext archive.

:::


## Associating an address with an identity

The [mailbox-association contract](mailbox-association.md) separates accepted identity evidence from the local decision to use that identity for an address. It defines ambiguous first contact, continuity breaks, alias handling and generation checks for queued operations. Its reference storage design does not provide independent ownership verification or complete transport-release integration.
