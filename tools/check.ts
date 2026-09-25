// Compiles every chapter exactly as the site does, then runs Vue's SFC compiler over the result,
// so a chapter that would fail to publish fails here first.
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { compileScript, compileTemplate, parse } from "@vue/compiler-sfc";
import { compileChapter } from "./compile.ts";

const PROPOSALS = ["html-next", "html-forms"];
let failures = 0;
let chapters = 0;
for (const dir of PROPOSALS) {
  for (const name of readdirSync(dir).filter((f) => f.endsWith(".md")).sort()) {
    const file = join(dir, name);
    chapters++;
    try {
      const { sfc } = compileChapter(readFileSync(file, "utf8"));
      const { descriptor, errors } = parse(sfc, { filename: `${file}.vue` });
      const problems = [...errors.map(String)];
      if (!descriptor.template) problems.push("no template produced");
      else {
        compileScript(descriptor, { id: file });
        problems.push(...compileTemplate({ source: descriptor.template.content, filename: file, id: file }).errors.map(String));
      }
      if (problems.length) throw new Error(problems.join("\n  "));
    } catch (error) {
      failures++;
      console.error(`✗ ${file}\n  ${(error as Error).message}`);
    }
  }
}
console.log(`${chapters - failures}/${chapters} chapters compile`);
process.exit(failures ? 1 : 0);
