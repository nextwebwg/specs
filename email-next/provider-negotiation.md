---
title: Optional provider negotiation
order: 10.2
blurb: fresh device evidence · separate control queue · account authorization
sectionNav: true
---

# Optional provider negotiation

A provider can help two clients exchange fresh key information without sending extra messages into either inbox. The provider carries the exchange; each client still decides whether the other device is authorized.

> [!ex] Both clients are available
> Alice's client already recognizes Bob's device, but needs fresh discovery evidence. It places a signed challenge in Bob's authorized control service. Bob's client retrieves it and returns a signed advertisement tied to that challenge. Alice validates the response, then uses the normal encryption protocol to establish the conversation.
>
> Bob's ordinary email client receives no probe or automatic reply. If Bob's upgraded client is unavailable, Alice's existing delivery policy determines whether to wait or use a permitted alternative.

> [!note] Proposed provider extension
> This chapter selects the roles and exchange lifecycle for a configured experiment. The [configured wire profile](provider-control.md) defines HTTP routes, signed records and retries. Configured HTTPS exchange and subsequent MLS admission have [local acceptance evidence](evidence/README.md#configured-provider-and-admission-report). The [public discovery profile](provider-discovery.md) selects domain delegation and native client registration. The [public grant profile](provider-grants.md) defines account/device linking and queue-credential issuance; joined deployment evidence remains absent. No provider capability identifier is ready for interoperable advertisement. The [ordinary-email discovery profile](passive-discovery.md) remains available independently.

## What the provider supplies

The service holds a small, authenticated queue separate from mailbox storage. A request identifies one initiating device and one target device. The target retrieves the request and writes one response into the same exchange. The initiator retrieves that response. There are no callback URLs, automatically generated emails or public online lists.

A successful exchange supplies **fresh evidence from one device**. It does not prove that every device on the account supports Email/2, that all account revocations are known, or that an encrypted conversation is ready. Encryption readiness remains a result of the [security profile](security-profile.md).

## Authorize the service and the devices separately

Before contacting a service, the client needs an authenticated account configuration binding the exact HTTPS service location to the intended service account. An email address, MX record, message link or provider brand is insufficient. The retained configured experiment installs this binding through trusted test-account configuration. The current public path uses the independently validated [descriptor2](provider-discovery.md#discover-the-asynchronous-agreement), account/device link and [grant2](provider-grants.md#authorize-asynchronous-pair-exchanges); a discovered location alone is not an account configuration or grant.

Access also requires a service grant naming the account, initiating device, target device, permitted operations and expiry. Each participant authenticates with its own credential restricted to its role. Permission to place a challenge does not include permission to answer it. Mailbox passwords and credentials issued for another service are not accepted as substitutes.

The service account and Email/2 identity are different authorities. An administrator can grant access to the queue; that action cannot enroll a device, replace a correspondent's established identity or authorize reading their encrypted history. Each client independently checks the accepted identity state and mailbox association before using the exchanged evidence.

> [!ex] Different providers
> Alice can contact Bob's service using a grant issued for that service. The response remains there for Alice to retrieve. Neither provider forwards Alice's credential to another provider. The domain discovery and native registration steps are [selected separately](provider-discovery.md); the [grant profile](provider-grants.md) defines account linking and pair-grant acquisition separately from the configured adapter.

Reassigning or reprovisioning the service account must invalidate its previous grants. It must not silently repin an established Email/2 identity to the new mailbox owner.

The [first-contact flow](first-contact-setup.md) additionally permits a content-free automated setup before the first human message. The [public bootstrap binding](bootstrap.md) supplies its separate authority; an unknown peer cannot enter this configured pair-grant queue without authorization. Recipient opt-in and a device policy can authorize automatic setup responses without a human email reply.

## One challenge, one response

| Step | Required behavior |
| --- | --- |
| Create | The initiating device records a fresh exchange identifier and nonce, exact participants, service and grant, intended identity states, purpose and expiry, then signs the request. |
| Admit | The service validates the credential, role, account scope, request limits and lifetime before storing the immutable request. |
| Answer | The target independently verifies the request and current device authority, then signs one response bound to the exact request and nonce. It durably saves that response before submitting it. |
| Validate | The initiator matches its outstanding request, verifies the target signature and current authority, and validates the enclosed passive advertisement and any admission material. |
| Finish | A response closes the exchange. An unanswered exchange expires. Neither outcome automatically creates another exchange. |

A response contains the existing signed passive advertisement for the exact target device, with optional single-use MLS admission material. Its validity cannot outlive the challenge or the evidence it carries. The response must identify the exact requested identity state and device binding. If the target has moved to another state, it does not sign a claim that the old state is current. Independent identity evidence must resolve that change before a new challenge can succeed.

The signature covers the original encoded record, including its record kind, participants, service, grant and request binding. A service status response authenticates only what the service reports; it cannot replace this device signature. The [wire profile](provider-control.md) defines exact encodings, signature context and validation order for configured experiments.

::: {.details summary="Retries, expiry and interrupted exchanges"}
The service stores an admitted request immutably. Retrying identical bytes retrieves the same exchange; different bytes under the same identifier are a conflict. The same rule applies to the one response. Retries cannot extend the lifetime, enqueue another request or create new admission material.

The responder saves the exact signed response before upload. If the upload's result is lost, it retries those bytes rather than generating another key package. A duplicate response never generates an acknowledgement response. The initiator likewise keeps its original challenge through restart.

The service must retain enough replay state to reject reused identifiers throughout the admitted validity and retry windows. Admission limits must bound that storage; discarding replay protection to admit more work is not allowed. Expired or invalid responses do not invalidate unrelated outstanding exchanges or replace accepted identity state.

Clients treat a timeout as an incomplete exchange. They preserve the sender's delivery policy and do not automatically retry through plaintext email. The wire profile specifies pagination, retention, clock handling, finite limits and recovery behavior. These choices must be tested together rather than inferred from HTTP status alone.
:::

## From evidence to encryption

For a new conversation, a validated response can provide the target's MLS KeyPackage. The client still follows the security profile's invitation, membership and confirmation rules. This control exchange does not reserve a package or bypass its single-use checks. An existing session does not consume a new package merely to demonstrate device freshness. The [freshness contract](freshness.md) defines exact per-device evidence, explicit age policy, credible clocks and release-time checks; live response never means complete knowledge of unseen remote changes.

The first provider experiment keeps invitations and encrypted contributions on the existing mail delivery path. The optional queue accelerates discovery while preserving that transport. Carrying invitations or application messages through the queue would require a separately specified payload and authorization contract.

**A fresh signed response is not key confirmation.** HTTP success, a provider's delivery status and the target's discovery signature cannot substitute for the cryptographic protocol's validation. The client must not display the conversation as ready for protected content until those checks succeed.

## Presence and privacy

There is no online/offline flag, last-seen field or public account lookup. Opening a control connection does not authorize a provider to publish availability. A response does reveal to its authorized initiator that the target device processed this challenge during its validity period; the grant interface must explain that disclosure.

Providers can observe participants, timing, public discovery evidence and message sizes. The exchange does not hide that metadata. It carries no conversation text, contact list or private key. Revoking a grant stops future service access but cannot retract a response already obtained by a peer.

## Acceptance and adoption

Providers can add this service after demonstrating reliable ordinary-message carriage. Clients can adopt it independently of their conversation renderer, but must retain ordinary-mail discovery and enforce the same identity and fallback rules on both paths. See the separate [client and server adoption paths](adoption.md).

The provider acceptance adapter must exercise two independently running clients, durable service storage, restart and lost responses. It must cover wrong accounts and roles, revoked grants, changed identity state, altered records, response replay, identifier conflicts, expired exchanges, resource exhaustion and interrupted pagination. A successful challenge must produce no SMTP submission or mailbox mutation. An offline target must preserve the sender's protection policy.

A complete positive test must then use the returned admission material in an actual protected conversation. Merely retrieving a signed response does not demonstrate automatic encryption. Public interoperability additionally requires the common service-discovery and credential-issuance bindings; configured test accounts do not establish those capabilities.
