---
title: Declarative HTML Components
order: -1
layout: proposal
eyebrow: HTML Next · Proposal
stamp: Unofficial Editor's Draft · Stage&nbsp;0
---

# Declarative HTML Components Level 1

A markup-first component model that compiles to, and polyfills on, the web platform.

- [Start with Overview →](/html-next/overview)
- [See Examples →](/html-next/examples)
- [Browse Chapters ↓](#chapters)

Editors
: Next Web Working Group

Reference implementation
: `html-next` repo · polyfill & component bridge

Status
: Unofficial Editor's Draft · Stage 0. Not a W3C or WHATWG deliverable.

## Status of this document {.sotd}

An **unofficial editor's draft** for discussion at Stage&nbsp;0. It is **not** a standard and does not represent the position of the W3C, the WHATWG, or any browser vendor.

This document specifies the component-authoring proposal in the [HTML Next collection](/#html-next). It defines an *authoring layer* above the platform today, with the explicit aim that proven features are **adopted into the platform** through the normal standards process. Everything normative here currently constrains conforming tooling; that boundary would move as features graduate.

## Abstract

**Declarative HTML Components proposes a reliable, reactive component-authoring model for HTML.** The platform gained a rendering engine, a networking stack, and a component *mechanism*, but never an **application authoring model**, so for fifteen years the primitives authors need most (reusable typed components, control flow, data sources, reactivity) were reinvented, incompatibly, in one JavaScript framework after another. This proposal expresses those primitives **as markup**, so the web gains a standard component layer that degrades to plain HTML and outlives any single framework. {.lede}

**In plain terms:** you write components, control flow, and reactivity *as HTML*, and run the same file in the browser or compile it to React, Vue, or Svelte, with no build step and no `eval()`.

```html
<!-- You write a component as markup -->
<x-button variant="solid">Save</x-button>

<!-- It becomes a real native button — no wrapper, no shadow root -->
<button data-component="x-button" data-variant="solid">Save</button>
```

You author a component once, as literal browser-parseable HTML with an inert typed contract. A conforming implementation lowers it into idiomatic Vanilla&nbsp;DOM, React, Vue, and Svelte, or interprets the same source directly in Chromium, Firefox, and WebKit. One semantics, many backends.

## Introduction & goals

### The missing layer

The web platform kept advancing: `fetch`, Grid, ES modules, even Custom Elements and Shadow DOM. Yet HTML's own vocabulary for *building applications* barely grew. The primitives an app author reaches for every day were never added to markup, so the same wheel was reinvented, again and again and incompatibly, in userland. Ask HTML, natively, for any of these and the answer is still "load a framework":

| Application need | Native HTML answer | What everyone does |
| --- | --- | --- |
| Reusable typed component with a documented API | None (Custom Elements are untyped, imperative) | React/Vue/Svelte component |
| Conditional & repeated markup | None | `v-if`, `{#each}`, `.map()` |
| Declarative reactivity | None | hooks, refs, runes, signals |
| Bind a control to state | None | controlled inputs, `v-model` |
| Declare a data dependency | None | fetch-in-effect, loaders, resources |

Every cell in the right column is an incompatible *language*. Web Components addressed packaging and skipped the language problem: a place to *put* a component but no declarative way to *write* one.

### Use the platform

The goal is to **use the platform** as much as possible. Each feature starts from real HTML and CSS patterns and from existing DOM interfaces: a component lowers to a native element, styles are scoped with CSS `@scope`, validity follows the Constraint Validation API, and events are DOM events. Where the platform has no pattern to draw on, the proposal adopts the shape that popular libraries have repeatedly and independently arrived at, such as conditional and repeated markup, two-way binding, and typed props, rather than inventing a new one.

### The component model

A [markup-first authoring language]{.dfn} realized by two kinds of conforming implementation that [must]{.kw} produce observably equivalent output:

::: two

> [!ex] The converter
> An ahead-of-time compiler lowers HTML Next to idiomatic Vanilla&nbsp;DOM, React, Vue, Svelte, CSS, contracts, and docs: a multi-target converter in the spirit of Mitosis.

> [!ex] The polyfill
> A browser runtime reads the same source, lowers it against the live DOM without Custom Elements or dynamic code, and subscribes to its declared dependency graph.

:::

The proposal is both an authoring layer you can **use today**, through the [converter and polyfill](https://github.com/nextwebwg/html-next), and a set of **platform features** meant to graduate into HTML itself, feature by feature, the way Declarative Shadow DOM and invoker commands went from userland shim to shipped native syntax.

The proposal is **purely additive markup**. You add one feature to an ordinary HTML file, one tag at a time, and everything else stays exactly as it was. A plain HTML file already satisfies the language, so adoption requires no file-format rewrite.

### How the proposal versions

There is no single umbrella version, no big-bang *HTML&nbsp;Next&nbsp;1.0*. The project versions the way the platform itself does today, on three borrowed axes:

::: two

> [!note] Levels, from CSS
> CSS specifications advance by **Level** (Selectors&nbsp;4, Color&nbsp;5, Grid&nbsp;2): each Level is a complete specification that extends the one before. Declarative HTML Components is one such specification, and this draft is **Level&nbsp;1**. Its chapters are parts of one component model, so they advance together.

> [!note] Stages, from proposals
> HTML is a **Living Standard**; new features incubate as **proposals** (WICG explainers), and JavaScript proposals move through **TC39 stages**&nbsp;0 to 4. This proposal is at **Stage&nbsp;0** today; maturity is a stage, not a number announced in advance.

:::

> [!norm] A snapshot is the published version
> A dated **snapshot** is the draft as published on that day, at its Level. It records what the proposal contains on that date; the working draft keeps moving.

**The worked example is Web Components.** The Level&nbsp;1 chapters (components, templating, reactivity, scoping) provide a practical component authoring model today. The parts a compiler cannot supply, including native-element extension and deeper Shadow DOM integration, belong in later upstream platform proposals.

## What declarative components need

A complete component-authoring model needs reactivity, style scoping, and reliable native semantics. This proposal addresses each in its own chapter. Components lower to real native elements **today**; live reactivity and style scoping build on that; deeper platform integration remains upstream standards work. {.lede}

::: fix

### Reactivity

A dependency graph you can read, type, and lower, not a runtime you're married to.

##### Why it's broken

- HTML has *no* declarative reactivity, so every framework invented its own (VDOM diffing, proxies, compilers, signals), and they don't interoperate.
- Reactivity is expressed in framework-specific JavaScript, not markup: it can't be inspected, typed once, or ported.
- Most runtime approaches need dynamic code (`new Function`) or ship a diffing engine to every user.

##### This proposal's answer

- Reactivity is a **declarative dependency graph** in markup: `<state>`, `<computed>`, `<data>`, and `:`/`bind:` bindings over a small pure expression language.
- The graph is **statically analyzable**: dependencies are read off the parsed expression, not discovered at runtime.
- One semantics, many backends: it lowers to React state, Vue refs, Svelte runes, or a signal-based browser runtime. **No `eval`**, CSP-clean.

:::

::: fix

### Web Components

The platform's own component mechanism is broken in ways a compiler cannot repair. A polyfill routes around it today; the platform-level fix is an upstream proposal.

##### Why it's broken

- No portable way to extend a native element: customized built-ins (`is=`) are formally opposed by WebKit, so `extends HTMLButtonElement` has no cross-browser path.[^2]
- The autonomous alternative, an `<x-button>` host, forfeits the native button's form submission, role, and focus, rebuilt by hand.
- Form participation dies at the shadow boundary; it needs `ElementInternals`, which stabilized cross-browser only in 2023.[^6]
- Imperative ceremony, string-only props with no inspectable contract, and cross-boundary styling friction round it out.[^1]

##### Polyfill today, platform change upstream

- HTML Next needs custom elements **not at all**: templating and native lowering emit a **real `<button>`**, so native semantics stay the browser's.
- The component is **typed markup with a declarative contract** and compiles to idiomatic React, Vue, and Svelte: portable, not a walled garden.
- What a compiler cannot fix (WebKit's refusal of customized built-ins, form association across a boundary) is platform work for a later Level and an **upstream proposal**.
- Its likely shape: templating that opts into an **extension of Declarative Shadow DOM**, closing the styling and form gaps DSD left open.

:::

::: fix

### Shadow DOM & scoping

Styles scoped to the component without a shadow boundary, so you stop paying the isolation tax you never wanted.

##### Why it's broken

- Shadow DOM gives all-or-nothing encapsulation. Styling across the boundary is painful (`::part`, `::slotted`); global theming and shared styles fight it.
- Declarative Shadow DOM and its SSR story arrived years late and remain awkward.
- Forms, focus, and accessibility relationships behave surprisingly across the boundary.
- Most authors want *scoping*, not *isolation*, and are forced to take both.

##### This proposal's answer

- **A component's styles are scoped to it by default**: its `<style>` affects only its own markup, not the whole page, and with no shadow boundary, the scoping the browser already offers with CSS `@scope`. Encapsulation without isolation.
- Degrades to plain CSS in the light DOM: theming, cascade, and shared design tokens keep working.
- Real isolation becomes an **opt-in target capability**, never the mandatory tax Shadow DOM makes it today.
- A **later Level** takes the isolation case further with an **extension of Declarative Shadow DOM** that fixes DSD's styling and form-participation gaps instead of inheriting them.

:::

### The record: Web Components in practice {#the-record}

Whether Web Components failed by design or only because they were never fully leveraged does not matter to an author choosing a component model today. In their shipped form they did not become the web's component layer, and the clearest evidence is the ecosystem's own behavior.

::: record

#### Champions retreated

The flagship "components will replace frameworks" project was wound down.

Google's Polymer entered maintenance mode in 2018 and was superseded by Lit (a thin rendering helper) because raw custom-element ergonomics were not enough on their own.[^8]

#### Framework authors opted out

The people who build component models did not build them on this one.

The creator of Svelte set out in 2019 why he does not use Web Components: Shadow DOM forces CSS into JavaScript; the property/attribute split forces boilerplate; slotted content renders eagerly; the registry is one global namespace; and the DOM is "an awkward interface for building interactive applications."[^1] React, Vue, Svelte, and Solid each built their own model instead.

#### The extension mechanism is blocked

There is no cross-browser way to extend a native element.

Customized built-in elements ship in Chromium and Firefox, but WebKit's formal standards position is to *oppose* them and not implement them.[^2][^3] The only spec-sanctioned route to reusing native semantics has no portable path.

#### Interop lagged a decade

The largest UI library could not talk to them properly until 2024.

For most of the feature's life React could not pass an object or array to a custom element, nor listen to its events; the gap was tracked on Custom Elements Everywhere. Full support arrived only in React 19, December 2024, more than a decade after custom elements were proposed.[^4][^5]

#### Forms and SSR arrived late

The basics took ten years to stabilize.

Form participation via `ElementInternals` stabilized cross-browser only with Safari 16.4 (March 2023); Declarative Shadow DOM reached Safari in 16.4 and Firefox in 123 (2024).[^6][^7]

:::

## Architecture

### Three kinds of element

The proposal keeps three layers distinct: authoring syntax, generated output, and the runtime or compiler that connects them.

::: targets
Control-flow directives
: $each $if $match

Component elements
: <x-button>

Output elements
: <button> <input>
:::

### Conforming implementations

Declarative HTML Components is a language specification: an implementation is a **converter** or a **polyfill**. Its governing conformance contract is [observable equivalence]{.dfn}: the same native DOM, state, events, accessibility, and errors for the same source.

::: flow
- Declarative component source {.acc}
- converter
- Vanilla / React / Vue / Svelte + CSS + docs
:::

> [!note] Specification and implementation
> The **Next Web Working Group** publishes the proposal and this site. The [**`html-next` implementation repository**](https://github.com/nextwebwg/html-next) contains the current polyfill and converter. As more proposals gain implementations, each will have its own package over shared infrastructure.

> [!norm] Static output is the baseline
> Progressive enhancement runs the other way from a hypermedia library: in htmx the server round-trip is the baseline and script enhances it; in HTML Next the **rendered HTML is the baseline** and the browser enhances it. A server-rendered page delivers its initial content as ordinary HTML that displays, is accessible, and is indexable with no JavaScript.
>
> How far past that first render a no-JavaScript page reaches depends on the *kind* of reactivity:
>
> - **State that maps to a native primitive** (a toggle to `<details>` or `popover`, selection to `:checked`, validity to constraint validation, relational reactivity to `:has()`) lowers to HTML and CSS and keeps working with no script.
> - **Genuinely dynamic reactivity** (data fetches, values computed over live input, lists over changing data) needs the runtime, or a server-round-trip fallback that is still open.
>
> So the guarantee is a no-JS **render**, and a no-JS *application* exactly as far as the reactivity has a native lowering.

## Conformance & Levels

Keywords follow RFC&nbsp;2119, scoped to HTML Next tooling. A tool [must]{.kw} emit an explicit unsupported-feature diagnostic, never silent literal fallback, for any construct above its level.

| Area | Level 1: normative today | Direction |
| --- | --- | --- |
| **Components** | Typed native-root components; default, named, fallback, and scoped slots; explicit polymorphic roots. [Shipping]{.pill .l1} | [L2]{.pill .inc} external imports and dynamic composition |
| **Targets** | Vanilla, React, Vue, Svelte, CSS, docs. [Shipping]{.pill .l1} | [L2]{.pill .inc} SSR, static/email |
| **Browser runtime** | One-shot lowering, no Custom Elements, no eval. [Shipping]{.pill .l1} | [L2]{.pill .inc} reactive updates |
| **Templating** | None yet | [L1]{.pill .l1} `$each`, `$if`, `$match`, `<value>` |
| **Reactivity** | None yet | [L1]{.pill .l1} state, computed, data |
| **Forms** | Native ownership, validation, submission, and submitter overrides. | [L2]{.pill .inc} expanded methods and composable submission scopes |
| **Types** | `string`, `boolean`, `number`, `enum`. | [L3]{.pill .soon} URLs, colors, refs, content models |
| **Isolation** | None yet | [Upstream]{.pill .inc} Declarative-Shadow-DOM extension; native-element extension upstream |

::: {#chapters}

## Chapters

The specification is one document in chapters, and it advances as a whole through Levels. Overview and Examples are reading guides, listed separately above.

::chapter-index

:::

## Adoption

A spec convinces no one; four things do, in order.

::: two

> [!ex] 1 · It runs today
> Author one component; compile it to the framework you already ship, *and* polyfill it in the browser with no build. Adoption risk is one file, not a rewrite.

> [!ex] 2 · It deletes a problem
> Each fix is a grievance a developer already has: reactivity lock-in, Custom Element ceremony, Shadow DOM pain.

> [!ex] 3 · It's just HTML
> No new mental-model tax: it reads like markup, survives the parser, and works under CSP. A component invocation even degrades to its inline children before any runtime runs.

> [!ex] 4 · A demo and a name
> One jaw-drop demo (one file → five targets + live browser) and a name that promises the next HTML.

:::

## Governance & the working group

The **Next Web Working Group** exists today as a GitHub organization. The path to a recognized standards venue, cheapest rung first:

1. **The org is the specs and the site.** Publishes standards; ships no tooling.
2. **A separate implementation repository**, [`html-next`](https://github.com/nextwebwg/html-next), organized into proposal-specific packages as implementations are added.
3. **An explicit stage process**, proposal → incubation → Level&nbsp;N, modeled on TC39 stages and WHATWG workstreams.
4. **A Community Group listing** for legitimacy without W3C membership.
5. **Upstream the wins.** A mature feature's endgame is a proposal into WHATWG/CSSWG/TC39.
{.algo}

## Open questions

Genuine design questions, not yet settled:

| Area | Question |
| --- | --- |
| Imports | Component-definition and registry-scoping syntax; untrusted-import trust model. |
| Data | Request, caching, cancellation, concurrency, and stale-response semantics. |
| Rendering | SSR serialization, hydration ownership, no-runtime fallback, static/email targets. |
| Expressions | `and`/`or`/`not` vs. `&&`/`\|\|`/`!`; missing-data value; object/list literals; safe navigation. |
| Reactive scheduling | Browser scheduling, teardown, and dynamic-index dependency breadth. |
| Parser contexts | SVG, MathML, table, and select insertion modes. |
| Extension | How consumers extend the element and type vocabulary; capability negotiation. |

> [!note] Prior art, credited
> Shopify Liquid (constrained template language, filter pipelines), Squarespace JSON-T (data-context-first templating), Vue & Svelte (markup-first components, scoped styles, browser-safe binding syntax), Mitosis (one source → many framework targets), and XSLT (declarative tree transformation) are inputs and evidence; none is adopted as the default answer.

## References

Informative. Retrieved September&nbsp;2026; standards positions and browser versions as published.

[^1]: **Rich Harris.** "Why I don't use web components." DEV, 20&nbsp;June&nbsp;2019. [dev.to/richharris/why-i-don-t-use-web-components-2cia](https://dev.to/richharris/why-i-don-t-use-web-components-2cia)
[^2]: **WebKit.** Standards position on customized built-in elements: *oppose*. Issue&nbsp;#97, 2022. [github.com/WebKit/standards-positions/issues/97](https://github.com/WebKit/standards-positions/issues/97)
[^3]: **WebKit Bugzilla&nbsp;182671.** "Implementation (or not) of customized builtins." [bugs.webkit.org/show_bug.cgi?id=182671](https://bugs.webkit.org/show_bug.cgi?id=182671)
[^4]: **Custom Elements Everywhere.** Framework interoperability tests. [custom-elements-everywhere.com](https://custom-elements-everywhere.com/)
[^5]: **React&nbsp;19.** Full custom-elements support, December&nbsp;2024. [react.dev/blog/2024/12/05/react-19](https://react.dev/blog/2024/12/05/react-19)
[^6]: **WebKit.** "ElementInternals and Form-Associated Custom Elements" (Safari&nbsp;16.4, 2023). [webkit.org/blog/13711](https://webkit.org/blog/13711/elementinternals-and-form-associated-custom-elements/)
[^7]: **WebKit.** "Declarative Shadow DOM" (Safari&nbsp;16.4; Firefox&nbsp;123, 2024). [webkit.org/blog/13851](https://webkit.org/blog/13851/declarative-shadow-dom/)
[^8]: **Lit.** "Lit for Polymer users": Polymer superseded by Lit; in maintenance since 2018. [lit.dev/articles/lit-for-polymer-users](https://lit.dev/articles/lit-for-polymer-users/)
