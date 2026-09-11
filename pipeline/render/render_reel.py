#!/usr/bin/env python3
"""Render one reel's video track from a storyboard and a beat timeline.

Frames are drawn, not generated, so motion is real: between two beats the
scene's numbers are tweened and a frame is drawn at each step. A beat holds on
one still and then moves into the next over TWEEN seconds.

Only distinct frames are written. ffmpeg's concat demuxer holds each one for as
long as it is on screen, so a 84 second reel is a few hundred files rather than
two and a half thousand.

Usage: render_reel.py <storyboard.json> <beats.json> <outdir>
  storyboard.json  {"scenes": [ {kind, ...params}, ... ] }   one per beat
  beats.json       [ {"n":1,"start":0.0,"end":1.1}, ... ]
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes as SC

FPS = 30
TWEEN = 0.40          # seconds of movement into each new beat


def render(storyboard, beats, outdir):
    os.makedirs(outdir, exist_ok=True)
    scs = storyboard["scenes"]
    assert len(scs) == len(beats), f"{len(scs)} scenes vs {len(beats)} beats"

    entries, idx, cache = [], 0, {}

    def emit(scene, dur):
        nonlocal idx
        svg = SC.render_svg(scene)
        if svg in cache:
            png = cache[svg]
        else:
            png = os.path.join(outdir, f"f{idx:05d}.png")
            sp = png[:-4] + ".svg"
            open(sp, "w").write(svg)
            subprocess.run(["rsvg-convert", "-w", str(SC.W), "-h", str(SC.H), sp, "-o", png],
                           check=True)
            os.remove(sp)
            cache[svg] = png
            idx += 1
        entries.append((png, dur))

    for i, (sc, bt) in enumerate(zip(scs, beats)):
        dur = bt["end"] - bt["start"]
        prev = scs[i - 1] if i else None
        tw = min(TWEEN, dur * 0.6) if prev else 0.0
        if tw > 0:
            steps = max(1, int(round(tw * FPS)))
            for s in range(steps):
                t = (s + 1) / steps
                # ease in and out so movement starts and stops softly
                e = t * t * (3 - 2 * t)
                emit(SC.blend(prev, sc, e), tw / steps)
        emit(sc, max(1.0 / FPS, dur - tw))

    listing = os.path.join(outdir, "concat.txt")
    with open(listing, "w") as fh:
        for png, dur in entries:
            fh.write(f"file '{os.path.basename(png)}'\nduration {dur:.4f}\n")
        fh.write(f"file '{os.path.basename(entries[-1][0])}'\n")   # demuxer needs the tail repeated
    print(f"{len(entries)} timeline entries, {idx} distinct frames -> {listing}")
    return listing


if __name__ == "__main__":
    sb = json.load(open(sys.argv[1]))
    bt = json.load(open(sys.argv[2]))
    render(sb, bt, sys.argv[3])
