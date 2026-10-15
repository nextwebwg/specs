---
title: Requests Explainer
order: 6.5
blurb: use cases · three shapes · late providers · framework mirroring
eyebrow: Declarative HTML Components · explainer for review
status: Non-normative · accompanies the proposed Requests section
pager: false
---

# Requests Explainer

This page accompanies the proposed [Requests](/declarative-components/javascript#requests) section of the JavaScript Layer. It is for the editors deciding that proposal. Five real use cases are worked through under three candidate shapes, with the code that every kind of author writes for each one, so the shapes can be judged by the code they produce rather than by a list of criteria.

> [!warn] Explainer for review
> Nothing on this page is normative. The proposal's text is in the [JavaScript Layer](/declarative-components/javascript#requests). Two decisions are already made: the shape is **A**, requests ([why](#b-against-a)), and when nobody answers, the asker receives `null`.

## The three shapes

Each shape lets a component get behavior from its consumer without a function-valued prop. They differ in what the component declares, how it asks, and how the consumer answers.

| Shape | The component declares | Its controller asks | The consumer answers |
| --- | --- | --- | --- |
| **A. Requests** (drafted) | `<request name type returns>` | `host.request(name, detail, { signal })`, which resolves to the answer or `null` | a listener calls `event.respondWith(answer)` |
| **B. Answerable events** | `<event name type returns>`: an ordinary event with a `returns` type | `host.dispatch(name, detail, { signal })`, which returns a promise because the event declares `returns` | the same listener and `respondWith` as A |
| **C. Provided capabilities** | `<capability name type returns>` | `host.use(name)` returns the nearest ancestor's function, or `null`, and the controller calls it | an ancestor provides a function: `host.provide(name, fn)`, a page-level `provide()`, or a framework provider |

A and B share one mechanism: a bubbling `RequestEvent` with `signal` and `respondWith`. They differ only in the declaration and the asking call, so every use case below is the same length in both: the component's code differs by two names (`<request>` or `<event returns>`, `host.request` or `host.dispatch`), and the consumers' code is identical. In B, a plain event and an answerable one sit side by side, and `returns` is what tells them apart:

```html
<defs>
  <event name="change" type="object({ content: unknown })"></event>
  <event name="mention-query" type="object({ query: string })"
    returns="list(object({ id: string, label: string }))"></event>
</defs>
```

```js
host.dispatch("change", { content });                                  // true or false, as today
const people = await host.dispatch("mention-query", { query }, { signal }); // a promise, because of returns
```

C is the context-like option. It looks up the nearest provider along the [logical component tree](/declarative-components/components), as `<context>` does, and the consumer supplies a function `(detail, { signal }) => answer`.

### The audiences and helpers

Each use case shows code for six audiences: **(i)** the component author, with the declaration and the controller; **(ii)** a plain HTML page with a page script; **(iii)** an HTML Next component with a controller; **(iv)** Vue; **(v)** React; and **(vi)** Svelte. The framework snippets use the event-binding form. [Framework mirroring](#framework-mirroring) shows the function-prop form.

The consumer snippets call application helpers, imported from the application's own module: `searchPeople(query, signal)`, `uploadImage(file, { signal, onprogress })`, `lookupTitle(href)`, `isLocal(href)`, and `fetchOrders(page, signal)` / `fetchPeople(page, signal)`. Each returns a promise.

## 1. Mention lookup while typing

The author types `@a`, then `@ad`, then `@ada`. Each keystroke asks the consumer for matching people. The answer to `@ad` must never replace the answer to `@ada`, so each new query aborts the previous one, and the consumer's network request is cancelled with it.

### A · requests {#mention-a}

```html title="(i) ui-editor.html"
<request name="mention-query" type="object({ query: string })"
  returns="list(object({ id: string, label: string }))">People matching the text after @.</request>
```

```js title="(i) ui-editor.js"
let pending;
session.onMentionQuery = (query) => {
  pending?.abort();                                   // the previous keystroke's request
  pending = new AbortController();
  host.request("mention-query", { query }, { signal: pending.signal })
    .then((people) => session.showMentions(people ?? []), () => {}); // rejected: superseded
};
```

```html title="(ii) page.html"
<ui-editor></ui-editor>
<script type="module">
  import { searchPeople } from "./app.js";
  document.addEventListener("mention-query", (event) =>
    event.respondWith(searchPeople(event.detail.query, event.signal)));
</script>
```

```js title="(iii) x-notes.js"
export default function controller(host) {
  host.on("mention-query", (event) =>
    event.respondWith(searchPeople(event.detail.query, event.signal)));
}
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @mention-query="(e) => e.respondWith(searchPeople(e.detail.query, e.signal))" />
<UiEditor onMentionQuery={(e) => e.respondWith(searchPeople(e.detail.query, e.signal))} />
<UiEditor onmention-query={(e) => e.respondWith(searchPeople(e.detail.query, e.signal))} />
```

### B · answerable events {#mention-b}

```html title="(i) ui-editor.html"
<event name="mention-query" type="object({ query: string })"
  returns="list(object({ id: string, label: string }))">People matching the text after @.</event>
```

```js title="(i) ui-editor.js"
let pending;
session.onMentionQuery = (query) => {
  pending?.abort();                                   // the previous keystroke's request
  pending = new AbortController();
  // dispatch returns a promise because the event declares returns
  host.dispatch("mention-query", { query }, { signal: pending.signal })
    .then((people) => session.showMentions(people ?? []), () => {}); // rejected: superseded
};
```

Consumers (ii) to (vi) are identical to A, because the event they receive is the same `RequestEvent`:

```js title="(ii) page script · (iii) controller"
document.addEventListener("mention-query", (e) => e.respondWith(searchPeople(e.detail.query, e.signal)));
host.on("mention-query", (e) => e.respondWith(searchPeople(e.detail.query, e.signal)));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @mention-query="(e) => e.respondWith(searchPeople(e.detail.query, e.signal))" />
<UiEditor onMentionQuery={(e) => e.respondWith(searchPeople(e.detail.query, e.signal))} />
<UiEditor onmention-query={(e) => e.respondWith(searchPeople(e.detail.query, e.signal))} />
```

### C · provided capabilities {#mention-c}

```html title="(i) ui-editor.html"
<capability name="mention-query" type="object({ query: string })"
  returns="list(object({ id: string, label: string }))">People matching the text after @.</capability>
```

```js title="(i) ui-editor.js"
session.onMentionQuery = (query) => {
  pending?.abort();
  const signal = (pending = new AbortController()).signal;
  const search = host.use("mention-query");           // the nearest provider's function, or null
  if (search === null) return session.showMentions([]);
  Promise.resolve(search({ query }, { signal }))
    .then((people) => { if (!signal.aborted) session.showMentions(people); }, () => {});
};
```

The author guards against a stale answer by hand: a plain function call has no runtime step that drops a late answer or checks its type. If the runtime wrapped the function to do both, C would become A with a function call in place of an event.

```js title="(ii) page script · (iii) controller"
import { provide } from "@nextwebwg/html";            // a page-level API C needs and A does not
provide(document.body, "mention-query", ({ query }, { signal }) => searchPeople(query, signal));

host.provide("mention-query", ({ query }, { signal }) => searchPeople(query, signal));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<!-- Vue, in the consumer's <script setup> -->
provideCapability("mention-query", ({ query }, { signal }) => searchPeople(query, signal));
<!-- React -->
<Capability name="mention-query" value={({ query }, { signal }) => searchPeople(query, signal)}>
  <UiEditor />
</Capability>
<!-- Svelte, in the consumer's <script> -->
setCapability("mention-query", ({ query }, { signal }) => searchPeople(query, signal));
```

## 2. Image upload with progress and cancel

The author drops a photo. A placeholder appears with a progress bar and a cancel button. Pressing cancel, or deleting the placeholder, aborts the upload. When the upload finishes, the image takes its uploaded `src`. With no uploader, the editor keeps a local preview.

A single answer cannot carry progress. A and B therefore need a progress channel, which the draft does not yet have. This explainer proposes the smallest one: a `progress` callback in the asker's options, and `event.progress(loaded, total)` on the `RequestEvent`, which the runtime forwards to it while the request is pending ([open question 6](#decisions)).

### A · requests {#upload-a}

```html title="(i) ui-editor.html"
<request name="image-upload" type="object">
  <prop name="file" type="unknown" required>The dropped or pasted File.</prop>
  <returns type="object">
    <prop name="src" type="string" required></prop>
  </returns>
</request>
```

```js title="(i) ui-editor.js"
session.onImageDrop = (file, placeholder) => {
  const upload = new AbortController();
  placeholder.onCancel = () => upload.abort();       // the cancel button, or deleting the node
  host.request("image-upload", { file }, {
    signal: upload.signal,
    progress: (loaded, total) => placeholder.setProgress(loaded / total),
  }).then((image) => image ? placeholder.setSrc(image.src) : placeholder.keepPreview(),
          () => placeholder.remove());
};
```

```html title="(ii) page.html"
<ui-editor></ui-editor>
<script type="module">
  import { uploadImage } from "./app.js";            // XMLHttpRequest, for upload progress
  document.addEventListener("image-upload", (event) =>
    event.respondWith(uploadImage(event.detail.file, {
      signal: event.signal,
      onprogress: (loaded, total) => event.progress(loaded, total),
    })));
</script>
```

```js title="(iii) x-notes.js"
host.on("image-upload", (event) => event.respondWith(uploadImage(event.detail.file, {
  signal: event.signal,
  onprogress: (loaded, total) => event.progress(loaded, total),
})));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @image-upload="(e) => e.respondWith(uploadImage(e.detail.file,
  { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))" />
<UiEditor onImageUpload={(e) => e.respondWith(uploadImage(e.detail.file,
  { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))} />
<UiEditor onimage-upload={(e) => e.respondWith(uploadImage(e.detail.file,
  { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))} />
```

### B · answerable events {#upload-b}

```html title="(i) ui-editor.html"
<event name="image-upload" type="object">
  <prop name="file" type="unknown" required>The dropped or pasted File.</prop>
  <returns type="object">
    <prop name="src" type="string" required></prop>
  </returns>
</event>
```

```js title="(i) ui-editor.js"
session.onImageDrop = (file, placeholder) => {
  const upload = new AbortController();
  placeholder.onCancel = () => upload.abort();       // the cancel button, or deleting the node
  host.dispatch("image-upload", { file }, {
    signal: upload.signal,
    progress: (loaded, total) => placeholder.setProgress(loaded / total),
  }).then((image) => image ? placeholder.setSrc(image.src) : placeholder.keepPreview(),
          () => placeholder.remove());
};
```

The consumers are identical to A:

```js title="(ii) page script · (iii) controller"
document.addEventListener("image-upload", (e) => e.respondWith(uploadImage(e.detail.file, { signal: e.signal, onprogress: (l, t) => e.progress(l, t) })));
host.on("image-upload", (e) => e.respondWith(uploadImage(e.detail.file, { signal: e.signal, onprogress: (l, t) => e.progress(l, t) })));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @image-upload="(e) => e.respondWith(uploadImage(e.detail.file, { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))" />
<UiEditor onImageUpload={(e) => e.respondWith(uploadImage(e.detail.file, { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))} />
<UiEditor onimage-upload={(e) => e.respondWith(uploadImage(e.detail.file, { signal: e.signal, onprogress: (l, t) => e.progress(l, t) }))} />
```

### C · provided capabilities {#upload-c}

C handles progress most naturally: the provider is an ordinary function, so `progress` is just another option it receives.

```html title="(i) ui-editor.html"
<capability name="image-upload" type="object">
  <prop name="file" type="unknown" required>The dropped or pasted File.</prop>
  <returns type="object">
    <prop name="src" type="string" required></prop>
  </returns>
</capability>
```

```js title="(i) ui-editor.js"
const upload = host.use("image-upload");
if (upload === null) return placeholder.keepPreview();
const abort = new AbortController();
placeholder.onCancel = () => abort.abort();
Promise.resolve(upload({ file }, { signal: abort.signal, progress: (l, t) => placeholder.setProgress(l / t) }))
  .then((image) => { if (!abort.signal.aborted) placeholder.setSrc(image.src); }, () => placeholder.remove());
```

```js title="(ii) page script · (iii) controller"
provide(document.body, "image-upload", ({ file }, { signal, progress }) => uploadImage(file, { signal, onprogress: progress }));
host.provide("image-upload", ({ file }, { signal, progress }) => uploadImage(file, { signal, onprogress: progress }));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
provideCapability("image-upload", ({ file }, { signal, progress }) => uploadImage(file, { signal, onprogress: progress }));
<Capability name="image-upload" value={({ file }, { signal, progress }) => uploadImage(file, { signal, onprogress: progress })}><UiEditor /></Capability>
setCapability("image-upload", ({ file }, { signal, progress }) => uploadImage(file, { signal, onprogress: progress }));
```

## 3. Supplying Tiptap extensions

An application adds its own Tiptap extensions, such as highlighting. These are JavaScript objects, needed once, when the editor builds its view. Every connection rebuilds the view, keeping the document and undo history in the controller's closure, so this request is asked once per connection. It is the use case that [late providers](#late-providers) affect.

### A · requests {#extensions-a}

```html title="(i) ui-editor.html"
<request name="extensions" returns="list(unknown)">Tiptap extensions added to the built-in set.</request>
```

```js title="(i) ui-editor.js"
host.on("connect", () => {
  let session;
  host.request("extensions").then((extensions) => {
    session = createEditorSession(host.refs.mount, { extensions: extensions ?? [] });
  }, () => {});                                       // rejected: disconnected before the answer
  return () => session?.destroy();
});
```

```html title="(ii) page.html"
<!-- Listen before the runtime starts, so the editor's first connection finds the listener. -->
<script type="module">
  import Highlight from "@tiptap/extension-highlight";
  document.addEventListener("extensions", (event) => event.respondWith([Highlight]));
</script>
<script type="module" src="/htmlnext.js"></script>
<ui-editor></ui-editor>
```

```js title="(iii) x-notes.js"
import Highlight from "@tiptap/extension-highlight";
export default function controller(host) {
  host.on("extensions", (event) => event.respondWith([Highlight]));   // reached by draft step 4
}
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @extensions="(e) => e.respondWith([Highlight])" />
<UiEditor onExtensions={(e) => e.respondWith([Highlight])} />
<UiEditor onextensions={(e) => e.respondWith([Highlight])} />
```

### B · answerable events {#extensions-b}

```html title="(i) ui-editor.html"
<event name="extensions" returns="list(unknown)">Tiptap extensions added to the built-in set.</event>
```

```js title="(i) ui-editor.js"
host.on("connect", () => {
  let session;
  host.dispatch("extensions").then((extensions) => {
    session = createEditorSession(host.refs.mount, { extensions: extensions ?? [] });
  }, () => {});                                       // rejected: disconnected before the answer
  return () => session?.destroy();
});
```

The consumers are identical to A:

```js title="(ii) page script · (iii) controller"
document.addEventListener("extensions", (e) => e.respondWith([Highlight]));
host.on("extensions", (e) => e.respondWith([Highlight]));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @extensions="(e) => e.respondWith([Highlight])" />
<UiEditor onExtensions={(e) => e.respondWith([Highlight])} />
<UiEditor onextensions={(e) => e.respondWith([Highlight])} />
```

### C · provided capabilities {#extensions-c}

```html title="(i) ui-editor.html"
<capability name="extensions" returns="list(unknown)">Tiptap extensions added to the built-in set.</capability>
```

```js title="(i) ui-editor.js"
host.on("connect", () => {
  const extensions = host.use("extensions")?.() ?? [];
  const session = createEditorSession(host.refs.mount, { extensions });
  return () => session.destroy();
});
```

```js title="(ii) page script · (iii) controller"
provide(document.body, "extensions", () => [Highlight]);
host.provide("extensions", () => [Highlight]);
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
provideCapability("extensions", () => [Highlight]);
<Capability name="extensions" value={() => [Highlight]}><UiEditor /></Capability>
setCapability("extensions", () => [Highlight]);
```

## 4. Link resolution

The author pastes `/docs/install`. The editor asks for a title and shows "Install HTML Next" in the link card. For a link outside the application, the consumer has no answer, and the editor keeps the link exactly as typed. `null` carries that meaning, whether the consumer answers `null` or does not answer at all.

### A · requests {#links-a}

```html title="(i) ui-editor.html"
<request name="link-resolve" type="object({ href: string })"
  returns="object({ title: string })">A title for a pasted link; null keeps the link as typed.</request>
```

```js title="(i) ui-editor.js"
session.onLinkPasted = (link) => {
  host.request("link-resolve", { href: link.href })
    .then((meta) => { if (meta) link.setTitle(meta.title); }, () => {});  // null: keep as typed
};
```

```html title="(ii) page.html"
<ui-editor></ui-editor>
<script type="module">
  import { lookupTitle } from "./app.js";            // resolves { title } or null
  document.addEventListener("link-resolve", (event) => {
    const url = new URL(event.detail.href, location.href);
    if (url.origin !== location.origin) return;     // no answer: the editor receives null
    event.respondWith(lookupTitle(url.pathname));
  });
</script>
```

```js title="(iii) x-notes.js"
host.on("link-resolve", (event) => {
  const url = new URL(event.detail.href, location.href);
  if (url.origin === location.origin) event.respondWith(lookupTitle(url.pathname));
});
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @link-resolve="(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))" />
<UiEditor onLinkResolve={(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))} />
<UiEditor onlink-resolve={(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))} />
```

### B · answerable events {#links-b}

```html title="(i) ui-editor.html"
<event name="link-resolve" type="object({ href: string })"
  returns="object({ title: string })">A title for a pasted link; null keeps the link as typed.</event>
```

```js title="(i) ui-editor.js"
session.onLinkPasted = (link) => {
  host.dispatch("link-resolve", { href: link.href })
    .then((meta) => { if (meta) link.setTitle(meta.title); }, () => {});  // null: keep as typed
};
```

The consumers are identical to A:

```js title="(ii) page script · (iii) controller"
document.addEventListener("link-resolve", (e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href)));
host.on("link-resolve", (e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href)));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiEditor @link-resolve="(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))" />
<UiEditor onLinkResolve={(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))} />
<UiEditor onlink-resolve={(e) => isLocal(e.detail.href) && e.respondWith(lookupTitle(e.detail.href))} />
```

### C · provided capabilities {#links-c}

```html title="(i) ui-editor.html"
<capability name="link-resolve" type="object({ href: string })"
  returns="object({ title: string })">A title for a pasted link; null keeps the link as typed.</capability>
```

```js title="(i) ui-editor.js"
const resolve = host.use("link-resolve");
if (resolve) Promise.resolve(resolve({ href: link.href }, {}))
  .then((meta) => { if (meta) link.setTitle(meta.title); }, () => {});
```

```js title="(ii) page script · (iii) controller"
provide(document.body, "link-resolve", ({ href }) => isLocal(href) ? lookupTitle(href) : null);
host.provide("link-resolve", ({ href }) => isLocal(href) ? lookupTitle(href) : null);
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
provideCapability("link-resolve", ({ href }) => isLocal(href) ? lookupTitle(href) : null);
<Capability name="link-resolve" value={({ href }) => isLocal(href) ? lookupTitle(href) : null}><UiEditor /></Capability>
setCapability("link-resolve", ({ href }) => isLocal(href) ? lookupTitle(href) : null);
```

## 5. A data grid that asks for rows by page

A data grid shows one page of rows. When the user pages or sorts, it asks for that page, and the previous page's request is abandoned. The application owns the data: a client-side store, a GraphQL client, or an endpoint that a `<data src>` cannot describe. Two grids on one screen, orders and people, need different sources. This case shows how each shape tells instances apart.

### A · requests {#grid-a}

```html title="(i) ui-data-grid.html"
<request name="grid-rows" type="object({ offset: integer, limit: integer, sort: string })"
  returns="object({ rows: list(unknown), total: integer })">One page of rows.</request>
```

```js title="(i) ui-data-grid.js"
host.effect(() => {
  const { offset, limit, sort } = host.state;          // declared state the pager and headers set
  const abort = new AbortController();
  host.request("grid-rows", { offset, limit, sort }, { signal: abort.signal }).then((page) => {
    host.state.rows = page?.rows ?? [];
    host.state.total = page?.total ?? 0;
  }, () => {});
  return () => abort.abort();                           // the next page or sort supersedes this one
});
```

```html title="(ii) page.html"
<section id="orders"><ui-data-grid></ui-data-grid></section>
<section id="people"><ui-data-grid></ui-data-grid></section>
<script type="module">
  import { fetchOrders, fetchPeople } from "./app.js";
  document.getElementById("orders").addEventListener("grid-rows", (e) => e.respondWith(fetchOrders(e.detail, e.signal)));
  document.getElementById("people").addEventListener("grid-rows", (e) => e.respondWith(fetchPeople(e.detail, e.signal)));
</script>
```

```js title="(iii) x-admin.js"
// x-admin.html renders <ui-data-grid $ref="orders"> and <ui-data-grid $ref="people">.
host.on("grid-rows", (e) => e.respondWith(e.target === host.refs.orders
  ? fetchOrders(e.detail, e.signal) : fetchPeople(e.detail, e.signal)));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiDataGrid @grid-rows="(e) => e.respondWith(fetchOrders(e.detail, e.signal))" />
<UiDataGrid onGridRows={(e) => e.respondWith(fetchOrders(e.detail, e.signal))} />
<UiDataGrid ongrid-rows={(e) => e.respondWith(fetchOrders(e.detail, e.signal))} />
```

### B · answerable events {#grid-b}

```html title="(i) ui-data-grid.html"
<event name="grid-rows" type="object({ offset: integer, limit: integer, sort: string })"
  returns="object({ rows: list(unknown), total: integer })">One page of rows.</event>
```

```js title="(i) ui-data-grid.js"
host.effect(() => {
  const { offset, limit, sort } = host.state;          // declared state the pager and headers set
  const abort = new AbortController();
  host.dispatch("grid-rows", { offset, limit, sort }, { signal: abort.signal }).then((page) => {
    host.state.rows = page?.rows ?? [];
    host.state.total = page?.total ?? 0;
  }, () => {});
  return () => abort.abort();                           // the next page or sort supersedes this one
});
```

The consumers are identical to A:

```js title="(ii) page script · (iii) controller"
document.getElementById("orders").addEventListener("grid-rows", (e) => e.respondWith(fetchOrders(e.detail, e.signal)));
host.on("grid-rows", (e) => e.respondWith(e.target === host.refs.orders ? fetchOrders(e.detail, e.signal) : fetchPeople(e.detail, e.signal)));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<UiDataGrid @grid-rows="(e) => e.respondWith(fetchOrders(e.detail, e.signal))" />
<UiDataGrid onGridRows={(e) => e.respondWith(fetchOrders(e.detail, e.signal))} />
<UiDataGrid ongrid-rows={(e) => e.respondWith(fetchOrders(e.detail, e.signal))} />
```

### C · provided capabilities {#grid-c}

```html title="(i) ui-data-grid.html"
<capability name="grid-rows" type="object({ offset: integer, limit: integer, sort: string })"
  returns="object({ rows: list(unknown), total: integer })">One page of rows.</capability>
```

```js title="(i) ui-data-grid.js"
host.effect(() => {
  const { offset, limit, sort } = host.state;
  const rows = host.use("grid-rows");
  const abort = new AbortController();
  if (rows) Promise.resolve(rows({ offset, limit, sort }, { signal: abort.signal })).then((page) => {
    if (!abort.signal.aborted) { host.state.rows = page.rows; host.state.total = page.total; }
  }, () => {});
  return () => abort.abort();
});
```

The nearest provider serves every grid beneath it. Two grids with different sources each need their own provider:

```js title="(ii) page script · (iii) controller"
provide(document.getElementById("orders"), "grid-rows", (page, { signal }) => fetchOrders(page, signal));
provide(document.getElementById("people"), "grid-rows", (page, { signal }) => fetchPeople(page, signal));
// A controller provides once for its whole subtree; two sources need a wrapper component per grid.
host.provide("grid-rows", (page, { signal }) => fetchOrders(page, signal));
```

```html title="(iv) Vue · (v) React · (vi) Svelte"
<!-- Vue and Svelte provide for a whole component, so the second source needs a wrapper component. -->
provideCapability("grid-rows", (page, { signal }) => fetchOrders(page, signal));
<Capability name="grid-rows" value={(page, { signal }) => fetchOrders(page, signal)}><UiDataGrid /></Capability>
setCapability("grid-rows", (page, { signal }) => fetchOrders(page, signal));
```

> [!note] A chart's value formatter
> A chart formats every tick label, which can mean fifty calls per render. One request per label would dispatch fifty events, so a formatter is asked for **once**. Either answer with formatting options (`returns="object({ style: keyword, currency: string })"`, passed to `Intl.NumberFormat`), or with the formatter itself (`returns="unknown"`, a function the chart keeps until it reconnects). The answer may be a function. What the shapes remove is the function-valued *prop*.

## Late providers and re-asking {#late-providers}

A request made at connect reaches only the listeners that already exist. Draft step 4 handles one source of lateness: a consuming **component** whose controller loads after the editor's. Two sources remain: a **page script** that loads later, such as a lazily imported setup module, and a **framework** that attaches listeners after the child mounts. In React, a parent's `useEffect` runs after its child's.

### Without re-asking

```text
t0  the runtime lowers <ui-editor>; the editor connects
t1  editor:  host.request("extensions")  →  no listener  →  resolves null
t2  editor:  builds its view with the built-in extensions only
t3  editor-setup.js loads and adds its "extensions" listener on document
t4  the author types "@ad": mention-query is asked now and answered (asked per use, so unaffected)
    extensions stay missing until the editor next connects
```

Requests asked on use, such as mentions, uploads, links, and grid pages, are unaffected. Requests asked at setup, such as extensions or a chart's formatter, are missed until the next connection.

### With re-asking

```text
t1  editor:  host.request("extensions")  →  null; the runtime remembers (editor, "extensions")
t3  editor-setup.js adds its listener, then announces it:
      document.dispatchEvent(new CustomEvent("request-available", { detail: { name: "extensions" } }))
t3' runtime: the remembered "extensions" requests inside document → the editor
      it fires "reask" on the editor's host with detail { name: "extensions" } and forgets the record
t4  editor:  host.request("extensions") again  →  answered  →  rebuilds its view and keeps the document
```

### The re-ask design

- **What is remembered.** Each request that resolved `null` because nobody answered, from a connected instance: one record per instance and request name. A record is cleared when that request is answered, when the instance disconnects, or when it is re-asked.
- **Who announces.** The responder:
  - A controller's `host.on(name, …)` announces automatically when it registers, because the runtime sees the registration.
  - A framework adapter announces when a request listener or function prop is attached after connect.
  - A page script announces by dispatching a bubbling `request-available` event, whose detail is `{ name }`, from the element it listens on. A helper with the [mirroring signature](#framework-mirroring), `respond(element, name, fn)`, could add the listener and announce in one call.
- **Who listens.** The runtime, once, on the document. This is the role the Context Protocol gives its `ContextRoot`. An announcement from element E matches remembered requests whose root is E or inside E.
- **What retries.** The asking controller, on `host.on("reask", …)`. The runtime never repeats the request itself, because only the controller knows whether a new answer matters: extensions mean a rebuild, while a mention list that is already closed means nothing. A controller with no `reask` listener is unaffected, and the original promise stays resolved `null`, as decided.

```js title="ui-editor.js with re-asking"
host.on("connect", () => {
  let session;
  const build = () => host.request("extensions").then((extensions) => {
    session?.destroy();                                 // the EditorState stays in the closure
    session = createEditorSession(host.refs.mount, { extensions: extensions ?? [] });
  }, () => {});
  build();
  const stop = host.on("reask", (event) => { if (event.detail.name === "extensions") build(); });
  return () => { stop(); session?.destroy(); };
});
```

Two alternatives were set aside. Keeping a request pending until someone answers would contradict the `null` decision and leave setup waiting forever on pages with no consumer. Having the runtime re-run the request and resolve the original promise a second time is impossible, because a promise settles once.

In C, lookups are runtime-mediated, so every `provide()` call announces itself, page-level ones included, and nothing needs a manual announcement. Setup-time capabilities still need the same `reask` notification to rebuild.

## Framework mirroring {#framework-mirroring}

The event form works in every framework but reads as DOM plumbing. Vue and React authors expect to pass a function that *returns* the answer. In both frameworks, an event handler's return value is ignored, so `@mention-query="searchPeople"` would silently answer nothing. These are the options for mirroring that intuition:

**1. Event binding only.** As in the use cases above. It's one spelling everywhere and `respondWith` stays explicit, but it's verbose and easy to get wrong in the way just described.

**2. A function prop as sugar.** The framework component accepts a camelCase prop named after the request. Its value is a function `(detail, { signal, progress }) => answer`, and the host adapter turns it into a responder:

```html
<!-- Vue -->
<UiEditor :mention-query="({ query }, { signal }) => searchPeople(query, signal)" />
<!-- React -->
<UiEditor mentionQuery={({ query }, { signal }) => searchPeople(query, signal)} />
<!-- Svelte -->
<UiEditor mentionQuery={({ query }, { signal }) => searchPeople(query, signal)} />
```

```js
// What the adapter does, once, before the controller runs:
root.addEventListener("mention-query", (event) => {
  const answer = props.mentionQuery;                  // read at request time, so a new prop needs no re-wiring
  if (answer) event.respondWith(answer(event.detail, { signal: event.signal, progress: event.progress }));
});
```

This is the mirroring. Each framework writes a function prop in its own idiom, while the HTML component still has no function prop: the prop exists only on the framework side, and the semantics stay A's (dropping stale answers, checking the answer's type, `null`). Attaching it after connect announces for re-asking. A request name that collides with a declared prop's camelCase name is a build error. Generated types give `mentionQuery?: (detail: { query: string }, init: { signal: AbortSignal }) => Answer` where `Answer` is the answer type, `null`, or a promise of either.

**3. One `requests` object prop.** `:requests="{ mentionQuery: search, imageUpload: upload }"` groups every answer and passes through wrapper components easily. It adds a second configuration convention beside ordinary props, and it reads less naturally in Svelte, where props are destructured individually.

**4. The same signature for page script.** A small runtime helper, `respond(element, "mention-query", ({ query }, { signal }) => searchPeople(query, signal))`, gives plain pages the same function signature and makes the re-ask announcement automatic.

**Recommendation: option 2, keeping the event form.** Function props are what Vue, React, and Svelte authors already write for providers, such as react-select's `loadOptions` or Vue's function props. The signature matches C's provider functions, so framework authors get C's ergonomics with A's semantics. The event form remains for listeners on an ancestor and for the rare consumer that needs the event itself. Option 4 is a small optional addition for page scripts.

## B against A {#b-against-a}

B makes `<event>` answerable instead of adding `<request>`. The consumer's code is identical. The differences fall on the component author and the reader of the component's contract:

- **Discoverability.** A lists requests separately, so generated documentation, types, and editor completions show "this component asks for these answers". In B, the obligation to answer is an attribute on one entry in a list of events. A consumer reading the events can take `mention-query` for a notification, listen without answering, and get `null` with no warning. A is better here.
- **One concept or two.** B has one declaration element and one dispatch method, and converters reuse their existing event mapping. B is better on surface count. The cost is that `host.dispatch` returns a boolean for one event and a promise for another, decided by an attribute elsewhere. Adding `returns` to an existing event also changes how it propagates, because the first responder stops it, so listeners that already exist stop receiving it.
- **`<dispatch>` and `$$event`.** In B, a handler's `<dispatch event="mention-query">` is legal, but the answer has nowhere to go. B would need either a diagnostic or a new `into="state"` attribute. That attribute would also give HTML Next declarative asking, which A could add later as its own step. B also allows `cancelable` alongside `returns`, so it must forbid the combination. A keeps `<dispatch>` fire-and-forget. In both shapes, a consumer's `on:` handler sees `$$event` but cannot answer it.
- **Type checking of the answer.** At runtime, both check the answer against `returns`. Statically, A's `host.request` is typed only over requests. B's `host.dispatch` must be overloaded by event name to return a boolean or a promise, which generated types can do, but untyped JavaScript gets no warning when it awaits a plain event's boolean.
- **Precedent.** Both are the same event underneath. Native `FetchEvent` is an ordinary event that gained `respondWith`, which favors B's framing. Its declaration, though, is a separate interface, which favors A's.

On balance, A is clearer for the people who consume components, and B is smaller for the specification. The main risk in B is that the obligation to answer is invisible to a consumer.

**Decided: A.** The code is the same length in both shapes, so the choice rests on what each one tells its readers:

- A component's contract lists what it asks its consumer for, apart from what it announces. An unanswered request degrades the component quietly, so a consumer must be able to see it.
- Framework mirroring maps mechanically: an `<event>` becomes an `onX` handler, and a `<request>` becomes a function prop that returns the answer. Under B, one declaration would map to either kind depending on an attribute, and a handler's ignored return value would answer nothing.
- `host.dispatch` always returns a boolean, and `host.request` always returns a promise.
- Existing events keep their propagation, and `<dispatch>` stays fire-and-forget, with no `cancelable` and `returns` conflict.

B's advantage, one fewer declaration and method, is small, because both run on the same `RequestEvent`.

## Summary: what to decide {#decisions}

| # | Question | Recommendation | Decide |
| --- | --- | --- | --- |
| 1 | Shape and naming | **A**: `<request>`, `host.request`, and `RequestEvent` | **decided: A** |
| 2 | No answer | `null` | **decided** |
| 3 | Ancestor wait (draft step 4) | Keep it. Wait only for each ancestor controller's synchronous body. | Confirm |
| 4 | Late providers | **Re-ask**: remember unanswered requests, announce with `request-available` (automatic for `host.on` and adapters, an event or `respond()` for page script), and notify with `reask` | Adopt, and the event names |
| 5 | DOM or logical ancestry | Follow the DOM. Retarget to the logical parent when `<portal>` lands. | Confirm |
| 6 | Upload progress | Add a `progress` option to `host.request` and `event.progress(loaded, total)` | Add now or later |
| 7 | Declarative answers or asks | Defer. Revisit `<respond>` or `into=` once controllers ship. | Confirm deferral |
| 8 | Framework mirroring | A **function prop** `(detail, { signal, progress }) => answer` on the framework side, keeping the event form | Adopt |
| 9 | Types for `File` and extension objects | `unknown` now. A named `file` type, like `event`, later. | Confirm |
| 10 | Placement | On acceptance, fold the result into the Components, Types, and JavaScript Layer chapters, and retire this explainer | Confirm |

With **1** decided, the decision that shapes the rest is **4** (re-ask). The others follow from it or can wait. To continue reading, see the proposed [Requests](/declarative-components/javascript#requests) section.
