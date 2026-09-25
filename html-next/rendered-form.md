---
title: Rendered Form & Hydration
order: 4.5
blurb: server markup that rebuilds the same instance
eyebrow: Declarative HTML Components Level 1
status: Level 1 · experimental in the reference implementation
---

# Rendered form & hydration

Lowering replaces an invocation with its native root, so after a server round trip only the lowered markup remains. The **rendered form** is that markup, defined precisely enough that server output plus the definition rebuilds **the same component instance** the authored markup would, using constructs already on the web platform's standards track.

## Two forms of one instance

A component instance can be written two ways. The **authored form** is the invocation a consumer writes. The **rendered form** is the lowered native DOM: the runtime leaves it in the document, and a server sends it to the browser.

```html
<!-- authored form: what a consumer writes -->
<x-card tone="warn">
  <b slot="title">Quarterly report</b>
  Body text
</x-card>
```

```html
<!-- rendered form: the lowered native DOM, as a server sends it -->
<article data-component="x-card" data-tone="warn">
  <header><?start slot="title"?><b slot="title">Quarterly report</b><?end?></header>
  <div><?start slot=""?>Body text<?end?></div>
</article>
```

Template output and projected content share one light-DOM tree (see [Components](/html-next/components)), so the rendered form must say where each slot's content begins and ends. Adjacent text is the forcing case: ` Hello  ` from a template followed by projected `world` serializes as `Hello world` and parses back as a single text node.

## The requirement: the same instance

A rendered form plus the definition [must]{.kw} build the same instance that the authored form plus the definition builds: the same prop values and the same set of *explicit* props, the same projected nodes for every slot (including slots not currently rendered), and the same state. The same later change, whether a prop write, a handler or controller changing state, or a new `$each` row, then produces the same DOM in both.

> [!note] Content no slot renders is part of the instance
> An instance holds projected content that no slot renders yet. Recovering the markup that is visible, and nothing else, would build a different instance, one that shows fallback where the authored one shows the consumer's content.

## Slot ranges

Every rendered slot is delimited by processing instructions:

```html
<?start slot=""?>…<?end?>                    <!-- default slot -->
<?start slot="title"?>…<?end?>               <!-- named slot -->
<?start slot="title" fallback=""?>…<?end?>   <!-- slot showing its fallback -->
<?marker slot="title"?>                      <!-- slot rendered empty, no fallback -->
<?carrier?><template>…</template>            <!-- carrier for content no slot renders -->
```

- Attributes use the platform's pseudo-attribute syntax: quoted `name="value"` pairs. A bare attribute is a parse error that leaves the instruction with no attributes at all, so the default slot is written `slot=""`.[^2][^3]
- A `start` or `marker` is a component mark only when it carries `slot`. Every `start` pairs with the nearest following unpaired `end` among its siblings, so a page's own partial-update ranges nest inside slot content without interfering.[^4]
- Processing instructions are invisible to CSS: `:empty`, `:first-child`, `>`, and `+` behave exactly as if the marks were absent.[^7] They do not change layout, the accessibility tree, `legend`/`summary`/`caption` positions, or form submission, and they survive parsing inside tables and `select`.
- Where a parser does not yet produce `ProcessingInstruction` nodes, the same text becomes a comment whose data is `?target data?`. Readers accept that form, and in those documents the runtime writes the comment the parser would, so lowered and hydrated DOM hold the same nodes.[^1]

## Content no slot renders yet

A slot under a false `$if`, content for an `$each` row that does not exist yet, or a slot whose name is computed from state: the instance holds that content, and a later change can render it.

```html
<!-- definition -->
<template component="x-disclosure">
  <defs>
    <state name="open" :value="false"></state>
    <handler name="toggle"><set name="open" :value="not open"></set></handler>
  </defs>
  <div>
    <button type="button" on:click="toggle">More</button>
    <section $if="open"><slot name="details"></slot></section>
    <slot></slot>
  </div>
</template>

<!-- invocation -->
<x-disclosure><p slot="details">Shown after the click.</p>Summary</x-disclosure>
```

Serialization appends an inert `<template>` to each component root that has such content. This **carrier** exists only in serialized output, the way `getHTML({ serializableShadowRoots })` writes a `<template shadowrootmode>` the live DOM does not hold.[^6] The lowered live DOM never contains it, and hydration removes it.

```html
<!-- rendered form, as serialized: the carrier holds what no slot renders yet -->
<div data-component="x-disclosure">
  <button type="button">More</button>
  <?start slot=""?>Summary<?end?>
  <?carrier?><template><p slot="details">Shown after the click.</p></template>
</div>
```

The carrier is marked by a `<?carrier?>` instruction immediately before it, read the same way as the slot marks, including the comment form where processing instructions are not parsed. Only the component root carries a component marker, and a component's own template may contain a `<template>` element, so position alone cannot identify the carrier. Qwik keeps unprojected content for the same reason.[^9]

## How hydration rebuilds the instance

1. Read explicit props from the root's `data-<name>` attributes.
2. Collect the root's own slot ranges in document order: its subtree, minus its own ranges' contents (consumer content), minus nested components' own regions, plus the contents of nested components' ranges (what this component projected into them).
3. The projected nodes are the contents of every range without `fallback`, each assigned that range's slot, followed by the carrier's nodes, which keep their own `slot` attribute. The carrier is removed.
4. Walk the template against the existing DOM. Each rendered slot adopts the next range whole: its marks, and either the projected nodes or the fallback nodes, adopted in place so their bindings attach.
5. A nested component's server-rendered root is adopted, not re-rendered. The outer template's nodes inside it are matched against that component's slot ranges and carrier, where lowering placed them, and the nested root hydrates as its own instance.

A root that a framework rendered is owned by that framework, which hydrates from its own state. Framework output need not carry slot ranges; its element tree remains subject to [target equivalence](/html-next/targets).

## Open questions

- **Explicit props a template binds.** When a template binds `data-<name>` for one of its own props, the rendered form cannot distinguish an explicit prop from its default, and an explicit prop is controlling. Either `data-<prop>` is reserved for the record, or explicitness is recorded separately.
- **Structural anchors.** `$if`, `$each`, and `$match` regions should use the same range grammar.
- **Consumer attributes.** Merge rules for `class` and `style` between template and consumer are unspecified, so their origin cannot be recovered.
- **Vendor support.** Chrome parses processing instructions in HTML; Gecko and WebKit have not yet taken a position.[^8] The comment form keeps the design working everywhere in the meantime.

## References

[^1]: WHATWG HTML, [Parse processing instructions in HTML (whatwg/html#12118)](https://github.com/whatwg/html/pull/12118): `<?target data?>` becomes a `ProcessingInstruction` node instead of a bogus comment; the target begins with an ASCII letter, so `<?/slot?>` remains a comment. Chrome: [Intent to Prototype](http://www.mail-archive.com/blink-dev@chromium.org/msg15714.html), [Intent to Experiment](http://www.mail-archive.com/blink-dev@chromium.org/msg16220.html) (origin trial 148 to 150).
[^2]: WHATWG DOM, [attributes on ProcessingInstruction (whatwg/dom#1454)](https://github.com/whatwg/dom/pull/1454), merged June 2026: `getAttribute`, `setAttribute`, `hasAttribute`, `removeAttribute`, `toggleAttribute`, parsed from the data.
[^3]: W3C, [Associating Style Sheets with XML documents](https://www.w3.org/TR/xml-stylesheet/): the rules for parsing pseudo-attributes that DOM applies to a processing instruction's data (quoted values, no duplicates, any error leaves no attributes).
[^4]: WICG, [Declarative Partial Updates](https://github.com/WICG/declarative-partial-updates/blob/main/patching-explainer.md): the `start`, `end`, and `marker` processing-instruction vocabulary for ranges.
[^5]: WICG, [DOM Parts, declarative syntax (webcomponents#1003)](https://github.com/WICG/webcomponents/issues/1003): processing-instruction ranges for locating nodes of interest during server rendering and updates.
[^6]: WHATWG HTML, [`getHTML()`](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#dom-element-gethtml) with `serializableShadowRoots`, and [`<template shadowrootmode>`](https://html.spec.whatwg.org/multipage/scripting.html#attr-template-shadowrootmode): a serialized form holding structure the live DOM does not, consumed by the parser.
[^7]: W3C, [Selectors Level 4, `:empty`](https://www.w3.org/TR/selectors-4/#the-empty-pseudo): comments and processing instructions do not affect emptiness.
[^8]: Standards positions on processing instructions in HTML: [Mozilla #1369](https://github.com/mozilla/standards-positions/issues/1369), [WebKit #628](https://github.com/WebKit/standards-positions/issues/628) (both open).
[^9]: Prior art: [Qwik projection](https://qwik.builder.io/docs/components/projection/) keeps projected content that is not currently rendered, because it may be projected later.
