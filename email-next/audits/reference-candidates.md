---
title: Reference closure candidates
sectionNav: true
---

# Reference closure candidates

This candidate list exposes RFC-number citations outside the current source inventory. It was extracted from complete captured base texts, including prose and reference lists. A citation is not automatically a normative dependency or an in-scope implementation requirement. Historical comparisons, superseded references and informative references are intentionally included for human disposition.

Each candidate needs an applicability decision: required normative behavior, conditional feature dependency, historical context, or out of scope with rationale. Required and conditional dependencies need an appropriate source review and successor/errata checks. No candidate is marked reviewed by extraction. Non-RFC documents, registries and transitive references from these candidates remain separate work.

62 candidates have explicit applicability classifications; classification does not mean their base texts were reviewed.

The scan covered 163 captured texts from 163 inventory records and found 782 distinct out-of-inventory RFC candidates. Missing source texts: none. Input SHA-256 values and parent citations are recorded in `reference-candidates.json` alongside this chapter.

| Candidate | Cited by inventoried RFCs | Disposition |
| --- | --- | --- |
| [RFC733](https://www.rfc-editor.org/rfc/rfc733.html) | 5234, 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC783](https://www.rfc-editor.org/rfc/rfc783.html) | 2046, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC791](https://www.rfc-editor.org/rfc/rfc791.html) | 5280, 5598, 8126, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC793](https://www.rfc-editor.org/rfc/rfc793.html) | 5246, 8314, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC821](https://www.rfc-editor.org/rfc/rfc821.html) | 1870, 1939, 2045, 2046, 2049, 2449, 2557, 2646, 2920, 3030, 3207, 3461, 3463, 3464, 3501, 5321, 5598, 6530 | Historical SMTP predecessor: RFC5321 section1.2 explicitly supersedes this source. Selected transport and routing behavior follows the reviewed RFC5321 contract and applicable updates; omitted historical transport models are not selected. This classification does not claim a review of the predecessor text. [Selected source review](smtp.md). |
| [RFC822](https://www.rfc-editor.org/rfc/rfc822.html) | 1847, 1870, 1939, 2045, 2046, 2047, 2049, 2183, 2184, 2231, 2369, 2387, 2392, 2449, 2480, 2557, 2634, 2919, 3030, 3156, 3461, 3464, 3501, 3503, 3798, 3834, 3864, 3886, 5173, 5234, 5321, 5322, 5335, 5337, 5598, 6522, 6530, 6532, 6533, 6854, 8098, 8551, 8601, 8621, 9051, 9787, 9788, 9991 | Historical message-format predecessor: selected syntax and obsolete-syntax reception follow reviewed RFC5322 and applicable updates. RFC5322 describes the succession through RFC2822; this classification does not claim a review of every historical RFC822 behavior. [Selected source review](message-format.md). |
| [RFC850](https://www.rfc-editor.org/rfc/rfc850.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC934](https://www.rfc-editor.org/rfc/rfc934.html) | 2045, 2046, 2047, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC937](https://www.rfc-editor.org/rfc/rfc937.html) | 5321 | Unclassified citation candidate; applicability and review not established |
| [RFC952](https://www.rfc-editor.org/rfc/rfc952.html) | 3492, 3986, 5890, 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC959](https://www.rfc-editor.org/rfc/rfc959.html) | 2046, 2049, 5321 | Unclassified citation candidate; applicability and review not established |
| [RFC974](https://www.rfc-editor.org/rfc/rfc974.html) | 1870, 5321 | Historical SMTP predecessor: RFC5321 section1.2 explicitly supersedes this source. Selected transport and routing behavior follows the reviewed RFC5321 contract and applicable updates; omitted historical transport models are not selected. This classification does not claim a review of the predecessor text. [Selected source review](smtp.md). |
| [RFC1034](https://www.rfc-editor.org/rfc/rfc1034.html) | 3492, 3986, 5280, 5322, 5598, 5890, 5891, 6376, 7208, 7672, 8552, 8820, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC1035](https://www.rfc-editor.org/rfc/rfc1035.html) | 5321, 5322, 5598, 5890, 5891, 7208, 7489, 7505, 7672, 8552, 8553, 8601, 9788, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC1036](https://www.rfc-editor.org/rfc/rfc1036.html) | 2557, 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC1047](https://www.rfc-editor.org/rfc/rfc1047.html) | 3464, 5321 | Informative explanation of SMTP duplicate delivery: the selected uncertainty and exact-retry rules remain required and are supplied by reviewed RFC5321 and RFC3464. This citation does not add a separately selected mechanism; RFC1047 base text remains unreviewed. [Selected source review](dsn-format.md). |
| [RFC1049](https://www.rfc-editor.org/rfc/rfc1049.html) | 2045, 2046, 2047, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1056](https://www.rfc-editor.org/rfc/rfc1056.html) | 5321 | Unclassified citation candidate; applicability and review not established |
| [RFC1064](https://www.rfc-editor.org/rfc/rfc1064.html) | 3501, 9051 | Historical IMAP2 predecessor: RFC9051 section10 explicitly supersedes RFC1064. Selected IMAP4rev2 behavior follows the reviewed successor; this citation does not select an IMAP2 adapter. The separate IMAP4rev1 compatibility dependency remains open under RFC3501. RFC1064 base text is not claimed reviewed. [Selected source review](imap-access.md). |
| [RFC1123](https://www.rfc-editor.org/rfc/rfc1123.html) | 2045, 2046, 2480, 2557, 2920, 3461, 3464, 3886, 3986, 5280, 5321, 5322, 5890, 6530, 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC1154](https://www.rfc-editor.org/rfc/rfc1154.html) | 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1176](https://www.rfc-editor.org/rfc/rfc1176.html) | 3501, 5321, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC1211](https://www.rfc-editor.org/rfc/rfc1211.html) | 3461 | Historical mailing-list operational evidence motivating DSNs. Selected report syntax and delivery behavior come from reviewed RFC3461/3464; no RFC1211 implementation is selected. Base text unreviewed. [Selected source review](dsn-extension.md). |
| [RFC1305](https://www.rfc-editor.org/rfc/rfc1305.html) | 5322 | Unclassified citation candidate; applicability and review not established |
| [RFC1321](https://www.rfc-editor.org/rfc/rfc1321.html) | 1939, 2104, 2557, 5147, 5246, 6151, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC1341](https://www.rfc-editor.org/rfc/rfc1341.html) | 2046, 2049, 9694 | Historical MIME predecessor: the reviewed MIME series describes the RFC1341/RFC1342 → RFC1521/RFC1522 → RFC2045–2049 succession. Current body and encoded-header handling follows that reviewed series and its updates; historical syntax is not an independent sending profile. This applicability classification does not claim review of the predecessor base text. [Selected source review](mime-conformance.md). |
| [RFC1342](https://www.rfc-editor.org/rfc/rfc1342.html) | 2049 | Historical MIME predecessor: the reviewed MIME series describes the RFC1341/RFC1342 → RFC1521/RFC1522 → RFC2045–2049 succession. Current body and encoded-header handling follows that reviewed series and its updates; historical syntax is not an independent sending profile. This applicability classification does not claim review of the predecessor base text. [Selected source review](mime-conformance.md). |
| [RFC1344](https://www.rfc-editor.org/rfc/rfc1344.html) | 2045, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1345](https://www.rfc-editor.org/rfc/rfc1345.html) | 2045, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1421](https://www.rfc-editor.org/rfc/rfc1421.html) | 2045, 2046, 2049, 4648, 9180 | Unclassified citation candidate; applicability and review not established |
| [RFC1422](https://www.rfc-editor.org/rfc/rfc1422.html) | 2046, 2049, 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC1423](https://www.rfc-editor.org/rfc/rfc1423.html) | 2046, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1424](https://www.rfc-editor.org/rfc/rfc1424.html) | 2046, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1425](https://www.rfc-editor.org/rfc/rfc1425.html) | 2920 | Unclassified citation candidate; applicability and review not established |
| [RFC1428](https://www.rfc-editor.org/rfc/rfc1428.html) | 2557 | Unclassified citation candidate; applicability and review not established |
| [RFC1437](https://www.rfc-editor.org/rfc/rfc1437.html) | 9694 | Historical example in RFC9694 section3: an unregistered April Fools media type. Email Next proposes application subtypes under the reviewed registration rules, so this entertainment example supplies no required wire behavior. RFC1437 base text is not claimed reviewed. [Selected source review](media-top-level.md). |
| [RFC1460](https://www.rfc-editor.org/rfc/rfc1460.html) | 1939 | Historical POP3 ancestry in RFC1939 section14. The selected command, UIDL and transaction semantics come from reviewed RFC1939 and applicable updates; no separate RFC1460 mode is selected. This disposition does not claim review of RFC1460 base text. [Selected source review](pop-base.md). |
| [RFC1496](https://www.rfc-editor.org/rfc/rfc1496.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC1505](https://www.rfc-editor.org/rfc/rfc1505.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC1506](https://www.rfc-editor.org/rfc/rfc1506.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC1521](https://www.rfc-editor.org/rfc/rfc1521.html) | 1847, 1870, 2049, 2183 | Historical MIME predecessor: selected body structure and conformance use reviewed RFC2045, RFC2046 and RFC2049. The MIME series explicitly obsoletes RFC1521; this is not a review of historical implementation deviations. [Selected source review](mime-format.md). |
| [RFC1522](https://www.rfc-editor.org/rfc/rfc1522.html) | 1870, 2047, 2049 | Historical encoded-header predecessor: selected header decoding uses reviewed RFC2047 and applicable updates. RFC2047 explicitly obsoletes RFC1522; no independent legacy deviation is selected from this citation. [Selected source review](header-text.md). |
| [RFC1524](https://www.rfc-editor.org/rfc/rfc1524.html) | 2045, 2049, 2387 | Unclassified citation candidate; applicability and review not established |
| [RFC1535](https://www.rfc-editor.org/rfc/rfc1535.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1543](https://www.rfc-editor.org/rfc/rfc1543.html) | 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1556](https://www.rfc-editor.org/rfc/rfc1556.html) | 2046, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1590](https://www.rfc-editor.org/rfc/rfc1590.html) | 2049, 2387 | Historical MIME registration predecessor: the MIME revision incorporates RFC1590. New media-type registration follows reviewed RFC6838 and its applicable updates; this does not close the separate RFC2048/RFC4289 registration dependencies. This applicability classification does not claim review of the predecessor base text. [Selected source review](mime-conformance.md). |
| [RFC1591](https://www.rfc-editor.org/rfc/rfc1591.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC1602](https://www.rfc-editor.org/rfc/rfc1602.html) | 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1630](https://www.rfc-editor.org/rfc/rfc1630.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1652](https://www.rfc-editor.org/rfc/rfc1652.html) | 2045, 2049, 3030, 4468, 5321, 5335, 5598 | Historical predecessor, superseded by RFC6152. 8BITMIME transport follows RFC6152; the predecessor does not define an additional transport profile. This classification does not claim a review of the predecessor text. [Selected source review](eight-bit-mime.md). |
| [RFC1700](https://www.rfc-editor.org/rfc/rfc1700.html) | 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1725](https://www.rfc-editor.org/rfc/rfc1725.html) | 1939 | Historical POP3 predecessor: reviewed RFC1939 supplies current command, UIDL and transaction behavior, including its explicit corrections to RFC1725. Existing POP adoption uses that successor and applicable updates, not a separate RFC1725 mode. This applicability classification does not claim review of the predecessor base text. [Selected source review](pop-base.md). |
| [RFC1730](https://www.rfc-editor.org/rfc/rfc1730.html) | 1939, 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC1732](https://www.rfc-editor.org/rfc/rfc1732.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC1733](https://www.rfc-editor.org/rfc/rfc1733.html) | 3501, 5598, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC1734](https://www.rfc-editor.org/rfc/rfc1734.html) | 1939, 2449, 5034 | Unclassified citation candidate; applicability and review not established |
| [RFC1736](https://www.rfc-editor.org/rfc/rfc1736.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1737](https://www.rfc-editor.org/rfc/rfc1737.html) | 3864, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1738](https://www.rfc-editor.org/rfc/rfc1738.html) | 2369, 2392, 2557, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1741](https://www.rfc-editor.org/rfc/rfc1741.html) | 2045, 2049 | Unclassified citation candidate; applicability and review not established |
| [RFC1750](https://www.rfc-editor.org/rfc/rfc1750.html) | 2919, 3885 | Unclassified citation candidate; applicability and review not established |
| [RFC1766](https://www.rfc-editor.org/rfc/rfc1766.html) | 2184, 2231, 5646, 8753 | Unclassified citation candidate; applicability and review not established |
| [RFC1767](https://www.rfc-editor.org/rfc/rfc1767.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC1806](https://www.rfc-editor.org/rfc/rfc1806.html) | 2183, 2387 | Unclassified citation candidate; applicability and review not established |
| [RFC1808](https://www.rfc-editor.org/rfc/rfc1808.html) | 2557, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC1826](https://www.rfc-editor.org/rfc/rfc1826.html) | 2104 | Unclassified citation candidate; applicability and review not established |
| [RFC1830](https://www.rfc-editor.org/rfc/rfc1830.html) | 3030 | Unclassified citation candidate; applicability and review not established |
| [RFC1845](https://www.rfc-editor.org/rfc/rfc1845.html) | 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC1846](https://www.rfc-editor.org/rfc/rfc1846.html) | 6409, 7504 | Unclassified citation candidate; applicability and review not established |
| [RFC1848](https://www.rfc-editor.org/rfc/rfc1848.html) | 3156 | Unclassified citation candidate; applicability and review not established |
| [RFC1854](https://www.rfc-editor.org/rfc/rfc1854.html) | 2920 | Unclassified citation candidate; applicability and review not established |
| [RFC1864](https://www.rfc-editor.org/rfc/rfc1864.html) | 3501, 3864, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC1866](https://www.rfc-editor.org/rfc/rfc1866.html) | 2557, 2646, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC1867](https://www.rfc-editor.org/rfc/rfc1867.html) | 7578 | Historical file-upload origin. Current multipart/form-data behavior follows reviewed RFC7578; this classification does not review RFC1867 or select its HTML extensions. [Selected source review](form-data.md). |
| [RFC1869](https://www.rfc-editor.org/rfc/rfc1869.html) | 1870, 2920, 3030, 3885, 3886, 5321 | Historical SMTP predecessor: RFC5321 section1.2 explicitly supersedes this source. Selected transport and routing behavior follows the reviewed RFC5321 contract and applicable updates; omitted historical transport models are not selected. This classification does not claim a review of the predecessor text. [Selected source review](smtp.md). |
| [RFC1873](https://www.rfc-editor.org/rfc/rfc1873.html) | 2387 | Unclassified citation candidate; applicability and review not established |
| [RFC1891](https://www.rfc-editor.org/rfc/rfc1891.html) | 3461 | Historical report predecessor: selected behavior follows reviewed RFC3461, including ASCII-before-xtext clarification and security considerations. The older text is not a separate compatibility profile and has not been reviewed in this classification. [Selected source review](dsn-extension.md). |
| [RFC1892](https://www.rfc-editor.org/rfc/rfc1892.html) | 6522 | Unclassified citation candidate; applicability and review not established |
| [RFC1893](https://www.rfc-editor.org/rfc/rfc1893.html) | 3463, 5248 | Unclassified citation candidate; applicability and review not established |
| [RFC1894](https://www.rfc-editor.org/rfc/rfc1894.html) | 3464 | Historical report predecessor: selected behavior follows reviewed RFC3464, including corrected delayed report example and gateway MTA-name type. The older text is not a separate compatibility profile and has not been reviewed in this classification. [Selected source review](dsn-format.md). |
| [RFC1896](https://www.rfc-editor.org/rfc/rfc1896.html) | 2046, 2049, 2646, 3676 | Unclassified citation candidate; applicability and review not established |
| [RFC1919](https://www.rfc-editor.org/rfc/rfc1919.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC1945](https://www.rfc-editor.org/rfc/rfc1945.html) | 2557, 3864, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC1948](https://www.rfc-editor.org/rfc/rfc1948.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC1950](https://www.rfc-editor.org/rfc/rfc1950.html) | 9110, 9580 | Selected PNG decompression dependency: RFC1950 sections 2.1–2.3 reviewed with current errata and update checks. The image-format audit defines the selected zlib/DEFLATE path. This is not a complete RFC base review, codec certification or review of every HTTP/OpenPGP compression use. [Selected source review](image-formats.md). |
| [RFC1951](https://www.rfc-editor.org/rfc/rfc1951.html) | 9110, 9580 | Selected PNG decompression dependency: RFC1951 sections 3.1–3.3 reviewed with current errata and update checks. The image-format audit defines the selected zlib/DEFLATE path. This is not a complete RFC base review, codec certification or review of every HTTP/OpenPGP compression use. [Selected source review](image-formats.md). |
| [RFC1952](https://www.rfc-editor.org/rfc/rfc1952.html) | 8460, 9110, 9990 | Unclassified citation candidate; applicability and review not established |
| [RFC1983](https://www.rfc-editor.org/rfc/rfc1983.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC1985](https://www.rfc-editor.org/rfc/rfc1985.html) | 5321, 5598, 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC1991](https://www.rfc-editor.org/rfc/rfc1991.html) | 3156, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC2015](https://www.rfc-editor.org/rfc/rfc2015.html) | 3156, 3676, 4954 | Unclassified citation candidate; applicability and review not established |
| [RFC2017](https://www.rfc-editor.org/rfc/rfc2017.html) | 2557 | Unclassified citation candidate; applicability and review not established |
| [RFC2026](https://www.rfc-editor.org/rfc/rfc2026.html) | 3864, 5646, 6838, 6854, 8126, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC2028](https://www.rfc-editor.org/rfc/rfc2028.html) | 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC2033](https://www.rfc-editor.org/rfc/rfc2033.html) | 3886, 5429, 5598, 6531, 8689 | Unclassified citation candidate; applicability and review not established |
| [RFC2034](https://www.rfc-editor.org/rfc/rfc2034.html) | 3207, 4468, 4954, 5429, 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC2044](https://www.rfc-editor.org/rfc/rfc2044.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC2048](https://www.rfc-editor.org/rfc/rfc2048.html) | 2045, 2046, 2047, 2049, 2183, 2184, 2231, 2557, 5228, 6838, 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC2060](https://www.rfc-editor.org/rfc/rfc2060.html) | 2184, 2231, 2449, 3461, 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2061](https://www.rfc-editor.org/rfc/rfc2061.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2062](https://www.rfc-editor.org/rfc/rfc2062.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2068](https://www.rfc-editor.org/rfc/rfc2068.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2070](https://www.rfc-editor.org/rfc/rfc2070.html) | 2557 | Unclassified citation candidate; applicability and review not established |
| [RFC2076](https://www.rfc-editor.org/rfc/rfc2076.html) | 3834 | Unclassified citation candidate; applicability and review not established |
| [RFC2077](https://www.rfc-editor.org/rfc/rfc2077.html) | 9051, 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC2086](https://www.rfc-editor.org/rfc/rfc2086.html) | 3503 | Unclassified citation candidate; applicability and review not established |
| [RFC2087](https://www.rfc-editor.org/rfc/rfc2087.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2110](https://www.rfc-editor.org/rfc/rfc2110.html) | 2557 | Unclassified citation candidate; applicability and review not established |
| [RFC2111](https://www.rfc-editor.org/rfc/rfc2111.html) | 2387, 2392 | Unclassified citation candidate; applicability and review not established |
| [RFC2112](https://www.rfc-editor.org/rfc/rfc2112.html) | 2387 | Unclassified citation candidate; applicability and review not established |
| [RFC2130](https://www.rfc-editor.org/rfc/rfc2130.html) | 2184, 2231 | Unclassified citation candidate; applicability and review not established |
| [RFC2132](https://www.rfc-editor.org/rfc/rfc2132.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC2136](https://www.rfc-editor.org/rfc/rfc2136.html) | 7672 | Unclassified citation candidate; applicability and review not established |
| [RFC2141](https://www.rfc-editor.org/rfc/rfc2141.html) | 3864, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2142](https://www.rfc-editor.org/rfc/rfc2142.html) | 2369, 5598, 7293, 7489, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC2144](https://www.rfc-editor.org/rfc/rfc2144.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC2145](https://www.rfc-editor.org/rfc/rfc2145.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2152](https://www.rfc-editor.org/rfc/rfc2152.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2156](https://www.rfc-editor.org/rfc/rfc2156.html) | 3834, 3864, 5321 | Unclassified citation candidate; applicability and review not established |
| [RFC2177](https://www.rfc-editor.org/rfc/rfc2177.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2180](https://www.rfc-editor.org/rfc/rfc2180.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2181](https://www.rfc-editor.org/rfc/rfc2181.html) | 5321, 5598, 5890, 7672, 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC2192](https://www.rfc-editor.org/rfc/rfc2192.html) | 4468 | Unclassified citation candidate; applicability and review not established |
| [RFC2193](https://www.rfc-editor.org/rfc/rfc2193.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2195](https://www.rfc-editor.org/rfc/rfc2195.html) | 4954 | Unclassified citation candidate; applicability and review not established |
| [RFC2197](https://www.rfc-editor.org/rfc/rfc2197.html) | 2449, 2920 | Unclassified citation candidate; applicability and review not established |
| [RFC2202](https://www.rfc-editor.org/rfc/rfc2202.html) | 6151 | Unclassified citation candidate; applicability and review not established |
| [RFC2222](https://www.rfc-editor.org/rfc/rfc2222.html) | 2449, 3207, 3501 | Unclassified citation candidate; applicability and review not established |
| [RFC2227](https://www.rfc-editor.org/rfc/rfc2227.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC2234](https://www.rfc-editor.org/rfc/rfc2234.html) | 2449, 2557, 2646, 2919, 3501, 3629, 3676, 3834, 3885, 3886, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2244](https://www.rfc-editor.org/rfc/rfc2244.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2245](https://www.rfc-editor.org/rfc/rfc2245.html) | 3501 | Unclassified citation candidate; applicability and review not established |
| [RFC2246](https://www.rfc-editor.org/rfc/rfc2246.html) | 3207, 3501, 5077, 5246, 6749, 6750, 8996, 9325, 9846 | TLS1.0 is prohibited by reviewed RFC8996. Historical references do not authorize its negotiation or fallback in the selected service profile; no independent implementation of this obsolete version is selected. [Selected source review](tls-deprecation.md). |
| [RFC2268](https://www.rfc-editor.org/rfc/rfc2268.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2277](https://www.rfc-editor.org/rfc/rfc2277.html) | 5280, 5337, 5646, 6533 | Unclassified citation candidate; applicability and review not established |
| [RFC2279](https://www.rfc-editor.org/rfc/rfc2279.html) | 2634, 3629, 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC2295](https://www.rfc-editor.org/rfc/rfc2295.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2298](https://www.rfc-editor.org/rfc/rfc2298.html) | 3503, 3798, 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC2308](https://www.rfc-editor.org/rfc/rfc2308.html) | 7208, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC2311](https://www.rfc-editor.org/rfc/rfc2311.html) | 2634, 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2312](https://www.rfc-editor.org/rfc/rfc2312.html) | 2634, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2313](https://www.rfc-editor.org/rfc/rfc2313.html) | 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2314](https://www.rfc-editor.org/rfc/rfc2314.html) | 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2315](https://www.rfc-editor.org/rfc/rfc2315.html) | 2634, 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2324](https://www.rfc-editor.org/rfc/rfc2324.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2342](https://www.rfc-editor.org/rfc/rfc2342.html) | 9042, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2368](https://www.rfc-editor.org/rfc/rfc2368.html) | 2369, 5436 | Unclassified citation candidate; applicability and review not established |
| [RFC2388](https://www.rfc-editor.org/rfc/rfc2388.html) | 7578 | Historical predecessor replaced by reviewed RFC7578. Legacy nested multipart reception remains covered by the successor’s explicit compatibility rule; the old base text is not separately reviewed. [Selected source review](form-data.md). |
| [RFC2389](https://www.rfc-editor.org/rfc/rfc2389.html) | 2557 | Unclassified citation candidate; applicability and review not established |
| [RFC2396](https://www.rfc-editor.org/rfc/rfc2396.html) | 3864, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2421](https://www.rfc-editor.org/rfc/rfc2421.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC2434](https://www.rfc-editor.org/rfc/rfc2434.html) | 2449, 3834, 3864, 5116, 5246, 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC2437](https://www.rfc-editor.org/rfc/rfc2437.html) | 5652 | Unclassified citation candidate; applicability and review not established |
| [RFC2440](https://www.rfc-editor.org/rfc/rfc2440.html) | 3156, 3676, 4648, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC2442](https://www.rfc-editor.org/rfc/rfc2442.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC2459](https://www.rfc-editor.org/rfc/rfc2459.html) | 5280, 9608 | Unclassified citation candidate; applicability and review not established |
| [RFC2460](https://www.rfc-editor.org/rfc/rfc2460.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC2476](https://www.rfc-editor.org/rfc/rfc2476.html) | 3030, 3207, 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC2487](https://www.rfc-editor.org/rfc/rfc2487.html) | 3207 | Unclassified citation candidate; applicability and review not established |
| [RFC2505](https://www.rfc-editor.org/rfc/rfc2505.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC2518](https://www.rfc-editor.org/rfc/rfc2518.html) | 3864, 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2554](https://www.rfc-editor.org/rfc/rfc2554.html) | 3207, 4468, 4954, 5034 | Historical SMTP AUTH predecessor: reviewed RFC4954 specifies AUTH, envelope authentication parameters, status handling and corrections to RFC2554. Its SASL and TLS dependencies remain separate; obsolete status behavior is not revived. This applicability classification does not claim review of the predecessor base text. [Selected source review](smtp-authentication.md). |
| [RFC2560](https://www.rfc-editor.org/rfc/rfc2560.html) | 5280, 5652 | Unclassified citation candidate; applicability and review not established |
| [RFC2585](https://www.rfc-editor.org/rfc/rfc2585.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC2595](https://www.rfc-editor.org/rfc/rfc2595.html) | 3501, 5034, 6186, 7817, 8314, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2606](https://www.rfc-editor.org/rfc/rfc2606.html) | 2919 | Unclassified citation candidate; applicability and review not established |
| [RFC2616](https://www.rfc-editor.org/rfc/rfc2616.html) | 3864, 5280, 5646, 5890, 6657, 6749, 6750, 6838, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2617](https://www.rfc-editor.org/rfc/rfc2617.html) | 3864, 6749, 6750, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2630](https://www.rfc-editor.org/rfc/rfc2630.html) | 2634, 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2631](https://www.rfc-editor.org/rfc/rfc2631.html) | 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2632](https://www.rfc-editor.org/rfc/rfc2632.html) | 2634, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2633](https://www.rfc-editor.org/rfc/rfc2633.html) | 2634, 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2645](https://www.rfc-editor.org/rfc/rfc2645.html) | 5598, 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC2671](https://www.rfc-editor.org/rfc/rfc2671.html) | 5891, 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC2672](https://www.rfc-editor.org/rfc/rfc2672.html) | 5893 | Unclassified citation candidate; applicability and review not established |
| [RFC2673](https://www.rfc-editor.org/rfc/rfc2673.html) | 5890 | Unclassified citation candidate; applicability and review not established |
| [RFC2683](https://www.rfc-editor.org/rfc/rfc2683.html) | 3501, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC2712](https://www.rfc-editor.org/rfc/rfc2712.html) | 5077 | Unclassified citation candidate; applicability and review not established |
| [RFC2717](https://www.rfc-editor.org/rfc/rfc2717.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2718](https://www.rfc-editor.org/rfc/rfc2718.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2732](https://www.rfc-editor.org/rfc/rfc2732.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC2774](https://www.rfc-editor.org/rfc/rfc2774.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2781](https://www.rfc-editor.org/rfc/rfc2781.html) | 3030, 5147, 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC2782](https://www.rfc-editor.org/rfc/rfc2782.html) | 5890, 6186, 7208, 7505, 8552, 8553, 8620, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC2785](https://www.rfc-editor.org/rfc/rfc2785.html) | 5246, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC2797](https://www.rfc-editor.org/rfc/rfc2797.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC2818](https://www.rfc-editor.org/rfc/rfc2818.html) | 6749, 6750, 8461, 8620, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC2821](https://www.rfc-editor.org/rfc/rfc2821.html) | 3207, 3501, 3676, 3798, 3864, 3885, 4468, 4865, 4954, 5228, 5248, 5280, 5321, 5335, 5337, 5598, 6530 | Historical SMTP predecessor: selected transport behavior is reviewed under RFC5321 and its applicable updates. RFC5321 explicitly obsoletes this document; this disposition does not claim a full review of historical differences. [Selected source review](smtp.md). |
| [RFC2822](https://www.rfc-editor.org/rfc/rfc2822.html) | 2919, 3501, 3676, 3798, 3834, 3864, 3885, 3886, 4865, 5173, 5228, 5322, 5335, 5337, 5598, 9580 | Historical message-format predecessor: selected behavior, including obsolete-syntax reception, is reviewed under RFC5322 and applicable updates. RFC5322 explicitly obsoletes this document; historical differences are not counted as reviewed. [Selected source review](message-format.md). |
| [RFC2831](https://www.rfc-editor.org/rfc/rfc2831.html) | 3501 | Unclassified citation candidate; applicability and review not established |
| [RFC2852](https://www.rfc-editor.org/rfc/rfc2852.html) | 3885, 4865, 6409, 8621 | Unclassified citation candidate; applicability and review not established |
| [RFC2854](https://www.rfc-editor.org/rfc/rfc2854.html) | 5147, 6657 | Unclassified citation candidate; applicability and review not established |
| [RFC2860](https://www.rfc-editor.org/rfc/rfc2860.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC2898](https://www.rfc-editor.org/rfc/rfc2898.html) | 5869 | Unclassified citation candidate; applicability and review not established |
| [RFC2912](https://www.rfc-editor.org/rfc/rfc2912.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC2938](https://www.rfc-editor.org/rfc/rfc2938.html) | 4648 | Unclassified citation candidate; applicability and review not established |
| [RFC2939](https://www.rfc-editor.org/rfc/rfc2939.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC2965](https://www.rfc-editor.org/rfc/rfc2965.html) | 3864 | Unclassified citation candidate; applicability and review not established |
| [RFC2978](https://www.rfc-editor.org/rfc/rfc2978.html) | 3501, 3629, 3986, 5147, 6838, 9051, 9110, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC2979](https://www.rfc-editor.org/rfc/rfc2979.html) | 5321, 8314 | Unclassified citation candidate; applicability and review not established |
| [RFC2985](https://www.rfc-editor.org/rfc/rfc2985.html) | 5280, 8550 | Unclassified citation candidate; applicability and review not established |
| [RFC3023](https://www.rfc-editor.org/rfc/rfc3023.html) | 6657, 6838, 6839 | Unclassified citation candidate; applicability and review not established |
| [RFC3028](https://www.rfc-editor.org/rfc/rfc3028.html) | 5228, 5429 | Unclassified citation candidate; applicability and review not established |
| [RFC3040](https://www.rfc-editor.org/rfc/rfc3040.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC3066](https://www.rfc-editor.org/rfc/rfc3066.html) | 3501, 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC3114](https://www.rfc-editor.org/rfc/rfc3114.html) | 8550 | Company classification-label policy is not selected for Email Next. The parent citation illustrates an optional attribute-certificate application, not basic S/MIME key validation. Base text not reviewed. [Selected source review](smime-certificates.md). |
| [RFC3161](https://www.rfc-editor.org/rfc/rfc3161.html) | 5280, 8933 | Unclassified citation candidate; applicability and review not established |
| [RFC3192](https://www.rfc-editor.org/rfc/rfc3192.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC3206](https://www.rfc-editor.org/rfc/rfc3206.html) | 5034 | Unclassified citation candidate; applicability and review not established |
| [RFC3211](https://www.rfc-editor.org/rfc/rfc3211.html) | 5652 | Unclassified citation candidate; applicability and review not established |
| [RFC3218](https://www.rfc-editor.org/rfc/rfc3218.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC3228](https://www.rfc-editor.org/rfc/rfc3228.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3230](https://www.rfc-editor.org/rfc/rfc3230.html) | 9404 | Unclassified citation candidate; applicability and review not established |
| [RFC3249](https://www.rfc-editor.org/rfc/rfc3249.html) | 8098 | Fax application profile is outside the selected Email Next feature set. The MDN automatic-action label remains supported without implementing fax processing. This classification does not review RFC3249 or imply rejection of ordinary messages containing fax documents. [Selected source review](disposition-notifications.md). |
| [RFC3261](https://www.rfc-editor.org/rfc/rfc3261.html) | 3864, 8996, 9325, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC3263](https://www.rfc-editor.org/rfc/rfc3263.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC3268](https://www.rfc-editor.org/rfc/rfc3268.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC3274](https://www.rfc-editor.org/rfc/rfc3274.html) | 8551, 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC3279](https://www.rfc-editor.org/rfc/rfc3279.html) | 5280, 8550, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC3280](https://www.rfc-editor.org/rfc/rfc3280.html) | 4954, 5035, 5246, 5280, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC3281](https://www.rfc-editor.org/rfc/rfc3281.html) | 5652, 9608 | Unclassified citation candidate; applicability and review not established |
| [RFC3282](https://www.rfc-editor.org/rfc/rfc3282.html) | 3864, 5646, 8621, 8753, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC3297](https://www.rfc-editor.org/rfc/rfc3297.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC3305](https://www.rfc-editor.org/rfc/rfc3305.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC3315](https://www.rfc-editor.org/rfc/rfc3315.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3316](https://www.rfc-editor.org/rfc/rfc3316.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3329](https://www.rfc-editor.org/rfc/rfc3329.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3339](https://www.rfc-editor.org/rfc/rfc3339.html) | 4865, 5646, 7293, 8460, 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC3348](https://www.rfc-editor.org/rfc/rfc3348.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC3369](https://www.rfc-editor.org/rfc/rfc3369.html) | 5652 | Historical CMS revision. Current CMS processing and explicit PKCS#7 compatibility follow RFC5652 and its reviewed updates; this does not review the old base or select an old CMS profile. [Selected source review](cms.md). |
| [RFC3370](https://www.rfc-editor.org/rfc/rfc3370.html) | 5652, 6211, 8551, 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC3394](https://www.rfc-editor.org/rfc/rfc3394.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC3403](https://www.rfc-editor.org/rfc/rfc3403.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC3436](https://www.rfc-editor.org/rfc/rfc3436.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3447](https://www.rfc-editor.org/rfc/rfc3447.html) | 5246, 6211, 6376, 8463, 8550 | Unclassified citation candidate; applicability and review not established |
| [RFC3454](https://www.rfc-editor.org/rfc/rfc3454.html) | 4954, 5034, 5280, 5890, 5892, 5893, 8753, 9233 | Unclassified citation candidate; applicability and review not established |
| [RFC3458](https://www.rfc-editor.org/rfc/rfc3458.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC3462](https://www.rfc-editor.org/rfc/rfc3462.html) | 3461, 3464, 3798, 5337, 5429, 5598, 6522 | Historical report predecessor: selected behavior follows reviewed RFC6522, including removal of the outermost-only multipart/report constraint. The older text is not a separate compatibility profile and has not been reviewed in this classification. [Selected source review](report-container.md). |
| [RFC3470](https://www.rfc-editor.org/rfc/rfc3470.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3489](https://www.rfc-editor.org/rfc/rfc3489.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3490](https://www.rfc-editor.org/rfc/rfc3490.html) | 3492, 3986, 5280, 5890, 5891, 6818, 8753, 9233, 9549 | Unclassified citation candidate; applicability and review not established |
| [RFC3491](https://www.rfc-editor.org/rfc/rfc3491.html) | 3492, 5890, 5891, 5892, 8753, 9233 | Unclassified citation candidate; applicability and review not established |
| [RFC3502](https://www.rfc-editor.org/rfc/rfc3502.html) | 6785, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC3513](https://www.rfc-editor.org/rfc/rfc3513.html) | 3986 | Unclassified citation candidate; applicability and review not established |
| [RFC3516](https://www.rfc-editor.org/rfc/rfc3516.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC3526](https://www.rfc-editor.org/rfc/rfc3526.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC3529](https://www.rfc-editor.org/rfc/rfc3529.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC3546](https://www.rfc-editor.org/rfc/rfc3546.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3548](https://www.rfc-editor.org/rfc/rfc3548.html) | 4648 | Historical predecessor; RFC4648 supplies the selected byte-encoding contract. No implementation of the obsolete version is selected. |
| [RFC3552](https://www.rfc-editor.org/rfc/rfc3552.html) | 5646, 8126, 8601, 8996, 9750, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC3553](https://www.rfc-editor.org/rfc/rfc3553.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC3560](https://www.rfc-editor.org/rfc/rfc3560.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC3565](https://www.rfc-editor.org/rfc/rfc3565.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC3568](https://www.rfc-editor.org/rfc/rfc3568.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3575](https://www.rfc-editor.org/rfc/rfc3575.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3588](https://www.rfc-editor.org/rfc/rfc3588.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3596](https://www.rfc-editor.org/rfc/rfc3596.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC3602](https://www.rfc-editor.org/rfc/rfc3602.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC3620](https://www.rfc-editor.org/rfc/rfc3620.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC3647](https://www.rfc-editor.org/rfc/rfc3647.html) | 9608 | Unclassified citation candidate; applicability and review not established |
| [RFC3656](https://www.rfc-editor.org/rfc/rfc3656.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3688](https://www.rfc-editor.org/rfc/rfc3688.html) | 9990 | Unclassified citation candidate; applicability and review not established |
| [RFC3691](https://www.rfc-editor.org/rfc/rfc3691.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC3692](https://www.rfc-editor.org/rfc/rfc3692.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3696](https://www.rfc-editor.org/rfc/rfc3696.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC3713](https://www.rfc-editor.org/rfc/rfc3713.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC3734](https://www.rfc-editor.org/rfc/rfc3734.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3748](https://www.rfc-editor.org/rfc/rfc3748.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3749](https://www.rfc-editor.org/rfc/rfc3749.html) | 5246, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3766](https://www.rfc-editor.org/rfc/rfc3766.html) | 5246, 6376, 8551, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC3767](https://www.rfc-editor.org/rfc/rfc3767.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3801](https://www.rfc-editor.org/rfc/rfc3801.html) | 3864, 5598, 8098 | Specialized VPIM voice gateway behavior is not selected. General message transport, opaque local parts and MDN labels do not require implementing voice gateway addressing or processing. Base text remains unreviewed; the cross-reference label mismatch is not treated as protocol evidence. [Selected source review](disposition-notifications.md). |
| [RFC3832](https://www.rfc-editor.org/rfc/rfc3832.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC3833](https://www.rfc-editor.org/rfc/rfc3833.html) | 6376, 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC3848](https://www.rfc-editor.org/rfc/rfc3848.html) | 4954, 5321, 6531, 8314 | Unclassified citation candidate; applicability and review not established |
| [RFC3850](https://www.rfc-editor.org/rfc/rfc3850.html) | 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC3851](https://www.rfc-editor.org/rfc/rfc3851.html) | 4954, 5321, 5598, 5652, 8550, 8551, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC3852](https://www.rfc-editor.org/rfc/rfc3852.html) | 5035, 5652, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC3856](https://www.rfc-editor.org/rfc/rfc3856.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3865](https://www.rfc-editor.org/rfc/rfc3865.html) | 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC3871](https://www.rfc-editor.org/rfc/rfc3871.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3875](https://www.rfc-editor.org/rfc/rfc3875.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC3887](https://www.rfc-editor.org/rfc/rfc3887.html) | 3885, 3886, 8553, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3888](https://www.rfc-editor.org/rfc/rfc3888.html) | 3885, 3886 | Unclassified citation candidate; applicability and review not established |
| [RFC3894](https://www.rfc-editor.org/rfc/rfc3894.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC3903](https://www.rfc-editor.org/rfc/rfc3903.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3920](https://www.rfc-editor.org/rfc/rfc3920.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3921](https://www.rfc-editor.org/rfc/rfc3921.html) | 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC3941](https://www.rfc-editor.org/rfc/rfc3941.html) | 5890 | Unclassified citation candidate; applicability and review not established |
| [RFC3942](https://www.rfc-editor.org/rfc/rfc3942.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3943](https://www.rfc-editor.org/rfc/rfc3943.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3958](https://www.rfc-editor.org/rfc/rfc3958.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC3968](https://www.rfc-editor.org/rfc/rfc3968.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC3974](https://www.rfc-editor.org/rfc/rfc3974.html) | 5321 | Unclassified citation candidate; applicability and review not established |
| [RFC3978](https://www.rfc-editor.org/rfc/rfc3978.html) | 4648 | Unclassified citation candidate; applicability and review not established |
| [RFC3979](https://www.rfc-editor.org/rfc/rfc3979.html) | 6838 | Unclassified citation candidate; applicability and review not established |
| [RFC3983](https://www.rfc-editor.org/rfc/rfc3983.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC3987](https://www.rfc-editor.org/rfc/rfc3987.html) | 5147, 5280, 5891, 6530, 9549 | Unclassified citation candidate; applicability and review not established |
| [RFC4013](https://www.rfc-editor.org/rfc/rfc4013.html) | 4954, 5034 | Unclassified citation candidate; applicability and review not established |
| [RFC4021](https://www.rfc-editor.org/rfc/rfc4021.html) | 5322, 5598, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC4025](https://www.rfc-editor.org/rfc/rfc4025.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4033](https://www.rfc-editor.org/rfc/rfc4033.html) | 4648, 6376, 7208, 7489, 7672, 7817, 8314, 8461, 8689, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC4034](https://www.rfc-editor.org/rfc/rfc4034.html) | 7672, 7817, 8689 | Unclassified citation candidate; applicability and review not established |
| [RFC4035](https://www.rfc-editor.org/rfc/rfc4035.html) | 7672, 7817, 8689 | Unclassified citation candidate; applicability and review not established |
| [RFC4044](https://www.rfc-editor.org/rfc/rfc4044.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4055](https://www.rfc-editor.org/rfc/rfc4055.html) | 5280, 8550 | Unclassified citation candidate; applicability and review not established |
| [RFC4056](https://www.rfc-editor.org/rfc/rfc4056.html) | 6211, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC4086](https://www.rfc-editor.org/rfc/rfc4086.html) | 5077, 5116, 5246, 5652, 8032, 8551, 9580, 9629, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC4097](https://www.rfc-editor.org/rfc/rfc4097.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4106](https://www.rfc-editor.org/rfc/rfc4106.html) | 5116 | Unclassified citation candidate; applicability and review not established |
| [RFC4107](https://www.rfc-editor.org/rfc/rfc4107.html) | 5116 | Unclassified citation candidate; applicability and review not established |
| [RFC4111](https://www.rfc-editor.org/rfc/rfc4111.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4120](https://www.rfc-editor.org/rfc/rfc4120.html) | 4468, 5077, 5280, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC4124](https://www.rfc-editor.org/rfc/rfc4124.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4132](https://www.rfc-editor.org/rfc/rfc4132.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4134](https://www.rfc-editor.org/rfc/rfc4134.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC4141](https://www.rfc-editor.org/rfc/rfc4141.html) | 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC4142](https://www.rfc-editor.org/rfc/rfc4142.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC4143](https://www.rfc-editor.org/rfc/rfc4143.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC4155](https://www.rfc-editor.org/rfc/rfc4155.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC4158](https://www.rfc-editor.org/rfc/rfc4158.html) | 9925 | Unclassified citation candidate; applicability and review not established |
| [RFC4162](https://www.rfc-editor.org/rfc/rfc4162.html) | 8996, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC4168](https://www.rfc-editor.org/rfc/rfc4168.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4169](https://www.rfc-editor.org/rfc/rfc4169.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4210](https://www.rfc-editor.org/rfc/rfc4210.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4217](https://www.rfc-editor.org/rfc/rfc4217.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4227](https://www.rfc-editor.org/rfc/rfc4227.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC4231](https://www.rfc-editor.org/rfc/rfc4231.html) | 6151 | Unclassified citation candidate; applicability and review not established |
| [RFC4234](https://www.rfc-editor.org/rfc/rfc4234.html) | 4468, 4865, 4954, 5034, 5228, 5229 | Unclassified citation candidate; applicability and review not established |
| [RFC4235](https://www.rfc-editor.org/rfc/rfc4235.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4244](https://www.rfc-editor.org/rfc/rfc4244.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4261](https://www.rfc-editor.org/rfc/rfc4261.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4270](https://www.rfc-editor.org/rfc/rfc4270.html) | 6151, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC4271](https://www.rfc-editor.org/rfc/rfc4271.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4279](https://www.rfc-editor.org/rfc/rfc4279.html) | 5077, 5246, 8996, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC4283](https://www.rfc-editor.org/rfc/rfc4283.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4288](https://www.rfc-editor.org/rfc/rfc4288.html) | 5147, 5322, 5598, 6522, 6838, 8126 | Historical media-registration predecessor: reviewed RFC6838 replaces the registration process, structured suffix rules, review procedure and template. New Email Next registrations use that successor and updates; RFC4288 is not an alternative registration route. This applicability classification does not claim review of the predecessor base text. [Selected source review](media-registration.md). |
| [RFC4289](https://www.rfc-editor.org/rfc/rfc4289.html) | 5322, 5598, 8551, 9110, 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC4291](https://www.rfc-editor.org/rfc/rfc4291.html) | 5321, 7208, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC4301](https://www.rfc-editor.org/rfc/rfc4301.html) | 6409 | Unclassified citation candidate; applicability and review not established |
| [RFC4302](https://www.rfc-editor.org/rfc/rfc4302.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC4303](https://www.rfc-editor.org/rfc/rfc4303.html) | 5116, 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC4306](https://www.rfc-editor.org/rfc/rfc4306.html) | 5869 | Unclassified citation candidate; applicability and review not established |
| [RFC4307](https://www.rfc-editor.org/rfc/rfc4307.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC4309](https://www.rfc-editor.org/rfc/rfc4309.html) | 5116 | Unclassified citation candidate; applicability and review not established |
| [RFC4314](https://www.rfc-editor.org/rfc/rfc4314.html) | 8621, 9042, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4315](https://www.rfc-editor.org/rfc/rfc4315.html) | 6785, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4325](https://www.rfc-editor.org/rfc/rfc4325.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4340](https://www.rfc-editor.org/rfc/rfc4340.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4343](https://www.rfc-editor.org/rfc/rfc4343.html) | 7489, 9525, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC4346](https://www.rfc-editor.org/rfc/rfc4346.html) | 4954, 5034, 5077, 5246, 5289, 8314, 8996, 8997, 9325, 9846, 10015 | TLS1.1 is prohibited by reviewed RFC8996. Historical references do not authorize its negotiation or fallback in the selected service profile; no independent implementation of this obsolete version is selected. [Selected source review](tls-deprecation.md). |
| [RFC4347](https://www.rfc-editor.org/rfc/rfc4347.html) | 8996, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC4356](https://www.rfc-editor.org/rfc/rfc4356.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC4366](https://www.rfc-editor.org/rfc/rfc4366.html) | 5077, 5246, 8996, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC4386](https://www.rfc-editor.org/rfc/rfc4386.html) | 8552, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC4387](https://www.rfc-editor.org/rfc/rfc4387.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC4406](https://www.rfc-editor.org/rfc/rfc4406.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC4408](https://www.rfc-editor.org/rfc/rfc4408.html) | 5321, 7208 | Historical SPF predecessor: reviewed RFC7208 retains deployed ptr/%p behavior while discouraging it, removes SPF RR type 99 and revises lookup limits. Current SPF assessment follows that successor and updates; RFC4408 is not an alternative policy. This applicability classification does not claim review of the predecessor base text. [Selected source review](spf.md). |
| [RFC4409](https://www.rfc-editor.org/rfc/rfc4409.html) | 4468, 4865, 4954, 5321, 5598, 6186, 6376, 6409 | Historical submission predecessor: RFC6409 Appendix A states the protocol is not substantively different, while updating references and clarifications. Selected submission behavior follows reviewed RFC6409 plus its TLS update rather than a separate RFC4409 profile. This applicability classification does not claim review of the predecessor base text. [Selected source review](submission.md). |
| [RFC4422](https://www.rfc-editor.org/rfc/rfc4422.html) | 4954, 5034, 8126, 8314, 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4446](https://www.rfc-editor.org/rfc/rfc4446.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4466](https://www.rfc-editor.org/rfc/rfc4466.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4467](https://www.rfc-editor.org/rfc/rfc4467.html) | 4468 | Unclassified citation candidate; applicability and review not established |
| [RFC4491](https://www.rfc-editor.org/rfc/rfc4491.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4492](https://www.rfc-editor.org/rfc/rfc4492.html) | 5246, 5289, 8996, 9846, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC4493](https://www.rfc-editor.org/rfc/rfc4493.html) | 6151 | Unclassified citation candidate; applicability and review not established |
| [RFC4497](https://www.rfc-editor.org/rfc/rfc4497.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4505](https://www.rfc-editor.org/rfc/rfc4505.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4506](https://www.rfc-editor.org/rfc/rfc4506.html) | 5246 | Unclassified citation candidate; applicability and review not established |
| [RFC4507](https://www.rfc-editor.org/rfc/rfc4507.html) | 5077, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4510](https://www.rfc-editor.org/rfc/rfc4510.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4511](https://www.rfc-editor.org/rfc/rfc4511.html) | 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC4512](https://www.rfc-editor.org/rfc/rfc4512.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4513](https://www.rfc-editor.org/rfc/rfc4513.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4514](https://www.rfc-editor.org/rfc/rfc4514.html) | 5280, 9525, 9925 | Unclassified citation candidate; applicability and review not established |
| [RFC4516](https://www.rfc-editor.org/rfc/rfc4516.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4518](https://www.rfc-editor.org/rfc/rfc4518.html) | 5280, 9549 | Unclassified citation candidate; applicability and review not established |
| [RFC4519](https://www.rfc-editor.org/rfc/rfc4519.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4520](https://www.rfc-editor.org/rfc/rfc4520.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4523](https://www.rfc-editor.org/rfc/rfc4523.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4531](https://www.rfc-editor.org/rfc/rfc4531.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4540](https://www.rfc-editor.org/rfc/rfc4540.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4549](https://www.rfc-editor.org/rfc/rfc4549.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4550](https://www.rfc-editor.org/rfc/rfc4550.html) | 5598 | Unclassified citation candidate; applicability and review not established |
| [RFC4559](https://www.rfc-editor.org/rfc/rfc4559.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC4572](https://www.rfc-editor.org/rfc/rfc4572.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4582](https://www.rfc-editor.org/rfc/rfc4582.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4589](https://www.rfc-editor.org/rfc/rfc4589.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4592](https://www.rfc-editor.org/rfc/rfc4592.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC4616](https://www.rfc-editor.org/rfc/rfc4616.html) | 4954, 5034, 8621, 8996, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4627](https://www.rfc-editor.org/rfc/rfc4627.html) | 6749, 6839, 8259 | Historical predecessor, superseded by RFC7159, itself superseded by RFC8259. JSON encoding follows RFC8259 and the selected application constraints; the older object/array-only JSON definition is not a second decoding mode. This classification does not claim a review of the predecessor text. [Selected source review](json-encoding.md). |
| [RFC4630](https://www.rfc-editor.org/rfc/rfc4630.html) | 5280 | Unclassified citation candidate; applicability and review not established |
| [RFC4632](https://www.rfc-editor.org/rfc/rfc4632.html) | 5280, 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC4634](https://www.rfc-editor.org/rfc/rfc4634.html) | 5077 | Unclassified citation candidate; applicability and review not established |
| [RFC4637](https://www.rfc-editor.org/rfc/rfc4637.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4642](https://www.rfc-editor.org/rfc/rfc4642.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4645](https://www.rfc-editor.org/rfc/rfc4645.html) | 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC4646](https://www.rfc-editor.org/rfc/rfc4646.html) | 5337, 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC4647](https://www.rfc-editor.org/rfc/rfc4647.html) | 5646, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC4680](https://www.rfc-editor.org/rfc/rfc4680.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4681](https://www.rfc-editor.org/rfc/rfc4681.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4686](https://www.rfc-editor.org/rfc/rfc4686.html) | 5321, 6376, 7489 | Unclassified citation candidate; applicability and review not established |
| [RFC4690](https://www.rfc-editor.org/rfc/rfc4690.html) | 5890, 5891, 5892, 6530, 8753 | Unclassified citation candidate; applicability and review not established |
| [RFC4712](https://www.rfc-editor.org/rfc/rfc4712.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4727](https://www.rfc-editor.org/rfc/rfc4727.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC4731](https://www.rfc-editor.org/rfc/rfc4731.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4732](https://www.rfc-editor.org/rfc/rfc4732.html) | 6376, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4735](https://www.rfc-editor.org/rfc/rfc4735.html) | 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC4743](https://www.rfc-editor.org/rfc/rfc4743.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4744](https://www.rfc-editor.org/rfc/rfc4744.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4752](https://www.rfc-editor.org/rfc/rfc4752.html) | 5034, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4785](https://www.rfc-editor.org/rfc/rfc4785.html) | 8996, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC4790](https://www.rfc-editor.org/rfc/rfc4790.html) | 5228, 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC4791](https://www.rfc-editor.org/rfc/rfc4791.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4823](https://www.rfc-editor.org/rfc/rfc4823.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4851](https://www.rfc-editor.org/rfc/rfc4851.html) | 5077, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4853](https://www.rfc-editor.org/rfc/rfc4853.html) | 5652 | Multiple-signer clarification incorporated into the reviewed CMS base. Selected behavior is recorded in RFC5652; RFC4853 has not been separately reviewed. [Selected source review](cms.md). |
| [RFC4855](https://www.rfc-editor.org/rfc/rfc4855.html) | 6838 | Unclassified citation candidate; applicability and review not established |
| [RFC4870](https://www.rfc-editor.org/rfc/rfc4870.html) | 6376, 8601, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC4871](https://www.rfc-editor.org/rfc/rfc4871.html) | 5321, 6376 | Historical DKIM predecessor: reviewed RFC6376 incorporates RFC5672 terminology/output rules and revises RFC4871 verification, including ignoring the deprecated g= key tag. Compatibility advice remains in the successor; current algorithm updates still apply. This applicability classification does not claim review of the predecessor base text. [Selected source review](dkim.md). |
| [RFC4880](https://www.rfc-editor.org/rfc/rfc4880.html) | 5321, 5598, 6376, 6409, 7208, 8689, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC4918](https://www.rfc-editor.org/rfc/rfc4918.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC4934](https://www.rfc-editor.org/rfc/rfc4934.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4949](https://www.rfc-editor.org/rfc/rfc4949.html) | 6749, 7489, 7672, 8551, 9325, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC4952](https://www.rfc-editor.org/rfc/rfc4952.html) | 5335, 5891, 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC4959](https://www.rfc-editor.org/rfc/rfc4959.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC4964](https://www.rfc-editor.org/rfc/rfc4964.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4975](https://www.rfc-editor.org/rfc/rfc4975.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4976](https://www.rfc-editor.org/rfc/rfc4976.html) | 8553, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC4985](https://www.rfc-editor.org/rfc/rfc4985.html) | 7817, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC4992](https://www.rfc-editor.org/rfc/rfc4992.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5018](https://www.rfc-editor.org/rfc/rfc5018.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5019](https://www.rfc-editor.org/rfc/rfc5019.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5023](https://www.rfc-editor.org/rfc/rfc5023.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5024](https://www.rfc-editor.org/rfc/rfc5024.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5026](https://www.rfc-editor.org/rfc/rfc5026.html) | 8552, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5049](https://www.rfc-editor.org/rfc/rfc5049.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5051](https://www.rfc-editor.org/rfc/rfc5051.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC5054](https://www.rfc-editor.org/rfc/rfc5054.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5068](https://www.rfc-editor.org/rfc/rfc5068.html) | 5598, 8314 | Unclassified citation candidate; applicability and review not established |
| [RFC5081](https://www.rfc-editor.org/rfc/rfc5081.html) | 5246, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5083](https://www.rfc-editor.org/rfc/rfc5083.html) | 8551, 8933, 9629, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC5084](https://www.rfc-editor.org/rfc/rfc5084.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC5091](https://www.rfc-editor.org/rfc/rfc5091.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5092](https://www.rfc-editor.org/rfc/rfc5092.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5101](https://www.rfc-editor.org/rfc/rfc5101.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5158](https://www.rfc-editor.org/rfc/rfc5158.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5161](https://www.rfc-editor.org/rfc/rfc5161.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5182](https://www.rfc-editor.org/rfc/rfc5182.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5183](https://www.rfc-editor.org/rfc/rfc5183.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5191](https://www.rfc-editor.org/rfc/rfc5191.html) | 5869 | Unclassified citation candidate; applicability and review not established |
| [RFC5198](https://www.rfc-editor.org/rfc/rfc5198.html) | 5335, 6530, 6532, 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5216](https://www.rfc-editor.org/rfc/rfc5216.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5226](https://www.rfc-editor.org/rfc/rfc5226.html) | 5248, 5436, 5646, 5892, 6376, 6749, 6838, 7301, 7489, 7636, 8098, 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC5230](https://www.rfc-editor.org/rfc/rfc5230.html) | 5429, 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5231](https://www.rfc-editor.org/rfc/rfc5231.html) | 5229 | Unclassified citation candidate; applicability and review not established |
| [RFC5232](https://www.rfc-editor.org/rfc/rfc5232.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5233](https://www.rfc-editor.org/rfc/rfc5233.html) | 8098 | Subaddressing explains why two notification addresses may not match; it does not authorize stripping tags or treating mailboxes as identical. The selected exact-address comparison follows reviewed RFC8098. The Sieve subaddress extension itself is not selected by this citation; base text unreviewed. [Selected source review](disposition-notifications.md). |
| [RFC5235](https://www.rfc-editor.org/rfc/rfc5235.html) | 5229, 5429, 5598, 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5238](https://www.rfc-editor.org/rfc/rfc5238.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5255](https://www.rfc-editor.org/rfc/rfc5255.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5256](https://www.rfc-editor.org/rfc/rfc5256.html) | 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5258](https://www.rfc-editor.org/rfc/rfc5258.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5263](https://www.rfc-editor.org/rfc/rfc5263.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5281](https://www.rfc-editor.org/rfc/rfc5281.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5288](https://www.rfc-editor.org/rfc/rfc5288.html) | 5289, 9325, 10015 | Selected TLS1.2 AES-GCM nonce, framing and record-protection rules reviewed; not complete base. [Selected source review](selected-crypto.md). |
| [RFC5293](https://www.rfc-editor.org/rfc/rfc5293.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5328](https://www.rfc-editor.org/rfc/rfc5328.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5336](https://www.rfc-editor.org/rfc/rfc5336.html) | 5335, 5337, 5598, 6530, 6531 | Unclassified citation candidate; applicability and review not established |
| [RFC5364](https://www.rfc-editor.org/rfc/rfc5364.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5378](https://www.rfc-editor.org/rfc/rfc5378.html) | 6838, 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC5389](https://www.rfc-editor.org/rfc/rfc5389.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5415](https://www.rfc-editor.org/rfc/rfc5415.html) | 8553, 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5422](https://www.rfc-editor.org/rfc/rfc5422.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5435](https://www.rfc-editor.org/rfc/rfc5435.html) | 5436, 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5448](https://www.rfc-editor.org/rfc/rfc5448.html) | 5869 | Unclassified citation candidate; applicability and review not established |
| [RFC5451](https://www.rfc-editor.org/rfc/rfc5451.html) | 6376, 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC5456](https://www.rfc-editor.org/rfc/rfc5456.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5464](https://www.rfc-editor.org/rfc/rfc5464.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5465](https://www.rfc-editor.org/rfc/rfc5465.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5469](https://www.rfc-editor.org/rfc/rfc5469.html) | 8996, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC5487](https://www.rfc-editor.org/rfc/rfc5487.html) | 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC5490](https://www.rfc-editor.org/rfc/rfc5490.html) | 9042 | Unclassified citation candidate; applicability and review not established |
| [RFC5504](https://www.rfc-editor.org/rfc/rfc5504.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC5507](https://www.rfc-editor.org/rfc/rfc5507.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC5509](https://www.rfc-editor.org/rfc/rfc5509.html) | 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC5518](https://www.rfc-editor.org/rfc/rfc5518.html) | 8552, 8553, 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC5530](https://www.rfc-editor.org/rfc/rfc5530.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5555](https://www.rfc-editor.org/rfc/rfc5555.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5581](https://www.rfc-editor.org/rfc/rfc5581.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC5585](https://www.rfc-editor.org/rfc/rfc5585.html) | 6376, 7489 | Unclassified citation candidate; applicability and review not established |
| [RFC5617](https://www.rfc-editor.org/rfc/rfc5617.html) | 6854, 7489, 8553, 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC5630](https://www.rfc-editor.org/rfc/rfc5630.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC5639](https://www.rfc-editor.org/rfc/rfc5639.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC5645](https://www.rfc-editor.org/rfc/rfc5645.html) | 5646 | Unclassified citation candidate; applicability and review not established |
| [RFC5672](https://www.rfc-editor.org/rfc/rfc5672.html) | 6376 | Historical DKIM predecessor: reviewed RFC6376 incorporates RFC5672 terminology/output rules and revises RFC4871 verification, including ignoring the deprecated g= key tag. Compatibility advice remains in the successor; current algorithm updates still apply. This applicability classification does not claim review of the predecessor base text. [Selected source review](dkim.md). |
| [RFC5679](https://www.rfc-editor.org/rfc/rfc5679.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5703](https://www.rfc-editor.org/rfc/rfc5703.html) | 6785 | Unclassified citation candidate; applicability and review not established |
| [RFC5705](https://www.rfc-editor.org/rfc/rfc5705.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC5721](https://www.rfc-editor.org/rfc/rfc5721.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC5734](https://www.rfc-editor.org/rfc/rfc5734.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5738](https://www.rfc-editor.org/rfc/rfc5738.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC5741](https://www.rfc-editor.org/rfc/rfc5741.html) | 5869, 5890, 5891, 5892, 5893, 6151, 6152, 6186, 6211, 6376, 6409, 6452, 6522, 6530, 6531, 6532, 6533, 6657, 6749, 6750, 6785, 6818, 6838, 6839, 6854, 7208, 7293, 7301, 7372, 7405, 7489, 7504, 7505, 7578, 7636, 7672, 7748, 7817 | Publication-status context, not an email processing requirement. All cited parent occurrences refer to RFC status boilerplate; RFC5741 base text has not been reviewed. [Selected source review](reference-candidates.md). |
| [RFC5742](https://www.rfc-editor.org/rfc/rfc5742.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC5746](https://www.rfc-editor.org/rfc/rfc5746.html) | 9325, 9852 | Selected initial secure-renegotiation acknowledgement and conditional Finished bindings reviewed; renegotiation need not be enabled. [Selected source review](selected-crypto.md). |
| [RFC5750](https://www.rfc-editor.org/rfc/rfc5750.html) | 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC5751](https://www.rfc-editor.org/rfc/rfc5751.html) | 6376, 6409, 6530, 7208, 8550, 8551, 9788 | Conditional historical-message dependency: RFC8551 supersedes S/MIME 3.2 for current S/MIME 4.0 and separately discusses historic-email processing. Legacy protected-mail reception may require version-specific behavior; RFC5751 is not dismissed merely because superseded, nor does it authorize old algorithms for new messages. That compatibility review remains open. This applicability classification does not claim review of the predecessor base text. [Selected source review](smime-message.md). |
| [RFC5753](https://www.rfc-editor.org/rfc/rfc5753.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC5754](https://www.rfc-editor.org/rfc/rfc5754.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC5755](https://www.rfc-editor.org/rfc/rfc5755.html) | 8550 | Conditional dependency for recommended S/MIME v2 attribute-certificate handling. It is not an Email Next principal-authority mechanism; exact syntax/validation review remains pending before claiming that compatibility capability. [Selected source review](smime-certificates.md). |
| [RFC5756](https://www.rfc-editor.org/rfc/rfc5756.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC5758](https://www.rfc-editor.org/rfc/rfc5758.html) | 8550 | Unclassified citation candidate; applicability and review not established |
| [RFC5763](https://www.rfc-editor.org/rfc/rfc5763.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC5764](https://www.rfc-editor.org/rfc/rfc5764.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC5766](https://www.rfc-editor.org/rfc/rfc5766.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5771](https://www.rfc-editor.org/rfc/rfc5771.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC5780](https://www.rfc-editor.org/rfc/rfc5780.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5782](https://www.rfc-editor.org/rfc/rfc5782.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC5785](https://www.rfc-editor.org/rfc/rfc5785.html) | 8461 | Unclassified citation candidate; applicability and review not established |
| [RFC5788](https://www.rfc-editor.org/rfc/rfc5788.html) | 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5789](https://www.rfc-editor.org/rfc/rfc5789.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC5795](https://www.rfc-editor.org/rfc/rfc5795.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC5804](https://www.rfc-editor.org/rfc/rfc5804.html) | 6785, 7817, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5819](https://www.rfc-editor.org/rfc/rfc5819.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC5825](https://www.rfc-editor.org/rfc/rfc5825.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC5849](https://www.rfc-editor.org/rfc/rfc5849.html) | 6749 | Unclassified citation candidate; applicability and review not established |
| [RFC5863](https://www.rfc-editor.org/rfc/rfc5863.html) | 6376, 6530, 7489 | Unclassified citation candidate; applicability and review not established |
| [RFC5864](https://www.rfc-editor.org/rfc/rfc5864.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5878](https://www.rfc-editor.org/rfc/rfc5878.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5894](https://www.rfc-editor.org/rfc/rfc5894.html) | 5890, 5891, 5892, 6530, 8753, 9233, 9549 | Unclassified citation candidate; applicability and review not established |
| [RFC5895](https://www.rfc-editor.org/rfc/rfc5895.html) | 9233 | Unclassified citation candidate; applicability and review not established |
| [RFC5905](https://www.rfc-editor.org/rfc/rfc5905.html) | 7293, 9110, 9420 | Unclassified citation candidate; applicability and review not established |
| [RFC5911](https://www.rfc-editor.org/rfc/rfc5911.html) | 9629 | Unclassified citation candidate; applicability and review not established |
| [RFC5912](https://www.rfc-editor.org/rfc/rfc5912.html) | 6211, 9598, 9608, 9629, 9925 | Selected certificate ASN.1 modules and algorithm declarations are required syntax dependencies. The scoped review covers selected modules, object/table semantics and all ten current errata dispositions; it does not cover every module or establish backend compliance. [Selected source review](rsa-certificate-signatures.md). |
| [RFC5914](https://www.rfc-editor.org/rfc/rfc5914.html) | 6818, 9925 | Unclassified citation candidate; applicability and review not established |
| [RFC5922](https://www.rfc-editor.org/rfc/rfc5922.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC5928](https://www.rfc-editor.org/rfc/rfc5928.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC5929](https://www.rfc-editor.org/rfc/rfc5929.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC5932](https://www.rfc-editor.org/rfc/rfc5932.html) | 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC5937](https://www.rfc-editor.org/rfc/rfc5937.html) | 6818 | Unclassified citation candidate; applicability and review not established |
| [RFC5952](https://www.rfc-editor.org/rfc/rfc5952.html) | 8460 | Unclassified citation candidate; applicability and review not established |
| [RFC5953](https://www.rfc-editor.org/rfc/rfc5953.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC5954](https://www.rfc-editor.org/rfc/rfc5954.html) | 8460 | Unclassified citation candidate; applicability and review not established |
| [RFC5965](https://www.rfc-editor.org/rfc/rfc5965.html) | 7489, 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC5982](https://www.rfc-editor.org/rfc/rfc5982.html) | 8753 | Unclassified citation candidate; applicability and review not established |
| [RFC5983](https://www.rfc-editor.org/rfc/rfc5983.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC5987](https://www.rfc-editor.org/rfc/rfc5987.html) | 6838, 7578 | These parent citations do not select extended HTTP parameter encoding: RFC7578 forbids filename* for form-data and RFC6838 uses it as a transport comparison. Any independently selected HTTP header feature would require a separate applicability decision and current-source review; RFC5987 is not marked reviewed. [Selected source review](form-data.md). |
| [RFC6008](https://www.rfc-editor.org/rfc/rfc6008.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC6012](https://www.rfc-editor.org/rfc/rfc6012.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6014](https://www.rfc-editor.org/rfc/rfc6014.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC6042](https://www.rfc-editor.org/rfc/rfc6042.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6055](https://www.rfc-editor.org/rfc/rfc6055.html) | 6530 | Unclassified citation candidate; applicability and review not established |
| [RFC6066](https://www.rfc-editor.org/rfc/rfc6066.html) | 6186, 7672, 7817, 8314, 8461, 9325, 9525, 9846 | Selected SNI and security rules reviewed in audits/tls-service-negotiation.md; full extension suite not reviewed |
| [RFC6068](https://www.rfc-editor.org/rfc/rfc6068.html) | 6530, 8460 | Unclassified citation candidate; applicability and review not established |
| [RFC6083](https://www.rfc-editor.org/rfc/rfc6083.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6084](https://www.rfc-editor.org/rfc/rfc6084.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6090](https://www.rfc-editor.org/rfc/rfc6090.html) | 7748, 8550, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC6091](https://www.rfc-editor.org/rfc/rfc6091.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6101](https://www.rfc-editor.org/rfc/rfc6101.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6117](https://www.rfc-editor.org/rfc/rfc6117.html) | 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC6118](https://www.rfc-editor.org/rfc/rfc6118.html) | 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC6120](https://www.rfc-editor.org/rfc/rfc6120.html) | 8553, 9325, 9525, 9750 | Unclassified citation candidate; applicability and review not established |
| [RFC6125](https://www.rfc-editor.org/rfc/rfc6125.html) | 6186, 6749, 7672, 7817, 8314, 8461, 8689, 9110, 9325, 9420, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC6154](https://www.rfc-editor.org/rfc/rfc6154.html) | 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC6176](https://www.rfc-editor.org/rfc/rfc6176.html) | 8996, 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6194](https://www.rfc-editor.org/rfc/rfc6194.html) | 8301, 8550, 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC6209](https://www.rfc-editor.org/rfc/rfc6209.html) | 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC6210](https://www.rfc-editor.org/rfc/rfc6210.html) | 6211, 8933 | Unclassified citation candidate; applicability and review not established |
| [RFC6212](https://www.rfc-editor.org/rfc/rfc6212.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC6230](https://www.rfc-editor.org/rfc/rfc6230.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC6234](https://www.rfc-editor.org/rfc/rfc6234.html) | 7636, 8032, 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC6265](https://www.rfc-editor.org/rfc/rfc6265.html) | 6750, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC6268](https://www.rfc-editor.org/rfc/rfc6268.html) | 8551, 9608, 9629 | Unclassified citation candidate; applicability and review not established |
| [RFC6275](https://www.rfc-editor.org/rfc/rfc6275.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC6278](https://www.rfc-editor.org/rfc/rfc6278.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC6335](https://www.rfc-editor.org/rfc/rfc6335.html) | 8314, 8552, 8553, 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC6347](https://www.rfc-editor.org/rfc/rfc6347.html) | 8996, 9325, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC6353](https://www.rfc-editor.org/rfc/rfc6353.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6365](https://www.rfc-editor.org/rfc/rfc6365.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC6367](https://www.rfc-editor.org/rfc/rfc6367.html) | 8996, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC6377](https://www.rfc-editor.org/rfc/rfc6377.html) | 6376, 7489, 8617, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC6454](https://www.rfc-editor.org/rfc/rfc6454.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC6460](https://www.rfc-editor.org/rfc/rfc6460.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6520](https://www.rfc-editor.org/rfc/rfc6520.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6541](https://www.rfc-editor.org/rfc/rfc6541.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC6570](https://www.rfc-editor.org/rfc/rfc6570.html) | 8620, 8820 | Unclassified citation candidate; applicability and review not established |
| [RFC6577](https://www.rfc-editor.org/rfc/rfc6577.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC6585](https://www.rfc-editor.org/rfc/rfc6585.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC6590](https://www.rfc-editor.org/rfc/rfc6590.html) | 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC6591](https://www.rfc-editor.org/rfc/rfc6591.html) | 7489, 9989, 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC6614](https://www.rfc-editor.org/rfc/rfc6614.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6637](https://www.rfc-editor.org/rfc/rfc6637.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC6647](https://www.rfc-editor.org/rfc/rfc6647.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC6648](https://www.rfc-editor.org/rfc/rfc6648.html) | 6838, 7208, 8098, 9051, 9110, 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC6651](https://www.rfc-editor.org/rfc/rfc6651.html) | 7489, 9989, 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC6652](https://www.rfc-editor.org/rfc/rfc6652.html) | 7208, 7489, 9989, 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC6655](https://www.rfc-editor.org/rfc/rfc6655.html) | 9846, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC6672](https://www.rfc-editor.org/rfc/rfc6672.html) | 7672 | Unclassified citation candidate; applicability and review not established |
| [RFC6686](https://www.rfc-editor.org/rfc/rfc6686.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC6692](https://www.rfc-editor.org/rfc/rfc6692.html) | 9991 | Unclassified citation candidate; applicability and review not established |
| [RFC6698](https://www.rfc-editor.org/rfc/rfc6698.html) | 7672, 7817, 8126, 8314, 8460, 8552, 9325, 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC6709](https://www.rfc-editor.org/rfc/rfc6709.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC6710](https://www.rfc-editor.org/rfc/rfc6710.html) | 8621 | Unclassified citation candidate; applicability and review not established |
| [RFC6713](https://www.rfc-editor.org/rfc/rfc6713.html) | 7489, 8460, 9990 | Unclassified citation candidate; applicability and review not established |
| [RFC6739](https://www.rfc-editor.org/rfc/rfc6739.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC6763](https://www.rfc-editor.org/rfc/rfc6763.html) | 8552, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC6764](https://www.rfc-editor.org/rfc/rfc6764.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC6797](https://www.rfc-editor.org/rfc/rfc6797.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC6819](https://www.rfc-editor.org/rfc/rfc6819.html) | 7636, 8252, 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC6851](https://www.rfc-editor.org/rfc/rfc6851.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC6855](https://www.rfc-editor.org/rfc/rfc6855.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC6891](https://www.rfc-editor.org/rfc/rfc6891.html) | 7208 | Unclassified citation candidate; applicability and review not established |
| [RFC6895](https://www.rfc-editor.org/rfc/rfc6895.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC6901](https://www.rfc-editor.org/rfc/rfc6901.html) | 8620, 8820 | Unclassified citation candidate; applicability and review not established |
| [RFC6912](https://www.rfc-editor.org/rfc/rfc6912.html) | 9233 | Unclassified citation candidate; applicability and review not established |
| [RFC6943](https://www.rfc-editor.org/rfc/rfc6943.html) | 8820 | Unclassified citation candidate; applicability and review not established |
| [RFC6960](https://www.rfc-editor.org/rfc/rfc6960.html) | 8461, 9325, 9608, 9846 | Selected OCSP response/status/signature/time rules and reached current ASN.1 imports are mapped in the certificate-status owner; exact source coverage and runtime limits remain separate. [Selected source review](certificate-status.md). |
| [RFC6961](https://www.rfc-editor.org/rfc/rfc6961.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6962](https://www.rfc-editor.org/rfc/rfc6962.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6979](https://www.rfc-editor.org/rfc/rfc6979.html) | 8550, 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC6994](https://www.rfc-editor.org/rfc/rfc6994.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC7001](https://www.rfc-editor.org/rfc/rfc7001.html) | 7208, 7293, 7372, 7489, 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC7030](https://www.rfc-editor.org/rfc/rfc7030.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC7114](https://www.rfc-editor.org/rfc/rfc7114.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC7120](https://www.rfc-editor.org/rfc/rfc7120.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC7159](https://www.rfc-editor.org/rfc/rfc7159.html) | 8259 | Historical predecessor, superseded by RFC8259. JSON encoding follows RFC8259 and the selected application constraints; earlier encoding guidance does not authorize alternate network encodings. This classification does not claim a review of the predecessor text. [Selected source review](json-encoding.md). |
| [RFC7162](https://www.rfc-editor.org/rfc/rfc7162.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC7218](https://www.rfc-editor.org/rfc/rfc7218.html) | 7672 | Unclassified citation candidate; applicability and review not established |
| [RFC7228](https://www.rfc-editor.org/rfc/rfc7228.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7230](https://www.rfc-editor.org/rfc/rfc7230.html) | 7301, 8058, 8252, 8620, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7231](https://www.rfc-editor.org/rfc/rfc7231.html) | 8460, 8620, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7232](https://www.rfc-editor.org/rfc/rfc7232.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7233](https://www.rfc-editor.org/rfc/rfc7233.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7234](https://www.rfc-editor.org/rfc/rfc7234.html) | 8461, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7235](https://www.rfc-editor.org/rfc/rfc7235.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7250](https://www.rfc-editor.org/rfc/rfc7250.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC7253](https://www.rfc-editor.org/rfc/rfc7253.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC7281](https://www.rfc-editor.org/rfc/rfc7281.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC7292](https://www.rfc-editor.org/rfc/rfc7292.html) | 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC7299](https://www.rfc-editor.org/rfc/rfc7299.html) | 9925 | Unclassified citation candidate; applicability and review not established |
| [RFC7320](https://www.rfc-editor.org/rfc/rfc7320.html) | 8820 | Unclassified citation candidate; applicability and review not established |
| [RFC7366](https://www.rfc-editor.org/rfc/rfc7366.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7410](https://www.rfc-editor.org/rfc/rfc7410.html) | 8601 | Unclassified citation candidate; applicability and review not established |
| [RFC7435](https://www.rfc-editor.org/rfc/rfc7435.html) | 7672, 8460, 9325, 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC7457](https://www.rfc-editor.org/rfc/rfc7457.html) | 8996, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7465](https://www.rfc-editor.org/rfc/rfc7465.html) | 8996, 9325, 9846, 9852 | Unclassified citation candidate; applicability and review not established |
| [RFC7469](https://www.rfc-editor.org/rfc/rfc7469.html) | 8314, 8460 | Unclassified citation candidate; applicability and review not established |
| [RFC7493](https://www.rfc-editor.org/rfc/rfc7493.html) | 8460, 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC7507](https://www.rfc-editor.org/rfc/rfc7507.html) | 8996, 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC7519](https://www.rfc-editor.org/rfc/rfc7519.html) | 9207 | Unclassified citation candidate; applicability and review not established |
| [RFC7521](https://www.rfc-editor.org/rfc/rfc7521.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC7523](https://www.rfc-editor.org/rfc/rfc7523.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC7525](https://www.rfc-editor.org/rfc/rfc7525.html) | 7636, 8314, 8461, 8620, 8689, 8996, 9051, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7538](https://www.rfc-editor.org/rfc/rfc7538.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7540](https://www.rfc-editor.org/rfc/rfc7540.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7541](https://www.rfc-editor.org/rfc/rfc7541.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7553](https://www.rfc-editor.org/rfc/rfc7553.html) | 8552, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC7562](https://www.rfc-editor.org/rfc/rfc7562.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC7564](https://www.rfc-editor.org/rfc/rfc7564.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC7566](https://www.rfc-editor.org/rfc/rfc7566.html) | 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC7568](https://www.rfc-editor.org/rfc/rfc7568.html) | 8996, 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC7590](https://www.rfc-editor.org/rfc/rfc7590.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7591](https://www.rfc-editor.org/rfc/rfc7591.html) | 8252, 9207, 9700 | Selected native public registration metadata, success/error and security rules reviewed. No JWT/software-statement or registration-management path; selected ranges only. [Selected source review](oauth-provider-discovery.md). |
| [RFC7595](https://www.rfc-editor.org/rfc/rfc7595.html) | 8126, 8252, 8820, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7601](https://www.rfc-editor.org/rfc/rfc7601.html) | 8601 | Historical Authentication-Results predecessor: reviewed RFC8601 supplies current grammar, trust-boundary handling, EAI guidance and revised property registrations. Earlier local authentication results do not acquire endpoint-authority status. This applicability classification does not claim review of the predecessor base text. [Selected source review](authentication-results.md). |
| [RFC7615](https://www.rfc-editor.org/rfc/rfc7615.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7616](https://www.rfc-editor.org/rfc/rfc7616.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7617](https://www.rfc-editor.org/rfc/rfc7617.html) | 8620, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7624](https://www.rfc-editor.org/rfc/rfc7624.html) | 9846, 9990 | Unclassified citation candidate; applicability and review not established |
| [RFC7627](https://www.rfc-editor.org/rfc/rfc7627.html) | 9325, 9846 | Selected full and resumed extended-master-secret rules reviewed; no legacy no-EMS fallback. [Selected source review](selected-crypto.md). |
| [RFC7633](https://www.rfc-editor.org/rfc/rfc7633.html) | 9325 | TLS Feature enforcement is required for service certificates declaring required stapling. The selected review covers the declaration and enforcement rules; required-staple sessions use full handshakes. This is not a full base-text or backend-conformance claim. [Selected source review](certificate-status.md). |
| [RFC7671](https://www.rfc-editor.org/rfc/rfc7671.html) | 7672, 8460, 8552 | Unclassified citation candidate; applicability and review not established |
| [RFC7673](https://www.rfc-editor.org/rfc/rfc7673.html) | 7672, 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7677](https://www.rfc-editor.org/rfc/rfc7677.html) | 8621, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC7685](https://www.rfc-editor.org/rfc/rfc7685.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC7694](https://www.rfc-editor.org/rfc/rfc7694.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7696](https://www.rfc-editor.org/rfc/rfc7696.html) | 9420 | Algorithm-agility design rationale. The selected MLS suite/version behavior comes from RFC9420 and the application profile; this citation does not import an additional wire algorithm or negotiation mechanism. RFC7696 base text has not been reviewed. [Selected source review](mls.md). |
| [RFC7711](https://www.rfc-editor.org/rfc/rfc7711.html) | 7817 | Unclassified citation candidate; applicability and review not established |
| [RFC7712](https://www.rfc-editor.org/rfc/rfc7712.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7752](https://www.rfc-editor.org/rfc/rfc7752.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC7807](https://www.rfc-editor.org/rfc/rfc7807.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC7838](https://www.rfc-editor.org/rfc/rfc7838.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC7841](https://www.rfc-editor.org/rfc/rfc7841.html) | 8032, 8058, 8098, 8126, 8174, 8252, 8259, 8301, 8314, 8460, 8461, 8463, 8550, 8551, 8552, 8553, 8601, 8616, 8617, 8620, 8621, 8689, 8753, 8820, 8933, 8996, 8997, 9042, 9051, 9078, 9110, 9180, 9207, 9233, 9325, 9404, 9420, 9525, 9549, 9580, 9598, 9608, 9618, 9629, 9670, 9694, 9700, 9750, 9787, 9788, 9846, 9852, 9925, 9963, 9989, 9990, 9991, 10007, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC7858](https://www.rfc-editor.org/rfc/rfc7858.html) | 9525, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC7888](https://www.rfc-editor.org/rfc/rfc7888.html) | 9051, 9404 | Unclassified citation candidate; applicability and review not established |
| [RFC7905](https://www.rfc-editor.org/rfc/rfc7905.html) | 8551, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC7919](https://www.rfc-editor.org/rfc/rfc7919.html) | 9325, 9846, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC7924](https://www.rfc-editor.org/rfc/rfc7924.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC7925](https://www.rfc-editor.org/rfc/rfc7925.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC7929](https://www.rfc-editor.org/rfc/rfc7929.html) | 8552, 9787, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC7960](https://www.rfc-editor.org/rfc/rfc7960.html) | 8617, 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC8017](https://www.rfc-editor.org/rfc/rfc8017.html) | 8301, 8463, 8933, 9180, 9580, 9846, 9963 | Required narrow HPKE dependency: sections4–4.2 integer/octet conversions and six captured errata reviewed. This does not select RSA for MLS. Full base review, live errata freshness and other citing profiles remain open. [Selected source review](hpke.md). |
| [RFC8018](https://www.rfc-editor.org/rfc/rfc8018.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC8020](https://www.rfc-editor.org/rfc/rfc8020.html) | 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC8030](https://www.rfc-editor.org/rfc/rfc8030.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC8081](https://www.rfc-editor.org/rfc/rfc8081.html) | 9051, 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC8141](https://www.rfc-editor.org/rfc/rfc8141.html) | 8126 | Unclassified citation candidate; applicability and review not established |
| [RFC8143](https://www.rfc-editor.org/rfc/rfc8143.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC8145](https://www.rfc-editor.org/rfc/rfc8145.html) | 8552, 8553 | Unclassified citation candidate; applicability and review not established |
| [RFC8162](https://www.rfc-editor.org/rfc/rfc8162.html) | 8550, 8552, 9787, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC8187](https://www.rfc-editor.org/rfc/rfc8187.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC8246](https://www.rfc-editor.org/rfc/rfc8246.html) | 8620, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC8261](https://www.rfc-editor.org/rfc/rfc8261.html) | 8996 | Unclassified citation candidate; applicability and review not established |
| [RFC8264](https://www.rfc-editor.org/rfc/rfc8264.html) | 8620, 9670 | Unclassified citation candidate; applicability and review not established |
| [RFC8288](https://www.rfc-editor.org/rfc/rfc8288.html) | 8820, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC8291](https://www.rfc-editor.org/rfc/rfc8291.html) | 8620 | Unclassified citation candidate; applicability and review not established |
| [RFC8305](https://www.rfc-editor.org/rfc/rfc8305.html) | 9051, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8310](https://www.rfc-editor.org/rfc/rfc8310.html) | 9852 | Unclassified citation candidate; applicability and review not established |
| [RFC8336](https://www.rfc-editor.org/rfc/rfc8336.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC8398](https://www.rfc-editor.org/rfc/rfc8398.html) | 8550, 9549, 9598 | Unclassified citation candidate; applicability and review not established |
| [RFC8399](https://www.rfc-editor.org/rfc/rfc8399.html) | 9549 | Unclassified citation candidate; applicability and review not established |
| [RFC8410](https://www.rfc-editor.org/rfc/rfc8410.html) | 8550 | Unclassified citation candidate; applicability and review not established |
| [RFC8414](https://www.rfc-editor.org/rfc/rfc8414.html) | 9207, 9700 | Selected public-provider metadata rules; independent endpoint authentication declarations, issuer equality and exact scope/endpoint binding reviewed. Selected ranges only; no complete base review. [Selected source review](oauth-provider-discovery.md). |
| [RFC8418](https://www.rfc-editor.org/rfc/rfc8418.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC8419](https://www.rfc-editor.org/rfc/rfc8419.html) | 8551 | Unclassified citation candidate; applicability and review not established |
| [RFC8422](https://www.rfc-editor.org/rfc/rfc8422.html) | 8996, 9325, 9846, 10015 | Selected authenticated ECDHE, point validation and fixed-width shared-secret rules reviewed; unselected static and DTLS branches remain separate. [Selected source review](selected-crypto.md). |
| [RFC8438](https://www.rfc-editor.org/rfc/rfc8438.html) | 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC8439](https://www.rfc-editor.org/rfc/rfc8439.html) | 9180, 9846 | Selected ChaCha20-Poly1305 primitive/AEAD/security rules and all captured errata reviewed for age and TLS1.3; not complete base or all vectors. [Selected source review](selected-crypto.md). |
| [RFC8446](https://www.rfc-editor.org/rfc/rfc8446.html) | 8461, 8620, 8996, 8997, 9051, 9110, 9180, 9325, 9420, 9525, 9618, 9750, 9846, 9925, 9963 | Historical TLS 1.3 predecessor: the selected current protocol follows reviewed RFC9846, which obsoletes RFC8446 while preserving wire compatibility. Its explicit compatibility requirements remain applicable; this classification does not claim a complete independent RFC8446 review. [Selected source review](tls13.md). |
| [RFC8447](https://www.rfc-editor.org/rfc/rfc8447.html) | 8996, 9846 | Selected ALPN registry name and alert120 update reviewed in audits/tls-service-negotiation.md; other registries and9847dependency separate |
| [RFC8448](https://www.rfc-editor.org/rfc/rfc8448.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8449](https://www.rfc-editor.org/rfc/rfc8449.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8452](https://www.rfc-editor.org/rfc/rfc8452.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC8457](https://www.rfc-editor.org/rfc/rfc8457.html) | 8621 | Unclassified citation candidate; applicability and review not established |
| [RFC8467](https://www.rfc-editor.org/rfc/rfc8467.html) | 9180 | Unclassified citation candidate; applicability and review not established |
| [RFC8470](https://www.rfc-editor.org/rfc/rfc8470.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8474](https://www.rfc-editor.org/rfc/rfc8474.html) | 8621, 9042, 9051 | Unclassified citation candidate; applicability and review not established |
| [RFC8484](https://www.rfc-editor.org/rfc/rfc8484.html) | 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC8555](https://www.rfc-editor.org/rfc/rfc8555.html) | 8552, 9525, 9608 | Unclassified citation candidate; applicability and review not established |
| [RFC8579](https://www.rfc-editor.org/rfc/rfc8579.html) | 9042 | Unclassified citation candidate; applicability and review not established |
| [RFC8580](https://www.rfc-editor.org/rfc/rfc8580.html) | 9042 | Unclassified citation candidate; applicability and review not established |
| [RFC8615](https://www.rfc-editor.org/rfc/rfc8615.html) | 8620, 8820, 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC8696](https://www.rfc-editor.org/rfc/rfc8696.html) | 9180 | Unclassified citation candidate; applicability and review not established |
| [RFC8701](https://www.rfc-editor.org/rfc/rfc8701.html) | 9420, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8705](https://www.rfc-editor.org/rfc/rfc8705.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC8707](https://www.rfc-editor.org/rfc/rfc8707.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC8773](https://www.rfc-editor.org/rfc/rfc8773.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8823](https://www.rfc-editor.org/rfc/rfc8823.html) | 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC8844](https://www.rfc-editor.org/rfc/rfc8844.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8870](https://www.rfc-editor.org/rfc/rfc8870.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8879](https://www.rfc-editor.org/rfc/rfc8879.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8915](https://www.rfc-editor.org/rfc/rfc8915.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC8937](https://www.rfc-editor.org/rfc/rfc8937.html) | 9180, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC8941](https://www.rfc-editor.org/rfc/rfc8941.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC9000](https://www.rfc-editor.org/rfc/rfc9000.html) | 9325, 9420, 9525, 9750 | Unclassified citation candidate; applicability and review not established |
| [RFC9001](https://www.rfc-editor.org/rfc/rfc9001.html) | 9325, 9420, 9525, 9846, 9852 | Unclassified citation candidate; applicability and review not established |
| [RFC9007](https://www.rfc-editor.org/rfc/rfc9007.html) | 9404 | Unclassified citation candidate; applicability and review not established |
| [RFC9068](https://www.rfc-editor.org/rfc/rfc9068.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9091](https://www.rfc-editor.org/rfc/rfc9091.html) | 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC9101](https://www.rfc-editor.org/rfc/rfc9101.html) | 9207, 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9106](https://www.rfc-editor.org/rfc/rfc9106.html) | 9580 | Unclassified citation candidate; applicability and review not established |
| [RFC9111](https://www.rfc-editor.org/rfc/rfc9111.html) | 9110 | Selected framing/connection and cache handling reviewed in audits/http-framing.md; full base review and general HTTP/cache conformance not claimed |
| [RFC9112](https://www.rfc-editor.org/rfc/rfc9112.html) | 9110, 9325, 9846 | Selected framing/connection and cache handling reviewed in audits/http-framing.md; full base review and general HTTP/cache conformance not claimed |
| [RFC9113](https://www.rfc-editor.org/rfc/rfc9113.html) | 9110, 9325, 9420 | Unclassified citation candidate; applicability and review not established |
| [RFC9114](https://www.rfc-editor.org/rfc/rfc9114.html) | 9110 | Unclassified citation candidate; applicability and review not established |
| [RFC9126](https://www.rfc-editor.org/rfc/rfc9126.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9147](https://www.rfc-editor.org/rfc/rfc9147.html) | 9325, 9525, 9846, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC9149](https://www.rfc-editor.org/rfc/rfc9149.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9155](https://www.rfc-editor.org/rfc/rfc9155.html) | 9325 | Selected TLS1.2 signature-algorithm restrictions reviewed; no MD5/SHA1 handshake fallback. [Selected source review](selected-crypto.md). |
| [RFC9162](https://www.rfc-editor.org/rfc/rfc9162.html) | 9325, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9191](https://www.rfc-editor.org/rfc/rfc9191.html) | 9325 | Unclassified citation candidate; applicability and review not established |
| [RFC9216](https://www.rfc-editor.org/rfc/rfc9216.html) | 9787, 9788 | Unclassified citation candidate; applicability and review not established |
| [RFC9219](https://www.rfc-editor.org/rfc/rfc9219.html) | 9787 | Unclassified citation candidate; applicability and review not established |
| [RFC9257](https://www.rfc-editor.org/rfc/rfc9257.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9258](https://www.rfc-editor.org/rfc/rfc9258.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9261](https://www.rfc-editor.org/rfc/rfc9261.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9345](https://www.rfc-editor.org/rfc/rfc9345.html) | 9525, 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9364](https://www.rfc-editor.org/rfc/rfc9364.html) | 9989 | Unclassified citation candidate; applicability and review not established |
| [RFC9396](https://www.rfc-editor.org/rfc/rfc9396.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9440](https://www.rfc-editor.org/rfc/rfc9440.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9449](https://www.rfc-editor.org/rfc/rfc9449.html) | 9700 | Unclassified citation candidate; applicability and review not established |
| [RFC9460](https://www.rfc-editor.org/rfc/rfc9460.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC9461](https://www.rfc-editor.org/rfc/rfc9461.html) | 9525 | Unclassified citation candidate; applicability and review not established |
| [RFC9562](https://www.rfc-editor.org/rfc/rfc9562.html) | 9990 | Unclassified citation candidate; applicability and review not established |
| [RFC9695](https://www.rfc-editor.org/rfc/rfc9695.html) | 9694 | Unclassified citation candidate; applicability and review not established |
| [RFC9847](https://www.rfc-editor.org/rfc/rfc9847.html) | 9846, 10015 | Unclassified citation candidate; applicability and review not established |
| [RFC9849](https://www.rfc-editor.org/rfc/rfc9849.html) | 9846 | Unclassified citation candidate; applicability and review not established |
| [RFC9851](https://www.rfc-editor.org/rfc/rfc9851.html) | 9852 | Unclassified citation candidate; applicability and review not established |
| [RFC9954](https://www.rfc-editor.org/rfc/rfc9954.html) | 9963 | Unclassified citation candidate; applicability and review not established |
| [RFC9958](https://www.rfc-editor.org/rfc/rfc9958.html) | 9852 | Unclassified citation candidate; applicability and review not established |
| Literal RFC53322 | 9989 | Source-token anomaly in RFC9989: RFC53322.From. No RFC53322 dependency inferred; related message-format requirements remain governed by RFC5322. |
