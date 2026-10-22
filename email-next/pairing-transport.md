---
title: Carrying a device-pairing exchange
order: 9.6
blurb: QR-bound rendezvous · exact retries · encrypted configuration
sectionNav: true
---

# Carrying a device-pairing exchange

The two devices can exchange pairing records through a chosen HTTPS relay. Scanning codes binds the exchange to those devices; the relay only carries records. It cannot approve enrollment or turn a downloaded file into trusted account setup.

The relay can see the account's public pairing records, including mailbox claims, and connection metadata. Contact/security configuration stays encrypted for the new device. Select a relay permitted to see that pairing metadata; this transport does not promise anonymous pairing or conceal the account from its chosen relay.

> [!ex] Scan, approve, finish setup
> The existing device creates an offer and displays its code. The new device scans it, downloads the matching offer, creates its own device key and displays a return code. The existing device scans that code and approves the exact device request. After the new device accepts enrollment, the same exchange carries the confidential setup request, encrypted response and staged/installed receipts. Mailbox login and usable peer setup remain separate readiness gates.

## Bind the relay to the scanned offer

:::: {.details summary="Rendezvous registration, transport descriptor and both QR records"}

`pairing-rendezvous-v0` is an application transport, not a new identity or cryptographic protocol. It carries the original [pairing records](identity-lifecycle.md#independent-confirmation) and [confidential setup records](identity-lifecycle.md#confidential-security-configuration-transfer) without changing their signatures, commitments, authority or timers. Current-suite use still requires the owning state1/current-authority validators; older state0 experiments are not complete implementation evidence.

A trusted local relay selection supplies a canonical HTTPS `service` origin and same-origin `prefix` under the [service URI grammar](service-answers.md#binding-the-action-to-the-service). Prefix ends in `/` and designates this transport's session collection; clients do not guess it. The native client uses the selected TLS service-identity/status/protocol rules, no redirects, no ambient cookies/credentials and no message-origin referrer. A received email cannot install a relay or start pairing. QR import is permitted only in the deliberately opened own-device pairing flow with its independent confirmation; it is not ordinary URL navigation or a generic trust-import handler.

Generate a fresh nonzero 32-octet lowercase-hex session under the pairing offer's existing grammar. Generate independent owner and target tokens from 32 cryptographically random octets, canonical unpadded base64url (43 ASCII characters, exact decode/re-encode). Retain tokens and immutable request bytes in protected local setup storage before publishing anything. Owner token stays on the approving device. Target token is carried in the first code; it grants only this session's target slot access, not identity, mailbox or provider authority. A source cannot infer good randomness from spelling alone.

QR payloads use the strict event JSON/scalar/depth rules and at most 2048 UTF-8 octets. Encode the complete original bytes with an adequate QR size/error-correction setting; never truncate a commitment or substitute a short URL. The accessible alternative transfers the complete original UTF-8 descriptor through an independently authenticated channel and compares the full commitments. Copying parsed fields into a differently serialized descriptor does not preserve transportDigest; expose the original descriptor for that handoff rather than asking the person to reconstruct JSON. This is a setup wire-processing bound, not a storage quota.

The first QR payload is exactly `{version,purpose,service,prefix,session,token,offerDigest,anchorBundleDigest,notAfter}`. Version is `"0"`, purpose `"pairing-rendezvous-offer"`; token is the target token. OfferDigest uses the existing full 256-bit pairing-offer commitment; anchorBundleDigest is SHA256 of the exact public anchor-bundle bytes. NotAfter is this transport lease's canonical uint64 epoch seconds. The approving device retains the exact UTF-8 QR bytes. Define transportDigest as SHA256 of ASCII `email2/pairing-rendezvous-qr/v0`, NUL, U32 big-endian length and those original bytes.

After the new device independently confirms this first code, it fetches the offer/anchor, compares both exact commitments, and validates the existing pairing account/anchor/binding rules. It creates and retains its own request and possession proof before uploading. Its return QR is exactly `{version,purpose,service,prefix,session,transportDigest,offerDigest,requestDigest,notAfter}`, with `"0"`, `"pairing-rendezvous-request"` and the existing full pairing-request commitment. All route/lease/offer fields must equal the retained first descriptor. No shortened comparison, provider login or same-relay copy substitutes for scanning/independently confirming all commitments.

The approving device fetches the original request, matches that return code and its retained transport descriptor, validates possession/account/current authority and obtains the existing enrollment approval. Merely fetching or recognizing a return code does not approve. Changing origin, prefix, session, token, commitment or lease requires a new independently confirmed exchange; neither a redirect nor a service error can authorize it. Both codes and tokens are sensitive setup material: no telemetry, public journal, emailed fallback or QR URL query carries them.

::::

## Store and retrieve exact records

:::: {.details summary="Session creation, role-specific HTTPS routes and immutable slots"}

Let root be `prefix + session`, with the exact ASCII session spelling. No query or fragment is permitted on any HTTP route. All requests/responses use no-store and bounded fixed representation bytes; JSON is strict UTF-8, duplicate names rejected, scalar/depth rules inherited. No content coding is selected. The transport's encoded JSON body/response ceiling is 4194304 octets and depth 32; smaller finite local budgets may refuse the operation but cannot truncate a record. Tokens occur only in their required protected setup storage/QR and TLS transport, never a slot body, receipt, locator or diagnostic, except the creation body's independently generated targetToken below.

Create with `PUT root`, owner token in `Authorization: Bearer <owner token>`, and exactly `{version,purpose,offer,anchor,targetToken,notAfter}`. Version is `"0"`, purpose `"pairing-rendezvous-create"`. Offer and anchor are canonical padded base64 of original strict JSON bytes, each at most 1048576 decoded octets. The offer session and anchor digest must match its declared values; a malformed object or mismatch is400. This structural check does not validate ownership. NotAfter is the immutable transport lease and must not precede the offer's session deadline. It is independent of the much longer device-grant lifetime.

Creation requires an unused random session; service policy may refuse allocation under its finite abuse/storage/lease budgets. Anonymous random-session creation is allowed by this transport and supplies no account authority. The service records owner/target token hashes, exact creation bytes protected at rest, lease and empty slot inventory atomically. Return201 with exactly `{version:"0",purpose:"pairing-rendezvous-created",session,requestDigest}`, digest SHA256 of original creation bytes. Same owner/current authorized exact retry returns the retained receipt with200; changed bytes under that identity conflict409. A foreign existing session reveals no record and is404. A lost response does not authorize publishing a different offer under the same session.

GET root requires either role token and returns exactly `{version:"0",purpose:"pairing-rendezvous-record",offer,anchor,notAfter}` from the original creation. It never returns the target/owner credential. Clients validate their retained commitments, not simply HTTP200. The remaining routes are:

| Suffix under root | PUT authority | GET authority | Exact stored representation |
| --- | --- | --- | --- |
| `/request` | Target | Owner | Original pairing request bytes |
| `/result` | Owner | Target | Original pairing enrollment-result bytes |
| `/setup-request/{transfer}` | Target | Owner | Original signed confidential-setup request wrapper |
| `/setup-response/{transfer}` | Owner | Target | Original signed response wrapper containing encrypted configuration or the version1 encrypted manifest |
| `/setup-part/{transfer}/{index}` | Owner | Target | Original signed encrypted part under the selected [selected configuration contract](paired-configuration.md); canonical uint64 index |
| `/setup-receipt/{transfer}/staged` | Target | Owner | Original signed staged receipt |
| `/setup-receipt/{transfer}/installed` | Target | Owner | Original signed installed receipt |

Transfer is the existing nonzero ObjectId. Staged/installed are separate immutable slots, not permission to replace an old receipt. The relay accepts bounded JSON data but does not claim that a signature, purpose, transfer or progression is valid: the owning validators match actual session/request/response references before effects. Unsupported future setup versions do not activate merely because they fit a slot.

PUT slots use `application/json` and original bytes, with no wrapping/reencoding. A first committed slot returns201; exact authorized replay200; changed bytes409 without replacing it. Successful PUT replies have exactly `{version:"0",purpose:"pairing-rendezvous-stored",session,path,requestDigest}`, where path is the exact suffix above and digest covers original slot bytes. GET returns those exact original bytes as `application/json`, never executing, consuming or acknowledging their meaning. Empty slots are404. A storage receipt is not enrollment, configuration staging/installation or send readiness.

Missing/invalid credential is401; a valid wrong role is403 without content; an inaccessible/unknown session is404. Expired retained sessions return410 only after credential validation; malformed input400, body bound413, exact-slot conflict409, capacity/rate refusal429 or503. Error bodies contain no records, credentials, contact data or executable instructions. HTTP failure, missing slot or410 is unavailable transport evidence, not proof that enrollment/configuration did not commit. Do not switch to ordinary email or a received callback URL.

The service enforces independent finite creation/connection/session/slot/byte/rate/retention budgets before expensive work. It does not send email, push or callbacks when records arrive, even if they contain an address. Thus an anonymous creator obtains a bounded rendezvous, not an anonymous messaging gateway to arbitrary recipients. A holder of a stolen target token can withhold/preempt slots; that denial cannot approve a different device without the full independent request confirmation. A dishonest relay can still deny service and observe metadata.

::::

## Expiry, disconnect and readiness

The transport carries the [current pairing identity binding](identity-lifecycle.md#current-pairing-and-multiple-administrators): unchanged exact pairing records contain the selected bundle1 evidence and state1 enrollment successor. Slot access and byte storage do not validate those objects or resolve concurrent administrator updates. A retained result retrieved after an interrupted session is historical evidence until the target completes current identity acceptance; it cannot roll back revocation or restart the expired lease.

The devices retain setup progress through interrupted connections and retry the same records. Expiry stops further use of the relay; it does not undo enrollment that already committed. Removing an enrolled device still requires the identity lifecycle.

:::: {.details summary="Lease, withdrawal, ciphertext privacy and acceptance obligations"}

The service lease is fixed at creation and enforced at each operation. Select it under finite local/service policy before creating/displaying the first code. Token use, slot writes, reconnect and polling cannot extend it. A setup request's entire validity must fit this remaining lease as well as its own source/target authority. The pairing offer's approval deadline and device-grant interval retain their separate checks. Retained results can describe completed enrollment after the offer deadline; the transport never renews enrollment permission.

Native clients poll only in their locally enabled session workflow, with one in-flight request per slot, finite bounded backoff/jitter and current lease/authority. No message opening, passive receipt or GET creates another pairing/setup request. Receiving the setup request does not authorize disclosure until the owning source validator passes; receiving encrypted configuration does not authorize installation until the target's original request and full reconciliation pass.

Owner-authorized `DELETE root`, with no body, disables all session reads/writes and both credentials before returning204. A retained owner-authenticated exact deletion retry may return204 from its revocation tombstone; it grants no renewed read. Purging relay bytes follows its stated retention policy and is not physical-erasure proof. Lost/unavailable deletion remains uncertain locally; neither party relies on it to revoke enrollment or recall already disclosed configuration. A new attempt uses a fresh session, tokens and confirmation without erasing prior uncertainty.

The confidential setup response retains the existing target-bound age encryption and source signature. Tokens/TLS authenticate only relay-slot access, never enrollment or configuration authority. Contact pins, verification, private context and policy must not be sent as an unencrypted generic slot payload. Only the current request/response/receipt formats selected by the owning configuration contract may use the setup routes. Public pairing/anchor/enrollment records are deliberately visible to this chosen relay; requiring their confidentiality needs a separately specified suitable carrier, and cannot be falsely advertised by this public-record transport. This boundary does not authorize public exports of correspondent configuration or ordinary Email/2 control proofs.

Readiness remains per contact/conversation: account access, actual current accepted enrollment, installed selected security configuration, usable fresh peer setup, chosen agreement, private-role provenance and actual admission/release checks. The transport receipt and even an installed configuration receipt are insufficient. Old message history is not a cryptographic setup/readiness prerequisite. Product access and pricing do not establish protocol authority.

Acceptance requires actual independent-code comparison, wrong origin/prefix/token/session/anchor/offer/request, role separation, same-slot byte conflicts, lost replies, lease boundary, concurrent PUT/DELETE, scanner/no-notification behavior, setup ciphertext substitution, cancelled/revoked authority and receipt replay without a second installation. Exercise native HTTPS framing and final source/target storage races. Existing local pairing, age setup/contact and protected SMTP cases cover their own cryptographic/application mechanics; they do not implement this public transport, prove camera/OS security, complete state1/configuration versions or establish QR-to-send readiness.

::::


## Reply-aware configuration slots

[Configuration2](paired-configuration.md#transfer-reply-aware-conversation-setup) reuses the confidential setup request/response/receipt and setup-part routes with their existing owner/target credentials, bounds and exact immutable transfer slots. Its original signed request selects version2 for its response, parts and receipts. Configuration1/0 requests cannot receive2 records under the same transfer, and a rejected2 record cannot be retried as1 to bypass validation. Source/target token access still grants only transport access, never enrollment, configuration authenticity or send readiness. A version change cannot create another lease, reset a deadline or reopen an occupied/cancelled slot. The relay carries the original signed encrypted records, not a decrypted configuration or client-supplied trust flags.


## Asynchronous configuration slots

[Configuration3](paired-configuration.md#transfer-asynchronous-scope-metadata) uses the same encrypted setup routes, original signed wrapper storage, owner/target token separation, individual bounds and immutable transfer/index slots. Its version3 request selects its exact configuration, manifest, parts and receipts. Older requests cannot receive3 records under an occupied transfer or treat a failed3 validation as2/1/0.

A new format grants no new relay lease, transport token, enrollment, trust-import permission or sending readiness. Whole selected configuration staging and source/target authority still precede scope effects. The lease-bound rendezvous carries this approved transfer; it is not an ongoing account-wide configuration service. Later metadata acquisition needs independently selected authority and transport, not reuse of expired session tokens or automatic retrieval of old human messages.
