// The reference implementation of this repository's Markdown flavor (documented in
// CONTRIBUTING.md). It compiles a chapter into a Vue single-file component built from the
// publishing site's components (Section, Callout, CodeBlock, …), so a chapter renders exactly as
// a hand-written page would. `pnpm check` runs it over every chapter.
import { readFileSync } from "node:fs";
import MarkdownIt from "markdown-it";
import type Token from "markdown-it/lib/token.mjs";
import container from "markdown-it-container";
import deflist from "markdown-it-deflist";
import { parse as parseYaml } from "yaml";

export interface ChapterMeta {
  title: string;
  order?: number;
  blurb?: string;
  navGroup?: string;
  layout?: "chapter" | "proposal";
  pager?: boolean;
  eyebrow?: string;
  status?: string;
  stamp?: string;
}

interface Node {
  token: Token;
  children: Node[];
}

type Mode = "template" | "html";

export function readFrontmatter(source: string): { meta: ChapterMeta; body: string } {
  const match = source.match(/^---\n([\s\S]*?)\n---\n/);
  if (!match) throw new Error("A chapter must begin with YAML frontmatter.");
  return { meta: parseYaml(match[1]) as ChapterMeta, body: source.slice(match[0].length) };
}

// ---------------------------------------------------------------------------------------------
// Parser: CommonMark + GFM tables, plus the flavor's conventions.

function createParser(): MarkdownIt {
  const md = new MarkdownIt({ html: false, linkify: false, typographer: false });
  md.use(deflist);
  // Pandoc fenced divs: `::: name` or `::: {.class #id key="value"}`.
  md.use(container, "div", { validate: () => true });

  // A line holding only `::name` places a site component, as a CommonMark generic leaf directive.
  md.block.ruler.before("paragraph", "leaf_component", (state, startLine, _endLine, silent) => {
    const start = state.bMarks[startLine] + state.tShift[startLine];
    const line = state.src.slice(start, state.eMarks[startLine]);
    const match = line.match(/^::([a-z][\w-]*)\s*$/);
    if (!match) return false;
    if (!silent) state.push("leaf_component", "", 0).info = match[1];
    state.line = startLine + 1;
    return true;
  });

  // Footnote definitions `[^n]: text` become the chapter's numbered reference list.
  md.block.ruler.before("reference", "footnote_def", (state, startLine, _endLine, silent) => {
    const start = state.bMarks[startLine] + state.tShift[startLine];
    const line = state.src.slice(start, state.eMarks[startLine]);
    const match = line.match(/^\[\^(\d+)\]:\s+(.*)$/);
    if (!match) return false;
    if (!silent) {
      const token = state.push("footnote_def", "", 0);
      token.info = match[1];
      token.content = match[2];
      token.children = [];
      state.md.inline.parse(match[2], state.md, state.env, token.children);
    }
    state.line = startLine + 1;
    return true;
  }, { alt: ["paragraph"] });

  // Inline: `[^n]` reference, `[text]{.class}` span, and the few inline HTML elements Markdown lacks.
  md.inline.ruler.before("link", "footnote_ref", (state, silent) => {
    const match = state.src.slice(state.pos).match(/^\[\^(\d+)\]/);
    if (!match) return false;
    if (!silent) state.push("footnote_ref", "", 0).info = match[1];
    state.pos += match[0].length;
    return true;
  });
  md.inline.ruler.before("link", "span", (state, silent) => {
    if (state.src.charCodeAt(state.pos) !== 0x5b /* [ */) return false;
    const end = state.md.helpers.parseLinkLabel(state, state.pos, true);
    if (end < 0) return false;
    const attrs = state.src.slice(end + 1).match(/^\{((?:\s*\.[\w-]+)+)\s*\}/);
    if (!attrs) return false;
    if (!silent) {
      const open = state.push("span_open", "span", 1);
      open.attrSet("class", attrs[1].trim().split(/\s+/).map((c) => c.slice(1)).join(" "));
      const oldMax = state.posMax;
      state.pos += 1;
      state.posMax = end;
      state.md.inline.tokenize(state);
      state.posMax = oldMax;
      state.push("span_close", "span", -1);
    }
    state.pos = end + 1 + attrs[0].length;
    return true;
  });
  md.inline.ruler.before("text", "inline_element", (state, silent) => {
    if (state.src.charCodeAt(state.pos) !== 0x3c /* < */) return false;
    const match = state.src.slice(state.pos).match(/^(?:<\/?(?:var|code)>|<br>)/);
    if (!match) return false;
    if (!silent) state.push("inline_element", "", 0).content = match[0];
    state.pos += match[0].length;
    return true;
  });
  return md;
}

// ---------------------------------------------------------------------------------------------
// Token stream → tree, and block attributes written as a trailing `{.class #id}`.

function toTree(tokens: Token[]): Node[] {
  const root: Node[] = [];
  const stack: Node[][] = [root];
  for (const token of tokens) {
    if (token.nesting === -1) {
      stack.pop();
      continue;
    }
    const node: Node = { token, children: [] };
    stack.at(-1)!.push(node);
    if (token.nesting === 1) stack.push(node.children);
  }
  return root;
}

const ATTRS = /\s*\{((?:\s*[.#][\w-]+)+)\s*\}$/;

function applyAttrs(target: Token, spec: string) {
  for (const part of spec.trim().split(/\s+/)) {
    if (part.startsWith("#")) target.attrSet("id", part.slice(1));
    else target.attrJoin("class", part.slice(1));
  }
}

// Take a trailing `{…}` off an inline token's last text child.
function takeTrailingAttrs(inline: Token | undefined): string | null {
  const last = inline?.children?.at(-1);
  if (!last || last.type !== "text") return null;
  const match = last.content.match(ATTRS);
  if (!match) return null;
  last.content = last.content.slice(0, match.index);
  if (last.content === "") {
    inline!.children!.pop();
    if (inline!.children!.at(-1)?.type === "softbreak") inline!.children!.pop();
  }
  return match[1];
}

function resolveAttrs(nodes: Node[]) {
  for (const node of nodes) {
    const { token } = node;
    if (token.type === "heading_open" || token.type === "paragraph_open") {
      const attrs = takeTrailingAttrs(node.children[0]?.token);
      if (attrs) applyAttrs(token, attrs);
    }
    if (token.type === "bullet_list_open" || token.type === "ordered_list_open") {
      // `{.class}` on the line after a list attaches to the list (the markdown-it-attrs convention).
      const lastItem = node.children.at(-1);
      const lastInline = lastItem?.children.at(-1)?.children[0]?.token;
      const text = lastInline?.children?.at(-1);
      const breakBefore = lastInline?.children?.at(-2)?.type === "softbreak";
      if (text?.type === "text" && breakBefore && /^\{((?:\s*[.#][\w-]+)+)\s*\}$/.test(text.content)) {
        applyAttrs(token, takeTrailingAttrs(lastInline)!);
      }
    }
    resolveAttrs(node.children);
  }
}

// ---------------------------------------------------------------------------------------------
// Rendering

const escapeText = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/\{/g, "&#123;");

const plainText = (inline: Token | undefined): string =>
  (inline?.children ?? []).map((t) => (t.type === "text" || t.type === "code_inline" ? t.content : t.type === "softbreak" ? " " : "")).join("");

function parseDivInfo(info: string): { classes: string[]; id?: string; attrs: Record<string, string> } {
  const text = info.trim().replace(/^div\s*/, "");
  if (!text.startsWith("{")) return { classes: text ? [text.split(/\s+/)[0]] : [], attrs: {} };
  const inner = text.replace(/^\{|\}$/g, "");
  const out = { classes: [] as string[], id: undefined as string | undefined, attrs: {} as Record<string, string> };
  for (const m of inner.matchAll(/([.#][\w-]+)|([\w-]+)=(?:"((?:[^"\\]|\\.)*)"|'([^']*)')/g)) {
    if (m[1]?.startsWith(".")) out.classes.push(m[1].slice(1));
    else if (m[1]?.startsWith("#")) out.id = m[1].slice(1);
    else out.attrs[m[2]] = m[3] === undefined ? m[4] : m[3].replace(/\\(.)/g, "$1");
  }
  return out;
}

class Compiler {
  md = createParser();
  codes: string[] = [];
  data: unknown[] = [];

  inline(token: Token | undefined, mode: Mode): string {
    if (!token?.children) return "";
    const links: string[] = [];
    let out = "";
    for (const t of token.children) {
      switch (t.type) {
        case "text": case "text_special": out += escapeText(t.content); break;
        case "softbreak": out += " "; break;
        case "hardbreak": out += "<br>"; break;
        case "code_inline": out += `<code>${escapeText(t.content)}</code>`; break;
        case "em_open": out += "<em>"; break;
        case "em_close": out += "</em>"; break;
        case "strong_open": out += "<strong>"; break;
        case "strong_close": out += "</strong>"; break;
        case "s_open": out += "<s>"; break;
        case "s_close": out += "</s>"; break;
        case "span_open": out += `<span class="${t.attrGet("class")}">`; break;
        case "span_close": out += "</span>"; break;
        case "inline_element": out += t.content; break;
        case "footnote_ref": out += `<sup class="ref"><a href="#r${t.info}">${t.info}</a></sup>`; break;
        case "link_open": {
          const href = t.attrGet("href")!;
          // Site-internal links navigate client-side, as NuxtLink; v-html strings cannot hold components.
          const internal = mode === "template" && href.startsWith("/");
          links.push(internal ? "</NuxtLink>" : "</a>");
          out += internal ? `<NuxtLink to="${escapeText(href)}">` : `<a href="${escapeText(href)}">`;
          break;
        }
        case "link_close": out += links.pop(); break;
        default: throw new Error(`Unsupported inline construct: ${t.type}`);
      }
    }
    return out;
  }

  bindData(value: unknown): string {
    this.data.push(value);
    return `__data[${this.data.length - 1}]`;
  }

  attrs(token: Token): string {
    return (token.attrs ?? []).map(([k, v]) => ` ${k}="${escapeText(v)}"`).join("");
  }

  // Blocks, wrapped into <Section> at each `##`, as a hand-written page groups them.
  blocks(nodes: Node[]): string {
    const out: string[] = [];
    let open = false;
    let run: Node[] = [];
    const flush = () => { if (run.length) out.push(this.children(run)); run = []; };
    const close = () => { flush(); if (open) out.push("</Section>"); open = false; };
    for (const node of nodes) {
      const { token } = node;
      if (token.type === "heading_open" && token.tag === "h2") {
        close();
        out.push(`<Section title="${escapeText(plainText(node.children[0]?.token))}"${this.attrs(token)}>`);
        open = true;
        continue;
      }
      // `---` ends the current section, for the rare block that sits between two sections.
      if (token.type === "hr") {
        close();
        continue;
      }
      if (token.type === "container_div_open" && node.children[0]?.token.tag === "h2") {
        close();
        out.push(this.block(node));
        continue;
      }
      run.push(node);
    }
    close();
    return out.filter(Boolean).join("\n");
  }

  // Consecutive `[^n]:` definitions become one reference list; a run of `::: fix` becomes one v-for.
  children(nodes: Node[]): string {
    const out: string[] = [];
    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      if (node.token.type === "footnote_def") {
        const refs: string[] = [];
        for (; nodes[i]?.token.type === "footnote_def"; i++) {
          if (Number(nodes[i].token.info) !== refs.length + 1) throw new Error(`Reference [^${nodes[i].token.info}] is out of sequence.`);
          refs.push(this.inline(nodes[i].token, "html"));
        }
        i--;
        out.push(`<RefList :refs="${this.bindData(refs)}" />`);
        continue;
      }
      if (node.token.type === "container_div_open" && parseDivInfo(node.token.info).classes[0] === "fix") {
        const fixes = [];
        for (; nodes[i]?.token.type === "container_div_open" && parseDivInfo(nodes[i].token.info).classes[0] === "fix"; i++) {
          fixes.push(this.fixCard(nodes[i], fixes.length + 1));
        }
        i--;
        out.push(`<FixCard v-for="f in ${this.bindData(fixes)}" :key="f.idx" v-bind="f" />`);
        continue;
      }
      out.push(this.block(node));
    }
    return out.filter(Boolean).join("\n");
  }

  block(node: Node): string {
    const { token } = node;
    switch (token.type) {
      case "paragraph_open":
        return token.hidden
          ? this.inline(node.children[0]?.token, "template")
          : `<p${this.attrs(token)}>${this.inline(node.children[0]?.token, "template")}</p>`;
      case "heading_open":
        if (token.tag !== "h3") throw new Error(`Unexpected ${token.tag}; chapters use ## sections and ### subsections.`);
        token.attrJoin("class", "sub");
        return `<h3${this.attrs(token)}>${this.inline(node.children[0]?.token, "template")}</h3>`;
      case "bullet_list_open":
      case "ordered_list_open": {
        const tag = token.type === "bullet_list_open" ? "ul" : "ol";
        return `<${tag}${this.attrs(token)}>${node.children.map((li) => `<li>${this.children(li.children)}</li>`).join("\n")}</${tag}>`;
      }
      case "blockquote_open": return this.callout(node);
      case "fence": return this.codeBlock(token);
      case "table_open": return `<div class="tablewrap">${this.table(node)}</div>`;
      case "container_div_open": return this.div(node);
      case "leaf_component":
        if (token.info === "chapter-index") return "<ChapterIndex />";
        throw new Error(`Unknown component ::${token.info}`);
      case "dl_open":
        return `<dl>${node.children.map((c) => `<${c.token.tag}>${c.token.tag === "dt" ? this.inline(c.children[0]?.token, "template") : this.children(c.children)}</${c.token.tag}>`).join("")}</dl>`;
      case "footnote_def":
        return this.children([node]);
      default:
        throw new Error(`Unsupported block construct: ${token.type}`);
    }
  }

  table(node: Node): string {
    const render = (n: Node): string => {
      const t = n.token;
      if (t.type === "inline") return this.inline(t, "template");
      return `<${t.tag}${this.attrs(t)}>${n.children.map(render).join("")}</${t.tag}>`;
    };
    return render(node);
  }

  // Obsidian-style callout: `> [!kind] Title`.
  callout(node: Node): string {
    const first = node.children[0];
    const inline = first?.children[0]?.token;
    const head = inline?.children?.[0];
    const match = head?.type === "text" ? head.content.match(/^\[!(note|ex|norm|warn)\]\s*(.*)$/) : null;
    if (!match) throw new Error("A blockquote must be a callout: > [!note|ex|norm|warn] Title");
    const rest = inline!.children!.slice(1);
    const breakAt = rest.findIndex((t) => t.type === "softbreak");
    const title = match[2] + (breakAt < 0 ? plainText({ children: rest } as Token) : plainText({ children: rest.slice(0, breakAt) } as Token));
    const body = [...node.children];
    if (breakAt < 0) body.shift();
    else inline!.children = rest.slice(breakAt + 1);
    return `<Callout kind="${match[1]}" tag="${escapeText(title.trim())}">\n${this.children(body)}\n</Callout>`;
  }

  codeBlock(token: Token): string {
    const [lang, ...meta] = token.info.trim().split(/\s+/);
    const filename = meta.join(" ").match(/title="([^"]*)"/)?.[1];
    this.codes.push(token.content.replace(/\n$/, ""));
    // HTML is CodeBlock's default language, so the prop is omitted for it, as hand-written pages did.
    const langAttr = lang && lang !== "html" ? ` lang="${lang}"` : "";
    const fileAttr = filename ? ` filename="${escapeText(filename)}"` : "";
    return `<CodeBlock :code="__code[${this.codes.length - 1}]"${langAttr}${fileAttr} />`;
  }

  div(node: Node): string {
    const { classes, id, attrs } = parseDivInfo(node.token.info);
    const [kind] = classes;
    const body = node.children;
    switch (kind) {
      case "entry": {
        const dl = body.find((c) => c.token.type === "dl_open");
        const rows = [];
        for (let i = 0; dl && i < dl.children.length; i += 2) {
          rows.push({ label: plainText(dl.children[i].children[0]?.token), value: this.inline(dl.children[i + 1].children[0]?.children[0]?.token, "html") });
        }
        const props: Record<string, unknown> = { name: escapeText(attrs.name ?? "").replace(/&quot;/g, '"').replace(/&#123;/g, "{") };
        if (attrs.role) props.role = attrs.role;
        props.rows = rows;
        return `<Entry v-bind="${this.bindData(props)}" />`;
      }
      case "record": {
        const items = [];
        for (let i = 0; i < body.length; i += 3) {
          items.push({
            label: plainText(body[i].children[0]?.token),
            claim: this.inline(body[i + 1].children[0]?.token, "html"),
            body: this.inline(body[i + 2].children[0]?.token, "html"),
          });
        }
        return `<div class="record">\n<RecordItem v-for="(r, i) in ${this.bindData(items)}" :key="i" v-bind="r" />\n</div>`;
      }
      case "targets":
        return `<div class="targets">${(body[0]?.children ?? []).reduce<string[]>((acc, c, i, all) => {
          if (c.token.type === "dt_open") acc.push(`<div class="t"><b>${this.inline(c.children[0]?.token, "template")}</b><span>${this.inline(all[i + 1].children[0]?.children[0]?.token, "template")}</span></div>`);
          return acc;
        }, []).join("\n")}</div>`;
      case "flow":
        return `<div class="flow">${(body[0]?.children ?? []).map((li, i) => {
          const inline = li.children[0]?.children[0]?.token;
          const extra = li.children[0]?.token.attrGet("class");
          const cls = ["node", ...(extra ? [extra] : [])].join(" ");
          return `${i ? '<span class="arw">→</span>\n' : ""}<span class="${cls}">${this.inline(inline, "template")}</span>`;
        }).join("")}</div>`;
      default: {
        const cls = classes.length ? ` class="${classes.join(" ")}"` : "";
        const idAttr = id ? ` id="${escapeText(id)}"` : "";
        const inner = body[0]?.token.tag === "h2" ? this.blocks(body) : this.children(body);
        return `<div${idAttr}${cls}>\n${inner}\n</div>`;
      }
    }
  }

  fixCard(node: Node, idx: number) {
    const body = node.children;
    const title = plainText(body.find((c) => c.token.tag === "h3")?.children[0]?.token);
    const sub = plainText(body.find((c) => c.token.type === "paragraph_open")?.children[0]?.token);
    const columns = body.flatMap((c, i) => (c.token.tag === "h5" ? [{ label: plainText(c.children[0]?.token), list: body[i + 1] }] : []));
    const items = (list: Node) => list.children.map((li) => this.inline(li.children[0]?.children[0]?.token, "html"));
    return { idx, title, sub, broken: items(columns[0].list), fixed: items(columns[1].list), fixedLabel: columns[1].label };
  }

  // -------------------------------------------------------------------------------------------
  // Page layouts: the chapter header and pager, or the proposal's front-page masthead.

  chapter(meta: ChapterMeta, nodes: Node[]): string {
    const [h1, ...rest] = nodes;
    if (h1?.token.tag !== "h1") throw new Error("A chapter's body starts with its # title.");
    const header: Record<string, string> = {};
    if (meta.eyebrow) header.eyebrow = meta.eyebrow;
    header.title = plainText(h1.children[0]?.token);
    if (rest[0]?.token.type === "paragraph_open" && !rest[0].token.attrs) header.lede = this.inline(rest.shift()!.children[0]?.token, "html");
    if (meta.status) header.status = this.inlineSource(meta.status);
    const parts = [`<PageHeader v-bind="${this.bindData(header)}" />`, this.blocks(rest)];
    if (meta.pager !== false) parts.push("<Pager />");
    parts.push("<SiteFooter />");
    return parts.join("\n");
  }

  proposal(meta: ChapterMeta, nodes: Node[]): string {
    const sotdAt = nodes.findIndex((n) => n.token.tag === "h2" && /\bsotd\b/.test(n.token.attrGet("class") ?? ""));
    const head = nodes.slice(0, sotdAt);
    const nextSection = nodes.findIndex((n, i) => i > sotdAt && n.token.tag === "h2");
    const sotd = nodes.slice(sotdAt + 1, nextSection);
    const h1 = head.find((n) => n.token.tag === "h1");
    const tagline = head.find((n) => n.token.type === "paragraph_open");
    const entry = head.find((n) => n.token.type === "bullet_list_open");
    const dl = head.find((n) => n.token.type === "dl_open");
    const links = (entry?.children ?? []).map((li) => this.inline(li.children[0]?.children[0]?.token, "template"));
    const rows: string[] = [];
    for (let i = 0; dl && i < dl.children.length; i += 2) {
      rows.push(`<div><dt>${this.inline(dl.children[i].children[0]?.token, "template")}</dt><dd>${this.inline(dl.children[i + 1].children[0]?.children[0]?.token, "template")}</dd></div>`);
    }
    const masthead = [
      `<header class="masthead">`,
      `<div class="eyebrow">${escapeText(meta.eyebrow ?? "")}</div>`,
      `<h1>${this.inline(h1?.children[0]?.token, "template")}</h1>`,
      `<p class="tagline">${this.inline(tagline?.children[0]?.token, "template")}</p>`,
      `<div class="stamp"><span class="dot" /> ${this.inlineSource(meta.stamp ?? "", "template")}</div>`,
      `<nav class="entry-points" aria-label="Start reading ${escapeText(meta.title)}">\n${links.join("\n")}\n</nav>`,
      `<dl class="meta">\n<div><dt>Latest snapshot</dt><dd><a :href="latestHtmlNextSnapshot.href">{{ latestHtmlNextSnapshot.label }}</a></dd></div>\n${rows.join("\n")}\n</dl>`,
      `<div class="sotd">\n<h2>${this.inline(nodes[sotdAt].children[0]?.token, "template")}</h2>\n${this.children(sotd)}\n</div>`,
      `</header>`,
    ].join("\n");
    return [masthead, "<Search />", this.blocks(nodes.slice(nextSection)), "<SiteFooter />"].join("\n");
  }

  inlineSource(source: string, mode: Mode = "html"): string {
    const tokens = this.md.parseInline(source, {});
    return this.inline(tokens[0], mode);
  }
}

export interface CompileOptions {
  // The proposal front page's masthead reads the latest snapshot and carries a scoped stylesheet;
  // both belong to the publishing site, which supplies them.
  proposalImports?: string;
  proposalStyle?: string;
}

export function compileChapter(source: string, options: CompileOptions = {}): { meta: ChapterMeta; sfc: string } {
  const { meta, body } = readFrontmatter(source);
  const compiler = new Compiler();
  const nodes = toTree(compiler.md.parse(body, {}));
  resolveAttrs(nodes);
  const proposal = meta.layout === "proposal";
  const template = proposal ? compiler.proposal(meta, nodes) : compiler.chapter(meta, nodes);
  // Code samples contain </script> and </template>; escape "<" so they cannot end an SFC block.
  const literal = (value: unknown) => JSON.stringify(value).replace(/</g, "\\u003c");
  // Nuxt resolves components automatically only in .vue files, so a compiled chapter imports the
  // ones it uses from the registry; #components keeps CodeBlock a server island.
  const used = [...new Set([...template.matchAll(/<([A-Z][A-Za-z]+)/g)].map((m) => m[1]))].sort();
  const script = [
    `import { ${used.join(", ")} } from "#components";`,
    proposal ? options.proposalImports ?? "const latestHtmlNextSnapshot = { href: \"\", label: \"\" };" : "",
    `const __code = ${literal(compiler.codes)};`,
    `const __data = ${literal(compiler.data)};`,
  ].filter(Boolean).join("\n");
  const style = proposal && options.proposalStyle ? `\n<style scoped>\n${readFileSync(options.proposalStyle, "utf8")}</style>\n` : "";
  return { meta, sfc: `<script setup>\n${script}\n</script>\n\n<template>\n${template}\n</template>\n${style}` };
}
