"""The dialogue demo: a conversation written in a Yarn file and shown by rules
in a box of the engine's own UI objects — a portrait, the speaker's name, the
line, and a button per choice — with commands that change the portrait and
hand over gold, and a line that remembers whether you have talked before.

    python3 tools/make-dialogue-demo.py [demos/dialogue]

Needs Pillow.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_kit import *

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "demos", "dialogue")
d = Demo(out, ["scenes", "vscript"], "a2000000")
W, H = 960, 540

# ── art: a guard's face, calm and cross ──
def face(cross):
    img = canvas(96, 96)
    g = ImageDraw.Draw(img)
    g.rounded_rectangle([8, 8, 87, 87], radius=18, fill=(214, 170, 130, 255), outline=(120, 80, 50, 255), width=3)
    g.rectangle([8, 8, 87, 30], fill=(90, 90, 100, 255))  # the helmet
    g.rectangle([14, 30, 81, 34], fill=(60, 60, 70, 255))
    if cross:
        g.line([26, 44, 40, 50], fill=(60, 30, 20, 255), width=4)
        g.line([70, 44, 56, 50], fill=(60, 30, 20, 255), width=4)
        g.arc([32, 62, 64, 84], 200, 340, fill=(90, 40, 30, 255), width=4)
    else:
        g.ellipse([28, 44, 40, 56], fill=(40, 30, 30, 255))
        g.ellipse([56, 44, 68, 56], fill=(40, 30, 30, 255))
        g.arc([32, 56, 64, 78], 20, 160, fill=(90, 40, 30, 255), width=4)
    return img

d.sprite("Portrait", 96, 96, [("calm", [face(False)], 400, "loop"), ("cross", [face(True)], 400, "loop")], [])
d.type_json("Portrait", "Sprite", {"spriteKey": "Portrait.sprite.json"})

# ── the box: a Type per thing a rule talks to ──
CARD = 0x24262c
d.type_json("Screen", "Layer", {"parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
d.type_json("Box", "Panel", {"backgroundColor": CARD, "boxWidth": 760, "boxHeight": 200})
d.type_json("Speaker", "Label", {"text": "", "fontSize": 16})
d.type_json("Speech", "Label", {"text": "", "fontSize": 15, "boxWidth": 600, "boxHeight": 70, "wrapMode": "Word"})
for k in range(4):
    d.type_json("Choice%d" % (k + 1), "Button", {"text": "", "fontSize": 14, "boxWidth": 600, "boxHeight": 30, "visible": False})
d.type_json("Hint", "Label", {"text": "", "fontSize": 12})
d.type_json("Purse", "Label", {"text": "", "fontSize": 14})
d.type_json("PurseValue", "Label", {"text": "0", "fontSize": 14})
d.type_json("Talk", "Node", {}, [{"componentClass": "TalkRules"}])

# ── the conversation ──
d.write("guard.yarn", """title: Guard
tags: gate
---
<<declare $gold = 0>>
<<declare $angered = false>>
<<if visited("Guard")>>
Guard: You again. The gate is still shut.
<<else>>
Guard: Halt! Who goes there?
<<endif>>
-> A friend.
    Guard: I know no friend of yours. State your business.
    <<jump Business>>
-> A foe! <<if not $angered>>
    <<portrait cross>>
    Guard: Then you shall not pass.
    <<set $angered to true>>
    <<jump Shut>>
-> Someone with gold. <<if $gold >= 5>>
    Guard: Gold opens every gate. Pass, friend.
    <<set $gold -= 5>>
    <<give -5>>
    <<jump Open>>
-> Never mind.
    Guard: Then be off with you.
===

title: Business
---
Guard: And what would that be?
-> Delivering a letter.
    Guard: A letter? Hand it over, then.
    <<portrait calm>>
    Guard: Hm. It says to give the bearer five gold. Here.
    <<set $gold += 5>>
    <<give 5>>
    Guard: Now, about that gate…
    <<jump Guard>>
-> Sightseeing.
    Guard: There is nothing to see. Go home.
===

title: Shut
---
The gate stays shut.
<<portrait calm>>
Guard: Come back when you have manners. Or gold.
===

title: Open
---
The gate swings open.
Guard: Mind the step.
===
""")

# ── the scene and its rules ──
root = d.uid(2000)
objects = [{"id": root, "name": "Talk"}, {"id": d.uid(2001), "parent": root, "name": "Talk1", "type": "Talk", "x": 0, "y": 0}]
seq = [1]
def place(name, type_name, x, y, parent=None, **extra):
    seq[0] += 1
    oid = d.uid(2000 + seq[0])
    objects.append(dict({"id": oid, "parent": parent if parent is not None else root, "name": name, "type": type_name, "x": x, "y": y}, **extra))
    return oid
screen = place("Screen1", "Screen", 0, 0)
place("Purse1", "Purse", 20, 20, parent=screen, text="Gold:")
place("PurseValue1", "PurseValue", 70, 20, parent=screen)
place("Box1", "Box", 100, 320, parent=screen)
place("Portrait1", "Portrait", 164, 420, parent=screen)
place("Speaker1", "Speaker", 240, 336, parent=screen)
place("Speech1", "Speech", 240, 364, parent=screen)
for k in range(4):
    place("Choice%d_1" % (k + 1), "Choice%d" % (k + 1), 240, 364 + k * 34, parent=screen)
place("Hint1", "Hint", 100, 522, parent=screen, text="Enter, Space or the pad's bottom button go on; the arrows or Tab and Enter choose.")
d.scene("scenes/Talk.scene.json", objects)

def dlg(name, *params): return line("dialogue", "Dialogue", name, *params)
def dval(name, *params, **k): return value("dialogue", "Dialogue", name, *params, **k)
def choice(k): return "Choice%d" % (k + 1)
def show(t): return line(t, "Node", "show")
def hide(t): return line(t, "Node", "hide")
def focus(t): return line(t, "Control", "takeFocus")
hide_all = [hide(choice(k)) for k in range(4)]
rules = [
    rule([once()], [dlg("start", s("Guard"))] + hide_all),
    # Over: Continue starts it again, remembering. Before the rule that goes on,
    # and marked fresh, so one press neither ends it and starts it again nor
    # starts it and skips its first line.
    rule([pressed("Continue"), not_(dlg("isRunning"))], [dlg("start", s("Guard")), set_sheet_var("Fresh", lit(1))]),
    # A line: who says it, and what. The choices go until options come.
    rule([dlg("onLine")], [line("Speaker", "Label", "setText", dval("lineSpeaker", returnType="String")), line("Speech", "Label", "setText", dval("lineText", returnType="String"))] + hide_all),
    rule([pressed("Continue"), dlg("isRunning"), not_(dlg("isWaitingForChoice")), compare(sheet_var("Fresh"), EQ, lit(0))], [dlg("continueConversation")]),
    # Options: a button per choice, the first focused.
    rule([dlg("onOptions")], [line("Speech", "Label", "setText", s(""))] + hide_all),
]
for k in range(4):
    rules.append(rule([dlg("onOptions"), compare(dval("optionCount"), GT, lit(k))],
        [show(choice(k)), line(choice(k), "Label", "setText", dval("optionText", lit(k), returnType="String"))],
        # One the file's <<if>> shuts is shown greyed.
        [rule([dlg("isOptionAvailable", lit(k))], [line(choice(k), "Button", "setDisabled", b(False))]),
         rule([not_(dlg("isOptionAvailable", lit(k)))], [line(choice(k), "Button", "setDisabled", b(True))])]))
    rules.append(rule([line(choice(k), "Button", "onPressed")], [dlg("choose", lit(k))]))
rules += [
    rule([dlg("onOptions")], [focus("Choice1")]),
    # The file's commands: the portrait's mood, and gold handed over.
    rule([dlg("onCommand", s("portrait"))], [line("Portrait", "Sprite", "setAnimation", dval("commandArg", lit(0), returnType="String"))]),
    # The purse shows the file's own $gold, which the give command says has changed.
    rule([dlg("onCommand", s("give"))], [line("PurseValue", "Label", "setNumber", dval("number", s("gold")))]),
    # Over: the box says so, and Continue starts it again, remembering.
    rule([dlg("onEnded")], [line("Speaker", "Label", "setText", s("")), line("Speech", "Label", "setText", s("(The guard turns away. Press Continue to talk again.)"))] + hide_all),
    rule([], [set_sheet_var("Fresh", lit(0))]),
]
d.write("vscript/TalkRules.vscript.json", {"vars": [{"name": "Fresh", "type": "number", "value": 0}], "rules": rules})

def pad(code): return {"kind": "pad", "code": code}
d.write("project.json", {"schemaVersion": 2, "name": "Dialogue demo", "entryScene": "scenes/Talk.scene.json",
    "dialogue": {"files": ["guard.yarn"]},
    "input": {
        "Continue": {"bindings": [{"kind": "key", "code": 13}, {"kind": "key", "code": 32}, pad(0)]},
    },
    "display": {"width": W, "height": H, "windowWidth": W, "windowHeight": H, "presentMode": "fit", "displayMode": "windowed", "autoResize": True},
    "physics": {"engine": "none"}})
d.write("README.md", """# Dialogue demo

A conversation with a gate guard, written in `guard.yarn` (the Yarn
language) and shown by rules in a box of the engine's own UI objects: a
portrait, the speaker's name, the line, and a button per choice.

- **On line** puts the speaker and the words in the box; **Continue** goes on.
- **On options** shows a button per choice (**optionCount**, **optionText**),
  and each button's **On pressed** is **Choose option**.
- The file's commands do things in the game: `<<portrait cross>>` plays the
  portrait's animation, `<<give 5>>` tells the purse to show the file's `$gold`.
- The guard remembers: `visited("Guard")` changes his greeting the second
  time, and a choice with `<<if $gold >= 5>>` opens the gate only once you
  have the gold.

Open `guard.yarn` on the Dialogue page to see the nodes as a map and try the
conversation without running the game.

Made by `tools/make-dialogue-demo.py`.
""")
print("made %s" % out)
