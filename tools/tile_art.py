import os
from PIL import Image, ImageDraw, ImageFont
OUT = "./tiles"; os.makedirs(OUT, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n): return ImageFont.truetype(FB, n)
S = 400  # drawn at 4x, saved at 100px per grid square equivalents

def save(im, name, size):
    im.resize(size, Image.LANCZOS).save(f"{OUT}/{name}.webp", quality=90)

def ctext(d, cx, y, text, f, fill):
    w = d.textlength(text, font=f); d.text((cx - w / 2, y), text, font=f, fill=fill)

# Stairwell door (seen from above, set into the wall)
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rectangle([20, 0, 380, 150], fill=(120, 126, 130), outline=(60, 62, 66), width=12)
d.rectangle([40, 0, 360, 130], fill=(150, 156, 160))
d.rectangle([60, 70, 340, 100], fill=(200, 200, 200), outline=(90, 90, 90), width=5)
d.rectangle([110, 160, 290, 230], fill=(240, 240, 230), outline=(40, 40, 40), width=5)
ctext(d, 200, 175, "STAFF ONLY", font(30), (20, 20, 20))
d.polygon([(130, 250), (270, 250), (200, 330)], fill=(240, 240, 230, 160))
save(im, "stairwell-door", (100, 100))

# Open great drain
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.ellipse([10, 10, 390, 390], fill=(12, 10, 10), outline=(90, 90, 88), width=18)
for k in range(5):
    y = 90 + k * 55; d.line([(150, y), (250, y)], fill=(130, 110, 80), width=12)
d.line([(150, 70), (150, 340)], fill=(110, 96, 70), width=10); d.line([(250, 70), (250, 340)], fill=(110, 96, 70), width=10)
d.ellipse([170, 170, 230, 230], outline=(240, 180, 200, 120), width=4)
save(im, "great-drain-open", (100, 100))

# Tobin's satchel
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([60, 110, 340, 320], 30, fill=(110, 70, 40), outline=(50, 30, 15), width=10)
d.rounded_rectangle([60, 110, 340, 210], 30, fill=(130, 84, 48), outline=(50, 30, 15), width=10)
for x in (130, 270): d.rectangle([x - 18, 190, x + 18, 240], fill=(212, 175, 55), outline=(120, 90, 20), width=4)
d.rectangle([150, 80, 250, 110], fill=(236, 230, 210))
d.arc([110, 30, 290, 200], 200, 340, fill=(60, 36, 18), width=14)
save(im, "tobins-satchel", (100, 100))

# Exit door, Celebration
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rectangle([40, 240, 360, 400], fill=(200, 160, 110), outline=(120, 70, 40), width=10)
d.line([(200, 240), (200, 400)], fill=(120, 70, 40), width=8)
d.rectangle([30, 20, 370, 200], fill=(255, 240, 245), outline=(232, 92, 120), width=8)
ctext(d, 200, 45, "PLEASE HAVE", font(40), (120, 40, 60)); ctext(d, 200, 95, "YOUR PASS", font(40), (120, 40, 60))
ctext(d, 200, 145, "READY", font(40), (120, 40, 60))
save(im, "exit-door", (100, 100))

# Ticket dispenser
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.ellipse([100, 100, 300, 300], fill=(150, 30, 40), outline=(212, 175, 55), width=12)
d.rectangle([170, 40, 230, 110], fill=(240, 234, 214), outline=(160, 150, 120), width=4)
ctext(d, 200, 165, "TAKE", font(36), (240, 230, 200)); ctext(d, 200, 205, "A NUMBER", font(28), (240, 230, 200))
save(im, "ticket-dispenser", (100, 100))

# Guest pass (item icon)
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.line([(200, 0), (120, 120)], fill=(232, 92, 120), width=16); d.line([(200, 0), (280, 120)], fill=(232, 92, 120), width=16)
d.rounded_rectangle([70, 110, 330, 330], 24, fill=(212, 175, 55), outline=(120, 90, 20), width=10)
ctext(d, 200, 150, "GUEST", font(52), (90, 60, 10)); ctext(d, 200, 215, "PASS", font(52), (90, 60, 10))
d.ellipse([180, 280, 220, 320], fill=(232, 92, 120))
save(im, "guest-pass", (200, 200))

# GM control buttons
def control(name, label, sub, col):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, 390, 390], 50, fill=(20, 20, 24, 235), outline=col, width=16)
    ctext(d, 200, 50, "GM", font(70), col)
    for i, line in enumerate(label.split("\n")): ctext(d, 200, 150 + i * 62, line, font(54), (240, 240, 240))
    ctext(d, 200, 320, sub, font(30), (170, 170, 170))
    save(im, name, (100, 100))
control("gm-lights-out", "LIGHTS\nOUT", "double-click", (255, 210, 90))
control("gm-open-drain", "OPEN\nDRAIN", "double-click", (120, 200, 255))
control("gm-now-serving", "NOW\nSERVING", "double-click", (140, 230, 140))
control("gm-approve", "APPROVE\nFORM", "double-click", (255, 120, 120))
print(sorted(os.listdir(OUT)))
