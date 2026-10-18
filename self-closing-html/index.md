---
title: Self-closing HTML
eyebrow: HTML Next · independent proposal
status: "Unofficial Editor's Draft · Stage 0 · Editor: [Matthew Dean](https://github.com/matthew-dean)"
pager: false
---

# Self-closing HTML

Let authors opt into self-closing HTML with `<!DOCTYPE html PUBLIC "next">`. In that document, `<div />` means `<div></div>`, and `<br />` still means `<br>`. HTML keeps its forgiving parsing rules and ordinary Document Object Model (DOM); the declaration explicitly selects the new tag interpretation.

## The proposal

Declare the parsing profile before the document's elements, then use one spelling for an element with no authored children.

```html title="Proposed HTML Next document"
<!DOCTYPE html PUBLIC "next">
<html lang="en">
  <head>
    <title>Profile</title>
  </head>
  <body>
    <user-avatar name="Ada" />
    <div class="divider" />
    <br />
  </body>
</html>
```

With the profile enabled, the source forms below have these equivalents:

| Source | Equivalent HTML |
| --- | --- |
| `<div />` | `<div></div>` |
| `<span class="marker" />` | `<span class="marker"></span>` |
| `<user-avatar />` | `<user-avatar></user-avatar>` |
| `<br />` | `<br>` |
| `<link />` | `<link>` |
| `<input name="query" />` | `<input name="query">` |

For an ordinary element, the shorthand means a start tag immediately followed by its matching end tag. For a **void element**, such as `br`, `link`, or `input`, it means the existing start tag alone. In particular, `<br />` becomes `<br>`, never `<br></br>`.[^1]

The request is to incubate the explicit profile declaration and its self-closing rule for document and fragment parsing. This is an independent Stage 0 proposal, not a W3C or WHATWG deliverable or a claim of native browser support.

## An explicit HTML Next parsing profile

`<!DOCTYPE html PUBLIC "next">` selects the proposed profile in a supporting HTML parser. Plain `<!DOCTYPE html>` keeps today's tag interpretation.

The declaration lets an author choose HTML's error recovery together with self-closing syntax. Documents remain `text/html`. Case-insensitive HTML names, boolean attributes, unquoted attribute values, optional tags, and recovery from malformed markup retain their HTML rules. The profile does not select XML parsing or require XML well-formedness.

HTML can gain self-closing syntax without adopting XML's strict parsing rules or changing how existing HTML documents are interpreted. The WHATWG discussion identifies the legacy-content problem and points to XML as an existing way to obtain self-closing syntax.[^3] This proposal addresses that compatibility objection by applying the new interpretation only to documents that explicitly declare `PUBLIC "next"`.

The discussion also raises an opt-in as a possible approach.[^3] This draft makes that route concrete: a named HTML parsing profile preserves HTML's error recovery while letting authors choose the new tag rule. XML is one existing path to self-closing syntax; an explicit HTML profile provides another proposed path.

The proposed activation rules are:

- The parser recognizes the declaration when processing the document's initial doctype, before element content. The doctype name is `html`, the public identifier is exactly the case-sensitive string `next`, and the system identifier is absent. Keywords and the doctype name retain HTML's case-insensitive matching.
- A recognized declaration selects the profile and standards rendering mode. Other doctypes and documents without this declaration retain existing parsing behavior.
- The selected profile is fixed for that parse. A later doctype, a DOM edit to the doctype, or registering a custom element cannot switch it.
- This draft defines the profile's self-closing rule. Selecting it does not implicitly enable the component, reactivity, or forms proposals in this collection.

### Why PUBLIC

`PUBLIC "next"` names a parsing profile built into the browser. It does not locate an external definition, fetch a document type definition (DTD), or enable DTD validation. The browser continues to use its HTML parser. Public identifiers historically name external definitions independently of their location; this proposal gives the identifier a new HTML-specific meaning.[^5]

The spelling also fits existing HTML tokenization. Under today's rules, `<!DOCTYPE html PUBLIC "next">` produces a parse error but still selects standards mode. Recognizing it as a conforming opt-in would be a standards change. Both `<!DOCTYPE html next>` and `<!DOCTYPE html-next>` instead trigger quirks mode today.[^6]

### Documents and fragments

The proposed propagation rule follows the document that supplies the parsing context:

- Context-based fragment parsing, including `innerHTML`, `outerHTML`, `insertAdjacentHTML()`, and `Range.createContextualFragment()`, uses the context document's selected profile. A doctype inside a fragment cannot select or change the profile.
- A separately parsed HTML document, including an iframe document or a document created by `DOMParser.parseFromString(..., "text/html")`, selects its own profile from its own declaration. It does not inherit the caller's profile.
- Moving existing DOM nodes between documents does not reparse them. Subsequent string parsing uses its destination context's profile.

These are proposed rules, not existing API behavior. Integrating them with template contents and their associated documents, shadow roots, document-writing APIs, and the full fragment-parsing algorithm requires an API-by-API specification and tests before adoption.[^6]

## Void elements are an explicit allowlist

Within the selected profile, only names in the HTML void-element allowlist have no end tag; all other HTML element names use tag pairs by default.

The allowlist for conforming HTML is the HTML Standard's existing set:[^1]

`area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.

Match these names ASCII-case-insensitively in the HTML namespace. For a listed name, both `<name>` and `<name />` mean the start tag alone. The slash is optional and desugaring must not generate an end tag. Thus `<BR />` also means `<br>`, and neither spelling generates `</br>`.

For any name outside the allowlist, including custom and unknown element names, `<name />` means `<name></name>`. Without the slash, `<name>` is an opening tag. An empty content model or a registered custom-element definition does not add a name to the allowlist.

Existing optional-end-tag and legacy error-recovery rules remain in force. SVG and MathML retain their own foreign-content rules; this allowlist governs HTML elements.

## Why authors want this

An author should be able to choose forgiving HTML parsing with a convention for empty elements already familiar from JSX and Vue templates.[^4] The document declaration makes that choice explicit.

```html
<section class="profile">
  <user-avatar name="Ada" />
  <div class="divider" />
  <input name="display-name" value="Ada" />
</section>
```

The benefits are concrete:

- **State intent at the point of use.** `<user-avatar />` says that this instance has no authored children. Repeating a long custom-element name in an adjacent end tag adds no information about that instance.
- **Remove a documented parsing surprise.** Vue's documentation explains that `<my-component />` works in its template parser, while native HTML parsing can make the following `span` a child of that component. Authors have to change the spelling when moving markup between those contexts.[^4] This proposal would remove that particular difference.
- **Use the same shorthand for native and custom elements.** An empty `div` and an empty `user-avatar` would follow the same authoring rule. The void-element allowlist keeps `br`, `link`, and other existing void elements working as they do today.
- **Support direct HTML authoring.** Native support would let authors use this shorthand in documents and fragments without requiring a build step solely to expand empty tags.

Adding children later means expanding the shorthand into a normal pair of tags. The element's content model stays the same: a self-closed `div` can still receive children through DOM APIs, and self-closing syntax does not make a custom element void.

The request also predates this proposal: WHATWG HTML issue #721 asks for general self-closing syntax and discusses both author expectations and compatibility.[^3] Together with the framework documentation, it records why the behavior is wanted; it does not establish how many sites would adopt it.

This proposal stands on its own. It requires neither a component framework nor the [Declarative HTML Components](/declarative-components/) proposal.

## Why this is probably the easiest proposal to adopt

Of the proposals in this collection, this is probably the easiest for browser makers to adopt. Its scope is an explicit parsing opt-in and a familiar source abbreviation that produces element structures browsers already support. That assessment concerns the feature's scope; browser implementers still need to establish compatibility and implementation cost.

- **The tokenizer already recognizes the syntax.** HTML already defines a self-closing start-tag state and a self-closing flag on tokens.[^2] The proposal changes how HTML tree construction handles that signal for non-void elements.
- **The declaration uses an existing token field.** The doctype token already carries a public identifier. The proposal recognizes `next` there and applies the new tag rule only in the selected profile.[^6]
- **The result uses the existing DOM.** `<div />` has the semantics of `<div></div>`. The proposal introduces no element interface, DOM node type, or JavaScript API.
- **Rendering uses existing behavior.** CSS, layout, accessibility, and element behavior operate on the expanded result. There is no new visual primitive or component lifecycle to implement.
- **Void and foreign elements retain their rules.** The explicit allowlist keeps `<br />` equivalent to `<br>`, and SVG and MathML retain their existing handling of self-closing syntax.
- **It can be evaluated independently.** Implementers can review and test this parser change without adopting the component, reactivity, or forms proposals in this collection.

The remaining work is concentrated in profile propagation, tree construction, and compatibility: raw-text elements, script execution, special insertion modes, and document and fragment parsing all need precise rules and tests. The explicit declaration preserves existing parsing for documents that have not opted in. Safe deployment still requires the compatibility work below.

## Source sugar, ordinary DOM

With the profile enabled, the browser should produce the same result as parsing the expanded source in the same context.

```html title="Proposed source"
<div class="marker" /><p>Next sibling</p>
```

```html title="Equivalent HTML"
<div class="marker"></div><p>Next sibling</p>
```

There is no self-closing node type or persistent flag on the element. Attributes, DOM interfaces, CSS matching, accessibility semantics, and custom-element lifecycle behavior follow the expanded form. HTML serialization continues to use ordinary HTML: an empty `div` serializes with an end tag, and a `link` without one. Preserving the author's shorthand is a source-tool concern.

The profile belongs to the parsing document. Tools emitting a complete document that relies on the shorthand must preserve its opt-in declaration; a serialized fragment relies on its receiving parser's context.

## Parsing rules

When the profile is enabled, recognize the shorthand where the tokenizer recognizes a self-closing start tag, then give it the effect of the expanded form. Without the profile, retain today's handling of the slash.

- **Names outside the void-element allowlist:** process the equivalent start and matching end tags, preserving the surrounding parser context. Following source becomes subsequent content according to the usual tree-construction rules.
- **Names in the void-element allowlist:** process the start tag alone, with or without a trailing slash. Never synthesize an end tag.
- **Custom elements:** recognize the shorthand without waiting for a JavaScript definition. Registering or upgrading an element does not change how its source is parsed.
- **SVG and MathML:** preserve existing foreign-content parsing, including its namespace and integration-point rules.[^1]
- **Attributes:** preserve existing tokenization. `<div data-path=assets/ />` closes the element; `<div data-path=assets/>` has the unquoted attribute value `assets/` and does not use the shorthand. A slash inside an attribute value is still data.[^1]

The intended scope includes elements with special parsing rules. For example, `<script src="app.js" />` should behave as `<script src="app.js"></script>`, and `<textarea />` as `<textarea></textarea>`. Script execution, raw-text handling, template insertion modes, and elements such as `table`, `select`, `html`, `head`, and `body` need explicit algorithms and tests. The equivalence above is the design goal; this draft does not yet supply a complete tree-construction patch.

An implementation cannot achieve this by globally replacing strings or by rewriting the DOM after parsing. Those approaches cannot reliably distinguish markup from attribute values, comments, script text, and other parser contexts.

## Compatibility and rollout

The explicit declaration limits the change to documents whose authors opt in. Existing HTML parsers ignore the self-closing flag on most non-void HTML start tags and report a parse error.[^2] That behavior continues in documents using plain `<!DOCTYPE html>`.

Consider this fragment:

```html
<div /><span>Following content</span>
```

In an ordinary HTML body context, the `span` remains a child of the `div`. In a supporting parser with the `next` profile enabled, the two are siblings. Authors adopting the profile must audit existing markup and inserted fragments that depend on today's nesting.

The declaration addresses the legacy-content objection raised in WHATWG HTML issue #721 by preserving today's interpretation in documents that have not opted in.[^3] Compatibility research must still check existing uses of the exact declaration, behavior in opted-in documents, and agreement across browsers and other HTML parsers.

> [!warn] Open for review
> Review the exact doctype matching rules, the fragment propagation model, template and document-writing behavior, and feature detection. The declaration records author intent; reading `document.doctype.publicId` alone does not demonstrate support for the new parsing behavior.

An unsupported browser still parses the declaration in standards mode and applies today's tag rules. Standards-mode fallback preserves the rendering mode; it does not make self-closing non-void tags work. Authors targeting those browsers must send expanded tags for non-void elements. Any build-time lowering must use a parser that understands the proposed syntax; a DOM-based runtime shim runs too late to recover the intended source structure reliably.

## Next steps

Incubation should turn the short authoring rule into a testable browser change.

1. Measure existing uses of `<!DOCTYPE html PUBLIC "next">` and test its rendering-mode fallback across engines.
2. Specify declaration recognition, profile propagation, and document and fragment parsing together, including migration of markup that depends on today's nesting or raw-text behavior.
3. Write web-platform tests for opted-in and ordinary documents, siblings, attributes, custom elements, raw-text elements, templates, tables, foreign content, and HTML serialization.
4. Seek browser implementer review alongside the existing WHATWG discussion.
{.algo}

Discuss the rule and its compatibility path in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## References

[^1]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags): void elements, foreign elements, and the boundary between an unquoted attribute value and a trailing slash.
[^2]: WHATWG HTML, [non-void HTML element start tag with trailing solidus](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^3]: WHATWG HTML, [issue #721: HTML should support self-closing tags in general](https://github.com/whatwg/html/issues/721), including discussion of compatibility and custom elements.
[^4]: React, [Writing Markup with JSX: close all the tags](https://react.dev/learn/writing-markup-with-jsx#2-close-all-the-tags), and Vue, [Components Basics: self-closing tags](https://vuejs.org/guide/essentials/component-basics.html#self-closing-tags). Vue documents the difference between its template parser and native HTML parsing, including unintended nesting of following content.
[^5]: W3C, [XML 1.0: external entities and identifiers](https://www.w3.org/TR/xml/#sec-external-ent), for the historical distinction between public identifiers and URI-based system identifiers. The proposed document remains HTML.
[^6]: WHATWG HTML, [the initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name state](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [parsing HTML fragments](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
