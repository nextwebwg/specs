---
title: Opt-in Self-Closing HTML
order: -1
eyebrow: Independent HTML proposal
status: "Unofficial Editor's Draft · Stage 0"
---

# Opt-in Self-Closing HTML

**Write an empty HTML element once.** Opt in with `self-closing` for this feature, or `next` for the current and future HTML Next family supported by the browser.

```html
<!DOCTYPE html PUBLIC "self-closing">

<user-avatar name="Ada" />
<small />
<button />
<table />
<script src="app.js" />
<p>Following content</p>
```

The family opt-in uses:

```html
<!DOCTYPE html PUBLIC "next">
```

[HTML Feature Profiles](/html-feature-profiles/) defines both selections and the proposed HTTP response header.

## The benefits of self-closing syntax

- **Less repeated markup.** Write `<user-avatar name="Ada" />` instead of `<user-avatar name="Ada"></user-avatar>`. The element name appears once.
- **An explicit empty-element boundary.** The opening tag contains everything the author supplies: its name, its attributes, and the marker that closes it. Following markup starts after that boundary.
- **A familiar spelling in native HTML.** JSX and Vue templates already use self-closing syntax.[^1] Authors could use the same notation for empty elements in HTML source without a compiler just for this syntax.

::: {.details summary="Evidence for these benefits"}

The shorter spelling and explicit closing marker are properties of the syntax. JSX and Vue demonstrate existing authoring practice and familiarity. No study of authoring speed, readability, or error rates is reported.

:::

## What changes from HTML today

Inside a document's `body`, consider:

```html
<div />
<p>Hello</p>
```

::::: two
:::: {.parser-path}
### HTML today

::: flow
- Create `div`; ignore the slash marker
- Keep `div` open {.acc}
- Put the following paragraph inside `div`
:::
::::
:::: {.parser-path}
### With this feature

::: flow
- Create `div`
- Process its matching closing action {.acc}
- Put the following paragraph after `div`
:::
::::
:::::

The parser already has rules for opening elements, closing them, and recovering from malformed markup. This proposal uses the matching closing action at the slash, before the next source is read. For text elements such as `style`, that also ends the context that reads following characters as text.

[Follow each parsing and recovery step →](/self-closing-html/parsing)

## What this draft adds to earlier proposals

Self-closing syntax and a document opt-in were already proposed in earlier discussions.[^4][^5] This draft develops three concrete parts for review:

- **A boundary for each parsing operation.** A document can select the grammar. Existing string-parsing APIs keep their current grammar; proposed explicit options select a different grammar for an individual call.
- **A specified safe path for untrusted HTML.** The proposed safe parsing method first creates nodes using the selected grammar, then removes unsafe content from those nodes before insertion. Ordinary page loading continues to parse authored HTML without that filtering.
- **Reproducible implementation evidence.** A reference parser, a separate native browser patch, and retained counterexamples make the behavior and its limits testable.

The closing action itself is the familiar idea. The contribution is the specified integration and its implementation evidence. A page that mixes the new grammar with strings filtered for the old grammar still has a security risk; the [security chapter](/self-closing-html/security) demonstrates it and explains the safe API boundary.

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
