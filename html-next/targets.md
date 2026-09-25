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

This is what makes "many backends" trustworthy: pick any two targets and their output must be the **same program**, observably. Two executions are equivalent when their lowered native roots share:

- the same namespace and tag name;
- the same effective attributes (order-independent);
- the same assigned property values for explicit property bindings;
- equivalent child order, text, and identity;
- the same native focus, form, and accessibility semantics; and
- the same validation failures for invalid source.

Hydration markers and development-only attributes are excluded from the comparison, but an adapter [must not]{.kw} add semantic wrapper elements.

> [!ex] CLI
> ```bash
> html-next build button.html --out-dir dist
> ```

Next: see a full source in [Examples](/html-next/examples), or how targets fit the component model in the [Overview](/html-next/overview). {.lede}
