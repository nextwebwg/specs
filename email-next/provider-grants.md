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

> [!note] Proposed public grant profile
> `email2-provider-grants-v0` defines account/device linking and issuance for the existing `en-provider-control-0` pair queue. The identifiers and scope strings are draft names. The [discovery profile](provider-discovery.md) supplies domain delegation, native registration and browser authorization. This contract assumes the peer devices are already identified; the [first-contact flow](first-contact-setup.md) needs a separately versioned unknown-peer bootstrap binding before it can create this permission automatically. Local approval/credential validation is not a deployed OAuth or grant service.

## Connect the account and its device

The person connects their own account through the selected provider origin and the native authorization flow. The provider derives its internal account and active grant family from the management access token. An incoming address, client identifier, device signature or request body cannot select that account.

The person selects one of that account's provider-authorized mailbox spellings under the [canonical address contract](mailbox-addresses.md). The service checks that membership; it does not infer aliases through plus-tag removal or case folding. The client approves linking its selected Email/2 principal/device to that account. A signed challenge binds this decision to the exact mailbox, account incarnation, delegation, OAuth family and device evidence.

Linking requires the device's current `receive` authority. This is narrow control-service authority, matching discovery; it cannot enroll or revoke a device, authorize application-message sending, or disclose encrypted history. The service validates the identity bundle and its own accepted identity state. The client independently checks its current state again before signing.

Account login does not silently replace an account's previously linked principal. A different principal requires an explicit account-reset operation with visible continuity-break consent. That operation rotates the opaque service account incarnation and revokes its links, queue grants, credentials and pending preparations. Correspondents retain their own identity anchors; an account reset does not repin them. Mailbox reassignment/reprovisioning performs the same queue-authority invalidation.

A new OAuth family can link another currently authorized device of the same principal. An ordinary identity-head advance preserves a link only under the unchanged-binding checks below. Relinking to a different binding requires fresh exact proof and cannot change the principal. It cannot enroll a device merely because the person signed in. A link belongs to one account incarnation, OAuth family and exact device binding; refresh-token rotation within the same family preserves it. Family withdrawal, absolute expiry, identity conflict or known loss of its required device authority blocks new grants and credentials.

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

## Issue separate credentials

Each participant requests a challenge for one exact role. The service freezes that challenge and the device signs it using the approved binding key. A successful completion produces a random opaque bearer credential, bound to this grant, role, origin, prefix, operations and expiry. Role configuration is derived from the immutable grant; a request cannot choose extra operations.

The initiator does not sign in to the target's account. Its possession proof and the target's prior approval authorize this narrowly scoped issuance. The target uses the same proof mechanism for its own queue role. Neither receives the other's token. Queue tokens never authorize management APIs, and management tokens never authorize queue operations.

Signing for issuance is not per-request sender constraint. A stolen queue token can exercise its limited role until expiry or revocation. The queue still requires its normal signed records, and clients still validate current endpoint authority. No full OAuth security or sender-constraint claim follows from this credential mechanism.

::: {.details summary="HTTP routes, authorization and exact record conventions"}

All management routes are suffixes under the discovered `managementPrefix`; queue routes stay under `controlPrefix`. Use the existing canonical HTTPS/path grammar, TLS 1.3, no redirects, no 0-RTT, no ambient credentials and no compressed bodies. Strict UTF-8 JSON rejects duplicate decoded names. Maximum management body is 4194304 octets, signed payload 262144 octets and container depth 32; each supplied identity bundle independently obeys its own tighter bounds. A local smaller processing budget returns an explicit unsupported/resource outcome without changing protocol state. Errors never echo submitted records or tokens. Responses use no-store.

Management Bearer credentials require the exact discovered issuer, service audience, client, active family, account incarnation and operation scope. `email2.provider.link` permits link creation and own-account link/reset/disconnect operations; `email2.provider.manage` permits grant preparation, completion and revocation. Neither scope authorizes another account. Reset and revoke are account-authority operations and remain possible without possession of a lost device key. Account-reset consent is separate from ordinary OAuth scope consent.

| Route | Authorization and result |
| --- | --- |
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

The provider UI requires fresh account authentication, matches the same authenticated account and current incarnation, shows the continuity break and queue revocation, and records explicit CSRF-protected confirmation. Its server-held approval is bound to this exact preparation, nonce, family, incarnation and expiry and is single-use. No incoming JSON boolean can assert completed authentication or consent. Completion PUT has no body, authenticates the original family, atomically consumes that approval and rotates the incarnation while revoking all old families/links/grants. A failed or expired confirmation leaves the incarnation unchanged. The authentication factor itself remains the provider's login boundary. An uncertain completion disables old local grants and requires reconnecting to inspect the current account incarnation; it cannot reuse the now-revoked family or infer failure from401.

`POST` requests carry caller-generated nonzero ObjectId `request` for exact retry. Namespace is account/family/route/request for authenticated management calls and grant/role/device/request for credential challenges. Persist exact request bytes, challenge and original result before reply. Same namespace with different authenticated content returns409; invalid signatures or unauthenticated submissions cannot create an authoritative conflict. Replaying a challenge request never extends its interval or allocates a second grant/token. No supplied URL is contacted.

GET is not selected for these routes; unsupported methods return405 with Allow. POST/PUT JSON bodies require application/json, DELETE and reset-completion PUT have no body. Error bodies are exactly `{error}`:400 invalid,401 unauthorized,403 unauthorized for insufficient scope,404 notFound,409 conflict,413 tooLarge,415 unsupportedRepresentation,429 rateLimited,503 unavailable. Bearer challenges follow the configured queue's RFC6750 rules. Missing/expired/unknown grant or invalid public credential proof has the same404 result, after bounded signature checks; there is no public account or grant listing. A public challenge may still reveal possession of a valid invitation ID; it reveals no new grant data beyond that invitation and no device online status.

Services configure finite authentication, signature-work, body/header, active link/preparation/challenge, new-token, per-account, per-device, per-source and deployment budgets, plus positive maximum challenge/token/grant/family lifetimes and retry retention. These are explicit deployment policy, not invented user quotas. A prepared challenge states the selected interval before approval. Exhaustion yields429 and positive Retry-After seconds, never token scope expansion, early replay-record eviction or another account's data. Clients use bounded backoff and no automatic replacement of uncertain operations.

Signatures use Ed25519 over the kind-specific ASCII domain below, NUL, u32 big-endian original payload byte length, then those exact payload bytes. Wrappers are exactly `{payload,signature}`: canonical padded base64 payload and128 lowercase hexadecimal signature characters. Payloads deliberately use safe JSON integer times and existing queue configuration integers, unlike string-only application events. Missing/unknown members and null are rejected unless expressly permitted below. Keys/digests/account/grant/family IDs are64 lowercase hexadecimal characters; devices/principals use the existing enp0/end0 grammars; ObjectIds are nonzero32 lowercase hexadecimal. An endpoint reference is exactly `{principal,device,state,binding,key}`. Record identifiers and nonces use cryptographically random bytes. The complete credible clock interval must fit every applicable validity interval; unavailable time holds new effects.

:::

::: {.details summary="Account-link and pair-approval records"}

### Account linking

The link challenge request is exactly `{profile,request,delegationDigest,mailbox,device}`. Profile is `email2-provider-grants-v0`; delegationDigest is SHA256 of the retained original domain record; mailbox uses the selected exact supported spelling; device is the endpoint reference. The service validates the current delegation and mailbox against the authenticated account before returning a challenge.

The retained challenge payload is exactly:

```
{profile,purpose,challenge,request,nonce,delegationDigest,service,
 account,family,mailbox,device,notBefore,notAfter}
```

Purpose is `provider-account-link`; challenge/request are ObjectIds; nonce is64hex; service is the exact discovered origin; account is the provider's opaque incarnation, not a JMAP identifier; family is an opaque binding to the authenticated OAuth family, not a token. Its interval lies inside family and device-binding authority. Signature domain: `email2/provider-account-link/v0`.

Completion body is exactly `{proof,identity}`, containing that wrapper and the identity bundle for the device's principal. Compare payload against the exact retained challenge, authenticate the same family/account, verify signature and current accepted head/binding/receive authority, and consume the challenge atomically with the new link. Validate self-consistent genesis under an explicit unverified first-observation policy where appropriate; do not call it independent identity verification. A failed new-principal link leaves no partial pin. Valid known-principal safety observations may remain even if linking is held.

The result is exactly `{profile,purpose,challenge,requestDigest,link,account,mailbox,device,notBefore,notAfter}`; purpose `provider-account-linked`, link ObjectId, requestDigest SHA256 of original challenge bytes, remaining values match the challenge. The result is TLS-authenticated state, not transferable provider evidence of mailbox ownership. Exact authorized retries return it after challenge expiry, but cannot reactivate a withdrawn link or family. Same-account repeat linking uses a new challenge only after explicit disconnect of the old family link; it cannot silently switch principals or keys.

### Pair approval

Preparation request is exactly `{profile,request,link,initiator,target,notBefore,notAfter,limits,initiatorIdentity,targetIdentity}`. Participants are endpoint references; target equals the active family link's device. Both identities and their current receive authority are validated, then retained as staged input until approval. Limits has exactly the fields of the configured queue contract; no omitted defaults. The service can reject unsupported limits but must not silently replace them.

The prepared payload is exactly:

```
{profile,purpose,preparation,request,nonce,delegationDigest,link,family,
 mailbox,configuration,initiatorKey,targetKey,notBefore,notAfter}
```

Purpose is `provider-pair-approval`; preparation/request/link are ObjectIds; nonce is64hex. Configuration is the complete existing queue configuration with `role:"target"` and its exact target operation array. Its service/prefix/account equal the current delegated control service and linked account. Device/state/binding fields equal the staged endpoint references. Key fields are the approved Ed25519 keys. The outer interval is approval validity and lies within the configuration interval and both binding/family/link lifetimes. Signature domain: `email2/provider-pair-approval/v0`.

The client checks all configuration fields and local disclosure/peer policy before signing. Completion body is exactly `{proof}`. Under one write transaction, authenticate the same account/family/link, compare the original retained prepared bytes, verify target signature, check both current accepted states/bindings/receive authority and all intervals, then activate that immutable grant and consume preparation. A known state change holds it; new configuration requires a new preparation/grant. Do not install previously untrusted staged identity anchors until valid approval and link authorization; safety observations for already known principals retain their own rules.

Result is exactly `{profile,purpose,preparation,approvalDigest,configuration}`, purpose `provider-pair-approved`; approvalDigest is SHA256 of original approval payload bytes and configuration is identical. Exact valid retries return the recorded result without creating another grant. Revocation is checked before any retry response and remains effective.

A transferable invitation is exactly `{profile,purpose,approval,targetIdentity}`, purpose `provider-pair-invitation`; approval is the target-signed prepared wrapper, targetIdentity its bundle. The initiator checks its locally selected participant and expected target mailbox/service, validates the approval and both current states independently, and directly retrieves a credential from the exact approved management service. The invitation by itself does not prove activation; credential issuance checks the active server record. No OAuth management credential, queue credential or private key is included.

:::

## Credentials and revocation

::: {.details summary="Credential proof, renewal and terminal lifecycle"}

The public credential-challenge body is exactly `{proof}`. Its signed payload is exactly `{profile,purpose,request,approvalDigest,grant,service,prefix,role,device,notBefore,notAfter}`; purpose is `provider-role-request`, and its signature domain is `email2/provider-role-request/v0`. Role is exactly initiator or target; device is the corresponding endpoint reference from the retained grant, not a new key. Grant/service/prefix equal the route and immutable grant. The current interval fits the grant, link/family and device binding, under the service's bounded request-lifetime policy. The server validates the exact request signature with the frozen role key before allocating a challenge or authoritative collision record. Random request IDs or a copied public invitation do not authorize allocation. Apply transport/source budgets before cryptography and separate authenticated role budgets afterward. A hostile authenticated role must not consume the other role's reserved challenge capacity; transport-wide exhaustion can still make the service unavailable. No unconditional availability guarantee is implied. A credential challenge never consumes an MLS package or publishes presence.

The returned retained payload is exactly:

```
{profile,purpose,credential,request,nonce,approvalDigest,grant,account,
 service,prefix,role,device,notBefore,notAfter}
```

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

The [relay module](relay-routes.md#discover-a-relay-service) reuses account-link possession/challenge mechanics under its own delegated namespace and OAuth scopes. Its source permissions and recipient routes are defined there, not by queue approval. Queue link/grant credentials cannot allocate aliases, change From or originate mail.
