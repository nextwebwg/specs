---
title: Targets & Equivalence
order: 10
blurb: generators · observable equivalence
eyebrow: Declarative HTML Components Level 1
status: Level 1 · reference implementation in progress
---

# Targets & observable equivalence

One source, many backends. Every generator lowers the same HTML Next source to a different target, and a single **equivalence contract** defines when two of those outputs are considered the same program.

## What every generator must do

Whatever the target, a generator turns one HTML Next source into that target's idiom while keeping the same observable behaviour. Concretely, every generator [must]{.kw}:

- use the contract's PascalCase name for the exported component;
- preserve the native root element;
- pass through native consumer attributes;
- apply the contract's declared defaults;
- serialize each prop to its target per the contract;
- project children into the default slot;
- import or reference the generated CSS exactly once; and
- produce deterministic output for deterministic input.

CSS output includes the component's transitive [`@import` dependencies](/declarative-components/styling#shared-css). Every target [must]{.kw} preserve imported rules' component scope, cascade order, conditions, layers, and source-relative assets, along with document-wide at-rule behavior. A target [may]{.kw} bundle or share CSS artifacts; it [must not]{.kw} turn component-owned imports into global styles or add stylesheet copies for each instance.

::: targets
Vanilla DOM
: ESM factory + .d.ts

React
: TSX, typed ref, no forwardRef

Vue
: <script setup> SFC

Svelte
: runes + svelte/elements

CSS
: scoped component styles

Docs
: Markdown API reference
:::

## The equivalence contract

Conversion requires an **identical user experience**. Each framework target uses its framework’s normal rendering, reconciliation and hydration behavior. Exact component lifecycle is not a conversion requirement.

Two executions are equivalent when their lowered native roots share:

- the same namespace and tag name;
- the same effective attributes (order-independent);
- the same assigned property values for explicit property bindings;
- equivalent visible child order and text;
- the same native focus, form, and accessibility semantics; and
- the same validation failures for invalid source.

Hydration markers and development-only attributes are excluded from the comparison, but an adapter [must not]{.kw} add semantic wrapper elements.

### Framework lifecycle {#framework-lifecycle}

A framework target [may]{.kw} create new DOM nodes or component instances during reconciliation, hydration or outlet changes, as its framework normally does. It does not have to reproduce the native implementation’s setup, mount, unmount or effect timing, or preserve exact DOM or framework instance identity. These internal differences are not conformance failures by themselves.

The user experience remains the requirement: rendered content and placement, interactions, focus, form behavior and accessibility must agree. Tests [must]{.kw} check those outcomes rather than require matching lifecycle counts, private ownership trees or object identity with no effect on the user.

Converters [should]{.kw} use supported framework primitives. An adapter [must not]{.kw} patch framework internals or introduce custom event or view-retention machinery solely to reproduce lifecycle mechanics that have no effect on the user. Integration code that addresses a demonstrated difference in user experience must preserve the framework’s normal event and rendering behavior.

> [!ex] CLI
> A generator's command line takes a source and an output directory, for example:
> ```bash
> component-build button.html --out-dir dist
> ```

Next: see a full source in [Examples](/declarative-components/examples), or how targets fit the component model in the [Overview](/declarative-components/overview). {.lede}
