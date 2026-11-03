"""The Controls scene pack: a screen where the player rebinds the controls,
made of the engine's own RebindList (a row per input command, built at run
time from the project's table) under a screen-fixed Layer, with a heading and
a Back button. Imported into any game through Scene ▸ Import a scene…, it
reads that game's own commands.

    python3 tools/make-rebind-scene.py [scenes/rebind]

A pack is a whole small project, so the templates test compiles it; the
editor copies everything but project.json and README.md into the game.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "scenes", "rebind")
d = Demo(out, ["scenes/singletons", "vscript"], "a2000000")
W, H = 960, 540

# ── the objects: a Type per thing a rule talks to ──
d.type_json("ControlsScreen", "Layer", {"parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
d.type_json("ControlsHeading", "Label", {"text": "Controls", "fontSize": 22})
d.type_json("ControlsHelp", "Label", {"text": "Change picks the next key, button or stick you give; Add keeps the old one too.", "fontSize": 12})
d.type_json("ControlsList", "RebindList", {"boxWidth": 560, "boxHeight": 330, "fontSize": 14, "labelWidth": 140, "addText": "Add"})
d.type_json("ControlsBack", "Button", {"text": "Back", "fontSize": 14, "boxWidth": 160, "boxHeight": 36})
d.type_json("ControlsLevel", "Node", {}, [{"componentClass": "ControlsRules"}])
d.type_json("ControlsScenes", "SceneManager", {})

# ── the scene ──
root = d.uid(2000)
objects = [{"id": root, "name": "Controls"}]
objects.append({"id": d.uid(2001), "parent": root, "name": "ControlsLevel1", "type": "ControlsLevel", "x": 0, "y": 0})
screen = d.uid(2002)
objects.append({"id": screen, "parent": root, "name": "ControlsScreen1", "type": "ControlsScreen", "x": 0, "y": 0})
def place(n, name, type_name, x, y, **extra):
    objects.append(dict({"id": d.uid(n), "parent": screen, "name": name, "type": type_name, "x": x, "y": y}, **extra))
place(2003, "ControlsHeading1", "ControlsHeading", 200, 40)
place(2004, "ControlsHelp1", "ControlsHelp", 200, 76)
place(2005, "ControlsList1", "ControlsList", 200, 110)
place(2006, "ControlsBack1", "ControlsBack", 200, 460)
d.scene("scenes/Controls.scene.json", objects)

# ── the rules: the list takes the focus, Back goes to the scene that opened this one ──
rules = [
    rule([once()], [line("ControlsList", "Control", "takeFocus")]),
    rule([line("ControlsBack", "Button", "onPressed")],
         [line("ControlsScenes", "SceneManager", "changeScene", value("ControlsScenes", "SceneManager", "previousScene"))]),
]
d.write("vscript/ControlsRules.vscript.json", {"rules": rules})

# ── the singleton with the Scene Manager, and the project ──
d.scene("scenes/singletons/ControlsSingletons.scene.json", [
    {"id": d.uid(3001), "name": "ControlsSingletons"},
    {"id": d.uid(3002), "parent": d.uid(3001), "name": "ControlsScenes1", "type": "ControlsScenes"},
])
def pad(code): return {"kind": "pad", "code": code}
def axis(code, sign): return {"kind": "axis", "code": code, "sign": sign}
d.write("project.json", {"schemaVersion": 2, "name": "Controls scene", "entryScene": "scenes/Controls.scene.json",
    "singletons": ["scenes/singletons/ControlsSingletons.scene.json"],
    "input": {
        "Left": {"bindings": [{"kind": "key", "code": 37}, {"kind": "key", "code": 65}, pad(14), axis(0, -1)]},
        "Right": {"bindings": [{"kind": "key", "code": 39}, {"kind": "key", "code": 68}, pad(15), axis(0, 1)]},
        "Jump": {"bindings": [{"kind": "key", "code": 32}, {"kind": "key", "code": 38}, pad(0)]},
        "Pause": {"bindings": [{"kind": "key", "code": 80}, pad(9)]},
    },
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True}})
d.write("README.md", """# Controls scene

A screen where the player rebinds the controls, ready to import into any
game: **Scene ▸ Import a scene…** in the editor, then open a way to it (a
button on your title screen whose rule changes the scene to `Controls`).

What it holds, as Object Types the game can restyle:

- **ControlsList**, on the engine's **RebindList**: a row per input command
  of the game it is in, read from the project's own table when the scene
  starts — the command's name, the inputs it has, **Change** (listen for the
  next input and put it in the old one's place) and **Add** (keep the old
  one too). A change is saved for next time; **Reset the controls** at the
  bottom goes back to the project's own table.
- **ControlsScreen**, a screen-fixed Layer, so the screen sits on the view
  whatever the camera does; **ControlsHeading** and **ControlsHelp**, Labels;
  **ControlsBack**, a Button whose rule changes to the scene that opened
  this one (`previousScene`), and **ControlsScenes**, the Scene Manager
  that rule uses, in a singleton scene.

Made by `tools/make-rebind-scene.py`.
""")
print("made %s" % out)
