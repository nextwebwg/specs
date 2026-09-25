// Turns an issue form's "Chapter" answer into a `chapter: …` label and its "Type" answer into a type
// label. Declarative HTML Components chapters map to their file names, so issues and pull requests
// share labels; HTML Forms parts map to their section titles. An answer only selects from labels
// defined here; it is never executed.
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

export const typeLabels = new Map([
  ["Editorial (wording, a typo, a link, or an example)", "editorial"],
  ["Substantive (what the proposal requires, allows, or defines)", "substantive"],
  ["Question", "question"],
]);

const answer = (body, field) => body?.match(new RegExp(`^### ${field}\\s*\\n+([^\\n]+)`, "m"))?.[1]?.trim();

export function labelsFor(body) {
  return [chapterLabels().get(answer(body, "Chapter")), typeLabels.get(answer(body, "Type"))].filter(Boolean);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, "utf8"));
  // One comma-separated list, the form `gh issue edit --add-label` takes; no label contains a comma.
  console.log(labelsFor(event.issue?.body).join(","));
}
