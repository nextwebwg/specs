---
title: Freshness, clocks and revocation knowledge
order: 10.14
blurb: asynchronous default · recent account assertions · live device evidence · queued sends
sectionNav: true
---

# Freshness, clocks and revocation knowledge

Routine Email/2 delivery can use accepted setup while the recipient is offline. The sender checks that its evidence is still valid and that no known revocation or conflict prevents the send. A stricter local policy can require a recent account assertion or a fresh response from each intended receiving device.

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

Evaluate every intended remote receiving endpoint, including a paired device on another machine. The result names its exact principal, device, key, binding, accepted head and original assertion. One device's response cannot refresh another device or an account-wide roster. Locally originating devices still need their own current authority checks. Membership, administrators, ordering witnesses, verification and historical access retain their independent rules.

Every mode first requires the selected identity chain, applicable independent-verification policy, current role and binding, signed assertion8/application support, full validity intervals, mailbox association and known-conflict/revocation checks. A freshness result alone cannot admit a package, install a group, authorize a route or release content. Learning a newer accepted state invalidates evidence tied to the former exact head; a known authorized conflict holds affected work. Missing or invalid unsolicited claims cannot replace an accepted head or create an authorized fork.

::: {.details summary="Exact age checks and live-attempt binding"}

### Policy and credible time

Retain the exact local policy revision, mode and selected maximum age. Maximum age is an explicit positive unsigned-64 number of seconds for recent checkpoint or live confirmation; there is no implicit value inferred from a receipt or cache. Cached continuity has no additional age window and still obeys every signed validity interval. A deployment may impose an explicit maximum clock-uncertainty width; it cannot silently treat an uncertain estimate as an exact instant. These are local policy inputs, not peer-supplied fields or new wire records.

Let the credible current interval be `[earliest, latest]`. Require ordered unsigned-64 bounds and the entire interval within every applicable binding, assertion, challenge, response, grant and admission lifetime. Unknown/unreliable time leaves the check held. Future, crossing and expired intervals cannot be repaired using Message Date, HTTP Date, sender timestamps or an implicit grace period. Use checked arithmetic or subtraction comparisons without wraparound.

### Recent checkpoint

Resolve the exact current accepted head and its original signed identity-state bytes. Its proofs and signer authority must already have passed the full identity transition rules. Recheck current conflict and target-device authority in the same local authorization boundary. Require `issuedAt <= earliest` and `latest - issuedAt <= maximumAge`. Arrival, retrieval, database reopen and backup import do not change issuedAt. A different historical record, even with a more convenient timestamp, cannot substitute for the current head. A higher revision without an accepted proof chain is insufficient.

### Live confirmation

Use either the [known-pair device exchange](provider-control.md#signed-challenge-and-response-records) or a fresh [bootstrap response](bootstrap.md#recipient-control-inbox-and-fresh-response). Both must carry the current agreement's original assertion8 and pass their complete owning account, signature, purpose, target, authorization and identity checks. Earlier experimental advertisement decoders are not current-suite adapters.

Before emitting a challenge, durably retain its original signed bytes and signature, nonce, protocol/service/grant scope, selected own account/device, intended mailbox and known target when available, local policy revision, operation identity and credible creation interval `[startEarliest, startLatest]`. A first-contact target can be bound after independent association selection; it must match the returned signed evidence and exact intended mailbox. Operation identity is a local random intent identifier, not a human-message content hash. The setup traffic stays content-free.

The challenge has its protocol's original fixed deadline. For use, require the same local operation/policy/account and original outstanding request, exact response request hash/digest, nonce, participants, service and scope, current authorized device signature, exact assertion/head/binding and all original intervals. Bootstrap publications and another operation's response do not qualify. Require `latest - startEarliest <= maximumAge`; a smaller signed/protocol lifetime still applies. If a known clock movement or restore makes that local creation interval unreliable, hold and retire the attempt. Starting a newly authorized attempt needs a fresh identifier/nonce and cannot refresh the old one.

Exact retry, reopening storage and delayed response retrieval retain the creation interval. Cancellation is terminal for future use of that attempt. A cancelled/expired result remains historical evidence; it cannot become a new live permission. Account/policy/device changes require reevaluation, not clearing terminal state. The known-pair exchange cannot answer for a requested old state after the target has advanced; obtain independently valid identity evidence and authorize a new exact challenge instead.

:::

## Recheck at release

Record freshness evidence as dependencies of the prepared send. Inside the [local release boundary](transport.md#local-authorization-and-release), recheck the current policy revision, accepted heads, role/verification/association state, evidence scope, complete credible time interval and operation-specific dependencies. A snapshot returned earlier is insufficient. Do not perform a blocking remote fetch while holding a long-lived database write lock: fetch bounded candidate evidence first, then revalidate and commit against current local state.

A held live requirement does not force an already established conversation to consume a new KeyPackage. Package validity and single-use admission are separate. A fresh response cannot extend either, restore an old device, widen an audience or grant historical keys.

Immediately before actual transport handoff, apply the existing final authority checks. If a prepared submission has already become uncertain, preserve its exact bytes and retry identity under the transport contract; fresh setup does not create another human message. A later revocation cannot recall content already disclosed. Ordinary historical reading needs no live confirmation and never triggers an automatic probe.

## Privacy, failure and evidence

An enabled device may answer automatically under its authorized setup policy. A valid fresh response reveals to the permitted requester that the signing device processed the challenge within that window; it does not prove human presence or reading. There is no public presence query. Service omission, exhaustion or timeout means freshness unavailable, not identity revoked or ordinary delivery authorized. A stronger requirement can intentionally sacrifice offline availability.

The [freshness component](evidence/README.md#freshness-policy-gate) exercises current accepted identity and actual assertion8/bootstrap signatures, recent declared-state age and a durable local live-attempt journal. It is not a trusted clock service, public provider, complete association/verification adapter, MLS admission or serialized send-release implementation. Current-suite integration remains required for both live exchange adapters.
