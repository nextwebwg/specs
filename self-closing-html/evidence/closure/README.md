# Immediate self-closing HTML: current implementation

This replacement processes a self-closing HTML start tag followed immediately by its corresponding end tag, before reading more source. It uses ordinary HTML recovery, including formatting, select, table, and template rules.

- HTML void elements already finish at their start tag; do not invent end tags for them.
- SVG/MathML start tags retain native foreign-content handling.
- Invalid-context tags and document structure retain HTML recovery. The shorthand is not permission to create an otherwise ignored element or put a sibling outside the document root.
- Script/style/text starts finish before their contents can consume following source. `plaintext` is handled at the token boundary; its literal legacy closing-tag spelling is not a valid comparison oracle because legacy plaintext consumes it as text.

## Security contract

Use the selected grammar to parse **before** sanitizing, then insert the sanitized nodes without reparsing a string. `safe-dom.mjs` demonstrates that composition using DOMPurify in place on an inert document assembled from the parser's AST. `safe-parse.mjs` supplies a jsdom host for reproducible Node tests. This is reference tooling, not an implementation of the native Sanitizer API or proof of every policy.

The unsafe parser does not make untrusted source safe. A legacy sanitized string is not automatically safe under the new grammar. The retained custom-policy counterexample demonstrates this distinction; it is not a vulnerability claim against sanitizer defaults.

## What does each kind of evidence tell us?

| Evidence | What it answers | What it does not establish |
| --- | --- | --- |
| Focused tests | Do ordinary names, special contexts, selected script pauses, and known bug regressions behave as specified? | Every malformed input or arbitrary script mutation. |
| Generated comparisons | Does changing chunk boundaries change these 10,000 documents? Does the safe path retain monitored hazards in 1,000 inputs? | An independent parser proof or every possible unsafe policy. |
| Three-engine execution | Do callbacks, mutations, resources, and direct insertion work in the tested browser adapters? | Native parsing support in those browsers; the adapters share this parser. |
| Native browser experiment | Does a separate engine implementation handle the recorded navigation and execution cases? | Production readiness, other engines, or unimplemented profile bindings. |
| Reduced counterexample | Can a custom legacy sanitizer policy leave source that becomes an active handler under the new grammar? | A vulnerability in sanitizer defaults. |
| Formal proof | The archived Lean theorem checks the earlier tree-rearrangement operation. | It does **not** prove this start-and-close grammar. No machine-checked correctness theorem is claimed for this implementation. |

## What is checked?

- `parser.test.mjs`: parser-known names against explicit pairs across ten contexts; special plaintext assertion; all two-chunk splits of selected sources; fragment contexts; script pause/resume.
- `safe-parse.test.mjs`: actual selected-grammar parse followed by in-place sanitization, known mismatch, monitored handler/script/URL removal, legacy default and explicit selection.
- `live-dom.test.mjs`: insertion-order and script-mutation ownership regressions.
- `check.mjs`: 10,000 seeded sources, 30,000 chunk comparisons, and 1,000 in-place sanitization inputs. `check-results.json` records results and source digests.
- `execution-runner.mjs`: 34 cases per engine, run sequentially in Chromium, Firefox, and WebKit, including classic-script blocking, callback/mutation checkpoints, real streamed input, direct safe node insertion, and 500 DOM comparisons per engine. `execution-results.json` records scope and digests. This uses a shared parse5-based parser, not those browsers' native tokenizers. Dynamic script placeholders are a prototype scheduling contract, not native parser-inserted script identity.

## Native browser results

A separate Ladybird implementation passes 50 execution checks, 810 document comparisons, six encoding cases, and 16 existing parser regressions. A focused garbage-collection-on-every-allocation run completes without failure. The comparison record preserves 120 baseline differences between Ladybird and parse5; named cases use Ladybird’s own explicit-pair result as their oracle. These do not count as cross-parser agreement.

[Native patch, exact limits, results, and reproduction](native.md).

## Reproduce

Use the pinned dependencies in the parent evidence directory. Node tests do not install or alter them.

```sh
cd self-closing-html/evidence
npm ci --ignore-scripts --no-audit --no-fund
node --test closure/*.test.mjs
node closure/check.mjs
node closure/execution-runner.mjs
```

The browser runner serves the evidence directory on loopback and closes browsers/server in `finally`. It accepts `CHROMIUM_EXECUTABLE`, `FIREFOX_EXECUTABLE`, and `WEBKIT_EXECUTABLE` for installed browser paths. Run only one local browser runner at a time. Result files are overwritten; source digests identify the recorded revision.

## What this replaces

The parent directory's projection algorithm, Lean proof, and original native patch describe a different restricted design. They remain historical evidence and do not prove this implementation correct. The new implementation must be judged on its own tests and security contract.
