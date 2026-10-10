"""The Platformer template, generated from Kenney's Pixel Platformer pack: the
smallest working platform game to start from. A player that runs and jumps,
ground painted as a tile map, a ledge to drop through, a wall to slide down
and jump off, a camera that follows and a sky that slides behind. Made by this
script rather than by hand, so a format change is a re-run.

    python3 tools/make-platformer-template.py <kenney pixel-platformer dir> <kenney digital-audio dir> [templates/platformer]

The packs: https://kenney.nl/assets/pixel-platformer and /digital-audio, both
CC0. Needs Pillow.
"""
import base64, json, os, shutil, struct, sys
from PIL import Image

pp, da = sys.argv[1], sys.argv[2]
out = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "..", "templates", "platformer"))
shutil.rmtree(out, ignore_errors=True)
for d in ["assets/art", "assets/sounds", "assets/tiles", "scenes", "events"]: os.makedirs(os.path.join(out, d))

def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

def uid(n):  # stable ids, so a re-run changes nothing that did not change
    return "a0000000-0000-4000-8000-%012d" % n

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
    """A sprite document: `animations` is [(name, [frame images], duration ms, play mode)], `collision` the shared shapes."""
    layer = next_id()
    anims, cels = [], []
    for aname, frames, duration, mode in animations:
        fids = []
        for f in frames:
            fid = next_id()
            fids.append(fid)
            cels.append({"layerId": layer, "frameId": fid, "pixels": argb(f)})
        anims.append({"id": next_id(), "name": aname, "loop": mode == "loop", "playMode": mode, "repeatTo": 0, "repeatCount": 0,
                      "collision": collision, "points": [], "collisionShared": True, "pointsShared": False,
                      "frames": [{"id": fid, "duration": duration, "pivotX": 0.5, "pivotY": 0.5, "collision": [], "points": []} for fid in fids]})
    write(name + ".sprite.json", {"width": size, "height": height or size, "colorMode": "rgba", "palette": [],
        "layers": [{"id": layer, "name": "Layer 1", "visible": True, "opacity": 1, "locked": False, "blendMode": "normal", "reference": False}],
        "animations": anims, "cels": cels})

def box(name, cx, cy, w, h, **extra):
    return dict({"name": name, "kind": "box", "cx": cx, "cy": cy, "w": w, "h": h}, **extra)

CELL = 18
char = lambda i: region(chars_im, i, 24, 9)
tile = lambda i: region(tiles_im, i, CELL, 20)
sprite("Player", 24, [("idle", [char(0)], 400, "loop"), ("walk", [char(0), char(1)], 150, "loop"), ("jump", [char(1)], 400, "loop")],
       [box("body", 12, 13, 14, 20)])
# A wall: six blocks in a column. A ledge: four planks, the end pieces at its ends.
WALL_H, LEDGE_W = 6, 4
def strip(indices, across):
    img = Image.new("RGBA", (CELL * (len(indices) if across else 1), CELL * (1 if across else len(indices))), (0, 0, 0, 0))
    for k, i in enumerate(indices): img.paste(tile(i), (k * CELL, 0) if across else (0, k * CELL))
    return img
sprite("Wall", CELL, [("still", [strip([6] * WALL_H, False)], 400, "loop")], [box("blocks", 9, WALL_H * 9, CELL, WALL_H * CELL)], height=WALL_H * CELL)
sprite("Ledge", LEDGE_W * CELL, [("still", [strip([48] + [49] * (LEDGE_W - 2) + [50], True)], 400, "loop")],
       [box("planks", LEDGE_W * 9, 3, LEDGE_W * CELL, 6)], height=CELL)

# ── sound ──
shutil.copy(os.path.join(da, "Audio", "phaseJump1.ogg"), os.path.join(out, "assets", "sounds", "jump.ogg"))
write("assets.json", {"schemaVersion": 1, "assets": [{"uuid": uid(900), "key": "jump", "path": "assets/sounds/jump.ogg"}]})

# ── collision layers, as bits ──
PLAYER, SOLID = 1, 4

# ── Types ──
def type_json(base, defaults, components=()):
    write(defaults.get("_name") + ".type.json", {"schemaVersion": 2, "baseClass": base,
        "defaults": {k: v for k, v in defaults.items() if k != "_name"}, "components": list(components)})

type_json("Sprite", {"_name": "Player", "spriteKey": "Player.sprite.json", "collision": {"layer": PLAYER, "mask": -1}},
          [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"},
           {"componentClass": "Platformer", "maxSpeed": 110, "acceleration": 900, "deceleration": 1200, "jumpStrength": 330, "jumpCut": 0.6,
            "coyoteTime": 0.1, "jumpBuffer": 0.1, "floorSnap": 3, "wallSlideSpeed": 60, "wallJump": True, "wallJumpAway": 120},
           {"componentClass": "PlayerRules"}])
type_json("Sprite", {"_name": "Wall", "spriteKey": "Wall.sprite.json", "collision": {"layer": SOLID, "mask": -1}},
          [{"componentClass": "PhysicsBody", "bodyType": "Static"}, {"componentClass": "PlatformerWall"}])
type_json("Sprite", {"_name": "Ledge", "spriteKey": "Ledge.sprite.json", "collision": {"layer": SOLID, "mask": -1}},
          [{"componentClass": "PhysicsBody", "bodyType": "Static"}, {"componentClass": "PlatformerFallThrough"}])

# ── the level ──
# 18 px cells, 10 rows (one screen tall), a little over two screens wide. '#'
# ground, 'L' the left end of a ledge (four planks) to jump up through and drop
# down through, 'W' the top of a wall (six blocks) to slide down and jump off,
# 'P' the player.
LEVEL = [
    "..........................................",
    "..........................................",
    "...............................W..........",
    "..........................................",
    "...........L..............................",
    "..........................L...............",
    "......................L...................",
    "...P..........###.........................",
    "##########################################",
    "##########################################",
]
H, W = len(LEVEL), len(LEVEL[0])
LEVEL_W = W * CELL
solid = lambda c, r: 0 <= r < H and 0 <= c < W and LEVEL[r][c] == "#"
cells = []
for r in range(H):
    for c in range(W):
        if LEVEL[r][c] != "#": continue
        if not solid(c, r - 1):
            t = 20 if not solid(c - 1, r) and not solid(c + 1, r) else 21 if not solid(c - 1, r) else 23 if not solid(c + 1, r) else 22
        else:
            t = [121, 122, 141, 142][(c * 7 + r * 13) % 4]
        cells.append([c, r, t])
tiles = []
for i in range(180):
    t = {"id": i, "x": (i % 20) * CELL, "y": (i // 20) * CELL, "collision": []}
    if i in (20, 21, 22, 23, 121, 122, 141, 142):
        t["collision"] = [{"kind": "box", "cx": 9, "cy": 9, "w": CELL, "h": CELL}]
    tiles.append(t)
write("assets/tiles/Ground.tileset.json", {"schemaVersion": 1, "image": "assets/art/" + TILES, "tileWidth": CELL, "tileHeight": CELL, "tiles": tiles})
# The sky: plain sky, a band of hills, then plain blue, in 24 px cells, past both ends of the level.
BACK = 24
write("assets/tiles/Sky.tileset.json", {"schemaVersion": 1, "image": "assets/art/" + BACKS, "tileWidth": BACK, "tileHeight": BACK,
    "tiles": [{"id": i, "x": (i % 8) * BACK, "y": (i // 8) * BACK, "collision": []} for i in range(24)]})
sky = [[c, r, 0 if r < 2 else 8 + (c % 4) if r == 2 else 16] for c in range(-8, LEVEL_W // BACK + 9) for r in range(8)]

# ── the scene ──
objects = [{"id": uid(1), "name": "Level"},
           # Behind everything: a Layer following four tenths of the camera's sideways movement, holding the sky.
           {"id": uid(2), "parent": uid(1), "name": "Backdrop", "type": "Layer", "parallaxX": 0.4},
           {"id": uid(3), "parent": uid(2), "name": "Sky", "type": "Tilemap", "tilesetKey": "assets/tiles/Sky.tileset.json",
            "cellWidth": BACK, "cellHeight": BACK, "cells": sky},
           # The ground's collision filter is the tile map's own: on the Ground layer, meeting everything.
           {"id": uid(4), "parent": uid(1), "name": "Ground", "type": "Tilemap", "tilesetKey": "assets/tiles/Ground.tileset.json",
            "cellWidth": CELL, "cellHeight": CELL, "cells": cells, "collisionLayer": SOLID, "collisionMask": -1}]
n = [10]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    objects.append(dict({"id": uid(n[0]), "parent": uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra))
counts = {}
start = None
for r in range(H):
    for c in range(W):
        ch = LEVEL[r][c]
        cx, cy = c * CELL + 9, r * CELL + 9
        if ch in "WL":
            t = "Wall" if ch == "W" else "Ledge"
            counts[t] = counts.get(t, 0) + 1
            # Placed by the middle of the picture, which is where its pivot is.
            if t == "Wall": place("Wall%d" % counts[t], t, cx, r * CELL + WALL_H * CELL / 2)
            else: place("Ledge%d" % counts[t], t, c * CELL + LEDGE_W * CELL / 2, cy)
        elif ch == "P":
            start = (cx, (r + 1) * CELL - 12)
place("Player1", "Player", start[0], start[1])
# The camera follows the player, kept inside the level, and is the view from the start.
place("Camera1", "Camera", start[0], 90, target="Player1", smoothing=0.1, keepInBounds=True,
      boundsLeft=0, boundsTop=0, boundsRight=LEVEL_W, boundsBottom=H * CELL, currentAtStart=True)
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
EQ = 0
facing = value("self", "Platformer", "getFacing", onComponent=True)

player_rules = [
    # The keys say what the Platformer does; it reads no input itself.
    rule([inp("Move Left")], [comp("Player", "Platformer", "moveLeft")]),
    rule([inp("Move Right")], [comp("Player", "Platformer", "moveRight")]),
    rule([inp("Jump")], [comp("Player", "Platformer", "jump")]),
    # Down on a ledge drops through it.
    rule([inp("Move Down")], [comp("Player", "Platformer", "holdDown")]),
    # The picture follows the Platformer's state: a jump, a fall, a landing, running or standing.
    rule([comp("Player", "Platformer", "onJumped")], [line("Player", "Sprite", "setAnimation", s("jump")), line("audio", "Audio", "playSound", s("jump"))]),
    rule([comp("Player", "Platformer", "onStartedFalling")], [line("Player", "Sprite", "setAnimation", s("jump"))]),
    rule([comp("Player", "Platformer", "onLanded")], [line("Player", "Sprite", "setAnimation", s("idle"))]),
    rule([comp("Player", "Platformer", "isOnFloor"), comp("Player", "Platformer", "isMoving"), line("Player", "Sprite", "isAnimationPlaying", s("walk"), **{"not": True})],
         [line("Player", "Sprite", "setAnimation", s("walk"))]),
    rule([comp("Player", "Platformer", "isOnFloor"), comp("Player", "Platformer", "isMoving", **{"not": True}), line("Player", "Sprite", "isAnimationPlaying", s("idle"), **{"not": True})],
         [line("Player", "Sprite", "setAnimation", s("idle"))]),
    # Facing left draws the picture mirrored.
    rule([line("system", "System", "compare", facing, lit(EQ), lit(-1))], [line("self", "Node", "setMirrored", b(True))]),
    rule([line("system", "System", "compare", facing, lit(EQ), lit(1))], [line("self", "Node", "setMirrored", b(False))]),
]
write("events/PlayerRules.vscript.json", {"rules": player_rules, "vars": []})

write("project.json", {"schemaVersion": 2, "name": "Platformer", "entryScene": "scenes/Level.scene.json",
    "collisionLayers": {"1": "Player", "3": "Ground"},
    "display": {"width": 320, "height": 180, "windowWidth": 1280, "windowHeight": 720, "presentMode": "fit", "displayMode": "windowed", "autoResize": True, "wholeWindowScale": True},
    "physics": {"engine": "arcade", "gravity": 700}})
write("README.md", """# Platformer

The smallest working platform game, to start your own from. Run with the
arrow keys or A and D, jump with Space, and press Down or S on a plank ledge
to drop through it. Climb the planks to the top of the stone wall, then slide
down its far side; jump while sliding to jump off it.

- **Player** carries the **Platformer** behaviour beside a **Physics Body**.
  Its rules in `events/PlayerRules` turn the keys into Platformer commands and
  choose its picture: standing, running or jumping, mirrored when it faces
  left.
- **Ground** is a tile map painted from `assets/tiles/Ground`.
- **Ledge** carries **Platformer Fall Through**: jumped up through, stood on,
  dropped through.
- **Wall** carries **Platformer Wall**: slid down and jumped off.
- **Camera1** follows the player and keeps inside the level. The sky sits on
  the **Backdrop** Layer, which follows four tenths of the camera's movement.

Art and sound by [Kenney](https://kenney.nl) (Pixel Platformer, Digital
Audio), CC0. Generated by `tools/make-platformer-template.py`.
""")
print("wrote", out, "with", len(cells), "ground cells,", len(objects), "objects")
