---
title: Expressions & Formatting
order: 2
blurb: grammar · operators · Intl formatting
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reserved direction
---

# Expressions & Formatting

Declarative HTML Components uses a small expression language for live values and conditions. It can read declared values, calculate with them, and choose a fallback without running JavaScript from an HTML attribute. Formatting is an expression operation, so the same formatted string can appear in template text, bindings, handler steps, and computed values.

## The expression language

Expressions appear in bindings (`from:x`, `bind:x`), handler steps (`expr:value`), structural directives, and inline text expressions (`{expression}`). A handler evaluates `expr:value` only when that step runs; `from:x` and `<computed from>` keep their dependencies live. Every root identifier [must]{.kw} resolve through the template's declared binding scope: props, state, computed values, data, imports, loop locals. Ambient JavaScript globals are not in scope. The browser evaluates a parsed tree; ahead-of-time targets compile the same tree. No `eval()`, no `new Function()`. The closest mainstream precedent is Angular template expressions, a restricted, AOT-compiled, non-`eval` subset; Alpine.js and Lit are the contrast, interpolating real JavaScript and inheriting the CSP hazard this avoids.[^9]

```html
<!-- Expressions look like this: plain reads, comparisons, and arithmetic. -->
<p $if="$user.isAdmin">…</p>                        <!-- a boolean guard -->
<progress from:value="$cart.items.length"></progress>  <!-- a bound value -->
{($price - $discount) * 1.08}     <!-- arithmetic, no filters -->
```

::: two

> [!ex] Included
> literals, reads & safe indexed access, comparisons, boolean and arithmetic operators, conditional selection (`test ? yes : no`), parentheses, and the [fixed functions below](#functions).

> [!warn] Excluded by construction
> assignment, mutation, statements, a filter pipeline (`|`), arbitrary function/method calls, constructors, lambdas, dynamic evaluation, and access to `window`/`document`/network.

:::

## Scope & name resolution

A bare identifier resolves through the template's declared scope, never an ambient JavaScript global, and an identifier that resolves to nothing is a **conformance error**. Scope has two parts.

### Identifier spelling and case

Expression identifiers are **case-sensitive**. A reference in an expression or through the JavaScript interface [must]{.kw} use the declaration's exact spelling: `$count` and `$Count` read different names. Public props [must not]{.kw} differ only in ASCII casing, because the HTML parser lowercases attribute names; `<prop name="count">` and `<prop name="Count">` cannot both be declared. Other scope names retain their case-sensitive identity.

An identifier starts with a CSS Syntax **ident-start code point** and continues with ident-start code points or ASCII digits.[^18] This reuses CSS's defined character repertoire, including `_` and permitted non-ASCII characters, but **not** CSS identifier tokenization: dashes are not allowed at any position, and names have no escape sequences. `$` is a reference marker, never part of a name. Thus `_name`, `first_name`, `firstName`, and `name2` are identifiers; `-name`, `--name`, `first-name`, `$name`, and `1name` are not identifier spellings. `$first-$name` is subtraction between two references. External keys outside this grammar remain accessible through a quoted bracket key, such as `$record['first-name']`.

### The component layer is flat, and collisions are errors

A component's own declarations, `<prop>`, `<state>`, `<computed>`, `<data>`, and `<context>`, share **one flat namespace**. Each uses its `name`, except `<context>` uses `as` when supplied. Two declarations introducing the same local name are a **conformance error**, not a silent precedence: the author disambiguates rather than memorizing which kind wins. Each `<data>` is named, so datasets are referenced individually (`search.value`, `orders.pending`). A context name reads the provider's state with the same type and reactive behavior, but is read-only in this scope (see [Reactivity](/declarative-components/reactivity)).

### Inner layers are lexical, and they shadow

`$each`, `$with`, `$match`, and scoped slots each **push a lexical layer** whose names are statically known. A bare identifier resolves in the nearest enclosing layer, walking outward to the component layer, so an inner layer *shadows* an outer one, because that is local and expected: a loop's `item` may shadow an outer `item`. Cross-layer shadowing is allowed; a collision *within* the flat component layer is not.

| Element | Adds to scope |
| --- | --- |
| `$each="item, i of $items"` | `item`, `i`, and `loop` (`.index`/`.first`/`.last`/`.count`) |
| `$with="expr as owner"` | `owner`, a single alias, never a spread |
| `$match="expr as plan"` | `plan`, one alias, available to every arm |
| scoped `<slot>` | the slot's declared props (e.g. `item`, `index`) |

> [!note] $with binds one explicit alias
> An explicit `as` binds one name whose members are reached with a dot, so every scope layer stays fixed and statically known. The reactive graph and type-checker can therefore resolve the whole scope. Spreading an object's members as bare names would make their origin ambiguous and their availability depend on a runtime shape.

## Grammar

```text
expr      := conditional                        (* no pipeline: there is no "|" filter *)
conditional := or ("?" expr ":" conditional)?    (* lowest precedence; associates right *)
or        := and ("or" and)*
and       := eq ("and" eq)*
eq        := cmp (("=" | "!=" | "^=" | "$=" | "*=") cmp)*
cmp       := add (("<" | "<=" | ">" | ">=") add)*
add       := mul (("+" | "-") mul)*
mul       := unary (("*" | "/" | "%") unary)*
unary     := ("not" | "-") unary | access
access    := primary (("." id) | ("." integer) | ("[" expr "]"))*
primary   := literal | dimension | reference | id | call | "(" expr ")" | object | array
reference := "$" id
id        := ident-start (ident-start | digit)*  (* CSS ident-start; no dashes or escapes *)
dimension := css-number css-unit | css-number "%" (* units from Types; no whitespace *)
integer   := digit+
call      := fn "(" (expr ("," expr)*)? ")"    (* fixed, typed, CSS-style — not arbitrary calls *)
fn        := "round" | "clamp" | "min" | "max" | "abs" | "default" | "concat" | "join" | "format" | "formatRange" | "formatParts"
object    := "{" (pair ("," pair)* ","?)? "}"
pair      := (id | string) ":" expr
array     := "[" (expr ("," expr)* ","?)? "]"
```

`css-number` is a finite CSS number token; `css-unit` is a unit accepted by `length` or `duration` in [Types](/declarative-components/types). A numeric token immediately followed by a known unit or `%` forms one dimensional literal before the parser considers the `%` remainder operator. Thus `25%` is a percentage; `25 % 4` is remainder. Unary `-` negates a number or dimensional literal, so `-2rem` is a length. Binary operators follow the [typed arithmetic rules](#arithmetic-with-units) below. Conventional precedence with parentheses applies. Equality, missing data, truthiness, and coercion are specified explicitly (see **Value semantics**, next) rather than inherited from JavaScript or any template language.

A `$`-prefixed name reads a declared value. A literal list index can be dotted or bracketed: `$items.0.name` and `$items[0].name` both read the first item's `name` and have the dependency path `items.0.name`, without the expression's `$` reference marker. Directly written integer keys retain their exact spelling in either form, so `$byId.9007199254740993` and `$byId[9007199254740993]` read the same object key without rounding it. Brackets also accept a computed key, such as `$items[$index]`, or a quoted object key that cannot be written as a dot segment.

`test ? yes : no` tests the same truthiness as `$if`, evaluates only the selected branch, and returns that branch's value without coercion. It is for a small inline value choice, such as `from:aria-current="$activeStep = $index ? 'step' : null"`; use `$match` when whole markup differs. All three branches participate in static name and dependency checks.

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

Reading a property that is not present at runtime, `order.error.message` when `error` is null, yields a single first-class **absent value** rather than an error, and further access on it is absent too, safe navigation everywhere. The absent value behaves consistently in every position: it renders as **empty text**, reads as **false** in a condition, and **removes the attribute** in `from:attr` position, exactly the serialization already defined for `null`/`undefined` (see [Bindings](/declarative-components/bindings)). It also **propagates**: any operation with an absent operand is itself absent, the way an invalid value invalidates a whole CSS declaration[^7] and a SQL `NULL` propagates through an expression.

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
| object | `{}` | any object with an own key |

*Empty* values are false: no characters, no count, no items. This makes ordinary guards work without a length check: `$if="$cart.items"` hides on `[]`, and `$if="$unread.count"` hides on `0`. `and`, `or`, and `not` return a **boolean** rather than one of their operands. Fallback for absence is explicit (below), never a side effect of `or`.

### Equality is typed; operators never coerce

Comparison is **typed**. Two values of different types are not equal, and comparing operands whose types are statically known to be disjoint, a `number` against a string literal, is a **conformance error**, a caught bug rather than a silent `false`. Where a type mismatch can only be known at runtime, the result is simply `false`; it never throws.

Arithmetic follows the operand types. `+` is *not* overloaded for string concatenation, so `"1" + 1` can never silently become `"11"`. An incompatible combination is a type error where it is statically known, and absent otherwise. Operators never coerce across types. Conversion happens at **typed edges**: a `number` prop converts its incoming string once, on the way in, the way `<input>` exposes both `value` and `valueAsNumber`, never mid-expression. The [rules for dimensions](#arithmetic-with-units) give each valid operation a result type.

`concat(value, …)` is an explicit conversion edge for constructing a string. One argument converts an accepted scalar value to text; further arguments append their text in order. It does not bypass a declaration's type check. Its arguments and errors are defined under [Functions](#functions).

### Fallback for absence

Because `or` returns a boolean, fallback has an explicit form. `default($user.name, 'friend')` uses `'friend'` when the value is absent or `null`; it preserves `false`, `0`, and `''`. The fallback is evaluated only when needed. This resembles CSS `var(--x, fallback)`[^7] and Jinja's undefined-only `default`[^10], with `null` included because an omitted optional prop resolves to `null`. `{default($user.name, 'friend')}` inserts that fallback result in text with the same absent-or-`null` trigger. A whole-markup choice among several states is a `$match`; a small value choice can use `? :`.

> [!norm] Fault tolerance is a platform requirement
> A conforming **runtime**, the polyfill or a future native implementation, [must not]{.kw} throw on a data condition: absent data yields the absent value and rendering continues, exactly as the HTML parser[^8] recovers from malformed markup rather than aborting the page. Anything less violates the platform. A **compiler** [may]{.kw} reject author mistakes, undeclared names, disjoint-type comparisons, incompatible arithmetic, at build time as static analysis, the way a validator or a type checker does; but this is optional, and every construct a compiler could reject still has a defined runtime behaviour (absent, empty, or logged), so a permissive implementation stays conformant. Diagnostics are recommended; compile-time rejection is optional; runtime throwing is forbidden.

## Object & array expressions

The grammar includes **object** and **array** expressions for structured values. They resemble JSON and a JS object but are **neither**: an object expression is a production of this pure, typed language, evaluated deterministically with no `eval()`, whose values are ordinary expressions from this same grammar, not arbitrary JavaScript. In shape they are simply `{ [key: string]: Expression }` and `[...Expression]`, so they **nest recursively**: any value may itself be another object or array expression.

```html
<state name="draft" type="object({ title: string, tags: list(string), done: boolean })"
       value="{ title: '', tags: [], done: false }">

<x-list rows="[{ id: 1, name: 'Ada' }, { id: 2, name: 'Lin' }]">

<!-- A computed object can read another declaration. -->
<computed name="filter" from="{ status: $currentStatus, limit: 10 }">
```

A declared structured prop or state can parse a fixed object or array from a plain attribute, as `rows` and `draft` do above. A `from:` binding or `<computed from>` evaluates an expression and updates when the values it reads change. A plain `value` attribute accepts literal contents.

Two rules keep them unambiguous, and both reuse positions defined elsewhere rather than inventing new ones:

- a **key** is *attribute-position*: a bare identifier and a quoted string are the same string key, so `{ open: … }` equals `{ 'open': … }`;
- a **value inside an expression** may be a reference or a literal: `{ label: $name }` reads `name`, while `{ label: name }` contains the literal keyword `name`. A plain typed attribute, including `<state value>`, accepts only literal values.

> [!note] Object expressions are the authoring syntax
> **JSON** is the *wire* format: it mandates double quotes because it is for machines. A **JS object** literal would imply arbitrary JavaScript. An **object expression** is the *authoring* form, lighter than JSON (bare keys, single-quoted strings, trailing commas) and safer than JS (pure, typed, no calls). Structured values are authored as object expressions and serialized to JSON only when they cross a boundary (see [Types](/declarative-components/types)).

## Functions

Functions cover operations that an operator or an existing HTML/CSS feature does not express clearly. Their names are fixed; a component cannot register a callable function in an attribute. A call has no side effects and reads the same reactive dependencies as its arguments.

```html
<computed name="snapped" from="round($width, 1px)"></computed>
<computed name="shown" from="default($count, 0)"></computed>
{format(($price - $discount) * 1.08, 'currency', { currency: 'USD' })}
```

| Function | Example → result | Accepted inputs and result | Prior art |
| --- | --- | --- | --- |
| `round(value[, step])` | `round(8.8px)` → `9px` | Round to the nearest multiple of `step`. If omitted, the step is `1` for a number or one unit of the written value for a length, percentage, or duration. A supplied dimensional step must use the value's written unit. A numeric result is `number`; a dimensional result keeps its dimension type.[^6] | CSS `round()` strategy; this proposal also defaults dimensional steps[^6] |
| `min(a, …)` / `max(a, …)` | `max(2px, 5px)` → `5px` | At least one argument; return the smallest/largest value. Arguments must be numbers, or dimensional quantities with the same written unit. A numeric result is `number`; a dimensional result keeps its dimension type.[^6] | CSS `min()` / `max()`[^6] |
| `clamp(minimum, value, maximum)` | `clamp(0, $volume, 100)` | Return `max(minimum, min(value, maximum))`. The minimum wins when the bounds conflict. Dimensional arguments must share one written unit.[^6] | CSS `clamp()`[^6] |
| `abs(value)` | `abs(-2rem)` → `2rem` | Return a number's or a dimensional quantity's magnitude. A numeric result is `number`; a dimensional result keeps its dimension type.[^6] | CSS `abs()`[^6] |
| `default(value, fallback)` | `default($count, 0)` | Return the fallback only for absent or `null`; otherwise return the original value. It does not replace `0`, `false`, `''`, or an empty list.[^7][^10] | CSS `var()` fallback; Jinja `default`[^7][^10] |
| `concat(value, …)` | `concat($progress, '%')` → `'40%'` | Convert one accepted scalar to text, or join several in order; return a string. This is text assembly, not locale formatting.[^11] | XPath `concat()`[^11] |
| `join(list, separator)` | `join($tags, ', ')` → `'red, blue'` | Convert a list of accepted scalar items to text, placing the string separator between items; return a string.[^16] | XPath `string-join()`; Liquid and Twig `join`[^16] |

`round` uses CSS's default *nearest* strategy: an exact halfway case goes toward positive infinity. Thus `round(2.5)` is `3` and `round(-2.5)` is `-2`. An omitted step rounds the numeric part of a dimensional value to a whole number in its current unit: `round(8.8px)` is `9px`, `round(25.5%)` is `26%`, and `round(1.6s)` is `2s`. `round(1600ms)` remains `1600ms`: the function rounds the value as written. CSS requires an explicit step for dimensions; this proposal makes it optional.[^6] A supplied step must use the same written unit, so `round(8.8px, 1px)` is valid and `round(8.8px, 1rem)` is invalid. A negative step has the same multiples as its positive magnitude; a step of zero has no result. Other CSS rounding strategies (`up`, `down`, `to-zero`) are not included in this level; adding them later will use CSS's leading strategy argument rather than changing the meaning of these calls.[^6]

### Values with units

The `length`, `percentage`, and `duration` types are strings at the JavaScript boundary, but they are **typed quantities** while an expression calculates with them. A literal such as `8.8px`, `25%`, or `200ms` has that type. A reference declared as one of those types supplies its accepted numeric part and written unit to a calculation. The result crosses back to a prop, state, or DOM binding in the [type's written form](/declarative-components/types), such as `9px`; it is not exposed as a JavaScript number. The HTML clock-time type `time` is not a CSS duration.

For a function with more than one dimensional argument, every argument must have the same type **and the same written unit**. `min(1px, 2px)` and `min(1rem, 2rem)` work; `min(1in, 100px)` and `max(200ms, 0.5s)` are invalid, even though CSS defines conversion ratios for those units.[^12] The functions do not convert units or silently choose an output unit. `abs` has one argument, so `abs(-2rem)` simply returns `2rem`. Percentages compare with percentages, never with lengths. Calculations that need unit conversion or layout and font context belong in a [controller](/declarative-components/javascript); CSS math remains available in CSS properties where that context exists.

```html
<state name="width" type="length" value="8.8px"></state>
<computed name="snappedWidth" from="round($width, 1px)"></computed>
<!-- snappedWidth has type length and written value 9px. -->

<computed name="safeWidth" from="max($width, 1rem)"></computed>
<!-- If width is in px, no comparison is made: the written units differ. -->
```

Unitless `0` is a number, so `round(8px, 0)` is a type error; use `0px` (which then fails as a zero step). The five math functions return `number` for numeric inputs, including `integer` inputs; an `integer` destination checks whether the result is whole at its typed edge.

### Arithmetic with units

An `integer` or a fractional `number` is unitless. The result type follows the operands, then the destination checks whether that result is allowed. Each dimensional result retains its operand's **written unit**. CSS math's type checking is prior art, but these rules use only calculations that need no unit conversion.[^17]

| Operation | Valid operands | Result | Example |
| --- | --- | --- | --- |
| `+`, `-` | Two numbers, or two dimensions of the same type **and written unit** | `number`, or that dimension | `1px + 2px` → `3px` |
| `*` | Two numbers, or one dimension and one number in either order | `number`, or that dimension | `2.5 * 100px` → `250px` |
| `/` | Two numbers, or a dimension divided by a number | `number`, or that dimension | `100px / 100` → `1px` |
| `%` | Two numbers | `number` | `5 % 2` → `1` |

`1px + 1` and `1px + 1ms` are invalid because their types differ. `1px + 1rem` is invalid because the written units differ. Multiplying two dimensions, dividing a number by a dimension, and dividing one dimension by another are not defined here, even when the written units match. A zero divisor or non-finite result from dimensional arithmetic is invalid. A compiler rejects a statically known invalid combination. At runtime, an invalid calculation does not write its destination: the destination keeps its last accepted value, or its default/`null` before any successful write, as described under [invalid reactive results](/declarative-components/reactivity#invalid-reactive-results). An absent operand still produces absence, with its ordinary empty/removal behavior. An `integer` destination accepts a result only when it is whole.

```html
<state name="width" type="length" value="100px"></state>
<computed name="quarterWidth" from="$width / 4"></computed>
<computed name="paddedWidth" from="$quarterWidth + 2px"></computed>
<!-- quarterWidth is 25px; paddedWidth is 27px. -->
```

If `width` then changes to `100rem`, `quarterWidth` becomes `25rem`, but `paddedWidth` keeps `27px`: adding `25rem` and `2px` is invalid. When `width` changes back to `120px`, `paddedWidth` updates to `32px`.

### Fallback and text assembly

`default` is lazy: it evaluates `value` first, and evaluates `fallback` only if that result is absent or `null`. Both arms must have the same declared type, or satisfy the same expected destination type; it does not create a mixed-type union. A present but invalid typed reference is **not** absence and cannot be rescued by `default`; the invalid result follows the [live-binding rule](/declarative-components/reactivity): the destination keeps its last accepted value, or its default/`null` if it has never accepted one. The function does not use truthiness.

`concat` requires at least one argument. Each must be a scalar (`string`, `keyword`, `boolean`, `integer`, `number`, or a serialized scalar type such as `length`). It uses that type's normal attribute text: for example `concat(true)` returns `'true'` and `concat(8px)` returns `'8px'`. A value keeps its normal type checks until it reaches this explicit text conversion. Missing data propagates as absent; `null` contributes an empty string. Lists and objects are not `concat` arguments. Locale-sensitive number, date, currency, and list presentation uses the [Intl formatting functions](#formatting-intl-expressions) below. XPath supplies the function's name and ordered concatenation, but Declarative Components also permits one argument so the same function can replace `format('%s', value)` without another conversion function.[^11]

`join` requires exactly two arguments: a list and a string separator. The list may be empty and must have one scalar item type, as described in [Types](/declarative-components/types#lists-and-their-written-forms). Items use the same text conversion as `concat`; a `null` item contributes an empty string, but still occupies its position between separators. An empty list returns `''`, and a one-item list returns that item's text without a separator. An absent list, separator, or item propagates as absent. An object item or a separator of another type makes the call invalid. For example, `join(['red', null, 'blue'], ', ')` returns `'red, , blue'`, while `join([], ', ')` returns `''`. This function assembles an attribute or computed string; `format($items, 'list')` is the locale-sensitive way to present a list to readers.[^16]

### Invalid calls and live bindings

Wrong argument counts, incompatible types or units, a zero rounding step, and a non-finite numeric result make the call invalid. A compiler reports a statically knowable mistake. The browser runtime reports an authored-definition mistake once, but does not throw or warn for an ordinary user edit that makes an input invalid. At runtime an invalid call does not write a bound destination: it keeps the last accepted result, or the declared default/`null` if no result was accepted. This is the same sequence as any other invalid live expression; it does not replace the destination with a string containing the invalid input.[^13]

| Expression | Result |
| --- | --- |
| `round(8.8px, 1px)` | `9px` (`length`) |
| `round(8.8px)` | `9px` (`length`; omitted step is `1px`) |
| `round(25.5%)` | `26%` (`percentage`; omitted step is `1%`) |
| `round(-2.5)` | `-2` (`number`) |
| `min(1px, 2px)` | `1px` (`length`) |
| `max(200ms, 500ms)` | `500ms` (`duration`) |
| `abs(-2rem)` | `2rem` (`length`) |
| `abs(-3)` | `3` (`number`) |
| `default(null, 0)` / `default(false, true)` | `0` / `false` |
| `concat(40, '%')` | `'40%'` (`string`) |
| `concat(true)` | `'true'` (`string`) |
| `join(['red', 'blue'], ', ')` | `'red, blue'` (`string`) |
| `join([], ', ')` | `''` (`string`) |
| `min(1in, 100px)` | invalid because units differ; no destination write |
| `max(200ms, 0.5s)` | invalid because units differ; no destination write |
| `round(8.8px, 1rem)` | invalid because units differ; no destination write |
| `round(8px, 0px)` | invalid zero step; no destination write |
| `concat()` | invalid argument count; no destination write |
| `join(['red'], 1)` | invalid separator type; no destination write |

```html
<prop name="amount" type="number" default="5"></prop>
<computed name="bounded" from="clamp(0, $amount, 10)"></computed>
<!-- amount 2 → bounded 2; then invalid input "oops" → bounded stays 2. -->
<!-- If the first input is invalid, amount and bounded begin from default 5. -->
```

### Why this set

The admission test for a built-in is concrete: it must express a recurring typed operation that an operator, element, or CSS property does not already express at that use site; it must be pure; and both the browser interpreter and compiled targets must be able to give it the same result. `round($width, 1px)` passes because a computed length may feed a prop or attribute, not just a CSS property. `concat($progress, '%')` passes because `+` is numeric-only and a live attribute may need a string. `join($tags, ', ')` assembles a list for an attribute with a chosen separator. Locale presentation uses `format()` below, so it works in computed values and bindings as well as displayed text.

Template languages show a need for transformations but disagree on what a broad library should contain. Liquid and Twig supply dozens of filters, including arithmetic and formatting; Jinja supplies a configurable filter library. Angular pipes cover locale formatting and arbitrary presentation transformations, while Vue 3 removed its template filters.[^14] Handlebars and Mustache show a smaller expression surface but rely on helpers or lambdas for custom work.[^15] Declarative Components places the recurring jobs where its existing syntax already puts them:

| Need | Existing place |
| --- | --- |
| Arithmetic and comparisons | Operators; `min`, `max`, `clamp`, `round`, `abs` for math that needs a name |
| Missing-value fallback | `default()` in any expression |
| Attribute text assembled from typed values | `concat()` |
| List items assembled with a chosen separator | `join()` |
| Locale presentation | `format()` and the globalization standard |
| Uppercase or truncation for display | CSS `text-transform`, `text-overflow`, or `line-clamp` |
| Sort, filter, or limit repeated items | `$sort`, `$where`, `$limit` on `$each` |
| Split, replace, regex, or application-specific computation | Component JavaScript and the reactive graph, not a callable template library |

`join()` uses an author-chosen separator; `format($names, 'list')` assembles a list using locale rules. Both return strings for any expression destination. Space- and comma-separated typed attributes also have their own written forms, so they do not need `join` just to parse a list.

This keeps the browser interpreter and generated Vue/React expressions deterministic. It also avoids silently choosing a different fallback rule from Liquid or Twig, both of which replace some present false or empty values.[^10]

## Formatting: Intl expressions

Locale-aware formatting is a fixed expression operation backed by the Intl formatters.[^4] It returns escaped text when used in template output, and the same result can feed an attribute, prop, handler step, or computed value. Options use the native **case-sensitive camelCase names**, such as `currencyDisplay`, `timeStyle`, and `maximumFractionDigits`.

```text
format(value, options?, locale?)
format(value, formatter, options?, locale?)
formatRange(start, end, options?, locale?)
formatRange(start, end, formatter, options?, locale?)
formatParts(value, options?, locale?)
formatParts(value, formatter, options?, locale?)
```

An object in the options position selects inferred formatting; a string in the formatter position selects an explicit formatter. To supply only a locale override, write an empty options object: `format($amount, {}, 'fr-CA')`. A locale is a BCP 47 language tag, with an optional region, and may itself be an expression. Omission uses the execution environment's default locale. Currency and time zone remain independent options. SSR must receive the same explicit locale and, for instants, time-zone options as the browser when identical initial text is required; a server cannot infer the browser's preferences.

### Explicit formatters

| Formatter | Native facility | Options and input |
| --- | --- | --- |
| `number` | `Intl.NumberFormat` | Decimal numbers; precision, grouping, signs, `notation` (`standard`, `compact`, `scientific`, `engineering`); native `style` may select currency, percent, or units |
| `currency` | `Intl.NumberFormat` | Number; required `currency`, optional `currencyDisplay`, `currencySign`, precision; selects `style: 'currency'` |
| `percent` | `Intl.NumberFormat` | Numeric ratio; selects `style: 'percent'`; `0.15` displays as 15% |
| `unit` | `Intl.NumberFormat` | Number; required `unit`, optional `unitDisplay`; selects `style: 'unit'`; labels the supplied magnitude without converting it |
| `date` | `Intl.DateTimeFormat` | Calendar date or instant; `dateStyle` or date fields; default medium date |
| `time` | `Intl.DateTimeFormat` | Clock time or instant; `timeStyle` or time fields; default medium time |
| `dateTime` | `Intl.DateTimeFormat` | Date and time; `dateStyle`, `timeStyle`, `timeZone`, calendar and field options; default medium date and time |
| `relativeTime` | `Intl.RelativeTimeFormat` | Signed numeric offset; required `unit`, optional `numeric` and `style`; no implicit read of the current clock |
| `duration` | `Intl.DurationFormat` | Duration record, or a typed CSS duration; `style` (`long`, `short`, `narrow`, `digital`), unit-display options, `fractionalDigits` |
| `list` | `Intl.ListFormat` | List of strings; `type` (`conjunction`, `disjunction`, `unit`), `style` (`long`, `short`, `narrow`) |
| `displayName` | `Intl.DisplayNames` | String code; required `type` (`language`, `region`, `script`, `currency`, `calendar`, `dateTimeField`), optional `style` and `fallback` |
| `plural` | `Intl.PluralRules` plus message selection | Number; `type` (`cardinal`, `ordinal`), precision options, and required `forms` record described below |

The explicit numeric presets set the native `style`; a conflicting authored `style` is invalid. Other options are delegated to the selected native constructor, including its defaults, accepted combinations, and treatment of unknown option names. HTML Next does not add a second options schema or rename the native options.

```html
<p>Total: {format($cart.total, 'currency', { currency: 'USD' })}</p>
<p>Published: {format($publishedAt, 'date', { dateStyle: 'long' })}</p>
<p>Updated: {format($minutesAgo, 'relativeTime', { unit: 'minute' })}</p>
<p>Guests: {format($names, 'list', { type: 'conjunction' }, $locale)}</p>
<output>{format($elapsed, 'duration', { style: 'digital' })}</output>
<computed name="priceLabel" from="format($price, 'currency', { currency: 'CAD' }, 'fr-CA')"></computed>
```

### Inference follows the declared type

Each supported type has one default formatter. Inference never parses an ordinary string to guess its meaning, and never guesses a formatter from option names. Constraints do not change the underlying formatting identity. Nullable unions ignore absence; other union members must agree on one identity. A selected type can infer only when all possible selections agree. An ordinary string, unknown value, or conflicting union requires an explicit formatter.

| Declared type | Inferred formatter |
| --- | --- |
| `number`, `integer` | `number` |
| `percentage` | `percent` |
| `date` | `date` |
| `time` | `time` |
| `datetime`, `datetime-local` | `dateTime` |
| `duration` | `duration` |
| List of strings or keywords | `list` |

Numeric expression literals and arithmetic also have their numeric or dimensional identity. Known string-list literals infer `list`. Typed nested paths and lexical aliases retain their declared identity. An untyped computed declaration needs an explicit formatter when its result's identity is unavailable at the use site.

```js
// These pairs are equivalent for the corresponding declared types.
format($clock, { timeStyle: 'long' })
format($clock, 'time', { timeStyle: 'long' })

format($amount, { style: 'currency', currency: 'USD' })
format($amount, 'currency', { currency: 'USD' })

// Generic options may be clearer with an explicit formatter.
format($names, 'list', { style: 'long' })
format($elapsed, 'duration', { style: 'long' })
```

Inference is a convenience, not a promise that every shorthand is readable without its declaration. Authors can always make intent visible with an explicit formatter.

### Typed values and native input

`date`, `time`, and `datetime-local` are civil values without a time zone. Formatting [must]{.kw} preserve their calendar and clock fields without shifting them to the machine's zone or inventing a zone label. The JavaScript adapter uses an internal UTC anchor and removes zone-name parts from long or full time styles. Explicit `timeZone` or `timeZoneName` options on those zone-free values are invalid. A `datetime` is an instant; it uses the selected native time zone. An explicit date/time formatter also accepts HTML date/time strings or numeric epoch milliseconds. A date-only input cannot supply clock fields, and a time-only input cannot supply calendar fields. Invalid dates [must not]{.kw} roll over into another calendar day.

A typed CSS percentage such as `15%` supplies the ratio `0.15` to number formatting. A typed CSS duration such as `1500ms` supplies a balanced hours/minutes/seconds/subseconds record; signs are preserved. A structured duration record passes its fields to Intl unchanged. These adapters preserve type meaning rather than treating every serialized value as an ordinary string.

### Plural messages

`plural` selects one of the CLDR categories `zero`, `one`, `two`, `few`, `many`, or `other` using `Intl.PluralRules`, then selects the corresponding string from `forms`. `other` is required and supplies the fallback. Every `#` in that selected string is replaced with the number formatted in the same locale and precision. This is a small message-selection operation layered on Intl, rather than an assertion that Intl itself interpolates messages.[^5]

```js
format($count, 'plural', { forms: { one: '# item', other: '# items' } })
format($position, 'plural', {
  type: 'ordinal',
  forms: { one: '#st', two: '#nd', few: '#rd', other: '#th' }
}, 'en')
```

### Ranges, parts, and invalid results

`formatRange()` uses native number or date/time range formatting. Both ends must be valid inputs for the selected formatter. `formatParts()` returns native structured parts for number, date/time, relative-time, list, or duration formatting, so markup can style individual pieces. It is not supported for display names or plural messages. Civil date/time parts omit invented zone names.

```html
<p>{formatRange($minimum, $maximum, 'currency', { currency: 'USD' })}</p>
<span $each="part of formatParts($price, 'currency', { currency: 'USD' })">{$part.value}</span>
```

Absence or null produces absence. An invalid input, formatter, argument count, native option combination, locale, or unsupported operation produces the existing invalid built-in result: no destination write, retaining the last accepted value. Formatted strings remain data, never a second round of HTML or template parsing. A JavaScript host without a selected Intl facility requires a conforming polyfill; an unavailable facility produces the same invalid result. Native locale data can vary across engine and ICU versions; the reference targets share the same adapter and preserve the selected platform semantics.

## Reactive dependencies

A parsed expression exposes exactly which paths it reads, so dependencies are statically known. `$subtotal`, `$discount`, and `$rate` in `($subtotal - $discount) * $rate` are all discoverable without runtime tracking: the browser subscribes to those paths, and each framework target translates them to its own reactive model. See [Reactivity](/declarative-components/reactivity).

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
[^10]: Jinja [default filter](https://jinja.palletsprojects.com/en/stable/templates/#jinja-filters.default) uses an undefined-only fallback unless explicitly told to include false values. Liquid [default](https://shopify.github.io/liquid/filters/default/) and Twig [default](https://twig.symfony.com/doc/3.x/filters/default.html) also replace some present false or empty values; Declarative Components does not.
[^11]: XPath and XQuery Functions and Operators 3.1 defines [string `concat()`](https://www.w3.org/TR/xpath-functions/#func-concat) for two or more atomic values. This proposal also permits one argument for explicit scalar-to-string conversion. Liquid's [different `concat` filter](https://shopify.github.io/liquid/filters/concat/) joins arrays; this proposal uses the XPath string meaning.
[^12]: CSS Values and Units Level 4 defines [absolute length ratios](https://www.w3.org/TR/css-values-4/#absolute-lengths), [relative lengths](https://www.w3.org/TR/css-values-4/#relative-lengths), [percentages](https://www.w3.org/TR/css-values-4/#percentages), and [time units](https://www.w3.org/TR/css-values-4/#time).
[^13]: [Reactivity](/declarative-components/reactivity) specifies that an invalid live expression leaves the destination at its last accepted value, or its initial default/`null`.
[^14]: [Liquid filters](https://shopify.github.io/liquid/filters/), [Twig filters](https://twig.symfony.com/doc/3.x/filters/index.html), [Jinja filters](https://jinja.palletsprojects.com/en/stable/templates/#list-of-builtin-filters), [Angular pipes](https://angular.dev/guide/templates/pipes), and the [Vue 3 filter removal](https://v3-migration.vuejs.org/breaking-changes/filters.html) show the range of template transformation designs.
[^15]: [Handlebars built-in helpers](https://handlebarsjs.com/guide/builtin-helpers.html) and [Mustache sections and lambdas](https://mustache.github.io/mustache.5.html) show smaller core syntax with extension points for custom behavior.
[^16]: XPath and XQuery Functions and Operators 3.1 defines [`string-join`](https://www.w3.org/TR/xpath-functions/#func-string-join); Twig [joins sequences](https://twig.symfony.com/doc/3.x/filters/join.html), and Liquid has a [join filter](https://shopify.github.io/liquid/filters/join/).
[^17]: CSS Values and Units Level 4, [math function type checking](https://drafts.csswg.org/css-values-4/#calc-type-checking), derives calculation types from operands. Declarative Components adopts only the operations listed above and does not convert written units.

[^18]: CSS Syntax Module Level 3, [ident-start code point](https://www.w3.org/TR/css-syntax-3/#ident-start-code-point). Only the character definition is reused; the leading-dash and escape rules of CSS identifier tokenization do not apply.
