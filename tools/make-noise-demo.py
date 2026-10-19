"""The Noise world demo: a native library in a game. stb_perlin, Sean Barrett's
single-file C noise library (public domain or MIT), sits in
plugins/libraries/perlin as Loominary's header importer reads it; a Noise
behavior calls it and offers its numbers to rules; an island is grown from
it on a tile map, clouds drift over it, and a boat wanders by it. N grows a
new island, W turns the weather on and off.

    python3 tools/make-noise-demo.py <stb_perlin.h> <Loominary's CodegenCli> [demos/noise]

The CodegenCli (engine/bin-codegen in Loominary's repository) writes the glue and
the Haxe class from the header, as Build does before it compiles, so the
project opens with them in place; the library itself is built on the first
Run, with the editor's C++ compiler (Editor Settings ▸ Build toolchain).
Everything else is drawn here. Needs Pillow.
"""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

header, codegen = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "..", "demos", "noise")
d = Demo(out, ["scenes", "vscript", "assets/art", "assets/tiles", "plugins/behaviors", "plugins/objects", "plugins/libraries/perlin/native", "scripts"], "n1000000")
W, H = 640, 360
T = 16
# Rounded up: a part row is still drawn, so the foot of the view is not left bare.
COLS, ROWS = -(-W // T), -(-H // T)

# ── the library: the header as it comes, its manifest, and the glue and class the importer writes ──
shutil.copy(header, os.path.join(d.out, "plugins/libraries/perlin/native/stb_perlin.h"))
d.write("plugins/libraries/perlin/library.json", {
    "name": "perlin", "version": "0.5", "kind": "native", "source": "src", "license": "MIT or public domain (stb)",
    "homepage": "https://github.com/nothings/stb", "defines": [], "header": "native/stb_perlin.h",
    "build": {"sources": [], "include": [], "link": []}, "native": {}})
made = subprocess.run([codegen, "library", d.out, "perlin"], capture_output=True, text=True)
if made.returncode != 0: sys.exit("the codegen tool could not write the glue: " + made.stderr)
print("the glue exports", made.stdout.strip())
for keep in [".gitkeep"]:
    for folder in ["plugins/behaviors", "plugins/objects"]:
        open(os.path.join(d.out, folder, keep), "w").close()

# ── the terrain tiles: deep water, shallows, sand, grass, forest, rock, snow ──
COLOURS = [(28, 64, 128), (52, 112, 186), (226, 206, 140), (104, 168, 80), (52, 116, 58), (130, 128, 124), (240, 240, 244)]
sheet = canvas(T * len(COLOURS), T)
g = ImageDraw.Draw(sheet)
for i, (r, gg, bb) in enumerate(COLOURS):
    g.rectangle([i * T, 0, i * T + T - 1, T - 1], fill=(r, gg, bb, 255))
    # A little grain, so the ground reads as ground.
    for k in range(6):
        x, y = (k * 7 + i * 3) % T, (k * 5 + i * 11) % T
        shade = (max(0, r - 18), max(0, gg - 18), max(0, bb - 18), 255)
        g.point((i * T + x, y), fill=shade)
    if i == 4:
        for (x, y) in [(3, 4), (10, 2), (7, 10), (13, 12)]:
            g.ellipse([i * T + x - 2, y - 2, i * T + x + 2, y + 2], fill=(30, 80, 36, 255))
sheet.save(os.path.join(d.out, "assets/art/terrain.png"))
d.write("assets/tiles/Terrain.tileset.json", {"schemaVersion": 1, "image": "assets/art/terrain.png", "tileWidth": T, "tileHeight": T,
    "tiles": [{"id": i, "x": i * T, "y": 0, "collision": []} for i in range(len(COLOURS))]})

# ── pictures ──
d.sprite("Cloud", 32, 32, [("still", [soft_dot(32, (255, 255, 255), 1.2)], 400, "loop")], [])
boat = canvas(24, 12)
bg = ImageDraw.Draw(boat)
bg.polygon([(0, 2), (18, 2), (23, 6), (18, 10), (0, 10)], fill=(150, 90, 50, 255), outline=(90, 50, 25, 255))
bg.rectangle([6, 4, 12, 8], fill=(240, 236, 220, 255))
d.sprite("Boat", 24, 12, [("still", [boat], 400, "loop")], [])

# ── the behaviour that calls the library, and the two scripts that use it ──
d.write("plugins/behaviors/Noise.hx", '''/**
	Smooth random numbers from the perlin library (plugins/libraries/perlin,
	stb_perlin): the same place always gives the same number, and places near
	each other give numbers near each other. For terrain, clouds, wobble,
	wandering. Rules read it as values; scripts call it directly.

	@behavior
	@name Noise
	@category Generate
	@appliesTo Node
**/
class Noise extends Component {
	/** Which world: a different seed is a different pattern. */
	public var seed:Int = 1;

	/**
		How large the features are: smaller is broader.
		@range 0.001 1 0.005
	**/
	public var scale:Float = 0.08;

	/**
		How many layers of detail, each half the size of the last.
		@range 1 8 1
	**/
	public var octaves:Int = 4;

	/**
		@group Noise
		@linktext Height at {0}, {1}
		@description Fractal noise at a place, about -1 to 1: broad hills with smaller ones on them.
		@param x Across.
		@param y Down.
	**/
	@:value
	public function heightAt(x:Float, y:Float):Float
		return Perlin.stb_perlin_fbm_noise3(x * scale, y * scale, seed * 7.31, 2.0, 0.5, octaves);

	/**
		@group Noise
		@linktext Noise at {0}, {1}, {2}
		@description Plain noise at a place and a moment, about -1 to 1: give it the time to make it move.
		@param x Across.
		@param y Down.
		@param t The third axis: time, usually.
	**/
	@:value
	public function noiseAt(x:Float, y:Float, t:Float):Float
		return Perlin.stb_perlin_noise3_seed(x * scale, y * scale, t, 0, 0, 0, seed);

	/**
		@group Noise
		@linktext New seed
		@description A different pattern from now on.
		@ruletext Take a new seed
	**/
	@:action
	public function newSeed():Void seed = 1 + Std.random(100000);
}
''')
open(os.path.join(d.out, "plugins/behaviors/Noise.icon.svg"), "w").write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <!-- A wavy line over a wavy line: smooth randomness. -->
  <path d="M2 9c3-4 5 3 8-1s5-2 7 1 3 0 5-2" />
  <path d="M2 16c2-2 4 2 7-1s5 1 7 0 4-2 6-1" />
</svg>
''')
d.write("scripts/IslandMaker.hx", f'''/**
	Grows an island on the tile map it is on: the Noise behavior beside it
	gives a height for each cell, lower towards the edges so the sea goes
	round, and the height picks the tile: deep water, shallows, sand, grass,
	forest, rock, snow. Grow island makes a new one with a new seed.
**/
@:host(Tilemap)
class IslandMaker extends Component {{
	public var columns:Int = {COLS};
	public var rows:Int = {ROWS};

	override public function onReady():Void grow();

	/**
		@group Island
		@linktext Grow island
		@description Makes the island again from the Noise behavior's seed.
		@ruletext Grow the island
	**/
	@:action
	public function grow():Void {{
		var noise:Noise = node.getComponent(Noise);
		if (noise == null) return;
		var cells:Array<Array<Int>> = [];
		for (y in 0...rows) for (x in 0...columns) {{
			// Zero in the middle, about one at the edges: the sea comes in from there.
			var dx = (x + 0.5) / columns * 2 - 1, dy = (y + 0.5) / rows * 2 - 1;
			var edge = Math.sqrt(dx * dx + dy * dy);
			var h = noise.heightAt(x, y) * 0.9 + 0.45 - edge * edge * 0.95;
			cells.push([x, y, tileFor(h)]);
		}}
		tilemap.setCells(cells);
	}}

	static function tileFor(h:Float):Int {{
		return h < -0.12 ? 0 : h < 0.0 ? 1 : h < 0.06 ? 2 : h < 0.32 ? 3 : h < 0.56 ? 4 : h < 0.78 ? 5 : 6;
	}}
}}
''')
d.write("scripts/Weather.hx", f'''/**
	Clouds over the island: a grid of soft white dots, each as opaque as the
	Noise behavior says at its place and the moment, so the clouds drift and
	change shape. Weather on and off fades them in and out.
**/
class Weather extends Component {{
	public var speed:Float = 0.25;
	var clouds:Array<Node> = [];
	var t = 0.0;
	var amount = 1.0;
	var wanted = 1.0;

	override public function onReady():Void {{
		for (y in 0...{ROWS // 2 + 2}) for (x in 0...{COLS // 2 + 2}) {{
			var c = new Cloud("Cloud");
			c.x = {-W // 2} + x * 32;
			c.y = {-H // 2} + y * 32;
			c.scaleX = c.scaleY = 2.2;
			node.addChild(c);
			clouds.push(c);
		}}
	}}

	override public function update(dt:Float):Void {{
		var noise:Noise = node.getComponent(Noise);
		if (noise == null) return;
		t += dt * speed;
		amount += (wanted - amount) * Math.min(1, dt * 2);
		for (c in clouds) {{
			var n = noise.noiseAt(c.x + t * 30, c.y, t);
			c.opacity = Math.max(0, Math.min(0.85, (n - 0.05) * 2.2)) * amount;
		}}
	}}

	/**
		@group Weather
		@linktext Set weather {{0}}
		@description Fades the clouds in or out.
		@ruletext Set weather {{0}}
		@param on On or off.
	**/
	@:action
	public function setWeather(on:Bool):Void wanted = on ? 1 : 0;

	/**
		@group Weather
		@linktext Switch the weather
		@description Clouds if there are none, none if there are.
		@ruletext Switch the weather
	**/
	@:action
	public function toggle():Void wanted = wanted > 0.5 ? 0 : 1;

	/**
		@group Weather
		@linktext Weather is on
		@description True while the clouds are wanted.
		@ruletext Weather is on
	**/
	@:condition
	public function isOn():Bool return wanted > 0.5;
}}
''')

# ── Types ──
d.type_json("Island", "Tilemap", {}, [{"componentClass": "Noise", "scale": 0.11, "octaves": 5}, {"componentClass": "IslandMaker"}])
d.type_json("Sky", "Node", {}, [{"componentClass": "Noise", "scale": 0.012, "seed": 3}, {"componentClass": "Weather"}])
d.type_json("Cloud", "Sprite", {"spriteKey": "Cloud.sprite.json", "collisionEnabled": False})
d.type_json("Boat", "Sprite", {"spriteKey": "Boat.sprite.json", "collisionEnabled": False}, [{"componentClass": "Noise", "scale": 1, "seed": 9}, {"componentClass": "BoatRules"}])
d.type_json("Level", "Node", {}, [{"componentClass": "LevelRules"}])
d.type_json("Help", "Label", {"text": "", "fontSize": 11})

# ── the scene ──
objects = [{"id": d.uid(1), "name": "World"},
    {"id": d.uid(2), "parent": d.uid(1), "name": "Level1", "type": "Level"},
    {"id": d.uid(3), "parent": d.uid(1), "name": "Island1", "type": "Island", "tilesetKey": "assets/tiles/Terrain.tileset.json",
     "x": -W // 2, "y": -H // 2, "cellWidth": T, "cellHeight": T, "cells": []},
    {"id": d.uid(4), "parent": d.uid(1), "name": "Boat1", "type": "Boat", "x": -250, "y": 140},
    {"id": d.uid(5), "parent": d.uid(1), "name": "Sky1", "type": "Sky", "x": 0, "y": 0},
    {"id": d.uid(6), "parent": d.uid(1), "name": "Help1", "type": "Help", "x": -W // 2 + 6, "y": -H // 2 + 4,
     "text": "N: a new island   W: the weather"}]
d.scene("scenes/World.scene.json", objects)

# ── rules ──
t = value("system", "System", "getElapsedTime")
d.write("vscript/BoatRules.vscript.json", {"rules": [
    # The heading wanders by the boat's own Noise, read at the moment; the boat keeps to the screen.
    # It bobs by the library's own tile, Perlin, with no behavior between: the words a native library's functions become.
    rule([], [line("self", "Node", "setScaleXY", op("+", lit(1), op("*", value("lib:PerlinWords", "PerlinWords", "noise3", op("*", t, lit(0.7)), lit(9), lit(0), lit(0), lit(0), lit(0)), lit(0.15))))]),
    rule([], [line("self", "Node", "setRotation", op("*", cvalue("self", "Noise", "noiseAt", lit(0), lit(0), op("*", t, lit(0.2))), lit(540))),
              line("self", "Node", "moveAtAngle", op("*", lit(26), dt()), value("self", "Node", "getRotation"))]),
    rule([line("self", "Node", "comparePositionX", lit(OBJ_GT), lit(W // 2 + 12))], [line("self", "Node", "setPositionX", lit(-W // 2 - 12))]),
    rule([line("self", "Node", "comparePositionX", lit(OBJ_LT), lit(-W // 2 - 12))], [line("self", "Node", "setPositionX", lit(W // 2 + 12))]),
    rule([line("self", "Node", "comparePositionY", lit(OBJ_GT), lit(H // 2 + 12))], [line("self", "Node", "setPositionY", lit(-H // 2 - 12))]),
    rule([line("self", "Node", "comparePositionY", lit(OBJ_LT), lit(-H // 2 - 12))], [line("self", "Node", "setPositionY", lit(H // 2 + 12))]),
]})
d.write("vscript/LevelRules.vscript.json", {"rules": [
    rule([pressed("New island")], [comp("Island", "Noise", "newSeed"), comp("Island", "IslandMaker", "grow")]),
    rule([pressed("Weather")], [comp("Sky", "Weather", "toggle")]),
]})

d.write("project.json", {"schemaVersion": 2, "name": "Noise world", "entryScene": "scenes/World.scene.json",
    "input": {"New island": keys(78), "Weather": keys(87)},
    "display": {"width": W, "height": H, "windowWidth": W * 2, "windowHeight": H * 2, "presentMode": "fit", "displayMode": "windowed", "autoResize": True, "wholeWindowScale": True},
    "physics": {"engine": "arcade", "gravity": 0}})
d.write("README.md", """# Noise world

A native library in a game. `plugins/libraries/perlin` holds
[stb_perlin](https://github.com/nothings/stb), Sean Barrett's single-file C
noise library, exactly as it comes: Loominary's header importer reads its
functions, writes the glue and the Haxe class `Perlin`, and builds it on the
first Run with your C++ compiler (Editor Settings ▸ Build toolchain).

- The **Noise** behavior (`plugins/behaviors/Noise.hx`) calls
  `Perlin.stb_perlin_fbm_noise3` and `stb_perlin_noise3_seed`, and offers
  **Height at** and **Noise at** to rules.
- **IslandMaker** (`scripts/`) grows the island on the tile map from the
  heights: deep water to snow. **N** takes a new seed and grows another.
- **Weather** drifts clouds over it, each as thick as the noise says at its
  place and the moment. **W** fades them out and in.
- The boat's heading wanders by its own Noise, read in `vscript/BoatRules`,
  and it bobs by the library's own **Perlin** tile in the rule picker
  (`plugins/libraries/perlin/src/PerlinWords.hx`, written by the header
  importer): **noise3** called straight from the sheet, no behavior between.

Open Project Settings ▸ Libraries to see the library and build it again.

Generated by `tools/make-noise-demo.py`; stb_perlin is MIT or public domain,
its license at the end of its header.
""")
print("wrote", d.out)
