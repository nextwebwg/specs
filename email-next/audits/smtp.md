---
title: SMTP audit
sectionNav: true
---

# SMTP audit

SMTP can carry the initial Email/2 profile without requiring provider upgrades. Its extension mechanism can support later server features, but next-hop negotiation cannot establish the capabilities of a recipient's devices.

**Coverage:** complete RFC 5321 text, appendices and references, plus all 15 retrieved errata records, read and assessed on 19 October 2026. Base-document review is complete; dependent standards, current registries and update integration remain open. IPv6 literal syntax requires explicit reconciliation with its dependencies. This is not an interoperability certification.

Source: [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321.html). [RFC 7504](https://www.rfc-editor.org/rfc/rfc7504.html) updates reply codes. The [capability contract](../interoperability.md#capability-negotiation) records the resulting proposal constraints.

## Section dispositions

| Section | Disposition and consequence |
| --- | --- |
| 1 — Introduction | Inherited introduction; transport model remains SMTP for baseline delivery. |
| 1.1 — Transport of Electronic Mail | Inherited reliable ordered stream and relay model. Changing underlying transport alone does not establish recipient capabilities. |
| 1.2 — History and Context for This Document | Historical consolidation reviewed; later submission and access specifications supersede cited versions and require their own audits. |
| 1.3 — Document Conventions | Inherited normative terminology; historical example domains must not be copied into production configuration. |
| 2 — The SMTP Model | Inherited client/server model; distinguish each transport hop from end-to-end interaction. |
| 2.1 — Basic Structure | Inherited transfer responsibility after final successful DATA reply. This acknowledges handoff, not reading, decryption or application of an event. |
| 2.2 — The Extension Model | Extension opportunity; retain baseline interoperable delivery and separately specify any server enhancement. |
| 2.2.1 — Background | Inherited EHLO negotiation and HELO fallback; capabilities describe the current peer, not all downstream systems. |
| 2.2.2 — Definition and Registration of Extensions | Inherited registration requirements, parameter grammar, command-length changes and X-prefixed bilateral experiments. Do not advertise invented registered keywords. |
| 2.2.3 — Special Issues with Extensions | Inherited extension-specific fallback. A transport fallback cannot override the sender encryption policy or create plaintext without authorization. |
| 2.3 — SMTP Terminology | Inherited terminology; role names are not proof of trust. |
| 2.3.1 — Mail Objects | Inherited envelope/content split. Error return path is distinct from message authorship. UTF-8 transport changes are covered by the [SMTPUTF8 audit](smtputf8.md). |
| 2.3.2 — Senders and Receivers | Inherited peer-role terminology; a relay can act as both server and client. |
| 2.3.3 — Mail Agents and Message Stores | Inherited caution about MUA/MTA boundaries; assign security responsibilities explicitly rather than inferring from labels. |
| 2.3.4 — Host | Inherited host naming; address literals require specified grammar. |
| 2.3.5 — Domain Names | Inherited resolvable FQDN requirements and EHLO/postmaster exceptions; do not turn local aliases into global discovery identities. |
| 2.3.6 — Buffer and State Table | Inherited transaction state; reset discards pending transfer state, not prior delivered application events. |
| 2.3.7 — Commands and Replies | Inherited numeric reply codes; human-readable reply text is not a rich protocol capability channel. |
| 2.3.8 — Lines | Inherited CRLF framing, no bare CR/LF transmission; message-source acceptance rules are not SMTP emission rules. |
| 2.3.9 — Message Content and Mail Data | Inherited MIME content boundary; proposed events live in message content. |
| 2.3.10 — Originator, Delivery, Relay, and Gateway Systems | Inherited distinction between relay preservation and gateway transformations; evaluate authenticated-content survival separately. |
| 2.3.11 — Mailbox and Address | Inherited recipient-domain authority over local-part semantics; intermediary normalization cannot determine key ownership. |
| 2.4 — General Syntax Principles and Transaction Model | Inherited case-preserving local parts, case-insensitive domains, negotiated 7/8-bit transport and prose constraints. 8BITMIME does not authorize arbitrary binary data. |
| 3 — The SMTP Procedures: An Overview | Inherited procedure overview; detailed command and operational rules are covered in the section dispositions below. |
| 3.1 — Session Initiation | Inherited greeting/session rejection; RFC 7504 reply additions remain separately tracked. |
| 3.2 — Client Initiation | Inherited EHLO/HELO initiation; claimed peer name is not cryptographic proof. |
| 3.3 — Mail Transactions | Inherited MAIL/RCPT/DATA sequencing, per-recipient acceptance and final responsibility. Partial recipient outcomes must remain separate from interaction success. |
| 3.4 — Forwarding for Address Correction or Updating | Inherited silent forwarding and optional address-correction replies. Do not infer final membership or replace identity keys from a forwarding response. |
| 3.5 — Commands for Debugging Addresses | Diagnostics reviewed; not selected as cryptographic discovery service. |
| 3.5.1 — Overview | Inherited VRFY/EXPN semantics and ambiguous replies; no assumption that every server reveals a usable directory. |
| 3.5.2 — VRFY Normal Response | Inherited diagnostic response formatting and configurable restrictions; discovery must work without enumeration. |
| 3.5.3 — Meaning of VRFY or EXPN Success Response | Inherited verification vs apparent validity distinction; neither establishes a recipient public key. |
| 3.5.4 — Semantics and Applications of EXPN | Inherited caution against source list expansion for deduplication; do not use EXPN to construct authoritative encrypted group membership. |
| 3.6 — Relaying and Mail Routing | Inherited relay routing; cryptographic endpoint identity remains independent. |
| 3.6.1 — Source Routes and Relaying | Inherited source-route treatment; no source-route discovery mechanism proposed. |
| 3.6.2 — Mail eXchange Records and Relaying | Inherited MX relay selection and policy refusal; return-path authentication is outside this section. |
| 3.6.3 — Message Submission Servers as Relays | Inherited submission distinction, null reverse-path notifications and relay content preservation. No automatic key messages in response to delivery errors. |
| 3.7 — Mail Gatewaying | Inherited gateway boundary; content transformations may invalidate structured/authenticated representations. |
| 3.7.1 — Header Fields in Gatewaying | Inherited gateway header rewrites; copying envelope recipients into visible fields can disclose Bcc. |
| 3.7.2 — Received Lines in Gatewaying | Inherited append-only Received trace and robust acceptance; do not repair original trace data in the preserved message. |
| 3.7.3 — Addresses in Gatewaying | Inherited gateway input/output address requirements; safe receiving and conforming generation remain separate. |
| 3.7.4 — Other Header Fields in Gatewaying | Inherited gateway conversion and reverse-path error routing. Reconcile replyability language with later RFC 6854 originator groups before declaring combined profile complete. |
| 3.7.5 — Envelopes in Gatewaying | Inherited gateway error-return mapping; last-resort originator mapping is not identity authentication. |
| 3.8 — Terminating Sessions and Connections | Inherited termination and temporary-failure handling; an interrupted connection can leave delivery outcome uncertain. |
| 3.9 — Mailing Lists and Aliases | Inherited list/alias expansion distinctions; visible recipients are not necessarily final destinations. |
| 3.9.1 — Alias | Inherited alias expansion preserves remaining envelope and body; an alias can expand to multiple recipients. |
| 3.9.2 — List | Inherited list error-path replacement and distinction between transit-like and message-modifying lists. An opaque alias/list cannot establish endpoint membership. |
| 4 — The SMTP Specifications | Inherited transport contract; no baseline SMTP command replacement proposed. |
| 4.1 — SMTP Commands | Inherited commands; upgraded client uses a submission service rather than assuming every MTA relays for it. |
| 4.1.1 — Command Semantics and Syntax | Inherited buffers, CRLF termination and argument restrictions; no unnegotiated parameters. |
| 4.1.1.1 — Extended HELLO (EHLO) or HELLO (HELO) | Inherited initialization, multiline EHLO and case-insensitive extension names; successful EHLO resets transaction state. |
| 4.1.1.2 — MAIL (MAIL) | Inherited MAIL reverse-path and buffer reset; reverse-path identifies error routing, not authenticated authorship. |
| 4.1.1.3 — RECIPIENT (RCPT) | Inherited individual RCPT acceptance and offered extension parameters; Postmaster is a case-insensitive exception. |
| 4.1.1.4 — DATA (DATA) | Inherited DATA framing, final-line handling and all-or-nothing SMTP acceptance. Never recognize bare-LF terminators; partial downstream failure uses notification after acceptance. |
| 4.1.1.5 — RESET (RSET) | Inherited RSET aborts pending transaction only; held erratum 1851 concerns placement of connection-loss prose. |
| 4.1.1.6 — VERIFY (VRFY) | Inherited diagnostic VRFY; no transaction mutation or key binding. |
| 4.1.1.7 — EXPAND (EXPN) | Inherited diagnostic EXPN; no transaction mutation or authenticated membership assertion. |
| 4.1.1.8 — HELP (HELP) | Inherited HELP; human help text is not a capability schema. |
| 4.1.1.9 — NOOP (NOOP) | Inherited NOOP; successful reply conveys no recipient/application success. |
| 4.1.1.10 — QUIT (QUIT) | Inherited QUIT; abort unfinished work without undoing completed transfers. |
| 4.1.1.11 — Mail-Parameter and Rcpt-Parameter Error Responses | Inherited 555 unsupported and 455 temporarily unavailable parameter handling, subject to extension-specific codes. |
| 4.1.2 — Command Argument Syntax | Inherited envelope grammar and quoted-local-part equivalence; verified erratum 2578 corrects ABNF reference. Held empty-string restriction is not adopted. |
| 4.1.3 — Address Literals | Inherited literal syntax subject to explicit pending IPv6 dependency reconciliation; do not silently adopt held 4315 or rejected 2467. |
| 4.1.4 — Order of Commands | Inherited sequencing and rejected-command state preservation; EHLO name/IP mismatch alone is not a mail-rejection basis. |
| 4.1.5 — Private-Use Commands | Inherited bilateral X-prefixed private commands; new registered commands require the specified process. |
| 4.2 — SMTP Replies | Inherited multiline replies, code-driven decisions and unknown-code severity handling; verified 4198 identifies the client as reply interpreter. |
| 4.2.1 — Reply Code Severities and Theory | Inherited 2/3/4/5 reply classes; all lines in a multiline reply share a code. Temporary/permanent failures have distinct retry outcomes. |
| 4.2.2 — Reply Codes by Function Groups | Inherited functional code table, subject to RFC 7504 update; textual wording is not general protocol state. |
| 4.2.3 — Reply Codes in Numeric Order | Inherited numeric code table, subject to RFC 7504 update; do not invent application-receipt meanings. |
| 4.2.4 — Reply Code 502 | Inherited distinction between unknown and unimplemented commands; an advertised command cannot return 500/502 as unsupported. |
| 4.2.5 — Reply Codes after DATA and the Subsequent <CRLF>.<CRLF> | Inherited final DATA responsibility: 2yz transfers it; 4yz/5yz leaves it with client and server must not later deliver that rejected transaction. |
| 4.3 — Sequencing of Commands and Replies | Inherited command/reply sequencing; negotiated extensions may change it. |
| 4.3.1 — Sequencing Overview | Inherited wait-for-reply operation, including greeting; no pipelining without its extension. |
| 4.3.2 — Command-Reply Sequences | Inherited command-specific replies and severity fallback; prefer enhanced codes for detail, not invented basic reply codes. |
| 4.4 — Trace Information | Inherited append-only Received, error Return-Path and partial-failure notifications; verified 1683 permits multiple registered clauses. Protect hidden recipients from FOR disclosure. |
| 4.5 — Additional Implementation Issues | Inherited implementation requirements; client application semantics do not waive transport rules. |
| 4.5.1 — Minimum Implementation | Inherited minimum commands and Postmaster behavior; disabling address disclosure uses the specified VRFY response. |
| 4.5.2 — Transparency | Inherited dot-stuffing and reversible storage transformations; transport transparency is not message canonicalization. |
| 4.5.3 — Sizes and Timeouts | Inherited size/time constraints; keep transport limits distinct from renderer resource limits. |
| 4.5.3.1 — Size Limits and Minimums | Inherited interoperability limits and extension qualifications; avoid treating every lower bound on capacity as a universal content maximum. |
| 4.5.3.1.1 — Local-part | Inherited 64-octet local-part limit; UTF-8 character count is not octet count. |
| 4.5.3.1.2 — Domain | Inherited 255-octet domain limit, also constrained by complete path and DNS rules. |
| 4.5.3.1.3 — Path | Inherited 256-octet path limit including punctuation. |
| 4.5.3.1.4 — Command Line | Inherited 512-octet command line including CRLF, unless extended. |
| 4.5.3.1.5 — Reply Line | Inherited 512-octet reply line including CRLF; multiline responses carry additional information. |
| 4.5.3.1.6 — Text Line | Inherited 1000-octet data line including CRLF, excluding extra transparency dot, unless extended. |
| 4.5.3.1.7 — Message Content | Inherited minimum supported message capacity of 64K octets; not a universal 64K message maximum. SIZE negotiation requires its own audit. |
| 4.5.3.1.8 — Recipients Buffer | Inherited minimum recipient buffering and orderly overflow; chunking must preserve per-recipient outcomes and Bcc isolation. |
| 4.5.3.1.9 — Treatment When Limits Exceeded | Inherited explicit errors for exceeded limits; no silent truncation of structured or encrypted payloads. |
| 4.5.3.1.10 — Too Many Recipients Code | Inherited 452 recipient-buffer exhaustion and contextual legacy 552 handling; site-policy rejection is distinct. |
| 4.5.3.2 — Timeouts | Inherited configurable per-command/data-block timeouts, not a single whole-message timer. |
| 4.5.3.2.1 — Initial 220 Message: 5 Minutes | Inherited recommended minimum five-minute initial greeting wait; TCP connection success is a separate observation. |
| 4.5.3.2.2 — MAIL Command: 5 Minutes | Inherited recommended minimum five-minute MAIL timeout. |
| 4.5.3.2.3 — RCPT Command: 5 Minutes | Inherited recommended minimum five-minute RCPT timeout, allowing longer alias/list processing. |
| 4.5.3.2.4 — DATA Initiation: 2 Minutes | Inherited recommended minimum two-minute DATA initiation timeout. |
| 4.5.3.2.5 — Data Block: 3 Minutes | Inherited recommended minimum three-minute data-block timeout. |
| 4.5.3.2.6 — DATA Termination: 10 Minutes. | Inherited recommended minimum ten-minute final DATA reply wait; premature timeout can cause duplicate delivery. |
| 4.5.3.2.7 — Server Timeout: 5 Minutes. | Inherited recommended minimum five-minute server wait for next command. |
| 4.5.4 — Retry Strategies | Inherited queuing and no error-response loops; keep automatic discovery out of bounce chains. |
| 4.5.4.1 — Sending Strategy | Inherited configurable delayed retry and envelope retention. General retry interval is at least 30 minutes with qualified strategies; give-up generally at least 4–5 days. Do not cache MAIL 5yz failures globally. |
| 4.5.4.2 — Receiving Strategy | Inherited concurrent receiving and operational queue activation; no online-user-presence inference. |
| 4.5.5 — Messages with a Null Reverse-Path | Inherited null reverse-path handling and recommendation against replying to it; ordinary discovery mail does not acquire notification status merely by being automated. |
| 5 — Address Resolution and Mail Handling | Inherited address resolution; DNS routing alone is not key discovery authorization. |
| 5.1 — Locating the Target Host | Inherited MX preference, implicit-MX conditions, alternate addresses, transient DNS retry and self-loop avoidance. The Null MX extension is covered by the [no-mail-service audit](no-mail-service.md). |
| 5.2 — IPv6 and MX Records | Inherited IPv4/IPv6 operational flexibility; no new endpoint identity semantics. |
| 6 — Problem Detection and Handling | Inherited failure handling; application validation remains distinct from SMTP acceptance. |
| 6.1 — Reliable Delivery and Replies by Email | Inherited durable acceptance and null-return-path notification suppression; final-acknowledgment loss can duplicate delivery. |
| 6.2 — Unwanted, Unsolicited, and "Attack" Messages | Inherited limited operational discretion for hostile traffic; silent dropping is not a sender-requested invisible-control channel. |
| 6.3 — Loop Detection | Inherited loop detection; suggested high Received-count threshold is not an application replay defense. |
| 6.4 — Compensating for Irregularities | Inherited origin/submission repairs and relay restrictions; finalize protected fields before transport and do not treat repaired headers as original signatures. |
| 7 — Security Considerations | Inherited transport threat model; later security protocols need independent review. |
| 7.1 — Mail Security and Spoofing | Inherited spoofing/delegation boundaries; hop authentication does not establish end-to-end author identity. Historical crypto citations require current replacements. |
| 7.2 — "Blind" Copies | Inherited Bcc protection and envelope/header separation; separate Bcc transactions can reduce exposure. |
| 7.3 — VRFY, EXPN, and Security | Inherited 252 for security-disabled VRFY/EXPN; avoid address harvesting and false verification claims. |
| 7.4 — Mail Rerouting Based on the 251 and 551 Response Codes | Inherited authenticity requirement before automatic address updates; forwarding cannot silently migrate trusted encryption identity. |
| 7.5 — Information Disclosure in Announcements | Inherited operational disclosure tradeoff for greetings/help; do not require detailed versions in recipient capability records. |
| 7.6 — Information Disclosure in Trace Fields | Inherited trace disclosure warning; encryption does not hide outer routing and trace metadata. |
| 7.7 — Information Disclosure in Message Forwarding | Inherited forwarding-address disclosure warning; do not automatically expose final alias targets. |
| 7.8 — Resistance to Attacks | Inherited attack-defense latitude; control traffic must tolerate throttling and rejection. |
| 7.9 — Scope of Operation of SMTP Servers | Inherited site acceptance/relay policy; rich-client compatibility does not imply unrestricted relay permission. |
| 8 — IANA Considerations | Inherited extension, literal, trace and header registries; current registry audit remains pending. |
| 9 — Acknowledgments | Acknowledgements reviewed; no protocol rule. |
| 10 — References | References reviewed; dependency closure still open. |
| 10.1 — Normative References | Normative dependencies identified: RFCs 821,1035,1123,5322,2119,5234,4291,3848,1870,3864 and ASCII. Retained historical references require scoped treatment. |
| 10.2 — Informative References | Informative dependencies reviewed as a list; queue control, duplication, gateway and updated security/access sources enter the scope ledger as relevant, not silently adopted. |
| Appendix A — TCP Transport Service | Inherited TCP octet transport and negotiated extension boundary; an 8-bit stream does not authorize arbitrary 8-bit mail. |
| Appendix B — Generating SMTP Commands from RFC 822 Header Fields | Inherited recommendation for a separate submission envelope; header-only gateway routing is prohibited and risks loops/Bcc leaks. |
| Appendix C — Source Routes | Inherited historical route semantics and no header-derived final routing; no new source-routing facility proposed. |
| Appendix D — Scenarios | Informative scenarios reviewed; examples are subordinate to normative preservation rules. |
| Appendix E — Other Gateway Issues | Inherited gateway layering guidance; information loss across incompatible environments must be explicit. |
| Appendix F — Deprecated Features of RFC 821 | Deprecated feature inventory reviewed; no revival for rich messaging. |
| D.1 — D.1 | Informative mixed RCPT success/failure example; accepted recipients continue independently. |
| D.2 — D.2 | Informative abort example; RSET prevents pending delivery. |
| D.3 — D.3 | Informative relay example contains message differences; held erratum 5711 flags body spacing. Date/Subject differences also must not become preservation test expectations. |
| D.4 — D.4 | Informative verification example; diagnostic success is not cryptographic identity verification. |
| F.1 — F.1 | Deprecated TURN is not a live key-exchange rendezvous mechanism. |
| F.2 — F.2 | Inherited receive/ignore source routes and no invented shortcuts; rejected 4265 does not narrow syntax acceptance. |
| F.3 — F.3 | Inherited HELO compatibility and EHLO preference. |
| F.4 — F.4 | Inherited prohibition on obsolete pound-sign integer address literals. |
| F.5 — F.5 | Inherited four-digit years for generated SMTP dates; message-store obsolete receiving rules remain distinct. |
| F.6 — F.6 | Deprecated SEND/SAML/SOML do not supply a new presence or silent-message channel. |

## Open questions and required evidence

- Complete dependent extension review and test the proposed delivery-state machine against SMTP failure cases.
- Reconcile gateway replyability wording with the later originator-group update; preserve source-specific scope instead of claiming every valid message has a replyable author.
- Test delivery interruption after DATA, partial recipient rejection and retransmission. A duplicate transport delivery must not apply a structured submission twice.
- Test alias expansion and message-modifying lists without claiming that SMTP directory commands establish authenticated group membership.
- Verify that encrypted MIME remains transport-safe over the selected baseline, including line endings, transfer encodings and downstream capability loss.

## Errata dispositions

All records below were individually read. Verified corrections inform the review; held/rejected reports do not silently amend the specification.

| Erratum | Section | Status | Consequence |
| --- | --- | --- | --- |
| [2467](https://www.rfc-editor.org/errata/eid2467) | 4.1.3 | Rejected | Rejected IPv6 compression change; reconcile receiving and generation rules with RFCs 4291/5952 rather than treating rejection as universal IPv6 guidance. |
| [1543](https://www.rfc-editor.org/errata/eid1543) | 3.8 | Held for Document Update | Held change of connection-loss comparison from 451 to 421; both are temporary failures, but no published text substitution assumed. |
| [1683](https://www.rfc-editor.org/errata/eid1683) | 4.4 | Verified | Verified repetition allows multiple registered Received clauses. |
| [1851](https://www.rfc-editor.org/errata/eid1851) | 4.1.1.5. | Held for Document Update | Held relocation of connection-loss prose; no substantive new reset behavior. |
| [1820](https://www.rfc-editor.org/errata/eid1820) | 3.9.2 | Rejected | Rejected forwarding/list wording change; preserve underlying reverse-path distinctions. |
| [2578](https://www.rfc-editor.org/errata/eid2578) | 4.1.2 | Verified | Verified ABNF core-reference correction to Appendix B of RFC 5234. |
| [3447](https://www.rfc-editor.org/errata/eid3447) | 4.4 | Held for Document Update | Held Return-Path/relay wording concerns; preserve source scopes and do not upgrade SHOULD to MUST. |
| [4055](https://www.rfc-editor.org/errata/eid4055) | 3.6.2 | Rejected | Rejected deletion request; SMTP discussion does not replace SPF/DKIM security semantics, which require direct review. |
| [4079](https://www.rfc-editor.org/errata/eid4079) | 4.3.2. | Rejected | Rejected reintroduction of initial DATA 451 in table; extension and unknown-code processing still apply. |
| [4198](https://www.rfc-editor.org/errata/eid4198) | 4.2 | Verified | Verified sender/client, not receiver/server, interprets reply severity. |
| [4265](https://www.rfc-editor.org/errata/eid4265) | F.2 | Rejected | Rejected restriction of source-route acceptance to headers; do not apply proposed correction. |
| [4315](https://www.rfc-editor.org/errata/eid4315) | 4.1.3 | Held for Document Update | Held IPv6 compression rewrite; dependency conflict remains explicit. |
| [5414](https://www.rfc-editor.org/errata/eid5414) | 4.1.2 | Held for Document Update | Held nonempty quoted-local-part restriction; do not reject empty quoted syntax on this basis alone. |
| [5711](https://www.rfc-editor.org/errata/eid5711) | D.3 | Held for Document Update | Held relay-example spacing correction; tests must follow content-preservation requirements. |
| [6561](https://www.rfc-editor.org/errata/eid6561) | 4.1.2. | Rejected | Rejected trailing-dot SMTP domain syntax change; DNS presentation conventions do not amend SMTP grammar. |
