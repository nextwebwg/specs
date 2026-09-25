---
title: Examples
order: 12
blurb: complete, copy-pasteable code
navGroup: guide
eyebrow: Reference
status: Illustrative · pairs with the runnable proof of concept
---

# Examples

Complete, copy-pasteable code for the common shapes, a plain component, control flow, a stateful component with a controller, and a graph of components that load lazily. Everything here is runnable: the same set is a live, unbundled demo in the reference repository.

## A minimal component

One prop, one native root, a scoped style. It lowers to a real `<button>`, no wrapper, no shadow root, with a `data-component` provenance stamp.

```html title="button.html"
<!-- button.html — a minimal component: one prop, one native root, scoped style. -->
<template component="x-button">
  <defs>
    <prop name="variant" type="outline | solid" default="outline">Visual treatment.</prop>
  </defs>
  <button><slot></slot></button>
  <style>
    :host { font: inherit; }
    :host-state([variant="solid"]) { background: CanvasText; color: Canvas; }
  </style>
</template>

<!-- use -->
<x-button variant="solid">Save</x-button>
<!-- lowers to -->
<button data-component="x-button" data-variant="solid">Save</button>
```

## Control flow, as attributes

Structural `$`-directives ride on ordinary elements (or a `<template>`), so they survive restrictive parser contexts like `<table>` and `<select>`. Iteration shaping (`$where`, `$sort`, `$limit`, `$key`) lives on the loop. See [Templating](/html-next/templating).

```html
<!-- templating: a filtered, sorted list and a three-way status, all as directives -->
<ul>
  <li $each="p of products" $where="p.inStock" $sort="price,-name" $key="p.id">
    <value of="p.price" format="currency" currency="USD"></value> — <span $value="p.name"></span>
  </li>
</ul>

<template $match="order.status as s">
  <p $when="s = 'pending'">Working…</p>
  <p $when="s = 'error'">Something went wrong.</p>
  <p $else>Done.</p>
</template>
```

## A stateful component, with a controller

The definition declares `<state>`, exposes a `$ref`, and names its controller on the carrier with `controller="./counter.js"`. The module loads lazily when the first instance connects; its default export receives the instance host and drives state while the runtime reflects state to the DOM. It needs no library import or repeated tag registration. Importing the component means trusting that declared dependency graph under the application's loading policy. See [The JavaScript Layer](/html-next/javascript).

::: two

```html title="counter.html"
<!-- counter.html — local state plus its optional controller module. -->
<template component="x-counter" controller="./counter.js">
  <defs>
    <prop name="start" type="number" default="0"></prop>
    <state name="count" :value="start"></state>
  </defs>
  <button $ref="btn" type="button">count: <span $value="count"></span></button>
</template>
```

```html title="counter.js"
// counter.js — the definition names this module; no library import is required.
export default function controller(host) {
  host.refs.btn.addEventListener("click", () => {
    // Drive STATE, never the DOM directly. The runtime reflects count to the <span>.
    host.state.count = host.state.count + 1;
  });
}
```

:::

> [!note] Integrating a foreign library
> The same shape wraps any imperative library: reach the element with a `$ref`, let the library own that (unbound) subtree, and re-run on data changes with `host.effect`.

::: two

```html title="chart.html"
<!-- chart.html — wraps a foreign drawing library through a $ref to a canvas. -->
<template component="x-chart" controller="./chart.js">
  <defs>
    <state name="bars" :value="[3, 7, 2, 5, 8, 4]"></state>
  </defs>
  <figure>
    <canvas $ref="surface" width="260" height="90" role="img" aria-label="chart"></canvas>
  </figure>
</template>
```

```html title="chart.js"
// chart.js — the library owns its own (unbound) canvas; an effect re-runs if data changes.
import { Chart } from "chart-lib";               // a bare specifier; the import map resolves it

export default function controller(host) {
  const chart = new Chart(host.refs.surface, { data: host.state.bars });
  host.effect(() => chart.update(host.state.bars));
  host.on("disconnect", () => chart.destroy());
}
```

:::

## A graph of components

A component declares its own component and controller dependencies; the page imports one concrete root and the complete graph remains statically discoverable. A package build resolves that graph through package exports. A live application resolves trusted URL prefixes through its own import map and CSP. The definitions are identical in both cases. See [the composition model](/html-next/javascript).

```html title="app.html"
<!-- app.html — purely declarative composition. It declares ONLY the components it uses;
     the graph composes transitively, like an ES-module graph. No controller, no <script>. -->
<link rel="component" href="./counter.html">
<link rel="component" href="./chart.html">

<template component="x-app">
  <defs>
    <prop name="title" type="string" default="App"></prop>
  </defs>
  <main>
    <h1 $value="title"></h1>
    <x-counter start="3"></x-counter>
    <x-chart></x-chart>
  </main>
</template>
```

```html title="index.html"
<!doctype html>
<link rel="component" href="/components/app.html">
<script type="importmap">                            <!-- ordinary unbundled JS dependencies -->
{
  "imports": {
    "chart-lib": "/vendor/chart-lib.js"
  }
}
</script>
<script type="module" src="/htmlnext.js"></script>

<x-app title="Dashboard"></x-app>
```

## Run it yourself

This exact example, a base `index.html`, component definitions as `.html` files, controllers as `.js` modules, and a small runtime, is a complete, unbundled, runnable demo at `examples/poc/` in the [`html-next` implementation repository](https://github.com/nextwebwg/html-next). Serve that directory with any static server and open it: the counter increments and the chart draws, with no build step.

> [!note] Proof of concept, honestly scoped
> The demo proves composition, definition-owned controller binding, and lazy controller loading end to end. It is deliberately simplified in places (eager definition loading, coarse reactivity, no SSR); its README says exactly what is demonstrated versus deferred.
