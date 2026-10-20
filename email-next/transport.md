---
title: Transport and delivery
order: 6
blurb: SMTP baseline · retries · provider upgrades
sectionNav: true
---

# Transport and delivery

Email Next initially travels as ordinary MIME mail through existing submission, relay and delivery services. An upgraded client does not require a new SMTP command to send a structured contribution. Provider upgrades can add discovery, control-message routing and faster delivery through separately negotiated contracts.

> [!note] Proposed application contract
> The requirements below define how an Email Next client interprets transport outcomes. They do not replace SMTP. MIME packaging, submission integration and security-profile selection remain dependent work. The [SMTP audit](audits/smtp.md) records source coverage and unresolved dependencies.

## Contribution, delivery and attempt

A contribution is the authored event. A delivery is a representation of that contribution prepared for a particular recipient set and security policy. An attempt is one transport operation for that delivery. These objects have different lifetimes.

Before submitting a delivery, the client records the immutable contribution, intended envelope recipients, prepared representation, protection mode and retry state durably. A retry preserves the contribution identity and meaning. It must not create another answer, service submission or reaction merely because transport was interrupted.

The exact relationship between contribution identity, MIME part identity and `Message-ID` is specified by the eventual wire profile. A retry does not repurpose `Message-ID` as a fresh attempt identifier. A delivery with materially changed content is a new message version; a new application contribution is necessary when the author changes the contribution itself.

A client may group recipients into one SMTP transaction only when they receive the same prepared message and that grouping preserves confidentiality. Bcc recipients require recipient-isolated metadata and protection against leakage through shared envelopes and trace fields. Separate Bcc transactions are the proposed default. Do not expose hidden recipients in an event's shared audience or encryption-key list.

## Local authorization and release

Preparing or durably queuing a delivery does not authorize a transport worker to submit it indefinitely. The prepared record MUST retain the immutable contribution and encoded representation, exact envelope recipients, protection and fallback policy, authenticated group identifier and epoch when applicable, and the identity-state and binding digests on which its device authorization depends. These references are dependencies to recheck, not proofs of current authority.

When preparing encrypted content advances local cryptographic state, the client MUST commit that updated state and the exact prepared ciphertext together. Recovery must expose either both or neither. Repeating preparation for the same immutable delivery returns the retained bytes; it must not encrypt again from an earlier state. This prevents a crash from leaving ciphertext available for sending while its corresponding state change has been lost.

The client maintains one durable attempt record for each client-controlled submission attempt. That record binds a unique local attempt identifier to the prepared delivery, its participating envelope recipients and the authorization dependencies actually checked. Local attempt identifiers are bookkeeping; they do not replace the contribution identifier or Message-ID and need not be exposed on the wire.

Before a worker can start an attempt, one serialized local operation MUST:

1. Confirm that no other worker owns an in-progress attempt for the same delivery and recipients.
2. Resolve the current accepted identity heads, selected bindings, role and validity checks, applicable freshness policy, and the accepted group epoch and complete roster. The caller's previously successful snapshot cannot replace this check.
3. Compare the prepared dependencies with those results. A conflict, missing evidence, changed policy, changed group epoch or superseded identity dependency holds the prepared attempt. The application may explicitly reauthorize and reconstruct a replacement delivery; it cannot merely relabel the old ciphertext.
4. Durably record authorization and exclusive ownership of the attempt before permitting that worker to transmit it. Identity-state installation, group-state installation and this authorization operation must share a serialization boundary. An already installed local revocation cannot be bypassed by an earlier computation.

That operation is the local release decision. It is distinct from successful SMTP handoff. A local outbox insertion, worker claim, socket connection or RCPT acceptance MUST NOT be presented as proof that a server accepted responsibility. A worker must transmit only the immutable representation and recipient subset bound to its attempt; content or target changes require a new authorized delivery decision.

The release decision covers one attempt, not an open-ended retry delegation. A worker that loses ownership or is replaced cannot resume using its old authorization. Before reassignment, the system must establish that the previous worker can no longer transmit, or retain an uncertain in-progress state; expiry of a lease alone cannot fence a live SMTP connection. A replacement worker must not create concurrent retries merely because a local timer elapsed.

### Changes after local release

A locally accepted revocation before the release decision blocks it. A revocation accepted after release is ordered after that attempt's authorization. The worker SHOULD abort an attempt known not to have disclosed message data when it learns of the change; it MUST NOT claim that this can recall already transmitted data. Other devices and providers may learn the revocation later, so this rule supplies local ordering rather than a global cutoff time.

A subsequent client-controlled retry is a new attempt and MUST recheck current authorization, including after an explicit temporary failure or an uncertain result. If the old ciphertext includes a device now known to be unauthorized, hold that retry. Preserve evidence that an earlier uncertain attempt may already have disclosed the content. Neither holding the retry nor generating newly authorized ciphertext makes the earlier copy inaccessible.

After a server has accepted responsibility, its relay retries follow SMTP. The client cannot treat those remote retries as locally cancellable or silently submit another copy as a replacement. Any corrective delivery retains the original contribution identity only if its authored meaning remains identical and the contribution's duplicate/conflict rules permit that representation. Editing the authored content uses its defined new-event or edit semantics.

### Crash and recovery outcomes

| Durable evidence after recovery | Required interpretation |
| --- | --- |
| Prepared delivery with no released attempt | No attempt authorized by this record; current checks are required before release |
| Released attempt with no conclusive transport outcome | Potentially transmitted; preserve uncertainty and establish worker termination before another attempt |
| Final successful submission response durably recorded | Handed off for that response's recipient scope; do not start a client retry |
| Explicit rejection durably recorded | Preserve its scope and temporary/permanent classification; any permitted retry still needs current authorization |
| Response observed but its durable record lost | No durable proof of the result; preserve uncertainty rather than infer acceptance or rejection |
| Accepted identity/group change after an uncertain attempt | Hold new attempts that no longer satisfy policy, while preserving possible earlier disclosure |

The client does not promise exactly-once delivery. A process can fail after server acceptance but before recording the result. Receiver-side contribution deduplication therefore remains necessary even with a transactional local outbox. Recovery must not generate a fresh contribution identifier merely to avoid recognizing the uncertainty.

The [configured sender experiment](evidence/README.md#durable-sender-release) joins preparation, current identity/group checks and local SMTP release. It exercises worker exclusion, uncertain crash recovery and recipient-specific retries. It uses configured envelopes and a loopback server; independent mailbox-ownership verification, deployed submission and restore handling remain outside its evidence.

### Restoring a backup is a separate recovery case

A restored database can be internally consistent while older than a transmitted message. Ordinary crash recovery does not establish that its MLS sending state is safe to reuse. A restored sender MUST hold new encryption until it establishes that its sending state has not rolled back, or completes a fresh authorized admission with new sending secrets. A current identity check alone does not establish either condition.

Do not repair uncertainty by incrementing an application counter, changing the event identifier or repeatedly trying encryption from the restored checkpoint. MLS owns its secret and nonce derivation. Any continuity proof must cover the actual cryptographic sending state and remain trustworthy across the restore that it is meant to detect. A marker restored from the same backup cannot provide that assurance.

Previously prepared ciphertext remains distinct from new encryption. It may be retried only when its exact bytes, recipient scope and attempt evidence are retained and the ordinary release checks permit it. Missing attempt history remains uncertainty; restoration must not turn it into a claim that nothing was sent. Historical reading does not grant permission to resume sending.

The [AEAD interface audit](audits/aead-interface.md) and [GCM nonce-lifecycle review](audits/gcm.md#limits-and-nonce-lifecycle) explain the nonce-reuse boundary. A restore-safe store and its recovery adapter remain required implementation work; the process-crash experiments do not supply them.

## Transport state

State is tracked per envelope recipient and prepared delivery, including the attempt that supplied the observation. The client must distinguish lack of evidence from negative evidence.

| State | Meaning | Permitted next action |
| --- | --- | --- |
| Prepared | Durable message and envelope are ready; no handoff accepted | Recheck current authorization and acquire an attempt before submission |
| In progress | A transport operation is underway | Await its result; do not issue concurrent retries for the same recipient/delivery |
| Retryable | Explicit temporary failure occurred before accepted handoff | Queue a delayed retry subject to current authorization and transport policy |
| Uncertain | Connection failed without a conclusive final result | Preserve uncertainty; a newly authorized retry may duplicate delivery |
| Handed off | Final successful DATA reply or equivalent submission-service evidence records transfer of responsibility | Stop client retries for those accepted recipients; await later evidence if available |
| Failed | Permanent rejection, definitive subsequent failure or retry policy exhaustion | Show failure and preserve evidence; require an explicit corrective action before a new attempt where required |

`RCPT` acceptance alone is provisional. A recipient enters Handed off only when the transaction's final success is known. Rejected recipients do not inherit another recipient's successful outcome. A final DATA rejection applies to the recipients participating in that transaction; a successful final DATA reply does not assert successful final delivery to all of them.

A later non-delivery report may establish failure after handoff, subject to report validation and correlation. An untrusted or uncorrelated report must not overwrite a known delivery outcome, trigger key replacement, resend sensitive content to a different destination or change the protection policy.

::: {.details summary="Inherited: SMTP responsibility and retry behavior"}
RFC 5321 §§4.1.1.4 and 4.2.5 distinguish successful handoff from rejected data. After a final 4yz or 5yz rejection, the receiving SMTP server must not subsequently deliver that rejected transaction. After acceptance, later failures use the notification mechanism. Section 4.4 explains partial downstream failures.

Sections 4.5.3.2, 4.5.4 and 6.1 require appropriate per-command timing and delayed retry, and explain how final-reply loss can duplicate delivery. The application does not shorten the SMTP timeout to produce an instant-chat appearance. A pending message can remain visible locally while delivery continues.
:::

### Explicit no-service failures

A 521 greeting identifies a host that does not accept mail. A 556 response identifies the no-service destination associated with the rejected command. Preserve that scope: failure at one host does not by itself declare every alternate destination unusable. Neither code indicates that the user lacks encryption support.

The [no-mail-service audit](audits/no-mail-service.md) records the SMTP update and null-MX behavior. Do not transform a no-service result into an automatic key request, a new destination address or permission to downgrade encryption. Temporary DNS lookup failures remain distinct from explicit no-service evidence.

### Transaction-wide acceptance and later recipient failures

In ordinary SMTP, the final DATA reply applies to the transaction's accepted recipient set. It does not encode a separate success or failure for each recipient. The sender MUST NOT invent per-recipient outcomes from the wording of that reply. Preserve earlier RCPT results separately, and apply later delivery reports only to the recipients and submission they reliably identify.

A receiving server that has delivered to some accepted recipients but cannot deliver to others returns successful transaction acceptance and reports the later failures through the applicable notification mechanism. Conversely, after returning a final negative DATA reply, it must not subsequently deliver that transaction. An Email Next delivery record must distinguish this explicit rejection from loss of the final reply, where acceptance remains uncertain.

RSET, QUIT and connection closure do not recall an already accepted message. A retry of an uncertain submission retains the same contribution identity and immutable semantics so the receiver can suppress repeated interaction effects. A user editing or replacing the contribution creates the corresponding new contribution rather than disguising the edit as a transport retry.

## Duplicate and conflicting contributions

Transport does not provide exactly-once delivery. An upgraded receiver performs the following checks before changing interaction state:

1. Parse and validate the contribution under its advertised profile. Preserve the received source independently.
2. Establish the contribution's authenticated author/session context when protected, or explicitly record its unverified status when ordinary mail is permitted.
3. Compare the contribution identity within that context against previously processed contributions. An unauthenticated claimant must not reserve an identifier in another author's authenticated namespace.
4. If the identity and authenticated semantic content match, retain delivery evidence as needed but do not apply the interaction again.
5. If the same authenticated identity carries conflicting semantic content, retain both representations as a conflict and do not silently replace either one.
6. Commit the interaction effect and the record that it was processed atomically. After a crash, replay must not apply a committed effect again.

The wire/security profile must define the exact comparison representation and replay retention behavior. A display-only legacy heuristic must not serve as a cryptographic duplicate detector. A client that cannot establish the required identity or comparison data leaves the structured action inactive and exposes the readable message.

## Retry scope and negative results

Queue records MUST retain both the immutable contribution and its delivery envelope. Track retries by the relevant destination and submission; do not turn a message-specific rejection into a permanent assertion about a participant or domain. In particular, a permanent MAIL rejection MUST NOT be cached as a rejection of subsequent messages. A server's latest successful EHLO response replaces earlier capability advertisements for that session.

Recipient-buffer exhaustion uses 452. An explicit site-policy rejection is a different condition and can be permanent. The SMTP revision removes RFC 5321's historical advice to reinterpret recipient-limit 552 replies as 452. An implementation providing legacy compatibility must scope any such exception to identified legacy behavior, rather than treating every 552 as retryable or silently discarding its reported meaning.

Successful SMTP handoff records acceptance of transport responsibility, not proof that the recipient saw, decrypted or acted on the contribution. Missing failure notifications do not upgrade that evidence: filtering, exceptional silent disposal and notification-delivery failure can prevent a later report. The interface MUST NOT infer a read receipt from elapsed time or absence of a bounce.

## Security policy survives transport changes

A temporary failure, expired capability record, less capable MX host or changed route does not authorize weakening encryption. A required-encryption delivery waits or fails if the selected profile cannot be delivered. A permitted ordinary-mail or hosted-link fallback is a distinct prepared delivery under the sender's policy, with its actual exposure shown in the conversation.

A relay cannot perform an end-to-end encryption downgrade because it must not have the required plaintext or endpoint private keys. A provider acting as a hosted-message endpoint has a different trust role that the [security chapter](security.md) must disclose. Reconnecting to another transport does not change those roles.

## Framing and content preservation

Prepare protected content before submission with the selected security profile's canonicalization rules. SMTP CRLF framing, dot-stuffing, trace insertion and final-delivery Return-Path handling are transport operations; they are not a new signature-canonicalization algorithm.

The baseline MIME must remain safe for the negotiated transfer path. Raw binary data cannot be sent merely because the connection carries octets. If an extension is unavailable, use a permitted representation or report failure; never truncate protected or structured content to fit a limit. SMTP size limits, MIME encoding overhead and renderer resource limits are separately measured.

Original messages retained for local reconstruction must not be rewritten to remove quotation, repair trace history or make authentication appear valid. The reconstructed conversation is a derived view.

## Disposition receipt destinations

Do not apply delivery-failure routing rules to every notification. An MDN uses the original message's Disposition-Notification-To destination in both its header and envelope, with a null envelope sender. Return-Path is used for the automatic-send privacy comparison; it is not a replacement destination for the requested receipt.

An MDN request can be ignored. If its destination differs from Return-Path, Return-Path is absent, or multiple distinct destinations are requested, the client must obtain the confirmation required by RFC 8098 or send no MDN. A general Email Next capability or encryption preference does not itself authorize that privacy-sensitive disclosure. Never generate an MDN in response to another MDN.

[RFC 8098 §§2.1 and 3](https://www.rfc-editor.org/rfc/rfc8098.html) define these specific destination and consent rules. The SMTP revision's broad description of notifications going to the previous reverse-path must not erase them. Full MDN profile review remains part of the standards audit.

### Interpreting disposition reports

An MDN's `displayed` disposition reports display to someone accessing the mailbox; it does not prove reading, understanding, decryption of the intended protected representation or acceptance of an interaction. `processed` may describe automated handling without a human viewer. `dispatched` can mean printing or forwarding, and `deleted` does not prove that the message was never seen or cannot be recovered.

Preserve the reported action mode separately from the receipt's sending mode. A manually initiated action and an automatically sent receipt are compatible facts. Neither mode proves the identity of the person operating the mailbox. RFC 8098 also permits a manual/manual mode report to protect configuration privacy, so these fields are reported labels rather than forensic evidence of an actual click. Correlate the message and recipient and assess authentication before using a report; unknown correlation remains unresolved rather than being assigned to a likely conversation participant.

MDNs are not a stream of changing presence or interaction state. RFC 8098 limits issuance per recipient and message, with specific forwarding and multiple-client considerations. Email Next MUST NOT map `processed` to successful form submission or treat an MDN as an authenticated key-negotiation acknowledgment.

### Shared-mailbox receipt suppression

For an IMAP mailbox supporting permanent `$MDNSent`, follow RFC 3503's suppression rules. The keyword is case-insensitive. Its presence prevents another MDN even if other flags suggest otherwise; a draft also must not trigger an MDN. Verify permanent-keyword support and handle storage failure. Preserve the marker when copying messages and when storing sent messages, generated receipts or unfinished drafts as specified by that profile. Do not clear it to retry a receipt.

The marker can record a decision not to send. It MUST NOT be presented as evidence that a receipt was transmitted or received. Neither `\Recent` nor `\Answered` substitutes for it; `\Seen` is not proof of receipt delivery or human understanding.

RFC 3503 does not define an atomic claim-and-send operation across IMAP and SMTP. Two clients can observe the marker absent before either updates it, and a crash can separate a mailbox update from submission. An Email Next implementation claiming stronger cross-device suppression must specify its coordinating authority, durable operation identity, concurrency handling and crash recovery. The keyword alone is insufficient evidence of exactly-once behavior.

These requirements use [RFC 3503](https://www.rfc-editor.org/rfc/rfc3503.html) for shared suppression while retaining the current RFC 8098 disposition vocabulary; historical `denied` and `failed` values in RFC 3503's timeline must not be revived as current MDN types.

## Automatic messages and control traffic

A null reverse-path prevents notification loops in specified cases; it does not instruct legacy clients to hide a message. Ordinary discovery traffic cannot assume exemption from SMTP failure handling simply because it is machine generated. Exact automatic-response rules depend on the RFC 3834 audit and the selected discovery profile.

No key negotiation is initiated solely by receiving a bounce, disposition notification or unauthenticated request. Control processing needs authenticated scope, duplicate suppression and bounded response behavior. A receiver must not generate an endless acknowledgment exchange in response to control messages.

A provider's authenticated control-routing service can offer a separate handling path for participating accounts. Without such a negotiated service, the client must assume an ordinary email can appear in every legacy client accessing the mailbox. Existing spam-discard discretion is not a protocol for sender-requested invisibility.

## Required validation

| Case | Expected result |
| --- | --- |
| One recipient rejected, another accepted | Independent outcomes; no resend to the accepted recipient because another failed |
| Final DATA response lost | Uncertain state; retry may duplicate mail but not the interaction effect |
| Final DATA temporary rejection | Retryable state; no application success claimed |
| Final DATA permanent rejection | Failed state; no automatic identical repeat to the same server contrary to SMTP rules |
| Duplicate arrives after receiver crash | Previously committed interaction is not applied again |
| Forged duplicate uses another author's identifier | Does not suppress that author's authenticated contribution |
| Same authenticated identifier, different content | Conflict retained; no last-arrival overwrite |
| Backup MX lacks an extension | Protection policy persists; no automatic plaintext substitution |
| Gateway changes protected content | Authentication failure exposed; original retained |
| Bcc copies traverse one provider | No hidden-recipient disclosure through shared event or key metadata |

These cases are required evidence for an implementation. No deployment or test execution is claimed by this chapter.

## Internationalized transport capability

SMTPUTF8 is negotiated per peer and selected per transaction when required. It does not establish recipient support for interactive messages, authenticated keys or end-to-end encryption. Alternate MX hosts may differ; negotiate again on the new connection and retain the prepared delivery's confidentiality policy.

When a required internationalized address or header cannot be transported, record a transport compatibility failure. Do not remove encryption, guess an ASCII alias or silently rewrite protected content. A sender-authorized submission transformation requires an established alternative address and a valid representation preserving the intended contribution and policy.

Trace protocol names and UTF-8 reply permission describe transport behavior. Neither provides live presence or recipient-device capability evidence. See the [SMTPUTF8 audit](audits/smtputf8.md) for inherited commands, failure codes and non-exclusive basic-code associations.

For post-DATA internationalized-header rejection, the proposed receiver handles both `550 5.6.9` and `554 5.6.9` as permanent rejection. Preserve the original code in diagnostics. The proposed server emits `554 5.6.9`, following RFC6531 §3.5; the registration table’s non-exclusive association with `550` does not override that requirement. Neither response authorizes plaintext retransmission, and neither is evidence that a recipient device lacks encryption support.

## 8-bit transport is hop-scoped

A client sends an 8-bit MIME body only after the current SMTP peer advertises 8BITMIME, using the appropriate BODY parameter. That advertisement does not permit unencoded binary, remove line limits, establish SMTPUTF8 header support, or describe recipient software.

When the next hop lacks support, valid lossless 7-bit conversion is an option only where it preserves the selected protection contract. Prepare transport-safe encoding before signing; do not repair a signed object by re-encoding it in transit. If the object cannot be carried without violating protection, report failure under the delivery policy. The [8-bit MIME audit](audits/eight-bit-mime.md) records the inherited rules and rejected erratum.

## Size negotiation and unchanged meaning

Determine SMTP message size from the final encoded MIME bytes, including headers and CRLF, excluding the DATA terminator and extra dot-stuffing octets. Encryption, armor and base64 overhead count. An advertised SIZE of zero means no fixed maximum, while a bare SIZE keyword leaves the maximum unknown; neither promises unlimited available storage.

A successful MAIL response is not final acceptance. Preserve per-recipient temporary and permanent failures through DATA and retry handling. A size rejection MUST NOT silently trigger plaintext fallback, attachment removal or hosted upload. Any change of representation or disclosure follows the authorized delivery plan and preserves the contribution's meaning. See the [message-size audit](audits/message-size.md).

## Pipelined reply correlation

PIPELINING changes command scheduling, not recipient authorization or acceptance semantics. Correlate complete replies with issued commands by their order; do not match by repeated status codes or response text. A multiline response consumes one command's position. Preserve individual RCPT outcomes even when a later RCPT fails.

Send contribution data only after DATA acceptance and at least one accepted recipient. If a server accepts DATA despite rejecting every recipient, terminate the empty transfer and process its reply without disclosing the contribution. A later command's failure must not overwrite an earlier transaction's confirmed acceptance. See the [pipelining audit](audits/pipelining.md).

## TLS resets session capabilities

After a successful STARTTLS handshake, reset the SMTP session and obtain fresh EHLO capabilities before using SIZE, PIPELINING, 8BITMIME or authentication mechanisms. Do not retain pre-handshake advertisements as authority for the protected session. Independently authenticated identity records remain subject to their own continuity policy.

Track achieved transport protection separately from end-to-end message protection. A TLS connection is not evidence of recipient decryption or author signature. Required transport security cannot be downgraded merely because STARTTLS disappears or negotiation fails. The [STARTTLS audit](audits/starttls.md) records the base behavior; current certificate identity and TLS policy standards remain separate dependencies.

## Authenticate the discovered service

Keep the expected service identity and the authorization for endpoint delegation when discovering submission or account-access services. An unauthenticated redirect cannot make its target the trusted reference identity merely because the target presents a valid certificate. SNI selects a certificate; certificate and service-identity validation remain necessary.

Provider-service authentication does not establish a correspondent's device key or authorize replacing a pinned key. Apply the [identity lifecycle](identity-lifecycle.md) independently. The [mail service identity audit](audits/mail-service-identity.md) covers RFC 7817; the final certificate profile must reconcile its historical rules with current general TLS identity guidance. Relay-to-relay authentication uses its own transport policy.

## Refresh endpoints without changing account behavior

When refreshing submission or mailbox-access discovery, preserve required transport protection and authenticate the selected service before sending credentials. Refreshing a configured mailbox endpoint must not silently switch between IMAP and POP3 because domain preferences changed. Protocol migration requires an explicit user choice.

Distinguish a missing service record, a temporary lookup failure and an explicit unavailable-service target. None is evidence about correspondent encryption support. The [service discovery audit](audits/service-discovery.md) records the inherited behavior and pending updates.

## Connection confidentiality indications

For submission and account access, a confidential-connection indication requires at least TLS 1.2, successful certificate verification and satisfaction of the account's protection policy. A stronger configured minimum still applies. This is a connection indication; it must not imply end-to-end message protection.

Apply the [TLS version update](audits/tls-version-update.md) when inheriting RFC 8314. The complete TLS algorithm and certificate profile remains subject to the outstanding dependency audit.

## Apply account protection before service preference

Filter discovered submission and mailbox-access services against the account's minimum protection before applying endpoint priority. Prefer implicit TLS; correctly enforced STARTTLS remains compatible. Do not test credentials on a connection below the configured minimum. Before that minimum is met, limit protocol activity to capability discovery and the transport-security upgrade.

Do not consult unauthenticated SRV records afresh on every connection. Preserve the established configuration; periodic change detection and authenticated refresh follow the [submission/access TLS rules](audits/submission-access-tls.md). A failed certificate check on an existing account must not become a routine prompt to trust a replacement certificate.

A TLS client certificate requires authorization for that account before disclosure. Provider credentials and certificate exceptions must not be reused across accounts merely because they share a client installation. These transport requirements apply independently of the selected message-encryption fallback policy.

## Administrative reports and returned content

Recognizing a `multipart/report` object does not authenticate its claim. Reports may be nested or forwarded. Validate the report profile, correlation and recipient scope before applying any delivery-state effect; keep unauthenticated reports visibly distinct from established delivery evidence.

Returned original content is diagnostic material. Do not execute embedded interactions or insert it as a new authored contribution. A delivery report cannot establish decryption, reading or interaction acceptance. Preserve encrypted material when returning it; never decrypt it merely to construct a report. The [report-container audit](audits/report-container.md) records the structure and outstanding DSN dependencies.

## Tracking is scoped transport evidence

Keep transport tracking identifiers and secrets separate from application event identity and public conversation metadata. Tracking authority does not establish a recipient's encryption key, group membership, presence or reading. Missing or expired tracking records mean that tracking knowledge is unavailable; they do not prove delivery failure.

Do not propagate tracking authority automatically across mailing lists or multi-recipient expansion. The [message tracking audit](audits/message-tracking.md) records the existing limits and unresolved source inconsistencies. Email Next does not adopt its historical hash construction as a new security profile.

## Chunking and binary upgrades

CHUNKING and BINARYMIME are separate per-hop capabilities. CHUNKING permits BDAT framing; binary content additionally requires BINARYMIME and the appropriate BODY declaration. Count exact transmitted octets without DATA dot-stuffing or a DATA terminator. An intermediate chunk acknowledgement is not final message acceptance.

Do not mix DATA and BDAT in a transaction. After a failed chunk, stop new chunks and reset as specified by the transport protocol; already-pipelined chunks must be handled without interpreting their payload as commands. Preserve application identity across uncertain final acknowledgements.

Transport optimization must preserve the protected representation. A server upgrade does not authorize decoding and rewriting signed material, and a downstream downgrade does not authorize decryption. The [binary MIME audit](audits/binary-mime.md) records framing, conversion and failure requirements.

## Authentication failure diagnostics

Keep reported authentication failures separate from address validity and end-to-end identity state. A policy rejection must not automatically remove a recipient, revoke a key or authorize a plaintext retry. Distinguish no passing signature, passing-but-unacceptable signature, SPF fail and SPF evaluation error.

Preserve the temporary or permanent transport outcome. A multiple-failure diagnostic does not identify its component failures, and a generic diagnostic may conceal policy details. The [authentication-status audit](audits/authentication-status.md) records the existing assignments and their limits.

## Sender-selected relay protection

REQUIRETLS can request authenticated TLS on participating relay hops. Keep that transport requirement separate from end-to-end encryption and ordinary-copy permissions. Permission to send an ordinary copy MUST NOT implicitly authorize adding `TLS-Required: No`, which requests relaxing recipient transport policy. The MAIL REQUIRETLS parameter takes precedence over a conflicting No header.

Preserve required transport handling through queues and local alias redistribution. Do not infer that a user-side forward retained an envelope requirement it could not observe. Each newly originated contribution follows its own send plan.

The [required-relay TLS audit](audits/required-relay-tls.md) records bounce exceptions, metadata exposure and pending DANE interpretation. Do not claim that REQUIRETLS protects content from intermediate servers or guarantees equally protected delivery of every failure report.

## Status-code interpretation

Preserve the basic SMTP reply and any enhanced status detail as separate diagnostic fields. The registry's associated basic-code column is explicitly non-exclusive; follow a protocol's applicable reply requirement rather than treating that column as an exhaustive validation table. A conflicting meaning assigned to an enhanced code requires separate resolution.

An authentication privacy-layer diagnostic does not advertise endpoint encryption capability. A disabled submission account does not revoke a correspondent's key. Clients MUST NOT interpret transport diagnostics as authorization to change endpoint identity, group membership or required content protection. Unrecognized detail codes must not erase the basic delivery outcome.

The [enhanced-status registry audit](audits/status-registry.md) records registration requirements and the distinction between reply associations and code-meaning collisions.

## Submission completion and protected content

Submission servers can complete or modify a message under RFC 6409; relays do not inherit that general permission. Email Next senders MUST finish the protected contribution before applying its signature or encryption. Required address expansion, encoding selection and other changes to protected fields must occur before protection, or produce a newly authorized contribution. A provider signature added afterward does not repair an invalid endpoint signature or confer the endpoint's authority.

A submission server that cannot accept the protected contribution under its policy must return a failure rather than silently altering the protected content or removing its protection. Outer routing and trace fields remain subject to their transport contracts; they are not automatically authenticated author data. Submission acceptance and subsequent delivery remain separate states, including when a later failure report follows acceptance.

RFC 6409 permits provider-side signing or encryption, but that alone does not establish endpoint-to-endpoint confidentiality. The security description must identify whether the provider can read the content and which principal authorized each protection layer. The existing [submission specification](https://www.rfc-editor.org/rfc/rfc6409.html#section-8) explicitly warns that message modification can invalidate signatures.

Do not canonicalize every address through DNS aliases on the assumption that SMTP prohibits aliases. [Verified erratum 3995](https://www.rfc-editor.org/errata/eid3995) corrects that claim in RFC 6409 §8.7, while noting that its replacement wording needs care. Apply the actual SMTP address rules and specific authorized mappings; DNS equivalence is not endpoint-identity equivalence.

The [message submission audit](audits/submission.md) records inherited MSA behavior, the distinction between mandatory and optional actions, and required preservation tests.

## Submission authentication and claimed origin

SMTP AUTH authenticates a session to a server. Its optional MAIL FROM `AUTH` parameter carries a claimed original submitter within a trusted relay relationship; it is not an endpoint signature over message content. A successful login, an AUTH parameter or an ESMTPA/ESMTPSA trace label MUST NOT by itself validate an Email Next author, key transition or capability advertisement.

Preserve `AUTH=<>` as an unknown or insufficiently authenticated origin. In particular, do not substitute the relay's authenticated identity for that origin. Forwarding through a logged-in relay must not turn an unverified message into a verified contribution. A list expansion treated as a new SMTP submission likewise does not inherit the original endpoint's signing authority.

When a SASL security layer takes effect, rediscover SMTP capabilities after the required state reset. Do not use an earlier unauthenticated advertisement as current capability evidence. Required secure submission remains required when authentication fails; the base protocol's permission to continue without authentication does not override the sender's policy.

Temporary authentication failure is not evidence of a wrong password and must not trigger repeated credential prompts. A mechanism-policy failure can select another permitted mechanism, but must not lower the required channel protection. [RFC 4954](https://www.rfc-editor.org/rfc/rfc4954.html) defines these session and origin distinctions; its historical TLS and identity-matching details must be read with the newer mail-service security requirements.

The [SMTP authentication audit](audits/smtp-authentication.md) records session state, origin propagation, error handling and corrected examples.

## Recipient privacy in trace information

A receiving system's trace information can expose envelope recipients even when Bcc is absent from visible address fields. An Email Next provider MUST NOT place another recipient's address in a shared copy's Received FOR clause. If it generates that clause for a particular copy, it must identify the RCPT address responsible for delivery of that copy. Provider trace policy must also consider whether selectively omitting the clause reveals the existence of other recipients.

Clients must preserve trace information for diagnostics without treating it as authenticated endpoint evidence. Sharing diagnostic extracts can disclose addresses and routing details; the client should show the extract being shared and omit unrelated sensitive data where possible, retaining the original privately.

These are proposed privacy requirements informed by the current [emailcore applicability draft](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-as-30/). That draft remains under IESG evaluation and does not replace the published protocol baseline. Its recommendation against a FOR clause on a multiple-recipient copy is distinct from the stricter Email Next requirement against disclosing another recipient.

## Scope of server capability advertisements

An SMTP extension advertisement applies to the current connection with the advertising server. It MUST NOT by itself establish support at another relay, the destination mailbox, or any recipient device. In particular, an upgraded submission server does not establish that every participant can decrypt a contribution or process its interactive controls. Endpoint capability and key evidence must satisfy the separate discovery and identity requirements.

Clients MUST ignore an unknown, well-formed extension advertisement. If a malformed response prevents reliable interpretation of EHLO, terminate the session rather than guessing which capabilities were offered. A retry may select another permitted route; it must preserve the sender's protection policy. A protocol fallback to HELO is not authorization to remove a required extension or disclose protected content.

This draft does not allocate an Email Next EHLO keyword. Any future SMTP extension needs its own defined semantics and registration, including whether its guarantee is local or depends on subsequent hops. An experimental implementation must not advertise a placeholder as a registered interoperable extension.

The ongoing [SMTP revision](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-rfc5321bis-44/) describes extension discovery, registration and handling of unsupported downstream features in sections 2.2 and 3.2. Its general discussion of falling back to an unextended representation does not override Email Next's explicit disclosure policy.


## Internationalized reports

A client that interprets delivery or disposition reports must distinguish their global UTF-8 media types from legacy report types, including mixed legacy/global parts within one multipart/report. It decodes each part's transfer encoding before interpreting fields. It preserves recipient addresses without manufacturing ASCII aliases or treating escaped report addresses as evidence of delivery capability.

When this client generates a report returning an undeliverable SMTPUTF8 message through a return-path server without SMTPUTF8, it uses the specified seven-bit transfer encoding for the encapsulated message or headers. This does not authorize an otherwise impossible envelope delivery, disclosure of encrypted plaintext or a change to the sender's fallback policy.

A correlated report remains an observation about delivery or disposition. A matching Message-ID, recipient address or diagnostic does not authenticate the reporting party, establish endpoint key possession, or authorize key replacement, group membership changes or plaintext fallback. Invalid address syntax preserved in a diagnostic remains inert source evidence. Human-readable and localized diagnostics are untrusted text.

The [internationalized-report audit](audits/internationalized-reports.md) records unresolved unitext and diagnostic grammar discrepancies and the reconciliation with current MDN fields. Until those are resolved in an exact profile and tested, this draft does not claim a complete global-report parser or generator.


## Delivery receipts and envelope correlation

When presenting a delivery-status report, the client must preserve the reported action and the scope of its evidence. In RFC3461, local delivery means availability to the mailbox access service, before a client retrieves the message. Delivery to a mailing-list address can mean availability to the list processor, even when that processor subsequently refuses distribution. A report of relay into an environment without equivalent notification support does not establish final delivery. None of these observations establishes endpoint decryption, human reading or acceptance of a structured action.

The client records an ENVID, when used, as envelope-correlation data associated with the submitted delivery. It does not substitute ENVID for contribution identity, Message-ID, a recipient identity or a cryptographic authenticator. Relays carrying the DSN extension preserve supplied envelope identifiers; a relay must not invent one when none was received. An ORCPT value identifies the original recipient for reporting and can differ from the current forwarding destination. A supplied ORCPT must not be case-normalized or rewritten during conforming relay. Its address-type label alone does not establish valid mailbox syntax or identity ownership.

A request for DELAY notifications permits delay reports; it does not guarantee one. Omission of a NOTIFY parameter is not equivalent to NEVER. Neither absence of a report nor a request to suppress reports proves success. NOTIFY=NEVER suppresses delivery notifications; it does not tell legacy clients to hide or discard the delivered message and must not be used as a capability for invisible key exchange.

Report-generation requests do not override encryption or disclosure policy. RET controls requested returned content, and a foreign gateway may not preserve that request. The client must therefore protect the originally submitted representation itself rather than relying on RET=HDRS to keep plaintext confidential. No DSN may be generated to a null reverse-path by finding an alternative sender address in message headers.

The [complete RFC3461 base-document audit](audits/dsn-extension.md) records the source requirements, all eight errata and unresolved command-length and example discrepancies. Current dependency closure and implementation validation remain open.


## Forwarding and mailing-list report boundaries

An alias and a mailing list do not have identical reporting semantics. List redistribution starts a new envelope/reporting context; it must not derive ENVID, NOTIFY, RET or ORCPT from the original delivery's parameters. Delivery to the list processor is not evidence of delivery to every subscriber. Alias expansion can produce relay or expansion reports, or propagate requests to a selected target. A client must not infer the actual recipient set or confirmed group membership from any of these outcomes.

Private forwarding can use a separate return path and reporting context to keep downstream failures from exposing the private address to the original sender. An Email Next client must not promote addresses discovered in diagnostics into shared participant lists, key-discovery targets or automatic reply destinations. Sharing a diagnostic with a conversation requires the same recipient-disclosure controls as sharing other message content.

A combined report does not justify showing unrelated recipient results. The client associates each reported outcome only with its corresponding submitted delivery and recipient observation. Storage in a dead-letter or postmaster mailbox remains a delivery failure for the intended recipient; it is not a successful alternate recipient delivery.


## Reported action and error cause

A delivery report's Action and Status describe different facts. The client must preserve both. `delayed` means that the reporting MTA intends to keep trying; `failed` means that it has abandoned that delivery. A status beginning with `4` can accompany either action. It describes a temporary cause and does not promise that retries continue. The client must not turn a terminal failed report into a pending delivery solely because its status begins with `4`.

`expanded` indicates forwarding beyond a multi-recipient alias and can precede further delayed or failed reports. It is not a terminal confirmation for every downstream address. `delivered` remains scoped to the reported recipient address, including a list processor. `relayed` remains evidence of handoff into an environment without equivalent success reporting.

A report can describe multiple recipients of one message, and multiple reports can concern the same submission. Each per-recipient field block is interpreted separately. The reporting MTA, remote MTA and translating DSN gateway are distinct roles; a gateway's presence must not cause the client to attribute the underlying delivery attempt to that gateway. Reported names and times remain claims from the report, not authenticated identity or causal ordering evidence.

An optional Last-Attempt-Date is the reported attempt time, not the outer message's Date. A Will-Retry-Until value is an expectation associated with a delayed action, not a guaranteed delivery deadline. Missing dates must not be fabricated from the report's arrival time. Conflicting or malformed reports remain inspectable observations and cannot authorize an automatic resend, group change or protection downgrade.


## Failure is not proof of nonreceipt

Even an authentic failed delivery report does not establish that no copy reached the recipient. A connection can fail after a receiving server accepts the content but before the sender receives the final acknowledgment. Subsequent attempts can have different outcomes. The client must retain this uncertainty instead of letting a later failure erase evidence of an earlier accepted or uncertain attempt.

A failure report must not trigger automatic creation of a new contribution or repetition of an external action. An authorized retry retains the contribution identity and follows the prepared delivery's retry and protection policy. A button answer or other structured action remains subject to its deduplication contract even when delivery reports disagree.

The [report-format audit](audits/dsn-format.md) records the source basis and remaining parser work. Delivery failures alone do not revoke keys, prove address reassignment or authorize authenticated group-member removal.


## Unknown and security-related status details

For a syntactically valid enhanced status code, the client preserves the received code and reports the recognized class even when it does not recognize the subject. If the subject is recognized but the detail is unknown, it presents that subject without inventing a more specific explanation. Invalid syntax remains an unparsed diagnostic rather than being repaired into a success code.

Diagnostic interpretation does not change the scope of delivery evidence. A positive transport class with an integrity-related warning must not produce an end-to-end integrity badge. Unsupported media, conversion requirements, unavailable keys or unsupported algorithms do not authorize removing protection, altering the authenticated content or changing the recipient identity. The client applies its delivery policy separately.

These application decisions use the [enhanced status-code audit](audits/enhanced-status.md). They supplement, rather than replace, the separate interpretation of a DSN Action and the authoritative SMTP transaction result.


## Tracking does not reveal the participant set

An optional message-tracking result must be interpreted under its own protocol. Its `transferred` action means handoff to a tracking-capable agent, not final delivery or endpoint capability. Its `opaque` action deliberately does not establish whether the system saw the message. The client must not translate that result into “not delivered,” “offline,” or “does not support encryption.”

Tracking must not traverse mailing-list expansion or expose the list's contents. A relayed, expanded or delivered tracking result is not permission to discover downstream identities. Any further query requires the tracking protocol's authorization and continuation rules; a remote hostname in diagnostic text alone is not permission to contact it or disclose a tracking credential.

[RFC 3886](https://www.rfc-editor.org/rfc/rfc3886.html) defines a separate message/tracking-status response format. Its mandatory fields and action values differ from ordinary DSNs. A parser must dispatch by the actual media type rather than treating the two formats as interchangeable. This draft does not yet specify a tracking-query implementation.


## Submission from stored content

A provider may offer BURL as a submission optimization. It is not a recipient capability or an end-to-end security mechanism. Before using it for a protected delivery, the client must establish that the referenced content is the intended prepared representation and that submission will preserve the bytes covered by its security profile. General permission to perform MIME or character-set conversion is not permission to rewrite protected content.

A BURL URL can carry an access credential. The client and submission service must protect that credential and the fetched content on every applicable connection. The URL must not enter a shared conversation, diagnostic export or automatic reply merely because it appeared in a submission transcript. Fetch authorization does not confer identity-transition, history-sharing or device-enrollment authority.

The client distinguishes an intermediate BURL response from successful completion of the LAST command. Intermediate success need not mean durable storage. A failed fetch fails the transaction; an uncertain final response follows the same duplicate-safe retry policy as other submissions. A retry must not silently fetch different content from a changed reference.

The service must validate the authenticated submitter's fetch authority and restrict credential use to its configured trust scope. No accepted recipient means no URL fetch. A user-controlled URL must not cause submission credentials to be offered to an arbitrary server. Resource bounds and exact reference-stability checks remain required implementation work.

RFC4468's verified errata895 and896 correct the trust-relationship status to X.7.14 and its example to 554 5.7.14. These diagnostics do not authorize creating a trust relationship automatically. The complete URLAUTH and IMAP dependency reviews remain outstanding.


### Default header confidentiality for protected legacy mail

When composing signed-and-encrypted S/MIME mail using RFC9788 header protection, the default policy is `hcp_baseline`: replace the outer Subject value with `[...]`, omit outer Comments and Keywords fields, and preserve other non-structural fields unless the reply's inherited confidentiality rules require further protection. Preserve the actual values inside the protected payload and record every deliberately exposed non-structural field there using HP-Outer. The policy name is not a wire parameter.

This default MUST NOT require the user to select a header policy. An implementation may expose an advanced policy setting, but its default must protect the subject. Stronger removal of address or threading metadata requires an explicitly specified delivery profile and interoperability evidence; recipient support for rich interactions alone does not establish that the transport will deliver such messages.

Before applying this policy, construct the intended headers separately for each permitted audience. Omit Bcc from the common protected payload. Encrypting a Bcc field does not hide it from the other recipients of that payload, and the baseline policy does not remove a Bcc field supplied to it. Recipient isolation must also cover cryptographic recipient identifiers and provider trace fields, as required above.

These composition choices follow [RFC9788 Sections 3 and 11.4](https://www.rfc-editor.org/rfc/rfc9788.html#section-3). They define the legacy S/MIME path; an MLS MIME binding must specify its own encapsulation explicitly rather than claim that RFC9788 defines it.


## Sieve variables and control routing

Recipient-authorized filtering MAY use Sieve variables for sorting. A capture from a message header MUST NOT be treated as authenticated capability or identity evidence merely because a filter matched it. Implementations MUST NOT use potentially truncated Sieve variable values as substitutes for original security-bearing octets. Authenticate the original material through the security profile before assigning trusted control semantics.

RFC5229 variable assignment does not cancel implicit keep, and its default script-local state is not durable replay protection. Advertising the Sieve variables extension MUST NOT be interpreted as support for invisible control delivery or Email Next endpoint capabilities. See the [Sieve variables audit](audits/sieve-variables.md).


## Stable mailbox routing and fallback

An implementation MAY use RFC9042 mailbox IDs for recipient-authorized storage routing. It MUST NOT treat a mailbox ID as an Email Next endpoint identity or proof that legacy clients cannot display the stored message. A missing ID can trigger positional-name fallback under RFC9042; a preceding mailboxidexists test is not a reservation or delivery guarantee.

A negotiated control service that promises separate handling MUST define and enforce its storage-failure behavior independently of Sieve's normal fallback. It MUST NOT report successful hidden handling merely because delivery to a different ordinary mailbox succeeded. Permission changes, missing mailboxes and quota failures must reach the service's failure path. Creating a replacement mailbox MUST retain server-assigned ID semantics; the client cannot demand reuse of a lost ID. See the [mailbox identity audit](audits/sieve-mailboxid.md).


## IMAP-triggered filtering

An IMAP APPEND, COPY or flag change MUST NOT by itself authorize a new Email Next contribution, key change, read receipt or repeated external effect. Provider integrations MUST preserve event deduplication across copies and repeated script invocations, including concurrent execution. The IMAP user performing a storage action is not necessarily the author of the stored message.

An implementation MUST NOT claim invisible control delivery on the basis of IMAP-event discard: RFC6785 first stores appended or copied messages and then marks them deleted; expunge is optional. Advertising IMAPSIEVE does not establish that a particular mailbox has an active script.

Clients protecting drafts from the provider MUST encrypt before remote storage. They MUST NOT rely on a Draft flag, later deletion or an assumed absence of filtering to keep remotely stored plaintext private: IMAP-event scripts can redirect it on a flag change. A provider performing content-transforming redirects or fileinto actions MUST preserve the distinction between the original authenticated contribution and a newly produced message. See the [IMAP-event audit](audits/sieve-imap-events.md).


## POP capability and retention boundaries

A POP adapter MUST interpret CAPA as capabilities of the connected server in the applicable protocol state. It MUST NOT infer recipient encryption, device availability or rich rendering from CAPA, UIDL or IMPLEMENTATION. It MUST NOT treat retrieval errors such as LOGIN-DELAY or IN-USE as permission to weaken a conversation's delivery policy.

An adapter MUST account for EXPIRE policy when preserving downloaded messages. Where session completion may delete retrieved mail, the client MUST durably retain the complete downloaded bytes and recovery state before completing that session. A TOP preview MUST NOT satisfy whole-message authentication. EXPIRE MUST NOT be displayed as an exact expiry time for an individual event. This draft adds no POP command or capability. See the [POP capability audit](audits/pop-capabilities.md).


## POP deletion and replay recovery

A POP adapter MUST keep session message numbers and maildrop-scoped UIDLs separate from authenticated event identities. Identical mail copies can share a UIDL; message-number changes do not create new events. Transport retrieval bookkeeping MUST NOT substitute for the event journal or authorize an effect to run again.

Before a session can remove its only server copy, retain the complete retrieved bytes and recovery state durably. A failed or unanswered transaction QUIT MUST be treated as an uncertain deletion outcome; the next session may contain some, all or none of the previously marked messages. Retry retrieval and event processing without duplicate effects. RSET clears current server deletion marks but does not undo committed application actions.

Remove POP dot stuffing before MIME processing. Preserve the retrieved message representation separately from display line-ending normalization. LIST sizes do not include stuffing octets and do not authenticate content. See the [POP3 base audit](audits/pop-base.md).

### POP framing evidence

The [POP framing experiment](evidence/README.md#pop-retrieval-framing) removes multiline dot stuffing, requires the terminating line, retains subsequent pipelined response bytes and returns no partial message after an incomplete response or limit failure. Its integration fixture carries a generated attachment package through retrieval decoding and preserves exact structured-event and resource bytes. It does not implement POP session state, authentication, durable receipt or deletion recovery; those remain separate required adapter work.


## TLS reporting boundary

SMTP TLS reports are operational diagnostics. Their TLS-failure delivery exceptions MUST NOT be applied to Email Next conversation content, device credentials, identity-state changes, recovery secrets or hosted-access credentials. A reporting destination is not a capability-discovery service or an endpoint-authority source.

Report success MUST NOT establish recipient decryption, endpoint encryption, message display or interaction consent. Missing reports MUST NOT authorize an encryption downgrade. Treat report text, links, filenames and compressed objects as untrusted diagnostic input; report ingestion must not execute content, automatically navigate supplied links or write sender-selected paths. See the [TLS reporting audit](audits/tls-reporting.md) for inherited requirements and unresolved source discrepancies.


## MLS transport experiment

The [MIME round-trip experiment](evidence/README.md#mls-bytes-through-mime) carries actual serialized MLS admission and encrypted-message objects through ordinary base64 attachment encoding before cryptographic processing. The experiment also traverses a bounded loopback SMTP transaction, supplying local network-framing and byte-preservation evidence. The versioned invitation, contribution and group-control experiments define their own bounded MIME shapes. Quorum carrier1 uses a readable text part and an application/json attachment containing the exact encrypted Commit and public certificate evidence. These experiments do not establish real-provider delivery or independent-client interoperability. They do not claim to implement an application binding of the registered message/mls type, and no media type makes a control message invisible to legacy clients.


## Provider transport policy and endpoint protection

> [!ex] A secure route to an older mailbox
> Alice's provider can require an authenticated encrypted connection to Bob's provider even if Bob uses an older email client. That improves the delivery route; it does not give Bob a compatible endpoint key or prevent either provider from reading an ordinary plaintext contribution.

MTA-STS and DANE belong to provider-to-provider transport policy. Keep their results separate from the contribution's authenticated author, audience and endpoint-encryption state. Successful MTA-STS validation MUST NOT override failing DANE validation. A transport-policy failure also does not authorize changing the contribution to plaintext or hosted access.

MTA-STS policy identifiers are change tokens, not ordered revisions. A missing usable DNS advertisement does not by itself erase a cached policy. Its policy parser also has its own extension and duplicate-field rules; the event JSON parser's stricter rules must not be substituted for them.

::: {.details summary="Inherited MTA-STS discovery, enforcement and rollout behavior"}

### Fetching and selecting a policy

A sending MTA fetches the policy from the fixed HTTPS endpoint with a certificate valid for the policy host. It accepts only HTTP 200, does not follow redirects and does not use HTTP caching for this fetch. Its MTA-STS policy cache is a separate mechanism. When discovery or fetching fails, a valid unexpired cached policy still applies. With no such cached policy, failure to fetch a policy does not establish MTA-STS enforcement. This first-contact limitation MUST NOT be presented as authenticated recipient-key discovery.

For a configured smart host, the policy domain is that relay's domain. A mailbox at a subdomain does not inherit its parent domain's MTA-STS policy. Delegating policy hosting does not change the certificate name that the original policy endpoint must authenticate.

### Applying a policy

Enforcement checks both the permitted MX hostname and the receiving server's STARTTLS support and certificate. An MX wildcard matches exactly one leftmost label: `*.example.com` matches `mail.example.com`, but neither `example.com` nor `a.mail.example.com`. A testing policy may report failures while allowing delivery; it MUST NOT be shown as enforced transport protection.

An enforcing sender must not deliver to a candidate that fails validation. It preserves ordinary MX traversal, treating an invalid candidate as unreachable rather than prefiltering the list in a way that changes loop prevention. Before permanently failing delivery under an enforcing policy, it checks for a policy update; transient failure and retry remain the recommended handling. None of these outcomes changes the conversation's authorized plaintext, hosted-access or endpoint-encrypted delivery choice.

### Limits of the protection

An attacker can suppress initial policy discovery, or prevent refresh until a cached policy expires. Proactive refresh and operational alerts reduce this exposure; they do not make MTA-STS a first-contact endpoint-authentication mechanism. A valid fraudulent certificate can also defeat its authentication assumptions.

Providers must consider which hosts a wildcard authorizes. A policy permitting `*.example.com` can accept a tenant-controlled host with a valid certificate for its name. Policy hosting and DNS signaling also need protection from untrusted tenant registration. Neither shared domain ownership nor a valid relay certificate establishes an Email Next account identity.

### Changing or removing a policy

Providers publish the new HTTPS body before changing the DNS update token and keep old policies usable while DNS updates propagate. Removing the DNS record is not immediate opt-out: providers first publish an authenticated `none` policy and wait for all previously served policies to expire before removing discovery and policy endpoints. An older policy can outlive the immediately preceding one if it had a longer lifetime.

These requirements come from [RFC8461 §§3.3–8.4](https://www.rfc-editor.org/rfc/rfc8461.html#section-3.3). Its suggested timeout, size, retry and refresh intervals are source recommendations, not newly fixed Email Next defaults. See the [MTA-STS audit](audits/mta-sts.md) for source interpretation and dependency status.

:::

## DANE discovery and delivery outcomes

> [!ex] A lookup fails while Alice's message is queued
> Alice's provider cannot retrieve Bob's relay's TLSA records. That failure is not evidence that Bob's provider has no transport-security policy. The sender can try another eligible relay or keep the message queued; it cannot treat the failed lookup as permission to bypass DANE.

A DANE-capable sender MUST distinguish the following results for a relay selected under the applicable DNS discovery rules:

| Discovery result | Relay delivery behavior |
| --- | --- |
| Secure TLSA records, with at least one usable record | Require encrypted, DANE-authenticated TLS |
| Secure, nonempty TLSA records, all unusable | Require TLS; do not claim DANE authentication |
| Insecure records or authenticated absence | Apply other configured transport policy; opportunistic DANE alone does not require authentication |
| Lookup error, bogus result or indeterminate result | Treat the candidate as unreachable; try another eligible candidate or delay delivery |

These are relay decisions. They MUST NOT change a contribution's authorized audience or encryption/fallback choice. In particular, a relay policy permitting an unencrypted SMTP connection does not authorize decrypting an endpoint-encrypted contribution. A configured requirement for DANE-authenticated delivery is stricter than opportunistic DANE and must not use the unauthenticated cases as a successful outcome.

::: {.details summary="Inherited DNS discovery and relay selection rules"}

A sender must use a security-aware resolver. Trust in an upstream resolver's validation requires a trusted resolver reached through a secure channel. A response indicating no records is distinct from an error that prevents determining whether records exist. Alias expansion must preserve validation status: an insecure link cannot become a secure discovery chain merely because later records validate.

Preserve ordinary MX preference and loop-prevention rules. A worse-preference MX with TLSA records must not preempt a better-preference MX merely because it offers stronger transport authentication. Authentication of a relay reached through insecure MX discovery MUST NOT be represented as authenticated delivery to the intended destination domain.

TLSA discovery uses the actual service port and the base domains selected by the address and alias-resolution algorithm. A TLSA record's own CNAME indirection does not change that selected base domain. Intermediate aliases are not additional candidate base domains. Shared end-entity certificate associations can permit substitution between services sharing that certificate; they do not establish that those services are interchangeable conversation endpoints.

A provider that explicitly disables DANE enforcement or uses an audit-only mode MUST distinguish that outcome from DANE-authenticated delivery in its status and logs. Such an operational exception MUST NOT change the conversation's endpoint-protection policy. A receiver publishing TLSA records must offer STARTTLS without requiring an initial plaintext delivery attempt to establish sender reputation.

The discovery algorithm and its ordering are defined in [RFC7672 §2](https://www.rfc-editor.org/rfc/rfc7672.html#section-2). These rules do not define recipient device-key discovery.


### Certificate authentication and key changes

DANE-EE authenticates the server's leaf certificate or public key through the secure TLSA association. Under RFC7672, certificate-name checks are prohibited for that usage and certificate expiry is ignored; the DNSSEC association supplies the binding and its validity. DANE-TA instead validates through the associated trust anchor and requires the applicable server-name checks. A provider adapter MUST preserve this distinction rather than apply a generic Web PKI validation result to every TLSA usage.

The sender MUST NOT deliver through a relay when a usable secure TLSA association fails to authenticate it. Neither a matching relay key nor a successfully validated trust anchor is an Email Next account credential.

Before a planned relay-key change, publish associations for both the old and new keys and allow the previous DNS records and signatures to expire from caches before activating the new key. Removing an association is not immediate revocation at every sender. Relay-key rotation MUST NOT be interpreted as a change to a correspondent's endpoint identity.

These rules follow [RFC7672 §§3–4](https://www.rfc-editor.org/rfc/rfc7672.html#section-3). Its relay-discovery profile does not define client-to-submission-server discovery or authentication.

:::

## Mailbox records and conversation identity

Mailbox record identifiers, folders and provider-generated threads are storage views. They do not identify authors, establish conversation membership or authorize a repeated action. A copied message can have a new provider identifier while remaining the same authenticated contribution.

The [mailbox integration chapter](mailbox-integration.md) specifies account scoping, synchronization, original-byte preservation, permissions and submission behavior for JMAP adapters. Clients using other access protocols retain the same separation between mailbox state and conversation authority.
