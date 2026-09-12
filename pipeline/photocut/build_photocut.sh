#!/usr/bin/env bash
# Build one Photo Cut reel inside the Higgsfield sandbox.
#
#   REF=<sha> build_photocut.sh <key> <narration-url> <images.json> [upload-url]
#
# images.json maps a shot name to a URL. Photographs are graded into the locked
# palette on the way in, so nothing off-palette can reach the frame.
set -euo pipefail

KEY="$1"; NARR="$2"; IMGS="$3"; UP="${4:-}"
REF="${REF:-claude/automated-video-shorts-lq2gya}"
RAW="https://raw.githubusercontent.com/sanjayt19/automate-faceless-content/$REF/pipeline"
WORK="/home/user/pcut/$KEY"

rm -rf "$WORK"; mkdir -p "$WORK/src" "$WORK/out"
cp "$IMGS" "$WORK/urls.json"
cd "$WORK"
curl -fsSL --retry 3 "$RAW/photocut/photocut.py" -o photocut.py
curl -fsSL --retry 3 "$RAW/photocut/render_photocut.py" -o render_photocut.py
curl -fsSL --retry 3 "$RAW/photocut/spec.json" -o spec.json
curl -fsSL --retry 3 "$RAW/render/align.py" -o align.py

python3 - <<'PY'
import json, subprocess
urls = json.load(open("urls.json"))
paths = {}
for k, u in urls.items():
    p = f"src/{k}.png"
    subprocess.run(["curl", "-fsSL", "--retry", "3", u, "-o", p], check=True)
    paths[k] = p
json.dump(paths, open("images.json", "w"))
print("fetched", len(paths), "stills")
PY

curl -fsSL --retry 3 "$NARR" -o raw.mp3
ffmpeg -y -v error -i raw.mp3 \
  -af "areverse,atrim=start=0.06,afade=t=in:st=0:d=0.04,areverse,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 narration.wav
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 narration.wav)
echo "AUDIO ${DUR}s"

python3 - "$KEY" <<'PY'
import json, sys
spec = json.load(open("spec.json"))[sys.argv[1]]
json.dump([b["t"] for b in spec["beats"]], open("beats.json", "w"))
PY

python3 - narration.wav timestamps.json <<'PY'
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("base", device="cpu", compute_type="int8")
segs, _ = m.transcribe(sys.argv[1], word_timestamps=True, language="en")
w = [{"word": x.word, "start": x.start, "end": x.end} for s in segs for x in (s.words or [])]
json.dump({"words": w}, open(sys.argv[2], "w"))
print("transcribed", len(w), "words")
PY

python3 align.py beats.json timestamps.json "$DUR" timeline.json

python3 render_photocut.py spec.json "$KEY" images.json timeline.json \
  | ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - \
      -i narration.wav -vf format=yuv420p \
      -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.1 \
      -c:a aac -b:a 192k -shortest -movflags +faststart out/final.mp4

ffprobe -v error -show_entries format=duration -of csv=p=0 out/final.mp4
ls -la out/final.mp4

if [ -n "$UP" ]; then
  curl -f -X PUT -H 'Content-Type: video/mp4' --upload-file out/final.mp4 "$UP"
  echo UPLOADED
fi
echo "DONE $KEY"
