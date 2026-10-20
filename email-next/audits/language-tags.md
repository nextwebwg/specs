---
title: Language tags audit
sectionNav: true
---

# Language tags audit

A language label helps a client pronounce text, choose fonts and distinguish a quoted passage from the surrounding message. [RFC5646](https://www.rfc-editor.org/rfc/rfc5646.html) defines those labels. It does not define HTML language inheritance, rendering behavior or the treatment of an empty `lang` attribute.

## Three different checks

| Check | What it establishes | Data needed |
| --- | --- | --- |
| Well-formed | The tag matches the complete grammar, including grandfathered tags. | RFC5646 grammar. |
| Valid | The tag satisfies registry-based and structural rules, including the prohibition on repeated variants or extension singletons. | An identified Language Subtag Registry snapshot; allocated extensions and applicable surrounding rules. |
| Canonical | Preferred mappings and extension ordering have been applied. This is a representation choice, not merely a pass/fail syntax check. | Registry data and, where applicable, the extension’s canonicalization rules. |

For example, `de-DE-1901-1901` matches the grammar but repeats a variant, so it is not valid. `en-BU` remains valid even though its region subtag is deprecated; its preferred replacement produces `en-MM`. Changing letter case alone does not perform canonicalization, and uppercase letters do not make a tag invalid. Comparisons use ASCII case-insensitive rules, independent of the user's locale.

The validity checklist in section 2.2.9 is not the whole contract. Section 2.2.2 forbids a second or third extended-language subtag even though the grammar accepts them. Section 2.2.6 also requires allocated extension singletons. Checking the values *inside* an extension is a further, separately versioned validation step. A generic locale API should not be assumed to implement exactly the selected RFC5646 contract.

## Decision left to the rendering profile

The [presentation profile](../presentation-profile.md#language-labels) selects registry-valid generated labels and preserves received labels without canonicalizing authenticated content. Its local snapshot/update policy supplies the processing choice; this audit explains the inherited distinctions.

Registry-based acceptance tests need identified data. A stable tag remains valid as the registry grows, but an older snapshot can reject a newly registered subtag, and preferred mappings can change. The selected policy therefore identifies each snapshot by File-Date and content digest, separates authenticated updates from mail processing, and preserves original labels. Extension-specific semantic checks would need their own specification/data versions; they are not selected merely by base RFC5646 validity.

Validation should work with local data. RFC5646 advises against depending on the registries being reachable and against frequent full downloads. A message's language label is not a request to contact a registry or extension service. Registry descriptions also cannot supply a complete localized language picker or reliable fallback-language map.

The HTML contract remains a separate dependency for empty values, inheritance, invalid-value handling and their accessibility consequences. Language matching requires RFC4647, the other part of BCP47. Neither has been reviewed merely by reading RFC5646's references.

## Section review

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | RFC5646 and RFC4647 together form BCP47. This review covers tag formation; matching requires the companion standard. |
| 2 | The Language Tag | Tags identify human languages, including signed and constructed languages; they do not identify programming languages. |
| 2.1 | Syntax | Use the complete ASCII grammar, including the fixed grandfathered list. No whitespace or underscores; subtags are at most eight characters, but whole tags have no fixed maximum. |
| 2.1.1 | Formatting of Language Tags | All tags, including private use and extensions, compare case-insensitively. Use locale-neutral ASCII casing; presentation casing carries no meaning. |
| 2.2 | Language Subtag Sources and Interpretation | The IANA registry, not a current ISO code list alone, defines registered subtags. Position determines type; extension and private-use sequences remain at the end. |
| 2.2.1 | Primary Language Subtag | Preserve primary-language rules, private-use ranges and historical stable assignments; do not substitute every ISO code as a valid language subtag. |
| 2.2.2 | Extended Language Subtags | Extlangs use their registered prefix; only one is permitted even though ABNF parses up to three. Prefer the corresponding primary-language form when generating tags. |
| 2.2.3 | Script Subtag | One script subtag occupies the defined position. Suppress-Script is generation guidance, not a declaration that an explicit script makes a tag invalid. |
| 2.2.4 | Region Subtag | One region subtag occupies the defined position. Only the selected registered ISO/UN values and private-use ranges apply, not every country or numeric area code. |
| 2.2.5 | Variant Subtags | Repeated variants are forbidden. Variant prefixes and ordering provide usage guidance; do not convert every SHOULD into a validity rejection. |
| 2.2.6 | Extension Subtags | Extension singletons must be allocated, unique and followed by content. Internal extension validity requires that extension’s specification and data; base validation need not perform it. |
| 2.2.7 | Private Use Subtags | Private use can occupy the entire tag or its final sequence; meaning requires private agreement and is not inferred from familiar-looking subtags. |
| 2.2.8 | Grandfathered and Redundant Registrations | Grandfathered tags remain valid, including irregular forms. Redundant registrations and preferred replacements do not make historical tags invalid. |
| 2.2.9 | Classes of Conformance | Separate ABNF well-formedness, registry-date validity and extension-specific validity. Apply surrounding section rules as well as the short checklist; erratum 5457 flags its extlang omission. |
| 3 | Registry Format and Maintenance | Treat registry content as versioned data with its specified record format, not as executable instructions or a flat list of complete tags. |
| 3.1 | Format of the IANA Language Subtag Registry | Treat registry content as versioned data with its specified record format, not as executable instructions or a flat list of complete tags. |
| 3.1.1 | File Format | Parse UTF-8 record-jar fields, folding and inclusive ranges; preserve NFC and field boundaries. The registry’s Unicode descriptions do not expand the ASCII tag alphabet. |
| 3.1.2 | Record and Field Definitions | Record File-Date and distinguish Tag from Subtag records. Respect repeated-field allowances; ignore unknown future fields as recommended. |
| 3.1.3 | Type Field | Keep type-specific namespaces separate when looking up a subtag. |
| 3.1.4 | Subtag and Tag Fields | Registry casing is standardized presentation; comparisons remain case-insensitive. |
| 3.1.5 | Description Field | Descriptions identify records but are not localized UI names. Held erratum 8711 concerns Latin-script descriptions, not the tag alphabet. |
| 3.1.6 | Deprecated Field | Deprecated tags remain valid; generation is discouraged. Deprecation without Preferred-Value supplies no replacement. |
| 3.1.7 | Preferred-Value Field | Preferred-Value supports canonicalization and can change through registry maintenance. Replacement does not require retagging existing content. |
| 3.1.8 | Prefix Field | Distinguish extlang prefix requirements from variant-prefix guidance. Prefix relationships can constrain useful ordering without making arbitrary combinations meaningful. |
| 3.1.9 | Suppress-Script Field | Suppress-Script guides omission of redundant scripts. Its absence does not prove a language has only one script or a known default script. |
| 3.1.10 | Macrolanguage Field | Macrolanguage relationships are informational; they do not guarantee mutual intelligibility or an appropriate fallback. |
| 3.1.11 | Scope Field | Scope distinguishes collections, macrolanguages, special and private-use values. Missing Scope means an individual language. |
| 3.1.12 | Comments Field | Comments are mutable explanatory material, not a stable validation rule. |
| 3.2 | Language Subtag Reviewer | Reviewer authority, maintenance and appeals govern registry changes; a rendering implementation consumes the resulting registry instead of bypassing it. |
| 3.3 | Maintenance of the Registry | Reviewer authority, maintenance and appeals govern registry changes; a rendering implementation consumes the resulting registry instead of bypassing it. |
| 3.4 | Stability of IANA Registry Entries | Stable identifiers and retained deprecated entries protect old content. Preferred mappings and other fields can change, so canonicalization needs identified data. |
| 3.5 | Registration Procedure for Subtags | Use the registration process for new public assignments; this proposal registers none. Historical contact details are not a current integration endpoint. |
| 3.6 | Possibilities for Registration | Use the registration process for new public assignments; this proposal registers none. Historical contact details are not a current integration endpoint. |
| 3.7 | Extensions and the Extensions Registry | Extension assignment, versioning and canonicalization are separate contracts. Identify extension data revisions if extension-specific validation is chosen. |
| 3.8 | Update of the Language Subtag Registry | RFC5645 describes the initial registry update; it does not substitute for an identified subsequent registry snapshot. |
| 3.9 | Applicability of the Subtag Registry | The registry is not a language picker, localized-name database, fallback map or complete model of language relationships. |
| 4 | Formation and Processing of Language Tags | Tag content with justified specificity. Any selection rules departing from this guidance need an explicit profile explanation; no such policy is selected by this audit. |
| 4.1 | Choice of Language Tag | Tag content with justified specificity. Any selection rules departing from this guidance need an explicit profile explanation; no such policy is selected by this audit. |
| 4.1.1 | Tagging Encompassed Languages | Prefer the known encompassed language, but do not infer intelligibility from a shared macrolanguage. |
| 4.1.2 | Using Extended Language Subtags | Extlang forms support compatibility. A macrolanguage tag remains valid; region alone does not uniquely identify an encompassed language. |
| 4.2 | Meaning of the Language Tag | A valid tag need not describe a plausible language/script/region combination. HTML span language differs from document audience metadata; tags do not guarantee character repertoire. |
| 4.3 | Lists of Languages | Language lists have application-specific scope. Do not treat a list of tags as one HTML lang value. |
| 4.4 | Length Considerations | There is no universal maximum whole-tag length; any profile limit is an additional documented choice. |
| 4.4.1 | Working with Limited Buffer Sizes | A fixed buffer limit must accommodate at least 35 characters; 35 is a minimum capacity, not a maximum valid length. Document overflow behavior. |
| 4.4.2 | Truncation of Language Tags | Truncation changes meaning. If permitted, remove complete rightmost subtags and stranded singletons rather than slicing characters. |
| 4.5 | Canonicalization of Language Tags | Canonicalization orders extension sequences and applies preferred mappings, including removing extlang form. Case normalization and variant reordering are separate optional steps; deprecated values without replacements can remain canonical. |
| 4.6 | Considerations for Private Use Subtags | Private-use ranges retain structural information but no public agreed meaning. Do not derive identity, geography or authorization from private values. |
| 5 | IANA Considerations | File-Date identifies registry publication; keep data available locally rather than requiring a network lookup for each message. |
| 5.1 | Language Subtag Registry | File-Date identifies registry publication; keep data available locally rather than requiring a network lookup for each message. |
| 5.2 | Extensions Registry | The extension registry identifies maintaining authorities and specifications; it does not contain each extension’s full value vocabulary. |
| 6 | Security Considerations | Language metadata can disclose sensitive inferences. Guard resource use; tags do not prevent homographs. Rendering must not require registry availability or fetch arbitrary extension URLs. |
| 7 | Character Set Considerations | Language tags are ASCII metadata; font selection and rendering behavior are outside this RFC and need the HTML/rendering contract. |
| 8 | Changes from RFC 4646 | Use operative grammar and rules rather than change-summary wording. The summary says grandfathered production was removed although the published grammar retains it. |
| 9 | References | References identify dependencies; their listing is not a full review of RFC4647, ISO standards, Unicode or extension specifications. |
| 9.1 | Normative References | References identify dependencies; their listing is not a full review of RFC4647, ISO standards, Unicode or extension specifications. |
| 9.2 | Informative References | References identify dependencies; their listing is not a full review of RFC4647, ISO standards, Unicode or extension specifications. |
| A | Examples of Language Tags (Informative) | Read all examples as illustrative. Hypothetical extension examples are not proof of current extension-specific validity; retain invalid-tag cases for tests. |
| B | Examples of Registration Forms | Registration-form examples illustrate procedure, not current language-tag validation or authority to submit a registration. |
| C | Acknowledgements | Acknowledgements and following author addresses add no protocol requirements. |

## Errata and review boundary

The complete 4,707-line RFC text, grammar, examples, references, registration procedures and appendices were read. Fresh [official metadata](https://www.rfc-editor.org/info/rfc5646) identifies it as Best Current Practice, published September 2009, obsoleting RFC4646, with no updating or obsoleting RFC listed. This is a document review, not an implemented validator or a rendering-conformance result.

All three records in the captured errata corpus were read. Fresh retrieval of the RFC's errata page failed, so this review does not claim live exhaustive errata closure.

| Record | Status | Effect |
| --- | --- | --- |
| [5457](https://www.rfc-editor.org/errata/eid5457) | Reported | Calls out the missing maximum-one-extlang condition in the validity checklist. The prohibition already appears in section 2.2.2; do not treat the reported replacement as an adopted change. |
| [8711](https://www.rfc-editor.org/errata/eid8711) | Held for Document Update | Proposes clarifying Latin script in registry descriptions using Unicode script properties. It does not expand the language-tag alphabet beyond ASCII. |
| [8712](https://www.rfc-editor.org/errata/eid8712) | Held for Document Update | Proposes the corresponding clarification for registration requests; no new tag-validation rule is adopted here. |

The review captured the [Language Subtag Registry](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry) with File-Date `2026-09-17` and the [extension registry](https://www.iana.org/assignments/language-tag-extensions-registry/language-tag-extensions-registry) with File-Date `2014-04-02`. The latter lists `t` (RFC6497) and `u` (RFC6067). These are evidence snapshots, not protocol pins. The full extension registry was read; individual language records and the extension specifications/data were not exhaustively audited.

Two additional source cautions matter when implementing tests. Section 8's historical summary claims that the grandfathered production was removed, but the operative grammar retains it. Section 4.1.1's Macedonian example uses `ma`, while the registered language subtag is `mk`; examples should not replace registry checks.

Acceptance fixtures should distinguish grammar failure, duplicate subtags, multiple extlangs, unregistered values, deprecated-but-valid values, private-use sequences, grandfathered tags, unknown extension contents and canonicalization changes. Also test ASCII casing under a Turkish locale, long tags without silent truncation, offline operation, and HTML's separately defined empty/inherited-language behavior. These tests remain to be implemented after the profile chooses its contract.
