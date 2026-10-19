---
title: Overview
order: 0
blurb: what it is, in plain terms
navGroup: guide
eyebrow: Start here
status: Orientation · read this first
---

# Declarative HTML Components in plain terms

This proposal is a way to build web interfaces by **writing markup**, not framework code. You define reusable tags, add data and behavior with a small set of attributes, and it turns into **ordinary native HTML** the browser already understands. This page is the plain-language tour; every section links to the precise spec.

## The one-sentence version

Take the good parts of modern component frameworks, components, reactive data, scoped styles, and express them **as HTML itself**, so they run natively in the browser (through a polyfill today) or compile to React, Vue, or Svelte, with **no build step required** and **no `eval()`**.

```html
<!-- You write this -->
<x-button variant="solid">Save</x-button>

<!-- It becomes a real native button (no wrapper, no shadow root) -->
<button data-component="x-button">Save</button>
```

A component is not a class or a function. It is a **piece of markup, treated as data**. The browser (or the polyfill) reads it and produces real elements, so what ships is a plain `<button>` with native focus, forms, and accessibility intact, plus a `data-component` stamp saying where it came from.

## The pieces, at a glance

Declarative HTML Components is one specification, in chapters that each define part of the component model. In plain terms:

| Chapter | In plain terms |
| --- | --- |
| [Components](/declarative-components/components) | Define a reusable tag with `<template component>`. Its interface (props) and non-visual declarations, including what it adds to the document head, live in a `<defs>` region; below that is the markup it renders. |
| [Templating](/declarative-components/templating) | Control flow uses attributes that survive the HTML parser: `$if` (show or not), `$each` (repeat), `$match` (pick one). Output uses `{expression}` for inline text and `$value`/`$html` to replace content with text or safe markup. |
| [Expressions](/declarative-components/expressions) | A small, typed, no-JavaScript expression language for bindings and inline text, with predictable rules for missing data and equality (it never throws). |
| [Bindings & events](/declarative-components/bindings) | Set reactive values with `from:attr`, two-way with `bind:`, react to events with `on:`, toggle a class or style with `class:`/`style:`. |
| [Reactivity](/declarative-components/reactivity) | Declare local `<state>`, derived `<computed>` values, and external `<data>` resources. Reads refetch and synchronized writes send according to their declared change policy. |
| [Types](/declarative-components/types) | Plain-keyword value types cover strings, numbers, HTML value formats, and selected CSS values. An omitted prop with no default is `null`. |
| [Validation](/declarative-components/validation) | A declared type is a constraint: a typed prop or data value that fails its type is invalid, through the validity model [HTML Forms](/html-forms) extends to every element, and styled with the native `:user-invalid`. |
| [Style scoping](/declarative-components/styling) | A component's `<style>` applies to that component, using CSS `@scope`, scoping without the isolation cost of a shadow root. |
| [The JavaScript layer](/declarative-components/javascript) | The escape hatch. When behavior genuinely needs code (a timer, a chart library), a separate ES-module *controller* attaches to the component. Definitions contain no code; they reference it. |

## How it fits together

Two ideas hold the whole thing up:

- **Declarative by default, code only when needed.** Most of an interface, structure, data, styling, is markup with no script. Imperative JavaScript is a deliberate, separate layer you reach for only when there is no declarative way, and even then the component definition stays pure data.
- **Everything joins by tag.** A definition and, if it has one, a controller both register under the same tag name in a registry, the exact way the platform's own custom elements join a tag to a class. Nothing references anything else by file path; the tag is the join.

> [!note] Two ways to run it
> The same source has two honest execution paths: a **polyfill** that lowers it to native DOM in the browser today, and **converters** that compile it to idiomatic React, Vue, or Svelte. Both must produce the same observable result ([Targets & Equivalence](/declarative-components/targets)).

## How "done" is measured

The specification advances through **Levels**, as CSS specifications do: this draft is Level&nbsp;1, including templating and live reactivity, and features beyond it are marked for a later Level where they appear. A Level describes the language contract, not an implementation milestone. A dated **Snapshot** records the draft on a given day. An implementation should identify the snapshot it supports; conformance tests establish whether it meets that contract.

## What the draft defines, and what is still open

This is a Stage&nbsp;0 proposal. The chapters define the language; implementation coverage belongs in the [reference tools](https://github.com/nextwebwg/html-next).

::: two

> [!ex] Defined in Level 1
> Typed native-root components and slots, templating and control flow, expressions, bindings, live state and computed updates, reactive data resources, validation, and style scoping. The browser runtime and compiled targets share one observable-equivalence contract.

> [!warn] Still open
> Some hydration records remain unresolved, including explicit prop recovery and logical ownership through server-rendered portals ([Rendered Form & Hydration](/declarative-components/rendered-form#open-questions)). Untagged type unions and writable computed bindings remain explorations. External composition is marked for Level 2; deeper native-element and Shadow DOM integration needs upstream platform work.

:::

## See it working

For complete, copy-pasteable code, one component, a component that uses another, and a JavaScript controller, see [Examples](/declarative-components/examples). Then read any chapter above for the precise rules.
