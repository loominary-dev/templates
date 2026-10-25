"""The Tank demo: water and falling shapes on the ARCADE solver, the Fluid's
other home. Water poured from a tap runs along two flat shelves and over the
weir into the sink at the bottom right, carrying crates and balls dropped in
at the top; the shapes are arcade Physics Bodies, pushed and floated by the
water, and fall out through the gap. A readout gives the frame rate, the
fluid's step time and the counts; Debugger ▸ Profile gives the physics time.

    python3 tools/make-tank-demo.py [demos/tank]

The cascade demo is the same idea on Box2D, with ramps and belts; arcade has
neither (its bodies are axis-aligned boxes and circles that never turn), so
here the water does the carrying. Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "tank")
d = Demo(out, ["scenes", "vscript"], "7a900000")
W, H = 960, 540

# ── pictures ──
STEEL, STEEL_EDGE, STEEL_LIGHT = (96, 104, 118, 255), (52, 58, 68, 255), (150, 160, 176, 255)

def panel(w, h, fill, edge, radius=3, top=None):
    img = canvas(w, h)
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=edge, width=2)
    if top: g.line([2, 2, w - 3, 2], fill=top, width=1)
    return img

def crate_picture(size, fill, edge):
    img = canvas(size, size)
    g = ImageDraw.Draw(img)
    g.rectangle([1, 1, size - 2, size - 2], fill=fill, outline=edge, width=2)
    g.line([1, 1, size - 2, size - 2], fill=edge, width=2)
    g.line([1, size - 2, size - 2, 1], fill=edge, width=2)
    return img

def ball_picture(size, fill, edge):
    img = canvas(size, size)
    g = ImageDraw.Draw(img)
    g.ellipse([1, 1, size - 2, size - 2], fill=fill, outline=edge, width=2)
    c = size / 2
    g.ellipse([c - size * 0.3, c - size * 0.3, c - size * 0.1, c - size * 0.1], fill=tuple(min(255, v + 70) for v in fill[:3]) + (255,))
    return img

SHELF1_W, SHELF2_W, FLOOR_W, WEIR_H = 400, 480, 720, 90
d.sprite("Shelf", SHELF1_W, 14, [("still", [panel(SHELF1_W, 14, STEEL, STEEL_EDGE, 3, STEEL_LIGHT)], 400, "loop")], [box("body", SHELF1_W / 2, 7, SHELF1_W, 14)])
d.sprite("ShelfLong", SHELF2_W, 14, [("still", [panel(SHELF2_W, 14, STEEL, STEEL_EDGE, 3, STEEL_LIGHT)], 400, "loop")], [box("body", SHELF2_W / 2, 7, SHELF2_W, 14)])
d.sprite("Floor", FLOOR_W, 18, [("still", [panel(FLOOR_W, 18, STEEL, STEEL_EDGE, 3, STEEL_LIGHT)], 400, "loop")], [box("body", FLOOR_W / 2, 9, FLOOR_W, 18)])
d.sprite("Weir", 14, WEIR_H, [("still", [panel(14, WEIR_H, STEEL, STEEL_EDGE, 3)], 400, "loop")], [box("body", 7, WEIR_H / 2, 14, WEIR_H)])
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
    "Crate": ("square", 26, (210, 160, 60, 255), (120, 84, 20, 255)),
    "Ball": ("disc", 24, (232, 92, 80, 255), (140, 40, 40, 255)),
}
for name, (kind, size, fill, edge) in SHAPES.items():
    if kind == "disc":
        pic, shape = ball_picture(size, fill, edge), circle("body", size / 2, size / 2, size / 2)
    else:
        pic, shape = crate_picture(size, fill, edge), box("body", size / 2, size / 2, size - 2, size - 2)
    d.sprite(name, size, size, [("still", [pic], 400, "loop")], [shape])

icon = os.environ.get("LOOMINARY_ICON") or os.path.join(os.path.dirname(__file__), "..", "..", "Loom", "editor", "chrome", "icon.png")
mark = Image.open(icon).convert("RGBA").resize((40, 40), Image.LANCZOS) if os.path.exists(icon) else panel(40, 40, STEEL, STEEL_EDGE, 8)
d.sprite("Mark", 40, 40, [("still", [mark], 400, "loop")], [])

# ── collision layers, as bits ──
SOLID, BODY, DRAIN = 1, 2, 4
EVERYTHING = -1
def solid(): return {"collision": {"layer": SOLID, "mask": EVERYTHING}}
def moving(): return {"collision": {"layer": BODY, "mask": SOLID | BODY}}
# Under arcade the level needs no body of its own: a solid sprite's shapes are the walls.
for name in ["Shelf", "ShelfLong", "Floor", "Weir", "Wall"]:
    d.type_json(name, "Sprite", dict(solid(), spriteKey=name + ".sprite.json"))
# A shape slides almost freely along a shelf, so the water can carry it.
for name in SHAPES:
    d.type_json(name, "Sprite", dict(moving(), spriteKey=name + ".sprite.json"),
                [{"componentClass": "PhysicsBody", "bodyType": "Dynamic", "bounceX": 0.3, "bounceY": 0.2, "frictionX": 0.05}, {"componentClass": "ShapeRules"}])
# The water a little denser than the shapes (an arcade body counts as density 1), so they float low in it.
d.type_json("Water", "Sprite", {"spriteKey": "Drop.sprite.json", "collisionEnabled": False},
            [{"componentClass": "Fluid", "kind": "Water", "radius": 5, "maxCount": 2000, "pictureScale": 2.0, "color": 0x2F8FEF, "colorBySpeed": True, "speedColor": 0xDDF3FF, "fullSpeed": 650,
              "viscosity": 0.2, "density": 1.4, "layers": SOLID | BODY}, {"componentClass": "WaterRules"}])
d.type_json("Tap", "Sprite", {"spriteKey": "Tap.sprite.json", "collisionEnabled": False},
            [{"componentClass": "Emitter", "system": "Water1", "group": "tap", "on": True, "rate": 70, "speed": 160,
              "speedVariation": 0.1, "spread": 5, "shape": "Line", "width": 16}])
d.type_json("Sink", "Sprite", {"spriteKey": "Sink.sprite.json", "collision": {"layer": DRAIN, "mask": 0}},
            [{"componentClass": "Drain", "system": "Water1"}])
d.type_json("Mark", "Sprite", {"spriteKey": "Mark.sprite.json", "collisionEnabled": False, "opacity": 0.85})
d.type_json("Spawner", "Node", {}, [{"componentClass": "SpawnRules"}])
d.type_json("Help", "Label", {"text": "", "fontSize": 13, "shadow": True})
d.type_json("Caption", "Label", {"text": "", "fontSize": 13, "shadow": True})
READOUTS = [("fps", "Fps"), ("fluid ms", "FluidMs"), ("particles", "ParticleCount"), ("shapes", "ShapeCount")]
for _, name in READOUTS: d.type_json(name, "Label", {"text": "0", "fontSize": 13, "shadow": True})

# ── the scene: the screen's middle is the world's origin ──
objects = [{"id": d.uid(1), "name": "Tank"}]
n = [10]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    objects.append(dict({"id": d.uid(n[0]), "parent": d.uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra))
place("Spawner1", "Spawner", -300, -250)
place("WallL", "Wall", -470, 0); place("WallR", "Wall", 470, 0)
# Two flat shelves, each spilling off its right end onto the next; the floor is a tank closed by a weir on the right,
# which the water tops and goes over into the sink in the gap, and the shapes with it, to fall out at the bottom.
place("Shelf1", "Shelf", -260, -150)
place("Shelf2", "ShelfLong", -200, -10)
place("Floor1", "Floor", -100, 250)
place("Weir1", "Weir", 253, 250 - WEIR_H / 2 - 9)
place("Sink1", "Sink", 380, 262)
place("Tap1", "Tap", -400, -245, rotation=math.pi / 2)
place("Water1", "Water", -455, -245)
place("Mark1", "Mark", 435, -160)
place("Help1", "Help", -470, -265,
      text="Arcade solver.   Click to splash, drag to stir.   With Space held the left button makes water, with D it takes water away.   Debugger ▸ Profile: the physics time")
for i, (caption, name) in enumerate(READOUTS):
    place(name + "Caption", "Caption", 330, -248 + 18 * i, text=caption)
    place(name + "1", name, 400, -248 + 18 * i)
d.scene("scenes/Tank.scene.json", objects)

# ── rules ──
px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def body_(scope, name, *params, **k): return comp(scope, "PhysicsBody", name, *params, **k)
def fl(name, *params): return comp("self", "Fluid", name, *params)
def label(name, v): return line(name, "Label", "setNumber", v)
def number_var(name): return {"name": name, "type": "number", "value": 0}
def every(seconds): return sheet("every", lit(seconds))

# Each shape starts with a drift to the right and a gravity scale of its own, and goes once it has fallen out of the bottom.
d.write("vscript/ShapeRules.vscript.json", {"rules": [
    rule([once()], [body_("self", "setVelocity", random(40, 120), lit(0)), body_("self", "setGravityScale", random(0.6, 1.4))]),
    rule([compare(value("self", "Node", "getPositionY"), GT, lit(330))], [line("self", "Node", "queueDestroy")]),
]})

# A shape of a random kind every so often, at a random place over the first shelf, while there are fewer than thirty.
shape_count = value(list(SHAPES)[0], "Node", "count")
for name in list(SHAPES)[1:]: shape_count = op("+", shape_count, value(name, "Node", "count"))
pick = sheet_var("pick")
d.write("vscript/SpawnRules.vscript.json", {"vars": [number_var("pick")], "rules": [
    rule([every(0.6), compare(shape_count, LT, lit(30))],
         [line("self", "Node", "setPosition", random(-430, -120), lit(-250)), set_sheet_var("pick", value("maths", "Maths", "floor", random(0, len(SHAPES))))],
         [rule([compare(pick, EQ, lit(i))], [sheet("createObject", s(name), lit(1))]) for i, name in enumerate(SHAPES)]),
]})

frames, elapsed = sheet_var("frames"), sheet_var("elapsed")
# A press splashes, a drag stirs: the water within reach is pushed the way the pointer moved since the last step.
last_x, last_y = sheet_var("lastX"), sheet_var("lastY")
stir_x, stir_y = op("*", op("-", px, last_x), lit(40)), op("*", op("-", py, last_y), lit(40))
d.write("vscript/WaterRules.vscript.json", {"vars": [number_var(n) for n in ["frames", "elapsed", "lastX", "lastY"]], "rules": [
    rule([mouse_down(LEFT_BUTTON), held("Make"), every(0.05)], [fl("makeInCircle", px, py, lit(14), s("made"))]),
    rule([mouse_down(LEFT_BUTTON), held("Delete")], [fl("destroyInCircle", px, py, lit(45))]),
    rule([mouse_pressed(LEFT_BUTTON), not_(held("Make")), not_(held("Delete"))], [fl("pushInCircle", px, py, lit(70), lit(0), lit(-420))]),
    rule([mouse_down(LEFT_BUTTON), not_(mouse_pressed(LEFT_BUTTON)), not_(held("Make")), not_(held("Delete"))], [fl("pushInCircle", px, py, lit(45), stir_x, stir_y)]),
    rule([], [set_sheet_var("lastX", px), set_sheet_var("lastY", py)]),
    # The readout: frames over the last half second, the fluid's step time to a tenth of a millisecond, the counts.
    rule([], [add_sheet_var("frames", lit(1)), add_sheet_var("elapsed", dt()),
              label("FluidMs", op("/", value("maths", "Maths", "round", op("*", fl("stepTime"), lit(10))), lit(10))),
              label("ParticleCount", fl("particleCount")), label("ShapeCount", shape_count)]),
    rule([compare(elapsed, GE, lit(0.5))],
         [label("Fps", value("maths", "Maths", "round", op("/", frames, elapsed))), set_sheet_var("frames", lit(0)), set_sheet_var("elapsed", lit(0))]),
]})

d.write("project.json", {"schemaVersion": 2, "name": "Tank demo", "entryScene": "scenes/Tank.scene.json",
    "collisionLayers": {"1": "Solid", "2": "Body", "3": "Drain"},
    "input": {"Make": keys(32), "Delete": keys(68)},
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "arcade", "gravity": 980}})
d.write("README.md", """# Tank demo

Water and shapes on the **arcade** solver (Project Settings ▸ Physics) with
the **Fluid** behavior: the Fluid runs under either solver, and here it is
the arcade one that the water pushes and floats.

- **The shapes**: crates and balls, each a Sprite with a **Physics Body**.
  `vscript/SpawnRules` drops one of a random kind every 0.6 seconds over the
  first shelf while there are fewer than thirty (**Every 0.6 seconds**,
  **Create**); each starts with a drift to the right and a random **gravity
  scale**. The water flowing along the shelves carries them to the edges, and
  in the tank they float low (the water is given a density of 1.4; an arcade
  body counts as 1). A shape that has fallen out of the bottom destroys
  itself. Arcade bodies are axis-aligned and never turn, so there are no
  ramps or belts here: the water does the carrying.
- **The level** is solid sprites with no bodies of their own: two flat
  shelves, a floor and a weir, which the water tops and goes over into the
  sink.
- **The water** is a Fluid of up to 2,000 particles poured by an **Emitter**
  at the top left and taken away by the **Drain** in the gap. **Click** to
  splash it and **drag** to stir it (**Push particles in a circle**, with the
  pointer's movement as the push). Hold the left button with **Space** to
  make more where the pointer is (**Make particles in a circle**), with **D**
  to take it away (**Destroy particles in a circle**).
- The readout at the top right is the frame rate, the fluid's step time in
  milliseconds, and the counts of particles and shapes. The physics time is
  in **Debugger ▸ Profile**.

Generated by `tools/make-tank-demo.py`; the pictures are drawn there, and
the mark in the corner is the editor's icon.
""")
print("wrote", d.out)
