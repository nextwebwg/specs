---
title: IMAP4rev1 compatibility audit
sectionNav: true
---

# IMAP4rev1 compatibility audit

An Email Next client can read an existing IMAP4rev1 mailbox without changing the messages stored there. It retrieves the original message, verifies any protected contribution and builds the conversation locally. The server's folders, flags and search results help find messages; they do not authenticate the conversation.

[RFC3501](https://www.rfc-editor.org/rfc/rfc3501.html) defines this older access protocol. Its replacement, IMAP4rev2, has a [separate audit](imap-access.md). Reviewing rev2 does not establish rev1 compatibility: commands, string encodings and synchronization behavior differ.

> [!ex] A new-message check returns an old message
> A client asks for UIDs from its saved next-UID value through `*`. When no new message has arrived, that range can still include the mailbox's last existing message: range endpoints work in either order. The client checks the returned UID before treating it as new, and independently deduplicates its authenticated contribution.

The complete RFC3501 base text, its grammar, all appendices and seven listed errata are covered below. This is source review of an optional adapter, not an implemented or independently tested IMAP connection. The configured conversation demonstration uses its own local SMTP path; this audit does not add an IMAP backend.

## What the adapter must preserve

The [mailbox integration contract](../mailbox-integration.md#imap-access) owns Email Next's adapter requirements. RFC3501 adds several compatibility details that matter when implementing them.

A stable mailbox reference combines the server and account, mailbox name, UIDVALIDITY and UID. Neither a sequence number nor a UID alone is durable. UIDNEXT is a prediction, not a reserved message identifier. `Recent` is especially unsuitable as a synchronization cursor: simultaneous connections need not see it on the same messages. Missing compatibility metadata prevents relying on the associated cache; it does not authorize inventing a UIDVALIDITY.

Retrieve the bytes required by the protection profile with non-marking operations such as `BODY.PEEK[]`. An IMAP ENVELOPE is a parsed projection with defaulted fields, not the SMTP envelope or the original headers. In particular, it has no References field. Fetch the original headers when reconstructing ordinary reply relationships, and verify protected relationships independently.

An APPEND can reversibly convert eight-bit data to a seven-bit MIME representation. Consequently, a successful store is not proof that the stored bytes equal the upload. An adapter must retrieve and check the representation required by its protection profile before reusing an authentication result. A permitted MIME transfer-encoding change may preserve the exact decoded protected payload or event bytes while changing outer MIME bytes. That can preserve the particular payload verification without proving byte-identical mailbox storage or the exact original SMTP representation. APPEND also has no SMTP envelope and does not deliver mail.

Mailbox deletion is separate from conversation withdrawal. `CLOSE` can remove all messages already marked deleted, including another client's changes, without reporting individual expunges. Selecting another mailbox, examining one or logging out does not implicitly expunge. A rev1-only adapter must not assume that the newer `UNSELECT` command exists.

## Keep protocol versions explicit

Base rev1 supports polling with NOOP. `IDLE`, `UNSELECT`, `MOVE` and `BINARY` are separate extensions, not commands implied by an `IMAP4rev1` capability. Authenticate the connection, refresh capabilities at the required security boundaries, and use an extension only under its own negotiated contract. Neither an access capability nor an IDLE notification proves that the other person supports Email Next or is online.

Rev1's mailbox internationalization convention uses modified UTF-7. Its base grammar does not accept arbitrary UTF-8 headers or binary NUL-containing literals. Do not send rev2 strings, non-synchronizing literals, SASL initial responses or saved-search syntax just because another supported protocol uses them. Internationalized message access needs its applicable UTF-8 extension and a complete-message retrieval policy; a legacy downgraded view cannot establish verification of the unavailable original.

The historical TLS 1.0, RC4 and older certificate-matching instructions in RFC3501 are not current security defaults. Apply the separately reviewed [access TLS policy](submission-access-tls.md), [TLS version deprecation](tls-deprecation.md) and [service discovery rules](service-discovery.md), including their identity-check dependencies. An encrypted conversation does not make an unauthenticated mailbox connection safe.

:::: {.details summary="Section-by-section dispositions"}

Grouped rows give a disposition for every named section, including its examples and unnumbered lists. The grammar is reviewed alongside the command and response text, rather than treating examples as complete fixtures.

| Sections | What carries into Email Next |
| --- | --- |
| Front matter, abstract, contents | Access and synchronization only; sending belongs to the transport contract. Historical publication status is not a deployment claim. |
| 1, 1.1–1.3 | Read prose, responses and grammar together. Connection and selected-mailbox session differ. Older fetch aliases and older protocol compatibility are explicit boundaries. |
| 2, 2.1, 2.2 | Reliable-stream framing and CRLF do not supply confidentiality or event authentication. |
| 2.2.1, 2.2.2 | Tags correlate completions; unsolicited data can interleave. Finish continuation exchanges before starting another command. |
| 2.3, 2.3.1, 2.3.1.1 | Cache the scoped unsigned UID/UIDVALIDITY pair; preserve immutable message identity across sessions and mailbox-name reuse. UIDNEXT is only a lower bound for later arrivals. Apply verified erratum 261. |
| 2.3.1.2 | Sequence numbers renumber immediately on expunge and cannot identify durable conversation events. |
| 2.3.2 | System flags, keywords and session/permanent flags differ. Seen/Answered are mailbox state, not authenticated receipts or structured answers. Recent cannot be set by the client and is ambiguous across connections. |
| 2.3.3–2.3.6, 2.4 | Internal date, encoded size, parsed envelope/body structure and selected texts have distinct meanings. Obtain the protected verification input, not a convenient projection. |
| 3, 3.1–3.4 and flow diagram | Track authentication and selected-mailbox states. Failed selection can deselect; normal logout reads BYE and tagged completion before closing. |
| 4, 4.1, 4.2 | Parse atoms and numeric domains in context. Numeric grammar is unsigned 32-bit; never infer a signed integer domain from the old prose. |
| 4.3, 4.3.1 | Literal length counts octets. Even a zero-length client literal needs continuation. Base rev1 forbids NUL-containing strings; MIME transfer encoding is not an authenticated transformation by itself. |
| 4.4, 4.5 | Preserve nested lists and context-specific distinctions between NIL, an empty string/list and a mailbox named NIL. |
| 5, 5.1 | INBOX is case-insensitive; other mailbox case behavior is server-specific. Names and wildcards are not filesystem paths. |
| 5.1.1, 5.1.2 | Use the returned hierarchy delimiter and respect namespace conventions. A namespace is not conversation membership. |
| 5.1.3 | Keep modified UTF-7 shifts, alphabet and encoded-case rules exact, with erratum 261. Do not apply mailbox decoding to signed message bytes. |
| 5.2, 5.3 | Record size changes and unsolicited state. EXISTS cannot shrink a mailbox; base rev1 prohibits unsolicited EXPUNGE when no command is in progress. |
| 5.4 | The corrected minimum idle timeout concerns authenticated sessions. It is not peer presence or an Email Next keepalive default. |
| 5.5 | Do not pipeline operations whose results depend on one another. UID operations permit expunge; a UID SEARCH can still contain sequence-number criteria. Apply erratum 261. |
| 6, 6.1, 6.1.1 | Command state, BAD/NO and capability-use rules govern the exchange. Advertisement does not enable incompatible behavior. |
| 6.1.2, 6.1.3 | NOOP checks mailbox changes; LOGOUT has an ordered completion. Neither confirms a human action. |
| 6.2, 6.2.1 | STARTTLS keeps the connection unauthenticated and invalidates earlier capabilities. Verify transport identity before credentials; no plaintext fallback from a failed upgrade. |
| 6.2.2 | Preserve SASL continuation, cancellation, strict base64 and security-layer transition boundaries. Base rev1 has no SASL initial-response argument. Historical suggested mechanisms are not a current security policy. |
| 6.2.3 | Respect LOGINDISABLED and protect credentials; account authentication is separate from contribution authorship. |
| 6.3, 6.3.1, 6.3.2 | Retain selection metadata, including conditional UNSEEN under erratum 3032. EXAMINE forbids permanent per-user changes; read-only SELECT has different allowances. Missing old-server metadata requires the specified compatibility fallback. |
| 6.3.3–6.3.5 | Create/delete/rename must preserve UID identity guarantees and child-mailbox rules. INBOX rename moves its messages but leaves its children. Deleting a mailbox does not retract contributions elsewhere. |
| 6.3.6, 6.3.7 | Subscriptions are account preferences and can name absent mailboxes. Their presence does not grant access or imply group membership. |
| 6.3.8 | LIST reference/wildcard interpretation can hide accessible mailboxes. An empty pattern requests delimiter/root information, not all messages or folders. |
| 6.3.9 | LSUB can return synthetic parent names and stale subscriptions; prefer LIST attributes when they conflict. |
| 6.3.10 | STATUS does not select or mutate the mailbox and is not selected-mailbox polling. The corrected contract requires its STATUS response. |
| 6.3.11 | APPEND stores one message, can re-encode eight-bit input and rolls back failed appends. It cannot submit SMTP recipients. Treat draft exceptions carefully, not as permission to send invalid protected messages. |
| 6.4, 6.4.1 | CHECK requests server housekeeping; it is not a reliable new-message poll or conversation checkpoint. |
| 6.4.2, 6.4.3 | CLOSE and EXPUNGE can remove other clients' deleted messages. Reconcile renumbering and Recent counts; do not turn deletion into an authenticated withdrawal. |
| 6.4.4, every listed search key | Search combines criteria and may omit non-text/non-message MIME terminals. Decode comparisons under erratum 261. String search is case-insensitive substring matching, date searches ignore time/zone, flags remain mutable, and empty HEADER search tests presence. None proves exact identity or complete history. |
| 6.4.5, every fetch item and part-number example | BODY.PEEK avoids implicit Seen changes. Preserve original section bytes, exact MIME nesting, header-subset boundaries and partial-fetch offsets. A truncated response cannot verify a complete object. RFC822 fetch aliases have explicit rev1 meanings. |
| 6.4.6, all FLAGS variants | STORE mutates flags, not message content. SILENT does not suppress unrelated updates; replacement can overwrite concurrent state. |
| 6.4.7 | COPY creates another mailbox record, preserves specified attributes and rolls back failed copies. A copy is not a new authenticated event. |
| 6.4.8 | Missing UIDs yield successful no-ops. FETCH prefixes remain sequence numbers and UID-command FETCH responses include UID. Ranges are order-independent, including `n:*`; inspect returned UIDs. |
| 6.5, 6.5.1 | Experimental commands and associated responses require explicit invocation. An X-prefixed capability is not a hidden message-discard mechanism. |
| 7, 7.1 and all response codes | Process state separately from tagged completion. Machine-readable codes govern recovery; human text and ALERT do not authenticate a correspondent. Unknown codes must not grant authority. |
| 7.1.1–7.1.3 | Untagged OK/NO/BAD do not directly determine the outstanding command result; preserve the matching tagged completion. |
| 7.1.4, 7.1.5 | PREAUTH is account state, not proof of secure transport. On an unprotected connection it leaves no base STARTTLS opportunity: close when required transport protection is absent. BYE handling differs between normal logout and failure; reconcile outcomes after disconnect. |
| 7.2, 7.2.1 | Capabilities apply to this server connection and can change after authentication or TLS. Unknown names are ignored. |
| 7.2.2–7.2.4 | Respect LIST selectability combinations under erratum 261, hierarchy delimiters and LSUB differences. STATUS data belongs to the named mailbox. |
| 7.2.5, 7.2.6 | SEARCH results use sequence numbers or UIDs according to the command. Record available FLAGS separately from permanent-write permissions. |
| 7.3, 7.3.1, 7.3.2 | Record EXISTS and RECENT updates. Recent messages need not be a contiguous suffix and do not prove new authenticated events. |
| 7.4, 7.4.1 | Renumber immediately for each EXPUNGE and enforce its command-interleaving restrictions. |
| 7.4.2, every FETCH result component | Parsed defaults, source-route/group address projection, encoded body sizes and extensible BODYSTRUCTURE are useful display/index data. BODY location is a string under erratum 261. Content-MD5 is not secure event authentication. ENVELOPE omits References. |
| 7.5 | Wait for continuation before literal bytes and preserve the command remainder after the counted octets. |
| 8 | The transcript is illustrative. It lacks UIDNEXT/PERMANENTFLAGS selection data and shows password login without a transport setup. It is not a modern secure conformance fixture. |
| 9, complete grammar and comments | Reconcile spaces, case, list nesting, literal lengths, numeric bounds, section syntax and correction 261. Do not extend fixed ENVELOPE shape from held erratum 6637. |
| 10 | Lineage does not imply support for obsolete commands or current suitability of old security dependencies. |
| 11, 11.1, 11.2 | Apply current transport/certificate policy instead of obsolete TLS algorithms. Protect credentials, limit guessing and avoid user-enumerating errors. End-to-end encryption remains a separate layer. |
| 12 | Existing IMAP capability and SASL service registrations are not new Email Next assignments; erratum 261 adds the service-name registration clarification. |
| Appendix A, A.1 | References identify dependency work; their presence is not a full review of their bodies. Correct the body-language reference under erratum 261. Historical compatibility references do not expand the optional adapter. |
| Appendix B, changes 1–114 | Cross-check change notes against normative text and grammar. Later removal of NEWNAME supersedes its earlier addition; do not implement an obsolete intermediary change. Erratum261 adds change 115 for Content-Location. |
| Appendix C | The keyword index is navigation, not a separate command definition. Resolve each entry through the corresponding command, response and grammar rules. |
| Author address, copyright and acknowledgement | Attribution and licensing only; no additional adapter behavior. |

::::

:::: {.details summary="Errata and extension boundaries"}

### Errata dispositions

The [current RFC Editor listing](https://www.rfc-editor.org/errata/rfc3501) contains seven records. Verified corrections, held suggestions and rejected changes have different authority.

| Record | Status | Disposition |
| --- | --- | --- |
| [261](https://www.rfc-editor.org/errata/eid261) | Verified | Apply its complete correction set: unsigned UID metadata; modified base64 alphabet; authenticated-session idle timeout; expunge and UID SEARCH concurrency; post-TLS capabilities; invalid SASL base64; DELETE child handling; required STATUS response; Recent count after expunge; decoded search/empty substring and literal continuation; LIST attribute exclusion; single-string body location; charset and sequence-set grammar; nonzero UID status values; SASL registration; language reference and change 115. |
| [3032](https://www.rfc-editor.org/errata/eid3032) | Verified | UNSEEN is required only when unseen messages exist. Its absence must not become an invented first-unseen sequence number. |
| [3093](https://www.rfc-editor.org/errata/eid3093) | Held for Document Update | Lowercases draft-exception wording in APPEND; no new message-validity guarantee. |
| [3445](https://www.rfc-editor.org/errata/eid3445) | Rejected | Retain old-server fallback for missing selection metadata, while keeping current server requirements. Rejection notes explain that the fallback is intentional. |
| [6160](https://www.rfc-editor.org/errata/eid6160) | Held for Document Update | Removes a stray word in the charset registration comment. It does not undo correction 261's charset grammar. |
| [6637](https://www.rfc-editor.org/errata/eid6637) | Held for Document Update | Suggests adding References to ENVELOPE. Do not emit or assume an extra field in the existing fixed wire structure; retrieve References from original headers. |
| [6636](https://www.rfc-editor.org/errata/eid6636) | Rejected | Later replacement of the message-format reference was not an error at RFC3501 publication. Apply current message-format requirements through their own specification. |

### Updates and optional extensions

[Official metadata](https://www.rfc-editor.org/info/rfc3501) identifies thirteen direct updates. The table distinguishes already reviewed security/discovery dependencies from optional extensions whose full audits remain separate. No extension-support claim follows from this base review.

| Update | Adapter boundary |
| --- | --- |
| [RFC4466](https://www.rfc-editor.org/rfc/rfc4466.html) | Consolidated extension ABNF, including some RFC3501 errata. Audit its grammar and later updates before implementing a combined extension parser; metadata inspection is not that review. |
| [RFC4469](https://www.rfc-editor.org/rfc/rfc4469.html) | CATENATE is optional server-side composition. Not selected by the base retrieval adapter; composed protected bytes still need verification. Later update RFC5550 needs separate disposition if adopted. |
| [RFC4551](https://www.rfc-editor.org/rfc/rfc4551.html) | Replaced by RFC7162. Do not implement a new CONDSTORE profile from the superseded text alone. |
| [RFC5032](https://www.rfc-editor.org/rfc/rfc5032.html) | WITHIN adds relative-time search; optional discovery aid, not authenticated freshness or ordering. |
| [RFC5182](https://www.rfc-editor.org/rfc/rfc5182.html) | SEARCHRES saves connection-local results. Not base rev1 syntax; requires its own concurrency and invalidation tests. |
| [RFC5738](https://www.rfc-editor.org/rfc/rfc5738.html) | Replaced by RFC6855, then RFC9755. Review the current UTF-8 extension before enabling internationalized rev1 access; rev2 includes its functionality separately. |
| [RFC6186](https://www.rfc-editor.org/rfc/rfc6186.html) | Reviewed in [service discovery](service-discovery.md), with later updates. Service location does not establish correspondent identity or authorize credential forwarding. |
| [RFC6858](https://www.rfc-editor.org/rfc/rfc6858.html) | Legacy internationalized-message downgrading can substitute a view. Full extension review remains required if supported; unavailable original bytes cannot be called verified. |
| [RFC7817](https://www.rfc-editor.org/rfc/rfc7817.html) | Reviewed identity-check update in the [mail-service identity audit](mail-service-identity.md); do not use RFC3501's older name-matching procedure. |
| [RFC8314](https://www.rfc-editor.org/rfc/rfc8314.html) | Reviewed current access/submission TLS policy, including update 8997, in the [access TLS audit](submission-access-tls.md). Cleartext is not an automatic interoperability fallback. |
| [RFC8437](https://www.rfc-editor.org/rfc/rfc8437.html) | UNAUTHENTICATE is optional administrative connection reuse. A new account context must never inherit the prior account's cache or authority; full extension review is separate. |
| [RFC8474](https://www.rfc-editor.org/rfc/rfc8474.html) | OBJECTID can improve cache reuse across moves/renames. Provider object identity still cannot replace authenticated event identity; full extension review is separate. |
| [RFC8996](https://www.rfc-editor.org/rfc/rfc8996.html) | Reviewed [TLS 1.0/1.1 deprecation](tls-deprecation.md). Historical mandatory TLS algorithms do not set this adapter's security floor. |

Other optional features mentioned by the adapter are defined separately: [IDLE](https://www.rfc-editor.org/rfc/rfc2177.html), [BINARY](https://www.rfc-editor.org/rfc/rfc3516.html), [UNSELECT](https://www.rfc-editor.org/rfc/rfc3691.html), [MOVE](https://www.rfc-editor.org/rfc/rfc6851.html), [CONDSTORE/QRESYNC](https://www.rfc-editor.org/rfc/rfc7162.html) and [UTF-8 for rev1](https://www.rfc-editor.org/rfc/rfc9755.html). Their metadata and applicability were inspected; their complete bodies and errata are not covered by this chapter's base-text review. Authentication mechanisms and implementation recommendations likewise retain their own review obligations.

::::

## Evidence needed before claiming rev1 support

An implemented adapter needs transcripts against actual rev1 servers, separate from rev2 negotiation tests. Cover empty and concurrent mailboxes, missing compatibility metadata, changed UIDVALIDITY, reversed UID ranges, literal rejection/continuation, expunge during UID operations, modified UTF-7, search false positives, partial retrieval, APPEND representation changes and uncertain outcomes after disconnect. Preserve controls as inactive until all required protected bytes are available and verified.

An extension claim additionally needs its complete source/update/errata review and applicable acceptance cases. No ordinary IMAP command requires legacy clients to hide an Email Next negotiation message. Cross-provider operation and independent implementations remain external evidence to obtain through the [adoption plan](../adoption.md).
