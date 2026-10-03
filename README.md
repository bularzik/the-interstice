# The Interstice: A Liminal Descent

A Backrooms-inspired liminal-horror adventure for **D&D 5e (2024 rules)**, 4–5 characters of levels 5–8, 2–3 sessions.
For **Foundry VTT v14** with **dnd5e 5.x/6.x**.

**Requires:** [Monk's Active Tile Triggers](https://github.com/ironmonk108/monks-active-tiles) 14.01+. Foundry offers to install it automatically.

## Install

In Foundry's Setup screen: **Add-on Modules → Install Module**, paste this into **Manifest URL**, and click **Install**:

```
https://github.com/OWNER/the-interstice/releases/latest/download/module.json
```

Then, in your dnd5e world:
1. **Game Settings → Manage Modules**: enable *The Interstice* and *Monk's Active Tile Triggers*.
2. **Compendium sidebar → The Interstice (Adventure)**: open it and click **Import Adventure**.
3. Read the journal **00. The Interstice: Adventure Overview**, including its **Automation** page.

## Contents
- 4 scenes (The Waiting Halls, The Undercroft, The Celebration, The Threshold) with walls, doors, lights, ambient sound and keyed map notes
- 29 Monk's Active Tile Triggers tiles: looping rooms, cross-scene transitions, lights-out events, a Guest Pass check, a Misfile trap, auto-opening handouts and hidden GM control buttons
- 10 actors (7 monsters including a CR 9 legendary boss, 3 NPCs) with token art
- 15 journal entries: overview, custom rules (Fraying, Wayfinding, havens), five chapters, cast, 7 handouts
- 2 roll tables and 2 playlists (4 ambient loops, 4 stingers)

All maps, art and audio are original and procedurally generated.

## Testing in Foundry

After importing, open the browser console (F12) as GM, paste the contents of [`tools/smoke-test.js`](tools/smoke-test.js), and press Enter. It checks every scene, actor, tile action and asset, then live-fires four tiles with a temporary token and cleans up. Results appear in the console and as a whispered chat message.

## Development

```
npm install
npm run build:packs   # compile src/packs/*.json into LevelDB packs/
npm run validate      # check every link, tile reference and asset path
npm run package       # build + validate + dist/module.zip
```

`src/packs/` holds the compendium content as JSON. `packs/` is generated and not committed. The Python scripts in `tools/` regenerate the maps, audio, art and JSON from scratch (`pip install numpy scipy pillow`, plus `ffmpeg`), run from the repo root: `python3 tools/audio.py`, `tools/maps.py`, `tools/tokens.py`, `tools/tile_art.py`, then `tools/build.py`.

## Releasing

Every push to `main` runs **Validate**. To publish a new version, create a GitHub release with a tag like `v1.2.0`. The **Release Module** workflow compiles the packs, validates them, stamps `module.json` with the version and URLs, and attaches `module.json` and `module.zip` to the release. Foundry picks up the update through the manifest URL above.
