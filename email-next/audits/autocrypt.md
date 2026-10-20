---
title: Autocrypt Level 1 audit
sectionNav: true
---

# Autocrypt Level 1 audit

The complete prose, algorithms, examples and history of the retrieved [Autocrypt Level 1 specification](https://autocrypt.org/level1.html) were reviewed. The page identifies itself as 1.1.0 documentation and publishes under CC0. This is a versioned source review, not an IETF RFC review; it does not increase the RFC review count. Example ciphertext and keys were read as supplied data, not independently decrypted or verified.

Captured HTML SHA-256: `d5cf76e519684b89423770e4fde983d1e8e11f60ddcdbec55c35d76fcfa280b3`.

| Section | Disposition |
| --- | --- |
| Autocrypt Level 1: Enabling encryption, avoiding annoyances | Passive-adversary scope and compatibility-first goals are explicit; not an active-substitution defense. |
| Terminology | Terminology reviewed. |
| Keywords to indicate requirement levels | Requirement keywords use BCP14 conventions. |
| Overview | Overview reviewed. |
| Approach and High Level Overview | In-band public keys avoid mandatory directory infrastructure. |
| Requirements on MUA/E-mail Provider interactions | Requires raw message access and custom outgoing headers; arbitrary webmail access is insufficient. |
| Autocrypt Internal State | Peer and own-account state have separate roles. |
| Communication Peers | Youngest-message key state is not authenticated identity continuity. |
| Accounts controlled by the MUA | Own-key availability and preference are independent settings. |
| Peer State Management | Incoming mail drives peer observations. |
| The Autocrypt Header | From matching, critical attributes, duplicate valid headers and size limits reviewed. |
| OpenPGP Based key data | Five-packet minimized keys and legacy curve identifiers need RFC9580 compatibility analysis. |
| Header injection in outbound mail | Changing outgoing identity must change the advertisement; recipient-specific variations discouraged. |
| Internal state storage | Missing advertisements affect recommendations, not cryptographic revocation. |
| Updating Autocrypt Peer State | Effective-date processing can replace keys; reports, spam and multiple From addresses receive special handling. |
| Provide a recommendation for message encryption | Recommendations are usability decisions, not identity proofs. |
| Recommendation structure | Recommendation and target-key map are distinct outputs. |
| Recommendations for single-recipient messages | Single-recipient evaluation reviewed. |
| Determine if encryption is possible | Unusable keys are excluded before recommendation. |
| Preliminary Recommendation | Gossip-only and sufficiently stale direct advertisements discourage encryption. |
| Deciding to Encrypt by Default | Encrypted replies or mutual preferences can enable encryption by default. |
| Recommendations for messages to multiple addresses | Aggregate recommendation uses all recipients; recipient edits must not silently remove chosen encryption. |
| Message Encryption | PGP/MIME signs and encrypts to recipients and sender. |
| Cleartext replies to encrypted messages | Quote omission is only optional here; Email Next requires explicit authorization for disclosure. |
| Key Gossip | Gossip distributes visible-recipient keys inside encryption and excludes Bcc disclosure. |
| Key Gossip Injection in Outbound Messages | Placement, recipient matching and key selection reviewed; preference is not gossip authority. |
| Updating Autocrypt Peer State from Key Gossip | Gossip updates its own timestamp/key state rather than direct-key state. |
| Message Drafts | Draft encryption targets the author, not intended recipients. |
| Storing Draft State | Draft-only state must be stripped before sending; outer placement exposes metadata. |
| Autocrypt Gossip headers for drafts | Encrypted draft gossip helps another client resume without granting endpoint continuity. |
| Managing accounts controlled by the MUA | Local account management reviewed. |
| Secret key generation and storage | Ed25519/Cv25519 generation recommendation is not automatically the new protocol's cryptographic suite. |
| Secret key protection at rest | Routine password prompts discouraged; recoverability and storage protection require design. |
| Handling Multiple Accounts and Aliases | Shared peer cache can link accounts; aliases are separately represented. |
| Avoiding MUA Conflicts | Independently generated client keys can produce intermittently unreadable mail. |
| Autocrypt Setup Message | Explicit export enables portability but is not automatic device enrollment. |
| Message Structure | Self-addressed multipart setup contains readable instructions and encrypted secret material. |
| Setup Code | Generated code stays out of email; armor prefix deliberately reveals limited information. |
| Setup Message Creation | Creation requires user action and exports the selected account's key/settings. |
| Setup Message Import | Import requires user action and actual code-based decryption; cached decryption success is insufficient. |
| User Interface | Minimal UI does not eliminate fallback decisions. |
| Message Composition | Composition control reflects recommendation while allowing user choices. |
| Account Preferences | Disabling and preferences are account-specific. |
| Helping Users get Started | Mailbox scan helps avoid generating competing keys; scan window is a heuristic. |
| Disabling Autocrypt | Disabling preserves keys and old-message access by default. |
| Destroying Secret Key Material | Destruction is separately consequential and must explain loss of readable history. |
| Appendix | All appendix prose and examples reviewed. |
| E-mail Address Canonicalization | Local-part lowercasing is not adopted for Email Next endpoint identity; distinct exact addresses remain distinct. |
| Example Autocrypt headers | Header structure reviewed; embedded key validity not cryptographically tested. |
| Example Autocrypt Gossip headers | Encrypted gossip and displayed plaintext reviewed; ciphertext not decrypted in this audit. |
| Example Copy when a Reply can’t be Encrypted | Example explains missing encryption; not a guarantee all future messages can encrypt. |
| Example User Interaction for Setup Message Creation | Setup-code presentation reviewed. |
| Example User Interaction for Setup Message Receipt | Import prompt reviewed; example interface is not a binding enrollment protocol. |
| Example Setup Message | MIME, armor, supplied code and displayed secret payload reviewed; no decryption validation claimed. |
| Example Stored Draft | Draft example reviewed; prose says Draft-Header but actual field and normative section say Draft-State. |
| Document History | Version history reviewed; changes do not establish current deployed interoperability. |

## Decisions for Email Next

Retain passive advertisement as prior art for ordinary-mail bootstrap. Keep its candidate keys and compatibility recommendations separate from established endpoint authority. Do not import its local-part lowercasing into identity continuity. Enforce the sender's disclosure policy when quoting protected material, including when a legacy recommendation would permit cleartext. These are deliberate differences, not claims of Autocrypt conformance.

The [identity lifecycle](../identity-lifecycle.md) separates disabling new encrypted delivery from destroying historical access. Recovery must also preserve current revocation and device-authorization checks. Its setup-message flow demonstrates portable key recovery, but does not define the complete Email Next device enrollment protocol.

Remaining integration work includes OpenPGP packet/version reconciliation, cryptographic example checks, and an adapter tested with independent implementations. This audit does not claim those tasks are complete.
