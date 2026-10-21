---
title: JSON encoding audit
sectionNav: true
---

# JSON encoding audit

The complete [RFC8259](https://www.rfc-editor.org/rfc/rfc8259.html) base text, examples, references and end matter were reviewed, together with all 16 entries in the captured errata corpus. Erratum 5318 was also checked against its official live record. Other statuses below describe the captured corpus; dependency closure remains open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | JSON data model reviewed; scalar-only strings are a stricter Email/2 choice. |
| 1.1 | Conventions Used in This Document | BCP14 and ABNF conventions reviewed. |
| 1.2 | Specifications of JSON | ECMA404 alignment is a normative dependency, not a second application schema. |
| 1.3 | Introduction to This Revision | Revision incorporates earlier errata and interoperability experience. |
| 2 | JSON Grammar | Complete token and whitespace grammar reviewed; Email/2 requires an object root. |
| 3 | Values | All value forms reviewed; numbers and null are excluded by the initial application profile. |
| 4 | Objects | Duplicate names yield inconsistent parser behavior; Email/2 rejects decoded duplicates before information loss. |
| 5 | Arrays | Arrays are ordered in JSON; application set semantics require explicit uniqueness and order rules. |
| 6 | Numbers | Grammar and precision discussion reviewed; rejecting numbers is an application choice rather than generic JSON validity. |
| 7 | Strings | String escapes and grammar reviewed; solidus correction conflicts with published acceptance and receives explicit profile treatment. |
| 8 | String and Character Issues | Character concerns reviewed separately from wire octets. |
| 8.1 | Character Encoding | Network JSON uses UTF-8; Email/2 additionally rejects BOM rather than ignoring it. |
| 8.2 | Unicode Characters | Generic grammar permits lone surrogate escapes; Email/2 excludes them. |
| 8.3 | String Comparison | Compare decoded strings; escape spelling does not change a member name. |
| 9 | Parsers | General parsers may accept extensions and impose limits; the application decoder rejects extensions. |
| 10 | Generators | Generators emit conforming JSON; profile output is further restricted. |
| 11 | IANA Considerations | application/json has no defined charset parameter; final Email/2 media binding remains separate. |
| 12 | Security Considerations | Never evaluate JSON as code; historical JavaScript subset wording is not a safe parser contract. |
| 13 | Examples | All object, array and scalar examples reviewed; several are valid JSON but intentionally outside Email/2 event grammar. |
| 14 | References | Complete references reviewed without claiming dependency closure. |
| 14.1 | Normative References | Unicode, UTF-8, ABNF and ECMA404 dependencies remain separately scoped. |
| 14.2 | Informative References | Historical standards and errata contextualize the revision. |
| Appendix A | Changes from RFC7159 | All changes, contributors and author end matter reviewed. |

## Errata dispositions

| Erratum | Captured status | Disposition |
| --- | --- | --- |
| [5218](https://www.rfc-editor.org/errata/eid5218) | Rejected | Historical JavaScript subset wording; no eval use permitted. |
| [5853](https://www.rfc-editor.org/errata/eid5853) | Rejected | Rejected charset-note rewrite not adopted. |
| [7600](https://www.rfc-editor.org/errata/eid7600) | Verified | Leading-zero restriction applies to the integer component. |
| [7603](https://www.rfc-editor.org/errata/eid7603) | Verified | Code-point terminology does not require accepting lone surrogates in an application profile. |
| [7617](https://www.rfc-editor.org/errata/eid7617) | Rejected | Rejected numeric interpretation rewrite not adopted. |
| [6208](https://www.rfc-editor.org/errata/eid6208) | Rejected | Rejected alternate-encoding BOM interpretation not adopted. |
| [7307](https://www.rfc-editor.org/errata/eid7307) | Rejected | Rejected null/string conflation not adopted. |
| [7383](https://www.rfc-editor.org/errata/eid7383) | Verified | Hexadecimal spelling; no change to literal values. |
| [8874](https://www.rfc-editor.org/errata/eid8874) | Rejected | Rejected replacement numeric design not adopted. |
| [7650](https://www.rfc-editor.org/errata/eid7650) | Held for Document Update | ABNF rule-name collision; held change not silently treated as new wire syntax. |
| [8438](https://www.rfc-editor.org/errata/eid8438) | Held for Document Update | Updated ECMA404 URL. |
| [7673](https://www.rfc-editor.org/errata/eid7673) | Rejected | Rejected expansion of required escaping not adopted. |
| [5210](https://www.rfc-editor.org/errata/eid5210) | Verified | STD90 boilerplate correction. |
| [8622](https://www.rfc-editor.org/errata/eid8622) | Rejected | Rejected duplicate-name complaint does not remove interoperability guidance. |
| [5318](https://www.rfc-editor.org/errata/eid5318) | Verified | Excludes literal solidus; live status verified and explicit receiver compatibility departure documented. |
| [9095](https://www.rfc-editor.org/errata/eid9095) | Reported | Reported charset-note deletion is not an approved change. |

## Application decisions

The [event encoding](../event-encoding.md) requires unique decoded member names, scalar-value strings, an object root and a restricted value vocabulary. It retains exact bytes instead of introducing canonical JSON. These are explicit Email/2 choices. The receiver accepts literal and escaped solidus; generators escape it to remain within both published and corrected grammars. This deliberate receiver departure from erratum 5318 is not a claim that the two grammars agree.

Six [encoding tests](../evidence/README.md#experimental-event-decoding) exercise the stated cases. They do not establish a production parser, resource bounds, complete event schemas or cryptographic interoperability.
