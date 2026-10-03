// Compiles the JSON sources in src/packs/<name> into Foundry LevelDB packs in packs/<name>.
import { compilePack } from "@foundryvtt/foundryvtt-cli";
import { rmSync, readdirSync } from "node:fs";
for (const name of readdirSync("src/packs")) {
  rmSync(`packs/${name}`, { recursive: true, force: true });
  await compilePack(`src/packs/${name}`, `packs/${name}`, { log: true });
}
