---
title: JMAP sharing audit
sectionNav: true
---

# JMAP sharing audit

The complete base text of [RFC9670](https://www.rfc-editor.org/rfc/rfc9670.html), including all property definitions, methods, examples, registry templates, references and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. The [core JMAP base audit](jmap-core.md) is recorded separately; dependency and live registry closure remain unfinished.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Defines a reusable sharing model, not the specific data or permission granularity and not an encryption protocol. |
| 1.1 | Notational Conventions | Core JMAP types and abbreviated example conventions apply; examples are not standalone requests. |
| 1.2 | Terminology | Capitalized Principal and ShareNotification are JMAP data types, not Email/2 cryptographic identities. |
| 1.3 | Data Model Overview | Principals represent people, groups or resources and may own zero or more accounts; directory management is out of scope. |
| 1.4 | Subscribing to Shared Data | Permission differs from subscription; Session omits unsubscribed non-owned accounts and their state-change events. Absence is not revocation evidence. |
| 1.5 | Addition to the Capabilities Object | Two capability URIs have distinct session/account placement. |
| 1.5.1 | urn:ietf:params:jmap:principals | Principals capability enables methods; currentUserPrincipalId may be null and is account-scoped. |
| 1.5.2 | urn:ietf:params:jmap:principals:owner | Owner capability appears only on accounts and links a principal via its containing account; bare IDs are not global identities. |
| 2 | Principals | Server-set immutable IDs coexist with mutable presentation data and nullable email/accounts; names and email claims do not authenticate endpoint keys. |
| 2.1 | Principal/get | Standard get semantics inherited; see the separate core JMAP audit. |
| 2.2 | Principal/changes | External directories may always return cannotCalculateChanges; clients need resynchronization rather than invented deltas. |
| 2.3 | Principal/set | Unauthorized mutations fail forbidden; permitted self-editable names/descriptions must not become trusted identity evidence. |
| 2.4 | Principal/query | Standard query semantics inherited. |
| 2.4.1 | Filtering | All conditions combine; email/name/text use substring matching, unsuitable for exact identity binding. |
| 2.5 | Principal/queryChanges | Query changes may be unavailable; inability to calculate changes is not absence of changes. |
| 3 | ShareNotifications | Server-created sharing notifications may be omitted for groups, coalesced, expired or evicted. They are not a complete membership audit log. |
| 3.1 | ShareNotification/get | Standard get semantics for stored notifications. |
| 3.2 | ShareNotification/changes | Standard changes semantics do not restore omitted historical notifications. |
| 3.3 | ShareNotification/set | Only destroy is allowed; create/update fail forbidden. Dismissal is not permission revocation. |
| 3.4 | ShareNotification/query | Standard notification query semantics inherited. |
| 3.4.1 | Filtering | After is inclusive, before exclusive; object type/account filters require identical values and all conditions match. |
| 3.4.2 | Sorting | Created must be sortable, but creation time is not cryptographic group epoch ordering. |
| 3.5 | ShareNotification/queryChanges | Standard queryChanges semantics inherited. |
| 4 | Framework for Shared Data | Shareable types define subscription, current rights and sharing map; owner's rights are implicit and owner must not appear in shareWith. |
| 4.1 | Example | Full to-do example reviewed; illustrative rights are not Email/2 rights. Example mayAdmin wording about myRights differs from its shareWith mutation description; do not copy it as an authorization schema. |
| 5 | Internationalization Considerations | Servers may transform permitted directory strings with returned changes or reject them; this does not permit rewriting authenticated Email/2 event bytes. |
| 6 | Security Considerations | Core JMAP security considerations apply; endpoint cryptographic trust remains separately required. |
| 6.1 | Spoofing | Editable names and Unicode lookalikes can trick users into sharing; display equality is not identity equality. |
| 6.2 | Unnoticed Sharing | A brief account compromise can create persistent sharing; membership authorization must not be inferred from existing mailbox access. |
| 6.3 | Denial of Service | Notification flooding, eviction and coalescing tradeoffs reviewed; no notification is not proof of unchanged rights. |
| 6.4 | Unauthorized Principals | Principal creation is controlled to prevent unwanted sharing and notification spam; this is a directory policy rather than federated key verification. |
| 7 | IANA Considerations | Four registry templates reviewed; current registry verification remains separate. |
| 7.1 | JMAP Capability Registration for "principals" | Registers principals capability. |
| 7.2 | JMAP Capability Registration for "principals:owner" | Registers principals:owner capability with account-only use defined earlier. |
| 7.3 | JMAP Data Type Registration for "Principal" | Principal type permits state-change use and no blob references. |
| 7.4 | JMAP Data Type Registration for "ShareNotification" | ShareNotification type permits state-change use and no blob references. |
| 8 | References | Complete references and author end matter reviewed. |
| 8.1 | Normative References | JMAP core, message syntax and requirement-language dependencies remain separately scoped. |
| 8.2 | Informative References | JMAP registry, timezone database and PRECIS references do not define Email/2 identity comparison. |

## Provider integration boundary

JMAP sharing can support account discovery, recipient selection and a user-visible sharing interface. Preserve the server/account/Principal identity context and independently establish the Email/2 identity binding. Substring email searches and editable names cannot establish that binding.

Subscription is a preference, not authorization. Notification history is intentionally incomplete: coalescing, eviction, expiration and group-notification suppression are permitted. An Email/2 provider adapter must fetch authoritative current permissions when needed and validate cryptographic membership independently. A notification cannot add a device to an encrypted audience, and dismissing it cannot remove one.

JMAP's implicit account-owner rights also differ from Email/2's explicit author-inclusive audience set. An adapter must translate through a specified mapping rather than treating shareWith keys as the complete encryption audience. The illustrative to-do model is not an Email/2 access-control schema.


The [transport adapter contract](../mailbox-integration.md#optional-blob-and-sharing-capabilities) incorporates these extension boundaries alongside the core protocol. This documents the mapping; it does not establish a tested provider implementation.
