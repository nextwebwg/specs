---
title: Connecting a service account
order: 3.6
sectionNav: true
---

# Connecting a service account

A service button needs two permissions: permission to act as an Email/2 principal, and permission to act on the service account. Signing in supplies the second. A fresh device proof links the two without treating an email address or OAuth subject as an Email/2 identity.

> [!ex] Connect once, answer later
> Bob connects his booking account through his email client's trusted service setup. He signs in through the system browser and approves linking his selected Email/2 principal. Later, an accepted “Reserve a seat?” question can use that grant when Bob presses its button. Receiving or opening the question does not start sign-in, link an account or submit an answer.

This is an experimental native-client authorization profile for a service whose authorization server and resource server share an authoritative grant store. It selects authorization code with S256 PKCE and opaque bearer tokens. The [service-answer contract](service-answers.md) still defines actions, exact submissions and receipts. The profile does not supply a general identity provider, infer mailbox ownership or claim complete OAuth-server conformance.

## Trust the service before opening sign-in

The client obtains a service registration through trusted installation or explicit local setup. A message, redirect or action descriptor cannot install it. Registration fixes the issuer, endpoints, client identifier and scopes. A changed registration invalidates pending authorization and link attempts; it does not erase an uncertain service submission.

The native client uses an external system browser. It binds an available literal IPv4 or IPv6 loopback listener before opening the authorization URL, trying the other family if necessary. The selected callback uses the exact registered host/path form and an ephemeral port. Its exact URI is retained with the attempt. The client does not use an embedded login view, a mailbox password or a static public-client secret.

The selected issuer is a canonical HTTPS origin equal to the service origin. That is this profile's restriction, not the general issuer grammar. Every success or error callback must contain the expected `iss` and state after form decoding. Their values are compared exactly; neither selects a token endpoint. This issuer-response defense distinguishes authorization servers even where clients use the same callback path. A client must not maintain ambiguous registrations for the same issuer/client without an explicit local selection.

## Link the signed-in account

The service derives the account from its authoritative grant store. The client never supplies an account ID, OAuth subject or email claim as the mapping authority.

After sign-in, the client asks for a short-lived link challenge for the selected principal and device. The service binds it to that authenticated account, client and grant family. The client checks the challenge against its trusted registration and current identity state, then signs the exact bytes with a device currently authorized to send. Linking is a deliberate trusted-client action; remembered authorization can govern later answers.

The service verifies the proof and commits challenge consumption, the principal mapping and its receipt together. A valid first observation establishes unverified key continuity, not verified human identity. Known newer identity state or a conflict can hold linking; an undisclosed remote revocation is not discoverable from a signature alone.

A successful link does not create an action, expand its choices or grant access to another account. Each service action independently authorizes the linked principal. The grant-family mapping cannot silently change to a different principal. Unlinking invalidates that family; a new link needs account authorization again.

:::: {.details summary="Registration and native authorization wire contract"}

### Exact registration

The registration has exactly these members. Duplicate decoded names, omitted members, null and additional members are invalid.

| Member | Value |
| --- | --- |
| `version`, `purpose` | `"0"`, `"service-authorization-registration"` |
| `registration` | Nonzero ObjectId |
| `generation` | Positive canonical uint64 decimal string |
| `service`, `issuer` | Identical canonical HTTPS origins using the service-origin grammar |
| `clientId` | Nonempty opaque ASCII identifier, compared exactly |
| `authorization`, `token`, `linkChallenge`, `linkComplete` | Four distinct canonical HTTPS endpoints at that origin |
| `redirectPath` | `/mail/oauth/callback` |
| `scopes` | Exactly `["mail.service.link", "mail.service.status", "mail.service.submit"]` |

These are operator-defined scope strings, not claims of IANA registration. `registrationDigest` is lowercase SHA-256 of the exact retained UTF-8 registration bytes. Reserialization changes that digest. The service retains the registrations it authorizes for each client and rejects unknown or withdrawn digests.

### Authorization and callback

The native loopback URI is `http://127.0.0.1:<port>/mail/oauth/callback` or `http://[::1]:<port>/mail/oauth/callback`. Exact registered host/path matching permits only the native-loopback ephemeral-port exception. No localhost resolution or arbitrary redirect is permitted. Supporting this client flow does not establish the full server redirect-option support described by RFC8252.

Each attempt uses independent cryptographically random 32-byte state and PKCE verifier values encoded as unpadded base64url. The S256 challenge is unpadded base64url of SHA-256 over the verifier's ASCII bytes. Persist the selected registration, exact redirect, verifier, state and attempt expiry in secret storage before browser navigation.

The authorization request supplies `response_type=code`, `client_id`, `redirect_uri`, the exact space-delimited scopes, `state`, `code_challenge` and `code_challenge_method=S256`. Failure does not permit a downgrade to plain PKCE. The authorization server binds the issued code to the authenticated account, client, redirect, challenge, scopes and expiry.

The external browser navigates with GET to the exact registered authorization
endpoint. This browser request is not required to include `Cache-Control:
no-store`: the native client cannot depend on injecting headers into system-browser
navigation. The authorization server MUST include `Cache-Control: no-store` on
authorization responses, including redirects and errors.

This request-header exception applies only to GET at that exact authorization
endpoint. Programmatic token exchange, refresh, link requests, service submissions
and status requests retain their owning request and response no-store rules.
The exception grants no endpoint, credential or redirect permission and changes
none of the issuer, state, PKCE, registered-callback, scope, account-authorization
or code-consumption checks. Invalid browser requests do not become authorized
merely because this cache header is absent.

A callback contains one matching `state` and one exact expected `iss`. Success contains one nonempty `code` and no error; denial contains one `error` and no code. Duplicate selected parameters or ambiguous branches fail. Unknown extensions cannot change endpoint or grant selection. Check attempt expiry and registration before token exchange. The fixed callback response must not echo credentials or load external content.

### Token exchange and renewal

POST form-encoded `grant_type=authorization_code`, code, client ID, the original exact redirect URI and verifier to the configured token endpoint. The redirect is not the callback URL with appended code/state. Use validated TLS, no redirects, no ambient credentials and no public-client secret.

A successful no-store JSON response supplies `token_type` as case-insensitive `Bearer`, opaque access and refresh token strings, and `expires_in` as a positive JSON integer (not a boolean). This profile requires a refresh token although OAuth generally makes one optional. The `scope` string contains exactly the selected case-sensitive scope set, in any order. Tokens are separated by one ASCII space; malformed strings and duplicates are rejected as a profile restriction, not a general OAuth duplicate-scope requirement. Base-defined OAuth parameters cannot repeat. The client consumes its pending callback before redemption; an uncertain redemption is held rather than automatically reusing a code. Server code replay is rejected and the associated issued family revoked where it is known.

Refresh is restricted to the same client, registration and original scope. Rotate refresh tokens and detect reuse by family. An uncertain refresh response requires reconnecting rather than guessing which refresh token remains valid. Renewal preserves existing service submission bytes. Tokens and verifiers may occur in their required TLS-protected authorization transport; they must not appear in public journals, message content, receipts, logs or callback display.

::::

:::: {.details summary="Exact challenge, device proof and mapping"}

### Challenge request and response

The challenge request has exactly `version:"0"`, `purpose:"service-account-link-request"`, `registrationDigest`, `principal`, `device`, `state` and `binding`. The principal/device use existing enp0/end0 grammars; state and binding are exact lowercase SHA-256 digests. An access token with `mail.service.link` authorizes this endpoint, not a client-supplied account identifier.

The returned challenge has exactly the following fields:

| Member | Value |
| --- | --- |
| `version`, `purpose` | `"0"`, `"service-account-link"` |
| `challenge` | Fresh random nonzero ObjectId |
| `nonce` | 32 fresh random bytes as 64 lowercase hexadecimal characters |
| `issuer`, `service`, `clientId`, `registrationDigest` | Exact trusted registration bindings |
| `grantBinding` | Opaque 32-byte lowercase-hex grant-family binding; not an account identifier |
| `principal`, `device`, `state`, `binding` | Exact requested identity bindings |
| `notBefore`, `notAfter` | Ordered canonical uint64 decimal seconds |

The service retains the exact bytes and internal account/client/family association before returning them. The response is authenticated by the direct TLS origin; it is not a transferable server signature. Challenge lifetimes and processing budgets are explicit deployment settings. The entire selected challenge interval must lie inside the current device binding's authorized interval.

### Signed completion

The completion wrapper has exactly `payload`, `signature` and `identity`. Payload is canonical padded base64 of the exact challenge bytes. Signature is 128 lowercase hexadecimal characters. Identity is the existing identity-bundle object; changing its transport serialization does not change the signed payload.

The signature uses Ed25519 and the fixed domain `email-next/service-account-link/v0`, followed by NUL, a four-byte unsigned big-endian payload length and the exact UTF-8 payload. Identity, discovery and invitation signature domains cannot substitute for it.

Before mutation, verify the wrapper, retained challenge correspondence, current authenticated grant and account/family, candidate signature, accepted identity chain/head/binding, send-role authority and credible interval. Recheck grant and identity authority after acquiring the write transaction. A failed first-contact link leaves no partial new identity pin. Valid known-principal transitions or conflicts remain observations even when they hold the proposed mapping.

Mapping is scoped to issuer, internal account key, client and grant family. It retains one exact principal, accepted identity evidence and link generation. This `send` proof authorizes only the proposed service-account link; it does not enroll a device or change the principal root. Known revocation or conflict blocks new service effects. Local membership checks by the email client and resource-side authorization both remain required.

### Receipt and exact retry

The receipt has exactly `version:"0"`, `purpose:"service-account-link-result"`, `challenge`, `requestDigest`, `service`, `principal`, `link`, `generation` and `outcome:"linked"`. The digest is SHA-256 of the exact challenge payload; link is a nonzero ObjectId and generation a positive canonical uint64 string. No token, account ID or identity bundle is included.

Retain the exact signed proof before submission. A currently authorized same-family retry with identical payload **and signature** returns the retained receipt, including after challenge expiry. Changed signature or payload cannot use that shortcut or poison the accepted mapping. Withdrawal still blocks authorization. The receipt records a link; it does not replace the service's current grant checks or become a conversation answer.

::::

## Reconnect without changing the action

Signing back in can restore access to an existing submission, but it must not move that submission to a different service account. The service binds each person's action to the account authorized for it. Choosing another account does not change that binding, even when both accounts are linked to the same Email/2 identity.

Replacing or revoking a device binding stops its old service link from authorizing new work. A currently authorized device can connect again through fresh sign-in and linking. Existing request bytes and receipts remain intact; reconnecting does not mean an uncertain action failed or should be performed again.

:::: {.details summary="Account isolation, link continuity, disconnect and execution boundaries"}

### Immutable action-account authority

For this native profile the service's independently provisioned action authorization binds each `(service, action, answering principal)` to exactly one internal account incarnation. The account handle is non-reassigned service state, not an email address, OAuth subject supplied by a client, request member or public receipt field. The service checks that binding for both POST and GET. Linking another account to the same principal does not authorize inspecting, replacing or repeating the original account's action. A missing authorization record holds access; first submission cannot allocate that authority.

An action intended for a different account needs independently provisioned action authority with a new action identity and its corresponding immutable question binding. The client cannot make that change as a retry or use it to resolve a possibly completed earlier action. The existing principal/action/submission deduplication and replacement chain remain unchanged; the immutable action-account authorization prevents using the same chain through another account. Reassignment or deletion of an account invalidates its grants and authorization before reuse of any login name; the new incarnation never inherits those records.

A reconnected family for the original account and principal can inspect retained submissions under current status authority. A different account receives an authorization denial with no receipt or effect details. An HTTP denial, missing record or successful sign-in does not prove whether an earlier action executed. Account authentication and Email/2 linking alone do not provision an action, choose its options or authorize a business effect.

### Current link and unchanged authority

Retain the linked principal, device, original accepted state and binding with the family. At each new service operation require current device send authority and [unchanged-binding accepted ancestry](provider-grants.md#retain-an-unchanged-device-binding) from that exact link. An unrelated accepted identity-head advance may preserve it; a different binding, key, role gap, known conflict, revocation or state1 repair does not. Loading the device's newest key or binding is not permission to retarget the old link. A link receipt is historical evidence, not a current authorization credential.

Version 0 permits one principal/device link per grant family. Apart from exact retained completion replay it does not refresh that mapping in place. A binding change or repair therefore requires disconnecting the old family and obtaining a new account grant and current signed link; a fresh login cannot change an old submission's action-account binding. Full state1 validation remains necessary before claiming repair-aware support. A retired principal cannot regain sending power through a service login. If current linking/status authority cannot be obtained, retain existing local evidence and hold protocol access rather than forging the old identity.

### Disconnect and revoked grants

`DELETE` to the exact registered `linkComplete` endpoint, with no body and an access token carrying `mail.service.link`, disconnects that authenticated family. No account/family selector is accepted in a body or URL. This method on the existing registered endpoint adds no guessed path or new registration field. Use the profile's direct TLS, no ambient credentials, no redirects, no-store and Bearer error rules. Commit family/link withdrawal and access/refresh invalidation before returning HTTP204 with an empty body. A still-valid independently authorized family cannot disconnect another family through a supplied identifier.

The client stops using and clears the selected local credentials even if the disconnect response is lost; it retains non-secret submission/receipt evidence and any required protected retry journal. An invalid or expired token cannot prove remote withdrawal. Reconnect or the service's separately trusted account-management interface may be required to finish revocation; report the uncertainty instead of saying every session is disabled. Disconnect is neither cancellation of a pending action nor reversal of a completed effect. Already authorized irreversible external work may still complete.

Registration withdrawal, refresh reuse, known incompatible identity changes and account deletion must be effective at the serialized resource decision, not merely checked at a preceding HTTP handler. Authorization and the effect/status read must share authoritative serialization or a fail-closed authorization lease invalidated before a conflicting withdrawal commits. A token snapshot from another connection cannot authorize a later mutation after revocation wins that order. Separate databases do not provide this property automatically. Retained pending effects need their documented recovery/reconciliation protocol; withdrawal never justifies a false rejected/not-applied receipt.

### Acceptance cases

Test the same principal in two authenticated accounts, absence of action-account provisioning, attempted authorization retargeting, reconnect to the original account, unchanged-binding head advance, changed binding with the same signing key and send role, state1 repair, retired identity, exact old link receipt replay, disconnect/lost response, expired revocation credentials, refresh reuse and concurrent resource commit/withdrawal. Original receipts remain historical; unknown outcomes cannot generate a replacement submission. Cross-account denial cannot disclose original receipts. The configured component covers selected account/binding cases, not full state1, public disconnect transport or cross-database revocation serialization.

::::

## Implementation evidence and boundaries

The [account-link experiment](evidence/README.md#service-account-authorization-and-linking) uses simulated trusted account authentication and consent, actual IPv4/IPv6-capable loopback callback transport, TLS code redemption and link endpoints, real device signatures, and the joined protected SMTP question/button/service path. A separate-origin browser demonstration presents synthetic account consent, explicit principal linking, then a newly delivered protected question. It does not supply a production login website, system-browser integration or platform keychain. Its encrypted local vault needs an externally protected key.

The selected bearer profile retains token-theft risk. Linking is not per-request sender constraint. A deployment must explicitly accept that boundary or select an audited sender-constrained profile. The experiment does not certify external account authentication, certificate-status backends, split-operator token validation, independent interoperability or complete RFC8252 authorization-server support. Local validation and a remote service effect are not one atomic transaction.
