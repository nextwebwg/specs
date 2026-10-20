---
title: POP3 base protocol audit
sectionNav: true
---

# POP3 base protocol audit

The complete base text of [RFC1939](https://www.rfc-editor.org/rfc/rfc1939.html), including every command, example, appendix and end-matter section, has been reviewed alongside all four entries in the captured errata corpus. This establishes base-document review, not closure of updates, authentication dependencies or current registries.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | POP downloads a maildrop; it is not a server conversation database or multi-folder synchronization protocol. |
| 2 | A Short Digression | Submission is separate from retrieval and may use a different relay; historical relay advice does not define current submission authentication. |
| 3 | Basic Operation | State transitions, CRLF framing, dot stuffing, uppercase status and 512-octet single-line responses reviewed. Inactivity timeout is at least ten minutes and does not enter UPDATE. Generic negative replies do not distinguish unsupported commands from temporary inability. |
| 4 | The AUTHORIZATION State | Authentication precedes maildrop locking and transaction state. Message numbers are assigned within the opened maildrop; they are not persistent event identities. QUIT here does not delete mail. |
| 5 | The TRANSACTION State | STAT/LIST exclude marked messages; RETR returns complete dot-stuffed content; DELE only marks; NOOP changes nothing; RSET clears deletion marks. All command arguments, responses and examples reviewed. |
| 6 | The UPDATE State | Only transaction QUIT enters UPDATE. Deletion errors may remove some or none of marked messages; abnormal termination must not perform UPDATE deletion. Retry must tolerate uncertain outcomes. |
| 7 | Optional POP3 Commands | TOP, UIDL, USER, PASS and APOP fully reviewed. UIDL persists across sessions, allows identical copies to share an ID, and verified erratum529 extends nonreuse to the maildrop lifetime. Preview and authentication identifiers are not message authorship evidence. |
| 8 | Scaling and Operational Considerations | Quota and site retention can remove read or unread messages outside ordinary protocol deletion; download-once policy requires durable storage before successful session completion. POP lacks general folder/push semantics. |
| 9 | POP3 Command Summary | Command summary reviewed; its placement of USER/PASS under minimal commands conflicts with Section7 and AppendixA making them optional. Do not infer a required plaintext authentication method from this table. |
| 10 | Example POP3 Session | Complete example session reviewed; its clear transport and APOP flow are historical examples, not Email Next security recommendations. |
| 11 | Message Format | Size reflects CRLF message representation and excludes extra dot-stuffing octets. Local storage line endings are not the transmitted byte representation. |
| 12 | References | All references reviewed; historical SMTP, message format, MD5, IMAP and AUTH dependencies require separate applicability/current-successor work. |
| 13 | Security Considerations | Clear passwords/mail, username enumeration and historical APOP security assumptions reviewed. None establishes endpoint identity or protects modern Email Next transport by itself. |
| 14 | Acknowledgements | Acknowledgments and historical lineage reviewed; no additional protocol behavior. |
| 15 | Authors' Addresses | Author end matter reviewed; no protocol requirements. |
| Appendix A | Differences from RFC 1725 | All listed changes reviewed, including optional USER/PASS, UID length, state/error clarifications and deletion policy. |
| Appendix B | Command Index | Every command index entry checked against the corresponding command description. |

## Captured errata dispositions

- Verified529: UIDL nonreuse lasts for the maildrop's lifetime, not merely the lifetime of an ambiguous entity. Apply the correction while retaining the explicit allowance for identical copies sharing a UIDL.
- Verified8627: remove duplicated “to” in the TOP argument description; no behavior change.
- Held1088: duplicated “than” in TOP prose; editorial correction does not change line-count behavior.
- Rejected4852: the verifier confirms that the512-octet bound applies to a single-line response, with multiline behavior explained separately. Do not adopt the rejected report as a new whole-message size limit.

## Retrieval is not event commitment

A POP message number is session-local. UIDL is maildrop-scoped bookkeeping and can be shared by identical copies; it is neither a cryptographic identity nor a substitute for an Email Next event reference. Preserve occurrence information separately from verified event deduplication. A repeated retrieval must not repeat an external effect, and a new session number must not create a new conversation contribution.

DELE marks a message until UPDATE. A failing QUIT may leave a partial deletion result, and a lost final response leaves the client uncertain about the server outcome. Durable receipt and event processing must survive either replay or disappearance on the next retrieval. RSET clears marks in the active session; it is not a distributed rollback of application actions.

POP dot unstuffing is transport decoding. Size counts exclude the added stuffing octets and use CRLF message lines. Do not hash stuffed transport lines or reconstructed local line endings as though they were the protected event bytes. MIME and event decoding follow the retrieval boundary.

## Source inconsistency and security boundary

The command summary places USER/PASS under minimal commands, while Section7 and AppendixA make them optional. The audit records that inconsistency without inventing an approved erratum. The authentication descriptions and modern transport policy govern adapter selection; a legacy example does not authorize plaintext credentials or establish a recipient device's identity. The [capability audit](pop-capabilities.md) separately records RFC2449 state-sensitive negotiation and limits.
