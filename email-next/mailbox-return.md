---
title: Confirm setup through both mailboxes
order: 7.175
blurb: ordinary mailboxes · private challenges · receiving setup in both directions
sectionNav: true
---

# Confirm setup through both mailboxes

Two compatible apps can check a round trip through each address before releasing
the first encrypted human message. Every step travels through ordinary email;
the providers need not implement Email/2. The writing stays on the sender’s device
while the apps exchange small setup controls.

> [!ex] Alice writes; both apps arrange the reply path
> 1. **Alice asks Bob for setup.** Her app introduces a candidate device, without sending her writing.
> 2. **Bob sends Alice a private challenge and his receiving setup.** Only Alice’s introduced device can decrypt it.
> 3. **Alice returns Bob’s challenge, adds her own and supplies her receiving setup.** Bob can now check that her device obtained the private reply mailed to her address.
> 4. **Bob returns Alice’s challenge.** Alice can now check the corresponding round trip to Bob. This last control asks for no acknowledgment.
>
> Both directions now have receiving material for their own protected streams.
> Each app still checks current authority, admission and delivery permissions.

This optional draft acquisition profile is `mailbox-return-v0`, inside the same
Email/2 specification and selecting `mail-conversation-v2`. Choose it before
allocating the attempt. The [direct-envelope setup path](mailbox-setup.md)
remains available with its exact original authentication, signed formats and
terminal response. A failed old-format check cannot silently become this path.

The check shows access to an addressed return route and the participating device
key for this exchange. It does **not** verify a person, exclusive mailbox
ownership or direct SMTP delivery. A forwarding destination, mailbox delegate,
domain administrator rerouting mail, or attacker intercepting the sealed return
mail while holding its device key can also obtain that route access.

Bob completes his local address check at step three; Alice completes hers at step
four. A lost final control leaves Alice pending. Neither side can claim both apps
received everything. Other recipients can complete their own setup independently.

> [!warn] Draft contract; interoperability remains to be demonstrated
> Complete implementation, actual unchanged-provider SMTP/IMAP operation and
> independent interoperability/security evaluation remain required. A local
> queue simulation, parser test or passing signature does not establish them.

## Choose when the round trip is allowed

Use valid cached setup or an independently authorized provider path when suitable.
A selected human send may authorize considering this enabled carrier; it does not
authorize address-book scanning. Requesting setup and answering requests have
separate visible, revocable account policies. No incoming email can enable them.
No per-correspondent manual approval or upgraded mail server is required by this
profile; stricter local disclosure/verification policies can still hold it.

An authenticated account may provide eligible fresh mail without proving whether
it arrived by SMTP or IMAP APPEND. An explicitly enabled unknown-ingress policy
permits only the bounded candidate exchange below. Record real acquisition facts;
never manufacture trusted envelope evidence from a downloaded header. Known local
imports, restore/history scans and quarantine do not initiate setup. Generic IMAP
cannot reliably classify every import, so this policy admits a bounded trigger
exposure rather than claiming delivery provenance.

Every leg still needs a valid current device signature and actual full-body DKIM
without an `l=` tag, covering the actual sole From, with signing domain exactly
equal to that leg’s source domain. A configured trusted verifier may supply those
exact facts; copied `Authentication-Results`, SPF, relaxed alignment and device-key
knowledge alone cannot. See [domain authentication](security.md#domain-signatures-and-algorithm-policy).

Request and offer evidence stay quarantined as candidates. They cannot pin or
replace a mailbox association, enter ordinary passive discovery, release human
content, enroll a group/list, disclose contacts/history or authorize a downgrade.
Current device authority, disclosure, credible time, pins, complete candidate set
and verification policy apply throughout. A domain signature is not mailbox
local-part or human identity proof.

## Formats and mail delivery

The new profile has closed record and sealing formats. Its notice contains no
human writing; older clients may display that notice rather than hide it.

::: {.details summary="Exact sealing profile, carrier and submission modes"}

Acquisition profile: **`mailbox-return-v0`**, selecting the existing
`mail-conversation-v2` protected agreement. It does not modify setup0/1/2 schemas,
add optional fields to their strict objects or reinterpret their terminal response.
Those responses still elicit no automatic acknowledgment. Old formats remain
terminal and cannot activate a return-confirmation attempt.

This procedure needs three non-legacy sealed kinds: `mailbox-return-offer`,
`mailbox-return-confirm` and `mailbox-return-finish`. Appending these silently to
the closed sealed2 kind list would misrepresent compatibility. The isolated extension is **`mailbox-return-control-v0`**: the [existing HPKE construction](suite-profile.md#confidential-setup-and-control) and length/bundle/intent inventories with an explicitly different
profile, magic, signature/info domains and closed three-kind list. It creates no
new cryptographic suite and changes no general conversation-control format.

| Sealing item | Exact draft value or inherited rule |
| --- | --- |
| Outer magic, eight ASCII octets | `MAILRTE0` |
| Inner magic, eight ASCII octets | `MAILRTI0` |
| HPKE algorithms | Existing Base-mode X25519/HKDF-SHA256/AES-128-GCM construction |
| HPKE info domain | `mail/mailbox-return-control/v0`, then existing NUL/raw key-ID/public-key suffix |
| Intent version | String `0` in this independently selected profile |
| Intent purpose | `mailbox-return-intent` |
| Intent signature domain | `mail/mailbox-return-intent/v0`, existing NUL/U32/original-byte framing |
| Intent members/framing/AAD | Same typed inventory and binary length rules as the existing construction, using these exact magics/domains; no trial decryption |
| Allowed kinds | Exactly the three return kinds above |
| Sender authority | Current receive-authorized device named by the owning leg; independent transport-account permission remains required |
| Recipient choice | Exact pending-attempt candidate and key authorized by this procedure, not a generic operational mailbox association |
| Body | Complete original strict owning wrapper bytes, preserving its independent signature |
| Key/body/bundle/JSON limits | Inherited existing bounded construction and stricter setup limits; never truncate |

The signed request and offer explicitly select `sealProfile` equal to
`mailbox-return-control-v0`. That is a narrow additional authorization to use the
exact assertion's fresh control key for this attempt's three return controls.
It neither changes an earlier published key promise nor extends a deadline or
gives this exception to any other kind. The key is still independent control key
material, not a signing/MLS/archive/route key. New request key custody is persisted
before publication. Its original deadline remains unchanged. The offer's key and
MLS receiving promises retain their independently owning intervals.

This explicit new signed authorization and purpose-limited candidate-recipient
selection are necessary additions, not permissions inferred from assertion10
alone. A legacy assertion10 does not claim support for the new profile. A client
recognizes the new request format or leaves it unhandled; it never tries an old
parser after a failed new validation. No top-level Email/2 version changes.

### Mail placement

The unsealed request uses a distinct unregistered candidate media type
`application/vnd.mail.return-request+json`, no parameters, canonical MIME base64
and filename `mail-return.json`. Reuse the bounded two-part notice/attachment
[layout, singleton-header and forbidden-field rules](mailbox-setup.md#send-one-content-free-request), without inheriting that path’s direct-envelope provenance gate. Its generic notice contains
no human draft or authored-message digest. The notice is exactly
`A compatible email app is confirming encryption setup.` followed by CRLF.

The three sealed legs use a distinct unregistered candidate media type
`application/vnd.mail.return-control`, no parameters, canonical MIME base64 and
filename `mail-return-control.bin`, with the same generic notice. Recognizing a
filename, media type or magic gives no authority.

MIME-Version is exactly `1.0`; the outer multipart/mixed has exactly two direct
children: `text/plain; charset=utf-8` with the exact notice above, then the exact
attachment. No nesting, extra parts, duplicate singleton headers, ambiguous MIME
or invalid transfer encoding is eligible for automatic processing. Retain each
original message for inspection; do not search forwards or quotations for controls.
Every leg has one From, one To, one Date, one Message-ID and the exact Auto-Submitted
value below. Its sole To must match the authorized selected local account/mailbox
and signed leg destination; its sole From must match the signed source for that
leg. An alias requires independently authorized exact mailbox selection, not
plus-tag guessing or case folding.

| Decoded object | Maximum octets/depth |
| --- | --- |
| Owning wrapper/body | 4,194,304 octets |
| Original payload | 262,144 octets |
| Each assertion wrapper | 1,048,576 octets |
| Strict JSON container depth | 32 |

The [sealed construction](suite-profile.md#confidential-setup-and-control) also
bounds complete plaintext to 8 MiB and identity bundle to 1 MiB. Apply the stricter
owning-body bound above. Bound carrier/header work before decoding; a smaller
local resource budget yields a processing limitation, never prefix acceptance.


| Leg | Outer From | Sole To / submission destination | Auto-Submitted | Proposed SMTP reverse-path |
| --- | --- | --- | --- | --- |
| Request | Original source | Original target | auto-generated | Original source |
| Offer | Original target | Original source | auto-replied | Frozen local null or exact-source mode |
| Confirm | Original source | Original target | auto-replied | Frozen local null or exact-source mode |
| Finish | Original target | Original source | auto-replied | Frozen local null or exact-source mode |

No Cc/Bcc, Sender, Reply-To, Resent-*, List-*, receipt request, callback or additional
recipient is permitted. Generic Subject remains `Secure email setup`. A sole
In-Reply-To can point to the preceding retained Message-ID for explanation, never
security correlation. All legs remain actual email messages carried through
ordinary mail infrastructure. A legacy client may show these controls; no legacy
silent-discard promise is made.

The new procedure explicitly permits only offer→confirm→finish under the retained
attempt. That is a bounded automatic-response exception with three different
purposes. Finish, bounce, receipt, unknown input and ordinary old setup responses
never initiate another leg. No error/cancellation/refresh acknowledgment mail is
invented. Generic auto-responder behavior cannot activate this exception.

### Proposed control-submission choices

The direct-envelope mailbox-setup profile explicitly chooses null reverse-path for
responses. That is a profile choice, not an RFC3834 requirement to use null in
every automatic response. RFC3834§3.3 says the return address SHOULD make loops
unlikely; it permits null or a specifically chosen address that does not
respond automatically. Its general guidance does not prove an ordinary mailbox
is such a special nonresponder address.

This draft profile defines two locally selected submission
modes: `null` where supported, or `exact-source` using the actual outgoing leg's
locally authorized From mailbox as MAIL FROM. This is an explicit compatibility
choice with the additional safeguards and residual risk below, not a claim that
RFC3834 recommends every ordinary source address. Do not provision or discover a
fictional special mailbox. An existing provider-authorized nonresponder facility
can remain its separately configured transport mechanism, not invented evidence.

Select and freeze the mode and actual envelope before preparing that outbox item.
The peer cannot choose it. A null submission failure does not silently switch an
uncertain item to exact-source or allocate another response. Existing definitive
failure/retry and separately authorized transport-preparation rules still govern.
No arbitrary third-party return address is permitted.

`exact-source` makes ordinary authenticated submission possible where null is
refused, without an Email/2 server. It permits DSNs/other automatic mail to arrive
at the sender's normal mailbox. The following are required in either mode:

- Only the three authenticated step transitions can emit controls, each once per
  durable branch/step; no generic reply-to-automatic behavior.
- Auto-Submitted remains auto-replied; request NOTIFY=NEVER where supported.
- Bounce, receipt, vacation reply, quoted/nested controls and unknown purposes
  produce no new leg, package or challenge. They cannot carry a valid peer device
  signature and exact current transcript merely by quoting the original.
- No arbitrary original human text, attachments or readable request quotation is
  signed into the automatic response. Only bounded fixed-purpose records and the
  minimal independently valid proofs are emitted, sealed to the exact key.
- Late errors update the matching outbox uncertainty/failure only through their
  own authenticated delivery-status contract; a descriptive bounce is not setup
  evidence, a success acknowledgment or an instruction to resend.

These gates bound conforming Email/2 behavior; they do not force every unrelated
legacy vacation responder, DSN generator or forwarding service to be well behaved.
An account with another automatic responder can still experience unwanted
third-party traffic or loops outside this state machine. Prefer null when usable,
expose/control the account's chosen mode and test coexistence. Do not claim that
exact-source eliminates backscatter or satisfies a generic nonresponder-address
assumption. Expose that residual risk with the account’s submission-mode policy. Selecting the mode does not require a per-correspondent approval step.

Account adapters still unable to submit the exact From/carrier or obtain usable
current DKIM stay unavailable with an explicit reason. No universal provider
compatibility is claimed. Every four-leg unchanged-provider SMTP/IMAP submission
mode needs actual tests before such claims; none requires the provider to adopt
Email/2.

### Address and material visibility

The initial request exposes its source/target mailboxes and public assertion;
private challenges do not appear until sealed legs. The unmasked baseline also
exposes From/To routing addresses on later controls. Encryption of the body does
not hide those headers. Public KeyPackages/keys/assertions are not secrets and
cannot serve as the return challenge.

The stable claimed mailbox and a provider's public relay address remain distinct.
A challenge destination cannot be replaced by a relay or callback nominated only
by the unproved candidate: that would let Mallory redirect victim's challenge to
herself and defeat the test. An already independently authorized route may carry
the control under its existing exact account/identity/ciphertext binding; its
proof scope is the authorized route, not an address-pattern inference. New route
claims need their actual owning authorization before use. The minimum unmasked
first-use path sends only to the original claimed mailbox. If current policy
requires concealed personal addresses and no independently authorized masked path
exists, this carrier holds; it cannot expose them and label the result masked.

:::

## Signed records

Each control commits to the exact earlier messages and devices. The third also supplies Alice’s ordinary receiving setup; the fourth confirms the same bytes.

::: {.details summary="Exact wrappers, payload fields and signatures"}

All payload fields are strings. Preserve the strict JSON, original UTF-8,
canonical mailbox, ObjectId, lowercase SHA-256 and uint64-string grammars already
selected by the suite. No unknown, duplicate, missing or null members; no numbers
or trailing bytes. Advertisement remains the complete original assertion10
wrapper under its own signature, native key/package and current identity rules.

Request and offer wrappers have exactly three members:

| Member | Meaning |
| --- | --- |
| `payload` | Canonical padded standard base64 of original payload bytes |
| `signature` | Existing exact Ed25519 signature hex grammar |
| `advertisement` | Canonical padded base64 of complete original assertion10 wrapper |

The confirm wrapper has exactly `payload`, `signature` and `receivingAdvertisement`.
The last member is canonical padded standard base64 of Alice's complete original
ordinary assertion10 wrapper. The finish wrapper has exactly `payload` and
`signature`. Their identity dependencies remain the exact retained request/offer
originals and independently validated current continuity proofs. Only confirm
introduces the separately bound ordinary receiving assertion defined below; no
new actor or temporary key is introduced. Do not fetch assertions from received
URLs or reconstruct discarded originals.

### Request payload

| Member | Exact meaning |
| --- | --- |
| `version` | `0` |
| `purpose` | `mailbox-return-request` |
| `agreement` | `mail-conversation-v2` |
| `request` | Fresh initiator ObjectId, retained for every leg |
| `nonce` | Original fresh 32-byte nonce, lowercase hex; public correlation only |
| `source` | Original canonical initiating mailbox |
| `target` | Distinct original canonical receiving mailbox |
| `assertion` | SHA-256 of original request advertisement bytes |
| `sealProfile` | `mailbox-return-control-v0` |
| `notBefore` | Original attempt start |
| `notAfter` | Original final attempt deadline |

Its advertisement is attempt-only: no MLS package, null package deadline and the
fresh dedicated initiating control key. It is ineligible as an ordinary ongoing
receiving advertisement. The request's original interval fits the same accepted
maximum setup duration and every stricter key/binding/publication interval. This
profile retains the existing attempt bound and original receiving promises.

### Shared offer/confirm/finish members

Every one of these payloads contains exactly the following shared members, plus
its row's additions below. `source` and `target` always keep the original request
meaning; they are not swapped when the mail direction changes.

| Member | Exact meaning |
| --- | --- |
| `version` | `0` |
| `purpose` | Exact owning leg purpose |
| `agreement` | Original `mail-conversation-v2` |
| `request` | Original request ID |
| `source` | Original initiating canonical mailbox |
| `target` | Original receiving canonical mailbox |
| `requestDigest` | SHA-256 of original decoded request payload bytes |
| `initiatorAssertion` | Exact original request advertisement digest |
| `responderAssertion` | Exact original offer advertisement digest |
| `sealProfile` | `mailbox-return-control-v0` |
| `notBefore` | Original request start, unchanged |
| `notAfter` | Original request final deadline, unchanged |

| Leg/purpose | Additional members | Required meaning |
| --- | --- | --- |
| mailbox-return-offer | challenge | Bob's fresh independent 32-byte private challenge, lowercase hex |
| mailbox-return-confirm | `offerDigest`, `answer`, `challenge`, `initiatorReceivingAssertion` | Exact original offer-payload digest; exact Bob challenge; Alice’s fresh private challenge; exact ordinary receiving-wrapper digest defined below |
| mailbox-return-finish | `offerDigest`, `confirmationDigest`, `answer`, `initiatorReceivingAssertion` | Exact offer and original confirm-payload digests; exact Alice challenge; same ordinary receiving-wrapper digest as confirm |

The offer advertisement supplies one independently valid unused MLS package and
its own nonnull control key. Its principal/device and actual current receive
binding must equal the sealed offer sender. The initiator advertisement identifies
the sealed offer/finish recipient and key. Confirm sender/recipient are the exact
opposite devices; finish returns to the exact original initiator. A current
continuous same-device/key/role renewal can be checked only under the existing
continuity owner; no new principal/device/key or gap may be substituted.

Sign original payload bytes under these distinct domains and the existing
NUL/U32/original-byte framing:

| Purpose | Signature domain |
| --- | --- |
| mailbox-return-request | mail/mailbox-return-request/v0 |
| mailbox-return-offer | mail/mailbox-return-offer/v0 |
| mailbox-return-confirm | mail/mailbox-return-confirm/v0 |
| mailbox-return-finish | mail/mailbox-return-finish/v0 |

The sealed intent independently binds actual sender/recipient, key, kind, exact
original body and original interval. Neither wrapper signature substitutes for
the final AEAD tag or original identity/assertion validation. Transcript digests
are computed over original payloads, never reserialization, Message-ID, envelope
headers or ciphertext encodings.

Both Bob’s offer challenge and Alice’s independently generated confirm challenge
are exactly **32 octets** generated by the maintained OS-backed cryptographic RNG
inside the honest issuing device, only after the preceding complete leg is
accepted and its branch reserved. Each is encoded as exactly **64 lowercase
hexadecimal characters**. Both `answer` fields have that same exact grammar and
must equal the corresponding retained private challenge: confirm answers Bob’s
offer challenge; finish answers Alice’s confirm challenge. An answer echoes the
original challenge; it is not regenerated or replaced by the request nonce, a
hash or another derived value. Reject wrong length, encoding or value before the
corresponding proof, association or outbox effects. Compare the decoded fixed-size
secret values with a maintained constant-time cryptographic comparison. It is not derived from a nonce, key, package,
record ID, digest, counter or clock. It appears only in sealed bodies sent to the
claimed mailbox and their sealed echoes. Do not publish it in headers, proof
summaries, discovery, URLs, logs, notifications or readable alternatives. A
commitment or knowledge of an encryption key is not the challenge answer.

:::

## Local proof and eligibility

An unanswered request is only a candidate. Each app records route access only after its own private challenge comes back correctly.

::: {.details summary="Candidate quarantine and asymmetric completion"}

Each responding device has its own branch:

`(initiator principal, initiator device, request, responder principal, responder device)`.

This tuple is a namespace, not a secret or proof. Canonical mailbox pair,
agreement, original request bytes/digest, both actor/assertion/key commitments,
original deadline and the one retained offer become immutable branch context.
Several valid responder devices are separate branches; they cannot borrow proof
from one another.

| Honest local side/event | Permitted state/effects | Still prohibited |
| --- | --- | --- |
| Alice prepares request | One pending send-linked attempt and exact request outbox | Bob selection or human-send release |
| Bob accepts request | Candidate-only evidence, one offer allocation/outbox under policy | Alice operational pin or passive-observation promotion |
| Alice accepts offer | Candidate Bob, retained offer, one confirm with private Alice challenge | Bob operational selection; knowing request nonce/KeyPackage is insufficient |
| Bob accepts confirm answering his retained challenge | Address-return observation for exact Alice principal/device/source; reserve one finish | Claim that Alice received finish; bypass ambiguity/current-policy or ordinary-send checks |
| Alice accepts finish answering her retained challenge | Address-return observation for exact Bob principal/device/target | Claim that Bob received a receipt for this finish, or independently verified human identity |

An address-return observation demonstrates, to its honest issuer, that the actor
key answered a fresh secret mailed only to the claimed return address. It is
local, exchange- and device-scoped evidence of route access, not a transferable
mailbox-ownership certificate. An actor who controls a forwarding destination or
intercepts that sealed return mail and holds the corresponding key can satisfy
it. Device-key knowledge without access to the secret-bearing return mail cannot.

Only the completed local observation can enter the new explicitly typed
`mailbox-return` association provenance. Before then, every attempt advertisement
stays excluded from operational/passive selection. Keep embedded advertisements
in a separate typed attempt store; do not pass them to a generic passive-ingestion
API that could independently promote them. Unsupported readers treat the whole
unknown control as unhandled, not as a nested activation opportunity. The existing current identity,
complete retained observation set, ambiguity and serialized association generation
checks still decide eligibility. Under allow-unverified, a sole eligible candidate
may become associated-unverified; require-verification still waits for its
independent selected mechanism. Existing pins remain fixed unless their actual
owner authorizes change. A later real victim candidate must not be demoted to an
unrelated claim against a pin installed from an unproved request/offer.

Bob obtains his proof at leg3; Alice at leg4. Bob can commit the proof and an exact
finish outbox together, without waiting for an acknowledgment of leg4. He may use
his local observation for a separately authorized operation only if all of that
operation's own requirements are also met. He has no automatic human-send intent. The separate ordinary receiving
assertion/package from confirm supplies Alice’s receiving material for his own
independently admitted return stream; the attempt-only assertion never does. Alice's original human send remains held until her own leg4 observation,
required setup-secret retirement and the current MLS/admission/ordinary assertion/
audience/transport checks complete. No side is universally “ready” solely because
a mailbox-return observation exists.

Finish delivery uncertainty affects Alice's pending state, not the truth of Bob's
already completed Alice-route observation. UI/state distinguishes local proof,
local outbox submission, peer receipt unknown and protected delivery ready. It
must not claim an infinite chain of mutual knowledge. Late controls cannot reopen
a finished attempt or cancel an independently authorized established conversation.

:::

## Persist each transition once

A duplicate email or restarted app must recover the same handshake step. It must not create another challenge, reserve another package or send another automatic reply.

::: {.details summary="Atomic state, deadlines, cancellation and secret retirement"}

### Shared durable rules

The root request identity is `(initiator principal, initiator device, request)`
across every acquisition route, folder, alias mapping, import, restore and retry.
Protocol format/agreement are immutable attributes of that attempt, not a new
namespace. An old setup attempt cannot be replayed as a fresh return attempt with
the same authenticated identity; a separately authorized new attempt uses a fresh
request identity and preserves old delivery uncertainty.

A per-branch durable coordinator performs these transitions under current authority,
pin/association, local disclosure and full credible-time checks:

1. **At Bob, request→offer:** validate the whole original request and actual
   sole-From/no-l/exact-domain DKIM; target/account authorization; enabled
   unknown-ingress policy; current candidate device/assertion; existing pins and
   abuse budgets. Atomically reserve the branch, one receiving package allocation,
   Bob's private challenge, exact offer/advertisement, required private-key
   custody and one exact sealed outbox. Nothing operational is pinned. A duplicate
   recovers this outcome without new challenge, package, ciphertext or automatic
   submission.
2. **At Alice, offer→confirm:** fully authenticate/decrypt the selected original
   offer, verify every transcript/actor/target/key/time dependency and current
   corresponding gates. Atomically retain its candidate-only evidence, Alice’s
   fresh challenge, exact ordinary receiving assertion and one unused package
   reservation for this Bob device, independent custody promises and one exact
   confirm outbox. Its echo must match the actual
   offer challenge. No operational Bob pin is created.
3. **At Bob, confirm→finish:** fully authenticate/decrypt and check the exact
   original branch, offer digest, private Bob challenge and independently valid
   ordinary receiving assertion/package under the reciprocal rules below. Recheck current local
   policy, pins, authority, whole credible time and all budget/allocation facts.
   Atomically record the consumed challenge, exact confirmation digest, derived
   Alice-route observation, exact reciprocal receiving evidence and one finish
   intent/ciphertext/outbox committing its digest. Association
   selection, if authorized by current policy, participates in the same evidence
   generation/serialization boundary; it is not an implicit side effect of parsing.
4. **At Alice, finish→local completion:** fully authenticate/decrypt and check exact
   original branch, offer/confirmation digests, current state and private Alice
   challenge. Atomically consume it, record the derived Bob-route observation and
   local attempt completion. The separate common setup handoff still authorizes
   MLS/protected-outbox work; this transition itself releases no writing.

Original signatures and final AEAD checks precede any secret comparison or
conflict/response effect. Validate actual account scope, outer singleton From/To,
exact source signing domain, full-body no-l coverage and whole carrier on all
four legs; the selected client-first branch does not infer authoritative envelope
facts. Outer mail direction must match the mail-placement table and the owning actor. Rechecks at
release include current authority, policy, pin/association generation and time,
including elapsed work and SMTP354. No generic receive-role privilege becomes a
transport-account grant.

A validated unequal offer/confirm/finish under one reserved branch/step is scoped
conflict evidence. It holds that attempted branch under its owner; unauthenticated
variants cannot poison it, and it cannot suspend a preexisting operational peer
pin. Fresh intent IDs, ciphertexts or Message-IDs cannot create another step,
package allocation or response opportunity. Concurrent input must not expose two
different first outcomes before reservation.

### Time, cancellation and transport uncertainty

Every leg's inner attempt interval equals the original request's interval. These
copied body bounds identify the attempt; they do not claim a later-generated
responder key existed at the initial request time or extend a device credential.
The actual sealed intent's creation/release interval fits its actor/key validity
and the original attempt. Do not reuse an old validator that treats the copied
attempt start as the new responder's key-creation time. The
sealed creation/release intervals fit that original interval, exact selected
control-key promises and current authority. The complete credible-time interval
must fit at preparation, receipt and final release, with existing rollback and
renewal rules. Another acquisition, response, timer or retry never extends it.
If four legs cannot finish in time, that branch remains unresolved and needs a
separately authorized fresh attempt; no hidden renewal, plaintext or device swap.

Local cancellation stops new preparation and unsent release. It sends no
cancellation mail and cannot prove recall of submitted/uncertain controls. The
remote side is bounded by the original deadline. A local route observation already
completed before cancellation is historical evidence; future use is governed by
current local policy and its owner, not automatically erased or refreshed.
Cancellation of the human send does not authorize a new automatic human send on
a later response. For a never-completed branch, late responses cannot promote it
after local cancellation or expiry.

Each permitted local retry uses the exact retained signed object and ciphertext
under the same outbox identity. Duplicate input does not autonomously resubmit an
already submitted or uncertain control. Lost offers, confirms and finishes
therefore preserve explicit uncertainty rather than creating an acknowledgment
storm. A finish never asks for another response. A previously accepted exact retry
returns its recorded local outcome without reallocating or reusing retired secret
material.

### Challenge/key retirement

While active, challenge values and decrypted echo bodies are sensitive temporary
state protected by supported OS/private storage, not passwords, QR enrollment,
contact sync or correspondence archives. Retain exact originals privately while
needed for active validation/outbox uncertainty. Challenge deletion does not delete
independent unused-package/control-key receiving promises early.

After the issuer atomically consumes its own challenge, it can retire that value
and unnecessary decoded copies. Retain branch/step identities, original digests,
challenge commitments, authenticated consumed/result records, original age,
conflict/tombstone and outbox uncertainty under existing retention windows. Retain
required original sealed carriers separately; they do not become readable history.
If a temporary exact plaintext must remain for the existing active retry contract,
protect it until that step closes, then retire it under the same custody rules.
Do not promise that a digest permits later independent signature reverification
of plaintext that was deliberately retired. This is an explicit retention scope
for the new purpose, not a silent change to old records.

At deadline/cancellation/withdrawal, retire unneeded challenge/plaintext and
attempt-only initiating private keys under their actual owning lifecycle. Persist
consumed/expired outcomes so deletion cannot reopen the attempt after restart.
Known restore/rollback holds uncertain permissions and reconciles credible time
before any use. A stopped client cannot run timers; enforce the original deadline
before restarting work. Deleting active plaintext is not guaranteed cryptographic erasure: a retained
sealed carrier can still reveal its challenge to a holder of its still-live
receiving key. Its original expiry/consumed record must independently prevent
future authority. Do not label a challenge irrecoverably wiped while that path
remains. No cryptographic secure-erasure guarantee is invented.

:::

## Several devices and recipients

Each device answers for itself. A ready recipient can progress while another remains pending, under the sender’s selected delivery policy.

::: {.details summary="Branch scope, continuity and independent progression"}

One initiator device can receive offers from several independently valid Bob
devices. Each generates its own private Bob challenge and package allocation.
Alice creates a distinct private challenge/confirmation and unused ordinary
receiving-package allocation for each branch; neither
Bob device can answer for another. Several authorized Alice devices use their own
attempts/keys and cannot decrypt or adopt another device's pending branch merely
because an account password or transcript is synced.

A current accepted pin may justify an existing operation through its actual
identity/association policy without redoing first contact. That is continuity of
already selected trust, not a new return-confirmed or human-verified badge. A new
principal, changed target/address, replacement device/key or missing dependency
cannot borrow it to bypass the applicable first-use proof. Once a local observation
is valid, existing authorized identity/device continuity rules decide successor
use; another device is not presumed to possess this route merely by sharing an
email address. Device linking and live mailbox proof are distinct authorities.

Alice→Bob and Alice→Carol are distinct recipient attempts. Bob's proof, package,
local completion and permitted protected copy need not wait for Carol. Their
statuses and audience/roster admission remain per device and per recipient under
the existing asynchronous agreement. No request contains an intended group roster,
Bcc list or another recipient's private setup. Completion for one branch cannot
create an unplanned shared copy, private copy, group enrollment or history transfer.

:::

## Receiving setup in both directions

Sending Alice’s first stream does not automatically give Bob a stream he can send
on. Each sending device owns its own stream, and an ordinary creator assertion
may omit a joining package. Alice therefore supplies a separate ordinary receiving
assertion and unused package in the third control. This avoids another setup
round trip before Bob can prepare a reply.

::: {.details summary="Reciprocal assertion binding, allocation and custody"}

### Original bytes and signed commitments

`receivingAdvertisement` is canonical padded standard base64 of Alice's complete original signed assertion10 wrapper. `initiatorReceivingAssertion` is lowercase hex SHA-256 of those decoded **wrapper bytes**, using the same wrapper-digest convention as this profile’s other assertion commitments. It is not a digest of reserialized JSON or a replacement for native assertion signatures. Native roster/assertion references still use their own existing payload-digest/signature convention; store both distinct references explicitly.

The third-message Ed25519 signature covers the added digest as part of the original payload. Its sealed intent commits the exact original wrapper/body including `receivingAdvertisement`. The fourth-message signature covers the exact same digest, and its `confirmationDigest` now covers the original third-message payload. Bob cannot accept an advertisement absent from that signed digest; Alice cannot treat a final answer committing a different digest as success. No URL, lazy fetch, remembered capability or reconstructed assertion substitutes for the original wrapper.

Both messages retain original `initiatorAssertion` pointing to the temporary request assertion. It is not overwritten with the ordinary assertion. `responderAssertion` remains Bob's original offer assertion. All challenges, source/target, original request/offer digests, devices and attempt deadlines remain unchanged.

### Current identity and ordinary receiving authority

Before Alice prepares the third message, and before Bob commits it, independently validate the original receiving assertion's signature, complete identity proof and current authority, canonical mailbox equal to original `source`, exact principal/device equal to the original initiator, unchanged selected agreement/application support, ordinary control key and native package. The current selected receiving binding must match that device's independently accepted authority under the existing continuity rules; a new device, key/role gap or conflicting identity is not silently adopted through an assertion. A legitimate ordinary control encryption key is distinct from the temporary control key, without changing the signing actor. Both its key ID and public-key bytes must differ. Reusing an independently valid ordinary receiving key is allowed under its original custody/allocation rules; setup does not require gratuitous ordinary key regeneration.

Require the complete ordinary application and a real unused package for the exact current suite, with valid native credential/signing-key bindings, KeyPackageRef and lifetime. This does not make Alice a sender on Bob's stream or waive his creator evidence. Match the publication/allocation's actual mailbox, account, local custody and peer restrictions to this exact Bob principal/device and request branch. The signed confirm itself restricts this supplied package to the exact retained branch and its responder principal/device; Bob retains that original signed restriction with the wrapper. It is not an unrestricted passive publication. A publication restricted to someone else, already consumed, allocated to another branch, withdrawn, expired, or lacking required local receiving secrets is ineligible.

The request's explicit grant to seal offer/finish remains attached only to the temporary key. The receiving assertion grants only its **already defined ordinary sealed-control-v2 receiving role**. Neither its presence nor its carriage here grants its key the new mailbox-return control purpose. Confirm remains encrypted to Bob's original offer key through that offer's explicit bounded return-purpose grant; finish remains encrypted to Alice's temporary key. An ordinary invitation later uses the independently eligible ordinary receiving key and normal sealed2 rules. No fallback to the temporary key is allowed.

All original whole-body/no-`l`/sole-From/exact-domain DKIM, unknown-ingress policy, disclosure, candidate quarantine, fresh private challenge, current pin, ambiguity, credible-time, account and route checks remain. An assertion/package does not prove mailbox access. Bob must verify the original private challenge answer in leg 3 before any Alice association effect. Alice must verify her private challenge answer in leg 4 before any Bob association effect. No request-only or offer-only operational pin is introduced.

### One allocation and one durable transition

Alice's leg-3 transaction reserves one exact eligible ordinary receiving package/allocation for the branch, retains the original receiving wrapper and its digest plus independently recorded ordinary control/package custody promises, and commits them with the challenge, signed confirm, ciphertext and one outbox. It never holds an unfrozen advertisement pointer that can resolve to newer bytes at retry time. Failure before commit publishes nothing. Crash recovery recovers the same outcome, not another package.

The ordinary package is reserved for at most one actual admission by this Bob device under this branch and its original allocation realm. It is not a reusable invitation to create arbitrary streams. If current accepted allocation semantics cannot express that peer-restricted allocation, implementation must first add the owning allocation record; an assertion signature alone is not evidence of reservation. Local storage must join the existing single-use/cross-path package ledger, rather than creating a new namespace for this profile.

Bob's leg-3 acceptance atomically retains exact original receiving evidence and its allocation restriction, records his completed Alice address-return observation, and reserves one final response committing that exact digest. Any unsupported/missing/invalid receiving evidence holds/rejects the whole leg-3 transition; it cannot commit proof plus send a success-like finish while quietly lacking the mandatory reciprocal evidence. Parsing failures do not install conflict facts. Authenticated unequal leg-3 variants for the same branch retain conflict and hold affected new effects, rather than picking the first replacement package. Leg-4 mismatch fails before Alice's proof/handoff effects.

### Admission and retirement

Alice's package is not consumed by transmitting confirm, receiving finish, or creating her own initial stream. Bob consumes it only in his separately authorized actual admission under the current common staging/retirement/outbox contract. Alice validates Bob's resulting invitation against that exact unused allocation and her retained receiving secrets. Reservation, admission consumption and receiving secret retirement remain different transitions. The same package cannot be offered to another Bob device, Carol, another acquisition path or a second return stream. Such cases obtain independently eligible packages under their own bounded setup, without borrowing this branch's proof or allocation.

The acquisition attempt's `notAfter` never changes. Offer/confirm/finish creation and submission must still fit its original interval and all applicable keys and authorities. Alice's ordinary receiving assertion/package/control key keep their **own original** publication/lifetime/receive-until bounds; their start need not predate the original request, but they must cover actual required creation/release and admission receiving intervals. Bob's later ordinary send needs current evidence then; it does not extend a package lifetime to make “ready” permanent.

Cancellation, expiration, rollback uncertainty or a final message lost in transit does not reclaim an already exposed package for reuse or erase uncertainty. An unconsumed exposed reservation remains unavailable for any new allocation and retires under its original custody/deadline schedule. No invented acknowledgment is needed to release it for reuse. Receiving secrets cannot be destroyed early merely because the temporary attempt key/challenges can retire: Bob may already have staged/sent a legitimate invitation inside the original promise. Actual cancellation/withdrawal policies and current authority still govern later admission. Keep exact references, outcomes, consumption/conflict tombstones and original receiving deadlines for replay safety; a restore cannot manufacture unused status.

:::

## Acceptance boundary

An implementation needs to demonstrate the complete exchange and the failures that would otherwise give false confidence. The cases below remain acceptance obligations, not reported successes.

::: {.details summary="Required positive and adversarial demonstrations"}

These are planned acceptance requirements, not executed mail/provider evidence.
The same actual request/offer/confirm/finish signatures, HPKE, native assertions,
DKIM and durable state must be used for positives and negatives.

| Case | Required result and discriminating counterfactual |
| --- | --- |
| Complete four legs where Alice’s initial creator assertion has no joining package | Confirm supplies her separate valid unused package; each side creates its own stream and exchanges an encrypted human reply through full native admission and transport |
| Missing/changed receiving advertisement, digest, package, actor or final commitment | Strict schema/signature/native/allocation/transcript failure before the corresponding local proof/finish effect; no remembered or temporary-key substitute |
| Consumed, cross-branch, wrong-peer or duplicate Alice package | No second allocation or admission; exact retries recover one retained outcome and preserve uncertainty |
| Bob’s valid return invitation precedes Alice’s finish | Pending only; no Bob association or human effect at Alice until her private challenge proof and current checks complete |
| Same-domain source signing oracle, Mallory owns introduced Alice key but cannot read claimed Alice mailbox (RFC4686§4.1.4) | Bob may reserve bounded offer; no operational Alice pin at request. Without obtaining Bob's fresh private challenge, Mallory cannot produce a valid confirm. Counterfactual request-only selection must demonstrate the victim identity race |
| Same-domain Bob signing oracle plus copied/intercepted clear request, no access to Bob's return mailbox | Mallory can know public nonce/assertion and create offer. Alice remains candidate-only at offer; she sends fresh private challenge only to Bob. Without its value Mallory cannot finish. Omitting final leg or treating the original public nonce as Bob proof must fail the assurance test |
| A known public/cached/duplicated MLS KeyPackage or assertion is used as proof | Reject as mailbox-return evidence. The attacker can know it independently of return-mail receipt; the positive requires dedicated private challenge |
| Response ID, ciphertext hash, exposed encapsulated key or request digest is echoed instead | Reject as the answer; none is the exact retained private challenge. A copied response cipher plus matching device key is route interception, not evidence of exclusive mailbox ownership |
| APPEND of current valid request through write-only mailbox access | Enabled unknown-ingress policy can permit only bounded candidate offer. No pin at request; attacker still needs the secret sent to the claimed source address. Known local import/history path initiates nothing |
| Forward to wrong target, list expansion or nested request | Wrong selected target/To or forbidden List/nesting fails; no automatic response, alias inference or group membership. A legitimate exact target acquiring a forwarded original still performs the full private round trip |
| Replay across SMTP/APPEND/folders/account reconnect/aliases/restart (RFC4686§4.1.5) | Same root/branch/step outcomes, deadlines, challenge, package and outbox identity; no new automatic submission or timer. Replaying original nonce does not satisfy either challenge |
| Device/principal/key/advertisement/digest/step transplanted from another branch | Exact signed transcript/actor/key checks fail before effects. Shared address does not allow one Bob device to prove another |
| Valid old intent paired with expired/withdrawn control key or role gap | No decryption/use or new preparation under a hidden renewal. Original time and current authority/receiving promises remain independently enforced |
| A different unproved candidate races a real victim | Neither request nor offer wins an operational pin; complete local observations are evaluated under the existing full candidate set and ambiguity/current-generation boundary |
| Pin/disclosure policy tightens, account mapping changes, cancellation or restore occurs during crypto/SMTP wait | Final serialized/release checks hold unsent work. Submitted uncertainty remains; no false recall or silent auto-send after cancellation |
| Finish lost after Bob accepted confirm | Bob's Alice-route observation and exact finish outbox remain; Alice stays pending. No infinite ACK and no global “both received” claim |
| Bad DKIM, l=0/equal-length l, unsigned/multiple From, bad target or copied Authentication-Results | No new path around actual full no-l/sole-From/exact-domain/current-assertion checks |
| Bounce, ordinary setup2 response, malformed/unknown kind or terminal finish | No automatic new handshake leg, error reply, refresh or cancellation mail |
| Automatic responder quotes attacker-chosen control/body to obtain an innocent-domain signature (RFC4686§4.1.4) | Only bounded fixed-purpose proof is emitted, encrypted; no human quotation or general signed echo. Still retain domain-signing-oracle and ciphertext-replay limits |
| Signed control replayed intact under changed SMTP envelope or a preserving list (RFC4686§4.1.5) | DKIM may still pass; exact target/transcript/branch and once-only reservation govern effects. Domain signature proves neither local-part ownership nor receipt/intent |
| Ordinary exact-source MAIL FROM causes a DSN/vacation reply or coexists with a legacy responder | No Email/2 step reactivation, no reallocation and no automatic retry from the reply; test actual account behavior. Residual outside-protocol automatic traffic/loops are acknowledged rather than declared impossible |
| First use reaches local route completion | No human identity badge, no content/history/contacts, no group/list enrollment and no ordinary send unless separate native setup/intent/outbox gates authorize it |

A real compatibility demonstration must run every leg through actual unchanged
SMTP submission and authenticated IMAP retrieval, including the signing-oracle
forced-MAIL-FROM difference and APPEND alternative. A local serialized mailbox
loop is useful state-machine testing, but is not that demonstration or independent
provider/security evaluation.

:::

## Complete the protected send

A completed local observation has scope `addressed-control-return` and outcome
`address-return-observed`. A client can describe it as “Address round trip checked.”
It records the honest local issuer, exact remote principal/device/mailbox,
original request/branch/transcript commitments, checked time and retained outcome.
It is not a transferable ownership certificate, read receipt or verified-person
badge. The [association rules](mailbox-association.md#address-and-observation-inputs)
can select `associated-unverified` only when current policy permits; independent
human verification remains separate.

Bob has Alice’s ordinary receiving package at step three; Alice has Bob’s from
step two but cannot use it operationally until step four completes her local proof.
A valid Bob invitation arriving before Alice’s finish stays pending and cannot
substitute for her private challenge answer. Both sides recheck current evidence
before [native admission and the protected outbox handoff](first-contact-setup.md#finish-setup-for-one-intended-send).
Setup does not create a human reply intent, parent message or group membership.
A reply still waits for its actual parent and selected reply policy where required.

The [transport release rules](transport.md#local-authorization-and-release) and
[secret-retirement rules](setup-secret-retirement.md#fixed-deadlines-including-unused-setup)
apply independently. Lost mail remains pending or uncertain, expiry does not
restart setup indefinitely, and no failure silently releases plaintext.
