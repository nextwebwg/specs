---
title: Registration and extension inventory
order: 17.3
blurb: draft names · registration templates · version boundaries
sectionNav: true
---

# Registration and extension inventory

Email/2 combines existing standards with new application formats. Those formats need recognizable names so independently built clients can agree on what they are receiving. A draft name is not an assigned standard, proof of support or permission to act.

This chapter identifies the proposed registrations and the names that remain local to the application. It supplies draft filing material without allocating identifiers or appointing a contact. The format-owning chapters remain authoritative for bytes, validation, authorization and failure behavior.

## Media types and retained experiments

:::: {.details summary="Media-type inventory and reusable registration templates"}

### Selected candidate names

All names in this table are unregistered draft candidates. Use requires explicit agreement on this draft; no claim of availability, reservation, filing or assignment follows. No parameters are defined, and none can select a version or weaken decoding. The owning contracts define exact JSON/binary size and depth limits and unknown-version behavior.

| Complete type name | Representation and owning contract | Intended use |
| --- | --- | --- |
| `application/vnd.threadlabs.email-next-event+json` | One contribution, including the selected envelope4, under [event encoding](event-encoding.md), [required suite](suite-profile.md) and [event registration](media-type-registration.md) | Event alternative inside the selected protected/compatible MIME binding |
| `application/vnd.threadlabs.email-next-discovery+json` | Exact signed assertion wrapper, version-selected by [passive discovery](passive-discovery.md) and the exact assertion8, assertion9 or selected assertion10 binding in the [suite](suite-profile.md) | Only explicitly permitted discovery carriage; not a reason to expose mailbox-bearing proofs in masked mail |
| `application/vnd.threadlabs.mail-event+json` | Exact envelope5 under the [reply-aware agreement](reply-intent.md#reply-aware-protected-agreement), or selected envelope6 under the [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) | Required event alternative selected by its exact authenticated carrier/context; versions are not aliases and MIME labeling cannot supply support |
| `application/vnd.threadlabs.mail-authored+json` | Complete original authored0 for the restricted [ordinary authored carriage](event-encoding.md#ordinary-authored-carriage) | Unprotected reaction/withdrawal candidate alternative; no native envelope, trusted namespace or structured-effect authority |
| `application/vnd.threadlabs.mail-control` | Exact sealed-control-v1 under the reply-aware agreement, including [setup1 responses](mailbox-setup.md#set-up-the-declared-reply-policy), or selected sealed2 controls, including [setup2 responses](mailbox-setup.md#set-up-an-asynchronous-delivery), under the asynchronous agreement | Fixed EML2CTL1, MAILCTL2 or separately offered [MAILDEL0 deletion control](deletion-controls.md) under its own exact binding; no trial parser, clear proof or generic encrypted-file interpretation |
| `application/vnd.threadlabs.mail-deletion-offer+json` | Exact signed receiving-offer0 under [deletion controls](deletion-controls.md) | Read-only metadata accompanying authorized human mail or an accepted protected attachment; no automatic response, identity installation or deletion effect |
| `application/vnd.threadlabs.mail-setup+json` | Exact signed request or decrypted response under [ordinary-mail setup](mailbox-setup.md) | Only the request has clear mail carriage; responses remain inside sealed-control |
| `application/vnd.email2.stream-control+json` | Exact selected source-control or recipient-update0/1/2 object under [ordinary streams](suite-profile.md#ordinary-protected-conversations) | Decrypted logical control inside the sealed carrier; no clear current-suite attachment |
| `application/vnd.email2.sealed-control` | Exact binary [sealed-control-v0](suite-profile.md#confidential-setup-and-control) | Retained conversation control and current separately selected identity/history carriage; not an alias for sealed-control-v1, an MLSMessage or a generic encrypted file |
| `application/vnd.email2.identity-bundle+json` | Exact bundle1 under [state1 identity lifecycle](identity-state.md#concurrent-administration-and-retirement) | Logical administration/public-evidence export only where independently authorized; automatic mail remains sealed |
| `application/vnd.email2.identity-repair-share+json` | Exact repair-share1 under that same lifecycle | Partial repair proof collection, never installation/approval merely by MIME type; authorized export or sealed administration |

The existing event template supplies its complete filing fields. For **each other selected row**, the following common fields and that row's type-specific values together form its draft template. This avoids duplicating operational schemas or implying that all JSON objects share one media type.

| Registration field | Draft value for each non-event selected row |
| --- | --- |
| Type name / subtype name | `application` / the exact text after `application/` in its row |
| Required parameters / optional parameters | N/A / N/A |
| Encoding considerations | Binary. JSON types contain one strict UTF-8 object without BOM; sealed-control contains its defined binary frame. MIME transport encoding is specified by its owning carrier, not by the subtype. |
| Security considerations | The owning contract's identity, authority, privacy, replay, resource and lifecycle requirements plus the type-specific analysis below. Recognition does not authorize installation, responses or execution. |
| Interoperability considerations | Version/schema, original-byte/signature and exact carrier agreement required. Unknown fields/versions and disallowed parameters cannot fall back to another parser or clear transport. Generic JSON validity is insufficient. |
| Published specification | This inventory row and its linked owning contract at the same frozen publication revision. A stable revision URI must be supplied when filing. |
| Applications that use this media type | Experimental Email/2 implementations and conformance tools; no deployed or independent support claimed. |
| Fragment identifier considerations | No additional semantics; JSON types follow applicable generic +json rules without selecting JSON Pointer. Binary sealed-control defines none. A fragment never authorizes an operation. |
| Deprecated alias names / magic numbers | N/A / N/A for JSON. The selected sealed-control row defines exact eight-octet magic `EML2CTL0`, `EML2CTL1`, `MAILCTL2` or independently offered `MAILDEL0`; none grants authentication or permits parser fallback. |
| File extensions / Macintosh file type codes | N/A / N/A |
| Person and email address for further information | Not nominated; an accountable contact and real address are required before filing. No personal address is invented by this draft. |
| Intended usage | LIMITED USE for explicitly agreed draft experiments. |
| Restrictions on usage | Exact row-specific purpose and carrier only; not arbitrary JSON, MLS or a generic automatic-response format; the mail-setup row has only its explicit bounded response semantics. |
| Author | Email/2 draft editors; responsible authors to be identified in the filing. |
| Change controller | Proposed responsible project maintainer, subject to actual appointment and registration review; no IETF/NextWebWG authority is claimed. |
| Provisional registration | N/A for these vendor-tree requests. |

Discovery exposes capability and association metadata; its signatures do not establish mailbox ownership or guarantee current remote state. Source/update controls depend on current account authority, actual native transitions and immutable receiving promises. Deletion offers disclose a mailbox/device relationship and promise only a dedicated receiving key; they cannot reuse an assertion control key or establish mailbox ownership. Sealed-control depends on the selected HPKE/signature/recipient construction and secret custody; decryption alone authorizes no inner effect. Identity bundles and partial shares contain sensitive relationship evidence, may carry conflicting branches and cannot repin a known identity or grant administration without full lifecycle validation. All parsers enforce their owning bounds before expensive work. No media-type declaration initiates a fetch, credential lookup, control response or human-message effect.

These are draft templates under the [media-registration rules](audits/media-registration.md), not registration requests already sent. Controller/contact appointment and stable publication are filing prerequisites; registry review/acceptance is external.

### Historical fixture names, not current clear-mail formats

| Retained experimental name | Exact disposition |
| --- | --- |
| `application/vnd.email-next.mls-invitation+json` | Earlier targeted invitation MIME fixture; its [invitation contract](mls-invitations.md) retains its recorded version-specific meaning |
| `application/vnd.email-next.mls-membership-invitation+json` | Earlier established-invitation fixture; selected by its explicit MIME adapter, not a generic current-suite carrier |
| `application/vnd.email-next.mls-transition+json` | Earlier designated-transition fixture; selected by its explicit adapter, not current ordinary or managed sealed control |

These names remain documented for reproduction, not proposed for filing in this current bundle. They are not aliases for the current candidates listed above. Current sealed-control transport does not activate a clear old fixture after decryption/parse failure. The example-only `application/vnd.example+json` in negative tests is not an Email/2 proposal.

Existing `application/json`, `application/octet-stream`, MIME multipart/text/image types and registered `message/mls` retain their own semantics. An octet-stream fixture is not automatically `message/mls`, and sealed-control is not an MLS wire-format registration.

::::

## Relay proof header

:::: {.details summary="Draft mail-header registration template"}

Recipient masking selects the experimental `Email2-Route-Proof` field defined by the [route-use contract](relay-routes.md#prove-a-delivery-without-exposing-personal-identities). This is a mail-header candidate, not an application-local string or an assigned field. The following is draft submission material under [RFC3864’s message-header template](https://datatracker.ietf.org/doc/html/rfc3864#section-4.2.2), for the [IANA Message Headers registry](https://www.iana.org/assignments/message-headers).

| Template field | Draft value |
| --- | --- |
| Header field name | `Email2-Route-Proof`; field-name comparison follows the mail header’s ASCII case-insensitive rules |
| Applicable protocol | Mail |
| Status | Experimental candidate; provisional submission proposed, not submitted or registered |
| Author/change controller | Responsible Email/2 editor and contact address must be nominated before filing; none is appointed here |
| Specification document | The exact route-use contract and this inventory at one stable published revision, to be supplied with a filing |
| Related information | One outer field only when the selected recipient-masking route requires it. Its canonical-base64 signed wrapper, permitted folding, complete size limits and strict parsing are defined by the owner. No additional field parameters or automatic actions are introduced. |

Recognition of the field cannot authorize a route. Verify its original signed bytes, current route/source/account authority, exact outer-message/carrier commitment and replay state before admission. Duplicated or malformed fields cannot be repaired into an accepted proof. The route key is independently scoped; neither the field nor its signature establishes the inner author’s identity. Do not insert personal mailboxes, global principal identifiers, bearer credentials or unrelated audience metadata into this outer field. Actual relay/header/trace privacy still needs its complete acceptance evidence.

::::

## Domain discovery locations

:::: {.details summary="Well-known URI draft registrations"}

Use these as three separate draft registrations under [RFC8615](https://www.rfc-editor.org/rfc/rfc8615.html#section-3.1). The common fields and each row's purpose/reference form the request. They register suffixes, not the operator-selected API paths returned by discovery.

| URI suffix | Purpose and specification |
| --- | --- |
| `mail-provider` | Mailbox-domain delegation of account-management service; [provider discovery](provider-discovery.md#keep-the-domain-and-service-authorities-distinct) and its exact domain/transport/publication rules |
| `mail-setup` | Domain delegation of content-free recipient setup; [bootstrap discovery](bootstrap.md) with its separate account/pair/recipient authority and abuse controls |
| `mail-relay` | Delegation of a selected provider/independent relay service; [relay discovery](relay-routes.md#discover-a-relay-service), declared roles and current route/account authority |

For each: **Change controller:** proposed responsible Email/2 project maintainer, nomination required before filing. **Specification documents:** the linked owning chapter and this inventory at the same stable revision, URI to be fixed when published. **Status requested:** provisional. **Related information:** canonical HTTPS, exact selected domain, no redirect/ambient credentials, bounded no-store JSON, separate purpose/publication high-water state and current authority as defined by that chapter. This is not a claim of provisional registration already granted.

Registration does not validate a particular domain, account, delegation or operator. A client must still apply the owning transport, source-domain, account, anti-rollback, private-network and abuse rules. The existing `oauth-authorization-server` location is reused through its standard binding; no new suffix is requested for it. Operator-defined API prefixes and the registered native client's exact loopback callback path are not additional well-known names.

::::

## MLS application-context extension

:::: {.details summary="MLS Extension Types draft request and private-use boundary"}

The [MLS Extension Types registry](https://www.iana.org/assignments/mls#mls-extension-types) uses Specification Required. The draft request follows [RFC9420 §17.3](https://www.rfc-editor.org/rfc/rfc9420.html#section-17.3):

| Field | Draft request |
| --- | --- |
| Value | To be assigned through the registry; no public number claimed |
| Name | `mail_application_context` |
| Message(s) | `GC` — GroupContext extension, not KeyPackage/LeafNode extension data |
| Recommended | N — experimental application binding; this does not ask IANA to recommend deployment or certify its security |
| Reference | Frozen [security-profile context](security-profile.md#authenticated-conversation-context) and the selected [context8](suite-profile.md#context-and-signed-receiving-agreement) or [context9](reply-intent.md#reply-aware-protected-agreement) or selected [context10](suite-profile.md#asynchronous-protected-agreement) agreement, revision URI required before filing |

Extension data is the exact UTF-8 JSON application-context bytes defined by the selected context version, not reconstructed JSON or a digest placeholder. The original suite selects context8 and the separately negotiated [reply-aware agreement](reply-intent.md#reply-aware-protected-agreement) selects context9. The selected [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) adds context10, its own assertion/admission/control versions and mime-suite-v2. Their exact data and admission rules remain distinct; older versions retain their explicit agreed experiment meaning. Exactly one selected context extension is required. It is listed in RequiredCapabilities and advertised as supported by the applicable creator/joiner capabilities; that advertisement does not place the context data in a KeyPackage or prove its application semantics. Validate full context/group/roster/authority agreement and exact original bytes before use.

The local experiment's `0xff00` is private use within the reserved range, not a public allocation or a globally unique Email/2 identifier. Unrelated experiments may collide. Isolated agreement must pin the exact meaning/version; a public deployment needs the actual assigned value and updated signed capability/admission bindings. Do not rewrite an existing GroupContext, signature or checkpoint to replace the number. A transition to a registered code point requires fresh independently admitted context under the suite's migration boundary, unless a later complete authenticated migration contract explicitly specifies otherwise.

The selected suite reuses the existing MLS cipher suite, BasicCredential, proposal/wire-format and required-capabilities constructions. It requests no new cipher-suite, credential, proposal or MLS wire-format code point. Application signature domains use their explicit application framing, not new MLS SignWithLabel/EncryptWithLabel/exporter label assignments.

::::

## Application-local names and extension policy

The draft introduces application identifiers rather than new registries for the following:

- Enp/end prefixes, EventReferences, JSON `purpose`/`version` strings, framing magic, signature domains and typed local outcomes use their exact owning grammars. They are not URI-scheme, mail-header or SMTP-command registrations.
- `email2-conversation-v0`, `mime-suite-v0`, source/quorum/control formats, presentation profiles and assertion operation/feature combinations are selected only by their authenticated receiving agreements. A familiar name or media type cannot supply missing tuple support. The successor `mail-conversation-v1`/`mime-suite-v1`, reply-intent0, assertion9/context9, mailbox-setup-v1, mail-provider-control-v1, mail-provider-grants-v1, bootstrap1 and security-configuration-v2/pairing-setup2 are application-local agreements/versions. The selected asynchronous mail-conversation-v2/mime-suite-v2, assertion10/context10, descriptor/control/grant/bootstrap/setup2, security-configuration-v3, own-setup-v0 and its restricted scope-configuration-v0 are likewise application-local bindings. They reuse the existing mail-provider/mail-setup locations and version-neutral scopes; none allocates another well-known suffix, OAuth parameter, mail header or registry.
- OAuth permission scopes use the version-neutral `mail` namespace. Their exact resource-local names are listed below; one resource cannot accept another resource’s tokens.
- Reply Microdata uses the exact `ReplyV0`/`PartV0` identifier URIs in [reply content](reply-content.md#microdata-vocabulary). They identify vocabulary without fetching it or claiming Schema.org/HTML registry adoption. Changing their host/spelling requires a new explicitly negotiated binding; old signed examples are not silently aliased.
- Resource `cid:` names and reserved `.invalid` example domains remain scoped identifiers/examples; they are not DNS service registrations, automatic retrieval locations or new URI schemes.

These scope names do not allocate global OAuth parameters:

| Resource | Permission scopes |
| --- | --- |
| Service actions | `mail.service.link`, `mail.service.status`, `mail.service.submit` |
| Provider control | `mail.provider.link`, `mail.provider.manage` |
| Relay | `mail.relay.link`, `mail.relay.manage`, `mail.relay.submit` |
| Automatic setup | `mail.setup.link`, `mail.setup.request`, `mail.setup.respond` |
| Hosted access | `mail.hosted.create`, `mail.hosted.link`, `mail.hosted.read`, `mail.hosted.revoke` |

No new SMTP extension, IMAP/JMAP capability, TLS/ALPN identifier, HTTP field, MIME parameter, HTML attribute, CSS property, DNS record type or service-label registration is selected by this initial bundle. The selected relay-proof mail header is listed separately above. Provider APIs use existing HTTP/JSON and their independently selected paths. Any future feature requiring a registered slot must add its full owning contract and registration entry rather than hiding allocation in a string constant or calling it an optional module.

Unknown names/versions have no guessed compatibility. Preserve input and its unsupported/pending outcome under the owning contract; do not sniff a different parser, widen a scope or send a fallback/control response merely to discover support.

The successor mail-event and mail-control candidates retain the common templates above. Their security considerations additionally include explicit reply audience/permission, immutable draft/action dependencies, current identity/account/route checks, exact new signature/HPKE domains, version separation and original descriptor/attempt correlation. The names cannot make a no-replies policy enforceable in a legacy client or turn a candidate proof into provider authorization. Both require the same unappointed filing contact/controller and frozen reference obligations as the earlier candidates.

## Before public filing or an interoperability claim

The selected mail-conversation-v2 binding adds no new media type or well-known suffix: its authored0/envelope6, assertion10/context10, new admission/control versions and sealed2/mime-suite-v2 are application-local encodings under the candidates above. Its complete automatic-acquisition and lifecycle implementation and joined acceptance remain unproven; these registry rows are not permission to advertise that complete implementation or file a request. The application-context request name is the unassigned mail_application_context label; its name does not alter the existing private-use numeric value or any signed GroupContext.

The internal work is to freeze exact names, contexts and version/unknown handling, maintain these templates and validate example/code agreement against them. Filing additionally needs an accountable contact/controller, a stable referenced revision and the registry's review. Public assignment and independent implementation/security evidence remain separate external outcomes. This chapter neither sends a request nor authorizes adoption under an unassigned code point.
