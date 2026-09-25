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
<button data-component="x-button" data-variant="solid">Save</button>
```

A component is not a class or a function. It is a **piece of markup, treated as data**. The browser (or the polyfill) reads it and produces real elements, so what ships is a plain `<button>` with native focus, forms, and accessibility intact, plus a `data-component` stamp saying where it came from.

## The pieces, at a glance

Declarative HTML Components is one specification, in chapters that each define part of the component model. In plain terms:

| Chapter | In plain terms |
| --- | --- |
| [Components](/html-next/components) | Define a reusable tag with `<template component>`. Its interface (props) and non-visual declarations live in a `<defs>` region; below that is the markup it renders. |
| [Templating](/html-next/templating) | Control flow as attributes that survive the HTML parser: `$if` (show or not), `$each` (repeat), `$match` (pick one), `$value`/`$html` (output text or safe markup). |
| [Expressions](/html-next/expressions) | A small, typed, no-JavaScript expression language for the values in those attributes, with predictable rules for missing data and equality (it never throws). |
| [Bindings & events](/html-next/bindings) | Set values with `:attr`, two-way with `bind:`, react to events with `on:`, toggle a class or style with `class:`/`style:`. |
| [Reactivity](/html-next/reactivity) | Declare local `<state>`, derived `<computed>` values, and external `<data>` resources. Reads refetch and synchronized writes send according to their declared change policy. |
| [Types](/html-next/types) | Props default to strings but can borrow richer web-native types from CSS (`<length>`, `<color>`, enums, lists, structured JSON). |
| [Validation](/html-next/validation) | A declared type is a constraint: a typed prop or data value that fails its type is invalid, through the validity model [HTML Forms](/html-forms) extends to every element, and styled with the native `:user-invalid`. |
| [Style scoping](/html-next/styling) | A component's `<style>` applies to that component, using CSS `@scope`, scoping without the isolation cost of a shadow root. |
| [The JavaScript layer](/html-next/javascript) | The escape hatch. When behavior genuinely needs code (a timer, a chart library), a separate ES-module *controller* attaches to the component. Definitions stay script-free. |

## How it fits together

Two ideas hold the whole thing up:

- **Declarative by default, code only when needed.** Most of an interface, structure, data, styling, is markup with no script. Imperative JavaScript is a deliberate, separate layer you reach for only when there is no declarative way, and even then the component definition stays pure data.
- **Everything joins by tag.** A definition and, if it has one, a controller both register under the same tag name in a registry, the exact way the platform's own custom elements join a tag to a class. Nothing references anything else by file path; the tag is the join.

> [!note] Two ways to run it
> The same source has two honest execution paths: a **polyfill** that lowers it to native DOM in the browser today, and **converters** that compile it to idiomatic React, Vue, or Svelte. Both must produce the same observable result ([Targets & Equivalence](/html-next/targets)).

## How "done" is measured

The specification advances through **Levels**, as CSS specifications do: this draft is Level&nbsp;1, the shipping baseline, and features beyond it are marked for a later Level where they appear. A dated **Snapshot** records the draft on a given day. A feature is real when it is specified and has conformance tests, not when a number is announced.

## What is solid, and what is still open

Being plain also means being honest about maturity:

::: two

> [!ex] Solid today
> The component model, templating and control flow, the expression language and its value semantics, bindings, types, style scoping, and the shape of the JavaScript layer, all specified, and the browser-lowering and validation paths have a tested reference implementation.

> [!warn] Still open
> Live reactive updates in the browser (a later Level), real-time data (SSE/WebSocket), routing, demand-driven lazy loading gated on reactive state, and the full converter targets. These are named as open, not hidden ([details](/html-next/javascript)).

:::

## See it working

For complete, copy-pasteable code, one component, a component that uses another, and a JavaScript controller, see [Examples](/html-next/examples). Then read any chapter above for the precise rules.
