#!/usr/bin/env python3
"""Re-split a scene manifest so each beat uses the fewest frames it legally can.

build_scene_timeline.py targets 1.2s per frame. The assembler's hard ceiling is 1.5s
and its density floor is ceil(narration_seconds / 1.5) frames, so a longer target
still passes both gates while generating fewer images.

Beat spans are preserved exactly; only the number of frames inside each beat changes.

Usage: coarsen_timeline.py scene_manifest.json [target_seconds]
"""
import json, math, sys

HARD_MAX = 1.5


def coarsen(manifest, target=1.48):
    spans = {}
    for f in manifest["frames"]:
        b = f["beat_n"]
        s, e = spans.get(b, (f["start"], f["end"]))
        spans[b] = (min(s, f["start"]), max(e, f["end"]))
    beats = {b["n"]: b for b in manifest["beats"]}
    frames, depth = [], 0
    for b in sorted(spans):
        start, end = spans[b]
        duration = end - start
        count = max(1, math.ceil(round(duration / target, 6)))
        while duration / count > HARD_MAX:
            count += 1
        for part in range(count):
            fs = start + duration * part / count
            fe = start + duration * (part + 1) / count
            n = len(frames) + 1
            wants = part > 0 or (bool(frames) and beats[b].get("image_mode") == "variation")
            is_var = bool(frames) and wants and depth < 2
            depth = depth + 1 if is_var else 0
            fr = {"n": n, "beat_n": b, "start": round(fs, 3), "end": round(fe, 3),
                  "duration": round(fe - fs, 3), "output_slot": f"frame-{n:03d}",
                  "image_mode": "variation" if is_var else "new", "generation_wave": depth}
            if is_var:
                fr["variation_of_frame"] = n - 1
                fr["reference_output_slot"] = f"frame-{n - 1:03d}"
                fr["change_only"] = str(beats[b].get("change_only") or "advance the named action")
            frames.append(fr)
    manifest["frames"] = frames
    manifest["generation_waves"] = [
        {"wave": w, "output_slots": [f["output_slot"] for f in frames if f["generation_wave"] == w]}
        for w in range(3) if any(f["generation_wave"] == w for f in frames)]
    return manifest


def main(argv):
    path = argv[1]
    target = float(argv[2]) if len(argv) > 2 else 1.48
    m = json.loads(open(path).read())
    before = len(m["frames"])
    audio = m["narration"]["audio_duration_seconds"]
    m = coarsen(m, target)
    floor = math.ceil(audio / 1.5)
    longest = max(f["duration"] for f in m["frames"])
    assert len(m["frames"]) >= floor, f"{len(m['frames'])} frames below density floor {floor}"
    assert longest <= HARD_MAX, f"frame of {longest}s exceeds {HARD_MAX}s"
    open(path, "w").write(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(f"coarsened {before} -> {len(m['frames'])} frames "
          f"(floor {floor}, longest {longest:.2f}s, saved {before - len(m['frames'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
