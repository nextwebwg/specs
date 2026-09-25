---
title: Type System
order: 7
blurb: web-native value & content types
eyebrow: Declarative HTML Components Level 1 · richer types in Level 3
status: Core types Level 1 · dimension types & lists Level 2 · content models & trusted content Level 3
---

# A web-native type system

HTML Next types are **wider than JavaScript's**; the web already has richer value domains than `string`/`number`/`boolean`, and the type system reuses them rather than inventing look-alikes. A type does two jobs at once: it **validates** an incoming value and tells a reader **how to parse the serialized string back**.

## Types are declared, and default to string

Every HTML attribute is already a string, so an **undeclared prop is a `string`**, no ceremony, and string-to-string round-trips for free. A `type` is opt-in: you declare one only to get something other than a string. This is the same line the platform already draws, an unregistered CSS custom property is the universal `*` syntax (any token stream) until `@property` gives it `syntax: "<length>"`.[^3][^7]

```html
<defs>
  <prop name="label">Any string (the default when no type is given).</prop>
  <prop name="count"   type="number">A parsed number.</prop>
  <prop name="loading" type="boolean">Presence means true.</prop>
  <prop name="replyTo" type="email" required>A syntactically valid email address.</prop>
  <prop name="variant" type="outline | solid | ghost" default="outline">A keyword set.</prop>
  <prop name="gap"     type="<length>">A CSS length: 8px, 1rem, 2ch.</prop>
  <prop name="accent"  type="<color>">A CSS color.</prop>
  <prop name="tags"    type="<string>#">A comma-separated list of strings.</prop>
  <prop name="rows"    type="array" required>Structured data, bound by reference (shape below).</prop>
</defs>
```

## The type-expression syntax

A `type` attribute is a grammar for one value. HTML Next adopts CSS's readable operators, but defines its own profile: it adds HTML-derived and structured types, does not import CSS property references or implicit CSS-wide keywords, and uses `required` to control whether the prop itself may be absent.

```html
<prop name="size" type="small | medium | large">
<prop name="inset" type="<length>{1,4}">
<prop name="stops" type="<color>#">
<prop name="placement" type="[ block-start | block-end ] && [ inline-start | inline-end ]?">
```

### Component forms

| Form | Meaning | Example |
| --- | --- | --- |
| `string` | An HTML Next built-in type. Built-in names are bare and reserved. | `type="number"` |
| `keyword` | A literal keyword. Following CSS and HTML enumerated attributes, matching is ASCII case-insensitive. A keyword that spells a built-in name is quoted, so it reads as the literal rather than the type. | `solid`, `'unknown'` |
| `<css-type>` | A named CSS value type parsed according to the specification that defines it. | `<length>`, `<color>` |
| `[ … ]` | A group. Brackets change precedence or let one multiplier apply to several components. | `[ <length> \| auto ]#` |

### Combinators

| Form | Meaning | Accepts |
| --- | --- | --- |
| juxtaposition | Every component, once, in the written order. | `<length> <color>` → `1rem red` |
| `&&` | Every component, once, in any order. | `inset && round` → either keyword order |
| `\|\|` | One or more components, once each, in any order. | `compact \|\| bordered` → either or both |
| `\|` | Exactly one alternative. | `small \| medium \| large` |

### Multipliers

| Suffix | Count and separator | Example |
| --- | --- | --- |
| `?` | Zero or one. | `<color>?` |
| `*` | Zero or more, space-separated. | `<length>*` |
| `+` | One or more, space-separated. | `<length>+` |
| `#` | One or more, comma-separated. | `<color>#` |
| `{A}`, `{A,B}`, `{A,}` | Exactly A, from A through B, or at least A, space-separated. | `<length>{1,4}` |
| `#{A,B}` | The same bounded count, comma-separated. | `<string>#{1,8}` |
| `!` | The group must produce at least one value, even when every component inside it is optional. | `[ <length>? <color>? ]!` |

### Precedence

From strongest to weakest: multipliers, juxtaposition, `&&`, `||`, then `|`. Thus `small | <length>+` means either the keyword `small` or a non-empty list of lengths. Brackets override that order. A parser must consume the entire value; an unmatched token makes the value invalid.

```text
type-expression = alternative
alternative     = options [ "|" options ]*
options         = any-order [ "||" any-order ]*
any-order       = sequence [ "&&" sequence ]*
sequence        = term+
term            = atom multiplier? | group [ multiplier | "!" ]
atom            = built-in | keyword | css-type
group           = "[" type-expression "]"
css-type        = "<" css-type-name ">"
multiplier      = "?" | "*" | "+" | "#" | range | "#" range
range           = "{" integer [ "," integer? ] "}"
```

### HTML Next profile

- **Level 1** includes the bare scalar types, literal keyword alternatives, and `|`.
- **Level 2** adds angle-bracketed CSS types, grouping, the remaining combinators, and all multipliers.
- `?` makes a component inside a composite value optional. It does not make the prop optional; absence is controlled by the `required` attribute.
- CSS property references such as `<'border-width'>` are excluded because a component prop is not a CSS property. CSS-wide keywords such as `inherit` are accepted only when written as explicit alternatives.
- A CSS type name is available only when this specification lists it. HTML Next uses that type's token grammar and value semantics, not the set of properties on which CSS happens to use it.
- A literal `default` must satisfy the declared type. A literal prop value that fails is a conformance error; a bound value that fails produces the validity result defined by the [Validation chapter](/html-next/validation).

The operators and their precedence come from CSS Value Definition Syntax.[^1][^6] The profile above is HTML Next's definition; referring to CSS does not add unlisted CSS grammar or types.

### CSS value types included by this level

Angle brackets select one of the CSS token grammars listed here. They do not mean “any CSS type,” and they do not turn the value into a CSS declaration. Parsing uses CSS tokenization, must consume the complete attribute value, and preserves the original serialization for reflection.

| Type | Accepted syntax and value |
| --- | --- |
| `<string>` | One CSS quoted string token. This differs from bare `string`, which accepts the complete HTML attribute string without CSS quotes. |
| `<custom-ident>` | A CSS custom identifier, excluding CSS-wide keywords, `default`, and any keyword reserved by the enclosing type expression. |
| `<length>` | A CSS length dimension or a permitted zero, resolved as a typed length rather than a number. |
| `<percentage>` | A CSS percentage token. |
| `<length-percentage>` | A value accepted by either `<length>` or `<percentage>`, including CSS calculations valid for that combined type. |
| `<angle>` | A CSS angle, including its unit or a permitted zero. |
| `<time>` | A CSS time dimension such as `200ms` or `1.5s`. This is unrelated to bare HTML `time`, which is a clock-time string. |
| `<resolution>` | A CSS resolution dimension such as `2dppx`. |
| `<color>` | Any value in the CSS Color `<color>` grammar, including named, functional, system, and current color values. |
| `<url>` | A CSS URL token or `url()` value. This differs from bare `url`, which is an HTML absolute-URL string and has no CSS wrapper. |

## HTML-native types and constraints

CSS does not define every useful web value. HTML already specifies parsers and intrinsic validity rules for email addresses, absolute URLs, numbers, and date/time strings. HTML Next exposes those as bare types and applies the same rules to component props and data values.[^15][^16][^17]

```html
<defs>
  <prop name="replyTo" type="email" required>
  <prop name="website" type="url">
  <prop name="starts" type="datetime-local" min="2026-01-01T00:00">
  <prop name="quantity" type="number" min="1" max="100" step="1">
  <prop name="handle" type="string" minlength="3" maxlength="32" pattern="[a-z0-9-]+">
</defs>
```

| Type | Accepted value | Applicable constraints |
| --- | --- | --- |
| `email` | An HTML-valid email address. Empty is allowed unless `required`; `multiple` permits HTML's comma-separated email list. | `required`, `multiple`, `pattern`, `minlength`, `maxlength` |
| `url` | An HTML-valid absolute URL. This is distinct from CSS `<url>`, which accepts CSS URL-token syntax. | `required`, `pattern`, `minlength`, `maxlength` |
| `date`, `month`, `week`, `time`, `datetime-local` | The corresponding HTML valid date or time string.[^18] | `required`, `min`, `max`, `step` |
| `number` | An HTML valid floating-point number, returned as a number rather than a string. | `required`, `min`, `max`, `step` |
| `integer` | A base-10 integer with no fractional part. | `required`, `min`, `max`, `step` |
| `string` | Any string. | `required`, `pattern`, `minlength`, `maxlength` |

> [!note] Use native validation where it exists
> These are the platform's parsers and constraints, not look-alike replacements. They produce the same reason categories as native controls: missing value, type mismatch, pattern mismatch, range underflow or overflow, step mismatch, and length errors. HTML Next adds no `tel` type because HTML itself does not define one worldwide telephone-number grammar; a telephone number remains `string` with an explicit `pattern` when a product has a narrower format.

Constraint attributes narrow a type; they never replace it. Their values are themselves parsed according to the declared type, and incompatible constraints are conformance errors. The [Validation chapter](/html-next/validation) defines when validity is recomputed, how failures are reported, and how native form controls interoperate.

## Two families: serializable and reference

A type either has a lossless string form or it does not, and that single fact decides everything about how it behaves.

| Family | Types | Behaviour |
| --- | --- | --- |
| **Scalar & list**<br>[L1]{.pill .l1} [L2]{.pill .soon} | `string`, `number`, `integer`, `boolean`, `email`, `url`, HTML date/time types, and keyword enums (L1); CSS types such as `<length>`, `<percentage>`, `<color>`, `<angle>`, `<time>`, `<url>`, and composite values (L2) | A single value token. Reflects to `data-*`, survives SSR, round-trips losslessly via the declared type. |
| **Structured**<br>[L2]{.pill .soon} | `object`, `array`; shape via nested `<prop>` or a referenced JSON Schema | Authored as an [object expression](/html-next/expressions), bound **by reference** for reactivity, and serialized as **JSON** only when it crosses a boundary (SSR payload, interop). Not reflected per-attribute. [Must]{.kw} be declared, since it cannot fall back to `string`. |

> [!warn] Prop contracts contain serializable values
> A prop contract contains values that can cross an HTML or JSON boundary. A component communicates upward with `<dispatch>` and `on:event`. Functions, callbacks, DOM nodes, and promises therefore stay outside the prop type grammar.

## Serialization: the string plus the type is the value

Because a serializable value has a string form and its type is declared, lowering can **record every serializable prop on the native root as `data-<name>`**. The invocation is then fully reconstructable from the DOM, replacement loses no information, and reading a value back is unambiguous: take the attribute string, parse it per the contract's type.

```html
<x-badge variant="solid" count="3">New</x-badge>

<!-- lowers to: each serializable prop recorded as data-*, so the invocation
     is fully reconstructable from the DOM -->
<span data-component="x-badge" data-variant="solid" data-count="3">New</span>

<!-- data-count="3" + the contract (count is a number) reads back as the number 3.
     the string plus the declared type is the value; nothing is lost. -->
```

| DOM | Declared type | Reads back as |
| --- | --- | --- |
| `data-label="Save"` | `string` | `"Save"` |
| `data-count="5"` | `number` | `5` |
| `data-loading` (present / absent) | `boolean` | `true` / `false` |
| `data-gap="1rem"` | `<length>` | a length |
| `data-variant="solid"` | `outline \| solid \| ghost` | `"solid"` |

> [!note] This is the platform's own pattern
> Typed values carried in strings are everywhere in HTML and CSS already: `<time datetime="2026-09-08">`, `<input type="number" value="5">`, `<meter value>`, and a registered `@property` custom property. HTML Next reuses the idea rather than inventing a parallel primitive-preservation channel. Reflection is **uniform**: a prop is recorded as `data-*` even when it also maps to a native attribute, so `data-*` is always the complete provenance record. Structured props are the one exception, they are carried as JSON rather than reflected. See [lowering & provenance](/html-next/components).

## Structured data: shape, authoring, wire

CSS has no object or array type, so structured data steps outside CSS to the web's other data standards. Three concerns stay separate, and each has its own well-defined form:

- **Shape** is declared in HTML, recursively, with nested `<prop>` (the contract's own vocabulary, no data island), or by referencing a **JSON Schema** for shared or external shapes.
- **Authoring** a value uses an [object expression](/html-next/expressions) (`{ id: 1, name: 'Ada' }`), lighter than JSON and pure, not a JS object. In practice most structured values are a *reference* to `<state>` or `<data>` rather than an inline literal.
- **Wire** form is **JSON**: the mandatory-double-quote serialization is a machine concern, used when a value must cross a boundary (SSR payload, network, interop), never the authoring syntax.

```html
<!-- shape described in HTML, recursively, with nested <prop> -->
<prop name="rows" type="array">
  <prop type="object">
    <prop name="id"   type="number">
    <prop name="name" type="string">
  </prop>
</prop>

<!-- or reference a JSON Schema for shared / external shapes -->
<prop name="rows" type="array" schema="/schemas/rows.json">
```

---

> [!norm] Zod and Valibot, but in the platform
> A declared type already does what a userland schema validator does: **parse** an input, **validate** it against a shape, and hand back a **typed** value. Libraries like [Zod](https://zod.dev/) and [Valibot](https://valibot.dev/) exist precisely because neither HTML nor JavaScript offers that natively. Get the type layer right here, and the interop with the JavaScript layer above it, and schema validation becomes a **DOM-native capability**: a component prop, a form field, or a data source carries its own schema and the platform enforces it, with no bundled validator. **The contract is the schema.**

## Keywords and the quoting rule

An enum is just `string` constrained to a set of keywords. It is written with **bare keywords** (`outline | solid | ghost`, never `"outline" | "solid"`) because in **attribute position** an unquoted identifier and a quoted string are the same token: `<foo bar=quiz>` equals `<foo bar="quiz">`, and `[bar=quiz]` equals `[bar="quiz"]`. So the string value `"solid"` satisfies `outline | solid | ghost`.

One exception keeps the bare form unambiguous. Because built-in type names are reserved, a keyword that spells one is written **quoted**: `'unknown' | known` is a two-member enum, while `unknown | known` reads `unknown` as the type that accepts any value, which makes the whole union accept anything. Quoting is the only way to say the literal, and it is confined to those reserved spellings; every other enum member stays bare. The canonical form of a type expression preserves that quoting for the same reason.

That equivalence **flips in expression position**, which is not attribute position. In the assignment-free expression language a bare word is an *identifier* (a binding) and quotes make a *string literal*, exactly as in a CSS selector value versus a scripting expression:

```html
<!-- ATTRIBUTE position: bare and quoted are the same token (as in HTML/CSS) -->
<x-button variant=solid>   is identical to   <x-button variant="solid">
<!-- and the enum type is written bare: outline | solid | ghost -->

<!-- EXPRESSION position: bare is a reference, quotes make a string literal -->
<button class:active="variant = 'solid'">   <!-- 'solid' is the string -->
<button class:active="variant = solid">      <!-- WRONG: solid read as a binding name -->
```

> [!note] One line, two sides
> Attribute / type / selector land: bare equals quoted (both the string). Expression land: bare is a reference, quotes are a literal. Both are where HTML and CSS already put the line, so neither needs a new rule to learn.

## Web value types

The dimension family is only part of a larger set of value domains the web already defines, which a markup type system should name rather than collapse to `string`.[^1][^2][^5]

| Domain | Examples |
| --- | --- |
| Attribute value spaces | boolean & enumerated attributes, token lists, sets |
| Web value types | URLs, MIME types, IDs & ID references, colors, lengths, percentages, times, angles |
| Constrained values | numeric ranges, element references, selectors |
| Content models | permitted / required / repeated / mutually exclusive children (e.g. tabs constraining their panels) |
| Trusted content | a dedicated trusted-HTML type: the only value `$html` places without sanitizing (an ordinary string is sanitized) |

## Beyond values: layered identity, content, and trust

These are Level&nbsp;3 directions that a value-only type system does not reach, and where "web-native" means structural, not just scalar.

> [!note] Layered value identity
> The same author-facing attribute can parse to a value, reflect to a DOM property under a different name, and participate in the reactive graph as a third thing. CSS Typed OM already exposes the distinction between serialized CSS and typed values.[^4][^8] Naming those layers explicitly is what lets one source lower correctly to React props, Vue refs, and native attributes without guessing. Lit `@property` converters are prior art for the attribute-to-property half of this, typed reflection with a declared converter.[^14]

> [!note] Content models
> A type can constrain *markup*, not only values: which children are permitted, required, repeated, or mutually exclusive (a tab list constraining its panels). This is the XML-Schema-shaped half of the system, applied to component composition.

> [!norm] Trusted content
> Placing raw, *unsanitized* markup accepts **only** a dedicated trusted-HTML type, never an ordinary string. There is no `.innerHTML` authoring syntax: markup goes through the `$html` directive, which **sanitizes an ordinary string** and places a **trusted-HTML value** as-is. The platform sinks a target ultimately lowers onto (`innerHTML`, `outerHTML`, `srcdoc`) are governed by the platform's [Trusted Types](https://www.w3.org/TR/trusted-types/); a bare string reaching them is a conformance error, which is what keeps the language `eval()`-free end to end.

## References

[^1]: W3C CSS Values and Units Level 4, [value definition syntax](https://www.w3.org/TR/css-values-4/#value-defs) and [component value types](https://www.w3.org/TR/css-values-4/#component-types), including numeric and dimension types such as `<length>`, `<percentage>`, `<angle>`, and `<time>`.
[^2]: W3C CSS Color Module Level 4, [the `<color>` type](https://www.w3.org/TR/css-color-4/#color-type).
[^3]: W3C CSS Properties and Values API Level 1, [registered custom properties](https://www.w3.org/TR/css-properties-values-api-1/#at-property-rule) and [their type syntax strings](https://www.w3.org/TR/css-properties-values-api-1/#syntax-strings).
[^4]: W3C CSS Typed OM Level 1, [typed representations of CSS values](https://www.w3.org/TR/css-typed-om-1/#stylevalue-objects).
[^5]: MDN, [CSS data types](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/Data_types) (an index spanning quantities, colors, images, positions, and other value domains).
[^6]: MDN, [CSS value definition syntax](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Values_and_units/Value_definition_syntax) (keywords, data types, combinators, and multipliers).
[^7]: MDN, [the `@property` `syntax` descriptor](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40property/syntax) (typed custom properties, lists, keywords, and the universal `*` syntax).
[^8]: MDN, [CSS Typed Object Model API](https://developer.mozilla.org/en-US/docs/Web/API/CSS_Typed_OM_API) (CSS values exposed as typed objects rather than undifferentiated strings).
[^9]: IETF, [JSON Schema](https://json-schema.org/) (the standard shape language for structured data).
[^10]: WHATWG HTML, [`data-*` attributes](https://html.spec.whatwg.org/multipage/dom.html#embedding-custom-non-visible-data-with-the-data-*-attributes) and [boolean attributes](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#boolean-attributes).
[^11]: W3C XML Schema Part 1, [attribute defaulting](https://www.w3.org/TR/xmlschema11-1/#cvc-au) (the `default` attribute).
[^12]: W3C, [Trusted Types](https://www.w3.org/TR/trusted-types/) (the trusted-content type model HTML Next mirrors for raw markup via `$html`).
[^13]: [Zod](https://zod.dev/) and [Valibot](https://valibot.dev/) (userland schema validation, the parse/validate/infer pattern this makes DOM-native).
[^14]: Lit [@property converters](https://lit.dev/docs/components/properties/#conversion): typed attribute-to-property reflection with a declared converter, prior art for the three-layer model where an author-facing attribute, a reflected DOM property, and the value it parses to are named separately.
[^15]: WHATWG HTML, [states of the `input` `type` attribute](https://html.spec.whatwg.org/multipage/input.html#states-of-the-type-attribute), including the email, URL, numeric, and date/time value syntaxes.
[^16]: WHATWG HTML, [the Constraint Validation API](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-constraint-validation-api) and its required, type, pattern, length, range, and step constraints.
[^17]: MDN, [Using HTML form validation and the Constraint Validation API](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Constraint_validation) (native type and constraint behavior with examples).
[^18]: MDN, [Date and time formats used in HTML](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Date_and_time_formats).
