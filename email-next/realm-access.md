---
title: Discovery installation access
order: 10.18
blurb: proposed bounded discovery reference
sectionNav: true
---

# Discovery installation access

**Proposed reference binding: `mail-realm-access-v0`.** An app creates a private installation key and obtains a scoped service credential in the background. Each operation signs the actual body, destination and expiry. The service checks admission and reserves bounded work before evaluating a blinded lookup, copying a snapshot or validating a publication.

This reuses the maintained discovery-access implementation's installation possession, optional platform evidence, RFC 9421 request signatures, token hashing, durable replay reservation and uncertain-outcome rules. It defines a new grammar and routes; the old `mail-access-draft-0` and `/mail/access/query` parser do not acquire realm scopes. Installation permission is resource admission only: it cannot prove mailbox control, enroll a correspondent, grant a package or authenticate message content.

Ordinary clients can use installation-only admission with adjustable operator limits. Supported platforms may supply verified App Attest or Play Integrity evidence. This profile requires no app-bundle secret, specialized hardware, CAPTCHA, extra account or per-contact sign-in. A caller-supplied verdict cannot substitute for verified platform evidence. Installation keys/tokens and platform proof material use actual protected local custody and background recovery.

## What the person experiences

The app obtains service access in the background during account setup and renews it with its protected installation key. Adding a recipient does not open another sign-in or ask the person to manage an API key. The service can limit costly discovery work without treating application branding as a secret.

Permission is separate for each service origin and operation. It lets an installation use resources; it does not establish mailbox ownership, authorize a recipient device or prove that returned setup is trustworthy. Optional platform evidence improves abuse resistance on supported platforms. Installation-only access remains available under the operator's adjustable limits.

> [!note] Abuse protection has a privacy cost
> A service can recognize the same installation across requests and sees network addresses, timing and the public epoch. Blinded lookup does not make these requests anonymous or prevent a determined authorized querier from trying guessed addresses.

:::: {.details summary="Realm-configured issuer, scopes and policy"}

The realm configuration gains one explicit required `access` field in this new candidate schema. It is an origin-sorted array with exactly one entry for each distinct configured index/evaluator/mirror origin. Each entry has exactly these required members:

| Member | Contract |
| --- | --- |
| `service` | Exact canonical HTTPS issuer/service origin. |
| `prefix` | Canonical same-origin HTTPS path prefix. |
| `policyGeneration` | Positive canonical uint64 policy generation. |
| `apps` | Unique ID-sorted array of exact application policy objects. |
| `assurances` | ASCII-sorted unique array of the allowed assurance strings. |
| `limits` | Exact finite bound object defined below. |

service is the exact HTTPS credential issuer and operation destination. Prefix is a full canonical absolute HTTPS URL at that exact origin, ending in `/`, under the [realm prefix rules](discovery-realms.md#exact-configuration-chain); a path-only value is invalid. It must not overlap other role prefixes by segment containment. Append each logical route suffix without its displayed leading slash to preserve the selected prefix path. policyGeneration positive canonical uint64. Apps unique ID-sorted array `{id,scopes}` with public application identifier matching `[A-Za-z0-9._:/-]{1,128}` (new proposed wire bound, not a user quota) and exact ASCII-sorted allowed scope subset. Application IDs are registration labels, not secrets or evidence of genuine software.

Scopes are exactly `mail.directory.evaluate`, `mail.directory.snapshot`, `mail.directory.publish`. Evaluator origin may grant evaluate; mirrors snapshot; index publish; a co-located origin may grant their union. These are this installation issuer's resource scopes, **not** inherited native OAuth scopes. A token for another origin/realm/policy/app/key cannot be forwarded or exchanged. Access enrollment does not require a mailbox-domain change or a mailbox login. A common operator may issue its own per-origin credentials automatically, but cannot widen a peer service's scopes.

Assurances is an ASCII-sorted unique subset of apple-app-attest, google-play-integrity, installation-only and MUST include installation-only for this profile. Operator may meter these classes differently, reject abusive installations and retain actual verified class; it cannot claim unsupported platforms are counterfeit. Previously vendor-backed recovery cannot silently downgrade to installation-only after a vendor/network failure.

Limits has the following exact required members:

| Member | Contract |
| --- | --- |
| `challengeLifetimeSeconds` | Positive canonical uint64 string. Maximum challenge interval in seconds. |
| `credentialLifetimeSeconds` | Positive canonical uint64 string. Maximum credential interval in seconds. |
| `proofLifetimeSeconds` | Current supported canonical uint64 proof lifetime. |
| `windowSeconds` | Positive canonical uint64 string. Work-metering window in seconds. |
| `requestsPerWindow` | Positive canonical uint64 string. Maximum requests in the work window. |
| `evaluationsPerWindow` | Positive canonical uint64 string. Maximum blinded evaluations in the work window. |
| `snapshotBytesPerWindow` | Positive canonical uint64 string. Maximum full-snapshot response bytes in the work window. |
| `mutationBytesPerWindow` | Positive canonical uint64 string. Maximum mutation bytes in the work window. |
| `maxRows` | Positive canonical uint64 string. Maximum retained execution rows, including reserved, completed, uncertain and replay-tombstone rows. |
| `maxRequestBytes` | Positive canonical uint64 string. Maximum complete request bytes. |
| `maxResponseBytes` | Positive canonical uint64 string. Maximum complete encoded response-envelope bytes. |
| `maxStoredResponseBytes` | Positive canonical uint64 string. Maximum total retained execution-result and reservation storage bytes. |
| `maxWorkers` | Positive canonical uint64 string. Maximum concurrent admitted workers. |
| `workerDeadlineMs` | Positive canonical uint64 string. Maximum worker lifetime in milliseconds. |

All limits are positive canonical unsigned-64 strings and adjustable operator bounds. They do not define user quotas. Client applies stricter local ceilings before parsing.

`maxResponseBytes` must fit the complete encoded response envelope for the configured full snapshot. Reject unsupported geometry before serving; never stream a selected row as fallback.

`maxStoredResponseBytes` bounds all retained execution results and reservations, including uncertain work. Reserve the maximum complete response-envelope allowance before an effect; replace it with exact retained bytes only after durable completion. Retained request commitments, nonces and execution metadata also count toward this bound.

Challenges and installations have separate explicit finite operator bounds. They do not consume execution rows under `maxRows`. Operator may add finite network, IP, header or proof-work budgets under privileged deployment policy without making them hidden user requirements.

The app selects this access mapping from the authenticated current realm configuration, never from a peer or lookup response. Installation key is fresh Ed25519 and separate from email device identity; use a different per-origin/realm installation key by default to avoid unnecessary cross-origin correlation. Reuse the same retained key for renewal/recovery; key regeneration must not be used automatically to evade denial or budgets. Server still sees the requesting network address and stable installation identity at that origin.

::::

:::: {.details summary="Challenge, platform evidence and credential lifecycle"}

New outer profile is `mail-realm-access-v0`; strict value, time and unknown-field rules come from the [realm binding](discovery-realms.md). Explicit arrays and objects retain their stated types. Nonces/tokens here deliberately retain the existing access owner's **43-character unpadded base64url32-byte** spelling, not realm-record lowercase hex. PublicKey is exact canonical Ed25519 SPKI PEM as maintained OpenSSL serializes it, at most 1024 bytes under the existing prototype cap; no alternate PEM/key algorithm. Original HTTP bytes remain the signature input. These are new challenge/credential types, never parsed as the old numeric-field prototype.

| At access prefix | Exact request | Result |
| --- | --- | --- |
| POST `/challenges` | `application/octet-stream`; original strict challenge-request JSON below; no Authorization or cookie | HTTP 200 `application/octet-stream`, exactly `{profile,challenge}`; `challenge` is base64 of the original prepared payload |
| POST `/enroll` | Installation-signed original challenge bytes; `Authorization: Installation none` or the current own token; optional one `Mail-Vendor-Proof` header | HTTP 200 original credential JSON |
| POST `/operations` | Installation-signed operation envelope, current own token | HTTP 200 original result envelope, or explicit error |

The challenge-request JSON has exactly these required members:

| Member | Contract |
| --- | --- |
| `profile` | `mail-realm-access-v0` |
| `realm` | Configured realm ObjectId |
| `configurationDigest` | SHA256 of the current original configuration payload |
| `app` | Public application identifier under the selected app policy |
| `publicKey` | Exact canonical Ed25519 SPKI PEM |
| `scopes` | Nonempty selected scope array |

Prepared challenge payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `service` | Exact canonical HTTPS issuer/service origin. |
| `app` | Public application identifier under the selected app policy. |
| `publicKey` | Canonical Ed25519 SPKI PEM under the access rules. |
| `scopes` | Exact selected scope array. |
| `nonce` | Original 43-character unpadded base64url nonce. |
| `policyGeneration` | Positive canonical uint64 policy generation. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `realm-access-enrollment`. Server selects/retains original nonce/interval/generation once under finite challenge budgets; interval at most challengeLifetimeSeconds, whole current time/config policy eligible. Requested scopes must be nonempty and allowed for that app at this origin. Challenge contains no queried mailbox/hash/blinded input/contact list. Challenge service equals actual selected issuer. Client signs those exact returned payload bytes; cannot add scopes or reserialize. Server derives its own current issuer/policy, not an incoming body identity.

Enrollment signature uses the exact common HTTP components below, with created=challenge.notBefore, expires=challenge.notAfter, signature nonce=challenge.nonce. Token is literal none for first enrollment/lost-token recovery; renewal includes the exact current own token. The server validates installation possession, original retained challenge/current policy/app/scope/key/interval and optional actual platform evidence, then consumes challenge and replaces the credential atomically. Invalid proof cannot consume it.

Challenge replay after commit is spent: it does not issue another token. Its lost response remains uncertain; no false success or forced permanent lockout follows.

Credential JSON has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `service` | Exact canonical HTTPS issuer/service origin. |
| `realm` | Configured realm ObjectId. |
| `app` | Public application identifier under the selected app policy. |
| `policyGeneration` | Positive canonical uint64 policy generation. |
| `scopes` | Exact selected scope array. |
| `token` | Random 32-byte unpadded base64url credential. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |
| `proofLifetimeSeconds` | Current supported canonical uint64 proof lifetime. |
| `assurance` | Exact verified tagged assurance object. |

Token random 32 bytes base64url, stored only hashed server-side and bound to this installation key/app/realm/policy/scopes/actual assurance. Interval at most credentialLifetimeSeconds/current configuration; proofLifetimeSeconds equals supported current limit. Assurance exactly `{kind:"installation-only"}`, `{kind:"apple",appId,platform}` or `{kind:"google",package,recognition,deviceLabels,licensing}`. These values derive from actual adapters, never client choice; deviceLabels sorted unique.

A client that supplied a selected vendor proof must validate the returned credential has that actually expected assurance scope; a dropped/failed proof cannot silently become installation-only success. Raw vendor credentials/evidence/counters stay in protected owner storage, not directory setup or query headers.

Mail-Vendor-Proof is one canonical padded base64 original strict vendor submission. Tagged forms exactly `{kind:"apple",keyId,attestation}`, `{kind:"apple-assertion",assertion}` or `{kind:"google",token}`; binary object fields base64 and keyId/token retain vendor exact spelling.

Actual maintained Apple attestation/assertion or Google verified server verdict must bind **SHA256 of the exact original prepared challenge bytes** under that adapter's standard clientDataHash/requestHash encoding, including service, app, key, scopes, realm, nonce, policy and interval. Keep registered app/certificate/root/production-policy/time/counter verification and stored Apple key-to-installation exclusivity; no supplied verdict true/false. Preflight signature/challenge/budget checks run before vendor service/crypto work.

Vendor timeout is unavailable, never evidence of counterfeit or permission to reduce retained assurance. [Apple validation](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server), [Play Integrity standard requests](https://developer.android.com/google/play/integrity/standard)

Renew/recover in background with a fresh challenge for the same stored installation key and unchanged app/realm. Requested scope may equal/narrow the old scope; adding a currently allowed scope is a fresh issuance decision under current app policy, not authority inherited from old token. Previously retained assurance must continue at the same vendor app/platform/package scope; fresh appropriate evidence required for vendor recovery.

Installation-only can recover by fresh proof of the same retained key even if the committed token response was lost. Apple stored-key assertions use actual increasing counters; Google fresh verified requestHash/time/package evidence remains required. Revoked installation cannot recover merely by possession; policy-generation change invalidates old credentials. Successful replacement invalidates prior token without resetting installation-level work counters/history.

Loss of the actual installation key requires separate enabled installation setup, never silent reuse of another device's email identity key.

Client durably protects pending original challenge/request/vendor evidence before transport, and new credential before clearing pending state. Exact retry may recover an unconsumed challenge attempt; spent/uncertain enrollment moves to fresh same-key recovery within original local policy. Neither challenge nor credential renewal restarts a human send/setup deadline. Existing implementation's lost-token recovery semantics are retained, not a new requirement for user approval.

::::

:::: {.details summary="Exact signed operation and durable admission"}

All signed requests use POST, actual HTTPS authority and exact access path, application/octet-stream, no query/redirect/cookie/proxy authorization/content encoding/trailers. Exactly one Content-Digest, Authorization, Signature-Input and Signature. Content-Digest exactly RFC 9530 `sha-256=:<canonical padded base64 SHA256(actual complete body)>:`. Verify actual bytes before signature success supplies authority.

RFC 9421 label is mail, algorithm ed25519/keyid installation. Required components in this exact order are `("@method" "@authority" "@path" "content-type" "content-digest" "authorization")`; signature parameters in exact order created,expires,nonce,alg,keyid. created/expires are RFC integer seconds, not quoted JSON times, and must fit both the local unsigned-second type and RFC 9421 structured-field integer representation without truncation; nonce the 43-character base64url string.

Authorization exactly `Installation <token>` or literal Installation none for eligible enrollment only. Method/authority/path/content-type/digest/auth must all be covered; valid subset signatures fail. Scheme is fixed HTTPS and origin selected independently. Signature verifies against the actual server-retained installation public key for that hashed token, not any supplied key header. [HTTP signatures](https://www.rfc-editor.org/rfc/rfc9421.html), [digest fields](https://www.rfc-editor.org/rfc/rfc9530.html)

Operation envelope strict JSON has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `request` | Original operation ObjectId. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `scope` | Exact selected resource scope. |
| `operation` | Exact tagged operation object defined below. |

Its purpose is `realm-operation`; request ObjectId. Operation exactly `{kind,body}`, body canonical padded base64 original logical request bytes. The installed realm config maps scope/kind only to handlers at this **same actual origin**:

| kind | scope | Exact decoded body and handler result |
| --- | --- | --- |
| current | mail.directory.snapshot | empty bytes; private-profile current checkpoint JSON |
| checkpoints | mail.directory.snapshot | empty bytes; full common checkpoint-chain JSON |
| snapshot | mail.directory.snapshot | strict `{profile,epoch,checkpointDigest}`, profile mail-private-snapshot-v0; complete matching binary file |
| evaluate | mail.directory.evaluate | original private-profile evaluate JSON; its request equals envelope request; exact evaluation/proof JSON |
| mutation | mail.directory.publish | original realm `{record,bundle,evidence}`; exact index commit receipt JSON |
| association-withdrawal | mail.directory.publish | original realm safety-withdrawal JSON; exact safety commit receipt JSON |

No caller URL/method/prefix/account callback selects a handler. Realm/configuration scope must match the current selected role mapping and original inner epoch/publication authorizations. The access credential supplies no additional enrollment truth or native identity role. The outer configurationDigest must match the currently selected realm role/access mapping; an old still-signed inner publication can retain its own historical configurationDigest under the publication owner.

A configuration conflict triggers authenticated account-global configuration recovery, never an in-place rewrite of the original inner proof. Config bootstrap GET remains public/account-global before admission so no circular token acquisition arises. The direct role routes in the [realm](discovery-realms.md) and [private snapshot](private-snapshot.md) chapters define these logical request/result semantics; **deployed profile does not also expose them anonymously**. Their anonymous direct HTTP form is comparative/local-test mode only, never the advertised default.

### Formatted operation example

The decoded body of a `snapshot` operation has this shape. These example values identify no deployed realm or authentic checkpoint. The request uses the complete body bytes, base64 encoded, inside `operation.body`; a sender must not substitute a selected-row URL.

```json
{
  "profile": "mail-private-snapshot-v0",
  "epoch": "1",
  "checkpointDigest": "abababababababababababababababababababababababababababababababab"
}
```

For `current` and `checkpoints`, `operation.body` is the empty base64 string `""`. For `evaluate`, it contains the complete original evaluate JSON. The inner request ID must equal the outer operation request ID. These examples do not supply installation signatures or authorize any work.

Result envelope original JSON has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `request` | Original operation ObjectId. |
| `requestDigest` | SHA256 of the original complete operation envelope. |
| `scope` | Exact selected resource scope. |
| `status` | Exact three-digit logical status string. |
| `contentType` | Exact logical media type. |
| `result` | Complete original logical result bytes, base64 encoded. |

requestDigest hashes original complete operation-envelope bytes; status a canonical three-digit string of logical 200/201 or one of the explicit logical handler errors400/403/404/409/413/415/429/503, contentType application/json or application/octet-stream matching handler, result base64 exact complete logical result bytes. A logical handler error has contentType application/json and result the exact original `{error}` JSON; it is a retained completed observation, never a successful publication/proof or evidence encryption unsupported.

Outer response 200 application/octet-stream; each child signature/proof/file hash is still independently checked. Snapshot decoded bytes are the same entire file for every target. Account credentials/enrollment contain no selected recipient; evaluate contains blinded input only. Publication bodies intentionally reveal the publisher's own address to the index.

At a request, first enforce transport/body/worker ceilings, then actual digest/signature/current credential/app/realm/scope/policy/time and complete allowed operation. Require the entire credible current interval inside notBefore inclusive/notAfter exclusive for credential/proof, expires>created, proof span <= proofLifetimeSeconds and expires <= credential.notAfter. The selected current configuration and actual worker deadline also bound the attempt.

The signed `expires` is the server-visible attempt deadline. There is no extra deadline member in an empty `current`/`checkpoints` body or in the defined snapshot/evaluation request. The client keeps the original human setup/send deadline in protected local attempt state and chooses `expires` no later than that deadline. A server cannot enforce a client-local deadline it has not received.

For `snapshot` and `evaluate`, the selected original checkpoint/context interval additionally bounds resource use and final disclosure. Mutation and association-withdrawal handlers enforce the original signed inner record's interval and authorization under their owning contracts. None of these bounds can be refreshed by polling, token renewal or exact retry; changing signed expiry creates a different authenticated request commitment. A new permitted attempt still retains the original client-local deadline.

Under owning database lock recheck current authority and credible clock; reserve per-installation/origin/realm/scope rate/evaluation/snapshot-byte/mutation-byte counters plus sufficient response-storage/work budget **before** expensive VOPRF/full snapshot copy/native publication validation.

A bounded logical handler rejection is represented as a completed LogicalRealmResult, while actual worker/storage/transport failure after reservation remains uncertain; do not misclassify an index409 or missing snapshot404 as a successful effect or automatically rerunnable reservation. Counters are shared across token renewal, cursors/connections and retries; fresh installation key creation is not Sybil immunity.

Bounded server worker custody/monotonic deadline remains live through actual effect, not released merely because an HTTP caller timed out.

Execution namespace retains existing `(credential hash, signature nonce)` reservation semantics. Request commitment is SHA256 of ASCII `mail/realm/access/request/v0`, NUL, U32BE RFC 9421 signature-base byte length, those exact base bytes, U32BE decoded signature length,64 signature bytes. Actual body digest was independently checked, so this binds actual operation/issuer/path/token/scopes/body/expiry. Equal nonce+commitment recovers retained completed exact response only under fresh current credential/policy/time checks.

Unequal authenticated same nonce409. Invalid signature cannot occupy it. Reserve durably before invoking the handler, then retain exact completed response before returning; crash/handler failure/cancellation after reservation leaves uncertain and never automatically reruns that nonce. No response is claimed before actual persistence.

Before completion/cached disclosure/response egress, recheck credible time, original proof/credential/config/scope and worker ownership. If expiry/revocation/cancellation became effective, stop new disclosure; preserve reserved/result history/uncertainty. A database lock does not stop wall time advancing. An uncertain old read/evaluation may be replaced only by a separately authorized new readonly operation/nonce within the original local deadline/rate policy, retaining old uncertainty and using a valid complete current context.

It is not automatic rerun of a reserved effect. Mutation retries retain exact original signed inner record; its own index CAS/idempotency prevents duplicate publication even if token recovery needs a new outer request. No old response or extra nonce extends setup/message deadlines or says encryption unsupported.

Admission/transport errors use outer400 invalid,401 unauthorized expired/revoked token/proof,403 unauthorized scope/app policy,409 conflict or uncertain,413 tooLarge,415 unsupportedRepresentation,429 rateLimited positive Retry-After,503 unavailable. Exact JSON body `{error}` with error uncertain for reserved-without-complete409; other values as realm grammar. Errors echo no tokens/body/recipient. Local currentness/auth failure does not return old cached data; lost errors still preserve uncertainty.

Rate/storage exhaustion happens before new effect, never evicts valid replay/tombstone obligations. TLS/service/network authorization remains distinct from signed subject truth.

::::

## Implementation boundary and privacy limit

Implementations need distinct challenge, credential and operation types for this profile, with separate route/signature selection. Existing access challenge types and route checks remain unchanged. Shared installation-signature and vendor-verification primitives may be reused only while preserving these exact transcript and authority boundaries.

A sealed `AuthorizedRealmOperation` receipt is created solely by actual successful current token/signature/scope/budget/replay transaction; private constructor binds origin/realm/config/policy/install/scopes/request digest/nonce/interval/worker custody. Handler cannot fabricate it from app ID, API key or ready flag. New vendor adapter entrypoints accept the actual retained RealmAccessChallenge transcript and produce actual sealed verified evidence; they do not serialize a fake old Challenge to borrow its verdict.

An older execution callback with a single body-size bound does not supply the scopes, separate request/response/storage budgets or final-time gate selected here. Implementations must enforce these fields before advertising this binding. Full snapshot envelope storage is explicitly accounted; no unbounded per-nonce duplicate file cache is assumed.

A service sees stable per-origin installation/key/token policy, IP, operations/timing and public epoch even while VOPRF hides recipient input. Reusing one installation for several queries links them; an app ID is copyable and installation-only admission is not genuine-binary proof. Vendor evidence and work budgets improve abuse resistance without user ceremony, but do not prevent determined enumeration or all Sybil identities. OHTTP/Privacy Pass/unlinkable credentials are not claimed or silently selected. This admission binding does not establish production scalability or combined-compromise protection.
