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

<!-- a component definition declares the bounds on its own prop -->
<template component="x-age-field">
  <defs><prop name="age" type="integer" min="0" max="120">Age.</prop></defs>
  <div from:data-age="age"></div>
</template>
<x-age-field from:age="draft.age"></x-age-field>

<!-- structured data validates against a schema; failures carry a path -->
<data name="profile" src="/api/me" schema="/schemas/profile.json">
```

## Built on HTML Forms

This chapter does not define a validity model of its own. [HTML Forms Level&nbsp;1](/html-forms#constraint-validation-on-any-element) defines one for any element with a value:

- `el.validity` with named flags such as `valueMissing`, `rangeOverflow`, and `tooShort`, plus a list of errors with messages and optional paths;
- `el.validate()` and `el.setValidity(errors)`;
- the `invalid` event, `validationMessage`, and `:valid`, `:invalid`, and `:user-invalid`.

That model leaves open where an element's constraints come from. A native `<input>` takes them from its attributes. A component takes them from its declared types, which is what this chapter defines.

> [!note] Included in the reference implementation
> The [`html-next` implementation repository](https://github.com/nextwebwg/html-next) includes a pure `validate(value, constraint)` helper and a generalized validity surface. Authored prop constraints use the same named failures as HTML's `ValidityState`.[^2] Authors use the proposed surface; the implementation handles browser compatibility.

## The type is the constraint

A prop's declared type and its constraint attributes (see [Types](/html-next/types)) compile to validity. Each kind of failure produces one of HTML Forms' reasons:

| Declared | A value fails when | Reason |
| --- | --- | --- |
| `required` | it is empty | `valueMissing` |
| the type (`number`, `color`, etc.) | it is the wrong kind of value | `typeMismatch` |
| `values` | it is outside the permitted set | `typeMismatch` |
| `min` / `max` | it is below or above the bound | `rangeUnderflow` / `rangeOverflow` |
| `minlength` / `maxlength` | it is too short or too long | `tooShort` / `tooLong` |
| `pattern` | it does not match | `patternMismatch` |
| the type's parser | it cannot be parsed as the type | `badInput` or `typeMismatch` |
| a JSON Schema rule | a rule with no reason above fails | the schema keyword, with the failing value's `path` |

A definition's `default` is checked when the definition is compiled. A malformed constraint is a declaration error in build tools; the live parser warns and ignores that constraint. A supplied value that fails a well-defined constraint is ordinary invalid data: it sets validity and does **not** produce a console warning. This includes values supplied through a reactive binding. If a written value cannot be parsed as its declared type, the component retains the written value and reports `badInput` or `typeMismatch`; it still mounts so the author can correct the value.

On a component with a non-native root, `el.validity` exposes the corresponding `ValidityState` flags and `el.validity.errors` gives each failure's prop path. `checkValidity()` reports whether the current values pass. When a component renders a native form control, the control retains its native `ValidityState`; the compatibility layer combines additional component failures with native validity. The [Types chapter](/html-next/types#value-constraints) defines which constraints apply to each type.

> [!norm] This is the schema, made native
> This is the mechanism behind “the contract is the schema” (see [Types](/html-next/types)). A typed prop, a `bind:` input, or a `<data>` value that fails its declared type produces a native validity error, one that form controls, components, and data sources all share.

## Where the validity lives

- **A typed prop** gives validity to the component's root element. When that root is a native control, such as a component that lowers to `<input>`, the prop's failures join the control's own, and the control still takes part in its form natively.
- **A `<data>` source** with a `schema` has validity for its current value. Each failure carries the `path` of the part that failed, so a form can point each error at its field.
- **The pure helper** `validate(value, type | schema)` validates raw data attached to no element and returns the same result.

```ts
el.validity            // { valid: false, rangeOverflow: true, errors: [{ reason: "rangeOverflow", path: "age", message: "…" }] }

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
