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

A component is defined by a native `<template component="tag">`. There is no custom-element-shaped wrapper. The `<template>` is **inert** (browsers parse its contents into a `DocumentFragment` and render nothing), so a definition degrades to inert markup with no runtime today, and could be consumed natively if the shape were adopted, the way `<template shadowrootmode>` went from inert to browser-native for Declarative Shadow DOM.[^4] Inertness is the transition guarantee, not the end state. `template[component]` is also a cheap selector for the polyfill. Its direct children are an optional `<defs>` region (the interface, behavior, and [head declarations](#head-declarations)), one markup root, and an optional `<style>`.

```html title="button.html"
<template component="x-button" status="early"
          summary="A native button with custom presentation.">
  <!-- <defs>: renders nothing. interface + behavior + data live here -->
  <defs>
    <prop name="variant" type="keyword" values="outline, solid, destructive, ghost"
          default="outline">Visual treatment.</prop>

    <event name="press"></event>
    <handler name="press"><dispatch event="press"></dispatch></handler>
  </defs>

  <!-- the visible markup: one native root, referencing the defs by name -->
  <button on:click="press"><slot></slot></button>
  <!-- styles are automatically scoped to this component (see Style scoping) -->
  <style>:host { box-sizing: border-box; }</style>
</template>
```

The interface is **declarative HTML**, not a data island. A `<prop>` states only what markup cannot already say: type, default, requiredness, description; its *target* is read from the `from:attribute`/`.property` binding and the native element from the markup root, so neither is restated. The invocation tag comes from the `component` attribute; a single hyphen keeps it collision-safe against native elements without registering a custom element. A compiler lowers all of this to a normalized JSON contract as build output (CSP-safe, no `eval()`, inspectable by docs and tooling), but JSON is the compiled artifact, never the authoring form.

> [!note] Prop declarations follow platform precedents
> `values` follows JSON Schema's finite-value constraint[^1]; `default` follows XML Schema's `default` attribute[^2]; `required` is the HTML boolean attribute of the same name[^3]; and a prop's description is its element text, as with `<option>`.

## Two regions: <defs> and the markup

A definition has two visibly separate parts, so a reader can tell at a glance what renders and what only describes behavior. The `<prop>`, `<event>`, `<request>`, and `<slot>` interface declarations, reactive `<state>` and `<computed>`, read and write `<data>` resources, and `<handler>` blocks live inside a single `<defs>` region as flat siblings, together with the [head declarations](#head-declarations): the title, metadata, links, and scripts the component adds to the document head while an instance is connected. A `<slot>` in `<defs>` is a declaration of that slot's props, and renders nothing; a `<slot>` in the markup is an outlet, where projected content renders. The visible markup is the one native root and its `<slot>` outlets. The content stays pure markup that points at behavior by name; the behavior stays a small labeled list above it.

This mirrors the document's own `<head>`/`<body>` split, declarations and resources versus rendered content, applied fractally to a component. The name is borrowed from SVG, where `<defs>` already means exactly this: definitions that render nothing and are referenced by name from elsewhere.[^5]

> [!note] <defs> survives fragment parsing
> `<defs>` is an ordinary element in HTML content, so it round-trips intact through `outerHTML` and carries the intended definition-only meaning. The HTML fragment parser instead discards `<head>` and `<body>` wrappers inside a `<template>` and hoists their children out (verified against the reference implementation's parse5-based build). Head elements need no wrapper: parse5, and Chromium's `DOMParser` and `innerHTML`, keep `<title>`, `<meta>`, `<link>`, and both `<script>` forms inside `<defs>`, where they are neither hoisted out nor executed.

## Requests: what a component asks its consumer {#requests}

Some components need behavior from whoever uses them: a rich-text editor asks for mention suggestions, an image field asks where to store a file. A prop cannot carry that behavior, because every prop has an HTML attribute form and a function has none. So the definition declares a **request** in `<defs>`, a named question with a typed detail and a typed answer. Its [controller](/declarative-components/javascript#requests) asks it with `host.request`, and the consumer answers in its own JavaScript.

```html title="ui-editor.html"
<defs>
  <request name="mention-query" type="object({ query: string })"
    returns="list(object({ id: string, label: string }))">People matching the text after @.</request>

  <request name="image-upload" type="object">
    <prop name="file" type="unknown" required>The File the author dropped or pasted.</prop>
    <returns type="object">
      <prop name="src" type="string" required></prop>
      <prop name="width" type="integer"></prop>
      <prop name="height" type="integer"></prop>
    </returns>
  </request>
</defs>
```

| Attribute or child | Meaning |
| --- | --- |
| `name` | The request's event type: lowercase kebab case, like an `<event>` name. A definition [must not]{.kw} declare an `<event>` and a `<request>` with the same name, or either one named `responder`, the host event for [late responders](/declarative-components/javascript#late-responders). A build tool reports either as an error. The live parser warns and ignores the declaration: for a shared name it keeps the `<event>` and ignores the `<request>`. |
| `type` | The type of the request's detail, written as for an `<event>`. Omitted, the detail is `null`. |
| `returns` | The type of the answer. Omitted, the answer is `unknown`. |
| `<prop>` children | The detail's fields, when `type="object"`, as for an [expanded event declaration](/declarative-components/types#structured-values). |
| one `<returns type>` child | The answer's type in expanded form, holding its own `<prop>` children. It replaces the `returns` attribute. |
| text content | The request's description, as for a `<prop>`. |

A request is not a prop: it is never reflected, never written into the [rendered form](/declarative-components/rendered-form), and never part of hydration data. Its detail and answer are JavaScript values, so they use the [request value types](/declarative-components/types#request-values). A generated framework component exposes each request as a [function prop](/declarative-components/javascript#framework-requests).

### Requests and events

A request and an event travel as the same native event, but a component declares them apart, because they tell the consumer different things:

- **The contract lists what a component asks for apart from what it announces.** An unanswered request degrades the component quietly, so a consumer must be able to see it in generated documentation, types, and editor completions.
- **Framework output maps mechanically.** An `<event>` becomes an `onX` handler, and a `<request>` becomes a function prop that returns the answer.
- **Each method has one return type.** `host.dispatch` always returns a boolean, and `host.request` always returns a promise.
- **Events keep their behavior.** Every listener receives an event, while the first responder stops a request. `<dispatch>` stays fire-and-forget.

The second declaration costs little, since both run on the same `RequestEvent` machinery.

## Head declarations: what a component adds to the document {#head-declarations}

Many components need something in the document head while they are on the page. A checkout form needs its payment provider's script. A product card describes itself to search engines with JSON-LD. A video embed opens a connection to its host early. A page sets its title and description. A component declares these in `<defs>`, beside its props and state, and the runtime adds them to `document.head` while an instance is connected.

```html title="checkout-form.html"
<template component="checkout-form" controller="./checkout-form.js">
  <defs>
    <prop name="pk" type="string" required>The Stripe publishable key.</prop>
    <event name="paymentready"></event>
    <event name="paymentunavailable"></event>
    <handler name="announceReady"><dispatch event="paymentready"></dispatch></handler>
    <handler name="announceUnavailable"><dispatch event="paymentunavailable"></dispatch></handler>

    <!-- Head declarations: in document.head while a checkout form is connected. -->
    <link rel="preconnect" href="https://js.stripe.com">
    <script name="stripe" src="https://js.stripe.com/v3/" loading="lazy"
            on:load="announceReady" on:error="announceUnavailable"></script>
  </defs>

  <form>
    <div $ref="card"></div>
    <template $match>
      <p $when="$stripe.error" role="alert">Payments are unavailable right now.</p>
      <p $when="$stripe.pending">Loading the secure payment form…</p>
    </template>
    <button>Pay</button>
  </form>
</template>
```

```js title="checkout-form.js"
export default function controller(host) {
  let card;
  host.on("connect", () => {
    // Settles on the inserted <script> element's own load or error event.
    host.scripts.stripe.ready.then(() => {
      if (!host.root.isConnected) return;
      card = Stripe(host.props.pk.value).elements().create("card");   // Stripe.js's global
      card.mount(host.refs.card);
    }, () => {});                                    // the form already shows $stripe.error
  });
  host.on("disconnect", () => { card?.destroy(); card = undefined; });
}
```

The site adds Stripe's origins to its Content Security Policy (CSP), as Stripe's own instructions say. No other setup is needed:

```text title="HTTP response header"
Content-Security-Policy:
  script-src 'self' https://js.stripe.com;
  frame-src https://js.stripe.com https://hooks.stripe.com;
  connect-src 'self' https://api.stripe.com
```

When a checkout form connects, the runtime adds the preconnect link to the head. When the form comes near the viewport, the runtime inserts an ordinary `<script src="https://js.stripe.com/v3/">` into `document.head`, and the browser fetches and runs it under the page's CSP, as it would a hand-written tag. `$stripe.pending` is true until that element fires `load` or `error`. The same event runs the form's `on:load` or `on:error` handler, which tells the page whether it can take a card, and settles `host.scripts.stripe.ready`, which the controller waits on to mount Stripe's card field. When the last checkout form disconnects, the runtime removes the preconnect link. The script stays loaded, because a browser cannot unload a script that has run.

Stripe recommends loading Stripe.js on every page so it can collect fraud signals. To do that, the application's layout declares the same script with the default `loading="eager"`. Both declarations name one URL, so the browser loads it once, as soon as the layout connects, and the checkout form's `ready` settles from that one load.

The design keeps three rules from the rest of this chapter, explained in [Security](/declarative-components/security#head-declarations): a definition never contains executable code, only visible references to it; importing a definition runs nothing; and importing a component does not give it control of the application's document.

### What a component can declare {#head-elements}

| Declaration in `<defs>` | Adds to `document.head` | Bindings |
| --- | --- | --- |
| `<title>` | The document title. | [Inline text expressions](/declarative-components/templating#inline-text-expressions) in its text. |
| `<meta name content>` or `<meta property content>` | A named metadata entry, such as `description` or Open Graph's `og:title`. | `from:content` |
| `<link rel href>` with a keyword listed below | A resource hint or a link to related metadata. | `from:href`, under the URL attribute policy. |
| `<script type="application/ld+json">` | A JSON data block, such as schema.org structured data. | `from:value` for the whole value. See [Data blocks and bound metadata](#head-data). |
| `<script src>` | An external script. See [Declared scripts](#declared-scripts). | `on:load` and `on:error` only. Its other attributes are literal, so a build can list them. |

A `<link>` head declaration uses one of these `rel` keywords: the resource hints `preconnect`, `dns-prefetch`, `preload`, `modulepreload`, and `prefetch`; the metadata links `canonical`, `alternate`, `icon`, and `manifest`; or the annotations `author`, `license`, `help`, `privacy-policy`, and `terms-of-service`. A head element may carry the attributes HTML defines for it, such as `hreflang`, `sizes`, `media`, `as`, and `crossorigin` on a link, and no others.

`<link rel="stylesheet">` is not a head declaration. A component's CSS is its [scoped `<style>`](/declarative-components/styling), including shared CSS through `@import`. An unscoped stylesheet link would style the whole document, so it would bypass scoping and give a component a second CSS path.

These are invalid anywhere in a definition: an inline executable `<script>` (one with no `src` that is not a JSON-LD data block), any other script `type` (including `importmap` and `speculationrules`), `<meta http-equiv>`, `<meta charset>`, `<base>`, `<link rel="stylesheet">`, `<link rel="import">`, the `blocking` and `nonce` attributes, and event-handler attributes. A build reports each one as an error, and the live loader rejects the definition with a diagnostic.

### When a declaration takes effect {#head-lifecycle}

Head declarations follow the instance's connection, the same lifetime that runs [controllers](/declarative-components/javascript):

- **Import.** Fetching, parsing, and registering a definition changes nothing in the document.
- **Connect.** The instance's declarations become contributions to the document head. The runtime inserts an element for each one, or shares an element that is already there.
- **Update.** While the instance is connected, a bound title, `content`, `href`, or data block updates in place, like any other binding. A JSON-LD block is its own instance's: a value change updates its text as the same node in the same position, a `null` value removes it, and a later value inserts it again.
- **Disconnect.** The instance's contributions leave. An element stays while another connected instance still contributes it; a title or description falls back to the next contributor, and then to the application's own element, restored as it was.
- **Scripts.** A declared script is inserted at most once per document and is never removed. Removing a `<script>` element does not undo code that has run, and inserting a second one would run that code again.
- **One change per update.** The runtime applies head changes once per update, after that update's connections and disconnections, so a page change is a single head change.

Every change is an ordinary DOM insertion, removal, or attribute or text change in `document.head`, made to elements that carry the `data-component-head` marker. The application's own head elements are never changed: while a contribution overrides one, it is set aside and restored. [Head management](#head-management) gives the exact steps.

### Declared scripts {#declared-scripts}

A declared script is an ordinary `<script>` element. The declaration gives it a name and says when to insert it. After the runtime inserts it, it is a script inserted through the DOM, and everything that follows is HTML's existing script behavior: classic or module evaluation, fetching, `integrity`, CORS, CSP, and the `load` and `error` events.

```html
<script name="maps" src="https://maps.example/sdk/v2.js"
        integrity="sha384-…" crossorigin="anonymous" loading="manual"></script>
```

The declaration's attributes fall into two groups. The runtime reads the declaration attributes and does not copy them. It copies the standard attributes onto the element it inserts, where they mean exactly what they mean on any `<script>`.

| Attribute | Group | Meaning |
| --- | --- | --- |
| `name` | declaration | Names the script's status: `$stripe` in expressions and `host.scripts.stripe` in a controller. It shares the component's [flat declaration namespace](/declarative-components/expressions). Optional, except that `loading="manual"` requires it. |
| `loading` | declaration | When the runtime inserts the element: `eager` (the default), `lazy`, or `manual`. |
| `on:load`, `on:error` | declaration | [Event bindings](/declarative-components/bindings) that run a `<handler>` when the script becomes available to this instance, or fails. See below. |
| `src` | standard | Required. The script's URL or a bare name, resolved as below. |
| `type` | standard | Omitted for a classic script, or `module` for a module script. |
| `integrity`, `crossorigin`, `referrerpolicy`, `fetchpriority` | standard | Copied unchanged. |

No other attribute is accepted. `async` and `defer` add nothing, because a script inserted through the DOM already runs as soon as it arrives. The `nonce` comes from the application, never from a definition (see [CSP](#declared-scripts-csp)).

`type="module"` is accepted because it is an ordinary script type with no extra rules: the browser's module map already evaluates each module URL once. A controller is still the way to give a component its own imperative behavior. A module script suits an SDK that is published as a module.

**When it loads.** The `loading` keyword comes from `<img>` and `<iframe>`, which use it for the same choice. On a declared script it means only when the runtime inserts the element:

- `eager`: when an instance connects.
- `lazy`: when a connected instance's root first comes near the viewport, by the rule the browser applies to `<img loading="lazy">`.
- `manual`: when the controller calls `host.scripts.name.load()`.

**Shared by every declaration.** The head holds one element per script URL and type. Every instance that declares that script reads the same status and `ready` from that one element, and runs its own `on:load` or `on:error` each time it connects. The element is never removed, so a script never runs twice, however many components declare it and however often they connect. Declarations of one script agree on `integrity`, `crossorigin`, and `referrerpolicy`, because those change the fetch; a disagreement is an error. `fetchpriority` comes from the declaration that inserts the element. A `<script>` the application authored with the same URL is shared the same way: the runtime uses it instead of inserting another. [Head management](#head-management) gives the exact rules, including how the runtime reads the status of a script that may have loaded before the runtime looked.

**Status.** Expressions read a script's status like a [`<data>`](/declarative-components/reactivity) resource:

| Path | Meaning |
| --- | --- |
| `stripe.pending` | The script element is inserted and has fired neither `load` nor `error`. |
| `stripe.ok` | The script fired `load`. |
| `stripe.error` | The `error` event the script fired, or `null`. |

Before insertion, `pending` and `ok` are false and `error` is `null`. A controller reads the same status through [`host.scripts`](/declarative-components/javascript#host-scripts), together with `ready`, a promise about the script that settles once: it resolves on `load` and rejects with the `error` event, and `load()`, which inserts the element if it is not inserted yet and returns `ready`.

**`on:load` and `on:error`.** These bindings mean "this script is available to this connection of the instance" and "this script failed". They call a `<handler>` like any element's `on:` binding, with the element's `load` or `error` event as `$$event`.

- Each time an instance connects, exactly one of the two runs, as soon as the script settles: when its `load` or `error` event fires, or straight away if it has already settled, through another component's declaration or an authored script.
- Nothing runs while the instance is disconnected. A connection that ends before the script settles gets neither handler, and a later connection gets its own. Each connection is a fresh setup, so work done in `on:load`, such as mounting a card field, runs again after a reconnect.
- Neither runs before the script is inserted, for example before a `lazy` script's instance comes near the viewport, or until a `manual` script's `load()` is called, unless another declaration has already inserted it.

Here two components on one page both need Stripe.js:

```html
<!-- saved-cards.html: needs Stripe as soon as it shows. -->
<template component="saved-cards">
  <defs>
    <state name="ready" type="boolean" value="false">
    <handler name="enable"><set name="ready" value="true"></set></handler>
    <script name="stripe" src="https://js.stripe.com/v3/" on:load="enable"></script>
  </defs>
  <ul from:aria-busy="not $ready">…</ul>
</template>

<!-- On the page: both declare https://js.stripe.com/v3/. -->
<saved-cards></saved-cards>
<checkout-form pk="pk_live_…"></checkout-form>
```

```html title="document.head, once both have connected"
<link rel="preconnect" href="https://js.stripe.com" data-component-head>
<script src="https://js.stripe.com/v3/" data-component-head></script>
```

The saved-cards list is `eager`, so it inserts the script when it connects. The checkout form is `lazy`, but the script it would have waited for is already loading, so it shares that element. When the element fires `load`, the browser has run Stripe.js once, and each instance's `on:load` handler runs: `enable` for the list and `announceReady` for the form. If the form is removed and added again, its `announceReady` runs again on that connection, straight away, because the script has already loaded.

**Resolution.** A script's `src` resolves by the [controller's rules](/declarative-components/javascript#loading-a-controller):

- A URL-like value (relative, root-relative, or absolute) resolves against the definition's final response URL. `https://js.stripe.com/v3/` is absolute, so it stays as written.
- A bare value, such as `src="@acme/maps-sdk"`, resolves through the application's import map with the module-specifier resolution algorithm, as a bare component reference does. The application then chooses the URL, and the definition stays the same in every deployment.
- Any component, whether from the application, an installed package, or a live import, may name any URL, including an unpinned third-party one like Stripe's. Only the document's CSP decides whether it loads, and builds and developer tools list it for review.
- A controller keeps its [live-scope rule](/declarative-components/security#live-components-use-an-application-owned-trust-root), because a controller is the component's own code from its publisher, while a declared script is typically a third-party SDK from another origin.

### Declared scripts under CSP {#declared-scripts-csp}

The inserted element is checked like any script:

- Under an origin allowlist, such as `script-src 'self' https://js.stripe.com`, the browser checks the script's URL against the list.
- Under `'strict-dynamic'`, a script that a trusted script inserts is trusted. The polyfill runtime is a script the page trusts, so the scripts it inserts load. This is the pattern `'strict-dynamic'` exists for.
- Under a nonce, a native implementation [must]{.kw} copy the `nonce` of the application element that imported the definition, the `<link rel="component">` or the inline `<template component>`, onto each script that definition's graph inserts, including definitions reached from it. The application grants trust by putting its nonce on the import, the same act as putting it on a `<script>`. The polyfill does the same under a nonce-only policy. Without a nonce on the import, a nonce policy blocks the script, and `error` reports it.

`integrity` and `crossorigin` are supported and recommended for any versioned URL. A build lists every declared script URL beside the controllers, with the component that declares it, so the application can review its scripts and generate its `script-src`. A definition that declares a script is trusted application code, exactly like one with a controller.

### Data blocks and bound metadata {#head-data}

Head declarations use the bindings a component already has. Here an article page builds its title, description, and structured data from a `<data>` resource:

```html title="pages/article.html"
<template component="page-article">
  <defs>
    <prop name="slug" type="string" required>The article's URL slug.</prop>
    <data name="article" src="/api/articles/{slug}"
          type="object({ title: string, summary: string, schema: object })">
      <param name="slug" from:value="$slug">
    </data>

    <title>{$article.value.title} · Field Notes</title>
    <meta name="description" from:content="$article.value.summary">
    <script type="application/ld+json" from:value="$article.value.schema"></script>
  </defs>

  <article><h1>{$article.value.title}</h1>…</article>
</template>
```

- `<title>` text uses inline text expressions, and `<meta>` binds `from:content`. A `<link>` may bind `from:href`, which applies the URL attribute policy.
- A JSON-LD block with literal content is inert text: the runtime copies it unchanged, and braces in it are literal, because inline text expressions apply to template text, not script content.
- `from:value` on a JSON-LD block binds the whole value. The value is an object or a list. The runtime serializes it as JSON and writes every `<` as `\u003c`, so the text can never close the element or open a comment when the page is serialized as HTML. A `null` result omits the element, as it does here while the article loads. Any other result is an [invalid reactive result](/declarative-components/reactivity#invalid-reactive-results) and keeps the last value written.
- A JSON-LD block has literal content or `from:value`, not both.

### When two components declare the same thing {#head-precedence}

A page and the layout around it may both set a title. Two cards on one page may both preconnect to the same image host. Each head declaration has a **key**, and its key's **kind** decides what happens when several connected instances contribute it:

| Kind | Declarations | What the head holds |
| --- | --- | --- |
| Competing | `<title>`, `<link rel="canonical">`, and each `<meta>` by its `name` or `property` | The entries of one component: the one with the highest precedence. When it disconnects, the next contributor's entries apply, and with none left, the application's own element returns. |
| Shared | Every other `<link>`, keyed by `rel` and `href` | One element per key, kept while any connected instance contributes it. The element is reference-counted: it is removed when the count reaches zero. |
| Owned | Each JSON-LD block | One element for each declaration of each connected instance, never shared: two products on a page are two blocks, even with identical text. |
| Script | `<script src>`, keyed by its resolved URL and type | One element per key, for the document's lifetime. See [Declared scripts](#declared-scripts). |

**Precedence: the deepest component wins.** Among the contributors to a competing key, the instance deepest in the [logical component tree](#component-ancestry-for-shared-state) has the highest precedence. A page renders inside its layout, so it is deeper, and its title replaces the layout's. Between instances at the same depth, the one that connected later wins.

**A key's value can be a list.** A `<meta>` key competes by its name or property, because two values for one name conflict: a document has one description. A component may still repeat an entry, such as two `<meta property="og:image">` elements; its entries for a key, in declared order, are that key's value. Lists from different components never mix: the winner's list replaces the previous one whole. A definition [must not]{.kw} declare two `<title>` elements, two canonical links, or two links with the same `rel` and `href`.

**Sub-properties follow their parent.** A `<meta>` name or property with three or more colon-separated parts, such as `og:image:width`, is a sub-property of the key without its last part, `og:image`. It does not compete on its own. It applies only while the same component wins its parent key, and it stays beside the parent entries it was declared with. So a page's `og:image:width` can never describe a layout's `og:image`. The rule is about the shape of the name, so it covers `og:image:*`, `og:video:*`, and conventions not yet written.

**The application's own head is set aside, never changed.** An element the application authored in its document head carries no marker. While a contribution wins a key the authored head also has, the runtime sets the authored element aside, detached but unmodified, and puts the managed element in its place. When no contributor remains, the runtime removes the managed element and puts the same authored node back where it was. The restore is exact because it is the same node. An authored shared element, such as a preconnect the application already has, satisfies a contribution with the same key, and the runtime inserts nothing; the authored element is never removed.

> [!note] Joining a list across components
> A component may one day need to add to a list another component owns, for example a second `og:image` from an embedded card. An opt-in `additive` attribute on a head declaration, which joins the key's list instead of competing for it, is a possible future addition if a real case appears. It is not part of this proposal.

### Head management {#head-management}

This section is normative. Polyfills, converters, server renderers, and native implementations [must]{.kw} produce the head these steps produce, so that output from one implementation hydrates under another.

**The marker attribute.** Every element in `document.head` that the component runtime manages [must]{.kw} carry the attribute `data-component-head`, spelled exactly so in ASCII lowercase. On a contribution's element its value is the empty string. On a `<template>` that server output uses to hold [set-aside elements](#head-ssr), its value is `set-aside`. Its presence means "the component runtime manages this element"; it carries no other information. An element in `document.head` without the attribute is **authored**.

Authored elements are never changed: while a contribution overrides one, it is set aside and restored. An implementation [must not]{.kw} modify an authored element's attributes or content, [must not]{.kw} adopt one as a contribution's element, and [must not]{.kw} remove one except to set it aside under step 2 below. A declared script [may]{.kw} share an authored `<script>` element under step S2, without modifying it. Server rendering [must]{.kw} write the marker on every element it writes for a head declaration, and hydration [must]{.kw} adopt only elements that carry it. A native implementation [may]{.kw} track ownership internally, but [must]{.kw} write and read this attribute wherever ownership passes from server output to a client.

**Terms.**

- A **contribution** is one head declaration of one connected instance, with its bindings evaluated. A page-wide head entry from an [imported component](#page-wide-head-entries) is not a contribution; the implementation [must]{.kw} report a diagnostic for it. A JSON-LD declaration whose bound value is `null` is not a contribution while its value is `null`.
- Each contribution has a **key**: `title` for `<title>`; `canonical` for `<link rel="canonical">`; `name` and the ASCII-lowercased `name` for `<meta name>`; `property` and the `property` value for `<meta property>`; the ASCII-lowercased `rel` and the resolved `href` for any other `<link>`; and the resolved URL with `classic` or `module` for a declared script. The first four are **competing** keys, the next is a **shared** key, and the last is a **script** key. A JSON-LD contribution has no key: it is **owned**, identified by its instance and its declaration, and never shared with another contribution.
- A `<meta>` key whose name or property has three or more colon-separated parts is a **sub-property** of the key formed by removing its last part and colon, with the same attribute. A key that is not a sub-property is a **top-level** key. A top-level competing key's **family** is the key and every key that is, directly or through another, its sub-property.
- Instance A has higher **precedence** than instance B when A is deeper in the logical component tree, or at equal depth when A connected after B.
- An **update** is one set of connections, disconnections, and binding changes that an implementation processes together: one batch of mutation records for the polyfill, one commit for a framework adapter, one navigation for an application router.

**Reconciliation.** After each update, once that update's connections and disconnections have happened and before its rendering is presented, the implementation [must]{.kw} reconcile `document.head` once:

1. Compute the target state. For each top-level competing key with at least one contribution, the **winner** is the contributing instance with the highest precedence, and the target is the winner's contributions to the key's family, in the winner's declared order. A contribution to a sub-property key whose winner's family does not include it is not part of any target. For each shared key with at least one contribution, the target is one element. A key with no contribution has no target.
2. For each top-level competing key with a target, if marked elements for its family are in `document.head`, update them to the target: set attributes and text, changing only values that differ, and insert or remove marked elements after the last one so their number and order equal the target's. Otherwise, if authored elements for the family are in `document.head`, record them in order as the family's **set-aside elements**, insert the target's elements, newly created and marked, before the first of them, and remove them from `document.head`. Otherwise append the target's elements, newly created and marked, to `document.head`.
3. For each top-level competing key without a target, if it has set-aside elements, insert them in their recorded order before the first marked element of its family and forget the record. Then remove the family's marked elements.
4. For each shared key with a target, if `document.head` holds a marked or authored element with that key, leave it as it is. Otherwise create the element, mark it, and append it to `document.head`.
5. For each shared key without a target, remove its marked element. A marked element that a script entry owns under step S4 is never removed.
6. For each owned contribution, if its instance and declaration have an element, update its text, changing it only if it differs. Otherwise create the element, mark it, append it to `document.head`, and record it as that instance and declaration's element. Then remove the element of each instance and declaration that has no contribution, because the instance disconnected or the value is `null`, and forget the record.
7. Create new elements in tree order of their instances, then declared order. Leave every element whose key has an unchanged target, and every owned contribution's element, in place: an element present before and after reconciliation [must not]{.kw} be removed and reinserted.
{.algo}

An implementation [must]{.kw} create every element it inserts for a contribution as a new element of the document. It [must not]{.kw} insert, move, or clone a definition's own nodes.

**Scripts.**

1. **S1. Bind.** When an instance connects and its definition declares a script, the implementation [must]{.kw} bind the instance to the document's script entry for that script's key, creating the entry under S2 if there is none.
2. **S2. Create an entry.** If the document contains an authored `<script>` element whose `src` resolves to the entry's URL and whose type matches, the entry uses that element and [must not]{.kw} modify it. Otherwise the entry has no element yet.
3. **S3. Check agreement.** When an instance binds to an entry whose first declaration, or authored element, has a different `integrity`, `crossorigin`, or `referrerpolicy`, the implementation [must]{.kw} report an error diagnostic and treat the script as failed for that instance: its `ready` rejects with a `TypeError` that describes the conflict, and `on:error` runs for it under S8. A different `fetchpriority` is not an error; the element keeps the value of the declaration that inserted it.
4. **S4. Insert.** When a bound instance calls for the script and the entry has no element, the implementation [must]{.kw} create one `script` element in the document, set its `src` to the resolved URL, copy the standard attributes from that instance's declaration, apply the [nonce rule](#declared-scripts-csp), mark it with `data-component-head`, append it to `document.head`, and observe its `load` and `error` events. An instance calls for the script when it connects, for `loading="eager"`; when its root first comes within the distance of the viewport at which the user agent fetches an `<img loading="lazy">`, for `lazy`; and when its controller calls `load()`, for `manual`. A marked `<link rel="preload">` or `<link rel="modulepreload">` whose `href` is the entry's URL belongs to the entry.
5. **S5. Keep.** The entry, its element, and any preload link it owns last for the document's lifetime. The implementation [must not]{.kw} remove, reinsert, or re-run them.
6. **S6. Settle.** The entry settles as loaded when its element fires `load`, and as failed when it fires `error`. An entry that uses an authored element that has not fired either event by the time the entry is created settles on the first one it fires, except that the implementation [must]{.kw} treat it as loaded at creation when it is a parser-inserted classic script without `async` or `defer`, or when the document's `load` event has already fired.
7. **S7. Settle `ready`.** Each entry has one `ready` promise, created with the entry. When the entry settles, the implementation [must]{.kw} resolve it when loaded, or reject it with the `error` event when failed, before it runs any handler under S8. It settles once and is shared by every instance bound to the entry, except that an instance in conflict under S3 has its own `ready`, rejected with the `TypeError`.
8. **S8. Run one handler per connection.** For each connection of a bound instance, the implementation [must]{.kw} run exactly one of the declaration's `on:load` and `on:error` handlers, once the entry has settled: when the entry settles, it queues one microtask for each bound instance that is connected and has not run a handler in its current connection; when an instance connects to an entry that has already settled, it queues that microtask at connection. The microtask runs `on:load` when the entry loaded and `on:error` when it failed, or `on:error` for an instance in conflict under S3. No handler runs while an instance is disconnected. A connection that ends before its microtask runs gets neither handler, and each later connection gets its own.
{.algo}

A script's status describes its entry: `pending` is true from the insertion of the entry's element until the entry settles, `ok` becomes true when it loads, and `error` becomes the `error` event when it fails. Before insertion, `pending` and `ok` are false and `error` is `null`. For an instance in conflict under S3, `pending` and `ok` are false and `error` is the `TypeError`.

Handlers run per connection because each connection is a fresh setup: work done in `on:load`, such as mounting a payment form's card field, has to run again after the instance reconnects. `ready` is a promise about the script, so it settles once.

> [!note] What S6 cannot see
> The DOM records no "has loaded" flag on a script element, so S6 infers it. Its inference has two limits: an authored script that failed before the runtime looked reads as loaded, and so does one that other code inserted after the document's `load` event and that is still loading. Declaring the script, rather than authoring it, avoids both.

### Page changes and client navigation {#head-transitions}

An update can disconnect some components and connect others in one step. The commonest is an application router's client navigation, which replaces one page component with another inside the same layout.

The implementation [must]{.kw} apply such an update's head changes as one reconciliation, after the new instances connect. No intermediate head state is observable: no layout title appears between two page titles, and an entry both pages contribute stays in place. The reconciliation [must]{.kw} run in the same update as the content change; inside a [view transition](https://drafts.csswg.org/css-view-transitions-1/), it runs within the transition's update callback. Back and forward navigation reconcile the same way. Declared scripts are never reinserted or re-run.

A single title change also means one screen-reader announcement of the new page, rather than an announcement of a transient title first.

Navigating from `/docs/a/` to `/docs/b/` inside a `docs-layout` that sets the title `Docs · Acme`, where both pages preconnect to `https://search.acme.example`:

| Moment | Instances | `document.head` |
| --- | --- | --- |
| Before | `docs-layout`, `page-a` | `<title data-component-head>Install · Docs</title>`, `<link rel="preconnect" href="https://search.acme.example" data-component-head>` |
| The router disconnects `page-a` and connects `page-b` | `docs-layout`, `page-b` | Unchanged. Reconciliation has not run. |
| Reconciliation | `docs-layout`, `page-b` | The same `<title>` element's text becomes `Configure · Docs`. The preconnect link is the same node, untouched. |

The title never reads `Docs · Acme`, and the preconnect link is never removed and reinserted.

### Page-wide head entries {#page-wide-head-entries}

Some head entries affect the whole page: its identity for search engines and sharing, and page-wide behavior. These are **page-wide head entries**, and only an **application component** can contribute them:

| Entry | Why the application owns it |
| --- | --- |
| `<link rel="canonical">` | Tells search engines which URL represents this document. |
| `<link rel="alternate">` | Declares other documents, such as translations and feeds, as versions of this one. |
| `<link rel="icon">` | The icon people recognize the site by in tabs and bookmarks. |
| `<link rel="manifest">` | Makes the document an installable application, with its own name, icons, and scope. |
| `<meta name="robots">` | Controls whether search engines index the document and follow its links. |
| `<meta name="referrer">` | Sets the referrer policy for every request the document makes. |
| `<meta name="viewport">` | Controls layout and zoom for the whole document, including whether people can zoom. |
| `<meta name="color-scheme">` | Selects light or dark rendering for the whole document. |
| `<meta name="theme-color">` | Colors the browser interface around the document. |
| `<meta property="og:url">` | The URL that link previews and social sharing attribute the document to. |
| `<meta name="component-src">` | Says which sources supply application components, below. |

**Application components.** A definition is an **application component** when it is one of these:

- part of the build's own source, in a build;
- written inline in the application document;
- loaded through URL-like references only, from the application document down, from a final response URL that matches the document's **`component-src` list**.

Every other definition is an **imported component**. That includes any definition reached through a bare specifier, such as an installed package subpath or a mapped live import, any definition from an unlisted cross-origin source, and every definition reached from an imported one. A resource reached both ways is an imported component.

The source list uses the grammar of a CSP source list: space-separated source expressions such as `'self'`, origins, and URL path prefixes. A URL matches it by the CSP rules for matching a URL to a source list, with the application document's origin as `'self'`.[^9] The application declares the list in its own authored head:

```html
<meta name="component-src" content="'self' https://cdn.acme.example/ui/">
```

- The list always includes `'self'`, so same-origin definitions are application components even when the meta is absent.
- A source the list names is also loadable: the loader [must]{.kw} accept a cross-origin component root whose URL matches a listed source expression and is reached by a URL-like reference, such as `<link rel="component" href="https://cdn.acme.example/ui/dashboard.html">`, as it accepts a same-origin one, without an import-map entry. The URL prefix that source expression names, or the root's origin when it names none, is the root's approved scope: its relative component and controller edges stay inside it, as they stay inside an [application-mapped prefix](/declarative-components/security#live-components-use-an-application-owned-trust-root).
- The implementation [must]{.kw} read the list only from the first `<meta name="component-src">` in the application document's authored head, as parsed. It [must]{.kw} ignore this entry from any component, application or imported, and [must]{.kw} report a diagnostic for a second authored one.
- A build reads the list from the application's document template.

The runtime ignores an imported component's page-wide head entries and reports a diagnostic. Its other head declarations apply as usual.

> [!note] The name and grammar of `component-src`
> The name follows CSP Level 3, whose fetch directives name a resource type plus `-src`: `script-src`, `img-src`, `style-src`, `frame-src`, `connect-src`, `font-src`, and `manifest-src`.[^9] `component-src` names where an application's own components come from. Its value reuses CSP's source-list syntax and source-expression matching exactly, `'self'`, origins, and path prefixes included, the same origin-list idea as a Permissions Policy allowlist.[^10] One difference is deliberate: a CSP `*-src` directive only permits loading, while `component-src` also marks matched components as the application's own, so they may set page-wide head entries. A browser could adopt the same name as a real CSP directive, delivered in the `Content-Security-Policy` header, such as `component-src 'self' https://cdn.acme.example/ui/`, with no change in meaning; the meta is then its in-document form.

In an application framework with file-based pages, pages and layouts live in the application's source, so they are application components. A component installed from a package is an imported component, even when an application page renders it.

```html title="app/pages/pricing.html"
<template component="page-pricing">
  <defs>
    <title>Pricing · Acme</title>
    <meta name="description" content="Plans for teams of every size.">
    <link rel="canonical" href="https://acme.example/pricing">
    <meta name="app:layout" content="marketing">
  </defs>
  <main>…</main>
</template>
```

A `<meta>` name that contains a colon, such as `app:layout`, belongs to the application build that defines it. This specification gives it no meaning: the runtime adds it to the head like any other `<meta>`, and a build that reads it at build time, here to choose the page's layout, may leave it out of its output.

### Server rendering and hydration {#head-ssr}

A server-rendered page arrives with its head already written, so a crawler or a no-JavaScript reader sees the title, description, and structured data. Hydration then takes over the same elements. Nothing renders twice, and no script runs twice.

1. **H1. Write contributions.** Server rendering [must]{.kw} compute the result of [reconciliation](#head-management) over the rendered tree, starting from the application document's authored head, and write that head, with each contribution's element marked `data-component-head`.
2. **H2. Write set-aside elements.** For each family whose authored elements reconciliation sets aside, server rendering [must]{.kw} write those elements, unmodified and in their recorded order, as the content of a `<template data-component-head="set-aside">` placed immediately after the family's last marked element. It [must not]{.kw} write them anywhere else.
3. **H3. Preload eager scripts.** For each script that an `eager` declaration in the rendered tree calls for, and that no authored script in the document satisfies under S2, server rendering [must]{.kw} write one `<link rel="preload" as="script">`, or `<link rel="modulepreload">` for `type="module"`, with the resolved URL as its `href`, the declaration's `crossorigin`, `integrity`, `referrerpolicy`, and `fetchpriority` where present, and `data-component-head`. It [must not]{.kw} write an executing `<script>` element for a declared script.
4. **H4. Leave lazy and manual scripts out.** Server rendering [must not]{.kw} write anything for a `lazy` or `manual` script. A component that wants an early connection declares its own `<link rel="preconnect">`, which H1 writes like any link. An automatic one would open connections for scripts that may never load.
5. **H5. Adopt.** Before its first reconciliation, the client runtime [must]{.kw} adopt each marked element whose key has a target, recording the instances that contribute it, and [must not]{.kw} insert a second element for an adopted key. For each `<template data-component-head="set-aside">`, it [must]{.kw} take the template's child elements, in order, as the set-aside elements of the family whose marked elements precede it, hold them detached, outside the template, and remove the template. Reconciliation then changes only values that differ. It [must]{.kw} adopt the marked JSON-LD blocks, in document order, as the elements of the owned contributions taken in tree order of their instances, then declared order. Marked elements whose keys have no target, and marked JSON-LD blocks left over, are removed by that first reconciliation, except preload links that a script entry owns under S4.
6. **H6. Insert eager scripts once.** After adoption, each eager declaration calls for its script under S4. The runtime inserts the real `<script>` exactly once; the browser serves it from the preload, runs it once, and its `load` or `error` event settles `ready` under S7 and runs each connected instance's `on:load` or `on:error` under S8.
{.algo}

H1 and H5 identify elements by the marker together with their keys, so server output needs no per-element ownership record. A JSON-LD block has no key, and its position identifies it instead: step 7 appends owned elements in tree order of their instances, then declared order, so H1 writes them in that order, and hydration starts from the tree and state the server rendered, so the client's owned contributions arrive in the same order. The marker separates managed elements from authored ones, and the set-aside template carries the authored elements the client must restore later, so restoring stays exact after hydration.

| Declaration | Server output in `document.head` | After hydration |
| --- | --- | --- |
| `<title>`, `<meta>` | The winner's entries, marked, in the place of any authored element with the same key. That authored element follows in a set-aside template. | The same elements, adopted. The authored element is held aside, out of the head, until no contributor remains. |
| `<link>` other than a preload for a script | One marked element per key, unless an authored one has the key. | The same element, adopted and reference-counted. |
| JSON-LD | One marked block for each declaration of each instance whose value is not `null`. | The same element, adopted by its instance and declaration. |
| `<script src>`, `eager` | A marked `preload` or `modulepreload` link. Never a `<script>`. | One marked `<script>`, inserted once and served from the preload. The link stays. |
| `<script src>`, `lazy` or `manual` | Nothing. | Inserted under S4 when an instance calls for it. |
| `on:load`, `on:error` | Nothing. | One of the two runs for each connection, once the script settles. |

For a checkout page inside a layout that loads Stripe.js eagerly, with an application document that authors `<title>Acme</title>`:

```html title="Server output"
<head>
  <title data-component-head>Checkout · Acme</title>
  <template data-component-head="set-aside"><title>Acme</title></template>
  <link rel="preconnect" href="https://js.stripe.com" data-component-head>
  <link rel="preload" as="script" href="https://js.stripe.com/v3/" data-component-head>
</head>
```

```html title="After hydration"
<head>
  <title data-component-head>Checkout · Acme</title>   <!-- adopted: the same node -->
  <link rel="preconnect" href="https://js.stripe.com" data-component-head>
  <link rel="preload" as="script" href="https://js.stripe.com/v3/" data-component-head>
  <script src="https://js.stripe.com/v3/" data-component-head></script>
</head>
<!-- The authored <title>Acme</title> is held aside, unmodified, to be restored. -->
```

```js title="What a conformance test checks"
// Hydration adopts the server's nodes instead of replacing them.
assert.equal(document.querySelector("title"), serverTitle);
assert.equal(document.title, "Checkout · Acme");
// One Stripe.js element, run once.
assert.equal(document.querySelectorAll('script[src="https://js.stripe.com/v3/"]').length, 1);
assert.equal(onLoadRuns("checkout-form"), 1);
// Removing and re-adding the form runs on:load again for the new connection,
// without inserting or running the script again.
form.remove(); main.append(form); await microtasks();
assert.equal(onLoadRuns("checkout-form"), 2);
assert.equal(document.querySelectorAll('script[src="https://js.stripe.com/v3/"]').length, 1);
// When no component sets a title, the authored node returns: the same object.
await navigate("/no-title/");
assert.equal(document.querySelector("title"), authoredTitle);
```

### Generated components {#head-generated}

A generated React, Vue, or Svelte component [must]{.kw} produce the same head contributions, at the same lifecycle points, with the same marker, keys, precedence, page-wide head entry rule, reconciliation, and script sharing, through its host adapter. An adapter [may]{.kw} use its framework's own head mechanism when the observable result is the same.

> [!note] Platform integration
> A native implementation needs three things: DOM insertion, removal, and value changes in `document.head` when instances connect and disconnect; the reconciliation steps above; and HTML's existing `<script>` and `<link rel="preload">` elements. It [may]{.kw} track ownership internally, but it uses the `data-component-head` marker for the handoff from server output to the client, so output from any server hydrates under any client. It needs no new security primitive: CSP, Subresource Integrity, CORS, and mixed-content blocking apply because each contribution is an ordinary element in the document. It is also much smaller than [HTML Imports](#imported-definitions-are-inert): there is no second document, no parser-blocking load, and no new script-ordering model. Each declared script is one script inserted through the DOM.

## Native lowering and explicit root branches

A component [should]{.kw} lower to the native element named by `nativeElement`: a button component *is* a real `<button>`, so form association, focus, and accessibility are the browser's. Undeclared invocation attributes pass through to that root; owned template attributes and prop targets take precedence.

A polymorphic component declares `as` as a keyword prop constrained to its supported roots and selects between explicit native roots with `$match`. The prop does not retag an element: the definition contains the actual `<button>` and `<a>` branches that it may render. Like any `$match`, the selection follows the prop: when it changes, the newly selected branch's element takes the previous root's place, keeping the instance's state, the consumer's projected content, and the attributes the consumer supplied.

```html
<template component="x-button">
  <defs>
    <prop name="as" type="keyword" values="button, a" default="button">Native root.</prop>
  </defs>

  <!-- Both possible native roots are visible in the definition. -->
  <template $match>
    <a $when="$as = 'a'"><slot></slot></a>
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
<button data-component="x-button">Save</button>
```

> [!norm] Determinism: one DOM, either path
> Lowering [must]{.kw} be a deterministic function of the invocation and the definition alone: no timestamps, generated ids, or client-only state. The converter running on the server and the polyfill running in the browser therefore produce **byte-identical** native DOM for the same source, so an SSR'd root and an in-browser-lowered root are indistinguishable. This is the equivalence contract applied to a single node.

Every lowered root carries one provenance attribute, `data-component`, injected by the implementation rather than authored. Its value is a **space-separated token list**, outermost invocation first, exactly like `class` or `rel`: a component that lowers straight to a native element carries a single token (`data-component="x-button"`), and one whose root is another component carries the whole lineage (`data-component="x-primary x-button"`). Each token is a component tag, so it resolves through the ordinary component registry, the loaded `<template component>` definitions keyed by tag, exactly the way `customElements` resolves a custom-element tag to its definition; no separate provenance format exists or is needed. Because it is deterministic, the stamp is identical under SSR and in-browser, and it composes across nested components and imported partials. How server output records slot boundaries and content no slot renders yet, so hydration rebuilds the same instance, is defined in [Rendered form & hydration](/declarative-components/rendered-form). Content projected through a `<slot>` is the consumer's, not the component's, so it keeps whatever provenance it already had and is never re-stamped as the enclosing component.

The root's visible attributes come from the template, its bindings, and invocation attributes that pass through. A prop is input to that rendering; it is not automatically exposed as `data-<name>`. The reference runtime may carry prop data for hydration, but its storage format is not an authored or observable component contract. Recovering explicit prop values after server rendering remains a [rendered-form question](/declarative-components/rendered-form). See [Types](/declarative-components/types) for how authored values are parsed.

A literal attribute on the invocation supplies the prop's **initial configuration**. Afterwards a prop changes through a parent template's `from:name` binding or the props a framework passes. Such a change updates bindings and state derived from that prop; it does not require a visible `data-<name>` attribute on the root.

The stamp is also what makes hydration an **adopt-in-place**, not a rebuild. An implementation lowers where it finds an `<x-button>` invocation, and *adopts* where it finds an already-lowered `[data-component]` root: it binds reactivity and events onto the existing node instead of recreating it. An SSR'd tree therefore hydrates with no replacement and no flicker, and a client-only page lowers to the same result. The only difference is a pre-lowering moment that exists only client-side, where the unknown `<x-button>` shows its children inline; SSR skips it.

## Slots

Content projection uses the native-shaped `<slot>`. Level&nbsp;1 includes default, named, fallback, and scoped slots because all four are part of the baseline component contract.

A slot's name is written, never computed, on both sides:

- An outlet's `name`, or the `$slot` value of a [`<template $slot>`](#parser-safe-outlets) outlet, is a literal [identifier](/declarative-components/expressions#identifier-spelling-and-case), with the spelling an expression name uses: letters, digits after the first character, and `_`, but no `-`. `<slot name="labelAction">` names a slot; `<slot name="label-action">` is an error.
- A consumer's `slot` attribute, on an element or on a `<template slot>`, is the same kind of literal identifier, naming the slot it fills. A value that is not an identifier, such as `slot="$which"`, and a bound `from:slot` are errors.
- An empty `slot=""` assigns content to the default slot, as having no `slot` attribute does.

Fixed names keep a component's slots part of its public interface: tools list them, generated components type them, and a consumer's content never changes slots as data changes. Content that varies by item is one named [scoped slot](#scoped-slots) that passes the item as a prop.

### Named & fallback {#named-fallback}

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

A slot shows its fallback while nothing is assigned to it, as a native `<slot>` shows its own children while it has no assigned nodes.[^11] Content the consumer writes under `$if` or `$each` is assigned while it renders. A slot whose only content is a false `$if`, or an `$each` with no rows, shows its fallback. When that content appears, the slot switches to it, and back to the fallback when it goes:

```html
<!-- use: the header reads "Untitled" until $heading has a value -->
<x-card>
  <h2 slot="title" $if="$heading">{$heading}</h2>
  <p>Body content lands in the default slot.</p>
</x-card>
```

Conditional and repeated content goes to the slot its `slot` attribute names whenever it renders, on the first render or after a later change.

### Content that renders on demand {#content-that-renders-on-demand}

Projected elements belong to the consumer, so they exist as soon as the consumer renders. They load their resources and bind even while their slot is not rendered, for example under a false `$if`. Only a component invoked among them waits: it is set up when a slot first places it. To defer the elements themselves until their slot renders, wrap them in a `<template slot="name">`:

```html
<!-- definition -->
<template component="x-disclosure"> …
  <div>
    <button type="button" on:click="toggle">More</button>
    <section $if="$open"><slot name="details"></slot></section>
  </div>
</template>

<!-- use: nothing inside the template exists until the section opens -->
<x-disclosure>
  <template slot="details">
    <img src="chart.png" alt="Sales by month">
    <x-chart from:rows="$sales"></x-chart>
  </template>
</x-disclosure>
```

- A slot renders the children of a consumer's `<template slot>` only while the slot itself renders. Until then nothing inside the template is created, fetched, or bound, and no component inside it is set up. The slot that receives the template decides. If a component places that slot inside content it projects into another component, the slot renders, and so does the template, even while the other component's slot is hidden; there the rendered elements are plain projected content.
- The children render in the consumer's scope with the consumer's bindings, like an `$if` body. Each time the slot renders again they render afresh, so elements and component state inside them do not survive a close and reopen.
- If a consumer supplies more than one `<template slot>` for the same slot, the slot renders the first. Other content assigned to that slot is not rendered with it.
- A slot without props accepts plain elements, and their projection stays eager as described above: the elements keep their identity while the slot closes and reopens, and a controller can read them through [`host.slots`](/declarative-components/javascript) while the slot is hidden. A listbox that reads its options while its panel is closed relies on this.
- A slot that exposes props, a scoped slot (below), renders only a `<template slot>`, because only a template can receive its props. Plain elements assigned to it without a template are an error, reported with a diagnostic; with nothing assigned, it shows its fallback.
- Server output keeps the `<template slot>` itself in the [carrier](/declarative-components/rendered-form), unrendered, whether or not its slot renders. Hydration renders it when its slot renders.

Use a template for content that is costly to create or load and only needed when shown. Project plain elements when the component must reach them while they are hidden.

### Scoped slots

A slot may expose data to the content projected into it. The definition declares the slot's props in `<defs>` and gives them on each `<slot>` outlet; the consumer supplies a `<template slot="name">`, which renders [on demand](#content-that-renders-on-demand) as above. Its **scope adds those exposed props** to the consumer's own: no new prefix, consistent with `$with`-style scoping.

```html
<!-- definition: a disclosure that tells its summary its label and how many items it holds -->
<template component="x-disclosure">
  <defs>
    <prop name="items" type="list(string)" default="[]">The items.</prop>
    <state type="boolean" name="open" value="false"></state>
    <handler name="toggle"><set name="open" expr:value="not $open"></set></handler>
    <slot name="summary">
      <prop name="label" type="string" default="Details">The summary's text.</prop>
      <prop name="count" type="number" required>How many items there are.</prop>
    </slot>
  </defs>
  <div>
    <button type="button" on:click="toggle">
      <slot name="summary" label="Open" from:count="$items.length">Details</slot>
    </button>
    <ul $if="$open"><li $each="item of $items">{$item}</li></ul>
  </div>
</template>

<!-- use: the template's scope is { label: string, count: number } -->
<x-disclosure from:items="['a', 'b']">
  <template slot="summary">{$label} ({$count})</template>
</x-disclosure>
```

### Declaring a slot's props {#slot-props}

- A `<slot>` inside `<defs>` is a **declaration**, never an outlet: it renders nothing. Its `name` names the slot it declares; without `name` it declares the default slot. A component declares each slot once.
- Its children are `<prop>` elements with exactly the vocabulary of a component's [`<prop>`](#element-reference): `name`, `type`, `values`, `default`, `required`, and a description as element text. Each name must be a valid name in expression scope, and unique within the slot.
- The declared props are part of the component's public interface, beside its props, events, and requests: tools list them, and generated components type them.

### Giving slot props on an outlet {#slot-prop-outlets}

A slot prop is given on the `<slot>` outlet the way a prop is given to a component invocation:

- **Static.** Every plain attribute on the outlet other than `name` is a prop's input. It converts by the declared type exactly as an invocation attribute converts by a component `<prop>`: with `type="number"`, `count="3"` gives `$count` the number `3`.
- **Bound.** `from:count="$items.length"` gives `$count` the expression's value, checked as an [accepted value](/declarative-components/javascript#accepted-values-and-prop-inputs) of the declared type, and follows it as it changes. A value that is not present, `null` or `undefined`, takes the prop's `default`, or `null` without one. A value the declared type rejects does the same, and the implementation [should]{.kw} warn once, naming the slot and the prop.

Static and bound props mix freely on one outlet. These are errors, each reported with a diagnostic that names the outlet:

- An outlet gives a prop its slot does not declare, or gives props to a slot with no declaration. The diagnostic names the `<slot>` and `<prop>` declaration to add.
- An outlet gives the same prop both ways (`label` and `from:label`).
- An outlet omits a `required` prop. A prop with a `default` that an outlet omits takes its default; one without either is absent from the template's scope.

An outlet with any prop is a scoped slot: it renders only a `<template slot>`, as below.

A slot that owns iteration gives each row's props the same way. Here the outlet sits in a table row, so it is written as a [`<template $slot>`](#parser-safe-outlets), which the HTML parser keeps in place:

```html
<!-- definition: a list that owns iteration, slots each row out -->
<defs>
  <prop name="rows" type="list(object({ id: string, name: string }))" required>The rows.</prop>
  <slot name="row">
    <prop name="kind" type="keyword" values="person, team" default="person">What a row is.</prop>
    <prop name="item" type="object({ id: string, name: string })" required>The row.</prop>
    <prop name="index" type="number" required>The row's position.</prop>
  </slot>
</defs>
<table><tr $each="row of $rows" $key="$row.id"><template $slot="row" kind="person" from:item="$row" from:index="$loop.index"></template></tr></table>

<!-- use: the template's scope is { kind, item, index } -->
<x-list from:rows="$people">
  <template slot="row"><td>{$item.name}</td></template>
</x-list>
```

Vue gives a scoped slot's props the same two ways, a plain attribute on its `<slot>` and a bound `:prop`, with only `name` reserved, and types them with `defineSlots`.[^12]

### Outlets in tables: `<template $slot>` {#parser-safe-outlets}

A `<slot>` cannot sit directly in table structure. The HTML parser moves (foster-parents) a `<slot>` written directly in `<table>`, `<thead>`, `<tbody>`, `<tfoot>`, `<tr>`, or `<colgroup>` out to just before the `<table>`, so the rows or cells it renders would land outside the table.[^13] Write the outlet there as a `<template>` with `$slot`:

```html
<!-- definition: header cells and rows slotted into table parts -->
<template component="x-table"> …
  <table>
    <thead><tr><template $slot><th>Name</th></template></tr></thead>
    <tbody>
      <template $slot="row" $each="row of $rows" $key="$row.id" from:item="$row">
        <tr><td>{$row.name}</td></tr>
      </template>
    </tbody>
  </table>
</template>

<!-- use: the consumer's table content is in <template slot> too -->
<x-table from:rows="$people">
  <template slot=""><th>Person</th></template>
  <template slot="row"><tr><td>{$item.name}</td></tr></template>
</x-table>
```

- `<template $slot>` is the default slot's outlet, and `<template $slot="row">` the outlet of the slot named `row`. The value follows the slot-name rules above; an empty value, like no value, means the default slot. `name` is not one of its attributes.
- It is the same outlet as the matching `<slot>`, written another way. Every other plain attribute is a static slot prop and every `from:` attribute a bound one, its content is the fallback, it renders a consumer's `<template slot>` for a [scoped slot](#scoped-slots), and it may carry `$each` or `$if`. Slot props are declared with a `<slot>` in `<defs>` either way.
- It renders no `<template>` element. Like a `<slot>` outlet, it is replaced by what it renders, and its [rendered form](/declarative-components/rendered-form#template-slot-outlets) is the same.
- It is valid wherever a `<slot>` outlet is. Table parts need it; elsewhere the two forms are interchangeable.
- A build tool [should]{.kw} report a `<slot>` that the parser moved out of a table, and suggest `<template $slot>`.

A `<template>` is used for the same reason [structural directives ride on one](/declarative-components/templating#parser-contexts): the parser keeps it wherever it is written, including table parts, and parses its content in the context of its first element, so a `<tr>` inside it stays a `<tr>`. A consumer's table content goes in a `<template slot>` for that reason: inside `<x-table>`, the parser drops `<tr>`, `<th>`, and `<td>` tags it finds outside a table. The `$` marks `$slot` as changing what the `<template>` does, as `$each` does, and keeps it apart from `slot`, which says which slot a consumer's content fills.

### Component ancestry for shared state {#component-ancestry-for-shared-state}

Each nested component has a logical parent: the component whose markup or slot outlet renders it. A component projected into a slot therefore sees the receiving component in its ancestry for [shared state](/declarative-components/reactivity); if content passes through more slots, each receiving component is in that chain. Its ordinary expressions still use the consumer's lexical scope, and its projected nodes keep their existing provenance rather than receiving the slot owner's `data-component` stamp. Context lookup and expression scope answer different questions.

Moving a component's rendered nodes with `<portal>` keeps that logical ancestry. Moving the DOM nodes alone does not select a different state ancestor. The nearest ancestor with the requested state cell supplies it, whether or not its native root is a DOM ancestor.

## Composition

### <template src>: import a component or partial

Native `<template>` has no `src`, so HTML Next defines it: `<template src="…">` loads an external component definition or partial. It is the import mechanism and the hook for lazy, code-split components. With no runtime it degrades to an empty inert template, safe.

```html
<template src="./card.html"></template>        <!-- register x-card -->
<template src="./chart.html" defer></template>  <!-- lazy: load on first use -->
```

### Choosing a component at runtime

When data decides which component renders, list each candidate as an arm of a [`$match`](/declarative-components/templating). The first arm whose `$when` is truthy renders, and when the data changes, the newly chosen arm replaces it. Every component the markup can render is named in the source, so its definition resolves the same way as any other invocation.

```html
<template $match>
  <x-callout $when="$block.type = 'callout'" from:data="$block"></x-callout>
  <x-figure $when="$block.type = 'figure'" from:data="$block"></x-figure>
  <p $else>{$block.text}</p>
</template>
```

A component that chooses its own native root uses the same pattern at its root; see [Native lowering and explicit root branches](#native-lowering-and-explicit-root-branches).

### <portal to>: render elsewhere {#portal}

Overlays (dialogs, tooltips, toasts) render outside their DOM position while staying logically owned by the component. `<portal to="selector">` moves its children to the target (a CSS selector or an element id) while preserving reactive bindings and event wiring. The term is React `createPortal`; Vue `Teleport` was originally named `<portal>`, and Angular CDK ships a `Portal` too.[^8]

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

For live loading, the loader [must]{.kw} fetch the HTML resource referenced by `<link rel="component">` and parse its contents as an inert HTML fragment in a `<template>` context. Build-time imports use the same parsing contract. A resource may contain sibling component carriers and dependency links, together with the build metadata allowed [below](#resource-contents); it does not need a document-level `<html>`, `<head>`, or `<body>` wrapper.

### What a component resource contains {#resource-contents}

A component resource is a file of component carriers and the dependency links they need. It may also hold build metadata for the file as a whole, such as which of its components is a page:

```html title="products.html"
<meta name="app:page" content="page-products">
<link rel="component" href="./product-summary.html">

<template component="page-products">
  <defs>
    <title>Products · Admin</title>
    <meta name="app:layout" content="admin">
  </defs>
  <section><h1>Products</h1><product-summary></product-summary></section>
</template>
```

Everything a component adds to the document head belongs to that component, in its carrier's `<defs>`, as [head declarations](#head-declarations). Only build metadata stays at resource scope, because it describes the file rather than any one component. A resource [must]{.kw} contain at least one component carrier. After HTML fragment parsing, its resource-level nodes are handled as follows:

| Resource-level node | Component loader behavior |
| --- | --- |
| `<template component="…">` | Parse and register the component definition. |
| `<link rel="component" href="…">` | Resolve the component dependency. |
| `<meta name content>` whose `name` contains a colon, such as `app:page` | Build metadata. The loader ignores it; it is never added to the document. |
| Comments and whitespace-only text | Ignore. |
| Anything else, including `<title>`, any other `<meta>`, any other `<link>`, `<style>`, any `<script>`, `<base>`, HTML Imports, ordinary body elements, plain non-component templates, and non-whitespace text | Reject as invalid resource content. |

A carrier's direct children are its `<defs>`, its markup root, and its `<style>`; a head element placed directly in the carrier, outside `<defs>`, is invalid. A namespaced name such as `app:page` belongs to the application build that defines it: in this example it selects the page component in a file that holds several. Its spelling and meaning are the build's, and the component runtime gives it none. See [Security](/declarative-components/security) for the imported-resource boundary.

### One import form, live or packaged {#one-import-form-live-or-packaged}

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
> A no-build page may map one package prefix to a versioned CDN directory through the ordinary import map `imports` table[^6]. That application-owned prefix is both the resolver and the boundary for declarative definition edges: relative component links and carrier controller references may stay within it, while an edge outside it must use another bare specifier the application maps. Imported definitions cannot contribute import maps or widen a prefix. Once a trusted controller runs, its own imports are ordinary ESM governed by CSP rather than a directory sandbox; [Security](/declarative-components/security) defines that boundary precisely.

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

The definition's `<style>` may also declare CSS `@import` edges. A static graph walk includes their transitive stylesheet dependencies, using the [shared CSS resolution and scoping contract](/declarative-components/styling#shared-css). Resolving these stylesheets requires no controller execution.

### Imported definitions are inert {#imported-definitions-are-inert}

`<link rel="import">` (HTML Imports)[^7] defined an imported `Document` graph together with its own parser-blocking, script-ordering, style-ordering, deduplication, `currentScript`, and custom-element processing rules. The later [HTML Modules proposal](https://github.com/WICG/webcomponents/blob/gh-pages/proposals/html-modules-proposal.md) explicitly identified global-object pollution and parse blocking among the problems and attempted to move the graph into ES modules. HTML Next keeps component definitions declarative and gives their one optional imperative edge to the existing ES-module loader.

A component definition **contains no executable code: code is referenced, never embedded**. Its only children are an optional `<defs>` region, one markup root, and an optional `<style>`. It [must not]{.kw} contain an inline executable `<script>`, inline event handlers, or anything requiring `eval()`, and bindings use a restricted pure expression language rather than ambient JavaScript. Code reaches a component only through references the definition makes visible: the carrier's `controller` module and the `src` of each [declared script](#declared-scripts). The platform loads both under the page's CSP, and only when an instance connects. So importing a definition is a pure fetch, parse, and register: no code executes, no globals are shared, nothing changes in the document, and there is no lifecycle to order. Registration is idempotent, deduplicated by tag, with a duplicate tag a conformance error, precisely because there are no script side effects to double-run.

> [!norm] Definitions stay declarative
> The definition contains no executable code, and its reactivity lowers and compiles. Imperative behavior lives in code the definition references by URL: its controller in the **ES module system**, reserved for a later level, and any declared scripts. Both are the only parts with a real lifecycle, and both start when an instance connects. Code lives in referenced files while the component definition remains data.

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
<button data-component="x-primary x-button">Save</button>
```

A delegating component forwards like any other lowering: its own declared props are applied through the bindings in its markup, template-owned attributes (here `variant="solid"`) take precedence, and any undeclared invocation attributes pass through to the delegated root and continue down the chain. Its `nativeElement` and native attribute surface are whatever the chain ultimately resolves to, so its generated types inherit that surface.

> [!note] The Level 1 single-root boundary
> A component that emits sibling `<li>`, `<tr>`, or `<option>` elements would have no single native element for invocation attributes, the provenance stamp, `:host`, controller `host.root`, or element events and methods. The source syntax also fails in a key case: when HTML parses an `<x-rows>` invocation inside `<tbody>`, it moves the custom element outside the table while keeping the `<tr>` elements inside. A browser runtime cannot reliably recover that invocation-to-output relationship from the parsed DOM. A `<template>` carrier survives there, but would be a different invocation form, not a fragment variant of the current component contract.
>
> Frameworks support sibling output by making separate tradeoffs, not by acquiring an invisible DOM element: [Vue requires explicit attribute fallthrough](https://vuejs.org/guide/components/attrs#attribute-inheritance-on-multiple-root-nodes) for multiple roots; [React provides a distinct `FragmentInstance`](https://react.dev/reference/react/Fragment#fragmentinstance) for fragment refs; [Svelte compiles sibling nodes without a wrapper](https://svelte.dev/examples/file-inputs), [scopes styles on the emitted elements](https://svelte.dev/docs/svelte/scoped-styles), and [returns component exports rather than a root element](https://svelte.dev/docs/svelte/svelte#mount). Svelte also [parses its own HTML++ source](https://svelte.dev/docs/svelte/basic-markup), so the browser never has to parse an `<x-rows>` invocation in `<tbody>`. A hostless component would need its own parsing, attribute, styling, controller, and hydration contract. Level 1 keeps the one-element-root invariant; structural `<template>` directives may still emit siblings *inside* an element-root component. Keeping `<x-rows>` as the invocation syntax in table contexts would require an HTML parser change.

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
: `<prop>`, `<event>`, `<request>`, `<slot>` declarations, `<state>`, `<computed>`, `<data>`, `<handler>`, and `<context>`, and the head declarations `<title>`, `<meta>`, `<link>`, and `<script>`, as flat siblings — everything that renders nothing in place.

Semantics
: Separates behavior/data/interface from visible markup; borrowed from SVG `<defs>`. Survives the template fragment parser where `<head>`/`<body>` do not.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<prop>" role="component interface declaration"}
Attributes
: `name` · `type` (base value type or constructor) · `pattern?` · `default?` · `required?`

Content
: the prop description (element text)

Placement
: a flat child of `<defs>` (no `<props>` wrapper); the public interface is the set of `<prop>` elements there. A `<prop>` inside a `<slot>` declaration in `<defs>` declares one of that slot's props instead

Inferred
: target from the first `from:attribute`/`.property` binding; not restated on the prop. A prop may be bound in more places; those only render it.

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<request>" role="declared question a consumer answers"}
Attributes
: `name`, `type?`, `returns?` · `<prop>` children for the detail · `<returns type>` for the answer

Placement
: a flat child of `<defs>`, beside `<prop>` and `<event>`

Asked with
: <code>host.request(<var>name</var>, <var>detail</var>, { signal, progress })</code>, resolving to the answer or `null` (see [the JavaScript Layer](/declarative-components/javascript#requests)); <code>host.hasResponder(<var>name</var>)</code> tells whether a [known responder](/declarative-components/javascript#has-responder) answers

Answered with
: a `RequestEvent` listener calling `respondWith`, [`RequestEvent.respond()`](/declarative-components/javascript#outside-a-controller), or a framework function prop; the nearest responder answers

Level
: [L2+]{.pill .soon} reserved, with the JavaScript layer
:::

::: {.entry name='<title> · <meta> · <link> · <script type="application/ld+json">' role="head declarations"}
Placement
: flat children of `<defs>`

Effect
: added to `document.head` while an instance is connected, marked `data-component-head`; competing keys by precedence, shared entries reference-counted (see [Head management](#head-management))

Bindings
: inline text in `<title>` · `from:content` · `from:href` · `from:value` on a JSON-LD block

Authority
: `canonical`, `alternate`, `icon`, `manifest`, `robots`, `referrer`, `viewport`, `color-scheme`, `theme-color`, `og:url`, and `component-src` are page-wide head entries, which apply only from application components

Level
: [L1 (proposed)]{.pill .l1}
:::

::: {.entry name="<script name src loading>" role="declared script"}
Declaration attributes
: `name?` · `loading`: `eager` (default), `lazy`, `manual` · `on:load`, `on:error`

Standard attributes
: `src` · `type?` (`module`) · `integrity` · `crossorigin` · `referrerpolicy` · `fetchpriority`, copied onto the inserted element

Exposes
: `.pending`, `.ok`, `.error` · `host.scripts.name` with `ready` and `load()` · `on:load` or `on:error` once per connection

Semantics
: one ordinary `<script>` element per URL and type in `document.head`, inserted once and never removed

Level
: [L2+]{.pill .soon} reserved, with the JavaScript layer
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
: `name?` (named slot) · any other plain attribute (a static slot prop, converted by its declared type) · `from:prop` bindings (bound slot props)

Placement
: in the markup, an outlet; inside `<defs>`, a [declaration](#slot-props) of the slot's props, whose children are `<prop>` elements

Children
: fallback content used when nothing is projected

Parser-safe form
: <code>&lt;template $slot&gt;</code> for the default slot, <code>&lt;template $slot="<var>name</var>"&gt;</code> for a named one: the same outlet, with the same props, fallback as its content, and the same rendered form; the parser keeps it in table parts, where it moves a `<slot>` out (see [Outlets in tables](#parser-safe-outlets))

Level
: [L1]{.pill .l1} · default, named, fallback, and scoped slots
:::

::: {.entry name='<link rel="component">' role="component entry import"}
Attributes
: `href`: URL-like live entry or bare package specifier · fetch vocabulary: `integrity`, `crossorigin`, `referrerpolicy`, `type`, `fetchpriority`

Semantics
: import a component resource as an inert HTML fragment and follow its statically declared dependency closure; package specifiers resolve through ordinary package/import-map resolution

Level
: [L1]{.pill .l1}
:::

::: {.entry name="<template src> · <portal to>" role="composition"}
Semantics
: import/lazy-load a definition · relocate children while preserving bindings

Level
: [L2]{.pill .soon}
:::

## Sources

[^1]: JSON Schema Validation, [the `enum` keyword](https://json-schema.org/draft/2020-12/json-schema-validation#name-enum).
[^2]: W3C XML Schema, [the `default` attribute](https://www.w3.org/TR/xmlschema11-1/#cvc-au) on element declarations.
[^3]: WHATWG HTML, [boolean attributes](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#boolean-attributes) (e.g. `required`) and [the `<option>` element](https://html.spec.whatwg.org/multipage/form-elements.html#the-option-element) (text content as label).
[^4]: WHATWG HTML, [Declarative Shadow DOM](https://html.spec.whatwg.org/multipage/scripting.html#attr-template-shadowrootmode) (`<template shadowrootmode>`, inert to native).
[^5]: SVG 2, [the `<defs>` element](https://www.w3.org/TR/SVG2/struct.html#DefsElement).
[^6]: WHATWG HTML, [import maps](https://html.spec.whatwg.org/multipage/webappapis.html#import-maps) (unrecognized top-level keys are ignored).
[^7]: W3C (retired), [HTML Imports](https://www.w3.org/TR/html-imports/) (`<link rel="import">`).
[^8]: Render-elsewhere, borrowed directly: React [createPortal](https://react.dev/reference/react-dom/createPortal) (the term) and Vue [Teleport](https://vuejs.org/guide/built-ins/teleport.html) (originally named `<portal>`), plus Angular CDK [Portal](https://material.angular.io/cdk/portal/overview).
[^9]: W3C, [Content Security Policy Level 3](https://www.w3.org/TR/CSP3/): the [fetch directives](https://www.w3.org/TR/CSP3/#directives-fetch), the [source list grammar](https://www.w3.org/TR/CSP3/#grammardef-serialized-source-list) and [matching a URL to a source list](https://www.w3.org/TR/CSP3/#match-url-to-source-list).
[^10]: W3C, [Permissions Policy](https://www.w3.org/TR/permissions-policy/): the [allowlist](https://www.w3.org/TR/permissions-policy/#allowlists) of origins a feature is enabled for.
[^11]: WHATWG DOM, [assigning slottables](https://dom.spec.whatwg.org/#assign-slotables) and [`assignedNodes()`](https://dom.spec.whatwg.org/#dom-htmlslotelement-assignednodes); CSS Scoping, [slots and fallback content in the flat tree](https://drafts.csswg.org/css-scoping/#slots-in-shadow-tree): a slot with no assigned nodes renders its own children, and switches as nodes are assigned or removed.
[^12]: Vue, [scoped slots](https://vuejs.org/guide/components/slots.html#scoped-slots): attributes on `<slot>` are passed to the slot, with `name` reserved; [`defineSlots()`](https://vuejs.org/api/sfc-script-setup.html#defineslots) types each slot's props.
[^13]: WHATWG HTML, [foster parenting](https://html.spec.whatwg.org/multipage/parsing.html#foster-parent) in the [in table insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-intable): an element that is not table content is inserted before the table, while a `<template>` start tag is processed by the in head rules and inserted where it is written.
