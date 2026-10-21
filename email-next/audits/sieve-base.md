---
title: Sieve base language audit
sectionNav: true
---

# Sieve base language audit

The complete captured [RFC5228](https://www.rfc-editor.org/rfc/rfc5228.html) text has been reviewed, including grammar, extended example, references, change history and end matter. Filtering can help route control traffic under receiver policy; it does not make sender-supplied messages universally invisible or authenticate their claims.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| [1](https://www.rfc-editor.org/rfc/rfc5228.html#section-1) | Introduction | Receiver-side final-delivery filtering, not sender-commanded invisibility. |
| [1.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-1.1) | Conventions Used in This Document | Usage conventions and semantic constraints supplement grammar. |
| [1.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-1.2) | Example Mail Messages | Illustrative messages do not define capability records. |
| [2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2) | Design | Language design reviewed separately from control-protocol authority. |
| [2.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.1) | Form of the Language | Token case, CRLF and NUL rules differ from event JSON. |
| [2.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.2) | Whitespace | Whitespace separates tokens; script line endings remain CRLF. |
| [2.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.3) | Comments | Both comment forms and multiline exception reviewed; apply corrected uppercase example spelling. |
| [2.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4) | Literal Data | Literal numbers, strings and lists are not executable authority. |
| [2.4.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.1) | Numbers | Binary size suffixes and integer range are Sieve-specific. |
| [2.4.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.2) | Strings | Escapes, arbitrary-octet compatibility, multiline endings and dot-stuffing require Sieve parsing. |
| [2.4.2.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.2.1) | String Lists | Existential list matching does not establish support by all recipients. |
| [2.4.2.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.2.2) | Headers | Header naming, unfolding and decoding do not authenticate control traffic. |
| [2.4.2.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.2.3) | Addresses | Outbound address grammar excludes groups/routes; invalid action addresses fail. |
| [2.4.2.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.4.2.4) | Encoding Characters Using "encoded-character" | Encoded-character ordering, octets and scalar bounds reviewed; extension declaration required. |
| [2.5](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.5) | Tests | Tests select control flow, not cryptographic authority. |
| [2.5.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.5.1) | Test Lists | Test lists implement compound predicates; no audience proof follows. |
| [2.6](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.6) | Arguments | Conflicting or repeated tagged/optional arguments are errors. |
| [2.6.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.6.1) | Positional Arguments | Required positional arguments preserve prescribed order. |
| [2.6.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.6.2) | Tagged Arguments | Tags precede positional arguments; tag ordering is otherwise flexible. |
| [2.6.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.6.3) | Optional Arguments | Defaults and comparator choice must be explicit in generated rules. |
| [2.6.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.6.4) | Types of Arguments | Grammar argument classes do not replace command-specific semantics. |
| [2.7](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.7) | String Comparison | Header names use fixed ASCII case mapping, distinct from value matching. |
| [2.7.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.7.1) | Match Type | Exact, substring and wildcard rules, empty keys and character units reviewed. |
| [2.7.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.7.2) | Comparisons across Character Sets | Charset conversion and fallback are not authenticated-byte equality. |
| [2.7.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.7.3) | Comparators | Default comparator and undefined-as-no-match cannot prove absent capability. |
| [2.7.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.7.4) | Comparisons against Addresses | Address-part matching is syntactic, not principal authentication. |
| [2.8](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.8) | Blocks | Base blocks contain no loops; extensions require separate behavior review. |
| [2.9](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.9) | Commands | Action, control and test categories do not supply a negotiation protocol. |
| [2.10](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10) | Evaluation | Evaluation and failure behavior constrain reliable control routing. |
| [2.10.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.1) | Action Interaction | Extension action interactions must be specified. |
| [2.10.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.2) | Implicit Keep | Implicit keep can leave unmatched traffic visible. |
| [2.10.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.3) | Message Uniqueness in a Mailbox | Implementation-defined mailbox deduplication is not event deduplication. |
| [2.10.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.4) | Limits on Numbers of Actions | Local action limits may cause errors; not protocol admission policy. |
| [2.10.5](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.5) | Extensions and Optional Features | Missing required extensions stop subsequent execution. |
| [2.10.6](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.6) | Errors | Errors require notification and implicit keep; atomic execution is optional. |
| [2.10.7](https://www.rfc-editor.org/rfc/rfc5228.html#section-2.10.7) | Limits on Execution | Minimum nesting support is a language requirement, not a negotiation quota. |
| [3](https://www.rfc-editor.org/rfc/rfc5228.html#section-3) | Control Commands | Control flow reviewed without assuming side-effect-free extensions. |
| [3.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-3.1) | Control if | Conditional chain selects one block; syntax/order constraints apply. |
| [3.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-3.2) | Control require | Require precedes other commands; support must not be assumed. |
| [3.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-3.3) | Control stop | Stop does not itself cancel implicit keep. |
| [4](https://www.rfc-editor.org/rfc/rfc5228.html#section-4) | Action Commands | Keep/discard/redirect required; fileinto recommended, not universal. |
| [4.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-4.1) | Action fileinto | Missing/invalid mailbox behavior may fail or deliver elsewhere. |
| [4.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-4.2) | Action redirect | Redirect preserves existing content, controls loops and null reverse paths; ignored redirect retains implicit keep. |
| [4.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-4.3) | Action keep | Keep uses normal local delivery, not a guaranteed physical folder. |
| [4.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-4.4) | Action discard | Discard is silent, cancels implicit keep only and permits retained copies. |
| [5](https://www.rfc-editor.org/rfc/rfc5228.html#section-5) | Test Commands | Required and optional tests reviewed; matching is not authentication. |
| [5.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.1) | Test address | Any matching address suffices; display names excluded; sole-address presence is not established. |
| [5.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.2) | Test allof | Logical allof does not prove complete recipient capability. |
| [5.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.3) | Test anyof | Logical anyof uses existential conditions. |
| [5.4](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.4) | Test envelope | Optional envelope test exposes this delivery's latest recipient, not a full roster. |
| [5.5](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.5) | Test exists | Exists requires all listed headers. |
| [5.6](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.6) | Test false | False is a constant predicate. |
| [5.7](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.7) | Test header | Whitespace, absent headers and empty-key semantics differ from strict event validation. |
| [5.8](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.8) | Test not | Not negates the predicate, not uncertainty in identity evidence. |
| [5.9](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.9) | Test size | Size counts IMF octets; strict under/over excludes equality and differs from decoded event size. |
| [5.10](https://www.rfc-editor.org/rfc/rfc5228.html#section-5.10) | Test true | True is a constant predicate. |
| [6](https://www.rfc-editor.org/rfc/rfc5228.html#section-6) | Extensibility | Extension interactions, version naming and loop suppression need explicit contracts. |
| [6.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.1) | Capability String | Case-sensitive names/vendor prefixes do not allocate an Email/2 capability. |
| [6.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.2) | IANA Considerations | Registration procedure does not activate a user's filter. |
| [6.2.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.2.1) | Template for Capability Registrations | Registration template reviewed; no submission made. |
| [6.2.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.2.2) | Handling of Existing Capability Registrations | Historical registry field migration reviewed. |
| [6.2.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.2.3) | Initial Capability Registrations | Initial capability entries reviewed; no current deployment support inferred. |
| [6.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-6.3) | Capability Transport | Capability advertisement goal supplies no discovery wire protocol here. |
| [7](https://www.rfc-editor.org/rfc/rfc5228.html#section-7) | Transmission | Application/sieve identifies script data, not installation authority. |
| [8](https://www.rfc-editor.org/rfc/rfc5228.html#section-8) | Parsing | Lexical and command grammars require semantic validation. |
| [8.1](https://www.rfc-editor.org/rfc/rfc5228.html#section-8.1) | Lexical Tokens | Octet ranges, comments, escaping and dot handling reviewed with legacy string rules. |
| [8.2](https://www.rfc-editor.org/rfc/rfc5228.html#section-8.2) | Grammar | Grammar acceptance is insufficient for command legality. |
| [8.3](https://www.rfc-editor.org/rfc/rfc5228.html#section-8.3) | Statement Elements | Shared argument grammar remains extensible; enabled extensions need review. |
| [9](https://www.rfc-editor.org/rfc/rfc5228.html#section-9) | Extended Example | Extended example is filtering illustration, not trusted control classification. |
| [10](https://www.rfc-editor.org/rfc/rfc5228.html#section-10) | Security Considerations | Protect scripts; constrain redirect abuse/loops; reconcile parser disagreement. |
| [11](https://www.rfc-editor.org/rfc/rfc5228.html#section-11) | Acknowledgments | Acknowledgments add no protocol requirements. |
| [12](https://www.rfc-editor.org/rfc/rfc5228.html#section-12) | Normative References | Normative references require applicability and successor review. |
| [13](https://www.rfc-editor.org/rfc/rfc5228.html#section-13) | Informative References | Historical/informative references do not close dependencies. |
| [14](https://www.rfc-editor.org/rfc/rfc5228.html#section-14) | Changes from RFC 3028 | Changes remove test-side-effect ban and reject extension; reconcile modern base behavior rather than inheriting RFC3028 assumptions. |

## Erratum and updates

[Verified editorial erratum 5579](https://www.rfc-editor.org/errata/eid5579) corrects an example to use uppercase K. The retrieved erratum page confirms its status. Use the corrected spelling in generated examples. Its note describes lowercase as invalid, but the base lexical prose calls numbers case-insensitive. This review does not turn an editorial spelling correction into a new parser-rejection rule.

RFC5228 obsoletes RFC3028. Its listed updates have separate recorded base reviews: [variables, RFC5229](sieve-variables.md), [rejection, RFC5429](sieve-rejection.md), [IMAP events, RFC6785](sieve-imap-events.md), and [mailbox identity, RFC9042](sieve-mailboxid.md). The retrieved erratum page corroborates that update list; the live JSON metadata endpoint was inaccessible to the web tool.

## Application and limits

The [security chapter](../security.md#filtering-in-older-systems) explains implicit keep, optional filing, ignored redirects, script provisioning and parser agreement. No Sieve control extension, provisioning API or interoperable hiding mechanism is selected. An application/sieve attachment remains data until an authorized configuration path installs it.

This base review does not close collation, historical RFC3028, extension applicability or transitive dependencies. It does not test a deployed Sieve implementation. No cryptographic negotiation or durable key installation follows from a successful filter action.
