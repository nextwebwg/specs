---
title: The JavaScript Layer
order: 6
blurb: controllers · host · $ref · finding elements · effects · requests · componentRegistry
eyebrow: Declarative HTML Components · reserved for Level 2
status: Proposed direction · the imperative escape hatch
---

# The JavaScript Layer

Almost everything is declarative, and a component definition **contains no executable code**: code is referenced, never embedded. When behavior genuinely needs imperative JavaScript, a timer, a stream, an observer, a foreign library, it lives in an ordinary **ES module** outside the definition and attaches through a small, native-grounded seam: a **controller** declared by the component definition. The definition stays pure data; the module stays pure behavior; they meet only at the contract.

## Imperative behavior uses controllers

The declarative layers, templating, bindings, and reactivity, cover the large majority of interface work with no script. But some behavior is irreducibly imperative: a `setInterval` clock, a Server-Sent-Events stream, an `IntersectionObserver`, wrapping a mapping or charting library, or computation too involved for a [pure expression](/declarative-components/expressions). That work needs JavaScript, and pretending otherwise would push authors back into inline handlers and `eval`-shaped escapes.

So HTML Next draws a firm line. A **component definition is declarative data**: no embedded script, no inline handlers, importable and inspectable without executing anything, and renderable on a server. A definition may also name a third-party script it needs, such as a payment SDK, as a [declared script](/declarative-components/components#declared-scripts): a visible URL that the runtime loads as an ordinary `<script>` element when an instance connects. Imperative JavaScript is a **separate concern** in an ordinary ES module. The two never fuse; they meet at a named seam.

> [!norm] Server rendering supplies the declarative baseline
> The JavaScript layer only *enhances*: a controller adds live imperative behavior on top and is never load-bearing for the first render. But be precise about what "no JS" delivers, because it depends on where the markup comes from. On a **server-rendered** page the first render is real HTML that displays, is accessible, and is indexable with no script; a controller failing to load leaves that baseline intact. On a **client-only** page there is no such baseline: an invocation like `<x-app>` is an unknown element, so without the runtime it renders *nothing* (its inline children, if any, are all that shows). So the guarantee is: **no-JS renders the declarative baseline when the HTML was server-rendered**; client-only pages need the runtime to produce first paint. Determinism and adopt-in-place hydration are likewise SSR properties (see [Components](/declarative-components/components)), not client-only ones.

## The controller

A component that needs imperative behavior gets a **controller**: the default-exported function from the ES module named by the component definition, run once per instance. It is the decoupled equivalent of a custom element's class plus its `ElementInternals`[^1], the same behavior a Web Component would put in a class, attached instead to a definition made of data.

::: two

```html title="x-map.html"
<!-- x-map.html: declarative data plus its optional controller dependency. -->
<template component="x-map" controller="./x-map.js">
  <defs>
    <state type="list(number)" name="center" value="[0, 0]">
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
> Event markup references a declarative handler by name (`on:click="save"` → a [<handler>](/declarative-components/bindings)), never an imperative JavaScript function. When the component needs imperative behavior, the carrier names one controller *module*; functions remain inside that module. The definition therefore exposes one static file dependency without baking framework-specific callbacks into markup.

## host: the ElementInternals of a data component

The controller receives one argument, `host`, its window onto the instance. The name is the platform's: Shadow DOM already calls the component element seen from inside `:host`[^3]. Every capability on it is a thin, framework-neutral surface with a native anchor, which is precisely what makes it portable across compile targets.

```ts
type EffectCallback = () => void | (() => void);

interface PropHandle<Value> {
  readonly value: Value;
  readonly inputValue: unknown;
  readonly validity: ValidityState;
  validate(): ValidityState;
}

interface DataResource<Value = unknown> {
  readonly pending: boolean;
  readonly value: Value;
  readonly error: unknown;
  readonly ok: boolean;
  readonly dirty?: boolean; // write resources
}

interface ScriptResource {
  readonly pending: boolean;
  readonly ok: boolean;
  readonly error: Event | TypeError | null;
  /** Resolves when the script loads; rejects with its error event. Settles once, with the script. */
  readonly ready: Promise<void>;
  /** Insert the script element if it is not inserted yet. Returns ready. */
  load(): Promise<void>;
}

interface ComponentHost<
  State extends object = Record<string, unknown>,
  Props extends object = Record<string, unknown>,
  Data extends Record<string, DataResource> = Record<string, DataResource>,
> {
  /** The component's root element. Its connection owns this controller's lifetime. */
  readonly root: Element;

  /** Local mutable <state>, read-only computed state, and inherited <context> values.
   *  Only paths rooted at a declared <state> are writable. */
  readonly state: State;

  /** Returns one state, or every state, to its declared value. */
  reset(name?: keyof State): void;

  /** One read-only resource per <data>; resource changes participate in effects. */
  readonly data: Readonly<Data>;

  /** One entry per named declared script; status changes participate in effects. */
  readonly scripts: Readonly<Record<string, ScriptResource>>;

  /** One handle per declared <prop>. No <state>, <computed>, or <data> entries. */
  readonly props: { readonly [Name in keyof Props]: PropHandle<Props[Name]> };

  /** Elements the definition marked with $ref, by name. A name inside $each is the
   *  list that iteration produced. */
  readonly refs: Readonly<Record<string, Element | readonly Element[]>>;

  /** Elements a consumer projected, by slot name, in order. Empty while the slot
   *  shows its fallback. A <template slot> contributes the elements it renders,
   *  only while its slot renders. The only way to enumerate projected content. */
  readonly slots: Readonly<Record<string, readonly Element[]>>;

  /** Run callback on a lifecycle or component event. Returns an unsubscribe. */
  on(type: string, callback: EventListener): () => void;

  /** Run while connected, re-running when a state path it read changes. */
  effect(callback: EffectCallback): () => void;

  /** Raise a component event a parent catches with on:event. */
  dispatch(type: string, detail?: unknown): boolean;

  /** Ask the consumer a declared request. Resolves to its answer, or null. Present when the component declares a request. */
  request?(name: string, detail?: unknown, options?: RequestOptions): Promise<unknown>;

  /** Whether a known responder answers a declared request; effects re-run when it changes. Present when the component declares a request. */
  hasResponder?(name: string): boolean;
}
```

| On `host` | Does | Native anchor |
| --- | --- | --- |
| `host.root` | The component's root element, whose connection owns this controller's lifetime. | `:host` / the custom-element instance |
| `host.state` | Read local mutable state, read-only computed state, and inherited `<context>` values. Only declared `<state>` entries are writable. Props and data resources are absent. | `ElementInternals` state[^2] (generalized from boolean `:state()` flags to values) |
| <code>host.reset(<var>name</var>)</code> | Return a state to its declared `value`, or every state when no name is given. See [Resetting state](#resetting-state). | A form's `reset()`, which returns each control to its default |
| <code>host.data.<var>name</var></code> | Read a declared `<data>` resource, including its `.pending`, `.value`, `.error`, and `.ok` fields. The resource is read-only. | The declared resource and its native fetch lifetime |
| <code>host.scripts.<var>name</var></code> | Read a [declared script](/declarative-components/components#declared-scripts)'s status, wait for it with `ready`, or insert it now with `load()`. | The inserted `<script>` element's `load` and `error` events |
| <code>host.props.<var>name</var></code> | Inspect a caller-supplied prop's accepted value, latest direct input, and validity. This is the controller's only path to a declared prop. | An HTML control separates its input and validity from the value its consumers read[^10] |
| <code>host.refs.<var>name</var></code> | The element declared with <code>$ref="<var>name</var>"</code>, or the list of them when that name sits inside an iteration. | captured at lowering (see below) |
| <code>host.slots.<var>name</var></code> | The elements a consumer projected into that slot, in order; empty while the slot shows its fallback. For a consumer's `<template slot>`, the elements the template renders while the slot renders, and none while it does not ([content that renders on demand](/declarative-components/components#content-that-renders-on-demand)). | `assignedElements()`[^9] |
| <code>host.on(<var>event</var>, fn)</code> | Run `fn` on a lifecycle or component event; `connect`, `disconnect`, and [`responder`](#late-responders) included. | `connectedCallback`/`disconnectedCallback`[^1] |
| `host.effect(fn)` | Run `fn` while connected and re-run it whenever a state path it read changes. Returns an early-stop function; connection also owns cleanup. | TC39 Signals `Watcher`[^4] plus DOM connection |
| <code>host.dispatch(<var>event</var>, detail)</code> | Raise a component event a parent can catch with `on:event`. | `CustomEvent` / `dispatchEvent`[^8] |
| <code>host.request(<var>name</var>, detail, { signal, progress })</code> | Ask the consumer a declared [request](#requests); resolves to its answer, or `null`. Present when the component declares a request. | `FetchEvent.respondWith()`[^11] |
| <code>host.hasResponder(<var>name</var>)</code> | Whether a [known responder](#has-responder) answers a declared request, as a reactive read. Present when the component declares a request. | the request's event path |

Teardown is either a disposer returned from an `host.on("connect", …)` callback or an explicit `host.on("disconnect", …)`; `host.effect` cleans itself up. This is the same connect-and-return-a-disposer shape used across the platform and userland alike.

### Waiting for a declared script {#host-scripts}

A component that wraps a third-party SDK declares the SDK's script in `<defs>` and waits for it in the controller. `host.scripts.name.ready` is a promise about the script: it settles once, on the inserted `<script>` element's own `load` or `error` event. The declaration's `on:load` and `on:error` handlers, by contrast, run once for each connection:

```js
// <script name="maps" src="https://maps.example/sdk/v2.js" loading="manual">
export default function controller(host) {
  host.on("connect", () => {
    host.refs.open.addEventListener("click", async () => {
      await host.scripts.maps.load();          // inserts the element once, then waits
      if (host.root.isConnected) new MapsSDK.Map(host.refs.canvas);
    }, { once: true });
  });
}
```

`load()` matters only for `loading="manual"`; for `eager` and `lazy` it inserts the element early. The script is shared by every component that declares the same URL and is never removed, so `ready` may already be resolved when an instance connects. A controller that sets up on every connection waits on `ready` in its `connect` callback, as here, or uses `on:load`. See [Declared scripts](/declarative-components/components#declared-scripts) for when the element is inserted and how its status is shared.

### Accepted values and prop inputs {#accepted-values-and-prop-inputs}

`host.props.amount.value` reads the prop's **accepted value**. Template expressions such as `$amount` read that value too; `host.state.amount` is absent. A declared `<state name="count">` is read and written through `host.state.count`, and `host.props.count` is absent. A `<computed>` declares **computed state**: its value is derived from dependencies and read through `host.state`, but cannot be assigned. Inherited `<context>` values are also read-only under `host.state`. Each `<data>` resource is read through `host.data`, for example `host.data.search.value`; data resources are absent from `host.state`. State has no `inputValue` or `validity`; a failed `<set>` or `bind:` write does not replace it. When the attempted value came from a native control, that control retains its edit and owns its validity.

`host.props.amount.inputValue` is the latest value supplied **directly to that prop before conversion**. An HTML attribute supplies a string; a framework prop may supply a JavaScript value. It is not an alias for DOM `getAttribute()`, which reads an attribute string and may describe a default rather than the current input. `host.props.amount.validity` checks that input against the declaration. `validate()` explicitly recomputes and returns the same per-prop validity shape. The component root exposes the aggregate validity with a path for each failing prop (see [Validation](/declarative-components/validation)). Reads through `host.props.amount.value`, `host.state.count`, computed state, and resource fields such as `host.data.search.value` participate in `host.effect` dependency tracking.

```js
// <prop name="amount" type="number" default="5">; invoked with amount="oops"
host.props.amount.inputValue      // "oops"
host.props.amount.value           // 5
host.state.amount                 // undefined: props are absent from state
host.props.amount.validity.badInput // true
```

### Resetting state {#resetting-state}

`host.reset(name)` returns one state to its declared `value`. `host.reset()` returns every state, in one batch. A form's `reset()` does the same for its controls.

```js
// <state name="count" type="integer" value="0">
// <state name="filter" type="object({ text: string })" value="{ text: '' }">
host.state.count = 5;
host.state.filter.text = "ada";
host.reset("count");   // count is 0 again
host.reset();          // every state is back: count is 0 and filter is { text: '' }
```

The reset value is a fresh copy, so an object or list is a new one each time, never shared with an earlier reset. A state without a `value` resets to `null`. A name that is not a declared `<state>`, such as a computed value, a context or a prop, throws a `TypeError` that names it. A reset notifies its readers as any write does, only when the value changes, and renders in the next flush.

Underneath, a reset is a `null` write: a state with a `value` always reads as its type, so writing `null` gives back that value ([Null and missing values](/declarative-components/types#null-and-missing-values)).

### State writes use the same checks as bindings {#state-writes-use-the-same-checks-as-bindings}

A controller assignment proposes a value to the declared state, just as `<set>` or `bind:` does. The destination's type rules apply before the write. A `null` or `undefined` write is never wrong-typed: a state with a `value` goes back to it, and one without stores `null`. A wrong-typed value is ignored, the state keeps its current value, and dependents are not notified. An attempt to assign computed state or an inherited context is likewise ignored because that destination is read-only.

```js
// <state name="count" type="number" value="1">
// <computed name="doubled" from="$count * 2">
host.state.count = 2;          // accepted; doubled becomes 4
host.state.count = 'blah';     // warning; count stays 2, doubled stays 4
host.state.count = null;       // accepted; count is 1 again, doubled becomes 2
host.state.doubled = 10;       // warning; computed state stays read-only
```

An invalid authored write reports the same runtime warning as an authored binding or handler write with the same defect. The warning identifies the destination and its expected type or read-only status; a repeated defect at the same authored location is reported once. These writes do not throw merely because their value is invalid. A build tool may report a statically knowable mistake before execution. An ordinary invalid user edit remains a validity concern and does not produce a warning. See [Invalid reactive results](/declarative-components/reactivity#invalid-reactive-results).

The checks have the same depth as declarative writes: an object or list is checked at its immediate boundary, and nested fields are checked when read or written through their declared paths. Controller assignment does not introduce a separate coercion or validation policy. Resource fields under `host.data` are also read-only; a controller changes a resource's declared state parameters rather than assigning its response or status fields.

A controller calculates with JavaScript's own operators. Three steps of `host.state.level += 0.1` from `0` store `0.30000000000000004`, where three runs of `<set name="level" expr:value="$level + 0.1">` store `0.3` by the [decimal arithmetic rule](/declarative-components/expressions#decimal-arithmetic). A controller that must match an expression applies the same rule; an implementation may export it as `add`, `subtract`, `multiply`, and `divide`.

### The companion JavaScript / DOM API {#the-companion-javascript-dom-api}

`host.effect(callback)` is the deliberately small JavaScript companion to declarative bindings. It exists for effects on systems outside the runtime-owned DOM, such as updating a chart, observer, or media object from component state. It is not required to make template bindings reactive; those are wired directly from their declared paths.

- **Connection:** an effect registered by the controller runs once when the instance is connected. Reads through `host.state` or `host.props` during its last successful run are its dependencies.
- **Update:** a change to a value it read marks the effect dirty; a write that leaves the value unchanged does not (see [What counts as a change](/declarative-components/reactivity#changes)). The runtime coalesces repeated changes and runs it in the same ordered microtask flush as affected bindings, after state and computed values have settled.
- **Rerun:** if the callback returned a disposer, that disposer runs before the next callback. The next run replaces the tracked dependency set, so conditional JavaScript reads remain precise without an authored `untrack`.
- **Disconnection:** the current disposer runs and every observation owned by the effect is removed. It does no work while detached; reconnection runs it once and establishes a fresh dependency set.
- **Early stop:** the function returned by `host.effect` performs the same cleanup permanently and is idempotent.

> [!norm] The reactive API is instance-scoped
> The contract exposes mutable and computed state and inherited contexts through `host.state`, declared resources through `host.data`, caller-supplied props through `host.props`, and lifetime-bound reactions through `host.effect`; it does not expose an instance's backing `Signal.State`, `Signal.Computed`, or `Watcher` objects. Raw handles would let code retain observations beyond the element's lifetime, bypass declared writability and type rules, and couple HTML Next to a Stage&nbsp;1 API shape. A browser runtime may use TC39 Signals internally, but that choice is not observable. Page code outside the controller uses the component's declared attributes and properties and listens for DOM events; it cannot retrieve the private `host`. The raw-signal question can be reopened if cross-system signal identity proves to be a real interoperability requirement.

> [!note] Grounded in the platform, not a framework
> The surface reads like userland (`state`, `effect`, `refs`), but each name has a standards anchor: the carrier's module reference ↔ declarative module loading, `host` ↔ `:host`, connect/disconnect ↔ the custom-element reactions, `effect` ↔ the Signals proposal. The overall shape, a controller bound to a host with connect and disconnect callbacks, is Lit's Reactive Controller[^5], adapted to a definition that contains no code.

## Element handles: $ref

A controller often needs a specific element, the node a library mounts into. Rather than a fragile `querySelector` that reaches into runtime-owned markup, the definition **declares** the handle with `$ref="name"`, and the controller reads it as `host.refs.name`.

```html
<!-- $ref is a directive: consumed at lowering, so no non-conforming attribute ships. -->
<div $ref="canvas"></div>
<canvas $ref="surface" width="640" height="480"></canvas>

<!-- inside an iteration, one name covers every element that iteration produced -->
<li $each="o of $options" $key="$o.id" $ref="rows"></li>

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
> The markers the runtime writes for styling (`data-component`, `data-<tag>-state`, `data-slotted`; see [Styling](/declarative-components/styling)) are implementation details. They exist so scoped CSS can find a root, they differ by target, and a framework target that scopes styles its own way need not emit them. A controller that selects by them couples its behavior to one target's output and breaks on another.

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
> State changes are fine-grained (only the bindings that read a changed path update) and coalesced into one flush per microtask, so a controller setting several state values in a row produces a single DOM update, not a cascade. See [Reactivity](/declarative-components/reactivity) for the scheduling model.

Communication upward is an event, not a mutated ancestor: `host.dispatch` raises a component event the parent catches declaratively.

```js
// Raise a component event; a parent listens with on:event, exactly like a <handler> dispatch.
host.dispatch("locationchange", { lat, lng });

// <x-map on:locationchange="recenter">
```

## Requests: behavior the consumer supplies {#requests}

> [!note] Ahead of the reference implementation
> This section specifies requests ahead of the reference implementation.

Some components need behavior from whoever uses them. A rich-text editor asks for mention suggestions, an image field asks where to store a file, a map asks how to geocode an address. Props cannot carry that behavior, because every prop has an HTML attribute form and a function has none. So a component declares a **request**: a named question its controller asks with `host.request`, and that the consumer answers in its own JavaScript, by listening for an event and calling `respondWith`. Behavior stays in controllers and scripts on both sides. Markup carries only names and types.

::: two

```html title="ui-editor.html"
<template component="ui-editor" controller="./ui-editor.js">
  <defs>
    <request name="mention-query"
      type="object({ query: string })"
      returns="list(object({ id: string, label: string }))">
      People or pages matching what the author typed after @.
    </request>
  </defs>
  <div $ref="mount"></div>
</template>
```

```js title="ui-editor.js"
export default function controller(host) {
  host.on("connect", () => {
    let pending;
    const session = createEditorSession(host.refs.mount, {
      // Called on each keystroke after @. Each query aborts the one before it.
      onMentionQuery: (query) => {
        pending?.abort();
        pending = new AbortController();
        host.request("mention-query", { query }, { signal: pending.signal })
          .then((people) => session.showMentions(people ?? []), () => {}); // rejected: superseded
      },
    });
    return () => { pending?.abort(); session.destroy(); };
  });
}
```

:::

The consumer answers in its own controller with the `host.on` it already has. The request bubbles from the editor's root to the consumer's root like any component event:

```js title="x-notes.js"
// x-notes.html renders <ui-editor> in its template.
export default function controller(host) {
  host.on("mention-query", (event) => {
    event.respondWith(searchPeople(event.detail.query, { signal: event.signal }));
  });
}
```

The author types `@a`, then `@ad`, then `@ada`. Each keystroke aborts the previous request, so the answer to `@ad` never replaces the answer to `@ada`, and `event.signal` cancels the consumer's network request with it.

A request is the inverse of a component event. An event reports something to whoever is listening and needs no answer; a request asks a question and waits for one answer. It uses the same native event channel, so page scripts and framework targets answer it with the listener mechanisms they already have. A component declares its requests with [`<request>`](/declarative-components/components#requests), apart from its events, and their detail and answer use the [request value types](/declarative-components/types#request-values).

### Asking: host.request {#host-request}

```ts
interface RequestOptions {
  /** Abort to withdraw the request. */
  signal?: AbortSignal;
  /** Receives the responder's progress while the request is pending. */
  progress?: (loaded: number, total: number) => void;
}

interface ComponentHost {
  /** Ask the consumer a declared request. Resolves to its answer, or null when none answered. Present when the component declares a request. */
  request?(name: string, detail?: unknown, options?: RequestOptions): Promise<unknown>;
}
```

`host.request` is present on the host of a component that declares at least one request. On any other host it is absent, so a controller that calls it there throws a `TypeError`, as calling any missing method does; a component that asks declares what it asks.

When a controller calls <code>host.request(<var>name</var>, <var>detail</var>, <var>options</var>)</code>, the runtime [must]{.kw} run these steps:

1. If the definition declares no `<request>` named <var>name</var>, return a promise rejected with a `TypeError`. A build tool [may]{.kw} report a literal undeclared name before execution.
2. If <var>detail</var> does not conform to the request's `type`, report a runtime warning that names the request, and return a promise rejected with a `TypeError`.
3. Let <var>signal</var> be `AbortSignal.any()` of <var>options</var>`.signal`, when given, and the instance's **connection signal**, which aborts when the instance disconnects. If <var>signal</var> is aborted, return a promise rejected with its reason.
4. Wait until every component whose root is a DOM ancestor of the instance's root, and whose definition declares a controller, has run that controller's synchronous body for its current connection, or has failed to load it. The wait ends when each controller function returns; promises a controller starts are outside it. If <var>signal</var> aborts while waiting, reject with its reason.
5. Create a `RequestEvent` whose `type` is <var>name</var>, whose `detail` is <var>detail</var> or `null`, and whose `signal` is <var>signal</var>. It bubbles, is composed, and is not cancelable.
6. Dispatch it at the instance's root.
7. If no listener called `respondWith` during that dispatch, remember the request for [late responders](#late-responders) and resolve with `null`.
8. Otherwise, forget any remembered request with this name from this instance, and wait for the value passed to `respondWith`, forwarding [progress](#request-progress) meanwhile. If <var>signal</var> aborts first, reject with its reason and discard the value when it arrives. If the value rejects, reject with that reason.
9. If the value is not `null` and does not conform to the request's `returns` type, reject with a `TypeError` and report a runtime warning that names the request. Otherwise resolve with the value.
{.algo}

Step 4 makes the order in which controllers load irrelevant. An editor that asks for its extensions when it connects reaches its consumer's listener even when the consumer's controller module loads second. A consumer [should]{.kw} register its answers in its controller's synchronous body or its `connect` callback, before any `await`; an answer can still arrive later, because `respondWith` accepts a promise. A responder that registers after the request was made is a [late responder](#late-responders).

`null` is the answer to an unanswered request, as it is the value of an omitted prop. An asker treats it as "no answer" whether the consumer answered `null` or never answered.

The detail and the answer are passed by reference, not cloned, as a `host.dispatch` payload is. The answer is not reactive and is not stored: a controller that needs it again asks again.

### Answering: RequestEvent {#request-event}

```ts
interface RequestEvent<Detail = unknown, Answer = unknown> extends CustomEvent<Detail> {
  /** Aborts when the asker no longer needs the answer, or its component disconnects. */
  readonly signal: AbortSignal;
  /** Answer the request with a value or a promise of one. */
  respondWith(answer: Answer | null | PromiseLike<Answer | null>): void;
  /** Report progress to the asker while the request is pending. */
  progress(loaded: number, total: number): void;
}
```

`respondWith(answer)` [must]{.kw} throw an `"InvalidStateError"` `DOMException` when it is called after the event's dispatch has finished, or when the request already has an answer. Otherwise it records <var>answer</var> and stops the event's propagation, including to the remaining listeners on the current target. The **nearest responder answers**: a listener on the editor's own root takes precedence over one on its consumer's root, which takes precedence over one on the document. An application can set a default upload destination on `document` and override it for one region of the page.

A responder that starts asynchronous work passes `event.signal` to it. When the asker aborts its own signal, for example because the author typed another character, or when the asking component disconnects, `event.signal` aborts and the request rejects with its reason without waiting for the responder.

A consumer that is itself a component may forward a request it also declares. Its own `host.on` sees requests from its own root too, so it checks the target first:

```js
host.on("mention-query", (event) => {
  if (event.target === host.root) return;   // our own request: let it bubble to our consumer
  event.respondWith(host.request("mention-query", event.detail, { signal: event.signal }));
});
```

### Reporting progress {#request-progress}

An answer arrives once, so a long task reports its progress separately. The asker passes a `progress` callback, and the responder calls `event.progress(loaded, total)`. An image upload shows a progress bar, a cancel button aborts it, and with no uploader the editor keeps a local preview:

```js title="ui-editor.js"
session.onImageDrop = (file, placeholder) => {
  const upload = new AbortController();
  placeholder.onCancel = () => upload.abort();        // the cancel button, or deleting the node
  host.request("image-upload", { file }, {
    signal: upload.signal,
    progress: (loaded, total) => placeholder.setProgress(loaded / total),
  }).then((image) => image ? placeholder.setSrc(image.src) : placeholder.keepPreview(),
          () => placeholder.remove());
};
```

```js title="x-notes.js"
host.on("image-upload", (event) => event.respondWith(uploadImage(event.detail.file, {
  signal: event.signal,
  onprogress: (loaded, total) => event.progress(loaded, total),   // XMLHttpRequest upload progress
})));
```

- While the request is pending, from its dispatch until it settles or <var>signal</var> aborts, `event.progress(loaded, total)` calls the asker's `progress` callback with the same two numbers. At any other time, or when the asker passed no callback, it does nothing.
- `loaded` and `total` mean what they mean on a `ProgressEvent`[^15]: the work done so far and the work in all, in units the responder chooses, with a `total` of `0` when the total is unknown.
- An exception the asker's callback throws is reported, as an event listener's exception is, and does not reach the responder.

### Who answers

Each kind of consumer answers with its own listener mechanism. Nothing new is written in markup.

| Consumer | Answers with |
| --- | --- |
| An HTML Next component | `host.on("mention-query", (event) => event.respondWith(…))` in its controller |
| Page script | `element.addEventListener("mention-query", …)` on the component's root or an ancestor, or [`RequestEvent.respond()`](#outside-a-controller) |
| Vue | a `mentionQuery` function prop, or `@mention-query="(event) => event.respondWith(…)"` |
| React | a `mentionQuery` function prop, or a generated `onMentionQuery` prop |
| Svelte | a `mentionQuery` function prop, or the generated event prop Svelte uses for the component's declared events |

The framework forms are defined in [Requests in framework components](#framework-requests). A declarative `<handler>` can observe a request through `on:` but cannot answer it.

A request travels along DOM ancestry, as every bubbling event does: its responders are listeners on the asking component's root, its DOM ancestors, and the document.

> [!future] Requests through a portal
> Content that a [`<portal>`](/declarative-components/components#portal) moves elsewhere stays logically owned by its component. When `<portal>` lands at Level&nbsp;2, a request from moved content retargets to its logical parent, so the consumer that renders the portal still answers it.

> [!future] Declarative answers and asks
> A request is asked and answered in JavaScript, by a controller or by the [`RequestEvent` static methods](#outside-a-controller). Answering one from markup, with an element such as `<respond>`, or asking one from a handler and storing its answer, with an attribute such as `into=` on `<dispatch>`, remains deferred to a later Level.

Generated TypeScript types each request from its declaration: `host.request("mention-query", …)` resolves to `{ id: string; label: string }[] | null`, and a framework's listener receives `RequestEvent<{ query: string }, { id: string; label: string }[]>`.

### Late responders {#late-responders}

A request reaches the listeners that exist when it is dispatched. Step 4 waits for consuming components' controllers, so their load order is irrelevant. A page script that loads later, such as a lazily imported setup module, or a framework that attaches listeners after its child mounts, is a **late responder**: it misses any request made before it arrived. In React, for example, a parent's `useEffect` runs after its child's.

Requests asked on each use, such as mentions and uploads, reach the late responder the next time they are asked. A request asked once at setup, such as an editor's extensions, needs a signal that a responder now exists. That signal is the `responder` event: a late responder announces itself, and the runtime relays the announcement to each component whose request went unanswered.

```js title="ui-editor.js"
host.on("connect", () => {
  let session;
  const build = () => host.request("extensions").then((extensions) => {
    session?.destroy();                                  // the document and undo history stay in the closure
    session = createEditorSession(host.refs.mount, { extensions: extensions ?? [] });
  }, () => {});                                          // rejected: disconnected before the answer
  build();
  const stop = host.on("responder", (e) => { if (e.detail.name === "extensions") build(); });
  return () => { stop(); session?.destroy(); };
});
```

```html title="page.html"
<ui-editor></ui-editor>
<script type="module" src="/htmlnext.js"></script>
<script type="module">
  // The setup module loads when the browser is idle, after the editor connected and asked.
  requestIdleCallback(() => import("./editor-setup.js"));
</script>
```

```js title="editor-setup.js"
import Highlight from "@tiptap/extension-highlight";
const { respond } = RequestEvent;
respond(document, "extensions", () => [Highlight]);   // adds the listener and announces it
```

```text
t1  editor:   host.request("extensions") → no listener → null; the runtime remembers (editor, "extensions")
t2  page:     RequestEvent.respond() adds its listener on document and announces a responder for "extensions"
t3  runtime:  the remembered request is inside document → fires responder at the editor's root, forgets it
t4  editor:   host.request("extensions") → answered → rebuilds its view, keeping the document
```

The `responder` event carries one fact: a responder for this request now exists. Its detail is `{ name }`, the request's name. These rules connect a late responder to the request it missed:

- **Remembered requests.** When a request resolves `null` at step 7 because nobody answered, the runtime records it: one record per connected instance and request name. A record is forgotten when a later request with that name from that instance is answered, when the instance disconnects, or when the runtime relays a `responder` event for it.
- **The announcement.** A page script announces itself by dispatching a bubbling `responder` event, a `CustomEvent` with detail `{ name }`, at the element it listens on: `element.dispatchEvent(new CustomEvent("responder", { bubbles: true, detail: { name: "extensions" } }))`. [`RequestEvent.respond()`](#outside-a-controller) dispatches the same announcement when it adds its listener.
- **The relay.** The runtime listens for `responder` once, on the document. For an announcement with name <var>N</var> from element <var>E</var>, it **relays**: it takes each record named <var>N</var> whose instance's root is <var>E</var> or inside <var>E</var>, in tree order, forgets the record, and dispatches a `responder` event with detail `{ name: N }` at that instance's root. The relayed event [must not]{.kw} bubble, so it never reaches the document listener as a new announcement.
- **Runtime-registered responders.** The runtime already holds the records, so a responder it registers itself dispatches no announcement. When a controller registers `host.on(N, …)`, the runtime relays for <var>N</var> from the host's root, exactly as if an announcement had come from there. A framework adapter uses the same relay at the component's root when it attaches a request listener or function prop after the controller was invoked. A name with no records relays nothing, so `host.on` needs no knowledge of which names are requests.

The asking controller decides whether to ask again, on `host.on("responder", …)`, which runs only for the runtime's relay to that instance; an announcement bubbling through its root is not delivered to it. The original promise stays resolved `null`, and the runtime never repeats a request itself: only the controller knows whether a new answer matters. New extensions mean a rebuild, while a mention list that has already closed needs nothing. A controller with no `responder` listener is unaffected.

`responder` is a host event, as `connect` and `disconnect` are. A definition [must not]{.kw} declare an `<event>` or a `<request>` named `responder`: a build tool reports it as an error, and the live parser warns and ignores that declaration.

### Checking for a responder: host.hasResponder {#has-responder}

Some features make sense only when someone answers. An editor's "Insert image" button is useless when nobody stores the image. `host.hasResponder(name)` tells the controller whether a **known responder** answers a declared request. It is reactive, so the button appears when an uploader arrives and disappears when the uploader leaves:

::: two

```html title="ui-editor.html"
<template component="ui-editor" controller="./ui-editor.js">
  <defs>
    <request name="image-upload" type="object">…</request>
    <state name="canUpload" type="boolean" value="false"></state>
  </defs>
  <div>
    <button type="button" $ref="insertImage" from:hidden="!$canUpload">Insert image</button>
    <div $ref="mount"></div>
  </div>
</template>
```

```js title="ui-editor.js"
export default function controller(host) {
  // Re-runs whenever a known image-upload responder arrives or leaves.
  host.effect(() => {
    host.state.canUpload = host.hasResponder("image-upload");
  });
  // The button's click handler asks host.request("image-upload", …),
  // as in Reporting progress.
}
```

:::

The page registers its uploader before the editor mounts, or later, when a lazily loaded module runs. The button follows either way:

```js title="app.js"
const { respond } = RequestEvent;
const stop = respond(document, "image-upload", ({ file }, { signal, progress }) =>
  uploadImage(file, { signal, onprogress: progress }));
```

```text
Registered before the editor mounts:
t1  app.js:   respond(document, "image-upload", …) records a known responder on document
t2  editor:   connects; host.hasResponder("image-upload") → true; the button shows

Registered after the editor mounts:
t1  editor:   connects; host.hasResponder("image-upload") → false; the button stays hidden
t2  app.js:   respond(document, "image-upload", …) records it and announces it
t3  runtime:  document is on the editor's path → the effect re-runs → true; the button shows
t4  app.js:   stop() removes it → the effect re-runs → false; the button hides
```

These rules define what the runtime knows and when a read changes:

- **Known responders.** The runtime keeps a record of known responders: one entry per registration, holding its target and the request name. Entries come from the three registrations that already take part in [late responders](#late-responders):
  - [`RequestEvent.respond(target, name, …)`](#outside-a-controller) adds an entry on <var>target</var>. Calling the function it returned removes it.
  - A controller's `host.on(name, …)` adds an entry on the host's root while the instance is connected. Calling the function `host.on` returned, or the instance disconnecting, removes it. `host.on` does not know which names are requests, so the record holds every name a controller listens for; only a request ever looks one up.
  - A [framework adapter](#framework-requests) adds an entry on the component's root while the request's function prop holds a function, or while a listener in the event form is attached. Unsetting the prop, detaching the listener, or unmounting the component removes it.
- **The lookup.** If the definition declares no `<request>` named <var>name</var>, `host.hasResponder(name)` [must]{.kw} throw a `TypeError`, as `host.request` rejects for one. Otherwise it returns `true` when the record holds an entry for <var>name</var> on any object in the event path of a request dispatched at the instance's root: the root, its ancestors across shadow boundaries, the document, and the window. An entry the instance's own controller added on its own root does not count: a component listens for its own request name to [forward a child's request](#request-event), and lets its own request bubble past.
- **Re-evaluation.** `host.hasResponder` is a reactive read: an effect that called it re-runs when its result changes. A change to the entries for <var>name</var> on an object <var>E</var> re-evaluates every read of <var>name</var> by an instance whose root is <var>E</var> or inside <var>E</var>. Additions are driven by the late-responder mechanism: the runtime's document listener re-evaluates on each `responder` announcement for <var>name</var> from <var>E</var>, and the runtime's relay for <var>name</var> from a root re-evaluates as it relays, when `host.on` or an adapter registers. A removal re-evaluates the same reads directly. Moving a root changes its path only by disconnecting and reconnecting it, and an effect runs again when its instance connects.
- **No new event.** Neither change dispatches anything. The `responder` event keeps its one meaning, that a responder now exists for a request that went unanswered, and the runtime still relays it only to instances with a remembered request.

A **known** responder is one the runtime saw registered. A plain `element.addEventListener("image-upload", …)` answers requests, but the DOM offers no way to list an element's listeners, so the runtime cannot detect it: `hasResponder` returns `false` for it, though a request would still be answered. An announcement dispatched by hand is the same: it relays to remembered requests and adds no entry. Code that wants to be discoverable uses `RequestEvent.respond()`. Read `true` as "someone will answer", not as a promise of a non-`null` answer, since a responder may answer `null`. Read `false` as "no known responder": an asker that asks anyway is never wrong.

### Requests outside a controller {#outside-a-controller}

Code that is not a controller has no `host`: a page script, a hand-written custom element, the code around a framework component. It answers, asks, and checks with three static methods on `RequestEvent`, the interface every request already uses:

```ts
interface RequestEventConstructor {
  /** Answer `name` requests that reach `target`, and announce the responder. Returns a function that removes it. */
  respond<Detail = unknown, Answer = unknown>(target: EventTarget, name: string, responder: Responder<Detail, Answer>): () => void;
  /** Ask `name` at `target`. Resolves to the answer, unchecked, or null when none answered. */
  request<Answer = unknown>(target: EventTarget, name: string, detail?: unknown, options?: RequestOptions): Promise<Answer | null>;
  /** Whether a known responder for `name` is on `target`'s event path, at the moment of the call. */
  hasResponder(target: EventTarget, name: string): boolean;
}
declare var RequestEvent: RequestEventConstructor;

type Responder<Detail, Answer> = (
  detail: Detail,
  init: { signal: AbortSignal; progress: (loaded: number, total: number) => void },
) => Answer | null | PromiseLike<Answer | null>;
```

```js
const { respond, request, hasResponder } = RequestEvent;
```

The three are **static operations that do not use `this`**. A destructured call, `request(element, "image-upload", …)`, behaves exactly as `RequestEvent.request(element, "image-upload", …)`, so callers destructure them once, as above. `Promise.withResolvers()`[^18] is different: it reads `this` to choose the promise constructor, so a detached call throws.

They are static methods on `RequestEvent` so that the proposal adds no global name. Methods on `EventTarget` or `Element` would collide with properties that existing components already define; a custom element with its own `request()` method is ordinary. The platform groups helpers on an interface the same way: `AbortSignal.any()` and `AbortSignal.timeout()`[^13], `Response.json()`[^16], `URL.canParse()`[^17], and `Promise.withResolvers()`[^18].

### Answering outside a controller: RequestEvent.respond {#request-event-respond}

`respond(target, name, fn)` gives a plain page the same function signature as [framework function props](#framework-requests). It adds a listener for <var>name</var> on <var>target</var> that calls `event.respondWith(fn(event.detail, { signal: event.signal, progress: (loaded, total) => event.progress(loaded, total) }))`, records a [known responder](#has-responder) on <var>target</var>, then announces a responder for <var>name</var> at <var>target</var>. It returns a function that removes both the listener and the entry. The function always answers, so it returns `null` when it has no answer:

```js
const { respond } = RequestEvent;
const stop = respond(document, "link-resolve", ({ href }) =>
  isLocal(href) ? lookupTitle(href) : null);       // null: the editor keeps the link as typed
```

### Asking outside a controller: RequestEvent.request {#request-event-request}

`request(target, name, detail, { signal, progress })` asks with the same protocol as `host.request`. A hand-written custom element asks for an upload this way:

```js title="photo-field.js"
const { request } = RequestEvent;

class PhotoField extends HTMLElement {
  #upload;
  async store(file) {
    this.#upload?.abort();                             // a newer file supersedes the last one
    this.#upload = new AbortController();
    const image = await request(this, "image-upload", { file }, {
      signal: this.#upload.signal,
      progress: (loaded, total) => this.setProgress(loaded / total),
    });
    if (image) this.setSrc(image.src); else this.keepPreview();
  }
}
```

When code calls <code>request(<var>target</var>, <var>name</var>, <var>detail</var>, <var>options</var>)</code>, the runtime [must]{.kw} run these steps:

1. Let <var>signal</var> be <var>options</var>`.signal` when given, or else a new `AbortSignal` that never aborts. If <var>signal</var> is aborted, return a promise rejected with its reason.
2. If <var>target</var> is a node, wait as in step 4 of [`host.request`](#host-request) for every component whose root is <var>target</var> or a DOM ancestor of it. If <var>signal</var> aborts while waiting, reject with its reason.
3. Create a `RequestEvent` whose `type` is <var>name</var>, whose `detail` is <var>detail</var> or `null`, and whose `signal` is <var>signal</var>. It bubbles, is composed, and is not cancelable.
4. Dispatch it at <var>target</var>.
5. If no listener called `respondWith` during that dispatch, resolve with `null`.
6. Otherwise, wait for the value passed to `respondWith`, forwarding [progress](#request-progress) meanwhile. If <var>signal</var> aborts first, reject with its reason and discard the value when it arrives. If the value rejects, reject with that reason. Otherwise resolve with the value.
{.algo}

It is the same protocol, so a responder receives the same `RequestEvent` and cannot tell `RequestEvent.request` from `host.request`. The difference is what the asker brings:

- **No declaration, so no runtime check.** Without a `<request>`, neither the detail nor the answer is checked. A TypeScript caller types the answer with the generic: `request<{ src: string }>(this, "image-upload", { file })` resolves to `{ src: string } | null`.
- **No instance, so no connection signal and no remembered request.** The caller's own signal is the only way to withdraw the request. An unanswered one is not remembered, because the runtime relays a late `responder` only to a component's root. Code that asks once at setup and must hear about a late responder belongs in a controller.

### Checking outside a controller: RequestEvent.hasResponder {#request-event-has-responder}

`hasResponder(target, name)` returns `true` when the record of [known responders](#has-responder) holds an entry for <var>name</var> on any object in the event path of a request dispatched at <var>target</var>, and `false` otherwise. It sees what `host.hasResponder` sees, with the same limit: a plain `addEventListener` is invisible to it. It differs in two ways. It reads the record at the moment of the call and is not reactive, so nothing tells its caller when the result changes. And it counts every entry on <var>target</var>, because no controller owns the call.

It costs nothing beyond `host.hasResponder`, which performs the same lookup, and it gives code that asks through `RequestEvent.request` the choice a controller has: to offer a feature only when someone will answer, for example when a hand-written element renders its toolbar. Code that must follow changes as they happen belongs in a controller, where the read is reactive.

> [!note] Until browsers implement RequestEvent
> A polyfill provides the same interface as a module export. Callers import `RequestEvent` and destructure it: `import { RequestEvent } from "./request-event.js"; const { respond, request, hasResponder } = RequestEvent;`. Native code is identical without the import line.

### Server rendering

Controllers never run on a server, so a server never makes or answers a request. A server-rendered component renders its declarative baseline, and its controller asks once it connects in the browser. Because answers are never serialized, a request adds nothing to the rendered form or to hydration.

> [!note] Grounded in the platform
> Answering an event with `respondWith` is the shape of the Service Worker `FetchEvent`[^11], which also stops propagation once answered. The `signal` follows `NavigateEvent`[^12] and the DOM's `AbortSignal`[^13], and `progress` follows `ProgressEvent`[^15]. The Web Components Community Group Context Protocol[^14] uses the same idea, an event that carries a way to answer, for exchanging values between JavaScript components; its `context-provider` event and `ContextRoot` are the precedent for announcing a late responder and listening once at the document. HTML Next declares the request in the definition, so its types are known to build tools and framework targets without running anything.

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
> The proposal defines browser behavior. Controller source has no required package import and no polyfill registration call. Until browsers implement the feature, a polyfill performs the same resolution, default-export check, and per-instance invocation behind the declarative surface. Build targets may statically import the same default export and pass it their host adapter. None of those implementation paths changes component source.

> [!note] Sharing the custom-element namespace
> A hyphenated tag like `x-chart` is also a valid *custom element* name, so the two registries occupy one namespace, and precedence must be defined, not left to a race. The rule: **a registered custom element wins**. If `customElements.get(tag)` is defined, the browser owns that tag (it upgrades and runs the element's own lifecycle), and HTML Next does not lower it, an author who registers a custom element for a tag has opted that tag out of HTML Next. The runtime checks this before lowering rather than tearing out a live custom element.

### Definitions and instances added after boot

An application may insert an inline `<template component>` definition or a new component instance after the runtime starts. The in-browser runtime uses `MutationObserver` to discover additions, validate and register new definitions, lower new instances, and connect their controllers. If an instance arrives before its definition, it lowers when that definition becomes available. The definition still binds behavior through `controller="…"` and a callable default export; the controller needs no package import or registration call.

Later discovery follows the same duplicate-definition, custom-element precedence, dependency, and trust rules as startup. A registered definition stays in the document registry after its carrier is consumed; inserting a second definition for that tag is an error. Inline definitions are inert data whose markup is validated before lowering. Their downstream live/imported dependencies still require application-owned resolution and import-map trust; a newly inserted definition cannot install policy. Sanitized `$html` and CMS content remain excluded from definition discovery.

The observer batches additions and removals, ignores its own completed lowering, and connects each instance once. Removal disconnects the instance and disposes its owned work; later reinsertion reconnects it. A move that stays within the same document during one mutation batch preserves the connection. Compiled/AOT builds discover the graph ahead of time and use target lifecycle hooks; they do not use `MutationObserver` for component discovery.

### Loading a controller {#loading-a-controller}

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
> Importing a component root trusts its dependency closure, including a declared controller. HTML Next does **not** pretend otherwise. The improvement over HTML Imports[^6] is architectural: a definition is parsed under one closed declarative grammar; arbitrary classic scripts and inline handlers are rejected; imperative behavior has one explicit `controller` attribute, and any third-party script is a visible declared `src`; and those edges use the existing ES-module loader and script element instead of an imported-document script lifecycle.
>
> ES modules provide standardized fetching, CORS, CSP, dependency graphs, deduplication, and one-time evaluation. They do **not** sandbox authority. A controller and its transitive module graph are trusted page JavaScript, just like the JavaScript shipped by a custom element or an installed UI package. So is a declared script.

## Creating components from code: componentRegistry {#component-registry}

Most components exist because markup invokes them. Sometimes code has to make one instead: an editor drawing a callout inside the document it manages, a virtual list creating rows as they scroll into view, a library rendering into a region it owns. Inserting `<ui-callout>` and letting the runtime find it does not work there. [Lowering](/declarative-components/components) replaces the authored element with the component's native root, so the code is left holding an element that is no longer in the document.

`componentRegistry` is how code takes part instead. It creates a component's finished native root directly, updates that instance's props later, and answers whether a definition is registered yet. It is modeled on the custom elements registry, `customElements`[^19]: the same names where they mean the same thing, and one registry for each document.

```js
const { create, update, whenDefined } = componentRegistry;

await whenDefined("ui-callout");                  // the definition may still be loading

const heading = document.createElement("span");
heading.slot = "heading";                         // a node picks its slot, as in markup
heading.textContent = "Before you start";
const callout = create("ui-callout", { props: { tone: "tip" }, content: [heading, "Install first."] });

editorBody.append(callout);                       // connects, like any authored instance
update(callout, { tone: "warning" });             // later: the tone changes, the heading stays
callout.addEventListener("close", onClose);       // its events, on its root, as for any instance
```

That instance is indistinguishable from one lowered from this markup:

```html
<ui-callout tone="tip"><span slot="heading">Before you start</span>Install first.</ui-callout>
```

### The interface {#component-registry-interface}

```ts
interface ComponentRegistry {
  /** Register the definition a <template component> carries. */
  define(carrier: HTMLTemplateElement): void;
  /** The definition registered for `tag`, or undefined. */
  get(tag: string): ComponentDefinition | undefined;
  /** Resolves with the definition once `tag` is registered. */
  whenDefined(tag: string): Promise<ComponentDefinition>;
  /** Lower the authored invocations inside `root` now. */
  upgrade(root: Node): void;
  /** Create an instance of `tag`: its native root, not yet connected. */
  create<K extends keyof ComponentTagMap>(tag: K, init?: ComponentInit<ComponentTagMap[K]["props"]>): ComponentTagMap[K]["element"];
  create(tag: string, init?: ComponentInit): Element;
  /** Set props on an instance, as attributes on an invocation or framework props would. */
  update(element: Element, props: Readonly<Record<string, unknown>>): void;
}

interface ComponentInit<Props = Readonly<Record<string, unknown>>> {
  /** The instance's props, as an invocation's attributes would set them. */
  props?: Props;
  /** The nodes an invocation would contain: a fragment, or nodes and strings, as append() takes. */
  content?: DocumentFragment | Iterable<Node | string>;
}

interface ComponentDefinition {
  readonly tag: string;
}

/** Each component adds its tag here, as HTMLElementTagNameMap does for createElement. */
interface ComponentTagMap {}

declare var componentRegistry: ComponentRegistry;
```

```js
const { define, get, whenDefined, upgrade, create, update } = componentRegistry;
```

Each member corresponds to a `customElements` member, or to the DOM operation that covers the same need for custom elements:

| `componentRegistry` | Custom elements | What differs |
| --- | --- | --- |
| `define(carrier)` | `customElements.define(name, constructor)` | It takes the `<template component>` carrier, the declarative definition, and reads the tag from its `component` attribute. There is no class. |
| `get(tag)` | `customElements.get(name)` | It returns the definition, not a constructor. |
| `whenDefined(tag)` | `customElements.whenDefined(name)` | It resolves with the definition. |
| `upgrade(root)` | `customElements.upgrade(root)` | Lowering replaces each authored element with its native root; a custom element upgrades in place. |
| `create(tag, init)` | `document.createElement(name)`[^20] | It returns the native root. It exists because an authored element would be replaced, so `createElement` cannot serve. |
| `update(element, props)` | setting properties on the element | It is the one way code sets an instance's props: the same channel as attributes on an invocation and framework props. |

The members are **static operations that do not use `this`**, so a destructured call behaves exactly as a call on `componentRegistry`, as with [`RequestEvent`'s statics](#outside-a-controller).

### Defining and waiting {#component-registry-define}

The runtime defines every definition it [discovers](#definitions-and-instances-added-after-boot), and `define(carrier)` registers one from code. Either way, the same rules apply, and when code calls <code>define(<var>carrier</var>)</code> the runtime [must]{.kw} run these steps:

1. If <var>carrier</var> is not a `<template>` element with a `component` attribute, throw a `TypeError`.
2. Validate it as a discovered definition is validated. If it is invalid, throw a `SyntaxError` `DOMException` that names the first error's code.
3. Let <var>tag</var> be its `component` attribute's value. If `customElements.get(tag)` is defined, throw a `NotSupportedError` `DOMException`: [a registered custom element wins](#binding-the-definition-owns-the-controller-edge).
4. If a definition for <var>tag</var> is already registered, return when it is the same definition, and otherwise throw a `NotSupportedError` `DOMException` (HR001).
5. Register it, resolve every pending `whenDefined(tag)` with it, and lower the authored invocations of <var>tag</var> already in the document.
{.algo}

`get(tag)` returns the registered `ComponentDefinition` or `undefined`. This proposal specifies only the definition's `tag`; exposing more of its contract is open. `whenDefined(tag)` rejects with a `SyntaxError` `DOMException` when <var>tag</var> is not a valid custom element name, resolves at once when the tag is registered, and otherwise resolves when it is. A controller whose code creates a component that its template does not use declares the edge with `<link rel="component">`, like any composed component, so the definition loads before the controller asks for it.

`upgrade(root)` lowers every authored invocation in <var>root</var>'s inclusive subtree whose definition is registered, in tree order and synchronously, as discovery would. It skips invocations already lowered and leaves invocations of unregistered tags alone. It lets code that has just inserted markup use the resulting instances without waiting for the runtime's next discovery batch.

### Creating an instance {#component-registry-create}

When code calls <code>create(<var>tag</var>, <var>init</var>)</code>, the runtime [must]{.kw} run these steps:

1. If `customElements.get(tag)` is defined, throw a `NotSupportedError` `DOMException`.
2. Let <var>definition</var> be the definition registered for <var>tag</var>. If there is none, throw a `NotFoundError` `DOMException`; code that cannot be sure of the order calls `whenDefined` first.
3. Let <var>nodes</var> be the children of <var>init</var>`.content` when it is a `DocumentFragment`, or else its items in order, each string replaced by a new `Text` node holding it.
4. For each entry of <var>init</var>`.props`, if <var>definition</var> declares no prop of that name, throw a `TypeError`.
5. Create the instance as lowering an invocation of <var>tag</var> creates one. Each prop of <var>init</var>`.props` is an input checked as [an accepted value](#accepted-values-and-prop-inputs), exactly as the matching attribute would be. <var>nodes</var> are the invocation's child nodes, so each is assigned to the slot its `slot` attribute names, or else to the default slot, as authored children are.
6. Return the instance's native root.
{.algo}

The root is not yet connected. Inserting it connects the instance and removing it disconnects it, by the same rules as [any instance](#definitions-and-instances-added-after-boot): its controller runs when it first connects, its effects start and stop with its connection, and a move within one mutation batch keeps the connection. It is an instance in every respect, so it dispatches its events at its root, asks its requests, and takes `update`. Native attributes that are not props, such as `id` or `aria-label`, are set on the returned root with `setAttribute`, as on any element.

`create` always makes an HTML Next instance, a native root with its runtime behavior attached, never a framework's component, even when the calling code runs inside a Vue, React, or Svelte application. Code creates components where a framework does not render, such as a document an editor library manages, so the instance lives outside the framework's tree. The [equivalence contract](/declarative-components/targets) makes it the same element a framework target would render.

### Updating props {#component-registry-update}

When code calls <code>update(<var>element</var>, <var>props</var>)</code>, the runtime [must]{.kw} run these steps:

1. If <var>element</var> is not the native root of a component instance, whether created by `create` or lowered from markup, throw a `TypeError`.
2. For each entry of <var>props</var>, if the instance's definition declares no prop of that name, throw a `TypeError`.
3. For each entry, when the value is `null` or `undefined`, return the prop to its implicit default. Otherwise, make it the prop's explicit input, checked as [an accepted value](#accepted-values-and-prop-inputs) exactly as the matching attribute would be.
4. Render the changes in the instance's next flush, batched with its state writes. A disconnected instance renders them when it reconnects.
{.algo}

### Types {#component-registry-types}

`ComponentTagMap` follows TypeScript's `HTMLElementTagNameMap`[^21], which types `document.createElement("input")` as an `HTMLInputElement`. A tool that emits declarations for a component adds an entry, so `create` types its props and its root:

```ts
interface ComponentTagMap {
  "ui-callout": { element: HTMLDivElement; props: { tone?: "info" | "tip" | "warning"; heading?: string } };
}
```

### Why a registry {#component-registry-why}

Requests needed only three operations, so they live as statics on the interface every request already uses, and add no global name. Components need more: definitions are per-document state with a lifecycle of their own. They are defined, waited for, upgraded and created from, which is exactly what `CustomElementRegistry` models for custom elements. A registry is also where a later level can scope definitions to a part of the document, as scoped custom element registries[^22] do with `new CustomElementRegistry()`. Scoping is not proposed here.

This adds two global names, `ComponentRegistry` and `componentRegistry`, which parallel `CustomElementRegistry` and `customElements`. The instance is not called `components`: a new global must not collide with names that pages already define, and an everyday word like that is far more likely to.

Controllers run in the browser only, and so do `create` and `update`. A server renders authored invocations.

> [!note] Until browsers implement componentRegistry
> A polyfill provides the same object as a module export. Callers import it and destructure it: `import { componentRegistry } from "./component-registry.js"; const { create, update, whenDefined } = componentRegistry;`. Every HTML Next bundle on a page shares one registry for each document, so code can create any registered component, whichever bundle defined it. Native code is identical without the import line.

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
    <h1>{$title}</h1>
    <template $match>
      <p $when="$metrics.pending">Loading…</p>
      <x-chart $else from:series="$metrics.value.series"></x-chart>
    </template>
  </section>
</template>
```

A declares its dependency on B with `<link rel="component">` and mentions no script. Its behavior, a reactive `<data>` read and a `$match`, is entirely declarative.

```html title="/components/b.html"
<!-- /components/b.html — declarative markup plus its controller dependency. -->
<template component="x-chart" controller="./b.js">
  <defs>
    <prop name="series" type="list" required>The data to plot.</prop>
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
    const series = host.props.series.value;
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
> The trust boundary stays where [Security](/declarative-components/security) puts it: at the root component package or live URL the application deliberately imports.
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

The example is one implementation's converter output. `adaptVue` and its package import are build tooling that implementation generates, not a browser API this proposal defines.

```html title="XMap.vue (generated)"
<!-- Vue output. The controller body is reused verbatim; only the host is adapted. -->
<script setup>
import controller from "./x-map.js";
import { adaptVue } from "./component-runtime/vue.js";

const props = defineProps({ center: { type: Array, default: () => [0, 0] } });
const canvas = ref();
adaptVue(controller, { refs: { canvas }, props });
</script>

<template>
  <div ref="canvas"></div>
</template>
```

This works because `host` is deliberately tiny, and every target already has all of it natively: lifecycle (Vue `onMounted`/`onUnmounted`, Svelte `onMount`/`onDestroy`, Solid `onMount`/`onCleanup`, React `useEffect`), effects (Vue `watchEffect`, Svelte `$effect`, Solid `createEffect`), refs (Vue `ref`, Svelte `bind:this`, React `useRef`), props for `host.props`, and mutable and computed state and context for `host.state`, and resources for `host.data`. `host.scripts` needs no framework primitive: the adapter inserts the same `<script>` element and follows the same [head management](/declarative-components/components#head-management) rules. `$ref="name"` maps to each target's ref idiom; `host.dispatch` to its event mechanism.

> [!note] React is the one that needs a bridge
> React has no native fine-grained reactivity, so its adapter backs `host.effect` and `host.state` with an external store (via `useSyncExternalStore`) rather than a signal. That wart is contained to the React adapter; the controller and every other target are unaffected.

### Requests in framework components {#framework-requests}

A framework component answers a [request](#requests) with a function that returns the answer, the way Vue, React, and Svelte authors already pass a loader such as react-select's `loadOptions`. The event form remains available.

```html
<!-- Vue -->
<UiEditor :mention-query="({ query }, { signal }) => searchPeople(query, signal)" />
<!-- React -->
<UiEditor mentionQuery={({ query }, { signal }) => searchPeople(query, signal)} />
<!-- Svelte -->
<UiEditor mentionQuery={({ query }, { signal }) => searchPeople(query, signal)} />
```

A generated framework component and its host adapter [must]{.kw} follow this contract:

- **The function prop.** For each declared `<request>`, the component accepts a prop named after the request in camelCase: `mention-query` becomes `mentionQuery`. Its value is a function `(detail, { signal, progress }) => answer`, where the answer is the answer value, `null`, or a promise of either. The function always answers, so it returns `null` when it has none.
- **The responder.** Before it invokes the controller, the host adapter adds one listener per declared request on the component's root. The listener reads the prop when the request arrives, so a new function needs no rewiring. When the prop holds a function, the listener calls `event.respondWith(fn(event.detail, { signal: event.signal, progress: (loaded, total) => event.progress(loaded, total) }))`; when it is unset, the request bubbles on to the component's ancestors.
- **Late responders.** Setting the prop after the controller was invoked, when it was unset, relays for that request from the root, as `host.on` does for a [late responder](#late-responders).
- **Known responders.** While the prop holds a function, or a listener in the event form is attached, the adapter records a [known responder](#has-responder) on the root. It removes the entry when the prop is unset, the listener is detached, or the component unmounts.
- **The event form.** The component also accepts the event form for each request: Vue's `@mention-query`, React's `onMentionQuery`, and Svelte's event prop for the component's declared events. The adapter attaches those listeners before it invokes the controller, and relays for the request from the root when one is attached afterwards. The event form serves listeners on an ancestor and consumers that need the event itself.
- **Names.** A request whose camelCase name equals a declared prop's camelCase name is a build error.
- **Types.** Generated types give each function prop the request's detail and answer types:

```ts
mentionQuery?: (
  detail: { query: string },
  init: { signal: AbortSignal; progress: (loaded: number, total: number) => void },
) => Answer | null | PromiseLike<Answer | null>;   // Answer is { id: string; label: string }[]
```

The function prop exists only on the framework side, while the HTML component keeps its attribute-only props. Its semantics are the request's: a stale answer is dropped, the answer is checked against `returns`, and an unanswered request resolves `null`. A function prop also avoids the mistake an event handler invites: Vue, React, and Svelte ignore a handler's return value, so `@mention-query="searchPeople"` would answer nothing.

## Lifecycle and hydration

A controller's `connect` fires when the instance connects, on first mount *and* on any later reconnection, matching the custom-element reaction rather than a once-only *mount*[^1]. On a server-rendered page, the markup arrives already lowered and inert; the controller attaches at **hydration**, where `connect` first runs in the browser. `disconnect` fires on removal, running teardown. Because the first render never depends on the controller, hydration is adopt-in-place: the controller binds to existing nodes rather than rebuilding them (see [Components](/declarative-components/components)).

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
: `element`, `state` (declared state only is writable), `reset`, `refs`, `elements`, `scripts`, `on`, `effect`, `dispatch`, and `request` and `hasResponder` when the component declares a request

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

::: {.entry name="componentRegistry" role="create and update components from code"}
Members
: `define`, `get`, `whenDefined`, `upgrade`, `create`, and `update`; static operations that do not use `this`

Creates
: an HTML Next instance's native root, never a framework's component

Native kin
: `customElements` (`CustomElementRegistry`) and `document.createElement`

Scope
: one registry for each document, shared by every HTML Next bundle on the page

Level
: [L2+]{.pill .soon} reserved
:::

## References

[^1]: WHATWG HTML, [custom elements](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-elements-core-concepts) (`connectedCallback`/`disconnectedCallback`): a controller supplies the same per-instance behavior and lifecycle to a data-defined component instead of requiring a class registration.
[^2]: WHATWG HTML, [ElementInternals](https://html.spec.whatwg.org/multipage/custom-elements.html#the-elementinternals-interface) and [custom states](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) with CSS [:state()](https://developer.mozilla.org/docs/Web/CSS/:state): the native model for the internal state of an element, generalized here from boolean flags to values.
[^3]: CSS Scoping, [Shadow Parts](https://drafts.csswg.org/css-shadow-parts/) (`part` / `::part()`) and [:host](https://developer.mozilla.org/docs/Web/CSS/:host): the platform words for a component element seen from inside, and for a named internal piece exposed to outside CSS.
[^4]: TC39, [Signals](https://github.com/tc39/proposal-signals) (`State`, `Computed`, and `Watcher`): a candidate low-level basis for `host.effect`. The proposal explicitly does not provide effects, scheduling, DOM ownership, or automatic disposal; this DOM-facing layer supplies them.
[^5]: Lit, [Reactive Controllers](https://lit.dev/docs/composition/controllers/) (`hostConnected`/`hostDisconnected`, a controller object attached to a host): direct prior art for the controller-plus-host shape, adapted to a definition that contains no code.
[^6]: W3C, [HTML Imports](https://www.w3.org/TR/webcomponents/#imports) (discontinued): the approach this layer deliberately avoids, fusing markup, style, and executing script into one imported document.
[^7]: WHATWG HTML, [module-script fetching](https://html.spec.whatwg.org/multipage/webappapis.html#fetch-a-single-module-script), [Content Security Policy](https://developer.mozilla.org/docs/Web/HTTP/Guides/CSP), and [Subresource Integrity](https://developer.mozilla.org/docs/Web/Security/Defenses/Subresource_Integrity): the existing loading and deployment controls used by controllers.
[^8]: WHATWG DOM, [CustomEvent](https://dom.spec.whatwg.org/#interface-customevent) and [dispatchEvent](https://dom.spec.whatwg.org/#dom-eventtarget-dispatchevent): what `host.dispatch` lowers to.
[^9]: WHATWG HTML, [`HTMLSlotElement.assignedElements()`](https://html.spec.whatwg.org/multipage/scripting.html#dom-slot-assignedelements): the native way a component reads what a consumer projected, rather than searching its own subtree for it.
[^10]: WHATWG HTML, [the input element's value, content attribute, and dirty value flag](https://html.spec.whatwg.org/multipage/input.html#the-input-element) and [bad input](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#suffering-from-bad-input): separate written input, current value, and validity inform this prop handle; the API is not identical to an `<input>`.
[^11]: W3C Service Workers, [`FetchEvent.respondWith()`](https://w3c.github.io/ServiceWorker/#fetch-event-respondwith): an event answered with a value or a promise, which also stops its propagation.
[^12]: WHATWG HTML, [`NavigateEvent`](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-navigateevent-interface) (`intercept()` and `signal`): an event whose handler takes over asynchronous work and receives a signal that aborts when the work is no longer wanted.
[^13]: WHATWG DOM, [`AbortSignal`](https://dom.spec.whatwg.org/#interface-AbortSignal), [`AbortSignal.any()`](https://dom.spec.whatwg.org/#dom-abortsignal-any), and [`AbortSignal.timeout()`](https://dom.spec.whatwg.org/#dom-abortsignal-timeout): the platform's cancellation primitive, whose helpers are static methods on the interface.
[^14]: Web Components Community Group, [Context Community Protocol](https://github.com/webcomponents-cg/community-protocols/blob/main/proposals/context.md): an event-based protocol in which a requesting element dispatches an event carrying a callback and the nearest provider answers it; a late provider announces itself with a `context-provider` event, which a `ContextRoot` listens for.
[^15]: XMLHttpRequest Standard, [`ProgressEvent`](https://xhr.spec.whatwg.org/#interface-progressevent) (`loaded` and `total`): the platform's progress shape, whose `total` is `0` when the length is unknown.
[^16]: WHATWG Fetch, [`Response.json()`](https://fetch.spec.whatwg.org/#dom-response-json): a static method that builds a response, offered on the interface instead of as a global function.
[^17]: WHATWG URL, [`URL.canParse()`](https://url.spec.whatwg.org/#dom-url-canparse): a static check offered on the interface it concerns.
[^18]: ECMAScript, [`Promise.withResolvers()`](https://tc39.es/ecma262/#sec-promise.withResolvers): a static helper on `Promise`; it reads its `this` value as the promise constructor, so it fails when called detached.
[^19]: WHATWG HTML, [`CustomElementRegistry`](https://html.spec.whatwg.org/multipage/custom-elements.html#customelementregistry) (`define`, `get`, `whenDefined`, and `upgrade`), reached through `customElements`: the registry `componentRegistry` is modeled on.
[^20]: WHATWG DOM, [`document.createElement()`](https://dom.spec.whatwg.org/#dom-document-createelement) and its `ElementCreationOptions` dictionary: how code creates an element, and the precedent for an options dictionary such as `ComponentInit`.
[^21]: TypeScript, [`HTMLElementTagNameMap`](https://github.com/microsoft/TypeScript/blob/main/src/lib/dom.generated.d.ts) in the DOM library declarations: the map from tag to element type that types `createElement`, which `ComponentTagMap` follows.
[^22]: WICG, [Scoped Custom Element Registries](https://github.com/WICG/webcomponents/blob/gh-pages/proposals/Scoped-Custom-Element-Registries.md): registries created with `new CustomElementRegistry()` and attached to a shadow root or document, the model for scoping component definitions at a later level.

## Component modules and browser connection {#modules}

A component may link an ES module with `module="./product-card.js"`. Its named `connect` export is browser connection behavior:

```html
<template component="product-card" module="./product-card.js">
  <defs><prop name="product" type="object({ name: string, price: number })" required>Product.</prop></defs>
  <article><h2>{$product.name}</h2></article>
</template>
```

```js
export function connect(host, { signal }) {
  const observer = new ResizeObserver(([entry]) => {
    host.root.style.setProperty('--card-width', `${entry.contentRect.width}px`);
  });
  observer.observe(host.root);
  return () => observer.disconnect();
}
```

A module is imported under ordinary ESM URL resolution and lifetime rules. `connect` runs for each browser activation of an instance and may return cleanup, synchronously or asynchronously. Deactivation aborts its signal and runs cleanup. Cleanup resolving after deactivation runs immediately. A retained reconnection preserves component state and starts fresh connection behavior. A connected move does not create a new lifetime. Browser-only APIs in `connect` and `on:connect` are valid and are not invoked or shimmed by server rendering. Other module exports do not implicitly become expression names.

A renderer may render the template with supplied typed props without importing browser behavior. Compatible source libraries may evaluate data separately and supply binding records for adoption, but no component is required to make its browser behavior runnable on a server. File discovery, private modules, data-source conventions and server execution phases belong to the host's integration.

The existing `controller` default callback remains a compatibility form with its existing once-per-instance behavior. `controller` and `module` on the same definition are a conformance error. Migrating a callback to `connect` adopts connection-scoped cleanup; an automatic export rename is not sufficient for arbitrary effectful callbacks.
