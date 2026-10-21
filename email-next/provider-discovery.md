---
title: Finding a provider service
order: 10.25
blurb: account setup · authenticated delegation · native client registration
sectionNav: true
---

# Finding a provider service

A client can learn where a mail domain offers an Email/2 control service without putting an address in a public lookup. It asks the selected domain for a small service record, checks that domain's HTTPS identity, and retains the exact delegation. Signing in and authorizing a particular peer are later, separate steps.

> [!ex] A custom-domain account
> Alice connects her existing `alice@example.org` account. During explicitly enabled provider setup, the client asks `https://example.org/.well-known/email2-provider` for service locations. The domain delegates to `https://mail-service.example`. Alice sees that service when she connects it. Her mailbox password and existing access tokens are never sent to the discovered location.
>
> The domain record does not contain Bob's keys or establish his identity. Alice's client still needs independently accepted device evidence and the permission required for a particular exchange.

> [!note] Proposed discovery profile
> `email2-provider-discovery-v0` selects account-domain delegation and native public-client registration. The well-known suffix and profile identifier are draft allocations, not registered names. The [configured queue contract](provider-control.md) remains unchanged. The [public grant profile](provider-grants.md) separately defines account/device links and pair-specific queue credentials. The [unknown-peer bootstrap contract](bootstrap.md) separately defines first-contact authority. Joined implementations remain unfinished; discovery alone does not make a service publicly interoperable.

## Discover for an explicit setup purpose

Account-setup discovery starts from an account the person has explicitly connected or selected, using its retained domain spelling. The separate [first-contact flow](first-contact-setup.md) may also discover the domain of an explicitly selected recipient under enabled secure-setup policy. Neither path starts from arbitrary incoming content, an HTML link, a signature block, an MX target or an HTTP authentication challenge. A client may remember the person's permission to refresh this account's provider setup.

Use the [canonical mailbox-address contract](mailbox-addresses.md), including internationalized and quoted local parts. Select the parsed lowercase A-label domain; an `@` inside a quoted local part is not a domain boundary. Only that domain enters discovery URLs. No local-part normalization, address-literal lookup or inference from a display name is permitted. Validation unavailable under the selected IDNA provider holds this extension without preventing separate ordinary-mail use.

Fetch exactly `https://<selected-domain>/.well-known/email2-provider`, using the proposed [RFC8615 well-known suffix](https://www.rfc-editor.org/rfc/rfc8615.html#section-3), at port 443, without a query, fragment, mailbox address, Authorization header, cookies, ambient client certificate or HTTP authentication. Do not follow redirects. TLS 1.3 and the [service identity contract](service-answers.md#establish-the-protected-connection) apply, with the original selected domain as the DNS-ID reference. Neither DNS resolution nor a certificate-selected name changes that reference. A CNAME does not authorize a different HTTP origin.

Only a 200 `application/json` response with identity content coding can supply a record. Reject compressed representations, duplicate JSON names, invalid UTF-8, unknown fields and bodies larger than 65536 octets; JSON container depth is at most 16. Enforce response-header and connection budgets before parsing. Servers use `Cache-Control: no-store`; clients request no-store and do not obtain the record from an unauthenticated cache. Client and server implementations retain finite connection, deadline and retry settings rather than claiming this representation limit bounds all network work.

A 404 or 410 means that this fetch has no usable public delegation. A timeout, TLS failure, 429, 5xx, redirect or invalid representation means unavailable or invalid, not permanent lack of Email/2 support. None authorizes plaintext delivery, clears a previous service binding, or changes a peer's identity. Apply Retry-After where valid, bounded local backoff otherwise; setup failure never starts a mail probe.

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

## Register and sign in through the selected service

This section applies only to connecting the person's own account, never to recipient bootstrap. A recipient's descriptor cannot trigger OAuth registration or sign-in.

The service origin is the OAuth issuer in this version. Obtain its [RFC8414 authorization-server metadata](https://www.rfc-editor.org/rfc/rfc8414.html#section-3) from `service + "/.well-known/oauth-authorization-server"` through the same credential-free, redirect-free transport rules. Require exact issuer equality. Unknown metadata extensions may be ignored; they cannot replace selected fields or install credentials.

Metadata must advertise distinct canonical same-origin `authorization_endpoint`, `token_endpoint`, `registration_endpoint` and `revocation_endpoint`; `response_types_supported` including `code`; `grant_types_supported` including `authorization_code` and `refresh_token`; `token_endpoint_auth_methods_supported` including `none`; `code_challenge_methods_supported` including `S256`; `authorization_response_iss_parameter_supported:true`; and both exact scopes `email2.provider.link` and `email2.provider.manage` in `scopes_supported`. Each selected list is an array of unique nonempty ASCII strings. Additional advertised supported values do not select them. Absent requirements leave this profile unavailable; do not infer support from an endpoint's name. No received `jwks_uri`, documentation link or signed-metadata field is fetched by this profile.

[Dynamic client registration](https://www.rfc-editor.org/rfc/rfc7591.html#section-3) supplies a client identifier without requiring every email client developer to arrange credentials with every provider. This profile selects unauthenticated registration for a public native client. The provider can enforce finite rate and capacity limits, but cannot advertise this public profile while requiring an undisclosed initial access token, developer allowlist, software statement or public-client secret. Registration establishes no trusted application brand, human identity, mailbox authority or Email/2 authority.

::: {.details summary="Native registration and authorization binding"}

POST `application/json` to the exact selected registration endpoint, with no Authorization header or ambient credentials. The request has exactly:

```json
{
  "redirect_uris": [
    "http://127.0.0.1:1/email2/provider/callback",
    "http://[::1]:1/email2/provider/callback"
  ],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "email2.provider.link email2.provider.manage"
}
```

The literal port 1 registers the two exact host/path forms, not a port to bind or an address to visit. For the native authorization request, the server accepts an available ephemeral port under the [RFC8252 loopback exception](https://www.rfc-editor.org/rfc/rfc8252.html#section-7.3). There are no wildcard hosts, localhost resolution, custom schemes or embedded browser callbacks in this version.

Require HTTP201, no-store JSON and bounded uncompressed bytes. The response includes the exact registered metadata, a nonempty opaque ASCII `client_id` of at most 256 characters, and a nonnegative safe JSON integer `client_id_issued_at`. The scope may reorder the same two strings, with no duplicates, additions or omissions. Other client metadata is not selected. RFC7591 additional response members may be ignored, except `client_secret`, `client_secret_expires_at`, `registration_access_token` and `registration_client_uri`, whose presence rejects this selected unmanaged public-client registration. No returned URL can change the retained endpoints. This is a profile restriction, not a claim that those members are generally unsafe in OAuth.

Retain the original delegation bytes/digest, exact selected metadata bytes/digest, client ID and registered callback forms before sign-in. Reuse the resulting client registration for the same accepted delegation and metadata; do not register on every message or restart. A lost registration response may leave an unused public registration: it grants no account access. Retry only through bounded setup policy; do not guess the lost identifier or claim exact registration idempotency. No dynamic registration-update API is selected.

Use authorization code with S256 PKCE, external system browser, fresh state, exact issuer-response checking, the retained ephemeral loopback redirect, no public-client secret and no resource-owner-password grant. The [native service authorization rules](service-authorization.md#authorization-and-callback) define those mechanics and code/refresh uncertainty handling. Here the selected callback path and scopes are the provider values above, not service-button scopes. Tokens are opaque Bearer credentials restricted to this provider's management resources. Rotate public-client refresh tokens with reuse detection. A token response must return exactly the selected scope set. A provider-management token is never a queue-role credential and cannot be sent to a peer provider.

The server derives the authenticated account from its own login/consent system; a client-supplied address or OAuth client identifier cannot select it. The [public grant profile](provider-grants.md) defines account-to-device linking and peer-grant issuance, validating that account independently. This discovery chapter does not let successful sign-in substitute for those operations.

The client binds every pending attempt to both exact retained descriptor digests, issuer, client ID, callback, scopes and current local setup generation. Recheck these before navigation, callback consumption, token exchange and link completion. A changed binding or uncertain code/refresh redemption holds the attempt and requires reconnecting. Changes cannot clear uncertain queue operations or authorize a fallback.

Use the discovered `revocation_endpoint` under [RFC7009](https://www.rfc-editor.org/rfc/rfc7009.html#section-2), POST form-encoded `token`, `token_type_hint=refresh_token`, `client_id`, no client secret and no ambient credentials. The server revokes the entire management grant family and its access/refresh tokens. HTTP200 does not prove remote deletion or that every device learned of a revocation. An uncertain result leaves the local family disabled and permits bounded exact retry. Never forward an old token to a changed endpoint; retain its original trusted endpoint binding for an explicit disconnect attempt. Local disconnect stops new requests immediately. Its effect on queue grants is defined by the [grant lifecycle](provider-grants.md#credentials-and-revocation): management-family withdrawal invalidates every derived queue credential and blocks reads as well as writes.

The bearer risk described by [service authorization](service-authorization.md#implementation-evidence-and-boundaries) remains: possession of a stolen management token can exercise its authorized service grant. PKCE, a linked device signature and a registered client ID do not create per-request sender constraint. This chapter does not claim complete current OAuth security compliance or select a DPoP binding.

:::

## Evidence and remaining binding

The [discovery experiment](evidence/README.md#provider-discovery-and-public-client-registration) validates exact delegation bytes, authenticated-fetch provenance, current intervals, same-origin metadata, public registration and durable local update decisions. It tests restart, rollback, conflicting generations, origin confirmation, reset and concurrent stale decisions. Its trusted fetch input is supplied by a test adapter. It does not implement DNS, public PKIX, dynamic registration HTTP, system-browser login, token issuance or peer grants.

Required public-deployment evidence additionally includes domain delegation through real TLS, network-boundary/DNS changes, throttled registration, an actual external-browser sign-in, account-to-device linking, pair-specific credential issuance and revocation through the queue, provider changes, mailbox reassignment and a protected message following a successful exchange. The [grant binding](provider-grants.md) defines the next steps; complete public provider-negotiation claims still require their joined implementation and acceptance evidence. The unknown-peer bootstrap binding remains separate.

## Independent relay capability

The [relay module](relay-routes.md#discover-a-relay-service) reuses the transport, publication, native authorization and credential-isolation mechanics here under its own descriptor, scopes and namespace. Relay-only providers need not advertise or implement the queue. An existing queue registration or token does not silently gain relay administration/submission rights.
