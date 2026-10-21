---
title: Reply Microdata — selected source review
order: 4.9
blurb: HTML item scopes · values · local boundaries
sectionNav: true
---

# Reply Microdata — selected source review

The [reply-content contract](../reply-content.md) selects a narrow HTML Microdata vocabulary. It does not redefine generic HTML parsing or claim a full audit of every Microdata vocabulary and conversion example.

| Selected HTML source | Inherited rule and reply-profile consequence |
| --- | --- |
| [Items, §5.2.2](https://html.spec.whatwg.org/multipage/microdata.html#items) | Items use item scopes and type identifiers. The reply profile admits only its two exact types and direct contained chunks. It excludes itemid and itemref; neither global identifiers nor external property ownership can substitute for the authenticated message/index. |
| [Property names, §5.2.3](https://html.spec.whatwg.org/multipage/microdata.html#names:-the-itemprop-attribute) | HTML allows property-name tokens. The selected vocabulary requires one exact property token per annotated element and rejects unknown/repeated properties rather than discarding ambiguity. |
| [Values, §5.2.4](https://html.spec.whatwg.org/multipage/microdata.html#values) | Nested items supply item values; meta elements supply content values. A generic element's string value is not an authenticated HTML fragment. The reply profile separately binds the markup property's element and indexed text. |
| [Association, §5.2.5](https://html.spec.whatwg.org/multipage/microdata.html#associating-names-with-items) | Property ownership depends on item scope and traversal. The reply profile narrows placement, forbids cross-tree references and checks every chunk against the JSON index. Generic extraction alone does not establish complete coverage. |

HTML parsing and recovery follow the [HTML parsing audit](html-parsing.md). The selected Microdata source is the publisher page captured on20October2026, SHA-256 `7aa5d7746f5c6e08c602b8e2f8035738a79bafbb719f28305ef60fdf251f5678` (224337bytes). This is a source fingerprint, not a whole-HTML conformance claim. Vocabulary URLs identify types and never authorize fetching.

The added metadata is extracted before baseline filtering and removed from the host rendering namespace. The existing presentation profile otherwise continues to reject arbitrary sender IDs and metadata. No claim is made that the current sanitizer or cryptographic carrier implements this extension. Example inspection and site compilation cannot establish malformed-input, accessibility or independent-client conformance.
