---
title: JMAP Mail audit
sectionNav: true
---

# JMAP Mail audit

The complete captured [RFC8621](https://www.rfc-editor.org/rfc/rfc8621.html) text has been reviewed, including examples, registrations, references and end matter. Its mailbox model supports conversation retrieval, but provider threads, parsed fields and submission status do not replace authenticated Email/2 events.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Mail model sits above core synchronization; mailbox moves retain Email identity. |
| 1.1 | Notational Conventions | All defined type properties are required; inherited notation applies. |
| 1.2 | Terminology | Email is a stored representation, distinct from original message bytes. |
| 1.3 | Additions to the Capabilities Object | Three separate capabilities do not imply one another. |
| 1.3.1 | urn:ietf:params:jmap:mail | Account limits distinguish raw attachment sizes from encoded message sizes. |
| 1.3.2 | urn:ietf:params:jmap:submission | Submission extensions can be implemented locally; advertisement is not every-hop support. |
| 1.3.3 | urn:ietf:params:jmap:vacationresponse | Vacation capability does not establish endpoint reply authority. |
| 1.4 | Data Type Support in Different Accounts | Shared-account mail access does not imply sending permission. |
| 1.5 | Push | EmailDelivery is a push-only new-object hint, not a delivery receipt. |
| 1.5.1 | Example | Read-state changes and new-message notifications have different triggers. |
| 1.6 | Ids | Cross-protocol object identity is recommended only with applicable IMAP support. |
| 2 | Mailboxes | Mailbox memberships, rights, counters and subscriptions are separate from conversation authority. |
| 2.1 | Mailbox/get | Get permits all mailbox ids; partial-access restrictions still apply. |
| 2.2 | Mailbox/changes | Count-only updatedProperties optimization cannot hide other changed properties. |
| 2.3 | Mailbox/query | Tree filtering/sorting and exact versus substring filters retain separate meanings. |
| 2.4 | Mailbox/queryChanges | Query changes inherit core state matching and invalidation. |
| 2.5 | Mailbox/set | Mailbox deletion may destroy otherwise unfiled Emails; not an event withdrawal. |
| 2.6 | Example | Example oldState mismatch must not relax delta matching. |
| 3 | Threads | Provider threading can delete/reinsert records; deduplicate by authenticated event identity. |
| 3.1 | Thread/get | Thread retrieval returns a provider grouping, not authenticated membership. |
| 3.1.1 | Example | Returned Email lists illustrate retrieval, not causal order. |
| 3.2 | Thread/changes | Thread changes remain provider synchronization data. |
| 4 | Emails | Email projections simplify MIME access but do not replace original-byte verification. |
| 4.1 | Properties of the Email Object | Flattened body and attachment lists may overlap. |
| 4.1.1 | Metadata | Object id differs from Message-ID; keywords and internal dates are mutable/contextual evidence. |
| 4.1.2 | Header Fields Parsed Forms | Parsed forms transform source data and have header-specific applicability. |
| 4.1.2.1 | Raw | Raw string form may replace invalid UTF-8 and removes NUL; not original octets. |
| 4.1.2.2 | Text | Unfolding, encoded-word decoding and NFC affect byte-sensitive checks. |
| 4.1.2.3 | Addresses | Best-effort addresses can be invalid for sending; groups/comments may be lost. |
| 4.1.2.4 | GroupedAddresses | Groups are preserved for display, not identity proof. |
| 4.1.2.5 | MessageIds | Parsed message ids remove brackets/CFWS and can fail to null. |
| 4.1.2.6 | Date | Parsed dates do not prove trusted time. |
| 4.1.2.7 | URLs | Extracted list URLs do not authorize execution. |
| 4.1.3 | Header Fields Properties | Single header properties select last occurrence; uniqueness checks require all fields. |
| 4.1.4 | Body Parts | Part ids are local; repaired/truncated body values cannot activate structured controls. |
| 4.2 | Email/get | Fetch defaults omit full original structure; invalid header forms reject the method. |
| 4.2.1 | Example | Illustrative request omits accountId; truncation/notFound outcomes remain explicit. |
| 4.3 | Email/changes | Newer intermediate changes may arrive first; no causal inference. |
| 4.4 | Email/query | Collapsed results are representative Emails, not complete threads. |
| 4.4.1 | Filtering | Text matching is deliberately flexible; search is not exact identity validation. |
| 4.4.2 | Sorting | Provider sorting is display order; required and optional comparators differ. |
| 4.4.3 | Thread Collapsing | Collapse occurs after filtering/sorting and retains first matching representative. |
| 4.5 | Email/queryChanges | Preserve collapseThreads in query cache identity and change requests. |
| 4.6 | Email/set | Creation can generate/repair message representation; preserve old draft until replacement succeeds. |
| 4.7 | Email/copy | Copy cannot modify message content; duplicate rejection may use Message-ID alone. |
| 4.8 | Email/import | Import may repair bytes with changed blobId; inspect before reuse of protection evidence. |
| 4.9 | Email/parse | Parse does not import; predictive threadId does not make an attached message a contribution. |
| 4.10 | Examples | All worked examples reviewed; batching is not a snapshot or atomic save. |
| 5 | Search Snippets | Search highlights are restricted display data, not trusted application HTML. |
| 5.1 | SearchSnippet/get | Match snippets by emailId; no state token or stable excerpt guarantee. |
| 5.2 | Example | Escaped text and mark tags illustrate highlighting without authenticating source meaning. |
| 6 | Identities | Provider sending Identity is not a cryptographic principal; defaults precede protection. |
| 6.1 | Identity/get | Identity retrieval includes sending preferences, not key proofs. |
| 6.2 | Identity/changes | Identity changes do not authorize key continuity transitions. |
| 6.3 | Identity/set | Creation enforces sending permission; forbiddenFrom is distinct from envelope permission. |
| 6.4 | Example | Wildcard identity and archive Bcc examples require explicit audience mapping. |
| 7 | Email Submission | Submission, irreversible relay, delivery and display claims remain distinct. |
| 7.1 | EmailSubmission/get | Missing submission records do not prove unsent status. |
| 7.2 | EmailSubmission/changes | Submission changes track provider reports, not recipient consent. |
| 7.3 | EmailSubmission/query | Filters use sendAt; sentAt sort spelling is a recorded inconsistency. |
| 7.4 | EmailSubmission/queryChanges | Query changes inherit core synchronization scope. |
| 7.5 | EmailSubmission/set | Send success and implicit filing success are separate; deletion does not cancel. |
| 7.5.1 | Example | Two responses share call id; localized rejection differs from success filing. |
| 8 | Vacation Response | Automated responses follow loop controls and do not constitute structured answers. |
| 8.1 | VacationResponse/get | Exactly one vacation object has singleton identity. |
| 8.2 | VacationResponse/set | Settings mutation does not grant endpoint encryption keys to provider. |
| 9 | Security Considerations | Core security plus mail-specific rendering and submission boundaries apply. |
| 9.1 | EmailBodyPart Value | Heuristic decoding and truncation can change semantics and filter outcomes. |
| 9.2 | HTML Email Display | Allowlisting, parser agreement, isolation and resource controls need implementation validation. |
| 9.3 | Multiple Part Display | Render each body part separately; raw concatenation can expose decrypted content. |
| 9.4 | Email Submission | Proxy authentication and filtering do not provide endpoint authorship. |
| 9.5 | Partial Account Access | Inaccessible records appear absent; duplicate errors may disclose hidden existence. |
| 9.6 | Permission to Send from an Address | From and MAIL FROM permissions differ; redirect exception is not identity delegation. |
| 10 | IANA Considerations | Registration entries do not establish Email/2 adoption. |
| 10.1 | JMAP Capability Registration for "mail" | Mail capability registration does not include submission authority. |
| 10.2 | JMAP Capability Registration for "submission" | Submission capability registration remains separately scoped. |
| 10.3 | JMAP Capability Registration for "vacationresponse" | Vacation capability registration describes automatic-response settings. |
| 10.4 | IMAP and JMAP Keywords Registry | Registry gains protocol scope; reserved names and other-protocol flags may be ignored. |
| 10.4.1 | Registration of JMAP Keyword "$draft" | Draft flag may alter filing/display and disclose activity to shared readers. |
| 10.4.2 | Registration of JMAP Keyword "$seen" | Seen is advisory shared metadata, not signed read evidence. |
| 10.4.3 | Registration of JMAP Keyword "$flagged" | Flagged may affect mailbox presentation and expose user preference. |
| 10.4.4 | Registration of JMAP Keyword "$answered" | Answered flag does not identify or authenticate an answer. |
| 10.4.5 | Registration of "$recent" Keyword | Recent is reserved, not a JMAP new-message mechanism. |
| 10.5 | IMAP Mailbox Name Attributes Registry | Mailbox attributes registry scope remains distinct from protocol identities. |
| 10.5.1 | Registration of "inbox" Role | Inbox role is registered for JMAP usage. |
| 10.6 | JMAP Error Codes Registry | Error registrations retain their owning operation scopes. |
| 10.6.1 | mailboxHasChild | Child mailboxes prevent parent destruction. |
| 10.6.2 | mailboxHasEmail | Nonempty mailbox destruction needs the explicit removal option. |
| 10.6.3 | blobNotFound | Missing referenced blobs prevent object creation. |
| 10.6.4 | tooManyKeywords | Keyword limits are provider constraints, not conversation quotas. |
| 10.6.5 | tooManyMailboxes | Mailbox membership limits do not authorize silent removal. |
| 10.6.6 | invalidEmail | Invalid email is a validation failure, not permission to weaken protection. |
| 10.6.7 | tooManyRecipients | Recipient limit failure must not silently shrink audience. |
| 10.6.8 | noRecipients | Empty recipient envelope cannot be treated as a send. |
| 10.6.9 | invalidRecipients | Invalid recipients require explicit correction, not guessed addresses. |
| 10.6.10 | forbiddenMailFrom | Envelope sender permission is separately enforced. |
| 10.6.11 | forbiddenFrom | Visible From permission is separately enforced. |
| 10.6.12 | forbiddenToSend | Sending denied is distinct from a delivery failure after acceptance. |
| 11 | References | Reference entries read; substantive dependency review remains separate. |
| 11.1 | Normative References | Mail, MIME, ACL, Unicode, transport and authentication dependencies need reconciliation. |
| 11.2 | Informative References | HTML/EFAIL, IMAP/DMARC successors and de facto proxy interfaces remain scoped followups. |

## Source status and inconsistencies

The [RFC information page](https://www.rfc-editor.org/info/rfc8621/) identifies Proposed Standard status. The source updates RFC5788's keyword registry. No RFC8621 entries occur in the captured full errata corpus; this does not prove live errata completeness or absence of defects.

Observed inconsistencies include a mailbox-change example whose oldState differs from the requested sinceState, address examples that lose the accent in a decoded name, a submission sort named sentAt where the object defines sendAt, and mdnblobIds in prose where the property is mdnBlobIds. Some requests omit accountId and examples contain ellipses or wrapped strings. These observations are not approved corrections or executable conformance vectors. An adapter must not silently relax state matching, identity handling or required fields to accept them.

## Application and remaining work

The [mailbox integration contract](../mailbox-integration.md) separates mailbox identities, permissions, query views, original bytes, imports, submission and receipts. The [rendering contract](../rendering.md) requires body-part isolation. No JMAP provider adapter or independent-client interoperability is established by this audit.

The [core JMAP audit](jmap-core.md), blob and sharing extensions are separately recorded. Dependency closure still requires reconciliation of ACLs, object identifiers, Unicode, SORT/THREAD, authentication mechanisms, delayed submission, HTML/CSP, EFAIL and proxy interfaces, plus current IMAP and DMARC successors. Registry status, implementation behavior and the reported source inconsistencies require further validation.
