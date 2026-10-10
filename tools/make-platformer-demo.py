"""The Platformer demo, generated from Kenney's Pixel Platformer pack: a level
painted as a tilemap, the astronaut as the player, slimes, coins, spikes and a
flag, with the rules a platform game needs. Made by this script rather than by
hand, so a format change is a re-run.

    python3 tools/make-platformer-demo.py <kenney pixel-platformer dir> <kenney digital-audio dir> <kenney impact-sounds dir> [demos/platformer]

The packs: https://kenney.nl/assets/pixel-platformer, /digital-audio and
/impact-sounds, all CC0. Needs Pillow.
"""
import base64, json, math, os, shutil, struct, sys, uuid
from PIL import Image

pp, da, im = sys.argv[1], sys.argv[2], sys.argv[3]
out = os.path.abspath(sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(__file__), "..", "demos", "platformer"))
shutil.rmtree(out, ignore_errors=True)
for d in ["assets/art", "assets/sounds", "assets/tiles", "scenes", "events"]: os.makedirs(os.path.join(out, d))

def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

def uid(n):  # stable ids, so a re-run changes nothing that did not change
    return "e0000000-0000-4000-8000-%012d" % n

# ── art: the packed sheets, copied as they are ──
TILES, CHARS, BACKS = "tilemap_packed.png", "tilemap-characters_packed.png", "tilemap-backgrounds_packed.png"
for f in [TILES, CHARS, BACKS]: shutil.copy(os.path.join(pp, "Tilemap", f), os.path.join(out, "assets", "art", f))
tiles_im = Image.open(os.path.join(pp, "Tilemap", TILES)).convert("RGBA")
chars_im = Image.open(os.path.join(pp, "Tilemap", CHARS)).convert("RGBA")

def region(sheet, index, size, columns):
    x, y = (index % columns) * size, (index // columns) * size
    return sheet.crop((x, y, x + size, y + size))

def argb(image):
    """Packed 0xAARRGGBB per pixel, little-endian int32 bytes, base64; -1 is transparent."""
    vals = []
    for r, g, b, a in image.getdata():
        vals.append(-1 if a == 0 else struct.unpack("<i", struct.pack("<I", (a << 24) | (r << 16) | (g << 8) | b))[0])
    return base64.b64encode(b"".join(struct.pack("<i", v) for v in vals)).decode()

seq = [100]
def next_id():
    seq[0] += 1
    return uid(seq[0])

def sprite(name, size, animations, collision, height=None):
    w, h = size, (height or size)
    """A sprite as its two files: the document, and the picture beside it holding every frame's pixels as a grid."""
    layer = next_id()
    anims, cels, pictures = [], [], []
    for aname, frames, duration, mode in animations:
        fids = []
        for f in frames:
            fid = next_id()
            fids.append(fid)
            cels.append({"layerId": layer, "frameId": fid, "at": len(pictures)})
            pictures.append(f)
        anims.append({"id": next_id(), "name": aname, "loop": mode == "loop", "playMode": mode, "repeatTo": 0, "repeatCount": 0,
                      "collision": collision, "points": [], "collisionShared": True, "pointsShared": False,
                      "frames": [{"id": fid, "duration": duration, "pivotX": 0.5, "pivotY": 0.5, "collision": [], "points": []} for fid in fids]})
    columns = max(1, math.ceil(math.sqrt(len(pictures))))
    rows = max(1, math.ceil(len(pictures) / columns))
    sheet = Image.new("RGBA", (w * columns, h * rows), (0, 0, 0, 0))
    for i, pic in enumerate(pictures):
        sheet.paste(pic.convert("RGBA"), ((i % columns) * w, (i // columns) * h))
    sheet.save(os.path.join(out, name + ".sprite.png"))
    write(name + ".sprite.json", {"width": w, "height": h, "colorMode": "rgba", "sheet": {"columns": columns}, "palette": [],
        "layers": [{"id": layer, "name": "Layer 1", "visible": True, "opacity": 1, "locked": False, "blendMode": "normal", "reference": False}],
        "animations": anims, "cels": cels})
    return name + ".sprite.json"

def box(name, cx, cy, w, h, **extra):
    return dict({"name": name, "kind": "box", "cx": cx, "cy": cy, "w": w, "h": h}, **extra)

char = lambda i: region(chars_im, i, 24, 9)
tile = lambda i: region(tiles_im, i, 18, 20)
sprite("Player", 24, [("idle", [char(0)], 400, "loop"), ("walk", [char(0), char(1)], 150, "loop"), ("jump", [char(1)], 400, "loop")],
       [box("body", 12, 13, 14, 20)])
sprite("Slime", 24, [("walk", [char(18), char(19)], 220, "loop"), ("squashed", [char(20)], 350, "once")],
       [box("head", 12, 11, 14, 4, sensor=True), box("body", 12, 17, 14, 8, sensor=True)])
sprite("Coin", 18, [("spin", [tile(151), tile(152)], 300, "loop")], [box("coin", 9, 9, 12, 12, sensor=True)])
sprite("Spikes", 18, [("still", [tile(68)], 400, "loop")], [box("points", 9, 13, 16, 8, sensor=True)])
sprite("Flag", 18, [("wave", [tile(111), tile(112)], 400, "loop")], [box("pole", 9, 9, 10, 18, sensor=True)])

# ── sounds ──
SOUNDS = {"jump": (da, "phaseJump1.ogg"), "coin": (da, "powerUp7.ogg"), "stomp": (im, "impactGeneric_light_001.ogg"),
          "hurt": (im, "impactGeneric_light_004.ogg"), "win": (da, "threeTone1.ogg")}
assets = []
for n, (key, (pack, f)) in enumerate(SOUNDS.items()):
    shutil.copy(os.path.join(pack, "Audio", f), os.path.join(out, "assets", "sounds", key + ".ogg"))
    assets.append({"uuid": uid(900 + n), "key": key, "path": "assets/sounds/%s.ogg" % key})
write("assets.json", {"schemaVersion": 1, "assets": assets})

# The level's width in pixels, for the camera's bounds; the level itself is below.
LEVEL_W = 78 * 18

# ── collision layers, as bits ──
PLAYER, PICKUP, SOLID, ENEMY, HAZARD = 1, 2, 4, 8, 16

# ── Types ──
def type_json(base, defaults, components=()):
    write(defaults.get("_name") + ".type.json", {"schemaVersion": 2, "baseClass": base,
        "defaults": {k: v for k, v in defaults.items() if k != "_name"}, "components": list(components)})

type_json("Sprite", {"_name": "Player", "spriteKey": "Player.sprite.json", "collision": {"layer": PLAYER, "mask": -1}},
          [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"},
           {"componentClass": "Platformer", "maxSpeed": 110, "acceleration": 900, "deceleration": 1200, "jumpStrength": 330, "jumpCut": 0.6,
            "coyoteTime": 0.1, "jumpBuffer": 0.1, "floorSnap": 3},
           {"componentClass": "PlayerRules"}])
type_json("Sprite", {"_name": "Slime", "spriteKey": "Slime.sprite.json", "collision": {"layer": ENEMY, "mask": PLAYER}},
          [{"componentClass": "Patrol", "axis": "Horizontal", "distance": 54, "speed": 28}, {"componentClass": "SlimeRules"}])
type_json("Sprite", {"_name": "Coin", "spriteKey": "Coin.sprite.json", "collision": {"layer": PICKUP, "mask": PLAYER}})
type_json("Sprite", {"_name": "Spikes", "spriteKey": "Spikes.sprite.json", "collision": {"layer": HAZARD, "mask": PLAYER}})
type_json("Sprite", {"_name": "Flag", "spriteKey": "Flag.sprite.json", "collision": {"layer": PICKUP, "mask": PLAYER}})
type_json("Sprite", {"_name": "CoinIcon", "spriteKey": "Coin.sprite.json"})
type_json("Label", {"_name": "CoinCount", "text": "0", "fontSize": 10})
type_json("Label", {"_name": "WinSign", "text": "You made it!", "fontSize": 14, "visible": False})

# ── the level ──
# 18 px cells, 10 rows (one screen tall), as wide as it reads. '#' ground, '=' a
# plank (one-way), 'c' coin, 's' spikes, 'S' slime, 'P' the player, 'F' the flag.
LEVEL = [
    "..............................................................................",
    "..............................................................................",
    "......................c.......................c..c............................",
    "..................c..===..............c....=======........................F...",
    ".........c.c.........................===...........##.....c.c.......##########",
    "....P.........==.............c...c.........................===.....####.......",
    "...####.....####.....S.....######.......####.....S.......#####..######........",
    "########...#######..######.######ss.#########...#####..ssss###############....",
    "##############################################.###############################",
    "##############################################################################",
]
H, W = len(LEVEL), len(LEVEL[0])
CELL = 18
solid = lambda c, r: 0 <= r < H and 0 <= c < W and LEVEL[r][c] == "#"
cells = []
for r in range(H):
    for c in range(W):
        ch = LEVEL[r][c]
        if ch == "#":
            if not solid(c, r - 1):
                t = 20 if not solid(c - 1, r) and not solid(c + 1, r) else 21 if not solid(c - 1, r) else 23 if not solid(c + 1, r) else 22
            else:
                t = [121, 122, 141, 142][(c * 7 + r * 13) % 4]
            cells.append([c, r, t])
        elif ch == "=":
            # A plank: its left half, and its right half at the end of a run.
            right = c + 1 >= W or LEVEL[r][c + 1] != "="
            cells.append([c, r, 49 if right else 48])

# The tile set: every tile of the sheet, the ground ones solid, the plank one-way.
tiles = []
for i in range(180):
    t = {"id": i, "x": (i % 20) * CELL, "y": (i // 20) * CELL, "collision": []}
    # A tile's collision is a flat list of shapes, as the tile set editor writes it.
    if i in (20, 21, 22, 23, 121, 122, 141, 142):
        t["collision"] = [{"kind": "box", "cx": 9, "cy": 9, "w": CELL, "h": CELL}]
    if i in (48, 49):
        t["collision"] = [{"kind": "box", "cx": 9, "cy": 3, "w": CELL, "h": 6, "oneWay": ["jumpThrough", "passLeft", "passRight", "dropThrough"]}]
    tiles.append(t)
write("assets/tiles/Ground.tileset.json", {"schemaVersion": 1, "image": "assets/art/" + TILES, "tileWidth": CELL, "tileHeight": CELL,
    "tiles": tiles, "physicsLayers": [{"name": "Ground", "collisionLayer": SOLID, "collisionMask": -1}]})
# The backdrop: sky, a band of hills, then plain blue, in 24 px cells, well past both ends of the level.
BACK = 24
back_tiles = [{"id": i, "x": (i % 8) * BACK, "y": (i // 8) * BACK, "collision": []} for i in range(24)]
write("assets/tiles/Sky.tileset.json", {"schemaVersion": 1, "image": "assets/art/" + BACKS, "tileWidth": BACK, "tileHeight": BACK,
    "tiles": back_tiles, "physicsLayers": []})
back_cells = []
for c in range(-8, W * CELL // BACK + 9):
    for r in range(0, 8):
        back_cells.append([c, r, 0 if r < 2 else 8 + (c % 4) if r == 2 else 16])

# ── the scene ──
objects = [{"id": uid(1), "name": "Level"}]
n = [2]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    o = dict({"id": uid(n[0]), "parent": uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra)
    objects.append(o)
    return o
# The backdrop: a Layer following four tenths of the camera's sideways movement, holding the sky's tile map.
objects.append({"id": uid(800), "parent": uid(1), "name": "Backdrop", "type": "Layer", "parallaxX": 0.4})
objects.append({"id": uid(2), "parent": uid(800), "name": "Sky", "type": "Tilemap", "tilesetKey": "assets/tiles/Sky.tileset.json",
                "cellWidth": BACK, "cellHeight": BACK, "cells": back_cells})
objects.append({"id": uid(3), "parent": uid(1), "name": "Ground", "type": "Tilemap", "tilesetKey": "assets/tiles/Ground.tileset.json",
                "cellWidth": CELL, "cellHeight": CELL, "cells": cells})
n[0] = 3
counts = {}
def numbered(t):
    counts[t] = counts.get(t, 0) + 1
    return "%s%d" % (t, counts[t])
# Plain objects that only group others, to keep the Hierarchy short: the coins
# under Rewards, the slimes and spikes under Danger.
REWARDS, DANGER = uid(802), uid(803)
objects.append({"id": REWARDS, "parent": uid(1), "name": "Rewards"})
objects.append({"id": DANGER, "parent": uid(1), "name": "Danger"})
def under(group, name, type_name, x, y):
    place(name, type_name, x, y)["parent"] = group
start = flag = None
for r in range(H):
    for c in range(W):
        ch = LEVEL[r][c]
        cx, cy = c * CELL + 9, r * CELL + 9
        if ch == "c": under(REWARDS, numbered("Coin"), "Coin", cx, cy)
        elif ch == "s": under(DANGER, numbered("Spikes"), "Spikes", cx, cy)
        elif ch == "S": under(DANGER, numbered("Slime"), "Slime", cx, (r + 1) * CELL - 12)
        elif ch == "F": flag = (cx, cy)
        elif ch == "P": start = (cx, (r + 1) * CELL - 12)
# The flag and the player after the groups, so they are drawn in front of them.
place("Flag1", "Flag", flag[0], flag[1])
place("Player1", "Player", start[0], start[1])
# The camera follows the player, kept inside the level, and is the view from the start.
place("Camera1", "Camera", start[0], 90, target="Player1", smoothing=0.12, keepInBounds=True,
      boundsLeft=0, boundsTop=0, boundsRight=LEVEL_W, boundsBottom=H * CELL, currentAtStart=True)
# The HUD: a Layer fixed to the screen, its children placed in the game's own pixels from the view's top-left.
objects.append({"id": uid(801), "parent": uid(1), "name": "HUD", "type": "Layer", "parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
for name, t, x, y in [("CoinIcon1", "CoinIcon", 12, 12), ("CoinCount1", "CoinCount", 22, 6), ("WinSign1", "WinSign", 110, 70)]:
    place(name, t, x, y)["parent"] = uid(801)
write("scenes/Level.scene.json", {"schemaVersion": 3, "objects": objects})

# ── the rules ──
def lit(v, kind=None):
    p = {"type": "literal", "value": v}
    if kind: p["valueKind"] = kind
    return p
def s(v): return lit(v, "string")
def b(v): return lit(v, "bool")
def value(scope, cls, name, *params, **k):
    return dict({"type": "value", "scope": scope, "className": cls, "name": name, "params": list(params), "returnType": "Float"}, **k)
def line(scope, cls, name, *params, **k):
    return dict({"scope": scope, "className": cls, "name": name, "params": list(params)}, **k)
def comp(scope, cls, name, *params, **k):
    return line(scope, cls, name, *params, onComponent=True, **k)
def inp(command): return line("input", "Input", "isActionOn", s(command))
def rule(conditions, actions, sub=()):
    return {"conditions": conditions, "actions": actions, "subRules": list(sub)}
EQ, NE, LT, LE, GT, GE = 0, 1, 2, 3, 4, 5
# Values read off the sheet's own object are scoped "self": a rule with no Player condition has no Player picked.
player_x = value("self", "Node", "getPositionX")
facing = value("self", "Platformer", "getFacing", onComponent=True)
coins = value("variables", "Variables", "getVariable", s("coins"))

player_rules = [
    rule([inp("Move Left")], [comp("Player", "Platformer", "moveLeft")]),
    rule([inp("Move Right")], [comp("Player", "Platformer", "moveRight")]),
    rule([inp("Jump")], [comp("Player", "Platformer", "jump")]),
    rule([inp("Move Down")], [comp("Player", "Platformer", "holdDown")]),
    # Animation from the Platformer's state: a jump, a landing, running or standing.
    rule([comp("Player", "Platformer", "onJumped")], [line("Player", "Sprite", "setAnimation", s("jump")), line("audio", "Audio", "playSound", s("jump"))]),
    rule([comp("Player", "Platformer", "onStartedFalling")], [line("Player", "Sprite", "setAnimation", s("jump"))]),
    rule([comp("Player", "Platformer", "onLanded")], [line("Player", "Sprite", "setAnimation", s("idle"))]),
    rule([comp("Player", "Platformer", "isOnFloor"), comp("Player", "Platformer", "isMoving"), line("Player", "Sprite", "isAnimationPlaying", s("walk"), **{"not": True})],
         [line("Player", "Sprite", "setAnimation", s("walk"))]),
    rule([comp("Player", "Platformer", "isOnFloor"), comp("Player", "Platformer", "isMoving", **{"not": True}), line("Player", "Sprite", "isAnimationPlaying", s("idle"), **{"not": True})],
         [line("Player", "Sprite", "setAnimation", s("idle"))]),
    rule([line("system", "System", "compare", facing, lit(EQ), lit(-1))], [line("self", "Node", "setMirrored", b(True))]),
    rule([line("system", "System", "compare", facing, lit(EQ), lit(1))], [line("self", "Node", "setMirrored", b(False))]),
    # Coins: the one touched goes, the count goes up and the HUD shows it.
    rule([line("Player", "Node", "onCollisionStarted", s("Coin"))],
         [line("Coin", "Node", "queueDestroy"), line("variables", "Variables", "addToVariable", s("coins"), lit(1)),
          line("CoinCount", "Label", "setNumber", coins), line("audio", "Audio", "playSound", s("coin"))]),
    # A slime: landed on, it is squashed and the player bounces; walked into, the player goes back to the start.
    rule([line("Player", "Node", "onCollisionStartedShapes", s("Slime"), s("body"), s("head"))],
         [line("Slime", "Sprite", "setAnimation", s("squashed")), line("Slime", "Node", "setCollisionEnabled", b(False)),
          comp("Slime", "Patrol", "stop"), comp("Player", "Platformer", "jump"), line("audio", "Audio", "playSound", s("stomp"))]),
    rule([line("Player", "Node", "onCollisionStartedShapes", s("Slime"), s("body"), s("body"))],
         [line("Player", "Node", "setPosition", lit(start[0]), lit(start[1])), line("audio", "Audio", "playSound", s("hurt"))]),
    rule([line("Player", "Node", "onCollisionStarted", s("Spikes"))],
         [line("Player", "Node", "setPosition", lit(start[0]), lit(start[1])), line("audio", "Audio", "playSound", s("hurt"))]),
    # The flag: the sign shows, the player stops, and a better coin count than the saved best is kept.
    rule([line("Player", "Node", "onCollisionStarted", s("Flag"))],
         [line("WinSign", "Node", "show"), comp("Player", "Platformer", "setEnabled", b(False)), line("audio", "Audio", "playSound", s("win"))],
         [rule([line("system", "System", "compare", coins, lit(GT), value("system", "System", "savedNumber", s("best")))],
               [line("system", "System", "saveNumber", s("best"), coins)])]),
]
write("events/PlayerRules.vscript.json", {"rules": player_rules, "vars": []})
slime_rules = [
    rule([line("Slime", "Sprite", "onAnimationFinished")], [line("Slime", "Node", "queueDestroy")]),
    rule([comp("Slime", "Patrol", "isHeadingOut")], [line("Slime", "Node", "setMirrored", b(False))]),
    rule([comp("Slime", "Patrol", "isHeadingOut", **{"not": True})], [line("Slime", "Node", "setMirrored", b(True))]),
]
write("events/SlimeRules.vscript.json", {"rules": slime_rules, "vars": []})

write("project.json", {"schemaVersion": 2, "name": "Platformer demo", "entryScene": "scenes/Level.scene.json",
    "collisionLayers": {"1": "Player", "2": "Pickup", "3": "Ground", "4": "Enemy", "5": "Hazard"},
    "display": {"width": 320, "height": 180, "windowWidth": 1280, "windowHeight": 720, "presentMode": "fit", "displayMode": "windowed", "autoResize": True, "wholeWindowScale": True},
    "physics": {"engine": "arcade", "gravity": 700}})
write("README.md", """# Platformer demo

A small complete platform game: run and jump with the arrow keys or WASD and
Space, collect the coins, squash the slimes by landing on them, mind the
spikes, and reach the flag. Your best coin count is saved.

Built on the **Platformer** behaviour and a tilemap level. A **Camera** follows
the player and keeps inside the level; the sky sits on a **Layer** that follows
four tenths of the camera's movement, and the coin count on a Layer fixed to
the screen. Every rule is in `events/PlayerRules` and `events/SlimeRules`; the
level is painted in `scenes/Level`.

Art and sounds by [Kenney](https://kenney.nl) (Pixel Platformer, Digital
Audio, Impact Sounds), CC0. Generated by `tools/make-platformer-demo.py`.
""")
print("wrote", out, "with", len(cells), "ground cells,", len(objects), "objects")
