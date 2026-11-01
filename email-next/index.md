---
title: Email/2
order: -1
layout: proposal
stamp: Independent discussion draft
eyebrow: Email/2 · Experimental protocol suite
sectionNav: true
---

# Email/2

Email that feels like a conversation, across the addresses and providers people already use.

- [See a conversation](#how-the-conversation-works)
- [Follow the everyday encryption journey](encryption-journey.md)
- [When a recipient is not ready](delivery-policy.md#per-recipient-outcomes)
- [For email client developers](adoption.md#email-client-adoption): use existing mailboxes and discover protection before sending.
- [For email server and service developers](adoption.md#email-server-adoption): start with a small discovery service alongside the existing mail server.

## Status of this document {.sotd}

**Independent discussion draft.** Parts of the design have local implementations and tests; the complete system is not yet implemented or independently evaluated. A future standards venue has not been selected. The name is a proposed platform name, not an official version number assigned to Internet email.

The [module guide distinguishes existing standards from experimental Email/2 extensions and unresolved research](modules.md#existing-standards-and-experimental-designs). Implementation and testing status are recorded separately.

Follow this short introduction:

1. [See a conversation below](#how-the-conversation-works): replies and answers stay connected to the messages they belong to.
2. [Follow the everyday encryption journey](encryption-journey.md): send the first message, add a device and understand recovery.
3. [See what happens when a recipient is not ready](delivery-policy.md#per-recipient-outcomes): choose whether that delivery waits or uses an alternative you permit.

You can leave the implementation disclosures closed for this tour.

**For developers:** the [client and mail-service adoption paths](adoption.md) explain where to begin. The developer reference below links to exact protocols, rendering rules and acceptance requirements. Requirements inside a closed disclosure still apply to implementations.

## How the conversation works

You write to a person, reply to a particular message, or answer a question with a button. Your app keeps the conversation in order and handles encryption when the people involved support it. You do not have to learn how encryption keys work.

Email/2 is a proposed shared set of rules for making that work between different apps. It combines existing email delivery and established security protocols with new rules for conversations and rich messages. It is not a new email service you must join.

::email-conversation

## Replies have a place

A discussion reply identifies the message it answers. A private reply starts its separate protected conversation; any source connection kept by the client stays local unless deliberately shared. The app builds the conversation from the messages in your mailbox, instead of making you read another copy of the entire history beneath each reply.

When you reply to something earlier, that connection stays visible. When you forward one message, you do not automatically send along the whole conversation. Older email can still appear in the same reading view; cleanup remains reversible when the app has to infer what was quoted.

[Read about messages and replies](messages.md), or [how existing email is displayed](rendering.md).

## Rich messages have shared rules

Email/2 apps share a defined set of HTML and CSS features, so a message has a predictable presentation. Questions, answer buttons, images and attachments have defined meanings too. A button can answer within the conversation or, when explicitly configured, submit an answer to a connected service. Simply opening an email never presses it.

Older apps receive a readable version when that delivery is permitted. Supporting an older app does not let an Email/2 app skip the shared rendering rules.

## Encryption happens before the writing leaves

For an encrypted send, your app first finds the recipient's authorized devices and obtains the public setup information it needs. Compatible apps can [exchange setup through ordinary email](mailbox-setup.md) while your writing stays private. Upgraded providers can exchange that information separately, avoiding setup emails in the inbox. Then your app encrypts the message and sends it through email infrastructure.

If setup cannot finish, your writing waits. You can decide whether a recipient may instead receive ordinary email, a hosted link, or must use a compatible app. Those choices have different privacy consequences; the app must not quietly make the choice for you.

Encryption protects message contents. Additional address-protection features can hide personal addresses from some systems carrying the mail. Neither feature makes all delivery metadata disappear or proves a new contact is who they claim to be.

[Follow the encryption journey](encryption-journey.md), including the everyday experience, adding a device and recovery.

The [cooperating-service design](service-federation.md) explains the next delivery
path: your app can use your provider or an independent service, find a
correspondent through authorized discovery, and exchange encrypted packets
quickly through their services or an optional direct connection. The same
conversation and mailbox history survive a route change. Exact federation and
fast-delivery bindings are still being specified.

## Add a device without starting over

Scan a pairing code and approve the new device on an existing device authorized to add devices. The app brings across the security setup for your contacts and prepares the new device to send encrypted mail using its own keys. You should not have to re-verify every unchanged contact.

Copying saved messages is separate from this setup. A new device can be ready for future encrypted email without possessing old messages or the keys used to carry them. Lost-device recovery also distinguishes recovering readable correspondence from authorizing a replacement device.

## Adoption can happen gradually

One app can make old email easier to read. Compatible apps can add structured replies and rich interactions. Encryption and provider-assisted setup add further capabilities. Personal-address protection can improve as providers adopt the necessary relay rules.

These are independent capabilities within one specification, not a promise that every app displaying “Email/2” implements every feature. An indicator must describe the protection actually used for a message.

[Read the client and provider adoption paths](adoption.md).

## Why another encrypted-email standard?

**Email/2 makes the whole conversation work together:** finding compatible devices, protecting the first message, adding a phone, handling a late reply and keeping years of correspondence readable. Encryption is part of that experience, rather than a separate task the person has to manage.

::: {.details summary="Comparison with earlier approaches and security limits"}

Existing encrypted email already protects messages. [PGP/MIME](https://www.rfc-editor.org/rfc/rfc3156.html) and [S/MIME](https://www.rfc-editor.org/rfc/rfc8551.html) define established ways to sign and encrypt mail. [Autocrypt](https://docs.autocrypt.org/level1.html) makes key exchange automatic over existing email. Email/2 builds on those lessons: its contribution is a shared conversation platform with defined behavior across apps, devices and providers.

> [!ex] Alice writes to Bob for the first time
> Alice uses Bob's existing address and presses Send. If both apps support the required setup and their policies allow it, they exchange public security information before releasing her writing. Bob receives the protected message in his conversation, answers its question and later adds a phone by scanning a pairing code. Neither person copies a key or changes email provider. If setup cannot finish, Alice's writing waits; it does not quietly leave unencrypted.

The difference is what the standard asks every participating app to do together:

- **Beyond an encrypted message format.** PGP/MIME and S/MIME define how to sign and encrypt mail. Email/2 also defines the surrounding conversation: discovering compatible devices, authorizing a new phone, handling delayed delivery, identifying replies and rendering rich content consistently. Existing products can assemble these features; Email/2 makes their shared behavior part of the contract.
- **Beyond opportunistic key exchange.** Autocrypt Level 1 already automates key distribution through existing email providers. It focuses on protection against passive collection and can recommend unencrypted delivery to avoid unreadable mail. Email/2 defines an eligible setup exchange before releasing the first human message, separates automatic setup from independently verified identity, and makes an encryption-required send wait when protection is unavailable. Two compatible clients can start over ordinary email; upgraded providers can improve setup and private routing later.
- **An evolving conversation, built on existing cryptography.** MLS supplies asynchronous group key agreement, forward secrecy and post-compromise security; these are existing MLS properties, not Email/2 inventions. Email/2 defines how to use that protocol with email identities, authorized devices and delayed messages, and keeps readable correspondence separate from short-lived delivery secrets. It also defines reply relationships, quotation boundaries and interaction meanings so the protected conversation remains useful across apps.

The intended advantage is a reason to adopt the client for everyday email, plus a path to private conversations as correspondents upgrade. The protocol leaves room for different apps and business models; it does not require everyone to join one encrypted-mail service.

**Choose protection before sending, without choosing everyone’s provider.** The client shows the intended protection for each recipient: end-to-end content encryption, independent identity verification, and sender or recipient address masking through authorized relays. These are separate capabilities, not different names for one lock. Missing or pending evidence stays visibly unresolved. Under the [delivery policy](delivery-policy.md), the sender can require protection and wait, or permit an eligible ordinary-email or hosted alternative. A downgrade is an explicit or remembered disclosure choice, never a consequence of a timeout. If any copy is ordinary email, encrypted copies elsewhere do not make the contribution confidential.

This is a shared contract that different clients and providers can implement. Automatic setup should remove routine key-handling work between compatible endpoints; it cannot make an arbitrary older client understand Email/2 or make unavailable protection appear ready.

| Approach | What it contributes | What Email/2 defines around it or chooses differently |
| --- | --- | --- |
| [PGP/MIME](https://www.rfc-editor.org/rfc/rfc3156.html) and [S/MIME](https://www.rfc-editor.org/rfc/rfc8551.html) | Signing and encrypting MIME messages; existing clients can automate parts of their setup. | A joined contract for setup, device authority, evolving conversations, presentation and failure handling. Its selected encrypted conversation protocol is MLS, rather than a new PGP/MIME or S/MIME encoding. |
| [Autocrypt Level 1](https://docs.autocrypt.org/level1.html) | Automatic, decentralized key distribution over existing mail, with an explicitly passive-attacker threat model and usability-driven encryption recommendations. | An enabled exchange before the first human message, explicit identity assurance and authorized device changes. An encryption-required send waits when protection is unavailable. Automatic first contact still does not establish independently verified identity. |
| [Messaging Layer Security](https://www.rfc-editor.org/rfc/rfc9420.html) | An established protocol for asynchronous group key agreement and evolving secrets. | The surrounding email contract: who may use a device key, how setup travels, how delayed deliveries become one conversation, and how readable history survives without retaining every transport secret. MLS alone does not supply an email client. |

Encrypted-mail services already offer some of these choices. For example, Proton Mail documents [encryption indicators in its composer](https://proton.me/support/encryption-lock-meaning), [external PGP interoperability, including WKD](https://proton.me/support/encryption-lock-meaning), and [password-protected browser access](https://proton.me/support/password-protected-emails); it also permits [ordinary external email](https://proton.me/support/how-to-use-pgp). Email/2 does not claim these features are unique. It specifies cross-provider setup, per-recipient delivery choices and independently indicated content, identity and routing protection as an interoperable contract, rather than relying on one service’s product behavior. Hosted access retains its own disclosure model and is not automatically equivalent to endpoint-only encryption.

Email/2 follows the usability and authenticated-content lessons in [RFC 9787](https://www.rfc-editor.org/rfc/rfc9787.html). Its [security profile](security-profile.md#relationship-to-encrypted-email-guidance) and [mixed-delivery policy](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status) explain deliberate differences from that guidance. Earlier systems are not inherently incapable of a good experience; this proposal makes the integration a shared contract instead of leaving each product to assemble its own.

The boundaries remain visible. Encryption is not independent identity verification. Providers still observe some routing and timing information. A compromised endpoint can expose its readable history, and first contact can remain vulnerable to identity substitution without independent verification. [Security and discovery](security.md) defines these limits. The [encryption journey](encryption-journey.md) explains the experience and the [adoption path](adoption.md) describes how clients and providers can participate.

:::

::: {.details summary="Developer reference: protocols, modules and exact behavior"}

For implementation, start with the [current protected client baseline](suite-profile.md#current-client-baseline): one asynchronous agreement with explicit reply destinations, required rich rendering, a common readable vocabulary and independently implemented interactions. Older numbered encodings retain their exact compatibility scope; no complete implementation or standards adoption is claimed.

The main reading path explains the experience. The architecture chapters define the exact requirements an implementer must follow. Expandable sections contain wire formats, algorithms and compatibility details; those requirements still apply when their disclosure is closed.

- [Modules and automatic protection upgrades](modules.md) defines independent client/provider capabilities, short terms and icon meanings within one specification.
- [Protected conversation agreement](suite-profile.md) fixes the protected core and shared optional interaction modules; [design resolutions](design-resolution.md) tracks the remaining questions and evidence.
- [Client behavior and conformance](client-behavior.md) defines the complete conversation flow, required components and observable client behavior.
- [Messages and interactions](messages.md) defines questions, answer buttons, attachments and readable fallbacks.
- [Reply content and quotation boundaries](reply-content.md) identifies new writing and quoted passages through a chunk index and matching HTML Microdata.
- [Rendering and existing email](rendering.md) defines presentation and reversible cleanup of old conversations.
- [Delivery protection and fallback](delivery-policy.md) defines what happens when recipients support different protection levels.
- [Mailbox addresses](mailbox-addresses.md) defines internationalized and quoted address spelling, equality, safe display and transport requirements.
- [Freshness and revocation knowledge](freshness.md) defines cached continuity, recent account assertions, live device evidence and use-time checks.
- [Security and discovery](security.md) explains automatic encryption and its trust boundaries.
- [Cooperating services and live connections](service-federation.md) separates private discovery, offline setup, service federation, optional direct connections and durable delivery outcomes.
- [Optional provider negotiation](provider-negotiation.md) explains how upgraded services can obtain fresh device evidence outside the inbox. [Service discovery](provider-discovery.md) defines domain delegation and native client registration; [exchange authorization](provider-grants.md) defines account links and separate peer credentials.
- [Private addressing](private-routing.md) separates personal addresses inside encryption from authorized provider relay addresses used for delivery; [route authorization](relay-routes.md) binds accountable source permissions, inbox-provider route issuance and delivery proofs.
- [Encrypting the first message](first-contact-setup.md) keeps the writing private while automatic provider-assisted setup runs, then releases the first encrypted human message; the [automatic exchange](bootstrap.md) defines who may ask, how providers verify authority and what setup may be returned. Complete joined implementation remains required.

The [baseline](baseline.md#protocol-suite) names the incorporated standards and the new bindings between them. The [design inventory](design-resolution.md) records unresolved internal work. The [coverage table](interoperability.md#contract-coverage-and-remaining-decisions) separates specified behavior from demonstrated implementation.

:::

::: {.details summary="Implement the experimental protocol"}

- [Rich messages and scoped resources](rich-messages.md)
- [Interaction state and conflicts](interaction-state.md)
- [Event identifiers and exact references](event-identifiers.md)
- [Event encoding](event-encoding.md)
- [Answers sent to a service](service-answers.md) and [connecting a service account](service-authorization.md)
- [Event media-type registration proposal](media-type-registration.md)
- [Experimental passive discovery binding](passive-discovery.md)
- [Deferred form operation exploration](form-operations.md)
- [Transport and delivery](transport.md)
- [Selected managed-conversation security profile](security-profile.md)
- [Protected private copies](private-copies.md) and [managed presentation](managed-presentation.md)
- [Identity continuity and devices](identity-lifecycle.md)
- [Identity-state records](identity-state.md)
- [Mailbox associations](mailbox-association.md)
- [Capability discovery](capability-discovery.md)
- [Group conversations](group-conversations.md)
- [HTML and CSS presentation profile](presentation-profile.md)

:::

::: {.details summary="Check inherited standards, evidence and remaining decisions"}

- [Existing email and proposed extensions](baseline.md)
- [Standards audit inventory](audit-inventory.md)
- [Section-by-section review index](audits/index.md)
- [Validation and experiments](validation.md)
- [Interoperability and remaining decisions](interoperability.md)

Autocrypt supplies prior art for distributing keys through existing mail; SecureJoin explores verified introductions. Signal's protocols and MLS address session establishment and evolving keys. These are sources for the security design, not interchangeable components whose combination is automatically secure.

:::
