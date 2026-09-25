# Repository guidance

## Authority

- Treat README.md and checked-in project documentation as product authority.
- Treat threadlabs.config.json as the repository-standard manifest.
- Ask the owner when requirements conflict or a destructive operation is required.

## Safe work

- Preserve unrelated changes and never rewrite shared Git history without explicit approval.
- Preview Foundation plans before applying them.
- Check threadlabs.config.json for each path's ownership mode before editing. For managed paths, use .threadlabs.lock.json to confirm the last-applied content and change the owning Foundation template; preserve local paths and stop on ambiguous ownership.
- Use Oxlint for JavaScript and TypeScript linting. Do not add Prettier or another repository-wide formatter.
- Do not add Tailwind. Use project-owned CSS, CSS Modules, or an explicitly selected non-Tailwind styling approach.

## Code documentation

- Explain invariants, non-obvious algorithms, platform boundaries, lifecycle ownership, measured performance tradeoffs, security limits, and why the code has its current shape.
- Put local warnings beside the code and cross-cutting rationale in checked-in design documentation. Keep both linked to tests or other evidence that proves the claim.
- Do not add blanket JSDoc, restate identifiers in sentences, or enforce comment density and word-count metrics. Semantic quality remains a review judgment; deterministic checks protect only declared documentation obligations from drift.

## Performance decisions

- Compare effects against variance across independent fresh-process runs of the complete benchmark set; repeated samples within one process do not establish stability. When measurement cannot distinguish a candidate from that variance, classify and shelve it as inconclusive for a quieter rerun; do not reject it. Do not invent a minimum improvement threshold. Keep any reliable improvement with no benchmark regressions and no significant code or size growth.

## Verification

- During development, run the smallest focused test plus `pnpm verify:inner`.
- Before handoff, run `pnpm verify:pr` and report commands, results, skips, and remaining judgment.
- Publication remains human-approved and runs only through the protected release workflow.
