---
title: HTTP semantics audit
sectionNav: true
---

# HTTP semantics audit

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) provides the HTTP foundation for answer endpoints, hosted access and service discovery. It supplies useful mechanisms for safe retrieval, conditional writes and status reporting. It does not supply Email/2 principal binding, a durable submission identifier, or a receipt proving which answer a service accepted.

The complete captured base text has been reviewed, including examples, registration tables, references, collected grammar, change appendices, index and front/end matter. Base-text review is complete; dependency closure and interoperable implementation are not.

## Consequences for Email/2

[Endpoint answers](../messages.md) need an explicit application contract above HTTP: the authorized target, authenticated participant, exact question and option, stable retry identity, and a result bound to that submission. A generic success class is insufficient: 202 is pending, whereas 200 and 201 have method-specific meanings. Transport failure and gateway failure can leave the result unknown. Conversely, individual status codes carry stronger information: 401 says this request was not applied; 408 describes an incomplete request; 421 permits retry over another connection. These statements concern the corresponding request, not every earlier attempt using the same submission identity.

[Hosted credential navigation](../delivery-policy.md#hosted-credential-navigation) addresses a particularly easy mistake: a fragment is absent from the HTTP request but can be inherited across a redirect and read by the destination's scripts. The proposed direct-entry policy is stricter than HTTP's general redirect permission because an emailed access grant must not travel to a newly selected recipient without authorization. This is a proposed application restriction, not a change to HTTP redirect semantics or evidence of implemented browser protection.

A submission profile must also specify caching, redirects, request authentication, content decoding and receipt retrieval. Essential evidence cannot rely solely on trailers, which intermediaries can discard. ETags support representation comparison and concurrency; even strong ETags are neither global event identities nor cryptographic proofs. HTTP conditional success for an apparently already-applied change does not replace exact submission deduplication.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | HTTP semantics support service interaction; they do not define email conversation identity. |
| 1.1 | Purpose | Service internals and effects beyond one response remain outside the uniform interface. |
| 1.2 | History and Evolution | HTTP/1.1, HTTP/2 and HTTP/3 share semantics; transport upgrades do not prove Email/2 capability. |
| 1.3 | Core Semantics | Interpret method, status, fields and content together. |
| 1.4 | Specifications Obsoleted by This Document | Use consolidated semantics rather than importing obsolete predecessor wording unchecked. |
| 2 | Conformance | Conformance depends on the HTTP roles implemented. |
| 2.1 | Syntax Notation | ABNF and case-sensitive notation apply; expanded list grammar has distinct sender/recipient rules. |
| 2.2 | Requirements Notation | An endpoint profile cannot redefine existing method semantics or advertise unsupported versions. |
| 2.3 | Length Requirements | Apply defensible implementation limits; no arbitrary universal Email/2 size follows from HTTP. |
| 2.4 | Error Handling | Permitted recovery is not a requirement to repair security-sensitive endpoint data. |
| 2.5 | Protocol Version | HTTP version negotiation and application capability negotiation remain separate. |
| 3 | Terminology and Core Concepts | Resource, message and intermediary terminology is adopted only for HTTP operations. |
| 3.1 | Resources | A resource URI cannot turn a safe method into answer submission. |
| 3.2 | Representations | A representation describes resource state; it is not the resource or a durable conversation event. |
| 3.3 | Connections, Clients, and Servers | Connection reuse does not establish that two requests come from one principal. |
| 3.4 | Messages | HTTP request/response messages are separate from email contributions. |
| 3.5 | User Agents | Automated clients and scanners are user agents too; retrieval is not evidence of a click. |
| 3.6 | Origin Server | Origin authority concerns its resource namespace, not a sender's conversation identity. |
| 3.7 | Intermediaries | Proxy, gateway and tunnel trust boundaries remain explicit. |
| 3.8 | Caches | Cached responses can bypass the origin; freshness and authorization require a caching profile. |
| 3.9 | Example Message Exchange | GET example illustrates ordinary retrieval, not an action receipt or secure deployment. |
| 4 | Identifiers in HTTP | Endpoint identity requires parsed URI semantics. |
| 4.1 | URI References | Resolve references against defined bases; support and bound URI lengths without truncating targets. |
| 4.2 | HTTP-Related URI Schemes | Scheme presence does not prove a service exists or supports the proposal. |
| 4.2.1 | http URI Scheme | Plain HTTP authority is insufficient for protected credentials or submission content. |
| 4.2.2 | https URI Scheme | Require secured HTTPS requests and responses; HTTPS does not hide content from the service. |
| 4.2.3 | http(s) Normalization and Comparison | Normalization must preserve origin and resource identity; path/query are not generally case-insensitive. |
| 4.2.4 | Deprecation of userinfo in http(s) URIs | Reject userinfo in message-supplied endpoints to avoid misleading authority and credential leakage. |
| 4.2.5 | http(s) References with Fragment Identifiers | Fragments are client-side references, not part of the HTTP target. |
| 4.3 | Authoritative Access | Resource authority is distinct from authorization to act in a conversation. |
| 4.3.1 | URI Origin | Bind scheme, normalized host and port; common ownership does not merge origins. |
| 4.3.2 | http Origins | DNS/routing-based plain HTTP authority does not provide authenticated service identity. |
| 4.3.3 | https Origins | Certificate-valid connection reuse still requires correct target-origin routing. |
| 4.3.4 | https Certificate Verification | Certificate matching uses service identity, not CN-ID; current identity-verification dependencies need reconciliation. |
| 4.3.5 | IP-ID Reference Identity | IP-literal service identities require exact address bytes in certificate subjectAltName. |
| 5 | Fields | Use HTTP field semantics separately from email header semantics. |
| 5.1 | Field Names | Case-insensitive names and unknown-field forwarding do not make new fields universally understood. |
| 5.2 | Field Lines and Combined Field Value | Combine repeated list fields in received order; reported erratum 9162 concerns separator wording. |
| 5.3 | Field Order | Do not blindly combine singleton fields or Set-Cookie; complete headers precede request effects. |
| 5.4 | Field Limits | Reject excessive request fields instead of silently ignoring security-relevant values. |
| 5.5 | Field Values | Control-character and singleton/list ambiguity must not create inconsistent authorization parsing. |
| 5.6 | Common Rules for Defining Field Values | Common grammar rules constrain any new endpoint fields. |
| 5.6.1 | Lists (#rule ABNF Extension) | List notation distinguishes generated syntax from tolerant receipt. |
| 5.6.1.1 | Sender Requirements | Senders do not generate empty list elements. |
| 5.6.1.2 | Recipient Requirements | Recipients tolerate reasonable empty elements without accepting empty required lists or unbounded work. |
| 5.6.2 | Tokens | Token character sets constrain names and unquoted values. |
| 5.6.3 | Whitespace | Interpret optional, required and historical whitespace per grammar. |
| 5.6.4 | Quoted Strings | Quoted-pair unescaping applies only where that production is defined. |
| 5.6.5 | Comments | Comments are legal only where explicitly allowed; do not import email comment syntax everywhere. |
| 5.6.6 | Parameters | Parameter names are case-insensitive; values follow their own definitions; no whitespace around equals. |
| 5.6.7 | Date/Time Formats | Emit IMF-fixdate and accept defined historical formats; dates are not trusted causal timestamps. |
| 6 | Message Abstraction | Keep HTTP framing, metadata and application event bytes separate. |
| 6.1 | Framing and Completeness | Framing completeness is not application acknowledgement; close-delimited responses can be ambiguous. |
| 6.2 | Control Data | Control data and version rules survive translation between HTTP versions. |
| 6.3 | Header Fields | Headers affect routing and interpretation before content processing. |
| 6.4 | Content | Content excludes transfer framing and trailers. |
| 6.4.1 | Content Semantics | Interpret content using method/status, including content-free response cases. |
| 6.4.2 | Identifying Content | Content-Location assertions do not independently authenticate a foreign resource. |
| 6.5 | Trailer Fields | Trailers remain separate from headers and cannot retroactively authorize earlier processing. |
| 6.5.1 | Limitations on Use of Trailers | Essential acknowledgement must not depend solely on trailers surviving intermediaries. |
| 6.5.2 | Processing Trailer Fields | Declared trailer names neither guarantee arrival nor permit arbitrary header merging. |
| 6.6 | Message Metadata | Message metadata is not conversation event metadata. |
| 6.6.1 | Date | Intermediaries can add or repair Date; it is not cryptographic proof of action time. |
| 6.6.2 | Trailer | Trailer advertises expected metadata without guaranteeing it will be sent. |
| 7 | Routing HTTP Messages | Bind the actual routed target to the service the user authorized. |
| 7.1 | Determining the Target Resource | Resolve target URI and exclude fragment; fragment-held credentials require a separate client mechanism. |
| 7.2 | Host and :authority | Host or :authority must match the intended target, including port. |
| 7.3 | Routing Inbound Requests | Cache, proxy and direct-origin paths have different trust and availability properties. |
| 7.3.1 | To a Cache | A cache hit is not evidence the service processed a new request. |
| 7.3.2 | To a Proxy | Proxy configuration does not authorize disclosure of mailbox credentials to the endpoint. |
| 7.3.3 | To the Origin | Direct access still requires scheme-specific authority checks. |
| 7.4 | Rejecting Misdirected Requests | Reject misdirected HTTPS requests even when a shared server holds a valid certificate. |
| 7.5 | Response Correlation | Responses can arrive before request completion; transport correlation is not durable submission identity. |
| 7.6 | Message Forwarding | Forwarding can buffer data; no real-time delivery guarantee follows from streaming syntax. |
| 7.6.1 | Connection | Hop-by-hop fields are removed; essential application semantics cannot depend on them being forwarded. |
| 7.6.2 | Max-Forwards | Max-Forwards applies to TRACE/OPTIONS diagnostics, not submission replay limits. |
| 7.6.3 | Via | Via records intermediaries and can use pseudonyms; it does not authenticate conversation authors. |
| 7.7 | Message Transformations | no-transform constrains compliant proxies but is not a cryptographic integrity guarantee. |
| 7.8 | Upgrade | Upgrade changes protocol on one connection, not the underlying transport; preserve outstanding request semantics. |
| 8 | Representation Data and Metadata | Define which encoded or decoded bytes the application authenticates. |
| 8.1 | Representation Data | Content-Type then Content-Encoding form the representation encoding model. |
| 8.2 | Representation Metadata | Metadata on HEAD describes the hypothetical GET representation. |
| 8.3 | Content-Type | Do not rely on MIME sniffing or conflicting Content-Type recovery for actionable payloads. |
| 8.3.1 | Media Type | Media type and parameter semantics require explicit endpoint formats. |
| 8.3.2 | Charset | Verified erratum 7419 substitutes Accept-Charset for the mistaken Accept-Encoding reference. |
| 8.3.3 | Multipart Types | Multipart boundary syntax does not delimit the enclosing HTTP message. |
| 8.4 | Content-Encoding | Content codings are representation properties; decoded bytes differ from coded transfer content. |
| 8.4.1 | Content Codings | Supported content codings require explicit decoding and resource limits. |
| 8.4.1.1 | Compress Coding | Legacy compress aliases do not imply required adoption by Email/2. |
| 8.4.1.2 | Deflate Coding | Deflate includes a zlib wrapper; raw-deflate compatibility must not be assumed. |
| 8.4.1.3 | Gzip Coding | Gzip CRC is not sender authentication or cryptographic integrity. |
| 8.5 | Content-Language | Content-Language describes intended linguistic audience, not authorized recipients. |
| 8.5.1 | Language Tags | Language tags are distinct from content format and principal identity. |
| 8.6 | Content-Length | Validate lengths, overflow and duplicate values; incorrect framing can enable request smuggling. |
| 8.7 | Content-Location | A receipt URL can identify a report; foreign Content-Location ownership needs independent verification. |
| 8.8 | Validator Fields | HTTP validators support state comparisons, not authenticated contribution identity. |
| 8.8.1 | Weak versus Strong | Strong validators are resource-scoped; weak validators do not prove byte equality. |
| 8.8.2 | Last-Modified | Last-Modified reports origin belief about representation change time. |
| 8.8.2.1 | Generation | Future dates are constrained and absent clocks limit generation. |
| 8.8.2.2 | Comparison | A date validator is usually weak; strength requires the stated timing evidence. |
| 8.8.3 | ETag | ETag is opaque and may appear in trailers; it is not a mandatory cryptographic digest. |
| 8.8.3.1 | Generation | Generation is server-defined; do not infer hashing or globally unique identity. |
| 8.8.3.2 | Comparison | Strong and weak comparison have different admissible matches. |
| 8.8.3.3 | Example: Entity Tags Varying on Content-Negotiated Resources | Encoded and unencoded representations need different strong tags; transfer coding alone does not. |
| 9 | Methods | Existing method semantics constrain endpoint design. |
| 9.1 | Overview | Method tokens are case-sensitive; 405 and 501 distinguish resource support from server implementation. |
| 9.2 | Common Method Properties | Safety, idempotency and cacheability are separate properties. |
| 9.2.1 | Safe Methods | GET/HEAD/OPTIONS/TRACE must not submit an answer merely because a scanner followed a URL. |
| 9.2.2 | Idempotent Methods | POST retries need known application idempotency or evidence no application occurred. |
| 9.2.3 | Methods and Caching | POST is not inherently uncachable; response caching rules must be explicit. |
| 9.3 | Method Definitions | Choose methods according to resource semantics rather than visual control labels. |
| 9.3.1 | GET | GET retrieves; request-body private agreements are not a portable submission mechanism. |
| 9.3.2 | HEAD | HEAD retrieves metadata without response content; missing generated headers need not indicate no support. |
| 9.3.3 | POST | POST fits service-specific answer processing; cached POST responses cannot satisfy later POST actions. |
| 9.3.4 | PUT | PUT creates/replaces known resource state; transformations constrain returned validators. |
| 9.3.5 | DELETE | DELETE removes URI association, not guaranteed physical erasure or recalled recipient copies. |
| 9.3.6 | CONNECT | CONNECT tunnels are not answer endpoints; arbitrary ports can expose SMTP and internal services. |
| 9.3.7 | OPTIONS | OPTIONS can describe resource capabilities but supplies no standard Email/2 capability schema. |
| 9.3.8 | TRACE | TRACE must not carry secrets and is not an adoption or security probe requirement. |
| 10 | Message Context | Context fields do not establish application-level author identity. |
| 10.1 | Request Context Fields | Minimize request context disclosed by message-triggered service access. |
| 10.1.1 | Expect | 100 Continue is interim permission to send content, not acceptance of the answer. |
| 10.1.2 | From | HTTP From is contact metadata, explicitly unsuitable for authentication/access control. |
| 10.1.3 | Referer | Referer can expose context; fragments are excluded but path/query secrets still need protection. |
| 10.1.4 | TE | TE concerns transfer/trailer handling, not support for application controls. |
| 10.1.5 | User-Agent | Avoid detailed client fingerprinting; product identity is not capability proof. |
| 10.2 | Response Context Fields | Response context needs method/status-aware interpretation. |
| 10.2.1 | Allow | Allow advertises currently supported methods, not user authorization to invoke them. |
| 10.2.2 | Location | Redirects inherit absent fragments; prevent hosted credentials reaching another origin. |
| 10.2.3 | Retry-After | Retry-After controls timing, not whether repeating the operation is safe. |
| 10.2.4 | Server | Server strings describe software and can leak detail; do not use them as trust proof. |
| 11 | HTTP Authentication | An endpoint profile must select an authentication mechanism; this framework alone selects none. |
| 11.1 | Authentication Scheme | Authentication scheme registration does not establish Email/2 principal binding. |
| 11.2 | Authentication Parameters | Parse unique authentication parameters and token68 according to their grammar. |
| 11.3 | Challenge and Response | 401 and 407 challenge different actors; never answer arbitrary challenges with mailbox credentials. |
| 11.4 | Credentials | Valid credentials with insufficient access differ from missing/invalid credentials. |
| 11.5 | Establishing a Protection Space (Realm) | Realm plus origin scopes credentials; shared realms can be broader than one action. |
| 11.6 | Authenticating Users to Origin Servers | Origin authentication is separate from proxy authentication. |
| 11.6.1 | WWW-Authenticate | 401 includes applicable challenge; multiple schemes require robust parsing. |
| 11.6.2 | Authorization | Authorization is scoped credentials, not implicit proof of conversation authorship. |
| 11.6.3 | Authentication-Info | Authentication-Info semantics belong to the chosen scheme; trailers need explicit permission. |
| 11.7 | Authenticating Clients to Proxies | Proxy credentials must remain in their intended proxy scope. |
| 11.7.1 | Proxy-Authenticate | Proxy-Authenticate concerns the next outbound client, not the email sender. |
| 11.7.2 | Proxy-Authorization | Proxy-Authorization is consumed by the intended proxy, not forwarded as endpoint credentials. |
| 11.7.3 | Proxy-Authentication-Info | Proxy authentication completion is not application action completion. |
| 12 | Content Negotiation | Negotiated format preference is distinct from negotiated application capability. |
| 12.1 | Proactive Negotiation | Servers may disregard preferences; validate the actual received format. |
| 12.2 | Reactive Negotiation | Alternative links require target and credential checks before following. |
| 12.3 | Request Content Negotiation | Response Accept/Accept-Encoding can describe future request formats without authorizing actions. |
| 12.4 | Content Negotiation Field Features | Preference syntax has absence, weight and wildcard rules. |
| 12.4.1 | Absence | Absent preferences do not prove support for every actionable format. |
| 12.4.2 | Quality Values | Quality values range from zero to one with at most three fractional digits. |
| 12.4.3 | Wildcard Values | Wildcards do not guarantee the server will honor preferences. |
| 12.5 | Content Negotiation Fields | Evaluate actual response metadata rather than inferring it from requested preferences. |
| 12.5.1 | Accept | Specific media ranges override broader ranges; apply verified example correction 7138. |
| 12.5.2 | Accept-Charset | Accept-Charset is deprecated; do not build a new fingerprinting capability exchange around it. |
| 12.5.3 | Accept-Encoding | Missing and empty Accept-Encoding differ; request support is resource/method-specific. |
| 12.5.4 | Accept-Language | Language preference must remain under user control and can reveal sensitive information. |
| 12.5.5 | Vary | Vary expands cache selection; it is not a substitute for authorization/privacy cache rules. |
| 13 | Conditional Requests | Conditional requests avoid lost updates but do not supply durable action deduplication. |
| 13.1 | Preconditions | Preconditions compare selected resource state, not global conversation history. |
| 13.1.1 | If-Match | If-Match uses strong comparison; apparent prior application may yield 2xx, so require exact receipt identity. |
| 13.1.2 | If-None-Match | If-None-Match uses weak comparison; star can guard initial creation, not prove previous content equivalence. |
| 13.1.3 | If-Modified-Since | If-Modified-Since is ignored when If-None-Match is present and only applies to GET/HEAD. |
| 13.1.4 | If-Unmodified-Since | Date preconditions have lower precision and can permit apparent-already-applied success. |
| 13.1.5 | If-Range | If-Range needs a strong validator; a mismatch yields a complete response, not appendable partial bytes. |
| 13.2 | Evaluation of Preconditions | Apply preconditions at the correct processing stage and precedence. |
| 13.2.1 | When to Evaluate | Authentication/routing errors precede conditions; conditionals do not bypass authorization. |
| 13.2.2 | Precedence of Preconditions | Follow specified precedence rather than treating all conditions as independent Boolean tests. |
| 14 | Range Requests | Range support is optional and can fall back to a complete representation. |
| 14.1 | Range Units | Range unit names are case-insensitive and independently registered. |
| 14.1.1 | Range Specifiers | Validate ranges and apply verified OWS correction 7306. |
| 14.1.2 | Byte Ranges | Byte offsets are inclusive over encoded representation bytes; guard numeric overflow. |
| 14.2 | Range | Range can be ignored, rejected or partly satisfied; inspect actual results. |
| 14.3 | Accept-Ranges | Accept-Ranges is advice, not a promise for the next request. |
| 14.4 | Content-Range | Validate bounds and unit before recombining; unknown complete length does not prove completeness. |
| 14.5 | Partial PUT | Partial PUT is not generally interoperable and can overwrite a whole resource on old implementations. |
| 14.6 | Media Type multipart/byteranges | Parse each multipart range independently; illustrative example has an invalid Last-Modified date. |
| 15 | Status Codes | Status codes describe HTTP outcomes; application receipts still bind exact submission identity. |
| 15.1 | Overview of Status Codes | Unknown codes retain class semantics; heuristic caching varies by code and method. |
| 15.2 | Informational 1xx | Interim responses are not final action outcomes. |
| 15.2.1 | 100 Continue | 100 permits continued transfer without proving application success. |
| 15.2.2 | 101 Switching Protocols | 101 switches only an agreed protocol on the existing connection. |
| 15.3 | Successful 2xx | Success class alone does not distinguish pending work from completed work. |
| 15.3.1 | 200 OK | 200 content meaning depends on request method; validate the application result. |
| 15.3.2 | 201 Created | 201 identifies created resource(s), not necessarily completion of downstream business work. |
| 15.3.3 | 202 Accepted | 202 is explicitly noncommittal; retain pending state and a defined status-query mechanism. |
| 15.3.4 | 203 Non-Authoritative Information | 203 can describe transformed content; do not silently trust it as original signed bytes. |
| 15.3.5 | 204 No Content | 204 cannot carry content or trailers; a receipt-body profile cannot accept it as an equivalent receipt. |
| 15.3.6 | 205 Reset Content | 205 requests view reset; it does not authorize erasing conversation evidence. |
| 15.3.7 | 206 Partial Content | 206 is partial retrieval; inspect ranges and total completeness. |
| 15.3.7.1 | Single Part | Single-range responses require Content-Range; example byte count is consistent. |
| 15.3.7.2 | Multiple Parts | Multipart range order/coalescing may differ from the request; inspect each part. |
| 15.3.7.3 | Combining Parts | Combine partial responses only with the same strong validator and complete coverage rules. |
| 15.4 | Redirection 3xx | Redirects can change method/target/credential scope; do not follow blindly for submissions. |
| 15.4.1 | 300 Multiple Choices | 300 alternatives are not a standard machine-readable action negotiation format. |
| 15.4.2 | 301 Moved Permanently | 301 may turn POST into GET; no implicit resubmission or migration of credentials. |
| 15.4.3 | 302 Found | 302 may turn POST into GET and is temporary. |
| 15.4.4 | 303 See Other | 303 retrieves an indirect result; the destination is not equivalent to the original target. |
| 15.4.5 | 304 Not Modified | 304 reuses a previously stored representation and carries no new content or trailers. |
| 15.4.6 | 305 Use Proxy | 305 is deprecated; do not configure a proxy from it. |
| 15.4.7 | 306 (Unused) | 306 is reserved and unused. |
| 15.4.8 | 307 Temporary Redirect | 307 preserves method when followed; preservation does not authorize a new recipient. |
| 15.4.9 | 308 Permanent Redirect | 308 preserves method per verified erratum 7109; permanent redirect is not principal migration. |
| 15.5 | Client Error 4xx | Client error class requires code-specific interpretation, not a universal rollback assumption. |
| 15.5.1 | 400 Bad Request | 400 can reflect malformed framing or deceptive routing; retain diagnostics without treating them as instructions. |
| 15.5.2 | 401 Unauthorized | 401 explicitly means this request was not applied; previous attempts may still need reconciliation. |
| 15.5.3 | 402 Payment Required | 402 is reserved, not a specified payment workflow. |
| 15.5.4 | 403 Forbidden | 403 refuses access; do not automatically retry with identical credentials. |
| 15.5.5 | 404 Not Found | 404 may conceal existence; it does not prove no prior submission or permanent absence. |
| 15.5.6 | 405 Method Not Allowed | 405 requires Allow and can be cached; support is resource-specific. |
| 15.5.7 | 406 Not Acceptable | 406 supplies negotiation failure, not permission to reinterpret arbitrary HTML as a receipt. |
| 15.5.8 | 407 Proxy Authentication Required | 407 requests proxy authentication, never endpoint or mailbox credentials interchangeably. |
| 15.5.9 | 408 Request Timeout | 408 reports incomplete request and permits retry; distinguish it from a local observation timeout. |
| 15.5.10 | 409 Conflict | 409 reports state conflict; a reused submission ID with different content needs explicit conflict semantics. |
| 15.5.11 | 410 Gone | 410 means likely permanent unavailability, not verified deletion of all stored copies. |
| 15.5.12 | 411 Length Required | 411 permits adding valid Content-Length; preserve the application identity and payload. |
| 15.5.13 | 412 Precondition Failed | 412 signals false precondition; it does not identify a prior successful attempt. |
| 15.5.14 | 413 Content Too Large | 413 refuses oversized content; temporary retry advice does not waive deduplication rules. |
| 15.5.15 | 414 URI Too Long | 414 must not trigger moving sensitive fields into a different unapproved destination. |
| 15.5.16 | 415 Unsupported Media Type | 415 distinguishes unsupported media type/content coding; do not blindly change signed bytes. |
| 15.5.17 | 416 Range Not Satisfiable | 416 can report unsatisfiable or excessive ranges; full response remains possible when Range is ignored. |
| 15.5.18 | 417 Expectation Failed | 417 concerns expectations and is distinct from answer rejection. |
| 15.5.19 | 418 (Unused) | 418 is reserved; no Email/2 use is proposed. |
| 15.5.20 | 421 Misdirected Request | 421 permits retry over another connection even for non-idempotent methods; preserve target authorization. |
| 15.5.21 | 422 Unprocessable Content | 422 distinguishes valid syntax from unusable instructions. |
| 15.5.22 | 426 Upgrade Required | 426 requires Upgrade; the illustrative HTTP/3.0 token is not a deployment recipe for transport migration. |
| 15.6 | Server Error 5xx | Server/gateway failures can leave upstream application outcome unknown. |
| 15.6.1 | 500 Internal Server Error | 500 does not establish that all application effects rolled back. |
| 15.6.2 | 501 Not Implemented | 501 reports unsupported server functionality and can be heuristically cached. |
| 15.6.3 | 502 Bad Gateway | 502 reports an invalid upstream response, not necessarily nonexecution upstream. |
| 15.6.4 | 503 Service Unavailable | 503 may provide retry timing; an unavailable server need not return it. |
| 15.6.5 | 504 Gateway Timeout | 504 reports missing timely upstream response; preserve unknown outcome until reconciled. |
| 15.6.6 | 505 HTTP Version Not Supported | 505 concerns HTTP major version, not Email/2 feature enrollment. |
| 16 | Extending HTTP | Prefer existing version-independent extension points; application features do not need a new HTTP version. |
| 16.1 | Method Extensibility | New methods require generic semantics rather than application-specific verbs. |
| 16.1.1 | Method Registry | Method registration requires IETF Review; no new method is allocated here. |
| 16.1.2 | Considerations for New Methods | New methods must define safety, idempotency, caching, content and conditional behavior. |
| 16.2 | Status Code Extensibility | Existing status meanings cannot be overridden by an application profile. |
| 16.2.1 | Status Code Registry | New status registrations require IETF Review; no code is allocated here. |
| 16.2.2 | Considerations for New Status Codes | Application result details belong in an explicit format unless generic new status semantics are justified. |
| 16.3 | Field Extensibility | Unknown fields may be ignored; required behavior needs explicit supported-profile evidence. |
| 16.3.1 | Field Name Registry | HTTP fields have a separate registry from email fields; permanent registration is Specification Required. |
| 16.3.2 | Considerations for New Fields | New fields need scope, trailer, intermediary, redirect and privacy rules. |
| 16.3.2.1 | Considerations for New Field Names | Use descriptive scoped names and avoid X- and ambiguous underscore mappings. |
| 16.3.2.2 | Considerations for New Field Values | Define duplicate/singleton behavior and comma encoding explicitly. |
| 16.4 | Authentication Scheme Extensibility | Authentication extensions must preserve framework semantics. |
| 16.4.1 | Authentication Scheme Registry | Authentication scheme registration requires IETF Review. |
| 16.4.2 | Considerations for New Authentication Schemes | Requests carry authentication context; custom credential fields need explicit cache controls. |
| 16.5 | Range Unit Extensibility | No new range unit is needed merely for button submissions. |
| 16.5.1 | Range Unit Registry | Range-unit registration requires IETF Review. |
| 16.5.2 | Considerations for New Range Units | Any future unit must define content-coding/intermediary interactions. |
| 16.6 | Content Coding Extensibility | Content-coding extension is independent of conversation operation encoding. |
| 16.6.1 | Content Coding Registry | Registration prevents incompatible reuse of transfer/content coding names. |
| 16.6.2 | Considerations for New Content Codings | Coding parameters should be self-describing rather than depend on lost metadata. |
| 16.7 | Upgrade Token Registry | Upgrade tokens are registered independently; registration does not provide deployment evidence. |
| 17 | Security Considerations | HTTP security requirements complement, not replace, application authorization and encrypted-mail boundaries. |
| 17.1 | Establishing Authority | Verify authority and show destination; origin branding and stored credentials can enable phishing. |
| 17.2 | Risks of Intermediaries | Intermediaries and caches remain trust boundaries; HTTP does not make their operators trustworthy. |
| 17.3 | Attacks Based on File and Path Names | Do not map untrusted URI/file names directly to local storage paths. |
| 17.4 | Attacks Based on Command, Code, or Query Injection | Treat request fields/content and stored diagnostics as data, never executable instructions. |
| 17.5 | Attacks via Protocol Element Length | Bound parsing, slow input and numeric conversions without inventing protocol-wide quotas. |
| 17.6 | Attacks Using Shared-Dictionary Compression | Separate secret and attacker-controlled compression contexts or disable sensitive compression. |
| 17.7 | Disclosure of Personal Information | Avoid disclosing mailbox identity, credentials and browsing state during endpoint access. |
| 17.8 | Privacy of Server Log Information | Logs can identify reading patterns even with pseudonyms; minimize and protect retained traces. |
| 17.9 | Disclosure of Sensitive Information in URIs | URLs leak through history/logs/sharing; bearer-link exposure is a deliberate weaker access model. |
| 17.10 | Application Handling of Field Names | Field-name normalization must not alias hyphens/underscores into conflicting security values. |
| 17.11 | Disclosure of Fragment after Redirects | Redirected fragments can be read by destination scripts; hosted-entry redirect restrictions address this risk. |
| 17.12 | Disclosure of Product Information | Limit product/internal-host information; version strings do not establish security assurance. |
| 17.13 | Browser Fingerprinting | Detailed negotiation fingerprints users; minimize advertised preferences. |
| 17.14 | Validator Retention | ETags are not malicious-change protection and can track users across requests. |
| 17.15 | Denial-of-Service Attacks Using Range | Many overlapping ranges amplify resource use; reject/coalesce as appropriate. |
| 17.16 | Authentication Considerations | Scheme-specific security review remains required. |
| 17.16.1 | Confidentiality of Credentials | Secure credentials before transmission; authentication alone does not prevent replay. |
| 17.16.2 | Credentials and Idle Clients | HTTP has no universal logout/credential-discard command; define expiry/revocation separately. |
| 17.16.3 | Protection Spaces | Shared-origin realms can expose credentials across tenants; isolate or narrowly scope access. |
| 17.16.4 | Additional Response Fields | Authentication response metadata can itself expose identity/protocol use. |
| 18 | IANA Considerations | Existing registrations are recorded; this draft makes no new allocation claim. |
| 18.1 | URI Scheme Registration | http/https schemes retain their registered meaning. |
| 18.2 | Method Registration | Method safety/idempotency table is preserved; wildcard method remains reserved. |
| 18.3 | Status Code Registration | Status registry entries do not define application receipt schemas. |
| 18.4 | Field Name Registration | HTTP fields moved out of email registries; Content-MD5 is obsoleted in HTTP. |
| 18.5 | Authentication Scheme Registration | No authentication scheme is defined by RFC 9110 itself. |
| 18.6 | Content Coding Registration | Coding registration includes deprecated aliases and reserved identity. |
| 18.7 | Range Unit Registration | bytes and reserved none are distinguished. |
| 18.8 | Media Type Registration | multipart/byteranges registration and q-parameter reservation apply. |
| 18.9 | Port Registration | Port registrations do not grant endpoint authorization. |
| 18.10 | Upgrade Token Registration | HTTP Upgrade token registration does not negotiate transport by itself. |
| 19 | References | Reference entries were read; dependency reading is a separate obligation. |
| 19.1 | Normative References | Caching, URI, TLS, certificate identity, MIME, grammar and encoding dependencies require their own dispositions. |
| 19.2 | Informative References | Protocol versions, cookies, authority delegation and web security dependencies remain distinct follow-ups. |
| A | Collected ABNF | Complete grammar reviewed; sender list expansion differs from tolerant receipt, and reported erratum 9164 describes equivalent normalization. |
| B | Changes from Previous RFCs | Every predecessor change subsection reviewed with verified corrections below. |
| B.1 | Changes from RFC 2818 | Apply verified erratum 7105: CN-ID handling changed despite the printed no-change claim. |
| B.2 | Changes from RFC 7230 | Apply verified erratum 8268: absolute-target priority change belongs to RFC 9112. |
| B.3 | Changes from RFC 7231 | Account for request-body interoperability, deprecated Accept-Charset and consolidated status definitions. |
| B.4 | Changes from RFC 7232 | Updated validator timing/precondition rules do not create durable action receipts. |
| B.5 | Changes from RFC 7233 | Range grammar and partial PUT changes require careful legacy compatibility. |
| B.6 | Changes from RFC 7235 | Authentication framework retained; scheme-specific review remains separate. |
| B.7 | Changes from RFC 7538 | 308 consolidation retains method-preserving semantics; see verified erratum 7109. |
| B.8 | Changes from RFC 7615 | Authentication-Info consolidation does not add a new scheme. |
| B.9 | Changes from RFC 7694 | Request content negotiation retained; predecessor examples/deployment advice are not reproduced. |
| Front matter | Abstract, status and copyright | Internet Standard STD 97 and declared replacement/update scope recorded; no adoption claim follows. |
| End matter | Acknowledgements, index and author addresses | Read completely; bibliographic navigation and attribution add no endpoint requirements. |

## Errata and example interpretation

The captured errata set contains fourteen records. Six verified corrections were also visible on the live [RFC Editor errata page](https://www.rfc-editor.org/errata/rfc9110) during this review. Reported proposals are not treated as corrections; rejected proposals are not applied.

| Record | Status | Disposition |
| --- | --- | --- |
| [7105](https://www.rfc-editor.org/errata/eid7105) | Verified | Appendix B.1 omitted the changed CN-ID rule; certificate verification follows §4.3.4. |
| [7109](https://www.rfc-editor.org/errata/eid7109) | Verified | 308 preserves the method; do not treat it as permission to turn a submission into GET. |
| [7138](https://www.rfc-editor.org/errata/eid7138) | Verified | The final Accept example row has quality 0.3, not 0.7. |
| [7306](https://www.rfc-editor.org/errata/eid7306) | Verified | Range grammar allows optional whitespace after equals; reconcile the collected grammar too. |
| [7419](https://www.rfc-editor.org/errata/eid7419) | Verified | Charset discussion refers to Accept-Charset, not Accept-Encoding. |
| [8268](https://www.rfc-editor.org/errata/eid8268) | Verified | The absolute-form routing change note belongs in RFC 9112 rather than this appendix. |
| [9162](https://www.rfc-editor.org/errata/eid9162) | Reported | Separator wording proposal; §5.3 already permits optional whitespace and recommends comma-space. Do not impose a new interoperability rejection. |
| [9164](https://www.rfc-editor.org/errata/eid9164) | Reported | Collected grammar uses equivalent normalization beyond list expansion. Preserve semantic equivalence instead of requiring textual equality. |
| [7107](https://www.rfc-editor.org/errata/eid7107) | Rejected | Referenced HTTP/1.1 trailer section exists; keep the reference. |
| [7530](https://www.rfc-editor.org/errata/eid7530) | Rejected | Processing enough to reject a request differs from applying its method. Preserve 401 nonapplication semantics. |
| [7599](https://www.rfc-editor.org/errata/eid7599) | Rejected | Do not add 205 to the framing-related no-content list; obey its separate prohibition on generated content. |
| [7870](https://www.rfc-editor.org/errata/eid7870) | Rejected | Preserve sender/forwarder distinctions in Content-Length handling. |
| [8138](https://www.rfc-editor.org/errata/eid8138) | Rejected | Proposed recursive-redirect addition is not an adopted erratum; existing loop handling and application target checks remain necessary. |
| [8459](https://www.rfc-editor.org/errata/eid8459) | Rejected | Valid status codes remain 100–599; application errors do not allocate 6xx–9xx codes. |

The examples are explanatory, not ready-made acceptance fixtures. In §14.6 the printed Last-Modified value lacks a year and uses a full month name, so it does not satisfy HTTP-date. Multipart and gzip examples contain placeholder content rather than the declared bytes. The §15.5.22 HTTP/3.0 Upgrade example must not be read as an HTTP/3 transport migration procedure: §7.8 explicitly limits Upgrade to the existing connection. A version-specific transport specification is still required.

## Coverage and remaining work

The RFC Editor JSON metadata retrieved on 19 October 2026 identifies RFC 9110 as an Internet Standard and lists no updating or obsoleting RFC. That is metadata evidence, not a completed review of every related extension. The HTML information-page fetch failed; the JSON metadata retrieval succeeded. All fourteen captured errata records were read, including original/corrected text and disposition notes; only the live page portion containing the verified records and reported-record openings was available in the browser result, so no complete live revalidation of every rejected record is claimed.

The base document's references establish follow-up obligations, not automatic inheritance of all referenced mechanisms. HTTP caching (RFC 9111), version-specific message parsing and transport (RFCs 9112–9114), URI processing (RFC 3986), TLS and service identity, cookie/browser behavior, chosen authentication schemes, content codings, and any selected structured-field mechanism require separate applicable dependency review. The certificate identity reference to RFC 6125 needs reconciliation with its current successor before implementation requirements are finalized.

No live endpoint, hosted browser flow, independent HTTP implementation, intermediary matrix or provider interoperability is validated by this reading. Acceptance work must cover scan-safe retrieval, retries after lost responses, duplicate/conflicting submissions, redirects with credentials and fragments, pending receipts, content-coding integrity, conditional-write races and cache isolation.
