#!/usr/bin/env bash
# Put OpenMontage at its pinned commit into the sandbox.
set -euo pipefail
PIN=08e2151fa02de28a5d6a312b3d575692bf147ad7
DEST=/home/user/openmontage
if [ ! -d "$DEST/.git" ]; then
  git clone --quiet https://github.com/calesthio/openmontage "$DEST"
fi
cd "$DEST"
git fetch --quiet origin "$PIN" 2>/dev/null || git fetch --quiet origin
git checkout --quiet "$PIN"
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt
python3 -c "import tools.tool_registry as r; print('openmontage ready at', '$PIN'[:8])"
