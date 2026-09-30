---
title: Type System
order: 7
blurb: value types and absence
eyebrow: Declarative HTML Components
---

# Types

A type names the kind of value a component accepts or produces. Base types have plain keyword names. A declaration such as `type="number"` determines how a prop's value is parsed and validated. Constraints such as `values` and `pattern` can further restrict that type.

HTML already applies rules like these inside its elements: an attribute can select a control mode, and that mode changes which values are valid and how the control handles them. Declarative Components lets authors state comparable rules for their own components. The declaration makes the parsing, permitted values, and dependencies available to the browser runtime, build tools, and generated TypeScript APIs instead of leaving them implicit in component code. A component's parsed JavaScript prop value follows its declared type; this does not change the native DOM definition of properties such as `HTMLInputElement.value`.

Component authors have often put missing behavior in JavaScript because code can implement any rule. That leaves rules such as permitted keywords, dates, colors, and lengths inside each component's code. HTML already defines many value formats and parsing rules; CSS defines a broad vocabulary of typed values and property grammars.[^1][^16] These declarative vocabularies describe domain values more precisely than JavaScript's built-in primitive types alone. This proposal gives component authors a way to declare those rules where tools and other authors can inspect them, while JavaScript remains available for behavior that needs code.

```html
<defs>
  <prop name="label" type="string"></prop>
  <prop name="tag" type="keyword"></prop>
  <prop name="count" type="integer"></prop>
  <prop name="ratio" type="number"></prop>
</defs>
```

## Base value types

The basic value types come first, followed by values defined by HTML and CSS. Each type has one name and one meaning.

| Type | Example | Description |
| --- | --- | --- |
| `string` | `"Save"`, `""` | Any string, including the empty string.[^1] |
| `keyword` | `compact`, `size-2` | One or more ASCII letters, digits, underscores, or hyphens (`^[A-Za-z0-9_-]+$`), represented as a JavaScript string.[^2] |
| `boolean` | `true`, `false` | A truth value.[^3] |
| `integer` | `3`, `-2` | A whole number, parsed using HTML's integer syntax.[^4] |
| `number` | `2.5` | A finite number, parsed using HTML's floating-point number syntax.[^4] |
| `url` | `https://example.org/` | A valid absolute URL string.[^5] |
| `email` | `ada@example.org` | A valid email address string.[^5] |
| `date` | `2026-09-29` | A calendar date without a time zone, written year-month-day: at least four year digits and exactly two digits each for month and day.[^6] |
| `month` | `2026-09` | A year and month without a time zone: at least four year digits, a hyphen, and a two-digit month.[^6] |
| `week` | `2026-W40` | A week-year and week number: at least four year digits, `-W`, and a two-digit week.[^6] |
| `time` | `13:45` | A time of day without a time zone: `HH:mm`, optionally followed by seconds and up to three fractional-second digits.[^6] |
| `datetime-local` | `2026-09-29T13:45` | HTML's ISO 8601-derived local date and time format, without a time zone: a valid date, `T` or a space, then a valid time (`YYYY-MM-DDTHH:mm` for the example shown).[^6] |
| `datetime` | `2026-09-29T13:45Z`, `2026-09-29T13:45-07:00` | HTML's global date and time format: a valid date and time followed by `Z` or a numeric UTC offset.[^6] |
| `color` | `rebeccapurple`, `#663399`, `rgb(102 51 153)` | A CSS color literal: recognized color keywords, hex notation, or numeric `rgb()`, `rgba()`, `hsl()`, `hsla()`, `hwb()`, `lab()`, `lch()`, `oklab()`, `oklch()`, and `color()` forms. The value stays a string.[^7] |
| `color-hex` | `#639`, `#663399`, `#663399cc` | A CSS hex color: `#` followed by 3, 4, 6, or 8 hexadecimal digits.[^8] |
| `length` | `8px`, `1rem` | A CSS length value, kept in its serialized string form.[^9] |
| `percentage` | `25%` | A CSS percentage value, kept in its serialized string form.[^9] |
| `duration` | `200ms`, `1.5s` | A CSS time value, kept in its serialized string form.[^9] |

In the [JavaScript layer](/html-next/javascript), `number` and `integer` prop values are JavaScript `Number` values. For a component invoked with `ratio="0.3"` and declaring `<prop name="ratio" type="number">`, a controller reads `host.state.ratio` as `0.3`.

## Finite choices

The `values` attribute limits a prop to a comma-separated set of values of its declared type. Each item is parsed and checked against `type` before the constraint is applied. The prop keeps one type; `values` does not convert a value into another type. A TypeScript target can expose the allowed values as a literal union within that type. This follows HTML's enumerated attributes, whose permitted keywords are defined separately from the attribute's value syntax, and JSON Schema's `enum` constraint.[^14][^15]

```html
<prop name="size" type="keyword" values="sm, md, lg" default="md"></prop>
<x-button size="sm">Save</x-button>

<prop name="level" type="integer" values="1, 2, 3" default="2"></prop>
<x-meter level="3"></x-meter>
```

Whitespace around commas is ignored. An item that does not conform to `type` invalidates the whole `values` constraint, as though `values` were absent. Build tools, including the unplugin, report this as a declaration error. The live browser parser warns and ignores the constraint. A bound value must have the declared JavaScript type and match a permitted value. For `type="integer" values="1, 2, 3"`, `level="3"` and `from:level="3"` produce the number `3`; `from:level="'3'"` is invalid. All declared props still accept `null` unless required.

## Pattern constraints

HTML's `pattern` attribute provides a regular-expression constraint for text values. A declaration writes the pattern without `/` delimiters; the pattern must match the entire nonempty value. The value remains a string in JavaScript. `required` determines whether an empty or omitted value is allowed.[^10]

```html
<prop name="sku" type="string" pattern="[A-Z]{3}-[0-9]{4}"></prop>
<!-- Accepts ABC-1234. -->
```

## Lists

A `+` suffix declares one or more space-separated values. A `#` suffix declares one or more comma-separated values, following CSS value definition syntax.[^12] Each item must satisfy the named base type. For `keyword`, the declarations are:

| Type | Written value | JavaScript value |
| --- | --- | --- |
| `keyword+` | `red blue` | `["red", "blue"]` |
| `keyword#` | `red, blue` | `["red", "blue"]` |

```html
<prop name="space-tags" type="keyword+"></prop>
<prop name="comma-tags" type="keyword#"></prop>
```

The separator is part of the written value; a component receives an array of parsed items in JavaScript. A comma-separated list may have whitespace around each comma. An empty item is invalid.

## Structured values

`object({ ... })` describes named fields and `list(T)` describes an array whose items have type `T`:

```html
<prop name="point" type="object({ x: number, y: number })"></prop>
<prop name="rows" type="list(object({ id: number, name: string }))"></prop>
```

These values are JavaScript objects and arrays, not delimited strings. The same shapes can be declared with nested `<prop>` elements when fields need their own declarations. In that form, `object` contains named fields and `array` contains one item declaration. A nested scalar field can use `values` to restrict that field without changing its base type:

```html
<prop name="point" type="object">
  <prop name="x" type="number" required></prop>
  <prop name="y" type="number" required></prop>
</prop>

<prop name="rows" type="array">
  <prop type="object">
    <prop name="id" type="number"></prop>
    <prop name="name" type="string"></prop>
  </prop>
</prop>
```

The same field declarations describe event details and structured state values:

```html
<event name="change" type="object">
  <prop name="value" type="number" required></prop>
  <prop name="trigger" type="keyword" values="keyboard, pointer, programmatic" required></prop>
  <prop name="previous" type="string" required nullable></prop>
</event>

<state name="history" type="array" :value="[]">
  <prop type="object">
    <prop name="trigger" type="keyword" values="keyboard, pointer, programmatic" required></prop>
  </prop>
</state>
```

Each nested field is checked when the object or array is checked. `required` means the field must be present; `nullable` permits an explicitly present `null` value, as in `previous` above. The same `nullable` attribute permits a declared state to hold `null`. An `open` object permits additional fields; a field with `type="unknown"` accepts any JavaScript value, but `unknown` cannot be a top-level prop because it has no HTML attribute form. A build tool reports a malformed nested `values` constraint as an error; the live browser parser warns and ignores that constraint. Generated TypeScript uses the closest literal types, so the event detail above has `trigger: 'keyboard' | 'pointer' | 'programmatic'`.

A shared or external schema can instead be referenced with `schema`, using JSON Schema:[^13]

```html
<prop name="rows" type="array" schema="/schemas/rows.json"></prop>
```

JSON Schema also has `enum` for a fixed set of values. An object schema can use it to constrain one field, and an enum can contain values of different JSON types.[^14] This JSON document is a schema, not an authored component value:

```json
{
  "type": "object",
  "properties": {
    "size": { "enum": ["sm", "md", "lg"] }
  }
}
```

### Writing structured values

Structured values use the object and array literal syntax of [HTML Next expressions](/html-next/expressions), **not JSON**. A plain attribute supplies a fixed value, parsed according to the declared prop type. A `from:` binding evaluates an expression that may read other values and change with them:

```html
<x-plot point="{ x: 3, y: 5 }"></x-plot>
<x-table rows="[{ id: 1, name: 'Ada' }, { id: 2, name: 'Lin' }]"></x-table>
<x-plot from:point="{ x: currentX, y: 5 }"></x-plot>
```

Bare keys, single-quoted strings, and trailing commas are allowed in both forms. A plain attribute contains only literal values; `point="{ x: currentX }"` is invalid because `currentX` is a reference. Use `from:point="{ x: currentX }"` to read it, or `from:point="point"` to pass an existing object from `<state>` or `<data>`. The `from:` prefix marks a binding, not an object. These expressions are pure and typed, not arbitrary JavaScript. JSON is used only as a wire format when structured data crosses an SSR, network, or interop boundary.

## Types selected by a prop or state value

A component can declare a prop whose type depends on the value of a declared prop or state value. The selector has one base type and a finite `values` constraint. Each permitted value selects one type for the dependent prop. The dependent prop remains declared in every case and resolves to `null` when omitted without a default.

An inline `<type>` belongs to the prop whose type varies:

```html
<defs>
  <prop name="type" type="keyword" values="text, number" default="text">The control mode.</prop>
  <prop name="value">The control value.
    <type from="type">
      <option value="text" type="string"></option>
      <option value="number" type="number"></option>
    </type>
  </prop>
</defs>
```

The same type can be named once under `<defs>` and referenced by a declaration's `type` attribute. A named type is local to that component:

```html
<defs>
  <type name="input-value" from="type">
    <option value="text" type="string"></option>
    <option value="number" type="number"></option>
  </type>
  <prop name="type" type="keyword" values="text, number" default="text">The control mode.</prop>
  <prop name="value" type="input-value">The control value.</prop>
</defs>
```

`from` looks up one declared prop or state value by name; it does not evaluate an expression. Each `<option value>` is parsed through the selector's declared type and must match one of its permitted values. Every permitted value must have exactly one option. An invalid `values` constraint cannot serve as a selector, so this declaration is an error. A selecting prop must be required or have a default; its effective value selects the type before any dependent value is parsed, regardless of attribute order. A selecting state uses its initialized value. A `null` selector permits only `null` for the dependent prop, because no option is selected. A dependent prop can declare a default only when its selector is a prop with a default; that value must satisfy the selected type.

Plain HTML attributes are parsed against the selected type. Thus `type="number" value="2.5"` gives the component a JavaScript number, while `type="text" value="2.5"` gives it a string. Bound values retain their JavaScript type and must satisfy the selected option. A selecting prop can itself be bound, as in `<x-input from:type="mode" from:value="entry"></x-input>`; when `mode` changes, the dependent type is selected again. Changing the selecting prop and its dependent prop together checks the resulting pair; a previously supplied dependent value that does not satisfy a newly selected type is invalid.

Generated TypeScript types preserve the relationship when the selector is a public prop: a numeric `type` accepts a number or `null` as `value`, and the default text type accepts a string or `null`. A named type reference and an inline `<type>` produce the same contract.

### Selecting from state

The same name lookup can select from state:

```html
<defs>
  <state name="mode" type="keyword" values="text, number" :value="'text'"></state>
  <prop name="value">The current value.
    <type from="mode">
      <option value="text" type="string"></option>
      <option value="number" type="number"></option>
    </type>
  </prop>
  <handler name="useNumber"><set name="mode" :value="'number'"></set></handler>
</defs>
```

When a selecting prop or state value changes, the type is selected again. A non-null dependent value that does not satisfy the new type is invalid; the component reports a type error rather than changing that value. A caller cannot know an internal state selector from the invocation alone, so generated TypeScript exposes the JavaScript representations of all its options while runtime validation checks the active option. Here that public type is `string | number | null`.

## Null and missing values

`null` means **no value**. It is distinct from the empty string, zero, and false. Every declared prop accepts `null`, regardless of whether its type is `string`, `number`, `list(...)`, or `object(...)`. The declared type constrains non-null values; `required` makes `null` invalid.

A declared prop that is omitted and has no default resolves to `null`, consistent with DOM `getAttribute()` returning `null` for a missing attribute.[^11] An explicit bound `null` also gives the prop a null value. An explicit empty string remains a string value.

```html
<!-- Given <prop name="label" type="string"></prop> -->
<x-note></x-note>             <!-- label is null -->
<x-note from:label="null"></x-note> <!-- label is null -->
<x-note label=""></x-note>    <!-- label is the empty string -->
```

## Future exploration

Unions could allow more than one base type. An untagged union of `string` and `number` needs a parsing rule: a written value of `2.5` could produce either a string or a number.

## Sources

[^1]: WHATWG HTML, [attribute values](https://html.spec.whatwg.org/multipage/dom.html#attributes); Web IDL, [`DOMString`](https://webidl.spec.whatwg.org/#idl-DOMString).
[^2]: This proposal's ASCII rule is informed by WHATWG HTML's [space-separated tokens](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#space-separated-tokens) and CSS's [custom identifiers](https://drafts.csswg.org/css-values-4/#custom-idents).
[^3]: Web IDL, [the `boolean` type](https://webidl.spec.whatwg.org/#idl-boolean).
[^4]: WHATWG HTML, [integers](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#signed-integers) and [floating-point numbers](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#floating-point-numbers).
[^5]: WHATWG HTML, [URL](https://html.spec.whatwg.org/multipage/input.html#url-state-(type=url)) and [email](https://html.spec.whatwg.org/multipage/input.html#e-mail-state-(type=email)) value formats.
[^6]: WHATWG HTML, [dates](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#dates), [months](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#months), [weeks](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#weeks), [times](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#times), [local dates and times](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#local-dates-and-times), and [global dates and times](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#global-dates-and-times).
[^7]: CSS Color Module Level 4, [color values](https://drafts.csswg.org/css-color-4/#color-type).
[^8]: CSS Color Module Level 4, [hexadecimal color notation](https://drafts.csswg.org/css-color-4/#hex-notation).
[^9]: CSS Values and Units Level 4, [lengths](https://drafts.csswg.org/css-values-4/#lengths), [percentages](https://drafts.csswg.org/css-values-4/#percentages), and [time values](https://drafts.csswg.org/css-values-4/#time).
[^10]: WHATWG HTML, [the `pattern` attribute](https://html.spec.whatwg.org/multipage/input.html#the-pattern-attribute); this proposal's [Validation chapter](/html-next/validation) applies pattern constraints to typed props.
[^11]: DOM Standard, [`getAttribute()`](https://dom.spec.whatwg.org/#dom-element-getattribute).
[^12]: CSS Values and Units Level 4, [value definition syntax multipliers](https://drafts.csswg.org/css-values-4/#component-multipliers).
[^13]: JSON Schema, [specification](https://json-schema.org/specification).
[^14]: JSON Schema Validation, [the `enum` keyword](https://json-schema.org/draft/2020-12/json-schema-validation#name-enum).
[^15]: WHATWG HTML, [keywords and enumerated attributes](https://html.spec.whatwg.org/multipage/common-microsyntaxes.html#keywords-and-enumerated-attributes).
[^16]: CSS Values and Units Level 4, [value definition syntax](https://drafts.csswg.org/css-values-4/#value-defs).
