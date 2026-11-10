"""Vector illustration engine for 'Mark in Pictures'.

Two looks, one skeleton:
  * KIDS   – bright cartoon: big heads, clean ink outline, two-tone cel shading.
  * NOVEL  – graphic novel: real proportions, three-tone chiaroscuro with rim
             light, painterly skies (SVG turbulence), grain and vignette.

Shading trick used everywhere: a shape is clipped to itself and re-filled with
copies shifted along the light direction, which leaves a crisp lit rim on the
side facing the light and a shadow on the far side.

Every figure is built in local coordinates facing right with the feet at
(0, 0); facing=-1 mirrors it. Text is never drawn: speech bubbles are a
separate layer in the reader.
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARS = {c["id"]: c for c in json.loads((ROOT / "data/characters.json").read_text())["characters"]}
W, H = 1200, 800


# ------------------------------------------------------------------ colour
def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in c)


def mix(a, b, t):
    A, B = _rgb(a), _rgb(b)
    return _hex([A[i] + (B[i] - A[i]) * t for i in range(3)])


def shade(a, f):
    return _hex([v * f for v in _rgb(a)])


# ------------------------------------------------------------------ geometry
def smooth(pts, closed=True, k=1.0):
    """Catmull-Rom spline through points -> SVG path."""
    n = len(pts)
    if n < 3:
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if closed else "")


def poly(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def circ(cx, cy, r):
    return f"M{cx-r:.1f} {cy:.1f} a{r:.1f} {r:.1f} 0 1 0 {2*r:.1f} 0 a{r:.1f} {r:.1f} 0 1 0 {-2*r:.1f} 0 Z"


def ell(cx, cy, rx, ry):
    return f"M{cx-rx:.1f} {cy:.1f} a{rx:.1f} {ry:.1f} 0 1 0 {2*rx:.1f} 0 a{rx:.1f} {ry:.1f} 0 1 0 {-2*rx:.1f} 0 Z"


def scale_pts(pts, sx, sy=None, ox=0, oy=0):
    sy = sx if sy is None else sy
    return [(ox + x * sx, oy + y * sy) for x, y in pts]


def limb(p, ang1, len1, ang2, len2, w0, w1, w2):
    """Two-segment tapered limb from p; angles in degrees, 0 = down, + = toward +x."""
    a1, a2 = math.radians(ang1), math.radians(ang2)
    e = (p[0] + math.sin(a1) * len1, p[1] + math.cos(a1) * len1)
    h = (e[0] + math.sin(a2) * len2, e[1] + math.cos(a2) * len2)

    def side(pt, a, w, s):
        return (pt[0] + math.cos(a) * w * s, pt[1] - math.sin(a) * w * s)
    am = (a1 + a2) / 2
    left = [side(p, a1, w0, 1), side(e, am, w1, 1), side(h, a2, w2, 1)]
    right = [side(h, a2, w2, -1), side(e, am, w1, -1), side(p, a1, w0, -1)]
    return smooth(left + right, True, .6), e, h


# ------------------------------------------------------------------ canvas
class Art:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.defs, self.body, self.n = [], [], 0

    def id(self, p="i"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, s):
        self.body.append(s)
        return s

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1):
        i = self.id("g")
        s = ""
        for st in stops:
            op = f' stop-opacity="{st[2]}"' if len(st) > 2 else ""
            s += f'<stop offset="{st[0]}" stop-color="{st[1]}"{op}/>'

        self.defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
        return f"url(#{i})"

    def rad(self, stops, cx=.5, cy=.5, r=.5, user=False):
        i = self.id("r")
        s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        units = ' gradientUnits="userSpaceOnUse"' if user else ""
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"{units}>{s}</radialGradient>')
        return f"url(#{i})"

    def filt(self, inner, extra='x="-20%" y="-20%" width="140%" height="140%"'):
        i = self.id("f")
        self.defs.append(f'<filter id="{i}" {extra} color-interpolation-filters="sRGB">{inner}</filter>')
        return f"url(#{i})"

    def shaded(self, d, layers, stroke=None, sw=0, opacity=None):
        """Fill path d with layers [(colour, dx, dy), ...] clipped to d."""
        c, pid = self.id("c"), self.id("d")
        self.defs.append(f'<path id="{pid}" d="{d}"/><clipPath id="{c}"><use href="#{pid}"/></clipPath>')
        inner = "".join(f'<use href="#{pid}" fill="{col}"' + (f' transform="translate({dx:.1f} {dy:.1f})"' if dx or dy else "") + "/>" for col, dx, dy in layers)
        op = f' opacity="{opacity}"' if opacity is not None else ""
        out = f'<g clip-path="url(#{c})"{op}>{inner}</g>'
        if stroke:
            out += f'<use href="#{pid}" fill="none" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="round" stroke-linecap="round"/>'
        return out

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" preserveAspectRatio="xMidYMid slice">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')


# ------------------------------------------------------------------ shared atmosphere
def clouds(A, y0, y1, col, seed=1, freq=(0.0025, 0.009), density=1.6, cut=.55, opacity=1, octaves=5):
    """Painterly cloud field from fractal noise, faded in a vertical band."""
    r, g, b = [v / 255 for v in _rgb(col)]
    f = A.filt(f'<feTurbulence type="fractalNoise" baseFrequency="{freq[0]} {freq[1]}" numOctaves="{octaves}" seed="{seed}" result="n"/>'
               f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 {r:.3f}  0 0 0 0 {g:.3f}  0 0 0 0 {b:.3f}  {density} 0 0 0 {-cut}"/>',
               'x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse"')
    m = A.id("m")
    fade = A.lin([(0, "#fff", 0), (.25, "#fff", 1), (.75, "#fff", 1), (1, "#fff", 0)])
    A.defs.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="{y0}" width="{A.w}" height="{y1-y0}"><rect x="0" y="{y0}" width="{A.w}" height="{y1-y0}" fill="{fade}"/></mask>')
    return f'<g mask="url(#{m})" opacity="{opacity}"><rect x="0" y="{y0}" width="{A.w}" height="{y1-y0}" filter="{f}"/></g>'


def grain(A, amount=.18, freq=.85):
    f = A.filt(f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" stitchTiles="stitch"/>'
               f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {amount} 0"/>',
               'x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse"')
    return f'<rect width="{A.w}" height="{A.h}" filter="{f}"/>'


def paper(A, amount=.10):
    f = A.filt(f'<feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="3" seed="9"/>'
               f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .97  0 0 0 0 .9  0 0 0 {amount} 0"/>',
               'x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse"')
    return f'<rect width="{A.w}" height="{A.h}" filter="{f}" style="mix-blend-mode:soft-light"/>'


def vignette(A, strength=.55, col="#000"):
    return f'<rect width="{A.w}" height="{A.h}" fill="{A.rad([(0, col, 0), (.6, col, 0), (1, col, strength)], .5, .5, .72)}"/>'


def glow(A, cx, cy, r, col, a=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{A.rad([(0, col, a), (.35, col, a*.45), (1, col, 0)])}"/>'


def rays(A, cx, cy, col, a=.16, n=14, spread=(-170, -10), length=1600, seed=2):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        ang = math.radians(spread[0] + (spread[1] - spread[0]) * (i + rnd.random() * .6) / n)
        w = math.radians(rnd.uniform(1.2, 3.5))
        p1 = (cx + math.cos(ang - w) * length, cy + math.sin(ang - w) * length)
        p2 = (cx + math.cos(ang + w) * length, cy + math.sin(ang + w) * length)
        out.append(f'<path d="M{cx} {cy} L{p1[0]:.0f} {p1[1]:.0f} L{p2[0]:.0f} {p2[1]:.0f} Z" fill="{col}" fill-opacity="{a*rnd.uniform(.5,1):.2f}"/>')
    f = A.filt('<feGaussianBlur stdDeviation="6"/>')
    return f'<g filter="{f}">{"".join(out)}</g>'


def rain(A, n, seed, ang=-18, col="#CFE2E6", op=.4, lmin=40, lmax=90, wmax=2.2):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, L = rnd.uniform(-150, A.w + 150), rnd.uniform(-80, A.h), rnd.uniform(lmin, lmax)
        dx = math.tan(math.radians(ang)) * L
        out.append(f'<path d="M{x:.0f} {y:.0f} l{dx:.0f} {L:.0f}" stroke="{col}" stroke-width="{rnd.uniform(.8, wmax):.1f}" stroke-opacity="{op*rnd.uniform(.4,1):.2f}" stroke-linecap="round"/>')
    return "".join(out)


def stars(A, n, seed, ymax, col="#FFF6D8", rmax=1.8, twinkle=0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y, r = rnd.uniform(0, A.w), rnd.uniform(0, ymax) ** 1.0, rnd.uniform(.5, rmax)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{col}" fill-opacity="{rnd.uniform(.35,1):.2f}"/>')
        if twinkle and i % max(1, n // twinkle) == 0:
            s = r * 5
            out.append(f'<path d="M{x:.0f} {y-s:.0f} Q{x:.0f} {y:.0f} {x+s:.0f} {y:.0f} Q{x:.0f} {y:.0f} {x:.0f} {y+s:.0f} Q{x:.0f} {y:.0f} {x-s:.0f} {y:.0f} Q{x:.0f} {y:.0f} {x:.0f} {y-s:.0f} Z" fill="{col}"/>')
    return "".join(out)


def ridge(y, amp, seed, n=9, w=W, h=H, rough=.5):
    rnd = random.Random(seed)
    pts = [(-20, h + 20), (-20, y)]
    for i in range(n + 1):
        pts.append((i * w / n, y - rnd.uniform(0, amp) - (amp * .4 if i % 3 == 1 else 0) * rough))
    pts += [(w + 20, y), (w + 20, h + 20)]
    return smooth(pts[1:-1], False, .9) + f" L{w+20} {h+20} L-20 {h+20} Z"


def waves_path(y, amp, n, seed, w=W, h=H, sharp=.0, phase=0):
    rnd = random.Random(seed)
    step = w / n
    d = f"M-40 {h+40} L-40 {y}"
    x = -40 + phase
    while x < w + 40:
        a = amp * (.65 + rnd.random() * .7)
        s = step * (.8 + rnd.random() * .4)
        d += (f" C{x+s*.25:.0f} {y-a*(1+sharp):.0f} {x+s*.45:.0f} {y-a:.0f} {x+s*.6:.0f} {y-a*.35:.0f}"
              f" S{x+s*.85:.0f} {y+a*.25:.0f} {x+s:.0f} {y:.0f}")
        x += s
    return d + f" L{w+40} {h+40} Z"


def wobble(A, scale=4, freq=.02, seed=3):
    return A.filt(f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="{seed}" result="t"/>'
                  f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" xChannelSelector="R" yChannelSelector="G"/>')


# ================================================================== FIGURES
POSES = {  # (far arm upper, far fore, near upper, near fore) degrees; 0 = hanging, + = forward
    "stand": (-8, -4, 10, 6),
    "point": (-8, -4, 82, 92),
    "raise": (-14, -8, 150, 172),
    "rebuke": (-12, -20, 128, 150),
    "reach": (-8, -4, 62, 78),
    "scared": (-150, -175, 150, 175),
    "awe": (-18, -165, 22, 170),
    "row": (35, 85, 50, 95),
    "bail": (60, 120, 30, 110),
    "cling": (130, 165, 110, 150),
    "beckon": (-8, -4, 55, 150),
    "bless": (-8, -4, 40, 140),
    "carry": (150, 185, 150, 185),
    "kneelpray": (30, 140, 40, 150),
    "touch": (-8, -4, 70, 70),
    "cast": (95, 120, 75, 100),
    "hips": (-30, 40, 30, -40),
    "cup": (30, 120, 45, 130),
    "pluck": (-8, -4, 120, 60),
    "lift": (-140, -175, 140, 175),
    "spread": (-75, -95, 75, 95),
    "sleep": (25, 70, 30, 80),
}

SKIN_EXTRA = {"leper": "#B98F72"}


def _char(cid):
    if cid in CHARS and CHARS[cid].get("svg"):
        return CHARS[cid]["svg"]
    return EXTRAS[cid]


EXTRAS = {
    "villager1": {"skin": "#B07A50", "hair": "#241A12", "hairStyle": "short", "beard": "short", "beardColor": "#241A12", "tunic": "#8E6C4A", "mantle": "#5C6B48"},
    "villager2": {"skin": "#C08E66", "hair": "#2A1A12", "hairStyle": "scarf", "scarf": "#C9A86A", "beard": "none", "beardColor": "#000", "tunic": "#D9C3A0", "mantle": None},
    "villager3": {"skin": "#A06B45", "hair": "#1A1410", "hairStyle": "curly", "beard": "full", "beardColor": "#1A1410", "tunic": "#6E5A8E", "mantle": None},
    "villager4": {"skin": "#B88660", "hair": "#2B2018", "hairStyle": "scarf", "scarf": "#5E8A8C", "beard": "none", "beardColor": "#000", "tunic": "#E3D2B0", "mantle": "#5E8A8C"},
    "villager5": {"skin": "#9C6A48", "hair": "#6E6A66", "hairStyle": "short", "beard": "long-grey", "beardColor": "#B5B0A8", "tunic": "#A65E3A", "mantle": None},
    "villager6": {"skin": "#C49670", "hair": "#2A1A12", "hairStyle": "braids", "beard": "none", "beardColor": "#000", "tunic": "#7FB0A6", "mantle": None},
    "leper": {"skin": "#B4927A", "hair": "#5A5048", "hairStyle": "wild", "beard": "long", "beardColor": "#5A5048", "tunic": "#9C9586", "mantle": "#7D776A"},
    "leper_healed": {"skin": "#B98A62", "hair": "#4A4038", "hairStyle": "wild", "beard": "long", "beardColor": "#4A4038", "tunic": "#D8CCB4", "mantle": "#8C9A7A"},
    "paralytic": {"skin": "#B48A68", "hair": "#2A1C14", "hairStyle": "short", "beard": "short", "beardColor": "#2A1C14", "tunic": "#D8CCB4", "mantle": None},
    "zebedee": {"skin": "#A06C48", "hair": "#8A8580", "hairStyle": "short", "beard": "long-grey", "beardColor": "#C9C4BC", "tunic": "#5C6E7E", "mantle": None},
    "mother_in_law": {"skin": "#B48662", "hair": "#8A8580", "hairStyle": "scarf", "scarf": "#7A5A8E", "beard": "none", "beardColor": "#000", "tunic": "#E2D2B4", "mantle": "#7A5A8E"},
    "scribe": {"skin": "#B18664", "hair": "#2A2018", "hairStyle": "shawl", "scarf": "#E8EAEE", "beard": "full", "beardColor": "#2A2018", "tunic": "#ECE6DA", "mantle": None},
}
for _k in ("beard",):
    pass


# ------------------------------------------------------------------ head shapes (units of head height, facing right)
PROFILE = [(-0.16, 0.50), (-0.44, 0.16), (-0.44, -0.24), (-0.10, -0.50), (0.26, -0.42), (0.38, -0.18), (0.40, -0.03),
           (0.39, 0.05), (0.50, 0.19), (0.40, 0.235), (0.42, 0.29), (0.385, 0.325), (0.415, 0.365), (0.35, 0.46),
           (0.17, 0.52), (0.08, 0.56)]
FRONT = [(0, -0.5), (0.33, -0.4), (0.39, -0.08), (0.34, 0.24), (0.2, 0.44), (0, 0.5), (-0.2, 0.44), (-0.34, 0.24), (-0.39, -0.08), (-0.33, -0.4)]

HAIR = {
    "wavy-long": [(0.30, -0.40), (0.12, -0.26), (0.03, -0.06), (-0.12, 0.18), (-0.16, 0.6), (-0.08, 1.05), (-0.30, 1.12), (-0.52, 0.95), (-0.56, 0.35), (-0.52, -0.22), (-0.26, -0.54), (0.08, -0.6)],
    "short": [(0.32, -0.36), (0.14, -0.24), (0.04, -0.06), (-0.10, 0.12), (-0.36, 0.30), (-0.49, 0.0), (-0.44, -0.36), (-0.12, -0.58), (0.22, -0.52)],
    "curly": [(0.33, -0.36), (0.14, -0.24), (0.04, -0.06), (-0.10, 0.14), (-0.40, 0.34), (-0.56, 0.02), (-0.50, -0.42), (-0.16, -0.66), (0.24, -0.58)],
    "curly-short": [(0.33, -0.34), (0.14, -0.22), (0.04, -0.06), (-0.10, 0.12), (-0.38, 0.30), (-0.53, 0.0), (-0.47, -0.40), (-0.14, -0.62), (0.24, -0.56)],
    "tied": [(0.32, -0.36), (0.14, -0.24), (0.04, -0.06), (-0.10, 0.12), (-0.36, 0.30), (-0.49, 0.0), (-0.44, -0.36), (-0.12, -0.58), (0.22, -0.52)],
    "wild": [(0.30, -0.42), (0.10, -0.26), (0.0, -0.05), (-0.14, 0.2), (-0.2, 0.7), (-0.05, 1.0), (-0.38, 0.95), (-0.5, 1.15), (-0.66, 0.6), (-0.74, 0.1), (-0.62, -0.4), (-0.40, -0.72), (-0.05, -0.74), (0.25, -0.62)],
    "braids": [(0.32, -0.36), (0.14, -0.24), (0.04, -0.06), (-0.10, 0.12), (-0.36, 0.30), (-0.49, 0.0), (-0.44, -0.36), (-0.12, -0.58), (0.22, -0.52)],
    "scarf": [(0.40, -0.34), (0.26, -0.16), (0.22, 0.24), (0.14, 0.62), (0.30, 1.35), (-0.30, 1.55), (-0.72, 1.3), (-0.64, 0.3), (-0.52, -0.46), (-0.08, -0.68), (0.32, -0.54)],
    "shawl": [(0.42, -0.36), (0.26, -0.16), (0.22, 0.24), (0.14, 0.62), (0.34, 1.45), (-0.30, 1.6), (-0.76, 1.4), (-0.66, 0.3), (-0.54, -0.46), (-0.08, -0.70), (0.34, -0.56)],
}


def beard_pts(kind):
    d = {"short": .06, "full": .14, "full-grey": .14, "long": .42, "long-grey": .34}.get(kind)
    if d is None:
        return None
    return [(-0.08, 0.02), (0.14, 0.2), (0.36, 0.27), (0.44, 0.33), (0.40, 0.40), (0.38, 0.52 + d), (0.18, 0.6 + d), (0.0, 0.52 + d * .6), (-0.12, 0.3)]


# ------------------------------------------------------------------ NOVEL figure
def novel(A, cid, x, y, h, pose="stand", facing=1, light=(1, -.35), lit="#F2D7A6", amb="#0B161B",
          rot=0, nimbus=False, kneel=False, expr="calm", ink="#05090B", scale_w=1.0, eyes_closed=False, mouth_open=False):
    c = _char(cid)
    L = math.hypot(*light)
    lx, ly = light[0] / L * facing, light[1] / L
    hh = h / 6.4
    out = []

    def tones(base, glow_k=.55, a=.12, b=.75):
        w1, w2 = hh * a, hh * b
        return [(mix(base, lit, glow_k), 0, 0), (mix(shade(base, .7), amb, .28), -lx * w1, -ly * w1), (mix(shade(base, .32), amb, .55), -lx * w2, -ly * w2)]

    top = -h
    ys = top + hh * 1.32
    yw = top + hh * 3.3
    if kneel:
        yw = top + hh * 3.0
    sw = hh * .84 * scale_w
    ww = hh * .62 * scale_w
    hw = hh * (.94 if not kneel else 1.45) * scale_w
    lean = hh * .12
    robe = [(-hh * .22, ys - hh * .12), (-sw * .78, ys - hh * .02), (-sw, ys + hh * .3), (-sw * .9, ys + hh * 1.2), (-ww, yw),
            (-ww * 1.12, yw + (0 - yw) * .45), (-hw, -hh * .06), (-hw * .5, hh * .03), (0, -hh * .02), (hw * .5, hh * .04), (hw + lean, -hh * .08),
            (ww * 1.14 + lean * .6, yw + (0 - yw) * .45), (ww + lean * .3, yw), (sw * .95, ys + hh * 1.2), (sw, ys + hh * .3), (sw * .8, ys - hh * .02), (hh * .22, ys - hh * .12)]
    robe_d = smooth(robe, True, .8)
    pose_a = POSES[pose]
    sh_far = (-sw * .78, ys + hh * .22)
    sh_near = (sw * .74, ys + hh * .22)
    ua, fa = hh * 1.45, hh * 1.3
    tun = c["tunic"]
    sleeve = mix(tun, "#000", .08)

    def arm(sp, a1, a2, near):
        d, e, hnd = limb(sp, a1, ua, a2, fa, hh * .26, hh * .23, hh * .25)
        parts = [A.shaded(d, tones(sleeve), ink, h * .004)]
        hd = ell(hnd[0] + math.sin(math.radians(a2)) * hh * .14, hnd[1] + math.cos(math.radians(a2)) * hh * .14, hh * .14, hh * .16)
        parts.append(A.shaded(hd, tones(c["skin"], .5), ink, h * .003))
        return "".join(parts)

    # nimbus behind everything
    hx, hy = 0, top + hh * .5
    if nimbus:
        r = hh * 1.0
        out.append(f'<g class="nimbus"><circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r:.1f}" fill="{A.rad([(0, "#F7DE9A", .55), (.7, "#E8C170", .28), (1, "#E8C170", .05)])}" stroke="#E8C170" stroke-width="{h*.006:.1f}"/>'
                   f'<path d="M{hx-r:.1f} {hy:.1f} H{hx+r:.1f} M{hx:.1f} {hy-r:.1f} V{hy-hh*.3:.1f}" stroke="#E8C170" stroke-width="{h*.006:.1f}" stroke-opacity=".75"/></g>')
    # long hair / scarf behind the body
    hs = c["hairStyle"]
    head_pts = PROFILE
    hp = lambda pts: scale_pts(pts, hh, hh, hx, hy)
    back_hair = hs in ("wavy-long", "wild", "scarf", "shawl")
    hair_col = c.get("scarf") if hs in ("scarf", "shawl") else c["hair"]
    if back_hair:
        out.append(A.shaded(smooth(hp(HAIR[hs])), tones(hair_col, .45), ink, h * .004))
    out.append(arm(sh_far, pose_a[0], pose_a[1], False))
    # body
    out.append(A.shaded(robe_d, tones(tun, .55, .16, 1.1), ink, h * .0045))
    for fx_, k in ((-.45, .9), (.1, 1.0), (.55, .85)):
        out.append(f'<path d="M{ww*fx_:.1f} {yw+hh*.3:.1f} Q{ww*fx_*1.2+hh*.05:.1f} {(yw*.5):.1f} {hw*fx_*1.25:.1f} {-hh*.1:.1f}" stroke="{mix(shade(tun,.25),amb,.5)}" stroke-width="{hh*.05:.1f}" fill="none" stroke-opacity="{.55*k:.2f}" stroke-linecap="round"/>')
    # clavus stripe + belt
    out.append(f'<path d="M{sw*.35:.1f} {ys:.1f} Q{sw*.45:.1f} {(ys+yw)/2:.1f} {hw*.5:.1f} {-hh*.08:.1f}" stroke="{shade(tun,.55)}" stroke-width="{hh*.08:.1f}" fill="none" stroke-opacity=".7"/>')
    belt = smooth([(-ww * 1.02, yw - hh * .08), (0, yw + hh * .05), (ww * 1.02 + lean * .3, yw - hh * .08), (ww * 1.02 + lean * .3, yw + hh * .1), (0, yw + hh * .22), (-ww * 1.02, yw + hh * .1)], True, .5)
    out.append(A.shaded(belt, tones("#5A3A22", .4), ink, h * .003))
    if hs == "helmet":
        arm_d = smooth([(-sw * .9, ys + hh * .1), (sw * .92, ys + hh * .1), (ww * 1.05, yw + hh * .1), (-ww * 1.05, yw + hh * .1)], True, .4)
        out.append(A.shaded(arm_d, tones("#7E8790", .65), ink, h * .004))
        for k in range(1, 4):
            yy = ys + hh * .1 + (yw - ys) * k / 4
            out.append(f'<path d="M{-sw*.85:.1f} {yy:.1f} Q0 {yy+hh*.1:.1f} {sw*.85:.1f} {yy:.1f}" stroke="{ink}" stroke-width="{h*.003:.1f}" fill="none"/>')
    # mantle
    if c.get("mantle"):
        m = [(-sw * .82, ys - hh * .05), (-sw * .2, ys + hh * .2), (sw * .55, ys + hh * 1.6), (ww * 1.2 + lean, yw + hh * 1.2), (hw * .95 + lean, -hh * .5),
             (hw * .55, -hh * .25), (ww * .5, yw + hh * .8), (-sw * .2, ys + hh * 1.5), (-sw * 1.02, ys + hh * 1.2), (-sw * 1.05, ys + hh * .3)]
        out.append(A.shaded(smooth(m, True, .7), tones(c["mantle"], .5), ink, h * .0045))
    # neck + head
    neck = poly([(-hh * .14, hy + hh * .25), (hh * .16, hy + hh * .3), (hh * .2, ys), (-hh * .2, ys)])
    out.append(A.shaded(neck, tones(c["skin"], .4), ink, h * .003))
    if hs == "helmet":
        pass
    head_d = smooth(hp(head_pts), True, .85)
    out.append(A.shaded(head_d, tones(c["skin"], .5, .07, .42), ink, h * .0045))
    # ear
    out.append(A.shaded(ell(hx - hh * .06, hy + hh * .02, hh * .07, hh * .1), tones(c["skin"], .4), ink, h * .0025))
    # eye + brow
    ex, ey = hx + hh * .27, hy - hh * .01
    if eyes_closed:
        out.append(f'<path d="M{ex-hh*.07:.1f} {ey:.1f} Q{ex:.1f} {ey+hh*.045:.1f} {ex+hh*.07:.1f} {ey:.1f}" stroke="{ink}" stroke-width="{hh*.03:.1f}" fill="none" stroke-linecap="round"/>')
    else:
        big = 1.25 if expr in ("fear", "awe") else 1
        out.append(f'<path d="M{ex-hh*.075:.1f} {ey:.1f} Q{ex:.1f} {ey-hh*.06*big:.1f} {ex+hh*.07:.1f} {ey+hh*.005:.1f} Q{ex:.1f} {ey+hh*.04*big:.1f} {ex-hh*.075:.1f} {ey:.1f} Z" fill="#E9E2D2"/>')
        out.append(f'<circle cx="{ex+hh*.025:.1f}" cy="{ey-hh*.003:.1f}" r="{hh*.032*big:.1f}" fill="{ink}"/>')
    by = {"calm": 0, "fear": -.06, "awe": -.08, "anger": .03, "pain": -.03}.get(expr, 0)
    tilt = {"fear": -.05, "awe": -.02, "anger": .05, "pain": -.06}.get(expr, 0)
    out.append(f'<path d="M{ex-hh*.11:.1f} {ey-hh*(.1-by-tilt):.1f} Q{ex:.1f} {ey-hh*(.15-by):.1f} {ex+hh*.1:.1f} {ey-hh*(.1-by+tilt):.1f}" stroke="{shade(c["hair"] if hs != "helmet" else "#2A1A10", .8)}" stroke-width="{hh*.045:.1f}" fill="none" stroke-linecap="round"/>')
    if mouth_open:
        out.append(f'<path d="M{hx+hh*.33:.1f} {hy+hh*.31:.1f} Q{hx+hh*.42:.1f} {hy+hh*.36:.1f} {hx+hh*.37:.1f} {hy+hh*.43:.1f} Q{hx+hh*.3:.1f} {hy+hh*.4:.1f} {hx+hh*.33:.1f} {hy+hh*.31:.1f} Z" fill="#2A0E0A"/>')
    # beard
    bp = beard_pts(c["beard"])
    if bp:
        out.append(A.shaded(smooth(hp(bp), True, .8), tones(c["beardColor"], .4), ink, h * .003))
    elif c["beard"] == "stubble":
        out.append(f'<path d="{smooth(hp([(-0.06,0.08),(0.2,0.24),(0.38,0.32),(0.36,0.48),(0.15,0.55),(-0.05,0.4)]))}" fill="{c["hair"]}" fill-opacity=".35"/>')
    # hair front / headwear
    if hs == "helmet":
        dome = smooth(hp([(0.38, -0.12), (0.30, -0.5), (-0.05, -0.66), (-0.42, -0.48), (-0.52, -0.05), (-0.46, 0.25), (-0.30, 0.22), (-0.20, -0.08), (0.30, -0.1)]))
        out.append(A.shaded(dome, tones("#B08A3E", .65), ink, h * .004))
        crest = smooth(hp([(0.36, -0.55), (0.0, -0.95), (-0.5, -0.78), (-0.6, -0.5), (-0.1, -0.68)]))
        out.append(A.shaded(crest, tones("#8C2F1F", .5), ink, h * .003))
    elif not back_hair or hs in ("wavy-long", "wild"):
        if hs not in ("wavy-long", "wild"):
            out.append(A.shaded(smooth(hp(HAIR.get(hs, HAIR["short"]))), tones(c["hair"], .45), ink, h * .004))
            if hs == "tied":
                out.append(A.shaded(circ(hx - hh * .52, hy - hh * .22, hh * .14), tones(c["hair"], .45), ink, h * .003))
            if hs == "braids":
                out.append(A.shaded(smooth(hp([(-0.4, 0.2), (-0.3, 0.9), (-0.42, 1.4), (-0.55, 1.35), (-0.45, 0.9), (-0.55, 0.25)])), tones(c["hair"], .45), ink, h * .003))
            if hs == "curly-short":
                out.append(f'<path d="M{hx-hh*.2:.1f} {hy-hh*.05:.1f} q{hh*.05:.1f} {hh*.1:.1f} {hh*.12:.1f} {hh*.12:.1f}" stroke="#9A938C" stroke-width="{hh*.06:.1f}" fill="none"/>')
    if hs in ("shawl",):
        out.append(f'<rect x="{hx+hh*.14:.1f}" y="{hy-hh*.5:.1f}" width="{hh*.13:.1f}" height="{hh*.11:.1f}" fill="#1A120C" transform="rotate(-20 {hx+hh*.2:.1f} {hy-hh*.45:.1f})"/>')
    # near arm last
    out.append(arm(sh_near, pose_a[2], pose_a[3], True))
    g = "".join(out)
    tr = f"translate({x:.1f} {y:.1f})" + (f" scale({facing} 1)" if facing != 1 else "")
    if rot:
        tr = f"rotate({rot} {x:.1f} {y:.1f}) " + tr
    return f'<g class="fig fig-{cid}" transform="{tr}">{g}</g>'


def novel_face(A, cid, x, y, hh, facing=1, light=(1, -.3), lit="#F2D7A6", amb="#0B161B", expr="calm", eyes_closed=False, mouth_open=False,
               rot=0, nimbus=False, ink="#05090B", shoulders=True):
    """Big close-up head (hh = head height in px) for dramatic panels."""
    return novel(A, cid, x, y + hh * 7.2 - hh * 6.0, hh * 7.2, "stand", facing, light, lit, amb, rot, nimbus, False, expr, ink,
                 eyes_closed=eyes_closed, mouth_open=mouth_open) if shoulders else ""


# ------------------------------------------------------------------ KIDS figure
KINK = "#2B1E2F"


def kid(A, cid, x, y, s=1.0, pose="stand", expr="smile", rot=0, nimbus=False, facing=1, light=(-1, -.6), kneel=False, blush=True):
    """Chibi figure, feet at (x, y), total height ~200*s."""
    c = _char(cid)
    lx, ly = light
    L = math.hypot(lx, ly)
    lx, ly = lx / L, ly / L
    w = 9 * s
    lw = 3.6 * s

    def cel(base, k=.78):
        return [(shade(mix(base, "#3A2A5A", .18), k), 0, 0), (base, lx * w, ly * w)]

    hr = 41 * s
    hx, hy = 0, -152 * s
    out = []
    if nimbus:
        r = hr * 1.5
        out.append(f'<g class="nimbus"><circle cx="{hx}" cy="{hy:.1f}" r="{r:.1f}" fill="#FFE27A" fill-opacity=".6" stroke="#E7A900" stroke-width="{3*s:.1f}"/>'
                   f'<path d="M{hx-r:.1f} {hy:.1f} H{hx+r:.1f} M{hx} {hy-r:.1f} V{hy-hr*.6:.1f}" stroke="#E7A900" stroke-width="{4.5*s:.1f}" stroke-opacity=".8"/></g>')
    hs = c["hairStyle"]
    hair = c["hair"]
    if hs == "wavy-long":
        out.append(A.shaded(smooth([(-hr*1.05, hy-hr*.2), (-hr*1.22, hy+hr*.8), (-hr*.9, hy+hr*1.45), (hr*.9, hy+hr*1.45), (hr*1.22, hy+hr*.8), (hr*1.05, hy-hr*.2), (0, hy-hr*1.1)]), cel(hair), KINK, lw))
    if hs == "wild":
        pts = []
        for i in range(22):
            a = math.pi * (i / 21) * 1.25 - math.pi * 1.12
            rr = hr * (1.42 if i % 2 else 1.1)
            pts.append((hx + math.cos(a) * rr, hy + math.sin(a) * rr + hr * .25))
        out.append(A.shaded(poly(pts), cel(hair), KINK, lw))
    if hs == "braids":
        for sx in (-1, 1):
            out.append(f'<path d="M{sx*hr*.82:.1f} {hy:.1f} q{sx*hr*.4:.1f} {hr*.9:.1f} {sx*hr*.12:.1f} {hr*1.8:.1f}" stroke="{KINK}" stroke-width="{hr*.5:.1f}" fill="none" stroke-linecap="round"/>'
                       f'<path d="M{sx*hr*.82:.1f} {hy:.1f} q{sx*hr*.4:.1f} {hr*.9:.1f} {sx*hr*.12:.1f} {hr*1.8:.1f}" stroke="{hair}" stroke-width="{hr*.38:.1f}" fill="none" stroke-linecap="round" stroke-dasharray="{hr*.18:.1f} {hr*.05:.1f}"/>')
    if hs in ("scarf", "shawl"):
        out.append(A.shaded(smooth([(-hr*1.25, hy+hr*1.6), (-hr*1.38, hy-hr*.4), (-hr*.8, hy-hr*1.3), (hr*.8, hy-hr*1.3), (hr*1.38, hy-hr*.4), (hr*1.25, hy+hr*1.6)]), cel(c["scarf"]), KINK, lw))
    # arms behind? draw body first
    tun = c["tunic"]
    top_b = -112 * s
    body_pts = [(-28 * s, top_b + 4 * s), (0, top_b - 4 * s), (28 * s, top_b + 4 * s), (38 * s, -60 * s), (47 * s, -14 * s), (0, -6 * s), (-47 * s, -14 * s), (-38 * s, -60 * s)]
    if kneel:
        body_pts = [(-28 * s, top_b + 40 * s), (0, top_b + 32 * s), (28 * s, top_b + 40 * s), (40 * s, -40 * s), (58 * s, -10 * s), (0, -4 * s), (-58 * s, -10 * s), (-40 * s, -40 * s)]
    off = 36 * s if kneel else 0
    hy += off
    out.append(A.shaded(smooth(body_pts, True, .7), cel(tun), KINK, lw))
    # clavi stripes + belt
    for sx in (-1, 1):
        out.append(f'<path d="M{sx*12*s:.1f} {top_b+off+2*s:.1f} L{sx*20*s:.1f} {-12*s:.1f}" stroke="{shade(tun,.68)}" stroke-width="{5*s:.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="M{-35*s:.1f} {-62*s+off*.6:.1f} Q0 {-54*s+off*.6:.1f} {35*s:.1f} {-62*s+off*.6:.1f}" stroke="{KINK}" stroke-width="{11*s:.1f}" fill="none" stroke-linecap="round"/>'
               f'<path d="M{-35*s:.1f} {-62*s+off*.6:.1f} Q0 {-54*s+off*.6:.1f} {35*s:.1f} {-62*s+off*.6:.1f}" stroke="#8A5A33" stroke-width="{6*s:.1f}" fill="none" stroke-linecap="round"/>')
    if c.get("mantle"):
        md = smooth([(-27 * s, top_b + off + 2 * s), (-6 * s, top_b + off + 8 * s), (24 * s, -70 * s), (44 * s, -26 * s), (40 * s, -12 * s), (16 * s, -40 * s), (-30 * s, -78 * s + off * .5)], True, .7)
        out.append(A.shaded(md, cel(c["mantle"]), KINK, lw * .9))
    if hs == "helmet":
        out.append(A.shaded(smooth([(-26 * s, -104 * s), (26 * s, -104 * s), (32 * s, -58 * s), (-32 * s, -58 * s)], True, .3), cel("#A7B0BA"), KINK, lw))
        for k in range(3):
            out.append(f'<path d="M{-27*s:.1f} {-(92-k*12)*s:.1f} Q0 {-(88-k*12)*s:.1f} {27*s:.1f} {-(92-k*12)*s:.1f}" stroke="{KINK}" stroke-width="{2*s:.1f}" fill="none"/>')
    # feet
    if not kneel:
        for sx in (-1, 1):
            out.append(A.shaded(ell(sx * 17 * s, -6 * s, 14 * s, 7.5 * s), cel("#7A4B2A"), KINK, lw * .8))
    # arms
    sk = c["skin"]
    sh = [(-26 * s, -100 * s + off), (26 * s, -100 * s + off)]
    hands = {
        "stand": [(-44, -50), (44, -50)], "point": [(-44, -50), (95, -122)], "raise": [(-50, -60), (58, -205)],
        "rebuke": [(-60, -90), (78, -190)], "scared": [(-64, -168), (64, -168)], "awe": [(-26, -138), (26, -138)],
        "row": [(40, -70), (60, -64)], "reach": [(-44, -50), (98, -88)], "bail": [(52, -76), (66, -96)],
        "cling": [(30, -190), (40, -170)], "beckon": [(-44, -50), (80, -140)], "bless": [(-44, -50), (70, -130)],
        "carry": [(-40, -200), (40, -200)], "kneelpray": [(6, -120), (14, -122)], "touch": [(-44, -50), (100, -100)],
        "cast": [(70, -120), (96, -108)], "hips": [(-40, -66), (40, -66)], "cup": [(-12, -84), (16, -86)],
        "pluck": [(-44, -50), (60, -150)], "lift": [(-64, -190), (64, -190)], "spread": [(-90, -100), (90, -100)],
        "sleep": [(30, -80), (40, -70)],
    }[pose]
    if facing == -1:
        hands = [(-hands[1][0], hands[1][1]), (-hands[0][0], hands[0][1])]
    for (sx_, sy_), (hx_, hy_) in zip(sh, hands):
        hx_, hy_ = hx_ * s, hy_ * s + off
        mx, my = (sx_ + hx_) / 2 + (10 * s if hx_ > sx_ else -10 * s), (sy_ + hy_) / 2 + 8 * s
        dd = f"M{sx_:.1f} {sy_:.1f} Q{mx:.1f} {my:.1f} {hx_:.1f} {hy_:.1f}"
        out.append(f'<path d="{dd}" stroke="{KINK}" stroke-width="{20*s:.1f}" fill="none" stroke-linecap="round"/>'
                   f'<path d="{dd}" stroke="{tun}" stroke-width="{13*s:.1f}" fill="none" stroke-linecap="round"/>'
                   f'<path d="{dd}" stroke="{shade(tun,.8)}" stroke-width="{5*s:.1f}" fill="none" stroke-linecap="round" transform="translate({-lx*3*s:.1f} {-ly*3*s:.1f})" opacity=".6"/>')
        ang = math.atan2(hy_ - sy_, hx_ - sx_)
        ca, sa = math.cos(ang), math.sin(ang)
        R = lambda a_, b_: (hx_ + ca * a_ - sa * b_, hy_ + sa * a_ + ca * b_)
        side = 1 if hx_ >= sx_ else -1
        mit = smooth([R(-4 * s, -8 * s), R(6 * s, -10 * s), R(13 * s, -5 * s), R(14 * s, 4 * s), R(7 * s, 9 * s), R(2 * s, 8 * s * side + 0 * s),
                      R(5 * s, 15 * s * side), R(-1 * s, 15 * s * side), R(-5 * s, 8 * s)], True, .7)
        out.append(A.shaded(mit, cel(sk), KINK, lw * .75))
    if pose == "row":
        out.append(f'<path d="M{20*s*facing:.1f} {-92*s:.1f} L{128*s*facing:.1f} {14*s:.1f}" stroke="{KINK}" stroke-width="{10*s:.1f}" stroke-linecap="round"/><path d="M{20*s*facing:.1f} {-92*s:.1f} L{128*s*facing:.1f} {14*s:.1f}" stroke="#A8743F" stroke-width="{6*s:.1f}" stroke-linecap="round"/>')
    # head
    out.append(A.shaded(circ(hx, hy, hr), cel(sk, .82), KINK, lw))
    fx = facing * hr * .12
    for sx in (-1, 1):
        if sx * facing < 0 or True:
            out.append(A.shaded(circ(hx + sx * hr * .98 - fx * .5, hy + hr * .12, hr * .19), cel(sk, .82), KINK, lw * .7))
    # beard
    bd, bc = c["beard"], c["beardColor"]
    if bd in ("short", "full", "full-grey", "long", "long-grey"):
        dpt = {"short": .55, "full": .72, "full-grey": .75, "long": 1.35, "long-grey": 1.2}[bd]
        d = (f"M{hx-hr*.95:.1f} {hy+hr*.02:.1f} Q{hx-hr*.85:.1f} {hy+hr*(1+dpt):.1f} {hx+fx:.1f} {hy+hr*(1+dpt):.1f} Q{hx+hr*.85:.1f} {hy+hr*(1+dpt):.1f} {hx+hr*.95:.1f} {hy+hr*.02:.1f}"
             f" Q{hx+hr*.55+fx:.1f} {hy+hr*.6:.1f} {hx+fx:.1f} {hy+hr*.52:.1f} Q{hx-hr*.55+fx:.1f} {hy+hr*.6:.1f} {hx-hr*.95:.1f} {hy+hr*.02:.1f} Z")
        out.append(A.shaded(d, cel(bc), KINK, lw * .85))
        if bd == "full-grey":
            out.append(f'<path d="M{hx-hr*.5:.1f} {hy+hr*1.2:.1f} q{hr*.2:.1f} {hr*.2:.1f} {hr*.4:.1f} 0 M{hx+hr*.1:.1f} {hy+hr*1.3:.1f} q{hr*.2:.1f} {hr*.2:.1f} {hr*.4:.1f} 0" stroke="#8A8480" stroke-width="{2.5*s:.1f}" fill="none"/>')
    elif bd == "stubble":
        out.append(f'<path d="M{hx-hr*.86:.1f} {hy+hr*.22:.1f} Q{hx+fx:.1f} {hy+hr*1.3:.1f} {hx+hr*.86:.1f} {hy+hr*.22:.1f} Q{hx+fx:.1f} {hy+hr*.75:.1f} {hx-hr*.86:.1f} {hy+hr*.22:.1f} Z" fill="{bc}" fill-opacity=".3"/>')
    # eyes
    ey = hy - hr * .02
    for sx in (-1, 1):
        ex = hx + sx * hr * .37 + fx
        if expr == "sleep":
            out.append(f'<path d="M{ex-hr*.17:.1f} {ey:.1f} Q{ex:.1f} {ey+hr*.15:.1f} {ex+hr*.17:.1f} {ey:.1f}" stroke="{KINK}" stroke-width="{3.4*s:.1f}" fill="none" stroke-linecap="round"/>')
            continue
        big = 1.22 if expr in ("scared", "awe", "shout") else 1
        rx, ry = hr * .18 * big, hr * .235 * big
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#fff" stroke="{KINK}" stroke-width="{lw*.6:.1f}"/>')
        px = ex + facing * hr * .05
        out.append(f'<circle cx="{px:.1f}" cy="{ey+hr*.03:.1f}" r="{hr*.13:.1f}" fill="#5A3518"/><circle cx="{px:.1f}" cy="{ey+hr*.04:.1f}" r="{hr*.075:.1f}" fill="{KINK}"/>'
                   f'<circle cx="{px+hr*.05:.1f}" cy="{ey-hr*.04:.1f}" r="{hr*.045:.1f}" fill="#fff"/><circle cx="{px-hr*.04:.1f}" cy="{ey+hr*.08:.1f}" r="{hr*.022:.1f}" fill="#fff"/>')
        if expr == "calm":
            out.append(f'<path d="M{ex-rx*1.1:.1f} {ey-ry*.25:.1f} Q{ex:.1f} {ey-ry*.75:.1f} {ex+rx*1.1:.1f} {ey-ry*.25:.1f} L{ex+rx*1.1:.1f} {ey-ry*1.2:.1f} L{ex-rx*1.1:.1f} {ey-ry*1.2:.1f} Z" fill="{sk}"/>'
                       f'<path d="M{ex-rx*1.05:.1f} {ey-ry*.25:.1f} Q{ex:.1f} {ey-ry*.75:.1f} {ex+rx*1.05:.1f} {ey-ry*.25:.1f}" stroke="{KINK}" stroke-width="{lw*.7:.1f}" fill="none" stroke-linecap="round"/>')
    # brows
    bcol = KINK if hs == "helmet" else shade(hair if hs not in ("scarf",) else "#3A2A1E", .9)
    tilt = {"worried": 1, "scared": 1.4, "shout": -1.2, "awe": .2, "sad": 1.2, "angry": -1.5}.get(expr, 0)
    lift = {"scared": .1, "awe": .14, "shout": 0}.get(expr, 0)
    if expr != "sleep":
        for sx in (-1, 1):
            ex = hx + sx * hr * .37 + fx
            y0 = ey - hr * (.38 + lift)
            out.append(f'<path d="M{ex-hr*.2:.1f} {y0+sx*tilt*hr*.06:.1f} Q{ex:.1f} {y0-hr*.08:.1f} {ex+hr*.2:.1f} {y0-sx*tilt*hr*.06:.1f}" stroke="{bcol}" stroke-width="{hr*.1:.1f}" fill="none" stroke-linecap="round"/>')
    # nose + mouth
    nx = hx + fx * 1.3
    out.append(f'<path d="M{nx-hr*.04:.1f} {hy+hr*.2:.1f} q{facing*hr*.08:.1f} {hr*.06:.1f} 0 {hr*.12:.1f}" stroke="{shade(sk,.6)}" stroke-width="{2.6*s:.1f}" fill="none" stroke-linecap="round"/>')
    my = hy + hr * .5
    mx = hx + fx
    if expr in ("smile", "calm"):
        wdt = .3 if expr == "smile" else .2
        fill = "#B83A3A" if expr == "smile" else "none"
        out.append(f'<path d="M{mx-hr*wdt:.1f} {my-hr*.05:.1f} Q{mx:.1f} {my+hr*.24:.1f} {mx+hr*wdt:.1f} {my-hr*.05:.1f}" stroke="{KINK}" stroke-width="{3*s:.1f}" fill="{fill}" stroke-linejoin="round"/>')
        if expr == "smile":
            out.append(f'<path d="M{mx-hr*wdt*.7:.1f} {my:.1f} Q{mx:.1f} {my+hr*.06:.1f} {mx+hr*wdt*.7:.1f} {my:.1f} L{mx+hr*wdt*.6:.1f} {my-hr*.03:.1f} L{mx-hr*wdt*.6:.1f} {my-hr*.03:.1f} Z" fill="#fff"/>')
    elif expr in ("scared", "awe", "shout"):
        r_ = {"scared": .17, "awe": .12, "shout": .22}[expr]
        out.append(f'<ellipse cx="{mx:.1f}" cy="{my+hr*.05:.1f}" rx="{hr*r_:.1f}" ry="{hr*r_*1.3:.1f}" fill="#6E1A1A" stroke="{KINK}" stroke-width="{lw*.6:.1f}"/>'
                   f'<ellipse cx="{mx:.1f}" cy="{my+hr*.05+hr*r_*.7:.1f}" rx="{hr*r_*.55:.1f}" ry="{hr*r_*.4:.1f}" fill="#E06A6A"/>')
    elif expr in ("worried", "sad"):
        out.append(f'<path d="M{mx-hr*.2:.1f} {my+hr*.1:.1f} Q{mx:.1f} {my-hr*.08:.1f} {mx+hr*.2:.1f} {my+hr*.1:.1f}" stroke="{KINK}" stroke-width="{3*s:.1f}" fill="none" stroke-linecap="round"/>')
    elif expr == "angry":
        out.append(f'<path d="M{mx-hr*.2:.1f} {my+hr*.06:.1f} L{mx+hr*.2:.1f} {my+hr*.02:.1f}" stroke="{KINK}" stroke-width="{3*s:.1f}" stroke-linecap="round"/>')
    elif expr == "sleep":
        out.append(f'<ellipse cx="{mx:.1f}" cy="{my+hr*.04:.1f}" rx="{hr*.06:.1f}" ry="{hr*.05:.1f}" fill="{KINK}"/>')
    if blush:
        for sx in (-1, 1):
            out.append(f'<ellipse cx="{hx+sx*hr*.62+fx:.1f}" cy="{hy+hr*.3:.1f}" rx="{hr*.15:.1f}" ry="{hr*.09:.1f}" fill="#FF6F6F" fill-opacity=".38"/>')
    # front hair / headwear
    if hs == "wavy-long":
        d = smooth([(-hr*1.04, hy-hr*.02), (-hr*.95, hy-hr*.8), (-hr*.3, hy-hr*1.14), (hr*.4, hy-hr*1.12), (hr*.98, hy-hr*.75), (hr*1.04, hy-hr*.02), (hr*.55, hy-hr*.62), (hr*.06+fx, hy-hr*.7), (-hr*.5, hy-hr*.58)], True, .8)
        out.append(A.shaded(d, cel(hair), KINK, lw))
        out.append(f'<path d="M{hx-hr*.5:.1f} {hy-hr*.95:.1f} Q{hx-hr*.1:.1f} {hy-hr*1.05:.1f} {hx+hr*.3:.1f} {hy-hr*.95:.1f}" stroke="{mix(hair,"#fff",.35)}" stroke-width="{3*s:.1f}" fill="none" stroke-linecap="round" opacity=".7"/>')
    elif hs in ("short", "tied", "braids"):
        d = smooth([(-hr*1.0, hy-hr*.08), (-hr*.9, hy-hr*.85), (-hr*.2, hy-hr*1.15), (hr*.5, hy-hr*1.1), (hr*1.0, hy-hr*.6), (hr*1.0, hy-hr*.08), (hr*.6, hy-hr*.5), (hr*.1+fx, hy-hr*.62), (-hr*.55, hy-hr*.5)], True, .8)
        out.append(A.shaded(d, cel(hair), KINK, lw))
        out.append(f'<path d="M{hx-hr*.45:.1f} {hy-hr*.9:.1f} Q{hx:.1f} {hy-hr*1.02:.1f} {hx+hr*.35:.1f} {hy-hr*.9:.1f}" stroke="{mix(hair,"#fff",.35)}" stroke-width="{3*s:.1f}" fill="none" stroke-linecap="round" opacity=".6"/>')
        if hs == "tied":
            out.append(A.shaded(circ(hx + hr * .82, hy - hr * .8, hr * .3), cel(hair), KINK, lw))
    elif hs in ("curly-short", "curly"):
        n = 8 if hs == "curly" else 7
        for k in range(n):
            a = math.pi + math.pi * (k / (n - 1))
            rr = hr * (.34 if hs == "curly" else .31)
            cx_, cy_ = hx + math.cos(a) * hr * .84, hy + math.sin(a) * hr * .84
            out.append(A.shaded(circ(cx_, cy_, rr), cel(hair), KINK, lw * .75))
        if hs == "curly-short":
            for sx in (-1, 1):
                out.append(f'<circle cx="{hx+sx*hr*.86:.1f}" cy="{hy-hr*.12:.1f}" r="{hr*.17:.1f}" fill="#A39C95" stroke="{KINK}" stroke-width="{lw*.6:.1f}"/>')
    elif hs == "wild":
        d = (f"M{hx-hr:.1f} {hy-hr*.1:.1f} Q{hx-hr*.6:.1f} {hy-hr*1.28:.1f} {hx:.1f} {hy-hr*1.18:.1f} Q{hx+hr*.6:.1f} {hy-hr*1.28:.1f} {hx+hr:.1f} {hy-hr*.1:.1f}"
             f" L{hx+hr*.62:.1f} {hy-hr*.56:.1f} L{hx+hr*.22:.1f} {hy-hr*.4:.1f} L{hx-hr*.2:.1f} {hy-hr*.62:.1f} L{hx-hr*.6:.1f} {hy-hr*.4:.1f} Z")
        out.append(A.shaded(d, cel(hair), KINK, lw))
    elif hs in ("scarf", "shawl"):
        d = smooth([(-hr*1.06, hy+hr*.25), (-hr*1.12, hy-hr*.6), (-hr*.5, hy-hr*1.28), (hr*.5, hy-hr*1.28), (hr*1.12, hy-hr*.6), (hr*1.06, hy+hr*.25), (hr*.86, hy-hr*.62), (fx, hy-hr*.84), (-hr*.86, hy-hr*.62)], True, .8)
        out.append(A.shaded(d, cel(c["scarf"]), KINK, lw))
        if hs == "shawl":
            for yy in (-.95, -.75):
                out.append(f'<path d="M{hx-hr*.95:.1f} {hy+hr*(yy+.4):.1f} Q{hx:.1f} {hy+hr*(yy-.25):.1f} {hx+hr*.95:.1f} {hy+hr*(yy+.4):.1f}" stroke="#3A6FB0" stroke-width="{4*s:.1f}" fill="none"/>')
            out.append(f'<rect x="{hx-hr*.17+fx:.1f}" y="{hy-hr*.98:.1f}" width="{hr*.34:.1f}" height="{hr*.28:.1f}" rx="{hr*.05:.1f}" fill="{KINK}"/>')
    elif hs == "helmet":
        d = (f"M{hx-hr*1.12:.1f} {hy+hr*.05:.1f} Q{hx-hr*1.12:.1f} {hy-hr*1.28:.1f} {hx:.1f} {hy-hr*1.22:.1f} Q{hx+hr*1.12:.1f} {hy-hr*1.28:.1f} {hx+hr*1.12:.1f} {hy+hr*.05:.1f}"
             f" L{hx+hr*.86:.1f} {hy+hr*.42:.1f} L{hx+hr*.78:.1f} {hy-hr*.42:.1f} L{hx-hr*.78:.1f} {hy-hr*.42:.1f} L{hx-hr*.86:.1f} {hy+hr*.42:.1f} Z")
        out.append(A.shaded(d, cel("#D2A043"), KINK, lw))
        out.append(A.shaded(f"M{hx-hr*1.2:.1f} {hy-hr*1.15:.1f} Q{hx:.1f} {hy-hr*1.95:.1f} {hx+hr*1.2:.1f} {hy-hr*1.15:.1f} Q{hx:.1f} {hy-hr*1.42:.1f} {hx-hr*1.2:.1f} {hy-hr*1.15:.1f} Z", cel("#C8372D"), KINK, lw))
    g = "".join(out)
    tr = f"translate({x:.1f} {y:.1f})"
    if rot:
        tr = f"rotate({rot} {x:.1f} {y-90*s:.1f}) " + tr
    return f'<g class="fig fig-{cid}" transform="{tr}">{g}</g>'


def head_of_novel(x, y, h, rot=0, facing=1):
    hh = h / 6.4
    dx, dy = 0, -h + hh * .5
    if rot:
        a = math.radians(rot)
        dx, dy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (x + dx, y + dy)


def head_of_kid(x, y, s=1.0, rot=0, kneel=False):
    dx, dy = 0, -152 * s + (36 * s if kneel else 0)
    if rot:
        a = math.radians(rot)
        py = -90 * s
        rx, ry = dx, dy - py
        dx, dy = rx * math.cos(a) - ry * math.sin(a), rx * math.sin(a) + ry * math.cos(a) + py
    return (x + dx, y + dy)
