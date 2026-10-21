---
title: Top-level media type audit
sectionNav: true
---

# Top-level media type audit

The complete base text of [RFC9694](https://www.rfc-editor.org/rfc/rfc9694.html), including examples, history, registry table, references and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. Live registry verification and reference closure remain separate work.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Top-level types differ from standards/vendor/personal registration trees; changing the protocol does not require a new top-level category. |
| 1.1 | Background | Subtypes are the main extension point and application is available for otherwise unmatched formats; media-type claims may be attacker-controlled. |
| 1.2 | Requirements Language | BCP14 uppercase requirement language reviewed. |
| 2 | Rules and Criteria for the Registration of New Top-Level Media Types | Defines criteria for new top-level categories, not a shortcut for registering Email/2 subtypes. |
| 2.1 | Required Criteria | New top-level types require a Standards Track RFC, registry request, clear inclusion criteria, security analysis and at least one subtype. |
| 2.2 | Additional Considerations | Deployment, multiple likely subtypes, common parameters and generic handling inform justification; unregistered top-level use is discouraged. |
| 2.3 | Negative Criteria | Do not use top-level types to mirror arbitrary identifiers, programming type systems or aliases; X-prefixed top-level types cannot be registered. |
| 3 | Top-Level Media Type History | Full history reviewed, including examples, font, haptics, chemical and local scheme-handler conventions. Illustrative names are not registration grants. |
| 4 | IANA Considerations | Registry procedures reviewed separately from current registry state. |
| 4.1 | Registration of Top-level Media Types | Standards Action governs new top-level types; records include defining specification, subtype-registry pointer and comments. |
| 4.2 | Initialization of the Registry of Top-Level Media Types | Initial registry table reviewed; historical initial values do not prove the current registry contents. |
| 5 | Security Considerations | New top-level security effects require explicit analysis. Acknowledgments, both reference lists and author end matter also reviewed; dependency closure remains separate. |

## Email/2 registration decision

The structured event is application data and can use an application subtype. This proposal does not request a new top-level type. Its name, registration tree, structured suffix and registration template are governed by the [RFC6838 review](media-registration.md) and applicable suffix rules; no placeholder spelling is a claim of registration.

Receivers must validate content and authenticated bindings independently of the supplied Content-Type. Selecting a handler is not permission to execute structured effects. Legacy handling of an unknown application subtype also cannot guarantee invisibility.

## Source discrepancy

Section2.3 illustrates a filename parameter with application/octet-string. This audit does not adopt that spelling as the generic binary MIME type; the applicable MIME baseline defines application/octet-stream. No approved erratum for this discrepancy occurs in the captured corpus, and the illustrative example does not change the registration decision.
