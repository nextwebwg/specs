---
title: Provider delivery outcomes
order: 6.01
blurb: provider observations · recipient outcomes · preserved uncertainty
sectionNav: true
---

# When delivery changes after sending

A provider can accept an email and discover later that it cannot deliver one copy. This optional service lets the sender's app retrieve that later result and show it beside the right recipient's delivery history.

> [!warn] Optional proposed capability
> This chapter proposes a configured provider service. Its identifiers are unallocated, and support is not part of the current protected-client baseline. The requirements apply only when this capability is adopted; complete implementation and independent evaluation remain required.

## What the sender experiences

1. **Send as usual.** The app retains exactly which copy it tried to send and to whom.
2. **Keep the handoff.** If the submission provider accepts responsibility, the app records that fact. Acceptance does not mean the recipient decrypted or read the message.
3. **Check the configured service.** An authorized delivery workflow can retrieve the provider's later observations. A query only reads status; it does not send another copy.
4. **Update the relevant history.** A later failure stays attached to its own recipient and delivery obligation. Another recipient's success remains independent.
5. **Keep uncertainty visible.** An unavailable service or missing result does not prove success, failure or lack of encryption support.

> [!ex] Bob's copy fails; Carol's does not
> Alice's provider accepts copies for Bob and Carol. A later result reports that Bob's delivery obligation failed. Alice's app keeps the earlier handoff and shows the later failure in Bob's delivery history. Carol's independent result remains intact. Nothing automatically resends or changes encryption.

> [!note] A provider's observation has a specific scope
> A list expansion and a later failure elsewhere can both be true. The app keeps observations about different custody obligations separate. It does not turn one branch's failure into a claim that every copy failed.

This first version requires deliberate account configuration and provider-side integration with the actual SMTP transaction. It does not trust an emailed status object, a familiar provider name or possession of a tracking token. Legacy delivery reports continue under their own rules.

> [!note] A service observation, not portable proof
> The result is attributed to the configured service. HTTPS does not make the provider truthful, and copied JSON is not independently verifiable proof. Ordinary legacy delivery reports continue under their existing validation and advisory rules.

## Use a service authorized for this account

The app uses a deliberately configured reporting connection for the sender’s own account. Setup permissions and other service credentials do not grant reporting access.

:::: {.details summary="Account registration, service authority and credential isolation"}

This first capability is configured alongside the sender's own SMTP submission account. It does not introduce DNS discovery, infer authority from From/MX/DKIM, or reuse a setup, relay-management or service-answer credential.

The application installs a trusted local registration with exactly these fields. Provisioning is an own-account operation; received mail cannot install it.

| Local field | Type and meaning |
| --- | --- |
| `profile` | Exact proposed literal `mail-outcomes-v0` |
| `origin` | Canonical HTTPS origin under the existing service-answer URI rules |
| `prefix` | Canonical absolute path prefix ending `/`, under those same path rules |
| `account` | Opaque service account identifier: 64 lowercase hexadecimal characters |
| `incarnation` | Opaque 64-lowercase-hex account-owner incarnation |
| `submissionAccount` | Existing local outgoing-account key |
| `submissionGeneration` | Current outgoing-account configuration generation, positive safe JSON integer |
| `credentialHandle` | Local secret-store reference; never transmitted as an identifier |
| `stages` | Nonempty duplicate-free array, in this order when present: `submission`, `relay`, `mailbox`, `list` |
| `retentionSeconds` | Positive safe integer; provider's promised minimum retention after accepting responsibility |
| `generation` | Positive local registration generation; changes to any authority/credential binding replace this registration |

The provider independently binds the bearer credential to this exact reporting account/incarnation, origin/prefix and **outcome-read-only** operation. This operation name is a proposed provisioned role, not a new OAuth scope. Credential provisioning and refresh use trusted configured-account integrations. This version defines no native-login endpoints. A mailbox password is not a reporting credential. Existing TLS/credential isolation rules apply; the client never sends this token to SMTP, another origin, another prefix or a peer.

The registration binds the same internal provider-owned account used to authenticate SMTP submission. The provider verifies that relationship through its authoritative account provisioning; matching public email strings are insufficient. Reassignment rotates incarnation and prevents the new owner from querying the old owner's submissions. Revocation and query authorization serialize with the provider's authoritative permission state. A disabled or uncertain local registration holds new requests. Local replacement may explicitly authorize inspection of retained older attempts only for the same original origin/prefix, service account/incarnation and outgoing-account association. Retain both old and new registration generations in that decision; credential renewal cannot silently select another provider or owner. A changed SMTP configuration does not rewrite the historical attempt binding.

`stages` limits what this service is authorized to report as **its own** observation. Submission concerns its authenticated incoming transaction; relay concerns its own onward delivery attempt; mailbox concerns a mailbox it actually serves; list concerns redistribution it actually performs. A relay cannot claim final mailbox arrival merely because another relay accepted responsibility. Forwarded DSNs or testimony from an independently operated downstream provider do not acquire this authority. Their separately authenticated/delegated reporting mechanism is outside this first capability.

::::

## Know which send the result describes

The provider and app bind a result to the actual submitted bytes and envelope. A fresh token identifies each SMTP attempt; it is never permission to inspect or send mail.

:::: {.details summary="Exact SMTP association, token lifetime and message commitment"}

A reporting-enabled attempt uses existing SMTP delivery status notification (DSN) negotiation and envelope identifier (ENVID) syntax. It requires the actual authenticated submission server to advertise DSN on that connection. This proposal allocates no EHLO keyword and changes no ordinary DSN message syntax.

Before opening the SMTP transaction, the client durably retains a fresh random 32-octet submission token, encoded as 64 lowercase hex characters. It uses that token as this attempt's ENVID. The retained record binds the token, reporting registration generation, outgoing-account generation, exact prepared message and envelope, original protection/permission, actual intended recipient subset and attempt identity. The token is correlation, never authorization. It is not a contribution ID, logical message ID or encryption key.

A new SMTP attempt uses a new token, even when reusing identical prepared content. An uncertain attempt is inspected under its original token; lookup never authorizes another attempt. The provider's account-scoped token namespace is shared with actual SMTP acceptance storage and is independent of HTTP query input. An outcome query cannot allocate or reserve a token.

For this configured capability, the provider reserves a token when accepting its authenticated MAIL command and refuses reuse in another SMTP transaction under that account/incarnation. A successful reservation is permanently nonreassignable within that account incarnation, across every authenticated application, restart, content-retention expiry and service restoration. The service retains a durable used-token tombstone after deleting detailed records and refuses the same token even for byte-identical content and envelope. This rule is an additional configured service constraint, not a claim that base DSN requires ENVID uniqueness. A refused/rejected/disconnected transaction keeps its actual outcome; reservation alone does not establish body release or handoff. The client never reuses a token, but safety does not depend on that client rule alone. Account incarnations are never reassigned to a new owner or recreated as a fresh empty token namespace.

::: {.details summary="Exact prepared-attempt commitment"}

The provider computes a commitment from the actual submission, not from values supplied by the outcome query. The client computes the same commitment from its retained preparation. Both use SHA256 over this binary sequence:

1. UTF8 bytes `mail/outcome-binding/v0`, followed by one NUL octet.
2. `LP(reversePath)`, where the empty byte string means null reverse-path.
3. `U32(recipientCount)`, followed by `LP(recipient)` for each actual attempted RCPT in order.
4. `LP(bodyMode)`, exactly ASCII `7bit`, `8bitmime` or `binarymime`.
5. `U64(messageOctets)`, then the 32 raw SHA256 octets of the exact prepared message.

`LP(x)` is four-octet unsigned big-endian byte length followed by exactly x. `U32` and `U64` are unsigned big-endian integers of those widths. Inputs exceeding an encoding width are unsupported; no truncation. The final commitment is encoded as 64 lowercase hex characters.

Addresses are the exact UTF8 addr-spec bytes emitted between SMTP path delimiters, without the delimiters, source routes or command parameters. Do not lowercase, expand aliases or normalize local parts. Ordinary SMTP address validation/serialization remains a separate prerequisite. The token is associated with the complete attempted RCPT vector, including rejected recipients; each recipient occurs at most once in this capability. A client requiring duplicate identical envelope recipients uses an ordinary reporting mode instead.

Message bytes exclude SMTP DATA dot stuffing and terminator, BDAT command framing and trace/authentication fields added by the server. They include the original prepared headers and final CRLF exactly as submitted. The provider captures this digest before modification. Body mode is the actual accepted BODY parameter, with absent BODY meaning 7bit. SMTPUTF8 and DSN parameters retain their actual negotiation evidence separately.

A transaction ending before the complete message is available has no complete prepared-attempt commitment. Its local SMTP evidence remains usable, but this HTTPS capability returns unavailable for that token rather than pretending to bind a partial body. This first profile does not solve reporting for an uncompleted SMTP transaction.

:::

If DSN is unavailable, this reporting capability is unavailable for that attempt. Existing submission policy decides whether ordinary SMTP may proceed; no protection downgrade or reporting-specific forced plaintext is permitted. The client records that no service-outcome binding was established.

The provider retains complete-message evidence and its final SMTP result atomically with the token's accepted responsibility record, or uses an equivalent durable recovery protocol. A lost final reply can therefore be reconciled by a retained service observation. A matching authenticated `accepted` observation can qualify local SMTP uncertainty as the provider's recorded acceptance; it cannot prove receipt by the intended endpoint. Missing state never proves nonacceptance.

::::

## Ask for an observation, without sending again

A read-only HTTPS query retrieves a bounded page of provider observations. A retry can reveal additional observations, but it cannot execute a delivery or action.

:::: {.details summary="Query and response schemas, HTTP rules, limits and errors"}

The only route is `POST prefix + observations`. It is a read-only query despite using POST: it cannot send mail, retry delivery, allocate a submission, change recipients, mark messages read or execute an interaction. POST keeps query identifiers out of ordinary URL logs. There are no callbacks, push subscriptions, status URLs supplied by a result or automatic requests induced by a DSN.

Use the existing selected HTTPS/TLS 1.3 service-answer authentication, DNS-ID/path validation, current trust-policy/status checks, no 0-RTT, no redirects, no ambient credentials and bounded fixed-length HTTP mechanism. Do not infer TLS backend support from this proposal. Credentials are released only after actual service authentication and current local authorization. Each request has `Content-Type: application/json`, `Accept: application/json`, Bearer authorization and no cookies. Both sides use `Cache-Control: no-store`. No compressed bodies or trailers are selected.

Request JSON is strict UTF8 with exactly these members, no duplicates, unknown members or null values. Integer fields use decimal integer tokens without signs, fractions or exponents and fit 0 through 9007199254740991 unless a tighter range is stated; strings use their decoded values after strict JSON parsing:

| Member | Type/value |
| --- | --- |
| `profile` | `mail-outcomes-v0` |
| `purpose` | `mail-outcome-query` |
| `account`, `incarnation` | Exact configured service identifiers |
| `submission` | Retained 64-hex ENVID token |
| `bindingDigest` | Retained 64-hex prepared-attempt commitment |
| `stream` | Empty string before the first accepted result; thereafter the exact service stream identifier |
| `after` | Safe integer 0 initially; thereafter last durably retained sequence |
| `nonce` | Fresh random 32 octets encoded as 64 lowercase hex, retained with these original query bytes before transport |

A lost query may be retried with exactly those bytes. This read-only query does not freeze the returned snapshot: a retry can return a longer prefix as the provider learns more. Returned requestDigest/nonce identify this query; observation identities independently deduplicate effects. No renewed nonce is needed to repair an uncertain query, and timeout does not resolve the underlying delivery.

The service authenticates the caller before lookup; derives account/incarnation from that credential; and requires exact equality with the request. It resolves submission and commitment from its own retained SMTP record. The request cannot create a record or choose an identity, stage permission or recipient inventory. Unknown token, mismatched commitment, another owner or expired retention return the same unavailable result without leaking records. A nonempty stream must equal the retained stream. An after value beyond the retained head is invalid, never evidence that events were lost.

::: {.details summary="Exact response and observation schemas"}

Only HTTP 200 with a complete strict JSON body of this exact shape supplies observations:

| Member | Type/value |
| --- | --- |
| `profile` | `mail-outcomes-v0` |
| `purpose` | `mail-outcome-observations` |
| `service` | Exact configured origin |
| `account`, `incarnation`, `submission`, `bindingDigest`, `nonce` | Exact request values |
| `requestDigest` | 64-hex SHA256 of the original request bytes, not a reserialization |
| `stream` | Stable random 32-octet hex identifier assigned to the retained SMTP transaction |
| `after` | Exact request after |
| `through` | Last sequence included, or after if events is empty |
| `events` | Array of observation objects below, in increasing sequence |
| `more` | Boolean: more retained events were available in this snapshot |

An observation has exactly `sequence`, `recipient`, `obligation`, `stage`, `action`, `status`:

- `sequence`: positive safe integer in this stream. The immutable append log starts at 1 with no gaps. The response includes the contiguous range after+1 through through. Across pages, its stream and complete original submission binding remain unchanged.
- `recipient`: zero-based safe-integer index into the complete attempted RCPT vector, never a supplied new address.
- `obligation`: stable opaque 32-octet hex identity allocated by the service for one actual custody obligation within this stream. Its recipient index and stage are immutable. The same stage can contain several distinct obligations; the service cannot reuse an obligation for another hop, fork, retry obligation or recipient. The identifier is correlation, not proof of custody or permission to disclose a branch.
- `stage`: exactly `submission`, `relay`, `mailbox` or `list`; present in the current trusted registration and derived by the provider from actual custody/operation, not a forwarded reporter label.
- `action`: exactly `accepted`, `deferred`, `failed`, `relayed`, `delivered` or `expanded`, subject to the table below.
- `status`: ASCII enhanced status string: class 2, 4 or 5, dot, one-to-three decimal subject digits, dot, one-to-three decimal detail digits; no leading zeros except single0. Unknown subject/detail values remain valid diagnostic classifications, not executable instructions.

| Stage/action | Meaning and status constraint |
| --- | --- |
| submission/accepted | Provider durably accepted SMTP responsibility for this recipient; class 2 |
| relay/deferred or submission/deferred | Provider still intends to try this recipient; class 4 |
| submission/failed or relay/failed or mailbox/failed or list/failed | Provider abandoned this scoped recipient obligation; class 4 or 5. Class 4 may explain exhaustion; do not rewrite action to deferred. |
| relay/relayed | Provider handed responsibility to its next hop; class 2, not final mailbox receipt |
| mailbox/delivered | Provider made the submitted representation available in the destination mailbox it serves; class 2, not decryption or human reading |
| list/expanded | Provider performed list expansion; class 2, not successful delivery to each member |

All other pairs are invalid. The service emits exactly one submission obligation per accepted original recipient. Its submission/accepted event must precede downstream events for that recipient in this log. A new downstream custody obligation has its own identifier, even when the stage matches an earlier hop. No event carries a parent/child link or proves that one obligation caused or completely covers another; that relationship is outside this version. A rejected RCPT recipient has no accepted event; its direct SMTP rejection remains the source. This profile does not use later query observations to invent an acceptance for a recipient excluded by a retained decisive SMTP result.

Sequence records the service's append order, not a trusted global time or proof of downstream causal order. No observation has a free-text diagnostic, alternate destination, participant identity, timestamp, encryption-support flag or requested remedy. Those belong to separately scoped evidence, not this result schema.

### Processing limits

| Input | Proposed maximum |
| --- | --- |
| Decoded query | 8192 octets |
| Response | 1048576 octets |
| JSON container depth | 8 |
| Observations per page | 256 |

These are proposed finite profile limits. Implementations may hold with an explicit local processing-limit outcome when their budget is smaller.

Providers configure bounded connection/header/rate/account/storage budgets and positive minimum polling intervals. They advertise those operational values through trusted configured provisioning, not untrusted result fields.

### Polling and backoff

Clients retain the configured interval and use bounded backoff. Exhaustion returns HTTP 429 with Retry-After as positive integer seconds.

Only an authorized outstanding delivery workflow or deliberate history inspection initiates a query. Rendering, opening or importing a message does not.

### HTTP error responses

| Status | Exact `error` value | Meaning |
| --- | --- | --- |
| 400 | `invalid` | Invalid request |
| 401 | `unauthorized` | Missing or expired credentials |
| 403 | `unauthorized` | Insufficient role |
| 404 | `unavailable` | Unavailable binding or stream |
| 415 | `unsupportedRepresentation` | Unsupported representation |
| 413 | `tooLarge` | Excessive request |
| 429 | `rateLimited` | Configured budget exhausted |
| 503 | `unavailable` | Service unavailable |

Except successful HTTP 200, no body supplies an outcome. An error body is exactly one object with the single string member `error` from that mapping. Other statuses/bodies remain unsuccessful observations. No redirects are followed.

Content-retention promises cover complete stream records rather than just mutable latest status. Detailed records may expire after the promised interval; used-token tombstones do not. After detailed records expire, the service returns 404 for the old token permanently and never rebinds it to another transaction. This remains true when the first client had never learned the original stream. Tombstones need retain only the authoritative account-incarnation/token nonreassignment fact, protected with the service's durable state; deleting a body, log or account UI record cannot clear it.

The provider configures a finite total capacity for these permanent reservation facts, reserves that capacity atomically with MAIL admission, and refuses new reporting-enabled token reservations before body release when capacity is exhausted. It does not evict old reservations, rely on a probabilistic filter with false negatives, or rotate an account incarnation simply to erase reservations. This is a cumulative storage and admission cost of the selected design, not a claim of indefinitely bounded storage while accepting unlimited attempts. An ordinary SMTP path, if separately authorized, retains its own reporting and protection semantics and cannot be reported as implementing this capability.

A recovery lacking authoritative nonreassignment state disables new reporting-enabled admissions and returns unavailable for lost historical evidence. It cannot recreate the same account incarnation with an empty namespace, reset a stream sequence, or substitute a new stream under an old token. A deliberate newly provisioned account incarnation has a distinct identifier and no authority to answer old-incarnation queries. Retirement prevents future old-incarnation credentials or admissions; identifiers are not recycled. Cross-service migration and recovery of lost nonreassignment state require a separate contract. History already retained by clients remains attributed and is not erased by404.

:::

::::

## Keep the history when an outcome changes

The app preserves earlier evidence and compares claims only within their proper custody obligation. Conflicting claims remain visible; different stages are not assumed to describe the same work.

:::: {.details summary="Current authority, durable admission, duplicates and scoped outcomes"}

The client accepts a page only from the configured direct authenticated HTTPS response to this exact route and query, with current account/registration/credential/channel authorization and matching original request digest, nonce, commitment and stream. Downloaded JSON, a forwarded result, an unrelated authenticated connection or an authenticated mailbox fetch cannot call this acceptance path.

Before transport and again before committing a result, the client rechecks current local reporting registration, account incarnation and outgoing-account association. Withdrawal prevents new result admission through that authority. The response may describe historical delivery; freshness of the authenticated acquisition does not make the observation a new delivery or endpoint proof. Local credible time and TLS validation obey the existing owning contract. This schema supplies no timestamp-based freshness claim.

Atomically append the exact query/response bytes, actual TLS/service/configuration evidence, original submission association and validated observations, and advance the cursor with the derived per-recipient projection. Failed persistence leaves the page unaccepted and the cursor unchanged. Reopen validates retained provenance; restore uncertainty cannot turn records into current request authority. Historical accepted observations remain inspectable after authority revocation, clearly attributed to their original authority and acquisition. They cannot authorize a new lookup or send.

Identical observations at the same stream/sequence are duplicates. A second authenticated different observation at that identity is a retained conflict; do not choose last arrival or perform new mail delivery. An untrusted malformed page does not reserve or poison the trusted observation namespace. A page gap, changed binding, decreasing through, inconsistent more/empty-page combination or unannounced stream change is invalid and cannot advance the cursor. more=true requires a nonempty page. Repeated pages use the same original record semantics, regardless of JSON whitespace/member ordering.

Compare observations only within the same service stream, original recipient, obligation and immutable stage. Different obligation identifiers, even within one stage, are separate scopes. Different stages are incomparable in this version. Sequence orders appends only; it does not establish a parent/child relationship, cross-stage completion or cancellation.

Within one obligation, repeated equal action/status claims are duplicates of the same meaning, even if separately appended. A terminal action is failed, delivered, expanded or relayed: each ends that particular custody obligation, with relayed ending only the reporting service's handoff obligation. A later deferred or accepted event cannot reopen it. Two different terminal actions for that same obligation are conflicting claims. Different enhanced status codes attached to the same terminal action remain separate diagnostic classifications; retain them without manufacturing a new action or ordering. A changed recipient or stage under a retained obligation identity is an authenticated binding conflict and cannot be used as a different scope.

A failure following an earlier acceptance **within the same submission obligation** can qualify that obligation as failed after handoff without erasing the handoff. A failure on a later relay obligation is a reported relay failure, not proof that the submission was never accepted. A list expansion followed by failure on a different relay/mailbox obligation is not a terminal conflict and not proof that every expanded delivery failed. Equally, delivery on one obligation does not establish delivery on every other obligation. This profile supplies no branch-coverage declaration or universal all-recipient success/failure proof.

| Retained observations within one obligation | Derived scoped description |
| --- | --- |
| Accepted only | Responsibility acceptance recorded for that obligation |
| Deferred, with no terminal observation | This custody obligation remains pending |
| Relayed, without another terminal action in this obligation | This service handed off that obligation; downstream outcome unknown |
| Failed, without another terminal action in this obligation | This custody obligation failed; preserve any prior acceptance |
| Delivered, without another terminal action in this obligation | This mailbox obligation made content available; no endpoint/read claim |
| Expanded, without another terminal action in this obligation | This list obligation expanded; branch/member outcomes unknown |
| Different terminal actions within the same obligation | Conflicted scoped claims, preserving each source observation |
| Different obligations or stages | Parallel attributed outcomes; no inferred conflict, overwrite or complete coverage |

The exact submission/accepted observation may be compared with the corresponding decisive local SMTP recipient result. An acceptance conflicting with a retained decisive RCPT/final rejection is explicit conflicting evidence for that transaction. Downstream-stage observations are not compared as alternative values for the direct SMTP transaction. A recipient summary retains its submission result and displays later scoped failures/progress; it does not replace that history with one arrival-selected global status. No scope establishes that content was never exposed.

A matching service acceptance may resolve an uncertain local handoff only as **this provider's retained acceptance**. It does not erase possible earlier exposure, establish final destination arrival, or rule out other attempts. Absence of an event, an empty page, unavailable/404, timeout or expired credential never proves nonacceptance, nonexecution, recipient incompatibility or success. Mark the relevant delivery pending, unknown or conflicted without inventing a remedy. Local SMTP rejection/uncertainty and ordinary legacy DSN advisories remain separately visible evidence.

No result changes content, author, audience, slot resolution, endpoint identity, device authority, key confirmation or encryption policy. Resend, reroute and downgrade still require the existing separately authorized intent/release procedure. A report does not allocate an action submission, execute a button, mark a conversation read or send a reply. Show a later actionable failure in the owning conversation/delivery presentation without creating an ordinary authored chat contribution.

::::

## Keep private recipients private

The reporting connection does not publish hidden recipients, protected content or unauthorized list branches to other participants. It does not make the configured provider unable to observe its own SMTP envelope or queries.

:::: {.details summary="Account access, private branches and metadata boundaries"}

Only the sender's authorized own-account reporting connection can inspect the stream. A recipient or another account cannot query it using a learned token, digest or cursor. Results contain recipient indices and opaque custody-obligation identifiers, not new addresses; the service and client already retain the original envelope meanings. The provider may expose only obligations the authenticated account is permitted to inspect. List-subscriber identities, hidden branch counts and branch identifiers are not implicitly authorized by permission to inspect the submitted list address. Only observations authorized for this account-facing stream enter its sequence log. Private internal branch events do not enter that stream and do not consume its sequence numbers; do not redact a completed page in a way that creates gaps or reveals hidden branch counts. Where branch disclosure is not authorized, omit it from the export stream rather than aggregate it into a false universal outcome; the visible list-expansion observation remains scoped and downstream coverage unknown. If later permission withdrawal prevents reading part of an existing stream, hold that stream lookup rather than renumber or silently present a filtered complete history. No visible conversation record receives the full private/Bcc envelope inventory. Different blind/private deliveries retain independent original attempt associations.

The query sends only identifiers/commitments the configured submission service is authorized to associate with its existing transaction. It contains no decrypted body, inner protected addresses, key data, contact list or logical conversation identifiers. Original bytes and credentials remain out of routine logs. The service still observes the SMTP envelope, commitment, polling and timing; this proposal does not hide metadata from that configured provider. Acquisition never follows a URL extracted from a report, diagnostic or response.

::::

## Join the service to real delivery records

Both ends need the real account, SMTP and persistence integrations. Parsing a result or inserting a fixture does not demonstrate that joined capability.

:::: {.details summary="Rust ownership boundaries and provider integration"}

The reusable Rust integration should have three distinct boundaries: a witnessed local reporting-registration owner; an actual authenticated query adapter that returns a nonconstructible scoped observation capability; and a Store admission transaction that consumes that capability with the retained original attempt. Exact public API names are implementation choices. A public result setter taking a bool, caller-claimed TLS receipt or an arbitrary parsed object would not implement the channel contract.

Reuse the durable SMTP reporting binding and actual account/trust acquisition mechanisms. The provider service must join the real SMTP-authenticated account, complete before-transformation body commitment and acceptance log; a test fixture inserting a trusted result without that join proves only parsing. Ordinary DSN ingestion continues independently and cannot be promoted by calling this new API with report-derived values.

::::

## Demonstrate the behavior before claiming support

Acceptance needs to exercise the actual service and durable owner, including failures, privacy and recovery. The scenarios below are acceptance requirements, not a claim that an implementation has passed.

:::: {.details summary="Required acceptance scenarios and observable results"}

| Actual scenario | Required observable result |
| --- | --- |
| Two recipients accepted; one later fails through actual configured query | Failure qualifies only its recipient after handoff; other recipient and original acceptance remain |
| Final SMTP reply lost, provider retained acceptance | Authenticated matching accepted event qualifies provider handoff; missing query result leaves uncertainty |
| Wrong token/account/incarnation/commitment/credential/stage or learned peer token | No foreign stream disclosure, accepted event or cursor advance |
| No DSN, partial body, rejected RCPT or unsupported body mode | Reporting unavailable or exact scoped refusal; no invented binding/acceptance or protection change |
| Duplicate SMTP token after restart and after detailed-record expiry, from a second authorized account application with identical body/envelope | Reservation refused permanently; original client with no prior stream cannot bind the later transaction; old-token lookup remains unavailable after expiry |
| Permanent reservation capacity exhausted or tombstone state missing on recovery | New reporting-enabled reservation refused before body release; no old-token recycling or same-incarnation empty namespace |
| Exact HTTP retry, pagination, restart and dropped response | No mail/action effect; identical events deduplicate and retained cursor resumes without gaps |
| Tampered request digest/nonce/stream, unknown members, duplicate names, truncation, oversized page or false sequence | No page admission; known state preserved |
| Different valid event at one sequence, or changed stage/recipient under one obligation | Exact identity/binding conflict retained; no namespace reassignment |
| Delivered then failed within one obligation; deferred after that obligation failed | Terminal conflict or preserved terminal state; no last-arrival overwrite/resend |
| List expansion then relay failure on a distinct obligation/stage | Both scoped observations retained without conflict or global failure; expansion does not imply subscriber delivery |
| Two relay obligations, one relayed and another failed | Separate handoff/failure scopes preserved; sequence does not invent a hop relationship or universal failure |
| Local withdrawal during query or provider revocation before lookup | No newly admitted result through withdrawn permission; earlier history remains attributed |
| Failed Store persistence or restore before cursor commit | Page not acknowledged as applied; retry/reopen cannot skip evidence or create authority |
| Legacy DSN with correct ENVID, DKIM-pass candidate, copied JSON or TLS IMAP acquisition | Remains its own evidence class, never promoted into authenticated service observation |
| Relay handoff, final mailbox and list expansion | Distinct stage-limited outcomes; no decryption/read/member-delivery claim |
| Bcc/private copy, relay transport identity and error logging | No hidden envelope identity or inner decrypted content exported to other recipients/logs |
| Authenticated failure and an existing confirmed button result | Mail recipient projection changes only; button history, keys and original protection remain |

Two deployments of one implementation demonstrate integration, not independent interoperability. All rows above are planned acceptance; no runtime pass is claimed.

::::

## Storage and lifetime cost

A token can never be reassigned within its account incarnation, even after detailed reporting records expire. The provider therefore retains permanent used-token facts. A finite configured capacity limits new reporting-enabled admissions; reaching it cannot justify recycling old tokens. The lifetime disclosure above contains the exact recovery and admission rules.

## Scope and remaining integration

This proposed capability selects configured direct read-only service observation, mandatory DSN/unique ENVID, pre-transformation message commitment, append-only paged observations and stage-limited first-party claims. These are additional service requirements, not guarantees supplied by base DSN. Permanent token nonreassignment requires cumulative reservation storage and can limit new admissions; explicit custody obligations require provider integration with actual delivery records.

Public discovery/login/credential issuance, delegated downstream testimony, transferable signed receipts, retention-policy publication and recovery/migration need separate contracts before public advertisement. This first version deliberately makes no promise of their interoperability. The numeric processing limits and identifiers remain proposed; no registry allocation or universal deployment quota is implied.

See [transport outcomes and legacy reports](transport.md), [what a status can tell you](client-behavior.md#what-a-status-can-tell-you), and [module-specific service permissions](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions). The [service-answer result](service-answers.md#read-the-service-s-result) illustrates a separately scoped HTTPS observation; its action permissions and receipt schema do not authorize mail reporting.
