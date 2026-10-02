---
title: Bindings & Events
order: 3
blurb: "from: · bind: · on: · class: · <handler>"
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reserved direction
---

# Bindings & Events

One consistent family of attribute bindings, all ordinary attribute names under the real HTML parser, so the same source is browser-parseable and framework-compilable. Behavior stays **local to the element** — you can tell what an element does by reading the element itself (locality of behaviour) — but typed and reactive, never a string reaching into a global.

## The binding family

An unprefixed attribute supplies a fixed literal. A declared component prop parses that literal according to its type; an undeclared or native attribute keeps its ordinary HTML meaning. A prefix marks a binding. The colon is verified across Chromium, Firefox, and WebKit to be an ordinary attribute-name character (not an XML namespace), so every form survives the parser and round-trips through `outerHTML`.

The shapes have direct framework precedent[^3]: `from:attr` supplies values to an element as Vue's `v-bind` does, while `bind:` (two-way) and `on:` (event) match Svelte verbatim. Angular `[(ngModel)]`, its banana-in-a-box, is the canonical one-way-in-plus-event-out two-way model that the `bind:` writability rules follow.

| Form | Meaning |
| --- | --- |
| `attr="…"` | Fixed literal. A declared component prop parses it using its type; an undeclared or native attribute follows HTML's attribute rules. |
| `from:attr="expr"` | One-way expression binding, evaluated and checked against the element contract. The target updates when a prop, state value, or other dependency changes. |
| `bind:prop="path"` | Two-way binding to a writable path. |
| `on:event="handler"` | Event binding to a declared handler. |
| `class:token="expr"` / `style:prop="expr"` | Live bindings: toggle one class or set one style property, then update it whenever the expression's dependencies change. |
| `$key="expr"` | List identity for reactive reconciliation (a `$each` modifier). |

For example, when a component declares `count` as `number` and `point` as `object`, both plain attributes produce typed values without a colon:

```html
<x-plot count="3" point="{ x: 3, y: 5 }"></x-plot>
<x-plot from:count="nextCount" from:point="{ x: currentX, y: 5 }"></x-plot>
```

The first invocation supplies fixed values. The second evaluates expressions that read `nextCount` and `currentX`. A plain structured value uses HTML Next's [object literal syntax](/html-next/types), not JSON; references such as `currentX` require `from:`. The prefix selects reactive expression evaluation, not a data type.

A live binding writes only a result that has its destination's declared type. If one evaluation has the wrong type, it leaves the destination at its last successfully written value; before the first successful write, the destination retains its default or `null`. The binding still watches its dependencies and can write again when the result becomes valid. This rule applies equally when the expression is a direct reference or a function call. A value of the right type that fails `min`, `max`, or another value constraint **does** get written and sets validity. [Reactivity](/html-next/reactivity#invalid-reactive-results) shows the full sequence.

> [!note] Prefixes name the operation
> `from:x`, `class:x`, and `style:x` all subscribe to the values their expressions read and recompute when those values change. `bind:x` also writes changes back; `on:x` invokes a handler. The suffix names the affected attribute, property, event, class, or style property.

### Constant, action-time, and computed values

These forms answer two separate questions: **is the supplied text a literal or an expression, and when is it used?** A literal is parsed through the destination's declared type; it is not necessarily a JavaScript string.

| Form | Interpretation | When it takes effect |
| --- | --- | --- |
| `value="2"` | Constant literal; a `number` destination receives JavaScript `2`, while a `string` destination receives `"2"`. | A declaration initializes, or a handler uses the constant when it runs. |
| `expr:value="count + 1"` | Expression evaluated against the component's current values. Its result must satisfy the destination's declared type. | Once each time a `<set>` or `<dispatch>` step runs. It creates no subscription. |
| `from:value="draft.title"` | Computed value with a live dependency on `draft.title`. | Recomputed when that dependency changes; the receiving element's effect then runs. |

For a `<set expr:value>` handler step, a wrong-typed result skips that state write. The handler can run again later; there is no subscription. A `from:` binding, by contrast, re-evaluates on every dependency change and leaves its previous value in place during an invalid evaluation.

```html
<state name="count" type="number" value="1"></state>
<state name="post" type="object({ id: string })" value="{ id: '42' }"></state>
<state name="draft" type="object({ title: string })" value="{ title: '' }"></state>
<state name="revision" type="integer" value="0"></state>
<handler name="increment"><set name="count" expr:value="count + 1"></set></handler>
<event name="publish" type="object({ title: string })"></event>
<handler name="publish"><dispatch event="publish" expr:value="draft"></dispatch></handler>
<data name="saveDraft" method="patch" src="/api/drafts/{id}" send="change">
  <param name="id" from:value="post.id"></param>
  <param name="title" from:value="draft.title"></param>
  <param name="clientRevision" expr:value="revision"></param>
</data>
```

The `title` parameter recomputes as the draft changes. The data resource's `send="change"` policy turns a changed `from:value` body parameter into a write; a read resource instead refetches. `clientRevision` is sampled for that write but changing `revision` alone does not schedule one. The dispatch runs only when its handler is invoked. `from:` on a dispatch would mean a live effect and would send on a dependency change, so handler steps use `expr:value` for expressions.

## One-way bindings

`from:name="expr"` binds an attribute or a contract-declared property. It normalizes before resolving: strip `from:`, ASCII-lowercase the remainder, look the key up in the generated platform manifest, and assign using the returned canonical spelling, **which may be an attribute or a DOM property**. The expression is evaluated when the element is created and again whenever its dependencies change. A dependency can be a prop or a state value. There is deliberately **no separate raw-property syntax**: the manifest is authoritative, so an author never hand-picks an exact IDL name, and no binding reaches an arbitrary DOM property outside the contract.

Replacing an element's content is not a binding but a [templating](/html-next/templating) directive: escaped text is `$value`, sanitized markup is `$html`. Raw, unsanitized HTML is available only through the dedicated trusted-HTML type (see [Types](/html-next/types)), never an ordinary string.

### Future exploration: writable computed values

A computed value could declare both its live read and the action to take when a binding writes to it:

```html
<state name="fraction" type="number" value="0.25"></state>
<computed name="percentage"
          read="fraction * 100"
          write="fraction: $value / 100"></computed>
<x-stepper bind:value="percentage"></x-stepper>
```

The read expression would recompute when `fraction` changes. When the component reports a new numeric value through `bind:value`, the write expression would set the writable `fraction` state. This keeps the inverse mapping in one declaration and reuses `bind:` at the call site, instead of pairing `from:value` and `to:value` on each invocation. The `fraction:` part is a proposed writable destination, not general expression assignment.

This syntax is exploratory. Design still needs to choose `read` versus the existing `<computed from>` spelling, define the component event that supplies `$value`, check the write result against the destination type, and prevent feedback loops. A read expression need not have an inverse: for `hasQuery = query != ''`, writing `false` can clear the query, but writing `true` cannot reconstruct text that was never supplied. Level&nbsp;1 computeds remain read-only and cannot be `bind:` destinations.

## How a bound value serializes

A binding evaluates to a typed value, and how that value lands depends on the value and the attribute's kind (the generated manifest carries each attribute's kind). One default rule covers almost everything:

| Value | Result on the attribute |
| --- | --- |
| `false` · `null` · `undefined` | **removed** (the "no value" signal) |
| `true` | **present**, with an empty value |
| a string | set verbatim, an empty string is present-but-empty, distinct from removed |
| a number | stringified |
| a list | space-joined, for token-list attributes |

The `false`/`null` → removed rule is what makes boolean attributes work with no special case: `from:disabled="isDisabled"` adds `disabled` when true and removes it when false, never the `disabled="false"` trap (which is actually disabled). When you want the *characters* "false", bind a string, `from:data-state="'false'"`, or an identifier that resolves to one.

> [!note] Two kinds get specific wiring
> **URL attributes** (`href`, `src`, `action`, …) are stringified and then have dangerous schemes stripped, the same posture the sanitizer applies to `$html`, so a bound `javascript:` URL is dropped. **Enumerated true/false attributes** (the `aria-*` family, `contenteditable`) take the literal strings `"true"`/`"false"` rather than presence, so a bound boolean coerces to that string: `from:aria-expanded="isOpen"` yields `aria-expanded="false"` when closed rather than removing it. Both are the manifest doing the work; the author writes the same `from:attr` either way.

Because the mapping is fixed and manifest-driven, every target serializes identically, the equivalence contract applied to attribute writes: the polyfill and the React/Vue/Svelte outputs each compile to their own idiom while producing the same observable attribute.

## Two-way binding: bind:

`bind:prop="path"` reflects the value and writes user input back to `path`. It is the forms workhorse, and it requires a **writable path** plus an element contract that supports updates.

```html
<input bind:value="search.query">
<input type="checkbox" bind:checked="filters.inStock">
```

### What counts as writable

A writable path is a member or index access chain rooted at a **`<state>`** cell, the only mutable source. Everything else is read-only, and `bind:` to it is a conformance error, caught statically because the root's declaration is known:

| Path | `bind:` | Why |
| --- | --- | --- |
| `draft.title`, `rows[i].done` | writable | rooted at `<state>`; a plain access chain |
| a `<computed>` | error | derived; write its inputs instead |
| a `<data>` `.value` | error | a fetched resource is read-only |
| a prop | error (inside the component) | props are one-way in; a component surfaces two-way by exposing a bindable prop and `<dispatch>`ing changes, which the consumer binds with `bind:` on the invocation |
| `a + b`, `x \| filter` | error | an expression is not an assignable location |

Writability flows from the root: a `$each` local or `$with` alias is writable exactly when it aliases a writable path, an item of a `<state>` collection is, an item of a `<data>` collection is not. Writing a sub-path updates that path in the state cell and re-runs its dependents; the implementation may model state as mutable-with-tracking or as a structural update, the observable result is the same.

> [!note] Editing fetched data
> A GET `<data>` result is read-only, so you do not `bind:` to it. Copy the fetched value into a `<state>` draft and bind controls to the draft. If that draft should autosave, a writable [`<data method="patch" send="change">`](/html-next/reactivity) observes the fields it sends. The fetched value, in-progress edit, and write effect remain distinct.

> [!note] Attribute vs. property
> Binding distinguishes an input's initial `value` attribute (serialized/default state) from its live `value` property (current control state). `from:value` updates the attribute from an expression; `bind:value` tracks the live property.

## Class & style bindings

Conditional presentation uses **keyed live bindings**, one class token or style property at a time. Like `from:`, each binding runs when the element is created and again when a prop, state value, or other dependency read by its expression changes. `class:btn--busy="$saving"` adds or removes the class as `saving` changes; `style:--progress="format('%s%', $pct)"` updates that property as `pct` changes. The [expression language](/html-next/expressions) defines `+` for numbers only; `format` produces a string. The **key is the attribute name** (a literal class token or CSS property) and the **value is a single pure expression**, so nothing packs a key/value list into one attribute value.[^4] Both compose with any literal `class` or `style`. Purely visual transforms remain CSS's job (see [Styling](/html-next/styling)); these bindings update presentation keys.

```html
<!-- one class or style property per keyed binding; the value is a single pure expression -->
<button class="btn" class:btn--busy="$saving" class:btn--danger="$variant = 'destructive'">
<div style:--progress="format('%s%', $upload.percent)"></div>
```

## Events & handlers

`on:event="handler"` wires a DOM event to a declared **handler**. The form echoes native `onclick` and joins the binding family, but the browser does *not* execute `on:click` as script: the value names a `<handler>`, it is not an expression. Behavior and visible markup stay cleanly separated, the handler lives in the definition's `<defs>` region (see [Components](/html-next/components)), the content just points at it by name.

```html
<!-- content references behavior by name; no steps inline -->
<button type="button" on:click="startEdit">Edit</button>

<!-- An internal button can ask the component's owner to run a command. -->
<button type="button" on:click="requestPublish">Publish</button>

<!-- behavior lives in the definition's <defs> region -->
<defs>
  <handler name="startEdit">
    <set name="editing" value="true">
  </handler>

  <handler name="requestPublish">
    <dispatch event="publish" expr:value="draft">
  </handler>
</defs>
```

### Handler steps

A handler is an ordered, enumerable list of declarative steps. The vocabulary is deliberately tiny, and none of it reaches into userland code.

| Step | Effect |
| --- | --- |
| `<set name value>` or `<set name expr:value>` | Write a local state cell. `value` is a typed constant; `expr:value` is evaluated when the handler runs. |
| `<dispatch event value?>` or `<dispatch event expr:value?>` | Dispatch a component event with an optional typed constant or action-time expression as its payload. |
| `$if` (on a step) | Guard a step; it runs only when the expression is truthy, the same `$if` directive used in templating. |

> [!norm] Handlers-only, by design
> State changes live in `<handler>` steps or `bind:`, never inline in the template. Assignment is absent from the expression language, so expressions stay pure. Reactive network synchronization belongs to a declared [`<data>` effect](/html-next/reactivity); a component that requests a one-shot command *dispatches an event*[^2] and lets its owner decide whether to submit a form or call imperative code. The payoff is that a component's entire declarative behavior is enumerable from its markup.

### Platform verbs: native invoker commands

Opening a dialog or toggling a popover is not component logic, it is a platform verb on a specific element. The platform already ships the declarative answer: **invoker commands** (`command` / `commandfor`), shipped in Chromium, WebKit, and Firefox.[^1] Use them directly, HTML Next adds nothing here.

```html
<!-- platform verbs: native invoker commands, no <handler> block needed -->
<button command="show-modal" commandfor="editor">Edit</button>
<dialog id="editor">…</dialog>

<button command="toggle-popover" commandfor="menu">Menu</button>
<div id="menu" popover>…</div>
```

> [!note] Invoker commands vs. handlers
> These are different jobs: the native `command`/`commandfor` attributes invoke a built-in *platform verb* on a target element by id (`show-modal`, `toggle-popover`), while a `<handler>` runs your own *state logic* from `on:event`. Reach for the invoker attributes for element verbs; reach for a handler for state.

### Modifiers & component events

A handler runs as declarative steps, so the operations you would otherwise call on the event object, `preventDefault`, `stopPropagation`, and the `addEventListener` options, have no imperative place to live. They ride the event name as **dotted modifiers**, each naming a real DOM operation: `on:submit.prevent`, `on:click.stop`, `on:click.once`, `on:scroll.passive`, `on:click.capture`. The dotted syntax itself is Vue's prior art, not an HTML native; key filters such as `on:keydown.enter` are convenience layered on top. A component declares emitted events in its contract; a consumer listens with the same form: `<x-dialog on:saved="refresh">`, where `refresh` is one of its own handlers. The same `on:` family carries the **lifecycle events** `on:connect`/`on:disconnect` (see [Lifecycle](/html-next/reactivity)).

## Keys

`$key="expr"`, a modifier on `$each` (see [Templating](/html-next/templating)), gives each iterated item a stable identity, so reactive updates and reordering are correct rather than index-positional. Keyed reconciliation is well-trodden prior art[^5]: React introduced `key`, and Vue, Svelte, Angular, and Lit each carry their own form.

### Replacing ref

Frameworks expose a `ref` handle so imperative code can reach a node. HTML Next has no imperative handler, so there is nothing to dereference, and each concrete use of a ref maps to a declarative form:

| What a `ref` was for | HTML Next |
| --- | --- |
| `inputRef.current.value` (read a control) | it is already state: `bind:value="draft.title"` |
| `ref.current.focus()` on mount | `autofocus` |
| `dialogRef.current.showModal()` | `<button command="show-modal" commandfor="dlg">` |
| toggle a popover | `<button command="toggle-popover" commandfor="menu">` |
| play / pause media | invoker commands for media (emerging) |
| scroll into view, measure, other imperative calls | [open]{.kw}: no declarative form yet, a genuine platform gap |

The pattern: reading is `bind:`; platform verbs are invoker commands addressed by `id` (the way `label[for]` and `[aria-controls]` already cross-reference); and the residual imperative cases are an acknowledged open area, not a hidden `ref`.

## Non-conforming

> [!warn] Rejected
> Inline `on*` handlers (the browser *executes* them) and other frameworks' directive prefixes (`@`, `v-`, `#`, `.`, `use:`, `transition:`, `animate:`) are non-conforming as literal attributes. Because there is no raw property binding, the dangerous sinks (`innerHTML`, `outerHTML`, `srcdoc`, `on*`) are simply unreachable by a binding: markup is set with `$html` (sanitized) or the trusted-HTML type, never a string assigned to a property.

## Element reference

::: {.entry name="on:event" role="event binding attribute"}
Value
: Name of a declared `<handler>` (not an expression).

Modifiers
: `.prevent` `.stop` `.once` `.enter` (and other key names)

Semantics
: Adds a listener; the browser never executes the attribute as script.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<handler>" role="named event handler"}
Attributes
: `name`

Placement
: In the definition's `<defs>` region, alongside `<state>` and `<data>`.

Children
: `<set>` and `<dispatch>`, each optionally guarded with `$if`. Ordered; no route to arbitrary code.

Level
: [L1]{.pill .l1}
:::

## References

[^1]: WHATWG HTML, [invoker commands](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-commandfor-attribute) (`command`/`commandfor`); see also [MDN: Invoker Commands API](https://developer.mozilla.org/en-US/docs/Web/API/Invoker_Commands_API).
[^2]: WHATWG DOM, [dispatching events](https://dom.spec.whatwg.org/#dispatching-events) (the `dispatch` verb behind `<dispatch>`).
[^3]: Binding-family prior art: Vue [v-bind](https://vuejs.org/api/built-in-directives.html#v-bind) (one-way values, expressed here with `from:attr`); Svelte [bind:](https://svelte.dev/docs/svelte/bind) and [on:](https://svelte.dev/docs/svelte/on) element directives (two-way and event, matched here verbatim); Angular [two-way binding](https://angular.dev/guide/templates/two-way-binding) (the `[(ngModel)]` banana-in-a-box: one-way-in plus event-out, the model behind the `bind:` writability rules).
[^4]: Keyed presentation prior art: Svelte [class:](https://svelte.dev/docs/svelte/class) and [style:](https://svelte.dev/docs/svelte/style) directives (the exact keyed syntax adopted here). Contrast: Vue [object `:class="{ open: x }"`](https://vuejs.org/guide/essentials/class-and-style.html) and Lit [`classMap`](https://lit.dev/docs/templates/directives/#classmap)/`styleMap` pack a key/value map into one attribute value; Angular `[class.x]`/`[style.x]`/`ngClass` and Solid [`classList`](https://docs.solidjs.com/reference/jsx-attributes/classlist) are the same keyed idea.
[^5]: Keyed iteration prior art: React [key](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key) (the origin of list identity), Vue [:key](https://vuejs.org/api/built-in-special-attributes.html#key), Svelte [keyed each](https://svelte.dev/docs/svelte/each), Angular [@for with track](https://angular.dev/guide/templates/control-flow) (and the older `trackBy`), and Lit [repeat with a key function](https://lit.dev/docs/templates/lists/#the-repeat-directive).
