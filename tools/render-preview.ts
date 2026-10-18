import { createHash } from "node:crypto";
import { tabsController } from "./render-tabs.ts";

// Documentation illustrations are authored separately from normative source examples.
// Keep their HTML out of Vue's template parser and the publishing page's DOM/styles.
const escapeAttribute = (value: string) => value
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;").replace(/\{/g, "&#123;");

export const previewStyle = `
:root { color-scheme: light dark; font: 15px/1.5 system-ui, sans-serif; }
body { margin: 16px; color: CanvasText; background: Canvas; }
body > :first-child { margin-top: 0; }
body > :last-child { margin-bottom: 0; }
table { border-collapse: collapse; width: 100%; }
th { font-weight: 700; background: color-mix(in srgb, CanvasText 6%, Canvas); }
th, td { border: 1px solid GrayText; padding: 8px 12px; text-align: left; vertical-align: top; }
td > :first-child, th > :first-child { margin-top: 0; }
td > :last-child, th > :last-child { margin-bottom: 0; }
td ul, td ol, th ul, th ol { padding-inline-start: 1.3em; margin-block: .35em; }
pre { overflow: auto; padding: 12px; background: color-mix(in srgb, CanvasText 6%, Canvas); border-radius: 6px; }
code { font-family: ui-monospace, monospace; }
.callout { border-inline-start: 4px solid #64748b; padding: 12px 16px; background: color-mix(in srgb, #64748b 10%, Canvas); }
.callout[data-type="note"] { border-inline-start-color: #2563eb; background: color-mix(in srgb, #2563eb 10%, Canvas); }
.callout[data-type="warning"] { border-inline-start-color: #9a6700; background: color-mix(in srgb, #e6b800 10%, Canvas); }
.callout > header { font-weight: 650; }
.chip, .mention { display: inline-block; padding: 1px 7px; border-radius: 12px; background: color-mix(in srgb, #20a464 15%, Canvas); }
.mention { background: color-mix(in srgb, #8560cf 15%, Canvas); }
figure { margin: 0; }
figcaption { margin-top: 8px; color: GrayText; }
details { border: 1px solid GrayText; border-radius: 6px; padding: 12px; }
summary { cursor: pointer; font-weight: 600; }
a { color: LinkText; }
[role="tablist"] { display: flex; flex-wrap: wrap; gap: 6px; margin-block-end: 12px; }
[role="tab"] { font: inherit; color: inherit; background: Canvas; border: 1px solid GrayText; border-radius: 6px; padding: 7px 12px; cursor: pointer; }
[role="tab"][aria-selected="true"] { font-weight: 700; background: color-mix(in srgb, #2563eb 15%, Canvas); border-color: #2563eb; }
[role="tab"]:focus-visible, [role="tabpanel"]:focus-visible { outline: 2px solid #2563eb; outline-offset: 3px; }
[role="tabpanel"] > :first-child { margin-top: 0; }
`;

export function renderPreview(html: string, title: string, height = "200", interactive?: string): string {
  if (!/^[1-9]\d*$/.test(height)) throw new Error("A rendering preview height must be a positive integer.");
  if (interactive !== undefined && interactive !== "tabs") throw new Error("Unknown interactive preview mode.");
  const script = interactive === "tabs" ? tabsController : "";
  const hash = createHash("sha256").update(script).digest("base64");
  // Only the exact publisher controller may run. The opaque sandbox still
  // denies parent access; authored scripts, handlers and external assets stay blocked.
  const scripts = script ? `script-src 'sha256-${hash}'; script-src-attr 'none';` : "script-src 'none';";
  const document = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; ${scripts} style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"><style>${previewStyle}</style></head><body>${html}${script ? `<script>${script}</script>` : ""}</body></html>`;
  return `<div class="render-preview"><p><strong>Rendering example</strong></p><iframe title="${escapeAttribute(title)}" sandbox="${script ? "allow-scripts" : ""}" loading="lazy" height="${height}" style="width:100%;border:1px solid GrayText;border-radius:6px" srcdoc="${escapeAttribute(document)}"></iframe></div>`;
}
