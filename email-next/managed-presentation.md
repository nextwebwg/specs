---
title: Protected subjects and recipient roles
order: 8.2
blurb: authenticated labels · protected subjects · separate transport details
sectionNav: true
---

# Protected subjects and recipient roles

A protected conversation should display the subject the author actually sent. This experimental profile places the subject, author-stated date and To/Cc roles inside the authenticated, encrypted contribution. Changing the surrounding email cannot change those labels or redirect a reply.

> [!ex] A changed outer subject stays outside the conversation
> Alice sends “Confidential roadmap” to Bob. A mail gateway changes the outer Subject to “Urgent payment” and adds a different Reply-To. After accepting the protected contribution, Bob sees “Confidential roadmap” and Alice's authenticated identity. Replying uses the conversation's authorized recipients. The gateway's fields are available separately as unprotected transport details.

The protected subject is a label for this contribution. It does not rename the conversation or establish an order for its messages. The stated date remains the author's claim, even when authenticated.

## What the reader sees

After successful cryptographic, identity, membership and application acceptance, a client MUST use the protected subject and recipient roles for this profile. It MUST derive the author from the authenticated contribution principal. Contact names may decorate those identities; an outer From field cannot replace them.

A client MUST keep outer Subject, From, To, Cc, Date, Reply-To and threading fields distinct from authenticated conversation data. It MAY expose them in a clearly labeled transport-details view. Before acceptance, a provisional view MUST NOT present those fields as protected or enable a reply or action from them. Unsupported protected profiles remain held; they are not silently interpreted as a supported older profile.

Older managed profiles do not authenticate their outer subject or date. Clients MUST preserve that distinction when displaying older accepted contributions. An empty protected subject means no subject; it does not authorize borrowing an outer title.

## Recipients and replies

To and Cc contain principals, not mailbox addresses. They describe the author's recipient roles within the already authenticated audience. They do not grant mailbox ownership, create a new recipient or select an endpoint. Replies continue to use the [selected mailbox association](mailbox-association.md) and [release checks](transport.md).

A [private copy](private-copies.md) has its own audience and contribution. Its roles cannot mention recipients outside that audience. The same rule applies when several authorized devices belong to one principal: recipient roles describe the person or account, while device membership follows the group contract.

The [required Email/2 suite](suite-profile.md) additionally carries [encrypted personal mailbox addresses](private-address-presentation.md) under envelope4. This chapter's envelope3 describes the earlier subject/role component; it does not establish complete Email/2 conformance. [Opaque provider routes](private-routing.md) remain a separate delivery capability whose provisioning/use and integration are unfinished.

## Confidentiality and ordinary copies

Protected transport uses a generic outer subject. Implementations MUST NOT copy the protected subject into that field. SMTP addressing and other routing metadata remain visible to the transport; this profile does not conceal traffic relationships.

An explicitly authorized ordinary-email copy exposes its reviewed subject and body. The disclosure preview MUST include that subject. The existing [mixed-delivery policy](delivery-policy.md) applies: encryption of another copy cannot undo the ordinary copy's disclosure. This profile adds no automatic fallback permission.

:::: {.details summary="Exact experimental encoding and negotiation"}

### Contribution fields

Envelope version `3` retains the preceding contribution fields and requires exactly one additional `presentation` object. Its four members are mandatory; omission, null and unknown members are invalid.

| Member | Exact value |
| --- | --- |
| `subject` | Unicode scalar text, including the empty string. C0, DEL and C1 control characters are invalid. Preserve the original spelling; do not interpret HTML. |
| `authoredAt` | Empty string for no stated date, or canonical unsigned decimal epoch seconds from `0` through `18446744073709551615`. No sign, whitespace, leading zeroes or numeric JSON value. |
| `to` | Ordered array of distinct principal identifiers. |
| `cc` | Ordered array of distinct principal identifiers, disjoint from `to`. |

The set containing the authenticated author plus every To/Cc principal MUST equal the contribution's audience exactly. Audience validation and the private-copy roster constraints still apply. This binds the roles to the intended audience without copying arbitrary email address syntax into the protected payload.

The timestamp MUST remain an exact string through parsing and storage. A client unable to represent it as a calendar date displays an unavailable-date indication and retains the original seconds for inspection. It MUST NOT truncate, round, wrap or use the date as event ordering or authorization evidence.

### Negotiated profile

This branch uses context version `6`, assertion version `5`, contribution envelope `3` and the `mime-rich-v0` payload. Context `6` retains the exact ordinary/private-copy delivery object and ordering choices of context `5`. Each admitted device's exact signed tuple must cover the selected envelope, payload, operations and ordering. Older tuples do not imply support.

Initial invitation version `5` binds common roster version `2`; established invitation version `5` binds the resulting context `6`. These reuse the existing [initial roster](mls-invitations.md) and [established Welcome](group-conversations.md) admission and release rules, including exact signed member evidence, target package selection, immutable retries, current authority and selected routing. The signature domains are `email-next/passive-discovery/v5`, `email-next/mls-initial-roster/v2`, `email-next/mls-new-conversation-invitation/v5` and `email-next/mls-established-membership-invitation/v5`, each followed by the existing NUL separator and exact encoded payload. No old version changes meaning.

### Display boundary

The renderer consumes accepted retained contribution bytes and their authenticated context. It MUST NOT construct protected labels by parsing the transport headers. The reference experiment also binds the requested view to the exact accepted carrier and contribution record. It creates text nodes for labels and keeps transport observations in a separate disclosure.

::::

## Relationship to existing protected email

[RFC9787 §§5.1 and 9.3](https://www.rfc-editor.org/rfc/rfc9787.html#section-9.3) require RFC9788 header protection for the encrypted-email composition they describe. [RFC9788 §3.3](https://www.rfc-editor.org/rfc/rfc9788.html#section-3.3) protects the subject by default, and [§4.8.1](https://www.rfc-editor.org/rfc/rfc9788.html#section-4.8.1) bases automatic behavior on protected fields.

This managed profile follows those confidentiality and authenticated-display goals with semantic fields inside MLS. It deliberately does not carry arbitrary protected mail headers, `HP-Outer` or the RFC9788 MIME representation. Principal audiences and conversation replies already have their own authenticated authority, so copying mail Reply-To or threading fields would introduce a second, competing source. This is **not RFC9788 wire compatibility**. The [legacy protected-mail path](transport.md#default-header-confidentiality-for-protected-legacy-mail) retains that specification's rules.

## Experiment coverage

The local experiment joins signed discovery, initial admission, encrypted SMTP delivery, accepted display data and a protected reply. It checks changed outer From, Subject, Reply-To and References; generic outer subjects; exact retry binding; out-of-calendar dates; private-audience exclusions; explicit plaintext subject exposure; device addition followed by an established Welcome over SMTP; and automatic atomic recovery through a revoked member while preserving the exact delivery and presentation context. Browser checks exercise actual accepted fixture data, text-only labels, keyboard opening of transport details and provisional display.

These checks establish local behavior, not independent-client interoperability, deployed-provider compatibility or assistive-technology certification. The profile is a proposal; arbitrary legacy protected-header import and a general header-preserving gateway remain separate work.
