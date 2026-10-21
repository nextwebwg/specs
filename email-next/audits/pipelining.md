---
title: SMTP pipelining audit
sectionNav: true
---

# SMTP pipelining audit

**Coverage:** complete nine-page RFC2920, including all dialogues and end matter; zero matching errata in refreshed dataset. Metadata retrieved19October2026 lists no later update or replacement. [RFC2920](https://www.rfc-editor.org/rfc/rfc2920.html).

| Section | Disposition |
| --- | --- |
| 1 | Latency optimization requires explicit support because older servers can lose buffered commands or mishandle failures. |
| 1.1 | Requirement vocabulary reviewed. |
| 2 | PIPELINING is an argument-free EHLO keyword; no added MAIL/RCPT parameters or verbs. |
| 3 | Use only after successful advertised negotiation on this connection. |
| 3.1 | Check every command status in sequence, including multiline replies. Do not correlate by status value or text. State-changing commands terminate a group unless their extension permits otherwise. Handle DATA354 even after all recipients fail by ending an empty transfer, not sending sensitive content. Nonblocking I/O or correct window handling avoids deadlock. Historic SEND/SOML/SAML/TURN mentions do not require new implementation of obsolete commands. |
| 3.2 | Server replies remain ordered, buffered responses flush appropriately, unknown/state-changing commands are not indefinitely buffered, and input is never discarded after errors. Empty transfer after zero accepted recipients must not create delivery. |
| 4 | Examples cover normal pipelining and both DATA outcomes after all recipients fail; turnaround counts are illustrative, not performance guarantees. |
| 5 | No new authentication or confidentiality provided; existing SMTP threat model remains. |
| 6 | Acknowledgements reviewed. |
| 7 | SMTP successor5321 base reviewed; host requirements and historical predecessor mapping remain dependencies. |
| 8 | Author information reviewed. |
| 9 | Copyright and acknowledgement reviewed. |

## Email/2 consequence

A command batch does not create an atomic all-recipient send. Maintain a command queue and correlate each complete reply by position, retaining every recipient's result. A multiline response belongs to one command; several250 replies do not form one response.

Do not transmit the contribution until DATA is accepted and there is at least one accepted recipient. Unexpected DATA acceptance with no recipients is a synchronization problem, not permission to send content. Terminate that empty DATA phase and consume its final reply before proceeding.

Required cases include mixed recipient outcomes, multiline responses split across network reads, identical response text, all recipients rejected with DATA354, final acceptance followed by a later command's error, and connection loss mid-batch. No real SMTP implementation has been exercised.
