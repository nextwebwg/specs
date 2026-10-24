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

- [How the conversation works](#how-the-conversation-works)
- [Follow the encryption journey](encryption-journey.md)

For implementation, start with the [current protected client baseline](suite-profile.md#current-client-baseline): one asynchronous agreement with explicit reply destinations, required rich rendering, a common readable vocabulary and independently implemented interactions. Older numbered encodings retain their exact compatibility scope; no complete implementation or standards adoption is claimed.

## Status of this document {.sotd}

**Independent discussion draft.** Parts of the design have local implementations and tests; the complete system is not yet implemented or independently evaluated. A future standards venue has not been selected. The name is a proposed platform name, not an official version number assigned to Internet email.

The main reading path explains the experience. The architecture chapters define the exact requirements an implementer must follow. Expandable sections contain wire formats, algorithms and compatibility details; those requirements still apply when their disclosure is closed.

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

For an encrypted send, your app first finds the recipient's authorized devices and obtains the public setup information it needs. Compatible apps can [exchange setup through ordinary email](mailbox-setup.md) while your writing stays private. An optional [four-step address round trip](mailbox-return.md) also supplies receiving setup in both directions when the provider cannot establish how the setup email reached the inbox. Upgraded providers can exchange that information separately, avoiding setup emails in the inbox. Then your app encrypts the message and sends it through email infrastructure.

If setup cannot finish, your writing waits. You can decide whether a recipient may instead receive ordinary email, a hosted link, or must use a compatible app. Those choices have different privacy consequences; the app must not quietly make the choice for you.

Encryption protects message contents. Additional address-protection features can hide personal addresses from some systems carrying the mail. Neither feature makes all delivery metadata disappear or proves a new contact is who they claim to be.

[Follow the encryption journey](encryption-journey.md), including the everyday experience, adding a device and recovery.

## Add a device without starting over

Scan a pairing code and approve the new device on an existing device authorized to add devices. The app brings across the security setup for your contacts and prepares the new device to send encrypted mail using its own keys. You should not have to re-verify every unchanged contact.

Copying saved messages is separate from this setup. A new device can be ready for future encrypted email without possessing old messages or the keys used to carry them. Lost-device recovery also distinguishes recovering readable correspondence from authorizing a replacement device.

## Adoption can happen gradually

One app can make old email easier to read. Compatible apps can add structured replies and rich interactions. Encryption and provider-assisted setup add further capabilities. Personal-address protection can improve as providers adopt the necessary relay rules.

These are independent capabilities within one specification, not a promise that every app displaying “Email/2” implements every feature. An indicator must describe the protection actually used for a message.

[Read the client and provider adoption paths](adoption.md).

::: {.details summary="Architecture: protocols, modules and exact behavior"}

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
- [Optional provider negotiation](provider-negotiation.md) explains how upgraded services can obtain fresh device evidence outside the inbox. [Service discovery](provider-discovery.md) defines domain delegation and native client registration; [exchange authorization](provider-grants.md) defines account links and separate peer credentials.
- [Private addressing](private-routing.md) separates personal addresses inside encryption from authorized provider relay addresses used for delivery; [route authorization](relay-routes.md) binds account permissions, peer approval and delivery proofs.
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
