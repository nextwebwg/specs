---
title: Existing email and proposed extensions
order: 0
blurb: existing rules · upgrade boundaries · extensions
sectionNav: true
---

# Existing email and proposed extensions

Email/2 is a proposed protocol suite for an email conversation platform. It combines inherited email standards, explicit selections and constraints, and new extensions. Each chapter identifies the existing rules it relies on and the behavior this profile adds or narrows. Expandable disclosures carry the inherited detail so readers can follow the proposal without reading a second copy of the email standards.

## The Email/2 protocol suite {#protocol-suite}

Email/2 defines the bundle and the integration contract. An implementation needs to know which protocols it must implement, which exact profiles and versions apply, how their inputs and outputs connect, and what happens when a peer supports only part of the suite. Merely implementing one incorporated standard does not establish Email/2 conformance.

| Layer | Incorporated standards or defined contract | Binding in this draft |
| --- | --- | --- |
| Mail carriage and readable alternatives | SMTP, Internet Message Format and MIME | [Transport](transport.md) and the selected content carriers preserve existing delivery and define structured content alongside readable alternatives |
| Conversation and interaction data | Event identity, exact references, messages, questions, answers and reactions | [Event encoding](event-encoding.md) and each operation's owning contract define interpretation and authority |
| Required client presentation | HTML and CSS under a finite selected vocabulary | [Presentation profile](presentation-profile.md) defines supported content, filtering and resource boundaries |
| Protected conversations | Messaging Layer Security (MLS), required ordinary sender streams and optionally managed quorum groups, with the selected credential/application/lifecycle rules | [Security profile](security-profile.md) binds the cryptographic protocol to the conversation model; implementing MLS alone is insufficient |
| Capability and device evidence | Selected signed discovery and identity contracts | [Passive discovery](passive-discovery.md) and [identity lifecycle](identity-lifecycle.md) define scope, freshness and transition authority |
| Provider-assisted services | Separately supported discovery and control exchange | [Provider negotiation](provider-negotiation.md) and [provider control](provider-control.md) improve participating deployments without becoming prerequisites for all ordinary-mail carriage |

These links own the exact versions, requirements and failure behavior; this table does not widen their negotiated profiles. The HTML/CSS presentation profile is a required client component, as defined in [required presentation](presentation-profile.md#required-presentation). Plain-text alternatives support existing clients and do not substitute for that component. The [client contract](client-behavior.md) collects the required components and observable behavior. Remaining joined bindings and acceptance evidence must be completed before a general Email/2 conformance claim is meaningful. Until then, implementations identify the exact experimental profiles they support. The [module framework](modules.md) defines one Email/2 specification with a base, independent client/provider capabilities and automatic protection upgrades. The [protected conversation agreement](suite-profile.md) binds the Encryption core, indexed replies and shared optional interaction modules. Implementing and testing the exact claimed combination remains a prerequisite for advertising it; every client/provider need not implement every module.

Prior art is distinct from incorporation. Reviewing S/MIME, PGP/MIME, Autocrypt or Signal protocols does not make all of them required or interchangeable components of this suite. The selected agreement names the actual protocol and distinct ordering rules used for ordinary streams and managed groups.

> [!note] What “unchanged” means
> An unchanged rule remains authoritative in its source specification, with applicable updates. Email/2 does not replace that text. A new restriction or interpretation is an explicit proposed change, even if it is convenient for implementations.

> [!note] Draft status
> The proposed extensions are still under development. Source reviews and unresolved dependencies are documented in the [standards audit](audits/index.md).

## What has to upgrade?

Email/2 separates the message a person reads from the service that carries it. Existing email architecture already distinguishes these layers and permits asynchronous delivery without both people being online. [RFC5598 §§1–1.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-1) describes that architecture; it is informational, not a replacement for the protocol specifications.

> [!ex] Two upgraded clients, ordinary mail providers
> Alice and Bob can exchange a supported structured contribution through ordinary mail transport. A richer interaction needs compatible endpoints and a valid protection context; it does not inherently require every relay to understand the interaction.

The proposed upgrade path preserves offline delivery. An optional live exchange can accelerate discovery or strengthen an existing trust relationship, but absence of simultaneous presence does not authorize plaintext fallback. Provider features need their own negotiated contracts. A provider advertising support does not prove that every recipient device can interpret or decrypt a contribution.

### Forwarding through a list or gateway

> [!ex] Bob forwards Alice's correction to a team list
> The list may deliver Bob's forwarded message to Carol, but that does not make Carol an authorized recipient of Alice's original encrypted contribution. Bob's forwarding action and Alice's original authorship remain separate facts.

For this proposed profile, a list or gateway that needs plaintext must be an explicitly authorized participant or act under a separately authorized disclosure. It cannot acquire decryption rights merely by appearing on the delivery path. A transformation that changes an authenticated event creates a different record; it must not retain the original author's verified attribution for the changed content. If a gateway cannot preserve the protected representation, apply the selected delivery policy rather than silently converting it to plaintext.

### An alias is a route, not a key binding

> [!ex] One address delivers to two mailboxes
> A team alias forwards Alice's message to Bob and Carol. That routing rule does not prove that Bob and Carol are one account, or that both can decrypt a contribution addressed to the alias.

The proposed encrypted audience must resolve to explicitly authorized principals. If several delivery addresses belong to the same verified account, the identity profile can establish that relationship. If they represent different accounts, their membership and key distribution must be handled separately. Unknown alias expansion does not justify a claim that every destination supports encryption. Preserve the selected fallback policy when that cannot be established.

## Relationship to existing standards

| Classification | Meaning | Presentation |
| --- | --- | --- |
| Inherited | Existing behavior is used without a proposed semantic change | Brief summary and expandable source mapping |
| Extension | New behavior uses an existing extension mechanism | Visible proposal plus exact source mechanism |
| Profile | The proposal selects or constrains options already permitted | Visible restrictions and compatibility consequences |
| Proposed replacement | Behavior conflicts with or replaces an existing rule | Exact affected section, replacement behavior, and migration analysis |
| Unresolved | A design choice remains open | Explicit question in the affected chapter |

This document structure does not amend existing IETF standards. Proposed replacements would require coordination with the relevant standards venue.

### Relationship to secure-email guidance

[RFC 9787](https://www.rfc-editor.org/rfc/rfc9787.html) supplies implementation guidance for end-to-end email. Email/2 carries forward its separation of authenticated content, ordinary surrounding mail and user-visible protection. The proposed managed-group protocol has different cryptographic machinery; it does not redefine S/MIME or PGP/MIME processing.

The differences that affect an implementer's behavior are explained where they apply:

| Behavior | Email/2 choice and rationale |
| --- | --- |
| Protection across recipients (§§3.2 and 9.6) | [Explicitly permitted mixed delivery](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status) supports gradual adoption. An ordinary copy still discloses the contribution; encrypting other copies does not undo that disclosure. |
| Selecting a related MIME body (§7.1) | [Honor an explicit related root on receipt](messages.md#related-root-traversal-for-protected-legacy-messages), even when it is not the first child, to avoid selecting a resource as the body. New composition puts the root first. |
| Blind recipients (§9.4.1) | [Separate managed-group deliveries](delivery-policy.md#why-the-managed-group-model-differs-from-rfc-9787) keep a blind recipient out of the visible group's membership. The certificate-based construction remains a separate profile. |

The [section-by-section comparison](audits/e2e-guidance.md) records inherited guidance and boundaries as well as departures. Requirements for a particular wire profile remain in its owning chapter.

## Existing mechanisms and their limits

| Existing rule | Meaning | Email/2 use |
| --- | --- | --- |
| RFC 5322 §3.6.4 | Message identity refers to a particular version; ordinary trace additions need not change it | Keep message-version identity distinct from authenticated event identity |
| RFC 5322 §3.6.4 | Multiple parents are possible in `In-Reply-To`; construction of multi-parent `References` is not defined | Project conversation relationships explicitly into legacy thread fields |
| RFC 6854 §2 | Originator fields can use group syntax, including an empty group, under its applicability restrictions | Do not assume every displayed author yields one replyable mailbox or discoverable key |
| RFC 2046 §5.1.4 | Alternatives are ordered, equivalent representations with specified selection behavior | Define order and preserve a useful readable representation |
| RFC 2387 §§3–6 | Related parts form one compound object; the root and media type matter | Use a related HTML alternative with explicit root and scoped resources |
| RFC 2392 §2 | Existing `cid:` and `mid:` references address parts and messages | Use cid references for bundled resources; keep mid navigation distinct |
| RFC 2183 §2.8 | Unknown dispositions are treated as attachments | A new “control” disposition cannot promise legacy invisibility |
| RFC 5228 §4.4 | A configured Sieve rule can silently discard a message | Distinguish recipient/provider filtering from a sender's request to hide mail |
| RFC 6657 §§3–4 | New textual media types must define charset handling; plain-text defaults remain unchanged | Define charset rules in the media-type registration |
| RFC 9078 §§3–4 | Reactions already have a defined MIME disposition and processing model | Reaction integration must account for placement and target rules, not only emoji text |

::: {.details summary="Inherited message fields"}
The current proposal preserves the roles of `Date`, `From`, `Sender`, `Reply-To`, `To`, `Cc`, `Bcc`, `Message-ID`, `In-Reply-To`, and `References`. Date is a composition/submission-readiness time, not proof of delivery or a total ordering of events. Author, transmitting agent, reply address, and recipient are distinct roles.

Sources: [RFC 5322 §3.6](https://www.rfc-editor.org/rfc/rfc5322.html#section-3.6), [RFC 6854](https://www.rfc-editor.org/rfc/rfc6854.html).
:::

::: {.details summary="MIME composition: inherited mechanisms and proposed additions"}
Existing MIME supplies alternative representations, compound objects, body-part identifiers, and presentation hints. An Email/2 interaction type would add semantics inside that framework. Unknown multipart types fall back to mixed-part processing; unknown application data is not automatically a readable message. Related-part processing takes precedence over the contained disposition types for clients that understand the compound object.

The [message chapter](messages.md) defines mixed attachments around alternative representations, with related resources inside the HTML alternative. Compatibility with older clients depends on their MIME selection and preservation behavior; see [interoperability](interoperability.md).

Sources: [RFC 2046 §5.1](https://www.rfc-editor.org/rfc/rfc2046.html#section-5.1), [RFC 2387](https://www.rfc-editor.org/rfc/rfc2387.html), [RFC 2392](https://www.rfc-editor.org/rfc/rfc2392.html).
:::

## Extension definitions and registration

Names used in this editor's draft are proposals unless an existing registration is explicitly identified. Neither publication here nor successful local tests register a header field, media type or SMTP extension. A provisional registration would not constitute technical endorsement.

A field definition must specify its applicable protocol and location, grammar, cardinality, duplicate and malformed handling, author or intermediary authority, forwarding behavior, confidentiality exposure and signature coverage. Reusing a familiar name does not import identical semantics across mail, MIME and HTTP. A registration entry locates a definition; it is not proof that a received value is authentic.

For a proposed mail header, record whether it belongs to the trace block. An empty Trace value in an existing registry entry is unspecified, not an explicit negative classification. Trace classification does not make attacker-supplied header values trustworthy.

Registration procedures and revision dependencies are documented in the [header-registration audit](audits/header-registration.md).
