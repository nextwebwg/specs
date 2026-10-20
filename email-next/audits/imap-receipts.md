---
title: Shared-mailbox receipt audit
sectionNav: true
---

# Shared-mailbox receipt audit

**Coverage:** complete nine-page [RFC 3503](https://www.rfc-editor.org/rfc/rfc3503.html), including timelines, all examples, grammar, references and end matter. No matching errata occur in the retrieved full dataset; RFC Editor metadata lists no updates or replacements. Referenced-protocol closure remains open.

| Section | Disposition |
| --- | --- |
| 1 | Requirement vocabulary and transcript notation reviewed. |
| 2 | Shared permanent keyword coordinates suppression across MUAs; it adds no command and does not prove receipt transmission. |
| 3 | Check PERMANENTFLAGS; never set unsupported permanent keyword. Handle STORE refusal, normally suppress sending if storage fails. Never clear marker. Denial may set it. Recent is not a trigger; other standard flags do not substitute. Historical disposition values require current RFC8098 reconciliation. |
| 3.1 | MDNSent suppresses generation regardless of other flags; Draft also prevents receipts for incomplete mail. |
| 3.2 | Verify marker preservation on COPY; cross-server APPEND must carry correct suppression state. |
| 3.3 | Saved sent-message copies must carry marker to prevent another client's receipt. |
| 3.4 | Saved unfinished messages must carry marker. |
| 4 | Server must satisfy keyword storage profile; ACL support adds separate rules. |
| 4.1 | Arbitrary keyword storage suffices without a new command. |
| 4.2 | Specific-keyword servers preserve marker on COPY and support corresponding keyword search. |
| 4.3 | Preserve on COPY even without keyword-write permission where recommended, but COPY authorization still applies. Current ACL dependency remains open. |
| 5 | All four transcript cases read. Keyword case insensitive. SEARCH KEYWORDS in example conflicts with singular KEYWORD described in4.2; do not copy the example as validated syntax. |
| 6 | Inherited MDN/IMAP threats and ACL behavior changes reviewed; no stronger concurrency guarantee supplied. |
| 7 | Case-insensitive keyword syntax reviewed; mailbox marker is not a message-header capability token. |
| 8 | Acknowledgments read. |
| 9 | Historical MDN, IMAP and ACL references reviewed; current successors require separate audits. |
| 10 | Author material read. |
| 11 | Copyright and final acknowledgment read. |

## What the marker establishes

`$MDNSent` means that another receipt must be suppressed. It may represent a refusal to send, a saved sent copy or an unfinished draft. It does not prove an MDN was transmitted, delivered or read. A client must preserve that distinction in its interface and state model.

The profile does not specify an atomic claim spanning IMAP state and SMTP submission. Concurrent clients can both observe an absent marker, and a crash can occur between storage and sending. This is an inference from the described operations, not a claim that the RFC promises exactly-once behavior. Any stronger Email Next guarantee requires an explicit coordination and recovery contract.

## Current-protocol reconciliation

The timeline mentions historical `denied` and `failed` dispositions; use the current [RFC 8098 audit](disposition-notifications.md) rather than reviving removed values. The example's `SEARCH KEYWORDS` spelling is not adopted as a command fixture. Current IMAP and ACL grammar must govern implementation.

The [transport contract](../transport.md) now preserves keyword scope, storage failure, copy behavior and evidence limits. Multi-client races, crash recovery, unsupported keywords, denied STORE, draft copies and cross-server copies still require implementation tests. Full IMAP and ACL dependency reviews remain pending.
