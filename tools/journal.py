"""Adventure text. Each entry: (name, [(page_name, html, level)]). `L` resolves links at build time."""

def box(t): return f'<blockquote class="read-aloud"><p><em>{t}</em></p></blockquote>'
def aside(title, body): return f'<aside class="notable"><h4>{title}</h4>{body}</aside>'
def ul(*items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
def P(*paras): return "".join(f"<p>{p}</p>" for p in paras)

def build(L):
    """L(kind, key) -> @UUID link string. kinds: actor, page, scene, table"""
    A = lambda k, n=None: L("actor", k, n)
    PG = lambda k, n=None: L("page", k, n)
    SC = lambda k, n=None: L("scene", k, n)
    TB = lambda k, n=None: L("table", k, n)
    SK = lambda s, dc: f"[[/skill skill={s} dc={dc}]]"
    SV = lambda a, dc: f"[[/save ability={a} dc={dc}]]"

    entries = []

    # ------------------------------------------------------------------ OVERVIEW
    entries.append(("00. The Interstice: Adventure Overview", [
        ("Introduction", "<h1>The Interstice</h1>" + P(
            "<em>The Interstice</em> is a liminal-horror adventure for four to five characters of 5th to 8th level, designed to run across two or three sessions. It's inspired by the Backrooms and the long tradition of uncanny, empty, in-between places: hallways that go on too long, waiting rooms with nobody waiting, parties that never end.",
            "The horror here is mostly atmosphere and pressure, not gore. Combat matters, but the real enemies are disorientation, isolation, and the slow sense that the place wants you to stay. Your best tools as GM are repetition, the steady hum of the lights, and changing one small detail at a time.",
            "<strong>What's in this module:</strong> four mapped scenes with walls, lighting, ambient sound and map pins already placed; ten statblocks; a set of custom rules (Fraying, Wayfinding, havens); two random tables; seven handouts; and two playlists of ambient loops and sound stingers.")
         + aside("Content Notes", P("This adventure features isolation, being lost, time loss, identity theft by a mimic, and a pleasant-seeming party that won't let anyone leave. Talk with your players before you start about anything they'd rather fade to black."))),
        ("Background", "<h2>Background</h2>" + P(
            "Thirty-one years ago, the Halvard Assay House ran out of room. The Assay House is the guild that measures things for the city of Calder's Reach: property lines, weights, deeds, the exact width of streets. Its archive had swallowed three cellars and was eyeing a fourth.",
            "Magister Tobin Ashgrove, the guild's most brilliant and most overworked assessor, proposed a solution. Every city is full of space nobody uses: the hallway behind the stairs, the hour a waiting room stands empty, the gap between one room and the next. He would <em>assess</em> that unused space, file it, and fold it into a single extradimensional archive. He called it the Interstitial Fold.",
            "It worked beautifully, for eleven days. Then the Fold began assessing on its own. It filed away every forgotten corridor and abandoned room it could reach, all over the world, and stitched them together into an endless plane of in-between places. Things that live in in-between places came with them.",
            "Tobin walked into the Fold to shut it down. He never came out. Over three decades he has fused with the place, becoming the Custodian: a tireless, confused clerk who processes the Interstice's endless paperwork and believes he's merely running late. The Fold can only be closed with his authorization, on the form he designed for the purpose and never got around to signing: <strong>Form 0-Δ, Application for Departure and Closure</strong>.",
            "Now the Fold's edges are thinning. People in Calder's Reach have started vanishing from hallways."), 2),
        ("Adventure Summary", "<h2>Adventure Summary</h2>" + P(
            "The characters investigate the disappearances at the Halvard Assay House, find Tobin's old memo, and step sideways out of the world.") + ul(
            f"<strong>Chapter 1: The Halvard Assay House.</strong> The hook, and the way in. No map; this is a short scene.",
            f"<strong>Chapter 2: The Waiting Halls</strong> ({SC('waiting')}). Endless amber rooms and humming lights. Rule: <em>Don't run.</em> Hollow Hounds and moth swarms. The way down is the light that doesn't hum.",
            f"<strong>Chapter 3: The Undercroft</strong> ({SC('undercroft')}). Flooded stone cellars, the Smiling Dark, and the Waystation, a camp of lost survivors that hides an Echo. The party recovers Tobin's satchel and the blank Form 0-Δ.",
            f"<strong>Chapter 4: The Celebration</strong> ({SC('celebration')}). A party that has been going on for decades. Rule: <em>Accept no invitation.</em> The party needs the Host's Guest Pass to leave.",
            f"<strong>Chapter 5: The Threshold</strong> ({SC('threshold')}). An infinite records office, the Custodian, and the Last Door. Talk Tobin into signing the form, or take his stamp by force.") + P(
            "<strong>Pacing.</strong> Session 1 covers Chapters 1–2 and arrival in the Undercroft. Session 2 covers the Undercroft and the Waystation. Session 3 covers the Celebration and the Threshold. For a two-session run, skip B2 and C2/C4 and use Wren's map to shortcut the Waiting Halls."), 2),
        ("Running Liminal Horror", "<h2>Running Liminal Horror</h2>" + ul(
            "<strong>Familiar, then wrong.</strong> Describe each place as boringly as you can: carpet, plaster, hum. Then change exactly one thing. A chalk mark that was an arrow is now a circle. The room has one more door than it did.",
            "<strong>Repeat yourself on purpose.</strong> Use the same sentence for every new room in the Waiting Halls for a while. When players start to groan, the place is working. Then break the pattern.",
            "<strong>Silence is a sound effect.</strong> Keep the ambient loop running. When something bad is about to happen, stop it. Your players will notice before their characters do.",
            "<strong>Never say what's behind them.</strong> Ask players who is walking last. Ask them to describe what they hear. Let their imaginations do the work.",
            "<strong>Make the rules learnable.</strong> Each level has one rule. Seed it in chalk graffiti, survivor advice, or a dead adventurer's notes. Players who figure out the rules should feel clever and be rewarded with safety.",
            "<strong>The way out is always real.</strong> Despair is not the point. There is always a door, and the characters can always find it. The question is what it costs them.")
         + aside("Using the Audio", P("Each scene has an ambient loop already placed, so it starts when the scene loads. The <strong>Interstice: Stingers</strong> playlist holds one-shot cues: distant footsteps, a hound's howl, the lights dying, and a cheerful party chime. Play them from the Playlists sidebar at the right moment.")), 2),
        ("Scaling & Advancement", "<h2>Scaling &amp; Advancement</h2>" + P(
            "The encounters assume four characters of 5th or 6th level. Characters should reach the next level after the Waystation, and again on returning home if they close the Fold.") + ul(
            "<strong>Level 7–8 party:</strong> add one Hollow Hound to every hound encounter, give the Smiling Dark maximum Hit Points (138) and an extra Unseen Touch, add two Celebrants to the Grand Hall, and give the Custodian 3 Legendary Resistances and 230 Hit Points.",
            "<strong>Five or more players:</strong> add one creature of the lowest CR present to each combat.",
            "<strong>Struggling party:</strong> let Dagny Roe and Wren Halloway fight alongside them. Make Sweetwater easier to find."), 2),
    ]))

    # ------------------------------------------------------------------ RULES
    entries.append(("01. Rules of the Interstice", [
        ("Fraying", "<h2>Fraying</h2>" + P(
            "The Interstice slowly wears away the sense of who and where you are. Each character has a <strong>Fraying</strong> score from 0 to 6. Track it however you like; a token status effect works, or just a tally on the character sheet.",
            "<strong>Gaining Fraying.</strong> A character gains 1 Fraying when they:") + ul(
            "fail a Wayfinding check by 5 or more;",
            f"witness a Wrongness event and fail a {SV('wis', 12)} saving throw (see {TB('wrongness')});",
            "gain the Frightened condition from a creature native to the Interstice;",
            "finish a Long Rest outside a haven;",
            "drink from the drains in the Undercroft (2 Fraying, and the Poisoned condition for 1 hour).") + P(
            "<strong>Reducing Fraying.</strong> A character loses Fraying when they:") + ul(
            "drink a cup of Sweetwater (−1; once per Short Rest);",
            "finish a Long Rest in a haven (−2);",
            "once per session, hold a personal memento and tell the table a true, specific memory of home (−1).") + "<h3>Fraying Effects</h3>" + """
<table><thead><tr><th>Fraying</th><th>Effect</th></tr></thead><tbody>
<tr><td>0–1</td><td>Steady. No effect.</td></tr>
<tr><td>2</td><td><strong>Unmoored.</strong> Disadvantage on Wisdom (Perception) and Wisdom (Insight) checks.</td></tr>
<tr><td>3</td><td><strong>Thin.</strong> Also Disadvantage on Wisdom saving throws.</td></tr>
<tr><td>4</td><td><strong>Echoing.</strong> At the start of each scene, the GM rolls on the Wrongness table for this character alone. Only they experience the result.</td></tr>
<tr><td>5</td><td><strong>Faded.</strong> Your Speed is halved. Other creatures must succeed on a DC 10 Wisdom (Perception) check to notice you if you haven't spoken in the last minute.</td></tr>
<tr><td>6</td><td><strong>Noclipped.</strong> At the end of your next turn you slip through the floor and vanish. You reappear on the next level as a lost soul who has to be found and talked back to themselves (a short scene). When you rejoin the party you have 3 Fraying and a permanent, harmless quirk of your choice (you hum without noticing; your reflection is a beat late).</td></tr>
</tbody></table>"""),
        ("Wayfinding", "<h2>Wayfinding</h2>" + P(
            "Maps lie in the Interstice. Moving from where the party arrives on a level to its exit is a group challenge. Each attempt represents about an hour of walking.",
            "<strong>The challenge.</strong> The party needs <strong>3 successes before 3 failures</strong> (4 successes in the Undercroft). On each attempt, one character describes how they're finding the way and makes a DC 14 check with a fitting skill. Any reasonable approach works:") + ul(
            f"{SK('sur', 14)}: tracking footprints in the damp carpet, sensing air currents;",
            f"{SK('prc', 14)}: listening for the one light that hums differently;",
            f"{SK('inv', 14)}: reading old chalk marks and graffiti;",
            f"{SK('arc', 14)}: feeling where the Fold's seams have been stitched together;",
            f"{SK('ins', 14)} or {SK('his', 14)}: knowing how buildings are <em>supposed</em> to be laid out, and following the wrongness.") + P(
            "Each skill can be used only once per level unless a character describes a genuinely new approach. Other characters can Help.",
            f"<strong>On a failure</strong>, roll on {TB('wandering')}. If the check failed by 5 or more, the character who made it gains 1 Fraying.",
            "<strong>On 3 failures</strong>, the party still reaches the exit eventually, but each character gains 1 Fraying and you choose a complication: they arrive mid-fight, an NPC is missing, or a hound pack has their scent.",
            "<strong>Chalk.</strong> If the party marks its route, it gains Advantage on one Wayfinding check per level. Chalk marks survive about an hour before the Interstice starts to <em>edit</em> them.",
            "<strong>Skipping the challenge.</strong> Wren's map, a <em>find the path</em> spell, or following a level's rule cleverly (standing beneath the Quiet Light) can each count as one or more automatic successes.")),
        ("Resting & Havens", "<h2>Resting &amp; Havens</h2>" + P(
            "<strong>Short Rests</strong> work normally. Roll a d6 when one begins; on a 1, roll on the Wandering table.",
            "<strong>Long Rests</strong> outside a haven still grant their normal benefits, but each character gains 1 Fraying, and a wandering encounter interrupts on a 1–3 on a d6.",
            "<strong>Havens</strong> are places the Interstice can't quite reach. The Waystation (B3) is a haven while its stove is lit. So is any extradimensional space created inside the Interstice, such as <em>rope trick</em>, <em>Leomund's tiny hut</em> or <em>Mordenkainen's magnificent mansion</em>. Players who think of this deserve the reward.")),
        ("Magic in the Interstice", "<h2>Magic in the Interstice</h2>" + ul(
            "<strong>Teleportation</strong> within the Interstice works, but you arrive somewhere random on the same level, regardless of the destination named.",
            "<strong>Plane-crossing magic</strong> (<em>plane shift</em>, <em>gate</em>, <em>teleport</em> to another plane, <em>wish</em> to escape) fails and the spell slot is expended. Only the Last Door leads out.",
            "<strong>Divination</strong> works, but answers arrive in neat, slanting handwriting on a slip of paper in the caster's pocket. <em>Find the path</em> always points toward the Threshold and counts as two Wayfinding successes.",
            "<strong>Sending</strong> and similar messages to the outside arrive 1d6 days late.",
            "<strong>Light</strong> spells work normally, and they are a powerful weapon against the Smiling Dark. Mundane flames burn pale and smell faintly of almonds.",
            "<strong>Extradimensional spaces</strong> (bags of holding, <em>rope trick</em>) work and count as havens. Inside a bag of holding, the party finds everything they ever lost.")),
        ("Sweetwater", "<h2>Sweetwater</h2>" + P(
            "Clear water in waxed-paper cups and clay jugs, cold no matter how long it sits out, tasting faintly of almonds. Nobody knows where it comes from. Survivors guard it like gold.",
            "<strong>Drinking a cup of Sweetwater</strong> restores [[/heal 1d4]] Hit Points and reduces Fraying by 1. A creature can benefit from Sweetwater once per Short Rest.",
            "Sweetwater turns up as treasure throughout the adventure. When in doubt, a lucky search turns up one cup.")),
    ]))

    # ------------------------------------------------------------------ CH1
    entries.append(("02. Chapter 1: The Halvard Assay House", [
        ("Hooks", "<h2>Chapter 1: The Halvard Assay House</h2>" + P(
            "Choose a hook that fits your campaign, or use more than one.") + ul(
            "<strong>The Guild's Problem.</strong> Assayer-Superior Imelda Corte quietly hires the party. Three clerks have vanished from the Assay House this month, last seen walking down the same corridor. She offers 600 gp and a sealed guild writ for discretion.",
            "<strong>A Missing Person.</strong> Someone a character cares about stepped into a stairwell at a tavern and didn't come out the other side. The last place they were seen is a few streets from the Assay House.",
            "<strong>It Happens to You.</strong> Start in the middle of something mundane. One character walks down an inn's hallway to their room and the hallway keeps going. Run Chapter 2 for that character alone for ten minutes, then let the others follow them in.")),
        ("The Assay House", "<h2>The Assay House</h2>" + box(
            "The Halvard Assay House is a squat, important building of grey stone and brass fittings, and it smells of ink and floor polish. Clerks work at long desks under green-shaded lamps. Everyone speaks quietly. Nobody looks at the east corridor.") + P(
            "<strong>The Clerks.</strong> A successful " + SK("per", 12) + " check gets a nervous junior clerk named Fennick to talk. The missing clerks were all sent to retrieve files from the Old Archive at the end of the east corridor. The corridor has been measured three times this month and gives a different length each time.",
            "<strong>The Old Archive.</strong> A dusty, disused records room. A successful " + SK("inv", 13) + " check turns up a locked drawer in Magister Tobin Ashgrove's old desk. Inside is a memo dated thirty-one years ago (see Handout 1: The Ashgrove Memo) and a stick of yellow chalk.",
            "<strong>The East Corridor.</strong> It's forty feet long. Walk it at a stroll, alone, without looking back, and it's longer. Characters who pace it with " + SK("prc", 13) + " notice the floorboards change to damp yellow carpet about halfway, and the hum begins.")),
        ("Stepping Sideways", "<h2>Stepping Sideways</h2>" + box(
            "The lamps behind you are gone. In their place is a hum, low and electric and everywhere, coming from long pale panels set into a ceiling you don't remember. The carpet underfoot is soft and faintly wet. The wallpaper is the yellow of old teeth. There is no corridor behind you. There is a wall, and then another room, and then another.") + P(
            f"Start the scene {SC('waiting')}. The party arrives at A1. Briefly explain the Fraying rules if you're using them openly, or keep them hidden and simply tell players when they gain Fraying and what it does.")),
    ]))

    # ------------------------------------------------------------------ CH2
    entries.append(("03. Chapter 2: The Waiting Halls", [
        ("Overview", "<h2>Chapter 2: The Waiting Halls</h2>" + P(
            "Endless rooms of damp, mustard-yellow carpet and yellowing wallpaper, lit by humming panels of cold light. The rooms connect at random. Every room looks like the last. The Waiting Halls are the Interstice's front door, and most people who come in never get any further.")
         + aside("Level Rule: Don't Run", P(
             "Hollow Hounds know the location of anyone who hurries (see Drawn to Haste). Any character who takes the Dash action, or who runs during exploration, draws a hound within 1d4 rounds. Survivors know this rule. The chalk graffiti in A2 says it over and over.")) + P(
            "<strong>Features.</strong> Bright light everywhere except under broken panels. The ceiling is 10 feet high and the panels can't be removed without breaking them (doing so creates a patch of darkness the Smiling Dark would love). The carpet squelches. The hum is constant; Wisdom (Perception) checks that rely on hearing are made with Disadvantage.",
            "<strong>Navigation.</strong> Use the Wayfinding rules. The exit is the Stairwell (A5), found by following the Quiet Light (A4).")),
        ("A1. Arrival", "<h3>A1. Arrival</h3>" + box(
            "A room, about thirty feet across. Yellow walls, yellow carpet, a pale panel buzzing overhead. Two doorless openings lead to rooms just like this one. A plastic-looking chair lies on its side in the corner, as if someone stood up very suddenly.") + P(
            "The wall the characters walked through is solid. Spells and checks reveal nothing; the way they came in is simply gone.",
            "<strong>The Chair.</strong> Under the chair is a waxed-paper cup of Sweetwater, still cold, and a scrap of paper: <em>“If you're reading this, don't run. — W.”</em>")),
        ("A2. The Chalked Room", "<h3>A2. The Chalked Room</h3>" + box(
            "Every wall of this room is covered in chalk. Arrows, tally marks, names, dates that make no sense. One phrase is written more than any other, in dozens of hands: DON'T RUN.") + P(
            "<strong>Reading the Walls.</strong> A successful " + SK("inv", 13) + " check sorts the useful from the frantic (show Handout 2: The Chalk Walls). The most recent arrows were drawn by Wren Halloway and point toward A4.",
            "<strong>Wrongness.</strong> If the party leaves and returns, one new line has appeared, in the handwriting of one of the characters, which that character doesn't remember writing: <em>“It's not the light that hums. It's the one that doesn't.”</em>")),
        ("A3. The Long Room", "<h3>A3. The Long Room</h3>" + box(
            "This room is far longer than it is wide, a corridor pretending to be a room. The far end is hard to see; the panels down there flicker. Halfway along, the carpet is torn in long parallel stripes.") + P(
            f"<strong>Encounter: Hollow Hounds.</strong> Two {A('hound', 'Hollow Hounds')} lurk at the far end beyond the flickering panels. They watch but don't attack unless someone runs, attacks them, or makes noise (a DC 13 group Dexterity (Stealth) check to pass). If combat starts, play the <em>Hollow Howl</em> stinger. Hounds flee at half Hit Points.",
            "<strong>Treasure.</strong> The torn carpet hides a dead adventurer's pack: 40 gp in old coin from a kingdom that fell eighty years ago, a <em>potion of greater healing</em>, 50 feet of rope, and two cups of Sweetwater.")),
        ("A4. The Quiet Light", "<h3>A4. The Quiet Light</h3>" + box(
            "Something is different here, and it takes you a moment to work out what. One panel in the middle of the ceiling is a cooler, bluer white than the others, and it is completely silent. The silence makes your ears ring. Around the humming panels at the edges of the room, grey shapes cluster like fur.") + P(
            f"<strong>Encounter: Lumen Moths.</strong> Two {A('moths', 'Lumen Moth Swarms')} cover the ordinary panels around the room. They stir when anyone carrying a torch, lantern, or <em>light</em> spell enters, and attack 1 round later. A party that douses its lights first can cross unbothered.",
            "<strong>The Quiet Light.</strong> Anyone who stands beneath the silent panel for a full minute hears, faintly, water dripping below their feet, and feels which direction is <em>down</em>. This counts as two Wayfinding successes for the level.",
            "<strong>Wren's Cache.</strong> Tucked in a slit in the carpet below the light: a tin box with three cups of Sweetwater and a folded sheet (Handout 3: Wren's Map Notes, part 1).")),
        ("A5. The Stairwell", "<h3>A5. The Stairwell</h3>" + box(
            "A door. A real one, grey-painted metal with a push bar, set into the yellow wall where no door should be. A small sign reads STAFF ONLY. Behind it, a concrete stairwell descends into the dim, lit by a single bulb on each landing.") + P(
            "The stair goes down thirteen flights. On the seventh landing the flights start going <em>up</em>, though the characters are definitely still descending. Anyone who looks back up the stairwell sees the same landing they're standing on, and someone standing on it, looking up.",
            f"At the bottom, the characters step into ankle-deep water. Switch to {SC('undercroft')}.")),
    ]))

    # ------------------------------------------------------------------ CH3
    entries.append(("04. Chapter 3: The Undercroft", [
        ("Overview", "<h2>Chapter 3: The Undercroft</h2>" + P(
            "Beneath the Waiting Halls lies an endless maze of wet flagstone storerooms, crates nobody packed, and drains that gurgle with something that isn't quite water. It's dim and cold, and it echoes. Somewhere in the middle, a small group of survivors keeps a stove lit.")
         + aside("Level Rule: Count the Doors", P(
             "Every doorway in the Undercroft has a small brass number plate. Walking toward the Waystation, the numbers count down. Walking away, they count up. If the party loses count (because of a fight, an argument, or anyone saying a number out loud that isn't the next one), the plates all change to the same number, and the party must restart its Wayfinding progress for this level. Survivors teach newcomers to count quietly together, like a prayer.")) + P(
            "<strong>Features.</strong> Dim light at best; most rooms are dark. Water 1 to 6 inches deep, Difficult Terrain where it pools. Wayfinding needs 4 successes here.",
            "<strong>The Drains.</strong> Iron grates in many floors. Never drink from them (see Fraying). The large grate at B4 is the way down.")),
        ("B1. The Landing", "<h3>B1. The Landing</h3>" + box(
            "The stair ends in a low stone room, water lapping at the bottom step. The air is cold enough to see your breath. A brass plate beside the only doorway reads 214. From somewhere ahead comes a steady drip, drip, drip, and very faintly the smell of woodsmoke.") + P(
            "Following the woodsmoke with " + SK("sur", 12) + " grants Advantage on the first Wayfinding check. The number plates count down toward the Waystation, which is room 1.")),
        ("B2. The Counting Rooms", "<h3>B2. The Counting Rooms</h3>" + box(
            "A run of identical storerooms, crates stacked to the ceiling, each doorway marked with its brass number. Someone has scratched tally marks into every plate, and in one room, painted on the floor in what you hope is rust: KEEP COUNTING. IT GETS IN WHEN YOU STOP.") + P(
            f"<strong>Encounter: The Lights Die.</strong> If the party loses count here, or rolls a 7 on the Wandering table, play the <em>Lights Die</em> stinger. Every light source within 60 feet gutters out, magical light excepted, and the {A('smiler', 'Smiling Dark')} attacks the character furthest from the group. If the Smiling Dark is fought here, it does not appear at B5.",
            "<strong>Treasure.</strong> A crate holds a box of twenty <em>everburning</em> tallow candles (treat as candles that never go out; they count as Bright Light against the Smiling Dark in a 5-foot radius).")),
        ("B3. The Waystation", "<h3>B3. The Waystation (Haven)</h3>" + box(
            "A heavy wooden door marked with a brass 1, and behind it, warmth. A rug. A cast-iron stove glowing orange. Bedrolls lined up neatly along one wall, and along the other, shelves of clay jugs filled with clear water. A painted sign hangs over the stove. Six thin, wary faces look up from around the fire.") + P(
            f"The Waystation is a haven while the stove is lit (see Resting &amp; Havens). Show Handout 4: Waystation Rules. Its people:") + ul(
            f"{A('amsel', 'Brother Amsel')}, the keeper of the stove and the Sweetwater. Kind, tired, and determined that everyone should <em>wait</em>. He'll share one cup of Sweetwater per guest per day.",
            f"{A('wren', 'Wren Halloway')}, the cartographer. She left the notes in A4. She'll trade her full map (Handout 3, part 2) for news of the outside, and is shattered to learn the year.",
            f"{A('dagny', 'Dagny Roe')}, the last of a mercenary crew. Wants to leave, and to bring her crew's names home. She doesn't trust Osric.",
            "<strong>Osric</strong>, a quiet lamplighter who keeps the stove fed. Osric died weeks ago in the Undercroft. This is the Echo (see below).",
            "<strong>Bel and Juniper Thrane</strong>, an elderly couple who walked in from a summer fair. Use them to show what waiting too long looks like: polite, faded, and only half there (Fraying 5).") + aside("The Echo Among Them", P(
            f"{A('echo', 'The Echo')} wears Osric's face. It has been taking survivors one at a time, a new face for every hunt. Clues:") + ul(
            "Under the Waiting Halls lights, Osric had no shadow. Dagny saw it once and has told no one.",
            "Osric never drinks Sweetwater. He “already had some.”",
            "Asked about his life before, he repeats the same three sentences word for word.",
            f"A successful {SK('ins', 14)} check while talking with him reveals he's watching the characters' mouths, not their eyes.") + P(
            "If exposed, the Echo attacks, stealing the voice of whoever accused it. If not, it follows the party out and attacks in the Celebration (C2), wearing the face of one of the party's allies.")) + P(
            "<strong>Convincing the Survivors.</strong> Amsel opposes leaving until he sees Handout 1 (the Ashgrove Memo) or Form 0-Δ, proof that someone built a way out. A successful " + SK("per", 15) + " check, or simply showing him the satchel from B5, wins him over. If he's convinced, he gives the party six cups of Sweetwater and his blessing (each character gains the benefit of a Long Rest in a haven, and Mend from him).")),
        ("B4. The Great Drain", "<h3>B4. The Great Drain</h3>" + box(
            "In the center of a round room, a huge iron grate covers a shaft wide enough to drop a cart through. Warm air breathes up from below, carrying the smell of frosting. And underneath the gurgle of water, very faint, you hear music. A waltz, played on a music box, slightly out of tune.") + P(
            "The grate lifts with a DC 15 Strength (Athletics) check, or opens on its own to anyone who says “thank you for having me.” Iron rungs lead down into a soft, warm dark, then a velvet curtain.",
            f"Switch to {SC('celebration')}. Start the party at C1.")),
        ("B5. The Flooded Gallery", "<h3>B5. The Flooded Gallery</h3>" + box(
            "The water here is waist-deep and black, and perfectly still. Broken light panels hang from the ceiling, dark. On a stone ledge at the far end, above the waterline, sits a leather satchel with brass clasps, untouched.") + P(
            f"<strong>Encounter: The Smiling Dark.</strong> If it hasn't been fought at B2, the {A('smiler', 'Smiling Dark')} lairs here and attacks once the party is halfway across. The water counts as Difficult Terrain.",
            "<strong>Tobin's Satchel.</strong> Tobin Ashgrove dropped this on his way to the Threshold thirty-one years ago. Inside:") + ul(
            "a blank <strong>Form 0-Δ: Application for Departure and Closure</strong> (Handout 6). It needs a signature and an APPROVED stamp from the Custodian;",
            "a pair of <em>Spectacles of the Assessor</em> (wondrous item, uncommon, attunement: while wearing them, you can see the true length of any room or corridor and you have Advantage on Wayfinding checks);",
            "a cracked hand-mirror on whose back is etched: <em>To Tobin, come home for supper. — M.</em> This is from his wife, Marguerite, and it matters at the end.")),
    ]))

    # ------------------------------------------------------------------ CH4
    entries.append(("05. Chapter 4: The Celebration", [
        ("Overview", "<h2>Chapter 4: The Celebration</h2>" + P(
            "A banquet hall, then another, then another. Plank floors scattered with confetti, long tables laid with cake and untouched plates, balloons nodding in the corners, streamers that never fade. A waltz is always playing two rooms over. The party has been going on for thirty-one years, ever since the Fold swallowed the retirement party the Assay House was throwing in the Old Archive for its oldest clerk, on the eleventh day.")
         + aside("Level Rule: Accept No Invitation", P(
             "The Celebrants will offer cake, a dance, a seat, a party hat, a drink. Any creature that accepts (by saying yes, eating, drinking, or putting on a hat) must succeed on a " + SV("wis", 14) + " saving throw or gain the Charmed condition toward all Celebrants and 1 Fraying. A creature Charmed this way wants to stay; it repeats the save each hour, or when it takes damage. Declining politely is always safe. Declining rudely makes them sad, and sad Celebrants want hugs.")) + P(
            "<strong>Features.</strong> Bright light. Doors between halls are double doors with no locks. The food is real and delicious, and eating it is accepting an invitation.",
            f"<strong>Wayfinding</strong> doesn't apply here. The exit corridor (C5) only opens for a guest holding the Host's <strong>Guest Pass</strong>. Play the <em>Party Chime</em> stinger when the party first arrives.")),
        ("C1. The Welcome Hall", "<h3>C1. The Welcome Hall</h3>" + box(
            "A burst of warmth, light and music, and a dozen cheerful voices crying “SURPRISE!” A long banner reads HAPPY DEPARTURE! Figures in party hats crowd around you: soft yellow cloth faces with huge smiles inked on. On the table is a cake, and on the cake, in pink icing, are your names.") + P(
            f"Four {A('celebrant', 'Celebrants')} greet the party with hugs, hats, and cake. They're not hostile unless an invitation is refused rudely or someone attacks. Use this room to teach the level rule. The Celebrants have no Guest Pass and can't explain what one is; they just point toward the music."
            )),
        ("C2. The Coat Room", "<h3>C2. The Coat Room</h3>" + box(
            "Rails of coats run the length of this room, hundreds of them, cloaks and jackets and children's mittens pinned to sleeves. Each has a paper tag. Near the door hang several coats you recognize. They're yours. You're still wearing them.") + P(
            "Each character finds a duplicate of their own outer garment. The tags read their names and today's date. Pockets of the other coats hold the belongings of people who vanished into the Interstice over thirty years: letters, keys, a child's tooth in a twist of paper. A thorough search (" + SK("inv", 12) + ") turns up 2d4 cups of Sweetwater and a party invitation (Handout 5).",
            f"<strong>The Echo.</strong> If it survived the Waystation, {A('echo', 'the Echo')} waits here wearing the face of an ally (Dagny, Wren, or Amsel). It tries to separate one character among the coat rails before it strikes.",
            "<strong>Wrongness.</strong> Anyone who puts on their duplicate coat gains 1 Fraying and remembers, vividly, a childhood birthday that never happened.")),
        ("C3. The Grand Hall", "<h3>C3. The Grand Hall</h3>" + box(
            "The music is loudest here. In the biggest hall of all, Celebrants waltz in slow, careful circles around a table piled with gifts. At the head of the room stands one that is taller than the rest, in a paper crown. Its smile has been drawn so many times the ink has bled down its chin like a beard. A brass pass hangs on a ribbon around its neck. It sees you, and it opens its arms wide.") + P(
            f"The {A('host', 'Celebrant Host')} and four {A('celebrant', 'Celebrants')} are here. The Host wants the party to stay forever. It has been keeping the party going for the guest of honor, an old clerk named Hollis Brandt who walked out of the room on day eleven and never came back.",
            "<strong>Talking.</strong> The Host can't be persuaded with logic, only with ceremony. The party can earn the Guest Pass three ways:") + ul(
            f"<strong>Give a toast.</strong> A character toasts the guest of honor and makes the Host believe the party is over because Hollis has <em>gone home happy</em>. This needs a {SK('prf', 16)} or {SK('per', 16)} check, with Advantage if they learned Hollis's name from the gift tags in C4.",
            "<strong>Be the guest of honor.</strong> A character accepts the party in Hollis's place, and then leaves properly: a speech, goodbyes to each Celebrant, out the door. This requires accepting an invitation (and the Charm save), but if the character makes it to the door, the Host weeps ink and hands over the pass.",
            "<strong>Take it.</strong> Defeat the Host. Remember The Party Must Go On: Fire and Radiant damage put Celebrants down for good.") + P(
            "<strong>Treasure.</strong> On the gift table: a <em>Quiet Lantern</em> (see C4) if it hasn't been found, and 300 gp in party favors made of real silver.")),
        ("C4. The Gift Room", "<h3>C4. The Gift Room</h3>" + box(
            "Presents. Hundreds of them, stacked to the ceiling in shiny paper, each tag lettered with care. You find your names on the tags.") + P(
            "Each character has one gift. Inside is a small thing they lost long ago: a toy, a ring, a letter. Opening it reduces their Fraying by 1. Gift tags on the older presents all read <em>For Hollis, with love from everyone at the Assay House</em>, which gives Advantage on the toast in C3.",
            "<strong>Magic Items.</strong> Among the gifts:") + ul(
            "<em>Quiet Lantern</em> (wondrous item, uncommon): a hooded brass lantern that never hums. It sheds Bright Light in a 30-foot radius. Creatures that take damage from being in Bright Light (such as the Smiling Dark) take it from this light, and Lumen Moth Swarms can't use Light-Drunk against its bearer.",
            "<em>Assessor's Chalk</em> (wondrous item, common, 3 sticks): marks made with this chalk never change or fade, even in the Interstice. A party using it gains Advantage on all Wayfinding checks for a level.")),
        ("C5. The Exit Corridor", "<h3>C5. The Exit Corridor</h3>" + box(
            "A long, quiet corridor leads away from the music. Paper bunting hangs along it, letters spelling THANK YOU FOR COMING! At the far end is a plain door, and above it, a small sign: PLEASE HAVE YOUR PASS READY.") + P(
            "Without the Guest Pass, the corridor loops: walk to the end and you're back at the start, the bunting reading THANK YOU FOR COMING! COME AGAIN! COME AGAIN! With the pass, the door opens onto a hush, a smell of paper, and a long queue.",
            f"Switch to {SC('threshold')}.")),
    ]))

    # ------------------------------------------------------------------ CH5
    entries.append(("06. Chapter 5: The Threshold", [
        ("Overview", "<h2>Chapter 5: The Threshold</h2>" + box(
            "Silence, after the music. A vast, high-ceilinged hall floored in green and cream marble, with rows of empty clerks' desks stretching ahead under cold blue lamps. Papers drift across the floor though there is no wind. Filing cabinets line the walls in deep alcoves. At the far end, on a dais of red carpet, a figure sits behind an enormous desk, stamping forms, one after another, without looking up. Behind him stands a pair of tall golden doors.") + P(
            "This is the administrative heart of the Fold, and the only way out. The Last Door (D5) is locked and can't be opened, damaged, or bypassed by any means, short of a properly completed Form 0-Δ.")
         + aside("Level Rule: Wait Your Turn", P(
             "The Threshold is a queue. Anyone who takes a ticket at D1 and waits will be called to the desk. Anyone who cuts the line, attacks, or approaches the dais uncalled is <em>out of order</em>: the Custodian immediately uses Misfile on them, and initiative begins.")) + P(
            "<strong>Play the Threshold Drone</strong> ambience, and let it run long. The Custodian calls numbers in a dry, tired voice: “Now serving… number… four hundred and eighty thousand and eleven.”")),
        ("D1. The Queue", "<h3>D1. The Queue</h3>" + box(
            "Brass stanchions and velvet rope form a switchback line just inside the entrance. A ticket dispenser on a post offers small paper slips. Pale, flickering figures stand in the queue: lost souls, waiting so long they have become part of the waiting.") + P(
            "The ticket dispenser gives each character a number. The numbers are absurdly high, except for one character's ticket, which reads <strong>0</strong>. That character will be called next. If you want tension, the figures in line begin to turn and look at them.",
            "<strong>The Lost.</strong> The waiting figures are the Faded remains of people who reached the Threshold and never finished their paperwork. A successful " + SK("rel", 13) + " or " + SK("per", 13) + " check gets one to whisper a warning: <em>“He'll sign if you remind him. He's forgotten what he's for.”</em>")),
        ("D2. The Clerks' Floor", "<h3>D2. The Clerks' Floor</h3>" + P(
            "Forty desks, each piled with forms. Each form is a record of someone who entered the Interstice: name, date of entry, and a large box marked STATUS. Almost every one reads PENDING.",
            "A search (" + SK("inv", 13) + ") turns up the characters' own files, already started, with their arrival time recorded to the minute. Their status reads PENDING. A second success finds a file marked <strong>ASHGROVE, TOBIN — Assessor — Status: LATE</strong>, with a note in a woman's hand clipped to it: <em>Supper's cold. Come home. — M.</em>")),
        ("D3. The Filing Alcoves", "<h3>D3. The Filing Alcoves</h3>" + P(
            "Cabinet after cabinet of records. Creatures hit by the Custodian's Misfile tend to land here, bruised and surrounded by paper.",
            "<strong>Tobin's Last Memo.</strong> In the bottom drawer of the nearest cabinet is a sheaf of pages in the same slanting handwriting as Handout 1, increasingly ragged (Handout 7: The Last Memo). It explains what he became and why he can't finish the form himself: <em>an applicant cannot approve their own application.</em> Someone else has to fill it in and bring it to him.",
            "Characters who read it have Advantage on checks to persuade the Custodian.")),
        ("D4. The Custodian's Desk", "<h3>D4. The Custodian's Desk</h3>" + P(
            f"{A('custodian', 'The Custodian')} sits on the dais. When a character is called (or arrives out of order), he looks up for the first time: a lantern-head of stacked paper, a dozen arms, each holding a stamp.") + box(
            "“Next. Name, purpose of visit, and supporting documents, please. I'm afraid we're running a little behind.”") + "<h4>The Peaceful Path</h4>" + P(
            "If the party presents Form 0-Δ, he takes it and frowns. “Incomplete. Applicant's signature missing.” Run a short skill challenge: <strong>3 successes before 3 failures</strong>, DC 16. Each success is a piece of Tobin's identity returning:") + ul(
            "<strong>His name.</strong> Showing him his own file (D2) or the mirror from the satchel (B5). Automatic success.",
            "<strong>His purpose.</strong> Reminding him that he built the Fold to <em>help</em>, and that it's hurting people. " + SK("per", 16) + " or " + SK("arc", 16) + ".",
            "<strong>His home.</strong> Telling him about Marguerite, about supper going cold, about the thirty-one years. " + SK("ins", 16) + " to find the right words, or " + SK("per", 16) + ".",
            "<strong>The rule.</strong> Pointing out that the form needs a different applicant, and having a character sign it as applicant themselves. " + SK("his", 16) + " or " + SK("inv", 16) + ".") + P(
            "On success, Tobin's arms slow and stop. He signs the form in a shaking hand, and stamps it APPROVED. “Thank you,” he says. “I'd like to go home now.”",
            "<strong>On 3 failures</strong>, or if the party attacks, the Custodian stands: “Your application is denied.” Roll initiative.") + "<h4>The Fight</h4>" + P(
            "The Custodian fights from the dais, using Misfile to scatter the party into the filing alcoves. If the characters keep trying to reason with him mid-fight, let a successful check count toward the challenge, and end the fight early if they reach 3 successes.",
            "When reduced to 0 Hit Points, he collapses into a drift of paper, and in the chair sits a very old, very small man, asleep. His brass APPROVED stamp lies on the desk. A character can stamp the form, but without his signature the door opens only partway (see Endings).")),
        ("D5. The Last Door & Endings", "<h3>D5. The Last Door</h3>" + P(
            "The golden doors open fully only for a signed and stamped Form 0-Δ; a form that is stamped but unsigned opens them partway. Beyond them is the dusty Old Archive of the Halvard Assay House, and the smell of floor polish.") + "<h4>Endings</h4>" + ul(
            "<strong>Closure (signed and stamped).</strong> The Fold closes behind them like a book. Everyone inside who is still themselves comes home: the Waystation survivors, Wren and Dagny if they lived, and Tobin Ashgrove, ninety years old and weeping. All the lost corridors of the world are a little shorter tomorrow. Imelda Corte pays double.",
            "<strong>Escape (stamped but unsigned).</strong> The doors open just wide enough for the party and anyone with them. The Fold stays open; the vanishings slow but don't stop. Tobin's body comes home. His mind stays behind, and a new, colder Custodian begins processing forms. Good hook for a sequel.",
            "<strong>Stayed behind.</strong> Any character who was Noclipped and not recovered, or who accepted the Celebration, can be rescued in a future session. They'll have been gone a day. It will have been a year.") + aside("Rewards", P(
            "Advance characters one level. Imelda Corte's fee (600 gp, or 1,200 gp for Closure). The Assay House grants each character a lifetime guild writ: free assessment of any property, deed or treasure, forever. Tobin, if he came home, gives the party his last invention, a pocket watch that always tells the true time anywhere, on any plane."))),
    ]))

    # ------------------------------------------------------------------ NPC / BESTIARY index
    entries.append(("07. Cast & Bestiary", [
        ("Monsters", "<h2>Monsters of the Interstice</h2>" + ul(
            f"{A('hound')} (CR 3): drawn to anyone who hurries. The Waiting Halls.",
            f"{A('moths')} (CR 2): eats light. Around the panels of the Waiting Halls.",
            f"{A('smiler')} (CR 5): lives where the lights broke. The Undercroft.",
            f"{A('echo')} (CR 4): a copy of a person, hiding among survivors. The Waystation.",
            f"{A('celebrant')} (CR 2): the eternal guests. The Celebration.",
            f"{A('host')} (CR 6): keeper of the party and the Guest Pass. The Grand Hall.",
            f"{A('custodian')} (CR 9): Tobin Ashgrove, thirty-one years late. The Threshold.")),
        ("Characters", "<h2>People of the Interstice</h2>" + ul(
            f"{A('wren')}: cartographer, arrived thirty-one years ago, believes it's been three days. Ally and guide.",
            f"{A('amsel')}: keeper of the Waystation stove and Sweetwater. Wants everyone to wait. Can be won over.",
            f"{A('dagny')}: last of a mercenary crew. Ready to leave. Suspects Osric.",
            "<strong>Osric</strong>: the Waystation's lamplighter. Actually the Echo.",
            "<strong>Magister Tobin Ashgrove</strong>: the architect of the Fold. Now the Custodian.",
            "<strong>Imelda Corte</strong>: Assayer-Superior of the Halvard Assay House. Patron (Chapter 1).",
            "<strong>Hollis Brandt</strong>: the guest of honor at a retirement party thirty-one years ago. Never seen; only remembered.")),
    ]))

    # ------------------------------------------------------------------ HANDOUTS
    entries.append(("08. Handouts", [
        ("Handout 1: The Ashgrove Memo", "<h2>Halvard Assay House — Internal Memorandum</h2>" + P(
            "<em>To: The Assayer-Superior<br>From: Magister T. Ashgrove, Senior Assessor<br>Re: The Interstitial Fold, Day 11</em>",
            "The Fold continues to exceed projections. As of this morning it has assessed, filed and incorporated every unused corridor in the Assay House, plus (I confess I cannot account for these) a waiting room in a town I have never visited, and a stairwell from a building that burned down in my grandfather's time.",
            "I have also received reports that clerks sent to the Old Archive are taking considerably longer to return than the distance would suggest. Hollis has not returned from his own retirement celebration, though I am assured he was enjoying himself.",
            "I am confident this is a filing error. I will go in this afternoon and correct it personally. Form 0-Δ (Departure and Closure) is drafted and only awaits a signature. I shall be back before supper.",
            "<em>— T.A.</em>")),
        ("Handout 2: The Chalk Walls", "<h2>Scrawled in Chalk</h2>" + P(
            "DON'T RUN &nbsp;·&nbsp; DON'T RUN &nbsp;·&nbsp; they come when you RUN",
            "day 4 &nbsp;·&nbsp; day 4 &nbsp;·&nbsp; day 4?? &nbsp;·&nbsp; is it still day 4",
            "the moths want your lantern. put it out &amp; walk slow",
            "MARTA I WENT LEFT &nbsp;·&nbsp; — no you didnt",
            "→ follow the blue light → it doesn't hum → it doesn't hum → (signed) W.H.",
            "THERES A STOVE DOWN BELOW. COUNT THE DOORS.")),
        ("Handout 3: Wren's Map Notes", "<h2>Wren's Map Notes</h2>" + P(
            "<strong>Part 1 (found at A4):</strong>",
            "The Halls don't hold still but they keep their <em>habits</em>. The light that doesn't hum is always in the middle. Stand under it a minute. Listen down. You'll hear the water. Go toward the water and look for a door that has no business being there.",
            "<strong>Part 2 (traded at the Waystation):</strong>",
            "Undercroft: count down to 1, that's home (the stove). Never say a number out loud that isn't the next one, it resets the plates. The big drain past the stove smells like cake. I don't go down there. Dagny says she will.",
            "There was a man with a satchel who went across the black water room years ago. Or yesterday. He never came back for it.",
            "Day 3. — W.H.")),
        ("Handout 4: Waystation Rules", "<h2>Painted Above the Stove</h2>" + ul(
            "Keep the stove lit. Always.",
            "One cup of water each per day. Ask Brother Amsel.",
            "Count the doors together.",
            "Nobody sleeps alone.",
            "If someone comes back different, tell somebody.",
            "Be patient. Our turn will come.")),
        ("Handout 5: An Invitation", "<h2>You're Invited!</h2>" + P(
            "<em>Please join everyone at the Halvard Assay House<br>for a Celebration in honor of</em>",
            "<strong>HOLLIS BRANDT</strong><br><em>on the occasion of his Departure,<br>after forty-four years of faithful service</em>",
            "<em>Old Archive · Sixth Bell · Cake will be served<br>Stay as long as you like!</em>")),
        ("Handout 6: Form 0-Δ", "<h2>Form 0-Δ: Application for Departure and Closure</h2>" + P(
            "<em>Halvard Assay House · Interstitial Fold Division · To be completed in ink</em>",
            "<strong>Section A: Applicant.</strong> Name: ____________ &nbsp; Date of entry: ____________",
            "<strong>Section B: Purpose.</strong> ☐ Departure (individual) &nbsp; ☐ Closure (all assessed space)",
            "<strong>Section C: Declaration.</strong> I, the undersigned, declare that I wish to go home.",
            "Applicant's signature: ____________",
            "<strong>Section D: For Office Use Only.</strong> Authorizing officer: ____________ &nbsp; Stamp: ☐ APPROVED ☐ DENIED ☐ PENDING",
            "<em>Note: An applicant may not authorize their own application.</em>")),
        ("Handout 7: The Last Memo", "<h2>The Last Memo</h2>" + P(
            "<em>Day 11 (still).</em> Found the problem. The Fold files everything that goes unused, and I have been very, very unused down here. I suspect I am being filed.",
            "<em>Day 11.</em> Cannot close it. Form 0-Δ requires an authorizing officer AND an applicant, and they cannot be the same person. I wrote that rule myself. I was very proud of it.",
            "<em>Day 11.</em> There are so many forms. Somebody has to process them. I'll just get a few done while I wait for someone to come.",
            "<em>Day</em>",
            "<em>If you find this, and you find me, please remind me. I had a supper to get home to. Her name was</em>")),
    ]))
    return entries
