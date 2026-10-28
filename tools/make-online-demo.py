"""The Online demo: the Two players demo played in two games, through a relay
(docs/multiplayer.md in the Loominary repository). Made from the generated
Two players demo, so it follows that demo when it changes.

    python3 tools/make-online-demo.py [demos/duo] [demos/online]

Three scenes, the way an online game usually goes:

- Title: a name, then Host a game (a private room, joined by its code), Play
  online (any public room of this game, or a new one), or Join by code. A game
  opened by an invite link joins that room by itself.
- Waiting room: who is in the room and whether they are ready; Ready, Copy
  invite, Leave, and Start for the host once everyone is ready.
- Level: the Two players level, each Player Synced and owned by its own
  player's game, the camera following this game's player.
"""
import json, os, shutil, sys

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "demos", "duo"))
out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "demos", "online"))
shutil.rmtree(out, ignore_errors=True)
generated = {".loominary", ".loominary-undo", ".vscode", "typeTextures.json"}
def keep(d, names):
    return [n for n in names if n in generated or n.endswith(".hx") or n.endswith(".log")]
shutil.copytree(src, out, ignore=keep)
os.makedirs(os.path.join(out, "scenes", "singletons"), exist_ok=True)

def read(rel):
    with open(os.path.join(out, rel)) as f: return json.load(f)
def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)
def type_json(name, base, defaults, components=()):
    write(name + ".type.json", {"schemaVersion": 2, "baseClass": base, "defaults": defaults, "components": [{"componentClass": c} for c in components]})

# ── rule pieces ──
def lit(v, kind=None):
    p = {"type": "literal", "value": v}
    if kind: p["valueKind"] = kind
    return p
def s(v): return lit(v, "string")
def b(v): return lit(v, "bool")
def op(o, left, right): return {"type": "op", "op": o, "left": left, "right": right}
def line(scope, cls, name, *params, **k): return dict({"scope": scope, "className": cls, "name": name, "params": list(params)}, **k)
def not_(c): return dict(c, **{"not": True})
def online(name, *params, **k): return line("online", "Online", name, *params, **k)
def value(scope, cls, name, *params, rt="String"): return {"type": "value", "scope": scope, "className": cls, "name": name, "params": list(params), "returnType": rt}
def ov(name, *params, rt="String"): return value("online", "Online", name, *params, rt=rt)
def once(): return line("system", "VisualScriptComponent", "triggerOnce")
def every(): return line("system", "VisualScriptComponent", "everyTick")
def rule(conditions, actions): return {"conditions": conditions, "actions": actions, "subRules": []}
def say(type_name, text): return line(type_name, "Label", "setText", text)
def pressed(type_name): return line(type_name, "Button", "onPressed")
def go(scene): return line("Scenes", "SceneManager", "changeScene", s("scenes/%s.scene.json" % scene))
def compare(left, o, right): return line("maths", "Maths", "compare", left, lit(["=", "≠", "<", "≤", ">", "≥"].index(o)), right)
def text_is(left, o, right): return line("maths", "Maths", "compareText", left, lit(["=", "≠", "contains"].index(o)), right)
def sheet_var(name): return value("system", "VisualScriptComponent", "sheetVar", s(name), rt="Float")
def set_sheet_var(name, v): return line("system", "VisualScriptComponent", "setSheetVar", s(name), v)
def field(type_name): return value(type_name, "TextField", "fieldText")
# A rule that reads another Type's values needs that Type in scope: the source condition that picks all of it.
def pick_all(type_name): return {"scope": type_name, "name": "pickAll", "params": []}
def show(type_name): return line(type_name, "Node", "show")
def hide(type_name): return line(type_name, "Node", "hide")

# The relay Run with players started, else one on this computer's port 8765 (node scripts/relay.mjs).
RELAY = ov("relayAddress", s("ws://127.0.0.1:8765"))

# ── the screens' objects: a Type per thing a rule talks to ──
SKY = 0x2b3a55
type_json("Screen", "Layer", {"parallaxX": 0, "parallaxY": 0, "zoomWithCamera": False})
type_json("Backdrop", "Panel", {"backgroundColor": SKY, "boxWidth": 320, "boxHeight": 180})
type_json("Heading", "Label", {"text": "", "fontSize": 14})
type_json("Caption", "Label", {"text": "", "fontSize": 8})
for name in ["Status", "Row1Name", "Row1Ready", "Row2Name", "Row2Ready"]:
    type_json(name, "Label", {"text": "", "fontSize": 8})
BUTTONS = {"HostButton": ("Host a game", 120), "QuickButton": ("Play online", 120), "JoinButton": ("Join", 52),
           "ReadyButton": ("Ready", 86), "StartButton": ("Start", 86), "InviteButton": ("Copy invite", 86), "LeaveButton": ("Leave", 86)}
for name, (text, w) in BUTTONS.items():
    type_json(name, "Button", {"text": text, "fontSize": 8, "boxWidth": w, "boxHeight": 16})
type_json("NameField", "TextField", {"text": "", "placeholder": "Your name", "fontSize": 8, "boxWidth": 120, "boxHeight": 16})
type_json("CodeField", "TextField", {"text": "", "placeholder": "Code", "fontSize": 8, "boxWidth": 64, "boxHeight": 16})
type_json("Scenes", "SceneManager", {})

def screen_scene(name, base, place_all, rules, vars=()):
    """A scene of screen-fixed UI, its rules on the scene's root Type."""
    root = "e0000000-0000-4000-8000-%012d" % base
    objects = [{"id": root, "name": name}]
    type_json(name + "Screen", "Node", {}, [name + "Rules"])
    objects.append({"id": "e0000000-0000-4000-8000-%012d" % (base + 1), "parent": root, "name": name + "Screen1", "type": name + "Screen", "x": 0, "y": 0})
    layer = "e0000000-0000-4000-8000-%012d" % (base + 2)
    objects.append({"id": layer, "parent": root, "name": "Screen1", "type": "Screen", "x": 0, "y": 0})
    n = [base + 3]
    def place(obj_name, type_name, x, y, **extra):
        objects.append(dict({"id": "e0000000-0000-4000-8000-%012d" % n[0], "parent": layer, "name": obj_name, "type": type_name, "x": x, "y": y}, **extra))
        n[0] += 1
    place("Backdrop1", "Backdrop", 0, 0)
    place_all(place)
    write("scenes/%s.scene.json" % name, {"schemaVersion": 2, "objects": objects})
    write("vscript/%sRules.vscript.json" % name, {"rules": rules, "vars": list(vars)})

# ── Title ──
def title(place):
    place("Heading1", "Heading", 20, 12, text="Online demo")
    place("NameLabel", "Caption", 20, 44, text="Name")
    place("Name1", "NameField", 100, 40)
    place("Host1", "HostButton", 100, 64)
    place("Quick1", "QuickButton", 100, 86)
    place("Code1", "CodeField", 100, 108)
    place("Join1", "JoinButton", 168, 108)
    place("Status1", "Status", 20, 150)
named = lambda: online("setMyName", field("NameField"))
screen_scene("Title", 1000, title, [
    rule([once(), not_(online("isConnected"))], [online("connect", RELAY), say("Status", s("Connecting to the relay..."))]),
    rule([once(), online("isConnected")], [say("Status", s("Host a game, play online, or join by code."))]),
    rule([online("onConnected")], [say("Status", s("Host a game, play online, or join by code."))]),
    # Opened by an invite link: straight into that room.
    rule([online("onConnected"), text_is(ov("roomFromLink"), "≠", s(""))], [online("joinRoom", ov("roomFromLink"))]),
    rule([pressed("HostButton"), pick_all("NameField")], [named(), set_sheet_var("Quick", lit(0)), online("createRoom", lit(2), b(False))]),
    rule([pressed("QuickButton"), pick_all("NameField")], [named(), set_sheet_var("Quick", lit(1)), online("joinAnyRoom"), say("Status", s("Looking for a room..."))]),
    rule([pressed("JoinButton"), pick_all("NameField"), pick_all("CodeField")], [named(), set_sheet_var("Quick", lit(0)), online("joinRoom", field("CodeField"))]),
    rule([online("onJoinFailed"), online("isConnected"), compare(sheet_var("Quick"), "=", lit(1))],
         [set_sheet_var("Quick", lit(0)), online("createRoom", lit(2), b(True))]),
    rule([online("onJoinFailed"), compare(sheet_var("Quick"), "=", lit(0))], [say("Status", ov("joinFailure"))]),
    rule([online("onDisconnected")], [say("Status", op("+", s("Not connected: "), ov("connectionError")))]),
    rule([online("onJoinedRoom")], [go("Lobby")]),
], vars=[{"name": "Quick", "type": "number", "value": 0}])

# ── Waiting room ──
def lobby(place):
    place("Heading1", "Heading", 20, 10)
    place("Hint1", "Caption", 20, 30, text="Give the other player the code, or an invite.")
    place("Row1Name1", "Row1Name", 30, 52)
    place("Row1Ready1", "Row1Ready", 200, 52)
    place("Row2Name1", "Row2Name", 30, 68)
    place("Row2Ready1", "Row2Ready", 200, 68)
    place("Ready1", "ReadyButton", 20, 96)
    place("Start1", "StartButton", 116, 96)
    place("Invite1", "InviteButton", 212, 96)
    place("Leave1", "LeaveButton", 20, 120)
    place("Status1", "Status", 20, 150)
first, second = ov("roomPlayerAt", lit(0), rt="Int"), ov("roomPlayerAt", lit(1), rt="Int")
me = ov("myPlayer", rt="Int")
everyone = [online("allPlayersReady"), compare(ov("playersInRoom", rt="Int"), "≥", lit(2))]
screen_scene("Lobby", 2000, lobby, [
    rule([every()], [say("Heading", op("+", s("Room "), ov("roomCode"))), say("Row1Name", ov("playerName", first))]),
    rule([online("isPlayerReady", first)], [say("Row1Ready", s("Ready"))]),
    rule([not_(online("isPlayerReady", first))], [say("Row1Ready", s("Not ready"))]),
    rule([online("isPlayerInRoom", second)], [say("Row2Name", ov("playerName", second))]),
    rule([online("isPlayerInRoom", second), online("isPlayerReady", second)], [say("Row2Ready", s("Ready"))]),
    rule([online("isPlayerInRoom", second), not_(online("isPlayerReady", second))], [say("Row2Ready", s("Not ready"))]),
    rule([not_(online("isPlayerInRoom", second))], [say("Row2Name", s("Waiting for a player...")), say("Row2Ready", s(""))]),
    # Ready turns on and off; the button says what pressing it does.
    rule([online("isPlayerReady", me)], [say("ReadyButton", s("Not ready"))]),
    rule([not_(online("isPlayerReady", me))], [say("ReadyButton", s("Ready"))]),
    rule([pressed("ReadyButton")], [set_sheet_var("Toggle", lit(1))]),
    rule([compare(sheet_var("Toggle"), "=", lit(1)), not_(online("isPlayerReady", me))], [online("setReady", b(True)), set_sheet_var("Toggle", lit(0))]),
    rule([compare(sheet_var("Toggle"), "=", lit(1)), online("isPlayerReady", me)], [online("setReady", b(False)), set_sheet_var("Toggle", lit(0))]),
    # Only the host starts, once everyone is ready.
    rule([online("isHost")], [show("StartButton")]),
    rule([not_(online("isHost"))], [hide("StartButton")]),
    rule([not_(online("allPlayersReady"))], [line("StartButton", "Button", "setDisabled", b(True))]),
    rule([compare(ov("playersInRoom", rt="Int"), "<", lit(2))], [line("StartButton", "Button", "setDisabled", b(True))]),
    rule(everyone, [line("StartButton", "Button", "setDisabled", b(False))]),
    rule([pressed("StartButton")], [online("startGame")]),
    rule([online("onGameStarted")], [go("Level")]),
    rule([pressed("InviteButton")], [line("system", "System", "copyToClipboard", ov("inviteLink")), say("Status", op("+", s("Copied: "), ov("inviteLink")))]),
    rule([online("onBecameHost")], [say("Status", s("The host left: this game is the host now."))]),
    rule([pressed("LeaveButton")], [online("leaveRoom")]),
    rule([online("onLeftRoom")], [go("Title")]),
], vars=[{"name": "Toggle", "type": "number", "value": 0}])

# ── Level: the Two players level, shared ──
# Each Player is Synced: with Owner 0 it belongs to the game whose player its Player number is.
player = read("Player.type.json")
player["components"].insert(0, {"componentClass": "Synced", "rate": 20})
write("Player.type.json", player)
type_json("LevelStatus", "Label", {"text": "", "fontSize": 8}, ["NetRules"])
scene = read("scenes/Level.scene.json")
hud = next(o for o in scene["objects"] if o["name"] == "HUD")
# One camera on the whole screen, following this game's own player.
scene["objects"] = [o for o in scene["objects"] if o["name"] != "Camera2"]
for o in scene["objects"]:
    if o["name"] == "Camera1": o["viewport"] = "Whole screen"
scene["objects"].append({"id": "e0000000-0000-4000-8000-000000000903", "parent": hud["id"], "name": "LevelStatus1", "type": "LevelStatus", "x": 60, "y": 8})
write("scenes/Level.scene.json", scene)
write("vscript/NetRules.vscript.json", {"rules": [
    rule([once(), online("isInRoom")], [line("Camera", "Camera", "follow", op("+", s("Player"), me)), say("LevelStatus", op("+", s("Room "), ov("roomCode")))]),
    rule([online("onLeftRoom")], [say("LevelStatus", ov("leftReason")), go("Title")]),
], "vars": []})

# ── the singleton with the Scene Manager, and the project ──
write("scenes/singletons/Online.scene.json", {"schemaVersion": 2, "objects": [
    {"id": "e0000000-0000-4000-8000-000000003001", "name": "Online"},
    {"id": "e0000000-0000-4000-8000-000000003002", "parent": "e0000000-0000-4000-8000-000000003001", "name": "Scenes1", "type": "Scenes", "x": 0, "y": 0},
]})
project = read("project.json")
project["name"] = "Online demo"
# A fixed id, so copies of the demo opened as they are meet; a project made from it gets its own.
project["id"] = "0e11d3e40000400080000000000000a1"
project["entryScene"] = "scenes/Title.scene.json"
project["singletons"] = ["scenes/singletons/Online.scene.json"]
project.setdefault("export", {})["version"] = "1.0"
write("project.json", project)

write("README.md", """# Online demo

The Two players demo played in two games at once, through a relay: each game
plays its own player and shows the other's. Three scenes, the way an online
game usually goes:

- **Title**: type a name, then **Host a game** (a private room; the other
  player joins with its code), **Play online** (any public room of this game,
  or a new one when there is none), or **Join** with a code. A game opened by
  an invite link joins that room by itself.
- **Waiting room** (Lobby): who is in the room and whether they are ready.
  **Ready**, **Copy invite** and **Leave**; the host's **Start** works once
  both players are ready, and takes both games to the level.
- **Level**: each **Player** has the **Synced** behavior, owned by the game
  whose player its Player number is; the camera follows this game's player.

To try it, choose **Project ▸ Run with players… ▸ 2 players**: the editor
starts a relay on this computer and opens two windows. Host in one and join
with the code in the other, or press Play online in both.

Run on its own, the game connects to a relay at ws://127.0.0.1:8765, which
`node scripts/relay.mjs` from the Loominary folder starts. Project ▸ Save relay
server… saves one, with what putting it online takes.

- `vscript/TitleRules`, `vscript/LobbyRules`: the Online words for rooms and
  the waiting room. `vscript/NetRules`: the level's.
- Rooms match games by the project's id and version (Project ▸ Export ▸
  Version), so a new version does not meet the old one.

Art and sounds by [Kenney](https://kenney.nl) (Pixel Platformer, Digital
Audio, Impact Sounds), CC0. Generated by `tools/make-online-demo.py` from the
Two players demo.
""")
print("wrote", out)
