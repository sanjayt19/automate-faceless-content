# Visual format options

Eight candidate looks for the next batch, rendered as 9:16 stills at 1.5k with
the same test caption burned in so the formats compare like for like. The test
line is the episode 6 hook.

Format A is the look the first seven episodes shipped in. The other seven are
untested.

All were generated with `seedream_v5_pro`, no reference assets, so each one is
a clean read of the style rather than a variation on the existing roster.

| Key | Format | Still |
|---|---|---|
| A | Editorial motion graphics, current look | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_056597d3-0d2a-41cd-984c-d8a4755f6788.png |
| B | Documentary photography, desaturated | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_0a7859e2-1751-49cd-98b0-dbc64b3b5873.png |
| C | Data first, one chart per frame | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_0856dc94-9434-4b70-9e56-7a09e6f108ac.png |
| D | Typographic only, no illustration | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162430_e96ea194-5511-4e75-824f-7c6b6824a6f0.png |
| E | Ink on paper, hand drawn | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_ede7020b-b9b3-4b77-ac1f-2aa72562f964.png |
| F | Dark interface, the system's side | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162430_18be7262-84e9-4a2c-a392-4d67f3aca099.png |
| G | Newsprint halftone, one spot colour | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_fa55b210-d5c4-494f-9e80-c9a6897b6313.png |
| H | Tactile top-down still life | https://d8j0ntlcm91z4.cloudfront.net/user_38wUSxud7GQiZyfLVI2S9e8x9HR/hf_20260911_162431_375a63a4-4839-4f41-b91f-511c3bedb5ee.png |

## What each one is for

**A. Editorial motion graphics.** Flat vector, cream ground, one faceless
figure. Abstract enough to illustrate anything, which is why it carried seven
episodes without a single new prop. Weakness: abstraction has no emotional
floor. Nothing in it hurts.

**B. Documentary photography.** A real person at a real table. Highest
emotional recognition of the eight, because the viewer is looking at their own
evening. Weakness: photoreal continuity across eighty frames is hard, the
person will drift, and it needs a strict no-stock-smiling rule or it turns into
a bank advert.

**C. Data first.** Every frame is one chart. Correct for the claims we actually
make, and the most credible-looking of the eight. Weakness: only works for
scripts with real numbers in them, so it constrains the writing.

**D. Typographic only.** No illustration at all. Cheapest to produce, fastest
to iterate, and impossible to get visually wrong. Weakness: it is also the
easiest to scroll past, and with burned captions already on screen you are
stacking text on text.

**E. Ink on paper.** Reads as a person explaining rather than a brand
broadcasting, which fits the honest-information posture better than anything
else here. Weakness: hand-drawn consistency across eighty frames is the hardest
continuity problem of the eight.

**F. Dark interface.** Shows the machine on the other side of the application.
The single best fit for hiring-side content, where the subject literally is a
screening system. Weakness: cold, and wrong for anything about the viewer's own
behaviour.

**G. Newsprint halftone.** Archival, serious, unmistakably not an AI content
account. Strongest scroll-stopping texture of the eight. Weakness: the style is
loud enough to compete with the message, and it dates fast.

**H. Tactile still life.** Real objects from above. Warm, quiet, credible.
Weakness: a narrow vocabulary. There are only so many ways to photograph paper,
and by episode four it repeats.

## How to choose

Pick two, not one. Run the next batch as a paired test: the same script treated
in two formats, posted a week apart on different platforms, and compare
completion rate. That is the only measurement that settles it.

If the next arc is hiring-side material, F is the obvious pair to A. If it
stays on the seeker's own behaviour, B or E.

Whatever is chosen, the production constraints do not move. Still 70 to 81
frames per episode, still a 1.5 second hold ceiling, still 90 seconds. The
format changes the prompt block in `build_frame_prompts.py` and the asset
roster in `frame_config.json`, nothing else in the pipeline.
