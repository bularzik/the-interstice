"""Generates the four Interstice battlemaps plus Foundry wall, light and note data (maps.json)."""
import numpy as np, json, os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

G = 100  # px per grid square (5 ft)
OUT = "./maps"
os.makedirs(OUT, exist_ok=True)

# ---------- helpers ----------
def noise(w, h, scale, seed, octaves=3):
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        small = r.random((h // s + 2, w // s + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w + 2 * s, h + 2 * s), Image.BICUBIC)
        acc += np.asarray(im, np.float32)[s:s + h, s:s + w] / 255 * amp; tot += amp; amp *= .5
    return acc / tot

def tint(base, n, strength):
    """base: rgb tuple, n: HxW noise 0..1 -> HxWx3 array"""
    b = np.array(base, np.float32)[None, None, :]
    return np.clip(b * (1 + (n[..., None] - .5) * strength), 0, 255)

def glow(img, cx, cy, r, color, alpha):
    layer = Image.new("RGB", img.size, (0, 0, 0)); d = ImageDraw.Draw(layer)
    for i in range(24, 0, -1):
        rr = r * i / 24; a = alpha * (1 - i / 24) ** 1.6
        c = tuple(int(v * a) for v in color)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    return ImageChops.add(img, layer.filter(ImageFilter.GaussianBlur(r / 8)))

# ---------- layout: BSP rooms on the grid, walls on cell edges ----------
def bsp(W, H, minsz, seed, maxsz=None):
    rnd = random.Random(seed); rooms = []
    def split(x, y, w, h, depth):
        can_v, can_h = w >= 2 * minsz, h >= 2 * minsz
        big = maxsz and (w > maxsz or h > maxsz)
        if (not can_v and not can_h) or (depth > 2 and not big and rnd.random() < .25):
            rooms.append((x, y, w, h)); return
        vert = can_v and (not can_h or (w > h if abs(w - h) > 2 else rnd.random() < .5))
        if vert:
            s = rnd.randint(minsz, w - minsz); split(x, y, s, h, depth + 1); split(x + s, y, w - s, h, depth + 1)
        else:
            s = rnd.randint(minsz, h - minsz); split(x, y, w, s, depth + 1); split(x, y + s, w, h - s, depth + 1)
    split(0, 0, W, H, 0); return rooms

def room_grid(W, H, rooms):
    g = np.zeros((H, W), int)
    for i, (x, y, w, h) in enumerate(rooms): g[y:y + h, x:x + w] = i
    return g

def edges_from(grid, seed, open_frac, min_open=1, max_open=3, n_open=(1, 2), door_mode=False, blocked=None):
    """Return wall edges {('h'|'v', x, y)} and door edges.
    'v',x,y = vertical edge at grid line x, from y..y+1. 'h',x,y = horizontal edge at line y, x..x+1."""
    rnd = random.Random(seed); H, W = grid.shape
    shared = {}
    for y in range(H):
        for x in range(W):
            if x + 1 < W and grid[y, x] != grid[y, x + 1]:
                shared.setdefault(tuple(sorted((grid[y, x], grid[y, x + 1]))), []).append(("v", x + 1, y))
            if y + 1 < H and grid[y, x] != grid[y + 1, x]:
                shared.setdefault(tuple(sorted((grid[y, x], grid[y + 1, x]))), []).append(("h", x, y + 1))
    walls, doors = set(), set()
    for pair, es in shared.items():
        es.sort(key=lambda e: (e[0], e[1], e[2]))
        if not door_mode and rnd.random() < open_frac: continue  # fully open plan
        es_set = set(es)
        k = rnd.randint(*n_open); openings = set()
        for _ in range(k):
            if len(es) < 3: break
            start = rnd.randrange(1, max(2, len(es) - max_open))
            wdt = rnd.randint(min_open, max_open)
            run = es[start:start + wdt]
            # keep the run on one straight line
            run = [e for e in run if e[0] == run[0][0] and (e[1] == run[0][1] if e[0] == "v" else e[2] == run[0][2])]
            openings.update(run)
        if not openings and es: openings.add(es[len(es) // 2])
        for e in es_set:
            if e in openings:
                if door_mode: doors.add(e)
            else: walls.add(e)
    for x in range(W): walls.add(("h", x, 0)); walls.add(("h", x, H))
    for y in range(H): walls.add(("v", 0, y)); walls.add(("v", W, y))
    return walls, doors

def merge_segments(edges):
    """Merge unit edges into long Foundry wall segments (pixel coords)."""
    segs = []
    hs = sorted([e for e in edges if e[0] == "h"], key=lambda e: (e[2], e[1]))
    vs = sorted([e for e in edges if e[0] == "v"], key=lambda e: (e[1], e[2]))
    cur = None
    for _, x, y in hs:
        if cur and cur[1] == y and cur[2] == x: cur[2] = x + 1
        else:
            if cur: segs.append([cur[0] * G, cur[1] * G, cur[2] * G, cur[1] * G])
            cur = [x, y, x + 1]
    if cur: segs.append([cur[0] * G, cur[1] * G, cur[2] * G, cur[1] * G])
    cur = None
    for _, x, y in vs:
        if cur and cur[0] == x and cur[2] == y: cur[2] = y + 1
        else:
            if cur: segs.append([cur[0] * G, cur[1] * G, cur[0] * G, cur[2] * G])
            cur = [x, y, y + 1]
    if cur: segs.append([cur[0] * G, cur[1] * G, cur[0] * G, cur[2] * G])
    return segs

def edge_px(e):
    k, x, y = e
    return (x * G, y * G, (x + 1) * G, y * G) if k == "h" else (x * G, y * G, x * G, (y + 1) * G)

def draw_walls(img, edges, thick, fill, edge_col, shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new("L", img.size, 0); sd = ImageDraw.Draw(sh)
        for e in edges:
            x1, y1, x2, y2 = edge_px(e); sd.line([x1 + 8, y1 + 10, x2 + 8, y2 + 10], fill=150, width=thick + 10)
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), sh.point(lambda v: int(v * .55)))
        d = ImageDraw.Draw(img)
    for e in edges:
        x1, y1, x2, y2 = edge_px(e); h = thick // 2
        d.rectangle([min(x1, x2) - h, min(y1, y2) - h, max(x1, x2) + h, max(y1, y2) + h], fill=edge_col)
    for e in edges:
        x1, y1, x2, y2 = edge_px(e); h = thick // 2 - 3
        d.rectangle([min(x1, x2) - h, min(y1, y2) - h, max(x1, x2) + h, max(y1, y2) + h], fill=fill)

def draw_doors(img, doors, col, frame):
    d = ImageDraw.Draw(img)
    for e in doors:
        x1, y1, x2, y2 = edge_px(e)
        if e[0] == "h": d.rectangle([x1 + 6, y1 - 7, x2 - 6, y1 + 7], fill=col, outline=frame, width=3)
        else: d.rectangle([x1 - 7, y1 + 6, x1 + 7, y2 - 6], fill=col, outline=frame, width=3)

def wall_docs(edges, doors=(), door_type=1, sight=20):
    out = [{"c": s, "move": 20, "sight": sight, "light": sight, "sound": 20, "door": 0, "ds": 0}
           for s in merge_segments(edges)]
    for e in doors:
        out.append({"c": list(edge_px(e)), "move": 20, "sight": 20, "light": 20, "sound": 20, "door": door_type, "ds": 0})
    return out

def room_center(r): x, y, w, h = r; return ((x + w / 2) * G, (y + h / 2) * G)
def rpx(r): x, y, w, h = r; return [x * G, y * G, w * G, h * G]

data = {}

# ======================= 1. THE WAITING HALLS =======================
def waiting_halls():
    W, H = 36, 26; seed = 11
    rooms = bsp(W, H, 4, seed, maxsz=10); grid = room_grid(W, H, rooms)
    walls, _ = edges_from(grid, seed, open_frac=.1, min_open=1, max_open=2, n_open=(1, 1))
    rnd = random.Random(seed)
    # free-standing pillars: 1x1 squares, add 4 edges each
    pillars = []
    for (x, y, w, h) in rooms:
        if w >= 6 and h >= 6 and rnd.random() < .7:
            px, py = x + rnd.randint(2, w - 3), y + rnd.randint(2, h - 3); pillars.append((px, py))
            walls |= {("h", px, py), ("h", px, py + 1), ("v", px, py), ("v", px + 1, py)}
    w_px, h_px = W * G, H * G
    n1 = noise(w_px, h_px, 6, 1, 2); n2 = noise(w_px, h_px, 220, 2, 3); n3 = noise(w_px, h_px, 60, 3, 2)
    arr = tint((176, 156, 88), n1 * .35 + n3 * .2 + .45, .5)
    stain = np.clip((n2 - .55) * 4, 0, 1)[..., None]                    # damp patches
    arr = arr * (1 - .35 * stain) + np.array([110, 98, 52]) * .35 * stain
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    # faint carpet seams every 2 squares
    for x in range(0, w_px, 2 * G): d.line([x + 50, 0, x + 50, h_px], fill=(150, 132, 72), width=2)
    # ceiling light panels (as seen projected) – the Foundry lights sit on these
    lights = []
    for gy in range(2, H, 4):
        for gx in range(2, W, 4):
            cx, cy = gx * G + rnd.randint(-20, 20), gy * G
            lights.append([cx, cy])
    for (cx, cy) in lights:
        img = glow(img, cx, cy, 260, (255, 240, 170), .28)
    d = ImageDraw.Draw(img)
    for (cx, cy) in lights:
        d.rectangle([cx - 45, cy - 14, cx + 45, cy + 14], fill=(250, 246, 214), outline=(196, 182, 120), width=3)
        d.line([cx - 45, cy, cx + 45, cy], fill=(220, 212, 170), width=2)
    # scattered debris: an overturned chair, a lone shoe, a water cup
    for _ in range(14):
        x, y = rnd.randrange(60, w_px - 60), rnd.randrange(60, h_px - 60)
        kind = rnd.random()
        if kind < .4: d.ellipse([x, y, x + 18, y + 18], outline=(235, 235, 225), width=4)
        elif kind < .7: d.rectangle([x, y, x + 40, y + 40], outline=(120, 96, 60), width=6)
        else: d.ellipse([x, y, x + 30, y + 14], fill=(70, 55, 40))
    draw_walls(img, walls, 20, (214, 197, 128), (150, 132, 70))
    d = ImageDraw.Draw(img)
    # wallpaper chevrons along walls
    for e in walls:
        x1, y1, x2, y2 = edge_px(e)
        for k in range(0, 100, 14):
            if e[0] == "h": d.line([x1 + k, y1 - 6, x1 + k + 6, y1 + 6], fill=(184, 166, 96), width=2)
            else: d.line([x1 - 6, y1 + k, x1 + 6, y1 + k + 6], fill=(184, 166, 96), width=2)
    img.save(f"{OUT}/01-waiting-halls.webp", quality=82)
    # notes: arrival (room touching 0,0), quiet light (center-ish), hound run (long room), exit (far corner)
    by_dist = sorted(rooms, key=lambda r: r[0] + r[1])
    arrival, exitr = by_dist[0], by_dist[-1]
    mid = min(rooms, key=lambda r: abs(room_center(r)[0] - w_px / 2) + abs(room_center(r)[1] - h_px / 2))
    longr = max([r for r in rooms if r not in (arrival, exitr, mid)], key=lambda r: max(r[2], r[3]) / min(r[2], r[3]))
    other = [r for r in rooms if r not in (arrival, exitr, mid, longr)]
    chalk = max(other, key=lambda r: r[2] * r[3])
    notes = {"A1": room_center(arrival), "A2": room_center(chalk), "A3": room_center(longr),
             "A4": room_center(mid), "A5": room_center(exitr)}
    quiet = notes["A4"]
    lt = [{"x": x, "y": y, "dim": 22, "bright": 10, "color": "#ffe9a8", "alpha": .35,
           "anim": "flicker" if rnd.random() < .15 else None} for x, y in lights]
    lt.append({"x": quiet[0], "y": quiet[1], "dim": 12, "bright": 6, "color": "#cfe6ff", "alpha": .5, "anim": "pulse"})
    start = room_center(arrival)
    return {"file": "01-waiting-halls.webp", "w": w_px, "h": h_px, "walls": wall_docs(walls), "lights": lt,
            "notes": notes, "darkness": .35, "start": start,
            "rects": {"A1": rpx(arrival), "A2": rpx(chalk), "A3": rpx(longr), "A4": rpx(mid), "A5": rpx(exitr)}}

# ======================= 2. THE UNDERCROFT =======================
def undercroft():
    W, H = 36, 26; seed = 23
    rooms = bsp(W, H, 4, seed, maxsz=9); grid = room_grid(W, H, rooms)
    rnd = random.Random(seed)
    station = max(rooms, key=lambda r: r[2] * r[3] if 2 < r[0] + r[2] / 2 < W - 2 else 0)
    walls, _ = edges_from(grid, seed, open_frac=.05, min_open=1, max_open=1, n_open=(1, 1))
    # Waystation: rebuild its boundary with doors only
    sx, sy, sw, sh = station
    boundary = {("h", x, sy) for x in range(sx, sx + sw)} | {("h", x, sy + sh) for x in range(sx, sx + sw)} | \
               {("v", sx, y) for y in range(sy, sy + sh)} | {("v", sx + sw, y) for y in range(sy, sy + sh)}
    boundary = {e for e in boundary if not ((e[0] == "h" and e[2] in (0, H)) or (e[0] == "v" and e[1] in (0, W)))} | \
               {e for e in boundary if (e[0] == "h" and e[2] in (0, H)) or (e[0] == "v" and e[1] in (0, W))}
    walls |= boundary
    inner = sorted([e for e in boundary if not ((e[0] == "h" and e[2] in (0, H)) or (e[0] == "v" and e[1] in (0, W)))])
    doors = set(rnd.sample(inner, 2)); walls -= doors
    w_px, h_px = W * G, H * G
    n = noise(w_px, h_px, 80, 5, 3); nf = noise(w_px, h_px, 5, 6, 1)
    arr = tint((112, 112, 106), n * .7 + nf * .3, .55)
    img = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(img)
    # flagstones
    for yy in range(0, h_px, 50):
        off = 25 if (yy // 50) % 2 else 0
        d.line([0, yy, w_px, yy], fill=(70, 70, 66), width=3)
        for xx in range(-off, w_px, 75 + rnd.randint(-8, 8)):
            d.line([xx, yy, xx, yy + 50], fill=(70, 70, 66), width=3)
    # puddles
    pud = Image.new("L", img.size, 0); pd = ImageDraw.Draw(pud)
    for _ in range(26):
        x, y = rnd.randrange(w_px), rnd.randrange(h_px)
        for _ in range(5):
            r = rnd.randint(30, 90); ox, oy = rnd.randint(-60, 60), rnd.randint(-40, 40)
            pd.ellipse([x + ox - r, y + oy - r * .6, x + ox + r, y + oy + r * .6], fill=255)
    pud = pud.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.new("RGB", img.size, (46, 58, 62)), (0, 0), pud.point(lambda v: int(v * .7)))
    d = ImageDraw.Draw(img)
    # drains
    drains = []
    for (x, y, w, h) in rooms:
        if (x, y, w, h) == station or rnd.random() < .45: continue
        cx, cy = (x + w // 2) * G + 50, (y + h // 2) * G + 50; drains.append((cx, cy))
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(30, 30, 30), outline=(90, 90, 88), width=5)
        for k in range(-24, 25, 12): d.line([cx + k, cy - 28, cx + k, cy + 28], fill=(85, 85, 82), width=4)
    # crates and barrels
    for (x, y, w, h) in rooms:
        if (x, y, w, h) == station: continue
        for _ in range(rnd.randint(0, 3)):
            cx, cy = (x + rnd.randint(0, w - 1)) * G + 15, (y + rnd.randint(0, h - 1)) * G + 15
            if rnd.random() < .6:
                d.rectangle([cx, cy, cx + 70, cy + 70], fill=(110, 82, 50), outline=(60, 42, 24), width=4)
                d.line([cx, cy, cx + 70, cy + 70], fill=(70, 50, 30), width=4); d.line([cx + 70, cy, cx, cy + 70], fill=(70, 50, 30), width=4)
            else:
                d.ellipse([cx, cy, cx + 60, cy + 60], fill=(96, 66, 40), outline=(50, 34, 20), width=4)
                d.ellipse([cx + 14, cy + 14, cx + 46, cy + 46], outline=(140, 120, 90), width=3)
    # Waystation dressing: rugs, bedrolls, stove, shelves of water jugs
    px, py = sx * G, sy * G
    d.rectangle([px + 40, py + 40, px + sw * G - 40, py + sh * G - 40], fill=(92, 52, 42), outline=(140, 100, 60), width=6)
    for k in range(min(6, sw - 1)):
        bx = px + 70 + k * 120
        if bx + 70 > px + sw * G - 60: break
        d.rounded_rectangle([bx, py + 80, bx + 70, py + 250], 20, fill=(70, 90, 70), outline=(40, 50, 40), width=3)
        d.ellipse([bx + 15, py + 90, bx + 55, py + 120], fill=(200, 190, 160))
    scx, scy = px + sw * G // 2, py + sh * G // 2 + 40
    d.ellipse([scx - 45, scy - 45, scx + 45, scy + 45], fill=(40, 36, 34), outline=(20, 20, 20), width=5)
    d.ellipse([scx - 20, scy - 20, scx + 20, scy + 20], fill=(240, 140, 40))
    for k in range(sw - 1):
        jx = px + 60 + k * 90; jy = py + sh * G - 120
        if jx + 60 > px + sw * G - 50: break
        d.rectangle([jx, jy, jx + 70, jy + 60], fill=(80, 64, 44))
        for j in range(3): d.ellipse([jx + 4 + j * 22, jy + 16, jx + 22 + j * 22, jy + 40], fill=(190, 215, 225), outline=(100, 120, 130))
    img = glow(img, scx, scy, 420, (255, 150, 60), .45)
    draw_walls(img, walls, 26, (84, 82, 78), (40, 40, 38)); draw_doors(img, doors, (120, 84, 46), (50, 34, 20))
    img.save(f"{OUT}/02-undercroft.webp", quality=82)
    others = [r for r in rooms if r != station]
    entry = min(others, key=lambda r: r[0] + r[1]); exitr = max(others, key=lambda r: r[0] + r[1])
    rest = [r for r in others if r not in (entry, exitr)]
    deep = max(rest, key=lambda r: r[2] * r[3])
    count = max([r for r in rest if r != deep], key=lambda r: r[2])
    notes = {"B1": room_center(entry), "B2": room_center(count), "B3": room_center(station),
             "B4": drains[len(drains) // 2] if drains else room_center(deep), "B5": room_center(exitr)}
    lt = [{"x": scx, "y": scy, "dim": 30, "bright": 15, "color": "#ff9a4a", "alpha": .45, "anim": "torch"}]
    for (x, y, w, h) in others:
        if rnd.random() < .35:
            cx, cy = room_center((x, y, w, h)); lt.append({"x": cx, "y": cy, "dim": 10, "bright": 3, "color": "#bcd0d8", "alpha": .3, "anim": "flicker"})
    return {"file": "02-undercroft.webp", "w": w_px, "h": h_px, "walls": wall_docs(walls, doors), "lights": lt,
            "notes": notes, "darkness": .8, "start": room_center(entry),
            "rects": {"B1": rpx(entry), "B2": rpx(count), "B3": rpx(station), "B5": rpx(exitr)}}

# ======================= 3. THE CELEBRATION =======================
def celebration():
    W, H = 34, 24; seed = 37
    rooms = bsp(W, H, 6, seed, maxsz=14); grid = room_grid(W, H, rooms)
    walls, doors = edges_from(grid, seed, 0, min_open=2, max_open=2, n_open=(1, 1), door_mode=True)
    rnd = random.Random(seed); w_px, h_px = W * G, H * G
    n = noise(w_px, h_px, 30, 8, 2)
    arr = np.zeros((h_px, w_px, 3), np.float32)
    # plank floors: alternate tone per plank row
    plank = (np.arange(h_px) // 25) % 7
    base = np.array([[150, 98, 58], [158, 104, 62], [142, 92, 54], [162, 108, 64], [146, 96, 56], [155, 101, 60], [139, 90, 52]], np.float32)
    arr[:] = base[plank][:, None, :]
    arr *= (.85 + .3 * n)[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    for y in range(0, h_px, 25): d.line([0, y, w_px, y], fill=(96, 60, 34), width=2)
    for y in range(0, h_px, 25):
        for x in range(rnd.randint(0, 300), w_px, 300 + rnd.randint(-40, 40)): d.line([x, y, x, y + 25], fill=(96, 60, 34), width=2)
    pal = [(232, 92, 120), (250, 205, 70), (90, 170, 230), (130, 210, 120), (200, 120, 230)]
    tables = []
    for (x, y, w, h) in rooms:
        cx, cy = room_center((x, y, w, h))
        horiz = w >= h; L = (min(w, h + 4) - 2) * G if horiz else (min(h, w + 4) - 2) * G
        tw, th = (max(200, L), 140) if horiz else (140, max(200, L))
        tx, ty = cx - tw / 2, cy - th / 2; tables.append((tx, ty, tw, th))
        d.rectangle([tx + 8, ty + 10, tx + tw + 8, ty + th + 10], fill=(60, 36, 20))
        d.rectangle([tx, ty, tx + tw, ty + th], fill=(244, 240, 228), outline=(200, 190, 170), width=4)
        steps = int((tw if horiz else th) // 70)
        for k in range(steps):
            for side in (0, 1):
                if horiz: px, py = tx + 35 + k * 70, ty + (30 if side == 0 else th - 30)
                else: px, py = tx + (30 if side == 0 else tw - 30), ty + 35 + k * 70
                d.ellipse([px - 20, py - 20, px + 20, py + 20], fill=(255, 255, 255), outline=(180, 180, 180), width=3)
                d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=rnd.choice([(170, 60, 50), (220, 190, 120), (120, 160, 80)]))
                # chairs
                if horiz: cy2 = ty - 30 if side == 0 else ty + th + 30; d.rectangle([px - 22, cy2 - 18, px + 22, cy2 + 18], fill=(110, 70, 40), outline=(60, 36, 20), width=3)
                else: cx2 = tx - 30 if side == 0 else tx + tw + 30; d.rectangle([cx2 - 18, py - 22, cx2 + 18, py + 22], fill=(110, 70, 40), outline=(60, 36, 20), width=3)
        # cake in the middle
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(255, 225, 235), outline=(220, 120, 160), width=5)
        for a in range(0, 360, 45):
            ax, ay = cx + 22 * math.cos(math.radians(a)), cy + 22 * math.sin(math.radians(a))
            d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(250, 220, 90))
    # confetti
    for _ in range(4500):
        x, y = rnd.randrange(w_px), rnd.randrange(h_px); c = rnd.choice(pal); d.rectangle([x, y, x + 6, y + 3], fill=c)
    # balloons in corners of rooms
    for (x, y, w, h) in rooms:
        for (bx, by) in [(x * G + 70, y * G + 70), ((x + w) * G - 70, (y + h) * G - 70)]:
            for k in range(3):
                ox, oy = rnd.randint(-30, 30), rnd.randint(-30, 30); c = rnd.choice(pal)
                d.ellipse([bx + ox - 26, by + oy - 30, bx + ox + 26, by + oy + 30], fill=c, outline=tuple(int(v * .6) for v in c), width=3)
                d.ellipse([bx + ox - 12, by + oy - 18, bx + ox - 2, by + oy - 6], fill=(255, 255, 255))
    # streamers along walls (wavy)
    lights = []
    for (x, y, w, h) in rooms:
        c = rnd.choice(pal)
        for side in range(2):
            yy = y * G + 30 if side == 0 else (y + h) * G - 30
            pts = [(x * G + 20 + i * 10, yy + 12 * math.sin(i / 3)) for i in range(int((w * G - 40) / 10))]
            d.line(pts, fill=c, width=6)
        lights.append(room_center((x, y, w, h)))
    for (cx, cy) in lights: img = glow(img, cx, cy, 380, (255, 210, 160), .22)
    draw_walls(img, walls, 22, (236, 222, 200), (170, 110, 120)); draw_doors(img, doors, (200, 160, 110), (120, 70, 40))
    d = ImageDraw.Draw(img)
    img.save(f"{OUT}/03-celebration.webp", quality=82)
    by = sorted(rooms, key=lambda r: r[2] * r[3])
    grand = by[-1]; entry = min([r for r in rooms if r != grand], key=lambda r: r[0] + r[1])
    exitr = max([r for r in rooms if r not in (grand, entry)], key=lambda r: r[0] + r[1])
    rest = [r for r in rooms if r not in (grand, entry, exitr)]
    coat = rest[0] if rest else entry; gift = rest[-1] if len(rest) > 1 else exitr
    notes = {"C1": room_center(entry), "C2": room_center(coat), "C3": room_center(grand), "C4": room_center(gift), "C5": room_center(exitr)}
    lt = [{"x": x, "y": y, "dim": 30, "bright": 15, "color": rnd.choice(["#ffd7a0", "#ffb6c8", "#bfe3ff"]), "alpha": .4, "anim": None} for x, y in lights]
    return {"file": "03-celebration.webp", "w": w_px, "h": h_px, "walls": wall_docs(walls, doors), "lights": lt,
            "notes": notes, "darkness": .25, "start": room_center(entry),
            "rects": {"C1": rpx(entry), "C2": rpx(coat), "C3": rpx(grand), "C4": rpx(gift), "C5": rpx(exitr)}}

# ======================= 4. THE THRESHOLD =======================
def threshold():
    W, H = 30, 24; rnd = random.Random(53); w_px, h_px = W * G, H * G
    arr = np.zeros((h_px, w_px, 3), np.float32)
    yy, xx = np.mgrid[0:h_px, 0:w_px]
    chk = ((yy // G) + (xx // G)) % 2
    arr[chk == 0] = (210, 204, 186); arr[chk == 1] = (46, 70, 62)
    n = noise(w_px, h_px, 40, 9, 3); arr *= (.85 + .3 * n)[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    walls = set()
    for x in range(W): walls |= {("h", x, 0), ("h", x, H)}
    for y in range(H): walls |= {("v", 0, y), ("v", W, y)}
    # filing-cabinet alcoves on left and right walls (walls with gaps)
    for side_x in (6, 24):
        for y in range(3, H - 2):
            if y % 4 != 0: walls.add(("v", side_x, y))
    for y in (3, 7, 11, 15, 19):
        for x in list(range(0, 6)) + list(range(24, 30)): pass
    # cabinets drawn in alcoves
    for (x0, x1) in ((0, 6), (24, 30)):
        for y in range(1, H - 1, 2):
            if rnd.random() < .85:
                for x in range(x0, x1, 1):
                    if rnd.random() < .5:
                        d.rectangle([x * G + 8, y * G + 8, x * G + 92, y * G + 70], fill=(108, 112, 118), outline=(60, 62, 66), width=4)
                        for k in range(3): d.line([x * G + 20, y * G + 20 + k * 16, x * G + 80, y * G + 20 + k * 16], fill=(150, 154, 160), width=3)
    # dais and the Last Door (top center)
    d.rectangle([11 * G, 0, 19 * G, 5 * G], fill=(120, 26, 36), outline=(212, 175, 55), width=8)
    d.rectangle([13 * G, 0, 17 * G, 30], fill=(40, 26, 18))
    door = [13 * G, 0, 17 * G, 0]
    d.rectangle([13 * G - 20, 0, 17 * G + 20, 60], outline=(212, 175, 55), width=10)
    d.line([15 * G, 0, 15 * G, 30], fill=(212, 175, 55), width=6)
    # the Custodian's desk
    d.rectangle([12 * G + 20, 3 * G, 18 * G - 20, 4 * G + 20], fill=(70, 40, 24), outline=(30, 16, 8), width=6)
    for k in range(8):
        px, py = 12 * G + 60 + k * 60, 3 * G + 20 + rnd.randint(0, 40)
        d.rectangle([px, py, px + 40, py + 52], fill=(240, 234, 214), outline=(160, 150, 120))
    d.rectangle([14 * G + 60, 2 * G + 30, 15 * G + 40, 2 * G + 90], fill=(60, 30, 30), outline=(20, 10, 10), width=4)  # chair
    # rows of clerk desks
    for row in range(7, H - 3, 3):
        for col in range(8, 23, 3):
            x, y = col * G, row * G
            d.rectangle([x + 10, y + 16, x + 180, y + 86], fill=(92, 58, 34), outline=(40, 24, 12), width=4)
            for k in range(rnd.randint(2, 6)):
                px, py = x + 20 + rnd.randint(0, 120), y + 22 + rnd.randint(0, 40)
                d.rectangle([px, py, px + 34, py + 42], fill=(236, 230, 210), outline=(170, 160, 130))
            d.rectangle([x + 70, y + 100, x + 120, y + 140], fill=(60, 40, 30))
    # papers drifting across floor
    for _ in range(260):
        x, y = rnd.randrange(w_px), rnd.randrange(h_px)
        a = rnd.uniform(0, math.pi); dx, dy = 18 * math.cos(a), 18 * math.sin(a)
        d.polygon([(x - dx, y - dy), (x + dy, y - dx), (x + dx, y + dy), (x - dy, y + dx)], fill=(238, 232, 214), outline=(170, 160, 130))
    # entry arch bottom center
    d.rectangle([14 * G, h_px - 30, 16 * G, h_px], fill=(20, 20, 20))
    lights = [(15 * G, 4 * G)] + [(x * G, y * G) for x in (10, 15, 20) for y in (9, 15, 21)]
    for (x, y) in lights[1:]: img = glow(img, x, y, 300, (170, 200, 255), .22)
    img = glow(img, 15 * G, 1 * G, 520, (255, 220, 140), .35)
    walls.discard(("h", 14, H)); walls.discard(("h", 15, H))
    for x in range(13, 17): walls.discard(("h", x, 0))
    draw_walls(img, walls, 24, (70, 62, 54), (24, 20, 18))
    d = ImageDraw.Draw(img)
    # the Last Door, drawn over the wall line
    d.rectangle([13 * G - 30, 0, 17 * G + 30, 90], fill=(60, 44, 20), outline=(212, 175, 55), width=10)
    d.rectangle([13 * G, 0, 15 * G - 4, 70], fill=(96, 60, 30), outline=(150, 110, 40), width=5)
    d.rectangle([15 * G + 4, 0, 17 * G, 70], fill=(96, 60, 30), outline=(150, 110, 40), width=5)
    for k in range(4):
        d.line([13 * G + 20, 14 + k * 14, 15 * G - 24, 14 + k * 14], fill=(130, 90, 40), width=3)
        d.line([15 * G + 24, 14 + k * 14, 17 * G - 20, 14 + k * 14], fill=(130, 90, 40), width=3)
    d.ellipse([15 * G - 22, 26, 15 * G + 22, 70], fill=(212, 175, 55), outline=(120, 90, 20), width=4)
    d.rectangle([15 * G - 5, 40, 15 * G + 5, 60], fill=(20, 14, 6))
    img.save(f"{OUT}/04-threshold.webp", quality=82)
    wd = wall_docs(walls)
    wd.append({"c": door, "move": 20, "sight": 20, "light": 20, "sound": 20, "door": 1, "ds": 2})  # locked
    notes = {"D1": (15 * G, (H - 2) * G), "D2": (11 * G, 12 * G), "D3": (3 * G, 9 * G), "D4": (15 * G, 4 * G), "D5": (15 * G, 1 * G)}
    lt = [{"x": 15 * G, "y": 1 * G, "dim": 25, "bright": 12, "color": "#ffd890", "alpha": .5, "anim": "pulse"}] + \
         [{"x": x, "y": y, "dim": 14, "bright": 6, "color": "#a9c4ff", "alpha": .35, "anim": "flicker" if rnd.random() < .3 else None} for x, y in lights[1:]]
    return {"file": "04-threshold.webp", "w": w_px, "h": h_px, "walls": wd, "lights": lt, "notes": notes,
            "darkness": .65, "start": (15 * G, (H - 1) * G),
            "rects": {"D1": [12 * G, 20 * G, 6 * G, 3 * G], "D3L": [1 * G, 1 * G, 5 * G, 22 * G], "D3R": [25 * G, 1 * G, 4 * G, 22 * G],
                      "DAIS": [11 * G, 5 * G, 8 * G, 1 * G], "DOOR": [13 * G, 0, 4 * G, 1 * G]}}

data["waiting"] = waiting_halls(); print("waiting halls")
data["undercroft"] = undercroft(); print("undercroft")
data["celebration"] = celebration(); print("celebration")
data["threshold"] = threshold(); print("threshold")
json.dump(data, open("tools/maps.json", "w"), indent=1)
for k in data:  # thumbnails
    im = Image.open(f"{OUT}/{data[k]['file']}"); im.thumbnail((400, 300)); im.save(f"{OUT}/thumb-{data[k]['file']}", quality=75)
print({k: len(v["walls"]) for k, v in data.items()})
