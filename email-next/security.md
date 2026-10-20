---
title: Security and discovery
order: 7
blurb: automatic keys · distributed trust · delivery policies
sectionNav: true
---

# Security and discovery

Email Next should establish encryption as part of an ordinary conversation. People keep their email addresses. Their clients find compatible devices, remember the keys they have already used, and show when a delivery would expose the conversation more widely.

> [!ex] A conversation becomes encrypted
> Alice sends Bob an ordinary email. Her client includes a small advertisement of the features and public key material it supports. Bob's compatible client learns from that message and supplies its own material in a reply. Once their clients have enough authenticated information, later messages can use protected delivery. Bob does not have to be online whenever Alice writes.
>
> The first exchange does not retroactively encrypt earlier mail. Carol's older client continues to receive readable email under the sender's chosen policy.

## What “encrypted” means

**Encryption answers who can read this copy. Identity checks answer which device it belongs to.** A client needs both before it can describe a message as protected for the intended participants.

A provider can carry encrypted messages and publish public keys without holding the private keys that decrypt them. If a provider-operated service does hold usable decryption keys, the interface must identify that service as having access. Encryption does not conceal all routing addresses, timing, message sizes or headers.

> [!norm] Keep the claims separate
> A successful server connection, domain signature or JSON parse must not become a verified-person badge. Successful decryption alone must not authorize a form submission or other conversation action. The client checks the author, audience and requested action separately.

The [managed-conversation profile](security-profile.md) proposes MLS 1.0 for both two-person and larger conversations. It is an experimental selection, not a completed security assurance. Its [identity and enrollment contracts](identity-lifecycle.md), [managed restore path](identity-lifecycle.md#import-history-then-reconnect) and ordering experiments need independent review and interoperability evidence before deployment assurance.

### Where the endpoint runs

> [!ex] A browser interface with server-side decryption
> Bob reads mail in a browser, but the service decrypts it on its server. That service has plaintext access, regardless of the interface's appearance.

Define the endpoint by where usable keys and plaintext are processed. A remote agent that decrypts or signs belongs inside the disclosed trust boundary. Ciphertext storage and public-key publication do not by themselves require that authority. For browser cryptography, identify both key custody and who can replace the executing code; browser-local keys alone do not establish protection from that operator. Provider-blind claims require a deployment-specific runtime-integrity model and evidence.

::: {.details summary="Responsibilities of devices, providers and witnesses"}

### Distribute responsibilities

| Actor | Proposed role | Boundary |
| --- | --- | --- |
| Device | Generate secrets, establish sessions, encrypt and decrypt | Private endpoint keys do not become provider directory data |
| Existing trusted device | Authorize another device and transfer protected state | Account login alone is not automatically equivalent to device authorization |
| Email provider | Carry messages and optionally publish key material or relay exchanges | Discovery authority does not grant plaintext access |
| Independent witness | Check consistency of key publication | Candidate extension; independence and privacy need definition |
| Conversation participant | Introduce another participant | Introduction evidence identifies its source and is scoped; it does not imply universal trust |

No single global directory is required by this proposed architecture. The [configured provider-control profile](provider-control.md) supports an explicitly authorized service, including a target service operated by another provider. Public service discovery and automatic credential acquisition remain unselected; configured access does not supply those interfaces.

:::

## Finding a compatible client

Discovery starts with information carried in normal messages. Before support is known, a client should not send a stream of probe emails that an older client might display.

Once support is established, the clients can use a defined control exchange. Upgraded providers may help route that traffic away from the inbox, publish public admission material for offline devices, or relay a live exchange. Neither provider support nor simultaneous presence proves the identity of the other person.

> [!ex] Both devices happen to be online
> Alice and Bob can refresh their session through a relay or direct connection. They still authenticate the exchange against their known identities. If Bob goes offline, ordinary asynchronous delivery remains available; the conversation does not become dependent on a live connection.

There is no universal “discard this control email” header. A compatible client may hide recognized protocol traffic; another client using the same mailbox may still show it. Existing automatic-response headers prevent some loops, but do not make mail invisible.

The [discovery chapter](capability-discovery.md) defines the evidence needed for each feature and the permitted exchange states. Support, identity continuity and online presence are separate observations.

::: {.details summary="Automatic negotiation and notification rules"}

### Automatic exchange boundary

An ordinary outgoing message may advertise capabilities without requesting a machine reply. A standalone negotiation response requires a specified service exchange: a validated reply destination, a permitted state transition, duplicate suppression and a terminal state. It MUST NOT use reply-all or treat From, Reply-To, Sender or a delivery return address as interchangeable authenticated identities.

Direct automatic responses use `Auto-Submitted: auto-replied`; independent automatic initiation uses `auto-generated`. These fields do not hide messages. Unknown automatic traffic MUST NOT initiate a negotiation response. Any permitted response to an automatic negotiation message must be expressly defined by the service state machine, rather than a general exception for every message carrying a recognizable header. The [configured provider-control exchange](provider-control.md) defines signed HTTPS requests, responses and retry bounds. It does not select a standalone automatic-email negotiation protocol or authorize responses to an unfamiliar control marker.

DSNs and MDNs MUST NOT be repurposed as hidden key-exchange messages. Suppressing delivery notifications does not prove successful delivery, capability support or participant presence. See the [automatic responses audit](audits/automatic-responses.md).

### Notifications and presence

Sieve-generated `auto-notified` messages are notifications, not key-negotiation requests. Embedded copies of an event do not create a new authenticated event. The notification's configured destination, original author and envelope sender are distinct roles.

An account or device MUST NOT be shown as online solely because email was accepted, a notification was generated, or a trace timestamp is recent. A presence extension needs independent authorization, freshness and privacy rules; human availability cannot be inferred from device connectivity. The [Sieve notification audit](audits/sieve-notifications.md) records the existing certainty requirement and the applicable automatic-message exception.

:::

::: {.details summary="Using existing filters without promising invisible mail"}

### Filtering in older systems

Sieve already defines a silent `discard` action in RFC 5228 §4.4. This is an action taken by a configured filtering program, not a universal message header that a sender can require legacy clients to obey. A deployment might reuse provider filtering rather than invent a new deletion mechanism, but it still needs authorized rules and safe protocol processing before discard.

A deployment must review the behavior of every enabled Sieve extension, including tests with side effects. The base language's limited syntax does not prove that an extended script only classifies mail. Any extension that generates messages or protocol requests needs explicit loop suppression and authorization; receiving or previewing a negotiation candidate must not accidentally trigger a reply storm.

Receiving an application/sieve attachment does not authorize installing or executing it. Provision control-routing rules only through an authenticated, authorized configuration path, and protect those rules from modification and unauthorized retrieval. This can be part of account setup; it need not require a separate prompt for each message. No such provisioning interface is selected by this draft yet.

The filter and protocol validator must agree on the representation being classified. Malformed headers, encoded NULs or different decoding choices must not let one component hide a message while another interprets it as ordinary correspondence or a different control operation. Preserve enough original evidence to diagnose disagreement without exposing secrets in routine logs.

A header or address match is only a filtering hint. Substring matching can include display text, comparator rules can ignore ASCII case, and a failed match can reflect unsupported or invalid input. A filter MUST NOT treat such matches as verified sender identity, key possession or proof of compatible control-message support. Route candidate traffic to the authorized validator; do not install keys or discard ordinary mail solely because a claimed header resembles a control marker.

Even a configured rule needs implementation-specific checks:

| Filtering action | Limit relevant to negotiation |
| --- | --- |
| Stop processing | Does not cancel implicit keep by itself |
| File into a control mailbox | Optional capability; missing or invalid mailbox handling can deliver elsewhere or fail |
| Redirect to a control service | May be ignored by policy, leaving implicit keep; forwarding does not prove recipient identity |

The envelope test exposes the recipient relevant to this delivery, not the complete original audience. It cannot establish that every recipient supports the richer protocol. A Sieve message-size test also measures the email representation, not the decoded structured-event size; enforce the event limit separately after transfer decoding.

Discard cancels implicit keep; it does not undo another action or guarantee erasure of retained copies. Script errors can result in implicit keep, and implementations need not execute all actions atomically. Consequently, a Sieve deployment cannot promise universal inbox invisibility or transactional protocol processing merely because its rule includes discard. The control handler must durably accept and validate the exchange under its own contract before a filtering action can be treated as completed negotiation. Failure must not install keys or authorize a downgrade.


Unknown MIME dispositions fall back to attachment handling under RFC 2183 §2.8. Neither mechanism creates a reliable sender-controlled invisible first-contact probe.

Sources: [RFC 5228 §4.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-4.4), [RFC 2183 §2.8](https://www.rfc-editor.org/rfc/rfc2183.html#section-2.8).

An extension must authenticate, correlate, deduplicate and rate-limit exchanges before hiding or discarding their mail. Replies must not trigger equivalent replies indefinitely. Numeric limits and the complete exchange remain open.

:::

## When a recipient cannot decrypt

The sender can allow ordinary email, offer browser access or require a compatible encrypted endpoint. That choice can be remembered; this draft does not require another prompt for every message or select a universal default.

| Sender's policy | What the recipient receives |
| --- | --- |
| Allow ordinary email | A readable copy, explicitly outside endpoint encryption |
| Offer browser access | A link, with its access conditions identified |
| Require endpoint encryption | Delivery waits for a compatible, authenticated endpoint |

> [!ex] Carol joins the conversation
> Alice and Bob have been exchanging encrypted messages. Carol uses an older client. Sending Carol a readable copy changes who can access that contribution, even if Bob's copy remains encrypted. The client shows that change and follows Alice's policy. It does not silently expose the protected history in a quoted reply.

A secret link is an access credential: whoever obtains it may gain access. A decryption secret sent in ordinary email is exposed to whoever can read that email. Browser access can provide a useful fallback, but does not by itself establish confidentiality from the email provider. A browser acting as an endpoint needs its own authorization and a stated trust model for the delivered code. A separate password is prior art, not the proposed routine experience.

Missing capability advertisements do not establish that a known correspondent deliberately disabled protection. The [delivery policy chapter](delivery-policy.md) owns the rules for mixed recipients, browser grants, previews and replies.

## Adding and removing devices

An account can have several authorized devices. Mailbox login alone must not add another one to an established encrypted identity. Existing authorized devices or an explicitly configured recovery mechanism establish that continuity.

> [!ex] Bob replaces his laptop
> A new key arrives from Bob's address. Alice's client keeps the identity history it already knows and checks how the new device was authorized. It does not replace Bob's known key just because the address matches.

Removing a device stops future protected delivery once senders learn and apply the change. It cannot erase messages the device already received. Recovery must distinguish continuing an existing identity from starting a new one, and explain whether old history can be recovered and by whom.

The [identity lifecycle](identity-lifecycle.md) and [group rules](group-conversations.md) define those changes. Keeping a readable archive or recoverable backup is a separate decision from keeping old transport keys.

::: {.details summary="Address changes and identity continuity"}

### Alternate-address bindings

Automatic fallback must not transfer a pinned key or disclose content to an alternate mailbox solely because an unverified message associates the addresses. Require binding evidence appropriate to the selected security mode. A deliberate user selection can change the destination, but it does not by itself prove that the old and new mailboxes share a cryptographic identity.

Transport compatibility failures preserve the sender's selected fallback policy. Address transformation, legacy display conversion and confidentiality downgrade are separate operations. Derived display views preserve the original protected source for verification. See the [internationalization framework audit](audits/internationalization-framework.md).

:::

## Protecting the whole contribution

The protection indication must match the content actually protected. A signed paragraph does not authenticate an unsigned attachment beside it. A signed URL does not authenticate whatever that URL returns later.

Receivers retain the original protected bytes for verification and derive the conversation display from the verified result. Reflowing text, sanitizing HTML or changing a filename for display must not change the bytes used to check a signature.

> [!ex] A protected answer has an unprotected attachment
> Bob's signed answer verifies, but a file beside it is outside that signature's coverage. The client can show the answer's verified status without giving the file the same status. Placing both in one conversation bubble does not extend the signature.

### When the author cannot be verified

A missing signature and a failed signature provide no authenticated-author assurance. For otherwise comparable messages, the client MUST use the same ordinary protection display and action restrictions in both cases. An unencrypted message is unprotected; a successfully decrypted message remains encrypted but unverified. Neither state authorizes structured answers, edits, key changes or other authenticated conversation effects. Readable content remains subject to the rendering rules.

An established protection expectation applies equally to both cases. If local policy or authenticated conversation state requires a verified author, the client MUST indicate that this expectation was not met whether the signature is absent or fails. A message's own claim that it is protected MUST NOT establish that expectation. The client MUST NOT silently reset known identity bindings or weaken the reply's delivery policy. Decrypted content retains its confidentiality restrictions even when its author cannot be verified.

> [!ex] A protected conversation receives an unverifiable message
> Alice's client expects authenticated contributions from Bob. It shows “Author could not be verified” for both an unsigned message and one with a failed signature. Neither can change Bob's earlier answer. Removing a broken signature therefore does not make the message appear more trustworthy.

::: {.details summary="How this follows RFC 9787 signature-failure guidance"}

[RFC 9787 §6.4](https://www.rfc-editor.org/rfc/rfc9787.html#section-6.4) requires comparable unsigned and failed-signature messages to receive equivalent treatment. Email Next follows that rule. Its expectation warning depends on prior trusted state, not on the presence of a broken signature; this extends the expectation model discussed in [Appendix A.9](https://www.rfc-editor.org/rfc/rfc9787.html#appendix-A.9), rather than making failed signatures a separate danger category.

Verification details MAY distinguish a missing signature, unavailable certificate, identity-binding failure, unacceptable algorithm and cryptographic mismatch. These diagnostics MUST NOT become a more alarming ordinary message status solely because a signature exists. Independent evidence of a different threat can still warrant its own indication.

:::

::: {.details summary="MIME protection and OpenPGP compatibility rules"}

### Protection coverage follows the MIME entity

A security profile using RFC1847 containers MUST validate their exact part count, control-part position, protocol type and algorithm consistency before granting any protection indication. Unsupported protocols and failed decryption leave the protected object unavailable; failed output is not input to an interactive renderer.

Protection applies only to the entity covered by the selected protocol. The receiver MUST NOT extend a nested signature's identity or integrity indication to outer message headers, external references or unprotected sibling attachments. The protected contribution includes its readable alternatives, structured event and every bundled resource or attachment for which protection is claimed. A referenced resource needs its own inclusion or authenticated binding; a signed reference alone does not authenticate fetched bytes.

Compose and encode the inner MIME entity before applying the selected security profile. Do not reflow text, sanitize HTML, re-encode signed parts or normalize display labels and then use that result as the verification input. Exact canonicalization remains the security profile's responsibility. See the [security-container audit](audits/security-containers.md).

### OpenPGP MIME is packaging, not identity enrollment

An `application/pgp-keys` part supplies key material. Its presence MUST NOT replace a known identity binding or confer verification merely because the key contains a matching mailbox string. Any automatic import remains subject to the selected discovery, continuity and revocation profile.

An implementation selecting OpenPGP MIME must use its specified canonical MIME representation, including signed content headers and transfer-encoded data. It must distinguish the content's final CRLF from the CRLF that introduces the next multipart boundary. The [OpenPGP MIME audit](audits/openpgp-mime.md) records these rules and the unresolved current-algorithm dependency. This draft does not adopt the historical example hashes as acceptable generation algorithms.

The [gateway audit](audits/security-gateways.md) distinguishes protected carriage from intentional conversion. Email Next does not treat conversion as equivalent protected delivery.

:::

## What existing mail checks contribute

Domain signatures and provider authentication results help explain how mail was delivered. They are useful evidence about domains and delivery systems. They do not authorize a new endpoint key, a changed recipient list or an interaction on behalf of a person.

| Check | What the result concerns | What it cannot establish by itself |
| --- | --- | --- |
| DKIM domain signature | The signing domain and the message content its signature covers | A person's device identity or permission to change a conversation |
| ARC forwarding history | Signed statements by mail handlers about earlier authentication | That every statement is true or the current message is unchanged |
| DMARC alignment | Use of the Author Domain through an aligned authenticated domain | The mailbox local part, encryption key or safety of the content |
| Authentication-Results | Checks reported by a producer through an established trusted boundary | Trust merely because the field appears in a downloaded message |

> [!ex] A mailing list changes a subject
> The list reports that Alice's incoming message passed domain checks before it added a subject prefix. That history can help explain the delivered email. It does not make the changed message pass Alice's original signature, or let the list replace her encryption keys.

Reports and notifications are separate disclosures. They must not leak decrypted messages, form answers, private recipient lists or access secrets. Notification delivery also must not be treated as proof that a person is online or has read a message.

The disclosures below define the inherited checks and their limits. They remain separate from the endpoint checks that authorize Email Next contributions.

::: {.details summary="DKIM: algorithms, parsing and exact signature coverage"}

### Domain signatures and algorithm policy

DKIM evidence records the signing domain, verified coverage and algorithm-policy result. A domain signature is not a correspondent's device credential. It does not authorize replacing an established encryption key or changing group membership.

Apply the [algorithm requirements update](audits/dkim-algorithms.md) and [Ed25519 update](audits/dkim-ed25519.md) when evaluating DKIM. RSA-SHA1 and undersized RSA signatures cannot count as valid under the updated rules. A valid signature must still cover the fields required by the operation relying on it. Ed25519-SHA256 uses Ed25519 over the DKIM SHA-256 digest; a different prehash variant or direct signature of canonicalized headers is not interchangeable.

These domain-signature algorithms do not select the Email Next end-to-end encryption suite.

### Domain-signature history and parsing

Keep domain-signature verification evidence separate from endpoint identity history. A DKIM selector identifies a signing-domain key lookup, not a user device. Changing or removing that lookup does not authorize a correspondent key transition. A later inability to verify an archived message must not silently erase an earlier recorded verification result or be presented as proof that the original message was forged.

When interpreting a DKIM tag list, preserve its specified case and whitespace semantics. Duplicate tag names invalidate the entire list; do not choose the first or last value. An empty value differs from an omitted tag and its default. Ignore an unknown tag under DKIM's extension rules, but do not treat it as a recognized Email Next capability or authorization. This is not a substitute for completing the signature's required-field, algorithm, coverage and cryptographic checks.

Apply RFC6376 together with its algorithm updates; its historical SHA-1 requirements do not override those updates.

### Partial domain-signature coverage

A valid domain signature does not authorize every visible element of a message. When DKIM supplies a body-length limit, coverage is measured over canonicalized body octets. Content after that limit must not inherit the signature's integrity indication. In particular, an appended question, form control, capability advertisement or instruction cannot become authenticated application input through a valid signature over an earlier prefix.

Header coverage likewise depends on the selected field instances, not merely the presence of a header name somewhere in the signature. The client must preserve the verifier's coverage evidence before attributing any meaning to it. An AUID that resembles an email address is not necessarily a mailbox, a reply destination or an endpoint identity. A signature timestamp or expiration is not a conversation sequence number or an anti-replay mechanism.

Canonicalization is verification input preparation. It must not replace the stored original or the rendering source. Simple and relaxed canonicalization have different whitespace and empty-body behavior; a display sanitizer, Unicode normalizer or generic whitespace reducer is not a substitute. Unknown signature tags remain part of the signed header input even when their semantics are ignored.

These boundaries supplement the endpoint security profile, which still must bind the full structured contribution, readable representations and authorized resources. DKIM alone does not supply that profile.

### Signed input and diagnostic copies

DKIM's copied-header `z=` material is diagnostic. It must not replace the actual message headers selected by `h=`, repair a failed signature or supply a trusted reply destination. Signature verification uses transfer-encoded message bytes before MIME decoding and after removal of transport framing such as SMTP dot stuffing. The client must keep that input separate from decoded content used for display.

The header-hash input includes the selected canonicalized headers followed by the signature header with its own `b=` value and surrounding whitespace removed, without that signature header's trailing CRLF. The body hash is already represented by `bh=`; it is not appended again as a separate header-hash input. This follows verified RFC6376 erratum5252. Unknown signature tags remain included in that input.

DNS TXT character strings within one key record are concatenated without inserted whitespace. Separate records must not be concatenated into a fabricated key. A key record's version and tag meanings differ from those in a signature header. Key revocation and service restrictions must be evaluated before a cryptographic success can become an accepted domain-signature result. None of these checks establishes endpoint identity continuity.

### Multiple signers and repeated headers

Record each domain signature's signer, coverage and verification outcome independently. A valid mailing-list or forwarding-service signature does not repair an invalid author-domain signature or prove that it was valid earlier. Signature order is not an authenticated history of which organization handled the message first. Continued delivery under a provider's filtering policy does not grant endpoint identity or interaction authority.

For DKIM coverage, repeated header names select instances from the physical bottom of the header block upward. A name appearing once in `h=` therefore does not cover every instance of that field. An extra occurrence in `h=` can protect against insertion of another field, but it does not make otherwise malformed duplicate singleton headers suitable for application processing. Preserve that ambiguity rather than choosing a convenient visible value and labeling it authenticated.

A contribution's author, audience, reply target and interaction references must satisfy the selected endpoint profile even when a domain signature verifies. Domain-level acceptance and authenticated application behavior remain separate decisions.

### Internationalized names and signed bytes

Keep original authenticated bytes separate from parsed addresses and DNS lookup representations. Convert internationalized domain labels for lookup under the applicable IDNA and authentication rules, but do not replace those labels inside signed input before verification. Apply only the selected protocol's canonicalization.

Mailbox local parts are not DNS names: do not apply IDNA conversion to them. Visually similar Unicode strings do not establish identity equivalence. The [internationalized authentication audit](audits/internationalized-authentication.md) records the SPF/DKIM distinctions and outstanding discovery-normalization dependencies.

:::

::: {.details summary="DKIM: verification results, replay and lookup privacy"}

### Verification outcomes and supplied result headers

Keep a temporary key-lookup failure distinct from a malformed signature, a missing key and a cryptographic mismatch. A temporary failure may justify another verification attempt; it does not authorize plaintext fallback or reset a previously established endpoint identity. A signature failure must not be converted into an SMTP temporary failure merely to retry unchanged cryptographic input. Delivery policy and endpoint-protection policy remain separate.

A successful header-signature calculation alone is insufficient: the covered body hash must also match. Parallel verification may change execution order, but must preserve the complete result. Report the actual signing domain and coverage rather than assigning its success to the displayed author automatically.

An incoming `Authentication-Results` field is message content until the receiving system establishes that it came from its trusted verification boundary. Its position, field name or asserted success cannot establish that trust. Do not use a sender-supplied result to authenticate controls, select correspondent keys or display a verified-author indication. The [Authentication-Results audit](audits/authentication-results.md) records the boundary rules and unresolved source issues.

### Replay, delegated signers and lookup privacy

A domain signature may remain valid when the same message is delivered again or to another envelope recipient. Do not use signature validity as evidence of a new contribution, fresh capability advertisement or authorized audience change. Deduplicate using the endpoint profile's authenticated contribution identity and evaluate audience authorization separately. A replay must not repeat a form submission or other external effect.

A selector assigned to a device or service does not itself restrict that signer to a particular mailbox local part. The deprecated DKIM key-record `g=` tag supplies no such restriction under RFC6376. Domain delegation must not be presented as independently verified personal identity or used to authorize endpoint-key replacement.

Key lookup can reveal that verification occurred: a sender can use a distinct selector and observe the resulting DNS query. This is not proof that a person opened or read the message. Capability discovery must document comparable lookup disclosures and must not turn them into presence or read receipts.

:::

::: {.details summary="ARC: what forwarding history can establish"}

### Authentication history through forwarding

ARC carries signed assertions about authentication checks made by mail handlers. It can help a receiver interpret mail that passed through a forwarding service or mailing list. A valid chain establishes the integrity of those assertions; it does not establish that each assertion is accurate or that the receiver trusts the handler making it.

For example, a mailing list can report that Alice's incoming message passed its domain-authentication checks before the list changed the subject. That report does not authorize the list to change Alice's protected contribution, enroll a device for her or add recipients to her encrypted conversation.

An Email Next client MUST keep ARC chain validation, trust in the reporting handler, interpretation of its authentication results and endpoint-event authentication as separate decisions. ARC validity MUST NOT repair a failed endpoint signature or supply missing authority for a key transition, audience change or interaction. An absent or invalid chain likewise does not establish that a correspondent lacks Email Next support.

A passing ARC result does not mean every earlier message signature validates against the current message. ARC requires validation of the latest message signature and every seal; checking earlier message signatures is optional and can identify where content changed. The interface MUST NOT present chain validity as proof that the message remained unchanged from its original author.

An ARC failure removes the chain's authentication benefit. It MUST NOT, by itself, invalidate an independently authenticated Email Next event or authorize an encryption downgrade. Keep ARC's failure classification separate from transport retry decisions and endpoint verification results.

A valid ARC chain is not evidence of freshness or unique delivery. The same intact chain can accompany a replayed message. Event deduplication, replay checks and interaction authorization MUST therefore operate independently of ARC results; another delivery of the same chain cannot make an action eligible to run again.

ARC history can expose relay domains and network addresses. Email Next providers MUST NOT add decrypted content, private audience membership, device credentials or access secrets to ARC assessment fields or diagnostic reports. The ability to carry an authenticated assertion does not authorize disclosing its contents to later handlers. HTML sanitization and resource-loading restrictions apply equally to messages with passing ARC results.

These boundaries follow ARC's distinction between verifiable testimony and independently reproducible authentication evidence in [RFC8617 §§2–3](https://www.rfc-editor.org/rfc/rfc8617.html#section-2).

:::

::: {.details summary="Authentication-Results: trusting the producer and delivery boundary"}

### Authentication-result interpretation

Trust in an authentication-result producer must include the path by which its assertion reaches the consumer. A familiar `authserv-id` string alone is insufficient. In particular, results inside a forwarded `message/rfc822` attachment or digest do not inherit the receiving account's trusted status merely because they name its provider. Keep those assertions scoped to the encapsulated message and untrusted unless independently established.

Preserve the method, supported version, result and evaluated property together. `header.d` in a DKIM result identifies a signature tag; an SPF `smtp.mailfrom` or `smtp.helo` result concerns transport identity, not automatically the visible author. Unknown property types must not drive handling decisions, and unsupported method versions must not be interpreted using a familiar result word such as `pass`.

A reported local-policy decision is distinct from the underlying authentication calculation. Do not turn `policy` into a claim of cryptographic failure or success. Likewise, an overall `none` assertion reports that authentication was not performed; it is not proof that the message lacks all signatures or that encryption is unavailable. These distinctions follow the completed [RFC8601 base review](audits/authentication-results.md); provider integration and parser conformance remain to be tested.

### Provider configuration and boundary processing

A client must not enable trust in `Authentication-Results` merely by finding the field in downloaded mail. Its account configuration must identify the trusted producer and the provider's boundary-processing arrangement. A provider adopting this mechanism must remove or obscure incoming assertions that claim its own authentication-service identity but arrive from an untrusted source. Unsupported field versions arriving over an untrusted SMTP connection must be removed under RFC8601. Internationalized identity comparisons follow that specification's A-label-to-U-label rule; this comparison must not rewrite bytes used to verify a signature.

Each producer adds its own result field; it must not append results to an existing field. Preserve trace-field order. Removing a forged or unsupported field can invalidate a signature that covered it; preserving that signature is not a reason to trust the forged assertion. Keep local provenance and original evidence separate from any normalized conversation display.

Result properties are method-specific. For `auth`, `smtp.mailfrom` reports the MAIL command's AUTH parameter, which can differ from its envelope reverse-path; `smtp.auth` reports the authorization identity from session authentication. For `spf`, `smtp.mailfrom` has the SPF-defined meaning. Never merge these into a generic verified-sender identity. Reverse-DNS `iprev` success likewise establishes neither a person nor an endpoint key.

Experimental authentication methods and results require explicit agreement among participating administrative domains. They are not a transparent public capability-negotiation channel for legacy mail. Unsupported methods or unregistered result/property types must not authorize application behavior. Provider deployment and user-interface testing remain necessary before displaying these assertions as trust signals.

### Historical attestations and imported messages

When a trusted intermediary reports that an earlier version passed authentication, preserve the distinction between that historical assertion and verification of the current bytes. A mailing-list signature covering its own result can protect the assertion that it checked the original message. It does not make the modified message pass the original author's signature or authorize changes to an endpoint-protected contribution.

Authentication evidence must remain tied to its message representation, producer, delivery context and evaluation time when known. Importing an attached message or extracting a digest must not promote embedded result fields into the receiving account's trusted delivery metadata. Preserve the original for inspection while excluding those fields from trusted application input unless provenance is independently established.

A provider's result can help describe delivery and domain authentication; it is not a general assurance that content is safe. Signed spam, look-alike domains and compromised authorized systems can pass checks. The interface must identify what was checked rather than use a universal “trusted message” badge. A message's `Priority` field is not an authentication or encryption signal, including when a legacy system used it to summarize results.

:::

::: {.details summary="DMARC: domain alignment and delivery decisions"}

### Domain alignment and correspondent identity

A DMARC pass validates use of the Author Domain through an aligned authenticated domain. It does not validate the mailbox local part, display name, encryption key or safety of the content. The interface must not turn domain alignment into a verified-person badge or use it alone to accept a key replacement.

For the SPF path, DMARC uses the MAIL FROM identity as defined by SPF, including SPF's null-reverse-path handling; an independent HELO pass is not a substitute. For the DKIM path, a valid aligned signature can suffice even when other signatures do not align. Preserve which method and domain supported the result.

Relaxed alignment is not a general rule that two addresses or endpoints are equivalent. The organizational-domain algorithm belongs to the applicable DMARC version and must not be reused as a rule for merging contacts, sharing cached keys or authorizing group membership. A malformed or repeated From field must not be repaired by selecting whichever value would make alignment pass.

DMARC policy discovery and organizational-domain determination are separate operations. A policy found directly for the Author Domain does not automatically make that domain the organizational boundary. The RFC9989 DNS tree walk, including its limits and explicit boundary flags, must be evaluated under that version's rules; a generic suffix comparison is insufficient.

A DMARC test-mode request changes requested handling of validation failures. It does not make failed validation pass, establish encryption support or authorize fallback. Likewise, aggregate and failure-report destinations are reporting configuration, not correspondent key-service addresses or conversation participants. Do not inherit reporting destinations from a public suffix where the applicable organizational policy declines to supply them.

Source interpretation questions are documented in the [DMARC audit](audits/dmarc.md).

### Validation outcomes and delivery decisions

Preserve the distinction between DMARC validation and the receiver's disposition. A required DNS lookup that fails does not establish either a DMARC pass or fail under RFC9989; accepting or deferring mail under local policy must not relabel that uncertainty as authenticated identity. Retain the underlying SPF and per-signature DKIM evidence rather than collapsing all errors into a binary author verdict.

Forwarding and mailing-list transformations can prevent domain alignment while an authorized communication remains legitimate. Conversely, acceptance of such mail under a local exception does not validate its endpoint-protected contribution. Display delivery and domain-check information separately from endpoint decryption, signature and identity-continuity results.

DMARC aggregate reports are not a complete delivery history: a message rejected by an SPF check before its content is transferred may never reveal an Author Domain for DMARC evaluation. Absence from a report therefore cannot prove that a message was not attempted or that a correspondent lacks the richer protocol.

:::

::: {.details summary="Reports: confidentiality, historical meanings and parser checks"}

### Reporting must preserve confidentiality

An authentication or delivery report is a separate disclosure to its report recipients. A reporting address published by a domain does not authorize disclosure of decrypted conversation content, form answers, private recipient lists, encryption secrets or hosted-access tokens. Implementations MUST NOT place those values in automatically generated authentication reports. This requirement also applies to diagnostic excerpts and attached originals assembled after decryption.

Aggregate data can reveal communication patterns even when it contains no message body. Providers must treat report destinations, access controls and retention as a separate privacy boundary. Encryption of the original conversation does not establish confidentiality of its reports. External report destinations require the applicable reporting protocol's authorization checks; they are not an extension of the conversation audience.

Report ingestion must treat reported identities and outcomes as assertions from the report producer. Malformed reports, fabricated results and excessive traffic must not mutate correspondent identity, replace keys or trigger repeated conversation actions. A reporting service is not a capability-discovery service.

These are proposed Email Next confidentiality requirements informed by RFC9989 Sections 10 and 11. They do not claim that DMARC itself prohibits every such disclosure. The [aggregate-report audit](audits/dmarc-aggregate.md) and [failure-report audit](audits/dmarc-failure.md) record their complete base-text reviews. ARF dependencies, redaction behavior and implementation verification remain open.

### Historical report interpretation

A report importer MUST retain the applicable reporting specification with its parsed result. The same field name can have incompatible historical meanings: [RFC7489 Section 7.3.1](https://www.rfc-editor.org/rfc/rfc7489.html#section-7.3.1) uses `Identity-Alignment` for methods that produced an aligned identity, whereas [RFC9991 Section 4](https://www.rfc-editor.org/rfc/rfc9991.html#section-4) uses it for methods that failed to authenticate an aligned identity. Their meanings of `none` differ accordingly.

An importer MUST NOT infer which meaning applies from the field's spelling or a message's asserted date. Without established producer/profile provenance, retain the original field and mark its interpretation unresolved. Do not invert historical results into current results silently. A generic ARF version value does not by itself identify the DMARC reporting revision. Even a correctly interpreted report remains producer-supplied domain evidence, not authority for a conversation action or key change.

### Structured report validation

Schema validity is not sufficient to trust a report. A report processor must also check the applicable protocol's value constraints, identifier scope, provenance and consistency before using its data. The RFC9990 schema, for example, permits values that fail its surrounding prose requirements: its version element is an unrestricted decimal and its source IP is a string. Counts and periods also need semantic checks before aggregation.

Parsing must not load external entities, schemas or extension definitions from sender-supplied locations. A namespace URI identifies a vocabulary; it does not authorize a network request. Decompression and parsing must have bounded resource use before report content reaches aggregation or storage. Unknown extensions must not acquire authority over encryption, identity or conversation state.

The audit's schema experiment establishes only that the published sample and three deliberately invalid semantic variants pass the published XSD. It does not establish a complete report parser or safe production resource limits.

:::

## Retries, drafts and history

A retry delivers the same contribution again; it must not submit the same answer twice.

> [!ex] The connection drops after Send
> Bob retries his answer after a delivery failure. The client retains the prepared protected object rather than rolling encryption state backward to create it again. Alice's client recognizes the authenticated event and does not apply the answer a second time.

A saved draft remains private to the author's authorized devices until sending, even after recipients have been entered. A readable archive and a transport retry queue have different jobs. Keeping history readable does not justify keeping old transport secrets indefinitely, and selecting ordinary delivery for the final message does not expose earlier draft revisions.

> [!norm] Preserve the boundary
> The client must coordinate encryption state with its outgoing record, authenticate before applying an action, and deduplicate before repeating effects. Restoring an older backup must not silently restore revoked authority or reuse consumed encryption state.

::: {.details summary="Sending and retrying without repeating an action"}

### Authenticated metadata and durable send state

Authenticated metadata is not necessarily confidential. An MLS PrivateMessage exposes its group identifier, epoch, content type and authenticated_data field outside its encrypted content. An Email Next binding MUST NOT place private recipient lists, form answers, access tokens or sensitive subject text in that field. Routing metadata and protocol identifiers must have an explicit disclosure model even when their integrity is protected.

Successful decryption alone must not authorize an interaction. Required sender signatures, group-context checks, membership checks and commit confirmation must succeed before the corresponding content changes application state. The applicable wire format and sender role determine those checks; a public handshake is not an encrypted application message.

A sender must durably coordinate cryptographic generation state with its outgoing message record. Retrying transport delivery should retransmit the already constructed protected object. It must not roll back ratchet state or regenerate a different object using a previously consumed key generation. A random reuse guard supplements persistent state; it does not make restoring an old device snapshot safe. Recovery from uncertain or rolled-back state requires the selected security profile's recovery procedure before further encryption.

The [durable sender](evidence/README.md#durable-sender-release) coordinates the selected MLS checkpoint with the exact queued message and reuses that object on retry. Its local transaction and failure checks cover this sending boundary. Restoration of a historical device snapshot needs separate reconciliation; successful queue recovery does not make a rolled-back snapshot safe. These constraints follow RFC9420 Section 6.

### Insider replay and application effects

An authenticated event identifier MUST be covered by the event's authenticated payload or authenticated additional data. Receivers MUST apply event deduplication after authentication and before any conversation-state mutation, form submission, notification-triggered action or external effect. A new MLS generation or a different ciphertext MUST NOT make a previously processed event fresh. Identical authenticated events remain retries; conflicting authenticated contents under the same event identity follow the collision-quarantine rules in the message contract.

This requirement covers the insider replay described in RFC9750 Section 8.6: a group member can re-encrypt another member's signed content under a fresh generation because the signature does not cover that generation. Transport duplicate detection and the MLS ratchet do not replace application event identity. An action whose prior execution status is no longer available MUST NOT be automatically executed as new merely because its deduplication record expired. The receiver must preserve an execution tombstone or require an explicitly new authorized action under the interaction contract.

A notification provider must not receive decrypted message content or form answers as an incidental consequence of push delivery. Encrypted push payloads still expose timing and device associations; the interface must not describe them as anonymous delivery. These limits follow the [MLS architecture audit](audits/mls-architecture.md).

:::

::: {.details summary="Draft privacy and retained conversation history"}

### Drafts are private working state

Remote draft synchronization MUST encrypt the draft for the author's authorized devices before upload. Intended recipients MUST NOT receive draft decryption access merely because their addresses have been entered in the composer. This applies while the final delivery policy is undecided and while a draft contains quoted protected material. Selecting ordinary delivery for the eventual message does not retroactively authorize exposing earlier draft revisions.

A draft MUST NOT carry a normal outbound contribution signature that could be replayed as the author's sent message or form submission. If authenticated device synchronization is used, its keys or signed context must distinguish draft synchronization from sending; the exact synchronization profile remains separately specified. Sending creates the immutable contribution and recipient-specific delivery objects only after the sender invokes Send under the selected delivery policy.

A recoverable sent archive and a retry queue have different purposes. A sender-only archival ciphertext MUST NOT be substituted for the actual queued recipient ciphertext during retry. A decrypted archival copy MUST NOT be submitted as a retry without reconstructing and validating the authorized protection plan. MLS transport-secret deletion requirements remain in force even when the client preserves readable history using separate archive encryption.

These boundaries incorporate [RFC9787 Sections 9.1 and 9.5](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.5). They specify required behavior; a multi-device draft synchronization implementation is not yet validated.

### Delayed delivery and retained history

Retaining a readable conversation archive is a separate storage decision from retaining transport decryption secrets. An MLS client must delete consumed secrets as required by the protocol, including ancestor secrets from which consumed message keys can be recovered. It may retain permitted unconsumed keys for delayed messages only under the profile's explicit retention policy. Keeping an epoch's root secret indefinitely to make mailbox replay convenient defeats that deletion requirement.

If the product retains decrypted history, it must protect that archive separately and describe its exposure honestly. Forward secrecy of transport keys does not protect plaintext history on a compromised device or in an accessible backup. A history transfer to a new device or participant is a new authorized disclosure, not restoration of a deleted MLS key by implication.

The profile must distinguish a message that cannot be decrypted because its permitted retention window ended from a message that failed authentication. Neither condition authorizes plaintext retransmission. Recovery and resend flows must preserve the sender's selected delivery policy and the current authorized audience. The [bounded-retention experiment](evidence/README.md#bounded-secret-retention-and-delayed-application-delivery) implements an explicit local policy for permitted delayed processing and secret retirement. The [managed restore path](identity-lifecycle.md#import-history-then-reconnect) imports history without activating old keys, then requires fresh enrollment or an explicit new identity. Protected archive transfer and encrypted backup recovery remain separate contracts. These requirements are informed by RFC9420 Section 9.

This is a transport-secret lifecycle choice, not a rule that credential expiry makes readable history disappear. [RFC9787 §9.2](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.2) distinguishes expiry for new encryption from access to existing messages. Email Next preserves that distinction: a readable retained archive remains history, while new conversation effects require current authority. MLS's deletion rules can make previously unprocessed ciphertext unreadable after its retention window; a separate protected archive is how a client preserves already received history without indefinitely retaining those transport secrets.

:::

::: {.details summary="Group verification, exported secrets and compromise recovery"}

### Scope of group verification and exported secrets

A comparison of MLS epoch authenticators verifies agreement for that group epoch through the comparison procedure used. It MUST NOT create a permanent verified-person badge or imply that later membership changes have been independently verified. The interface must distinguish verified account-key continuity from a checked snapshot of group state. The profile must specify what happens to that indication when the epoch changes.

Any exported secret used for attachments or another Email Next function must have a distinct purpose label and context, with its source group and epoch recorded. It must not be reused as an unrelated authentication token or treated as valid for a changed audience merely because the conversation identifier is unchanged. Retention of resumption secrets and refresh of exported values require explicit limits and transition rules in the security profile.

Adding an external pre-shared key does not, by itself, establish stronger forward secrecy or post-compromise security. Its generation, distribution, storage and lifetime are part of the security claim. These boundaries follow RFC9420 Sections 8.4–8.7. Exported-secret applications, external pre-shared keys and human epoch-authenticator comparisons need separately selected bindings before interoperable support can be claimed.

### Limits of compromise recovery

A proposed key update does not establish recovery from compromise. Recovery depends on the relevant members processing an accepted transition that replaces compromised material. A delivery service can delay or suppress those transitions; an interface must not claim that confidentiality has been restored merely because an update was queued or submitted.

Compromise of an identity authority is a different threat from compromise of a relay. An authority able to bind arbitrary keys to an account can impersonate that account or introduce a fraudulent device unless the application requires additional continuity evidence. Device cross-signing and transparency mechanisms must be evaluated against that threat; their presence alone is not proof that every unauthorized binding will be prevented or detected.

An accepted MLS commit is also not proof that every member can process it. A malicious member can construct an update that fails only for particular subtrees, including members currently offline. The group profile must define failure reporting and authorized recovery for this case. Requiring acknowledgments can improve detection but trades away availability when the needed members are offline; an arbitrary majority is not equivalent to the subtree coverage described in RFC9420 Section 16.12. The selected profiles do not guarantee that every member can process an accepted Commit. Failed local processing holds application effects; it does not authorize a competing branch. The [group lifecycle](group-conversations.md) defines selected recovery paths and their limits. A subtree-acknowledgment protocol is not selected.

:::

::: {.details summary="Delegating cryptography to another component"}

### Provider assistance and encryption proxies

An upgraded provider may distribute public key material, queue encrypted delivery objects and report transport outcomes. Possession of those capabilities MUST NOT be represented as possession of the user's endpoint identity or as permission to decrypt content. A provider-operated service that holds usable message decryption keys is within the confidentiality boundary and MUST be identified as such.

A client delegating cryptographic operations MUST convey the authorized recipient set, delivery policy, inherited confidentiality requirements and operation context through an authenticated interface. Ordinary SMTP submission alone does not express this contract. A proxy MUST NOT infer permission to disclose protected quoted content from the absence of an encryption header or from a transport retry.

A client accepting verification results from another component MUST authenticate that component and bind each result to the exact message bytes and evaluated protection layers. Message-supplied headers MUST NOT impersonate verification results. The result must distinguish signature validity, identity binding, encryption scope and processing failures; a single undifferentiated secure flag is insufficient. The interface and result schema remain work required before proxy interoperability can be claimed.

These requirements follow the limitations identified in [RFC9787 Section 9.7](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.7). Its Appendix A explicitly leaves a complete proxy integration protocol for future work.

:::

## Design basis and remaining work

The proposal draws on automatic exchange in Autocrypt, asynchronous setup in Signal protocols, and managed groups in MLS. These inform separate design choices; they are not algorithms to concatenate into a new cryptographic construction.

::: {.details summary="Protocol prior art and the selected experimental baseline"}

### Establish sessions through several paths

### Existing email

Autocrypt demonstrates automatic public-key exchange using headers and group key information carried inside encrypted mail. Its Level 1 threat model addresses passive collection rather than active key substitution.[^1] Reuse must respect the actual protocol; this draft does not redefine Autocrypt headers as a generic key container.

Advertisement is evidence of capability, not proof of identity. Clients should retain key history and distinguish an initial observation, continuity with a known key, and verification through another trusted mechanism.

### Offline recipients

A compatible service may publish public prekeys whose private counterparts remain on the recipient’s devices. A sender can establish an encrypted session before the recipient comes online. X3DH and PQXDH provide prior art for asynchronous establishment; their identity authentication and prekey lifecycle requirements still apply.[^2]

### Both participants online

Clients may perform a fresh authenticated exchange through a relay or direct connection. Being simultaneously online does not authenticate either participant. The exchange must bind the identities, chosen capabilities, and cryptographic protocol to the resulting session.

Live exchange is an optimization and an opportunity to refresh state. Delivery must not acquire a permanent requirement that both users be online. Presence discovery should not create a public directory of who is currently active.

### Ongoing and group conversations

Ratchet protocols evolve keys as communication proceeds. Forward secrecy limits exposure of earlier traffic after later key compromise; post-compromise security can protect later traffic after fresh uncompromised contributions under the protocol’s assumptions. Neither repairs an endpoint that remains controlled by an attacker.[^3]

The [experimental managed-conversation profile](security-profile.md) selects MLS 1.0 for both two-person and larger managed conversations. Its architecture separates authentication and delivery services from endpoints.[^4] The [transport](transport.md), [ordering exchange](ordering-exchange.md) and [group lifecycle](group-conversations.md) define the selected handling of delays, duplicates, missing messages, concurrent changes and recovery. Their local experiments do not establish complete distributed liveness.

The [group conversation contract](group-conversations.md) defines proposed administrator authority, membership transitions, history sharing and delayed-message boundaries. The versioned [application bindings](security-profile.md) select supported operations and transitions. Unsupported administrator changes, migration and other extensions retain explicit hold or terminal outcomes; the general application semantics do not imply wire support for every operation.

> [!warn] Experimental profile; independent review required
> MLS 1.0 with cipher suite 0x0001 is selected for the experimental managed-conversation baseline. Autocrypt, PQXDH and Double Ratchet are not concatenated into that suite. This draft defines no new cryptographic construction and makes no forward-secrecy or post-quantum conformance claim. The selected bindings define authentication, replay and transition rules with local test cases; these do not establish independent interoperability or security assurance.

The [discovery decision contract](capability-discovery.md) defines per-feature evidence states, passive bootstrap, authorized control exchanges and interrupted-session behavior. It separates endpoint capability from provider support and requires positive usability tests as well as rejection tests.

:::

The next implementation work is defined in the [security profile](security-profile.md), [discovery contract](capability-discovery.md) and [interoperability chapter](interoperability.md). The audits preserve the inherited requirements and unresolved source issues. A completed audit or passing local experiment is not a claim that the full protocol is ready to deploy.

## References

[^1]: [Autocrypt Level 1](https://docs.autocrypt.org/level1.html) and [SecureJoin](https://securejoin.delta.chat/en/latest/summary.html).
[^2]: Signal, [X3DH](https://signal.org/docs/specifications/x3dh/) and [PQXDH](https://signal.org/docs/specifications/pqxdh/).
[^3]: Signal, [Double Ratchet](https://signal.org/docs/specifications/doubleratchet/).
[^4]: [RFC 9420 — MLS](https://www.rfc-editor.org/rfc/rfc9420.html) and [RFC 9750 — MLS architecture](https://www.rfc-editor.org/rfc/rfc9750.html).
[^5]: [Proton password-protected emails](https://proton.me/support/password-protected-emails), consulted 19 October 2026.
[^6]: [RFC 3834 — Automatic email responses](https://www.rfc-editor.org/rfc/rfc3834.html).
[^7]: [RFC 9788 — Header protection](https://www.rfc-editor.org/rfc/rfc9788.html).
