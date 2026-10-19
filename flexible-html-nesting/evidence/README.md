# Flexible HTML Nesting: baseline evidence

These three deterministic parse5 8.0.1 observations establish the motivating legacy behavior: a custom host is foster-parented out of a table; an ordinary marked div has no new grammar and is relocated while its row enters a tbody; a list wrapper remains in the DOM while the li's direct parent is the div.

They do not implement or prove the proposed marker, content-model relaxation, layout, shadow participation, accessibility, or combined profile. parse5 8.0.1 is pinned by the sibling self-closing evidence package and does not represent all later HTML changes, particularly select parsing.

Reproduce with a Node version accepted by that package:

```sh
cd self-closing-html/evidence
npm ci --ignore-scripts --no-audit --no-fund
cd ../../flexible-html-nesting/evidence
node baseline.mjs
```

`baseline-results.json` records the source inputs, asserted parent relationships, runtime, and script digest. The renderer and parser comparison cases still required are specified in the proposal and layout chapter. No safety result transfers from the separate self-closing proposal.
