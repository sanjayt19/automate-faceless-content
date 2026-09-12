#!/usr/bin/env python3
"""One scene per beat, for all twelve reels.

Authored as blocks rather than as 456 separate scenes. A block names a scene
kind, how many beats it covers, and the start and end value of each parameter.
The block expands to one scene per beat with the numbers stepped between those
ends, so the picture is always moving in the direction the narration is going.
"""
import json, sys


def blk(kind, count, **ranges):
    """Expand one block into `count` scenes, stepping every parameter across it."""
    out = []
    for i in range(count):
        t = 0.0 if count == 1 else i / (count - 1)
        sc = {"kind": kind}
        for k, v in ranges.items():
            if isinstance(v, tuple):
                a, b = v
                sc[k] = a + (b - a) * t
            else:
                sc[k] = v
        out.append(sc)
    return out


def board(*blocks):
    return [s for b in blocks for s in b]


B = {}

B["passion"] = board(                                                    # 38
    blk("single", 3, size=(0.62, 1.0), accent=(0.0, 0.25)),
    blk("grid", 5, cols=5, rows=2, filled=(0.05, 0.2), boxed=(0.0, 0.2), accent=(0.25, 0.4)),
    blk("timeline", 6, pos=(0.05, 0.9), marker=1.0, accent=(0.4, 0.55)),
    blk("funnel", 6, w0=(1.0, 1.0), w1=(0.2, 0.62), w2=(0.05, 0.34), hi=2, accent=(0.55, 0.7)),
    blk("compare", 5, left=(0.8, 0.28), right=(0.2, 0.92), hi=1, accent=(0.7, 0.8)),
    blk("branch", 6, n=3, hi=(2, 0), spread=(0.5, 1.0), accent=(0.8, 0.9)),
    blk("stack", 4, n=4, hi=(-1, 0), fill=(0.0, 0.5), accent=(0.9, 0.95)),
    blk("single", 3, size=(0.55, 1.0), accent=1.0))

B["toolate"] = board(                                                    # 38
    blk("timeline", 4, pos=(0.95, 0.95), gap0=-1, gap1=-1, marker=(0.2, 1.0), accent=(0.0, 0.2)),
    blk("timeline", 5, pos=0.95, gap0=(0.35, 0.35), gap1=(0.36, 0.62), marker=1.0, accent=(0.2, 0.35)),
    blk("stack", 5, n=4, hi=(-1, 3), fill=(0.0, 1.0), accent=(0.35, 0.5)),
    blk("grid", 6, cols=4, rows=2, filled=(0.9, 0.12), boxed=(0.0, 0.28), accent=(0.5, 0.62)),
    blk("compare", 5, left=(0.85, 0.18), right=(0.15, 0.9), hi=1, accent=(0.62, 0.75)),
    blk("stack", 6, n=3, hi=(-1, 2), fill=(0.2, 1.0), accent=(0.75, 0.88)),
    blk("timeline", 4, pos=(0.2, 0.95), gap0=0.35, gap1=0.62, marker=1.0, accent=(0.88, 0.96)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["qualified"] = board(                                                  # 38
    blk("grid", 4, cols=5, rows=2, filled=(0.0, 0.2), boxed=0.0, accent=(0.0, 0.2)),
    blk("grid", 7, cols=5, rows=2, filled=(0.2, 1.0), boxed=(0.0, 0.0), accent=(0.2, 0.38)),
    blk("grid", 5, cols=5, rows=2, filled=1.0, boxed=(0.0, 0.62), accent=(0.38, 0.5)),
    blk("compare", 4, left=(0.9, 0.55), right=(0.25, 0.6), hi=1, accent=(0.5, 0.6)),
    blk("bigfig", 6, value=(10, 60), bar=(0.1, 0.6), accent=(0.6, 0.75)),
    blk("stack", 6, n=3, hi=(-1, 1), fill=(0.0, 1.0), accent=(0.75, 0.88)),
    blk("grid", 3, cols=5, rows=2, filled=0.6, boxed=(0.62, 0.62), accent=(0.88, 0.95)),
    blk("single", 3, size=(0.55, 1.0), accent=1.0))

B["gauges"] = board(                                                     # 38
    blk("stack", 4, n=4, hi=(-1, -1), fill=(0.0, 0.25), accent=(0.0, 0.2)),
    blk("orbit", 6, n=4, r=(120, 260), core=(0.2, 0.9), out_hi=-1, accent=(0.2, 0.35)),
    blk("stack", 7, n=4, hi=-1, fill=(0.25, 1.0), accent=(0.35, 0.52)),
    blk("stack", 5, n=4, hi=(2, 2), fill=(1.0, 0.5), accent=(0.52, 0.64)),
    blk("compare", 5, left=(0.9, 0.15), right=(0.15, 0.15), hi=0, accent=(0.64, 0.76)),
    blk("split", 5, ratio=(0.9, 0.35), accent=(0.76, 0.88)),
    blk("stack", 3, n=4, hi=2, fill=(0.5, 1.0), accent=(0.88, 0.96)),
    blk("single", 3, size=(0.55, 1.0), accent=1.0))

B["goodatit"] = board(                                                   # 37
    blk("single", 3, size=(0.6, 1.0), accent=(0.0, 0.2)),
    blk("stack", 6, n=4, hi=(0, 0), fill=(0.1, 0.9), accent=(0.2, 0.36)),
    blk("orbit", 6, n=6, r=(300, 170), core=(0.4, 1.0), out_hi=-1, accent=(0.36, 0.52)),
    blk("compare", 5, left=(0.85, 0.85), right=(0.2, 0.35), hi=0, accent=(0.52, 0.64)),
    blk("branch", 6, n=3, hi=(0, 2), spread=(0.4, 1.0), accent=(0.64, 0.8)),
    blk("split", 5, ratio=(0.2, 0.75), accent=(0.8, 0.92)),
    blk("timeline", 3, pos=(0.3, 0.92), marker=1.0, accent=(0.92, 0.98)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["wrongproblem"] = board(                                               # 38
    blk("stack", 4, n=6, hi=(-1, -1), fill=(0.15, 1.0), accent=(0.0, 0.2)),
    blk("grid", 6, cols=5, rows=4, filled=(0.1, 1.0), boxed=0.0, accent=(0.2, 0.38)),
    blk("compare", 5, left=(0.9, 0.9), right=(0.1, 0.12), hi=1, accent=(0.38, 0.5)),
    blk("branch", 6, n=4, hi=(3, 0), spread=(0.4, 0.95), accent=(0.5, 0.66)),
    blk("grid", 6, cols=5, rows=4, filled=(1.0, 0.1), boxed=(0.0, 0.22), accent=(0.66, 0.8)),
    blk("funnel", 5, w0=(1.0, 1.0), w1=(0.8, 0.42), w2=(0.6, 0.14), hi=2, accent=(0.8, 0.92)),
    blk("stack", 3, n=3, hi=(-1, 0), fill=(0.4, 1.0), accent=(0.92, 0.98)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["story"] = board(                                                      # 38
    blk("branch", 4, n=2, hi=(0, 0), spread=(0.3, 0.9), accent=(0.0, 0.2)),
    blk("compare", 6, left=(0.85, 0.9), right=(0.12, 0.08), hi=0, accent=(0.2, 0.36)),
    blk("orbit", 6, n=5, r=(160, 280), core=(1.0, 0.35), out_hi=-1, accent=(0.36, 0.52)),
    blk("branch", 5, n=2, hi=(0, 1), spread=(0.9, 0.9), accent=(0.52, 0.64)),
    blk("stack", 6, n=2, hi=(-1, 1), fill=(0.0, 1.0), accent=(0.64, 0.8)),
    blk("timeline", 5, pos=(0.15, 0.85), marker=1.0, accent=(0.8, 0.92)),
    blk("orbit", 3, n=5, r=280, core=(0.4, 1.0), out_hi=(-1, 2), accent=(0.92, 0.98)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["gravity"] = board(                                                    # 38
    blk("single", 3, size=(1.0, 0.5), accent=(0.0, 0.18)),
    blk("stack", 6, n=4, hi=(-1, -1), fill=(0.0, 1.0), accent=(0.18, 0.34)),
    blk("compare", 5, left=(0.15, 0.9), right=(0.15, 0.2), hi=0, accent=(0.34, 0.46)),
    blk("grid", 6, cols=4, rows=3, filled=(1.0, 0.35), boxed=(0.0, 0.5), accent=(0.46, 0.62)),
    blk("split", 6, ratio=(0.5, 0.5), accent=(0.62, 0.78)),
    blk("stack", 6, n=3, hi=(-1, 0), fill=(0.9, 0.3), accent=(0.78, 0.9)),
    blk("funnel", 3, w0=1.0, w1=(0.9, 0.5), w2=(0.8, 0.16), hi=2, accent=(0.9, 0.97)),
    blk("single", 3, size=(0.55, 1.0), accent=1.0))

B["log"] = board(                                                        # 38
    blk("grid", 4, cols=7, rows=2, filled=(0.0, 0.12), boxed=0.0, accent=(0.0, 0.18)),
    blk("grid", 7, cols=7, rows=2, filled=(0.12, 1.0), boxed=0.0, accent=(0.18, 0.36)),
    blk("stack", 6, n=5, hi=(-1, 1), fill=(0.3, 1.0), accent=(0.36, 0.52)),
    blk("grid", 6, cols=7, rows=2, filled=1.0, boxed=(0.0, 0.44), accent=(0.52, 0.66)),
    blk("orbit", 5, n=4, r=(280, 150), core=(0.3, 1.0), out_hi=-1, accent=(0.66, 0.78)),
    blk("funnel", 5, w0=1.0, w1=(0.85, 0.45), w2=(0.7, 0.18), hi=2, accent=(0.78, 0.9)),
    blk("stack", 2, n=3, hi=0, fill=1.0, accent=(0.9, 0.96)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["threelives"] = board(                                                 # 38
    blk("branch", 4, n=3, hi=(0, 0), spread=(0.15, 0.9), accent=(0.0, 0.2)),
    blk("stack", 5, n=3, hi=(0, 0), fill=(0.34, 0.34), accent=(0.2, 0.34)),
    blk("stack", 5, n=3, hi=(1, 1), fill=(0.67, 0.67), accent=(0.34, 0.48)),
    blk("stack", 5, n=3, hi=(2, 2), fill=(1.0, 1.0), accent=(0.48, 0.6)),
    blk("single", 4, size=(0.9, 0.42), accent=(0.6, 0.7)),
    blk("branch", 7, n=3, hi=(0, 2), spread=(0.9, 1.0), accent=(0.7, 0.86)),
    blk("orbit", 5, n=3, r=(150, 270), core=(1.0, 0.4), out_hi=(-1, 1), accent=(0.86, 0.96)),
    blk("branch", 3, n=3, hi=1, spread=1.0, accent=1.0))

B["prototype"] = board(                                                  # 38
    blk("split", 4, ratio=(0.95, 0.55), accent=(0.0, 0.2)),
    blk("compare", 6, left=(0.15, 0.2), right=(0.15, 0.95), hi=1, accent=(0.2, 0.36)),
    blk("grid", 5, cols=3, rows=2, filled=(0.0, 0.34), boxed=(0.0, 0.36), accent=(0.36, 0.5)),
    blk("timeline", 6, pos=(0.08, 0.3), marker=1.0, accent=(0.5, 0.64)),
    blk("branch", 6, n=3, hi=(1, 0), spread=(0.5, 1.0), accent=(0.64, 0.8)),
    blk("compare", 5, left=(0.2, 0.15), right=(0.9, 0.95), hi=0, accent=(0.8, 0.92)),
    blk("orbit", 3, n=4, r=220, core=(0.4, 1.0), out_hi=(-1, 0), accent=(0.92, 0.98)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))

B["degree"] = board(                                                     # 39
    blk("single", 3, size=(1.0, 0.5), accent=(0.0, 0.18)),
    blk("bigfig", 5, value=(20, 75), bar=(0.2, 0.75), accent=(0.18, 0.34)),
    blk("orbit", 6, n=4, r=(120, 120), core=(1.0, 1.0), out_hi=-1, accent=(0.34, 0.5)),
    blk("compare", 5, left=(0.85, 0.35), right=(0.2, 0.85), hi=1, accent=(0.5, 0.62)),
    blk("branch", 6, n=3, hi=(0, 1), spread=(0.3, 0.85), accent=(0.62, 0.78)),
    blk("timeline", 6, pos=(0.12, 0.88), marker=1.0, accent=(0.78, 0.9)),
    blk("stack", 5, n=3, hi=(-1, 2), fill=(0.3, 1.0), accent=(0.9, 0.97)),
    blk("single", 3, size=(0.58, 1.0), accent=1.0))


if __name__ == "__main__":
    counts = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    for k, v in B.items():
        n = len(counts[k]["beats"]) if counts else None
        flag = "" if n is None else ("  ok" if n == len(v) else f"  MISMATCH beats={n}")
        print(f"{k:<14}{len(v):>4} scenes{flag}")
