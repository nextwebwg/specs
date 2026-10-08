---
title: Templating
order: 1
blurb: $each · $if · $match · $with · inline text
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reserved direction · reference implementation pending
---

# Templating

Control flow is a family of **marked directives on ordinary elements**: `$each`, `$if`, `$match`, `$with`, `$value`. A leading `$` marks a *structural* directive, it controls whether, how many times, or in what scope markup is produced, distinct from the `:` binding family that sets values. There are **no control-flow elements**: every directive rides on any element or a `<template>`, so it survives every parser context, and none appears in the output.

## Structural directives

A structural directive is a `$`-prefixed attribute. It goes on the element it applies to, or on a `<template>` to apply to a group of siblings. The `$` is deliberate: bindings (`from:x`, `bind:x`, `on:x`) set or wire *values*; a `$` directive changes *whether, how many times, or in what scope* markup is produced. At lowering the directive is evaluated and **removed**, so it never appears in the output (rendered DOM, compiled component, or serialized HTML alike), which is why its attribute name is free to be a directive.

```html
<li $each="p of $products">…</li>          <!-- iterate this element -->
<p  $if="$cart.items.length">…</p>          <!-- guard this element -->
<td $value="$user.name"></td>               <!-- escaped text content -->

<!-- multi-way and scope are directives too, on an element or a <template> -->
<template $match>
  <p $when="$a">…</p>
  <p $else>…</p>
</template>
```

| Directive | Effect |
| --- | --- |
| `$each="item of $items"` | Instantiate once per element of `items`, binding `item`. |
| `$if="expr"` | Instantiate only when `expr` is truthy. |
| `$match` · `$when="expr"` · `$else` | Multi-way choice: on a container, its direct children are arms; the first `$when` that is truthy wins, `$else` is the fallback. |
| `$with="expr as name"` | Bind `expr` to `name` in scope for the children. |
| `$value="expr"` · `$html="expr"` | Set the content to escaped text, or to sanitized HTML. |
| `$where` `$sort` `$limit` `$key` | Iteration modifiers on `$each`. |

> [!note] Structural directives survive HTML parsing
> An attribute on a context-valid element survives HTML parsing, and a group can use a `<template>`, which is valid everywhere and preserves its direct children (a `<tr>` stays a `<tr>`). A hyphenless wrapper such as `<for>` or `<match>` is instead foster-parented out of a `<table>` and dropped in a `<select>` (verified against the reference parser). Angular's structural directives `*ngIf`/`*ngFor` follow the same element-level approach.[^7] The `$` marks the attribute as a directive and stays clear of the native `for`/`as` attributes a bare name would shadow.

## Inline text expressions

Authored template text inserts a value with `{expression}`. Every insertion has explicit opening and closing braces, including a simple path such as `{$user.name}`. Each expression uses the same scope, reactive dependencies, escaped-text conversion, absent-value behavior, and invalid-result retention as `$value`. Surrounding text and elements are preserved, with no wrapper element. For a sole read, `<td>{$r.name}</td>` and `<td $value="$r.name"></td>` have the same observable output.

```html
<table><tbody>
  <tr $each="r of $rows" $key="$r.id"><td>{$r.name}</td></tr>
</tbody></table>

<p>Total: {$cart.total} due today</p>
<p>Hello, {$user.name}!</p>
<p>Download: {$file.name}.txt</p>
<p>Price: $1.15. The text $ident stays literal.</p>
```

Outside braces, `$` is ordinary text: `$ident`, `$HOME`, and `$1.15` do not read values and need no escape. In authored text, `\{` emits a literal opening brace and `\\` emits a literal backslash; other backslashes remain literal, including `\$`. These are text escapes, not identifier escapes. `$value` and `$html` continue to own their element's content when present.

## $if: single guard

`$if="expr"` instantiates the element (or a `<template>`'s content) only when `expr` is truthy. While `expr` stays truthy the element and everything inside it stay as they are: a change to what `expr` reads updates the bindings inside, and creates nothing again. A test that turns falsy removes the element; one that turns truthy again creates it afresh (see [What counts as a change](/declarative-components/reactivity#changes)). It is a **single guard with no else**; multi-way branching is `$match`. The single-guard / multi-way split follows XSLT's `xsl:if` versus `xsl:choose`, rather than an imperative `if`/`else if`/`else`.[^1]

```html
<p $if="$cart.items.length">You have items in your cart.</p>

<!-- guard several siblings at once via a <template> -->
<template $if="$cart.items.length">
  <h2>Your cart</h2>
  <ul>…</ul>
</template>
```

> [!note] Negation stays in the expression grammar
> The expression language's `not` operator handles a negative condition directly: `$if="not $cart.items.length"`. A separate `$unless` directive would duplicate that operation; Liquid and Twig are examples of template languages that provide both.[^4]

## $each: iteration

`$each="item of $items"` instantiates once per element of `items`, binding `item` in a fresh scope layer (with an optional index, `$each="item, i of $items"`). The value uses the `for…of` grammar, one bounded, familiar form, not a packed micro-syntax. Iteration *shaping* is expressed as sibling `$` modifiers, following XSLT's `xsl:sort` living inside `xsl:for-each` rather than a value pipeline.[^1]

`$sort` takes a comma-separated list of keys, each optionally prefixed with `-` for descending, so `$sort="p.price,-p.name"` orders by price ascending then name descending, the convention JSON:API's `sort` parameter[^2] and Django's `order_by`[^3] use. Each key is a path from the loop item, not an expression: it starts with the item's name, so `p.price` reads the item's `price` and `p` alone sorts by the item itself. A bare field such as `price` is an error, because it could not be told apart from the item when a field shares the item's name. A leading `$` is accepted even though it is not required.

```html
<li $each="p of $products"
    $where="$p.inStock" $sort="p.price,-p.name" $limit="10" $key="$p.id">
  {$p.name}
</li>

<!-- index alias, when needed -->
<li $each="p, i of $products">…</li>
```

> [!note] Iteration control is declarative
> `$where` selects the items that participate and `$limit` bounds how many are instantiated. These operations cover the declarative roles of `continue` and an early `break`. A bare `$if` on the same element guards the whole iteration rather than each pass.

## $match / $when / $else: multi-way choice

A multi-way decision is a container carrying `$match` whose **direct children are arms**: each child with `$when="expr"` is a conditional arm, the first truthy one wins, and a child with `$else` is the terminal fallback. The winning arm stays as it is while it keeps winning; when another arm wins, the old arm is removed and the new one created. On a `<template>` the container itself renders nothing (only the winning arm does); on a real element the element wraps the winner.

```html
<template $match>
  <progress $when="$order.pending">Placing order…</progress>
  <output   $when="$order.error">{$order.error.message}</output>
  <p        $else>Thanks for your order.</p>
</template>
```

### Optional scope

`$match="expr as name"` binds a subject value once for every arm, the way `$with` does, using the same `as` grammar. Bare `$match` rebases nothing.

```html
<!-- optional scope: bind the subject once, for every arm -->
<template $match="$account.plan as plan">
  <span $when="$plan.tier = 'pro'">{$plan.seats} seats</span>
  <span $else>Free plan</span>
</template>
```

### Multi-way among rows and options

Because the arms are direct children of the `<template>`, not wrapped in a `<when>` element, a `<tr>` or `<option>` arm keeps its table/select context and survives, the case the old element form could not express.

```html
<!-- multi-way among rows: arms are direct <template> children, so they survive -->
<table><tbody>
  <template $match>
    <tr $when="$row.error" class="err"><td>{$row.message}</td></tr>
    <tr $else><td>{$row.name}</td></tr>
  </template>
</tbody></table>
```

> [!note] Conformance
> Every direct child of a `$match` container [must]{.kw} carry `$when` or `$else`. A `$else` must be the last such child; a compiler rejects a second `$else` or any arm after it. This is XSLT's `xsl:choose`/`xsl:when`/`xsl:otherwise` unit,[^1] as a directive family, and a near-exact twin of Angular `@switch`/`@case`/`@default`.[^8]

## $with: scope alias

Introducing a value under a name is a separate, *visible* operation. `$with="expr as name"` binds `expr` to `name` for the element's children (use it on a `<template>` for a wrapper-free scope). A new value updates what reads `name` in place; the children are not created again. It takes an explicit **alias** rather than spreading the value's members as bare names: spreading reproduces the JavaScript `with` statement's ambiguity about where a name resolves, and defeats static scope analysis (see [Scope & name resolution](/declarative-components/expressions)).

```html
<section $with="$account.owner as owner">
  <p>{$owner.name}</p>   <!-- owner is in scope here -->
</section>
```

## Output: inline text, $value, and $html

Authored text evaluates expressions only inside `{expression}`. `$value="expr"` sets an element's whole text content, and `<template $value="expr">` places wrapper-free text among siblings. All text forms share the same expression scope, reactivity, absence behavior, invalid-value retention, and escaping. Formatting uses `format()` in any expression (see [Expressions](/declarative-components/expressions#formatting-intl-expressions)).

```html
<td>{$user.name}</td>
<p>Hello {$user.name}, welcome.</p>
<p>Total: {format($cart.total, 'currency', { currency: 'USD' })}</p>
<output $value="format($cart.total, 'currency', { currency: 'USD' })"></output>
<article $html="$post.body"></article>
```

### Expression boundaries and errors

A single opening brace starts an expression; its matching closing brace ends it. String literals and nested object braces are part of the expression and do not terminate it. All ordinary expression syntax is available, including computed indexes, conditionals, and fixed function calls. Empty, malformed, or unterminated expressions and undeclared roots are conformance errors. These author errors follow the same diagnostic and compile-time rejection policy as `$value` (see [expression fault tolerance](/declarative-components/expressions#fallback-for-absence)); braces never request a literal-text fallback. Write `\{` for a literal opening brace. Interpolation applies to authored template text, not attributes, styles, plain projected content, returned strings, or dynamic HTML.

```html
<p>{format($amount, 'currency', { currency: $currency }, $locale)}</p>
<p>{default($items[$selected].name, 'Unknown')}</p>
<p>Literal: \{format($amount)} and $amount</p>
```

Mixed literal text and expression segments retain one native text node per authored text node. Each segment retains its own last accepted value when a typed read or built-in operation becomes invalid; a segment with no accepted value remains empty. An absent or `null` result clears the segment, as it does for `$value`. Adjacent markup and text-node identity survive updates and hydration.

> [!norm] Aligned with the HTML Sanitizer API
> `$html="expr"` renders markup, but **does not raw-inject** it. The string is parsed as an inert HTML fragment in a `<template>` context, then filtered with one versioned copy of the **HTML Sanitizer API's safe-default policy**[^5] before insertion. The filter drops `<script>`, inline `on*` handlers, and `javascript:` URLs. Browsers and servers must use the same policy.
>
> `$html` must **not** call native `Element.setHTML()`, even when it exists. Firefox currently reorders malformed table content differently from Chromium, WebKit, and the reference HTML parser. Using native `setHTML()` would make the result depend on the browser and could break server-rendered hydration. It remains useful for comparing sanitizer policies, not for rendering `$html`.
>
> The result renders markup but cannot execute code, the same script-free guarantee a `<template component>` import receives. Raw, *unsanitized* HTML is not available here; it requires the dedicated trusted-HTML type (see [Types](/declarative-components/types)), the only path that can carry script and therefore the only one gated.

## Whitespace & mixed content

HTML Next does **not** transform the whitespace an author writes. A template is HTML, so its whitespace is **HTML whitespace**: the parser preserves the text nodes, and runs of spaces, tabs, and newlines collapse at **render time through CSS** (`white-space`)[^6], exactly as they do in a hand-written `.html` file. There is no condensing pass, no whitespace flag, and nothing to learn: indent your source however reads best, and CSS collapses it the same way it always has. To keep whitespace, reach for CSS (`white-space: pre`, `<pre>`); to space things out, reach for CSS (`gap`, margins), never for whitespace-as-layout.

```html
<!-- Whitespace is HTML's. The space around the value is significant and stays. -->
<p>Total: {$cart.total} due today</p>

<!-- Indentation and line breaks are preserved as text nodes, then collapse at
     RENDER through CSS white-space — exactly as in a hand-written .html file,
     not through a template build step. -->
<ul>
  <li $each="t of $tags">{$t}</li>
</ul>

<!-- Opt out the way any HTML page does: with CSS, not a template flag. -->
<pre style="white-space: pre">  spaces and newlines, kept  </pre>

<!-- $value / $html own the element's whole content: authored children
     alongside them are a conformance error, never a silent merge. -->
<p $value="$user.name">welcome</p>   <!-- ✗ text child + $value -->
```

Text expressions, elements, and `<template $value>` interleave as ordinary **mixed content**. The space in `Total: {$cart.total}` is significant and is preserved; `$each` emits the whitespace inside and around it like any repeated markup, with no join or separator behaviour of its own. The one hard rule is the content-owning directives: `$value` and `$html` set an element's *entire* content, so authored children beside them are a **conformance error** rather than a silent merge, the same constraint a content-replacing property binding carries.

> [!note] Coming from a framework
> This will surprise anyone migrating from React, Vue, or Svelte, which **condense** whitespace in a build step (collapsing runs, dropping whitespace-only nodes between elements). HTML Next does not, for one reason: **it is not a framework, it is a standard.** A framework owns its own runtime and may rewrite your markup on the way to it; HTML Next lowers to the *real* native DOM, and the browser already defines what template whitespace means. Condensing would make the same markup produce a different DOM through HTML Next than as plain HTML, and it would stop being HTML.
>
> **What this means in practice, and how to adapt:**
>
> - The **rendered result is identical** to the condensed frameworks under normal `white-space`. The only difference is that insignificant whitespace-only text nodes remain in the DOM; they never affect layout.
> - Use CSS for spacing (`gap`, margins) instead of relying on markup whitespace being stripped, the platform-first habit that is good practice in plain HTML anyway.
> - If a test asserts on exact `childNodes` or untrimmed `textContent`, assert on the **rendered output** or trimmed text instead. Whitespace-only nodes are not part of the contract (see below).

> [!norm] What observable equivalence covers
> Every conforming target, polyfill and converter alike, must agree on the **rendered result and all significant text**. It is *not* defined on the identity of insignificant whitespace-only text nodes: a converter targeting React, Vue, or Svelte may let its host condense them, because CSS collapses both forms to the same pixels. That carve-out is what lets HTML Next stay HTML-native (the polyfill deletes nothing the parser created) while its framework targets keep behaving as their authors expect.

## Parser contexts

Because control flow is entirely `$` **attributes**, it survives every parser context, including the restrictive ones (`<table>`, `<select>`, SVG/MathML) where a hyphenless element would be foster-parented out or dropped. A group of siblings rides a `<template>`, which is valid everywhere and parses its contents permissively.

```html
<!-- every $ directive is an attribute, so it survives every parser context -->
<table><tbody>
  <tr $each="r of $rows" $key="$r.id"><td>{$r.name}</td></tr>
</tbody></table>

<select>
  <option $each="o of $opts" from:value="$o.id">{$o.label}</option>
</select>

<!-- a fragment (several siblings) rides a <template> -->
<table><tbody>
  <template $each="r of $rows">
    <tr class="head"><td>{$r.title}</td></tr>
    <tr class="body"><td>{$r.detail}</td></tr>
  </template>
</tbody></table>
```

> [!note] Context-safe formatting
> Inline text expressions and `$value` attributes preserve their native parser context, so formatted output works in cells and options without a special output element.

## Future exploration: transitions

> [!future] Optional extension · outside Level 1
> Structural directives could animate the markup they add, remove, and reorder. The browser already does the animating: the View Transitions API[^9] takes a picture of the page before and after a DOM change and animates between the two, including an element that exists on only one side. What it lacks is a declarative way in. Today an author wraps the change in `document.startViewTransition()`, gives each element a unique `view-transition-name`, and styles the `::view-transition-old()` and `::view-transition-new()` pseudo-elements. This extension would let a template say which elements take part and how they move, and leave the rest to the runtime.
>
> ```html
> <aside $if="$open" $transition="fly 200ms ease-out">…</aside>
>
> <li $each="todo of $todos" $key="$todo.id" $transition="fade">{$todo.title}</li>
>
> <img $each="photo of $photos" $key="$photo.id" $transition-name="$photo.id">
> <img $if="$selected" class="hero" $transition-name="$selected.id">
> ```
>
> The panel flies in and out. Each todo fades in and out, and glides to its new place when the list reorders. When a photo is selected, its thumbnail grows into the hero image.
>
> **`$transition`** says how an element animates when a structural directive adds or removes it, or when it moves. The value is a literal in the form of the CSS `animation` shorthand[^10]: a keyframes name, then an optional duration, easing, and delay. It is not an expression, so, like `$sort`, it can never take references. The name is a built-in (`fade`, `fly`, `scale`, `blur`) or any `@keyframes` in the component's `<style>`. Keyframes describe *arriving*; leaving plays them in reverse. With no value, the element uses the browser's default crossfade.
>
> ```html
> <p $if="$saved" $transition="pop 150ms">Saved</p>
>
> <style>
>   @keyframes pop { from { scale: .5; opacity: 0; } }
> </style>
> ```
>
> **`$transition-name="expr"`** is the element's identity across the change, as `view-transition-name` is in CSS. It is an expression: `$photo.id` reads a value, and a bare word such as `hero` is a keyword (see [Expressions](/declarative-components/expressions)). When one element leaves and another with the same name arrives in the same update, the browser moves and resizes the first into the second. The runtime would turn any value into a valid CSS identifier. Names are page-wide, which is what lets a grid and a detail view in different components pair up. An element with only `$transition` gets a unique generated name.
>
> An element with either directive *participates*. The runtime would:
>
> - run an update inside a view transition only when a structural directive inserts, removes, or reorders a participating element, using `Element.startViewTransition()`[^11] on the nearest container where it is supported and `document.startViewTransition()` otherwise; every other update stays as it is;
> - keep the rest of the page out of the transition, so it stays live and clickable;
> - play each element's keyframes on its picture, forwards when it arrives and reversed when it leaves, and apply its timing to the browser's own move;
> - skip the animation when the user prefers reduced motion.
>
> Authors can still write `::view-transition-*` rules; the extension removes the requirement, not the option.
>
> **Why pictures instead of delayed removal.** Svelte and Vue keep a leaving node in the DOM until its animation ends. Here the DOM always holds the true state: a removed `$if` branch is gone at once, so refs, keyed rows, focus, and form submission never see a node on its way out. A framework target only has to wrap its state update, rather than map onto that framework's own transition component. CSS alone cannot cover removal: `@starting-style`[^12] animates an element's arrival, but nothing animates an element leaving the DOM.
>
> **Still open.**
>
> - A second document-level view transition skips the first, so closing and reopening quickly jumps instead of reversing. Element-scoped transitions, which can run side by side, are in Chromium only.
> - An animated update reaches the DOM one frame later, after the browser captures the old state.
> - When a sibling leaves, content that does not participate moves to its new position at once; it glides only if it participates too.
> - A leaving picture can draw outside an `overflow` container until element-scoped transitions are widely available.
> - Two elements on screen with the same name abort the transition.
> - A framework target can wrap the component's own state writes, but a parent's prop change re-renders the child before the old state can be captured.
> - Naming: `$transition` versus `$view-transition`, the platform's own term. Separate enter and leave animations wait until a use needs them.

## Reference

::: {.entry name="$each" role="iteration directive"}
Value
: the for-of grammar: `item of items`, or `item, i of items`

Modifiers
: `$where`, `$sort` (`p.a,-p.b`), `$limit`, `$key`

Scope
: binds the alias (and index) in a lexical layer; `loop.index/first/last/count`

Level
: [L1]{.pill .l1}
:::

::: {.entry name="$if" role="guard directive"}
Value
: `expr`; the element/template instantiates only when truthy

Semantics
: single guard, no else; multi-way is `$match`

Level
: [L1]{.pill .l1}
:::

::: {.entry name="$match · $when · $else" role="multi-way choice"}
Value
: `$match` optional `expr as name` scope · `$when="expr"` arm · `$else` fallback

Semantics
: direct children of the $match container are arms; first truthy $when wins; $else terminal and last

Prior art
: XSLT `xsl:choose`/`xsl:when`/`xsl:otherwise`

Level
: [L1]{.pill .l1}
:::

::: {.entry name="$with" role="scope alias directive"}
Value
: `expr as name`; binds one alias for the children, never spreads

Semantics
: the alias is a lexical layer that shadows outer names

Level
: [L1]{.pill .l1}
:::

::: {.entry name="$value · $html" role="output directives"}
Value
: `expr`; `$value` escaped text, `$html` sanitized HTML (script stripped)

Semantics
: set the content; raw unsanitized HTML needs the trusted-HTML type

Level
: [L1]{.pill .l1}
:::

::: {.entry name="{expression}" role="inline escaped text"}
Value
: Any checked expression inside matching braces

Semantics
: Reads the current lexical scope; escaped text; each segment retains its last accepted value on invalid input

Formatting
: `format()` chooses an explicit Intl formatter or infers the default from the declared type

Escapes
: `\{` for a literal opening brace, `\\` for a literal backslash; dollars are ordinary text outside expressions

Level
: [L1]{.pill .l1}
:::

## References

[^1]: W3C, [XSL Transformations (XSLT) 3.0](https://www.w3.org/TR/xslt-30/) (`xsl:if`, `xsl:choose`/`when`/`otherwise`, `xsl:sort`).
[^2]: JSON:API, [sorting](https://jsonapi.org/format/#fetching-sorting) (the `sort=a,-b` convention).
[^3]: Django, [QuerySet.order_by](https://docs.djangoproject.com/en/stable/ref/models/querysets/#order-by) (the same `-`-prefix descending convention).
[^4]: Shopify [Liquid](https://shopify.github.io/liquid/tags/control-flow/) and [Twig](https://twig.symfony.com/doc/3.x/tags/if.html) (the `unless` tag HTML Next omits).
[^5]: WHATWG HTML, [the HTML Sanitizer API](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#the-sanitizer-api) (the safe-default policy on which `$html` is based).
[^6]: W3C, [CSS Text Module Level 3](https://www.w3.org/TR/css-text-3/#white-space-processing) (the white-space processing and collapsing model HTML Next defers to at render).
[^7]: Angular [structural directives](https://angular.dev/guide/directives/structural-directives) (`*ngIf`/`*ngFor`): control flow expressed as a directive on the context-valid element rather than a wrapper element, the same parser-survival property argued here. Contrast: Svelte [`{#if}`](https://svelte.dev/docs/svelte/if)/`{#each}` and Solid [`Show`](https://docs.solidjs.com/reference/components/show)/`For` are wrapper or block forms that do not survive `<table>`/`<select>` foster-parenting.
[^8]: Angular [`@switch`/`@case`/`@default`](https://angular.dev/guide/templates/control-flow) blocks: a near-exact twin of `$match`/`$when`/`$else`, alongside the XSLT `xsl:choose` unit.
[^9]: W3C, [CSS View Transitions Module Level 1](https://www.w3.org/TR/css-view-transitions-1/) (`startViewTransition()`, [`view-transition-name`](https://www.w3.org/TR/css-view-transitions-1/#view-transition-name-prop), and the `::view-transition-*` pseudo-elements).
[^10]: W3C, [CSS Animations Level 1](https://www.w3.org/TR/css-animations-1/#animation) (the `animation` shorthand).
[^11]: Chrome for Developers, [element-scoped view transitions](https://developer.chrome.com/docs/css-ui/view-transitions/element-scoped-view-transitions) (`Element.startViewTransition()`, which runs transitions side by side and keeps the rest of the page interactive).
[^12]: W3C, [CSS Transitions Level 2](https://www.w3.org/TR/css-transitions-2/#defining-before-change-style) (`@starting-style`).
