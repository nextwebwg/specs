---
title: Flowed plain text audit
sectionNav: true
---

# Flowed plain text audit

**Coverage:** full20-page RFC3676, including grammar, examples, appendix and end matter. Zero matching errata in the refreshed dataset checked19October2026. [RFC3676](https://www.rfc-editor.org/rfc/rfc3676.html). Dependencies and current text/plain registration remain open.

| Section | Disposition |
| --- | --- |
| 1 | Backward-compatible plain-text paragraph and quotation semantics; no structured-answer authority. |
| 2 | Paragraph means logical display unit; requirement language retained. |
| 3 | Fixed-line baseline and line-length context reviewed. |
| 3.1 | Paragraph versus fixed-line rendering distinguished; no guessing from visual width. |
| 3.2 | Malformed wrapping can confuse attribution; reconstruction must retain uncertainty. |
| 3.3 | Historical enriched/HTML compatibility motivates parameter extension; not a modern HTML-profile definition. |
| 4 | Format and DelSp case-insensitive. Missing/unknown Format means fixed; missing/unknown DelSp means no. Ignore DelSp outside flowed plain text. Transfer decoding precedes interpretation. |
| 4.1 | Count initial quote marks before removing one stuffing space; trailing SP marks flow except signature separator. DelSp=yes removes exactly one trailing SP. Preserve other spaces. End paragraph on depth change, signature boundary or body end, including malformed input. |
| 4.2 | Generation uses soft SP CRLF, correct DelSp for wrapping method, mandatory stuffing, equal quote depth per paragraph and no accidental signature separator. 78-character recommendation includes stuffing; long unbroken words exception does not waive SMTP hard limits. QP discouraged except necessity or cryptographic protection. |
| 4.3 | DASH DASH SP separator is neither fixed nor flowed. Recognize before quotation processing and after quoted stuffing removal; never absorb into paragraph. Separator is not authority to discard subsequent answers. |
| 4.4 | Remove one stuffing SP after quote detection; stuffed literal > is not quotation. Protect From-space and leading-space lines. |
| 4.5 | Initial consecutive > count sets depth; > > has depth1, not2. Depth wins over malformed flow across quote boundaries. Rewrap dequoted content and restore exact depth. |
| 4.6 | Cryptographic processing uses profile-defined wire representation, not reflowed display. Cleartext-signature trailing-whitespace treatment can permit display changes; evaluate current OpenPGP/MIME successors separately. |
| 4.7 | Examples and displayed soft/hard marker notation reviewed; examples are not literal wire stars/hashes. |
| 5 | Legacy viewers retain readable line breaks and stuffing; old flowed readers may retain inserted spaces. Aligned art/code should remain fixed. |
| 6 | ABNF and precedence reviewed, including sig-sep ambiguity resolved by prose and independent fixed lines. Charset encodes SP and quote markers; byte-level ASCII guesses are insufficient before character decoding. |
| 7 | Failure modes retained as diagnostics, not automatic repair authority. |
| 7.1 | Stripping spaces loses flow; adding spaces can change grouping. Do not infer lost spaces or apply speculative odd-length heuristic. |
| 8 | Plain-text security applies; display transformations must remain separate from authentication. |
| 9 | text/plain registration reference specified; live media registration and related dependencies remain open. |
| 10 | DelSp supports scripts without common ASCII spaces; bidi wrapping requires care, no locale-independent visual attribution assumptions. |
| 11 | Acknowledgements and historical prior implementation reviewed. |
| 12 | MIME2045/2046 base audits complete; ABNF2234 successor5234 and requirement-language dependencies remain open. |
| 13 | Current Unicode line breaking, message format5322, SMTP5321, OpenPGP9580 and MIME3156 require appropriate current mapping; base5321/5322 reviewed. |
| Appendix A | All substantive/editorial changes from2646 reviewed: DelSp, 78-character guidance, stuffing/quote constraints, EOF paragraph ending, signature handling and crypto cautions. |

| Front/end matter | Status, abstract, copyright, intellectual-property statement and author contact reviewed. |

## Reconstruction consequence

A line ending in a space is not enough to join it to the next line. Flowed interpretation requires the MIME parameter, quote-depth agreement and the signature exception. Space unstuffing must occur after quote detection: a literal greater-than sign protected by an initial space must not become a newly discovered quotation.

Authenticate the appropriate original representation before presenting a derived paragraph view. Preserve source ranges through reflow. The existing fixed-line quote experiment does not implement these rules and must not be applied directly to flowed input.

Required fixtures: absent/unknown parameters, DelSp yes/no, multiple trailing spaces, space-stuffed literal quote, nested depths, malformed depth transition, signature boundary, EOF after a flowed line, empty lines, non-ASCII scripts, bidi content and transfer encoding before interpretation.

## Executable evidence

The [flowed-text experiment](../evidence/README.md#flowed-text-interpretation-experiment) tests12 decoding and boundary cases. It does not constitute complete RFC conformance, wire-generation validation or cryptographic processing.
