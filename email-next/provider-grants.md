---
title: Authorizing a provider exchange
order: 10.27
blurb: account linking · pair grants · device-bound issuance · revocation
sectionNav: true
---

# Authorizing a provider exchange

A provider account can authorize a queue without becoming the authority for a person's encryption identity. The client first connects the account, proves possession of an authorized device key, then approves one exact pair of devices. Each device obtains its own queue credential by signing a fresh provider challenge. Credentials are never placed in email or sent through another provider.

> [!ex] Permission to ask, not permission to answer
> Bob authorizes Alice's selected device to request fresh setup through his service. Alice proves possession of that device's key to obtain an initiator credential. Bob obtains a different target credential. Alice's credential can place and read the exchange; it cannot answer on Bob's behalf, list his other grants or manage his account.

> [!note] Retained version0 grant profile
> `email2-provider-grants-v0` defines account/device linking and issuance for the existing `en-provider-control-0` pair queue. The identifiers and scope strings are draft names. The [discovery profile](provider-discovery.md) supplies domain delegation, native registration and browser authorization. This contract assumes the peer devices are already identified; the [first-contact flow](first-contact-setup.md) uses its own [bootstrap authority](bootstrap.md) before a known-pair permission can be selected. That binding is defined; its complete joined implementation remains unproven. Local approval/credential validation is not a deployed OAuth or grant service.

The [current Encryption baseline](suite-profile.md#current-client-baseline) uses [provider grants2](#authorize-asynchronous-pair-exchanges) when this capability is offered. Retained version0/1 records remain exact. Changing profile does not reset account/family blocks, revocation, replay, budgets or package allocation; these bindings do not establish a complete implementation.

## Connect the account and its device

The person connects their own account through the selected provider origin and the native authorization flow. The provider derives its internal account and active grant family from the management access token. An incoming address, client identifier, device signature or request body cannot select that account.

The person selects one of that account's provider-authorized mailbox spellings under the [canonical address contract](mailbox-addresses.md). The service checks that membership; it does not infer aliases through plus-tag removal or case folding. The client approves linking its selected Email/2 principal/device to that account. A signed challenge binds this decision to the exact mailbox, account incarnation, delegation, OAuth family and device evidence.

Linking requires the device's current `receive` authority. This is narrow control-service authority, matching discovery; it cannot enroll or revoke a device, authorize application-message sending, or disclose encrypted history. The service validates the identity bundle and its own accepted identity state. The client independently checks its current state again before signing.

Account login does not silently replace an account's previously linked principal. A different principal requires an explicit account-reset operation with visible consent to clearing that service-account link; any new principal remains a separate endpoint-identity decision. That operation rotates the opaque service account incarnation and revokes its links, queue grants, credentials and pending preparations. Correspondents retain their own identity anchors; an account reset does not repin them. Mailbox reassignment/reprovisioning performs the same queue-authority invalidation.

A new OAuth family can link another currently authorized device of the same principal. An ordinary identity-head advance preserves a link only under the unchanged-binding checks below. Relinking to a different binding requires fresh exact proof and cannot change the principal. It cannot enroll a device merely because the person signed in. A link belongs to one account incarnation, OAuth family and exact device binding; refresh-token rotation within the same family preserves it. Family withdrawal, absolute expiry, identity conflict or known loss of its required device authority blocks new grants and credentials.

## Shared account links, separate module authority

Provider control, relay accounts and automatic setup use the same account-link record format. A link still belongs to one selected module and authenticated account. Reusing a proof format does not share permissions, account resets or contact identity.

| Module | Required link scope | Descriptor bound by the proof | Meaning of `mailbox` |
| --- | --- | --- | --- |
| Provider control | `mail.provider.link` | Provider-service descriptor for that selected mailbox domain | A mailbox the provider authorizes for the authenticated account |
| Relay | `mail.relay.link` | The deliberately selected relay-service descriptor | An account-contact mailbox selected from that relay account's authorized contact records; not proof of control by its domain |
| Automatic setup | `mail.setup.link` | Bootstrap-service descriptor for that selected mailbox domain | A mailbox the provider authorizes for the authenticated sending or receiving account |

> [!ex] A relay account is not a mailbox provider
> Bob connects an account at `relay.example` with `bob@personal.example` as its account contact. The relay can link that account to Bob's device. This does not let it publish encryption setup on behalf of `personal.example` or verify Bob's personal address to his correspondents.

:::: {.details summary="Exact shared records, module lookup and reset boundaries"}

### Reuse the account-link subset only

All three modules reuse the account-link and reset operation shapes, but select their exact signed branch from the authenticated connection:

| Selected connection | Link/reset record profile | Account-link signature domain |
| --- | --- | --- |
| Retained provider queue, descriptor1 | mail-provider-grants-v1 | mail/provider-account-link/v1 |
| Selected asynchronous queue, descriptor2 | mail-provider-grants-v2 | mail/provider-account-link/v2 |
| Earlier provider queue, descriptor0 | email2-provider-grants-v0 | email2/provider-account-link/v0 |
| Relay, under its relay descriptor | email2-provider-grants-v0 | email2/provider-account-link/v0 |
| Automatic setup, including bootstrap descriptor0/1/2 | email2-provider-grants-v0 | email2/provider-account-link/v0 |

The [queue successor binding](#reply-aware-account-and-pair-permissions) owns its exact version1 substitution. The relay/setup subset deliberately retains its original version0 profile and signature domain; the generic descriptor digest can bind their actual selected descriptor without a schema rewrite. Select one branch before decoding. Do not infer a module or grant profile from a signature that happened to verify, an OAuth scope string alone, or a callback path.

For the relay/setup subset and earlier provider queue, the shared `profile` remains `email2-provider-grants-v0`; the challenge purpose remains `provider-account-link`, its signature domain remains `email2/provider-account-link/v0`, and its result purpose remains `provider-account-linked`. The reset purpose remains `provider-account-reset`. No field, signature prefix or callback path is derived by substituting a module name. The subset retains this chapter’s safe JSON integer timestamp grammar. It does not adopt the string timestamps of relay/bootstrap-specific records. Select the schema from the authenticated module and exact operation route; never choose it by trying another parser after failure.

Reuse only `/account`, `/links/challenges`, `/links/challenges/{challenge}`, `/links/{link}`, `/account-reset/preparations` and `/account-reset/preparations/{preparation}` under that module's accepted management prefix, with the inherited methods and errors. Queue pair/grant/role-credential routes are not inherited. Relay and bootstrap operations remain owned by their own chapters. Apply the [native module binding](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions) before any link operation.

The module is trusted local/API authorization context, not another unsigned body field. Resolve it from the selected connection and authenticated module-bound management grant. Keep module, service, authenticated internal account/incarnation, family, link/challenge/request identifiers and accepted descriptor in the local lookup namespace. Even if IDs or management-prefix strings coincide, a token, link or preparation cannot cross modules. An arbitrary request header, JSON member or callback cannot choose another namespace.

### Check the mailbox under the correct authority

For provider control and automatic setup, the selected `mailbox` domain must have its own accepted delegation to the selected service. An alias in another domain needs that domain's delegation too. Account membership, exact address spelling and module policy remain separate mandatory checks.

For an independent relay, the selected discovery domain identifies the relay account/service. The inherited `mailbox` field is private account-contact metadata, in the same canonical address grammar; the service must derive its allowed value from the authenticated account rather than an arbitrary request claim. It may be in another domain. Do not discover that contact domain automatically, treat the relay as its delegate, install a correspondent association from this link, or use it as authenticated personal From/To. Actual source mailbox authority, protected address evidence and inbox-provider route issuance retain their own rules. Receiving-service association during normal account connection is distinct from per-alias approval; current routes require no such device approval. The internal account/incarnation is still the account key; the contact address cannot select another account.

### Complete, retry or reset the selected link

Compare the original challenge bytes and every module/account/family/descriptor dependency before signing or accepting completion. Validate the device's own current receive authority and required policy; further sending, enrollment and historical disclosure need their separately required roles. Changing the signature or claimed module cannot replace a missing account grant. Consume the challenge and install the scoped link atomically with the owning current-authority checks. An exact retained retry returns only its original result and cannot reactivate withdrawn authority.

A link deletion or reset affects that module's own account incarnation, families, links and derived permissions. Provider control revokes its queue grants/credentials; relay resets revoke its receiving-service authorizations/source permissions/routes/queued unreleased intents; setup resets revoke its source permissions, publications and pending disclosure work. Keep original reservations, abuse handles, uncertain deliveries and history under their owning retention rules. Revocation cannot recall already disclosed material.

The selected module's reset cannot reset another module, replace an endpoint principal or erase correspondence. A service-wide account security action or actual account reassignment may invalidate several modules through the operator's separately authorized account policy; an ordinary module-link proof does not authorize that wider action. Correspondents retain their pins, and reconnecting must obtain fresh appropriately scoped account/device proof.

The [shared-link component](evidence/README.md#shared-account-link-proof) checks real signatures and configured retained account/descriptor/module dependencies. It supplies no OAuth authentication, contact-membership service, first-contact pin installation, atomic challenge journal or full state1 service implementation.

::::

## Reset a connection, not the encryption identity

A service reset clears the selected module's account links and permissions. It does not revoke devices in the person's Email/2 identity, replace a correspondent's saved identity or restore access to old encrypted conversations. If a person later connects a different principal, clients still apply the normal identity-change rules.

The confirmation must name the selected service/module and explain its actual consequence: queue permissions and credentials, relay permissions/routes and unreleased work, or setup permissions/publications and pending disclosure work. Shared proof formats do not make a reset apply to all three modules. A wider account-security action needs the service's separately authorized account policy.

If the result is lost, the client stops using the old local permissions and checks the retained reset outcome after fresh sign-in. It does not guess that the reset failed, restore old credentials from backup or reset again automatically. The [inspection procedure](#inspect-a-reset-after-reconnecting) preserves the original attempt and distinguishes a historical completed reset from the account's current state.

## Approve one pair

The target device requests a prepared grant naming one initiating device and itself, their exact identity states, keys, requested interval and all queue limits. The service returns the complete proposed queue configuration. The target checks and approves those exact bytes before anything becomes an active grant. A remembered local contact policy may authorize this approval; the service cannot manufacture that policy from mail.

The granted interval must fit both devices' binding lifetimes, the account link and the absolute management-family authorization. The target's approval freezes the queue account, origin, prefix, device pair, state/binding digests, keys and limits. Changing those frozen values requires a new grant identifier. An unrelated accepted head advance does not change the frozen values: reuse follows the unchanged-binding checks below. The old proof is never rewritten to name the newer head.

The target can give the peer the resulting signed approval as a **public invitation**. It contains keys and queue identifiers, not a bearer credential. Forwarding it cannot give another device either participant's permission. A client accepts it only for its exact selected peer and device, under current discovery/association policy; it independently verifies the target's signature, current authority and expected provider/domain binding. The invitation cannot install an OAuth issuer or trigger sign-in.

## Retain an unchanged device binding

For account links, pair grants and their role credentials, the signed endpoint state is an authorization anchor, not a requirement that the account never change. The service MUST perform these checks under the same authority snapshot as each new effect:

1. Resolve the principal's current locally accepted state. Missing evidence or an unresolved conflict holds the operation. Apply the selected verification policy; ancestry does not upgrade an unverified identity.
2. Require the endpoint's exact device, binding digest, signing key and required role to remain currently authorized for the whole credible time interval. Known revocation immediately prevents new use.
3. Follow only locally accepted predecessors from that current state to the original signed anchor. At every state, including the anchor, require the same device and binding digest, the same signing key and the required role, with no revocation. Merely finding an old digest somewhere in a supplied bundle is insufficient. Missing history, a cycle or exhausted local traversal budget holds use; none authorizes repinning.
4. Keep the original signatures, endpoint references, grant identifiers, scope, approval and absolute intervals. Recheck current account incarnation, link, OAuth family, delegation, grant and token authority independently. An accepted state update cannot extend any of them.

The [relay contract](relay-routes.md) uses the same check for its retained endpoint permissions. Historical transfer authorization also checks unchanged accepted ancestry. This rule does not rebase a pending enrollment, change an MLS GroupContext or membership checkpoint, turn an expired package into a fresh one, reset a challenge timer or prove recent/live device presence. Those operations retain their own explicit state and freshness rules.

## Continuity and freshness have different scopes

Adding another device or publishing an unchanged-roster checkpoint does not change an existing device's own key or permissions. The client can keep using that device's still-valid setup after verifying the accepted history. This continuity is not evidence that the device recently answered a request.

::: {.details summary="Purpose-specific state anchors, renewal and invalidation"}

The unchanged-binding algorithm above is also the current suite's default for retained endpoint authorization. Always resolve original signed references and the current accepted state separately in one authorization snapshot. The following table defines where an old anchor may remain usable; it does not rewrite older experimental wire contracts.

| Purpose | Required treatment |
| --- | --- |
| Current assertion10 and retained assertion8/9 for cached discovery or new setup | The exact original binding/key/receive role must survive at every accepted state from the original anchor through the current head. Assertion, package, control-key and local policy deadlines remain unchanged. Full package/association validation and single-use rules still apply. |
| Bootstrap source preparation or offline publication | Apply the same unchanged-binding test, plus the exact retained account incarnation/link/family, source/target, opt-in, package allocation and original attempt/publication interval. A refreshed local slot may name a newer accepted head for the same exact device/binding/key; compare the original publication through its own accepted anchor, never rewrite it. It remains offline setup, not a live response. |
| Recent-checkpoint policy | Read the original signed bytes and issuance time of the **current accepted head**, independently of the advertisement's older anchor. Recompute the result after an advance. A convenient historical timestamp or arrival time cannot replace it. |
| Live bootstrap response | Require the exact current target head, binding and key together with the original locally outstanding challenge, nonce, service, operation, policy and age bound. An older target-head response cannot be promoted to live after a head advance even when cached support survives. The frozen bootstrap source may retain unchanged-binding authorization without refreshing its timer. |
| Known-pair live challenge | Keep that protocol's exact requested target state. A target-head change needs independently accepted evidence and a new authorized challenge; when the configured grant freezes that target state, prepare and approve a new exact pair grant/configuration as well. Remembered eligible contact policy may authorize this preparation, but the old queue/grant cannot be edited. Retained outcome retrieval is not a new live proof. Do not substitute the cached-discovery exception. |
| Late sealed-control receipt | The original signed sender anchor must be accepted. The same device/key/required role must survive every intervening state. A binding renewal may retain authority only through overlapping or touching validity intervals with no key, role or revocation gap. Original signature/body creation bounds are checked against the original binding; current authority is checked at receipt. The original recipient/control-key promise and all owning deadlines still apply. This is not renewal of a grant or a new sending right. |
| Account links, pair grants, route endpoint permissions and new history disclosures | Keep the exact unchanged binding under their existing contracts. A changed binding needs a new appropriate authorization; same-key renewal cannot extend an old grant's absolute deadline. |
| QR enrollment, identity-state transitions, fixed MLS context or managed ordering proof | Preserve the exact predecessor/context dependencies. Ancestry cannot rebase an approved enrollment, merge a fork, change a roster or invent another accepted Commit. |

An original anchor must actually contain that exact device/binding; a key added later cannot borrow an older account state. Resolve each step from independently retained accepted records, not from a claim that a supplied bundle has a larger revision. Unknown ancestry, missing records, accepted conflicts, key change, known revocation or loss of the required role holds use. Local processing budgets may hold a traversal; they never authorize skipping it. All original signatures and record identities remain immutable. Verification assurance does not increase through a state advance.

Current cached discovery deliberately preserves only the **exact binding**, not every same-key renewal. Replacing the binding therefore invalidates old assertion10/9/8 material for new setup, even when the signing key is unchanged. Publish freshly signed setup under the replacement binding. A state advance that only adds another device or changes unrelated state is not feature withdrawal. To invalidate this device's published setup early through identity authority, revoke it or replace its binding with an authorized transition; withdraw provider pool entries separately and stop local custody under its explicit withdrawal rules. No instant global withdrawal is promised to peers that have not learned those changes. A valid advertisement with fewer optional features does not revoke another still-valid assertion, and timeout never authorizes downgrade. Standalone feature-only withdrawals are not inferred from absent mail or a later timestamp.

A [state1 repair](identity-state.md#concurrent-administration-and-retirement) is a fresh-authorization boundary for all earlier endpoint links, grants and route permissions. Reprove appropriately scoped current authority from the repaired head; the one-parent unchanged-binding algorithm cannot skip a repair parent or carry the old grant across it. This does not rotate the account incarnation or independently verified identity. Retirement terminates new operational authority.

At every final release/installation boundary, resolve and recheck the current accepted heads and dependencies again. An advance invalidates the earlier authorization **result**, not necessarily its original unchanged-binding evidence. Retain the old evidence and compute a new result; do not transfer a cached ready flag to the newer state. Changes to authority, policy, mailbox association or required freshness may still hold the operation. None of these rules grants automatic history access, new reply recipients or a different delivery policy.

:::

## Issue separate credentials

Each participant requests a challenge for one exact role. The service freezes that challenge and the device signs it using the approved binding key. A successful completion produces a random opaque bearer credential, bound to this grant, role, origin, prefix, operations and expiry. Role configuration is derived from the immutable grant; a request cannot choose extra operations.

The initiator does not sign in to the target's account. Its possession proof and the target's prior approval authorize this narrowly scoped issuance. The target uses the same proof mechanism for its own queue role. Neither receives the other's token. Queue tokens never authorize management APIs, and management tokens never authorize queue operations.

Signing for issuance is not per-request sender constraint. A stolen queue token can exercise its limited role until expiry or revocation. The queue still requires its normal signed records, and clients still validate current endpoint authority. No full OAuth security or sender-constraint claim follows from this credential mechanism.

::: {.details summary="HTTP routes, authorization and exact record conventions"}

All management routes are suffixes under the discovered `managementPrefix`; queue routes stay under `controlPrefix`. Use the existing canonical HTTPS/path grammar, TLS 1.3, no redirects, no 0-RTT, no ambient credentials and no compressed bodies. Strict UTF-8 JSON rejects duplicate decoded names. Maximum management body is 4194304 octets, signed payload 262144 octets and container depth 32; each supplied identity bundle independently obeys its own tighter bounds. A local smaller processing budget returns an explicit unsupported/resource outcome without changing protocol state. Errors never echo submitted records or tokens. Responses use no-store.

Management Bearer credentials require the exact discovered issuer, service audience, client, active family, account incarnation and operation scope. `mail.provider.link` permits link creation and own-account link/reset/disconnect operations; `mail.provider.manage` permits grant preparation, completion and revocation. Neither scope authorizes another account. Reset and revoke are account-authority operations and remain possible without possession of a lost device key. Account-reset consent is separate from ordinary OAuth scope consent.

| Route | Authorization and result |
| --- | --- |
| GET /account | Link scope;200 current account-incarnation observation |
| GET /account-reset/preparations/{preparation} | Link scope;200 retained outcome for this owner and module |
| POST /links/challenges | Management link scope; exact request below, returns200 retained challenge |
| PUT /links/challenges/{challenge} | Same management family and device proof; returns201 new link,200 identical retained retry |
| DELETE /links/{link} | Same account incarnation, link scope;204 after disabling that link and all grants derived from it |
| POST /account-reset/preparations | Link scope; creates one exact reset preparation and same-origin confirmation view |
| PUT /account-reset/preparations/{preparation} | Same family, link scope and server-retained fresh account-UI approval;204 after atomic incarnation rotation and revocation |
| POST /grants/preparations | Active linked target and manage scope; returns200 exact prepared approval payload |
| PUT /grants/preparations/{preparation} | Same family/link and target proof;201 new grant,200 identical retained retry |
| DELETE /grants/{grant} | Same account incarnation, manage scope;204 after grant/credential revocation |
| DELETE /grants | Same account incarnation, manage scope;204 after revoking all queue grants in that account |
| POST /grants/{grant}/credentials/challenges | No management token; signed role request, returns200 retained challenge for that approved device |
| PUT /grants/{grant}/credentials/{credential} | Device proof over exact retained challenge, no management token;201 new credential,200 identical retained retry |

Deletion of an unknown link/grant under the authenticated account returns the same204 result. It cannot address another incarnation's namespace. Link/reset deletion does not delete identity evidence or correspondence.

Reset preparation body is exactly `{profile,request}`, with request ObjectId. Its200 response is exactly `{profile,purpose,preparation,account,family,nonce,confirmation,notBefore,notAfter}`: purpose `provider-account-reset`, preparation ObjectId, nonce64hex, account/family are the authenticated bindings, and confirmation is a canonical same-origin HTTPS endpoint for the provider's browser UI, without credentials in its URL. Interval is bounded by the family and the service's finite reset-preparation policy. The client opens that view only after a local reset request, retaining the exact preparation and original endpoint binding. Normal provider-browser login cookies are confined to that separate UI, never attached to the management API. Opening the view performs no reset.

The service UI requires fresh account authentication, matches the same authenticated account and current incarnation, identifies the selected module and the exact scope of link/permission revocation described above, and records explicit CSRF-protected confirmation. It explains that any later different linked principal has no inherited endpoint continuity; resetting this service account does not itself replace or retire an Email/2 identity. For the queue branch, the affected permissions are its queue grants/credentials; the inherited relay/setup branches show their own affected routes/permissions/publications instead. Its server-held approval is bound to this exact preparation, nonce, family, incarnation and expiry and is single-use. No incoming JSON boolean can assert completed authentication or consent. Completion PUT has no body, authenticates the original family, atomically consumes that approval and rotates the incarnation while revoking all old families/links/grants. A failed or expired confirmation leaves the incarnation unchanged. The authentication factor itself remains the provider's login boundary. An uncertain completion immediately disables old local grants. Reconnect through fresh native authorization and inspect the account and original reset preparation as defined below. Do not reuse the old family, infer failure from401, or automatically submit another reset.

### Inspect a reset after reconnecting

A lost reset response leaves the result uncertain. Fresh sign-in lets the client check the original attempt without resetting again. These reads never reactivate old credentials or authorize a new identity link.

`GET /account` returns exactly the following fields. The response describes the selected module’s account at the read transaction; it is not signed identity evidence.

| Field | Required value |
| --- | --- |
| `profile` | `email2-provider-grants-v0` |
| `purpose` | `provider-account-state` |
| `account` | Current account incarnation, 64 lowercase hexadecimal characters |
| `family` | The authenticated current OAuth family, 64 lowercase hexadecimal characters |
| `principal` | Current linked principal in the existing nonzero `enp0:` grammar, or the empty string when unlinked |

`GET /account-reset/preparations/{preparation}` returns exactly this record:

| Field | Required value |
| --- | --- |
| `profile` | `email2-provider-grants-v0` |
| `purpose` | `provider-account-reset-state` |
| `preparation` | The original preparation ObjectId, equal to the route |
| `outcome` | Exactly `pending`, `completed` or `expired` |
| `account` | For `completed`, the immutable resulting incarnation; otherwise the original preparation’s incarnation. 64 lowercase hexadecimal characters |

A fresh family may inspect an earlier preparation only for the same selected module and continuing internal account owner. The service retains an internal owner-generation binding across that owner’s deliberate resets. Account reassignment or reprovisioning creates a new owner generation, even if an internal account ID or mailbox spelling is reused. Tokens and contact addresses cannot choose this binding. A later owner cannot read the earlier owner’s reset outcomes.

| Outcome | Meaning |
| --- | --- |
| `pending` | The original preparation remains eligible for completion under its original family, approval and deadline. This read does not authorize the fresh family to complete it. |
| `completed` | That exact attempt committed. The recorded resulting incarnation remains unchanged even after another reset. |
| `expired` | That attempt did not commit and can no longer commit, including expiry, original-family withdrawal or an incompatible incarnation change. |

Read the preparation and its eligibility under the same transaction boundary as reset completion. Completion must atomically retain its `completed` result with the incarnation rotation and revocations, before replying. It cannot later become `pending` or `expired`. Once `expired` is observed, that attempt cannot commit later. Apply the existing replay-retention window; do not evict a live preparation or its result early to admit new work.

Unknown, foreign-owner and garbage-collected preparation identifiers have the same 404 result. A404, network failure or unavailable record is **not evidence that the reset failed**. Preserve the original attempt and its uncertainty. Retain a known completed result locally; later absence cannot erase it. A different resulting incarnation for that same completed preparation is a conflict: hold affected operations for reconciliation.

The current-account response and retained reset result are separate observations, not one atomic snapshot. Another authorized action may change the account between them. A completed result for an older incarnation does not install that incarnation as current. Reconnect and perform fresh account/device linking under the current incarnation before new operations. Neither observation changes correspondent identity pins, restores an old queue or repeats a destructive action.

`POST` requests carry caller-generated nonzero ObjectId `request` for exact retry. Namespace is account/family/route/request for authenticated management calls and grant/role/device/request for credential challenges. Persist exact request bytes, challenge and original result before reply. Same namespace with different authenticated content returns409; invalid signatures or unauthenticated submissions cannot create an authoritative conflict. Replaying a challenge request never extends its interval or allocates a second grant/token. No supplied URL is contacted.

Only the two listed inspection routes support GET. They require no request body or query and return application/json with no-store; all other GETs and unsupported methods return405 with Allow. POST/PUT JSON bodies require application/json, DELETE and reset-completion PUT have no body. Error bodies are exactly `{error}`:400 invalid,401 unauthorized,403 unauthorized for insufficient scope,404 notFound,409 conflict,413 tooLarge,415 unsupportedRepresentation,429 rateLimited,503 unavailable. Bearer challenges follow the configured queue's RFC6750 rules. Missing/expired/unknown grant or invalid public credential proof has the same404 result, after bounded signature checks; there is no public account or grant listing. A public challenge may still reveal possession of a valid invitation ID; it reveals no new grant data beyond that invitation and no device online status.

Services configure finite authentication, signature-work, body/header, active link/preparation/challenge, new-token, per-account, per-device, per-source and deployment budgets, plus positive maximum challenge/token/grant/family lifetimes and retry retention. These are explicit deployment policy, not invented user quotas. A prepared challenge states the selected interval before approval. Exhaustion yields429 and positive Retry-After seconds, never token scope expansion, early replay-record eviction or another account's data. Clients use bounded backoff and no automatic replacement of uncertain operations.

Signatures use Ed25519 over the kind-specific ASCII domain below, NUL, u32 big-endian original payload byte length, then those exact payload bytes. Wrappers are exactly `{payload,signature}`: canonical padded base64 payload and128 lowercase hexadecimal signature characters. Payloads deliberately use safe JSON integer times and existing queue configuration integers, unlike string-only application events. Missing/unknown members and null are rejected unless expressly permitted below. Keys/digests/account/grant/family IDs are64 lowercase hexadecimal characters; devices/principals use the existing enp0/end0 grammars; ObjectIds are nonzero32 lowercase hexadecimal. An endpoint reference is exactly `{principal,device,state,binding,key}`. Record identifiers and nonces use cryptographically random bytes. The complete credible clock interval must fit every applicable validity interval; unavailable time holds new effects.

:::

::: {.details summary="Account-link and pair-approval records"}

### Account linking

The link challenge request is exactly `{profile,request,delegationDigest,mailbox,device}`. Profile is `email2-provider-grants-v0`; delegationDigest is SHA256 of the retained original domain record; mailbox uses the selected exact supported spelling; device is the endpoint reference. The service validates the current delegation and mailbox against the authenticated account before returning a challenge.

The retained challenge payload is exactly:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `purpose` | The exact purpose specified below. |
| `challenge` | The account-link challenge ObjectId. |
| `request` | The caller’s request ObjectId. |
| `nonce` | The random challenge nonce, under the exact grammar below. |
| `delegationDigest` | SHA256 of the retained original domain-delegation record. |
| `service` | The exact selected service origin. |
| `account` | The configured provider account identifier; its owning account grammar applies. |
| `family` | An opaque binding to the authenticated OAuth family; never a token. |
| `mailbox` | The exact mailbox spelling authorized for the account. |
| `device` | The selected device endpoint reference. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |

Purpose is `provider-account-link`; challenge/request are ObjectIds; nonce is64hex; service is the exact discovered origin; account is the provider's opaque incarnation, not a JMAP identifier; family is an opaque binding to the authenticated OAuth family, not a token.

Its interval lies inside family and device-binding authority. Signature domain: `email2/provider-account-link/v0`.

Completion body is exactly `{proof,identity}`, containing that wrapper and the identity bundle for the device's principal. Compare payload against the exact retained challenge, authenticate the same family/account, verify signature and current accepted head/binding/receive authority, and consume the challenge atomically with the new link. Validate self-consistent genesis under an explicit unverified first-observation policy where appropriate; do not call it independent identity verification. A failed new-principal link leaves no partial pin. Valid known-principal safety observations may remain even if linking is held.

The result is exactly `{profile,purpose,challenge,requestDigest,link,account,mailbox,device,notBefore,notAfter}`; purpose `provider-account-linked`, link ObjectId, requestDigest SHA256 of original challenge bytes, remaining values match the challenge. The result is TLS-authenticated state, not transferable provider evidence of mailbox ownership. Exact authorized retries return it after challenge expiry, but cannot reactivate a withdrawn link or family. Same-account repeat linking uses a new challenge only after explicit disconnect of the old family link; it cannot silently switch principals or keys.

### Pair approval

Preparation request is exactly `{profile,request,link,initiator,target,notBefore,notAfter,limits,initiatorIdentity,targetIdentity}`. Participants are endpoint references; target equals the active family link's device. Both identities and their current receive authority are validated, then retained as staged input until approval. Limits has exactly the fields of the configured queue contract; no omitted defaults. The service can reject unsupported limits but must not silently replace them.

The prepared payload is exactly:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `purpose` | The exact purpose specified below. |
| `preparation` | The pair-approval preparation ObjectId. |
| `request` | The caller’s request ObjectId. |
| `nonce` | The random challenge nonce, under the exact grammar below. |
| `delegationDigest` | SHA256 of the retained original domain-delegation record. |
| `link` | The current account/device link ObjectId. |
| `family` | An opaque binding to the authenticated OAuth family; never a token. |
| `mailbox` | The exact mailbox spelling authorized for the account. |
| `configuration` | The complete immutable queue configuration. |
| `initiatorKey` | The approved initiator Ed25519 key. |
| `targetKey` | The approved target Ed25519 key. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |

Purpose is `provider-pair-approval`; preparation/request/link are ObjectIds; nonce is64hex. Configuration is the complete existing queue configuration with `role:"target"` and its exact target operation array. Its service/prefix/account equal the current delegated control service and linked account. Device/state/binding fields equal the staged endpoint references. Key fields are the approved Ed25519 keys.

The outer interval is approval validity and lies within the configuration interval and both binding/family/link lifetimes. Signature domain: `email2/provider-pair-approval/v0`.

The client checks all configuration fields and local disclosure/peer policy before signing.

Completion body is exactly `{proof}`. Under one write transaction, authenticate the same account/family/link, compare the original retained prepared bytes, verify target signature, check both current accepted states/bindings/receive authority and all intervals, then activate that immutable grant and consume preparation. A known state change holds it; new configuration requires a new preparation/grant. Do not install previously untrusted staged identity anchors until valid approval and link authorization; safety observations for already known principals retain their own rules.

Result is exactly `{profile,purpose,preparation,approvalDigest,configuration}`, purpose `provider-pair-approved`; approvalDigest is SHA256 of original approval payload bytes and configuration is identical. Exact valid retries return the recorded result without creating another grant. Revocation is checked before any retry response and remains effective.

A transferable invitation is exactly `{profile,purpose,approval,targetIdentity}`, purpose `provider-pair-invitation`; approval is the target-signed prepared wrapper, targetIdentity its bundle. The initiator checks its locally selected participant and expected target mailbox/service, validates the approval and both current states independently, and directly retrieves a credential from the exact approved management service. The invitation by itself does not prove activation; credential issuance checks the active server record. No OAuth management credential, queue credential or private key is included.

:::

## Credentials and revocation

::: {.details summary="Credential proof, renewal and terminal lifecycle"}

The public credential-challenge body is exactly `{proof}`. Its signed payload is exactly `{profile,purpose,request,approvalDigest,grant,service,prefix,role,device,notBefore,notAfter}`; purpose is `provider-role-request`, and its signature domain is `email2/provider-role-request/v0`. Role is exactly initiator or target; device is the corresponding endpoint reference from the retained grant, not a new key. Grant/service/prefix equal the route and immutable grant. The current interval fits the grant, link/family and device binding, under the service's bounded request-lifetime policy. The server validates the exact request signature with the frozen role key before allocating a challenge or authoritative collision record. Random request IDs or a copied public invitation do not authorize allocation. Apply transport/source budgets before cryptography and separate authenticated role budgets afterward. A hostile authenticated role must not consume the other role's reserved challenge capacity; transport-wide exhaustion can still make the service unavailable. No unconditional availability guarantee is implied. A credential challenge never consumes an MLS package or publishes presence.

The returned retained payload is exactly:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `purpose` | The exact purpose specified below. |
| `credential` | The credential identifier under the exact grammar below. |
| `request` | The caller’s request ObjectId. |
| `nonce` | The random challenge nonce, under the exact grammar below. |
| `approvalDigest` | SHA256 of the original pair-approval payload bytes. |
| `grant` | The immutable pair-grant identifier. |
| `account` | The configured provider account identifier; its owning account grammar applies. |
| `service` | The exact selected service origin. |
| `prefix` | The canonical configured control-service prefix. |
| `role` | The exact configured participant role. |
| `device` | The selected device endpoint reference. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |

Purpose is `provider-role-credential`; credential is a fresh64hex ID, request ObjectId, nonce64hex. Service/prefix/account/grant equal the immutable queue configuration. Device is the selected role's frozen endpoint reference. The interval is the issued credential's interval, contains the full current clock interval and is contained in the signed role-request interval, grant, owning link/family and selected device binding. Services select a bounded short lifetime under their published account policy; no implicit refresh or grace period. Signature domain: `email2/provider-role-credential/v0`.

Completion is exactly `{proof}`; route credential ID equals the retained payload. Verify possession with the frozen role key, unchanged exact challenge, original caller request, interval and current known authority. Both participants' frozen heads/bindings, active account/link/family/grant and revocation are rechecked under the issuance transaction. Mint32 cryptographically random token bytes encoded as unpadded base64url. Atomically retain challenge consumption, credential scope, token hash, secret retry response and result. Protect the retry token at rest with the service's secret storage; the hash alone cannot return an identical lost response.

The exact response is `{profile,purpose,credential,tokenType,accessToken,notBefore,notAfter,configuration}`: purpose `provider-role-issued`, tokenType exactly `Bearer`, credential/interval match the challenge, accessToken is the opaque token above. Configuration derives from the immutable queue record with only role and exact role-operation array selected. Initiator cannot obtain target operations. Nothing in a request or HTTP challenge may widen it.

Retain exact signed completion bytes before PUT. Exact still-authorized retry returns the same token/result while its credential interval remains usable, not a newly minted one. An expired retained response is inspectable in secret service storage but is not returned for new use: return409 and acquire a fresh bounded challenge if policy still permits. Lost-response recovery before expiry requires no new private keys or packages. There are no queue refresh tokens. Renewal is a new signed challenge/credential in the same active grant; old credentials remain valid only until their expiry unless explicitly revoked with the grant. Clients preserve pending queue bytes across renewal.

At every queue operation the service resolves the token to its immutable account/grant/role/configuration, checks expiry and active link/family/grant/incarnation, then uses the existing queue validator/store. A periodically copied static token dictionary is insufficient: revocation checks and queue mutation must serialize against the same authoritative state or a fail-closed authorization lease that revocation invalidates before completion. A token snapshot taken earlier cannot authorize mutation after revocation wins that order. Already completed network delivery cannot be recalled.

Grant deletion, link deletion, management-family withdrawal/refresh-token reuse, account reset/reassignment and known incompatible identity changes invalidate all derived credentials and reject subsequent reads as well as writes. No device-key proof is needed to exercise the account owner's separate revocation authority. Revocation is not device removal or erasure of already retrieved evidence. A new OAuth login cannot restore an old queue grant; issue a new grant after explicit linking/approval.

Retain immutable challenges, approval/results and collision tombstones until the later of their validity/derived grant expiry plus the selected retention interval; admission capacity must cover that window. Exact retries after restart preserve identifiers, bytes and tokens. Garbage collection cannot reopen an identifier with expired signed times. On a known store restore or lost replay journal, disable affected grants before serving writes and reissue new grants after reconciliation; do not interpret restored absence as permission to recreate old effects. Whole-machine undetected rollback is outside this local persistence guarantee and must not be described as prevented.

:::

## Evidence and required integration

The [pair approval experiment](evidence/README.md#public-provider-pair-approval) validates real signatures and accepted device authority, exact approval/configuration binding, separate role derivation and credential-proof correlation. It does not implement OAuth account linking, grant activation, credential minting, an HTTP server or revocation serialization with the queue. Trusted retained link/challenge records are test inputs, not incoming network authority.

Public acceptance must join native discovery/registration/sign-in, account linking, pair approval, distinct credential issuance, actual queue operations, renewal, lost replies and atomic revocation. Test a forwarded invitation, changed peer/state/key, wrong OAuth account/family/audience, concurrent issuance/deletion, management-token theft boundaries, refresh reuse, mailbox reassignment, service migration and restored stores. Then use returned valid device admission material in protected delivery. A configured token fixture or isolated proof test cannot establish that complete path.

## Relay account links remain separately scoped

The [relay module](relay-routes.md#discover-the-selected-service) reuses account-link possession/challenge mechanics under its own delegated namespace and OAuth scopes. Its source permissions and recipient routes are defined there, not by queue approval. Queue link/grant credentials cannot allocate aliases, change From or originate mail.


## Reply-aware account and pair permissions

A queue permission for an earlier setup format cannot be silently upgraded. The recipient approves a fresh exact pair configuration, and each device obtains only its own role credential. The user's account and revocations remain the same account authority across these protocol versions.

::: {.details summary="Exact public grant1 subset and proof domains"}

The successor public queue profile is `mail-provider-grants-v1`, selected by [provider descriptor1](provider-discovery.md#reply-aware-queue-discovery). It uses the complete public grant0 request, challenge, completion, result, reset, pair-preparation/approval/invitation and role-credential member inventories, routes, safe integer time grammar and lifecycle, with the profile literal replaced by this new one wherever that schema has a profile field. No new optional member or timestamp representation is inferred. Embedded queue configurations must be complete [mail-provider-control-v1](provider-control.md#reply-aware-known-pair-exchanges) configurations, including required agreement `"mail-conversation-v1"`.

Account-link signatures use `mail/provider-account-link/v1`; pair approvals use `mail/provider-pair-approval/v1`; role requests use `mail/provider-role-request/v1`; role credential proofs use `mail/provider-role-credential/v1`. Framing remains NUL, U32 big-endian original payload length and exact original bytes. Purposes and independently checked account/family/link/peer/state/key/nonce/descriptor/approval/configuration commitments remain unchanged. Reset preparations/completion retain their existing owner authentication and original bounded confirmation secrets; changing profile cannot recreate a consumed operation or enlarge permission.

Account-link challenge/request proof binds the exact descriptor1 digest. Pair approval signs the original complete successor configuration, participant keys, current links/family and original interval. The sender validates that same approval, actual recipient mailbox/service and expected participant before obtaining its separate role credential. Token requests and credential challenges cannot change the approved profile, agreement, account, peers, state or role. Fresh grant IDs, original byte retention and role separation remain required. An old queue token cannot be accepted against a different new grant/configuration.

All versions share the authoritative queue module's account/family/incarnation, reset/link and revocation boundary. A queue-account reset disables eligible old and new queue grants under that account; it is not a separate profile-specific account. Storage and conflict/replay records preserve existing account/family/request and grant/role/device/request namespaces. The protocol label cannot clear a block, reset a budget, make a stale restore writable or turn a previously uncertain result into absence. Actual current grant authorization and queue mutation serialize against the same state or owning fail-closed lease.

The relay/bootstrap shared account-link/reset subset remains its existing literal grant0 subset and domains under the correct module namespace. A bootstrap descriptor1 can be bound by that existing generic descriptor-digest field without changing the subset schema. This queue grant1 profile does not migrate those modules, widen their scopes or make one module's reset affect another. They retain their separate service/account/device authority.

No declaration here supplies OAuth login, account membership or automatic consent. New pair preparation may use an independently remembered eligible local policy; exact currently authorized approval is still required. Full descriptor1/native login, account linking, new pair approval, role issuance, queue exchange1, serialized revocation and first-message handoff must be tested together before public support is advertised.

:::


## Authorize asynchronous pair exchanges

An asynchronous queue uses a fresh exact pair permission. Account ownership, device approval and revocations remain the same authority across queue versions; a version change cannot restore a revoked account or widen either participant's role.

::: {.details summary="Exact grant2 substitution and shared account authority"}

The profile is `mail-provider-grants-v2`, selected by [provider descriptor2](provider-discovery.md#discover-the-asynchronous-agreement). Every grant1 request, challenge, completion, result, reset, pair-preparation/approval/invitation and role-credential schema keeps its exact inventory and types, replacing the profile literal wherever that schema has a profile. Embedded configurations must be complete [mail-provider-control-v2](provider-control.md#obtain-asynchronous-device-evidence) records with required agreement mail-conversation-v2. No extension bag, optional agreement or changed timestamp grammar is admitted.

| Signed purpose | Signature domain |
| --- | --- |
| Account-link proof | `mail/provider-account-link/v2` |
| Pair approval | `mail/provider-pair-approval/v2` |
| Role request | `mail/provider-role-request/v2` |
| Role-credential proof | `mail/provider-role-credential/v2` |

Keep the existing NUL/U32-length/original-byte framing and purpose/account/family/link/device/key/nonce/interval checks. Account-link proof binds the exact descriptor2 digest. Pair approval signs the complete original control2 configuration and current participant evidence. Validate the same bytes, expected target mailbox/service and actual approved role before issuing a credential. Fresh IDs and role-separated operations remain required; changing a profile string cannot activate an old approval or token.

An already accepted active queue account/family/device link may support a new grant2 preparation when the exact service, mailbox/account, device/binding and current family authority remain eligible. Its original link proof keeps its original profile, descriptor digest and bytes; it is not replayed or relabeled as a new link proof. Independently revalidate the current delegation and owning accepted account state. A protocol upgrade alone does not require unlinking a healthy family. A missing link needs its actual new profile2 link procedure; changed origin, account, family, device or revoked authority follows the existing reconnect/reset/enrollment rules. No unsolicited old proof can create this accepted state or bypass a current link hold.

Grant0/1/2 share the queue module's authoritative account, family/incarnation, reset/link, request/conflict and revocation state. Reset/unlink/family retirement serialize against old and new queue operations together. They do not acquire new namespaces or fresh budgets from a protocol label. A consumed or uncertain request remains so, including after restore. A freshly authorized grant can follow an independently eligible remembered approval policy, but no service can invent consent or replace the exact approved configuration.

Relay and automatic-setup account links keep their separately selected shared-link subset and module-local lookup/reset authority. A bootstrap descriptor2 digest fits that existing generic digest field without changing the subset's literal profile or proof domains. Grant2 neither migrates those modules nor adds scopes. The [connection table](#shared-account-links-separate-module-authority) distinguishes the selected queue profile from those shared subsets.

:::
