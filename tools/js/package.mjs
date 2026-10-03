// Stamps module.json with release URLs and zips the module for distribution.
// Env: REPO (owner/name), TAG (e.g. v1.2.0). Falls back to module.json values for local runs.
import { readFileSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { execSync } from "node:child_process";
const m = JSON.parse(readFileSync("module.json", "utf8"));
const repo = process.env.REPO, tag = process.env.TAG;
if (repo && tag) {
  m.version = tag.replace(/^v/, "");
  m.url = `https://github.com/${repo}`;
  m.manifest = `https://github.com/${repo}/releases/latest/download/module.json`;
  m.download = `https://github.com/${repo}/releases/download/${tag}/module.zip`;
}
rmSync("dist", { recursive: true, force: true }); mkdirSync("dist");
writeFileSync("module.json", JSON.stringify(m, null, 2) + "\n");
writeFileSync("dist/module.json", JSON.stringify(m, null, 2) + "\n");
execSync("zip -rq dist/module.zip module.json README.md packs maps audio tokens tiles", { stdio: "inherit" });
console.log(`Packaged ${m.id} ${m.version} -> dist/module.zip`);
