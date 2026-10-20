---
title: Grammar notation audit
sectionNav: true
---

# Grammar notation audit

[RFC5234](https://www.rfc-editor.org/rfc/rfc5234.html) defines the ABNF notation used by the inherited email grammars. [RFC7405](https://www.rfc-editor.org/rfc/rfc7405.html) adds explicit case-sensitive literals. Neither introduces an email feature.

## Application boundary

Rule names are case insensitive. Bare quoted literals also ignore ASCII letter case; use `%s` for exact case. Numeric terminals remain exact. Concatenation adds no implicit whitespace. Encoding, size limits and authorization need their own application rules.

The core `HEXDIG` accepts both letter cases. An application requiring lowercase identifiers must constrain them explicitly. The core `LWSP` is unsuitable for defining new mail headers; use the applicable message-format folding rules.

## Review coverage

Both complete texts, examples, references and end matter were reviewed. RFC5234 sections 1–4 define notation; section 5 supplies no application security assurance; section 6 and appendices A–B cover references, provenance and core rules. RFC7405 sections 1–2 define the update; sections 3–4 cover security and its dependency on RFC5234. ASCII remains an external reference.

## Errata

The [RFC5234 errata](https://www.rfc-editor.org/errata/rfc5234) contain two verified whitespace corrections (2968, 3076), four held editorial reports (2820, 2914, 6172, 6173), and six rejected changes (1423, 3096, 4040, 4564, 5110, 4361). All were reviewed. The verified corrections concern the metagrammar; their verifier notes retain testing caveats.

[RFC7405 erratum 5334](https://www.rfc-editor.org/errata/eid5334) is rejected: single-quoted literals would change the language. No such syntax is adopted. Reviewing notation does not establish that every application grammar or parser conforms.

::: {.details summary="Section-by-section dispositions"}

| Source / section | Disposition |
| --- | --- |
| RFC5234 / 1 | Notation dependency; not an email extension. |
| RFC5234 / 2 | Rule definitions. |
| RFC5234 / 2.1 | Rule names case insensitive. |
| RFC5234 / 2.2 | Explicit definitions and indented continuation. |
| RFC5234 / 2.3 | Numeric terminals and ASCII literals; apply7405 update. |
| RFC5234 / 2.4 | Wire encoding specified separately. |
| RFC5234 / 3 | Operators. |
| RFC5234 / 3.1 | Concatenation adds no implicit whitespace. |
| RFC5234 / 3.2 | Alternatives are not ordered parser choices. |
| RFC5234 / 3.3 | Incremental alternatives extend a named rule. |
| RFC5234 / 3.4 | Ranges and dotted sequences are distinct. |
| RFC5234 / 3.5 | Group multi-element alternatives. |
| RFC5234 / 3.6 | Repetition bounds explicit; omitted upper bound unbounded. |
| RFC5234 / 3.7 | Exact counts. |
| RFC5234 / 3.8 | Optional sequence stays together. |
| RFC5234 / 3.9 | Comments end at line end. |
| RFC5234 / 3.10 | Precedence reviewed. |
| RFC5234 / 4 | Complete metagrammar; verified2968/3076 narrow trailing/blank-line whitespace. |
| RFC5234 / 5 | Notation is not a security validator. |
| RFC5234 / 6 | References. |
| RFC5234 / 6.1 | ASCII external normative dependency. |
| RFC5234 / 6.2 | Historical mail references not additional syntax selection. |
| RFC5234 / A | Acknowledgements. |
| RFC5234 / B | Core rules. |
| RFC5234 / B.1 | HEXDIG accepts both cases; avoid LWSP for mail header definitions. |
| RFC5234 / B.2 | Common ASCII encoding does not override application encoding. |
| RFC5234 / front/end | Status,copyright,contacts reviewed. |
| RFC7405 / 1 | ASCII case distinction rationale. |
| RFC7405 / 2 | Replaces5234 terminal-string prose and char-val. |
| RFC7405 / 2.1 | Percent-s exact case,percent-i and bare literals insensitive. |
| RFC7405 / 2.2 | Complete grammar including empty quoted string; no single-quote alternative. |
| RFC7405 / 3 | No security assurance from notation. |
| RFC7405 / 4 | 5234 reviewed dependency. |
| RFC7405 / front/end | Status,copyright,author reviewed. |

:::

::: {.details summary="Individual errata dispositions"}

| Erratum | Disposition |
| --- | --- |
| [2968](https://www.rfc-editor.org/errata/eid2968) | Verified: elements trailing WSP correction; verifier notes solution untested. |
| [3076](https://www.rfc-editor.org/errata/eid3076) | Verified: rulelist blank-line WSP correction; verifier notes solution untested. |
| [2820](https://www.rfc-editor.org/errata/eid2820) | Held: prose-val excludes greater-than, not both angles. |
| [2914](https://www.rfc-editor.org/errata/eid2914) | Held: grammar recursion explanatory omission. |
| [6172](https://www.rfc-editor.org/errata/eid6172) | Held: character sets typo. |
| [6173](https://www.rfc-editor.org/errata/eid6173) | Held: absent upper repetition bound wording. |
| [1423](https://www.rfc-editor.org/errata/eid1423) | Rejected: repeat rewrite creates empty match; not adopted. |
| [3096](https://www.rfc-editor.org/errata/eid3096) | Rejected: LWSP minimum change not adopted. |
| [4040](https://www.rfc-editor.org/errata/eid4040) | Rejected: HEXDIG already case insensitive. |
| [4564](https://www.rfc-editor.org/errata/eid4564) | Rejected: optional sequence is not alternation. |
| [5110](https://www.rfc-editor.org/errata/eid5110) | Rejected: BIT represents digit characters. |
| [4361](https://www.rfc-editor.org/errata/eid4361) | Rejected: bracketed name prose does not replace formal grammar. |
| [5334](https://www.rfc-editor.org/errata/eid5334) | Rejected: single-quote syntax is a proposed new language change, not correction. |

:::
