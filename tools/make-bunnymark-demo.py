"""The BunnyMark demo: how many moving pictures the engine draws before the
frame rate drops. Two scenes, each with a HUD of the frame rate and the
count. Bunnies: plain bouncing bunnies, each moved by its own visual script,
as pixi.js's bunnymark does it. Trees: each one a bunny turning slowly with
a smaller bunny on it turning too, and a smaller one again. Hold the left
button to add ten a frame, the right to take ten away; 1 and 2 change scene.

    python3 tools/make-bunnymark-demo.py [demos/bunnymark]

Everything is drawn here. Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "bunnymark")
d = Demo(out, ["scenes/singletons", "vscript"], "b1000000")
W, H = 800, 600
L, T = -W // 2, -H // 2

# ── the bunny, 16 × 24, pixel art, white with pink ears as pixi's but smaller; four frames of a hop: ears out, a bob down, ears in ──
C = {"o": (60, 50, 60, 255), "w": (250, 250, 250, 255), "s": (205, 205, 220, 255), "p": (240, 160, 180, 255), "e": (30, 30, 40, 255)}
EARS = [
    "...oo......oo...",
    "..owwo....owwo..",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "...owwoooowwo..."]
EARS_OUT = [
    "..oo........oo..",
    ".owwo......owwo.",
    ".owpwo....owpwo.",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "...owwoooowwo..."]
EARS_IN = [
    "....oo....oo....",
    "...owwo..owwo...",
    "...owpwoowpwo...",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "..owpwo..owpwo..",
    "...owwoooowwo..."]
BODY = [
    "..owwwwwwwwwwo..",
    ".owwwwwwwwwwwwo.",
    ".oweewwwwwweewo.",
    ".oweewwwwwweewo.",
    ".owwwwwwwwwwwwo.",
    ".owwwwwppwwwwwo.",
    "..owwwwwwwwwwo..",
    "..owwwwwwwwwwo..",
    ".owwwwwwwwwwwwo.",
    "owwwwwwwwwwwwwwo",
    "owwwwwwwwwwwwwwo",
    "owwwwwwwwwwwwwwo",
    "owwwwwwwwwwwwwwo",
    "owwwwwwwwwwwwswo",
    ".owwwwwwwwwwsso.",
    ".owssswwwwwsssso",
    "..oooo....oooo.."]
# The bob: a row shorter in the middle, the gap left at the top so the feet stay put.
BODY_DOWN = BODY[:10] + BODY[11:]
frames = [drawn(EARS + BODY, C), drawn(EARS_OUT + BODY, C), drawn(["." * 16] + EARS + BODY_DOWN, C), drawn(EARS_IN + BODY, C)]
d.sprite("Bunny", 16, 24, [("hop", frames, 130, "loop")], [])
backing = canvas(150, 52)
ImageDraw.Draw(backing).rounded_rectangle([0, 0, 149, 51], radius=6, fill=(20, 20, 30, 210))
d.sprite("Backing", 150, 52, [("still", [backing], 400, "loop")], [])
strip = canvas(W, 26)
ImageDraw.Draw(strip).rectangle([0, 0, W - 1, 25], fill=(20, 20, 30, 210))
d.sprite("Strip", W, 26, [("still", [strip], 400, "loop")], [])

# ── Types ──
no_collision = {"collisionEnabled": False}
d.type_json("Bunny", "Sprite", dict(no_collision, spriteKey="Bunny.sprite.json"), [{"componentClass": "BunnyRules"}, {"componentClass": "BatchTint"}])
# The trees: a bunny turning, a smaller one on it turning, and a smaller one again. Only the root is tinted: a tint carries down to the twigs.
for name in ["TreeBunny", "Twig"]:
    d.type_json(name, "Sprite", dict(no_collision, spriteKey="Bunny.sprite.json"), [{"componentClass": "Rotate", "speed": 0}, {"componentClass": "TreeRules"}]
                + ([{"componentClass": "BatchTint"}] if name == "TreeBunny" else []))
d.type_json("Benches", "SceneManager", {"transition": "None"})
d.type_json("Backing", "Sprite", dict(no_collision, spriteKey="Backing.sprite.json"))
d.type_json("Strip", "Sprite", dict(no_collision, spriteKey="Strip.sprite.json"))
d.type_json("BunnyBench", "Node", {}, [{"componentClass": "BunnyBenchRules"}])
d.type_json("TreeBench", "Node", {}, [{"componentClass": "TreeBenchRules"}])
d.type_json("Switcher", "Node", {}, [{"componentClass": "SwitchRules"}])
for name, text, size in [("Title", "", 18), ("Caption", "", 14), ("FpsText", "0", 18), ("CountText", "0", 18)]:
    d.type_json(name, "Label", {"text": text, "fontSize": size})

# ── scenes ──
def hud(first_id, what):
    """The HUD: a Layer fixed to the screen, its children in the game's own pixels from the view's top-left."""
    u = d.uid
    return [
        {"id": u(first_id), "parent": u(1), "name": "HUD", "type": "Layer", "parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False, "zIndex": 10},
        {"id": u(first_id + 6), "parent": u(first_id), "name": "Backing1", "type": "Backing", "x": 79, "y": 30},
        {"id": u(first_id + 7), "parent": u(first_id), "name": "Strip1", "type": "Strip", "x": W // 2, "y": H - 15},
        {"id": u(first_id + 1), "parent": u(first_id), "name": "FpsCaption", "type": "Caption", "x": 8, "y": 8, "text": "FPS"},
        {"id": u(first_id + 2), "parent": u(first_id), "name": "FpsText1", "type": "FpsText", "x": 60, "y": 6},
        {"id": u(first_id + 3), "parent": u(first_id), "name": "CountCaption", "type": "Caption", "x": 8, "y": 30, "text": what},
        {"id": u(first_id + 4), "parent": u(first_id), "name": "CountText1", "type": "CountText", "x": 60, "y": 28},
        {"id": u(first_id + 5), "parent": u(first_id), "name": "Help", "type": "Caption", "x": 8, "y": H - 24,
         "text": "Hold left to add ten a frame, each press a new color; right takes ten away. 1 and 2 change scene."},
    ]
d.scene("scenes/Bunnies.scene.json", [{"id": d.uid(1), "name": "Bunnies"},
    {"id": d.uid(2), "parent": d.uid(1), "name": "BunnyBench1", "type": "BunnyBench", "x": 0, "y": 0}] + hud(10, "Bunnies"))
d.scene("scenes/Trees.scene.json", [{"id": d.uid(1), "name": "Trees"},
    {"id": d.uid(2), "parent": d.uid(1), "name": "TreeBench1", "type": "TreeBench", "x": 0, "y": 0}] + hud(10, "Trees"))
# One tree, made whole each time: 0.6 the size at each step down, each held off its parent's middle so the turn shows.
d.scene("scenes/BunnyTree.scene.json", [
    {"id": d.uid(1), "name": "TreeBunny1", "type": "TreeBunny"},
    {"id": d.uid(2), "parent": d.uid(1), "name": "Twig1", "type": "Twig", "x": 22, "y": -14, "scaleX": 0.6, "scaleY": 0.6},
    {"id": d.uid(3), "parent": d.uid(2), "name": "Twig2", "type": "Twig", "x": 22, "y": -14, "scaleX": 0.6, "scaleY": 0.6},
])
d.scene("scenes/singletons/Bench.scene.json", [{"id": d.uid(1), "name": "Bench"},
    {"id": d.uid(2), "parent": d.uid(1), "name": "Benches1", "type": "Benches"},
    {"id": d.uid(3), "parent": d.uid(1), "name": "Switcher1", "type": "Switcher"}])

# ── rules ──
x, y = value("self", "Node", "getPositionX"), value("self", "Node", "getPositionY")
# Each bunny: pixi's numbers, in pixels a second rather than a frame, played at
# three quarters of pixi's pace so the smoothness of the motion can be seen.
# Speeds scale by PACE and gravity by PACE squared, so the arcs are pixi's own.
PACE = 0.75
GRAVITY = 1800 * PACE * PACE   # pixi's 0.5 a frame at 60 frames a second, slowed
bunny_rules = [
    rule([line("self", "Node", "onCreated")],
         [set_sheet_var("vx", random(0, 600 * PACE)), set_sheet_var("vy", random(-300 * PACE, 300 * PACE)), line("self", "Node", "setPosition", lit(L), lit(T))]),
    rule([], [line("self", "Node", "setPosition", op("+", x, op("*", sheet_var("vx"), dt())), op("+", y, op("*", sheet_var("vy"), dt()))),
              add_sheet_var("vy", op("*", lit(GRAVITY), dt()))]),
    rule([line("self", "Node", "comparePositionX", lit(OBJ_GT), lit(-L))], [set_sheet_var("vx", op("*", sheet_var("vx"), lit(-1))), line("self", "Node", "setPositionX", lit(-L))]),
    rule([line("self", "Node", "comparePositionX", lit(OBJ_LT), lit(L))], [set_sheet_var("vx", op("*", sheet_var("vx"), lit(-1))), line("self", "Node", "setPositionX", lit(L))]),
    rule([line("self", "Node", "comparePositionY", lit(OBJ_GT), lit(-T))],
         [set_sheet_var("vy", op("*", sheet_var("vy"), lit(-0.85))), line("self", "Node", "setPositionY", lit(-T))],
         [rule([compare(random(0, 1), GT, lit(0.5))], [add_sheet_var("vy", op("*", random(0, 6), lit(-60 * PACE)))])]),
    rule([line("self", "Node", "comparePositionY", lit(OBJ_LT), lit(T))], [set_sheet_var("vy", lit(0)), line("self", "Node", "setPositionY", lit(T))]),
]
d.write("vscript/BunnyRules.vscript.json", {"vars": [{"name": "vx", "type": "number", "value": 0}, {"name": "vy", "type": "number", "value": 0}], "rules": bunny_rules})

# Each press of the left button picks the color of the batch; the first hundred are left white (255, 255, 255).
PARTS = ["red", "green", "blue"]
d.write("vscript/BatchTint.vscript.json", {"rules": [
    rule([line("self", "Node", "onCreated")], [line("self", "Node", "setTintRgb", *[var(c) for c in PARTS])])]})

# Every part of every tree in a batch turns at the batch's speed, picked with its color.
SPIN = 30   # degrees a second, either way
tree_rules = [rule([line("self", "Node", "onCreated")], [comp("self", "Rotate", "setSpeed", var("spin"))])]
d.write("vscript/TreeRules.vscript.json", {"rules": tree_rules})

FPS_EVERY = 0.5   # seconds between readings of the frame rate, so the number can be read

def bench(kind, count_scope, make, ready):
    # Create draws a Type's picture once Preload object type (or Preload scene) has loaded it: nothing is made before.
    frames, elapsed = sheet_var("frames"), sheet_var("elapsed")
    return [
        # Each scene starts white; then before the making below, so a press's first ten already take its color.
        # A tint can only darken, so each part starts at 60: no batch is lost against the black.
        rule([once()], [line("variables", "Variables", "setVariable", s(c), lit(255)) for c in PARTS]
             + [line("variables", "Variables", "setVariable", s("spin"), random(-SPIN, SPIN))]),
        rule([mouse_pressed(LEFT_BUTTON)], [line("variables", "Variables", "setVariable", s(c), random(60, 256)) for c in PARTS]
             + [line("variables", "Variables", "setVariable", s("spin"), random(-SPIN, SPIN))]),
        rule([ready, once(), system("repeat", lit(100))], [make]),
        rule([ready, mouse_down(LEFT_BUTTON), system("repeat", lit(10))], [make]),
        rule([mouse_down(RIGHT_BUTTON)], [sheet("destroyNewest", s(kind), lit(10))]),
        # The frames over the last half second, shown as a whole number.
        rule([], [add_sheet_var("frames", lit(1)), add_sheet_var("elapsed", dt()),
                  line("CountText", "Label", "setNumber", value(count_scope, "Node", "count"))]),
        rule([compare(elapsed, GE, lit(FPS_EVERY))],
             [line("FpsText", "Label", "setNumber", value("maths", "Maths", "round", op("/", frames, elapsed))),
              set_sheet_var("frames", lit(0)), set_sheet_var("elapsed", lit(0))]),
    ]
BENCH_VARS = [{"name": n, "type": "number", "value": 0} for n in ["frames", "elapsed"]]
d.write("vscript/BunnyBenchRules.vscript.json", {"vars": BENCH_VARS, "rules": bench("Bunny", "Bunny", sheet("createObject", s("Bunny"), lit(0)),
    sheet("objectTypeIsPreloaded", s("Bunny")))})
# A tree anywhere on the screen, kept a little in from its edges.
d.write("vscript/TreeBenchRules.vscript.json", {"vars": BENCH_VARS, "rules": bench("TreeBunny", "TreeBunny",
    sheet("createScene", s("scenes/BunnyTree.scene.json"), lit(0), random(L + 30, -L - 30), random(T + 30, -T - 30)),
    sheet("sceneIsPreloaded", s("scenes/BunnyTree.scene.json")))})
d.write("vscript/SwitchRules.vscript.json", {"rules": [
    rule([once()], [sheet("preloadObjectType", s("Bunny")), sheet("preloadScene", s("scenes/BunnyTree.scene.json"))]),
    rule([pressed("Bunnies")], [line("Benches", "SceneManager", "changeScene", s("Bunnies"))]),
    rule([pressed("Trees")], [line("Benches", "SceneManager", "changeScene", s("Trees"))]),
]})

d.write("project.json", {"schemaVersion": 2, "name": "BunnyMark", "entryScene": "scenes/Bunnies.scene.json",
    "singletons": ["scenes/singletons/Bench.scene.json"],
    "input": {"Bunnies": keys(49), "Trees": keys(50)},
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "arcade", "gravity": 0}})
d.write("README.md", """# BunnyMark

How many moving pictures the engine draws before the frame rate drops. The
HUD shows the frames a second and the count.

- **Bunnies** (press 1): plain bouncing bunnies. Each one has its own visual
  script, `vscript/BunnyRules`: a sideways and an upward speed of its own,
  gravity every step, a bounce off the bottom and the sides, as pixi.js's
  bunnymark does it, at three quarters of its pace so the smooth motion shows.
- **Trees** (press 2): each one a bunny with a **Rotate** behavior, with a
  bunny 0.6 its size on it turning too, and a smaller one again on that. Every
  part of every tree in a batch turns at that batch's speed, picked at random
  between 30 degrees a second either way with the batch's color. A tree is the
  scene `scenes/BunnyTree`, made whole by **Create scene**.

Hold the left mouse button to add ten a frame, the right to take ten away
(**Destroy the newest**), and watch for stutter, dropped frames and the
frame rate. Each press of the left button starts a batch in a new random
color, as pixi's does: `vscript/BatchTint` sets the tint from the red, green
and blue the press picked when a bunny (or a tree's root, whose twigs take it
from there) is made. The frame rate shown is the
average over each half second, rounded, so it can be read.

Generated by `tools/make-bunnymark-demo.py`; everything is drawn there.
""")
print("wrote", d.out)
