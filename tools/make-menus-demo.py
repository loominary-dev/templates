"""The menus demo: a title screen, an options screen with a volume slider and
a rebind table, and a small game with a pause menu — every screen built from
the engine's own UI objects (Panel, Label, Button, Checkbox, Slider) under a
screen-fixed Layer, walked by Tab, the arrows or a pad, and driven by rules.

    python3 tools/make-menus-demo.py [demos/menus]

Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "menus")
d = Demo(out, ["scenes/singletons", "vscript"], "a1000000")
W, H = 960, 540

# ── art ──
def block(w, h, fill, edge):
    img = canvas(w, h)
    ImageDraw.Draw(img).rectangle([0, 0, w - 1, h - 1], fill=fill, outline=edge, width=2)
    return img

d.sprite("Hero", 24, 24, [("still", [block(24, 24, (90, 170, 255, 255), (30, 70, 140, 255))], 400, "loop")], [box("body", 12, 12, 24, 24)])
d.sprite("Floor", 640, 12, [("still", [block(640, 12, (96, 92, 84, 255), (60, 56, 50, 255))], 400, "loop")], [box("body", 320, 6, 640, 12)])
d.type_json("Hero", "Sprite", {"spriteKey": "Hero.sprite.json"})
d.type_json("Floor", "Sprite", {"spriteKey": "Floor.sprite.json"})

# ── the UI objects: a Type per thing a rule talks to, on the engine's own widgets ──
CARD = 0x24262c
BUTTONS = {
    "PlayButton": "Play", "OptionsButton": "Options", "QuitButton": "Quit", "BackButton": "Back", "ResetButton": "Reset the controls",
    "ResumeButton": "Resume", "PauseOptionsButton": "Options", "TitleButton": "Title screen",
    "JumpButton": "Change", "LeftButton": "Change", "RightButton": "Change",
}
for name, text in BUTTONS.items():
    d.type_json(name, "Button", {"text": text, "fontSize": 14, "boxWidth": 200 if not name.endswith(("JumpButton", "LeftButton", "RightButton")) else 100, "boxHeight": 36})
d.type_json("Heading", "Label", {"text": "", "fontSize": 22})
d.type_json("Caption", "Label", {"text": "", "fontSize": 14})
d.type_json("Help", "Label", {"text": "", "fontSize": 12})
for name in ["JumpName", "LeftName", "RightName", "VolumeValue", "Prompt"]:
    d.type_json(name, "Label", {"text": "", "fontSize": 14})
d.type_json("Card", "Panel", {"backgroundColor": CARD, "boxWidth": 300, "boxHeight": 320})
d.type_json("VolumeSlider", "Slider", {"min": 0, "max": 1, "value": 0.8, "boxWidth": 240, "boxHeight": 24})
d.type_json("RumbleBox", "Checkbox", {"text": "Rumble on a jump", "fontSize": 14, "boxWidth": 240, "boxHeight": 28})
d.type_json("Screen", "Layer", {"parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
d.type_json("PauseMenu", "Layer", {"parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False, "visible": False})
d.type_json("Scenes", "SceneManager", {})

seq = [0]
def scene(file, build, rules):
    """A scene whose root Type carries the sheet; `build(place)` places the objects, in game pixels under the Screen layer."""
    base = 2000 + len(SCENES) * 100
    root = d.uid(base)
    objects = [{"id": root, "name": file}]
    level = file + "Level"
    d.type_json(level, "Node", {}, [{"componentClass": file + "Rules"}])
    objects.append({"id": d.uid(base + 1), "parent": root, "name": level + "1", "type": level, "x": 0, "y": 0})
    def place(name, type_name, x, y, parent=None, **extra):
        seq[0] += 1
        oid = d.uid(base + 2 + seq[0])
        objects.append(dict({"id": oid, "parent": parent if parent is not None else root, "name": name, "type": type_name, "x": x, "y": y}, **extra))
        return oid
    build(place)
    d.scene("scenes/%s.scene.json" % file, objects)
    d.write("vscript/%sRules.vscript.json" % (file,), {"rules": rules})
    SCENES.append(file)
SCENES = []

def go(scene_file): return line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % scene_file))
# A rule that reads another Type's values needs that Type in scope: the source condition that picks all of it.
def pick_all(type_name): return {"scope": type_name, "name": "pickAll", "params": []}
# The comparison is the index of its option: <, ≤, =, ≠, ≥, >.
def compare(left, o, right): return line("maths", "Maths", "compare", left, lit(["=", "≠", "<", "≤", ">", "≥"].index(o)), right)
def pressed_btn(type_name): return line(type_name, "Button", "onPressed")
def focus(type_name): return line(type_name, "Control", "takeFocus")
WALK = "Tab, the arrows or a pad's D-pad move between the buttons; Enter, Space or the pad's bottom button press one."

# ── Title ──
def title(place):
    screen = place("Screen1", "Screen", 0, 0)
    place("Card1", "Card", 330, 100, parent=screen)
    place("Heading1", "Heading", 380, 120, parent=screen, text="Menus demo")
    place("Play1", "PlayButton", 380, 180, parent=screen)
    place("Options1", "OptionsButton", 380, 240, parent=screen)
    place("Quit1", "QuitButton", 380, 300, parent=screen)
    place("Walk1", "Help", 200, 460, parent=screen, text=WALK)
scene("Title", title, [
    rule([once()], [focus("PlayButton")]),
    rule([pressed_btn("PlayButton")], [go("Game")]),
    rule([pressed_btn("OptionsButton")], [go("Options")]),
    rule([pressed_btn("QuitButton")], [line("system", "System", "quitGame")]),
])

# ── Options: volume, rumble, and a rebind row per command ──
COMMANDS = [("Jump", "JumpName", "JumpButton"), ("Left", "LeftName", "LeftButton"), ("Right", "RightName", "RightButton")]
def options(place):
    screen = place("Screen1", "Screen", 0, 0)
    place("Card1", "Card", 250, 40, parent=screen, boxWidth=460, boxHeight=470)
    place("Heading1", "Heading", 300, 60, parent=screen, text="Options")
    place("VolumeLabel", "Caption", 300, 118, parent=screen, text="Volume")
    place("Volume1", "VolumeSlider", 400, 118, parent=screen)
    place("VolumeValue1", "VolumeValue", 660, 118, parent=screen)
    place("Rumble1", "RumbleBox", 400, 160, parent=screen)
    for k, (command, name_type, btn_type) in enumerate(COMMANDS):
        y = 220 + 44 * k
        place(command + "Label", "Caption", 300, y + 8, parent=screen, text=command)
        place(name_type + "1", name_type, 400, y + 8, parent=screen)
        place(btn_type + "1", btn_type, 600, y, parent=screen)
    place("Prompt1", "Prompt", 300, 360, parent=screen, text="Press a key, a mouse button or a pad button…", visible=False)
    place("Reset1", "ResetButton", 300, 400, parent=screen)
    place("Back1", "BackButton", 300, 450, parent=screen)
options_rules = [
    rule([once()], [focus("VolumeSlider")]),
    rule([pick_all("VolumeSlider")], [line("VolumeValue", "Label", "setNumber", value("VolumeSlider", "Slider", "sliderValue"))]),
    rule([sheet("everyTick")], [line(name_type, "Label", "setText", value("input", "Input", "commandBindingName", s(command), lit(0))) for command, name_type, _ in COMMANDS]),
    rule([line("VolumeSlider", "Slider", "onSliderChanged")], [line("audio", "Audio", "setMasterVolume", value("VolumeSlider", "Slider", "sliderValue"))]),
    rule([line("RumbleBox", "Checkbox", "onToggled"), line("RumbleBox", "Checkbox", "isChecked")], [line("input", "Input", "rumble", lit(0.6), lit(0.25))]),
]
for command, _, btn_type in COMMANDS:
    options_rules.append(rule([pressed_btn(btn_type)], [set_sheet_var("Command", s(command)), line("input", "Input", "listenForInput"), line("Prompt", "Node", "show")]))
options_rules += [
    rule([line("input", "Input", "hasCapturedInput")], [line("input", "Input", "bindCapturedTo", sheet_var("Command")), line("input", "Input", "saveBindings"), line("Prompt", "Node", "hide")]),
    rule([pressed_btn("ResetButton")], [line("input", "Input", "resetBindings")]),
    rule([pressed_btn("BackButton")], [go("Title")]),
]
scene("Options", options, options_rules)
d.write("vscript/OptionsRules.vscript.json", {"vars": [{"name": "Command", "type": "text", "value": "Jump"}], "rules": options_rules})

# ── Game: a block that walks and jumps, and a pause menu over it ──
FLOOR = 150
def game(place):
    place("Floor1", "Floor", 0, FLOOR + 18)
    place("Hero1", "Hero", 0, FLOOR)
    hud = place("Screen1", "Screen", 0, 0)
    place("Hint1", "Help", 20, 20, parent=hud, text="Left and Right (or A and D, or a pad) walk, Space (or the pad's bottom button) jumps, Escape (or Start) pauses.")
    menu = place("Pause1", "PauseMenu", 0, 0)
    place("Card1", "Card", 330, 130, parent=menu, boxHeight=260)
    place("Heading1", "Heading", 380, 150, parent=menu, text="Paused")
    place("Resume1", "ResumeButton", 380, 200, parent=menu)
    place("PauseOptions1", "PauseOptionsButton", 380, 260, parent=menu)
    place("Title1", "TitleButton", 380, 320, parent=menu)
hx, hy = value("Hero", "Node", "getPositionX"), value("Hero", "Node", "getPositionY")
running = compare(sheet_var("Paused"), "=", lit(0))
game_rules = [
    rule([pick_all("Hero"), held("Left"), running], [line("Hero", "Node", "setPositionX", op("-", hx, op("*", lit(240), dt())))]),
    rule([pick_all("Hero"), held("Right"), running], [line("Hero", "Node", "setPositionX", op("+", hx, op("*", lit(240), dt())))]),
    rule([pick_all("Hero"), pressed("Jump"), running, compare(hy, "≥", lit(FLOOR))], [set_sheet_var("Vy", lit(-460))]),
    rule([pick_all("Hero"), running], [line("Hero", "Node", "setPositionY", op("+", hy, op("*", sheet_var("Vy"), dt()))), add_sheet_var("Vy", op("*", lit(980), dt()))]),
    rule([pick_all("Hero"), compare(hy, ">", lit(FLOOR))], [line("Hero", "Node", "setPositionY", lit(FLOOR)), set_sheet_var("Vy", lit(0))]),
    rule([pressed("Pause"), running], [set_sheet_var("Paused", lit(1)), line("PauseMenu", "Node", "show"), focus("ResumeButton")]),
    rule([pressed_btn("ResumeButton")], [set_sheet_var("Paused", lit(0)), line("PauseMenu", "Node", "hide")]),
    rule([pressed("Pause"), compare(sheet_var("Paused"), "=", lit(1))], [set_sheet_var("Paused", lit(0)), line("PauseMenu", "Node", "hide")]),
    rule([pressed_btn("PauseOptionsButton")], [go("Options")]),
    rule([pressed_btn("TitleButton")], [go("Title")]),
]
scene("Game", game, game_rules)
d.write("vscript/GameRules.vscript.json", {"vars": [{"name": "Vy", "type": "number", "value": 0}, {"name": "Paused", "type": "number", "value": 0}], "rules": game_rules})

# ── the singleton with the Scene Manager, and the project ──
d.scene("scenes/singletons/Menus.scene.json", [
    {"id": d.uid(3001), "name": "Menus"},
    {"id": d.uid(3002), "parent": d.uid(3001), "name": "Scenes1", "type": "Scenes"},
])
def pad(code): return {"kind": "pad", "code": code}
def axis(code, sign): return {"kind": "axis", "code": code, "sign": sign}
d.write("project.json", {"schemaVersion": 2, "name": "Menus demo", "entryScene": "scenes/Title.scene.json",
    "singletons": ["scenes/singletons/Menus.scene.json"],
    "input": {
        "Left": {"bindings": [{"kind": "key", "code": 37}, {"kind": "key", "code": 65}, pad(14), axis(0, -1)]},
        "Right": {"bindings": [{"kind": "key", "code": 39}, {"kind": "key", "code": 68}, pad(15), axis(0, 1)]},
        "Jump": {"bindings": [{"kind": "key", "code": 32}, {"kind": "key", "code": 38}, pad(0)]},
        "Pause": {"bindings": [{"kind": "key", "code": 27}, pad(9)]},
    },
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "arcade", "gravity": 980}})
d.write("README.md", """# Menus demo

Three screens built from the engine's own UI objects — **Panel**, **Label**,
**Button**, **Checkbox** and **Slider** — placed under a screen-fixed
**Layer** so they sit on the view whatever the camera does, and driven by
rules on each scene's root Type:

- **Title**: Play, Options and Quit. Tab, the arrows or a pad's D-pad move the
  focus; Enter, Space or the pad's bottom button press.
- **Options**: a volume slider whose value a label follows, a checkbox that
  rumbles the pad, and a rebind row per command — *Change* listens for the
  next input, *An input was captured* binds it and saves the controls, and the
  labels show each command's first binding.
- **Game**: a block that walks and jumps; Escape or Start opens a pause menu
  over it, with Resume, Options and the title screen.

Made by `tools/make-menus-demo.py`.
""")
print("made %s with %d scenes" % (out, len(SCENES)))
