---
title: Structured syntax suffix audit
sectionNav: true
---

# Structured syntax suffix audit

The complete captured [RFC6839](https://www.rfc-editor.org/rfc/rfc6839.html) text, including every initial suffix template, references and end matter, has been reviewed. Its one captured erratum, [4367](https://www.rfc-editor.org/errata/eid4367), is rejected; the live erratum page confirms that status. It is not applied as an approved correction.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Suffix registration history and requirement conventions reviewed; generic syntax differs from application meaning. |
| 2 | When to Use These Structured Syntax Suffixes | Generic parsers require no special application knowledge; this grants no action authority. |
| 3 | Initial Structured Syntax Suffix Definitions | All six initial templates reviewed, not just JSON. |
| 3.1 | The +json Structured Syntax Suffix | Use current registry and RFC8259 UTF-8/binary rules; rejected4367 is not an approved correction. Fragment precedence reviewed. |
| 3.2 | The +ber Structured Syntax Suffix | Binary TLV and nesting/length hazards reviewed; BER is not selected for events. |
| 3.3 | The +der Structured Syntax Suffix | DER suffix classification and hazards reviewed; no automatic canonicalization of JSON follows. |
| 3.4 | The +fastinfoset Structured Syntax Suffix | Binary XML template, transfer encodings and fragment hierarchy reviewed; no-security wording is not inherited as an Email Next assurance. |
| 3.5 | The +wbxml Structured Syntax Suffix | Binary XML and generic fragment rules reviewed; not an event encoding choice. |
| 3.6 | The +zip Structured Syntax Suffix | Compression/encryption template reviewed; source IP-files typo differs from current ZIP registry wording. ZIP encryption is not the managed-conversation profile. |
| 4 | IANA Considerations | Initial registration instructions are distinct from current registry state. |
| 4.1 | The +xml Structured Syntax Suffix | Historical XML template reviewed; current entry points to RFC7303, separately applicable only if XML is selected. |
| 5 | Security Considerations | Generic fragment precedence and effects on existing subtypes require compatibility review. |
| 6 | References | Complete reference lists and author end matter reviewed. |
| 6.1 | Normative References | JSON update is relevant; unrelated binary/XML format dependencies are not automatically event requirements. |
| 6.2 | Informative References | Registration procedure, fragment guidance and historical XML draft references recorded. |

## Current JSON entry and application boundary

The [IANA suffix registry](https://www.iana.org/assignments/media-type-structured-suffix), checked on 19 October 2026, references RFC8259 and RFC6839 for +json and specifies UTF-8 with binary encoding considerations. Email Next follows that current entry and its separately audited strict JSON profile, rather than inheriting RFC6839's historical UTF-16/UTF-32 discussion.

The registry's generic fragment rules take precedence when applicable. This event subtype defines no additional fragment syntax. An event identifier or field identifier is a protocol reference, not an implicit JSON Pointer URI fragment. Generic JSON parsing cannot establish event authenticity, supported operations, audience or consent.

RFC7303 updates the XML entry. The registry now references it; this audit does not claim a full RFC7303 review or adopt XML for the event representation. The BER, DER, Fast Infoset, WBXML and ZIP entries were read for complete base-document coverage but are not selected event encodings. The base text's IP-files wording in the ZIP entry is inconsistent with the current registry's ZIP wording; neither supplies the selected MLS security properties.

## Evidence limits

This closes the base suffix-definition review needed to propose +json. It does not register an Email Next type, validate a generic JSON parser against the stricter profile, prove MIME interoperability or close all referenced binary/XML specifications. The [event media-type proposal](../media-type-registration.md) records the concrete candidate and its submission prerequisites.
