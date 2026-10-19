---
title: Opt-in Self-Closing HTML
order: -1
eyebrow: Independent HTML proposal
status: "Unofficial Editor's Draft · Stage 0"
---

# Opt-in Self-Closing HTML

Native self-closing tags, with forgiving HTML syntax. An explicit opt-in adds the shorthand while preserving HTML's boundaries between text and markup.

## Write the empty element once

```html
<!DOCTYPE html PUBLIC "self-closing">

<user-avatar name="Ada" />
<div class="divider" />
<br />
```

::: two
> [!norm] Ordinary elements
> `<div />` → `<div></div>`
>
> `<x-card />` → `<x-card></x-card>`

> [!ex] Void elements
> `<br />` → `<br>`
>
> `<link />` → `<link>`
:::

Authors already use self-closing components in JSX and Vue templates. This brings the shorthand to HTML source.[^1] HTML's void-element allowlist remains explicit: **`<br />` never becomes `<br></br>`.**[^2]

Case-insensitive names, boolean attributes, unquoted values, optional tags, and error recovery retain their HTML rules. XML parsing is not required.

## Why this is useful to authors

An empty component often gets all its information from attributes. Repeating its name in a closing tag adds no child content:

```html title="Existing HTML"
<user-avatar name="Ada"></user-avatar>
<status-badge state="ready"></status-badge>
```

```html title="With this proposal enabled"
<user-avatar name="Ada" />
<status-badge state="ready" />
```

The name appears once, and `/>` marks “no authored children” at the opening tag. Eligible empty components could use that spelling directly in HTML source.

[JSX](https://react.dev/learn/writing-markup-with-jsx#2-close-all-the-tags) and [Vue templates](https://vuejs.org/guide/essentials/component-basics.html#self-closing-tags) already use the syntax. That shows existing practice, not measured gains in speed, readability, or error rates. No study establishes whether this proposal’s benefit outweighs its exceptions.

**The main tradeoff:** not every element can self-close. `<script />` still starts a script and can swallow following source. [Read the exceptions and consequences](/self-closing-html/parsing#preserve-sensitive-elements). Elements with children keep closing tags. Component embedding in tables is a [separate proposal](/flexible-html-nesting/).

## Current implementation gap

The draft no longer makes `hidden`, `inert`, `disabled`, or `popover` change self-closing eligibility, and removes container exclusions justified only by visibility/focus observations. The archived prototypes still use the older restrictions. Their results are evidence about that earlier algorithm, not verification of the revised rules. [Read the correction](/self-closing-html/security#what-the-containment-tests-actually-showed).

## What has been checked?

The [plain-language issue checklist](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme) explains each problem, its proposed fix, the supporting evidence, and the remaining work. Start there for the findings; the [security chapter](/self-closing-html/security) explains the main examples. The [parsing rules](/self-closing-html/parsing) are the implementation reference.

## What held this back

Browsers currently ignore the slash on ordinary HTML elements. Changing that everywhere would change existing pages.[^3][^4]

A second obstacle is security. A sanitizer can treat apparent tags as harmless text, while a different parser exposes them as markup. A document opt-in alone does not fix that mismatch.[^5]

## How the proposal resolves it

The proposal combines three rules: explicit opt-in, preserved parsing context, and exemptions for sensitive elements.

### Opt in without changing existing pages

`<!DOCTYPE html PUBLIC "self-closing">` requests this capability for document source. The [HTML Feature Profiles proposal](/html-feature-profiles/) defines named selection and the alternative `PUBLIC "next"` preset. Plain `<!DOCTYPE html>` keeps today's behavior. The selector names a built-in profile: it fetches no DTD and does not enable XML. Current browsers retain standards rendering mode with this declaration, but do not implement the new syntax.[^6][^7]

### Close the DOM element; keep the parser's context

For ordinary shorthand, following content becomes a sibling:

::: two
```html title="Source"
<div class="divider" />
<span>Following</span>
```

```html title="Resulting DOM"
<div class="divider"></div>
<span>Following</span>
```
:::

The parser still remembers the div for later closing tags and error recovery. Making it empty changes where following nodes sit, without changing HTML’s decisions about text and tags. [See the worked example](/self-closing-html/security#recover-at-namespace-boundaries).

### Keep text parsing unchanged

Sensitive elements retain their existing slash handling. For example:

```html
<style/><img src onerror=alert(1)><style></style>
```

`style` is exempt. The apparent image remains style text; no image or event-handler node is created. Retained recovery context also protects cases where an earlier ordinary element affects a later text or namespace boundary.

> [!ex] The rule behind the shorthand
> Change eligible parent/child relationships while preserving recognized tags, text, namespaces, and text-parsing boundaries. Existing HTML insertion APIs retain their current grammar.

The native experiment tests the earlier literal `PUBLIC "next"` opt-in. The proposed [response header and profile selection](/html-feature-profiles/) and [explicit parsing calls](/self-closing-html/parsing#parse-independently-of-the-caller-s-document) are not implemented by that experiment.

## What feedback is needed?

Review is requested on whether the authoring benefit justifies the [exceptions and their consequences](/self-closing-html/parsing#why-keep-exceptions), whether the retained parsing context adequately addresses sanitizer disagreement, and what native tests and implementation changes are needed next. Broader self-closing behavior is not ruled out, but is not established by the current evidence. The [work plan before shipment](/self-closing-html/security#work-plan-before-browser-shipment) separates discussion readiness from production readiness.

## Read the proposal

::chapter-index

This is an independent Stage 0 draft. The mathematical proof covers the node-rearrangement rule; an experimental native Ladybird implementation now passes bounded streaming and execution checks. Production conformance and universal execution safety remain unproved.

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
