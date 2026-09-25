---
title: Reactivity & Data
order: 5
blurb: state · computed · data · effects · lifecycle
eyebrow: Declarative HTML Components Level 1 · proposed shapes
status: Stage 0 · Level 1 proposal
---

# Reactivity & Data

Reactivity is a **declared dependency graph in markup**: local state, derived values, and external resources, each with a distinct lifecycle. The graph is statically analyzable, so it lowers to React state, Vue refs, Svelte runes, or a signal-based browser runtime: one semantics, many backends, no `eval()`.

## Reactive values and resources

HTML Next keeps a few concepts separate rather than overloading one element, because their lifecycles differ. All of them are declarations: they live in the definition's `<defs>` region, not in the visible markup (see [Components](/html-next/components)).

| Element | Is | Changes when |
| --- | --- | --- |
| `<state name :value>` | a local mutable value | `<set>` runs in a handler, or `bind:` writes it |
| `<computed name from>` | a pure value derived from others | nothing, recomputed from its dependencies |
| `<data name src>` | a remote resource: a read source or write sink | its params; fetched or synchronized reactively |

```html
<state name="query" value="">        <!-- literal string -->
<state name="page" :value="1">        <!-- number, via the colon -->
<state name="rows" type="list(object({ id: string, label: string }))" :value="[]">
                                      <!-- declared type, as a prop's -->
<computed name="hasQuery" from="query != ''">  <!-- derived boolean -->
```

The design, a declared dependency graph that can be analyzed statically rather than traced at runtime, has deep prior art in signals and fine-grained reactivity[^5]: Solid signals and `createMemo` and Angular signals are its closest current relatives, with Knockout observables as the historical ancestor. RxJS is a deliberate contrast, it models push streams, not the settled value cells `<state>` and `<computed>` are.

A `<state>` may declare a `type` in the same type syntax props use (see [Types](/html-next/types)). Without one, its type is its initial value's: `:value="false"` is a boolean, `:value="[]"` a list whose items are unknown. Declare the type when the initial value cannot say what the state will hold, such as an empty list of records; tools and converters then know each item's fields.

> [!note] The colon carries the type
> `<set>` mirrors `<state>` exactly: same `name`, same `:value`. A plain attribute is a string; the `:` prefix makes the value a typed expression. `:value="false"` is the boolean, `value="false"` the five-character string.

## <data>: a declared, reactive resource

This is HTML Next's standards-shaped answer to htmx[^1]: instead of `hx-get`/`hx-trigger`/`hx-target` string attributes swapping opaque HTML, a `<data>` element declares a **typed, reactive resource** whose parameters are visible right where it lives. For a read, each `<param :value>` subscribes to the state it binds, so the set of params *is* the dependency graph: change one and the resource refetches, and bindings that read it re-render. Nothing triggers it imperatively. This is the surface Solid `createResource` already ships[^6], a resource whose fetch re-runs on source change and exposes loading and error; TanStack and Vue Query are the same idea with a params-keyed cache.

```html
<data name="search" src="/api/search" type="object" debounce="200ms">
  <param name="q" :value="query">     <!-- subscribes to query: refetches when it changes -->
  <param name="page" :value="page">
</data>
```

Params are serialized, never interpolated into a URL string. A `{name}` placeholder in `src` is filled from the matching `<param>` (RFC&nbsp;6570 URI Templates)[^2]; on a read, params not named in the template become the query string. There is no string concatenation, and therefore no injection surface.

> [!norm] Expanded request methods
> `<data method>` is an **ASCII-case-insensitive enumerated attribute** with lowercase canonical keywords. Level&nbsp;1 keywords are `get`, `query`, `post`, `put`, `patch`, and `delete`. Before constructing a request, an implementation maps the selected keyword to `GET`, `QUERY`, `POST`, `PUT`, `PATCH`, or `DELETE`; `patch` and `PATCH` both produce HTTP `PATCH`. This rule is explicit because Fetch normalizes only a limited set of methods and does not uppercase `patch` for the caller.[^9]
>
> `get` follows the read lifecycle using URL query parameters. `query` follows the read lifecycle while encoding non-identity params as request content with the selected media type, as defined by RFC&nbsp;10008.[^10] Both run on connection, re-run when a parameter changes, and cancel stale in-flight reads. The other methods follow the write lifecycle only when a send policy is present. The HTTP verb describes the request; it does not turn a command into reactive synchronization.
>
> The keywords follow HTML's lowercase enumerated-attribute convention and map to uppercase HTTP methods before request construction. The form action `dialog` is not an HTTP method and is not valid on `<data>`.

A `<data>` exposes a small, typed surface any binding can read:

| Path | Meaning |
| --- | --- |
| `search.pending` | a request is in flight |
| `search.value` | the resolved value (typed as `type`) |
| `search.error` | the failure, if any |
| `search.ok` | settled with a value and no error |
| `saveDraft.dirty` | a write resource has body changes not yet acknowledged |

To refetch with unchanged inputs (a manual refresh, polling) there is no imperative call: bump a state param the source depends on, or declare a `poll` interval. For a read, a param change cancels the stale in-flight GET request. Reads are keyed by their resolved params, giving a natural cache key.

> [!ex] Locality of behaviour, end to end
> ```html
> <input bind:value="query" placeholder="Search…">
> <template $match>
>   <progress $when="search.pending"></progress>
>   <output $when="search.error"><value of="search.error.message"></value></output>
>   <ul $else>
>     <li $each="r of search.value.results" $key="r.id"><value of="r.title"></value></li>
>   </ul>
> </template>
> ```

### What goes on the wire

Typing `oat` into the control bound to `query` changes a declared value, which is the whole trigger: the `<param>` that binds it is a dependency, so the resource re-reads. Nothing calls the endpoint imperatively, and no code assembles a URL. With `debounce="200ms"` the keystrokes coalesce into one request, and each param is serialized into the query string because neither name appears in the `src` template:

```text
GET /api/search?q=oat&page=1
Accept: application/json
```

The endpoint answers with JSON. The payload becomes `search.value` as it arrived; a declared `type` constrains the *references* into it rather than gating the response as a whole:

```json
{
  "results": [
    { "id": "r-1", "title": "Rolled oats" },
    { "id": "r-2", "title": "Oat milk" }
  ]
}
```

From there the result is ordinary reactive data: `search.pending` was true while the request was in flight, `search.value.results` now feeds the `$each` above, and `search.ok` is true. The last resolved value stays bound while the next read runs, so a refetch does not blank what the page already shows. Editing `query` again cancels the in-flight read before starting the next one, so a fast typist never renders an earlier answer over a later one.

> [!norm] A reference conforms or it is inert
> A declared type is checked where a reference is read, not where its value arrived. If `results[0].title` holds a number where the declaration says `string`, that reference cannot participate in reactivity: a binding reading it does not update and keeps what it last rendered, and a `<computed>` reading it does not recompute, so nothing downstream of it moves either. The payload is left exactly as the endpoint sent it, and references into its conforming parts keep working.
>
> This is distinct from absence. A property that is not there is absence, which renders as empty text and is a normal state for data that has not arrived. A property that is present but breaks its declared type is a broken contract: rather than rendering a value the declaration forbids, or discarding a response a page may be mid-way through using, the offending reference goes quiet and the violation is reported to the author.
>
> A declaration with no type constrains nothing, and `unknown` is the type every value satisfies. A closed object shape states that an undeclared field is not there, so a reference to one is a violation; an open shape (`...`) says nothing about fields it does not name, which is what a payload that may grow should declare.

The outbound half is symmetrical. A body param of a synchronized write is serialized as request content rather than a query parameter, while a param consumed by the `src` template identifies the resource:

```text
PATCH /api/posts/42
Content-Type: application/json

{ "title": "Draft title", "tags": ["design", "docs"] }
```

`id` filled the `{id}` placeholder and therefore does not repeat in the body; `title` and `tags` are the body. The same rule decides both directions, so an author reading a declaration can tell what the request will look like without reading any JavaScript.

## Writes: reactive data effects

A synchronized write is the outbound half of the same reactive resource model. A `<data>` with a modifying `method` and `send="change"` observes its body parameters and sends their latest snapshot when they change. This mode represents state synchronization: each body is the latest state, never a request to perform a one-shot command. `debounce` controls the quiet period before the effect runs, so autosave does not mean one request per keystroke. The declaration lives in `<defs>` and exposes `.dirty`, `.pending`, `.value`, `.error`, and `.ok`.

```html
<defs>
  <!-- A modifying <data> is a reactive sink, not a hidden form. -->
  <data name="saveDraft"
        method="patch"
        src="/api/posts/{id}"
        send="change"
        debounce="500ms">
    <param name="id" :value="post.id">        <!-- resource identity -->
    <param name="title" :value="draft.title"> <!-- reactive body field -->
    <param name="tags" :value="draft.tags">
  </data>

  <!-- An explicit command stays an event for the owner to handle. -->
  <handler name="requestPublish">
    <dispatch event="publish" :value="draft">
  </handler>
</defs>

<!-- These controls may already be inside a consumer-owned native <form>. -->
<input bind:value="draft.title">
<button type="button" on:click="requestPublish">Publish</button>

<p aria-live="polite" $if="saveDraft.pending">Saving…</p>
```

Initial connection samples the current body as that resource key's baseline and does not send a write. After the first acknowledged write, the baseline is the last acknowledged body for that key. A body-param change marks the resource dirty and queues a write. Every queued or in-flight write captures an immutable resolved resource identity and body snapshot. While a write is pending, further body changes for the same key replace one trailing queued snapshot with the latest one. A sent write is never cancelled because cancellation cannot undo a request the server may already have applied.

A parameter consumed by the `src` URI template identifies the resource. Changing it activates an independent baseline for the new key; queued and in-flight work keeps its captured old key and may finish there. Completion for an old key updates only that key's stored result. It must not change the active new key's `.dirty`, `.pending`, `.value`, `.error`, or `.ok`.

Disconnecting removes observations, pauses unsent queued work, and preserves its dirty latest snapshot and captured key. A sent write may finish, but it cannot schedule DOM work for a detached instance. On reconnect, preserved queues resume under their own keys. For the current key, the runtime samples the current body: an unseen key gets an initial no-send baseline; a known key remains dirty and resumes synchronization when its body differs from its last acknowledged baseline. While no instance is connected, nothing new is observed or scheduled.

A writable data resource does not own controls or create a rendered `<form>`. The same state can feed several resources with different endpoints, methods, parameter subsets, and send options. The visible controls may be standalone, inside a native form owned by the component, or inside a form that already contains the component instance.

> [!norm] Resource and control ownership
> A `<data>` declaration lives in `<defs>` and owns request synchronization. It names parameters, selects a method, and serializes request data while producing no rendered or form-associated element. Visible controls keep their native form owner, validation, and submitter behavior. A component instance can therefore live inside an author-owned form without adding another submission scope.[^3]

> [!ex] Async validity composes with native forms
> Consider a slug field whose component declares a reactive `<data>` lookup to ask whether the current slug is reserved. The component's dependency graph keeps that lookup and its availability result current. The [validation contract](/html-next/validation) applies the result to the field's validity. If the component invocation lives inside a page author's native form, any native input produced by the component remains associated with that outer form after lowering, and the author-owned form decides whether and where the complete form is submitted. The same component may instead render a standalone control or no form control at all.

### Commands remain explicit

Publishing, charging, sending email, and deleting are commands, not synchronization. They must not run because a dependency happened to change. Their commitment point remains author-owned: native form submission, an imperative controller call, or a component event dispatched from an internal button. An internal button may itself be a native submit button associated with the surrounding form; when it is not, its handler can dispatch the command intent without owning the endpoint. HTML Next therefore adds no `<send>` handler step and does not distort reactive state into a command trigger.

> [!warn] Open for review
> Direction: reads and synchronized writes are `<data>` resources; form/control ownership and one-shot commands remain separate. The initial write policy is `send="change"` with optional `debounce`. Still open: additional send policies, retry and conflict policy, resource identity carried outside the URI template (including query-shaped identity), the declarative bridge from an async lookup into an author-owned control's validity, pagination accumulation, optimistic updates, revalidation, request headers/auth, and real-time push (SSE/WebSocket) where the server drives change without a param bump. Outside-world reactions (timers, subscriptions) are the JavaScript layer's job, see Lifecycle below.

## Lifecycle

In a reactive component most of what framework lifecycle callbacks did is absorbed by the dependency graph, so HTML Next needs far fewer hooks, and names the ones it keeps after the platform's custom-element reactions, for least surprise.

### What the graph already handles

- **Prop / attribute changes**: the bindings, `<computed>`, and `<data>` that read a prop re-run automatically. This is `attributeChangedCallback`, and you never write it.
- **Fetch on mount, refetch on change**: declare a `<data>`; it runs when its params resolve and again when they change. This is the `connectedCallback` fetch.
- **Initial and derived state**: `<state :value>` and `<computed>`; initial focus is `autofocus`.

### Declarative lifecycle events

For a reaction that is not a derivation, `on:connect` and `on:disconnect` run a [handler](/html-next/bindings) when the component is connected or disconnected, mirroring `connectedCallback`/`disconnectedCallback`[^7] and firing again on reconnect. Because handlers are declarative, they set state or `<dispatch>` an event, with no imperative code. They are **client-only**: SSR renders the static tree, and hydration is what connects, so nothing lifecycle-driven runs on the server.

```html
<defs>
  <state name="visible" :value="false">
  <handler name="show"><set name="visible" :value="true"></handler>
  <handler name="hide"><set name="visible" :value="false"></handler>
</defs>

<!-- lifecycle events run handlers; client-only (SSR never connects) -->
<section on:connect="show" on:disconnect="hide">…</section>
```

| Web Components reaction | HTML Next |
| --- | --- |
| `constructor` | none, the `<template component>` declaration *is* the definition |
| `connectedCallback` | `on:connect` (declarative) · the JS behavior's connect (imperative, below) |
| `disconnectedCallback` | `on:disconnect` · the JS behavior's teardown |
| `attributeChangedCallback` | not written, reactivity re-runs the dependents |
| `adoptedCallback` | `on:adopt` (rare, cross-document moves) |
| form-associated callbacks | the forms & validation story (see [Validation](/html-next/validation)) |

> [!note] Connection defines the lifecycle boundary
> `on:connect` fires each time an element joins a live, interactive document, including after a move and re-insertion. That boundary also fits **SSR**: the server produces static markup, then client [hydration](/html-next/components) adopts and connects the node. Framework developers can read connect/disconnect as the platform-specific counterpart to mount/unmount, with repeated connection made explicit.

> [!norm] Imperative lifecycle is the JavaScript layer
> Timers, subscriptions (SSE/WebSocket), `IntersectionObserver`, third-party libraries, imperative animation: these are genuinely imperative, with setup and teardown, and have no declarative form. They live in the reserved **JavaScript layer** (see [The JavaScript Layer](/html-next/javascript)), at a later Level, where a component may attach an ES-module *controller* whose connect hook returns a disposer run on disconnect, the shape `connectedCallback`/`disconnectedCallback` and React/Svelte effects already established.[^8] The declarative layer stays free of lifecycle ceremony; the imperative layer is the only part with a real lifecycle, and it is opt-in.

## The dependency graph

Every expression exposes the paths it reads, and every `<param :value>` names a subscription, so the graph is known statically. This buys type-checkable expressions, predictable invalidation, ahead-of-time generation for any reactive framework, and a browser runtime that needs no dynamic code.

| Target | Lowers reactivity to |
| --- | --- |
| React | `useState` / `useMemo` / a resource hook |
| Vue | `ref` / `computed` / `watch` |
| Svelte | runes (`$state` / `$derived` / `$effect`) |
| Browser runtime | signals (the TC39 Signals proposal as a candidate substrate)[^4] |

## Relationship to TC39 Signals

**Decision:** HTML Next integrates with, but does not depend on, the TC39 Signals proposal.[^4] Signals are a good optional substrate for a browser runtime and a potential implementation interoperability point. They are not the authored markup model, a required implementation strategy, or a second source of observable semantics. A runtime may use native Signals, a small userland graph, or a target framework's reactivity so long as the HTML Next result is equivalent.

The TC39 proposal is intentionally lower-level than a UI system: it standardizes writable and computed cells plus dirtiness notification, while leaving effects, scheduling, DOM ownership, and automatic disposal to frameworks. HTML Next already has the missing owner: the connected template instance.

> [!norm] Connection owns observation
> When an instance connects, the runtime wires only the bindings, computed values, data parameters, and controller effects that its currently instantiated tree can reach. When a conditional branch disappears, its observations disappear with it. When the instance disconnects, the runtime removes every live observation, cancels stale GET reads, pauses unsent write effects without losing their captured state, and runs controller-effect cleanup. Already-sent writes may finish, but cannot schedule detached DOM updates. A later reconnection wires the same declared graph again, resumes preserved writes under their captured resource keys, and evaluates it against the values then current.
>
> **Connection owns observation.** Template expressions are pure and expose their dependencies directly; their connection to the DOM supplies the lifetime. State may remain on a still-referenced detached instance, but nothing observes it and no DOM work is scheduled while that instance is disconnected. Authors therefore write no `watch`, `unwatch`, or `untrack`; the DOM integration supplies the subscription bookkeeping and teardown that a low-level Signals implementation requires.

### The minimum useful Signals subset

If an implementation chooses TC39 Signals, HTML Next needs the semantics of `State`, `Computed`, and `Watcher`: writable cells, lazy cached and glitch-free derivations, and a notification that lets the DOM layer schedule a flush. The DOM layer owns when to call `watch`/`unwatch`; authors do not.

| Signals facility | HTML Next position |
| --- | --- |
| `Signal.State` | A suitable backing cell for declared `<state>` and changing props. |
| `Signal.Computed` | A suitable backing cell for `<computed>`; HTML Next additionally knows its dependency paths statically. |
| `Signal.subtle.Watcher` | An internal invalidation hook. One instance-owned scheduler batches affected DOM work into a microtask and unwatches it on disconnect. |
| built-in effects and scheduling | Not supplied by TC39 and not requested from it. The [`host.effect` DOM API](/html-next/javascript) supplies lifecycle, scheduling, and cleanup. |
| `Signal.subtle.untrack`, graph introspection, subclassing, custom equality | Not required by HTML Next's authored model. An implementation may use them, but markup semantics never expose them. |

> [!note] Signals can advance independently
> The TC39 proposal is currently Stage&nbsp;1 and explicitly treats DOM integration as separate future work. HTML Next should provide that integration evidence without freezing itself to the proposal's present class names or `subtle` surface. If Signals advance, a native runtime can adopt them underneath this contract; if they change or do not ship, the markup and its lifecycle semantics remain intact.

## Element reference

::: {.entry name="<state> · <computed>" role="local reactive values"}
Attributes
: `<state name :value>` · `<computed name from>`

Semantics
: state is mutated only by `<set>`/`bind:`; computed is pure and recomputed from dependencies.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<data> · <param>" role="declared reactive resource"}
Attributes
: `name`, `src`, `method?`, `type?`, `send?`, `debounce?`, `poll?`, `enctype?` · `<param name :value>`

Methods
: `get`, `query`, `post`, `put`, `patch`, and `delete`; parsed ASCII-case-insensitively and mapped to uppercase HTTP methods before request construction.

Exposes
: `.dirty`, `.pending`, `.value`, `.error`, `.ok`

Reads
: GET runs on connection and when a bound param changes; stale reads are cancelled and results are keyed by resolved params.

Writes
: `send="change"` observes body params after the initial no-send baseline; `debounce` delays and coalesces the effect. Queued work captures an immutable identity and body, and sent writes are not cancelled.

Identity
: `{name}` in `src` is an RFC 6570 path param. Each key has an independent last-acknowledged baseline and result state; old-key completion cannot update the active key.

Disconnect
: Observation stops. Unsent writes pause without losing their dirty snapshot; sent writes may finish but cannot schedule detached DOM work.

Level
: [L1 (proposed)]{.pill .l1}
:::

## Sources

[^1]: [htmx](https://htmx.org/docs/) (`hx-get`/`hx-trigger`/`hx-target`) and its [Locality of Behaviour](https://htmx.org/essays/locality-of-behaviour/) essay.
[^2]: IETF, [RFC 6570: URI Template](https://www.rfc-editor.org/rfc/rfc6570) (the `{name}` placeholder syntax).
[^3]: WHATWG HTML, [form submission](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-algorithm) (the native model for constructing an entry list and selecting an endpoint, method, and encoding).
[^4]: TC39, [Signals proposal](https://github.com/tc39/proposal-signals) (Stage&nbsp;1): a candidate reactive substrate whose `State`, `Computed`, and `Watcher` primitives deliberately leave effects, scheduling, DOM ownership, automatic disposal, and future HTML/DOM integration to a higher layer.
[^5]: Signals and fine-grained reactivity as a declared, statically-analyzable dependency graph: [Solid signals](https://docs.solidjs.com/concepts/signals) and [createMemo](https://docs.solidjs.com/reference/secondary-primitives/create-memo), [Angular signals](https://angular.dev/guide/signals), with [Knockout observables](https://knockoutjs.com/documentation/observables.html) as the historical ancestor (and Vue `ref`/`computed`, [Preact signals](https://preactjs.com/guide/v10/signals/)). Contrast: [RxJS](https://rxjs.dev/) models push streams, not value cells.
[^6]: [Solid createResource](https://docs.solidjs.com/reference/basic-reactivity/create-resource): a resource whose fetch re-runs when its source changes, exposing loading and error, the exact surface `<data>` exposes as `.pending`/`.error`/`.value`/`.ok`. [TanStack Query](https://tanstack.com/query/latest) and [Vue Query](https://tanstack.com/query/latest/docs/framework/vue/overview) key a cache by request params, matching requests keyed by resolved params here.
[^7]: WHATWG HTML, [custom element reactions](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-element-reactions) (`connectedCallback`/`disconnectedCallback`, the naming precedent for `on:connect`/`on:disconnect`).
[^8]: The return-a-disposer teardown shape: Solid [onCleanup](https://docs.solidjs.com/reference/lifecycle/on-cleanup) and React [effect cleanup](https://react.dev/reference/react/useEffect#connecting-to-an-external-system).
[^9]: WHATWG Fetch, [methods](https://fetch.spec.whatwg.org/#methods): method normalization uppercases `DELETE`, `GET`, `HEAD`, `OPTIONS`, `POST`, and `PUT`; it does not include `PATCH`.
[^10]: IETF, [RFC&nbsp;10008: The HTTP QUERY Method](https://www.rfc-editor.org/rfc/rfc10008): a safe, idempotent method that carries request content.
[^11]: WHATWG HTML, [issue&nbsp;#12594](https://github.com/whatwg/html/issues/12594): the active proposal to support `method="query"` and `formmethod="query"` in HTML forms.
