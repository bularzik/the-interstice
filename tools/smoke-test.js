/**
 * The Interstice — in-Foundry smoke test (Foundry v14, dnd5e, Monk's Active Tile Triggers).
 *
 * Run as GM in a dnd5e world with both modules enabled: open the browser console (F12),
 * paste this whole file, and press Enter. It takes about a minute. Results are printed as a
 * table and whispered to you in chat; they are also left on window.intersticeSmokeTest.
 *
 * It imports the adventure, checks every document, tile action and asset, then plays through
 * the automation with a temporary player and character (tiles ignore non-player tokens).
 * Afterwards it deletes the temporary user, character and tokens and re-imports the
 * adventure so every tile, door and handout is back in its starting state.
 */
window.intersticeSmokeTest = (async () => {
  const results = [];
  const check = (ok, test, detail = "") => results.push({ result: ok ? "✅ PASS" : "❌ FAIL", test, detail });
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const byName = (scene, name) => scene.tiles.find(t => t.flags["monks-active-tiles"]?.name === name);
  const center = (tok) => ({ x: tok.x + tok.width * tok.parent.grid.size / 2, y: tok.y + tok.height * tok.parent.grid.size / 2 });
  const inside = (tok, tile) => { const c = center(tok); return c.x >= tile.x && c.x <= tile.x + tile.width && c.y >= tile.y && c.y <= tile.y + tile.height; };
  const findToken = (name) => game.scenes.contents.flatMap(s => s.tokens.filter(t => t.name === name));
  let user, pc, adv;

  try {
    // ---------- 1. Environment ----------
    check(game.user.isGM, "Running as GM");
    check(game.system.id === "dnd5e", "System is dnd5e", `${game.system.id} ${game.system.version}`);
    check(game.modules.get("the-interstice")?.active, "The Interstice enabled", game.modules.get("the-interstice")?.version);
    check(game.modules.get("monks-active-tiles")?.active, "Monk's Active Tile Triggers enabled", game.modules.get("monks-active-tiles")?.version);
    const MATT = game.MonksActiveTiles;
    if (!MATT) throw new Error("Monk's Active Tile Triggers is not active; enable it and reload.");

    // ---------- 2. Import ----------
    [adv] = await game.packs.get("the-interstice.the-interstice").getDocuments();
    await adv.import({ dialog: false });
    {
      const scenes = adv.scenes.map(s => game.scenes.get(s._id));
      check(scenes.every(Boolean), "Scenes imported", `${scenes.filter(Boolean).length}/${adv.scenes.size}`);
      check(adv.actors.every(a => game.actors.get(a._id)), "Actors imported", `${adv.actors.size}`);
      check(adv.journal.every(j => game.journal.get(j._id)), "Journals imported", `${adv.journal.size}`);
      check(adv.tables.every(t => game.tables.get(t._id)), "Roll tables imported", `${adv.tables.size}`);
      check(adv.playlists.every(p => game.playlists.get(p._id)), "Playlists imported", `${adv.playlists.size}`);
    }

    // ---------- 3. Actors ----------
    for (const src of adv.actors) {
      const a = game.actors.get(src._id);
      const noActs = a.items.filter(i => i.type === "weapon" && !(i.system.activities?.size > 0)).map(i => i.name);
      check(Number.isFinite(a.system.attributes.ac.value) && a.system.attributes.hp.max > 0 && !noActs.length,
        `Actor prepares: ${a.name}`, `AC ${a.system.attributes.ac.value}, HP ${a.system.attributes.hp.max}, CR ${a.system.details.cr}`);
    }
    check(!!game.actors.getName("Celebrant Host")?.items.getName("Guest Pass"), "Celebrant Host carries the Guest Pass");

    // ---------- 4. Tiles, references, assets ----------
    const scenes = adv.scenes.map(s => game.scenes.get(s._id));
    let tiles = 0; const bad = [], paths = new Set();
    for (const s of scenes) {
      paths.add(s.initialLevel?.background?.src ?? s.background?.src);
      s.sounds.forEach(x => paths.add(x.path));
      for (const t of s.tiles) {
        if (t.texture.src) paths.add(t.texture.src);
        const f = t.flags["monks-active-tiles"]; if (!f) continue; tiles++;
        for (const a of f.actions) {
          if (!MATT.triggerActions[a.action]) bad.push(`${f.name}: unknown action ${a.action}`);
          for (const r of JSON.stringify(a.data ?? {}).match(/(Scene\.\w+\.\w+\.\w+|JournalEntry\.\w+|RollTable\.\w+)/g) ?? [])
            if (!fromUuidSync(r)) bad.push(`${f.name}: missing ${r}`);
        }
      }
    }
    check(tiles === 29, "All 29 MATT tiles present", `${tiles}`);
    check(!bad.length, "Every tile action is valid and every reference resolves", bad.join("; "));
    adv.actors.forEach(a => { const d = game.actors.get(a._id); paths.add(d.img); paths.add(d.prototypeToken.texture.src); });
    adv.playlists.forEach(p => p.sounds.forEach(s => paths.add(s.path)));
    paths.delete(null); paths.delete(undefined);
    const missing = [];
    for (const p of paths) if (!(await fetch(p, { method: "HEAD" })).ok) missing.push(p);
    check(!missing.length, "All map, token, tile and audio files load", missing.join(", ") || `${paths.size} files`);

    // ---------- 5. Live play-through with a temporary player ----------
    const [halls, under, party, thr] = scenes;
    user = await User.create({ name: "Smoke Test Player", role: CONST.USER_ROLES.PLAYER });
    pc = await Actor.create({ name: "Smoke Test PC", type: "character", ownership: { default: 0, [user.id]: 3 } });
    const place = async (scene, x, y) => {
      for (const t of findToken("Smoke Test PC")) await t.delete();
      const td = await pc.getTokenDocument({ x, y, name: "Smoke Test PC", actorLink: true });
      const [tok] = await scene.createEmbeddedDocuments("Token", [td.toObject()]);
      await wait(800); return tok;
    };
    // Movement must be animated: MATT only detects y-only moves when they animate, like a real drag.
    const walk = async (tok, x, y, ms = 3500) => { await tok.move({ x, y }); await wait(ms); };

    // A3: the room gets longer (50% chance per entry)
    {
      const loop = byName(halls, "A3: The Room Gets Longer (50%)"), dest = byName(halls, "A3: Loop destination");
      const tok = await place(halls, loop.x - 200, loop.y + 200); let looped = false;
      for (let i = 0; i < 8 && !looped; i++) {
        await walk(tok, loop.x - 200, loop.y + 200, 1500);
        await walk(tok, loop.x, loop.y + 200, 2500);
        looped = inside(halls.tokens.get(tok.id), dest);
      }
      check(looped, "Live A3: the Long Room sends the token back to its start");
    }
    // A4: stopping on the Quiet Light reveals the stairwell door
    {
      const quiet = byName(halls, "A4: The Quiet Light (stop here)"), door = byName(halls, "A5: Stairwell Door → Undercroft");
      const tok = await place(halls, quiet.x + 200, quiet.y - 100);      // pillar sits in the light's top-left square
      await walk(tok, quiet.x + 100, quiet.y + 100, 4000);
      const d = halls.tiles.get(door.id);
      check(!d.hidden && d.flags["monks-active-tiles"].active, "Live A4: the Quiet Light reveals the stairwell door");
      // A5: walking onto the door moves the token to the Undercroft
      const tok2 = await place(halls, door.x, door.y + 300);
      await walk(tok2, door.x, door.y, 6000);
      const arrived = under.tokens.getName("Smoke Test PC");
      check(!!arrived && !halls.tokens.getName("Smoke Test PC"), "Live A5: the stairwell moves the token to the Undercroft", arrived ? `${arrived.x},${arrived.y}` : "");
    }
    // B4: GM control opens the drain; walking in moves the token to the Celebration
    {
      const drain = byName(under, "B4: Great Drain → Celebration"), ctl = byName(under, "GM: Open the Great Drain");
      await ctl.trigger({ tokens: [], method: "dblclick", pt: { x: ctl.x + 50, y: ctl.y + 50 } }); await wait(2000);
      const d = under.tiles.get(drain.id);
      check(!d.hidden && d.flags["monks-active-tiles"].active, "Live B4: GM Open Drain reveals and arms the drain");
      const tok = await place(under, drain.x - 100, drain.y);
      await walk(tok, drain.x, drain.y, 6000);
      check(!!party.tokens.getName("Smoke Test PC"), "Live B4: the drain moves the token to the Celebration");
    }
    // C5: no Guest Pass loops back; with the pass the token reaches the Threshold
    {
      const door = byName(party, "C5: Exit Door (needs Guest Pass)");
      const tok = await place(party, door.x - 100, door.y);
      await walk(tok, door.x, door.y, 5000);
      const t = party.tokens.get(tok.id);
      check(!!t && t.y < door.y - 200 && !thr.tokens.getName("Smoke Test PC"), "Live C5: without the Guest Pass, the exit door loops the token back", t ? `${t.x},${t.y}` : "token gone");
      await pc.createEmbeddedDocuments("Item", [game.actors.getName("Celebrant Host").items.getName("Guest Pass").toObject()]);
      const tok2 = await place(party, door.x - 100, door.y);
      await walk(tok2, door.x, door.y, 6000);
      check(!!thr.tokens.getName("Smoke Test PC"), "Live C5: with the Guest Pass, the exit door moves the token to the Threshold");
    }
    // D4/D5: Out of Order trap, GM Now Serving, GM Approve Form, through the Last Door
    {
      const ooo = byName(thr, "D4: Out of Order → Misfile"), alcove = byName(thr, "D3: Misfile destination");
      const tok = await place(thr, 1400, 700);
      await walk(tok, 1400, 500, 5000);
      check(inside(thr.tokens.get(tok.id), alcove), "Live D4: approaching the dais uncalled Misfiles the token");
      const serve = byName(thr, "GM: Now Serving (disable Out of Order)");
      await serve.trigger({ tokens: [], method: "dblclick", pt: { x: serve.x + 50, y: serve.y + 50 } }); await wait(2000);
      check(!thr.tiles.get(ooo.id).flags["monks-active-tiles"].active, "Live D4: GM Now Serving disarms the trap");
      const approve = byName(thr, "GM: Approve Form (open the Last Door)");
      await approve.trigger({ tokens: [], method: "dblclick", pt: { x: approve.x + 50, y: approve.y + 50 } }); await wait(2000);
      const door = thr.walls.find(w => w.door === CONST.WALL_DOOR_TYPES.DOOR && w.c[1] === 0 && w.c[3] === 0);
      check(door?.ds === CONST.WALL_DOOR_STATES.OPEN, "Live D5: GM Approve Form opens the Last Door");
      const tok2 = await place(thr, 1300, 400);
      await walk(tok2, 1400, 100, 4000);
      check(thr.tokens.get(tok2.id)?.hidden === true, "Live D5: stepping through the Last Door removes the token from play");
    }
  } catch (err) {
    check(false, "Test run aborted", err.message); console.error(err);
  } finally {
    // ---------- Cleanup ----------
    for (const t of findToken("Smoke Test PC")) await t.delete();
    await pc?.delete(); await user?.delete();
    if (adv) await adv.import({ dialog: false });           // restore tiles, doors and lights to their starting state
    for (const j of game.journal) if (j.folder?.name === "Handouts" && j.ownership.default !== 0) await j.update({ "ownership.default": 0 });
  }

  console.table(results);
  const failed = results.filter(r => r.result.includes("FAIL"));
  const msg = `The Interstice smoke test: ${results.length - failed.length}/${results.length} passed.`;
  failed.length ? ui.notifications.error(msg + " See console for details.") : ui.notifications.info(msg);
  ChatMessage.create({ whisper: [game.user.id], content: `<h3>${msg}</h3><ul>${failed.map(r => `<li>${r.test}: ${r.detail}</li>`).join("") || "<li>No failures.</li>"}</ul>` });
  return results;
})();
