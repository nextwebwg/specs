---
title: Freshness, clocks and revocation knowledge
order: 10.14
blurb: asynchronous default · recent account assertions · live device evidence · queued sends
sectionNav: true
---

# Freshness, clocks and revocation knowledge

Routine Email/2 delivery can use accepted setup while the recipient is offline. The sender checks that its evidence is still valid and that no known revocation or conflict prevents the send. A stricter local policy can require a recent account assertion or a fresh response from each device selected for an actual delivery. Other intended recipients can remain pending while eligible deliveries proceed.

These checks answer different questions. A valid encryption key can belong to an identity whose ownership has never been independently verified. A device can answer a fresh challenge while a provider withholds a newer revocation. Neither a directory lookup nor a successful handshake proves that every remote change has been disclosed.

> [!ex] A fresh response cannot undo a known removal
> Alice has accepted the state removing Bob's old laptop. The laptop answers a new challenge with its old key. Alice still excludes it: the fresh signature does not restore its authority.
>
> If Alice has not learned of that removal, the result depends on the information available locally. Email/2 does not promise instantaneous global revocation.

## Select the requirement explicitly

**Cached continuity** is the default for asynchronous sending. Stronger policies are separate choices recorded with the account, conversation or send intent. No failure, timeout or missing feature can lower the selected requirement. A current permitted policy change can affect new work, but must pass the normal send-plan reevaluation; it cannot rewrite an uncertain earlier submission.

| Mode | Required additional evidence | Permitted claim |
| --- | --- | --- |
| Cached continuity | None beyond current accepted identity, selected valid assertion and operation dependencies | Uses the accepted identity information available locally |
| Recent checkpoint | The exact locally accepted current identity-state record, with a declared issuance time inside an explicitly selected maximum age | The accepted account state declares a recent issuance time |
| Live confirmation | A valid device response to the exact locally outstanding challenge, within its original lifetime and an explicitly selected maximum age | This device answered this challenge within its bounded attempt |

Recent checkpoint uses the existing signed identity-state format, including ordinary authorized transitions or unchanged-roster continuity checkpoints. It adds no provider timestamp or unsigned directory record. Its issuance time is claimed by the authorized signer: it is not independent proof of when signing occurred, a live response, or absence of a withheld successor. A previously produced future-dated state could become eligible later. A policy needing evidence caused by a new challenge must select live confirmation.

Live confirmation requires a device signature. A provider's authenticated HTTP response, live source-account inspection, relay activation or setup `ready` state authenticates its own service fact; none substitutes for the recipient device response. An offline bootstrap publication may supply valid asynchronous admission material but cannot satisfy live confirmation.

## Apply the requirement to the selected devices

Evaluate every remote receiving endpoint selected for the actual delivery, including a paired device on another machine. Intended recipients still awaiting setup are not treated as having passed this check; their later deliveries need their own eligible evidence. The result names its exact principal, device, key, binding, accepted head and original assertion. One device's response cannot refresh another device or an account-wide roster. Locally originating devices still need their own current authority checks. Membership, administrators, ordering witnesses, verification and historical access retain their independent rules.

Every mode first requires the selected identity chain, applicable independent-verification policy, current role and binding, the selected signed assertion/application support (assertion10 for the current baseline, with assertion9/assertion8 only under their exact earlier agreements), full validity intervals, mailbox association and known-conflict/revocation checks. A freshness result alone cannot admit a package, install a group, authorize a route or release content. Learning a newer accepted state invalidates the previous freshness decision, which must be recomputed; still-valid selected assertion evidence can retain its original anchor under the [purpose-specific continuity rules](provider-grants.md#continuity-and-freshness-have-different-scopes). Recent-checkpoint mode uses the current head, while live target responses retain their exact-head requirement; a known authorized conflict holds affected work. Missing or invalid unsolicited claims cannot replace an accepted head or create an authorized fork.

::: {.details summary="Exact age checks and live-attempt binding"}

### Policy and credible time

Retain the exact local policy revision, mode and selected maximum age. Maximum age is an explicit positive unsigned-64 number of seconds for recent checkpoint or live confirmation; there is no implicit value inferred from a receipt or cache. Cached continuity has no additional age window and still obeys every signed validity interval. A deployment may impose an explicit maximum clock-uncertainty width; it cannot silently treat an uncertain estimate as an exact instant. These are local policy inputs, not peer-supplied fields or new wire records.

Let the credible current interval be `[earliest, latest]`. Require ordered unsigned-64 bounds and the entire interval within every applicable binding, assertion, challenge, response, grant and admission lifetime. Unknown/unreliable time leaves the check held. Future, crossing and expired intervals cannot be repaired using Message Date, HTTP Date, sender timestamps or an implicit grace period. Use checked arithmetic or subtraction comparisons without wraparound.

### Recent checkpoint

Resolve the exact current accepted head and its original signed identity-state bytes. Its proofs and signer authority must already have passed the full identity transition rules. Recheck current conflict and target-device authority in the same local authorization boundary. Require `issuedAt <= earliest` and `latest - issuedAt <= maximumAge`. Arrival, retrieval, database reopen and backup import do not change issuedAt. A different historical record, even with a more convenient timestamp, cannot substitute for the current head. A higher revision without an accepted proof chain is insufficient.

### Live confirmation

For the current opaque carrier, use exact [provider control3](provider-control.md#obtain-complete-mail-receiving-evidence), a fresh [bootstrap3 response](bootstrap.md#first-message-setup-with-carrier-support), or the [mailbox setup3 response](mailbox-setup.md#set-up-the-opaque-application-carrier). Each carries the complete original receiving-bundle0, including assertion10 and signed carrier support. Apply all owning account, signature, purpose, target, authorization and identity checks.

Retained version2 exchanges keep their original assertion10 evidence and earlier carriage scope; version1/assertion9 and version0/assertion8 exchanges retain their own contracts. An older decoder or response cannot satisfy a current3 attempt.

Before emitting a challenge, durably retain its original signed bytes and signature, nonce, exact protocol and applicable service/grant or mailbox-carrier scope, selected own account/device, intended mailbox and known target when available, local policy revision, operation identity and credible creation interval `[startEarliest, startLatest]`. A first-contact target can be bound after independent association selection; it must match the returned signed evidence and exact intended mailbox. Operation identity is a local random intent identifier, not a human-message content hash. The setup traffic stays content-free.

The challenge has its protocol's original fixed deadline. For use, require the same local operation/policy/account and original outstanding request, exact response request hash/digest, nonce, participants, service and scope, current authorized device signature, exact current target head/binding and original assertion/challenge correlation with all original intervals. The source preparation may retain unchanged-binding ancestry, without changing its signed bytes or creation interval. Bootstrap publications and another operation's response do not qualify. Require `latest - startEarliest <= maximumAge`; a smaller signed/protocol lifetime still applies. If a known clock movement or restore makes that local creation interval unreliable, hold and retire the attempt. Starting a newly authorized attempt needs a fresh identifier/nonce and cannot refresh the old one.

Exact retry, reopening storage and delayed response retrieval retain the creation interval. Cancellation is terminal for future use of that attempt. A cancelled/expired result remains historical evidence; it cannot become a new live permission. Account/policy/device changes require reevaluation, not clearing terminal state. The known-pair exchange cannot answer for a requested old state after the target has advanced; obtain independently valid identity evidence and authorize a new exact challenge instead.

:::

## Live confirmation through existing mailboxes

An enabled compatible device can answer a setup request through ordinary email and supply fresh device evidence without a provider control service. This proves that the signing device answered that request within its bounded attempt. It does not prove human presence, independent mailbox ownership or knowledge of every later revocation.

Use the existing mailbox setup exchange, not a second probe or an acknowledgment of the response. All automatic-response policy, direct-delivery authentication, abuse limits, confidentiality, receiving-key custody and no-loop rules remain required. Slow delivery may leave a strict freshness requirement waiting; it never permits a weaker send. Required address masking still applies: if the ordinary mailbox carrier cannot meet it, use an independently permitted setup path or wait.

::: {.details summary="Exact mailbox-response qualification and retained attempt"}

For the current opaque carrier, select mailbox-setup-v3, its complete original receiving-bundle0, response signature and narrowly selected sealed3 response.

Retained mailbox-setup-v2 keeps its original assertion10/sealed2 binding; version1/assertion9/sealed1 and version0/assertion8/sealed0 retain their own bindings. Select the exact profile before creating the attempt; no mixed parser or fallback is permitted. These are the existing setup formats, not additional freshness records.

Before the request leaves, durably bind its exact signed bytes, original request/nonce/digest, selected source and target mailboxes, own account/principal/device, required agreement, local send-intent revision, freshness policy/maximum age, credible creation interval and original deadline to that attempt. Retain the dedicated response-decryption key under its existing immutable receiving promise. A response cannot supply these local facts or create its own pending attempt.

After full carrier/sealed-response validation, independently validate the response wrapper, its exact selected commitment and device authority.

Current3 commits the complete original receiving-bundle0; validate its advertisement and signed carrier support under the owning setup3 rules. Retained profiles keep their original advertisement commitments. Do not extract an advertisement from a current3 bundle and treat it as the complete setup proof.

Match the original request, requestDigest, nonce, source/target, agreement and actual responder across the response, advertisement and sealed intent. Resolve the intended principal/device under the current association/verification policy; first-contact ambiguity remains a hold. The response advertisement must name the exact currently accepted target head and binding for live use, not merely an older still-authorized cached anchor. A known target-head change invalidates that live result; an eligible cached assertion can remain cached evidence only.

Require the entire credible current interval inside every original request, response, assertion, binding and owning key lifetime. Retain the original local creation interval and apply the same maximum-age and backward-clock checks as other live attempts. Neither mail receipt time nor Message Date resets the age. Exact duplicate responses and retries retain the same attempt and result. Cancellation, expiry, unreliable restored timing or changed account/policy/intent dependencies cannot reactivate it. A new permitted attempt has fresh request identity/nonce/key and its own finite retry policy; it does not erase old uncertain submission or retirement obligations.

Qualify each remote device selected for that delivery separately. One mailbox response cannot prove freshness of another device sharing the address. Devices that did not respond remain unavailable under live policy. A response for a completed setup may be retained as evidence for that exact send while its original live window and dependencies remain valid; it cannot become an account-wide reusable freshness token or authorize another send intent. Finishing acquisition may retire its temporary key without changing the retained response bytes; use still needs the original independently validated evidence and current authority.

The mailbox response's admission package retains its single-use rules. Checking fresh evidence does not itself consume that package, create a group or require an established conversation to replace its keys. If an existing context lacks eligible fresh evidence, hold it or perform separately authorized setup for this actual send; do not turn ordinary reading into presence polling. Final preparation/release repeats the normal current authority and freshness checks. A fully validated fresh response is neither an MLS acknowledgment nor a content-release permission.

:::

## Freshness does not repair a restored authority store

A new challenge, recent directory response or current wall clock cannot by itself prove that the client's own identity, allocation, ratchet, vote or action history survived restoration. A response from a removed device can still verify against an old snapshot that forgot the removal. Apply the [recovery hold and fresh-enrollment rules](identity-lifecycle.md#a-restored-device-is-not-an-ordinary-restart) before using restored operational state. Freshness policies remain checks on their exact evidence, not whole-store rollback detection.

Do not reset an outstanding attempt's creation interval or reuse its nonce after a known restore. Retire the unusable attempt while preserving possible release and cleanup obligations; any permitted new attempt needs current independently established authority and fresh identifiers. Historical reading does not require such a challenge and cannot release the hold.

## Recheck at release

Record freshness evidence as dependencies of the prepared send. Inside the [local release boundary](transport.md#local-authorization-and-release), recheck the current policy revision, accepted heads, role/verification/association state, evidence scope, complete credible time interval and operation-specific dependencies. A snapshot returned earlier is insufficient. Do not perform a blocking remote fetch while holding a long-lived database write lock: fetch bounded candidate evidence first, then revalidate and commit against current local state.

A held live requirement does not force an already established conversation to consume a new KeyPackage. Package validity and single-use admission are separate. A fresh response cannot extend either, restore an old device, widen an audience or grant historical keys.

Immediately before actual transport handoff, apply the existing final authority checks. If a prepared submission has already become uncertain, preserve its exact bytes and retry identity under the transport contract; fresh setup does not create another human message. A later revocation cannot recall content already disclosed. Ordinary historical reading needs no live confirmation and never triggers an automatic probe.

## Privacy, failure and evidence

An enabled device may answer automatically under its authorized setup policy. A valid fresh response reveals to the permitted requester that the signing device processed the challenge within that window; it does not prove human presence or reading. There is no public presence query. Service omission, exhaustion or timeout means freshness unavailable, not identity revoked or ordinary delivery authorized. A stronger requirement can intentionally sacrifice offline availability.

The [freshness component](evidence/README.md#freshness-policy-gate) exercises current accepted identity and actual assertion8/bootstrap signatures, recent declared-state age and a durable local live-attempt journal. It is not a trusted clock service, public provider, complete association/verification adapter, MLS admission or serialized send-release implementation. Current-suite integration remains required for both live exchange adapters.


A [state1 repair](identity-state.md#concurrent-administration-and-retirement) is a fresh-authorization boundary. Earlier cached assertions, pending challenges and prior freshness results are preserved as evidence but do not become current permissions through a guessed DAG path. Acquire the owning new evidence from the repaired head. Repair's derived issuedAt is the maximum parent time; its certificate is not itself a fresh live response or a current-time checkpoint.


## Reply-aware setup freshness

For the retained mail-conversation-v1 [reply-aware agreement](reply-intent.md#reply-aware-protected-agreement), the same cached-continuity, recent-checkpoint and live-device policies validate original assertion9. Its exact new signature, tuple, package/control-key and identity rules apply. A newer agreement does not relax the configured freshness mode or independently verified identity policy.

A live result uses its exact [provider exchange1](provider-control.md#reply-aware-known-pair-exchanges), [bootstrap1 response](bootstrap.md#provider-setup-for-declared-reply-policies), or qualified [mailbox setup1 response](#live-confirmation-through-existing-mailboxes), original local attempt, current target head/binding, purpose, agreement, nonce and complete credible interval. Original assertion8 evidence, a version0 result, publication retrieval or a service's ready status cannot satisfy it. Bootstrap publication1 can supply eligible cached evidence only under its own allocation and authorization rules; it is not a live challenge. Recompute after current identity/policy/source changes and retain original deadline/age anchors across retries. These requirements do not establish that current successor live-exchange adapters exist.


## Freshness for asynchronous deliveries

The selected freshness policy applies separately to each actual delivery's devices. A ready Bob does not prove that Carol is ready, and a pending Carol does not by itself stop an eligible delivery to Bob.

::: {.details summary="Assertion10, original live attempts and per-copy release"}

For mail-conversation-v2, validate original assertion10 under its exact signature, fixed readable application, per-device interactions, package/control-key receiving windows, current identity/association and known-negative rules. Cached continuity, recent checkpoint and live confirmation retain their meanings, local policy inputs and full credible-time checks. A newer agreement does not relax independent verification or make a publication live.

For the current opaque carrier, live evidence uses an exact [control3 device response](provider-control.md#obtain-complete-mail-receiving-evidence), fresh [bootstrap3 response](bootstrap.md#first-message-setup-with-carrier-support), or qualified [mailbox setup3 response](mailbox-setup.md#set-up-the-opaque-application-carrier), retaining the complete original receiving-bundle0 and signed carrier support.

Retained version2 results keep their earlier carriage scope and cannot satisfy a current3 attempt.

The selected live response must match the original locally outstanding intent/attempt, source account, target mailbox/device, agreement, nonce/digests, current exact target head/binding, original interval and selected maximum age. Apply all owning account/grant/disclosure/signature checks before freshness. Earlier responses, provider-ready states, publication retrieval and another target's valid response do not satisfy it.

Freeze each attempt's credible creation interval and original age/deadline anchors. Retry, late arrival, route completion or a change of acquisition version cannot reset them. A changed target head, account, policy, required agreement or selected intent invalidates dependent live decisions. Preserve accepted negative facts and uncertain submissions; another source cannot clear them by supplying newer-looking evidence.

For a ready cohort, independently qualify every actual selected device and the separate ordinary creator receiving evidence. Still-pending intended slots are not claimed to have responded. A later delivery obtains its own eligible current evidence and admission without rewriting the common authored bytes. No earlier live result is an account-wide token or a permission to disclose content beyond its retained original send intent. Package single use, retirement, native membership and final release remain independently required. Restored operational uncertainty remains a hold, even when fresh remote evidence exists.

:::
