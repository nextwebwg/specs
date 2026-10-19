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

The div remains on the parser's recognition stack even though it is empty in the DOM. A later `</div>` can still close that entry and any intervening SVG context. The next `style` then uses HTML text parsing, so image-looking text stays text. **The slash changes containment without discarding the scope information that protects text boundaries.**

### Keep text and protected content inside their boundaries

Sensitive elements retain their existing slash handling. For example:

```html
<style/><img src onerror=alert(1)><style></style>
```

`style` is exempt. The apparent image remains style text; no image or event-handler node is created. Retained recovery context also protects cases where an earlier ordinary element affects a later text or namespace boundary.

> [!ex] The rule behind the shorthand
> Change eligible parent/child relationships while preserving recognized tags, text, namespaces, and protected containers. Existing HTML insertion APIs retain their current grammar.

The [parsing rules](/self-closing-html/parsing) define eligibility and recovery. [Security and evidence](/self-closing-html/security) separates the sanitizer and distant-mode-switch objections, shows the retained stack token by token, and states what the reference construction establishes.

The recorded experimental implementation uses the earlier literal `PUBLIC "next"` opt-in. Named-selector resolution and HTTP-header selection are proposed in HTML Feature Profiles and are not implemented by those evidence artifacts.

A server can also select this capability with the proposed `HTML-Feature-Profile` response header. [HTML Feature Profiles](/html-feature-profiles/#http-response-header) defines the header, its precedence over the doctype, and unsupported-request handling.

## Read the proposal

::chapter-index

This is an independent Stage 0 draft. The reference model establishes a static text-to-markup preservation property; an experimental native Ladybird implementation now passes bounded streaming and execution checks. Production conformance and universal execution safety remain unproved.

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
