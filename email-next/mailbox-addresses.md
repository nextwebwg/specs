---
title: Mailbox addresses and internationalized email
order: 10.12
blurb: internationalized addresses · exact identity · quoted local parts · SMTPUTF8
sectionNav: true
---

# Mailbox addresses and internationalized email

Email/2 supports internationalized mailbox names and quoted local parts. It uses one precise spelling for addresses in signed records, account links, encrypted personal addresses and association keys. That spelling identifies a mailbox claim; it does not establish ownership or authorize delivery.

> [!ex] Preserve the person’s address
> `用户@example.org` remains that address. It is not transliterated into an ASCII username. `"user@desk"@example.org` is also valid: the first `@` belongs to the quoted local part, and `example.org` is the provider domain.
>
> `"alice"@EXAMPLE.ORG` becomes `alice@example.org` when the client constructs a new record. Those redundant quotes and domain case do not identify another mailbox. Received signed records already need the canonical spelling; clients do not rewrite their signed bytes.

The [protected conversation agreement](suite-profile.md) selects this contract for assertion8 and its dependent invitation/roster, contribution and provider records. It is part of the same unpublished Email/2 specification, not an optional internationalization module. Earlier experiment encodings retain their narrower input rules and do not establish support for the current agreement.

## Keep local identity separate from domain lookup

The local part preserves its exact Unicode scalar sequence and case after SMTP quoting is decoded. Do not normalize it to NFC, case-fold it, remove dots or tags, apply IDNA to it, or infer an alias from a provider convention. For example, composed `é` and `e` followed by a combining acute accent remain different mailbox claims unless the account provider separately authorizes both addresses. Unicode similarity is not equality.

The domain uses lowercase ASCII DNS labels, with valid IDNA A-labels where needed. Trusted input construction can convert a valid NFC U-label such as `bücher` to `xn--bcher-kva` under the selected [Unicode17 IDNA rules](audits/idna-unicode-review.md). It applies no compatibility mapping, alternate-dot mapping or Unicode case-folding. Domain conversion never changes the local part. A missing coherent IDNA validator means unavailable validation, not acceptance of something merely shaped like an A-label.

For a received record, validate the complete bare mailbox spelling and compare its canonical UTF-8 bytes exactly. Never repair a received spelling before signature, conflict, audience or association checks. Preserve the original signed bytes as evidence. Equivalent user/header input can be canonicalized only by the separate trusted construction procedure below.

## Read and display addresses safely

A header parser first extracts one actual mailbox from header syntax; display names, comments and angle brackets are not part of the Email/2 address value. Decode valid SMTP quoting before constructing its canonical form. Preserve the original header and parser provenance. Encoded display names, Reply-To, a forwarded From or a visually matching label do not supply account authority.

Display addresses as isolated text, never markup or an automatically opened URL. Address text cannot alter surrounding writing direction. Make C1 controls (`U+0080–U+009F`), `U+061C`, `U+200E–U+200F`, `U+202A–U+202E` and `U+2066–U+2069` visibly identifiable by code point in displayed address labels and accessible text; keep their actual values unchanged in the underlying address. Provide inspection of the exact local part and A-label domain when displaying a friendlier Unicode domain. A contact name is chosen by the accepted principal/contact association, not visual resemblance of an address.

Valid UTF-8 syntax is not a guarantee that an address is safe-looking, assigned or deliverable. The distinction matters because [SMTPUTF8 extends the grammar](https://www.rfc-editor.org/rfc/rfc6531.html#section-3.3) to non-ASCII scalars; silently deleting invisible characters would change the address rather than validate it.

::: {.details summary="Construction, canonical wire spelling and equality"}

### Construct a new bare address

This procedure receives a bare mailbox already extracted from trusted user input or a header parser. It is not a replacement for parsing a complete RFC5322 header or `mailto` URI.

1. Require well-formed UTF-8/Unicode scalars. Parse `Local-part "@" Domain` under RFC5321 as extended by RFC6531; an `@` inside a quoted local part is not the separator. No obsolete route, comment, display name, address literal, URI scheme, surrounding whitespace or trailing domain root dot enters this value.
2. An unquoted local part is a nonempty dot-string: nonempty atoms separated by literal ASCII dots; each atom contains RFC5322 ASCII `atext` or RFC6531 `UTF8-non-ascii`. In a quoted local part, accept SMTP qtext plus non-ASCII scalars and ASCII quoted pairs only. Decode each quoted pair to its following character. ASCII controls, DEL and unescaped quote/backslash are not qtext. Quoted empty local parts retain their required quotes.
3. Preserve the decoded local scalar sequence exactly. If it can be represented as an unquoted dot-string, use it without quotes. Otherwise surround it with ASCII double quotes, escaping only literal double quotes and backslashes with a single ASCII backslash. This gives the minimal quoting required for that exact sequence. It implements the [SMTP requirement to treat equivalent quoted forms consistently](https://www.rfc-editor.org/rfc/rfc5321.html#section-4.1.2).
4. Lowercase ASCII domain letters. Convert valid NFC IDNA U-label input under the selected coherent Unicode17 implementation to validated canonical lowercase A-labels, including whole-domain contextual/bidirectional checks. No transitional processing or compatibility mapping. Ordinary labels use NR-LDH syntax; the reserved hyphens in positions3–4 are permitted only for a validated `xn--` label. Check each label and its A/U round trip. A received wire domain must already be canonical ASCII.
5. Check octet bounds, not character counts: local-part spelling at most64 UTF-8 octets; each ASCII domain label1–63 octets; DNS wire name at most255 including length octets and root; textual domain at most253; canonical bare mailbox plus surrounding SMTP path brackets at most256 octets. Input SMTP local-part spelling must also satisfy its64-octet bound. These transport bounds do not enlarge any tighter containing-record limit.
6. Join canonical local spelling, one ASCII `@` and the canonical domain. Store that value and original input provenance separately. A signed-wire validator performs the same checks but requires the input already equal this result; it never substitutes transformed bytes into a signature.

A local-part may contain characters that are meaningful to a URL, JSON string or header. Each containing format applies its own escaping; do not percent-decode, JSON-decode twice or infer a different mailbox from that escaping. The JSON string’s decoded value is the address; its surrounding payload bytes remain signature input.

### Equality and account binding

Canonical address equality is exact UTF-8 byte equality. Equivalent quoted spellings have already been resolved during trusted construction; case differences or normalization differences in local parts have not. An account provider validates the selected mailbox against its own authoritative membership, using this same representation. A provider may authorize several distinct aliases, but that authorization neither merges their local association histories nor proves that another provider treats them as equivalent.

Every domain-selection operation parses the mailbox using this contract. It must not split at the first `@`, inspect a display name or use an arbitrary string suffix. This applies to source-account domain delegation, recipient bootstrap, relay administration and direct SMTP routing. Private-copy and duplicate-recipient checks compare the canonical values, not their visual presentation.

:::

## Delivery through older infrastructure

Implementations of the current Email/2 agreement support these addresses in their own protocol records. SMTP carriage separately obeys [SMTPUTF8 negotiation](https://www.rfc-editor.org/rfc/rfc6531.html#section-3.2). A non-ASCII outer envelope local part or internationalized header at any MIME level requires SMTPUTF8; use the MAIL parameter and other applicable SMTP extension rules. A-label domains alone do not require it. Inspect the final outgoing representation rather than assuming that every HTML or UTF-8 body needs this extension.

Encrypted personal addresses are content inside protection. If all actual outer envelope addresses and MIME headers are ASCII and the protected object is carried through the defined base64 MIME format, internationalized addresses inside that object do not by themselves require SMTPUTF8. An already authorized ASCII relay route can therefore carry such a protected message through older infrastructure. This is address masking under its own approval and exposure policy, not conversion of the personal address.

If the selected actual SMTP path cannot carry the required representation, hold or report the transport failure under the existing delivery policy. A hop advertising SMTPUTF8 does not promise support at every downstream hop. Do not transliterate, remove characters, invent an ASCII alias, expose encrypted personal addresses or fall back to plaintext. A deliberately selected alternative account or authorized relay needs the same current identity, audience, route and release checks as any other send. An uncertain earlier submission retains its immutable retry identity; changing routes cannot pretend that the earlier attempt never happened.

## Acceptance boundary

The [address component](evidence/README.md#mailbox-address-spelling) tests exact Unicode/quoted spelling, octet limits and configured Unicode17 IDNA conversion and validation. Metadata and bootstrap components use this address parser, including quoted `@` routing. These are not complete header parsing, internationalized account login, SMTPUTF8 submission or mailbox-ownership evidence.

A complete client must additionally exercise internationalized and quoted addresses through assertion8 signatures, ordinary-header extraction, account and association selection, initial8/roster5 admission, private-copy checks, encrypted MIME, actual direct SMTPUTF8 and ASCII relay delivery, retry/restart and safe accessible display. Invalid/noncanonical input must leave accepted identities and prepared sends intact. No earlier ASCII-only fixture establishes this coverage.
