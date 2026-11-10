#!/usr/bin/env bash
# Rebuild everything in the right order.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/authoring/season1.py      # episodes 1-8: storyboards + texts
python3 tools/authoring/glosses.py      # glossary + pilot glosses
python3 tools/render_art.py             # all art; places speech bubbles
python3 tools/portraits.py              # cast portraits
python3 tools/authoring/glosses_s1.py   # margin glosses for episodes 1-8
python3 tools/authoring/extras.py      # before-you-read cards, map places, quizzes
python3 tools/build_prompts.py
python3 tools/build_reader.py
