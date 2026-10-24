"""The skeletons demo: four characters, each showing off what bones do, drawn in SVG (tools/skeleton_art) and rigged here.

- The dinosaur walks; hold the mouse down on it and it runs. Rigid legs, arms, head and jaw on bones; the body with its
  neck, and the tail, are Mesh Sprites bent by their bones.
- The tree sways; hold the mouse down on it and the wind gets up. One picture of wood bent by a branching tree of bones
  with a sway motor at its foot; each leaf clump on a bone of its own with a jiggle motor.
- The jellyfish drifts; hold the mouse down on it and it swims. Its bell is a Mesh Sprite pulsed by deform keys; each
  tentacle a Mesh Sprite on a chain of bones with a wave motor.
- The dapper skeleton idles and tips its hat; hold the mouse down on it and it dances the Charleston. Every bone a rigid
  picture; its elbows limited so they never fold back.

Hold B to fade the pictures almost away and see the bones.

    python3 tools/make-skeletons-demo.py [demos/skeletons]

Needs Pillow, and node with the Loom repository beside this one (LOOMINARY_REPO) for resvg.
"""
import math, os, sys, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "skeleton_art"))
from demo_kit import *
import characters as C

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "demos", "skeletons")
d = Demo(out, ["scenes", "vscript", "scripts"], "a3000000")
# Drawn at 1920 x 1080 and shown in a 960 x 540 window (fit): every picture at twice the pixels it is shown at, sharp when scaled.
U = 2
W, H = 960 * U, 540 * U
GROUND = 200 * U   # the ground line, in the scene (its 0, 0 is the middle of the view)

# ── the characters, their pictures rendered from SVG ──
rigs = [(C.tree(0.52 * U), (-350 * U, GROUND)), (C.dinosaur(0.78 * U), (-75 * U, GROUND)), (C.dancer(1.0 * U), (170 * U, GROUND)), (C.jellyfish(1.1 * U), (380 * U, -5 * U))]
work = tempfile.mkdtemp()
for rig, _ in rigs:
    rig.render(work)
    for p in rig.parts:
        img = Image.open(p.png)
        tn = rig.name + p.name
        d.sprite(tn, img.width, img.height, [("still", [img], 400, "loop")], [])
        d.type_json(tn, "MeshSprite" if p.mesh else "Sprite", {"spriteKey": tn + ".sprite.json"})
    d.type_json(rig.name, "Skeleton", {})

# ── the scene ──
root = d.uid(1)
objs = [{"id": root, "name": "Skeletons"}]
seq = [10]
def put(name, type_name, parent=None, **fields):
    seq[0] += 1
    oid = d.uid(seq[0])
    objs.append(dict({"id": oid, "parent": parent or root, "name": name, "type": type_name}, **fields))
    return oid

# The sky and the jellyfish's tank, behind everything; the ground is a picture of its own, drawn IN FRONT of the
# characters, so a foot that dips below the ground line on a walk is hidden by it rather than seen through it.
sky = canvas(W, H)
g = ImageDraw.Draw(sky)
for y in range(H):
    t = y / H
    g.line([(0, y), (W, y)], fill=(int(176 + 50 * t), int(214 + 26 * t), int(240 + 8 * t), 255))
tank = (H // 2 - 160 * U, H // 2 + 175 * U)
g.rounded_rectangle([W // 2 + (380 - 92) * U, tank[0], W // 2 + (380 + 92) * U, tank[1]], radius=18 * U, fill=(150, 205, 232, 255), outline=(60, 110, 140, 255), width=4 * U)
for bx, by, br in [(x * U, y * U, r * U) for x, y, r in ((808, 140, 5), (918, 205, 3), (790, 300, 4), (925, 330, 3), (900, 395, 5))]:
    g.ellipse([bx - br, by - br, bx + br, by + br], outline=(235, 248, 255, 255), width=2)
d.sprite("Backdrop", W, H, [("still", [sky], 400, "loop")], [])
d.type_json("Backdrop", "Sprite", {"spriteKey": "Backdrop.sprite.json"})
put("Backdrop1", "Backdrop", x=-W / 2, y=-H / 2, pivotNormalized=True, pivotX=0, pivotY=0, zIndex=-10)
GH = H // 2 - GROUND
ground = canvas(W, GH)
g = ImageDraw.Draw(ground)
g.rectangle([0, 0, W, GH], fill=(122, 170, 86, 255))
g.line([(0, 1), (W, 1)], fill=(70, 110, 50, 255), width=3 * U)
d.sprite("Ground", W, GH, [("still", [ground], 400, "loop")], [])
d.type_json("Ground", "Sprite", {"spriteKey": "Ground.sprite.json"})
put("Ground1", "Ground", x=-W / 2, y=GROUND, pivotNormalized=True, pivotX=0, pivotY=0, zIndex=1)

def type_of(b): return "Bone"
# Each character is a scene of its own, its skeleton the scene's root, placed in the main scene as an instance:
# opened, it is edited on its own like any scene.
for k, (rig, at) in enumerate(rigs):
    cobjs = []
    cseq = [0]
    def cput(name, type_name, parent=None, **fields):
        cseq[0] += 1
        oid = d.uid(10000 * (k + 2) + cseq[0])
        o = dict({"id": oid, "name": name, "type": type_name}, **fields)
        if parent is not None: o["parent"] = parent
        cobjs.append(o)
        return oid
    rig.objects(cput, (0, 0), type_of, d)
    entry = cobjs[0]
    scene_path = "scenes/%s.scene.json" % rig.name
    objs.append({"id": d.uid(500 + k), "parent": root, "name": rig.name + "1", "sceneInstance": scene_path, "x": at[0], "y": at[1]})
    anims = getattr(C, rig.name.lower() + "_animations")(rig)
    entry["animations"] = {}
    # Only what moves gets a track, the same set in every animation of the skeleton so a blend between them puts each back.
    props = rig.moving([spec[1] for spec in anims.values()])
    for name, spec in anims.items():
        dur, akeys = spec[0], spec[1]
        # The gaits are dense keys of a steady motion: straight lines between them, no slowing at each key.
        tracks = rig.keyed(akeys, props, ease=None if rig.name == "Dinosaur" else "easeInOut")
        if len(spec) > 2:
            tracks.append({"target": rig.name + "BellPicture", "property": "deform", "keys": spec[2]})
        entry["animations"][name] = {"duration": dur, "mode": "loop", "markers": [], "tracks": tracks}
    if entry["animations"]:
        entry["animation"] = list(anims)[0]
    entry.pop("x", None); entry.pop("y", None)
    d.scene(scene_path, cobjs)

# Where the mouse counts as on each character: an invisible box each.
AREAS = {name: tuple(v * U for v in box) for name, box in {"TreeArea": (-350, 100, 250, 200), "DinosaurArea": (-75, 105, 240, 190),
         "DancerArea": (170, 80, 120, 240), "JellyfishArea": (380, 30, 180, 320)}.items()}
for name, (cx, cy, w, h) in AREAS.items():
    d.sprite(name, w, h, [("still", [canvas(w, h)], 400, "loop")], [box("area", w / 2, h / 2, w, h)])
    d.type_json(name, "Sprite", {"spriteKey": name + ".sprite.json"})
    # Behind the characters: a press in the editor reaches the character, and the rules ask containsPoint, which ignores the order.
    put(name + "1", name, x=cx, y=cy, pivotNormalized=True, pivotX=0.5, pivotY=0.5, zIndex=-1)

d.type_json("Caption", "Label", {"text": "", "fontSize": 12 * U, "textColor": 0x24331F, "hAlign": "Center"})
for i, (x, text) in enumerate([(-350, "Mesh and motors.\nHold the mouse on it: wind."),
                              (-75, "Bones and meshes.\nHold the mouse on it: it runs."),
                              (170, "Bones only, elbows limited.\nHold the mouse on it: it dances."),
                              (380, "Mesh, deform keys, motors.\nHold the mouse on it: it swims.")]):
    put("Caption%d" % (i + 1), "Caption", x=(x - 110) * U, y=GROUND + 12 * U, boxWidth=220 * U, text=text, zIndex=2)
put("Hint1", "Caption", x=-W / 2 + 10 * U, y=-H / 2 + 8 * U, boxWidth=300 * U, text="Hold B to see the bones.", hAlign="Left", zIndex=2)
put("Demo1", "Demo")
d.scene("scenes/Skeletons.scene.json", objs)

# ── the rules ──
def sk(t, name, *params): return line(t, "Skeleton", name, *params)
PX = value("input", "Input", "worldPositionX")
PY = value("input", "Input", "worldPositionY")
def on(area): return line(area, "Node", "containsPoint", PX, PY)
def held_on(area, char, var, active, rest, blend_in, blend_out):
    """Mouse down on the character: it crosses into its active animation; let go, or off it: back."""
    return [
        rule([mouse_down(LEFT_BUTTON), on(area), compare(sheet_var(var), EQ, lit(0))], [sk(char, "blendToAnimation", s(active), lit(blend_in)), set_sheet_var(var, lit(1))]),
        rule([compare(sheet_var(var), EQ, lit(1)), not_(mouse_down(LEFT_BUTTON))], [sk(char, "blendToAnimation", s(rest), lit(blend_out)), set_sheet_var(var, lit(0))]),
        rule([compare(sheet_var(var), EQ, lit(1)), not_(on(area))], [sk(char, "blendToAnimation", s(rest), lit(blend_out)), set_sheet_var(var, lit(0))]),
    ]
rules = [rule([once()], [sk("Dinosaur", "playAnimation", s("walk")), sk("Dancer", "playAnimation", s("idle")), sk("Jellyfish", "playAnimation", s("drift"))])]
rules += held_on("DinosaurArea", "Dinosaur", "running", "run", "walk", 0.35, 0.5)
rules += held_on("DancerArea", "Dancer", "dancing", "charleston", "idle", 0.5, 0.5)
rules += held_on("JellyfishArea", "Jellyfish", "swimming", "swim", "drift", 0.4, 0.8)
# The wind: eased toward strong while the mouse is down on the tree, back to a breeze after; the sway motor's amount follows it.
rules += [
    rule([], [set_sheet_var("wind", lit(0))]),
    rule([mouse_down(LEFT_BUTTON), on("TreeArea")], [set_sheet_var("wind", lit(1))]),
    rule([], [add_sheet_var("gust", op("*", op("-", sheet_var("wind"), sheet_var("gust")), op("*", dt(), lit(2)))),
              sk("Oak", "setMotorAmount", s("Trunk1"), op("+", lit(2.5), op("*", sheet_var("gust"), lit(7))))]),
]
d.write("vscript/DemoRules.vscript.json", {"vars": [{"name": n, "type": "number", "value": 0} for n in ("running", "dancing", "swimming", "wind", "gust")], "rules": rules})
d.type_json("Demo", "Node", {}, [{"componentClass": "DemoRules"}, {"componentClass": "XRay"}])
d.write("scripts/XRay.hx", open(os.path.join(HERE, "skeleton_art", "XRay.hx")).read())

d.write("project.json", {"schemaVersion": 2, "name": "Skeletons demo", "entryScene": "scenes/Skeletons.scene.json",
    "display": {"width": W, "height": H, "windowWidth": W // U, "windowHeight": H // U, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "input": {"Bones": keys(66)},
    "physics": {"engine": "none"}})
d.write("README.md", open(os.path.join(HERE, "skeleton_art", "README.md")).read())
shutil.rmtree(work)
print("made %s" % out)
