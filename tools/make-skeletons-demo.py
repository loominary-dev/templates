"""The skeletons demo: bones, skeletons and what moves them, in one scene.

- A critter whose tail waves on a motor and whose ears jiggle; a click makes
  the tail wag fast for two seconds (a motor's duration), easing in and out,
  then it settles back (On motor finished).
- An arm that reaches for the mouse (Aim bone: two bones, an elbow that bends
  one way and only so far, a little lag).
- A snake that follows the mouse, trailing behind its head (Follow).
- A flag: one picture bent by three bones (a Mesh Sprite), rippling.
- A blob that breathes by deform keys alone: its points eased between shapes.

    python3 tools/make-skeletons-demo.py [demos/skeletons]

Needs Pillow.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "skeletons")
d = Demo(out, ["scenes", "vscript"], "a3000000")
W, H = 960, 540

# ── art ──
def oval(w, h, fill, outline=(40, 30, 30, 255), eye=None):
    img = canvas(w, h)
    g = ImageDraw.Draw(img)
    g.ellipse([1, 1, w - 2, h - 2], fill=fill, outline=outline, width=2)
    if eye:
        ex, ey, r = eye
        g.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, 255, 255, 255))
        g.ellipse([ex - r // 2 + 1, ey - r // 2, ex + r // 2 + 1, ey + r // 2], fill=(20, 20, 30, 255))
    return img

def bar(w, h, fill):
    img = canvas(w, h)
    ImageDraw.Draw(img).rounded_rectangle([1, 1, w - 2, h - 2], radius=h // 2 - 1, fill=fill, outline=(40, 30, 30, 255), width=2)
    return img

def ear(w, h, fill):
    img = canvas(w, h)
    ImageDraw.Draw(img).polygon([(0, 2), (w - 1, h // 2), (0, h - 3)], fill=fill, outline=(40, 30, 30, 255))
    return img

ORANGE, DARK, SKIN, GREEN, TEAL = (240, 150, 60, 255), (190, 100, 40, 255), (235, 190, 150, 255), (120, 200, 90, 255), (70, 170, 170, 255)
pictures = {
    "CritterBody": (oval(70, 44, ORANGE), 70, 44),
    "CritterHead": (oval(46, 42, ORANGE, eye=(30, 16, 5)), 46, 42),
    "CritterEar": (ear(28, 18, DARK), 28, 18),
    "CritterTail": (oval(26, 14, DARK), 26, 14),
    "UpperArm": (bar(96, 24, SKIN), 96, 24),
    "Forearm": (bar(86, 20, SKIN), 86, 20),
    "Hand": (oval(28, 28, SKIN), 28, 28),
    "SnakeBody": (oval(24, 22, GREEN), 24, 22),
    "SnakeHead": (oval(30, 24, GREEN, eye=(20, 8, 4)), 30, 24),
    "Pole": (bar(10, 230, (120, 90, 60, 255)), 10, 230),
}
for name, (img, w, h) in pictures.items():
    d.sprite(name, w, h, [("still", [img], 400, "loop")], [])
    d.type_json(name, "Sprite", {"spriteKey": name + ".sprite.json"})

# The flag and the blob are Mesh Sprites: one picture each, bent.
FW, FH = 180, 110
flag = canvas(FW, FH)
g = ImageDraw.Draw(flag)
for i in range(5):
    g.rectangle([0, i * FH // 5, FW - 1, (i + 1) * FH // 5], fill=[(200, 60, 60, 255), (240, 240, 240, 255)][i % 2])
g.rectangle([0, 0, 70, 50], fill=(50, 70, 160, 255))
for k in range(5):
    a = -math.pi / 2 + k * 4 * math.pi / 5
    g.ellipse([35 + 14 * math.cos(a) - 3, 25 + 14 * math.sin(a) - 3, 35 + 14 * math.cos(a) + 3, 25 + 14 * math.sin(a) + 3], fill=(250, 220, 80, 255))
d.sprite("Flag", FW, FH, [("still", [flag], 400, "loop")], [])
d.type_json("Flag", "MeshSprite", {"spriteKey": "Flag.sprite.json"})

BW, BH = 120, 100
blob = canvas(BW, BH)
g = ImageDraw.Draw(blob)
g.ellipse([4, 8, BW - 5, BH - 3], fill=(110, 200, 240, 255), outline=(30, 80, 120, 255), width=3)
g.ellipse([36, 36, 50, 50], fill=(20, 30, 40, 255))
g.ellipse([70, 36, 84, 50], fill=(20, 30, 40, 255))
g.arc([44, 52, 76, 72], 20, 160, fill=(20, 30, 40, 255), width=3)
d.sprite("Jelly", BW, BH, [("still", [blob], 400, "loop")], [])
# Not "Blob": a project class is a global of the web build, and Blob is the browser's.
d.type_json("Jelly", "MeshSprite", {"spriteKey": "Jelly.sprite.json"})

# A Type for each skeleton a rule talks to; captions.
for t in ["Critter", "Arm", "Snake", "Banner", "Breather"]:
    d.type_json(t, "Skeleton", {})
d.type_json("Caption", "Label", {"text": "", "fontSize": 13})
d.type_json("Demo", "Node", {}, [{"componentClass": "DemoRules"}])

# ── meshes, worked out here as the editor's Make mesh would ──
def grid_mesh(w, h, nx, ny, bones, weigh):
    """A grid over a w x h picture centered on its origin; `bones` are (name, bind matrix as six numbers); `weigh(x, y)` gives a weight per bone."""
    verts, uvs, idx = [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y = -w / 2 + w * i / nx, -h / 2 + h * j / ny
            verts += [round(x, 2), round(y, 2)]
            uvs += [round(i / nx, 5), round(j / ny, 5)]
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            idx += [a, a + 1, a + nx + 2, a, a + nx + 2, a + nx + 1]
    n = len(verts) // 2
    weights = {b: [] for b, _ in bones}
    for v in range(n):
        ws = weigh(verts[v * 2], verts[v * 2 + 1])
        total = sum(ws) or 1
        for (b, _), wv in zip(bones, ws): weights[b].append(round(wv / total, 4))
    mesh = {"vertices": verts, "uvs": uvs, "indices": idx, "bones": [b for b, _ in bones], "binds": [x for _, m in bones for x in m], "weights": weights}
    if bones: mesh["painted"] = list(range(n))
    return mesh

# The flag's three bones run along it from the pole: at -90, -30 and 30 in its space, unturned. A bind undoes each one's place.
flag_bones = [("F1", [1, 0, 0, 1, 90, 0]), ("F2", [1, 0, 0, 1, 30, 0]), ("F3", [1, 0, 0, 1, -30, 0])]
def flag_weigh(x, y):
    centres = [-60, 0, 60]
    if x <= -60: return [1, 0, 0]
    if x >= 60: return [0, 0, 1]
    return [max(0, 1 - abs(x - c) / 60) for c in centres]
flag_mesh = grid_mesh(FW, FH, 12, 4, flag_bones, flag_weigh)
blob_mesh = grid_mesh(BW, BH, 8, 6, [], lambda x, y: [])

# ── the scene ──
root = d.uid(3000)
objects = [{"id": root, "name": "Skeletons"}]
seq = [0]
def place(name, type_name, parent=None, **extra):
    seq[0] += 1
    oid = d.uid(3000 + seq[0])
    objects.append(dict({"id": oid, "parent": parent if parent is not None else root, "name": name, "type": type_name}, **extra))
    return oid
def bone(name, parent, length, x=0, y=0, deg=0, **extra):
    o = dict({"x": x, "y": y, "length": length}, **extra)
    if deg: o["rotation"] = round(math.radians(deg), 6)
    return place(name, "Bone", parent, **o)
def picture(name, type_name, on):
    # Along its bone: its origin the middle of its left edge, at the bone's base.
    return place(name, type_name, on, pivotNormalized=True, pivotX=0, pivotY=0.5)
def key(t, v, ease=None):
    k = {"t": t, "v": v}
    if ease: k["ease"] = ease
    return k

place("Demo1", "Demo", x=0, y=0)

# The critter: a body, a head, two jiggling ears, a tail that waves.
critter = place("Critter1", "Critter", x=-330, y=110, animation="idle", animations={"idle": {"duration": 1.2, "mode": "loop", "markers": [], "tracks": [
    {"target": "Body", "property": "y", "keys": [key(0, 0, "easeInOut"), key(0.6, -6, "easeInOut"), key(1.2, 0)]},
    {"target": "Head", "property": "rotation", "keys": [key(0, -0.35, "easeInOut"), key(0.6, -0.15, "easeInOut"), key(1.2, -0.35)]},
]}})
body = bone("Body", critter, 60)
picture("Body1", "CritterBody", body)
head = bone("Head", body, 40, x=58, y=-6, deg=-20)
picture("Head1", "CritterHead", head)
for i, (ex, deg) in enumerate([(10, -110), (24, -80)]):
    e = bone("Ear%d" % (i + 1), head, 26, x=ex, y=-14, deg=deg, motor="jiggle", motorAmount=40, motorSpeed=1.4, motorDelay=0.12)
    picture("Ear%d_1" % (i + 1), "CritterEar", e)
tail = body
for i, length in enumerate([24, 22, 20, 18, 16]):
    extra = {"motor": "wave", "motorAmount": 16, "motorSpeed": 0.8, "motorDelay": 0.18, "motorEase": 0.5} if i == 0 else {}
    tail = bone("Tail%d" % (i + 1), tail, length, x=4 if i == 0 else [24, 22, 20, 18][i - 1] - 2, deg=180 if i == 0 else 0, **extra)
    picture("Tail%d_1" % (i + 1), "CritterTail", tail)
place("CritterCaption", "Caption", x=-410, y=180, text="Motors: a waving tail, jiggling ears.", boxWidth=300)
place("CritterCaption2", "Caption", x=-410, y=200, text="Click for a fast wag of two seconds.", boxWidth=300)

# The arm: a shoulder that reaches for the mouse, an elbow that bends one way.
arm = place("Arm1", "Arm", x=-60, y=40)
upper = bone("Upper", arm, 90, deg=60, aimLag=0.12)
picture("Upper1", "UpperArm", upper)
fore = bone("Fore", upper, 80, x=90, deg=40, aimLag=0.12, limitAngles=True, minAngle=0, maxAngle=150)
picture("Fore1", "Forearm", fore)
hand = bone("Hand", fore, 1, x=80)
picture("Hand1", "Hand", hand)
place("ArmCaption", "Caption", x=-60, y=235, text="IK: reaches for the mouse, the elbow bends one way.", boxWidth=380)

# The snake: ten bones, its head the last, trailing after the mouse.
snake = place("Snake1", "Snake", x=120, y=170)
seg = snake
for i in range(10):
    seg = bone("S%d" % (i + 1), seg, 18, x=0 if i == 0 else 18, aimLag=0.1 if i == 9 else 0, limitAngles=i > 0, minAngle=-45, maxAngle=45)
    picture("S%d_1" % (i + 1), "SnakeHead" if i == 9 else "SnakeBody", seg)
place("SnakeCaption", "Caption", x=150, y=200, text="Follow: trails behind the mouse.", boxWidth=300)

# The flag: one picture on three bones, the outer two waving.
banner = place("Banner1", "Banner", x=250, y=-150)
place("Pole1", "Pole", banner, x=-95, y=60)
f1 = bone("F1", banner, 60, x=-90)
f2 = bone("F2", f1, 60, x=60, motor="wave", motorAmount=9, motorSpeed=0.7, motorDelay=0.25)
bone("F3", f2, 60, x=60)
place("Flag1", "Flag", banner, mesh=flag_mesh)
place("FlagCaption", "Caption", x=170, y=-60, text="A Mesh Sprite: one picture bent by three bones.", boxWidth=300)

# The blob: no bones at all; a deform track breathes it.
n = len(blob_mesh["vertices"]) // 2
def shape(fx, fy):
    vs = []
    for v in range(n):
        x, y = blob_mesh["vertices"][v * 2], blob_mesh["vertices"][v * 2 + 1]
        # Taller and narrower, the bottom staying on the ground.
        vs += [round(x * fx, 2), round((y - BH / 2) * fy, 2)]
    return vs
breather = place("Breather1", "Breather", x=-330, y=-120, animation="breathe", animations={"breathe": {"duration": 1.6, "mode": "loop", "markers": [], "tracks": [
    {"target": "Jelly1", "property": "deform", "keys": [{"t": 0, "vs": shape(0, 0), "ease": "easeInOut"}, {"t": 0.8, "vs": shape(-0.1, 0.18), "ease": "easeInOut"}, {"t": 1.6, "vs": shape(0, 0)}]},
]}})
place("Jelly1", "Jelly", breather, mesh=blob_mesh)
place("BlobCaption", "Caption", x=-410, y=-50, text="Deform keys: no bones, its points eased between shapes.", boxWidth=380)
d.scene("scenes/Skeletons.scene.json", objects)

# ── the rules ──
def sk(t, name, *params): return line(t, "Skeleton", name, *params)
px = op("-", value("input", "Input", "getPointerX"), lit(W / 2))
py = op("-", value("input", "Input", "getPointerY"), lit(H / 2))
rules = [
    rule([once()], [sk("Critter", "playAnimation", s("idle")), sk("Breather", "playAnimation", s("breathe"))]),
    rule([], [sk("Arm", "aimBone", s("Fore"), px, py, lit(2)), sk("Snake", "followWith", s("S10"), px, py, lit(10))]),
    # A click: two seconds of fast wagging, eased in and out, then back to the slow wave.
    rule([mouse_pressed(0)], [sk("Critter", "setMotorSpeed", s("Tail1"), lit(3)), sk("Critter", "setMotorDuration", s("Tail1"), lit(2)), sk("Critter", "setMotor", s("Tail1"), s("wave"))]),
    rule([sk("Critter", "onMotorFinished", s("Tail1"))], [sk("Critter", "setMotorSpeed", s("Tail1"), lit(0.8)), sk("Critter", "setMotorDuration", s("Tail1"), lit(0)), sk("Critter", "setMotor", s("Tail1"), s("wave"))]),
]
d.write("vscript/DemoRules.vscript.json", {"rules": rules})
d.write("project.json", {"schemaVersion": 2, "name": "Skeletons demo", "entryScene": "scenes/Skeletons.scene.json",
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "none"}})
d.write("README.md", """# Skeletons demo

Bones, skeletons and what moves them, in one scene.

- **The critter** plays its `idle` animation (keys on its body and head) with
  **motors** on top: its tail **waves**, its ears **jiggle** when its head
  moves. Click and its tail wags fast for two seconds (**Set motor
  duration**), easing in and out (the tail bone's **Motor Ease**), and **On
  motor finished** sets it back to its slow wave.
- **The arm** reaches for the mouse every step with **Aim bone**: two bones,
  the elbow's **Limit Angles** letting it bend one way only, its **Aim Lag**
  making it follow a little behind.
- **The snake** **follows** the mouse: its head's tip goes to the pointer
  and each bone before it trails behind, each joint limited to 45 degrees.
- **The flag** is one picture, a **Mesh Sprite**, bent by three bones; the
  middle one has a wave motor.
- **The blob** has no bones: a **deform** track on its skeleton's
  `breathe` animation eases its points between two shapes.

Choose a skeleton and open the **Timeline** tab to see its animations, turn
on **Onion** to see the poses either side of the playhead, and tick
**Preview motors and IK** in its Inspector to watch the motors while editing.

Made by `tools/make-skeletons-demo.py`.
""")
print("made %s" % out)
