---
title: Content disposition audit
sectionNav: true
---

# Content disposition audit

Content-Disposition communicates presentation intent. It supplies neither a hidden control-message channel nor permission to execute received content. Its filename, date and size parameters remain sender-supplied hints.

**Coverage:** full twelve-page RFC2183 and all four retrieved errata read and individually assessed on 19 October 2026. Current registry policy and extension registrations remain separate review work.

Sources: [RFC2183](https://www.rfc-editor.org/rfc/rfc2183.html), [errata](https://www.rfc-editor.org/errata/rfc2183).

| Section | Disposition |
| --- | --- |
| Boilerplate | Verified1457 corrects relationship: obsoletes RFC1806, not merely updates it. Abstract reviewed. |
| 1 | Presentation and archival hints reviewed; original MIME does not specify comprehensive rendering, supporting the need for a defined new profile. |
| 2 | Optional field, case-insensitive disposition and parameter grammar inherited. Absent disposition leaves presentation to the client. Numeric zones required for date parameters. Token grammar excludes spaces/controls despite shorthand note; reported5330 is not a verified update. |
| 2.1 | Inline suggests immediate display in MIME order subject to multipart semantics; it does not authorize scripting or network access. |
| 2.2 | Attachment requires further user action for display; new profile retains this boundary. |
| 2.3 | Filename is a suggestion for a terminal name, not a directory or mandatory disk write. Prevent overwrite and platform-specific hazards; use RFC2231 successor of2184 for extended values. |
| 2.4 | Creation-date is file metadata; POSIX st_ctime is not creation time. No event ordering or authorship evidence. |
| 2.5 | Modification-date is quoted file metadata, not authenticated event revision. |
| 2.6 | Read-date describes file access metadata; it is not a recipient read receipt or live presence signal. |
| 2.7 | Size is approximate octets; never trust it as actual decoded size, allocation authority or validation limit. |
| 2.8 | Unknown dispositions handled as attachment; unknown parameters ignored. Parameters generally apply to all dispositions unless defined otherwise. No secret discard behavior. |
| 2.9 | Multipart disposition applies to whole container; user opens attachment container before subpart presentation. Related-specific precedence remains as defined by RFC2387. |
| 2.10 | Field may apply to main message body; receiver must not assume it is attachment-only metadata. |
| 3 | All examples reviewed; verified3847 removes trailing semicolon. Text says genome.jpg while sample uses genome.jpeg; use actual parameter in independent fixtures. Indented/placeholder parts are illustrative. |
| 4 | Summary reviewed with extension behavior in2.8; not a closed two-value registry. |
| 5 | Inherit filename hazard examples and prohibition on implicit execution through placement. Platform-specific paths, startup files and command pipes require safe handling. |
| 6 | References reviewed;2184 superseded by2231, other MIME audits tracked. |
| 7 | Acknowledgements reviewed; no protocol behavior. |
| 8 | Contact information reviewed; no protocol behavior. |
| 9 | Historical registration procedures reviewed; current registry policy must be checked before registration. No disposition registration submitted. |
| 10 | All changes from1806 reviewed; base disposition semantics retained. |

## Errata

| Record | Status | Disposition |
| --- | --- | --- |
| [485](https://www.rfc-editor.org/errata/eid485) | Verified | Correct spelling of lengths; no behavior change. |
| [1457](https://www.rfc-editor.org/errata/eid1457) | Verified | RFC2183 obsoletes RFC1806. Preserve correction in dependency reasoning even if source metadata differs. |
| [3847](https://www.rfc-editor.org/errata/eid3847) | Verified | Remove trailing semicolon in example header. |
| [5330](https://www.rfc-editor.org/errata/eid5330) | Reported | Flags shorthand conflicting with token grammar. Generate using the actual MIME token grammar; do not promote proposed text to verified status. |

## Profile consequences

Unknown dispositions remain visible as attachments; inventing a disposition cannot make a legacy client silently discard an exchange. Inline status cannot bypass the rendering sandbox. Opening an attachment permits its requested presentation, not arbitrary execution or submission of an interaction.

File read-date must not feed message read receipts or presence. File modification-date must not determine event ordering. Approximate size must not override measured decoded sizes and resource limits. These distinctions should be tested explicitly because the names can tempt implementers into conflating unrelated concepts.

For related-aware rendering, RFC2387's compound-object processing takes precedence over the disposition type of constituent resources. For ordinary mixed attachments, preserve container-before-child activation. A new-profile generator marks independent attachments as attachment and leaves bundled related-resource selection to the related rules.

Proposed cases include unknown disposition, filename on inline content without disk write, attachment multipart containing inline children, hostile directory-bearing filenames, misleading size, read-date mistaken for a receipt, and related resources labeled attachment. No implementation results are claimed.
