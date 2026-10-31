---
title: Rendered Form & Hydration
order: 4.5
blurb: server markup that rebuilds the same instance
eyebrow: Declarative HTML Components Level 1
status: Level 1 · experimental in the reference implementation
---

# Rendered form & hydration

Lowering replaces an invocation with its native root, so after a server round trip only the lowered markup remains. The **rendered form** is that markup. It must let server output plus the definition rebuild **the same component instance** the authored markup would. Slot boundaries are specified below; the format for recovering explicit props is still open.

The root's `component` attribute identifies the components being hydrated. Polyfills also accept `data-component` under the [identity and compatibility rules](/declarative-components/components#component-identity): a present `component` takes precedence, even when empty, and adoption leaves the authored spelling in place. New serialized roots use `component` by default.

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
<!-- rendered form: visible slot structure; prop hydration data is not shown -->
<article component="x-card">
  <header><?start slot="title"?><b slot="title">Quarterly report</b><?end?></header>
  <div><?start slot=""?>Body text<?end?></div>
</article>
```

Template output and projected content share one light-DOM tree (see [Components](/declarative-components/components)), so the rendered form must say where each slot's content begins and ends. Adjacent text is the forcing case: ` Hello  ` from a template followed by projected `world` serializes as `Hello world` and parses back as a single text node.

## The requirement: the same instance

A rendered form plus the definition [must]{.kw} build the same instance that the authored form plus the definition builds: the same prop values and the same set of *explicit* props, the same projected nodes for every slot (including slots not currently rendered), and the same state. The same later change, whether a prop write, a handler or controller changing state, or a new `$each` row, then produces the same DOM in both.

For [shared state](/declarative-components/reactivity), this also means a hydrated reader must resolve to the same provider instance. Slot ranges recover which component received projected content. A portal can move a reader away from its provider in the serialized DOM, so the current rendered form does not yet specify enough to hydrate that relationship; the required owner record remains open below.

> [!note] Content no slot renders is part of the instance
> An instance holds projected content that no slot renders yet. Recovering the markup that is visible, and nothing else, would build a different instance, one that shows fallback where the authored one shows the consumer's content.

## Slot ranges

Every rendered slot is delimited by processing instructions:

```html
<?start slot=""?>…<?end?>                            <!-- default slot -->
<?start slot="title"?>…<?end?>                       <!-- named slot -->
<?start slot="title" fallback=""?>…<?end?>           <!-- slot showing its fallback -->
<?start slot="row" scoped=""?>…<?end?>               <!-- slot rendering a consumer's <template slot> -->
<?start slot="row" fallback="" scoped=""?>…<?end?>   <!-- slot with props showing its fallback -->
<?marker slot="title"?>                              <!-- slot rendered empty, no fallback -->
```

- Attributes use the platform's pseudo-attribute syntax: quoted `name="value"` pairs. A bare attribute is a parse error that leaves the instruction with no attributes at all, so the default slot is written `slot=""`.[^2][^3]
- A `start` or `marker` is a component mark only when it carries `slot`. Every `start` pairs with the nearest following unpaired `end` among its siblings, so a page's own partial-update ranges nest inside slot content without interfering.[^4]
- Processing instructions are invisible to CSS: `:empty`, `:first-child`, `>`, and `+` behave exactly as if the marks were absent.[^7] They do not change layout, the accessibility tree, `legend`/`summary`/`caption` positions, or form submission, and they survive parsing inside tables and `select`.
- Where a parser does not yet produce `ProcessingInstruction` nodes, the same text becomes a comment whose data is `?target data?`. Readers accept that form, and in those documents the runtime writes the comment the parser would, so lowered and hydrated DOM hold the same nodes.[^1]

### Outlets written as `<template $slot>` {#template-slot-outlets}

A definition may write an outlet as [`<template $slot>`](/declarative-components/components#parser-safe-outlets), the form the HTML parser keeps in table parts. Its rendered form is exactly the rendered form of the matching `<slot>`: the same marks around the same nodes, and no `<template>` element of its own. Server output does not record which form the definition used, and hydration does not need it: it walks the definition's outlets, written either way, against the ranges.

```html
<!-- definition -->
<template component="x-table"> …
  <table>
    <thead><tr><template $slot><th>Name</th></template></tr></thead>
    <tbody><template $slot="row" $each="row of $rows" from:item="$row"><tr><td>{$row}</td></tr></template></tbody>
  </table>
</template>

<!-- rendered form, as serialized: no consumer content, so each outlet shows its fallback -->
<table component="x-table">
  <thead><tr><?start slot="" fallback=""?><th>Name</th><?end?></tr></thead>
  <tbody><?start slot="row" fallback="" scoped=""?><tr><td>Ada</td></tr><?end?><?start slot="row" fallback="" scoped=""?><tr><td>Bea</td></tr><?end?></tbody>
</table>
```

The marks stay where the outlet rendered, because processing instructions, and the comment form, survive parsing inside table sections and rows. So does a [carrier](#content-no-slot-renders-yet): the parser keeps a `<template>` that is a child of a `<table>`.

## Content no slot renders yet

A slot under a false `$if`, content for an `$each` row that does not exist yet, or a slot whose name is computed from state: the instance holds that content, and a later change can render it.

```html
<!-- definition -->
<template component="x-disclosure">
  <defs>
    <state type="boolean" name="open" value="false"></state>
    <handler name="toggle"><set name="open" expr:value="not $open"></set></handler>
  </defs>
  <div>
    <button type="button" on:click="toggle">More</button>
    <section $if="$open"><slot name="details"></slot></section>
    <slot></slot>
  </div>
</template>

<!-- invocation -->
<x-disclosure><p slot="details">Shown after the click.</p>Summary</x-disclosure>
```

Serialization appends an inert `<template carrier>` to the component root for each component that has such content. This **carrier** exists only in serialized output, the way `getHTML({ serializableShadowRoots })` writes a `<template shadowrootmode>` the live DOM does not hold, and like that template it says in an attribute what it is for.[^6] The lowered live DOM never contains it, and hydration removes it.

```html
<!-- rendered form, as serialized: the carrier holds what no slot renders yet -->
<div component="x-disclosure">
  <button type="button">More</button>
  <?start slot=""?>Summary<?end?>
  <template carrier="x-disclosure"><p slot="details">Shown after the click.</p></template>
</div>
```

A carrier is a `<template>` child of the component root whose `carrier` attribute is the tag of the component that holds its content. Only the component root carries a component marker, and a component's own template may contain a `<template>` element, so position alone cannot identify the carrier; the attribute does. Qwik keeps unprojected content for the same reason.[^9]

Each projected node appears in exactly one carrier: that of the component whose consumer wrote it, since projected nodes keep their provenance. A component that forwards its own slot through an element it projects into another component, where that element is not rendered, leaves the element in the other component's carrier with the forwarding outlet's slot marks around an empty range. The consumer's node stays in the forwarding component's carrier, and the outlet renders it once its slot renders.

`carrier` on a `<template>` is reserved for the rendered form. A component definition whose markup writes it is invalid, reported with a diagnostic.

### Components that share a root {#shared-root-carriers}

A component whose markup root is another component's invocation lowers to that component's root, so the two share one element, listed outer to inner in its `component` value. Each holds its own projected content. Serialization appends one carrier for each of them that has content no slot renders, in the same outer-to-inner order, and hydration gives each carrier's nodes to the component it names:

```html
<!-- definition: x-relay forwards its scoped row slot to x-list's -->
<template component="x-relay"> …
  <x-list><template slot="row"><slot name="row" from:item="$item"></slot></template></x-list>
</template>

<!-- invocation -->
<x-relay><template slot="row"><b>{$item}</b></template></x-relay>

<!-- rendered form: x-list renders x-relay's template, which renders the consumer's -->
<ul component="x-relay x-list">
  <li><?start slot="row" scoped=""?><?start slot="row" scoped=""?><b>Ada</b><?end?><?end?></li>
  <template carrier="x-relay"><template slot="row">…</template></template>
  <template carrier="x-list"><template slot="row">…</template></template>
</ul>
```

## Conditional content in a slot

A consumer may write slot content under `$if` or `$each`. A slot whose only such content renders nothing shows its fallback, and switches to the content when it appears (see [Named & fallback](/declarative-components/components#named-fallback)). The instance still holds the region, so a later change can render into it. The rendered form keeps the region's marks in the slot's range, after its fallback nodes:

```html
<!-- invocation: the meta slot has content only while $open is true -->
<x-row><span slot="meta" $if="$open">Opened</span></x-row>

<!-- rendered form while $open is false: the fallback, then the empty region's marks -->
<span class="meta"><?start slot="meta" fallback=""?>No meta<!--if--><!--/if--><?end?></span>

<!-- after $open becomes true, the same range holds the content between the marks -->
<span class="meta"><?start slot="meta"?><!--if--><span slot="meta">Opened</span><!--/if--><?end?></span>
```

- A `fallback` range holds the slot's fallback nodes first. Hydration adopts them by walking the slot's fallback children; any nodes left in the range after them are the marks of the consumer's empty regions, and they are that slot's projected content.
- `<!--if-->` and `<!--/if-->` stand for the region's marks, which are the implementation's until structural anchors share the range grammar (an open question below).
- A native `<slot>` behaves the same way: it shows its own children while no node is assigned to it, and its assigned nodes once there are some.[^10]

## How hydration rebuilds the instance

1. Recover explicit props from the server-rendered instance's hydration data. The proposal has not fixed a wire format for that data; visible `data-<name>` attributes are not required.
2. Collect the root's own slot ranges in document order: its subtree, minus its own ranges' contents (consumer content), minus nested components' own regions, plus the contents of nested components' ranges (what this component projected into them).
3. The projected nodes are the contents of every range without `fallback` or `scoped`, each assigned that range's slot, then the marks of any consumer region that follow the fallback nodes in a `fallback` range (see [Conditional content in a slot](#conditional-content-in-a-slot)), assigned that range's slot, followed by the nodes of the carrier that names this component, which keep their own `slot` attribute. A consumer's [`<template slot>`](/declarative-components/components#content-that-renders-on-demand) is always in its receiving component's carrier: the live DOM holds what it renders, never the template. The carrier is removed.
4. Walk the template against the existing DOM. Each rendered slot, whether its outlet is a `<slot>` or a `<template $slot>`, adopts the next range whole: its marks, and either the projected nodes, the fallback nodes and any empty consumer regions after them, or the nodes its `<template slot>` rendered, adopted in place so their bindings attach. A forwarding outlet inside carried content adopts its marks and places its component's projected nodes between them.
5. A nested component's server-rendered root is adopted, not re-rendered. The outer template's nodes inside it are matched against that component's slot ranges and its carrier, where lowering placed them, and the nested root hydrates as its own instance.

A root that a framework rendered is owned by that framework, which hydrates from its own state. Framework output need not carry slot ranges; its element tree remains subject to [target equivalence](/declarative-components/targets).

## Open questions

- **Context through a server-rendered portal.** A deterministic record must connect each relocated reader to its logical component owner. DOM ancestry and `component` tag lineage cannot identify the providing instance when several instances share a tag.
- **Explicit prop recovery.** The rendered form needs the values and explicitness of props supplied to the invocation, including structured values. The hydration data format and how it is associated with the root remain open; ordinary visible attributes cannot be assumed to carry it.
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
[^10]: WHATWG DOM, [assigning slottables](https://dom.spec.whatwg.org/#assign-slotables); CSS Scoping, [slots and fallback content in the flat tree](https://drafts.csswg.org/css-scoping/#slots-in-shadow-tree).
