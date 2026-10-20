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

## Separate conversations, separate authority

Each private conversation contains exactly two principals: the originator and one private recipient. Each may have multiple currently authorized devices. The originator creates the group. Device membership changes follow the existing signed authorization rules; they cannot add a third principal or leave either principal absent. Sharing with different people requires another independently authorized conversation.

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

Without common support for the required marker and context, hold protected private delivery or use an explicitly permitted alternative. Do not remove a hidden leaf from an audience declaration to simulate compatibility. Plaintext/hosted plans must be authorized before the corresponding protected declaration is released. A later disclosure is additional exposure; it cannot retroactively rewrite a delivered event's declaration.

::::

## Why this differs from RFC 9787

[RFC9787 §9.4.1](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.4.1) describes a certificate-based construction in which each blind copy is also decryptable by the named recipients. A member-visible MLS roster cannot reproduce that construction without exposing its membership. This profile instead gives each blind principal an independent conversation with the sender. Named recipients do not thereby gain access to the private copy or its replies.

The [existing mixed-protection rationale](delivery-policy.md#mixed-delivery-and-the-message-s-confidentiality-status) still applies when an ordinary or hosted fallback is authorized. Separate delivery does not restore confidentiality after broader disclosure.

## Local evidence and limits

The experiment covers signed initial admission, two-device principal coverage, separate visible/private questions over SMTP, a private answer that leaves visible answer state unchanged, exact retry, same-principal device addition with an established Welcome, rejection of a third principal, explicit ordinary fallback and exact attachment bytes. A loopback browser flow presents the private role and sends a private answer through actual protected SMTP. These are local fixtures, not deployed interoperability. See the [reproducible evidence](evidence/README.md#protected-private-copy-experiment) for exact checks and remaining limits.
