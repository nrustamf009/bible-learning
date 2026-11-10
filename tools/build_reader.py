#!/usr/bin/env python3
"""Bundle all data + art into the web reader.

Output:
  site/index.html     full page: open in a browser or publish on GitHub Pages
  site/fragment.html  same page without <html>/<head> (for embedding / Claude artifacts)

Art for each panel, in order of preference:
  art/<style>/<episode>/<panel>.png (+ <panel>.orthodox.png)   generated / illustrated
  art/<style>/<episode>/<panel>.svg                              drawn by tools/render_art.py
SVG is embedded as text; the reader removes the nimbus layer for the
Protestant edition at runtime, so each picture is stored only once.
PNG files are linked by relative path (too big to embed).

Usage:  python3 tools/build_reader.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
STYLES = ("kids", "adults")


def j(p):
    return json.loads((ROOT / p).read_text())


def compact_svg(s):
    s = re.sub(r"(\d{2,})\.\d+", r"\1", s)
    s = re.sub(r"(\d\.\d)\d+", r"\1", s)
    return re.sub(r">\s+<", "><", s)


def art_src(svg_path, png_dir=None, pid=None, ident=""):
    if png_dir is not None and pid and (png_dir / f"{pid}.png").exists():
        out = {"id": ident, "png": "../" + str((png_dir / f"{pid}.png").relative_to(ROOT))}
        if (png_dir / f"{pid}.orthodox.png").exists():
            out["pngOrth"] = "../" + str((png_dir / f"{pid}.orthodox.png").relative_to(ROOT))
        return out, True
    if svg_path.exists():
        return {"id": ident, "svg": compact_svg(svg_path.read_text())}, False
    return None, False


def verses_for(scr, ref):
    out = []
    end = ref.get("end")
    chap, v = ref["chapter"], ref["from"]
    last_c, last_v = (end["chapter"], end["verse"]) if end else (ref["chapter"], ref["to"])
    multi = bool(end)
    while (chap, v) <= (last_c, last_v):
        text = scr["chapters"].get(str(chap), {}).get(str(v))
        if text is None:
            if str(chap + 1) in scr["chapters"] or (end and chap < last_c):
                chap, v = chap + 1, 1
                continue
            break
        out.append({"label": f"{chap}:{v}" if multi or v == ref["from"] else str(v), "text": text})
        v += 1
    return out


def prompts_for(ep_id, style):
    d = ROOT / "prompts" / ep_id / style
    return {f.name[:-4]: f.read_text() for f in sorted(d.glob("*.txt"))} if d.exists() else {}


def main():
    data = {"series": j("data/episodes.json"), "characters": j("data/characters.json"), "sources": j("data/sources.json"), "glossary": j("data/glossary.json"), "about": j("data/about.json"), "extras": j("data/extras.json"),
            "episodes": {}, "sheets": {}}
    scripture = {"en": j("data/scripture/en-bsb/mark.json"), "ru": j("data/scripture/ru-synodal/mark.json")}
    data["hero"] = {}
    data["portraits"] = {}
    for style in STYLES:
        data["portraits"][style] = {}
        for f in sorted((ROOT / "art" / style / "portraits").glob("*.svg")):
            data["portraits"][style][f.stem], _ = art_src(f, ident=f"por-{style}-{f.stem}")
    for style in STYLES:
        data["sheets"][style], _ = art_src(ROOT / "art" / style / "character-sheet.svg", ident=f"sheet-{style}")
        data["hero"][style], _ = art_src(ROOT / "art" / style / "hero.svg", ident=f"hero-{style}")
    for ep_dir in sorted((ROOT / "episodes").iterdir()):
        if not (ep_dir / "episode.json").exists():
            continue
        ep = json.loads((ep_dir / "episode.json").read_text())
        content = json.loads((ep_dir / "content.json").read_text())
        sc = {}
        for lang, s in scripture.items():
            vs = verses_for(s, ep["ref"])
            sc[lang] = {"translation": s["translation"], "license": s["license"], "verify": bool(s.get("verify")),
                        "verses": vs, "hasText": len(vs) > 0}
        art, real, cover = {}, {}, {}
        for style in STYLES:
            art[style], real[style] = {}, False
            for p in ep["panels"]:
                src, r = art_src(ROOT / "art" / style / ep["id"] / f"{p['id']}.svg", ROOT / "art" / style / ep["id"], p["id"], f"{style}-{ep['id']}-{p['id']}")
                if src:
                    art[style][p["id"]] = src
                real[style] = real[style] or bool(src)
            if not all(p["id"] in art[style] for p in ep["panels"]):
                real[style] = False
            if ep.get("cover"):
                cover[style], _ = art_src(ROOT / "art" / style / "covers" / f"{ep['cover']}.svg", ident=f"cover-{style}-{ep['cover']}")
            else:
                cover[style] = art[style].get("p5") or next(iter(art[style].values()), None)
        data["episodes"][ep["id"]] = {"episode": ep, "content": content, "scripture": sc, "art": art, "hasArt": real,
                                      "cover": cover, "prompts": {s: prompts_for(ep["id"], s) for s in STYLES}}

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    frag = (SITE / "template.html").read_text().replace("/*__DATA__*/null", payload)
    (SITE / "fragment.html").write_text(frag)
    head, rest = frag.split("<style>", 1)
    full = ('<!doctype html>\n<html lang="ru" data-skin="adults">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "<style>\n:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}\n[hidden]{display:none!important}\nimg{max-width:100%}\n"
            + rest.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n")
    (SITE / "index.html").write_text(full)
    print("site/index.html", round(len(full) / 1024), "KB;", len(data["episodes"]), "episodes")


if __name__ == "__main__":
    main()
