---
title: Components & Composition
order: 4
blurb: <template component> · <defs> · slots · as
eyebrow: Declarative HTML Components Level 1 · external composition in Level 2
status: "Definitions, native roots, and slots: Level&nbsp;1 · external composition: Level&nbsp;2"
---

# Components & Composition

A component is **typed markup that lowers to a real native element**: no class, no registry, no lifecycle ceremony. This is HTML Next's answer to Web Components: native semantics stay the browser's, the interface is inspectable markup, and the same source compiles to idiomatic React, Vue, and Svelte.

## Definition: <template component>

A component is defined by a native `<template component="tag">`. There is no custom-element-shaped wrapper. The `<template>` is **inert** (browsers parse its contents into a `DocumentFragment` and render nothing), so a definition degrades to inert markup with no runtime today, and could be consumed natively if the shape were adopted, the way `<template shadowrootmode>` went from inert to browser-native for Declarative Shadow DOM.[^4] Inertness is the transition guarantee, not the end state. `template[component]` is also a cheap selector for the polyfill. Its direct children are an optional `<defs>` region (the interface and every non-rendered declaration), one markup root, and an optional `<style>`.

```html title="button.html"
<template component="x-button" status="early"
          summary="A native button with custom presentation.">
  <!-- <defs>: renders nothing. interface + behavior + data live here -->
  <defs>
    <prop name="variant" type="outline | solid | destructive | ghost"
          default="outline">Visual treatment.</prop>

    <state name="pending" :value="false">
    <handler name="press"><dispatch event="press"></handler>
  </defs>

  <!-- the visible markup: one native root, referencing the defs by name -->
  <button on:click="press"><slot></slot></button>
  <!-- styles are automatically scoped to this component (see Style scoping) -->
  <style>:host { box-sizing: border-box; }</style>
</template>
```

The interface is **declarative HTML**, not a data island. A `<prop>` states only what markup cannot already say: type, default, requiredness, description; its *target* is read from the `:attribute`/`.property` binding and the native element from the markup root, so neither is restated. The invocation tag comes from the `component` attribute; a single hyphen keeps it collision-safe against native elements without registering a custom element. A compiler lowers all of this to a normalized JSON contract as build output (CSP-safe, no `eval()`, inspectable by docs and tooling), but JSON is the compiled artifact, never the authoring form.

> [!note] The type grammar follows platform precedents
> Scalar keywords (`string`, `number`, `boolean`) mirror the CSS Values & Units data types `<number>`/`<string>`; the enum bar `outline | solid | destructive | ghost` is that spec's value-definition-syntax *“exactly one of”* combinator[^1]; `default` follows XML Schema's `default` attribute[^2]; `required` is the HTML boolean attribute of the same name[^3]; and a prop's description is its element text, as with `<option>`.

## Two regions: <defs> and the markup

A definition has two visibly separate parts, so a reader can tell at a glance what renders and what only describes behavior. Everything that produces no output, the `<prop>` interface declarations, reactive `<state>` and `<computed>`, read and write `<data>` resources, and `<handler>` blocks, lives inside a single `<defs>` region as flat siblings. Everything after it is the visible markup: the one native root and its `<slot>`s. The content stays pure markup that points at behavior by name; the behavior stays a small labeled list above it.

This mirrors the document's own `<head>`/`<body>` split, declarations and resources versus rendered content, applied fractally to a component. The name is borrowed from SVG, where `<defs>` already means exactly this: definitions that render nothing and are referenced by name from elsewhere.[^5]

> [!note] <defs> survives fragment parsing
> `<defs>` is an ordinary element in HTML content, so it round-trips intact through `outerHTML` and carries the intended definition-only meaning. The HTML fragment parser instead discards `<head>` and `<body>` wrappers inside a `<template>` and hoists their children out (verified against the reference implementation's parse5-based build).

## Native lowering and explicit root branches

A component [should]{.kw} lower to the native element named by `nativeElement`: a button component *is* a real `<button>`, so form association, focus, and accessibility are the browser's. Undeclared invocation attributes pass through to that root; owned template attributes and prop targets take precedence.

A polymorphic component declares `as` as an ordinary enum prop and selects between explicit native roots with `$match`. The prop does not retag an element: the definition contains the actual `<button>` and `<a>` branches that it may render.

```html
<template component="x-button">
  <defs>
    <prop name="as" type="button | a" default="button">Native root.</prop>
  </defs>

  <!-- Both possible native roots are visible in the definition. -->
  <template $match>
    <a $when="as = 'a'"><slot></slot></a>
    <button $else><slot></slot></button>
  </template>
</template>

<x-button>Save</x-button>                       <!-- → <button> -->
<x-button as="a" href="/save">Save</x-button>   <!-- → <a href> -->
```

> [!note] Conformance
> The selected branch [must]{.kw} produce exactly one significant root. Each branch carries its own native attribute surface, so generated framework types can narrow attributes from the `as` value: `href` belongs to the `a` branch, for example.

## Lowering, provenance & hydration

Lowering is **destructive and directional**. The `<template component>` is the definition and renders nothing; `<x-button>` is the *invocation* the author writes; lowering **replaces** the invocation with the definition's native root. The invocation tag does not survive: `<x-button>` becomes a real `<button>`, never `<x-button><button>…</button></x-button>`. Children land where the `<slot>` was, declared props map to their targets, and undeclared attributes pass through.

```html
<!-- definition: written once, inert, renders nothing -->
<template component="x-button">
  <button><slot></slot></button>
</template>

<!-- invocation: what you write on the page -->
<x-button variant="solid">Save</x-button>

<!-- output: identical whether lowered on the server or in the browser -->
<button data-component="x-button" data-variant="solid">Save</button>
```

> [!norm] Determinism: one DOM, either path
> Lowering [must]{.kw} be a deterministic function of the invocation and the definition alone: no timestamps, generated ids, or client-only state. The converter running on the server and the polyfill running in the browser therefore produce **byte-identical** native DOM for the same source, so an SSR'd root and an in-browser-lowered root are indistinguishable. This is the equivalence contract applied to a single node.

Every lowered root carries one provenance attribute, `data-component`, injected by the implementation rather than authored. Its value is a **space-separated token list**, outermost invocation first, exactly like `class` or `rel`: a component that lowers straight to a native element carries a single token (`data-component="x-button"`), and one whose root is another component carries the whole lineage (`data-component="x-primary x-button"`). Each token is a component tag, so it resolves through the ordinary component registry, the loaded `<template component>` definitions keyed by tag, exactly the way `customElements` resolves a custom-element tag to its definition; no separate provenance format exists or is needed. Because it is deterministic, the stamp is identical under SSR and in-browser, and it composes across nested components and imported partials. How server output records slot boundaries and content no slot renders yet, so hydration rebuilds the same instance, is defined in [Rendered form & hydration](/html-next/rendered-form). Content projected through a `<slot>` is the consumer's, not the component's, so it keeps whatever provenance it already had and is never re-stamped as the enclosing component.

Alongside `data-component`, every **serializable prop** is reflected on the root as `data-<name>` carrying its effective value (passed or default). The two together make the invocation **fully reconstructable from the DOM**: `data-component` names which component, the `data-*` attributes carry what it was invoked with, so replacing `<x-button>` with a native `<button>` loses no information. The attribute string plus the prop's declared type round-trips losslessly, so no separate value channel is needed; structured (object/array) props are bound by reference and carried as JSON in the payload instead of reflected per-attribute. Reflection is uniform even when a prop also maps to a native attribute, so `data-*` is always the complete record. See [Types](/html-next/types).

The stamp is also what makes hydration an **adopt-in-place**, not a rebuild. An implementation lowers where it finds an `<x-button>` invocation, and *adopts* where it finds an already-lowered `[data-component]` root: it binds reactivity and events onto the existing node instead of recreating it. An SSR'd tree therefore hydrates with no replacement and no flicker, and a client-only page lowers to the same result. The only difference is a pre-lowering moment that exists only client-side, where the unknown `<x-button>` shows its children inline; SSR skips it.

## Slots

Content projection uses the native-shaped `<slot>`. Level&nbsp;1 includes default, named, fallback, and scoped slots because all four are part of the baseline component contract.

### Named & fallback

```html
<!-- definition -->
<template component="x-card"> …
  <article>
    <header><slot name="title">Untitled</slot></header>   <!-- fallback content -->
    <slot></slot>                                          <!-- default slot -->
  </article>
</template>

<!-- use -->
<x-card>
  <h2 slot="title">Quarterly report</h2>
  <p>Body content lands in the default slot.</p>
</x-card>
```

### Scoped slots

A slot may expose data to the content projected into it. The definition binds slot props on the `<slot>`; the consumer supplies a `<template slot="name">` whose **scope is those exposed props**: no new prefix, consistent with `$with`-style scoping.

```html
<!-- definition: a list that owns iteration, slots each row out -->
<slot $each="row of rows" $key="row.id" name="row" :item="row" :index="loop.index"></slot>

<!-- use: the template's scope is { item, index } -->
<x-list :rows="people">
  <template slot="row"><td $value="item.name"></td></template>
</x-list>
```

## Composition

### <template src>: import a component or partial

Native `<template>` has no `src`, so HTML Next defines it: `<template src="…">` loads an external component definition or partial. It is the import mechanism and the hook for lazy, code-split components. With no runtime it degrades to an empty inert template, safe.

```html
<template src="./card.html"></template>        <!-- register x-card -->
<template src="./chart.html" defer></template>  <!-- lazy: load on first use -->
```

### <component is>: dynamic component

When the component to render is decided at runtime, `<component is="expr">` resolves the tag from an expression, the name and syntax taken verbatim from Vue `<component :is>` (Svelte `<svelte:component>` and Angular `NgComponentOutlet` are the same idea).[^8] Props and children pass through as with a literal invocation.

```html
<component is="block.type" :data="block"></component>
```

### <portal to>: render elsewhere

Overlays (dialogs, tooltips, toasts) render outside their DOM position while staying logically owned by the component. `<portal to="selector">` moves its children to the target (a CSS selector or an element id) while preserving reactive bindings and event wiring. The term is React `createPortal`; Vue `Teleport` was originally named `<portal>`, and Angular CDK ships a `Portal` too.[^9]

```html
<portal to="body">
  <dialog open><slot></slot></dialog>
</portal>
```

## Registration & loading

An `<x-button>` invocation has to resolve to a definition. There are three ways to make one known, in ascending scope:

1. an inline `<template component>` in the document;
2. `<template src="./x-button.html">`, the inline import above;
3. a document-level `<link rel="component">` whose `href` is either a live URL or a package specifier.
{.algo}

### One import form, live or packaged

The application names the concrete component files it directly uses. A same-origin URL-like `href` (`./` or `/`) stays **live project source**: the runtime fetches that definition and follows its declared component and controller edges. A bare `href` is a **package subpath**: an install/build resolves that exact exported HTML file through package metadata, while a no-build live application resolves it through its own import map. Every path selects the same definition and preserves the same dependency graph:

```html
<!-- First-party source: an ordinary URL, fetched at runtime. -->
<link rel="component" href="./components/dashboard.html">

<!-- Installed package: a concrete exported package subpath. -->
<link rel="component" href="@acme/ui/dashboard.html">
```

A package exposes concrete component files with the ordinary `package.json` `exports` field. It needs no HTML Next manifest and no registration script:

```html title="node_modules/@acme/ui/package.json"
{
  "name": "@acme/ui",
  "exports": {
    "./*.html": "./components/*.html"
  }
}
```

The build resolves `@acme/ui/dashboard.html` to that file, then statically walks its declared edges. A dashboard definition might link `./chart.html`; that definition's carrier might declare `controller="./chart.js"`; the controller's static imports complete the statically visible JavaScript side. No step executes code to discover dependencies, and no generated manifest hides them. Development may serve those files directly; production may inline, copy, rewrite, or bundle them while preserving their meaning.

> [!norm] Definitions declare; applications resolve
> A component definition contains only its reusable dependency facts. It never contains an approval flag, consumer allowlist, deployment URL, or consumer-specific hash. Relative references travel with the definition. Bare references are resolved by the consuming application's ordinary import map or package build. Installing or directly importing a packaged root is the application's trust decision; the definition is identical whether it is consumed from a package, a build output, or a live URL.

> [!note] The separate live trust path
> A no-build page may map one package prefix to a versioned CDN directory through the ordinary import map `imports` table[^6]. That application-owned prefix is both the resolver and the boundary for declarative definition edges: relative component links and carrier controller references may stay within it, while an edge outside it must use another bare specifier the application maps. Imported definitions cannot contribute import maps or widen a prefix. Once a trusted controller runs, its own imports are ordinary ESM governed by CSP rather than a directory sandbox; [Security](/html-next/security) defines that boundary precisely.

```html
<script type="importmap">
{
  "imports": {
    "@acme/ui/": "https://cdn.example/@acme/ui@4/components/"
  }
}
</script>
<link rel="component" href="@acme/ui/dashboard.html" crossorigin>
```

For live loading, `<link rel="component">` retains the normal fetch vocabulary: `integrity`, `crossorigin`, `referrerpolicy`, `type`, and `fetchpriority`. Packaged output normally relies on the package lock and same-origin content-hashed assets. For a stricter live deployment, tooling can crawl the same static graph and generate the application's URL-keyed integrity metadata; component authors do not calculate or embed deployment hashes.

### Resolution

All of these forms feed one document-level registry keyed by tag; when the parser meets `<x-button>` it looks the tag up there. A tag [must]{.kw} have exactly one definition in a document. Declaring the same tag more than once, inline or by pointer, is a conformance error rather than last-wins, so resolution stays deterministic.

A definition that composes other components [should]{.kw} carry its own `<link rel="component">` edges, normally as relative URLs inside one live location or package. If it needs imperative behavior, its carrier declares one `controller` specifier. The complete HTML-to-HTML-to-JavaScript graph is therefore discoverable by a static walk, without relying on the consuming document to reconstruct it or executing a package entry point.

### Imported definitions are inert

`<link rel="import">` (HTML Imports)[^7] defined an imported `Document` graph together with its own parser-blocking, script-ordering, style-ordering, deduplication, `currentScript`, and custom-element processing rules. The later [HTML Modules proposal](https://github.com/WICG/webcomponents/blob/gh-pages/proposals/html-modules-proposal.md) explicitly identified global-object pollution and parse blocking among the problems and attempted to move the graph into ES modules. HTML Next keeps component definitions declarative and gives their one optional imperative edge to the existing ES-module loader.

A component definition is **declarative and script-free**. Its only children are an optional `<defs>` region, one markup root, and an optional `<style>`; it [must not]{.kw} contain an executable `<script>`, inline event handlers, or anything requiring `eval()`, and bindings use a restricted pure expression language rather than ambient JavaScript. So importing a definition is a pure fetch, parse, and register: no code executes, no globals are shared, and there is no lifecycle to order. Registration is idempotent, deduplicated by tag, with a duplicate tag a conformance error, precisely because there are no script side effects to double-run.

> [!norm] Definitions stay declarative
> The definition is declarative and script-free, its reactivity lowers and compiles, and the **ES module system** is reserved for genuine imperative behavior at a later level, the only part with a real lifecycle. Code lives in the module graph while the component definition remains data.

> [!note] The upstream surface stays small
> The component-loading proposal needs `rel="component"`, external `<template src>`, and application of the existing module-specifier resolution algorithm to bare component references. It does not require a new import-map section, a global tag manifest, or a second package metadata format.

## Roots: native or delegated

A component has **exactly one significant root**. That single root is what gives it one native element and one place for its provenance stamp, so the rule earns its keep. The root may take either shape, and neither introduces a wrapper:

1. a **native element**, the common case: the component lowers straight to it, and `nativeElement` is that tag; a polymorphic definition uses explicit conditional branches whose selected arm provides the native root;
2. another **component invocation** (*delegation*): the component has no native element of its own and lowers to whatever the delegated component lowers to, so a preset such as `x-primary` is built as an `x-button` with a fixed variant.
{.algo}

Delegation still resolves to a single native element, transitively through the chain and with a cycle a conformance error, and it loses no provenance because `data-component` is a token list, outermost first:

```html
<!-- delegation: a preset built from another component -->
<template component="x-primary">
  <x-button variant="solid"><slot></slot></x-button>
</template>

<x-primary>Save</x-primary>

<!-- lowers to a single native button, with the lineage preserved -->
<button data-component="x-primary x-button" data-variant="solid">Save</button>
```

A delegating component forwards like any other lowering: its own declared props are applied through the bindings in its markup, template-owned attributes (here `variant="solid"`) take precedence, and any undeclared invocation attributes pass through to the delegated root and continue down the chain. Its `nativeElement` and native attribute surface are whatever the chain ultimately resolves to, so its generated types inherit that surface.

> [!note] Fragments are a later level
> A component that must emit several siblings (list items, table rows, `<option>`s inside a `<select>`) needs a **fragment root**: an explicit declaration that produces multiple nodes and lowers to each target's fragment form. It relaxes the one-root rule in a controlled way and is deferred to a later Level rather than allowed ad hoc, so Level 1 keeps the clean single-root, single-stamp model.

## Element reference

::: {.entry name="<template component>" role="component definition"}
Attributes
: `component`: the invocation tag (hyphenated, collision-safe) · optional `controller`: one relative, URL-like, or bare ES-module specifier · optional `status`, `summary`.

Children
: an optional `<defs>` region, one markup root, optional `<style>`.

Semantics
: Inert native template (as `<template shadowrootmode>` was before native adoption); parsed to a fragment; renders nothing without a runtime.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<defs>" role="non-rendered declarations"}
Contains
: `<prop>`, `<state>`, `<computed>`, `<data>`, `<handler>` as flat siblings — everything that renders nothing.

Semantics
: Separates behavior/data/interface from visible markup; borrowed from SVG `<defs>`. Survives the template fragment parser where `<head>`/`<body>` do not.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<prop>" role="component interface declaration"}
Attributes
: `name` · `type` (scalar keyword or `a | b | c` enum) · `default?` · `required?`

Content
: the prop description (element text)

Placement
: a flat child of `<defs>` (no `<props>` wrapper); the public interface is the set of `<prop>` elements there

Inferred
: target from the first `:attribute`/`.property` binding; not restated on the prop. A prop may be bound in more places; those only render it.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="data-component" role="provenance stamp (output)"}
Value
: space-separated token list, outermost invocation first (`x-primary x-button`); a single token for a native-root component

Emitted by
: the implementation on every lowered native root; not authored

Resolves via
: the component registry, the loaded `<template component>` definitions keyed by tag (like `customElements`)

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<slot>" role="content projection"}
Attributes
: `name?` (named slot) · `:prop` bindings (scoped-slot data)

Children
: fallback content used when nothing is projected

Level
: [L1]{.pill .l1} · default, named, fallback, and scoped slots
:::

::: {.entry name='<link rel="component">' role="component entry import"}
Attributes
: `href`: URL-like live entry or bare package specifier · fetch vocabulary: `integrity`, `crossorigin`, `referrerpolicy`, `type`, `fetchpriority`

Semantics
: import one direct component file and its statically declared dependency closure; package specifiers resolve through ordinary package/import-map resolution

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<template src> · <component is> · <portal to>" role="composition"}
Semantics
: import/lazy-load a definition · render a runtime-chosen component · relocate children while preserving bindings

Level
: [L2]{.pill .soon}
:::

## Sources

[^1]: CSS Values and Units Level 4, [value definition syntax](https://www.w3.org/TR/css-values-4/#component-combinators) (scalar keywords and the `|` “exactly one of” bar).
[^2]: W3C XML Schema, [the `default` attribute](https://www.w3.org/TR/xmlschema11-1/#cvc-au) on element declarations.
[^3]: WHATWG HTML, [boolean attributes](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#boolean-attributes) (e.g. `required`) and [the `<option>` element](https://html.spec.whatwg.org/multipage/form-elements.html#the-option-element) (text content as label).
[^4]: WHATWG HTML, [Declarative Shadow DOM](https://html.spec.whatwg.org/multipage/scripting.html#attr-template-shadowrootmode) (`<template shadowrootmode>`, inert to native).
[^5]: SVG 2, [the `<defs>` element](https://www.w3.org/TR/SVG2/struct.html#DefsElement).
[^6]: WHATWG HTML, [import maps](https://html.spec.whatwg.org/multipage/webappapis.html#import-maps) (unrecognized top-level keys are ignored).
[^7]: W3C (retired), [HTML Imports](https://www.w3.org/TR/html-imports/) (`<link rel="import">`).
[^8]: Dynamic component, borrowed directly: Vue [`<component :is>`](https://vuejs.org/api/built-in-special-elements.html#component) (name and syntax verbatim), Svelte [`<svelte:component>`](https://svelte.dev/docs/svelte/svelte-component), and Angular [NgComponentOutlet](https://angular.dev/api/common/NgComponentOutlet).
[^9]: Render-elsewhere, borrowed directly: React [createPortal](https://react.dev/reference/react-dom/createPortal) (the term) and Vue [Teleport](https://vuejs.org/guide/built-ins/teleport.html) (originally named `<portal>`), plus Angular CDK [Portal](https://material.angular.io/cdk/portal/overview).
