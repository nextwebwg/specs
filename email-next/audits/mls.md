---
title: Messaging Layer Security audit
sectionNav: true
---

# Messaging Layer Security audit

The complete [RFC9420](https://www.rfc-editor.org/rfc/rfc9420.html), all structures, algorithms, figures, tables, appendices, references and end matter have been read. All five captured errata are covered in the [errata reconciliation](mls-errata.md). This base-text audit does not establish a complete Email Next MLS binding, dependency closure or verified implementation.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Asynchronous group key establishment supports offline recipients; does not supply application identity or delivery semantics. |
| 2 | Terminology | All terms reviewed; client is a cryptographic endpoint, not necessarily one person. |
| 2.1 | Presentation Language | TLS presentation language plus MLS-specific encodings reviewed. |
| 2.1.1 | Optional Value | Presence byte accepts only zero or one. |
| 2.1.2 | Variable-Size Vector Length Headers | Minimal 1/2/4-byte lengths required; prefix 11 invalid; wire maximum does not authorize unbounded allocation. |
| 3 | Protocol Overview | Trusted authentication service distinguished from largely untrusted delivery service. |
| 3.1 | Cryptographic State and Evolution | Ratchet tree, key schedule and secret tree have separate responsibilities. |
| 3.2 | Example Protocol Execution | All flows reviewed; proposals do not apply changes until committed; regular updates and access control are application responsibilities. |
| 3.3 | External Joins | External joining needs current GroupInfo and application authorization. |
| 3.4 | Relationships between Epochs | Reinitialization, branching and resumption links reviewed; they do not imply history disclosure. |
| 4 | Ratchet Tree Concepts | Tree structure supports efficient exclusion and updates. |
| 4.1 | Ratchet Tree Terminology | Complete binary tree terminology; internal representation unconstrained. |
| 4.1.1 | Ratchet Tree Nodes | Resolution ordering, blanks and unmerged leaves reviewed with examples. |
| 4.1.2 | Paths through a Ratchet Tree | Direct, copath and filtered paths reviewed with full table. |
| 4.2 | Views of a Ratchet Tree | Tree invariant restricts private-key knowledge; descendants need not know every ancestor key. |
| 5 | Cryptographic Objects | All cryptographic object definitions read. |
| 5.1 | Cipher Suites | Single suite selects HPKE, hash, MAC and signature primitives. |
| 5.1.1 | Public Keys | Opaque public-key formats depend on selected primitive. |
| 5.1.2 | Signing | Signature algorithms and labeled signing structures reviewed. |
| 5.1.3 | Public Key Encryption | HPKE Base mode uses labeled context; ciphertext purposes remain distinct. |
| 5.2 | Hash-Based Identifiers | KeyPackage and proposal references hash distinct labeled encodings; KDF wording requires reconciliation. |
| 5.3 | Credentials | Basic credential is bare identity assertion; application supplies reference identity and validation. |
| 5.3.1 | Credential Validation | All credential-introduction events require AS validation; replacement additionally requires authorized succession. |
| 5.3.2 | Credential Expiry and Revocation | Expiry, renewal, historical signatures and revocation need distinct application policies. |
| 5.3.3 | Uniquely Identifying Clients | Leaf index epoch-scoped; account identity may span devices; application_id is not AS-authenticated. |
| 6 | Message Framing | All structures read; application messages require PrivateMessage. |
| 6.1 | Content Authentication | Sender-specific keys, signed context and commit confirmation reviewed; AEAD alone insufficient. |
| 6.2 | Encoding and Decoding a Public Message | Public member messages require membership tag and valid authentication data. |
| 6.3 | Encoding and Decoding a Private Message | Private framing leaves group, epoch, type and authenticated_data visible. |
| 6.3.1 | Content Encryption | Zero padding, unused generation, persistent state, reuse guard and AEAD bounds reviewed. |
| 6.3.2 | Sender Data Encryption | Sender data derives protection from ciphertext sample; indicated leaf must be non-blank. |
| 7 | Ratchet Tree Operations | All tree operations reviewed. |
| 7.1 | Parent Node Contents | Parent public key/hash and sorted unmerged-leaf indices reviewed. |
| 7.2 | Leaf Node Contents | Signed leaf capabilities, source-specific fields and lifetime maximum are application-relevant requirements. |
| 7.3 | Leaf Node Validation | All credential/signature/capability/lifetime/source/unique-key checks reviewed; default-list tension retained. |
| 7.4 | Ratchet Tree Evolution | Fresh path/node derivation reviewed; obsolete leaf_secret figure covered by reported8211. |
| 7.5 | Synchronizing Views of the Tree | Full synchronization sequence, derived-public-key comparison and obsolete-secret deletion reviewed. |
| 7.6 | Update Paths | Exact ordered encrypted resolution excludes new leaves; provisional context binds HPKE. |
| 7.7 | Adding and Removing Leaves | Extension/truncation operations and examples reviewed; internal algorithms not mandated. |
| 7.8 | Tree Hashes | Tree hash commits current node contents and blank status. |
| 7.9 | Parent Hashes | Original sibling hash accounts for unmerged leaves; verified8031 editorial correction applied. |
| 7.9.1 | Using Parent Hashes | Signed parent hashes attest key introduction and recipient subtree. |
| 7.9.2 | Verifying Parent Hashes | All non-blank parents require valid chains; rejected8032 does not change D to C. |
| 8 | Key Schedule | Complete derivation diagram and purpose-separated secret table reviewed. |
| 8.1 | Group Context | Constant group ID, incrementing epoch, tree/transcript commitment and extensions reviewed. |
| 8.2 | Transcript Hashes | Confirmed/interim transcript formulas and diagram reviewed; not application-message history. |
| 8.3 | External Initialization | External initialization uses HPKE exporter to establish new init secret. |
| 8.4 | Pre-Shared Keys | Ordered PSK mixing, fresh nonce and storage/compromise caveats reviewed. |
| 8.5 | Exporters | Exporter label/context purpose separation and epoch refresh reviewed. |
| 8.6 | Resumption PSK | Historical resumption-secret retention needs application upper bound. |
| 8.7 | Epoch Authenticators | Epoch authenticator needs secondary verification protocol; does not permanently verify future epochs. |
| 9 | Secret Tree | Secret-tree derivation and separate handshake/application ratchets reviewed. |
| 9.1 | Encryption Keys | Single-use per-generation key/nonce and derivation formulas reviewed. |
| 9.2 | Deletion Schedule | Consumed secrets and ancestors deleted in all representations; bounded unused keys may support reordering. |
| 10 | Key Packages | Signed single-use packages, unique init keys, version agreement and advertised capabilities reviewed. |
| 10.1 | KeyPackage Validation | Suite/version, valid leaf/signature and distinct init/encryption keys required. |
| 11 | Group Creation | One-member initialization, best shared parameters and unique group ID reviewed. |
| 11.1 | Required Capabilities | Required capabilities constrain admission and configuration changes. |
| 11.2 | Reinitialization | ReInit links replacement group via post-transition resumption PSK; offline initiator recovery wording needs reconciliation. |
| 11.3 | Subgroup Branching | Branch uses fresh packages and authenticated subset; usage restrictions reviewed. |
| 12 | Group Evolution | Membership/key changes occur through committed proposals. |
| 12.1 | Proposals | Signed current-epoch proposals cached by authenticated reference. |
| 12.1.1 | Add | Valid package added at leftmost blank leaf; unmerged ancestors updated. |
| 12.1.2 | Update | Update replaces sender leaf and blanks direct path. |
| 12.1.3 | Remove | Remove requires occupied leaf and truncates emptied right subtrees. |
| 12.1.4 | PreSharedKey | PSK usage/nonce checks and ordering reviewed. |
| 12.1.5 | ReInit | ReInit cannot lower protocol version; old group closes. |
| 12.1.6 | ExternalInit | ExternalInit confined to external commits. |
| 12.1.7 | GroupContextExtensions | Extensions wholesale replacement; validate resulting membership capabilities. |
| 12.1.8 | External Proposals | External proposals require authorization and restricted types; public framing necessary. |
| 12.1.8.1 | External Senders Extension | External sender credentials/keys explicitly provisioned in group context. |
| 12.2 | Proposal List Validation | All regular/external list restrictions reviewed; reported8815 missing-reference rule not adopted as verified erratum. |
| 12.3 | Applying a Proposal List | Configuration, updates, removes, ordered adds and ordered PSKs applied in specified sequence. |
| 12.4 | Commit | Observed valid proposals precede application sends; omissions possible; empty/partial/full path requirements distinguished. |
| 12.4.1 | Creating a Commit | Complete commit/Welcome construction read; stale prose fields recorded for reconciliation. |
| 12.4.2 | Processing a Commit | Complete validation before installing current state; removal/reinit stops sends; path-list discrepancy retained. |
| 12.4.3 | Adding Members to the Group | Signed GroupInfo and unique group identity reviewed. |
| 12.4.3.1 | Joining via Welcome Message | All Welcome checks read: tree, own leaf, keys, confirmation and reinit/branch membership. |
| 12.4.3.2 | Joining via External Commits | External commits require path and no referenced proposals; resync takeover risk and PSK wording recorded. |
| 12.4.3.3 | Ratchet Tree Extension | Trimmed in-order tree encoding, padding, root verification and confidentiality of external retrieval reviewed. |
| 13 | Extensibility | All extension mechanisms reviewed. |
| 13.1 | Additional Cipher Suites | Suite agility balanced against common interoperability baseline. |
| 13.2 | Proposals | Non-default proposals require support by processing members. |
| 13.3 | Credential Extensibility | Credential support must preserve mutual authentication. |
| 13.4 | Extensions | Unknown optional fields ignored, duplicate extensions forbidden, group-context extensions mandatory; reported8745 noted. |
| 13.5 | GREASE | All GREASE placements reviewed; advertised GREASE excluded from local capability intersection. |
| 14 | Sequencing of State Changes | Conflict resolution required; candidate does not change current state; Welcome withheld until acceptance; fork retention bounded. |
| 15 | Application Messages | Per-epoch application protection and local secret deletion reviewed. |
| 15.1 | Padding | Padding reduces some length leakage but must respect transport size limits. |
| 15.2 | Restrictions | AEAD limits and applying transitions before new application encryption required. |
| 15.3 | Delayed and Reordered Application Messages | Separate skipped-key age/count and maximum ratchet-advance limits needed. |
| 16 | Security Considerations | Security claims read with architecture/dependency limitations. |
| 16.1 | Transport Security | Secure transport recommended for metadata and interference protection. |
| 16.2 | Confidentiality of Group Secrets | Tree invariant enables exclusion and key replacement. |
| 16.3 | Confidentiality of Sender Data | Sender-data security depends on distinct secrets, ciphertext sampling and AEAD properties. |
| 16.4 | Confidentiality of Group Metadata | All exposed object/field categories reviewed. |
| 16.4.1 | GroupID, Epoch, and Message Frequency | Delivery service sees group ID, epoch and message frequency. |
| 16.4.2 | Group Extensions | Public proposals or unprotected external GroupInfo disclose extensions. |
| 16.4.3 | Group Membership | Trees, proposals and KeyPackage-reference correlation can reveal membership. |
| 16.5 | Authentication | Group membership authentication differs from individual signature authentication; signing-key compromise enables impersonation. |
| 16.6 | Forward Secrecy and Post-Compromise Security | PCS begins after processed update; FS depends on deletion by all relevant members; offline members increase exposure. |
| 16.7 | Uniqueness of Ratchet Tree Key Pairs | Leaf and parent key uniqueness checks required. |
| 16.8 | KeyPackage Reuse | Single-use package deletion, last-resort reuse risk and request rate limiting reviewed. |
| 16.9 | Delivery Service Compromise | Compromised delivery service can censor updates, starve commits and hinder PCS. |
| 16.10 | Authentication Service Compromise | Compromised identity authority can introduce impersonators; transparency/cross-signing are application mechanisms. |
| 16.11 | Additional Policy Enforcement | Additional access/rate policies needed; transport policy does not replace client authorization. |
| 16.12 | Group Fragmentation by Malicious Insiders | Malicious paths can fragment offline members; subtree acknowledgments trade availability for detection. |
| 17 | IANA Considerations | Registry procedures and initial contents reviewed; selected suite, basic credential and private-use extension range reconciled below. Other registry entries remain separate. |
| 17.1 | MLS Cipher Suites | All seven suites and mappings read; suite 0x0001 mandatory for MLS1.0. |
| 17.2 | MLS Wire Formats | All five wire formats and private-use range reviewed. |
| 17.3 | MLS Extension Types | Extension codepoints and permitted placements reviewed. |
| 17.4 | MLS Proposal Types | External/path-required properties and all proposal registrations reviewed. |
| 17.5 | MLS Credential Types | Basic/X509, GREASE and private-use credential assignments reviewed. |
| 17.6 | MLS Signature Labels | All signature labels reviewed; extension labels require collision avoidance. |
| 17.7 | MLS Public Key Encryption Labels | HPKE purpose labels reviewed. |
| 17.8 | MLS Exporter Labels | Application exporter labels need distinct registration; initial registry empty. |
| 17.9 | MLS Designated Expert Pool | Expert process read; no registration submitted or approval claimed. |
| 17.10 | The "message/mls" Media Type | message/mls is binary; embedded version takes precedence over MIME parameter; email transfer encoding needs reconciliation. |
| 18 | References | All references read. |
| 18.1 | Normative References | Selected HPKE, TLS and KDF source reviews are recorded separately in the review index; citation review alone does not establish dependency closure. |
| 18.2 | Informative References | Architecture and AEAD draft successors, cryptographic analyses and prior art remain separate research work. |
| Appendix A | Protocol Origins of Example Trees | Every example-tree construction sequence reviewed. |
| Appendix B | Evolution of Parent Hashes | Complete parent-hash evolution reviewed; stale individual links can coexist with valid complete coverage. |
| Appendix C | Array-Based Trees | All array algorithms, including both common-ancestor routines, read; not production verification. |
| Appendix D | Link-Based Trees | All linked-tree code and end matter read; empty/single-leaf boundary handling needed before reuse. |

## Consequences for the proposal

MLS supplies asynchronous authenticated group key establishment, not automatic mailbox identity, mail ordering or recovery. The [group contract](../group-conversations.md), [identity lifecycle](../identity-lifecycle.md), [capability discovery](../capability-discovery.md), [security requirements](../security.md) and [validation plan](../validation.md) record the application responsibilities identified in this review.

The [selected security profile](../security-profile.md) defines the credential encoding and common suite. The invitation, group and identity chapters define package consumption, durable admission, delayed-message handling and recovery, with local experiments recorded in the validation chapter. Remaining ordering-exchange and lifecycle questions are identified in the group contract; the completed components do not establish a complete interoperable application. Source review, registry assignments and implementation evidence remain distinct. No claim of universal legacy-client handling or invisible control-mail delivery follows from this audit.

## Selected registry bindings

The [IANA MLS registry](https://www.iana.org/assignments/mls/) identifies suite `0x0001` as the selected X25519/AES-128-GCM/SHA-256/Ed25519 suite and credential type `0x0001` as `basic`. The extension range `0xF000–0xFFFF` remains private use. The experiment's `0xFF00` context is inside that range; this is not an Email Next allocation or a guarantee against collisions.

The corresponding [HPKE registry](https://www.iana.org/assignments/hpke/) identifies KEM `0x0020` as DHKEM(X25519, HKDF-SHA256), KDF `0x0001` as HKDF-SHA256 and AEAD `0x0001` as AES-128-GCM. The AEAD sizes are 16-byte keys, 12-byte nonces and 16-byte tags. These entries describe identifiers and parameters, not implementation validation.

These selected entries were reconciled against retained registry snapshots on 20 October 2026. This check does not cover every MLS extension, proposal, exporter label or future suite, and it does not register the experimental application identifiers.

The selected group worker uses the registered private-message (`0x0002`), Welcome (`0x0003`) and KeyPackage (`0x0005`) wire types. Its embedded tree and mandatory application-context support use `ratchet_tree` (`0x0002`) and `required_capabilities` (`0x0003`). Add (`0x0001`), Remove (`0x0003`) and GroupContextExtensions (`0x0007`) identify its selected proposal operations. These values were checked against the same MLS snapshot. A self-update's UpdatePath is not evidence that the application accepts standalone Update proposals; unsupported transitions retain their own rejection rules.
