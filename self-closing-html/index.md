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

## The insight: empty in the document, remembered by the parser

HTML already recognizes `/>`, but for ordinary non-void HTML elements it keeps the element open. This proposal makes an eligible element empty in the output **while retaining the parser state that determines what the following characters mean**.

```html
<small/><span>Following content</span>
```

The output contains an empty small element followed by the span. Internally, HTML's ordinary recovery records still remember the small element until its rules close it. Formatting elements, ordinary wrappers and custom-element hosts use the same containment operation.

[See the two trees and each parsing step →](/self-closing-html/parsing)

## Why immediate closing is not enough

The security objection is that changing parser state can turn text into executable markup. In this example, an early close can change how a later closing tag recovers from SVG:

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

The recognition-preserving algorithm makes div empty but retains its internal entry. The later `</div>` still exits SVG, so the following style is an HTML stylesheet and the apparent image stays text. No image handler is created.

**The protection comes from preserving HTML's interpretation, not from sanitizing a different interpretation afterward.**

[Follow the unsafe immediate-close path and the proposed recovery →](/self-closing-html/parsing#why-remembering-the-element-matters)

## Consistent boundaries for exceptions

Text-reading elements such as `style`, `script` and `textarea` keep their ordinary closing behavior. Template contents stay inactive. Document scaffolding, dedicated table/select containers and explicit inert containers also keep their boundaries.

These groups follow from text recognition, inactive ownership and child-placement rules. Attributes such as hidden, disabled and popover do not determine eligibility. Small, links, emphasis, buttons and forms participate in the same ordinary output rule.

For example, `<script />` still opens a script and requires a closing tag. The [boundary table](/self-closing-html/parsing#text-and-inactive-contents-keep-their-boundaries) explains each category and its consequence.

## What the current evidence establishes

| Question | Evidence and limit |
| --- | --- |
| Can recognized text become a new element through this operation? | Output uses the recognizer's existing nodes and data. The abstract projection theorem preserves payload order and protected ancestry. It is not a verified implementation of the complete HTML parser. |
| Do the retained attacks stay inactive? | Reference and three-engine DOM-adapter tests retain text, template ownership and the tested inactive resources. These are targeted results, not universal execution safety. |
| Does the rule support ordinary and formatting elements? | The simple body-context inventory includes 76 eligible parser-known names, including small, links, emphasis, buttons and forms. Complex recovery is specified by the containment algorithm, rather than literal source expansion. |
| Is there a native implementation of this replacement? | Not yet. The earlier immediate-closure native experiment implements a different algorithm and does not establish this replacement. |

The reference passes 61 focused tests and 120,000 generated document/fragment comparisons. Ten targeted cases pass per engine in Chromium, Firefox and WebKit through a shared-recognizer DOM adapter. [Results, reproduction and limitations →](/self-closing-html/security)

## Status and review

This is a recognition-preserving replacement for the earlier immediate-opening-and-closing draft. The earlier broad security claim was not supported by that algorithm; its counterexample remains evidence against it.

Native integration, form association, declarative shadow-root ownership, modules and scheduling, encoding restarts, speculative loading and independent implementer review remain required. The current results support review of this candidate, not a claim that every browser security concern is resolved.

[HTML Feature Profiles](/html-feature-profiles/) owns opt-in selection and explicit API options. [Flexible HTML Nesting](/flexible-html-nesting/) remains a separate proposal. Earlier self-closing and opt-in proposals are prior art.[^4][^5]

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
