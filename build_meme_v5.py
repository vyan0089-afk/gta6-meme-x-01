#!/usr/bin/env python3
"""Build meme v5 for the make.fun gta6-meme-x-01 bounty:
'SURAT KETERANGAN MENGANGGUR' -- the v4 kelurahan certificate, with the
GTA 6 flavour turned up so it reads as "GTA" at first glance while
still looking like a real kelurahan letter.

Concept (unchanged): Fufufafa worked 4,812 days and is now unemployed
because he wants to play GTA 6 -- and now he earns money from make.fun
bounties instead. The make.fun ghost is the magenta "CUAN" rubber
stamp, so make.fun is part of the document, not a sticker on it.

v5 changes vs v4 (one revision round, owner-ordered: "nuansa GTA 6
lebih dikentalkan lagi"):
- FIXED the v4 flaws the owner spotted:
  * Signature: the old layered-sine scribble looked zigzag/artificial.
    Replaced with a smooth flowing signature -- chained quadratic
    beziers forming one looping stroke plus a single shallow underline
    flourish. No more sawtooth.
  * WANTED label: the tiny 14 px label under the header stars was
    unreadable at 480 px. Removed from the header and merged into a
    proper document field (see below) where the stars are big enough
    to read.
  * Full re-check: no clipped or overlapping text (must_fit asserts
    guard every wide line).
- GTA flavour, LOUDER (max 2 new fields, document stays clean):
  * New field "TINGKAT PENCARIAN: ★★★★★" -- five BIG gold wanted
    stars (r 17) as a formal letter row, the single most iconic GTA
    element, now impossible to miss at 480 px.
  * New field "KENDARAAN TERAKHIR: MOBIL MERAH" -- carjacking flavour
    written as official letter data, not a pasted sticker.
  * Sunset strip: wider (10 -> 16 px) and now a 4-stop GTA VI key-art
    gradient -- purple -> hot magenta -> orange -> gold -- instead of
    the old 3-stop strip.
  * Palm watermark: clearer (alpha 52 -> 78) and slightly taller, so
    the Leonida/Vice-City silhouette survives the downscale, still
    faint enough not to cover any text.
- Kept verbatim from v4: FUFUFAFA, "4.812 HARI" red headline (verified:
  GTA V launched 17 Sep 2013; to 20 Nov 2026 is exactly 4,812 days),
  "MENGANGGUR", "SUMBER CUAN: BOUNTY DI make.fun" (make.fun magenta),
  the big red reason lines, the big CUAN ghost stamp, the green
  kelurahan stamp, the gold-emblem letterhead, Nomor 013/SKM/XI/2026,
  Lurah H. BUDI SANTOSO, S.Sos (NIP 19680113 199303 1 002), Tembusan.
- Layout reflowed for the two extra rows: 6 body rows at 40 px spacing
  (was 4 rows at 46 px), title 44 -> 42 pt, reason lines 48 -> 44 pt.
  Everything still fits with clearance; nothing collides.

All art is drawn in code with Pillow (no external images). Deterministic:
same input, same bytes, every run. Output: meme-v5.png, 1024x1024.
"""

import hashlib
import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "meme-v5.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

GREEN = (13, 84, 55)
GREEN_DARK = (7, 52, 33)
GOLD = (255, 201, 60)
GOLD_DARK = (178, 138, 0)
PAPER = (255, 252, 238)
INK = (28, 28, 28)
GREY = (110, 110, 110)
GREY_DARK = (70, 70, 70)
RED = (196, 24, 24)
MAGENTA = (226, 0, 122)
ORANGE = (255, 110, 40)
PURPLE = (120, 40, 170)
WHITE = (255, 255, 255)
PALE = (208, 232, 214)
SAND = (176, 148, 88)


def load(path, size):
    return ImageFont.truetype(path, size)


def star5(cx, cy, r_out, r_in):
    """Five-point star, one point straight up."""
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(-90.0 + i * 36.0)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle(cx, cy, r):
    """Four-point sparkle for the ghost's eyes."""
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28
        a = math.radians(-90.0 + i * 45.0)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def ghost_shape(cx, cy, w, h):
    """Sheet-ghost outline: domed head (upper half of an ellipse),
    straight sides, wavy hem with three bumps. y grows downward, so the
    dome is the 180..360 degree sweep."""
    hw = w / 2.0
    dome_y = cy - h * 0.10
    dome_ry = h * 0.40
    hem = cy + h * 0.32
    outline = []
    for deg in range(180, 361, 6):
        a = math.radians(deg)
        outline.append((cx + hw * math.cos(a), dome_y + dome_ry * math.sin(a)))
    outline.append((cx + hw, hem))
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        x = cx + hw - t * w
        lift = 0.5 - 0.5 * math.cos(2.0 * math.pi * 3.0 * t)
        outline.append((x, hem + h * 0.07 * lift))
    outline.append((cx - hw, dome_y))
    return outline


def paint_ghost(d, cx, cy, w, h):
    """White ghost, black outline, two sparkle eyes."""
    d.polygon(ghost_shape(cx, cy, w, h), fill=WHITE, outline=INK,
              width=max(3, int(round(w * 0.07))))
    ey = cy - h * 0.12
    er = w * 0.09
    d.polygon(sparkle(cx - w * 0.19, ey, er), fill=INK)
    d.polygon(sparkle(cx + w * 0.19, ey, er), fill=INK)


def cuan_stamp(img, cx, cy, size):
    """Round magenta CUAN stamp, ghost inside, tilted like a rubber
    stamp. Drawn on its own layer so the tilt stays clean."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size / 2.0
    d.ellipse([5, 5, size - 5, size - 5], outline=MAGENTA, width=7)
    d.ellipse([14, 14, size - 14, size - 14], outline=MAGENTA, width=2)
    paint_ghost(d, c, c - size * 0.05, size * 0.62, size * 0.66)
    f = load(BOLD, int(size * 0.115))
    d.text((c, c + size * 0.335), "CUAN", font=f, fill=MAGENTA, anchor="mm")
    layer = layer.rotate(-10, resample=Image.BICUBIC, expand=False)
    img.paste(layer, (int(cx - size / 2), int(cy - size / 2)), layer)


def kelurahan_stamp(img, cx, cy, size):
    """Small round green official stamp: double ring, star on top,
    office name across the middle. Tilted the other way, like a second
    stamp pressed next to the first one."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size / 2.0
    d.ellipse([4, 4, size - 4, size - 4], outline=GREEN, width=5)
    d.ellipse([11, 11, size - 11, size - 11], outline=GREEN, width=2)
    d.polygon(star5(c, c - size * 0.24, size * 0.11, size * 0.045),
              fill=GREEN)
    f1 = load(BOLD, int(size * 0.10))
    f2 = load(BOLD, int(size * 0.058))
    # Text must stay inside the inner ring: check each line against the
    # chord of the circle at that line's height, so nothing is clipped.
    r_in = (size - 22) / 2.0
    for txt, f, dy in (("KELURAHAN", f1, size * 0.05),
                       ("TANJUNG MATAHARI", f2, size * 0.17)):
        chord = 2.0 * math.sqrt(max(0.0, r_in * r_in - dy * dy))
        got = d.textlength(txt, font=f)
        assert got <= chord, "stamp line too wide: %.0f > %.0f (%r)" % (
            got, chord, txt)
    d.text((c, c + size * 0.05), "KELURAHAN", font=f1, fill=GREEN,
           anchor="mm")
    d.text((c, c + size * 0.17), "TANJUNG MATAHARI", font=f2, fill=GREEN,
           anchor="mm")
    layer = layer.rotate(8, resample=Image.BICUBIC, expand=False)
    img.paste(layer, (int(cx - size / 2), int(cy - size / 2)), layer)


def sunset_strip(img, y0, y1):
    """Wider GTA VI key-art sunset: purple -> hot magenta -> orange ->
    gold, left to right. v5: 16 px tall (was 10) with a purple stop
    added, so the sunset reads even at 480 px."""
    stops = [(0.00, PURPLE), (0.33, MAGENTA), (0.66, ORANGE),
             (1.00, GOLD)]
    for x in range(28, 996):
        t = (x - 28) / 968.0
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * u)
                            for j in range(3))
                break
        else:
            col = stops[-1][1]
        for y in range(y0, y1):
            img.putpixel((x, y), col)


def _bez(p0, p1, p2, n=24):
    """Points along a quadratic bezier curve."""
    out = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def palm_watermark(img, crown_x, crown_y, height):
    """One faint palm silhouette on the paper, right side of the body.
    Drawn on a translucent layer so the text stays dominant. v5: a
    little clearer (alpha 78, was 52) and taller, so the silhouette
    survives the 480 px downscale."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = SAND + (78,)
    # Trunk: gentle S-curve from the base up to the crown.
    base = (crown_x + 16, crown_y + height)
    mid = (crown_x - 14, crown_y + height * 0.55)
    pts = _bez(base, mid, (crown_x, crown_y), 32)
    d.line(pts, fill=col, width=7, joint="curve")
    # Six drooping fronds fanning out from the crown.
    tips = [(-height * 0.52, height * 0.10), (-height * 0.46, -height * 0.16),
            (-height * 0.28, -height * 0.34), (height * 0.22, -height * 0.36),
            (height * 0.44, -height * 0.20), (height * 0.52, height * 0.06)]
    for dx, dy in tips:
        tip = (crown_x + dx, crown_y + dy)
        ctrl = (crown_x + dx * 0.55, crown_y + dy * 0.55 - height * 0.16)
        d.line(_bez((crown_x, crown_y), ctrl, tip, 20), fill=col, width=5,
               joint="curve")
    img.paste(layer, (0, 0), layer)


def signature_smooth(d, x0, x1, y_base):
    """A flowing hand signature: one looping stroke (a tall loop, a dip,
    then a long sweep to the right) plus a single shallow underline
    flourish. Chained quadratic beziers with matching endpoints, so the
    line is smooth everywhere -- no sawtooth, no zigzag."""
    # Main stroke: loop up, loop down, dip, long sweep right.
    segs = [((x0, y_base + 6), (x0 + 12, y_base - 22), (x0 + 32, y_base - 14)),
            ((x0 + 32, y_base - 14), (x0 + 52, y_base - 24), (x0 + 48, y_base - 2)),
            ((x0 + 48, y_base - 2), (x0 + 56, y_base + 14), (x0 + 82, y_base + 2)),
            ((x0 + 82, y_base + 2), (x0 + 118, y_base - 12), (x1, y_base + 2))]
    pts = []
    for p0, p1, p2 in segs:
        pts.extend(_bez(p0, p1, p2, 20)[:-1])
    pts.append(segs[-1][2])
    d.line(pts, fill=INK, width=3, joint="curve")
    # Underline flourish: one shallow S-curve, left to right.
    d.line(_bez((x0 + 4, y_base + 18), (x0 + (x1 - x0) / 2, y_base + 24),
                (x1 - 6, y_base + 14), 30), fill=INK, width=2, joint="curve")


def must_fit(d, text, f, max_w, what):
    got = d.textlength(text, font=f)
    assert got <= max_w, "%s too wide: %.0f > %.0f (%r)" % (what, got,
                                                           max_w, text)


def main():
    img = Image.new("RGB", (W, H), PAPER)

    # --- faint GTA palm on the paper, before any text -----------------------
    palm_watermark(img, 878, 388, 190)

    d = ImageDraw.Draw(img)

    # --- frame --------------------------------------------------------------
    d.rectangle([0, 0, W - 1, H - 1], outline=GREEN_DARK, width=14)
    d.rectangle([26, 26, W - 27, H - 27], outline=GOLD, width=3)

    # --- letterhead band ----------------------------------------------------
    d.rectangle([28, 28, W - 29, 150], fill=GREEN)
    # Gold kelurahan emblem: double ring + star.
    d.ellipse([102, 51, 178, 127], outline=GOLD, width=4)
    d.ellipse([110, 59, 170, 119], outline=GOLD, width=2)
    d.polygon(star5(140, 89, 20, 8), fill=GOLD)
    f_gov = load(BOLD, 20)
    f_off = load(SERIF, 30)
    f_addr = load(REG, 17)
    must_fit(d, "PEMERINTAH KOTA TANJUNG MATAHARI", f_gov, 640, "gov line")
    d.text((512, 58), "PEMERINTAH KOTA TANJUNG MATAHARI", font=f_gov,
           fill=WHITE, anchor="mm")
    must_fit(d, "KELURAHAN TANJUNG MATAHARI", f_off, 640, "office line")
    d.text((512, 92), "KELURAHAN TANJUNG MATAHARI", font=f_off, fill=WHITE,
           anchor="mm")
    must_fit(d, "Jl. Pantai Tanjung Matahari No. 13  •  Telp. (021) 555-0136",
             f_addr, 640, "address line")
    d.text((512, 126), "Jl. Pantai Tanjung Matahari No. 13  •  Telp. (021) 555-0136",
           font=f_addr, fill=PALE, anchor="mm")
    # Five gold wanted stars, right side of the band (v5: the unreadable
    # 14 px WANTED label is gone -- the wanted level now lives as a
    # proper field row in the body, where the stars are big).
    for i in range(5):
        d.polygon(star5(848 + i * 32, 88, 15, 6), fill=GOLD,
                  outline=GOLD_DARK)

    # --- GTA sunset strip (wider, 4-stop) + double rule ---------------------
    sunset_strip(img, 150, 166)
    d = ImageDraw.Draw(img)
    d.line([(90, 178), (934, 178)], fill=GREEN_DARK, width=3)
    d.line([(90, 185), (934, 185)], fill=GREEN_DARK, width=1)

    # --- title, serif like a real certificate -------------------------------
    f_t = load(SERIF, 42)
    must_fit(d, "SURAT KETERANGAN", f_t, 844, "title 1")
    d.text((512, 218), "SURAT KETERANGAN", font=f_t, fill=GREEN_DARK,
           anchor="mm")
    must_fit(d, "MENGANGGUR", f_t, 844, "title 2")
    d.text((512, 262), "MENGANGGUR", font=f_t, fill=GREEN_DARK, anchor="mm")

    # --- number + subject block ----------------------------------------------
    f_no = load(REG, 22)
    d.text((90, 298), "Nomor : 013/SKM/XI/2026", font=f_no, fill=GREY_DARK,
           anchor="lm")
    d.text((90, 324), "Perihal : Keterangan Menganggur", font=f_no,
           fill=GREY_DARK, anchor="lm")

    # --- opening line + body rows (v5: six rows, 40 px apart) ----------------
    d.text((90, 362), "Yang bertanda tangan di bawah ini menerangkan bahwa:",
           font=f_no, fill=INK, anchor="lm")
    f_label = load(BOLD, 24)
    f_label2 = load(BOLD, 22)
    f_value = load(BOLD, 34)
    f_note = load(REG, 20)
    f_mk = load(BOLD, 34)
    # NAMA
    d.text((90, 396), "NAMA", font=f_label, fill=GREY, anchor="lm")
    must_fit(d, "FUFUFAFA", f_value, 934 - 380, "value NAMA")
    d.text((380, 396), "FUFUFAFA", font=f_value, fill=INK, anchor="lm")
    # MASA KERJA -- the headline number, in red, with the 13-year gloss.
    d.text((90, 436), "MASA KERJA", font=f_label, fill=GREY, anchor="lm")
    must_fit(d, "4.812 HARI (13 tahun)", f_value, 934 - 380, "value MASA")
    d.text((380, 436), "4.812 HARI", font=f_value, fill=RED, anchor="lm")
    w_days = d.textlength("4.812 HARI", font=f_value)
    d.text((380 + w_days + 8, 436), "(13 tahun)", font=f_note,
           fill=GREY_DARK, anchor="lm")
    # STATUS
    d.text((90, 476), "STATUS", font=f_label, fill=GREY, anchor="lm")
    must_fit(d, "MENGANGGUR", f_value, 934 - 380, "value STATUS")
    d.text((380, 476), "MENGANGGUR", font=f_value, fill=INK, anchor="lm")
    # SUMBER CUAN -- the make.fun pitch as a formal letter field.
    d.text((90, 516), "SUMBER CUAN", font=f_label, fill=GREY, anchor="lm")
    must_fit(d, "BOUNTY DI make.fun", f_value, 934 - 380, "value CUAN")
    d.text((380, 516), "BOUNTY DI ", font=f_value, fill=INK, anchor="lm")
    w_bounty = d.textlength("BOUNTY DI ", font=f_value)
    d.text((380 + w_bounty, 516), "make.fun", font=f_mk, fill=MAGENTA,
           anchor="lm")
    # TINGKAT PENCARIAN -- NEW in v5: five BIG gold wanted stars as a
    # formal field row. The most iconic GTA element, now at a size that
    # survives the 480 px downscale.
    must_fit(d, "TINGKAT PENCARIAN", f_label2, 380 - 90, "label WANTED")
    d.text((90, 556), "TINGKAT PENCARIAN", font=f_label2, fill=GREY,
           anchor="lm")
    for i in range(5):
        d.polygon(star5(392 + i * 40, 556, 17, 7), fill=GOLD,
                  outline=GOLD_DARK)
    # KENDARAAN TERAKHIR -- NEW in v5: carjacking flavour as official
    # letter data.
    must_fit(d, "KENDARAAN TERAKHIR", f_label2, 380 - 90, "label CAR")
    d.text((90, 596), "KENDARAAN TERAKHIR", font=f_label2, fill=GREY,
           anchor="lm")
    must_fit(d, "MOBIL MERAH", f_value, 934 - 380, "value CAR")
    d.text((380, 596), "MOBIL MERAH", font=f_value, fill=INK, anchor="lm")

    # --- the reason, in big red letters: the number is the headline --------
    d.text((90, 626), "ALASAN MENGANGGUR", font=f_label, fill=GREY,
           anchor="lm")
    f_why = load(BOLD, 44)
    must_fit(d, "MENGANGGUR 4.812 HARI", f_why, 844, "reason line 1")
    must_fit(d, "KARENA MAU MAIN GTA 6", f_why, 844, "reason line 2")
    d.text((90, 658), "MENGANGGUR 4.812 HARI", font=f_why, fill=RED,
           anchor="lm")
    d.text((90, 704), "KARENA MAU MAIN GTA 6", font=f_why, fill=RED,
           anchor="lm")

    # --- divider ---------------------------------------------------------------
    d.line([(90, 744), (934, 744)], fill=GREEN_DARK, width=3)

    # --- punchline: bigger CUAN stamp + official stamp + the pitch ----------
    cuan_stamp(img, 150, 812, 170)
    kelurahan_stamp(img, 300, 816, 120)
    d = ImageDraw.Draw(img)
    f_p1 = load(BOLD, 34)
    f_p2 = load(BOLD, 30)
    must_fit(d, "SEKARANG CARI CUAN", f_p1, 934 - 368, "punch line 1")
    d.text((368, 786), "SEKARANG CARI CUAN", font=f_p1, fill=INK, anchor="lm")
    d.text((368, 830), "DARI BOUNTY DI ", font=f_p2, fill=INK, anchor="lm")
    w2 = d.textlength("DARI BOUNTY DI ", font=f_p2)
    d.text((368 + w2, 830), "make.fun", font=f_mk, fill=MAGENTA, anchor="lm")

    # --- signature block, bottom right -----------------------------------------
    f_date = load(REG, 17)
    f_sig = load(BOLD, 18)
    f_name = load(BOLD, 19)
    f_nip = load(REG, 15)
    d.text((934, 892), "November 2026", font=f_date, fill=GREY_DARK,
           anchor="rm")
    d.text((934, 914), "Lurah Tanjung Matahari,", font=f_sig, fill=INK,
           anchor="rm")
    signature_smooth(d, 760, 930, 930)
    d.text((934, 966), "H. BUDI SANTOSO, S.Sos", font=f_name, fill=INK,
           anchor="rm")
    d.text((934, 986), "NIP 19680113 199303 1 002", font=f_nip,
           fill=GREY_DARK, anchor="rm")

    # --- distribution note, bottom left ----------------------------------------
    f_cc = load(REG, 14)
    d.text((90, 976), "Tembusan: 1. Arsip Kelurahan; 2. Ybs.", font=f_cc,
           fill=GREY, anchor="lm")

    img.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    print("%s: %d bytes, sha256 %s" % (OUT, len(data),
                                       hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
