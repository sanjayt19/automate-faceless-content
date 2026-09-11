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


def _rule(y, w=6, c=NAVY):
    return f'<line x1="{ART_X0}" y1="{y}" x2="{ART_X1}" y2="{y}" stroke="{c}" stroke-width="{w}"/>'


def _frame_rules(accent_h=0.0):
    """The two hairlines that make every frame read as one publication."""
    s = [_rule(ART_Y0), _rule(ART_Y1)]
    if accent_h > 0.01:
        h = accent_h * (ART_Y1 - ART_Y0)
        s.append(f'<rect x="{ART_X0}" y="{ART_Y0}" width="10" height="{h:.1f}" fill="{RED}"/>')
    return "".join(s)


# ---------------------------------------------------------------- scene kinds

def stack(n=5, hi=-1, fill=0.0, **_):
    """n horizontal bars. Bars below `fill` are sky. Bar `hi` is red."""
    n = max(1, int(round(n)))
    top, gap = 340, 26
    bh = min(132, (ART_Y1 - 60 - top - gap * (n - 1)) / n)
    out = []
    for i in range(n):
        y = top + i * (bh + gap)
        c = RED if i == int(round(hi)) else (SKY if i < fill * n else PAPER)
        out.append(f'<rect x="196" y="{y:.1f}" width="708" height="{bh:.1f}" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="6"/>')
    return "".join(out)


def grid(cols=5, rows=2, filled=0.0, boxed=0.0, **_):
    """A grid of cells. `filled` of them are sky. `boxed` draws a red bracket."""
    cols, rows = max(1, int(round(cols))), max(1, int(round(rows)))
    s, gap = 108, 40
    gw = cols * s + (cols - 1) * gap
    x0 = (W - gw) / 2
    y0 = 360
    total = cols * rows
    k = filled * total
    out = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            x, y = x0 + c * (s + gap), y0 + r * (s + gap)
            col = SKY if i < k else PAPER
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" fill="{col}" '
                       f'stroke="{NAVY}" stroke-width="7"/>')
    if boxed > 0.01:
        bw = (x0 + boxed * gw) - (x0 - 24)
        out.append(f'<rect x="{x0-24:.1f}" y="{y0-24:.1f}" width="{max(0,bw):.1f}" '
                   f'height="{rows*s+(rows-1)*gap+48:.1f}" fill="none" stroke="{RED}" stroke-width="14"/>')
    return "".join(out)


def timeline(pos=0.5, gap0=-1.0, gap1=-1.0, marker=1.0, **_):
    """A line across the frame. Optional sky gap. A red marker travels along it."""
    y = 700
    out = [f'<line x1="200" y1="{y}" x2="880" y2="{y}" stroke="{NAVY}" stroke-width="8"/>',
           f'<circle cx="200" cy="{y}" r="26" fill="{NAVY}"/>']
    if gap0 >= 0 and gap1 > gap0:
        x0, x1 = 200 + gap0 * 680, 200 + gap1 * 680
        out.append(f'<rect x="{x0:.1f}" y="{y-38}" width="{x1-x0:.1f}" height="76" '
                   f'fill="{SKY}" stroke="{NAVY}" stroke-width="7"/>')
    if marker > 0.01:
        cx = 200 + pos * 680
        out.append(f'<circle cx="{cx:.1f}" cy="{y}" r="{34*marker:.1f}" fill="{RED}" '
                   f'stroke="{NAVY}" stroke-width="7"/>')
    return "".join(out)


def compare(left=0.5, right=0.5, hi=1, **_):
    """Two columns. The taller one makes the point; `hi` picks which is red."""
    base, maxh = 1000, 600
    out = []
    for i, v in enumerate((left, right)):
        x = 250 + i * 340
        h = max(8, v * maxh)
        c = RED if i == int(round(hi)) else SKY
        out.append(f'<rect x="{x}" y="{base-h:.1f}" width="240" height="{h:.1f}" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="7"/>')
    out.append(f'<line x1="200" y1="{base}" x2="880" y2="{base}" stroke="{NAVY}" stroke-width="8"/>')
    return "".join(out)


def funnel(w0=1.0, w1=0.5, w2=0.15, hi=2, **_):
    """Three descending widths. The last is usually the red one."""
    out = []
    for i, v in enumerate((w0, w1, w2)):
        w = max(20, v * 708)
        y = 380 + i * 200
        c = RED if i == int(round(hi)) else SKY
        out.append(f'<rect x="{(W-w)/2:.1f}" y="{y}" width="{w:.1f}" height="140" fill="{c}" '
                   f'stroke="{NAVY}" stroke-width="7"/>')
    return "".join(out)


def orbit(n=6, r=250, core=1.0, out_hi=-1, **_):
    """A red core with sky satellites. One satellite may be red."""
    import math
    n = max(1, int(round(n)))
    cx, cy = 540, 660
    out = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        c = RED if i == int(round(out_hi)) else SKY
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="46" fill="{c}" stroke="{NAVY}" stroke-width="7"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{max(4,core*110):.1f}" fill="{RED}" '
               f'stroke="{NAVY}" stroke-width="8"/>')
    return "".join(out)


def split(ratio=0.5, **_):
    """The artwork box divided. Sky on the left, red on the right."""
    x = ART_X0 + ratio * (ART_X1 - ART_X0)
    return (f'<rect x="{ART_X0}" y="330" width="{max(0,x-ART_X0):.1f}" height="620" fill="{SKY}" '
            f'stroke="{NAVY}" stroke-width="7"/>'
            f'<rect x="{x:.1f}" y="330" width="{max(0,ART_X1-x):.1f}" height="620" fill="{RED}" '
            f'stroke="{NAVY}" stroke-width="7"/>')


def branch(n=3, hi=0, spread=1.0, **_):
    """One route splitting into n. The chosen one is red."""
    n = max(2, int(round(n)))
    x0, y0 = 240, 660
    out = [f'<circle cx="{x0}" cy="{y0}" r="30" fill="{NAVY}"/>']
    for i in range(n):
        dy = (i - (n - 1) / 2) * 210 * spread
        y1 = y0 + dy
        c = RED if i == int(round(hi)) else SKY
        wdt = 16 if i == int(round(hi)) else 10
        out.append(f'<path d="M{x0} {y0} C 480 {y0}, 560 {y1:.1f}, 820 {y1:.1f}" '
                   f'fill="none" stroke="{c}" stroke-width="{wdt}" stroke-linecap="round"/>')
        out.append(f'<circle cx="840" cy="{y1:.1f}" r="34" fill="{c}" stroke="{NAVY}" stroke-width="7"/>')
    return "".join(out)


def single(size=1.0, **_):
    """One red disc. Maximum emphasis, used sparingly."""
    return (f'<circle cx="540" cy="650" r="{max(6,size*300):.1f}" fill="{RED}" '
            f'stroke="{NAVY}" stroke-width="9"/>')


def bigfig(value=60.0, bar=0.6, **_):
    """A figure the script actually says, with a bar showing the same quantity."""
    v = int(round(value))
    return (f'<text x="540" y="700" font-family="Archivo" font-weight="800" font-size="300" '
            f'text-anchor="middle" fill="{RED}">{v}%</text>'
            f'<rect x="196" y="820" width="708" height="34" fill="{SKY}" stroke="{NAVY}" stroke-width="6"/>'
            f'<rect x="196" y="820" width="{max(0,bar*708):.1f}" height="34" fill="{RED}" '
            f'stroke="{NAVY}" stroke-width="6"/>')


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
