#!/usr/bin/env python3
"""Head-and-shoulders portraits of every character, in both styles.

art/<kids|adults>/portraits/<id>.svg  — used for the cast cards in the reader.
Run: python3 tools/portraits.py
"""
import json
from pathlib import Path

from art_engine import Art, kid, mix, shade, glow, grain, paper, _char
from silhouette import sil

ROOT = Path(__file__).resolve().parent.parent
IDS = [c["id"] for c in json.loads((ROOT / "data/characters.json").read_text())["characters"]]


def kid_portrait(cid):
    A = Art(240, 240)
    c = _char(cid)
    bg = mix(c.get("mantle") or c.get("tunic", "#888"), "#FFF6E0", .62)
    A.add(f'<rect width="240" height="240" fill="{bg}"/>')
    A.add(f'<circle cx="120" cy="250" r="150" fill="{mix(bg, "#fff", .4)}"/>')
    s = 1.55
    A.add(kid(A, cid, 120, 112 + 152 * s, s, "stand", "smile", nimbus=False))
    A.add(paper(A, .1))
    return A


def adult_portrait(cid):
    A = Art(240, 240)
    c = _char(cid)
    tint = c.get("mantle") or c.get("tunic", "#888")
    A.add(f'<rect width="240" height="240" fill="{A.lin([(0, mix(tint, "#F2D7A6", .55)), (1, mix(tint, "#3A2A1E", .35))])}"/>')
    A.add(glow(A, 200, 70, 200, "#FFF0D0", .9))
    h = 660
    A.add(sil(A, cid, 112, 92 + h - h / 7.3 * .5, h, "stand", 1, (1, -.3), "#FFF2D6", "#100A08", tint=.78))
    A.add(grain(A, .12))
    return A


def main():
    for style, fn in (("kids", kid_portrait), ("adults", adult_portrait)):
        d = ROOT / "art" / style / "portraits"
        d.mkdir(parents=True, exist_ok=True)
        for cid in IDS:
            try:
                (d / f"{cid}.svg").write_text(fn(cid).svg())
            except KeyError:
                pass
    print("portraits:", len(IDS))


if __name__ == "__main__":
    main()
