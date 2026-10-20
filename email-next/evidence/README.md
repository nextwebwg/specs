---
title: Local implementation experiments
sectionNav: true
---

# Local implementation experiments

These components exercise selected Email Next contracts. Start with the [offline acceptance report](#offline-acceptance-report) for runnable button fixtures, the [adoption chapter](../adoption.md) for client and server integration paths, and the [validation record](../validation.md) for coverage. No complete client or provider adapter is included.

## Run the integrated checks

The repository's `pnpm verify:pr` gate compiles the specifications and runs JavaScript tests. Python, Rust and browser evidence require the additional commands below; a passing repository gate alone does not cover them. The [validation record](../validation.md) identifies the tool versions used for the recorded results.

Install `requirements-experiments.txt` into an isolated Python environment. Reuse that environment and one external Cargo target directory for repeated checks. Node must be available on the command path. The HTML comparison tests also require parse5 8.0.1; point `EMAIL_NEXT_PARSE5_MODULE` to its installed `dist/index.js` file URL. A missing adapter produces skipped tests, which are not complete integration evidence.

From the specification repository, with the absolute paths adjusted to existing local installations:

```sh
python -m pip install -r email-next/evidence/requirements-experiments.txt
CARGO_TARGET_DIR=/absolute/path/shared-target cargo build --locked \
  --manifest-path email-next/evidence/mls-smoke/Cargo.toml --bins
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/shared-target/debug \
EMAIL_NEXT_PARSE5_MODULE=file:///absolute/path/parse5/dist/index.js \
python -m unittest discover -s email-next/evidence -p 'test_*.py'
CARGO_TARGET_DIR=/absolute/path/shared-target cargo test --locked \
  --manifest-path email-next/evidence/mls-smoke/Cargo.toml
```

`python` above is the isolated environment's interpreter. If it has a different executable name, set `EMAIL_NEXT_PYTHON` for the Rust test's Python bridge. The build must finish successfully before starting tests that call its workers. Keep private runtime checkpoints out of logs and source control.

Run the [browser checks](#isolated-browser-rendering) separately with the configured Python interpreter and an existing Playwright installation. One browser runner is sufficient; do not infer screen-reader or native zoom support from its automated results. The [acceptance reports](#offline-acceptance-report) select smaller requirement-linked case sets and retain untested deployment scenarios explicitly.

## Answer-state experiment

This small executable model explores the answer replacement and withdrawal graph in [Interaction state and conflicts](../interaction-state.md). It is specification evidence, not a mail client or a production implementation.

Run `node --test email-next/evidence/answer-state.test.mjs` from the specs repository. Fourteen tests cover duplicates, concurrent answers, explicit conflict resolution, missing dependencies, withdrawals, cycles, revision scope, author scope and conflicting authenticated identities. Eleven scenarios enumerate every permutation of their supplied delivery sequence. The result is identical for those permutations.

Inputs deliberately stand in for records that have already passed authentication, form schema and capability checks. `fixtureIdentity` is a fixture assertion that two authenticated records are equal; it is **not** a hash, canonical serialization or an acceptable substitute for checking signed bytes. Changing the payload while dishonestly retaining this assertion is outside this model's input contract.

The model recomputes from an in-memory event set. It does not implement persistent deduplication, atomic storage, notification delivery, form revision validation, identity continuity, key revocation, external effects or resource limits. Its recursive graph traversal is unsuitable for untrusted production inputs without bounded processing. These tests demonstrate the listed finite cases, not a proof of convergence for every graph or independent implementation interoperability.

The specification must distinguish reversible local views from irreversible effects. Recomputing a view after an identity conflict can remove authorized attribution, but cannot undo mail already sent or external actions already performed. This experiment performs no external effects.

## Legacy quotation experiment

`legacy-quotes.mjs` maps fixed-line decoded plain text into visible spans and repeated-quotation candidates. Nine tests cover interleaved answers, edited quotes, unmarked duplicates, ambiguous matches, nested and localized markers, signature-like answers, blank quotes and line endings. Every case verifies that the source lines remain present in their original order.

Run `node --test email-next/evidence/legacy-quotes.test.mjs`. The experiment only accepts explicit earlier-message candidates supplied by its caller. It does not discover threads, authenticate authors, parse MIME, process format=flowed, sanitize HTML, or render an accessible UI. It removes one optional space after a run of quote markers solely for candidate comparison. It does not normalize case, Unicode, trailing whitespace or wording. It collapses no ambiguous or nested quote.

Source line arrays preserve text content, not original CRLF bytes. A real client must separately retain the original message. Exact text repetition is display evidence, never proof of authorship. Full legacy reconstruction remains unfinished.

## Flowed-text interpretation experiment

`flowed-text.mjs` interprets decoded plain text under the RFC3676 Format and DelSp parameters. Twelve tests exercise default parameters, joining, deletion of exactly one flow-marker space, Japanese text, quote detection before unstuffing, malformed depth transitions, signature boundaries, source-line mapping and end-of-body behavior. Run `node --test email-next/evidence/flowed-text.test.mjs`.

This is a display transformation, not a MIME parser or signature canonicalizer. It accepts Unicode text after transfer and character decoding. It preserves source-line indices and reports malformed flow boundaries. It accepts CRLF, LF and CR as local input separators; conforming wire generation still uses CRLF. Empty input produces no lines, and a terminal separator closes a line without creating an extra empty line.

The experiment does not generate flowed messages, implement Unicode line breaking or bidirectional layout, validate all wire grammar, impose production resource limits, or authenticate the input. Its output must not be passed through the fixed-line quotation detector as though reconstructed text were original quote syntax: a space-stuffed literal greater-than character remains content. A combined renderer must carry the parsed quote-depth metadata alongside source mappings.

These finite tests provide evidence for the listed decoding cases. The separate [conversation demo](#inspectable-legacy-conversation-demo) joins these helpers to a local reader; broad HTML/client coverage and independent-client testing remain outstanding.

## Readable MIME fixtures

`examples/question.eml` and `examples/answer.eml` demonstrate an ordinary question and reply with equivalent plain-text and HTML meaning. They preserve an unanswered optional location field and use ordinary Message-ID, In-Reply-To and References fields. They are unencrypted and have no structured event part.

Run `python3 email-next/evidence/readable_examples.py` from the specs repository. Two standard-library tests check both fixtures for parser defects, CRLF line endings, SMTP line lengths, alternative ordering, UTF-8 declarations, expected visible facts, absence of active form/script/resource elements, and correct reply targeting. This fixture-specific check is not a general HTML sanitizer, schema validator or independent mail-client test. It is an additional Python check, separate from the Node-based verify:inner gate.

## SMTP size accounting experiment

`smtp-size.mjs` counts the final encoded message octets separately from DATA dot stuffing and its terminating line. Six tests distinguish unknown and zero fixed limits, preserve decimal precision above JavaScript's safe integer range, check exact size boundaries, exercise the question/answer fixtures and reject noncanonical fixture line endings rather than rewriting them. Run `node --test email-next/evidence/smtp-size.test.mjs`.

The functions receive one already parsed SIZE advertisement; they do not parse EHLO replies or validate a complete SMTP transaction. A false `exceedsAdvertisedLimit` result means only that this preflight check did not find a fixed-size barrier. It does not predict acceptance, sufficient storage, downstream limits or per-recipient success. The fixture helper requires a final CRLF, does not implement all MIME or SMTP validity checks, and buffers complete messages in memory. It is not a bounded production transport implementation.

## Published DKIM Ed25519 vector

`dkim-ed25519.test.mjs` exercises the public test keys and signature from RFC 8463 Appendix A using Node's built-in cryptography. Four tests reproduce the published body hash and Ed25519 signature over the DKIM SHA-256 digest, reject direct signing of the canonical headers, and reject a changed covered subject. Run `node --test email-next/evidence/dkim-ed25519.test.mjs`.

The header input is a fixed, manually canonicalized fixture. The body fixture performs only its known double-space reduction. Neither is a general DKIM canonicalizer. The tests do not parse mail, select repeated headers, retrieve DNS keys, evaluate DKIM policy, test RSA, or exercise Ed25519ph. Public example keys must never be used as deployment credentials. This is one published vector checked with one cryptographic implementation, not independent-client interoperability or a complete verifier audit.


## Flowed quotation reconstruction

`flowed-quotes.mjs` combines parsed RFC3676 quotation depth with exact paragraph matching. Run `node --test email-next/evidence/flowed-quotes.test.mjs`. Ten tests cover wrapped questions with inline answers, per-message DelSp, stuffed literal quote markers, malformed boundaries, ambiguous sources, edited blocks, nested/signature-like text and complete source-line coverage.

Only declared flowed input enters this path. Parent messages use their own format parameters. Exactly one matching occurrence of a clean, unquoted parent paragraph sequence permits a repeated-quote classification. Diagnostics, signature separators and ambiguous matches prevent collapsing. Output preserves paragraph metadata and line references; it never reconstructs quote syntax from already unstuffed text.

This is a local display experiment, not thread discovery, authentication, HTML parsing or a complete client. It does not perform collapse in an accessible interface, preserve original wire bytes itself, or impose production processing limits. Independently selected parent inputs remain a caller responsibility.


## Experimental event identifiers

`event-identifiers.mjs` implements the grammar in [Event identifiers](../event-identifiers.md), using Node's cryptographic random generator. Three tests check malformed encodings, generated-value syntax and exact reference shape with a caller-supplied principal validator. Run `node --test email-next/evidence/event-identifiers.test.mjs`.

The helper accepts already parsed objects and cannot detect duplicate names discarded by a JSON parser. It does not validate the complete event, authenticate a principal, prove random-source quality, or implement durable deduplication. The complete wire parser must reject duplicate JSON members before these object-level checks.


## Experimental event decoding

Run `python3 -m unittest discover -s email-next/evidence -p test_event_encoding.py`. Nine tests exercise byte/depth limits, strict UTF-8, duplicate decoded member names at nested levels, scalar-value strings, restricted value types, exact byte preservation, distinct serializations and solidus compatibility. The generator escapes solidus and validates its output; callers must retain its returned bytes for retries. The decoder checks byte size and container depth before tree allocation. It does not implement streaming MIME/cryptographic limits, allocation accounting or operation-schema validation. These Python checks are separate from the Node verification gate.


## Typed form answer validation

> [!note] Exploratory forms, beyond the first version
> The four form experiments below explore validation, exact targets and revision history. They are not required for a first-version client. Start with [button questions and answers](../messages.md#questions-and-answer-buttons) for the selected interaction model.

Run `node --test email-next/evidence/form-values.test.mjs`. Five tests exercise required-field presence with intentional empties, whole-submission rejection, choice membership and uniqueness, duplicate fields, exact member names and empty forms. Inputs must already pass strict event decoding; the referenced field definitions must already be validated and authenticated. The function checks answer values only. It does not validate definition shapes, resolve references, check authorship or commit effects.


## Form operation shapes

Run `node --test email-next/evidence/form-operations.test.mjs`. Seven tests cover all three operation shapes, required and additional members, field/choice uniqueness, scalar-value labels, reference-set equality, empty withdrawals and the distinction between shape validity and resolved answer validity. The principal callback checks profile syntax in this experiment; it does not authenticate a principal. Strict byte decoding and duplicate JSON-member detection must precede this stage. Authority, reference availability, revision graph constraints and persistent effects remain separate checks.


## Exact submission target resolution

Run `node --test email-next/evidence/submission-target.test.mjs`. Seven tests connect operation shape and answer-value validation to a caller-supplied exact revision resolver. They cover missing/conflicted/invalid targets, principal and revision substitution, cross-conversation references, wrong forms, partially invalid answers and preservation of an old choice label when a newer revision is present.

The resolver is assumed to supply prior authentication and revision-graph results. Its output is checked against the requested identity, but this experiment does not create those trust results. Success is named `target-valid`, deliberately distinct from an authorized submission: supersession authority, current author identity, event conflicts, audience policy and atomic effects still require validation. No network request or state mutation occurs.


## Form revision graph

Run `node --test email-next/evidence/form-revisions.test.mjs`. Eight tests cover concurrent revisions and explicit merges, missing parents, cross-author changes, field removal/reintroduction, cycles, competing initial definitions, exact-byte conflicts and independent author namespaces. The supplied concurrent cases enumerate every delivery order.

Inputs stand for strictly decoded, cryptographically authenticated records. The caller must bind each operation to its exact `octets`; the model does not verify that binding or authenticate a principal. The callback validates the fixture principal namespace only. Multiple initial definitions under the same author/form identity remain ambiguous. Field-type history propagates through validated predecessor branches even when a field is absent in an intermediate revision.

The implementation recomputes an in-memory graph and is not bounded against hostile graph size or depth. It performs no storage transaction, signature verification, device authorization or external effect. Its output can supply the earlier revision-result assumption in the target experiment, but no integrated secure client is claimed.


## Single-use package allocation

Run `node --test email-next/evidence/keypackage-allocation.test.mjs`. Six tests cover allocation retries, distinct request scopes, no republication after allocation, stable depletion results, immutable returned results and device/profile pool isolation. The pool is scoped to one target device and security profile.

This is synchronous in-memory transition evidence, not a network service or cryptographic package validator. It assumes authenticated request context and validated package references. It has no crash-safe transaction, expiry, rate limit, cross-process concurrency or Welcome processing. Its unbounded records are unsuitable for production deployment. Those requirements remain explicit in the [security profile](../security-profile.md#single-use-admission-packages).


## Durable package allocation

Run `python3 -m unittest discover -s email-next/evidence -p test_package_store.py`. Seven tests exercise SQLite allocation across reopened connections, concurrent distinct and duplicate requests, device isolation, blocked republication, injected transaction failure, and process exit after commit before a response. The last case verifies that a retry retrieves the committed allocation.

The store uses an immediate transaction to serialize allocation, persists the request result before returning it, and enforces unique package allocation. A failed uncommitted transaction may leave its package available because no allocation was returned. There is no operation to recycle an allocated package. Tests use temporary databases and independent connections; they do not simulate disk corruption, power loss, distributed replication or a compromised provider.

The experiment stores package references only and assumes validated package material and authenticated request context. It is not an endpoint service: it lacks credentials, admission validation, expiry, quotas, migration, backup reconciliation and production resource controls. A durable local allocation is not proof that the recipient accepted a Welcome or that the sender may add that device.


## Admission lifetime decisions

Run `node --test email-next/evidence/package-lifetime.test.mjs`. Six tests cover inclusive boundaries, definitely early/expired material, uncertain clocks, the experimental seven-day maximum, unsigned 64-bit bounds and missing time evidence. Inputs are BigInts from authenticated protocol fields; JSON numbers are not used.

The function does not establish time accuracy, parse or authenticate a KeyPackage, process Welcome, enforce deletion or implement storage expiry. Its result is one admission prerequisite, not authorization. The seven-day bound is an explicit draft parameter recorded in the security profile, not a property guaranteed by MLS.

## Inline CSS declaration filtering

Install `requirements-css.txt` in an isolated Python environment, then run `python -m unittest discover -s email-next/evidence -p test_css_profile.py`. Eleven tests cover the presentation profile's property/value allowlist, active values and layout escape properties, escaped property names, last-valid declaration selection, important declarations, literal numeric spellings, comment handling, parser recovery and rebuilding output. The experiment uses tinycss2 1.4.0's CSS declaration parser and emits newly constructed declarations; it never returns original style text. Escaped keyword values are decoded before allowlist comparison. Escaped property names and nonliteral numeric spellings are rejected.

This is only a declaration filter. It does not parse or sanitize HTML, enforce resource limits, prevent oversized message trees, establish browser containment, test accessibility or validate layout across engines. Its eleven finite tests are not security certification. Python checks remain separate from the Node verification gate. Parser documentation: [tinycss2 API reference](https://doc.courtbouillon.org/tinycss2/stable/api_reference.html).


## Contribution envelope context

Run `node --test email-next/evidence/event-envelope.test.mjs`. Six tests cover exact required members, unsupported purposes/versions, author membership, audience uniqueness, order-independent audience comparison and context substitutions. The operation validator is reused rather than duplicated.

Inputs must already pass strict JSON byte decoding. The principal callback checks profile syntax only. The supplied verified context is a trusted fixture assumption: the experiment neither authenticates bytes nor creates a secure MLS binding. Its success result is context-matched, not authorized. It performs no reference resolution, replay persistence or external effects. The envelope covers form and text-message operations; other contribution kinds remain schema work.


## Text-message operations

Run `node --test email-next/evidence/message-operation.test.mjs`. Six tests cover the common envelope, literal Unicode text, exact shape, missing/conflicted targets, cross-conversation rejection and complete reference identity. The resolver receives already authenticated records supplied by its caller. The experiment performs no network fetch, rendering, cryptography or persistent deduplication; shape validation must precede target resolution. An unresolved target does not suppress the received text or authorize a guessed attribution.


## Serialized event pipeline

Run `python3 -m unittest discover -s email-next/evidence -p test_wire_pipeline.py` with Node available on PATH. Eight integration tests send actual UTF-8 event bytes through the strict Python decoder, then pass the decoded value to the JavaScript envelope and operation validators. They cover message/form/attachment/edit records, exact edit references, duplicate predecessor rejection, canonical manifest lengths, duplicate decoded names before schema validation, valid JSON with invalid event structure, and equal parsed values whose original wire bytes remain distinct.

The adapter reserializes only the decoded value for a test subprocess; that intermediate serialization is never used as authenticated content. The original octets remain separately retained. The serialized pipeline now uses the selected enp0 account encoding and its real spelling validator. The identifiers are test values with no authenticated mailbox or key bindings. These checks integrate parsing and schema stages, but provide no encryption, signature verification, MIME transport, authorization, durable replay handling or independent implementation interoperability.


## Readable contribution projections

Run `node --test email-next/evidence/readable-projection.test.mjs`. Seven tests cover withdrawal wording, inert escaping, message newlines, form labels and choices, intentionally empty versus absent answers, exact-revision choice ordering, missing/conflicted/substituted references and whole-projection rejection for invalid answers. The output is a candidate plain-text/HTML pair with matching text; it performs no transmission.

The revision resolver must already provide authenticated, graph-validated records in the existing submission-target experiment's `id` representation. Fixture success does not authenticate that resolver. The generator does not implement MIME, cryptographic alternative binding, every operation kind, HTML parsing, visual accessibility checks, legacy-client interoperability or limits on expanded output. Labels remain author text and must not be presented as trusted client status. It is specification evidence, not a production fallback renderer.


## Withdrawal targets

Run `node --test email-next/evidence/withdrawal-target.test.mjs`. Five tests check exact form/submission references, author and conversation scope, substituted records, unresolved states and order-independent aggregate outcomes. The readable-projection test adds a withdrawal fallback that names the responses and does not claim that history or external actions have been undone.

The resolver must supply already authenticated and semantically validated records, including valid submission answers and prior graph authority. This experiment rechecks reference and operation relationships; it does not create those trust results, authenticate a device, traverse all history, commit state or undo effects. Success is targets-matched, not an authorization result.


## Complete-resource assembly

Run `node --test email-next/evidence/resource-assembly.test.mjs`. Eight tests cover processing limits, out-of-order chunks, duplicate/overlapping bytes, gaps, conflicting overlaps, digest mismatch, invalid ranges, a caller-supplied size ceiling, empty resources and a split UTF-8 sequence. No partial content is returned on failure or incomplete coverage.

The expected length and SHA256 digest are trusted fixture inputs, not authenticated by this module. This is an in-memory assembly model with two byte arrays proportional to resource size. It requires explicit caller limits for final bytes, chunk count and aggregate input bytes before allocation and copying. It does not implement transport-level buffering limits, decrypt content, verify a signed manifest, persist partial downloads or certify media decoders. The local limits passed by a caller are not specification-wide attachment limits. Repeated overlapping bytes count again toward the input budget; zero-length chunks still count toward the chunk budget. Completion proves equality to the supplied fixture expectation, not authorship or content safety.

## Resource manifest boundary

Run `node --test email-next/evidence/resource-manifest.test.mjs`. Five tests cover canonical unsigned decimal lengths, uniqueness, strict digest spelling, unknown members, missing resources, exact conversion after local bounds, and manifest-to-assembly byte validation. The unsigned 64-bit wire range is a proposed encoding choice, not a promised attachment capacity.

The caller still supplies the manifest without cryptographic verification. A shape-valid or bounded result is not authentication. Complete operation composition, encrypted MIME transport and media-role binding remain unfinished; this experiment does not enable structured-resource capability advertisement.

## Bundled-resource binding

Run `node --test email-next/evidence/resource-binding.test.mjs`. Five tests exercise single-part binding, duplicate ambiguity even for identical bytes, event separation, canonical identifier comparison, changed/truncated bytes, unknown entries and local limits. This composes the manifest and assembly experiments instead of accepting a MIME Content-ID match as sufficient integrity evidence.

Inputs are already parsed, transfer-decoded parts supplied from one compound scope. The fixture authenticates neither that scope nor its manifest. There is no MIME parser, decoder, decryption, media execution or network fallback in this model. A production adapter must enforce those boundaries before calling it and bound its MIME part inventory independently.

## Attachment metadata

Run `node --test email-next/evidence/attachment-metadata.test.mjs`. Four tests cover exact manifest references, duplicate rejection, strict media-type spelling, scalar display strings and exact members. The validator intentionally accepts path-like and markup-like names as inert author data; it does not create safe filesystem names, sanitize a user interface, authenticate an event or decode a file. Those must be enforced at their actual use sites.

## Attachment-message composition

Run `node --test email-next/evidence/attachment-operation.test.mjs`. Three integration tests cover the common contribution envelope, inert readable metadata, complete manifest use, nonempty attachment lists, exact operation members and rejection of an implicit upgrade to an ordinary message. Existing resource tests separately check lookup and byte integrity. The projection does not load or verify resource bytes and explicitly avoids asserting file availability. MIME generation, cryptographic verification and a client attachment UI remain unimplemented.

## MIME resource decoding

Run `python3 -m unittest discover -s email-next/evidence -p test_mime_resources.py`. Six tests parse actual MIME bytes with Python's standard email parser, decode base64, reject repeated resource headers and malformed/truncated containers, enforce caller limits, and feed decoded parts into the JavaScript manifest/binding/assembly modules. The integration fixture distinguishes original bytes from a same-length altered resource by digest failure.

This experiment accepts only a flat multipart/mixed resource container with canonical generated Content-IDs and canonical base64 (apart from MIME folding whitespace). It is not the complete contribution packaging format or a general legacy MIME receiver. Its stricter base64 fixture rule must not be mistaken for a reinterpretation of MIME's legacy receiving rules. It rejects nested containers rather than traversing them. Wire size is checked before parsing; the standard parser builds the bounded input tree before part-count enforcement, and decoded output is checked after each bounded part decode. Production streaming, depth enforcement during parsing and precise allocation accounting are not implemented.

The subprocess bridge is a local test harness accepting trusted test data; it is not a network endpoint. Manifest authenticity and selection of the decrypted compound are caller assumptions. No cryptographic or live-mail interoperability claim follows from these tests.

## Complete attachment packaging fixture

Run `python3 -m unittest discover -s email-next/evidence -p test_mime_package.py`. Fourteen tests compose the strict event encoder, JavaScript schema/readable projection, Python MIME generation and parsing, and the selected resource-scope decoder. The generated layout is multipart/mixed containing a multipart/alternative contribution followed by independent attachments. Alternatives are text/plain, text/html and the candidate application/vnd.threadlabs.email-next-event+json carrier. Tests verify exact structured-event octets, binary resource octets, Unicode filename recovery, alternative ordering, readable Unicode text and refusal of missing, extra or modified input resources.

The candidate event carrier is only a local experiment; it does not register an Email Next media type or advertise protocol support. The generator assumes operation validation and projection have already succeeded, as exercised by the harness. Its API is not an untrusted-input boundary. Readable text serialization may add normal MIME line endings; authenticated structured-event bytes are separately retained exactly. The incoming fixture inspector requires the exact mixed/alternative layout, one Content-Type per part and exactly three ordered alternatives. It rejects generic JSON and unrelated suffix types, all event media parameters, duplicate alternatives and nested resource substitutions. Type-name case differences preserve the same selection. It retains original structured bytes and budgets aggregate decoded content. It then repackages the selected resource scope for the resource-only decoder. This is a strict generated-profile selector, not a general-purpose legacy message selector.

No mail is sent. No encryption wrapper, signature, recipient policy, real-client rendering, independent MIME implementation or transport gateway is exercised. Final media registration, protected-container integration and arbitrary legacy-layout selection remain required work.

The incoming attachment pipeline now feeds selected event values into the JavaScript envelope/operation validator and decoded parts into manifest binding. Tests cover an invalid manifest length, same-length substituted resource bytes and a replaced neighboring HTML alternative. The regenerated view comes from the structured event, not the replaced HTML. The harness reports validated-unverified explicitly: neither schema success nor matching resource hashes supplies cryptographic authority. Its JSON subprocess transport is only test plumbing and does not replace the separately retained original event bytes.

A filename-projection regression covers CR, LF, NUL, DEL and an empty name. The MIME filename uses the defined header projection while the extracted structured event retains the original display name. This was added after direct probes showed that raw newline names failed header serialization and NUL could be emitted. The projection is not a filesystem sanitization claim.

The composite-file regression packages a nested multipart email under message/rfc822, message/global and multipart/mixed claimed types. The outer attachment stays application/octet-stream, the structured description retains the original type, and exact file bytes reach manifest verification without exposing a nested resource scope. Deliberate viewing and nested-document authentication are not implemented.

The incoming inventory regression appends an unlisted resource and duplicates a listed part. The harness reports unbound part indices separately, excludes them from the structured attachment results, and marks repeated matches ambiguous. Inventory matching releases no bytes and supplies no cryptographic authority. Original MIME remains the evidence for raw inspection.

## Presentation default styles

`presentation-defaults.css` records proposed client-owned typography, spacing, native semantic presentation and system colors for an isolated sanitized message document. It is not sender CSS and must not be accepted through the inline declaration allowlist. No browser or accessibility pass is claimed for this file. An implementation still needs an inert HTML parser, sanitizer, isolated host, enforced final containment/accessibility overrides and labeled scroll regions before visual conformance can be tested.

## Inert HTML element projection

Install requirements-html.txt in an isolated environment, then run `python -m unittest discover -s email-next/evidence -p test_html_tree.py`. Five tests cover fresh filtered node data, allowed structure, prohibited/foreign subtree removal with surrounding text retained, unknown-wrapper removal, HTML table-body insertion, invalid UTF-8 and caller limits. The experiment uses html5lib 1.1 with namespaces and scripting disabled, following its [document parsing API](https://html5lib.readthedocs.io/en/latest/). It constructs no browser DOM and has no resource loader.

This is a partial tree-and-attribute stage: navigation and image sources remain omitted from live attributes; language labels are preserved without registry certification. Its output must not be advertised or deployed as a complete profile sanitizer. The remaining permitted attributes, image resolution, serialization, browser differential fixtures and accessibility are unfinished. Input bytes are bounded before parsing; node/depth bounds are checked after tree construction, not as streaming parser limits. The pinned parser is a reproducible experiment dependency, not certification against a current HTML Standard snapshot.

The partial attribute stage adds four tests (nine HTML-stage tests in total). It preserves inert labels and direction, normalizes bounded numeric attributes, handles boolean reversed by presence, and passes HTML-decoded style strings through the existing CSS parser/filter. Later integration retains link destinations and image sources as inert data, and preserves received language labels as described below. Navigation and image loading remain absent from the preview. Image decoding and client-owned resource handling still preclude conforming image rendering.

Four additional encoding tests bring the HTML-stage total to thirteen. The adapter requires an explicit UTF-8 MIME charset, rejects invalid UTF-8 before parsing, records conflicting or unsupported meta forms, and preserves a nonconformance diagnostic when duplicate source attributes would otherwise be collapsed by tree construction. It never reinterprets Unicode through an HTML-supplied encoding. A consistent encodingState is not permission to activate content; the rest of the incomplete renderer still applies.

## Navigation URL validation

Run `node --test email-next/evidence/navigation-url.test.mjs` with Node 24.20.0. Ten tests cover absolute HTTP/HTTPS destinations, normalization, Unicode and numeric hosts, IPv6, percent encoding, relative and executable schemes, credentials, controls and malformed addresses. The validator returns destination data without networking; the isolated browser host presents that parsed destination before deliberate navigation.

Run `EMAIL_NEXT_PLAYWRIGHT_MODULE=<absolute Playwright module> node email-next/evidence/navigation-browser-test.mjs` to compare 31 focused inputs in Node and Chromium. The checked runtimes are Node 24.20.0 and Chromium 153.0.8010.12. Chromium accepted a leading-zero decimal component inside IPv6 that the URL Standard rejects; an explicit pre-parser rejection now produces the required result in both runtimes. These checks do not establish complete URL conformance, phishing protection or DNS policy.


## HTML navigation integration

Run `python -m unittest discover -s email-next/evidence -p test_html_navigation.py` with the HTML dependencies installed and Node available. Three integration tests connect HTML entity decoding, fresh-tree construction and the JavaScript URL validator. Accepted links produce client-owned destination data; rejected links retain visible text without a destination. Raw candidates, sender targets, tracking ping and event handlers do not enter the output attribute map. Together with the existing tree, attribute and encoding suites, sixteen Python HTML-stage tests pass.

The bridge accepts only the already bounded projection format. It is not a generic untrusted JSON sanitizer or browser host. Rendering, keyboard accessibility, actual navigation/referrer enforcement, resource resolution and cryptographic provenance remain unimplemented.

## Fresh HTML serialization

Run `python -m unittest discover -s email-next/evidence -p test_html_serialize.py` with the HTML dependencies installed. Four tests cover text/attribute injection escaping, filtered table-structure stability after another HTML parse, exclusion of network-bearing href/src attributes in the inert preview, and refusal of unexpected elements/attributes. The HTML-stage suite now has twenty passing Python tests.

The serializer consumes only the internal filtered data tree; it is not an independent sanitizer for arbitrary JSON. Its document wrapper adds a client-owned restrictive CSP and unverified-preview title. Those wrapper metadata are not sender profile content and are outside body equivalence checks. CSP is defense in depth, not proof of browser isolation. The preview intentionally omits active navigation and image loading; those required profile features still need their client-owned handlers and resource pipeline. No browser execution, accessibility or mutation-XSS differential pass is claimed by same-parser round trips.

## Adversarial HTML recovery

Run `python -m unittest discover -s email-next/evidence -p test_html_recovery.py`. Four added tests cover template table-content relocation, noscript recovery, foreign-namespace HTML integration points and a malformed foreign-content reparse fixture. Twenty-four Python HTML-stage tests pass in total.

Direct probes found that removing template/noscript nodes from this parser's repaired tree can leave source content outside them. The experimental adapter now refuses documents retaining either node rather than returning that projection as successful. This is an acknowledged implementation gap: it does not change the required profile or prove comprehensive source-origin tracking. The malformed fixture round trip uses the same parser and is not browser differential or mutation-XSS certification. No production sanitizer claim is made.

## Independent HTML parser probe

`compare-html-parser.mjs` accepts a file URL for a separately installed parse5 8.0.1 dist/index.js. It runs the same template, noscript and foreign-namespace fixtures with scripting disabled and records parser errors plus body text after prohibited-container removal. The local run produced: template → visible; noscript → hiddenvisible with disallowed-content-in-noscript-in-head; foreign → visible.

The template result differs from html5lib 1.1. The noscript result agrees, identifying a profile source-versus-repaired-tree ambiguity rather than a Python-only defect. This three-fixture probe is not an independent renderer implementation or broad parser conformance test. parse5 remains an evaluation dependency in the work directory; the production/evidence pipeline has not yet migrated to it. Its [tree adapter documentation](https://github.com/inikulin/parse5/blob/master/packages/parse5/lib/tree-adapters/default.ts) distinguishes template content from ordinary childNodes, which an integration must preserve.

## parse5 projection adapter

Set EMAIL_NEXT_PARSE5_MODULE to the file URL of a pinned parse5 8.0.1 dist/index.js, then run `python -m unittest discover -s email-next/evidence -p test_parse5_adapter.py`. Four tests passed with that dependency present. They integrate parse5 document construction with the existing Python node, attribute and CSS filters: template table content is removed, foreign descendants stay excluded, duplicate encoding diagnostics survive, and malformed noscript remains explicitly unsupported. Without the configured module these four tests skip; a skipped run is not integration evidence.

The adapter preserves template content as children in its internal interchange solely so resource counting and subtree removal can see it. It retains namespaces and parse-error codes, and never attaches the source tree to a browser. This local subprocess bridge adds buffering and has no production timeout/streaming guarantees. It is an explicitly selected experimental parser path; the default Python parser path remains available with its recorded refusal rule. Full parser migration, source provenance, browser differential tests and the remaining attribute/resource features are unfinished.

The parse5 adapter suite now has six passing tests. Valid body noscript content is removed while surrounding content remains; malformed head noscript recovery is refused using the parser's diagnostic, including with following paragraph and table structures. The default Python parser retains its broader template/noscript refusal. This is a selected profile recovery rule, not a claim that all HTML parser-recovery cases have been audited.

## POP retrieval framing

Run `python -m unittest discover -s email-next/evidence -p test_pop_response.py`. Five tests cover dot unstuffing, complete-message release, empty versus negative replies, pipelined remainders, status-line limits, nontruncation of long body lines and preservation of binary octets without character decoding. This decoder accepts an already buffered input under caller byte limits. It does not implement a streaming socket, authentication, CAPA, mailbox state, deletion, persistence or retry policy.

The attachment packaging suite now has eleven tests: an added integration carries generated MIME through POP multiline framing, then incoming selection/schema/resource checks. Both exact event bytes and resource integrity survive that fixture. This is a local transport representation test, not a live POP server exchange or encrypted delivery demonstration. The primitive's preservation of arbitrary body octets does not declare them conforming Internet message content.

## Account and device identifiers

Run `node --test email-next/evidence/principal-identifiers.test.mjs`. Three tests cover exact account/device domain separation, invalid/unknown spellings, generated encodings and contribution-envelope integration without authentication. Random generation uses the runtime cryptographic source; the tests check format, not statistical randomness or global collision absence. Existing fixtures with short principal labels remain explicit mock-validator tests, not valid new-profile wire examples. Credential binding, mailbox verification, device authorization and continuity remain separate unfinished implementation work.

The serialized event and complete attachment MIME fixtures now use enp0 principal values and the selected identifier validator in all three subprocess bridges. The five strict-wire tests and eleven attachment packaging tests pass after that migration. This replaces the earlier label-only validation in these integrated paths; separate unit models may still inject mock principal validators. Syntactic identity acceptance remains distinct from cryptographic authority.

## MLS credential identity payload

Run `node --test email-next/evidence/credential-identity.test.mjs`. Four tests cover the exact 85-octet BasicCredential identity payload, account/device field ordering, prefix/length/trailing-data rejection and invalid identifier domains. The payload uses selected identifiers but carries no mailbox or authorization claim. This module does not serialize the surrounding MLS Credential, verify a signature or establish the external binding between an account/device pair and its signing key.

## Device-binding signature experiment

Run `node --test email-next/evidence/binding-signature.test.mjs`. Four tests exercise actual Ed25519 signing/verification through the runtime crypto implementation, exact-byte sensitivity, a wrong public key, a signature lacking the application domain context, strict local proof spelling and payload bounds. The test payload is deliberately only a small placeholder record; it is not the completed device-binding schema. Signature-valid is not account authorization, mailbox verification, key continuity or an MLS admission result. No custom cryptographic algorithm is implemented; protocol context construction and complete integration still require review.

## Device-binding record schema

Run `node --test email-next/evidence/device-binding.test.mjs`. Three tests cover first-contact versus state authority shapes, role uniqueness, strict unsigned time spelling, identifier domains and a signed record whose role mutation invalidates the proof. The schema validator checks public-key spelling, not mathematical key validity or possession by itself. The actual proof test uses a generated Ed25519 key. Neither result supplies an authenticated identity-state resolver, mailbox evidence, revocation status or administrative authorization.

## Device possession proof

`binding-possession.test.mjs` adds three tests using generated Ed25519 keys: possession and authorization signatures cannot substitute across domains even under one key; an enrolling authority cannot prove possession of another device's key; and byte or encoding changes fail verification. Together with the four existing binding-signature tests, the targeted run passed seven tests.

The primitive takes exact payload bytes; the fixture is deliberately not a complete binding record. It tests cryptographic separation, not schema parsing, identity ownership, authority resolution, durable enrollment or MLS admission. The specification's acceptance order requires those additional stages before enrollment.

## Identity-state schema

`identity-state.mjs` implements the exact state payload shape in [Identity-state records](../identity-state.md). Four tests cover genesis versus successor structure, ordered unique disjoint roster/revocation lists, strict identifiers and counters, and a successor that removes its own signer. The last case ensures schema parsing does not incorrectly require an authorizer to remain in the proposed roster: authority must be checked against the predecessor.

This validates shape only. It does not resolve a binding, verify state signatures, compare predecessor revisions or roles, transact installation, establish freshness, or recover a branch. These missing stages prevent a schema-valid result from authorizing admission.

## Identity transition policy

`identity-transition.mjs` evaluates ordinary transitions over already authenticated, digest-resolved state and binding objects. Six tests cover an allowed addition, substituted predecessors, a new signer authorizing itself, excessive role grants, missing revocation, last-administrator removal, revocation rollback, unknown targets, expired bindings and unresolved/substituted records. A permitted handoff allows the old signer to remove itself while retaining a new authorized administrator.

`policy-valid` is intentionally not an acceptance result. The input Map asserts digest resolution; this model does not hash or parse original bytes, verify any proof, establish current-state freshness, detect forks against durable history, or perform a transaction. Missing bindings return invalid under this resolved-input contract; a network resolver must separately preserve pending versus rejected evidence before calling it. The supplied time is a trusted fixture instant, not an implemented clock-uncertainty policy.

## Identity-state signatures

`identity-state-proof.test.mjs` adds three tests for a schema-valid state payload: its exact-byte proof and digest change under reserialization; all nine signer/verifier pairings across binding, possession and state domains accept only the matching purpose; changed state bytes, wrong keys and noncanonical proof spellings fail. The combined signature run passed ten tests.

The fixed-purpose public functions share framing and Ed25519 handling internally. They do not accept an arbitrary caller-selected domain. This primitive neither establishes the signer in the predecessor nor validates the referenced binding. It must be connected to strict parsing, authenticated resolution and durable transition installation before acceptance.

## First-contact proof pipeline

`test_genesis_pipeline.py` connects strict UTF-8 JSON decoding to `check-genesis.mjs`, preserving original state and binding bytes. Five tests check a valid claim, substituted proof purposes, reserialization of either payload, duplicate names and malformed UTF-8, and a clock-uncertainty interval that must fit wholly inside binding validity. The generator makes fresh Ed25519 test keys; it does not export private keys.

The internal Python-to-Node bridge carries parsed values beside exact bytes. Only the strict decoder constructs that input; it is not an untrusted transport format. The bridge checks genesis schema, account/device agreement, required administrator roles, the binding digest, possession, self-binding, state signature and the supplied time interval. It returns `claim-valid-unverified`, never enrollment or verified ownership.

It does not check an existing identity pin, competing genesis history, directory authenticity, mailbox evidence, revocation freshness, durable acceptance or MLS admission. The caller must supply those policy stages. This bounded fixture pipeline is not a streaming mail receiver or production authentication service.

## Durable first-contact evidence

`genesis_store.py` runs the strict first-contact pipeline before a SQLite transaction stores the candidate evidence and optionally pins the sole unverified claim. `allow-unverified` and `require-verification` are explicit caller policies; neither is selected as a universal default. A later self-consistent but unlinked claim remains stored and never replaces or suspends an existing pin. Multiple claims observed before any pin leave first contact ambiguous; changing to a permissive policy does not choose among them. Exact retries retain one claim. Invalid proofs are not inserted.

Seven store tests cover retry/reopen persistence, strict policy without a pin, unlinked claims, invalid-proof rejection, concurrent delivery through separate database connections, unresolved first-contact ambiguity after a policy change, and preservation of the original pin after restart with an unlinked claim. The store-only targeted run passed seven tests. Reopening tests ordinary persistence; no forced-crash, disk-loss or backup-rollback test is claimed.

A stored pin is unverified historical evidence, not current permission to send. Changing to a stricter delivery policy must still hold delivery until that policy is satisfied, even when a pin exists. The snapshot result must be checked together with current authority and freshness before any protected action; an authorized successor conflict can still require holding operations. An unrelated self-signed claim cannot impose that hold merely by copying a public identifier. This experiment contains no mailbox-to-principal mapping, independent identity verification, successor-state installation, fork recovery, quotas, secret storage or MLS integration. Its fixture transport is not a public protocol.

## Identity proof bundles

`identity_bundle.py` decodes the selected application carrier and preserves exact embedded bytes. Seven tests cover real genesis proof verification, wrapper reformatting without proof changes, duplicate payloads, account-scope mismatch, base64/proof spelling, nested duplicate JSON names, partial evidence and the aggregate input bound. Carrier decoding checks purpose/version/scope; full state and binding schemas are enforced by the genesis verifier for its supported case.

The carrier is not signed as a whole and does not assert completeness or freshness. The experiment handles one genesis through its verifier; the successor verifier below resolves one explicit predecessor and candidate, while durable successor acceptance remains unfinished. It buffers bounded input and uses the existing internal Python-to-Node proof bridge. No MIME media type has been registered and no live email exchange is claimed.

## Successor proof pipeline

`verify_successor_bundle` connects strict carrier decoding and exact SHA256 references to `check-successor.mjs`. Five tests cover real signatures with unordered records, cryptographically valid excessive role grants, missing dependencies, substituted proof purposes, forged state proofs and an incorrect local anchor. The test generator uses two fresh device keys without exporting their private material.

The accepted predecessor digest is a trusted local input. The verifier does not accept a bundle's claim to be its own trust anchor, re-verify the already accepted history, select the newest state, or install a transition. It requires referenced predecessor bindings by their exact digest, verifies each changed binding under the old state signer and the new device's possession key, and checks the transition policy across the supplied time interval. A retained administrator must cover that entire interval.

A successful result is `transition-valid-uncommitted`. Fork detection, comparison with a durable current head, acceptance transactions, revocation freshness, recovery and MLS membership changes remain required. These tests do not establish independent implementation interoperability or secure handling of a malicious local caller that forges the trusted anchor.

## Durable successor acceptance

`identity_store.py` extends the first-contact evidence store with a current head and retained transition records. The receiver takes its predecessor anchor from a locally pinned genesis or an accepted transition, then verifies the supplied bundle inside a SQLite write transaction before installing it. A candidate cannot nominate an untrusted predecessor as accepted state. Exact previously recorded transitions return stored status without rolling back the head.

Seven tests cover commit/reopen/retry, absence of an accepted genesis, a forged candidate that cannot advance or create a conflict, concurrent authorized successors through separate connections, replay after revocation, authorized record-identifier reuse, and forced child-process exit after database writes but before commit. The interrupted transaction leaves no partial transition and succeeds on retry after reopening. Both authorized branches are retained; the previously installed head remains historical evidence and the conflict flag holds subsequent acceptance. An unlinked genesis remains distinct from an authorized branch conflict.

This is a bounded local experiment. Running the proof subprocess while holding the database write transaction trades throughput for a simple atomic boundary; it is not a production concurrency architecture. The process-exit test does not simulate power loss, restore rollback, distributed replicas, branch repair or an outgoing MLS operation racing with revocation. No freshness service or mailbox verification is supplied. `accepted-unverified` records continuity from an unverified first-contact pin, not verified ownership, current global authority or permission to release history. All fixture bundles supply their dependencies; fetching missing evidence is not implemented.

## Binding validity outcomes

Two additional genesis pipeline/store tests distinguish known expiry and future validity from clock uncertainty, check inclusive validity endpoints, and ensure an expired replay preserves an existing pin without establishing a new one. The targeted genesis suites pass fourteen tests. `not-current` is not a failed signature, revoked identity, plaintext-fallback permission or instruction to erase historical evidence. These results do not supply a trusted clock or current revocation service.

## OpenMLS encrypted exchange

`mls-smoke` pins OpenMLS0.9.1, openmls_basic_credential0.6.0 openmls_rust_crypto0.6.0 and openmls_traits0.6.0, with the resolved dependency graph in Cargo.lock. Run `cargo test --locked --manifest-path email-next/evidence/mls-smoke/Cargo.toml` from the specs repository. The recorded run used Rust1.91.1 and an external build directory; one integration-style unit test passed. Rust checks are separate from verify:inner and the Python suite.

Two independent provider instances create credentials with the selected85-octet identity representation and suite0x0001. The test creates and serializes an admission package, validates its decoded signature and protocol version, serializes/deserializes Welcome and the public ratchet tree, joins the second device, compares epoch authenticators, serializes a protected application message and decrypts exact original bytes, rejects replay, and returns an encrypted reply. Exact decoders reject appended bytes on the admission package, Welcome, public tree and protected message; a changed package signature is rejected before admission. It also checks that the literal payload is absent from the serialized ciphertext; that finite check is not a confidentiality proof.

The tamper case exposed a material integration constraint in the pinned release: after rejecting an altered ciphertext, the same live receiver object rejects the genuine copy with SecretReuseError. Reloading the group from the provider's unchanged storage allows the genuine copy. The test preserves this observation rather than silently treating rejection as mutation-free. Source inspection of the pinned release's processing.rs places the message-secret storage write after successful decrypt_message; this explains the tested decryption-failure path, not every possible failure path. The provider storage here is memory, not a durable database. No universal reload-on-error recovery rule is established.

The lifetime is constructed explicitly: the convenience Lifetime::new function adds a one-hour backward margin, which would exceed the draft's seven-day interval if called with seven days directly. The fixture instead uses a sixty-second past margin and a corresponding reduced future interval. Exact expiry-boundary integration remains to be checked because the library rejects at not_after.

The experiment connects the sender’s generated MLS key to a signed genesis claim and the first-contact store as described below. It does not implement a complete contribution authorization policy, deliver its MIME fixtures through a real mail provider or mailbox, enforce a registered group context, persist secret state across processes, or exchange data with a second MLS implementation. It uses fixed fixture identifiers and never exports private keys. The [official library documentation](https://docs.rs/openmls/0.9.1/openmls/) and the selected crate's source informed API usage; successful compilation is not a security audit of its dependency graph.

## MLS bytes through MIME

`mls_mime.py` packages opaque bytes as a base64 application/octet-stream attachment beside a readable fixture notice, then parses the generated message back into exact bytes. The Rust MLS exchange applies this round trip to KeyPackage, Welcome, public tree, application ciphertext and reply before their respective cryptographic processing. The expanded Rust test passes. Three separate Python tests cover all256 octet values, CRLF preservation, corrupted transfer data, duplicate encoding headers and input bounds.

This fixture uses an explicit expected layout and does not discover protocol roles from arbitrary attachments. It is not the selected final Email Next MIME binding and does not claim that legacy clients hide the attachment. The [registered message/mls type](https://www.iana.org/assignments/media-types/message/mls) is binary; the application profile must reconcile its email carriage with RFC2045/2046 and RFC6532's allowance for newly defined message types to permit transfer encoding. The fixture deliberately makes no claim that this registration already authorizes a particular email encoding.

The Python3 helper uses only its standard library; the Rust test invokes it through EMAIL_NEXT_PYTHON when set, otherwise python3. The loopback SMTP extension below exercises a local transaction. Mailbox delivery, provider transformation, multipart selection beyond this exact fixture, identity-store admission and an independent MLS implementation remain untested.

## Loopback SMTP exchange

`smtp_loopback.py` binds one ephemeral IPv4 loopback listener and receives one message from Python's standard SMTP client. It accepts the narrow EHLO/MAIL/RCPT/DATA/QUIT sequence used by the fixture, removes DATA dot-stuffing and returns accepted message bytes. It closes the connection and joins its receiver thread after each exchange; no external address is contacted or listener intentionally retained. The example.invalid addresses are envelope fixtures, not destinations on the public network.

Three tests cover single-dot and repeated-dot lines, all-octet binary content through MIME and SMTP, and malformed/oversized inputs rejected before listener creation. The Rust MLS test now passes each transported object through MIME generation, this SMTP transaction, MIME parsing and exact cryptographic decoding. That encrypted exchange also passes.

This is not a conforming general-purpose SMTP server, mail relay or delivery oracle. It does not implement STARTTLS, authentication, DNS routing, recipient-specific failures, downstream acceptance, mailbox storage, provider rewrites, reconnect/retry or concurrent SMTP clients. Its parser and resource bounds apply only to the narrow local fixture. Passing it supplies network-framing evidence, not real-provider interoperability.

## Structured contribution over MLS and SMTP

The Rust exchange encrypts the exact UTF-8 `mls-smoke/fixtures/message.json` contribution, carries it through loopback SMTP and MIME, and passes the decrypted bytes plus the credential returned by MLS processing to `mls_contribution.py`. Strict decoding precedes the existing envelope/operation validator and readable projection. The credential's account identifier must equal the contribution principal. A second fully encrypted message with a different claimed author is rejected with sender-mismatch despite successful MLS decryption. The expanded Rust exchange test passes.

This links the MLS-authenticated leaf credential to the event's claimed account; it does not prove that the credential belongs to the intended correspondent. Fixture membership is established directly by the test. The subsequent context and first-contact checks below cover current-epoch conversation/audience consistency and sender-key binding. Successor-state authorization, exact reference authorization and durable application effects remain incomplete. The readable projection is generated internally; no browser UI or automatic reply is exercised.


### Authenticated MLS conversation context

The OpenMLS exchange now includes a required private-use GroupContext extension carrying the candidate context defined in [the security profile](../security-profile.md#authenticated-conversation-context). The bridge obtains the context and roster from the receiving MLS group, strictly decodes the context and checks author, conversation and deduplicated account audience before projection. Four JavaScript tests cover context shape, multi-device audience derivation and mismatch cases. The actual encrypted exchange also rejects wrong-conversation and wrong-audience contributions alongside the existing wrong-author case.

Run `node --test conversation-context.test.mjs` from this directory and the existing locked Cargo test command. This remains a current-epoch experiment with fixture account identifiers, not successor-state authorization, invitation verification or membership policy implementation.


### MLS signing-key binding to first-contact identity

`mls_identity.py` connects the actual sender leaf to the existing strict genesis proof verifier and SQLite first-contact store. The Rust fixture creates the binding and state payloads for its generated Ed25519 device key and signs the three distinct proof domains using that same private key inside Rust. Only public records and signatures cross the process boundary. The helper verifies these proofs and validity, explicitly accepts unverified first contact, retrieves the retained binding under its pinned state digest, and compares the account/device credential and signing key obtained from the receiver's authenticated MLS roster. It also requires the send role.

The exchange asserts successful authorization before sending its structured contribution. Negative cases substitute the other device's signing key, substitute its credential, corrupt the binding authorization proof and evaluate the claim after expiry; all are rejected. The final contribution still undergoes the separate authenticated sender, conversation and audience checks before readable projection.

This fixture creates a fresh temporary identity store for each case. It tests the cryptographic and parsing connection, not retained continuity across sessions, automatic discovery, membership admission, a successor/revocation race or mailbox ownership. A real receiver must use its retained accepted identity history and applicable freshness policy; it cannot create a new first-contact store to bypass an existing pin or conflict. The MLS test does not yet provide that application lifecycle. Its explicit first-contact policy is a test choice, not a universal deployment default.


### MLS removal and delayed ciphertext

The same locked exchange test serializes a removal commit through MIME and loopback SMTP, advances the creator to a one-member epoch, and checks the other device before and after notification. The other device can decrypt delayed old-epoch ciphertext, cannot decrypt new-epoch ciphertext, and becomes inactive after accepting its removal. Its subsequent send attempt fails. See [Applying account changes to an MLS group](../group-conversations.md#applying-account-changes-to-an-mls-group) for the required application boundary and remaining integration work. This fixture supplies no competing-commit ordering or automatic identity-revocation handling.


### Current device authority from retained state

`IdentityStore.check_device` evaluates a send or receive operation against one read-transaction snapshot of the accepted head and its retained binding records. It reports the accepted head and selected binding digest with successful unverified authorization. It holds absent identity, accepted conflicts, missing dependencies, uncertain time and stricter verification policy; it rejects revoked or absent devices, mismatched signing keys and missing operation roles. It does not accept a caller-provided historical state as current.

Four tests exercise first-contact policy and key substitution; enrollment followed by revocation, reopening and replay; an authorized competing branch; and validity at the endpoint, after expiry and across an uncertain interval. The actual MLS first-contact bridge uses this same check after verifying and pinning its signed records. The Rust exchange passes.

The database snapshot ends before this API returns. Its result must not be cached as permission to release later ciphertext. Transport release, concurrent revocation serialization, remote freshness and accepted branch repair remain outside this implementation.


## Message edit targets

Run `node --test email-next/evidence/edit-operation.test.mjs` from the specs repository. Seven tests cover literal replacement text, strict shape, duplicate predecessors, exact root identity, same-author and conversation scope, self-reference, root consistency across edit predecessors, and order-independent pending/conflict/invalid outcomes.

`edit-operation.mjs` checks the candidate object and targets supplied by a trusted resolver. A valid resolver result must already include authentication and dependency-graph validation. These tests do not establish those properties, derive current versions, provide durable effects or bind readable MIME alternatives. The contribution-envelope validator accepts this candidate shape; acceptance alone does not authorize effects.


## Message edit state

Run `node --test email-next/evidence/edit-state.test.mjs`. Ten tests exercise concurrent edits, complete and partial merges, missing predecessors, cycles and their descendants, changed authentication evidence and preservation of known predecessors while a child is pending. Representative input permutations yield the same heads; this is fixture evidence rather than a proof over all graphs.

`edit-state.mjs` evaluates a synchronous immutable snapshot and discovers referenced ancestors. Its resolver supplies previously authenticated records and exact-byte identity conflicts. The evaluator checks edit dependencies and derives current heads without changing records or reply references. It performs no network retrieval, durable commit or external effects. Traversal is iterative: each distinct event is resolved once and dependency edges are processed without recursive calls. A 12,000-version fixture checks this behavior. Memory still grows with the supplied history; optional local record/reference budgets stop traversal with an incomplete result and no partial heads. These budgets are caller settings, not interoperability limits. Resolver cost, total input allocation, durable transactions and resumable processing remain outside the experiment. Each evaluation must use one consistent resolver snapshot. Cross-author, cross-conversation and self-referencing predecessor edges are rejected before ancestor lookup; an invalid edit does not cause resolution of unrelated history.


## Readable edit corrections

Run `node --test email-next/evidence/edit-projection.test.mjs`. Five tests cover envelope acceptance with continued protection-context checks, exact root/predecessor references, HTML escaping, explicit empty replacement text, missing/conflicting/invalid targets and omission of earlier message text. The projection includes the complete new text and explains that earlier replies and copies remain unchanged. It does not quote undisclosed earlier content.

The generator rejects scope violations across the complete reference set before calling its resolver, including violations after valid-looking references. The generator requires validated targets supplied by its resolver. A receiver lacking those targets may still display the original received readable fallback as an unresolved correction; it must not manufacture a validated replacement. This projection experiment supplies no cryptographic verification, durable edits or real-client interoperability evidence. The separate generated-MIME check below covers packaging.


## Generated correction MIME

Run `python3 -m unittest discover -s email-next/evidence -p test_edit_mime.py`. Two generation tests connect the real readable edit projector to the shared MIME-alternative generator and Python email parser. The generated text/plain, text/html and unregistered event-type alternatives retain correction text, exact target identifiers and original event bytes; earlier private text is not copied into either readable alternative.

Four additional incoming-selection tests exercise the strict standalone alternative layout, duplicate/reordered alternatives, event parameters, malformed base64 and wire/part/decoded limits. The selector returns untrusted event and fallback bytes; it does not authenticate or apply edits. This is not an SMTP test. The generator accepts caller-supplied alternatives and cannot establish their semantic or cryptographic binding. A negative boundary check makes that limitation explicit. The trusted fixture resolver supplies an already validated root; no identity verification is performed.


## Received edit preparation

Run `node --test email-next/evidence/receive-edit.test.mjs`. Four tests join the existing conversation-context checks, edit dependency evaluator and readable projector. A matching author/epoch/audience context does not bypass missing, conflicted or invalid history. Sender mismatch stops before ancestor resolution; local budget exhaustion prepares no correction.

`prepareReceivedEdit` selects the candidate from a caller-supplied authenticated storage snapshot, including exact-byte identity-conflict results. Its sender credential and membership context must come from verified MLS processing. These fixtures construct those inputs; they do not perform encryption or prove identity. Successful preparation returns a readable projection, not a storage commit, transmission authorization or a complete set of current heads. The candidate's ancestor closure cannot establish absence of concurrent branches. Durable integration must evaluate the complete known edit set and compare snapshot revisions before installation.


## Encrypted correction transport

The locked MLS exchange test also sends `mls-smoke/fixtures/edit.json` through actual MLS encryption, the existing MIME/loopback SMTP transport and recipient decryption. It checks exact decrypted bytes and passes the actual sender credential, group context and membership roster to the strict contribution bridge. The resulting edit remains pending because that bridge intentionally supplies no retained-history resolver.

The original message was delivered earlier in the exchange, but the bridge does not persist it between invocations. This fixture therefore proves encrypted carriage and refusal to invent missing history, not application of an edit to a stored conversation. Connecting authenticated retained history, conflict evidence and durable view installation remains required.


## Paired meeting correction examples

`examples/meeting-original.eml` and `examples/meeting-correction.eml` are complete unencrypted messages with readable alternatives and the unregistered event media type. They use synthetic account identifiers and reserved example mailboxes; no mailbox-to-principal binding is implied. The correction's ordinary reply header names the original email, while its structured root names the original contribution exactly.

Run `python3 -m unittest discover -s email-next/evidence -p test_edit_examples.py`. The test selects both MIME packages and checks exact root/predecessor linkage, distinct event identities, matching ordinary reply headers, complete replacement text and omission of old text from the correction. This verifies authored examples, not client support or encryption.


## Answer-button objects

`button-operations.mjs` separates a question with predefined choices and a single selected answer from the deferred general-form experiment. Run `node --test email-next/evidence/button-operations.test.mjs` from the specs repository.

Six tests cover exact question/option matching, malformed controls, forbidden extra members, unknown options, pending and conflicted targets, pre-resolution author/conversation boundaries, exact replacement targets, duplicate references and self-replacement. The caller supplies records already authenticated and authorized for resolution. The validator never fetches a target or sends a request.

A `references-matched` result is not authorization to apply an answer. The experiment does not check graph cycles, the previous answers' transitive validity, authenticated envelope context, audience access, durable state, readable MIME binding or HTTPS endpoints. The contribution-envelope validator now accepts these candidate operations. Five additional button-projection tests cover inert question output, exact answer labels, missing/invalid targets, audience expansion and independently verified context. The projector refuses automatic context copying outside the question audience. The button MIME round-trip experiment below exercises packaging; authenticated receive integration, graph validity and durable effects remain unfinished.


## Button MIME round trips

`test_button_mime.py` projects candidate questions and answers through the JavaScript projector, packages their exact UTF-8 event bytes with readable text/HTML, and reselects the structured part through the bounded MIME inspector. Four tests cover both operation kinds, Unicode and escaped labels, no unselected-choice transcript in an answer, invalid target handling and refusal to copy context to a wider audience. The downloadable `examples/button-question.eml` and `examples/button-answer.eml` are checked against the exact candidate events and projector output, including their ordinary reply headers.

Run `python3 -m unittest discover -s email-next/evidence -p 'test_button_mime.py'`. The numeric budgets in these fixtures are test inputs, not protocol quotas. The packager does not verify the relationship between arbitrary caller-supplied fallback and structured content; this test supplies the projector's output. Authentication, malicious fallback substitution, durable answer state, real SMTP/provider delivery and legacy-client display remain separate validation requirements.

## Offline acceptance report

Run `python3 email-next/evidence/run_acceptance.py` from the specs repository to emit a JSON report for the candidate button MIME profile. The checked-in `acceptance-cases.json` links each case to its requirement. The report includes hashes of the fixtures, manifest and declared implementation sources, Python/Node versions, individual results and an explicit completeness flag. These identify the local inputs; they are not signed provenance or proof of an independent implementation. Four local checks currently run; legacy-client display, provider carriage and authenticated service submission are explicitly not tested.

The default exit status detects failures in the implemented development checks. Use `--require-complete` for an acceptance gate: it also fails for untested and unsupported scenarios. A zero default exit status is not a conformance claim. The report distinguishes pass, fail, not-tested and unsupported. An unsupported case requires an explicit implementation declaration with a reason and is labeled as declaration evidence; missing adapters and skipped tests remain not-tested. Test skips never become passes. The default button manifest performs local fixture checks. The optional provider manifest below starts loopback test services; neither mode certifies a client or exercises a deployed provider. Its case vocabulary is an experimental report format, not a registered protocol.

### Configured provider and admission report

Select the separately scoped manifest to exercise actual configured HTTPS discovery, MLS admission and encrypted local mail:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python email-next/evidence/run_acceptance.py \
  --manifest acceptance-provider-admission.json --require-complete
```

Use the evidence Python environment with TLS dependencies and build the Rust workers first. The manifest path is relative to the evidence directory; parent traversal and symlinks escaping that directory are rejected. The default button manifest remains unchanged.

This report currently records **five passes and three not-tested cases**. The completeness command therefore exits 1 as intended. Public credential/discovery lifecycle, independent implementations and deployed mail carriage are not tested. Its 66 declared source hashes include the relevant Rust sources, fixtures and lockfile; unrelated button example hashes are omitted. Runtime checkpoints and credentials are not report inputs. These checks still use the earlier test-only invitation envelope, not the complete [new invitation carrier](../mls-invitations.md).

## Button answer graph

`button-state.mjs` evaluates the replacement graph for the exact question/answer objects. Its resolver supplies independently authenticated, authorized records and exact-identity conflicts. The evaluator follows replacement ancestors, rejects cycles and invalid ancestors, preserves concurrent answers, and only suppresses predecessors of valid answers. Missing dependencies leave replacements pending. Optional local work budgets return an incomplete result without a partial set of current answers.

Run `node --test email-next/evidence/button-state.test.mjs`. Seven cases cover delivery order, discovered ancestors, concurrency and explicit reconciliation, missing dependencies, cycles and their descendants, invalid options, conflicted identities, budget exhaustion and a 3,000-answer chain. The implementation uses iterative traversal. These are snapshot results, not durable deduplication, cryptographic validation, audience authorization or endpoint execution. The readable projector is a separate component; neither result alone authorizes externally visible effects.

## Preparing a received button answer

`receive-answer.mjs` composes the conversation-context check, transitive answer-graph evaluation and readable projection. `prepareReceivedAnswer` consumes an exact reference, independently verified sender/context/membership and a resolver over one authenticated storage snapshot. It does not verify cryptography itself. A prepared result contains the readable projection of that answer, not a claim that it is the sole current answer: concurrent branches outside its ancestor closure have not been examined.

Run `node --test email-next/evidence/receive-answer.test.mjs`. Seven tests cover successful preparation, pending/conflicted/invalid questions, sender mismatch before history access, question-audience restrictions, invalid transitive replacements, malformed historical envelopes and local-budget exhaustion. Historical records must have been authorized under their own authenticated context; the current epoch does not retroactively establish that authority. The caller must retain authenticated bytes and identity conflicts, authorize history access, and transact durable changes separately. This experiment neither submits to endpoints nor commits user-visible effects.

The acceptance-runner regression checks exercise skipped, empty, missing-test, expected-failure and unexpected-success outcomes. None can produce a passing case. Empty manifests, duplicate case identities and cases that name more than one of a test, unavailable reason or unsupported declaration are rejected before execution. Six runner tests cover these distinctions and safe manifest selection, including the explicit unsupported status.

## Contribution journal

`contribution_journal.py` stores exact, already-validated contribution bytes under conversation/principal/event identity. Identical retransmissions do not create additional records. Different bytes under the same identity remain conflicting variants, including after a subsequent duplicate. Snapshot reads retain those variants rather than choosing a winner.

Run `python3 -m unittest discover -s email-next/evidence -p 'test_contribution_journal.py'`. Three tests cover reopen persistence, exact-byte duplicate/conflict behavior, identity mismatch, rollback of an injected database write failure and abrupt process exit immediately before or after commit. A retry stores the previously uncommitted record or recognizes the committed duplicate, respectively; both leave one intact record. These tests do not simulate power loss, filesystem corruption or external side effects. This is a storage component, not a cryptographic receiver: callers must validate envelopes, authenticate and authorize inputs, and retain the original protection/context evidence separately. Its recorded state does not mean an event is valid for application. The answer adapter below exercises graph evaluation and a local derived-view cache. Notifications, external effects and integrated authorization remain unfinished.

## Recomputing answers from the journal

`journal_button_view.py` connects a single stored snapshot to the JavaScript answer graph. It strictly decodes each unique recorded contribution, retains exact-identity conflicts, validates envelope shape and prevents answer audience expansion beyond a resolved question. It returns candidate current answers for that snapshot. The journal's caller remains responsible for authenticating and authorizing every record under its original context.

Run `python3 -m unittest discover -s email-next/evidence -p 'test_journal_button_view.py'`. Four integration tests cover durable cache installation and invalidation, snapshot invalidation across two database connections, answer-before-question delivery, reopen/retry, a later conflicting question identity and a malformed stored envelope. An unresolved answer becomes a candidate after its question arrives; a question conflict removes that interpretation without deleting the original records. Recomputing cannot undo a notification or service action already performed. The adapter does not itself persist a derived view, execute effects or establish cryptographic assurance. Callers can save its result using the journal cache described below.

The derived journal view carries a local `sourceToken` over its conversation and exact ordered records, using length-delimited hash inputs. Exact duplicates preserve the token; new records or conflicting variants change it. It survives reopening the same content. This token detects a stale source snapshot; it is not an event identity, authentication proof or lock. Comparing it and then acting can still race with a later write. Durable publication or external effects must serialize their validation and commit, and must also recheck authorization changes held outside this journal.

`install_view` compares the source token and saves a local projection in one SQLite write transaction. An intervening contribution causes a `stale` result without overwriting the saved view. `read_view` checks the cache and journal in one read transaction; it returns no payload when later contributions have made the cache stale. Exact retransmissions do not invalidate it. The integration fixture checks this behavior across two connections and a reopen. The caller supplies the projection and must validate its derivation; these APIs do not make arbitrary cached data authoritative. A successful read describes that database snapshot only. External authorization changes, subsequent writes, notifications and service submissions still require their own integrated transaction or effect protocol.

### Inert image candidates

The HTML tree stage retains HTML-decoded image sources as `imageCandidate` data for a future authenticated resource resolver. They never become `src` attributes in the preview, including remote URLs and unresolved Content-IDs. Missing `alt` is reported separately from an explicitly empty alternative. The integration fixture checks that both source kinds remain absent from serialized preview markup. This does not implement image resolution, decoding, resource authentication or rendering; only those later checks may release an image to a client-owned renderer.

`image-resource.mjs` resolves a candidate `cid:` value against the experimental event-scoped resource convention. Percent escapes decode once, the event must match, and the selected compound must contain exactly one part whose bytes match the authenticated manifest and local limits. Four cases cover escaped identifiers, cross-event and external references, ambiguity, altered bytes and bounds. Successful output is `encoded-resource`, deliberately not a decoded image: even arbitrary non-image bytes can satisfy a correct manifest. PNG/JPEG validation, decoding limits and integration into a client-owned renderer remain required. The caller must authenticate the HTML and manifest in the same contribution context before invoking this resolver.

### Language-label preservation

The attribute filter and preview serializer retain received `lang` values, including empty and unrecognized labels, without recanonicalizing or fetching anything. The fixture checks nested empty/unknown labels and single HTML decoding followed by safe serialization. This is receiver preservation, not a complete language implementation: authoring-client integration and assistive-technology behavior remain unimplemented; the standalone registry-based authoring check is described below. The projection now propagates structural and removed-wrapper language into retained nodes and bare-text spans. Its standalone document has no host-application language ancestor or default metadata. Two additional fixtures check effective language after serialization/reparse and preserve table whitespace without injecting a span into table structure. This does not supply a complete DOM/accessibility integration. The presentation chapter owns those requirements.

## Passive discovery carrier

`discovery_mime.py` extracts only the direct discovery child of an ordinary mixed message. Five fixtures cover exact bytes under transfer refolding, forwarded and nested parts, misleading filenames, multiple candidates, conflicting headers, unsupported parameters, malformed base64 and local limits. Output is an inert candidate, never accepted identity evidence. Input wire size is bounded before MIME parsing and decoded size before release; the wire bound is not a streaming-parser guarantee. Signature, identity, mailbox association and MLS checks remain separate. Run `python3 -m unittest discover -s email-next/evidence -p test_discovery_mime.py`.

`passive_discovery.py` adds strict wrapper and assertion decoding, preserving original bytes and the domain-separated signing input. Eight tests cover shape, canonical encodings, duplicate names, size/depth bounds, identifiers, mailbox spelling, feature/package relationships and time intervals. Its status is `syntax-only-unverified`: fake signatures and opaque non-MLS package bytes can pass syntax checks. A-labels explicitly require further IDNA validation. This parser does not authenticate state records, verify the discovery signature or install a mailbox association. These gaps prevent the experiment from establishing automatic encrypted bootstrap.

## Passive discovery signature and identity check

`verify_passive_discovery` verifies the fixed-purpose Ed25519 signature over exact assertion bytes, then asks the existing identity store to authorize the device for receiving under the requested trust policy and time interval. The asserted head and binding must match the returned current snapshot. It never installs incoming identity records. Six integration fixtures exercise MIME transfer re-encoding and wrapper reserialization, valid signatures, tampering and purpose substitution, absent acceptance, stronger trust policy, stale state and mismatched keys. Success remains `snapshot-authorized-unverified`, with mailbox ownership and MLS validation explicitly false. The store read transaction ends before return: later identity changes require revalidation and coordinated commit before release or other effects.

## Language-tag authoring validation

`language_tags.py` validates base RFC5646 language tags using checked-in Language Subtag and Extension Registry snapshots. Their File-Date and SHA256 values are recorded in `language-data/manifest.json` and checked when loading. Eleven tests include grandfathered tags, private-use ranges, deprecated values, repeated variants/singletons, extlang count and prefix, allocated extensions and malformed input. `validate_lang_attribute` separately accepts HTML’s empty unknown-language value. Extension contents receive syntax checks, not extension-specific semantic validation; no canonicalization or network access occurs. These datasets pin the experiment, not every future profile implementation. The [presentation contract](../presentation-profile.md#language-labels) defines local snapshot identification and authenticated maintenance separately from mail processing. Authoring-client and update-path integration remain unimplemented. Received labels follow the separate preservation rule.

## Passive MLS admission-package checks

The Rust experiment exports `validate_discovery_package` for bounded, exact TLS-encoded MLSMessage KeyPackages. It checks library signatures, protocol version, suite 0x0001, the expected credential and accepted signing key, the seven-day lifetime bound and the required application-context capability. Last-resort packages are excluded. Three focused tests cover valid input, raw/trailing/mutated bytes, identity and key substitution, version/suite mismatch, capabilities, clock intervals and input size. The complete Rust suite passes four tests, including the existing encrypted exchange.

The caller must obtain the accepted key and device authority independently. OpenMLS also checks its system clock; a supplied uncertainty interval does not override that additional library check. A clock disagreement can therefore prevent this experiment from accepting a package otherwise inside the supplied interval. Success does not consume the package, authorize membership, commit group state or verify that the peer really implements an advertised capability. The Python adapter and joined discovery test below connect these component checks; atomic admission remains unimplemented.


## Joined passive discovery and MLS package experiment

`test_passive_discovery_chain.py` connects a real signed advertisement to an accepted local identity and a cryptographically valid MLS package. The Rust fixture signs the binding, possession, genesis and advertisement records with the package's device key. The test accepts genesis under an explicit unverified-first-contact policy, verifies the advertisement against that identity snapshot, retrieves the accepted signing key from storage and checks the exact advertised package. An independently valid package with another key fails matching; replacing the package inside the advertisement invalidates its signature.

The package adapter has four additional tests for corruption, trailing bytes, identity/key/time mismatches, size bounds and canonical arguments. Build the local binaries with `cargo build --locked --manifest-path email-next/evidence/mls-smoke/Cargo.toml --bins`, then set `EMAIL_NEXT_MLS_BIN_DIR` to the absolute Cargo `target/debug` directory. With Node and Python available, run `python -m unittest discover -s email-next/evidence -p 'test_passive_discovery*.py'`. The complete Python suite also needs the isolated HTML/CSS dependencies and configured parse5 module described above. Missing Rust binaries are setup errors, not skipped successes.

These checks do not form an atomic admission transaction. They do not verify mailbox ownership, consume a package, install a group, exercise a roster change or contact a mail provider. The accepted identity can change between checks; release still requires the profile's current-authority checks. The separate MIME experiment covers carrier extraction, not this joined test's network delivery.


## Service-answer request and result binding

Run `python -m unittest discover -s email-next/evidence -p test_service_answer.py`. Five tests exercise the configured-deployment [service-answer contract](../service-answers.md): strict JSON, identifiers, outcome/reason combinations, exact-request SHA256 and every receipt/request binding. Reformatting a receipt preserves its decoded meaning; reformatting a request changes its exact-byte identity and requires a different bound digest. Duplicate fields, missing/extra members and mismatched references fail.

`service_answer.py` performs no HTTP, token validation, action authorization, deduplication storage or business effects. Its expected service origin must come from a separately validated descriptor. Success returns `bound-unverified`, not confirmation; transport authentication and all action prerequisites remain mandatory.


## Service-question carriage and readable fallback

`service-question.mjs` validates the exact operation/descriptor shape, narrow HTTPS spelling, ordered validity bounds and the descriptor's reference to the enclosing event. The envelope validator dispatches this operation explicitly. The readable projector lists the service origin and choices as inert text, explains the configured-client requirement and keeps ordinary email replies separate from service confirmation. Six focused JavaScript tests include malformed destinations, self-reference substitution and rejection by the existing conversation-answer resolver, graph and receive path. A-label hosts remain unsupported until the IDNA boundary is implemented; this validator is not a complete profile implementation.

Run `python -m unittest discover -s email-next/evidence -p test_service_question_mime.py` for two MIME composition tests. Exact structured bytes survive ordinary alternative packaging, readable parts retain service/choice meaning without endpoint links, and a wrong self-reference prevents projection. These use synthetic identities and neither authenticate delivery nor cause HTTP/email effects.


## Durable mailbox association selection

`mailbox_association_store.py` implements the local unverified selection portion of the [mailbox association contract](../mailbox-association.md), sharing the existing `IdentityStore` SQLite connection. It retains observations and proof variants, compares association generations, stores idempotent decisions, and rechecks accepted identity authority inside the selection transaction. Initial competing principals remain ambiguous under both policies. Replacement, disable and enable preserve history and advance the generation when state changes.

Run `python3 -m unittest discover -s email-next/evidence -p test_mailbox_association_store.py`. Fifteen focused tests cover restart, exact retry and changed-request rejection, concurrent connections, atomic rollback, current identity and validity checks, strict policy, address distinctions, replacement, disable/enable, and authenticated advertisement collisions across mailboxes. A real foreign-key signature over identical assertion bytes cannot block later authorized admission; retained unauthorized variants cannot overwrite authenticated evidence. Authenticated collision history persists independently of expiry, while independent advertisement records remain eligible.

This is a trusted local ingestion API. Callers must verify exact assertion signatures, validate the complete credible time interval, and provide trusted sole-From parsing and source provenance before ingestion. The normal verification path is `verify_passive_discovery`; the store additionally rechecks identity authority before indexing an authenticated record. Its `observedAt` point check does not justify narrowing uncertain time. Original header retention remains external. No received authentication Boolean substitutes for these preconditions.

These tests establish local selection and persistence behavior, not mailbox ownership or safe transmission. Independent verification, durable operation/release coordination, provider integration, backup reconciliation and deployment migration remain outside this store. Snapshot and decision results cannot authorize sending.

## Canonical byte-encoding boundaries

`test_base_encoding.py` exercises the discovery field decoder against the RFC4648 base64 vectors using explicit ASCII input octets, the binary examples, all nonzero unused-bit alternatives for the final one- and two-octet quanta, and malformed padding, whitespace, NUL, non-ASCII and base64url substitutions. Three tests pass. The [encoding audit](../audits/base-encodings.md) records source and errata coverage. These are record-field checks; outer MIME folding has its own decoder and tests. No encoding check authenticates the decoded bytes.

## MLS contribution epoch binding

The Rust exchange captures an accepted library epoch snapshot and passes its group, epoch, member indices, credential identities and signature keys to `mls_contribution.py`. The adapter requires empty application AAD and uses the authenticated sender index to select the matching epoch credential/key. A real delayed application message succeeds against its retained earlier snapshot and fails against a newer epoch snapshot. These checks preserve the original contribution bytes.

Five Python adapter tests cover sender/roster/context mismatches, trailing-object rejection and an optional check against a retained `IdentityStore`, including wrong key, strict policy and account conflict. The Rust subprocess remains context-only; it does not share that persistent account store. These are separate tested boundaries, not an atomic durable receive pipeline or authorization to cause effects. The [security profile](../security-profile.md) defines the proposed binding and remaining integration work.

## Reaction operations and local views

`reaction-operations.mjs`, `reaction-state.mjs` and readable projection cover the [reaction contract](../reactions.md). Twelve focused tests cover the pinned vocabulary and exact shapes, additive events, explicit withdrawals, missing/conflicting evidence, order-independent evaluation, local work limits and projections that omit target history. Envelope dispatch recognizes the two new kinds. The Unicode17 input, derived membership table, source hashes and license are retained under `unicode-17/`; the vocabulary test reconstructs the table from the source and checks its hashes.

The evaluator consumes a caller-supplied authenticated and schema-validated snapshot. It neither verifies that history nor commits a durable current view. The compound MIME selector has the bounded implementation below; protected receive integration remains unimplemented. A legacy reaction marker never authorizes the structured operation.

## Reaction MIME packaging and selection

`reaction_mime.py` generates the proposed two-child reaction layout, or ordinary alternatives when no transport target is available and for withdrawals. Six tests in `test_reaction_mime.py` use actual MIME and the JavaScript readable projector. Exact structured bytes survive transfer folding; duplicates, ambiguous ordering, invalid headers/encoding, resource limits and forwarded nesting are rejected. Emoji mismatch returns a diagnostic alongside untrusted event bytes instead of claiming a verified pair.

The local adapter accepts a narrow ASCII Message-ID subset, not every valid RFC5322 spelling. Caller-provided target mapping and readable-text equivalence are not independently verified. No encrypted carrier, authenticated receive effect or real email client is exercised.

The offline acceptance report now hashes its known service-question/reaction dependencies and pinned emoji input along with existing implementation files. Nested evidence paths are allowed only within the evidence directory; escaping paths and symlinks are rejected. The report remains a local observation, not signed provenance or independent implementation evidence.

## HTTPS certificate identity and TLS minimum

`service_tls.py` constructs a verifying TLS context with TLS1.3 as its minimum and Common Name fallback disabled. It takes an independently authorized DNS reference host and an optional locally trusted CA file; incoming mail must not choose the trust store. The bounded host parser explicitly refuses A-labels pending IDNA support.

Install `requirements-tls.txt` in the isolated Python environment before running `python -m unittest discover -s email-next/evidence -p test_service_tls.py` or the full Python suite. Eight tests generate temporary certificates and perform actual loopback handshakes: a matching SAN succeeds; wrong host, Common Name-only, an untrusted certificate and TLS1.2 fail; wildcard matching is limited to one complete label. The parent verification used Python3.14, OpenSSL3.6.2 and cryptography50.0.2. Missing cryptography is an environment error, not a skipped success.

The adapter neither sends HTTP nor handles tokens, redirects, endpoint authorization, ALPN selection or revocation. These tests are not complete RFC9525/PKIX conformance or deployed service evidence. The [service identity audit](../audits/service-identity.md) records the normative scope and remaining dependencies.

## Staged durable MLS reception

Build the Rust binaries with `cargo build --locked --manifest-path email-next/evidence/mls-smoke/Cargo.toml --bins` and set `EMAIL_NEXT_MLS_BIN_DIR` to the resulting absolute binary directory before the full Python suite. The `receive-staged` worker stages a complete opaque provider map; `mls_receive.py` commits it, authenticated receive evidence and eligible message/question/answer journal bytes in one transaction on the retained identity store’s connection. The journal supports a transaction-owned append helper while retaining its existing standalone API.

Fourteen tests in `test_mls_receive.py` exercise real MLS ciphertext, exact replay after restart, same-event re-encryption, authenticated collisions, tampering, authenticated invalid application data, current strict/conflict policy, invalid local time, concurrent connections and precommit failures. One child process terminates after the checkpoint write but before receive-ledger insertion, proving rollback of the entire local transaction. Generated checkpoints remain secret test inputs in memory, pipes and temporary databases; do not include worker input/output in logs or reports.

The worker accepts only the current pre-established group epoch and private application messages. Retained messages and button operations can be reevaluated against current authority without rerunning the worker. Tests cover answer-before-question across restart, stable repeated views, collisions and preserved history. The revocation integration case supplies a modeled identity-store rejection, not a newly generated signed successor proof. Reevaluation has local bounds of 4,096 receive records and 16 MiB of retained application/evidence input; exhaustion returns incomplete without a partial new view. Group admission, older-epoch integration, other operation kinds and effect/outbox dispatch are not implemented. All results report no effects applied. SQLite snapshots and old pages can retain secrets; logical atomicity is not secure erasure. The [security profile](../security-profile.md#durable-reception) owns the receive contract and limits.

## Explicit no-revocation certificate extension

`certificate_no_revocation.py` checks the RFC9608 extension in DER certificates using the pinned cryptography dependency. Run `python -m unittest discover -s email-next/evidence -p test_certificate_no_revocation.py` in the same environment as the TLS experiment. Eight generated-certificate tests cover exact DER NULL, absence versus an explicit exception, CA/CRL/OCSP combinations, issuer-only AIA and malformed input. A valid critical extension is distinguished from conforming issuer criticality rather than rejected solely for that issuance discrepancy. No arbitrary certificate-lifetime limit is applied.

The result concerns extension syntax and combinations only. It does not verify the certificate signature, trust path, service name, validity or revocation status, and it is not integrated into a TLS handshake. `certificateValidated` and `revocationChecked` remain false. The [no-revocation audit](../audits/no-revocation.md) records the inherited scope.

## Configured provider record validation

`provider_control.py` validates the configured provider profile and signed challenge/response wrappers. Run `python -m unittest discover -s email-next/evidence -p test_provider_control.py` with Node available. Seven tests use generated Ed25519 keys and signatures, covering exact configuration, role operations, limits, duplicate names, encoding/depth bounds, context and request binding, nested passive evidence, altered signatures and expired retained records. The Node helper has a local ten-second execution timeout.

Static signature validity is separate from `new_admission_time`: expiry prevents new admission but does not prevent inspection of a retained exact retry. Callers still supply independently authorized keys/configuration and validate current identity authority, binding expiry and MLS package suitability. Results explicitly report `identity_authorized: false` and `mls_validated: false`. This is not an HTTP service or durable exchange store; token authorization, queue admission, pagination, rate enforcement and end-to-end protection remain integration work.

## Validated proposals and application sending

`proposal_observation.py` retains fully validated nonempty proposal observations for the current group epoch. `ordering_mls.py` obtains counts from actual OpenMLS staged proposals, after MLS and application validation. Raw exchange receipt does not write observations. A separate durable observation commit precedes publication into the vote database, followed by scope and current-authority rechecks.

`SenderRelease` and `SenderWorker` enforce the resulting hold at preparation, retry, release and pre-DATA. Ordinary copies and hosted disclosures bound to the same protected contribution also check it. Control traffic retains its separate path. Accepted certified advancement permits new-epoch content; it does not authorize stale prepared bytes. Observation history survives restart and candidate abandonment. Legacy local staged rows without provenance fail closed; old peer-vote inspection cannot be inferred from raw retained mail.

Run `PYTHONPATH=email-next/evidence python -m unittest test_proposal_observation` with the configured MLS workers. Three integration cases cover configured and signed-discovery removal, real certified carrier installation, Add/mixed/context proposals, pre-DATA interruption, durable restart and transaction failure. Existing sender-continuity cases separately preserve empty self-update interleaving. These are local checks of the [proposal-observation contract](../group-conversations.md#pause-content-while-a-membership-plan-is-pending), not independent distributed-liveness or security assurance.

## Isolated image decoding

Install `requirements-images.txt` in the isolated Python environment. `image_decode.py` decodes PNG/JPEG in a subprocess and returns width, height and tightly packed RGBA8 bytes. Callers must supply `DecodeLimits` for encoded bytes, width, height, pixels, output bytes and wall time. The optional positive `max_metadata` bound defaults to 1 MiB and covers ancillary/marker metadata and expanded PNG ICC data. These are adjustable local policy, not universal wire quotas.

Run `PYTHONPATH=email-next/evidence python -W error::ResourceWarning -m unittest test_image_decode test_image_fidelity test_scoped_image_decode`. The 42 tests cover ten existing decoder cases, 26 fidelity cases and six authenticated-resource binding cases. Dependencies are pinned to Pillow 12.3.0 and PyPNG 0.20220715.0. The worker emits no source metadata or error traceback.

PNG structure and filtered expansion are checked before PyPNG reconstructs the same immutable stream. Transparent-color comparison uses source samples before rounded RGBA8 reduction. The worker accepts all selected static PNG depths/types, filters and Adam7; common eight-bit baseline/progressive Huffman JPEG uses Pillow/libjpeg. Bounded primary Exif Orientation 1–8 is applied once, including reflections, with dimensions checked again. Unused Exif 3.1 UTF-8 descriptions are bounded without being displayed.

Public ImageCms transforms applicable RGB/gray ICC v2/v4 profiles to sRGB without changing alpha. Untagged PNG gamma/chromaticity uses the selected source primaries, white adaptation and sRGB transfer curve. Unsupported present PNG cICP or ICC ADGC produces the explicit image fallback. Synthetic LUT8/LUT16, mAB and multi-process matrix vectors exercise actual library paths; unknown unsupported elements are not removed to force a successful transform. The eight-bit path can quantize or clip out-of-gamut SDR colors and does not provide HDR tone mapping or printer/proofing fidelity. The [image interpretation contract](../audits/image-formats.md) owns the required processing behavior.

The worker now installs the shared process limits before reading encoded input or importing Pillow: CPU and output-file enforcement, process-group wall timeout and a resident-memory watchdog. The existing six positional or keyword `DecodeLimits` arguments remain valid. Optional adjustable defaults add three CPU seconds, a 256 MiB resident termination threshold and 20 ms sampling; output framing is limited to the caller's pixel-output budget plus 128 bytes. Invalid policies reject before spawning. These are implementation choices, not wire requirements.

As with [HTML parsing](#isolated-html-parsing), macOS resident monitoring can overshoot and is not a hard pre-header allocation ceiling. Strict hard-memory policy rejects on this tested platform; the Linux address-space path is untested here. No filesystem/network sandbox is claimed. Tests include exact existing pixels, malformed headerless input, actual timeout/resident termination and unsupported strict policy. Scoped authenticated integration and browser display have separate evidence below. The focused image tests establish selected orientation and color behavior, not comprehensive codec/fuzz coverage, independent CMS agreement or OS sandbox assurance.

## Durable provider exchange storage

`provider_store.py` stores immutable signed requests and responses in SQLite. Run `python -m unittest discover -s email-next/evidence -p test_provider_store.py`. Thirteen tests use actual signed-record validation and cover restart, exact retries after expiry, collisions, account/grant/role boundaries, admission quotas and snapshot pagination. Once an unanswered exchange is certainly expired, its retained terminal state prevents reopening after a clock rollback. A completed response remains immutable.

The caller supplies authenticated credential context, current configuration and verification keys. The store enforces shared grant/account/service pending and rolling-minute admission budgets. Immutable cursor positions preserve retry pages; fresh arrivals require a fresh enumeration. Snapshot lifetime is fixed, and the active-cursor budget counts snapshots. The local accounting clock persists a nondecreasing trusted earliest time and rejects rollback. One database represents one configured service; an immutable local grant registry enforces aggregate-limit agreement.

This component does not authenticate tokens or implement HTTP, per-credential request/failed-authentication counters, grant revocation/reconfiguration, retention cleanup or backup-restore detection. Its role checks are not proof of credential authentication. An exact retry after exchange expiry still requires a currently usable grant. No device authorization, MLS admission or external effect is inferred from storage success.

## Scoped resource-to-pixel integration

`scoped_image_decode.py` calls the existing Node image-resource resolver through `resolve-image-decode.mjs`, then the isolated image decoder. Run `python -m unittest discover -s email-next/evidence -p test_scoped_image_decode.py`. Six tests exercise genuine PNG/JPEG resources, wrong event scope, missing/duplicate parts, digest mismatch, remote/data sources, format mismatch, local limits and a correctly hashed malformed image. Negative binding cases assert that decoding is never reached. Failure returns the caller's original alt string as inert text.

The caller must authenticate the manifest/event and supply parts from exactly one selected MIME compound. This adapter does not verify those signatures, fetch anything or display the image in a browser. Its parsed MIME media type is checked against the bytes before full decoding. Bridge and decoder limits are explicit local inputs; the decoder's memory-containment and fidelity limitations still apply.

## Configured provider HTTPS adapter

`provider_http.py` joins configured bearer credentials, signed-record validation and durable exchange storage over actual loopback TLS 1.3. Run `python -m unittest discover -s email-next/evidence -p test_provider_http.py` in the pinned cryptography environment. The adapter handles one bounded HTTP/1.1 request per connection, exact configured Host and route bindings, role scope, JSON representations and no-store responses. Tests use an explicit test-only mapping from the configured DNS service to loopback.

Creation versus retry is reported atomically by the store, so HTTP 201/200 does not depend on a separate existence check. Expired unanswered response admission has a distinct conflict outcome. Per-credential request counts and failed-authentication source budgets are retained locally; credentials and keys are supplied through trusted test configuration, never acquired from incoming email.

This is a loopback experiment, not a general-purpose HTTP server or production authorization service. It does not establish public token issuance/revocation, distributed quotas, retention cleanup, backup-restore recovery, complete PKIX revocation handling or actual MLS admission. A stored signed response remains discovery evidence, not encryption readiness. Current integrated test totals are recorded separately in the validation chapter.

## Isolated browser rendering

The browser experiment connects the filtered HTML tree and scoped image decoder to a client-owned rendering host. It constructs fresh DOM nodes inside an opaque-origin sandbox, supplies only decoded RGBA pixels to image canvases, and keeps navigation destinations in the parent client. Sender markup is never inserted as HTML. The client supplies the element/CSS policy, baseline stylesheet and explicit resource limits separately from message data.

The parent bounds tree depth, node/text counts and image dimensions before copying data into the frame. A private message channel binds the frame to its render instance. Timeout, failure and replacement dispose of the channel and frame. These controls do not establish OS containment of the earlier image decoder or HTML parser.

Run the sequential experiment with an existing Playwright installation and the Python environment containing the evidence dependencies:

```sh
EMAIL_NEXT_PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs \
EMAIL_NEXT_PYTHON=/absolute/path/to/python \
node email-next/evidence/browser-render-test.mjs
```

The fixtures exercise projected headings, lists, table semantics, language and direction, decoded pixels and alternative text, rejected sender code, no automatic network requests, keyboard-triggered destination disclosure, and opening the selected destination without referrer or opener. They also check forced colors, enlarged root text, invalid input, replacement and timeout cleanup. Unspecified direction uses the default left-to-right base; explicit `dir="auto"` remains automatic.

The optional client configuration `fontFamily` accepts `serif`, `sans-serif`, `monospace` or `system-ui`. It applies an important client rule to the body and every descendant, overriding permitted sender fonts; omission restores ordinary typography. Invalid values are rejected before replacing the active view. This finite list is an experimental client setting, not a wire restriction. Named/custom fonts and actual user-origin stylesheet tests remain outside the experiment.

The client can also set `rootFontSizePx` to a finite number of CSS pixels. It applies an important client-owned rule to the isolated document root; sender `rem` declarations remain relative and unchanged. Omission uses the browser’s initial root size. The experiment defaults to an allowed range of 8–64 CSS pixels; the trusted client can adjust it with `rootFontSizeRange: {min, max}`, using finite positive ordered bounds. These are adjustable implementation defaults, not protocol limits or user requirements. Invalid preferences leave the existing view intact. Changing preferences remounts the message through the existing host API.

The optional `lineHeightRatio` preference applies a unitless line height through client-owned important rules on the body and every descendant. It overrides sender spacing while scaling with each element’s font size. Omission restores the baseline and sender styles. The local default range is 1–3; trusted clients can adjust finite positive ordered bounds with `lineHeightRange: {min, max}`. These are experiment defaults, not protocol limits. Invalid configuration leaves the current view intact.

Fifteen sequential Chromium check groups pass. Line-height cases cover inherited ratios at different font sizes, overriding explicit sender spacing, an adjusted preference range, reset and invalid values. Root-size cases cover 16, 24, 40 and 64 CSS pixels, an explicitly adjusted range allowing 80, nested `rem` sizes/spacing without compounding, inherited text and heading sizes, reset to browser defaults, invalid input, and overflowing content remaining inside the fixed isolated frame. Native zoom, minimum-font restrictions, screen readers, other engines and complete mixed-script fallback remain untested.

This is one Chromium implementation. An accessibility-tree snapshot is not a screen-reader test, and doubling the root text size is not native browser zoom. Context menus, modifier-key navigation, native link copying, other browser engines, full layout fidelity and real assistive-technology behavior remain unverified. The host is development evidence, not a complete client or rendering-profile support claim.

## Provider discovery to encrypted mail

The joined experiment retains a device's actual MLS package and private initialization state, retrieves that same package through the configured HTTPS control service, and uses it to establish an encrypted conversation. The receiving device validates its current peer authority, package validity, expected roster and conversation context before installing the joined state. Package consumption and the receiving checkpoint commit in the same identity database transaction.

Five integration tests cover an encrypted message and reply carried through loopback SMTP, an invalid invitation followed by a valid retry, incorrect roster/context or stale identity state, two competing valid invitations, and process exits immediately before and after the admission commit. A failed admission leaves the package available; a successful one prevents a different invitation from consuming it. An exact retry returns the retained admission result, not fresh authority to perform another action.

Build the Rust workers with the shared target directory used for the other MLS experiments, then run:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_provider_mls.py'
```

`provider_mls.py` coordinates the experiment; `provider-mls.rs` retains and restores opaque OpenMLS checkpoints. These contain private key material and must not be logged or transmitted as discovery records. The target uses real staged admission. The creator installs its locally created group through the existing fixture helper; there is no durable send outbox in this experiment.

The invitation's Welcome/tree JSON envelope is test-only and does not define interoperable mail carriage. Both identities are synthetic, configured and explicitly unverified. There is one group per identity store and one security-library implementation. Public onboarding, independent mailbox ownership verification, secure checkpoint storage/erasure, restore protection, group transitions and deployed-provider interoperability remain outside these results.

## Initial invitation carrier

`mls_invitation.py` and `invitation_mime.py` implement the candidate [initial invitation](../mls-invitations.md) in a configured two-device experiment. The creator signs an exact recipient-scoped record. The receiver checks current retained creator send authority, target receive authority and an explicit local allowed-creator policy. Candidate identity bundles cannot reset its retained identity state or establish mailbox ownership.

The Rust worker requires the membership tree inside the encrypted Welcome, supplies no external tree, rejects unsupported PSKs and exposes the validated GroupInfo signer for comparison with the named creator. The application then checks the actual group, epoch, roster and context. Staging uses a disposable checkpoint; package consumption, checkpoint installation and the accepted invitation record commit together.

An accepted retry matches the original payload and signature. A changed signature does not reuse the success path. Wrapper reserialization does not change the signed invitation identity. Successful replay returns the recorded admission outcome, not new authorization to send or perform an external effect.

Run the focused cases after building the shared Rust workers:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_mls_invitation.py'
```

Six focused tests cover accepted replay, invalid signatures, missing embedded trees, wrong verified signers, signed target/group/context changes, duplicate or forwarded MIME, malformed singleton headers/parameters, transfer decoding and notice UTF-8. These cases do not establish every acceptance requirement in the chapter.

The MIME generator uses synthetic placeholder addresses and is a fixture helper, not an outbox or recipient-selection implementation. The selector only returns candidate bytes; it does not authenticate them. This experiment retains the single-group store and configured, explicitly unverified identities. Established-group admission, multi-group storage, durable sender release, restore reconciliation, secure secret retirement and independent interoperability remain incomplete.


## Preserving evidence bytes in Git

The specification's `.gitattributes` disables text normalization for complete email examples, MLS JSON fixtures and digest-pinned registry/Unicode text inputs. Email examples retain CRLF line endings. This keeps checkout settings from changing protocol bytes or invalidating pinned source digests. Generated reports still need a recorded implementation revision; byte preservation is not signed provenance.

## Initial invitation acceptance report

The `acceptance-invitation.json` manifest maps six local invitation checks to the [initial-invitation requirements](../mls-invitations.md). It covers signed admission and replay, embedded membership-tree and target bindings, the validated Welcome signer, direct MIME scope, ambiguous headers and notice decoding. Use the integrated-check setup above to build the worker and install its dependencies, then run:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python email-next/evidence/run_acceptance.py --manifest acceptance-invitation.json
```

The current result is six passes and three **not tested** cases: durable invitation sending, deployed mail carriage with ordinary-client presentation, and independent implementation interoperability. Adding `--require-complete` therefore exits 1. The manifest does not cover established-group invitations or claim the entire profile is implemented. Its source inventory includes the provider/admission helpers used by the invitation fixtures; the separately reported provider scenarios are not rerun by this manifest.

## Version-1 initial invitation acceptance report

The separate [version-1 invitation manifest](acceptance-invitation-v1.json) covers the signed application agreement and durable initial-invitation path. Its twelve local cases exercise actual loopback delivery and admission, a protected follow-up, exact proof and context binding, transaction rollback, process interruption, immutable retry and full signed-interval checks. It uses configured identities and the shared OpenMLS worker.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python email-next/evidence/run_acceptance.py --manifest acceptance-invitation-v1.json
```

The result is twelve passes and two **not tested** cases: deployed provider carriage with ordinary-client presentation, and independent implementation interoperability. `--require-complete` therefore fails. The report hashes its declared source inventory; that inventory includes shared and dynamically invoked helpers and is not a claim that every included file or branch was exercised. This manifest covers initial invitations, not established-group Welcome delivery or the complete membership lifecycle.

## Durable sender release

`sender_release.py` commits the exact encrypted message and advanced MLS checkpoint together in the identity store's transaction. Preparing the same delivery again returns the retained bytes. `sender_worker.py` rechecks current policy, identity dependencies and authenticated group metadata before recording release and opening its loopback SMTP connection.

One cooperating POSIX worker holds a lock adjacent to the canonical database. Recovery treats a released attempt without a conclusive durable result as uncertain; a lease timeout cannot replace a live worker. Recipient eligibility is reconstructed from the complete attempt history: final accepted recipients are not resubmitted, permanent rejections stay held, temporary recipients may retry, and uncertain recipients need an explicit retry choice. Every retry rechecks authorization and sends the same retained message bytes to its eligible envelope subset.

With the integrated-check dependencies and shared workers available:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_sender_release.py'
```

The focused suite exercises real MLS preparation, a signed accepted identity successor blocking release, process-lock exclusion, process death after server acceptance, unchanged-byte retry, mixed recipient outcomes across attempts and an observed policy change aborting before DATA. These cases establish local ordering and recovery behavior, not recall of transmitted data or exactly-once delivery.

This experiment supports plain message contributions, one configured group and explicitly unverified configured identities/envelopes. Its optional selected-association mode checks retained mailbox evidence as described below. It does not prove ownership, submit invitations, use deployed SMTP/TLS, recover restored databases or establish global revocation timing. The lock requires cooperating processes and a stable local database/lock path; aliases, network filesystems and inherited transmitting workers are outside the model.

## Configured group-transition comparison

`group_transitions.py` and the `group-transitions` Rust worker exercise membership additions and self-updates with a configured endpoint ordering role. The fixture starts from an already established group; three account principals own four device leaves, including a second device enrolled through a real signed identity successor. This is an ordering comparison, not the selected general distributed architecture.

Preparation keeps the candidate and Welcome private. A decision atomically installs its checkpoint, immutable predecessor decision and outbox record. Release rechecks current authority. Receiving separates authenticated private-message advancement from membership installation, so a policy-rejected commit cannot install its proposed group. Future-epoch inputs stay pending. A same-epoch receive change invalidates an older prepared candidate rather than allowing its checkpoint to roll back received state.

Run with the integrated-check setup and built shared worker:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_group_transitions.py'
```

Nine focused tests cover real transitions and Welcome admission, withheld release, unauthorized additions, wrong writers, separate send/receive authority, identity revocation, future epochs, replay, malformed cryptographic data, competing processes and process death around decision and receive commits. The commit sender must retain send authority even when its device still has receive authority.

The integrated comparison shares one MLS checkpoint with application sending and receiving and uses configured device/key admission intent. It does not implement remote administrative commands, package-specific grants, removals, service/quorum ordering, failover, branch-conflict recovery, garbage collection, secure erasure or backup reconciliation. An unreleased candidate can be explicitly retired and regenerated with fresh authorization if membership is unchanged; this never automatically chooses a competing branch.

## Configured service execution

`service_execution.py` and `service_https.py` connect retained request bytes to a local TLS1.3 HTTP/1.1 endpoint with configured bearer grants. The service records a scheduling choice and its terminal receipt in one SQLite transaction. Deferred requests remain durable until an explicit worker reconciles them; reading status never executes an action. The client retains authenticated direct-response evidence, keeps terminal results when later HTTP attempts fail, and records incompatible terminal receipts as conflict.

```sh
python -m unittest discover -s email-next/evidence -p 'test_service*.py'
```

The focused checks cover exact-byte retries after credential renewal, concurrent duplicates and replacements, process death around commit, a lost post-commit response recovered through GET, pending work across restart, expiry and authorization rechecks, and reordered/conflicting receipts from the configured trusted endpoint. The client requires its complete credible-time interval to fit the action bounds before POST. A later status request can recover retained evidence after the action closes.

The effect is local transactional state, not an external network operation. Descriptor authority, endpoint routing, certificate trust and bearer grants are fixture configuration; received-question authentication and public credential acquisition remain incomplete. Other limits include IDNA, certificate revocation deployment, general HTTP hardening, multiprocess client coordination, garbage collection, backup reconciliation and independent interoperability. A single client adapter serializes its requests. These tests do not establish production service readiness or exactly-once external effects.

## Selected mailbox evidence at release

`sender_association.py` joins the local mailbox store to encrypted preparation and release. A selected-association delivery retains each exact recipient spelling, selection generation, principal and explicitly chosen advertisement digest. Preparation, release and the pre-DATA cancellation check verify the selection and its current identity evidence inside the shared database transaction. An existing delivery cannot silently substitute refreshed evidence or follow a replacement principal.

The checker reuses the store's retained authenticated-record collision rules. A different authenticated assertion under the same record identity blocks use, including collisions observed through another mailbox. A later same-principal advertisement can be explicitly chosen for a new preparation; it cannot rewrite the old delivery's dependencies.

Routing checks cover the recipients participating in the current SMTP attempt. Full cryptographic-roster authority still applies because excluding an address from a retry does not remove its device from the existing ciphertext's decryption audience.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_sender_association.py'
```

The tests use actual verified passive advertisements and ordinary selection APIs. They cover disable/re-enable, principal replacement, evidence refresh, authenticated collisions, uncertain retries and cancellation before DATA. The combined sender and mailbox-store run passes 52 executions, including inherited sender cases. Configured-roster mode remains distinct from selected-association mode; neither establishes independent mailbox ownership, remote freshness, production transport or restore safety.

## Strict HTML quotation mapping

`html-quotes.mjs` scans original decoded HTML before constructing display nodes. The complete fragment must contain only ASCII space/tab/CR/LF between blocks, attribute-free lowercase `p` paragraphs, literal `br` inside paragraphs, one-level `blockquote` containers, and balanced inert `div` wrappers or text/`br`-only `div` paragraphs. `blockquote` accepts only quoted `cite`, `type` and `class` attributes; `div` accepts only quoted `class`. Attribute values never affect matching or display; duplicate/unknown attributes reject. Paragraph text accepts supported literal Unicode scalars, the semicolon-terminated named references `amp`, `lt`, `gt`, `quot`, `apos`, and decimal or lowercase-`x` hexadecimal numeric references. Nulls, surrogates, noncharacters and control/replacement cases are rejected, except tab, LF and CR. Comments, attributes, implied tags, nested quotes and other markup are outside the profile.

Every node retains a half-open **UTF-16 code-unit** range into the unchanged decoded source—not MIME-byte offsets or RFC5147 character positions. Comparison alone decodes accepted references and normalizes literal CRLF/CR to LF; `br` supplies a logical newline. No case, Unicode or other whitespace normalization occurs. A complete quotation collapses only when its paragraph sequence matches exactly one contiguous sequence of unquoted parent paragraphs. Parent quotations cannot supply or bridge a candidate sequence. Changed or duplicate matches stay visible; localized marker paragraphs remain ordinary text.

Malformed or unsupported input returns one whole-source visible block. The demo constructs known paragraph/blockquote/br elements and text nodes, never sender HTML or locations derived from a repaired DOM. Ten pure HTML tests cover interleaving/entity equivalence, astral UTF-16 ranges and CRLF, changed/duplicate matches, unsupported/nested markup, invalid references and parent-quote exclusion:

```sh
node --test email-next/evidence/html-quotes.test.mjs
```

This narrow experiment does not recognize general Gmail/Outlook markup, classify localized reply boundaries, handle arbitrary entities/inline formatting or establish production parsing/resource bounds.

## Inspectable legacy conversation demo

The local reader parses actual synthetic single-part UTF-8 MIME messages and calls the fixed-line, flowed and strict HTML reconstruction helpers. Interleaved answers stay visible; uniquely repeated quotations can expand; edited, nested and ambiguous passages remain visible or use the explicit whole-source fallback. **Original** shows the complete decoded body; **MIME source** and download preserve separate original-message evidence. Plain-text source navigation uses physical-line mappings; HTML navigation uses original decoded UTF-16 ranges.

Start the allowlisted loopback server with the configured Python runtime:

```sh
EMAIL_NEXT_PYTHON=/absolute/path/to/python node email-next/evidence/legacy-demo-server.mjs
```

Open the printed local URL. Six scenarios exercise fixed text, ambiguity, flowed text, DelSp, a missing parent that can be included locally, and narrow HTML with localized surrounding text and unsupported-source fallback. View switching preserves quote expansion and focus; no message is sent or rewritten. Fixture headers remain visibly unverified and quote relationships remain display inferences.

The separate `legacy-demo-browser-test.mjs` runner uses the existing Playwright module and one Chromium worker. Eleven sequential check groups passed, covering helper-derived maps, expansion/source navigation, exact MIME downloads, original text, focus, recomputation, HTML source ranges, inert unsupported markup and local request confinement:

```sh
EMAIL_NEXT_PYTHON=/absolute/path/to/python \
EMAIL_NEXT_PLAYWRIGHT_MODULE=/absolute/path/to/playwright/index.mjs \
node email-next/evidence/legacy-demo-browser-test.mjs
```

This browser runner is separate from the ordinary Node test gate. Broad real-client HTML/localized corpora, other browser engines and screen-reader testing remain unfinished. The fixture loader is not a general multipart/charset-recovery implementation. Source navigation does not claim byte-level highlighting inside transfer-encoded MIME.

## Group transitions through ordinary mail

`transition_carrier.py` and `transition_mime.py` carry a configured endpoint-ordered Commit as a direct MIME attachment with a readable notice. Actual loopback SMTP fixtures exchange applications before and after the epoch change. The shared checkpoint revision prevents a staged candidate from overwriting intervening send/receive ratchets. Previously prepared application ciphertext cannot be released under an outdated epoch.

The receiver retains exact commit bytes for replay comparison and exact selected carrier bytes for future-epoch processing. Deferred processing rechecks the original predecessor binding; a bare retry cannot drop it. Invalid unauthenticated wrapper metadata does not permanently prevent a separately supplied valid carrier from succeeding. The comparison's v1 context is enabled only through an explicit persisted local opt-in; unknown context versions are not generally accepted.

Seventeen group/carrier tests pass, including future-context rejection and a forced digest-index collision that must not substitute different commit bytes. `release_mime` only selects locally checked bytes. Durable submission uses the separate typed path below.

### Durable control submission

`control_release.py` prepares immutable transition MIME only from a retained, decided Commit. Recipients are explicitly mapped to devices in the predecessor group; the new device receives no Commit in place of its separate Welcome. The sender must retain send authority, the resulting roster must retain receive authority, and selected mailbox evidence is rechecked when that mode is used.

`SenderWorker.submit_control` uses a fixed local adapter contract and records control attempts separately from application attempts, even when their local labels match. It reuses the cooperating-worker lock, durable release record, pre-DATA cancellation check, recipient-specific retry and uncertain-outcome recovery. The prepared bytes are retained across retries. No database write lock is held during network I/O, and this is not an atomic transaction spanning SQLite and SMTP.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_control_release.py'
```

Seven control tests pass. They cover no decision/no socket, actual SMTP delivery into the transition receiver, revoked send authority, policy and selected-mailbox changes before DATA, separate application/control identities, process death after release and after the final SMTP response, exact-byte uncertain retry, partial-recipient retry and a newer epoch holding an older prepared control. The combined application-sender, mailbox-selection, control and carrier regression run passes 52 executions.

This intermediate path requires the current group to remain at the exact decided resulting context. It therefore does **not** support historical transition catch-up after a later epoch is installed. The historical adapter below supplies a separate catch-up path for supported transitions. The separate [established Welcome adapter](#durable-established-welcome-delivery) supplies signed context-v1 admission delivery. It does not broaden this Commit adapter's release rules. Safe writer failover, service/quorum ordering and the final distributed architecture also remain unfinished.

### Historical control catch-up

`commit_history.py` retains exact accepted Commit bytes and public predecessor/result metadata without requiring old sender checkpoints for retransmission. `historical_release.py` and `SenderWorker.submit_historical` use a separate fixed adapter: each release proves a contiguous retained path to the current group and checks continuous target-device membership and current authority. Ordinary application and current-control gates remain unchanged.

Each device/mailbox plan submits its selected transitions in order. SMTP acceptance advances dispatch progress, not a claim about the receiver's epoch. A changed tip after release aborts before DATA; a new attempt can prove the extended path. Uncertain retries retain the same MIME. Completion and cancellation archive public path and attempt evidence before unpinning; cancellation does not claim non-delivery.

Eleven history tests and thirteen dispatch tests pass, with real MLS advancement, a new application after two missed Commits, future-first processing, process death after SMTP acceptance, explicit retry, changed tips and signed authority loss. Parent runs separately verified the eleven history cases with nine transition regressions, and all thirteen dispatch cases. Five dispatch cases use actual verified advertisements and selection APIs: exact mapping succeeds, while disable/re-enable, replacement, a change before DATA and same-principal device substitution hold sending.

The configured model supports additions, self-updates and survivor catch-up across removals. A receiver that already knows a revocation holds an intermediate addition without consuming its private Commit key. The [atomic recovery path](../group-conversations.md#catching-up-through-a-revoked-member) accepts a caller-supplied complete sequence under explicit retention policy; it never activates the intervening epoch. Rejoin, writer failover, public cursor proof, distributed ordering and archive cleanup also remain unfinished. Retained ledger bounds are not a total database limit; full-map checkpoint secret retirement and WAL/backup erasure are separate unresolved work.

### Configured removal and membership periods

`group_transitions.py` and the Rust worker support removal-only requests naming exact device credentials and signing keys. Leaf indices come from the locked predecessor. The committing administrator must remain authorized, and every surviving member must retain receive authority; a revoked predecessor leaf need not regain authority before it can be removed. Mixed Add/Remove proposal lists are rejected in this bounded experiment.

`membership_episodes.py` records admission and removal boundaries with the accepted transition. Direct receive and pending-operation reevaluation check the current membership period as well as account authority. Membership-only removal therefore blocks new effects even when the account key remains valid. Already accepted contributions remain part of history. Configured stores missing these records require migration; the experiment does not infer old periods from today's roster.

Nine tests in `test_group_removal.py` cover actual signed revocation, removal while application authority is held, exact targets, transaction rollback/retry, pending encrypted answers, accepted history, survivor catch-up through real loopback SMTP, inactive removed endpoints and missing membership records. The evicted endpoint's staged serialized GroupContext differs from the survivor's finalized context; group, epoch, application context and roster agree. The receiver retains terminal evidence without asserting the survivor's context commitment or inserting a reusable historical decision.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p 'test_group_removal.py'
```

Accepted reusable transitions retain the identity heads, binding checks and membership changes authorized in their acceptance transaction. Historical validation uses that evidence without demanding current receive authority for an already removed old member; release still checks the current committer and full current roster. Older ledger entries without accepted authorization evidence hold rather than being backfilled from current state.

The [direct established admission experiment](#established-membership-instances-and-direct-rejoin) supplies a separate configured rejoin path. A separate [durable Welcome adapter](#durable-established-welcome-delivery) supplies local context-v1 submission. Atomic multi-Commit recovery has separate local evidence; legacy consumed-key migration, failover and secure erasure remain unfinished. These results do not establish general historical-epoch application processing or recall already handed-off ciphertext.

### Terminal removal notification

`terminal_removal_release.py` submits only an already-decided removal Commit to its exact removed predecessor device. `terminal_routing.py` checks the original authenticated observation and unchanged selected mailbox generation/anchor, preserving its original expiry. Its result is explicitly terminal-only routing evidence; it cannot grant ordinary current device authority. Current committer and surviving-roster checks still apply.

The fixed sender adapter retains exact MIME across uncertain retries, rechecks route and tip before DATA, and records transport handoff separately from receiver acceptance. Completion/cancellation archives public decision and attempt evidence before unpinning. A removed endpoint missing the predecessor remains pending; the adapter never supplies secret-bearing catch-up. An observed target rejoin holds the old notice.

Fifteen tests in `test_terminal_removal.py` cover an actual revoked receiver, exact terminal bytes and inactivity, expired/collided/mismatched evidence, route replacement/disable, a second-connection change before DATA, real signed committer authority loss, changed tips, altered MIME, explicit uncertain retry, process death after SMTP acceptance, evidence-preserving cancellation and an offline target missing its predecessor. Fifty-seven existing sender/control/historical regression executions also pass. The rejoin hold is implemented; separate direct-admission tests now exercise fresh-Welcome rejoin, but this terminal suite does not combine that flow with notification dispatch. Archive cleanup, independent mailbox ownership and deployed transport remain outside this experiment.

## Established membership instances and direct rejoin

`group_instances.py` and `established_invitation.py` connect retained membership evidence to direct signed Welcome admission. The configured version-1 group keeps each admission in a distinct local instance. Accepted history remains available; pending contributions from an inactive instance cannot gain effects after rejoining.

Migration requires retained installation and transition evidence. Ambiguous history rolls back qualification instead of assigning it to the newest roster. Admission checks an independently selected creator and exact context, current device bindings and the actual package across the entire signed validity interval, and the authenticated Welcome's group, epoch, roster, signer and finalized context. Package consumption, checkpoint replacement, episode links and acceptance evidence commit together. Previous-epoch and Commit commitments remain signed inviter assertions because the joining device cannot decrypt the predecessor Commit.

Seven migration tests and five direct-admission tests pass. Actual MLS cases include same-signing-key rejoin with a fresh package, continued hold of an old pending answer, acceptance of new ciphertext, and later removal affecting only the current instance. Failure cases cover rollback, conflicting replay, invalid context and overlong signed validity without package consumption.

The direct API is complemented by the [durable established Welcome adapter](#durable-established-welcome-delivery) below, including joined SMTP rejoin and context-version-2 application agreement composition. Advanced-history instance migration, distributed ordering and restore protection remain unfinished. Initial fixed-roster admission qualification is covered [separately](#signed-initial-membership-instances). Configured retention now retires known obsolete live checkpoint copies in transition and admission records while preserving public decision, consumption and retry evidence. Database journals, backups and physical storage still prevent a claim of secure secret erasure. See the [group requirements](../group-conversations.md) for the remaining lifecycle boundaries.

## Durable established Welcome delivery

`established_invitation_release.py` and `established_invitation_mime.py` connect a retained membership decision to a signed Welcome sent through loopback SMTP. The fixed `SenderWorker.submit_established_invitation` adapter preserves the exact MIME, selected mailbox generation and device evidence across retries. It checks the complete signed validity interval against the actual package and current bindings. The recipient checks the delivered Welcome through the direct admission API above.

The experimental local ordering policy requires successful Commit handoff for every remote predecessor device before Welcome handoff. It checks recipient/device mappings in retained control records. Shared account mailboxes require separate device submissions backed by exact checked association evidence; one SMTP acceptance cannot count for different devices. Missing, partial or uncertain handoff holds the Welcome. This is local SMTP ordering evidence: existing clients may still be offline or have not processed their Commit.

Release also requires the original target admission episode to remain active, the configured writer and current roster to retain authority, and the selected mailbox evidence to remain unchanged. Accepted later transitions may extend the history while preserving those conditions. A tip or dependency change after release stops transmission before DATA. Removal and rejoin cannot revive an old prepared Welcome.

Run `test_established_invitation_release` with the existing integrated Python/MLS setup. Its 12 tests cover actual delivered admission, incomplete and uncertain predecessor handoff, recipient-specific retry, unbound shared-mailbox rejection, selected-route changes, later tips, pre-DATA cancellation, target removal, immutable retry, preparation rollback, distinct MIME selection and process death after server acceptance. Explicit completion or cancellation archives public evidence before releasing retention pins; cancellation of an uncertain attempt does not assert non-delivery.

The version-0 success case deliberately leaves existing clients without processing their Commit. The separate `test_established_application` suite joins actual Commit and Welcome SMTP handoff, context-v2 admission, removal and same-key rejoining with a fresh package. The new instance accepts new contributions while an unresolved reply from the ended instance remains held.

### Signed application selection for established invitations

The experimental established payload version `1` uses signature domain `email-next/mls-established-membership-invitation/v1` with the existing domain framing. Its exact version-0 fields gain `applicationAssertions`: one `{principal, device, digest, signature}` reference per resulting member, in roster order. The outer wrapper gains an equally ordered `applicationAssertions` array of signed version-1 discovery wrappers. The selected context is version `2` with designated-member ordering; this does not broaden the initial fixed-roster invitation contract. Version `0` retains its existing shape and domain.

`transition_support.py` records an explicit current confirmation with its actual acceptance time, epoch and membership period. It requires the already selected application profile and independently accepted current device authority. The accepted Add decision retains exact source references; preparation cannot replace the target proof with a later advertisement. A current confirmation never claims the device advertised support in an earlier epoch. Retained established-version-1 admission proofs can also supply the exact historical source without a new confirmation. Reuse requires the same local instance, an uninterrupted membership period, unchanged signing key and exact context/profile, and agreement provenance matching the accepted signed invitation. A surviving endpoint records a returning member's fresh source under a new membership period; it cannot use that member's ended period to reactivate pending actions. The returning endpoint itself receives a new local instance.

Public initial-version-1 invitations remain fixed-roster. Their evidence cannot be reinterpreted as designated-writer agreement, and no transition from that initial mode to an evolving group is defined here. A separately reviewed ordering/admission contract is still needed for that path.

For existing members, **historical profile selection is an inviter assertion**. The joining device verifies each referenced signature against the independently authorized current member key and checks support for the exact selected profile. It cannot independently reconstruct the group's past selection from the Welcome. An existing member's historical assertion may have expired; its expiry does not revoke an established agreement. The target's assertion is different: its exact package, identity binding, mailbox and complete invitation interval must be current. All resulting members and the inviter still undergo independent current role and binding checks.

The recipient atomically installs exact per-device agreement and proof provenance in the new membership instance. It does not copy agreements from an ended instance or reactivate old pending actions. The focused application suite also checks historical confirmation expiry, rejection of a replacement target proof, overlong target validity and proof substitution. Broader signed-origin migration, real-provider transport, distributed ordering and independent implementations remain unfinished. These established-delivery tests are not included in the initial-invitation acceptance manifests. The candidate MIME type is unregistered; local identity and mailbox associations remain explicitly unverified ownership.

## Configured hosted bearer access

The hosted experiment creates an immutable text grant, serves a deliberate browser retrieval flow, retains holder-attributed replies and submits a minimal notification through loopback SMTP. Management authority is independently configured; possessing the invitation does not prove mailbox ownership or provide end-to-end encryption.

`hosted_access.py` serializes creation, replies, expiry and revocation in SQLite. `hosted_vault.py` protects exact credential-bearing requests with AES-GCM, fresh nonces and separately supplied keys; expected roles and row bindings form authenticated associated data. The sender, host request and host reply roles remain separate. Current bearer access stops after expiry or revocation, while authorized management can inspect historical receipts. These are configured keys, not a production keystore or recovery design.

`hosted_management.py` uses fixed direct HTTPS routes and retains authenticated response provenance bound to the exact prepared request. It rejects redirects and unrelated receipts; a well-formed contradictory result for the exact request is retained as conflict. `hosted_notification_release.py` consumes those local evidence records, checks current configured routing, policy, credible expiry and known revocation/conflict, and decrypts only the immutable notification needed for submission. A second check runs before SMTP DATA. The older `hosted_notification.submit` raw-receipt helper is not accepted provenance for this path.

Each submission has durable attempt history. The canonical database lock and process ownership checks prevent cooperating workers from transmitting concurrently. `reconcile` marks an abandoned release uncertain without inferring delivery. Temporary rejections permit another explicit submission; uncertain outcomes require `retry_uncertain=True`; accepted and permanently rejected notifications cannot be resent. Retries use identical MIME bytes. A historical creation receipt does not guarantee that the remote grant is still active, and SQLite plus SMTP is not one atomic transaction.

```sh
python -W default -m unittest discover -s email-next/evidence -p 'test_hosted_access.py'
python -W default -m unittest discover -s email-next/evidence -p 'test_hosted_release.py'
node email-next/evidence/hosted-response.test.mjs
```

Ten backend tests and eleven release tests pass. They cover real subprocess crashes, encrypted storage, distinct authorities, inclusive expiry, retained management evidence, actual configured TLS and SMTP, conflicting receipts, policy changes before DATA, temporary/permanent failures, explicit uncertain retry, canonical lock contention and inherited-worker rejection. The release run used Python 3.14 with resource warnings enabled and none emitted.

The separate `hosted-browser-test.mjs` runner uses the configured Python, Playwright and Chromium executable. It checks actual HTTPS entry, fragment removal, empty persistent storage, inert initial loading, explicit retrieval, bearer headers, holder replies, and rejected fetch redirects. Deliberately broken entry redirects demonstrate that script cannot prevent pre-load fragment forwarding. The browser fixture pins its ephemeral certificate key; it does not establish deployed public trust or complete PKIX validation.

`hosted_reply_admission.py` derives a create-v1 limit from the exact retained observer template using the shared event serializer. `hosted_reply_export.py` receives historical replies only through the fixed authenticated management transport, checks exact request/receipt/destination binding and commits encrypted export provenance atomically. Old create-v0 grants remain distinct. The limit can reveal overhead and support size inference; no roster identities are explicitly included in it.

Seven additional export/admission tests pass: actual escaped-text equality and one-byte overflow, immutable template binding, maximum 1 MiB request export with longest configured DNS origin, unchanged ordinary event limits, post-revocation management access, malformed/contradictory exports, encrypted DB/WAL checks and subprocess crashes around provenance commit. The nine event-encoding regressions also pass. The hosted browser runner additionally preserves a draft after HTTP 413 and submits a shortened replacement.

### Original hosted messages, questions and holder observations

`hosted_disclosure.py` records an explicit local author plan for an exact message or question and configured external grants. The plan authorizes provider access before later mail delivery. Normal protected preparation requires every declared origin to have its plan; a mixed plaintext/provider declaration requires both kinds of authorization. Multiple grants at one origin produce one descriptor, with no grant IDs or recipient counts in that descriptor. External recipients stay outside the protected group.

The source-bound management adapter creates grants only for a locally prepared contribution with current author, context and policy checks. Released requests have durable uncertainty and exact-byte reconciliation; loss of a response does not authorize a replacement grant. The bound notification path rechecks the original plan before DATA. Ordinary protected submission also enforces the plan at release and pre-DATA, so a different entry point cannot bypass withdrawal. Once hosting has occurred, withdrawing local delivery authorization does not erase that historical external disclosure.

`HostedObserverRelease` consumes only persisted authenticated export evidence in the same canonical SQLite database as identity and MLS state. It commits the immutable holder-to-event mapping, staged encryption, local author evidence and checkpoint together. The original target must have accepted received evidence or exact local author evidence. `SenderWorker.submit_observer` rechecks source conflicts, target, current device/context and policy; ordinary application submission cannot substitute for that fixed path. The receiver displays the observer's principal and grant-holder attribution, not a verified holder mailbox identity.

Seven observer tests and seven original-disclosure tests pass. The joined path performs actual local HTTPS creation and holder POST, minimal notification SMTP, protected original delivery with its declaration, authenticated export, observer MLS and receiver acceptance. Cases cover revoked bearer/history, restart deduplication, wrong audience/device/context, source conflicts, post-RCPT policy withdrawal, mixed plans, multiple grants, lost creation response and real subprocess crashes around release and the shared commit. The normal local application journal contains readable application content; vault encryption does not claim whole-database encryption.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
PYTHONPATH=email-next/evidence \
python -W default -m unittest test_hosted_observer test_hosted_disclosure test_hosted_questions
```

`hosted_projection.py` preserves the existing raw message-text branch and obtains question text from the authoritative `project-event.mjs` / `projectReadable` path. All choices, ordering, instructions and sharing declarations participate in exact-content checks. The plan retains its selected source text; changed formatter output holds creation/notification, and observer checks use the same helper. Older plan rows without retained source text are held rather than guessed or silently rewritten.

Three hosted-question tests pass: the actual joined question/holder/observer path, label/order/formatter mismatch, and overflow without truncation. Number and matching-label replies remain observations, with no structured answers or answer heads added. The separate hosted browser runner also passed in question mode (`EMAIL_NEXT_HOSTED_QUESTION=1`), displaying Unicode and markup-like choice labels as inert text while retaining the existing entry, reply and redirect checks. Public management authorization, production SMTP/TLS, independent client interoperability, deployed origin isolation and credential/key recovery remain outside this milestone. Account-bound and independently authorized cryptographic-endpoint models are separate work.

## Joined question and ordinary reply

The conversation interface uses an open message layout, with answer buttons alongside their question and a bottom composer for an ordinary-email participant. A contact-name conversation list separates Contacts and Other, and sorts by the latest actual local activity. Switching threads retains separate unsent drafts. Contacts in this demonstration are synthetic configured entries; it does not read the user’s address book. The sender-address ghost button selects one of two configured ordinary-email accounts and retains that choice per draft. The server resolves its account ID to an enabled local sending grant and rejects arbitrary From fields or withdrawn accounts. Both composer accounts remain unencrypted; choosing one does not create an MLS identity, grant membership, or change the separate protected-answer fixture. The composer shows its selected reply target and a thin looped connector to the message, defaulting to the latest message in view. **Open thread** focuses a reply branch in the same pane; **All messages** returns to the broader view. **New thread** requires a title and sends only the new body, without reply headers or copied history. Selecting an earlier reply uses its retained local target and actual email Message-ID; a browser cannot supply arbitrary reply headers. These are client presentation and composition choices; legacy reply relationships remain unverified email evidence. Each received reply remains in arrival order for the demo session. Technical delivery details are available through each message’s disclosure; protected and ordinary messages remain visibly distinguished. Ordinary replies use their actual reply header to select the retained ordinary question. Unique exact fixed-line quotations collapse behind **Quoted text**; changed or ambiguous text stays visible. Each ordinary reply retains a downloadable original email. This joined view does not yet apply the separate reader’s HTML or flowed-text paths. The session timeline is ephemeral and does not demonstrate persistent mailbox synchronization.

The standalone server also populates Sam's conversation with nine ordinary synthetic messages across hiking, photos and dinner. Three independent roots, replies within each topic and a late reply to the original hiking message make branch navigation inspectable. These messages pass through loopback SMTP, retain their original bytes and carry actual reply headers. Select Sam, open a message to focus its descendants, and use **All messages** to return. `--minimal-fixture` disables these extra samples; direct `serve()` callers keep the smaller test fixture unless they request `samples=True`.

The local conversation demonstration sends a real MLS-protected question, lets Bob choose an answer in the browser, and receives his authenticated answer through loopback SMTP. A separately authorized ordinary-email copy reaches a legacy fixture. Its textual reply appears alongside the protected exchange with ordinary-email attribution; it never becomes a structured answer.

`client_flow.py` retains a stable local action and exact event before preparation. `SenderRelease` atomically retains local author evidence, the journal entry, prepared MIME and updated checkpoint. This allows Alice to resolve an answer against her own question without manufacturing received-MLS evidence. `application_agreement.py` records explicit agreement for each exact group/device/signature key. Sender and receiver require the exact authenticated application context and selected operation; parsing a version-1 envelope is insufficient. The demo defaults to raw-event context 2; `--mime` explicitly selects configured MIME context 3.

`plaintext_release.py` records an explicit immutable question-copy plan bound to exact contribution bytes and policy revision. It reuses the readable projector, prepares separate multipart/alternative MIME, and submits through the worker's fixed `configured-plaintext-submit-v1` path. Protected MIME has no readable question beside its ciphertext. This demo uses question copies with configured addresses; the separate ordinary-copy tests also cover answers, reactions and withdrawals. Neither establishes mailbox ownership or general fallback for every operation. Changing policy holds a prepared copy under the shared release checks. SMTP uncertainty and retry remain the existing worker's responsibility.

The focused joined tests cover actual submission in both directions, restart, stable action retry, duplicate receive, a third observer receiving the answer before the question, missing per-device agreement, and a real signed identity successor removing Bob's send role while retaining receive. The browser check covers the button, ordinary reply, readable source, safe text rendering and rejected requests without the local session token. The demo reuses the synthetic joined-test deployment; it is not a production account interface.

Run the local demo with the evidence directory on `PYTHONPATH`, `EMAIL_NEXT_MLS_BIN_DIR` pointing to the built worker directory, and the configured Python interpreter:

```sh
python client_flow_server.py --port 8765
```

Open the printed loopback URL. `client-flow-browser-test.mjs` uses the configured Playwright module and `EMAIL_NEXT_PYTHON` to exercise the flow automatically. Set `EMAIL_NEXT_CLIENT_MIME=1` for the configured MIME variant. Both modes have passed the same browser flow: answer, two distinct reactions, withdrawal, ordinary reply, inert text rendering and session-token rejection. One foreground browser runner is used.

This demonstrates one implementation with synthetic accounts and configured application agreement. Independent clients, real providers, public application negotiation, production persistence and general mixed-delivery policy remain separate acceptance work. The demonstration does not convert an ordinary email author's header into a cryptographic identity.

## Signed application agreement at admission

`signed_application_admission.py` joins actual signed application advertisements to the retained identity, selected mailbox association and MLS package-admission path. Every selected device must support the complete chosen operation set and ordering mode. Complementary support cannot be combined into a capability that no individual device supports.

The target commits exact assertion/signature provenance, selected application agreement, membership episodes, package consumption and the authenticated MLS checkpoint in one SQLite transaction. A real process-exit test before commit leaves all of them uninstalled. Current identity head, binding and mailbox generation are checked inside the transaction. The creator additionally needs send authority and must be the authenticated Welcome signer. The caller's explicit trust policy is preserved.

Established signed agreement is separate from advertisement freshness. Exact accepted retries remain valid after advertisement expiry, and a subsequent real encrypted contribution can use the established agreement while device authority remains current. New admissions using expired evidence are held. The configured-device API cannot overwrite signed-admission evidence.

Seven focused cases cover actual signed admission and application receive, complementary support with a successful common subset, stale identity and mailbox evidence, strict trust, expiry, rollback and process exit. The retained assertion pair is the replay identity; reserialization of the independently signed identity bundle does not redefine that pair.

This lower-level experiment uses the local test invitation carrier in `provider_mls.py`. The separate [version-1 initial invitation](#version-1-initial-invitation-and-durable-submission) supplies the candidate ordinary-mail carrier for context 2; version-0 invitations retain their exact original restriction. Neither experiment independently verifies mailbox ownership or advertises hosted-holder-observation support.

## Version-1 initial invitation and durable submission

`application_invitation.py` implements the exact version-1 carrier with signed references to both devices' application assertions and embedded-tree-only MLS admission. `application_invitation_release.py` verifies the creator's retained identity and selected-mailbox evidence, checks the actual target package across the invitation interval, and atomically records the initial group, signed agreement, membership episodes and immutable invitation delivery. `SenderWorker.submit_initial_invitation` is a fixed local adapter, not a remotely chosen transport or trust mode.

The joined tests submit actual MIME over loopback SMTP, admit the target through the versioned carrier, and receive a real protected contribution afterward. Receiver checks cover proof substitution, signature-domain separation, direct carrier selection, missing embedded tree, local association requirements, transaction failure and process exit. Sender checks cover preparation rollback, no prepared record/no socket, policy changes before DATA and a process exit after SMTP acceptance followed by an explicit uncertain retry of the same bytes.

The target retains exact signed application provenance in the same transaction as package consumption and checkpoint installation. Creator-side `signed-initial-creation` agreement references its immutable preparation record. Ordinary configured-device APIs cannot overwrite either signed provenance kind. Accepted assertion identity binds both payload bytes and signature, while separately signed identity bundles can be reserialized without changing that identity.

Version 0 remains separately implemented and unchanged. This is a working candidate for initial two-device fixed-roster conversations, not proof of multi-device established-group admission, final distributed ordering, public provider deployment or independent interoperability. The MIME type remains unregistered. Synthetic account decisions remain unverified mailbox ownership, and local SMTP acceptance never means that the target joined.


## Designated-writer initial invitation

The initial invitation experiment accepts an explicit version-2 branch for context version `2` with designated-member ordering naming the creator device. The creator is the sole initial administrator. Its fields and assertion-reference encodings match initial version `1`, but its signing domain is `email-next/mls-new-conversation-invitation/v2`. Both exact device proofs must be assertion version `1` and advertise the selected operations under designated-member ordering. The existing version-1 fixed-roster branch remains unchanged. Initial version `2` also accepts context version `3`, with either fixed-roster or creator-designated ordering, only through signed assertion-version-2 tuples matching the exact payload, ordering and operations. Context version `2` retains its assertion-version-1 designated branch; proof versions are never interchangeable.

Creation requires an explicit designated choice; recipient admission requires independently selected exact context bytes. The current two-device initial stage is an implementation limit, not a limit on the intended protocol. This starts a new evolving conversation; it cannot reinterpret an existing fixed-roster conversation or its history.

Original signed proofs, consumed package, checkpoint, instance and agreements commit together. Later additions may reuse those exact initial proofs for uninterrupted members with unchanged keys and profile. A missing fresh advertisement does not erase accepted historical selection, but current identity and role authority still apply. A new member requires fresh package and support evidence. Original assertions are not replaced by current cached advertisements.

`test_designated_initial` has three focused checks. The joined case creates a conversation over loopback SMTP, sends an actual Add Commit to the existing peer, then delivers an established Welcome to a third device using the original member proofs. Other checks reject missing independent context selection, incompatible version/context and signature-domain combinations, and verify rollback and accepted replay. This does not establish distributed ordering, real-provider interoperability or generalized initial multi-device admission.

## Signed payload-tuple invitations

`application_support.py` checks exact per-device tuple coverage for the selected profile. Initial invitation version `2` selects context version `3` with assertion version `2`; established invitation version `2` uses the same context and proof versions under designated ordering. Their respective signature domains remain distinct. Established fields preserve the prior schema, including ordered per-member assertion references, exact context and prior/result context commitments. Unknown or mismatched versions do not fall back to older proof interpretation.

Recipient initial-version-2 and established admission require independently selected exact context bytes. Current role, binding, selected mailbox evidence, complete invitation interval and actual target package checks still apply. Existing-member proof reuse retains the original instance and membership-period provenance; an expired historical assertion is not fresh authorization. Stored agreements include the selected payload format, so raw event and MIME support cannot be combined into a capability neither device advertised.

`test_tuple_invitations` exercises signed assertion2 → initial2 over SMTP → actual protected body MIME over SMTP → Add Commit → established2 Welcome for a third device. It also checks fixed-roster context3 without designated opt-in, wrong signature-domain rollback/replay and rejection when only another payload tuple is supported. Submission diagnostics identify the parsed wire version; internal worker dispatch keys remain separate implementation identifiers.

The lifecycle permits `attachment-message` only for the exact context3 `mime-contribution-v0` tuple, subject to the same complete device intersection. Old profiles and raw-event tuples retain their restrictions. Signed attachment receipt, resource reading and client download require their own joined tests; this body-carrier milestone alone makes no attachment or embedded-media rendering claim. Independent implementations and deployed-provider carriage remain untested.

## Protected reaction client flow

The configured client demonstration now sends a protected reaction and an explicit withdrawal through the existing durable application sender, loopback SMTP and actual MLS receiver. Two deliberate equal reactions remain two events; retrying one action reuses its exact prepared bytes. `client_reactions.py` selects authorship, audience and withdrawal references from local authenticated state. Browser input cannot grant those authorities. The browser check exercises compact emoji chips, adding two emoji and removing one without removing the other, alongside the structured answer and ordinary replies. Chip counts show people per emoji while authenticated duplicate events remain retained.

`receive-reaction.mjs` and `reevaluate-mls-reactions.mjs` require the operation in an authenticated context-v2 profile and a matching durable agreement. The receiver resolves targets only from accepted journal history, after answer authorization; its intermediate decrypted candidate index is not target authority. Additions are admitted before withdrawals, and a withdrawal with missing dependencies removes nothing. `journal_reaction_view.py` derives a versioned presentation snapshot; that helper itself does not authenticate inputs or establish membership-instance authority.

Run `test_joined_reactions`, `test_signed_reactions`, `test_journal_reaction_view` and `receive-reaction.test.mjs` for the focused paths. They cover actual protected delivery, reordering, restart, exact retry versus separate equal events, all-or-nothing withdrawals, pending answer targets, current signed send revocation and per-device signed support intersection. The signed test uses the versioned initial invitation MIME carrier over loopback mail before a real protected reaction. Existing contexts remain unchanged; installing newer software does not add reactions to their selected operation list.

The configured designated-writer comparison now checks the same immutable application profile for predecessor members and explicitly configured added devices. `test_reaction_removal` proves actual membership removal holds a pending reaction even while its account/device retains send authority. With default zero retention, the delayed previous-epoch target is rejected cryptographically. The separately configured [secret-retention experiment](#bounded-secret-retention-and-delayed-application-delivery) now receives that original target after removal and restart while keeping the removed sender’s pending reaction held. Fixed-roster transitions remain forbidden. The separate [established Welcome integration](#durable-established-welcome-delivery) adds signed device support and context-v2 application agreements.

Ordinary RFC9078 MIME does not enter this authenticated journal. The candidate MIME generator/selector remains separate from this protected raw-event flow. [Joined protected carriers](#joined-protected-carriers-and-deliberate-attachment-download) add encrypted compound MIME, while the ordinary-copy tests cover explicitly authorized reaction and withdrawal fallback. Those paths retain their own profile and disclosure checks. No real-provider deployment, independent-client interoperability or assistive-technology acceptance is claimed.


## Bounded secret retention and delayed application delivery

`secret_retention.py` and `retention-staged.rs` provide an explicitly configured local policy for delayed encrypted mail. Existing fixtures retain the OpenMLS default of zero past epochs until configured. The policy selects epoch count, age, serialized checkpoint bytes, out-of-order tolerance and maximum generation distance. The test values are adjustable experiment settings, not protocol requirements. `test_secret_retention.py` and `test_secret_retirement.py` exercise the actual pinned OpenMLS library.

A retained application is checked against its original accepted epoch snapshot and membership instance. The receiver never labels an old message as current or restores an old checkpoint to decrypt it. A real delayed target can arrive after a membership removal and restart; the removed sender's pending reaction still fails its current episode check. Missing or conflicting historical context holds processing. Deleted secrets produce retained ciphertext with a failure reason, without automatic history recovery or plaintext downgrade.

The library prunes actual past message-secret entries by count and cutoff time. Sender-ratchet configuration bounds generation jumps. Maintenance measures the serialized active checkpoint; if deleting all past secrets cannot meet the selected byte budget, the public coordinator retires the local group. A caller-owned preparation transaction fails and rolls back oversized staged growth, preserving its already-maintained bounded checkpoint. It must perform maintenance before starting that transaction; the hosted observer coordinator does so. Checkpoint bytes are a secret-state budget, not a quota for all mailbox content, attachments or public history.

Maintenance runs before receive, ordinary sender preparation/submission and configured control preparation/decision/receive, and after staged checkpoint changes. An explicit maintenance entrypoint supports startup or a client-owned timer. Removed endpoints can maintain their remaining stored secrets without reactivating membership. No cleanup runs while the process is closed; retained-at-rest exposure during inactivity remains a limitation. Credible local clock intervals and a persisted nondecreasing cutoff prevent rollback from restoring expired history. Unknown clocks hold active processing. At the exact library boundary, a secret timestamp equal to the cutoff remains; an earlier timestamp is pruned. Legacy entries without timestamps are removed by the library's explicit API.

Logical retirement also removes known private checkpoint fields from finalized control records and consumed admission caches. Undecided private candidates become terminal abandoned records when maintenance changes their source checkpoint; regeneration requires fresh authorization. Exact wire, public snapshots, authorization, signed requests, package-consumption evidence and public admission receipts remain. The older internal provider helper's retired result carries `privateState: "retired"` and no checkpoint; it cannot restore a joined group on retry. Public invitation receipt retries remain unchanged. A legacy unconsumed package checkpoint containing group-secret storage records holds maintenance for explicit migration; the adapter neither silently destroys active admission material nor claims those copies were pruned. An uncertain SMTP attempt still requires an explicit retry and uses the retained identical ciphertext.

Tests cover actual delayed decryption, removal authority, age/count/generation bounds, exact age cutoff, legacy timestamps, clock rollback/absence, storage retirement, missing/conflicted snapshots, send-only/control-only/inactive maintenance, subprocess exits before and after commit, consumed-package retirement and uncertain ciphertext retry. Timestamp-boundary tests alter only fixture timestamps in the pinned storage representation; secret bytes and ciphertext remain real. Logical live-row removal does not establish physical erasure from SQLite pages, WAL, backups, swap or process memory, and this is not a production security audit.

## Signed initial membership instances

`signed_initial_instances.py` qualifies the retained creator and recipient records of the public version-1 initial invitation. Both sides derive the same membership-instance identifier from the exact signed invitation. Their provenance remains distinct: committed creator preparation and accepted recipient admission. New installations record this qualification within the original transaction.

The helper verifies retained signatures, original device agreements, accepted selection evidence and current epoch-1 membership. Existing received messages keep their original instance, acceptance and view state. It neither decrypts them again nor replaces a checkpoint. Expired evidence can still describe history; current revocation continues to prevent new effects.

Eleven focused tests pass, using actual signed invitations and MLS messages. They cover creator/recipient agreement, exact receipt replay, prior accepted and pending messages, restart, process interruption, retired cached secrets, expiry, signed revocation, conflicting records and retained-epoch indexing. Run them with the integrated dependencies and shared workers built:

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
python -m unittest discover -s email-next/evidence -p test_signed_initial_instances.py
```

This covers the two-device, context-version-2 **fixed-roster** initial state at epoch 1. Advanced, terminal, rejoined, configured signed-admission and designated-writer histories require separate migration paths. Ambiguous history is held; a current roster cannot substitute for missing original evidence. The helper is not backup rollback protection or a complete membership lifecycle implementation.

## Durable readable interaction copies

`plaintext_release.py` now prepares ordinary copies of messages, questions, answers, reactions and reaction withdrawals through the existing fixed sender worker. `plaintext_projection.py` and its Node bridge resolve references only from the accepted contribution journal, including locally authored records admitted by the sender pipeline. Missing or conflicting dependencies hold preparation. The stored disclosure review covers the exact plain text, inert HTML, subject, reference mapping and generated-header policy. Answers therefore require local authorization for the copied question and option label; reaction copies disclose references without copying target text. This is a trusted local remembered-policy API, not a requirement for a new dialog on every send or a browser-supplied authority flag.

The ordinary copy contains plain/HTML alternatives only; it does not add a structured event alternative to earlier approvals. A reaction with a recipient-specific known Message-ID mapping adds the RFC9078 first part. Different mappings can use separately prepared recipient subsets; an unmapped or heterogeneous combined route remains explanatory mail. Withdrawals never produce a reaction-disposition part. Approved recipients remain in local envelope state, not the common To field. Exact prepared bytes survive restart and explicit uncertainty reconciliation; each route retains its own outcome. The adapter requires one retained exact target representation for the target EventReference and each selected recipient, with a matching single Message-ID and explicit trusted-local-import provenance. Conflicting imports hold pairing and submission. The trusted importer attests the target/recipient association; MIME parsing alone cannot authenticate it, and neither browser-supplied mapping strings nor matching subjects supply evidence. Import bounds are adjustable experiment defaults.

`test_plaintext_interactions.py` joins actual protected questions/reactions with ordinary SMTP copies, exact copied-context authorization, recipient-specific routes, missing mapping, unaccepted dependency rejection, signed send-role revocation, a policy change before DATA, and actual process death after SMTP acceptance followed by explicit exact-byte retry. Existing question/hosted regressions cover the earlier message/question interface. Old prepared records lacking the new retained review are held at release until a trusted local authorization supplies the matching review; no structured disclosure is inferred from an old approval.

These copies are ordinary mail. Their readability does not establish protected reaction authority or prove how independent legacy clients display them. Protected compound MIME remains a separate proposed versioned profile; current MLS application data is still the exact raw event.

## Candidate protected MIME entity codec

`protected_carrier.py` is a standalone explicitly selected codec, not a negotiated MLS payload change. It accepts direct plain/HTML/exact-event alternatives or the exact two-child reaction layout. It preserves the original event bytes, reports a valid reaction-part mismatch without manufacturing reaction authority, and rejects unexpected routing headers, surrounding content, duplicate parameters, nested alternatives, resource children, malformed encodings and invalid UTF-8 readable leaves. Its generator can create a reaction pair when supplied a target identifier; that low-level argument is not target-mapping evidence.

Nine codec tests plus six existing reaction-MIME tests pass. Codec cases exercise exact wire/decoded/part/depth boundaries, Unicode failure in every readable leaf, direct pairing, mismatch and ordering. The wire-byte bound is checked before parsing; Python's email parser allocates its tree before part/depth validation, and transfer decoding allocates leaf bytes before the decoded-size check. These are acceptance limits, not streaming or preallocation guarantees. The depth default of three is an adjustable experiment setting; raising it does not enable unsupported nested layouts.

Actual MLS payload selection, signed per-device payload-capability intersection, versioned invitation admission, attachments/resources and safe renderer integration remain required. Existing contexts still carry raw event bytes. This codec does not prove readable alternatives are equivalent to the structured event or establish any author, audience or effect authority.

## Established invitation acceptance report

The [established invitation manifest](acceptance-established-v1.json) checks version-1 membership invitations separately from initial conversation setup. It covers loopback SMTP admission, removal and rejoin, preservation of ended membership instances, historical confirmation expiry, immutable proof selection and package-consumption rollback. Run it with the same built MLS binaries and Python environment as the established delivery tests:

```sh
python run_acceptance.py --manifest acceptance-established-v1.json
```

The report fingerprints its declared source inputs and refuses to produce a report if those inputs change during execution. Deployed-provider carriage and an independently implemented peer remain `not-tested`. Use `--require-complete` to make either missing scenario fail the completeness gate. A successful local test run does not establish those deployment results or complete public onboarding.

## Candidate payload capability tuples

`application_tuples.py` validates and intersects exact `(envelopeVersion, payload, ordering)` combinations, with operations attached to each combination. Passive assertion version2 has its own fixed signing domain; versions0/1 retain their existing schemas and domains. The context3 shape validator requires an exact selected payload agreement, while old configured contexts retain their existing behavior. These are preparatory schema components: they do not admit a device, establish mailbox ownership or select a new payload for an existing group.

Twenty-two focused discovery/schema checks include real Ed25519 verification, older-domain rejection, unknown/duplicate tuple rejection, complementary device support and payload/ordering cross-product rejection. Attachment-message is recognized only in the MIME tuple vocabulary; no runtime advertisement is emitted by this change. Signed admission, durable agreement installation, sender/receiver payload dispatch and the complete attachment resource path remain integration work.

## Protected attachment carrier experiment

`protected_attachment_carrier.py` selects one direct body-alternatives object followed by opaque attachment leaves. It preserves the exact entity, decoded event and resource bytes, and the MIME filename/media projections for later comparison. It rejects routing headers, hidden preambles/epilogues and nested message interpretation. The wire limit is checked before parsing; part and decoded-size limits are acceptance bounds, not peak-memory guarantees.

Eight tests connect this structural selection to the existing attachment manifest checker and metadata-projection rules. Exact bytes bind successfully; changed content, duplicate resources and a Content-ID scoped to another event do not. Conflicting neighboring HTML cannot replace the structured projection. Unexpected filename/media-type differences are reported without replacing the event’s claims; specified filename sanitization and opaque composite-media projections remain expected differences. Exact combined decoded-byte and part limits are checked. These use the existing version-0 event fixture and return `validated-unverified`: neither MIME parsing nor resource integrity proves sender identity.

The configured context-3 integration now connects this adapter to MLS send/receive storage, version-1 event admission, retained resources and explicit local byte retrieval. Four joined checks exercise protected SMTP delivery and invalid resource copies. The [joined protected-carrier experiment](#joined-protected-carriers-and-deliberate-attachment-download) adds signed capability admission and deliberate browser download. Clients must not advertise protected attachment support on the strength of these codec tests alone.

## Joined protected carriers and deliberate attachment download

Context3 now selects raw-event or MIME application data from its authenticated epoch agreement. Sender records retain original event bytes separately from the exact encrypted MIME representation. Receivers preserve the source payload, extract the exact event for the existing authority and journal gates, and never retry failed MIME selection as raw JSON. Readable-projection consistency is recorded per ciphertext representation, including after delayed dependencies arrive; two MIME copies of one event can therefore have different discrepancy diagnostics without becoming two events.

The configured body/resource/client tests cover actual SMTP, question/answer/reaction/withdrawal, reordered normal and conflicting readable copies, exact event deduplication, restart, transaction rollback and strict payload selection. Attachment resources are stored per received carrier and checked against the accepted event's scoped IDs, lengths and hashes. Altered, duplicate or wrong-scope resources remain unavailable even when the independent event is accepted. A complete later copy can supply bytes without upgrading earlier bad copies. Authenticated file descriptions remain separate from MIME header discrepancies. `received_attachments.view` presents accepted descriptions and availability; `read` deliberately retrieves one integrity-complete event/resource/carrier selection, with no filesystem write, remote lookup or automatic nested-message processing.

`test_signed_attachments.py` joins signed assertion2 and initial invitation2 admission to actual SMTP delivery of an encrypted attachment and exact received-byte retrieval. The configured attachment/browser demo uses server-retained opaque selections under its existing local Origin/session checks. It displays malicious filename text without creating markup, distinguishes complete and corrupt resources, reports header discrepancies, and permits an explicit fixed-name octet-stream download only for available bytes. An arbitrary path, URL, event reference or carrier is not accepted from the download request. The MIME browser run also retains the ordinary question, answer, reaction, withdrawal and ordinary-reply checks.

Evidence at this checkpoint: eleven combined configured body/resource/client tests, one signed attachment test, and the actual Chromium MIME client browser run pass. This is a local synthetic deployment and deliberate-download baseline. Embedded media, rich HTML body presentation, independent-client interoperability, production account authentication and a complete multi-platform attachment-opening experience are not established by it. Wire and decoded-resource budgets are acceptance limits; Python MIME parsing is not claimed to enforce streaming allocation bounds or a total mailbox storage quota.

## Protected rich body and scoped images

The [rich-message contract](../rich-messages.md) defines the operation and carriage exercised here. The rich-body experiment carries an exact `rich-message` event, readable text, the selected HTML/CSS presentation, and separately identified embedded and download-only resources. `rich_carrier.py` selects the direct MIME structure; `received_rich.py` reads only an accepted event and its exact retained carrier. Resource bytes must match the authenticated manifest before the existing PNG/JPEG decoder supplies pixels to the isolated renderer. Corrupt or unavailable images retain their alternative text. An independent HTML attachment remains a deliberate download, never another rendered message.

`test_signed_rich.py` joins signed assertion3 and the common initial roster3 invitation to actual loopback SMTP, durable admission, a protected rich contribution, and exact decoded pixels. The configured tests cover corrupt image bytes, wrong-carrier selection and independent attachment retrieval. The renderer tests reject missing alternative text, remote or foreign-scope image URLs, script content and omitted readable text. That authoring check detects specific omissions; it does not establish semantic equivalence between HTML and plain text.

Run the existing browser demonstration with `EMAIL_NEXT_CLIENT_RICH=1` for its configured context4 conversation, or `EMAIL_NEXT_CLIENT_SIGNED_RICH=1` for a rich card obtained through the actual signed roster/SMTP fixture. Both use the existing isolated renderer. The browser check exercises the image's accessible name, explicit plain/rich switching, disposal when the conversation redraws, ordinary attachment downloads and the existing question/answer/reaction controls. This is one local Chromium implementation, not independent-client interoperability or a native assistive-technology assessment. The client-owned sandbox nonce permits only the generated renderer script and stylesheet under the enclosing page's policy; message HTML is never interpolated into that script or stylesheet.

An ordinary rich copy uses `plaintext_rich.py` and the durable plaintext adapter. Its retained exposure includes the complete generated MIME entity, including HTML, scoped Content-IDs, resource bytes and projected attachment headers. It excludes the structured event alternative. A trusted remembered policy can authorize that exact exposure; the experiment adds no compulsory confirmation dialog. A previous plain/HTML-only approval cannot authorize this expanded copy. Focused tests send the actual ordinary copy over loopback SMTP and verify its image bytes and immutable retry.

Limits in these helpers are adjustable experiment settings. MIME parsing is bounded at input and selected-content boundaries; no parser preallocation bound is claimed. Resource decoding remains subject to the existing decoder's limits. Established context4 membership delivery and broader deployment still depend on their separately specified lifecycle paths.


## Generalized initial roster and delayed admission

`initial_roster.py` and `initial_roster_lifecycle.py` implement the experimental initial3 carrier in [Invitations to protected conversations](../mls-invitations.md#starting-with-several-devices). A common signed roster binds every selected account/device, original capability proof and actual joining package. Each device gets a separately signed target invitation and immutable MIME message. Creator checkpoint, all messages, agreements and membership periods commit together; recipient package consumption and installation are also atomic. The exact common payload **and signature** determine the shared creation anchor.

The actual MLS tests use three principals with two devices each. Context3/assertion2 selects the existing MIME tuple; context4/assertion3 selects the rich tuple. These are explicit branches of one roster schema. Local intended principals and device inventory are independent inputs. This does not discover all of a person's devices or conceal membership/mailbox claims from the roster.

`SenderWorker.submit_initial_roster` uses the existing process fence and per-target attempt history. `submit_initial_roster_late` additionally requires an active retained `HistoricalRelease` plan proving continuous membership from the original finalized GroupContext to the current tip. It preserves the original route and identity dependencies. The modes share delivery history; switching modes cannot bypass uncertain or accepted handoff. A tip change before DATA aborts release. Existing catch-up plan completion/cancellation archives exact public path, original invitation and attempt evidence before unpinning; uncertainty remains explicit.

`initial_roster_support.py` reuses original signed proofs only in the same uninterrupted membership period, key and immutable application agreement. The joined context3 test creates the roster, accepts an Add without manually reconfirming original members, sends a delayed original Welcome over local SMTP, admits its device at epoch1, then sends and accepts the exact retained Commit. SMTP acceptance does not establish remote processing.

Focused modules are `test_initial_roster`, `test_initial_roster_lifecycle` and `test_initial_roster_catchup`. They cover target-package ambiguity, exact reference/signature binding, creator and recipient rollback, independent inventory, separate SMTP outcomes, explicit uncertain retry, pre-DATA changes, delayed catch-up and retained-proof key/profile/ended-period rejection. They do not establish deployed interoperability, hidden-recipient support, distributed ordering, restore safety or physical secret erasure. Full inventory discovery and broader real-client delivery observations remain acceptance work.

## Client-only ordinary-mail onboarding

`client_onboarding.py` joins passive MIME selection, actual signature/identity validation and the durable mailbox-association store. The caller supplies explicit local first-contact and device-target policies; received content cannot set them. Automatic ingestion cannot satisfy verification-required mode by itself. The optional `human_verification.py` adapter accepts a separately confirmed comparison through a trusted local interface; its evidence is distinct from the advertisement and does not certify provider ownership. Ingestion makes no SMTP or HTTP request. A successful initial pin and mailbox association commit together, and an exact ingestion retry returns its retained outcome. Independently authorized updates to an already accepted identity remain separate from advertisement usability: a valid conflicting successor is retained even when the accompanying capability signature is unusable.

`test_client_onboarding.py` exercises two fresh endpoint stores, each initially knowing only its own account. Actual ordinary messages travel through loopback SMTP before the receiving clients acquire peer evidence. The existing invitation sender then sends a signed invitation, the target admits it, and both endpoints exchange actual protected contributions. Additional checks cover verification-required mode, rollback before association, competing first-contact claims, later unrelated identities, restart, stripped evidence, expiry, mismatched From and missing evidence for a second authorized device.

The target selector returns an evidence snapshot, not permission to send. Admission and serialized release still validate the actual package, exact profile intersection, selected association and current authority. Evidenced-device mode reports missing devices; all-authorized-device mode holds when any required device lacks evidence. Neither mode establishes mailbox ownership. Complete device discovery and own-account synchronization remain separate work; the single-device passive format is unchanged.

The ingestion batch's adjustable limits are experiment settings: 32 messages, 8 MiB total input, 2 MiB per message and 64 direct MIME parts by default. No background account service, public credential issuance or new wire version is introduced.


## Optional human-confirmed onboarding

The [comparison contract](../mailbox-association.md#optional-human-comparison) defines the exact mailbox, principal and identity-state comparison. `human_verification_ui.py` serves the trusted local confirmation screen; received email cannot supply the confirmation gesture. Normal automatic unverified continuity remains available under its selected local policy.

`test_human_verification.py` and `test_verified_delivery.py` cover atomic comparison records, exact address scope, accepted successor continuity, strict initial-roster SMTP admission and a protected reply. Preparation and release retain the exact verification evidence; expiry or withdrawal holds delivery. `human-verification-browser-test.mjs` checks the local screen's confirmation and request boundaries. These local checks do not establish provider ownership, deployed interoperability or native accessibility. The nine-case onboarding acceptance manifest remains scoped to its original ordinary-mail scenarios.

## Rich group membership and shared mailboxes

The context4 lifecycle uses the existing configured-writer transition and delivery machinery. Established invitation3 selects exact context4/assertion3 proofs with its distinct `/v3` signing domain. Fixed-roster contexts remain fixed; older invitation versions keep their previous exact mappings. Historical existing-member selection remains inviter-attested, while target proofs/packages and independent current key authority remain current checks.

`test_rich_group_lifecycle` exercises signed common-roster creation, original-proof reuse for an Add, actual per-device Commit and established3 Welcome SMTP handoff, recipient admission, rich image pixels and explicit attachment-byte retrieval. The joined removal/rejoin path sends the terminal Commit, uses the same signing key with a fresh package, verifies a different returning instance, holds both old-instance and removed-sender pending answers, and accepts new rich traffic. Further cases reject older invitation versions claiming context4, wrong signature domains and overlong target intervals, while allowing expired original proofs to remain historical evidence. Rich initial delayed Welcome and exact Commit catch-up reuse the existing retained-plan path.

Shared-mailbox cases use separate submissions for the devices of one principal, with original signed observations and accepted attempt evidence binding each exact principal/device/key. Configured caller labels without that evidence cannot manufacture coverage. This is an experimental local ordering policy, not a device acknowledgment or a user-prescribed transport rule. Competing principal claims remain governed by the existing mailbox-association hold.

No new consensus or release lifecycle is introduced. Distributed writer failover, branch/restore recovery, hidden-recipient privacy, physical secret erasure and independent deployed interoperability remain unproven.

## Client-only onboarding acceptance report

The [onboarding manifest](acceptance-onboarding.json) connects nine local scenarios to the passive-discovery contract, including actual ordinary-mail bootstrap, protected replies, policy holds, device coverage and conflicting identity updates. It also names deployed carriage and independent-peer scenarios that have not run.

```sh
EMAIL_NEXT_MLS_BIN_DIR=/absolute/path/to/shared-target/debug \
EMAIL_NEXT_PARSE5_MODULE=file:///absolute/path/to/parse5/dist/index.js \
python email-next/evidence/run_acceptance.py --manifest acceptance-onboarding.json
```

Use the configured evidence Python environment and built workers. Add `--require-complete` to fail while deployment scenarios remain untested. A default successful run proves only its named local checks. Source hashes cover the shared implementation dependency set; they do not imply that every fingerprinted module was exercised. Independent identity verification and complete account-device synchronization are not implemented by this report.

## HTML parser differential and inherited titles

`html-parser-browser-test.mjs` runs eleven sequential Chromium fixtures and compares their inert projections with html5lib 1.1 through `html-parser-differential.py`. Set `EMAIL_NEXT_PLAYWRIGHT_MODULE` and `EMAIL_NEXT_PYTHON` to existing local runtimes. The runner reports raw-tree and filtered-tree agreement separately; it does not hide differences or certify a parser.

Chromium153.0.8010.12 and html5lib1.1 agree on all eleven filtered trees. Three raw select trees differ only inside removed subtrees. Both retain legacy comment recovery for the selected processing-instruction cases, so their agreement does not prove the newer pinned HTML algorithm. No network requests occur. The title fixture covers document inheritance and empty overrides; eighteen focused Python tree/serializer tests additionally cover removed wrappers, tails, table contexts and exact preview roundtrips.

## Isolated HTML parsing

`html_tree.project_tree()` checks the input byte limit before sending ordinary HTML to a disposable Python worker. The worker uses the same html5lib parser, scripting mode and projection rules; tree/depth limits still apply to its result. Parsing no longer allocates an attacker-controlled tree in the calling process. A trusted explicit parser adapter owns its own parsing boundary: the supplied parse5 adapter executes Node in the worker process, with no nested parser child, then passes its bounded result through the same projection checks.

`ParserLimits` exposes adjustable implementation defaults: five seconds wall time, three seconds CPU, 4 MiB output and a 256 MiB resident-memory termination threshold sampled every 20 ms. These are experiment choices, not Email Next wire limits or user requirements. Worker CPU and output-file limits apply before parser import; wall timeout terminates the process group, including descendants. The parse5 adapter separately defaults to a 128 MiB V8 old-space cap. That cap does not bound every Node allocation.

On the tested macOS host, attempts to set address-space and data-segment limits were rejected. Memory enforcement there is therefore a watchdog: it observes resident memory and terminates the process, with possible sampling and termination overshoot. It is **not a hard preallocation ceiling**. Requiring hard memory enforcement rejects that unsupported Python path; the Node adapter also rejects that stricter requirement rather than describing its heap cap as total memory enforcement. A Linux address-space-limit path exists but has not been validated by this macOS run. Failure to obtain the resident-memory observation also rejects processing.

The caller receives either a complete projection or a resource failure, never a partial tree. Rich receipt retains the authenticated original and readable text and shows a plain-only result after parser failure. Composition holds rather than sending an unreviewed rich representation. Process separation and limits are not a filesystem/network sandbox or a claim of complete HTML-parser conformance. Image decoding retains its separately documented process and resource boundaries.

`test_parser_process.py` checks normal semantic equivalence, deeply nested and wide hostile HTML, actual wall/output/CPU limits, resident-watchdog termination, descendant cleanup, unsupported strict policy and readable rich fallback. The focused run also includes the configured parse5 adapter and actual protected rich-message tests; parser source coverage and resource enforcement remain separate claims.

## Native list markers

`list-markers-browser-test.mjs` mounts the actual isolated host and checks generated native markers, rather than inferring numbering from HTML attributes. Set `EMAIL_NEXT_PLAYWRIGHT_MODULE` and `EMAIL_NEXT_PYTHON` to existing runtimes and run it sequentially. Its JSON report contains marker text, measured box bounds and computed colors for 13 fixtures under four root-text/forced-color combinations.

All 52 cases pass in Chromium153.0.8010.12 at a 320px viewport. They cover ascending/reversed/explicit/nested lists, native bullet levels, signed 32-bit bounds in LTR and RTL, wrapping, block children and empty items. Native marker accessibility text is read in tree order; collapsible spaces are disregarded for ordinal comparison, while punctuation and digits are retained. RTL ordering and square glyph expectations describe this captured engine. Layout checks require marker boxes within the message's inline bounds. The client baseline uses native inside markers to avoid the measured outside-marker clipping; it does not synthesize number text or enable sender counter styles.

The existing 19 host groups also pass. This is bounded Chromium accessibility-tree/layout evidence, not screen-reader, native zoom, all-font, all-width or cross-browser certification. Source scope is recorded in the [lists audit](../audits/css-lists.md).

## Localized labels and attributed legacy quotations

The source-preserving reader also recognizes balanced inert `div` wrappers, text/`br`-only `div` paragraphs, and `blockquote` with quoted `cite`, `type` or `class` attributes. Attribute values are discarded from presentation and never establish identity, load a URL or identify a quote on their own. Only explicit quote structure with one exact earlier-content match can collapse. Edited or ambiguous quotes remain visible; malformed, nested-quote or unsupported markup retains the complete source. All recognized source spans still reconstruct the original decoded HTML exactly.

Twenty focused HTML/plain quote tests cover interleaving and French, German, Japanese and Arabic attribution labels. Labels are inert visible text, not boundary heuristics or claims of provider-specific localization coverage. The demo adds Japanese interleaved answers and an attributed quotation, with original-message access unchanged. Structural examples follow the [HTML blockquote definition](https://html.spec.whatwg.org/multipage/grouping-content.html#the-blockquote-element); plain quote-depth handling remains distinct from [RFC3676 flowed text](https://www.rfc-editor.org/rfc/rfc3676.html#section-4.5). Synthetic fixtures contain no mailbox data. This remains a deliberately limited source scanner, not a universal HTML repair or provider-format parser.

The expanded legacy browser runner passes twelve check groups in Chromium156.0.8078.4 with one worker, including Japanese labels/answers, attributed quotation collapse without a generated link, exact original recovery and no external requests. This is not an independent client or screen-reader result.

## Table and box layout

`table-box-browser-test.mjs` uses the actual isolated host with the existing `EMAIL_NEXT_PLAYWRIGHT_MODULE` and `EMAIL_NEXT_PYTHON` runtimes (Python needs the already-used Pillow dependency). Run it sequentially with other browser runners. Eight groups pass in Chromium153.0.8010.12 at480px viewport/device scale1: margin collapse, padding/border geometry, separating parent edges, table spacing/padding applicability, ignored internal margins, captions/spans, cell alignment and shared-border painting.

The border check samples actual screenshot PNG pixels, not only computed styles: a wider red collapsed edge wins over the adjacent narrow blue border; separate mode retains the blue cell edge. This is local layout/paint evidence, not cross-browser, fractional-scale, screen-reader or full CSS conformance. The [source audit](../audits/css-table-box.md) records the selected rules and remaining boundaries.

## Atomic membership recovery

`RemediationChain.receive` processes existing control carriers as one transaction. Its explicit request includes permitted additions, the expected predecessor, current signed support for new final members and the `delete-all-past-for-remediation` policy. Missing that policy holds recovery. Exact retries return the retained result without replacing proofs.

`test_remediation_chain` and `test_signed_remediation` cover configured contexts 1–4, signed rich admission and final support, pending controls, malformed chains, rollback, concurrent connections and process crashes. Intermediate epochs cannot authorize new effects; past epoch secrets are deleted while accepted readable history remains. The owning [recovery contract](../group-conversations.md#catching-up-through-a-revoked-member) explains the trade-off and boundaries. This is not automatic chain retrieval, writer failover, repair of already-consumed legacy Commit keys, secure erasure or independent interoperability.

## Image box bounds

`image-box-browser-test.mjs` runs one sequential Chromium instance against the actual pixel host. Eight cases cover 240/320 CSS-pixel frames, LTR/RTL and 16/32-pixel root fonts, retaining 2rem side padding and 3px borders. The original content-box rule overflowed by 70 or 134 pixels; the client border-box override preserves spacing while fitting these cases. Chromium 153.0.8010.12 passed all eight. This is bounded geometry evidence, not general accessibility or cross-engine conformance; spacing alone can exceed an arbitrarily small container.

Use the existing `EMAIL_NEXT_PLAYWRIGHT_MODULE` and `EMAIL_NEXT_PYTHON` runtime configuration and run `node image-box-browser-test.mjs`. No sender property is added. See the [selected layout audit](../audits/css-layout-dependencies.md).

## Renderer channel bootstrap and nonce

The trusted child creates its own message channel. Before inserting the frame, the parent listens for an exact ready message from that frame's opaque origin with the current token and one port. It sends content only through the accepted endpoint, closes rejected renderer-handshake ports, and invalidates the view on subsequent navigation or disposal. The default script nonce encodes 16 random bytes; a trusted embedding/test override remains syntax-checked configuration, not an entropy guarantee.

`renderer-nonce.test.mjs` has three focused checks. The existing `browser-render-test.mjs` now passes 21 groups in Chromium153.0.8010.12 with one worker, including forged/malformed, repeated/stale handshake cases and before/after-ready navigation, alongside timeout, disposal and normal rendering. Invalid event injection is test-harness evidence; no compromised-parent defense or independent security assurance is claimed. The [selected DOM/sandbox/CSP/referrer source audit](../audits/renderer-isolation.md) records source scope and unresolved dependencies separately.

## Inline fragments and bidirectional text

`inline-bidi-browser-test.mjs` mounts the actual isolated host with its existing client policy and baseline. Four sequential cases passed in Chromium 153.0.8010.12, using 150px and 260px containers with LTR and RTL parents. The widths and monospace preference are fixture choices. Assertions compare relative geometry against the reviewed rules: narrower wrapping produces more fragments, slice applies start/end edges once rather than fresh edges on every line, and an RTL parent puts the first visual edge on the right. Opposite-direction mixed spans fragment; an isolated Hebrew run retains RTL ordering beside neutral punctuation; decomposed base/accent pairs stay on the same line. Logical text remains unchanged.

From the repository root, use the same existing runtimes as the main browser check:

```sh
EMAIL_NEXT_PYTHON=<absolute Python executable> \
EMAIL_NEXT_PLAYWRIGHT_MODULE=<absolute Playwright module> \
node email-next/evidence/inline-bidi-browser-test.mjs
```

The Python environment needs the [evidence dependencies](requirements-experiments.txt). Playwright must have its matching Chromium installed. Run this sequential check alone while it owns the repository's browser slot. Optional `EMAIL_NEXT_GEOMETRY_REPORT` names a local JSON output file for measured rectangles and browser version; it is not a golden snapshot or authority source.

These checks measure rectangle geometry, not painted mixed-span border continuity or mirrored glyph appearance. They do not establish shaping fidelity, font fallback, the full Unicode bidi conformance corpus, independent engines or assistive-technology behavior. Source coverage is recorded in the [inline audit](../audits/css-inline.md#inline-boxes-can-have-several-fragments) and [direction audit](../audits/html-direction.md#selected-unicode-algorithm-and-data).

## Automatic mailbox recovery

`recovery_retrieval.py` connects a configured local mailbox spool to the atomic membership-recovery path. It scans original MIME, retains source cursors transactionally, extracts untrusted support candidates, verifies the chain and current signed support, then installs only the final accepted state. Sources supply bytes, not membership authority. Exact permitted additions and the past-secret retirement policy remain explicit local inputs.

`test_recovery_retrieval.py` has eleven focused cases covering actual SMTP delivery followed by automatic retrieval, authenticated competing successors, invalid metadata variants, pending-effect suppression, source failure, cursor/budget rollback, process crashes and immutable retries. Run it with the shared MLS workers and parse5 dependency configured as described above:

```sh
python -m unittest test_recovery_retrieval
```

The test module directory must be on `PYTHONPATH`. The configured spool is not an IMAP/JMAP adapter, and the coordinator emits no remote retransmission request. It does not replace the authorized writer. After prior epoch secrets are deleted, later ciphertext may no longer provide verifiable fork evidence; untrusted transport labels cannot block current traffic. See the [recovery contract](../group-conversations.md#catching-up-through-a-revoked-member) for acceptance and secret-retirement rules.

## Certificate status policy

`certificate_status_policy.py` is a **synthetic policy experiment**, not an OCSP validator or an integrated service transport. It models trusted backend observations for the [service status contract](../service-answers.md#select-a-certificate-status-mode), including indeterminate compatible-mode status, strict holds, required staples, per-certificate exceptions, credible time, policy revisions and bounded reuse. Its inputs must never be treated as authenticated evidence merely because JSON or a caller supplied them.

Run `python -W error::ResourceWarning -m unittest test_certificate_status_policy` in this directory with the installed TLS test dependencies. Five test methods exercise time/mode/exception/nonce/reuse cases and six actual TLS1.3 loopback connections. The loopback gate binds fixture observations to the connected peer certificate digest and sends only a fixed noncredential marker after acceptance; rejected cases send zero application bytes. Both ends close TLS and sockets explicitly. The synthetic observations are not OCSP fetched or validated on the wire.

The focused run passed on CPython3.14.0 with cryptography50.0.2. It does not test actual resumption tickets, OCSP signatures/issuers, staple acquisition, public roots, algorithm interoperability or full path-policy enforcement. The separate `certificate_no_revocation.py` tests cover extension syntax/conflicts; neither experiment is wired into `service_tls.py`. No production backend compliance is claimed.


## Own-account public device synchronization

`own_devices.py` coordinates exact enrollment approval, signed public evidence and per-device discovery across independently anchored local stores. Run the focused checks with the configured evidence Python environment and built MLS workers:

```sh
python -W error::ResourceWarning -m unittest test_own_devices
```

Ten tests pass, including actual protected SMTP delivery to two devices, revocation before DATA, transactional crash/retry behavior and publication that excludes unrelated message bodies and attachments. Public synchronization carries no private keys or historical checkpoints. Inventory describes the accepted identity head; it neither proves globally current state nor authorizes sending. See [own-device synchronization](../identity-lifecycle.md#finding-and-synchronizing-your-own-devices).

The reference transport is a configured local spool. Trusted anchor handoff and enrollment approval are local inputs; this does not implement remote pairing, a deployed provider service, key backup or protected history transfer.

## Protected private-copy experiment

The [private-copy contract](../private-copies.md) uses exact envelope2/context5/assertion4/initial4/common-roster1/established4 branches. Its only selected payload tuple is `mime-rich-v0`; old versions remain strict. The local disclosure plan retains exact other-copy bytes privately and is checked before preparation and submission. A generic marker describes intended sharing, not recipient counts or delivery success.

`test_private_copy_lifecycle.py` covers signed four-device/two-principal admission and exact retry, wrong-principal creation, protected SMTP, rejection of a third-principal Add, same-principal device Add and established Welcome over SMTP, explicitly authorized ordinary fallback, and exact opaque attachment bytes. `test_private_copy_fanout.py` creates a visible conversation and two private conversations, with separate signed rosters and question identities. Actual SMTP private answers change only their own question state. `test_private_copy_plan.py` covers immutable byte plans, policy reauthorization and rejected foreign-author/target transplantation. `test_private_copy_tuples.py` rejects old-version upgrades, unsupported payload combinations and complementary-device capability unions. The focused Python checkpoint has 12 passing tests; three additional Node private-context cases pass alongside 14 existing envelope/context cases. The earlier combined roster/rich regression checkpoint passed 39 tests before the final focused additions.

Run the focused tests from the repository root, with the documented Python dependencies and built MLS binaries:

```sh
EMAIL_NEXT_MLS_BIN_DIR=<absolute MLS binary directory> \
<Python executable> -m unittest discover -s email-next/evidence -p 'test_private_copy_*.py'
node --test email-next/evidence/private-copy-context.test.mjs
```

For the synthetic browser demonstration, set `EMAIL_NEXT_PYTHON`, `EMAIL_NEXT_MLS_BIN_DIR` and `EMAIL_NEXT_PLAYWRIGHT_MODULE`, then run `node email-next/evidence/private-copy-browser-test.mjs`. One sequential Chromium 153.0.8010.12 run passed: accepted-context private label and participation notice, a private answer through actual SMTP, unchanged visible answer state, rejected missing session and an exact HTTP retry without resubmission. `private_copy_demo.py` can also serve the fixture on loopback for inspection. It uses synthetic accounts, not a user's mailbox.

This does not establish provider deployment, independent peers, hidden traffic metadata, universal Bcc privacy or a transferable signed forwarding proof. Received outer headers do not choose the private role or reply audience. Raw-history export and an automated foreign-author content-export workflow remain separate from the self-contained local-author copy planner. Per-route outcomes reuse the sender worker; there is no cross-database or all-recipient SMTP atomicity claim.

## Managed protected presentation

The [protected presentation contract](../managed-presentation.md) negotiates subject, author-stated date and principal To/Cc roles inside MLS. `managed_presentation.py` builds display data from an accepted retained contribution and its exact authenticated carrier/context; unprotected transport fields remain separate. `managed-presentation-ui.mjs` uses text nodes for labels and an expandable transport-details view. This is semantic MLS presentation, not RFC9788 wire compatibility.

The focused helper/lifecycle run passes 9 tests, including signed initial5/roster2 admission, actual encrypted SMTP delivery and protected reply, changed outer From/Subject/Reply-To/References, generic outer subject, exact retry, safe uint64 date display, private audience rejection, authorized ordinary-copy subject exposure and Add→established5 Welcome over SMTP. Six Node checks cover the new exact presentation schema and preserved private context rules. The sequential `managed-presentation-browser-test.mjs` passes four browser groups using actual SMTP-accepted data, with text-only labels, keyboard disclosure and provisional display. It requires explicit `EMAIL_NEXT_PLAYWRIGHT_MODULE`, `EMAIL_NEXT_PYTHON` and `EMAIL_NEXT_MLS_BIN_DIR` configuration and performs no external delivery.

These results are local evidence; independent peers, deployed-provider behavior and assistive-technology certification remain untested. Older profiles retain an explicit unauthenticated outer-subject/date notice. Subject confidentiality does not conceal SMTP routing or prevent an authorized ordinary copy from exposing its reviewed subject.

## Joined service-question control

The [joined-service acceptance manifest](acceptance-joined-service.json) packages the six backend scenarios as requirement-linked cases, with independent-service and deployed-carriage cases explicitly untested. Run `python run_acceptance.py --manifest acceptance-joined-service.json` using the documented Python, MLS worker and parse5 configuration. This manifest covers configured authorization; it does not establish public sign-in, browser accessibility or independent interoperability. Its [recorded acceptance report](reports/acceptance-joined-service.json) contains six passed cases and two explicitly untested scenarios, with the input fingerprints retained. Later source changes require a fresh report.

`client_service.py` joins an accepted instance-qualified `service-question` to the existing configured HTTPS service. Its control comes from the accepted event and exact carrier; an independent local registration supplies origin, principal, paths and credential handle. The explicit assertion5/context6 tuple selects this operation. Old signed operation lists and other context versions do not gain support implicitly.

`test_joined_service.py` exercises actual signed admission and SMTP before TLS execution, exact retry across credential renewal, stale registration and unavailable credential holds, lost-response status reconciliation, current signed device-send revocation, wrong registration/source/option, and exact capability intersection. The service stores one effect for repeated identical submissions. `service-question-browser-test.mjs` runs the synthetic loopback client and real TLS fixture, with session-bound activation and no browser-selected endpoint. Use the same `EMAIL_NEXT_PYTHON`, `EMAIL_NEXT_MLS_BIN_DIR` and `EMAIL_NEXT_PLAYWRIGHT_MODULE` setup as the other browser checks.

The [owning contract](../service-answers.md#from-an-accepted-question-to-a-service-action) separates this configured demonstration from public credential acquisition, account/principal mapping and independent-service interoperability. Service receipts are authenticated by their direct HTTPS origin; they are not transferable signed proofs. There is no cross-database or local/remote atomicity claim.

## Endpoint quorum ordering experiment

The `ordering_certificates.py`, `ordering_store.py`, `ordering_scope.py`, `ordering_mls.py` and `ordering_carrier.py` experiments join independently signed ordering evidence to actual MLS membership transitions and an ordinary MIME/SMTP control carrier. They are a configured comparison, not a completed public admission profile or certified consensus implementation. Context7 selects the exact context6 managed-presentation tuple with endpoint quorum ordering; existing contexts and designated-writer gates remain strict. The admitted application path below adds separately versioned signed initial admission; the original comparison fixture remains available.

The proof parser verifies fixed-purpose Ed25519 signatures and recursively verifies the complete prepared/new-view evidence graph. Higher-view proposals require their new-view justification; report-to-prepared edges decrease view. Quorums count unique keys from the accepted predecessor policy. The durable store retains exact votes and their proof dependencies before publication, refuses conflicting votes, and keeps prepared evidence across coordinator changes. Local resource overflow holds the entire object; no partial quorum is accepted. The configured carrier reports `unsupported-size` under its inherited bounds.

The joined fixture independently validates actual MLS Commit processing, exact administrator approval against the predecessor, resulting roster/context, current accepted account authority and witness bindings. It tests an old-policy-certified ordering handoff, an Add and actual Welcome join, immutable decision identity, and atomic checkpoint/decision/outbox installation. Its initial group and per-device application support are explicitly configured and retained; incoming control bytes cannot create that support. Voting holds the identity-store transaction while persisting the separate signing record, and installation rechecks current authority. Its fixed outbox release checks current state and account roles; it is not a database/SMTP atomicity claim or a normal SenderWorker integration. A new joiner's successful Welcome processing is not a complete public invitation or history-proof protocol.

Run `python -W error::ResourceWarning -m unittest test_signed_ordering test_joined_ordering test_display_boundary` with `EMAIL_NEXT_MLS_BIN_DIR` selecting the built workers. Fifteen tests passed on the recorded local run: real signature purpose/substitution failures, nested proof rejection, withheld evidence and local prepared locks, delayed decisions, subprocess termination before/after vote durability and publication, actual MLS handoff/Add, loopback SMTP carriage, subprocess termination before/after installation, and a signed account successor that blocks a now-unauthorized prepared decision. The display test is an accepted-record adapter fixture, not evidence that the ordinary application receiver admits context7.

The original `JoinedOrdering` comparison retains a separate experimental checkpoint/outbox. `AdmittedQuorum` instead shares the normal application checkpoint after signed initial admission, as described below. The carrier's fixed local addresses are fixture routing, not mailbox association authority. Automatic view scheduling, deployed mail synchronization, full restore anti-rollback, authenticated public capability acquisition, application-effect integration and arbitrary fault schedules remain untested. The finite model and these joined cases do not constitute a formal safety/liveness proof. Current-authority veto can freeze a prepared value, and no offline protocol provides instantaneous global send fencing.

### Admitted quorum application path

`admitted_quorum.py` and `quorum_admission.py` connect context7 to ordinary `SenderRelease` and `MlsReceive`. Passive assertion6, initial invitation6 and common roster3 select only envelope3, `mime-rich-v0` and `endpoint-quorum-v0`; service questions remain excluded. Older signed versions keep their existing meanings. The signed initial roster binds the initial witness set to admitted device keys and current identity state/binding references at generation zero. It establishes genesis, not a claimed quorum decision. Identity and mailbox acquisition remain configured in this experiment.

The retained quorum record belongs to the admitted group instance. A fixed quorum adapter verifies the actual predecessor, administrator intent and complete signed decision before atomically updating the shared MLS checkpoint, membership episodes, decision record and control outbox. Ordinary application preparation and release require the retained quorum admission. A locally authored quorum candidate retains a library-serialized StagedCommit bound to its exact candidate, group, full predecessor, library version and serialized-object digest. Installation merges that locally retained object through OpenMLS into the current checkpoint; it does not restore the candidate’s older whole checkpoint. This allows intervening application traffic without rolling back its ratchets. Peer-supplied staged secret objects are never accepted. Incoming decisions are processed against current local MLS state.

`test_admitted_quorum` exercises signed initial admission of four devices over loopback SMTP, an actual protected rich contribution, certified removal of a non-witness member at the retained members, and an ordinary protected reply in the resulting epoch. It also checks actual accepted presentation, rollback before installation, duplicate decision after adapter restart, mismatched proof, missing admission, exact merging after both outbound and inbound application traffic, local staged-version mismatch, actual subprocess crashes before/after installation, retained replay without new receive effects, and rejection of old tuple versions and service questions. These fixtures retain the existing zero-past-epoch setting; they do not establish delayed old-epoch decryptability under other retention settings. These are configured local integration tests, not interoperability with a separately implemented client.

The proof-aware established joiner below extends this path. Removed-device terminal delivery, historical control release and restore/remediation still require quorum integration. The fixed durable adapter below replaces fixture-only submission for the selected current-tip flow. The signed vote-store crash tests remain separate from this shared-checkpoint test. None of these results establishes deployed capability acquisition or consensus liveness.

### Proof-aware quorum joining

Established invitation6 adds a signed `genesis` anchor and contiguous `orderingPath` to the established invitation. `quorum_join.py` accepts the anchor only through explicit independent selection of the original signed roster3, creator, context and member keys. Importing that evidence does not consume an original recipient's package, join the conversation, or make manual anchor setup transparent discovery.

Each path entry carries the exact existing candidate and complete decision proof. Verification starts with the pinned genesis witness policy and follows exact predecessor commitments, stable decisions and certified policy changes. Every edge preserves the selected application and private-copy bounds. The joiner verifies signed transition claims; it does not decrypt historical Commits. Its actual Welcome processing must match the final certified group, epoch, context and member keys. Current account authority and exact assertion6 support remain required. Revocation of required historical witness authority can hold joining.

`quorum_join_support.py` retains independently checked current target support before voting and installs the accepted per-device agreement in the membership transaction. `quorum_invitation.py` creates immutable signed invitation bytes only from retained certified history and the local MLS Welcome author. Established admission atomically consumes the exact local package and installs the shared checkpoint, membership episodes, application agreement and certified quorum tip. Missing or altered proof does not turn a bare Welcome into permission to join.

`test_quorum_join` checks an actual certified Add, loopback invitation delivery, independently accepted anchor, actual Welcome join and ordinary protected contributions in both directions. Negative cases cover wrong anchor, missing/duplicated/substituted path, wrong target, older support, transaction rollback and private-copy expansion. Whole-object limits still apply: an oversized path is held rather than partially accepted. This is a bounded configured experiment. The fixed adapter below supplies durable current-tip control/invitation submission; historical compaction and deployed anchor acquisition remain separate work.

### Durable quorum control and invitation delivery

`quorum_release.py` supplies separate fixed control and invitation entry points in `SenderWorker`. It retains exact MIME and selected mailbox/device evidence, uses the existing exclusive worker lock and per-attempt history, and rechecks current policy, identity, context and routes before release and before DATA. Invitation submission requires successful SMTP handoff records covering every predecessor device other than its author. An unresolved handoff holds the invitation; a lost response requires an explicit exact-byte retry. Accepted recipients are not automatically resent.

Control carrier1 carries exactly the added devices’ signed assertion6 wrappers. The receiver verifies current authority without installing incoming identity state, and compares each advertised package with the actual OpenMLS Add proposal’s KeyPackageRef. Multiple Adds require complete unique coverage. Support, accepted agreements, membership episodes, checkpoint and outbox are committed together. No-Add carriers require an empty assertion array. Whole-object and complete-proof bounds remain unchanged.

`test_quorum_release` exercises controls, uncertain retry, ordered invitation handoff, actual admission and protected contributions in both directions through the durable worker. It also changes policy between release and DATA and checks that no content is sent. `test_quorum_control_v1` exercises two simultaneous Adds at a non-voting member with no retained target support, rejects a fresh different package for the same key, rejects missing/extra/duplicate/older assertions, rolls back a precommit crash, and rejects malformed cached-decision replay. Existing carrier0 comparisons remain separate.

The transport is still configured loopback SMTP. The invitation adapter requires the exact resulting decision to remain current. The separate terminal and historical adapters below extend control delivery; restore assurance remains unimplemented. SMTP acceptance is not remote installation or delivery proof.

### Quorum terminal notification and historical delivery

`quorum_release.py` adds a fixed terminal worker entry point for an exact removed predecessor device. It uses retained authenticated routing without granting that device current receive authority. `quorum_history.py` verifies retained certificate ancestry and recipient continuity; `quorum_historical_release.py` prepares immutable ordered controls for a continuing endpoint or only through a removed endpoint’s terminal edge. These use the existing worker lock, attempt journal and pre-DATA authorization checks. Local complete-path limits hold oversized requests without accepting a prefix.

Four focused tests in `test_quorum_terminal.py` and `test_quorum_history.py` exercise an actual combined Add/Remove, complete predecessor handoff coverage, terminal replay and application denial, removal-only notification, route withdrawal after release, ordered offline catch-up and stopping before later epochs. They reject altered Commit/certificate/predecessor evidence, a mismatched computed terminal context, out-of-order receive, missing ancestry and an insufficient local history budget. The tests use real signatures, MLS processing and loopback SMTP; they do not certify a deployed distributed service.

The [terminal context contract](../group-conversations.md#terminal-notification-and-offline-catch-up) distinguishes computed public fields from certificate-attested final transcript values. OpenMLS 0.9.1 returns self-removal before final transcript/confirmation validation. This path installs only an inactive instance. It does not weaken retained-member validation or reactivate old membership. Normal per-edge checks continue to hold a known-revoked intermediate roster; the separate atomic recovery path below handles that case.

### Atomic quorum recovery evidence

`quorum_recovery.py` consumes existing carrier1 messages without broadening ordinary transition acceptance. It validates certificate ancestry and actual MLS results on disposable checkpoints, checks current final-member authority and signed support, retires past secrets under the explicit existing recovery policy, and commits only the final state. Intermediate epochs receive effect holds. `quorum_recovery_identity.py` permits a newer accepted witness head only along a proven local chain with an unchanged binding/key and current send authority. Ordinary quorum history validation remains strict.

`test_quorum_recovery.py` uses real signed sibling revocation, retained control delivery through the durable worker and loopback SMTP, rollback/retry, a protected reply after recovery, and current support for a newly retained member. It checks wrong ordering, missing support, exact local addition selection, unknown identity ancestry, revoked keys, changed signed binding and conflicted identity. Separate recovery provenance supports subsequent recovery but does not populate the ordinary forwardable history/outbox. The experiment requires explicit local recovery input and retention selection; it does not claim transparent public history acquisition or rollback-resistant storage.

## Private and protected-presentation recovery

`test_delivery_remediation.py` exercises context5 private copies and context6 protected presentation through the existing historical sender, actual local SMTP, mailbox spool and automatic atomic recovery. Each test uses a real signed device revocation, a currently signed final-member assertion and an already decrypted pending answer from the revoked device. Insufficient or expired signed support holds recovery; a simulated final-support installation failure rolls back checkpoint and recovery receipts. Retrying preserves exact selected inputs. The pending answer remains held without re-decryption while previously accepted history and original event bytes remain available.

The recovery structure checks the exact delivery object and private principal pair on both sides of every step, with an unchanged application context. Role or presentation changes are rejected. This is exact context5/6 support under the existing designated-writer and explicit secret-retirement policy; it does not imply quorum/context7 recovery or support for arbitrary future versions.

## Remote own-device pairing experiment

`remote_pairing.py` joins trusted two-way comparison input to normal signed device enrollment. It retains public offer/request/result bytes, distinguishes session lifetime from device grant validity, and commits the enrollment result with the existing OwnDevices approval/head/outbox transaction. `pairing_relay.py` transports those bytes through a fixed local HTTP origin; it is not a deployed account service or ownership authority.

`test_remote_pairing.py` covers an initially unanchored new store, two independent confirmations, key possession, swapped requests, grant bounds, head races, expiry, cancellation, crash rollback, immutable result retrieval after reopening the database, delayed receipt and actual initial-roster/protected-message SMTP delivery. That joined path also checks revocation before DATA. The combined pairing and existing own-device run passes 21 tests with ResourceWarning treated as an error; the final explicit database-reopen and conflicting-anchor rollback cases pass separately.

The optional `pairing_demo.py` serves two trusted local client surfaces with QR displays and a full-comparison alternative. It requires the existing MLS binaries and image environment plus [requirements-pairing.txt](requirements-pairing.txt), which pins qrcode 8.2. `pairing-browser-test.mjs` uses the configured existing Playwright installation and Python environment; five browser groups exercise both QR displays, rejected mismatches, both manual confirmations and the actual protected-delivery path. Camera/image scanning and assistive-technology behavior are not exercised. The demo uses synthetic local accounts and transfers no private keys, mailbox credentials, MLS checkpoints or history. See the [owning pairing contract](../identity-lifecycle.md#pairing-another-device).

## Service-account authorization and linking

`service_authorization.py` implements the selected same-operator opaque code/grant/refresh-family store and device-signed principal link. `service_authorization_client.py` retains encrypted native authorization state, tries available IPv6/IPv4 loopback listeners, validates exact issuer/state/registration before TLS code redemption, and retains exact link proofs before submission. `service_authorization_http.py` joins its TLS token/link endpoints to the existing service effect/status store. The [owning contract](../service-authorization.md) defines the schemas and trust boundary.

`test_service_authorization.py` uses **simulated trusted account authentication and consent**, then an actual loopback callback, S256 code redemption over TLS, actual authorized-device signature/link, accepted protected SMTP question and deliberate service action. There is no seeded effective token-to-principal mapping. Checks cover exact link retry after a lost response/restart, another account, altered signature, callback issuer/state/expiry, changed registration, wrong verifier/redirect/code replay, rotating refresh reuse, unlink and known signed send-role revocation. The separate bearer parser check covers scheme case and missing/malformed credentials.

`test_service_authorization_client.py` additionally checks unordered exact scope sets, token response types, and two independent processes contending for the same callback or refresh claim. Claims commit before network exchange; changing the selected account prevents an old response from replacing the new attempt. Fourteen backend/client checks pass with ResourceWarning treated as an error.

`service_connect_demo.py` provides a reviewable local client and a separate synthetic service consent page. `service-connect-browser-test.mjs` uses `EMAIL_NEXT_PYTHON`, `EMAIL_NEXT_PLAYWRIGHT_MODULE` and `EMAIL_NEXT_MLS_BIN_DIR`; run it with one browser worker. The Chromium 153 check completes separate-context consent → actual loopback/PKCE → explicit signed account link → fresh protected SMTP question → HTTPS effect and exact retry. Attacker-host and wrong-path authorization redirects are rejected before consent. Only the separate synthetic browser context ignores its fixture CA error; native token/link requests validate the configured CA.

The script-free synthetic consent page permits `http:` in its form-action policy because Chromium rejects an IPv6 loopback CSP source. This is a fixture policy, not production consent guidance: the server independently validates the exact registered loopback host/path and selected port before retaining or following a redirect. The page accepts no sender-authored content or scripts. Its pending-consent count and lifetime are adjustable fixture limits.

This does not implement a production login website, system-browser launch integration, platform keychain or all RFC8252 server redirect options. The AES-GCM vault requires an externally protected key; local fixture keys are test setup. The client supports the selected loopback profile and uses issuer-response binding, not an email-derived issuer. HTTP bodies necessarily carry authorization credentials where the protocol requires them; public journals, logs and receipts must not. Receipt authentication is direct HTTPS origin authentication, not a transferable service signature. Existing certificate-status deployment limitations remain.


## Managed archive import and fresh reconnection

[`safe_restore.py`](safe_restore.py) opens a selected local snapshot as imported history in a fresh workspace. Only exact contribution records enter the separate archive. Source keys, identity pins, MLS ratchets, queues and votes never become live state. Imported content has no actions and is labeled as not reverified; attachment resources and rich HTML rendering are not imported.

A surviving authorized device can enroll the newly generated key through the existing independently confirmed pairing flow. When no such authority survives, the alternative creates an explicitly new identity; an established correspondent must accept the continuity break separately. The tests exercise both paths through actual initial invitation and protected-message SMTP delivery. Old ciphertext does not become decryptable merely because its plaintext history was imported.

[`test_safe_restore.py`](test_safe_restore.py) uses a real database snapshot containing MLS and queued-message state together with an actual signed vote, checks that none of that live state is activated, rejects views/virtual tables and oversized input, and verifies import/activation rollback and reopening. The source remains unchanged. The regression in [`test_signed_initial_instances.py`](test_signed_initial_instances.py) checks that retained creator proofs bind by exact digest regardless of the caller's selection order.

Run [`restore_demo.py`](restore_demo.py) with the configured MLS binaries to inspect the synthetic local restore interface. It shows inert history, a reconnect hold, and explicit new-identity confirmation without exposing keys. [`restore-browser-test.mjs`](restore-browser-test.mjs) checks those states in one sequential browser runner. The restore UI does not itself perform the separate two-device confirmation screens; the pairing UI and backend tests cover that ceremony. This experiment is not a cloud backup service, encrypted archive format, private-key recovery mechanism or whole-machine rollback detector. Its managed entry point does not convert low-level test APIs into a universal operating-system security boundary.

## Joined protected message edits

`client_edits.py` prepares an explicitly selected correction in one transaction with its source-token check, retained action identity and staged protected bytes. `receive-edit.mjs` evaluates complete ancestor graphs; `mls_receive.py` admits eligible edits under their original instance and retains the exact accepted author evidence. `journal_edit_view.py` derives heads from immutable records plus current identity evidence, and rechecks that evidence on every trusted view read. The [owning edit contract](../interaction-state.md#message-edits) defines the exact operation and temporal policy.

The view checks selected-conversation row counts and stored byte lengths before loading its snapshot, then looks up only relevant exact-digest provenance and bounds identity evidence before decoding it. Its adjustable experiment defaults are 4,096 records, 16,384 references and 16 MiB of evidence/request bytes; these are not protocol limits or a hard process-memory guarantee. Exhaustion preserves the previous view as stale and suppresses dependent actions.

`test_joined_edits.py` uses signed assertion5/context6 admission and actual SMTP delivery. It covers reordered roots/parents/merges, equal text with distinct identities, exact retry, same-author different-device correction, signed revocation and identity fork, binding replacement, expired discovery/binding, unknown-authority and budget holds, transactional compose rollback, missing device capability, and a real membership-only removal followed by delayed old-epoch target processing after receiver restart. An accepted edit survives group removal; an old pending edit cannot gain effects afterward. The unknown-evidence test injects an unavailable identity lookup, not a forged revocation.

The ordinary-copy test authorizes the exact replacement text and references, sends plain/HTML through the durable SMTP adapter, and checks that undisclosed original wording is absent. It does not transmit a structured event alternative. Changed identity evidence invalidates a view token even without a new contribution; explicit revocation suspends supersession without deleting versions or claiming historical signatures forged.

`edit_demo.py` and `edit-browser-test.mjs` expose a synthetic signed conversation using the existing Python, MLS and Playwright environment variables. The Chromium 153 runner checks deliberate correction, inert markup text, competing heads, explicit resolution and continued access to the original. It does not exercise native assistive technology or independent clients. Only assertion5/context6/envelope3/mime-rich-v0 with explicit `edit` support is enabled; context7 and earlier profiles remain excluded. General forms and rich-content edits are not enabled.

## Local vault writer accounting

`vault_key_owner.py` provides explicit fresh-key provisioning and an independent SQLite reservation ledger for the hosted and native-authorization vaults. Pass `writer_owner` to `HostedSender`, `HostedStore` or `NativeAuthorization` to write; omitting it permits legacy decryption but does not certify an old key as fresh. The owner must use a separate database, checked by resolved path and file identity. `vault_fixture.py` is test-only provisioning, not a production keychain.

Every encryption consumes a durable reservation before the application transaction can commit or roll back. The inherited random-IV ceiling is 2³² invocations per key across all instances; test cases use smaller explicit limits. Exact retained-ciphertext retries consume none. Fresh provisioning generates the key; unknown keys cannot acquire write authority by constructor use. Retired/exhausted keys remain decrypt-only. Explicit migration preserves the original records on rollback while consumed reservations remain consumed.

The owner ledger's continuity is trusted. Restoring only the application database or sharing its key among clones is supported only while all writers use the intact shared owner. Copying/restoring that owner cannot prove global continuity: provision a fresh writer key and retain old keys for decryption. The experiment does not detect malicious offline duplication, supply a platform keychain or certify entropy quality. See [certificate backends and randomness](../audits/certificate-backends.md).

Run `test_vault_key_owner.py`, `test_service_authorization_client.py` and the hosted regression modules for process concurrency, rollback/restart, explicit migration, RNG failure and alias checks. These checks do not infer collision freedom from sampled random values.

## Certificate backend targets

`test_certificate_backend.py` exercises the actual service TLS context with RSA and P-256 ECDSA targets, mixed issuer/leaf keys, and additional Ed25519, Ed448 and P-384 acceptance probes. It checks validly signed expired, wrong-EKU, unknown-critical-extension, DNS-name-constraint, CA and key-usage failures, plus path length, directory-name matching and RSA-PSS salt-parameter verification. `certificate_algorithms.py` checks recognized absent-parameter signature identifiers in the original authenticated-chain DER after the TLS handshake and before HTTP. Re-signed ECDSA/Ed25519 NULL-parameter fixtures show the backend violation and the adapter correction. Missing chain APIs fail closed; returned trust-anchor encoding checks do not validate trust through self-signatures. This is a selected local backend matrix, not an algorithm allowlist or full malformed-DER/name-comparison audit. Generation/load failures remain distinct from client verification failures; see the owning [backend audit](../audits/certificate-backends.md).

## Signed and configured predecision ordering exchange

[`quorum_exchange.py`](quorum_exchange.py) carries complete signed ordering graphs and their exact public candidates in a distinct ordinary-mail wrapper. Exchange1 selects signed assertion7 support bound to the current identity state, binding and signing key. The older exchange0 requires separate explicit configuration. Context7 support alone is insufficient. The fixed sender path checks current authority, route, policy and support again before DATA and preserves immutable bytes across an explicitly authorized uncertain retry.

[`test_quorum_exchange.py`](test_quorum_exchange.py) exercises real local SMTP proposal/prepared/decision carriage, missing and withdrawn support, missing candidate closure, duplicate receipt without MLS effects, durable prepare dependencies across restart, and subsequent final-control installation. Receipt alone does not cast a vote or install membership. The joined vote path retains complete exact candidate bodies in the signing database before a vote can be published. The configured0 case also carries a real signed view change and delayed lower-view certified decision. The separate signed1 path uses authenticated capability evidence, not trusted per-witness wrapper configuration.

[`quorum_retention.py`](quorum_retention.py) logically removes local staged secret objects and obsolete candidate checkpoints after a certified slot installation while preserving the public records needed by control delivery. Public history and vote safety records remain retained; bounded history pruning is not implemented. Cached admitted decisions validate newly supplied proof graphs and return `already-installed`; equivalent valid proof serialization does not become a false branch conflict. No physical erasure or independent implementation interoperability is claimed.

[`test_quorum_signed_exchange.py`](test_quorum_signed_exchange.py) exercises assertion7/initial7/roster4 admission, actual exchange1 SMTP, complete carrier2 witness evidence, immutable support-renewal holds, wrong-purpose/expired support, and established7 durable delivery followed by protected application traffic. Historical path edges retain the complete carrier2 supplemental evidence. These are bounded local tests; no independent client interoperability or public deployment is claimed.

`test_quorum_signed_recovery.py` adds actual carrier2 recovery through a now-revoked intermediate device, with complete historical witness signatures and independently fresh final witness assertions. Missing or altered historical witness evidence, missing current support and injected precommit failure roll back. Only the final epoch is published; late intermediate application traffic stays ineligible, and a protected reply from the recovered endpoint is accepted. Recovery retains exact carrier2 evidence without granting ordinary history-forwarding authority.

## Signed group acceptance report

[`acceptance-quorum-signed.json`](acceptance-quorum-signed.json) packages eight local scenarios for signed ordering-exchange discovery and the corresponding group lifecycle. They cover initial7 admission, exchange1 and carrier2 delivery, durable sender-handshake continuity across repeated candidates and restart, validated-proposal send holds, established7 admission, immutable support dependencies, later witness promotion and atomic recovery through revoked intermediate epochs. Old capability versions keep their own meanings.

After configuring the Python environment, Node runtime and MLS workers described above, run:

```sh
python run_acceptance.py --manifest acceptance-quorum-signed.json
```

The manifest records the exact source inventory and links each scenario to its governing requirement. Independent peer interoperability, deployed provider carriage and independent security review remain explicitly untested. A successful local run cannot establish any of those results. Use `--require-complete` when a gate must reject every remaining untested case.
