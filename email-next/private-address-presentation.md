---
title: Encrypted personal-address presentation
order: 8.3
blurb: required inner addresses · principal bindings · safe display
sectionNav: true
---

# Encrypted personal-address presentation

People compose to personal email addresses. Providers can deliver through aliases without exposing those addresses in the outer message. Email/2 keeps the personal From/To/Cc inside the encrypted contribution and binds each address to a conversation principal. A client displays the accepted inner information while retaining the actual transport source separately.

> [!ex] One person, two different addresses for different jobs
> Alice composes from `alice@sender.example` to `bob@recipient.example`. The encrypted contribution carries those personal addresses. Delivery uses a shared sender relay and Bob's separately authorized opaque route. Bob's client authenticates Alice's contribution before showing her name and personal address; replying resolves Alice's current route rather than copying the shared outer From.

> [!note] Required Email/2 behavior; implementation unfinished
> Personal addresses inside encryption are part of the [required protected Email/2 conversation contract](suite-profile.md). They are not a separate optional flavor of Email/2. This chapter owns the address schema and display rules; the suite chapter owns the exact receiving agreement. [Relay route provisioning and route-use authorization](relay-routes.md) have a proposed contract and local configured component evidence; joined public service/transport implementation remains unfinished. Component tests do not establish complete client or relay conformance.

## What the addresses mean

The inner From is the author's selected personal sending mailbox. Inner To/Cc give the author's selected mailbox spelling for the corresponding intended principal. They are authenticated author statements, not independent proof of mailbox ownership, provider routing instructions or a second source of conversation membership.

The sender must have an eligible current source-account association for From and an eligible selected mailbox-to-principal association for every intended To/Cc entry. Apply the existing first-contact and verification policy. A changed association generation, principal, source account or route holds release for reevaluation. A valid signature over an arbitrary mailbox is insufficient. Address evidence and routing grants remain distinct dependencies.

The complete inner record is encrypted, including addresses for the sender and recipients. Do not copy the message's address-presentation record into an outer header, readable notification, filename, MIME parameter or provider control request. A separately required setup address follows its own control purpose and disclosure rules. Deliberately authored text can itself contain an address; the protocol does not claim to erase addresses people write. Setup services still learn the account/address needed for their control role.

## Exact address record

Contribution envelope `4` has exactly the envelope3 members and their existing grammars, with `version: "4"`. Its presentation retains `subject`, `authoredAt`, `to` and `cc` and adds exactly one required `addresses` member. The complete presentation has five members; no optional extension container exists. Unknown, omitted or null members invalidate this representation.

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

The [required suite](suite-profile.md) carries envelope4 in `mime-suite-v0`, under its one exact signed application agreement. Encrypted personal addresses are mandatory within that Encryption agreement. A device cannot advertise Encryption receiving support while omitting them. Internal format numbers identify the draft's wire encodings; they do not establish separate product editions or optional address-security tiers.

The event alternative carries the entire address record within the authenticated MLS application data. The media type stays the existing candidate event representation; that media type alone does not establish compatibility. Required operation dispatch, direct MIME structure, resource rules and projections remain in the suite contract. Addresses are presentation metadata, not a new body alternative or resource; there is no redundant inner RFC5322 header block to reconcile. Do not add address metadata automatically to text/HTML body projections.

Earlier exploratory implementations using envelope3 do not implement this required address contract. Their existing results remain component evidence with their actual scope. Do not rewrite retained experimental messages or count older receiving support as complete Email/2 support. The discussion draft has no deployed baseline that requires keeping this behavior in a second suite.

## Receive and display

Perform the following checks before exposing an accepted address presentation:

1. Authenticate and process MLS using the selected group and authorized sender device. Validate the exact required-suite application, membership, identity, audience, retained bytes and full operation under that agreement, including its MIME projections and resource obligations. Authentication alone is insufficient application acceptance.
2. Validate envelope4 and the entire address record as one object. Require the author, conversation and complete audience to match the independently authenticated context. Validate role/address equality and private-copy constraints. A malformed record cannot yield a partially accepted address list or interactive effect.
3. Resolve local mailbox associations independently. A matching association for the same principal can decorate the displayed mailbox with that association's actual assurance. No association means **author-stated address**; it does not install an association or mark ownership verified. An enabled association to a different principal means **address conflict**, retained visibly without reattributing the contribution. Local policy may require resolution before further sending.
4. Choose contact names and avatars by the authenticated principal and accepted local contact association. Never look up an inner claimed address and borrow another principal's familiar identity. An unverified first-contact association retains its unverified status. Keep sender-stated mailbox text separate from independently confirmed labels.
5. Reply to the accepted conversation principals under current account, association and route checks. Neither inner mailbox text nor outer From/Reply-To alone supplies a delivery route. Do not reply automatically, add audience members or disclose history during display.

A client can show an authenticated author's message while clearly reporting a conflicting mailbox claim; it cannot show the conflicting address as a verified replacement. Before complete acceptance, expose only provisional transport information and safe diagnostics, not a decrypted familiar contact as though application acceptance succeeded. Render mailbox text as text, never HTML or an automatically invoked URL.

Retain exact original event and MIME bytes, authenticated evidence and the address-assurance decision separately from mutable contact labels. Reopening history does not require a currently live alias, and route expiry does not retroactively erase an admitted contribution. Historical verification keeps its original scope; current account reassignment does not reattribute old messages.

## Acceptance evidence and limits

The [address-presentation experiment](evidence/README.md#encrypted-personal-address-presentation) checks strict address metadata, role/audience binding, configured-context dispatch and assurance outcomes. Its crypto case carries an actual MIME event inside MLS through loopback SMTP, checks sender/context binding and rejects ciphertext modification. This is a configured component probe, not required-suite admission, a complete operation/renderer implementation or a private relay service. Its SMTP fixture still uses configured personal envelope addresses and therefore provides no address-privacy evidence for transport.

Complete suite acceptance additionally requires its signed device agreement, initial and established admission, ordering/control transitions, all required operations/resources, restart and immutable retries. Complete private addressing also requires public route issuance/use/revocation, real opaque SMTP recipients/bounces, independent relay final-hop tests and source/header/log/DSN inspection. Those obligations cannot be satisfied by encrypting an address JSON fixture alone.
