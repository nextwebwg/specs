---
title: Experimental event encoding
order: 4
blurb: UTF-8 JSON · exact bytes · strict interpretation
sectionNav: true
---

# Experimental event encoding

The experimental event representation uses a restricted JSON object encoded as UTF-8. This chapter selects parsing and byte-identity rules; it includes the initial contribution envelope but does not register a media type or complete all contribution kinds. A conforming wire implementation still needs the selected security profile and MIME binding.

## Decoding and parsing

After MIME transfer decoding and any required decryption, the event octets MUST decode as valid UTF-8 without replacement characters introduced by recovery. A leading UTF-8 byte order mark is invalid. The result MUST contain exactly one JSON object, with only JSON whitespace before or after it. Comments, trailing commas and additional values are invalid.

Every object, including nested objects, MUST have unique member names after JSON escape decoding. For example, `event` and `\u0065vent` are the same name. A parser that silently keeps the first or last duplicate is insufficient. Duplicate detection must happen before the parser discards those occurrences.

All strings, including member names, MUST consist of Unicode scalar values. Properly paired surrogate escapes are accepted; lone surrogate escapes are invalid. Comparison occurs after escape decoding, without Unicode normalization or case folding. Text values retain their original sequence of scalar values. Application display may apply accessibility rules without changing those values.

A literal U+FFFD, a noncharacter or an unassigned scalar is not malformed UTF-8. A receiver must not substitute a character-assignment lookup for strict byte decoding. Internal U+FEFF remains content; the prohibition above concerns a leading byte order mark. The [UTF-8 and Unicode source review](audits/utf8.md) explains these boundaries without changing the separately selected emoji or display-property data.

The baseline event encoding admits objects, arrays, strings and booleans. JSON numbers and null are not admitted. Version identifiers are strings; identifiers use the identifier grammar. This avoids implicit rounding and ambiguous null-versus-absent field values in the initial text/choice form model. A future numeric response capability needs an explicit representation and comparison rule; a receiver MUST NOT guess one.

These restrictions intentionally narrow the grammar described in [RFC8259](https://www.rfc-editor.org/rfc/rfc8259.html). Sections 4, 6 and 8 explain the duplicate-name, numeric-precision and Unicode interoperability issues relevant here. The [base-document and errata audit](audits/json-encoding.md) is complete; transitive dependencies remain separately scoped work.

## Authenticated bytes and duplicate identity

The event's authenticated representation is its exact UTF-8 octet sequence after transfer decoding and decryption. Generators serialize once when sending and retain those bytes for retries. A receiver MUST NOT parse and reserialize an event before verifying the protection that binds those bytes. It MUST NOT substitute a normalized string, sorted object or reconstructed JSON encoding.

Object member order and insignificant JSON whitespace do not change interpretation, but changing either changes the authenticated representation. Two differently serialized records under the same authenticated event identity are therefore a conflict, even if they parse into equal objects. Implementations must reuse stored event bytes when retransmitting. This deliberate rule avoids requiring a JSON canonicalization algorithm in this experimental profile.

The security profile MUST bind these bytes together with their protocol purpose, version and applicable author/audience context. Merely signing arbitrary JSON bytes is not the complete Email Next signature construction. MIME transfer re-encoding can preserve the event bytes; changing decoded content cannot.

## Unknown fields and unsupported versions

Each operation schema enumerates its permitted members. An unknown member outside an explicitly defined extension container invalidates structured processing of that event. Misspelled fields MUST NOT be silently ignored. Unknown versions likewise leave the rich representation inactive while preserving a readable alternative with its actual protection status.

An extension container, when defined, must distinguish required semantics from optional annotations. An unknown required extension prevents structured effects. Optional data cannot change the baseline event's target, audience, authorization or meaning. This chapter does not invent an extension namespace ahead of that schema.

## Failure and resource limits

Parsing failure preserves the received source and diagnostics. It MUST NOT yield a partially accepted submission or a repaired authenticated identity. Implementations enforce the common byte and nesting limits below before constructing a JSON object tree; they may additionally enforce documented local allocation limits. Exceeding a limit is incomplete processing, not proof that the sender is malicious or that plaintext fallback is authorized. A limit failure does not authorize truncation, partial effects, splitting an authenticated event or changing its delivery protection.

## Evidence

The Python encoding experiment rejects duplicate decoded names, malformed UTF-8, lone surrogates, numbers, null and non-object roots. It preserves the exact input bytes separately from parsed values. Boundary cases also reject overlong forms, encoded surrogates, out-of-range scalars, truncation, stray continuation bytes and CESU-8 while accepting authored U+FFFD, noncharacters and unassigned scalars. The decoder checks event byte size and container depth before JSON tree construction. It is not a production streaming MIME/cryptographic pipeline and does not perform complete operation-schema validation. It does not authenticate input or implement the final cryptographic context binding.


## Solidus compatibility decision

Receivers in this experimental profile MUST accept both a literal solidus (`/`) and its JSON escape (`\/`) inside strings. Generators MUST escape solidus characters. This accepts the published RFC8259 grammar and emits a form also admitted by [verified erratum 5318](https://www.rfc-editor.org/errata/eid5318), which removes literal solidus from that grammar. The receiver rule is an explicit compatibility choice rather than a claim that the base text and correction agree.

Escape decoding yields the same string value for those forms, but their serialized bytes remain different. A retransmission MUST retain the original authenticated encoding. A gateway MUST NOT rewrite solidus escaping inside an authenticated event. JSON parsing MUST use a data parser; evaluating the text as program code is prohibited.


## Initial contribution envelope

The experimental version `0` contribution envelope has exactly the following seven required members. No additional members or extension container are admitted in this version. This selects the enclosing data shape; principal encoding, MIME binding and cryptographic context construction remain required parts of the security and transport profile.

| Member | Type and meaning |
| --- | --- |
| `version` | Exactly the string `0` |
| `purpose` | Exactly the string `contribution` |
| `event` | Event ObjectId |
| `conversation` | Conversation ObjectId |
| `principal` | Claimed author principal, in the security profile's encoding |
| `audience` | Nonempty set of distinct principal strings, including the author |
| `operation` | One complete message or attachment-message operation from the message chapter, edit operation from interaction state, or form, submit or withdraw operation from the form-operation schemas |

The audience is the complete intended principal set for this event, including the sender's own access. It is not a list of mailbox addresses or device keys. Multiple devices of one principal do not create duplicate audience entries. The author MUST NOT add a principal solely because an outer To or Cc field names it. For the selected MLS binding, the cryptographic profile must map authorized device leaves to principals and bind the resulting audience and conversation to the event's protected context. A provider or extra device outside those bindings must not be silently treated as an authorized participant.

Audience array order has no semantic meaning, but remains part of the exact authenticated bytes. Sorting it during a retry changes the record and is prohibited. Audience comparison requires exact set equality, not merely inclusion of the receiver or claimed author. Adding or removing a recipient requires a new event and the applicable group transition; retrying the original event preserves its original audience.

After strict decoding and schema checks, the receiver MUST compare the claimed version, purpose, conversation, author and complete audience against independently verified protection context bound to these exact event bytes. Header claims, a successful JSON parse or a matching conversation ID do not provide that context. Mismatch prevents structured effects. Absence of verified context leaves the event unverified, not authorized by optimistic interpretation.

A matching envelope is still not an authorized operation. Reference resolution, device authority, membership policy, form-revision validation, replay/collision handling and atomic effects remain necessary. An attacker cannot create a verified context merely by supplying an object labeled verified; that label exists only in the experiment's trusted caller interface.

Draft sync, key negotiation, group controls, rich-body binding, and edits need their own selected schemas and purpose bindings. They MUST NOT be smuggled into a form operation or accepted as unknown members. This initial envelope therefore defines message and form-event shapes without claiming that every Email Next contribution kind is already specified. Private or hidden recipients are not represented by secretly omitting principals from this audience; they require the separately specified delivery policy and cannot share a misleading common-group context.


## Version 0 event resource bounds

A decoded event is at most 1,048,576 octets, including all JSON whitespace and escape spellings. This limit applies to the exact authenticated representation after MIME transfer decoding and any decryption, not to the smaller of a parsed or reserialized representation. Generators MUST check the serialized bytes before sending. Attachments, when their manifest is specified, are separate resources and cannot evade the event limit by being inserted as giant JSON strings.

The maximum container depth is 32. The root object counts as depth1; each nested object or array increases depth by one. Strings, booleans and member names do not increase depth. Brackets and braces inside strings, including escaped quotes and backslashes, are text rather than containers. A receiver MUST enforce this limit before allocating the complete object tree. A structural pre-scan may reject excess depth but MUST NOT replace the full JSON syntax check.

These are proposed experimental interoperability limits, selected by the draft rather than inherited from JSON or requested as fixed user constraints. They bound input size and recursion without claiming to bound every implementation's allocation overhead or processing cost. A conforming receiver must support valid events up to these bounds under normal available resources; temporary resource exhaustion must be reported as incomplete processing.

Transfer and cryptographic implementations must separately bound buffering of encoded inputs and decompression, if any future profile permits it. A receiver MUST NOT allocate an unbounded MIME entity merely to discover afterward that the decoded event is too large. A bounded pipeline may stop retaining further event data once the limit is exceeded, record the failure and preserve the original through its ordinary bounded message-storage policy. It MUST NOT execute a prefix or treat limit failure as evidence for a security downgrade.


## Parser-to-schema integration evidence

The [serialized event pipeline](evidence/README.md#serialized-event-pipeline) connects strict UTF-8/JSON decoding to the envelope and operation validators. Duplicate decoded member names fail before schema validation, while structurally wrong events fail even when their JSON is valid. The original byte representation remains separate from the parsed value. These finite integration checks use fixture principal labels and do not implement the cryptographic context or MIME binding.


## Media-type category

The proposed event representation uses the application top-level category. It does not require or request a new top-level MIME type. The [registration proposal](media-type-registration.md) selects a vendor-tree candidate, +json suffix, parameter policy and template. It has not been submitted or assigned. A supplied Content-Type selects candidate parsing behavior; it MUST NOT substitute for schema validation, authenticated context or operation authorization. See the [top-level media type audit](audits/media-top-level.md).


## Principal spelling

The experimental security profile now selects [account and device identifier encodings](security-profile.md#account-and-device-identifier-encoding). Account principal fields in this envelope and its references use the enp0 encoding. This replaces the previously open spelling without making an identifier an authentication result. Test-only principal callbacks accepting names such as fixture:alice are mocks and MUST NOT be used as production wire validators.


### Registration path and authority

The [media-type registration audit](audits/media-registration.md) supplies the base registration requirements. The experimental implementation may pursue a vendor-tree registration with a complete public format specification; that tree also accommodates noncommercial producers. A standards-tree proposal requires its separately established review and organization eligibility. No candidate name in this document is an assigned or reserved identifier.

The final registration MUST distinguish payload encoding from MIME transfer encoding, define all parameters and any fragment behavior, and describe bounded parsing, authenticated-byte preservation and interaction authorization. Duplicate parameters are errors; an unknown parameter MUST NOT silently enable a new operation or protection mode. Generic JSON handling does not establish Email Next capability. A media-type match cannot authorize automatic replies, form submission, resource fetching or key installation.


## Service-question dispatch

The [service-question operation](service-answers.md#service-question-schema) uses this same contribution envelope and exact-byte protection. Its action descriptor is nested data, with an exact reference to the enclosing event. Shape validation must check that self-reference before accepting the envelope. Recognizing this operation does not assert that the client can authorize or execute its service action. Unknown operation handling and readable fallback remain unchanged.

## Reaction operation binding

The [reaction contract](reactions.md) owns the candidate `reaction` and `reaction-withdraw` operation schemas. They use this same seven-member envelope, strict encoding, exact-byte identity and authenticated context. The operation dispatcher recognizes their exact shapes; target resolution and withdrawal authority remain separate required checks before effects. MIME reaction markers cannot substitute for these checks.

## Declaring readable copies outside encryption

A question can reach an upgraded participant as a protected contribution and another person as ordinary email. The protected contribution must say that its author intends that additional disclosure. It must not put the readable question beside the ciphertext in the same protected message.

The configured experimental version `1` envelope adds one required member to the version `0` envelope: `disclosures`. All existing members retain their meanings and exact-byte identity rules. Its `audience` remains the authenticated protected group roster; readers of additional copies do not thereby become group members or acquire authority to send structured answers.

::: {.details summary="Exact disclosure descriptors"}

### Descriptor schema

`disclosures` is an array containing only these exact object shapes:

```json
{"kind":"plaintext-email"}
```

```json
{"kind":"provider-hosted","service":"https://answers.example","model":"bearer"}
```

`service` follows the [service-origin contract](service-answers.md). It is an origin, not a resource URL. Unknown members, kinds or models invalidate structured processing. At most one plaintext descriptor is allowed; it precedes all hosted descriptors. Hosted descriptors are sorted by their canonical service origin and cannot repeat an origin.

Descriptors contain no recipient identifiers, recipient counts, copy counts, grant identifiers or access tokens. A named service can still support inferences about a recipient; omission of identity and count is not a promise of perfect Bcc privacy.

An empty array declares that the author plans no external disclosure for this contribution. It cannot prove that someone will never forward or copy the content. A descriptor describes intended exposure, not successful delivery or independently verified provider behavior. Release of an external copy requires a matching durable delivery plan; schema acceptance alone never authorizes that release.

### Application agreement

Version `1` requires the [version `2` authenticated application context](security-profile.md#configured-application-agreement). A version `0` or version `1` conversation context does not enable it. Operation shape support does not imply agreement to receive that operation.

:::
