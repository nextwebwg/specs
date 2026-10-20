---
title: MLS architecture audit
sectionNav: true
---

# MLS architecture audit

The complete [RFC9750](https://www.rfc-editor.org/rfc/rfc9750.html), including all recommendations, figures, references and end matter, has been read. This is an Informational architecture document, not an application wire profile. Its one captured erratum is reconciled below. Dependency and current draft-status closure remain open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Informational architecture; does not itself define an interoperable application profile. |
| 2 | General Setting | General setting and complete diagram reviewed. |
| 2.1 | Protocol Overview | Asynchronous group key agreement is distinct from application delivery and identity. |
| 2.2 | Abstract Services | AS and DS are abstract roles; centralized, federated and client-distributed implementations are possible. |
| 3 | Overview of Operation | Complete formation diagram and narrative reviewed. |
| 3.1 | Step 1: Account Creation | Account creation is an illustrative application step, not a mandatory central authority. |
| 3.2 | Step 2: Initial Keying Material | Initial key publication enables offline invitations; refresh and consumption matter. |
| 3.3 | Step 3: Adding Bob to the Group | Commit and Welcome have different audiences; delivery service need not decrypt either. |
| 3.4 | Step 4: Adding Charlie to the Group | Additional member introduction requires a group transition and separate Welcome. |
| 3.5 | Other Group Operations | Application defines authorization; MLS membership alone does not establish administrative rights. |
| 3.6 | Proposals and Commits | Proposals do not apply changes; commits may embed proposals or perform empty updates. |
| 3.7 | Users, Clients, and Groups | Client, user and member differ; invitation does not prove Welcome receipt or successful joining. |
| 4 | Authentication Service | All three AS functions reviewed; PKI, user verification and transparency are alternatives; cross-group client consistency detects rather than prevents ghosts. |
| 5 | Delivery Service | Directory and routing roles separated; malicious delivery can block progress without reading payloads. |
| 5.1 | Key Storage and Retrieval | Per-client version/suite KeyPackages, single-use consumption, last-resort risks and private-key deletion reviewed. |
| 5.2 | Delivery of Messages | Proposal dependencies and one accepted Commit per epoch require application coordination; transport arrival is insufficient. |
| 5.2.1 | Strongly Consistent | Ordered broadcast and first-valid processing require an actual shared ordering service, not local first arrival. |
| 5.2.2 | Eventually Consistent | Delay/tie-break and rollback approaches require explicit convergence and retention policies; finite waiting does not prove all contenders arrived. |
| 5.2.3 | Welcome Messages | Welcome acceptance must match winning transition; reinitialization takeover races require the same agreement discipline. |
| 5.3 | Invalid Commits | Invalid commits can desynchronize filtering servers; automatic external rejoin can revive compromised history and weaken PCS. |
| 6 | Functional Requirements | Scale aims do not establish application performance guarantees. |
| 6.1 | Membership Changes | Membership changes must be known; user operations map to devices; external joins remain subject to application authorization. |
| 6.2 | Parallel Groups | Healing one group does not heal another; exported PSK cross-group linkage requires a separately defined mechanism. |
| 6.3 | Asynchronous Usage | MLS does not require simultaneous presence; application delivery and coordination may impose availability constraints. |
| 6.4 | Access Control | Encrypted handshakes require consistent client-enforced policy; external-sender permission does not grant arbitrary group control. |
| 6.5 | Handling Authentication Failures | Credential validation, invalidity response and proactive replacement must be consistent across participants. |
| 6.6 | Recovery After State Loss | State-loss rejoining does not restore missed history; recovery PSK distribution and survival require a separate design. |
| 6.7 | Support for Multiple Devices | New device is a new client; history transfer is outside MLS and changes retention risk. |
| 6.8 | Extensibility | KeyPackage and group extensions provide capability and shared-context hooks. |
| 6.9 | Application Data Framing and Type Advertisements | Application framing and migrations need a concrete profile; visible AAD is authenticated but not confidential. |
| 6.10 | Federation | Federation requires compatible identity, suite, content and infrastructure contracts. |
| 6.11 | Compatibility with Future Versions of MLS | Authenticated capabilities support version selection; withholding advertisements and application fallback remain separate threats. |
| 7 | Operational Requirements | Every listed service, lifetime, reorder bound, encoding, proposal policy, credential-equivalence rule and operational choice reviewed; concrete profile still required. |
| 8 | Security and Privacy Considerations | Network-attacker model reviewed; transport confidentiality protects metadata independently of message encryption. |
| 8.1 | Assumptions on Transport Security Links | Transport security remains useful; group and traffic metadata can correlate participants. |
| 8.1.1 | Integrity and Authentication of Custom Metadata | Public routing metadata belongs in authenticated AAD when needed; secrets belong inside encryption. |
| 8.1.2 | Metadata Protection for Unencrypted Group Operations | Public handshakes over unprotected transport expose group structure. |
| 8.1.3 | DoS Protection | Transport and admission controls mitigate resource abuse; MLS alone is not a DoS solution. |
| 8.1.4 | Message Suppression and Error Correction | Generation gaps indicate missing messages, not cause; sequencing simplification must be reconciled with invalid-commit handling in 5.3. |
| 8.2 | Intended Security Guarantees | Security guarantees are conditional on identity, state handling and threat model. |
| 8.2.1 | Message Secrecy and Authentication | Payload authentication includes signatures; padding only mitigates length leakage. |
| 8.2.2 | Forward Secrecy and Post-Compromise Security | Deletion and processed honest updates govern FS/PCS; offline stale state remains a risk. |
| 8.2.3 | Non-Repudiation vs. Deniability | No general deniability claim; abuse evidence and third-party proof are separate application choices. |
| 8.2.4 | Associating a User's Clients | Distinct device leaves leak device activity; shared state requires synchronization and can impair compromise recovery. |
| 8.3 | Endpoint Compromise | All enumerated compromise models reviewed separately. |
| 8.3.1 | Compromise of Symmetric Keying Material | Key, ratchet and group secret compromises differ in scope and recovery. |
| 8.3.1.1 | Compromise of AEAD Keys | AEAD success proves neither unique sender nor signature validity; one key does not derive the ratchet. |
| 8.3.1.2 | Compromise of Ratchet Secret Material | Ratchet compromise exposes future generations of that chain in the epoch, not deleted prior generations. |
| 8.3.1.3 | Compromise of the Group Secrets of a Single Group for One or | Passive versus active recovery claims require reconciliation with the stated uncompromised-signature premise. |
| 8.3.2 | Compromise by an Active Adversary with the Ability to Sign | Signing-oracle access permits legitimate-client operations even without extracting the key. |
| 8.3.3 | Compromise of Authentication with Access to a Signature Key | Extracted signing keys require credential replacement/invalidation; captured reported erratum 8665 supplies identical original and correction. |
| 8.3.4 | Security Considerations in the Context of a Full State | Full compromise exposes retained plaintext; secure hardware and compartmentalization assist but do not establish recovery alone. |
| 8.4 | Service Node Compromise | Service compromise reviewed independently of endpoint compromise. |
| 8.4.1 | General Considerations | Service privacy mechanisms do not imply end-to-end secrecy from services. |
| 8.4.1.1 | Privacy of the Network Connections | Network addresses and timing remain visible; anonymity needs additional architecture. |
| 8.4.1.2 | Storage of Metadata and Encryption at Rest on the Servers | Server-at-rest encryption with server-accessible exported keys is not endpoint-only content encryption. |
| 8.4.2 | Delivery Service Compromise | Malicious DS can suppress, serve stale keys and exploit weak identity binding; broad detection claim qualified by 5.2 and 8.6. |
| 8.4.2.1 | Privacy of Delivery and Push Notifications | Push tokens and synchronized fanout reveal device associations even with encrypted payloads. |
| 8.4.3 | Authentication Service Compromise | AS can misbind identities; generating private endpoint keys on AS permits impersonation. |
| 8.4.3.1 | Authentication Compromise: Ghost Users and Impersonation | Ghost devices, transparency and out-of-band checks reviewed; per-client authentication_secret wording conflicts with RFC9420 group-epoch authenticator semantics. |
| 8.4.3.2 | Privacy of the Group Membership | Group membership and reused signature keys reveal associations; encrypted handshakes reduce but do not eliminate metadata. |
| 8.5 | Considerations for Attacks Outside of the Threat Model | Physical attack scope and correct-implementation assumptions read; hardware is defense in depth. |
| 8.6 | No Protection Against Replay by Insiders | Insiders can re-encrypt signed content with fresh generations; authenticated application event IDs must prevent repeated effects. |
| 8.7 | Cryptographic Analysis of the MLS Protocol | All cited analysis versions/scopes read as references, not proofs of this application or implementation. |
| 9 | IANA Considerations | No IANA actions; this architecture does not register an Email Next profile. |
| 10 | References | Complete reference list reviewed. |
| 10.1 | Normative References | RFC5116 normative dependency remains open; RFC9420 base review complete. |
| 10.2 | Informative References | Extension, federation, transparency and proxy draft revisions need current-status resolution; referenced research not independently audited. |

## Email transport and distributed coordination

Existing mail infrastructure can carry messages and published key material, but ordinary SMTP delivery does not provide a shared order for competing group transitions. The architecture explicitly assigns this problem to delivery services and clients. Its eventually consistent alternatives are design sketches: a local wait does not establish that every client has seen the same competing commits, and rollback retains secrets and can strand application messages or welcomes on a discarded branch.

An Email Next profile must choose a coordination mechanism and state its partition behavior. Provider upgrades may supply an ordering service without becoming trusted to read content. Clients must still validate the ordered candidates: a provider cannot declare an invalid encrypted commit valid. Automatically rejoining on an invalid commit would allow an attacker to trigger recovery against stale state.

## Authenticated replay versus delivery duplication

Section 8.6 distinguishes an insider's replay from an exact duplicate ciphertext. A member can re-encrypt another member's signed content under a fresh generation. A ratchet-generation deduplication check alone therefore cannot protect a form submission or conversation operation. The authenticated application event identifier must survive such re-encryption and suppress repeated effects.

## Errata and source tensions

Captured erratum [8665](https://www.rfc-editor.org/errata/eid8665) is Reported, technical, against Section 8.3.3. Its original and proposed correction are identical and its note only alleges a logical contradiction. It supplies no usable replacement wording. The draft retains the requirement to replace compromised signing credentials and invalidate old authority; it does not treat the report as an approved correction.

Section 8.4.3.1 calls authentication_secret a per-client secret generated for each user. RFC9420 instead defines it in the group epoch key schedule and exposes it as the epoch authenticator. Email Next follows the protocol definition: comparison establishes agreement on an epoch under a separately authenticated comparison procedure, not a permanent per-person identity credential.

Section 8.3.1.3 introduces a compromise without signature-key access, then describes an active attacker performing updates on the victim's behalf. That latter capability is not established by the stated premise alone. Recovery claims must identify the attacker's signing capability rather than importing the paragraph as an unconditional result. Likewise, broad replay/detection language in Section 8.4.2 is constrained by the explicit limitations in Sections 5.2 and 8.6.

Section 8.1.4's suggestion that multiple commits need not be delivered must be read with Section 5.3: an opaque invalid candidate cannot permanently consume the only transition slot. Section 8.4.1.2's server-accessible at-rest keys must not be presented as end-to-end confidentiality from that server.

## Remaining dependency work

The document references specific work-in-progress revisions of MLS extensions, federation, key transparency and MASQUE proxy documents. These references are not adopted as current or finalized by this audit. RFC5116, referenced transport/PKI specifications and the research papers require their own scoped review where used. A cited cryptographic analysis of an earlier MLS draft does not validate Email Next's application binding.
