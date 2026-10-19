# HTML Feature Profiles: verification evidence

This evidence separates the proposed contract from current browser behavior. It does not implement the native `profile` option, profile-aware sanitizer, response header, or flexible-nesting layout.

## Contract reference model

`resolver.mjs` models named selection, API-only `inherit`, current `next`, absent/undefined legacy defaults, immutable snapshots, dependency/composition rejection, and header-over-doctype precedence. The navigation entry point assumes an already recognized profile request; it does not implement doctype recognition, redirects, HTTP caches, or a full HTTP stack. Its HTTP recognizer accepts the proposal's restricted bare-token-list subset and is not a general RFC 9651 parser.

The repository’s `pnpm verify:pr` includes these lightweight model checks; recorded browser controls are not rerun by that command.

`resolver.test.mjs` contains 36 authored contract checks, including adversarial string conversion, invalid headers with a valid fallback doctype, inherited old snapshots versus new presets, legacy callers, unsupported revisions/dependencies/combinations, immutable copies, and selector normalization. Fixture identifiers and revisions are test data, not a real preset manifest or an approval policy.

The stateful DOMString case first failed: the model converted the input twice, so a custom `toString` could disagree with the recorded request. It now converts once before validation and record construction. The failing observation and retained regression are recorded in `verification-results.json`.

Run with Node 24.20.0 (no extra model dependencies):

```sh
node --test resolver.test.mjs
node verify.mjs
```

`verify.mjs` checks the recorded browser script digest and observed safe-method protections, then records model results and source SHA-256 digests. It does not rerun browsers automatically.

## Current-browser controls

`browser-baseline.mjs` runs Chromium, Firefox, and WebKit sequentially using the sibling self-closing evidence package's pinned Playwright 1.62.1. Reuse that package's install; do not create another dependency store. Install its dependencies and test browser binaries using its README, then run:

```sh
node browser-baseline.mjs
node verify.mjs
```

`CHROMIUM_EXECUTABLE`, `FIREFOX_EXECUTABLE`, and `WEBKIT_EXECUTABLE` can select compatible existing binaries. The report records actual engine versions and script digest.

The available methods ignored the `profile` dictionary getter, accepted an unsupported profile name without error, and exposed no native resolved record. The source remained legacy nested HTML with and without the proposed option. That is a negative support control, not successful native profile implementation. WebKit's tested build lacked `Document.parseHTML`; its available unsafe method is reported separately rather than counted as a safe-method pass.

The available safe methods removed the tested script, event-handler attribute, JavaScript URL, and custom host under their current policies. Unsafe defaults retained the unsafe content but did not execute the source script during parsing. Optional default-sanitizer observations are recorded independently. These are selected controls, not an exhaustive sanitizer or side-effect proof. The first probe looked up sanitized IDs; safe parsing removed those IDs, so the final structural observation instead locates the native span directly.

## Limits

No result verifies the proposed option in a native browser. The reference model cannot prove native cross-realm selection, Trusted Types/CSP processing, sanitizer equivalence under a new grammar, callbacks, resource behavior, or layout. The proposal lists those remaining implementation obligations. Existing self-closing native and formal evidence remains scoped to its recorded implementation and literal `next` opt-in; it does not transfer to this selector system or flexible nesting.
