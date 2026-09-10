#!/usr/bin/env python3
"""Turn the beat script plus the Whisper frame table into one prompt per frame.

New frames are composed from the locked asset roster. Variation frames are edits
of the immediately previous frame and carry exactly one visible change.
"""
import json, sys, pathlib

EP = pathlib.Path("pipeline/episodes/ep01-atomic-habits")

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

EDIT_PREAMBLE = (
    "Take the reference image and keep it EXACTLY: same composition, same crop, same camera, same "
    "character, same colors, same background, same style. Change ONLY: {change}. Do not redraw or "
    "re-stage anything else."
)

ASSETS = {
    "style_key": "2aafdb1d-7e9d-4fbd-8f1d-7a623ae64ee9",
    "character": "0f8a8c2b-02e6-41ac-85ca-1830f7511700",
    "stage":     "5a140cec-03e4-4f51-a646-fa728429beee",
    "hallway":   "0e08c513-490b-469a-bb0f-3c8dc4c7b9fc",
    "kitchen":   "f7a94a39-6d20-417e-9fc2-d74abc1a02c7",
    "roomplan":  "60ca1974-d476-40e0-a882-ea0dbbbd4ebe",
    "shoes":     "a9c6c35b-2662-4577-87de-5809a05342eb",
    "book":      "7051f741-cb8b-450d-a981-bfbe88bee329",
    "hand":      "c4f9cab5-dd4c-49ed-b9fd-7227ca986ee3",
    "steps":     "bb0e6612-5c9e-4015-a153-98c9637e5643",
}

# Which roster pieces each beat composes from, beyond the style key.
BEAT_ASSETS = {
    1: ["stage", "character"], 2: ["stage", "character"], 3: ["stage", "character"],
    4: ["stage", "character"], 5: ["stage"], 6: ["stage"], 7: ["stage"], 8: ["stage"],
    9: ["stage", "character"], 10: ["stage", "character"], 11: ["stage", "character"],
    12: ["stage", "character"], 13: ["stage", "hand"], 14: ["stage", "hand"],
    15: ["stage", "hand"], 16: ["stage", "book"], 17: ["stage", "book"],
    18: ["stage", "book"], 19: ["stage"], 20: ["stage"], 21: ["stage"], 22: ["stage"],
    23: ["stage", "steps"], 24: ["stage", "steps"], 25: ["stage", "hand"],
    26: ["hallway", "shoes"], 27: ["hallway", "shoes"], 28: ["kitchen", "hand"],
    29: ["kitchen", "hand"], 30: ["roomplan"], 31: ["roomplan"],
    32: ["stage", "character"], 33: ["stage", "character"], 34: ["roomplan", "stage"],
    35: ["stage"], 36: ["stage"], 37: ["stage", "steps"], 38: ["stage", "steps"],
    39: ["stage", "book"], 40: ["stage", "book"],
}

# Scenes for the new framings that fall inside a variation beat.
VAR_SCENES = {
    2: "MEDIUM: the same two monochrome halftone cutout figures on the cream stage seen closer, both with one arm raised in an identical gesture, the burnt orange disc behind them",
    4: "WIDE: one monochrome cutout figure walking right across the cream stage, a second figure's legs disappearing off the left edge, a torn paper calendar strip with abstract tick marks along the bottom",
    7: "MEDIUM: a burnt orange arrow loop of three monochrome cutout icons on the cream stage with a single burnt orange flag cutout planted at the far right",
    8: "WIDE: the cream stage almost bare, a single burnt orange flag cutout standing alone, the faded monochrome arrow loop behind it",
    10: "CLOSE-UP: a monochrome halftone cutout figure slumped forward at a desk, head lowered onto one hand, a burnt orange half disc low behind",
    17: "CLOSE-UP: one single small monochrome book cutout alone on the cream stage, a burnt orange downward arrow shrunk beside it",
    33: "MEDIUM: a dot-matrix semicircle gauge on the cream stage with only one burnt orange dot left among monochrome dots, a monochrome cutout figure beside it",
    40: "MEDIUM: a single monochrome book cutout standing on a large flat burnt orange disc with a hand-drawn burnt orange marker circle around it, tape strips at the corners",
    12: "MEDIUM: the same row of five monochrome halftone runner cutouts seen closer, a single burnt orange marker underline running beneath all of them on the cream stage",
    14: "CLOSE-UP: one very small burnt orange paper block alone on the wide empty cream stage, a soft paper drop shadow beneath it",
    20: "MEDIUM: three pinned photo cards in a row on the cream stage with white borders and tape strips, the middle card popped in burnt orange",
    24: "CLOSE-UP: two monochrome halftone feet standing together on a torn paper step, a burnt orange stroke marking the step edge below them",
    27: "WIDE: the hallway stage plate with the monochrome door cutout, the burnt orange running shoes at its base, an empty patch of cream paper where a phone used to be",
    29: "MEDIUM: the oversized monochrome hand holding a single burnt orange fruit above the kitchen counter stage plate",
    31: "WIDE: the overhead torn paper room plan with one straight burnt orange route line crossing it cleanly",
    36: "WIDE: the cream stage nearly empty, a burnt orange marker cross stroke alone where the mountain cutout used to be",
    38: "MEDIUM: four torn paper steps rising to the right on the cream stage, the lowest step burnt orange, a monochrome shoe cutout at the base",
}

# Extra single-detail edits, consumed in order after a beat's own authored change.
EXTRAS = {
    1:  ["the left figure turns their head toward the other"],
    3:  ["the walking figure's leading leg swings forward"],
    5:  ["the fist opens into a flat empty palm"],
    6:  ["one of the three icons snaps forward toward the viewer",
         "the burnt orange arrow loop rotates a quarter turn"],
    7:  ["the orange flag tilts over to one side"],
    9:  ["the seated figure lifts their head upright",
         "one arm rises onto the desk"],
    11: ["the middle runner strides half a step ahead of the row"],
    12: ["the underline stroke extends past the last runner"],
    13: ["the oversized hand withdraws to the frame edge"],
    15: ["the hand lifts away, leaving the orange block alone"],
    16: ["the top book slides off the stack",
         "the burnt orange arrow lengthens downward"],
    19: ["the right hand card tilts and a tape strip peels"],
    21: ["one more burnt orange dot fills at the base of the bar"],
    23: ["the foot presses fully down onto the step"],
    24: ["both feet shift up onto the next step"],
    25: ["the fan of cards spreads wider under the hand"],
    26: ["the door cutout swings partly open"],
    28: ["the cupboard door closes over the biscuit tin"],
    30: ["two of the paper furniture shapes slide into new positions"],
    32: ["several burnt orange dots in the gauge flip to monochrome",
         "the standing figure's shoulders drop"],
    34: ["the large burnt orange disc behind the plan grows wider"],
    35: ["the burnt orange cross stroke thickens across the peak"],
    37: ["the monochrome shoe lifts onto the orange step"],
    38: ["a fourth step snaps into place at the top right"],
    39: ["the book tilts forward on the orange disc",
         "a tape strip snaps across the book's lower corner"],
}


def main() -> int:
    script = json.loads((EP / "script_manifest.json").read_text())
    beats = {b["n"]: b for b in script["beats"]}
    rows = [l.split("|") for l in (EP / "frames.tsv").read_text().strip().split("\n")]

    pending = {n: list(v) for n, v in EXTRAS.items()}
    used_authored = set()
    frames = []
    for row in rows:
        n, beat_n = int(row[0]), int(row[1])
        mode, parent = row[4], (None if row[5] == "-" else int(row[5]))
        beat = beats[beat_n]
        if mode == "new":
            scene = beat.get("scene") or VAR_SCENES[beat_n]
            frames.append({
                "n": n, "beat": beat_n, "mode": "new",
                "refs": [ASSETS["style_key"]] + [ASSETS[k] for k in BEAT_ASSETS[beat_n]],
                "prompt": f"{scene}\n\n{STYLE}",
            })
            continue
        if beat["image_mode"] == "variation" and beat_n not in used_authored:
            change = beat["change_only"]
            used_authored.add(beat_n)
        else:
            change = pending[beat_n].pop(0)
        frames.append({
            "n": n, "beat": beat_n, "mode": "variation", "parent": parent,
            "prompt": EDIT_PREAMBLE.format(change=change),
        })

    leftover = {n: v for n, v in pending.items() if v}
    if leftover:
        print(f"unused extras: {leftover}", file=sys.stderr)
        return 1
    (EP / "frame_prompts.json").write_text(json.dumps(frames, indent=1))
    print(f"wrote {len(frames)} frames, "
          f"{sum(1 for f in frames if f['mode'] == 'new')} new, "
          f"{sum(1 for f in frames if f['mode'] == 'variation')} edits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
