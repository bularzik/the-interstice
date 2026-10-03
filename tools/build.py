import json, os, shutil, subprocess
from actors import build_monsters, build_npcs, uid, MOD
import journal, matt
from actors import _item, SRC as ASRC

ROOT = "."
SRC = "src/packs"
shutil.rmtree(SRC, ignore_errors=True)
for d in ("the-interstice", "interstice-bestiary"): os.makedirs(f"{SRC}/{d}", exist_ok=True)
maps = json.load(open("tools/maps.json"))

monsters, npcs = build_monsters(), build_npcs()
allactors = {**monsters, **npcs}
_h = monsters["host"]
_h.items.append(_item(_h.id, uid(_h.id, "guest-pass"), "Guest Pass", "loot", f"{MOD}/tiles/guest-pass.webp", {
    "description": {"value": "<p>A brass pass on a pink ribbon, engraved GUEST. Whoever carries it may leave the Celebration through the Exit Corridor (C5). The exit door tile checks for an item with exactly this name.</p>", "chat": ""},
    "quantity": 1, "weight": {"value": 0, "units": "lb"}, "price": {"value": 0, "denomination": "gp"}, "rarity": "",
    "identified": True, "type": {"value": "", "subtype": ""}, "source": ASRC, "identifier": "guest-pass", "properties": []}, 900000))

# ---------- ids ----------
SCENE_KEYS = {"waiting": "The Waiting Halls", "undercroft": "The Undercroft", "celebration": "The Celebration", "threshold": "The Threshold"}
scene_ids = {k: uid("scene", k) for k in SCENE_KEYS}
table_ids = {"wandering": uid("table", "wandering"), "wrongness": uid("table", "wrongness")}
F = {t: uid("folder", t) for t in ("JournalEntry", "Actor", "Actor-npc", "Scene", "Playlist", "RollTable")}

def L(kind, key, name=None):
    if kind == "actor":
        a = allactors[key]; return f"@UUID[Actor.{a.id}]{{{name or a.doc['name']}}}"
    if kind == "scene": return f"@UUID[Scene.{scene_ids[key]}]{{{name or SCENE_KEYS[key]}}}"
    if kind == "table": return f"@UUID[RollTable.{table_ids[key]}]{{{name or ('the Wandering table' if key == 'wandering' else 'the Wrongness table')}}}"
    raise KeyError(kind)

# ---------- journal ----------
journals, page_index, handout_ids = [], {}, {}
F["Handouts"] = uid("folder", "Handouts")
_entries = journal.build(L)
_entries[0][1].append(("Automation (Monk's Active Tile Triggers)", matt.GM_GUIDE, 2))
_split = []
for ename, pages in _entries:
    if ename == "08. Handouts":
        for p in pages: _split.append((p[0], [p], "Handouts"))
    else:
        _split.append((ename, [(p[0], p[1] + (f'<aside class="notable"><h4>Automation</h4><p>{matt.PAGE_NOTES[p[0]]}</p></aside>' if p[0] in matt.PAGE_NOTES else ""), *p[2:]) for p in pages], "JournalEntry"))
for ei, (ename, pages, fkey) in enumerate(_split):
    jid = uid("journal", ename); pdocs = []
    for pi, page in enumerate(pages):
        pname, html = page[0], page[1]; level = page[2] if len(page) > 2 else 1
        pid = uid(jid, pname); page_index[pname] = (jid, pid)
        pdocs.append({"_id": pid, "name": pname, "type": "text", "title": {"show": True, "level": level},
                      "text": {"format": 1, "content": html}, "sort": (pi + 1) * 100000,
                      "ownership": {"default": -1}, "flags": {}, "image": {}, "video": {}, "src": None, "system": {}})
    if fkey == "Handouts": handout_ids[ename] = f"JournalEntry.{jid}"
    journals.append({"_id": jid, "name": ename, "pages": pdocs, "folder": F[fkey], "sort": (ei + 1) * 100000,
                     "ownership": {"default": 0}, "flags": {}, "categories": []})

# ---------- actors ----------
def actor_doc(a, folder):
    d = json.loads(json.dumps(a.doc)); d["folder"] = folder
    for it in d["items"]: it.pop("_key", None)
    d.pop("_key", None); return d
adv_actors = [actor_doc(a, F["Actor"]) for a in monsters.values()] + [actor_doc(a, F["Actor-npc"]) for a in npcs.values()]

# ---------- roll tables ----------
def table(key, name, formula, desc, rows, img):
    tid = table_ids[key]; res = []
    for i, (lo, hi, text) in enumerate(rows):
        res.append({"_id": uid(tid, str(i)), "type": "text", "name": "", "description": text, "img": "icons/svg/d20-black.svg",
                    "weight": hi - lo + 1, "range": [lo, hi], "drawn": False, "flags": {}})
    return {"_id": tid, "name": name, "img": img, "description": desc, "results": res, "formula": formula,
            "replacement": True, "displayRoll": True, "folder": F["RollTable"], "sort": 0, "ownership": {"default": 0}, "flags": {}}

wandering = table("wandering", "Wandering in the Interstice", "1d8", "<p>Roll when a Wayfinding check fails, during rests, or whenever the party lingers.</p>", [
    (1, 1, "<strong>Footsteps.</strong> Distant footsteps that match the party's own, a half-step behind. Play the Footsteps stinger. Each character makes a DC 12 Wisdom save or gains 1 Fraying."),
    (2, 2, "<strong>The Hound.</strong> One Hollow Hound (two if anyone Dashed in the last minute) stalks the party, attacking the rearmost character."),
    (3, 3, "<strong>Moths.</strong> A Lumen Moth Swarm drifts in, drawn to the brightest light the party carries."),
    (4, 4, "<strong>Edited.</strong> The party enters a room it has already been in. Its chalk marks are still there, rewritten in a stranger's handwriting, pointing the other way."),
    (5, 5, "<strong>A Lost Soul.</strong> A flickering person asks politely what year it is. If told, they smile, fade away, and the character who told them loses 1 Fraying."),
    (6, 6, "<strong>Sweetwater.</strong> A single waxed-paper cup of Sweetwater, on the floor in the middle of the room, still cold."),
    (7, 7, "<strong>Lights Out.</strong> Play the Lights Die stinger. All lights within 60 feet go out for 1 minute. In the Undercroft, the Smiling Dark comes; elsewhere, something breathes in the dark and is gone when the lights return."),
    (8, 8, "<strong>A Door That Shouldn't Be.</strong> Roll 1d4: (1) a stairwell, which grants one Wayfinding success; (2) a closet holding a child's crayon drawing of the party, exactly as they look now; (3) a perfect replica of one character's childhood bedroom (DC 14 Wisdom save or +1 Fraying; leaving something behind instead removes 1 Fraying); (4) the Waystation, if the party has found it before."),
], "icons/svg/door-exit.svg")

wrongness = table("wrongness", "Wrongness", "1d12", "<p>Small, unsettling events. Roll for atmosphere, or for any character at Fraying 4 or higher at the start of a scene (only they experience it).</p>", [
    (1, 1, "Your reflection in a puddle or polished surface moves a fraction of a second late."),
    (2, 2, "From the next room, someone calls your name in your own voice."),
    (3, 3, "The hum stops. Everyone looks up. It starts again, slightly lower."),
    (4, 4, "One of your companions is standing somewhere they weren't a moment ago, and doesn't seem to have moved."),
    (5, 5, "You count the party and get one more than there should be. Count again; it's right."),
    (6, 6, "A chair in the corner is facing you. It wasn't before."),
    (7, 7, "Your shadow is pointing toward a light, not away from it."),
    (8, 8, "You remember this room clearly. You've never been here."),
    (9, 9, "The carpet underfoot is warm, as if someone was lying here a moment ago."),
    (10, 10, "A phone rings somewhere far away, a sound none of you has a word for. It rings eleven times."),
    (11, 11, "You notice the wallpaper pattern is made of tiny repeating doors."),
    (12, 12, "Your hands smell of almonds."),
], "icons/svg/eye.svg")
tables = [wandering, wrongness]

# ---------- playlists ----------
def snd(name, file, repeat, vol, desc=""):
    return {"_id": uid("sound", file), "name": name, "path": f"{MOD}/audio/{file}.ogg", "repeat": repeat, "volume": vol,
            "description": desc, "fade": 1000 if repeat else None, "playing": False, "pausedTime": None, "sort": 0, "flags": {}}
playlists = [
    {"_id": uid("playlist", "amb"), "name": "Interstice: Ambience", "description": "Seamless 64-second loops for each level.",
     "mode": -1, "fade": 1000, "sounds": [
        snd("The Waiting Halls: Fluorescent Hum", "ambience-waiting-halls-hum", True, .45),
        snd("The Undercroft: Drips & Pipes", "ambience-undercroft-drip", True, .5),
        snd("The Celebration: Through the Walls", "ambience-celebration-distant", True, .45),
        snd("The Threshold: Drone & Clock", "ambience-threshold-drone", True, .5)],
     "folder": F["Playlist"], "sort": 100000, "ownership": {"default": 0}, "flags": {}, "playing": False},
    {"_id": uid("playlist", "sting"), "name": "Interstice: Stingers", "description": "One-shot cues.", "mode": -1, "fade": None,
     "sounds": [snd("Footsteps (Wandering 1)", "sting-footsteps", False, .7), snd("Hollow Howl", "sting-hollow-howl", False, .7),
                snd("The Lights Die", "sting-lights-die", False, .7), snd("Party Chime (Celebration)", "sting-party-chime", False, .6)],
     "folder": F["Playlist"], "sort": 200000, "ownership": {"default": 0}, "flags": {}, "playing": False},
]

# ---------- scenes ----------
NOTE_PAGES = {"A1": "A1. Arrival", "A2": "A2. The Chalked Room", "A3": "A3. The Long Room", "A4": "A4. The Quiet Light", "A5": "A5. The Stairwell",
              "B1": "B1. The Landing", "B2": "B2. The Counting Rooms", "B3": "B3. The Waystation", "B4": "B4. The Great Drain", "B5": "B5. The Flooded Gallery",
              "C1": "C1. The Welcome Hall", "C2": "C2. The Coat Room", "C3": "C3. The Grand Hall", "C4": "C4. The Gift Room", "C5": "C5. The Exit Corridor",
              "D1": "D1. The Queue", "D2": "D2. The Clerks' Floor", "D3": "D3. The Filing Alcoves", "D4": "D4. The Custodian's Desk", "D5": "D5. The Last Door & Endings"}
AMB = {"waiting": "ambience-waiting-halls-hum", "undercroft": "ambience-undercroft-drip", "celebration": "ambience-celebration-distant", "threshold": "ambience-threshold-drone"}
LIGHT_SCALE = {"waiting": 1.4, "undercroft": 1.0, "celebration": 1.0, "threshold": 1.2}

scenes = []
for i, (key, name) in enumerate(SCENE_KEYS.items()):
    m = maps[key]; sid = scene_ids[key]
    walls = [{"_id": uid(sid, "w", str(j)), **w, "dir": 0, "threshold": {"light": None, "sight": None, "sound": None, "attenuation": False}, "flags": {}}
             for j, w in enumerate(m["walls"])]
    lights = []
    for j, l in enumerate(m["lights"]):
        s = LIGHT_SCALE[key]
        lights.append({"_id": uid(sid, "l", str(j)), "x": int(l["x"]), "y": int(l["y"]), "rotation": 0, "walls": True, "vision": False, "hidden": False,
                       "config": {"dim": round(l["dim"] * s), "bright": round(l["bright"] * s), "color": l["color"], "alpha": l["alpha"], "angle": 360,
                                  "coloration": 1, "luminosity": .5, "attenuation": .5, "saturation": 0, "contrast": 0, "shadows": 0,
                                  "animation": {"type": l["anim"], "speed": 3, "intensity": 3, "reverse": False}, "darkness": {"min": 0, "max": 1}},
                       "flags": {}})
    notes = []
    for code, (x, y) in m["notes"].items():
        jid, pid = page_index[NOTE_PAGES[code]]
        notes.append({"_id": uid(sid, "n", code), "entryId": jid, "pageId": pid, "x": int(x), "y": int(y),
                      "texture": {"src": "icons/svg/book.svg", "tint": "#ffe9a8"}, "iconSize": 48, "text": NOTE_PAGES[code].split(" & ")[0],
                      "fontSize": 28, "textAnchor": 1, "textColor": "#ffffff", "global": False, "flags": {}})
    sounds = [{"_id": uid(sid, "s"), "path": f"{MOD}/audio/{AMB[key]}.ogg", "x": m["w"] // 2, "y": m["h"] // 2, "radius": 400,
               "easing": False, "walls": False, "repeat": True, "volume": .45, "hidden": False, "flags": {},
               "darkness": {"min": 0, "max": 1}, "effects": {"base": {"type": None, "intensity": 5}, "muffled": {"type": None, "intensity": 5}}}]
    sx, sy = m["start"]
    scenes.append({"_id": sid, "name": name, "navigation": True, "navOrder": i, "navName": "", "active": False,
                   "background": {"src": f"{MOD}/maps/{m['file']}"}, "foreground": None,
                   "thumb": f"{MOD}/maps/thumb-{m['file']}", "width": m["w"], "height": m["h"], "padding": 0,
                   "initial": {"x": int(sx), "y": int(sy), "scale": .7}, "backgroundColor": "#0b0a07",
                   "grid": {"type": 1, "size": 100, "style": "solidLines", "thickness": 1, "color": "#000000", "alpha": .12, "distance": 5, "units": "ft"},
                   "tokenVision": True, "fog": {"exploration": True, "reset": None, "overlay": None, "colors": {"explored": None, "unexplored": None}},
                   "environment": {"darknessLevel": m["darkness"], "darknessLock": False, "globalLight": {"enabled": False}, "cycle": True},
                   "drawings": [], "tokens": [], "lights": lights, "notes": notes, "sounds": sounds, "regions": [], "tiles": [], "walls": walls,
                   "playlist": None, "playlistSound": None, "journal": page_index[NOTE_PAGES[list(m["notes"])[0]]][0], "journalEntryPage": None,
                   "weather": "", "folder": F["Scene"], "sort": (i + 1) * 100000, "ownership": {"default": 0}, "flags": {}})

sk = list(SCENE_KEYS)
ctx = {"scene_ids": scene_ids, "rects": {k: maps[k]["rects"] for k in sk}, "notes": {k: maps[k]["notes"] for k in sk},
       "handouts": handout_ids, "table_uuid": {k: f"RollTable.{v}" for k, v in table_ids.items()},
       "lights": {"waiting": [f"Scene.{scene_ids['waiting']}.AmbientLight.{l['_id']}" for l in scenes[0]["lights"]],
                  "undercroft_nostove": [f"Scene.{scene_ids['undercroft']}.AmbientLight.{l['_id']}" for l in scenes[1]["lights"][1:]]},
       "last_door": f"Scene.{scene_ids['threshold']}.Wall.{scenes[3]['walls'][-1]['_id']}"}
assert scenes[3]["walls"][-1]["ds"] == 2
tiles = matt.build_tiles(ctx)
for i, k in enumerate(sk): scenes[i]["tiles"] = tiles[k]

folders = [
    {"_id": F["JournalEntry"], "name": "The Interstice", "type": "JournalEntry", "color": "#7a6a2a", "sorting": "a", "folder": None, "sort": 0, "flags": {}},
    {"_id": F["Handouts"], "name": "Handouts", "type": "JournalEntry", "color": "#a08a3a", "sorting": "a", "folder": F["JournalEntry"], "sort": 0, "flags": {}},
    {"_id": F["Actor"], "name": "Interstice: Monsters", "type": "Actor", "color": "#7a6a2a", "sorting": "a", "folder": None, "sort": 0, "flags": {}},
    {"_id": F["Actor-npc"], "name": "Interstice: People", "type": "Actor", "color": "#5a6a4a", "sorting": "a", "folder": None, "sort": 0, "flags": {}},
    {"_id": F["Scene"], "name": "The Interstice", "type": "Scene", "color": "#7a6a2a", "sorting": "m", "folder": None, "sort": 0, "flags": {}},
    {"_id": F["Playlist"], "name": "The Interstice", "type": "Playlist", "color": "#7a6a2a", "sorting": "m", "folder": None, "sort": 0, "flags": {}},
    {"_id": F["RollTable"], "name": "The Interstice", "type": "RollTable", "color": "#7a6a2a", "sorting": "a", "folder": None, "sort": 0, "flags": {}},
]

adv_id = uid("adventure", "interstice")
adventure = {"_id": adv_id, "name": "The Interstice", "img": f"{MOD}/maps/cover.webp",
             "caption": "A liminal-horror adventure for 5th–8th level characters",
             "description": "<p>People are vanishing from the corridors of Calder's Reach. Behind a door that shouldn't exist lie endless humming halls, flooded cellars, a party that never ends, and a tired clerk who holds the only way home.</p><p><strong>Contents:</strong> 4 scenes with walls, lights, notes, ambient sound and Monk's Active Tile Triggers automation; 10 actors; 15 journal entries; 2 roll tables; 2 playlists.</p><p>Start with the journal <em>00. The Interstice: Adventure Overview</em>.</p>",
             "actors": adv_actors, "combats": [], "items": [], "scenes": scenes, "journal": journals, "tables": tables,
             "macros": [], "cards": [], "playlists": playlists, "folders": folders, "sort": 0, "flags": {},
             "_key": f"!adventures!{adv_id}"}
json.dump(adventure, open(f"{SRC}/the-interstice/the-interstice.json", "w"), indent=1)

# Standalone bestiary pack (keys required for embedded items)
for k, a in allactors.items():
    d = json.loads(json.dumps(a.doc)); d["folder"] = None
    json.dump(d, open(f"{SRC}/interstice-bestiary/{k}.json", "w"), indent=1)

# ---------- manifest ----------
manifest = {
    "id": "the-interstice", "title": "The Interstice: A Liminal Descent",
    "description": "<p>A Backrooms-inspired liminal-horror adventure for D&amp;D 5e (2024 rules), levels 5–8. Includes four scenes, ten actors, journals, handouts, roll tables and original ambient audio.</p>",
    "version": "1.1.0",
    "url": "https://github.com/bularzik/the-interstice",
    "manifest": "https://github.com/bularzik/the-interstice/releases/latest/download/module.json",
    "download": "https://github.com/bularzik/the-interstice/releases/download/v1.1.0/module.zip",
    "authors": [{"name": "Generated with Claude"}],
    "compatibility": {"minimum": "14", "verified": "14"},
    "relationships": {
        "systems": [{"id": "dnd5e", "type": "system", "compatibility": {"minimum": "5.0.0"}}],
        "requires": [{"id": "monks-active-tiles", "type": "module",
                      "manifest": "https://github.com/ironmonk108/monks-active-tiles/releases/latest/download/module.json",
                      "compatibility": {"minimum": "14.01"}, "reason": "Scene automation: teleports, looping rooms, lights-out events, scene transitions and the Guest Pass check."}]},
    "packs": [
        {"name": "the-interstice", "label": "The Interstice (Adventure)", "path": "packs/the-interstice", "type": "Adventure",
         "system": "dnd5e", "ownership": {"PLAYER": "NONE", "ASSISTANT": "OWNER"}},
        {"name": "interstice-bestiary", "label": "The Interstice: Bestiary", "path": "packs/interstice-bestiary", "type": "Actor",
         "system": "dnd5e", "ownership": {"PLAYER": "NONE", "ASSISTANT": "OWNER"}}],
    "packFolders": [{"name": "The Interstice", "sorting": "m", "color": "#7a6a2a", "packs": ["the-interstice", "interstice-bestiary"]}],
    "languages": [], "esmodules": [], "styles": [],
}
json.dump(manifest, open(f"{ROOT}/module.json", "w"), indent=2)
print("sources written:", len(scenes), "scenes,", len(journals), "journals,", sum(len(j['pages']) for j in journals), "pages,", len(adv_actors), "actors")
