---
title: MIME parameters audit
sectionNav: true
---

# MIME parameters audit

RFC2231 lets attachment labels carry non-ASCII text and language information without abusing encoded words. Its continuation rules require reconstruction by numbered sections, not by header order.

**Coverage:** full ten-page RFC2231 and all seven retrieved errata read and individually assessed on 19 October 2026. Content-Disposition, current IMAP and internationalized-header behavior remain separate audit dependencies.

Sources: [RFC2231](https://www.rfc-editor.org/rfc/rfc2231.html), [errata](https://www.rfc-editor.org/errata/rfc2231).

| Section | Disposition |
| --- | --- |
| 1 | Scope: parameter continuations, charset/language and encoded-word language extension; all reviewed. |
| 2 | Inherit separate parameter mechanism rather than encoded-word substitution; language aids accessible display, not identity. |
| 2.1 | Requirement vocabulary reviewed. |
| 3 | Inherit zero-based contiguous decimal sections without leading zeroes; concatenate in numeric order independent of header order after parameter syntax unquoting. Mixed quoted and unquoted sections allowed. |
| 4 | Inherit extended name marker, charset/language apostrophe delimiters and percent-encoded octets. Empty labels are permitted but must not imply parameter-defined defaults. The claim that percent encoding agrees with RFC2047 is misleading: Q uses equals, not percent. |
| 4.1 | Inherit mixed encoded/unencoded segments, initial-only charset/language and required delimiters for encoded initial segment. Apply verified590 separators in example. |
| 5 | Inherit charset*language extension to encoded words; encoding selector remains required under verified478. |
| 6 | IMAP SHOULD reconstruct parameter continuations in BODY/BODYSTRUCTURE; current IMAP audit must account for already reconstructed values. |
| 7 | Apply verified477,478,7326 grammar corrections. Preserve regular continuations despite unverified5701. Attribute matching remains case-insensitive; extended segment markers determine decoding. |
| 8 | Historical preference for future inline language labeling reviewed; does not mandate an unselected future encoding. |
| 9 | Source reports no new security issues; profile adds explicit ambiguity and filename handling rather than treating absence of discussion as assurance. |
| 10 | Dependencies reviewed; current language-tag registry, charset and IMAP versions require separate reconciliation. |
| 11 | Contact information reviewed; no protocol behavior. |
| 12 | Copyright statement reviewed; no protocol behavior. |

## Errata

| Record | Status | Disposition |
| --- | --- | --- |
| [476](https://www.rfc-editor.org/errata/eid476) | Verified | Article correction; no decoding change. |
| [477](https://www.rfc-editor.org/errata/eid477) | Verified | Use defined extended-initial-value production. |
| [478](https://www.rfc-editor.org/errata/eid478) | Verified | Restore encoding selector and separator in encoded-word grammar. |
| [590](https://www.rfc-editor.org/errata/eid590) | Verified | Restore semicolons between example parameters. |
| [3269](https://www.rfc-editor.org/errata/eid3269) | Held | Compatibility concern for continued boundary/charset. New-profile generators explicitly keep these ordinary and unsplit; this is a proposed profile restriction. |
| [5701](https://www.rfc-editor.org/errata/eid5701) | Reported | Do not adopt removal of regular continuation syntax: §3 expressly defines unencoded continuations. |
| [7326](https://www.rfc-editor.org/errata/eid7326) | Verified | Remove unmatched parenthesis in other-sections production. |

## Proposed handling

Parse and unquote parameters first. Collect continuation sections by case-insensitive attribute name and numeric index. Reject gaps, duplicate indices and illegal leading zeroes for authoritative interpretation. Decode percent escapes only in starred segments, exactly once; concatenate octets before interpreting the declared charset. Charset/language declarations belong only to the initial encoded segment. Do not interpret an unstarred segment's literal percent sign as an escape.

Conflicting regular, extended or continued forms do not silently select a security-relevant value. For an ambiguous filename, show a neutral attachment label and retain the raw metadata for inspection. Filenames never choose a path or executable handler. Exact precedence for benign redundant labels remains a profile decision; the base source does not supply a universal first-wins rule.

New-profile generators keep boundary and charset parameters ordinary and unsplit, use UTF-8 for non-ASCII human labels with explicit charset, and avoid duplicate parameter forms. UTF-8 generation is an editorial profile choice, not a claim that RFC2231 requires it. A reader can safely display legacy charsets without changing the authenticated original.

Acceptance cases: reversed section order, an unstarred literal percent escape, a starred encoded percent requiring only one decode, a multibyte value split between complete encoded octets across segments, a missing index, duplicate index, leading-zero index, mixed quoted/unquoted segments, conflicting filename forms, and IMAP metadata already reconstructed by a server. No implementation pass is claimed.


## Historical source closure

The superseded [RFC2184 review](mime-parameter-history.md) records its three verified errata and remaining transcription inconsistencies. RFC2184's erroneous one-based continuation example and omitted encoded-word encoding field are not alternate Email Next wire formats. Current generation and validation follow RFC2231; any legacy display recovery must preserve ambiguity rather than authorize an operation from guessed metadata.
