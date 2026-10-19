---
title: Parsing rules
order: 1
blurb: opt-in · eligible elements · recovery · insertion APIs
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · proposed rules
status: "Unofficial Editor's Draft · Stage 0"
---

# Parsing rules

Define which elements can self-close, how recovery works, and where the new grammar applies.

## Select the capability

For a navigated HTML resource, request this capability through [HTML Feature Profiles](/html-feature-profiles/):

```html
<!DOCTYPE html PUBLIC "self-closing">
```

A server may instead select `self-closing` through the proposed `HTML-Feature-Profile` response header, which takes precedence over the doctype. The shared proposal owns header handling, selector grammar, the alternative `PUBLIC "next"` preset, support detection, and operation-local precedence. A resolved feature set is fixed for the parse; later declarations, doctype DOM changes, styles, scripts, and custom-element registration cannot switch it. The resource remains `text/html`; no DTD is fetched and XML is not enabled.

The recorded experimental implementation accepts the earlier exact public identifier `next`, with no system identifier. It does not implement the new response header, named-list selector, or family selection contract. Its evidence remains bounded to that pinned opt-in and the self-closing rules tested.

Plain HTML retains existing behavior. These profile declarations require a standards change; current standards rendering behavior is not native support for the proposed grammar.[^1]

## Distinguish empty pairs from void elements

An eligible self-closing start token creates an empty element. The slash closes its DOM containment; it does not make the element void.

```html
<x-card />
<!-- Empty x-card element; it can gain children through DOM APIs later. -->
```

HTML's explicit void allowlist remains:

`area`, `base`, `br`, `col`, `embed`, `hr`, `img`, `input`, `link`, `meta`, `source`, `track`, `wbr`.[^2]

Match names case-insensitively in the HTML namespace. For a void element, process only a start tag, with or without the slash. Never synthesize an end tag. Preserve existing recovery for obsolete names.

Eligible custom and unknown names do not depend on registration. Native SVG/MathML self-closing rules remain unchanged.[^3]

## Preserve sensitive elements

These names and contexts retain current slash handling in the reference profile:

| Category | Exempt names or contexts |
| --- | --- |
| Text and scripting | `script`, `style`, `title`, `textarea`, `xmp`, `iframe`, `noembed`, `noframes`, `noscript`, `plaintext` |
| Structure and controls | `html`, `head`, `body`, `frameset`, `frame`, `table`, `caption`, `colgroup`, `col`, `tbody`, `tfoot`, `thead`, `tr`, `td`, `th`, `template`, `select`, `option`, `optgroup`, `form`, `fieldset`, `button` |
| Native containment | `details`, `dialog`, `datalist`, `audio`, `video`, `canvas`, `object`, `applet` |
| Formatting and recovery | `a`, `b`, `big`, `code`, `em`, `font`, `i`, `nobr`, `s`, `small`, `strike`, `strong`, `tt`, `u`, `p`, `pre`, `listing`; HTML special elements while an active formatting scope is present |
| Protected contexts | Foreign ancestors and their HTML integration points; elements carrying `inert`, `hidden`, `disabled`, or `popover` |

Exemptions do not make an element void. Where HTML recognizes explicit end tags, use them. For example, `<style />` keeps existing HTML behavior; authors write `<style></style>` for an empty style element.

The initial set must match the browser algorithm. Lifting an exemption requires a defined interpretation and safety argument for that context. [Why these boundaries matter →](/self-closing-html/security#preserve-protected-containment)

## Keep HTML attribute tokenization

The slash must be recognized as part of the tag syntax, rather than an unquoted attribute value.[^4]

::: two
```html title="Self-closing"
<div data-path=assets/ />
```

```html title="Not self-closing"
<div data-path=assets/>
```
:::

In the second example, the attribute value is `assets/`. The final slash belongs to that value.

## Retain recognition while changing containment

Use ordinary HTML tokenization and recovery to determine the recognized node tree in the actual parser context and scripting state. Keep its open-element, formatting, form, namespace, and template state. This recognition state follows ordinary HTML independently of output DOM parenting: an eligible shorthand's empty DOM element can still have a live open-element entry used for scope checks and later closing tags.

For each eligible self-closing start token that creates an element:

1. Retain the element as an empty node in the output DOM.
2. Place its recognized children immediately after it, in order, within the same containing root. Apply the rule recursively for consecutive shorthand elements.
3. Resolve later opening and closing tags using the retained recognition state, rather than inferring that state from output DOM ancestry.

> [!norm] Recovery records follow HTML's scope rules
> Ignored start tokens create no record. Records expire when HTML recovery removes them, including through an ancestor's closing tag. Retain complete state: a set of previously closed names cannot represent heading aliases, namespace transitions, or formatting recovery.

For example, HTML can use `</h2>` to close an `h1`. A recovery rule that checks only exact names would miss that relationship. [See the worked SVG-boundary example →](/self-closing-html/security#recover-at-namespace-boundaries)

For example, after `<div/><svg>`, the recognition stack still contains the div below SVG, while the output DOM places the empty div and SVG as siblings. A later `</div>` can therefore pop both recognition entries before the next token is interpreted.

The static reference is ordinary HTML recognition followed by this containment projection. When recovery depends on an ignored slash, the result can differ from parsing a literally expanded string. That conservative interpretation is part of the profile.

### Incremental execution checkpoints

Construct the output incrementally. Before running a parser-triggered script or delivering a custom-element reaction, expose the output corresponding to recognition completed at that checkpoint. Preserve application mutations rather than reconstructing the active document from a fresh snapshot. A script moving an output node does not rewrite the retained recognition stack. Parser pauses must prevent later source from becoming observable before resume.

Speculative loading must obey the same recognition boundaries; disabling the optional scanner is the experimental native implementation’s conservative strategy. Arbitrary encoding restarts and full scheduling conformance remain unresolved shipment requirements. The [security evidence](/self-closing-html/security#native-execution-coverage-and-limitations) separates the formal static argument, live adapter tests, and native execution results.

### Preserve shadow-root ownership

Declarative shadow-root host selection uses the retained recognition context. Keep each root attached to that same host; project only light-DOM children. A template declaration cannot migrate to a following sibling or the body.

## Parse independently of the caller's document

An explicitly requested parsing operation may enable `self-closing` even when its caller's document uses ordinary HTML or a different profile. [HTML Feature Profiles](/html-feature-profiles/#explicit-parsing) owns the proposed per-call option, selector validation, inertness, and failure rules. No ambient document flag is required or inherited. Omitting `profile` keeps existing behavior; `profile: "inherit"` explicitly copies the relevant document’s resolved snapshot, while `profile: "next"` opts into the HTML Next family of current and future proposals supported by the browser.

```js
// profile is a proposed option on this existing API.
const response = await fetch("/fragment.html");
const parsed = Document.parseHTML(await response.text(), {
  profile: "self-closing"
});
```

The returned detached document contains the requested DOM structure. Importing or adopting its nodes into an ordinary document preserves those actual relationships; it does not switch the destination's profile. Parsing is not sanitization, and insertion still follows ordinary security and activation rules. Existing string parsing APIs do not gain this behavior implicitly. The historical prototype does not implement these new options. The safe method retains its mandatory sanitization under the selected grammar; the unsafe method retains its separate contract.

## Keep existing insertion APIs stable

A document's profile must not change the grammar of existing string insertion and parsing APIs:

- `innerHTML`, `outerHTML`, and `insertAdjacentHTML`;
- `Range.createContextualFragment` and `DOMParser`;
- `Document.parseHTML*` and existing HTML insertion methods;
- `iframe.srcdoc`.

A doctype inside an input string cannot enable Next.

Dynamic Next insertion requires an explicit request. Parse and sanitize together in the actual target context, then insert nodes directly. Reject unsupported requests before insertion. A legacy-sanitized string or existing TrustedHTML wrapper is not proof of safety in a different context.[^5][^6]

`document.write/writeln` must not feed new-profile tokens through a legacy string API. Specify rejection before mutation or an equivalently isolated contract. `document.open` must not silently escalate grammar.

## DOM behavior and fallback

Elements gain no new interface or persistent self-closing flag. Ordinary DOM operations can add children later. Serialization remains HTML; serialized strings carry no safety or parser-state provenance.

Unsupported browsers need expanded tag pairs. A lowering tool must implement the profile's recovery contract; regex replacement is insufficient. Before adoption, measure existing use of the exact declaration and define reliable capability detection. `document.doctype.publicId` records author intent, not implementation support.

[Continue: security argument, browser requirements, and evidence →](/self-closing-html/security)

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), [after DOCTYPE name](https://html.spec.whatwg.org/multipage/parsing.html#after-doctype-name-state), [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments), and [current doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype).
[^2]: WHATWG HTML, [elements](https://html.spec.whatwg.org/multipage/syntax.html#elements-2) and [start tags](https://html.spec.whatwg.org/multipage/syntax.html#start-tags).
[^3]: WHATWG HTML, [tree construction](https://html.spec.whatwg.org/multipage/parsing.html#tree-construction), [parsing elements that contain only text](https://html.spec.whatwg.org/multipage/parsing.html#parsing-elements-that-contain-only-text), and [foreign-content rules](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign). Inert Chromium comparison recorded 18 October 2026; no event handlers were executed.
[^4]: WHATWG HTML, [trailing solidus on non-void elements](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus) and [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state).
[^5]: WHATWG HTML, [#9491 sanitizer-mismatch example](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [concerns about parsing-mode switches at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
[^6]: WHATWG HTML, [HTML parsing and insertion methods](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html#html-parsing-and-insertion-methods), including safe parsing with sanitization.
:::
