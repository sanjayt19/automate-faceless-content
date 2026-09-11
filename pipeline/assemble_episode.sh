#!/usr/bin/env bash
# Assemble one Picture Story episode inside the Higgsfield sandbox.
#
# Everything the run needs is fetched fresh, because the sandbox is discarded
# between calls. Inputs come from the repo (script, timeline, frame results)
# and from durable generation URLs (narration, frames).
#
# Usage: REF=<commit-sha> assemble_episode.sh <episode-dir-name> <narration-mp3-url> <frame-count> <requested-seconds> [upload-url]
#
# Pin REF to a commit sha: raw.githubusercontent.com caches branch paths for
# minutes and ignores query strings, so a branch path can serve a stale file.
set -euo pipefail

EP="$1"; NARRATION_URL="$2"; BLOCKS="$3"; SECONDS_TARGET="$4"; UPLOAD_URL="${5:-}"
REF="${REF:-claude/automated-video-shorts-lq2gya}"
RAW="https://raw.githubusercontent.com/sanjayt19/automate-faceless-content/$REF/pipeline/episodes/$EP"
HF="${HF_WORKFLOWS}/faceless-video/scripts"

mkdir -p work/voices work/output work/frames
for f in script_manifest.json scene_manifest.json frame_results.json; do
  curl -fsSL -H 'Cache-Control: no-cache' --retry 3 "$RAW/$f?cb=$(date +%s)" -o "$f"
done

curl -fsSL --retry 3 "$NARRATION_URL" -o raw_narration.mp3
ffmpeg -y -v error -i raw_narration.mp3 \
  -af "areverse,atrim=start=0.06,afade=t=in:st=0:d=0.04,areverse,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 work/voices/narration.wav

python3 "$HF/validate_picture_story.py" --script script_manifest.json --duration-seconds "$SECONDS_TARGET"
python3 "$HF/bind_scene_frame_results.py" --manifest scene_manifest.json \
  --results frame_results.json --out scene_manifest.bound.json
python3 "$HF/materialize_scene_frames.py" --manifest scene_manifest.bound.json --frames-dir work/frames

chmod +x "$HF"/*.sh
bash "$HF/assemble_slides.sh" --out work/output/final_clean.mp4 --audio work/voices/narration.wav \
  --blocks "$BLOCKS" --timeline scene_manifest.bound.json --frames-dir work/frames \
  --requested-seconds "$SECONDS_TARGET"

chmod +x "${HF_WORKFLOWS}"/subtitles/scripts/*.sh
bash "${HF_WORKFLOWS}/subtitles/scripts/fetch_fonts.sh"
python3 "${HF_WORKFLOWS}/subtitles/scripts/audio_to_captions.py" work/voices/narration.wav \
  --srt work/output/final.srt --script script_manifest.json --language en
python3 "${HF_WORKFLOWS}/subtitles/scripts/subtitle_paper_burn.py" --in work/output/final_clean.mp4 \
  --srt work/output/final.srt --out work/output/final.mp4 --style bold --font-key tiktok

ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 work/output/final.mp4
python3 -c "import json;d=json.load(open('work/output/final_clean.mp4.assembly.json'));print('SIDECAR frames',d.get('frames'),'blocks',d.get('blocks'))"

if [ -n "$UPLOAD_URL" ]; then
  curl -f -X PUT -H 'Content-Type: video/mp4' --upload-file work/output/final.mp4 "$UPLOAD_URL"
  echo "UPLOADED"
fi
echo "DONE $EP"
