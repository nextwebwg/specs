---
title: Encrypted personal-address presentation
order: 8.3
blurb: required inner addresses · principal bindings · safe display
sectionNav: true
---

# Encrypted personal-address presentation

People compose to personal email addresses. Providers can deliver through aliases without exposing those addresses in the outer message. Email/2 keeps the personal From/To/Cc inside the encrypted authored contribution. Its actual delivery mappings bind selected mailbox slots to conversation principals; other intended slots can remain pending. A client displays the accepted inner information while retaining the actual transport source separately.

> [!ex] One person, two different addresses for different jobs
> Alice composes from `alice@sender.example` to `bob@recipient.example`. The encrypted contribution carries those personal addresses. Delivery uses a shared sender relay and Bob's separately authorized opaque route. Bob's client authenticates Alice's contribution before showing her name and personal address; replying resolves Alice's current route rather than copying the shared outer From.

> [!note] Required Email/2 behavior; implementation unfinished
> Personal addresses inside encryption are part of the [required protected Email/2 conversation contract](suite-profile.md). They are not a separate optional flavor of Email/2. This chapter owns the address schema and display rules; the suite chapter owns the exact receiving agreement. [Relay route provisioning and route-use authorization](relay-routes.md) have a proposed contract and local configured component evidence; joined public service/transport implementation remains unfinished. Component tests do not establish complete client or relay conformance.

The [current baseline](suite-profile.md#current-client-baseline) carries [per-message personal addresses](event-encoding.md#asynchronous-authored-records-and-deliveries) inside authored0: From plus slot-based To/Cc and exact slot/mailbox choices. Envelope6 separately binds actual native recipients. The envelope4/5 schema retained here has principal-based roles and remains exact; its mailbox association/display safeguards apply where the current binding incorporates them. An older address decoder alone does not establish current support.

## What the addresses mean

The inner From is the author's selected personal sending mailbox. In a private reply that author may be the original private recipient; the stable private-copy originator does not replace the current author or their From address. Inner To/Cc give the author’s selected mailbox spelling for each intended slot. Actual delivery mappings establish the independently validated principal for each delivered slot; a pending slot remains an author-stated address claim. They are authenticated author statements, not independent proof of mailbox ownership, provider routing instructions or a second source of conversation membership.

The sender must have an eligible current source-account association for From and an eligible selected mailbox-to-principal association for every To/Cc slot actually included in this secured delivery. Under current authored0, other intended slots can remain pending; their displayed addresses are frozen author claims, not proof of resolved identity or delivery. Earlier envelope4/5 requires its complete per-copy audience under its own binding. Apply the existing first-contact and verification policy. A changed association generation, principal, source account or route holds release for reevaluation. A valid signature over an arbitrary mailbox is insufficient. Address evidence and routing grants remain distinct dependencies.

The complete inner record is encrypted, including addresses for the sender and recipients. Do not copy the message's address-presentation record into an outer header, readable notification, filename, MIME parameter or provider control request. A separately required setup address follows its own control purpose and disclosure rules. Deliberately authored text can itself contain an address; the protocol does not claim to erase addresses people write. Setup services still learn the account/address needed for their control role.

## To, Cc and Bcc remain different

Email/2 preserves the roles people chose when composing. Putting people in one encrypted audience does not turn every recipient into a direct addressee or erase the distinction between To and Cc.

| Composer role | Protected meaning |
| --- | --- |
| To | A direct recipient, recorded in the authenticated To role and personal-address entries |
| Cc | A copied recipient, recorded separately in the authenticated Cc role and address entries; still an intended recipient with access to that contribution |
| Bcc | One independently protected [private copy](private-copies.md) per blind recipient, outside the visible copy's audience and membership |

To and Cc express addressing intent, not different encryption strength or a prohibition on replying. Both are visible to that copy's authorized audience. A Cc recipient must not be relabeled as To merely because the client presents a conversational view. Role selection alone does not authorize any button, service effect, membership change or future disclosure.

Bcc stays in the sender's private composition and delivery plan. It is not a shared Bcc array or a hidden cryptographic member. A blind recipient receives the sender–recipient private conversation, with its own event identities and protected address record; it does not inherit the visible conversation or its original To/Cc list. The private-copy context identifies the private relationship, so clients must not present that separately addressed copy as evidence that the person was an original visible To recipient. A reply stays within that private relationship unless the user deliberately shares with a new audience under the owning disclosure rules.

The existing [disclosure declaration](private-copies.md#declare-planned-sharing-without-naming-recipients) still records planned separate protected sharing generically, without blind-recipient names or counts. Blind addressing therefore does not promise that the existence of all additional sharing is hidden.

The client keeps recipient roles inspectable for the contribution being read and the draft being sent. Seeing names elsewhere in the conversation is not permission to add those people to a reply. Replying to the author and replying to the visible recipients are different audience choices; show the actual choice, preserve its To/Cc roles, and never add a blind recipient from private local delivery records. To/Cc alone do not establish a group-discussion or reply-routing contract. In particular, a Cc entry cannot silently become either a subscription to later messages or a restriction on replying. A private exchange follows the [separate audience and composer rules](client-behavior.md#private-exchanges-beside-a-group-discussion). The earlier envelope4 has no authenticated reply-mode field; the [current reply-intent record](reply-intent.md#exact-reply-intent-record) has its own schema and cannot be inserted as an optional presentation member. The retained [reply-aware protected agreement](reply-intent.md#reply-aware-protected-agreement) keeps its complete principal-based address record and version1 acquisition bindings. Current automatic acquisition uses the [version2 handoff](first-contact-setup.md#acquisition-for-independently-ready-deliveries), authored0 and envelope6; a complete implementation remains unproven.

## Exact address record

The retained contribution envelope `4` has the complete nine-member root inventory below, with `version: "4"`. Its presentation has `subject`, `authoredAt`, `to`, `cc` and the required `addresses` member. The complete presentation has five members; no optional extension container exists. Unknown, omitted or null members invalidate this representation.

:::: {.details summary="Retained envelope4 fields and principal-based addresses"}

This retained envelope has exactly these nine required root members. This table is the complete envelope4 field inventory; earlier envelope versions retain their own schemas and are not optional field sets. Common [strict encoding and byte/depth limits](event-encoding.md) apply. Omitted, null, duplicate or additional members are invalid.

| Member | Required value |
| --- | --- |
| `version` | Exactly `"4"`. |
| `purpose` | Exactly `"contribution"`. |
| `event` | Nonzero 32-lowercase-hex Event ObjectId, fresh for a new authored contribution; retain its exact representation on retry. |
| `conversation` | Nonzero ObjectId naming the actual accepted conversation context. A matching string alone grants no access. |
| `principal` | Nonzero `enp0` identifier of the independently authenticated author, not a claimed outer mailbox or display name. |
| `audience` | Nonempty array of distinct principal identifiers, including the author. Its set equals the actual protected principal audience. Array order has no membership meaning but remains part of the frozen bytes. |
| `operation` | Exactly one complete operation permitted by this retained agreement’s signed [application selection](suite-profile.md#module-agreement-and-common-operation-selection), under its owning schema and target/effect rules. Recognition by a dispatcher does not enable an operation outside that agreement. |
| `disclosures` | Required array, possibly empty, of the exact descriptors and order below. It states planned additional exposure, not successful delivery or authority for an external effect. |
| `presentation` | Exactly `subject`, `authoredAt`, `to`, `cc`, `addresses`, under the complete rules below. |

Disclosures retain the envelope2/3 contract: at most one exact `{kind:"separate-protected-copy"}` first, then at most one exact `{kind:"plaintext-email"}`, then unique exact `{kind:"provider-hosted",service,model:"bearer"}` entries sorted by canonical service origin. No other members, kinds or hosted models are admitted. The [service origin grammar](service-answers.md) and [copy/disclosure policy](private-copies.md) apply. Descriptors never contain recipient/copy counts, private identities, grant identifiers or access tokens. Empty disclosures cannot prove that a recipient will never forward content.

Presentation subject is a scalar-value string, including empty, with C0/DEL/C1 controls prohibited. AuthoredAt is empty or a canonical unsigned64 decimal epoch-second string; never a JSON number, rounded calendar value, ordering decision or authorization time. To/Cc are ordered distinct principal arrays, disjoint from one another. The author plus their union equals audience exactly; their address arrays below supply canonical personal mailbox spellings. Missing/malformed addresses do not select a transport-header fallback.

The envelope does **not** add a delivery or ordering member: those belong to the authenticated context8, including the stable private-copy roles and actual owner/witness agreement. A decoded envelope4 or envelope5 shape is still not proof of current identity, mailbox association, admission, resource/source binding or permission to execute its operation. Complete the current agreement and [ordered acceptance gates](rich-messages.md#accept-the-event-check-its-presentation-separately) before effects.

For these retained envelope4/5 agreements, the operation set is the protected core plus the selected Answers/Reactions/Corrections/Service actions/Hosted replies blocks. A selected service-question or hosted-holder-observation requires its complete owning binding. The current authored0/envelope6 agreement instead has the [fixed readable vocabulary and independent per-device interactions](suite-profile.md#asynchronous-protected-agreement). General forms and older hosted/service tuples cannot replace either selected agreement merely because their schemas exist elsewhere.

::::

`addresses` has exactly:

| Member | Required value |
| --- | --- |
| `from` | One personal mailbox under the spelling below; its principal is the envelope's authenticated author. |
| `to` | Ordered array of address entries. Each entry has exactly `principal` and `mailbox`. |
| `cc` | Ordered array of address entries with the same entry grammar. |

Each entry principal uses the existing nonzero `enp0` encoding. An array can be empty. For each role, take its entries in order and retain each principal's first occurrence; that result must equal the existing presentation's principal role array exactly. Several distinct mailboxes for one principal are permitted in one role. A principal cannot occur in both To and Cc, following envelope3. The author may also be a To/Cc recipient, including a self-addressed message.

Every exact recipient mailbox must occur only once across To/Cc. Across From and all entries, the same exact mailbox must never name different principals. From can also occur as an explicitly self-addressed recipient for the author. No addresses for an outside principal are admitted: author plus role principals must equal the authenticated contribution audience. Private-copy isolation applies to this record as well as the principal arrays; do not include another private copy's addresses.

### Mailbox spelling and compatibility

The required [mailbox-address contract](mailbox-addresses.md) supports internationalized and quoted local parts, minimal SMTP quoting, exact local Unicode/case preservation and canonical validated A-label domains. JSON strings carry that canonical bare address, not a complete header. No display name, comment, address literal, URI scheme or trailing domain dot enters this value. A validator missing the selected IDNA provider returns unavailable, not valid.

Compare canonical decoded address values exactly for role, duplicate and conflicting-principal checks. Trusted user/header input construction may canonicalize domain case and equivalent SMTP quoting before a new record is signed; a received record must already have that spelling. It cannot borrow identity through Unicode similarity, local normalization, dot/plus equivalence or forwarding rules. Unsupported actual SMTP carriage holds under the transport policy; it does not justify changing the personal address or sending plaintext.

### Example

Principal abbreviations below stand for their full valid `enp0` identifiers; they are explanatory placeholders, not wire values.

```json
{
  "subject": "Design review",
  "authoredAt": "",
  "to": ["<Bob principal>"],
  "cc": [],
  "addresses": {
    "from": "alice@sender.example",
    "to": [{"principal": "<Bob principal>", "mailbox": "bob@recipient.example"}],
    "cc": []
  }
}
```

## Part of the required conversation agreement

The [current suite](suite-profile.md#current-client-baseline) carries authored0 inside envelope6/mime-suite-v2, using its exact per-message slot/mailbox record and actual native delivery map. Earlier agreements carry envelope5/mime-suite-v1 or envelope4/mime-suite-v0 with their unchanged principal-based address schemas. Encrypted personal addresses are mandatory within that Encryption agreement. A device cannot advertise Encryption receiving support while omitting them. Internal format numbers identify the draft's wire encodings; they do not establish separate product editions or optional address-security tiers.

The event alternative carries the entire address record within the authenticated MLS application data. The media type stays the existing candidate event representation; that media type alone does not establish compatibility. Required operation dispatch, direct MIME structure, resource rules and projections remain in the suite contract. Addresses are presentation metadata, not a new body alternative or resource; there is no redundant inner RFC5322 header block to reconcile. Do not add address metadata automatically to text/HTML body projections.

Earlier exploratory implementations using envelope3 do not implement this required address contract. Their existing results remain component evidence with their actual scope. Do not rewrite retained experimental messages or count older receiving support as complete Email/2 support. The discussion draft has no deployed baseline that requires keeping this behavior in a second suite.

## Receive and display

Perform the following checks before exposing an accepted address presentation:

1. Authenticate and process MLS using the selected group and authorized sender device. Validate the exact required-suite application, membership, identity, audience, retained bytes and full operation under that agreement, including its MIME projections and resource obligations. Authentication alone is insufficient application acceptance.
2. Validate the exact selected authored0/envelope6 and complete personal-address record; compare the actual delivery audience and slot bindings with independently authenticated context evidence. Other intended slots retain their pending state. Validate per-message role/address coverage, current association for delivered slots and private-copy constraints. Older envelope4/5 is accepted only under its own complete agreement and principal-role equality rules. A malformed record cannot yield a partially accepted address list or interactive effect.
3. Resolve local mailbox associations independently. A matching association for the same principal can decorate the displayed mailbox with that association's actual assurance. No association means **author-stated address**; it does not install an association or mark ownership verified. An enabled association to a different principal means **address conflict**, retained visibly without reattributing the contribution. Local policy may require resolution before further sending.
4. Choose contact names and avatars by the authenticated principal and accepted local contact association. Never look up an inner claimed address and borrow another principal's familiar identity. An unverified first-contact association retains its unverified status. Keep sender-stated mailbox text separate from independently confirmed labels.
5. Reply to the accepted conversation principals under current account, association and route checks. Neither inner mailbox text nor outer From/Reply-To alone supplies a delivery route. Do not reply automatically, add audience members or disclose history during display.

A client can show an authenticated author's message while clearly reporting a conflicting mailbox claim; it cannot show the conflicting address as a verified replacement. Before complete acceptance, expose only provisional transport information and safe diagnostics, not a decrypted familiar contact as though application acceptance succeeded. Render mailbox text as text, never HTML or an automatically invoked URL.

Retain exact original event and MIME bytes, authenticated evidence and the address-assurance decision separately from mutable contact labels. Reopening history does not require a currently live alias, and route expiry does not retroactively erase an admitted contribution. Historical verification keeps its original scope; current account reassignment does not reattribute old messages.

## Acceptance evidence and limits

The [address-presentation experiment](evidence/README.md#encrypted-personal-address-presentation) checks strict address metadata, role/audience binding, configured-context dispatch and assurance outcomes. Its crypto case carries an actual MIME event inside MLS through loopback SMTP, checks sender/context binding and rejects ciphertext modification. This is a configured component probe, not required-suite admission, a complete operation/renderer implementation or a private relay service. Its SMTP fixture still uses configured personal envelope addresses and therefore provides no address-privacy evidence for transport.

Complete suite acceptance additionally requires its signed device agreement, initial and established admission, ordering/control transitions, all required operations/resources, restart and immutable retries. Complete private addressing also requires public route issuance/use/revocation, real opaque SMTP recipients/bounces, independent relay final-hop tests and source/header/log/DSN inspection. Those obligations cannot be satisfied by encrypting an address JSON fixture alone.


## Confidential setup proofs

The [sealed-control layer](suite-profile.md#confidential-setup-and-control) also encrypts invitations and key-update proofs that contain personal mailbox claims. Inner message-address protection alone is insufficient when those proofs are exposed elsewhere. Invitations, stream/admin/history controls and setup responses use their selected sealed carrier. The only clear automatic mail-setup exception is the explicitly enabled, content-free [initial mailbox request](mailbox-setup.md), which cannot satisfy required personal-address masking. Required masking additionally checks the actual sender/recipient route projection; a sealed-control failure never authorizes a clear replacement. Neither encryption success nor a relayed address substitutes for accepted identity, mailbox association or original owning-protocol validation.
