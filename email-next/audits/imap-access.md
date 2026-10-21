---
title: IMAP4rev2 audit
sectionNav: true
---

# IMAP4rev2 audit

[IMAP4rev2](https://www.rfc-editor.org/rfc/rfc9051.html) already supplies selective message retrieval, mailbox change notifications and stable identifiers within a mailbox. These let a richer client work with existing servers. They do not provide peer presence, message submission, authenticated conversation membership or end-to-end key exchange.

The complete base text, examples, grammar, references, appendices and end matter have been read. All nine records in the captured RFC Editor errata corpus were also read. This is a document review, not a tested IMAP implementation. Captured official metadata lists no updating or obsoleting RFC; fresh status and errata retrieval failed, so live closure remains open. Referenced extensions and security dependencies need their own reviews before an implementation claims their conformance.

The [IMAP4rev1 compatibility audit](imap-rev1.md) covers RFC3501 separately, including its different base commands, mailbox encoding and errata. Rev2 review is not evidence that a rev1 adapter implements those rules.

## What Email/2 can reuse

A client can retrieve message headers and selected MIME parts, then build a conversation from messages already available in the account. It should use non-marking retrieval (`BODY.PEEK`) for background processing and verify the protected representation before accepting structured events. Server-parsed headers, search results and mailbox flags are useful indexes, not authenticated facts.

`IDLE` reports changes to the account's mailboxes. It does not reveal whether a correspondent is online. `APPEND` stores a message but explicitly does not deliver it: it has no SMTP envelope. Neither facility supplies a hidden negotiation channel that older clients must discard.

Mailbox copies and moves can give the same message different UIDs. Conversation event identity must survive those operations, while synchronization keeps the server, mailbox, UIDVALIDITY and UID scope separate. QRESYNC, CONDSTORE and OBJECTID are promising optional improvements; RFC9051 recommends them without making them part of its baseline.

## Section review

Grouped rows apply the stated disposition to each named section and its indicated subparts.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1, 1.1 | Reading and organization | Reconcile command prose, response prose and grammar; examples alone are not an implementation contract. |
| 1.2 | Conventions | Connection, selected-mailbox session, client and user have distinct meanings. |
| 1.3 | Implementation scope | Access and synchronization are separate from submission; rev1 compatibility needs an explicit profile. |
| 2, 2.1 | Transport | A reliable stream and port selection do not establish message confidentiality. |
| 2.2, 2.2.1 | Commands | Tags correlate command completion, not persistent application events. Finish a continuation before starting another command. |
| 2.2.2 | Responses | Untagged data can interleave with command exchanges; retain the required state updates. |
| 2.3, 2.3.1 | Message attributes and numbers | Keep mailbox identifiers separate from message content and conversation identity. |
| 2.3.1.1 | UIDs | Scope UIDs by server, mailbox and UIDVALIDITY. UIDNEXT predicts a lower bound, not a guaranteed next assigned identifier. |
| 2.3.1.2 | Sequence numbers | Expunge renumbers messages immediately; sequence numbers cannot be durable event identifiers. |
| 2.3.2 | Flags | Mutable flags and keywords are not authenticated answers or proof of reading. Permanent and session flags differ; conflicting junk classifications have defined handling. |
| 2.3.3 | Internal date | Arrival, copy and append semantics differ from the author's Date field; this is not authenticated event order. |
| 2.3.4 | Size | RFC822.SIZE measures the message representation, not decoded content. |
| 2.3.5 | Envelope | IMAP ENVELOPE parses message headers; it is not the SMTP delivery envelope. |
| 2.3.6, 2.4 | Body structure and texts | Selective retrieval is useful; parsed structure and partial bytes do not establish cryptographic validity. |
| 3, 3.1–3.4 | States | Enforce command state boundaries, failed selection behavior and logout ordering. |
| 4, 4.1 | Formats and atoms | Parse protocol tokens according to their context, rather than applying message-text rules. |
| 4.1.1 | Sets | Command context determines sequence numbers versus UIDs; the contradictory final sentence is a reported source defect. |
| 4.2 | Numbers | Respect the specified 32-bit and 63-bit domains; do not use lossy numeric representations. |
| 4.3, 4.3.1 | Strings and binary strings | Literal lengths count octets; even an empty synchronizing literal needs continuation. NUL requires the permitted binary form. |
| 4.4, 4.5 | Lists and NIL | Preserve nesting and the distinction between NIL, empty values and an atom naming a mailbox NIL. |
| 5, 5.1 | Naming | Mailbox NFC and case rules do not authorize normalization of signed message bytes or identities. INBOX is a special case. |
| 5.1.1 | Hierarchy | Use the server's hierarchy delimiter, not a filesystem assumption. |
| 5.1.2, 5.1.2.1, 5.1.2.2 | Namespaces | Prefixes and accessibility depend on the server and authenticated account; access is not conversation membership. |
| 5.2 | Updates | Remember message and flag changes; EXISTS cannot reduce the message count. |
| 5.3 | Unsolicited responses | Respect flow and expunge restrictions rather than assuming responses belong to the last command. |
| 5.4 | Autologout | The protocol's idle timing is not a presence signal or an Email/2 policy default. |
| 5.5 | Pipelining | Sequence-number changes and saved-search dependencies constrain safe concurrency. |
| 6 | Commands | BAD and NO have different semantics; failed SELECT/EXAMINE can still change selection state. |
| 6.1, 6.1.1 | Universal commands and capabilities | Advertising a feature is not enabling it. A dual rev1/rev2 server initially retains rev1 behavior. |
| 6.1.2 | NOOP | Polls account state, not peer presence or human reading. |
| 6.1.3 | LOGOUT | Process BYE and the tagged completion in their specified order. |
| 6.2 | Authentication state | TLS does not itself authenticate an account or grant message privileges. |
| 6.2.1 | STARTTLS | Discard pre-TLS capabilities and prevent buffered plaintext from becoming post-TLS commands. |
| 6.2.2 | AUTHENTICATE | Apply SASL framing, cancellation and security-layer boundaries; refresh capabilities after a changed security context. |
| 6.2.3 | LOGIN | Do not expose passwords on an unprotected connection or ignore LOGINDISABLED. |
| 6.3 | Authenticated commands | Mailbox operations remain constrained by account permissions. |
| 6.3.1 | ENABLE | Enablement is additive and acknowledged by ENABLED; unknown or inapplicable requests are ignored, not inferred successful. |
| 6.3.1.1 | Extension design | Use ENABLE only when incompatible response behavior requires it. |
| 6.3.2 | SELECT | Retain required mailbox metadata; selecting a new mailbox first closes the old one, including on failure. |
| 6.3.3 | EXAMINE | Read-only examination forbids permanent changes, including per-user state. |
| 6.3.4 | CREATE | Normalize consistently or reject; reusing a name must not silently reuse old UID identity. |
| 6.3.5 | DELETE | Successful deletion removes messages but must not recursively delete child mailboxes. |
| 6.3.6 | RENAME | Children normally follow the rename; INBOX has special behavior. Subscriptions do not automatically follow. |
| 6.3.7, 6.3.8 | Subscriptions | Idempotent account preferences, potentially naming nonexistent mailboxes; not conversation membership or permissions. |
| 6.3.9 | LIST | Options, wildcard and reference semantics matter. A listing is not necessarily a complete inventory of accessible mailboxes. |
| 6.3.9.1 | Selection | SUBSCRIBED may include nonexistent names; REMOTE expands scope; RECURSIVEMATCH requires a base selection option. |
| 6.3.9.2 | Return options | Extra returned data does not expand the selection. Missing STATUS data must not be interpreted as zero. |
| 6.3.9.3 | Response principles | At most one solicited LIST response per name; account for selection and descendant rules. |
| 6.3.9.4 | Attribute implications | NonExistent implies NoSelect; NoInferiors implies HasNoChildren. |
| 6.3.9.5 | Children | HasNoChildren concerns accessible children; NoInferiors additionally forbids future children. Listings can race with changes. |
| 6.3.9.6 | CHILDINFO | Describes descendant selection matches, not proof that a usable child mailbox exists. |
| 6.3.9.7 | OLDNAME | Correlates normalization, rename or deletion; does not authenticate a new principal. |
| 6.3.9.8 | Examples | Selection and return options differ; child information can describe nonexistent subscriptions. Multi-pattern examples need LIST-EXTENDED beyond the base grammar. |
| 6.3.10 | NAMESPACE | Accept multiple namespaces and account-specific visibility; source examples need the corrections discussed below. |
| 6.3.11 | STATUS | Does not select or mutate the mailbox. Do not use it to poll the selected mailbox; SIZE may be expensive and is an upper bound. |
| 6.3.12 | APPEND | Storage is not delivery. Failure rolls back the append, with a possible UIDNEXT change; write-only access must not expose APPENDUID. |
| 6.3.13 | IDLE | Receives mailbox updates until DONE; no new command during continuation. Unsolicited FETCH includes UID. Not peer presence. |
| 6.4 | Selected commands | Message mutation requires a selected mailbox and applicable access rights. |
| 6.4.1 | CLOSE | Expunges deleted messages on a writable mailbox; it is not a harmless deselection operation. |
| 6.4.2 | UNSELECT | Deselects without expunging. |
| 6.4.3 | EXPUNGE | Removes all messages flagged deleted in the mailbox; concurrent clients make blanket expunge consequential. |
| 6.4.4 | SEARCH | Search narrows candidates. HEADER substring results still need exact local parsing and verification; BODY/TEXT may use flexible matching. |
| 6.4.4.1 | Saved results | SAVE sets a connection-local message set. Selection, UIDVALIDITY and expunge affect it; MIN/MAX alone save only extrema. |
| 6.4.4.2 | Search dependencies | Execute a saved search before commands consuming its result, even when pipelined. |
| 6.4.4.3 | Save refusal | NOTSAVED clears the result; never reuse an older set after failure. |
| 6.4.4.4 | Examples | Test option combinations and failure paths; the verified BADCHARSET correction itself has a semantic inconsistency. |
| 6.4.5 | FETCH | Prefer PEEK for background processing. BINARY offsets address decoded content; BODY offsets address the transmitted representation. |
| 6.4.5.1 | Sections | MIME part numbering and header subsetting have exact rules; selected headers are not a substitute for the protected entity. |
| 6.4.6 | STORE | Changes flags, not immutable message bytes. SILENT does not suppress unrelated flag updates. |
| 6.4.7 | COPY | Preserves content with a new mailbox identity; failure must roll back the destination copy, apart from possible UIDNEXT increments. |
| 6.4.8 | MOVE | A set can partially succeed. Each message remains in at least one mailbox; map COPYUID before EXPUNGE and reconcile duplicates. |
| 6.4.9 | UID | Missing UIDs can yield successful no-ops. FETCH/EXPUNGE leading numbers remain sequence numbers; UID EXPUNGE narrows deletion. |
| 6.5 | Extensions | New commands need capabilities; new untagged responses require the associated command or enablement. No silent legacy behavior is implied. |
| 7 | Responses | Process state updates independently of command completion, subject to connection-state security rules. |
| 7.1 | Status codes | Use machine-readable codes; unknown codes are ignored. Protect sensitive UID information and distrust unprotected ALERT text. |
| 7.1.1 | OK | Untagged information is not command completion. |
| 7.1.2 | NO | Untagged warnings can accompany a successful command; tagged NO is the operation result. |
| 7.1.3 | BAD | Distinguish protocol errors and untagged server failures. |
| 7.1.4 | PREAUTH | On an unprotected port it prevents STARTTLS; mandatory-TLS clients must close. |
| 7.1.5 | BYE | Read pending responses through closure; normal logout and immediate failure differ. |
| 7.2, 7.2.1 | Server status and ENABLED | The acknowledged list, possibly empty, identifies enabled features. |
| 7.2.2 | CAPABILITY | Capabilities can change after TLS or authentication. Unknown names do not authorize guessed behavior. |
| 7.3, 7.3.1 | Mailbox status and LIST | Special-use roles are optional, account-specific and potentially repeated; an All mailbox may omit Trash/Junk. |
| 7.3.2 | NAMESPACE | Missing namespace classes use NIL; extensions require tolerant structural parsing. |
| 7.3.3 | STATUS | Associate returned data with the named mailbox, not the selected mailbox by assumption. |
| 7.3.4 | ESEARCH | Honor the correlator and UID indicator; result order is unspecified and returned ranges must be complete. |
| 7.3.5 | FLAGS | Remember available flags, separately from PERMANENTFLAGS. |
| 7.4, 7.4.1 | Mailbox size and EXISTS | Remember counts; presence of a new message does not prove a new conversation event. |
| 7.5, 7.5.1 | Message status and EXPUNGE | Renumber immediately; UID commands have different expunge interleaving rules from plain FETCH/STORE/SEARCH. |
| 7.5.2 | FETCH response | ENVELOPE defaults and BODYSTRUCTURE decoding lose original representation detail. BINARY normalizes text line endings. Fetch verification inputs deliberately. |
| 7.6 | Continuations | Wait before sending synchronizing literal bytes; the remaining command follows the counted bytes. |
| 8 | Transcript | Illustrative exchange, not a ready-made conformance fixture; reconcile omissions against normative requirements. |
| 9 | Grammar | Exact spaces, literal lengths, UTF-8, numeric domains and context matter. Prose/grammar discrepancies remain identified below. |
| 10 | History | Explains lineage; does not import all superseded behavior. |
| 11 | Security | Protect the access connection independently of end-to-end message protection. |
| 11.1 | TLS | Validate server identity and negotiated protection. Resolve current TLS dependencies before implementing historical algorithm references. |
| 11.2 | TLS ports | Both client negotiation paths and server implicit TLS have defined requirements; discovery may override default connection attempts. |
| 11.3 | Invalid-state responses | Ignore mailbox data in inappropriate states and unprotected alerts; account for PREAUTH downgrade hazards. |
| 11.4 | UID disclosure | Apply the stricter command-section prohibition on revealing APPENDUID/COPYUID to write-only users. |
| 11.5 | Other users | Do not enumerate users without granted listing access. |
| 11.6 | MD5 | Exposing Content-MD5 does not make it a secure authentication mechanism. |
| 11.7 | Authentication | Avoid credential enumeration, plaintext exposure and unbounded guessing; password policy remains an account service responsibility. |
| 12 | Registrations | Existing IMAP TCP services and reserved UDP ports are not new Email/2 transports. |
| 12.1 | Capabilities registry | Follow the actual registration procedure, rather than copying fictitious X-prefixed examples. |
| 12.2 | SASL service | Reuse the registered imap service in its defined role. |
| 12.3 | LIST registries | Selection, return and extended-data registrations retain RFC5258 procedures. |
| 12.4 | Attribute and response registries | Reuse existing meanings; new semantics need their own defined extension. |
| 13, 13.1 | References | References were read as dependencies; their listing is not a full audit of their bodies. |
| 13.2, 13.2.1 | Related work | QRESYNC, OBJECTID, ACL and discovery documents remain separate capabilities and review dependencies. |
| 13.2.2 | History | Older protocol references explain compatibility, not current security defaults. |
| Appendix A, A.1 | Rev1 compatibility | Explicitly enable rev2 on dual servers. Modified UTF-7 belongs to the legacy mailbox interface and has strict shift/case rules. |
| Appendix B | BINARY compatibility | Base rev2 includes retrieval only; binary APPEND requires the separate BINARY capability. |
| Appendix C | LIST compatibility | Multiple patterns require LIST-EXTENDED. |
| Appendix D | Large sizes | Clients must handle 63-bit sizes; old clients may see hidden or replaced oversized messages. Do not claim complete history from such a view. |
| Appendix E | Change list | Informative summary contains terminology and spelling issues; normative sections and grammar govern. |
| Appendix F | Optional improvements | QRESYNC/CONDSTORE reduce synchronization cost; OBJECTID preserves caches across moves and renames. Neither is required by the base. |
| Front matter, acknowledgements, index, addresses | End matter | Read for scope and navigation; no additional Email/2 behavior. |

## Errata and source issues

The captured errata have different statuses. A reported correction is not an approved change.

| Record | Captured status | Treatment |
| --- | --- | --- |
| [7343](https://www.rfc-editor.org/errata/eid7343) | Reported | Proposes tolerating omitted trailing spaces in empty response text. Keep strict sender grammar distinct from a documented receiver tolerance. |
| [7518](https://www.rfc-editor.org/errata/eid7518) | Reported | Identifies the sequence-set contradiction in Section 4.1.1 but supplies no usable replacement. Sections 6.4.9 and 9 establish command-dependent UID use. |
| [7246](https://www.rfc-editor.org/errata/eid7246) | Reported | Identifies BINARY response offset prose absent from grammar. Do not silently select one interpretation for a new interoperability claim. |
| [7323](https://www.rfc-editor.org/errata/eid7323) | Verified | Correctly requires parentheses for BADCHARSET, but the replacement lists KOI8-R while saying it is unsupported. Section 7.1 says the list contains supported charsets; a corrected fixture should list supported UTF-8 in parentheses. |
| [6826](https://www.rfc-editor.org/errata/eid6826) | Held for Document Update | RFC822 fetch aliases were removed from rev2 syntax; use BODY equivalents, with legacy support separately profiled. |
| [7593](https://www.rfc-editor.org/errata/eid7593) | Reported | SPECIAL-USE selection was not incorporated into the base. Merely removing that option does not establish that listing nonexistent special-use mailboxes satisfies the general LIST rules. |
| [8001](https://www.rfc-editor.org/errata/eid8001) | Reported | Requests a compatibility-note addition for idempotent subscriptions; the rev2 command text already defines the behavior. |
| [8030](https://www.rfc-editor.org/errata/eid8030) | Verified | Corrects the example mailbox name to Deleted Items. |
| [8863](https://www.rfc-editor.org/errata/eid8863) | Verified | Repairs IMAPrev spelling to IMAP4rev; no new protocol behavior. |

Additional inconsistencies were found by comparing the text and grammar. Section 9 retains 32-bit `body-fld-octets`, BINARY.SIZE and BODY response offsets despite the 63-bit size discussion. Section 7.5.2 describes nested envelope/body fields for MESSAGE/RFC822 but its grammar also includes MESSAGE/GLOBAL. Appendix E says `$NonJunk` where the actual keyword is `$NotJunk`. These are source issues, not permission for an implementation to invent wire syntax.

Some transcripts omit required selection data, and a SELECT example uses UIDVALIDITY 9877410381, outside the specified nonzero 32-bit range. The saved-search example also mismatches C282 with an ESEARCH C283 correlator. Examples must be repaired and validated before use as acceptance fixtures.

## Acceptance work still needed

The adoption tools should exercise both ordinary rev1 servers and explicit rev2 negotiation. High-value cases include expunge renumbering during UID operations, stale UIDVALIDITY, partial MOVE failure, write-only mailbox UID disclosure, PEEK without setting Seen, saved-search failure, partial and decoded MIME retrieval, Unicode mailbox names, large numeric values, pre-authentication response injection and IDLE reconnects.

These are proposed acceptance cases. This review did not run a server, a parser conformance suite or cryptographic verification over fetched messages. It does not establish complete update, extension or live registry closure.
