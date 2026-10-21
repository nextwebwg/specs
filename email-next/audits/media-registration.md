---
title: Media type registration audit
sectionNav: true
---

# Media type registration audit

The complete 1795-line captured text of [RFC6838](https://www.rfc-editor.org/rfc/rfc6838.html), including both templates, grammar, appendices, references and end matter, has been reviewed. No RFC6838 entries occur in the captured full errata corpus. The live all-status listing on 20 October 2026 explicitly reports no matching errata. The RFC Editor status page confirms the RFC9694 update; its [separate review](media-top-level.md) covers new top-level types. Dependency closure remains open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Registration coordinates format identifiers; it is separate from transport support. |
| 1.1 | Historical Note | Mail compatibility motivates common profiles, not a ban on new types. |
| 1.2 | Conventions Used in This Document | BCP14 and ABNF conventions reviewed. |
| 2 | Media Type Registration Preliminaries | Proposal, tree-specific review and acceptance precede registration claims. |
| 3 | Registration Trees and Subtype Names | Registration trees and top-level types are different dimensions. |
| 3.1 | Standards Tree | Standards-tree eligibility and ownership require the specified IETF or recognized-organization process; NextWebWG recognition is not assumed. |
| 3.2 | Vendor Tree | Noncommercial producers can use the vendor tree; ownership, third-party submissions and expert review apply. |
| 3.3 | Personal or Vanity Tree | Personal-tree registration is available for experiments; it is not an unregistered namespace. |
| 3.4 | Unregistered x. Tree | Private x-dot types require active agreement and are discouraged; x-hyphen has different historical treatment. |
| 3.5 | Additional Registration Trees | A new tree requires Standards Action; unnecessary for this proposal. |
| 4 | Registration Requirements | Tree-specific requirements reviewed with each subsection. |
| 4.1 | Functionality Requirement | Register a real format, not base64 or a charset disguised as a media type. |
| 4.2 | Naming Requirements | Case-insensitive names, restricted grammar, 127-character limit and 64-character recommendation reviewed; final plus and first dot have defined roles. |
| 4.2.1 | Text Media Types | New text subtypes must define charset determination; structured application events need not be labeled text merely because JSON is textual. |
| 4.2.2 | Image Media Types | Image classification does not validate an attachment or authorize a decoder. |
| 4.2.3 | Audio Media Types | Audio classification does not establish safe playback or codec support. |
| 4.2.4 | Video Media Types | Video can include coordinated audio/text; content-type alone does not justify active handling. |
| 4.2.5 | Application Media Types | Application is suitable for machine-processed interactions; the scheduling example is relevant prior art, not an automatic-action permission. |
| 4.2.6 | Multipart and Message Media Types | Composite types retain RFC2046 rules as amended by RFC6532; new labels do not bypass MIME transfer restrictions. |
| 4.2.7 | Additional Top-Level Types | Read with the separately audited RFC9694 update; no new top-level type is proposed. |
| 4.2.8 | Structured Syntax Name Suffixes | Suffix must match actual syntax and its registered rules; +json grants generic syntax handling, not Email/2 semantics. |
| 4.2.9 | Deprecated Aliases | Preferred name and deprecated aliases require explicit handling; aliases do not create additional formats. |
| 4.3 | Parameter Requirements | Parameter syntax, values and meaning must be defined; duplicates are errors, order irrelevant, and parameters are not an unrestricted feature-negotiation channel. |
| 4.4 | Canonicalization and Format Requirements | Canonical format and public specification requirements reviewed; this does not instruct receivers to reserialize signed payload bytes. |
| 4.5 | Interchange Recommendations | Known interoperability issues must be recorded without claiming universal support. |
| 4.6 | Security Requirements | Active effects, privacy, expansion hazards and external confidentiality/integrity dependencies require accurate disclosure. |
| 4.7 | Requirements Specific to XML Media Types | XML-specific obligations are not selected for the JSON event format; historical XML reference needs its update chain if used. |
| 4.8 | Encoding Requirements | Encoding consideration describes payload octets, not the chosen MIME transfer encoding; binary is not a guarantee of binary SMTP support. |
| 4.9 | Usage and Implementation Non-Requirements | Registration does not require universal deployment; use restrictions and the application profile remain separate. |
| 4.10 | Publication Requirements | Publication and copying permissions reviewed; registration is not general IETF endorsement or certification. |
| 4.11 | Fragment Identifier Requirements | Fragment behavior must respect any selected suffix; URI fragments do not grant authority over event references. |
| 4.12 | Additional Information | Magic, filename extensions and platform codes are optional identification aids, not authenticated evidence. |
| 5 | Media Type Registration Procedures | Registration is an administrative process, distinct from standards approval. |
| 5.1 | Preliminary Community Review | Community review solicits format/security/interoperability feedback; no message has been sent by this audit. |
| 5.2 | Submit Request to IANA | Submission paths and organization-dependent review requirements reviewed; no request has been filed. |
| 5.2.1 | Provisional Registrations | Provisional standards-tree names require the stated eligibility; temporary assignments may be abandoned and are not final registrations. |
| 5.3 | Review and Approval | Expert review, appeal and recognized-organization checks apply; project naming alone cannot satisfy them. |
| 5.4 | Comments on Media Type Registrations | Comments may update public registration evidence through review, not by changing a local document alone. |
| 5.5 | Change Procedures | Change control, obsolescence, compatibility and ownership transfer reviewed; deployed semantics cannot be silently replaced. |
| 5.6 | Registration Template | Every template field reviewed, including explicit N/A, intended use, restrictions, contacts, change control and provisional status. |
| 6 | Structured Syntax Suffix Registration Procedures | Suffix registration, collision checking and expert review are separate from registering a subtype. |
| 6.1 | Change Procedures | Suffix changes follow their original approval mechanism. |
| 6.2 | Structured Syntax Suffix Registration Template | All suffix template fields reviewed; security assessment is mandatory for suffixes. |
| 7 | Security Considerations | Security analysis refers to the substantive requirements in section4.6. |
| 8 | IANA Considerations | Registry history, provisional restrictions and contact changes reviewed; repetitive standards-tree sentence recorded as a wording defect, not an extra rule. |
| 9 | Acknowledgments | Acknowledgments and source provenance reviewed. |
| 10 | References | Both complete reference lists and author end matter reviewed. |
| 10.1 | Normative References | Normative references require separate applicability and update-chain closure. |
| 10.2 | Informative References | Historical references inform interpretation; they are not automatically current requirements. |
| Appendix A | Grandfathered Media Types | Grandfathering needs the stated review and approvals; not a shortcut for choosing a new unregistered name. |
| Appendix B | Changes since RFC 4288 | All listed changes from RFC4288 reviewed, including suffixes, provisional registration, aliases and naming grammar. |

## Consequences for Email/2

Use the application category for machine-processed events. A vendor-tree registration can support a noncommercial implementation project without claiming recognized standards-body status. A future standards-tree registration requires its applicable eligibility and review process. Neither NextWebWG's name nor a published proposal establishes IESG recognition. No registration request, provisional assignment or approval has been obtained by this work.

The [IANA media-type registry](https://www.iana.org/assignments/media-types), consulted on 19 October 2026, is the authority for assigned names. This review does not reserve a name or certify its availability. The event experiment uses the unregistered candidate defined in the registration proposal. The MLS application/octet-stream carrier remains an explicitly agreed local fixture. Neither registration nor experimental signaling promises invisible legacy delivery.

A final registration must describe exact payload syntax, parameters, charset determination, encoding considerations, fragment behavior, security and interoperability concerns, intended use and change control. The selected strict JSON event encoding preserves original payload octets for proofs. The registration's canonical-format requirement must not be misread as permission to normalize or reserialize an authenticated object before verification.

For JSON events, use a registered suffix only after its applicable rules are reviewed. Do not infer executable semantics from generic JSON support. For MLS, binary payload classification alone does not settle email transfer encoding: composite message types still require reconciliation with RFC2046 and RFC6532 and the particular registration. The generic local opaque-attachment experiment avoids claiming that this issue is already settled.

Section8 contains a repetitive statement about standards-tree registrations being allowed in the standards tree. The surrounding provisional-registration scope and eligibility rules are clear, but this audit does not invent an approved correction. References to older HTTP, XML and IANA-policy documents also require their applicable update chains before reuse.

## Remaining evidence

The subtype and suffix choice, full registration template, final MIME layout, independent parsing and legacy-client behavior remain implementation and standardization work. Registration cannot demonstrate encryption, capability support, safe actions, secure content handling or interoperability. Those claims require their own evidence.
