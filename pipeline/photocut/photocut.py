"""Photo Cut: the second visual format for the channel.

Where the Bold Contrast format draws flat vector scenes, this one grades real
photographs into the locked palette and cuts them fast. Nothing here may emit a
colour outside the palette: the duotone ramp, the cards and the caption plate
all pull from the four hexes below.

    render_photocut.py <spec.json> <key> <images.json> <timeline.json> <out.rgb>
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

NAVY  = (29, 53, 87)
PAPER = (241, 250, 238)
RED   = (230, 57, 70)
SKY   = (168, 218, 220)

W, H, FPS = 1080, 1920, 30

FONT_DIRS = ["/usr/share/fonts/truetype/higgsfield", "/usr/share/fonts/truetype/dejavu"]
FONT_NAMES = ["Metropolis-ExtraBold.ttf", "Metropolis-Bold.ttf", "DejaVuSans-Bold.ttf"]


def font_path():
    for d in FONT_DIRS:
        for n in FONT_NAMES:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise SystemExit("no bold font found")


_FP = None
_FCACHE = {}


def fnt(size):
    global _FP
    if _FP is None:
        _FP = font_path()
    if size not in _FCACHE:
        _FCACHE[size] = ImageFont.truetype(_FP, size)
    return _FCACHE[size]


# ---------------------------------------------------------------- duotone

def _ramp():
    """Navy in the shadows, sky through the mids, paper in the highlights."""
    stops = [(0.00, NAVY), (0.50, SKY), (1.00, PAPER)]
    out = []
    for i in range(256):
        x = i / 255.0
        for j in range(len(stops) - 1):
            a, ca = stops[j]
            b, cb = stops[j + 1]
            if a <= x <= b:
                t = (x - a) / (b - a)
                out.append(tuple(int(round(ca[k] + (cb[k] - ca[k]) * t)) for k in range(3)))
                break
    return out


RAMP = _ramp()


def grade(im):
    """Photograph in, palette-locked duotone out, contrast pushed for a phone."""
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=1)
    # S-curve: crush the shadows, lift the highlights, so shapes read in 0.5s.
    lut = [int(round(255 * (0.5 - 0.5 * math.cos(math.pi * (v / 255.0) ** 0.92)))) for v in range(256)]
    g = g.point(lut)
    r = g.point([RAMP[v][0] for v in range(256)])
    gg = g.point([RAMP[v][1] for v in range(256)])
    b = g.point([RAMP[v][2] for v in range(256)])
    return Image.merge("RGB", (r, gg, b))


# ---------------------------------------------------------------- ken burns

def kb_params(idx, variant):
    """Deterministic motion that never repeats the same move back to back."""
    moves = [
        (1.00, 1.14, 0.50, 0.50, 0.45, 0.55),   # push in
        (1.16, 1.02, 0.50, 0.50, 0.55, 0.45),   # pull out
        (1.10, 1.10, 0.38, 0.60, 0.50, 0.50),   # pan right
        (1.10, 1.10, 0.62, 0.40, 0.50, 0.50),   # pan left
        (1.02, 1.18, 0.44, 0.56, 0.58, 0.42),   # push up-right
        (1.18, 1.04, 0.58, 0.46, 0.42, 0.56),   # pull down-left
    ]
    return moves[(idx * 2 + variant * 3) % len(moves)]


def frame_from_photo(src, idx, variant, p):
    z0, z1, x0, x1, y0, y1 = kb_params(idx, variant)
    e = p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    cx = x0 + (x1 - x0) * e
    cy = y0 + (y1 - y0) * e
    sw, sh = src.size
    # Cover the 9:16 frame, then crop a window of 1/z of it around (cx, cy).
    scale = max(W / sw, H / sh) * z
    tw, th = int(sw * scale + 0.5), int(sh * scale + 0.5)
    big = src.resize((tw, th), Image.LANCZOS)
    left = int(round((tw - W) * cx))
    top = int(round((th - H) * cy))
    left = max(0, min(tw - W, left))
    top = max(0, min(th - H, top))
    return big.crop((left, top, left + W, top + H))


# ---------------------------------------------------------------- cards

def punch_card(bg, word, p):
    """A full-bleed colour card with one word. The rhythm break."""
    ground = RED if bg == "red" else NAVY
    ink = PAPER
    # Two frames of inverted flash on entry so the cut lands hard.
    if p < 0.06:
        ground, ink = PAPER, (RED if bg == "red" else NAVY)
    im = Image.new("RGB", (W, H), ground)
    d = ImageDraw.Draw(im)
    pop = min(1.0, p / 0.18)
    s = 0.88 + 0.12 * (pop * pop * (3 - 2 * pop))
    lines = word.split(" ")
    if len(lines) > 2:
        lines = [" ".join(lines[:len(lines) // 2]), " ".join(lines[len(lines) // 2:])]
    base = 200 if len(lines) == 1 else 150
    size = max(40, int(base * s))
    f = fnt(size)
    hs = [d.textbbox((0, 0), l, font=f)[3] for l in lines]
    total = sum(hs) + int(size * 0.16) * (len(lines) - 1)
    y = (H - total) // 2
    for l, lh in zip(lines, hs):
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), l, font=f, fill=ink)
        y += lh + int(size * 0.16)
    bar = int(size * 0.10)
    d.rectangle([W // 2 - 170, y + 60, W // 2 + 170, y + 60 + bar], fill=ink)
    return im


GAUGES = ["HEALTH", "WORK", "PLAY", "LOVE"]
# Stage 0 draws empty tracks, 1 adds labels, 2 fills, 3 flags play at zero.
GAUGE_VALUES = [
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.7, 0.3, 0.0, 0.7],
    [0.7, 0.3, 0.0, 0.7],
]
GAUGE_HOT = [[], [], [1], [2]]


def gauge_card(stage, p):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    vals = GAUGE_VALUES[stage]
    hot = GAUGE_HOT[stage]
    e = min(1.0, p / 0.45)
    e = e * e * (3 - 2 * e)
    x0, x1 = 150, 930
    top, bot = 420, 1040
    slot = (x1 - x0) / 4.0
    bw = int(slot * 0.52)
    for i in range(4):
        cx = int(x0 + slot * (i + 0.5))
        lx, rx = cx - bw // 2, cx + bw // 2
        d.rectangle([lx, top, rx, bot], outline=NAVY, width=8)
        v = vals[i] * e
        if v > 0.001:
            fh = int((bot - top - 16) * v)
            col = RED if i in hot else NAVY
            d.rectangle([lx + 8, bot - 8 - fh, rx - 8, bot - 8], fill=col)
        if stage >= 1:
            f = fnt(40)
            label = GAUGES[i]
            bb = d.textbbox((0, 0), label, font=f)
            d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], bot + 34), label, font=f,
                   fill=RED if i in hot else NAVY)
        if stage == 3 and i == 2:
            f = fnt(52)
            bb = d.textbbox((0, 0), "0", font=f)
            d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], bot - 90), "0", font=f, fill=RED)
    d.rectangle([150, 300, 930, 312], fill=NAVY)
    return im


# ---------------------------------------------------------------- captions

CAP_CY = int(H * 0.655)
CAP_MAXW = int(W * 0.78)


def wrap(words, f, draw):
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        txt = " ".join(t[0] for t in trial)
        if draw.textlength(txt, font=f) > CAP_MAXW and cur:
            lines.append(cur)
            cur = [w]
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


_capcache = {}


def caption_plate(text, em):
    """A paper plate with navy type and one red word. Same plate every beat, so
    the eye never has to hunt for it."""
    key = (text, em)
    if key in _capcache:
        return _capcache[key]
    scratch = Image.new("RGB", (10, 10))
    d0 = ImageDraw.Draw(scratch)
    ems = [w.lower().strip(".,'!?") for w in em.split()] if em else []
    words = [(w.upper(), w.lower().strip(".,'!?") in ems) for w in text.split()]
    size = 84
    while size > 40:
        f = fnt(size)
        lines = wrap(words, f, d0)
        if len(lines) <= 3:
            break
        size -= 6
    f = fnt(size)
    lines = wrap(words, f, d0)
    lh = int(size * 1.14)
    tw = max(int(d0.textlength(" ".join(t[0] for t in l), font=f)) for l in lines)
    th = lh * len(lines)
    padx, pady = 34, 26
    pw, ph = tw + padx * 2, th + pady * 2
    plate = Image.new("RGBA", (pw + 14, ph + 14), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rectangle([14, 14, 14 + pw, 14 + ph], fill=NAVY + (255,))       # hard drop shadow
    pd.rectangle([0, 0, pw, ph], fill=PAPER + (255,), outline=NAVY + (255,), width=6)
    y = pady
    for l in lines:
        txt = " ".join(t[0] for t in l)
        x = (pw - int(d0.textlength(txt, font=f))) // 2
        for w, hot in l:
            pd.text((x, y), w, font=f, fill=(RED if hot else NAVY) + (255,))
            x += int(d0.textlength(w + " ", font=f))
        y += lh
    _capcache[key] = plate
    return plate


def draw_caption(im, text, em, p):
    plate = caption_plate(text, em)
    pw, ph = plate.size
    rise = 1.0 - (1.0 - min(1.0, p / 0.10)) ** 2
    y = CAP_CY - ph // 2 + int((1 - rise) * 26)
    im.paste(plate, ((W - pw) // 2, y), plate)
    return im
