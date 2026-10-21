---
title: OAuth framework audit
sectionNav: true
---

# OAuth framework audit

OAuth supplies a way for a mail client to obtain limited service access without collecting the account password. It does **not** establish that the account belongs to an Email/2 principal. The [native authorization profile](../service-authorization.md) therefore separates code redemption from an explicit device-signed account link.

This audit maps the complete RFC6749 framework to that selected profile. Authorization code, S256 PKCE, a native loopback callback, issuer binding and rotating refresh tokens form the selected path. Implicit, password, client-credentials and extension grants are not fallback sign-in methods. The [RFC9700 security audit](oauth-security.md) remains authoritative for the current security update; historical permissions in the base framework do not override it.

## Coverage and limits

The [complete RFC6749 text](https://www.rfc-editor.org/rfc/rfc6749.html), including diagrams, examples, registration templates, grammar, references and end matter, has been reviewed. The source capture contains 4,259 LF separators (4,260 indexed entries including the terminal empty entry); its SHA-256 is `f204fc8661d6c92d2ec6e0b54808f961a9ad26e792f57f312d9528335519bd71`. Official metadata checked on 20 October 2026 lists updates RFC8252, RFC8996 and RFC9700. All 31 errata in the captured official listing have individual dispositions below.

This completed source review is included in the current source inventory and section ledger. It does not prove implementation conformance, production account authentication, independent interoperability, a full live-registry review or complete transitive dependency closure. The selected registry check covers 22 entries used by code, Bearer, PKCE and issuer binding; the service scope strings are operator-defined, not claimed IANA registrations.

## Section dispositions

Each row states how the selected profile uses, restricts or excludes the source section. Exclusion means the source was reviewed and the mechanism is not selected; it does not silently add another grant to the client.

:::details Roles and registration

| Source section | Selected-profile disposition |
| --- | --- |
| [1 — Introduction](https://www.rfc-editor.org/rfc/rfc6749.html#section-1) | Delegated service access replaces sharing the account password with the mail client; it does not itself identify an Email/2 principal. |
| [1.1 — Roles](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.1) | Keep resource owner, client, authorization server and resource server roles distinct. The selected issuer/resource store has one operator. |
| [1.2 — Protocol Flow](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.2) | Apply the authorization→grant→token→resource sequence; explicit device linking is an additional independently checked step. |
| [1.3 — Authorization Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.3) | Select authorization code only; the other grant families are not automatic compatibility fallbacks. |
| [1.3.1 — Authorization Code](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.3.1) | Use short-lived single-use codes bound to client and exact redirect, supplemented by S256 PKCE. |
| [1.3.2 — Implicit](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.3.2) | Do not select browser-delivered implicit access tokens; apply RFC9700's current security guidance. |
| [1.3.3 — Resource Owner Password Credentials](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.3.3) | Do not collect the resource-owner password in the mail client; RFC9700 prohibits this grant. |
| [1.3.4 — Client Credentials](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.3.4) | Do not substitute client-credentials authority for a human account's consent or principal link. |
| [1.4 — Access Token](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.4) | Use opaque scoped, expiring access tokens; possession remains bearer authority, not device proof. |
| [1.5 — Refresh Token](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.5) | Keep refresh credentials at the token endpoint and rotate their family; never send them to service actions. |
| [1.6 — TLS Version](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.6) | Historical TLS advice is superseded by RFC8996/9700 and the selected TLS profile. |
| [1.7 — HTTP Redirections](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.7) | Authorization browser redirects are separate from service submission's no-redirect rule; do not forward credential POSTs with 307. |
| [1.8 — Interoperability](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.8) | Fill the framework's discovery/registration choices with trusted registration, not endpoints inferred from mail. |
| [1.9 — Notational Conventions](https://www.rfc-editor.org/rfc/rfc6749.html#section-1.9) | BCP14, ABNF and URI terminology apply; their appearance here does not complete transitive source review. |
| [2 — Client Registration](https://www.rfc-editor.org/rfc/rfc6749.html#section-2) | Require independent client/issuer registration before starting authorization; account consent does not register a client. |
| [2.1 — Client Types](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.1) | Treat the native client as public; a shipped shared secret cannot make it confidential. |
| [2.2 — Client Identifier](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.2) | Send the registered client_id as an identifier, never as proof of client or account identity. |
| [2.3 — Client Authentication](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.3) | Do not claim public-client authentication from client_id. Stronger client authentication requires a separately selected method. |
| [2.3.1 — Client Password](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.3.1) | Client-password/Basic authentication is not selected for this public native profile. |
| [2.3.2 — Other Authentication Methods](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.3.2) | No additional client authentication method is selected by this profile. |
| [2.4 — Unregistered Clients](https://www.rfc-editor.org/rfc/rfc6749.html#section-2.4) | Reject unregistered clients; the base framework's accommodation does not authorize email-provided registration. |

:::

:::details Endpoints and authorization grants

| Source section | Selected-profile disposition |
| --- | --- |
| [3 — Protocol Endpoints](https://www.rfc-editor.org/rfc/rfc6749.html#section-3) | Bind endpoints in trusted registration. Authorization, token and resource destinations have distinct credential rules. |
| [3.1 — Authorization Endpoint](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1) | Use the registered HTTPS authorization endpoint and external account consent; endpoint discovery is not supplied by this section. |
| [3.1.1 — Response Type](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.1) | Request response_type=code only; unknown or unsupported response types cannot select another grant. |
| [3.1.2 — Redirection Endpoint](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2) | Bind the exact chosen loopback callback to the pending attempt under RFC8252's native exception. |
| [3.1.2.1 — Endpoint Request Confidentiality](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2.1) | Use local loopback HTTP only for the selected native callback; all remote authorization/token traffic requires TLS. |
| [3.1.2.2 — Registration Requirements](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2.2) | Register the callback host/path independently, allowing only the selected ephemeral-port exception. |
| [3.1.2.3 — Dynamic Configuration](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2.3) | Do not adopt broad partial-URI matching; apply current exact matching and the explicit native port exception. |
| [3.1.2.4 — Invalid Endpoint](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2.4) | Reject invalid client/redirect requests locally at the service; never redirect an error to an unvalidated URI. |
| [3.1.2.5 — Endpoint Content](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.1.2.5) | Return minimal callback content without third-party resources; keep code/state out of exposed page content and logs. |
| [3.2 — Token Endpoint](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.2) | Send form-encoded token requests only to the registered TLS token endpoint; reject unsupported grants. |
| [3.2.1 — Client Authentication](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.2.1) | Public clients provide client_id; code/client/redirect/PKCE binding supplies the selected redemption checks, not a static secret. |
| [3.3 — Access Token Scope](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.3) | Evaluate actual granted scope as case-sensitive space-delimited tokens with order-independent set equality. Duplicate rejection is a selected restriction. |
| [4 — Obtaining Authorization](https://www.rfc-editor.org/rfc/rfc6749.html#section-4) | Only the code path below is a selected means of obtaining user authorization. |
| [4.1 — Authorization Code Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1) | Use code plus S256, issuer and transaction binding; code possession alone does not authorize an Email/2 principal. |
| [4.1.1 — Authorization Request](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.1) | Bind client_id, exact chosen redirect, scope, state and PKCE challenge to one pending attempt before opening consent. |
| [4.1.2 — Authorization Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2) | Validate state, required issuer response and original callback URI before redeeming a short-lived one-use code. |
| [4.1.2.1 — Error Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2.1) | Validate issuer/state on errors too; invalid redirects must not receive error redirects. |
| [4.1.3 — Access Token Request](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.3) | Redeem with the exact original redirect/client and verifier; claim the local attempt atomically before network access. |
| [4.1.4 — Access Token Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.4) | Process token response using §5.1 and actual scope/expiry; do not treat successful code redemption as a principal link. |
| [4.2 — Implicit Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2) | Implicit grant is not selected; do not return access tokens through browser redirects. |
| [4.2.1 — Authorization Request](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2.1) | The implicit response_type=token request is unsupported, including its example parameters. |
| [4.2.2 — Access Token Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2.2) | Fragment access-token delivery and its example do not define the selected callback behavior. |
| [4.2.2.1 — Error Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2.2.1) | Implicit fragment-error handling is not selected; use code-flow errors with issuer/transaction checks. |
| [4.3 — Resource Owner Password Credentials Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.3) | Password grant is prohibited by the current security update, regardless of historical conditional permission here. |
| [4.3.1 — Authorization Request and Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.3.1) | The mail client must not acquire account passwords to create a password-grant request. |
| [4.3.2 — Access Token Request](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.3.2) | Do not accept grant_type=password at the selected token endpoint. |
| [4.3.3 — Access Token Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.3.3) | Password-grant response examples do not add an alternate token issuance path. |
| [4.4 — Client Credentials Grant](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4) | Client-credentials grant is not selected for user account connection. |
| [4.4.1 — Authorization Request and Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.1) | Client authentication cannot stand in for resource-owner consent in this profile. |
| [4.4.2 — Access Token Request](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.2) | Do not accept grant_type=client_credentials in the selected endpoint. |
| [4.4.3 — Access Token Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4.3) | Client-credentials response behavior does not establish the account-to-principal mapping. |
| [4.5 — Extension Grants](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.5) | No absolute-URI extension grant or SAML example is selected. |

:::

:::details Tokens, extensions and native clients

| Source section | Selected-profile disposition |
| --- | --- |
| [5 — Issuing an Access Token](https://www.rfc-editor.org/rfc/rfc6749.html#section-5) | Issue tokens only after the selected code or refresh validation; keep credentials out of public receipts. |
| [5.1 — Successful Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-5.1) | Require understood case-insensitive Bearer type, exact scope set and positive JSON integer expiry (excluding bool). Refresh is required by this profile, although optional in the base response; use no-store. |
| [5.2 — Error Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-5.2) | Use the defined token error boundary without exposing credentials; reported errata do not introduce extra base errors. |
| [6 — Refreshing an Access Token](https://www.rfc-editor.org/rfc/rfc6749.html#section-6) | Rotate refresh tokens without expanding scope; atomically claim local refresh and preserve family replay detection under RFC9700. |
| [7 — Accessing Protected Resources](https://www.rfc-editor.org/rfc/rfc6749.html#section-7) | Resource requests need current token, scope, audience and action authorization; token acquisition alone is insufficient. |
| [7.1 — Access Token Types](https://www.rfc-editor.org/rfc/rfc6749.html#section-7.1) | Select Bearer under the separately audited bearer rules; do not infer MAC or sender-constrained semantics. |
| [7.2 — Error Response](https://www.rfc-editor.org/rfc/rfc6749.html#section-7.2) | Use bearer resource errors separately from token endpoint errors and service business receipts. |
| [8 — Extensibility](https://www.rfc-editor.org/rfc/rfc6749.html#section-8) | Extensions require explicit selection; this profile does not invent an OAuth grant or token type. |
| [8.1 — Defining Access Token Types](https://www.rfc-editor.org/rfc/rfc6749.html#section-8.1) | Reuse Bearer; no new access-token type registration is proposed. |
| [8.2 — Defining New Endpoint Parameters](https://www.rfc-editor.org/rfc/rfc6749.html#section-8.2) | Use reviewed PKCE/issuer extensions. Base-defined duplicates are prohibited; unknown extension repetition is not universally forbidden by that rule. |
| [8.3 — Defining New Authorization Grant Types](https://www.rfc-editor.org/rfc/rfc6749.html#section-8.3) | Do not define a new authorization grant; device linking is a separate protected service operation. |
| [8.4 — Defining New Authorization Endpoint Response Types](https://www.rfc-editor.org/rfc/rfc6749.html#section-8.4) | Reuse code response type; no compound or custom response type is selected. |
| [8.5 — Defining Additional Error Codes](https://www.rfc-editor.org/rfc/rfc6749.html#section-8.5) | Use applicable existing error codes; profile validation failures do not amend the OAuth error registry. |
| [9 — Native Applications](https://www.rfc-editor.org/rfc/rfc6749.html#section-9) | Apply RFC8252's external-agent rules instead of the historical embedded-browser option. Loopback-only client evidence does not prove full server BCP support. |

:::

:::details Security considerations

| Source section | Selected-profile disposition |
| --- | --- |
| [10 — Security Considerations](https://www.rfc-editor.org/rfc/rfc6749.html#section-10) | Apply these threats together with RFC9700; tests do not certify production authorization security. |
| [10.1 — Client Authentication](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.1) | Do not mistake a native public identifier for confidential client authentication. |
| [10.2 — Client Impersonation](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.2) | Client identity and branding cannot prove user identity; validate registered destinations and explicit account consent. |
| [10.3 — Access Tokens](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.3) | Protect access tokens in transport/storage, constrain audience/scope/lifetime and acknowledge bearer theft risk. |
| [10.4 — Refresh Tokens](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.4) | Protect and rotate refresh credentials, bind them to the client/grant family and detect reuse. |
| [10.5 — Authorization Codes](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.5) | Use expiring single-use codes bound to exact client/redirect and PKCE; reuse can revoke the affected family. |
| [10.6 — Authorization Code Redirection URI Manipulation](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.6) | Reject callback substitutions before authorization and redemption; compare the original redirect, not the augmented callback. |
| [10.7 — Resource Owner Password Credentials](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.7) | Do not retain historical password-grant mitigation as permission; current guidance prohibits the grant. |
| [10.8 — Request Confidentiality](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.8) | Use TLS for credential-bearing remote requests and keep credential material out of public journals/logs/receipts. |
| [10.9 — Ensuring Endpoint Authenticity](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.9) | Validate service certificates and registered endpoint identity; issuer response cannot select a token endpoint. |
| [10.10 — Credentials-Guessing Attacks](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.10) | Use unpredictable generated credentials and explicit processing/rate budgets; fixture defaults are not protocol security constants. |
| [10.11 — Phishing Attacks](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.11) | Use independently configured issuer and external consent. The synthetic account fixture does not demonstrate phishing-resistant production login. |
| [10.12 — Cross-Site Request Forgery](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.12) | Bind state to the local attempt and validate issuer before exchange; consume attempts atomically, including across processes. |
| [10.13 — Clickjacking](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.13) | Keep consent outside embedded mail content and prevent framing. The fixture CSP is not production deployment guidance. |
| [10.14 — Code Injection and Input Validation](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.14) | Validate parameter encodings/types, duplicates and boundaries before effects; no decoded input becomes code or markup. |
| [10.15 — Open Redirectors](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.15) | Never redirect to an unvalidated destination; fixed registration also constrains native callbacks. |
| [10.16 — Misuse of Access Token to Impersonate Resource Owner in Implicit](https://www.rfc-editor.org/rfc/rfc6749.html#section-10.16) | An access token or OAuth account subject is not delegated identity authentication or an enp0 proof; require the signed account-link step. |

:::

:::details Registries and references

| Source section | Selected-profile disposition |
| --- | --- |
| [11 — IANA Considerations](https://www.rfc-editor.org/rfc/rfc6749.html#section-11) | Reuse selected registrations; no new registry allocation or full live-registry audit is claimed. |
| [11.1 — OAuth Access Token Types Registry](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.1) | The access-token-type registry supplies the existing Bearer choice, not a new draft token type. |
| [11.1.1 — Registration Template](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.1.1) | The registration template is relevant only if a new token type is proposed; none is selected. |
| [11.2 — OAuth Parameters Registry](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.2) | Use existing endpoint parameter registrations and their request/response locations. |
| [11.2.1 — Registration Template](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.2.1) | No new OAuth parameter registration is requested by the account-link JSON schema. |
| [11.2.2 — Initial Registry Contents](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.2.2) | Initial entries are historical registry seeds; selected current entries were checked separately rather than assuming this list is current. |
| [11.3 — OAuth Authorization Endpoint Response Types Registry](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.3) | Reuse the code response type registry entry. |
| [11.3.1 — Registration Template](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.3.1) | No response-type registration template is submitted by this proposal. |
| [11.3.2 — Initial Registry Contents](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.3.2) | Code is selected; the token entry does not activate implicit flow. |
| [11.4 — OAuth Extensions Error Registry](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.4) | Use registered applicable extension errors without claiming the entire registry reviewed. |
| [11.4.1 — Registration Template](https://www.rfc-editor.org/rfc/rfc6749.html#section-11.4.1) | No new OAuth extension error registration is requested. |
| [12 — References](https://www.rfc-editor.org/rfc/rfc6749.html#section-12) | References identify dependencies; listing them is not recursive audit completion. |
| [12.1 — Normative References](https://www.rfc-editor.org/rfc/rfc6749.html#section-12.1) | Apply current selected replacements for historical TLS/HTTP/JSON requirements and separately track reached dependencies. |
| [12.2 — Informative References](https://www.rfc-editor.org/rfc/rfc6749.html#section-12.2) | Informative references can explain threats/alternatives without selecting those mechanisms or completing their review. |

:::

:::details Grammar and appendices

| Source section | Selected-profile disposition |
| --- | --- |
| [A — Augmented Backus-Naur Form (ABNF) Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A) | Apply parameter grammar to decoded values while keeping Unicode characters, UTF-8 octets and form encoding distinct. |
| [A.1 — "client_id" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.1) | client_id uses the registered identifier; it is not a secret. |
| [A.2 — "client_secret" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.2) | client_secret grammar does not activate a static secret in the public native profile. |
| [A.3 — "response_type" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.3) | Select only the code response-type value; no whitespace-separated response-type combination is negotiated. |
| [A.4 — "scope" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.4) | Apply scope-token's ASCII syntax, case sensitivity and space separation; compare sets independently of order. |
| [A.5 — "state" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.5) | Use unpredictable state retained exactly for one local attempt; narrower random formatting is a profile choice. |
| [A.6 — "redirect_uri" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.6) | Validate the decoded redirect URI against the chosen registered native callback, not merely grammar validity. |
| [A.7 — "error" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.7) | Keep OAuth error values within the applicable defined error vocabulary and encoding. |
| [A.8 — "error_description" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.8) | Treat error descriptions as untrusted readable text, never executable markup or authority. |
| [A.9 — "error_uri" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.9) | An error_uri is not a new trusted issuer, endpoint or automatic navigation instruction. |
| [A.10 — "grant_type" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.10) | Accept only authorization_code and refresh_token grants; URI-valued extension grammar is not support. |
| [A.11 — "code" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.11) | Use opaque exact code bytes; entropy/lifetime and one-use binding are independent of grammar acceptance. |
| [A.12 — "access_token" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.12) | Retain opaque access tokens confidentially; syntax does not establish audience or scope. |
| [A.13 — "token_type" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.13) | Interpret understood token types case-insensitively; select Bearer only. |
| [A.14 — "expires_in" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.14) | Serialize expires_in as a positive JSON integer in this selected response; ABNF digits do not require a JSON string. |
| [A.15 — "username" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.15) | Username grammar does not authorize password-grant collection. |
| [A.16 — "password" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.16) | Password grammar does not authorize password-grant collection. |
| [A.17 — "refresh_token" Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.17) | Treat refresh tokens as opaque confidential credentials distinct from access tokens. |
| [A.18 — Endpoint Parameter Syntax](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-A.18) | Validate parameter names and selected extension locations; do not infer universal duplicate rules for unknown extensions. |
| [B — Use of application/x-www-form-urlencoded Media Type](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-B) | Encode form parameters as UTF-8 then form escaping; decode before exact value comparisons. Do not apply JSON or raw-URI comparisons to encoded form bytes. |
| [C — Acknowledgements](https://www.rfc-editor.org/rfc/rfc6749.html#appendix-C) | Acknowledgements create no wire or trust requirement. |

:::

Front matter, status, copyright and author/contact material establish publication context and attribution, not additional endpoint or identity requirements.

## Errata dispositions

Verified corrections are applied where relevant. Reported proposals are not treated as approved amendments; Held for Document Update records retain their stated status, and the rejected correction is not applied. A reported clarification may describe behavior already required by the base text without becoming the authority for that behavior.

:::details All 31 captured errata

| Erratum | Captured status | Applicability decision |
| --- | --- | --- |
| [3446](https://www.rfc-editor.org/errata/eid3446) | Verified | Resource-owner password wording; introductory legacy-password scenario only. |
| [3500](https://www.rfc-editor.org/errata/eid3500) | Verified | Redirect is of user agent to client; exact original redirect URI binding remains required. |
| [3904](https://www.rfc-editor.org/errata/eid3904) | Verified | Missing error registry entry; registry verification remains separate. |
| [5708](https://www.rfc-editor.org/errata/eid5708) | Verified | Duplicate prohibition scoped to base-defined parameters; do not reject repetition of all unknown extensions on this authority. |
| [6613](https://www.rfc-editor.org/errata/eid6613) | Verified | Scope is a space-delimited list of case-sensitive strings. |
| [4679](https://www.rfc-editor.org/errata/eid4679) | Reported | Reported charset correction; JSON media-type treatment must follow selected current JSON contract. |
| [4745](https://www.rfc-editor.org/errata/eid4745) | Reported | Reported additional token errors not treated as base amendments. |
| [4749](https://www.rfc-editor.org/errata/eid4749) | Reported | Reported clarification of Basic encoding; public native profile does not select client password authentication. |
| [4819](https://www.rfc-editor.org/errata/eid4819) | Reported | Reported implicit-example host mismatch; implicit flow not selected. |
| [5234](https://www.rfc-editor.org/errata/eid5234) | Reported | Reported public-client wording not adopted. |
| [5332](https://www.rfc-editor.org/errata/eid5332) | Reported | Reported validation-order clarification; base4.1.1 already validates request before authorization. |
| [5793](https://www.rfc-editor.org/errata/eid5793) | Reported | Reported Basic support clarification; confidential password flow not selected. |
| [5873](https://www.rfc-editor.org/errata/eid5873) | Reported | Reported initial registry contents; no current registry validation inferred. |
| [6017](https://www.rfc-editor.org/errata/eid6017) | Reported | Reported replacement of Basic encoding not adopted; conflicts require owning auth scheme review if selected. |
| [7429](https://www.rfc-editor.org/errata/eid7429) | Reported | Reported registration actor clarification; actual client registration remains independent of account consent. |
| [7631](https://www.rfc-editor.org/errata/eid7631) | Reported | Reported authorization-code terminology correction; no MAC substitution inferred. |
| [7642](https://www.rfc-editor.org/errata/eid7642) | Reported | Reported introductory wording; no change to trust model. |
| [7715](https://www.rfc-editor.org/errata/eid7715) | Reported | Reported fragment-to-query change not adopted; implicit flow not selected. |
| [7716](https://www.rfc-editor.org/errata/eid7716) | Reported | Reported implicit-example changes not adopted; implicit flow not selected. |
| [7823](https://www.rfc-editor.org/errata/eid7823) | Reported | Reported client-credentials binding addition; client-credentials grant not selected. |
| [8722](https://www.rfc-editor.org/errata/eid8722) | Reported | Reported diagram reference clarification only. |
| [8790](https://www.rfc-editor.org/errata/eid8790) | Reported | Reported extension-duplicate default not adopted as approved correction. |
| [8791](https://www.rfc-editor.org/errata/eid8791) | Reported | Reported extension-duplicate default not adopted as approved correction. |
| [4697](https://www.rfc-editor.org/errata/eid4697) | Reported | Reported Bearer casing; base token_type is case-insensitive. |
| [4945](https://www.rfc-editor.org/errata/eid4945) | Reported | Reported grammatical change; invalid token request remains error. |
| [5379](https://www.rfc-editor.org/errata/eid5379) | Reported | Reported; JSON numeric expires_in already follows base serialization language; do not treat quoted prose as a string-type requirement. |
| [6614](https://www.rfc-editor.org/errata/eid6614) | Reported | Reported JSON member wording clarification. |
| [6615](https://www.rfc-editor.org/errata/eid6615) | Reported | Reported grammatical clarification only. |
| [3780](https://www.rfc-editor.org/errata/eid3780) | Held for Document Update | Held: public client identifier advice; candidate public profile uses client_id without static secret. |
| [4206](https://www.rfc-editor.org/errata/eid4206) | Held for Document Update | Held: compare original registered/request redirect URI, not code/state-augmented callback URI. |
| [3880](https://www.rfc-editor.org/errata/eid3880) | Rejected | Rejected correction not applied; implicit flow not selected. |

The [official errata listing](https://www.rfc-editor.org/errata_search.php?rfc=6749) was checked on 20 October 2026. Captured listing SHA-256: `2d008f9c30a13ea12604baa131bfdc75bccbbdd78a2843e9ba81248c0b1cdc4e`. Registry-related corrections do not replace the separate selected-entry check.

:::

## What remains separate

The [authorization contract](../service-authorization.md) owns the actual schemas and validation order. Its evidence includes synthetic account consent, real loopback/TLS exchange, signed linking and the protected SMTP question-to-service path. Production authentication, platform browser/key storage integration and independent service interoperability remain deployment work. Dependencies reached by a future token type, grant, metadata discovery mechanism or sender-constrained profile require their own applicability review before selection.
