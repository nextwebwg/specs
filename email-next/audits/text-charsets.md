---
title: Text charset rules audit
sectionNav: true
---

# Text charset rules audit

**Coverage:** complete six-page RFC6657 and zero matching errata in the refreshed dataset, checked19October2026. [Source](https://www.rfc-editor.org/rfc/rfc6657.html).

| Section | Disposition |
| --- | --- |
| 1 | Does not change existing registered defaults; historical HTTP context reviewed. |
| 2 | Requirement vocabulary reviewed. |
| 3 | New text subtypes define charset determination explicitly; defaults subtype-specific, not transport-specific. Existing unspecified registrations retain US-ASCII. Internal signaling or explicit parameter preferred; new defaults discouraged. |
| 4 | text/plain default remains US-ASCII. |
| 5 | Guessing and conflicting charset sources can cause security disagreement. |
| 6 | Registry preamble change reviewed; no new registration here. |
| 7 | References reviewed. |
| 7.1 | MIME/UTF-8 dependencies tracked. |
| 7.2 | Historical HTML/XML/HTTP references need current successor mapping. |
| Appendix A | Acknowledgements reviewed. |
| Front matter and authors | Status, abstract, copyright and contacts reviewed. |

## Proposed rendering contract

Email Next-generated readable alternatives use explicitly declared UTF-8. This is a generation restriction, not a redefinition of the text/plain default or every text subtype. Legacy decoding remains subtype-specific.

For new-profile interactive processing, contradictory charset declarations or invalid UTF-8 disable activation. A recovered legacy view remains available and labeled as such. Recovery must not supply canonical bytes for a signature or an authenticated event. The final HTML profile still needs an exact parser and charset-precedence reference; this audit alone does not select one.

Required cases include missing charset on plain text, explicit UTF-8, invalid UTF-8, conflicting metadata, and a legacy charset whose display recovery does not change security interpretation.
