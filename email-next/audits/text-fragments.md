---
title: Plain-text fragment audit
sectionNav: true
---

# Plain-text fragment audit

The complete base text of [RFC5147](https://www.rfc-editor.org/rfc/rfc5147.html), including grammar, examples, references and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. Dependency closure and live registry verification remain separate work.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Updates text/plain with client-side fragment references, not a messaging operation protocol. |
| 1.1 | What Is text/plain? | Character decoding precedes counting; byte offsets are not character offsets. |
| 1.2 | What Is a URI Fragment Identifier? | Fragment interpretation depends on retrieved media type, not URI scheme alone. |
| 1.3 | Why text/plain Fragment Identifiers? | Targeting text can improve inline discussion without adding hidden markup to the source. |
| 1.4 | Incremental Deployment | Unsupported clients can show the whole resource; server retrieval cannot prove fragment support. |
| 1.5 | Notation Used in This Memo | Requirement keywords reviewed. |
| 2 | Fragment Identification Methods | Four position/range methods reviewed; initial encoding BOM is not textual content. |
| 2.1 | Fragment Identification Principles | Position/range and character/line dimensions are independent. |
| 2.1.1 | Positions and Ranges | Zero-based boundary positions; omitted range endpoints use resource boundaries; zero-length ranges are legal. |
| 2.1.2 | Characters and Lines | Count characters with line endings as one; line ranges include their terminators. |
| 2.2 | Combining the Principles | All four combinations reviewed. |
| 2.2.1 | Character Position | A character position is a boundary, not the character itself. |
| 2.2.2 | Character Range | Character ranges span start to end boundaries. |
| 2.2.3 | Line Position | Line positions likewise denote boundaries. |
| 2.2.4 | Line Range | Line ranges include selected complete lines. |
| 2.3 | Fragment Identifier Robustness | Checks apply after content/transfer decoding; charset mismatch prevents direct comparison and transcoding may be lossy. |
| 3 | Fragment Identification Syntax | Exact lowercase scheme names and decimal grammar reviewed; entirely empty comma range is not admitted. |
| 3.1 | Integrity Checks | Code-point length and MD5 checks are optional aids, not authenticated semantic identity; unknown check types are ignored. |
| 4 | Fragment Identifier Processing | Processing rules reviewed separately from grammar. |
| 4.1 | Handling of Line Endings in text/plain MIME Entities | Line endings count as one under the applicable context; decoding and newline treatment must be explicit. |
| 4.2 | Handling of Position Values | Overlarge positions clamp to end; final inequality contradicts Section 2.1.1 and increasing-range examples; record discrepancy rather than silently claiming settled text. |
| 4.3 | Handling of Integrity Checks | Clients may ignore checks entirely; detected changes should prevent fragment interpretation. |
| 4.4 | Syntax Errors in Fragment Identifiers | Invalid fragments are ignored without guessing or correction. |
| 5 | Examples | All four URI examples reviewed; media-type inference can make references unreliable. |
| 6 | IANA Considerations | Adds reference to text/plain registration; live registry verification remains separate. |
| 7 | Security Considerations | Showing only a fragment can omit material context or support spoofing; preserve visible boundaries and full source access. |
| 8 | References | Complete reference lists reviewed. |
| 8.1 | Normative References | URI, IRI, charset, Unicode and ABNF dependencies are separate from this base review. |
| 8.2 | Informative References | Historical media registration and linking references do not specify Email/2 event targets. |
| Appendix A | Acknowledgements | Acknowledgements and remaining end matter read; no additional protocol requirements. |

## Unresolved source discrepancy

Section 4.2 describes improperly ordered positions with a less-than comparison, while Section 2.1.1 requires the end to be at least the start and Section 5 demonstrates increasing ranges. This audit records the contradiction; it does not claim an approved erratum. A compatibility implementation must document its interpretation and test increasing, equal and decreasing bounds.

## Application boundary

The [rendering contract](../rendering.md) treats these fragments as display references. They do not authorize form submission, identify an authenticated field revision or establish authorship. Its clamping, optional checks and media-dependent counting cannot substitute for exact structured-event targets. Reflowed text and recovered character decoding must not silently change a stored reference's meaning.
