---
title: Validation evidence and remaining coverage
order: 17
sectionNav: true
---

# Validation evidence and remaining coverage

Email/2 has executable local evidence for selected message, identity, transport and rendering behavior. It does not yet have two independently implemented clients exchanging the complete protocol through deployed email providers. Passing component tests does not establish security assurance or complete conformance.

## Recorded checks

These results describe local feature branches, not a published release. The [experiment notes](evidence/README.md) give setup instructions, individual scopes and limitations. Delivery gates must run against the delivered revision.

| Check | Recorded result | What it establishes |
| --- | --- | --- |
| Specification compilation | 254 chapters compile | Markdown compiles through the shared compiler; this is not a semantic audit |
| Local vault writer accounting | Seven focused tests pass; six native authorization client tests pass | Includes real process death after a committed reservation, shared process budget, rollback/restart, explicit legacy migration and rejection outside an application transaction; restored-owner continuity remains an operational assumption |
| Repository Node gate | 370 tests pass: 34 compiler, 36 existing feature-profile, 300 Email/2 | Covered compiler and experimental models pass; Python, Rust and browser checks run separately |
| Python integration | 1,038-case run: 1,034 passed, four retry-test stub failures; all 37 sender/association tests pass after correcting that stub | Resource warnings are errors. The four failures were repeated uses of one test that blocked the new read-only state inspection; it now permits inspection while rejecting a second encryption or transport. Implementation inputs are unchanged after the complete run; the complete command was not rerun after this test-only correction. |
| Conversation interface | Raw and signed-rich browser flows pass; four focused message-reaction/compatibility checks pass | Right-edge selectors use exact per-message targets, protected answers/attachments retain authenticated reactions, ordinary reactions use RFC9078 MIME, unsupported protected rich targets remain unavailable; real local protected answers, reactions, ordinary replies retained in arrival order, contact/group names, Contacts/Other separation, recent-activity ordering, separate drafts, conservative quoted-history collapse, exact originals, rich rendering and narrow-screen layout; session-only timeline, not a persistent mailbox client |
| Validated proposal observations | 34 integrated checks pass | Covers configured and signed-discovery holds, actual staged proposal lists, restart, certified carrier advancement, sender continuity, bound copies and pre-DATA interruption; raw wrapper receipt alone has no hold effect |
| Image interpretation | 42 focused checks and 8 browser image-box cases pass | Selected PNG depth/type/interlace, transparency, Exif orientation, ICC and gamma/chromaticity behavior; broader codec/fuzz coverage and independent color-management agreement remain unproven |
| Concurrent group changes | Four admitted-quorum tests and an additional real-process crash case pass | Locally retained exact MLS Commit merges into the latest group state after incoming and outgoing messages; rollback, replay and retry checked; no cross-version staged-state migration |
| Protected edits | 13 joined tests and the browser flow pass; final resource-bound changes pass two focused checks independently | Signed SMTP corrections, concurrent versions, retained originals, explicit resolution, revocation effects and bounded view reconstruction; no rich-message editing or independent-client claim |
| Protected presentation | 9 focused tests pass; 4 loopback browser groups pass | Accepted subject/author/audience, altered outer headers, protected reply and explicit ordinary subject disclosure; semantic MLS fields, not RFC9788 wire compatibility |
| Protected private copies | 12 focused tests pass; loopback browser flow passes | Separate visible and private questions, private replies, device changes, fallback and attachment bytes; no independent-client or global delivery-atomicity claim |
| [Joined service control](evidence/README.md#joined-service-question-control) | 6 focused tests pass; loopback browser flow passes | Signed SMTP question, trusted activation, HTTPS effect/receipt, exact retries, renewed authorization and device-revocation holds; no public credential acquisition |
| [Native service authorization](service-authorization.md) | 14 focused backend/client tests and the separate-context browser flow pass | Simulated account consent, actual loopback callback/TLS exchange, signed account link, protected SMTP question and service effect; no production login or independent interoperability |
| [Managed restoration](identity-lifecycle.md#import-history-then-reconnect) | 7 focused tests pass; 4 browser checks pass | Inert history import, excluded live state, fresh pairing or explicit new identity and protected SMTP; no encrypted backup or whole-machine rollback detection |
| Own-account device coordination | 10 focused tests pass | Independent stores, exact enrollment approval, public-only synchronization, protected SMTP delivery and revocation holds; no remote pairing or history transfer |
| Confidential setup and contact installation | Twelve signed/encrypted transfer cases plus the reference contact-store integration below | Accepted QR pairing, real age, source snapshot, per-contact live trust installation, original comparison provenance/expiry/withdrawal, conflict holds and scoped receipts; no deployed account login or whole-client send-ready result |
| Certificate algorithm correction | Ten backend tests pass independently | Correctly re-signed forbidden ECDSA/Ed parameters rejected from original verified-chain DER before HTTP; valid RSA/PSS/mixed algorithms, DN matching and path constraints checked; no exhaustive backend certification |
| Certificate-status policy and adjacent TLS checks | 21 focused tests pass | Synthetic policy observations and actual socket gates; no real OCSP authentication or backend certification |
| Quorum lifecycle | 7 focused tests pass independently | Terminal removal notice, ordered history through removal, atomic recovery through revoked intermediate epochs and final protected reply; configured loopback, no global fencing or complete distributed liveness claim |
| Automatic mailbox recovery | 11 focused tests pass | Actual SMTP-to-spool retrieval, current support selection, atomic acceptance, fork/cursor/crash checks; no deployed synchronization or writer replacement |
| Parser and image cleanup | 24 focused tests pass without resource warnings | Includes explicit closure of partially written worker input after timeout; the full-suite run above includes this cleanup fix |
| Optional human verification | 68 focused tests and the trusted confirmation-screen browser checks pass | Exact comparison evidence, strict roster delivery, protected reply and expiry/withdrawal checks; not provider-certified mailbox ownership |
| Browser isolation | 21 Chromium check groups plus 3 nonce tests pass | Message-channel bootstrap, isolated rendering and lifecycle checks; not a security sandbox certification |
| Inline and bidirectional geometry | 4 Chromium cases pass at two widths and both parent directions | Fragment edges, isolation, opposite-direction spans and combining-pair line placement; not painted-glyph or full Unicode conformance |
| Static site generation | 227 Email/2 chapters and 1,210 section links checked | Generated routes, local links and source downloads, including eight acceptance manifests and their reports; draft excluded from homepage proposal navigation |

The complete integration run executed 1,038 tests in 1,395.448 seconds using configured parse5 and shared Rust workers, with resource warnings treated as errors. Four repeated retry cases failed because their test stub prohibited every crypto-worker call, including the newly required read-only current-state inspection. The corrected test permits only inspection and still verifies exact ciphertext, unchanged checkpoint and no transport. All 37 sender/association tests then passed in 10.230 seconds. Only that test file changed after the full run; no implementation input changed. These are separate recorded results, not a clean full-command rerun.

The run includes the populated conversation, image interpretation and validated-proposal observation implementation. Dedicated raw/signed-rich browser flows and the scoped image checks provide separate UI/resource evidence. The earlier 1,008-test checkpoint passed before these additions; it does not replace the current integration results.

Browser evidence uses Chromium153.0.8010.12 with one runner. Other engines, native zoom, screen readers, hard memory enforcement on macOS and complete image-decoder fidelity remain unverified. Parser and decoder workers have tested CPU, output and time limits plus a sampled resident-memory watchdog; that is not a hard allocation ceiling or a general security sandbox.

Specification checks use Node24.20.0 and pnpm11.25.0. Site generation uses Node22.23.3 and tools revision5287ff26fdede242afcbdee54b1ee93f1a9843c1. The preview uses real local specification/tools checkouts. Final dependency pins and the acceptance-kit upstream revision remain delivery requirements. The generated-site check validates chapter routes, section links and source downloads; it does not validate protocol semantics.

## Reusable acceptance reports

The linked reports cover the current source inputs, including populated conversations, image interpretation and the validated-proposal send boundary. Manifest, implementation and declared mail-fixture hashes were checked after all eight reports completed. Each report retains those fingerprints; later implementation changes require a new report. These are development results, not release certification.

| Manifest | Local result | Explicitly missing coverage |
| --- | --- | --- |
| [Button examples](evidence/acceptance-cases.json) · [report](evidence/reports/acceptance-cases.json) | 4 pass, 3 not tested | Legacy-client display, provider carriage and authenticated service submission |
| [Provider/admission](evidence/acceptance-provider-admission.json) · [report](evidence/reports/acceptance-provider-admission.json) | 5 pass, 3 not tested | Public credential/discovery lifecycle, independent implementations and deployed carriage |
| [Version-0 initial invitation](evidence/acceptance-invitation.json) · [report](evidence/reports/acceptance-invitation.json) | 6 pass, 3 not tested | Durable sending within this manifest, deployed carriage and independent implementations |
| [Version-1 initial invitation](evidence/acceptance-invitation-v1.json) · [report](evidence/reports/acceptance-invitation-v1.json) | 12 pass, 2 not tested | Deployed carriage and independent implementations |
| [Established invitation](evidence/acceptance-established-v1.json) · [report](evidence/reports/acceptance-established-v1.json) | 5 pass, 2 not tested | Deployed carriage and independent implementations |
| [Client-only onboarding](evidence/acceptance-onboarding.json) · [report](evidence/reports/acceptance-onboarding.json) | 9 pass, 2 not tested | Deployed carriage and independent implementations |
| [Joined service answers](evidence/acceptance-joined-service.json) · [report](evidence/reports/acceptance-joined-service.json) | 6 pass, 2 not tested | Independent client/service implementations and deployed carriage |
| [Signed quorum lifecycle](evidence/acceptance-quorum-signed.json) · [report](evidence/reports/acceptance-quorum-signed.json) | 8 pass, 3 not tested | Independent peers, deployed carriage and independent security review |

The eight reports total 55 passed cases, 20 not-tested cases and zero failures. All eight retain their unavailable scenarios. Each manifest links cases to requirements and hashes its declared sources. Development mode permits explicitly untested scenarios; `--require-complete` fails for all eight. None is certification. Each report covers its named profile/version, not every newer experiment. In particular, the ordinary-mail onboarding manifest does not include the separate optional human-comparison checks.

The [adoption chapter](adoption.md#acceptance-tools-and-interoperability-program) explains how to reproduce these reports and contribute client or server adapters.

The older button manifest does not execute the newer joined service-control tests. Its untested endpoint-submission case remains visible even though separate local signed-SMTP and HTTPS evidence is recorded above.

## Integrated stages and limits

| Stage | Executable evidence | Remaining boundary |
| --- | --- | --- |
| Contributions and references | Joined protected questions, answers, reactions/withdrawals, exact references and separately authorized ordinary copies | Remaining operation bindings, public service authority and independent clients; general forms are not part of v1 |
| Attachments and rich presentation | Signed admission, protected MIME, scoped images, deliberate downloads, worker limits and isolated rendering | Broader legacy layouts, decoder fidelity, additional platforms and native accessibility |
| Identity and discovery | Signed state proofs, durable pins/transitions, ordinary-mail onboarding, configured HTTPS exchange, optional human comparison and local own-device coordination | Provider-certified ownership, deployed pairing/account synchronization and public provider credential/discovery bindings; local pairing, native service authorization and managed restoration have separate evidence above |
| Admission and sending | Initial multi-device rosters, separate established Welcome delivery, delayed admission, durable recipient-specific submission and exact-byte retry | Deployed transport integration and remaining certified membership lifecycle paths; managed restore uses fresh authority rather than old checkpoints |
| Receiving and group controls | Instance-qualified reception, retained-epoch processing, removal/rejoin, pending-effect holds and atomic membership remediation | Deployed mailbox synchronization, safe distributed ordering and legacy consumed-key recovery |
| Service answers | Signed SMTP question → accepted control → deliberate button → HTTPS effect/receipt; exact retry, credential renewal, revocation holds and lost-response reconciliation | Production account integration for the selected native authorization/link profile, general external effects, certificate-status backend integration and independent interoperability |
| Hosted fallback | Configured message/question disclosure, notification, observer replies, expiry and durable retries | Production authorization, browser-code trust and deployed lifecycle validation |
| Legacy reading | Source-preserving plain/HTML views, interleaved replies, attributed blockquotes and synthetic localized labels | Broader real-client/localized corpora, client-store integration and native accessibility |

The sender checks include signed device revocation before a socket opens and a same-epoch incoming message advancing the shared checkpoint without invalidating prepared ciphertext. Neither establishes a global revocation cutoff or recalls already transmitted content.

Configured group ordering uses a designated writer. Separate Commit and Welcome deliveries, fresh-package rejoin and atomic remediation have local evidence. Recovery installs only the final accepted state and requires its explicit past-secret deletion policy; intermediate states cannot authorize new effects. These checks do not establish distributed consensus, writer succession, physical secret erasure or safe backup restoration. The separate eleven-case recovery run covers automatic retrieval from the configured mailbox spool. The older full-suite checkpoint does not establish coverage of later integration changes; current verification status is recorded above.

No deployed mail provider or ordinary email client participated in these local checks. Preview inspection establishes generated structure and direct access to the independent draft, not production publication or complete visual/accessibility validation.

## Outstanding acceptance evidence

- Close the applicable standards, updates, errata, normative-reference and registry audit with explicit section dispositions.
- Complete the enclosing wire/MIME contracts and registration proposals, with validated examples.
- Complete the selected security lifecycle, downgrade handling, device changes, group ordering/recovery and interoperable vectors.
- Exercise discovery under first contact, offline delivery, replay, key change and mixed-client mailbox access.
- Validate the defined HTML/CSS profile, resource isolation, accessibility and broader legacy reconstruction in a usable client.
- Complete authorized service effects and hosted-access tests covering credentials, scanners, expiry, revocation and reply attribution.
- Exchange the supported profiles between two independent implementations over actual email infrastructure.
- Finish repository review, committed dependency pins, delivery gates and any authorized publication steps.

The following security scenarios remain acceptance requirements. Where a local experiment covers part of a scenario, that does not establish the complete case.

## Group key-transition evidence

An MLS binding must demonstrate rejection of an UpdatePath with an incorrect encrypted-secret count, incorrect recipient ordering, mismatched derived public keys or a parent-hash mismatch. It must also demonstrate that newly added leaves receive state through the specified admission flow rather than being accidentally included in path-secret encryption intended for existing members.

State installation and deletion tests must cover interruption between validating a transition, persisting the new state and retiring superseded key material. A successful tree-hash calculation alone is insufficient: current-state agreement and authenticated provenance of parent keys are separate checks. Tests must distinguish delayed-message retention explicitly permitted by the selected profile from unintended retention of replaced node keys and intermediate derivation secrets.

These are required test cases derived from the RFC9420 Sections 7.5–7.9 review, not completed implementation evidence. The selected implementation and profile must establish the exact acceptance, persistence and deletion behavior.


## Commit processing and delayed dependencies

The group implementation must demonstrate that a commit failing its final confirmation check does not install its provisional membership, extensions or keys as the current state. Cases must cover missing referenced proposals, unavailable pre-shared keys, conflicting proposals, duplicate client additions, unauthorized additions and required update paths omitted from a commit. A missing dependency must not be replaced with guessed state.

Tests must distinguish the required application order from proposal arrival order: configuration changes apply before membership operations, and ordered additions and pre-shared keys retain their specified order. A receiver must not reject an otherwise valid commit merely because it omits a proposal that the receiver saw but the committer may not have received. Any retry of an omitted proposal must use the current epoch and pass authorization again.

A member that observes valid MLS proposals must follow RFC9420 Section 12.4's Commit-before-application rule; the selected transport's treatment of standalone proposals and inline Commit candidates must be stated separately. A removed member must stop sending. A future capability offering reinitialization must stop new sends in the old group; the current selected profiles hold unsupported ReInit operations. Welcome admission has separate validation because a new member cannot verify the prior epoch's Commit directly. The [established invitation experiment](evidence/README.md#durable-established-welcome-delivery) has local admission and durable delivery evidence. Those checks do not establish independent-client conformance or every proposal-observation case.


## Bounded out-of-order decryption

The [retention contract](group-conversations.md#delayed-decryption-and-retained-secrets) requires separate elapsed-time, storage/count and forward-generation bounds. The [configured retention experiment](evidence/README.md#bounded-secret-retention-and-delayed-application-delivery) tests actual library age, count and generation behavior, including rejection of an extreme jump without consuming an available message. A conformance run must state its settings and exercise each bound independently. Authentication does not make excessive derivation work safe.

Padding tests must count the final transport representation against message-size limits. Metadata tests must distinguish encrypted sender data from visible group identifiers, epochs, message lengths and ordinary mail envelope fields. No sender-anonymity claim follows merely from using MLS PrivateMessage. These additional padding and metadata cases follow RFC9420 Sections 15–16; the retention results do not establish their complete coverage.


### Replay across encryption generations

A conforming security implementation must exercise an insider replay fixture in which the same signed application event is re-encrypted under a fresh MLS generation. Authentication may succeed, but the original action must execute only once. A conflicting authenticated payload with the same event identifier must enter collision handling rather than replace the original. Repeat the replay after normal message-history pruning: deleting displayed history must not silently erase the protection against executing the action again. Current-epoch reception has local replay and authenticated-collision evidence. Replay after history pruning and complete action-effect integration remain required.


### Protected reply fields

Header-protection fixtures must include an encrypted message whose outer Cc and Reply-To are changed to an attacker address for which the client already has a key. Neither reply nor reply-all may add that address. Repeat with a From mismatch that triggers the outer-address display exception: the displayed value must not become the reply authority.

A confidential subject must remain confidential after automatic reply-prefix insertion and after a user edits only part of it. Repeat with a local policy that normally leaves that field visible and with confidentiality inherited only from the referenced message. Verify the actual serialized outer headers, not merely the compose preview. These are required fixtures, not a claim that a working encrypted client has passed them.


The [partial RFC9788 vector experiment](audits/header-vector-checks.md) demonstrates why fixture extraction must preserve trailing whitespace: the literal text rendition of its detached-signature baseline fails verification, while a separately recorded one-space trial succeeds. This experiment does not establish certificate trust or validate a header-protection implementation.


### Embedded encrypted content

A rendering fixture must place an encrypted MIME subtree between attacker-controlled unencrypted parts. After decryption, the plaintext must remain in a distinct content container, must not be concatenated into surrounding HTML, and must not upgrade the outer message's status. Generating a reply must not extract that plaintext into quoted or attributed text. Repeat with an inline armored block and with a forwarded message that carries its own signature. A verified attached message must not authenticate the enclosing message or its sender.


### Private draft and retry boundaries

Verify that adding a recipient does not add that recipient to the draft's encryption audience. A draft-sync artifact replayed at a message or action endpoint must not become a sent contribution. After an interrupted send, retry must use the correct recipient delivery object rather than the sender-only archive representation; changing the archive's storage format must not change the wire delivery policy.


### Delegated cryptographic results

Inject a message header that resembles a provider verification result and confirm that it cannot affect endpoint security status. Replay an authenticated result against different message bytes and different MIME-layer boundaries; both substitutions must be rejected. Exercise a submission proxy without the original compose context and confirm that it cannot silently choose plaintext delivery for protected quotations. These are required fixtures; no proxy implementation is certified by this document.

### Joined question, button answer and ordinary reply

The [joined local conversation experiment](evidence/README.md#joined-question-and-ordinary-reply) connects browser authoring, durable actions, actual MLS applications, loopback SMTP, authenticated receive and conversation rendering. Its focused cases include delayed history at a third observer, restart, exact retries and a real signed removal of a device's send authority. A separate authorized question copy and ordinary reply preserve their actual protection status. These results cover one configured implementation; independent clients and provider accounts must still repeat the scenario.
