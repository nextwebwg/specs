---
title: Protected private copies
order: 4.7
blurb: blind recipients · private replies · separate audiences
sectionNav: true
---

# Protected private copies

Alice writes to Bob and privately copies Dana. Bob's protected conversation contains Alice and Bob. Dana receives an independently protected conversation containing Alice and Dana. Neither conversation contains a hidden MLS member.

> [!ex] A private answer stays private
> Alice sends “Which day works?” to Bob and privately copies Dana. Each conversation has its own question identity. Dana selects Friday in her private conversation. Alice sees Dana's private answer; Bob's question does not acquire an answer from Dana.

This experimental binding defines protected blind delivery, using the existing MLS, identity, invitation and exact-byte rules. It does not hide network traffic, prevent deliberate forwarding or establish independent-client interoperability.

The [current baseline](suite-profile.md#current-client-baseline) applies these pair-audience and disclosure boundaries to context10/authored0/envelope6 and slot reply-intent1. Private copies have independent scope roots and authored identities, never the visible group's pending slots or public correlation. Earlier numbered formats retain their own exact schemas and signed evidence; they cannot be converted in place.

## Bcc in the composer

Email/2 supports blind copying through this private-copy contract. The sender can choose Bcc alongside To and Cc, but a blind recipient is not added secretly to the visible protected audience. Each receives a separate sender–recipient conversation. Its private reply stays with the sender and does not become Reply all to the visible copy.

The original visible To/Cc list is not automatically copied into that private conversation. Names or addresses deliberately written in the body retain their actual disclosure; the protocol cannot make those words secret from their recipient. The [address-role contract](private-address-presentation.md#to-cc-and-bcc-remain-different) preserves these distinctions in composition and presentation.

## Separate conversations, separate authority

Each private conversation contains exactly two principals: the originator and one private recipient. Each may have multiple currently authorized devices. The originator establishes the original private-copy conversation. Current-suite ordinary return streams follow the [private-reply rules](#private-replies-in-the-current-agreement) below. Device membership changes follow the existing signed authorization rules; they cannot add a third principal or leave either principal absent. Sharing with different people requires another independently authorized conversation.

A private copy gets fresh conversation, event, MIME Message-ID and scoped resource identifiers. Its authenticated audience is the complete principal set for its own group. Copy correlation remains in the sender's local delivery records. No other group's identifiers, private recipient counts, shared delivery manifest or hidden history is transmitted to explain the relationship.

The recipient can still infer information from deliberately authored content. A private-copy label is not a guarantee against inference, collusion, transport metadata or a participant revealing their own involvement.

## Declare planned sharing without naming recipients

An author planning an additional protected audience includes the generic descriptor `{"kind":"separate-protected-copy"}`. It says that selected content is intentionally shared in another protected conversation. It does not say how many copies exist, identify a blind recipient, or assert delivery success. Visible and private copies carry their applicable disclosure declarations independently.

Plaintext and hosted sharing retain their separate descriptors. Encryption of one copy does not erase broader exposure. An empty declaration cannot prove that someone will never copy or forward the message.

A durable local plan authorizes the exact outgoing event bytes and copied resources/metadata for the actual destinations. Remembered policy may supply permission; this profile does not require a new confirmation dialog on every send. A readable preview cannot conceal additional transmitted metadata. Each route retains its own outcome and exact retry bytes. Database preparation and SMTP delivery are not one atomic transaction.

## Copy content without transplanting an author's authority

The originator may independently author the same message or question for each audience. A copied question has its own answer state. Resource bytes can be reused under fresh scoped identifiers with the existing digest, role and safe-opening checks.

An answer, reaction or edit cannot keep an active reference into a different conversation. Export its authorized readable statement and necessary context as a new message instead. A selected contribution written by someone else remains visibly quoted or forwarded content, authored as a forward by the person sharing it. It does not become a newly authenticated statement by the original author to the new audience.

The local experiment's automatic copy-plan API accepts self-contained locally authored messages, questions and resource contributions. It rejects foreign-author transplantation and target-dependent operations. It does not implement a transferable source-proof export format. The [history and forwarding rules](messages.md#conversation-history-and-forwarding) apply to deliberate quoted exports and raw-message exports separately.

## Reply privately by default

The authenticated private-copy role tells the client which principal is the private peer. A reply stays in that conversation. Outer To, Cc or Reply-To fields cannot add recipients or establish that role. If the user chooses other people, the client treats this as a new audience and makes the consequence—revealing participation—apparent under the effective disclosure policy.

Generated copies omit Bcc. Their routing and message identifiers belong to their independent delivery. They do not add cross-conversation References or In-Reply-To values. This profile does not authenticate ordinary outer headers; protected header presentation is a separate contract.

Forwarding selected content creates a new independently authorized contribution. Forward-as-attachment or raw export can expose private audience/context metadata and needs authorization for that complete source. Neither action grants membership in the original private group.

:::: {.details summary="Exact experimental versions and acceptance rules"}

### Contribution envelope 2

Envelope `2` has exactly the eight members of envelope `1`, with `version` equal to `"2"`. Existing operation schemas are unchanged. The disclosure array permits an optional singleton `separate-protected-copy` descriptor first, then an optional singleton `plaintext-email` descriptor, then unique provider-hosted descriptors ordered by canonical service origin. The new descriptor has exactly one member, `kind`. Unknown or duplicate descriptors fail. Envelope `1` does not accept the new kind.

### Conversation context 5

Context `5` has the context `4` members plus required `delivery`. Its application tuple has exactly `envelopeVersion`, `payload` and `operations`. The selected implemented branch requires envelope `"2"` and payload `"mime-rich-v0"`; no raw-event or body-only cross-product is inferred. Its operation vocabulary is answer, attachment-message, message, question, reaction, reaction-withdraw and rich-message, with existing sorted unique operation-list rules. Every admitted device must support the exact selected tuple and operation set.

`delivery` is exactly one of:

```json
{"kind":"ordinary-v0"}
```

```json
{"kind":"private-copy-v0","originator":"<principal>","recipient":"<different principal>"}
```

The placeholders above use the existing principal grammar. Private delivery requires exactly those two principals in the authenticated roster; both must remain present. The context, including delivery role and operation selection, is immutable. Ordinary delivery does not acquire the two-principal restriction.

### Signed discovery and invitations

Signed passive assertion `4` uses the existing assertion fields and exact tuple inventory, limited to the envelope2/rich-payload branch. Its signing domain is `email-next/passive-discovery/v4` followed by NUL, using the existing signed-payload framing. Existing assertion versions remain unchanged.

Initial targeted invitation `4` uses the existing targeted common-roster fields, with common roster `1`. Their signature domains are respectively `email-next/mls-new-conversation-invitation/v4` and `email-next/mls-initial-roster/v1`, followed by NUL. They bind context5 and one exact assertion4 proof per device. Creation anchor0 retains its unchanged exact payload-and-signature framing. The private originator must equal the authenticated creator principal.

Established invitation `4` uses the existing established fields with application proofs, binds context5/assertion4, and uses `email-next/mls-established-membership-invitation/v4` followed by NUL. The unchanged-context and current authority checks apply before release/admission; transition authorization also checks the resulting two-principal roster. These are separate exact branches, not widened old-version parsers.

### Retry, failure and fallback

Each route's original event and MIME bytes remain immutable on retry. Current authority, recipient evidence, policy and disclosure authorization are rechecked at release. A changed destination or content creates a new plan. An uncertain submission is not silently retried or counted as another route's success.

Without common support for the required marker and context, hold protected private delivery or use an explicitly permitted alternative. Do not remove a hidden leaf from an audience declaration to simulate compatibility. Plaintext/hosted plans must be authorized before the corresponding protected declaration is released. A later disclosure is additional exposure; it cannot retroactively rewrite a delivered event's declaration. The [copy-progression and frozen-disclosure contract](delivery-policy.md#a-waiting-delivery-is-different-from-missing-setup) distinguishes partial transport release from a different protected audience, and gates hosted content before notification.

::::

## Private replies in the current agreement

The original sender and the private recipient keep the same two-person conversation when either replies. Each sending device still owns its own encrypted stream. Being the original sender of a private copy does not make that person the only one allowed to send a reply.

The private-copy role and the current message's From/To roles describe different things. If Alice privately copies Dana, Alice remains the private-copy originator when Dana replies. Dana authors the reply, her personal address is its encrypted From, and Alice is its recipient. Bob is not added to either the reply or its metadata.

:::: {.details summary="Current-suite composition, private stream birth and disclosure isolation"}

### Preserve private roles across independent streams

For the current context10 agreement, preserve the retained originator/recipient pair independently of each stream owner. The [authored-record private boundary](event-encoding.md#asynchronous-authored-records-and-deliveries) additionally requires every scope-definition slot to name exactly one expected principal from that pair before encryption. No unresolved or outside-pair slot may hide outside the actual delivery map. Each private copy has its own scope root, authored identity and resource scope; it cannot reuse the visible group record. Current personal roles and addresses are in authored0 presentation, while envelope6 describes the actual delivery mappings. The return-stream admission and disclosure rules below still apply through that binding.

The earlier context8/envelope4 agreement uses the exact two-principal `private-copy-v0` delivery object already defined here. Its `originator` identifies the original private-copy sender and its `recipient` identifies that private peer. Neither field means the author of every future contribution or owner of every MLS stream.

For the original private-copy establishment, the creator/source owner is the originator. A later ordinary stream in that accepted private conversation may be owned by an authorized device of **either** role principal. That stream retains the exact original delivery object and conversation identifier. Its sole stream administrator is its actual owner principal, its complete principal audience remains the same pair, and only its owner device can author its application contributions and transitions. All identity/package/agreement/current-authority rules remain mandatory.

Before admitting a recipient-owned return stream, independently select the existing private conversation and exact role pair from previously accepted private-context evidence or an explicitly authorized trusted local selection retaining that evidence. Validate its provenance under the normal invitation/account rules. The incoming invitation, claimed subject, outer headers, or reply reference alone cannot establish that prior authorization. If that evidence is missing or conflicted, hold this admission for reconciliation; do not silently reverse the roles, merge an ordinary conversation or guess a relationship from a shared conversation ID. An explicitly new private-copy conversation instead follows its own fresh originator-owned establishment.

No new delivery member, wire flag or alternate interpretation of earlier contexts is introduced. Context5/6/7 admission retains its original creator and managed-group rules. Context8 ordinary mode separates the original role pair from the source owner as specified here. Managed mode retains its selected membership/administrator authority; ordinary source independence does not transfer managed administration. A fresh source supplies no historical plaintext or keys, and existing private replies/answers keep their exact target and two-person audience.

### Compose each copy as an independent disclosure

| Material | Required boundary |
| --- | --- |
| Protected subject, author date and personal From/To/Cc | Inside each current copy's authored0 presentation with its exact intended roles and eligible addresses; envelope6 separately accounts for the actual native audience. Earlier envelope4 retains its principal-role/address equality. Neither transport headers nor another copy supplies missing fields. |
| Private recipient and source relationship | Retain the complete relationship in the author's protected local plan. Other deliveries contain no hidden principal/device list, cross-copy event reference, count or correlation manifest. |
| Intentional additional protected sharing | Use the generic `separate-protected-copy` descriptor where applicable; it asserts a sharing plan, not a recipient identity/count or delivery receipt. |
| Ordinary or hosted disclosure | Authorize exact content and metadata before uploading/releasing. Keep the applicable plaintext/provider-hosted descriptors even when another route is encrypted. A failed route does not erase the exposure of one already uploaded or sent. |
| Indexed replies, quotations, answers, reactions and edits | Do not transplant active cross-conversation references into an automatic copy. Independently compose a permitted new self-contained contribution or an explicitly reviewed inert quotation/forward; do not strip the reference and pretend the original operation survived. |
| Resources and MIME identity | Use fresh scoped identifiers and exact authorized bytes for each copy. Inspect transmitted metadata, HTML/Microdata indexes, resource names/links and attachments, not only the visible text. Preserve the declared resource roles/digests and existing isolation rules. |
| Entry notifications and outer routing | Use the selected minimal notification/generic subject and actual authorized routes. Do not copy encrypted addresses, private labels, history or the author's complete delivery plan into them. Address masking additionally needs its actual relay and sealed-control gates. |

Private roles do not exempt sender and recipient mailbox associations from current validation. For Dana's reply the encrypted From must be Dana's eligible selected source mailbox, even though Alice remains `delivery.originator`. Contact labels are selected by the authenticated contribution principal, never by borrowing the originator's familiar identity or another claimed mailbox's contact name. The display separately preserves author-stated address/conflict assurance and transport facts.

A new reply has a new audience/disclosure plan. Previous permission for Alice to issue additional copies is not permission for Dana to do so. A private reply cannot implicitly address the original visible recipients. Deliberately choosing a new audience needs its own authorized composition and disclosure of participation; this chapter does not prescribe a general reply-all interface for ordinary mail.

### Acceptance requirements and evidence

Exercise Alice-to-Dana establishment, Dana-to-Alice return stream and Alice's next reply, including independently enrolled devices, restart and immutable retries. Preserve the role pair while actual source owners and encrypted From/To change. Reject an owner outside the pair, a third principal, an inverted pair selected only by incoming bytes, missing/conflicted prior private-context evidence, a copied visible-conversation reference and leaked private address in an ordinary/hosted notification. Verify Bob receives neither Dana's reply nor its identifiers, address metadata, resources or answer state.

The context/roster/private-role components check shape and independently supplied expected selection only. Historical configured private-copy, protected-presentation and address components retain their actual evidence scope. None is a joined current-suite private conversation or proof of relay/notification privacy, actual source admission, safe complete forwarding or independent interoperability.

::::

## Why this differs from RFC 9787

[RFC9787 §9.4.1](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.4.1) describes a certificate-based construction in which each blind copy is also decryptable by the named recipients. A member-visible MLS roster cannot reproduce that construction without exposing its membership. This profile instead gives each blind principal an independent conversation with the sender. Named recipients do not thereby gain access to the private copy or its replies.

The [existing mixed-protection rationale](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status) still applies when an ordinary or hosted fallback is authorized. Separate delivery does not restore confidentiality after broader disclosure.

## Local evidence and limits

The experiment covers signed initial admission, two-device principal coverage, separate visible/private questions over SMTP, a private answer that leaves visible answer state unchanged, exact retry, same-principal device addition with an established Welcome, rejection of a third principal, explicit ordinary fallback and exact attachment bytes. A loopback browser flow presents the private role and sends a private answer through actual protected SMTP. These are local fixtures, not deployed interoperability. See the [reproducible evidence](evidence/README.md#protected-private-copy-experiment) for exact checks and remaining limits.
