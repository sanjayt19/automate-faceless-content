# Vertical Animated Series: Build Plan

Owner: Sanjay. Created 2026-09-10. Target: 5 publish-ready episodes by Sat 2026-09-12.
Platforms: Instagram Reels, Facebook Reels, YouTube Shorts.

---

## 1. Findings: existing GitHub repos

### This repository
`sanjayt19/automate-faceless-content` is a fork of `cporter202/automate-faceless-content`.
It is an affiliate-marketing course for Syllaby.io and ViralWave Studio. It contains
markdown lessons and referral links. There is no code, no pipeline, no automation.
Value: near zero for our build. Keep the branch, put our work in `pipeline/`, ignore the rest.

### Open-source candidates reviewed

| Repo | Stars | Stack | Verdict |
|---|---|---|---|
| harry0703/MoneyPrinterTurbo | ~75k | Python, FFmpeg | Stock footage + TTS. Cannot produce an animated look. Reject. |
| RayVentura/ShortGPT | ~7k | Python | Same stock-footage ceiling. Reject. |
| gyoridavid/short-video-maker | ~1.3k | TypeScript | Clean IG/Shorts renderer. Useful as reference for output specs only. |
| claude-faceless-shorts-creator | ~230 | TS, Remotion, ElevenLabs | Closest to "Claude drives it end to end". Good fallback path. |
| claude-remotion-skill | ~142 | TS, Remotion | Motion-graphics skill for Claude. Useful if we go text-on-screen. |
| reelforge | ~82 | JS | Agent-native brief to narrated subtitled video. Reference for the brief schema. |
| sasharun/awesome-faceless | n/a | List | Tool directory. Useful for scanning alternatives. |
| n8n social templates | n/a | n8n | Real value is in the publishing layer, not generation. |

**Conclusion.** Every mature open-source pipeline is a stock-footage-plus-TTS assembler.
None of them make original animation, which is the entire point of the reference channel.
Do not ingest one as the base. Use them only for the publish and orchestration layer.

### What we already have that beats all of them

The Higgsfield MCP server is connected to this session and carries a production
`faceless-video` workflow, version 2.4. It is a 10-phase pipeline: intake, style lock,
character and location asset roster, script and block plan, batch video generation,
narration in a single locked voice, assembly, burned subtitles, thumbnail, delivery.
Output is one finished 9:16 MP4 with captions.

Two of its five channel types map directly onto a "2-Minute Novelist" style series:
- **Fairy Tale & Myth**, Cinematic Storybook look. Hand-painted 2D, animated on twos,
  2 to 3 minutes, hushed storyteller voice. This is the closest match.
- **Picture Story** in stills mode. One held illustration per spoken beat, timed to the
  audio. Much cheaper and faster per episode.

Account state: Creator plan, 5,633 credits available.

Magnific MCP is also connected and covers upscaling, music, SFX, and voice work if needed.

---

## 2. Review of the ChatPRD document

### What is right and worth keeping
- Naming convention and episode ID scheme.
- Rights register for every font, voice, track, and AI output.
- The QA checklist, particularly the sound-off review pass.
- Release log and the per-episode analytics fields.
- 9:16 safe areas and caption legibility rules.
- The originality guardrail: format inspiration only, never character design or composition.

### What is wrong for this goal
1. **It is an operations manual, not an automation spec.** It describes a solo human
   studio with SOPs and handoffs. You asked for a few button clicks. The PRD never names
   a tool, an API, a file format, or a data model.
2. **The schedule does not fit.** Phases 1 to 4 total 11 to 16 days before the first
   pilot. Saturday is two days away.
3. **The core non-goal blocks the work.** "Selecting the final subject matter" is
   excluded, but you cannot generate five episodes without deciding the format. The
   content decision is the actual blocker, not the pipeline.
4. **Platform mismatch.** The PRD targets TikTok. You asked for Facebook.
5. **Over-scoped for a pilot.** Capacity models, collaborator handoff kits, and decision
   logs are week-six problems. Build them after the format is proven.

### Verdict
Keep the PRD as the quality and rights charter. Do not use it as the build sequence.

---

## 3. The plan

### Architecture

```
Episode brief (YAML in repo)
        |
        v
Claude + Higgsfield faceless-video workflow
   style lock -> asset roster -> script -> blocks -> VO -> assembly -> captions
        |
        v
Finished 9:16 MP4 + SRT + cover image
        |
        v
Review gate (you approve or reject)
        |
        v
Publish: manual for pilots, API automated from week 2
```

The repeatable unit is the episode brief. Everything downstream is one command.

### Consistency strategy
Lock these once, reuse across every episode:
- One style preset, chosen in episode 1 and never changed.
- One narrator voice ID.
- One caption style, font, and position.
- A character sheet for any recurring on-screen presence.
- One cover-frame template.

These live in `pipeline/series-lock.yml`. Drift between episodes is the single biggest
failure mode for this format, and locking these files is the fix.

### Timeline to Saturday

**Thursday, today.** Answer the four open questions below. Lock format, style, and length.
Produce episode 1 end to end as the calibration run. Review it together.

**Friday.** Batch-produce episodes 2 through 5 using the locked style. Run QA on all five.
Write titles, captions, hashtags, and covers. Set up the three accounts if not already live.

**Saturday.** Final review, publish or schedule, log the release data.

Episodes 2 to 5 are much faster than episode 1 because the style, voice, caption, and
character assets are already locked.

### Publishing

Two tiers, because the fully automated path cannot be ready by Saturday.

**Tier 1, this weekend.** Manual upload, or a scheduler with an existing Meta connection
such as Metricool or Buffer. No app review, no waiting.

**Tier 2, week two.** Direct API publishing.
- Instagram and Facebook: Meta Graph API, requires a Business account, a linked Page, a
  Meta developer app, and approved `instagram_business_content_publish` permission.
  App review takes days to weeks. Limit is 25 published posts per 24 hours.
- YouTube: Data API v3 `videos.insert`. Uploads bill to a separate bucket of roughly 100
  calls per day, so quota is not a constraint at our volume.
- Faster alternative: a posting aggregator such as Blotato or upload-post, driven from
  n8n or a small script. Skips Meta app review entirely at the cost of a subscription.

Start Meta app review on Friday so it is running while we publish tier 1.

### Cost control
Before the first paid run, call `get_cost` and price both a stills episode and a
motion episode. Stills mode is materially cheaper. If motion is more than roughly 400
credits per episode, produce the pilot five in stills mode and reserve motion for the
episodes that prove out.

---

## 4. Open questions

1. **Format.** What exactly is the episode? Classic novels retold in two minutes,
   original short fiction, or something else?
2. **Visual style.** Painterly cinematic storybook motion, or flat illustrated stills
   with camera moves?
3. **Length.** 45 to 60 seconds, or a full 2 to 3 minutes?
4. **Publishing tier.** Manual this weekend and automate later, or block on full API
   automation?

---

## 5. Claude Code or Cowork

Both, on different halves.

**Claude Code**, this session, for building: the repo, the episode brief schema, the
series lock file, the publishing scripts, the n8n workflows, and the QA checks. It is
also where the Higgsfield generation runs are driven from today.

**Cowork** for the weekly production run once the pipeline is stable. It keeps files,
connects to Drive and Gmail, and is chat-driven rather than terminal-driven. Reviewing
five videos, approving assets, and filing them belongs there.

One caveat about this session specifically: the container is ephemeral and I cannot
play a video back to you. Higgsfield hosts the finished files at URLs, so review happens
in your browser either way.
