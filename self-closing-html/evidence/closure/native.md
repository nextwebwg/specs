# Native browser experiment

**The same broad closure rule runs inside a separately modified Ladybird parser.** It passes the recorded navigation, execution, encoding, regression, and focused garbage-collection checks. This is an experimental build of one engine, not browser support available to authors.

## Checklist and evidence

| Question | Result | Record |
| --- | --- | --- |
| Do ordinary elements, text elements, attributes, namespaces, and shadow roots close consistently? | ✅ Included in 50 native execution checks. | [Navigation log](native-navigation.log), fixtures in [patch](native.patch). |
| Do real parser-inserted scripts preserve blocking, async, defer, module imports, stylesheet pauses, and CSP? | ✅ The tested cases pass. Network streaming runs a script before EOF, then resumes. | Same execution fixture; no browser adapter is used. |
| Are custom-element reactions and script-driven moves/removals retained? | ✅ Construction, upgrade, mutation, and ownership cases pass. | Same execution fixture. |
| Can a legacy sanitizer's retained text become active markup? | ✅ The custom-policy mismatch exposes and executes the image handler; legacy DOMParser sees no image. | `custom-policy legacy sanitizer mismatch` case. This is a reproduced hazard, not a safe-parser result. |
| Does closure match the expected document? | ✅ 610 named/context cases match native explicit pairs; 200 generated cases match the reference. Zero mismatches. | [Comparison record](native-comparison-results.json). |
| Does decoding preserve the grammar? | ✅ Six fixed cases: UTF-8 header/BOM, UTF-16LE/BE BOM, windows-1252 header/meta. | Encoding fixture and navigation log. Arbitrary restarts remain unverified. |
| Do selected existing parser tests still pass? | ✅ 16 pass, including streams, late charset changes, script source lines, and detached-subtree insertion. | [Regression log](native-regressions.log). |
| Does collecting garbage on every allocation break the focused closure case? | ✅ One fixture completes, with no crash or timeout. | [GC log](native-gc.log). This is not an ASan/UBSan run or memory-safety proof. |
| Can proposed WPT tests execute? | ✅ Two assertions pass using the vendored WPT testharness in Ladybird's runner. | [Harness output](native-wpt-output.txt), [runner log](native-wpt.log). This is not an upstream WPT submission or full WPT suite run. |

The [metadata](native-results.json) identifies the upstream revision, patch and binary digests, tools, configuration, counts, and limitations.

### Why the comparison record includes 120 baseline differences

Ladybird's existing parsing and parse5's existing parsing differ in the `select` context. For example, Ladybird retains an explicit `<a></a>` there while the pinned parse5 baseline discards it. The record preserves examples. Named cases therefore compare the experimental native result with **that engine's own explicit opening/closing pair result**. All 810 cases are compared; none is silently skipped. These baseline differences are not claimed as cross-parser agreement or fixed by the proposal.

## Reproduce the native run

Apply [native.patch](native.patch) to Ladybird revision `eb5262a610d8be85a5bf8210a34dc222af802513`. The patch includes the new parser rule, navigation selection and document-writing isolation, test fixtures, and a test-runner font-catalog adjustment. It contains no legacy projection implementation.

The recorded macOS arm64 build used Apple clang 21, Rust 1.98.0, CMake 4.4.4, Ninja 1.13.2, Qt through `/opt/homebrew/opt/qtbase`, and the upstream Release preset (`RelWithDebInfo`). It used the pinned upstream vcpkg baseline; versioned ports require that baseline's Git history. Follow the pinned upstream setup requirements, then configure:

```sh
cmake --preset Release \
  -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qtbase \
  -DENABLE_GUI_TARGETS=ON -DENABLE_LTO_FOR_RELEASE=OFF \
  -DENABLE_CRANELIFT_JIT=OFF -DENABLE_LAGOM_CCACHE=OFF \
  -DRUST_RUSTC=/absolute/path/to/rustc \
  -DRUST_CARGO=/absolute/path/to/cargo
cmake --build Build/release --target test-web --parallel 8
export LADYBIRD_SOURCE_DIR="$PWD"
Build/release/bin/test-web --test-concurrency 1 --per-test-timeout 240 \
  --filter 'Text/input/HTML/next-parsing-*.html' --results-dir results/closure
Build/release/bin/test-web --test-concurrency 1 --per-test-timeout 240 \
  --filter 'Text/input/HTML/parser-*.html' --results-dir results/regressions
Build/release/bin/test-web --test-concurrency 1 --per-test-timeout 240 \
  --collect-garbage-on-every-allocation \
  --filter 'Text/input/HTML/next-parsing-stress.html' --results-dir results/gc
Build/release/bin/test-web --test-concurrency 1 --per-test-timeout 60 \
  --filter 'Text/input/HTML/closure-wpt/self-closing.tentative.html' --results-dir results/wpt
```

Run these sequentially. The mirrored WPT fixture changes only the two testharness resource paths for the local runner; the assertions and selected document match [wpt/](wpt/README.md).

## Limits that remain

- Native selection accepts the initial navigation doctype's `next` or `self-closing` name. The proposed HTTP profile header and native API options are not implemented by this patch.
- Legacy DOMParser and string-insertion APIs remain legacy; document-writing calls that would mix grammars are rejected in selected navigations.
- The optional speculative scanner is disabled for selected documents. Recognized resource loading works in the tests; optimized look-ahead loading remains integration work.
- Upstream's general navigation restart after an incompatible late encoding change is unimplemented. Fixed decoding cases and existing on-the-fly charset regressions do not prove that missing restart path.
- The safe reference parser is a separate DOMPurify composition. This patch does not implement the proposed safe native API binding or establish every sanitizer policy.
- Other engines, broader conformance, implementer security review, ASan/UBSan, performance, and production integration remain unclaimed.

<details>
<summary>Build and harness corrections retained in the work record</summary>

The first build selected an older system Rust compiler and failed on baseline syntax; configuring Rust 1.98.0 fixed the toolchain. A copied but unused sibling FFI failed the C++ prototype check and was removed. The first comparison run reported zero semantic mismatches but differed from an obsolete 200-case expected summary. The expected report was updated only after inspecting all 810 comparisons and preserving baseline examples. The first mirrored WPT run passed both assertions but lacked a runner expected-output file; adding the verified output made its fixture pass. None of these failed runner/build outcomes is counted as a passing test.

</details>
