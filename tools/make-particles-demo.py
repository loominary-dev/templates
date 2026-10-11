"""The particles demo: water, sand and sparks, each a sprite carrying a Fluid
behaviour whose picture is drawn once per particle. A tap and a hopper pour
through Emitters, a plughole drains through a Drain, a fan blows across the
basin through a Field, crates float and can be dragged, and the mouse
splashes and pours. On Box2D, so the water pushes the crates and they push
back.

    python3 tools/make-particles-demo.py <kenney digital-audio dir> [demos/particles]

Everything is drawn here; the sounds are Kenney's (CC0). Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

da = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "demos", "particles")
d = Demo(out, ["scenes", "events"], "f1000000")
W, H = 960, 540

def panel(w, h, fill, edge, radius=3):
    img = canvas(w, h)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=edge, width=2)
    return img

STONE, STONE_EDGE = (110, 112, 124, 255), (66, 68, 78, 255)
d.sprite("Floor", 640, 20, [("still", [panel(640, 20, STONE, STONE_EDGE, 0)], 400, "loop")], [box("body", 320, 10, 640, 20)])
d.sprite("Side", 20, 280, [("still", [panel(20, 280, STONE, STONE_EDGE, 0)], 400, "loop")], [box("body", 10, 140, 20, 280)])
d.sprite("Shelf", 160, 14, [("still", [panel(160, 14, STONE, STONE_EDGE, 2)], 400, "loop")], [box("body", 80, 7, 160, 14)])
crate = panel(30, 30, (196, 140, 82, 255), (100, 64, 34, 255), 2)
ImageDraw.Draw(crate).line([4, 4, 25, 25], fill=(100, 64, 34, 255), width=2)
d.sprite("Crate", 30, 30, [("still", [crate], 400, "loop")], [box("body", 15, 15, 30, 30, density=0.5)])
# One particle each: a soft dot, tinted by the particle's own colour when drawn.
d.sprite("Drop", 16, 16, [("still", [soft_dot(16, (255, 255, 255), 0.8)], 400, "loop")], [])
d.sprite("Grain", 12, 12, [("still", [soft_dot(12, (255, 255, 255), 0.4)], 400, "loop")], [])
d.sprite("Spark", 10, 10, [("still", [soft_dot(10, (255, 255, 255), 1.6)], 400, "loop")], [])
tap = canvas(40, 30)
g = ImageDraw.Draw(tap)
g.rectangle([0, 6, 30, 16], fill=(170, 175, 190, 255), outline=(90, 92, 104, 255))
g.rectangle([22, 6, 32, 29], fill=(170, 175, 190, 255), outline=(90, 92, 104, 255))
d.sprite("Tap", 40, 30, [("still", [tap], 400, "loop")], [])
hopper = canvas(50, 40)
ImageDraw.Draw(hopper).polygon([(0, 0), (49, 0), (30, 39), (19, 39)], fill=(150, 120, 80, 255), outline=(90, 70, 40, 255))
d.sprite("Hopper", 50, 40, [("still", [hopper], 400, "loop")], [])
grinder = canvas(36, 36)
ImageDraw.Draw(grinder).ellipse([1, 1, 34, 34], fill=(120, 120, 130, 255), outline=(60, 60, 66, 255), width=3)
d.sprite("Grinder", 36, 36, [("still", [grinder], 400, "loop")], [])
plug = canvas(60, 10)
ImageDraw.Draw(plug).rectangle([0, 0, 59, 9], fill=(30, 30, 36, 255))
d.sprite("Plug", 60, 10, [("still", [plug], 400, "loop")], [box("hole", 30, 5, 60, 10, sensor=True)])
d.sprite("Breeze", 260, 100, [("still", [panel(260, 100, (255, 255, 255, 16), (255, 255, 255, 40), 8)], 400, "loop")], [box("air", 130, 50, 260, 100, sensor=True)])

d.sounds({"splash": (da, "phaserDown2.ogg"), "click": (da, "pepSound1.ogg")})

SOLID, BODY, DRAIN, AIR = 1, 2, 4, 8
EVERYTHING = -1
for name in ["Floor", "Side", "Shelf"]:
    d.type_json(name, "Sprite", {"spriteKey": name + ".sprite.json", "collision": {"layer": SOLID, "mask": EVERYTHING}})
d.type_json("Crate", "Sprite", {"spriteKey": "Crate.sprite.json", "collision": {"layer": BODY, "mask": SOLID | BODY}},
            [{"componentClass": "PhysicsBody", "bodyType": "Dynamic"}, {"componentClass": "DragRules"}])
def fluid(**k): return dict({"componentClass": "Fluid", "layers": SOLID | BODY}, **k)
d.type_json("Water", "Sprite", {"spriteKey": "Drop.sprite.json", "collisionEnabled": False},
            [fluid(kind="Water", radius=5, maxCount=3500, pictureScale=2.6, color=0x4AA8FF, viscosity=0.2), {"componentClass": "WaterReadout"}])
d.type_json("Sand", "Sprite", {"spriteKey": "Grain.sprite.json", "collisionEnabled": False},
            [fluid(kind="Powder", radius=5, maxCount=2000, pictureScale=1.8, color=0xD9B56B, density=1.6), {"componentClass": "SandReadout"}])
d.type_json("Sparks", "Sprite", {"spriteKey": "Spark.sprite.json", "collisionEnabled": False, "blendMode": "add"},
            [fluid(kind="Water", radius=3, maxCount=600, pressure=0, viscosity=0, coupling=0, gravityScale=0.6, lifetime=1.2,
                   fadeOut=True, colorOverLife=True, color=0xFFE27A, endColor=0xC02810, pictureScale=2)])
def emitter(**k): return dict({"componentClass": "Emitter"}, **k)
d.type_json("Tap", "Sprite", {"spriteKey": "Tap.sprite.json", "collisionEnabled": False},
            [emitter(system="Water1", group="tap", on=True, rate=100, speed=300, speedVariation=0.1, spread=4, shape="Line", width=30)])
d.type_json("Hopper", "Sprite", {"spriteKey": "Hopper.sprite.json", "collisionEnabled": False},
            [emitter(system="Sand1", group="hopper", on=False, rate=70, speed=240, speedVariation=0.1, spread=6, shape="Line", width=30)])
d.type_json("Grinder", "Sprite", {"spriteKey": "Grinder.sprite.json", "collisionEnabled": False},
            [emitter(system="Sparks1", group="sparks", on=True, rate=90, speed=280, speedVariation=0.4, spread=50), {"componentClass": "Rotate", "speed": 360}])
d.type_json("Plug", "Sprite", {"spriteKey": "Plug.sprite.json", "collision": {"layer": DRAIN, "mask": 0}},
            [{"componentClass": "Drain", "system": "Water1", "on": False}])
d.type_json("Breeze", "Sprite", {"spriteKey": "Breeze.sprite.json", "collision": {"layer": AIR, "mask": 0}},
            [{"componentClass": "Field", "kind": "Wind", "strength": 0, "affects": "Particles"}])
d.type_json("Level", "Node", {}, [{"componentClass": "LevelRules"}])
for name, size in [("Help", 13), ("Caption", 13), ("Readout", 13)]:
    d.type_json(name, "Label", {"text": "", "fontSize": size})
for name in ["WaterCount", "SandCount", "StepTime"]:
    d.type_json(name, "Label", {"text": "0", "fontSize": 13})

objects = [{"id": d.uid(1), "name": "Basin"}]
n = [10]
def place(name, type_name, x, y, **extra):
    n[0] += 1
    objects.append(dict({"id": d.uid(n[0]), "parent": d.uid(1), "name": name, "type": type_name, "x": x, "y": y}, **extra))
place("Level1", "Level", 0, 0)
place("Floor1", "Floor", 0, 240)
place("SideL", "Side", -330, 110); place("SideR", "Side", 330, 110)
place("Shelf1", "Shelf", 200, 60)
# The fluids' own objects: their pictures stand in the corner until they have particles.
place("Water1", "Water", -440, 200); place("Sand1", "Sand", -440, 222); place("Sparks1", "Sparks", -440, 244)
place("Tap1", "Tap", -230, -210, rotation=math.pi / 2)
place("Hopper1", "Hopper", 200, -200, rotation=math.pi / 2)
place("Grinder1", "Grinder", 400, -120, rotation=math.pi * 0.85)
place("Plug1", "Plug", -60, 232)
place("Breeze1", "Breeze", 0, -40)
place("Help1", "Help", -470, -262, text="W: the tap   S: the sand   D: the plughole   F: the fan   C: clear   click: splash   right click: pour   drag: the crates")
place("WaterCaption", "Caption", 380, -262, text="Water"); place("WaterCount1", "WaterCount", 430, -262)
place("SandCaption", "Caption", 380, -244, text="Sand"); place("SandCount1", "SandCount", 430, -244)
place("StepCaption", "Caption", 380, -226, text="ms"); place("StepTime1", "StepTime", 430, -226)
d.scene("scenes/Basin.scene.json", objects)

px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def body_(scope, name, *params, **k): return comp(scope, "PhysicsBody", name, *params, **k)
d.write("events/DragRules.vscript.json", {"rules": [
    rule([mouse_pressed(LEFT_BUTTON), line("self", "Node", "containsPoint", px, py)], [body_("self", "dragToward", px, py)]),
    rule([mouse_down(LEFT_BUTTON), body_("self", "isDragged")], [body_("self", "dragToward", px, py)]),
    rule([not_(mouse_down(LEFT_BUTTON)), body_("self", "isDragged")], [body_("self", "releaseDrag")]),
]})

def toggle(key, flag, on, off):
    """A key that switches something on and off, through a variable: 2 means 'just switched on', so the off rule waits a step."""
    return [
        rule([pressed(key), compare(var(flag), EQ, lit(0))], [line("variables", "Variables", "setVariable", s(flag), lit(2))] + on),
        rule([pressed(key), compare(var(flag), EQ, lit(1))], [line("variables", "Variables", "setVariable", s(flag), lit(0))] + off),
        rule([compare(var(flag), EQ, lit(2))], [line("variables", "Variables", "setVariable", s(flag), lit(1))]),
    ]
click = line("audio", "Audio", "playSound", s("click"))
level_rules = (
    # The tap starts on: its flag starts at 1 (see the variables below).
    toggle("Tap", "tap", [comp("Tap", "Emitter", "setOn", b(True)), click], [comp("Tap", "Emitter", "setOn", b(False)), click])
    + toggle("Sand", "sand", [comp("Hopper", "Emitter", "setOn", b(True)), click], [comp("Hopper", "Emitter", "setOn", b(False)), click])
    + toggle("Drain", "drain", [comp("Plug", "Drain", "setOn", b(True)), click], [comp("Plug", "Drain", "setOn", b(False)), click])
    + toggle("Fan", "fan", [comp("Breeze", "Field", "setStrength", lit(500)), click], [comp("Breeze", "Field", "setStrength", lit(0)), click])
    + [
        rule([once()], [line("variables", "Variables", "setVariable", s("tap"), lit(1)), sheet("preloadObjectType", s("Crate"))]),
        # The crates come once there is water to float them: something resting on the floor has none under it.
        rule([compare(value("system", "System", "getElapsedTime"), GT, lit(6)), once()], [], [
            rule([system("repeat", lit(3))], [sheet("createObject", s("Crate"), lit(0)), line("Crate", "Node", "setPosition", random(-250, 120), lit(-180))])]),
        rule([pressed("Clear")], [comp("Water", "Fluid", "destroyAll"), comp("Sand", "Fluid", "destroyAll"), click]),
        rule([mouse_pressed(LEFT_BUTTON)], [comp("Water", "Fluid", "pushInCircle", px, py, lit(70), lit(0), lit(-450)),
                                            comp("Sand", "Fluid", "pushInCircle", px, py, lit(70), lit(0), lit(-300)), line("audio", "Audio", "playSound", s("splash"))]),
        rule([mouse_pressed(RIGHT_BUTTON)], [comp("Water", "Fluid", "makeInCircle", px, py, lit(24), s("poured"))]),
    ])
d.write("events/LevelRules.vscript.json", {"rules": level_rules})
# The readouts: each fluid says its own count; the water leaves its step time for the sand to add its own to.
d.write("events/WaterReadout.vscript.json", {"rules": [rule([], [
    line("WaterCount", "Label", "setNumber", cvalue("self", "Fluid", "particleCount")),
    line("variables", "Variables", "setVariable", s("waterMs"), cvalue("self", "Fluid", "stepTime"))])]})
d.write("events/SandReadout.vscript.json", {"rules": [rule([], [
    line("SandCount", "Label", "setNumber", cvalue("self", "Fluid", "particleCount")),
    line("StepTime", "Label", "setNumber", op("+", var("waterMs"), cvalue("self", "Fluid", "stepTime")))])]})

d.write("project.json", {"schemaVersion": 2, "name": "Particles demo", "entryScene": "scenes/Basin.scene.json",
    "collisionLayers": {"1": "Solid", "2": "Body", "3": "Drain", "4": "Air"},
    "input": {"Tap": keys(87), "Sand": keys(83), "Drain": keys(68), "Fan": keys(70), "Clear": keys(67)},
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "box2d", "gravity": 980}})
d.write("README.md", """# Particles demo

A basin of water, sand and sparks. Each is a sprite with a **Fluid**
behaviour: the sprite's picture is drawn once per particle, tinted by the
particle's colour, and the behaviour holds the settings (its **Kind**: Water,
Powder for the sand, and water with no pressure, a lifetime and colour over
life for the sparks).

- **W** turns the tap on and off, **S** the sand hopper (both **Emitters**
  that name the object carrying the Fluid).
- **D** opens the plughole, a **Drain**.
- **F** starts the fan, a **Field** set to Wind that pushes particles.
- **C** clears the basin.
- **Click** to splash (**Push particles in a circle**), **right click** to
  pour a drop (**Make particles in a circle**), and drag the crates.

On Box2D, so the water pushes the crates and they push back. The crates
are dropped in once the basin has water, six seconds in.

Generated by `tools/make-particles-demo.py`; the pictures are drawn there and
the sounds are Kenney's (Digital Audio), CC0.
""")
print("wrote", d.out)
