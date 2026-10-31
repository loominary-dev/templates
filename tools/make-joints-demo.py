"""The joints demo: a scene for each way two bodies can be joined on the
Box2D solver, the Physics Body's joint words. Hinges with a motor, a spring
and a chain; welds that break or give; sliders with a motor and a spring;
springs, a rod and a rope; wheels on sprung axles; a follow by force; and
Meld, which makes two objects one body and back.

    python3 tools/make-joints-demo.py <kenney digital-audio dir> <kenney impact-sounds dir> [demos/joints]

Everything is drawn here; the sounds are Kenney's (CC0). Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

da, im = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "..", "demos", "joints")
d = Demo(out, ["scenes/singletons", "vscript"], "j1000000")
W, H = 960, 540

# ── pictures ──
WOOD, WOOD_DARK, WOOD_LINE = (196, 140, 82, 255), (132, 88, 48, 255), (100, 64, 34, 255)
STEEL, STEEL_EDGE = (120, 120, 132, 255), (70, 70, 80, 255)
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
def still(name, w, h, img, collision, points=()): d.sprite(name, w, h, [("still", [img], 400, "loop")], collision, points)

still("Ground", 960, 40, panel(960, 40, (92, 140, 70, 255), (54, 90, 40, 255), 0), [box("body", 480, 20, 960, 40)])
still("Wall", 20, 540, panel(20, 540, (100, 100, 110, 255), (60, 60, 70, 255), 0), [box("body", 10, 270, 20, 540)])
still("Beam", 640, 16, panel(640, 16, STEEL, STEEL_EDGE, 2), [box("body", 320, 8, 640, 16)])
still("Post", 20, 20, panel(20, 20, STEEL, STEEL_EDGE), [box("body", 10, 10, 20, 20)])
still("Crate", 32, 32, panel(32, 32, WOOD, WOOD_LINE, 2, [(3, 3, 28, 28), (28, 3, 3, 28)]), [box("body", 16, 16, 32, 32)],
      [point("top", 16, 0), point("bottom", 16, 32), point("left", 0, 16), point("right", 32, 16)])
still("Ball", 28, 28, disc(28, (232, 92, 80, 255), (140, 40, 40, 255)), [circle("body", 14, 14, 14)], [point("top", 14, 0)])
still("Shot", 20, 20, disc(20, (60, 60, 66, 255), (20, 20, 24, 255)), [circle("body", 10, 10, 10, density=4)])
# A door hangs from its top; a chain link from its top too, the next link hung from its bottom.
still("Door", 14, 130, panel(14, 130, WOOD, WOOD_LINE, 2, [(7, 10, 7, 120)]), [box("body", 7, 65, 14, 130)], [point("top", 7, 0)])
still("Link", 10, 30, panel(10, 30, STEEL, STEEL_EDGE, 4), [box("body", 5, 15, 10, 30)], [point("top", 5, 0), point("bottom", 5, 30)])
still("Hook", 12, 12, disc(12, STEEL, STEEL_EDGE), [circle("body", 6, 6, 6)])
still("Sign", 90, 56, panel(90, 56, WOOD, WOOD_LINE, 4, [(10, 18, 80, 18), (10, 30, 70, 30), (10, 42, 60, 42)]), [box("body", 45, 28, 90, 56)], [point("foot", 45, 56)])
still("Lift", 120, 14, panel(120, 14, STEEL, STEEL_EDGE, 2), [box("body", 60, 7, 120, 14)])
still("Rail", 6, 200, panel(6, 200, (60, 60, 68, 255), (40, 40, 46, 255), 1), [])
still("Drawer", 90, 40, panel(90, 40, WOOD, WOOD_LINE, 3, [(70, 14, 70, 26)]), [box("body", 45, 20, 90, 40)])
still("Cabinet", 100, 60, panel(100, 60, (70, 50, 30, 255), (40, 28, 16, 255), 3), [])
car = panel(100, 28, (60, 120, 220, 255), (24, 52, 110, 255), 6)
ImageDraw.Draw(car).rectangle([58, 4, 86, 14], fill=(190, 225, 255, 255))
still("Cart", 100, 28, car, [box("body", 50, 14, 100, 28)])
still("Wheel", 28, 28, disc(28, (40, 40, 44, 255), (12, 12, 14, 255), 5, (180, 180, 190, 255)), [circle("tire", 14, 14, 14, friction=0.95)])
still("Bump", 60, 60, disc(60, (92, 140, 70, 255), (54, 90, 40, 255)), [circle("body", 30, 30, 30)])
still("Lead", 36, 36, panel(36, 36, (60, 120, 220, 255), (24, 52, 110, 255), 4), [box("body", 18, 18, 36, 36)])
still("Tail", 36, 36, panel(36, 36, (235, 150, 60, 255), (140, 80, 20, 255), 4), [box("body", 18, 18, 36, 36)])
still("Lump", 48, 48, disc(48, (90, 90, 100, 255), (40, 40, 46, 255), 0, (140, 140, 150, 255)), [circle("body", 24, 24, 24, density=3)])
still("Bit", 16, 16, disc(16, (232, 92, 80, 255), (140, 40, 40, 255)), [circle("body", 8, 8, 8)])

d.sounds({"click": (da, "pepSound1.ogg"), "crack": (im, "impactWood_heavy_000.ogg"), "bump": (im, "impactWood_light_002.ogg"),
          "clank": (im, "impactMetal_light_000.ogg"), "kick": (im, "impactSoft_medium_000.ogg")})

# ── types ──
SOLID, BODY = 1, 2
EVERYTHING = -1
def body(**k): return dict({"componentClass": "PhysicsBody", "bodyType": "Dynamic"}, **k)
def solid(): return {"collision": {"layer": SOLID, "mask": EVERYTHING}}
def moving(): return {"collision": {"layer": BODY, "mask": SOLID | BODY}}
def drag(): return {"componentClass": "DragRules"}
for name in ["Ground", "Wall", "Beam", "Post", "Hook", "Bump"]:
    d.type_json(name, "Sprite", dict(solid(), spriteKey=name + ".sprite.json"))
for name in ["Rail", "Cabinet"]:
    d.type_json(name, "Sprite", {"spriteKey": name + ".sprite.json", "collisionEnabled": False})
# Dynamic, draggable with the mouse.
for name in ["Crate", "Ball", "Door", "Link", "Sign", "Drawer", "Lead", "Lump", "Bit"]:
    d.type_json(name, "Sprite", dict(moving(), spriteKey=name + ".sprite.json"), [body(), drag()])
d.type_json("Shot", "Sprite", dict(moving(), spriteKey="Shot.sprite.json"), [body(bounceX=0.2, bounceY=0.2)])
d.type_json("Lift", "Sprite", dict(moving(), spriteKey="Lift.sprite.json"), [body()])
d.type_json("Tail", "Sprite", dict(moving(), spriteKey="Tail.sprite.json"), [body()])
d.type_json("Cart", "Sprite", dict(moving(), spriteKey="Cart.sprite.json"), [body(), drag()])
d.type_json("Wheel", "Sprite", dict(moving(), spriteKey="Wheel.sprite.json"), [body(friction=0.95)])
# The same crate under other names, so a scene's rules can speak of one and not the others.
for name in ["Block", "PairA", "PairB"]:
    d.type_json(name, "Sprite", dict(moving(), spriteKey="Crate.sprite.json"), [body(), drag()])
d.type_json("Caption", "Label", {"text": "", "fontSize": 15, "shadow": True})
d.type_json("Help", "Label", {"text": "", "fontSize": 13, "shadow": True})
d.type_json("Readout", "Label", {"text": "", "fontSize": 13, "shadow": True})

# ── rule words ──
px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def body_(scope, name, *params, **k): return comp(scope, "PhysicsBody", name, *params, **k)
def bvalue(scope, name, *params, **k): return cvalue(scope, "PhysicsBody", name, *params, **k)
def has_joint(scope, j): return body_(scope, "hasJoint", s(j))
def obj(scope): return {"type": "object", "scope": scope}
def set_var(name, v): return line("variables", "Variables", "setVariable", s(name), v)
def add_var(name, v): return line("variables", "Variables", "addToVariable", s(name), v)
def sound(key): return line("audio", "Audio", "playSound", s(key))
def label(name, v): return line(name, "Label", "setNumber", v)
def joint_once(scope, name, *actions, when=()):
    """A joint is made once both bodies are there: "has no joint" asks again each step until it is."""
    return rule(list(when) + [not_(has_joint(scope, name))], list(actions))
def toggle(key, flag, on, off):
    """A key that switches something on and off, through a variable: 2 means 'just switched on', so the off rule waits a step."""
    return [
        rule([pressed(key), compare(var(flag), EQ, lit(0))], [set_var(flag, lit(2))] + on),
        rule([pressed(key), compare(var(flag), EQ, lit(1))], [set_var(flag, lit(0))] + off),
        rule([compare(var(flag), EQ, lit(2))], [set_var(flag, lit(1))]),
    ]
click = sound("click")

d.write("vscript/DragRules.vscript.json", {"rules": [
    rule([mouse_pressed(LEFT_BUTTON), line("self", "Node", "containsPoint", px, py)], [body_("self", "dragToward", px, py)]),
    rule([mouse_down(LEFT_BUTTON), body_("self", "isDragged")], [body_("self", "dragToward", px, py)]),
    rule([not_(mouse_down(LEFT_BUTTON)), body_("self", "isDragged")], [body_("self", "releaseDrag")]),
]})

# ── scenes: each its own objects under one root, a Level whose sheet holds its rules, and lines saying what it shows ──
FEATURES = []
GROUND = 230   # the ground's top
def feature(file, title, about, controls, build, rules):
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
    # The walls first, so the lines of text are drawn over them, and the text starts inside them.
    place("WallL", "Wall", -470, 0); place("WallR", "Wall", 470, 0)
    place("Title", "Caption", -452, -262, text=title)
    lines = about if isinstance(about, list) else [about]
    for k, text in enumerate(lines): place("About%d" % (k + 1), "Help", -452, -244 + 18 * k, text=text)
    place("Controls", "Help", -452, -244 + 18 * len(lines), text=controls)
    build(place)
    # Drawn after the scene's things: a bump is a disc half under the ground.
    place("Ground1", "Ground", 0, GROUND + 20)
    d.scene("scenes/%s.scene.json" % file, objects)
    d.write("vscript/%s.vscript.json" % sheet_name, {"rules": [rule([pressed("Reset")], [line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % file))])] + rules})
    FEATURES.append((file, title))
def readout(place, name, x, y, caption):
    """A caption and, after it, a number or text a rule sets: a Label type of its own, which is how a rule names it."""
    d.type_json(name, "Label", {"text": "", "fontSize": 13, "shadow": True})
    place(name + "Caption", "Readout", x, y, text=caption); place(name + "1", name, x + len(caption) * 6.4 + 8, y)

# 1. Hinges: a door with a motor, a door on a spring, and a chain of links with a ball on the end.
BEAM_Y = -150
def hinges(place):
    place("Beam1", "Beam", 0, BEAM_Y)
    place("MotorDoor", "Door", -250, BEAM_Y + 8 + 2 + 65)
    place("SpringDoor", "Door", -90, BEAM_Y + 8 + 2 + 65)
    for i in range(6): place("Link%d" % (i + 1), "Link", 180, BEAM_Y + 8 + 15 + 30 * i)
    place("Bob", "Ball", 180, BEAM_Y + 8 + 180 + 14)
    readout(place, "Angle", 200, -190, "Motor door angle, degrees:")
    readout(place, "Effort", 200, -172, "its motor's effort:")
feature("Hinges", "Hinges",
        ["Hinge to: the two turn about one point. A hinge takes limits, a motor and a spring; a chain is links hinged to one another."],
        "Hold Space to drive the left door's motor.   Drag the right door, or the chain, and let go.   R restarts the scene",
        hinges,
        [joint_once("Door", "hinge", body_("Door", "hingeTo", s(""), s("top"), s("hinge")), body_("Door", "setJointLimits", s("hinge"), lit(-110), lit(110))),
         # The right door springs back to hanging straight; the left is driven while Space is held and swings free after.
         rule([line("Door", "Node", "nameIs", s("SpringDoor")), has_joint("Door", "hinge"), once()], [body_("Door", "setJointSpring", s("hinge"), lit(1.5), lit(0.15))]),
         rule([line("Door", "Node", "nameIs", s("MotorDoor")), held("Act")], [body_("Door", "setJointMotor", s("hinge"), lit(240), lit(1500000))]),
         rule([line("Door", "Node", "nameIs", s("MotorDoor")), not_(held("Act"))], [body_("Door", "setJointMotorOn", s("hinge"), b(False))]),
         joint_once("Link", "chain", body_("Link", "hingeTo", s(""), s("top"), s("chain")), when=[line("Link", "Node", "nameIs", s("Link1"))])]
        + [joint_once("Link", "chain", body_("Link", "hingeTo", s("Link%d" % i), s("top"), s("chain")), when=[line("Link", "Node", "nameIs", s("Link%d" % (i + 1)))]) for i in range(1, 6)]
        + [joint_once("Ball", "chain", body_("Ball", "hingeTo", s("Link6"), s("top"), s("chain"))),
           rule([line("Door", "Node", "nameIs", s("MotorDoor"))], [label("Angle", bvalue("Door", "jointPosition", s("hinge"))), label("Effort", bvalue("Door", "jointMotorEffort", s("hinge")))])])

# 2. Welds: a tower of blocks welded together that a shot breaks apart, and a sign welded on a spring.
def welds(place):
    # The tower leans, each block 9 px over the one below: its welds hold it up, and cut it falls.
    for i in range(5): place("Block%d" % (i + 1), "Block", 220 + 9 * i, GROUND - 16 - 32 * i)
    place("Post1", "Post", -250, GROUND - 10)
    place("Shot1", "Shot", -440, GROUND - 10)
    place("Sign1", "Sign", -250, GROUND - 20 - 28)
    readout(place, "Broken", 200, -190, "Welds broken:")
feature("Welds", "Welds",
        ["Weld to: no movement between the two. A weld breaks past its break force, or gives on a spring."],
        "Space fires the ball at the leaning tower.   K takes every weld off.   Drag the sign; it is welded on a spring.   R restarts the scene",
        welds,
        # The welds are made while none has broken or been cut: a broken weld made again would break again where the block lies.
        [rule([once()], [set_var("broken", lit(0)), set_var("cut", lit(0))]),
         # Each weld has a name of its own: both its ends know a joint by its name, so one name for all would be two joints to the middle blocks.
         joint_once("Block", "weld1", body_("Block", "weldTo", s(""), s("bottom"), s("weld1")), body_("Block", "setJointBreakForce", s("weld1"), lit(6000)),
                    when=[line("Block", "Node", "nameIs", s("Block1")), compare(var("broken"), EQ, lit(0)), compare(var("cut"), EQ, lit(0))])]
        + [joint_once("Block", "weld%d" % (i + 1), body_("Block", "weldTo", s("Block%d" % i), s("bottom"), s("weld%d" % (i + 1))), body_("Block", "setJointBreakForce", s("weld%d" % (i + 1)), lit(6000)),
                      when=[line("Block", "Node", "nameIs", s("Block%d" % (i + 1))), compare(var("broken"), EQ, lit(0)), compare(var("cut"), EQ, lit(0))]) for i in range(1, 5)]
        + [rule([line("Block", "Node", "nameIs", s("Block%d" % i)), body_("Block", "onJointBroke", s("weld%d" % i))], [add_var("broken", lit(1)), sound("crack")]) for i in range(1, 6)]
        + [joint_once("Sign", "mount", body_("Sign", "weldTo", s("Post1"), s("foot"), s("mount")), body_("Sign", "setJointSpring", s("mount"), lit(2.5), lit(0.1))),
           # The one shot, fired again from the left each time: a new object has no body to give a speed to until the next step.
           rule([pressed("Act")], [line("Shot", "Node", "setPosition", lit(-430), lit(60)), body_("Shot", "setVelocity", lit(1800), lit(-100)), sound("kick")]),
           rule([pressed("Cut")], [set_var("cut", lit(1)), body_("Block", "disconnectJoint", s("")), click]),
           rule([], [label("Broken", var("broken"))])])

# 3. Sliders: a lift driven up and down by a motor between limits, and a drawer that slides out and springs back.
def sliders(place):
    place("Rail1", "Rail", -200, GROUND - 100)
    place("Lift1", "Lift", -200, GROUND - 7)
    place("Rider", "Crate", -200, GROUND - 14 - 16)
    place("Cabinet1", "Cabinet", 160, 60)
    place("Drawer1", "Drawer", 160, 60)
    readout(place, "Travel", 200, -190, "Lift travel, pixels:")
feature("Sliders", "Sliders",
        ["Slide on: moves along one line fixed in the other, without turning. A slider takes limits, a motor and a spring."],
        "Space sends the lift up, and down again.   Drag the drawer out and let go.   R restarts the scene",
        sliders,
        [rule([once()], [set_var("up", lit(0))]),
         joint_once("Lift", "lift", body_("Lift", "slideOn", s(""), lit(90), s(""), s("lift")), body_("Lift", "setJointLimits", s("lift"), lit(-180), lit(0)),
                    body_("Lift", "setJointMotor", s("lift"), lit(90), lit(8000))),
         joint_once("Drawer", "slide", body_("Drawer", "slideOn", s(""), lit(0), s(""), s("slide")), body_("Drawer", "setJointLimits", s("slide"), lit(0), lit(110)),
                    body_("Drawer", "setJointSpring", s("slide"), lit(1.2), lit(0.3))),
         rule([line("Lift", "Node", "nameIs", s("Lift1"))], [label("Travel", bvalue("Lift", "jointPosition", s("lift")))])]
        + toggle("Act", "up", [body_("Lift", "setJointMotor", s("lift"), lit(-90), lit(8000)), click], [body_("Lift", "setJointMotor", s("lift"), lit(90), lit(8000)), click]))

# 4. Springs: a ball on a spring, a crate on a rope and a ball on a rod, all hung from hooks on a beam.
def springs(place):
    place("Beam1", "Beam", 0, BEAM_Y)
    for name, x in [("HookA", -220), ("HookB", 0), ("HookC", 220)]: place(name, "Hook", x, BEAM_Y + 8 + 6)
    place("Bouncer", "Ball", -220, BEAM_Y + 60)
    place("Hanger", "Crate", 0, BEAM_Y + 80)
    place("Swinger", "Ball", 220, BEAM_Y + 150)
    readout(place, "Force", 200, -190, "Spring force:")
feature("Springs", "Springs",
        ["Spring to: keeps a distance between two points. Stiff, it is a rod; with a spring it bounces; with a limit and almost no spring, a rope."],
        "Space kicks them.   Drag any of them and let go.   R restarts the scene",
        springs,
        [joint_once("Ball", "spring", body_("Ball", "springTo", s("HookA"), s(""), s(""), lit(130), s("spring")), body_("Ball", "setJointSpring", s("spring"), lit(1.2), lit(0.1)),
                    when=[line("Ball", "Node", "nameIs", s("Bouncer"))]),
         joint_once("Crate", "rope", body_("Crate", "springTo", s("HookB"), s("top"), s(""), lit(150), s("rope")), body_("Crate", "setJointSpring", s("rope"), lit(0.05), lit(0)),
                    body_("Crate", "setJointLimits", s("rope"), lit(0), lit(150))),
         joint_once("Ball", "rod", body_("Ball", "springTo", s("HookC"), s(""), s(""), lit(150), s("rod")), when=[line("Ball", "Node", "nameIs", s("Swinger"))]),
         rule([pressed("Act")], [body_("Ball", "applyImpulse", op("*", bvalue("Ball", "mass"), lit(500)), op("*", bvalue("Ball", "mass"), lit(-300))),
                                 body_("Crate", "applyImpulse", op("*", bvalue("Crate", "mass"), lit(500)), op("*", bvalue("Crate", "mass"), lit(-300))), sound("kick")]),
         rule([line("Ball", "Node", "nameIs", s("Bouncer"))], [label("Force", bvalue("Ball", "jointForce", s("spring")))])])

# 5. Wheels: a cart on two wheel joints driven by their motors, over bumps, its springs soft or stiff.
def wheels(place):
    for x in [-120, 60, 240]: place("Bump%d" % x, "Bump", x, GROUND + 18)
    place("Cart1", "Cart", -350, GROUND - 34)
    place("WheelL", "Wheel", -383, GROUND - 16); place("WheelR", "Wheel", -317, GROUND - 16)
    readout(place, "Speed", 200, -190, "Wheel speed, degrees a second:")
    readout(place, "Ride", 200, -172, "its axle's travel, pixels:")
feature("Wheels", "Wheels",
        ["Be a wheel of: turns about its axle and rides a sprung axis fixed in the cart; a motor drives it."],
        "A and D drive the motors.   Space switches the springs between soft and stiff.   Drag the cart.   R restarts the scene",
        wheels,
        [rule([once()], [set_var("stiff", lit(0))]),
         joint_once("Wheel", "axle", body_("Wheel", "wheelOf", s("Cart1"), lit(-90), s(""), s("axle")), body_("Wheel", "setJointSpring", s("axle"), lit(3), lit(0.5))),
         rule([held("Right")], [body_("Wheel", "setJointMotor", s("axle"), lit(1080), lit(9000))]),
         rule([held("Left")], [body_("Wheel", "setJointMotor", s("axle"), lit(-1080), lit(9000))]),
         rule([not_(held("Left")), not_(held("Right"))], [body_("Wheel", "setJointMotorOn", s("axle"), b(False))]),
         rule([line("Wheel", "Node", "nameIs", s("WheelL"))], [label("Speed", bvalue("Wheel", "jointSpeed", s("axle"))), label("Ride", bvalue("Wheel", "jointPosition", s("axle")))])]
        + toggle("Act", "stiff", [body_("Wheel", "setJointSpring", s("axle"), lit(12), lit(0.9)), click], [body_("Wheel", "setJointSpring", s("axle"), lit(3), lit(0.5)), click]))

# 6. Follow by force: a block pulled to a place beside another by a motor joint, pushing crates out of its way.
def follow(place):
    place("Lead1", "Lead", -150, 60)
    place("Tail1", "Tail", -70, 60)
    for i, x in enumerate([40, 100, 160, 220]): place("Crate%d" % (i + 1), "Crate", x, GROUND - 16)
    place("Crate5", "Crate", 70, GROUND - 48); place("Crate6", "Crate", 190, GROUND - 48)
    readout(place, "Holds", 200, -190, "The orange block follows:")
feature("Follow", "Follow by force",
        ["Follow by force: pulled toward a place beside another object by force, so others can push it off and it comes back."],
        "Drag the blue block; the orange one follows it and shoves the crates.   Space puts it on the other side.   R restarts the scene",
        follow,
        [rule([once()], [set_var("side", lit(0))]),
         joint_once("Tail", "tow", body_("Tail", "followByForce", s("Lead1"), lit(80), lit(0), s("tow"))),
         rule([line("Tail", "Node", "nameIs", s("Tail1"))], [line("Holds", "Label", "setText", bvalue("Tail", "jointHolds", s("tow"), returnType="string"))])]
        + toggle("Act", "side", [body_("Tail", "setJointRest", s("tow"), lit(-80), lit(0)), click], [body_("Tail", "setJointRest", s("tow"), lit(80), lit(0)), click]))

# 7. Meld: a lump rolls down a ramp and melds whatever it touches into its own body as it goes; Space bursts it apart.
RAMP_DEG = 20
def ramp_y(x): return 20 + (x + 140) * math.tan(math.radians(RAMP_DEG))   # the ramp's middle line, 640 long, about (-140, 20)
def meld(place):
    place("Ramp", "Beam", -140, 20, rotation=math.radians(RAMP_DEG))
    place("Lump1", "Lump", -400, ramp_y(-400) - 8.5 - 26)
    for i, x in enumerate([-300, -230, -160, -90, -20, 50, 110]):
        if i % 2 == 0: place("Crate%d" % i, "Crate", x, ramp_y(x) - 8.5 - 17)
        else: place("Bit%d" % i, "Bit", x, ramp_y(x) - 8.5 - 8.5)
    place("PairA1", "PairA", 250, GROUND - 16); place("PairB1", "PairB", 282, GROUND - 16)
    for i, x in enumerate([340, 380, 420]): place("Bit%d" % (10 + i), "Bit", x, GROUND - 8)
    readout(place, "Mass", 200, -190, "The lump's mass:")
melders = ["Crate", "Bit", "PairA", "PairB"]
feature("Meld", "Meld",
        ["Meld to: an object joins another's body and the two move as one until Unmeld; its shapes, its mass and its joints go with it."],
        "The lump melds whatever it rolls over; the pair at the foot is hinged, so the second comes along by its hinge.   Space bursts it apart.   R restarts the scene",
        meld,
        [rule([once()], [set_var("burst", lit(0))]),
         joint_once("PairB", "pair", body_("PairB", "hingeTo", s("PairA1"), s("left"), s("pair"))),
         # The lump is picked first, then each piece touching it melds to it: a word that takes an object takes the one picked.
         # After the burst nothing melds again, or the pieces would rejoin where they lie against it.
         rule([line("Lump", "Node", "nameIs", s("Lump1")), compare(var("burst"), EQ, lit(0))], [label("Mass", bvalue("Lump", "mass"))],
              [rule([line(t, "Node", "isOverlapping", s("Lump")), not_(body_(t, "isMelded"))], [body_(t, "meldTo", obj("Lump")), click]) for t in melders]),
         rule([pressed("Act"), compare(var("burst"), EQ, lit(0))], [set_var("burst", lit(1)), sound("crack")],
              [rule([body_(t, "isMelded")], [body_(t, "unmeld")]) for t in melders])])

# ── the singleton: the Scene Manager, the keys that change scene, and the list of scenes ──
SCENES = FEATURES
d.type_json("Scenes", "SceneManager", {"transition": "Fade", "fadeTime": 0.15})
d.type_json("Switcher", "Node", {}, [{"componentClass": "SwitchRules"}])
d.type_json("SceneList", "Label", {"text": "", "fontSize": 13, "shadow": True})
keys_for = [str((i + 1) % 10) for i in range(min(10, len(SCENES)))]
listing = "   ".join("%s %s" % (k, title) for k, (_, title) in zip(keys_for, SCENES)) + "   Left and Right step through the scenes"
d.scene("scenes/singletons/Demo.scene.json", [
    {"id": d.uid(3001), "name": "Demo"},
    {"id": d.uid(3002), "parent": d.uid(3001), "name": "Scenes1", "type": "Scenes"},
    {"id": d.uid(3003), "parent": d.uid(3001), "name": "Switcher1", "type": "Switcher"},
    {"id": d.uid(3004), "parent": d.uid(3001), "name": "SceneList1", "type": "SceneList", "x": -452, "y": 238, "text": listing},
])
# The arrows step through the scenes. A variable holds which scene is up: the arrows move it by one and wrap it,
# then the rule for that number changes scene. The move comes first and the change rules only read the number,
# so one press moves one scene.
def go(i): return line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % SCENES[i][0]))
def at(i): return set_var("scene", lit(i))
n = len(SCENES)
d.write("vscript/SwitchRules.vscript.json", {"rules": [
    rule([pressed("Scene" + k)], [at(i), go(i)]) for i, k in enumerate(keys_for)]
    + [rule([pressed("NextScene")], [add_var("scene", lit(1))]),
       rule([pressed("PreviousScene")], [add_var("scene", lit(-1))]),
       rule([compare(var("scene"), GE, lit(n))], [at(0)]),
       rule([compare(var("scene"), LT, lit(0))], [at(n - 1)])]
    + [rule([pressed("NextScene"), compare(var("scene"), EQ, lit(i))], [go(i)]) for i in range(n)]
    + [rule([pressed("PreviousScene"), compare(var("scene"), EQ, lit(i))], [go(i)]) for i in range(n)]})

d.write("project.json", {"schemaVersion": 2, "name": "Joints demo", "entryScene": "scenes/%s.scene.json" % SCENES[0][0],
    "collisionLayers": {"1": "Solid", "2": "Body"},
    "singletons": ["scenes/singletons/Demo.scene.json"],
    # The keys the demos share: Space acts, R restarts the scene, 1 to 0 and the arrows choose a scene; A and D drive, K cuts joints.
    "input": dict({"Act": keys(32), "Reset": keys(82), "Left": keys(65), "Right": keys(68), "Cut": keys(75), "NextScene": keys(39), "PreviousScene": keys(37)},
                  **{"Scene" + k: keys(ord(k)) for k in keys_for}),
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "box2d", "gravity": 980, "interpolate": True}})
d.write("README.md", """# Joints demo

A scene for each way two bodies can be joined on the **Box2D** solver
(Project Settings ▸ Physics): the **Physics Body**'s joint words, every
joint made by a rule that asks "has no joint" each step, so it is made as
soon as both bodies are there. Keys 1 to 7, or the arrows, change scene;
Space acts, R restarts the scene; drag anything with the mouse.

| Key | Scene | What it shows |
|---|---|---|
| 1 | Hinges | **Hinge to**, with **Limit**, **Drive** (hold Space) and **Set the spring**; a chain of links hinged to one another, a ball on its end |
| 2 | Welds | **Weld to** with **Set the break force**: a tower a shot (Space) breaks apart, **Joint broke** counting; a sign welded on a spring; **Disconnect** (K) |
| 3 | Sliders | **Slide on** with **Limit** and **Drive**: a lift (Space); with **Set the spring**: a drawer that springs back |
| 4 | Springs | **Spring to**: on a spring it bounces, stiff it is a rod, with **Limit** and almost no spring a rope; **Joint force** |
| 5 | Wheels | **Be a wheel of** with **Drive** (A and D) and **Set the spring** (Space: soft or stiff); **Joint speed**, **Joint position** |
| 6 | Follow by force | **Follow by force**: the orange block is pulled to a place beside the blue one and shoves crates; **Set the rest** (Space); **Joint holds** |
| 7 | Meld | **Meld to**: a lump rolling down a ramp makes whatever it touches part of its own body, mass and all, a hinged pair by its hinge; **Unmeld** (Space) bursts it apart, each piece keeping its speed |

Generated by `tools/make-joints-demo.py`; the pictures are drawn there and
the sounds are Kenney's (Digital Audio, Impact Sounds), CC0.
""")
print("wrote", d.out)
