// Round-trips the compiled packs and checks the module for broken references.
import { extractPack } from "@foundryvtt/foundryvtt-cli";
import { readFileSync, readdirSync, existsSync, rmSync, mkdirSync } from "node:fs";
const errors = [], warn = (m) => errors.push(m);
const manifest = JSON.parse(readFileSync("module.json", "utf8"));
const tmp = ".validate"; rmSync(tmp, { recursive: true, force: true }); mkdirSync(tmp);

for (const p of manifest.packs) {
  if (!existsSync(p.path)) { warn(`Pack ${p.name} not compiled at ${p.path}`); continue; }
  await extractPack(p.path, `${tmp}/${p.name}`, { log: false });
}
const adv = JSON.parse(readFileSync(`${tmp}/the-interstice/${readdirSync(`${tmp}/the-interstice`)[0]}`, "utf8"));
const ids = {
  Actor: new Set(adv.actors.map(a => a._id)), Scene: new Set(adv.scenes.map(s => s._id)),
  RollTable: new Set(adv.tables.map(t => t._id)), JournalEntry: new Set(adv.journal.map(j => j._id))
};
const embedded = new Set(), files = new Set();
for (const s of adv.scenes) {
  for (const [coll, key] of [["tiles", "Tile"], ["lights", "AmbientLight"], ["walls", "Wall"]])
    for (const d of s[coll]) embedded.add(`Scene.${s._id}.${key}.${d._id}`);
  for (const n of s.notes) {
    const j = adv.journal.find(j => j._id === n.entryId);
    if (!j || !j.pages.some(p => p._id === n.pageId)) warn(`Scene ${s.name}: map note "${n.text}" points at a missing page`);
  }
}
const text = JSON.stringify(adv);
for (const [, type, id] of text.matchAll(/@UUID\[(\w+)\.(\w+)\]/g))
  if (!ids[type]?.has(id)) warn(`Broken @UUID link ${type}.${id}`);
// Monk's Active Tile Triggers references
let tiles = 0, actions = 0;
for (const s of adv.scenes) for (const t of s.tiles) {
  const f = t.flags?.["monks-active-tiles"]; if (!f) continue; tiles++;
  for (const a of f.actions) {
    actions++;
    for (const ref of JSON.stringify(a.data ?? {}).match(/(Scene\.\w+\.\w+\.\w+|JournalEntry\.\w+|RollTable\.\w+)/g) ?? []) {
      const [type, id] = ref.split(".");
      if (!(embedded.has(ref) || ids[type]?.has(id))) warn(`Tile "${f.name}" (${s.name}) action ${a.action} references missing ${ref}`);
    }
  }
}
// Every module-relative asset path must exist
for (const [, path] of text.matchAll(/modules\/the-interstice\/([^"'\s)]+)/g)) files.add(path);
for (const p of readdirSync(`${tmp}/interstice-bestiary`)) {
  const t = readFileSync(`${tmp}/interstice-bestiary/${p}`, "utf8");
  for (const [, path] of t.matchAll(/modules\/the-interstice\/([^"'\s)]+)/g)) files.add(path);
}
for (const f of files) if (!existsSync(f)) warn(`Missing asset ${f}`);
// IDs must be 16-char alphanumeric and unique
const allIds = [...text.matchAll(/"_id":"([^"]+)"/g)].map(m => m[1]);
if (allIds.some(i => !/^[A-Za-z0-9]{16}$/.test(i))) warn("Invalid document id found");
if (new Set(allIds).size !== allIds.length) warn("Duplicate document ids found");
rmSync(tmp, { recursive: true, force: true });

console.log(`Checked ${adv.scenes.length} scenes, ${adv.actors.length} actors, ${adv.journal.length} journals, ${tiles} active tiles (${actions} actions), ${files.size} asset paths.`);
if (errors.length) { console.error(errors.map(e => "  ✗ " + e).join("\n")); process.exit(1); }
console.log("  ✓ All references resolve.");
