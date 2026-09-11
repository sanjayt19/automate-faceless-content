#!/usr/bin/env python3
"""Bold Contrast scene library.

Every frame of every reel is drawn here. Four colours, no others. The caption
band is reserved: no scene may draw inside it, which is what guarantees that
burned captions always sit navy-on-paper.

A scene is a name plus numeric parameters. Two scenes with the same name can be
interpolated, which is how motion is produced: the renderer tweens the numbers
and draws a frame at each step, so a bar grows and a marker travels instead of
cutting from one still to the next.
"""

RED   = "#E63946"
PAPER = "#F1FAEE"
NAVY  = "#1D3557"
SKY   = "#A8DADC"

W, H = 1080, 1920

# Artwork may only occupy this box. Everything below it belongs to the captions
# and to the platforms' own interface.
ART_X0, ART_X1 = 140, 940
ART_Y0, ART_Y1 = 250, 1050
CAP_Y0, CAP_Y1 = 1100, 1560          # reserved, always bare paper


def _lerp(a, b, t):
    return a + (b - a) * t


def blend(s0, s1, t):
    """Interpolate two scenes of the same kind. Falls back to a hard cut."""
    if s1 is None or s0 is None or s0["kind"] != s1["kind"]:
        return s1 if t >= 0.5 else s0
    out = {"kind": s0["kind"]}
    for k in set(s0) | set(s1):
        if k == "kind":
            continue
        a, b = s0.get(k), s1.get(k)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            out[k] = _lerp(a, b, t)
        else:
            out[k] = b if t >= 0.5 else a
    return out


def _rule(y, w=10, c=NAVY):
    return f'<line x1="{ART_X0}" y1="{y}" x2="{ART_X1}" y2="{y}" stroke="{c}" stroke-width="{w}"/>'


def _frame_rules(accent_h=0.0):
    """The two hairlines that make every frame read as one publication."""
    s = [f'<rect x="{ART_X0}" y="{ART_Y0-96}" width="{ART_X1-ART_X0}" height="30" fill="{NAVY}"/>',
         _rule(ART_Y1)]
    if accent_h > 0.01:
        h = accent_h * (ART_Y1 - ART_Y0)
        s.append(f'<rect x="{ART_X0-34}" y="{ART_Y0}" width="18" height="{h:.1f}" fill="{RED}"/>')
    return "".join(s)


# ---------------------------------------------------------------- scene kinds

def stack(n=5, hi=-1, fill=0.0, **_):
    """n horizontal bars. Bars below `fill` are sky. Bar `hi` is red."""
    n = max(1, int(round(n)))
    top, gap = ART_Y0 + 20, 26
    bh = (ART_Y1 - 40 - top - gap * (n - 1)) / n
    out = []
    for i in range(n):
        y = top + i * (bh + gap)
        c = RED if i == int(round(hi)) else (SKY if i < fill * n else PAPER)
        out.append(f'<rect x="{ART_X0}" y="{y:.1f}" width="{ART_X1-ART_X0}" height="{bh:.1f}" '
                   f'fill="{c}" stroke="{NAVY}" stroke-width="10"/>')
    return "".join(out)


def grid(cols=5, rows=2, filled=0.0, boxed=0.0, **_):
    """A grid of cells. `filled` of them are sky. `boxed` draws a red bracket."""
    cols, rows = max(1, int(round(cols))), max(1, int(round(rows)))
    gap = 26
    s = min((ART_X1 - ART_X0 - gap * (cols - 1)) / cols,
            (ART_Y1 - ART_Y0 - 40 - gap * (rows - 1)) / rows)
    gw = cols * s + (cols - 1) * gap
    x0 = (W - gw) / 2
    y0 = ART_Y0 + 20 + max(0, (ART_Y1 - ART_Y0 - 40 - (rows * s + (rows - 1) * gap)) / 2)
    total = cols * rows
    k = filled * total
    out = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            x, y = x0 + c * (s + gap), y0 + r * (s + gap)
            col = SKY if i < k else PAPER
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" '
                       f'fill="{col}" stroke="{NAVY}" stroke-width="10"/>')
    if boxed > 0.01:
        bw = (x0 + boxed * gw) - (x0 - 24)
        out.append(f'<rect x="{x0-26:.1f}" y="{y0-26:.1f}" width="{max(0,bw):.1f}" '
                   f'height="{rows*s+(rows-1)*gap+52:.1f}" fill="none" stroke="{RED}" stroke-width="22"/>')
    return "".join(out)


def timeline(pos=0.5, gap0=-1.0, gap1=-1.0, marker=1.0, **_):
    """A line across the frame. Optional sky gap. A red marker travels along it."""
    y = (ART_Y0 + ART_Y1) / 2
    out = [f'<line x1="{ART_X0}" y1="{y}" x2="{ART_X1}" y2="{y}" stroke="{NAVY}" stroke-width="18"/>',
           f'<circle cx="{ART_X0}" cy="{y}" r="46" fill="{NAVY}"/>']
    if gap0 >= 0 and gap1 > gap0:
        x0, x1 = ART_X0 + gap0 * (ART_X1-ART_X0), ART_X0 + gap1 * (ART_X1-ART_X0)
        out.append(f'<rect x="{x0:.1f}" y="{y-90}" width="{x1-x0:.1f}" height="180" '
                   f'fill="{SKY}" stroke="{NAVY}" stroke-width="12"/>')
    if marker > 0.01:
        cx = ART_X0 + pos * (ART_X1-ART_X0)
        out.append(f'<circle cx="{cx:.1f}" cy="{y}" r="{92*marker:.1f}" fill="{RED}" '
                   f'stroke="{NAVY}" stroke-width="12"/>')
    return "".join(out)


def compare(left=0.5, right=0.5, hi=1, **_):
    """Two columns. The taller one makes the point; `hi` picks which is red."""
    base, maxh = ART_Y1 - 30, ART_Y1 - ART_Y0 - 80
    out = []
    for i, v in enumerate((left, right)):
        x = ART_X0 + 40 + i * 400
        h = max(10, v * maxh)
        c = RED if i == int(round(hi)) else SKY
        out.append(f'<rect x="{x}" y="{base-h:.1f}" width="320" height="{h:.1f}" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="12"/>')
    out.append(f'<line x1="{ART_X0}" y1="{base}" x2="{ART_X1}" y2="{base}" '
               f'stroke="{NAVY}" stroke-width="14"/>')
    return "".join(out)


def funnel(w0=1.0, w1=0.5, w2=0.15, hi=2, **_):
    """Three descending widths. The last is usually the red one."""
    out = []
    for i, v in enumerate((w0, w1, w2)):
        w = max(30, v * (ART_X1 - ART_X0))
        y = ART_Y0 + 30 + i * 250
        c = RED if i == int(round(hi)) else SKY
        out.append(f'<rect x="{(W-w)/2:.1f}" y="{y}" width="{w:.1f}" height="200" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="12"/>')
    return "".join(out)


def orbit(n=6, r=250, core=1.0, out_hi=-1, **_):
    """A red core with sky satellites. One satellite may be red."""
    import math
    n = max(1, int(round(n)))
    cx, cy = 540, (ART_Y0 + ART_Y1) / 2
    out = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        c = RED if i == int(round(out_hi)) else SKY
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="76" fill="{c}" stroke="{NAVY}" stroke-width="12"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{max(6,core*180):.1f}" fill="{RED}" '
               f'stroke="{NAVY}" stroke-width="14"/>')
    return "".join(out)


def split(ratio=0.5, **_):
    """The artwork box divided. Sky on the left, red on the right."""
    x = ART_X0 + ratio * (ART_X1 - ART_X0)
    y0, hh = ART_Y0 + 20, ART_Y1 - ART_Y0 - 40
    return (f'<rect x="{ART_X0}" y="{y0}" width="{max(0,x-ART_X0):.1f}" height="{hh}" fill="{SKY}" '
            f'stroke="{NAVY}" stroke-width="12"/>'
            f'<rect x="{x:.1f}" y="{y0}" width="{max(0,ART_X1-x):.1f}" height="{hh}" fill="{RED}" '
            f'stroke="{NAVY}" stroke-width="12"/>')


def branch(n=3, hi=0, spread=1.0, **_):
    """One route splitting into n. The chosen one is red."""
    n = max(2, int(round(n)))
    x0, y0 = ART_X0 + 20, (ART_Y0 + ART_Y1) / 2
    out = [f'<circle cx="{x0}" cy="{y0}" r="52" fill="{NAVY}"/>']
    for i in range(n):
        dy = (i - (n - 1) / 2) * 300 * spread
        y1 = y0 + dy
        c = RED if i == int(round(hi)) else SKY
        wdt = 34 if i == int(round(hi)) else 20
        out.append(f'<path d="M{x0} {y0} C 500 {y0}, 580 {y1:.1f}, 800 {y1:.1f}" '
                   f'fill="none" stroke="{c}" stroke-width="{wdt}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{ART_X1-20}" cy="{y1:.1f}" r="70" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="12"/>')
    return "".join(out)


def single(size=1.0, **_):
    """One red disc. Maximum emphasis, used sparingly."""
    return (f'<circle cx="540" cy="{(ART_Y0+ART_Y1)/2:.0f}" r="{max(8,size*372):.1f}" '
            f'fill="{RED}" stroke="{NAVY}" stroke-width="16"/>')


def bigfig(value=60.0, bar=0.6, **_):
    """A figure the script actually says, with a bar showing the same quantity."""
    v = int(round(value))
    wdt = ART_X1 - ART_X0
    return (f'<text x="540" y="{ART_Y0+390}" font-family="Archivo, DejaVu Sans, sans-serif" '
            f'font-weight="800" font-size="400" text-anchor="middle" fill="{RED}">{v}%</text>'
            f'<rect x="{ART_X0}" y="{ART_Y1-190}" width="{wdt}" height="90" fill="{SKY}" '
            f'stroke="{NAVY}" stroke-width="12"/>'
            f'<rect x="{ART_X0}" y="{ART_Y1-190}" width="{max(0,bar*wdt):.1f}" height="90" '
            f'fill="{RED}" stroke="{NAVY}" stroke-width="12"/>')


KINDS = {"stack": stack, "grid": grid, "timeline": timeline, "compare": compare,
         "funnel": funnel, "orbit": orbit, "split": split, "branch": branch,
         "single": single, "bigfig": bigfig}


def render_svg(scene):
    body = KINDS[scene["kind"]](**{k: v for k, v in scene.items() if k != "kind"})
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
            f'{_frame_rules(scene.get("accent", 0.0))}'
            f'{body}'
            f'</svg>')


if __name__ == "__main__":
    import sys
    demo = {"kind": sys.argv[1] if len(sys.argv) > 1 else "stack"}
    print(render_svg(demo))
