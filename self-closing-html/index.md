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

## The benefits of self-closing syntax

- **Less repeated markup.** Write `<user-avatar name="Ada" />` instead of `<user-avatar name="Ada"></user-avatar>`. The element name appears once.
- **An explicit empty-element boundary.** The opening tag contains everything the author supplies: its name, its attributes, and the marker that closes it. Following markup starts after that boundary.
- **A familiar spelling in native HTML.** JSX and Vue templates already use self-closing syntax.[^1] Authors could use the same notation for empty elements in HTML source without a compiler just for this syntax.

::: {.details summary="Evidence for these benefits"}

The shorter spelling and explicit closing marker are properties of the syntax. JSX and Vue demonstrate existing authoring practice and familiarity. No study of authoring speed, readability, or error rates is reported.

:::

## The key insight: parsing and sanitization agree

The slash takes effect while the parser is building the document. It processes the element's opening action and its matching closing action before reading the next source character. The parser's memory of open elements, formatting, tables, and templates therefore advances at the same boundary. A self-closing `select` ends the select context; following markup is parsed in the resulting context.

That change also matters for security. Consider:

```html
<style /><img src="x" onerror="runCode()">
```

Today's HTML parser treats the apparent image as stylesheet text. Under the proposed grammar, it is an image element with an event handler. A sanitizer using today's grammar could check the text while a later parser creates the active element.[^5]

**The safe path parses with the selected grammar first, then sanitizes the actual nodes it produces.** In this example, the sanitizer sees the image and removes its handler. The caller receives sanitized nodes to insert directly. This keeps parsing, filtering, and insertion in agreement.

[Exact parsing rules →](/self-closing-html/parsing)

## How this addresses the earlier concerns

| Concern | Proposed answer |
| --- | --- |
| Existing pages and libraries depend on today's parsing. | [HTML Feature Profiles](/html-feature-profiles/) selects the grammar explicitly, through a document declaration, proposed response header, or proposed parsing option. Existing parsing APIs retain their grammar by default. |
| A parsing change can expose markup that a sanitizer treated as text. | The safe entry point parses the selected grammar and sanitizes its resulting nodes before insertion. The reference implementation demonstrates removal of the handler in a retained sanitizer-mismatch case. |
| Scripts, tables, formatting, and text elements have special parser behavior. | The matching closing action updates ordinary HTML parser state at the slash. Reference and native tests exercise those contexts, streaming, execution checkpoints, and mutations. |

The proposal combines a consistent closure rule, explicit grammar selection, and sanitization of that grammar's actual result. Those are concrete, testable responses to the compatibility and security objections in earlier discussions.[^4][^5]

The [evidence checklist](/self-closing-html/security) separates passing experiments from remaining shipment work, including native profile API integration, encoding restarts, and implementer security review. These results support incubation; adoption requires that review and broader interoperability work.

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
