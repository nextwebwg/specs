// Content regressions: decisions the specification has made and must keep saying. Each test reads
// the Markdown source, so it guards the text a contributor edits.
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { test } from "node:test";
import { compileChapter } from "./compile.ts";

const chapter = (name: string) => readFileSync(`html-next/${name}.md`, "utf8");
const forms = () => readFileSync("html-forms/index.md", "utf8");
const chapters = readdirSync("html-next").filter((f) => f.endsWith(".md")).map((f) => f.replace(/\.md$/, ""));
const modules = chapters.filter((name) => name !== "index");

test("the type system separates base types, permitted values, and selected types", () => {
  const types = chapter("types");

  assert.match(types, /Type names are plain keywords/);
  assert.match(types, /The `values` attribute limits a prop to a comma-separated set of values of its declared type/);
  assert.match(types, /<prop name="size" type="keyword" values="sm, md, lg"/);
  assert.match(types, /<type from="type">/);
  assert.match(types, /<event name="change" type="object">[\s\S]*?<prop name="trigger" type="keyword" values="keyboard, pointer, programmatic"/);
  assert.doesNotMatch(types, /type="enum\(/);
  for (const section of ["components", "examples", "styling"]) {
    assert.doesNotMatch(chapter(section), /type="enum\(/, section);
  }
  assert.match(types, /A declared prop that is omitted and has no default resolves to `null`/);
  assert.ok(types.indexOf("| `string` |") < types.indexOf("| `length` |"));
  assert.doesNotMatch(types, /^### (?:Combinators|Multipliers|Precedence)$/m);
});

test("validation keeps polyfill details behind the platform surface", () => {
  const validation = chapter("validation");

  assert.match(validation, /Authors set validity through `setValidity\(\)` and style/);
  assert.match(validation, /Authors use the proposed surface/);
  assert.doesNotMatch(validation, /style polyfilled validity with/);
  assert.doesNotMatch(validation, /polyfilled as `\[data-invalid\]/);
});

test("invalid reactive results keep the last accepted destination value", () => {
  const reactivity = chapter("reactivity");
  const validation = chapter("validation");
  const bindings = chapter("bindings");

  assert.match(reactivity, /^## Invalid reactive results$/m);
  assert.match(reactivity, /does not write[\s\S]*?most recent successful write/);
  assert.match(reactivity, /declared default, or `null` when there is no default/);
  assert.match(reactivity, /\| Supply `2` \| `2` \| `2` \| `2` \|/);
  assert.match(reactivity, /\| Supply `"oops"` \| `"oops"` \| `2` \| `2` \|/);
  assert.match(reactivity, /\| Supply `7` \| `7` \| `7` \| `7` \|/);
  assert.match(reactivity, /after `2`, it stays at `2`, not `5` or `null`/);
  assert.match(reactivity, /\| `\{ label: 42, note: 'b' \}` \| `first` \(last valid result\) \| `b` \|/);
  assert.match(reactivity, /\| `\{ label: 'third', note: 'c' \}` \| `third` \| `c` \|/);
  assert.match(reactivity, /one-time `<set expr:value>`[\s\S]*?skips that handler step's write/);
  assert.match(reactivity, /<computed from>[\s\S]*?last successfully computed value/);
  assert.match(reactivity, /`items\.0\.name`/);
  assert.match(reactivity, /\$results\.0\.title/);
  assert.doesNotMatch(reactivity, /items\[0\]\.name|results\[0\]\.title/);
  assert.match(chapter("expressions"), /\$items\.0\.name[\s\S]*?items\.0\.name/);
  assert.match(chapter("expressions"), /\$items\[0\]\.name` is invalid/);
  assert.match(validation, /supplied number above `max`[\s\S]*?becomes the prop's current value/);
  assert.match(validation, /number prop is supplied as `amount="oops"`[\s\S]*?remains its `inputValue`/);
  assert.match(validation, /Template expressions and `host\.props\.amount\.value` read that accepted value/);
  assert.match(validation, /Validity for a directly supplied prop describes its current \*\*input\*\*/);
  assert.match(chapter("javascript"), /`host\.props\.amount\.value` reads the prop's \*\*accepted value\*\*/);
  assert.match(chapter("javascript"), /State has no `inputValue` or `validity`/);
  assert.match(bindings, /function call[\s\S]*?full sequence/);
});

test("reactivity defines the Signals boundary and lifecycle-owned JavaScript API", () => {
  const reactivity = chapter("reactivity");
  const javascript = chapter("javascript");

  assert.match(reactivity, /integrates with, but does not depend on/);
  assert.match(reactivity, /\*\*Connection owns observation\.\*\*/);
  assert.match(reactivity, /`State`[^\n]*`Computed`[^\n]*`Watcher`/);
  assert.match(javascript, /interface ComponentHost/);
  assert.match(javascript, /type EffectCallback = \(\) => void \| \(\(\) => void\)/);
  assert.match(javascript, /effect\(callback: EffectCallback\): \(\) => void/);
  assert.match(javascript, /The reactive API is instance-scoped/);
});

test("proposal callouts name their contract and review requests demand attention", () => {
  const proposal = modules.map(chapter).join("\n");
  const reactivity = chapter("reactivity");

  assert.match(reactivity, /^> \[!norm\] Resource and control ownership$/m);
  assert.match(reactivity, /^> \[!ex\] Async validity composes with native forms$/m);
  assert.match(reactivity, /^> \[!warn\] Open for review$/m);
  assert.doesNotMatch(proposal, /^(?:## |> \[!\w+\] )(?:No |Not |Why |Why not|There is no)/m);
});

test("polymorphic roots use explicit native branches", () => {
  const components = chapter("components");

  assert.match(components, /<prop name="as" type="keyword" values="button, a" default="button">/);
  assert.match(components, /<a \$when="as = 'a'">/);
  assert.match(components, /<button \$else>/);
  assert.doesNotMatch(components, /<button as="button \| a">/);
  assert.match(components, /The prop does not retag an element/);
});

test("props are initial configuration without required data-* reflection", () => {
  const components = chapter("components");
  const reactivity = chapter("reactivity");

  assert.match(components, /A prop is input to that rendering; it is not automatically exposed as `data-<name>`/);
  assert.match(components, /A literal attribute on the invocation supplies the prop's \*\*initial configuration\*\*/);
  assert.doesNotMatch(components, /effective value \(passed or default\)/);
  assert.doesNotMatch(reactivity, /This is `attributeChangedCallback`/);
  assert.match(components, /a parent template's `from:name` binding/);
  assert.doesNotMatch(components, /data-variant="solid"/);
});

test("the baseline component contract includes the complete slot model", () => {
  const components = chapter("components");
  const slotEntryStart = components.indexOf('{.entry name="<slot>"');
  const slotEntryEnd = components.indexOf("{.entry", slotEntryStart + 1);
  const slotEntry = components.slice(slotEntryStart, slotEntryEnd);

  assert.ok(slotEntryStart >= 0, "the element reference must include a slot entry");
  assert.match(components, /Level&nbsp;1 includes default, named, fallback, and scoped slots/);
  assert.match(chapter("index"), /default, named, fallback, and scoped slots/);
  assert.match(slotEntry, /\[L1\]\{\.pill \.l1\} · default, named, fallback, and scoped slots/);
  assert.doesNotMatch(slotEntry, /\.pill \.soon|L2/);
  assert.doesNotMatch(components, /Level&nbsp;2 adds named, fallback, and scoped slots/);
});

test("data examples use declared types and every citation has a target", () => {
  const reactivity = chapter("reactivity");
  assert.match(reactivity, /<data name="search" src="\/api\/search" type="object"/);
  assert.doesNotMatch(reactivity, /type="SearchResults"/);

  for (const name of [...chapters.map((c) => `html-next/${c}.md`), "html-forms/index.md"]) {
    const source = readFileSync(name, "utf8");
    const defined = new Set([...source.matchAll(/^\[\^(\d+)\]:/gm)].map((m) => m[1]));
    for (const [, ref] of source.matchAll(/\[\^(\d+)\](?!:)/g)) assert.ok(defined.has(ref), `${name} cites [^${ref}] without a definition`);
  }
});

test("writes are reactive data effects and commands remain author-owned", () => {
  const reactivity = chapter("reactivity");
  const bindings = chapter("bindings");

  for (const phrase of [/<data name="saveDraft"/, /method="patch"/, /send="change"/, /^> \[!norm\] Expanded request methods$/m,
    /ASCII-case-insensitive enumerated attribute/, /`patch` and `PATCH` both produce HTTP `PATCH`/, /`query` follows the read lifecycle/,
    /Level&nbsp;1 keywords are `get`, `query`, `post`, `put`, `patch`, and `delete`/,
    /Initial connection samples .* baseline and does not send a write/, /last acknowledged body/,
    /immutable resolved resource identity and body snapshot/, /preserves its dirty latest snapshot/, /old-key completion/,
    /For a read, a param change cancels/, /does not own controls or create a rendered `<form>`/,
    /validation contract\]\(\/html-next\/validation\) applies the result to the field's validity/,
    /native form submission, an imperative controller call, or a component event/]) {
    assert.match(reactivity, phrase);
  }
  assert.doesNotMatch(reactivity, /<form name="save" method="post" src=/);
  assert.doesNotMatch(reactivity, /<mutation|<send mutation/);
  assert.doesNotMatch(reactivity, /A param change cancels any in-flight request/);
  assert.doesNotMatch(reactivity, /discards a queued write/);
  assert.doesNotMatch(bindings, /<send mutation|<mutation name=/);
});

test("HTML Forms is an independent proposal with composable submission scopes", () => {
  const source = forms();

  assert.ok(!existsSync("html-next/forms.md"));
  for (const phrase of [/^title: HTML Forms$/m, /HTML Next · independent proposal/, /A form is an \*\*author-owned submission scope\*\*/,
    /method="query"/, /method="patch"/, /formmethod="post"/, /ASCII-case-insensitive enumerated attribute/,
    /`patch` and `PATCH` both produce HTTP `PATCH`/, /RFC&nbsp;10008/, /WHATWG HTML PR&nbsp;#11347/, /WHATWG HTML issue&nbsp;#12594/,
    /<form composable/, /nearest ancestor `<form>` remains its form owner/,
    /Submitting the outer form collects the successful controls of its descendant form scopes/,
    /^> \[!warn\] Parser compatibility requires incubation$/m, /^> \[!warn\] Open for review$/m, /form element pointer/]) {
    assert.match(source, phrase);
  }
  assert.doesNotMatch(source, /^status: .*(?:review|input)/im);
  assert.doesNotMatch(source, /No nested forms|forms are not|not form ownership/i);
  // HTML Forms stands alone: its examples use no component-model markup, and it does not route
  // readers into the component model's reactivity chapter.
  const samples = [...source.matchAll(/^```[^\n]*\n([\s\S]*?)^```$/gm)].map((m) => m[1]).join("\n");
  assert.doesNotMatch(samples, /<data[\s>]|<defs>|template component/i);
  assert.doesNotMatch(source, /\/html-next\/reactivity/i);
  assert.doesNotMatch(chapter("overview"), /\]\(\/html-next\/forms\)/);
  assert.doesNotMatch(chapter("reactivity"), /\]\(\/html-next\/forms\)/);
});

test("current targets do not publish detached contract JSON", () => {
  assert.doesNotMatch([chapter("index"), chapter("targets"), chapter("security")].join("\n"), /Contract JSON|contract JSON|contracts\//);
});

test("security defines mandatory controls instead of disclaiming the model", () => {
  const security = chapter("security");
  const javascript = chapter("javascript");
  const examples = chapter("examples");
  const components = chapter("components");

  for (const phrase of [/Secure by construction/, /\[must\]\{\.kw\} reject inline event-handler attributes/,
    /\[must not\]\{\.kw\} weaken a rule/, /\[must\]\{\.kw\} reject the source or value/, /Controllers have page authority/,
    /type="importmap"[\s\S]*invalid anywhere in a definition/, /cannot create, replace, merge, or widen an import map/,
    /inert-definition rule applies \*\*before\*\* code executes/, /neither CSP nor an import-map prefix creates a directory-level sandbox/,
    /browser live-trust procedure is not involved/, /mapped target prefix is the live scope/,
    /Content inserted through `\$html`[\s\S]*\[must never\]\{\.kw\} be processed as a component-definition source/]) {
    assert.match(security, phrase);
  }
  assert.match(javascript, /<template component="x-chart" controller="\.\/b\.js">/);
  assert.match(javascript, /await import\(controllerURL\)/);
  assert.match(javascript, /export default function controller\(host\)/);
  assert.match(javascript, /typeof module\.default !== "function"/);
  assert.match(javascript, /@nextwebwg\/html\/vue/);
  assert.match(examples, /<template component="x-counter" controller="\.\/counter\.js">/);
  assert.match(components, /"@acme\/ui\/": "https:\/\/cdn\.example\/@acme\/ui@4\/components\/"/);
  assert.match(components, /"\.\/\*\.html": "\.\/components\/\*\.html"/);
  assert.doesNotMatch([security, javascript, examples, components].join("\n"), /html-next-controller/);
  assert.doesNotMatch([javascript, examples, components].join("\n"), /<link[^>]*\scontrollers(?:\s|>)/);
  assert.doesNotMatch(javascript, /link rel="controller"/);
  assert.doesNotMatch([javascript, examples].join("\n"), /defineController|@nextweb\/html|from "html\/components"/);
  assert.doesNotMatch(javascript, /third-party component's \*markup\* is always safe/);
  assert.doesNotMatch(javascript, /later `import\(\)` reuses that verified module/);
  assert.doesNotMatch(security, /make untrusted component definitions safe/);
});

test("the proposal front page offers its reading paths and full-document snapshot links", () => {
  const landing = chapter("index");
  const { sfc } = compileChapter(landing);

  assert.match(chapter("overview"), /^navGroup: guide$/m);
  assert.match(chapter("examples"), /^navGroup: guide$/m);
  assert.match(landing, /\[Start with Overview →\]/);
  assert.match(landing, /\[See Examples →\]/);
  assert.match(landing, /\[Browse Chapters ↓\]\(#chapters\)/);
  assert.match(landing, /^::: \{#chapters\}$/m);
  assert.match(sfc, /aria-label="Start reading Declarative HTML Components"/);
  assert.doesNotMatch(sfc, /<NuxtLink[^>]+(?:latestHtmlNextSnapshot|snapshot)\.href/);
  assert.match(landing, /Unofficial Editor(?:'|’)s Draft/);
  assert.doesNotMatch(landing, /Next Web Working Group · Working Draft|Living working draft|editors' working draft/i);
});

test("chapters contain no stale internal specification routes", () => {
  for (const name of chapters) assert.doesNotMatch(chapter(name), /\]\(\/spec\//, name);
});

test("browser discovery covers later definitions without changing controller binding or trust", () => {
  const javascript = chapter("javascript");

  for (const phrase of [/Definitions and instances added after boot/, /MutationObserver/, /instance arrives before its definition/,
    /application-owned resolution and import-map trust/, /Sanitized `\$html` and CMS content remain excluded/,
    /Removal disconnects the instance and disposes its owned work/, /Compiled\/AOT builds[\s\S]*do not use `MutationObserver/]) {
    assert.match(javascript, phrase);
  }
});

test("text reaches v-html props escaped, never as markup", () => {
  const { sfc } = compileChapter([
    "---", "title: Probe", "---", "", "# Probe", "", "A lede with `<code>` and <b>.", "",
    "## Section", "", "::: {.entry name='<slot name=\"x\">' role=\"r\"}", "Level", ": `<slot>` <i>", ":::", "",
  ].join("\n"));
  const data = sfc.match(/const __data = (.*);/)![1].replace(/\\u003c/g, "<");

  assert.match(data, /"name":"&lt;slot name=\\"x\\"&gt;"/);
  assert.match(data, /"lede":"A lede with <code>&lt;code&gt;<\/code> and &lt;b&gt;\."/);
  assert.match(data, /"value":"<code>&lt;slot&gt;<\/code> &lt;i&gt;"/);
  assert.doesNotMatch(data, /<b>|<i>|<slot/);
});
