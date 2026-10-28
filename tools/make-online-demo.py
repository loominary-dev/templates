"""The Online demo: the Two players demo played in two games, through a relay
(docs/multiplayer.md in the Loominary repository). Made from the generated
Two players demo, so it follows that demo when it changes.

    python3 tools/make-online-demo.py [demos/duo] [demos/online]

What changes: each Player is Synced, so each game decides where its own
player is and shows the other's; a Status line on the HUD connects to the
relay when the game starts, joins any public room, or makes one when there is
none, and says what happened.
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

def read(rel):
    with open(os.path.join(out, rel)) as f: return json.load(f)
def write(rel, data):
    with open(os.path.join(out, rel), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

project = read("project.json")
project["name"] = "Online demo"
write("project.json", project)

# Each Player is Synced: with Owner 0 it belongs to the game whose player its Player number is.
player = read("Player.type.json")
player["components"].insert(0, {"componentClass": "Synced", "rate": 20})
write("Player.type.json", player)

# The status line, with the rules that take the game online.
write("Status.type.json", {"schemaVersion": 2, "baseClass": "Label", "defaults": {"text": "", "fontSize": 8},
                           "components": [{"componentClass": "NetRules"}]})
scene = read("scenes/Level.scene.json")
hud = next(o for o in scene["objects"] if o["name"] == "HUD")
scene["objects"].append({"id": "e0000000-0000-4000-8000-000000000903", "parent": hud["id"], "name": "Status1", "type": "Status", "x": 60, "y": 8})
write("scenes/Level.scene.json", scene)

def lit(v, kind=None):
    p = {"type": "literal", "value": v}
    if kind: p["valueKind"] = kind
    return p
def s(v): return lit(v, "string")
def b(v): return lit(v, "bool")
def online(name, *params, **k): return dict({"scope": "online", "className": "Online", "name": name, "params": list(params)}, **k)
def value(scope, cls, name, *params, rt="String"): return {"type": "value", "scope": scope, "className": cls, "name": name, "params": list(params), "returnType": rt}
def say(*params): return {"scope": "self:Status", "className": "Label", "name": "setText", "params": list(params)}
def once(): return {"scope": "system", "className": "VisualScriptComponent", "name": "triggerOnce", "params": []}
def rule(conditions, actions): return {"conditions": conditions, "actions": actions, "subRules": []}
# The relay Run with players started, else one on this computer's port 8765 (node scripts/relay.mjs).
relay = value("online", "Online", "relayAddress", s("ws://127.0.0.1:8765"))
rules = [
    rule([once()], [online("connect", relay), say(s("Connecting to the relay..."))]),
    rule([online("onConnected")], [online("joinAnyRoom")]),
    rule([online("onJoinFailed"), online("isConnected")], [online("createRoom", lit(2), b(True)), say(s("Waiting for a second player..."))]),
    rule([online("onJoinFailed"), online("isConnected", **{"not": True})], [say(value("online", "Online", "joinFailure"))]),
    rule([online("onJoinedRoom")], [say(value("online", "Online", "roomCode"))]),
    rule([online("onLeftRoom")], [say(value("online", "Online", "leftReason"))]),
]
write("vscript/NetRules.vscript.json", {"rules": rules, "vars": []})

write("README.md", """# Online demo

The Two players demo in two games at once, through a relay: each game plays
its own player and shows the other's.

To try it, choose **Project ▸ Run with players… ▸ 2 players**: the editor
starts a relay on this computer and opens two windows. The first makes a room
and the second joins it. Each window moves its own player with W A S D or the
arrows (or a pad); the other player moves as the other window plays.

- **Status** on the HUD holds the rules that go online (`vscript/NetRules`):
  connect to the relay when the game starts, join any public room, make one
  when there is none. It shows the room's code once in one.
- Each **Player** has the **Synced** behavior. Its Owner is 0, so it belongs
  to the game whose player its Player number is: player 1's game decides where
  Player1 is, player 2's where Player2 is.
- The player rules are the Two players demo's: **Player Self.player: input
  command … is on**. In a room, each game's own player reads every key and pad
  of that computer.

Run on its own, the game finds no relay and plays as the Two players demo. A
relay of your own is `node scripts/relay.mjs` from the Loominary folder, on
port 8765 unless told otherwise.

Art and sounds by [Kenney](https://kenney.nl) (Pixel Platformer, Digital
Audio, Impact Sounds), CC0. Generated by `tools/make-online-demo.py` from the
Two players demo.
""")
print("wrote", out)
