"""Cinematic silhouette figures for the adult (graphic-novel) style.

Faces and bodies are read through their outline, the way film posters and
shadow-theatre show people against a bright sky: a carefully drawn profile,
robes with folds, sleeves that widen at the wrist, hands with a thumb and
fingers. Light comes from one side and leaves a thin bright rim, with a
soft second band; the body is a dark colour tinted by the costume.

Local coordinates: facing right, feet at (0, 0), y up is negative.
"""
import math

from art_engine import _char, mix, shade, smooth, circ, ell, POSES

U = 1 / 7.3  # head height as a fraction of body height


def _pt(c, x, y, u):
    return (c[0] + x * u, c[1] + y * u)


def _rot(v, a):
    ca, sa = math.cos(a), math.sin(a)
    return (v[0] * ca - v[1] * sa, v[0] * sa + v[1] * ca)


# head profile, facing right, in head units around the head centre
PROFILE = [(-0.44, -0.02), (-0.36, -0.36), (-0.06, -0.52), (0.24, -0.44), (0.34, -0.24), (0.36, -0.09), (0.33, -0.02),
           (0.37, 0.04), (0.47, 0.18), (0.38, 0.21), (0.395, 0.27), (0.35, 0.305), (0.385, 0.34), (0.34, 0.44), (0.21, 0.51),
           (0.08, 0.50), (0.06, 0.62), (-0.22, 0.62), (-0.28, 0.42), (-0.4, 0.24)]
PROFILE_OPEN = [(-0.44, -0.02), (-0.36, -0.36), (-0.06, -0.52), (0.24, -0.44), (0.34, -0.24), (0.36, -0.09), (0.33, -0.02),
                (0.37, 0.04), (0.47, 0.18), (0.38, 0.21), (0.395, 0.26), (0.30, 0.30), (0.36, 0.40), (0.34, 0.47), (0.21, 0.54),
                (0.08, 0.52), (0.06, 0.62), (-0.22, 0.62), (-0.28, 0.42), (-0.4, 0.24)]
HAIR = {
    "wavy-long": [(0.28, -0.42), (0.10, -0.30), (0.02, -0.12), (-0.06, 0.16), (-0.12, 0.62), (-0.04, 1.18), (-0.30, 1.26), (-0.50, 1.02), (-0.58, 0.4), (-0.54, -0.22), (-0.3, -0.56), (0.06, -0.62)],
    "short": [(0.30, -0.40), (0.14, -0.32), (0.04, -0.12), (-0.12, 0.08), (-0.40, 0.18), (-0.50, -0.08), (-0.40, -0.44), (-0.08, -0.6), (0.22, -0.54)],
    "curly": [(0.32, -0.40), (0.16, -0.34), (0.05, -0.12), (-0.12, 0.1), (-0.44, 0.24), (-0.58, -0.04), (-0.5, -0.5), (-0.14, -0.7), (0.24, -0.62)],
    "curly-short": [(0.32, -0.38), (0.15, -0.32), (0.05, -0.12), (-0.12, 0.08), (-0.42, 0.2), (-0.55, -0.06), (-0.47, -0.48), (-0.12, -0.66), (0.24, -0.6)],
    "tied": [(0.30, -0.40), (0.14, -0.32), (0.04, -0.12), (-0.12, 0.08), (-0.40, 0.14), (-0.62, 0.0), (-0.72, -0.16), (-0.58, -0.28), (-0.42, -0.44), (-0.08, -0.6), (0.22, -0.54)],
    "wild": [(0.28, -0.44), (0.08, -0.3), (0.0, -0.08), (-0.1, 0.24), (-0.12, 0.8), (0.0, 1.1), (-0.3, 1.0), (-0.42, 1.24), (-0.62, 0.8), (-0.82, 0.5), (-0.7, 0.1), (-0.86, -0.2), (-0.62, -0.46), (-0.6, -0.72), (-0.3, -0.66), (-0.1, -0.82), (0.12, -0.64), (0.3, -0.62)],
    "braids": [(0.30, -0.40), (0.14, -0.32), (0.04, -0.12), (-0.12, 0.08), (-0.26, 0.3), (-0.30, 0.9), (-0.40, 1.4), (-0.54, 1.36), (-0.48, 0.8), (-0.5, -0.08), (-0.40, -0.44), (-0.08, -0.6), (0.22, -0.54)],
    "scarf": [(0.40, -0.36), (0.24, -0.14), (0.20, 0.24), (0.12, 0.66), (0.40, 1.5), (-0.4, 1.7), (-0.82, 1.4), (-0.7, 0.3), (-0.56, -0.48), (-0.1, -0.72), (0.32, -0.58)],
    "shawl": [(0.42, -0.38), (0.25, -0.14), (0.20, 0.24), (0.12, 0.66), (0.46, 1.62), (-0.4, 1.8), (-0.86, 1.5), (-0.72, 0.3), (-0.58, -0.5), (-0.1, -0.74), (0.34, -0.6)],
    "helmet": [(0.36, -0.10), (0.30, -0.50), (-0.04, -0.66), (-0.42, -0.50), (-0.52, -0.06), (-0.46, 0.30), (-0.28, 0.30), (-0.18, -0.06), (0.30, -0.08)],
}


def _beard(kind):
    d = {"short": .06, "full": .16, "full-grey": .16, "long": .5, "long-grey": .4}.get(kind)
    if d is None:
        return None
    return [(-0.12, 0.06), (0.10, 0.20), (0.33, 0.25), (0.40, 0.30), (0.39, 0.37), (0.37, 0.52 + d), (0.24, 0.64 + d), (0.0, 0.6 + d * .7), (-0.16, 0.36)]


def _hand(wrist, ang, u, open_=False):
    """Hand silhouette at the wrist, pointing along ang (radians, 0 = down)."""
    d = (math.sin(ang), math.cos(ang))
    n = (math.cos(ang), -math.sin(ang))
    L = u * (.5 if open_ else .42)
    w = u * .17
    P = lambda a, b: (wrist[0] + d[0] * a + n[0] * b, wrist[1] + d[1] * a + n[1] * b)
    pts = [P(0, -w), P(L * .45, -w * 1.25), P(L * .8, -w * 1.05), P(L, -w * .4), P(L * 1.02, w * .2), P(L * .85, w * .9),
           P(L * .5, w * 1.05), P(L * .62, w * 1.9), P(L * .5, w * 2.1), P(L * .25, w * 1.3), P(0, w)]
    return smooth(pts, True, .6)


def _arm(sh, a1, a2, u, sleeve=1.0):
    r1, r2 = math.radians(a1), math.radians(a2)
    up, fo = u * 1.42, u * 1.28
    el = (sh[0] + math.sin(r1) * up, sh[1] + math.cos(r1) * up)
    wr = (el[0] + math.sin(r2) * fo, el[1] + math.cos(r2) * fo)

    def off(p, a, w):
        return ((p[0] + math.cos(a) * w, p[1] - math.sin(a) * w), (p[0] - math.cos(a) * w, p[1] + math.sin(a) * w))
    w0, w1, w2 = u * .27, u * .2, u * .3 * sleeve
    s0, s1 = off(sh, r1, w0)
    e0, e1 = off(el, (r1 + r2) / 2, w1)
    c0, c1 = off(wr, r2, w2)
    # fabric droops under a raised forearm
    horiz = abs(math.sin(r2))
    mid = ((el[0] + wr[0]) / 2, (el[1] + wr[1]) / 2 + u * (.12 + .42 * horiz))
    lower = [c1, mid, e1] if c1[1] > c0[1] else [c0, mid, e0]
    if c1[1] > c0[1]:
        pts = [s0, e0, c0, (wr[0] + math.sin(r2) * u * .06, wr[1] + math.cos(r2) * u * .06), c1, mid, e1, s1]
    else:
        pts = [s0, e0, mid, c0, (wr[0] + math.sin(r2) * u * .06, wr[1] + math.cos(r2) * u * .06), c1, e1, s1]
    return smooth(pts, True, .5), wr, r2


def sil(A, cid, x, y, h, pose="stand", facing=1, light=(1, -.35), lit="#F2D7A6", amb="#0B161B", rot=0, nimbus=False,
        kneel=False, expr="calm", ink=None, scale_w=1.0, eyes_closed=False, mouth_open=False, face_light=False, sit=False, tint=.88):
    c = _char(cid)
    u = h * U
    Lx, Ly = light
    n = math.hypot(Lx, Ly)
    lx, ly = Lx / n * facing, Ly / n
    top = -h
    if kneel or sit:
        top = -h * (.74 if kneel else .68)
    hc = (0, top + u * .5)
    ys = top + u * 1.45
    yw = top + u * 3.05
    lean = u * (.18 if pose in ("reach", "touch", "beckon", "bail", "row") else .06)
    sw, ww, hw = u * .92 * scale_w, u * .6 * scale_w, u * .98 * scale_w
    parts = []  # (path, tint)

    # long hair / scarf behind
    hs = c.get("hairStyle", "short")
    hair_col = c.get("scarf") if hs in ("scarf", "shawl") else c.get("hair", "#222")
    hp = lambda pts: [_pt(hc, a, b, u) for a, b in pts]
    if hs in ("wavy-long", "wild", "scarf", "shawl", "braids"):
        parts.append((smooth(hp(HAIR[hs]), True, .8), hair_col))

    # far arm
    pa = POSES.get(pose, POSES["stand"])
    sh_far = (-sw * .55 + lean, ys + u * .22)
    sh_near = (sw * .62 + lean, ys + u * .25)
    tun = c.get("tunic", "#777")
    arm_far, wr_f, ra_f = _arm(sh_far, pa[0], pa[1], u)
    parts.append((arm_far, shade(tun, .85)))
    parts.append((_hand(wr_f, ra_f, u, pose in ("raise", "rebuke", "spread", "bless")), c.get("skin", "#a07050")))

    # robe
    if kneel or sit:
        robe = [(-u * .16, ys - u * .2), (-sw, ys + u * .18), (-sw * 1.02, ys + u * .8), (-ww * 1.05, yw), (-ww * 1.25, yw + u * .8),
                (-u * 1.15, -u * .35), (-u * 1.0, 0), (u * .2, u * .02), (u * 1.5, 0), (u * 1.62, -u * .35), (u * 1.4, -u * .7),
                (ww * 1.2 + lean, yw + u * .5), (ww + lean, yw), (sw * .98 + lean, ys + u * .8), (sw + lean, ys + u * .2), (u * .18 + lean, ys - u * .2)]
    else:
        folds = []
        k = 7
        for i in range(k + 1):
            t = i / k
            folds.append((-hw + 2 * hw * t + lean * 1.3, -u * .22 + (u * .07 if i % 2 else 0)))
        robe = ([(-u * .16, ys - u * .2), (-sw, ys + u * .18), (-sw * .98, ys + u * .8), (-ww, yw), (-ww * 1.12, yw + u * 1.1), (-hw * .96, -u * 1.0)]
                + folds +
                [(hw * .98 + lean * 1.3, -u * 1.0), (ww * 1.12 + lean, yw + u * 1.1), (ww + lean, yw), (sw * .98 + lean, ys + u * .8), (sw + lean, ys + u * .2), (u * .18 + lean, ys - u * .2)])
    parts.append((smooth(robe, True, .7), tun))
    # feet / sandals under the hem
    if not (kneel or sit):
        for fx in (-u * .45, u * .5):
            parts.append((smooth([(fx - u * .2, -u * .25), (fx + u * .35, -u * .2), (fx + u * .5, -u * .02), (fx - u * .22, 0)], True, .5), "#3a2416"))
    # mantle: back drape + front fold
    if c.get("mantle"):
        m = c["mantle"]
        back = [(-u * .1, ys - u * .1), (-sw * 1.12, ys + u * .25), (-sw * 1.25, yw), (-hw * 1.1, (-u * 1.4 if not (kneel or sit) else -u * .4)),
                (-hw * .6, (-u * 1.2 if not (kneel or sit) else -u * .3)), (-ww * .6, yw), (-sw * .4, ys + u * .4)]
        parts.append((smooth(back, True, .7), m))
        front = [(sw * .2 + lean, ys + u * .1), (sw * 1.05 + lean, ys + u * .4), (ww * 1.1 + lean, yw + u * .6), (ww * .5 + lean, yw + u * 1.3), (-ww * .3, yw + u * .4)]
        parts.append((smooth(front, True, .7), m))
    if hs == "helmet":
        parts.append((smooth([(-sw * .95, ys + u * .1), (sw * .95 + lean, ys + u * .1), (ww * 1.05 + lean, yw + u * .15), (-ww * 1.05, yw + u * .15)], True, .3), "#6E767E"))
    # head + beard + hair
    head = PROFILE_OPEN if mouth_open else PROFILE
    parts.append((smooth(hp(head), True, .8), c.get("skin", "#a07050")))
    bp = _beard(c.get("beard", "none"))
    if bp:
        parts.append((smooth(hp(bp), True, .8), c.get("beardColor", "#222")))
    if hs not in ("wavy-long", "wild", "scarf", "shawl", "braids"):
        parts.append((smooth(hp(HAIR.get(hs, HAIR["short"])), True, .8), hair_col if hs != "helmet" else "#8A6A2E"))
    elif hs in ("wavy-long", "wild", "braids"):
        parts.append((smooth(hp(HAIR["short"]), True, .8), hair_col))
    if hs == "helmet":
        parts.append((smooth(hp([(0.34, -0.58), (0.0, -1.0), (-0.52, -0.84), (-0.66, -0.52), (-0.1, -0.68)]), True, .8), "#7A2418"))
    if hs == "tied":
        parts.append((circ(*_pt(hc, -0.62, -0.18, u), u * .15), hair_col))
    # near arm
    arm_near, wr_n, ra_n = _arm(sh_near, pa[2], pa[3], u)
    parts.append((arm_near, tun))
    parts.append((_hand(wr_n, ra_n, u, pose in ("raise", "rebuke", "spread", "bless", "touch", "beckon")), c.get("skin", "#a07050")))

    # ---- render: union clip, rim light, tinted darks
    cid_ = A.id("s")
    ids = [A.id("q") for _ in parts]
    A.defs.append("".join(f'<path id="{i}" d="{d}"/>' for i, (d, _) in zip(ids, parts)) + f'<clipPath id="{cid_}">' + "".join(f'<use href="#{i}"/>' for i in ids) + "</clipPath>")
    w1, w2 = u * .022, u * .06
    out = []
    if nimbus:
        r = u * .95
        hx, hy = hc
        out.append(f'<g class="nimbus"><circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r*1.5:.1f}" fill="{A.rad([(0, "#FFE9A8", .55), (.5, "#F2C66A", .18), (1, "#F2C66A", 0)])}"/>'
                   f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r:.1f}" fill="none" stroke="#F2CF7A" stroke-width="{u*.05:.1f}"/>'
                   f'<path d="M{hx-r:.1f} {hy:.1f} H{hx-u*.55:.1f} M{hx+u*.55:.1f} {hy:.1f} H{hx+r:.1f} M{hx:.1f} {hy-r:.1f} V{hy-u*.55:.1f}" stroke="#F2CF7A" stroke-width="{u*.05:.1f}" stroke-opacity=".8"/></g>')
    rim = "".join(f'<use href="#{i}" fill="{lit}"/>' for i in ids)
    mid = "".join(f'<use href="#{i}" fill="{mix(mix(t, amb, .62), lit, .22)}" transform="translate({-lx*w1:.1f} {-ly*w1:.1f})"/>' for i, (d, t) in zip(ids, parts))
    dark = "".join(f'<use href="#{i}" fill="{mix(t, amb, tint)}" transform="translate({-lx*w2:.1f} {-ly*w2:.1f})"/>' for i, (d, t) in zip(ids, parts))
    face = ""
    if face_light:
        # broader light on the face side for close-ups
        hd = smooth(hp(head), True, .8)
        fc = A.id("fc")
        A.defs.append(f'<clipPath id="{fc}"><path d="{hd}"/></clipPath>')
        face = (f'<g clip-path="url(#{fc})"><path d="{hd}" fill="{mix(c.get("skin", "#a07050"), lit, .25)}"/>'
                f'<path d="{hd}" fill="{mix(shade(c.get("skin", "#a07050"), .5), amb, .6)}" transform="translate({-lx*u*.42:.1f} {-ly*u*.3:.1f})"/></g>')
        if bp:
            face += f'<path d="{smooth(hp(bp), True, .8)}" fill="{mix(shade(c.get("beardColor", "#222"), .6), amb, .5)}"/>'
        if hs not in ("wavy-long", "wild", "scarf", "shawl", "braids"):
            face += f'<path d="{smooth(hp(HAIR.get(hs, HAIR["short"])), True, .8)}" fill="{mix(shade(hair_col, .6), amb, .5)}"/>'
        else:
            face += f'<path d="{smooth(hp(HAIR["short"] if hs != "scarf" and hs != "shawl" else HAIR[hs]), True, .8)}" fill="{mix(shade(hair_col, .6), amb, .5)}"/>'
        ex, ey = _pt(hc, .25, -.02, u)
        if eyes_closed:
            face += f'<path d="M{ex-u*.06:.1f} {ey:.1f} q{u*.06:.1f} {u*.04:.1f} {u*.12:.1f} 0" stroke="{amb}" stroke-width="{u*.025:.1f}" fill="none" stroke-linecap="round"/>'
        else:
            face += f'<path d="M{ex-u*.05:.1f} {ey:.1f} q{u*.05:.1f} {-u*.04:.1f} {u*.1:.1f} {u*.01:.1f} q{-u*.05:.1f} {u*.03:.1f} {-u*.1:.1f} {-u*.01:.1f}Z" fill="{amb}"/>'
            face += f'<path d="M{ex-u*.09:.1f} {ey-u*.09:.1f} q{u*.08:.1f} {-u*.04:.1f} {u*.16:.1f} {u*.0:.1f}" stroke="{mix(shade(hair_col, .5), amb, .5)}" stroke-width="{u*.035:.1f}" fill="none" stroke-linecap="round"/>'
    out.append(f'<g clip-path="url(#{cid_})">{rim}{mid}{dark}</g>{face}')
    g = "".join(out)
    tr = f"translate({x:.1f} {y:.1f})" + (" scale(-1 1)" if facing == -1 else "")
    if rot:
        tr = f"rotate({rot} {x:.1f} {y:.1f}) " + tr
    return f'<g class="fig fig-{cid}" transform="{tr}">{g}</g>'


def head_of_sil(x, y, h, rot=0, facing=1, kneel=False, sit=False):
    top = -h * (.74 if kneel else .68 if sit else 1)
    dx, dy = 0, top + h * U * .5
    if rot:
        a = math.radians(rot)
        dx, dy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    return (x + dx, y + dy)
