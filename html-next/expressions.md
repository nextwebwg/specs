---
title: Expressions & Formatting
order: 2
blurb: grammar · operators · Intl formatting
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reserved direction
---

# Expressions & Formatting

A small, pure, typed expression language (**not JavaScript in a string**) plus standards-shaped value formatting. There is **no filter library**: formatting delegates to a globalization standard, visual transforms to CSS, arithmetic to operators, iteration shaping to `$each`, and data manipulation to the reactive graph.

## The expression language

Expressions appear in bindings (`:x`, `bind:x`), in language-element attributes (`test`, `of`, `each`), and in `<value of>`. Every root identifier [must]{.kw} resolve through the template's declared binding scope: props, state, computed values, data, imports, loop locals. Ambient JavaScript globals are not in scope. The browser evaluates a parsed tree; ahead-of-time targets compile the same tree. No `eval()`, no `new Function()`. The closest mainstream precedent is Angular template expressions, a restricted, AOT-compiled, non-`eval` subset; Alpine.js and Lit are the contrast, interpolating real JavaScript and inheriting the CSP hazard this avoids.[^9]

```html
<!-- Expressions look like this: plain reads, comparisons, and arithmetic. -->
<p $if="user.isAdmin">…</p>                        <!-- a boolean guard -->
<progress :value="cart.items.length"></progress>  <!-- a bound value -->
<value of="(price - discount) * 1.08"></value>     <!-- arithmetic, no filters -->
```

::: two

> [!ex] Included
> literals, reads & safe indexed access, comparisons, boolean and arithmetic operators, parentheses, and a **fixed set of typed functions** (CSS-style: `round`, `clamp`, `min`, `max`, `abs`).

> [!warn] Excluded by construction
> assignment, mutation, statements, a filter pipeline (`|`), arbitrary function/method calls, constructors, lambdas, dynamic evaluation, and access to `window`/`document`/network.

:::

## Scope & name resolution

A bare identifier resolves through the template's declared scope, never an ambient JavaScript global, and an identifier that resolves to nothing is a **conformance error**. Scope has two parts.

### The component layer is flat, and collisions are errors

A component's own declarations, `<prop>`, `<state>`, `<computed>`, and `<data>`, share **one flat namespace**, each introduced by its `name`. Two declaring the same name is a **conformance error**, not a silent precedence: the author disambiguates rather than memorizing which kind wins. Each `<data>` is named, so datasets are referenced individually (`search.value`, `orders.pending`).

### Inner layers are lexical, and they shadow

`$each`, `$with`, `$match`, and scoped slots each **push a lexical layer** whose names are statically known. A bare identifier resolves in the nearest enclosing layer, walking outward to the component layer, so an inner layer *shadows* an outer one, because that is local and expected: a loop's `item` may shadow an outer `item`. Cross-layer shadowing is allowed; a collision *within* the flat component layer is not.

| Element | Adds to scope |
| --- | --- |
| `$each="item, i of items"` | `item`, `i`, and `loop` (`.index`/`.first`/`.last`/`.count`) |
| `$with="expr as owner"` | `owner`, a single alias, never a spread |
| `$match="expr as plan"` | `plan`, one alias, available to every arm |
| scoped `<slot>` | the slot's declared props (e.g. `item`, `index`) |

> [!note] $with binds one explicit alias
> An explicit `as` binds one name whose members are reached with a dot, so every scope layer stays fixed and statically known. The reactive graph and type-checker can therefore resolve the whole scope. Spreading an object's members as bare names would make their origin ambiguous and their availability depend on a runtime shape.

## Grammar

```text
expr      := or                                 (* no pipeline: there is no "|" filter *)
or        := and ("or" and)*
and       := eq ("and" eq)*
eq        := cmp (("=" | "!=" | "^=" | "$=" | "*=") cmp)*
cmp       := add (("<" | "<=" | ">" | ">=") add)*
add       := mul (("+" | "-") mul)*
mul       := unary (("*" | "/" | "%") unary)*
unary     := ("not" | "-") unary | access
access    := primary (("." id) | ("[" expr "]"))*
primary   := literal | id | call | "(" expr ")" | object | array
call      := fn "(" (expr ("," expr)*)? ")"    (* fixed, typed, CSS-style — not arbitrary calls *)
fn        := "round" | "clamp" | "min" | "max" | "abs"
object    := "{" (pair ("," pair)* ","?)? "}"
pair      := (id | string) ":" expr
array     := "[" (expr ("," expr)* ","?)? "]"
```

Conventional precedence with parentheses. Equality, missing data, truthiness, and coercion are specified explicitly (see **Value semantics**, next) rather than inherited from JavaScript or any template language.

Equality and string matching are spelled the way **CSS attribute selectors** already spell them. The language is assignment-free, so a single `=` means *equal* with nothing to disambiguate it from, and the selector match family carries over directly:

| Operator | Prior art | Meaning |
| --- | --- | --- |
| `=` | CSS `[a=b]`[^1] | equal |
| `!=` | XPath, attribute selectors have no negation[^2] | not equal |
| `^=` | CSS `[a^=b]`[^1] | starts with |
| `$=` | CSS `[a$=b]`[^1] | ends with |
| `*=` | CSS `[a*=b]`[^1] | contains substring |
| `<` `<=` `>` `>=` | CSS range queries (`@media (width >= …)`)[^3] | ordered comparison |

## Value semantics

Equality, missing data, truthiness, and coercion are defined here explicitly, so nothing is inherited by accident from JavaScript or a template language. The whole model follows one platform instinct: **the platform does not throw**. CSS drops an invalid declaration and falls back; the HTML parser recovers from any malformed input. Absence is a value, not a crash.

### The absent value

Reading a property that is not present at runtime, `order.error.message` when `error` is null, yields a single first-class **absent value** rather than an error, and further access on it is absent too, safe navigation everywhere. The absent value behaves consistently in every position: it renders as **empty text**, reads as **false** in a condition, and **removes the attribute** in `:attr` position, exactly the serialization already defined for `null`/`undefined` (see [Bindings](/html-next/bindings)). It also **propagates**: any operation with an absent operand is itself absent, the way an invalid value invalidates a whole CSS declaration[^7] and a SQL `NULL` propagates through an expression.

> [!note] Absent is runtime; undeclared is an error
> The absent value covers *data* gaps, a field a fetch did not return. It is distinct from an *undeclared root identifier*, a name that resolves to nothing in the component scope: that is a typo or a reach for an ambient global, and it is a conformance error (see Scope & name resolution above), never silently absent. Structure is checked; data is tolerated.

### Truthiness: the empty value of each type is false

`$if`, `$when`, and `and`/`or`/`not` test truthiness by one rule, **the empty value of each type is false**, everything else true:

| Type | False (empty) | True |
| --- | --- | --- |
| boolean | `false` | `true` |
| absent | always | — |
| string | `""` | any non-empty |
| number | `0` | any non-zero |
| list | `[]` | any non-empty |
| object | — | any present value |

*Empty* values are false: no characters, no count, no items. This makes ordinary guards work without a length check: `$if="cart.items"` hides on `[]`, and `$if="unread.count"` hides on `0`. `and`, `or`, and `not` return a **boolean** rather than one of their operands. Fallback for absence is explicit (below), never a side effect of `or`.

### Equality is typed; operators never coerce

Comparison is **typed**. Two values of different types are not equal, and comparing operands whose types are statically known to be disjoint, a `number` against a string literal, is a **conformance error**, a caught bug rather than a silent `false`. Where a type mismatch can only be known at runtime, the result is simply `false`; it never throws.

Arithmetic is **numeric only**. `+` adds numbers; it is *not* overloaded for string concatenation, so `"1" + 1` can never silently become `"11"`. A non-numeric operand is a type error where that is statically known, and absent otherwise. There is no cross-type coercion anywhere: values are converted at **typed edges**, a `number` prop coerces its incoming string once, on the way in, the way `<input>` exposes both `value` and `valueAsNumber`, never mid-expression.

### Fallback for absence

Because `or` returns a boolean, and absence is not the same as empty, fallback has its own explicit form, the direct analog of CSS `var(--x, fallback)`[^7], which substitutes only when the variable is *missing*, not when it is `0`. For text, `<value>` carries a `default`: `<value of="user.name" default="friend">` shows the fallback only when `user.name` is absent. A presentation choice among several states is a `$match`, not an operator.

> [!norm] Fault tolerance is a platform requirement
> A conforming **runtime**, the polyfill or a future native implementation, [must not]{.kw} throw on a data condition: absent data yields the absent value and rendering continues, exactly as the HTML parser[^8] recovers from malformed markup rather than aborting the page. Anything less violates the platform. A **compiler** [may]{.kw} reject author mistakes, undeclared names, disjoint-type comparisons, non-numeric arithmetic, at build time as static analysis, the way a validator or a type checker does; but this is optional, and every construct a compiler could reject still has a defined runtime behaviour (absent, empty, or logged), so a permissive implementation stays conformant. Diagnostics are recommended; compile-time rejection is optional; runtime throwing is forbidden.

## Object & array expressions

The grammar includes literal **object** and **array** expressions for structured values, initializing state, passing structured data to a component. They resemble JSON and a JS object but are **neither**: an object expression is a production of this pure, typed language, evaluated deterministically with no `eval()`, whose values are ordinary expressions from this same grammar, not arbitrary JavaScript. In shape they are simply `{ [key: string]: Expression }` and `[...Expression]`, so they **nest recursively**: any value may itself be another object or array expression.

```html
<state name="draft" :value="{ title: '', tags: [], done: false }">

<x-list :rows="[{ id: 1, name: 'Ada' }, { id: 2, name: 'Lin' }]">

<!-- key is attribute-position (bare = string); value is expression-position -->
<state name="filter" :value="{ status: currentStatus, limit: 10 }">
```

Two rules keep them unambiguous, and both reuse positions defined elsewhere rather than inventing new ones:

- a **key** is *attribute-position*: a bare identifier and a quoted string are the same string key, so `{ open: … }` equals `{ 'open': … }`;
- a **value** is *expression-position*: a bare word is a reference and quotes make a string literal, so `{ label: name }` reads state `name` while `{ label: 'name' }` is the literal string.

> [!note] Object expressions are the authoring syntax
> **JSON** is the *wire* format: it mandates double quotes because it is for machines. A **JS object** literal would imply arbitrary JavaScript. An **object expression** is the *authoring* form, lighter than JSON (bare keys, single-quoted strings, trailing commas) and safer than JS (pure, typed, no calls). Structured values are authored as object expressions and serialized to JSON only when they cross a boundary (see [Types](/html-next/types)).

## Arithmetic operators

HTML Next writes arithmetic directly with operators. Template languages without operators often provide `plus`, `minus`, and `times` helpers for the same operations.

```html
<!-- filter-pipeline style -->   subtotal | minus: discount | times: 1.08
<!-- HTML Next -->                  <value of="(subtotal - discount) * 1.08" format="currency" currency="USD"></value>
```

A tiny set of numeric *shaping* functions that are not operators is drawn from CSS precedent (`calc`/`clamp`/`min`/`max`/`round`)[^6]: `round`, `clamp`, `min`, `max`, `abs`. Nothing more.

## Formatting: delegated to a globalization standard

Locale-aware presentation is the one transformation that genuinely earns first-class status: it is hard to do by hand, and the platform already standardized it. HTML Next exposes it as **typed attributes on `<value>`** (mirroring how `<time datetime>`, `<meter>`, and `<data value>` already carry typed value semantics), never a `| currency` pipe. The formatters bind to `Intl`[^4].

| format | Backed by (JS binding) | Key attributes |
| --- | --- | --- |
| `number` | `Intl.NumberFormat` | `notation`, `mindigits`, `maxdigits` |
| `currency` | `Intl.NumberFormat` | `currency` (ISO 4217), `currencydisplay` |
| `percent` | `Intl.NumberFormat` | `maxdigits` |
| `unit` | `Intl.NumberFormat` | `unit`, `unitdisplay` |
| `date` / `time` / `datetime` | `Intl.DateTimeFormat` | `datestyle`, `timestyle`, `timezone` |
| `relativetime` | `Intl.RelativeTimeFormat` | `unit`, `numeric` |
| `list` | `Intl.ListFormat` | `listtype` |
| `plural` | `Intl.PluralRules` + MessageFormat | `zero` `one` `two` `few` `many` `other` |

```html
<value of="price"       format="currency" currency="USD"></value>
<value of="ratio"       format="percent" maxdigits="1"></value>
<value of="publishedAt" format="date" datestyle="long"></value>
<value of="editedAgo"   format="relativetime" unit="minute"></value>
<value of="tags"        format="list" listtype="conjunction"></value>
```

### Plurals: CLDR categories

The plural attributes are the CLDR plural *categories*: `zero`, `one`, `two`, `few`, `many`, `other`. The runtime selects the category for the value in the active locale (English uses `one`/`other`; Arabic uses all six; Polish uses `few`/`many`/`other`), then substitutes `#` with the formatted number, following Unicode MessageFormat.

```html
<value of="count" format="plural" one="# item" other="# items"></value>
<!-- count = 1 → "1 item";  count = 5 → "5 items" -->
```

> [!note] CLDR and ICU define portable formatting
> Formatting semantics are specified against **Unicode CLDR/ICU** and MessageFormat[^5], not against `Intl` specifically. `Intl` is merely the JavaScript *binding*; a .NET target binds the same behavior through `System.Globalization` (which runs on ICU), a JVM target through ICU4J. So a C#/Razor or Java compile target formats identically without reinventing `Intl`.

## Transformation ownership

HTML Next routes each transformation to the part of the web platform that already owns it. This keeps presentation, globalization, arithmetic, collection shaping, and arbitrary computation in their respective languages and APIs:

| Transformation | Where it belongs in HTML Next |
| --- | --- |
| Uppercase / capitalize for display | CSS `text-transform` |
| Truncate / ellipsis | CSS `line-clamp` / `text-overflow` |
| Number / date / currency / plural | `<value format>` → globalization standard |
| Arithmetic & comparison | expression operators |
| Sort / filter / limit a list | `$sort` / `$where` / `$limit` on `$each` |
| Split / replace / map / regex | `<computed>`; arbitrary computation is the reserved JavaScript layer (a later Level) |

> [!note] Typed elements and functions transform values
> The platform transforms values through an element that carries a typed value (`<value>`, like `<time>`/`<meter>`) and a fixed set of named typed functions (like CSS `calc()`/`clamp()`). `<value default>` supplies fallback for missing data. This model does not add a `|` filter pipeline or a bespoke template mini-language.

## Reactive dependencies

A parsed expression exposes exactly which paths it reads, so dependencies are statically known. `subtotal`, `discount`, and `rate` in `(subtotal - discount) * rate` are all discoverable without runtime tracking: the browser subscribes to those paths, and each framework target translates them to its own reactive model. See [Reactivity](/html-next/reactivity).

## References

[^1]: CSS Selectors Level 4, [attribute selectors](https://www.w3.org/TR/selectors-4/#attribute-selectors) (`[a=b]`, `^=`, `$=`, `*=`).
[^2]: XPath, [XML Path Language 3.1](https://www.w3.org/TR/xpath-31/) (the `!=` inequality).
[^3]: CSS Media Queries Level 4, [range context](https://www.w3.org/TR/mediaqueries-4/#mq-range-context) (`< <= > >=`).
[^4]: ECMAScript Internationalization API, [ECMA-402](https://tc39.es/ecma402/) (the `Intl` formatters).
[^5]: Unicode LDML, [MessageFormat](https://www.unicode.org/reports/tr35/tr35-messageFormat.html); [CLDR](https://cldr.unicode.org/) plural categories.
[^6]: CSS Values and Units Level 4, [math functions](https://www.w3.org/TR/css-values-4/#math-function) (`calc`/`clamp`/`min`/`max`/`round`).
[^7]: CSS Custom Properties Level 1, [the guaranteed-invalid value](https://www.w3.org/TR/css-variables-1/#guaranteed-invalid-value) and [`var()` fallback](https://www.w3.org/TR/css-variables-1/#using-variables) (absence propagates; fallback triggers only on absence).
[^8]: WHATWG HTML, [parse errors and recovery](https://html.spec.whatwg.org/multipage/parsing.html#parse-errors) (the parser never aborts; the fault-tolerance model the runtime follows).
[^9]: Angular [template expressions](https://angular.dev/guide/templates/expression-syntax): a deliberately restricted, AOT-compiled, non-`eval` subset, the closest mainstream precedent to an expression language that is not JavaScript in a string. Contrast (do not inherit): Alpine.js [`x-data`](https://alpinejs.dev/directives/data) expressions and Lit [template expressions](https://lit.dev/docs/templates/expressions/) both interpolate real JavaScript, the CSP hazard HTML Next avoids.
