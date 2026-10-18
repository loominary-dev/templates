"""The Cascade demo: water and falling shapes down a flight of tilted ramps and
conveyor belts, with the Box2D solver's contact points drawn. Shapes of four
kinds drop in at the top with a random gravity scale, slide down the ramps,
ride the belts (Set the surface speed) and fall out through the gap at the
bottom, where a Drain takes the water; a readout gives the frame rate, the
fluid's step time and the counts.

    python3 tools/make-cascade-demo.py [demos/cascade]

Everything is drawn here but the mark in the corner, which is the editor's own
icon (editor/chrome/icon.png in the Loominary repository, given as LOOMINARY_ICON
or found beside this clone). Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "cascade")
d = Demo(out, ["scenes", "vscript"], "ca500000")
W, H = 960, 540

# ── pictures ──
STEEL, STEEL_EDGE, STEEL_LIGHT = (96, 104, 118, 255), (52, 58, 68, 255), (150, 160, 176, 255)
RUBBER, RUBBER_EDGE, CHEVRON = (58, 60, 66, 255), (28, 30, 34, 255), (236, 196, 60, 255)

def panel(w, h, fill, edge, radius=3, top=None):
    img = canvas(w, h)
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=edge, width=2)
    if top: g.line([2, 2, w - 3, 2], fill=top, width=1)
    return img

def belt_frames(w, h, direction, count=3, period=24):
    """A belt whose chevrons slide along it: each frame shifts them a third of their spacing."""
    frames = []
    for i in range(count):
        img = panel(w, h, RUBBER, RUBBER_EDGE, 4)
        g = ImageDraw.Draw(img)
        shift = i * period / count * direction
        x = -period
        while x < w + period:
            cx = x + shift
            tip, back = (cx + 5, cx - 1) if direction > 0 else (cx - 5, cx + 1)
            g.line([back, 4, tip, h / 2, back, h - 5], fill=CHEVRON, width=2)
            x += period
        g.rounded_rectangle([0, 0, w - 1, h - 1], radius=4, outline=RUBBER_EDGE, width=2)
        frames.append(img)
    return frames

def shape_picture(size, kind, fill, edge):
    img = canvas(size, size)
    g = ImageDraw.Draw(img)
    pts = polygon_points(size, kind)
    if kind == "disc": g.ellipse([1, 1, size - 2, size - 2], fill=fill, outline=edge, width=2)
    else: g.polygon(pts, fill=fill, outline=edge, width=2)
    # A highlight, so a turning shape shows its turn.
    c = size / 2
    g.ellipse([c - size * 0.3, c - size * 0.3, c - size * 0.1, c - size * 0.1], fill=tuple(min(255, v + 70) for v in fill[:3]) + (255,))
    return img

def polygon_points(size, kind):
    c, r = (size - 1) / 2, (size - 1) / 2 - 1
    if kind == "square": return [(1, 1), (size - 2, 1), (size - 2, size - 2), (1, size - 2)]
    n = {"triangle": 3, "pentagon": 5, "disc": 0}[kind]
    if n == 0: return []
    return [(c + r * math.cos(-math.pi / 2 + i * 2 * math.pi / n), c + r * math.sin(-math.pi / 2 + i * 2 * math.pi / n)) for i in range(n)]

RAMP_W, BELT_W, FLOOR_W = 420, 300, 760
d.sprite("Ramp", RAMP_W, 14, [("still", [panel(RAMP_W, 14, STEEL, STEEL_EDGE, 3, STEEL_LIGHT)], 400, "loop")], [box("body", RAMP_W / 2, 7, RAMP_W, 14)])
d.sprite("Belt", BELT_W, 18, [("run", belt_frames(BELT_W, 18, 1), 90, "loop")], [box("body", BELT_W / 2, 9, BELT_W, 18)])
d.sprite("BeltLeft", BELT_W, 18, [("run", belt_frames(BELT_W, 18, -1), 90, "loop")], [box("body", BELT_W / 2, 9, BELT_W, 18)])
d.sprite("FloorBelt", FLOOR_W, 18, [("run", belt_frames(FLOOR_W, 18, 1), 90, "loop")], [box("body", FLOOR_W / 2, 9, FLOOR_W, 18)])
d.sprite("Wall", 20, 540, [("still", [panel(20, 540, STEEL, STEEL_EDGE, 0)], 400, "loop")], [box("body", 10, 270, 20, 540)])
sink = panel(180, 30, (34, 36, 42, 255), (18, 20, 24, 255), 2)
for x in range(8, 180, 14): ImageDraw.Draw(sink).line([x, 6, x, 24], fill=(70, 74, 84, 255), width=3)
d.sprite("Sink", 180, 30, [("still", [sink], 400, "loop")], [box("grate", 90, 15, 180, 30)])
tap = canvas(28, 18)
g = ImageDraw.Draw(tap)
g.rounded_rectangle([0, 4, 27, 13], radius=4, fill=STEEL_LIGHT, outline=STEEL_EDGE, width=2)
g.rectangle([18, 0, 27, 17], fill=STEEL, outline=STEEL_EDGE, width=2)
d.sprite("Tap", 28, 18, [("still", [tap], 400, "loop")], [])
d.sprite("Drop", 16, 16, [("still", [soft_dot(16, (255, 255, 255), 0.8)], 400, "loop")], [])

SHAPES = {  # name: (kind, size, fill, edge)
    "Disc": ("disc", 28, (232, 92, 80, 255), (140, 40, 40, 255)),
    "Square": ("square", 26, (70, 150, 230, 255), (28, 70, 130, 255)),
    "Triangle": ("triangle", 32, (90, 190, 110, 255), (34, 100, 50, 255)),
    "Pentagon": ("pentagon", 30, (210, 160, 60, 255), (120, 84, 20, 255)),
}
for name, (kind, size, fill, edge) in SHAPES.items():
    pic = shape_picture(size, kind, fill, edge)
    if kind == "disc": shape = circle("body", size / 2, size / 2, size / 2, friction=0.5)
    elif kind == "square": shape = box("body", size / 2, size / 2, size - 2, size - 2, friction=0.5)
    else: shape = poly("body", polygon_points(size, kind), friction=0.5)
    d.sprite(name, size, size, [("still", [pic], 400, "loop")], [shape])

icon = os.environ.get("LOOMINARY_ICON") or os.path.join(os.path.dirname(__file__), "..", "..", "Loom", "editor", "chrome", "icon.png")
mark = Image.open(icon).convert("RGBA").resize((40, 40), Image.LANCZOS) if os.path.exists(icon) else panel(40, 40, STEEL, STEEL_EDGE, 8)
d.sprite("Mark", 40, 40, [("still", [mark], 400, "loop")], [])

# ── collision layers, as bits ──
SOLID, BODY, DRAIN = 1, 2, 4
EVERYTHING = -1
def solid(): return {"collision": {"layer": SOLID, "mask": EVERYTHING}}
def moving(): return {"collision": {"layer": BODY, "mask": SOLID | BODY}}
def body(**k): return dict({"componentClass": "PhysicsBody", "bodyType": "Dynamic"}, **k)

for name in ["Ramp", "Wall"]:
    d.type_json(name, "Sprite", dict(solid(), spriteKey=name + ".sprite.json"))
# The belts are Static bodies of their own, so a rule can give them a surface speed.
d.type_json("Belt", "Sprite", dict(solid(), spriteKey="Belt.sprite.json"), [body(bodyType="Static"), {"componentClass": "BeltRules"}])
d.type_json("BeltLeft", "Sprite", dict(solid(), spriteKey="BeltLeft.sprite.json"), [body(bodyType="Static"), {"componentClass": "BeltLeftRules"}])
d.type_json("FloorBelt", "Sprite", dict(solid(), spriteKey="FloorBelt.sprite.json"), [body(bodyType="Static"), {"componentClass": "BeltRules"}])
for name in SHAPES:
    d.type_json(name, "Sprite", dict(moving(), spriteKey=name + ".sprite.json"),
                [body(bounceX=0.2, bounceY=0.2), {"componentClass": "ShapeRules"}, {"componentClass": "DragRules"}])
d.type_json("Water", "Sprite", {"spriteKey": "Drop.sprite.json", "collisionEnabled": False},
            [{"componentClass": "Fluid", "kind": "Water", "radius": 5, "maxCount": 3000, "pictureScale": 2.0, "color": 0x4AA8FF,
              "viscosity": 0.2, "layers": SOLID | BODY}, {"componentClass": "WaterRules"}])
d.type_json("Tap", "Sprite", {"spriteKey": "Tap.sprite.json", "collisionEnabled": False},
            [{"componentClass": "Emitter", "system": "Water1", "group": "tap", "on": True, "rate": 75, "speed": 120,
              "speedVariation": 0.1, "spread": 5, "shape": "Line", "width": 16}])
d.type_json("Sink", "Sprite", {"spriteKey": "Sink.sprite.json", "collision": {"layer": DRAIN, "mask": 0}},
            [{"componentClass": "Drain", "system": "Water1"}])
d.type_json("Mark", "Sprite", {"spriteKey": "Mark.sprite.json", "collisionEnabled": False, "opacity": 0.85})
d.type_json("Spawner", "Node", {}, [{"componentClass": "SpawnRules"}])
d.type_json("Level", "Node", {}, [{"componentClass": "LevelRules"}])
d.type_json("Help", "Label", {"text": "", "fontSize": 13, "shadow": True})
d.type_json("Caption", "Label", {"text": "", "fontSize": 13, "shadow": True})
READOUTS = [("fps", "Fps"), ("fluid ms", "FluidMs"), ("particles", "ParticleCount"), ("shapes", "ShapeCount")]
for _, name in READOUTS: d.type_json(name, "Label", {"text": "0", "fontSize": 13, "shadow": True})

# ── the scene: the screen's middle is the world's origin ──
objects = [{"id": d.uid(1), "name": "Cascade"}]
n = [10]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    objects.append(dict({"id": d.uid(n[0]), "parent": d.uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra))
place("Level1", "Level", 0, 0)
place("Spawner1", "Spawner", -300, -250)
place("WallL", "Wall", -470, 0); place("WallR", "Wall", 470, 0)
# The flight, each stage handing on to the next: a ramp from the left wall down to the right, a belt carrying right,
# a ramp from the right wall down to the left, a belt carrying left, and the floor belt carrying everything right to
# the gap at the bottom right, where the sink takes the water and the shapes fall out.
place("Ramp1", "Ramp", -260, -180, rotation=0.2)
place("Belt1", "Belt", 100, -80)
place("Ramp2", "Ramp", 270, 20, rotation=-0.25)
place("Belt2", "BeltLeft", -60, 130)
place("FloorBelt1", "FloorBelt", -90, 250)
place("Sink1", "Sink", 380, 262)
place("Tap1", "Tap", -400, -245, rotation=math.pi / 2)
place("Water1", "Water", -455, -245)
place("Mark1", "Mark", 435, -160)
place("Help1", "Help", -470, -265,
      text="Shapes fall onto the ramps and ride the belts.   Hold the left button with Space to make water, with D to take it away.   Drag the shapes.   C: contact points")
for i, (caption, name) in enumerate(READOUTS):
    place(name + "Caption", "Caption", 330, -248 + 18 * i, text=caption)
    place(name + "1", name, 400, -248 + 18 * i)
d.scene("scenes/Cascade.scene.json", objects)

# ── rules ──
px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def body_(scope, name, *params, **k): return comp(scope, "PhysicsBody", name, *params, **k)
def fl(name, *params): return comp("self", "Fluid", name, *params)
def label(name, v): return line(name, "Label", "setNumber", v)
def number_var(name): return {"name": name, "type": "number", "value": 0}
def every(seconds): return sheet("every", lit(seconds))

d.write("vscript/BeltRules.vscript.json", {"rules": [rule([once()], [body_("self", "setSurfaceSpeed", lit(140))])]})
d.write("vscript/BeltLeftRules.vscript.json", {"rules": [rule([once()], [body_("self", "setSurfaceSpeed", lit(-140))])]})

d.write("vscript/DragRules.vscript.json", {"rules": [
    rule([mouse_pressed(LEFT_BUTTON), line("self", "Node", "containsPoint", px, py)], [body_("self", "dragToward", px, py)]),
    rule([mouse_down(LEFT_BUTTON), body_("self", "isDragged")], [body_("self", "dragToward", px, py)]),
    rule([not_(mouse_down(LEFT_BUTTON)), body_("self", "isDragged")], [body_("self", "releaseDrag")]),
]})

# Each shape falls as hard as its own random gravity scale says, and goes once it has fallen out of the bottom.
d.write("vscript/ShapeRules.vscript.json", {"rules": [
    rule([once()], [body_("self", "setGravityScale", random(0.3, 1.5))]),
    rule([compare(value("self", "Node", "getPositionY"), GT, lit(330))], [line("self", "Node", "queueDestroy")]),
]})

# A shape of a random kind every so often, at a random place over the first ramp, while there are fewer than ninety.
shape_count = value(list(SHAPES)[0], "Node", "count")
for name in list(SHAPES)[1:]: shape_count = op("+", shape_count, value(name, "Node", "count"))
pick = sheet_var("pick")
d.write("vscript/SpawnRules.vscript.json", {"vars": [number_var("pick")], "rules": [
    rule([every(0.45), compare(shape_count, LT, lit(90))],
         [line("self", "Node", "setPosition", random(-430, -120), lit(-250)), set_sheet_var("pick", value("maths", "Maths", "floor", random(0, 4)))],
         [rule([compare(pick, EQ, lit(i))], [sheet("createObject", s(name), lit(1))]) for i, name in enumerate(SHAPES)]),
]})

frames, elapsed = sheet_var("frames"), sheet_var("elapsed")
d.write("vscript/WaterRules.vscript.json", {"vars": [number_var("frames"), number_var("elapsed")], "rules": [
    rule([mouse_down(LEFT_BUTTON), held("Make"), every(0.05)], [fl("makeInCircle", px, py, lit(14), s("made"))]),
    rule([mouse_down(LEFT_BUTTON), held("Delete")], [fl("destroyInCircle", px, py, lit(45))]),
    # The readout: frames over the last half second, the fluid's step time to a tenth of a millisecond, the counts.
    rule([], [add_sheet_var("frames", lit(1)), add_sheet_var("elapsed", dt()),
              label("FluidMs", op("/", value("maths", "Maths", "round", op("*", fl("stepTime"), lit(10))), lit(10))),
              label("ParticleCount", fl("particleCount")), label("ShapeCount", shape_count)]),
    rule([compare(elapsed, GE, lit(0.5))],
         [label("Fps", value("maths", "Maths", "round", op("/", frames, elapsed))), set_sheet_var("frames", lit(0)), set_sheet_var("elapsed", lit(0))]),
]})

# The contact points are drawn from the start; C hides and shows them (the value 2 keeps one press from doing both in one step).
d.write("vscript/LevelRules.vscript.json", {"rules": [
    rule([once()], [sheet("showContactPoints", b(True)), line("variables", "Variables", "setVariable", s("contacts"), lit(1))]),
    rule([pressed("Contacts"), compare(var("contacts"), EQ, lit(0))], [line("variables", "Variables", "setVariable", s("contacts"), lit(2)), sheet("showContactPoints", b(True))]),
    rule([pressed("Contacts"), compare(var("contacts"), EQ, lit(1))], [line("variables", "Variables", "setVariable", s("contacts"), lit(0)), sheet("showContactPoints", b(False))]),
    rule([compare(var("contacts"), EQ, lit(2))], [line("variables", "Variables", "setVariable", s("contacts"), lit(1))]),
]})

d.write("project.json", {"schemaVersion": 2, "name": "Cascade demo", "entryScene": "scenes/Cascade.scene.json",
    "collisionLayers": {"1": "Solid", "2": "Body", "3": "Drain"},
    "input": {"Make": keys(32), "Delete": keys(68), "Contacts": keys(67)},
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "box2d", "gravity": 980, "interpolate": True}})
d.write("README.md", """# Cascade demo

Water and shapes down a flight of ramps and conveyor belts, on the **Box2D**
solver (Project Settings ▸ Physics) and the **Fluid** behaviour:

- **The shapes**: discs, squares, triangles and pentagons, each a Sprite with
  a **Physics Body**. `vscript/SpawnRules` drops one of a random kind every
  half second over the first ramp (**Every 0.45 seconds**, **Create**), and
  each gives itself a random **gravity scale** between 0.3 and 1.5 when it
  starts, so some fall like feathers and some like stones. A shape that has
  fallen out of the bottom destroys itself.
- **The belts** are Static Physics Bodies given a **surface speed** by their
  rules: the first carries to the right, the second to the left, and the
  floor to the right, toward the gap. Their chevrons are an animation running
  the same way.
- **The water** is a Fluid of up to three thousand particles poured by an
  **Emitter** at the top left and taken away by the **Drain** in the gap.
  Hold the left button with **Space** to make more where the pointer is
  (**Make particles in a circle**), with **D** to take it away (**Destroy
  particles in a circle**).
- **The contact points**: **Show contact points** draws a yellow cross
  wherever two bodies touch; **C** hides and shows them.
- **Drag** any shape with the mouse (`vscript/DragRules`).
- The readout at the top right is the frame rate, the fluid's step time in
  milliseconds, and the counts of particles and shapes.

Generated by `tools/make-cascade-demo.py`; the pictures are drawn there, and
the mark in the corner is the editor's icon.
""")
print("wrote", d.out)
