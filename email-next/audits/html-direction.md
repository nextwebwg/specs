---
title: HTML language and direction audit
sectionNav: true
---

# HTML language and direction audit

Direction belongs to a boundary in the message tree. Copying a direction attribute onto every descendant changes isolation and automatic direction detection. Language inheritance is separate: a language label does not determine text direction.

## Selected source coverage

This is a scoped review of WHATWG HTML revision `c97dc912b4121294569d6701a21e88880b1e4e1f`, not a complete HTML parser, CSS or Unicode bidi audit. The source file SHA-256 is `d2b3e690add4730aa7f6c3f4575546a1028ba707a425425db9f5ca8995652416`.

| Source lines | Reviewed behavior | Email/2 consequence |
| --- | --- | --- |
| 14760–14875 | Language attributes and language determination | Preserve explicit empty/unknown labels and inheritance; ordinary HTML `xml:lang` is not a substitute |
| 15004–15388 | Direction attributes and automatic, parent and text direction algorithms | Keep direction boundaries and automatic detection; do not infer direction from language |
| 16060–16114 | Bidi controls and rendering obligations | Text order needs actual browser evidence |
| 26035–26108 | `bdi` definition and example | Omitted direction remains automatic, even under an RTL parent |
| 152973–153015 | Selected bidi rendering rules | `pre` automatic direction has paragraph-level behavior; a single computed direction is insufficient |

The [immutable source](https://github.com/whatwg/html/blob/c97dc912b4121294569d6701a21e88880b1e4e1f/source) identifies the reviewed revision. These ranges do not cover the full parser or all referenced algorithms.

## Projection decisions

The [presentation profile](../presentation-profile.md#direction-after-projection) evaluates automatic direction on filtered message content. Client-generated title or interface text must not participate. Filtering may change the source's first eligible strong character, so the result is not a claim to reproduce its original computed direction.

The projection retains explicit document direction as nested inert message containers and replaces a direction-bearing form with one inert block in selected flow contexts. Tails remain outside that boundary. Other removed direction-bearing wrappers produce a diagnostic until their context-safe replacement is specified. A universal block or inline replacement could corrupt tables or change browser reparsing.

## Evidence and remaining coverage

Tree tests establish boundary structure, unchanged omitted `bdi` direction and exclusion of head text. They do not establish visual bidi order, `pre` paragraph behavior, independent direction of alt/title text, malformed-table reparsing or assistive-technology output. The source review and tree tests therefore support only this projection decision; browser and accessibility checks remain separate.

## Direction is more than character order

The native renderer combines HTML direction with the Unicode bidirectional algorithm. The selected Unicode17 source separates paragraph-level resolution from per-line display reordering, keeps combining marks attached to their logical base and mirrors eligible glyphs without changing stored characters. CSS maps containing-block direction and isolation into that algorithm; source bidi controls remain relevant. A correct `dir` value alone is not evidence that all these steps are implemented correctly. [UAX9 revision51](https://www.unicode.org/reports/tr9/tr9-51.html), [CSS directional integration](https://www.w3.org/TR/2019/CR-css-writing-modes-4-20190730/#bidi-algo).

Plain conversion can lose markup-supplied direction. Clients must not claim that stripping tags preserves every visual ordering, nor rewrite authenticated source bytes to achieve it. The draft's readable plain alternative is separately authored and retained. Clipboard behavior and mixed-script glyph placement need their own tests.

## Selected Unicode algorithm and data

Mixed Hebrew or Arabic text, Latin names, numbers and parentheses can require several directional runs inside one line. The reviewed baseline is Unicode17, UAX9 revision51. It covers definitions and paragraph resolution, explicit embeddings and isolates, weak and neutral types, paired brackets, implicit levels and final line reordering (BD/P/X/W/N/I/L). This is source coverage, not a claim that the native renderer passes the Unicode conformance corpus.

| Stage | Consequence for a message renderer |
| --- | --- |
| Paragraphs and isolates | Automatic paragraph detection skips isolate contents; CSS paragraph direction and the first-strong heuristic inside an isolate are distinct inputs. Unmatched and excessive controls follow the algorithm's overflow rules. |
| Directional runs | Explicit controls removed during X9 are removed from the algorithm's working sequence, not the authenticated message. Isolate boundaries still affect run construction; joiners retain their shaping role. |
| Numbers, neutrals and brackets | Resolve weak types, paired brackets and surrounding strong context before assigning implicit levels. Bracket matching is not ordinary punctuation matching. The specified bracket equivalences do not authorize source normalization. |
| Lines and glyphs | Resolve levels before per-line reordering. Line breaking and shaping need their own rules; mirrored display does not replace stored code points. |

The explicit-depth limit 125 and bracket-stack limit 63 come from UAX9. They are algorithm rules, not Email/2 message-size quotas. [Basic algorithm](https://www.unicode.org/reports/tr9/tr9-51.html#Basic_Display_Algorithm).

The selected data dependencies are Unicode17 `Bidi_Class`, `Bidi_Paired_Bracket`, `Bidi_Paired_Bracket_Type` and `Bidi_Mirrored`. The extracted class file includes range-specific defaults: unlisted characters cannot all be treated as left-to-right. Later `@missing` ranges override earlier defaults. `BidiBrackets.txt` supplies the normative bracket properties; `BidiMirroring.txt` is an informative character mapping for only part of mirrored display. A missing mapping does not remove a character's mirroring requirement. [UCD defaults](https://www.unicode.org/reports/tr44/tr44-36.html#Missing_Conventions), [class data](https://www.unicode.org/Public/17.0.0/ucd/extracted/DerivedBidiClass.txt), [bracket data](https://www.unicode.org/Public/17.0.0/ucd/BidiBrackets.txt), [mirroring data](https://www.unicode.org/Public/17.0.0/ucd/BidiMirroring.txt).

A data consistency check covered all 128 bracket records and 428 character-mirroring mappings against the selected Unicode17 character properties. It did not execute bidi layout. Native engine Unicode-version alignment, the Unicode bidi conformance corpus, line-breaking and shaping dependencies, visual fragment geometry and accessibility remain separate evidence gaps. No concrete native behavior mismatch was established by this source review.
