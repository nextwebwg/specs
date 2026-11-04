---
title: A small encryption-discovery service
order: 10.2
blurb: provider support hints · existing mail servers · separate setup
sectionNav: true
---

# A small encryption-discovery service

A mail provider can help clients find encryption support without replacing SMTP, IMAP or its existing mailbox service. It can add one small HTTPS service that answers whether it advertises Email/2 setup for a selected recipient. It does not need to hold decryption keys, run a control queue or implement relay addresses.

> [!ex] Add discovery beside an existing mail server
> Bob enables compatible setup with his provider. Alice's client asks Bob's domain whether setup is advertised. A positive answer helps her choose an enabled setup path; the clients still obtain and validate actual setup before releasing Alice's writing. If no usable setup is obtained, Alice sees the missing protection and can wait or authorize a permitted compatible copy.

**A support hint is not permission to encrypt.** It establishes neither usable keys nor identity verification, supported masking, current device availability or support in every app accessing the mailbox. Actual encryption and optional address protection retain their own validation and authorization.

## One independently adoptable role

The **Setup discovery** module has a provider role that publishes the hint and a client role that consumes it. An operator can implement the provider role as a small sidecar backed by its account opt-in records. No provider-control registration, OAuth account connection, bootstrap queue, key publication or mail-server rewrite is a dependency of this role.

This is a draft wire binding, `mail-support-v0`; the proposed `mail-support` well-known suffix is not registered. The [registration inventory](registration-inventory.md#domain-discovery-locations) records that external step. No deployed service or complete runtime implementation is claimed here.

A provider advertises an account only when its current operator/account policy permits publishing that the account supports an Email/2 setup path. It may decline to advertise even a capable account. The optional public endpoint deliberately reveals positive support to anyone who can query it. It is unsuitable where that disclosure is prohibited; publishing it is not mandatory for Encryption, Auto setup or ordinary mail carriage.

## Ask the selected mailbox domain

A client queries only for an explicitly selected recipient under its enabled discovery policy. Receiving or opening arbitrary mail does not initiate a query. Construct and validate the recipient with the [mailbox-address contract](mailbox-addresses.md), including quoted and internationalized local parts. Use the parsed lowercase A-label domain, not an MX target, display name, relay alias or URL supplied in message content.

Send an HTTPS POST to exactly `https://<recipient-domain>/.well-known/mail-support`, port443, without query, fragment or redirect. The recipient address is in the request body, not a URL or path. This discloses it to its own selected domain, the TLS endpoint and relevant infrastructure; it is not anonymous discovery. No message text, sender address, contact list, device key or conversation identifier enters this request.

Use the [provider-discovery transport and parsing protections](provider-discovery.md#discover-for-an-explicit-setup-purpose): TLS1.3 and selected-domain service identity, no cookies, ambient Authorization, client certificate or HTTP authentication, no redirect following, identity content coding, strict UTF-8 JSON with unique member names, bounded headers/body/depth and finite connection, deadline and retry settings. Apply its network-boundary checks to DNS candidates and the actual connected endpoint. The same65536-octet body and16-container-depth ceilings apply independently to requests and responses; the exact inventories below permit much smaller normal messages. These are protocol limits, not deployment quotas.

Both sides use `Content-Type: application/json` and `Cache-Control: no-store`. The server does not enable cross-origin browser reading or invoke another URL. No access credential, sign-in redirect or account challenge is part of this binding. Rate limiting and abuse controls remain finite operator policy; they cannot change a rejected query into a claim about account existence.

::: {.details summary="Exact request, response and unavailable outcomes"}

The request is a JSON object with exactly these two required string members. Null, missing, extra or duplicate members and other versions are invalid.

| Member | Value |
| --- | --- |
| `version` | `"0"` |
| `recipient` | Exact canonical bare mailbox, whose parsed domain equals the selected HTTPS domain |

A valid supported response is HTTP200 with exactly these two required string members:

| Member | Value |
| --- | --- |
| `version` | `"0"` |
| `support` | `"advertised"` or `"not-advertised"` |

`advertised` means that the domain currently permits publishing setup support for this recipient. It is not a key, handshake result or guarantee that an automatic response will be granted. `not-advertised` deliberately combines nonexistent, unsupported, private, disabled and otherwise unadvertised accounts. It makes no assertion that the mailbox exists or does not exist. For a valid request these negative categories use the same response status, member inventory and body bytes; do not add category-specific diagnostics, redirects or account-dependent response headers. Implementations must also address distinguishable lookup timing and operational side channels in their deployment evidence; matching bodies alone does not prove enumeration resistance.

Invalid syntax, a wrong-domain recipient or unsupported version receives HTTP400 with no account-specific body. A denied or limited public query may receive403 or429; temporary service failure may receive5xx. Clients treat all of those,404/410, a timeout, invalid JSON, TLS failure, redirect or any response outside this binding as **unknown/unavailable**, never as `not-advertised`. A valid Retry-After can delay eligible work under bounded local policy; it cannot authorize repeated disclosure indefinitely.

The response is the observational result of that exact outstanding HTTPS request to the authenticated selected domain. Concurrent queries retain their own recipient association; results must not cross recipients or accounts. There is no response signature, reusable credential, publication sequence, long-lived capability lifetime or remote transaction to retry in this profile. A replayed recorded body outside its authenticated request cannot update current support. Repeating an eligible query is a new observation, not a new email or setup authorization. Retained local history is diagnostic evidence, not continuing authority.

:::

## Continue with actual setup

A positive hint can help select an already enabled [ordinary-mail setup exchange](mailbox-setup.md) or a separately available [provider bootstrap](bootstrap.md). It cannot itself activate either mechanism, select an undeclared endpoint or bypass its identity, authentication, disclosure, replay and lifetime rules. Actual clients can also obtain setup without this service through their independently authorized mechanisms.

A negative hint or failed query cannot erase usable accepted setup, revoke a device, reset a pin, overwrite current identity or change a valid already prepared delivery. A client with independently usable material can continue under that material's owning rules. Otherwise show protection as unestablished for this send while enabled setup proceeds or ends; do not claim the account can never encrypt. No unreadable encrypted test is sent to an unsupported client.

If protected preparation remains unavailable, [delivery policy](delivery-policy.md#check-protection-before-releasing-content) decides whether to wait or use an already permitted ordinary/hosted mode. A sender can explicitly authorize mixed protection after seeing the per-recipient plan. The hint supplies no downgrade permission. Sender masking, recipient masking and independent verification stay separately determined.

## Acceptance boundaries

A provider-role claim tests actual domain-authenticated HTTPS requests, canonical addresses, opt-in changes, the uniform negative categories, malformed/wrong-domain requests, no ambient credentials or redirects, bounds, withdrawal and operational timing/disclosure. A client-role claim additionally tests concurrent recipient association, positive versus actual setup, expired/conflicting setup, independently usable cached setup during outage or negative hints, strict protection and explicitly authorized mixed delivery. No query alone releases human content, installs keys or creates a visible conversation contribution.

The [example](examples/encryption-support.json) and its focused fixture checks establish only documented field inventories and synthetic cases. They are not a running sidecar, actual TLS/abuse testing, account ownership proof, or complete discovery-to-encrypted-send conformance. Providers can add setup distribution, authorized control queues and private routing independently under their owning contracts; none is implied by this hint role.
