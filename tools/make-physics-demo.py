"""The Box2D physics demo: one playground of the Box2D solver's words. A rope
bridge of planks on hinges, a car on two wheel joints driven by their
motors, a wrecking ball on a hinge to the world, a see-saw, a pool that
floats what falls in (Fluid Zone), a fan that blows (Field), crates the car
can pick up and put down (Attach and Detach), and everything draggable with
the mouse (Drag toward).

    python3 tools/make-physics-demo.py <kenney digital-audio dir> <kenney impact-sounds dir> [demos/physics]

Everything is drawn here; the sounds are Kenney's (CC0). Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

da, im = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "..", "demos", "physics")
d = Demo(out, ["scenes", "vscript"], "p1000000")
W, H = 960, 540

# ── pictures ──
WOOD, WOOD_DARK, WOOD_LINE = (196, 140, 82, 255), (132, 88, 48, 255), (100, 64, 34, 255)
def panel(w, h, fill, edge, radius=3, lines=()):
    img = canvas(w, h)
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=edge, width=2)
    for (x0, y0, x1, y1) in lines: g.line([x0, y0, x1, y1], fill=edge, width=2)
    return img
def disc(size, fill, edge, spokes=0, hub=None):
    img = canvas(size, size)
    g = ImageDraw.Draw(img)
    g.ellipse([1, 1, size - 2, size - 2], fill=fill, outline=edge, width=2)
    c = (size - 1) / 2
    for i in range(spokes):
        a = i * math.pi * 2 / spokes
        g.line([c, c, c + math.cos(a) * c * 0.75, c + math.sin(a) * c * 0.75], fill=edge, width=2)
    if hub: g.ellipse([c - 4, c - 4, c + 4, c + 4], fill=hub)
    return img

d.sprite("Crate", 32, 32, [("still", [panel(32, 32, WOOD, WOOD_LINE, 2, [(3, 3, 28, 28), (28, 3, 3, 28)])], 400, "loop")], [box("body", 16, 16, 32, 32)])
d.sprite("Plank", 28, 10, [("still", [panel(28, 10, WOOD, WOOD_LINE, 2)], 400, "loop")], [box("body", 14, 5, 28, 10)],
         [point("left", 0, 5), point("right", 28, 5)])
d.sprite("Post", 20, 20, [("still", [panel(20, 20, (120, 120, 132, 255), (70, 70, 80, 255))], 400, "loop")], [box("body", 10, 10, 20, 20)])
d.sprite("Ball", 28, 28, [("still", [disc(28, (232, 92, 80, 255), (140, 40, 40, 255))], 400, "loop")], [circle("body", 14, 14, 14)])
# The wrecking ball hangs from a point well above itself: its pin, where the hinge to the world goes.
d.sprite("WreckingBall", 44, 44, [("still", [disc(44, (70, 70, 80, 255), (30, 30, 36, 255), 0, (110, 110, 120, 255))], 400, "loop")],
         [circle("body", 22, 22, 22)], [point("pin", 22, -298)])
d.sprite("Chain", 4, 320, [("still", [panel(4, 320, (90, 90, 100, 255), (60, 60, 66, 255), 1)], 400, "loop")], [])
car = panel(100, 28, (60, 120, 220, 255), (24, 52, 110, 255), 6)
ImageDraw.Draw(car).rectangle([58, 4, 86, 14], fill=(190, 225, 255, 255))
d.sprite("Buggy", 100, 28, [("still", [car], 400, "loop")], [box("body", 50, 14, 100, 28)])
d.sprite("Wheel", 28, 28, [("still", [disc(28, (40, 40, 44, 255), (12, 12, 14, 255), 5, (180, 180, 190, 255))], 400, "loop")],
         [circle("tire", 14, 14, 14, friction=0.95)])
d.sprite("Board", 220, 12, [("still", [panel(220, 12, WOOD, WOOD_LINE, 3)], 400, "loop")], [box("body", 110, 6, 220, 12)])
fulcrum = canvas(40, 30)
ImageDraw.Draw(fulcrum).polygon([(20, 0), (39, 29), (0, 29)], fill=(120, 120, 132, 255), outline=(70, 70, 80, 255))
d.sprite("Fulcrum", 40, 30, [("still", [fulcrum], 400, "loop")], [{"name": "body", "kind": "poly", "points": [{"x": 20, "y": 0}, {"x": 40, "y": 30}, {"x": 0, "y": 30}]}])
d.sprite("Ground", 960, 40, [("still", [panel(960, 40, (92, 140, 70, 255), (54, 90, 40, 255), 0)], 400, "loop")], [box("body", 480, 20, 960, 40)])
d.sprite("Wall", 20, 540, [("still", [panel(20, 540, (100, 100, 110, 255), (60, 60, 70, 255), 0)], 400, "loop")], [box("body", 10, 270, 20, 540)])
water = canvas(300, 100)
ImageDraw.Draw(water).rectangle([0, 0, 299, 99], fill=(60, 140, 230, 110))
ImageDraw.Draw(water).line([0, 1, 299, 1], fill=(170, 215, 255, 200), width=2)
d.sprite("Pool", 300, 100, [("still", [water], 400, "loop")], [box("water", 150, 50, 300, 100, sensor=True)])
d.sprite("Raft", 90, 12, [("still", [panel(90, 12, WOOD_DARK, WOOD_LINE, 3)], 400, "loop")], [box("body", 45, 6, 90, 12, density=0.4)])
fan = disc(40, (200, 200, 210, 255), (90, 90, 100, 255), 3, (90, 90, 100, 255))
d.sprite("Fan", 40, 40, [("still", [fan], 400, "loop")], [])
d.sprite("Breeze", 400, 90, [("still", [panel(400, 90, (255, 255, 255, 18), (255, 255, 255, 40), 8)], 400, "loop")], [box("air", 200, 45, 400, 90, sensor=True)])

d.sounds({"bump": (im, "impactWood_light_002.ogg"), "grab": (da, "powerUp2.ogg"), "drop": (da, "lowDown.ogg"), "swing": (im, "impactMetal_heavy_000.ogg")})

# ── collision layers, as bits ──
SOLID, BODY, WATER, AIR = 1, 2, 4, 8
EVERYTHING = -1
def body(**k): return dict({"componentClass": "PhysicsBody", "bodyType": "Dynamic"}, **k)
def solid(): return {"collision": {"layer": SOLID, "mask": EVERYTHING}}
def moving(): return {"collision": {"layer": BODY, "mask": SOLID | BODY}}

for name in ["Ground", "Wall", "Post", "Fulcrum"]:
    d.type_json(name, "Sprite", dict(solid(), spriteKey=name + ".sprite.json"))
d.type_json("Crate", "Sprite", dict(moving(), spriteKey="Crate.sprite.json"), [body(), {"componentClass": "DragRules"}, {"componentClass": "CrateRules"}])
d.type_json("Ball", "Sprite", dict(moving(), spriteKey="Ball.sprite.json"), [body(bounceX=0.5, bounceY=0.5), {"componentClass": "DragRules"}])
d.type_json("Raft", "Sprite", dict(moving(), spriteKey="Raft.sprite.json"), [body(), {"componentClass": "DragRules"}])
d.type_json("Plank", "Sprite", dict(moving(), spriteKey="Plank.sprite.json"), [body(), {"componentClass": "DragRules"}])
d.type_json("Board", "Sprite", dict(moving(), spriteKey="Board.sprite.json"), [body(), {"componentClass": "BoardRules"}])
d.type_json("WreckingBall", "Sprite", dict(moving(), spriteKey="WreckingBall.sprite.json"), [body(), {"componentClass": "WreckingRules"}, {"componentClass": "DragRules"}])
d.type_json("Chain", "Sprite", {"spriteKey": "Chain.sprite.json", "collisionEnabled": False})
d.type_json("Buggy", "Sprite", dict(moving(), spriteKey="Buggy.sprite.json"), [body(), {"componentClass": "DragRules"}])
d.type_json("Wheel", "Sprite", dict(moving(), spriteKey="Wheel.sprite.json"), [body(friction=0.95), {"componentClass": "WheelRules"}])
d.type_json("Pool", "Sprite", {"spriteKey": "Pool.sprite.json", "collision": {"layer": WATER, "mask": BODY}},
            [{"componentClass": "FluidZone", "density": 2, "drag": 2.5, "angularDrag": 2}])
d.type_json("Fan", "Sprite", {"spriteKey": "Fan.sprite.json", "collisionEnabled": False}, [{"componentClass": "Rotate", "speed": 0}])
d.type_json("Breeze", "Sprite", {"spriteKey": "Breeze.sprite.json", "collision": {"layer": AIR, "mask": BODY}},
            [{"componentClass": "Field", "kind": "Wind", "strength": 0, "affects": "Bodies"}])
d.type_json("Level", "Node", {}, [{"componentClass": "LevelRules"}])
d.type_json("Help", "Label", {"text": "", "fontSize": 13})

# ── the playground: the screen's middle is the world's origin; the ground's top is at 230 ──
objects = [{"id": d.uid(1), "name": "Playground"}]
n = [10]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    objects.append(dict({"id": d.uid(n[0]), "parent": d.uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra))
place("Level1", "Level", 0, 0)
place("Ground1", "Ground", 0, 250)
place("WallL", "Wall", -470, 0); place("WallR", "Wall", 470, 0)
# The bridge: ten planks between two posts, each hinged to the one before at its left edge, the last to the right post too.
BRIDGE_Y = -40
place("PostL", "Post", -150, BRIDGE_Y); place("PostR", "Post", 150, BRIDGE_Y)
for i in range(10): place("Plank%d" % (i + 1), "Plank", -140 + 14 + 28 * i, BRIDGE_Y)
for i, x in enumerate([-60, 0, 60]): place("Crate%d" % (i + 1), "Crate", x, -160 - i * 40)
# The car, on the ground at the left; its wheels make their own joints.
place("Buggy1", "Buggy", -405, 196)
place("Wheel1", "Wheel", -438, 214); place("Wheel2", "Wheel", -372, 214)
for i, (x, y) in enumerate([(-305, 214), (-271, 214), (-288, 182)]): place("Crate%d" % (i + 4), "Crate", x, y)
# The see-saw, a crate on one end.
place("Fulcrum1", "Fulcrum", -110, 215); place("Board1", "Board", -110, 194)
place("Crate7", "Crate", -190, 170); place("Ball1", "Ball", -30, 60)
# The pool, and a raft on it.
place("Pool1", "Pool", 120, 180); place("Raft1", "Raft", 100, 120); place("Ball2", "Ball", 160, 80)
# The wrecking ball at the right, hanging from a pin above it, and a stack of crates for it.
place("WreckingBall1", "WreckingBall", 400, 148)
# The chain is a child of the ball, half way to its pin, so it swings with it; it has no shapes, so it is no part of the ball's body.
n[0] += 1
# A child is placed from its parent's top-left: the ball is 44 across, so its middle is at 22, 22.
objects.append({"id": d.uid(n[0]), "parent": objects[-1]["id"], "name": "Chain1", "type": "Chain", "x": 22, "y": 22 - 160})
for i in range(4): place("Crate%d" % (i + 8), "Crate", 330, 214 - 32 * i)
# The fan and its breeze, over the bridge.
place("Fan1", "Fan", -440, -80); place("Breeze1", "Breeze", -220, -80)
help_text = "Arrows drive the car. G picks up crates near it, H puts them down. Drag anything with the mouse. B swings the ball, F starts the fan."
place("Help1", "Help", -470, -262, text=help_text)
d.scene("scenes/Playground.scene.json", objects)

# ── rules ──
px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def body_(scope, name, *params, **k): return comp(scope, "PhysicsBody", name, *params, **k)
def has_joint(scope, j): return body_(scope, "hasJoint", s(j))

drag_rules = [
    rule([mouse_pressed(LEFT_BUTTON), line("self", "Node", "containsPoint", px, py)], [body_("self", "dragToward", px, py)]),
    rule([mouse_down(LEFT_BUTTON), body_("self", "isDragged")], [body_("self", "dragToward", px, py)]),
    rule([not_(mouse_down(LEFT_BUTTON)), body_("self", "isDragged")], [body_("self", "releaseDrag")]),
]
d.write("vscript/DragRules.vscript.json", {"rules": drag_rules})

# A joint is made once both bodies are there: "has no joint" asks again each step until it is.
wheel_rules = [
    rule([not_(has_joint("self", "axle"))], [body_("self", "wheelOf", s("Buggy1"), lit(-90), s(""), s("axle")),
                                             body_("self", "setJointSpring", s("axle"), lit(4), lit(0.7))]),
    rule([held("Right")], [body_("self", "setJointMotor", s("axle"), lit(1080), lit(9000))]),
    rule([held("Left")], [body_("self", "setJointMotor", s("axle"), lit(-1080), lit(9000))]),
    rule([not_(held("Left")), not_(held("Right"))], [body_("self", "setJointMotorOn", s("axle"), b(False))]),
]
d.write("vscript/WheelRules.vscript.json", {"rules": wheel_rules})

d.write("vscript/BoardRules.vscript.json", {"rules": [rule([not_(has_joint("self", "pivot"))], [body_("self", "hingeTo", s(""), s(""), s("pivot"))])]})
mass = cvalue("self", "PhysicsBody", "mass")
d.write("vscript/WreckingRules.vscript.json", {"rules": [
    rule([not_(has_joint("self", "chain"))], [body_("self", "hingeTo", s(""), s("pin"), s("chain"))]),
    rule([pressed("Swing")], [body_("self", "applyImpulse", op("*", mass, lit(-700)), lit(0)), line("audio", "Audio", "playSound", s("swing"))]),
]})
d.write("vscript/CrateRules.vscript.json", {"rules": [
    rule([line("self", "Node", "onContactStarted", s("Crate"))], [line("audio", "Audio", "playSound", s("bump"))]),
]})

level_rules = [
    # The bridge: each plank hinged at its left edge to the one before, the first to the left post, the last to the right post too.
    rule([line("Plank", "Node", "nameIs", s("Plank1")), not_(has_joint("Plank", "link"))], [body_("Plank", "hingeTo", s("PostL"), s("left"), s("link"))]),
] + [
    rule([line("Plank", "Node", "nameIs", s("Plank%d" % i)), not_(has_joint("Plank", "link"))], [body_("Plank", "hingeTo", s("Plank%d" % (i - 1)), s("left"), s("link"))])
    for i in range(2, 11)
] + [
    rule([line("Plank", "Node", "nameIs", s("Plank10")), not_(has_joint("Plank", "end"))], [body_("Plank", "hingeTo", s("PostR"), s("right"), s("end"))]),
    # The car's crane: G attaches the crates near the car to it, H lets them go.
    rule([pressed("Grab"), line("Crate", "Node", "isWithinDistanceOf", s("Buggy"), lit(70)), not_(body_("Crate", "isAttached"))],
         [body_("Crate", "attachTo", s("Buggy1")), line("audio", "Audio", "playSound", s("grab"))]),
    rule([pressed("Drop"), body_("Crate", "isAttached")], [body_("Crate", "detach"), line("audio", "Audio", "playSound", s("drop"))]),
    # The fan: F starts and stops it.
    rule([pressed("Fan"), compare(var("fan"), EQ, lit(0))],
         [line("variables", "Variables", "setVariable", s("fan"), lit(2)), comp("Breeze", "Field", "setStrength", lit(900)), comp("Fan", "Rotate", "setSpeed", lit(720))]),
    rule([pressed("Fan"), compare(var("fan"), EQ, lit(1))],
         [line("variables", "Variables", "setVariable", s("fan"), lit(0)), comp("Breeze", "Field", "setStrength", lit(0)), comp("Fan", "Rotate", "setSpeed", lit(0))]),
    rule([compare(var("fan"), EQ, lit(2))], [line("variables", "Variables", "setVariable", s("fan"), lit(1))]),
]
d.write("vscript/LevelRules.vscript.json", {"rules": level_rules})

d.write("project.json", {"schemaVersion": 2, "name": "Physics demo", "entryScene": "scenes/Playground.scene.json",
    "collisionLayers": {"1": "Solid", "2": "Body", "3": "Water", "4": "Air"},
    "input": {"Left": keys(37, 65), "Right": keys(39, 68), "Grab": keys(71), "Drop": keys(72), "Swing": keys(66), "Fan": keys(70)},
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "box2d", "gravity": 980, "interpolate": True}})
d.write("README.md", """# Physics demo

A playground for the **Box2D** solver (Project Settings ▸ Physics), every
part of it a word of the **Physics Body** or a behavior:

- **The bridge**: ten planks, each hinged at its `left` point to the one
  before (**Hinge to**), the first to the left post and the last to the right
  one too. The joints are made by `vscript/LevelRules`; a rule asks "has no
  joint" each step, so each is made as soon as both bodies are there.
- **The car**: each wheel is **a wheel of** the car on a sprung axis, and the
  arrow keys **Drive** its motor. **G** attaches the crates near the car to
  it (**Attach to**), **H** puts them down again (**Detach**).
- **The wrecking ball** hangs from its `pin` point, a hinge to the world;
  **B** gives it a push (**Give an impulse**).
- **The see-saw** is a board hinged to the world at its middle.
- **The pool** is a **Fluid Zone**: what falls in floats by its density and is
  slowed; the raft's shape has a density of 0.4.
- **The fan** drives a **Field** set to Wind; **F** starts and stops it.
- **Drag** anything with the mouse: `vscript/DragRules` uses **Contains point**
  to take hold of the object under the pointer and **Drag toward** to pull it.

Generated by `tools/make-physics-demo.py`; the pictures are drawn there and
the sounds are Kenney's (Digital Audio, Impact Sounds), CC0.
""")
print("wrote", d.out)
