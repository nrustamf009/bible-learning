#!/usr/bin/env python3
"""Draw all illustrations: pilot panels, episode covers, character sheets.

  python3 tools/render_art.py

Writes SVG files to art/<kids|adults>/... and stores where each speaker's
head is, so the reader's speech-bubble tails point at the right person
(episodes/<ep>/episode.json -> bubbles[].tx / ty are updated in place).
"""
import json
import math
import random
from pathlib import Path

from art_engine import (Art, CHARS, W, H, mix, shade, smooth, poly, circ, ell, clouds, grain, paper, vignette, glow, rays, rain,
                        stars, ridge, waves_path, wobble, kid, novel, head_of_kid, head_of_novel, KINK)

ROOT = Path(__file__).resolve().parent.parent
ANCH = {}  # (style, panel) -> {who: (x%, y%)}


def anchor(style, pid, who, pt):
    ANCH.setdefault((style, pid), {})[who] = (round(pt[0] / W * 100, 1), round(pt[1] / H * 100, 1))


# ================================================================== props
def kboat(A, x, y, s=1.0, tilt=0, sail="up"):
    L = 300 * s
    back, front = [], []
    if sail != "none":
        back.append(f'<path d="M{x-10*s:.0f} {y-30*s:.0f} V{y-310*s:.0f}" stroke="{KINK}" stroke-width="{13*s:.1f}" stroke-linecap="round"/>'
                    f'<path d="M{x-10*s:.0f} {y-30*s:.0f} V{y-310*s:.0f}" stroke="#7A4A26" stroke-width="{8*s:.1f}" stroke-linecap="round"/>')
        if sail == "up":
            sd = smooth([(x - 4 * s, y - 296 * s), (x + 150 * s, y - 250 * s), (x + 132 * s, y - 120 * s), (x - 4 * s, y - 100 * s)], True, .5)
            back.append(A.shaded(sd, [("#E9D3A8", 0, 0), ("#FFF4DA", -14 * s, 0)], KINK, 4 * s))
            back.append(f'<path d="M{x+30*s:.0f} {y-285*s:.0f} L{x+40*s:.0f} {y-108*s:.0f} M{x+80*s:.0f} {y-270*s:.0f} L{x+86*s:.0f} {y-112*s:.0f}" stroke="#D2B989" stroke-width="{3*s:.1f}"/>')
        else:
            back.append(f'<path d="M{x-10*s:.0f} {y-290*s:.0f} l{90*s:.0f} {30*s:.0f}" stroke="{KINK}" stroke-width="{6*s:.1f}"/><ellipse cx="{x+30*s:.0f}" cy="{y-276*s:.0f}" rx="{50*s:.0f}" ry="{14*s:.0f}" fill="#F3E2BE" stroke="{KINK}" stroke-width="{3*s:.1f}" transform="rotate(18 {x+30*s:.0f} {y-276*s:.0f})"/>')
    hull = smooth([(x - L, y - 70 * s), (x - L * .82, y + 18 * s), (x - L * .45, y + 44 * s), (x + L * .45, y + 44 * s), (x + L * .85, y + 18 * s), (x + L * 1.02, y - 84 * s), (x + L * .5, y - 40 * s), (x, y - 34 * s), (x - L * .55, y - 44 * s)], True, .7)
    front.append(A.shaded(hull, [("#8C5530", 0, 0), ("#C07B42", 0, -16 * s)], KINK, 5 * s))
    for k, yy in enumerate((-10, 14)):
        front.append(f'<path d="M{x-L*.86:.0f} {y+yy*s:.0f} Q{x:.0f} {y+(yy+18)*s:.0f} {x+L*.9:.0f} {y+(yy-10)*s:.0f}" stroke="#6E4122" stroke-width="{4*s:.1f}" fill="none" stroke-linecap="round"/>')
    front.append(f'<path d="M{x-L*.9:.0f} {y-58*s:.0f} Q{x:.0f} {y-26*s:.0f} {x+L*.98:.0f} {y-70*s:.0f}" stroke="#E0A060" stroke-width="{4*s:.1f}" fill="none" stroke-linecap="round" opacity=".8"/>')
    front.append(f'<circle cx="{x-L*.72:.0f}" cy="{y-30*s:.0f}" r="{11*s:.0f}" fill="#F4E3C0" stroke="{KINK}" stroke-width="{3*s:.1f}"/><circle cx="{x-L*.72:.0f}" cy="{y-30*s:.0f}" r="{4*s:.0f}" fill="{KINK}"/>')
    b, f = "".join(back), "".join(front)
    if tilt:
        b, f = (f'<g transform="rotate({tilt} {x} {y})">{v}</g>' for v in (b, f))
    return b, f


def nboat(A, x, y, s=1.0, tilt=0, lit="#F2D7A6", amb="#06100F", sail="up", light=(1, -.3)):
    L = 270 * s
    back, front = [], []
    if sail != "none":
        back.append(f'<path d="M{x-14*s:.0f} {y-26*s:.0f} V{y-360*s:.0f}" stroke="{amb}" stroke-width="{9*s:.1f}"/>'
                    f'<path d="M{x-10*s:.0f} {y-26*s:.0f} V{y-360*s:.0f}" stroke="{lit}" stroke-width="{1.6*s:.1f}" stroke-opacity=".5"/>')
        if sail == "up":
            sd = smooth([(x - 8 * s, y - 350 * s), (x + 170 * s, y - 330 * s), (x + 162 * s, y - 120 * s), (x - 8 * s, y - 110 * s)], True, .35)
            back.append(A.shaded(sd, [(mix("#B9A580", lit, .4), 0, 0), (mix("#6E6250", amb, .3), -20 * s * light[0], 0)], amb, 1.5 * s))
    hull = smooth([(x - L, y - 56 * s), (x - L * .84, y + 22 * s), (x - L * .45, y + 40 * s), (x + L * .45, y + 40 * s), (x + L * .86, y + 22 * s), (x + L * 1.04, y - 70 * s), (x, y - 26 * s)], True, .7)
    front.append(A.shaded(hull, [(mix("#3A2416", lit, .35), 0, 0), (mix("#2A1A10", amb, .4), -6 * s * light[0], 6 * s), (mix("#120A06", amb, .6), -30 * s * light[0], 26 * s)], amb, 1.5 * s))
    front.append(f'<path d="M{x-L*.92:.0f} {y-46*s:.0f} Q{x:.0f} {y-18*s:.0f} {x+L*1.0:.0f} {y-60*s:.0f}" stroke="{lit}" stroke-width="{2.4*s:.1f}" fill="none" stroke-opacity=".8"/>')
    for yy in (-4, 18):
        front.append(f'<path d="M{x-L*.86:.0f} {y+yy*s:.0f} Q{x:.0f} {y+(yy+16)*s:.0f} {x+L*.9:.0f} {y+(yy-12)*s:.0f}" stroke="#000" stroke-opacity=".35" stroke-width="{2*s:.1f}" fill="none"/>')
    b, f = "".join(back), "".join(front)
    if tilt:
        b, f = (f'<g transform="rotate({tilt} {x} {y})">{v}</g>' for v in (b, f))
    return b, f


def kcloud(A, cx, cy, s, col="#FFFFFF", shadow=None, light=(-1, -.6)):
    rnd = random.Random(int(cx * 7 + cy))
    circles = [(cx + (i - 2) * s * .36 + rnd.uniform(-.05, .05) * s, cy - (1 - abs(i - 2) * .32) * s * .28, s * (.42 - abs(i - 2) * .06)) for i in range(5)]
    circles += [(cx - s * .55, cy + s * .05, s * .3), (cx + s * .55, cy + s * .05, s * .3), (cx, cy + s * .08, s * .36)]
    sh = shadow or shade(col, .85)
    out = "".join(f'<circle cx="{x:.0f}" cy="{y + s*.08:.0f}" r="{r:.0f}" fill="{sh}"/>' for x, y, r in circles)
    out += "".join(f'<circle cx="{x + light[0]*s*.03:.0f}" cy="{y - s*.02:.0f}" r="{r*.94:.0f}" fill="{col}"/>' for x, y, r in circles)
    return f'<g opacity=".95">{out}</g>'


def reeds(x, y, s, col, n=7, seed=1):
    rnd = random.Random(seed)
    out = ""
    for i in range(n):
        dx = rnd.uniform(-30, 30) * s
        hgt = rnd.uniform(90, 170) * s
        bend = rnd.uniform(-30, 30) * s
        out += f'<path d="M{x+dx:.0f} {y:.0f} Q{x+dx+bend*.3:.0f} {y-hgt*.6:.0f} {x+dx+bend:.0f} {y-hgt:.0f}" stroke="{col}" stroke-width="{rnd.uniform(3,6)*s:.1f}" fill="none" stroke-linecap="round"/>'
        if i % 2 == 0:
            out += f'<ellipse cx="{x+dx+bend:.0f}" cy="{y-hgt:.0f}" rx="{5*s:.0f}" ry="{14*s:.0f}" fill="{col}" transform="rotate({bend/s*.6:.0f} {x+dx+bend:.0f} {y-hgt:.0f})"/>'
    return out


def palm(A, x, y, s, trunk="#7A4A26", leaf="#3E8E5A", ink=KINK, light=(-1, -.6), outline=True):
    out = []
    td = smooth([(x - 10 * s, y), (x - 6 * s, y - 120 * s), (x + 10 * s, y - 230 * s), (x + 24 * s, y - 228 * s), (x + 12 * s, y - 120 * s), (x + 12 * s, y)], True, .7)
    out.append(A.shaded(td, [(shade(trunk, .75), 0, 0), (trunk, light[0] * 6 * s, 0)], ink if outline else None, 3.5 * s))
    cx, cy = x + 17 * s, y - 232 * s
    for a in (-160, -120, -80, -40, -5, 20):
        r = math.radians(a)
        tip = (cx + math.cos(r) * 150 * s, cy + math.sin(r) * 80 * s + 50 * s)
        mid = (cx + math.cos(r) * 80 * s, cy + math.sin(r) * 80 * s - 10 * s)
        ld = smooth([(cx, cy), (mid[0], mid[1] - 14 * s), tip, (mid[0], mid[1] + 14 * s)], True, .8)
        out.append(A.shaded(ld, [(shade(leaf, .72), 0, 0), (leaf, light[0] * 10 * s, light[1] * 10 * s)], ink if outline else None, 3 * s))
    return "".join(out)


def houses(A, x0, y, s, n, seed, wall="#3E3A3A", lit="#6E6560", roof="#5A4632", ink=KINK, window="#FFC15A", outline=True, light=(1, -.5)):
    rnd = random.Random(seed)
    out = []
    x = x0
    for i in range(n):
        w = rnd.uniform(110, 180) * s
        h = rnd.uniform(80, 140) * s
        yb = y + rnd.uniform(-12, 12) * s
        d = poly([(x, yb), (x, yb - h), (x + w, yb - h), (x + w, yb)])
        out.append(A.shaded(d, [(wall, 0, 0), (lit, -light[0] * w * .7, 0)] if light[0] > 0 else [(lit, 0, 0), (wall, w * .3, 0)], ink if outline else None, 3 * s))
        out.append(f'<rect x="{x-4*s:.0f}" y="{yb-h-10*s:.0f}" width="{w+8*s:.0f}" height="{12*s:.0f}" fill="{roof}"' + (f' stroke="{ink}" stroke-width="{2.5*s:.1f}"' if outline else "") + "/>")
        for k in range(rnd.randint(1, 2)):
            wx = x + w * (.25 + .4 * k)
            out.append(f'<rect x="{wx:.0f}" y="{yb-h*.62:.0f}" width="{18*s:.0f}" height="{24*s:.0f}" rx="{8*s:.0f}" fill="{window}"/>')
        if rnd.random() < .5:
            out.append(f'<rect x="{x+w*.6:.0f}" y="{yb-h*.48:.0f}" width="{28*s:.0f}" height="{h*.48:.0f}" fill="{shade(wall,.5)}"/>')
        x += w + rnd.uniform(-10, 20) * s
    return "".join(out)


def dove(x, y, s, col="#FFFFFF", ink="#2B1E2F", outline=True):
    st = f' stroke="{ink}" stroke-width="{3*s:.1f}" stroke-linejoin="round"' if outline else ""
    return (f'<path d="M{x:.0f} {y:.0f} C{x-40*s:.0f} {y-50*s:.0f} {x-110*s:.0f} {y-60*s:.0f} {x-150*s:.0f} {y-30*s:.0f} C{x-100*s:.0f} {y-20*s:.0f} {x-50*s:.0f} {y-5*s:.0f} {x-20*s:.0f} {y+12*s:.0f} Z" fill="{col}"{st}/>'
            f'<path d="M{x:.0f} {y:.0f} C{x+40*s:.0f} {y-50*s:.0f} {x+110*s:.0f} {y-60*s:.0f} {x+150*s:.0f} {y-30*s:.0f} C{x+100*s:.0f} {y-20*s:.0f} {x+50*s:.0f} {y-5*s:.0f} {x+20*s:.0f} {y+12*s:.0f} Z" fill="{col}"{st}/>'
            f'<ellipse cx="{x:.0f}" cy="{y+18*s:.0f}" rx="{22*s:.0f}" ry="{34*s:.0f}" fill="{col}"{st}/>'
            f'<circle cx="{x:.0f}" cy="{y+52*s:.0f}" r="{14*s:.0f}" fill="{col}"{st}/>')


def net(x, y, w, h, col, sw=2):
    out = []
    for i in range(9):
        t = i / 8
        out.append(f'<path d="M{x+w*t:.0f} {y:.0f} Q{x+w*t+w*.05:.0f} {y+h*.6:.0f} {x+w*t*.8+w*.1:.0f} {y+h:.0f}" stroke="{col}" stroke-width="{sw}" fill="none"/>')
    for j in range(6):
        t = j / 5
        out.append(f'<path d="M{x:.0f} {y+h*t:.0f} Q{x+w*.5:.0f} {y+h*t+h*.12:.0f} {x+w*(1-t*.2):.0f} {y+h*t:.0f}" stroke="{col}" stroke-width="{sw}" fill="none"/>')
    return "".join(out)


def wheat(A, y0, y1, col, dark, seed, n=260, ink=None, sc=1.0):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.uniform(-20, W + 20)
        yb = rnd.uniform(y0, y1)
        k = (yb - y0) / max(1, (y1 - y0))
        h = (40 + 120 * k) * sc
        bend = rnd.uniform(-12, 12)
        c = mix(dark, col, rnd.uniform(.3, 1))
        out.append(f'<path d="M{x:.0f} {yb:.0f} Q{x+bend*.4:.0f} {yb-h*.6:.0f} {x+bend:.0f} {yb-h:.0f}" stroke="{c}" stroke-width="{1+2.2*k:.1f}" fill="none"/>'
                   f'<ellipse cx="{x+bend:.0f}" cy="{yb-h-6*(1+k):.0f}" rx="{2+3*k:.1f}" ry="{6+9*k:.1f}" fill="{c}"/>')
    return "".join(out)


def lantern(A, x, y, s, col="#FFC861"):
    return glow(A, x, y, 70 * s, col, .55) + f'<circle cx="{x}" cy="{y}" r="{5*s:.0f}" fill="#FFF3C8"/>'


# ================================================================== KIDS panels
def kids_panels(orth=True):
    P = {}
    st = "kids"
    # ---------------------------------------------------------------- p1 shore at sunset
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#FF8D7A"), (.45, "#FFB06B"), (.75, "#FFD58C")])}"/>')
    A.add(glow(A, 950, 420, 360, "#FFF0B0", .9))
    A.add(f'<circle cx="950" cy="420" r="78" fill="#FFF4C8" stroke="#F3A25A" stroke-width="5"/>')
    A.add(kcloud(A, 230, 150, 110, "#FFD9C9", "#F2A8A0", (1, -.4)) + kcloud(A, 760, 110, 80, "#FFE2CF", "#F4B2A2", (1, -.4)))
    A.add(A.shaded(ridge(430, 90, 4, 7), [("#A8708F", 0, 0), ("#C68AA6", -20, 0)], KINK, 4))
    A.add(A.shaded(ridge(455, 50, 7, 9), [("#8E6A92", 0, 0), ("#A98BB0", -20, 0)], KINK, 4))
    A.add(f'<rect y="452" width="{W}" height="240" fill="{A.lin([(0, "#4DB2D6"), (1, "#2C7CB9")])}"/>')
    rnd = random.Random(3)
    for i in range(16):
        yy = 470 + i * 9
        w = 260 - i * 12 + rnd.uniform(-20, 20)
        A.add(f'<path d="M{950-w/2:.0f} {yy} h{w:.0f}" stroke="#FFF1B8" stroke-width="{4 - i*.15:.1f}" stroke-linecap="round" opacity="{.9-i*.04:.2f}"/>')
    for i in range(10):
        x0 = rnd.uniform(0, 700)
        A.add(f'<path d="M{x0:.0f} {rnd.uniform(500,640):.0f} q20 -8 40 0" stroke="#BFE8F7" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>')
    sand = smooth([(-20, 560), (200, 545), (420, 590), (600, 680), (640, 820), (-20, 820)], True, .8)
    A.add(A.shaded(sand, [("#E2B877", 0, 0), ("#F6D59A", 20, -10)], KINK, 4))
    A.add(reeds(30, 600, 1.0, "#4C7A4E", 8, 2))
    for i in range(14):
        A.add(f'<ellipse cx="{rnd.uniform(40,560):.0f}" cy="{rnd.uniform(650,790):.0f}" rx="{rnd.uniform(4,9):.0f}" ry="4" fill="#C9975A"/>')
    crowd = [("villager2", 90, 640, .55, "stand", "smile", 1), ("villager1", 150, 625, .58, "beckon", "smile", 1), ("villager6", 215, 650, .48, "spread", "smile", 1),
             ("villager4", 60, 700, .6, "stand", "smile", 1), ("villager5", 130, 712, .62, "bless", "smile", 1), ("villager3", 205, 720, .6, "stand", "smile", 1)]
    for cid, x, y, s, po, ex, fc in crowd:
        A.add(kid(A, cid, x, y, s, po, ex, facing=fc))
    b, f = kboat(A, 850, 650, .95, sail="none")
    A.add(b)
    A.add(kid(A, "jesus", 820, 640, .98, "point", "smile", nimbus=orth, facing=1))
    anchor(st, "p1", "jesus", head_of_kid(820, 640, .98))
    A.add(f)
    A.add(f'<path d="M560 700 q60 -14 120 -2 q60 12 140 -6" stroke="#E6F6FB" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/>')
    A.add(kid(A, "peter", 430, 735, 1.05, "beckon", "smile", facing=1))
    A.add(kid(A, "john", 330, 752, .92, "stand", "smile", facing=1))
    A.add(vignette(A, .25, "#5A2A3A"))
    P["p1"] = A
    # ---------------------------------------------------------------- p2 calm dusk
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#3D3B87"), (.5, "#8B63B5"), (.8, "#F49CA0")])}"/>')
    A.add(stars(A, 60, 4, 330, "#FFF6C8", 2.6, 6))
    A.add(glow(A, 1010, 150, 200, "#FFF2C0", .6))
    A.add(f'<circle cx="1010" cy="150" r="66" fill="#FFF3C9" stroke="#E9C877" stroke-width="5"/><circle cx="990" cy="140" r="12" fill="#F1DFA7"/><circle cx="1030" cy="170" r="8" fill="#F1DFA7"/>')
    A.add(A.shaded(ridge(470, 60, 11, 8), [("#5B4C8A", 0, 0), ("#7464A6", 20, 0)], KINK, 4))
    A.add(f'<rect y="468" width="{W}" height="340" fill="{A.lin([(0, "#5470B8"), (1, "#2D3F86")])}"/>')
    for i in range(12):
        A.add(f'<path d="M{1010-90+i*4:.0f} {490+i*14} h{180-i*8:.0f}" stroke="#FFF1C2" stroke-width="3" stroke-linecap="round" opacity="{.75-i*.05:.2f}"/>')
    for bx, by, sc in ((130, 545, .28), (300, 520, .2)):
        bb, ff = kboat(A, bx, by, sc)
        A.add(bb + ff + lantern(A, bx + 60 * sc, by - 70 * sc, .6))
    b, f = kboat(A, 590, 620, 1.0)
    A.add(b)
    for cid, x, y, s, po, ex, fc in (("peter", 400, 630, .9, "row", "smile", 1), ("andrew", 490, 622, .85, "row", "calm", 1),
                                    ("james", 590, 620, .85, "row", "smile", 1), ("john", 680, 625, .8, "stand", "smile", -1)):
        A.add(kid(A, cid, x, y, s, po, ex, facing=fc))
    A.add(kid(A, "jesus", 800, 640, .85, "stand", "calm", nimbus=orth, facing=-1))
    A.add(f)
    A.add(A.shaded(waves_path(690, 16, 9, 5), [("#26357A", 0, 0), ("#3A52A0", 0, 8)], KINK, 4))
    A.add(vignette(A, .3, "#1A1440"))
    P["p2"] = A
    # ---------------------------------------------------------------- p3 storm
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#1A1F3D"), (1, "#3B4C80")])}"/>')
    A.add(glow(A, 760, 120, 340, "#BFD3FF", .35))
    for cx, cy, sc in ((140, 70, 160), (420, 40, 150), (1080, 60, 170), (700, 10, 120)):
        A.add(kcloud(A, cx, cy, sc, "#5E6890", "#3E4670", (1, -.5)))
    bolt = "M780 0 L720 160 L790 160 L700 330 L850 120 L770 120 L830 0 Z"
    A.add(f'<path d="{bolt}" fill="#FFE066" stroke="{KINK}" stroke-width="5" stroke-linejoin="round"/>')
    A.add(glow(A, 780, 170, 160, "#FFF2A8", .45))
    A.add(rain(A, 120, 7, -20, "#CFE0FF", .55, 30, 60, 3.2))
    A.add(A.shaded(waves_path(460, 80, 5, 8, sharp=.4), [("#1B4486", 0, 0), ("#2A63AE", 0, 16)], KINK, 5))
    b, f = kboat(A, 590, 560, 1.0, tilt=-13)
    sleeper = (800, 540, .74)
    inner = (kid(A, "peter", 410, 565, .9, "scared", "scared") + kid(A, "andrew", 500, 565, .85, "cling", "scared") +
             kid(A, "james", 600, 560, .85, "bail", "scared") + kid(A, "john", 690, 565, .8, "scared", "scared") +
             f'<rect x="815" y="460" width="86" height="28" rx="13" fill="#D9473E" stroke="{KINK}" stroke-width="4"/>' +
             kid(A, "jesus", *sleeper, "stand", "sleep", rot=80, nimbus=orth))
    A.add(b + f'<g transform="rotate(-13 590 560)">{inner}</g>' + f)
    A.add(A.shaded(waves_path(600, 70, 4, 9, sharp=.6), [("#2059A6", 0, 0), ("#3A7DCB", 0, 14)], KINK, 5))
    for x, y, r in ((300, 560, 16), (330, 534, 10), (360, 550, 7), (880, 590, 18), (930, 566, 11), (960, 586, 8)):
        A.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#F2FAFF" stroke="{KINK}" stroke-width="3"/>')
    A.add(vignette(A, .4, "#05081A"))
    P["p3"] = A
    # ---------------------------------------------------------------- p4 wake up
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#232C57"), (1, "#3F5A8F")])}"/>')
    A.add(glow(A, 250, 80, 420, "#D6E4FF", .35))
    A.add(rain(A, 120, 8, -20, "#CFE0FF", .5, 30, 60, 3))
    A.add(f'<path d="M1050 -20 V560" stroke="{KINK}" stroke-width="30"/><path d="M1050 -20 V560" stroke="#7A4A26" stroke-width="22"/><path d="M1044 -20 V560" stroke="#A06A3E" stroke-width="5"/>')
    deck = smooth([(-30, 540), (300, 500), (700, 520), (1230, 490), (1230, 830), (-30, 830)], True, .6)
    A.add(A.shaded(deck, [("#8C5530", 0, 0), ("#C07B42", 0, 14)], KINK, 6))
    A.add('<path d="M-20 610 Q400 580 1220 600" stroke="#6E4122" stroke-width="8" fill="none"/><path d="M-20 700 Q500 676 1220 690" stroke="#6E4122" stroke-width="8" fill="none"/>')
    A.add(kid(A, "john", 1060, 680, 1.2, "cling", "scared", facing=-1))
    A.add(f'<rect x="560" y="560" width="300" height="66" rx="30" fill="#D9473E" stroke="{KINK}" stroke-width="5"/><path d="M580 580 Q710 566 840 580" stroke="#F0786C" stroke-width="6" fill="none" stroke-linecap="round"/>')
    A.add(kid(A, "jesus", 590, 690, 1.42, "stand", "sleep", rot=82, nimbus=orth))
    A.add(f'<path d="M780 520 q50 -150 140 -70 q-40 10 -54 70 z" fill="#CDEBFF" stroke="{KINK}" stroke-width="4"/><circle cx="830" cy="410" r="16" fill="#CDEBFF" stroke="{KINK}" stroke-width="3"/><circle cx="880" cy="384" r="10" fill="#CDEBFF" stroke="{KINK}" stroke-width="3"/>')
    A.add(kid(A, "peter", 300, 800, 1.7, "reach", "shout", facing=1))
    anchor(st, "p4", "peter", head_of_kid(300, 800, 1.7))
    A.add(f'<path d="M520 420 l26 -20 M540 450 l34 -6 M520 480 l30 10" stroke="#FFE066" stroke-width="7" stroke-linecap="round"/>')
    A.add(vignette(A, .35, "#05081A"))
    P["p4"] = A
    # ---------------------------------------------------------------- p5 rebuke
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#2F3B6E"), (1, "#6C86C2")])}"/>')
    A.add(rays(A, 560, 190, "#FFF0B0", .5, 18, (-200, 20), 1500, 4))
    A.add(glow(A, 560, 190, 420, "#FFF3C2", 1))
    for cx, cy, sc in ((80, 40, 150), (1100, 40, 170), (1180, 200, 120), (-20, 220, 110)):
        A.add(kcloud(A, cx, cy, sc, "#7381B0", "#56628F", (-1, .2)))
    A.add(A.shaded(waves_path(585, 22, 8, 11), [("#3770BC", 0, 0), ("#5A9AE0", 0, 10)], KINK, 4))
    b, f = kboat(A, 640, 660, 1.05, sail="none")
    A.add(b)
    for cid, x, s, po, ex in (("john", 700, .8, "awe", "awe"), ("peter", 790, .92, "awe", "awe"), ("andrew", 875, .84, "awe", "awe"), ("james", 950, .84, "awe", "awe")):
        A.add(kid(A, cid, x, 668, s, po, ex, facing=-1))
    A.add(kid(A, "jesus", 500, 665, 1.3, "raise", "calm", nimbus=orth, facing=-1))
    anchor(st, "p5", "jesus", head_of_kid(500, 665, 1.3))
    A.add(f)
    A.add(A.shaded(waves_path(705, 12, 8, 12), [("#2D62AA", 0, 0), ("#4C88D0", 0, 8)], KINK, 4))
    A.add(vignette(A, .3, "#101A40"))
    P["p5"] = A
    # ---------------------------------------------------------------- p6 great calm
    A = Art()
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#121638"), (.7, "#2B3B78")])}"/>')
    A.add(stars(A, 110, 6, 470, "#FFF6C8", 2.4, 10))
    A.add(glow(A, 1080, 120, 220, "#FFF0B8", .5))
    A.add(f'<circle cx="1080" cy="120" r="56" fill="#FFF3C9" stroke="#E9C877" stroke-width="5"/>')
    A.add(A.shaded(ridge(520, 40, 3, 8), [("#1D2652", 0, 0), ("#28336A", 20, 0)], KINK, 4))
    A.add(f'<rect y="520" width="{W}" height="300" fill="{A.lin([(0, "#2B3B78"), (1, "#121638")])}"/>')
    A.add(f'<g transform="translate(0 1100) scale(1 -1)" opacity=".25">{stars(A, 40, 9, 260, "#FFF6C8", 2)}</g>')
    A.add(f'<ellipse cx="1080" cy="690" rx="70" ry="16" fill="#FFF3C9" opacity=".35"/><ellipse cx="1080" cy="740" rx="40" ry="8" fill="#FFF3C9" opacity=".25"/>')
    b, f = kboat(A, 600, 560, 1.0)
    rb, rf = kboat(A, 600, 560, 1.0)
    A.add(f'<g transform="translate(0 1130) scale(1 -1)" opacity=".22">{rb}{rf}</g>')
    A.add(b)
    figs = (("peter", 420, .9, "awe", "awe", 1), ("andrew", 495, .84, "awe", "awe", 1), ("james", 735, .84, "awe", "awe", -1), ("john", 810, .8, "awe", "awe", -1))
    for cid, x, s, po, ex, fc in figs:
        A.add(kid(A, cid, x, 575, s, po, ex, facing=fc))
    A.add(kid(A, "jesus", 620, 580, .98, "bless", "smile", nimbus=orth, facing=1))
    anchor(st, "p6", "jesus", head_of_kid(620, 580, .98))
    anchor(st, "p6", "disciples", head_of_kid(735, 575, .84))
    A.add(f)
    A.add('<path d="M120 650 h140 M860 670 h180 M380 740 h260" stroke="#8EA4E6" stroke-width="3" stroke-linecap="round" opacity=".5"/>')
    for i in range(10):
        r = random.Random(i)
        A.add(glow(A, r.uniform(80, 1120), r.uniform(560, 760), 14, "#FFF2A0", .9))
    A.add(vignette(A, .35, "#05081A"))
    P["p6"] = A
    for A in P.values():
        A.add(paper(A, .12))
    return P


# ================================================================== NOVEL panels
def finish(A, grain_amt=.2, vig=.6):
    A.add(vignette(A, vig))
    A.add(grain(A, grain_amt))


def novel_panels(orth=True):
    P = {}
    st = "adults"
    # ---------------------------------------------------------------- p1 golden hour
    A = Art()
    lit, amb = "#FFD9A0", "#1A0E08"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#3A4C5A"), (.35, "#B5683A"), (.6, "#F0A65A"), (.72, "#FFD08A")])}"/>')
    A.add(clouds(A, 0, 380, "#FFC48A", 3, (.0022, .011), 1.7, .62, .85))
    A.add(clouds(A, 0, 300, "#6A4A50", 8, (.003, .012), 1.5, .7, .6))
    A.add(rays(A, 1000, 470, "#FFE2A8", .25, 16, (-200, -100), 1400, 3))
    A.add(glow(A, 1000, 470, 420, "#FFE8B0", .9))
    A.add(f'<circle cx="1000" cy="470" r="46" fill="#FFF4D6"/>')
    wf = wobble(A, 5, .015, 2)
    A.add(f'<path d="{ridge(450, 80, 4, 8)}" fill="#8A5A50" opacity=".55" filter="{wf}"/>')
    A.add(f'<path d="{ridge(475, 50, 9, 10)}" fill="#5E3E3A" opacity=".8" filter="{wf}"/>')
    A.add(f'<rect y="472" width="{W}" height="180" fill="{A.lin([(0, "#E8A060"), (1, "#6A3E2E")])}"/>')
    rnd = random.Random(1)
    for i in range(40):
        y = 480 + i * 4 + rnd.uniform(-2, 2)
        w = rnd.uniform(40, 260) * (1 - i / 50)
        A.add(f'<path d="M{1000 - w/2 + rnd.uniform(-60,60):.0f} {y:.0f} h{w:.0f}" stroke="#FFE9B8" stroke-width="{rnd.uniform(1,3):.1f}" opacity="{rnd.uniform(.3,.9):.2f}"/>')
    shore = smooth([(-20, 560), (260, 548), (520, 600), (700, 700), (760, 830), (-20, 830)], True, .8)
    A.add(A.shaded(shore, [("#4A2C1C", 0, 0), ("#2A160C", -30, 10)]))
    crowd = [("villager1", 60, 640, 150), ("villager2", 110, 650, 140), ("villager4", 160, 632, 135), ("villager5", 210, 646, 148), ("villager3", 260, 640, 142), ("villager6", 300, 652, 110)]
    for cid, x, y, h in crowd:
        A.add(novel(A, cid, x, y, h, "stand", -1, (1, -.2), lit, amb))
    b, f = nboat(A, 870, 650, .95, lit=lit, amb=amb, sail="none")
    A.add(b)
    A.add(novel(A, "jesus", 860, 640, 330, "point", 1, (1, -.25), lit, amb, nimbus=orth))
    anchor(st, "p1", "jesus", head_of_novel(860, 640, 330))
    A.add(f)
    A.add(novel(A, "john", 560, 735, 360, "beckon", 1, (1, -.25), lit, amb))
    A.add(novel(A, "peter", 680, 800, 440, "reach", 1, (1, -.25), lit, amb, scale_w=1.12))
    A.add(f'<path d="M640 720 q80 -10 170 0" stroke="#FFE2A8" stroke-width="2" fill="none" opacity=".6"/>')
    finish(A, .18, .55)
    P["p1"] = A
    # ---------------------------------------------------------------- p2 blue hour
    A = Art()
    lit, amb = "#A9D2D8", "#03090B"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#07161D"), (.55, "#1C4A55"), (.75, "#5A7F86")])}"/>')
    A.add(stars(A, 90, 3, 330, "#E8E4DA", 1.4))
    A.add(clouds(A, 120, 420, "#7FA2A8", 5, (.002, .014), 1.5, .72, .45))
    A.add(glow(A, 1010, 140, 160, "#E8E4DA", .5))
    A.add(f'<circle cx="1010" cy="140" r="34" fill="#EDE8DC"/>')
    A.add(f'<path d="{ridge(470, 40, 12, 9)}" fill="#0E2730"/>')
    A.add(f'<rect y="468" width="{W}" height="340" fill="{A.lin([(0, "#2A5560"), (1, "#081619")])}"/>')
    for i in range(14):
        A.add(f'<path d="M{1010-50+i*3:.0f} {482+i*10} h{100-i*6:.0f}" stroke="#E8E4DA" stroke-width="2" opacity="{.6-i*.04:.2f}"/>')
    for bx, by in ((150, 548), (330, 532)):
        bb, ff = nboat(A, bx, by, .22, lit=lit, amb=amb, sail="up")
        A.add(bb + ff + lantern(A, bx + 20, by - 40, .7, "#FFC861"))
    b, f = nboat(A, 600, 610, 1.1, lit=lit, amb=amb, sail="up")
    A.add(b)
    for cid, x, h, po, fc in (("peter", 400, 300, "row", 1), ("andrew", 480, 290, "row", 1), ("james", 570, 292, "row", 1), ("john", 650, 270, "stand", -1)):
        A.add(novel(A, cid, x, 612, h, po, fc, (-1, -.3), lit, amb))
    A.add(novel(A, "jesus", 800, 618, 250, "sleep", -1, (-1, -.3), lit, amb, nimbus=orth, kneel=True, eyes_closed=True))
    A.add(f)
    A.add(f'<path d="{waves_path(680, 6, 10, 4)}" fill="#071417" opacity=".9"/>')
    finish(A, .2, .6)
    P["p2"] = A
    # ---------------------------------------------------------------- p3 storm
    A = Art()
    lit, amb = "#D6EEF2", "#020607"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#03080A"), (1, "#122B32")])}"/>')
    A.add(clouds(A, 0, 520, "#2C4A52", 11, (.003, .008), 1.8, .55, 1))
    A.add(glow(A, 880, 90, 420, "#CFE6EA", .45))
    bolt = "M900 0 L860 120 L895 118 L836 270 L930 96 L892 98 L926 0 Z"
    lf = A.filt('<feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    A.add(f'<path d="{bolt}" fill="#F4FBFC" filter="{lf}"/>')
    A.add(rain(A, 260, 5, -24, "#B9D3D8", .45, 50, 110, 2))
    wave = smooth([(700, 830), (760, 600), (860, 380), (1010, 250), (1140, 230), (1240, 280), (1240, 830)], True, .9)
    A.add(f'<path d="{wave}" fill="{A.lin([(0, "#2E6A76"), (.4, "#123842"), (1, "#061418")], 0, 0, 1, 1)}"/>')
    A.add(f'<path d="M760 600 C820 430 900 330 1010 262" stroke="#9FC4CA" stroke-width="3" fill="none" opacity=".5" filter="{wobble(A, 6, .05, 4)}"/>')
    A.add(f'<path d="M1010 252 C1080 228 1160 224 1236 270 C1180 256 1130 262 1100 286 C1070 270 1040 262 1010 252 Z" fill="#CFE3E6" opacity=".85" filter="{wobble(A, 8, .04, 5)}"/>')
    A.add(clouds(A, 240, 520, "#B9D3D8", 21, (.03, .03), 1.6, .9, .35, 2))
    b, f = nboat(A, 500, 560, 1.0, tilt=-14, lit=lit, amb=amb, light=(1, -.6))
    lightv = (1, -.7)
    inner = (novel(A, "peter", 360, 560, 270, "bail", 1, lightv, lit, amb, expr="fear", scale_w=1.1) +
             novel(A, "andrew", 440, 560, 260, "cling", 1, lightv, lit, amb, expr="fear") +
             novel(A, "james", 530, 560, 262, "bail", 1, lightv, lit, amb, expr="fear") +
             novel(A, "john", 600, 560, 245, "cling", -1, lightv, lit, amb, expr="fear") +
             '<rect x="650" y="496" width="80" height="16" rx="6" fill="#3A2416"/>' +
             novel(A, "jesus", 600, 500, 230, "stand", -1, lightv, "#F2C68A", amb, rot=90, nimbus=orth, eyes_closed=True))
    A.add(b + f'<g transform="rotate(-14 500 560)">{inner}</g>' + f)
    A.add(A.shaded(waves_path(620, 70, 5, 6, sharp=.5), [("#0B242B", 0, 0), ("#081A1F", 0, 30)]))
    A.add(f'<path d="{waves_path(620, 70, 5, 6, sharp=.5)}" fill="none" stroke="#9FC4CA" stroke-width="2.5" opacity=".7" filter="{wobble(A, 6, .05, 3)}"/>')
    finish(A, .22, .5)
    P["p3"] = A
    # ---------------------------------------------------------------- p4 close-up
    A = Art()
    lit, amb = "#DCEFF3", "#020607"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#0B1A1F"), (1, "#18323A")])}"/>')
    A.add(clouds(A, 0, 500, "#24434B", 31, (.004, .01), 1.7, .6, .8))
    A.add(glow(A, 180, 40, 520, "#D8ECF0", .5))
    A.add(rain(A, 200, 9, -22, "#B9D3D8", .45, 50, 110, 2.2))
    A.add(f'<path d="M1060 -20 V600" stroke="#030708" stroke-width="34"/><path d="M1046 -20 V600" stroke="{lit}" stroke-width="2" opacity=".5"/>')
    A.add(novel(A, "john", 1110, 560, 330, "cling", -1, (-1, -.5), lit, amb, expr="fear"))
    deck = smooth([(-30, 560), (600, 520), (1230, 540), (1230, 830), (-30, 830)], True, .6)
    A.add(A.shaded(deck, [("#3A2416", 0, 0), ("#1A0E08", 0, 18)]))
    A.add(f'<path d="M-30 560 Q600 520 1230 540" stroke="#F2C68A" stroke-width="2.5" fill="none" opacity=".7"/>')
    A.add(f'<rect x="760" y="560" width="230" height="48" rx="18" fill="#4A2A18"/><path d="M780 566 Q870 556 970 566" stroke="#C08A5A" stroke-width="3" fill="none"/>')
    A.add(glow(A, 900, 560, 260, "#F2C68A", .35))
    A.add(novel(A, "jesus", 330, 600, 680, "stand", -1, (-1, -.6), "#F2C68A", amb, rot=90, nimbus=orth, eyes_closed=True))
    A.add(novel(A, "peter", 250, 1650, 1450, "touch", 1, (-1, -.4), lit, amb, expr="fear", mouth_open=True, scale_w=1.08))
    anchor(st, "p4", "peter", head_of_novel(250, 1650, 1450))
    A.add(f'<path d="M700 510 q60 -170 170 -90 q-60 14 -76 90 z" fill="#B9D3D8" opacity=".45" filter="{wobble(A, 10, .05, 8)}"/>')
    finish(A, .22, .55)
    P["p4"] = A
    # ---------------------------------------------------------------- p5 rebuke
    A = Art()
    lit, amb = "#FFE6B0", "#02070A"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#0A1B21"), (1, "#24464F")])}"/>')
    A.add(clouds(A, 0, 560, "#2E4E57", 41, (.003, .008), 1.8, .5, 1))
    A.add(rays(A, 420, 150, "#FFE9B8", .32, 22, (-210, 30), 1600, 5))
    A.add(glow(A, 420, 150, 520, "#FFE2A0", .95))
    rnd = random.Random(9)
    A.add("".join(f'<circle cx="{rnd.uniform(0,W):.0f}" cy="{rnd.uniform(0,620):.0f}" r="{rnd.uniform(1,2.6):.1f}" fill="#E8F2F4" opacity="{rnd.uniform(.3,.8):.2f}"/>' for _ in range(220)))
    A.add(A.shaded(waves_path(660, 26, 6, 10), [("#1F3E46", 0, 0), ("#0E2228", 0, 14)]))
    A.add(f'<path d="{waves_path(660, 26, 6, 10)}" fill="none" stroke="#FFE6B0" stroke-width="2" opacity=".5"/>')
    b, f = nboat(A, 680, 720, 1.25, lit=lit, amb=amb, sail="none", light=(-1, -.5))
    A.add(b)
    for cid, x, h, fc in (("john", 760, 240, -1), ("peter", 850, 290, -1), ("andrew", 940, 260, -1), ("james", 1020, 262, -1)):
        A.add(novel(A, cid, x, 728, h, "kneelpray" if cid in ("john", "andrew") else "awe", fc, (-1, -.6), lit, amb, kneel=True, expr="awe"))
    A.add(novel(A, "jesus", 470, 905, 760, "rebuke", 1, (-1, -.7), lit, amb, nimbus=orth, expr="calm"))
    anchor(st, "p5", "jesus", head_of_novel(470, 905, 760))
    A.add(f)
    finish(A, .2, .5)
    P["p5"] = A
    # ---------------------------------------------------------------- p6 calm
    A = Art()
    lit, amb = "#E8E4DA", "#02070A"
    A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#040C10"), (.7, "#163640")])}"/>')
    A.add(stars(A, 220, 12, 500, "#E8E4DA", 1.6))
    A.add(glow(A, 1080, 120, 260, "#E8E4DA", .55))
    A.add(f'<circle cx="1080" cy="120" r="44" fill="#EEEAE0"/>')
    A.add(clouds(A, 300, 520, "#DDE6E6", 51, (.002, .02), 1.4, .8, .25))
    A.add(f'<path d="{ridge(525, 34, 3, 9)}" fill="#071418"/>')
    A.add(f'<rect y="523" width="{W}" height="300" fill="{A.lin([(0, "#163640"), (1, "#03090B")])}"/>')
    A.add(f'<ellipse cx="1080" cy="690" rx="40" ry="140" fill="#E8E4DA" opacity=".08"/>')
    b, f = nboat(A, 600, 575, 1.0, lit=lit, amb=amb, sail="up", light=(1, -.3))
    rb, rf = nboat(A, 600, 575, 1.0, lit=lit, amb=amb, sail="up", light=(1, -.3))
    A.add(f'<g transform="translate(0 1160) scale(1 -1)" opacity=".3">{rb}{rf}</g>')
    A.add(b)
    for cid, x, h, fc in (("peter", 430, 250, 1), ("andrew", 495, 240, 1), ("james", 700, 242, -1), ("john", 765, 228, -1)):
        A.add(novel(A, cid, x, 580, h, "awe", fc, (1, -.3), lit, amb, expr="awe"))
    A.add(novel(A, "jesus", 600, 584, 262, "stand", 1, (1, -.3), "#F2D7A6", amb, nimbus=orth))
    anchor(st, "p6", "jesus", head_of_novel(600, 584, 262))
    anchor(st, "p6", "disciples", head_of_novel(700, 580, 242))
    A.add(f)
    finish(A, .2, .55)
    P["p6"] = A
    return P


# ================================================================== COVERS (episodes 1–8)
def kid_cover(n, orth):
    A = Art()
    if n == 1:  # voice in the wilderness
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#FF9F68"), (.6, "#FFD38A")])}"/>')
        A.add(glow(A, 900, 300, 300, "#FFF2B8", .8))
        A.add(A.shaded(ridge(430, 120, 21, 6), [("#D08A55", 0, 0), ("#E9A86A", -20, 0)], KINK, 4))
        A.add(A.shaded(ridge(520, 70, 22, 7), [("#C47A48", 0, 0), ("#DE9B60", -20, 0)], KINK, 4))
        A.add(A.shaded(smooth([(-20, 600), (300, 570), (700, 620), (1220, 590), (1220, 660), (700, 690), (-20, 670)], True, .8), [("#2F86C4", 0, 0), ("#5BB4E0", 0, -8)], KINK, 4))
        A.add(A.shaded(smooth([(-20, 660), (500, 690), (1220, 650), (1220, 820), (-20, 820)], True, .7), [("#E2B877", 0, 0), ("#F6D59A", 0, -14)], KINK, 4))
        A.add(A.shaded(smooth([(560, 640), (640, 560), (820, 560), (880, 650)], True, .7), [("#9B7A5A", 0, 0), ("#B8987A", -10, -10)], KINK, 4))
        A.add(kid(A, "john_baptist", 720, 600, 1.2, "point", "shout", facing=-1))
        for cid, x, y, s in (("villager1", 140, 740, .9), ("villager2", 250, 760, .85), ("villager5", 360, 750, .9), ("villager4", 470, 770, .82), ("villager6", 90, 790, .7)):
            A.add(kid(A, cid, x, y, s, "stand", "awe", facing=1))
    elif n == 2:  # baptism
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#7FC6F0"), (.7, "#D8F0FF")])}"/>')
        A.add(rays(A, 600, -40, "#FFF6C8", .5, 12, (60, 120), 1100, 5))
        A.add(glow(A, 600, 0, 420, "#FFF7D0", 1))
        A.add(dove(600, 150, .9))
        A.add(A.shaded(ridge(470, 90, 31, 7), [("#7DAA6A", 0, 0), ("#98C27E", -20, 0)], KINK, 4))
        A.add(palm(A, 80, 560, 1.2) + palm(A, 1080, 540, 1.0))
        A.add(kid(A, "jesus", 560, 760, 1.35, "spread", "calm", nimbus=orth))
        A.add(kid(A, "john_baptist", 820, 770, 1.2, "bless", "awe", facing=-1))
        A.add(A.shaded(smooth([(-20, 680), (600, 670), (1220, 680), (1220, 820), (-20, 820)], True, .7), [("#2E7DC0", 0, 0), ("#4FA3DA", 0, -10)], KINK, 4, opacity=.9))
        A.add('<path d="M420 700 q80 -10 160 0 M640 712 q80 -10 160 0 M300 760 q100 -12 200 0" stroke="#D9F2FF" stroke-width="5" fill="none" stroke-linecap="round"/>')
    elif n == 3:  # fishers of people
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#8FD3F0"), (.6, "#FFE7B5")])}"/>')
        A.add(glow(A, 200, 380, 260, "#FFF2B8", .8))
        A.add(kcloud(A, 820, 140, 110) + kcloud(A, 380, 90, 80))
        A.add(A.shaded(ridge(420, 60, 41, 8), [("#7DAA8A", 0, 0), ("#98C2A0", 20, 0)], KINK, 4))
        A.add(f'<rect y="420" width="{W}" height="300" fill="{A.lin([(0, "#4DB2D6"), (1, "#2C7CB9")])}"/>')
        b, f = kboat(A, 760, 560, 1.0)
        A.add(b + kid(A, "peter", 700, 570, .95, "cast", "smile") + kid(A, "andrew", 820, 572, .9, "cast", "smile", facing=-1) + f)
        A.add(net(870, 470, 220, 160, "#F4E3C0", 3))
        A.add(A.shaded(smooth([(-20, 650), (300, 620), (520, 680), (560, 820), (-20, 820)], True, .7), [("#E2B877", 0, 0), ("#F6D59A", 10, -10)], KINK, 4))
        A.add(kid(A, "jesus", 250, 740, 1.25, "beckon", "smile", nimbus=orth))
    elif n == 4:  # day in Capernaum
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#4A3C8C"), (.5, "#C46A8E"), (.8, "#FFB57A")])}"/>')
        A.add(stars(A, 30, 2, 200, "#FFF6C8", 2.2, 4))
        A.add(houses(A, -20, 560, 1.4, 8, 3, "#4A4550", "#6E6878", "#7A5A3A"))
        A.add(A.shaded(smooth([(-20, 560), (1220, 560), (1220, 820), (-20, 820)], True, .5), [("#C99A6A", 0, 0), ("#E2B887", 0, -8)], KINK, 4))
        A.add(lantern(A, 520, 420, 1.2))
        A.add(kid(A, "villager5", 690, 740, 1.0, "kneelpray", "awe", kneel=True, facing=-1))
        A.add(kid(A, "jesus", 520, 740, 1.3, "bless", "calm", nimbus=orth))
        for cid, x, y, s in (("villager1", 860, 700, .8), ("villager4", 950, 720, .82), ("villager3", 1060, 710, .8), ("villager6", 140, 720, .7), ("villager2", 250, 730, .8), ("peter", 360, 735, .85)):
            A.add(kid(A, cid, x, y, s, "stand" if x < 500 else "awe", "awe", facing=-1 if x > 600 else 1))
    elif n == 5:  # the touch
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#FFC98A"), (.7, "#FFF0C8")])}"/>')
        A.add(rays(A, 600, 200, "#FFFFFF", .5, 14, (-200, 20), 1200, 2))
        A.add(A.shaded(ridge(500, 80, 51, 7), [("#C9A06A", 0, 0), ("#E2BC86", -20, 0)], KINK, 4))
        A.add(A.shaded(smooth([(-20, 620), (1220, 600), (1220, 820), (-20, 820)], True, .5), [("#D9B27A", 0, 0), ("#EFCB94", 0, -8)], KINK, 4))
        A.add(kid(A, "jesus", 520, 760, 1.4, "touch", "calm", nimbus=orth))
        A.add(kid(A, "leper", 740, 780, 1.25, "kneelpray", "sad", kneel=True, facing=-1))
        for cid, x in (("peter", 200), ("john", 300)):
            A.add(kid(A, cid, x, 730, .85, "awe", "awe"))
    elif n == 6:  # through the roof
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#8FD3F0"), (.5, "#FFE7B5")])}"/>')
        wall = smooth([(80, 260), (1120, 260), (1120, 820), (80, 820)], True, .2)
        A.add(A.shaded(wall, [("#5B5560", 0, 0), ("#77707C", 30, 0)], KINK, 5))
        A.add(f'<rect x="130" y="320" width="940" height="500" fill="#3A2E2E" stroke="{KINK}" stroke-width="4"/>')
        A.add(f'<rect x="130" y="320" width="940" height="500" fill="{A.rad([(0, "#FFD27A", .55), (1, "#FFD27A", 0)], .5, .1, .7)}"/>')
        A.add(f'<rect x="60" y="230" width="1080" height="40" fill="#7A5A3A" stroke="{KINK}" stroke-width="4"/><rect x="470" y="225" width="260" height="50" fill="#FFE7B5"/>')
        for cid, x in (("villager1", 470), ("villager3", 560), ("villager5", 650), ("james", 730)):
            A.add(kid(A, cid, x, 238, .55, "lift", "smile"))
        A.add(f'<path d="M470 240 L520 520 M730 240 L680 520" stroke="#F4E3C0" stroke-width="5"/>')
        A.add(A.shaded(smooth([(500, 510), (700, 510), (700, 545), (500, 545)], True, .3), [("#C9B48A", 0, 0), ("#E6D2A6", 0, -6)], KINK, 4))
        A.add(kid(A, "paralytic", 600, 535, .6, "stand", "awe", rot=90))
        A.add(kid(A, "jesus", 600, 800, 1.2, "spread", "smile", nimbus=orth))
        for cid, x in (("villager2", 230), ("pharisee", 340), ("villager4", 880), ("peter", 990)):
            A.add(kid(A, cid, x, 800, 1.0, "awe", "awe", facing=1 if x < 600 else -1))
    elif n == 7:  # dinner with sinners
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#2C2350"), (1, "#6A3E5E")])}"/>')
        A.add(glow(A, 600, 470, 520, "#FFC86A", .55))
        for lx in (250, 600, 950):
            A.add(lantern(A, lx, 300, 1.4))
            A.add(f'<path d="M{lx} 160 V292" stroke="#E0B060" stroke-width="3"/>')
        for cid, x, po, ex in (("villager1", 200, "cup", "smile"), ("matthew", 340, "spread", "smile"), ("jesus", 600, "bless", "smile"), ("villager3", 830, "cup", "smile"), ("peter", 980, "stand", "smile")):
            A.add(kid(A, cid, x, 690, 1.1, po, ex, nimbus=(orth and cid == "jesus"), facing=1 if x < 600 else -1))
        A.add(A.shaded(smooth([(60, 600), (1140, 600), (1140, 660), (60, 660)], True, .2), [("#8C5530", 0, 0), ("#B97640", 0, -10)], KINK, 5))
        A.add(f'<rect x="60" y="650" width="1080" height="200" fill="#5A3A22" stroke="{KINK}" stroke-width="5"/>')
        for x in (220, 420, 640, 860, 1020):
            A.add(f'<ellipse cx="{x}" cy="598" rx="46" ry="14" fill="#E9D3A8" stroke="{KINK}" stroke-width="3"/><circle cx="{x-10}" cy="588" r="10" fill="#B83A3A"/><circle cx="{x+12}" cy="590" r="9" fill="#6A9A3A"/>')
        A.add(kid(A, "pharisee", 1110, 560, .8, "hips", "angry", facing=-1))
    elif n == 8:  # lord of the sabbath
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#7FC6F0"), (.6, "#FFF1C8")])}"/>')
        A.add(glow(A, 1000, 160, 200, "#FFF6C8", .9))
        A.add(kcloud(A, 300, 130, 100))
        A.add(A.shaded(ridge(430, 50, 61, 8), [("#9BB070", 0, 0), ("#B4C98A", -20, 0)], KINK, 4))
        A.add(f'<rect y="430" width="{W}" height="400" fill="{A.lin([(0, "#F2C14E"), (1, "#D99A2B")])}"/>')
        A.add(wheat(A, 440, 600, "#FFE08A", "#C68A22", 2, 220, sc=.8))
        for cid, x, po in (("john", 300, "pluck"), ("peter", 420, "cup"), ("andrew", 530, "pluck")):
            A.add(kid(A, cid, x, 690, 1.0, po, "smile"))
        A.add(kid(A, "jesus", 680, 700, 1.15, "bless", "calm", nimbus=orth, facing=-1))
        A.add(kid(A, "pharisee", 920, 700, 1.1, "point", "angry", facing=-1))
        A.add(kid(A, "scribe", 1040, 705, 1.0, "hips", "angry", facing=-1))
        A.add(wheat(A, 650, 820, "#FFE08A", "#B07818", 3, 120, sc=1.2))
    A.add(vignette(A, .25, "#3A1A2A"))
    A.add(paper(A, .12))
    return A


def novel_cover(n, orth):
    A = Art()
    if n == 1:
        lit, amb = "#FFD49A", "#140A06"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#3A3036"), (.45, "#B0603A"), (.7, "#F0A860")])}"/>')
        A.add(clouds(A, 0, 360, "#FFC48A", 61, (.002, .012), 1.6, .65, .7))
        A.add(glow(A, 880, 380, 360, "#FFE2A8", .8))
        wf = wobble(A, 6, .012, 2)
        A.add(f'<path d="{ridge(430, 140, 21, 6)}" fill="#7A4A36" filter="{wf}"/><path d="{ridge(520, 80, 22, 7)}" fill="#4A2A1E" filter="{wf}"/>')
        A.add(f'<path d="M-20 600 Q600 570 1220 600 L1220 640 Q600 610 -20 650 Z" fill="#E8B070" opacity=".8"/>')
        A.add(f'<rect y="640" width="{W}" height="200" fill="#1C0E08"/>')
        A.add(A.shaded(smooth([(560, 660), (640, 560), (820, 560), (880, 660)], True, .7), [("#5A3A2A", 0, 0), ("#2A160C", -30, 0)]))
        A.add(novel(A, "john_baptist", 720, 600, 400, "raise", -1, (1, -.3), lit, amb, expr="anger"))
        for cid, x, y, h in (("villager1", 140, 760, 300), ("villager2", 250, 780, 280), ("villager5", 360, 770, 300), ("villager4", 470, 790, 270)):
            A.add(novel(A, cid, x, y, h, "stand", 1, (1, -.3), lit, amb))
    elif n == 2:
        lit, amb = "#FFF2D0", "#06100F"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#2E4E57"), (.6, "#9AB4AE")])}"/>')
        A.add(clouds(A, 0, 400, "#2A3E44", 71, (.003, .01), 1.7, .5, .9))
        A.add(rays(A, 600, -60, "#FFF6D8", .45, 14, (65, 115), 1100, 6))
        A.add(glow(A, 600, 0, 460, "#FFF6D8", 1))
        A.add(dove(600, 160, .8, "#FFFFFF", "#000", False))
        A.add(f'<path d="{ridge(470, 80, 31, 7)}" fill="#33503F" filter="{wobble(A, 5, .015, 3)}"/>')
        A.add(novel(A, "jesus", 560, 900, 620, "stand", 1, (0, -1), lit, amb, nimbus=orth))
        A.add(novel(A, "john_baptist", 900, 920, 580, "awe", -1, (-.3, -1), lit, amb, expr="awe"))
        A.add(f'<rect y="610" width="{W}" height="220" fill="{A.lin([(0, "#5E8A86", .85), (1, "#0E2226", .95)])}"/>')
        A.add('<path d="M380 616 q120 -8 240 0 M640 630 q120 -8 240 0" stroke="#FFF6D8" stroke-width="2" fill="none" opacity=".7"/>')
    elif n == 3:
        lit, amb = "#FFE2B0", "#06100F"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#5E7E8A"), (.55, "#E8B888")])}"/>')
        A.add(clouds(A, 0, 380, "#FFE2C0", 81, (.002, .012), 1.6, .65, .7))
        A.add(glow(A, 180, 400, 300, "#FFF0C8", .9))
        A.add(f'<path d="{ridge(430, 50, 41, 8)}" fill="#4E6A64"/>')
        A.add(f'<rect y="428" width="{W}" height="300" fill="{A.lin([(0, "#7FA2A0"), (1, "#1E3A40")])}"/>')
        b, f = nboat(A, 760, 560, 1.0, lit=lit, amb=amb, sail="none", light=(-1, -.3))
        A.add(b + novel(A, "peter", 700, 566, 270, "cast", 1, (-1, -.3), lit, amb, scale_w=1.1) + novel(A, "andrew", 830, 568, 260, "cast", -1, (-1, -.3), lit, amb) + f)
        A.add(net(880, 450, 240, 180, "#E8D6B0", 1.6))
        A.add(A.shaded(smooth([(-20, 650), (300, 620), (520, 690), (560, 830), (-20, 830)], True, .7), [("#3A2A1E", 0, 0), ("#1A100A", 30, 0)]))
        A.add(novel(A, "jesus", 250, 790, 460, "beckon", 1, (-1, -.3), lit, amb, nimbus=orth))
    elif n == 4:
        lit, amb = "#FFC66A", "#0A0608"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#14182E"), (.6, "#6A3A4A"), (.85, "#C27050")])}"/>')
        A.add(stars(A, 60, 2, 240, "#E8E4DA", 1.4))
        A.add(houses(A, -20, 570, 1.5, 8, 3, "#14121A", "#2A2630", "#1A140E", "#000", "#FFB54A", False))
        A.add(f'<rect y="566" width="{W}" height="260" fill="#120C0A"/>')
        A.add(glow(A, 560, 560, 360, "#FFC66A", .5))
        A.add(novel(A, "villager5", 700, 760, 300, "kneelpray", -1, (-1, -.4), lit, amb, kneel=True, expr="awe"))
        A.add(novel(A, "jesus", 520, 780, 460, "bless", 1, (-1, -.4), lit, amb, nimbus=orth))
        for cid, x, h in (("villager1", 860, 360), ("villager4", 960, 350), ("villager3", 1060, 360), ("peter", 330, 380), ("villager2", 200, 350)):
            A.add(novel(A, cid, x, 760, h, "stand", -1 if x > 600 else 1, (-1 if x > 600 else 1, -.4), lit, amb))
    elif n == 5:
        lit, amb = "#FFF0CC", "#0A0806"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#6E5A48"), (.6, "#E8C890")])}"/>')
        A.add(clouds(A, 0, 400, "#FFF0D0", 91, (.002, .012), 1.6, .6, .6))
        A.add(rays(A, 600, 160, "#FFF6E0", .4, 14, (-200, 20), 1200, 2))
        A.add(f'<path d="{ridge(520, 70, 51, 7)}" fill="#6A5038" filter="{wobble(A, 5, .015, 3)}"/>')
        A.add(f'<rect y="610" width="{W}" height="220" fill="#2A1C12"/>')
        A.add(novel(A, "jesus", 500, 830, 600, "touch", 1, (-1, -.5), lit, amb, nimbus=orth))
        A.add(novel(A, "leper", 760, 830, 460, "kneelpray", -1, (-1, -.5), lit, amb, kneel=True, expr="pain"))
    elif n == 6:
        lit, amb = "#FFD27A", "#0A0806"
        A.add(f'<rect width="{W}" height="{H}" fill="#120E0C"/>')
        A.add(f'<rect x="440" y="0" width="320" height="300" fill="{A.lin([(0, "#BFE2EE"), (1, "#FFF2CC")])}"/>')
        A.add(rays(A, 600, -40, "#FFF2CC", .35, 10, (70, 110), 1000, 3))
        A.add(f'<rect x="0" y="280" width="1200" height="40" fill="#2A1C12"/><rect x="440" y="276" width="320" height="48" fill="#BFE2EE" opacity=".6"/>')
        for x in (470, 560, 650, 730):
            A.add(novel(A, "villager1" if x != 730 else "james", x, 286, 150, "lift", 1, (0, -1), lit, amb))
        A.add('<path d="M470 290 L520 520 M730 290 L680 520" stroke="#C8B48A" stroke-width="3"/>')
        A.add(A.shaded(smooth([(500, 510), (700, 510), (700, 540), (500, 540)], True, .3), [("#8A7A5A", 0, 0), ("#4A3E2A", 0, 10)]))
        A.add(novel(A, "paralytic", 520, 518, 200, "stand", -1, (0, -1), lit, amb, rot=90))
        A.add(novel(A, "jesus", 600, 940, 600, "bless", 1, (0, -1), lit, amb, nimbus=orth, expr="calm"))
        for cid, x in (("scribe", 220), ("pharisee", 330), ("villager4", 880), ("peter", 990)):
            A.add(novel(A, cid, x, 900, 520, "stand", 1 if x < 600 else -1, (0, -1), lit, amb, expr="awe"))
    elif n == 7:
        lit, amb = "#FFC66A", "#080406"
        A.add(f'<rect width="{W}" height="{H}" fill="#0E0A0C"/>')
        A.add(glow(A, 600, 470, 560, "#FFB54A", .55))
        for lx in (250, 600, 950):
            A.add(lantern(A, lx, 380, 1.4, "#FFC66A"))
        for cid, x, po in (("villager1", 210, "stand"), ("matthew", 370, "cup"), ("jesus", 600, "bless"), ("villager3", 830, "cup"), ("peter", 990, "stand")):
            A.add(novel(A, cid, x, 760, 380, po, 1 if x < 600 else -1, (0, -1), lit, amb, nimbus=(orth and cid == "jesus")))
        A.add(A.shaded(smooth([(60, 600), (1140, 600), (1140, 640), (60, 640)], True, .2), [("#6A4024", 0, 0), ("#3A2010", 0, 12)]))
        A.add(f'<rect x="60" y="636" width="1080" height="200" fill="#1A0E08"/>')
        A.add(novel(A, "pharisee", 1120, 620, 300, "hips", -1, (-1, -.3), "#8AA0A8", amb, expr="anger"))
    elif n == 8:
        lit, amb = "#FFE2A0", "#0E0A04"
        A.add(f'<rect width="{W}" height="{H}" fill="{A.lin([(0, "#6A8A96"), (.55, "#F2D49A")])}"/>')
        A.add(clouds(A, 0, 360, "#FFF0D0", 95, (.002, .012), 1.6, .6, .7))
        A.add(glow(A, 1000, 200, 300, "#FFF2CC", .9))
        A.add(f'<path d="{ridge(430, 50, 61, 8)}" fill="#7A7A50"/>')
        A.add(f'<rect y="430" width="{W}" height="400" fill="{A.lin([(0, "#C8963A"), (1, "#4A3010")])}"/>')
        A.add(wheat(A, 440, 600, "#F2D07A", "#7A5418", 2, 260, sc=.8))
        for cid, x, po in (("john", 300, "pluck"), ("peter", 420, "cup"), ("andrew", 530, "pluck")):
            A.add(novel(A, cid, x, 720, 360, po, 1, (1, -.4), lit, amb))
        A.add(novel(A, "jesus", 690, 740, 420, "bless", -1, (1, -.4), lit, amb, nimbus=orth))
        A.add(novel(A, "pharisee", 920, 740, 410, "point", -1, (1, -.4), lit, amb, expr="anger"))
        A.add(novel(A, "scribe", 1050, 745, 400, "hips", -1, (1, -.4), lit, amb, expr="anger"))
        A.add(wheat(A, 680, 830, "#E8C060", "#5A3A10", 3, 140, sc=1.3))
    finish(A, .18, .55)
    return A


# ================================================================== character sheets
ORDER = ["jesus", "peter", "andrew", "james", "john", "matthew", "judas", "john_baptist", "mary_magdalene", "pharisee", "roman_soldier", "child"]


def kid_sheet(orth):
    A = Art(1800, 1000)
    A.add(f'<rect width="1800" height="1000" fill="{A.lin([(0, "#FFF4E0"), (1, "#FFE6C4")])}"/>')
    for row in (0, 1):
        A.add(f'<ellipse cx="900" cy="{470+row*490}" rx="900" ry="26" fill="#F5D7A8"/>')
    poses = {"jesus": ("bless", "smile"), "peter": ("hips", "smile"), "andrew": ("beckon", "calm"), "james": ("point", "smile"), "john": ("awe", "awe"),
             "matthew": ("cup", "smile"), "judas": ("stand", "calm"), "john_baptist": ("raise", "shout"), "mary_magdalene": ("spread", "smile"),
             "pharisee": ("hips", "worried"), "roman_soldier": ("stand", "calm"), "child": ("lift", "smile")}
    for i, cid in enumerate(ORDER):
        col, row = i % 6, i // 6
        x, y = 150 + col * 300, 460 + row * 490
        po, ex = poses[cid]
        A.add(kid(A, cid, x, y, 1.6 if cid != "child" else 1.25, po, ex, nimbus=(orth and cid == "jesus"), facing=1 if col % 2 == 0 else -1))
    A.add(paper(A, .12))
    return A


def novel_sheet(orth):
    A = Art(1800, 1000)
    lit, amb = "#F2D7A6", "#071114"
    A.add(f'<rect width="1800" height="1000" fill="{A.lin([(0, "#0D2128"), (1, "#1C3E46")])}"/>')
    A.add(glow(A, 900, 300, 900, "#2E5A62", .6))
    for i, cid in enumerate(ORDER):
        col, row = i % 6, i // 6
        x, y = 150 + col * 300, 470 + row * 490
        A.add(f'<ellipse cx="{x}" cy="{y}" rx="110" ry="14" fill="#000" opacity=".35"/>')
        A.add(novel(A, cid, x, y, 430 if cid != "child" else 320, "stand", 1 if col % 2 == 0 else -1, (1 if col % 2 == 0 else -1, -.35), lit, amb, nimbus=(orth and cid == "jesus")))
    A.add(grain(A, .16))
    return A


# ================================================================== main
def strip_nimbus(svg):
    import re
    return re.sub(r'<g class="nimbus">.*?</g>', "", svg, flags=re.S)


def kid_hero(orth=True):
    A = Art(1800, 900)
    A.add(f'<rect width="1800" height="900" fill="{A.lin([(0, "#7FC4EE"), (.45, "#FFC7A0"), (.62, "#FFE3A6")])}"/>')
    A.add(glow(A, 1300, 520, 520, "#FFF4C8", 1))
    A.add(f'<circle cx="1300" cy="520" r="90" fill="#FFF0B0" stroke="#F3A25A" stroke-width="6"/>')
    A.add(kcloud(A, 300, 170, 150, "#FFFFFF", "#F2D6E0", (1, -.4)) + kcloud(A, 900, 110, 110, "#FFFFFF", "#F2D6E0", (1, -.4)) + kcloud(A, 1550, 200, 120, "#FFFFFF", "#F2D6E0", (1, -.4)))
    A.add(A.shaded(ridge(560, 110, 4, 7, 1800, 900), [("#9C7CB0", 0, 0), ("#B898C8", -24, 0)], KINK, 4))
    A.add(A.shaded(ridge(590, 60, 7, 9, 1800, 900), [("#7FA88A", 0, 0), ("#9AC4A0", -24, 0)], KINK, 4))
    A.add(f'<rect y="588" width="1800" height="320" fill="{A.lin([(0, "#56BCE0"), (1, "#2C7CB9")])}"/>')
    rnd = random.Random(2)
    for i in range(14):
        y = 604 + i * 11
        w = 300 - i * 16
        A.add(f'<path d="M{1300-w/2:.0f} {y} h{w:.0f}" stroke="#FFF4C8" stroke-width="5" stroke-linecap="round" opacity="{.9-i*.05:.2f}"/>')
    for i in range(16):
        x0 = rnd.uniform(0, 1700)
        A.add(f'<path d="M{x0:.0f} {rnd.uniform(640, 860):.0f} q24 -9 48 0" stroke="#C8EEFA" stroke-width="4" fill="none" stroke-linecap="round" opacity=".8"/>')
    b, f = kboat(A, 1150, 760, 1.15)
    A.add(b)
    A.add(kid(A, "peter", 900, 770, 1.0, "row", "smile") + kid(A, "andrew", 990, 765, .95, "row", "smile") + kid(A, "james", 1090, 762, .95, "row", "smile") +
          kid(A, "john", 1190, 766, .9, "lift", "smile") + kid(A, "jesus", 1340, 772, 1.08, "point", "smile", nimbus=orth))
    A.add(f)
    A.add(A.shaded(waves_path(820, 16, 12, 5, 1800, 900), [("#2A6FB0", 0, 0), ("#3F8ED0", 0, 8)], KINK, 4))
    A.add(paper(A, .12))
    return A


def _lines(text, w_pct, kids):
    fs = 31 if kids else 25
    per_line = max(6, int(w_pct / 100 * 1200 / (fs * .5)))
    return max(1, -(-len(text) // per_line))


def place_bubbles(ep, ANCH=ANCH):
    """Move speech bubbles next to the speaker and aim the tail at the head."""
    for p in ep["panels"]:
        for style, bubbles in p["bubbles"].items():
            anch = ANCH.get((style, p["id"]), {})
            boxes = []
            for b in bubbles:
                txt = max((b["text"]["en"], b["text"]["ru"]), key=len)
                hgt = _lines(txt, b["w"], style == "kids") * (5.2 if style == "kids" else 4.4) + 3.5
                b["_h"] = hgt
                if b["kind"] in ("caption", "sfx"):
                    boxes.append((b["x"], b["y"], b["x"] + b["w"], b["y"] + hgt))
            for b in bubbles:
                a = anch.get(b.get("who"))
                if not a or b["kind"] in ("caption", "sfx"):
                    continue
                ax, ay = a
                x = min(max(ax - b["w"] / 2, 2), 98 - b["w"])
                y = max(3, ay - 12 - b["_h"])
                cand = (x, y, x + b["w"], y + b["_h"])
                if any(not (cand[2] < bx0 or cand[0] > bx1 or cand[3] < by0 or cand[1] > by1) for bx0, by0, bx1, by1 in boxes):
                    x, y = b["x"], b["y"]
                    cand = (x, y, x + b["w"], y + b["_h"])
                b["x"], b["y"] = round(x, 1), round(y, 1)
                b["tx"], b["ty"] = ax, round(ay - (6 if style == "kids" else 4), 1)
                boxes.append(cand)
            for b in bubbles:
                b.pop("_h", None)


def main():
    import render_adults as RA
    out = ROOT / "art"
    d = out / "kids" / "ep12-storm"
    d.mkdir(parents=True, exist_ok=True)
    for pid, A in kids_panels(True).items():
        (d / f"{pid}.svg").write_text(A.svg())
    d = out / "adults" / "ep12-storm"
    d.mkdir(parents=True, exist_ok=True)
    for pid, (A, an) in RA.panels(True).items():
        (d / f"{pid}.svg").write_text(A.svg())
        for who, pt in an.items():
            anchor("adults", pid, who, pt)
    (out / "kids" / "character-sheet.svg").write_text(kid_sheet(True).svg())
    (out / "adults" / "character-sheet.svg").write_text(RA.sheet(True).svg())
    (out / "kids" / "hero.svg").write_text(kid_hero(True).svg())
    (out / "adults" / "hero.svg").write_text(RA.hero(True).svg())
    for style, fn in (("kids", kid_cover), ("adults", RA.cover)):
        cd = out / style / "covers"
        cd.mkdir(parents=True, exist_ok=True)
        for n in range(1, 9):
            (cd / f"ep{n:02d}.svg").write_text(fn(n, True).svg())
    ep_file = ROOT / "episodes/ep12-storm/episode.json"
    ep = json.loads(ep_file.read_text())
    place_bubbles(ep)
    ep_file.write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n")
    render_season1()
    print("art written")


def render_season1(only=None):
    import scenes
    import sys
    sys.path.insert(0, str(ROOT / "tools" / "authoring"))
    from season1_scenes import SCENES
    for ep_id, panels in SCENES.items():
        if only and ep_id not in only:
            continue
        anch = {}
        for style, fn in (("kids", scenes.render_kids), ("adults", scenes.render_adults)):
            d = ROOT / "art" / style / ep_id
            d.mkdir(parents=True, exist_ok=True)
            for pid, spec in panels.items():
                A, heads = fn(spec, True)
                (d / f"{pid}.svg").write_text(A.svg())
                anch[(style, pid)] = {k: (round(v[0] / W * 100, 1), round(v[1] / H * 100, 1)) for k, v in heads.items()}
                if heads:
                    anch[(style, pid)]["disciples"] = next(iter(anch[(style, pid)].values()))
        f = ROOT / "episodes" / ep_id / "episode.json"
        ep = json.loads(f.read_text())
        place_bubbles(ep, anch)
        f.write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n")
        print("drew", ep_id)


if __name__ == "__main__":
    main()
