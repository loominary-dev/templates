"""The Dungeon demo, generated from Kenney's Tiny Dungeon pack: six rooms seen
from above, each its own scene, changed by a Scene Manager that lives in a
singleton scene with the player, the HUD and the lantern. Bats that chase, spiders and rats on patrol,
arrows from a pool, a dark room lit by a lantern and two braziers, a key, a
locked door and a chest. Made by this script rather than by hand, so a format
change is a re-run.

    python3 tools/make-dungeon-demo.py <kenney tiny-dungeon dir> <kenney digital-audio dir> <kenney impact-sounds dir> [demos/dungeon]

The packs: https://kenney.nl/assets/tiny-dungeon, /digital-audio and
/impact-sounds, all CC0. The key, the heart, the flame and the glow are drawn
here. Needs Pillow.
"""
import base64, json, math, os, shutil, struct, sys
from PIL import Image

td, da, im = sys.argv[1], sys.argv[2], sys.argv[3]
out = os.path.abspath(sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(__file__), "..", "demos", "dungeon"))
shutil.rmtree(out, ignore_errors=True)
for d in ["assets/art", "assets/sounds", "assets/tiles", "scenes/singletons", "events"]: os.makedirs(os.path.join(out, d))

def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

def uid(n):  # stable ids, so a re-run changes nothing that did not change
    return "d1000000-0000-4000-8000-%012d" % n

# ── art ──
TILES = "tilemap_packed.png"
shutil.copy(os.path.join(td, "Tilemap", TILES), os.path.join(out, "assets", "art", TILES))
sheet = Image.open(os.path.join(td, "Tilemap", TILES)).convert("RGBA")
T = 16
def tile(i): return sheet.crop(((i % 12) * T, (i // 12) * T, (i % 12) * T + T, (i // 12) * T + T))

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

def sprite(name, w, h, animations, collision):
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

def drawn(rows, colours):
    """A small picture from rows of characters, one colour per character, '.' clear."""
    img = Image.new("RGBA", (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".": img.putpixel((x, y), colours[ch])
    return img

GOLD = {"o": (35, 25, 25, 255), "g": (240, 196, 72, 255), "y": (255, 235, 140, 255)}
key_img = drawn([
    "................",
    "................",
    "................",
    "..oooo..........",
    ".oggggo.........",
    "oggyyggoooooooo.",
    "ogy..ygggggggggo",
    "ogy..ygooogooggo",
    "oggyyggo..o.oo..",
    ".oggggo.........",
    "..oooo..........",
    "................",
    "................",
    "................",
    "................",
    "................"], GOLD)
heart_img = drawn([
    "................",
    "................",
    "..ooo....ooo....",
    ".orrro..orrro...",
    "orrwrrooorrrro..",
    "orwrrrrrrrrrro..",
    "orrrrrrrrrrrro..",
    ".orrrrrrrrrro...",
    "..orrrrrrrro....",
    "...orrrrrro.....",
    "....orrrro......",
    ".....orro.......",
    "......oo........",
    "................",
    "................",
    "................"], {"o": (35, 25, 25, 255), "r": (228, 72, 77, 255), "w": (255, 190, 190, 255)})
FIRE = {"o": (60, 30, 20, 255), "r": (230, 80, 40, 255), "y": (255, 200, 70, 255), "w": (255, 245, 200, 255), "s": (110, 110, 125, 255)}
flame1 = drawn([
    "................", "................", ".......r........", "......ry........", "......ryr.......", ".....ryyr.......",
    ".....rywyr......", "....ryywyr......", "....rywwyr......", ".....ryyr.......", "..ssssssssssss..", "..sooooooooooos.",
    "...ssssssssss...", "....s......s....", "....s......s....", "...ss......ss..."], FIRE)
flame2 = drawn([
    "................", "................", "........r.......", ".......yr.......", "......ryr.......", "......ryyr......",
    ".....rywyr......", ".....rywyyr.....", "....ryywwyr.....", ".....ryyr.......", "..ssssssssssss..", "..sooooooooooos.",
    "...ssssssssss...", "....s......s....", "....s......s....", "...ss......ss..."], FIRE)

def glow(size):
    """A soft round light: white, its alpha falling off from the middle."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            if d < 1: img.putpixel((x, y), (255, 255, 255, int(255 * (1 - d) ** 1.6)))
    return img

pillar = Image.new("RGBA", (16, 32))
pillar.paste(tile(6), (0, 0)); pillar.paste(tile(18), (0, 16))
arrow = tile(131).rotate(-90)  # the pack's points up; a Bullet's heading 0 is right

# The player collides by its feet, so a doorway one cell wide is easy to walk through.
sprite("Player", 16, 16, [("idle", [tile(112)], 400, "loop")], [box("body", 8, 8, 10, 8)])
sprite("Bat", 16, 16, [("fly", [tile(120)], 400, "loop")], [box("body", 8, 8, 12, 10, sensor=True)])
sprite("Spider", 16, 16, [("walk", [tile(122)], 400, "loop")], [box("body", 8, 9, 12, 10, sensor=True)])
sprite("Rat", 16, 16, [("run", [tile(123)], 400, "loop")], [box("body", 8, 10, 12, 8, sensor=True)])
sprite("Arrow", 16, 16, [("fly", [arrow], 400, "loop")], [box("tip", 8, 8, 8, 4)])
sprite("Key", 16, 16, [("still", [key_img], 400, "loop")], [box("key", 8, 7, 14, 8, sensor=True)])
sprite("Potion", 16, 16, [("still", [tile(115)], 400, "loop")], [box("potion", 8, 9, 8, 10, sensor=True)])
sprite("Heart", 16, 16, [("still", [heart_img], 400, "loop")], [])
sprite("Chest", 16, 16, [("shut", [tile(89)], 400, "loop"), ("open", [tile(91)], 400, "loop")], [box("chest", 8, 9, 14, 12, sensor=True)])
sprite("Sign", 16, 16, [("still", [tile(66)], 400, "loop")], [box("sign", 8, 9, 12, 12)])
sprite("LockedDoor", 16, 16, [("shut", [tile(45)], 400, "loop")], [box("door", 8, 8, 16, 16), box("lock", 8, 8, 22, 22, sensor=True)])
sprite("Pillar", 16, 32, [("still", [pillar], 400, "loop")], [box("base", 8, 24, 14, 14, occluder=1)])
sprite("Brazier", 16, 16, [("burn", [flame1, flame2], 160, "loop")], [box("base", 8, 12, 12, 6)])
sprite("Glow", 96, 96, [("still", [glow(96)], 400, "loop")], [])

# ── sounds ──
SOUNDS = {"shoot": (da, "laser4.ogg"), "hit": (im, "impactPunch_medium_000.ogg"), "hurt": (im, "impactGeneric_light_004.ogg"),
          "key": (da, "powerUp2.ogg"), "unlock": (im, "impactMetal_light_000.ogg"), "potion": (da, "powerUp7.ogg"), "win": (da, "threeTone1.ogg")}
assets = []
for n, (key, (pack, f)) in enumerate(SOUNDS.items()):
    shutil.copy(os.path.join(pack, "Audio", f), os.path.join(out, "assets", "sounds", key + ".ogg"))
    assets.append({"uuid": uid(900 + n), "key": key, "path": "assets/sounds/%s.ogg" % key})
write("assets.json", {"schemaVersion": 1, "assets": assets})

# ── collision layers, as bits ──
PLAYER, SOLID, ENEMY, ARROW, PICKUP, DOOR = 1, 2, 4, 8, 16, 32
EVERYTHING = -1

def type_json(base, defaults, components=()):
    write(defaults.get("_name") + ".type.json", {"schemaVersion": 2, "baseClass": base,
        "defaults": {k: v for k, v in defaults.items() if k != "_name"}, "components": list(components)})

type_json("Sprite", {"_name": "Player", "spriteKey": "Player.sprite.json",
                     "collision": {"layer": PLAYER, "mask": SOLID | ENEMY | PICKUP | DOOR}},
          [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"},
           {"componentClass": "TopDownMovement", "maxSpeed": 90, "acceleration": 900, "deceleration": 1200, "face": "Mirror"},
           {"componentClass": "Health", "max": 3, "current": 3},
           {"componentClass": "PlayerRules"}])
type_json("Sprite", {"_name": "Arrow", "spriteKey": "Arrow.sprite.json", "collision": {"layer": ARROW, "mask": SOLID | ENEMY}},
          [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"},
           {"componentClass": "Bullet", "speed": 220, "range": 150}])
type_json("Sprite", {"_name": "Bat", "spriteKey": "Bat.sprite.json", "collision": {"layer": ENEMY, "mask": PLAYER | ARROW}},
          [{"componentClass": "Follow", "speed": 45, "stopWithin": 0}, {"componentClass": "Health", "max": 1, "current": 1},
           {"componentClass": "EnemyRules"}, {"componentClass": "BatRules"}])
type_json("Sprite", {"_name": "Spider", "spriteKey": "Spider.sprite.json", "collision": {"layer": ENEMY, "mask": PLAYER | ARROW}},
          [{"componentClass": "Patrol", "axis": "Horizontal", "distance": 64, "speed": 30}, {"componentClass": "Health", "max": 3, "current": 3},
           {"componentClass": "EnemyRules"}])
type_json("Sprite", {"_name": "Rat", "spriteKey": "Rat.sprite.json", "collision": {"layer": ENEMY, "mask": PLAYER | ARROW}},
          [{"componentClass": "Patrol", "axis": "Vertical", "distance": 96, "speed": 55}, {"componentClass": "Health", "max": 1, "current": 1},
           {"componentClass": "EnemyRules"}])
type_json("Sprite", {"_name": "Key", "spriteKey": "Key.sprite.json", "collision": {"layer": PICKUP, "mask": PLAYER}}, [{"componentClass": "KeyRules"}])
type_json("Sprite", {"_name": "Potion", "spriteKey": "Potion.sprite.json", "collision": {"layer": PICKUP, "mask": PLAYER}})
type_json("Sprite", {"_name": "Chest", "spriteKey": "Chest.sprite.json", "collision": {"layer": PICKUP, "mask": PLAYER}})
type_json("Sprite", {"_name": "Sign", "spriteKey": "Sign.sprite.json", "collision": {"layer": SOLID, "mask": EVERYTHING}})
type_json("Sprite", {"_name": "LockedDoor", "spriteKey": "LockedDoor.sprite.json", "collision": {"layer": SOLID | DOOR, "mask": EVERYTHING}},
          [{"componentClass": "DoorRules"}])
type_json("Sprite", {"_name": "Pillar", "spriteKey": "Pillar.sprite.json", "collision": {"layer": SOLID, "mask": EVERYTHING}})
type_json("Sprite", {"_name": "Brazier", "spriteKey": "Brazier.sprite.json", "collision": {"layer": SOLID, "mask": EVERYTHING}})
type_json("Node", {"_name": "Doorway", "collision": {"layer": DOOR, "mask": PLAYER, "shapes": [box("way", 0, 0, 14, 14, sensor=True)]}})
type_json("Node", {"_name": "Marker"})
type_json("Light", {"_name": "Lantern", "spriteKey": "Glow.sprite.json", "tint": 0xFFD9A0, "opacity": 0.55, "scaleX": 1.3, "scaleY": 1.3, "radius": 2, "lightHeight": 12})
type_json("Light", {"_name": "FireLight", "spriteKey": "Glow.sprite.json", "tint": 0xFF9A40, "scaleX": 1.4, "scaleY": 1.4, "radius": 3, "lightHeight": 16})
type_json("Sprite", {"_name": "HeartIcon", "spriteKey": "Heart.sprite.json"})
type_json("Sprite", {"_name": "KeyIcon", "spriteKey": "Key.sprite.json"})
for counter in ["HealthCount", "KeyCount", "TimeLabel"]:
    type_json("Label", {"_name": counter, "text": "0", "fontSize": 10})
type_json("Label", {"_name": "WinSign", "text": "You found the treasure!", "fontSize": 14, "visible": False})
# The Scene Manager: changes what Scenery holds, with a short fade.
type_json("SceneManager", {"_name": "Rooms", "transition": "Fade", "fadeTime": 0.2})

# ── the tiles: walls solid and casting shadows, floors open ──
WALLS = [40, 57, 58, 59]
FLOORS = [48, 48, 48, 49, 42, 48, 50]
tiles = []
for i in range(132):
    t = {"id": i, "x": (i % 12) * T, "y": (i // 12) * T, "collision": []}
    if i in WALLS: t["collision"] = [{"kind": "box", "cx": 8, "cy": 8, "w": T, "h": T, "occluder": 1}]
    tiles.append(t)
write("assets/tiles/Dungeon.tileset.json", {"schemaVersion": 1, "image": "assets/art/" + TILES, "tileWidth": T, "tileHeight": T,
    "tiles": tiles})

# ── the rooms ──
# 20 × 11 cells of 16 px, centred on the world's origin, which is the screen's
# middle: one room is one screen. '#' wall, '.' floor, 'D' a doorway in the
# wall, 'L' the locked door, 'e' where a player arrives after dying, and one
# letter per thing: b bat, x spider, r rat, k key, h potion, C chest, S sign,
# o pillar, f brazier.
ROOMS = {
    "Entrance": ["####################",
                 "#..................#",
                 "#..................#",
                 "#....S.............#",
                 "#..................#",
                 "#..e...............D",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "####################"],
    "BatHall": ["####################",
                "#..................#",
                "#...b.......b......#",
                "#..................#",
                "#........b.........#",
                "D.........e........D",
                "#..................#",
                "#..##..........##..#",
                "#..##..........##..#",
                "#..................#",
                "#########D##########"],
    "DarkRoom": ["####################",
                 "#..................#",
                 "#....o.......o.....#",
                 "#........f.........#",
                 "#..................#",
                 "D.e.........x...k..#",
                 "#..................#",
                 "#....o...f...o.....#",
                 "#..................#",
                 "#..................#",
                 "####################"],
    "Crossing": ["#########D##########",
                 "#..................#",
                 "#....r.......r.....#",
                 "#..................#",
                 "#..................#",
                 "D.........e.......LD",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "####################"],
    "Armoury": ["####################",
                "#..................#",
                "#..x...............#",
                "#..........##......#",
                "#..........##..h...#",
                "#..............e...D",
                "#....x.............#",
                "#..................#",
                "#..................#",
                "#..................#",
                "####################"],
    "Treasury": ["####################",
                 "#..................#",
                 "#..................#",
                 "#.........C........#",
                 "#..................#",
                 "D..e...............#",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "#..................#",
                 "####################"],
}
# Who is through each side's doorway.
NEIGHBOURS = {
    "Entrance": {"east": "BatHall"},
    "BatHall": {"west": "Entrance", "east": "DarkRoom", "south": "Crossing"},
    "DarkRoom": {"west": "BatHall"},
    "Crossing": {"north": "BatHall", "west": "Armoury", "east": "Treasury"},
    "Armoury": {"east": "Crossing"},
    "Treasury": {"west": "Crossing"},
}
ROWS, COLS = 11, 20
LEFT, TOP = -COLS * T // 2, -ROWS * T // 2
centre = lambda c, r: (LEFT + c * T + T // 2, TOP + r * T + T // 2)
THINGS = {"b": "Bat", "x": "Spider", "r": "Rat", "k": "Key", "h": "Potion", "C": "Chest", "S": "Sign", "L": "LockedDoor", "f": "Brazier"}

def side(c, r):
    return "west" if c == 0 else "east" if c == COLS - 1 else "north" if r == 0 else "south"

def inward(c, r):
    return (1, 0) if c == 0 else (-1, 0) if c == COLS - 1 else (0, 1) if r == 0 else (0, -1)

for room, rows in ROOMS.items():
    assert len(rows) == ROWS and all(len(row) == COLS for row in rows), room
    dark = room == "DarkRoom"
    root = uid(1)
    objects = [{"id": root, "name": room}]
    cells, n = [], [10]
    for r in range(ROWS):
        for c in range(COLS):
            ch = rows[r][c]
            cells.append([c, r, WALLS[(c * 7 + r * 3) % 4] if ch == "#" else FLOORS[(c * 5 + r * 11) % len(FLOORS)]])
    tint = {"tint": 0x2E2A38} if dark else {}
    # The walls' collision filter is the tile map's own: on the Walls layer, meeting everything.
    objects.append(dict({"id": uid(2), "parent": root, "name": "Floor", "type": "Tilemap", "tilesetKey": "assets/tiles/Dungeon.tileset.json",
                         "x": LEFT, "y": TOP, "cellWidth": T, "cellHeight": T, "cells": cells, "collisionLayer": SOLID, "collisionMask": EVERYTHING}, **tint))
    def place(name, type_name, x, y, **extra):
        n[0] += 1
        o = dict({"id": uid(n[0]), "parent": root, "name": name, "type": type_name, "x": x, "y": y}, **extra)
        objects.append(o)
        return o
    counts = {}
    for r in range(ROWS):
        for c in range(COLS):
            ch = rows[r][c]
            x, y = centre(c, r)
            if ch == "D":
                to = NEIGHBOURS[room][side(c, r)]
                # Named after the room it leads to: the player's rule passes that name to Change scene.
                place(to, "Doorway", x, y)
                dx, dy = inward(c, r)
                # Where a player coming from that room arrives, a step inside.
                place("From" + to, "Marker", x + dx * T, y + dy * T)
            elif ch == "e":
                place("Entry", "Marker", x, y)
            elif ch == "o":
                counts["Pillar"] = counts.get("Pillar", 0) + 1
                place("Pillar%d" % counts["Pillar"], "Pillar", x, y - T // 2)
            elif ch in THINGS:
                t = THINGS[ch]
                counts[t] = counts.get(t, 0) + 1
                place("%s%d" % (t, counts[t]), t, x, y)
                if t == "Brazier": place("FireLight%d" % counts[t], "FireLight", x, y - 4)
    write("scenes/%s.scene.json" % room, {"schemaVersion": 3, "objects": objects})

# ── the singleton: the Scene Manager, the player and the HUD, loaded once and kept ──
ex, ey = centre(3, 5)
game = [
    {"id": uid(1), "name": "Game"},
    {"id": uid(2), "parent": uid(1), "name": "Rooms1", "type": "Rooms"},
    {"id": uid(3), "parent": uid(1), "name": "Player1", "type": "Player", "x": ex, "y": ey},
    {"id": uid(4), "parent": uid(3), "name": "Lantern1", "type": "Lantern", "x": 0, "y": 0, "visible": False},
    # The HUD: a Layer fixed to the screen, its children in the game's own pixels from the view's top-left.
    {"id": uid(5), "parent": uid(1), "name": "HUD", "type": "Layer", "parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False},
    {"id": uid(6), "parent": uid(5), "name": "HeartIcon1", "type": "HeartIcon", "x": 12, "y": 12},
    {"id": uid(7), "parent": uid(5), "name": "HealthCount1", "type": "HealthCount", "x": 22, "y": 6, "text": "3"},
    {"id": uid(8), "parent": uid(5), "name": "KeyIcon1", "type": "KeyIcon", "x": 12, "y": 28},
    {"id": uid(9), "parent": uid(5), "name": "KeyCount1", "type": "KeyCount", "x": 22, "y": 22},
    {"id": uid(10), "parent": uid(5), "name": "WinSign1", "type": "WinSign", "x": 74, "y": 70},
    {"id": uid(11), "parent": uid(5), "name": "TimeLabel1", "type": "TimeLabel", "x": 140, "y": 92, "visible": False},
]
write("scenes/singletons/Game.scene.json", {"schemaVersion": 3, "objects": game})

# ── the rules ──
def lit(v, kind=None):
    p = {"type": "literal", "value": v}
    if kind: p["valueKind"] = kind
    return p
def s(v): return lit(v, "string")
def b(v): return lit(v, "bool")
def value(scope, cls, name, *params, **k):
    return dict({"type": "value", "scope": scope, "className": cls, "name": name, "params": list(params), "returnType": "Float"}, **k)
def op(o, left, right): return {"type": "op", "op": o, "left": left, "right": right}
def line(scope, cls, name, *params, **k):
    return dict({"scope": scope, "className": cls, "name": name, "params": list(params)}, **k)
def comp(scope, cls, name, *params, **k):
    return line(scope, cls, name, *params, onComponent=True, **k)
def sheet(name, *params, **k): return line("system", "VisualScriptComponent", name, *params, **k)
def once(): return sheet("triggerOnce")
def inp(command): return line("input", "Input", "isActionOn", s(command))
def pressed(command): return line("input", "Input", "isActionPressed", s(command))
def var(name): return value("variables", "Variables", "getVariable", s(name))
def rule(conditions, actions, sub=()):
    return {"conditions": conditions, "actions": actions, "subRules": list(sub)}
EQ, NE, LT, LE, GT, GE = 0, 1, 2, 3, 4, 5
def compare(left, o, right): return line("system", "System", "compare", left, lit(o), right)

me_x, me_y = value("self", "Node", "getPositionX"), value("self", "Node", "getPositionY")
facing = value("self", "TopDownMovement", "facingAngle", onComponent=True)
health = value("self", "Health", "health", onComponent=True)
away = lambda t: op("+", value("self", "Node", "angleToNearest", s(t)), lit(180))
touched = value("Doorway", "Node", "overlappingObject", returnType="String")

def hurt_by(t):
    return rule([line("Player", "Node", "onCollisionStarted", s(t))],
                [comp("Player", "Health", "damage", lit(1)), comp("Player", "TopDownMovement", "push", away(t), lit(180)),
                 line("audio", "Audio", "playSound", s("hurt"))])

player_rules = [
    # Arrows wait in a pool: Create takes one, a Bullet's end puts it back.
    rule([line("Player", "Node", "onCreated")], [sheet("keepReady", s("Arrow"), lit(8))]),
    rule([inp("Move Left")], [comp("Player", "TopDownMovement", "moveLeft")]),
    rule([inp("Move Right")], [comp("Player", "TopDownMovement", "moveRight")]),
    rule([inp("Move Up")], [comp("Player", "TopDownMovement", "moveUp")]),
    rule([inp("Move Down")], [comp("Player", "TopDownMovement", "moveDown")]),
    rule([pressed("Shoot"), comp("Player", "TopDownMovement", "isBeingPushed", **{"not": True})],
         [sheet("createObject", s("Arrow"), lit(1)), line("Arrow", "Node", "setPosition", me_x, me_y),
          comp("Arrow", "Bullet", "setHeading", facing), line("audio", "Audio", "playSound", s("shoot"))]),
    # The game starts with the player at the first room's Entry, whichever room that is.
    rule([line("Player", "Node", "onCreated")], [line("Rooms", "SceneManager", "place", s("Player1"), s("Entry"))]),
    # A doorway is named after the room it leads to; the player arrives at the marker named after the room it left.
    # Place waits for the room to arrive. Not while a change is under way: the player is still in the doorway.
    rule([line("Player", "Node", "onCollisionStarted", s("Doorway")), line("Rooms", "SceneManager", "isChanging", **{"not": True})],
         [line("Rooms", "SceneManager", "changeScene", touched),
          line("Rooms", "SceneManager", "place", s("Player1"), op("+", s("From"), value("Rooms", "SceneManager", "currentScene", returnType="String")))]),
    hurt_by("Bat"), hurt_by("Spider"), hurt_by("Rat"),
    rule([line("Player", "Node", "onCollisionStarted", s("Key"))],
         [line("variables", "Variables", "addToVariable", s("keys"), lit(1)), line("variables", "Variables", "setVariable", s("gotKey"), lit(1)),
          line("Key", "Node", "queueDestroy"), line("audio", "Audio", "playSound", s("key"))]),
    rule([line("Player", "Node", "onCollisionStarted", s("LockedDoor")), compare(var("keys"), GT, lit(0))],
         [line("variables", "Variables", "addToVariable", s("keys"), lit(-1)), line("variables", "Variables", "setVariable", s("doorOpen"), lit(1)),
          line("LockedDoor", "Node", "queueDestroy"), line("audio", "Audio", "playSound", s("unlock"))]),
    rule([line("Player", "Node", "onCollisionStarted", s("Potion"))],
         [comp("Player", "Health", "heal", lit(1)), line("Potion", "Node", "queueDestroy"), line("audio", "Audio", "playSound", s("potion"))]),
    rule([line("Player", "Node", "onCollisionStarted", s("Chest")), once()],
         [line("Chest", "Sprite", "setAnimation", s("open")), line("WinSign", "Node", "show"), line("TimeLabel", "Node", "show"), line("TimeLabel", "Label", "setNumber", var("time")),
          comp("Player", "TopDownMovement", "setEnabled", b(False)), line("variables", "Variables", "setVariable", s("won"), lit(1)),
          line("audio", "Audio", "playSound", s("win"))],
         [rule([line("system", "System", "isSaved", s("best"), **{"not": True})], [line("system", "System", "saveNumber", s("best"), var("time"))]),
          rule([compare(var("time"), LT, value("system", "System", "savedNumber", s("best")))], [line("system", "System", "saveNumber", s("best"), var("time"))])]),
    # Dying: the room it died in, loaded afresh; the player arrives at its Entry, whole again.
    rule([comp("Player", "Health", "isDead"), once()],
         [comp("Player", "Health", "restore"), line("Rooms", "SceneManager", "changeScene", value("Rooms", "SceneManager", "currentScene", returnType="String")),
          line("Rooms", "SceneManager", "place", s("Player1"), s("Entry"))]),
    # The time, and the HUD.
    rule([compare(var("won"), EQ, lit(0))], [line("variables", "Variables", "addToVariable", s("time"), value("system", "System", "getDeltaTime"))]),
    rule([], [line("HealthCount", "Label", "setNumber", health), line("KeyCount", "Label", "setNumber", var("keys"))]),
    # The lantern is lit only in the dark room.
    rule([line("Rooms", "SceneManager", "isLoaded", s("DarkRoom"))], [line("Lantern", "Node", "show")]),
    rule([line("Rooms", "SceneManager", "isLoaded", s("DarkRoom"), **{"not": True})], [line("Lantern", "Node", "hide")]),
]
write("events/PlayerRules.vscript.json", {"rules": player_rules, "vars": []})

enemy_rules = [
    rule([line("self", "Node", "onCollisionStarted", s("Arrow"))],
         [comp("self", "Health", "damage", lit(1)), comp("Arrow", "Bullet", "endNow"), line("audio", "Audio", "playSound", s("hit"))]),
    rule([comp("self", "Health", "isDead")], [line("self", "Node", "queueDestroy")]),
]
write("events/EnemyRules.vscript.json", {"rules": enemy_rules, "vars": []})
bat_rules = [
    rule([line("self", "Node", "isWithinDistanceOf", s("Player"), lit(80)), once()], [comp("self", "Follow", "follow", s("Player1"))]),
]
write("events/BatRules.vscript.json", {"rules": bat_rules, "vars": []})
# A room is built afresh each visit: the key and the door remember, through a variable, that they are gone.
write("events/KeyRules.vscript.json", {"rules": [rule([line("self", "Node", "onCreated"), compare(var("gotKey"), EQ, lit(1))], [line("self", "Node", "queueDestroy")])], "vars": []})
write("events/DoorRules.vscript.json", {"rules": [rule([line("self", "Node", "onCreated"), compare(var("doorOpen"), EQ, lit(1))], [line("self", "Node", "queueDestroy")])], "vars": []})

def keys(*codes): return {"bindings": [{"kind": "key", "code": c} for c in codes]}
write("project.json", {"schemaVersion": 2, "name": "Dungeon demo", "entryScene": "scenes/Entrance.scene.json",
    "singletons": ["scenes/singletons/Game.scene.json"],
    "collisionLayers": {"1": "Player", "2": "Walls", "3": "Enemy", "4": "Arrow", "5": "Pickup", "6": "Door"},
    "input": {"Move Left": keys(37, 65), "Move Right": keys(39, 68), "Move Up": keys(38, 87), "Move Down": keys(40, 83),
              "Shoot": keys(32, 74), "Pause": keys(27)},
    "display": {"width": 320, "height": 180, "windowWidth": 1280, "windowHeight": 720, "presentMode": "fit", "displayMode": "windowed", "autoResize": True, "wholeWindowScale": True},
    "physics": {"engine": "arcade", "gravity": 0}})
write("README.md", """# Dungeon demo

Six rooms seen from above. Walk with the arrow keys or WASD and shoot with
Space or J. Bats chase you once you are close, spiders and rats keep to
their rounds. The key is in the dark room; the locked door is in the
Crossing, and the chest behind it. Your best time is saved.

Each room is its own scene, and the game starts in the Entrance. The
singleton scene `scenes/singletons/Game` is loaded once beside the rooms and
kept: it holds the **Rooms** Scene Manager, the player with its lantern, and
the HUD on a screen-fixed Layer. Walking through a doorway runs **Change
scene** with the doorway's name and **Place** with the marker named after
the room it is leaving, so the player arrives a step inside the doorway it
came through. Run any room on its own
and the singleton comes with it.

Built on the **Top-down Movement**, **Bullet**, **Follow**, **Patrol** and
**Health** behaviours. Every rule is in `events/`.

Art and sounds by [Kenney](https://kenney.nl) (Tiny Dungeon, Digital Audio,
Impact Sounds), CC0; the key, heart, brazier and glow are drawn by the
generator. Generated by `tools/make-dungeon-demo.py`.
""")
print("wrote", out)
