# Photo Cut

The channel's second visual format. Bold Contrast (`pipeline/render`) draws flat
vector scenes; this one grades real photographs into the same locked palette.

## Why it exists

The first twelve-reel batch came back with three complaints, all fair:

- **Repetition.** Ten scene kinds cycling across thirty-eight beats meant the
  same shapes came round every reel, and by the third reel the format was
  reading as one long diagram.
- **Pace.** Eighty seconds over thirty-eight beats is 2.1s a beat, and a held
  vector frame at 2.1s is a still picture on a feed that scrolls.
- **Comprehension.** Abstract shapes need decoding. A photograph does not.

## What changed

| | Bold Contrast (batch 1) | Photo Cut |
|---|---|---|
| runtime | 76–89s | 45–50s |
| words | ~195 | ~115 |
| beats | 37–39 | 25 |
| visual cuts | one per beat | one per beat, plus a sub-cut on any beat over 1.9s |
| average shot | 2.1s | 1.36s |
| imagery | drawn vectors | graded photographs, punch cards, one gauge card |

Any beat longer than 1.9s is split at its midpoint and the second half reframes
the same photograph, so the picture never sits still long enough for a thumb to
move. Punch cards (a full-bleed red or navy frame carrying one word) break the
rhythm where the script lands a single beat, and open on two frames of inverted
colour so the cut reads as a hit.

## Palette

Nothing here can emit an off-palette colour. Photographs are converted to
luminance, contrast-pushed, then mapped through a fixed ramp: `#1D3557` in the
shadows, `#A8DADC` through the mids, `#F1FAEE` in the highlights. `#E63946` is
reserved for the emphasis word in a caption, the flagged gauge bar, and the red
punch card. Measured on the finished burnout reel at four frames a second, mean
distance from that ramp is 6.8 of 255 across 191 frames, which is JPEG noise.

## Captions

One paper plate, navy type, a hard navy drop shadow, centred at 65.5% down the
frame. That clears the TikTok caption block and music ticker, the Shorts title,
and the right-hand action rail. The emphasis word in each beat is red. The plate
is the same shape and position every beat, so the eye never hunts for it.

## Build

    REF=<sha> build_photocut.sh <key> <narration-url> <images.json> [upload-url]

`images.json` maps a shot name to a URL. Narration is Magnific `eleven_v3`,
voice 350, measured at 2.44 words per second, so runtime is `words / 2.44`.
Stills are Magnific text-to-image at 75 credits each; twelve stills and one
narration came to 1,028 credits.

## The finished batch

Twelve reels, all Photo Cut, all under the ninety second Reels ceiling.

| reel | runtime | cuts | average shot |
|---|---|---|---|
| You Might Not Need A New Job | 47.7s | 35 | 1.36s |
| Follow Your Passion Is Bad Advice | 46.8s | 37 | 1.27s |
| It Is Not Too Late | 52.1s | 36 | 1.45s |
| Apply At Sixty Percent | 52.0s | 42 | 1.24s |
| Being Good At It Is The Trap | 46.8s | 37 | 1.27s |
| You Are Solving The Wrong Problem | 47.9s | 40 | 1.20s |
| Stop Asking For A Job | 51.8s | 38 | 1.36s |
| Some Of Your Problems Are Gravity | 55.5s | 41 | 1.35s |
| A Two Week Log Beats Guessing | 49.1s | 39 | 1.26s |
| You Have Three Next Jobs | 57.8s | 42 | 1.38s |
| Try The Job Before You Take It | 51.9s | 39 | 1.33s |
| Your Degree Decided Nothing | 45.4s | 38 | 1.19s |

Palette conformance, measured on the delivered files at two frames a second:
mean distance from the locked ramp runs 6.2 to 7.2 of 255 across the eleven
reels, worst single frame 12.4. That is JPEG noise, so nothing drifted.

Cost for the eleven: 102 stills at 75 credits and eleven narrations at about
130, roughly 9,100 Magnific credits. No Higgsfield image or video credits were
spent; the sandbox was used only for ffmpeg, whisper and the frame renderer.

## A note on assets/urls.json

`resolve.py` needs a `urls.json` next to it mapping each still identifier to its
production id and signature. That file is generated per batch and git-ignored,
because the signatures it carries expire two days after the stills are made. To
rebuild a reel after that, regenerate the stills and write a fresh map.
