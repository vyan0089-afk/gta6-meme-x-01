#!/usr/bin/env python3
"""Build the GTA 6 x make.fun meme image (original PIL drawing).

Scene: golden-hour beach road in Tanjung Matahari. Raka's red car speeds
down the coast road, the make.fun ghost (official press-kit mark) rides
above it, a police helicopter spotlights the chase, 5 wanted stars.
Joke: waited 13 years for GTA 6; the ghost earned money on make.fun instead.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# ---------- sky gradient (sunset) ----------
top = (255, 122, 26)      # vivid orange
mid = (255, 78, 110)      # pink
bot = (88, 40, 120)       # purple dusk
HORIZON = 620
for y in range(HORIZON):
    t = y / HORIZON
    if t < 0.55:
        k = t / 0.55
        c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
    else:
        k = (t - 0.55) / 0.45
        c = tuple(int(mid[i] + (bot[i] - mid[i]) * k) for i in range(3))
    d.line([(0, y), (W, y)], fill=c)

# ---------- sun + glow ----------
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, a in ((190, 26), (150, 40), (110, 60)):
    gd.ellipse([700 - r, 540 - r, 700 + r, 540 + r], fill=(255, 214, 90, a))
img = Image.alpha_composite(img.convert("RGBA"), glow)
d = ImageDraw.Draw(img)
d.ellipse([700 - 68, 540 - 68, 700 + 68, 540 + 68], fill=(255, 236, 150))

# a few clouds (soft ellipses)
for (cx, cy, rx, ry, a) in ((180, 180, 130, 22, 70), (330, 250, 90, 16, 55),
                            (880, 150, 120, 20, 60), (120, 420, 110, 18, 50)):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 190, 200, a))

# ---------- ocean band ----------
for y in range(HORIZON, 700):
    t = (y - HORIZON) / 80
    c = tuple(int((38 + 120 * t) if i == 0 else (110 - 40 * t) if i == 1 else (170 - 60 * t))
              for i in range(3))
    d.line([(0, y), (W, y)], fill=c)
# sun reflection streak on the water
for y in range(HORIZON + 4, 700, 6):
    wdt = 26 + (y - HORIZON)
    d.line([(700 - wdt, y), (700 + wdt, y)], fill=(255, 220, 120), width=3)
# wave lines
for yy in (640, 662, 684):
    for x in range(0, W, 46):
        d.arc([x, yy - 6, x + 40, yy + 6], 200, 340, fill=(220, 240, 255), width=3)

# ---------- sand ----------
for y in range(700, H):
    t = (y - 700) / (H - 700)
    c = (232 - int(40 * t), 196 - int(50 * t), 122 - int(30 * t))
    d.line([(0, y), (W, y)], fill=c)
# sand speckles
import random
random.seed(7)
for _ in range(220):
    x = random.randint(0, W - 1)
    y = random.randint(710, H - 1)
    d.point((x, y), fill=(190, 150, 90))

# ---------- road (coast road, slight diagonal) ----------
d.polygon([(0, 780), (W, 716), (W, 852), (0, 916)], fill=(52, 52, 58))
d.polygon([(0, 780), (W, 716), (W, 726), (0, 790)], fill=(70, 70, 78))
d.polygon([(0, 906), (W, 842), (W, 852), (0, 916)], fill=(38, 38, 44))
# centre dashed line
for i in range(9):
    x0 = i * 118 - 20
    y0 = 806 - i * 7
    d.polygon([(x0, y0), (x0 + 62, y0 - 4), (x0 + 62, y0 + 4), (x0, y0 + 8)],
              fill=(250, 220, 90))

# ---------- palm trees (silhouettes) ----------
def palm(x, base_y, s):
    d.line([(x, base_y), (x + 14 * s, base_y - 150 * s)], fill=(43, 27, 18), width=int(12 * s))
    cx, cy = x + 14 * s, base_y - 150 * s
    for ang in (-160, -120, -80, -40, -5, 30):
        a = math.radians(ang)
        ex = cx + math.cos(a) * 95 * s
        ey = cy + math.sin(a) * 42 * s - 18 * s
        d.line([(cx, cy), (ex, ey)], fill=(43, 27, 18), width=int(8 * s))
        d.line([(cx, cy), (ex, ey + 26 * s)], fill=(43, 27, 18), width=int(5 * s))
palm(90, 760, 1.0)
palm(955, 726, 0.85)
palm(880, 736, 0.6)

# ---------- helicopter silhouette + spotlight ----------
def heli(x, y, s):
    d.ellipse([x, y, x + 92 * s, y + 34 * s], fill=(30, 30, 36))          # body
    d.polygon([(x + 88 * s, y + 10 * s), (x + 150 * s, y + 2 * s),
               (x + 150 * s, y + 14 * s), (x + 88 * s, y + 22 * s)], fill=(30, 30, 36))
    d.line([(x + 10 * s, y - 12 * s), (x + 86 * s, y - 12 * s)], fill=(30, 30, 36), width=6)
    d.line([(x + 40 * s, y + 34 * s), (x + 34 * s, y + 48 * s)], fill=(30, 30, 36), width=5)
    d.line([(x + 66 * s, y + 34 * s), (x + 74 * s, y + 48 * s)], fill=(30, 30, 36), width=5)
    d.line([(x + 30 * s, y + 48 * s), (x + 78 * s, y + 48 * s)], fill=(30, 30, 36), width=5)
heli(790, 250, 0.9)
beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(beam)
bd.polygon([(830, 300), (890, 300), (700, 760), (560, 760)], fill=(255, 250, 190, 60))
img = Image.alpha_composite(img, beam)
d = ImageDraw.Draw(img)

# ---------- red sports car (side view, facing right) ----------
def car(x0, y0, s):
    # y0 = ground line (wheel bottoms)
    # body
    d.polygon([(x0, y0 - 58 * s), (x0 + 60 * s, y0 - 66 * s), (x0 + 150 * s, y0 - 96 * s),
               (x0 + 300 * s, y0 - 100 * s), (x0 + 430 * s, y0 - 62 * s),
               (x0 + 470 * s, y0 - 40 * s), (x0 + 470 * s, y0 - 18 * s),
               (x0, y0 - 18 * s)], fill=(214, 28, 44))
    # cabin / windows
    d.polygon([(x0 + 165 * s, y0 - 92 * s), (x0 + 285 * s, y0 - 96 * s),
               (x0 + 330 * s, y0 - 62 * s), (x0 + 175 * s, y0 - 62 * s)],
              fill=(178, 224, 240))
    d.line([(x0 + 245 * s, y0 - 94 * s), (x0 + 245 * s, y0 - 62 * s)],
           fill=(214, 28, 44), width=int(6 * s))
    # lower shading + door line
    d.rectangle([x0, y0 - 26 * s, x0 + 470 * s, y0 - 18 * s], fill=(160, 16, 30))
    d.line([(x0 + 250 * s, y0 - 58 * s), (x0 + 250 * s, y0 - 24 * s)],
           fill=(160, 16, 30), width=3)
    # headlight + beam
    d.ellipse([x0 + 448 * s, y0 - 52 * s, x0 + 468 * s, y0 - 38 * s], fill=(255, 240, 140))
    # wheels
    for wx in (x0 + 95 * s, x0 + 375 * s):
        d.ellipse([wx - 40 * s, y0 - 40 * s, wx + 40 * s, y0 + 40 * s], fill=(18, 18, 20))
        d.ellipse([wx - 20 * s, y0 - 20 * s, wx + 20 * s, y0 + 20 * s], fill=(200, 200, 205))
        d.ellipse([wx - 8 * s, y0 - 8 * s, wx + 8 * s, y0 + 8 * s], fill=(120, 120, 125))
    # motion lines behind
    for i, yy in enumerate((y0 - 70 * s, y0 - 46 * s, y0 - 24 * s)):
        d.line([(x0 - 110 * s + i * 22, yy), (x0 - 18 * s, yy)],
               fill=(255, 255, 255, 200), width=6)
car(210, 800, 1.0)

# ---------- road sign: TANJUNG MATAHARI (drawn after the car so it covers the motion lines) ----------
d.polygon([(60, 684), (236, 684), (236, 748), (60, 748)], fill=(24, 90, 60))
d.rectangle([60, 684, 236, 748], outline=(255, 255, 255), width=4)
f_sign = ImageFont.truetype(FONT_BOLD, 23)
d.text((148, 690), "TANJUNG", font=f_sign, fill=(255, 255, 255), anchor="ma")
f_sign2 = ImageFont.truetype(FONT_BOLD, 19)
d.text((148, 718), "MATAHARI", font=f_sign2, fill=(255, 255, 255), anchor="ma")

# ---------- make.fun ghost (official press-kit mark) ----------
ghost = Image.open("assets/ghost.png").convert("RGBA")
ghost = ghost.resize((330, 330), Image.LANCZOS).rotate(-9, resample=Image.BICUBIC, expand=True)
img.paste(ghost, (600, 330), ghost)
d = ImageDraw.Draw(img)

# ---------- wanted stars (top-left) ----------
def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=(120, 70, 0), width=3)
for i in range(5):
    star(64 + i * 58, 252, 26, (255, 210, 40))

# ---------- meme text ----------
def big_text(y, lines, size, fill=(255, 255, 255)):
    f = ImageFont.truetype(FONT_BOLD, size)
    total = sum(d.textbbox((0, 0), ln, font=f)[3] - d.textbbox((0, 0), ln, font=f)[1] + 8
                for ln in lines)
    cy = y
    for ln in lines:
        d.text((W // 2, cy), ln, font=f, fill=fill, anchor="ma",
               stroke_width=7, stroke_fill=(0, 0, 0))
        cy += d.textbbox((0, 0), ln, font=f)[3] - d.textbbox((0, 0), ln, font=f)[1] + 8

big_text(18, ["MENUNGGU GTA 6", "SELAMA 13 TAHUN"], 76)
big_text(872, ["HANTU INI MALAH", "CUAN DI make.fun"], 66)

img.convert("RGB").save("meme.png", optimize=True)
print("saved meme.png")
from PIL import Image as _I
im = _I.open("meme.png")
print(im.size, im.mode, __import__("os").path.getsize("meme.png"), "bytes")
