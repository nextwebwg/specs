---
title: Parsing rules
order: 1
blurb: recognition · empty output · recovery · protected contexts
sectionNav: true
eyebrow: Opt-in Self-Closing HTML · proposed rules
status: "Unofficial Editor's Draft · Stage 0"
---

# Parsing rules

**Make the element empty without changing which characters HTML recognizes as text or markup.** The proposed parser keeps HTML's existing reading and recovery state. For an eligible `/>`, it changes where the resulting nodes appear in the document.

## What HTML already does

```html
<div />
<p>Hello</p>
```

HTML's **tokenizer** recognizes the self-closing marker. Its **tree builder** nevertheless keeps this ordinary non-void HTML element open. That defined parse-error recovery puts the paragraph inside the div.[^1]

The proposal also keeps the div in the parser's internal records, so later source is interpreted by those same HTML rules. The difference is the output document: the div is empty and its recognized children appear after it.

## Same recognition, different containment

::::: two
:::: {.parser-path}
### Existing HTML output

::: flow
- Recognize the self-closing marker on `div`
- Keep `div` in the parser's open-element records
- Recognize the following paragraph as an element
- Put the paragraph inside the div {.acc}
:::

```text
body
└─ div
   └─ p
      └─ "Hello"
```
::::
:::: {.parser-path}
### Proposed output

::: flow
- Recognize the self-closing marker on `div`
- Keep `div` in the parser's open-element records
- Recognize the following paragraph as an element
- Keep div empty; put the paragraph after it {.acc}
:::

```text
body
├─ div
└─ p
   └─ "Hello"
```
::::
:::::

**The parser remembers more than the output contains.** An empty output element can still have an entry in the parser's recovery state. A later real closing tag acts on that entry until ordinary HTML rules remove it.

Formatting elements such as `small`, `b`, `a` and `em` use this same rule. For example, `<small/><span>tail</span>` produces an empty small element followed by the span.

## Why remembering the element matters

Consider this source:

```html
<div/><svg></div><style><img src=x onerror="attack()"></style></svg>
```

The critical question is whether the apparent image stays stylesheet text or becomes an element with executable code. Simply processing an immediate `</div>` at the slash can change that answer.

::::: two
:::: {.parser-path}
### Immediate opening-and-closing actions

::: flow
- Open div and immediately close it
- Read `svg`; the parser is now in SVG
- The later `</div>` has no div left to close {.acc}
- The following style is interpreted in SVG context
- The apparent image becomes markup with a handler
:::
::::
:::: {.parser-path}
### Proposed recognition-preserving rule

::: flow
- Make div empty in the output; retain its parser entry
- Read `svg` using ordinary HTML rules
- The later `</div>` finds that entry and exits SVG and div {.acc}
- The following style is an HTML stylesheet
- The apparent image remains text; no image handler is created
:::
::::
:::::

This is ordinary HTML recovery using retained parser state. It does not guess intent from future tags. The output changes as tokens arrive; the parser does not wait for the whole source before making the div empty.

The [reference tests and browser observations](/self-closing-html/security) exercise this example and counterexamples where old entries have already expired. Retaining full HTML recovery state avoids treating a stale tag name as a live closing target.

## Text and inactive contents keep their boundaries

```html
<style/><img src=x onerror="attack()"></style>
```

Here the existing parser reads the apparent image as stylesheet text. **This proposal keeps that interpretation:** `style` retains its ordinary closing behavior, so the apparent image never becomes an element. A sanitizer is not involved in obtaining that result.

The same principle protects script text, textarea text and other starts that put the tokenizer into a special text-reading state. Template contents also remain in their inactive content document.

| Boundary | Proposed handling | Reason |
| --- | --- | --- |
| A start that selects a special text-reading state, such as HTML `style`, `script` or `textarea` | Use its ordinary closing behavior. | Ending that state early can expose text as markup. |
| `template` and its contents | Keep the template boundary and its content document. | Moving contents into the active document could activate scripts or resources. |
| Document structure: `html`, `head`, `body`, `frameset` | Use existing document-structure handling. | These govern document construction. |
| Table/select child-placement containers: `table`, `caption`, `colgroup`, `tbody`, `thead`, `tfoot`, `tr`, `td`, `th`, `select` | Use their ordinary closing behavior. | Their dedicated child-placement modes need their container boundaries. |
| An element with the HTML `inert` attribute | Keep its containment boundary. | Its descendants retain their explicit interaction-inert ancestry. The attribute itself does not disable scripts. |

Existing void elements and native SVG/MathML self-closing handling continue to use their existing rules. Other attributes, including `hidden`, `disabled` and `popover`, do not choose the algorithm.

For an exempt text element, writing `<script />` still opens a script: authors must supply its closing tag. Use `<script src="app.js"></script>` for an external script.

## The proposed algorithm

1. Process the source token with ordinary HTML tokenization, tree construction and recovery. Keep namespaces, formatting records, insertion modes and parser associations in that recognition state.
2. When an unacknowledged self-closing marker creates an eligible HTML element, mark that element for empty output. Respect the boundaries listed above.
3. Construct the output from the recognized nodes. Keep a marked element but place its recognized children immediately after it. Apply the same operation recursively.
4. Preserve each node's identity and data, its order, its namespace ancestry, its template-content ownership and its explicit inert ancestry.
5. At a completed token checkpoint, apply parser-owned output changes before exposing the result to a parser-triggered script or callback. Preserve application-owned DOM changes and normal pause/resume boundaries.

**No text is tokenized a second time to create the output.** The operation changes containment among nodes the HTML parser already recognized. It does not manufacture an image, script or handler from a text node.

Formatting repair retains the empty-output mark on reconstructed elements from the same marked start token.

This is a containment rule. In complex formatting recovery, its output can differ from spelling a literal opening tag followed by a closing tag. The retained recognition state remains authoritative for subsequent source.

::: {.details summary="Reference implementation and proof scope"}

[recognition/parser.mjs](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/parser.mjs) retains an ordinary parse5 recognition tree and constructs output snapshots without mutating it. Text-state exceptions follow the actual tokenizer state after the start, including namespace and scripting state. HTML's existing acknowledged self-closing handling takes precedence.

The [live DOM adapter](https://github.com/nextwebwg/specs/blob/main/self-closing-html/evidence/recognition/live-dom.mjs) applies node deltas and creates nodes in a document without a browsing context before insertion. This prevents the adapter from first constructing a template image as an active image. It uses the previous delta reconciler's mutation ownership rules.

The abstract forest-projection theorem preserves payload order and protected ancestor paths. Generated comparisons and browser adapter tests check the reference implementation. They do not prove complete native scheduling, form association, declarative shadow-root ownership or all script interleavings. The earlier immediate-closure native patch implements a different algorithm.

:::

## Opt in explicitly

Use either declaration:

```html
<!DOCTYPE html PUBLIC "self-closing">
```

Or:

```html
<!DOCTYPE html PUBLIC "next">
```

`self-closing` selects this feature. `next` selects the current and future HTML Next family supported by the implementation. [HTML Feature Profiles](/html-feature-profiles/) owns selection, the proposed response header and explicit API options. Existing documents keep their existing interpretation.

The slash must be a marker rather than part of an unquoted value:

```html
<div data-path=assets/ /> <!-- Marker; value is assets/ -->
<div data-path=assets/>  <!-- No marker; value is assets/ -->
```

### Explicit parsing and insertion APIs

Existing string-parsing APIs keep their existing behavior. The shared profile proposal defines explicit selection for proposed `Document.parseHTML()` and `Document.parseHTMLUnsafe()` options. A fetched string can be parsed with an explicit selection independently of its caller's document; a response header does not remain attached to a `.text()` string.

Safe parsing methods still perform their normal sanitization for untrusted HTML. That is a separate API protection, not the reason this algorithm preserves text recognition. Inserting the resulting nodes does not switch the destination document's parsing mode.

Legacy document writing must be rejected or isolated in an opted-in navigation until an implementation specifies how writes participate in both recognition and output state. Native profile API integration and execution review remain implementation work.

[Security properties, tests and remaining work →](/self-closing-html/security)

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [self-closing start-tag state](https://html.spec.whatwg.org/multipage/parsing.html#self-closing-start-tag-state), [trailing solidus parse error](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus), [tree construction](https://html.spec.whatwg.org/multipage/parsing.html#tree-construction) and [foreign content](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign).
[^2]: WHATWG HTML, [#9491: sanitizer mismatch](https://github.com/whatwg/html/issues/9491#issuecomment-1623702790) and [parsing-mode changes at a distance](https://github.com/whatwg/html/issues/9491#issuecomment-1695514547).
:::
