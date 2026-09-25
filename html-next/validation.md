---
title: Validation
order: 8
blurb: the type is the constraint
eyebrow: Declarative HTML Components Level 2 · proposed direction
status: Proposed direction · Level 2
---

# Validation

A declared type is a constraint. [HTML Forms](/html-forms) extends constraint validation to any element with a value; this chapter defines how a component's **prop types** and a `<data>` source's **schema** produce validity in that model, so schema validation stops being a library and becomes native.

## At a glance

The same validation that already works on a form `<input>` works on any typed value, a component prop or a data response, with no forms library:

```html
<!-- a form control validates against its constraints, exactly as today -->
<input bind:value="email" type="email" required>

<!-- a typed component prop validates the same way, with no forms library -->
<x-field :value="draft.age" type="<number>" min="0" max="120">

<!-- structured data validates against a schema; failures carry a path -->
<data name="profile" src="/api/me" schema="/schemas/profile.json">
```

## Built on HTML Forms

This chapter does not define a validity model of its own. [HTML Forms Level&nbsp;1](/html-forms#constraint-validation-on-any-element) defines one for any element with a value:

- `el.validity` as a list of reasons (`missing`, `type`, `range`, …), each with a message and optionally a path;
- `el.validate()` and `el.setValidity(errors)`;
- the `invalid` event, `validationMessage`, and `:valid`, `:invalid`, and `:user-invalid`.

That model leaves open where an element's constraints come from. A native `<input>` takes them from its attributes. A component takes them from its declared types, which is what this chapter defines.

> [!note] Included in the reference implementation
> The [`html-next` implementation repository](https://github.com/nextwebwg/html-next) includes this validation layer today. Its `validate(value, constraint)` function checks required values, scalar types, keyword enums, ranges, lengths, patterns, and steps, and it returns the reason list HTML Forms defines. Authors use the proposed surface; the implementation handles browser compatibility.

## The type is the constraint

A prop's declared type and its constraint attributes (see [Types](/html-next/types)) compile to validity. Each kind of failure produces one of HTML Forms' reasons:

| Declared | A value fails when | Reason |
| --- | --- | --- |
| `required` | it is empty | `missing` |
| the type (`number`, `<color>`, an enum…) | it is the wrong kind of value | `type` |
| `min` / `max` | it is out of range | `range` |
| `minlength` / `maxlength` | it is too short or too long | `length` |
| `pattern` | it does not match | `pattern` |
| `step` | it is off the step grid | `step` |
| the type's parser | it cannot be parsed as the type | `unparseable` |
| a JSON Schema rule | a rule with no reason above fails | the schema keyword, with the failing value's `path` |

A literal value is checked when the definition is compiled: a literal prop value or `default` that fails its type is a conformance error. A bound value is checked at run time and produces validity.

> [!norm] This is the schema, made native
> This is the mechanism behind “the contract is the schema” (see [Types](/html-next/types)). A typed prop, a `bind:` input, or a `<data>` value that fails its declared type produces a native validity error, one that form controls, components, and data sources all share.

## Where the validity lives

- **A typed prop** gives validity to the component's root element. When that root is a native control, such as a component that lowers to `<input>`, the prop's failures join the control's own, and the control still takes part in its form natively.
- **A `<data>` source** with a `schema` has validity for its current value. Each failure carries the `path` of the part that failed, so a form can point each error at its field.
- **The pure helper** `validate(value, type | schema)` validates raw data attached to no element and returns the same result.

```ts
// validity recomputes when the value changes: usually you read it, not call it
el.validity            // { valid: false, errors: [{ reason: "range", message: "…" }] }

// a failure the type cannot know about, such as a server's answer
el.setValidity([{ reason: "taken", message: "That email is in use." }])

// a pure helper: validate any value against a type or schema, no element involved
validate(value, type | schema)   // → { valid, errors }
```

## When validation runs

A component's values are already reactive dependencies, so validity recomputes whenever a value changes; `el.validity` is always current, and nothing needs to trigger it. `el.validate()` is for an explicit check, such as at submit time. Showing an error follows HTML Forms: it waits for interaction, through `:user-invalid`.

For an asynchronous rule, such as whether a name is taken, a `<data>` lookup keeps the answer current and `setValidity()` applies it (see [Reactivity](/html-next/reactivity)).

## How it runs today

> [!norm] Authors write the platform syntax
> Authors set validity through `setValidity()` and style `:valid`, `:invalid`, and `:user-invalid`. They do not target polyfill attributes. Until browsers implement HTML Forms' validity for every element, the reference implementation provides it:
>
> - native form controls use their real `setCustomValidity()`, so the real `:invalid` and form submission still work;
> - form-associated custom elements use the real `ElementInternals.setValidity()`;
> - every other element gets the same validity object and event, and the matching ARIA state.
>
> When browsers expose validity on every element, the implementation steps aside without any change to component source or application CSS.

## References

[^1]: HTML Forms Level 1, [constraint validation on any element](/html-forms#constraint-validation-on-any-element) (the validity model this chapter builds on).
[^2]: WHATWG HTML, [the Constraint Validation API](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-constraint-validation-api) and [ValidityState](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-validitystate-interface).
[^3]: CSS Selectors Level 4, [validity pseudo-classes](https://www.w3.org/TR/selectors-4/#validity-pseudos) (`:valid`, `:invalid`, `:user-invalid`).
[^4]: IETF [JSON Schema](https://json-schema.org/); [Zod](https://zod.dev/) / [Valibot](https://valibot.dev/) (the issue-list model this mirrors).
