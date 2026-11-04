---
title: Security
order: 11
blurb: no eval · static resolution · trust
eyebrow: Declarative HTML Components Level 1
status: Level 1 · normative
---

# Security

HTML Next defines a **secure execution model**. Expressions cannot execute JavaScript; executable attributes and raw DOM sinks are rejected; text, markup, URLs, properties, imports, and controllers each pass through a sink-specific policy. A conforming implementation must fail closed when it cannot enforce one.

What that looks like in practice: expressions never run as code, dangerous sinks are unreachable by an ordinary binding, and dynamic content enters the DOM only through an operation that knows what kind of content it is receiving.

```html
<!-- Blocked: no expression is ever eval'd; a bound javascript: URL is dropped -->
<a from:href="$user.website">…</a>       <!-- javascript:… as the value → attribute removed -->
<button onclick="…">                 <!-- inline handler → non-conforming, rejected -->

<!-- Safe sinks are explicit -->
<h2 $value="$post.title">             <!-- textContent: markup stays text -->
<article $html="$post.body">          <!-- deterministic HTML parsing + the standard safe-default policy -->
```

## Secure by construction

The source language is deliberately less powerful than JavaScript. The compiler classifies every dynamic value by destination and emits only the operation permitted for that destination, so safety is settled when the component is built.

| Input or destination | Required handling |
| --- | --- |
| HTML Next expression | Parse with the closed expression grammar and evaluate against declared scope. No global lookup, prototype traversal, `eval()`, or generated function. |
| Text via `{expression}` or `$value` | Write through `textContent` or the target framework's text node operation, so markup is never interpreted. |
| Markup via `$html` | Parse as an inert HTML fragment in a `<template>` context and apply the versioned HTML Sanitizer safe-default policy before nodes become live. Do not dispatch to native `setHTML()`, whose parsing currently differs between engines. |
| URL-valued attribute | Parse and validate for that attribute's URL policy. Reject executable schemes and fail closed on an unparseable value. |
| DOM property binding | Resolve through the generated allowlist for the element interface. Raw-code and raw-markup sinks are not bindable. |
| Literal executable syntax | Reject inline `on*` handlers and target-framework directives. |
| Controller module | Accept only the definition carrier's explicit `controller` specifier. Resolve URL-like values from the definition and bare values through the application-owned import map, then use the standard module loader so CSP, CORS, and import-map integrity apply. |
| Declared script | Accept only `<script src>` in `<defs>`. Resolve `src` as a controller specifier is resolved, without the live-scope check, then insert one new, ordinary `<script>` element into `document.head` so CSP, CORS, mixed-content blocking, and `integrity` apply. |
| Head declaration | Accept only the [listed elements and `rel` keywords](/declarative-components/components#head-elements). Create new elements in the document, never insert the definition's nodes, and ignore an imported component's page-wide head entries. |

## Conformance requirements

1. The compiler and runtime [must not]{.kw} evaluate source through `eval()`, `new Function()`, or equivalent. Expressions are parsed by HTML Next's [restricted expression language](/declarative-components/expressions); names resolve only from the declared scope and built-in pure functions.
2. An implementation [must]{.kw} reject inline event-handler attributes, framework directive syntax, bindings to raw properties such as `innerHTML`, `outerHTML`, and `srcdoc`, and any destination for which it has no defined sink policy.
3. `{expression}` and `$value` [must]{.kw} produce text. `$html` [must]{.kw} sanitize with the standard safe configuration before insertion (see [Templating](/declarative-components/templating)). URL, style, and future trusted-content values [must]{.kw} use their own contextual parser and policy; generic escaping is not a substitute.
4. Every generated target [must]{.kw} preserve these checks. A converter may enforce a rule at compile time or emit a target-native runtime guard, but it [must not]{.kw} weaken a rule because React, Vue, Svelte, or the DOM exposes a more permissive sink.
5. Property resolution uses a generated [static manifest](/declarative-components/bindings) keyed by ASCII-lowercase name, never runtime prototype enumeration, and [must]{.kw} reject two properties that collapse to the same key rather than pick a winner.
6. A component definition may declare at most one controller, as the `controller` attribute on its `<template component>` carrier, and any number of [declared scripts](/declarative-components/components#declared-scripts) and JSON-LD data blocks in `<defs>`. Every other `<script>` element—inline executable scripts and every other `type`, including `type="importmap"`—inline code, executable event attributes, `<base>`, `<meta http-equiv>`, `<link rel="stylesheet">`, and HTML Imports are invalid anywhere in a definition.
7. A fetched definition [must]{.kw} be parsed as inert component data and [must not]{.kw} be inserted as an active document fragment. Registering a definition [must not]{.kw} change the document. [Head declarations](/declarative-components/components#head-declarations) take effect only while an instance is connected, through new elements the runtime creates, and an imported component's [page-wide head entries](/declarative-components/components#page-wide-head-entries) [must]{.kw} be ignored. Resource-level build metadata [must]{.kw} be ignored by the component loader. Only import maps in the application document participate in resolution. An imported definition cannot create, replace, merge, or widen an import map or live trust scope.
8. A URL-like component, controller, or declared-script reference [must]{.kw} be resolved and canonicalized against the final response URL of its containing definition. A bare reference [must]{.kw} resolve through the application-owned map. For component and controller references, redirect targets are checked after redirect handling; a redirect cannot escape the approved live scope. A declared script is gated only by the document's CSP, as below.
9. For packaged input, the installer or build resolves bare package subpaths through package metadata, validates the same graph, and emits application-owned assets; the browser live-trust procedure is not involved. For cross-origin live input, a direct application import selects a root inside an application-mapped URL prefix, or one the document's [`component-src` list](/declarative-components/components#page-wide-head-entries) names, which it may reference by URL. Relative edges may remain inside that prefix or listed source; leaving it requires another application-owned bare-specifier mapping. Declared scripts are not edges of this scope: a controller is the component's own code from its publisher, while a declared script is typically a third-party SDK from another origin, which the document's CSP governs.
10. The controller request [must]{.kw} use the standard module loader and obey the document's CSP and the platform's CORS and referrer-policy rules. URL-keyed integrity metadata generated in the application's import map applies to the module graph. A blocked, unresolved, out-of-scope, or failed controller leaves the declarative rendering in place and reports a diagnostic. A declared script is an ordinary script element under the same policies; when it is blocked or fails, its status reports the error, `on:error` runs, and the declarative rendering stays in place.
11. Content inserted through `$html`, CMS fields, slots accepting untrusted markup, or equivalent content sinks [must never]{.kw} be processed as a component-definition source. Sanitized content cannot register components, contribute dependency edges, or introduce controllers.
12. If an implementation cannot apply a required sanitizer, URL policy, property allowlist, declared integrity check, CSP decision, or CORS check, it [must]{.kw} reject the source or value. Silent pass-through is non-conforming.
{.algo}

> [!norm] Controllers have page authority
> A controller is ordinary JavaScript. Once evaluated, it can use `window`, `document`, storage, network APIs, and any other authority available to page script. The `host` object is a small, portable programming interface; it is **not** a capability membrane. ESM supplies a standard dependency graph, module scope, strict mode, CORS fetching, caching, and one-time evaluation. None of those properties confines what evaluated code may do.
>
> The inert-definition rule applies **before** code executes. A fetched definition cannot install an import map or otherwise modify application policy. A controller that has already been trusted and evaluated can manipulate the page and request anything ordinary page script can request—including attempting to add an import map under the browser's normal processing rules. At that point it already has page authority; pretending the component loader still contains it would be misleading.
>
> Therefore a component package that contains a controller is trusted application code, including the controller's transitive module graph. A definition that declares a script is trusted application code in exactly the same way. CSP limits where code may come from, and integrity pins which bytes may run, but neither makes trusted code untrusted. If code needs an actual authority boundary, it must run in a separate environment such as a Worker or sandboxed iframe and communicate through messages; that stronger isolation trades away direct page-DOM access.

## Component imports use the existing module loader

Importing a component with imperative behavior means trusting that behavior. HTML Next keeps the imported definition constrained and declarative, then loads its optional controller through the platform's existing ES module system. This provides a smaller, explicit format and one execution model; controller code keeps the full authority of other page JavaScript.

|  | HTML Imports | HTML Next component import |
| --- | --- | --- |
| **Imported unit** | An HTML `Document` with general markup, styles, dependencies, and scripts. | A definition constrained to the HTML Next component grammar. |
| **Imperative code** | General classic or module scripts could appear throughout imported documents. | Inline scripts and inline handlers are invalid. A definition may name one controller entry on its carrier and declare external scripts by URL in `<defs>`. |
| **Loading time** | Imported-document parsing defined script execution and ordering. | A controller loads as an ES module when its first component instance connects, or eagerly when the application imports it itself. A declared script is inserted when an instance connects, comes into view, or asks for it. |
| **Execution model** | A separate HTML-import document, dependency, parsing, and script-ordering model. | The existing JavaScript module loader, CSP, CORS, import maps, and integrity model. |
| **Authority after execution** | Page-level JavaScript authority. | Also page-level JavaScript authority. ESM does not improve this part. |

The old HTML Imports proposal was [explicit that scripting was enabled in imported documents](https://www.w3.org/TR/html-imports/); it has since been [retired by W3C](https://www.w3.org/standards/history/html-imports/). Its difficulty was broader than “too many script tags”: an HTML-document dependency graph also needed rules for parsing, parser blocking, transitive script order, style order, deduplication, `document.currentScript`, and custom-element upgrades. It created a second loading and execution model alongside JavaScript modules, while a content import still carried page-authority code.

HTML Next keeps the defensible parts and claims only the boundaries that exist. A definition cannot hide arbitrary executable syntax among its markup: it has a closed declarative grammar and, when imperative behavior is necessary, one visible `controller` specifier on the carrier and visible `src` URLs for any third-party scripts. That module uses the existing JavaScript loader and its CSP, CORS, caching, import-map resolution, integrity behavior, and script ordering.

> [!norm] Trust the root, constrain the closure
> An application approves a component root, not a hand-copied list of everything below it. That is the useful trust boundary shared by ES-module, package, and iframe imports. The component definition only declares dependencies; it cannot carry consumer approval or change the application's map. Requiring approval for every transitive controller would add ceremony without creating a sandbox.

### Shared stylesheet resources

Stylesheets reached through a component's CSS `@import` are part of its declarative resource graph. A live loader [must]{.kw} resolve each import against its containing source, check the final response URL against the containing component's approved live scope, and enforce the application's CSP and the CORS requirements for reading and transforming cross-origin CSS. URL resolution alone does not authorize a fetch. A CSS import cannot widen a live trust scope; ordinary CSS URL strings do not acquire JavaScript import-map resolution. Packaged builds use their host resolver and application-owned asset graph instead, as defined in [Style Scoping](/declarative-components/styling#shared-css).

Component scoping constrains selector matching, not resource requests. Fonts, images, and other assets referenced by imported CSS retain their original source bases and the platform's normal resource policies. An implementation [must not]{.kw} activate an unscoped sheet as a fallback when its contents cannot be read or transformed. The application's policies govern both fetching source CSS and applying the generated styles; a JavaScript loader using Fetch remains subject to `connect-src` as well as the applicable style policy.

### Packaged components do not use live trust

Installing a package already admits its controller code to the application's software supply chain. The build resolves a concrete exported HTML subpath, walks its component and controller edges, follows static ESM imports, and emits application-owned assets. The package lock records versions and the normal review/build pipeline handles updates. A second runtime permission list would duplicate that bookkeeping without containing malicious installed code.

### Live components use an application-owned trust root {#live-components-use-an-application-owned-trust-root}

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
> This is an affirmative reason to standardize Declarative Components in browsers. A native implementation can enforce the final-target rule inside module fetching, before controller evaluation, and provide a consistent security guarantee that userland code cannot reproduce.

| Distribution | Resolution and security |
| --- | --- |
| Installed package | Package exports resolve concrete files. The lockfile and build own the resulting graph and its approval. |
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

A normal packaged application may reasonably rely on its lockfile, same-origin HTTPS deployment, CSP, and content-hashed build assets. Live cross-origin entry points may carry generated integrity metadata and must satisfy CORS. Build tooling calculates the hashes. A high-assurance deployment can pin more of the graph and adopt [`Integrity-Policy`](https://developer.mozilla.org/docs/Web/HTTP/Reference/Headers/Integrity-Policy) as browser support matures.

## Head declarations and declared scripts {#head-declarations}

A component can add a title, metadata, links, and JSON-LD to the document head, and can name the external scripts it needs, as [head declarations](/declarative-components/components#head-declarations) in its `<defs>`. A checkout form can load Stripe.js; a page can set its title and canonical link. Three rules keep this safe:

1. **No hidden code.** A definition never contains executable code. Code enters only through declared, visible references, the carrier's `controller` and each `<script src>` in `<defs>`, which the platform loads under the page's CSP.
2. **Importing is pure.** Fetching and registering a definition runs nothing and changes nothing in the document. Effects start only when an instance connects.
3. **No borrowed authority.** Importing a component does not give it control of the application's document. Policy elements are invalid everywhere, and [page-wide head entries](/declarative-components/components#page-wide-head-entries) apply only from the application's own components.
{.algo}

**Using a component is trusting it.** This is the position the rest of this chapter takes for controllers: the application approves a root, not every edge. A declared script has page authority once it runs, so a definition that declares one is trusted application code, exactly like one with a controller. The same approval covers scripts, whichever component declares them, from the application, an installed package, or a live import. The platform's control over which code runs is CSP, and builds and developer tools list every declared script URL.

Browsers have no default CSP. Without one, a declared script loads like any other code the page includes. Application tooling [should]{.kw} generate a CSP from the declared graph: the controllers and declared script URLs it already lists.

The one allowlist in this design is the [`component-src` list](/declarative-components/components#page-wide-head-entries). It protects the page's identity and page-wide behavior, which CSP does not cover.

| Threat | Rule that covers it |
| --- | --- |
| A component smuggles in code. | An inline executable `<script>`, any other script type, and event-handler attributes are invalid in a definition. The runtime creates new elements and never inserts the definition's own nodes, so a parsed `<script>` cannot run by being cloned into the document. Every script is a visible `src`, and a build lists every declared script URL. |
| Importing a component has an effect. | Registration inserts nothing. Head contributions and scripts wait for a connected instance, and `lazy` and `manual` scripts wait longer. |
| A component takes over document policy. | `<meta http-equiv>`, which can set a CSP, a refresh, or cookies; `<base>`, which would rebase every relative URL; import maps; and the render-blocking `blocking` attribute are invalid in a definition. Only the application document's import map resolves bare names. |
| A component hijacks the document's search identity. | `canonical`, `alternate`, `robots`, `icon`, `manifest`, and `og:url` are page-wide head entries. An imported component's are ignored, with a diagnostic. Only the application's authored `component-src` list decides which sources are the application's own. |
| A component changes the referrer policy, viewport, or color scheme. | `referrer`, `viewport`, `color-scheme`, and `theme-color` are page-wide head entries too. |
| A network attacker swaps a script in transit. | The inserted element follows HTML's rules: mixed-content blocking stops an `http:` script on an `https:` page, and `integrity` rejects changed bytes. Declare HTTPS URLs, and add `integrity` to versioned ones. |
| A third-party script host is compromised. | A versioned URL can carry `integrity`, which pins its bytes. An evergreen SDK such as Stripe.js cannot be pinned: loading it is an explicit trust decision the application makes, visible in the markup and in the build's script list. It is the same decision as a hand-written `<script>` tag today. |
| A component pings a tracker through `preconnect`, `preload`, or a script URL. | No new capability: a component can already make a request to any origin with `<img src>` or `<data src>`. CSP governs each fetch by its destination, as it does for any element. |
| Tags stay behind after navigation. | Contributions are removed when their last contributor disconnects, and a title falls back to the next contributor or to the application's own element, restored as the same node. Only scripts stay, because code that has run cannot be unloaded. |
| A script runs twice. | The head holds one element per script URL and type, never removed and never reinserted. Server rendering writes an eager script only as a `preload` link, never as a `<script>`, and the client inserts the real element once. |
| A component declares a script the application did not expect. | Using the component is trusting it, as with its controller. The document's CSP decides whether the script loads, and builds and developer tools list every declared script URL for review. |

**What already exists.** A `<data>` resource already fetches from declared URLs, and images and CSS already request any origin. A controller already has page authority, including the power to insert any script it likes. Head declarations make the common cases declarative and visible; they do not widen what a trusted component can do. They narrow what an imported one can do, because its page-wide head entries are ignored, where a controller's DOM writes would not be.

### Declared scripts under a Content Security Policy

A declared script is an ordinary element, so a typical policy covers it unchanged. An origin allowlist names the script's origin:

```text title="HTTP response header"
Content-Security-Policy: script-src 'self' https://js.stripe.com
```

A nonce-based policy with `'strict-dynamic'` trusts the scripts a trusted script inserts, which is how the polyfill runtime's insertions load. A native implementation has no inserting script, so it copies the `nonce` of the application element that imported the definition onto the scripts that definition's graph inserts. The application grants that trust by placing its nonce on the import, as it would on a `<script>`:

```html
<!-- Content-Security-Policy: script-src 'nonce-r4nd0m' 'strict-dynamic' -->
<link rel="component" href="./checkout-form.html" nonce="r4nd0m">
```

A build lists every declared script URL beside the controllers, with the component that declares each one, so the application can review its scripts and generate its `script-src`.
