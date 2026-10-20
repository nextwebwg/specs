---
title: HTML aggregation audit
sectionNav: true
---

# HTML aggregation audit

MHTML already supports complete HTML documents bundled with their resources. Its origin and cache warnings remain directly relevant to Email Next. The new rendering profile must state its restrictions separately from inherited compatibility behavior.

**Coverage:** all 28 pages of RFC2557, including all examples and closing material, and all 11 retrieved errata read and individually assessed on 19 October 2026. Dependencies and later HTML/URL rules remain separate audit work.

Sources: [RFC2557](https://www.rfc-editor.org/rfc/rfc2557.html), [errata](https://www.rfc-editor.org/errata/rfc2557).

| Section | Disposition |
| --- | --- |
| 1 | Inherit aggregation purpose and source-preserving references. Rewriting imported HTML can invalidate integrity evidence; original and derived display remain distinct. |
| 2 | Terminology reviewed; source conformance and proposed profile conformance remain separate. |
| 2.1 | Inherit requirement vocabulary in this source; do not equate proposed editorial requirements with an adopted standard. |
| 2.2 | Terms reviewed, including removal of Content-Base and difference between displayed text and markup. |
| 3 | Reviewed sender, reader, archival and external-browser use cases. A mail sandbox remains necessary even when a browser supplies rendering. |
| 4 | Content-Location labels resources; it does not establish their origin. |
| 4.1 | Grammar reviewed: optional comments/folding surround an absolute or relative URI. Historical grammar dependencies remain tracked. |
| 4.2 | Inherit one Content-Location per heading, coexistence with Content-ID, and possible fictitious or inaccessible labels. Verified419 is wording correction. |
| 4.3 | Inherit aggregate identity distinct from root identity and possible historical-version differences. |
| 4.4 | Encoding subsection reviewed; header decoding is distinct from URI percent processing. |
| 4.4.1 | Inherit source-specific encoded-word handling for inappropriate header characters, header-only transformation and UNKNOWN-8BIT fallback where charset cannot be established. Reconcile with RFC2047 and current internationalized-header rules before implementation. |
| 4.4.2 | Inherit encode-before-fold order and RFC2017 dependency for URL folding. |
| 4.4.3 | Inherit unfold-before-decode order on receipt. |
| 5 | Inherit legacy base precedence: embedded base, immediate absolute Content-Location, enclosing headings, HTTP retrieval URI where applicable, then thismessage:/. Do not use a browser page URL or local filesystem path as an accidental mail base. |
| 6 | Inherit standalone HTML without related container when linked resources are absent. Missing connectivity and inaccessible links do not imply malformed mail or authorize automatic fetching. |
| 7 | Inherit related aggregation, start-object type including multipart/alternative, source URI preservation and label uniqueness. Legacy inner-to-enclosing lookup is explicitly supported; peer and inward lookup are outside source coverage. New profile isolation is a proposed restriction. |
| 8 | Link-processing scope reviewed. |
| 8.1 | Reviewed archival and navigation use cases. Mention of script, applets and objects is not permission under the new rendering profile. |
| 8.2 | Inherit legacy URI matching after MIME decoding and base resolution, using octet equality without percent-decoding Content-Location comparisons. Source permits fallback Internet lookup; profile disables automatic network fallback. CID-specific rules are distinct. |
| 8.3 | Inherit cid matching only against Content-ID, never a cid-valued Content-Location. Preserve global identifier uniqueness requirements; identifiers are not authentication. |
| 9 | Examples are explicitly illustrative and subordinate to prose. Indentation and ellipses are not wire data. |
| 9.1 | Standalone HTML example reviewed; raw 8bit transport needs negotiated support and explicit charset. |
| 9.2 | Absolute-location example reviewed with verified645 correcting malformed root IDs. |
| 9.3 | Relative-location example reviewed with duplicate verified646/647. Remaining demonstration comments, missing image types, literal equals signs in quoted-printable markup, and incorrect numeric copyright reference mean this is not a wire fixture. |
| 9.4 | No-base example illustrates thismessage:/; same abbreviated image data and quoted-printable demonstration issues prevent fixture reuse. |
| 9.5 | CID example reviewed; cid-valued Content-Location ignored. Multiple-at-sign identifiers and explanatory semicolon text are not emitted by the proposed generator. |
| 9.6 | Nested lookup example reviewed with verified648–651 and8566. Remaining malformed HTML/URI examples are not copied into tests; source prose defines supported direction of lookup. |
| 10 | Inherit separate HTML character references, MIME charset and transfer encoding stages. CRLF conversion can break checksums; profile preserves received original evidence and never presents transformed content as unchanged authenticated bytes. |
| 11 | Security subsections reviewed. |
| 11.1 | Inherit untrusted origin labels, URI/token leakage, executable-content risk and tracking exposure. These directly motivate isolation and deliberate external navigation. |
| 11.2 | Inherit bundled-resource precedence and prohibition on sharing received resources through a general cache. Scope caches to the original aggregate; do not let a sender populate a trusted web-origin cache. |
| 12 | Reviewed differences from RFC2110; never generate Content-Base. Optional legacy recognition is compatibility behavior, not a new-profile feature. |
| 13 | Acknowledgements reviewed; no protocol behavior. |
| 14 | References reviewed with verified418/8603 correcting related and CID RFC numbers. Historical URL, HTML and MIME dependencies require explicit current-version mapping. |
| 15 | Contact information reviewed; no protocol behavior. |
| 16 | Copyright statement reviewed; no protocol behavior. |

## Errata

All eleven records are Verified in the retrieved snapshot.

| Record | Disposition |
| --- | --- |
| [418](https://www.rfc-editor.org/errata/eid418) | Correct REL reference to RFC2387. |
| [419](https://www.rfc-editor.org/errata/eid419) | Wording correction; no algorithm change. |
| [645](https://www.rfc-editor.org/errata/eid645) | Correct root Content-ID and matching start parameter. |
| [646](https://www.rfc-editor.org/errata/eid646) | Replace illustrative semicolon annotation with header form; continuation still needs legal folding when generating a fixture. |
| [647](https://www.rfc-editor.org/errata/eid647) | Duplicate of646; retain record without counting an independent behavior. |
| [648](https://www.rfc-editor.org/errata/eid648) | Correct malformed Content-ID in nested example. |
| [649](https://www.rfc-editor.org/errata/eid649) | Insert header/body separator before nested multipart delimiter. |
| [650](https://www.rfc-editor.org/errata/eid650) | Correct malformed nested Content-ID. |
| [651](https://www.rfc-editor.org/errata/eid651) | Correct nested header/body separation and Content-ID. |
| [8566](https://www.rfc-editor.org/errata/eid8566) | Balance SRC quotation marks in one example. |
| [8603](https://www.rfc-editor.org/errata/eid8603) | Correct MIDCID reference to RFC2392. |

## Consequences for the proposal

New messages use cid references for bundled rendering resources. They do not require Content-Location or an HTML base element. Imported legacy mail can retain its Content-Location references and resolve included resources using the legacy rules without rewriting original bytes.

The proposed new profile confines automatic lookup to the selected related object. RFC2557 also supports lookup from an inner related object into an enclosing one; a legacy renderer may support that behavior within the same received message. Neither path can silently obtain a missing resource from another message, a shared web cache or the network.

Content-Location matching does not percent-decode the URI. This differs from converting a cid URL to its Content-ID. The implementation must not reuse a single generic decode-everything helper for both operations. Resolve base references before comparing legacy location labels; do not promote a sender-chosen label to trusted origin identity.

The source's unique-label rule and RFC2392's alternative-representation exception need a precise composition: generated baseline resources have distinct IDs; received alternative variants are selected using MIME rules before ambiguous matches are rejected. This is a proposed reconciliation, not an undocumented blanket first-match rule.

Acceptance cases include an inner legacy reference to an enclosing resource, prohibited cross-message cache reuse, a spoofed trusted-site Content-Location, an encoded URI that must not be percent-normalized for location matching, a cid-valued location that cannot satisfy a cid reference, and missing-resource handling without network access. No implementation pass is claimed yet.
