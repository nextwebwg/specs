---
title: Sieve IMAP events audit
sectionNav: true
---

# Sieve IMAP events audit

The complete base text of [RFC6785](https://www.rfc-editor.org/rfc/rfc6785.html), including syntax, examples, references, acknowledgments and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. This does not establish dependency closure or live registry verification.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Extends filtering beyond final delivery to message-store events. |
| 1.1 | Overview | Requires metadata, environment and flag support; server processing can benefit intermittently connected clients. |
| 1.2 | Differences between IMAP Events and Mail Delivery | APPEND may lack any delivery envelope or original sender context; bulk user actions can trigger many independent script runs. |
| 1.3 | Conventions Used in This Document | Requirement-keyword conventions reviewed. |
| 2 | The "IMAP Events in Sieve" Extension | Defines IMAP-event execution, not authenticated Email/2 events. |
| 2.1 | The "imapsieve" Capability Strings | One IMAPSIEVE ManageSieve endpoint is advertised; scripts require imapsieve and directly used environment support explicitly. |
| 2.2 | Existing IMAP Functions Affected by IMAP Events in Sieve | Each affected message triggers separately; execution may be parallel, so no global serial order is supplied. |
| 2.2.1 | The IMAP APPEND Command | APPEND triggers configured scripts; MULTIAPPEND invokes once per created message. |
| 2.2.2 | The IMAP COPY Command | COPY triggers scripts on newly created copies under selected metadata. |
| 2.2.3 | Changes to IMAP Message Flags | Flag changes expose post-change flags; implementations must prevent loops and should suppress recursive flag-triggered invocation. |
| 2.2.4 | When Script Actions Set the \Deleted Flag | Action-induced Deleted flags do not invoke another script; optional expunge targets only affected messages, not unrelated deletions. |
| 2.3 | New Functions Defined by IMAP Events in Sieve | Metadata supplies script selection. |
| 2.3.1 | Interaction with Metadata | Mailbox metadata takes precedence over server metadata; an empty, missing-script or unusable mailbox selection does not fall back to the server script. ManageSieve support is required. |
| 3 | Applicable Sieve Actions and Interactions | Action semantics depend on this execution context and each extension's interaction rules. |
| 3.1 | The Implicit Keep | Implicit keep preserves the original immutable message; transient content modifications are not retained. |
| 3.2 | The "keep" Action | Explicit keep has the same original-message preservation semantics. |
| 3.3 | The "fileinto" Action | Fileinto creates a separate message and does not trigger another IMAP event; without keep the original is marked Deleted, not silently never stored. |
| 3.4 | The "redirect" Action | Redirect can submit a message with reconstructed envelope/header information; original storage remains and without keep is marked Deleted. Submission fix-up is not preservation of authenticated bytes. |
| 3.5 | The "discard" Action | Discard first stores APPEND/COPY input, then marks Deleted unless explicit keep applies; this is not invisible delivery. |
| 3.6 | The "notify" Action | Notify sends a notification while normal message handling otherwise continues. |
| 3.7 | The "addheader" and "deleteheader" Actions | Header edits are transient for outgoing/new copies and do not mutate a kept message in place. |
| 3.8 | The "setflag", "deleteflag", and "removeflag" Actions | Flag actions and hasflag operate on current flags; recursive execution must be prevented. Heading naming does not substitute for the referenced flag extension's action definitions. |
| 3.9 | MIME Part Tests and Replacement | MIME replacement/enclosure is transient and cannot rewrite the kept immutable original. |
| 3.10 | spamtest and virustest | Spam and virus tests may apply; their results are not endpoint identity evidence. |
| 3.11 | Inapplicable Actions | Reject, ereject and vacation requirements or use terminate an IMAP-event script with an error. |
| 3.12 | Future Sieve Actions | Future action extensions must specify IMAP-event applicability; delivery-only actions remain inapplicable. |
| 4 | Interaction with Sieve Environment | Environment describes invocation context, not authenticated message authorship. |
| 4.1 | Base Sieve Environment Items: location and phase | Location is MS and phase is post, including APPEND that may replace delivery entirely. |
| 4.2 | New Sieve Environment Items: imap.user and imap.email | imap.user and imap.email identify the acting IMAP user; both are empty during normal final delivery. |
| 4.3 | New Sieve Environment Item: imap.cause | APPEND, COPY and FLAG identify causes; future causes require requested extension capabilities. |
| 4.4 | New Sieve Environment Item: imap.mailbox | Mailbox name is fixed at invocation and is not changed by fileinto. |
| 4.5 | New Sieve Environment Item: imap.changedflags | Changedflags lists changed names, not set/reset direction; inspect current flags for direction. Other causes yield empty text. |
| 4.6 | Interaction with Sieve Tests (Comparisons) | Envelope tests are forbidden and generate runtime errors outside final delivery; other comparisons are unchanged. |
| 5 | Examples | All three examples reviewed: copy-based redirect, changed-flag notification and post-TLS capability discovery; none proves authenticated receipt. |
| 6 | Security Considerations | Prevent flag, redirect and notify loops; fileinto does not recursively invoke scripts. Innocuous flag changes can leak appended plaintext drafts through redirect. |
| 7 | IANA Considerations | Capability, environment and metadata registrations reviewed; current registry checks remain separate. |
| 7.1 | Registration of "imapsieve" IMAP Capability | Registers IMAPSIEVE= as an IMAP capability. |
| 7.2 | Registration of "imapsieve" Sieve Extension | Registers imapsieve as a Sieve extension. |
| 7.3 | Registration of Sieve Environment Items | Registers invocation environment items. |
| 7.3.1 | Registration of Sieve Environment Item: imap.cause | Registers imap.cause with APPEND, COPY and FLAG values. |
| 7.3.2 | Registration of Sieve Environment Item: imap.mailbox | Registers fixed invocation mailbox name. |
| 7.3.3 | Registration of Sieve Environment Item: imap.changedflags | Registers changed flag names or empty value. |
| 7.3.4 | Registration of Sieve Environment Item: imap.user | Registers the acting user's IMAP login identity. |
| 7.3.5 | Registration of Sieve Environment Item: imap.email | Registers the acting user's primary email address. |
| 7.4 | Registration of IMAP METADATA Mailbox Entry Name | Registers shared mailbox script metadata as UTF-8 plain text. |
| 7.5 | Registration of IMAP METADATA Server Entry Name | Registers server fallback script metadata; mailbox entry presence takes precedence. |
| 8 | References | Both reference lists and author end matter reviewed. |
| 8.1 | Normative References | IMAP, MULTIAPPEND, copy, environment, flags, metadata, ManageSieve and submission dependencies remain separately scoped. |
| 8.2 | Informative References | UIDPLUS, vacation, spam tests, header editing, reject, notify and MIME extensions require their own reviews. |

## Application boundary

IMAP events are storage events, not new authenticated contributions. Copying an old message or changing a flag must not repeat an Email/2 operation. Script-driven redirects can export plaintext drafts, and discard may leave a stored message visible until expunge. Neither action provides an invisible negotiation channel.

Per-message script execution may be concurrent. A provider integration still needs authenticated event deduplication and atomic effects independently of Sieve invocation. Mailbox metadata may intentionally disable a server-level script; the presence of an IMAPSIEVE capability alone does not prove that a particular message was processed.
