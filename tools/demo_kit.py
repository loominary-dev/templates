"""What the demo generators share: writing files, sprites as their two files,
shapes, Types, scenes, and the visual-script rule shapes. Each generator
makes one demo folder from nothing, so a format change is a re-run."""
import atexit, base64, json, math, os, shutil, struct
import origin_rule
from PIL import Image, ImageDraw


_RESERVED = None
def check_name(name):
    """A Type's name is a class of the game: one the engine, Haxe or the browser uses would hide theirs
    (a Type named Blob breaks every picture on the web). Loominary's own list, when its checkout is beside this one."""
    global _RESERVED
    if _RESERVED is None:
        loom = os.environ.get("LOOMINARY_REPO") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Loom")
        _RESERVED = set()
        listed = os.path.join(loom, "engine", "reserved-names.json")
        if os.path.exists(listed):
            data = json.load(open(listed))
            _RESERVED = {n.lower() for n in data["haxe"] + data["browser"]}
            for d in ["engine/src", "engine/src/core", "engine/src/objects", "engine/src/behaviors", "editor/behaviors"]:
                full = os.path.join(loom, d)
                if os.path.isdir(full): _RESERVED |= {f[:-3].lower() for f in os.listdir(full) if f.endswith(".hx")}
    if name.lower() in _RESERVED:
        raise SystemExit('"%s" is a name the engine, Haxe or the browser uses itself: give the Type another' % name)


class Demo:
    def __init__(self, out, folders, prefix):
        self.out = os.path.abspath(out)
        # Everything here is written measured from a picture's top-left corner, as the generators were
        # written; when the generator ends, the project is moved to the origin rule (origin_rule.py,
        # Loominary's docs/origin-scope.md): shapes, points, meshes and children from the origin.
        atexit.register(origin_rule.convert, self.out)
        # The folder's git settings are not the generator's to make: kept through the rebuild.
        kept = {}
        for name in (".gitattributes", ".gitignore"):
            path = os.path.join(self.out, name)
            if os.path.isfile(path):
                with open(path, "rb") as f: kept[name] = f.read()
        shutil.rmtree(self.out, ignore_errors=True)
        for d in folders: os.makedirs(os.path.join(self.out, d))
        os.makedirs(self.out, exist_ok=True)
        for name, data in kept.items():
            with open(os.path.join(self.out, name), "wb") as f: f.write(data)
        self.prefix = prefix
        self.seq = 100

    def write(self, rel, data):
        path = os.path.join(self.out, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(json.dumps(data, indent=2) + "\n" if not isinstance(data, str) else data)

    def uid(self, n):  # stable ids, so a re-run changes nothing that did not change
        return "%s-0000-4000-8000-%012d" % (self.prefix, n)

    def next_id(self):
        self.seq += 1
        return self.uid(self.seq)

    def sprite(self, name, w, h, animations, collision, points=()):
        """A sprite as its two files: the document, and the picture beside it holding every frame's pixels as a grid."""
        layer = self.next_id()
        anims, cels, pictures = [], [], []
        for aname, frames, duration, mode in animations:
            fids = []
            for f in frames:
                fid = self.next_id()
                fids.append(fid)
                cels.append({"layerId": layer, "frameId": fid, "at": len(pictures)})
                pictures.append(f)
            anims.append({"id": self.next_id(), "name": aname, "loop": mode == "loop", "playMode": mode, "repeatTo": 0, "repeatCount": 0,
                          "collision": collision, "points": list(points), "collisionShared": True, "pointsShared": True,
                          "frames": [{"id": fid, "duration": duration, "pivotX": 0.5, "pivotY": 0.5, "collision": [], "points": []} for fid in fids]})
        columns = max(1, math.ceil(math.sqrt(len(pictures))))
        rows = max(1, math.ceil(len(pictures) / columns))
        sheet = Image.new("RGBA", (w * columns, h * rows), (0, 0, 0, 0))
        for i, pic in enumerate(pictures):
            sheet.paste(pic.convert("RGBA"), ((i % columns) * w, (i // columns) * h))
        sheet.save(os.path.join(self.out, name + ".sprite.png"))
        self.write(name + ".sprite.json", {"width": w, "height": h, "colorMode": "rgba", "sheet": {"columns": columns}, "palette": [],
            "layers": [{"id": layer, "name": "Layer 1", "visible": True, "opacity": 1, "locked": False, "blendMode": "normal", "reference": False}],
            "animations": anims, "cels": cels})
        return name + ".sprite.json"

    def type_json(self, name, base, defaults, components=()):
        check_name(name)
        self.write(name + ".type.json", {"schemaVersion": 2, "baseClass": base, "defaults": dict(defaults), "components": list(components)})

    def scene(self, rel, objects, components=()):
        data = {"schemaVersion": 3, "objects": objects}
        if components: data["components"] = list(components)
        self.write(rel, data)

    def sounds(self, table):
        """`{key: (pack dir, file)}` copied to assets/sounds and listed in assets.json."""
        assets = []
        os.makedirs(os.path.join(self.out, "assets", "sounds"), exist_ok=True)
        for n, (key, (pack, f)) in enumerate(table.items()):
            shutil.copy(os.path.join(pack, "Audio", f), os.path.join(self.out, "assets", "sounds", key + ".ogg"))
            assets.append({"uuid": self.uid(900 + n), "key": key, "path": "assets/sounds/%s.ogg" % key})
        self.write("assets.json", {"schemaVersion": 1, "assets": assets})


# ── shapes and points ──
def box(name, cx, cy, w, h, **extra): return dict({"name": name, "kind": "box", "cx": cx, "cy": cy, "w": w, "h": h}, **extra)
def circle(name, cx, cy, r, **extra): return dict({"name": name, "kind": "circle", "cx": cx, "cy": cy, "r": r}, **extra)
def poly(name, points, **extra): return dict({"name": name, "kind": "poly", "points": [{"x": x, "y": y} for x, y in points]}, **extra)
def point(name, x, y): return {"name": name, "x": x, "y": y}


# ── pictures ──
def canvas(w, h): return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def drawn(rows, colors):
    """A small picture from rows of characters, one color per character, '.' clear."""
    img = canvas(len(rows[0]), len(rows))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".": img.putpixel((x, y), colors[ch])
    return img

def soft_dot(size, color=(255, 255, 255), power=1.4):
    """A round dot whose alpha falls off from the middle: one particle's picture."""
    img = canvas(size, size)
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / (c + 0.5)
            if d < 1: img.putpixel((x, y), color + (int(255 * (1 - d) ** power),))
    return img


# ── rules ──
def lit(v, kind=None):
    p = {"type": "literal", "value": v}
    if kind: p["valueKind"] = kind
    return p
def s(v): return lit(v, "string")
def b(v): return lit(v, "bool")
def value(scope, cls, name, *params, **k):
    return dict({"type": "value", "scope": scope, "className": cls, "name": name, "params": list(params), "returnType": "Float"}, **k)
def cvalue(scope, cls, name, *params, **k): return value(scope, cls, name, *params, onComponent=True, **k)
def op(o, left, right): return {"type": "op", "op": o, "left": left, "right": right}
def line(scope, cls, name, *params, **k): return dict({"scope": scope, "className": cls, "name": name, "params": list(params)}, **k)
def comp(scope, cls, name, *params, **k): return line(scope, cls, name, *params, onComponent=True, **k)
# The sheet's own words run on the sheet; the picker lists the ray words under Physics and the making, pooling and family words under Objects.
PHYSICS_WORDS = ['lineIsClear', 'showContactPoints', 'pickByRay', 'pickInBox', 'queryCount', 'rayHitDistance', 'rayHitX', 'rayHitY', 'rayNormalX', 'rayNormalY']
OBJECT_WORDS = ['createObject', 'createScene', 'destroyNewest', 'forgetAllPools', 'forgetPool', 'isSetAside', 'keepReady', 'keepSceneReady', 'letGo', 'letGoAll', 'objectTypeIsPreloaded', 'pickChild', 'pickClosestAbove', 'pickDescendant', 'pickParent', 'preloadObjectType', 'preloadScene', 'sceneIsPreloaded', 'scenePreloadLoaded', 'scenePreloadProgress', 'scenePreloadTotal', 'stepPreloadScene', 'unparkObject']
def sheet(name, *params, **k): return line("physics" if name in PHYSICS_WORDS else "objects" if name in OBJECT_WORDS else "system", "VisualScriptComponent", name, *params, **k)
def system(name, *params, **k): return line("system", "System", name, *params, **k)
def once(): return sheet("triggerOnce")
def held(command): return line("input", "Input", "isCommandOn", s(command))
def pressed(command): return line("input", "Input", "isCommandPressed", s(command))
def mouse_down(button): return line("input", "Input", "isMouseDown", lit(button))
def mouse_pressed(button): return line("input", "Input", "isMousePressed", lit(button))
def not_(c): return dict(c, **{"not": True})
def var(name): return value("variables", "Variables", "getVariable", s(name))
def sheet_var(name): return value("system", "VisualScriptComponent", "sheetVar", s(name))
def set_sheet_var(name, v): return sheet("setSheetVar", s(name), v)
def add_sheet_var(name, v): return sheet("addSheetVar", s(name), v)
def random(lo, hi): return value("maths", "Maths", "random", lit(lo), lit(hi))
def dt(): return value("system", "System", "getDeltaTime")
def rule(conditions, actions, sub=()): return {"conditions": conditions, "actions": actions, "subRules": list(sub)}
# System's Compare orders its operators =, ≠, <, ≤, >, ≥; an object's own comparisons (position, scale…) <, ≤, =, ≠, ≥, >.
EQ, NE, LT, LE, GT, GE = 0, 1, 2, 3, 4, 5
OBJ_LT, OBJ_LE, OBJ_EQ, OBJ_NE, OBJ_GE, OBJ_GT = 0, 1, 2, 3, 4, 5
def compare(left, o, right): return line("maths", "Maths", "compare", left, lit(o), right)
LEFT_BUTTON, RIGHT_BUTTON = 0, 1
def keys(*codes): return {"bindings": [{"kind": "key", "code": c} for c in codes]}
