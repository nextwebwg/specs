---
title: Table and list layout
order: 1
blurb: participation · grids · shadow DOM · APIs
sectionNav: true
eyebrow: Flexible HTML Nesting · proposed rendering contract
status: "Unofficial Editor's Draft · Stage 0"
---

# Table and list layout

The browser discovers native parts in eligible wrappers as those parts become available. The browser preserves the DOM, derives a participation structure, and then applies CSS box generation and native table or list algorithms.

## Three structures, three jobs

| Structure | Purpose | Effect of an eligible transparent wrapper |
| --- | --- | --- |
| DOM and shadow trees | Node ownership, selectors, event paths, script access. | Preserve the wrapper and shadow boundaries. |
| Structural participation | Associate native row groups, rows, cells, and list items with their structural owner. | Infer permitted native parts from composed wrapper content. |
| CSS box tree | Sizing, grid placement, painting, and fragmentation. | Default to a boxless wrapper at eligible positions; honor author overrides and CSS table fixup. |

These structures are related, not interchangeable. A row supplied through a wrapper is not reparented in the DOM merely because it participates in a table's layout. A closed shadow root remains closed to outside script.

## A worked table

```html
<!DOCTYPE html PUBLIC "flexible-nesting">
<table>
  <tbody>
    <div>
      <tr><th scope="row">Ada</th><td rowspan="2">Editors</td></tr>
      <tr><th scope="row">Grace</th></tr>
    </div>
  </tbody>
</table>
```

For this proposed example, the proposed reasoning is:

1. Preserve `table → tbody → div → tr` in the DOM. The two rows remain children of the div.
2. The `tbody` owner discovers the div’s two native rows, in order.
3. Under each row, native `th` and `td` elements supply the cells. An eligible wrapper inside a row would be traversed at that level.
4. The wrapper supplies no row-group boundary. Both rows remain in the one native `tbody` group.
5. Apply the native table grid algorithm to those rows and cells. The `rowspan="2"` cell occupies the second column in both rows; the wrapper does not reset its span.
6. Apply CSS table layout to the generated table boxes. Intrinsic sizes come from the actual cell content; the wrapper does not become a spare cell or a second table in the default case.

The same default result is proposed whether the two rows are light children of a div or composed children supplied by an eligible component host. That equivalence is a proposed test obligation, not an implemented result.

## Native context determines participation

A wrapper under a table can supply native sections or rows. A wrapper within a section can supply rows, and one within a row can supply cells. The wrapper itself does not impersonate a native row or cell.

At table level, consecutive participating rows outside an explicit section form an implicit row group for table-model processing. The parser's required implied-`tbody` DOM behavior needs a coordinated algorithm; an implementation must not create different hidden groups depending on upgrade timing. Explicit native sections retain their boundaries and ordering rules. A nested table owns its own rows and cells and is never traversed as a wrapper of its outer table.

Spans use native `rowspan` and `colspan` parsing, including native zero-rowspan and row-group limits. A wrapper cannot let a cell span through another native row group or allocate an arbitrary column outside the native grid rules. Column sizing, `table-layout`, border collapse, caption placement, writing modes, and fragmentation keep their CSS table behavior after participation and box generation.[^1][^2]

Native `caption`, `colgroup`, and `col` retain their existing rules. This initial relaxation does not wrap those categories. The proposal is not an arbitrary descendant search for table-looking content.

## CSS and the wrapper's own box

The candidate user-agent rendering rule gives a valid participating wrapper `display: contents` in its structural position when its composed output qualifies. Empty wrappers qualify and supply no parts; incompatible output restores the ordinary user-agent display default. This classification is derived from native structure, not from computed style, avoiding a style/classification dependency loop. It creates no principal box by default. Its background, border, padding, and width therefore do not paint or size a wrapper box; inherited styles and rules targeting its descendants still apply.[^3]

An author can override that display value. A nontransparent wrapper box then participates through the existing CSS table fixup rules, including anonymous boxes where required. The browser must not discard a requested block, flex, or grid box to force the transparent result. Consequently the wrapped native rows are not guaranteed to occupy the outer table's grid under such an override. That is an explicit layout choice, not a second parser grammar.

A wrapper with mixed or invalid supplied content falls back to an ordinary wrapper box for layout. The browser must preserve that content rather than dropping it to make the table appear well-formed. That output does not qualify for transparent participation. Exact fallback interaction with table fixup and parser recovery is required prototype work.

`display: none`, `hidden`, visibility, containment, and protected-container behavior still apply. Structural traversal is not permission to render suppressed content or bypass inertness. Hidden native parts can retain HTML ownership while generating no layout boxes, as other DOM and CSS differences already allow.

Selectors and inheritance follow the actual DOM and CSS scoping rules. `table > tr` does not match through a wrapper. Layout transparency does not imply selector transparency.

## Shadow DOM and slots

```html
<table>
  <tbody>
    <user-rows>
      <template shadowrootmode="open">
        <tr><td>Shadow-provided row</td></tr>
      </template>
    </user-rows>
  </tbody>
</table>
```

This is proposed source, not a current-browser compatibility example. Declarative shadow-root parsing must preserve the native row in its table context; existing string parsing APIs do not automatically gain that context.

The parser preserves the eligible host before registration; rendering later inspects actual composed output. When shadow content exists, its composed children supply the actual native parts. Assigned slot nodes participate at the slot, once; fallback participates only while the slot is unassigned. A nested eligible wrapper in the same structural context can continue the traversal, but an ineligible boundary or nested native table/list is a boundary.

The renderer can inspect closed roots internally without returning their nodes to outside script. Shadow ownership, event retargeting, CSS scoping, and slot assignment remain intact. An invalid shadow output does not cause the browser to borrow hidden light children or synthesize rows from text.

A runtime component can construct native `tr` and `td` nodes using DOM methods. Setting a shadow root's legacy `innerHTML` does not request this profile and is not promised to parse row source correctly in a generic host context. Any explicit profile-aware parsing API requires separate design.

## DOM APIs and encapsulation

The proposed initial API choice preserves existing DOM-based table collections and mutations. `table.rows`, section `rows`, row `cells`, `rowIndex`, `sectionRowIndex`, `cellIndex`, `insertRow`, `deleteRow`, `insertCell`, and `deleteCell` keep their native DOM rules. They are not redefined to traverse wrappers or expose nodes in shadow roots.[^1]

This has a visible cost: a participating row through a wrapper or shadow host may affect the rendered grid without appearing in the outer table's `rows` collection. A light-DOM row under a generic wrapper can therefore have `rowIndex === -1`; closed-root rows remain inaccessible. Authors cannot treat the existing collection as a complete list of composed rendered rows.

This is an explicit proposal choice for review, not an assertion that the tradeoff is settled. A new structural inspection API, or revised light-DOM collections, would need a separate compatibility and encapsulation contract. No API may reveal a closed-root node merely because it participates in layout.

## Lists and numbering

The same traversal gives a `ul` or `ol` an ordered sequence of native participating `li` nodes. Wrappers add no list items. Nested native lists start separate ownership and counter sequences.

For an `ol`, native `start`, `reversed`, and `li[value]` determine item ordinals over that sequence. With `reversed` and no explicit start, count the participating list items, not the number of wrapper hosts. Update numbering when slot assignment or participating children change. Explicit author counter styles retain their CSS effects; list ownership alone does not override arbitrary counter declarations.

A component that supplies three native `li` nodes contributes three items. A component that paints three visually similar boxes but supplies no native list items contributes none. The inference does not automatically manufacture list semantics for arbitrary widgets.

## Dynamic changes and accessibility

Insertion, removal, reordering, slot reassignment, shadow attachment, and relevant CSS changes invalidate the affected owner's participation or box tree. Recompute before the next layout/paint and when a synchronous layout read requires it. Parser recognition never depends on these later changes. Later layout changes do not change the parsing profile or reparse source.

The accessible table must associate participating rows and cells with the same native table and header relationships used by the HTML table model. Accessible lists must expose participating item order and count without adding an item for a transparent wrapper. Existing explicit roles, names, and interaction on wrappers must not be silently erased. A wrapper with conflicting native or explicit semantics needs an eligibility restriction or a defined accessible mapping before adoption; that part is unresolved.

Screen-reader navigation, keyboard focus, header association, closed-root encapsulation, and updates after slot changes require native implementation and assistive-technology tests. A visually aligned grid alone is insufficient evidence.

## Required comparison cases

| Case | Required result or explicit boundary |
| --- | --- |
| Same rows unwrapped, light-wrapped, or shadow-supplied | Same default grid, span placement, and cell sizing. |
| Wrapper inside one row group | Wrapper adds no new span boundary. |
| Nested native table | Inner cells never join the outer grid. |
| Slots, fallback, and reassignment | Each composed part participates once; layout updates. |
| Closed shadow root | Layout works without exposing internal nodes through table collections. |
| Wrapper `display: block` or `grid` override | Preserve the requested box and use CSS fixup; do not promise a transparent outer grid. |
| Hidden, inert, or closed protected ancestor | No escape from its visibility, interaction, or ownership boundary. |
| Ordered list with `start`, `reversed`, and item values | Number participating native items, including supplied items, in the inferred sequence. |
| Mixed or incompatible content | No invented roles or dropped content; use the stated fallback and report nonconformance. |

The [proposal and evidence plan](/flexible-html-nesting/#evidence-and-safety-obligations) separates this proposed contract from the current parser baseline. No native layout conformance result is claimed.

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [table model](https://html.spec.whatwg.org/multipage/tables.html#processing-model-1) and [table DOM interfaces](https://html.spec.whatwg.org/multipage/tables.html#the-table-element).
[^2]: CSS Tables Level 3, [table structure, fixup, and layout](https://drafts.csswg.org/css-tables-3/). This evolving CSS draft is cited for the model and review surface, not as an implementation guarantee.
[^3]: CSS Display, [box generation](https://drafts.csswg.org/css-display/#box-generation).
:::
