---
title: Modules and automatic protection upgrades
order: -0.6
blurb: one specification · independent capabilities · automatic upgrades · honest indicators
sectionNav: true
---

# Modules and automatic protection upgrades

Email/2 is one specification with a shared conversation model and independently supported modules. Clients and providers can adopt it in stages. They discover the capabilities needed for a particular exchange, automatically use the supported combination permitted by the sender's policy, and report the protection actually achieved.

> [!ex] Better protection without changing the address you type
> Alice and Bob use compatible clients over ordinary email providers. Their clients can encrypt after acquiring usable setup material. Later, their providers add private routing. The next eligible send uses authorized relay addresses outside the encrypted package, while both people still compose and read personal addresses. No one has to copy aliases or switch to a different edition of Email/2.

The **Conversations** base covers the [client conversation behavior](client-behavior.md): address-book presentation, thread/reply relationships, retained source, reversible interpretation of old messages and the required finite HTML/CSS presentation. It does not promise encryption, provider-assisted setup or address masking. Ordinary-mail attribution remains ordinary-mail attribution; the base cannot manufacture authenticated principals or activate protected operations from unverified metadata.

Optional modules have complete dependencies. A client implementing encryption must implement its identity, device, storage, cryptographic and protected-message rules; a provider carrying ciphertext need not hold decryption keys. Optionality is permission to omit a module, not to implement half its safety boundary and claim it.

## Modules and responsibilities

These are short human-facing names. The owning contracts define machine encodings and requirements; these labels are not newly registered protocol tokens.

| Module | What it adds | Required participants and dependencies |
| --- | --- | --- |
| Conversations | The base conversation view, reply targeting and defined presentation | Client; source-preserving mailbox carriage. Protected effects require the relevant protection module. |
| Encryption | End-to-end protected contributions to authorized recipient devices | Sending and receiving clients implement the [protected conversation core](suite-profile.md); ordinary providers can carry the opaque messages. Setup material and current authority must be usable before release. |
| Auto setup | Content-free automatic acquisition of recipient setup before sending the first human message | Enabled clients and authenticated provider control under [first-contact setup](first-contact-setup.md) and the exact [bootstrap contract](bootstrap.md); complete joined implementation remains required. Cached or passive evidence remains a separate available path. |
| Sender masking | Shared authorized outer From and opaque failure routing | Originating provider or selected relay and sending client, under [private routing](private-routing.md) and [route authorization](relay-routes.md); Encryption is required for the protected personal-author display. |
| Recipient masking | Opaque SMTP destination without a personal-address forwarding hop | Recipient provider or selected receiving relay, sending client and recipient authorization, under private routing and route authorization; Encryption and exact route-use permission are required. |
| Verification | Independent confirmation of the selected correspondent identity | Client and the explicitly selected [verification mechanism](mailbox-association.md#independent-verification-remains-separate). Encryption, a certificate or alias possession alone does not establish this assurance. |
| Answers | Questions with predefined answers that produce structured conversation replies | Both clients support `question` and `answer` together in the selected protected application. [Service actions](service-answers.md) additionally need their own explicit agreement and endpoint authorization. |
| Reactions | Add or withdraw a reaction on an exact contribution | Both clients support `reaction` and `reaction-withdraw` together under [reaction state](interaction-state.md). |
| Corrections | Authenticated correction of a person's own plain-text contribution | Both clients support `edit` under [edit state](interaction-state.md); no arbitrary rich edit is implied. |
| Encrypted backup | Portable encrypted historical correspondence and recovery | Archive writer/reader and independent recovery kit under [archives](encrypted-archives.md), with [collections](archive-sets.md) where used. Managed storage is optional. Backup never restores live identity authority. |

A provider can implement carriage, automatic setup, sender masking or recipient masking without implementing all client modules. An Encryption client need not implement a provider control service or every interaction. A module claim states its actor role and tested dependencies. “Email/2” with a module list is meaningful; an unqualified claim that every feature works is not.

The [complete protected conversation bundle](suite-profile.md) is the combination with all three optional interaction modules. It is an interoperability target, not the admission price for every Email/2 implementation. The base client still requires the defined HTML/CSS presentation; modularity does not introduce a text-only conversation client class.

## Independent guarantees, not one security score

Content encryption, routing privacy and correspondent verification answer different questions. They are not one sequence of increasingly strong encryption. In this draft the Encryption module selects one exact MLS version and cipher suite. There is no invented second encryption-strength level. A future cryptographic choice must define its actual guarantee, dependencies and authenticated negotiation before receiving another label.

Sender and recipient masking are independent: either can be available without the other. Independent identity verification can be absent even when content and both personal addresses are protected. Providers still know account/routing mappings; masking does not promise provider anonymity or defeat timing/size correlation.

Use numbered levels only if a future capability defines strict cumulative requirements. Do not call unrelated combinations “Level 1” and “Level 2”. This specification uses named capabilities instead.

## Capability negotiation and automatic step-ups

Discover support at the actor that owns it. Device-signed evidence determines a receiving device's protected application support; provider-authorized evidence determines relay/control support. A provider's promise cannot upgrade every client on an account, and a client cannot authorize an arbitrary provider alias.

For a new protected conversation, the [suite selection algorithm](suite-profile.md#module-agreement-and-common-operation-selection) selects the shared protected core and optional interactions from current signed device agreements. Provider service capabilities are checked separately. A conversation's chosen application remains exact; receiving a new feature claim cannot silently change established group authority or interpretation.

For each prepared delivery:

1. Resolve the selected sending account, intended recipients, current identity/association evidence and authorized receiving devices. Keep the human draft private while required setup runs.
2. Resolve the sender's effective content/fallback policy, address-privacy requirements and verification requirements independently. No capability advertisement changes those permissions.
3. Prefer end-to-end delivery when usable under that policy. Within an encrypted delivery, independently select supported and authorized sender masking and recipient masking. Where the effective policy permits routine automatic upgrade, use newly available protection without another alias-selection prompt.
4. Hold a delivery if any required capability or evidence is unavailable. A remembered policy may permit a less private envelope, ordinary email or a particular hosted model; if so the plan and sent record must reflect that actual exposure. A timeout or failed signature never supplies fallback permission.
5. Freeze the contribution, encrypted personal addresses, exact application, selected routes, supporting evidence and disclosure plan. Apply the [address-swap sequence](private-routing.md#when-the-addresses-change) and current serialized release checks. A changed or revoked dependency requires reevaluation before release.

An automatic upgrade applies to the next unsubmitted delivery. It does not rewrite already sent copies, recall a leaked address or turn old plaintext into ciphertext. An exact retry preserves its prepared bytes and route identity; changing route/mode follows the owning replacement/conflict rules. Upgrading one recipient cannot conceal ordinary or hosted exposure elsewhere in a mixed contribution.

## Short terms and icon meanings

A support page can list module capabilities. A composer shows the planned delivery state; sent history shows recorded outcomes; a received message shows only guarantees the receiver can establish. Do not use a product's capability icon as proof of a particular message's protection.

| Short term | Suggested icon description | Meaning when shown as an achieved message state |
| --- | --- | --- |
| Encrypted | Closed padlock | The displayed contribution was accepted under the end-to-end protection contract. It does not mean every other copy was encrypted. |
| Sender masked | Person silhouette with a cut-out outgoing arrow at the chest and a cut-out lock overlay | The recorded originating projection used the authorized sender-masking route. State the tested boundary; the provider still knows the account. |
| Recipient masked | Person silhouette with a cut-out incoming arrow at the chest and a cut-out lock overlay | The recorded destination route used the authorized opaque recipient path, without claiming privacy on uninspected later hops. |
| Verified identity | Person with a check mark | The selected independent verification evidence applies to this identity and stated scope; expose its source and limits on inspection. |
| Answers | A small choice/button symbol | The current shared application supports predefined structured answers. This is an interaction capability, not a security guarantee. |
| Reactions | A reaction face or small reaction symbol | The current shared application supports reaction and withdrawal. |
| Encrypted backup | Archive box with a padlock | In a capability view, encrypted backup is supported; a completed-backup state requires an actual authenticated complete selected archive/collection result. |

These descriptions define meaning, not mandatory artwork. Icons need accessible names and an inspectable explanation; color alone is insufficient. Routine composition need not repeat long security prose. Pending, unavailable and conflicted evidence must not look like an achieved guarantee. Verification and routing details remain available without flooding the message with boilerplate.

## Prior art

[JMAP RFC8620 §2](https://www.rfc-editor.org/rfc/rfc8620.html#section-2) defines a required core capability and a discoverable capability map; [§3.3](https://www.rfc-editor.org/rfc/rfc8620.html#section-3.3) lets a request state the capabilities it uses. This is a close precedent for one protocol framework with explicit supported components.

[SMTP RFC5321 §2.2](https://www.rfc-editor.org/rfc/rfc5321.html#section-2.2) and [§4.1.1.1](https://www.rfc-editor.org/rfc/rfc5321.html#section-4.1.1.1) provide another precedent: service extensions are advertised through EHLO. [XMPP service discovery](https://xmpp.org/extensions/xep-0030.html#info) similarly identifies features supported by a server or client entity. These are architectural precedents, not imported Email/2 wire formats or evidence that a capability advertisement itself grants security authority.
