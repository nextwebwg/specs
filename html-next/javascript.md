---
title: The JavaScript Layer
order: 6
blurb: controllers · host · $ref · finding elements · effects
eyebrow: Declarative HTML Components · reserved for Level 2
status: Proposed direction · the imperative escape hatch
---

# The JavaScript Layer

Almost everything is declarative, and a component definition holds **no script at all**. When behavior genuinely needs imperative JavaScript, a timer, a stream, an observer, a foreign library, it lives in an ordinary **ES module** outside the definition and attaches through a small, native-grounded seam: a **controller** declared by the component definition. The definition stays pure data; the module stays pure behavior; they meet only at the contract.

## Imperative behavior uses controllers

The declarative layers, templating, bindings, and reactivity, cover the large majority of interface work with no script. But some behavior is irreducibly imperative: a `setInterval` clock, a Server-Sent-Events stream, an `IntersectionObserver`, wrapping a mapping or charting library, or computation too involved for a [pure expression](/html-next/expressions). That work needs JavaScript, and pretending otherwise would push authors back into inline handlers and `eval`-shaped escapes.

So HTML Next draws a firm line. A **component definition is declarative data**: no `<script>`, no inline handlers, importable and inspectable without executing anything, and renderable on a server. Imperative JavaScript is a **separate concern** in an ordinary ES module. The two never fuse; they meet at a named seam.

> [!norm] Server rendering supplies the declarative baseline
> The JavaScript layer only *enhances*: a controller adds live imperative behavior on top and is never load-bearing for the first render. But be precise about what "no JS" delivers, because it depends on where the markup comes from. On a **server-rendered** page the first render is real HTML that displays, is accessible, and is indexable with no script; a controller failing to load leaves that baseline intact. On a **client-only** page there is no such baseline: an invocation like `<x-app>` is an unknown element, so without the runtime it renders *nothing* (its inline children, if any, are all that shows). So the guarantee is: **no-JS renders the declarative baseline when the HTML was server-rendered**; client-only pages need the runtime to produce first paint. Determinism and adopt-in-place hydration are likewise SSR properties (see [Components](/html-next/components)), not client-only ones.

## The controller

A component that needs imperative behavior gets a **controller**: the default-exported function from the ES module named by the component definition, run once per instance. It is the decoupled equivalent of a custom element's class plus its `ElementInternals`[^1], the same behavior a Web Component would put in a class, attached instead to a definition made of data.

::: two

```html title="x-map.html"
<!-- x-map.html: declarative data plus its optional controller dependency. -->
<template component="x-map" controller="./x-map.js">
  <defs>
    <state name="center" :value="[0, 0]">
  </defs>
  <div $ref="canvas"></div>
</template>
```

```js title="x-map.js"
// x-map.js: an ordinary ES module, the imperative controller for <x-map>.
// No HTML Next package import is required: the definition already names this module.
export default function controller(host) {
  let map;
  host.effect(() => {
    map ??= new MapLib(host.refs.canvas);                // recreated after a reconnect
    map.setCenter(host.state.center);                    // re-runs whenever center changes
  });
  host.on("disconnect", () => { map?.destroy(); map = undefined; });
}
```

:::

The controller is written against the small `host` interface and exported as the module's default. The platform already knows the tag from the definition that named the module, so the controller neither imports an HTML Next library nor repeats the tag in a registration call. That contract lets the same source run under a native implementation, today's polyfill, or a framework target (below). It is a portability contract, **not a security boundary**: an ES module can still use `window`, `document`, storage, network APIs, and anything else page JavaScript can reach.

> [!note] Events stay declarative
> Event markup references a declarative handler by name (`on:click="save"` → a [<handler>](/html-next/bindings)), never an imperative JavaScript function. When the component needs imperative behavior, the carrier names one controller *module*; functions remain inside that module. The definition therefore exposes one static file dependency without baking framework-specific callbacks into markup.

## host: the ElementInternals of a data component

The controller receives one argument, `host`, its window onto the instance. The name is the platform's: Shadow DOM already calls the component element seen from inside `:host`[^3]. Every capability on it is a thin, framework-neutral surface with a native anchor, which is precisely what makes it portable across compile targets.

```ts
type EffectCallback = () => void | (() => void);

interface ComponentHost<State extends object = Record<string, unknown>> {
  /** The component's root element. Its connection owns this controller's lifetime. */
  readonly root: Element;

  /** Every value declared in <defs>: props, state, computed, data. Only paths
   *  rooted at a declared <state> are writable; a write flows through the graph. */
  readonly state: State;

  /** Elements the definition marked with $ref, by name. A name inside $each is the
   *  list that iteration produced. */
  readonly refs: Readonly<Record<string, Element | readonly Element[]>>;

  /** Elements a consumer projected, by slot name, in order. Empty while the slot
   *  shows its fallback. The only way to enumerate projected content. */
  readonly slots: Readonly<Record<string, readonly Element[]>>;

  /** Run callback on a lifecycle or component event. Returns an unsubscribe. */
  on(type: string, callback: EventListener): () => void;

  /** Run while connected, re-running when a state path it read changes. */
  effect(callback: EffectCallback): () => void;

  /** Raise a component event a parent catches with on:event. */
  dispatch(type: string, detail?: unknown): boolean;
}
```

| On `host` | Does | Native anchor |
| --- | --- | --- |
| `host.root` | The component's root element, whose connection owns this controller's lifetime. | `:host` / the custom-element instance |
| `host.state` | Read the instance's props, state, computed values, and resources. Only paths rooted at a declared `<state>` are writable; a valid write flows through the dependency graph. | `ElementInternals` state[^2] (generalized from boolean `:state()` flags to values) |
| <code>host.refs.<var>name</var></code> | The element declared with <code>$ref="<var>name</var>"</code>, or the list of them when that name sits inside an iteration. | captured at lowering (see below) |
| <code>host.slots.<var>name</var></code> | The elements a consumer projected into that slot, in order; empty while the slot shows its fallback. | `assignedElements()`[^9] |
| <code>host.on(<var>event</var>, fn)</code> | Run `fn` on a lifecycle or component event; `connect`/`disconnect` included. | `connectedCallback`/`disconnectedCallback`[^1] |
| `host.effect(fn)` | Run `fn` while connected and re-run it whenever a state path it read changes. Returns an early-stop function; connection also owns cleanup. | TC39 Signals `Watcher`[^4] plus DOM connection |
| <code>host.dispatch(<var>event</var>, detail)</code> | Raise a component event a parent can catch with `on:event`. | `CustomEvent` / `dispatchEvent`[^8] |

Teardown is either a disposer returned from an `host.on("connect", …)` callback or an explicit `host.on("disconnect", …)`; `host.effect` cleans itself up. This is the same connect-and-return-a-disposer shape used across the platform and userland alike.

### The companion JavaScript / DOM API

`host.effect(callback)` is the deliberately small JavaScript companion to declarative bindings. It exists for effects on systems outside the runtime-owned DOM, such as updating a chart, observer, or media object from component state. It is not required to make template bindings reactive; those are wired directly from their declared paths.

- **Connection:** an effect registered by the controller runs once when the instance is connected. Reads through `host.state` during its last successful run are its dependencies.
- **Update:** a dependency change marks the effect dirty. The runtime coalesces repeated changes and runs it in the same ordered microtask flush as affected bindings, after state and computed values have settled.
- **Rerun:** if the callback returned a disposer, that disposer runs before the next callback. The next run replaces the tracked dependency set, so conditional JavaScript reads remain precise without an authored `untrack`.
- **Disconnection:** the current disposer runs and every observation owned by the effect is removed. It does no work while detached; reconnection runs it once and establishes a fresh dependency set.
- **Early stop:** the function returned by `host.effect` performs the same cleanup permanently and is idempotent.

> [!norm] The reactive API is instance-scoped
> The contract exposes values through `host.state` and lifetime-bound reactions through `host.effect`; it does not expose an instance's backing `Signal.State`, `Signal.Computed`, or `Watcher` objects. Raw handles would let code retain observations beyond the element's lifetime, bypass declared writability and type rules, and couple HTML Next to a Stage&nbsp;1 API shape. A browser runtime may use TC39 Signals internally, but that choice is not observable. Page code outside the controller uses the component's declared attributes and properties and listens for DOM events; it cannot retrieve the private `host`. The raw-signal question can be reopened if cross-system signal identity proves to be a real interoperability requirement.

> [!note] Grounded in the platform, not a framework
> The surface reads like userland (`state`, `effect`, `refs`), but each name has a standards anchor: the carrier's module reference ↔ declarative module loading, `host` ↔ `:host`, connect/disconnect ↔ the custom-element reactions, `effect` ↔ the Signals proposal. The overall shape, a controller bound to a host with connect and disconnect callbacks, is Lit's Reactive Controller[^5], adapted to a script-free definition.

## Element handles: $ref

A controller often needs a specific element, the node a library mounts into. Rather than a fragile `querySelector` that reaches into runtime-owned markup, the definition **declares** the handle with `$ref="name"`, and the controller reads it as `host.refs.name`.

```html
<!-- $ref is a directive: consumed at lowering, so no non-conforming attribute ships. -->
<div $ref="canvas"></div>
<canvas $ref="surface" width="640" height="480"></canvas>

<!-- inside an iteration, one name covers every element that iteration produced -->
<li $each="o of options" $key="o.id" $ref="rows"></li>

```

```js
host.refs.canvas    // the <div>
host.refs.surface   // the <canvas>
host.refs.rows      // [<li>, <li>, ...] in rendered order
```

`$ref` is a **directive**, part of the `$` family (`$if`, `$each`, `$value`): the runtime reads it, records the node for the controller, and **strips it at lowering**. So the final DOM carries no `ref` attribute, which matters because a literal `ref` (or a `name` on a non-form element) would be non-conforming HTML. A consumed directive sidesteps that entirely. It is the **only** way a controller reaches an element: there is no second path for elements that happen to carry a `name`, so an author never has to know which kind of element they are holding.

A name's **multiplicity is inferred from where the `$ref` sits**, the way a binding's type is inferred from what it reads. Outside any iteration a name is one element; inside `$each` it is the list that iteration produced, in rendered order, and it grows and shrinks with the iteration. Both cases are statically known, because the analysis that reads dependencies off the parsed markup already knows which regions iterate. Repeating one name outside an iteration is a **diagnostic**, exactly like a duplicate `<prop>`: two elements answering to one handle is an authoring mistake, not a collection.


> [!note] $ref names a JavaScript handle
> `$ref` is consumed at lowering and gives the controller a JavaScript handle to a named element. Shadow DOM's `part` / `::part()`[^3] remains the CSS mechanism for exposing a theming surface across a shadow boundary. The two names serve separate APIs.

## Finding elements: the root, and what is inside it

`host.root` is the component's root element. Everything a controller works with is reached from it with the DOM the platform already has: `host.refs` for the component's own named parts, whether one element or the list an iteration produced, `host.slots` for the elements a consumer projected, and `root.closest` for the component or form it sits in.

```js title="x-listbox.js"
// x-listbox.js
export default function controller(host) {
  const root = host.root;                    // the component's root element

  // Its own parts: declared in the template with $ref, read as host.refs.
  const panel = host.refs.panel;

  // What the consumer projected: the assigned elements, in order.
  const options = () => host.slots.default;


  // The component it sits in, found by public contract, walking up from its root.
  const form = root.closest("form");
  const group = root.closest('[role="group"]');

  // An event from inside, resolved to the part it came from.
  host.on("connect", () => {
    const onClick = (event) => {
      const option = event.target.closest('[role="option"]');
      if (option && root.contains(option)) host.state.value = option.dataset.value;
    };
    root.addEventListener("click", onClick);
    return () => root.removeEventListener("click", onClick);
  });
}
```

Where a controller does query, outward with `root.closest` or to resolve an event target upward, it goes by the **public contract** an element already carries: its ARIA role (`[role="option"]`, `[role="treeitem"]`), its native element and type (`input[type="radio"]`, `form`), its `name`, and attributes the author wrote. That contract is the one assistive technology reads, so a controller that follows it resolves exactly the parts a user perceives.

> [!norm] Projected content is reached through its slot, never by query
> A component lowers into **one tree with no shadow boundary**, so a query rooted at `host.root` cannot tell an element a consumer projected from one the component's own template rendered: both are ordinary descendants, and both match the same selector. Shadow DOM gets that distinction free from keeping two trees, and a controller there asks `assignedElements()`[^9] rather than querying. Here the slot restores it. A controller [must]{.kw} enumerate projected content through <code>host.slots.<var>name</var></code>, and [must not]{.kw} discover it by searching its own subtree.

> [!norm] Never select by runtime markers
> The markers the runtime writes for styling (`data-component`, `data-<tag>-state`, `data-slotted`; see [Styling](/html-next/styling)) are implementation details. They exist so scoped CSS can find a root, they differ by target, and a framework target that scopes styles its own way need not emit them. A controller that selects by them couples its behavior to one target's output and breaks on another.

```js
// Wrong: selects by markers the runtime writes for styling.
root.querySelectorAll('[data-component~="x-option"]');
root.closest('[data-x-select-state~="open"]');

// Right: selects by the public contract those elements already carry.
root.querySelectorAll('[role="option"]');
root.closest('[role="listbox"]');
```

## Controller and runtime ownership

Because a component lowers to **real DOM with no shadow boundary**, a controller *could* reach in and mutate bound nodes, and if it did, two writers, the controller and the runtime, would fight over the same DOM and thrash. The rule that prevents this is a single sentence:

```js
// The controller drives STATE. The runtime reflects state to the DOM.
host.state.center = [51.5, -0.1];   // a write; the graph updates every binding that reads center
host.state.center;                  // a read

// It never writes bound DOM directly. That stays the runtime's, so there is one writer
// to the DOM and one source of truth. The map library owns its own (unbound) canvas subtree.
```

The runtime owns the subtree it lowered and every bound attribute and text node in it. The controller writes **state**; the runtime reflects state to the DOM. That keeps one writer to the DOM and one source of truth. A controller only touches DOM directly in its own *foreign* subtree, the canvas a map library renders into, which is unbound and therefore no one else's. User- and browser-driven native state (`:checked`, `<details open>`, form values) is treated as input through `bind:`, not fought.

> [!note] Updates are batched, so this is cheap
> State changes are fine-grained (only the bindings that read a changed path update) and coalesced into one flush per microtask, so a controller setting several state values in a row produces a single DOM update, not a cascade. See [Reactivity](/html-next/reactivity) for the scheduling model.

Communication upward is an event, not a mutated ancestor: `host.dispatch` raises a component event the parent catches declaratively.

```js
// Raise a component event; a parent listens with on:event, exactly like a <handler> dispatch.
host.dispatch("locationchange", { lat, lng });

// <x-map on:locationchange="recenter">
```

## Binding: the definition owns the controller edge

The runtime discovers definitions and instances in the document. Each definition names its controller entry module directly, and that module's default export supplies the behavior:

```html
<!-- 1. the DEFINITION names both the tag and its controller module. -->
<template component="x-chart" controller="./x-chart.js"> … </template>

// 2. x-chart.js default-exports the controller. It does not repeat "x-chart".
export default function controller(host) { … }

<!-- 3. INSTANCES connect to the controller declared by their definition. -->
<x-chart></x-chart>

// The explicit dependency edge is static and unique:
//   x-chart definition → ./x-chart.js default export.
```

The **definition** registers declaratively, by being a parsed `<template component="x-chart" controller="./x-chart.js">`. Its `controller` attribute is a static dependency edge to one ES-module entry point. The browser imports that module, requires a callable default export, and invokes it with each connected instance's `host`. The tag is not repeated in JavaScript, so markup and behavior cannot silently disagree.

> [!norm] A platform contract, not a library convention
> The proposal defines browser behavior. Controller source has no required package import and no polyfill registration call. Until browsers implement the feature, `@nextwebwg/html` performs the same resolution, default-export check, and per-instance invocation behind the declarative surface. Build targets may statically import the same default export and pass it their host adapter. None of those implementation paths changes component source.

> [!note] Sharing the custom-element namespace
> A hyphenated tag like `x-chart` is also a valid *custom element* name, so the two registries occupy one namespace, and precedence must be defined, not left to a race. The rule: **a registered custom element wins**. If `customElements.get(tag)` is defined, the browser owns that tag (it upgrades and runs the element's own lifecycle), and HTML Next does not lower it, an author who registers a custom element for a tag has opted that tag out of HTML Next. The runtime checks this before lowering rather than tearing out a live custom element.

### Definitions and instances added after boot

An application may insert an inline `<template component>` definition or a new component instance after the runtime starts. The in-browser runtime uses `MutationObserver` to discover additions, validate and register new definitions, lower new instances, and connect their controllers. If an instance arrives before its definition, it lowers when that definition becomes available. The definition still binds behavior through `controller="…"` and a callable default export; the controller needs no package import or registration call.

Later discovery follows the same duplicate-definition, custom-element precedence, dependency, and trust rules as startup. A registered definition stays in the document registry after its carrier is consumed; inserting a second definition for that tag is an error. Inline definitions are inert data whose markup is validated before lowering. Their downstream live/imported dependencies still require application-owned resolution and import-map trust; a newly inserted definition cannot install policy. Sanitized `$html` and CMS content remain excluded from definition discovery.

The observer batches additions and removals, ignores its own completed lowering, and connects each instance once. Removal disconnects the instance and disposes its owned work; later reinsertion reconnects it. A move that stays within the same document during one mutation batch preserves the connection. Compiled/AOT builds discover the graph ahead of time and use target lifecycle hooks; they do not use `MutationObserver` for component discovery.

### Loading a controller

A definition names its controller module directly on the carrier with `controller="…"`. A URL-like value resolves relative to the definition; a bare value uses the application's ordinary import map, just like a JavaScript import. That HTML-to-JavaScript edge is statically discoverable without executing either file, and the controller's own static imports continue the visible graph through JavaScript. The component author declares dependencies; the application decides how bare specifiers resolve:

```html
<!-- LAZY: the controller loads when the first x-chart connects. -->
<template component="x-chart" controller="./b.js">…</template>

<!-- EARLY FETCH: preload the same declared module without executing or registering it twice. -->
<link rel="modulepreload" href="/components/b.js">
```

**Normally**, the browser resolves the definition's `controller` specifier and imports it when the first instance connects. An application can fetch a known critical controller earlier with ordinary `modulepreload`; the definition remains the sole binding. CSP, CORS, and any application-generated integrity metadata apply through the standard module loader. There is no controller namespace, permission attribute, manifest, or second list:

```js
// Inside /htmlnext.js. URL-like values resolve from the definition;
// bare values resolve through the application's ordinary import map.
const specifier = definition.getAttribute("controller");
const controllerURL = resolveComponentSpecifier(specifier, definitionURL);

// Standard module loading. The application's CSP, CORS rules, and generated
// import-map integrity metadata apply; the component does not carry deployment policy.
const module = await import(controllerURL);
if (typeof module.default !== "function") throw new TypeError("Controller must be callable");
module.default(host);
```

The resulting association is direct and inspectable:

| Surface | Declares | Resolved by | Evaluated by |
| --- | --- | --- | --- |
| `<template component>` | tag, declarative interface, markup, and optional controller URL | HTML Next component loader | HTML parser and component runtime |
| controller module | one default-exported host function plus ordinary static imports | the definition's `controller` edge | ES module loader[^7] |

> [!norm] The honest boundary from HTML Imports
> Importing a component root trusts its dependency closure, including a declared controller. HTML Next does **not** pretend otherwise. The improvement over HTML Imports[^6] is architectural: a definition is parsed under one closed declarative grammar; arbitrary classic scripts and inline handlers are rejected; imperative behavior has one explicit `controller` attribute; and that edge uses the existing ES-module loader instead of an imported-document script lifecycle.
>
> ES modules provide standardized fetching, CORS, CSP, dependency graphs, deduplication, and one-time evaluation. They do **not** sandbox authority. A controller and its transitive module graph are trusted page JavaScript, just like the JavaScript shipped by a custom element or an installed UI package.

## A worked example: a component that uses another

Take a dashboard, `<x-dashboard>` (component A), that reads metrics and renders a chart, `<x-chart>` (component B). A is **purely declarative** and needs no JavaScript at all; B wraps a charting library, so it has a controller. Here are the whole files.

```html title="/components/a.html"
<!-- /components/a.html — the <x-dashboard> component. Pure data: no <script>, no controller. -->
<link rel="component" href="./b.html">            <!-- A renders <x-chart>: declare the edge -->

<template component="x-dashboard">
  <defs>
    <prop name="title" type="string" default="Overview">Panel heading.</prop>
    <data name="metrics" src="/api/metrics">        <!-- a declared, reactive read -->
  </defs>

  <section>
    <h1 $value="title"></h1>
    <template $match>
      <p $when="metrics.pending">Loading…</p>
      <x-chart $else :series="metrics.value.series"></x-chart>
    </template>
  </section>
</template>
```

A declares its dependency on B with `<link rel="component">` and mentions no script. Its behavior, a reactive `<data>` read and a `$match`, is entirely declarative.

```html title="/components/b.html"
<!-- /components/b.html — declarative markup plus its controller dependency. -->
<template component="x-chart" controller="./b.js">
  <defs>
    <prop name="series" type="array" required>The data to plot.</prop>
  </defs>

  <figure>
    <canvas $ref="surface" role="img" aria-label="Revenue by month"></canvas>
  </figure>
</template>
```

B remains declarative markup. Its `controller="./b.js"` attribute declares the one module that supplies its imperative behavior, and the definition exposes a `$ref` for that controller to use. The specifier resolves relative to `b.html`, so the component remains self-contained when served live, installed from a package, or moved by a build.

```js title="/components/b.js"
// /components/b.js — an ordinary ES module: the ONLY JavaScript in the whole tree.
import { Chart } from "chart-lib";                  // a bare specifier; the import map resolves it

export default function controller(host) {          // native HTML Next and build targets use this
  let chart;
  host.effect(() => {
    const series = host.state.series;
    if (chart) chart.update(series);                 // re-plot when series changes
    else chart = new Chart(host.refs.surface, { data: series });
  });
  host.on("disconnect", () => { chart?.destroy(); chart = undefined; });
}
```

The controller is the sole piece of component JavaScript in the tree, an ordinary ES module with a default export. The page imports only the root component; the controller's own bare JavaScript dependencies still use the ordinary import map in this unbundled example:

```html title="index.html"
<!doctype html>
<link rel="component" href="/components/a.html">
<script type="importmap">                            <!-- ordinary JS dependencies, when unbundled -->
{
  "imports": {
    "chart-lib": "/vendor/chart-lib.js"
  }
}
</script>
<script type="module" src="/htmlnext.js"></script>

<x-dashboard title="Q3 revenue"></x-dashboard>
```

### How it loads, step by step

1. The browser loads `/htmlnext.js` (the runtime). It reads the application's concrete `<link rel="component" href="/components/a.html">` root and fetches `a.html`. (`rel="component"` is not a scanner-preloaded rel today, so this fetch starts once the runtime runs; to pull it forward, pair it with a `<link rel="preload">`, or resolve the graph at SSR time, see below.)
2. The runtime scans the DOM, finds `<x-dashboard>`, resolves it to `a.html`, and **fetches and parses that file as inert data, executing nothing**. Registering it, the runtime reads `<link rel="component" href="./b.html">` and records `x-chart → /components/b.html` (it does not fetch B yet).
3. It lowers `<x-dashboard>`: the `<h1>` renders, the `<data>` fetch to `/api/metrics` starts, and the `$match` shows *Loading…* while `metrics.pending`.
4. When metrics resolve, the `$match` switches to the `<x-chart>` arm. **Now** an `x-chart` is needed, so `b.html` is fetched, parsed under the declarative component grammar, and registered. Its `controller` attribute records `x-chart → /components/b.js`; `<x-chart>` lowers to `<figure><canvas>`.
5. The `<x-chart>` instance **connects**. Only now does the runtime run:
{.algo}

```js
// Inside /htmlnext.js. URL-like values resolve from the definition;
// bare values resolve through the application's ordinary import map.
const specifier = definition.getAttribute("controller");
const controllerURL = resolveComponentSpecifier(specifier, definitionURL);

// Standard module loading. The application's CSP, CORS rules, and generated
// import-map integrity metadata apply; the component does not carry deployment policy.
const module = await import(controllerURL);
if (typeof module.default !== "function") throw new TypeError("Controller must be callable");
module.default(host);
```

That is the entire lazy mechanism: resolve and import the controller entry when an instance first connects. Deduplication, one-time evaluation, caching, import-map integrity, CSP, and CORS are the platform loader's job. If metrics stay empty and the chart arm never renders, **neither `b.html` nor `b.js` is fetched**; and with no runtime at all, steps&nbsp;1–4 still produce the server-rendered declarative baseline, only the chart library is skipped.

> [!norm] How the security model holds
> The trust boundary stays where [Security](/html-next/security) puts it: at the root component package or live URL the application deliberately imports.
>
> - **Definitions use a closed grammar.** Arbitrary `<script>` elements and inline handlers are rejected, expressions cannot `eval`, and `$html` is sanitized. Imperative behavior has one visible, inspectable edge: the carrier's `controller` attribute.
> - **Application policy stays outside the component.** Installing a package and importing a concrete subpath trusts that package graph; the install/build resolves it without a browser import map. Live use is a separate application opt-in: its import map resolves a package prefix to a chosen remote root, and declarative definition edges cannot escape that mapped scope without another application-owned mapping. A running controller's imports remain ordinary ESM and are constrained by CSP origins, not by the directory prefix. Production tooling may generate import-map integrity metadata for resolved URLs. Component authors never add consumer approvals or hashes.
> - **ESM is not a sandbox.** The controller and every module it imports have the ordinary authority of page JavaScript. `host` is a stable adapter API, not a capability membrane. Package locks, code review, CSP, and optional generated integrity protect the normal software-supply boundary.
> - **Isolation requires a different execution environment.** Code that must not receive page authority belongs in a Worker or sandboxed iframe behind messages, accepting the corresponding loss of direct DOM access. That is an optional stronger deployment boundary, not something ES modules provide.

> [!note] The static graph supports incremental loading
> **Composable:** each component owns its complete dependency edges, while the application chooses only direct roots. **Lazy:** definitions fetch when a tag first lowers and controllers load on first connect, so an untaken branch costs nothing. **Cached:** definitions use HTTP caching and controllers use the module map, so a component used a hundred times evaluates its controller once. **Tunable:** `<link rel="modulepreload">` may pull a critical controller forward, while integrity metadata can pin independently hosted bytes. SSR or a package build can resolve the graph ahead of time and emit the optimized asset set automatically.

> [!note] Honest costs: async lowering, and a deep client waterfall
> Client-side lowering is **asynchronous** (fetch B, then continue), the same way a module graph resolves. And because deep dependencies live *inside* fetched definition files, a chain A→B→C→D is a **serial waterfall** on a client-only page: nothing can preload a URL it has not discovered yet. This is the strongest argument for **SSR**, which resolves the entire graph on the server and ships both the finished HTML and `modulepreload` hints for the controllers, collapsing the waterfall. Demand-driven fetching gated on *reactive* state (the `$match` example above) additionally needs lowering to pause and resume mid-subtree; that interleaving of async loading with reactivity is the genuinely hard, still-open part of this layer.

## Compiling to React, Vue, and Svelte

A controller is imperative JavaScript, so it is not transpiled into idiomatic framework code; it is **run as-is**. Because it is authored against `host`, each target ships a small **host adapter** that builds that interface from the framework's own primitives and runs the controller against it. The imperative body ports unchanged, provided it observes that portability contract; direct use of browser globals is allowed JavaScript but naturally makes the controller browser-specific.

```html title="XMap.vue (generated)"
<!-- Vue output. The controller body is reused verbatim; only the host is adapted. -->
<script setup>
import controller from "./x-map.js";
import { adaptVue } from "@nextwebwg/html/vue";

const props = defineProps({ center: { type: Array, default: () => [0, 0] } });
const canvas = ref();
adaptVue(controller, { refs: { canvas }, state: props });
</script>

<template>
  <div ref="canvas"></div>
</template>
```

This works because `host` is deliberately tiny, and every target already has all of it natively: lifecycle (Vue `onMounted`/`onUnmounted`, Svelte `onMount`/`onDestroy`, Solid `onMount`/`onCleanup`, React `useEffect`), effects (Vue `watchEffect`, Svelte `$effect`, Solid `createEffect`), refs (Vue `ref`, Svelte `bind:this`, React `useRef`), and props-or-state for `host.state`. `$ref="name"` maps to each target's ref idiom; `host.dispatch` to its event mechanism.

> [!note] React is the one that needs a bridge
> React has no native fine-grained reactivity, so its adapter backs `host.effect` and `host.state` with an external store (via `useSyncExternalStore`) rather than a signal. That wart is contained to the React adapter; the controller and every other target are unaffected.

## Lifecycle and hydration

A controller's `connect` fires when the instance connects, on first mount *and* on any later reconnection, matching the custom-element reaction rather than a once-only *mount*[^1]. On a server-rendered page, the markup arrives already lowered and inert; the controller attaches at **hydration**, where `connect` first runs in the browser. `disconnect` fires on removal, running teardown. Because the first render never depends on the controller, hydration is adopt-in-place: the controller binds to existing nodes rather than rebuilding them (see [Components](/html-next/components)).

## Reference

::: {.entry name="controller attribute" role="bind a definition to its controller module"}
Syntax
: `<template component="x-map" controller="./x-map.js">`

Module contract
: a callable `default` export receiving `host`; no package import or registration call

Runs
: once per instance, at connect (and at hydration on SSR pages)

Level
: [L2+]{.pill .soon} reserved
:::

::: {.entry name="host" role="the instance window passed to a controller"}
Provides
: `element`, `state` (declared state only is writable), `refs`, `elements`, `on`, `effect`, `dispatch`

Effect lifetime
: connected only; dependency changes are microtask-batched; cleanup runs before rerun and on disconnect; the returned stop function ends it early

Native kin
: `ElementInternals` + `:host`

Rule
: drives state, never bound DOM; owns only its foreign subtree

Level
: [L2+]{.pill .soon} reserved
:::

::: {.entry name="$ref" role="declared element handle"}
Value
: a name; <code>host.refs.<var>name</var></code> is the element

Semantics
: a `$` directive, consumed at lowering; no attribute ships

Multiplicity
: one element, or the list an enclosing `$each` produced; inferred, never declared

Level
: [L2+]{.pill .soon} reserved
:::

## References

[^1]: WHATWG HTML, [custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-elements-core-concepts) (`connectedCallback`/`disconnectedCallback`): a controller supplies the same per-instance behavior and lifecycle to a data-defined component instead of requiring a class registration.
[^2]: WHATWG HTML, [ElementInternals](https://html.spec.whatwg.org/multipage/custom-elements.html#the-elementinternals-interface) and [custom states](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) with CSS [:state()](https://developer.mozilla.org/docs/Web/CSS/:state): the native model for the internal state of an element, generalized here from boolean flags to values.
[^3]: CSS Scoping, [Shadow Parts](https://drafts.csswg.org/css-shadow-parts/) (`part` / `::part()`) and [:host](https://developer.mozilla.org/docs/Web/CSS/:host): the platform words for a component element seen from inside, and for a named internal piece exposed to outside CSS.
[^4]: TC39, [Signals](https://github.com/tc39/proposal-signals) (`State`, `Computed`, and `Watcher`): a candidate low-level basis for `host.effect`. The proposal explicitly does not provide effects, scheduling, DOM ownership, or automatic disposal; this DOM-facing layer supplies them.
[^5]: Lit, [Reactive Controllers](https://lit.dev/docs/composition/controllers/) (`hostConnected`/`hostDisconnected`, a controller object attached to a host): direct prior art for the controller-plus-host shape, adapted to a script-free definition.
[^6]: W3C, [HTML Imports](https://www.w3.org/TR/webcomponents/#imports) (discontinued): the approach this layer deliberately avoids, fusing markup, style, and executing script into one imported document.
[^7]: WHATWG HTML, [module-script fetching](https://html.spec.whatwg.org/multipage/webappapis.html#fetch-a-single-module-script), [Content Security Policy](https://developer.mozilla.org/docs/Web/HTTP/Guides/CSP), and [Subresource Integrity](https://developer.mozilla.org/docs/Web/Security/Defenses/Subresource_Integrity): the existing loading and deployment controls used by controllers.
[^8]: WHATWG DOM, [CustomEvent](https://dom.spec.whatwg.org/#interface-customevent) and [dispatchEvent](https://dom.spec.whatwg.org/#dom-eventtarget-dispatchevent): what `host.dispatch` lowers to.
[^9]: WHATWG HTML, [`HTMLSlotElement.assignedElements()`](https://html.spec.whatwg.org/multipage/scripting.html#dom-slot-assignedelements): the native way a component reads what a consumer projected, rather than searching its own subtree for it.
