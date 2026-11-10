"""One scene description, two styles.

A panel is described once (place, time of day, people, props) and drawn by
both renderers: KIDS (bright cartoon) and ADULTS (cinematic silhouettes).

Scene spec:
  {"env": {"kind": "outdoor"|"interior"|"roof"|"symbol", "time": "dawn"|"day"|"dusk"|"night",
           "ground": "sand"|"grass"|"field"|"shore"|"river"|"rock",
           "features": ["town", "palms", "reeds", "lake", "river", "rocks", "dove", "light", "stars", "door", "lamps", "window", "columns"]},
   "figs": [{"id": "jesus", "x": 600, "y": 700, "s": 1.0, "pose": "bless", "f": 1, "e": "calm",
             "kneel": False, "sit": False, "lie": False}],
   "props": [{"k": "boat", "x": .., "y": .., "s": .., "sail": "up"}, ...]}
Returns (Art, anchors) where anchors maps character id -> head position.
"""
import math
import random

from art_engine import (Art, W, H, mix, shade, smooth, poly, circ, ell, clouds, grain, paper, vignette, glow, rays, stars, ridge,
                        waves_path, wobble, kid, head_of_kid, KINK)
from silhouette import sil, head_of_sil
import render_adults as RA
from render_art import kboat, kcloud, reeds as kreeds, palm, houses, dove, net, wheat, lantern

# ------------------------------------------------------------------ palettes by time of day
K_SKY = {"dawn": ["#FFB59A", "#FFD9A8", "#FFF0C8"], "day": ["#6FC0EE", "#BFE6FA", "#E8F6FF"],
         "dusk": ["#FF8D7A", "#FFB06B", "#FFD58C"], "night": ["#1E2250", "#2F3C7A", "#4A5A9A"]}
K_HILL = {"dawn": ("#C79AB0", "#A97B98"), "day": ("#9BC48A", "#7FA872"), "dusk": ("#A8708F", "#8E6A92"), "night": ("#2A3366", "#1E2652")}
A_SKY = {"dawn": [(0, "#2E3E52"), (.45, "#B07A6A"), (.62, "#F0B888"), (.7, "#FFE0B0")],
         "day": [(0, "#4E7E96"), (.5, "#A8C6CC"), (.7, "#E8DCC0")],
         "dusk": [(0, "#2C3E4C"), (.35, "#8A5A4A"), (.58, "#E09A58"), (.7, "#FFD08C")],
         "night": [(0, "#03080C"), (.55, "#0F2830"), (.72, "#244550")]}
A_LIGHT = {"dawn": ("#FFE2B4", "#120C0A"), "day": ("#FFF4DA", "#14130F"), "dusk": ("#FFDCA0", "#140B07"), "night": ("#DDE6E6", "#02070A")}


def _k_lightdir(time):
    return (-1, -.6)


# ================================================================== KIDS
def k_env(A, env):
    kind, time = env.get("kind", "outdoor"), env.get("time", "day")
    feats = set(env.get("features", []))
    if kind == "interior":
        wall = {"house": "#E8C48E", "synagogue": "#EEE2C8", "feast": "#B9774A"}.get(env.get("room", "house"), "#E8C48E")
        if time == "night" or env.get("room") == "feast":
            wall = mix(wall, "#3A2A50", .45)
        A.add(f'<rect width="{W}" height="{H}" fill="{wall}"/>')
        A.add(f'<rect y="0" width="{W}" height="60" fill="{shade(wall, .8)}"/><path d="M0 60 H{W}" stroke="{KINK}" stroke-width="4"/>')
        if "columns" in feats:
            for x in (120, 380, 820, 1080):
                A.add(A.shaded(f"M{x-34} 62 H{x+34} V700 H{x-34} Z", [(shade(wall, .85), 0, 0), (mix(wall, "#fff", .25), -18, 0)], KINK, 4))
        if "window" in feats:
            A.add(f'<rect x="520" y="110" width="160" height="170" rx="80" fill="#BFE6FA" stroke="{KINK}" stroke-width="5"/>')
            A.add(f'<path d="M520 300 L440 720 H900 L680 300 Z" fill="#FFF4C0" opacity=".35"/>')
        if "door" in feats:
            A.add(f'<rect x="900" y="230" width="190" height="470" fill="{shade(wall, .45)}" stroke="{KINK}" stroke-width="5"/><rect x="915" y="245" width="160" height="455" fill="#FFB86B" opacity=".5"/>')
        if "lamps" in feats:
            for x in (260, 600, 940):
                A.add(f'<path d="M{x} 0 V150" stroke="{KINK}" stroke-width="3"/>' + glow(A, x, 165, 120, "#FFE07A", .7) + f'<ellipse cx="{x}" cy="165" rx="22" ry="12" fill="#C9873E" stroke="{KINK}" stroke-width="3"/><path d="M{x} 150 q8 -16 0 -26 q-8 10 0 26" fill="#FFB020"/>')
        A.add(A.shaded(f"M0 690 H{W} V{H} H0 Z", [(shade(wall, .6), 0, 0), (shade(wall, .72), 0, 10)], KINK, 4))
        return
    sky = K_SKY[time]
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, sky[0]), (.55, sky[1]), (1, sky[2])])}"/>')
    if time == "night" or "stars" in feats:
        A.add(stars(A, 70, 5, 380, "#FFF6C8", 2.4, 8))
        A.add(f'<circle cx="1040" cy="130" r="46" fill="#FFF3C9" stroke="#E9C877" stroke-width="4"/>')
    else:
        sx = 980 if time in ("dusk",) else 200 if time == "dawn" else 1020
        sy = 420 if time in ("dusk", "dawn") else 120
        A.add(glow(A, sx, sy, 220, "#FFF4C0", .8) + f'<circle cx="{sx}" cy="{sy}" r="58" fill="#FFF0B0" stroke="#F3A25A" stroke-width="5"/>')
        A.add(kcloud(A, 330, 130, 95) + kcloud(A, 780, 90, 70))
    if "light" in feats:
        A.add(rays(A, 600, -40, "#FFF6C8", .5, 12, (60, 120), 1100, 5) + glow(A, 600, 0, 420, "#FFF7D0", 1))
    if "dove" in feats:
        A.add(dove(600, 170, .8))
    h1, h2 = K_HILL[time]
    hz = env.get("horizon", 450)
    A.add(A.shaded(ridge(hz - 10, 90, 4, 7), [(shade(h1, .9), 0, 0), (h1, -20, 0)], KINK, 4))
    A.add(A.shaded(ridge(hz + 20, 50, 9, 9), [(shade(h2, .9), 0, 0), (h2, -20, 0)], KINK, 4))
    if "town" in feats:
        A.add(houses(A, 40, hz + 30, .55, 9, 3, "#8E8A96", "#B7B2BE", "#7A5A3A"))
    ground = env.get("ground", "sand")
    gcol = {"sand": "#EBC78A", "grass": "#A8D27E", "field": "#F2C14E", "shore": "#EBC78A", "river": "#EBC78A", "rock": "#D2B48C"}[ground]
    if time == "night":
        gcol = mix(gcol, "#2A3366", .55)
    if ground in ("shore",) or "lake" in feats:
        A.add(f'<rect y="{hz+20}" width="{W}" height="{H}" fill="{A.lin([(0, "#56BCE0" if time != "night" else "#3B5AA0"), (1, "#2C7CB9" if time != "night" else "#1E2A66")])}"/>')
        for i in range(10):
            A.add(f'<path d="M{random.Random(i).uniform(0, 1100):.0f} {hz+40+i*18} q22 -8 44 0" stroke="#C8EEFA" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>')
        if ground == "shore":
            A.add(A.shaded(smooth([(-20, 600), (300, 580), (620, 620), (900, 700), (1000, 820), (-20, 820)], True, .7), [(shade(gcol, .85), 0, 0), (gcol, 10, -10)], KINK, 4))
        return
    if kind == "roof":
        A.add(houses(A, -20, hz + 60, .7, 12, 8, "#8E8A96", "#B7B2BE", "#7A5A3A"))
        A.add(A.shaded(f"M-20 640 H1220 V820 H-20 Z", [("#B88A5A", 0, 0), ("#D2A472", 0, -10)], KINK, 5))
        A.add(f'<rect x="460" y="672" width="280" height="40" fill="#3A2A20" stroke="{KINK}" stroke-width="4"/>')
        return
    A.add(A.shaded(f"M-20 {hz+40} Q600 {hz+20} 1220 {hz+40} V820 H-20 Z", [(shade(gcol, .88), 0, 0), (gcol, 0, -12)], KINK, 4))
    if ground == "river" or "river" in feats:
        A.add(A.shaded(smooth([(-20, 560), (400, 545), (800, 585), (1220, 560), (1220, 640), (800, 670), (400, 625), (-20, 640)], True, .7), [("#2E86C4", 0, 0), ("#5BB4E0", 0, -8)], KINK, 4))
    if ground == "field":
        A.add(wheat(A, hz + 50, 640, "#FFE08A", "#C68A22", 2, 200, sc=.8))
    if "palms" in feats:
        A.add(palm(A, 70, 600, 1.1) + palm(A, 1120, 590, .95))
    if "reeds" in feats:
        A.add(kreeds(60, 640, 1.0, "#4C7A4E", 9, 2))
    if "rocks" in feats:
        A.add(A.shaded(smooth([(600, 690), (660, 600), (820, 590), (890, 690)], True, .7), [("#9B7A5A", 0, 0), ("#B8987A", -10, -10)], KINK, 4))


def k_prop(A, p):
    k = p["k"]
    if k == "boat":
        b, f = kboat(A, p["x"], p["y"], p.get("s", 1), p.get("tilt", 0), p.get("sail", "up"))
        return b, f
    if k == "net":
        return net(p["x"], p["y"], p.get("w", 220), p.get("h", 160), "#F4E3C0", 3), ""
    if k == "mat":
        return A.shaded(f"M{p['x']-110} {p['y']-14} H{p['x']+110} V{p['y']+14} H{p['x']-110} Z", [("#C9B48A", 0, 0), ("#E6D2A6", 0, -6)], KINK, 4), ""
    if k == "ropes":
        return f'<path d="M{p["x"]-100} 0 L{p["x"]-100} {p["y"]} M{p["x"]+100} 0 L{p["x"]+100} {p["y"]}" stroke="#F4E3C0" stroke-width="5"/>', ""
    if k == "table":
        y = p["y"]
        t = A.shaded(f"M60 {y} H1140 V{y+50} H60 Z", [("#8C5530", 0, 0), ("#B97640", 0, -10)], KINK, 5)
        food = "".join(f'<ellipse cx="{x}" cy="{y-2}" rx="44" ry="13" fill="#E9D3A8" stroke="{KINK}" stroke-width="3"/><circle cx="{x-10}" cy="{y-12}" r="10" fill="#B83A3A"/><circle cx="{x+12}" cy="{y-10}" r="9" fill="#6A9A3A"/>' for x in (220, 420, 640, 860, 1020))
        return "", t + food + f'<rect x="60" y="{y+50}" width="1080" height="200" fill="#5A3A22" stroke="{KINK}" stroke-width="5"/>'
    if k == "booth":
        x, y = p["x"], p["y"]
        return "", A.shaded(f"M{x-130} {y-90} H{x+130} V{y} H{x-130} Z", [("#8C5530", 0, 0), ("#B97640", 0, -8)], KINK, 5) + "".join(f'<circle cx="{x-80+i*28}" cy="{y-100}" r="11" fill="#F2C94C" stroke="{KINK}" stroke-width="3"/>' for i in range(6))
    if k == "hole":
        return f'<rect x="{p["x"]-130}" y="0" width="260" height="70" fill="#BFE6FA" stroke="{KINK}" stroke-width="5"/>' + rays(A, p["x"], 0, "#FFF6C8", .5, 8, (70, 110), 900, 3), ""
    if k == "loaves":
        x, y = p["x"], p["y"]
        return "", "".join(f'<ellipse cx="{x-150+i*60}" cy="{y}" rx="26" ry="16" fill="#D99A4E" stroke="{KINK}" stroke-width="3"/>' for i in range(6)) + A.shaded(f"M{x-200} {y+14} H{x+200} V{y+40} H{x-200} Z", [("#B08A2E", 0, 0), ("#E2BC62", 0, -6)], KINK, 4)
    if k == "stretcher":
        x, y, w = p["x"], p["y"], p.get("w", 260)
        return "", A.shaded(f"M{x-w/2} {y-12} H{x+w/2} V{y+12} H{x-w/2} Z", [("#C9B48A", 0, 0), ("#E6D2A6", 0, -6)], KINK, 4) + f'<path d="M{x-w/2-30} {y} H{x+w/2+30}" stroke="{KINK}" stroke-width="9" stroke-linecap="round"/><path d="M{x-w/2-30} {y} H{x+w/2+30}" stroke="#8A5A33" stroke-width="5" stroke-linecap="round"/>'
    if k == "roofhole":
        x, y = p["x"], p["y"]
        return A.shaded(smooth([(x - 150, y), (x - 120, y - 24), (x + 110, y - 30), (x + 150, y - 4), (x + 130, y + 26), (x - 130, y + 30)], True, .5), [("#2A1A12", 0, 0), ("#3A2618", 0, 6)], KINK, 5) + "".join(f'<path d="M{x-160+i*40} {y-30} l{10+i*3} -16" stroke="#7A5A3A" stroke-width="6" stroke-linecap="round"/>' for i in range(8)), ""
    if k == "skins":
        x, y = p["x"], p["y"]
        def skin(cx, cy, col, cracked):
            body = smooth([(cx - 90, cy - 60), (cx - 40, cy - 120), (cx + 50, cy - 110), (cx + 100, cy - 30), (cx + 70, cy + 70), (cx - 60, cy + 80), (cx - 110, cy + 10)], True, .9)
            out = A.shaded(body, [(shade(col, .8), 0, 0), (col, -14, -14)], KINK, 5)
            out += A.shaded(f"M{cx-30} {cy-118} Q{cx-20} {cy-170} {cx+10} {cy-175} Q{cx+30} {cy-150} {cx+20} {cy-112} Z", [(shade(col, .8), 0, 0), (col, -6, -6)], KINK, 4)
            out += f'<path d="M{cx-28} {cy-150} H{cx+22}" stroke="#F4E3C0" stroke-width="7" stroke-linecap="round"/>'
            if cracked:
                out += f'<path d="M{cx+40} {cy-80} l-20 30 l24 20 l-18 34" stroke="{KINK}" stroke-width="5" fill="none"/><path d="M{cx+60} {cy-20} q40 20 60 70" stroke="#8A1E3A" stroke-width="10" fill="none" stroke-linecap="round"/>'
            return out
        old = skin(x - 220, y, "#7A5232", True)
        new = skin(x + 200, y, "#C88A4A", False) + f'<path d="M{x+330} {y-330} q-30 60 -110 140" stroke="#8A1E3A" stroke-width="16" fill="none" stroke-linecap="round"/>' + A.shaded(f"M{x+300} {y-380} h90 v40 q0 30 -45 40 q-45 -10 -45 -40 Z", [("#B8733A", 0, 0), ("#D99A5A", -6, -6)], KINK, 4)
        return "", old + new
    if k == "skins_old":
        x, y = p["x"], p["y"]
        old = A.shaded(smooth([(x - 220, y - 160), (x - 120, y - 200), (x - 60, y - 60), (x - 140, y + 40), (x - 260, y - 20)], True, .8), [("#6E4A2A", 0, 0), ("#8C6236", -10, -10)], KINK, 4)
        crack = f'<path d="M{x-160} {y-140} l20 40 l-24 30 l26 40" stroke="{KINK}" stroke-width="4" fill="none"/>'
        new = A.shaded(smooth([(x + 60, y - 170), (x + 180, y - 210), (x + 260, y - 60), (x + 180, y + 40), (x + 40, y - 20)], True, .8), [("#B97A42", 0, 0), ("#D99A5A", -10, -10)], KINK, 4)
        wine = f'<path d="M{x+60} {y-260} q30 40 60 70" stroke="#7A1E3A" stroke-width="16" fill="none" stroke-linecap="round"/>'
        return "", old + crack + new + wine
    if k == "shadow":
        x, y = p["x"], p["y"]
        return "", f'<path d="M{x} {y} C{x+40} {y-120} {x+140} {y-160} {x+200} {y-260} C{x+120} {y-220} {x+60} {y-140} {x+20} {y-40} Z" fill="#3A2A5A" opacity=".7"/>'
    if k == "angel":
        x, y = p["x"], p["y"]
        return glow(A, x, y - 150, 160, "#FFF6D0", .9) + f'<path d="M{x-40} {y} Q{x} {y-260} {x+40} {y} Z" fill="#FFFDF0" opacity=".85"/><circle cx="{x}" cy="{y-250}" r="26" fill="#FFFDF0" opacity=".9"/>', ""
    if k == "jar":
        return "", A.shaded(smooth([(p["x"] - 22, p["y"]), (p["x"] - 30, p["y"] - 50), (p["x"] - 14, p["y"] - 80), (p["x"] + 14, p["y"] - 80), (p["x"] + 30, p["y"] - 50), (p["x"] + 22, p["y"])], True, .7), [("#B8733A", 0, 0), ("#D99A5A", -6, -6)], KINK, 4)
    return "", ""


def k_fig(A, f, orth):
    cid = f["id"]
    s = f.get("s", 1.0)
    rot = 80 if f.get("lie") else 0
    y = f["y"] + (67 * s if f.get("lie") else 0)
    svg = kid(A, cid, f["x"], y, s, f.get("pose", "stand"), f.get("e", "smile"), rot=rot, nimbus=(orth and cid == "jesus"),
              facing=f.get("f", 1), kneel=f.get("kneel", False) or f.get("sit", False))
    return svg, head_of_kid(f["x"], y, s, rot, f.get("kneel", False) or f.get("sit", False))


def render_kids(spec, orth=True):
    import places
    A = Art()
    if "place" in spec["env"]:
        places.k_place(A, spec["env"])
    else:
        k_env(A, spec["env"])
    if spec["env"].get("dove"):
        A.add(dove(600, 170, .8))
    ride = lambda r: r[0] - 205 * r[1]
    backs, fronts = [], []
    for p in spec.get("props", []):
        if p.get("ride"):
            p = dict(p, y=ride(p["ride"]))
        b, f = k_prop(A, p)
        (backs if p.get("layer", "back") == "back" else fronts).append(b)
        fronts.append(f)
    A.add("".join(backs))
    anchors = {}
    figs = [dict(f, y=ride(f["ride"]) - 22 * f["s"]) if f.get("ride") else f for f in spec.get("figs", [])]
    figs = sorted(figs, key=lambda f: (f.get("ride") is None, f["y"]))
    for f in figs:
        if not f.get("lie"):
            sc = f.get("s", 1.0)
            A.add(f'<ellipse cx="{f["x"]}" cy="{f["y"]-2}" rx="{58*sc:.0f}" ry="{11*sc:.0f}" fill="#3A2A40" opacity=".22"/>')
        svg, head = k_fig(A, f, orth)
        A.add(svg)
        anchors.setdefault(f["id"], head)
    A.add("".join(fronts))
    if spec["env"].get("front_water"):
        A.add(A.shaded(waves_path(spec["env"]["front_water"], 14, 9, 5), [("#2A6FB0", 0, 0), ("#3F8ED0", 0, 8)], KINK, 4))
    if "place" in spec["env"]:
        finish_kids(A, spec["env"])
    A.add(vignette(A, .22, "#3A1A2A"))
    A.add(paper(A, .12))
    return A, anchors


# ================================================================== ADULTS
def a_env(A, env):
    kind, time = env.get("kind", "outdoor"), env.get("time", "day")
    feats = set(env.get("features", []))
    lit, amb = A_LIGHT[time]
    if kind == "interior":
        room = env.get("room", "house")
        base = {"house": "#1A130E", "synagogue": "#1E1C18", "feast": "#120B08"}[room]
        A.add(f'<rect width="{W}" height="{H}" fill="{base}"/>')
        if "columns" in feats:
            for x in (120, 380, 820, 1080):
                A.add(f'<rect x="{x-34}" y="0" width="68" height="700" fill="{mix(base, "#000", .4)}"/><rect x="{x+26}" y="0" width="6" height="700" fill="{lit}" opacity=".25"/>')
        if "window" in feats:
            A.add(f'<rect x="520" y="90" width="160" height="190" fill="{A.lin([(0, "#E8E4D0"), (1, "#C8B88A")])}"/>')
            A.add(f'<path d="M520 280 L380 720 H940 L680 280 Z" fill="{A.lin([(0, "#FFF0C8", .45), (1, "#FFF0C8", 0)])}"/>')
            A.add(rays(A, 600, 180, "#FFF0C8", .18, 8, (60, 120), 900, 4))
        if "door" in feats:
            A.add(f'<rect x="900" y="230" width="190" height="470" fill="{A.lin([(0, "#3E6A7A"), (1, "#7A6A50")])}"/>')
        if "lamps" in feats:
            for x in (260, 600, 940):
                A.add(f'<path d="M{x} 0 V150" stroke="#3A2A1A" stroke-width="2"/>' + glow(A, x, 160, 150, "#FFC66A", .8) + f'<ellipse cx="{x}" cy="162" rx="14" ry="8" fill="#FFE2A0"/>')
        else:
            A.add(glow(A, 600, 300, 600, "#FFC66A", .25))
        A.add(f'<rect y="690" width="{W}" height="120" fill="{mix(base, "#000", .5)}"/><path d="M0 690 H{W}" stroke="{lit}" stroke-width="1.5" opacity=".35"/>')
        return lit, amb
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin(A_SKY[time])}"/>')
    hz = env.get("horizon", 460)
    if time == "night":
        A.add(stars(A, 200, 12, 480, "#E8E4DA", 1.5))
        A.add(glow(A, 1040, 130, 240, "#E8E4DA", .5) + '<circle cx="1040" cy="130" r="36" fill="#F2EEE4"/>')
    else:
        A.add(clouds(A, 0, 380, mix(A_SKY[time][-1][1], "#fff", .3), 3 + hz, (.0018, .010), 1.6, .65, .6))
        sx = 980 if time == "dusk" else 220 if time == "dawn" else 900
        sy = hz - 20 if time in ("dusk", "dawn") else 140
        A.add(glow(A, sx, sy, 420, mix(lit, "#fff", .3), .85) + f'<circle cx="{sx}" cy="{sy}" r="34" fill="#FFF8E4"/>')
    if "light" in feats:
        A.add(rays(A, 600, -60, "#FFF6D8", .45, 16, (62, 118), 1100, 6) + glow(A, 600, -20, 520, "#FFF6D8", 1))
    if "dove" in feats:
        A.add('<g transform="translate(600 170) scale(.7)"><path d="M0 0 C-40 -50 -110 -60 -150 -30 C-100 -20 -50 -5 -20 12 Z M0 0 C40 -50 110 -60 150 -30 C100 -20 50 -5 20 12 Z" fill="#FFFFFF"/><ellipse cx="0" cy="18" rx="22" ry="34" fill="#FFFFFF"/><circle cx="0" cy="52" r="14" fill="#FFFFFF"/></g>')
    far = A_SKY[time][-1][1]
    RA.hills(A, hz, mix(far, "#000", .15), mix(amb, far, .25), 2, hz, (70, 36))
    if "town" in feats:
        rnd = random.Random(hz)
        x = 40
        while x < 520:
            w, h = rnd.uniform(40, 70), rnd.uniform(26, 50)
            A.add(f'<rect x="{x:.0f}" y="{hz+8-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{mix(amb, far, .35)}"/>')
            x += w + rnd.uniform(0, 6)
    ground = env.get("ground", "sand")
    if ground == "shore" or "lake" in feats:
        RA.water(A, hz + 6, mix(far, "#6A8A8A", .4), mix(amb, "#000", .3), mix(lit, "#fff", .2), 900 if time != "dawn" else 220, hz)
        if ground == "shore":
            A.add(f'<path d="{smooth([(-30, 600), (300, 580), (620, 620), (900, 700), (980, 830), (-30, 830)], True, .7)}" fill="{amb}"/>')
        return lit, amb
    if kind == "roof":
        rnd = random.Random(3)
        x = -20
        while x < W:
            w, h = rnd.uniform(90, 150), rnd.uniform(60, 120)
            A.add(f'<rect x="{x:.0f}" y="{hz+60-h:.0f}" width="{w:.0f}" height="{h+200:.0f}" fill="{mix(amb, far, .4)}"/>')
            x += w + rnd.uniform(0, 10)
        A.add(f'<rect x="-20" y="640" width="1240" height="200" fill="{mix("#5A4030", amb, .4)}"/><path d="M-20 640 H1220" stroke="{lit}" stroke-width="2" opacity=".6"/><rect x="460" y="672" width="280" height="40" fill="#0A0604"/>')
        return lit, amb
    gcol = {"sand": "#8A6A4A", "grass": "#4A5A36", "field": "#B8862E", "river": "#8A6A4A", "rock": "#6A5A48"}.get(ground, "#7A5A3A")
    if time == "night":
        gcol = mix(gcol, amb, .6)
    A.add(f'<path d="M-20 {hz+20} Q600 {hz} 1220 {hz+20} V820 H-20 Z" fill="{A.lin([(0, mix(gcol, far, .35)), (1, mix(gcol, amb, .7))])}"/>')
    if ground == "river" or "river" in feats:
        A.add(f'<path d="{smooth([(-20, 560), (400, 545), (800, 585), (1220, 560), (1220, 640), (800, 670), (400, 625), (-20, 640)], True, .7)}" fill="{A.lin([(0, mix(far, "#8AB0B0", .5)), (1, mix(amb, "#2A4A50", .4))])}"/>')
        A.add(f'<path d="M-20 560 Q400 545 800 585 T1220 560" stroke="{lit}" stroke-width="2" fill="none" opacity=".6"/>')
    if ground == "field":
        rnd = random.Random(2)
        A.add("".join(f'<path d="M{(xx:=rnd.uniform(-20, W+20)):.0f} {(yy:=rnd.uniform(hz+30, 700)):.0f} q2 -20 {rnd.uniform(-6, 6):.0f} -{20+(yy-hz)*.3:.0f}" stroke="{mix("#5A3A10", "#F2D07A", rnd.random())}" stroke-width="{1+(yy-hz)/150:.1f}" fill="none"/>' for _ in range(380)))
    if "palms" in feats:
        for px, s in ((80, 1.1), (1120, .95)):
            A.add(f'<path d="M{px} 640 Q{px+10} 500 {px+20} {640-230*s}" stroke="{amb}" stroke-width="{12*s}" fill="none"/>' + "".join(
                f'<path d="M{px+20} {640-230*s} q{math.cos(math.radians(a))*120*s:.0f} {math.sin(math.radians(a))*60*s:.0f} {math.cos(math.radians(a))*170*s:.0f} {math.sin(math.radians(a))*60*s + 70*s:.0f}" stroke="{amb}" stroke-width="{14*s}" fill="none" stroke-linecap="round"/>' for a in (-170, -130, -90, -50, -10, 20)))
    if "reeds" in feats:
        A.add(RA.reeds(60, 650, 1.0, amb, 12, 3))
    if "rocks" in feats:
        A.add(f'<path d="{smooth([(600, 700), (660, 600), (820, 590), (890, 700)], True, .7)}" fill="{amb}"/>')
    return lit, amb


def a_prop(A, p, lit, amb):
    k = p["k"]
    if k == "boat":
        return RA.boat(A, p["x"], p["y"], p.get("s", 1), p.get("tilt", 0), dark=amb, lit=lit, sail=p.get("sail", "up"), sailcol="#8C7A5E")
    if k == "net":
        x, y, w, h = p["x"], p["y"], p.get("w", 220), p.get("h", 160)
        return "".join(f'<path d="M{x+i*w/9:.0f} {y} Q{x+i*w/9+15:.0f} {y+h*.6:.0f} {x+i*w/9.4:.0f} {y+h}" stroke="{lit}" stroke-width="1.2" fill="none" opacity=".7"/>' for i in range(10)) + \
            "".join(f'<path d="M{x} {y+j*h/5:.0f} Q{x+w/2} {y+j*h/5+12:.0f} {x+w} {y+j*h/5:.0f}" stroke="{lit}" stroke-width="1.2" fill="none" opacity=".7"/>' for j in range(6)), ""
    if k == "mat":
        return f'<rect x="{p["x"]-110}" y="{p["y"]-12}" width="220" height="24" rx="6" fill="{mix("#5A4630", amb, .3)}"/><path d="M{p["x"]-110} {p["y"]-12} H{p["x"]+110}" stroke="{lit}" stroke-width="1.5" opacity=".6"/>', ""
    if k == "ropes":
        return f'<path d="M{p["x"]-100} 0 L{p["x"]-100} {p["y"]} M{p["x"]+100} 0 L{p["x"]+100} {p["y"]}" stroke="#C8B48A" stroke-width="3"/>', ""
    if k == "table":
        y = p["y"]
        food = "".join(f'<ellipse cx="{x}" cy="{y-2}" rx="44" ry="10" fill="#C8A878"/><circle cx="{x-10}" cy="{y-8}" r="8" fill="#7A2A20"/><circle cx="{x+12}" cy="{y-7}" r="7" fill="#4A6A2A"/>' for x in (220, 420, 640, 860, 1020))
        return "", f'<rect x="60" y="{y}" width="1080" height="40" fill="#3A2010"/><path d="M70 {y+2} H1130" stroke="{lit}" stroke-width="2" opacity=".6"/><rect x="60" y="{y+36}" width="1080" height="200" fill="#120806"/>' + food
    if k == "booth":
        x, y = p["x"], p["y"]
        return "", f'<rect x="{x-130}" y="{y-90}" width="260" height="90" fill="{mix("#3A2416", amb, .4)}"/><path d="M{x-130} {y-90} H{x+130}" stroke="{lit}" stroke-width="2" opacity=".7"/>' + "".join(f'<circle cx="{x-80+i*28}" cy="{y-98}" r="8" fill="#E2BC62"/>' for i in range(6))
    if k == "hole":
        return f'<rect x="{p["x"]-130}" y="0" width="260" height="70" fill="{A.lin([(0, "#AFD8E6"), (1, "#FFF0C8")])}"/>' + rays(A, p["x"], 0, "#FFF0C8", .45, 10, (70, 110), 1000, 3), ""
    if k == "loaves":
        x, y = p["x"], p["y"]
        return "", "".join(f'<ellipse cx="{x-150+i*60}" cy="{y}" rx="26" ry="14" fill="#C8904A"/>' for i in range(6)) + f'<rect x="{x-200}" y="{y+12}" width="400" height="24" fill="#8A6A2A"/><path d="M{x-200} {y+12} H{x+200}" stroke="{lit}" stroke-width="2" opacity=".7"/>'
    if k == "stretcher":
        x, y, w = p["x"], p["y"], p.get("w", 260)
        return "", f'<rect x="{x-w/2}" y="{y-10}" width="{w}" height="20" rx="4" fill="{mix("#5A4630", amb, .3)}"/><path d="M{x-w/2-30} {y} H{x+w/2+30}" stroke="{amb}" stroke-width="7" stroke-linecap="round"/><path d="M{x-w/2} {y-10} H{x+w/2}" stroke="{lit}" stroke-width="1.5" opacity=".6"/>'
    if k == "roofhole":
        x, y = p["x"], p["y"]
        return f'<path d="{smooth([(x - 150, y), (x - 120, y - 24), (x + 110, y - 30), (x + 150, y - 4), (x + 130, y + 26), (x - 130, y + 30)], True, .5)}" fill="#000"/>' + glow(A, x, y, 120, "#FFC66A", .35), ""
    if k == "skins":
        x, y = p["x"], p["y"]
        def skin(cx, cy, col, cracked):
            body = smooth([(cx - 90, cy - 60), (cx - 40, cy - 120), (cx + 50, cy - 110), (cx + 100, cy - 30), (cx + 70, cy + 70), (cx - 60, cy + 80), (cx - 110, cy + 10)], True, .9)
            out = A.shaded(body, [(mix(col, lit, .3), 0, 0), (mix(col, amb, .5), 10, 10), (mix(col, amb, .8), 40, 30)])
            out += f'<path d="M{cx-30} {cy-118} Q{cx-20} {cy-170} {cx+10} {cy-175} Q{cx+30} {cy-150} {cx+20} {cy-112} Z" fill="{mix(col, amb, .5)}"/><path d="M{cx-28} {cy-150} H{cx+22}" stroke="{lit}" stroke-width="4" opacity=".7"/>'
            if cracked:
                out += f'<path d="M{cx+40} {cy-80} l-20 30 l24 20 l-18 34" stroke="{lit}" stroke-width="2.5" fill="none"/><path d="M{cx+60} {cy-20} q40 20 60 70" stroke="#5A1426" stroke-width="8" fill="none" stroke-linecap="round"/>'
            return out
        return "", skin(x - 220, y, "#5A3A22", True) + skin(x + 200, y, "#9A6A3A", False) + f'<path d="M{x+330} {y-330} q-30 60 -110 140" stroke="#5A1426" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M{x+300} {y-380} h90 v40 q0 30 -45 40 q-45 -10 -45 -40 Z" fill="{amb}"/>'
    if k == "skins_old":
        x, y = p["x"], p["y"]
        old = f'<path d="{smooth([(x - 220, y - 160), (x - 120, y - 200), (x - 60, y - 60), (x - 140, y + 40), (x - 260, y - 20)], True, .8)}" fill="{mix("#4A3020", amb, .3)}"/>'
        new = f'<path d="{smooth([(x + 60, y - 170), (x + 180, y - 210), (x + 260, y - 60), (x + 180, y + 40), (x + 40, y - 20)], True, .8)}" fill="{mix("#8A5A30", lit, .15)}"/>'
        return "", old + f'<path d="M{x-160} {y-140} l20 40 l-24 30 l26 40" stroke="{lit}" stroke-width="2" fill="none" opacity=".8"/>' + new + f'<path d="M{x+60} {y-260} q30 40 60 70" stroke="#6A1A30" stroke-width="12" fill="none" stroke-linecap="round"/>'
    if k == "shadow":
        x, y = p["x"], p["y"]
        return "", f'<path d="M{x} {y} C{x+40} {y-120} {x+140} {y-160} {x+200} {y-260} C{x+120} {y-220} {x+60} {y-140} {x+20} {y-40} Z" fill="#000" opacity=".6" filter="{wobble(A, 14, .03, 5)}"/>'
    if k == "angel":
        x, y = p["x"], p["y"]
        return glow(A, x, y - 160, 200, "#FFF6D0", .9) + f'<path d="M{x-46} {y} Q{x} {y-280} {x+46} {y} Z" fill="#FFF8E0" opacity=".7"/><circle cx="{x}" cy="{y-268}" r="26" fill="#FFF8E0" opacity=".8"/>', ""
    if k == "jar":
        return "", f'<path d="{smooth([(p["x"] - 22, p["y"]), (p["x"] - 30, p["y"] - 50), (p["x"] - 14, p["y"] - 80), (p["x"] + 14, p["y"] - 80), (p["x"] + 30, p["y"] - 50), (p["x"] + 22, p["y"])], True, .7)}" fill="{amb}"/>'
    return "", ""


def render_adults(spec, orth=True):
    import places
    A = Art()
    if "place" in spec["env"]:
        lit, amb, _ = places.a_place(A, spec["env"])
    else:
        lit, amb = a_env(A, spec["env"])
    light = (1, -.35) if spec["env"].get("time") != "dawn" else (-1, -.35)
    if spec["env"].get("kind") == "interior" or spec["env"].get("place") in ("synagogue", "house", "feast"):
        light = (.3, -1)
    if spec["env"].get("dove"):
        A.add('<g transform="translate(600 170) scale(.7)"><path d="M0 0 C-40 -50 -110 -60 -150 -30 C-100 -20 -50 -5 -20 12 Z M0 0 C40 -50 110 -60 150 -30 C100 -20 50 -5 20 12 Z" fill="#FFFFFF"/><ellipse cx="0" cy="18" rx="22" ry="34" fill="#FFFFFF"/><circle cx="0" cy="52" r="14" fill="#FFFFFF"/></g>')
    HF = 270
    ride = lambda r: r[0] - HF * r[1] * 1.15
    backs, fronts = [], []
    for p in spec.get("props", []):
        if p.get("ride"):
            p = dict(p, y=ride(p["ride"]))
        b, f = a_prop(A, p, lit, amb)
        (backs if p.get("layer", "back") == "back" else fronts).append(b)
        fronts.append(f)
    A.add("".join(backs))
    anchors = {}
    figs = [dict(f, y=ride(f["ride"]) - 4) if f.get("ride") else f for f in spec.get("figs", [])]
    for f in sorted(figs, key=lambda f: (f.get("ride") is None, f["y"])):
        h = HF * f.get("s", 1.0)
        rot = 90 if f.get("lie") else 0
        facing = -1 if f.get("lie") else f.get("f", 1)
        y = f["y"] - (h * .07 if f.get("lie") else 0)
        x = f["x"] - (h * .5 if f.get("lie") else 0)
        if not f.get("lie") and spec["env"].get("kind") not in ("interior",):
            dx = -light[0] * h * .5
            A.add(f'<path d="M{x-h*.12:.0f} {y:.0f} L{x+h*.12:.0f} {y:.0f} L{x+h*.12+dx:.0f} {y+h*.05:.0f} L{x-h*.12+dx:.0f} {y+h*.07:.0f} Z" fill="{amb}" opacity=".45" filter="{RA.wobble(A, 3, .05, 2)}"/>')
        elif not f.get("lie"):
            A.add(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{h*.16:.0f}" ry="{h*.025:.0f}" fill="#000" opacity=".5"/>')
        if f["id"] == "jesus" and not rot:
            hx, hy = head_of_sil(x, y, h, 0, facing, f.get("kneel", False), f.get("sit", False))
            A.add(glow(A, hx, hy + h * .25, h * .55, "#FFE6B0", .28))
        A.add(sil(A, f["id"], x, y, h, f.get("pose", "stand"), facing, light, lit if f["id"] != "jesus" else mix(lit, "#FFE6A8", .5),
                  amb, rot=rot, nimbus=(orth and f["id"] == "jesus"), kneel=f.get("kneel", False), sit=f.get("sit", False),
                  mouth_open=f.get("e") in ("shout", "scared"), tint=(.7 if f["id"] == "jesus" else .86)))
        anchors.setdefault(f["id"], head_of_sil(x, y, h, rot, facing, f.get("kneel", False), f.get("sit", False)))
    A.add("".join(fronts))
    if "place" in spec["env"]:
        finish_adults(A, spec["env"], lit, amb)
    RA.finish(A, .14, .45)
    return A, anchors


# ------------------------------------------------------------------ finishing pass: light, grade, foreground framing
def _branch(x, y, s, col, flip=1):
    out = f'<path d="M{x} {y} q{flip*120*s:.0f} {-40*s:.0f} {flip*260*s:.0f} {-10*s:.0f}" stroke="{col}" stroke-width="{10*s:.1f}" fill="none" stroke-linecap="round"/>'
    for i in range(7):
        bx, by = x + flip * (40 + i * 32) * s, y - (18 + (i % 3) * 6) * s
        out += f'<ellipse cx="{bx:.0f}" cy="{by + (20 if i % 2 else -20) * s:.0f}" rx="{26*s:.0f}" ry="{10*s:.0f}" fill="{col}" transform="rotate({(35 if i % 2 else -35) * flip} {bx:.0f} {by:.0f})"/>'
    return out


def finish_kids(A, env):
    place, time = env.get("place"), env.get("time", "day")
    outdoor = place not in ("synagogue", "house", "feast")
    if outdoor and time != "night":
        sx = 1030 if time != "dawn" else 220
        A.add(f'<rect width="{W}" height="{H}" fill="{A.rad([(0, "#FFF4C8", .35), (1, "#FFF4C8", 0)], sx / W, .1, .8)}" style="mix-blend-mode:screen"/>')
    A.add(f'<rect y="{H*.72:.0f}" width="{W}" height="{H*.28:.0f}" fill="{A.lin([(0, "#2B1E2F", 0), (1, "#2B1E2F", .18)])}"/>')
    if outdoor and place in ("jordan", "road", "field", "wilderness", "shore"):
        tuft = "#5E9A4E" if place != "wilderness" else "#9A8A50"
        for x0, flip in ((-10, 1), (1210, -1)):
            for i in range(6):
                bx = x0 + flip * i * 16
                A.add(f'<path d="M{bx} 810 q{flip*6} -40 {flip*18} -{60+i*8}" stroke="{KINK}" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M{bx} 810 q{flip*6} -40 {flip*18} -{60+i*8}" stroke="{tuft}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if time == "night":
        A.add(f'<rect width="{W}" height="{H}" fill="#1E2250" opacity=".12"/>')


def finish_adults(A, env, lit, amb):
    place, time = env.get("place"), env.get("time", "day")
    outdoor = place not in ("synagogue", "house", "feast")
    grade = {"dawn": "#FFB48A", "day": "#FFE7C0", "dusk": "#FF9A5A", "night": "#3A6A8A"}.get(time, "#FFE7C0")
    A.add(f'<rect width="{W}" height="{H}" fill="{grade}" opacity=".07" style="mix-blend-mode:overlay"/>')
    if outdoor:
        hz = {"wide": 450, "medium": 500, "close": 560}.get(env.get("cam", "medium"), 500)
        A.add(f'<rect y="{hz-50}" width="{W}" height="110" fill="{A.lin([(0, lit, 0), (.5, lit, .14), (1, lit, 0)])}"/>')
        if place in ("jordan", "road", "field"):
            A.add(_branch(-20, 40, 1.3, amb, 1) + _branch(1220, 70, 1.1, amb, -1))
        elif place == "shore":
            A.add(f'<path d="M-20 830 Q60 700 30 600 M10 830 Q80 720 70 640" stroke="{amb}" stroke-width="7" fill="none"/>')
    else:
        A.add(f'<rect width="{W}" height="34" fill="{amb}"/><rect x="0" y="0" width="{W}" height="{H}" fill="{A.rad([(0, "#000", 0), (.7, "#000", 0), (1, "#000", .35)], .5, .45, .75)}"/>')
