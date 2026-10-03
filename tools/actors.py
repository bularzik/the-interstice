"""dnd5e (2024 rules) actor builders for The Interstice."""
import hashlib, re

def slug(n): return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")

MOD = "modules/the-interstice"

def uid(*parts):
    h = hashlib.sha1("|".join(parts).encode()).hexdigest()
    alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    n = int(h, 16); out = ""
    for _ in range(16): out += alpha[n % 62]; n //= 62
    return out

SRC = {"revision": 1, "rules": "2024", "book": "The Interstice", "license": ""}
VIS = {"level": {}, "requireAttunement": False, "requireIdentification": False, "requireMagic": False}

def _act(aid, typ, act_type="action", act_value=None, extra=None, rng=None, target=None, name=""):
    a = {"_id": aid, "type": typ, "name": name, "sort": 0, "img": None, "flags": {},
         "activation": {"type": act_type, "value": act_value, "override": False, "condition": ""},
         "consumption": {"scaling": {"allowed": False}, "spellSlot": True, "targets": []},
         "description": {"chatFlavor": ""}, "duration": {"units": "inst", "concentration": False, "override": False},
         "effects": [], "range": rng or {"override": False, "units": "self"},
         "target": target or {"template": {"contiguous": False, "units": "ft", "type": ""},
                               "affects": {"choice": False, "type": ""}, "override": False, "prompt": True},
         "uses": {"spent": 0, "recovery": [], "max": ""}, "visibility": VIS}
    if extra: a.update(extra)
    return a

def dmg_part(n, d, types, bonus=""):
    return {"custom": {"enabled": False, "formula": ""}, "number": n, "denomination": d, "bonus": bonus,
            "types": types, "scaling": {"number": 1}}

def _item(actor_id, iid, name, typ, img, system, sort):
    return {"_id": iid, "name": name, "type": typ, "img": img, "system": system, "effects": [], "flags": {},
            "folder": None, "sort": sort, "ownership": {"default": 0},
            "_key": f"!actors.items!{actor_id}.{iid}"}

class Monster:
    def __init__(self, key, name, cr, size, ctype, align, ac, hp, hp_formula, abilities, speed,
                 token, senses=None, skills=None, saves=(), di=(), dr=(), dv=(), ci=(), languages="",
                 lang_values=(), swarm="", subtype="", bio="", disposition=-1, legact=0, legres=0,
                 ac_calc="natural", tsize=1, init_bonus=""):
        self.id = uid("actor", key); self.items = []; self.sort = 0
        prof = 2 if cr < 5 else 3 if cr < 9 else 4 if cr < 13 else 5
        ab = {}
        for k, v in zip(["str", "dex", "con", "int", "wis", "cha"], abilities):
            ab[k] = {"value": v, "proficient": 1 if k in saves else 0, "bonuses": {"check": "", "save": ""}}
        sk = {}
        for k, lvl in (skills or {}).items(): sk[k] = {"value": lvl}
        mv = {"walk": 0, "units": "ft", "hover": False}
        mv.update(speed)
        self.doc = {
            "_id": self.id, "name": name, "type": "npc", "img": f"{MOD}/tokens/{token}.webp",
            "system": {
                "abilities": ab, "skills": sk,
                "attributes": {
                    "ac": {"calc": ac_calc, "flat": ac},
                    "hp": {"value": hp, "max": hp, "temp": None, "tempmax": None, "formula": hp_formula},
                    "init": {"ability": "", "bonus": init_bonus},
                    "movement": mv,
                    "senses": {"units": "ft", "special": "", "ranges": senses or {}},
                    "spellcasting": "int",
                },
                "details": {"biography": {"value": bio, "public": ""}, "alignment": align,
                            "type": {"value": ctype, "subtype": subtype, "swarm": swarm, "custom": ""},
                            "cr": cr, "habitat": {"value": [{"type": "planar", "subtype": "The Interstice"}], "custom": ""}},
                "resources": {"legact": {"max": legact, "spent": 0}, "legres": {"max": legres, "spent": 0},
                              "lair": {"value": False, "initiative": None, "inside": False}},
                "source": SRC,
                "traits": {"size": size,
                           "di": {"value": list(di), "custom": "", "bypasses": []},
                           "dr": {"value": list(dr), "custom": "", "bypasses": []},
                           "dv": {"value": list(dv), "custom": "", "bypasses": []},
                           "ci": {"value": list(ci), "custom": ""},
                           "languages": {"value": list(lang_values), "custom": languages}},
            },
            "prototypeToken": {"name": name, "displayName": 20, "actorLink": False, "disposition": disposition,
                               "displayBars": 20, "bar1": {"attribute": "attributes.hp"}, "width": tsize, "height": tsize,
                               "texture": {"src": f"{MOD}/tokens/{token}.webp", "scaleX": 1, "scaleY": 1},
                               "sight": {"enabled": False}, "appendNumber": True},
            "items": self.items, "effects": [], "folder": None, "sort": 0, "flags": {},
            "ownership": {"default": 0}, "_key": f"!actors!{self.id}",
        }

    def _next(self): self.sort += 100000; return self.sort

    def trait(self, name, html, img="icons/magic/symbols/question-stone-yellow.webp"):
        iid = uid(self.id, name)
        sysd = {"type": {"value": "monster", "subtype": ""}, "activities": {}, "uses": {"spent": 0, "recovery": [], "max": ""},
                "description": {"value": html, "chat": ""}, "identifier": slug(name),
                "source": SRC, "properties": ["trait"], "requirements": ""}
        self.items.append(_item(self.id, iid, name, "feat", img, sysd, self._next())); return self

    def attack(self, name, n, d, dtype, ability, kind="melee", reach=5, rng=None, extra_parts=(), note="",
               img="icons/creatures/claws/claw-curved-jagged-gray.webp", act_type="action", act_value=None):
        iid = uid(self.id, name); aid = uid(iid, "atk")
        act = _act(aid, "attack", act_type, act_value, {
            "attack": {"critical": {"threshold": None}, "flat": False, "type": {"value": kind, "classification": ""},
                       "ability": ability, "bonus": ""},
            "damage": {"critical": {"bonus": ""}, "includeBase": True, "parts": [dmg_part(*p) for p in extra_parts]}})
        desc = '<p class="feature">[[/attack extended]]. [[/damage average extended]].' + (f" {note}" if note else "") + "</p>"
        sysd = {"type": {"value": "natural", "baseItem": ""}, "activities": {aid: act},
                "uses": {"spent": 0, "recovery": [], "max": ""}, "description": {"value": desc, "chat": ""},
                "identifier": slug(name), "source": SRC, "quantity": 1, "equipped": True,
                "damage": {"base": {"number": n, "denomination": d, "types": [dtype], "custom": {"enabled": False},
                                    "scaling": {"number": 1}, "bonus": ""}},
                "properties": ["fin"] if ability == "dex" and kind == "melee" else [], "proficient": None,
                "range": {"value": rng[0] if rng else None, "long": rng[1] if rng else None, "reach": reach, "units": "ft"}}
        self.items.append(_item(self.id, iid, name, "weapon", img, sysd, self._next())); return self

    def save(self, name, ability, dc_from, parts, on_save, html, rng_ft=None, template=None, count="1",
             affects="creature", recharge=None, act_type="action", act_value=None, per_day=None,
             img="icons/magic/control/fear-fright-monster-grin-red-orange.webp"):
        iid = uid(self.id, name); aid = uid(iid, "save")
        rng = {"override": False, "units": "ft", "value": str(rng_ft)} if rng_ft else {"override": False, "units": "self"}
        tgt = {"template": {"contiguous": False, "units": "ft", "type": template[0] if template else "",
                            "size": str(template[1]) if template else ""},
               "affects": {"choice": False, "type": affects, "count": "" if template else count, "special": ""},
               "override": False, "prompt": True}
        act = _act(aid, "save", act_type, act_value, {
            "damage": {"parts": [dmg_part(*p) for p in parts], "onSave": on_save},
            "save": {"ability": [ability], "dc": {"calculation": dc_from, "formula": ""}}}, rng, tgt)
        uses = {"spent": 0, "recovery": [], "max": ""}
        if recharge: uses = {"spent": 0, "max": "1", "recovery": [{"period": "recharge", "formula": str(recharge), "type": "recoverAll"}]}
        if per_day: uses = {"spent": 0, "max": str(per_day), "recovery": [{"period": "day", "type": "recoverAll"}]}
        sysd = {"type": {"value": "monster", "subtype": ""}, "activities": {aid: act}, "uses": uses,
                "description": {"value": html, "chat": ""}, "identifier": slug(name),
                "source": SRC, "properties": [], "requirements": ""}
        self.items.append(_item(self.id, iid, name, "feat", img, sysd, self._next())); return self

    def utility(self, name, html, act_type="action", act_value=None, recharge=None, per_day=None,
                img="icons/magic/symbols/runes-star-orange-purple.webp"):
        iid = uid(self.id, name); aid = uid(iid, "use")
        act = _act(aid, "utility", act_type, act_value, {"roll": {"prompt": False, "visible": False}}, name="Use")
        uses = {"spent": 0, "recovery": [], "max": ""}
        if recharge: uses = {"spent": 0, "max": "1", "recovery": [{"period": "recharge", "formula": str(recharge), "type": "recoverAll"}]}
        if per_day: uses = {"spent": 0, "max": str(per_day), "recovery": [{"period": "day", "type": "recoverAll"}]}
        sysd = {"type": {"value": "monster", "subtype": ""}, "activities": {aid: act}, "uses": uses,
                "description": {"value": html, "chat": ""}, "identifier": slug(name),
                "source": SRC, "properties": [], "requirements": ""}
        self.items.append(_item(self.id, iid, name, "feat", img, sysd, self._next())); return self

M = "[[lookup @name lowercase]]{monster}"
def P(*paras): return "".join(f"<p>{x}</p>" for x in paras)

def build_monsters():
    out = {}

    # ---------- Hollow Hound (CR 3) ----------
    m = Monster("hollow-hound", "Hollow Hound", 3, "med", "monstrosity", "Unaligned", 13, 52, "8d8 + 16",
                (16, 16, 14, 4, 14, 6), {"walk": 50}, "hollow-hound",
                senses={"blindsight": 30, "darkvision": 60}, skills={"prc": 1, "ste": 1},
                bio=P("A long, hairless thing that runs on its knuckles, with a face like a stretched paper lantern and two holes where light should be. Hollow Hounds are the Interstice's immune response: they come for anything that hurries.",
                      "<strong>Tactics.</strong> Hounds circle at the edge of vision and only commit when someone runs. They flee when reduced to half Hit Points, and return ten minutes later from a direction the party has already cleared."))
    m.trait("Drawn to Haste", P(f"The {M} knows the location of any creature within 300 feet of it that took the Dash action or moved more than its Speed in a turn within the last minute. Doors and walls do not hide such a creature from it."))
    m.trait("Pounce", P(f"If the {M} moves at least 20 feet straight toward a creature and then hits it with Rend on the same turn, the target must succeed on a DC [[lookup @abilities.str.dc]] Strength saving throw or have the Prone condition."))
    m.utility("Multiattack", P(f"The {M} makes two Rend attacks."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Rend", 1, 10, "slashing", "str", img="icons/creatures/abilities/mouth-teeth-long-red.webp")
    m.save("Hollow Howl", "wis", "wis", [], "none",
           P(f"<em>Wisdom Saving Throw:</em> each creature within 60 feet that can hear the {M}.",
             "<em>Failure:</em> The target has the Frightened condition until the end of its next turn, and it must use its movement on that turn to move away from the hound. A creature that ends up Dashing this way triggers Drawn to Haste."),
           template=("radius", 60), recharge=5, img="icons/creatures/abilities/wolf-howl-moon-white.webp")
    out["hound"] = m

    # ---------- Lumen Moth Swarm (CR 2) ----------
    m = Monster("lumen-moths", "Lumen Moth Swarm", 2, "med", "beast", "Unaligned", 13, 36, "8d8",
                (3, 16, 11, 1, 12, 3), {"walk": 5, "fly": 40}, "lumen-moth-swarm",
                senses={"blindsight": 10}, swarm="tiny", dr=("bludgeoning", "piercing", "slashing"),
                ci=("charmed", "frightened", "grappled", "paralyzed", "petrified", "prone", "restrained", "stunned"),
                bio=P("Pale, felted moths that gather around the light panels of the Waiting Halls until the panels look furred. They feed on light itself, and leave a fine grey dust that tastes like a dead battery."))
    m.trait("Swarm", P(f"The {M} can occupy another creature's space and vice versa, and can move through any opening large enough for a Tiny moth. It can't regain Hit Points or gain Temporary Hit Points."))
    m.trait("Light-Drunk", P(f"The {M} has Advantage on attack rolls against any creature carrying a source of Bright Light. Nonmagical flames in the swarm's space are extinguished at the end of each of its turns."))
    m.attack("Choking Dust", 2, 6, "poison", "dex", reach=0, note="Damage is halved if the swarm is Bloodied.",
             img="icons/creatures/mammals/bats-movement-flying-black.webp")
    m.save("Stolen Flare", "con", "con", [], "none",
           P(f"<em>Constitution Saving Throw:</em> each creature within 10 feet of the {M}.",
             "<em>Failure:</em> The target has the Blinded condition until the end of its next turn. The swarm releases all the light it has eaten in a single silent white flash; for 1 round, the area is Bright Light even if every lamp in the room is dark."),
           template=("radius", 10), recharge=6, img="icons/magic/light/explosion-star-glow-silhouette.webp")
    out["moths"] = m

    # ---------- The Smiling Dark (CR 5) ----------
    m = Monster("smiling-dark", "The Smiling Dark", 5, "med", "aberration", "Chaotic Evil", 14, 82, "11d8 + 33",
                (6, 18, 16, 10, 14, 18), {"walk": 0, "fly": 40, "hover": True}, "smiling-dark",
                senses={"darkvision": 120}, skills={"ste": 2}, di=("necrotic", "poison"), dv=("radiant",),
                dr=("acid", "cold", "fire", "lightning", "thunder"),
                ci=("exhaustion", "grappled", "paralyzed", "petrified", "poisoned", "prone", "restrained"),
                bio=P("Wherever a light has been broken in the Interstice, the dark that replaces it is not quite the same dark. Look long enough and you see the eyes. Look a moment longer and it smiles.",
                      "<strong>Tactics.</strong> The Smiling Dark douses lights before it attacks, picks off whoever is standing furthest from the group, and retreats from Bright Light. Players who think to light everything up should feel very clever."))
    m.trait("Incorporeal Movement", P(f"The {M} can move through other creatures and objects as if they were Difficult Terrain. It takes 5 (1d10) Force damage if it ends its turn inside an object."))
    m.trait("Light Aversion", P(f"While in Bright Light, the {M} has Disadvantage on attack rolls and can't use Grin. If it starts its turn within Bright Light created by a spell or magic item, it takes 5 (1d10) Radiant damage."))
    m.utility("Unscrew the Light", P(f"The {M} extinguishes one nonmagical light source within 30 feet of it, or one Light panel in the room flickers out for 1 minute."),
              act_type="bonus", img="icons/magic/perception/shadow-stealth-eyes-purple.webp")
    m.utility("Multiattack", P(f"The {M} makes two Unseen Touch attacks."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Unseen Touch", 2, 6, "necrotic", "dex", img="icons/magic/unholy/hand-claw-glow-orange.webp")
    m.save("Grin", "wis", "cha", [(4, 8, ["psychic"])], "half",
           P(f"<em>Wisdom Saving Throw:</em> each creature within 30 feet that can see the {M}.",
             "<em>Failure:</em> [[/damage average]] damage, and the target has the Frightened condition for 1 minute. It repeats the save at the end of each of its turns, ending the effect on itself on a success. A creature that fails also gains 1 Fraying.",
             "<em>Success:</em> Half damage only."),
           template=("radius", 30), recharge=5, img="icons/creatures/abilities/mouth-teeth-human.webp")
    out["smiler"] = m

    # ---------- The Echo (CR 4) ----------
    m = Monster("echo", "The Echo", 4, "med", "monstrosity", "Neutral Evil", 14, 75, "10d8 + 30",
                (14, 16, 16, 14, 14, 16), {"walk": 30}, "the-echo", subtype="shapechanger",
                senses={"darkvision": 60}, skills={"dec": 2, "ins": 1, "ste": 1},
                languages="any language it has heard spoken",
                bio=P("The Interstice does not make new things. It copies. The Echo is what happens when it copies a person: perfect from the outside, and empty enough to rattle.",
                      "<strong>Tells.</strong> Under the fluorescent lights of the Waiting Halls it casts no shadow. It never drinks Sweetwater. It can't say a word it has never heard its original say, so it deflects unfamiliar questions with phrases it has already used, word for word."))
    m.trait("Mimicry", P(f"The {M} can mimic any voice it has heard. A creature that hears it can tell it's an imitation only with a successful DC [[lookup @abilities.cha.dc]] Wisdom (Insight) check, made with Advantage if the creature knew the original well."))
    m.trait("No Shadow", P(f"Under the lights of the Interstice, the {M} casts no shadow. A creature that specifically looks notices this automatically."))
    m.utility("Assume Shape", P(f"The {M} transforms to look like a Small or Medium Humanoid it has observed for at least 1 minute, or back into its true form. Its statistics don't change. Any equipment it is wearing or carrying isn't transformed."),
              act_type="bonus", img="icons/creatures/magical/humanoid-silhouette-glowing-pink.webp")
    m.utility("Multiattack", P(f"The {M} makes two Hollowing Claw attacks."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Hollowing Claw", 2, 6, "slashing", "dex", extra_parts=[(1, 6, ["psychic"])],
             img="icons/creatures/claws/claw-hooked-barbed.webp")
    m.save("Steal Voice", "cha", "cha", [(2, 8, ["psychic"])], "none",
           P(f"<em>Charisma Saving Throw:</em> one creature the {M} can see within 30 feet.",
             "<em>Failure:</em> [[/damage average]] damage, and the target can't speak until the Echo dies or the target finishes a Long Rest. The Echo can speak in the stolen voice perfectly, and it knows every word the target has ever said aloud to it."),
           rng_ft=30, recharge=5, img="icons/magic/control/silhouette-hold-change-blue.webp")
    out["echo"] = m

    # ---------- Celebrant (CR 2) ----------
    m = Monster("celebrant", "Celebrant", 2, "med", "construct", "Chaotic Neutral", 12, 52, "8d8 + 16",
                (16, 14, 14, 6, 10, 16), {"walk": 30}, "celebrant", senses={"blindsight": 60},
                ci=("charmed", "exhaustion", "frightened"), di=("psychic",),
                languages="understands Common but only says party phrases",
                bio=P("Stuffed figures of yellow cloth with smiles drawn on in thick black ink. Celebrants are thrilled you came. They have been waiting so long. They would hate for you to leave.",
                      "<strong>Roleplaying.</strong> Celebrants only speak in cheerful party phrases: <em>“You made it!”</em>, <em>“Have you had cake?”</em>, <em>“Don't go yet, the best part is coming!”</em> They never answer a direct question."))
    m.trait("Everyone's Having Fun", P(f"The {M} has Advantage on an attack roll against a creature if at least one of the {M}'s allies is within 5 feet of the creature and the ally doesn't have the Incapacitated condition."))
    m.trait("Confetti Burst", P(f"When the {M} dies, it bursts into confetti. Each creature within 5 feet of it must succeed on a DC 12 Constitution saving throw or have the Blinded condition until the end of its next turn."))
    m.attack("Hug", 2, 6, "bludgeoning", "str", note=f"If the target is a Medium or smaller creature, it has the Grappled condition (escape DC [[lookup @abilities.str.dc]]).",
             img="icons/skills/melee/unarmed-punch-fist.webp")
    m.save("Join Us!", "wis", "cha", [], "none",
           P(f"<em>Wisdom Saving Throw:</em> one creature within 30 feet of the {M} that can hear it.",
             f"<em>Failure:</em> The target has the Charmed condition until the start of the {M}'s next turn. On its turn, the Charmed target must use its movement to move toward the nearest Celebrant by the safest route."),
           rng_ft=30, act_type="bonus", img="icons/magic/control/hypnosis-mesmerism-swirl.webp")
    out["celebrant"] = m

    # ---------- Celebrant Host (CR 6) ----------
    m = Monster("celebrant-host", "Celebrant Host", 6, "lg", "construct", "Chaotic Neutral", 15, 123, "13d10 + 52",
                (18, 14, 18, 12, 14, 20), {"walk": 30}, "celebrant-host", senses={"blindsight": 60},
                saves=("wis", "cha"), skills={"prf": 2, "per": 1}, ci=("charmed", "exhaustion", "frightened"), di=("psychic",),
                languages="Common", tsize=2,
                bio=P("A towering Celebrant in a paper crown, its smile drawn and redrawn so many times the ink has soaked through. The Host remembers when this was a real party, for someone who was leaving. It has been keeping the party going ever since, because if the party ends, the guest of honor really is gone.",
                      "<strong>The Guest Pass.</strong> The Host wears a brass Guest Pass on a ribbon. Only a guest holding the pass can leave the Celebration through the Exit Corridor (C5)."))
    m.trait("The Party Must Go On", P(f"While the {M} has at least 1 Hit Point, Celebrants within 60 feet of it that are reduced to 0 Hit Points reform at the start of the Host's next turn with half their Hit Points, unless they died from Radiant or Fire damage."))
    m.utility("Multiattack", P(f"The {M} makes two Embrace attacks. It can replace one with Raise a Toast if it's available."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Embrace", 2, 8, "bludgeoning", "str", reach=10,
             note=f"The target has the Grappled condition (escape DC [[lookup @abilities.str.dc]]) if it's Large or smaller. The Host can grapple two creatures at once.",
             img="icons/skills/melee/unarmed-punch-fist.webp")
    m.save("Raise a Toast", "cha", "cha", [(4, 10, ["psychic"])], "half",
           P(f"<em>Charisma Saving Throw:</em> each creature of the {M}'s choice within 30 feet.",
             "<em>Failure:</em> [[/damage average]] damage, and the target has the Charmed condition until the end of its next turn. While Charmed, it raises an imaginary glass and does nothing else.",
             "<em>Success:</em> Half damage only."),
           template=("radius", 30), recharge=5, img="icons/consumables/drinks/alcohol-beer-stein-wooden-metal-brown.webp")
    m.utility("More Guests!", P(f"The {M} claps. 1d3 Celebrants step out from behind curtains, doorways, and under tables within 30 feet. Use the Celebrant statistics."),
              act_type="bonus", per_day=1, img="icons/magic/control/silhouette-aura-energy.webp")
    out["host"] = m

    # ---------- The Custodian (CR 9, legendary) ----------
    m = Monster("custodian", "The Custodian", 9, "lg", "aberration", "Lawful Neutral", 17, 178, "17d10 + 85",
                (18, 12, 20, 22, 16, 16), {"walk": 30}, "the-custodian", senses={"truesight": 60},
                saves=("con", "int", "wis"), skills={"arc": 2, "ins": 1, "prc": 1}, dr=("force", "psychic"),
                ci=("charmed", "exhaustion", "frightened"), languages="all", legact=3, legres=2, tsize=2,
                bio=P("What remains of Magister Tobin Ashgrove, Assessor of the Halvard Assay House, after thirty-one years of processing the Interstice's paperwork alone. His head is a lantern of stacked forms; his many arms each hold a stamp. He is not cruel. He is simply behind schedule, and very tired, and the forms are never finished.",
                      "<strong>Roleplaying.</strong> The Custodian speaks in the patient, clipped voice of a clerk at the end of a long day. He will not fight anyone who waits their turn and presents a complete application. He sometimes forgets his own name."))
    m.trait("Legendary Resistance (2/Day)", P(f"If the {M} fails a saving throw, it can choose to succeed instead."))
    m.trait("Procedure", P(f"Any creature within 60 feet of the {M} that tries to teleport or leave the plane by any means fails, and it takes 10 (3d6) Force damage. The spell or effect is wasted."))
    m.trait("Bound to the Threshold", P(f"The {M} can't leave the Threshold. If reduced to 0 Hit Points, it collapses into a drift of paper, a brass stamp, and a very old man asleep in a chair. (See D4.)"))
    m.utility("Multiattack", P(f"The {M} makes three Stamp attacks. It can replace one of them with Misfile."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Stamp", 2, 8, "bludgeoning", "str", reach=10, extra_parts=[(1, 8, ["force"])],
             note="The target's forehead bears a red ink stamp reading PENDING until it finishes a Long Rest.",
             img="icons/sundries/documents/document-sealed-red-yellow.webp")
    m.save("Misfile", "cha", "int", [(4, 10, ["force"])], "half",
           P(f"<em>Charisma Saving Throw:</em> one creature within 60 feet that the {M} can see.",
             "<em>Failure:</em> [[/damage average]] damage, and the target is teleported to an unoccupied space the Custodian can see within 60 feet, typically a filing alcove (D3).",
             "<em>Success:</em> Half damage only."),
           rng_ft=60, img="icons/sundries/documents/document-sealed-brown-red.webp")
    m.save("Your Application Is Denied", "wis", "int", [(6, 8, ["psychic"])], "half",
           P(f"<em>Wisdom Saving Throw:</em> each creature within 30 feet of the {M}.",
             "<em>Failure:</em> [[/damage average]] damage, and the target has the Incapacitated condition until the end of its next turn while it stares at a form it cannot finish.",
             "<em>Success:</em> Half damage only."),
           template=("radius", 30), recharge=5, img="icons/sundries/documents/document-torn-diagram-tan.webp")
    m.trait("Legendary Actions", P(f"<em>Legendary Action Uses: 3. Immediately after another creature's turn, the {M} can expend a use to take one of the following actions. It regains all expended uses at the start of each of its turns.</em>"),
              img="icons/magic/time/clock-stopwatch-white-blue.webp")
    m.utility("Shuffle Papers", P(f"The {M} moves up to half its Speed without provoking Opportunity Attacks, and papers swirl around it: it has Half Cover until the start of its next turn."),
              act_type="legendary", act_value=1, img="icons/sundries/documents/document-writing-pink.webp")
    m.attack("Stamp (Legendary)", 2, 8, "bludgeoning", "str", reach=10, extra_parts=[(1, 8, ["force"])],
             img="icons/sundries/documents/document-sealed-red-yellow.webp", act_type="legendary", act_value=1)
    m.save("Refile (Costs 2 Actions)", "cha", "int", [(4, 10, ["force"])], "half",
           P(f"The {M} uses Misfile."), rng_ft=60, act_type="legendary", act_value=2,
           img="icons/sundries/documents/document-sealed-brown-red.webp")
    out["custodian"] = m
    return out

def build_npcs():
    out = {}
    m = Monster("wren", "Wren Halloway", 0.5, "med", "humanoid", "Neutral Good", 13, 27, "6d8",
                (10, 14, 11, 15, 15, 12), {"walk": 30}, "wren-halloway", skills={"sur": 2, "prc": 1, "inv": 1},
                languages="Common, Dwarvish", lang_values=("common", "dwarvish"), disposition=0, ac_calc="flat",
                bio=P("A wiry cartographer with ink-stained fingers, a satchel stuffed with mismatched paper, and a compass she no longer trusts. Wren believes she wandered into the Interstice three days ago. It has been thirty-one years, and she is somehow still the age she was when she arrived.",
                      "<strong>Wants:</strong> To finish her map. <strong>Fears:</strong> That the map is drawing her. <strong>Knows:</strong> The routes through the Waiting Halls and Undercroft (see Handout: Wren's Map Notes)."))
    m.trait("Map of Nowhere", P("While Wren travels with the party, the group has Advantage on Wayfinding checks in the Waiting Halls and the Undercroft."))
    m.attack("Shortsword", 1, 6, "piercing", "dex", img="icons/weapons/swords/greatsword-crossguard-barbed.webp")
    m.attack("Sling", 1, 4, "bludgeoning", "dex", kind="ranged", reach=None, rng=(30, 120), img="icons/weapons/slings/slingshot-wood.webp")
    out["wren"] = m

    m = Monster("amsel", "Brother Amsel", 2, "med", "humanoid", "Lawful Neutral", 13, 45, "7d8 + 14",
                (12, 10, 14, 13, 16, 14), {"walk": 30}, "brother-amsel", skills={"med": 2, "ins": 1, "rel": 1},
                saves=("wis",), languages="Common, Celestial", lang_values=("common", "celestial"), disposition=0, ac_calc="flat",
                bio=P("A gaunt, kindly cleric of a lantern-god nobody else has heard of, who keeps the stove lit and the Sweetwater rationed at the Waystation. Amsel arrived nine years ago (he says two months).",
                      "<strong>Secret:</strong> Amsel has twice turned newcomers away from the Waystation when Sweetwater ran low, and the Hollow Hounds took them. He believes leaving is a sin against patience: the Custodian will process everyone eventually, if they only wait. He wants the party to stay. He'll come around if they show him Form 0-Δ or Tobin's memo."))
    m.trait("Keeper of the Stove", P("While Amsel is at the Waystation, creatures there gain the benefits of a haven (see Rules of the Interstice)."))
    m.attack("Lantern Mace", 1, 6, "bludgeoning", "str", extra_parts=[(1, 6, ["radiant"])], img="icons/weapons/maces/mace-flanged-steel.webp")
    m.save("Steady Flame", "dex", "wis", [(3, 8, ["radiant"])], "half",
           P("<em>Dexterity Saving Throw:</em> one creature within 60 feet. <em>Failure:</em> [[/damage average]] damage. <em>Success:</em> Half damage. Against the Smiling Dark, the light lingers: the target's space counts as Bright Light until the end of Amsel's next turn."),
           rng_ft=60, img="icons/magic/fire/flame-burning-hand-white.webp")
    m.utility("Mend", P("Amsel touches one creature, which regains [[/heal 2d8+3]] Hit Points and reduces its Fraying by 1."), per_day=3,
              img="icons/magic/life/cross-worn-green.webp")
    out["amsel"] = m

    m = Monster("dagny", "Dagny Roe", 3, "med", "humanoid", "Chaotic Good", 17, 65, "10d8 + 20",
                (16, 13, 14, 10, 11, 10), {"walk": 30}, "dagny-roe", skills={"ath": 2, "prc": 1, "sur": 1},
                saves=("str", "con"), languages="Common, Orc", lang_values=("common", "orc"), disposition=0, ac_calc="flat",
                bio=P("A scarred sell-sword who came in with a five-person crew hired to “retrieve archive materials.” She's the only one left. Dagny is blunt, sleeps with her sword drawn, and has been planning to try for the Threshold alone.",
                      "<strong>Wants:</strong> Out, and to bring her crew's names home. She has all four written on the inside of her shield. <strong>Suspects:</strong> That Osric, the quiet lamplighter at the Waystation, is not who he says he is. She's right (he's the Echo)."))
    m.utility("Multiattack", P("Dagny makes two Longsword attacks."), img="icons/skills/melee/strike-weapons-orange.webp")
    m.attack("Longsword", 1, 8, "slashing", "str", img="icons/weapons/swords/sword-guard-purple.webp")
    m.attack("Heavy Crossbow", 1, 10, "piercing", "dex", kind="ranged", reach=None, rng=(100, 400), img="icons/weapons/crossbows/crossbow-heavy-black.webp")
    m.utility("Shield Wall", P("When a creature Dagny can see hits an ally within 5 feet of her, Dagny imposes Disadvantage on the attack roll or reduces the damage by 1d10 (her choice, decided after the roll)."),
              act_type="reaction", img="icons/equipment/shield/heater-steel-spiral.webp")
    out["dagny"] = m
    return out
