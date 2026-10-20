---
title: Related MIME parts audit
sectionNav: true
---

# Related MIME parts audit

Multipart/related supplies an existing container for a root document and its resources. Email Next can use it without inventing a resource bundle, but must define safe behavior where the source leaves processing undefined.

**Coverage:** complete RFC2387 and six retrieved errata read and assessed on 19 October 2026. CID addressing, HTML message aggregation, disposition parameters and current registrations remain separate dependencies.

Sources: [RFC2387](https://www.rfc-editor.org/rfc/rfc2387.html), [metadata](https://www.rfc-editor.org/rfc/rfc2387.json), [errata](https://www.rfc-editor.org/errata/rfc2387).

| Section | Disposition |
| --- | --- |
| 1 | Inherit compound-object model and related processing precedence over disposition. |
| 2 | Inherit required type and optional start/start-info; multipart transfer restrictions remain applicable. |
| 3 | Inherit root selected by start, otherwise first part; compound relationships belong to the consuming application. |
| 3.1 | Inherit required type matching root type. Source leaves mismatch undefined; proposed profile rejects rich activation for mismatch. |
| 3.2 | Inherit Content-ID root selection. Proposed profile requires exactly one matching root. |
| 3.3 | Start-info needs application-defined semantics. Baseline defines no command execution or use of start-info. |
| 3.4 | Verified5578 makes type required. Prose requires MIME parameter quoting; held5048 exposes an unresolved grammar presentation issue. Generic MIME syntax controls generated quoting. Recursive cid-list has no terminating production; do not implement that fragment as a complete parser. |
| 4 | Inherit ignoring disposition type for related-aware processing; filenames remain optional hints, not resource identity or filesystem authority. |
| 5 | Illustrative examples reviewed, not adopted wire fixtures. |
| 5.1 | Fixed-record example has parameter separator defects tracked by held3386. |
| 5.2 | Image example has separator defect tracked by held3387 and a mismatching CID punctuation in an image reference; generate independently validated examples. |
| 5.3 | Related-aware versus mixed fallback behavior reviewed; inline is no hiding guarantee. |
| 6 | Inherit mixed fallback for unaware clients. Malformed suppression sentence tracked by held3389; do not manufacture a stronger inherited rule. |
| 6.1 | Inherit provision of bodies, Content-* headers, container parameters and resource correspondence to the consuming application. |
| 6.2 | Inherit link-preserving storage; derived local mappings must retain original source. |
| 6.3 | Inherit recursive processing/storage; proposed lookup scopes must prevent cross-message resource capture. |
| 6.4 | Configuration suggestion reviewed; not a wire media type or permission to launch external programs. |
| 7 | Inherit content-specific security; container supplies no authentication or sandbox by itself. |
| 8 | Acknowledgements reviewed; no protocol requirement. |
| 9 References | Dependencies reviewed; current CID, MIME and disposition sources tracked separately. |
| 9 Author | Duplicate source numbering retained explicitly; contact information has no protocol behavior. |
| 10 | Historical removal of angle brackets from cid URLs reviewed; current RFC2392 controls addressing. |
| 11 | Copyright statement reviewed; no protocol requirement. |

## Errata

| Record | Status | Consequence |
| --- | --- | --- |
| [3386](https://www.rfc-editor.org/errata/eid3386) | Held | Example separators; emitted headers follow RFC2045 grammar. |
| [3387](https://www.rfc-editor.org/errata/eid3387) | Held | Same issue in second example. |
| [3389](https://www.rfc-editor.org/errata/eid3389) | Held | Suppression sentence ambiguous; no automatic normative upgrade. |
| [3574](https://www.rfc-editor.org/errata/eid3574) | Held | Configuration wording/spelling only. |
| [5048](https://www.rfc-editor.org/errata/eid5048) | Held | Quoting discrepancy remains explicit; do not adopt an unquoted slash-containing MIME parameter. |
| [5578](https://www.rfc-editor.org/errata/eid5578) | Verified | Type parameter required, matching prose. |

## Proposed resource rules

For the HTML alternative with embedded resources, use a multipart/related container with type="text/html" and an explicit start identifying the HTML root. Put that root first for clients using mixed fallback. Independent user attachments remain outside the related object.

Resource resolution is local to the selected compound object. A missing or ambiguous target produces a missing-resource indication; it does not trigger network retrieval or a search through other conversations. No sender-provided filename becomes a local path. Authentication requirements apply to the complete protected compound object, including referenced resources.

The [RFC2392 audit](content-identifiers.md) now covers percent decoding and the repeated-ID alternative exception; the [message chapter](../messages.md) defines the proposed scoped selection policy. Current identifier grammar reconciliation remains open. Tests must cover root mismatch, absent root, ambiguous IDs, nested containers, mixed fallback and attachment isolation. No interoperability result is claimed.
