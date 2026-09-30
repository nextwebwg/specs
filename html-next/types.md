---
title: Type System
order: 7
blurb: value types and absence
eyebrow: Declarative HTML Components
---

# Types

A type names the kind of value a component accepts or produces. Base types have plain keyword names; type constructors combine or constrain them. A declaration such as `type="number"` determines how a prop's value is parsed and validated.

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

`enum(...)` accepts exactly its listed non-null literal values. It takes one or more distinct quoted strings, booleans, or finite numbers; quoted words are values, not type names. String comparison is case-sensitive, so `SM` does not match `'sm'`. The parsed JavaScript value keeps the member's type, and a TypeScript target can expose the corresponding literal union. Like every prop, an enum prop also accepts `null` as no value. This constructor follows JSON Schema's `enum` constraint, which allows members of different types.[^14]

```html
<prop name="size" type="enum('sm', 'md', 'lg')" default="md"></prop>
<x-button size="sm">Save</x-button>

<prop name="current" type="enum(true, false, 'page', 'step', 'location')" default="false"></prop>
<x-nav-item current="false">Not current</x-nav-item>
<x-nav-item current="step">Current step</x-nav-item>
<x-nav-item :current="false">Also not current</x-nav-item>
```

For a plain HTML attribute, the enum serializes each member to its attribute spelling and selects the one whose spelling exactly matches the written string. The attribute value is converted to that member's type: `current="false"` becomes JavaScript `false`, while `current="step"` becomes the string `"step"`. The non-null JavaScript value is a boolean or one of the named strings. A TypeScript target exposes `boolean | 'page' | 'step' | 'location' | null`, preserving those literal choices and the universal absence value. The match must be unique: `enum(false, 'false')` is invalid because both members have the HTML spelling `"false"`. A `:` binding already supplies a typed value, so `:current="false"` is valid while `:current="'false'"` is invalid; bound values are checked by type and value without string conversion.

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

These values are JavaScript objects and arrays, not delimited strings. The same shapes can be declared with nested `<prop>` elements when fields need their own declarations. In that form, `object` contains named fields and `array` contains one item declaration:

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

Structured values use the object and array literal syntax of [HTML Next expressions](/html-next/expressions), **not JSON**. A plain attribute supplies a fixed value, parsed according to the declared prop type. A `:` binding evaluates an expression that may read other values and change with them:

```html
<x-plot point="{ x: 3, y: 5 }"></x-plot>
<x-table rows="[{ id: 1, name: 'Ada' }, { id: 2, name: 'Lin' }]"></x-table>
<x-plot :point="{ x: currentX, y: 5 }"></x-plot>
```

Bare keys, single-quoted strings, and trailing commas are allowed in both forms. A plain attribute contains only literal values; `point="{ x: currentX }"` is invalid because `currentX` is a reference. Use `:point="{ x: currentX }"` to read it, or `:point="point"` to pass an existing object from `<state>` or `<data>`. The `:` marks a binding, not an object. These expressions are pure and typed, not arbitrary JavaScript. JSON is used only as a wire format when structured data crosses an SSR, network, or interop boundary.

## Null and missing values

`null` means **no value**. It is distinct from the empty string, zero, and false. Every declared prop accepts `null`, regardless of whether its type is `string`, `number`, `enum(...)`, `list(...)`, or `object(...)`. The declared type constrains non-null values; `required` makes `null` invalid.

A declared prop that is omitted and has no default resolves to `null`, consistent with DOM `getAttribute()` returning `null` for a missing attribute.[^11] An explicit bound `null` also gives the prop a null value. An explicit empty string remains a string value.

```html
<!-- Given <prop name="label" type="string"></prop> -->
<x-note></x-note>             <!-- label is null -->
<x-note :label="null"></x-note> <!-- label is null -->
<x-note label=""></x-note>    <!-- label is the empty string -->
```

## Future exploration

Unions could allow more than one base type. An untagged union of `string` and `number` needs a parsing rule: a written value of `2.5` could produce either a string or a number. A component's `type` prop could discriminate the types of `value` and other props, but the declaration syntax and behavior remain open.

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
