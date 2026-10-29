---
title: Client and server adoption
order: 16
blurb: implementation stages · acceptance tools · interoperability
sectionNav: true
---

# Client and server adoption

Email/2 should become useful before every provider upgrades. A client can improve conversation reading on its own. Two compatible clients can exchange richer contributions over ordinary email. Server support then makes discovery, delivery and synchronization more reliable.

> [!ex] Start with the account people already use
> A client first makes an existing inbox easier to read. Later, two upgraded clients exchange a question and a button answer while a third person continues replying through ordinary email. Their provider can then add supported discovery and control routing without taking possession of their decryption keys.

This chapter describes proposed implementation paths and the evidence needed to advance along them. Implementations advertise specific supported profiles, not a single “Email/2 compatible” flag. This chapter announces no vendor commitments or available certification.

| Implementer | Practical starting point | What is available now |
| --- | --- | --- |
| Client | Open the conversation demos, then reproduce one exchange in your client | A source-preserving reader, joined interactions and signed protected rich-message fixtures; no complete client acceptance harness |
| Mail provider | Submit and retrieve representative messages through a test account, comparing preserved content with the source | Example messages and local checks; no completed provider deployment adapter |
| Interoperability contributor | Reproduce a published case and record the observed result against its requirement | Button and configured provider/admission report manifests; independent client/server results remain needed |

The [available starting material](#available-starting-material) distinguishes these development inputs from the proposed acceptance kit.

The [joined conversation demonstration](evidence/README.md#joined-question-and-ordinary-reply) supplies a concrete local integration target: a protected question, a browser answer button, actual encrypted reply delivery, and an ordinary email reply in one readable conversation. Its contact-name conversation list separates known contacts from other participants, orders threads by recent activity and keeps rich messages in an open layout. Ordinary replies retain their original email and collapse only uniquely matched fixed-line quotations. Its accounts and application agreement are explicitly configured; it is a development fixture, not a complete client acceptance harness.

New clients claiming Encryption target the [current asynchronous baseline](suite-profile.md#current-client-baseline). Provider carriage remains independently adoptable, and optional provider/setup or managed-group roles keep their declared bindings. Earlier experiments demonstrate only their exact compatibility or component scope.

The [cooperating-service architecture](service-federation.md) also lets a client
choose an independent home service while its existing mailbox provider stays
unchanged. A provider can contribute domain delegation or discovery alone before
adding rendezvous or fast delivery. Each capability needs its own complete wire
binding and acceptance evidence; the federation and fast-path bindings remain
unfinished. A directory result is not presence, a device enrollment or permission
to send content.

## No-cost participation

Two-way encryption depends on the recipient having a usable compatible client. The adoption target is a maintained client available at no cost for ordinary protected conversation, so receiving an invitation does not introduce a purchase decision. A paid-only client cannot assume correspondents will buy software merely to reply privately.

This is a proposed ecosystem adoption strategy, not a wire-protocol condition or a claim that a free implementation is already available. It does not require every implementation or service to use the same business model or software license. Other compatible clients must be able to participate through the same published protocol and acceptance cases.

Price is only one barrier. Installation, mailbox connection, first contact, adding a device and recovery must also be understandable. The [encryption journey](encryption-journey.md) provides the scenarios to test. An ordinary or hosted alternative remains a disclosed compatibility choice, not a substitute for making protected participation accessible.

## Email client adoption

The [client behavior contract](client-behavior.md) defines the target of these implementation stages, including people and thread lists, explicit composition targets, reactions, restart behavior and protection outcomes.

A client can deliver the first benefit alone: make existing mail easier to follow. It can then add predictable rich presentation, protected exchanges and structured answers over the same email account. None of these steps requires a provider control service. Each advertised capability still needs its complete profile and dependencies. These are development stages, not separate conformance levels: an Email/2 reading client must implement the [required HTML/CSS presentation](presentation-profile.md#required-presentation). A useful legacy-mail reader or text-only prototype does not yet meet that requirement.

| Release step | What the user gets | Starting point and acceptance check |
| --- | --- | --- |
| Read existing mail | A cleaner conversation without losing interleaved answers or attachments | Run the [source-preserving reader](evidence/README.md#inspectable-legacy-conversation-demo). Compare its view with the original; uncertain quotation matches stay visible and **View original** remains available. Include attributed blockquotes and interleaved replies; labels alone never identify repeated content. |
| Render the defined profile | Predictable formatting, described images, deliberate downloads and a usable plain-text view | Run the [rich-body example](evidence/README.md#protected-rich-body-and-scoped-images). Test an unavailable image, a misleading filename, keyboard use and switching between plain and rich views. |
| Establish protection through ordinary mail | Compatible clients exchange setup before the first human message, without manual key copying | Implement [mailbox setup](mailbox-setup.md) and its complete first-message acceptance case. The existing [client-only onboarding experiment](evidence/README.md#client-only-ordinary-mail-onboarding) uses human-authored introductions and proves only that earlier path. |
| Display protected context | The subject and sender remain tied to the accepted contribution even if a gateway changes the surrounding email | Run the [protected-presentation checks](evidence/README.md#managed-protected-presentation). Change outer Subject, From and Reply-To; verify the protected labels and reply audience remain unchanged. Keep older profiles visibly distinct. |
| Exchange structured contributions | A question can receive a button answer while an ordinary correspondent still replies in text | Run the [joined conversation demonstration](evidence/README.md#joined-question-and-ordinary-reply). Verify exact question references, duplicate delivery, restart and the separate ordinary reply. |
| Correct a message | Replacement text is marked as edited, while originals and competing versions remain available | Run the [joined edit flow](evidence/README.md#joined-protected-message-edits). Test reordered corrections, two-device conflicts, explicit resolution, revocation and the separately authorized ordinary copy. |
| Support device and group changes | A new authorized device can join, while removed devices cannot create new conversation effects | Run the [membership delivery checks](evidence/README.md#durable-established-welcome-delivery). Include delayed invitations, changed mailbox selections, removal, rejoin and uncertain submission. |

For multiple devices, the [own-account synchronization experiment](evidence/README.md#own-account-public-device-synchronization) supplies a second integration target: approve one new device, synchronize its signed public evidence, and deliver a protected message to both devices. The [pairing experiment](identity-lifecycle.md#pairing-another-device) adds two-way confirmation and a public-evidence relay for a new device. A deployed account service and platform pairing integration remain separate. Enrollment alone does not transfer old conversation history.

For a first integration, connect the client's retained message store to the source-preserving reader. Keep the original MIME available while deriving the cleaner view. Then connect the existing composer, durable send queue and authenticated receiver for one question and one answer. A displayed button becomes active only after its author, context and target have been accepted. Drawing a control over ordinary text is not authentication.

Automatic onboarding needs an explicit local first-contact policy. The implemented unverified-continuity path can remember one eligible first-seen identity and address association. It does not verify ownership of that address. Verification-required mode holds until an accepted mechanism supplies independent evidence. The optional [human comparison](mailbox-association.md#optional-human-comparison) records a comparison made through a separate trusted channel; it confirms the correspondent identity, not provider-certified mailbox ownership. Both modes preserve existing pins when an advertisement disappears; receiving an advertisement generates no automatic reply or network lookup. Use the [onboarding contract](capability-discovery.md#automatic-first-contact-over-ordinary-mail) for the exact boundary.

Device coverage needs its own decision. A client may target individually evidenced devices and show those not included, or require evidence for every authorized receiving device and wait when any is missing. An account login or one laptop's advertisement cannot establish support on another client. The local own-account experiment synchronizes signed public device evidence across independent stores. The pairing experiment supplies a separate trusted comparison and enrollment flow. Deployed account synchronization remains integration work; neither local result establishes complete account-wide discovery.

> [!ex] One account, two different clients
> Bob answers a question from his upgraded laptop. Later he opens the same mailbox on an ordinary client. An authorized readable copy can explain the answer there; the laptop's capabilities do not make that other client able to decrypt a protected-only copy or operate structured controls.

For rich messages, the supplied fixture joins signed admission, actual loopback SMTP, durable reception and the isolated browser renderer. Start with one described image and one download-only file. Test corruption and a redraw while the rich view is open. An ordinary rich copy needs retained permission covering the actual HTML and every resource; remembered policy can supply that permission without another compose dialog. The current browser checks cover Chromium. Other engines, native accessibility and production client integration still need their own evidence.

For evolving conversations, use the existing [initial roster](mls-invitations.md) and [group membership](group-conversations.md) profiles. The local experiments cover multiple accounts and devices, separate invitations, membership changes and fresh-package rejoin. They also test [atomic recovery through membership changes](evidence/README.md#atomic-membership-recovery): intermediate states cannot authorize new effects, and the selected recovery policy deletes past epoch secrets. Automatic chain retrieval from a configured mailbox spool has local checks. Live provider synchronization and ordering failover remain separate work. Keep each target’s submission and admission outcomes separate; a fixed-roster group does not become an evolving group merely because a later client supports more features.

> [!note] Show the outcome the client actually knows
> “Submitted” means the mail server accepted the message. “Joined” needs authenticated admission evidence. Sending a membership update before an invitation does not prove that another client processed either message.

[Service answers](service-answers.md) let a deliberate button press submit a choice to an independently authorized service. Start with the [joined service control](evidence/README.md#joined-service-question-control): signed discovery and SMTP lead to an accepted question, a trusted button, an HTTPS effect and a matching receipt. The service result remains separate from a conversation answer. The [native authorization profile](service-authorization.md) adds a reviewable sign-in and explicit device-linking flow, exercised with separate synthetic browser consent, a real loopback callback and TLS. Production login integration and independent-service interoperability remain outstanding.

These sources are implemented local fixtures and reference components, not a finished client toolkit. Use the [acceptance reports](#available-starting-material) to see which cases actually ran, then add an adapter for your client. A local pass cannot stand in for real-provider carriage, independent peers or manual accessibility checks. Test the intended benefits too: whether people can find each person's answer, avoid repeated quoting and understand the actual protection state. No measured usability improvement is claimed yet.

## Email server adoption

Providers can add support in stages while keeping existing addresses, SMTP delivery and IMAP or JMAP access. The first useful upgrade is dependable carriage: compatible clients can already exchange protected contributions through ordinary email. A provider does not need to hold decryption keys, render message HTML or run a key directory to preserve those packages.

Each later stage advertises a specific capability. Upgrading a server can improve discovery or delivery, but it cannot make an older client understand a new message format. A successful transport negotiation describes that hop; protection still depends on the intended receiving devices and the sender's delivery policy.

| Stage | What it unlocks | Evidence before advertising support |
| --- | --- | --- |
| Preserve submission, storage and retrieval | Structured and protected packages survive the account's normal mail path | A report from actual submission, filtering, relay and retrieval paths, with protected-payload comparisons and recipient-specific outcomes |
| Add authorized discovery and control | Compatible clients obtain scoped device evidence without sending negotiation mail into inboxes | Authorization, expiry, replay, device scope, resource limits and service-withdrawal checks against the selected control profile |
| Add a completed synchronization or relay capability | The particular continuity or delivery benefit defined by that capability | Its own contract, client integration and interoperability report; these extensions are not unlocked merely by implementing discovery |

### Start with carriage

Use the [loopback MIME exchange](evidence/README.md#loopback-smtp-exchange) to reproduce the supplied packages and comparisons. Then submit and retrieve those packages through synthetic accounts in the provider's staging environment. The loopback fixture is available; an authenticated adapter for a real provider remains to be built.

Compare the submitted and retrieved representations, distinguishing MIME transfer re-encoding from changes to protected payload bytes. Retain the source messages, observed transformations and per-recipient outcomes. Include forwarding as a separate operation: a forward is a new message, not proof that the original delivery path preserved its contents. Server acceptance alone does not establish decryption, reading or successful answer submission.

The first corpus should include:

- A question with a readable alternative and a structured answer, including an ordinary client's reply.
- A protected rich message with a scoped image and a separate attachment. The [carrier checks](evidence/README.md#joined-protected-carriers-and-deliberate-attachment-download) and [rich-body fixture](evidence/README.md#protected-rich-body-and-scoped-images) supply source packages; the provider need not render them.
- A Commit addressed to existing devices and a separate Welcome addressed to a joining device. Test delay, duplication and reordering while preserving their distinct recipient scopes. The [Welcome checks](evidence/README.md#durable-established-welcome-delivery) supply local recovery cases.

This stage gives a provider a concrete contribution to interoperability without requiring an account-service rollout. Publish the observed limitations as well as successful cases so client implementers can reproduce failures.

### Add account services independently

The [provider negotiation proposal](provider-negotiation.md) defines service roles; its [configured wire profile](provider-control.md) defines the experimental exchange. Start with the [configured HTTPS adapter](evidence/README.md#configured-provider-https-adapter), then reproduce [discovery through encrypted mail](evidence/README.md#provider-discovery-to-encrypted-mail). These join local service authorization, device evidence, admission and message exchange. The separate [discovery contract](provider-discovery.md) adds domain delegation and native public-client registration. These experiments do not provide public queue-credential issuance, prove mailbox ownership or demonstrate a deployed provider integration. [Automatic first-contact setup](first-contact-setup.md) requires implementing and integrating the selected [public bootstrap binding](bootstrap.md) before a provider can offer encrypted first messages to previously unknown peers.

The [provider/admission report](evidence/README.md#configured-provider-and-admission-report) is an available, bounded acceptance entry point. It records local checks and explicitly untested deployment scenarios. Extend it with the staging adapter and actual observations; do not turn a local pass into a deployment claim.

Keep the service separate from ordinary mailbox delivery. Rejecting an invalid control-service request is permitted by that service's contract; deleting or hiding an email because it resembles negotiation traffic is not. Publishing device evidence also does not enroll a device or promise that every client using the account can decrypt.

Hosted fallback is another optional service, with a different trust boundary. The [hosted-access experiment](hosted-access.md) supplies configured message/question access, notification and holder-attributed replies. It does not make bearer possession proof of mailbox ownership or end-to-end encryption. A provider can evaluate that service independently of protected carriage; public authorization and production hosting remain outstanding.

### Roll out with withdrawal tested

After staging checks, an operator can choose an opt-in cohort and measure the benefit of each capability. Keep a way to disable optional services. Test withdrawal while work is queued: ordinary delivery remains available where the sender's policy permits it, while required protected work stays held. Withdrawal must not erase pinned identities or silently convert protected contributions to plaintext. Cohort size and timing remain deployment choices.

The intended gains are fewer damaged protected deliveries, less negotiation clutter and a documented client integration surface. These are benefits to measure, not established results or vendor commitments. Synchronization and upgraded relay features need completed contracts and independent evidence before advertisement. Existing transport remains useful throughout the rollout.

## Acceptance tools and interoperability program

Start with one implemented profile and reproduce its report before writing an adapter for your client or server. The [implementation-claim rules](conformance.md) define what the result supports. Passing local checks establishes only the cases named by that manifest; it does not certify a client, establish mailbox ownership or demonstrate independent interoperability.

1. Choose a manifest below and follow its linked setup instructions. Preserve the selected profile and manifest revision rather than silently replacing an older wire version with a newer one.
2. Run the [offline acceptance runner](evidence/README.md#offline-acceptance-report) with `--manifest` and retain its JSON report, source hashes and scenario results. The default manifest is the button example. For example, from the Email/2 directory after configuring the documented test dependencies:

   ```sh
   python3 evidence/run_acceptance.py --manifest acceptance-onboarding.json
   ```

3. Compare the observed outcome with the linked requirement. Fix failures, leave unavailable cases visibly untested, then add an adapter that records the same observations from your implementation. Preserve submitted and received bytes, versions and topology; record manual rendering or accessibility evidence separately.

| Existing manifest | Local report scope | Cases still unavailable in that report |
| --- | --- | --- |
| [Button examples](evidence/acceptance-cases.json) · [setup](evidence/README.md#offline-acceptance-report) | Four MIME and structured-answer checks | Ordinary-client display, deployed carriage and authenticated endpoint submission |
| [Provider/admission](evidence/acceptance-provider-admission.json) · [setup](evidence/README.md#configured-provider-and-admission-report) | Five configured discovery, admission and protected-message checks | Public provider authorization, independent peers and deployed carriage |
| [Initial invitation](evidence/acceptance-invitation.json) · [setup](evidence/README.md#initial-invitation-acceptance-report) | Six version-0 carrier and admission checks | Durable sending within this manifest, deployed carriage and independent peers |
| [Version-1 initial invitation](evidence/acceptance-invitation-v1.json) · [setup](evidence/README.md#version-1-initial-invitation-acceptance-report) | Twelve admission, durable sending and recovery checks | Deployed carriage and independent peers |
| [Established invitation](evidence/acceptance-established-v1.json) · [setup](evidence/README.md#established-invitation-acceptance-report) | Five application-aware admission and removal/rejoin checks | Deployed carriage and independent peers |
| [Client-only onboarding](evidence/acceptance-onboarding.json) · [setup](evidence/README.md#client-only-onboarding-acceptance-report) | Nine ordinary-mail discovery, invitation and protected-reply checks | Deployed carriage and independent peers |
| [Joined service answers](evidence/acceptance-joined-service.json) · [setup](evidence/README.md#joined-service-question-control) | Six configured signed-question, HTTPS-effect, retry and authorization checks | Independent client/service implementations and deployed carriage; native sign-in is a separate experiment |
| [Signed group lifecycle](evidence/acceptance-quorum-signed.json) · [setup](evidence/README.md#signed-group-acceptance-report) | Eight assertion7 discovery, exchange1, carrier2 admission, sender-continuity, proposal-observation, support-renewal and atomic recovery checks | Independent peers, deployed provider carriage and independent security review |

A normal successful runner exit means no executed case failed. It can still contain `not-tested` cases and report `complete: false`. `--require-complete` also fails while any case has not passed; all eight manifests retain unavailable external scenarios. A skipped security case cannot become a pass. These reports cover their selected versions and scenarios, not every newer experiment in this repository. The joined service-answer manifest exercises authenticated endpoint submission; the older button manifest still reports that case as untested. The [validation record](validation.md#reusable-acceptance-reports) links the current reports and their recorded input hashes.

The reusable interoperability kit below is proposed packaging, not a finished product. Each case should have an identifier, profile revision, input, expected observable result and governing requirement. Reports must distinguish pass, fail, unsupported and not tested. Existing code and fixtures are [available starting material](#available-starting-material).

| Proposed deliverable | Useful output | Work needed beyond existing components |
| --- | --- | --- |
| Message inspection command | A local report of MIME scope, original payload hashes, readable alternatives and validation failures | One versioned interface, structured diagnostics and integration with actual authentication |
| Mixed-client conversation kit | Downloadable messages and a checklist covering reply, edit, forward and replay | Extend the implemented local question/answer demo into packaged scenarios and collect observations from actual ordinary and upgraded clients |
| Provider carriage adapter | Source/delivered representations and a requirement-linked transformation report | Authenticated real-provider submission and retrieval, credentials and timeout reconciliation |
| Client rendering checklist | Rendered evidence plus keyboard and screen-reader outcomes | Broader browser coverage, validated platform resource enforcement and comparable manual accessibility results; parser/decoder process limits and a memory watchdog already exist locally |
| Protected lifecycle adapter | Separate records of submission, admission, device changes, restart and replay | Package the implemented initial/established invitation, multi-device roster and signed-instance tests into versioned adapters; add independently implemented peers |
| Configured control-service adapter | Results for authorization, replay, expiry and absence of negotiation mail | Package the joined local provider/encryption checks; add public authorization/discovery bindings and deployment evidence |

Use the existing offline report format where practical, adding topology and manual evidence as needed. A screenshot or support declaration is not an automated pass. Manual accessibility and usability checks remain visible where automation cannot establish the result.

Cross-implementation runs should use the same scenarios with different clients, servers and security libraries. Reports identify the exact versions and topology, including mixed legacy participants. A successful loopback through one implementation is useful development evidence but does not demonstrate independent interoperability.

> [!ex] Answering through a mixed conversation
> Alice sends “Tuesday or Thursday?” Bob presses “Thursday” in an upgraded client. Carol reads the question in an ordinary client and replies in text. The test checks that Bob's answer identifies the exact question, Carol's reply remains ordinary text, retrying Bob's submission does not add another answer, and neither reply automatically includes the conversation history.

Security cases include stripped capability advertisements, altered MIME alternatives, a replayed answer, an unauthorized key change, a removed device and a service request whose response is lost. The expected result must include what the person sees and which effects are prevented, not just whether a parser returns an error.

The service-answer adapter must also reorder acknowledgements: deliver pending after confirmed, duplicate a terminal receipt, return “not found” after a receipt has been retained, and supply incompatible authenticated terminal results. The client must preserve the confirmed outcome in the first three cases and show conflict in the last. An unauthenticated conflicting response must not alter the valid submission. These are required scenarios for the proposed cross-implementation service adapter. The joined service-answer manifest covers local lost-response and status reconciliation, but does not cover this complete reordering matrix or independent implementations. Local service experiments do not substitute for that external adapter.

## Making participation practical

Publish a short entry point, downloadable fixtures and machine-readable results for each stage. Keep the first run local; offer optional adapters for real test accounts. An implementer can contribute one scenario by publishing the versions, topology and observed result, with a minimized reproduction and requirement link for any mismatch. Resolve disagreements in the specification and add a shared regression case. Independent client implementers, mail operators, accessibility specialists and security reviewers are prospective participants; no partnership or commitment is assumed.

Track adoption by independently implemented profiles, successful cross-implementation scenarios and resolved deployment failures. Download counts, a vendor logo or a self-declared capability flag do not establish compatibility. Publish limitations alongside successful results, and keep any future certification or trademark policy separate from the technical requirements.

## Internationalized domain validation

Implementers can reproduce the [configured Unicode17 provider checks](evidence/IDNA17.md) before accepting internationalized domain labels. The supplied adapter validates canonical A-labels in passive advertisements and HTTPS reference names, with explicit data-version checks and no silent fallback. Without configuration, these experimental consumers continue to hold or reject A-labels. Passing domain syntax checks does not prove control of a mailbox or service.

## Available starting material

The [local experiments](evidence/README.md) supply runnable components and synthetic messages. The [validation record](validation.md) identifies what ran and its limits. These are development inputs, not a complete client toolkit, provider deployment or certification program.

| Start with | Available local evidence | Next integration step |
| --- | --- | --- |
| [Conversation reader](evidence/README.md#inspectable-legacy-conversation-demo) | Source-preserving plain and HTML views, interleaved answers, attributed blockquotes and visible localized labels | Connect an actual client store and collect broader, consented format examples; preserve originals and ambiguous text |
| [Rich presentation](evidence/README.md#protected-rich-body-and-scoped-images) | Signed admission, loopback delivery, durable reception, scoped images, explicit downloads and plain/rich browser views | Integrate the client renderer and test other engines and native accessibility |
| [Client-only onboarding](evidence/README.md#client-only-ordinary-mail-onboarding) | Ordinary mail supplies peer evidence before signed admission and protected replies, with explicit first-contact and device-coverage policies | Integrate the implemented human comparison, own-device evidence and remote-pairing flows with deployed accounts; validate independent peers |
| [Joined interactions](evidence/README.md#joined-question-and-ordinary-reply) | Browser answer controls, authenticated references, durable protected replies and separately authorized ordinary copies | Package further operation scenarios and run them with independent clients |
| [Membership delivery](evidence/README.md#durable-established-welcome-delivery) and [atomic recovery](evidence/README.md#atomic-membership-recovery) | Separate invitation/control submission, removal/rejoin, replay and transaction/crash checks | Add live provider synchronization, safe ordering failover and independent lifecycle interoperability |
| [Provider exchange](evidence/README.md#configured-provider-https-adapter) | Configured HTTPS authorization, signed device evidence and durable retries, joined to admission and encrypted mail | Supply public authorization/discovery bindings and a staging-provider adapter |
| [Service answers](service-answers.md) and [hosted access](hosted-access.md) | Signed SMTP question → trusted button → HTTPS effect/receipt; native account authorization and signed linking; separately configured hosted access and holder-attributed replies | Integrate production login and hosted management credentials, then test deployed services without confusing outcomes with conversation authorship |

The [acceptance manifests above](#acceptance-tools-and-interoperability-program) are the report entrypoints. Start with one, retain its source revision and result, and leave unavailable scenarios explicitly untested. Local checks and loopback delivery do not establish independent interoperability.

HTML parsing and image decoding run in limited worker processes. The [resource-enforcement evidence](evidence/README.md#isolated-html-parsing) distinguishes tested CPU, output and time enforcement from the sampled memory watchdog on macOS. It does not claim a hard allocation ceiling, a security sandbox or complete decoder fidelity. Treat platform enforcement and rendering quality as separate checks.

The next tooling work is to package the remaining profile cases and add actual client/server adapters. Independent implementations must then publish the versions, topology, outcomes and limitations of shared runs. The [open decisions](interoperability.md) identify boundaries still needing a complete contract or implementation.
