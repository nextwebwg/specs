---
title: Publishing & Integration
order: 5
blurb: navigation · presentation survey · migration gaps
eyebrow: Expressive Markdown · Optional profile
status: Unofficial Editor's Draft · Stage 0
---

# Publishing & Integration

The optional publishing profile defines shared navigation metadata. The
presentation survey records what a documentation publisher must preserve to
reproduce the Declarative HTML Components proposal with the same styles.

## Navigation frontmatter

Keep a readable document title and optionally give it a shorter navigation label.

```yaml
---
title: Installing Expressive Markdown
navigation:
  label: Installation
  hidden: false
---
```

| Field | Type | Meaning and default |
| --- | --- | --- |
| `navigation` | Mapping | Optional publishing-profile metadata, retained in `document.metadata.navigation`. |
| `navigation.label` | Plain-text string | Label for generated site navigation. Omission uses the document title's plain-text projection; a publisher without a document title uses its declared fallback. |
| `navigation.hidden` | Boolean | Omit the document from generated site navigation. Default false. The document remains available at its address. |

The label can serve a sidebar, menu or chapter index. It does not replace the
document title or rewrite links someone authored explicitly. Hidden navigation
does not change the document's content or its availability. A document's own
TOC is authored content with a separate refresh contract.

These fields are optional. A core parser preserves them without having to build
navigation. A publishing-profile implementation uses their declared types;
invalid values remain preserved and recommend a diagnostic rather than string
or boolean coercion. A meaningful metadata null stays null, even when it is
invalid for a profile field. Preserve unknown keys within `navigation`.

Routing aliases are outside this profile. Routing history and redirect policy
belong to the publishing application's route configuration. An extension key
still survives ordinary frontmatter round-tripping without becoming a recognized
Expressive field.

## Survey of the existing proposal

The current Declarative HTML Components documents are a concrete migration
case. The survey covers every named content convention in their compiler and
contribution guide, plus the components and CSS that present those conventions.
It identifies representation and integration gaps; it does not claim Markupress
already reproduces the site.

The source baseline is `nextwebwg/specs` revision `80593f8` and the published
site observed 17 October 2026. The proposal's current markup flavor
is distinct from Expressive Markdown. Migration must translate that flavor,
preserve authored content, and bind the result to the existing design system.

| Current presentation | Meaning/content to preserve | Expressive mapping or remaining work |
| --- | --- | --- |
| Document masthead, eyebrow, tagline, status and metadata rows | Identity, title, publication status, reading paths and attribution | Root title/metadata plus readable body. Publisher-owned masthead mapping; custom publication fields remain preserved metadata. |
| Numbered sections, subsection rules and anchors | Ordered headings and explicit or output-derived link targets | Native heading nodes, authored IDs and the declared output-anchor policy. Numbering/rules are renderer CSS. |
| Lede paragraphs | Introductory prose with stronger visual emphasis | Paragraph attributes or styled block group; the existing `lede` class can be retained through native HTML. |
| Paragraphs, emphasis, strong, deletion, inline code and links | Ordinary readable content and inline structure | Native core nodes and supported native attributes. |
| `note`, `ex`, `norm`, `warn`, `future` callouts | Context, example, normative rule, review/caution and future exploration | Containers with profile-defined subtypes. Preserve the distinct meanings; `norm` must not become merely an informational color. Only note/tip/warning/danger are the core callout registry. |
| Code panels and filenames | Literal example, language and optional filename | Code value/language/string caption. Shiki colors and dual-theme token styles are derived presentation. |
| Ordinary and comparison tables | Row/column relationships, headings, alignment and inline content | Structured tables/cells; keep overflow wrappers and CSS in the renderer. Rich cells and spans remain structured data. |
| Numbered algorithm lists | Ordered steps and algorithm styling | Ordered list plus attributes. A new procedure language is not required to retain the existing list. |
| Definition lists | Explicit term/description relationships | Dedicated syntax/AST extension needs a contract; native HTML can preserve them, but opaque HTML is not equivalent to structured editing. |
| Element reference entries | Authored entry title, descriptive role label and definition rows | Container title/body with an entry profile; definition-list support remains a structured-data gap. The displayed role label must not be mistaken for an ARIA role. |
| Normative keywords (`kw`) | Requirement-language emphasis without changing the word | Inline node/profile meaning or styled group, preserving the keyword text. Semantic mapping needs a declared profile contract. |
| Defined terms (`dfn`) | A term being defined | Inline definition profile or native HTML preservation. Do not collapse its semantic distinction into an arbitrary color. |
| Level pills (`l1`, `inc`, `soon`) | Authored maturity label and variant | Chip data with retained label and profile attributes. Preserve level meaning separately from hue. |
| Side-by-side blocks (`two`) | Grouped content with comparison layout | Generic block group or a custom container with retained body and layout attributes; CSS supplies responsive columns. |
| Target cards (`targets`) | Label/description pairs presented in a grid | Container/group retaining each pair. Structured definition-list support is needed for an equivalent editable import. |
| Source/converter/output flow (`flow`, highlighted `acc` step) | Ordered stages and a highlighted authored stage | List in a custom container, retaining per-stage attributes. Arrows are presentation. |
| Problem-and-answer cards (`fix`) | Title, summary, numbered item and two labelled lists | Nested containers with named titles and list bodies; custom layout binding. No special positional child may silently acquire a title's role. |
| Evidence records (`record`) | Label, claim and supporting prose | Containers with explicit title/body roles and retained text; a rendering profile places the label and claim. |
| Citation markers and numbered references | Reference identity, text, link target and ordering | Footnote/reference syntax and structured AST mapping remain a gap. Native markup preserves output; a real migration must preserve editable reference relationships. |
| Variables within code, explicit breaks and nonbreaking spaces | Variable meaning and intentional text boundaries | Native HTML preservation for variable markup; break/text nodes retain line and character meaning. Structured variable-in-code mapping needs a profile contract. |
| Section anchor wrappers | A grouping's explicit link target | Generic group/container ID; preserve the target without adding an unnecessary visible heading. |
| Chapter index | Real links/titles/descriptions derived from the chapter catalogue | Publisher generates readable navigation content. It must not export an empty component placeholder as the only representation. |
| Search, sidebar, pager, masthead and footer | Publisher navigation and interactive site shell | Publisher integrations, using the existing shared shell. They are not additional Markdown body node types. |
| Snapshots and history | Publication provenance and immutable editions | Publisher-owned records and routes. A new proposal must not inherit another proposal's snapshot. |
| Light/dark themes, typography, borders, spacing and responsive behavior | Consistent visual presentation | Reuse the current design tokens and CSS. These are renderer assets, not hardcoded language meanings. |

## What still needs a language decision

Definition lists and reference relationships are the two clear syntax/data gaps
exposed by the survey. They need explicit semantics, source forms, AST shapes,
conversion guidance and round-trip fixtures before a structured migration can
claim completeness. A preservation-only HTML fallback keeps content but does
not complete those decisions.

The other special blocks can use the existing generic content roles and open
subtypes. Their rendering profiles must still specify how title/body data maps
to the current layouts. Mapping everything to an opaque component or one generic
styled span would fail the semantic-preservation goal.

Live component examples are a separate runtime integration. Literal code samples
stay inert. Core Markdown parsing does not acquire JavaScript execution simply
because the publishing site supports an interactive example.

## Migration acceptance

A future Markupress integration should import every chapter and compare both
content and visual output against the current site. Required evidence includes:

- Identical authored text, code, reference targets and semantic distinctions.
- All compiler conventions above mapped, with no silently omitted component,
  definition row, reference, variant, ID or presentation attribute.
- The same shared CSS/design tokens at desktop and mobile widths, in light and
  dark themes, with tables and code remaining readable without page overflow.
- Readable generated navigation in saved/exported Markdown, including TOCs and
  chapter indexes; navigation metadata remains editable frontmatter.
- A declared result for every unsupported construct. No claim of complete
  migration while definition/reference data or native presentation remains opaque.

The current Expressive proposal uses the existing site's compiler, components
and styles. That verifies its presentation within this site; it is not evidence
that the future Expressive parser or Markupress integration is implemented.

## Source references

- [Chapter authoring conventions](https://github.com/nextwebwg/specs/blob/80593f8/CONTRIBUTING.md) and [chapter compiler](https://github.com/nextwebwg/specs/blob/80593f8/tools/compile.ts).
- [Declarative HTML Components source chapters](https://github.com/nextwebwg/specs/tree/80593f8/html-next).
- Published examples: [proposal front page](/declarative-components/),
  [Types](/declarative-components/types), [Templating](/declarative-components/templating)
  and [Reactivity & Data](/declarative-components/reactivity).

Continue with [Presentation Coverage](/expressive-markdown/presentation) for the
broader documentation and rich-editor acceptance matrix.
