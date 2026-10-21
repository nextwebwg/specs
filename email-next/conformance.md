---
title: Implementation claims and acceptance
order: 15.5
blurb: supported profiles · dependencies · reproducible results
sectionNav: true
---

# Implementation claims and acceptance

An implementation supports the Email/2 base and named modules in particular roles, under the exact wire encodings those contracts select. It does not become universally compatible by recognizing one attachment, displaying a button or passing a parser test. A support claim identifies the implemented profile revision, its dependencies and the behavior that has actually been checked.

> [!ex] A provider carries protected mail
> A provider can preserve a protected message through submission and retrieval without implementing its encryption. Its report demonstrates carriage. It cannot advertise that every device using the mailbox can decrypt that message.

This chapter defines proposed claim and evidence rules. There is no certification program or completed whole-protocol conformance suite. The [validation record](validation.md) describes current local evidence; the [adoption plan](adoption.md) describes participation and tooling.

## Reading requirements

Uppercase MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL use the meanings in [BCP 14 (RFC2119 and RFC8174)](audits/requirement-language.md). Lowercase words retain their ordinary meaning. Requirements can also be stated directly without uppercase keywords.

These are requirements of the proposed profile, not evidence that it has been adopted by a standards body. An optional capability may be omitted, but its specified fallback and rejection rules still apply. A SHOULD exception requires understanding its consequences; it cannot override an independent MUST.

## State the role and scope

A claim must identify the implementation and version, the exact profile revision, the acting role and the tested configuration. A client, renderer, submitting service, retrieving service and discovery service have different obligations. One product can perform several roles, but evidence for one does not establish another.

| Claim | Necessary boundary |
| --- | --- |
| Conversation reconstruction | Original content remains available; uncertain attribution stays visible; no distinct response disappears |
| Structured contributions | Supported operations, exact references, authentication prerequisites, replay handling and readable alternatives |
| Presentation | Complete selected vocabulary, rejection behavior, resource isolation and accessibility requirements |
| Protected conversation | Identity and device authority, protocol processing, durable lifecycle, policy and disclosure behavior, including [setup-secret retirement](setup-secret-retirement.md) and accurate memory/storage erasure claims |
| Provider carriage | Actual submission/storage/retrieval paths and any transformations of protected bytes |
| Provider control | Exact configured service contract, authorization, expiry, retries and resource limits; optional [public discovery](provider-discovery.md) requires its exact domain/issuer/registration and durable publication rules, the separate [public grant profile](provider-grants.md) requires account/device linking, exact pair approval, role issuance and serialized revocation, and [Auto setup](bootstrap.md) requires independently authorized source accounts, exact exchange/device proofs, recipient opt-in, bounded disclosure and full first-message acceptance; component tests do not establish implemented integration |
| Service interaction | Accepted question and chosen option, independently trusted destination, account authorization, durable request identity and authenticated outcome |
| Own-device enrollment | Independent confirmation of the new device, current enrollment authority, exact permissions, replay prevention and atomic acceptance |
| Archive and collection reader | Independent recovery kit, complete file authentication, writer signatures, exact inventories, atomic history-only acceptance and honest completeness/freshness outcomes under [archives](encrypted-archives.md) and [collections](archive-sets.md) |
| History transfer | Accepted endpoint authority, exact source disclosure decision, recipient-specific files, request/grant/cancel correlation, historical import and terminal result under [history transfer](history-transfer.md) |
| Group ordering | Selected ordering policy, authorized membership change, sufficient decision evidence, atomic installation and behavior when progress is impossible |

A limitation must not contradict a mandatory requirement while retaining a claim for the affected module. A provider or client may omit optional modules and report its supported module list. The [module framework](modules.md) distinguishes omitted modules from incomplete implementation of a claimed module; none requires a separate edition of Email/2.

## Protected conversation agreement

An Encryption implementation targets the [protected core and selected optional interactions](suite-profile.md), including its exact signed application/ordering agreement and both required rendering profiles. The complete protected bundle implements all three interaction modules; base clients and providers need not implement that entire bundle. Existing component results do not establish joined module support. [Design resolutions](design-resolution.md) distinguishes remaining protocol work from implementation and external evidence.

## Dependencies are part of the claim

A profile's mandatory dependencies must be implemented in the role where they apply. Passing schema validation does not establish authenticated authorship; decrypting a packet does not establish current authority to perform an action. An account capability cannot substitute for a receiving device's capability.

Unknown or unsupported profile revisions must follow the owning contract's fallback or rejection rules. They must not be interpreted as the nearest familiar version. A failed check cannot authorize weaker protection unless the sender's independently established policy allows that outcome.

Experimental identifiers and private-use formats remain experimental even when two implementations agree on them. Registration, standardization and implementation support are separate facts.

### Character-data and parser dependencies

Record the data versions actually used by each decision, not only the library’s package version. Domain validation can depend on separate normalization, case-folding, character-property and IDNA tables. Those providers must agree with the selected profile. A newer table combined with an older host-runtime normalizer is not evidence of support for the newer Unicode version.

A declared version is necessary but insufficient. Check the selected normalization corpus, applicable property defaults and ranges, contextual rules and derived classifications against the pinned sources. Report any differences and their disposition before enabling that profile. A provider mismatch holds the affected validation; it must not silently select another version, rewrite the address or accept an unchecked encoded label.

The same principle applies to HTML/CSS parsing and cryptographic adapters: identify the parser or library, its configuration and the rules supplied by the application. A library’s supported feature set does not prove that the application selected or enforced those rules. Test the integrated boundary as well as the underlying component.

### Key expiry and renewal policy

A protected-conversation report records the configured [maximum setup-key lifetime](security-profile.md#experimental-admission-lifetime), issuance defaults and any additional library limits. Seven days is a configurable default, not evidence that automatic renewal works. Test a shorter interval and a longer configured interval; the same signed package must still fail after its original expiry. Include uncertain time, malformed local policy, revocation before expiry, consumed-package retry, restart, and a publication or invitation attempting to outlive its underlying authority.

A complete automatic-renewal claim also requires fresh replacement keys and references, authenticated publication, unchanged-contact continuity, an interrupted renewal with preserved drafts, and retirement of unused expired secrets. Historical reading must remain available without reactivating consumed transport keys. Component lifetime checks do not establish these joined outcomes or a universal rotation schedule.

## Report observable outcomes

Each acceptance case identifies its governing requirement, input, setup and expected observable result. Reports retain the implementation versions, profile revision, relevant configuration, source/fixture digests and whether execution used one implementation or independent peers. Secrets and live credentials do not belong in reports.

| Outcome | Meaning |
| --- | --- |
| Pass | The stated check ran and its expected result was observed |
| Fail | The check ran and contradicted its expected result, or failed to execute successfully |
| Unsupported | The implementation explicitly does not implement the named capability |
| Not tested | The check did not establish an outcome, including missing adapters and skipped tests |

Unsupported and not-tested cases never count as passes. A complete report has no unpassed mandatory cases for its stated scope. Even a complete report proves only that case set: it does not establish omitted requirements, independent interoperability or security review.

### Keep separately authorized steps visible

A joined test must exercise the actual transitions between components. For a service button, receiving an authenticated question, linking a service account, authorizing an option and retaining a service receipt are separate checks. A preconfigured token-to-principal mapping cannot demonstrate account linking. A receipt for a service effect cannot demonstrate that a conversation reply was delivered.

For a new device, enrollment, confidential security-configuration staging, live trust reconciliation, mailbox connection, publication of supported profiles and admission to a conversation are separate transitions. The [setup transfer](identity-lifecycle.md#confidential-security-configuration-transfer) requires actual contact-store installation evidence before an installed receipt or send-ready claim. Test conflicting existing pins, newer revocations, withdrawn verification, original evidence expiry, a locally stronger policy, a cancelled or expired request and a crash before activation; a staged plaintext file cannot count as those outcomes. A paired device does not acquire old message keys merely because its enrollment succeeded. For a membership change, a valid ordering decision does not by itself prove that the application installed it without losing newer message-processing state. Test the shared durable state at that boundary, including a crash or intervening message.

Manual evidence must identify the method and observed result. An accessibility-tree snapshot is not a screen-reader test; a MIME inspection is not an ordinary client's rendered display. Record these distinctions rather than treating automation as a substitute for the intended observation.

## Exercise failures and mixed deployments

Acceptance must include invalid input, missing dependencies, duplicate and reordered delivery, restart and failed persistence wherever the profile can change durable state. A failure case checks both the visible outcome and the absence of prohibited effects. An error message alone does not prove that a package was not consumed, a recipient was not added or an external action was not submitted.

Mixed-client cases retain ordinary replies and readable alternatives. Mixed-protection cases check the disclosed exposure and the sender's selected policy. Independent client/server runs identify the actual topology; a local SMTP loopback remains a local experiment.

The [interoperability scenarios](interoperability.md#proposed-acceptance-scenarios) and each profile's acceptance requirements supply the specific cases. This chapter does not replace their schemas or algorithms.

## Required encrypted personal addresses

Encryption receiving support includes the [personal-address contract](private-address-presentation.md): envelope4, address/audience binding and assurance/display behavior under the one required suite agreement. Address metadata alone does not authorize routes or independently verify mailbox ownership. A full transport-address privacy claim additionally requires the [relay lifecycle and transport projection](private-routing.md), the [source/route/proof contract](relay-routes.md), actual provider/SMTP/mailbox integration and all required control-carrier protection; configured encrypted-carriage evidence does not establish that lifecycle or opaque SMTP delivery.
