#!/usr/bin/env python3
"""Give every beat a start and end time.

The narration is read verbatim from the beats, so the transcript's words line up
with the beat words in order. Walk both in step and hand each beat the span of
the words it claims. No fuzzy matching is needed and none is used, which is why
this is reliable: the only thing that can drift is whisper mishearing a word,
and a mishearing still occupies the right slot in the sequence.
"""
import json, re, sys


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def align(beats, words, audio_dur):
    toks = [(norm(w["word"]), w) for w in words]
    toks = [t for t in toks if t[0]]
    out, cur = [], 0
    for i, beat in enumerate(beats):
        n = len([w for w in beat.split() if norm(w)])
        take = toks[cur:cur + n]
        if not take:                       # transcript ran out; share the tail evenly
            start = out[-1]["end"] if out else 0.0
            step = (audio_dur - start) / max(1, len(beats) - i)
            out.append({"n": i + 1, "start": round(start, 3), "end": round(start + step, 3)})
            continue
        out.append({"n": i + 1,
                    "start": round(take[0][1]["start"], 3),
                    "end": round(take[-1][1]["end"], 3)})
        cur += n
    # make the timeline contiguous and end exactly on the audio
    for i in range(len(out) - 1):
        out[i]["end"] = out[i + 1]["start"]
    out[0]["start"] = 0.0
    out[-1]["end"] = round(audio_dur, 3)
    for b in out:
        if b["end"] - b["start"] < 0.25:   # never let a beat flash past
            b["end"] = round(b["start"] + 0.25, 3)
    for i in range(len(out) - 1):
        out[i]["end"] = min(out[i]["end"], out[i + 1]["start"])
        if out[i]["end"] <= out[i]["start"]:
            out[i]["end"] = round(out[i]["start"] + 0.2, 3)
            out[i + 1]["start"] = out[i]["end"]
    out[-1]["end"] = round(audio_dur, 3)
    return out


if __name__ == "__main__":
    beats = json.load(open(sys.argv[1]))
    ts = json.load(open(sys.argv[2]))
    dur = float(sys.argv[3])
    res = align(beats, ts["words"], dur)
    json.dump(res, open(sys.argv[4], "w"), indent=1)
    spans = [round(b["end"] - b["start"], 2) for b in res]
    print(f"{len(res)} beats  shortest {min(spans)}s  longest {max(spans)}s  ends {res[-1]['end']}s")
