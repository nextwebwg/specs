---
title: Service URLs and routing
sectionNav: true
---

# Service URLs and routing

A button's endpoint is an authorization boundary. URI syntax determines how to read that endpoint; it does not authorize a different destination that happens to serve the same resource. The [service-answer contract](../service-answers.md) therefore uses an exact endpoint supplied by the provider.

## Preserve the destination through routing

[RFC 3986 §§2.1–2.4](https://www.rfc-editor.org/rfc/rfc3986.html#section-2.1) distinguishes delimiters from encoded data. Separate components before decoding, and do not decode the same string repeatedly. A proxy that turns `%252F` into a path separator can defeat an exact-path check performed earlier.

The prototype rejects dot segments, encoded separators and alternative spellings of unreserved characters. It retains other escapes on the wire. The fixture server compares the POST path exactly and accepts only a submission identifier after the configured GET prefix. This exercises direct routing; it does not establish equivalent behavior through a deployed reverse proxy.

URI equivalence and permission are separate. The comparison techniques in [RFC 3986 §6.2](https://www.rfc-editor.org/rfc/rfc3986.html#section-6.2) do not grant permission to repair an endpoint, follow a redirect or send credentials to another path.

## Message links have a different contract

RFC 3986 §§3.4–5.4 separates path, query and fragment data and defines how relative references use a base URI. Email Next’s presentation profile instead requires absolute HTTP(S) links and supplies no base URL. The client must not accidentally resolve a rejected relative link against its own webmail or preview address. This does not claim that relative links are invalid in legacy HTML generally.

## Let providers choose their paths

[RFC 8820](https://www.rfc-editor.org/rfc/rfc8820.html) updates RFC 3986 and replaces RFC 7320. Its path rules allow application resources beneath a deployment-controlled prefix, rather than a mandatory global path. Email Next's provider chooses `submit` and `statusPrefix`; example path names carry no discovery meaning.

The experimental DNS-only authority spelling remains a compatibility limitation requiring standards review under RFC 8820 §2.2. It must not become a claim that other valid HTTPS authorities are malformed. Broadening support requires corresponding identity, routing and parser tests.

## Browser-parser review

The [URL Standard](https://url.spec.whatwg.org/) distinguishes a validation error from a parsing failure. Its web-compatible host processing differs from strict IDNA2008; a successfully parsed navigation destination is not proof of mailbox-domain validity. Email Next applies its control-character, credential and backslash restrictions before parsing.

The reproducibility record retains [commit 845bafc](https://url.spec.whatwg.org/commit-snapshots/845bafca22fb0c5a42c4bf384a9bdea525a2f10d/) as historical evidence, not a replacement for the living standard. Reviewed portions cover HTTP(S) parser states, domain/host processing, IPv4/IPv6 parsing, serializers, the URL constructor/getters and the HTTP(S) origin branch. The selected supporting definitions are reviewed below. Ten focused Node24.20.0 navigation tests pass. A separate 31-case comparison now agrees between Node24.20.0 and Chromium153.0.8010.12 after the narrow compatibility guard described below; neither result certifies the entire URL implementation.

## Conversions used by navigation

The URL constructor accepts a Web IDL scalar-value string. Its conversion replaces unpaired surrogates with U+FFFD while preserving valid surrogate pairs. Email Next rejects unpaired surrogates before that conversion and accepts only primitive strings, so parsing cannot silently repair them or invoke an object's string conversion. This rule concerns navigation input, not message-text normalization. [Web IDL USVString](https://webidl.spec.whatwg.org/#js-USVString), [Infra strings](https://infra.spec.whatwg.org/#strings)

The selected constructor uses UTF-8 for non-ASCII path, query and fragment data. Host processing percent-decodes bytes and uses the specified UTF-8 decoding operation before domain validation. Replacement decoding and fatal decoding are different algorithms; “without BOM” does not mean stripping a BOM from this embedded input. A URL decoder must not substitute the strict message-envelope decoder or a legacy character encoding. [Encoding UTF-8 algorithms](https://encoding.spec.whatwg.org/#utf-8-decode-without-bom)

Browser domain processing uses UTS46 mapping, NFC and nontransitional conversion with the flags selected by the URL Standard. Its non-strict ASCII compatibility branch can preserve an ASCII host despite a failed strict diagnostic. These rules differ from the strict IDNA2008 validation used for authenticated mailbox domains. The reviewed UTS46 revision35 is for Unicode17; its normative mapping table is captured separately. Runtime-version records and focused examples do not prove that every embedded runtime table matches that data. [UTS46 §§4–5](https://www.unicode.org/reports/tr46/tr46-35.html#Processing)

For admitted HTTP(S) destinations, the displayed origin is the serialization of a tuple: scheme, serialized host and a port only when non-null. The URL parser removes a default port before this step. Paths, queries, fragments and credentials are not origin components. Origin display therefore uses the parsed tuple, not a substring copied from the input. [HTML origin serialization](https://html.spec.whatwg.org/multipage/browsers.html#ascii-serialisation-of-an-origin)

The browser comparison found a real difference: Chromium accepted an IPv4 component with a leading zero inside an IPv6 literal, while Node rejected it. The pinned URL algorithm requires rejection. A narrow check now rejects that form before native normalization can erase it. All 31 comparison cases then agree, without fetching any destination. Other runtime differences remain possible; this evidence does not replace broader conformance testing.

## Errata dispositions

The captured RFC 3986 listing contains 18 records. Status matters: a proposed correction is not automatically a rule.

| Status and records | Consequence for this profile |
| --- | --- |
| Verified 2525 | Corrects a new-scheme guidance reference; no new URI scheme is selected. |
| Verified 7590 | Removes an accidental hyperlink; no algorithm change. |
| Reported 9147 | Proposed backslash addition is not adopted. |
| Held 2033, 2624, 2933 | Empty-path and pseudocode/regex notation; no new endpoint behavior. |
| Held 4547, 4789, 5428 | Relative-resolution proposals; service endpoints are absolute. |
| Held 4942 | Proposed registered-name restriction is not treated as general URI grammar. |
| Rejected 1783, 2717, 3330, 4293, 4393, 4394, 7019, 8442 | No proposed changes adopted. Component extraction is not validation, and ABNF alternatives are not ordered parser instructions. |

## Coverage and remaining work

The complete 3,419-line RFC 3986 source was read, including appendices, examples, references and end matter, along with all 18 listed errata. The complete 407-line RFC 8820 source was also read; its live errata search returned no matching entries on 20 October 2026. Both sources are registered in the audit inventory; these source reviews do not establish implementation conformance.

The selected navigation source dependencies are reviewed; exhaustive runtime conformance and end-to-end proxy behavior remain separate work. Six existing service-question checks pass, including exact endpoint grammar; they are not a complete URI parser suite.

Source SHA-256:

- RFC 3986: `3102dae4b68cebe40337730312fcb612297b8928547267e8b3d1ee6002b2d683`.
- RFC 8820: `d4872896c3beae79143cc5f3c085c6992e6c6f9427a94f6295dce2bc4746a12c`.
