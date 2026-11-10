"""Adult edition: cinematic graphic novel built from light, atmosphere and silhouettes.

People stay at medium scale; the drama is carried by sky, water, weather and
rim light. Every scene is layered front-to-back with atmospheric perspective.
"""
import math
import random

from art_engine import Art, W, H, mix, shade, smooth, poly, circ, ell, clouds, grain, vignette, glow, rays, rain, stars, ridge, waves_path, wobble
from silhouette import sil, head_of_sil

# ------------------------------------------------------------------ environment kit


def sky(A, stops):
    A.add(f'<rect width="{A.w}" height="{A.h}" fill="{A.lin(stops)}"/>')


def hills(A, horizon, haze, near, n=3, seed=1, amp=(70, 40, 20), wob=True):
    """n mountain layers from far (close to haze colour) to near."""
    f = wobble(A, 4, .012, seed) if wob else None
    for i in range(n):
        t = (i + 1) / (n + 1)
        col = mix(haze, near, t)
        y = horizon - amp[i] * .2 + i * 6
        d = ridge(y, amp[i] if i < len(amp) else 20, seed + i * 7, 7 + i * 2)
        A.add(f'<path d="{d}" fill="{col}"' + (f' filter="{f}"' if f else "") + "/>")


def water(A, top, c_top, c_bot, glint=None, glint_x=None, seed=2, lines=True, mirror_sky=None):
    A.add(f'<rect y="{top}" width="{A.w}" height="{A.h-top+2}" fill="{A.lin([(0, c_top), (1, c_bot)])}"/>')
    if mirror_sky:
        A.add(f'<rect y="{top}" width="{A.w}" height="{A.h-top+2}" fill="{A.lin(mirror_sky)}" opacity=".35"/>')
    rnd = random.Random(seed)
    if glint and glint_x is not None:
        for i in range(60):
            y = top + 4 + i * (A.h - top) / 70 * (1 + i / 60)
            if y > A.h:
                break
            w = rnd.uniform(20, 160) * (1 - i / 80)
            A.add(f'<path d="M{glint_x - w/2 + rnd.uniform(-40-i*3, 40+i*3):.0f} {y:.0f} h{w:.0f}" stroke="{glint}" stroke-width="{rnd.uniform(1, 2.6):.1f}" opacity="{rnd.uniform(.25, .85)*(1-i/70):.2f}" stroke-linecap="round"/>')
    if lines:
        for i in range(40):
            y = top + rnd.uniform(6, A.h - top)
            x = rnd.uniform(-50, A.w)
            A.add(f'<path d="M{x:.0f} {y:.0f} q{30+ (y-top)*.2:.0f} -3 {60 + (y-top)*.4:.0f} 0" stroke="#000" stroke-opacity="{.08 + (y-top)/(A.h-top)*.12:.2f}" stroke-width="1.6" fill="none"/>')


def haze(A, y, col, h=80, a=.5):
    A.add(f'<rect y="{y-h/2}" width="{A.w}" height="{h}" fill="{A.lin([(0, col, 0), (.5, col, a), (1, col, 0)])}"/>')


def boat(A, x, y, s=1.0, tilt=0, dark="#0A0806", lit="#F2D7A6", sail="up", light=(1, -.3), sailcol="#8C7A5E", lanterns=False):
    L = 260 * s
    back, front = [], []
    if sail != "none":
        back.append(f'<path d="M{x-12*s:.0f} {y-24*s:.0f} V{y-360*s:.0f}" stroke="{dark}" stroke-width="{8*s:.1f}" stroke-linecap="round"/>')
        back.append(f'<path d="M{x-12*s:.0f} {y-350*s:.0f} L{x+120*s:.0f} {y-330*s:.0f}" stroke="{dark}" stroke-width="{5*s:.1f}"/>')
        if sail == "up":
            sd = (f"M{x-6*s:.0f} {y-344*s:.0f} L{x+118*s:.0f} {y-328*s:.0f} Q{x+186*s:.0f} {y-230*s:.0f} {x+156*s:.0f} {y-112*s:.0f} "
                  f"L{x-6*s:.0f} {y-104*s:.0f} Q{x+40*s:.0f} {y-224*s:.0f} {x-6*s:.0f} {y-344*s:.0f} Z")
            back.append(A.shaded(sd, [(mix(sailcol, lit, .32), 0, 0), (mix(sailcol, dark, .5), -light[0] * 30 * s, 0)]))
            back.append(f'<path d="M{x-6*s:.0f} {y-104*s:.0f} L{x+156*s:.0f} {y-112*s:.0f}" stroke="{dark}" stroke-width="{5*s:.1f}"/>')
            back.append(f'<path d="M{x+20*s:.0f} {y-338*s:.0f} Q{x+50*s:.0f} {y-220*s:.0f} {x+30*s:.0f} {y-106*s:.0f}" stroke="{dark}" stroke-opacity=".25" stroke-width="{2*s:.1f}" fill="none"/>')
        elif sail == "furl":
            back.append(f'<path d="M{x-12*s:.0f} {y-346*s:.0f} Q{x+50*s:.0f} {y-320*s:.0f} {x+118*s:.0f} {y-328*s:.0f}" stroke="{mix(sailcol, dark, .3)}" stroke-width="{12*s:.1f}" stroke-linecap="round" fill="none"/>')
    hull = smooth([(x - L, y - 60 * s), (x - L * .86, y + 16 * s), (x - L * .5, y + 38 * s), (x + L * .5, y + 38 * s), (x + L * .88, y + 14 * s),
                   (x + L * 1.06, y - 78 * s), (x + L * .98, y - 70 * s), (x, y - 28 * s), (x - L * .92, y - 52 * s)], True, .7)
    front.append(A.shaded(hull, [(mix("#3A2416", lit, .45), 0, 0), (mix("#2A1A10", dark, .5), -light[0] * 6 * s, 5 * s), (dark, -light[0] * 26 * s, 22 * s)]))
    front.append(f'<path d="M{x-L*.95:.0f} {y-54*s:.0f} Q{x:.0f} {y-22*s:.0f} {x+L*1.0:.0f} {y-72*s:.0f}" stroke="{lit}" stroke-width="{2.2*s:.1f}" fill="none" stroke-opacity=".85"/>')
    for yy in (-6, 16):
        front.append(f'<path d="M{x-L*.86:.0f} {y+yy*s:.0f} Q{x:.0f} {y+(yy+16)*s:.0f} {x+L*.9:.0f} {y+(yy-12)*s:.0f}" stroke="#000" stroke-opacity=".35" stroke-width="{1.6*s:.1f}" fill="none"/>')
    if lanterns:
        front.append(glow(A, x + L * .9, y - 90 * s, 60 * s, "#FFC861", .7) + f'<circle cx="{x+L*.9:.0f}" cy="{y-90*s:.0f}" r="{4*s:.1f}" fill="#FFF0C0"/>')
    b, f = "".join(back), "".join(front)
    if tilt:
        b, f = (f'<g transform="rotate({tilt} {x} {y})">{v}</g>' for v in (b, f))
    return b, f


def reflection(A, svg, axis_y, op=.28, blur=2):
    fb = A.filt(f'<feGaussianBlur stdDeviation="0 {blur}"/>')
    return f'<g transform="translate(0 {2*axis_y}) scale(1 -1)" opacity="{op}" filter="{fb}">{svg}</g>'


def reeds(x, y, s, col, n=10, seed=1):
    rnd = random.Random(seed)
    out = ""
    for i in range(n):
        dx = rnd.uniform(-40, 40) * s
        h = rnd.uniform(80, 200) * s
        b = rnd.uniform(-30, 30) * s
        out += f'<path d="M{x+dx:.0f} {y:.0f} Q{x+dx+b*.3:.0f} {y-h*.6:.0f} {x+dx+b:.0f} {y-h:.0f}" stroke="{col}" stroke-width="{rnd.uniform(2, 4.5)*s:.1f}" fill="none" stroke-linecap="round"/>'
        if i % 3 == 0:
            out += f'<ellipse cx="{x+dx+b:.0f}" cy="{y-h:.0f}" rx="{4*s:.1f}" ry="{13*s:.1f}" fill="{col}" transform="rotate({b/s*.5:.0f} {x+dx+b:.0f} {y-h:.0f})"/>'
    return out


def bolt(A, pts, col="#F4FBFC", w=4):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    f = A.filt('<feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>')
    return f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round" filter="{f}"/>'


def finish(A, g=.16, v=.5):
    A.add(vignette(A, v))
    A.add(grain(A, g))


def anchor_rel(pt):
    return (round(pt[0] / W * 100, 1), round(pt[1] / H * 100, 1))


# ================================================================== pilot panels
def panels(orth=True):
    P, AN = {}, {}

    # ---------------------------------------------------------------- p1 golden hour on the shore
    A = Art()
    lit, amb = "#FFE0A8", "#140B07"
    sky(A, [(0, "#2C3E4C"), (.32, "#8A5A4A"), (.55, "#E09A58"), (.68, "#FFD08C")])
    A.add(clouds(A, 20, 380, "#FFC58C", 3, (.0018, .010), 1.7, .62, .8))
    A.add(clouds(A, 0, 260, "#5A3E44", 8, (.0025, .012), 1.6, .72, .55))
    A.add(glow(A, 960, 445, 520, "#FFE7B4", .95))
    A.add(f'<circle cx="960" cy="445" r="40" fill="#FFF6DC"/>')
    hills(A, 455, "#E6A673", "#5A3326", 3, 4, (70, 46, 22))
    haze(A, 458, "#FFD7A0", 40, .6)
    water(A, 462, "#E8A562", "#3A2219", "#FFF0C8", 960, 1)
    shore = smooth([(-30, 585), (230, 566), (470, 600), (640, 690), (700, 830), (-30, 830)], True, .8)
    A.add(f'<path d="{shore}" fill="{amb}"/><path d="M-30 585 Q230 566 470 600 Q600 650 640 690" stroke="{lit}" stroke-width="2" fill="none" opacity=".5"/>')
    A.add(reeds(40, 600, .9, amb, 12, 3))
    for i, (cid, x, y, h) in enumerate((("villager1", 120, 612, 118), ("villager2", 160, 618, 110), ("villager4", 205, 608, 112),
                                         ("villager5", 250, 616, 120), ("villager3", 300, 610, 116), ("villager6", 335, 620, 86))):
        A.add(sil(A, cid, x, y, h, "stand", -1, (1, -.2), lit, amb))
    b, f = boat(A, 900, 660, .9, dark=amb, lit=lit, sail="none")
    A.add(b)
    A.add(sil(A, "jesus", 880, 646, 300, "point", 1, (1, -.25), lit, amb, nimbus=orth))
    AN["jesus"] = head_of_sil(880, 646, 300)
    A.add(f)
    A.add(f'<path d="M680 700 q90 -10 200 2 q80 8 160 -4" stroke="{lit}" stroke-width="2" fill="none" opacity=".55"/>')
    A.add(sil(A, "john", 560, 740, 300, "beckon", 1, (1, -.25), lit, amb))
    A.add(sil(A, "peter", 690, 770, 330, "reach", 1, (1, -.25), lit, amb, scale_w=1.12))
    finish(A, .14, .45)
    P["p1"] = (A, AN)

    # ---------------------------------------------------------------- p2 blue hour, sailing
    A, AN = Art(), {}
    lit, amb = "#BFE0E4", "#040B0E"
    sky(A, [(0, "#06121A"), (.45, "#1B4250"), (.66, "#6D8C8C"), (.72, "#C9A27C")])
    A.add(stars(A, 120, 3, 300, "#E8E4DA", 1.4))
    A.add(clouds(A, 160, 440, "#C9A27C", 5, (.0015, .02), 1.5, .74, .45))
    A.add(glow(A, 1010, 140, 220, "#E8E4DA", .55) + '<circle cx="1010" cy="140" r="30" fill="#F0ECE2"/>')
    hills(A, 470, "#6D8C8C", "#0C2229", 2, 12, (36, 22))
    haze(A, 472, "#C9A27C", 26, .5)
    water(A, 474, "#4E6E72", "#061012", "#F0D9B0", 640, 4, mirror_sky=[(0, "#C9A27C"), (1, "#061012")])
    for bx, by, sc in ((150, 540, .2), (330, 528, .16)):
        bb, ff = boat(A, bx, by, sc, dark=amb, lit=lit, sail="up", sailcol="#5E6A66")
        A.add(bb + ff + glow(A, bx + 30, by - 30, 40, "#FFC861", .8) + f'<circle cx="{bx+30}" cy="{by-30}" r="3" fill="#FFF0C0"/>')
        A.add(f'<path d="M{bx+30} {by+6} v40" stroke="#FFC861" stroke-width="3" opacity=".35"/>')
    b, f = boat(A, 600, 620, 1.1, dark=amb, lit=lit, sail="up", sailcol="#9A8C70", lanterns=True)
    figs = (sil(A, "peter", 390, 612, 260, "row", 1, (1, -.3), lit, amb, sit=True) + sil(A, "andrew", 470, 612, 250, "row", 1, (1, -.3), lit, amb, sit=True) +
            sil(A, "james", 560, 612, 252, "row", 1, (1, -.3), lit, amb, sit=True) + sil(A, "john", 650, 614, 240, "stand", -1, (1, -.3), lit, amb, sit=True) +
            sil(A, "jesus", 800, 622, 240, "sleep", -1, (1, -.3), "#F2D7A6", amb, sit=True, nimbus=orth))
    A.add(reflection(A, b + f, 640, .25, 3))
    A.add(b + figs + f)
    finish(A, .16, .55)
    P["p2"] = (A, AN)

    # ---------------------------------------------------------------- p3 the storm
    A, AN = Art(), {}
    lit, amb = "#D8EEF2", "#010405"
    sky(A, [(0, "#020608"), (.6, "#0E2229"), (1, "#163039")])
    A.add(clouds(A, 0, 560, "#1E3A42", 11, (.003, .007), 1.9, .5, 1))
    A.add(glow(A, 880, 130, 460, "#CFE6EA", .55))
    A.add(clouds(A, 0, 360, "#9FC0C6", 13, (.004, .009), 1.8, .72, .55))
    A.add(bolt(A, [(905, 0), (880, 70), (900, 80), (860, 170), (885, 176), (830, 290)], "#F4FBFC", 4))
    A.add(bolt(A, [(880, 70), (840, 120), (850, 150)], "#F4FBFC", 2))
    A.add(rain(A, 320, 5, -24, "#B9D3D8", .42, 60, 130, 1.8))
    wave = smooth([(660, 830), (720, 620), (820, 420), (960, 290), (1090, 236), (1180, 246), (1240, 300), (1240, 830)], True, .9)
    A.add(f'<path d="{wave}" fill="{A.lin([(0, "#3B7884"), (.35, "#143A44"), (1, "#03090B")], .2, 0, 1, 1)}"/>')
    A.add(f'<path d="M1090 236 C1150 222 1210 236 1240 268 C1200 256 1160 262 1130 284 C1110 262 1100 250 1090 236Z" fill="#E0EEF0" opacity=".9" filter="{wobble(A, 10, .05, 7)}"/>')
    A.add(f'<path d="M720 620 C780 470 860 360 960 290" stroke="#A8CCD2" stroke-width="3" fill="none" opacity=".45" filter="{wobble(A, 6, .06, 8)}"/>')
    A.add(clouds(A, 240, 600, "#C8DEE2", 21, (.03, .02), 1.7, .95, .35, 2))
    b, f = boat(A, 470, 560, 1.0, tilt=-15, dark=amb, lit=lit, sail="up", light=(1, -.6), sailcol="#4E5A58")
    lv = (1, -.7)
    inner = (sil(A, "peter", 330, 560, 250, "bail", 1, lv, lit, amb, scale_w=1.1) + sil(A, "andrew", 410, 560, 240, "cling", 1, lv, lit, amb) +
             sil(A, "james", 500, 560, 240, "bail", 1, lv, lit, amb) + sil(A, "john", 575, 560, 228, "scared", -1, lv, lit, amb) +
             f'<rect x="610" y="502" width="78" height="14" rx="6" fill="#2A1A10"/>' +
             sil(A, "jesus", 580, 506, 220, "stand", -1, lv, "#F2C68A", amb, rot=90, nimbus=orth))
    A.add(b + f'<g transform="rotate(-15 470 560)">{inner}</g>' + f)
    front = waves_path(626, 64, 5, 6, sharp=.5)
    A.add(f'<path d="{front}" fill="{A.lin([(0, "#123038"), (1, "#020607")])}"/>')
    A.add(f'<path d="{front}" fill="none" stroke="#A8CCD2" stroke-width="2.5" opacity=".6" filter="{wobble(A, 7, .05, 3)}"/>')
    A.add(rain(A, 120, 15, -24, "#DDEFF2", .5, 120, 220, 2.6))
    finish(A, .2, .45)
    P["p3"] = (A, AN)

    # ---------------------------------------------------------------- p4 "Teacher, don't You care?"
    A, AN = Art(), {}
    lit, amb = "#E4F4F7", "#010405"
    sky(A, [(0, "#9EC4CC"), (.45, "#3E6A74"), (1, "#0C1E24")])
    A.add(clouds(A, 0, 520, "#E8F4F6", 31, (.004, .01), 1.6, .68, .7))
    A.add(glow(A, 300, 60, 640, "#F2FBFC", .8))
    A.add(bolt(A, [(250, 0), (232, 70), (250, 76), (205, 190)], "#FFFFFF", 3))
    A.add(rain(A, 260, 9, -22, "#F0FAFB", .5, 70, 140, 2))
    A.add(f'<path d="M1060 -20 V640" stroke="{amb}" stroke-width="24"/><path d="M1060 -20 L1180 30" stroke="{amb}" stroke-width="10"/>')
    spray = smooth([(760, 560), (800, 430), (880, 380), (960, 420), (900, 440), (860, 520)], True, .8)
    A.add(f'<path d="{spray}" fill="#DDEEF0" opacity=".5" filter="{wobble(A, 12, .05, 8)}"/>')
    deck = smooth([(-30, 600), (500, 556), (1230, 572), (1230, 830), (-30, 830)], True, .6)
    A.add(f'<path d="{deck}" fill="{amb}"/><path d="M-30 600 Q500 556 1230 572" stroke="{lit}" stroke-width="2" fill="none" opacity=".7"/>')
    A.add(sil(A, "john", 1010, 640, 400, "cling", -1, (-1, -.5), lit, amb))
    A.add(f'<rect x="760" y="548" width="150" height="26" rx="12" fill="#1A120C"/><path d="M770 550 Q835 540 900 550" stroke="{lit}" stroke-width="2" fill="none" opacity=".6"/>')
    A.add(sil(A, "jesus", 440, 560, 420, "stand", -1, (-1, -.7), "#F2D7A6", amb, rot=90, nimbus=orth))
    A.add(sil(A, "peter", 330, 640, 520, "touch", 1, (-1, -.4), lit, amb, kneel=True, mouth_open=True, scale_w=1.1))
    AN["peter"] = head_of_sil(330, 640, 520, kneel=True)
    finish(A, .2, .5)
    P["p4"] = (A, AN)

    # ---------------------------------------------------------------- p5 "Silence! Be still!"
    A, AN = Art(), {}
    lit, amb = "#FFE7B4", "#020607"
    sky(A, [(0, "#0A1A20"), (.7, "#28464E")])
    A.add(clouds(A, 0, 600, "#33525A", 41, (.003, .007), 1.9, .5, 1))
    A.add(glow(A, 760, 150, 620, "#FFE2A0", .95))
    A.add(rays(A, 760, 150, "#FFEFC8", .34, 26, (-200, 30), 1700, 5))
    A.add(clouds(A, 0, 360, "#FFE2B0", 43, (.004, .01), 1.8, .78, .45))
    rnd = random.Random(9)
    A.add("".join(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 640):.0f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="#F4F8F6" opacity="{rnd.uniform(.3, .8):.2f}"/>' for _ in range(260)))
    sea = waves_path(668, 22, 7, 10)
    A.add(f'<path d="{sea}" fill="{A.lin([(0, "#2A4C54"), (1, "#03090B")])}"/><path d="{sea}" fill="none" stroke="{lit}" stroke-width="2" opacity=".55"/>')
    A.add(f'<ellipse cx="760" cy="676" rx="260" ry="10" fill="{lit}" opacity=".25"/>')
    b, f = boat(A, 640, 760, 1.35, dark=amb, lit=lit, sail="none", light=(1, -.5))
    A.add(b)
    for cid, x, h, po in (("john", 780, 240, "kneelpray"), ("peter", 860, 270, "awe"), ("andrew", 940, 250, "kneelpray"), ("james", 1020, 250, "awe")):
        A.add(sil(A, cid, x, 742, h, po, -1, (-1, -.6), lit, amb, kneel=True))
    A.add(sil(A, "jesus", 470, 900, 640, "rebuke", 1, (1, -.8), lit, amb, nimbus=orth))
    AN["jesus"] = head_of_sil(470, 900, 640)
    A.add(f)
    finish(A, .18, .45)
    P["p5"] = (A, AN)

    # ---------------------------------------------------------------- p6 great calm
    A, AN = Art(), {}
    lit, amb = "#E8E4DA", "#02070A"
    sky(A, [(0, "#03080C"), (.55, "#0F2830"), (.7, "#244550")])
    A.add(stars(A, 260, 12, 520, "#E8E4DA", 1.6))
    A.add(glow(A, 1060, 130, 300, "#E8E4DA", .5) + '<circle cx="1060" cy="130" r="42" fill="#F2EEE4"/>')
    A.add(clouds(A, 380, 530, "#DDE6E6", 51, (.0015, .03), 1.4, .82, .35))
    hills(A, 530, "#244550", "#06141A", 2, 3, (30, 18))
    haze(A, 534, "#C8D6D6", 30, .35)
    A.add(f'<rect y="536" width="{W}" height="{H-536}" fill="{A.lin([(0, "#1E3E48"), (1, "#020709")])}"/>')
    A.add(f'<g opacity=".25" transform="translate(0 1072) scale(1 -1)">{stars(A, 80, 14, 530, "#E8E4DA", 1.2)}</g>')
    rnd = random.Random(4)
    for i in range(46):
        y = 545 + i * 6
        w = 30 + rnd.uniform(0, 70) * (1 + i / 30)
        A.add(f'<path d="M{1060 - w/2 + rnd.uniform(-12, 12):.0f} {y} h{w:.0f}" stroke="#F2EEE4" stroke-width="1.6" opacity="{.6 - i*.011:.2f}"/>')
    b, f = boat(A, 600, 590, 1.0, dark=amb, lit=lit, sail="up", sailcol="#6E7470")
    figs = "".join(sil(A, cid, x, 584, h, po, fc, (1, -.3), lit, amb) for cid, x, h, po, fc in
                   (("peter", 430, 240, "awe", 1), ("andrew", 490, 230, "awe", 1), ("james", 700, 232, "awe", -1), ("john", 760, 220, "awe", -1)))
    jes = sil(A, "jesus", 600, 588, 252, "bless", 1, (1, -.3), "#F2D7A6", amb, nimbus=orth)
    A.add(reflection(A, b + figs + jes + f, 612, .3, 2))
    A.add(b + figs + jes + f)
    AN["jesus"] = head_of_sil(600, 588, 252)
    AN["disciples"] = head_of_sil(700, 584, 232)
    haze(A, 610, "#C8D6D6", 40, .18)
    finish(A, .16, .5)
    P["p6"] = (A, AN)
    return P


# ================================================================== covers
def cover(n, orth=True):
    A = Art()
    if n == 1:
        lit, amb = "#FFDDA4", "#160B06"
        sky(A, [(0, "#3A3036"), (.4, "#A65E3C"), (.62, "#F0A860"), (.7, "#FFD594")])
        A.add(clouds(A, 0, 380, "#FFC48A", 61, (.002, .012), 1.6, .65, .7))
        A.add(glow(A, 300, 430, 420, "#FFE6B0", .9) + rays(A, 300, 430, "#FFE6B0", .2, 14, (-200, -110), 1200, 6))
        hills(A, 470, "#E09A68", "#3A2016", 3, 21, (110, 70, 40))
        A.add(f'<path d="M-20 640 Q300 600 620 640 T1220 630 L1220 668 Q900 650 600 676 T-20 680 Z" fill="#F2C27E" opacity=".75"/>')
        A.add(f'<rect y="670" width="{W}" height="140" fill="{amb}"/>')
        A.add(smooth([(600, 690), (660, 570), (840, 560), (900, 690)], True, .7).join(['<path d="', f'" fill="{amb}"/>']))
        A.add(sil(A, "john_baptist", 760, 600, 360, "raise", -1, (-1, -.3), lit, amb))
        for cid, x, y, h in (("villager1", 140, 780, 260), ("villager2", 240, 790, 240), ("villager5", 340, 780, 262), ("villager4", 440, 795, 236), ("villager3", 1030, 790, 250), ("villager6", 1110, 800, 180)):
            A.add(sil(A, cid, x, y, h, "stand", 1 if x < 600 else -1, (-1, -.3), lit, amb))
    elif n == 2:
        lit, amb = "#FFF4D6", "#06100F"
        sky(A, [(0, "#20343A"), (.55, "#7FA09A"), (.7, "#D8D2B0")])
        A.add(clouds(A, 0, 420, "#2A3E44", 71, (.003, .009), 1.8, .5, .9))
        A.add(glow(A, 600, -20, 520, "#FFF6D8", 1) + rays(A, 600, -40, "#FFF6D8", .5, 16, (62, 118), 1100, 6))
        A.add(f'<g transform="translate(600 170) scale(.8)"><path d="M0 0 C-40 -50 -110 -60 -150 -30 C-100 -20 -50 -5 -20 12 Z M0 0 C40 -50 110 -60 150 -30 C100 -20 50 -5 20 12 Z" fill="#FFFFFF"/><ellipse cx="0" cy="18" rx="22" ry="34" fill="#FFFFFF"/><circle cx="0" cy="52" r="14" fill="#FFFFFF"/></g>')
        hills(A, 520, "#7FA09A", "#1E3A34", 2, 31, (80, 40))
        water(A, 560, "#86A6A0", "#0A1A1C", "#FFF6D8", 600, 9)
        A.add(sil(A, "jesus", 560, 760, 420, "spread", 1, (0, -1), lit, amb, nimbus=orth))
        A.add(sil(A, "john_baptist", 790, 770, 400, "awe", -1, (-.3, -1), lit, amb))
        A.add(f'<rect y="660" width="{W}" height="160" fill="{A.lin([(0, "#3E5E5A", .9), (1, "#06100F", 1)])}"/>')
        A.add('<path d="M420 668 q120 -8 260 0 M640 682 q120 -8 240 0" stroke="#FFF6D8" stroke-width="2" fill="none" opacity=".7"/>')
    elif n == 3:
        lit, amb = "#FFE6B8", "#06100F"
        sky(A, [(0, "#4C6E7A"), (.5, "#D9B08A"), (.6, "#F6D2A0")])
        A.add(clouds(A, 0, 380, "#FFE2C0", 81, (.002, .012), 1.6, .65, .7))
        A.add(glow(A, 200, 440, 360, "#FFF0C8", .9))
        hills(A, 450, "#C9A890", "#33504C", 2, 41, (50, 30))
        water(A, 454, "#9AA8A0", "#10262A", "#FFF0C8", 200, 3)
        b, f = boat(A, 780, 590, 1.0, dark=amb, lit=lit, sail="none", light=(-1, -.3))
        figs = sil(A, "peter", 720, 590, 280, "cast", 1, (-1, -.3), lit, amb, scale_w=1.1) + sil(A, "andrew", 850, 592, 266, "cast", -1, (-1, -.3), lit, amb)
        A.add(reflection(A, b + figs + f, 620, .25))
        A.add(b + figs + f)
        A.add("".join(f'<path d="M{900+i*24} 470 Q{915+i*24} 560 {905+i*22} 640" stroke="#E8D6B0" stroke-width="1.2" fill="none" opacity=".7"/>' for i in range(10)))
        A.add("".join(f'<path d="M900 {470+j*30} Q1010 {482+j*30} 1120 {470+j*28}" stroke="#E8D6B0" stroke-width="1.2" fill="none" opacity=".7"/>' for j in range(6)))
        A.add(f'<path d="{smooth([(-20, 680), (260, 650), (480, 700), (540, 830), (-20, 830)], True, .7)}" fill="{amb}"/>')
        A.add(sil(A, "jesus", 260, 760, 400, "beckon", 1, (-1, -.3), lit, amb, nimbus=orth))
    elif n == 4:
        lit, amb = "#FFC873", "#070406"
        sky(A, [(0, "#0E1226"), (.5, "#4A2C4A"), (.78, "#C26E4E")])
        A.add(stars(A, 80, 2, 260, "#E8E4DA", 1.4))
        rnd = random.Random(4)
        x = -20
        while x < W:
            w, h = rnd.uniform(110, 180), rnd.uniform(90, 160)
            A.add(f'<rect x="{x:.0f}" y="{600-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#120E14"/><rect x="{x-4:.0f}" y="{590-h:.0f}" width="{w+8:.0f}" height="12" fill="#0A080C"/>')
            for k in range(rnd.randint(1, 2)):
                wx = x + w * (.25 + .38 * k)
                A.add(glow(A, wx + 8, 600 - h * .6 + 12, 34, "#FFB54A", .6) + f'<rect x="{wx:.0f}" y="{600-h*.62:.0f}" width="16" height="22" rx="7" fill="#FFC873"/>')
            x += w + rnd.uniform(0, 14)
        A.add(f'<rect y="596" width="{W}" height="230" fill="{amb}"/>' + glow(A, 600, 610, 420, "#FFB54A", .45))
        A.add(sil(A, "villager5", 720, 790, 300, "kneelpray", -1, (-1, -.4), lit, amb, kneel=True))
        A.add(sil(A, "jesus", 560, 800, 420, "bless", 1, (-1, -.4), lit, amb, nimbus=orth))
        for cid, x, h in (("villager1", 880, 330), ("villager4", 980, 320), ("villager3", 1080, 330), ("peter", 360, 350), ("villager2", 230, 320), ("villager6", 130, 240)):
            A.add(sil(A, cid, x, 790, h, "stand", -1 if x > 600 else 1, (-1 if x > 600 else 1, -.4), lit, amb))
    elif n == 5:
        lit, amb = "#FFF2CE", "#0A0806"
        sky(A, [(0, "#5E5040"), (.55, "#E2C08A"), (.68, "#FFE6B0")])
        A.add(clouds(A, 0, 400, "#FFF0D0", 91, (.002, .012), 1.6, .6, .6))
        A.add(glow(A, 620, 420, 480, "#FFF6E0", 1) + rays(A, 620, 420, "#FFF6E0", .3, 16, (-200, 20), 1200, 2))
        hills(A, 520, "#E2C08A", "#4A3826", 2, 51, (70, 40))
        A.add(f'<rect y="600" width="{W}" height="230" fill="{amb}"/>')
        A.add(sil(A, "jesus", 520, 820, 520, "touch", 1, (1, -.4), lit, amb, nimbus=orth))
        A.add(sil(A, "leper", 760, 820, 420, "kneelpray", -1, (1, -.4), lit, amb, kneel=True))
    elif n == 6:
        lit, amb = "#FFD78A", "#0A0806"
        A.add(f'<rect width="{W}" height="{H}" fill="#120D0A"/>' + glow(A, 600, 560, 620, "#FFC66A", .35))
        A.add(f'<rect x="430" y="0" width="340" height="290" fill="{A.lin([(0, "#AFD8E6"), (1, "#FFF0C8")])}"/>')
        A.add(rays(A, 600, -40, "#FFF0C8", .4, 12, (70, 110), 1000, 3))
        A.add(f'<rect x="0" y="282" width="1200" height="34" fill="#1E140C"/><rect x="430" y="282" width="340" height="34" fill="#E8D8B0" opacity=".5"/>')
        for x, cid in ((470, "villager1"), (560, "villager3"), (650, "villager5"), (730, "james")):
            A.add(sil(A, cid, x, 290, 150, "lift", 1, (0, -1), "#FFF0C8", amb))
        A.add('<path d="M470 290 L520 520 M730 290 L680 520" stroke="#C8B48A" stroke-width="3"/>')
        A.add(f'<rect x="500" y="508" width="200" height="22" rx="6" fill="#2A1C12"/>')
        A.add(sil(A, "paralytic", 525, 512, 190, "stand", -1, (0, -1), lit, amb, rot=90))
        A.add(sil(A, "jesus", 600, 900, 560, "bless", 1, (0, -1), lit, amb, nimbus=orth))
        for cid, x in (("scribe", 220), ("pharisee", 330), ("villager4", 880), ("peter", 990)):
            A.add(sil(A, cid, x, 860, 500, "stand", 1 if x < 600 else -1, (0, -1), lit, amb))
    elif n == 7:
        lit, amb = "#FFC66A", "#080406"
        A.add(f'<rect width="{W}" height="{H}" fill="#0C0809"/>' + glow(A, 600, 470, 600, "#FFB54A", .55))
        for lx in (260, 600, 940):
            A.add(f'<path d="M{lx} 0 V350" stroke="#3A2A1A" stroke-width="2"/>' + glow(A, lx, 360, 110, "#FFC66A", .8) + f'<ellipse cx="{lx}" cy="362" rx="14" ry="8" fill="#FFE2A0"/>')
        for cid, x, po in (("villager1", 210, "stand"), ("matthew", 370, "cup"), ("jesus", 600, "bless"), ("villager3", 830, "cup"), ("peter", 990, "stand")):
            A.add(sil(A, cid, x, 760, 380, po, 1 if x < 600 else -1, (0, -1), lit, amb, nimbus=(orth and cid == "jesus")))
        A.add(f'<rect x="60" y="600" width="1080" height="40" rx="6" fill="#3A2010"/><path d="M70 602 H1130" stroke="{lit}" stroke-width="2" opacity=".6"/><rect x="60" y="636" width="1080" height="200" fill="#120806"/>')
        for x in (220, 420, 640, 860, 1020):
            A.add(f'<ellipse cx="{x}" cy="598" rx="44" ry="10" fill="#C8A878"/><circle cx="{x-10}" cy="590" r="9" fill="#7A2A20"/><circle cx="{x+12}" cy="592" r="8" fill="#4A6A2A"/>')
        A.add(sil(A, "pharisee", 1140, 600, 280, "hips", -1, (-1, -.3), "#8AA0A8", amb))
    elif n == 8:
        lit, amb = "#FFE6A8", "#100A04"
        sky(A, [(0, "#5E8494"), (.55, "#F0D49A"), (.62, "#FFE8B0")])
        A.add(clouds(A, 0, 360, "#FFF4D8", 95, (.002, .012), 1.6, .6, .7))
        A.add(glow(A, 1000, 230, 360, "#FFF2CC", .9))
        hills(A, 440, "#C8C08A", "#6A6234", 2, 61, (50, 26))
        A.add(f'<rect y="440" width="{W}" height="400" fill="{A.lin([(0, "#D6A64A"), (1, "#3A2408")])}"/>')
        rnd = random.Random(2)
        A.add("".join(f'<path d="M{(xx:=rnd.uniform(-20, W+20)):.0f} {(yy:=rnd.uniform(450, 620)):.0f} q2 -20 {rnd.uniform(-6, 6):.0f} -{20+(yy-450)*.3:.0f}" stroke="{mix("#7A5418", "#F2D07A", rnd.random())}" stroke-width="{1+(yy-450)/120:.1f}" fill="none"/>' for _ in range(400)))
        for cid, x, po in (("john", 300, "pluck"), ("peter", 420, "cup"), ("andrew", 530, "pluck")):
            A.add(sil(A, cid, x, 720, 340, po, 1, (1, -.4), lit, amb))
        A.add(sil(A, "jesus", 690, 740, 400, "bless", -1, (1, -.4), lit, amb, nimbus=orth))
        A.add(sil(A, "pharisee", 920, 740, 390, "point", -1, (1, -.4), lit, amb))
        A.add(sil(A, "scribe", 1050, 745, 380, "hips", -1, (1, -.4), lit, amb))
        A.add("".join(f'<path d="M{(xx:=rnd.uniform(-20, W+20)):.0f} {(yy:=rnd.uniform(680, 830)):.0f} q4 -50 {rnd.uniform(-14, 14):.0f} -{60+(yy-680)*.6:.0f}" stroke="{mix("#3A2408", "#C8963A", rnd.random()*.6)}" stroke-width="{2+(yy-680)/50:.1f}" fill="none"/>' for _ in range(160)))
    finish(A, .16, .5)
    return A


def sheet(orth=True):
    from render_art import ORDER
    A = Art(1800, 1000)
    lit, amb = "#FFE2B0", "#120A08"
    A.add(f'<rect width="1800" height="1000" fill="{A.lin([(0, "#22323A"), (.6, "#B07A52"), (1, "#F0C080")])}"/>')
    A.add(glow(A, 900, 1000, 1000, "#FFE6B0", .8))
    for i, cid in enumerate(ORDER):
        col, row = i % 6, i // 6
        x, y = 150 + col * 300, 460 + row * 490
        A.add(f'<ellipse cx="{x}" cy="{y+2}" rx="110" ry="10" fill="#000" opacity=".25"/>')
        A.add(sil(A, cid, x, y, 400 if cid != "child" else 300, "stand", 1 if col % 2 == 0 else -1, (1 if col % 2 == 0 else -1, -.3), lit, amb, nimbus=(orth and cid == "jesus")))
    A.add(grain(A, .14))
    return A


def hero(orth=True):
    """Wide key art for the library: dawn on the lake, the boat setting out."""
    A = Art(1800, 900)
    A.w, A.h = 1800, 900
    lit, amb = "#FFE4B0", "#081014"
    A.add(f'<rect width="1800" height="900" fill="{A.lin([(0, "#0C1A24"), (.42, "#3A5462"), (.62, "#D49A6A"), (.7, "#FFD9A0")])}"/>')
    A.add(clouds(A, 60, 480, "#FFCB98", 7, (.0012, .008), 1.7, .62, .8))
    A.add(glow(A, 1250, 560, 700, "#FFE8B8", .95))
    A.add(f'<circle cx="1250" cy="560" r="44" fill="#FFF6DE"/>')
    for i, (col, y, amp, seed) in enumerate((("#B88A7A", 560, 90, 3), ("#6A5258", 575, 60, 5), ("#2E2A34", 590, 30, 9))):
        A.add(f'<path d="{ridge(y, amp, seed, 9, 1800, 900)}" fill="{col}"/>')
    A.add(f'<rect y="592" width="1800" height="320" fill="{A.lin([(0, "#E0A878"), (.4, "#4A3A40"), (1, "#060A0E")])}"/>')
    rnd = random.Random(5)
    for i in range(70):
        y = 598 + i * 4.4
        w = rnd.uniform(30, 260) * (1 - i / 90)
        A.add(f'<path d="M{1250 - w/2 + rnd.uniform(-30-i*3, 30+i*3):.0f} {y:.0f} h{w:.0f}" stroke="#FFF0C8" stroke-width="{rnd.uniform(1, 2.4):.1f}" opacity="{(1-i/75)*.8:.2f}"/>')
    b, f = boat(A, 1180, 700, .95, dark=amb, lit=lit, sail="up", sailcol="#A08C6C", light=(1, -.2))
    figs = (sil(A, "peter", 1010, 692, 230, "row", 1, (1, -.2), lit, amb, sit=True) + sil(A, "john", 1090, 692, 214, "stand", 1, (1, -.2), lit, amb, sit=True) +
            sil(A, "jesus", 1370, 690, 250, "point", 1, (1, -.2), lit, amb, nimbus=orth))
    A.add(reflection(A, b + figs + f, 724, .28, 3))
    A.add(b + figs + f)
    A.add(f'<path d="M0 820 Q300 790 520 812 T900 830 L900 900 L0 900Z" fill="{amb}"/>' + reeds(120, 840, 1.2, amb, 18, 7))
    A.add(vignette(A, .5))
    A.add(grain(A, .14))
    return A
