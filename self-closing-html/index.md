---
title: Opt-in Self-Closing HTML
order: -1
eyebrow: Independent HTML proposal
status: "Unofficial Editor's Draft · Stage 0"
---

# Opt-in Self-Closing HTML

**Write an empty HTML element once.** With an explicit opt-in, `/>` processes the opening tag and immediately closes it before reading more source.

```html
<!DOCTYPE html PUBLIC "self-closing">

<user-avatar name="Ada" />
<small />
<button />
<table />
<script src="app.js" />
<p>Following content</p>
```

HTML void elements and SVG/MathML keep their existing behavior. HTML error recovery still applies, including invalid contexts and the document's required structure.

## Why authors would use it

Instead of `<user-avatar name="Ada"></user-avatar>`, write `<user-avatar name="Ada" />`. The name appears once, and the end of the opening tag states that it has no authored children.

JSX and Vue templates already use self-closing syntax; native HTML does not give ordinary elements that meaning.[^1] The proposal removes that syntax difference for empty elements. Existing practice supports familiarity, not a measured productivity claim: no study of authoring speed, readability, or error rates is reported.

## One consistent mechanism

For a non-void HTML element, the parser processes its start tag and then its end-tag action as the source arrives. A self-closing `select` ends the select context before following source. A self-closing `script` finishes the script element, then parsing continues with the following markup.

The slash must be tag syntax, not part of an unquoted attribute value. Ignored tags remain subject to normal HTML recovery, and a self-closing document root cannot create siblings outside the root. [Read the exact rules](/self-closing-html/parsing).

## Opt in deliberately

[HTML Feature Profiles](/html-feature-profiles/) defines the named `self-closing` selection, proposed response header, and `next` family opt-in. Documents and existing parsing APIs keep their current behavior unless they explicitly select the new grammar.

## Security: sanitize for the grammar you use

A legacy sanitizer's output is not automatically safe when reparsed under a different grammar. The safe parsing path must parse the selected grammar first, sanitize its resulting tree, and insert sanitized nodes without a string round trip. The reference implementation demonstrates this composition; it does not make unsafe input safe merely by selecting a profile.

[Security checklist and concrete sanitizer counterexample →](/self-closing-html/security)

## Implementation and feedback

The [reference implementation and results](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence/closure#readme) cover broad closure, chunking, sanitization of the selected grammar, and browser execution. Each result states which implementation it tests and what it establishes.

Review is requested on the token-level rule, its sanitizer integration contract, and native conformance. [Flexible HTML Nesting](/flexible-html-nesting/) remains a separate proposal.

## Read the proposal

::chapter-index

Independent Stage 0 draft. Experimental results are scoped evidence, not production support or a universal security proof.

## Sources

::: {.details summary="Sources and prior art"}
[^1]: React, [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx#2-close-all-the-tags), and Vue, [self-closing tags](https://vuejs.org/guide/essentials/component-basics.html#self-closing-tags).
[^2]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags).
[^3]: WHATWG HTML, [trailing solidus on non-void elements](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^4]: WHATWG HTML, [#721: HTML should support self-closing tags in general](https://github.com/whatwg/html/issues/721), including compatibility, XML, and opt-in discussion.
[^5]: WHATWG HTML, [#9491 sanitizer-mismatch example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [concerns about parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^6]: W3C, [XML 1.0 external identifiers](https://www.w3.org/TR/xml/#sec-external-ent), for the historical distinction between public names and URI-based system identifiers.
[^7]: WHATWG HTML, [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
:::
