---
title: Self-closing HTML
eyebrow: HTML Next · independent proposal
status: "Unofficial Editor's Draft · Stage 0 · Editor: [Matthew Dean](https://github.com/matthew-dean)"
pager: false
---

# Self-closing HTML

Let browsers accept `<div />` as shorthand for `<div></div>`. Closing an empty element where it starts is an obvious authoring convenience. This proposal adds `/>` as optional syntax sugar, with the same elements and behavior in the Document Object Model (DOM).

## The proposal

Use one spelling for an element with no authored children, whether it is an ordinary HTML element, a custom element, or a void element.

| Source | Equivalent HTML |
| --- | --- |
| `<div />` | `<div></div>` |
| `<span class="marker" />` | `<span class="marker"></span>` |
| `<user-avatar />` | `<user-avatar></user-avatar>` |
| `<br />` | `<br>` |
| `<link />` | `<link>` |
| `<input name="query" />` | `<input name="query">` |

For an ordinary element, the shorthand means a start tag immediately followed by its matching end tag. For a **void element**, such as `br`, `link`, or `input`, it means the existing start tag alone. In particular, `<br />` becomes `<br>`, never `<br></br>`.[^1]

The request is to incubate this rule for browser HTML parsing, including document and fragment parsing. Review should establish a safe compatibility path and precise parser behavior before any adoption. This is an independent Stage 0 proposal, not a W3C or WHATWG deliverable or a claim of native browser support.

## Void elements are an explicit allowlist

Only names in the HTML void-element allowlist have no end tag; all other HTML element names use tag pairs by default.

The allowlist for conforming HTML is the HTML Standard's existing set:[^1]

`area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.

Match these names ASCII-case-insensitively in the HTML namespace. For a listed name, both `<name>` and `<name />` mean the start tag alone. The slash is optional and desugaring must not generate an end tag. Thus `<BR />` also means `<br>`, and neither spelling generates `</br>`.

For any name outside the allowlist, including custom and unknown element names, `<name />` means `<name></name>`. Without the slash, `<name>` is an opening tag. An empty content model or a registered custom-element definition does not add a name to the allowlist.

Existing optional-end-tag and legacy error-recovery rules remain in force. SVG and MathML retain their own foreign-content rules; this allowlist governs HTML elements.

## Why this should be simple

An author can see that an element is empty without repeating its name in an end tag.

```html
<section class="profile">
  <user-avatar name="Ada" />
  <div class="divider" />
  <input name="display-name" value="Ada" />
</section>
```

The same convention works for native elements and custom elements. Adding children later means expanding the shorthand into a normal pair of tags. The element's content model stays the same: a self-closed `div` can still receive children through DOM APIs, and self-closing syntax does not make a custom element void.

This proposal stands on its own. It requires neither a component framework nor the [Declarative HTML Components](/declarative-components/) proposal.

## Source sugar, ordinary DOM

The browser should produce the same result as parsing the expanded source in the same context.

```html title="Proposed source"
<div class="marker" /><p>Next sibling</p>
```

```html title="Equivalent HTML"
<div class="marker"></div><p>Next sibling</p>
```

There is no self-closing node type or persistent flag on the element. Attributes, DOM interfaces, CSS matching, accessibility semantics, and custom-element lifecycle behavior follow the expanded form. HTML serialization continues to use ordinary HTML: an empty `div` serializes with an end tag, and a `link` without one. Preserving the author's shorthand is a source-tool concern.

## Parsing rules

Recognize the shorthand where the tokenizer recognizes a self-closing start tag, then give it the effect of the expanded form.

- **Names outside the void-element allowlist:** process the equivalent start and matching end tags, preserving the surrounding parser context. Following source becomes subsequent content according to the usual tree-construction rules.
- **Names in the void-element allowlist:** process the start tag alone, with or without a trailing slash. Never synthesize an end tag.
- **Custom elements:** recognize the shorthand without waiting for a JavaScript definition. Registering or upgrading an element does not change how its source is parsed.
- **SVG and MathML:** preserve existing foreign-content parsing, including its namespace and integration-point rules.[^1]
- **Attributes:** preserve existing tokenization. `<div data-path=assets/ />` closes the element; `<div data-path=assets/>` has the unquoted attribute value `assets/` and does not use the shorthand. A slash inside an attribute value is still data.[^1]

The intended scope includes elements with special parsing rules. For example, `<script src="app.js" />` should behave as `<script src="app.js"></script>`, and `<textarea />` as `<textarea></textarea>`. Script execution, raw-text handling, template insertion modes, and elements such as `table`, `select`, `html`, `head`, and `body` need explicit algorithms and tests. The equivalence above is the design goal; this draft does not yet supply a complete tree-construction patch.

An implementation cannot achieve this by globally replacing strings or by rewriting the DOM after parsing. Those approaches cannot reliably distinguish markup from attribute values, comments, script text, and other parser contexts.

## Compatibility is the adoption question

Existing HTML parsers ignore the self-closing flag on most non-void HTML start tags and report a parse error.[^2] Consequently, this source changes meaning under the proposal:

```html
<div /><span>Following content</span>
```

Today, in a normal body context, the `span` becomes a child of the `div`. Under the proposal, the two are siblings. That difference is the benefit for new source and the compatibility risk for existing pages.

WHATWG HTML issue #721 already discusses this request and the risk of reinterpreting deployed markup.[^3] This proposal needs current compatibility evidence. Familiar syntax alone does not establish that changing existing parsing is safe.

> [!warn] Open for review
> Determine whether the rule can safely apply to existing HTML, or needs an explicit opt-in. If an opt-in is required, define it for both documents and fragment APIs, including `innerHTML`, before claiming interoperability. No opt-in spelling is selected in this draft.

Authors targeting current browsers should continue to send expanded tags for non-void HTML elements. Any build-time lowering must use a parser that understands the proposed syntax; a DOM-based runtime shim runs too late to recover the intended source structure reliably.

## Next steps

Incubation should turn the short authoring rule into a testable browser change.

1. Measure deployed uses of trailing slashes on non-void elements, including cases that depend on today's nesting or raw-text behavior.
2. Resolve the compatibility boundary and specify document and fragment parsing together.
3. Write web-platform tests for siblings, quoted and unquoted attributes, custom elements, raw-text elements, templates, tables, foreign content, and HTML serialization.
4. Seek browser implementer review alongside the existing WHATWG discussion.
{.algo}

Discuss the rule and its compatibility path in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## References

[^1]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags): void elements, foreign elements, and the boundary between an unquoted attribute value and a trailing slash.
[^2]: WHATWG HTML, [non-void HTML element start tag with trailing solidus](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^3]: WHATWG HTML, [issue #721: HTML should support self-closing tags in general](https://github.com/whatwg/html/issues/721), including discussion of compatibility and custom elements.
