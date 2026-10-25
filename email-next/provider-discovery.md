---
title: Finding a provider service
order: 10.25
blurb: account setup · authenticated delegation · native client registration
sectionNav: true
---

# Finding a provider service

A client can learn where a mail domain offers an Email/2 control service without putting an address in a public lookup. It asks the selected domain for a small service record, checks that domain's HTTPS identity, and retains the exact delegation. Signing in and authorizing a particular peer are later, separate steps.

> [!ex] A custom-domain account
> Alice connects her existing `alice@example.org` account. During explicitly enabled provider setup, the client asks `https://example.org/.well-known/mail-provider` for service locations. The domain delegates to `https://mail-service.example`. Alice sees that service when she connects it. Her mailbox password and existing access tokens are never sent to the discovered location.
>
> The domain record does not contain Bob's keys or establish his identity. Alice's client still needs independently accepted device evidence and the permission required for a particular exchange.

> [!note] Retained version0 discovery profile
> `email2-provider-discovery-v0` selects account-domain delegation and native public-client registration. The well-known suffix and profile identifier are draft allocations, not registered names. The [configured queue contract](provider-control.md) remains unchanged. The [public grant profile](provider-grants.md) separately defines account/device links and pair-specific queue credentials. The [unknown-peer bootstrap contract](bootstrap.md) separately defines first-contact authority. Joined implementations remain unfinished; discovery alone does not make a service publicly interoperable.

The [current Encryption baseline](suite-profile.md#current-client-baseline) uses [provider descriptor2](#discover-the-asynchronous-agreement) when this capability is offered. Retained descriptor0/1 definitions remain exact for earlier exchanges. Version2 selects the asynchronous application while preserving shared account authority; a descriptor is not evidence that the complete service is implemented.

The [cooperating-service architecture](service-federation.md) additionally calls
for separately scoped directory, rendezvous and ciphertext-delivery roles. Those
roles need an exact new discovery binding. They are not extra fields in the
retained strict descriptors below, and a domain delegation still does not prove a
mailbox-to-device identity. Clients using independent services need an accepted
locator or configured common federation when their email domain supplies none.

## Discover for an explicit setup purpose

Account-setup discovery starts from an account the person has explicitly connected or selected, using its retained domain spelling. The separate [first-contact flow](first-contact-setup.md) may also discover the domain of an explicitly selected recipient under enabled secure-setup policy. Neither path starts from arbitrary incoming content, an HTML link, a signature block, an MX target or an HTTP authentication challenge. A client may remember the person's permission to refresh this account's provider setup.

Use the [canonical mailbox-address contract](mailbox-addresses.md), including internationalized and quoted local parts. Select the parsed lowercase A-label domain; an `@` inside a quoted local part is not a domain boundary. Only that domain enters discovery URLs. No local-part normalization, address-literal lookup or inference from a display name is permitted. Validation unavailable under the selected IDNA provider holds this extension without preventing separate ordinary-mail use.

Fetch exactly `https://<selected-domain>/.well-known/mail-provider`, using the proposed [RFC8615 well-known suffix](https://www.rfc-editor.org/rfc/rfc8615.html#section-3), at port 443, without a query, fragment, mailbox address, Authorization header, cookies, ambient client certificate or HTTP authentication. Do not follow redirects. TLS 1.3 and the [service identity contract](service-answers.md#establish-the-protected-connection) apply, with the original selected domain as the DNS-ID reference. Neither DNS resolution nor a certificate-selected name changes that reference. A CNAME does not authorize a different HTTP origin.

Only a 200 `application/json` response with identity content coding can supply a record. Reject compressed representations, duplicate JSON names, invalid UTF-8, unknown fields and bodies larger than 65536 octets; JSON container depth is at most 16. Enforce response-header and connection budgets before parsing. Servers use `Cache-Control: no-store`; clients request no-store and do not obtain the record from an unauthenticated cache. Client and server implementations retain finite connection, deadline and retry settings rather than claiming this representation limit bounds all network work.

A 404 or 410 means that this fetch has no usable public delegation. A timeout, TLS failure, 429, 5xx, redirect or invalid representation means unavailable or invalid, not permanent lack of Email/2 support. None supplies new permission for plaintext delivery, clears a previous service binding, or changes a peer’s identity. Apply Retry-After where valid, bounded local backoff otherwise. Failure alone cannot start mailbox setup; a separately enabled [ordinary-mail setup policy](mailbox-setup.md) may select its own bounded authorized attempt. A retained delivery fallback condition still follows the [frozen policy and disclosure rules](delivery-policy.md#freeze-disclosure-before-releasing-content); a failed lookup does not authenticate incompatibility.

Automated network access must respect the client's configured network boundary. Public discovery must not release requests to loopback, link-local, private or otherwise disallowed resolved addresses. Apply the policy to every candidate address and the actual connected endpoint, including across DNS changes; do not validate one answer and connect to an unchecked second answer. An explicitly configured enterprise/test network can authorize its own destinations while retaining TLS identity, exact-origin and credential isolation. A received record cannot change that policy. The prototype below does not implement a DNS resolver or these socket checks.

## Keep the domain and service authorities distinct

HTTPS authenticates the account domain's delegation of service locations. It does not prove a mailbox belongs to an Email/2 principal, enroll a device or verify a human. A provider serving several mailbox domains publishes a delegation through each domain it supports; an MX hostname is not a substitute. The service validates its own TLS identity before registration or sign-in.

A delegate may be at another canonical HTTPS origin. All advertised control and management endpoints, the OAuth issuer and authorization endpoints are restricted to that one service origin in this version. The delegation does not permit sending a credential issued for the account domain, mail server or another service. A browser sign-in is a deliberate account-setup action; receiving or opening mail never starts it.

During account connection, the client displays the selected account domain and service origin before sign-in. Recipient bootstrap uses its separately enabled setup policy; it never signs the sender into the recipient's service or supplies a management credential. A changed service origin requires a fresh local confirmation before new account registration or sign-in. Existing secrets remain bound to their original origin and exact grant. Even a legitimate new provider cannot inherit them through this record.

::: {.details summary="Exact delegation record and retained publication state"}

The response object has exactly the following members. Null, omissions, extra members and wrong types are invalid.

| Member | Contract |
| --- | --- |
| `version`, `purpose` | `"0"`, `"provider-service-discovery"` |
| `domain` | Exact selected discovery domain, independently validated as above |
| `publication` | Random nonzero ObjectId: 32 lowercase hexadecimal characters |
| `generation` | Positive canonical unsigned-64 decimal string |
| `service` | Canonical HTTPS origin under the service-answer origin grammar |
| `controlPrefix`, `managementPrefix` | Distinct canonical absolute HTTPS path prefixes at `service`, ending in `/`; their paths must not overlap by segment-prefix containment |
| `notBefore`, `notAfter` | Ordered canonical unsigned-64 decimal Unix seconds; the whole current credible clock interval must fit |

Prefixes obey the existing service endpoint grammar: no query, fragment, userinfo, dot segments, encoded slash/backslash or noncanonical encodings. They designate protocol resources beneath provider-controlled paths. They are not instructions to crawl a website or infer more endpoints. OAuth metadata is obtained separately at the fixed location below.

A publication identifies one monotonically versioned delegation history for this domain. The publisher serves identical response bytes for a retained generation. Any byte change, including serialization or validity renewal, requires a higher generation. The generation is not a signature, a proof of global freshness, or a trustworthy timestamp.

Retain `(domain, purpose, publication, generation, exact response bytes, SHA256(response bytes), service, local decision generation)` durably before using the delegation. Storage may contain additional local provenance. Reads of a candidate do not mutate this accepted row. Retain the local purpose as either `account-setup` or `recipient-bootstrap`; one purpose never authorizes the other. A local accept operation compares the expected decision generation, validates trusted transport provenance and the complete current clock interval again, and commits its decision and row together:

- No row: require authorization for the exact local setup purpose. Account sign-in additionally requires confirmation of the discovered service origin; recipient bootstrap requires enabled secure-setup policy for the selected recipient and never gains sign-in authority.
- Same publication and generation: identical bytes are a retry; different bytes are a conflict and cannot replace the retained row.
- Same publication, higher generation: accept the complete fresh record, including skipped generations, only under current account-refresh permission. For account sign-in, confirm an origin change separately. Recipient bootstrap rechecks its domain delegation and setup policy; it cannot migrate any credential. Do not mix fields from two records.
- Lower generation: reject rollback. A failed fetch or expired record never resets the high-water mark.
- Different publication: require explicit local reset/reconnection for this domain and purpose, retaining the old decision as history. A reset retires pending authorization attempts; it cannot be authorized by the incoming record or an HTTP error.

A normal publication keeps its ID even when service locations change. New publication IDs exist for an explicit publisher/client reset, not automatic rollback recovery. The high-water mark detects rollback only relative to retained local state; a newly installed client or whole-machine rollback can lack it. HTTPS supplies no proof that a newer publication has not been withheld.

Updating a delegation invalidates pending native authorization and account-link attempts tied to the former exact descriptor digest. It does not rewrite accepted queue grants, revoke a device, delete an uncertain submission or grant access at a new location. Existing immutable queue grants remain subject to their own expiry, revocation and explicit local authorization. A failed candidate cannot overwrite them. Disabling provider access locally stops subsequent control requests without changing mail delivery policy.

:::

## Reuse sign-in mechanics without sharing permissions

Provider control, relay management and automatic setup use the same native sign-in procedure. Each connection still has its own module, delegated service and exact requested scopes. Connecting one does not connect the others.

| Own-account connection | Selected scopes |
| --- | --- |
| Provider control | Both `mail.provider.link` and `mail.provider.manage` |
| Relay | An explicitly selected nonempty subset of `mail.relay.link`, `mail.relay.manage`, `mail.relay.submit`, sufficient for the intended operations |
| Automatic setup | An explicitly selected nonempty subset of `mail.setup.link`, `mail.setup.request`, `mail.setup.respond`, sufficient for the intended operations |

Request only the permissions needed. An operation that lacks a required scope or account/device link stays unavailable; the client cannot borrow it from another connection. Finding a recipient's service is not an own-account connection and cannot start sign-in.

:::: {.details summary="Shared callbacks, exact registration and module isolation"}

All three connections use exactly the two registered loopback callback forms shown below: `http://127.0.0.1:1/mail/provider/callback` and `http://[::1]:1/mail/provider/callback`. The provider spelling names the shared callback route; it does not select a provider-control grant. Keep the existing ephemeral-port exception, external-browser, issuer, state and PKCE checks. Do not derive another callback path from a module label or accept a wildcard path.

For each connection, validate the exact descriptor under that module's owning discovery contract. Fetch OAuth metadata only from its selected service origin. All required metadata capabilities, same-origin endpoint restrictions, public-client rules and response bounds in this chapter still apply. Replace only the required scope set with the exact set selected for that module. Additional advertised scopes do not become requested permissions.

The registration request has the same exact fields and callback array as the provider example, with `scope` containing only the selected module's scopes, once each, separated by one ASCII space. The response must retain that exact set, in any order, without omissions, additions, duplicates or malformed separators. The token response and subsequent refreshes retain the same exact selected scope set under the existing native authorization rules. Other protocol fields and required validation do not acquire new defaults.

Bind retained registrations, pending state/PKCE records, account grants and local lookup keys to the selected module, own-account purpose, original delegation and metadata bytes/digests, issuer, client ID, registered callback forms, exact scope set and local setup generation. A shared origin, identical callback path or equal client ID cannot merge these records or make a different grant acceptable. The callback selects only its exact retained one-time attempt; a URL path alone cannot select a module or account.

Reuse a registration only under that complete unchanged binding. A different module or requested scope set needs its own registration and authorization; no registration-update API or refresh-based scope widening is selected. A changed descriptor/metadata binding invalidates pending attempts as specified below. Previously issued credentials retain only their original scope, endpoint and lifecycle; they cannot be forwarded to a replacement service or silently repurposed. Preserve uncertain operations and their old outcomes during reconnection.

These rules define native authorization reuse only. Queue, relay and bootstrap account-link records, device proofs, role checks and operation lifecycles remain owned by their respective contracts. A native token is not a queue-role credential, route permission, recipient key or content-release authorization.

::::

### Independent registrar and home connections

An independent registrar, home or package service uses the native sign-in procedure above under the following explicit candidate module selection. This connects the person's own selected service account. It does not prove control of a mailbox or authorize another person's account.

| Module | Selected descriptor | Exact requested scope set |
| --- | --- | --- |
| `mailbox-association` | [Association descriptor](mailbox-registration.md#exact-service-descriptor), profile `mail-association-service-v0` | `mail.association.link mail.association.manage` |
| `rendezvous` | [Home-service descriptor](rendezvous.md), profile `mail-rendezvous-v0` and purpose `rendezvous-service` | `mail.rendezvous.link mail.rendezvous.manage` |
| `packages` | [Package-service descriptor](package-allocation.md#service-descriptor), profile `mail-package-allocation-v0` and purpose `package-service` | `mail.packages.link mail.packages.manage` |

For each candidate, the selected descriptor comes from explicit own-account service configuration or an already accepted delegation under its owning contract. Preserve that original selection and its trust provenance; do not manufacture a mailbox-domain delegation for an independent service. Incoming recipient evidence cannot select this login or install a new service origin. Rendezvous currently selects explicit own-account configuration; its still-undefined domain-discovery binding cannot be inferred from this shared sign-in procedure.

The selected origin supplies the required RFC8414 metadata at the same well-known location defined below. Its `scopes_supported` must include both exact scopes for the selected row. The other metadata, public-client registration, issuer, endpoints, external-browser, S256 PKCE, token, refresh and revocation requirements remain unchanged. These bindings introduce no new OAuth metadata member or discovery URL. The same two registered loopback callback forms apply; do not derive an association or rendezvous callback path from the module name.

Register each module separately with exactly its selected scope set. Retain the selected module, descriptor bytes/digest, own-account configuration or delegation provenance, metadata bytes/digest, issuer, client ID, callback forms, scope set and local setup generation in the attempt and credential binding. A shared origin, client ID or callback does not merge grants. A descriptor or metadata change invalidates pending attempts; it does not forward an old credential to the replacement service. Refresh cannot add another module's scopes.

A successful native login supplies only the selected account-management grant. The association, rendezvous and package owners define their own device-link records, signature purposes, string timestamps, reset/inspection and later operation permissions. Existing provider/relay/setup links, proofs and credentials cannot be relabeled for these candidates. A client implementing only the earlier provider, relay and setup modules does not gain these capabilities merely because a server advertises these scope strings.

Acceptance evidence must include the selected modules at a shared origin with equal callback/client identifiers, wrong or missing advertised scopes, changed descriptor/metadata during an attempt, a callback from another module's pending attempt, an incorrectly scoped token or refresh, and revocation restricted to its original grant family. Successful native authorization must still leave mailbox verification and device/home authority unestablished until their actual owning checks complete. The new candidate bindings require their own implementation evidence; earlier native-flow tests do not establish their support.

## Register and sign in through the selected service

This section applies only to connecting the person's own account, never to recipient bootstrap. A recipient's descriptor cannot trigger OAuth registration or sign-in.

The service origin is the OAuth issuer in this version. Obtain its [RFC8414 authorization-server metadata](https://www.rfc-editor.org/rfc/rfc8414.html#section-3) from `service + "/.well-known/oauth-authorization-server"` through the same credential-free, redirect-free transport rules. Require exact issuer equality. Unknown metadata extensions may be ignored; they cannot replace selected fields or install credentials.

The service must explicitly support native public clients both when issuing tokens and when revoking them. Token support alone does not establish revocation support: RFC8414 gives each endpoint its own authentication-method declaration, with a secret-based default when that declaration is absent.

::: {.details summary="Required authorization-server metadata"}

Require the following fields. Each selected list is an array of unique nonempty ASCII strings. Additional supported values do not select them. An absent requirement leaves this profile unavailable; endpoint names cannot establish support.

| Field | Required value or included values |
| --- | --- |
| `issuer` | Exact selected service origin. |
| `authorization_endpoint`, `token_endpoint`, `registration_endpoint`, `revocation_endpoint` | Four distinct canonical same-origin endpoints. |
| `response_types_supported` | `code`. |
| `grant_types_supported` | `authorization_code` and `refresh_token`. |
| `token_endpoint_auth_methods_supported` | `none`, explicitly advertised. |
| `revocation_endpoint_auth_methods_supported` | `none`, independently and explicitly advertised. |
| `code_challenge_methods_supported` | `S256`. |
| `authorization_response_iss_parameter_supported` | JSON boolean `true`. |
| `scopes_supported` | The exact selected module's scope set; provider control requires `mail.provider.link` and `mail.provider.manage`. |

No received `jwks_uri`, documentation link or signed-metadata field is fetched by this profile. Unknown extensions cannot replace required fields, change the selected origin or install credentials.

:::

[Dynamic client registration](https://www.rfc-editor.org/rfc/rfc7591.html#section-3) supplies a client identifier without requiring every email client developer to arrange credentials with every provider. This profile selects unauthenticated registration for a public native client. The provider can enforce finite rate and capacity limits, but cannot advertise this public profile while requiring an undisclosed initial access token, developer allowlist, software statement or public-client secret. Registration establishes no trusted application brand, human identity, mailbox authority or Email/2 authority.

::: {.details summary="Native registration and authorization binding"}

POST `application/json` to the exact selected registration endpoint, with no Authorization header or ambient credentials. The request has exactly:

```json
{
  "redirect_uris": [
    "http://127.0.0.1:1/mail/provider/callback",
    "http://[::1]:1/mail/provider/callback"
  ],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mail.provider.link mail.provider.manage"
}
```

The literal port 1 registers the two exact host/path forms, not a port to bind or an address to visit. For the native authorization request, the server accepts an available ephemeral port under the [RFC8252 loopback exception](https://www.rfc-editor.org/rfc/rfc8252.html#section-7.3). There are no wildcard hosts, localhost resolution, custom schemes or embedded browser callbacks in this version.

Require HTTP201, no-store JSON and bounded uncompressed bytes. The response includes the exact registered metadata, a nonempty opaque ASCII `client_id` of at most 256 characters, and a nonnegative safe JSON integer `client_id_issued_at`. The scope may reorder the exact requested set, with no duplicates, additions or omissions. The provider-control example requests its two scopes; relay and setup use their explicitly selected nonempty sets under the shared native-module rules. Other client metadata is not selected. RFC7591 additional response members may be ignored, except `client_secret`, `client_secret_expires_at`, `registration_access_token` and `registration_client_uri`, whose presence rejects this selected unmanaged public-client registration. No returned URL can change the retained endpoints. This is a profile restriction, not a claim that those members are generally unsafe in OAuth.

A registration error installs no client identifier, endpoints or permissions. For HTTP400, treat RFC7591's `error` and optional `error_description` as bounded inert data; never execute a returned description or use it to repair a redirect URI automatically. Other errors, malformed responses and unexpected success statuses also install nothing. An HTTP401 challenge does not authorize supplying a developer secret, initial access token or software statement. Rate limits, temporary failures and lost responses permit only bounded retry under the original setup policy and endpoint binding.

Retain the original delegation bytes/digest, exact selected metadata bytes/digest, client ID and registered callback forms before sign-in. Reuse the resulting client registration for the same complete [module, delegation, metadata and scope binding](#reuse-sign-in-mechanics-without-sharing-permissions); do not register on every message or restart. A lost registration response may leave an unused public registration: it grants no account access. Retry only through bounded setup policy; do not guess the lost identifier or claim exact registration idempotency. No dynamic registration-update API is selected.

Use authorization code with S256 PKCE, external system browser, fresh state, exact issuer-response checking, the retained ephemeral loopback redirect, no public-client secret and no resource-owner-password grant. The [native service authorization rules](service-authorization.md#authorization-and-callback) define those mechanics and code/refresh uncertainty handling. Here the selected callback path and scopes are the provider values above, not service-button scopes. Tokens are opaque Bearer credentials restricted to this provider's management resources. Rotate public-client refresh tokens with reuse detection. A token response must return exactly the selected scope set. A provider-management token is never a queue-role credential and cannot be sent to a peer provider.

The server derives the authenticated account from its own login/consent system; a client-supplied address or OAuth client identifier cannot select it. The [public grant profile](provider-grants.md) defines account-to-device linking and peer-grant issuance, validating that account independently. This discovery chapter does not let successful sign-in substitute for those operations.

The client binds every pending attempt to both exact retained descriptor digests, issuer, client ID, callback, scopes and current local setup generation. Recheck these before navigation, callback consumption, token exchange and link completion. A changed binding or uncertain code/refresh redemption holds the attempt and requires reconnecting. Changes cannot clear uncertain queue operations or authorize a fallback.

Local disconnect disables the management family immediately. Submit revocation only to its originally trusted `revocation_endpoint`; a changed discovery record cannot receive an old token. Use the following [RFC7009](https://www.rfc-editor.org/rfc/rfc7009.html#section-2) binding.

::: {.details summary="Revocation request, family effects and uncertain results"}

POST form-encoded `token` containing the original refresh token, `token_type_hint=refresh_token` and the original `client_id`. Send no Authorization header, client secret or ambient credentials. No query-string, JSONP or browser-script revocation mechanism is selected.

The server validates the registered client identifier and, for a recognized token, verifies that the token belongs to that client before changing a grant family. A client identifier alone cannot select an account or family. This profile returns HTTP400 `invalid_client` for an unknown client, and HTTP400 `invalid_grant` for a recognized token belonging to another client; these error mappings are profile choices, not additional RFC7009 requirements.

For a recognized eligible refresh token, revoke the entire management grant family and its access/refresh tokens atomically under the [grant lifecycle](provider-grants.md#credentials-and-revocation). That lifecycle also invalidates every derived queue credential and blocks reads as well as writes. An unknown or already-invalid token receives HTTP200 without selecting or changing another family. Ignore the HTTP200 body. Success does not prove that a particular token existed, that every device learned of the revocation, or that stored message data were deleted.

The token-type hint only guides lookup. Ignore an unsupported hint; if the hinted lookup misses, check other supported token types as RFC7009 requires. Bound parsing, lookup and connection work through the service's declared finite capacity and rate policy. A lookup miss cannot authorize searching an arbitrary account selected by client input.

HTTP503 means the token may still be valid remotely. Lost responses, other errors and unsupported token types also leave the result uncertain. Keep the local family disabled and preserve the original token, client and endpoint binding for bounded retry, respecting applicable Retry-After and backoff. Do not switch token type, endpoint, origin or authentication method automatically to overcome an error.

:::

The bearer risk described by [service authorization](service-authorization.md#implementation-evidence-and-boundaries) remains: possession of a stolen management token can exercise its authorized service grant. PKCE, a linked device signature and a registered client ID do not create per-request sender constraint. This chapter does not claim complete current OAuth security compliance or select a DPoP binding.

:::

## Evidence and remaining binding

The [discovery experiment](evidence/README.md#provider-discovery-and-public-client-registration) validates exact delegation bytes, authenticated-fetch provenance, current intervals, same-origin metadata, public registration and durable local update decisions. It tests restart, rollback, conflicting generations, origin confirmation, reset and concurrent stale decisions. Its trusted fetch input is supplied by a test adapter. It does not implement DNS, public PKIX, dynamic registration HTTP, system-browser login, token issuance or peer grants.

Required public-deployment evidence additionally includes domain delegation through real TLS, network-boundary/DNS changes, throttled registration, an actual external-browser sign-in, account-to-device linking, pair-specific credential issuance and revocation through the queue, provider changes, mailbox reassignment and a protected message following a successful exchange. The [grant binding](provider-grants.md) defines the next steps; complete public provider-negotiation claims still require their joined implementation and acceptance evidence. The unknown-peer bootstrap binding remains separate.

## Independent relay capability

The [relay module](relay-routes.md#discover-a-relay-service) reuses the transport, publication, native authorization and credential-isolation mechanics here under its own descriptor, scopes and namespace. Relay-only providers need not advertise or implement the queue. An existing queue registration or token does not silently gain relay administration/submission rights.


## Reply-aware queue discovery

A provider advertising automatic setup for declared reply policies uses descriptor1 for the known-pair queue. It says which exact agreement the service carries; it does not prove that a recipient device supports that agreement.

::: {.details summary="Exact provider descriptor1 and account boundaries"}

Descriptor1 has exactly descriptor0's fields plus required `agreement`, with version `"1"` and agreement exactly `"mail-conversation-v1"`. Purpose, selected-domain validation, well-known path `/.well-known/mail-provider`, publication/generation, canonical service, two distinct same-origin prefixes, transport/validity and retained high-water rules remain unchanged. Its controlPrefix selects [mail-provider-control-v1](provider-control.md#reply-aware-known-pair-exchanges); its managementPrefix selects [mail-provider-grants-v1](provider-grants.md#reply-aware-account-and-pair-permissions). Active version0 and version1 prefixes at one service cannot overlap by segment containment. Version is not a new domain-delegation, account or publication namespace.

Native public-client registration/login/PKCE, the exact selected mail.provider.link/mail.provider.manage scopes, origin-bound credentials, callback forms and module separation remain unchanged. A new descriptor or agreement does not authorize a new origin, broader scopes, another principal or a recipient's account. Account/family/incarnation and link/reset/revocation state remain authoritative across queue versions. Unsupported descriptor1 leaves this provider path unavailable; never reinterpret it as0 or infer a compatible endpoint from its URL spelling. Existing version0 records retain their original routes/validity while independently eligible.

Fresh role credentials and pair approval must name the exact successor configuration. An old active grant cannot be edited into the new profile, even when participants, service and account names match. A remembered eligible approval policy may authorize a new preparation, but the service cannot silently replace the approved bytes or expand peer scope.

:::


## Discover the asynchronous agreement

A provider can offer setup for independently ready deliveries through descriptor2. The selected agreement identifies the records the service carries. Each actual recipient device must still publish its own valid support; a provider cannot promise that support on its behalf.

::: {.details summary="Exact descriptor2 and connection boundaries"}

Descriptor2 has exactly descriptor1's member inventory, with `version` equal to `"2"` and `agreement` equal to `"mail-conversation-v2"`. Purpose remains provider-service-discovery. The selected-domain grammar, `/.well-known/mail-provider` path, service origin, publication/generation, two prefixes, validity, strict parsing and transport rules remain unchanged. Its controlPrefix selects [mail-provider-control-v2](provider-control.md#obtain-asynchronous-device-evidence); managementPrefix selects [mail-provider-grants-v2](provider-grants.md#authorize-asynchronous-pair-exchanges).

Active prefixes for different queue versions at one service cannot overlap by segment containment. The descriptor response selects one exact branch before validation; a failed descriptor2 cannot be parsed as1 or0. Unsupported discovery leaves this path unavailable for the retained required agreement. It neither proves recipient incompatibility nor authorizes an older agreement or ordinary delivery.

All versions share the same domain/purpose/publication high-water and account/module authority. Changing any accepted descriptor bytes requires a higher generation. Version is not another publication, rollback escape or reset namespace. Retained earlier grants keep their original locations, deadlines and authorization; a descriptor update cannot edit them.

Use the existing native registration/login, issuer-bound authorization-code/S256 PKCE, exact mail.provider.link/mail.provider.manage scopes, account/device linking and origin-bound credentials. Descriptor2 introduces no scope, callback or sign-in permission. Origin changes require the existing reconnection decision. A recipient lookup never signs the sender into that recipient's service. New grants and role credentials bind the exact accepted descriptor2/configuration bytes; old tokens are not migrated.

The [synthetic queue descriptor](examples/async-provider-descriptor.json) illustrates only discovery fields. It is not an active delegation, account login or device advertisement.

:::
