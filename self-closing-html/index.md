---
title: HTML Next Parsing
eyebrow: HTML Next · independent proposal
status: "Unofficial Editor's Draft · Stage 0"
pager: false
---

# HTML Next Parsing

Native self-closing tags, with forgiving HTML syntax. An explicit opt-in adds the shorthand while preserving HTML's boundaries between text and markup.

## Write the empty element once

```html
<!DOCTYPE html PUBLIC "next">

<user-avatar name="Ada" />
<div class="divider" />
<br />
```

::: two
> [!norm] Ordinary elements
> `<div />` → `<div></div>`
>
> `<x-card />` → `<x-card></x-card>`

> [!ex] Void elements
> `<br />` → `<br>`
>
> `<link />` → `<link>`
:::

Eligible elements become empty DOM nodes. HTML's existing void-element allowlist remains explicit: **`<br />` never becomes `<br></br>`.**[^1]

Authors already use self-closing components in JSX and Vue templates. This brings the shorthand to HTML source.[^4]

Case-insensitive names, boolean attributes, unquoted values, optional tags, and error recovery retain their HTML rules. XML parsing is not required.

## What held this back

Browsers currently ignore the slash on ordinary HTML elements. Changing that everywhere would change existing pages. An explicit document opt-in addresses that compatibility problem.[^2][^3]

There is also a security problem: a sanitizer can regard apparent tags as harmless text, while a different parser exposes them as markup. WHATWG's self-closing discussion identifies this with a `style` example. Merely adding a doctype or excluding `style` is insufficient.[^9]

> [!warn] The boundary that must not move
> ```html
> <style/><img src onerror=alert(1)><style></style>
> ```
>
> The apparent image is text in existing HTML. The shorthand must not turn it into an image with an event handler.

## Close the element. Preserve the context.

The proposed parser closes the element's **DOM containment** while retaining the context HTML needs to interpret later tags.

For example, a later `</div>` still receives the appropriate HTML recovery behavior after `<div />`. It cannot accidentally leave the parser inside SVG and turn subsequent style text into markup.

> [!ex] Empty elements; stable text boundaries
> The reference model produces empty elements and following siblings while preserving recognized nodes, namespaces, attributes, text, and inert template boundaries.
>
> Text-mode and other parser-sensitive elements keep their existing slash handling. Ordinary HTML insertion APIs keep their existing grammar.

This makes recovery part of the feature's contract. The slash is not a global instruction to reinterpret everything that follows.

## The rules at a glance

| Concern | Proposed rule |
| --- | --- |
| Existing pages | Plain `<!DOCTYPE html>` retains existing parsing. |
| Author opt-in | `<!DOCTYPE html PUBLIC "next">` selects a fixed profile for document source. |
| Ordinary empty elements | Eligible HTML and custom elements close DOM containment. |
| Void elements | Use the existing allowlist; never synthesize their end tags. |
| Sensitive contexts | Preserve text, namespace, inertness, and recovery boundaries through exemptions and retained parser context. |
| Dynamic HTML | Existing APIs remain stable. Explicit Next insertion must parse and sanitize in the destination context. |

`PUBLIC "next"` names a built-in profile. It fetches no DTD and does not enable XML. Current browsers retain standards rendering mode with this declaration but do not implement the new syntax.[^5][^6]

## Evidence

The safety argument is structural: the reference model changes eligible parent/child relationships without retokenizing text or creating new elements. The experiments check that implementation and its edge cases. Active-browser checks also identified native containment exemptions and the need to preserve shadow-root ownership.

| Check | Result |
| --- | --- |
| Generated parsing cases | 800,000 comparisons preserved the checked recognition properties. |
| Ordinary authoring examples | 40 comparisons matched explicit pairs or the specified exemption. |
| Chromium probes | 12 inert comparisons preserved the checked node properties, including the reported text/namespace cases. |
| Serialization and reparsing | 200,000 comparisons found no new marker exposure against the legacy baseline. |
| Native containment and shadow roots | Active checks identified necessary exemptions; six inert open-root ownership comparisons passed. |

Sources, pinned dependencies, commands, and recorded results are in the [reproduction directory](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence). These establish properties of the reference model; native browser execution still requires implementation and conformance testing.

## Extension: more places for components {#placement-extension}

> [!future] Extension · placement · Proposal
> Preserve components as direct children in more contexts, including tables and templates.
>
> ```html
> <table>
>   <some-component></some-component>
> </table>
> ```
>
> Today's parser moves this component outside the table. The extension would preserve the authored structure. It needs its own parsing and safety contract; `display: contents` alone cannot change parsing.[^7][^8]

## Specification details

::: {.details summary="Parsing profile and element eligibility"}
### Profile selection

For a navigated HTML resource, an initial doctype with name `html`, public identifier exactly `next` (case-sensitive), and no system identifier selects the profile. Keywords and the doctype name retain HTML's case-insensitive matching. The resource remains `text/html` in standards rendering mode.

The profile is fixed for that parse. Later declarations, changes to the doctype DOM node, and custom-element registration cannot switch it. `next` identifies a fixed grammar, not a rolling latest version. Incompatible additions require a distinct opt-in.

Existing doctypes retain their behavior. Today `PUBLIC "next"` is nonconforming but selects standards rendering mode; making it conforming requires a standards change. `<!DOCTYPE html next>` and `<!DOCTYPE html-next>` currently select quirks mode.[^6]

### Void elements

The explicit allowlist is `area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.[^1]

Match names case-insensitively in the HTML namespace. Process only a start tag, with or without the slash. Preserve existing recovery for obsolete names.

### Initial exemptions

The reference profile preserves current slash handling for these non-void elements and contexts:

| Category | Exempt names or contexts |
| --- | --- |
| Text and scripting | `script`, `style`, `title`, `textarea`, `xmp`, `iframe`, `noembed`, `noframes`, `noscript`, `plaintext` |
| Structure and controls | `html`, `head`, `body`, `frameset`, `frame`, `table`, `caption`, `colgroup`, `col`, `tbody`, `tfoot`, `thead`, `tr`, `td`, `th`, `template`, `select`, `option`, `optgroup`, `form`, `fieldset`, `button` |
| Native containment | `details`, `dialog`, `datalist`, `audio`, `video`, `canvas`, `object`, `applet` |
| Formatting and recovery | `a`, `b`, `big`, `code`, `em`, `font`, `i`, `nobr`, `s`, `small`, `strike`, `strong`, `tt`, `u`, `p`, `pre`, `listing`; HTML special elements while an active formatting scope is present |
| Protected contexts | Foreign ancestors and their HTML integration points; elements carrying `inert`, `hidden`, or `disabled` |

Exemptions do not make an element void. Where HTML recognizes explicit end tags, use them. Eligible custom and unknown names do not depend on registration. Native SVG/MathML self-closing rules remain unchanged.[^12]

The initial set must match the browser algorithm. Lifting an exemption requires a defined interpretation and safety argument for that context.

### Tokenization

Preserve HTML attribute tokenization. `<div data-path=assets/ />` uses the shorthand. `<div data-path=assets/>` has an unquoted value of `assets/` and does not.[^2]
:::

::: {.details summary="Recovery algorithm and safety argument"}
### Recognition and containment

Use ordinary HTML tokenization and recovery to determine the recognized node tree in the actual parser context and scripting state. Keep its open-element, formatting, form, namespace, and template state. Match scripting state too: disagreement about `noscript` parsing caused the Bleach mutation-XSS vulnerability.[^11]

For each eligible self-closing start token that creates an element:

1. Retain the element as an empty node in the output DOM.
2. Place its recognized children immediately after it, in order, within the same containing root. Apply the rule recursively for consecutive shorthand elements.
3. Resolve later opening and closing tags using the retained recognition state, rather than inferring that state from output DOM ancestry.

This static reference is ordinary HTML recognition followed by the specified containment projection. Ignored start tokens create no recovery record. Records expire when HTML recovery removes them, including through an ancestor's closing tag.

The parser must preserve complete recovery state: aliases such as `</h2>` closing an `h1`, namespace transitions, and formatting recovery cannot be reduced to a set of previously closed names.

### Example: a closing tag at an SVG boundary

```html
<div/><svg></div><style><img data-probe></style></svg>
```

Naive start/end expansion exposes an image. Under the proposed reference rule, `div` is empty in the DOM, but its recovery record remains. `</div>` closes that record and the intervening SVG parsing context. `style` retains HTML text parsing; no image node appears.

When recovery depends on an ignored slash, this rule can differ from parsing a literally expanded string. That conservative interpretation is part of the profile.

### Construction argument

Let `R(s,c)` be ordinary HTML recognition of source `s` in exact parser state `c`. Let `P` be the containment projection. The static result is `P(R(s,c))`.

`P` does not tokenize strings, create elements, or change node namespaces, attributes, or text. It preserves node identities and preorder. Because protected containers never self-close, their contents retain the designated containment boundaries. This includes native disclosure, dialog, and fallback containers: lifting their children can expose previously hidden controls. Text recognized by `R` therefore cannot become newly recognized executable markup through `P`.

This addresses the text-to-markup mismatch illustrated in WHATWG #9491. It is a property of the static reference function, not a universal safety claim for an unimplemented browser. Script execution, custom-element reactions, shadow-root ownership, and DOM mutation interleavings must preserve the same boundaries in the native algorithm.

### Implementation requirements

A native implementation must construct the specified DOM incrementally and preserve its safety boundaries at script and reaction checkpoints. Rewriting an already active page after parsing does not implement this contract.

Declarative shadow-root host selection must use the retained recognition context. Keep each root attached to that same host; project only light-DOM children. A template declaration cannot migrate to a following sibling or the body.

Define parser pauses and encoding restarts, speculative loading, script-driven mutations, and document-writing isolation before shipment. The placement extension changes recognition itself and requires a separate safety argument.

Parentage intentionally changes. Application-defined components and script gadgets require their own policy; a sanitizer must not authorize hazardous content solely because an ordinary ancestor currently hides or intercepts it.[^10]
:::

::: {.details summary="Insertion APIs, compatibility, and reproduction"}
### Existing APIs

The destination document's profile must not switch the grammar of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `Range.createContextualFragment`, `DOMParser`, `Document.parseHTML*`, existing HTML insertion methods, or `iframe.srcdoc`. A doctype inside an input string cannot enable Next.

Dynamic Next insertion requires an explicit request. Parse and sanitize together in the actual target context, then insert nodes directly. Reject unsupported requests before insertion. A legacy-sanitized string or existing TrustedHTML wrapper is not proof of safety in a different context.[^9][^10]

`document.write/writeln` must not feed new-profile tokens through a legacy string API. Specify rejection before mutation or an equivalently isolated contract. `document.open` must not silently escalate grammar.

### DOM and fallback

Elements gain no new interface or persistent self-closing flag. Ordinary DOM operations can add children later. Serialization remains HTML; serialized strings carry no safety or parser-state provenance.

Unsupported browsers need expanded tag pairs. A lowering tool must implement the profile's recovery contract; regex replacement is insufficient. Before adoption, measure existing use of the exact declaration and define reliable capability detection. `document.doctype.publicId` records author intent, not implementation support.

### Reproduction

The [evidence README](https://github.com/nextwebwg/specs/tree/main/self-closing-html/evidence#readme) documents each command, dependency version, seed, result, and limitation.

- `projection-candidate.mjs`: static reference and generated recognition comparisons.
- `sugar-check.mjs`: ordinary authoring comparisons.
- `recovery-browser.html`: inert Chromium comparisons with marker attributes standing in for source metadata.
- `roundtrip-check.mjs`: serialization/reparsing comparisons.
- `active-build.mjs` / `active-browser.html`: 32 sandboxed observations, including containment, script mutation, custom-element reactions, and an unsupported serialization case.
- `shadow-browser.html`: six inert native open-root ownership comparisons.
- `matrix.mjs`: representative sanitizer configurations and earlier expansion variants.

Finite tests check implementation behavior; they do not prove all inputs safe. The model uses parse5 8.0.1, whose select behavior differs from current Chromium. Its serializer does not preserve declarative shadow-root ownership; it is not a conforming lowering tool. It does not execute source scripts or implement a native navigation parser. Chromium probes cover the recorded cases, not an independent implementation of the complete profile.

This remains an independent Stage 0 draft. Browser implementation, Web Platform Tests, and implementer security review are required before shipment.

Editor: [Matthew Dean](https://github.com/matthew-dean). Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).
:::

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags).
[^2]: WHATWG HTML, [trailing solidus on non-void elements](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^3]: WHATWG HTML, [#721: HTML should support self-closing tags in general](https://github.com/whatwg/html/issues/721), including compatibility, XML, and opt-in discussion.
[^4]: React, [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx#2-close-all-the-tags), and Vue, [self-closing tags](https://vuejs.org/guide/essentials/component-basics.html#self-closing-tags).
[^5]: W3C, [XML 1.0 external identifiers](https://www.w3.org/TR/xml/#sec-external-ent), for the historical distinction between public names and URI-based system identifiers.
[^6]: WHATWG HTML, [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
[^7]: WHATWG HTML, [unexpected markup in tables](https://html.spec.whatwg.org/multipage/parsing.html#unexpected-markup-in-tables), [in-template insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-intemplate), and [in-body insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inbody). These rules explain table relocation and why a wrapper can change how following row and cell tags are parsed.
[^8]: CSS Display, [box generation](https://drafts.csswg.org/css-display/#box-generation). `display` controls layout rather than the document tree or document-language semantics.
[^9]: WHATWG HTML, [#9491 sanitizer-mismatch example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [concerns about parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^10]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
[^11]: Mozilla, [CVE-2020-6802: Bleach mutation XSS in noscript handling](https://bugzilla.mozilla.org/show_bug.cgi?id=1615315).
[^12]: WHATWG HTML, [tree construction](https://html.spec.whatwg.org/multipage/parsing.html#tree-construction), [parsing elements that contain only text](https://html.spec.whatwg.org/multipage/parsing.html#parsing-elements-that-contain-only-text), and [foreign-content rules](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign). Inert Chromium comparison recorded 18 October 2026; no event handlers were executed.
:::
