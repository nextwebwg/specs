---
title: Experimental event encoding
order: 4
blurb: UTF-8 JSON · exact bytes · strict interpretation
sectionNav: true
---

# Experimental event encoding

The experimental event representation uses a restricted JSON object encoded as UTF-8. This chapter selects parsing and byte-identity rules; it includes the initial contribution envelope but does not register a media type or complete all contribution kinds. A conforming wire implementation still needs the selected security profile and MIME binding.

## Start with the current agreement

Current Encryption clients implement [authored0, envelope6, context10 and mime-suite-v2](suite-profile.md#current-client-baseline). The complete original authored record identifies one message; separately secured envelopes identify its actual deliveries. [Slot reply-intent1 and protected per-message addresses](#asynchronous-authored-records-and-deliveries) retain the full intended recipients while independently ready deliveries progress.

All current protected readers implement the fixed twelve-kind readable vocabulary, required rich/indexed rendering, scope processing and written-reply rules. Answer buttons, reactions, corrections, service actions and hosted-reply interactions require their separately declared complete local capabilities. They do not reduce the readable application to a common optional subset. General form/submit/withdraw operations remain deferred.

The version0/version1 contribution sections below and retained envelope4/5 agreements are exact compatibility encodings. Their fields, signatures and evidence cannot be mixed into the current grammar. Common strict parsing and byte-identity rules apply where the selected owner incorporates them; wrapper6 has its own larger bound, and a signed record's explicit null exception never widens authored events.

## Decoding and parsing

After MIME transfer decoding and any required decryption, the event octets MUST decode as valid UTF-8 without replacement characters introduced by recovery. A leading UTF-8 byte order mark is invalid. The result MUST contain exactly one JSON object, with only JSON whitespace before or after it. Comments, trailing commas and additional values are invalid.

Every object, including nested objects, MUST have unique member names after JSON escape decoding. For example, `event` and `\u0065vent` are the same name. A parser that silently keeps the first or last duplicate is insufficient. Duplicate detection must happen before the parser discards those occurrences.

All strings, including member names, MUST consist of Unicode scalar values. Properly paired surrogate escapes are accepted; lone surrogate escapes are invalid. Comparison occurs after escape decoding, without Unicode normalization or case folding. Text values retain their original sequence of scalar values. Application display may apply accessibility rules without changing those values.

A literal U+FFFD, a noncharacter or an unassigned scalar is not malformed UTF-8. A receiver must not substitute a character-assignment lookup for strict byte decoding. Internal U+FEFF remains content; the prohibition above concerns a leading byte order mark. The [UTF-8 and Unicode source review](audits/utf8.md) explains these boundaries without changing the separately selected emoji or display-property data.

The baseline event encoding admits objects, arrays, strings and booleans. JSON numbers and null are not admitted in contribution events. A different signed record may admit null only where its owning schema explicitly defines it: [assertion8](suite-profile.md#creating-a-delivery-and-receiving-it-later) and retained [assertion9](reply-intent.md#reply-aware-protected-agreement) each require `keyPackageReceiveUntil: null` when no package is supplied, and permits root `controlKey: null` only when no usable control key is published and no MLS package is supplied. Current [assertion10](suite-profile.md#asynchronous-protected-agreement) inherits precisely these two root-member exceptions. These exceptions apply only to those exact root members and version; it does not make null valid in other fields, nested values or older advertisements. Version identifiers are strings; identifiers use the identifier grammar. This avoids implicit rounding and ambiguous null-versus-absent field values in the initial text/choice form model. A future numeric response capability needs an explicit representation and comparison rule; a receiver MUST NOT guess one.

These restrictions intentionally narrow the grammar described in [RFC8259](https://www.rfc-editor.org/rfc/rfc8259.html). Sections 4, 6 and 8 explain the duplicate-name, numeric-precision and Unicode interoperability issues relevant here. The [base-document and errata audit](audits/json-encoding.md) is complete; transitive dependencies remain separately scoped work.

## Authenticated bytes and duplicate identity

The event's authenticated representation is its exact UTF-8 octet sequence after transfer decoding and decryption. Generators serialize once when sending and retain those bytes for retries. A receiver MUST NOT parse and reserialize an event before verifying the protection that binds those bytes. It MUST NOT substitute a normalized string, sorted object or reconstructed JSON encoding.

Object member order and insignificant JSON whitespace do not change interpretation, but changing either changes the authenticated representation. Two differently serialized records under the same authenticated event identity are therefore a conflict, even if they parse into equal objects. Implementations must reuse stored event bytes when retransmitting. This deliberate rule avoids requiring a JSON canonicalization algorithm in this experimental profile.

The security profile MUST bind these bytes together with their protocol purpose, version and applicable author/audience context. Merely signing arbitrary JSON bytes is not the complete Email/2 signature construction. MIME transfer re-encoding can preserve the event bytes; changing decoded content cannot.

## Unknown fields and unsupported versions

Each operation schema enumerates its permitted members. An unknown member outside an explicitly defined extension container invalidates structured processing of that event. Misspelled fields MUST NOT be silently ignored. Unknown versions likewise leave structured operation processing inactive while preserving a readable alternative with its actual protection status.

An extension container, when defined, must distinguish required semantics from optional annotations. An unknown required extension prevents structured effects. Optional data cannot change the baseline event's target, audience, authorization or meaning. This chapter does not invent an extension namespace ahead of that schema.

## Failure and resource limits

Parsing failure preserves the received source and diagnostics. It MUST NOT yield a partially accepted submission or a repaired authenticated identity. Implementations enforce the common byte and nesting limits below before constructing a JSON object tree; they may additionally enforce documented local allocation limits. Exceeding a limit is incomplete processing, not proof that the sender is malicious or that plaintext fallback is authorized. A limit failure does not authorize truncation, partial effects, splitting an authenticated event or changing its delivery protection.

## Evidence

The Python encoding experiment rejects duplicate decoded names, malformed UTF-8, lone surrogates, numbers, null and non-object roots by default. Its explicit root-member exception lets the assertion8 and separately selected assertion9 parsers admit their schema-defined null without changing older callers. It preserves the exact input bytes separately from parsed values. Boundary cases also reject overlong forms, encoded surrogates, out-of-range scalars, truncation, stray continuation bytes and CESU-8 while accepting authored U+FFFD, noncharacters and unassigned scalars. The decoder checks event byte size and container depth before JSON tree construction. It is not a production streaming MIME/cryptographic pipeline and does not perform complete operation-schema validation. It does not authenticate input or implement the final cryptographic context binding.


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

Draft sync, key negotiation, group controls, rich-body binding, and edits need their own selected schemas and purpose bindings. They MUST NOT be smuggled into a form operation or accepted as unknown members. This initial envelope therefore defines message and form-event shapes without claiming that every Email/2 contribution kind is already specified. Private or hidden recipients are not represented by secretly omitting principals from this audience; they require the separately specified delivery policy and cannot share a misleading common-group context.


## Version 0 event resource bounds

A decoded event is at most 1,048,576 octets, including all JSON whitespace and escape spellings. This limit applies to the exact authenticated representation after MIME transfer decoding and any decryption, not to the smaller of a parsed or reserialized representation. Generators MUST check the serialized bytes before sending. Attachments, when their manifest is specified, are separate resources and cannot evade the event limit by being inserted as giant JSON strings.

The maximum container depth is 32. The root object counts as depth1; each nested object or array increases depth by one. Strings, booleans and member names do not increase depth. Brackets and braces inside strings, including escaped quotes and backslashes, are text rather than containers. A receiver MUST enforce this limit before allocating the complete object tree. A structural pre-scan may reject excess depth but MUST NOT replace the full JSON syntax check.

These are proposed experimental interoperability limits, selected by the draft rather than inherited from JSON or requested as fixed user constraints. They bound input size and recursion without claiming to bound every implementation's allocation overhead or processing cost. A conforming receiver must support valid events up to these bounds under normal available resources; temporary resource exhaustion must be reported as incomplete processing.

Transfer and cryptographic implementations must separately bound buffering of encoded inputs and decompression, if any future profile permits it. A receiver MUST NOT allocate an unbounded MIME entity merely to discover afterward that the decoded event is too large. A bounded pipeline may stop retaining further event data once the limit is exceeded, record the failure and preserve the original through its ordinary bounded message-storage policy. It MUST NOT execute a prefix or treat limit failure as evidence for a security downgrade.


## Parser-to-schema integration evidence

The [serialized event pipeline](evidence/README.md#serialized-event-pipeline) connects strict UTF-8/JSON decoding to the envelope and operation validators. Duplicate decoded member names fail before schema validation, while structurally wrong events fail even when their JSON is valid. The original byte representation remains separate from the parsed value. These finite integration checks use fixture principal labels and do not implement the cryptographic context or MIME binding.


## Indexed reply content

The proposed [reply-message operation](reply-content.md) carries a chunk index and corresponding HTML Microdata, with exact source selectors for text quotations. It requires its own explicit application/carrier agreement; the old operation dispatchers and immutable profiles remain unchanged. Generic JSON or Microdata recognition cannot enable it.

## Media-type category

The proposed event representation uses the application top-level category. It does not require or request a new top-level MIME type. The [registration proposal](media-type-registration.md) selects a vendor-tree candidate, +json suffix, parameter policy and template. It has not been submitted or assigned. A supplied Content-Type selects candidate parsing behavior; it MUST NOT substitute for schema validation, authenticated context or operation authorization. See the [top-level media type audit](audits/media-top-level.md).


## Principal spelling

The experimental security profile now selects [account and device identifier encodings](security-profile.md#account-and-device-identifier-encoding). Account principal fields in this envelope and its references use the enp0 encoding. This replaces the previously open spelling without making an identifier an authentication result. Test-only principal callbacks accepting names such as fixture:alice are mocks and MUST NOT be used as production wire validators.


### Registration path and authority

The [media-type registration audit](audits/media-registration.md) supplies the base registration requirements. The experimental implementation may pursue a vendor-tree registration with a complete public format specification; that tree also accommodates noncommercial producers. A standards-tree proposal requires its separately established review and organization eligibility. No candidate name in this document is an assigned or reserved identifier.

The final registration MUST distinguish payload encoding from MIME transfer encoding, define all parameters and any fragment behavior, and describe bounded parsing, authenticated-byte preservation and interaction authorization. Duplicate parameters are errors; an unknown parameter MUST NOT silently enable a new operation or protection mode. Generic JSON handling does not establish Email/2 capability. A media-type match cannot authorize automatic replies, form submission, resource fetching or key installation.


## Service-question dispatch

The [service-question operation](service-answers.md#service-question-schema) uses this same contribution envelope and exact-byte protection. Its action descriptor is nested data, with an exact reference to the enclosing event. Shape validation must check that self-reference before accepting the envelope. Recognizing this operation does not assert that the client can authorize or execute its service action. Unknown operation handling and readable fallback remain unchanged.

## Reaction operation binding

The [reaction contract](reactions.md) owns the candidate `reaction` and `reaction-withdraw` operation schemas. The retained version0 dispatch uses the seven-member contribution envelope, strict encoding, exact-byte identity and authenticated context. Current dispatch uses the authored0 logical targets and envelope6 delivery binding defined below; the reaction operation’s exact own fields remain unchanged. The operation dispatcher recognizes their exact shapes; target resolution and withdrawal authority remain separate required checks before effects. MIME reaction markers cannot substitute for these checks.

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

An empty array declares that the author plans no external disclosure for this contribution. It cannot prove that someone will never forward or copy the content. A descriptor describes intended exposure, not successful delivery or independently verified provider behavior. It is the plan for the original authenticated bytes, not a live global disclosure ledger. The [frozen-disclosure rules](delivery-policy.md#freeze-disclosure-before-releasing-content) govern later fallback or sharing changes; they cannot rewrite an existing event’s array. Release of an external copy requires a matching durable delivery plan; schema acceptance alone never authorizes that release.

### Application agreement

Version `1` requires the [version `2` authenticated application context](security-profile.md#configured-application-agreement). A version `0` or version `1` conversation context does not enable it. Operation shape support does not imply agreement to receive that operation.

:::


## Ordinary authored carriage

An ordinary email can include the same structured reaction that an upgraded client
would receive through a protected delivery. It carries the original writing, not
an invented encryption envelope. The receiving client can inspect its exact reply
target while keeping the email's actual unprotected status visible.

The ordinary representation uses the unregistered candidate
`application/vnd.threadlabs.mail-authored+json`. The
[registration contract](media-type-registration.md#ordinary-authored-candidate)
owns its media-type rules. This representation does not change the secured
`mail-event` carrier or supply encryption support for a recipient.

::: {.details summary="Exact ordinary representation and trust boundary"}

The decoded payload MUST be the complete original authored0 octets, with
`version` equal to `0` and `purpose` equal to `authored-contribution`. Apply the
[authored-record schema](#asynchronous-authored-records-and-deliveries), strict JSON,
Unicode, duplicate/unknown-member, byte and depth rules. Do not reserialize or
strip scope, addresses or disclosure members. No delivery event, native audience,
slot mapping, package or protection context is added. The first ordinary binding
admits only the selected `reaction` and `reaction-withdraw` operations; it carries
no resources. Other operations remain unsupported in this binding.

The generated ordinary layout is `multipart/alternative` with exactly three
children in order: UTF-8 `text/plain`, inert UTF-8 `text/html`, and the ordinary
authored representation. The structured child has no media parameters and uses
base64 transfer encoding. The readable children preserve the operation's meaning
and exact references without quoting target content. The optional first RFC9078
part and its enclosing mixed wrapper follow the
[reaction projection](reactions.md#readable-ordinary-email-projection). It is not
an extra part in a secured mime-suite-v2 carrier. Ambiguous, duplicate, nested or
wrong-order candidates leave this generated-layout selector inactive with the
original source available.

Every parsed result MUST remain an ordinary unprotected, unverified candidate.
Syntax, From, DKIM, transport TLS, a Message-ID and a matching emoji MUST NOT admit
a native contribution, reserve an authenticated namespace, change a trusted
reaction count, withdraw an accepted reaction, execute a service action or supply
missing target history. Failed or unsupported structured parsing MUST NOT promote
a neighboring legacy reaction to trusted status. Reading this representation
MUST NOT trigger setup, remote resource retrieval or another response.

A receiver MAY relate the ordinary representation to an independently accepted
protected event only after comparing the complete original authored bytes and
rechecking the owning current presentation permission. That comparison adds
ordinary delivery provenance; it does not authenticate this carrier or create a
second trusted effect. Different authenticated bytes retain the existing
conflict rules. Unauthenticated variants cannot reserve or poison a protected
namespace. A gateway that removes or changes the structured record leaves no
proof of equivalence from emoji, subject or sender spelling alone.

Before generation or release, the sender MUST retain the deliberate ordinary
permission for the actual destination and the complete exposed authored record,
including its scope, personal addresses, identifiers and references, plus the
readable alternatives and outer routing metadata. Authorization for visible text
alone is insufficient. Private/Bcc copies use their own independently authored
records; a visible record MUST NOT be substituted or edited into a private copy.
A reference alone authorizes neither disclosure of its target nor resource access.

The ordinary sender retains immutable prepared bytes, original deadlines,
per-destination outcomes and possible-release uncertainty under the existing
outbox contract. Separate ordinary permission does not mutate an earlier
protected preparation or claim atomic network delivery. Earlier media types and
negotiated carriers keep their original parsers; receivers MUST NOT try this
ordinary parser as recovery for a failed secured carrier.

:::

## Asynchronous authored records and deliveries

One person’s writing can travel through several separately encrypted deliveries. Keep the writing as one immutable record. Put the actual recipients and delivery identity around it, so a later copy for a newly ready recipient does not become a second message or change what the author originally said.

The components below select exact records for the [asynchronous-group design](delivery-policy.md#one-message-several-deliveries). The [selected asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) defines context10/assertion10, native admission, readable capability selection and mime-suite-v2. The [automatic acquisition binding](first-contact-setup.md#acquisition-for-independently-ready-deliveries) is selected. The [ongoing own-device setup binding](paired-configuration.md#keep-setup-current-between-your-own-devices) is selected. The [pending-delivery lifecycle](delivery-policy.md#complete-a-pending-delivery) is selected. This is the current draft baseline; complete implementation and independent acceptance remain separate outcomes. These records cannot be inserted into retained envelope5, selected by MIME sniffing, or advertised as supported merely because a parser recognizes them.

### Follow one exchange

The [synthetic exchange catalog](examples/async-exchange.json) lists the original records and their separate delivery envelopes. It is a fixture index, not a wire message. The samples contain no signatures, native admission or transport evidence and must not be submitted to an earlier envelope5 context.

| Authored contribution | Intended visible discussion |
| --- | --- |
| [Alice: “Which day works?”](examples/async-root-authored.json) | Alice, Bob and Carol; Carol’s principal is initially unresolved. |
| [Bob: “Thursday works for me.”](examples/async-reply-authored.json) | The same discussion; the parent names Alice’s logical question, rather than Bob’s particular received delivery. |
| [Alice: “Great — Thursday it is.”](examples/async-followup-authored.json) | The same discussion; the parent names Bob’s logical reply. |

Bob can first receive [Alice’s ready delivery](examples/async-root-first-delivery.json). Alice later [resolves Carol’s slot for Bob](examples/async-resolution-authored.json) through a separately authenticated control; that control is not a fourth visible conversation message. Bob still applies his own current recipient and disclosure checks.

Carol’s [Bob reply delivery](examples/async-reply-late-delivery.json) can arrive before [Alice’s original delivery](examples/async-root-late-delivery.json). The missing scope/root relationship stays pending. Once the original independently validates, both copies resolve through the same logical identifiers. Alice’s [follow-up delivery](examples/async-followup-late-delivery.json) then completes the three-message exchange in Carol’s available history. Neither the catalog’s order nor its labels supply authentication or prove an implemented pending queue.

::: {.details summary="Immutable authored-record version0"}

The authored record is a strict UTF-8 JSON object with exactly the ten members below. Its complete original bytes, not a reserialized object, identify its authenticated content across deliveries. Common scalar, duplicate-name, unknown-member, number/null and depth rules apply. Its decoded size is at most 1,048,576 octets; embedded HTML and scope definitions share that allowance.

| Member | Requirement |
| --- | --- |
| `version` | String `"0"`. |
| `purpose` | String `"authored-contribution"`. |
| `event` | Nonzero Event ObjectId for the logical authored contribution. |
| `conversation` | Nonzero Conversation ObjectId. |
| `principal` | Authenticated author principal under the selected identity profile. |
| `scope` | Exactly one of the scope selections below. |
| `operation` | One complete explicitly selected operation, with the logical-reference rules below. |
| `disclosures` | The existing exact planned-exposure descriptors, order and confidentiality meaning. They commit the author’s planned additional exposure; another delivery cannot edit them. |
| `presentation` | Exactly the seven members below. |
| `replyIntent` | The exact slot-based version1 record below. |

A creating scope selection has exactly `kind`, `root` and `definition`. `kind` is `"create"`; `root` equals this authored record’s full logical reference; `definition` is the complete [intended-recipients0 definition](delivery-policy.md#an-invitation-is-not-yet-an-encryption-identity) with that same root. The actual publishing author must be the definition’s creator. A scope cannot be created by an answer, reaction, withdrawal, edit, indexed reply or recipient-resolution control. A message, attachment-message or rich-message creates it only with empty replyTo. Question, service-question and independently authorized hosted-holder-observation may create a scope under their own operation rules; a holder observation does not authenticate its holder.

An existing scope selection has exactly `kind` and `root`. `kind` is `"existing"`; `root` selects an independently accepted scope definition in the same conversation, from its creator’s accepted root or the [configuration3 own-device setup ledger](paired-configuration.md#transfer-asynchronous-scope-metadata). The metadata path does not supply that root’s human message or reserve its authored identity. It cannot equal this record’s own reference or name a reference-only scope alias. A missing accepted scope definition keeps the scope dependency pending. When an eligible own-device setup observation supplies that definition, absence of the original human root alone does not block a fresh message. A reply, quotation, answer or other source-dependent operation still needs its own independently accepted target/content and remains pending if that evidence is missing. A rejected/conflicted definition cannot be replaced by a sender-supplied roster or subject match.

The presentation members are:

| Member | Requirement |
| --- | --- |
| `subject` | The existing protected subject scalar/control-character rules. |
| `authoredAt` | The existing empty-or-canonical-uint64-seconds string; it supplies no trusted creation time or ordering. |
| `authorSlot` | One slot in the selected scope, independently bound to this authored principal. |
| `from` | One canonical personal mailbox, with the author’s independently eligible source-account association. It is not a relay route. |
| `to` | Ordered array of distinct slot IDs in the selected scope. |
| `cc` | Ordered array of distinct slot IDs in the selected scope, disjoint from to. |
| `addresses` | Slot-sorted array of exact slot/mailbox objects, covering each to/cc slot once, with no other entries. |

The intended slots for this contribution are exactly authorSlot plus the union of to and cc. An author may deliberately address their own slot in one role, as with self-addressed mail. Other slots in the scope are not recipients of this contribution. Preserve the selected roles and address spellings; do not make a principal-level To/Cc union that loses which selected mailbox was copied. Independently selected aliases of one principal can remain distinct addressed slots while native membership still deduplicates that principal. The retained envelope4/5 principal-role arrays are not an additional field set in this record.

Each address entry has exactly `slot` and `mailbox`. Slot is one of the role-selected IDs; mailbox is the author’s canonical personal destination for this contribution. Exact duplicate recipient mailboxes across to/cc are invalid. This array does not change the scope’s frozen principal expectations or resolve an unknown slot. A different address for a bound slot must independently associate with that same principal under current policy before release. Until creator-authorized resolution is available, a merely chosen alternate mailbox supplies no principal and no release eligibility.

The scope’s mailbox is its original invitation claim, not a permanent routing address for every future message. This per-message addresses array preserves the actual authored To/Cc choices while the stable slots preserve who is intended. A new message can address the same verified principal through another eligible personal alias without inventing a participant or changing the scope’s resolution authority. A late copy of an already frozen message retains its original chosen mailbox; a different personal-address choice requires new authorized composition, not an edited retry. Opaque route substitution remains under its separate privacy contract.

The [alias-choice example](examples/async-alias-reply-authored.json) retains Bob’s slot and logical reply relationship while selecting bob@work.example for this new message. Its [delivery envelope](examples/async-alias-reply-delivery.json) preserves those exact authored bytes. This unsigned example supplies no current mailbox-association proof and cannot itself authorize release to that alias.

The scope’s mailbox claims remain immutable. From can name another independently eligible personal sending mailbox of the same author, but it cannot change the author slot’s principal or borrow another account’s source association. Rendering, quoting or reopening the record does not resolve a new route.

Slot reply intent has the same four kinds and applicability as the [reply-intent contract](reply-intent.md#exact-reply-intent-record), with version exactly `"1"`. For discussion, the exact members are version, kind, participants and privateReplies. Participants are distinct ASCII-sorted slot IDs, include authorSlot and are a subset of this record’s intended slots; privateReplies is a JSON boolean. Private, none and not-applicable each contain only version and kind. Recipient-resolution admits only not-applicable. A slot record is not principal-based reply-intent0, and no parser may reinterpret one version as the other.

For a discussion continuation, require the same exact scope root as the accepted source and an intended-slot set equal to that source’s declared discussion slots. The current author must be independently bound to an included author slot. This comparison is over the complete intended set, not whichever recipients have already obtained decryption setup. Missing setup for another slot does not prevent an otherwise eligible ready delivery. A private response creates its separate independently scoped root; it does not retain a transmitted group parent.

:::

::: {.details summary="Actual secured-delivery envelope6"}

Envelope6 is a distinct strict JSON object with exactly eight required members. It has no operation, presentation or replyIntent member at its outer level. Its decoded size is at most 8,388,608 octets and its maximum container depth is32. The larger wrapper allowance accommodates the authored record’s base64 expansion and explicit recipient mapping; it does not enlarge the authored-record or resource allowances. These are draft engineering bounds, not user-prescribed quotas or a guarantee against temporary resource exhaustion. Older envelope parsers keep their original limits and schemas.

| Member | Requirement |
| --- | --- |
| `version` | String `"6"`. |
| `purpose` | String `"contribution-delivery"`. |
| `event` | Fresh nonzero ObjectId for this secured delivery; an exact prepared retry retains it. This is not the authored event ID. |
| `conversation` | Exactly the authored record’s conversation and the accepted native context’s conversation. |
| `principal` | Exactly the authored record’s principal and the independently authenticated native publishing principal. |
| `audience` | Nonempty, distinct, ASCII-sorted array of principal strings, including the author; its set equals the actual authenticated native principal audience. |
| `slots` | Nonempty array of exact slot/principal mappings, uniquely sorted by slot ID in ascending ASCII order. |
| `authored` | Canonical padded base64 of the complete original authored-record UTF-8 octets, with no whitespace or alternative alphabet. |

Every slot mapping has exactly `slot` and `principal`, both strings under their owning grammars. The selected authorSlot must be present and map to this publishing principal. Every listed slot must be an intended slot of this authored contribution; no merely historical scope slot, private recipient or outside participant is admitted. The deduplicated set of mapping principals must equal audience exactly. Several selected slots may map to one principal. Actual devices, credentials and recipient setup still come from independently accepted native admission, not this array.

A slot mapping must match its accepted expected principal or creator resolution, with current identity, address-association, protection and disclosure checks. An accepted root delivery from the scope creator can supply the explicit first resolution of its own previously unresolved slots through this mapping, under the [creator-resolution transaction](delivery-policy.md#an-invitation-is-not-yet-an-encryption-identity). Another author’s delivery cannot. Unlisted intended slots are outside this actual delivery; their absence is neither deletion from the discussion nor proof of their readiness or global outcome.

Enforce the encoded authored length bound before base64 allocation, then its decoded one-mebibyte bound and full strict parsing. Require canonical encoding, exact original bytes and complete schema; do not repair malformed UTF-8, duplicate fields or a truncated record. A wrapper cannot split one authored record across events, include another root object, or obtain effects from a successfully decoded prefix.

The native sender authenticates the complete wrapper and complete carrier-bound original authored bytes. Compare actual epoch credentials, accepted device-to-principal authority, full native context and exact audience under the completed successor binding. A valid Bob sender cannot publish Alice’s authored record. A current Alice device can prepare another delivery of identical retained Alice content through its own independently eligible admission and pending-send authority; it does not inherit another device’s stream or outbox.

The delivery namespace is separately typed as publishing principal plus delivery event; the authored namespace is principal plus authored event. A delivery ID cannot be used as an operation target or logical parent. Changing the actual audience, slot map, native preparation, resources/carrier preparation or publishing device requires a fresh delivery identity and independent release decision while retaining eligible identical authored bytes. Retrying a frozen preparation retains its original delivery ID, bytes, dependencies and uncertainty. It does not repeat already successful recipient work.

Retain delivery identity with the original accepted native sender/context and protected preparation provenance. Different valid delivery bindings under one delivery identity are a delivery conflict, not permission to choose a later preparation. Independently authenticated unequal authored bytes under one authored identity are an authored-message conflict. Equal authored content received through another valid delivery remains one message; delivery conflict alone cannot rewrite it or manufacture undo of a historical external effect. The [two-ledger receiving algorithm](event-identifiers.md#keep-delivery-identity-separate-from-message-identity) defines equality, independent authored conflict processing and the limits of delivery/outcome correlation; no delivery-key collision hides an otherwise validated authored variant.

:::

::: {.details summary="Operation references, resources and acceptance order"}

Inside the authored record, each operation uses its existing exact field inventory. Every enclosing-event self-reference and every source, question, answer replacement, reaction/withdrawal target, edit root/predecessor and hosted-observation target that formerly used EventReference instead uses the exact logical reference to an authored record. The names remain principal, conversation and event; they never name envelope6’s delivery event. Choice, resource and chunk identifiers remain local to their owning authored operation. Deferred general-form operations are not enabled.

The recipient-resolution operation is the exact additional control body defined by the scope chapter. It belongs to the same scope it names, authenticates as its creator and has not-applicable reply intent. Its required operation selection and inert carrier projection are defined by the [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement).

Apply the owning operation’s same-author, same-conversation, target-kind, replacement, source-policy and deliberate-action checks to independently accepted logical records. Discussion equality uses complete intended slots as above. Actual release still requires a native audience exactly accounted for by the selected delivery map. For source-derived content within one scope, an automatic audience-subset check compares the explicitly selected intended slot sets; actual release still requires each delivered slot’s accepted creator binding and current eligibility. Across different scopes, require independently accepted principal bindings for every slot needed by that comparison and the owning explicit disclosure permission. Unknown bindings leave that cross-scope comparison unavailable; matching mailbox text or an arbitrary discovered principal cannot satisfy it. This does not authorize forwarding the complete original or activating its controls in a new scope. No current per-copy operation graph may be reused by substituting the delivery event as a logical reference.

A question’s and service descriptor’s self-reference names the logical question. Every delivery therefore refers to the same question, not one question per ready cohort. Service submission identifiers, credentials, replacement/status rules and uncertainty remain separate. Replaying the question through a new delivery cannot authorize a new HTTP submission. A hosted observation remains authored by its actual observer and attributed to a grant holder under its owning contract.

Resource commitments and roles are in the original authored operation. Their identity is the authored record’s complete logical reference plus manifest-local resource ID. The [mime-suite-v2 binding](suite-profile.md#asynchronous-protected-agreement) resolves that exact logical resource scope in the same selected compound object; an outer Message-ID or delivery event cannot rename it. Transfer encoding or fresh encryption may differ across a newly authorized preparation, but complete decoded resource bytes must retain the original length/digest. Missing/bad resources retain their owning unavailable-resource outcomes; a matching digest never grants access to another message’s file.

First validate the authenticated native/carrier candidate and strict wrapper, then the complete original authored record, scope/creator bindings, actual map and operation. Missing evidence needed to establish a valid scope or actual map remains a durable acceptance dependency; retain source bytes and independently established native authorship without reserving an accepted logical namespace. An otherwise accepted complete contribution whose primary parent, quotation source or interaction target has not arrived instead retains its logical identity under the owning operation’s pending-relationship/effect rules. Missing target evidence cannot invent an edge, verified source claim or active control; an incomplete required HTML/index map is still held under its own acceptance contract. Once its required scope/map acceptance succeeds, atomically commit authored namespace/provenance, per-delivery evidence and the effect or pending target dependency under the [assembly algorithm](delivery-policy.md#one-message-several-deliveries).

For a private-copy context, validate every scope-definition slot before encryption: expected contains exactly one principal from the retained originator/recipient pair, the creator belongs to that pair, and all bindings/resolutions/current personal-address associations remain within it. An unknown or third-person scope slot cannot hide in a private delivery merely because it is absent from the actual map. Outside-pair resolution is invalid, not private membership expansion. Receiver validation repeats this isolation; it cannot undo a source’s earlier disclosure.

Private/Bcc copies have their own authored root, scope, logical IDs and resources where required. Do not reuse the visible authored record merely to gain common-message deduplication. A separately authorized ordinary/hosted projection preserves its actual exposure status; neither a logical identifier nor later encryption undoes that disclosure.

:::
