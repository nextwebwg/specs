---
title: Scrolling and clipping audit
sectionNav: true
---

# Scrolling and clipping audit

Clipping keeps message content inside its rendering area. Scrolling makes overflowing content reachable. These are separate requirements: hiding overflow alone does not satisfy the presentation profile.

This review covers the rules reached by the actual host in [CSS Overflow 3, 7 October 2025](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/): overflow concepts, scroll origins, overflow values, viewport propagation and scrollbar sizing/default gutters. It is a Working Draft. The captured latest-publication and dated-publication bytes match; exact hashes and reviewed ranges are retained privately. This is not a full-module audit or a change to the sender CSS vocabulary.

## Reachable content

The host uses `overflow:auto` on the message body and on client-created table wrappers. When content overflows, `auto` supplies scrolling. By contrast, `hidden` permits programmatic scrolling without direct user scrolling, while `clip` forbids scrolling entirely. Paint containment does not replace the scrolling mechanism. See [overflow values](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#overflow-control) and the [containment audit](css-layout-dependencies.md).

Scrollable overflow includes relevant line boxes and descendant border boxes. Ink effects such as decoration and overhanging glyphs do not necessarily enlarge the scrollable area. A clipped mark is therefore not automatically recoverable by scrolling. The draft also leaves some ordinary descendant-margin inclusion undefined. A renderer must not infer accessibility merely from a large `scrollWidth` or the presence of a scrollbar. See [overflow concepts](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#overflow-concepts).

Each table receives its own focusable, named wrapper, including nested tables. A descendant scroll container traps its own overflow instead of simply passing it to the outer container. Checking the message's outer bounds consequently does not prove that every nested table can be read. Keyboard access, visible focus and reaching both ends of each relevant container remain behavioral checks.

## Direction and viewport

The default scroll origin is the block-start/inline-start corner. In horizontal RTL content, inline-start is the right side. Content placed beyond the origin can occupy an unreachable region that browsers must clip. The source does not define a universal numerical coordinate convention for scrolling APIs; code must not assume that all RTL scrolling uses positive offsets. See [scrolling overflow](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#scrolling).

The host contains the body. This disables the usual HTML body overflow propagation to the viewport; the body and viewport must not be treated as one scroll container. Root `visible` overflow is interpreted as `auto` at the viewport. See [viewport propagation](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#overflow-propagation).

Classic scrollbars consume layout space; overlay scrollbars do not. Their size, appearance and side are browser/platform choices. A narrow-window check on one scrollbar configuration does not establish identical geometry on another. See [scrollbar layout](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#scrollbar-layout).

## Evidence boundary

The existing host checks exercise bounded table scrolling and containment cases. This source review adds no browser execution. Focusability is an implementation provision, not proof of screen-reader behavior or successful keyboard traversal through every nested container. Larger root fonts and narrower CSS viewports are useful checks, but neither is a substitute for native browser zoom testing. Native zoom, platform scrollbar variants, cross-engine behavior and complete nested RTL focus/scroll traversal remain unverified here.

Printing is a separate concern: scrolling is unavailable in static output. The draft recommends exposing relevant content through an appropriate print layout; the interactive host evidence does not certify that layout.
