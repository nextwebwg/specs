---
title: Internet mail architecture audit
sectionNav: true
---

# Internet mail architecture audit

The complete captured [RFC5598](https://www.rfc-editor.org/rfc/rfc5598.html) text has been reviewed, including references, acknowledgments and end matter. This informational architecture supplies role vocabulary; protocol-specific requirements remain authoritative. The review informed the proposal's separation of delivery routes, authenticated principals and endpoint authority.

## Section dispositions

| Section | Topic | Disposition |
| --- | --- | --- |
| [1](https://www.rfc-editor.org/rfc/rfc5598.html#section-1) | Introduction | architectural vocabulary separates SMTP transfer, IMF object and MIME content extension. Informational descriptive document, not an overriding normative source. |
| [1.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-1.1) | History | distinguish user-level interoperability from transfer-path interoperability. Asynchronous operation and absence of simultaneous online presence are core architecture properties. Proposal inference: live exchange supplements rather than replaces offline mail; lack of presence never grants downgrade permission. |
| [1.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-1.2) | The Role of This Architecture | architecture is descriptive/post hoc and permits explained implementation divergence. Do not convert its high-level account into protocol conformance requirements without source-specific checks. |
| [1.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-1.3) | Document Conventions | preserve distinctions between RFC5322.From and RFC5321.MailFrom; shorthand names must not collapse envelope and authored identity. |
| [2](https://www.rfc-editor.org/rfc/rfc5598.html#section-2) | Responsible Actor Roles | Adopt role distinctions for analysis; responsibilities are not synonymous with software modules. |
| [2.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.1) | User Actors | Keep user-level interaction separate from transfer handling. |
| [2.1.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.1.1) | Author | Authored audience and content require application authorization, independently of submission. |
| [2.1.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.1.2) | Recipient | Receipt and reply remain distinct actions; receiving is not consent. |
| [2.1.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.1.3) | Return Handler | Return-handler address is not evidence of author identity or decryption membership. |
| [2.1.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.1.4) | Mediator | Mediated redistribution is a new submission; no inferred original-author permission to expand protected audience. |
| [2.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.2) | Message Handling Service (MHS) Actors | Delivery service does not itself maintain conversation authority. |
| [2.2.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.2.1) | Originator | Submission validation/accountability is not proof of original authorship. |
| [2.2.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.2.2) | Relay | Transfer representation changes must preserve authenticated inner bytes; source descriptions do not authorize arbitrary content rewrites. |
| [2.2.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.2.3) | Gateway | Gateway compatibility does not create authority to decrypt or impersonate an author. |
| [2.2.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.2.4) | Receiver | Redirected delivery does not imply identity/key continuity. |
| [2.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-2.3) | Administrative Actors | Provider boundary and policy enforcement do not imply endpoint trust; transport and content authorization remain distinct. |
| [3](https://www.rfc-editor.org/rfc/rfc5598.html#section-3) | Identities | distinguish each identifier's scope; architectural uniqueness is not authentication or collision evidence. |
| [3.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.1) | Mailbox | local-part is domain-interpreted; no generic dot/plus normalization for principal continuity. Source-route and specialized gateway syntax remain delegated to their defining specifications. |
| [3.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.2) | Scope of Email Address Use | address use as online identity does not establish security-profile identity. |
| [3.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.3) | Domain Names | domain/service identity does not identify a human or device by itself. |
| [3.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.4) | Message Identifier | preserve content-versus-transfer distinction. |
| [3.4.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.4.1) | Message-ID | Message-ID is insufficient for security-sensitive reference equality; structured edits use authenticated exact references. New corrections get fresh outer identifiers under the proposed generation profile. |
| [3.4.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-3.4.2) | ENVID | ENVID follows a transfer, not an immutable conversation contribution. Reposting and retry identities require transport-specific rules. |
| [4](https://www.rfc-editor.org/rfc/rfc5598.html#section-4) | Services and Standards | functional modules do not identify security principals; mapping implementations onto them needs explicit trust boundaries. |
| [4.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.1) | Message Data | preserve distinction between transport envelope, message header and MIME body. DSN, MDN and Sieve serve different roles and cannot become generic interaction consent. Historical MDN/media-registration citations require their separately audited successors. |
| [4.1.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.1.1) | Envelope | trace is not an authenticated contribution reference; preserve original message evidence independently. |
| [4.1.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.1.2) | Header Fields | extensibility of headers does not imply preservation by gateways. Missing capability advertisement cannot authorize downgrade. |
| [4.1.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.1.3) | Body | MIME hierarchy is handled by the existing MIME audit/profile rather than inferred from architectural prose. |
| [4.1.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.1.4) | Identity References in a Message | identity table's actor/field distinctions support independent reply-target discovery. Reply-To cannot transfer author keys; visible destination fields cannot establish complete delivery or protected audience. Return address, list identity and network-hop identity do not authenticate an endpoint principal. |
| [4.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.2) | User-Level Services | human interaction intent is not inferred from transport behavior. |
| [4.2.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.2.1) | Message User Agent (MUA) | an MUA can be distributed or automated; security endpoint labels must follow actual key/plaintext processing. Folder names are not protocol state. Automatic responses retain RFC3834-specific limits. |
| [4.2.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.2.2) | Message Store (MS) | remote/local storage location does not itself determine decryption authority. |
| [4.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.3) | MHS-Level Services | retain transfer-level versus user-level distinction. |
| [4.3.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.3.1) | Mail Submission Agent (MSA) | posting transfers responsibility; submission rewriting must occur before protected content is frozen or respect protected representation. RFC4409 citation requires successor handling, already separately scoped. |
| [4.3.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.3.2) | Message Transfer Agent (MTA) | distinguish representation changes from semantic changes; retransmission robustness is not a durable application-effect transaction. Routing identity is not recipient key authority. |
| [4.3.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.3.3) | Mail Delivery Agent (MDA) | delivery to mailbox is not display, read, consent or form submission. Redirect preferences do not prove principal continuity. |
| [4.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.4) | Transition Modes | push/pull transfer direction is independent of endpoint encryption and online negotiation; no online-presence prerequisite inferred. |
| [4.5](https://www.rfc-editor.org/rfc/rfc5598.html#section-4.5) | Implementation and Operation | implementation placement and synchronized message stores need explicit authorization/state models; synchronized folders are not authenticated conversation convergence. |
| [5](https://www.rfc-editor.org/rfc/rfc5598.html#section-5) | Mediators | forwarded content, replies and annotations retain distinct authorship/evidence. “Preserving tone” is not preservation of authenticated bytes. |
| [5.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-5.1) | Alias | alias expansion changes routing destinations and can fan out. It cannot transfer principal identity or authorize new decryption members. Hidden expansion is not an authenticated audience roster. |
| [5.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-5.2) | ReSender | Resent-* records redistribution context, not original-author authorization of a new audience or keys. |
| [5.3](https://www.rfc-editor.org/rfc/rfc5598.html#section-5.3) | Mailing Lists | list transformations and archives require explicit confidentiality handling. A list-modified Reply-To can expand the reply audience; composer must surface actual intended recipients and protection policy. |
| [5.4](https://www.rfc-editor.org/rfc/rfc5598.html#section-5.4) | Gateways | gateway semantic conversion can invalidate protected content; display transformed content with separate evidence and never inherit original authentication for changed bytes. |
| [5.5](https://www.rfc-editor.org/rfc/rfc5598.html#section-5.5) | Boundary Filter | security filtering can alter content; operational filtering authority does not produce original-author signatures over the result. |
| [6](https://www.rfc-editor.org/rfc/rfc5598.html#section-6) | Considerations | contextual considerations, not a new protocol. |
| [6.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-6.1) | Security Considerations | transport authentication/encryption is distinct from endpoint protection. Historical crypto citations require modern successor review. Spoofable source/network identifiers cannot become account-key authority. |
| [6.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-6.2) | Internationalization | architecture's experimental EAI and blanket access-protocol descriptions are historical. Apply reviewed SMTPUTF8/internationalized-header/access-protocol successors, not the old wording as a current support guarantee. Keep charset, transfer encoding and address syntax separate. |
| [7](https://www.rfc-editor.org/rfc/rfc5598.html#section-7) | References | Reference lists reviewed; citation does not establish applicability or completed dependency review. |
| [7.1](https://www.rfc-editor.org/rfc/rfc5598.html#section-7.1) | Normative References | Normative references seed protocol-specific successor and applicability review; no blanket inheritance. |
| [7.2](https://www.rfc-editor.org/rfc/rfc5598.html#section-7.2) | Informative References | Historical and specialist references are scoped separately, including gateway and security dependencies. |
| [Appendix A](https://www.rfc-editor.org/rfc/rfc5598.html#appendix-A) | Acknowledgments | Acknowledgments reviewed with index and author end matter; no additional protocol requirements. |

## Errata and status

The captured metadata lists no update or obsolescence relationships. The live information page confirms Informational status. The live all-status errata listing on 20 October 2026 matches the retained record set, statuses, original/corrected text and notes. Current metadata confirms the recorded relationships.

| Erratum | Captured status | Disposition |
| --- | --- | --- |
| [3260](https://www.rfc-editor.org/errata/eid3260) | Verified; editorial | Use Message Submission Agent terminology; no authority or transport change. |
| [2956](https://www.rfc-editor.org/errata/eid2956) | Held for Document Update | Figure 5 is not an exhaustive inventory of transfer mechanisms. |
| [3282](https://www.rfc-editor.org/errata/eid3282) | Held for Document Update | Describe actual provider roles rather than relying on ambiguous labels. |
| [7150](https://www.rfc-editor.org/errata/eid7150) | Reported | Simplified reporting paths do not establish complete implementation behavior. |
| [5925](https://www.rfc-editor.org/errata/eid5925) | Reported | Proposed supersession of SMTP text is not an approved protocol update. |

## Application and remaining dependencies

The [baseline](../baseline.md) explains client/provider upgrades, aliases and mediated forwarding with examples. [Discovery](../capability-discovery.md#choosing-whose-capability-to-check) separates reply destinations from identity continuity. [Security](../security.md#where-the-endpoint-runs) identifies where keys and plaintext are processed. [Event references](../event-identifiers.md#ordinary-email-identifiers) remain separate from ordinary threading identifiers.

Historical EAI, IMAP, submission, media-registration and cryptographic citations require their separately tracked successors. Gateway security, alternative transfer services, distributed stores, specialist addressing and operational-policy references remain subject to applicability and dependency review. Completing this base-text review does not close those dependencies or demonstrate interoperable behavior.
