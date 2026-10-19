"""The particle effects demo: a scene for each thing a Particles object does,
every effect a `.effect.json` of its own in `assets/effects`, on sprites drawn
here (a soft spot, a spark, a drop, a flake, a ring that grows frame by
frame). Keys 1 to 6 change scene through a Scene Manager in the singleton
scene.

    python3 tools/make-effects-demo.py [demos/effects]

Needs Pillow.
"""
import math, os, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "effects")
d = Demo(out, ["scenes/singletons", "vscript", "assets/effects"], "e1000000")
W, H = 960, 540

# ── the pictures ──
def panel(w, h, fill, edge, radius=3):
    img = canvas(w, h)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill, outline=edge, width=2)
    return img

def ring(size, r0, r1, colour=(255, 255, 255)):
    """A soft ring between two radii: one frame of a puff that grows."""
    img = canvas(size, size)
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            dist = math.hypot(x - c, y - c)
            if r0 <= dist <= r1:
                t = (dist - r0) / max(1, r1 - r0)
                a = math.sin(t * math.pi)
                img.putpixel((x, y), colour + (int(255 * a),))
    return img

def flake(size=16):
    img = canvas(size, size); g = ImageDraw.Draw(img)
    c = size / 2
    for k in range(3):
        a = k * math.pi / 3
        g.line([c + math.cos(a) * (c - 1), c + math.sin(a) * (c - 1), c - math.cos(a) * (c - 1), c - math.sin(a) * (c - 1)], fill=(255, 255, 255, 230), width=2)
    return img

def drop(w=16, h=6):
    """A streak drawn pointing right: a particle is turned to the way it travels from there."""
    img = canvas(w, h); g = ImageDraw.Draw(img)
    g.rounded_rectangle([0, 0, w - 1, h - 1], radius=3, fill=(255, 255, 255, 220))
    return img

STONE, STONE_EDGE = (110, 112, 124, 255), (66, 68, 78, 255)
d.sprite("Puff", 24, 24, [("still", [soft_dot(24, (255, 255, 255), 1.2)], 400, "loop")], [])
d.sprite("Spark", 8, 8, [("still", [soft_dot(8, (255, 255, 255), 1.8)], 400, "loop")], [])
d.sprite("Drop", 16, 6, [("still", [drop()], 400, "loop")], [])
d.sprite("Flake", 16, 16, [("still", [flake()], 400, "loop")], [])
d.sprite("Ring", 32, 32, [("grow", [ring(32, 2, 7), ring(32, 6, 11), ring(32, 10, 14), ring(32, 13, 15.5)], 120, "loop")], [])
d.sprite("Floor", 700, 20, [("still", [panel(700, 20, STONE, STONE_EDGE, 0)], 400, "loop")], [box("body", 350, 10, 700, 20)])
d.sprite("Roof", 220, 16, [("still", [panel(220, 16, (120, 70, 50, 255), (70, 40, 30, 255), 2)], 400, "loop")], [box("body", 110, 8, 220, 16)])
log = panel(90, 22, (120, 80, 45, 255), (70, 45, 25, 255), 6)
ImageDraw.Draw(log).line([8, 11, 82, 11], fill=(90, 60, 32, 255), width=3)
d.sprite("Log", 90, 22, [("still", [log], 400, "loop")], [])
crate = panel(30, 30, (196, 140, 82, 255), (100, 64, 34, 255), 2)
ImageDraw.Draw(crate).line([4, 4, 25, 25], fill=(100, 64, 34, 255), width=2)
d.sprite("Crate", 30, 30, [("still", [crate], 400, "loop")], [box("body", 15, 15, 30, 30)])
grinder = canvas(36, 36)
ImageDraw.Draw(grinder).ellipse([1, 1, 34, 34], fill=(120, 120, 130, 255), outline=(60, 60, 66, 255), width=3)
d.sprite("Grinder", 36, 36, [("still", [grinder], 400, "loop")], [])
wand = canvas(14, 14)
ImageDraw.Draw(wand).ellipse([1, 1, 12, 12], fill=(230, 200, 255, 255), outline=(120, 80, 200, 255), width=2)
d.sprite("Wand", 14, 14, [("still", [wand], 400, "loop")], [])

# ── the effects ──
def argb(a, rgb): return int.from_bytes(((a << 24) | rgb).to_bytes(4, "big"), "big", signed=True)
def hold(): return {"shape": "Hold"}
def linear(end, spread=0): return {"shape": "Linear", "end": end, "endSpread": spread}
def ease(end, kind="Quad", direction="Out", spread=0): return {"shape": "Ease", "ease": kind, "direction": direction, "end": end, "endSpread": spread}
def peak(mid, end, spread=0): return {"shape": "Peak", "mid": mid, "end": end, "endSpread": spread}
def custom(*pts): return {"shape": "Custom", "points": list(pts)}
def gradient(*stops): return {"shape": "Gradient", "stops": list(stops)}
def spread(value, s, random=None): return dict({"value": value, "spread": s}, **({"random": random} if random else {}))

def effect(sprite, **over):
    e = {"version": 1, "sprite": sprite, "animations": [], "animationSpeed": "fixed", "randomness": "normal", "blend": "add",
        "emission": {"mode": "continuous", "rate": 40, "rateOverTime": hold(), "cycle": 2, "repeat": True, "shape": "point", "width": 32, "height": 32, "edgeOnly": False,
                     "direction": "facing", "angle": 0, "spread": 30, "warmUp": 0, "lifetime": spread(1.2, 0.3), "maxParticles": 600, "local": False, "offScreen": True, "under": False},
        "start": {"speed": spread(120, 30), "spin": spread(0, 0), "angle": "travel", "angleSpread": 0, "size": spread(1, 0),
                  "opacity": spread(1, 0), "color": argb(255, 0xffffff), "color2": argb(255, 0xffffff), "offsetX": 0, "offsetY": 0},
        "life": {"size": hold(), "opacity": linear(0), "color": hold(), "speed": hold(), "spin": hold(), "direction": hold()},
        "forces": {"gravityX": 0, "gravityY": 0, "drag": 0, "windX": 0, "windY": 0, "windOverTime": hold(), "windCycle": 2, "windRepeat": True, "windSpread": 0,
                   "push": 0, "swirl": 0, "turbulence": 0, "turbulenceStrength": 0, "speedJitter": 0},
        "collision": {"on": False, "mask": -1, "radius": 0, "onHit": "bounce", "bounce": 0.6, "friction": 0.8, "bounceSpin": 0, "bounces": 0}}
    for k, v in over.items():
        cur = e
        parts = k.split(".")
        for part in parts[:-1]: cur = cur[part]
        cur[parts[-1]] = v
    return e

EFFECTS = {
    # A fire: a line of flames rising, white to orange to dark, each flame tumbling a little and buffeted.
    "Fire": effect("Puff.sprite.json", **{"emission.rate": 110, "emission.shape": "line", "emission.width": 60, "emission.direction": "angle", "emission.angle": -90, "emission.spread": 20,
        "emission.lifetime": spread(0.9, 0.3), "emission.warmUp": 1, "start.speed": spread(130, 30), "start.spin": spread(0, 40), "start.size": spread(1.3, 0.4),
        "life.size": linear(0.2, 0.1), "life.opacity": ease(0, "Quad", "In"),
        "life.color": gradient(0, argb(255, 0xfff2b0), 0.3, argb(255, 0xff9a20), 0.7, argb(255, 0xc82a08), 1, argb(0, 0x400000)),
        "forces.gravityY": -170, "forces.drag": 0.8, "forces.turbulence": 1.5, "forces.turbulenceStrength": 0.6}),
    # Smoke: slow grey puffs that swell and fade, the wind on them rising and falling over six seconds.
    "Smoke": effect("Puff.sprite.json", **{"blend": "mix", "emission.rate": 22, "emission.shape": "circle", "emission.width": 36, "emission.height": 36, "emission.direction": "angle", "emission.angle": -90, "emission.spread": 30,
        "emission.lifetime": spread(3.2, 0.8), "emission.warmUp": 2.5, "emission.maxParticles": 300, "start.speed": spread(40, 15), "start.spin": spread(0, 30), "start.size": spread(1.1, 0.3), "start.opacity": spread(0.5, 0.1),
        "life.size": linear(3.2, 0.5), "life.opacity": ease(0, "Quad", "Out"), "life.color": gradient(0, argb(255, 0x9a9a9a), 1, argb(0, 0x404040)),
        "forces.gravityY": -18, "forces.windX": 90, "forces.windOverTime": peak(1, 0), "forces.windCycle": 6, "forces.windRepeat": True, "forces.windSpread": 0.6,
        "forces.drag": 0.3, "forces.turbulence": 0.8, "forces.turbulenceStrength": 0.5}),
    # Embers: a burst flung from a point, falling and dying out.
    "Embers": effect("Spark.sprite.json", **{"emission.mode": "burst", "emission.rate": 50, "emission.spread": 360, "emission.lifetime": spread(1.4, 0.5),
        "start.speed": spread(220, 80, "even"), "start.spin": spread(0, 300), "start.size": spread(1, 0.3),
        "life.size": linear(0.3), "life.opacity": ease(0, "Quad", "In"), "life.color": gradient(0, argb(255, 0xffe080), 0.5, argb(255, 0xff6a10), 1, argb(0, 0x801000)),
        "forces.gravityY": 420, "forces.drag": 0.6}),
    # Rain: a wide line of drops falling at a slant, bouncing once off what they land on.
    "Rain": effect("Drop.sprite.json", **{"blend": "mix", "randomness": "even", "emission.rate": 240, "emission.shape": "line", "emission.width": 1000, "emission.direction": "angle", "emission.angle": 96, "emission.spread": 3,
        "emission.lifetime": spread(1.8, 0.2), "emission.warmUp": 1.8, "emission.maxParticles": 1500, "start.speed": spread(560, 60), "start.size": spread(0.9, 0.2), "start.opacity": spread(0.7, 0.2),
        "life.opacity": hold(), "life.color": gradient(0, argb(255, 0xaaccff), 1, argb(255, 0x88aaee)),
        "forces.gravityY": 300, "collision.on": True, "collision.radius": 3, "collision.onHit": "bounce", "collision.bounce": 0.2, "collision.friction": 0.3, "collision.bounces": 1}),
    # Snow: flakes drifting down, each feeling the wind its own way, turning slowly.
    "Snow": effect("Flake.sprite.json", **{"blend": "mix", "emission.rate": 60, "emission.shape": "line", "emission.width": 1000, "emission.direction": "angle", "emission.angle": 90, "emission.spread": 10,
        "emission.lifetime": spread(12, 1.5), "emission.warmUp": 10, "emission.maxParticles": 1100, "start.speed": spread(95, 15), "start.spin": spread(20, 40), "start.size": spread(0.7, 0.3), "start.opacity": spread(0.9, 0.1),
        "life.opacity": custom(0, 1, 0.8, 1, 1, 0), "life.color": hold(),
        "forces.windX": 40, "forces.windOverTime": peak(1, 0), "forces.windCycle": 5, "forces.windSpread": 0.8, "forces.turbulence": 0.6, "forces.turbulenceStrength": 0.8,
        "collision.on": True, "collision.radius": 4, "collision.onHit": "stick", "collision.mask": 1}),
    # Sparks off a grinder: fast, bright, bouncing twice then gone; what they hit is picked by a rule.
    "Sparks": effect("Spark.sprite.json", **{"emission.rate": 160, "emission.spread": 28, "emission.lifetime": spread(0.9, 0.3), "start.speed": spread(420, 120, "even"), "start.size": spread(1, 0.4),
        "life.size": linear(0.2), "life.opacity": linear(0, 0.3), "life.color": gradient(0, argb(255, 0xffffff), 0.3, argb(255, 0xffd060), 1, argb(0, 0xff4000)),
        "forces.gravityY": 500, "collision.on": True, "collision.radius": 2, "collision.onHit": "bounce", "collision.bounce": 0.5, "collision.friction": 0.6, "collision.bounceSpin": 400, "collision.bounces": 2}),
    # Magic: a ring of motes flung outward and swirled round, carried with the wand that makes them.
    "MagicLocal": effect("Puff.sprite.json", **{"emission.rate": 150, "emission.shape": "ring", "emission.width": 40, "emission.height": 40, "emission.direction": "outward", "emission.spread": 40,
        "emission.lifetime": spread(1.2, 0.3), "emission.local": True, "start.speed": spread(40, 20), "start.size": spread(0.5, 0.2),
        "life.size": peak(1.2, 0), "life.opacity": linear(0), "life.color": gradient(0, argb(255, 0xd080ff), 0.5, argb(255, 0x60e0ff), 1, argb(0, 0x2040ff)),
        "forces.push": 60, "forces.swirl": 220, "forces.drag": 0.2}),
    # The same, left in the world as the wand moves on.
    "MagicWorld": effect("Puff.sprite.json", **{"emission.rate": 150, "emission.shape": "ring", "emission.width": 40, "emission.height": 40, "emission.direction": "outward", "emission.spread": 40,
        "emission.lifetime": spread(1.2, 0.3), "emission.local": False, "start.speed": spread(40, 20), "start.size": spread(0.5, 0.2),
        "life.size": peak(1.2, 0), "life.opacity": linear(0), "life.color": gradient(0, argb(255, 0xffb060), 0.5, argb(255, 0xff60a0), 1, argb(0, 0xff2040)),
        "forces.push": 60, "forces.swirl": 220, "forces.drag": 0.2}),
    # Rings that play their four frames across each particle's life, and the same at the animation's own pace.
    "RingsOverLife": effect("Ring.sprite.json", **{"blend": "mix", "animations": ["grow"], "animationSpeed": "over life", "emission.rate": 6, "emission.shape": "box", "emission.width": 200, "emission.height": 120, "emission.spread": 360,
        "emission.lifetime": spread(1.6, 0.4), "start.speed": spread(0, 0), "start.size": spread(1.4, 0.4), "start.opacity": spread(0.9, 0), "life.opacity": linear(0),
        "life.color": gradient(0, argb(255, 0x80ffd0), 1, argb(255, 0x40a0ff))}),
    "RingsOwnPace": effect("Ring.sprite.json", **{"blend": "mix", "animations": ["grow"], "animationSpeed": "fixed", "emission.rate": 6, "emission.shape": "box", "emission.width": 200, "emission.height": 120, "emission.edgeOnly": True, "emission.spread": 360,
        "emission.lifetime": spread(1.6, 0.4), "start.speed": spread(0, 0), "start.size": spread(1.4, 0.4), "start.opacity": spread(0.9, 0), "life.opacity": linear(0),
        "life.color": gradient(0, argb(255, 0xffd080), 1, argb(255, 0xff80a0))}),
    # A geyser: its rate rising and falling over a three-second cycle, the water arcing and falling.
    "Geyser": effect("Drop.sprite.json", **{"blend": "mix", "emission.rate": 320, "emission.rateOverTime": custom(0, 0, 0.2, 1, 0.5, 0.8, 0.7, 0, 1, 0), "emission.cycle": 3, "emission.repeat": True,
        "emission.shape": "line", "emission.width": 16, "emission.direction": "angle", "emission.angle": -90, "emission.spread": 12, "emission.lifetime": spread(1.6, 0.2), "emission.maxParticles": 1200,
        "start.speed": spread(520, 40), "start.angle": "travel", "start.size": spread(0.9, 0.2), "start.opacity": spread(0.8, 0.2),
        "life.opacity": hold(), "life.color": gradient(0, argb(255, 0xc0e0ff), 0.8, argb(255, 0x80b0ff), 1, argb(0, 0x80b0ff)),
        "forces.gravityY": 600, "forces.turbulence": 0.5, "forces.turbulenceStrength": 0.2}),
    # A firework: a burst whose motes slow as they spread, their trails made by a second effect.
    "Firework": effect("Spark.sprite.json", **{"emission.mode": "burst", "emission.rate": 90, "emission.spread": 360, "emission.lifetime": spread(1.8, 0.3),
        "start.speed": spread(260, 20), "start.size": spread(1.2, 0.3), "life.speed": ease(0.1, "Quad", "Out"), "life.size": linear(0.4), "life.opacity": custom(0, 1, 0.7, 1, 1, 0),
        "life.color": gradient(0, argb(255, 0xffffff), 0.3, argb(255, 0xffe060), 0.7, argb(255, 0xff5080), 1, argb(0, 0x8020ff)),
        "forces.gravityY": 120, "forces.speedJitter": 0.3}),
}
for name, e in EFFECTS.items(): d.write("assets/effects/%s.effect.json" % name, e)

# ── the Types ──
for name in EFFECTS:
    d.type_json(name, "Particles", {"effectKey": "assets/effects/%s.effect.json" % name, "spriteKey": EFFECTS[name]["sprite"]})
for name, w, h in [("Floor", 700, 20), ("Roof", 220, 16), ("Crate", 30, 30)]:
    d.type_json(name, "Sprite", {"spriteKey": name + ".sprite.json", "collision": {"layer": 1, "mask": -1, "shapes": [box("body", w / 2, h / 2, w, h)]}})
d.type_json("Log", "Sprite", {"spriteKey": "Log.sprite.json"})
d.type_json("Grinder", "Sprite", {"spriteKey": "Grinder.sprite.json"}, [{"componentClass": "Rotate", "speed": 240}])
# One Type a wand, so a rule can move each by name.
for name in ["WandL", "WandR"]: d.type_json(name, "Sprite", {"spriteKey": "Wand.sprite.json"})
for name, size in [("Help", 13), ("Caption", 13), ("Hits", 13)]:
    d.type_json(name, "Label", {"text": "", "fontSize": size})

px, py = value("input", "Input", "worldPositionX"), value("input", "Input", "worldPositionY")
def pt(t, name, *params): return line(t, "Particles", name, *params)

# The ground, clear of the scene list along the bottom.
FLOOR_Y = 215
SCENES = []
def feature(file, title, about, controls, build, rules):
    """A scene: its own objects under one root, a Level whose sheet holds its rules, and lines saying what it shows."""
    seq = [0]
    root = d.uid(2000 + len(SCENES) * 100)
    objects = [{"id": root, "name": file}]
    def place(name, type_name, x, y, **extra):
        seq[0] += 1
        objects.append(dict({"id": d.uid(2000 + len(SCENES) * 100 + seq[0]), "parent": root, "name": name, "type": type_name, "x": x, "y": y}, **extra))
    sheet_name = file + "Rules"
    level = file + "Level"
    d.type_json(level, "Node", {}, [{"componentClass": sheet_name}])
    place(level + "1", level, 0, 0)
    place("Title", "Caption", -470, -262, text=title)
    # A line the screen cannot hold goes on to the next.
    lines = [w for t in (about if isinstance(about, list) else [about]) for w in textwrap.wrap(t, 125)]
    for k, text in enumerate(lines): place("About%d" % (k + 1), "Help", -470, -244 + 18 * k, text=text)
    place("Controls", "Help", -470, -244 + 18 * len(lines), text=controls)
    build(place)
    d.scene("scenes/%s.scene.json" % file, objects)
    d.write("vscript/%s.vscript.json" % sheet_name, {"rules": rules})
    SCENES.append((file, title))

# 1. The campfire: fire and smoke on gradients and curves, embers burst where you click.
def campfire(place):
    place("Log1", "Log", -60, 180)
    place("Fire1", "Fire", -60, 172)
    place("Smoke1", "Smoke", -60, 150)
    place("Embers1", "Embers", 0, 0)
feature("Campfire", "A campfire", [
    "Fire: a line of flames with a four-stop color gradient over the life, size falling and opacity easing out, turbulence, drag, and a second of warm up.",
    "Smoke: slow puffs that swell three times over, drifting on a wind that rises and falls over a six-second cycle, each puff feeling it its own way.",
], "click: a burst of embers where you point (a Burst effect, with Even randomness on its speed)", campfire, [
    rule([mouse_pressed(LEFT_BUTTON)], [line("Embers", "Node", "setPosition", px, py), pt("Embers", "burst", lit(50))]),
])

# 2. Rain and snow: collision with the roof and the ground; Even against Normal randomness.
def weather(place):
    place("Floor1", "Floor", 0, FLOOR_Y)
    place("Roof1", "Roof", 180, 60, rotation=-0.25)
    place("Rain1", "Rain", 0, -300)
    place("Snow1", "Snow", 0, -300, emitting=False)
feature("RainAndSnow", "Rain and snow", [
    "Rain: a wide line of drops with Even randomness, each swept as a circle through the world's shapes; they bounce once off the roof and the ground, then go.",
    "Snow: flakes with Normal randomness, turning as they fall, on a wind that gusts over five seconds and that each flake feels differently; they stick where they land.",
], "hold R to stop the rain   hold S for snow instead", weather, [
    rule([held("Rain")], [pt("Rain", "stopEmitting")]),
    rule([not_(held("Rain")), not_(held("Snow"))], [pt("Rain", "startEmitting")]),
    rule([held("Snow")], [pt("Snow", "startEmitting"), pt("Rain", "stopEmitting")]),
    rule([not_(held("Snow"))], [pt("Snow", "stopEmitting")]),
])

# 3. Sparks that hit: On particle hit picks the crates the sparks land on.
def sparks(place):
    place("Floor1", "Floor", 0, FLOOR_Y)
    place("Grinder1", "Grinder", -300, 40, rotation=0.5)
    place("Sparks1", "Sparks", -300, 40, rotation=0.5)
    for i, (x, y) in enumerate([(-120, 225), (-60, 225), (0, 225), (60, 225), (-90, 195), (-30, 195), (30, 195), (-60, 165), (0, 165)]):
        place("Crate%d" % (i + 1), "Crate", x, y - (250 - FLOOR_Y))
    place("HitsCaption", "Caption", 160, -120, text="Sparks hitting a crate this step:")
    place("Hits1", "Hits", 400, -120, text="0")
feature("SparksThatHit", "Sparks that hit", [
    "Sparks fly off a grinder, bounce twice with spin and then go. The rule 'On particle hit Crate' picks the crates the sparks land on, and tints them; a second later they are plain again.",
    "hitCount says how many hit something this step.",
], "click: move the grinder to where you point", sparks, [
    rule([pt("Sparks", "onParticleHit", s("Crate"))], [line("Crate", "Node", "setTint", s("#ff9040"))]),
    rule([sheet("every", lit(1))], [line("Crate", "Node", "setTint", s("#ffffff"))]),
    # The emitter picked by a condition, so the readout's action can read its count.
    rule([pt("Sparks", "isEmitting")], [line("Hits", "Label", "setNumber", value("Sparks", "Particles", "hitsThisStep"))]),
    rule([mouse_pressed(LEFT_BUTTON)], [line("Grinder", "Node", "setPosition", px, py), line("Sparks", "Node", "setPosition", px, py)]),
])

# 4. Magic: a ring of motes pushed outward and swirled; local particles move with the wand, world ones are left behind.
def orbit_x(centre): return op("+", op("*", value("maths", "Maths", "cosine", op("*", value("system", "System", "getElapsedTime"), lit(90))), lit(110)), lit(centre))
def orbit_y(): return op("*", value("maths", "Maths", "sine", op("*", value("system", "System", "getElapsedTime"), lit(90))), lit(70))
def magic(place):
    place("WandL1", "WandL", -200, 0)
    place("MagicLocal1", "MagicLocal", -200, 0)
    place("WandR1", "WandR", 200, 0)
    place("MagicWorld1", "MagicWorld", 200, 0)
    place("LeftCaption", "Caption", -260, -130, text="Carried with the wand (Move with the emitter: yes)")
    place("RightCaption", "Caption", 100, -130, text="Left in the world (no)")
feature("Magic", "Magic", [
    "Motes born on a ring, sent outward, pushed from the center and swirled round it, their size peaking mid-life on a purple-to-cyan gradient.",
    "Both wands orbit; the left one's motes move with it, the right one's stay where they were made.",
], "", magic, [
    # Each wand and its emitter are put at the same place by the same sums: no rule reads another type's position.
    rule([], [line("WandL", "Node", "setPosition", orbit_x(-200), orbit_y()), line("MagicLocal", "Node", "setPosition", orbit_x(-200), orbit_y())]),
    rule([], [line("WandR", "Node", "setPosition", orbit_x(200), orbit_y()), line("MagicWorld", "Node", "setPosition", orbit_x(200), orbit_y())]),
])

# 5. Rings: a four-frame animation played across each particle's life, and at its own pace.
def rings(place):
    place("RingsOverLife1", "RingsOverLife", -230, 60)
    place("RingsOwnPace1", "RingsOwnPace", 230, 60)
    place("LeftCaption", "Caption", -330, -60, text="The frames spread over each ring's life")
    place("RightCaption", "Caption", 130, -60, text="The frames at the animation's own pace, on a box's edge")
feature("AnimatedRings", "Animated particles", [
    "Each particle plays the sprite's 'grow' animation: on the left its four frames are spread across the particle's life, so every ring grows once however long it lives;",
    "on the right they run at the animation's own pace, born only on the edge of a box.",
], "", rings, [])

# 6. A geyser on a rate curve, and fireworks on a click.
def bursts(place):
    place("Floor1", "Floor", 0, FLOOR_Y)
    place("Geyser1", "Geyser", -250, FLOOR_Y - 12)
    place("Firework1", "Firework", 0, 0, emitting=False)
feature("GeyserAndFireworks", "A geyser and fireworks", [
    "The geyser's rate follows a hand-drawn curve over a three-second cycle, round and round: a spurt, a sigh, nothing, again.",
    "A firework is a burst whose motes ease to a stop as they spread, fade late, and change color four times.",
], "click: a firework where you point", bursts, [
    rule([mouse_pressed(LEFT_BUTTON)], [line("Firework", "Node", "setPosition", px, py), pt("Firework", "burst", lit(90))]),
])

# ── the singleton: the scene list and the keys that change scene ──
d.type_json("Scenes", "SceneManager", {"transition": "Fade", "fadeTime": 0.15})
d.type_json("Switcher", "Node", {}, [{"componentClass": "SwitchRules"}])
d.type_json("SceneList", "Label", {"text": "", "fontSize": 13})
keys_for = [str(i + 1) for i in range(len(SCENES))]
listing = "   ".join("%s %s" % (k, title) for k, (_, title) in zip(keys_for, SCENES))
d.scene("scenes/singletons/Demo.scene.json", [
    {"id": d.uid(3001), "name": "Demo"},
    {"id": d.uid(3002), "parent": d.uid(3001), "name": "Scenes1", "type": "Scenes"},
    {"id": d.uid(3003), "parent": d.uid(3001), "name": "Switcher1", "type": "Switcher"},
    {"id": d.uid(3004), "parent": d.uid(3001), "name": "SceneList1", "type": "SceneList", "x": -470, "y": 238, "text": listing},
])
d.write("vscript/SwitchRules.vscript.json", {"rules": [
    rule([pressed("Scene" + k)], [line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % f))]) for k, (f, _) in zip(keys_for, SCENES)]})

d.write("project.json", {"schemaVersion": 2, "name": "Particle effects demo", "entryScene": "scenes/Campfire.scene.json",
    "collisionLayers": {"1": "Solid"},
    "singletons": ["scenes/singletons/Demo.scene.json"],
    "input": dict({"Rain": keys(82), "Snow": keys(83)}, **{"Scene" + k: keys(ord(k)) for k in keys_for}),
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "arcade", "gravity": 980}})
d.write("README.md", """# Particle effects demo

A scene for each thing a **Particles** object does. Every effect is a
`.effect.json` under `assets/effects`, opened on its own page by
double-clicking it; each emitter in a scene is a Type built on Particles
that names its effect, and any emitter's **Preview** in the Inspector plays
it in the viewport.

Keys **1** to **6** change scene (a Scene Manager in the singleton scene
`scenes/singletons/Demo`); each scene says what it shows and its keys.

| Key | Scene | What it shows |
|---|---|---|
| 1 | A campfire | a four-stop color gradient, size and opacity curves, turbulence, warm up; smoke on a wind that rises and falls over a cycle; a **Burst** of embers where you click |
| 2 | Rain and snow | **collision**: rain bouncing once off a roof and the ground, snow sticking where it lands; **Even** against **Normal** randomness; wind each flake feels its own way |
| 3 | Sparks that hit | **On particle hit** picking the crates the sparks land on; bounce spin and a bounce count; **hitCount** |
| 4 | Magic | a ring shape, outward direction, push and swirl, a Peak size curve; particles carried with the emitter against left in the world |
| 5 | Animated particles | each particle playing the sprite's animation, across its life or at its own pace; a box's edge |
| 6 | A geyser and fireworks | a hand-drawn **rate over time** curve on a repeating cycle; a burst whose speed eases to a stop, with a late fade |

The sprites are drawn by `tools/make-effects-demo.py`, which makes the
whole project from nothing.
""")
print("made", out, "with", len(SCENES), "scenes")
