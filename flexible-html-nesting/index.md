---
title: Flexible HTML Nesting
order: -1
eyebrow: Independent HTML proposal
status: "Unofficial Editor's Draft · Stage 0"
sectionNav: true
---

# Flexible HTML Nesting

Keep ordinary wrappers and component hosts in constrained HTML contexts, and derive native structure from the parts they actually supply. Tables and lists are the first targets.

```html
<!DOCTYPE html PUBLIC "flexible-nesting">

<table>
  <tbody>
    <div class="people">
      <tr><td>Ada</td><td>Editor</td></tr>
    </div>
  </tbody>
</table>

<ul>
  <user-items></user-items>
</ul>
```

The proposed parser preserves the div at its authored position. The table discovers its native row through that wrapper. The list can discover native list items supplied later by `user-items`, including through its shadow tree. Neither wrapper needs a marker promising what will arrive.

> [!note] Status and scope
> This is a separate Stage 0 proposal. The inference model below is a candidate contract, not implemented browser behavior. Parser recovery, layout, DOM APIs, accessibility, and security need independent implementation and review. The self-closing proposal's proofs do not establish this proposal's safety.

## The problem has three parts

A table parser can move an unexpected element before the table. A list parser can preserve a wrapper even though the source does not satisfy the list's content model. Those are different problems: parsing, conformance, and layout must be addressed separately.[^1][^2]

Preserving a host also does not explain how rows or list items inside its shadow tree participate. CSS `display: contents` alone does not define table ownership, native span rules, list numbering, accessible structure, or DOM API behavior.[^3]

The proposal therefore combines:

1. Defined parser and content-model relaxations for eligible wrappers.
2. Structural inference from native elements in those wrappers' composed content.
3. A rendering and ownership contract for the inferred parts.

## Shared selection contract

[HTML Feature Profiles](/html-feature-profiles/) owns named selection, the `next` preset, support detection, dependencies, and precedence across HTML, CSS, JavaScript, and tools. This proposal's identifier is `flexible-nesting`.

```html
<!DOCTYPE html PUBLIC "self-closing, flexible-nesting">
```

The named list requests both capabilities. `<!DOCTYPE html PUBLIC "next">` instead requests the implementation's documented preset. Resolve and freeze the request for the parsing operation. Registration, styles, and later doctype mutation cannot switch it. The declaration fetches no DTD and does not enable XML.

The existing self-closing prototype does not implement named-list selection or flexible nesting. Existing string parsing APIs keep their current grammar. A document flag must not silently change a library's parsing behavior.

A server can also select this capability with the proposed `HTML-Feature-Profile` response header. [HTML Feature Profiles](/html-feature-profiles/#http-response-header) defines the header, its precedence over the doctype, and unsupported-request handling.

## Candidate contexts and wrappers

| Structural owner | Native parts it can accept through wrappers |
| --- | --- |
| `table` | Native row groups and rows, retaining the table's native section rules. |
| `thead`, `tbody`, `tfoot` | `tr` rows. |
| `tr` | `td` and `th` cells. |
| `ul`, `ol` | `li` list items. |

The initial candidate wrapper set is `div`, `span`, and autonomous custom-element hosts with valid custom-element names. This is a reviewable starting point, not a demonstrated safe or complete allowlist. Registration is irrelevant to eligibility; HTML's custom-element-name rules include reserved-name exclusions.[^4]

Native structural elements, text-sensitive elements, form controls, and protected containers do not become generic wrappers. The proposal must preserve hidden, inert, popover, template, and namespace boundaries. Exact eligibility and malformed-input recovery require independent security review.

Other constrained contexts, including `select`, need their own categories and interaction rules. Current customizable-select work must be considered rather than assuming an outdated option-only model.[^5]

## Preserve the wrapper before its content exists

Parsing cannot wait for a component definition or future output to decide where its host belongs. The proposed profile therefore recognizes eligible wrappers from source and preserves their authored position in the named structural contexts. Actual DOM parentage is visible before connected callbacks run.

Structural token dispatch uses the nearest native table or list context through the active eligible wrappers. Native row, section, cell, and list-item tokens retain their native meaning. The wrapper keeps its identity and attributes. A complete algorithm must coordinate stack clearing, implied `tbody` creation, optional end tags, wrapper closure, and surrounding native structure.

This draft does not yet replace every affected HTML insertion-mode algorithm. Required recovery traces include nested wrappers, mixed text, unmatched end tags, early table/list closure, end of input, namespace transitions, declarative shadow roots, and script-driven mutation. Simply disabling foster parenting or skipping wrappers in a stack operation is insufficient.

Examples use explicit paired tags. A self-closing host can later supply shadow content only when the separately selected self-closing capability applies. The combined selection needs its own checkpoint and ownership tests.

## Infer structure from the parts that arrive

A table or list can initially have no participating parts. When native parts appear, the browser discovers them and invalidates the affected layout and accessible structure. It does not wait indefinitely for registration and does not manufacture roles from a component's name.

For each structural owner, traverse composed children in order:

1. Accept the native parts permitted for this owner, using their actual node identities.
2. At an eligible generic wrapper, recursively inspect composed children for that owner's permitted parts.
3. A shadow host supplies its shadow tree's composed children. A slot supplies assigned nodes, or fallback children when unassigned. Count a node once at its composed position, not again at its light-DOM position.
4. Stop at a nested native structural owner, inert template content, a protected boundary, or an ineligible element. Do not search arbitrary descendants for matching names.
5. An empty wrapper supplies no part yet. If its contents consist only of permitted parts, eligible wrappers, ignorable whitespace, and nonparticipating metadata, it is structurally transparent for that owner. Nonparticipating metadata means comments and inert template declarations; scripts retain their specified execution and are not reinterpreted as structural content.
6. Non-whitespace text or a mismatched element does not acquire a native role. A mixed-content wrapper is not transparent: preserve it as an ordinary layout boundary and apply native box fixup rather than silently dropping its contents.

This is contextual inference: a div under a row can supply cells; a div under a list can supply list items. It is not inference from visual resemblance or from a JavaScript class. A component that renders generic boxes supplies no native `tr` or `li` just because those boxes look like rows or items.

A required author marker is not part of this candidate design. A future declarative role hint could be evaluated if inference proves ambiguous or costly, but it cannot replace checking actual parts or protecting ownership boundaries.

## Shadow DOM and changing output

A component may start empty, upgrade, attach a shadow root, or change slot assignments. Recompute structural participation as content changes. Rendering may inspect closed roots internally without returning their nodes to outside script; shadow ownership, event retargeting, and CSS scoping remain intact.

```html
<ul>
  <user-items>
    <template shadowrootmode="open">
      <li>Ada</li>
      <li>Grace</li>
    </template>
  </user-items>
</ul>
```

This proposed list owns two participating native items, while the host remains in the DOM. A nested `ul` or `ol` owns its own items. A component with mixed incompatible output falls back to an ordinary layout boundary; content is not discarded to produce a convenient structure.

[Read the table and list layout contract →](/flexible-html-nesting/layout)

## Evidence and safety obligations

The [baseline evidence](https://github.com/nextwebwg/specs/tree/main/flexible-html-nesting/evidence) records ordinary parse5 8.0.1 behavior for custom and ordinary wrappers in tables and lists. The proposed-marker baseline is retained as a historical control: an unknown attribute did not itself change parsing. It does not justify requiring that marker. The pinned parser is not evidence about all current HTML behavior, especially select parsing.

No native flexible-nesting implementation or safety proof is reported. Changing recognition requires its own argument; the self-closing projection theorem assumes ordinarily recognized input and cannot be transferred to this parser change.

Required work includes sanitizer mismatches, text and namespace boundaries, protected containment, parser pauses, reactions, mutation, encoding restarts, speculative loading, serialization, and combined-profile behavior. Layout tests must cover empty and late content, mixed-content fallback, table spans and sizing, list numbering, slots, nested owners, closed-root encapsulation, keyboard behavior, and accessible structure.

## Review requested

Feedback is requested on source-preserved wrappers, inference from actual composed content, the initial wrapper/context sets, parser recovery, and the layout and API tradeoffs. Concrete counterexamples belong in the [specifications repository](https://github.com/nextwebwg/specs/issues).

Editor: [Matthew Dean](https://github.com/matthew-dean). Independent Stage 0 proposal; not a W3C or WHATWG deliverable.

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [in-table insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-intable) and [unexpected markup in tables](https://html.spec.whatwg.org/multipage/parsing.html#unexpected-markup-in-tables).
[^2]: WHATWG HTML, [the ul element](https://html.spec.whatwg.org/multipage/grouping-content.html#the-ul-element) and [the ol element](https://html.spec.whatwg.org/multipage/grouping-content.html#the-ol-element).
[^3]: CSS Display, [box generation](https://drafts.csswg.org/css-display/#box-generation).
[^4]: WHATWG HTML, [valid custom element names and core concepts](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-elements-core-concepts).
[^5]: WHATWG HTML, [the select element](https://html.spec.whatwg.org/multipage/form-elements.html#the-select-element).
:::
