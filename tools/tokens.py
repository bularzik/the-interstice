import os, math, random
from PIL import Image, ImageDraw, ImageFilter

OUT = "./tokens"; os.makedirs(OUT, exist_ok=True)
S = 800

def base(bg_in, bg_out, ring):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(60, 0, -1):
        t = i / 60; c = tuple(int(bg_in[k] * (1 - t) + bg_out[k] * t) for k in range(3))
        r = 360 * t; d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=c + (255,))
    return im, d, ring

def finish(im, ring, name):
    d = ImageDraw.Draw(im)
    d.ellipse([22, 22, S - 22, S - 22], outline=ring + (255,), width=26)
    d.ellipse([40, 40, S - 40, S - 40], outline=(0, 0, 0, 120), width=6)
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse([10, 10, S - 10, S - 10], fill=255)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0)); out.paste(im, (0, 0), mask)
    out.resize((400, 400), Image.LANCZOS).save(f"{OUT}/{name}.webp", quality=88)

def hound():
    im, d, ring = base((70, 64, 40), (20, 18, 12), (176, 156, 88))
    d.polygon([(400, 150), (520, 330), (600, 600), (400, 520), (200, 600), (280, 330)], fill=(214, 206, 186))
    d.polygon([(400, 170), (500, 330), (560, 560), (400, 490), (240, 560), (300, 330)], fill=(190, 180, 158))
    for x in (345, 455): d.ellipse([x - 38, 300, x + 38, 380], fill=(10, 8, 6))
    d.polygon([(330, 430), (470, 430), (440, 500), (360, 500)], fill=(20, 10, 10))
    for k in range(6): d.polygon([(340 + k * 22, 430), (352 + k * 22, 430), (346 + k * 22, 462)], fill=(240, 236, 220))
    for x in (230, 570): d.line([(400, 160), (x, 90)], fill=(190, 180, 158), width=14)
    finish(im, ring, "hollow-hound")

def moths():
    im, d, ring = base((255, 246, 200), (70, 60, 30), (230, 220, 160))
    rnd = random.Random(4)
    for _ in range(26):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(60, 300); x, y = 400 + r * math.cos(a), 400 + r * math.sin(a)
        s = rnd.uniform(26, 52); rot = rnd.uniform(0, 6.28)
        for side in (-1, 1):
            pts = [(x, y)] + [(x + side * s * math.cos(rot + k) * 1.2, y + s * math.sin(rot + k) * .8) for k in (0.3, 0.9, 1.6)]
            d.polygon(pts, fill=(236, 228, 200), outline=(120, 110, 80))
        d.ellipse([x - 5, y - 12, x + 5, y + 12], fill=(90, 80, 60))
    finish(im, ring, "lumen-moth-swarm")

def smiler():
    im, d, ring = base((14, 12, 18), (0, 0, 0), (60, 50, 80))
    for x in (300, 500): d.ellipse([x - 34, 280, x + 34, 330], fill=(250, 250, 250))
    d.chord([180, 280, 620, 600], 15, 165, fill=(250, 250, 250))
    for k in range(15):
        x = 215 + k * 26; d.line([(x, 440), (x + 4, 560 - abs(7 - k) * 8)], fill=(30, 30, 30), width=5)
    finish(im.filter(ImageFilter.GaussianBlur(.6)), ring, "smiling-dark")

def echo():
    im, d, ring = base((120, 118, 130), (30, 30, 36), (150, 150, 170))
    d.ellipse([240, 160, 560, 560], fill=(214, 186, 160))
    d.rectangle([400, 150, 570, 570], fill=(120, 118, 130))
    d.ellipse([240, 160, 560, 560], outline=(40, 40, 50), width=6)
    d.pieslice([240, 160, 560, 560], 90, 270, fill=(214, 186, 160))
    d.ellipse([300, 300, 350, 330], fill=(40, 30, 30)); d.arc([290, 400, 400, 470], 20, 120, fill=(90, 40, 40), width=8)
    d.pieslice([240, 160, 560, 560], 270, 450, fill=(226, 224, 230))
    d.line([(400, 160), (400, 560)], fill=(40, 40, 50), width=6)
    finish(im, ring, "the-echo")

def celebrant(name, hat_color, crown=False):
    im, d, ring = base((250, 214, 120), (120, 60, 60), (232, 92, 120))
    d.ellipse([230, 230, 570, 600], fill=(236, 206, 90), outline=(150, 120, 40), width=8)
    for y in range(260, 590, 26): d.line([(250, y), (550, y + 6)], fill=(214, 186, 76), width=3)
    for x in (330, 470): d.ellipse([x - 26, 350, x + 26, 400], fill=(20, 20, 20))
    d.arc([280, 360, 520, 560], 15, 165, fill=(20, 20, 20), width=14)
    if crown:
        d.polygon([(260, 250), (300, 120), (350, 210), (400, 90), (450, 210), (500, 120), (540, 250)], fill=hat_color, outline=(120, 90, 20))
    else:
        d.polygon([(320, 255), (400, 70), (480, 255)], fill=hat_color, outline=(80, 40, 60))
        d.ellipse([380, 50, 420, 90], fill=(250, 250, 250))
        for k in range(3): d.line([(340 + k * 30, 240 - k * 50), (470 - k * 25, 240 - k * 50)], fill=(250, 250, 250), width=8)
    finish(im, ring, name)

def custodian():
    im, d, ring = base((60, 70, 66), (10, 14, 12), (212, 175, 55))
    d.rectangle([260, 330, 540, 700], fill=(46, 48, 56))
    d.polygon([(400, 330), (360, 420), (400, 520), (440, 420)], fill=(230, 226, 214))
    d.rectangle([300, 120, 500, 330], fill=(240, 220, 150), outline=(212, 175, 55), width=12)
    for k in range(3): d.line([(300, 180 + k * 50), (500, 180 + k * 50)], fill=(212, 175, 55), width=6)
    d.rectangle([340, 90, 460, 120], fill=(212, 175, 55))
    for side in (-1, 1):
        for k in range(3):
            x0 = 400 + side * 150; d.line([(x0, 420 + k * 40), (400 + side * (290 - k * 10), 360 + k * 70)], fill=(46, 48, 56), width=22)
            d.rectangle([400 + side * (290 - k * 10) - 20, 340 + k * 70, 400 + side * (290 - k * 10) + 20, 380 + k * 70], fill=(150, 30, 40))
    finish(im, ring, "the-custodian")

def emblem(name, bg, ring, draw):
    im, d, r = base(bg, tuple(int(c * .3) for c in bg), ring); draw(d); finish(im, r, name)

def wren(d):
    d.rectangle([220, 250, 580, 560], fill=(232, 220, 186), outline=(120, 90, 50), width=8)
    for k in range(6): d.line([(240, 280 + k * 45), (560, 300 + k * 38)], fill=(150, 120, 80), width=4)
    d.ellipse([430, 380, 560, 510], fill=(200, 170, 80), outline=(90, 70, 20), width=8)
    d.polygon([(495, 395), (510, 445), (495, 495), (480, 445)], fill=(160, 30, 30))

def amsel(d):
    d.polygon([(400, 140), (600, 660), (200, 660)], fill=(80, 60, 50))
    d.ellipse([320, 280, 480, 440], fill=(30, 20, 18))
    d.polygon([(400, 470), (440, 560), (400, 620), (360, 560)], fill=(255, 170, 60))
    d.polygon([(400, 510), (420, 565), (400, 600), (380, 565)], fill=(255, 235, 150))

def dagny(d):
    d.chord([250, 180, 550, 560], 180, 360, fill=(150, 150, 160), outline=(70, 70, 80), width=8)
    d.rectangle([250, 370, 550, 470], fill=(150, 150, 160), outline=(70, 70, 80), width=8)
    d.rectangle([290, 330, 510, 360], fill=(20, 20, 24))
    d.line([(400, 470), (400, 680)], fill=(200, 200, 210), width=24); d.line([(330, 520), (470, 520)], fill=(120, 90, 40), width=18)

hound(); moths(); smiler(); echo()
celebrant("celebrant", (232, 92, 120)); celebrant("celebrant-host", (250, 205, 70), crown=True)
custodian()
emblem("wren-halloway", (90, 120, 110), (176, 156, 88), wren)
emblem("brother-amsel", (120, 70, 40), (255, 170, 60), amsel)
emblem("dagny-roe", (70, 80, 100), (180, 180, 190), dagny)
# cover image for the adventure
from PIL import Image as I
cover = I.open("./maps/01-waiting-halls.webp").crop((0, 0, 1600, 900)).convert("RGB")
dd = ImageDraw.Draw(cover)
from PIL import ImageFont
f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 120)
f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 46)
dd.rectangle([0, 560, 1600, 900], fill=(20, 18, 10))
dd.text((80, 590), "THE INTERSTICE", font=f1, fill=(236, 222, 160))
dd.text((86, 750), "A liminal descent for 5th–8th level characters", font=f2, fill=(190, 176, 120))
cover.save("./maps/cover.webp", quality=85)
print(sorted(os.listdir(OUT)))
