"""The particles demo: water, sand and sparks, each a sprite carrying a Fluid
behavior whose picture is drawn once per particle. A tap and a hopper pour
through Emitters, a plughole drains through a Drain, a fan blows across the
basin through a Field, crates float and can be dragged, and the mouse
splashes and pours. On Box2D, so the water pushes the crates and they push
back.

    python3 tools/make-particles-demo.py <kenney digital-audio dir> [demos/particles]

Everything is drawn here but the pictures in tools/art: the animals and the sounds are Kenney's (CC0),
the forest is the project's own. Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

da = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "demos", "particles")
d = Demo(out, ["scenes/singletons", "vscript"], "f1000000")
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
# One particle each: a soft dot, tinted by the particle's own color when drawn.
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
peg = canvas(18, 18)
ImageDraw.Draw(peg).ellipse([1, 1, 16, 16], fill=STONE, outline=STONE_EDGE, width=2)
d.sprite("Peg", 18, 18, [("still", [peg], 400, "loop")], [circle("body", 9, 9, 9)])
# Pictures to turn into particles: Kenney's animal heads (Animal Pack Redux, CC0), at their own size.
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art")
for pic in ["Frog", "Pig", "Panda"]:
    im = Image.open(os.path.join(ART, "kenney-%s.png" % pic.lower())).convert("RGBA")
    d.sprite(pic, im.width, im.height, [("still", [im], 400, "loop")], [])
# A particle drawn as a small square: a picture turned into particles then looks like the picture,
# at the particles' size, rather than a blur of overlapping dots.
d.sprite("Pixel", 8, 8, [("still", [Image.new("RGBA", (8, 8), (255, 255, 255, 255))], 400, "loop")], [])

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
    d.type_json(name, "Label", {"text": "", "fontSize": size, "shadow": True})
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
d.write("vscript/DragRules.vscript.json", {"rules": [
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
d.write("vscript/LevelRules.vscript.json", {"rules": level_rules})
# The readouts: each fluid says its own count; the water leaves its step time for the sand to add its own to.
d.write("vscript/WaterReadout.vscript.json", {"rules": [rule([], [
    line("WaterCount", "Label", "setNumber", cvalue("self", "Fluid", "particleCount")),
    line("variables", "Variables", "setVariable", s("waterMs"), cvalue("self", "Fluid", "stepTime"))])]})
d.write("vscript/SandReadout.vscript.json", {"rules": [rule([], [
    line("SandCount", "Label", "setNumber", cvalue("self", "Fluid", "particleCount")),
    line("StepTime", "Label", "setNumber", op("+", var("waterMs"), cvalue("self", "Fluid", "stepTime")))])]})

# ── the feature scenes: one each, named for what it shows ──
MOULD = 16
d.type_json("Peg", "Sprite", {"spriteKey": "Peg.sprite.json", "collision": {"layer": SOLID, "mask": EVERYTHING}})
# A hidden shape that particles are laid in (Fill with particles) and that nothing meets: a pool or a block
# placed in the scene, rather than at coordinates (the Fluid works in the physics world's space, which in a
# running game is offset from the scene's by the camera; see the engine's TODO).
d.type_json("Mold", "Node", {"collision": {"layer": MOULD, "mask": 0, "shapes": [box("shape", 0, 0, 20, 20)]}})
d.type_json("Dropper", "Node", {"collision": {"layer": MOULD, "mask": 0, "shapes": [box("shape", 0, 0, 20, 20)]}})
for pic in ["Frog", "Pig", "Panda"]:
    d.type_json(pic, "Sprite", {"spriteKey": pic + ".sprite.json", "collisionEnabled": False})
def water_type(name, picture="Drop", readout=None, **k):
    extra = []
    if readout:
        # A fluid says its own numbers: a value is read in the sheet of the object it belongs to.
        extra = [{"componentClass": name + "Readout"}]
        d.write("vscript/%sReadout.vscript.json" % name, {"rules": readout})
    d.type_json(name, "Sprite", {"spriteKey": picture + ".sprite.json", "collisionEnabled": False}, [fluid(**dict({"kind": "Water", "radius": 4, "pictureScale": 2.6}, **k))] + extra)
water_type("PoolOnePass", maxCount=1500, color=0x4AA8FF, substeps=1, sleep=False,
           readout=[rule([], [line("OneMs", "Label", "setNumber", cvalue("self", "Fluid", "stepTime"))])])
water_type("PoolPasses", maxCount=1500, color=0x4AA8FF, substeps=0, sleep=False,
           readout=[rule([], [line("PassesMs", "Label", "setNumber", cvalue("self", "Fluid", "stepTime")),
                             line("PassCount", "Label", "setNumber", cvalue("self", "Fluid", "passes"))])])
water_type("StillWater", radius=5, maxCount=1500, color=0x4AA8FF, readout=[
    rule([], [line("StillMs", "Label", "setNumber", cvalue("self", "Fluid", "stepTime"))]),
    rule([comp("self", "Fluid", "isAsleep")], [line("SleepState", "Label", "setText", s("asleep: nothing is stepped"))]),
    rule([not_(comp("self", "Fluid", "isAsleep"))], [line("SleepState", "Label", "setText", s("awake"))])])
water_type("Jelly", maxCount=2500, color=0x7CE06A, pictureScale=2.2, stiffness=0.3)
water_type("Net", maxCount=2500, color=0xD79BFF, pictureScale=2.2, stiffness=0.25)
water_type("Walled", maxCount=2500, color=0x4AA8FF)
water_type("OilWater", maxCount=2500)
water_type("Mixing", maxCount=2500, colorMixing=0.5)
water_type("Foam", maxCount=2500, color=0x1E5AA8, colorBySpeed=True, speedColor=0xFFFFFF, fullSpeed=380)
water_type("Bits", picture="Pixel", radius=2, maxCount=6000, pictureScale=1.15, stiffness=0.35)
d.type_json("CupTap", "Sprite", {"spriteKey": "Tap.sprite.json", "collisionEnabled": False},
            [emitter(system="Walled1", group="water", on=True, rate=60, speed=250, spread=4, shape="Line", width=20)])
d.type_json("FoamTap", "Sprite", {"spriteKey": "Tap.sprite.json", "collisionEnabled": False},
            [emitter(system="Foam1", group="water", on=True, rate=110, speed=420, speedVariation=0.1, spread=6, shape="Line", width=24)])
d.type_json("FoamPlug", "Sprite", {"spriteKey": "Plug.sprite.json", "collision": {"layer": DRAIN, "mask": 0}},
            [{"componentClass": "Drain", "system": "Foam1", "on": True}])
d.type_json("Stirrer", "Sprite", {"spriteKey": "Grinder.sprite.json", "collisionEnabled": False},
            [{"componentClass": "Field", "kind": "Vortex", "strength": 0, "range": 170, "pull": 0.2, "affects": "Particles"}, {"componentClass": "Rotate", "speed": 0}])
for name in ["OneMs", "PassesMs", "PassCount", "StillMs", "SleepState"]:
    d.type_json(name, "Label", {"text": "", "fontSize": 13})

def mould(place, name, cx, cy, w, h, type_name="Mold", **extra):
    place(name, type_name, cx, cy, scaleX=w / 20, scaleY=h / 20, **extra)
def fill(t, mould_name, group): return fl(t, "fillObject", s(mould_name), group if isinstance(group, dict) else s(group))

def tank(place, cx, floor_y, width, height, tag):
    """A floor and two sides around a box of open water `width` across and `height` deep."""
    place("Floor" + tag, "Floor", cx, floor_y, scaleX=(width + 40) / 640)
    for side, sx in [("L", -1), ("R", 1)]:
        place("Side" + side + tag, "Side", cx + sx * (width / 2 + 10), floor_y - 10 - height / 2, scaleY=height / 280)

FEATURES = []
def feature(file, title, about, controls, build, rules):
    """A scene: its own objects under one root, a Level whose sheet holds its rules, and two lines saying what it shows."""
    seq = [0]
    root = d.uid(2000 + len(FEATURES) * 100)
    objects = [{"id": root, "name": file}]
    def place(name, type_name, x, y, **extra):
        seq[0] += 1
        objects.append(dict({"id": d.uid(2000 + len(FEATURES) * 100 + seq[0]), "parent": root, "name": name, "type": type_name, "x": x, "y": y}, **extra))
    sheet_name = file + "Rules"
    level = file + "Level"
    d.type_json(level, "Node", {}, [{"componentClass": sheet_name}])
    place(level + "1", level, 0, 0)
    place("Title", "Caption", -470, -262, text=title)
    lines = about if isinstance(about, list) else [about]
    for k, text in enumerate(lines): place("About%d" % (k + 1), "Help", -470, -244 + 18 * k, text=text)
    place("Controls", "Help", -470, -244 + 18 * len(lines), text=controls)
    build(place)
    d.scene("scenes/%s.scene.json" % file, objects)
    d.write("vscript/%s.vscript.json" % sheet_name, {"rules": rules})
    FEATURES.append((file, title))

def fl(t, name, *params): return comp(t, "Fluid", name, *params)
splash = lambda t: rule([mouse_pressed(LEFT_BUTTON)], [fl(t, "pushInCircle", px, py, lit(70), lit(0), lit(-450)), line("audio", "Audio", "playSound", s("splash"))])
pour = lambda t, g: rule([mouse_pressed(RIGHT_BUTTON)], [fl(t, "makeInCircle", px, py, lit(22), s(g))])

def deep(place):
    # Their tops below the lines of help.
    tank(place, -200, 240, 180, 400, "A"); tank(place, 200, 240, 180, 400, "B")
    place("PoolOnePass1", "PoolOnePass", -460, 250); place("PoolPasses1", "PoolPasses", -460, 250)
    mould(place, "PoolA", -200, 30, 170, 380); mould(place, "PoolB", 200, 30, 170, 380)
    place("LeftCaption", "Caption", -290, -150, text="One pass a step, ms:"); place("OneMs1", "OneMs", -150, -150)
    # The solver says how many passes it worked out: "3 passes a step, ms: 4".
    place("PassCount1", "PassCount", 110, -150); place("RightCaption", "Caption", 122, -150, text="passes a step, ms:"); place("PassesMs1", "PassesMs", 265, -150)
fill_deep = [fl("PoolOnePass", "destroyAll"), fl("PoolPasses", "destroyAll"),
             fill("PoolOnePass", "PoolA", "pool"), fill("PoolPasses", "PoolB", "pool")]
feature("DeepPoolInPasses", "Deep pool in passes",
        ["The same deep pool twice. Left, the solver runs once a step: the pool packs down and churns.",
         "Right, the solver works its passes out from gravity and the radius (Substeps 0): it keeps its depth and lies still."],
        "Space fills both again.   Click to splash.   The numbers are each pool's step time, milliseconds.",
        deep,
        [rule([once()], fill_deep), rule([pressed("Act")], fill_deep),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("PoolOnePass", "pushInCircle", px, py, lit(60), lit(0), lit(-450)), fl("PoolPasses", "pushInCircle", px, py, lit(60), lit(0), lit(-450))])])

def still(place):
    tank(place, 0, 240, 600, 200, "")
    place("StillWater1", "StillWater", -460, 250)
    mould(place, "Pool", 0, 175, 590, 110)
    place("StateCaption", "Caption", -100, -150, text="The pool is"); place("SleepState1", "SleepState", -10, -150)
    place("MsCaption", "Caption", -100, -132, text="Step time, ms:"); place("StillMs1", "StillMs", 10, -132)
feature("SettledPoolSleeps", "A settled pool sleeps",
        ["Leave the pool alone: once every particle has stayed slow for two seconds the whole system sleeps,",
         "and its step costs nothing until something disturbs it."],
        "Click to splash and wake it.   Right click to pour a drop in.",
        still,
        [rule([once()], [fill("StillWater", "Pool", "pool")]),
         splash("StillWater"), pour("StillWater", "poured")])

def jelly_drop(where):
    group = op("+", s("jelly"), var("blocks"))
    return [line("variables", "Variables", "setVariable", s("blocks"), op("+", var("blocks"), lit(1))),
            fill("Jelly", where, group), fl("Jelly", "setGroupKind", group, lit(1))]
def jelly(place):
    tank(place, 0, 240, 640, 260, "")
    place("Jelly1", "Jelly", -460, 250)
    place("Ramp", "Shelf", -150, 70, rotation=0.35, scaleX=1.6); place("Step", "Shelf", 170, 150, scaleX=1.2)
    for name, x in [("BlockA", -200), ("BlockB", 0), ("BlockC", 200)]: mould(place, name, x, -170, 56, 48)
    mould(place, "Dropper1", 0, -170, 56, 48, "Dropper")
feature("ElasticJelly", "Elastic jelly",
        ["Each block is a group made elastic: it keeps the shape it was made in, squashes when it lands and springs back,",
         "and slides off the ramp whole."],
        "Space drops another block.   Click to knock them about.",
        jelly,
        [rule([once()], [line("variables", "Variables", "setVariable", s("blocks"), lit(0))] + jelly_drop("BlockA") + jelly_drop("BlockB") + jelly_drop("BlockC")),
         rule([pressed("Act")], [line("Dropper", "Node", "setPosition", random(-260, 260), lit(-170))] + jelly_drop("Dropper1")),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("Jelly", "pushInCircle", px, py, lit(80), lit(0), lit(-500))])])

def net_drop():
    group = op("+", s("net"), var("nets"))
    return [line("variables", "Variables", "setVariable", s("nets"), op("+", var("nets"), lit(1))),
            fill("Net", "Strip", group), fl("Net", "setGroupKind", group, lit(2))]
def net(place):
    tank(place, 0, 240, 640, 260, "")
    place("Net1", "Net", -460, 250)
    mould(place, "Strip", 0, -170, 380, 20)
    for i, (x, y) in enumerate([(-150, 40), (0, 90), (150, 40)]):
        place("Peg%d" % (i + 1), "Peg", x, y)
feature("SpringNet", "Spring net",
        ["A strip made a spring group: every neighbor pair keeps its length and nothing more,", "so it falls like a net and drapes over the pegs."],
        "Space drops another net.   Click to toss them.",
        net,
        [rule([once()], [line("variables", "Variables", "setVariable", s("nets"), lit(0))] + net_drop()),
         rule([pressed("Act")], net_drop()),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("Net", "pushInCircle", px, py, lit(90), lit(0), lit(-500))])])

cup_build = [fl("Walled", "destroyAll"), fl("Walled", "fillObject", s("CupBase"), s("cup")), fl("Walled", "fillObject", s("CupLeft"), s("cup")),
             fl("Walled", "fillObject", s("CupRight"), s("cup")), fl("Walled", "setGroupKind", s("cup"), lit(3)), fl("Walled", "colorGroup", s("cup"), lit(0xA0A4B0))]
def walls(place):
    tank(place, 0, 240, 640, 200, "")
    place("Walled1", "Walled", -460, 250)
    place("CupBase", "Mold", 0, 120, scaleX=11, scaleY=0.8)
    place("CupLeft", "Mold", -118, 50, rotation=-0.35, scaleX=0.8, scaleY=7.5)
    place("CupRight", "Mold", 118, 50, rotation=0.35, scaleX=0.8, scaleY=7.5)
    place("CupTap1", "CupTap", -10, -160, rotation=math.pi / 2)
feature("WallsOfParticles", "Walls made of particles",
        ["The cup is particles laid in three hidden shapes and made a wall group: they stand where they are,", "and the water poured in rests on them."],
        "Space makes the cup plain water, and it gives way.   R builds it again.   Click to splash.",
        walls,
        [rule([once()], cup_build), rule([pressed("Reset")], cup_build),
         rule([pressed("Act")], [fl("Walled", "setGroupKind", s("cup"), lit(0)), fl("Walled", "colorGroup", s("cup"), lit(0x4AA8FF)), click]),
         splash("Walled")])

oil_start = [fl("OilWater", "destroyAll"),
             fl("OilWater", "setColor", lit(0x4AA8FF)), fill("OilWater", "WaterSpot", "water"),
             fl("OilWater", "setColor", lit(0xE8B23A)), fill("OilWater", "OilSpot", "oil"),
             fl("OilWater", "setGroupKind", s("oil"), lit(4))]
def oil(place):
    tank(place, 0, 240, 520, 240, "")
    place("OilWater1", "OilWater", -460, 250)
    mould(place, "WaterSpot", -120, 150, 230, 150); mould(place, "OilSpot", 120, 150, 230, 150); mould(place, "OilDrop", 0, -120, 70, 70)
feature("OilAndWaterRepel", "Oil and water repel",
        ["Two groups in one fluid, the amber one made repulsive: it pushes the blue away wherever they meet,", "so however hard they are stirred they part again."],
        "Click to splash them together.   Space pours more oil into the middle.   R starts again.",
        oil,
        [rule([once()], oil_start), rule([pressed("Reset")], oil_start),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("OilWater", "pushInCircle", px, py, lit(110), lit(0), lit(-500))]),
         rule([pressed("Act")], [fl("OilWater", "setColor", lit(0xE8B23A)), fill("OilWater", "OilDrop", "oil"),
                                 fl("OilWater", "setGroupKind", s("oil"), lit(4))])])

mix_start = [fl("Mixing", "destroyAll"),
             fl("Mixing", "setColor", lit(0xE8324A)), fill("Mixing", "RedSpot", "red"),
             fl("Mixing", "setColor", lit(0x3A62F0)), fill("Mixing", "BlueSpot", "blue")]
def mixing(place):
    tank(place, 0, 240, 520, 240, "")
    place("Mixing1", "Mixing", -460, 250)
    mould(place, "RedSpot", -120, 150, 230, 150); mould(place, "BlueSpot", 120, 150, 230, 150)
    place("Stirrer1", "Stirrer", 0, 160)
feature("ColorMixing", "Color mixing",
        ["Red and blue water with Color mixing on: touching particles' colors drift toward each other's,", "so where they meet it turns purple, and stirred it all does."],
        "Space starts and stops the stirrer.   Click to splash.   R starts again.",
        mixing,
        [rule([once()], mix_start + [line("variables", "Variables", "setVariable", s("stir"), lit(0))]), rule([pressed("Reset")], mix_start)]
        + toggle("Act", "stir", [comp("Stirrer", "Field", "setStrength", lit(900)), comp("Stirrer", "Rotate", "setSpeed", lit(240)), click],
                 [comp("Stirrer", "Field", "setStrength", lit(0)), comp("Stirrer", "Rotate", "setSpeed", lit(0)), click])
        + [splash("Mixing")])

def foam(place):
    tank(place, 0, 240, 640, 180, "")
    place("Foam1", "Foam", -460, 250)
    mould(place, "FoamPool", 0, 190, 630, 80)
    place("FoamTap1", "FoamTap", -200, -160, rotation=math.pi / 2)
    place("FoamPlug1", "FoamPlug", 220, 232)
feature("ColorBySpeed", "Color by speed",
        ["Deep blue water drawn toward white the faster each particle goes (Color by speed):", "the falling stream and every splash foam, and the pool settles dark."],
        "Space turns the tap on and off.   Click to splash.",
        foam,
        [rule([once()], [line("variables", "Variables", "setVariable", s("foamtap"), lit(1)), fill("Foam", "FoamPool", "pool")])]
        + toggle("Act", "foamtap", [comp("FoamTap", "Emitter", "setOn", b(True)), click], [comp("FoamTap", "Emitter", "setOn", b(False)), click])
        + [splash("Foam")])

PICTURES = [("Frog1", "frog"), ("Pig1", "pig"), ("Panda1", "panda")]
def into(place):
    tank(place, 0, 240, 640, 200, "")
    place("Bits1", "Bits", -460, 250)
    for (name, _), x in zip(PICTURES, [-200, 0, 200]):
        place(name, name[:-1], x, -40)
feature("ObjectsIntoParticles", "Objects into particles",
        ["Turn into particles puts a particle wherever an object's picture is opaque, colored from its pixel.",
         "Made elastic, the pictures fall and bounce looking like themselves; left as water, they melt."],
        "E turns them into elastic particles.   M melts them into water.   R puts them back.   Click to knock the pieces about.",
        into,
        [rule([pressed("Elastic")], [a for name, g in PICTURES for a in (fl("Bits", "turnIntoParticles", s(name), s(g), lit(128), lit(1)), fl("Bits", "setGroupKind", s(g), lit(1)))] + [click]),
         # Melting makes jelly plain water again, and turns a picture still whole straight into water.
         rule([pressed("Melt")], [a for name, g in PICTURES for a in (fl("Bits", "setGroupKind", s(g), lit(0)), fl("Bits", "turnIntoParticles", s(name), s(g), lit(128), lit(1)))] + [click]),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("Bits", "pushInCircle", px, py, lit(80), lit(0), lit(-500))]),
         rule([pressed("Reset")], [line("Scenes", "SceneManager", "changeScene", s("scenes/ObjectsIntoParticles.scene.json"))])])

# A whole picture into particles, then what they become, by key: water, jelly, colors that mix, a soft
# net, honey; each turns the picture into particles first if it is still whole. (Sand was one: Powder
# steps three times slower, too slow for a picture this size.)
forest = Image.open(os.path.join(ART, "forest-deer.png")).convert("RGBA")
d.sprite("Forest", forest.width, forest.height, [("still", [forest], 400, "loop")], [])
d.type_json("Forest", "Sprite", {"spriteKey": "Forest.sprite.json", "collisionEnabled": False})
water_type("Flood", picture="Pixel", radius=2, maxCount=20000, pictureScale=1.15,
           readout=[rule([], [line("WaterCount", "Label", "setNumber", cvalue("self", "Fluid", "particleCount")),
                              line("StepTime", "Label", "setNumber", cvalue("self", "Fluid", "stepTime"))])])
def picture(place):
    # Walls start below the captions, just above the picture; its water fills less than that.
    tank(place, 0, 262, 912, 440, "")
    place("Flood1", "Flood", -500, 250)
    place("Forest1", "Forest", 0, 60, scaleX=0.8, scaleY=0.8)
    place("Stirrer1", "Stirrer", 0, 170, visible=False)
    place("CountCaption", "Caption", 380, -262, text="Particles"); place("WaterCount1", "WaterCount", 440, -262)
    place("StepCaption", "Caption", 380, -244, text="ms"); place("StepTime1", "StepTime", 440, -244)
melt = fl("Flood", "turnIntoParticles", s("Forest1"), s("picture"), lit(128), lit(1))
calm = [comp("Stirrer", "Field", "setStrength", lit(0)), comp("Stirrer", "Rotate", "setSpeed", lit(0)), line("Stirrer", "Node", "hide")]
def mode(key, *actions):
    return rule([pressed(key)], [melt] + list(actions) + [click])
water = [fl("Flood", "setKind", s("Water")), fl("Flood", "setViscosity", lit(0.25)), fl("Flood", "setColorMixing", lit(0))]
feature("PictureIntoWater", "A picture into particles",
        ["Turn into particles on a whole picture, each particle colored from its pixel, then choose what they become."],
        "Q water   W jelly   E colors that mix, stirred   R a soft net   T honey   P puts it back   Click to splash",
        picture,
        [mode("PictureWater", *water, fl("Flood", "setGroupKind", s("picture"), lit(0)), *calm),
         mode("PictureJelly", *water, fl("Flood", "setGroupKind", s("picture"), lit(1)), *calm),
         mode("PictureMix", fl("Flood", "setKind", s("Water")), fl("Flood", "setViscosity", lit(0.25)), fl("Flood", "setColorMixing", lit(0.5)),
              fl("Flood", "setGroupKind", s("picture"), lit(0)), comp("Stirrer", "Field", "setStrength", lit(900)), comp("Stirrer", "Rotate", "setSpeed", lit(240)), line("Stirrer", "Node", "show")),
         mode("PictureNet", *water, fl("Flood", "setGroupKind", s("picture"), lit(2)), *calm),
         mode("PictureHoney", fl("Flood", "setKind", s("Water")), fl("Flood", "setViscosity", lit(4)), fl("Flood", "setColorMixing", lit(0)),
              fl("Flood", "setGroupKind", s("picture"), lit(0)), *calm),
         rule([mouse_pressed(LEFT_BUTTON)], [fl("Flood", "pushInCircle", px, py, lit(80), lit(0), lit(-500)), line("audio", "Audio", "playSound", s("splash"))])])

# ── the singleton: the Scene Manager, the keys that change scene, and the list of scenes ──
SCENES = [("Basin", "Basin")] + FEATURES
d.type_json("Scenes", "SceneManager", {"transition": "Fade", "fadeTime": 0.15})
d.type_json("Switcher", "Node", {}, [{"componentClass": "SwitchRules"}])
d.type_json("SceneList", "Label", {"text": "", "fontSize": 13, "shadow": True})
# 1 to 9 and 0, then P for the picture.
keys_for = [str((i + 1) % 10) for i in range(min(10, len(SCENES)))] + ["P"] * (len(SCENES) > 10)
named = ["%s %s" % (k, title) for k, (_, title) in zip(keys_for, SCENES)]
listing = "   ".join(named[:6]) + "\n" + "   ".join(named[6:])
d.scene("scenes/singletons/Demo.scene.json", [
    {"id": d.uid(3001), "name": "Demo"},
    {"id": d.uid(3002), "parent": d.uid(3001), "name": "Scenes1", "type": "Scenes"},
    {"id": d.uid(3003), "parent": d.uid(3001), "name": "Switcher1", "type": "Switcher"},
    {"id": d.uid(3004), "parent": d.uid(3001), "name": "SceneList1", "type": "SceneList", "x": -470, "y": 238, "text": listing},
])
d.write("vscript/SwitchRules.vscript.json", {"rules": [
    rule([pressed("Scene" + k)], [line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % f))]) for k, (f, _) in zip(keys_for, SCENES)]})

d.write("project.json", {"schemaVersion": 2, "name": "Particles demo", "entryScene": "scenes/Basin.scene.json",
    "collisionLayers": {"1": "Solid", "2": "Body", "3": "Drain", "4": "Air", "5": "Mold"},
    "singletons": ["scenes/singletons/Demo.scene.json"],
    "input": dict({"Tap": keys(87), "Sand": keys(83), "Drain": keys(68), "Fan": keys(70), "Clear": keys(67),
                   "Act": keys(32), "Elastic": keys(69), "Melt": keys(77), "Reset": keys(82),
                   "PictureWater": keys(81), "PictureJelly": keys(87), "PictureMix": keys(69), "PictureNet": keys(82), "PictureHoney": keys(84)},
                  **{"Scene" + k: keys(ord(k)) for k in keys_for}),
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "box2d", "gravity": 980}})
d.write("README.md", """# Particles demo

A basin of water, sand and sparks. Each is a sprite with a **Fluid**
behavior: the sprite's picture is drawn once per particle, tinted by the
particle's color, and the behavior holds the settings (its **Kind**: Water,
Powder for the sand, and water with no pressure, a lifetime and color over
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

## The other scenes

Keys **1** to **0**, and **P**, change scene (a Scene Manager in the singleton scene
`scenes/singletons/Demo`); each scene says what it shows and its keys.

| Key | Scene | What it shows |
|---|---|---|
| 2 | Deep pool in passes | the same deep pool stepped once a step and in passes worked out from gravity and the radius (**Substeps** 0): one packs down and churns, the other holds |
| 3 | A settled pool sleeps | **Sleep**: once everything is slow the system stops stepping, and **Particles are asleep** says so |
| 4 | Elastic jelly | **Make group … elastic**: blocks that keep their shape |
| 5 | Spring net | **Make group … spring**: a strip that drapes like a net |
| 6 | Walls made of particles | **Make group … wall**: a cup of particles that holds water, then made plain |
| 7 | Oil and water repel | **Make group … repulsive**: two groups that part again however they are stirred |
| 8 | Color mixing | **Color mixing**: red and blue water turning purple where they meet |
| 9 | Color by speed | **Color by speed**: a stream and splashes that foam white |
| 0 | Objects into particles | **Turn … into particles**: Kenney's animal heads made elastic, then melted |
| P | A picture into particles | a whole picture in its own colors, about seventeen thousand particles; Q to T make it water, jelly, colors that mix, a soft net or honey |

The pools and blocks are laid with **Fill … with particles** into hidden
shapes placed in each scene (the Mold and Dropper objects), so they land
where the scene shows them.

Generated by `tools/make-particles-demo.py`; the pictures are drawn there and
the sounds are Kenney's (Digital Audio), CC0, and so are the animal heads (Animal Pack Redux, tools/art).
""")
print("wrote", d.out)
