---
title: Interoperability and open decisions
order: 15
blurb: prior art · compatibility · completion criteria
sectionNav: true
---

# Interoperability and open decisions

The first implementation target is useful upgraded clients over existing mail. Additional server capabilities must improve that baseline without silently changing the meaning of a conversation.

## Relationship to existing standards

The table summarizes the mechanisms used or considered by this draft. The [baseline chapter](baseline.md) explains inheritance and proposed changes; the [audit inventory](audit-inventory.md) records source, update and errata coverage. This overview does not replace the section-by-section audits.

| Existing work | Relevant mechanism | Role in this draft |
| --- | --- | --- |
| MIME, RFC 2046 | Alternate representations and extensible media types | Structured content with readable alternatives |
| Internet Message Format, RFC 5322 | Message identifiers and reply references | Preserve ordinary threading while adding event relationships |
| RFC 3676 | Flowed plain text and quotation rules | More reliable interpretation of qualifying legacy text |
| Experimental RFC 9078 | Email reactions | Readable reaction projection; protected authority comes from the separate authenticated event contract. Publication as an RFC does not make it Standards Track |
| JMAP Mail, RFC 8621 | Client/server mail access | Optional integration surface; not a replacement inter-provider transport |
| RFC 3834 | Automatic response conventions | Loop prevention, not invisible delivery |
| RFC 2183 | Content disposition and unknown-value behavior | Unknown content is not a silent-discard mechanism |
| RFC 9788 | Cryptographic header protection | Protect selected metadata and evaluate legacy handling |
| Autocrypt and SecureJoin | In-band keys and verified introductions | Bootstrap and distributed trust candidates |
| PQXDH and Double Ratchet | Asynchronous establishment and evolving sessions | Prior art; not components of the selected MLS baseline |
| MLS and its architecture | Group establishment and separated service roles | Selected experimental baseline for two-person and larger managed conversations |
| AMP for Email | Restricted presentation and interactions | Prior art for rendering and action boundaries |

The linked sources in the other chapters support those descriptions. Additional sources for this table are [RFC 9078](https://www.rfc-editor.org/rfc/rfc9078.html), [RFC 8621](https://www.rfc-editor.org/rfc/rfc8621.html), and [RFC 2183](https://www.rfc-editor.org/rfc/rfc2183.html).

## Capability negotiation

Capabilities identify independently supported contracts. A client distinguishes rich rendering, interaction semantics, security protocols, and provider services. An advertisement must be scoped to the identity/device/service it describes and have a defined freshness rule.

An advertisement does not prove every client on a mailbox can decrypt. A server advertising relay support does not imply every local account supports end-to-end encryption. An unknown capability is unsupported, not permission to guess a compatible revision.

Authenticated session negotiation must bind relevant capabilities to the selected protocol. A missing or stripped advertisement cannot silently erase previously established identity evidence or bypass a policy requiring encryption.

### Capability scope and delivery state

The proposed capability model has three separate scopes:

| Scope | What it can establish | What it cannot establish by itself |
| --- | --- | --- |
| Transport peer | Negotiated features on the current server connection | Features on downstream hops or recipient devices |
| Account service | Authenticated services delegated for a particular mailbox, such as key publication or control-message routing | Possession of private keys by every device accessing that mailbox |
| Device or established session | Supported content/security profiles bound to that endpoint or session | Support by newly enrolled devices or undisclosed alias/list members |

A record includes its scope, subject, issuer, supported profile versions, validity interval and authentication evidence. The [passive device advertisement](passive-discovery.md) defines the experimental serialization and signature format for its narrow receiving-capability scope. The [configured provider-control profile](provider-control.md) defines a separate account-service exchange. Public account-service discovery and transport-peer advertisements remain outside that profile; the device format does not define them. Cached observations from one scope must not be promoted into another. A disappearance or expiry means capability knowledge is unavailable; it does not revoke established encryption policy.

SMTP acceptance after DATA means that the receiving server accepted responsibility for delivery or failure handling. It does not mean a person read the message, a device decrypted it, or an interaction was accepted. The application therefore tracks transport handoff, delivery evidence, decryption and interaction validation as separate facts. It must not infer later facts from an earlier one. Any receipts used to advance application state need their own authenticated contract.

Aliases and lists can expand beyond the addresses visible to the sender. VRFY, EXPN, forwarding replies and MX records must not supply cryptographic membership authority. A compatible list service needs an explicit group contract. Otherwise the sender's security policy determines whether delivery waits, fails or uses an allowed fallback. A transport relay must not decrypt or regenerate the message to make it fit a less capable downstream hop.

Sources: [RFC 5321 §§2–3](https://www.rfc-editor.org/rfc/rfc5321.html#section-2); [SMTP audit and coverage](audits/smtp.md).

> [!warn] No silent first-contact guarantee
> Without known key material or compatible discovery, an encrypted first message may need to wait, use a visible introduction, or follow an allowed fallback. Existing legacy clients cannot be assumed to discard an unfamiliar key request. A future provider service can remove this limitation for participating accounts.

The [transport chapter](transport.md) defines proposed per-recipient delivery states, retry identity and duplicate-processing requirements.

## Proposed acceptance scenarios

| Scenario | Expected behavior |
| --- | --- |
| Upgraded sender, legacy recipient | Readable questions and answers; no opaque mandatory interaction |
| Compatible clients, ordinary providers | Capability/key exchange can ride existing mail; provider upgrades are not required for every protected exchange |
| Recipient offline with published prekeys | Selected asynchronous protocol can establish a session without presence |
| Both endpoints online | Authenticated exchange may complete promptly without changing conversation identity |
| Legacy and upgraded clients share a mailbox | Document actual visibility and readability; do not promise invisible control traffic |
| Third recipient lacks encryption support | Apply selected fallback; accurately represent the resulting exposure |
| Known identity presents a replacement key | Preserve continuity evidence and apply the defined recovery/change procedure |
| Duplicated or reordered delivery | Do not duplicate submissions or invent causal order |
| Group membership changes concurrently | Selected group profile resolves or reports the conflict without inventing membership |
| Mailing list modifies the MIME body | Report authentication/structure consequences; retain a safe readable view where available |
| Link forwarded to another person | Enforce the stated bearer or identity-bound access model |
| Bcc delivery | No disclosure of hidden recipients in shared structured or cryptographic metadata |

These are acceptance objectives. Limited semantic experiments and site checks are recorded in the [validation evidence](validation.md); no complete client or real-provider interoperability has been tested against this draft.

## Contract coverage and remaining decisions

The linked chapters own the proposed behavior. “Defined” here means specified in this discussion draft, not adopted, implemented or security-reviewed. The evidence column distinguishes local implementation from remaining contract and deployment work.

| Area | Defined proposal | Local evidence and remaining work |
| --- | --- | --- |
| Events and interactions | [Answer buttons](messages.md#questions-and-answer-buttons), [edit semantics](interaction-state.md#message-edits), [event encoding](event-encoding.md) and exact references | Joined protected carriers cover buttons, reactions and resources; [plain-message edits](evidence/README.md#joined-protected-message-edits) add durable conflict/authority views and ordinary corrections. [Service authorization](service-authorization.md) joins local acquisition and signed account linking to the service path. Production login, independent clients and rich-content editing beyond the selected plain-message operation remain outside that evidence. |
| Rendering | [Finite HTML/CSS vocabulary and resource policy](presentation-profile.md) | Validate additional platforms and browser engines, native accessibility, decoder fidelity and remaining selected-source dependencies. [Isolated parsing and decoding](evidence/README.md#isolated-html-parsing) implement CPU/output/time enforcement and a memory watchdog; macOS has no demonstrated hard allocation ceiling or security sandbox |
| Security | [Protection boundaries](security.md) and [selected experimental MLS suite and credential/context encodings](security-profile.md) | Evaluate the selected lifecycle/effect boundaries across independent implementations and deployed recovery sources. Local signed exchange, candidate retention and atomic catch-up have [joined evidence](ordering-exchange.md#implementation-evidence); these do not establish distributed liveness or independent security assurance. The [managed restore path](identity-lifecycle.md#import-history-then-reconnect) keeps imported history inert and requires fresh device authority; encrypted backups and protected history transfer remain separate contracts. Local evidence includes instance-qualified reception, bounded retained-epoch processing and [atomic membership recovery](evidence/README.md#atomic-membership-recovery); the recovery path requires its explicit past-secret deletion policy and does not repair already-consumed legacy Commit keys |
| Identity and devices | [Transition authority, enrollment and recovery semantics](identity-lifecycle.md) | Integrate the selected recovery, pairing and own-account synchronization paths with deployed clients and accounts; independently evaluate their failure behavior. The [two-device pairing experiment](identity-lifecycle.md#pairing-another-device) now joins independent confirmations, signed enrollment and protected delivery through a local relay; camera scanning and deployed account integration remain unverified. The [local public-evidence coordinator](evidence/README.md#own-account-public-device-synchronization) joins exact enrollment approval, independent stores and protected delivery; it does not transfer old history. Optional [human comparison](mailbox-association.md#optional-human-comparison) has local strict-delivery integration; it confirms a correspondent through a separate trusted channel, not provider ownership. Durable successor acceptance and signed invitation admission have local integration evidence; [identity-state records and proofs](identity-state.md) retain their authority and freshness requirements. The managed restore experiment tests history-only import and fresh reconnection; it does not detect whole-machine rollback or reactivate archived keys |
| Discovery | Separate account/device/transport scopes and an [experimental passive attachment](passive-discovery.md) with exact signed assertion fields | Evaluate independent ownership verification, deployed own-account pairing and synchronization, public provider discovery and online exchange adapters. Local own-account public-evidence synchronization is implemented; it does not supply remote account-service integration. [Client-only onboarding](evidence/README.md#client-only-ordinary-mail-onboarding) joins ordinary-mail evidence to signed admission and protected replies under an explicit unverified-continuity policy; it does not prove mailbox ownership |
| Groups | [Administrator authority, explicit history sharing and membership semantics](group-conversations.md); MLS selected for managed groups | The [endpoint-quorum experiment](evidence/README.md#endpoint-quorum-ordering-experiment) adds signed ordering and local admission/delivery checks; signed-support recovery has local integration evidence; deployed synchronization and independent ordering evaluation remain separate. [Initial roster and delayed admission](evidence/README.md#generalized-initial-roster-and-delayed-admission) and [rich group membership](evidence/README.md#rich-group-membership-and-shared-mailboxes) have local sending, admission, removal and fresh-package rejoin evidence. [Atomic catch-up through a revoked member](group-conversations.md#catching-up-through-a-revoked-member) has local signed-support and crash/retry evidence; automatic retrieval from a configured mailbox spool has local evidence; live provider synchronization, legacy consumed-key recovery and independent interoperability remain unfinished |
| Fallback | [Remembered policy, hosted-access models and reply attribution](delivery-policy.md) | Extend the [joined bearer-access experiment](hosted-access.md), which now binds message/question disclosure, notification and observer replies, through production authorization, browser-code trust, recovery and deployed lifecycle validation |
| Reactions | [Exact-target reaction and withdrawal operations](reactions.md), local snapshot evaluation and readable projection | Broader localized/accessibility rendering, independent clients and deployed carriage. [Protected reaction delivery](evidence/README.md#protected-reaction-client-flow) includes durable receive/presentation, replay and withdrawal; [compound carriers](evidence/README.md#joined-protected-carriers-and-deliberate-attachment-download) integrate protected MIME. Ordinary RFC9078 projections do not authorize protected journal effects |
| Legacy reconstruction | [Reversible source mapping and uncertainty rules](rendering.md) | Extend the [synthetic plain-text and narrow HTML demo](evidence/README.md#inspectable-legacy-conversation-demo) to broader real-client HTML, observed localized quotation corpora and complete client integration. Attributed blockquotes, inert div wrappers and synthetic localized labels now have source-preservation checks |
| Provider control traffic | [Configured HTTPS exchange](provider-control.md), immutable signed records, scoped role credentials, retry behavior and resource bounds | Public discovery and credential lifecycle, deployed-provider and multi-client mailbox tests |
| Registration | [Candidate event media type and registration template](media-type-registration.md); unregistered status explicit | Finalize other required registrations, responsible contacts and stable references; submit through the applicable registry procedures |

## External standardization and adoption decisions

The draft can define behavior and supply reproducible experiments before a standards organization or vendor adopts it. The following decisions require participation beyond this repository. They do not excuse unfinished protocol definitions, missing source reviews or failures in the supplied tools.

| Decision | What this draft supplies | What remains external |
| --- | --- | --- |
| Standards venue and document ownership | An independent discussion draft, its compatibility analysis and explicit departures from existing guidance | Select a suitable venue with prospective participants and agree on document ownership. Hosting the draft on this site does not submit it or establish working-group support. |
| Names and registrations | Experimental identifiers and a [candidate media-type template](media-type-registration.md) | Confirm the final names, responsible contacts and stable references, then obtain the applicable registry review. Implementations must not advertise an experimental identifier as registered. |
| Independent interoperability | Requirement-linked examples, local experiments and [acceptance report formats](adoption.md#acceptance-tools-and-interoperability-program) | Independently developed clients and providers must run the same scenarios and publish versioned results. A second installation of the reference code is not an independent implementation. |
| Deployment and user experience | Explicit fallback policies, readable legacy copies and staged client/server integration paths | Providers and client developers choose whether to participate. Real-mail trials, accessibility evaluation and usability studies must establish what works for their users. No vendor commitment is assumed. |
| Security assurance | Defined trust boundaries, negative cases and recorded experimental limits | Independent protocol and implementation review must evaluate the selected design. Using an established cryptographic library does not review the surrounding identity, delivery or user-interface rules. |

Until those decisions have evidence, the corresponding claims remain unmade. Internal completion is tracked separately in the contract table above: an unavailable external reviewer does not make an incomplete recovery rule complete, and a complete recovery rule does not establish production security assurance.

## Next development step

Use the [audit inventory](audit-inventory.md) to identify inherited behavior and reviewed dependencies, and [validation evidence](validation.md) to distinguish implemented experiments from untested requirements. The selected contracts are testable draft choices; source reviews and local tests do not establish deployment readiness.

Use the supplied lifecycle cases when integrating a client: delayed history, removal, fresh-package admission, signed quorum catch-up and history-only restoration already have bounded local experiments. Exercise their composition with the client's actual mailbox, device stores and recovery sources. Local components must agree on authorization and durable state before they authorize effects; successful local fixtures do not establish deployed recovery or complete distributed liveness.

Then exercise two independent clients over real mail infrastructure. Test first contact, offline recipients, a new device and key loss as well as the normal conversation. Provider adoption must be tested separately from client support, following the [adoption plan](adoption.md). Independent interoperability and security review remain required before deployment claims.

## Discovery context changes

A session becoming authenticated or encrypted does not retroactively authenticate capability statements received before that transition. Refresh service capabilities in the established security context. Keep separately authenticated signed records under their own issuer, scope and freshness rules; do not confuse them with unauthenticated session hints.

Account login establishes access to an account service. It does not independently establish a correspondent's key, device roster or encryption readiness. The [POP SASL audit](audits/pop-sasl.md) supplies relevant prior art for discarding pre-security session knowledge.
