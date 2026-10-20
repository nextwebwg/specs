---
title: Experimental managed-conversation security profile
order: 8
blurb: selected MLS baseline · device leaves · remaining bindings
sectionNav: true
---

# Experimental managed-conversation security profile

The experimental baseline selects MLS 1.0, as specified in RFC9420, for managed encrypted conversations. This includes conversations between two people and their authorized devices. The selection is an editorial proposal for implementation work, not a claim that this document already defines a complete or independently validated MLS application.

## Common protocol and suite

Implementations of this profile MUST support MLS protocol version 1 and cipher suite `0x0001`, `MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519`. This is the mandatory baseline identified in RFC9420 Section 17.1; Email Next does not replace its component algorithms or packet encodings. The first experimental interoperability configuration uses that suite exclusively. Other suites require a separately specified negotiation and migration capability.

Implementations retain MLS's composition of its cryptographic components. Supporting an individual primitive does not establish support for this conversation profile.

:::: {.details summary="Inherited cryptographic components and source reviews"}

| Component | Source review |
| --- | --- |
| HPKE | [Construction and context binding](audits/hpke.md) |
| AES-GCM | [Authenticated-encryption interface](audits/aead-interface.md), [GCM limits and nonce lifecycle](audits/gcm.md), [AES block cipher](audits/aes.md) |
| Key derivation and hashing | [HKDF](audits/hkdf.md), [HMAC](audits/hmac.md), [SHA-256 and SHA-512](audits/sha256.md) |
| Key agreement and signatures | [X25519 input rules](audits/x25519.md), [plain Ed25519](audits/ed25519.md) |

These reviews explain inherited requirements. They do not certify a cryptographic library or the complete client.

::::

The selected suite is not post-quantum. No interface or conformance claim may describe this baseline as post-quantum secure. PQXDH and Double Ratchet remain prior art for separately evaluated paths; they are not extra layers to concatenate with MLS in this profile.

## Relationship to encrypted-email guidance

[RFC9787 §§5.2–5.3](https://www.rfc-editor.org/rfc/rfc9787.html#section-5.2) recommends signing inside encryption and avoiding an encryption-only composition option. This profile follows those security goals through MLS rather than adding a separate PGP/MIME or S/MIME signature layer.

An MLS PrivateMessage encrypts the application content together with its authentication data, including the sender's signature. The receiver validates that authentication data and resolves the signing leaf through the accepted identity and group state before enabling conversation effects. Decryption alone does not establish who authored the contribution. These are the framing and validation rules of [RFC9420 §§6.1 and 6.3](https://www.rfc-editor.org/rfc/rfc9420.html#section-6.3), not an additional Email Next cryptographic construction.

The difference is the selected wire protocol and its device-group model. A managed contribution does not need a second MIME signature to become authenticated, and an outer mail signature cannot substitute for the MLS checks. Separate legacy PGP/MIME and S/MIME profiles retain their own composition rules. The deliberate departure from RFC9787's recommendation for uniform protection across recipients is explained in the [mixed-delivery policy](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status).

This framing does not implement RFC9788 header protection by itself. [RFC9787 §§5.1 and 9.3](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.3) require that protection for its encrypted-email composition model. The managed profile instead authenticates the event's principal, audience and conversation through its selected application binding; an outer From, Subject or threading field does not acquire that protection. This difference keeps transport routing separate from conversation authority. The separately negotiated [protected presentation profile](managed-presentation.md) adds an encrypted subject, author-stated date and principal To/Cc roles. It is a semantic MLS binding, not RFC9788 wire compatibility; older profiles still leave their outer subject unprotected. The [legacy composition path](transport.md#default-header-confidentiality-for-protected-legacy-mail) retains RFC9788's rules.

### Differences to account for

RFC9787 remains the implementation guidance for the legacy encrypted-email formats it describes. The managed profile makes the following choices explicit:

| Area | Choice and reason | Definition |
| --- | --- | --- |
| Different protection for different recipients (§§3.2, 9.6) | Allow an explicitly authorized ordinary or hosted copy so adoption can be gradual. Any such copy broadens disclosure for the contribution; encryption of another copy cannot undo that disclosure. | [Mixed-delivery policy](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status) |
| Signature and encryption composition (§§5.2–5.3) | Use MLS's signed, encrypted application framing for device groups. This preserves author authentication inside encryption without a second MIME signature. | [Managed framing](#relationship-to-encrypted-email-guidance) |
| User-facing headers (§§5.1, 9.3) | Protect subject, author-stated date and recipient roles in a separately negotiated semantic MLS binding. Outer fields remain transport observations; arbitrary protected mail headers and RFC9788 wire compatibility are not supplied. | [Protected presentation](managed-presentation.md) |
| Selecting the displayed body (§7.1) | Honor an explicit multipart/related root when reading existing mail, even when it is not the first child. Otherwise a resource could be displayed as the message body. Newly composed mail puts the root first. | [Message interpretation](messages.md#related-root-traversal-for-protected-legacy-messages) |
| Blind recipients (§9.4.1) | Never hide a recipient inside a member-visible MLS roster. Use the separately negotiated [private-copy binding](private-copies.md), with one sender/recipient principal pair and independent events. Unsupported peers require a hold or explicitly permitted alternative. | [Blind-copy boundary](delivery-policy.md#why-the-managed-group-model-differs-from-rfc-9787) |

MLS also changes how delayed ciphertext and retained history interact. Consumed transport secrets are deleted, while readable history may be kept in a separately protected archive. This addresses the long-lived-key exposure discussed in RFC9787 Appendix A.10; it does not make credential expiry a reason to hide readable history (§9.2). See [delayed delivery and retained history](security.md#delayed-delivery-and-retained-history).

Absent and failed signatures still receive equivalent ordinary treatment. An expectation warning comes from prior trusted state and applies equally to either case; it is not a departure from §6.4. See [author verification](security.md#when-the-author-cannot-be-verified). The [section-by-section audit](audits/e2e-guidance.md) covers the remaining guidance and identifies unresolved integration work.

## Device and conversation mapping

Each authorized device occupies its own MLS leaf. A person with two devices therefore normally has two leaves. Sharing one leaf's evolving secret state between independent concurrent devices is not the baseline device model. The authentication binding must map each leaf credential to its stable account principal, device identity and authorized roles under the identity lifecycle contract.

An Email Next conversation identifier and an MLS group identifier are distinct. A conversation may contain ordinary contributions and separately authorized protected deliveries. The encrypted group's authenticated application context must bind its conversation identifier, security-profile version and membership policy. Matching a conversation identifier in an untrusted message does not establish that binding.

Two-person conversations use the same managed-group mechanism and device rules as larger groups. Adding a device still requires endpoint authorization. Removing a person removes all leaves representing that membership. A hidden recipient is not silently added to the member-visible group; any separate delivery follows the fallback and disclosure contract.

## Admission and asynchronous delivery

A recipient device publishes MLS KeyPackages under the selected discovery binding. That material permits asynchronous invitation; the recipient need not be online when the sender constructs it. Publication alone does not prove account ownership or authorize admission. KeyPackage validation, single-use handling, device authorization and expiry policy remain required.

An accepted membership transition precedes release of its Welcome messages. Clients validate the complete Welcome and authenticated context before treating the session as ready. The [initial invitation carrier](mls-invitations.md) defines admission for new conversations, including the selected multi-device roster profile. Established groups use their separate [Welcome delivery contract](group-conversations.md#membership-in-rich-conversations). Direct online contact can refresh admission material or confirm state, but does not replace those checks or create a separate mandatory handshake protocol.

Application contributions use MLS PrivateMessage protection. The selected group-control experiments carry encrypted MLS Commits with separate ordering evidence. Quorum carrier1 also exposes its signed ordering scope, resulting roster and proof metadata outside the MLS ciphertext; it does not hide those fields from mail infrastructure. The separate [signed ordering exchange](ordering-exchange.md) binds standalone candidate/vote transport to explicit support and durable dependencies. Ordinary SMTP acceptance supplies delivery evidence only; it does not commit a group transition.

## Legacy and fallback boundaries

Autocrypt/PGP-MIME and S/MIME are separate legacy delivery profiles. An Autocrypt key is not an MLS KeyPackage, and receiving one does not demonstrate support for this profile. A conforming implementation must not label a legacy encrypted copy as MLS-protected or assume that its key lifecycle has MLS's properties.

A sender may select an authorized legacy or hosted path for an incompatible recipient under the delivery policy. That choice does not change the MLS group's membership or silently expose its history. Ordinary readable copies remain disclosed outside endpoint encryption, even when other recipients receive MLS-protected copies.

## Application bindings

MLS supplies the cryptographic group protocol. The application must also bind devices, conversation state, transported contributions and durable effects. The following contracts define those boundaries; selecting the cipher suite alone does not satisfy them.

| Boundary | Owning contract |
| --- | --- |
| Principals, devices and credentials | [Identity state](identity-state.md), [device binding](#mls-basiccredential-identity-payload) and current role authority |
| Conversation and application agreement | [Authenticated context](#authenticated-conversation-context) and exact selected payload profiles |
| Admission | [Initial invitations](mls-invitations.md), single-use packages and acceptance-time lifetime checks |
| Membership and ordering | [Group transitions](group-conversations.md), separate Commit/Welcome delivery and the selected writer policy |
| Contribution carriage and effects | [Protected contribution bytes](#protected-contribution-bytes), [durable reception](#durable-reception) and exact event references |
| History and secrets | [Retention policy](security.md#delayed-delivery-and-retained-history), authorized exports and atomic recovery |

The endpoint-quorum experiment supplies certified coordinator changes, atomic catch-up and [durable candidate/vote exchange](ordering-exchange.md). Its selected lifecycle retains public safety evidence and retires obsolete staged secrets after certified installation. Designated-writer takeover remains unsupported; adding it requires a separate capability. [Managed restoration](identity-lifecycle.md#import-history-then-reconnect) imports inert history and reconnects with fresh authority. Live-secret backup restoration and whole-machine rollback assurance are not supplied by that path. Protected blind delivery now has a separately versioned [private-copy contract](private-copies.md) and bounded local evidence. The [coverage table](interoperability.md#contract-coverage-and-remaining-decisions) distinguishes them from implemented local evidence. The [MLS protocol audit](audits/mls.md) and [architecture audit](audits/mls-architecture.md) provide source analysis, not implementation certification. Forward secrecy and compromise recovery depend on actual key deletion, accepted updates and endpoint security.

## Single-use admission packages

This experimental profile does not use MLS's optional reusable last-resort KeyPackage mode. Each published package is for one admission. A depleted pool causes refresh or a pending invitation under the selected delivery policy; it does not authorize reusing an already allocated package or switching to plaintext.

A provider allocation service MUST atomically associate a package reference with one authorized request identity before returning it. The request identity is scoped to the requesting principal, target device and selected profile. Repeating that same request returns its original result, including a depleted-pool outcome; after replenishment a new authorized request is required. A different request cannot obtain the same package. An abandoned or expired allocation MUST NOT return its package to the pool, because a delayed Welcome may still exist. Generate fresh material instead.

An ordinary message carrying a package cannot provide an atomic allocation service by itself. Such advertisements are therefore not assumed to offer exclusive package ownership. The recipient must enforce single-use acceptance independently, and a failed concurrent invitation must obtain fresh admission material. This availability cost must remain visible in the bootstrap design; do not claim that passive mail alone prevents races among senders.

A received malformed or unauthorized Welcome MUST NOT consume a package merely by naming its reference. After complete cryptographic and application validation, acceptance and consumption must be committed atomically with installation of the corresponding group state. A retry of the exact accepted admission retrieves its recorded result rather than creating another group instance. A different admission attempting to use consumed material is rejected.

The client retains a non-secret consumed-package record sufficient to prevent reuse after restart. A backup restore must reconcile that record before publishing or accepting old package material. Retention and garbage collection must never turn an old allocation into a reusable one. The lifetime policy below bounds unused admission-secret retention separately from these non-secret reuse records.

These are application requirements building on RFC9420 Sections 10 and 16.8. They deliberately strengthen its normal single-use recommendation and exclude its last-resort exception for this baseline. The [durable allocation experiment](evidence/README.md#durable-package-allocation) tests local transactional allocation, retries and process exit. The [joined provider-to-MLS experiment](evidence/README.md#provider-discovery-to-encrypted-mail) additionally validates real admission and atomically installs the target checkpoint with package consumption. Signed invitation carriage and separate established Welcome delivery have their own local experiments. Backup reconciliation and deployed admission-service integration remain unvalidated; these allocation checks alone do not establish them.

## Experimental admission lifetime

The first experimental profile limits a KeyPackage lifetime to 604800 seconds (seven days). This is an editorial interoperability parameter, not an IETF limit or a user-selected retention rule. It bounds how long unused admission secrets need remain usable while allowing ordinary asynchronous exchange. Deployment evidence may justify a revised profile; a peer cannot silently extend the bound through an advertisement.

The authenticated `not_before` and `not_after` values use MLS's unsigned 64-bit seconds representation. A package is structurally unacceptable if the end precedes the start or the interval exceeds the profile maximum. A sender validates the lifetime immediately before constructing an Add proposal or Commit, not merely when downloading the package. The allocation service must not issue material it knows to be expired; service validation does not replace the sender's check.

For a new local admission through Welcome, this profile also requires the joining device's package to remain valid at acceptance time. This deliberately chooses the stricter receiving behavior permitted by RFC9420 Section 7.3. Mail delayed beyond expiry requires fresh admission material and a new authorized membership attempt. It is not evidence of malicious behavior and does not authorize plaintext retransmission. This check does not require every historical member's original KeyPackage lifetime to remain valid forever; existing tree credentials follow their applicable MLS validation and identity-lifecycle rules.

Clients must maintain a credible current-time estimate. If the client represents clock uncertainty as an interval, the entire interval must lie inside the package lifetime to accept it. A clock known to be unreliable leaves time validation unresolved. Message Date fields, provider response timestamps and a peer's assertion of when it sent an invitation MUST NOT extend the lifetime. There is no additional implicit grace period.

After the lifetime ends, unused admission private material must be retired; a pending invitation cannot extend it indefinitely. Successfully consumed material follows MLS's secret-deletion requirements. The non-secret consumption record remains separately protected against rollback. Replaying the exact already accepted admission may return its recorded outcome after expiry, but MUST NOT decrypt the Welcome again using retained admission secrets or install another group instance.

The lifetime experiment checks unsigned bounds and uncertain-clock decisions. It does not supply trusted time, implement MLS parsing or validate a Welcome. Seven days is not a guarantee of delivery latency or protection against compromise during that interval.


## Provider directory and sharing boundaries

A JMAP Principal record MUST NOT be used directly as an Email Next cryptographic principal merely because its name or email matches. Preserve its service and account scope and establish the security profile's identity binding independently. Provider authorization to read a mailbox is not authorization to add a device or principal to an MLS group.

JMAP subscriptions and ShareNotifications MUST NOT be the authoritative cryptographic membership record. Notifications may be omitted, coalesced or removed; missing notifications do not prove unchanged permissions. Dismissing a notification does not revoke access. Translating a shareWith map to an encrypted audience must explicitly account for implicit owner rights and independently authorized endpoint devices. See the [JMAP sharing audit](audits/jmap-sharing.md).

## Account and device identifier encoding

The experimental version-0 account principal is the literal ASCII prefix `enp0:` followed by 64 lowercase hexadecimal characters encoding 32 octets. A device identifier uses `end0:` followed by the same-length encoding. The all-zero value is invalid in both domains. New identifiers MUST be generated from a cryptographically secure random source and stored durably before use. These are opaque identifiers, not URLs, mailbox addresses or hashes of mailbox names.

Compare identifiers by exact ASCII bytes. No case folding, whitespace trimming, Unicode normalization, prefix aliasing or account-name inference is permitted. An account principal cannot be used where a device identifier is required, and vice versa. Prefix versions other than the supported value are unknown encodings, not aliases. This selects a wire representation, not a registry allocation or proof of global coordination.

The account identifier remains stable across authorized device changes and mailbox-address updates under the identity lifecycle contract. Distinct accounts MUST NOT be merged merely because they share a mailbox label, display name or provider record. A device identifier denotes one authorized device identity; replacing its keys or restoring state requires the lifecycle checks independently of whether its identifier remains unchanged. Copying identifiers does not copy authorization.

A syntactically valid identifier proves neither ownership nor key possession. The authenticated credential binding MUST associate the account principal, device identifier, signing key, mailbox claims and applicable validity/revocation state. Conflicting bindings remain unresolved until the lifecycle policy validates continuity; choosing the first observed string or trusting a provider's directory name does not resolve the conflict. The device-binding payload below selects part of that schema. The [identity-state contract](identity-state.md) defines authority validation, and [mailbox association](mailbox-association.md) distinguishes accepted continuity from independent ownership evidence. A configured association or successful local fixture does not prove mailbox ownership.

Contribution `principal`, audience members and EventReference principal fields use the account encoding above. They MUST NOT carry a bare email address or a device ID. The [identifier experiment](evidence/README.md#account-and-device-identifiers) connects this spelling to envelope validation while demonstrating that schema success still leaves authentication unverified.

## MLS BasicCredential identity payload

The first experimental configuration uses MLS credential type `basic` for device leaves. The BasicCredential identity field contains exactly 85 octets, in this order:

| Offset | Length | Value |
| --- | --- | --- |
| 0 | 21 | ASCII `email-next/device/v0` followed by one zero octet |
| 21 | 32 | Account principal's decoded hexadecimal value |
| 53 | 32 | Device identifier's decoded hexadecimal value |

The textual enp0/end0 prefixes are not included in the two binary identifier fields. Both values MUST be nonzero. A receiver MUST reject a different length, domain/version prefix or trailing data. It MUST NOT trim the identity, treat it as a C string, parse it as a mailbox, or guess an older encoding. The surrounding Credential and vector framing remain exactly MLS's encoding; this payload does not replace them.

The MLS leaf signature key MUST match the independently validated binding for this account/device pair and the selected cipher suite. Parsing the identity or verifying a leaf's self-signature alone MUST NOT establish account ownership. A claimed existing device with a different key requires the identity lifecycle's authorized replacement procedure; it cannot silently overwrite an accepted binding. Likewise, copying a legitimate account/device payload into a new KeyPackage grants no admission rights.

Mailbox claims, role grants, validity intervals, continuity evidence and revocation records are not embedded in this compact identity field. Their credential-binding record and validation protocol remain required before interoperability or verified-sender claims. The experimental BasicCredential choice does not convert an S/MIME certificate or a provider session into MLS authorization. Other MLS credential types require their own explicitly specified application binding.

The [credential identity experiment](evidence/README.md#mls-credential-identity-payload) checks fixed bytes and domain separation. It does not implement the surrounding MLS codec, key validation, signature verification, account authorization or admission.

## Device-binding proof experiment

A candidate detached proof signs exact binding-record bytes using Ed25519. Its experimental signing input is the ASCII string `email-next/device-binding/v0` followed by one zero octet, a four-octet unsigned big-endian payload length, and the original payload bytes. This is domain separation for the application binding record; it MUST NOT replace MLS's own signature labels, framing or verification rules.

The experiment limits payloads to 1048576 octets and represents a raw 32-octet public key and 64-octet signature as lowercase hexadecimal at its local API boundary. The [identity proof bundle](identity-state.md#identity-proof-bundle) carries these encodings; MIME packaging and registration remain separate work. It does not canonicalize JSON: equivalent values serialized differently require a different proof. Strict record parsing and complete schema validation remain separate prerequisites.

A successful cryptographic check establishes only that the supplied key signed those bytes under this proof context. The receiver MUST independently resolve the authorizing identity state, permitted role, validity, revocation and transition history before accepting a binding. A self-signed first-contact record remains a claim under the user's first-contact policy. Supplying a previously known key without proving that it had the relevant authority is insufficient.

The [binding-signature experiment](evidence/README.md#device-binding-signature-experiment) verifies actual signatures and rejects byte substitutions, wrong keys and missing domain separation. The device-binding payload below supplies the record schema. Authority chains, mailbox evidence, replay/branch rules and integration with MLS admission are still required. No enrollment or verified-correspondent result is produced by this primitive.

## Device-binding record schema

A version-0 device-binding payload is one strict UTF-8 JSON object under the event encoding rules, with exactly these members:

| Member | Value |
| --- | --- |
| version | String `0` |
| purpose | String `device-binding` |
| record | Nonzero ObjectId, stable across retries |
| principal | Account enp0 identifier |
| device | Device end0 identifier |
| signingKey | Raw Ed25519 public-key bytes as 64 lowercase hexadecimal characters |
| roles | Nonempty array of distinct role strings from the set below |
| notBefore, notAfter | Canonical unsigned-64 decimal strings containing UTC epoch seconds; end must not precede start |
| authority | One of the exact objects described below |

Roles are `send`, `receive`, `enroll`, `revoke` and `recover`. Send permits application contribution origination; receive permits inclusion in future protected delivery. Enrollment, revocation and recovery roles identify separate administrative powers and MUST NOT be inferred from send or receive. Their exercise remains subject to the accepted identity state's policy; listing a role in an unaccepted record does not grant it. MLS protocol-control traffic has its separately authorized group rules.

First-contact authority is exactly `{"kind":"first-contact"}`. Its detached proof must be made by the listed signing key and is only a possession claim. It may be accepted for initial unverified use under the configured first-contact policy; it MUST NOT replace an established binding, enroll an extra device into an established account, or authorize historical access.

Established authority is exactly `{"kind":"state","digest":"…"}`, where digest is the lowercase SHA256 of the exact authorizing identity-state record bytes. The receiver must resolve that state within the same account, authenticate its authority and validate the proof under an authorized signing key. The digest alone supplies none of those results. Missing, conflicted, superseded or revoked authority cannot be replaced with the newest advertisement or an implicit first-contact path.

The validity fields describe the binding, not an extension of MLS KeyPackage lifetime or evidence of trusted current time. Canonical decimals have no leading zeros except `0`, signs, whitespace, fractions or exponents. Role order does not grant priority, but the proof still covers its exact serialized order. A changed record with the same record identifier is a collision requiring resolution, not a last-writer-wins update.

This schema selects the payload shape and proof relationship. [Identity-state records](identity-state.md) specify state serialization, ordinary role delegation and replay/branch behavior. Revocation freshness, maximum binding lifetimes, mailbox verification, recovery and integrated validation remain required before this record can authorize interoperable enrollment. The [binding-record experiment](evidence/README.md#device-binding-record-schema) validates shapes and actual proof sensitivity; it does not implement those authority decisions.

## Binding possession and acceptance order

A device-binding record requires proof that the proposed device possesses its listed signing key, separately from proof that an established account authorizes that key. The possession signing input is ASCII `email-next/device-possession/v0` followed by one zero octet, a four-octet unsigned big-endian length, and the exact binding payload bytes. It uses the same Ed25519 key and signature encodings and payload limit as the detached binding proof. Receivers MUST verify possession under the record's signingKey. An enrollment authority's signature cannot substitute for this proof.

For first contact, both the binding proof and the possession proof use the listed key under their respective domains. This establishes a self-consistent claim, not mailbox ownership or continuity. For established enrollment, the possession proof uses the proposed device key; the binding proof uses an independently authorized key resolved from the referenced identity state. The two keys may coincide only when the accepted state permits that operation. Neither signature can be reused in the other's role.

Receivers process a candidate in this order:

1. Bound the input and strictly decode the original payload under the event encoding rules. Validate the entire binding schema. Preserve those original bytes for both proofs; do not reserialize the parsed object for verification.
2. Verify device possession. Missing or invalid possession makes the candidate invalid, regardless of an otherwise valid enrollment signature.
3. Resolve authority. For first contact, verify the self-binding proof and consult the configured initial-use policy. Any already established account binding prevents this path from acting as replacement or additional-device enrollment. For state authority, resolve exactly the referenced state for the same principal. An unavailable state is pending; contradictory accepted authority is conflicted. Neither outcome permits enrollment.
4. Verify the binding proof under a signer authorized by that state for the requested operation. Administrative delegation must explicitly permit every requested role and scope. An enroll role alone MUST NOT be interpreted as unlimited permission to grant enroll, revoke or recover powers to others.
5. Check binding validity, applicable revocations, accepted-state freshness and continuity. The interval is inclusive at both endpoints. Uncertain current time or unavailable required freshness evidence holds the operation; expiry does not imply a permitted fallback to plaintext. This check also applies at use time, rather than only when the advertisement arrives.
6. Check the record identifier and device identity against durable accepted history. Exact-byte retries are idempotent. Different bytes under the same record identifier are a conflict. A different key for an existing device requires an authorized replacement; it is not an ordinary additional binding. An old valid proof cannot restore superseded or revoked authority.
7. Atomically persist acceptance, the authority reference, proofs and replay evidence before making the device eligible for the permitted operation. Recheck the authority state when committing; a concurrent removal or branch conflict must not be bypassed by a decision computed from an earlier snapshot.

These steps define acceptance requirements, not an implementation claim. Pending and conflicted outcomes preserve evidence without granting roles. Invalid candidates cannot erase existing accepted authority merely by naming it. First-contact acceptance remains explicitly unverified unless separate identity evidence establishes a stronger assurance level. Authorization to receive future content still does not authorize historical key transfer.

The [possession-proof experiment](evidence/README.md#device-possession-proof) checks the two cryptographic domains and key distinction. The [state record and ordinary delegation rules](identity-state.md) supply the next protocol layer. The identity-bundle carrier is specified there. MIME packaging, freshness, recovery and atomic lifecycle implementation remain prerequisites for an interoperable enrollment protocol. This experiment does not supply them.


## Library integration evidence

The [OpenMLS exchange experiment](evidence/README.md#openmls-encrypted-exchange) exercises suite0x0001 with the selected credential identity bytes, serialized admission packages, Welcome, public-tree data and protected messages. Exact decoding rejects trailing bytes, and package validation rejects the tested signature alteration. The structured-message extension checks the claimed event author against the credential returned by MLS processing after decryption. The sender’s actual leaf key is checked against a genesis binding verified and pinned under an explicit unverified first-contact policy. Substituted keys, credentials, forged proofs and expired claims are rejected. This fixture does not yet connect successor states and revocation to the group lifecycle, implement authorized membership changes or implement the complete application profile. The receiver now compares the contribution against the authenticated conversation context and current epoch roster as described below.

A receiver integration MUST account for cryptographic library mutation on unsuccessful processing. The tested OpenMLS0.9.1 path rejects tampered ciphertext but leaves its live receiver object unable to process the genuine copy until group state is reloaded from the provider's unchanged storage. Applications must define which failure paths preserve, commit or discard tentative state and validate those rules together with replay protection and secret deletion. Do not infer mutation-free rejection from an error return, or roll back previously committed valid messages as a generic recovery strategy.


## Authenticated conversation context

The candidate MLS profile carries an application context in GroupContext extensions. The local experiment uses private-use extension type 0xff00, within the range reserved by [RFC 9420 section 17.3](https://www.rfc-editor.org/rfc/rfc9420.html#section-17.3). This is an experimental code point, not an assigned interoperable Email Next identifier. It MUST NOT be assumed unique across unrelated experiments. A published interoperable binding requires registration or an explicitly isolated deployment agreement.

The extension payload is a strict JSON object under the event encoding limits, with exactly these fields:

| Field | Candidate requirement |
| --- | --- |
| version | String `0` |
| purpose | String `conversation-context` |
| conversation | A valid conversation object identifier |
| profile | String `mls-1-0001` |
| administrators | Nonempty array of unique account principal identifiers in ascending ASCII order |

The group includes this extension type in RequiredCapabilities. Creator leaf capabilities and joining KeyPackages advertise support. Advertising an opaque extension alone does not establish that a client implements its application semantics.

Before rendering a contribution, receivers MUST validate the context from the authenticated message epoch and derive the account audience from that epoch's authenticated leaf credentials. Multiple devices belonging to one account produce one audience entry. Duplicate account/device pairs invalidate this candidate roster. The processed sender credential must identify a member, and its account must equal the contribution principal. The contribution conversation must equal the context conversation, and its audience must equal the derived account set. Every listed administrator must belong to that set. Failure MUST NOT produce a rich contribution. Outer mail headers cannot supply or override these values.

These checks establish internal group consistency. They do not establish that a received Welcome represents the conversation the user intended to join, that the claimed device keys have account authorization, or that an administrator change was authorized. Admission must separately bind the expected invitation/conversation and validate identity state. Membership and administrator changes need application authorization before committing the new epoch. The versioned initial and established invitation contracts supply admission checks; the group chapter defines the supported membership transitions. Administrator changes and unsupported transition kinds remain held. Delayed messages require the corresponding historical epoch context and roster; substituting the newest roster would be incorrect.

The local exchange carries this extension through a serialized Welcome and checks decrypted contributions against a snapshot of the authenticated epoch. Separate encrypted messages with a wrong conversation, wrong audience and wrong claimed author are rejected by the application bridge after successful MLS processing. Application rejection does not roll back cryptographic receive state. A separate removal case exercises delayed old-epoch decryption, matching historical context and new-epoch exclusion. It does not implement historical effect authorization or account-driven membership changes. The required account-to-group consequences and queued-send boundary are specified in [group conversations](group-conversations.md#applying-account-changes-to-an-mls-group).

## Protected contribution bytes

Conversation-context versions 0, 1 and 2 carry exactly one original UTF-8 contribution envelope as MLS application data. It uses the [event encoding](event-encoding.md), including its size limits, strict parsing and exact-byte identity. It adds no MIME entity, compression, JSON wrapper or trailing object inside that application payload. Version 3 explicitly selects its payload format as defined below. Control messages use their separate MLS types and authorization rules; arbitrary application strings are not contributions.

For this profile, MLS `authenticated_data` is empty. Receivers reject nonempty values rather than guessing another convention. The authenticated conversation-context extension and the contribution's exact `version` and `purpose` establish the application interpretation. MLS supplies its own framing, signatures and encryption; no additional application signature construction is introduced. This is an experimental profile choice, not a requirement imposed by the email baseline.

Before using decrypted bytes, the application binds the processed message's group identity, epoch and member sender index to a snapshot captured from that accepted library group state. It resolves the sender's credential and signature key from that exact epoch's leaf. It then applies the conversation, principal and audience checks above. A current roster cannot substitute for an older epoch's roster. An unresolved group branch remains pending; matching an epoch number alone does not resolve competing commits.

The member's epoch key is also checked against current retained account authority before new effects are allowed. Successful historical decryption cannot restore a revoked key or a lost send role. Exact event retries remain subject to application idempotence even when separately encrypted; cryptographic replay rejection alone is not the event ledger. The [late-message rules](group-conversations.md) continue to govern new arrivals after authority changes.

::: {.details summary="Joined experiment and remaining integration"}

### Application bridge evidence

The Rust exchange captures context, roster, member indices and signing keys from library group state, and obtains group, epoch, sender credential and authenticated data from the processed MLS message. The Python bridge compares those values before projecting the original contribution bytes. These are trusted internal adapter inputs, not authentication claims accepted from mail.

The encrypted exchange rejects nonempty authenticated data. A delayed contribution validates against its retained old-epoch snapshot and fails against the newer group's snapshot. Existing wrong-author, conversation and audience checks still apply. A separate five-case Python test exercises exact group/epoch matching, sender index and credential consistency, duplicate roster rejection, one-object parsing, and checks against a retained `IdentityStore`, including wrong signing keys, strict policy and an accepted identity conflict. Those adapter tests supply fixture snapshots; the Rust exchange supplies actual library snapshots.

The Rust subprocess path performs context/projection checks; it does not yet share a persistent account store with the receiver. The Python API can join a supplied retained identity store, but that check is still a read snapshot. Neither path commits an application effect or supplies atomic receive processing, secret deletion, persistent replay handling, group-ordering recovery or send authorization. The staged current-epoch coordinator below joins a separate receive path with durable storage and retained identity checks. The MIME carrier remains the [opaque attachment experiment](transport.md#mls-transport-experiment), not a final interoperable MLS email binding.

:::

## Durable reception

A receiver must preserve the relationship between a consumed message key and the outcome recorded for that message. A crash must not lose an accepted contribution, apply it twice or turn rejected application content into a fresh cryptographic attempt.

Successful MLS authentication and application acceptance are separate decisions. When authentication succeeds but the contribution is malformed or unauthorized, retain the cryptographic advancement and the rejection or pending outcome together. When cryptographic authentication fails, do not install tentative library changes. Only committed outcomes may drive presentation or later authorized effects.

::: {.details summary="Staged receive experiment and crash recovery"}

### One local commit

The local reference receiver uses a disposable Rust worker loaded from a stored OpenMLS checkpoint. The worker authenticates one private application message and returns its staged state, original contribution bytes and authenticated epoch evidence. It does not write the live database or send anything.

While holding one SQLite transaction, the receiver checks current retained identity authority, validates the contribution and records the new checkpoint with its outcome. Eligible contributions enter the shared journal in that same transaction. The receiver integrates messages, questions, answers, reactions and withdrawals, hosted-holder observations, attachments and rich messages under their separately negotiated profiles. Supporting one profile does not authorize another; resource availability and later dependency resolution retain their own validation gates. A worker failure or database failure commits none of these changes. The fixed storage format is local to the pinned library, not a wire format or a requirement to use SQLite.

An exact ciphertext retry returns its retained outcome. A separately encrypted copy of the same event advances its own cryptographic state but creates no second journal contribution. Authenticated different bytes under one event identity preserve both variants and report `event-conflict`. An earlier stored outcome is historical evidence, not fresh authorization to perform an action.

The real-crypto cases cover restart, ciphertext and event replay, authenticated collisions, invalid application bytes, failed authentication, local-clock input errors, current identity conflict, concurrent connections, injected write failures and process death before commit. The fixture starts with a pre-established group; it does not prove invitation or group admission. The separate [joined admission experiment](evidence/README.md#provider-discovery-to-encrypted-mail) establishes a new target group before using this receiver; its test-only invitation envelope is not the final mail binding.

### Limits

Pending messages, button questions and answers can be reevaluated from retained authenticated bytes without decrypting again. The receiver checks current authority before promoting a pending contribution, resolves exact references from the retained snapshot, and commits acceptance and local button views together. Previously accepted history remains available; its earlier acceptance is not permission for a new external action. An answer arriving before its question can therefore resolve after restart when the question arrives. Exact ciphertext retries retain their original decision snapshot; an explicit reevaluation reports current application state.

This receiver handles the current accepted epoch. Historical-epoch reception, handshake/commit routing, other operation kinds, effect dispatch, group ordering, admission and send-release coordination still need integration. No received contribution automatically invokes a service or sends a reply.

The checkpoint contains secrets. Replacing its database row does not prove that old pages, journals, backups or filesystem snapshots erased them. This experiment establishes logical commit behavior, not production secret-erasure or forward-secrecy storage hygiene. The [receive experiment instructions](evidence/README.md#staged-durable-mls-reception) describe its setup and test boundary.

:::

## Passive receiving-capability assertions

The [experimental passive discovery binding](passive-discovery.md) permits a currently authorized receive device to sign advertisements for its own receiving features and admission material. This authority does not extend to another device, account-wide capabilities, device enrollment or identity changes. Sending the accompanying human contribution still requires independent send authority. Clients must validate the discovery assertion against the current accepted identity head and the binding’s receive role before using it.

## Admission-package validation evidence

The [package-validation experiment](evidence/README.md#passive-mls-admission-package-checks) checks exact MLSMessage carriage, cryptographic validity, expected device/key, suite, lifetime and required capabilities before returning a package. Its accepted signing key is a caller-supplied trust dependency. It does not perform the recipient’s single-use consumption or atomic group installation. The library’s additional system-clock check is an implementation limitation to reconcile with the profile’s time-uncertainty rules; rejection does not authorize a plaintext retry.

## Configured application agreement

Supporting encryption does not automatically mean supporting answer buttons or a new contribution format. Every device in the authenticated roster must have a retained agreement for the same application profile. The configured experiment records an explicit deployment setting. The [signed-admission experiment](evidence/README.md#signed-application-agreement-at-admission) instead retains independently verified signed device evidence atomically with admission; an unverified claim in an incoming email supplies neither kind of agreement.

Version `2` conversation context binds that profile to the authenticated MLS epoch. Older context versions retain their exact contracts. Public capability naming and authenticated negotiation remain required work; the existing `mls-1-0001` capability alone does not establish this application agreement.

::: {.details summary="Context fields and local device evidence"}

### Exact context

Version `2` has exactly `version`, `purpose`, `conversation`, `profile`, `administrators`, `application` and `ordering`. The base fields follow the version `0` context contract, with `version` equal to the string `2`.

`application` has exactly `envelopeVersion`, the string `1`, and `operations`, a nonempty sorted array of distinct operation names. The selected vocabulary is `answer`, `hosted-holder-observation`, `message`, `question`, `reaction` and `reaction-withdraw`. The hosted operation's admission and effects additionally require its own contract; adding its name does not authorize external effects.

`ordering` is either exactly `{"kind":"fixed-roster-v0"}` or the separately configured designated-member object used by the group-transition comparison. Null and unknown fields are invalid. The fixed-roster setting supplies no membership-change ordering protocol.

### Acceptance

The contribution must use envelope version `1`; its operation must appear in the authenticated context's declared operations. Each roster device's established agreement must match the complete application object and the exact authenticated device credential and signature key. Signed admission records the selected subset supported by every device, together with immutable assertion and signature provenance; later advertisement expiry does not retroactively remove that established agreement. Missing or mismatched evidence holds structured processing. The designated-member ordering setting still requires its separate configured opt-in and an ordering device present in the authenticated roster.

Current sending checks this local agreement during preparation and again through the release-time authority checks. A browser-supplied flag, an unknown incoming version or a successful shape validation cannot replace it. These settings do not establish mailbox ownership or general public interoperability.

:::

## Explicit payload agreement

Context version `3` makes the protected payload format part of the agreement. It has the same seven top-level fields as version 2, with `version` equal to `3`. Its `application` object has exactly `envelopeVersion`, `payload` and `operations`:

| Field | Value |
| --- | --- |
| `envelopeVersion` | String `1` |
| `payload` | `raw-event-v0` or `mime-contribution-v0` |
| `operations` | Nonempty, sorted, unique operations supported under that payload |

The operation vocabulary and exact device-support combinations follow [version-2 discovery](passive-discovery.md#version-2-exact-supported-combinations). The existing ordering objects and administrator requirements remain unchanged. Payload support does not grant authority to order membership changes. Every device agreement must match the complete application object, including `payload`.

For `raw-event-v0`, application data remains the exact original event bytes. For `mime-contribution-v0`, it is one complete MIME entity containing readable alternatives and the exact structured event, with attachment resources only under their specified layout. It is not an enclosing email message. MLS authenticated data remains empty. The transfer-decoded original event bytes determine event identity; MIME boundary changes do not create another event.

Select the decoder from the message’s authenticated epoch context and original membership instance. Do not inspect content to guess the format, try raw JSON after MIME failure, or substitute the newest agreement for an old epoch. Retain the received entity separately from its extracted event and diagnostics. Invalid application content follows the durable-reception rule: authenticated cryptographic advancement and the rejected outcome are committed together without application effects or an automatic downgrade.

Readable alternatives are the sender’s supplied bytes, not proof of equivalence to the structured event. The rich view derives from the independently admitted event. A discrepancy remains visible in source inspection; it does not silently replace the event’s meaning. When a pending event becomes accepted after its dependencies arrive, check each retained representation separately, including different MIME copies of the same event.

> [!note] Integration status
> Exact context and capability validation are implemented. Configured body and attachment flows have passed local encrypted SMTP checks, including retained resource-integrity results and explicit byte retrieval. Signed tuple admission has passed a joined body-message and third-device invitation flow. The [joined attachment experiment](evidence/README.md#joined-protected-carriers-and-deliberate-attachment-download) also covers signed admission, encrypted delivery and deliberate browser download. These local fixtures do not establish independent interoperability or production client integration. The attachment codec alone does not establish supported encrypted attachment reception. Existing context versions retain their original byte interpretation.
