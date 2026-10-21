---
title: Email/2
order: -1
layout: proposal
stamp: Independent discussion draft
eyebrow: Email/2 · Experimental protocol suite
sectionNav: true
---

# Email/2

A protocol suite for interoperable email conversations.

> [!ex] The same conversation in different clients
> Alice asks **Which day works?**, with **Tuesday** and **Thursday** as choices. Bob selects Thursday in his upgraded client. Carol sees an ordinary email listing the choices and replies, “Thursday works for me.”
>
> Alice sees Bob's answer beside the question. Her client can suggest that Carol's reply belongs there too, while keeping Carol's words and making the interpretation visible. Nobody needs a new address. Carol can participate without installing anything.

Email/2 starts with existing email delivery. Upgraded clients add explicit relationships and richer controls; upgraded providers can add discovery and protocol-message handling. A useful conversation view does not have to wait for everyone to upgrade.

- [Explore the protocol suite](baseline.md#protocol-suite)
- [Read the message model](messages.md)

## Status of this document {.sotd}

**Independent discussion draft.** The requirements describe proposed behavior, with exact experimental profiles in their owning chapters. A future standards venue has not been selected. Local reference implementations and tests support selected profiles; they do not establish adoption, independent interoperability or production security assurance.


## Explore the suite

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

## What changes

Email/2 bundles selected standards and protocols into a common conversation platform: explicit reply relationships, identifiable authored and quoted content, predictable rich rendering, interactions and negotiated protection. It builds on existing email infrastructure so clients and providers can adopt it in stages.

Email already reaches people across providers. Its presentation often makes readers work through copies of earlier messages to find what changed. HTML support varies, an answer rarely identifies its question, and encryption often asks users to manage keys themselves.

This proposal adds contracts for those missing relationships and behaviors:

::: targets
Conversations
: Each contribution identifies what it replies to. Repeated quotations can collapse without losing the original message.

Interactions
: Questions and predefined answer buttons have explicit meanings. Readable text and HTML carry the same meaning for older clients.

Presentation
: A required, finite HTML/CSS profile is the shared presentation format for Email/2 clients. Plain-text alternatives serve existing email clients; they are not a substitute for Email/2 rendering support.

Protection
: Clients establish encryption automatically. The sender chooses whether incompatible recipients receive ordinary email, hosted access, or wait for a compatible endpoint.
:::

HTML/CSS presentation support is mandatory for Email/2 clients. Optional interaction modules, encryption and provider services are negotiated for their respective roles under the [module framework](modules.md). An account can have several devices and clients with different capabilities; one compatible client does not upgrade every client on that account.

| Capability | What has to upgrade? |
| --- | --- |
| Reconstruct an old conversation | One reading client |
| Send a predefined answer with one button press | Participating upgraded clients; others retain readable fallback |
| Participate as an Email/2 reading client | Required HTML/CSS renderer; plain-text-only rendering does not qualify |
| Deliver encrypted content automatically | Compatible endpoints with sufficient identity and key material |
| Discover capabilities before an earlier exchange | An agreed discovery service |
| Route negotiation outside the ordinary inbox | Provider support |

The [adoption plan](adoption.md) separates client and server implementation paths and describes the acceptance tools needed to make both practical.

## Encryption without routine key management

[Encrypted archives](encrypted-archives.md) preserve correspondence independently of live identity and storage subscriptions. Their [protection selection](audits/archive-protection.md) distinguishes the inherited file encryption from the new signed history container.

The [encryption journey](encryption-journey.md) defines setup, first contact, everyday sending, device changes and total-loss recovery, with mechanism coverage and failure cases.

Automatic key exchange over existing email is the initial direction. Routine conversation should not need separately shared passwords, manual key management or repeated encryption toggles. Provider upgrades can improve discovery and support stronger checks without requiring a new address or abandoning email transport.

When a recipient cannot decrypt, the sender's policy decides the outcome. Ordinary email and hosted access are explicit permitted tradeoffs, not equivalent forms of end-to-end encryption. The client can remember a policy, but must show the resulting exposure. An enforced-encryption policy cannot silently weaken after a discovery or delivery failure.

The [delivery chapter](delivery-policy.md) defines these choices, including mixed recipients and partial delivery. The [security chapters](security.md) define the checks needed before a client can claim protected delivery.

## How this specification uses existing email

Email/2 defines a protocol suite: a selected bundle of standards and protocols, their required versions and constraints, and the bindings that make them operate together. Its conformance contract must identify a required baseline and separately negotiated extensions. It supplies new contracts where the incorporated standards leave gaps. MIME already carries alternate representations, and reply headers already connect messages. The platform contract distinguishes three kinds of requirements:

- **Inherited standards:** existing rules that remain authoritative in their source specifications.
- **Profile requirements:** selected capabilities, versions and constraints that implementations must support together for a particular negotiated profile.
- **New extensions:** conversation semantics, content boundaries and other behavior that the inherited standards do not supply.

The name identifies this proposed platform, not an official overall version number for Internet email. Support is established by the exact negotiated profiles, not by a claim to support “Email/2” alone.

The main chapters explain behavior with examples. Expandable sections contain parsing rules, exact schemas and inherited compatibility details. Those details still apply; the disclosures let a reader follow the model before implementing every boundary.

> [!note] Audit and implementation status
> The [audit inventory](audit-inventory.md) distinguishes reviewed source text from dependency and implementation coverage. The [contract coverage table](interoperability.md#contract-coverage-and-remaining-decisions) identifies remaining internal work, while [external decisions](interoperability.md#external-standardization-and-adoption-decisions) cover venue, registrations and independent evaluation. No affiliation with or adoption by W3C, WHATWG or IETF is implied.

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
