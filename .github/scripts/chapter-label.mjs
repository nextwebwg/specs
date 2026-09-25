// Turns an issue form's "Chapter" answer into a `chapter: …` label. Declarative HTML Components
// chapters map to their file names, so issues and pull requests share labels; HTML Forms parts map
// to their section titles. The answer only selects from labels derived here; it is never executed.
import { readdirSync, readFileSync } from "node:fs";

export function chapterLabels() {
  const labels = new Map();
  for (const file of readdirSync("html-next").filter((f) => f.endsWith(".md"))) {
    const title = readFileSync(`html-next/${file}`, "utf8").match(/^title: (.+)$/m)?.[1];
    if (title) labels.set(title, `chapter: ${file === "index.md" ? "front-page" : file.replace(/\.md$/, "")}`);
  }
  for (const part of ["Expanded request methods", "QUERY forms", "Composable submission scopes", "Constraint validation on any element"]) {
    labels.set(part, `chapter: ${part.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`);
  }
  return labels;
}

export function labelFor(body) {
  const answer = body?.match(/^### Chapter\s*\n+([^\n]+)/m)?.[1]?.trim();
  return answer ? chapterLabels().get(answer) : undefined;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, "utf8"));
  const label = labelFor(event.issue?.body);
  if (label) console.log(label);
}
