# Draft Web Platform Test fixtures

These are proposed feature-conformance tests in WPT layout, not an upstream submission or full WPT infrastructure run. Place them under an appropriate WPT HTML feature directory and serve through the WPT test server, which supplies `/resources/testharness.js` and `/resources/testharnessreport.js`.

The selected navigation fixture requires an implementation of the proposed grammar. Existing browsers ignoring the declaration will not pass it; unsupported feature behavior is not converted into a passing result. DOMParser's legacy isolation has a separate assertion.

Both assertions passed using Ladybird’s vendored WPT testharness in its native test runner. The mirror changes only the two harness resource paths. [Executed output and exact scope](../native.md). No full WPT suite result is claimed here.
