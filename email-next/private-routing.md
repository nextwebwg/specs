---
title: Private addressing through provider relays
order: 6.1
blurb: shared outer sender · opaque recipient routes · authenticated conversation display
sectionNav: true
---

# Private addressing through provider relays

A protected email can carry a provider's shared relay address on the outside while keeping the conversation's author and audience inside encryption. The recipient's client displays the authenticated author and contact names after acceptance. It does not display the relay as the person, and it does not rewrite the retained source email to pretend that its headers were protected.

> [!ex] What travels between providers
> Alice sends through her provider's authorized `relay@sender.example`. The destination is an opaque delivery alias at Bob's provider. The outer message has a generic subject and no personal To/Cc list. After decrypting and accepting the contribution, Bob's client displays Alice and the protected subject. Reply uses the conversation's authorized routes, not the relay's From address.

> [!note] Part of Email/2; joined relay implementation unfinished
> The independent Sender masking and Recipient masking modules define the proposed outer projection and release/privacy requirements. It builds on the protected application and transport carrier; it is not a replacement encryption scheme. The [encrypted personal-address record](private-address-presentation.md) is part of the required Email/2 conversation agreement; it is not a separate optional variant. [Relay route issuance and use](relay-routes.md) defines account links, source permissions, inbox-provider issuance, delivery proofs, replay handling and withdrawal. Component evidence is local and configured; no public relay deployment or integrated SMTP privacy test is claimed.

## Protect the author and the destination separately

A shared outer From hides the sender's personal address from that field. It does not encrypt the SMTP recipient. Recipient-address privacy additionally requires an opaque routing alias supplied by the recipient's provider. The SMTP envelope still names that alias so the receiving provider can deliver it.

The provider domain, relay infrastructure, destination provider, message size and timing remain visible. The sender's provider knows its submitting account; the recipient's provider knows its alias-to-account mapping. Setup/control traffic and both providers together may reveal the relationship. A unique custom domain can itself identify a person, so a common provider domain offers a larger sharing group than a personal domain. This is address minimization, not anonymity from providers or a traffic-analysis defense.

The current [authored0 presentation](event-encoding.md#asynchronous-authored-records-and-deliveries) keeps the subject, author date, personal From/To/Cc and intended mailbox slots inside encryption. Envelope6 separately names the actual delivery’s slot-to-principal mappings and native audience; other intended recipients may still be pending. The [personal-address contract](private-address-presentation.md) defines address validation and display assurance. A local contact lookup does not supply a missing authenticated address record. Retained envelope3 protects subject and principal roles but has no personal mailbox addresses; retained envelope4 adds its own exact address record. Those older schemas are not the current slot-based record. Complete current suite admission and private-route integration remain unimplemented.

## Compose personal addresses; deliver through aliases

The composer continues to show the person's selected sending account and intended personal To/Cc addresses. The recipient’s normal inbox provider assigns and renews temporary delivery aliases under its account routing policy. Normal account connection establishes trust in that service; no recipient device approves individual aliases. The sending transport adapter validates the service’s issuance, current account/service authority, exact peer/conversation scope and lifetime before use. An independent receiving relay is an explicitly selected alternative, not an extra account required for the normal case.

Before submission, preserve the personal From/To/Cc values inside encryption and substitute only the authorized transport addresses outside. The protected personal-address record must identify the author and each intended To/Cc mailbox slot, agree with the authored scope and roles, and exclude other private-copy recipients. Each actual delivery’s independently validated mappings bind its selected slots to authorized principals; an unresolved intended slot is not a guessed principal or an extra native member. Retained principal-based address records keep their own exact audience-equality checks. Its authenticated association evidence must determine whether a mailbox can be shown as verified, unverified or conflicting; an encrypted self-asserted address is not proof of ownership. The [personal-address profile](private-address-presentation.md) defines syntax, duplicates, role binding, exact negotiation, assurance and failure behavior for the initial supported spelling. Complete receiving and relay integration must pass before advertisement. When a setup exchange creates routing permission, retain its [exact source and provider issuance operations](relay-routes.md#exact-route-issuance-inspection-and-immutable-retries); a restart cannot allocate a fresh alias merely because the result was lost.

After acceptance, the client displays those authenticated inner values and accepted contact labels. The user need not edit, copy or remember the delivery alias. Viewing source still shows the actual relay envelope and headers. The client does not overwrite them with a fabricated original.

Temporary aliases remain transport internals. The application keeps a stable logical destination for the person/account/conversation; its adapter resolves or renews eligible routes before freezing each new delivery. Normal UI does not show alias expiry as an expired contact, ask for alias edits or replace a personal address. Historical reading and replies remain independent of old alias liveness. A generic SMTP adapter still retains exact physical addresses/proofs for audit and immutable retries. Renewal failure is a delivery pending/failure outcome, never an automatic identity change.

## Relay providers and accountability

A relay provider is a service authorized by an account holder to originate masked outer messages, receive scoped alias deliveries, or both. The normal case is the existing Email/2 inbox provider. A separately selected receiving relay is an explicit alternative. Service selection and delegation must be authenticated; a URL or alias in an unsolicited message cannot install a relay provider.

The initial independent receiving-relay contract stores an encrypted mailbox and provides authenticated retrieval itself. It does not forward to a personal SMTP recipient. Forwarding exposes that address on the onward hop; even an opaque forwarding chain requires a separately complete per-hop authorization/privacy contract before support. The [route contract](relay-routes.md) defines the selected direct-retrieval boundary.

The service binds route administration and outbound submission to authenticated accounts and authorized devices. An account means an accountable service account, not a mandatory government-identity check. Recipient grants restrict which peers may use a route. Domain-level SPF/DKIM success alone is insufficient to distinguish two users of the same provider. The exact route-use proof must enforce that distinction without publishing the sender's personal address or stable global identity in an outer header.

Recipients must be able to revoke a route and block further requests from the associated source account/peer under provider policy. Services need replay and delivery deduplication, bounded abuse handling and protection against an abusive account simply allocating another alias to bypass that block. Alias possession or forwarding must not create an open relay. These controls mitigate abuse; they do not promise that account creation or identity changes can never evade enforcement. Ciphertext-only relays cannot inspect encrypted content as if it were plaintext; any user-submitted content report requires deliberate disclosure.

[Apple's relay services](audits/relay-aliasing.md) provide prior art for scoped aliases, authorized senders, masked replies and revocation. Their documented email authentication mechanisms do not supply the cross-provider route-grant or encrypted address binding required here.

## When the addresses change

The swap is automatic transport projection, not an address-book edit or a different address the person must learn. Sender and recipient masking are independent [Email/2 modules](modules.md). The ordinary personal addresses remain the draft's semantic addresses throughout the following sequence.

1. **Compose.** Retain the selected personal sending account, To/Cc and deliberate private recipients in private draft state. Show those personal addresses and accepted contact names. Never replace a composer recipient with a relay alias merely because setup found one.
2. **Resolve delivery routing.** Use a retained valid route or obtain a new route directly from the recipient’s authorized inbox service. Validate the expected recipient identity independently, then the provider’s original service association/certificate, active account incarnation, exact scope, expiry and route-key permission. An alias string alone is only a candidate. The service can issue and renew aliases while the recipient device is offline, without per-alias device approval. A sender relay still needs its own account/source authority. Keep the human message private while required facts are missing.
3. **Choose each protection independently.** Resolve the sender's effective policy and current evidence for content encryption, sender masking, recipient masking and verification. Prefer available authorized upgrades within that policy. Required but unavailable protection holds the delivery. A remembered permission may allow an encrypted copy with public SMTP addresses; it must never be represented as fully masked. Ordinary/hosted fallback remains the separate delivery-policy decision.
4. **Freeze the personal presentation.** Build the exact required inner From/To/Cc record from the selected personal addresses and associated principals. Validate every role and audience, including private-copy exclusions. Save the account/association generations, selected application and route/evidence dependencies with the immutable send intent. Do not substitute an opaque route into the inner personal-address record.
5. **Encrypt, then construct the outside.** Produce the protected application and carrier bytes first. At the authorized outgoing origination boundary, construct a fresh outer message. When sender masking was selected, use the authorized shared outer From and opaque MAIL FROM bounce. When recipient masking was selected, use its authorized alias as SMTP RCPT TO. Use the fixed empty outer To and no outer Cc/Bcc for a fully masked copy, under the projection below. The actual personal addresses remain inside encryption. Never send a personal-address message first and attempt to scrub it after submission.
6. **Recheck and release.** Immediately before the serialized local release point, recheck identity, audience, policy, association generations, current route grants and exact prepared dependencies. If they changed, hold for reevaluation. The visible destination remains the intended person; the delivery worker submits only the exact selected outer envelope/bytes. Store actual masking and disclosure outcomes per copy rather than deriving them from the product's capabilities.
7. **Receive and accept.** Store the received outer source as transport evidence. Decrypt, authenticate and complete application/address acceptance. Then show the inner personal addresses and principal-based contact labels. The shared relay is available in transport details; it does not become the visible author. Unavailable, invalid or unsupported evidence stays provisional/held and cannot borrow a familiar name.
8. **Reply.** Start a new contribution from the displayed conversation principals and the person's selected replying account. Resolve current personal associations and routes again. Neither the outer relay From nor an inner address string alone is reply authority. Exact retries retain their frozen addresses, ciphertext and route identity; new route selection follows the replacement/conflict rules.

An authorized sender provider may perform the fresh origination on behalf of the client, or an authorized client may prepare that provider's permitted outer projection. The submitting account must be authenticated to that service in either case. If the provider originates the outer wire, the preparation/release record must bind the exact encrypted payload and authorized projection request, and the provider must retain its exact resulting outer bytes for retries. Do not claim client-side control of final trace headers that the service adds later.

### Partial provider adoption

| Usable capabilities for an encrypted copy | Selected outer source | Selected SMTP destination | Actual address-privacy state |
| --- | --- | --- | --- |
| No masking service | Personal sender under ordinary sending authorization | Personal recipient under ordinary routing | Content encrypted; personal routing addresses remain exposed |
| Sender masking only | Shared authorized relay and opaque bounce | Personal recipient | Sender masked at the tested originating boundary; recipient not masked |
| Recipient masking only | Personal sender under ordinary sending authorization | Authorized opaque alias | Recipient masked on the authorized route; sender not masked |
| Both | Shared authorized relay and opaque bounce | Authorized opaque alias | Both personal addresses masked within the tested route boundary |

In every row, the encrypted inner record keeps the same intended personal From/To/Cc. The fully masked projection table below applies to the final row. A partial row must accurately preserve the ordinary source/destination exposure it still needs; it must not claim the fully masked table's guarantees. A route can impose additional source-account or submission constraints, which must also be satisfied. No row can route via an arbitrary alias just because the corresponding capability exists.

A later provider upgrade can select a better row for the next eligible unsubmitted delivery without asking the person to edit addresses. Loss of support follows the independently remembered requirements: hold if masking was required, or use an already permitted less-private route with an accurate state. Do not change a prepared uncertain retry or claim that a later upgrade erased earlier exposure.

## Establish authority before using an address

The sender provider authorizes one shared relay mailbox and its opaque bounce/message-ID domains through authenticated account setup. `relay@<domain>` is an example, not a reserved or universally usable address. Clients cannot manufacture it from MX, a provider brand or an incoming message. The provider confirms that the authenticated submitting account may use this relay mode and binds that permission to the selected device/account and lifetime.

The recipient provider issues an unguessable alias for a declared routing scope, such as one selected peer and conversation/device set. Use at least 128 bits of independent random entropy; do not derive the local part from a personal address, principal, conversation ID or reversible encoding of those values. A new alias for an unrelated peer/private copy avoids an unnecessary stable correlation identifier. A stable alias still links uses within its own scope; encryption does not hide that correlation.

Alias possession is routing information, not membership, decryption authority or proof that a device belongs to a person. A finite service association established during normal inbox connection authorizes the provider’s routing role. The provider issues individual routes under private account policy and independently proves its control of the alias, intended peer/conversation scope and active account incarnation. No device signature approves the alias. Endpoint identity, mailbox associations, native membership and application acceptance remain separate. Forwarding an alias cannot authorize another audience or expose history.

The [route-grant contract](relay-routes.md) specifies issuer/delegation and account-incarnation checks, scope, lifetimes, per-peer/device authorization, immutable issuance/retry records, opaque bounce routing, withdrawal, alias non-reassignment and explicit service migration. Its credentials have explicit routing scope; the [queue-management grant](provider-grants.md) does not implicitly authorize sending mail, allocating aliases or changing SMTP From. The relay module reuses browser authorization through its own exact scopes and namespace; queue access is not inherited. No client may treat a configured test route as evidence that these public mechanisms exist.

## Release with minimal outer metadata

A fully masked send requires all three: usable protected application state, authorized sender relay service and authorized recipient aliases for that exact actual delivery. Other intended recipients still pending setup are not routed by this delivery; their later deliveries need their own current route evidence under the frozen progression policy. Partial adoption follows the independent module selection above. Apply the existing current-identity, audience, device, group, association, disclosure and serialized release checks. Route grants and provider capability/expiry checks become additional immutable delivery dependencies. A changed or revoked alias cannot be silently substituted into an already released attempt.

When the effective policy permits automatic masking upgrades, select the full projection when both sides' routing permissions exist, or the supported partial projection otherwise. If privacy is required and they are unavailable, retain the draft/send and explain the missing provider support. An ordinary personal-address envelope or content-only encrypted route is a separately authorized alternative with visible metadata exposure, not a successful private-addressing send. Existing content-encryption profiles remain recognizable under their own exact contracts; they must not acquire an address-privacy claim retroactively.

The provider originates a fresh outer relay message around the exact prepared encrypted carrier. It must not forward the original submission headers as a way to construct it. This is a new outer origination at an authorized relay, not permission for an arbitrary intermediary to delete or rewrite another relay's Received trace. Internal submission/account evidence remains in protected operational storage under its retention policy, rather than becoming an outward personal-address header.

::: {.details summary="Outer message projection and SMTP envelope"}

The projection applies only after the crypto engine produced the exact protected carrier bytes. It is not an encryption test or permission to put plaintext into an opaque attachment. The final MIME binding of each contribution/invitation/control carrier retains its own rules; no configured carrier fixture establishes this complete private-routing binding or registered message/mls compatibility.

| Field or channel | Required private-addressing behavior |
| --- | --- |
| SMTP MAIL FROM | Provider-owned per-delivery opaque bounce address; no personal local part or reversible account ID. The provider privately maps failures to the submitting account. |
| SMTP RCPT TO | Recipient-provider-authorized opaque alias for this exact route. Isolate each private/recipient delivery where grouping could reveal addresses or relationships. |
| From | Exactly the authorized shared relay mailbox, with no personal display name. A common provider relay is preferred to a per-user pseudonym where the goal is hiding individual account identity. |
| To | The fixed empty group `undisclosed-recipients:;`. No personal address and no list of other aliases. Actual recipients remain in the SMTP envelope and protected application audience. |
| Cc, Bcc, Sender, Reply-To | Omitted. A legacy reply to the shared relay never becomes a conversation reply or acquires the private routing map. |
| Subject | Fixed `Encrypted conversation`. No protected subject, message excerpt or contact names. |
| Date | Outer provider-origination time. The protected author-stated date remains separate. Timing remains visible; this is not a batching/delay protocol. |
| Message-ID | Independent opaque random value at a provider-authorized domain, stable for the prepared delivery's exact retries. Do not derive it from an author address or authenticated conversation/event ID. |
| In-Reply-To, References | Omitted. Reply relationships remain inside the authenticated contribution; no public cross-message chain is generated to reconstruct the conversation. |
| MIME labels and readable notification | Fixed non-personal carrier labels and generic notification only; no original filenames, subjects, quotations, recipient roles or body excerpts. Resources stay inside the selected encrypted carrier. |
| DKIM/SPF/DMARC | Normal provider authorization and alignment for the actual outer relay identity. A pass authenticates that relay's transport role, not the inner author. The client never spoofs an unauthorized shared From. |
| Received, Return-Path, Authentication-Results, ARC, X-* and diagnostics | Do not leak personal submission addresses, authenticated usernames, original From/To, personal device names, private audience lists or original message IDs through traces added by this origination. Downstream relays may add operational metadata; deployments must test it, not infer privacy from the initial headers. |
| DSN/ORCPT/ENVID, forwarding and failure reports | Use independently authorized opaque routing identifiers. Do not reintroduce personal recipients or send plaintext/ciphertext originals to a generic relay mailbox. The SMTP/reporting contracts still govern actual delivery outcomes. |

SMTP routing credentials, alias administration tokens and source-account mappings are not attached to the message. A relay email address is not a bearer token for automatic actions. Shared relay reception needs an explicit provider policy: ordinary mail arriving there cannot ask the provider to look up an encrypted audience or forward a reply on the original author's behalf.

Retain the complete prepared wire bytes, opaque envelope, route/relay grant references and expected provider/account incarnations. An exact retry uses those bytes and that authorized scope, under a new current release decision. If the old route expires or is revoked, hold the retry; it cannot refresh the route in place or imply that a previous uncertain delivery was recalled. Constructing a replacement route follows the contribution/delivery conflict rules and preserves earlier uncertainty.

:::

## Render the accepted conversation, not a guessed replacement

Before cryptographic and application acceptance, display the outer relay identity only as an untrusted transport observation. A valid relay-domain signature cannot promote an inner author. Unsupported or invalid protected content stays held; it cannot borrow a familiar contact name from an inner unverified From field.

After acceptance, derive the author from the authenticated MLS contribution and its currently/historically applicable identity binding. Use the protected subject, audience roles and reply target, with contact labels from accepted local associations. The expected difference between a shared relay From and the authenticated author does not warrant a spoof warning by itself. Missing author/association evidence still needs the owning pending/conflict/verification outcome. Do not suppress warnings for ordinary messages merely because they use a relay-looking address.

Reply resolves the authorized conversation participants and valid private routes. It never sends to outer From, Reply-To, Return-Path or an alias copied from an arbitrary forwarded message. Changing the replying account re-evaluates identity, group and relay/route authority. Legacy clients may show the generic relay and encrypted attachment; they cannot reconstruct the encrypted author and must not be promised a transparent personal-address experience.

A view can expose the original message and transport details for inspection. It must preserve which values were authenticated and which were observed. It must not claim that the absence of an address in the received copy proves that no earlier hop saw it.

## Why this differs from RFC 9788

[RFC9788 §3.1.1](https://www.rfc-editor.org/rfc/rfc9788.html#section-3.1.1) generally keeps the outer and protected From addr-spec equivalent, supporting existing anti-spoofing and compatibility behavior. Its [ambitious confidentiality discussion](https://www.rfc-editor.org/rfc/rfc9788.html#section-3.4.1) allows stronger policies with explicit applicability considerations. Header protection does not itself provide provider-issued delivery aliases or hide the SMTP envelope.

This profile makes the outer provider an explicitly authorized relay originator, while the existing managed MLS binding authenticates the conversation author separately. That separation is why the client can display the accepted principal instead of the shared relay. It is not a reinterpretation of S/MIME/PGP certificate-to-address validation and does not claim RFC9788 wire compatibility. The [legacy header-protection path](transport.md#default-header-confidentiality-for-protected-legacy-mail) retains its own rules.

## Evidence and adoption boundary

This chapter selects the proposed behavior and privacy boundary. The [personal-address component probe](private-address-presentation.md#acceptance-evidence-and-limits) exercises metadata validation and actual encrypted MIME carriage under configured context. The separate [route component](relay-routes.md#acceptance-obligations) adds actual signature/current-identity and durable local admission/block/replay evidence. There is no integrated private-addressing implementation or acceptance result; neither component establishes public issuance, actual opaque SMTP delivery or complete application acceptance.

A public claim additionally needs authenticated relay/route provisioning, cross-provider issuance and revocation, complete mailbox/submission trace inspection, DSN and bounce tests, forwarding/legacy behavior, alias rotation/reassignment, isolated private-copy delivery and exact retry after lost replies. Test that modifying the outer From cannot change the accepted author and that a missing/invalid inner authentication cannot display the protected contact. A metadata audit must include setup, drafts, logs and reports as well as the final message.
