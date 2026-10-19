---
title: HTML Feature Profiles
order: -1
eyebrow: Independent HTML proposal
status: "Unofficial Editor's Draft · Stage 0"
sectionNav: true
---

# HTML Feature Profiles

Select proposed HTML capabilities through an HTTP response header or document declaration, or opt into a documented `next` preset. This proposal defines the shared selection contract so individual features can specify their behavior without inventing competing switches.

```html
<!DOCTYPE html PUBLIC "self-closing, flexible-nesting">
```

This requests the named capabilities. An author who wants the implementation's documented experimental preset can instead write:

```html
<!DOCTYPE html PUBLIC "next">
```

A server can select the same profile without changing the doctype:

```http
Content-Type: text/html; charset=utf-8
HTML-Feature-Profile: self-closing, flexible-nesting
```

The header can also carry `next`. `HTML-Feature-Profile` is a **proposed HTTP response header**, not an already registered or implemented standard field. A plain `<!DOCTYPE html>` can remain in the response body.

Neither mechanism downloads a DTD or enables XML. These are proposed built-in HTML profile selectors, not syntax supported by current production browsers.[^1]

> [!note] Status and authority
> This Stage 0 proposal owns the response header, selector grammar, preset resolution, support detection, and precedence. [Opt-in Self-Closing HTML](/self-closing-html/) owns `self-closing`; [Flexible HTML Nesting](/flexible-html-nesting/) owns `flexible-nesting`. Feature behavior and safety remain obligations of those proposals. The API shapes below are candidates, not existing web APIs.

## Named capabilities and the next preset

| Selector | Requested behavior |
| --- | --- |
| `self-closing` | Only the capability specified by Opt-in Self-Closing HTML, plus explicitly required dependencies. |
| `flexible-nesting` | Only the structural capabilities specified by Flexible HTML Nesting, plus explicitly required dependencies. |
| `self-closing, flexible-nesting` | The supported, compatible composition of those capabilities. |
| `next` | The exact feature set and revision in the implementation's published preset manifest at parse start. |

`next` is not permission to enable every proposal on the web. A preset manifest must list included identifiers, semantic revisions, dependencies, and approved compositions. Adding an identifier to a registry does not include it in the preset. Inclusion requires compatibility, composition, and security review.

The same preset rules apply whether `next` came from the response header or the doctype. The preset may evolve between implementation releases. It must not evolve while a document is being parsed or remain dependent on a network lookup. Resolve it once, record the resolved revision and features, then freeze that document's parsing and feature contract. An origin's older `next` documents can still change behavior after a browser update; that compatibility risk must be evaluated before changing the preset. Named selectors are the more deliberate choice for authors who do not want new unrelated capabilities.

Feature identifiers are durable contracts, not floating aliases to arbitrary incompatible semantics. A breaking revision needs a separately named contract or an explicit migration design. This draft does not invent a version suffix grammar.

## Selector grammar

A selector is either the exact ASCII string `next` or a nonempty comma-separated list of lowercase feature identifiers. An identifier starts with `a`–`z` and continues with `a`–`z`, `0`–`9`, or `-`. Ignore ASCII whitespace around each entry; do not ignore whitespace inside an identifier.

Order does not give priority. Resolve dependencies and composition rules before parsing; `self-closing, flexible-nesting` requests the same set as `flexible-nesting,self-closing`. Duplicate identifiers, empty entries, uppercase variants, and mixing `next` with named identifiers are invalid. Reject them rather than guessing intent.

| Input | Proposed interpretation |
| --- | --- |
| `self-closing` | Named request. |
| ` self-closing , flexible-nesting ` | Two named requests after trimming surrounding ASCII whitespace. |
| `next` | Preset request. |
| `next,self-closing` | Invalid: preset and named selection are mutually exclusive. |
| `self-closing,` | Invalid: empty entry. |
| `Self-Closing` | Invalid: identifiers are case-sensitive. |
| `future-feature` | Syntactically valid but unsupported unless registered and implemented. |

When the doctype is the selector source, it must have the HTML name and no system identifier. The public identifier carries the selector. Plain `<!DOCTYPE html>` selects existing HTML. Historical public/system identifiers retain their established handling unless they match the new selector recognition rules.

Recognizing a new short public identifier as a profile request can conflict with previously ignored identifiers. The exact recognition discriminator, including malformed selectors beginning with a known identifier, requires a compatibility survey before adoption. A conforming implementation must not treat a recognized but unsupported request as a successful legacy parse.

## HTTP response header

The candidate field name is `HTML-Feature-Profile`. HTTP field names are case-insensitive; feature identifiers and `next` retain the selector grammar's case-sensitive matching. Its value is a Structured Field List of bare tokens, using RFC 9651. Each token must satisfy the feature-identifier grammar, or be the sole `next` token. Strings, inner lists, parameters, numbers, and booleans are invalid. This preserves the readable comma-separated spelling without the doctype’s surrounding quotes.

```http
HTML-Feature-Profile: next
```

This is a response-header field, not a trailer field. Trailers and informational responses cannot select or revise a profile after body processing begins. The final navigation response's header is authoritative for a `text/html` document. Resolve it before consuming profile-sensitive body source. A doctype profile selector is used only when the header is absent. If both are present, the header wins; the doctype cannot add features, remove them, or switch the preset. A developer diagnostic may report a conflicting source declaration, but that conflict does not change the selected profile.

An empty, malformed, or unsupported header is an error under the same resolution rules as other requests. Do not silently fall back to the doctype or apply only supported entries. Multiple field lines are combined and parsed as one Structured Field List before feature validation; repeated identifiers and a combined `next`/named request remain invalid. Presence of a malformed header does not count as absence.

Only the final response selects the profile. Redirect-response headers do not carry into the destination document. Each navigated iframe resolves its own final response; the parent document's header does not select a child's grammar. Ordinary subresources do not change their owner's profile. This draft introduces no request header or automatic capability advertisement.

The header applies to HTML document navigation, not to arbitrary strings retrieved with `fetch`. Passing a fetched string to legacy `innerHTML` or `DOMParser` retains that API's grammar. `iframe.srcdoc` has no response header and retains its separately specified API contract. A future profile-aware parser can accept an explicit selector, but must not acquire it by ambient inheritance.

The header does not replace `Content-Type`, select XML, alter charset decoding, or override the normal doctype rules for rendering mode. Servers should still emit an appropriate HTML doctype. CSP, Trusted Types, origin checks, and sanitization remain independent controls.

Caches must retain the profile header together with the body. If a server varies a representation according to request metadata, its ordinary cache key and `Vary` handling must cover that variation. A proxy, service worker, or user-land transform that changes the selector must treat that as a grammar-changing representation change; it cannot claim semantic equivalence without checking the body. This header is not a security boundary against a party already able to rewrite the response.

Before adoption, the field needs specification and HTTP field registration, compatibility review, intermediary tests, and native implementation. Legacy browsers can ignore it and parse the body normally; sending the header does not establish support.

## Resolve before consuming profile-sensitive source

1. Determine the parsing operation and its authoritative selector using the precedence table below.
2. Validate the selector and resolve named capabilities or the local `next` manifest.
3. Verify that every required capability, dependency, semantic revision, and combination is supported. There is no comma-order override.
4. Freeze a resolved feature record for that operation. Tokenization, tree construction, feature-specific rendering rules, and execution checkpoints use that record.
5. If resolution fails, report an unsupported or invalid request before running profile-dependent source or applying a partial subset.

For profile-aware parsing APIs, invalid syntax throws `SyntaxError`; unsupported identifiers, dependencies, or combinations throw `NotSupportedError`, before parsing or DOM mutation. This proposal does not retrofit an options argument onto an existing API by implication; each participating API needs explicit specification.

For a recognized unsupported navigation request, the proposed failure is an inert diagnostic document, with source scripts and active subresources unprocessed. This is a proposed behavior in implementing browsers, not a protection that legacy browsers supply. Current browsers can ignore these public identifiers and parse legacy HTML normally. Authors therefore need a support/fallback strategy; the declaration alone is not a security boundary against older browsers.

## Selection and precedence across HTML, CSS, JavaScript, and tools

Each layer has a defined job. A later layer cannot silently replace an earlier operation's parsing contract.

| Operation or layer | Authoritative request | Conflict and inheritance rule |
| --- | --- | --- |
| HTML document navigation | Final response `HTML-Feature-Profile` header; initial source doctype only when the header is absent. | The header wins over a conflicting doctype. Resolve once; later declarations, registration, stylesheets, or scripts cannot replace it. |
| Future explicit profile-aware parse API | Its explicit per-call profile option. | A doctype in the input string is data for that operation, not a second selector. The caller's option governs; invalid or unsupported options fail before mutation. |
| Existing HTML string APIs | Their existing grammar. | They do not inherit the containing document's profile. An input string cannot silently opt them into a new grammar. |
| CSS | Normal cascade plus feature-specific rendering rules enabled by the resolved document record. | CSS cannot select or switch HTML tokenization. Author declarations can override user-agent rendering defaults only as the feature specification permits; protected behavior is not bypassed by a style rule. |
| JavaScript and custom elements | Explicit calls and feature APIs. | JavaScript cannot toggle the active document grammar, and registration timing cannot select a profile. DOM construction remains DOM construction, not source reparsing. |
| User-land compiler or server renderer | An explicit build/transform target. | Resolve it against a declared tool manifest. If it conflicts with emitted source intent, require an explicit conversion or report a diagnostic; do not silently add or remove capabilities. |
| User-land polyfill | Its explicit installation and transformation contract. | It cannot claim native support, change unrelated library parsing, or redefine the browser's native `next` manifest. |

The precedence rule is operation-local authority, not a global priority such as “JavaScript beats CSS.” A parse call, a document navigation, and a CSS declaration affect different contracts. The current document's resolved feature record governs feature-specific rendering and behavior for nodes inserted later, but does not change how a legacy string API recognized those nodes.

A profile is not a sandbox. Existing origin, CSP, Trusted Types, sanitizer, permissions, and script-execution rules still apply. A tool or script cannot acquire additional trust merely by choosing `next`.

## Proposed detection and resolved record

A candidate native API is `HTMLProfiles.supports(selector)`. It returns a boolean, performs no parsing, fetch, registration, or mutation, and checks the entire request including dependencies and composition. Invalid or unsupported requests return `false`.

A candidate read-only `document.htmlProfile` record exposes:

| Field | Proposed value |
| --- | --- |
| `requested` | Selector string, or `null` for ordinary HTML. |
| `features` | Immutable array of resolved identifiers, in canonical order. |
| `preset` | `"next"` or `null`. |
| `revision` | Resolved manifest revision string, or `null` for ordinary HTML. |
| `source` | `"header"`, `"doctype"`, `"api"`, or `"legacy"`. |
| `status` | `"active"`, `"legacy"`, or `"unsupported"`. |

These names and shapes need API review. The record reflects the parser's internal selection; changing the DOM doctype cannot change it. For header-selected documents, `requested` records the authoritative header selector and `source` is `"header"`. User-land objects with similar names are not native support evidence. A future worker or fragment API needs an operation result record rather than a mutable global default.

For an evolving preset, `supports("next")` says that the implementation supports its current documented preset, not that two browsers include identical experimental capabilities. Code that needs particular features must check the named combination and inspect the resolved record. Lack of the native API means support is not established; it does not authorize a polyfill to return a misleading native-success signal.

CSS feature queries retain their own meaning. `CSS.supports()` cannot establish support for an HTML parser profile. A future profile-aware CSS query would require separate syntax and privacy review; none is introduced here.

## Feature registration and composition

A feature specification must define its identifier, parser changes, applicability to DOM-created nodes, rendering and API behavior, dependencies, conflict rules, security obligations, support conditions, and compatibility with other preset features. It must state which behavior is user-agent default styling and which is a required semantic boundary.

A combined selector is supported only when the implementation supports the combination, not merely each feature in isolation. Self-closing and flexible nesting can both affect a marked host and later native rows; their parser checkpoint and shadow ownership interactions need explicit tests. Removing or failing one feature is an error, not a silent downgrade.

The registry and preset manifest need a governance and revision process before standardization. This proposal does not grant this publisher authority to define browser-wide experiments.

## Evidence and current implementation limits

The earlier self-closing experiments use the literal selector `next` and their pinned implementation rules. They establish the claims recorded in [that proposal's evidence](/self-closing-html/security), not support for this new named-list grammar, preset manifest system, detection API, failure document, or flexible nesting.

No native implementation of this orchestration proposal is reported. Required tests include header-only selection, header/doctype conflicts, malformed and repeated header fields, redirect isolation, iframe isolation, caching and intermediary handling, selector normalization and rejection, unsupported/dependency/conflict failures, fixed selection across scripts and doctype mutation, no accidental inheritance by legacy APIs, source/tool conflicts, preset revision stability during streaming, and combined feature execution. Compatibility tests must include historical doctypes and unsupported legacy browsers.

## Review requested

Review is requested on the response-header contract, selector grammar, the evolving preset's compatibility policy, unsupported-navigation behavior, operation-local precedence, detection API, and ownership of the registry and manifest. Discuss these separately from whether to adopt any individual feature in the [specifications repository](https://github.com/nextwebwg/specs/issues).

Editor: [Matthew Dean](https://github.com/matthew-dean). Independent Stage 0 proposal; not a W3C or WHATWG deliverable.

## Sources

::: {.details summary="Sources and prior art"}
[^1]: WHATWG HTML, [doctype syntax](https://html.spec.whatwg.org/multipage/syntax.html#the-doctype), [initial insertion mode](https://html.spec.whatwg.org/multipage/parsing.html#the-initial-insertion-mode), and [fragment parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-html-fragments). The proposed selectors change the platform contract; current doctype behavior is not implementation of this draft.

HTTP field syntax, repeated field lines, and caching follow [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-field-lines-and-combined-fie) [Structured Field Values](https://www.rfc-editor.org/rfc/rfc9651.html), and [HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html). The proposed field requires its own standardization and registration.
:::
