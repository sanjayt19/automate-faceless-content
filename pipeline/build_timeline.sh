#!/usr/bin/env bash
# Build one episode's frame timeline inside the Higgsfield sandbox.
#
# Transcribes the narration, aligns it to the authored beats, then coarsens the
# result so each beat uses the fewest frames the assembler allows. Prints the
# frame table for frames.tsv and the numbers worth recording.
#
# Usage: REF=<commit-sha> build_timeline.sh <episode-dir-name> <narration-mp3-url>
set -euo pipefail

EP="$1"; NARRATION_URL="$2"
REF="${REF:-claude/automated-video-shorts-lq2gya}"
BASE="https://raw.githubusercontent.com/sanjayt19/automate-faceless-content/$REF/pipeline"
HF="${HF_WORKFLOWS}/faceless-video/scripts"

mkdir -p work/voices
curl -fsSL --retry 3 "$BASE/episodes/$EP/script_manifest.json" -o script_manifest.json
curl -fsSL --retry 3 "$BASE/coarsen_timeline.py" -o coarsen.py
curl -fsSL --retry 3 "$NARRATION_URL" -o raw_narration.mp3

ffmpeg -y -v error -i raw_narration.mp3 \
  -af "areverse,atrim=start=0.06,afade=t=in:st=0:d=0.04,areverse,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 work/voices/narration.wav

python3 - work/voices/narration.wav timestamps.json <<'PY'
import json, sys
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, _ = model.transcribe(sys.argv[1], word_timestamps=True, language="en")
words = [{"word": w.word, "start": w.start, "end": w.end}
         for s in segments for w in (s.words or [])]
json.dump({"words": words}, open(sys.argv[2], "w"))
PY

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 work/voices/narration.wav)
echo "AUDIO_DURATION=$DURATION"
python3 "$HF/build_scene_timeline.py" --script script_manifest.json --timestamps timestamps.json \
  --audio-duration "$DURATION" --out scene_manifest.json
python3 coarsen.py scene_manifest.json 1.48

echo "===TSV==="
python3 - scene_manifest.json <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
for f in m["frames"]:
    print(f"{f['n']}|{f['beat_n']}|{f['start']:.2f}|{f['duration']:.2f}|{f['image_mode']}|{f.get('variation_of_frame','-')}")
n = m["narration"]
print("SIMILARITY", n["alignment_similarity"], "DUR", n["audio_duration_seconds"])
PY
