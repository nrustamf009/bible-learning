"""Scene descriptions for every panel of episodes 1–8 (drawn by tools/scenes.py in both styles).

Camera: wide = establishing shot, medium = people from the knees up, close = faces and hands.
Figures with y > 800 are cropped by the frame (foreground / over-the-shoulder shots).
'ride' places a figure or a prop on raised hands (a stretcher carried by four men).
"""


def F(i, x, y, s=1.0, pose="stand", f=1, e="smile", **kw):
    d = {"id": i, "x": x, "y": y, "s": s, "pose": pose, "f": f, "e": e}
    d.update(kw)
    return d


def E(place, time="day", cam="medium", **kw):
    d = {"place": place, "time": time, "cam": cam}
    d.update(kw)
    return d


def P(k, x=0, y=0, **kw):
    d = {"k": k, "x": x, "y": y}
    d.update(kw)
    return d


V = ("villager1", "villager2", "villager3", "villager4", "villager5", "villager6")


def crowd(xs, y, s, f=1, e="smile", start=0, pose="stand"):
    return [F(V[(start + i) % 6], x, y + (i % 2) * 10, s, pose, f, e) for i, x in enumerate(xs)]


SCENES = {
    "ep01-voice": {
        "p1": {"env": E("wilderness", "dawn", "wide"), "figs": [F("john_baptist", 700, 610, .8, "stand", -1, "calm")]},
        "p2": {"env": E("wilderness", "day", "close"), "figs": [F("john_baptist", 560, 900, 2.3, "cup", 1, "smile")]},
        "p3": {"env": E("road", "day", "wide"), "figs": crowd([420, 500, 580, 660], 600, .9, 1, "smile", 0) + crowd([120, 1080], 900, 2.0, 1, "smile", 3) + [F("john_baptist", 980, 560, .7, "raise", -1, "shout")]},
        "p4": {"env": E("jordan", "day", "medium"), "figs": [F("john_baptist", 760, 700, 1.6, "raise", -1, "shout")] + crowd([110, 300], 900, 2.0, 1, "awe", 1)},
        "p5": {"env": E("jordan", "day", "close"), "figs": [F("john_baptist", 700, 900, 2.0, "bless", -1, "calm"), F("villager5", 460, 900, 1.9, "kneelpray", 1, "calm", kneel=True)]},
        "p6": {"env": E("jordan", "dusk", "medium"), "figs": [F("john_baptist", 360, 900, 2.1, "point", 1, "awe"), F("jesus", 990, 560, .5, "stand", -1, "calm")]},
    },
    "ep02-baptism": {
        "p1": {"env": E("jordan", "day", "wide"), "figs": [F("jesus", 280, 680, 1.2, "stand", 1, "smile"), F("john_baptist", 860, 640, 1.0, "awe", -1, "awe")] + crowd([560, 640, 720], 610, .7, -1, "smile")},
        "p2": {"env": E("jordan", "day", "close"), "figs": [F("jesus", 520, 900, 1.9, "kneelpray", 1, "calm", kneel=True), F("john_baptist", 790, 900, 2.0, "bless", -1, "calm")]},
        "p3": {"env": E("jordan", "day", "medium", light=True, dove=True), "figs": [F("jesus", 600, 880, 1.9, "spread", 1, "calm")]},
        "p4": {"env": E("jordan", "day", "medium", light=True), "figs": [F("jesus", 600, 760, 1.4, "stand", 1, "calm"), F("john_baptist", 840, 770, 1.35, "awe", -1, "awe")] + crowd([90, 250, 1120], 900, 1.9, 1, "awe", 2)},
        "p5": {"env": E("wilderness", "night", "medium"), "figs": [F("jesus", 430, 820, 1.8, "kneelpray", 1, "sad", kneel=True)], "props": [P("shadow", 820, 780, layer="front")]},
        "p6": {"env": E("wilderness", "dawn", "medium"), "figs": [F("jesus", 470, 830, 1.8, "stand", 1, "smile", sit=True)], "props": [P("angel", 800, 820), P("jar", 650, 830, layer="front")]},
    },
    "ep03-fishers": {
        "p1": {"env": E("street", "day", "medium"), "figs": [F("jesus", 600, 780, 1.6, "spread", 1, "smile")] + crowd([150], 920, 2.3, 1, "awe", 0) + crowd([1060], 920, 2.3, -1, "awe", 3) + crowd([330, 880], 760, 1.2, 1, "smile", 1)},
        "p2": {"env": E("shore", "dawn", "medium", poles=False), "figs": [F("peter", 600, 720, 1.5, "cast", 1, "smile"), F("andrew", 780, 722, 1.4, "cast", -1, "smile")], "props": [P("boat", 690, 730, s=1.25, sail="none", layer="front"), P("net", 840, 480, w=260, h=190)]},
        "p3": {"env": E("shore", "dawn", "medium", poles=False), "figs": [F("jesus", 230, 920, 2.4, "beckon", 1, "smile"), F("peter", 740, 690, 1.15, "awe", -1, "awe"), F("andrew", 860, 692, 1.1, "awe", -1, "awe")], "props": [P("boat", 810, 700, s=1.0, sail="none", layer="front")]},
        "p4": {"env": E("shore", "day", "medium"), "figs": [F("peter", 480, 840, 1.8, "beckon", -1, "smile"), F("andrew", 660, 850, 1.7, "stand", -1, "smile")], "props": [P("net", 780, 690, w=300, h=130)]},
        "p5": {"env": E("shore", "day", "medium", poles=False), "figs": [F("james", 650, 730, 1.35, "cup", 1), F("john", 770, 732, 1.3, "cup", -1), F("zebedee", 920, 734, 1.3, "stand", -1, "calm"), F("jesus", 160, 920, 2.2, "beckon", 1, "smile")], "props": [P("boat", 780, 740, s=1.3, sail="up", layer="front")]},
        "p6": {"env": E("shore", "dusk", "wide", poles=False), "figs": [F("jesus", 300, 740, 1.3, "point", -1, "smile"), F("peter", 470, 745, 1.25, "stand", -1), F("andrew", 600, 748, 1.2, "stand", -1), F("james", 720, 745, 1.2, "stand", -1), F("john", 830, 748, 1.15, "stand", -1)]},
    },
    "ep04-capernaum": {
        "p1": {"env": E("synagogue", "day", "medium"), "figs": [F("jesus", 600, 760, 1.6, "bless", 1, "calm"), F("scribe", 900, 770, 1.4, "hips", -1, "worried")] + crowd([170], 930, 2.4, 1, "awe", 0) + crowd([1060], 930, 2.3, -1, "awe", 2)},
        "p2": {"env": E("synagogue", "day", "close"), "figs": [F("jesus", 390, 900, 2.0, "rebuke", 1, "calm"), F("villager3", 830, 900, 1.9, "scared", -1, "scared")], "props": [P("shadow", 850, 560, layer="front")]},
        "p3": {"env": E("synagogue", "day", "medium"), "figs": crowd([330, 480, 720, 870], 760, 1.3, 1, "awe", 1) + crowd([140], 930, 2.3, 1, "awe", 0) + crowd([1070], 930, 2.3, -1, "awe", 4)},
        "p4": {"env": E("house", "day", "medium"), "figs": [F("jesus", 520, 820, 1.75, "touch", 1, "smile"), F("mother_in_law", 780, 830, 1.65, "stand", -1, "smile", sit=True), F("peter", 230, 830, 1.6, "awe", 1, "awe")]},
        "p5": {"env": E("street", "dusk", "medium"), "figs": [F("jesus", 560, 800, 1.6, "bless", 1, "calm"), F("villager5", 760, 810, 1.5, "kneelpray", -1, "sad", kneel=True)] + crowd([130], 930, 2.3, 1, "awe", 1) + crowd([1080], 930, 2.3, -1, "awe", 3)},
        "p6": {"env": E("wilderness", "night", "medium"), "figs": [F("jesus", 420, 820, 1.8, "kneelpray", 1, "calm", kneel=True), F("peter", 930, 760, 1.4, "beckon", -1, "shout")]},
    },
    "ep05-touch": {
        "p1": {"env": E("road", "day", "medium"), "figs": [F("leper", 600, 830, 1.8, "stand", 1, "sad")] + crowd([200, 320], 700, 1.1, -1, "scared", 0) + crowd([880, 1000], 700, 1.1, 1, "scared", 2)},
        "p2": {"env": E("road", "day", "close"), "figs": [F("jesus", 400, 900, 2.1, "stand", 1, "calm"), F("leper", 770, 900, 2.0, "kneelpray", -1, "sad", kneel=True)]},
        "p3": {"env": E("road", "day", "close", light=True), "figs": [F("jesus", 440, 910, 2.2, "touch", 1, "calm"), F("leper", 770, 910, 2.1, "kneelpray", -1, "sad", kneel=True)]},
        "p4": {"env": E("road", "day", "close", light=True), "figs": [F("jesus", 400, 900, 2.0, "bless", 1, "smile"), F("leper_healed", 770, 900, 2.0, "spread", -1, "awe")]},
        "p5": {"env": E("road", "day", "medium"), "figs": [F("jesus", 420, 830, 1.8, "point", 1, "calm"), F("leper_healed", 760, 830, 1.7, "stand", -1, "smile")]},
        "p6": {"env": E("street", "day", "medium"), "figs": [F("leper_healed", 600, 820, 1.7, "lift", 1, "smile")] + crowd([330, 870], 760, 1.2, 1, "awe", 1) + crowd([120], 930, 2.3, 1, "awe", 0) + crowd([1080], 930, 2.3, -1, "awe", 3)},
    },
    "ep06-roof": {
        "p1": {"env": E("house", "day", "medium"), "figs": [F("jesus", 520, 780, 1.6, "spread", 1, "calm"), F("scribe", 230, 790, 1.5, "hips", 1, "worried")] + crowd([760, 900], 770, 1.3, -1, "awe", 0) + crowd([1080], 930, 2.3, -1, "awe", 3)},
        "p2": {"env": E("street", "day", "medium"), "figs": [F("villager1", 330, 820, 1.4, "carry", 1), F("villager3", 460, 825, 1.4, "carry", 1), F("villager5", 740, 820, 1.4, "carry", 1), F("james", 870, 825, 1.4, "point", -1, "shout"),
                                                             F("paralytic", 600, 0, 1.05, "stand", 1, "sad", lie=True, ride=(820, 1.4))], "props": [P("stretcher", 600, 0, w=420, ride=(820, 1.4))]},
        "p3": {"env": E("roof", "day", "medium"), "figs": [F("villager1", 360, 800, 1.5, "reach", 1, "smile", kneel=True), F("villager3", 470, 805, 1.45, "reach", 1, "smile", kneel=True),
                                                           F("villager5", 740, 800, 1.5, "reach", -1, "smile", kneel=True), F("james", 850, 805, 1.45, "reach", -1, "smile", kneel=True)], "props": [P("roofhole", 600, 790)]},
        "p4": {"env": E("house", "day", "medium"), "figs": [F("jesus", 330, 840, 1.9, "spread", 1, "smile"), F("paralytic", 720, 520, 1.15, "stand", -1, "awe", lie=True)], "props": [P("hole", 720, 0), P("ropes", 720, 520), P("mat", 720, 535, layer="front")]},
        "p5": {"env": E("house", "day", "medium"), "figs": [F("jesus", 350, 830, 1.8, "point", 1, "calm"), F("scribe", 760, 840, 1.7, "hips", -1, "angry"), F("pharisee", 950, 845, 1.6, "stand", -1, "worried")]},
        "p6": {"env": E("street", "day", "medium"), "figs": [F("paralytic", 600, 830, 1.7, "carry", 1, "smile"), F("jesus", 250, 790, 1.4, "bless", 1, "smile")] + crowd([860, 980], 780, 1.3, -1, "awe", 1) + crowd([1110], 930, 2.3, -1, "awe", 4),
               "props": [P("stretcher", 600, 0, w=300, ride=(830, 1.7), layer="front")]},
    },
    "ep07-dinner": {
        "p1": {"env": E("shore", "day", "medium"), "figs": [F("matthew", 600, 800, 1.6, "cup", 1, "worried"), F("roman_soldier", 900, 805, 1.55, "stand", -1, "calm")] + crowd([170, 300], 830, 1.6, 1, "angry", 0), "props": [P("booth", 600, 840, layer="front")]},
        "p2": {"env": E("shore", "day", "close"), "figs": [F("jesus", 290, 930, 2.4, "beckon", 1, "smile"), F("matthew", 780, 880, 1.9, "awe", -1, "awe")], "props": [P("booth", 860, 900, layer="front")]},
        "p3": {"env": E("feast", "night", "medium"), "figs": [F("villager1", 200, 730, 1.5, "cup", 1), F("matthew", 380, 730, 1.55, "spread", 1), F("jesus", 600, 730, 1.6, "bless", 1, "smile"), F("villager3", 820, 730, 1.5, "cup", -1), F("peter", 1000, 730, 1.5, "stand", -1)], "props": [P("table", 0, 640, layer="front")]},
        "p4": {"env": E("street", "night", "medium"), "figs": [F("pharisee", 380, 830, 1.8, "point", 1, "angry"), F("scribe", 560, 835, 1.7, "hips", 1, "angry"), F("john", 870, 830, 1.65, "stand", -1, "worried")]},
        "p5": {"env": E("feast", "night", "medium"), "figs": [F("jesus", 480, 840, 1.9, "spread", 1, "calm"), F("pharisee", 880, 840, 1.7, "hips", -1, "worried")]},
        "p6": {"env": E("house", "dusk", "medium"), "figs": [], "props": [P("skins", 600, 600, layer="front")]},
    },
    "ep08-sabbath": {
        "p1": {"env": E("field", "day", "medium"), "figs": [F("john", 300, 810, 1.5, "pluck"), F("peter", 470, 815, 1.6, "cup"), F("andrew", 640, 810, 1.5, "pluck"), F("jesus", 860, 815, 1.6, "stand", -1, "smile")]},
        "p2": {"env": E("field", "day", "close"), "figs": [F("pharisee", 620, 910, 2.2, "point", -1, "angry"), F("scribe", 880, 915, 2.1, "hips", -1, "angry")] + crowd([120, 230], 660, .9, 1, "worried", 0)},
        "p3": {"env": E("synagogue", "day", "medium"), "figs": [F("jesus", 300, 850, 1.9, "spread", 1, "calm")], "props": [P("loaves", 790, 650, layer="front")]},
        "p4": {"env": E("field", "day", "close"), "figs": [F("jesus", 420, 910, 2.2, "bless", 1, "calm"), F("pharisee", 830, 910, 2.0, "hips", -1, "worried")]},
        "p5": {"env": E("synagogue", "day", "medium"), "figs": [F("jesus", 350, 820, 1.7, "beckon", 1, "calm"), F("villager5", 630, 825, 1.6, "stand", -1, "worried"), F("pharisee", 920, 830, 1.55, "hips", -1, "angry")]},
        "p6": {"env": E("synagogue", "day", "close"), "figs": [F("villager5", 650, 900, 2.0, "raise", -1, "smile"), F("jesus", 330, 905, 1.9, "bless", 1, "smile"), F("pharisee", 1060, 780, 1.3, "stand", 1, "angry")]},
    },
}
