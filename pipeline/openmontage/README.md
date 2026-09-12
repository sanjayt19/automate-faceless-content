# OpenMontage in this project

Upstream: https://github.com/calesthio/openmontage
Pinned commit: `08e2151fa02de28a5d6a312b3d575692bf147ad7` (2026-09-05)
Licence: AGPL-3.0

## What it actually is

An orchestration layer. It generates nothing on its own. Every asset comes from
a provider it calls, and `tools/video/higgsfield_video.py` shows Higgsfield is
one of those providers rather than something it replaces. What it buys us is a
single job spec that can be pointed at a different provider without rewriting
the pipeline, plus two pieces we do not have: real stock footage search
(`tools/video/{pexels,pixabay}_video.py`, `corpus_builder.py`, `clip_search.py`)
and Manim rendering (`tools/graphics/math_animate.py`).

We vendor nothing. The clone lives in the sandbox and is pinned by commit, so an
upstream change can never alter a render we have already shipped.

## Why it is not the whole answer

It composes with Remotion (Node) and assumes provider API keys we do not hold
for Pexels or Pixabay. Until those keys exist, its free footage path is inert
and our own renderers do the work. Keep both: `pipeline/render` draws vector
scenes, `pipeline/photocut` grades photographs, and OpenMontage becomes the
front end when we want provider choice per shot.

## Bootstrap

    bash pipeline/openmontage/bootstrap.sh

Clones the pinned commit into `/home/user/openmontage` inside the sandbox and
installs the sixteen Python dependencies. Run it once per sandbox lease.
