#!/usr/bin/env python3
"""Build ready-to-paste image prompts from the data files.

A prompt = style block + scene (from episode.json) + fixed character looks
(from data/characters.json) + place looks + negative list.
Same input -> same prompt, which is what keeps characters consistent.

Output:
  prompts/characters/<style>/<character>.txt   reference sheets (make these FIRST)
  prompts/<episode>/<style>/<panel>.txt        one file per panel
  prompts/<episode>/<style>/<panel>.orthodox.txt  same + halo (only panels with Jesus)
  prompts/<episode>/PROMPTS.md                 everything on one page, for ChatGPT / Codex
  prompts/<episode>/jobs.json                  machine-readable list for generate_images.py

Usage:  python3 tools/build_prompts.py [episode-id ...]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/characters.json").read_text())
STYLES = DATA["styles"]
CHARS = {c["id"]: c for c in DATA["characters"]}
PLACES = {p["id"]: p for p in DATA["places"]}
HALO = DATA["traditionLayers"]["orthodox"]["promptAddon"]
SIZE = {"panel": "1536x1024", "sheet": "1536x1024"}


def character_block(ids, style):
    lines = []
    for cid in ids:
        c = CHARS[cid]
        lines.append(f"- {c['look']}; {c[style]}")
    return "\n".join(lines)


def panel_prompt(ep, panel, style, orthodox=False):
    st = STYLES[style]
    places = "; ".join(PLACES[p]["look"] for p in ep.get("place", []))
    parts = [
        f"STYLE: {st['prompt']}.",
        f"SCENE ({panel['camera']}): {panel['scene'][style]}.",
        f"SETTING: {places}.",
        "CHARACTERS (keep exactly the same look in every image):\n" + character_block(panel["characters"], style),
        "COMPOSITION: wide 3:2 frame; keep the top quarter of the image calm and uncluttered (speech bubbles will be added later).",
    ]
    if orthodox and "jesus" in panel["characters"]:
        parts.append(f"DETAIL: {HALO}.")
    parts.append(f"AVOID: {st['negative']}.")
    return "\n\n".join(parts)


def sheet_prompt(cid, style):
    st = STYLES[style]
    c = CHARS[cid]
    return "\n\n".join([
        f"STYLE: {st['prompt']}.",
        f"CHARACTER REFERENCE SHEET of one character: {c['look']}; {c[style]}.",
        "LAYOUT: plain light background, the same character shown 4 times: front view, three-quarter view, side view, and a close-up of the face with three expressions (calm, surprised, sad). Full body visible, consistent proportions and clothing in every view.",
        f"AVOID: {st['negative']}.",
    ])


def build(ep_id):
    ep = json.loads((ROOT / "episodes" / ep_id / "episode.json").read_text())
    out = ROOT / "prompts" / ep_id
    jobs, md = [], [f"# Image prompts — {ep['title']['en']} / {ep['title']['ru']} (Mark {ep['ref']['chapter']}:{ep['ref']['from']}–{ep['ref']['to']})\n",
                    "How to use: generate the character reference sheets first (prompts/characters), then attach the sheets of the characters in the panel as reference images together with the panel prompt. Size 1536x1024. Save as art/<style>/<episode>/<panel>.png (and <panel>.orthodox.png for the halo version).\n"]
    for style in ("kids", "adults"):
        md.append(f"\n## {STYLES[style]['name']['en']}\n")
        for panel in ep["panels"]:
            for orth in (False, True):
                if orth and "jesus" not in panel["characters"]:
                    continue
                suffix = ".orthodox" if orth else ""
                text = panel_prompt(ep, panel, style, orth)
                f = out / style / f"{panel['id']}{suffix}.txt"
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text + "\n")
                jobs.append({"style": style, "panel": panel["id"], "variant": "orthodox" if orth else "base",
                             "prompt_file": str(f.relative_to(ROOT)),
                             "references": [f"art/{style}/characters/{c}.png" for c in panel["characters"]],
                             "out": f"art/{style}/{ep_id}/{panel['id']}{suffix}.png", "size": SIZE["panel"]})
                if not orth:
                    md.append(f"\n### {panel['id']} · verses {', '.join(map(str, panel['verses']))}\n\n```text\n{text}\n```\n")
    (out / "PROMPTS.md").write_text("".join(md))
    (out / "jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=1))
    return len(jobs)


def build_sheets():
    jobs = []
    for style in ("kids", "adults"):
        for cid in CHARS:
            f = ROOT / "prompts" / "characters" / style / f"{cid}.txt"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(sheet_prompt(cid, style) + "\n")
            jobs.append({"style": style, "character": cid, "prompt_file": str(f.relative_to(ROOT)),
                         "references": [], "out": f"art/{style}/characters/{cid}.png", "size": SIZE["sheet"]})
    (ROOT / "prompts" / "characters" / "jobs.json").write_text(json.dumps(jobs, indent=1))
    return len(jobs)


if __name__ == "__main__":
    eps = sys.argv[1:] or [p.name for p in (ROOT / "episodes").iterdir() if (p / "episode.json").exists()]
    print("character sheets:", build_sheets())
    for e in eps:
        print(e, "panel prompts:", build(e))
