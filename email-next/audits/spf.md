---
title: Sender Policy Framework audit
sectionNav: true
---

# Sender Policy Framework audit

Complete 64-page [RFC7208](https://www.rfc-editor.org/rfc/rfc7208.html), all examples, collected grammar, references and end matter reviewed. All 17 errata are covered in the [errata reconciliation](spf-errata.md). This review does not close normative dependencies or establish a tested SPF implementation.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Scope is host authorization for SMTP identities, not message content or personal authorship. |
| 1.1 | Terminology | All terminology reviewed. |
| 1.1.1 | Key Words | Requirement keywords read. |
| 1.1.2 | Imported Definitions | Imported grammar dependencies identified. |
| 1.1.3 | MAIL FROM Definition | MAIL FROM means reverse-path, not visible From. |
| 1.1.4 | HELO Definition | HELO includes EHLO and identifies the SMTP client. |
| 1.2 | check_host() | check_host is semantic algorithm, not required API name. |
| 2 | Operational Overview | Operational model reviewed in full. |
| 2.1 | Publishing Authorization | Publication, no-mail policies and policy-transition timing read. |
| 2.2 | Checking Authorization | Correct reliable inputs required; other identities not authorized by default; archaic address parsing risks noted. |
| 2.3 | The "HELO" Identity | HELO-first recommendation and valid multi-label requirement read; none is not pass. |
| 2.4 | The "MAIL FROM" Identity | MAIL FROM check and null reverse-path postmaster@HELO synthesis read; synthetic identity is not correspondent. |
| 2.5 | Location of Checks | Prefer transaction-time checks; later headers and changed DNS can mislead; avoid backscatter. |
| 2.6 | Results of Evaluation | All seven outcomes separately reviewed. |
| 2.6.1 | None | None means no usable domain or record, not authorization. |
| 2.6.2 | Neutral | Neutral makes no definite authorization assertion. |
| 2.6.3 | Pass | Pass authorizes host for evaluated identity only. |
| 2.6.4 | Fail | Fail explicitly denies host authorization. |
| 2.6.5 | Softfail | Softfail is weaker than fail. |
| 2.6.6 | Temperror | Temperror is potentially transient evaluation failure. |
| 2.6.7 | Permerror | Permerror means uninterpretable policy, not proof of forged authorship. |
| 3 | SPF Records | Publication and owner-name scope reviewed. |
| 3.1 | DNS Resource Records | TXT-only ASCII; failed dual-record migration informs common discovery baseline, not automatic TXT selection. |
| 3.2 | Multiple DNS Records | Multiple selected SPF records forbidden. |
| 3.3 | Multiple Strings in a Single DNS Record | Strings within one TXT record concatenate without spaces. |
| 3.4 | Record Size | All DNS response-size guidance read; other TXT records contribute. |
| 3.5 | Wildcard Records | Wildcard examples read; not parent-policy inheritance; reported4841 noted. |
| 4 | The check_host() Function | Full evaluation contract read; semantic equivalence required. |
| 4.1 | Arguments | IP/domain/sender arguments and global recursive accounting reviewed. |
| 4.2 | Results | Evaluation result separated from handling policy. |
| 4.3 | Initial Processing | Invalid initial domain returns none; A-label conversion and postmaster substitution reviewed. |
| 4.4 | Record Lookup | TXT lookup error/timeouts return temperror; DNS alias dependency remains open. |
| 4.5 | Selecting Records | Exact version boundary and zero/multiple-record outcomes reviewed; ABNF case rules retained. |
| 4.6 | Record Evaluation | Entire record syntax validated before evaluation. |
| 4.6.1 | Term Evaluation | Mechanism/modifier grammar and case-insensitive names read. |
| 4.6.2 | Mechanisms | Left-to-right matching, qualifiers and exceptions reviewed. |
| 4.6.3 | Modifiers | Modifiers are not predicates; redirect acts after unmatched mechanisms. |
| 4.6.4 | DNS Lookup Limits | Global ten query-causing terms, MX/PTR bounds, elapsed-time and void-lookup rules read; source limits not Email Next defaults. |
| 4.7 | Default Result | No match defaults neutral unless redirected. |
| 4.8 | Domain Specification | Invalid expanded targets explicitly unspecified; do not invent universally required behavior. |
| 5 | Mechanism Definitions | Address-family/CIDR and DNS error rules reviewed. |
| 5.1 | "all" | All always matches; later mechanisms and redirect ignored as specified. |
| 5.2 | "include" | Include is recursive predicate, not text inclusion; all seven child outcomes mapped; sender/IP unchanged. |
| 5.3 | "a" | A mechanism uses address family of client. |
| 5.4 | "mx" | MX address matching bounded; no SMTP implicit-MX fallback. |
| 5.5 | "ptr" (do not use) | PTR discouraged for publishers but required in verifiers; direction/order contradictions and reports retained. |
| 5.6 | "ip4" and "ip6" | All IP grammar and numeric range constraints read; held4453 does not remove bounds. |
| 5.7 | "exists" | Exists always queries A, including IPv6 clients; arbitrary expanded queries disclose data. |
| 6 | Modifier Definitions | Known modifier duplicates fail; unknown modifiers ignored. |
| 6.1 | redirect: Redirected Query | Redirect replaces result/policy; absent or malformed target permerror; all overrides redirect. |
| 6.2 | exp: Explanation | Explanation errors do not change result; ASCII, attribution and include/redirect precedence reviewed. |
| 7 | Macros | Macro mechanism reviewed in full. |
| 7.1 | Formal Specification | Complete macro ABNF and literal escapes read. |
| 7.2 | Macro Definitions | All macro names and explanation-only restrictions read. |
| 7.3 | Macro Processing Details | Split/reverse/right-parts, IPv6, URL escape, length handling and dependency-aware caching reviewed. |
| 7.4 | Expansion Examples | All IPv4/IPv6 expansion examples read. |
| 8 | Result Handling | SMTP and delivered-message handling options read; no universal rejection policy. |
| 8.1 | None | None permits no authorization conclusion. |
| 8.2 | Neutral | Neutral MUST be treated like none. |
| 8.3 | Pass | Pass permits domain responsibility assessment, not verified-person indication. |
| 8.4 | Fail | Fail handling/local policy and verified6721 multiline reply correction read; RFC7372 update applies separately. |
| 8.5 | Softfail | Softfail alone SHOULD NOT cause rejection. |
| 8.6 | Temperror | Transient lookup handling reviewed; no key downgrade authority. |
| 8.7 | Permerror | Uninterpretable-policy handling reviewed; macros may cause errors. |
| 9 | Recording the Result | Both result formats read; consistency and provenance required. |
| 9.1 | The Received-SPF Header Field | All fields, ABNF and examples read; verified5436 and reported5843 distinguished. |
| 9.2 | SPF Results in the Authentication-Results Header Field | Authentication-Results is less reconstructive; current RFC8601 reviewed separately. |
| 10 | Effects on Infrastructure | Operational advice distinguished from normative protocol. |
| 10.1 | Sending Domains | Outbound architecture and administrative policy reviewed. |
| 10.1.1 | DNS Resource Considerations | All cost comparison examples read. |
| 10.1.2 | Administrator's Considerations | No-mail and host-policy examples read; not discovery advertisements. |
| 10.1.3 | Bounces | Null-path/HELO bounce behavior reviewed. |
| 10.2 | Receivers | Pass may be harmful; fail may follow legitimate forwarding. |
| 10.3 | Mediators | Last-hop IP changes through mediators; no automatic endpoint-identity consequence. |
| 11 | Security Considerations | All security subsections read. |
| 11.1 | Processing Limits | Amplification, exhaustion and third-party query risks reviewed. |
| 11.2 | SPF-Authorized Email May Contain Other False Identities | Other message identities may be false despite SPF pass. |
| 11.3 | Spoofed DNS and IP Data | DNS integrity and reliable connection IP are assumptions. |
| 11.4 | Cross-User Forgery | Shared MTA users can forge other local users absent submission controls; SPF is not personal-key authentication. |
| 11.5 | Untrusted Information Sources | SMTP and DNS input remain untrusted data. |
| 11.5.1 | Recorded Results | Recorded results and reply text require injection/length checks. |
| 11.5.2 | External Explanations | Third-party explanation links can be malicious; no automatic discovery fetch. |
| 11.5.3 | Macro Expansion | Macro expansions can inject hostile lookup text. |
| 11.6 | Privacy Exposure | Queries reveal sender and possible receiving-system information. |
| 11.7 | Delivering Mail Producing a "Fail" Result | Failure handling does not establish reputation or distinguish known/good actors. |
| 12 | Collected ABNF | Complete collected ABNF read; takes precedence over fragments; verified5436 applies. |
| 13 | Contributors and Acknowledgements | Acknowledgments read. |
| 14 | IANA Considerations | All registration actions read; live registry reconciliation remains open. |
| 14.1 | The SPF DNS Record Type | RRtype99 no longer used by SPFv1. |
| 14.2 | The Received-SPF Mail Header Field | Received-SPF registration read. |
| 14.3 | SPF Modifier Registry | Exp/redirect modifier reference updates read. |
| 15 | References | All references read. |
| 15.1 | Normative References | Normative DNS/URI/IP/IDNA/architecture dependency closure remains open. |
| 15.2 | Informative References | All informative references read; no assertion that all historical experiments are standardized. |
| Appendix A | Extended Examples | All DNS fixtures and examples read; A.4 type and target defects recorded. |
| Appendix B | Changes in Implementation Requirements from RFC 4408 | Entire implementation-change list read. |
| Appendix C | Further Testing Advice | Tracking exists example exposes sender/IP/HELO via DNS without special verifier cooperation. |
| Appendix D | SPF/Mediator Interactions | All sender/mediator/receiver mitigations read; none supplies endpoint key negotiation. |
| Appendix E | Mail Services | Shared service cross-customer forgery risk reviewed. |
| Appendix F | MTA Relays | Boundary inputs and secondary-MX issues reviewed. |
| Appendix G | Local Policy Considerations | All local policy considerations, queue-delay risks and end matter read. |

## Consequences for Email Next

SPF is useful transport-domain evidence. It does not authenticate encryption keys, visible authors or every user of a shared sending service. Forwarding can change SPF results without changing an endpoint-protected contribution. The [discovery contract](../capability-discovery.md) therefore separates capabilities and keys from SPF, limits diagnostic authority, and requires privacy-aware lookup and caching rules.

The failed SPF record-type migration supplies a concrete lesson: every conforming implementation needs a shared publication-and-retrieval baseline. Optional upgraded paths cannot replace that baseline before compatible overlap is defined.

RFC7372, RFC8553 and RFC8616 have separate recorded reviews. Remaining DNS, URI, address and architecture dependencies and current registry verification remain open. PTR contradictions and invalid expanded-domain behavior are source limitations, not silently resolved new SPF requirements.
