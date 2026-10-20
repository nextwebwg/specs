---
title: Emoji vocabulary audit
sectionNav: true
---

# Emoji vocabulary audit

The reaction profile selects the fully-qualified rows in Unicode Emoji 17.0. The checked-in table reproduces all 3,944 unique selected strings exactly. It excludes the nine standalone component rows included in the broader RGI set.

## Scope and sources

The review covers the complete prose, definitions, tables, annexes and reference inventory of [UTS51 revision29](https://www.unicode.org/reports/tr51/tr51-29.html), plus the selected [versioned data](https://www.unicode.org/Public/17.0.0/emoji/emoji-test.txt). Artwork implementations, fonts, assistive technology and the contents of referenced standards are outside this review. The pinned source and license hashes are retained with the experiment.

Exact membership requires no grapheme-segmentation or normalization algorithm. UTF-8/JSON scalar validation remains a separate dependency. Localized readable labels require separately versioned CLDR data and rendering/accessibility checks; English data comments do not establish accessibility.

Keep selectors, modifiers and joiners exactly as selected. A missing font glyph must not change the authenticated value or turn a compound flag into a misleading substitute. A future vocabulary revision needs an explicit profile decision.

The bundled data and derived table retain the Unicode License V3 notice. That data license does not automatically license report prose, illustrations or fonts. See [Unicode terms](https://www.unicode.org/copyright.html).

## Section dispositions

| Sections | Disposition for this reaction profile |
|---|---|
| Front matter, status, contents | Pin revision 29 / version 17.0; Unicode conformance does not imply UTS conformance. |
| 1, 1.1, 1.2, 1.3 | Context: history, emoticons, encoding and interoperability goals. No emoticon conversion or private-use acceptance. |
| 1.4 | Definition inventory governs interpretation of the selected data. |
| 1.4.1 | Emoji and Extended_Pictographic character properties are not a sequence acceptance predicate; component property differs from standalone component rows. |
| 1.4.2 | Presentation style is separate from scalar identity and font availability. |
| 1.4.3 | VS15/VS16 distinctions retained; no arbitrary selector addition. |
| 1.4.4 | Modifier sequences accepted only by exact listed membership. |
| 1.4.5 | Flag, keycap, tag and ZWJ grammar broader than selected vocabulary; no grammar-based expansion. Single grapheme observation is not a validator. |
| 1.4.6 | Direct dependency: ED18 qualification, ED20–27 RGI components/sets, ED28 data-defined qualification. Selected fully-qualified rows exclude nine standalone component rows. |
| 1.4.7 | Notation understood; no regex engine requirement. |
| 1.4.8 | Property stability scoped to version; exact values never casefolded. |
| 1.4.9 | Superset regex needs further validation; not used. |
| 1.5 | C1–C3 capability/conformance boundary reviewed. This validator makes no complete display/edit/input conformance claim. |
| 1.5.1 | Collation and short-name conformity require explicit CLDR version; not protocol identity or current acceptance. |
| 1.5.2 | Pin 17.0; introduction E-ages not acceptance versions. |
| 2, 2.1, 2.2 | Presentation: names and glyph design differ; glyph similarity cannot collapse identifiers. Artwork is a separate licensed asset. |
| 2.3, 2.3.1, 2.3.2 | Presentation/input: preserve explicit gender sequence; no assumed gender substitution. |
| 2.4, 2.4.1, 2.4.2 | Presentation/input: modifiers and fallback variation; optional display tolerance for old defective modifier sequences does not expand wire vocabulary. |
| 2.5 | Presentation: unsupported ZWJ can split; retain exact value and readable fallback. |
| 2.6, 2.6.1, 2.6.2 | Presentation/input: multiperson gender/skin-tone variants may share images but remain different strings. Version 17 additions already in selected data. |
| 2.7, 2.7.1 | Fully-qualified input guidance supports selection. Optional display of minimally/unqualified forms does not mandate accepting them as operations. VS15 breaks ZWJ presentation. |
| 2.7.2 | Tags require special display care; table controls acceptance. |
| 2.8, 2.9, 2.10, 2.11 | Hair/color/direction/order guidance reviewed; no combinatorial generation of unlisted strings. |
| 3 | Counts depend on set; report 3,944 selected strings, not all possible emoji or universal platform support. |
| 4, 4.1 | Presentation can vary; selectors preserved as data. |
| 4.2, 4.3, 4.4 | Locale/script/font controls are optional rendering techniques, not added acceptance dependencies. |
| 5 | UI order may use CLDR; exact identity is not collation. |
| 6 | Palette/dictionary input context; selected values created before signing. No generalized text-to-emoji conversion contract. |
| 7 | Accessibility/search names require localized data; TTS naming outside report scope. No current CLDR conformance claim. |
| 8 | Embedded graphics are separate future feature; remote assets may expose usage. Not reaction vocabulary. |
| A, A.1 | Direct data inventory/format caveat reviewed. emoji-test is selected source; charts not normative implementation data. Other files not reimplemented. |
| B | Region-valid flag grammar broader topic; selected table avoids CLDR-region algorithm dependency. Flags identify regions, not immutable artwork. |
| B.1 | Presentation: unsupported flags may show missing glyphs/letters; avoid assuming identical visual meaning. |
| B.2 | Localized flag order is UI-only and would require CLDR. |
| C | Tag validity and 32-code-point bound reviewed; membership is narrower and already bounded by table, no new universal length rule. |
| C.1 | General subdivision/region validity requires CLDR if implemented; not needed for three selected tag sequences. |
| C.1.1 | England/Scotland/Wales selected; valid non-RGI tags excluded. Unsupported-tag fallback must not misleadingly claim a different flag. |
| C.1.2 | Invalid tags never accepted as reaction; no interpretation as another regular tag image. |
| C.1.3 | Ill-formed tags rejected by absence from vocabulary. |
| Acknowledgments, rights | Reviewed attribution/artwork distinction; no copied artwork licensed through table license. |
| References | All dependency classes inventoried; linked standards not claimed fully audited. Versioned data links preferred. |
| Modifications | Revision 29 changes checked against current version; no reliance on revision 27 or latest/proposed 18. |
| Copyright/footer | Private source retention only; original analysis and links can be public; bundled data license separate. |
