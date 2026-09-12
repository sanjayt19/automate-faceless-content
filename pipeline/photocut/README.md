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
