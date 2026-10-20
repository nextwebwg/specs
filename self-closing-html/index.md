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

## The insight: read once, place separately

HTML already recognizes the slash in `<small/>`, but ordinarily leaves small open. Simply closing it in the parser can change whether later characters become text or executable markup.

This proposal separates **reading the source** from **placing its nodes**. The source reader retains HTML's existing interpretation. A second builder places eligible self-closing elements using normal opening-and-closing actions. Every result is checked against what the source reader actually recognized.

```html
<nav><nav /></nav><p>Outside both navs</p>
<table><tr><td /><td>Second cell</td></tr></table>
```

The inner nav and first table cell are empty. The paragraph follows both navs; the table has two cells. Ordinary wrappers, formatting elements, custom-element hosts and table rows/cells share this behavior.

[Compare existing HTML and the proposal, step by step →](/self-closing-html/parsing)

## How it addresses the text-to-markup objection

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

Removing div from the source reader too early can change SVG recovery and turn the apparent image into markup. This proposal retains that recovery entry: the later closing div exits SVG, the following style is HTML, and its contents remain text.

The placement builder receives that text as text. A conflicting placement is rejected in favor of the recognized HTML recovery. **The protection is part of parsing: only elements the source reader recognized may appear, with their original namespace, attributes and protected contents.**

[Follow the security case and checked recovery →](/self-closing-html/parsing#why-remembering-the-element-matters)

## A small set of understandable boundaries

Text-reading starts such as script/style/textarea, template owners, form/select contexts and document scaffolding retain their ordinary closing behavior. Each owns a reading or construction boundary that the source reader needs. Table rows and cells participate in the shorthand.

For example, `<script />` opens a script and still requires `</script>`. The [boundary table](/self-closing-html/parsing#boundaries-that-require-a-real-closing-tag) explains the categories and concrete reasons. Malformed input follows checked recovery; ordinary authored shorthand follows normal empty-element placement.

## What the evidence establishes

| Question | Evidence and limit |
| --- | --- |
| Does ordinary shorthand behave as authors expect? | 4,000 structured authoring cases and 1,000 table cases match explicit empty pairs, including nested same-name wrappers and formatting. This is finite coverage. |
| Can the output introduce an element the source reader rejected? | Both placement paths check source identity, namespace, attributes and protected context. A checked abstract theorem establishes source authorization for the selection rule; it does not verify the JavaScript or HTML parser. |
| Do the retained security examples stay inactive? | 120,000 generated comparisons, 20,504 token-checkpoint audits and 16 targeted cases per browser adapter engine pass. The tested text/template attacks create no active image or observed attack request. |
| Is this implemented in a native browser parser? | Not yet. Chromium, Firefox and WebKit supply DOM/execution/resource behavior through a shared parse5 adapter. Native integration remains required. |

The suite also passes 88 component and placement tests. [Results, reproduction and limits →](/self-closing-html/security)

## Status and review

This is a proposed source-authorized placement algorithm. Its retained counterexamples and recovery checks are part of the evidence available for review.

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
