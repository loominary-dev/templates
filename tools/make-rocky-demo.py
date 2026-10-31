"""The Rocky demo: a platform level on Szadi art's Rocky Level pack (public domain): Gino runs and
jumps through a cave, collecting diamonds and hearts, stomping slimes, ducking bats and a snapping
plant, keeping off the crystals, to reach the great crystal. A few lights glow on the crystals.
Sounds from Kenney's Digital Audio and Impact Sounds (CC0).

    python3 tools/make-rocky-demo.py <rocky platformer dir> <kenney digital-audio dir> <kenney impact-sounds dir> [demos/rocky]

Needs Pillow.
"""
import math, os, sys
from PIL import ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

ROCKY, DA, IM = sys.argv[1], sys.argv[2], sys.argv[3]
out = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(__file__), "..", "demos", "rocky")
d = Demo(out, ["assets/art", "assets/tiles", "scenes", "vscript"], "e7000000")
P = lambda *parts: os.path.join(ROCKY, *parts)
img = lambda *parts: Image.open(P(*parts)).convert("RGBA")
GINO = ("Sprites", "Gino Character", "PNG")

# ── the art ──
SHEET = img("01. Rocky Level", "main_lev_build.png")
OTHER = img("01. Rocky Level", "other_lev_build.png")
SHEET.save(os.path.join(d.out, "assets", "art", "rock_tiles.png"))

def pieces(sheet, box, min_px=40, gap=2):
    """The separate drawings in a part of a sheet, each cropped to itself: split where whole columns, then whole rows, are clear."""
    def runs(flags):
        out, start, empty = [], None, 0
        for i in range(len(flags) + 1):
            if i < len(flags) and flags[i]:
                if start is None: start = i
                empty = 0
            elif start is not None:
                empty += 1
                if empty > gap or i == len(flags):
                    out.append((start, i - empty + 1)); start, empty = None, 0
        return out
    region = sheet.crop(box)
    a = region.getchannel("A").load()
    w, h = region.size
    out = []
    for x0, x1 in runs([any(a[x, y] > 20 for y in range(h)) for x in range(w)]):
        for y0, y1 in runs([any(a[x, y] > 20 for x in range(x0, x1)) for y in range(h)]):
            part = region.crop((x0, y0, x1, y1))
            bb = part.getbbox()
            if bb and (bb[2] - bb[0]) * (bb[3] - bb[1]) >= min_px: out.append(part.crop(bb))
    return out

def framed(frames, box):
    """Frames cut to one window, so the figure sits in the middle and turns about itself."""
    return [f.crop(box) for f in frames]

def seq(folder, stem, n, first=1, fmt="%02d"):
    return [img(*folder, (stem + fmt + ".png") % i) for i in range(first, first + n)]

# Gino: 64 px frames with the figure left of middle; a 40 px window centers it.
GBOX = (2, 24, 42, 64)
run_dir = GINO + ("Idle, run, jump",)
hit_dir = GINO + ("Hit, death",)
g_idle = framed(seq(run_dir, "idle", 9), GBOX)
g_run = framed(seq(run_dir, "run", 8), GBOX)
g_rise = framed(seq(run_dir, "jump_start", 2) + seq(run_dir, "jump_mid", 2), GBOX)
g_fall = framed([img(*run_dir, "jump_mid03.png"), img(*run_dir, "jump_mid04.png")], GBOX)
g_land = framed([img(*run_dir, "jump_landing.png")], GBOX)
g_hit = framed(seq(hit_dir, "hit", 3), GBOX)
d.sprite("Gino", 40, 40, [("idle", g_idle, 110, "loop"), ("run", g_run, 80, "loop"), ("jump", g_rise, 90, "once"),
                          ("fall", g_fall, 120, "loop"), ("land", g_land, 90, "once"), ("hit", g_hit, 90, "once")],
         [box("body", 20, 22, 14, 28)])

# The slime walks on the ground; its head is where a stomp lands.
BBOX = (0, 12, 24, 32)
d.sprite("Slime", 24, 20, [("walk", framed(seq(("Sprites", "Enemy02"), "walk", 6), BBOX), 110, "loop"),
                          ("squashed", framed(seq(("Sprites", "Enemy02"), "hit", 3), BBOX), 90, "once")],
         [box("head", 11, 5, 16, 5, sensor=True), box("body", 11, 13, 18, 12, sensor=True)])
d.sprite("Bat", 32, 32, [("fly", seq(("Sprites", "Enemy01"), "fly", 7), 80, "loop")], [box("body", 16, 15, 20, 16, sensor=True)])
# The snap reaches 16 px past the stem: a window the width of the source frame, about the stem, keeps it whole.
PBOX = (0, 16, 64, 64)
d.sprite("Plant", 64, 48, [("idle", framed(seq(("Sprites", "Enemy03"), "idle", 8), PBOX), 120, "loop"),
                           ("snap", framed(seq(("Sprites", "Enemy03"), "attack_right", 8), PBOX), 70, "loop")],
         [box("body", 32, 30, 18, 34, sensor=True)])

d.sprite("Diamond", 16, 14, [("shine", seq(("Collectible",), "diamond_big_", 6), 110, "loop")], [box("gem", 8, 7, 12, 10, sensor=True)])
d.sprite("Heart", 13, 13, [("beat", seq(("Collectible",), "heart", 6), 110, "loop")], [box("heart", 6, 6, 11, 11, sensor=True)])
d.sprite("HeartIcon", 13, 13, [("still", [img("Collectible", "heart01.png")], 400, "loop")], [])
d.sprite("DiamondIcon", 16, 14, [("still", [img("Collectible", "diamond_big_01.png")], 400, "loop")], [])
# The goal: the diamond drawn three times its size, pixel for pixel.
big = [f.resize((48, 42), Image.NEAREST) for f in seq(("Collectible",), "diamond_big_", 6)]
d.sprite("GreatCrystal", 48, 42, [("shine", big, 140, "loop")], [box("crystal", 24, 21, 30, 30, sensor=True)])
d.sprite("Sparkle", 80, 80, [("burst", seq(("Effects",), "destr_effect", 5), 60, "once")], [])
d.sprite("Puff", 32, 32, [("burst", seq(("Effects",), "hit_effect", 5), 60, "once")], [])

# Crystals: the teal clumps along the sheet's top row, a hazard to step on.
crystal = Image.new("RGBA", (32, 16))
crystal.alpha_composite(SHEET.crop((19 * 16, 0, 21 * 16, 16)))
d.sprite("Crystals", 32, 16, [("still", [crystal], 400, "loop")], [box("points", 16, 11, 26, 8, sensor=True)])

# A soft round light, tinted per kind.
def glow(size):
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - c, y - c) / c
            if r < 1: g.putpixel((x, y), (255, 255, 255, int(255 * (1 - r) ** 1.2)))
    return g
# One glow per light, drawn at the size it lights: a light at scale 1 with a texture scale of 1 works its
# shadows out at one texel to a pixel, so their edges stay sharp (the manual's "Shadow edges and texels").
for name, size in (("CrystalGlow", 332), ("BatGlow", 486), ("LanternGlow", 410), ("GoalGlow", 460)):
    d.sprite(name, size, size, [("still", [glow(size)], 400, "loop")], [])

# Scenery, no collision: dry grass, green plants, rock piles, dead trees, stalagmites.
DECOR = {
    "Grass": pieces(SHEET, (576, 256, 1024, 290), 60),
    "Sprout": pieces(SHEET, (576, 400, 1024, 464), 40),
    "Rocks": pieces(SHEET, (760, 80, 920, 176), 200),
    "Tree": pieces(OTHER, (40, 360, 480, 485), 400),
    "Stalagmite": pieces(OTHER, (100, 140, 420, 212), 300),
}
for name, parts in DECOR.items():
    for i, p in enumerate(parts):
        d.sprite("%s%d" % (name, i + 1), p.width, p.height, [("still", [p], 400, "loop")], [])

# The backdrop: three pictures the size of the view, which repeat side to side; the far ones move least.
for i in (1, 2, 3):
    # Darkened, so the lights stand out against it.
    ImageEnhance.Brightness(img("01. Rocky Level", "background%d.png" % i)).enhance(0.6).save(os.path.join(d.out, "assets", "art", "background%d.png" % i))
    d.write("assets/tiles/Back%d.tileset.json" % i, {"schemaVersion": 1, "image": "assets/art/background%d.png" % i, "tileWidth": 480, "tileHeight": 270,
        "tiles": [{"id": 0, "x": 0, "y": 0, "collision": []}], "physicsLayers": []})

d.sounds({"jump": (DA, "phaseJump1.ogg"), "gem": (DA, "powerUp7.ogg"), "heart": (DA, "powerUp2.ogg"), "stomp": (IM, "impactGeneric_light_001.ogg"),
          "hurt": (IM, "impactGeneric_light_004.ogg"), "win": (DA, "threeTone1.ogg")})

# ── collision layers, as bits ──
PLAYER, PICKUP, SOLID, ENEMY, HAZARD = 1, 2, 4, 8, 16

# ── the level ──
# 16 px cells, 17 rows (one view tall). '#' rock, 'o' a floating rock ledge (two rows), '^' crystals,
# 'd' a diamond, 'h' a heart, 'B' a slime, 'V' a bat, 'X' a plant, 'P' the start, 'G' the great crystal,
# 'L' a light, scenery: 'g' grass, 's' a sprout, 'r' rocks, 't' a tree, 'm' a stalagmite.
W, H, CELL = 140, 17, 16
grid = [["."] * W for _ in range(H)]
def ground(c0, c1, top):
    for c in range(c0, c1 + 1):
        for r in range(top, H): grid[r][c] = "#"
def ledge(c0, c1, r):
    for c in range(c0, c1 + 1): grid[r][c] = grid[r + 1][c] = "o"
def put(ch, c, r): grid[r][c] = ch
ground(0, 30, 12); ground(31, 38, 10); ground(39, 44, 12); ground(48, 66, 12)
ground(71, 82, 9); ground(83, 90, 13); ground(91, 104, 11); ground(109, 124, 12); ground(125, 139, 10)
ledge(22, 25, 8); ledge(45, 47, 9); ledge(56, 59, 8); ledge(67, 70, 10); ledge(93, 96, 6); ledge(99, 102, 8); ledge(105, 108, 9)
for c, r, ch in [(3, 11, "P"), (8, 11, "g"), (11, 11, "s"), (12, 9, "d"), (16, 9, "d"), (20, 11, "t"), (24, 7, "d"), (27, 11, "B"),
                 (33, 9, "g"), (36, 9, "d"), (40, 11, "^"), (42, 11, "^"), (41, 9, "L"), (46, 8, "d"), (41, 5, "V"), (52, 11, "r"),
                 (57, 7, "d"), (58, 7, "h"), (61, 11, "B"), (64, 11, "s"), (68, 9, "d"), (74, 8, "m"), (77, 8, "d"), (80, 8, "g"),
                 (86, 12, "X"), (88, 10, "d"), (94, 5, "d"), (95, 5, "d"), (97, 3, "V"), (100, 7, "d"), (102, 10, "t"), (106, 8, "d"),
                 (111, 11, "g"), (113, 11, "^"), (115, 11, "^"), (114, 9, "L"), (118, 11, "B"), (121, 11, "s"), (127, 9, "X"),
                 (130, 9, "r"), (132, 9, "h"), (136, 9, "G"), (136, 6, "L"), (5, 11, "r")]:
    put(ch, c, r)
LEVEL = ["".join(row) for row in grid]

rock = lambda c, r: 0 <= r < H and 0 <= c < W and LEVEL[r][c] in "#o"
used, cells, solid_tiles, ledge_tiles = set(), [], set(), set()
def tile_at(col, row):
    used.add((col, row))
    return row * 64 + col
for r in range(H):
    for c in range(W):
        ch = LEVEL[r][c]
        if ch not in "#o": continue
        v = 7 + (c * 7 + r * 3) % 17   # the sheet's middle columns, varied
        left, right = not rock(c - 1, r), not rock(c + 1, r)
        if ch == "o":
            # A ledge: the sheet's floating platform, rock on top and teal crystals hanging under.
            lft, rgt = LEVEL[r][c - 1] != "o", c + 1 >= W or LEVEL[r][c + 1] != "o"
            col = 8 if lft else 16 if rgt else 9 + (c % 7)
            under = rock(c, r - 1) and LEVEL[r - 1][c] == "o"
            cells.append([c, r, tile_at(col, 13 if under else 12)])
            ledge_tiles.add((13 if under else 12) * 64 + col)
            if not under: solid_tiles.add(12 * 64 + col)
            continue
        if not rock(c, r - 1):                    # the top: its lit rim
            t = tile_at(5 if left else 25 if right else v, 2)
        else:                                      # below: the walls and the dark inside
            depth = 3 if not rock(c, r - 2) else 4 + (c + r) % 5
            t = tile_at(5 if left else 25 if right else v, depth)
        cells.append([c, r, t])
        solid_tiles.add(t)
def outline(col, row):
    """The convex outline of a tile's drawn pixels, in its own pixels: what a ledge casts its shadow from."""
    pts = []
    for y in range(CELL):
        for x in range(CELL):
            if SHEET.getpixel((col * CELL + x, row * CELL + y))[3] > 64:
                pts += [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
    pts = sorted(set(pts))
    if len(pts) < 3: return None
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
    return [{"x": x, "y": y} for x, y in lower[:-1] + upper[:-1]]

def tile_shapes(col, row):
    box = {"kind": "box", "cx": 8, "cy": 8, "w": CELL, "h": CELL}
    if row * 64 + col in ledge_tiles:
        # A ledge stands on its box and casts its shadow from the shape it is drawn.
        hull = outline(col, row)
        shapes = [box] if row * 64 + col in solid_tiles else []
        return shapes + ([{"kind": "poly", "points": hull, "sensor": True, "occluder": 1}] if hull else [])
    return [dict(box, occluder=1)] if row * 64 + col in solid_tiles else []

d.write("assets/tiles/Rock.tileset.json", {"schemaVersion": 1, "image": "assets/art/rock_tiles.png", "tileWidth": CELL, "tileHeight": CELL,
    "tiles": [{"id": row * 64 + col, "x": col * CELL, "y": row * CELL,
               "collision": tile_shapes(col, row)}
              for col, row in sorted(used)],
    "physicsLayers": [{"name": "Ground", "collisionLayer": SOLID, "collisionMask": -1}]})

# ── Types ──
d.type_json("Gino", "Sprite", {"spriteKey": "Gino.sprite.json", "collision": {"layer": PLAYER, "mask": -1}},
            [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"},
             {"componentClass": "Platformer", "maxSpeed": 120, "acceleration": 1000, "deceleration": 1300, "jumpStrength": 340, "jumpCut": 0.55,
              "coyoteTime": 0.1, "jumpBuffer": 0.12, "floorSnap": 3},
             {"componentClass": "Blink", "interval": 0.08, "offOpacity": 0.25},
             {"componentClass": "GinoRules"}])
d.type_json("Slime", "Sprite", {"spriteKey": "Slime.sprite.json", "collision": {"layer": ENEMY, "mask": PLAYER}},
            [{"componentClass": "Patrol", "axis": "Horizontal", "distance": 56, "speed": 26}, {"componentClass": "SlimeRules"}])
# A bat carries a light, so it glows: the dark shows where that light comes from.
d.type_json("Bat", "Sprite", {"spriteKey": "Bat.sprite.json", "collision": {"layer": HAZARD, "mask": PLAYER}, "glows": True},
            [{"componentClass": "Patrol", "axis": "Horizontal", "distance": 72, "speed": 34},
             {"componentClass": "Oscillate", "property": "y", "magnitude": 10, "period": 1.4}, {"componentClass": "BatRules"}])
d.type_json("Plant", "Sprite", {"spriteKey": "Plant.sprite.json", "collision": {"layer": HAZARD, "mask": PLAYER}}, [{"componentClass": "PlantRules"}])
# The gems glow: drawn at their own brightness over the dark (Glows), as the crystals that light the cave would.
for t, layer, glows in [("Diamond", PICKUP, True), ("Heart", PICKUP, False), ("GreatCrystal", PICKUP, True), ("Crystals", HAZARD, True)]:
    d.type_json(t, "Sprite", dict({"spriteKey": t + ".sprite.json", "collision": {"layer": layer, "mask": PLAYER}}, **({"glows": True} if glows else {})))
for t in ("Sparkle", "Puff"):
    d.type_json(t, "Sprite", {"spriteKey": t + ".sprite.json"}, [{"componentClass": "EffectRules"}])
d.type_json("DiamondIcon", "Sprite", {"spriteKey": "DiamondIcon.sprite.json"})
for i in (1, 2, 3): d.type_json("HeartIcon%d" % i, "Sprite", {"spriteKey": "HeartIcon.sprite.json"})
d.type_json("DiamondCount", "Label", {"text": "0", "fontSize": 10, "textColor": 0xF2F6E8})
d.type_json("WinSign", "Label", {"text": "You reached the great crystal!", "fontSize": 14, "textColor": 0xF2F6E8, "visible": False})
# The lights: teal over the crystals, white over the great crystal.
d.type_json("CrystalLight", "Light", {"spriteKey": "CrystalGlow.sprite.json", "tint": 0x4FE3D0, "opacity": 0.9, "radius": 3})
# Lights that move, so the shadows the ledges and rocks cast swing as they pass: the glow each bat carries,
# and the soft light Gino carries. Each is its carrier's child, so it goes where the carrier goes.
d.type_json("BatLight", "Light", {"spriteKey": "BatGlow.sprite.json", "tint": 0xFFD98A, "opacity": 1.0, "radius": 4})
# Pale and cool: the light map multiplies over a teal-green cave, where a warm light has little red to lift.
d.type_json("Lantern", "Light", {"spriteKey": "LanternGlow.sprite.json", "tint": 0xBFF6FF, "opacity": 1.0, "radius": 3})
d.type_json("GoalLight", "Light", {"spriteKey": "GoalGlow.sprite.json", "tint": 0xD8FFF8, "opacity": 0.9, "radius": 4})
for name, parts in DECOR.items():
    for i in range(len(parts)): d.type_json("%s%d" % (name, i + 1), "Sprite", {"spriteKey": "%s%d.sprite.json" % (name, i + 1)})

# ── the scene ──
uid = d.uid
objects = [{"id": uid(1), "name": "Level"}]
n = [10]
def place(name, type_name, x, y, parent=None, **extra):
    n[0] += 1
    o = dict({"id": uid(n[0]), "parent": parent or uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra)
    objects.append(o)
    return o
for i, factor in ((1, 0.1), (2, 0.25), (3, 0.45)):
    layer = uid(800 + i)
    objects.append({"id": layer, "parent": uid(1), "name": "Back%d" % i, "type": "Layer", "parallaxX": factor})
    # Enough copies to reach past the level's end at this layer's pace, and a little before its start.
    objects.append({"id": uid(810 + i), "parent": layer, "name": "Backdrop%d" % i, "type": "Tilemap", "tilesetKey": "assets/tiles/Back%d.tileset.json" % i,
                    "cellWidth": 480, "cellHeight": 270, "cells": [[c, 0, 0] for c in range(-1, 2 + int(W * CELL * factor / 480))]})
SCENERY, GROUND_ID, REWARDS, DANGER, LIGHTS = uid(820), uid(821), uid(822), uid(823), uid(824)
objects.append({"id": SCENERY, "parent": uid(1), "name": "Scenery"})
objects.append({"id": GROUND_ID, "parent": uid(1), "name": "Ground", "type": "Tilemap", "tilesetKey": "assets/tiles/Rock.tileset.json",
                "cellWidth": CELL, "cellHeight": CELL, "cells": cells})
for gid, name in ((REWARDS, "Rewards"), (DANGER, "Danger"), (LIGHTS, "Lights")):
    objects.append({"id": gid, "parent": uid(1), "name": name})
counts = {}
def numbered(t):
    counts[t] = counts.get(t, 0) + 1
    return "%s%d" % (t, counts[t])
def light(name, type_name, x, y, parent):
    return place(name, type_name, x, y, parent=parent)
pick = {"g": "Grass", "s": "Sprout", "r": "Rocks", "t": "Tree", "m": "Stalagmite"}
start = goal = None
for r in range(H):
    for c in range(W):
        ch = LEVEL[r][c]
        cx, floor = c * CELL + 8, (r + 1) * CELL
        if ch in pick:
            kind = pick[ch]
            k = 1 + (c * 5 + r) % len(DECOR[kind])
            h = DECOR[kind][k - 1].height
            place(numbered(kind), "%s%d" % (kind, k), cx, floor - h / 2, parent=SCENERY)
        elif ch == "d": place(numbered("Diamond"), "Diamond", cx, r * CELL + 8, parent=REWARDS)
        elif ch == "h": place(numbered("Heart"), "Heart", cx, r * CELL + 8, parent=REWARDS)
        elif ch == "^": place(numbered("Crystals"), "Crystals", cx + 8, floor - 8, parent=DANGER)
        elif ch == "B": place(numbered("Slime"), "Slime", cx, floor - 10, parent=DANGER)
        elif ch == "V":
            bat = place(numbered("Bat"), "Bat", cx, r * CELL + 8, parent=DANGER)
            light(numbered("BatLight"), "BatLight", 16, 16, bat["id"])
        elif ch == "X": place(numbered("Plant"), "Plant", cx, floor - 24, parent=DANGER)
        elif ch == "L": light(numbered("Light"), "GoalLight" if c > 130 else "CrystalLight", cx + (0 if c > 130 else 8), r * CELL + 8, LIGHTS)
        elif ch == "G": goal = (cx, floor - 21)
        elif ch == "P": start = (cx, floor - 17)
place("GreatCrystal1", "GreatCrystal", goal[0], goal[1])
gino = place("Gino1", "Gino", start[0], start[1])
# The light Gino carries: his child, so it goes where he goes.
light("Lantern1", "Lantern", 20, 13, gino["id"])
# Starts the level again when Gino is out of hearts.
d.type_json("Scenes", "SceneManager", {})
place("Scenes1", "Scenes", 0, 0)
place("Camera1", "Camera", start[0], 135, target="Gino1", smoothing=0.12, keepInBounds=True,
      boundsLeft=0, boundsTop=0, boundsRight=W * CELL, boundsBottom=H * CELL, currentAtStart=True)
HUD = uid(830)
objects.append({"id": HUD, "parent": uid(1), "name": "HUD", "type": "Layer", "parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
for name, t, x, y in [("HeartIcon1", "HeartIcon1", 14, 12), ("HeartIcon2", "HeartIcon2", 30, 12), ("HeartIcon3", "HeartIcon3", 46, 12),
                      ("DiamondIcon1", "DiamondIcon", 72, 12), ("DiamondCount1", "DiamondCount", 82, 6), ("WinSign1", "WinSign", 130, 110)]:
    place(name, t, x, y, parent=HUD)
d.scene("scenes/Level.scene.json", objects)

# ── the rules ──
gems, lives = var("diamonds"), var("lives")
facing = cvalue("self", "Platformer", "getFacing")
gx, gy = value("Gino", "Node", "getPositionX"), value("Gino", "Node", "getPositionY")
def sound(k): return line("audio", "Audio", "playSound", s(k))
def anim(t, a): return line(t, "Sprite", "setAnimation", s(a))
def playing(t, a): return line(t, "Sprite", "isAnimationPlaying", s(a))
def setvar(n, v): return line("variables", "Variables", "setVariable", s(n), v)
def addvar(n, v): return line("variables", "Variables", "addToVariable", s(n), lit(v))
hurt = [addvar("lives", -1), comp("Gino", "Blink", "blinkFor", lit(1.2)), anim("Gino", "hit"), comp("Gino", "Platformer", "jump"), sound("hurt")]
safe = not_(comp("Gino", "Blink", "isBlinking"))
to_start = [line("Gino", "Node", "setPosition", lit(start[0]), lit(start[1]))]
gino_rules = [
    rule([once()], [setvar("lives", lit(3)), setvar("diamonds", lit(0))]),
    rule([held("Move Left")], [comp("Gino", "Platformer", "moveLeft")]),
    rule([held("Move Right")], [comp("Gino", "Platformer", "moveRight")]),
    rule([held("Jump")], [comp("Gino", "Platformer", "jump")]),
    rule([held("Move Down")], [comp("Gino", "Platformer", "holdDown")]),
    rule([comp("Gino", "Platformer", "onJumped")], [anim("Gino", "jump"), sound("jump")]),
    rule([comp("Gino", "Platformer", "onStartedFalling")], [anim("Gino", "fall")]),
    rule([comp("Gino", "Platformer", "onLanded")], [anim("Gino", "land")]),
    rule([comp("Gino", "Platformer", "isOnFloor"), comp("Gino", "Platformer", "isMoving"), not_(playing("Gino", "run")), not_(playing("Gino", "hit"))], [anim("Gino", "run")]),
    rule([comp("Gino", "Platformer", "isOnFloor"), not_(comp("Gino", "Platformer", "isMoving")), not_(playing("Gino", "idle")), not_(playing("Gino", "land")), not_(playing("Gino", "hit"))],
         [anim("Gino", "idle")]),
    rule([line("Gino", "Sprite", "onAnimationFinished")], [anim("Gino", "idle")]),
    rule([compare(facing, EQ, lit(-1))], [line("self", "Node", "setMirrored", b(True))]),
    rule([compare(facing, EQ, lit(1))], [line("self", "Node", "setMirrored", b(False))]),
    # A diamond: gone in a burst of light, counted on the HUD.
    rule([line("Gino", "Node", "onCollisionStarted", s("Diamond"))],
         [sheet("createObject", s("Sparkle"), lit(1)), line("Sparkle", "Node", "setPosition", value("Diamond", "Node", "getPositionX"), value("Diamond", "Node", "getPositionY")),
          line("Sparkle", "Node", "setScaleXY", lit(0.5)),
          line("Diamond", "Node", "queueDestroy"), addvar("diamonds", 1), line("DiamondCount", "Label", "setNumber", gems), sound("gem")]),
    # A heart gives back a life, up to three.
    rule([line("Gino", "Node", "onCollisionStarted", s("Heart")), compare(lives, LT, lit(3))],
         [line("Heart", "Node", "queueDestroy"), addvar("lives", 1), sound("heart")]),
    # A slime landed on is squashed and Gino bounces; walked into, it hurts.
    rule([line("Gino", "Node", "onCollisionStartedShapes", s("Slime"), s("body"), s("head"))],
         [anim("Slime", "squashed"), line("Slime", "Node", "setCollisionEnabled", b(False)), comp("Slime", "Patrol", "stop"),
          sheet("createObject", s("Puff"), lit(1)), line("Puff", "Node", "setPosition", value("Slime", "Node", "getPositionX"), value("Slime", "Node", "getPositionY")),
          comp("Gino", "Platformer", "jump"), sound("stomp")]),
    rule([line("Gino", "Node", "onCollisionStartedShapes", s("Slime"), s("body"), s("body")), safe], hurt),
    rule([line("Gino", "Node", "isOverlapping", s("Bat")), safe], hurt),
    rule([line("Gino", "Node", "isOverlapping", s("Plant")), safe], hurt),
    rule([line("Gino", "Node", "isOverlapping", s("Crystals")), safe], hurt),
    # Down a gap costs a heart and puts Gino back at the start. Out of hearts, the level starts
    # again: diamonds, hearts and enemies back, three hearts (the first rule), the best kept.
    rule([compare(gy, GT, lit(H * CELL + 40))], to_start + [addvar("lives", -1), sound("hurt")]),
    rule([compare(lives, LE, lit(0)), once()], [line("Scenes", "SceneManager", "changeScene", s("scenes/Level.scene.json"))]),
    # The great crystal: the sign, a stop, and a better diamond count than the saved best kept.
    rule([line("Gino", "Node", "onCollisionStarted", s("GreatCrystal"))],
         [line("WinSign", "Node", "show"), comp("Gino", "Platformer", "setEnabled", b(False)), sound("win")],
         [rule([compare(gems, GT, value("save", "Save", "savedNumber", s("best")))], [line("save", "Save", "saveNumber", s("best"), gems)])]),
    # The hearts on the HUD follow the lives left.
    rule([compare(lives, LT, lit(3))], [line("HeartIcon3", "Node", "hide")]),
    rule([compare(lives, GE, lit(3))], [line("HeartIcon3", "Node", "show")]),
    rule([compare(lives, LT, lit(2))], [line("HeartIcon2", "Node", "hide")]),
    rule([compare(lives, GE, lit(2))], [line("HeartIcon2", "Node", "show")]),
    rule([compare(lives, LT, lit(1))], [line("HeartIcon1", "Node", "hide")]),
    rule([compare(lives, GE, lit(1))], [line("HeartIcon1", "Node", "show")]),
]
d.write("vscript/GinoRules.vscript.json", {"rules": gino_rules, "vars": []})
d.write("vscript/SlimeRules.vscript.json", {"rules": [
    rule([line("Slime", "Sprite", "onAnimationFinished")], [line("Slime", "Node", "queueDestroy")]),
    # The slime looks left as drawn: turned round while heading out to the right.
    rule([comp("Slime", "Patrol", "isHeadingOut")], [line("Slime", "Node", "setMirrored", b(True))]),
    rule([not_(comp("Slime", "Patrol", "isHeadingOut"))], [line("Slime", "Node", "setMirrored", b(False))]),
], "vars": []})
d.write("vscript/BatRules.vscript.json", {"rules": [
    rule([comp("Bat", "Patrol", "isHeadingOut")], [line("Bat", "Node", "setMirrored", b(False))]),
    rule([not_(comp("Bat", "Patrol", "isHeadingOut"))], [line("Bat", "Node", "setMirrored", b(True))]),
], "vars": []})
# The plant snaps while Gino is near, facing him: the pack's "attack_right" frames lunge to the LEFT.
px = value("self", "Node", "getPositionX")
near = compare(value("maths", "Maths", "absolute", op("-", gx, px)), LT, lit(64))
far = compare(value("maths", "Maths", "absolute", op("-", gx, px)), GE, lit(64))
pick_gino = {"scope": "Gino", "name": "pickAll", "params": []}
d.write("vscript/PlantRules.vscript.json", {"rules": [
    rule([pick_gino, near, not_(playing("self:Plant", "snap"))], [anim("self:Plant", "snap")]),
    rule([pick_gino, far, not_(playing("self:Plant", "idle"))], [anim("self:Plant", "idle")]),
    rule([pick_gino, compare(gx, LT, px)], [line("self", "Node", "setMirrored", b(False))]),
    rule([pick_gino, compare(gx, GE, px)], [line("self", "Node", "setMirrored", b(True))]),
], "vars": []})
d.write("vscript/EffectRules.vscript.json", {"rules": [rule([line("self:Sprite", "Sprite", "onAnimationFinished")], [line("self", "Node", "queueDestroy")])], "vars": []})

INPUT = {"Move Left": keys(37, 65), "Move Right": keys(39, 68), "Move Up": keys(38, 87), "Move Down": keys(40, 83),
         "Jump": {"bindings": [{"kind": "key", "code": c} for c in (32, 38, 87)] + [{"kind": "pad", "code": 0}]},
         "Accept": keys(13, 32), "Cancel": keys(27), "Pause": keys(27)}
d.write("project.json", {"schemaVersion": 2, "name": "Rocky demo", "entryScene": "scenes/Level.scene.json", "input": INPUT,
    "collisionLayers": {"1": "Player", "2": "Pickup", "3": "Ground", "4": "Enemy", "5": "Hazard"},
    "display": {"width": 480, "height": 270, "windowWidth": 960, "windowHeight": 540, "presentMode": "fit", "displayMode": "windowed",
                "autoResize": True, "wholeWindowScale": True, "drawnAt": "game", "highResolution": "normal"},
    "physics": {"engine": "arcade", "gravity": 760},
    # A dim cave: the light map multiplied over the world, so the lights show as light.
    "lighting": {"lightMap": True, "ambient": "#2e343c", "blend": "multiply"}})
d.write("README.md", """# Rocky demo

A platform level in a cave: run and jump with the arrow keys or WASD (Space
jumps too), collect the diamonds, stomp the slimes by landing on them, keep
clear of the bats, the snapping plant and the crystals, and reach the great
crystal. Three hearts: a hit or a fall down a gap costs one, a heart found gives one
back, and out of hearts the level starts again. Your best diamond count is saved.

Built on the **Platformer** behavior and a tilemap level. A **Camera** follows
Gino; the cave behind is three **Layers**, the far ones moving least. The
slimes and bats **Patrol** (the bats **Oscillate** too), Gino **Blinks** after a
hit. **Lights** glow over the crystals; each bat carries a glow and Gino
carries one, so their shadows move; the project's light map dims the cave. What gives the light
**Glows**, drawn at its own brightness over the dark: the crystals, the bats and the diamonds, so the
cave shows where its light comes from, not only what it lights. Every rule is in `vscript/`.

Art by Szadi art (Rocky Level pack, public domain). Sounds by
[Kenney](https://kenney.nl) (Digital Audio, Impact Sounds), CC0. Generated by
`tools/make-rocky-demo.py`.
""")
print("wrote", d.out, "with", len(cells), "ground cells and", len(objects), "objects")
