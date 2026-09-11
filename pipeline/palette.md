# Palette — locked

Supplied by the channel owner. These four are the only colours used in any reel
of this batch. No tints, no shades, no substitutions, no additional accents.

| Role | Hex | Used for |
|---|---|---|
| Red | `#E63946` | The single thing each reel is about. One hero element per frame, never two |
| Paper | `#F1FAEE` | The ground, and always the ground behind the caption band |
| Navy | `#1D3557` | All type, all rules, all outlines, all marks |
| Sky | `#A8DADC` | Supporting fills, secondary shapes, the "before" state in a comparison |

## Contrast rules

Navy on paper is the primary pairing and it is what the captions use: navy fill
with a paper-coloured halo. That pair is legible at phone size, outdoors, on a
dimmed screen.

Never set navy type over red. Never set sky type on paper. Both fail at reel size.

The caption band is always paper. Because we draw every frame, this is enforced
in the drawing code rather than left to chance: no artwork is placed inside the
band, so the caption always sits navy-on-paper.

Red and sky may sit next to each other. Red is the accent of attention and
appears once per frame. Sky carries everything that is context rather than point.
