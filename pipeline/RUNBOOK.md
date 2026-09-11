# Shvii reels: production runbook

Everything one person needs to take a book, or any body of ideas, and ship a
finished vertical explainer reel. Seven episodes were built this way. The
numbers, the constraints and the failure modes below are all measured, not
guessed.

Read this once end to end before your first episode. After that, section 6 is
the only part you work from.

---

## 1. What this channel is

Short vertical videos for job seekers, published to Instagram Reels, Facebook
Reels and YouTube Shorts. Each one takes a single useful idea from a book and
explains it plainly in about eighty seconds.

The audience is an adult who has been applying for months and is getting
nothing back. They have been sold a lot of nonsense already. The editorial rule
follows from that: say the true thing, say what it costs, and never pitch the
product inside the video. Not one of the seven scripts mentions Shvii. The
account bio does the selling. The video earns the right to be believed.

**What counts as on-brand**

- A mechanism the viewer did not know, explained so they could act on it today.
- Numbers where we have them, absent where we do not.
- Naming the uncomfortable part. "One in five postings is not real" is the kind
  of line that buys attention.

**What does not**

- Hustle-speak, life hacks, "secrets recruiters don't want you to know".
- Any claim we cannot source back to the book or to public data.
- Motivation without mechanism.

---

## 2. The constraint set

These are hard walls. Every one of them was found by hitting it.

| Constraint | Value | Where it comes from |
|---|---|---|
| Runtime ceiling | 90 seconds | Below this a video is eligible for the Instagram Reels tab. Over it, it is not. Target 85. |
| Runtime floor | 5 seconds | Same eligibility rule. Never a problem in practice. |
| Aspect | 9:16 | All three platforms. |
| Beat density | 25 to 35 beats per minute | `validate_picture_story.py` rejects the script outside this band. |
| Words per phrase | 4 to 8 | Same validator. Caption legibility. |
| Total words | duration x 2.5 maximum | Same validator. This is a ceiling, not a target. See section 4. |
| Longest held frame | 1.5 seconds | `assemble_slides.sh` fails the build above this. |
| Shortest held frame | 0.7 seconds | Below this the cut reads as a flicker. |
| Frame count floor | ceil(narration seconds / 1.5) | The assembler asserts it. An 85 second episode needs at least 57 frames. |
| Genre | education, history, kids or storytelling | The validator accepts nothing else. We use education. |

The two that interact badly: the beat-density floor forces at least 36 beats
into a 90 second video, and the 1.5 second hold ceiling forces roughly two
frames per beat. So **70 to 81 images per episode is the floor, not a choice.**
Any plan that assumes twenty images per video is wrong.

---

## 3. The seven-step pipeline

```
  1  pick the idea        ->  script.md
  2  write the beats      ->  script_manifest.json
  3  narrate              ->  narration mp3 (Higgsfield TTS)
  4  align and coarsen    ->  scene_manifest.json, frames.tsv
  5  write frame prompts  ->  frame_prompts.json
  6  generate frames      ->  frame_results.json
  7  assemble and upload  ->  final mp4
```

Steps 4 and 7 run inside the Higgsfield sandbox. Everything else is local.

Every episode lives in `pipeline/episodes/<epNN-slug>/` and carries the same
nine files. `run_state.json` is the ledger: it records the narration URL, every
frame job id, the alignment similarity and finally the output URL. If a session
dies, `run_state.json` is how the next one picks up without regenerating
anything.

---

## 4. Writing the script

**Length is the whole game.** The validator's word ceiling is duration x 2.5,
but the narrator does not read at 2.5 words per second. Measured across seven
episodes, Arthur reads at **1.9 to 2.3 words per second**, and it drifts. Write
to the validator's ceiling and the render comes back at 95 seconds and is
unusable.

Use this instead:

| Target runtime | Write this many words |
|---|---|
| 77s | 176 |
| 81s | 178 |
| 83s | 178 |
| 87s | 165 |

Those are real episodes. Note that 165 words produced a *longer* video than
178 did. Sentence-end punctuation is why: every full stop adds roughly 0.66
seconds of breath. Converting full stops to commas across a whole script bought
about three seconds, which is not enough to rescue an over-long take. **Word
count is the only reliable lever. Cut words.**

If a take comes back over 90 seconds, do not try to speed it up in post. Cut
ten words and re-narrate. It costs one TTS call.

**Structure that works**

1. **Beat 1 is the hook and it must land inside three seconds.** Not a preamble,
   not a question, not "let's talk about". A concrete failure state the viewer
   is in right now. "Twenty messages, zero replies." "Job searches die in week
   three."
2. Name the wrong explanation the viewer currently believes, and kill it.
3. Give the mechanism. This is the body, roughly half the runtime.
4. Give the procedure. Numbered, small, doable this week.
5. Close on the single sentence worth remembering. No sign-off, no call to
   action, no "follow for more". The loop back to the start is the retention
   device.

**Beats** are phrase-sized, 4 to 8 words, one visual idea each. Forty beats is
a comfortable count for an eighty-second episode. Write them so that reading
the beat list alone still tells the story, because for a silent viewer the
captions *are* the video.

**Rights.** Ideas and facts are not copyrightable, expression is. So: our own
words throughout, no quoted passages, no cover art, no author likeness, title
and author named as attribution. That policy is in `series-lock.yml` and it is
not negotiable.

---

## 5. The visual system

One style, locked, across the whole channel. Editorial Motion Graphics: flat
vector, cream ground, muted slate and terracotta, one simplified faceless
figure, heavy negative space. It is deliberately unfashionable. It reads as a
serious publication rather than a content account, which is the point.

Frames come in two kinds and the rhythm between them is what makes the video
feel authored rather than generated.

- **KIND-A, a new framing.** Composed fresh from the asset roster. Costs a full
  prompt.
- **KIND-B, an edit.** Takes the previous frame as reference and changes
  **exactly one visible thing.** Same composition, same crop, same camera, same
  colours. The prompt says so explicitly, because the model will happily redraw
  everything if you let it.

Rules: never more than two edits in a row, never more than two new framings in
a row. Two consecutive edits with the same change description produce an
identical frame and a visible stall. Check for duplicate `change_only` lines
before generating. This bit us once on episode 6.

**The asset roster** is ten reference media ids, reused across every episode.
Reusing them is the single biggest cost saving in the pipeline and the reason
the character looks like the same character in episode 7 as in episode 1. They
are recorded in `frame_config.json` in each episode directory. Do not generate
new props unless a script genuinely needs one.

---

## 6. Running an episode

Prerequisites: a Higgsfield account with credits, and this repository. All
sandbox scripts fetch their inputs from GitHub by commit SHA, so **commit and
push before every sandbox call.**

### 6.1 Narrate

Higgsfield `generate_audio`, model `text2speech_v2`, variant `elevenlabs`, the
text goes in `prompt` not `text`. Voice is Arthur, preset, id
`30fc8796-ceb6-4a66-b3a7-4a145ef7f346`. Record the returned mp3 URL in
`run_state.json`.

Check the duration before doing anything else. Over 90 seconds, cut words and
go again.

### 6.2 Build the timeline

```
REF=<commit-sha> bash build_timeline.sh <episode-dir> <narration-mp3-url>
```

This transcribes with faster-whisper, aligns the authored beats to the word
timestamps, then coarsens so each beat uses the fewest frames allowed.

Two things to read off the output. **Alignment similarity** should be above
0.95; ours ranged 0.95 to 0.98. Below 0.90 means the narration and the script
have drifted apart and you should look at why. **Frame count** goes into the
assembly call later.

Do not pass `--requested-duration`. It is optional, and supplying it makes the
aligner reject any take outside a tolerance you did not choose. Gate on the 90
second ceiling yourself.

Paste the printed table into `frames.tsv`.

### 6.3 Write the frame prompts

```
python3 build_frame_prompts.py <episode-dir>
```

Reads the script manifest, the frame table and the asset config, emits
`frame_prompts.json`. Read the output. Look for duplicate consecutive change
lines and for any edit prompt that has drifted into describing a whole new
scene.

### 6.4 Generate the frames

`generate_image_batch`, model `seedream_v5_pro`, `aspect_ratio` 9:16,
`resolution` 1.5k, `use_unlim` false. Reference assets go in `medias` with role
**`image_references`**. Batches of 8 to 12. Poll with `jobs_wait`.

Expect `429 rate_limit_reached`. It gets worse the longer a session runs. Early
on, twelve of twelve succeed; late in a long session, two of seven. Handle it
by capping batch size, sleeping between submissions and resubmitting the failed
indices. Write every job id into `run_state.json` as you go, so a dropped
session costs nothing.

When all frames are done, write `frame_results.json` in the shape
`{"frames": [{"output_slot": "frame-001", "job_id": "...", "url": "..."}]}`
and verify the count against `run_state.json` before moving on.

**Commit and push.**

### 6.5 Assemble

Get a presigned upload URL first with `media_upload`. Then:

```
REF=<commit-sha> bash assemble_episode.sh <episode-dir> <narration-mp3-url> \
  <frame-count> <requested-seconds> <upload-url>
```

Run it with `background: true` and poll the log. It takes fifteen to twenty
minutes. When the log prints `UPLOADED` and `DONE`, call `media_confirm` with
type `video` and the media id.

Record the output URL, runtime, frame count, caption count and alignment
similarity in `run_state.json`, set `status` to complete, commit and push.

### 6.6 Write the publishing copy

`publish.md` in the episode directory: YouTube title with `#shorts`,
long description, Reels caption, hashtags, and a note on which frame to use as
the cover. Then add the episode to `captions-and-hashtags.md`, which is the
sheet whoever posts actually works from.

---

## 7. Failure modes, and what they actually mean

**The sandbox is ephemeral.** It is discarded about ten seconds after a call
returns. Background jobs get a fifteen-minute lease and are killed when it
expires, mid-download, with no error. Episode 6 died this way and had to be
relaunched. It cost nothing because every frame was already generated and
recorded; that is precisely why `run_state.json` exists. Chain work into single
commands, and poll background jobs promptly.

**raw.githubusercontent.com serves stale files** for minutes and ignores
query-string cache busters. Two consecutive assembly runs silently used an old
timeline. The fix is in the scripts already: every fetch is pinned to a commit
SHA rather than a branch name. Never revert that.

**`sandbox_exec` caps the command at 16000 characters.** This is why episode
artifacts live in the repo and the sandbox pulls them, rather than being
heredoc'd in.

**Timeline gap or overlap before frame N.** Frame starts got rounded to two
decimals, leaving sub-frame gaps. Build frames so each one starts exactly where
the previous ends. The assembler fails on any discrepancy above 0.01s.

**`sleep 60` hits the 60 second tool timeout.** Use 50 to 55.

**MCP servers disconnect mid-session.** Reload the tool schemas and carry on.

---

## 8. What an episode costs

Roughly 110 to 145 credits, almost all of it frame generation.

Two things brought it down. Coarsening the timeline to a 1.48 second target
cuts the frame count to the assembler's floor, which took episode 5 to 111
credits against episode 3's 144. Reusing the ten-asset roster instead of
generating new props keeps the marginal cost of a new episode to its frames
alone.

Wall-clock is roughly two to three hours per episode, most of it waiting on
frame generation and the twenty-minute assembly.

---

## 9. Publishing and measurement

Post one per day at the same hour, in episode order. Episodes 2 through 7 are a
sequence where each answers the problem the last one set up, so posting out of
order costs the thread.

Hashtags go in the caption, not the first comment. The overlap between episodes
in an arc is deliberate and tells the ranker they are one body of work.

The first line of the caption is the only line that shows before the More cut.
Write it to stand alone.

Facebook Reels takes the same file and the same caption. YouTube Shorts takes
the longer description from `publish.md`.

At 48 hours, log for every episode: reach, three-second views, average view
duration, completion rate.

**Completion rate is the decision number.** It tells you whether the format
holds, and it is the only one worth acting on. Reach without completion means
the hook worked and the body did not. Do not commission a new arc until the
current one has 48 hours of data.

---

## 10. Still open

- **Channel name and handle.** `series-lock.yml` still says TBD. Needed before
  the accounts go live and before any cover art is made.
- **Publishing is manual.** Automating it means the Meta Graph API with
  `instagram_business_content_publish` approval, and YouTube Data API v3
  `videos.insert`. Worth doing only once the format is proven.
- **One visual format has been tested.** Alternatives are being evaluated
  separately.
