"""Stream Photo Cut frames as raw RGB on stdout, for ffmpeg to swallow.

    render_photocut.py <spec.json> <key> <images.json> <timeline.json>

Every beat gets its own shot. Any beat that runs longer than SUBCUT seconds is
split in two, so the picture never sits still long enough for a thumb to move.
"""
import json, sys
from PIL import Image
import photocut as P

SUBCUT = 1.9      # a beat longer than this is cut in half
MIN_HALF = 0.55   # ...unless the halves would be too short to read


def load_images(paths):
    out = {}
    for k, p in paths.items():
        im = Image.open(p).convert("RGB")
        out[k] = P.grade(im)
    return out


def shots_for(beats, timeline):
    """One (start, end, code, variant) per cut."""
    cuts = []
    for i, (b, t) in enumerate(zip(beats, timeline)):
        s, e = t["start"], t["end"]
        code = b["s"]
        photo = not code.startswith(("!", "#"))
        if photo and (e - s) > SUBCUT and (e - s) / 2 >= MIN_HALF:
            m = s + (e - s) / 2
            cuts.append((s, m, code, 0, i))
            cuts.append((m, e, code, 1, i))
        else:
            cuts.append((s, e, code, 0, i))
    return cuts


def main():
    spec = json.load(open(sys.argv[1]))[sys.argv[2]]
    imgs = load_images(json.load(open(sys.argv[3])))
    timeline = json.load(open(sys.argv[4]))
    beats = spec["beats"]
    cuts = shots_for(beats, timeline)

    total = int(round(timeline[-1]["end"] * P.FPS))
    out = sys.stdout.buffer
    ci = 0
    for f in range(total):
        t = f / P.FPS
        while ci + 1 < len(cuts) and t >= cuts[ci][1]:
            ci += 1
        cs, ce, code, variant, bi = cuts[ci]
        p = 0.0 if ce <= cs else min(1.0, max(0.0, (t - cs) / (ce - cs)))
        beat = beats[bi]

        if code.startswith("!"):
            _, rest = code.split("!", 1)
            bg, word = rest.split(":", 1)
            im = P.punch_card(bg, word, p)
        elif code.startswith("#"):
            stage = int(code.split(":", 1)[1])
            im = P.gauge_card(stage, p)
            im = P.draw_caption(im, beat["t"], beat.get("em", ""), p)
        else:
            src = code.split("@", 1)[0]
            im = P.frame_from_photo(imgs[src], ci, variant, p)
            # Caption rides the beat, not the cut, so a sub-cut does not
            # re-animate text the viewer is already reading.
            bp = (t - timeline[bi]["start"]) / max(0.001, timeline[bi]["end"] - timeline[bi]["start"])
            im = P.draw_caption(im, beat["t"], beat.get("em", ""), min(1.0, max(0.0, bp)))
        out.write(im.tobytes())
    out.flush()
    print(f"{total} frames, {len(cuts)} cuts, "
          f"{round(timeline[-1]['end'] / len(cuts), 2)}s average shot", file=sys.stderr)


if __name__ == "__main__":
    main()
