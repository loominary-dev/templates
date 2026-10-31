"""The Two players demo: the Platformer demo for two on one keyboard, or a
keyboard and a pad, each with their own half of the screen. Made from the
generated Platformer demo rather than from Kenney's packs, so it follows that
demo when it changes.

    python3 tools/make-duo-demo.py [demos/platformer] [demos/duo]

What changes: two control sets (WASD on the left of the keyboard, the arrows
on the right) and a third for a pad; two players in Project Settings ▸ Players;
a second Player in the level, tinted, with Player 2 set; every input condition
asks for the object's own player, and every rule acts on the Player running it
rather than on every Player; two cameras, one for each half.
"""
import json, os, shutil, sys

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "demos", "platformer"))
out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "demos", "duo"))
shutil.rmtree(out, ignore_errors=True)
# The demo's own files only: what the editor generates or keeps for this machine is made again.
generated = {".loominary", ".loominary-undo", ".vscode", "typeTextures.json"}
def keep(d, names):
    return [n for n in names if n in generated or n.endswith(".hx") or n.endswith(".log")]
shutil.copytree(src, out, ignore=keep)

def read(rel):
    with open(os.path.join(out, rel)) as f: return json.load(f)
def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

# ── the controls: one table, three control sets ──
LEFT, RIGHT, PAD = "Left keys", "Right keys", "Pad"
def key(code, set_=None):
    b = {"kind": "key", "code": code}
    if set_: b["set"] = set_
    return b
def pad(code): return {"kind": "pad", "code": code, "set": PAD}
def stick(axis, sign): return {"kind": "axis", "code": axis, "sign": sign, "set": PAD}
A, D, S, W, SPACE = 65, 68, 83, 87, 32
LEFT_ARROW, UP_ARROW, RIGHT_ARROW, DOWN_ARROW, ENTER = 37, 38, 39, 40, 13
DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT, PAD_BOTTOM, PAD_START = 13, 14, 15, 0, 9
INPUT = {
    # The first set is written as none: WASD, Space too for Jump.
    "Move Left": {"bindings": [key(A), key(LEFT_ARROW, RIGHT), stick(0, -1), pad(DPAD_LEFT)]},
    "Move Right": {"bindings": [key(D), key(RIGHT_ARROW, RIGHT), stick(0, 1), pad(DPAD_RIGHT)]},
    "Move Down": {"bindings": [key(S), key(DOWN_ARROW, RIGHT), stick(1, 1), pad(DPAD_DOWN)]},
    "Jump": {"bindings": [key(W), key(SPACE), key(UP_ARROW, RIGHT), pad(PAD_BOTTOM)]},
    "Accept": {"bindings": [key(ENTER), key(SPACE)]},
    "Cancel": {"bindings": [key(27)]},
    "Pause": {"bindings": [key(80), pad(PAD_START)]},
}
project = read("project.json")
project["name"] = "Two players demo"
project["input"] = INPUT
project["players"] = {"count": 2, "sets": [LEFT, RIGHT, PAD], "seats": [{"controls": LEFT}, {"controls": RIGHT}]}
write("project.json", project)

# ── the level: a second player and a camera for each half ──
scene = read("scenes/Level.scene.json")
objects = scene["objects"]
by_name = {o["name"]: o for o in objects}
p1, cam1 = by_name["Player1"], by_name["Camera1"]
p1["player"] = 1
p2 = dict(p1, id="e0000000-0000-4000-8000-000000000901", name="Player2", x=p1["x"] + 20, player=2, tint=0xFFB4A0)
cam1["viewport"] = "Left half"
cam2 = dict(cam1, id="e0000000-0000-4000-8000-000000000902", name="Camera2", target="Player2", viewport="Right half", currentAtStart=False)
at = objects.index(cam1)
objects[at:at + 1] = [p2, cam1, cam2]
write("scenes/Level.scene.json", scene)

# ── the rules: each Player reads its own player's commands ──
rules = read("vscript/PlayerRules.vscript.json")
mine = {"type": "value", "scope": "self", "className": "Node", "name": "getPlayer", "params": [], "returnType": "Int"}
def own(c):
    if c.get("className") == "Input" and c.get("name") == "isCommandOn":
        c["name"] = "isPlayerCommandOn"
        c["params"] = c["params"] + [mine]
    return c
def selfward(x):
    # "Player" is every Player in the level; each Player's own sheet acts on itself.
    if isinstance(x, dict):
        if x.get("scope") == "Player": x["scope"] = "self:Player"
        for v in x.values(): selfward(v)
    elif isinstance(x, list):
        for v in x: selfward(v)
def walk(rs):
    for r in rs:
        r["conditions"] = [own(c) for c in r["conditions"]]
        walk(r.get("subRules", []))
selfward(rules["rules"])
walk(rules["rules"])
write("vscript/PlayerRules.vscript.json", rules)

write("README.md", """# Two players demo

The Platformer demo for two, side by side: the left half of the screen
follows the first player, the right half the second.

- Player 1 plays with **W A S D** (Space jumps too).
- Player 2 plays with the **arrow keys**.
- For a pad, set Player 2's controls to **Pad** in Project Settings ▸ Players.

The controls are one table with three **control sets** (Project Settings ▸
Input commands…): Left keys, Right keys and Pad. Each player holds one. Both
Players are one Type with one set of rules: each rule asks **Player
Self.player: input command … is on**, and each Player in the level has its own
**Player** number in the Inspector. Two **Cameras**, each on half of the
screen (Viewport: Left half and Right half), follow one player each.

Art and sounds by [Kenney](https://kenney.nl) (Pixel Platformer, Digital
Audio, Impact Sounds), CC0. Generated by `tools/make-duo-demo.py` from the
Platformer demo.
""")
print("wrote", out)
