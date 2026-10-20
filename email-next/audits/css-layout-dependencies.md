---
title: Decoration, direction and layout audit
sectionNav: true
---

# Decoration, direction and layout audit

The presentation profile uses a small sender vocabulary over a client-owned layout. These selected source rules explain how decorations, direction and box sizing interact; they do not add sender properties.

## Decorations and direction

An underline or strike can continue through descendant text even when a child specifies `text-decoration-line:none`. Decoration propagates through boxes rather than inheritance; `none` does not erase an ancestor's line. The originating box supplies its decoration color and style. Atomic inline content, including images, is excluded. Exact line thickness and placement retain browser discretion. See [Text Decoration 3, sections 2–2.5](https://www.w3.org/TR/2022/CRD-css-text-decor-3-20220505/#line-decoration).

The baseline's logical spacing and sender physical spacing address the same mapped sides. Writing mode and direction determine the mapping; cascade precedence determines the winning declaration. The client uses the horizontal writing mode. HTML direction and isolation remain governed by the [HTML direction audit](html-direction.md). This does not authorize sender writing-mode declarations. See [Logical Properties 1, section 4](https://www.w3.org/TR/2025/WD-css-logical-1-20251204/#box) and [Writing Modes 4, sections 2–3 and 6](https://www.w3.org/TR/2019/CR-css-writing-modes-4-20190730/).

## Boxes and containment

Native block, inline, list and table boxes retain their formatting behavior, including anonymous boxes. A containing block provides a sizing reference; it is not a clipping boundary. Baseline subscript and superscript offsets move their boxes without enlarging the normal line height. See [Display 3](https://www.w3.org/TR/2026/CRD-css-display-3-20260605/) and [CSS2.1 normal flow](https://www.w3.org/TR/2011/REC-CSS2-20110607/visuren.html#normal-flow).

Layout containment establishes an independent formatting context without fixing its dimensions. Paint containment clips; separately selected overflow behavior supplies scrolling. Containment on the body also suppresses its usual propagation of direction and related properties to the viewport. The host's `style` containment scopes counter and quote effects; it is not stylesheet isolation. The iframe provides a separate isolation boundary. These rules come from [Containment 1](https://www.w3.org/TR/2024/REC-css-contain-1-20240625/) and the selected style/paint sections of [Containment 2](https://www.w3.org/TR/2022/WD-css-contain-2-20220917/).

## Image sizing

Ordinary content-box sizing excludes padding and borders. Consequently, a content width capped at 100% can still produce a wider visible box. The host uses client-enforced border-box sizing for image canvases: the preferred width and maximum inline size include retained padding and borders. The remaining content area displays the image with its intrinsic proportions. This is a client layout choice, not a new sender declaration. See [Sizing 3, box sizing](https://www.w3.org/TR/2026/WD-css-sizing-3-20260904/#box-sizing).

The [image box check](../evidence/README.md#image-box-bounds) measured the original overflow and verifies the correction for both reading directions, two narrow widths and two root font sizes. These cases do not prove arbitrary spacing fits every possible container: padding and borders alone can exceed an extremely small available width.

## Scope

This review covers selected decoration, physical/logical mapping, horizontal direction integration, normal-flow display, replaced sizing, percentage contributions and containment. It includes applicable CSS2.1 corrections. Captured source hashes and exact read ranges are retained privately. Several selected modules are drafts; their dated revisions are linked above. No full-module, cross-engine or assistive-technology conformance is claimed. Full Unicode bidi rendering and inline fragmentation remain separate source boundaries. Selected scrolling and viewport behavior is covered by the [overflow audit](css-overflow.md).
