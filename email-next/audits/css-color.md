---
title: Message colors and user palettes
sectionNav: true
---

# Message colors and user palettes

Email Next permits opaque three- or six-digit hexadecimal sender colors, plus transparent backgrounds. The client owns system colors and accessibility overrides. Accepting a color does not establish readable contrast.

## Selected color meanings

The [CSS Color Level 4 draft](https://www.w3.org/TR/2026/CRD-css-color-4-20261009/#hex-notation) defines these hexadecimal forms in sRGB; three digits expand by repeating each digit. The profile excludes alpha hexadecimal forms and color functions even though CSS supports them.

Transparent backgrounds do not erase the text or underlying background. Client `currentColor` borders follow the element's foreground. `Canvas`, `CanvasText` and `LinkText` express user/browser palette roles, not fixed RGB constants. The selected review covers these definitions and their value resolution, not every color space or image color-management operation.

## Dark mode and forced colors

Declaring support for light and dark schemes does not automatically recolor sender declarations or guarantee their contrast. Mixing a fixed foreground with a system background can make text illegible. Clients must keep the readable plain view available and honor user color overrides. [CSS Color Adjustment](https://www.w3.org/TR/2025/CR-css-color-adjust-1-20251216/#preferred)

The host's forced-color rules replace sender foreground/background colors and preserve visible link styling. Sender declarations cannot disable forced-color adjustment. Browser emulation is useful evidence but does not establish behavior in a user's operating-system theme or screen reader.

## Verification boundary

The browser-host palette case checks permitted hex values, transparent backgrounds, light/dark system pairs and the forced-color override. Background/border painting, selected media-query definitions and native accessibility remain separately reviewed dependencies. Neither this audit nor the finite sender vocabulary promises that every authored color combination is legible.
