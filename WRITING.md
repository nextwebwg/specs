# Documentation writing guide

Last updated: 2026-09-11

This is the standard the HTML Next documentation follows. It exists so the docs are
**accessible to a wide audience of varying technical ability** without losing precision.

## North star

> The best-documented project on the web, where *best-documented does not mean most-detailed*.
> It means a reader **immediately makes sense of things, the how and the why, and always knows
> what to do next.**

Vue's documentation is the benchmark: approachable, example-first, explains its reasoning, and
never leaves you at a dead end. We aim for that bar. Length is not the goal; **fast
understanding is**. If a page is long, it earns the length by staying easy to follow, not by
being exhaustive.

## What this is (and is not)

- It **is** a small set of principles and a check to run before publishing.
- It is **not** a rigid template, a word-count rule, or an excuse to strip out necessary
  precision. Detailed, exact content still belongs in the docs, layered so a newcomer is not
  forced through it to get the idea.

## Grounding

These principles are distilled from established sources, not invented here:

- **Plain language** — ISO 24495-1:2023 (*Plain language, governing principles*) and the US
  Federal Plain Language Guidelines (plainlanguage.gov): writing is plain when the intended
  reader can **find** what they need, **understand** it, and **use** it.
- **How people read on the web** — Nielsen Norman Group (Jakob Nielsen, *How Users Read on the
  Web*): most people **scan**, they do not read word by word. Favor scannable structure, the
  **inverted pyramid** (most important first), and objective, concrete language.
- **The four kinds of documentation** — Diátaxis (Daniele Procida): *tutorials*, *how-to
  guides*, *reference*, and *explanation* answer different needs; a page is clearest when it
  does one of these at a time and does not blend them.
- **Web content that works** — Ginny Redish, *Letting Go of the Words*: write for the reader's
  task, in their words; cut throat-clearing.
- **Reading-level accessibility** — WCAG 2.1 (SC 3.1.3 Unusual Words, 3.1.4 Abbreviations,
  3.1.5 Reading Level): define unusual terms and abbreviations; offer a version a
  lower-secondary-education reader can follow where feasible.
- **What makes Vue's docs work** (an applied exemplar of the above): every concept opens with a
  minimal concrete example; the *why* sits next to the *how*; content is layered (essentials
  before deep API); and each page points to a sensible next step.

## Principles

1. **Lead with the plain "what" and "why," then the precise "how."** Open every page and major
   section with what this is, who it is for, and why it matters, in plain words, before the
   exact rules. Front-load; do not bury the point (inverted pyramid).
2. **Show an example early, for every concept.** A minimal, concrete example next to (ideally
   before) the abstract rule. People understand a shape faster than a specification of it.
3. **Always answer "what next."** No dead ends: end sections and pages with the next step or a
   meaningful cross-link. A reader should never wonder where to go.
4. **Explain the why, not only the how.** State the reasoning or the trade-off behind a
   decision. Rationale is what turns reference into understanding, and it is what readers trust.
5. **Layer for a mixed audience (progressive disclosure).** Keep an accessible entry layer and a
   precise detail layer. Add the plain layer; never replace the precise one. The Overview page
   and each page's opening are the entry layer; the module pages are the precise layer.
6. **Do one job per page (Diátaxis).** Know whether a page is explaining, showing how, or
   listing reference, and keep it to that. Mixing a tutorial into a reference table helps no one.
7. **Write plainly.** Short sentences. Active voice. Common words over jargon. Define a term the
   first time it appears; expand an acronym once. Prefer "you" and the concrete.
8. **Make it scannable.** Meaningful headings that say what the section covers; one idea per
   paragraph; lists and tables for sets and comparisons; meaningful link text (never "click
   here").
9. **Be honest about maturity.** Say plainly what is solid and what is still open. Accessible
   also means not misleading; an overclaim a reader later discovers costs more than a caveat.
10. **Respect the reader's time.** Cut warm-up sentences and restatements. Best-documented is
    not longest-documented.

## Publication language

The site distinguishes the group from the documents it publishes. The root page describes
the **Next Web Working Group** and lists proposals. Detailed HTML Next content belongs under
`/html-next/`, where the module navigation is available.

Use the current publication fields from `app/data/publications.json`; do not improvise status
labels on individual pages. Until a recognized standards venue adopts the work, call HTML
Next an **Unofficial Editor's Draft · Stage 0**, never a W3C Working Draft. A module **Level**
describes that module's maturity. A dated **Snapshot** identifies a frozen publication. None
of those terms substitutes for another.

Published snapshots are records, not pages to revise. Correct the current draft and publish
a new date instead of editing anything under `public/html-next/YYYY-MM-DD/`.

## Before you publish: a quick check

Not a template, just questions to ask of a page or section:

- Does the **first paragraph** say, in plain words, what this is, who it is for, and why it
  matters?
- Is there a **concrete example** near the top, before the abstract rules?
- Does it explain **why**, not only how?
- Is every **new term defined or linked**, and every acronym expanded once?
- Is there a **clear next step** or cross-link at the end?
- Are **maturity claims honest** (solid vs open)?
- Could a **smart non-expert** follow the first screenful without getting stuck?
- Is anything here **longer than it needs to be** to make sense?

If a page answers yes to these, it meets the bar, regardless of how detailed it then goes.
