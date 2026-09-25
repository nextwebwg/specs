---
title: Security
order: 11
blurb: no eval · static resolution · trust
eyebrow: Declarative HTML Components Level 1
status: Level 1 · normative
---

# Security

HTML Next defines a **secure execution model**, not a collection of optional precautions. Expressions cannot execute JavaScript; executable attributes and raw DOM sinks are rejected; text, markup, URLs, properties, imports, and controllers each pass through a sink-specific policy. A conforming implementation must fail closed when it cannot enforce one.

What that looks like in practice: expressions never run as code, dangerous sinks are unreachable by an ordinary binding, and dynamic content enters the DOM only through an operation that knows what kind of content it is receiving.

```html
<!-- Blocked: no expression is ever eval'd; a bound javascript: URL is dropped -->
<a :href="user.website">…</a>       <!-- javascript:… as the value → attribute removed -->
<button onclick="…">                 <!-- inline handler → non-conforming, rejected -->

<!-- Safe sinks are explicit -->
<h2 $value="post.title">             <!-- textContent: markup stays text -->
<article $html="post.body">          <!-- Sanitizer API or a conforming equivalent -->
```

## Secure by construction

The source language is deliberately less powerful than JavaScript. The compiler does not accept arbitrary executable markup and hope an application configures it safely later; it classifies every dynamic value by destination and emits only the operation permitted for that destination.

| Input or destination | Required handling |
| --- | --- |
| HTML Next expression | Parse with the closed expression grammar and evaluate against declared scope. No global lookup, prototype traversal, `eval()`, or generated function. |
| Text via `$value` | Write through `textContent` or the target framework's text node operation, so markup is never interpreted. |
| Markup via `$html` | Use the HTML Sanitizer API with the HTML Next safe configuration, or a conforming equivalent, before nodes become live. |
| URL-valued attribute | Parse and validate for that attribute's URL policy. Reject executable schemes and fail closed on an unparseable value. |
| DOM property binding | Resolve through the generated allowlist for the element interface. Raw-code and raw-markup sinks are not bindable. |
| Literal executable syntax | Reject inline `on*` handlers and target-framework directives rather than copying them through. |
| Controller module | Accept only the definition carrier's explicit `controller` specifier. Resolve URL-like values from the definition and bare values through the application-owned import map, then use the standard module loader so CSP, CORS, and import-map integrity apply. |

## Conformance requirements

1. The compiler and runtime [must not]{.kw} evaluate source through `eval()`, `new Function()`, or equivalent. Expressions are parsed by HTML Next's [restricted expression language](/html-next/expressions); names resolve only from the declared scope and built-in pure functions.
2. An implementation [must]{.kw} reject inline event-handler attributes, framework directive syntax, bindings to raw properties such as `innerHTML`, `outerHTML`, and `srcdoc`, and any destination for which it has no defined sink policy.
3. `$value` [must]{.kw} produce text. `$html` [must]{.kw} sanitize with the standard safe configuration before insertion (see [Templating](/html-next/templating)). URL, style, and future trusted-content values [must]{.kw} use their own contextual parser and policy; generic escaping is not a substitute.
4. Every generated target [must]{.kw} preserve these checks. A converter may enforce a rule at compile time or emit a target-native runtime guard, but it [must not]{.kw} weaken a rule because React, Vue, Svelte, or the DOM exposes a more permissive sink.
5. Property resolution uses a generated [static manifest](/html-next/bindings) keyed by ASCII-lowercase name, never runtime prototype enumeration, and [must]{.kw} reject two properties that collapse to the same key rather than pick a winner.
6. A component definition may declare at most one controller, as the `controller` attribute on its `<template component>` carrier. Arbitrary `<script>` elements—including `type="importmap"`—inline code, executable event attributes, `<base>`, and policy-changing `<meta>` elements are invalid anywhere in a definition.
7. A fetched definition [must]{.kw} be parsed as inert component data and [must not]{.kw} be inserted as an active document fragment. Only import maps in the application document participate in resolution. An imported definition cannot create, replace, merge, or widen an import map or live trust scope.
8. A URL-like component or controller reference [must]{.kw} be resolved and canonicalized against the final response URL of its containing definition. A bare reference [must]{.kw} resolve through the application-owned map. Redirect targets are checked after redirect handling; a redirect cannot escape the approved live scope.
9. For packaged input, the installer or build resolves bare package subpaths through package metadata, validates the same graph, and emits application-owned assets; the browser live-trust procedure is not involved. For cross-origin live input, a direct application import selects a root inside an application-mapped URL prefix. Relative edges may remain inside that prefix; leaving it requires another application-owned bare-specifier mapping.
10. The controller request [must]{.kw} use the standard module loader and obey the document's CSP and the platform's CORS and referrer-policy rules. URL-keyed integrity metadata generated in the application's import map applies to the module graph. A blocked, unresolved, out-of-scope, or failed controller leaves the declarative rendering in place and reports a diagnostic.
11. Content inserted through `$html`, CMS fields, slots accepting untrusted markup, or equivalent content sinks [must never]{.kw} be processed as a component-definition source. Sanitized content cannot register components, contribute dependency edges, or introduce controllers.
12. If an implementation cannot apply a required sanitizer, URL policy, property allowlist, declared integrity check, CSP decision, or CORS check, it [must]{.kw} reject the source or value. Silent pass-through is non-conforming.
{.algo}

> [!norm] Controllers have page authority
> A controller is ordinary JavaScript. Once evaluated, it can use `window`, `document`, storage, network APIs, and any other authority available to page script. The `host` object is a small, portable programming interface; it is **not** a capability membrane. ESM supplies a standard dependency graph, module scope, strict mode, CORS fetching, caching, and one-time evaluation. None of those properties confines what evaluated code may do.
>
> The inert-definition rule applies **before** code executes. A fetched definition cannot install an import map or otherwise modify application policy. A controller that has already been trusted and evaluated can manipulate the page and request anything ordinary page script can request—including attempting to add an import map under the browser's normal processing rules. At that point it already has page authority; pretending the component loader still contains it would be misleading.
>
> Therefore a component package that contains a controller is trusted application code, including the controller's transitive module graph. CSP limits where code may come from, and integrity pins which bytes may run, but neither makes trusted code untrusted. If code needs an actual authority boundary, it must run in a separate environment such as a Worker or sandboxed iframe and communicate through messages; that stronger isolation trades away direct page-DOM access.

## Component imports use the existing module loader

Importing a component with imperative behavior means trusting that behavior. HTML Next keeps the imported definition constrained and declarative, then loads its optional controller through the platform's existing ES module system. This provides a smaller, explicit format and one execution model; it does not make controller code less authoritative than other page JavaScript.

|  | HTML Imports | HTML Next component import |
| --- | --- | --- |
| **Imported unit** | An HTML `Document` with general markup, styles, dependencies, and scripts. | A definition constrained to the HTML Next component grammar. |
| **Imperative code** | General classic or module scripts could appear throughout imported documents. | Arbitrary scripts and inline handlers are invalid. A definition may name one controller entry on its carrier. |
| **Loading time** | Imported-document parsing defined script execution and ordering. | A controller loads as an ES module when its first component instance connects, or eagerly when the application imports it itself. |
| **Execution model** | A separate HTML-import document, dependency, parsing, and script-ordering model. | The existing JavaScript module loader, CSP, CORS, import maps, and integrity model. |
| **Authority after execution** | Page-level JavaScript authority. | Also page-level JavaScript authority. ESM does not improve this part. |

The old HTML Imports proposal was [explicit that scripting was enabled in imported documents](https://www.w3.org/TR/html-imports/); it has since been [retired by W3C](https://www.w3.org/standards/history/html-imports/). Its difficulty was broader than “too many script tags”: an HTML-document dependency graph also needed rules for parsing, parser blocking, transitive script order, style order, deduplication, `document.currentScript`, and custom-element upgrades. It created a second loading and execution model alongside JavaScript modules, while a content import still carried page-authority code.

HTML Next keeps the defensible parts without claiming a security boundary that is not there. A definition cannot hide arbitrary executable syntax among its markup: it has a closed declarative grammar and, when imperative behavior is necessary, one visible `controller` specifier on the carrier. That module uses the existing JavaScript loader and its CSP, CORS, caching, import-map resolution, and integrity behavior. There is no imported-document global, parser-blocking script lifecycle, or second script-ordering system.

> [!norm] Trust the root, constrain the closure
> An application approves a component root, not a hand-copied list of everything below it. That is the useful trust boundary shared by ES-module, package, and iframe imports. The component definition only declares dependencies; it cannot carry consumer approval or change the application's map. Requiring approval for every transitive controller would add ceremony without creating a sandbox.

### Packaged components do not use live trust

Installing a package already admits its controller code to the application's software supply chain. The build resolves a concrete exported HTML subpath, walks its component and controller edges, follows static ESM imports, and emits application-owned assets. The package lock records versions and the normal review/build pipeline handles updates. A second runtime permission list would duplicate that bookkeeping without containing malicious installed code.

### Live components use an application-owned trust root

Live cross-origin loading is different because the publisher can change bytes without an application dependency update. The application maps a package-like prefix to a selected, preferably versioned HTTPS location, then imports a concrete root. The definition is unchanged:

```html
<script type="importmap">
{
  "imports": {
    "@acme/ui/": "https://cdn.example/@acme/ui@4/components/"
  }
}
</script>

<!-- The application selects one concrete root inside that live scope. -->
<link rel="component" href="@acme/ui/dashboard.html" crossorigin>
```

The mapped target prefix is the live scope for the definition graph. Relative component links and carrier `controller` references can remain within it. A declarative edge outside it must use another bare specifier that the application maps; an absolute or normalized path escape fails. Import maps found in fetched definitions are invalid and inert.

After a controller starts, its own static and dynamic imports are the ordinary ESM graph. Today CSP can constrain their origins, but neither CSP nor an import-map prefix creates a directory-level sandbox. That is appropriate for code the application chose to trust, and it is why a mutable live publisher is a stronger trust decision than installing reviewed, locked package bytes. Prefer versioned immutable live URLs; use tool-generated integrity when publisher compromise or unreviewed updates are in scope. The current polyfill's definition fetches and controller modules remain subject to application CSP:

```html title="HTTP response header"
Content-Security-Policy:
  default-src 'self';
  connect-src 'self' https://cdn.example;
  script-src 'self' https://cdn.example
```

> [!note] The controller redirect check needs browser integration
> The final-target rule above is a requirement on a native implementation. The current polyfill can check a component response's final URL before registration and can reject an out-of-scope controller entry before calling `import()`. Native module loading does not expose the controller's final response URL before evaluation, so a polyfill cannot independently reject a redirect after the browser accepts that entry. CORS, CSP, and applicable integrity metadata still govern the module request; enforcing the live-scope redirect rule itself requires integration with the browser's module loader.
>
> This is an affirmative reason to standardize Declarative Components in browsers, not merely a polyfill limitation. A native implementation can enforce the final-target rule inside module fetching, before controller evaluation, and provide a consistent security guarantee that userland code cannot reproduce.

| Distribution | Resolution and security |
| --- | --- |
| Installed package | Package exports resolve concrete files. The lockfile and build own the resulting graph; no browser import map or live approval ceremony is required. |
| First-party source | Relative or root-relative references resolve inside the application and remain under its ordinary CSP. |
| Live cross-origin source | The application maps one prefix to the remote tree, imports a concrete root, and allows the necessary origins through CSP. CORS must succeed. Optional generated integrity can pin selected or complete static graph bytes. |

This follows the useful shape of [iframe embedded policy](https://www.w3.org/TR/csp-embedded-enforcement/)—select one root and constrain its subtree—but not its isolation claim. An iframe has a separate document and can be sandboxed. An inline controller that receives ordinary page-DOM access is trusted same-realm JavaScript. Code that must remain untrusted needs a Worker-compatible controller API or a sandboxed iframe, with message passing instead of direct DOM access.

### Integrity is risk-based

| Mechanism | What it protects | What it does not do |
| --- | --- | --- |
| Package lock and build | Fix the installed package versions and emit a known application asset graph. | Do not make package code trustworthy; review and supply-chain controls still matter. |
| CSP and CORS | Constrain permitted script origins and cross-origin loading under the platform's existing rules. | An allowed origin can serve more than one file; controller code still has page authority. |
| [Subresource Integrity](https://www.w3.org/TR/sri-2/) | Detects changed bytes, especially useful for a live CDN or independently hosted dependency. | Does not protect against code that was malicious when selected, and adds little when an attacker can also rewrite the application document and its hashes. |
| Worker or sandboxed iframe | Creates an actual authority boundary for code that is not trusted with the page. | Does not provide direct DOM access; integration must use messages. |

A normal packaged application may reasonably rely on its lockfile, same-origin HTTPS deployment, CSP, and content-hashed build assets. Live cross-origin entry points may carry generated integrity metadata and must satisfy CORS. Authors should never calculate hashes by hand. A high-assurance deployment—not the general default—can pin more of the graph and adopt [`Integrity-Policy`](https://developer.mozilla.org/docs/Web/HTTP/Reference/Headers/Integrity-Policy) as browser support matures.
