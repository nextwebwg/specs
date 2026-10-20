---
title: Bearer token usage audit
sectionNav: true
---

# Bearer token usage audit

RFC6750 supplies the existing Authorization header and challenge/error contract for the proposed HTTPS button service. It does not define Email Next principal association, grant acquisition, idempotency or portable signed service receipts. Full OAuth conformance is not established by using its header.

## Service-answer consequences

Use `Authorization: Bearer <token>` with the token kept opaque. Its grammar admits letters, digits, `-._~+/` followed by zero or more trailing `=` characters; require at least one non-padding character. Separate the scheme and token with one or more ASCII spaces. Generate a single space. Do not apply the discovery JSON's canonical-base64 rules to bearer tokens, decode/re-encode them, or put them in the answer JSON/query. Preserve scheme parsing under the HTTP authentication framework rather than assuming all parameters share case rules.

Missing or unusable credentials require a Bearer WWW-Authenticate challenge. Distinguish missing credentials (normally no error detail), malformed authorization (invalid_request, normally400), an invalid/expired/revoked token (invalid_token, normally401), and insufficient scope (normally403). Include challenge parameters correctly: scope is a case-sensitive space-separated set; order has no authority. Realm and defined scope/error attributes occur at most once. Error descriptions and error_uri are developer diagnostics, not instructions to fetch a new authorization endpoint or grant broader access. Authorization renewal retains the exact service submission identity and answer.

The resource server must restrict audience, scope and lifetime using authenticated token content or authoritative opaque-token state; RFC6750 does not require JWT or define an introspection protocol. Client certificate/server identity verification and confidentiality extend to backend hops after TLS termination. An expiry claim supplied by the attacker or response arrival time cannot extend access. Access-token lifetime is separate from the action retry deadline and deduplication retention. Bearer theft allows use without the original client's device key; no device-authentication assurance should be inferred.

The base source's one-hour-or-less lifetime is a SHOULD recommendation, especially for browser-like exposure, not a universal one-hour MUST. Its discussion of TLS1.0 deployment is historical: metadata lists RFC8996 and RFC9700 updates that must be reviewed before adopting a current TLS/OAuth profile. The Email Next choices of no cookies, no redirects and no query/body token transport are explicit narrower application rules. The source's token-response example belongs to OAuth issuance and cannot be parsed as the draft's number-free answer JSON.

## Evidence

Full eighteen-page base text, all grammar/examples, flow figure, references and end matter read. Official metadata lists Proposed Standard and updates RFC8996/RFC9700. The complete live errata page confirms four Reported records; none is a verified correction. The updates and transitive dependencies remain outside this base-text review.

| Section | Disposition |
| --- | --- |
| front | Abstract, status, copyright and contents read; bearer possession is sufficient to exercise associated access. |
| 1 | TLS-protected resource requests; not a complete authorization grant protocol. Historical TLS recommendations require listed updates. |
| 1.1 | ABNF, case-sensitive parameters by default and imported HTTP authentication grammar reviewed. |
| 1.2 | Bearer is not proof-of-possession; no device-key continuity follows from token possession. |
| 1.3 | Complete flow figure and A–F description read; this RFC defines resource access E/F and some token semantics, not all issuance steps. |
| 2 | Never transmit a token by multiple methods in one request. |
| 2.1 | Authorization Bearer scheme with one or more SP and b64token grammar; server must support header method. Token spelling is opaque, not a mandate to base64-decode. |
| 2.2 | Form-body method requires single-part ASCII form encoding and appropriate method; GET prohibited. Not selected for JSON answer POST. |
| 2.3 | Query token method and examples reviewed; discouraged due disclosure. Email Next excludes it and applies stricter no-store responses. |
| 3 | Missing/inadequate credentials require WWW-Authenticate; Bearer challenge with auth parameters. Single occurrences, character sets and realm/scope/error roles reviewed; scope/error text not user-facing instructions. |
| 3.1 | invalid_request normally400, invalid_token401, insufficient_scope403; absent credentials normally omit error detail. Retry after renewal does not authorize new action identity. |
| 4 | Complete issuance example read; numeric expires_in belongs to OAuth issuance schema, not the restricted Email Next JSON schema. |
| 5 | Security scope and reliance on OAuth security guidance reviewed. |
| 5.1 | Manufacture/modification, disclosure, redirect and replay threats reviewed. Token audience confusion is distinct from HTTP redirect following. |
| 5.2 | Integrity or unguessable opaque references, audience/scope, protected token transport including TLS termination backends, certificate validation, bounded lifetime reviewed. Token encoding/introspection mechanics unspecified. |
| 5.3 | Safeguarding, server identity/TLS, cookie exposure/CSRF, short lifetimes, scope/audience and URL leakage recommendations reviewed. |
| 6 | All registry material read. |
| 6.1 | Existing access token type registration, no new Email Next registration supplied. |
| 6.1.1 | Bearer registration fields read; IETF change control preserved. |
| 6.2 | Error registry introduction reviewed. |
| 6.2.1 | invalid_request resource access error registration reviewed. |
| 6.2.2 | invalid_token resource access error registration reviewed. |
| 6.2.3 | insufficient_scope resource access error registration reviewed. |
| 7 | Full reference lists read without recursive review claims. |
| 7.1 | Fourteen normative entries read; applicable closure recorded separately. |
| 7.2 | Four informative entries read, including historical HTTP auth draft. |
| A | Complete acknowledgements read. |
| authors | Both author records and final page/end matter read. |

## Errata

- 5335 proposes renaming b64token to token68. Reported only; the actual grammar already prevents treating the token as compulsory canonical base64.
- 6161 proposes removing charset from the §4 JSON example. Reported only. The service-answer profile already emits application/json without parameters.
- 9053 and9054 repeat that media-type issue but identify §5.1 rather than the actual §4 example. Reported only; their claims about strict OAuth client behavior are reporter claims, not demonstrated interoperability evidence or adopted requirements.

## Dependency boundary

RFC6749 remains essential for authorization roles, token issuance and error/scope grammar. Historical HTTP/auth imports need reconciliation with the existing RFC9110 audit; RFC2818/TLS/certificate validation dependencies require current successor review alongside RFC8996. RFC9700 is an explicit security update and must be reviewed before claiming a modern authorization profile. URI/ABNF/requirements references remain applicable; form-body encoding, cookie authorization and query-token mechanisms are not selected, without pretending their source sections were skipped.

Sources: https://www.rfc-editor.org/rfc/rfc6750.html ; https://www.rfc-editor.org/rfc/rfc6750.json ; https://www.rfc-editor.org/errata/rfc6750 . The section ledger records this base-text review; the listed updates remain pending.
