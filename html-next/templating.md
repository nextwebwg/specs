---
title: Templating
order: 1
blurb: $each · $if · $match · $with · value
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reserved direction · reference implementation pending
---

# Templating

Control flow is a family of **marked directives on ordinary elements**: `$each`, `$if`, `$match`, `$with`, `$value`. A leading `$` marks a *structural* directive, it controls whether, how many times, or in what scope markup is produced, distinct from the `:` binding family that sets values. There are **no control-flow elements**: every directive rides on any element or a `<template>`, so it survives every parser context, and none appears in the output.

## Structural directives

A structural directive is a `$`-prefixed attribute. It goes on the element it applies to, or on a `<template>` to apply to a group of siblings. The `$` is deliberate: bindings (`:x`, `bind:x`, `on:x`) set or wire *values*; a `$` directive changes *whether, how many times, or in what scope* markup is produced. At lowering the directive is evaluated and **removed**, so it never appears in the output (rendered DOM, compiled component, or serialized HTML alike), which is why its attribute name is free to be a directive.

```html
<li $each="p of products">…</li>          <!-- iterate this element -->
<p  $if="cart.items.length">…</p>          <!-- guard this element -->
<td $value="user.name"></td>               <!-- escaped text content -->

<!-- multi-way and scope are directives too, on an element or a <template> -->
<template $match>
  <p $when="a">…</p>
  <p $else>…</p>
</template>
```

| Directive | Effect |
| --- | --- |
| `$each="item of items"` | Instantiate once per element of `items`, binding `item`. |
| `$if="expr"` | Instantiate only when `expr` is truthy. |
| `$match` · `$when="expr"` · `$else` | Multi-way choice: on a container, its direct children are arms; the first `$when` that is truthy wins, `$else` is the fallback. |
| `$with="expr as name"` | Bind `expr` to `name` in scope for the children. |
| `$value="expr"` · `$html="expr"` | Set the content to escaped text, or to sanitized HTML. |
| `$where` `$sort` `$limit` `$key` | Iteration modifiers on `$each`. |

> [!note] Structural directives survive HTML parsing
> An attribute on a context-valid element survives HTML parsing, and a group can use a `<template>`, which is valid everywhere and preserves its direct children (a `<tr>` stays a `<tr>`). A hyphenless wrapper such as `<for>` or `<match>` is instead foster-parented out of a `<table>` and dropped in a `<select>` (verified against the reference parser). Angular's structural directives `*ngIf`/`*ngFor` follow the same element-level approach.[^7] The `$` marks the attribute as a directive and stays clear of the native `for`/`as` attributes a bare name would shadow.

## $if: single guard

`$if="expr"` instantiates the element (or a `<template>`'s content) only when `expr` is truthy. It is a **single guard with no else**; multi-way branching is `$match`. The single-guard / multi-way split follows XSLT's `xsl:if` versus `xsl:choose`, rather than an imperative `if`/`else if`/`else`.[^1]

```html
<p $if="cart.items.length">You have items in your cart.</p>

<!-- guard several siblings at once via a <template> -->
<template $if="cart.items.length">
  <h2>Your cart</h2>
  <ul>…</ul>
</template>
```

> [!note] Negation stays in the expression grammar
> The expression language's `not` operator handles a negative condition directly: `$if="not cart.items.length"`. A separate `$unless` directive would duplicate that operation; Liquid and Twig are examples of template languages that provide both.[^4]

## $each: iteration

`$each="item of items"` instantiates once per element of `items`, binding `item` in a fresh scope layer (with an optional index, `$each="item, i of items"`). The value uses the `for…of` grammar, one bounded, familiar form, not a packed micro-syntax. Iteration *shaping* is expressed as sibling `$` modifiers, following XSLT's `xsl:sort` living inside `xsl:for-each` rather than a value pipeline.[^1]

`$sort` takes a comma-separated list of keys, each optionally prefixed with `-` for descending, so `$sort="p.price,-p.name"` orders by price ascending then name descending, the convention JSON:API's `sort` parameter[^2] and Django's `order_by`[^3] use.

```html
<li $each="p of products"
    $where="p.inStock" $sort="p.price,-p.name" $limit="10" $key="p.id">
  <value of="p.name"></value>
</li>

<!-- index alias, when needed -->
<li $each="p, i of products">…</li>
```

> [!note] Iteration control is declarative
> `$where` selects the items that participate and `$limit` bounds how many are instantiated. These operations cover the declarative roles of `continue` and an early `break`. A bare `$if` on the same element guards the whole iteration rather than each pass.

## $match / $when / $else: multi-way choice

A multi-way decision is a container carrying `$match` whose **direct children are arms**: each child with `$when="expr"` is a conditional arm, the first truthy one wins, and a child with `$else` is the terminal fallback. On a `<template>` the container itself renders nothing (only the winning arm does); on a real element the element wraps the winner.

```html
<template $match>
  <progress $when="order.pending">Placing order…</progress>
  <output   $when="order.error"><value of="order.error.message"></value></output>
  <p        $else>Thanks for your order.</p>
</template>
```

### Optional scope

`$match="expr as name"` binds a subject value once for every arm, the way `$with` does, using the same `as` grammar. Bare `$match` rebases nothing.

```html
<!-- optional scope: bind the subject once, for every arm -->
<template $match="account.plan as plan">
  <span $when="plan.tier = 'pro'"><value of="plan.seats"></value> seats</span>
  <span $else>Free plan</span>
</template>
```

### Multi-way among rows and options

Because the arms are direct children of the `<template>`, not wrapped in a `<when>` element, a `<tr>` or `<option>` arm keeps its table/select context and survives, the case the old element form could not express.

```html
<!-- multi-way among rows: arms are direct <template> children, so they survive -->
<table><tbody>
  <template $match>
    <tr $when="row.error" class="err"><td $value="row.message"></td></tr>
    <tr $else><td $value="row.name"></td></tr>
  </template>
</tbody></table>
```

> [!note] Conformance
> Every direct child of a `$match` container [must]{.kw} carry `$when` or `$else`. A `$else` must be the last such child; a compiler rejects a second `$else` or any arm after it. This is XSLT's `xsl:choose`/`xsl:when`/`xsl:otherwise` unit,[^1] as a directive family, and a near-exact twin of Angular `@switch`/`@case`/`@default`.[^8]

## $with: scope alias

Introducing a value under a name is a separate, *visible* operation. `$with="expr as name"` binds `expr` to `name` for the element's children (use it on a `<template>` for a wrapper-free scope). It takes an explicit **alias** rather than spreading the value's members as bare names: spreading reproduces the JavaScript `with` statement's ambiguity about where a name resolves, and defeats static scope analysis (see [Scope & name resolution](/html-next/expressions)).

```html
<section $with="account.owner as owner">
  <p><value of="owner.name"></value></p>   <!-- owner is in scope here -->
</section>
```

## Output: $value, $html, and <value>

Plain dynamic text is a directive: `$value="expr"` sets an element's whole text content, and `<template $value="expr">` places wrapper-free text inline among other content. The `<value>` element is kept for the one case a directive serves poorly, **locale-formatted** output, where the Intl options (`format`, `currency`, `datestyle`, …) need an attribute surface (see [Expressions](/html-next/expressions)). None use `{{…}}` interpolation, and all three **escape by default**: the expression becomes text, so a `<b>` in the data renders as literal characters.

```html
<!-- plain escaped text: on the element, or wrapper-free with a <template> -->
<td $value="user.name"></td>
<p>Hello <template $value="user.name"></template>, welcome.</p>

<!-- locale-formatted output keeps the <value> element and its Intl attributes -->
<p>Total: <value of="cart.total" format="currency" currency="USD"></value></p>

<!-- markup: sanitized (parsed; <script>, on* handlers, javascript: URLs stripped) -->
<article $html="post.body"></article>
```

> [!norm] Aligned with the HTML Sanitizer API
> For markup, `$html="expr"` is the bypass, and it **does not raw-inject**: it is defined in terms of the platform's **HTML Sanitizer API**[^5]. The string is parsed and run through the sanitizer's safe default configuration, dropping `<script>`, inline `on*` handlers, and `javascript:` URLs, matching `Element.setHTML()`. It reuses the **platform's** sanitizer rather than inventing a bespoke blocklist, and the reference library ships a lazy-loaded **polyfill of the Sanitizer API** where the browser does not yet provide it, so behavior tracks the standard and evolves with it. The result renders markup but cannot execute code, the same script-free guarantee a `<template component>` import receives. Raw, *unsanitized* HTML is not available here; it requires the dedicated trusted-HTML type (see [Types](/html-next/types)), the only path that can carry script and therefore the only one gated.

## Whitespace & mixed content

HTML Next does **not** transform the whitespace an author writes. A template is HTML, so its whitespace is **HTML whitespace**: the parser preserves the text nodes, and runs of spaces, tabs, and newlines collapse at **render time through CSS** (`white-space`)[^6], exactly as they do in a hand-written `.html` file. There is no condensing pass, no whitespace flag, and nothing to learn: indent your source however reads best, and CSS collapses it the same way it always has. To keep whitespace, reach for CSS (`white-space: pre`, `<pre>`); to space things out, reach for CSS (`gap`, margins), never for whitespace-as-layout.

```html
<!-- Whitespace is HTML's. The space around the value is significant and stays. -->
<p>Total: <value of="cart.total"></value> due today</p>

<!-- Indentation and line breaks are preserved as text nodes, then collapse at
     RENDER through CSS white-space — exactly as in a hand-written .html file,
     not through a template build step. -->
<ul>
  <li $each="t of tags"><value of="t"></value></li>
</ul>

<!-- Opt out the way any HTML page does: with CSS, not a template flag. -->
<pre style="white-space: pre">  spaces and newlines, kept  </pre>

<!-- $value / $html own the element's whole content: authored children
     alongside them are a conformance error, never a silent merge. -->
<p $value="user.name">welcome</p>   <!-- ✗ text child + $value -->
```

Text, elements, `<value>`, and `<template $value>` interleave as ordinary **mixed content**. The space in `Total: <value…>` is significant and is preserved; `$each` emits the whitespace inside and around it like any repeated markup, with no join or separator behaviour of its own. The one hard rule is the content-owning directives: `$value` and `$html` set an element's *entire* content, so authored children beside them are a **conformance error** rather than a silent merge, the same constraint a content-replacing property binding carries.

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
  <tr $each="r of rows" $key="r.id"><td $value="r.name"></td></tr>
</tbody></table>

<select>
  <option $each="o of opts" :value="o.id" $value="o.label"></option>
</select>

<!-- a fragment (several siblings) rides a <template> -->
<table><tbody>
  <template $each="r of rows">
    <tr class="head"><td $value="r.title"></td></tr>
    <tr class="body"><td $value="r.detail"></td></tr>
  </template>
</tbody></table>
```

> [!note] The one remaining element
> The only templating *element* is `<value>` (locale-formatted output), and it is subject to the ordinary rules: fine inline in flow content, dropped directly in a `<select>`. Prefer `$value` on a cell or option, where formatting is not needed. See the empirical findings in `browser-findings.md`.

## Reference

::: {.entry name="$each" role="iteration directive"}
Value
: the for-of grammar: `item of items`, or `item, i of items`

Modifiers
: `$where`, `$sort` (`a,-b`), `$limit`, `$key`

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

::: {.entry name="<value>" role="formatted output (the one element)"}
Attributes
: `of`: expression; `format` and its Intl options.

Semantics
: Locale-formatted, escaped text; explicit end tag required. Plain text uses `$value` or `<template $value>`.

Level
: [L1]{.pill .l1}
:::

## References

[^1]: W3C, [XSL Transformations (XSLT) 3.0](https://www.w3.org/TR/xslt-30/) (`xsl:if`, `xsl:choose`/`when`/`otherwise`, `xsl:sort`).
[^2]: JSON:API, [sorting](https://jsonapi.org/format/#fetching-sorting) (the `sort=a,-b` convention).
[^3]: Django, [QuerySet.order_by](https://docs.djangoproject.com/en/stable/ref/models/querysets/#order-by) (the same `-`-prefix descending convention).
[^4]: Shopify [Liquid](https://shopify.github.io/liquid/tags/control-flow/) and [Twig](https://twig.symfony.com/doc/3.x/tags/if.html) (the `unless` tag HTML Next omits).
[^5]: WHATWG HTML, [the HTML Sanitizer API](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#dom-element-sethtml) (parse-and-sanitize, the basis for `$html`).
[^6]: W3C, [CSS Text Module Level 3](https://www.w3.org/TR/css-text-3/#white-space-processing) (the white-space processing and collapsing model HTML Next defers to at render).
[^7]: Angular [structural directives](https://angular.dev/guide/directives/structural-directives) (`*ngIf`/`*ngFor`): control flow expressed as a directive on the context-valid element rather than a wrapper element, the same parser-survival property argued here. Contrast: Svelte [`{#if}`](https://svelte.dev/docs/svelte/if)/`{#each}` and Solid [`Show`](https://docs.solidjs.com/reference/components/show)/`For` are wrapper or block forms that do not survive `<table>`/`<select>` foster-parenting.
[^8]: Angular [`@switch`/`@case`/`@default`](https://angular.dev/guide/templates/control-flow) blocks: a near-exact twin of `$match`/`$when`/`$else`, alongside the XSLT `xsl:choose` unit.
