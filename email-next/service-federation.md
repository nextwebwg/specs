---
title: Cooperating services and live connections
order: 10.15
blurb: private discovery · cooperating services · optional direct connections
sectionNav: true
---

# Cooperating services and live connections

**Service architecture within the Email/2 draft.** Discovery finds usable setup. A connection service helps apps reach each other. Delivery carries the encrypted message. These capabilities work together, but a service can adopt one at a time.

The architecture below defines their responsibilities. The exact federation, rendezvous and fast-delivery wire bindings are still being specified; these capabilities cannot yet be advertised as interoperable support. The existing [provider queue](provider-control.md), [ordinary-mail setup](mailbox-setup.md) and protected message agreements keep their current contracts.

Your app can use your email provider or an independent **home service** while you keep your existing email address. The service can help you connect without holding the keys that decrypt your messages. Your mailbox provider does not need to upgrade first.

## Your mailbox and your Email/2 service

The app can combine two connections into one conversation view:

- **Mailbox connection:** sends and retrieves email through your existing provider. Your address and mailbox can stay where they are.
- **Email/2 connection:** supplies the selected discovery, secure setup and live-communication capabilities. This service can be part of your email provider or an independent companion service.

An upgraded provider can supply both connections. With an unchanged provider, the app connects to the mailbox as usual and signs in separately to the companion service. Two correspondents can choose the same companion service, or their different services can communicate through the selected federation. They do not need to move their mailboxes or choose the same app.

> [!ex] The mailbox stays where it is
> Alice keeps her existing mailbox and connects her app to a companion service. Bob does the same. Their apps still send and retrieve ordinary email through their respective mailbox providers. The companion connection helps their authorized devices find setup and exchange encrypted traffic immediately when a usable live path exists.
>
> If Alice and Bob use the same companion service, that service can connect them. If they use different services, those services cooperate under the federation contract. A direct connection is an additional option; it is not required for the two-connection model.

The live connection can also support separately negotiated typing and optional read indicators. Those signals belong to the exact thread and audience; a private reply does not announce activity to the wider discussion. Their wire format and permissions need their own complete contract before clients advertise support. Delivery, mailbox read flags and discovery responses cannot substitute for them.

::: {.details summary="Two connections do not merge credentials or authority"}

A client using an independent companion keeps its mailbox and companion connections separately configured and authenticated. Mailbox credentials go only to their authorized mailbox endpoints. Companion credentials go only to that service's selected module endpoints; they are not forwarded to a correspondent's service. One provider may offer a shared sign-in experience, but each connection retains its own scopes, origin and authorization.

Connecting a companion does not grant it mailbox access, message-decryption keys, device-enrollment authority or permission to replace a pinned identity. Its own account/device link and any association with an existing email address follow their respective authorization contracts. A successful service login alone proves neither mailbox control nor a correspondent's identity. Routine use of an already authorized connection needs no new per-contact sign-in.

Using the same home service does not bypass device authentication, recipient policy, exact audience checks or content encryption. Using different services does not require either service to control the mailbox domain. A common discovery federation or an already accepted locator is still needed to find an independently chosen service.

The client assembles accepted messages from every authorized path using the same protected contribution and delivery identities. Changing the connection does not create a new conversation, turn an uncertain send into a failure, mark a message read or remove an intended recipient. Failure of an optional live service leaves separately authorized mailbox paths available; it cannot silently downgrade protection.

:::

> [!ex] Alice and Bob use different apps
> Alice adds Bob to a message. Her app finds Bob's signed setup through a service they can both use and checks whether it can encrypt for his authorized devices. If it can, it encrypts before sending.
>
> Their services can carry the encrypted packet immediately. If Bob is connected, his app receives it over its existing connection. If he is away, the packet waits in the agreed mailbox or storage path. Their apps can also agree on a direct connection when that is useful and permitted.
>
> Bob sees the same conversation whichever route the packet takes. The route does not change who wrote it, who may receive it or what it replies to.

There is no need to ask a public directory “is Bob online?” before sending. Good offline setup can enable encryption while he is away. A short-lived answer from one of his devices can help establish a live connection; it does not prove his identity merely because it arrived quickly.

## One address, several ways to find its service

The client begins with the complete recipient the person selected. It can use:

- A still-valid service binding it has already accepted for that correspondent.
- An authenticated service delegation from the recipient's email domain.
- A private lookup in a discovery federation configured for this account.

The proposed [discovery realm binding](discovery-realms.md) supplies a pinned configuration, admitted publishers and publication lifecycle for a bounded common index. [Private snapshot lookup](private-snapshot.md) defines complete acquisition on ordinary hardware, and [installation access](realm-access.md) defines its background resource admission. These are reference bindings with explicit scale, trusted-index and combined-compromise limits; their joined registration, allocation and Store acceptance prerequisites remain separate.

A **discovery federation** is a common index that accepts authorized publications from several services. Several mirrors can serve that same index. The client queries one eligible mirror; it does not send the recipient's address to every participating service.

> [!note] An unchanged domain cannot name an unknown service
> An ordinary email address does not reveal which independent service its owner joined. Without domain delegation or an earlier accepted locator, the two apps need a common discovery federation. Unrelated, unconfigured directories cannot automatically find one another just because both support Email/2.
>
> This does not require a single global operator. It does require declaring which federation supplies the lookup and how its configuration and participating publishers are trusted. Ordinary email remains the compatibility path when no shared discovery method is available.

The client should reuse accepted evidence when it remains eligible. If it checks more than one authorized source, a conflicting identity stays a conflict; the first or fastest answer does not win. An absent entry or failed request means that this path supplied no usable setup. It does not prove that the address does not exist, cannot encrypt or is offline.

## How Alice finds Bob before sending

The intended first-contact flow is:

1. **Bob connects his account.** His app connects to his mailbox and chosen Email/2 companion. The selected registration process verifies control of his email address and binds the publication to an authorized device. This can happen automatically under his account policy; Bob does not approve each future sender individually.
2. **His app publishes a signed service locator.** Registration evidence connects Bob's address, authorized devices and chosen service. The publication enters a discovery federation configured for his account, with its original validity and withdrawal rules. The companion need not operate his mailbox or own its domain.
3. **Alice enters Bob's address.** Her app uses eligible cached evidence, domain delegation or a private query to an already configured discovery federation. It looks up this selected recipient, without uploading Alice's address book or sending a setup probe into Bob's inbox.
4. **Alice's app validates the result.** It checks the original registration and device evidence, service authorization, identity continuity, supported capabilities and expiry. A directory cannot replace the identity Alice already trusts for Bob or turn mailbox control into verified personal identity.
5. **The app obtains usable encryption setup.** The selected private-discovery contract must cover complete locator/setup retrieval. If setup needs a one-use package, a separately authorized allocation reserves it before disclosure; that operation has its own metadata and privacy boundary. A support indicator alone is insufficient. Eligible prepublished setup can allow an encrypted first message while Bob's device is offline.
6. **Alice sends through an authorized path.** Her app encrypts for the eligible intended recipients and uses the selected mailbox or service-delivery contract. Their services can negotiate a permitted live path when their devices are connected. Typing and enabled read indicators then follow their own exact thread, audience and permission rules.

Alice and Bob can share a companion or use different companions that publish into a common discovery federation. Both clients need to know that federation's configuration beforehand, or have another accepted locator/delegation. Choosing a companion per account does not make unrelated directories automatically discoverable.

> [!note] Discovery and readiness stay separate
> Discovery has a bounded attempt, not an indefinite automatic wait. A missing entry leaves capability unknown. An exhausted package pool or unavailable service can leave a known-capable recipient pending. None of these outcomes proves Bob cannot encrypt.
>
> Required-protection messages stay pending until eligible setup is available or the sender makes a separately authorized permitted choice. Under an already permitted ordinary-send policy, the first human message can carry Alice's setup information so an upgraded recipient can begin the bounded automatic upgrade. This does not send background probes to legacy recipients or retroactively encrypt that first readable message.

These are the intended service and client responsibilities. The exact federation bootstrap, registration, private-retrieval and allocation bindings must be complete and tested before advertising this whole flow as interoperable support. Existing primitive experiments or a working same-service demo do not establish it.

::: {.details summary="Service delegation, federation bootstrap and registration authority"}

Domain discovery uses the existing parsed mailbox-domain and HTTPS delegation rules. Only the domain enters the initial discovery URL. A new binding owned by [service discovery](provider-discovery.md) must separately identify directory, rendezvous and ciphertext-delivery roles, their exact HTTPS origins and paths, protocol profiles, signing-key authority and validity. A shared origin does not merge permissions. MX records, CNAMEs, DKIM keys, diagnostic links and arbitrary redirects do not supply these roles.

A client-selected independent service can register a person's existing address after the selected own-account mailbox-control verification and authorized device publication succeed. Mailbox control is not independent personal identity and cannot defeat a malicious mailbox provider. The original verification evidence and its limits remain distinct from device signatures and correspondent pins.

Federation configuration must identify the realm, authenticated configuration history, admitted registrar authority, mandatory private-retrieval construction and parameters, evaluator key epoch, dataset verification/checkpoint keys, eligible mirror origins and validity. It comes from account configuration or an accepted configuration-update chain, not from incoming email or a failed lookup. A new trust root is a local account/configuration decision. Existing credentials remain restricted to their original purpose and origin.

A client distribution or account setup may supply an initial eligible federation configuration. Its exact bootstrap and authenticated update contract must identify the trust roots and complete retrieval profile; a familiar service brand is not a substitute. Different independent operators may serve the same configured index. An independently selected service becomes discoverable through that index only after its publication authority and the person's registration are admitted.

A federation may partition its implementation by email domain. Such a partition is a routing or isolation choice, not authority to represent that domain or select every account's companion. Two people with addresses at the same unchanged provider may choose different homes. Separate handlers or hostnames alone establish neither private lookup nor resistance to combined operator compromise; those properties depend on the selected construction and its stated trust assumptions. Do not derive an unconfigured backup authority from the mailbox spelling.

A registrar authorizes enrollment and publication. An index admits complete protected records and withdrawals. A mirror serves authenticated dataset material. None can replace a pinned principal or grant membership merely by returning an entry. The client independently validates the exact mailbox subject, enrollment authority, original device signature, identity continuity, current roles, selected application and all original expiry conditions.

Private requests must not disclose a plaintext recipient, predictable unkeyed address hash, draft or contact list. A private first lookup followed by a uniquely identifying public setup fetch does not satisfy complete private acquisition. The selected profile must account for both steps. Multiple opaque selectors needed to retrieve one selected recipient's object are not a contact-list upload.

A realm needs a complete interoperable cryptographic retrieval profile before advertising private discovery. A generic “private lookup” algorithm field is insufficient. Configuration/snapshot signatures do not prove registration truth, global freshness, authenticated absence or that a malicious server evaluated the exact committed dataset. The selected construction must state what is proved and what remains a trust assumption.

Publication changes retain original signed bytes, publication identity, generation and predecessor. Equal generation with unequal bytes is conflict. Withdrawals retain authenticated tombstones; expiry does not erase rollback evidence or contact pins. Address reassignment requires new enrollment assurance and explicit identity-continuity handling. Service migration retains signed handover and independently authorized destination acceptance; old tokens cannot migrate automatically.

Different realms need deliberate shared publication or an already accepted locator to interoperate. Clients do not crawl a realm graph. A failed mirror can cause bounded failover only within the already authorized realm, under the same epoch and attempt policy. It cannot reset a high-water mark or install a different evaluator key.

:::

## Connect through the services first

For most messages, the recommended fast route is:

`Alice's app → Alice's home service → Bob's home service → Bob's app`

Both apps use connections they opened themselves. That works with ordinary firewalls and mobile networks. The services carry the existing encrypted packet and never receive its content-decryption keys.

Alice's own service is her connection point, not an authority to disclose her recipient to arbitrary operators. The client performs the selected private lookup, or uses an independently specified privacy-preserving broker. An ordinary cleartext “look up Bob for me” request has a different disclosure contract.

The proposed [home-service rendezvous binding](rendezvous.md) defines device-signed homes, source dispatch and exact request-bound answers. Its native-module/reset, pending retrieval and preparation-route prerequisites remain explicit; it does not define content upload or advertise direct WebRTC.

When a live exchange is needed, Alice's app makes one authorized **rendezvous offer**. Bob's service can pass it to his permitted devices without publishing an online roster. One device may return a short-lived answer automatically under the account's existing policy. The clients validate the answer and their common capabilities before using the selected path.

The service's initial “accepted for processing” response does not say whether Bob exists or is online. A missing answer leaves this route unavailable or expired; encrypted mailbox delivery can continue if its own conditions are satisfied.

::: {.details summary="Rendezvous states, records and permissions"}

Rendezvous is an operation scoped to specific principals, devices and purpose. It is not a persistent global online/offline attribute.

| State | Transition | Required retained evidence |
| --- | --- | --- |
| Not requested | An authorized local setup/send operation needs a live exchange. | Exact recipient selection, purpose, original deadline, selected identity/setup and disclosure policy. |
| Offered | The client durably freezes and authenticates an offer before release. | Exchange ID, nonce, original bytes/digest, source/target principals and selected devices, service-delegation digests, grant/admission binding and offered capabilities. |
| Accepted for processing | The destination service admits the exact offer under current policy. | Immutable request and bounded status/replay record. This state reveals no public presence category. |
| Answer received | A permitted target device authenticates a response. | Exact request digest/nonce, actual answering device/current setup binding, selected route, handshake commitment and bounded validity. |
| Path usable | Both clients validate the selected answer and path against current authority and capabilities. | Exact authenticated transcript and connection binding. This does not replace native admission or content-release authorization. |
| Unavailable, expired, cancelled or conflicting | No eligible answer/path remains under the original attempt. | Original request, prior possible disclosure and reason. No new permission or automatic cleartext fallback. |

The existing [provider authorization](provider-grants.md) and [first-contact bootstrap](bootstrap.md) remain separate authorities. The proposed federated binding must define its own scoped grants and how they are obtained; none of the permissions below is implied by a retained queue credential.

An own-service credential is accepted only at its scoped own-service endpoint. A service-to-service credential authenticates the originating service and its allowed operation, not the end user's identity. A known-pair destination grant must bind the source service, actual initiating principal/device, destination account/target, operation and expiry. Unknown first contact follows its separate recipient-enabled bootstrap/admission rules. Installation evidence and a directory match cannot supply either permission.

The destination applies account/device policy, blocks, source-service admission and finite work limits before expensive or persistent work. HTTPS alone does not make an arbitrary service an admitted correspondent. No mailbox password, OAuth management token or installation credential is forwarded to a peer service.

Exact offer retries recover the same retained state. Unequal bytes under the same exchange identity are a conflict. A delayed answer, reconnect or retry cannot extend expiry, create another request or alter the selected protection policy. A service cannot manufacture a device answer or turn its own status response into key confirmation.

An account may have several authorized devices. Each answer retains the actual responding device and its own capabilities, identity evidence and validity. One answer is not proof that every device supports a feature. The sender must apply its selected device-target and freshness policy; required devices remain pending independently. No answer reveals the private group roster to uninvolved devices or services.

:::

## A direct connection is optional

The apps may additionally negotiate a direct WebRTC data channel. That can be useful for sustained exchanges or large resources. It is not necessary for end-to-end encryption or immediate delivery through the services.

Direct connections can reveal network addresses to the correspondent. A relay-only policy keeps direct candidates out of the exchange and uses an authorized relay instead. If direct connection setup fails, the apps continue on an already authorized encrypted service or mailbox route.

::: {.details summary="Direct-channel authorization and network boundaries"}

The selected WebRTC binding uses maintained ICE/STUN/TURN and data-channel mechanisms. Its offer/answer and selected DTLS fingerprint must be authenticated through the accepted Email/2 control context. Signaling-service control over a response does not authorize replacing the endpoint identity or fingerprint. The existing MLS packet remains protected above the data channel.

Before gathering or releasing candidates, the client applies IP-disclosure and network-boundary policy. Unauthenticated strangers must not receive host candidates merely because they asked whether an address supports encryption. A relay-only selection must not release direct candidates. Candidate handling cannot become an arbitrary internal-network probe.

The binding must define reliable channel/framing behavior, message/resource bounds, candidate limits, ICE restart/generation handling, consent expiry, simultaneous offers, relay credentials, backpressure and abort. A backend's unspecified defaults do not establish interoperability. A successful ICE check or data-channel write is not an authenticated durable message acceptance.

Direct-channel failure does not extend the original setup/delivery deadline or require a new authored message. Switching paths preserves the exact prepared packet where allowed; a different protected preparation follows the existing fresh-delivery authorization rules.

:::

## One message, even when it arrives by two routes

The same message may reach an app through the fast path and later through its mailbox. The client validates both, keeps their delivery provenance and displays one authored contribution. It uses the protected identities and exact authenticated contents, not the outer email Message-ID or an HTTP request identifier.

A network acknowledgement can mean several different things:

| Acknowledgement | What it means |
| --- | --- |
| Locally queued | This app durably retained the prepared work. |
| Service custody | The selected service committed the exact encrypted packet for the destination account and its declared retention/retrieval obligation. |
| Endpoint accepted | An authorized recipient device validated and durably committed this exact protected delivery. |
| Read | A separate optional, authorized receipt. None of the other stages implies it. |

Fast arrival on a phone must not make the message disappear from its agreed mailbox history. If the service cannot commit the required mailbox copy, SMTP delivery stays scheduled or the account uses an explicitly selected independent encrypted storage contract. A server can suppress a redundant SMTP copy only through an authenticated account-scoped match to committed custody and exact packet equality. An attacker copying a Message-ID cannot make a real delivery vanish.

::: {.details summary="Packet preservation, durable outcomes and asynchronous recipients"}

The fast carriage binding must specify reversible extraction of the complete original protected compound object, including its authenticated native/carrier dependencies and required resource bytes. It cannot send bare operation JSON that bypasses the selected mailbox protection profile. Transfers may differ only where the owning carrier contract permits it.

The existing [two-ledger algorithm](event-identifiers.md) remains authoritative. One authored identity retains immutable authored bytes and scope. Each protected preparation has its own delivery identity, original audience and native provenance. Exact transport retries retain those bytes and identity. A newly authorized preparation can preserve eligible authored bytes while receiving a fresh delivery identity. Authenticated unequal variants remain conflicts; untrusted outer IDs cannot reserve either namespace.

Custody receipts bind issuing service, destination account/route, original request/preparation, exact packet length/digest and retention scope. Endpoint receipts bind the actual authorized accepting device, original protected preparation/audience and durable acceptance. Receipt correlation cannot grant access to private scope or imply another device/recipient possesses the same history.

A lost response leaves possibly released work uncertain. Status reconciliation and exact retry must preserve the original attempt and prior disclosure. They cannot silently replace it, refresh authority or erase uncertainty. Timeout is not proof of nonreceipt. A later independently authorized preparation must retain that history and the original authored/scope identity where permitted.

Group readiness remains per intended recipient and device. Bob's ready path cannot remove Carol from the declared discussion, imply she received it, or expose a private copy. A later eligible delivery to Carol carries the same authored content only after its own current package, identity, audience and disclosure checks. Fast-path receipts are not one global group-delivered flag.

An ordinary legacy reader cannot display encrypted personal names or body unless it can decrypt them. The service must not reveal them merely to make the mailbox copy look familiar. Address protection, content encryption and lookup privacy remain independent capabilities.

:::

## Upgrade without waiting for every provider

A provider may add just domain delegation or a small discovery sidecar. A client can instead use an independent home service and a configured federation. Later upgrades can add authorized rendezvous, durable fast delivery, address protection or direct channels. These are separately negotiated capabilities within one Email/2 specification.

No service location or support indicator promises every capability. Clients select an exact common application, encryption agreement and transport binding. A missing optional capability leaves existing compatible paths available. An unavailable path never silently weakens required protection.

Unknown discovery need not send an automatic encryption probe into an older inbox. Under an already permitted ordinary-send policy, the first human message can carry its sender's setup information. An upgraded recipient can then follow the separately authorized bounded negotiation rules. Earlier readable messages do not become encrypted retroactively. Required-protection sends stay held until suitable setup exists or the sender makes a separately authorized permitted choice.

::: {.details summary="Still needed before interoperable capability advertisement"}

The architecture fixes service roles, authority separation, progressive adoption and safe state outcomes. The following exact wire choices remain necessary:

- A complete production private publication/retrieval construction per interoperable federation profile. The [bounded snapshot reference](private-snapshot.md) specifies epoch/file rules and complete static acquisition but does not establish scalable production privacy or combined-compromise protection. Private membership lookup does not itself allocate a one-use package.
- Registrar admission, federation bootstrap/update authority, reassignment/migration and witness/consistency assumptions. Unconfigured realms are not universally discoverable.
- Exact descriptor role extensions, service-to-service authentication and known-pair/first-contact grant acquisition; no implicit reuse of old challenge-queue permissions.
- Offer/answer codecs, multi-device selection and exact transcript binding.
- Full fast-packet carriage, custody/endpoint receipt schemas, replay/status retention and atomic mailbox duplicate suppression.
- A complete optional WebRTC binding and declared IP-disclosure modes.

No profile can advertise complete support while these mandatory bindings are unspecified. Existing retained wire agreements keep their original meanings. Private lookup, combined-operator compromise resistance, independent implementation interoperability and security review must be qualified separately.

:::

## Related protocols

[Matrix federation](https://spec.matrix.org/latest/server-server-api/) provides precedent for separate client-to-service and service-to-service exchanges. [AT Protocol identities](https://atproto.com/specs/did) separate persistent identity from a movable service location. Their naming and authority models do not by themselves provide private discovery of unchanged email addresses.

The optional direct path draws on the [WebRTC protocol suite](https://www.rfc-editor.org/rfc/rfc8825.html), [data channels](https://www.rfc-editor.org/rfc/rfc8831.html), [ICE](https://www.rfc-editor.org/rfc/rfc8445.html) and [TURN](https://www.rfc-editor.org/rfc/rfc8656.html). These supply established connection mechanisms; Email/2 still needs the exact authorization, framing and receipt bindings described above.
