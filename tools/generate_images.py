#!/usr/bin/env python3
"""Generate the real art from the prompts with an image model (OpenAI Images API).

Order matters for consistent characters:
  1. character sheets   python3 tools/generate_images.py prompts/characters/jobs.json
  2. episode panels     python3 tools/generate_images.py prompts/ep12-storm/jobs.json
Panels are generated with the character sheets attached as reference images
(images.edit), so faces and clothes stay the same from panel to panel.

Setup:
  pip install openai
  export OPENAI_API_KEY=...        (never commit the key)

Options:
  --model gpt-image-1    image model name (change when a newer one is available)
  --quality high|medium|low
  --only kids|adults     one style only
  --variant base|orthodox
  --force                regenerate even if the file exists
  --dry-run              print what would be generated

After generating: python3 tools/build_reader.py  (the reader picks up the PNGs).
"""
import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("--model", default="gpt-image-1")
    ap.add_argument("--quality", default="high")
    ap.add_argument("--only")
    ap.add_argument("--variant")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    jobs = json.loads((ROOT / a.jobs).read_text() if not Path(a.jobs).is_absolute() else Path(a.jobs).read_text())
    jobs = [j for j in jobs if (not a.only or j["style"] == a.only) and (not a.variant or j.get("variant", "base") == a.variant)]
    if not a.dry_run:
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("pip install openai")
        client = OpenAI()

    for j in jobs:
        out = ROOT / j["out"]
        if out.exists() and not a.force:
            print("skip  ", j["out"])
            continue
        prompt = (ROOT / j["prompt_file"]).read_text()
        refs = [ROOT / r for r in j.get("references", []) if (ROOT / r).exists()]
        print(("dry   " if a.dry_run else "make  ") + j["out"], f"(+{len(refs)} reference images)")
        if a.dry_run:
            continue
        if refs:
            files = [open(r, "rb") for r in refs]
            try:
                res = client.images.edit(model=a.model, image=files, prompt=prompt, size=j["size"], quality=a.quality)
            finally:
                for f in files:
                    f.close()
        else:
            res = client.images.generate(model=a.model, prompt=prompt, size=j["size"], quality=a.quality)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.b64decode(res.data[0].b64_json))


if __name__ == "__main__":
    main()
