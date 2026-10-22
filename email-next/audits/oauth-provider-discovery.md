---
title: Public provider authorization audit
sectionNav: true
---

# Public provider authorization audit

A native mail client needs a provider that can issue and revoke credentials without an application secret. The [provider discovery contract](../provider-discovery.md#register-and-sign-in-through-the-selected-service) selects explicit metadata, public registration and a bound revocation request to make that connection usable across providers. Successful registration identifies a client; it does not verify an application brand, mailbox owner or Email/2 device.

## Consequences for the selected profile

| Source | Selected behavior |
| --- | --- |
| [RFC8414 §2](https://www.rfc-editor.org/rfc/rfc8414.html#section-2) | Token and revocation authentication methods have independent defaults. Require `none` explicitly at both endpoints; never infer one from the other. |
| [RFC8414 §§3–4](https://www.rfc-editor.org/rfc/rfc8414.html#section-3) | Fetch metadata through the independently accepted service origin and require exact issuer equality. Metadata cannot select a replacement origin. |
| [RFC7591 §§2–3](https://www.rfc-editor.org/rfc/rfc7591.html#section-2) | Register the exact native callbacks, code flow, public-client method and selected scopes. Only a fully validated successful response installs a registration. |
| [RFC7009 §§2,5](https://www.rfc-editor.org/rfc/rfc7009.html#section-2) | Identify the original public client and prove a recognized token belongs to it before changing a family. Unknown tokens cannot select another family. |
| [RFC7009 §2.2](https://www.rfc-editor.org/rfc/rfc7009.html#section-2.2) | Unknown or already-invalid tokens receive HTTP200; ignore the response body. HTTP503 and lost responses leave remote revocation uncertain. |

The profile requires a stronger family-wide effect than RFC7009's minimum: the [grant lifecycle](../provider-grants.md#credentials-and-revocation) serializes withdrawal with derived queue access. A local disabled state and an HTTP response alone do not establish that a deployed service implements that boundary. The exact HTTP400 client/token error mappings are profile choices; they are not RFC errata.

Signed metadata, JWT software statements, registration-management credentials, client secrets, introspection and browser-script revocation are not selected. Their presence cannot trigger additional fetches or credentials. Source recommendations for optional application names and URLs do not authenticate a brand and are outside the minimal registration request.

::: {.details summary="Selected source coverage and errata"}

This is a selected-range review, separate from the completed OAuth framework, PKCE, native-app and issuer-response reviews. It adds no claim that the complete bases of RFC8414, RFC7591 or RFC7009 were read.

| Source | Reviewed scope | Scope limit |
| --- | --- | --- |
| RFC8414 | §§2–6 and selected registration semantics in §§7–7.1.1. | Not every initial registry entry, introduction, references or end matter. |
| RFC7591 | Selected §2 metadata/defaults, §2.1 consistency, §2.3 software-statement exclusion, §3 request/success/error, selected §4 registry semantics, §§5–6 security/privacy. | Not the localization or complete JWT example, every initial registry entry, appendices or references. |
| RFC7009 | §§2–5, including optional browser modes and the selected initial registry contents. | Not the complete introduction, references or end matter. |
| RFC6819 | Only §4.4.1.11, reached by RFC7009's denial-of-service guidance. | No new full threat-model review. Finite endpoint work controls do not create universal account quotas. |

The captured all-status listings contain seven records for the three selected OAuth documents. Reported and rejected records are not promoted to published amendments.

| RFC | Record | Status and disposition |
| --- | --- | --- |
| 8414 | [7793](https://www.rfc-editor.org/errata/eid7793) | Reported conditional response-type declaration; this profile always selects an authorization endpoint and code flow. |
| 8414 | [9178](https://www.rfc-editor.org/errata/eid9178) | Reported issuer mismatch in examples; exact normative issuer matching remains required. |
| 8414 | [8696](https://www.rfc-editor.org/errata/eid8696) | Rejected bibliography change; no operational change. |
| 7591 | [7782](https://www.rfc-editor.org/errata/eid7782) | Reported identifier uniqueness change; client identifiers remain bound to their server and registration, never global identity proofs. |
| 7591 | [7969](https://www.rfc-editor.org/errata/eid7969) | Reported missing issuer in a software-statement example; that mode is not selected. |
| 7591 | [8557](https://www.rfc-editor.org/errata/eid8557) | Rejected HTML cross-reference issue; no wire change. |
| 7009 | [6663](https://www.rfc-editor.org/errata/eid6663) | Reported Bearer-authentication proposal; retain the published public-client identification and token-ownership checks. |

RFC6819's directly reached [4267](https://www.rfc-editor.org/errata/eid4267) is Held for Document Update: it corrects the threat premise about guessable codes, not the countermeasure of sufficient entropy. It is not a verified amendment. The selected registry check covers 24 OAuth entries and the existing `oauth-authorization-server` well-known registration; it is not a whole-registry audit or a registration of the draft's mail scopes.

:::

## Evidence boundary

The [provider discovery component](../evidence/README.md#provider-discovery-and-public-client-registration) checks explicit independent endpoint methods and exact module scopes. Its regression rejects otherwise usable metadata when either public-client method declaration is omitted, secret-only, empty, malformed or duplicated. It does not implement a public OAuth server, native sign-in, token-family storage or transactional queue revocation. The [conformance cases](../conformance.md#public-registration-and-revocation-outcomes) require those joined effects before a provider implementation claim.
