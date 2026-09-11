#!/usr/bin/env bash
# Build one reel end to end inside the Higgsfield sandbox. No image credits.
#
#   REF=<sha> build_reel.sh <key> <narration-url> [upload-url]
#
# Frames are drawn from the storyboard, tweened between beats, held by ffmpeg's
# concat demuxer, then captioned with the burn-in the rest of the channel uses.
set -euo pipefail

KEY="$1"; NARR="$2"; UP="${3:-}"
REF="${REF:-claude/automated-video-shorts-lq2gya}"
RAW="https://raw.githubusercontent.com/sanjayt19/automate-faceless-content/$REF/pipeline/render"
SUBS="${HF_WORKFLOWS}/subtitles/scripts"
WORK="/home/user/build/$KEY"

rm -rf "$WORK"; mkdir -p "$WORK/frames" "$WORK/out"
cd "$WORK"
for f in scenes.py render_reel.py storyboards.py align.py reels.json; do
  curl -fsSL --retry 3 "$RAW/$f" -o "$f"
done

curl -fsSL --retry 3 "$NARR" -o raw.mp3
ffmpeg -y -v error -i raw.mp3 \
  -af "areverse,atrim=start=0.06,afade=t=in:st=0:d=0.04,areverse,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 narration.wav
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 narration.wav)
echo "AUDIO ${DUR}s"

python3 - "$KEY" <<'PY'
import json, sys
r = json.load(open("reels.json"))[sys.argv[1]]
json.dump(r["beats"], open("beats.json", "w"))
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

python3 - "$KEY" <<'PY'
import json, sys, storyboards
json.dump({"scenes": storyboards.B[sys.argv[1]]}, open("storyboard.json", "w"))
PY

python3 render_reel.py storyboard.json timeline.json frames

ffmpeg -y -v error -f concat -safe 0 -i frames/concat.txt -i narration.wav \
  -vf "fps=30,scale=1080:1920:flags=lanczos,format=yuv420p" \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.1 \
  -c:a aac -b:a 192k -shortest -movflags +faststart out/clean.mp4

bash "$SUBS/fetch_fonts.sh" >/dev/null 2>&1 || true
python3 "$SUBS/audio_to_captions.py" narration.wav --srt out/caps.srt --language en
python3 "$SUBS/subtitle_paper_burn.py" --in out/clean.mp4 --srt out/caps.srt \
  --out out/final.mp4 --style bold --font-key tiktok \
  --bottom-frac 0.30 --maxw-frac 0.72

ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 out/final.mp4
ls -la out/final.mp4

if [ -n "$UP" ]; then
  curl -f -X PUT -H 'Content-Type: video/mp4' --upload-file out/final.mp4 "$UP"
  echo UPLOADED
fi
echo "DONE $KEY"
