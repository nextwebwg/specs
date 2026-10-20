---
title: UTF-8 and exact text bytes
sectionNav: true
---

# UTF-8 and exact text bytes

Email Next's event and identity records use strict UTF-8. [RFC3629](https://www.rfc-editor.org/rfc/rfc3629.html) restricts encoding to one through four octets and excludes surrogate code points. Invalid encoding is a failed record, not text to repair before authentication.

## Applying the encoding rules

Reject overlong sequences, isolated continuation bytes, truncated sequences, invalid continuations, encoded surrogates and values above U+10FFFF. The second-byte restrictions after E0, ED, F0 and F4 matter: checking only the leading-byte shape is insufficient. CESU-8 and historical five- or six-byte forms are not UTF-8.

Valid UTF-8 is only the first layer. The JSON grammar and event schema still apply. JSON surrogate escape pairs can represent a supplementary scalar; lone escaped surrogates are rejected by the event profile. A literal U+FFFD is valid text; introducing it to recover malformed authenticated input is not permitted. Unassigned code points and noncharacters are not malformed UTF-8 merely because they lack ordinary glyphs.

The event profile rejects a leading BOM and retains the original octets for signatures, digests and retries. It does not strip internal U+FEFF, normalize combining sequences, fold case or reserialize before verification. Different JSON spellings can decode to equal strings while remaining different authenticated byte sequences. Ordinary legacy-message display recovery is a separate operation and cannot authorize a contribution.

## Unicode source and data versions

The selected scalar and encoding definitions were checked against [Unicode17.0.0 Chapter3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/), particularly D76, D79, D91–D95 and Tables3-6/3-7. Scalars are U+0000–U+D7FF and U+E000–U+10FFFF. These ranges and UTF-8 byte validity require no assigned-character database lookup. A receiver must not reject otherwise valid event text merely because its Unicode database predates a character assignment.

This source pin does not update the separately selected emoji repertoire, normalization, IDNA, segmentation or display-property data. Those features need their own versioned contracts. Exact string comparison is not a claim that visually or canonically similar text has different meaning to a reader.

## Review evidence and limits

All 787 lines of RFC3629 were read, including examples, references and end matter. Retrieved metadata lists Internet Standard status, replacement of RFC2279, and no later update or replacement. The live errata search returned no entries on 20 October 2026, matching the captured corpus.

The Unicode review is section-scoped, not a complete Unicode audit: version guidance, C1–C10, selected character definitions, surrogate/scalar definitions, encoding-form tables and UTF-8 serialization. Unicode17's release is independently confirmed by its [release announcement](https://blog.unicode.org/2025/09/unicode-170-release-announcement.html). Version landing pages retain inconsistent preliminary-status text; no automatic latest-version or property migration follows. The reviewed errata/corrigenda listings identify no change to these selected17 encoding rules. Exact source hashes and reading ranges are retained in the private ledger.

Inspection of `event_encoding.py` found strict decoding, scalar checking and original-byte retention, without a Unicode property lookup. This audit did not execute a malformed-input test corpus or certify every language runtime. Full IDNA, display safety and character-property processing remain separate dependencies.

Source SHA 256 values:

- rfc3629.txt: `a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6`.
- unicode17-ch3.html: `69fef5215c021368a1880d91bc59d7935d13a5455f1373eda17b8818d41b7b41`.
- unicode17-ch3.txt: `45dfe5474872c20ee8da6b13c2f249108ff8c5942f03ae0761ac2053dbc2f5c5`.
