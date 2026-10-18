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
.callout { border-inline-start: 4px solid #9a6700; padding: 12px 16px; background: color-mix(in srgb, #e6b800 10%, Canvas); }
.callout header { font-weight: 650; }
.chip, .mention { display: inline-block; padding: 1px 7px; border-radius: 12px; background: color-mix(in srgb, #20a464 15%, Canvas); }
.mention { background: color-mix(in srgb, #8560cf 15%, Canvas); }
figure { margin: 0; }
figcaption { margin-top: 8px; color: GrayText; }
details { border: 1px solid GrayText; border-radius: 6px; padding: 12px; }
summary { cursor: pointer; font-weight: 600; }
a { color: LinkText; }
`;

export function renderPreview(html: string, title: string, height = "200"): string {
  if (!/^[1-9]\d*$/.test(height)) throw new Error("A rendering preview height must be a positive integer.");
  // An empty sandbox blocks scripts and parent access. CSP also keeps examples
  // self-contained: figures use inline SVG/data, never external network assets.
  const document = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"><style>${previewStyle}</style></head><body>${html}</body></html>`;
  return `<div class="render-preview"><p><strong>Rendering example</strong></p><iframe title="${escapeAttribute(title)}" sandbox="" loading="lazy" height="${height}" style="width:100%;border:1px solid GrayText;border-radius:6px" srcdoc="${escapeAttribute(document)}"></iframe></div>`;
}
