---
title: Email Next
order: -1
layout: proposal
stamp: Independent discussion draft
eyebrow: Email Next · Experimental specification
sectionNav: true
---

# Email Next

Email that reads like a conversation: answers beside questions, one-click answer buttons, predictable presentation, and encryption that clients establish automatically.

> [!ex] The same conversation in different clients
> Alice asks **Which day works?**, with **Tuesday** and **Thursday** as choices. Bob selects Thursday in his upgraded client. Carol sees an ordinary email listing the choices and replies, “Thursday works for me.”
>
> Alice sees Bob's answer beside the question. Her client can suggest that Carol's reply belongs there too, while keeping Carol's words and making the interpretation visible. Nobody needs a new address. Carol can participate without installing anything.

Email Next starts with existing email delivery. Upgraded clients add explicit relationships and richer controls; upgraded providers can add discovery and protocol-message handling. A useful conversation view does not have to wait for everyone to upgrade.

- [Messages and interactions](messages.md) defines questions, answer buttons, attachments and readable fallbacks.
- [Rendering and existing email](rendering.md) defines presentation and reversible cleanup of old conversations.
- [Delivery protection and fallback](delivery-policy.md) defines what happens when recipients support different protection levels.
- [Security and discovery](security.md) explains automatic encryption and its trust boundaries.
- [Optional provider negotiation](provider-negotiation.md) explains how upgraded services can obtain fresh device evidence outside the inbox.

## Status of this document {.sotd}

**Independent discussion draft.** The requirements describe proposed behavior, with exact experimental profiles in their owning chapters. A future standards venue has not been selected. Local reference implementations and tests support selected profiles; they do not establish adoption, independent interoperability or production security assurance.


## What changes

Email already reaches people across providers. Its presentation often makes readers work through copies of earlier messages to find what changed. HTML support varies, an answer rarely identifies its question, and encryption often asks users to manage keys themselves.

This proposal adds contracts for those missing relationships and behaviors:

::: targets
Conversations
: Each contribution identifies what it replies to. Repeated quotations can collapse without losing the original message.

Interactions
: Questions and predefined answer buttons have explicit meanings. Readable text and HTML carry the same meaning for older clients.

Presentation
: A finite, testable HTML/CSS profile defines what clients support and what they do with unsupported content.

Protection
: Clients establish encryption automatically. The sender chooses whether incompatible recipients receive ordinary email, hosted access, or wait for a compatible endpoint.
:::

These capabilities are independent. An account is not simply “modern” or “legacy”: it can have several devices, different clients and different available features.

| Capability | What has to upgrade? |
| --- | --- |
| Reconstruct an old conversation | One reading client |
| Send a predefined answer with one button press | Participating upgraded clients; others retain readable fallback |
| Render the defined HTML/CSS profile | The receiving renderer |
| Deliver encrypted content automatically | Compatible endpoints with sufficient identity and key material |
| Discover capabilities before an earlier exchange | An agreed discovery service |
| Route negotiation outside the ordinary inbox | Provider support |

The [adoption plan](adoption.md) separates client and server implementation paths and describes the acceptance tools needed to make both practical.

## Encryption without routine key management

Automatic key exchange over existing email is the initial direction. Routine conversation should not need separately shared passwords, manual key management or repeated encryption toggles. Provider upgrades can improve discovery and support stronger checks without requiring a new address or abandoning email transport.

When a recipient cannot decrypt, the sender's policy decides the outcome. Ordinary email and hosted access are explicit permitted tradeoffs, not equivalent forms of end-to-end encryption. The client can remember a policy, but must show the resulting exposure. An enforced-encryption policy cannot silently weaken after a discovery or delivery failure.

The [delivery chapter](delivery-policy.md) defines these choices, including mixed recipients and partial delivery. The [security chapters](security.md) define the checks needed before a client can claim protected delivery.

## How this specification uses existing email

Email Next extends existing formats and delivery mechanisms. MIME already carries alternate representations, and reply headers already connect messages. The draft keeps inherited behavior where it serves the new model and identifies proposed changes explicitly.

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
