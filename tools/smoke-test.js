/**
 * The Interstice — in-Foundry smoke test.
 *
 * Run as a GM in a dnd5e world with "The Interstice" and "Monk's Active Tile Triggers" enabled:
 * open the browser console (F12), paste this whole file, and press Enter.
 *
 * It imports the adventure if needed, checks every scene, actor, tile action and asset,
 * then live-fires four tiles with a temporary token and cleans up after itself.
 */
(async () => {
  const results = [];
  const pass = (test, detail = "") => results.push({ result: "✅ PASS", test, detail });
  const fail = (test, detail = "") => results.push({ result: "❌ FAIL", test, detail });
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const check = (ok, test, detail) => ok ? pass(test, detail) : fail(test, detail);

  try {
    // ---------- 1. Environment ----------
    check(game.user.isGM, "Running as GM");
    check(game.system.id === "dnd5e", "System is dnd5e", `${game.system.id} ${game.system.version}`);
    check(game.modules.get("the-interstice")?.active, "The Interstice enabled", game.modules.get("the-interstice")?.version);
    check(game.modules.get("monks-active-tiles")?.active, "Monk's Active Tile Triggers enabled", game.modules.get("monks-active-tiles")?.version);
    const MATT = game.MonksActiveTiles;
    if (!MATT) throw new Error("Monk's Active Tile Triggers is not active; enable it and reload.");

    // ---------- 2. Import ----------
    const pack = game.packs.get("the-interstice.the-interstice");
    check(!!pack, "Adventure compendium present");
    const [adv] = await pack.getDocuments();
    check(!!adv, "Adventure document loads", adv?.name);
    const needImport = adv.scenes.some(s => !game.scenes.get(s._id));
    if (needImport) {
      if (typeof adv.import === "function") {
        await adv.import({ dialog: false });
        pass("Adventure imported via API");
      } else {
        adv.sheet.render(true);
        ui.notifications.warn("Click Import Adventure in the window that opened, then run this test again.");
        return;
      }
    } else pass("Adventure already imported");

    // ---------- 3. Documents ----------
    for (const src of adv.scenes) check(!!game.scenes.get(src._id), `Scene imported: ${src.name}`);
    for (const src of adv.actors) {
      const a = game.actors.get(src._id);
      if (!a) { fail(`Actor imported: ${src.name}`); continue; }
      const ac = a.system.attributes.ac.value, hp = a.system.attributes.hp.max;
      const noActs = a.items.filter(i => ["weapon"].includes(i.type) && !(i.system.activities?.size > 0)).map(i => i.name);
      check(Number.isFinite(ac) && hp > 0 && !noActs.length, `Actor prepares: ${a.name}`, `AC ${ac}, HP ${hp}, CR ${a.system.details.cr}, ${a.items.size} items${noActs.length ? `, no activities: ${noActs}` : ""}`);
    }
    for (const src of adv.journal) check(!!game.journal.get(src._id), `Journal imported: ${src.name}`);
    for (const src of adv.tables) check(!!game.tables.get(src._id), `Table imported: ${src.name}`);
    for (const src of adv.playlists) check(!!game.playlists.get(src._id), `Playlist imported: ${src.name}`);
    const host = game.actors.find(a => a.name === "Celebrant Host");
    check(!!host?.items.getName("Guest Pass"), "Celebrant Host carries the Guest Pass");

    // ---------- 4. Tiles & references ----------
    const scenes = adv.scenes.map(s => game.scenes.get(s._id)).filter(Boolean);
    let tileCount = 0;
    for (const scene of scenes) {
      for (const tile of scene.tiles) {
        const f = tile.flags["monks-active-tiles"]; if (!f) continue; tileCount++;
        const bad = [];
        for (const a of f.actions) {
          if (!MATT.triggerActions[a.action]) bad.push(`unknown action "${a.action}"`);
          const refs = JSON.stringify(a.data ?? {}).match(/(Scene\.\w+\.\w+\.\w+|JournalEntry\.\w+|RollTable\.\w+)/g) ?? [];
          for (const r of refs) if (!fromUuidSync(r)) bad.push(`missing ${r}`);
        }
        check(!bad.length, `Tile OK: ${scene.name} / ${f.name}`, bad.join("; ") || `${f.actions.length} actions, trigger ${f.trigger}`);
      }
    }
    check(tileCount === 29, "All 29 MATT tiles present", `${tileCount} found`);

    // ---------- 5. Assets ----------
    const paths = new Set();
    for (const s of scenes) {
      paths.add(s.background?.src ?? s.initialLevel?.background?.src);
      s.tiles.forEach(t => t.texture.src && paths.add(t.texture.src));
      s.sounds.forEach(x => paths.add(x.path));
    }
    game.actors.filter(a => adv.actors.some(s => s._id === a.id)).forEach(a => paths.add(a.img));
    adv.playlists.forEach(p => p.sounds.forEach(s => paths.add(s.path)));
    paths.delete(undefined); paths.delete(null);
    const missing = [];
    for (const p of paths) { const r = await fetch(p, { method: "HEAD" }); if (!r.ok) missing.push(p); }
    check(!missing.length, "All map, token, tile and audio files load", missing.join(", ") || `${paths.size} files`);
    for (const s of scenes) check(!!(s.background?.src ?? s.initialLevel?.background?.src), `Scene has background: ${s.name}`);

    // ---------- 6. Live tile tests ----------
    const wren = game.actors.getName("Wren Halloway");
    const byName = (scene, name) => scene.tiles.find(t => t.flags["monks-active-tiles"]?.name === name);
    const inside = (tok, tile) => {
      const cx = tok.x + tok.width * tok.parent.grid.size / 2, cy = tok.y + tok.height * tok.parent.grid.size / 2;
      return cx >= tile.x && cx <= tile.x + tile.width && cy >= tile.y && cy <= tile.y + tile.height;
    };
    const tempToken = async (scene, x, y) => {
      const td = await wren.getTokenDocument({ x, y, name: "Smoke Test", actorLink: false, hidden: true });
      const [tok] = await scene.createEmbeddedDocuments("Token", [td.toObject()]);
      return tok;
    };
    const [halls, under, party] = [scenes[0], scenes[1], scenes[2]];

    // 6a. A3: the room gets longer (same-scene teleport)
    {
      const loop = byName(halls, "A3: The Room Gets Longer (50%)"), dest = byName(halls, "A3: Loop destination");
      const tok = await tempToken(halls, loop.x, loop.y);
      await loop.trigger({ tokens: [tok], method: "enter" }); await wait(1500);
      const moved = halls.tokens.get(tok.id);
      check(moved && inside(moved, dest), "Live: A3 loop teleports token back", moved ? `now at ${moved.x},${moved.y}` : "token gone");
      await moved?.delete();
    }
    // 6b. A4: Quiet Light reveals and arms the stairwell door
    {
      const quiet = byName(halls, "A4: The Quiet Light (stop here)"), door = byName(halls, "A5: Stairwell Door → Undercroft");
      const before = { qa: quiet.flags["monks-active-tiles"].active, dh: door.hidden, da: door.flags["monks-active-tiles"].active };
      const tok = await tempToken(halls, quiet.x, quiet.y);
      await quiet.trigger({ tokens: [tok], method: "stop" }); await wait(1500);
      const d2 = halls.tiles.get(door.id);
      check(!d2.hidden && d2.flags["monks-active-tiles"].active, "Live: Quiet Light reveals stairwell door");
      await tok.delete();
      // 6c. A5: cross-scene teleport to the Undercroft
      const tok2 = await tempToken(halls, door.x, door.y);
      await halls.tiles.get(door.id).trigger({ tokens: [tok2], method: "enter" }); await wait(2500);
      const arrived = under.tokens.find(t => t.name === "Smoke Test");
      check(!!arrived && inside(arrived, byName(under, "B1: Arrival from the Stairwell")), "Live: stairwell moves token to the Undercroft (B1)");
      for (const t of [...halls.tokens.filter(t => t.name === "Smoke Test"), ...under.tokens.filter(t => t.name === "Smoke Test")]) await t.delete();
      // restore
      await quiet.update({ "flags.monks-active-tiles.active": before.qa });
      await halls.tiles.get(door.id).update({ hidden: before.dh, "flags.monks-active-tiles.active": before.da });
    }
    // 6d. C5: without a Guest Pass, the exit door loops you back
    {
      const door = byName(party, "C5: Exit Door (needs Guest Pass)"), dest = byName(party, "C5: Loop destination");
      const tok = await tempToken(party, door.x, door.y);
      await door.trigger({ tokens: [tok], method: "enter" }); await wait(1500);
      const moved = party.tokens.get(tok.id);
      check(moved && inside(moved, dest), "Live: C5 door loops a pass-less token");
      await moved?.delete();
    }
    if (canvas.scene?.id !== game.scenes.viewed?.id) await game.scenes.viewed?.view();
  } catch (err) {
    fail("Test run aborted", err.message); console.error(err);
  }

  console.table(results);
  const failed = results.filter(r => r.result.includes("FAIL")).length;
  const msg = `The Interstice smoke test: ${results.length - failed}/${results.length} passed.`;
  failed ? ui.notifications.error(msg + " See console for details.") : ui.notifications.info(msg);
  ChatMessage.create({ whisper: [game.user.id], content: `<h3>${msg}</h3><ul>${results.filter(r => r.result.includes("FAIL")).map(r => `<li>${r.test}: ${r.detail}</li>`).join("") || "<li>No failures.</li>"}</ul>` });
  return results;
})();
