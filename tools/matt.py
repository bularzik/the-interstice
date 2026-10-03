"""Monk's Active Tile Triggers automation for The Interstice."""
from actors import uid, MOD

MATT = "monks-active-tiles"
AUD = f"{MOD}/audio"
TOKEN = {"id": "token", "name": "Triggering Token"}
PLAYERS = {"id": "players", "name": "Players"}

class TB:
    """Tile builder for one scene."""
    def __init__(self, sid):
        self.sid = sid; self.tiles = []; self.n = 0

    def tid(self, key): return uid(self.sid, "tile", key)
    def tuuid(self, key): return f"Scene.{self.sid}.Tile.{self.tid(key)}"

    def tile(self, key, rect, actions=(), trigger="enter", img=None, hidden=False, active=True,
             restriction="player", controlled="all", pertoken=False, chance=100, name=None):
        x, y, w, h = rect
        acts = []
        for i, (a, data) in enumerate(actions):
            d = {"id": uid(self.tid(key), "a", str(i)), "action": a}
            if data is not None: d["data"] = data
            acts.append(d)
        self.n += 1
        self.tiles.append({
            "_id": self.tid(key), "x": int(x), "y": int(y), "width": int(w), "height": int(h),
            "texture": {"src": img, "anchorX": .5, "anchorY": .5, "scaleX": 1, "scaleY": 1, "tint": "#ffffff",
                        "alphaThreshold": .75, "fit": "fill"},
            "elevation": 0, "sort": self.n, "rotation": 0, "alpha": 1, "hidden": hidden, "locked": False,
            "occlusion": {"mode": 0, "alpha": 0}, "restrictions": {"light": False, "weather": False},
            "flags": {MATT: {"name": name or key, "active": active, "trigger": trigger, "restriction": restriction,
                             "controlled": controlled, "pertoken": pertoken, "minrequired": 0, "chance": chance,
                             "vision": True, "fileindex": 0, "files": [], "actions": acts}}})
        return self

# ---------- action helpers ----------
def scroll(text, entity=TOKEN, to="trigger", dur=5):
    return ("scrollingtext", {"text": text, "entity": entity, "for": to, "duration": dur, "anchor": 0, "direction": 2})
def chat(text, to="gm", flavor="", speaker=None):
    return ("chatmessage", {"flavor": flavor, "text": text, "entity": speaker or "", "incharacter": False,
                            "chatbubble": "false", "showto": to, "language": ""})
def sound(file, to="everyone", vol="0.8"):
    return ("playsound", {"audiofile": f"{AUD}/{file}.ogg", "audiofor": to, "volume": vol, "loop": False, "fade": 0.25,
                          "scenerestrict": False, "prevent": False, "delay": False, "playlist": True})
def teleport(dest_uuid, entity=TOKEN, position="random", cross=False):
    return ("teleport", {"entity": entity, "location": {"id": dest_uuid, "name": "Destination"}, "position": position,
                         "remotesnap": True, "animatepan": cross, "triggerremote": False, "deletesource": cross,
                         "preservesettings": True, "avoidtokens": True, "colour": ""})
def activate(uuids, state, collection="tiles"):
    return ("activate", {"entity": {"id": ",".join(uuids) if isinstance(uuids, list) else uuids, "name": "Targets"},
                         "collection": collection, "activate": state})
def deactivate_self(): return ("activate", {"entity": {"id": "tile", "name": "This Tile"}, "collection": "tiles", "activate": "deactivate"})
def showhide(uuid, state, collection="tiles"):
    return ("showhide", {"entity": {"id": uuid, "name": "Target"}, "collection": collection, "hidden": state, "fade": 0})
def delay(sec): return ("delay", {"delay": str(sec)})
def journal(uuid, to="everyone"):
    return ("openjournal", {"entity": {"id": uuid, "name": "Handout"}, "page": "", "subsection": "", "showto": to,
                            "asimage": False, "permission": "OBSERVER", "enhanced": False})
def rolltable(uuid, mode="gmroll"):
    return ("rolltable", {"rolltableid": uuid, "quantity": "1", "rollmode": mode, "chatmessage": True, "reset": True})

def build_tiles(ctx):
    """ctx: dict with scene ids, rects, light ids, wall ids, journal ids, table ids. Returns {scene_key: [tiles]}."""
    out = {}
    S, R = ctx["scene_ids"], ctx["rects"]
    W, U, C, T = (TB(S[k]) for k in ("waiting", "undercroft", "celebration", "threshold"))
    H = ctx["handouts"]

    # ======================= THE WAITING HALLS =======================
    x, y, w, h = R["waiting"]["A3"]
    W.tile("a1-arrival", R["waiting"]["A1"], [scroll("The hum is everywhere.")], pertoken=True, name="A1: The Hum")
    W.tile("a2-chalk", R["waiting"]["A2"], [journal(H["Handout 2: The Chalk Walls"], to="trigger"),
                                           rolltable(ctx["table_uuid"]["wrongness"])],
           pertoken=True, name="A2: Chalk Walls (handout + Wrongness)")
    W.tile("a3-hounds", R["waiting"]["A3"], [
        sound("sting-hollow-howl"),
        chat("<strong>A3. The Long Room.</strong> Two Hollow Hounds watch from beyond the flickering panels. They attack anyone who runs, attacks, or fails a DC 13 group Stealth check."),
        deactivate_self()], name="A3: Howl (once)")
    if w >= h: strip, back = [x + w - 100, y, 100, h], [x + 100, y, 100, h]
    else: strip, back = [x, y + h - 100, w, 100], [x, y + 100, w, 100]
    W.tile("a3-loop-dest", back, active=False, name="A3: Loop destination")
    W.tile("a3-loop", strip, [teleport(W.tuuid("a3-loop-dest"), position="relative"),
                              scroll("Wasn't this room shorter?")], chance=50, name="A3: The Room Gets Longer (50%)")
    W.tile("a5-door", [3300, 1800, 100, 100], [
        sound("sting-footsteps", to="token"),
        teleport(U.tuuid("b1-dest"), cross=True)],
        img=f"{MOD}/tiles/stairwell-door.webp", hidden=True, active=False, name="A5: Stairwell Door → Undercroft")
    W.tile("a4-quiet", [1400, 1300, 200, 200], [
        scroll("Silence. And below your feet, faintly: dripping water."),
        chat("<strong>A4. The Quiet Light</strong> found: the party gains 2 Wayfinding successes. The Stairwell door (A5) has been revealed."),
        showhide(W.tuuid("a5-door"), "show"), activate(W.tuuid("a5-door"), "activate"),
        deactivate_self()], trigger="stop", name="A4: The Quiet Light (stop here)")
    W.tile("gm-lights", [0, 2500, 100, 100], [
        sound("sting-lights-die"), activate(ctx["lights"]["waiting"], "deactivate", "lights"),
        delay(45), activate(ctx["lights"]["waiting"], "activate", "lights")],
        trigger="dblclick", img=f"{MOD}/tiles/gm-lights-out.webp", hidden=True, restriction="all", controlled="gm",
        name="GM: Lights Out (45s)")
    out["waiting"] = W.tiles

    # ======================= THE UNDERCROFT =======================
    U.tile("b1-dest", [100, 100, 200, 400], active=False, name="B1: Arrival from the Stairwell")
    U.tile("b2-lights", R["undercroft"]["B2"], [
        sound("sting-lights-die"), activate(ctx["lights"]["undercroft_nostove"], "deactivate", "lights"),
        chat("<strong>B2. The lights die.</strong> The Smiling Dark attacks the character furthest from the group. Lights return in 60 seconds."),
        delay(60), activate(ctx["lights"]["undercroft_nostove"], "activate", "lights"),
        deactivate_self()], chance=25, name="B2: The Lights Die (25%, once)")
    U.tile("b3-haven", R["undercroft"]["B3"], [scroll("Warmth. The stove is lit.")], pertoken=True, name="B3: Haven")
    bx, by = ctx["notes"]["undercroft"]["B4"]
    U.tile("b4-drain", [bx - 50, by - 50, 100, 100], [
        sound("sting-party-chime", to="token", vol="0.6"),
        teleport(C.tuuid("c1-dest"), cross=True)],
        img=f"{MOD}/tiles/great-drain-open.webp", hidden=True, active=False, name="B4: Great Drain → Celebration")
    U.tile("b5-satchel", [3300, 2000, 100, 100], [
        chat("A leather satchel with brass clasps, untouched for thirty-one years. Inside: a blank form, a pair of spectacles, and a cracked hand-mirror.", to="everyone", flavor="B5. Tobin's Satchel"),
        journal(H["Handout 6: Form 0-Δ"]), showhide("tile", "hide"), deactivate_self()],
        trigger="click", img=f"{MOD}/tiles/tobins-satchel.webp", name="B5: Tobin's Satchel (click)")
    U.tile("gm-drain", [100, 2500, 100, 100], [
        showhide(U.tuuid("b4-drain"), "show"), activate(U.tuuid("b4-drain"), "activate"),
        chat("The great grate grinds open. Warm air rises, carrying the smell of frosting and a faint, out-of-tune waltz.", to="everyone", flavor="B4. The Great Drain")],
        trigger="dblclick", img=f"{MOD}/tiles/gm-open-drain.webp", hidden=True, restriction="all", controlled="gm",
        name="GM: Open the Great Drain")
    U.tile("gm-lights", [0, 2500, 100, 100], [
        sound("sting-lights-die"), activate(ctx["lights"]["undercroft_nostove"], "deactivate", "lights"),
        delay(45), activate(ctx["lights"]["undercroft_nostove"], "activate", "lights")],
        trigger="dblclick", img=f"{MOD}/tiles/gm-lights-out.webp", hidden=True, restriction="all", controlled="gm",
        name="GM: Lights Out (45s)")
    out["undercroft"] = U.tiles

    # ======================= THE CELEBRATION =======================
    C.tile("c1-dest", [100, 100, 300, 100], active=False, name="C1: Arrival from the Drain")
    C.tile("c1-surprise", R["celebration"]["C1"], [
        sound("sting-party-chime"),
        scroll("SURPRISE!", entity={"id": "tile", "name": "This Tile"}, to="everyone", dur=6),
        chat("<strong>SURPRISE!</strong> A dozen cheerful voices, a burst of light and music, and soft yellow faces with huge inked smiles crowding close. The banner reads HAPPY DEPARTURE!", to="everyone", flavor="C1. The Welcome Hall"),
        deactivate_self()], trigger="movement", name="C1: Surprise! (first movement)")
    C.tile("c2-coats", R["celebration"]["C2"], [scroll("Your coat is here. You're still wearing it.")], pertoken=True, name="C2: Your Coat")
    C.tile("c3-host", R["celebration"]["C3"], [
        chat("<strong>C3. The Grand Hall.</strong> The Celebrant Host and four Celebrants. The Host carries the <em>Guest Pass</em> (a loot item on its sheet). A character must hold it for the C5 exit door to work."),
        deactivate_self()], name="C3: GM Reminder (once)")
    C.tile("c4-gifts", R["celebration"]["C4"], [scroll("There's a present here with your name on it.")], pertoken=True, name="C4: Gifts")
    C.tile("c5-loop-dest", [2800, 1600, 200, 100], active=False, name="C5: Loop destination")
    C.tile("c5-door", [2800, 2200, 100, 100], [
        ("inventory", {"entity": PLAYERS, "item": "Guest Pass", "count": "> 0", "quantity": ">= 1"}),
        ("exists", {"entity": "", "collection": "tokens", "count": "> 0", "none": "NoPass"}),
        sound("sting-party-chime", to="token", vol="0.5"),
        teleport(T.tuuid("d1-dest"), cross=True),
        ("anchor", {"tag": "NoPass", "stop": True}),
        teleport(C.tuuid("c5-loop-dest")),
        scroll("THANK YOU FOR COMING! COME AGAIN!")],
        img=f"{MOD}/tiles/exit-door.webp", name="C5: Exit Door (needs Guest Pass)")
    out["celebration"] = C.tiles

    # ======================= THE THRESHOLD =======================
    T.tile("d1-dest", [1200, 2100, 600, 200], active=False, name="D1: Arrival from the Celebration")
    T.tile("d3-alcove", R["threshold"]["D3L"], active=False, name="D3: Misfile destination")
    T.tile("d1-ticket", [1000, 2200, 100, 100], [
        chat("{{value.tokens.0.name}} takes a ticket. It reads <strong>[[1d999999]]</strong>. Far ahead, a tired voice calls a different number.", to="everyone", flavor="D1. The Queue", speaker=TOKEN)],
        trigger="click", img=f"{MOD}/tiles/ticket-dispenser.webp", name="D1: Take a Number (click)")
    T.tile("d4-out-of-order", [1000, 0, 1000, 600], [
        scroll("OUT OF ORDER", to="everyone"),
        chat("<strong>Out of order!</strong> {{value.tokens.0.name}} approached the dais uncalled. The Custodian uses <em>Misfile</em> and initiative begins (D4)."),
        teleport(T.tuuid("d3-alcove"))], name="D4: Out of Order → Misfile")
    T.tile("d5-through", [1300, 100, 400, 100], [
        scroll("Floor polish. Ink. Home.", to="everyone"),
        chat("{{value.tokens.0.name}} steps through the Last Door into the dusty Old Archive of the Halvard Assay House.", to="everyone", flavor="D5. The Last Door"),
        showhide("token", "hide", "tokens")], active=False, name="D5: Through the Last Door")
    T.tile("gm-serving", [0, 2300, 100, 100], [
        activate(T.tuuid("d4-out-of-order"), "deactivate"),
        chat("“Now serving…” The tired voice calls a number, and this time it's yours. You may approach the desk.", to="everyone", flavor="D4. The Custodian's Desk")],
        trigger="dblclick", img=f"{MOD}/tiles/gm-now-serving.webp", hidden=True, restriction="all", controlled="gm",
        name="GM: Now Serving (disable Out of Order)")
    T.tile("gm-approve", [100, 2300, 100, 100], [
        ("changedoor", {"entity": {"id": ctx["last_door"], "name": "The Last Door"}, "type": "nothing", "state": "open",
                        "movement": "nothing", "light": "nothing", "sight": "nothing", "sound": "nothing"}),
        activate(T.tuuid("d4-out-of-order"), "deactivate"), activate(T.tuuid("d5-through"), "activate"),
        chat("<strong>APPROVED.</strong> The stamp comes down. The golden doors swing open, and the smell of floor polish drifts through.", to="everyone", flavor="D5. The Last Door")],
        trigger="dblclick", img=f"{MOD}/tiles/gm-approve.webp", hidden=True, restriction="all", controlled="gm",
        name="GM: Approve Form (open the Last Door)")
    out["threshold"] = T.tiles
    return out

GM_GUIDE = """<h2>Automation with Monk's Active Tile Triggers</h2>
<p>This module requires <strong>Monk's Active Tile Triggers</strong> (MATT). Every scene has tiles that react when player tokens walk, stop, or click. Monster tokens never set them off. Each tile is named in its MATT settings, so you can find and tweak any of them from the Tiles layer.</p>
<h3>GM Controls</h3>
<p>Some scenes have hidden <strong>GM control buttons</strong> in the bottom-left corner. Players can't see them. Switch to the <strong>Tiles</strong> layer to see them, then double-click a button from the Tokens layer to fire it. You can also open any tile's config and use MATT's trigger button.</p>
<table><thead><tr><th>Scene</th><th>Control</th><th>What it does</th></tr></thead><tbody>
<tr><td>Waiting Halls, Undercroft</td><td>Lights Out</td><td>Plays the Lights Die cue, turns the scene's lights off for 45 seconds, then back on. (In the Undercroft the stove stays lit.)</td></tr>
<tr><td>Undercroft</td><td>Open Drain</td><td>Reveals and arms the Great Drain (B4) once the party lifts the grate or says the magic words.</td></tr>
<tr><td>Threshold</td><td>Now Serving</td><td>Disables the Out of Order trap around the dais so a called character can approach the Custodian.</td></tr>
<tr><td>Threshold</td><td>Approve Form</td><td>Opens the Last Door and arms the exit tile beyond it.</td></tr>
</tbody></table>
<h3>Automatic Tiles</h3>
<table><thead><tr><th>Where</th><th>Trigger</th><th>Effect</th></tr></thead><tbody>
<tr><td>A1</td><td>Enter (once per token)</td><td>Scrolling text.</td></tr>
<tr><td>A2</td><td>Enter (once per token)</td><td>Opens Handout 2 for that player and grants them access; privately rolls the Wrongness table for you.</td></tr>
<tr><td>A3</td><td>Enter (once)</td><td>Hollow Howl cue and a GM reminder whispered to you.</td></tr>
<tr><td>A3 far end</td><td>Enter (50%)</td><td>The token is teleported back to the start of the room. The room gets longer.</td></tr>
<tr><td>A4</td><td>Stop on the Quiet Light</td><td>Scrolling text, a GM whisper (2 Wayfinding successes), and the hidden Stairwell door appears in A5.</td></tr>
<tr><td>A5</td><td>Enter the door</td><td>Footsteps cue; the token moves to the Undercroft and its owner's view follows.</td></tr>
<tr><td>B2</td><td>Enter (25%, once)</td><td>Lights die for 60 seconds and you get a whisper: the Smiling Dark attacks.</td></tr>
<tr><td>B3</td><td>Enter (once per token)</td><td>Scrolling text marks the haven.</td></tr>
<tr><td>B4</td><td>Enter the open drain</td><td>Party chime; the token moves to the Celebration.</td></tr>
<tr><td>B5</td><td>Click the satchel</td><td>Opens Handout 6 for everyone and removes the satchel from the map.</td></tr>
<tr><td>C1</td><td>First movement in the hall</td><td>SURPRISE! Chime, scrolling text, chat message.</td></tr>
<tr><td>C2, C4</td><td>Enter (once per token)</td><td>Scrolling text.</td></tr>
<tr><td>C3</td><td>Enter (once)</td><td>GM reminder about the Guest Pass.</td></tr>
<tr><td>C5 door</td><td>Enter</td><td>If <em>any</em> player-owned token on the scene carries an item named <strong>Guest Pass</strong>, the token moves to the Threshold. Otherwise it's looped back across the room: “COME AGAIN!”</td></tr>
<tr><td>D1</td><td>Click the ticket machine</td><td>Posts the character's absurd ticket number to chat.</td></tr>
<tr><td>D4 dais</td><td>Enter (until Now Serving)</td><td>“OUT OF ORDER”: the token is Misfiled into the filing alcoves and you're told to roll initiative.</td></tr>
<tr><td>D5</td><td>Enter (after Approve)</td><td>The token steps through the Last Door and is hidden from the map.</td></tr>
</tbody></table>
<p><strong>Tips.</strong> Cross-scene moves bring each token's owner along automatically, so move the whole party before switching your own view. If players skip ahead or you want to run a beat by hand, toggle a tile's Active checkbox in its config. The Guest Pass is a loot item on the Celebrant Host; have a player drag it to their sheet when they earn it.</p>"""

PAGE_NOTES = {
    "A2. The Chalked Room": "Automated: the first time each character enters, Handout 2 opens for that player, and the Wrongness table is rolled privately for you.",
    "A3. The Long Room": "Automated: the howl plays when the party first enters. Tokens that reach the far end have a 50% chance of being teleported back to the start.",
    "A4. The Quiet Light": "Automated: a player token that stops on the silent panel reveals and arms the Stairwell door tile in A5.",
    "A5. The Stairwell": "Automated: the door tile is hidden until the Quiet Light is found (or until you reveal it and toggle it Active yourself). Walking onto it moves the token to the Undercroft.",
    "B2. The Counting Rooms": "Automated: entering B2 has a 25% chance (once) of killing the lights for 60 seconds. Use the GM Lights Out control if the party loses count elsewhere.",
    "B4. The Great Drain": "Automated: double-click the GM Open Drain control when the grate is lifted. The drain tile appears, and walking onto it moves the token to the Celebration.",
    "B5. The Flooded Gallery": "Automated: clicking the satchel tile opens Handout 6 (Form 0-Δ) for everyone and removes the satchel from the map.",
    "C1. The Welcome Hall": "Automated: the first movement in the hall triggers the SURPRISE! chime, text and chat message.",
    "C5. The Exit Corridor": "Automated: the exit door tile checks every player token on the scene for an item named Guest Pass. With it, tokens move to the Threshold; without it, they loop back across the room.",
    "D1. The Queue": "Automated: players can click the ticket machine to take a number.",
    "D4. The Custodian's Desk": "Automated: the dais is ringed by an Out of Order trigger that Misfiles anyone who approaches uncalled. Double-click GM Now Serving to let a called character through, and GM Approve Form to open the Last Door.",
}
