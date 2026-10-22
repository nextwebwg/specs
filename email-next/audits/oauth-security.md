---
title: OAuth security update audit
sectionNav: true
---

# OAuth security update audit

RFC9700 strengthens the configured HTTPS button service's bearer-token boundary. Query-string access tokens are now prohibited. Every resource request needs audience and resource/action authorization; client-side destination restrictions do not replace those checks. Sender-constrained tokens are recommended, so a plain-bearer experiment must identify that limitation instead of claiming complete current OAuth security conformance.

## Consequences for the service profile

The configured bearer experiment can remain an explicit limited implementation choice, but server-side scope/audience checks, secret storage and proxy protection remain necessary. Service submission idempotency prevents repeating one business operation; it does not prevent an attacker using a stolen bearer token to create another authorized-looking submission. An Email/2 device signature does not automatically turn an OAuth token into a sender-constrained token. Select and audit mTLS/RFC8705 or DPoP/RFC9449 if that property is claimed.

For every request, reject a token intended for another service, resource or action. Map token subjects to enp0 only through an authoritative association that distinguishes a client identity from a human resource owner; a client-controlled client_id or sub string cannot impersonate an account. Do not log/store/forward plaintext access tokens. At a TLS-terminating proxy, sanitize attacker-supplied security headers and protect the backend connection against eavesdropping, injection and replay.

The [native authorization profile](../service-authorization.md) defines credential acquisition separately from service-answer submission. It selects authorization code with S256 PKCE, a loopback callback, issuer binding and rotating refresh tokens. Resource-owner-password grant is prohibited. Public authorization-code clients must use PKCE; authorization servers must support it and enforce downgrade-resistant challenge/verifier rules. Multiple issuers require mix-up defense; exact redirect matching, CSRF binding and protection against response leakage also apply. Refresh tokens for public clients require rotation or sender constraint. Native loopback exceptions, browser origin checks and CORS rules do not grant general permission to redirect button submissions or send ambient credentials to an email-proposed service.

For browser-based acquisition, exact postMessage sender/receiver origins are required, wildcard receivers forbidden, and ordinary flow protections still apply. Authorization endpoints must not support CORS; other directly accessed endpoints may do so. Protect authorization UI against clickjacking and avoid credential leakage through history, third-party content or Referer. The selected native profile uses an external browser context and a loopback callback, not postMessage authorization delivery. Its simulated account-consent fixture is distinct from production sign-in or operating-system browser integration.

## Evidence and dispositions

Complete46-page base text, all2569 lines, examples/pseudocode, references and end matter reviewed. Official metadata lists BCP240 updating6749/6750/6819 and no successor/update. Both captured corpus and live official errata search show no matching errata. Dependency and implementation closure remain open.

| Section | Disposition |
| --- | --- |
| front | Full abstract, status, copyright and contents read. |
| 1 | Dynamic endpoint trust, evolving browser behavior and broader threats motivate update; complements rather than replaces OAuth base guidance. |
| 1.1 | Document structure reviewed. |
| 1.2 | Terminology, BCP14 and open-redirector definition reviewed. |
| 2 | Core best practices plus detailed section4 requirements reviewed. |
| 2.1 | Exact redirect matching, CSRF, issuer mix-up defense and credential-safe redirect requirements apply to the selected native acquisition flow. |
| 2.1.1 | Public clients require PKCE; confidential clients recommended; transaction-specific binding, S256 preference, verifier enforcement and detectable support required. |
| 2.1.2 | Implicit/token-in-authorization-response discouraged; not selected for Email/2 acquisition. |
| 2.2 | Token replay prevention is separate from business submission deduplication. |
| 2.2.1 | Sender-constrained access tokens SHOULD be used; plain configured bearer baseline needs explicit bounded exception/rationale, not full BCP compliance claim. |
| 2.2.2 | Public-client refresh tokens MUST be sender-constrained or rotated; confidential-client binding remains. |
| 2.3 | Least privilege, audience and action/resource checks at every resource request; wrong intended audience must be refused. |
| 2.4 | Resource-owner-password grant MUST NOT be used; mailbox-password token acquisition excluded. |
| 2.5 | Client authentication where feasible, asymmetric methods recommended; not an implicit device-enrollment mechanism. |
| 2.6 | Trusted metadata, TLS, HTTPS response redirects, strict postMessage origins and endpoint-specific CORS reviewed. Authorization endpoint must not support CORS. |
| 3 | All A1–A5 attackers and collaboration reviewed; configured resource service may still be compromised or counterfeit. |
| 4 | Detailed attacks supplement existing threat model; no automatic selection of every flow. |
| 4.1 | Pattern matching redirect URIs creates disclosure risks. |
| 4.1.1 | Complete code-grant attack and wildcard/subdomain takeover examples read; TLS domain family is insufficient ownership evidence. |
| 4.1.2 | Complete implicit/fragment-inheritance attack requests and responses read; redirects can preserve bearer fragments. |
| 4.1.3 | Exact matching/native localhost port exception and authenticated-request exception reviewed; no arbitrary endpoint promotion. |
| 4.2 | Referer leakage reviewed, including historical browser bug; no assumption that fragment placement solves all leakage. |
| 4.2.1 | Client page third-party resources/links can leak response data. |
| 4.2.2 | Authorization-server page can leak request/state data. |
| 4.2.3 | Leaked state can defeat CSRF correlation; code/token leakage has distinct effects. |
| 4.2.4 | No third-party resources, referrer policy, code/PKCE, one-use code/state and form-post option reviewed; not a selected new flow. |
| 4.3 | Browser-history leakage reviewed. |
| 4.3.1 | Authorization-code URL history mitigations require code binding/replay controls. |
| 4.3.2 | Client URI-query access tokens MUST NOT be used; strengthens older RFC6750 discouragement. |
| 4.4 | Multiple authorization servers introduce mix-up exposure. |
| 4.4.1 | All six attack steps and four variants read; honest authorization URL alone cannot identify token endpoint authority. |
| 4.4.2 | Bind selected issuer/endpoint tuple to each request and user agent; multiple issuers require defense. |
| 4.4.2.1 | Returned issuer must match retained issuer under RFC9207 rules, otherwise abort. |
| 4.4.2.2 | Distinct redirect URI defense and limitations reviewed; weaker fallback only when other options unavailable. |
| 4.5 | Code injection may bind attacker's session to victim resources even with confidential client auth. |
| 4.5.1 | All six injection steps read. |
| 4.5.2 | Exact redirect/code relationship checks and implementation pitfalls read; asymmetric client auth alone insufficient. |
| 4.5.3 | Code-instance binding options reviewed. |
| 4.5.3.1 | PKCE counters injection and public-client stolen-code redemption. |
| 4.5.3.2 | OIDC nonce validation from token endpoint must precede any token use; does not replace PKCE for public clients. |
| 4.5.3.3 | Other proposed mechanisms lack baseline support; no new cryptographic solution selected. |
| 4.5.4 | Request tampering limits defenses; leakage protection still needed. |
| 4.6 | Complete token injection scenario reviewed. |
| 4.6.1 | Pure implicit OAuth lacks injection binding; OIDC at_hash/nonce and sender constraint limits reviewed. |
| 4.7 | Redirect CSRF scope distinguished from service-side action authorization. |
| 4.7.1 | PKCE support must be established before relying on it for CSRF; application state integrity still matters. |
| 4.8 | Optional PKCE can allow downgrade when challenge/verifier relationships ignored. |
| 4.8.1 | All six downgrade steps read. |
| 4.8.2 | Reject verifier with no original challenge; enforce challenge/verifier linkage. |
| 4.9 | Resource-side token leakage is relevant even with correctly delivered HTTPS requests. |
| 4.9.1 | Late-bound service URL phishing is directly relevant to email-proposed action endpoints. |
| 4.9.2 | Compromised resource/log storage can expose tokens beyond the service. |
| 4.9.3 | Sender/audience constraints recommended; resource server must not store/transfer access tokens in plaintext. |
| 4.10 | Sender constraint and audience restriction recommended together; architecture/performance may limit deployments. |
| 4.10.1 | Three-step model, mTLS and DPoP descriptions read. They need their own binding; compromised token plus key defeats protection. |
| 4.10.2 | Audience restriction must be enforced by resource server; actual destination binding helps phishing defense. Resources/privacy tradeoffs reviewed. |
| 4.10.3 | Both nonstandard metadata examples and rejection rationale read; client destination allowlist alone cannot substitute for server enforcement. |
| 4.11 | Open redirects threaten credentials and trust cues. |
| 4.11.1 | Clients must not expose open redirectors. |
| 4.11.2 | All three AS phishing scenarios and risk-based redirect safeguards read. |
| 4.12 | Credential-bearing authorization POST must not use307;303 recommended. Service-answer no-redirect policy remains stricter and separate. |
| 4.13 | Sanitize inbound security headers and protect/authenticate proxy-backend link against disclosure, injection and replay. |
| 4.14 | Refresh enables short access-token lifetimes but introduces long-lived authority. |
| 4.14.1 | Existing refresh secrecy, client binding, unguessability and lifecycle requirements reviewed. |
| 4.14.2 | Risk-assess issuance; bind consented scope/resources; public clients require rotation or sender constraint; inactivity expiry recommended. |
| 4.15 | Client identity may impersonate resource-owner identity in shared subject namespace; directly affects enp0 mapping. |
| 4.15.1 | Prevent client-controlled identity collision or provide reliable token-kind distinction. |
| 4.16 | Clickjacking defenses and complete CSP/X-Frame example read; example is nonnormative, no current browser support claim. |
| 4.17 | In-browser authorization delivery needs origin validation plus ordinary flow protections. |
| 4.17.1 | All nonnormative browser pseudocode examples reviewed. |
| 4.17.1.1 | Wildcard postMessage target leaks responses. |
| 4.17.1.2 | Attacker-chosen receiver origin leaks responses. |
| 4.17.1.3 | Unchecked sender origin permits injected responses. |
| 4.17.2 | Exact receiver and sender origins; no wildcard target; section2.1 protections remain mandatory. |
| 5 | No IANA actions. |
| 6 | Security treatment located in2–4. |
| 7 | Complete references reviewed, not recursively audited. |
| 7.1 | All normative entries read including BCP195 components; grant/profile-specific dependencies remain. |
| 7.2 | All informative entries read, including PKCE/DPoP/issuer/resource references used by normative prose. |
| Acknowledgements | Complete acknowledgements read. |
| Authors | All four author records and end matter read. |

## Dependency boundary

RFC6749 and RFC6819 remain framework/threat-model dependencies; this document complements them. RFC9325 supplies current TLS configuration beyond the separately audited8996 deprecation. The selected PKCE, native-app and issuer-response requirements are described below. The retained static-registration experiment does not imply metadata discovery. The selected public-provider path has a separate [metadata, registration and revocation review](oauth-provider-discovery.md). Sender-constrained8705/9449 need a complete application binding. Resource8707, authorization-details9396 and JWT-profile9068 are options, not automatically selected mechanisms. References categorized informative can still be needed by normative requirements; their bibliography category does not complete a protocol binding.

Source examples explicitly labeled nonstandard (resource_servers and access_token_resource_server) must not become invented discovery fields. Complete attack examples were read as illustrative material, not executed interoperability fixtures. Source review and execution evidence are separate. The [native authorization profile](../service-authorization.md) describes the implemented local flow and its limits; its tests do not establish complete OAuth conformance or deployed interoperability.

Sources: https://www.rfc-editor.org/rfc/rfc9700.html ; https://www.rfc-editor.org/rfc/rfc9700.json ; https://www.rfc-editor.org/errata/rfc9700 .


## PKCE dependency for client sign-in

PKCE binds one authorization request to its token exchange. Generate a fresh high-entropy verifier for each request, send its S256 challenge to the authorization endpoint, and disclose the verifier only to the token endpoint. Select S256 explicitly; an error does not permit downgrading to plain. The server retains the challenge and method with the code and checks the verifier before issuing tokens. PKCE does not establish an Email/2 principal, service ownership or action permission. [RFC 7636 §§4 and 7](https://www.rfc-editor.org/rfc/rfc7636.html#section-4)

Verified erratum 5687 corrects the compatibility text: the authorization request carries the challenge, not the verifier. Reports 6179 and 6471 remain unverified; rejected reports 8457 and 8458 do not change the ABNF names. The complete base text and appendix encoding vectors were reviewed; this source review does not prove an implemented authorization flow or deployed interoperability. [RFC 7636 errata](https://www.rfc-editor.org/errata/rfc7636)

## Native-app sign-in and issuer binding

A native mail client opens authorization in an external browser security context. The client must not inspect the login page, its cookies or the account password. A platform browser tab can provide this separation without forcing the person to leave the app; an ordinary embedded web view cannot. Public native clients use authorization code with PKCE. A client identifier or shared secret bundled in the application does not authenticate the installation. [RFC 8252 §§3–6 and 8](https://www.rfc-editor.org/rfc/rfc8252.html#section-3)

For a loopback callback, bind only a loopback interface and retain the exact selected URI with the pending authorization request. Register the complete address and path; the ephemeral port is the matching exception. Use an IP literal, allow the available IP version, and close the listener after the response. An incoming callback still needs the pending transaction's state, issuer and redirect checks before code redemption. Loopback HTTP is a specific native callback exception, not permission to send service credentials over ordinary HTTP. [RFC 8252 §§7.3–8.4](https://www.rfc-editor.org/rfc/rfc8252.html#section-7.3)

The issuer response parameter identifies the authorization server, not the person or Email/2 principal. Decode `iss` from form encoding and compare it as an exact string with the issuer retained for that attempt. Apply the check to success and error responses. When support is required, a missing or different issuer stops the flow; the callback cannot nominate another token endpoint. Issuer identifiers use HTTPS without a query or fragment, and distinct authorization servers must not share one identifier. Static trusted issuer configuration is permitted; automatic metadata discovery is a separate choice. [RFC 9207 §§2–4](https://www.rfc-editor.org/rfc/rfc9207.html#section-2)

::: {.details summary="Why the experiment selects one callback and token model"}

The desktop experiment selects a loopback callback, an independently configured issuer and opaque tokens validated by the service's own authorization store. This gives the reference implementation a concrete sign-in path without requiring platform app-link registration, dynamic discovery or a new JWT validation profile. Those are scope choices, not limitations imposed by OAuth.

The choice also limits the claim: it does not demonstrate mobile callback integration, a general authorization server or federation between independent token issuers and resource servers. Supporting those deployments requires their corresponding contracts and tests. The selected issuer check prevents a callback from redirecting code redemption to a different configured authority; it does not authenticate the Email/2 principal or replace the service's account-link proof.

:::

### Review coverage

The native-app review covers the complete base text, including callback registration, browser isolation and the historical platform appendix. A loopback-only server experiment does not implement the full server support checklist, which also requires private-use and claimed HTTPS redirects. RFC 8252's reported erratum 8080 does not relax the private-use scheme requirement; rejected erratum 5848 does not establish current platform API support. The complete RFC 9207 base text was reviewed, with no errata returned by the official search on 20 October 2026. These source checks do not prove operating-system integration or independent interoperability. [RFC 8252 errata](https://www.rfc-editor.org/errata/rfc8252), [RFC 9207 errata](https://www.rfc-editor.org/errata/rfc9207)

The selected wire names reuse the registered authorization-code, Bearer, S256 PKCE and issuer-response entries. The registry check covers those 22 entries, including their usage locations and owning specifications; it does not register the draft's service scopes or select automatic metadata discovery. [IANA OAuth Parameters](https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml)

## Grant selection

The native profile uses authorization code with PKCE and rotating refresh tokens. The other RFC6749 grant descriptions do not add fallback sign-in methods:

| Source sections | Disposition |
| --- | --- |
| 4.2–4.2.2.1: implicit grant | Excluded. Access tokens are not returned through the browser redirect. |
| 4.3–4.3.3: password grant | Excluded. RFC9700 prohibits this grant; the older conditional permission does not apply. |
| 4.4–4.4.3: client credentials | Excluded from native user sign-in. A client's authority does not establish a person's account link. |
| 4.5: extension grants | No extension grant selected. Its absolute-URI mechanism does not authorize accepting arbitrary grant types. |

These sections, their flow diagrams and complete examples were reviewed. The reference authorization store accepts only authorization-code redemption and refresh; other grant types receive `unsupported_grant_type`. This is a selected-profile boundary, not a claim that the service implements every OAuth grant. [RFC6749 §4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4)

### OAuth framework coverage

The [OAuth framework audit](oauth-framework.md) maps every RFC6749 section and appendix, including diagrams, examples, grammar, registry templates and all 31 captured errata, to the selected profile. These completed reviews are included in the current source inventory and section ledger; complete transitive dependency closure remains open.

Its historical TLS and embedded-browser allowances are superseded by the reviewed security and native-app updates. Its registration procedures do not register Email/2 fields or scopes. The live registry review remains limited to the 22 selected entries described above. Source review does not establish implementation conformance or independent interoperability.


::: {.details summary="Supplemental OAuth section dispositions"}

### RFC7636

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Authorization-code interception threat and full request/code/verifier/token flow reviewed; PKCE does not authenticate the Email/2 principal. |
| 1.1 — Protocol Flow | Authorization-code interception threat and full request/code/verifier/token flow reviewed; PKCE does not authenticate the Email/2 principal. |
| 2 — Notational Conventions | Requirements, notation and terminology reviewed; verifier and challenge are distinct values. |
| 3 — Terminology | Requirements, notation and terminology reviewed; verifier and challenge are distinct values. |
| 3.1 — Abbreviations | Requirements, notation and terminology reviewed; verifier and challenge are distinct values. |
| 4 — Protocol | Fresh high-entropy verifier per request, exact unreserved syntax and43–128character bounds; local implementation selects secure generation. |
| 4.1 — Client Creates a Code Verifier | Fresh high-entropy verifier per request, exact unreserved syntax and43–128character bounds; local implementation selects secure generation. |
| 4.2 — Client Creates the Code Challenge | Select S256 explicitly: SHA-256 of ASCII verifier then unpadded base64url; send challenge and method, not verifier, to authorization endpoint. |
| 4.3 — Client Sends the Code Challenge with the Authorization Request | Select S256 explicitly: SHA-256 of ASCII verifier then unpadded base64url; send challenge and method, not verifier, to authorization endpoint. |
| 4.4 — Server Returns the Code | Retain challenge/method with code; unsupported method or required-but-missing challenge produces error, not automatic downgrade. |
| 4.4.1 — Error Response | Retain challenge/method with code; unsupported method or required-but-missing challenge produces error, not automatic downgrade. |
| 4.5 — Client Sends the Authorization Code and the Code Verifier to the Token Endpoint | Token exchange presents verifier; server recomputes retained method and compares before token issuance, rejecting mismatch. |
| 4.6 — Server Verifies code_verifier before Returning the Tokens | Token exchange presents verifier; server recomputes retained method and compares before token issuance, rejecting mismatch. |
| 5 — Compatibility | Verified5687 corrects compatibility to missing challenge; selected native profile requires PKCE and does not use compatibility to bypass it. |
| 6 — IANA Considerations | Parameter locations, challenge-method registry, registration template and initial entries reviewed; selected registry entries checked separately. |
| 6.1 — OAuth Parameters Registry | Parameter locations, challenge-method registry, registration template and initial entries reviewed; selected registry entries checked separately. |
| 6.2 — PKCE Code Challenge Method Registry | Parameter locations, challenge-method registry, registration template and initial entries reviewed; selected registry entries checked separately. |
| 6.2.1 — Registration Template | Parameter locations, challenge-method registry, registration template and initial entries reviewed; selected registry entries checked separately. |
| 6.2.2 — Initial Registry Contents | Parameter locations, challenge-method registry, registration template and initial entries reviewed; selected registry entries checked separately. |
| 7 — Security Considerations | Verifier entropy, eavesdropper resistance and salt discussion reviewed. No S256-to-plain downgrade; reported errata do not silently amend the profile. |
| 7.1 — Entropy of the code_verifier | Verifier entropy, eavesdropper resistance and salt discussion reviewed. No S256-to-plain downgrade; reported errata do not silently amend the profile. |
| 7.2 — Protection against Eavesdroppers | Verifier entropy, eavesdropper resistance and salt discussion reviewed. No S256-to-plain downgrade; reported errata do not silently amend the profile. |
| 7.3 — Salting the code_challenge | Verifier entropy, eavesdropper resistance and salt discussion reviewed. No S256-to-plain downgrade; reported errata do not silently amend the profile. |
| 7.4 — OAuth Security Considerations | OAuth threats and TLS remain additional obligations; PKCE is not transport security or callback issuer binding. |
| 7.5 — TLS Security Considerations | OAuth threats and TLS remain additional obligations; PKCE is not transport security or callback issuer binding. |
| 8 — References | Complete references read; selected applicability and current updates remain separate from bibliography category. |
| 8.1 — Normative References | Complete references read; selected applicability and current updates remain separate from bibliography category. |
| 8.2 — Informative References | Complete references read; selected applicability and current updates remain separate from bibliography category. |
| A — Notes on Implementing Base64url Encoding without Padding | Unpadded base64url and S256 worked vectors reviewed and independently reproduced in retained review evidence; not a full-flow test. |
| B — Example for the S256 code_challenge_method | Unpadded base64url and S256 worked vectors reviewed and independently reproduced in retained review evidence; not a full-flow test. |

### RFC8252

| Section | Disposition |
| --- | --- |
| 1 — Introduction | External user agent replaces embedded authorization approaches. |
| 2 — Notational Conventions | BCP14 interpretation. |
| 3 — Terminology | External browser security domain distinguished from controllable web view; hybrid apps count as native. |
| 4 — Overview | Separate browser context protects credentials and reuses authentication state. |
| 4.1 — Authorization Flow for Native Apps Using the Browser | Six-step browser/code/token exchange reviewed. |
| 5 — Using Inter-App URI Communication for OAuth | External user agent required for native authorization. |
| 6 — Initiating the Authorization Request from a Native App | Authorization code and PKCE required for public native clients; platform browser tab permitted if isolation retained. |
| 7 — Receiving the Authorization Response in a Native App | Full server support includes all three redirect options; local loopback-only experiment does not claim full checklist. |
| 7.1 — Private-Use URI Scheme Redirection | Private-use scheme must be reverse domain under app control; not selected by loopback experiment. |
| 7.2 — Claimed "https" Scheme URI Redirection | Claimed HTTPS callbacks preferred when available; platform ownership guarantee needs implementation evidence. |
| 7.3 — Loopback Interface Redirection | IP-literal loopback with dynamic port; try available IPv4/IPv6. |
| 8 — Security Considerations | Security requirements apply to selected flow. |
| 8.1 — Protecting the Authorization Code | Code interception mitigated by verifier possession; PKCE support mandatory. |
| 8.2 — OAuth Implicit Grant Authorization Flow | Implicit grant not selected. |
| 8.3 — Loopback Redirect Considerations | Loopback HTTP exception local only, listener restricted and temporary, localhost discouraged. |
| 8.4 — Registration of Native App Clients | Register public type and complete callback, match exactly except loopback port. |
| 8.5 — Client Authentication | Bundled shared secret cannot authenticate public client installation. |
| 8.6 — Client Impersonation | Previous consent alone does not prove current client identity. |
| 8.7 — Fake External User-Agents | Fake browser UI remains malicious-app threat. |
| 8.8 — Malicious External User-Agents | Malicious default handler is broader device compromise. |
| 8.9 — Cross-App Request Forgery Protections | Fresh random state binds pending request; unmatched callbacks rejected. |
| 8.10 — Authorization Server Mix-Up Mitigation | Distinct issuer redirect defense and retained exact callback required; selected RFC9207/RFC9700 issuer defense must be stated explicitly. |
| 8.11 — Non-Browser External User-Agents | Other external agents outside selected browser profile. |
| 8.12 — Embedded User-Agents | Embedded authorization prohibited; credential/cookie access and phishing boundaries reviewed. |
| 9 — IANA Considerations | No new IANA actions; domain-based scheme registration guidance reviewed. |
| 10 — References | References read, not automatically recursively audited. |
| 10.1 — Normative References | Normative references enumerated and read. |
| 10.2 — Informative References | Informative references read; historical AppAuth links not current API certification. |
| A — Server Support Checklist | Five-point server checklist read; broader than loopback experiment. |
| B — Platform-Specific Implementation Details | Platform appendix explicitly nonnormative and historical. |
| B.1 — iOS Implementation Details | Historical iOS API/redirect descriptions; no current support claim. |
| B.2 — Android Implementation Details | Historical Android Custom Tabs/links; no current support claim. |
| B.3 — Windows Implementation Details | Historical Windows callback/exclusive-socket and broker security details; no current support claim. |
| B.4 — macOS Implementation Details | Historical macOS browser/private-scheme/loopback options. |
| B.5 — Linux Implementation Details | Historical Linux browser launch and socket reuse cautions. |

### RFC9207

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Mix-up threat across issuers and credential destination binding; formal research claim not independently reproduced. |
| 1.1 — Conventions and Terminology | Terminology/BCP14; issuer definition sourced to8414. |
| 2 — Response Parameter iss | iss required in success and error for supporting servers; HTTPS identifier without query/fragment. |
| 2.1 — Example Authorization Response | Success callback example read. |
| 2.2 — Example Error Response | Error callback example read. |
| 2.3 — Providing the Issuer Identifier | Metadata consistency/support flag or independently configured issuer. |
| 2.4 — Validating the Issuer Identifier | Form decode then simple exact comparison; missing required issuer rejected; OIDC/JARM alternatives not selected. |
| 3 — Authorization Server Metadata | Support metadata boolean defaults false; metadata discovery not selected implicitly. |
| 4 — Security Considerations | Unique issuer per server; iss is not a general integrity signature; conflicts among multiple issuer identifiers reject. |
| 5 — IANA Considerations | Registry changes read; selected current entries independently checked. |
| 5.1 — OAuth Authorization Server Metadata | authorization_response_iss_parameter_supported entry. |
| 5.2 — OAuth Parameters Registration | iss parameter usage and references. |
| 6 — References | References read; no recursive closure claim. |
| 6.1 — Normative References | Normative reference list reviewed. |
| 6.2 — Informative References | Informative list reviewed; JARM/OIDC/JAR/dynamic registration not selected. |

:::
