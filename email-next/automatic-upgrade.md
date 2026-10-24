---
title: Upgrading an ordinary conversation
order: 7.18
blurb: real message first when permitted · automatic setup · future encryption
sectionNav: true
---

# Upgrading an ordinary conversation

A real email can also invite a secure conversation. If the sender permits ordinary delivery, the message carries a small setup invitation. A compatible recipient app can answer automatically, even when it processes the email days later. The sending app returns one final setup confirmation. Future messages can then use encryption as each direction becomes ready.

Use already usable setup to **encrypt the first message whenever possible**. This path is for ordinary messages the sender has actually authorized. Unknown support, a failed lookup or a timeout does not permit plaintext or weaken an established protected conversation.

> [!ex] Alice writes; the apps arrange what comes next
> Alice sends Bob a normal message with a setup invitation attached. Bob’s app processes it when he next connects and returns fresh receiving setup. Alice’s app returns its own fresh setup in one final confirmation. Neither person writes a handshake reply, and they do not need to be online together.
>
> Alice’s original message remains ordinary email. The apps show when future messages can be protected, without resending the original or marking it encrypted after the fact.

The three steps use existing SMTP submission and mailbox retrieval. Setup records are attachments inside those emails; no new mail server, special hardware or public directory is required. Older clients may display the attachment or setup response normally. This protocol does not depend on those clients hiding or discarding messages.

> [!note] Independent discussion draft
> The invitation, offer and confirmation bindings below are proposed protocol definitions. Complete cryptographic, transport, restart and real-provider acceptance remain required. They do not widen the existing passive-discovery or content-free setup parsers, and their names are not registered allocations.

## One invitation, two automatic responses

1. **Invitation.** A policy-authorized ordinary message carries a targeted invitation and a separate key dedicated to receiving setup offers. No valid conversation ciphertext uses that key.
2. **Receiving offer.** A compatible recipient app validates the invitation and actual delivery evidence, then sends its current receiving setup encrypted to the invitation key. It includes a separate key authorizing one final confirmation.
3. **Terminal confirmation.** The inviter returns its own current receiving setup encrypted to that confirmation key. This final message never produces an automatic answer.

Automatic completion follows the client’s setup policy and existing account authorization. This chapter imposes no separate manual toggle, per-message consent prompt or fixed key lifetime. Each signed promise must fit the actual credential, protected key custody and receiving capability. Published setup can enable offline encryption; it does not prove that someone is online or has read a message.

## What people see

Show the actual protection for each sent contribution and each selected recipient. Setup pending, missing evidence, expired keys, failed transport and uncertain submission remain distinct. A successful setup fetch is not a sent or read receipt. One ready person does not make a whole group ready.

After accepting the relevant setup and admission, show a concise protection-change boundary and accurate composer status. Keep the original readable message as ordinary history. Begin a fresh protected root; a local link to the earlier email is unverified context, not an authenticated reply relationship or permission to copy old history.

A ready direction can progress while another waits under the [delivery plan](delivery-policy.md). A failed setup cannot silently downgrade existing protection, add a recipient, turn Cc into a discussion subscription, reveal a blind copy or bypass the [declared reply policy](reply-intent.md).

## Mail account support still matters

Automatic responses require trustworthy direct-delivery and source-authentication evidence. A valid DKIM signature does not authenticate the SMTP envelope, prove mailbox-local-part ownership or independently identify a human. Arbitrary Return-Path or Authentication-Results headers downloaded over an authenticated mailbox connection are not enough.

Some legacy account interfaces do not expose the required evidence. The person can still read the ordinary email, but automatic setup remains unavailable on that input. This chapter does not claim broad provider interoperability from a MIME or cryptographic experiment. [The source and target gates](#4-source-and-target-gates-before-automatic-answering) define the exact supported-input boundary.

## Relation to the other setup paths

[Passive discovery](passive-discovery.md) remains observation only. [Content-free ordinary-mail setup](mailbox-setup.md) retains its own exact request, response and600-second active-attempt limit. [First-message encryption](first-contact-setup.md) remains preferable when eligible receiving evidence is available. A durable invitation here is a new scoped publication permission, not an extension or relabeling of that active request.

This optional acquisition binding adds no field or tuple to assertion10 and does not change `mail-conversation-v2`. Its exact invitation structure selects this response permission; a generic capability advertisement cannot. A client that supports current conversation rendering or encryption cannot be assumed to support these automatic invitation records. Unknown or unsupported attachment formats remain inactive without changing access to readable mail.

## Precise protocol contract

The following disclosures define the signed records, key roles, exact mail placement and durable lifecycle. The fixed byte/depth limits are wire-engineering selections. Deployment work budgets remain finite and configurable; these limits are not storage quotas or a prescribed user-policy default.

::: {.details summary="2. Roles, identity and time"}

### 2. Roles, identity and time

**Inviter** is the device sending the real ordinary message. **Responder** is one currently authorized receiving device at the exact target mailbox. An invitation is per target transport copy, not a group-wide bearer permission.

Use the existing [canonical mailbox spelling](mailbox-addresses.md), [identity identifiers and bundles](identity-state.md), [strict encoding](event-encoding.md) and [credible-clock/freshness rules](freshness.md). The current receiving assertion is original assertion10 for the [selected asynchronous agreement](suite-profile.md#asynchronous-protected-agreement), with native packages validated by the maintained MLS implementation. Use the maintained implementations and exact selected cryptographic algorithms; this binding introduces no new cryptographic primitive.

`Time` means a canonical unsigned-64 decimal JSON string of UTC epoch seconds. `Id` means a random nonzero 16-octet ObjectId encoded as 32 lowercase hexadecimal characters. `Hash` means SHA256 of the named complete original bytes, encoded as 64 lowercase hexadecimal characters. `Nonce` means 32 random octets encoded as 64 lowercase hexadecimal characters. `Bytes` means canonical padded standard base64, with no whitespace. Overflow, unsupported current address validation, duplicate decoded members, null, unknown fields and wrong types fail the selected binding without partial activation.

Every publication selects an explicit signed interval. The issuer chooses it within actual credential/key custody, receiving capability and local policy. The recipient applies its configured finite validity/processing policy; it can decline an excessive interval without silently shortening an already published promise. There is no new fixed duration or default. Examples measured in days below illustrate offline operation, not a mandated lifetime.

Creation/release requires the whole credible current interval inside original publication and relevant authority intervals. Delayed receipt uses the original independently promised receive deadline and current accepted continuous authority, preserving the existing purpose-specific continuity/repair boundaries. An incoming claimed historical signing time cannot excuse revocation, a role/key gap, repair or a newer retained clock floor. Receipt Date and Message-ID are not trusted clocks.

:::

::: {.details summary="3. Invitation record"}

### 3. Invitation record

**3.1 Exact wrapper and signature**

The decoded invitation attachment is exactly `{payload,signature,identity}`. `payload` is Bytes of one original strict UTF-8 JSON payload; `signature` is the 64-octet Ed25519 signature as 128 lowercase hexadecimal characters; `identity` is one exact identity-bundle1 object. For this candidate, bound the complete decoded invitation wrapper to 8,388,608 octets and its original decoded signed payload to 262,144 octets. Apply the actual identity-bundle1 complete strict-JSON bound of 4,194,304 octets from the [identity-bundle1 contract](identity-state.md#concurrent-administration-and-retirement), with independent state/binding payload limits. The complete candidate wrapper has maximum JSON depth 32; this whole-wrapper scope is a candidate wire choice, not an inherited standalone-bundle limit. Carrier/header/encoded-body work is independently bounded before allocation.

Sign ASCII `mail/upgrade-invitation/v0`, NUL, U32 big-endian original payload length and exact original payload bytes, using the inviter's device signing key. The bundle supplies candidates and dependencies; it is not trusted merely because it arrived.

The payload has exactly these members, all required:

| Member | Type and value |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"conversation-upgrade-invitation"`. |
| `invitation` | Id, unique within the actual inviting principal/device namespace. |
| `source`, `target` | Distinct canonical mailbox strings, exact source and selected target of this ordinary transport copy. |
| `principal`, `device` | Existing principal/device identifiers for the inviter. |
| `state`, `binding` | Hashes of the inviter's original signed identity-state and device-binding payloads. |
| `agreement` | String `"mail-conversation-v2"`. |
| `carrier` | Exact single generated Message-ID field value, excluding field name and surrounding field whitespace; syntactically valid under the accepted Message-ID generator/parser. |
| `nonce` | Nonce, retained unchanged in every response to this invitation. |
| `notBefore`, `notAfter` | Time; ordered publication/response-creation interval. |
| `receiveUntil` | Time, at least `notAfter`; last promised setup-offer receipt time. |
| `replyKey` | Exact object `{id,publicKey}`: Id and 32 canonical X25519 public-key octets encoded as 64 lowercase hexadecimal characters. |

The signed creation interval and complete receiving promise must fit the inviter's applicable receiving credential/custody promise at issuance. The inviter has current `send` and `receive` authority when publishing this invitation through its actual selected account. Generate independent X25519 material; never convert or reuse a signing, MLS, route, pairing, backup or ordinary control key. The identifier is unique across the local inventory, including other key roles. Before publication, verify possession and durably retain original descriptor, exact key owner/role, deadlines and protected custody.

The `replyKey` role is exactly `upgrade-offer-receive`. It selects only the frame in §6 and only the setup-offer body in §5. It cannot be published as assertion10's ordinary `controlKey`, accept another kind or authorize sending. No valid application message or MLS Welcome in this protocol uses this key; arbitrary HPKE ciphertext cannot be made semantically safe by its key role alone. The invitation contains no admission package, draft/content digest, body, subject, group roster, historical quotation, native conversation ID, callback or service URL.

`carrier` binds the invitation to the observed transport copy, not to its prose. A copied invitation cannot authenticate the body around it or identify the human author independently. The invitation authorizes a targeted setup offer to `source`, from an eligible device at `target`, within the original interval, and completion of the bounded confirmation below under current local account policy. It authorizes neither a written reply nor ordinary content release.

**3.2 Ordinary MIME placement**

Use ordinary required headers and the real human subject/body. There is exactly one MIME-Version of 1.0, one unambiguous outer `multipart/mixed`, the normal readable body first, ordinary user attachments if any next, and exactly one final direct invitation child. A multipart/alternative readable body may be the first child. The invitation child has:

- `Content-Type: application/vnd.threadlabs.mail-upgrade-invitation+json`, without parameters;
- `Content-Transfer-Encoding: base64`;
- `Content-Disposition: attachment; filename="mail-upgrade-invitation.json"`.

Use legal MIME base64 folding, canonical alphabet/padding and complete decoding. The filename is explanatory, not authority. Reject duplicate singleton part headers, multiple invitation children, ambiguous framing/parameters, invalid transfer encoding, trailing decoded JSON and resource-limit excess for automatic activation. Do not scan descendants, forwarded message/rfc822/global, archives, quotations, arbitrary attachments or HTML for a candidate. Human reading survives inactive metadata.

There is one selected SMTP envelope recipient for this prepared copy. Visible To/Cc remains the deliberate ordinary-message projection. No invitation requests an extra recipient. Blind copies receive independently prepared invitation, carrier and control identities under existing private-copy separation; no shared upgrade correlation is exposed across copies. This binding does not promise that ordinary addressing conceals a recipient already visible in the author's headers.

:::

::: {.details summary="4. Source and target gates before automatic answering"}

### 4. Source and target gates before automatic answering

Process the readable mail first as ordinary mail. The following complete gate authorizes an automatic offer; recognizing a type, subject or key never does:

1. Validate the exact direct invitation placement and original signature under the independently resolved identity and current role rules. Check interval, clock, budgets, actual target selection and retained blocks before expensive or outbound work.
2. Require exactly one actual parsed outer From mailbox, matching signed `source`; exactly one Message-ID, matching signed `carrier`; no Sender, Resent-* or List-* fields; and Auto-Submitted absent or exactly one value `no`. Reply-To may be present for the human message but is never a setup destination. Several To/Cc mailboxes are allowed; they do not select the control target.
3. A configured trustworthy receive component supplies the actual directly delivered local mailbox and authoritative SMTP reverse-path for this exact stored message. They must equal signed `target` and signed `source` respectively. Reverse-path is nonnull. Forward/list/alias expansion without independently authorized exact mailbox selection cannot supply this proof. Do not infer equivalence by plus tags, case folding or contact names. A downloaded Return-Path string alone is insufficient. DKIM authenticates neither SMTP reverse-path nor delivery recipient; these independently trusted facts cannot be manufactured from a signature pass.
4. Require trusted full-body DKIM success, no `l=` tag, signing domain exactly the canonical source domain, actual sole From coverage and accepted algorithm policy. Verify independently now, or use an authenticated configured receive producer's retained result for this exact original message. Such a retained result identifies actual arrival/verification time, complete body/From coverage, signer and algorithm decision; accepting it is a pre-existing trust configuration, not trust in arbitrary Authentication-Results text. A result that cannot be bound to this stored source is unavailable. Independent verification after selector removal/expiry can fail; that failure does not create a weaker automatic path. The invitation and device authority must still be operationally eligible now.
5. Apply recipient automatic setup/disclosure policy, exact source identity/continuity/pin rules and finite per-domain/address/principal/device/account/total-work budgets. No new prompt is required by this candidate. A known valid unrelated claim cannot repin an existing correspondent; invalid evidence cannot reserve an identity, create a conflict tombstone, erase a key or stop valid work.

These gates deliberately retain the accepted strict reverse-path and domain-accountability checks while allowing ordinary To/Cc and human content. They do not prove source-local-part ownership or independent human identity. A dishonest signing domain or compromised account can still abuse a valid invitation. A provider that rewrites the reverse-path or does not expose trustworthy envelope facts may deliver the ordinary message but cannot satisfy this automatic path. That is an explicit supported-input limitation, not a requirement to replace its SMTP server or a claim that every existing IMAP account already supplies the evidence.

The durable solicitation permission is new and explicitly scoped; it is not an accepted setup2 request with its timer renamed or extended. The new permission is the exact authenticated invitation, attached to a deliberate real send. A recipient is not probing an unknown legacy account: it is answering the compatible inviter that signed permission to receive this specific response. Do not contact a URL, start login, request a read receipt, send a rejection notice or answer an invitation that fails these gates. Block and budget policy applies even when the domain signature is valid. A replay at the original target can still provoke the one originally authorized offer if that target has never processed it; this is retained permission, not evidence of a new human send or recent intent. A different envelope target fails the signed target gate. A legitimate old invitation does not permit a second offer after terminal processing. This bounds backscatter authorization; it does not claim universal spam prevention.

Before cryptographic work or DNS lookup, enforce finite header/body/part counts, signature/key-size and aggregate verification-work limits. Bound DNS operations, response bytes, alias traversal, time and concurrency under the configured resolver/network policy; arbitrary received URLs are never DNS-key callbacks. Cache within current DNS/key-policy limits, including failures where allowed, without converting DNS outage, key revocation or lookup exhaustion into positive authentication. Distinct attacker-selected selectors can leak verification activity to their authoritative DNS operator; configured trusted receive verification or a shared resolver can reduce direct-client exposure but does not prove invisibility. Never label DNS or DKIM as independent first-contact device verification.

:::

::: {.details summary="5. Fresh receiving offer produced when the recipient returns"}

### 5. Fresh receiving offer produced when the recipient returns

After the gate passes, the responder prepares an ordinary assertion10 with its current eligible public control key and a separately valid unused MLS package, under the exact selected application. The offer is newly created receiving publication, not an answer proving live presence to an active 600-second request. Its assertion, ordinary control key and MLS package keep their own independent intervals and single-use/allocation rules.

The offer wrapper is exactly `{payload,signature,identity,advertisement}`. Payload, signature and identity have §3's types and independent limits. `advertisement` is Bytes of the complete original assertion10 wrapper, limited by its owning bounds. Sign the original offer payload using ASCII `mail/upgrade-offer/v0`, NUL and U32-length/original bytes. The complete decrypted offer wrapper is at most 8,388,608 octets and depth 32. Its original decoded signed payload is at most 262,144 octets; its complete identity-bundle1 strict JSON is at most 4,194,304 octets under the actual accepted identity contract. The decoded advertisement is the complete original assertion10 wrapper, at most 1,048,576 octets under its separate passive-discovery wrapper contract; that 1 MiB bound is not an identity-bundle1 limit. Base64 expansion counts toward the outer wrapper limit. These distinct limits also apply to confirmation wrappers. An otherwise valid standalone bundle or advertisement that exceeds the selected complete-wrapper depth/size is an explicit unsupported-size/depth outcome, never a truncated accepted prefix.

The offer payload has exactly:

| Member | Type and value |
| --- | --- |
| `version`, `purpose` | Strings `"0"`, `"conversation-upgrade-offer"`. |
| `offer` | Fresh Id for this immutable responder outcome. |
| `invitation` | Original invitation Id. |
| `invitationDigest` | Hash of the complete original signed invitation payload bytes, not MIME or reserialization. |
| `nonce` | Original invitation Nonce. |
| `source`, `target` | Canonical mailboxes: responder's mailbox (original invitation target), then inviter's mailbox (original source). |
| `principal`, `device`, `state`, `binding` | Actual responder and its original signing identity references. |
| `recipientPrincipal`, `recipientDevice` | Exact original inviter identifiers. |
| `key` | Original invitation replyKey Id. |
| `agreement` | String `"mail-conversation-v2"`. |
| `evidence` | String `"publication"`; there is no live mode in this binding. |
| `assertion` | Hash of the complete original advertisement-wrapper bytes. |
| `notBefore`, `notAfter` | Time; ordered creation/release bounds contained by the invitation publication interval, original responder binding and assertion/control-key publication bounds. |
| `receiveUntil` | Time, at least offer notAfter and no later than original invitation receiveUntil. |
| `confirmationKey` | Exact object `{id,publicKey,notBefore,notAfter,receiveUntil}` under the existing control-key descriptor scalar grammar, with fresh independent X25519 material and role exactly `upgrade-confirmation-receive`. |

Offer receipt may be delayed through its signed receiveUntil if the original invitation key is retained and current continuous authority remains eligible. Operational use of its assertion still requires the whole current interval inside that assertion's own permitted use window, required freshness and current authority. Receiving an old offer cannot refresh its package, key, assertion or pin. A longer outer receive promise does not make expired setup usable.

The offer's sender, advertisement actor/mailbox, outer response From, signed `source` and local selected responder account all agree exactly. The offer's recipient/key, original invitation actor/source, outer To, signed `target` and retained initiating account agree exactly. Check recipient/key before encryption. No sender-selection field inside an incoming bundle supplies trust.

Identity of the one responder outcome is `(inviter principal, inviter device, invitation, responder principal, responder device)`, across MIME rewrites and all attempts at this candidate version. Reserve it only after authentication. Exact repeats return the same stored original payload, advertisement, package allocation, sealed bytes and mail submission. Different authenticated bytes are a retained outcome conflict, never an arrival-order winner. Invalid variants cannot poison the outcome.

The confirmation key and its descriptor are durably owned by the actual responding device. The complete publication interval fits its current receiving credential, and its independent receiving promise fits actual protected custody. It authorizes exactly one original inviter/device to return one terminal confirmation for this offer, with no further automatic response. Its original promise may outlive the invitation: this is a separately signed child permission, not extension of the original reply key or invitation. No package, group key or device-signing key can supply it.

The MLS package reference is reserved to this actual peer/invitation allocation under the existing allocation realm before disclosure. Do not also publish it into an independent pool or reuse it under another offer, alias, ID or version. A new offer or signature does not make a package reusable. The recipient independently validates and atomically consumes actual admission material later.

:::

::: {.details summary="6. Confidential offer frame and SMTP response"}

### 6. Confidential offer frame and SMTP response

Use [RFC9180 single-shot HPKE Base mode](https://www.rfc-editor.org/rfc/rfc9180.html#section-6.1) with the existing suite: KEM 0x0020 DHKEM(X25519,HKDF-SHA256), KDF 0x0001 HKDF-SHA256, AEAD 0x0001 AES-128-GCM. Use a maintained implementation and its canonical public-key/invalid shared-secret checks. No custom nonce, PSK, Auth mode or alternate suite is selected.

The separate candidate frame is exactly eight ASCII octets `MAILUPG0`, 16 raw reply-key ID octets, 32 HPKE encapsulated-key octets, U32 big-endian ciphertext length, then that many ciphertext octets including the 16-octet tag. No trailing objects. Plaintext is exactly the complete strict offer-wrapper JSON from §5, not a generic sealed-control intent or arbitrary body. HPKE info is ASCII `mail/upgrade-offer-encryption/v0`, NUL, raw key ID, selected 32 public-key octets and 32 raw invitation-payload-digest octets. AAD is magic, raw key ID and the four length octets. Ciphertext length is plaintext length+16. With the candidate 8,388,608-octet plaintext-wrapper limit, ciphertext is at most 8,388,624 octets and the entire 60-octet-header binary frame at most 8,388,684 octets. These limits apply before allocation; transfer-encoded MIME work has its own finite configured bound. Every new outcome uses fresh single-shot encapsulation; retries reuse the retained ciphertext.

This is a domain-separated container built from the existing HPKE primitive, not permission to add a kind to accepted sealed2 or fall back between decoders. The reply-key ID locates exactly one locally issued role/owner/invitation descriptor. An unknown or expired key produces no response or fallback. A header hint cannot choose an own account or authorize a package. Decrypt and authenticate fully in private staging, then validate exact JSON, original signature, association and all correlations before an effect. No body accepts an MLS Welcome, group export, content-bearing attachment, archive or general ciphertext blob.

The response mail is exactly one outer multipart/mixed with two direct children: `text/plain; charset=utf-8`,7bit body `A compatible email app returned encryption setup.` plus CRLF, then `application/vnd.threadlabs.mail-upgrade-offer`, parameter-free, base64, attachment filename `mail-upgrade-offer.bin`. Subject is `Email setup`; Auto-Submitted is exactly `auto-replied`; From is the selected responder mailbox; To is the original source mailbox; SMTP has exactly that one recipient and null reverse-path. Normal Date and one independently allocated Message-ID are retained. In-Reply-To contains the exact original invitation carrier value for explanation only. No Cc/Bcc/Sender/Reply-To/Resent/List/receipt fields, extra parts, readable proof or resource URL. Request NOTIFY=NEVER where DSN is supported. Exact structural/canonical decode and total-work rules from §3 apply.

The inviter accepts only an actual direct delivery to the retained own source account with matching sole outer From/To, exact candidate frame and original pending invitation/key. Trusted exact-domain full-body DKIM remains required; response null reverse-path is expected and is not compared to From. An actual retained original invitation proves that this client authorized the response; an unsolicited offer cannot create that permission. Outer In-Reply-To, Message-ID, HPKE success or a sender's self-signature alone cannot create the pending invitation or a verified identity.

A valid accepted offer authorizes only the one terminal confirmation below. It never triggers another offer, challenge, URL fetch, key refresh or automatic human message. An invalid envelope, unavailable evidence, decryption failure or retired ID produces no automatic email. Local diagnostics remain inspectable.

**6.1 One terminal confirmation supplies the reverse direction**

After independently accepting the responder’s exact offer and association, the inviter automatically prepares its own current ordinary assertion10 with eligible unused package and ordinary control key for this exact peer/device. This is separate from the invitation reply key. The offer’s explicit confirmation grant and the still-current account/setup policy authorize this one content-free completion; receipt of arbitrary mail does not. No new human composition or 600-second live challenge is invented.

The confirmation wrapper is exactly `{payload,signature,identity,advertisement}`, with the same scalar types and byte/depth bounds as the offer. Its payload has exactly these members:

| Member | Required value |
| --- | --- |
| `version`, `purpose` | Strings `"0"`, `"conversation-upgrade-confirmation"`. |
| `confirmation` | Fresh Id, retained as the immutable child outcome. |
| `invitation`, `invitationDigest`, `nonce` | Original invitation Id, original signed payload Hash and Nonce. |
| `offer`, `offerDigest` | Original offer Id and Hash of its exact signed payload bytes. |
| `source`, `target` | Original inviter mailbox, then this exact responder mailbox. |
| `principal`, `device`, `state`, `binding` | Inviter’s actual currently authorized signing device; principal/device equal the original invitation actor, with original and current authority validated independently. |
| `recipientPrincipal`, `recipientDevice` | This exact offer’s responder principal/device. |
| `key` | Original offer confirmationKey Id. |
| `agreement`, `evidence` | Strings `"mail-conversation-v2"`, `"publication"`. |
| `assertion` | Hash of the complete original confirmation advertisement wrapper. |
| `notBefore`, `notAfter` | Ordered Time creation/release bounds fitting the original confirmation-key publication, current source/target authority and supplied assertion/control-key publication bounds. |
| `receiveUntil` | Time at least notAfter and no later than the original confirmationKey.receiveUntil. |

Sign ASCII `mail/upgrade-confirmation/v0`, NUL, U32-length and original payload bytes. The advertisement actor/mailbox and current identity agree with the original inviter and actual selected source account. Reserve the package to this exact responder-device child allocation; confirmation to another responding device requires independently eligible admission material, not reuse of one joining package.

Encrypt once using the same maintained HPKE suite and binary layout as §6, with magic exactly `MAILUPC0`, info ASCII `mail/upgrade-confirmation-encryption/v0`, NUL, raw confirmation-key ID, selected 32 public-key octets and 32 raw offer-payload-digest octets. AAD remains magic/key ID/ciphertext length. Plaintext is exactly this complete confirmation wrapper. The receiving key role is only `upgrade-confirmation-receive`; do not try invitation reply keys, accepted sealed2, or ordinary control keys. Domain separation and narrow APIs constrain protocol use; HPKE does not by itself certify the semantic type of plaintext.

The mail is the same exact two-child response structure, with notice `A compatible email app completed encryption setup.` plus CRLF, Subject `Email setup`, and second part `application/vnd.threadlabs.mail-upgrade-confirmation`, parameter-free, base64, attachment filename `mail-upgrade-confirmation.bin`. From/To are inviter/responder, reverse-path is null, Auto-Submitted auto-replied, and In-Reply-To is the retained offer mail’s Message-ID for explanation only. Apply all other response header/transfer restrictions. Authoritative actual delivery, exact-domain full-body trusted DKIM, retained original offer/key grant and all original correlations are required. No incoming header can supply a missing own-account child permission.

Child identity is `(original inviter principal/device/invitation, responder principal/device/offer)`. Authenticate before reserving it. Serialize one confirmation outcome and package allocation with exact bytes/outbox before release. Repeated accepted offer delivery reconciles the saved child; it never automatically resubmits mail. Changed authenticated confirmation bytes under that child identity conflict. At the responder, atomically retain accepted receiving evidence, consumed-control outcome and terminal key retirement intent. Replays cannot allocate, send or install another native effect.

The confirmation is terminal: it elicits no automatic email, acknowledgment, challenge, receipt or error. A forged confirmation cannot advance/close the real pending operation or retire its key. Confirmation receipt supplies publication evidence only. Reverse-direction native admission, single-use enforcement and final content release remain separate. A missing/invalid/expired confirmation leaves Bob→Alice unready, while already eligible Alice→Bob can progress. No global all-ready flag or user-facing successful-send claim is created.

:::

::: {.details summary="7. Durable operation, lifetime and retirement"}

### 7. Durable operation, lifetime and retirement

Before releasing the original ordinary message, atomically retain its immutable send intent/revision and exact prepared mail, invitation bytes/identity, account/peer selections, reply-key original descriptor and protected possession, deadlines and invitation-outcome state. A policy-authorized ordinary send may proceed if the upgrade attachment cannot be prepared only by deliberately selecting a representation without it before release; an uncertain already submitted message cannot be silently replaced with a second invitation-bearing message.

A responder atomically reserves its offer/package/confirmation-key custody and exact signed/sealed/mail bytes before submission. The inviter applies the same reserve-once rule to the confirmation child and its separate receiving package. Recheck current account/identity/disclosure/block/time authority after heavy preparation and at actual SMTP release, including after 354. On each receive side, perform the corresponding full current dependency/clock/policy checks after heavy validation and immediately before atomic acceptance, conflict/terminal retention or key-retirement commitment. Historical exact retries return only their recorded outcome and cannot create a new effect after expiry. Concurrent workers return the one retained outcome, not another package. SMTP final-ack loss remains possible execution; restarting or receiving a duplicate invitation does not enqueue another mail. A separately authorized bounded transport retry uses the same exact mail/outcome, never another offer identity. No response can turn ordinary-mail uncertainty into proof the human message was received.

Several independently authorized devices may each supply their own outcome; no account-wide exactly-once promise exists without actual shared serialized state. The inviter evaluates the complete currently available candidate batch under its accepted association policy, then freezes only the actual eligible receiving cohort under the owning suite. It never treats one offer as readiness for all account devices or a group roster. Parallel devices that share storage coordinate actual invitation/key ownership and outcomes there; independent devices do not inherit each other's secret or grant.

Retire the invitation-only reply key on original receiveUntil, cancellation/withdrawal, or durable completion of the selected acquisition/handoff. A validated offer alone cannot delete it before the selected response/cohort decision and retained candidate snapshot are committed. If more required device evidence remains pending, retain only through the original promise. Completion closes the invitation to new operational responses; late legitimate other-device offers remain nonactivating diagnostics and require future independently authorized discovery to add a device. They do not reopen a completed cohort.

The responder retires its confirmation-only key on independently signed receiveUntil, explicit local cancellation/withdrawal, or durable acceptance of the exact confirmation. It preserves the offer/child outcome through its original eligibility period; a lost confirmation cannot silently renew the grant or create a second child. Invitation-key retirement does not delete an independently queued eligible confirmation or extend its key.

Retirement is a durable close-and-delete operation under the same generation fence as receive/outbox activation. On crash after closing but before deletion, startup reconciles deletion; it cannot use the closed key. Missing key bytes are not erasure evidence. A restored stale key cannot reopen a closed invitation; missing/inconsistent anti-rollback state holds rather than recreating authority. Retain terminal/replay and original descriptor facts at least while the original invitation can authorize a new response or receipt, independently of private key deletion. Finite retention policy may keep them longer. Only after original eligibility is irreversibly expired under the retained credible-time/rollback floor can their removal cease enabling new automatic effects; absence alone is never a fresh permission. The dedicated key must not enter ordinary device pairing, contact export or correspondence archives as ongoing receiving authority.

Unauthenticated later mail cannot close, withdraw, rotate or overwrite the key or extend a timer. A formerly valid offer replay after completion returns only its existing local outcome, with no new native effect, readiness expansion, package use or submission. Unknown outcomes after expiry remain expired; they cannot resurrect a deleted key. Required native single-use cleanup still occurs separately after actual native admission, not merely after receiving public setup.

:::

::: {.details summary="8. Offline sequence and per-direction readiness"}

### 8. Offline sequence and per-direction readiness

An illustrative ordinary invitation can be explicitly issued with a multi-day response interval, provided its actual binding and reply-key custody support that promise. Bob's client processing it days later creates an offer with its own current usable ordinary receiving assertion/package. Alice processing that offer later can prepare Alice→Bob delivery asynchronously, while those independent publication/admission bounds still permit it. Bob need not be online at that moment. The original invitation key reveals only public setup metadata if later compromised; it never decrypts Alice's later conversation content.

Bob→Alice is a different readiness state. Bob’s fresh offer authorizes one terminal confirmation containing Alice’s newly selected ordinary receiving assertion. Alice can send that confirmation after returning online, and Bob can consume it later while its independently promised key/offer bounds remain eligible. Neither ordinary receiving publication depends on keeping a 600-second request alive or on releasing human writing. Each direction performs its own native admission when needed. A valid offer readies only Alice→Bob evidence; a valid confirmation supplies Bob→Alice evidence. Readiness still depends on actual eligible devices, freshness and native context, not merely a completed email count.

If required policy demands a live response rather than publication evidence, start the existing newly scoped 600-second challenge only through an independently authorized accepted setup path once its preconditions are met. This candidate's invitation/offer never counts as that live proof and does not automatically emit a challenge. Offline published capability can permit encryption without establishing current online presence. Unavailability of a live proof does not weaken that policy.

Simultaneous Alice/Bob invitations remain separate signed operations and response keys. Each can elicit at most its per-responder offer and that offer’s one terminal confirmation. Do not choose a winner by subject/date/address order or merge package allocations, native streams or invitations. Independently eligible evidence may satisfy future composition under its own allocation; reusing one package twice is forbidden. Each completed invitation retires its own key and cannot erase its opposite operation. A later authenticated application contract, not a UI heuristic, owns any native conversation convergence.

**Local phase transitions**

| Owning state | Authenticated event | Only automatic mail permitted | Durable result |
| --- | --- | --- | --- |
| Inviter ordinary send frozen | Actual selected policy and publication/custody valid | Original real message plus invitation | Retained I/outbox/key; submission outcome separate. |
| Responder I unseen | All direct-authentication/current-policy gates pass | One offer O per actual responding device | Original I, package reservation, confirmation-key custody and exact O/outbox committed together. |
| Responder O submitted/uncertain | Duplicate I | None from duplicate arrival | Same retained O and transport uncertainty. |
| Inviter I outstanding | Valid O under actual I/key and current association | One confirmation C per O child | Accepted O/evidence plus original C/package/outbox mapping; no human-send effect. |
| Inviter child submitted/uncertain | Duplicate O | None from duplicate arrival | Same child and transport uncertainty. |
| Responder O outstanding | Valid C under exact original O/key | None | Accepted A receiving evidence and terminal C outcome/key-retirement intent. |
| Any phase terminal/expired/cancelled | Replayed/changed/forged records | None | Existing outcome/conflict/diagnostic only; no resumed authority. |

The three message purposes form a finite chain I→O→C. No C→I, C→O, O→O, error→request or timer→new-identity transition exists. Transport retry is the owning saved mail operation, not another phase or package. Fresh legitimate human sends may create independent invitations under current policy; incoming traffic cannot manufacture those human send intents.

:::

::: {.details summary="9. History, groups, reply policy and user-visible results"}

### 9. History, groups, reply policy and user-visible results

The readable original stays ordinary and remains attributed under its actual provenance. The invitation's signed carrier reference permits a local explanatory link to that original mail, not verified-body status or an interoperable authenticated parent. Use **a fresh protected root**, with any local ordinary-history connection explicitly unverified. No transmitted bridge, automatic history import or authenticated stitching claim is introduced. The local history link does not supply authentication for ordinary prose; a future interoperable history bridge needs its own explicit authenticated contract.

For groups, issue independent invitations only on the ordinary copies actually authorized for those targets. Each peer/direction/delivery has its own evidence, expiry, offer and native cohort. Pending invitees stay pending; ready protected copies can proceed under the frozen existing progression policy. No reply membership is inferred from To/Cc. Private/Bcc branches retain separate identities and no shared private activity disclosure. Existing protected conversations never become ordinary because setup fails, a key expires, a lookup times out or an error arrives.

Setup is control traffic, not a written reply, and does not create discussion membership. The invitation can appear on a no-written-replies message only if the sender's ordinary publication policy selected it; its explicit permission authorizes the targeted offer only. No-replies/private-only/discussion intent still governs future written composition and authenticated operations under the selected agreement. This candidate does not suppress intentional independent email composition by legacy clients or promise they enforce reply restrictions.

Show compact per-recipient/direction protection when composing and the actual protection on each sent contribution. After accepted setup/admission, both compatible clients can show the upgrade boundary from their actual evidence. Publication receipt alone is not “message sent,” “read,” “verified person” or “all devices ready.” Machine mail can be grouped as inspectable setup activity in upgraded clients; a legacy client may show it normally. No invitation causes a plaintext resend of previously protected content or an encrypted duplicate of the original ordinary message.

:::

## Authentication limits and acceptance

[DKIM threat analysis](https://www.rfc-editor.org/rfc/rfc4686.html) describes signed-message replay, reflection and verifier/DNS attacks. Those limits require independently selected targets, bounded work and durable original outcomes here. [DKIM architecture](https://www.rfc-editor.org/rfc/rfc5585.html) separates signing-domain responsibility from endpoint identity; [deployment guidance](https://www.rfc-editor.org/rfc/rfc5863.html) distinguishes trustworthy verifier results from arbitrary received headers. Existing [algorithm and coverage requirements](security.md#domain-signatures-and-algorithm-policy) remain authoritative. Historical Sender Signing Practices, old algorithm recommendations and obsolete local-part delegation rules are not selected by this binding.

A copied signature can remain valid without proving a new send or present intent. An offer and confirmation carry published receiving evidence, not live-presence proof. A required live confirmation still uses its independently authorized freshness mechanism. These boundaries reduce specific automatic-response risks; they do not establish universal spam prevention or independent first-contact verification.

::: {.details summary="Acceptance cases and implementation evidence"}

### Acceptance cases

| Case | Required observed result |
| --- | --- |
| Usable pre-existing receiving evidence | First human message protected; no forced ordinary prelude. |
| Unknown legacy recipient, ordinary permitted | One real readable message plus attachment; no standalone blind probe, timeout-triggered new invitation or setup-error mail. |
| Compatible recipient processes ordinary mail days later | Current eligible invitation produces one freshly created confidential offer through actual SMTP/retrieval; invitation reply key has never been an MLS/group key. |
| Inviter returns later, offer still eligible | Its exact confirmation is queued once; receiver later validates fresh inviter publication. Each direction can independently admit a future protected message while its peer is offline. |
| Live verification required | Offer remains publication evidence; no false live badge or policy weakening. |
| Signature/DKIM/header/target/custody gate fails | Ordinary body readable; no response, callback, association overwrite, conflict poison, key deletion or ordinary fallback from protected state. |
| Reverse-path rewritten or trustworthy producer unavailable | Explicit unavailable automatic setup; no raw Return-Path/Authentication-Results trust. |
| Invitation forwarded, nested or moved to another target | No automatic answer or enrollment; copied Message-ID cannot overcome exact account/target/authentication checks. |
| Invalid/all-zero/noncanonical X25519, key ID collision, wrong frame role | Maintained crypto/ownership validation refuses; no alternate decoder/key trial. |
| Multiple devices / simultaneous real sends | Actual per-device outcomes and separate invitations retained; no account-wide lock claim, crossed-key substitution or duplicated package use. |
| Offer/confirmation cross-kind substitution or forged terminal reply | No parser/key-role fallback, automatic reply loop, premature key deletion or unscoped ready state. |
| Duplicate delivery after SMTP acknowledgment loss | Original sealed bytes/mail/outcome and possible-execution state; no second automatic submission from arrival alone. |
| Authenticated changed offer under same responder identity | Retained conflict, no first/last writer selection; invalid competing bytes cannot poison. |
| Close/expire/cancel race with heavy validation or354 | Serialized final current check wins; original secret promise is not refreshed; already released bytes retain actual uncertainty. |
| Crash before/after reserve, seal, submit, accept, cohort freeze, key retirement | Same original operation resumes or holds; no recreated key, package, identity, native effect or human message. |
| Restored old key / forged late replay after terminal close | No reopened response acceptance or new effect; inconsistent restore state fails closed. |
| Cc/Bcc/no-replies/mixed groups | No audience widening or private correlation; per-recipient protection and independent pending state remain accurate. |
| Original ordinary mail displayed beside fresh protected root | Original remains ordinary/unverified history; no retroactive encryption, false authored0 reference or automatic content retransmission. |

Actual acceptance requires maintained cryptography and actual mail adapters, recorded submitted/retrieved bytes and trusted provenance, durable multiworker/restart tests and independently checked secret roles. These are acceptance obligations, not evidence of an implemented interoperable deployment, physical key erasure or complete Email/2 conformance.

:::
