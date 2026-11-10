"""Recognisable places of Mark's Galilee and Judea, in both styles.

place: jordan | wilderness | shore | street | synagogue | house | feast | roof | field | road
time:  dawn | day | dusk | night
cam:   wide | medium | close   (sets the horizon: the closer the camera, the lower the horizon)
Each function draws the background and returns the ground line y.
"""
import math
import random

from art_engine import mix, shade, smooth, poly, circ, ell, clouds, glow, rays, stars, ridge, wobble, KINK, W, H
from render_art import kcloud
import render_adults as RA

HORIZON = {"wide": 450, "medium": 500, "close": 560}


# ------------------------------------------------------------------ shared shapes
def stones(x0, y0, x1, y1, seed, col, line, r=(18, 30)):
    """Rounded basalt / limestone block wall."""
    rnd = random.Random(seed)
    out, y = [], y0
    row = 0
    while y < y1:
        h = rnd.uniform(*r)
        x = x0 - (rnd.uniform(0, 30) if row % 2 else 0)
        while x < x1:
            w = rnd.uniform(r[0] * 1.6, r[1] * 2.2)
            c = mix(col, "#000", rnd.uniform(0, .12))
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w-4:.0f}" height="{h-4:.0f}" rx="{h*.3:.0f}" fill="{c}" stroke="{line}" stroke-width="1.5"/>')
            x += w
        y += h
        row += 1
    return "<g>" + "".join(out) + "</g>"


def tree_round(x, y, s, trunk, leaf, leaf2, ink=None, sw=3):
    st = f' stroke="{ink}" stroke-width="{sw}"' if ink else ""
    t = f'<path d="M{x-8*s:.0f} {y:.0f} Q{x-4*s:.0f} {y-80*s:.0f} {x:.0f} {y-140*s:.0f} L{x+10*s:.0f} {y-140*s:.0f} Q{x+8*s:.0f} {y-80*s:.0f} {x+12*s:.0f} {y:.0f} Z" fill="{trunk}"{st}/>'
    blobs = [(x - 50 * s, y - 150 * s, 55 * s), (x + 40 * s, y - 165 * s, 60 * s), (x - 5 * s, y - 200 * s, 62 * s), (x + 75 * s, y - 130 * s, 42 * s), (x - 85 * s, y - 120 * s, 40 * s)]
    f = "".join(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{br:.0f}" fill="{leaf}"{st}/>' for bx, by, br in blobs)
    f += "".join(f'<circle cx="{bx-br*.25:.0f}" cy="{by-br*.25:.0f}" r="{br*.55:.0f}" fill="{leaf2}"/>' for bx, by, br in blobs)
    return t + f


# ================================================================== KIDS
K_SKY = {"dawn": ["#FFB59A", "#FFD9A8", "#FFF0C8"], "day": ["#6FC0EE", "#A9DDF7", "#E3F4FF"],
         "dusk": ["#FF8D7A", "#FFB06B", "#FFD58C"], "night": ["#1E2250", "#2F3C7A", "#4A5A9A"]}


def k_sky(A, time, hz, sun=True, sun_x=None):
    s = K_SKY[time]
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, s[0]), (.6, s[1]), (1, s[2])])}"/>')
    if time == "night":
        A.add(stars(A, 80, 5, hz - 40, "#FFF6C8", 2.4, 8) + f'<circle cx="1040" cy="120" r="44" fill="#FFF3C9" stroke="#E9C877" stroke-width="4"/>')
        return
    if sun:
        sx = sun_x or (1000 if time == "dusk" else 220 if time == "dawn" else 1030)
        sy = hz - 60 if time in ("dusk", "dawn") else 110
        A.add(glow(A, sx, sy, 200, "#FFF4C0", .8) + f'<circle cx="{sx}" cy="{sy}" r="54" fill="#FFF0B0" stroke="#F3A25A" stroke-width="5"/>')
    A.add(kcloud(A, 300, 120, 90) + kcloud(A, 720, 80, 64))


def k_hills(A, hz, c1, c2, seed=4):
    A.add(A.shaded(ridge(hz - 6, 80, seed, 7), [(shade(c1, .9), 0, 0), (c1, -20, 0)], KINK, 4))
    A.add(A.shaded(ridge(hz + 14, 40, seed + 5, 9), [(shade(c2, .9), 0, 0), (c2, -20, 0)], KINK, 4))


def k_ground(A, hz, col, col2=None):
    A.add(A.shaded(f"M-20 {hz+10} Q600 {hz-10} 1220 {hz+10} V820 H-20 Z", [(shade(col, .88), 0, 0), (col2 or col, 0, -12)], KINK, 4))


def k_house(A, x, y, w, h, wall="#6E6872", lit="#8E8896", stairs=True, door=True, win=True):
    out = A.shaded(f"M{x} {y} V{y-h} H{x+w} V{y} Z", [(wall, 0, 0), (lit, -w * .6, 0)], KINK, 4)
    out += stones(x + 4, y - h + 4, x + w - 4, y - 4, int(x + w), shade(lit, .95), shade(wall, .7), (16, 24))
    out += f'<rect x="{x-6}" y="{y-h-12}" width="{w+12}" height="14" fill="#8A6A44" stroke="{KINK}" stroke-width="3"/>'
    if door:
        out += f'<path d="M{x+w*.18} {y} V{y-h*.55} Q{x+w*.28} {y-h*.66} {x+w*.38} {y-h*.55} V{y} Z" fill="#4A3426" stroke="{KINK}" stroke-width="3"/>'
    if win:
        out += f'<rect x="{x+w*.6}" y="{y-h*.7}" width="{w*.14}" height="{h*.16}" rx="6" fill="#FFD36A" stroke="{KINK}" stroke-width="3"/>'
    if stairs:
        for i in range(6):
            out += f'<rect x="{x+w-6+i*0}" y="{y-12-i*h/7:.0f}" width="{30+i*0}" height="10" fill="{lit}" stroke="{KINK}" stroke-width="2" transform="translate({i*10} 0)"/>'
    return out


def k_place(A, env):
    place, time, cam = env.get("place", "road"), env.get("time", "day"), env.get("cam", "medium")
    hz = HORIZON[cam]
    night = time == "night"
    nm = (lambda c: mix(c, "#24306A", .55)) if night else (lambda c: c)
    if place in ("synagogue", "house", "feast"):
        return k_interior(A, place, time, cam)
    k_sky(A, time, hz)
    if place == "jordan":
        k_hills(A, hz, nm("#D9A86A"), nm("#C49058"))
        k_ground(A, hz, nm("#9CCB7A"), nm("#B4DB8E"))
        A.add(A.shaded(smooth([(-20, hz + 60), (500, hz + 40), (1220, hz + 70), (1220, hz + 170), (600, hz + 150), (-20, hz + 180)], True, .7), [(nm("#2E86C4"), 0, 0), (nm("#5BB4E0"), 0, -10)], KINK, 4))
        for i in range(8):
            A.add(f'<path d="M{80+i*140} {hz+100+(i%3)*20} q22 -8 44 0" stroke="#D6F2FF" stroke-width="3" fill="none" stroke-linecap="round" opacity=".8"/>')
        A.add(tree_round(90, hz + 60, .9, "#7A5232", nm("#6FA35E"), nm("#8FC27A"), KINK) + tree_round(1120, hz + 50, .8, "#7A5232", nm("#6FA35E"), nm("#8FC27A"), KINK))
        A.add(reeds_k(40, hz + 200, 1.1, nm("#4C7A4E")) + reeds_k(1160, hz + 190, 1.0, nm("#4C7A4E")))
    elif place == "wilderness":
        A.add(A.shaded(smooth([(-20, 820), (-20, hz - 160), (120, hz - 200), (260, hz - 120), (330, hz + 40), (360, 820)], True, .5), [(nm("#B9774A"), 0, 0), (nm("#D99A62"), 26, 0)], KINK, 4))
        A.add(A.shaded(smooth([(1220, 820), (1220, hz - 220), (1080, hz - 240), (960, hz - 140), (900, hz + 30), (880, 820)], True, .5), [(nm("#B9774A"), 0, 0), (nm("#D99A62"), -26, 0)], KINK, 4))
        k_hills(A, hz, nm("#D9A86A"), nm("#C99860"), 7)
        k_ground(A, hz, nm("#D8B07A"), nm("#E9C68E"))
        for x in (420, 520, 760, 840):
            A.add(f'<ellipse cx="{x}" cy="{hz+60+(x%3)*14}" rx="26" ry="10" fill="{nm("#A27A50")}" stroke="{KINK}" stroke-width="3"/>')
    elif place == "shore":
        k_hills(A, hz - 10, nm("#A98BB0"), nm("#8FA88A"))
        A.add(f'<rect y="{hz}" width="{W}" height="{H}" fill="{A.lin([(0, nm("#56BCE0")), (1, nm("#2C7CB9"))])}"/>')
        for i in range(12):
            A.add(f'<path d="M{random.Random(i).uniform(0, 1150):.0f} {hz+20+i*14} q22 -8 44 0" stroke="#C8EEFA" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>')
        A.add(A.shaded(smooth([(-20, hz + 150), (400, hz + 120), (800, hz + 160), (1220, hz + 140), (1220, 820), (-20, 820)], True, .7), [(nm("#DDB277"), 0, 0), (nm("#F0CC90"), 0, -10)], KINK, 4))
        if env.get("poles", True):
            for x in (980, 1110):
                A.add(f'<path d="M{x} {hz+150} V{hz-30}" stroke="{KINK}" stroke-width="9"/><path d="M{x} {hz+150} V{hz-30}" stroke="#8A5A33" stroke-width="5"/>')
            A.add(f'<path d="M980 {hz-20} Q1045 {hz+40} 1110 {hz-20}" stroke="#F4E3C0" stroke-width="4" fill="none"/>' + "".join(f'<path d="M{990+i*12} {hz-14+abs(i-5)*3} v{60-abs(i-5)*8}" stroke="#F4E3C0" stroke-width="2"/>' for i in range(10)))
    elif place in ("street", "roof"):
        A.add(k_house(A, -10, hz + 40, 260, 230) + k_house(A, 270, hz + 30, 220, 190, stairs=False) + k_house(A, 740, hz + 40, 240, 220) + k_house(A, 1000, hz + 30, 230, 200, stairs=False))
        k_ground(A, hz + 30, nm("#C9A77A"), nm("#DDBC8E"))
        rnd = random.Random(2)
        for i in range(30):
            A.add(f'<ellipse cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(hz+60, 800):.0f}" rx="{rnd.uniform(14, 26):.0f}" ry="7" fill="{nm("#B8946A")}" opacity=".7"/>')
        if place == "roof":
            A.add(A.shaded(f"M-20 {hz+110} H1220 V820 H-20 Z", [(nm("#B88A5A"), 0, 0), (nm("#D2A472"), 0, -10)], KINK, 5))
            A.add(f'<path d="M-20 {hz+150} H1220 M-20 {hz+210} H1220 M-20 {hz+270} H1220" stroke="#9A7046" stroke-width="3" opacity=".5"/>')
    elif place in ("field", "road"):
        k_hills(A, hz, nm("#9BC48A"), nm("#7FA872"))
        if env.get("village", True):
            A.add(k_house(A, 860, hz + 6, 90, 60, stairs=False, door=False) + k_house(A, 950, hz + 10, 110, 70, stairs=False, door=False))
        if place == "field":
            k_ground(A, hz, nm("#E9B84A"), nm("#F2C860"))
            from render_art import wheat
            A.add(wheat(A, hz + 20, 700, "#FFE08A", "#C68A22", 2, 260, sc=.9))
            A.add(A.shaded(f"M-20 {hz+40} H1220 V{hz+58} H-20 Z", [("#A69A88", 0, 0), ("#C2B6A2", 0, -4)], KINK, 3))
            for x in range(40, 1200, 160):
                A.add(f'<circle cx="{x}" cy="{hz+90+(x%3)*30}" r="7" fill="#E04A3A"/>')
        else:
            k_ground(A, hz, nm("#D8B98A"), nm("#E6CAA0"))
            A.add(f'<path d="M560 {hz+10} L640 {hz+10} L1000 820 L200 820 Z" fill="{nm("#E9D2A6")}" stroke="{KINK}" stroke-width="3"/>')
            A.add(tree_round(140, hz + 120, 1.0, "#6E5236", nm("#8FA27A"), nm("#AABE92"), KINK) + tree_round(1080, hz + 110, 1.0, "#6E5236", nm("#8FA27A"), nm("#AABE92"), KINK))
    if env.get("light"):
        A.add(rays(A, 600, -40, "#FFF6C8", .5, 12, (60, 120), 1100, 5) + glow(A, 600, 0, 420, "#FFF7D0", 1))
    return hz


def reeds_k(x, y, s, col):
    rnd = random.Random(int(x))
    out = ""
    for i in range(9):
        dx, h, b = rnd.uniform(-40, 40) * s, rnd.uniform(90, 180) * s, rnd.uniform(-25, 25) * s
        out += f'<path d="M{x+dx:.0f} {y:.0f} Q{x+dx+b*.3:.0f} {y-h*.6:.0f} {x+dx+b:.0f} {y-h:.0f}" stroke="{KINK}" stroke-width="{7*s:.1f}" fill="none" stroke-linecap="round"/><path d="M{x+dx:.0f} {y:.0f} Q{x+dx+b*.3:.0f} {y-h*.6:.0f} {x+dx+b:.0f} {y-h:.0f}" stroke="{col}" stroke-width="{4*s:.1f}" fill="none" stroke-linecap="round"/>'
        if i % 2 == 0:
            out += f'<ellipse cx="{x+dx+b:.0f}" cy="{y-h:.0f}" rx="{6*s:.0f}" ry="{16*s:.0f}" fill="#8A5A33" stroke="{KINK}" stroke-width="2.5"/>'
    return out


def k_interior(A, place, time, cam):
    hz = 690 if cam != "close" else 740
    if place == "synagogue":
        wall, floor = "#EFE3C8", "#D8C49E"
        A.add(f'<rect width="{W}" height="{H}" fill="{wall}"/>' + stones(0, 70, W, hz, 11, "#F2E8D2", "#D2C2A0", (34, 46)))
        A.add(f'<rect x="520" y="110" width="160" height="170" rx="80" fill="#BFE6FA" stroke="{KINK}" stroke-width="5"/><path d="M520 300 L420 {hz} H880 L680 300 Z" fill="#FFF4C0" opacity=".35"/>')
        for x in (110, 330, 870, 1090):
            A.add(A.shaded(f"M{x-34} 80 H{x+34} V{hz} H{x-34} Z", [("#E2D4B4", 0, 0), ("#FBF3E0", -16, 0)], KINK, 4) + f'<rect x="{x-46}" y="70" width="92" height="24" fill="#E2D4B4" stroke="{KINK}" stroke-width="4"/>')
        for i, y in enumerate((hz - 40, hz - 80)):
            A.add(f'<rect x="-10" y="{y}" width="{W+20}" height="22" fill="#CBB38A" stroke="{KINK}" stroke-width="3" opacity="{.9 - i*.2}"/>')
        A.add(A.shaded(f"M0 {hz} H{W} V{H} H0 Z", [(shade(floor, .9), 0, 0), (floor, 0, 10)], KINK, 4))
    elif place == "house":
        wall = "#7C7480" if time != "night" else "#4A4460"
        A.add(f'<rect width="{W}" height="{H}" fill="{wall}"/>' + stones(0, 60, W, hz, 21, mix(wall, "#fff", .18), shade(wall, .6), (24, 36)))
        for x in range(0, W, 200):
            A.add(f'<rect x="{x}" y="0" width="40" height="60" fill="#6E4A2A" stroke="{KINK}" stroke-width="3"/>')
        A.add(f'<rect y="40" width="{W}" height="24" fill="#8A5A33" stroke="{KINK}" stroke-width="3"/>')
        A.add(f'<path d="M140 260 h90 v70 h-90 Z" fill="{shade(wall, .5)}" stroke="{KINK}" stroke-width="3"/>' + glow(A, 185, 300, 90, "#FFD36A", .7) + f'<ellipse cx="185" cy="318" rx="20" ry="9" fill="#C9873E" stroke="{KINK}" stroke-width="2"/><path d="M185 306 q7 -14 0 -22 q-7 9 0 22" fill="#FFB020"/>')
        for x, s in ((1060, 1.0), (1130, .8)):
            A.add(A.shaded(smooth([(x - 30 * s, hz), (x - 40 * s, hz - 70 * s), (x - 16 * s, hz - 110 * s), (x + 16 * s, hz - 110 * s), (x + 40 * s, hz - 70 * s), (x + 30 * s, hz)], True, .7), [("#B8733A", 0, 0), ("#D99A5A", -8, -8)], KINK, 4))
        A.add(A.shaded(f"M0 {hz} H{W} V{H} H0 Z", [("#8A6A4A", 0, 0), ("#A07E5A", 0, 10)], KINK, 4))
        A.add(f'<rect x="80" y="{hz+30}" width="300" height="40" rx="6" fill="#C9A86A" stroke="{KINK}" stroke-width="3"/>')
    elif place == "feast":
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#232055"), (1, "#4A3A6A")])}"/>' + stars(A, 40, 3, 200, "#FFF6C8", 2))
        A.add(A.shaded(f"M200 {hz} V260 Q600 40 1000 260 V{hz} H900 V300 Q600 140 300 300 V{hz} Z", [("#9A6A4A", 0, 0), ("#B98A62", -16, 0)], KINK, 5))
        A.add(f'<path d="M0 120 Q300 200 600 130 T1200 140" stroke="#5A4030" stroke-width="3" fill="none"/>')
        for i, x in enumerate(range(60, 1200, 110)):
            y = 150 + 30 * math.sin(i)
            A.add(glow(A, x, y, 60, "#FFD36A", .7) + f'<circle cx="{x}" cy="{y:.0f}" r="9" fill="#FFE07A" stroke="{KINK}" stroke-width="2"/>')
        A.add(A.shaded(f"M0 {hz} H{W} V{H} H0 Z", [("#6A4A3A", 0, 0), ("#8A6A50", 0, 10)], KINK, 4))
    return hz


# ================================================================== ADULTS
A_SKY = {"dawn": [(0, "#2E3E52"), (.45, "#B07A6A"), (.62, "#F0B888"), (.72, "#FFE0B0")],
         "day": [(0, "#3E6E86"), (.5, "#9CBFC6"), (.72, "#EADCBC")],
         "dusk": [(0, "#2C3E4C"), (.35, "#8A5A4A"), (.58, "#E09A58"), (.72, "#FFD08C")],
         "night": [(0, "#03080C"), (.55, "#0F2830"), (.72, "#244550")]}
A_LIGHT = {"dawn": ("#FFE2B4", "#120C0A"), "day": ("#FFF4DA", "#1A1612"), "dusk": ("#FFDCA0", "#140B07"), "night": ("#DDE6E6", "#02070A")}


def a_sky(A, time, hz):
    lit, amb = A_LIGHT[time]
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin(A_SKY[time])}"/>')
    if time == "night":
        A.add(stars(A, 220, 12, hz, "#E8E4DA", 1.5) + glow(A, 1040, 120, 240, "#E8E4DA", .5) + '<circle cx="1040" cy="120" r="34" fill="#F2EEE4"/>')
    else:
        A.add(clouds(A, 0, hz - 40, mix(A_SKY[time][-1][1], "#fff", .3), hz, (.0018, .010), 1.6, .65, .65))
        sx = 980 if time == "dusk" else 220 if time == "dawn" else 900
        sy = hz - 30 if time in ("dusk", "dawn") else 130
        A.add(glow(A, sx, sy, 420, mix(lit, "#fff", .3), .85) + f'<circle cx="{sx}" cy="{sy}" r="32" fill="#FFF8E4"/>')
    return lit, amb


def a_houses(A, x0, x1, base, h0, h1, col, lit, seed, lamps=False):
    rnd = random.Random(seed)
    x = x0
    out = ""
    while x < x1:
        w, h = rnd.uniform(140, 240), rnd.uniform(h0, h1)
        out += f'<rect x="{x:.0f}" y="{base-h:.0f}" width="{w:.0f}" height="{h+300:.0f}" fill="{col}"/><rect x="{x-6:.0f}" y="{base-h-10:.0f}" width="{w+12:.0f}" height="12" fill="{shade(col, .7)}"/>'
        out += f'<path d="M{x+w-2:.0f} {base-h:.0f} V{base+300:.0f}" stroke="{lit}" stroke-width="2" opacity=".5"/>'
        if rnd.random() < .6:
            dx = x + w * .2
            out += f'<path d="M{dx:.0f} {base:.0f} V{base-h*.5:.0f} Q{dx+w*.1:.0f} {base-h*.62:.0f} {dx+w*.2:.0f} {base-h*.5:.0f} V{base:.0f} Z" fill="{shade(col, .5)}"/>'
        if lamps and rnd.random() < .7:
            wx = x + w * .62
            out += glow(A, wx + 8, base - h * .6, 40, "#FFB54A", .6) + f'<rect x="{wx:.0f}" y="{base-h*.68:.0f}" width="16" height="22" rx="7" fill="#FFC873"/>'
        if rnd.random() < .5:
            for i in range(6):
                out += f'<rect x="{x+w-4+i*10:.0f}" y="{base-12-i*h/7:.0f}" width="26" height="8" fill="{col}"/>'
        x += w + rnd.uniform(4, 20)
    return out


def a_place(A, env):
    place, time, cam = env.get("place", "road"), env.get("time", "day"), env.get("cam", "medium")
    hz = HORIZON[cam]
    if place in ("synagogue", "house", "feast"):
        return a_interior(A, place, time, cam)
    lit, amb = a_sky(A, time, hz)
    far = A_SKY[time][-1][1]
    if place == "wilderness":
        A.add(f'<path d="{smooth([(-20, 820), (-20, hz-180), (140, hz-220), (270, hz-120), (330, hz+40), (360, 820)], True, .5)}" fill="{mix(amb, far, .25)}"/>')
        A.add(f'<path d="{smooth([(1220, 820), (1220, hz-240), (1080, hz-260), (960, hz-150), (900, hz+30), (880, 820)], True, .5)}" fill="{mix(amb, far, .25)}"/>')
        A.add(f'<path d="M330 {hz+40} L360 820" stroke="{lit}" stroke-width="2" opacity=".4"/>')
    RA.hills(A, hz, mix(far, "#000", .12), mix(amb, far, .3), 2, hz + len(place), (70, 36))
    ground = {"jordan": "#4E5A3A", "wilderness": "#7A5A3E", "shore": "#6A5440", "street": "#6A5844", "roof": "#6A5844", "field": "#B8862E", "road": "#7A6448"}[place]
    if time == "night":
        ground = mix(ground, amb, .6)
    if place == "shore":
        RA.water(A, hz + 4, mix(far, "#6A8A8A", .4), mix(amb, "#000", .3), mix(lit, "#fff", .2), 900 if time != "dawn" else 220, hz)
        A.add(f'<path d="{smooth([(-30, hz+150), (400, hz+120), (800, hz+160), (1230, hz+140), (1230, 830), (-30, 830)], True, .7)}" fill="{A.lin([(0, mix(ground, far, .3)), (1, amb)])}"/>')
        if env.get("poles", True):
            A.add(f'<path d="M980 {hz+150} V{hz-30} M1110 {hz+150} V{hz-30}" stroke="{amb}" stroke-width="7"/><path d="M980 {hz-20} Q1045 {hz+40} 1110 {hz-20}" stroke="{lit}" stroke-width="2" fill="none" opacity=".7"/>'
                  + "".join(f'<path d="M{990+i*12} {hz-14+abs(i-5)*3} v{60-abs(i-5)*8}" stroke="{lit}" stroke-width="1.2" opacity=".55"/>' for i in range(10)))
        return lit, amb, hz
    A.add(f'<path d="M-20 {hz+10} Q600 {hz-10} 1220 {hz+10} V820 H-20 Z" fill="{A.lin([(0, mix(ground, far, .4)), (1, mix(ground, amb, .75))])}"/>')
    if place == "jordan":
        A.add(f'<path d="{smooth([(-20, hz+60), (500, hz+40), (1220, hz+70), (1220, hz+170), (600, hz+150), (-20, hz+180)], True, .7)}" fill="{A.lin([(0, mix(far, "#9AB8B4", .5)), (1, mix(amb, "#2A4A50", .4))])}"/>')
        A.add(f'<path d="M-20 {hz+60} Q500 {hz+40} 1220 {hz+70}" stroke="{lit}" stroke-width="2" fill="none" opacity=".7"/>')
        for x, s in ((90, .9), (1120, .8)):
            A.add(tree_round(x, hz + 60, s, amb, mix(amb, far, .15), mix(amb, far, .25)))
        A.add(RA.reeds(50, hz + 210, 1.1, amb, 14, 3) + RA.reeds(1160, hz + 200, 1.0, amb, 12, 5))
    elif place in ("street", "roof"):
        A.add(a_houses(A, -20, 1220, hz + 40, 150, 240, mix(amb, far, .3), lit, 7, lamps=time in ("dusk", "night")))
        A.add(f'<rect y="{hz+40}" width="{W}" height="400" fill="{A.lin([(0, mix(ground, far, .25)), (1, amb)])}"/>')
        if place == "roof":
            A.add(f'<rect x="-20" y="{hz+110}" width="1240" height="300" fill="{mix("#5A4030", amb, .45)}"/><path d="M-20 {hz+110} H1220" stroke="{lit}" stroke-width="2" opacity=".7"/>')
    elif place == "field":
        rnd = random.Random(2)
        A.add(f'<rect x="-20" y="{hz+30}" width="1240" height="16" fill="{mix("#8A7A60", amb, .3)}"/>')
        A.add("".join(f'<path d="M{(xx:=rnd.uniform(-20, W+20)):.0f} {(yy:=rnd.uniform(hz+40, 760)):.0f} q2 -20 {rnd.uniform(-6, 6):.0f} -{20+(yy-hz)*.35:.0f}" stroke="{mix("#5A3A10", "#F2D07A", rnd.random())}" stroke-width="{1+(yy-hz)/140:.1f}" fill="none"/>' for _ in range(420)))
    elif place == "road":
        A.add(f'<path d="M560 {hz+10} L640 {hz+10} L1000 820 L200 820 Z" fill="{mix("#B8A07A", far, .2)}" opacity=".5"/>')
        for x, s in ((140, 1.0), (1080, 1.0)):
            A.add(tree_round(x, hz + 120, s, amb, mix(amb, far, .2), mix(amb, far, .3)))
    if env.get("light"):
        A.add(rays(A, 600, -60, "#FFF6D8", .45, 16, (62, 118), 1100, 6) + glow(A, 600, -20, 520, "#FFF6D8", 1))
    return lit, amb, hz


def a_interior(A, place, time, cam):
    hz = 690 if cam != "close" else 740
    if place == "synagogue":
        lit, amb = "#FFF0CC", "#15130F"
        A.add(f'<rect width="{W}" height="{H}" fill="#2A2620"/>' + stones(0, 70, W, hz, 11, "#36312A", "#221E19", (34, 46)))
        A.add(f'<rect x="520" y="100" width="160" height="190" fill="{A.lin([(0, "#E8E4D0"), (1, "#C8B88A")])}"/><path d="M520 290 L380 {hz} H940 L680 290 Z" fill="{A.lin([(0, "#FFF0C8", .4), (1, "#FFF0C8", 0)])}"/>' + rays(A, 600, 200, "#FFF0C8", .16, 8, (60, 120), 900, 4))
        for x in (110, 330, 870, 1090):
            A.add(f'<rect x="{x-34}" y="80" width="68" height="{hz-80}" fill="#1E1B16"/><rect x="{x+28}" y="80" width="6" height="{hz-80}" fill="{lit}" opacity=".3"/><rect x="{x-46}" y="68" width="92" height="22" fill="#1E1B16"/>')
        A.add(f'<rect x="-10" y="{hz-40}" width="{W+20}" height="20" fill="#14110D"/><rect y="{hz}" width="{W}" height="140" fill="#0E0C09"/><path d="M0 {hz} H{W}" stroke="{lit}" stroke-width="1.5" opacity=".35"/>')
    elif place == "house":
        lit, amb = "#FFD9A0", "#0E0907"
        A.add(f'<rect width="{W}" height="{H}" fill="#1E1712"/>' + stones(0, 60, W, hz, 21, "#2A211A", "#15100C", (24, 36)))
        A.add("".join(f'<rect x="{x}" y="0" width="36" height="60" fill="#120C08"/>' for x in range(0, W, 200)) + f'<rect y="40" width="{W}" height="20" fill="#120C08"/>')
        A.add(glow(A, 185, 300, 160, "#FFC66A", .75) + '<path d="M140 260 h90 v70 h-90 Z" fill="#0A0705"/><ellipse cx="185" cy="318" rx="18" ry="8" fill="#FFE2A0"/>')
        A.add(f'<rect y="{hz}" width="{W}" height="140" fill="#0A0705"/><path d="M0 {hz} H{W}" stroke="{lit}" stroke-width="1.5" opacity=".35"/>')
    else:
        lit, amb = "#FFC66A", "#080406"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#0A0C1A"), (1, "#1E1424")])}"/>' + stars(A, 60, 3, 220, "#E8E4DA", 1.2))
        A.add(f'<path d="M200 {hz} V260 Q600 40 1000 260 V{hz} H900 V300 Q600 140 300 300 V{hz} Z" fill="#120A08"/><path d="M300 300 Q600 140 900 300" stroke="{lit}" stroke-width="2" fill="none" opacity=".4"/>')
        for i, x in enumerate(range(60, 1200, 110)):
            A.add(glow(A, x, 150 + 30 * math.sin(i), 70, "#FFC66A", .7) + f'<circle cx="{x}" cy="{150+30*math.sin(i):.0f}" r="5" fill="#FFF0C0"/>')
        A.add(f'<rect y="{hz}" width="{W}" height="140" fill="#080404"/>')
    return lit, amb, hz
