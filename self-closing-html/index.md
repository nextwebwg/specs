---
title: Self-closing HTML
eyebrow: HTML Next · independent proposal
status: "Unofficial Editor's Draft · Stage 0"
pager: false
---

# Self-closing HTML

Write an empty element once. Opt in to self-closing tags while keeping HTML's forgiving parser and ordinary DOM.

## The proposal

One declaration enables the shorthand:

```html
<!DOCTYPE html PUBLIC "next">

<user-avatar name="Ada" />
<div class="divider" />
<br />
```

::: two
> [!norm] Tag pairs
> `<div />` → `<div></div>`
>
> `<x-card />` → `<x-card></x-card>`

> [!ex] Void elements
> `<br />` → `<br>`
>
> `<link />` → `<link>`
:::

Only HTML's explicit void-element allowlist skips the end tag. Everything else defaults to a tag pair. **`<br />` never becomes `<br></br>`.**[^1]

## HTML can evolve without becoming XML

Self-closing syntax should be available without adopting XML's strict parsing rules.

> [!note] Keep HTML's flexibility
> Case-insensitive names, boolean attributes, unquoted values, optional tags, and error recovery all keep their HTML rules. The document remains `text/html`.

> [!norm] Let authors choose
> Plain `<!DOCTYPE html>` keeps today's tag interpretation. `<!DOCTYPE html PUBLIC "next">` explicitly selects the new rule.

This addresses the legacy-content objection in **WHATWG HTML #721**: existing documents keep their meaning. The thread also suggested an opt-in; this declaration makes that route concrete within HTML.[^3]

## Why authors want it

- **Less repetition.** An empty custom element declares its intent without repeating a long name.
- **Fewer surprises.** Vue documents how self-closing components work in its templates but can swallow following content in native HTML.[^4]
- **Direct HTML authoring.** Native support would remove the need for a build step solely to expand empty tags.

Adding children later means expanding the tag pair. The element's behavior stays the same.

## A small change for browsers

This is probably the easiest proposal in this collection for browser makers to adopt: its scope is one explicit opt-in and one source abbreviation.

> [!ex] Reuse what browsers already have
> The doctype already carries a public identifier. The tokenizer already recognizes `/>`. The result uses existing DOM elements, rendering, and accessibility behavior.[^2][^6]

`PUBLIC "next"` names a built-in parsing profile. It fetches no external definition and requires neither a new component model nor the other proposals in this collection.[^5]

> [!warn] Stage 0 · open for review
> Browser vendors still need to validate parser edge cases, fragment behavior, and rollout. Current browsers keep standards mode with this declaration but still require expanded tag pairs for non-void elements.[^6]

Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## Parser details and sources

::: {.details summary="Read the proposed parser contract"}
### Selecting the profile

Recognize the initial doctype before element content: name `html`, public identifier exactly `next` (case-sensitive), system identifier absent. Keywords and the doctype name keep HTML's case-insensitive matching.

The profile selects standards rendering mode and is fixed for that parse. Other doctypes retain existing behavior. Later declarations, DOM edits to the doctype, and custom-element registration cannot switch it.

`PUBLIC` names the profile rather than locating a DTD. There is no DTD fetch or validation and no switch to XML. Today this spelling produces a parse error but selects standards mode; recognizing it as conforming requires a standards change. `<!DOCTYPE html next>` and `<!DOCTYPE html-next>` currently trigger quirks mode.[^5][^6]

### Interpreting tags

For HTML names outside the void-element allowlist, process `/>` as a start tag immediately followed by its matching end tag. Without the slash, the start tag remains open under normal HTML rules.

The allowlist is: `area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.[^1]

Match those names case-insensitively in the HTML namespace. With or without the slash, process only the start tag; never generate an end tag. Custom and unknown names default to pairs, regardless of registration or content model. SVG and MathML retain their foreign-content rules.

Keep existing tokenization: `<div data-path=assets/ />` uses the shorthand; `<div data-path=assets/>` has an unquoted value of `assets/` and does not. Optional-end-tag and legacy error recovery remain in force.

### Documents, fragments, and the DOM

- Context-based fragment parsing (`innerHTML`, `outerHTML`, `insertAdjacentHTML()`, and `Range.createContextualFragment()`) uses the context document's profile. A doctype inside a fragment cannot change it.
- Separately parsed HTML documents, including iframe documents and `DOMParser.parseFromString(..., "text/html")`, select their own profile from their own declaration.
- Moving nodes does not reparse them. Later string parsing uses its destination context's profile.
- Elements gain no new node type, interface, JavaScript API, or persistent self-closing flag. CSS, accessibility, and custom-element lifecycles follow the expanded form. A self-closed non-void element can still receive children through DOM APIs.
- Element serialization stays ordinary HTML. Tools emitting complete source that relies on the shorthand must preserve its declaration; fragments rely on the receiving context.

### Compatibility and remaining work

In `<div /><span>Following content</span>`, ordinary HTML makes the `span` a child of the `div`. A supporting parser with the profile enabled makes them siblings. Authors opting in must audit existing markup and inserted fragments for dependencies on today's nesting.[^2][^3]

The profile also intends `<script src="app.js" />` to mean `<script src="app.js"></script>`, and `<textarea />` to mean `<textarea></textarea>`. Precise algorithms and tests remain necessary for script execution, raw-text elements, tables, select elements, document structure, template-associated documents, shadow roots, and document-writing APIs.

Before adoption, measure existing uses of the exact declaration, test fallback across engines, and specify profile propagation and feature detection. `document.doctype.publicId` records author intent; it does not prove support. The small scope is an adoption argument, not a measured implementation estimate.

Unsupported browsers retain today's tag rules. Send them expanded tag pairs. Build-time lowering needs a parser that understands the proposed syntax; string replacement or a DOM rewrite after parsing cannot reliably recover source intent.

Seek browser implementer review alongside the existing WHATWG discussion. This is an independent Stage 0 draft, not a W3C or WHATWG deliverable.

Editor: [Matthew Dean](https://github.com/matthew-dean).
:::

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags).
[^2]: WHATWG HTML, [trailing solidus on non-void elements](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^3]: WHATWG HTML, [#721: HTML should support self-closing tags in general](https://github.com/whatwg/html/issues/721), including compatibility, XML, and opt-in discussion.
[^4]: React, [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx#2-close-all-the-tags), and Vue, [self-closing tags](https://vuejs.org/guide/essentials/component-basics.html#self-closing-tags).
[^5]: W3C, [XML 1.0 external identifiers](https://www.w3.org/TR/xml/#sec-external-ent), for the historical distinction between public names and URI-based system identifiers.
[^6]: WHATWG HTML, [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
:::
