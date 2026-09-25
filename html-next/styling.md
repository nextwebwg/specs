---
title: Style Scoping
order: 9
blurb: scoped styles without shadow cost
eyebrow: Declarative HTML Components Level 1
status: Level 1 · stable direction
---

# Style scoping

A component's `<style>` is **scoped to that component**: its rules match the component's own markup and no further, without a shadow boundary. This is the styling half of fixing Web Components: the scoping authors actually wanted, without the cascade and theming losses that kept them away from Shadow DOM.

## The scope: what a rule matches

The rules in a component's `<style>` match the component's **region**: its root element and the markup inside it, down to the boundaries below, and nowhere else in the document. A bare type or class selector needs no qualification, and **every combinator works normally inside the region**: descendant (`a b`), child (`a > b`), sibling (`a + b`, `a ~ b`), and `:has()`.

```html
<template component="x-card">
  <defs>…</defs>
  <article>
    <h2>…</h2>             <!-- in scope -->
    <p class="lead">…</p>  <!-- in scope -->
    <slot></slot>          <!-- projected content: out of scope unless :slotted() -->
    <x-badge>New</x-badge> <!-- nested component: out of scope, root included -->
  </article>
  <style>
    :host { padding: 1rem; }          /* the root */
    h2 { margin: 0; }                 /* descendant, matches */
    :host > .lead { color: gray; }    /* child of the root, matches */
  </style>
</template>
```

## Where the scope ends

A component's subtree can contain markup that is not the component's to style. Two boundaries close the region, so it is a range with a lower limit, not just a starting point.

| Boundary | Rule |
| --- | --- |
| Nested components | A nested component is its **own** scope, root included. The enclosing component's rules [must not]{.kw} match the nested component's root or anything inside it. The enclosing component lays its children out from its own markup (`gap`, grid, and flex on its container); a consumer that needs to adjust one child's box puts its own `class` on that invocation. |
| Projected content | Content a consumer passes through a `<slot>` belongs to the consumer, not the component (see [Components](/html-next/components)). The component's rules [must not]{.kw} match projected nodes unless it opts in with [`:slotted()`](#slotted). |

Content a component moves elsewhere with [`<portal>`](/html-next/components) stays logically owned by it, so it stays in the component's region: the component's rules keep matching it after the move, and the same two boundaries apply inside it.

```html
<template component="x-menu">
  <button>Options</button>
  <portal to="body">
    <ul class="list">…</ul>   <!-- moved to body, still this component's markup -->
  </portal>
  <style>
    .list { position: fixed; padding: 0.25rem; }   /* still matches after the move */
  </style>
</template>
```

> [!note] Scoping, not a security boundary
> Scoping decides where a component's rules apply. It does not protect markup from other code: nodes another script inserts inside a component's region are styled like the rest of that region.

## The root: :host

`:host` selects the component's own root. It is the only way to select the root; `:scope` is not part of the authoring syntax.

A rule may be conditioned on context outside the component by placing that context before `:host`: an ancestor anywhere in the document, such as a theme class on the root element, or another component, named by its tag. A selector that does not mention `:host` is relative to the component, so `.dark .label` looks for a `.dark` inside it. Either way, the element a rule styles is always inside the component's region; only the condition reaches outside.

```html
<style>
  :host .label { color: var(--x-card-text, CanvasText); }
  .dark :host .label { color: var(--x-card-text, Canvas); }  /* .dark anywhere above the component */
  x-sidebar :host { inline-size: 100%; }                     /* inside an x-sidebar */
  .dark .label { … }   /* a .dark inside this component, not a page theme */
</style>
```

Styling the page itself (its `<body>`, other components, or unrelated elements) is never a component's to do. Page-wide rules belong in the page's stylesheets, or in a stylesheet a package ships alongside its components for the page to include. At-rules that are document-wide in CSS, such as `@font-face`, `@property`, and `@keyframes` names, keep that meaning inside a component's `<style>`.

## Styling by state: :host-state()

`:host-state()` selects the root while the component's **props and state have given values**. Its argument is a sequence of attribute-selector-shaped tests on declared names:

```html
<template component="x-container">
  <defs>
    <prop name="measure" type="narrow | normal | wide" default="normal">Maximum line length.</prop>
  </defs>
  <div><slot></slot></div>
  <style>
    :host {
      display: block;
      margin-inline: auto;
      max-inline-size: var(--x-container-measure, 65ch);
    }
    :host-state([measure="narrow"]) { max-inline-size: var(--x-container-measure, 45ch); }
    :host-state([measure="wide"])   { max-inline-size: var(--x-container-measure, 80ch); }
  </style>
</template>
```

| Test | Matches while |
| --- | --- |
| `[name="value"]` | the prop or state `name` resolves to `value`, including when `value` is the declared default |
| `[name]` | `name` is truthy |
| `[a="x"][b]` | every test holds |

A test names a declared prop or state whose type is a string, number, boolean, or keyword union. Only equality and presence are supported; other attribute operators, and props of structured types, are diagnostics.

State works the same way as props, so a component styles what its controller changes without writing attributes for its own stylesheet:

```html
<template component="x-disclosure">
  <defs>
    <prop name="summary" type="string" default="">Visible heading.</prop>
    <state name="open" :value="false"></state>
  </defs>
  <details>…</details>
  <style>
    :host-state([open]) .marker { rotate: 90deg; }
    :host-state([summary=""]) .marker { display: none; }
  </style>
</template>
```

> [!note] Resolved values, not reflected attributes
> A lowered root records only the props an author wrote, as `data-*` attributes (see [Rendered form](/html-next/rendered-form)), so a selector on them cannot see defaults. `:host-state()` sees the resolved value, so default styling is written like any other.

## Styling projected content: :slotted() {#slotted}

When a component *wants* to style what a consumer projects, such as a form control skinning its `<input>` or a prose component setting rhythm for headings and lists, it opts in with `:slotted()`:

```html
<template component="x-prose">
  <article><slot></slot></article>
  <style>
    :slotted(h2)       { margin-block: 1.5em 0.5em; }
    :slotted(ul li)    { margin-block: 0.25em; }
    :slotted(p) { & + p { margin-block-start: 1em; } }
    :host-state([compact]) :slotted(*) { margin-block: 0; }
  </style>
</template>
```

- `:slotted(sel)` matches projected content at **any depth**: a projected node, or any node inside one, that matches `sel`.
- The argument is a full selector, and nested rules work inside a `:slotted()` rule.
- Matching stops at any nested component.
- `:slotted()` rules are a **low-specificity baseline**: a consumer's own rules on their projected nodes win ties, so a component sets a default look without seizing control. `:slotted(*) { all: unset }` is the idiomatic clean slate.

> [!note] Deeper than ::slotted()
> Shadow DOM's `::slotted()` accepts only a compound selector on top-level nodes, a restriction adopted because matching from a shadow tree into light-DOM descendants was costly; authors have asked for years to lift it.[^5] Here, projected content stays in one document and is matched like any other markup, so the restriction has no reason to exist. A component ported from Shadow DOM rewrites `::slotted(x)` as `:slotted(x)`.

## Customization: custom properties

A component's customizable surface is its **custom properties**. The component reads each one with its default, `var(--x-button-radius, 6px)`, and an application or an enclosing component sets it on any ancestor, or on the invocation itself through `class` or `style`. Custom properties inherit, so they reach the component across every boundary without selecting anything inside it.

A component never reaches into another component's internals. There is deliberately no `:deep()`: a selector into someone else's private structure couples the caller to it and breaks when that structure is refactored. What a component does not expose as a custom property is not part of its styling contract.

## Validity selectors

`:valid`, `:invalid`, and `:user-invalid` keep their native meaning. Scoping does not broaden them to ordinary elements. A component that needs form participation uses a native control as its root or inside its markup.

## Inheritance still crosses

Scoping constrains **selector matching**, not the cascade. Inherited properties (`color`, `font`, and custom properties such as design tokens) flow across every boundary above, into nested components and projected content alike, exactly as they do in ordinary light-DOM HTML. Authors get encapsulation of their *own selectors* while global theming, shared tokens, and the cascade keep working, which is the trade Shadow DOM refused to offer.

> [!note] Selector scoping preserves the cascade
> Vue and Svelte scoped styles, and Angular ViewEncapsulation.Emulated as the shipped default,[^3] won in practice over Shadow DOM because most authors want *scoping* (my selectors do not leak) and not *isolation* (nothing gets in or out). Shadow DOM, and Lit built on it, forces both.[^4] HTML Next makes scoping the default and treats isolation as the special case.

## Isolation: opt-in, later

Full isolation via a real shadow boundary [may]{.kw} be requested explicitly; it is never the default cost. A **later Level** specifies it as an *extension of Declarative Shadow DOM* driven by the template, closing the styling and form-participation gaps that kept authors away from Shadow DOM, rather than inheriting them.

## Open issues

- **Declared custom properties.** Whether a definition declares its public custom properties in `<defs>`, with a type and a default like a prop, so the customization surface is documented, typed, and checkable instead of being discovered from the stylesheet.

---

> [!note] How this is achieved is an implementation detail
> This page defines only the *behaviour*. How an implementation produces it is documented with that implementation. The model maps directly onto CSS `@scope`, whose **range** form (`@scope (root) to (limit)`) expresses the root-plus-lower-limit region above. A state test lowers to a token on a per-component `data-<tag>-state` attribute, written only for the names a definition's own stylesheet tests.

## References

[^1]: CSS Cascading and Inheritance Level 6, [@scope](https://www.w3.org/TR/css-cascade-6/#scoped-styles) (a style rule scoped to a subtree, with an optional lower limit forming a range).
[^2]: WHATWG HTML, [Declarative Shadow DOM](https://html.spec.whatwg.org/multipage/scripting.html#attr-template-shadowrootmode) (the opt-in isolation path).
[^3]: Scoped-style precedent: Angular [ViewEncapsulation.Emulated](https://angular.dev/guide/components/styling), its shipped default, is attribute-hash scoping with no shadow boundary; Vue [`<style scoped>`](https://vuejs.org/api/sfc-css-features.html#scoped-css) and [Svelte scoped styles](https://svelte.dev/docs/svelte/scoped-styles) are the same scoping-not-isolation approach.
[^4]: The isolation contrast authors avoided: Shadow DOM and Lit [component styles](https://lit.dev/docs/components/styles/) impose a real shadow boundary that also blocks shared theming and the cascade.
[^5]: CSS Scoping, [`:host`](https://www.w3.org/TR/css-scoping-1/#host-selector) and [`::slotted()`](https://www.w3.org/TR/css-scoping-1/#slotted-pseudo); the long-standing request to let `::slotted()` take complex selectors, [csswg-drafts #2425](https://github.com/w3c/csswg-drafts/issues/2425), and to make it a combinator, [#7922](https://github.com/w3c/csswg-drafts/issues/7922).
