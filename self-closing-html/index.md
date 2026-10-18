---
title: HTML Next Parsing
eyebrow: HTML Next · independent proposal
status: "Unofficial Editor's Draft · Stage 0"
pager: false
---

# HTML Next Parsing

Self-closing tags, with forgiving HTML rules and the same DOM. One explicit opt-in lets HTML grow while existing pages keep their meaning.

## Self-closing tags

One declaration opts document source into the shorthand:

```html
<!DOCTYPE html PUBLIC "next">

<user-avatar name="Ada" />
<div class="divider" />
<br />
```

::: two
> [!norm] Tag pairs
> `<div />` → `<div></div>`
>
> `<x-card />` → `<x-card></x-card>`

> [!ex] Void elements
> `<br />` → `<br>`
>
> `<link />` → `<link>`
:::

HTML's explicit void-element allowlist skips the end tag. Other eligible HTML elements use tag pairs; text-mode and namespace exclusions are under security review. **`<br />` never becomes `<br></br>`.**[^1]

## HTML can evolve without becoming XML

Self-closing syntax should be available without adopting XML's strict parsing rules.

> [!note] Keep HTML's flexibility
> Case-insensitive names, boolean attributes, unquoted values, optional tags, and error recovery all keep their HTML rules. The document remains `text/html`.

> [!norm] Let authors choose
> Plain `<!DOCTYPE html>` keeps today's tag interpretation. `<!DOCTYPE html PUBLIC "next">` explicitly selects the new rule for document source.

This addresses the legacy-content objection in **WHATWG HTML #721**: existing documents keep their meaning. The thread also suggested an opt-in; this declaration makes that route concrete within HTML.[^3]

## Why authors want it

- **Less repetition.** An empty custom element declares its intent without repeating a long name.
- **Fewer surprises.** Vue documents how self-closing components work in its templates but can swallow following content in native HTML.[^4]
- **Direct HTML authoring.** Native support would remove the need for a build step solely to expand empty tags.

Adding children later means expanding the tag pair. The element's behavior stays the same.

## A small syntax change

The self-closing rule has a small syntactic scope: one explicit opt-in and one source abbreviation. Safe adoption also needs stable insertion APIs and sanitizer compatibility. The placement extension below is a larger design task.

> [!ex] Reuse what browsers already have
> The doctype already carries a public identifier. The tokenizer already recognizes `/>`. The result uses existing DOM elements, rendering, and accessibility behavior.[^2][^6]

`PUBLIC "next"` names a built-in parsing profile. It fetches no external definition and requires neither a new component model nor the other proposals in this collection.[^5]

> [!warn] No silent parsing switches
> The doctype must not change how existing HTML-insertion APIs parse strings. Dynamic Next parsing requires an explicit API; untrusted input must be parsed and sanitized together. Server-generated pages need compatible sanitation too. These are shipping requirements, not problems solved by opting in.[^9][^10]

This is a Stage 0 draft. Current browsers keep standards mode with the declaration but still require expanded tag pairs for non-void elements.[^6]

Discuss the proposal in the [specifications repository](https://github.com/nextwebwg/specs/discussions).

## Extension: more places for components {#placement-extension}

> [!future] Extension · placement · Proposal
> Let web components and declarative components appear as direct children in more contexts, under the same proposed doctype opt-in.
>
> Today, the parser moves this component outside the table:[^7]
>
> ```html
> <table>
>   <some-component></some-component>
> </table>
> ```
>
> The goal: keep the component where it was authored, with its child structure intact. Tables are one example; template contents and other restrictive contexts need the same review.
>
> Layout and accessibility remain design questions. `display: contents` is an option to evaluate, not a chosen default.[^8]

## Parser details and sources

::: {.details summary="Read the proposed parser contract"}
### Selecting the profile

For an HTML resource parsed during navigation, recognize the initial doctype before element content: name `html`, public identifier exactly `next` (case-sensitive), system identifier absent. Keywords and the doctype name keep HTML's case-insensitive matching.

The name `next` identifies a defined profile, not a rolling latest mode. Settle which capabilities it selects before shipping; later incompatible parsing changes need a distinct identifier or a separately specified opt-in.

The profile selects standards rendering mode and is fixed for that parse. Other doctypes retain existing behavior. Later declarations, DOM edits to the doctype, and custom-element registration cannot switch it.

`PUBLIC` names the profile rather than locating a DTD. There is no DTD fetch or validation and no switch to XML. Today this spelling produces a parse error but selects standards mode; recognizing it as conforming requires a standards change. `<!DOCTYPE html next>` and `<!DOCTYPE html-next>` currently trigger quirks mode.[^5][^6]

### Interpreting tags

For eligible HTML names outside the void-element allowlist, process `/>` as a start tag immediately followed by its matching end tag. Eligibility is subject to the security exclusion study below; the draft does not yet settle the complete exception set. Without the slash, the start tag remains open under normal HTML rules.

The allowlist is: `area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.[^1]

Match those names case-insensitively in the HTML namespace. With or without the slash, process only the start tag; never generate an end tag. Eligible custom and unknown names default to pairs, regardless of registration. SVG and MathML retain their existing foreign-content rules; HTML integration points need separate review before extending the shorthand there.

Keep existing tokenization: `<div data-path=assets/ />` uses the shorthand; `<div data-path=assets/>` has an unquoted value of `assets/` and does not. Optional-end-tag and legacy error recovery remain in force.

### Documents, fragments, and the DOM

- The doctype selects the profile for navigation document source, including a separately navigated iframe resource. It is not an ambient switch for string-to-DOM APIs.
- Existing APIs retain their current grammar-selection rules: `innerHTML`, `outerHTML`, `insertAdjacentHTML()`, `Range.createContextualFragment()`, `DOMParser.parseFromString(..., "text/html")`, and existing HTML parsing/insertion methods. Neither the destination document's profile nor a doctype inside the supplied string silently enables Next syntax. Ordinary HTML/XML and element-context distinctions remain.
- Existing string-based document creation, including `iframe.srcdoc`, needs the same fixed-grammar boundary. Document-writing APIs must not silently feed Next syntax to an active parser. Specify a compatible isolation or rejection rule before shipping; `document.write()` integration remains unresolved.
- Dynamic Next parsing requires an explicit, standardized API request with a defined grammar and insertion context. This draft defines the boundary, not an API name or signature. Unsupported requests must fail before insertion rather than fall back silently. Default calls to existing APIs keep their behavior.
- Moving nodes does not reparse their markup. Later string parsing follows the called API's explicit contract, not a profile inherited from the destination. Elements gain no new node type, element interface, or persistent self-closing flag. A self-closed non-void element can still receive children through DOM APIs.
- Element serialization stays ordinary HTML. A serialized string carries no guarantee that another grammar or context will interpret it identically. Complete source relying on the shorthand must preserve its declaration; dynamic consumers must select the grammar explicitly.

### Compatibility and remaining work

In `<div /><span>Following content</span>`, ordinary HTML makes the `span` a child of the `div`. A supporting parser with the profile enabled makes them siblings. Authors opting in must audit document source for dependencies on today's nesting. Existing fragment API calls keep their current behavior.[^2][^3]

Self-closing `script`, `textarea`, and other text-mode elements are candidates for exclusion, not promised capabilities. Precise algorithms and tests remain necessary for script execution, text modes, tables, selects, document structure, template-associated documents, shadow roots, and document-writing APIs.

Before adoption, measure existing uses of the exact declaration, test fallback across engines, and specify explicit dynamic parsing and feature detection. `document.doctype.publicId` records author intent; it does not prove support. The small scope is an adoption argument, not a measured implementation estimate.

Unsupported browsers retain today's tag rules. Send them expanded tag pairs. Build-time lowering needs a parser that understands the proposed syntax; string replacement or a DOM rewrite after parsing cannot reliably recover source intent.

### Placement extension: goals and open questions

The `placement` extension proposes using the same `next` parsing profile to make more parent/child combinations available to components. It is at Proposal stage, separate from the self-closing rule; neither a parser algorithm nor a rendering default is settled.

Preserve the authored parent and child structure of eligible component elements when existing context rules would relocate them or discard their descendants. This includes inert template contents. For example, a wrapper around `<tr><td>Row</td></tr>` should not cause those row and cell elements to disappear. The component runtime still decides what the component does; preserving a node does not instantiate or render a declarative component by itself.[^7]

Review each affected context, including table insertion modes, templates, selects, and document structure. Define which component or unknown element names qualify, how implied containers and omitted end tags interact with them, and how an explicit dynamic parsing request selects the behavior. Existing fragment APIs must not inherit it. Preserve HTML's void elements, text-only parsing, namespace handling, and forgiving recovery outside the specified changes. The extension does not promise arbitrary nesting for every native element.

Evaluate DOM structure, native layout, and accessibility separately. `display: contents` changes box generation, not parsing; it cannot recover discarded nodes. A rendering design must account for native table and control behavior, focus, events, and accessible relationships before selecting any default.[^8]

Existing documents keep today's behavior. Authors opting in must audit document-source component placement as well as self-closing syntax; fallback, sanitizer compatibility, and feature detection need tests for each capability. The shared doctype expresses intent, not proof that a browser supports every part of this draft.

Seek browser implementer review alongside the existing WHATWG discussion. This is an independent Stage 0 draft, not a W3C or WHATWG deliverable.

Editor: [Matthew Dean](https://github.com/matthew-dean).
:::

::: {.details summary="Read the security boundaries and exclusion study"}
### Keep sanitization and interpretation together

WHATWG HTML #9491 identifies a real parser-mismatch risk: a sanitizer can treat attacker-controlled markup as harmless text while another grammar exposes executable elements. An explicit document opt-in does not prevent that mismatch. A related mismatch caused the Bleach vulnerability CVE-2020-6802.[^9][^11]

The proposed dynamic Next path must parse and sanitize untrusted input under the same grammar and actual insertion context, then insert the resulting nodes directly. It must not sanitize a string under legacy rules and reparse it as Next. Existing safe methods such as `setHTML()` provide a precedent for integrating parsing and sanitization; this proposal does not add implicit Next behavior to them.[^10]

A legacy-sanitized string, or an existing trusted-value wrapper without a matching grammar/context contract, is not proof of Next safety. Define the explicit API, sanitizer policy, supported contexts, and failure behavior before shipping. Reject unsupported grammar/context requests or sanitizer configurations before DOM changes; silent fallback cannot establish safety.

### Investigate fixed exclusions

A conservative candidate is to keep current slash handling for HTML elements that enter script, RAWTEXT, RCDATA, or plaintext parsing: `script`, `style`, `title`, `textarea`, `xmp`, `iframe`, `noembed`, `noframes`, `noscript`, and `plaintext`. This includes legacy names and state-dependent cases so review does not miss them.[^12]

If adopted, these remain non-void elements: `/>` does not make them empty. Their current parsing continues; explicit end tags remain necessary where the existing grammar recognizes them. Tooling should diagnose the unsupported shorthand. An external `src` is not by itself evidence that self-closing `script` is safe.

This stops the specific example in #9491 from acquiring a new text/markup boundary:

```html
<style/><img src onerror=alert(1)><style></style>
```

A rule that guesses from later markup is insufficient. Under one interpretation the example has two empty styles and an image; under the other, the apparent tags are style text. Removing the second `<style>` still leaves the mismatch. Choose eligibility from fixed parser rules, not an attempt to infer intent from following tags.

### Tag names alone are not enough

Even closing an ordinary custom element can change the namespace of later elements:

```html
<math><mtext><x-box/><mglyph><style><img data-probe></style></mglyph></mtext></math>
```

In an inert Chromium comparison, the source above produces no `img` element. Replacing only `<x-box/>` with `<x-box></x-box>` produces one: `style` changes from HTML text parsing to a MathML element. This compares current parsing with one hand-expanded example; it is not a Next implementation or a demonstrated sanitizer bypass. It shows why excluding only `style` from the shorthand is insufficient.[^12]

A second candidate is to disable the new HTML shorthand within SVG/MathML contexts, including their HTML integration points. Existing foreign-content self-closing syntax would remain unchanged. Both candidate restrictions require precise algorithms and cross-engine review; neither is a proven complete safety boundary.

### Shipping requirements

Server-generated Next source can still reinterpret HTML sanitized under legacy rules. Define and validate a matching sanitation and context-escaping pipeline for that path. Updating a library alone does not protect existing installations. If compatibility cannot be established, narrow the feature or defer it rather than treating author opt-in as sufficient protection.

Before adoption, test direct document parsing, explicit dynamic parsing, legacy APIs, server embedding, serialization/reparsing, and cross-document use. Cover text modes, scripting state, SVG/MathML integration, malformed markup, and the placement extension. Use the #9491 example and namespace case as starting regressions, alongside representative sanitizer integrations and broader security review. Do not ship until the remaining mismatch risks have an accepted resolution.
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
