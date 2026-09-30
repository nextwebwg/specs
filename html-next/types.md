---
title: Type System
order: 7
blurb: value types and absence
eyebrow: Declarative HTML Components
---

# Types

A declared type tells Declarative Components how to read a value written in HTML and what JavaScript value to give the component.

```html
<prop name="count" type="integer"></prop>
<x-counter count="3"></x-counter>
```

Here the written `count="3"` becomes the number `3` in `host.state.count`. Type names are plain keywords; `values` and `pattern` can further limit what the component accepts.

## Base value types

Each type has one name and one meaning.

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

> [!note] Declared type rules
> HTML already parses formats such as dates and URLs, and control modes change which values are valid. CSS defines colors, lengths, and other value grammars.[^1][^16] JavaScript can implement these rules, but putting them only in component code hides them from the browser runtime, build tools, and generated TypeScript. Declarations expose the rules without changing native DOM properties such as `HTMLInputElement.value`.

In the [JavaScript layer](/html-next/javascript), `number` and `integer` prop values are JavaScript `Number` values. A written `ratio="0.3"` therefore becomes the number `0.3` in `host.state.ratio` when `ratio` is declared as `number`.

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

## Lists and their written forms

Every list has one item type. These three declarations all produce a JavaScript array of keywords; they differ in how the value is written in an HTML attribute:

| Declared type | Written value | JavaScript value |
| --- | --- | --- |
| `list(keyword)` | `['red', 'blue']` | `["red", "blue"]` |
| `keyword+` | `red blue` | `["red", "blue"]` |
| `keyword#` | `red, blue` | `["red", "blue"]` |

`list(T)` uses a bracketed value, accepts an empty list (`[]`), and can give its items a structured type such as `object({ id: number })`. `keyword+` and `keyword#` are shorter written forms for **one or more keywords**: space-separated and comma-separated, respectively, following CSS value definition syntax.[^12] They do not change the JavaScript representation. Whitespace around a comma is allowed; an empty item is invalid.

## Structured values

`object({ ... })` describes named fields; `list(T)` requires every list item to have type `T`:

```html
<prop name="point" type="object({ x: number, y: number })"></prop>
<prop name="rows" type="list(object({ id: number, name: string }))"></prop>
```

These values are written as object and bracketed list literals and become JavaScript objects and arrays. When a field needs its own `values`, `required`, `nullable`, or description, expand the shape into nested `<prop>` declarations. Write `type="list"` with one unnamed child `<prop>` for its item type. This expanded declaration describes the same `rows` type as `list(object({ id: number, name: string }))` above:

```html
<prop name="rows" type="list">
  <prop type="object">
    <prop name="id" type="number" required></prop>
    <prop name="name" type="string" required></prop>
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

<state name="history" type="list" :value="[]">
  <prop type="object">
    <prop name="trigger" type="keyword" values="keyboard, pointer, programmatic" required></prop>
  </prop>
</state>
```

Each nested field is checked when the object or array is checked. `required` means the field must be present; `nullable` permits an explicitly present `null` value, as in `previous` above. The same `nullable` attribute permits a declared state to hold `null`. An `open` object permits additional fields; a field with `type="unknown"` accepts any JavaScript value, but `unknown` cannot be a top-level prop because it has no HTML attribute form. A build tool reports a malformed nested `values` constraint as an error; the live browser parser warns and ignores that constraint. Generated TypeScript uses the closest literal types, so the event detail above has `trigger: 'keyboard' | 'pointer' | 'programmatic'`.

A shared or external schema can instead be referenced with `schema`, using JSON Schema:[^13]

```html
<prop name="rows" type="list" schema="/schemas/rows.json"></prop>
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

A component can select a prop's type from the current value of another declared prop or state value. For example, a `type` prop can select whether `value` is a string or a number.

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

### Selection rules

The selector has one base type and a finite `values` constraint:

- `from` names one declared prop or state value. It is a name lookup, not an expression.
- Each permitted selector value needs exactly one `<option>`. The option's `value` is parsed as the selector's base type. An invalid `values` constraint makes the type declaration invalid.
- A selecting prop must be `required` or have a default. Its effective value selects the type before the dependent attribute is parsed, regardless of attribute order. A selecting state uses its initialized value.
- The dependent prop exists for every option. It is `null` when omitted without a default. A `null` selector also permits only a `null` dependent value because it selects no option.
- A dependent prop may have a default only when its selector is a prop with a default. That dependent default must satisfy the selected type.

### Reading and changing values

Plain attributes are parsed using the selected type. With the declaration above, `type="number" value="2.5"` produces the JavaScript number `2.5`; `type="text" value="2.5"` produces the string `"2.5"`.

- Bound values keep their JavaScript type and must satisfy the selected option. For example, `<x-input from:type="mode" from:value="entry"></x-input>` can read two reactive values.
- When the selector changes, the dependent type is selected again. Changing both values together checks the resulting pair. A previously supplied non-null dependent value that fails the new type is invalid; the component reports a type error instead of converting it.
- Generated TypeScript preserves the relationship for a public prop selector: `type="number"` accepts a number or `null` for `value`, while `type="text"` accepts a string or `null`. Inline and named `<type>` declarations produce the same contract.

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
  <handler name="useNumber"><set name="mode" value="number"></set></handler>
</defs>
```

The same selection rules apply as `mode` changes. A caller cannot know an internal state selector from the invocation alone, so generated TypeScript exposes all option types while runtime validation checks the active one. Here `value` has the public type `string | number | null`.

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
