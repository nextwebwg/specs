---
title: Sieve mailbox identity audit
sectionNav: true
---

# Sieve mailbox identity audit

The complete base text of [RFC9042](https://www.rfc-editor.org/rfc/rfc9042.html), including syntax, examples, references, acknowledgments and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. This does not establish dependency closure or live registry verification.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Stable server mailbox identifiers prevent rename races in recipient-created filtering rules; not endpoint or conversation identities. |
| 2 | Conventions Used in This Document | BCP14 uppercase requirement convention reviewed. |
| 3 | Sieve Capability String | Scripts must explicitly require mailboxid; this is interpreter capability, not sender authorization. |
| 4 | Argument :mailboxid to Command fileinto | Fileinto searches the personal namespace by ID and otherwise falls back to the positional mailbox name; absent ID does not force failure. |
| 4.1 | Interaction with Mailbox Extension | Create with a missing ID creates the named mailbox with a new server-chosen ID; the script cannot assign the requested ID. |
| 4.2 | Interaction with Special-Use Extension | Combining mailboxid and specialuse on one fileinto is an error; explicit tests can select alternatives. |
| 5 | Interaction with FCC Extension | FCC supports mailboxid with name fallback; mailboxid and specialuse together remain an error. Generated-message copies are not secure endpoint acknowledgments. |
| 6 | Test mailboxidexists | Every supplied ID must exist and permit delivery; ACL p or i rights qualify, or READ-WRITE without ACL. Success does not guarantee later delivery or quota availability. |
| 7 | Interaction with Variables Extension | IDs may contain variable expansions when variables is enabled; expansion supplies no authentication. |
| 8 | Security Considerations | Mailbox IDs remain server-generated even with create; Sieve and OBJECTID security dependencies remain separate. |
| 9 | IANA Considerations | Registers mailboxid in the Sieve extensions registry; live registration verification is separate. |
| 10 | References | References, acknowledgments and author end matter reviewed. |
| 10.1 | Normative References | Namespace, Sieve, OBJECTID, FCC, ABNF and requirement-keyword dependencies are separately scoped. |
| 10.2 | Informative References | Legacy IMAP, ACL, variables, mailbox metadata and special-use interactions reviewed as references, not claimed fully audited here. |

## Application to control-message storage

An upgraded provider can use a stable mailbox ID for recipient-authorized routing, avoiding accidental changes when a folder is renamed. This is a useful existing mechanism, but its fallback semantics matter: losing the target ID can deliver to the positional mailbox name. A successful existence test is also not a reservation and does not remove delivery failures such as quota exhaustion.

Email/2 must therefore separate ordinary mailbox storage from a negotiated control service's guarantees. A folder can remain visible to legacy clients, and its ID does not authenticate a message or recipient device. Any service promising hidden control handling needs its own explicit behavior for missing storage, permission changes and failed writes. A silently substituted mailbox cannot satisfy that promise.
