# HTML Next specifications

The specifications for the [HTML Next](https://nextwebwg.org/) proposals, published by the Next
Web Working Group. Each proposal is an **Unofficial Editor's Draft at Stage 0**: a document for
discussion, not a W3C or WHATWG deliverable.

| Proposal | Source | Published |
| --- | --- | --- |
| Declarative HTML Components | [`html-next/`](./html-next) — one specification in chapters | [nextwebwg.org/html-next](https://nextwebwg.org/html-next/) |
| HTML Forms | [`html-forms/`](./html-forms) | [nextwebwg.org/html-forms](https://nextwebwg.org/html-forms/) |

The site renders these files as they are on `main`; dated snapshots are frozen copies. The
reference implementation, a browser runtime and compiler, lives in
[`nextwebwg/html-next`](https://github.com/nextwebwg/html-next).

## Give feedback

- **About a draft's text** — a question, an ambiguity, a problem, or a suggestion:
  [open an issue](https://github.com/nextwebwg/specs/issues/new/choose) with the form for that
  proposal. Choosing a chapter labels the issue, so the people working on that chapter see it.
- **About something new** — an idea for a proposal, or a direction no draft covers yet:
  [start a discussion](https://github.com/nextwebwg/specs/discussions).
- **About the tooling** — a bug in the runtime, compiler, unplugin, or converter:
  [file it in `html-next`](https://github.com/nextwebwg/html-next/issues).

## Edit a chapter

Chapters are Markdown with a few established conventions for the things a specification needs:
footnote-style references, callouts, definition-list element entries, and a handful of named
blocks. [CONTRIBUTING.md](./CONTRIBUTING.md) documents every one of them, and
[WRITING.md](./WRITING.md) is the writing standard the drafts follow.

Check your change the way the site will build it:

```sh
corepack pnpm install
corepack pnpm verify:pr
```

`verify:pr` compiles every chapter with the site's own compiler ([`tools/compile.ts`](./tools/compile.ts))
and runs the content tests that guard decisions the drafts have made.

## License

The specification text (the chapters and the documentation) is licensed under
[CC BY 4.0](./LICENSES/CC-BY-4.0.txt); the code that builds and checks it (`tools/`, the workflow
scripts) under the [MIT License](./LICENSES/MIT.txt). [`REUSE.toml`](./REUSE.toml) records which
applies to each file, following the [REUSE](https://reuse.software) convention.
