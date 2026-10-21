---
title: Capability discovery and exchange decisions
order: 10
blurb: ordinary-mail bootstrap · provider upgrades · live exchange
sectionNav: true
---

# Capability discovery and exchange decisions

Before using a rich interaction or encryption, a client needs to know what the recipient can receive. **Discovery** supplies that information. It can begin with ordinary email or an authorized automatic setup exchange; provider upgrades can obtain setup before the first human message.

> [!ex] Learn through a normal conversation
> Alice emails Bob. Her upgraded client includes information about its supported features. Bob's next human-written reply can include his client's information. Once their clients have sufficient valid identity and key evidence, they can establish encryption automatically under their first-contact policies.
>
> This cannot encrypt Alice's first message to a key she has not obtained. Her policy determines whether that message goes as ordinary email, uses permitted browser access, or waits.

| Deployment | How clients learn | What it does not establish by itself |
| --- | --- | --- |
| Ordinary email | Passive advertisements travel with messages people send | A machine reply, invisible delivery, or encryption of earlier mail |
| Upgraded provider | An authorized discovery or control service supports exchanges outside normal inbox delivery | Device enrollment or support by every client using the account |
| Both endpoints available | A fresh authenticated exchange can confirm a session | Peer identity merely because someone is online |

Support is checked feature by feature and for the actual destination. A client may support answer buttons while lacking current encryption material. A provider may offer a control service while a legacy client still reads the same mailbox.

> [!note] Proposed decision contract
> This chapter defines how discovery evidence affects sending. The [experimental passive binding](passive-discovery.md) selects ordinary-email carriage, signed records and expiry rules for implementation work. Its media type is unregistered. The [optional provider extension](provider-negotiation.md) selects a separate control queue and device-challenge lifecycle. Its [configured wire profile](provider-control.md) defines the exchange; [domain discovery](provider-discovery.md), [public account/grant authority](provider-grants.md) and [unknown-peer bootstrap](bootstrap.md) are defined separately; their complete joined implementations remain unfinished. These requirements alone do not establish interoperable discovery.

## Bootstrap through ordinary email

An outgoing human-authored message may include a passive advertisement. Receiving it does not create a requirement to send a machine response. A subsequent human reply can carry the recipient's own advertisement, allowing compatible clients to establish protection under their first-contact policies.

For an unknown correspondent without previously obtained key material, this passive exchange cannot encrypt the first ordinary message to an unknown key. The sender can use permitted ordinary delivery, use permitted browser access, or hold content until suitable key evidence becomes available. The interface must state which happened; it must not retroactively describe earlier readable mail as encrypted.

A missing advertisement can result from a legacy client, stripping, forwarding, stale data or deliberate omission. It is not an authenticated refusal of encryption. Existing identity evidence and required-protection policies survive that omission.

::: {.details summary="Inherited email behavior"}
Normal delivery, MIME parsing and automatic-response rules continue to apply. `Auto-Submitted`, a null reverse-path, `NOTIFY=NEVER`, DSNs and MDNs do not establish sender-controlled invisible delivery. Reports also do not demonstrate endpoint presence or key possession. See the [automatic-response audit](audits/automatic-responses.md), [delivery-status extension audit](audits/dsn-extension.md) and [report-format audit](audits/dsn-format.md).
:::

## Choosing whose capability to check

> [!ex] A reply goes to a different address
> Alice's message asks Bob to reply to a shared support mailbox. Bob's composer can offer that destination, but it cannot reuse Alice's device keys or encryption capability as proof that the support mailbox can decrypt the reply.

Discovery follows the actual proposed recipient after ordinary reply composition and explicit audience choices. A Reply-To address is a proposed destination, not an identity-continuity proof. The sender must resolve its recipient identity and protection policy separately before sending. An unfamiliar destination remains visible in the send plan.

Return-Path, a bounce address, a relay greeting, a source IP address or a List-Id value MUST NOT substitute for an intended recipient principal or select that principal's encryption keys. To and Cc fields alone do not establish who received a message or who is authorized to receive a new contribution. Use the [delivery policy](delivery-policy.md) for mixed recipients and private copies.

A gateway removing an advertisement is indistinguishable from missing evidence at this layer. Preserve the existing protection policy and report missing capability evidence; do not interpret absence as permission to downgrade. These are proposed discovery requirements, not new meanings assigned to ordinary email headers.

## Provider upgrades and live sessions

An upgraded provider can carry negotiation through a separate control service. The client must establish that the service is authorized for the account and operation; an address or URL in a message is not enough. The [provider negotiation chapter](provider-negotiation.md) defines the proposed roles, device challenge and terminal exchange lifecycle. The requirements below apply to any eventual binding.

A live exchange adds fresh evidence when both sides are available. It becomes ready for protected content only after the selected cryptographic protocol validates the exchange and confirms the keys. An interrupted exchange leaves the last valid identity state intact.

:::: {.details summary="Provider control-channel contract"}

### Provider control channel

A provider upgrade may expose a control service separately from normal inbox delivery. Use requires an authenticated service binding and authorization for the addressed account, operation and reply destination. An arbitrary URL or address found in a message is not such a binding.

The receiving service validates scope, protocol version, size limits and authorization before admitting an exchange. Unknown or invalid input must not trigger a message to a claimed third-party destination. A response is bound to a locally recorded outstanding exchange; unsolicited responses cannot create an exchange or refresh its lifetime.

Each exchange has a profile-defined identifier, initiating principal, target principal, purpose, permitted response kinds, expiry and terminal outcome. A duplicate request may retrieve the same recorded outcome under the service's retry contract; it must not create another enrollment, key transition or response chain. A duplicate response does not cause an acknowledgment loop. After completion or expiry, further traffic cannot reopen the exchange without a separately authorized initiation.

The profile must define resource limits, retry timing, retention and replay behavior before deployment. These are implementation and protocol choices, not user-approved quotas. Authentication failures and unknown service support preserve the sender's fallback policy; they do not authorize ordinary-mail probes.

::::

:::: {.details summary="Live exchange, interruption and presence"}

### Live exchange and asynchronous delivery

Being online permits an authenticated fresh exchange; it does not authenticate the peer. Bind the exchange to the initiating and target principals, intended purpose, selected protocol version and negotiated capabilities. The selected cryptographic protocol must define transcript validation and key confirmation. An SMTP acceptance, delivery report or HTTP success response is not key confirmation.

Until the cryptographic exchange succeeds, no session is treated as ready for protected application content. On interruption, retain the last valid identity state and report the exchange as incomplete. Do not adopt partially received replacement keys or restart by sending plaintext. Another authorized route, including a profile-defined prekey exchange, may establish a session without requiring simultaneous availability.

Provider presence is optional and separately authorized. A service must not publish a person's availability merely because their device opened a control connection. Peers can establish a session without exposing a public online roster. A transport timeout is neither evidence that the person is offline nor withdrawal of their capabilities.

::::

## Evaluate each feature at send time

| Evidence state | Meaning | Permitted behavior |
| --- | --- | --- |
| Unknown | No usable assertion for this feature | Prepare compatible ordinary content or use separately permitted fallback. Do not probe by sending a supposedly invisible email. |
| Observed | A candidate assertion exists, without sufficient authority for the intended operation | Retain it. Apply the first-contact policy before using candidate encryption material; do not replace an established identity. |
| Usable | Validation, scope, version, freshness and identity requirements for this operation pass | Use the feature for the prepared delivery, recording which evidence justified it. |
| Stale | A previously usable assertion is outside its permitted freshness interval | Refresh through an authorized mechanism or hold affected work. Do not infer intentional withdrawal or permission to weaken protection. |
| Conflicted | Applicable evidence cannot be reconciled | Hold operations requiring the disputed authority. Preserve reading and other operations that do not depend on it. |
| Withdrawn | Authorized evidence removes the feature or device from future use | Stop new use within the withdrawal's scope and re-evaluate queued deliveries. Do not erase past attribution or infer a replacement identity. |

These are feature-decision results, not a single trust ranking. A destination may simultaneously have usable rendering support, stale encryption capability and a verified historical identity. Revocation and device removal follow the identity lifecycle contract; they cannot be simulated by a missing feature advertisement.

A send plan records the exact evidence and endpoint target set used to prepare it. Before submission after a material identity, capability or policy change, re-evaluate that plan. If its prerequisites no longer hold, wait, fail or prepare an explicitly permitted alternate delivery. Do not silently alter an already protected contribution or reuse its authorization for a different audience.

### Select a supported combination

A device’s capabilities describe combinations that work together: the event version, the protected payload format, the membership-ordering mode and the operations supported in that combination. Check the same combination for every intended device. Support advertised under another combination cannot fill a gap.

> [!ex] Supporting both formats does not mean supporting every feature in both
> Alice’s client can receive questions as raw structured events and attachments inside protected MIME. That does not mean it can receive attachments as raw events. If Bob supports questions only inside MIME, the two advertisements do not yet establish a shared question format.

Choose the required operations from the intersection for one exact combination. Record that selection with the devices and signed evidence that justified it. Adding a device requires support for the conversation’s existing selection; learning a newer capability does not change old messages or silently switch the conversation’s format. A different format needs an explicit new-conversation agreement or a separately specified authenticated transition.

The proposed version-2 capability binding expresses these combinations explicitly. Its implementation is in progress; earlier signed advertisement versions retain their existing meanings. A client must not advertise an operation merely because it can parse the format: receiving, validation, safe presentation and delivery recovery must also be implemented.

:::: {.details summary="What the client records for each destination"}

### Record observations without granting authority

For each exact destination mailbox, retain independently:

- The observed endpoint principal and authorized device set, if established.
- Each feature assertion, its asserting authority, scope, profile version and validity interval.
- The source and original bytes of the assertion, plus its validation result.
- The identity state to which the assertion was bound.
- Any local delivery policy and unresolved conflict affecting the destination.

A feature assertion describes its own scope: for example, structured-answer processing, a rendering profile, a receiving cryptographic suite or a provider control service. Support for one feature does not imply the others. A provider can assert service capabilities within its delegated scope; that assertion does not enroll a device or prove that every client accessing the account can decrypt.

Record arrival time separately from asserted validity and authenticated sequence information. A later arrival is not necessarily a newer assertion. Retransmission of the same validated assertion is idempotent. Contradictory assertions remain visible to the decision process until their applicable authority rules resolve them.

::::

## Identity freshness modes

[Freshness, clocks and revocation knowledge](freshness.md) defines the current agreement's complete policy selection and age checks. Cached continuity is the default for asynchronous delivery. Recent checkpoint additionally bounds the accepted account state's declared issuance time; live confirmation requires the exact device response to a locally outstanding challenge. The modes do not independently verify mailbox ownership or prove absence of unseen revocations.

The [known-pair device exchange](provider-control.md) and fresh [bootstrap response](bootstrap.md) provide defined live-evidence formats when their complete current-suite adapters are implemented. Offline publications, provider HTTP success, message arrival and relay inspection do not substitute for a device response. The [freshness gate](evidence/README.md#freshness-policy-gate) has local current-identity/assertion8/bootstrap evidence; complete public-service and send-release integration remain required.

Use the whole credible clock interval, retain the original local attempt/age anchor, apply policy independently to each intended device, and recheck current heads and known removals inside the release boundary. Replay, cache retrieval and restart never extend evidence. Stronger policy holds if its evidence is unavailable; a failure cannot lower it or authorize plaintext. Ordinary historical reading does not initiate a live check. MLS package lifetime/single-use, audience, verification and history rights remain separate gates.

## Discovery services and privacy

A discovery method needs a common publication and retrieval baseline so two conforming clients can find each other's information. Optional upgrades can extend that baseline. They cannot leave conforming clients with no method in common.

A lookup can reveal who is communicating and when. Its authority, privacy and cache rules therefore belong to the discovery contract, alongside the format of its result. Diagnostic text, mail-routing records and another protocol's delegation are not automatic authority to find or replace a person's encryption keys.

:::: {.details summary="Common method and migration requirements"}

### A common discovery baseline

Each interoperable Email/2 discovery profile must define at least one publication and retrieval method that every conforming implementation of that profile supports. Optional provider and live-exchange methods may add capabilities, but must not leave two conforming implementations with no discovery method in common. Migration between discovery methods must specify overlapping support and the conditions for retiring the earlier method.

This is a proposed Email/2 requirement informed by SPF's deployment history: RFC7208 section3.1 records the failure of a transition with no common record type that implementations were required both to publish and to check. It does not imply that Email/2 should reuse SPF records or select TXT records by default. The [passive discovery binding](passive-discovery.md) is the candidate common method for ordinary-mail experiments. Its acceptance tests and provider or live-exchange extensions remain unfinished.

An SPF result can describe a host's authorization to use an SMTP identity. It must not authorize a mailbox's encryption-key advertisement or be applied to the visible From address as though those identities were interchangeable. A synthetic `postmaster` identity used when evaluating a null reverse-path is not a discovered correspondent, a key owner or a destination for automatic negotiation.

::::

:::: {.details summary="DNS naming and untrusted diagnostic links"}

### DNS namespace boundaries

A DNS discovery profile must specify its resource-record type, globally scoped underscored label, subordinate naming rules and registration requirements. Underscored labels are coordinated namespaces, not automatically private extension space. Registration does not authenticate a mailbox, device or advertised capability. Existing DKIM key records retain their DKIM meaning and must not be reinterpreted as Email/2 endpoint-key advertisements. See the [registry audit](audits/underscored-registry.md) and [companion amendments](audits/underscored-dns.md). The registry audit checks the relevant current entries. The exact discovery binding remains unselected, so no new name-availability or registration claim follows.

A wildcard DNS answer can synthesize a record at an underscored name without the intended service meaning. Record presence alone MUST NOT establish Email/2 support or authorize key use. The discovery binding must validate its record syntax, intended scope and authentication. Registry expert review establishes entry clarity and uniqueness; it does not approve the protocol’s security or establish recipient identity.

### Diagnostics do not discover trusted services

A URL or instruction found in an SMTP diagnostic, SPF explanation, delivery report or authentication-result comment must not become a discovery endpoint automatically. Such text can originate with a remote party. Present it as attributed diagnostic content; opening a link requires the same user action and URL checks as other untrusted message links. Do not fetch it in the background to “repair” encryption or send credentials, keys or conversation content to it.

Discovery redirects and delegated sources need explicit, independently specified authority and scope. A delegated SPF policy, MX host or diagnostic hostname does not confer authority over a correspondent's endpoint keys. A failed optional explanation lookup must not change an independently established authentication result or the selected encryption policy.

::::

:::: {.details summary="Lookup privacy, scoped caches and delegated authority"}

### Lookup privacy and cache scope

Every discovery binding must state which identifiers leave the client or provider in its requests, who can observe them, and what event causes a request. A lookup may disclose communication timing even if the message body is encrypted. Sender-controlled templates must not cause automatic disclosure of local account identifiers, private recipient lists, message content or conversation history to arbitrary lookup destinations.

Cache entries must retain the inputs, authority and validity conditions on which the result depends. A result for one mailbox, device or feature must not become a domain-wide capability by dropping a distinguishing input from the cache key. When evidence depends on multiple records, the effective validity must not exceed the earliest relevant expiration. Expiration triggers re-evaluation or an unknown/stale state; it does not authorize a security downgrade.

A discovery profile must also bound recursive delegation and network work across the whole resolution attempt. Resetting those bounds at each delegation defeats them. Exact profile limits and failure behavior remain to be specified and tested; SPF's own numeric limits are not automatically Email/2 limits.


### Purpose-bound delegation

A third party's willingness to receive one protocol's traffic does not authorize it to act for a correspondent in another protocol. In particular, DMARC external-report authorization and wildcard report acceptance MUST NOT be treated as permission to publish encryption keys, approve devices, receive private conversation state or negotiate capabilities.

For any Email/2 delegated discovery service, the authenticated delegation must identify its purpose, subject and destination. An override or redirect must remain within that authority; a changed destination requires its own authorization. Cached authorization remains subject to its validity period, and a failed refresh must not expand its scope. The exact discovery binding and redirect rules remain to be finalized with the wire profile.

RFC9990 Section 4 provides relevant prior art for scoped external-destination authorization and loop prevention. Its reporting-specific DNS records and organizational-domain tests are not adopted as Email/2 identity rules.

::::
## Discovery when joining a group

Discovering a device is not the same as admitting it to a conversation. Admission checks its authenticated capabilities against the group's current requirements and validates the material used to join. Cached public group data also retains its confidentiality requirements; public cryptographic structure does not imply permission to publish the membership.

:::: {.details summary="Group capability checks and cached admission state"}

### Capability checks at group admission

Discovery is an input to admission, not permanent permission to skip validation. A group security binding must revalidate a joining or updating device's authenticated capabilities against the current group requirements. A device must support the credential types and required protocol features needed to validate the other members; the other members must likewise support its credential type. An advertisement observed earlier is insufficient if the authenticated admission object no longer satisfies those requirements.

Unknown optional capability values may be ignored where the underlying protocol requires it. An unknown required feature must not be treated as supported, silently removed from the group requirements or converted into plaintext fallback. Protocol-defined implicit defaults must be interpreted under that protocol's rules rather than requiring every default feature to appear explicitly in an advertisement.

The selected [MLS admission lifetime](security-profile.md#experimental-admission-lifetime) checks each package’s signed expiry and the receiver’s configured maximum total lifetime at sender admission and receiver Welcome acceptance. Seven days is the recommended configurable default, not a fixed profile limit. A package that was valid when observed cannot be reused indefinitely. Delayed arrival alone is not evidence that the sender originally selected expired material; the receiving attempt can still require fresh material. Implementations must apply that authoritative profile rather than a separate discovery-cache lifetime.


### Cached group state and admission material

An untrusted cache may distribute a group's public cryptographic tree when the joining client can verify it against authenticated group state. That integrity check does not make the tree safe to publish: credentials, member relationships and group configuration may remain sensitive. The transport used for cached state must preserve the confidentiality policy applied to the corresponding handshake data.

A client must validate the complete admission object before installing group state, including its own authorized membership, required credentials, tree integrity and confirmation. A cache response or successful decryption is insufficient on its own. GroupInfo used for an external join is epoch-specific; an accepted join changes the epoch, so another attempted join may need refreshed state and must not silently reuse a stale admission decision.

A resynchronization operation that replaces a device must satisfy the identity-lifecycle recovery rules. Possession of its signing key alone must not bypass a recovery policy that requires additional continuity evidence. The exact admission and recovery binding remains under review with RFC9420 Section 12.4.3 and its errata.

::::
## Existing encrypted-email mechanisms

S/MIME and Autocrypt both offer prior art for learning capabilities or keys through ordinary mail. An implementation can support those paths while keeping each protocol's evidence within its own scope. A compatibility advertisement cannot silently replace an established Email/2 identity or override required encryption.

:::: {.details summary="S/MIME capability and certificate preferences"}

### S/MIME compatibility boundary

S/MIME already supports passive capability exchange in ordinary signed mail. [RFC8551 Section 2.5.2](https://www.rfc-editor.org/rfc/rfc8551.html#section-2.5.2) defines a signed, partial list of supported algorithms and optional features. Section 2.5.3 separately identifies a preferred encryption certificate, which can differ from the signing certificate. These provide prior art for automatic exchange without a separate negotiation email.

An S/MIME adapter MUST validate the signature, attribute multiplicity, certificate suitability and applicable identity binding before using those assertions. Keep the resulting S/MIME preferences scoped to that protocol and correspondent. An algorithm capability does not announce Email/2 answer buttons, a rendering profile, MLS admission or support by every device accessing the mailbox. Omission from the partial list is not proof of non-support.

A later signed preference may update the S/MIME compatibility cache under its own rules; it MUST NOT by itself replace an established Email/2 principal or enroll a device. The reason is the different authority being exercised: choosing a certificate for an S/MIME reply does not establish an account's device roster or authorize access to conversation history. A signing time is asserted by the signer, not a live-response proof. It cannot satisfy the stronger freshness modes defined above.

The [S/MIME audit](audits/smime-message.md) records the source requirements and remaining certificate/algorithm dependencies. No interoperable S/MIME-to-Email-Next discovery adapter is established by this mapping.

::::

:::: {.details summary="Autocrypt first contact and separate compatibility state"}

### Autocrypt compatibility boundary

[Autocrypt Level 1](https://autocrypt.org/level1.html) provides prior art for distributing keys in ordinary outgoing mail without a discovery server. Its threat model addresses passive collection; its peer-state update algorithm can replace a remembered key using a newer message.

An Email/2 implementation that also implements Autocrypt MUST keep that compatibility state separate from established Email/2 identity authority. An Autocrypt advertisement MAY supply candidate first-contact material under the selected first-contact policy. It MUST NOT, by itself, authorize replacement of an established principal, enrollment of a device, or release of conversation history. Autocrypt recommendation changes MUST NOT override a required-protection policy.

This separation permits a legacy interoperability path without presenting two different trust models as equivalent. The [complete source audit](audits/autocrypt.md) records the remaining OpenPGP compatibility and implementation checks; this section does not claim an interoperable adapter.

::::

## Required acceptance cases

The conformance suite must exercise passive advertisements without replies; legacy access to the same mailbox; missing and replayed assertions; capability expiry without identity revocation; authorized withdrawal; competing key claims; provider changes without device enrollment; invalid reply destinations; duplicate requests and responses; exchange expiry; interrupted live exchange; and send-plan re-evaluation before submission.

It must also demonstrate the intended user experience: automatic protected sending after sufficient evidence, a readable fallback for a permitted legacy recipient, and a held send when protection is required but unavailable. A suite that only rejects unsafe exchanges does not establish that automatic encryption works.

## Automatic first contact over ordinary mail

A client may use **automatic unverified continuity** after that mode has been selected in local policy. It can then accept one eligible first-contact identity and associate it with the exact address without asking the person to exchange keys manually. **Verification required** keeps the same evidence pending until independent verification is available. Neither mode is a universal product default, and neither is selected by an incoming message.

Alice's ordinary message carries her device's signed advertisement. Bob's client records it without sending a response. Bob's next human-written reply can carry his own advertisement and, where the effective policy and available material permit, establish a protected conversation through the existing invitation path. The first ordinary message does not become encrypted retroactively. Missing or consumed admission material leaves protection pending; it does not cause an automatic request for more keys.

The interface distinguishes “encrypted to the identity first seen for this address” from independently verified ownership. A self-consistent first message can be substituted by an attacker. Pinning improves subsequent continuity; it does not eliminate that initial risk. The [mailbox-association rules](mailbox-association.md) keep the principal pin and address association as separate decisions. A client commits their initial selection together or commits neither. Exact retry preserves that decision, while each new use still checks current authority and validity.

Device coverage is also an explicit local policy:

| Device-target policy | When protected delivery can proceed |
| --- | --- |
| Evidenced devices | The intended individually evidenced devices satisfy the exact selected profile. The client shows which authorized devices were not included. |
| All authorized devices | Every current receive-role device has suitable evidence. A missing device leaves delivery pending. |

An identity roster authorizes devices; it does not advertise their applications or supply their admission packages. One passive assertion still describes one device. Evidence gathered from later human messages can support further authorized membership changes, but the client must not claim that an unevidenced device can read the conversation. The exact profile intersection and invitation checks apply to every intended target under either policy.

The [client-only onboarding experiment](evidence/README.md#client-only-ordinary-mail-onboarding) begins without preinstalled peer identities or mailbox associations. It joins ordinary SMTP messages to atomic selection, signed invitation delivery and an actual protected message/reply. These are local unverified-continuity checks, not an independent ownership-verification mechanism, complete account synchronization or provider deployment. Verification-required mode holds unless a separately accepted verifier supplies evidence. The optional [human comparison](mailbox-association.md#optional-human-comparison) can establish human-confirmed correspondent identity through an independent trusted channel; it does not establish provider-certified mailbox ownership.
