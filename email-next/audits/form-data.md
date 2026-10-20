---
title: Multipart form data audit
sectionNav: true
---

# Multipart form data audit

RFC8058's recommended one-click unsubscribe encoding depends on [RFC7578](https://www.rfc-editor.org/rfc/rfc7578.html). Encoding does not authorize submission or identify the person submitting it. Email Next's structured conversation replies and service-answer JSON do not become arbitrary HTML forms.

**Coverage:** complete fifteen-page base text, including examples, references and appendices. Current official metadata lists no updates or successor. All four current errata were read and reconciled with the captured records. No encoder, parser or deployed endpoint was tested.

| Section | Disposition |
| --- | --- |
| 1 | Application-independent encoding; not authorization. |
| 2 | Filename escaping option. |
| 3 | Form processing remains external. |
| 4 | MIME multipart foundation. |
| 4.1 | Collision-free boundary required. |
| 4.2 | Required disposition/name; filenames untrusted. |
| 4.3 | Separate repeated file parts. |
| 4.4 | Per-part type defaults. |
| 4.5 | Explicit text charset. |
| 4.6 | Default-charset convention; corrected example. |
| 4.7 | Avoid transfer encoding over HTTP. |
| 4.8 | Restricted part headers. |
| 5 | Deployment differences matter. |
| 5.1 | Non-ASCII compatibility boundaries. |
| 5.1.1 | ASCII names preferred. |
| 5.1.2 | Application supplies charset. |
| 5.1.3 | Legacy decoding ambiguity. |
| 5.2 | Preserve order and duplicates. |
| 5.3 | URL-encoding is separate. |
| 5.4 | No intrinsic request binding. |
| 6 | Registry reference changes. |
| 7 | No confidentiality/integrity; prevent disclosure. |
| 8 | Registration and required boundary. |
| 9, 9.1, 9.2 | Dependencies inspected, not recursively closed. |
| A | Historical encoding changes. |
| B | Alternatives are not selected. |

Front matter, acknowledgements and author details were also read.

Verified erratum **4676** repairs delimiter placement. Reported **5616**, **7385** and **9032** are not accepted replacements. In particular, 7385's proposed percent-encoded text does not override the specification's distinction between filename escaping and text-body charset handling.

The narrow unsubscribe body needs no filenames, uploads or non-ASCII field names. Supporting those general features would require additional application rules; this audit does not select them.
