#!/usr/bin/env python3
"""Turn an episode's beat script plus its Whisper frame table into one prompt per frame.

New frames are composed from the locked asset roster. Variation frames are edits of
the immediately previous frame and carry exactly one visible change.

Each episode directory holds:
  script_manifest.json  the beats, with a scene on every new beat
  frames.tsv            n|beat|start|duration|mode|parent, from build_scene_timeline
  frame_config.json     assets, per-beat asset picks, scenes for new frames that fall
                        inside a variation beat, extra edit lines, and an optional
                        "style" block overriding the series default

Usage: build_frame_prompts.py pipeline/episodes/ep02-volume-trap
"""
import json, sys, pathlib

STYLE = (
    "STYLE: flat editorial documentary collage on a warm cream paper stage with subtle fiber grain: "
    "monochrome halftone archival photo cutouts with rough white keylines and a slightly offset burnt "
    "orange stroke behind each cutout, one single burnt orange accent color per video - a large flat "
    "burnt orange disc behind the main subject and exactly one color-popped hero element among the "
    "monochrome - torn paper edges and tape strips, soft paper drop shadows, hand-drawn burnt orange "
    "marker circles, arrows and underline strokes (abstract strokes only, never letters), abstract "
    "unlabeled data shapes and flat stylized maps, subtle print misregistration on inked elements, "
    "non-photorealistic illustrated collage, never live-action.\n\n"
    "PALETTE LOCK: warm cream paper base, monochrome halftone cutouts, ONE burnt orange accent - no "
    "other colors, no gradients, no full-color scenes.\n\n"
    "NEGATIVE: readable text, letters, words, numbers, live-action footage, photographic realism, "
    "full-color scene, foreign accent colors, 3D render."
)

EDIT = (
    "Take the reference image and keep it EXACTLY: same composition, same crop, same camera, same "
    "character, same colors, same background, same style. Change ONLY: {change}. Do not redraw or "
    "re-stage anything else."
)


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    ep = pathlib.Path(argv[1])
    script = json.loads((ep / "script_manifest.json").read_text())
    cfg = json.loads((ep / "frame_config.json").read_text())
    style = cfg.get("style", STYLE)   # a visual format may override the locked block
    beats = {b["n"]: b for b in script["beats"]}
    assets, beat_assets = cfg["assets"], cfg["beat_assets"]
    var_scenes = {int(k): v for k, v in cfg["var_scenes"].items()}
    pending = {int(k): list(v) for k, v in cfg["extras"].items()}

    used_authored = set()
    frames = []
    for row in (ep / "frames.tsv").read_text().strip().split("\n"):
        cols = row.split("|")
        n, beat_n, mode = int(cols[0]), int(cols[1]), cols[4]
        parent = None if cols[5] == "-" else int(cols[5])
        beat = beats[beat_n]
        if mode == "new":
            scene = beat.get("scene") or var_scenes[beat_n]
            refs = [assets["style_key"]] + [assets[k] for k in beat_assets[str(beat_n)]]
            frames.append({"n": n, "beat": beat_n, "mode": "new", "refs": refs,
                           "prompt": f"{scene}\n\n{style}"})
            continue
        if beat["image_mode"] == "variation" and beat_n not in used_authored:
            change = beat["change_only"]
            used_authored.add(beat_n)
        else:
            change = pending[beat_n].pop(0)
        frames.append({"n": n, "beat": beat_n, "mode": "variation", "parent": parent,
                       "prompt": EDIT.format(change=change)})

    leftover = {n: v for n, v in pending.items() if v}
    if leftover:
        print(f"unused extras: {leftover}", file=sys.stderr)
        return 1
    (ep / "frame_prompts.json").write_text(json.dumps(frames, indent=1))
    print(f"{ep.name}: {len(frames)} frames, "
          f"{sum(1 for f in frames if f['mode'] == 'new')} new, "
          f"{sum(1 for f in frames if f['mode'] == 'variation')} edits")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
