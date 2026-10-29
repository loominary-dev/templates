#!/usr/bin/env python3
"""One project's files moved to the origin rule (docs/origin-scope.md), in place.

    python3 scripts/convert-to-origin.py <project folder> [--dry]

Before it, an object's own space had 0,0 at its picture's top-left corner: collision
shapes, named points and children were measured from there. After it they are
measured from the object's origin (its x and y), which a sprite frame's origin puts
on its picture. Run it once on a project made before 2026-10-29:

- a sprite file's frame shapes and points are moved by minus the frame's origin in
  pixels (an animation's shared ones by its first frame's), and the frame keys
  `pivotX`/`pivotY` become `originX`/`originY`;
- a Type's shapes and points are moved by minus the Type's origin (its own, else its
  sprite frame's), and `pivotX`/`pivotY`/`pivotNormalized` become `origin*`;
- in a scene, the same for an object's own shapes and points, a MeshSprite's mesh
  (vertices moved, each bone's bind put back on them), and a child of an object
  with an origin is moved by minus that origin.

Normalized named points are left alone: they are fractions of the box, and the box
moves with them. A project already converted (a sprite frame keyed `originX`) is
left alone.
"""
import json, os, sys

FRAME_ORIGIN = {"Sprite", "Light", "MeshSprite", "Particles"}
RENAME = {"pivotX": "originX", "pivotY": "originY", "pivotNormalized": "originNormalized"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data, dry):
    if dry:
        print("would write", path)
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def num(v):
    """A whole number stays whole: a shift of 0 wrote 0.0 where the file said 0."""
    return int(v) if isinstance(v, float) and v.is_integer() else v


def shift_shape(s, dx, dy):
    s = dict(s)
    if s.get("kind") == "poly":
        s["points"] = [dict(p, x=num(p["x"] + dx), y=num(p["y"] + dy)) for p in s.get("points", [])]
    else:
        s["cx"] = num(s.get("cx", 0) + dx)
        s["cy"] = num(s.get("cy", 0) + dy)
    return s


def shift_points(points, dx, dy):
    return [p if p.get("normalized") else dict(p, x=num(p["x"] + dx), y=num(p["y"] + dy)) for p in points]


def rename(d):
    for old, new in RENAME.items():
        if old in d:
            d[new] = d.pop(old)


class Project:
    def __init__(self, root):
        self.root = root
        self.sprites = {}   # path relative to the root → (w, h, ox, oy) of the first frame, origin normalized
        self.types = {}     # type name → its file's data
        for dirpath, _, files in os.walk(root):
            if "/generated" in dirpath or "/node_modules" in dirpath or "/." in dirpath:
                continue
            for f in files:
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root)
                if f.endswith(".sprite.json"):
                    d = load(full)
                    first = next((fr for a in d.get("animations", []) for fr in a.get("frames", [])), {})
                    ox = first.get("pivotX", first.get("originX", 0.5))
                    oy = first.get("pivotY", first.get("originY", 0.5))
                    self.sprites[rel] = (d.get("width", 0), d.get("height", 0), ox if ox is not None else 0.5, oy if oy is not None else 0.5)
                elif f.endswith(".type.json"):
                    self.types[f[:-len(".type.json")]] = d = load(full)
                    d["__path"] = full

    def sprite(self, key):
        if not key:
            return None
        if key in self.sprites:
            return self.sprites[key]
        base = os.path.basename(key)
        for rel, v in self.sprites.items():
            if os.path.basename(rel) == base:
                return v
        return None

    def type_chain(self, name):
        """The Type and the Types it extends, nearest first, until an engine class."""
        out, seen = [], set()
        while name in self.types and name not in seen:
            seen.add(name)
            out.append(self.types[name])
            name = self.types[name].get("baseClass")
        return out, name

    def field(self, obj, chain, key):
        if obj is not None and key in obj:
            return obj[key]
        for t in chain:
            df = t.get("defaults", {})
            if key in df:
                return df[key]
        return None

    def origin(self, type_name, obj=None):
        """Where the object's origin is on its picture, in pixels from its top-left (the old local 0,0)."""
        chain, engine_class = self.type_chain(type_name)
        if not chain and obj is None:
            engine_class = type_name
        px, py = self.field(obj, chain, "pivotX"), self.field(obj, chain, "pivotY")
        norm = self.field(obj, chain, "pivotNormalized")
        spr = self.sprite(self.field(obj, chain, "spriteKey"))
        own = (px not in (None, 0)) or (py not in (None, 0)) or norm
        if own:
            px, py = px or 0, py or 0
            if norm:
                if spr:
                    return px * spr[0], py * spr[1]
                if engine_class == "AreaSprite":
                    return px * (self.field(obj, chain, "areaWidth") or 0), py * (self.field(obj, chain, "areaHeight") or 0)
                return 0.0, 0.0
            return float(px), float(py)
        # Only a sprite (and a light, a mesh, particles) follows its frame's origin; an area of
        # pictures, a tilemap, a camera and everything else default to their own 0,0.
        if spr and engine_class in FRAME_ORIGIN:
            return spr[2] * spr[0], spr[3] * spr[1]
        return 0.0, 0.0


def convert_sprite(path, dry):
    d = load(path)
    before = json.dumps(d, sort_keys=True)
    frames = [fr for a in d.get("animations", []) for fr in a.get("frames", [])]
    if any("originX" in fr for fr in frames):
        return False
    w, h = d.get("width", 0), d.get("height", 0)
    for a in d.get("animations", []):
        fs = a.get("frames", [])
        first = fs[0] if fs else {}
        ax = -(first.get("pivotX", 0.5) if first.get("pivotX") is not None else 0.5) * w
        ay = -(first.get("pivotY", 0.5) if first.get("pivotY") is not None else 0.5) * h
        if a.get("collision"):
            a["collision"] = [shift_shape(s, ax, ay) for s in a["collision"]]
        if a.get("points"):
            a["points"] = shift_points(a["points"], ax, ay)
        for fr in fs:
            fx = -(fr.get("pivotX", 0.5) if fr.get("pivotX") is not None else 0.5) * w
            fy = -(fr.get("pivotY", 0.5) if fr.get("pivotY") is not None else 0.5) * h
            if fr.get("collision"):
                fr["collision"] = [shift_shape(s, fx, fy) for s in fr["collision"]]
            if fr.get("points"):
                fr["points"] = shift_points(fr["points"], fx, fy)
            rename(fr)
    if json.dumps(d, sort_keys=True) == before:
        return False
    save(path, d, dry)
    return True


def convert_mesh(mesh, ox, oy):
    """A MeshSprite's mesh: vertices moved by minus the origin, and each bone's bind (a, b, c, d, tx, ty)
    multiplied by a move to the origin, so the skinned vertices land where they did."""
    if not isinstance(mesh, dict) or (ox == 0 and oy == 0):
        return
    v = mesh.get("vertices")
    if v:
        mesh["vertices"] = [num(round(x - (ox if i % 2 == 0 else oy), 6)) for i, x in enumerate(v)]
    b = mesh.get("binds")
    if b:
        out = list(b)
        for i in range(0, len(out) - 5, 6):
            a_, b_, c_, d_ = out[i], out[i + 1], out[i + 2], out[i + 3]
            out[i + 4] = num(round(out[i + 4] + a_ * ox + c_ * oy, 6))
            out[i + 5] = num(round(out[i + 5] + b_ * ox + d_ * oy, 6))
        mesh["binds"] = out


def convert_own(target, ox, oy):
    """An object's (or a Type's defaults') own shapes, points and mesh, moved to be measured from its origin."""
    col = target.get("collision")
    if isinstance(col, dict) and col.get("shapes"):
        col["shapes"] = [shift_shape(s, -ox, -oy) for s in col["shapes"]]
    if target.get("points"):
        target["points"] = shift_points(target["points"], -ox, -oy)
    convert_mesh(target.get("mesh"), ox, oy)
    rename(target)


def convert(root, dry=False):
    p = Project(root)
    # A project in the new form has sprite frames keyed originX: it is left as it is.
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(".sprite.json") and '"originX"' in open(os.path.join(dirpath, f), encoding="utf-8").read():
                print(root, "is already converted")
                return []
    changed = []
    # Origins first, from the files as they were.
    type_origin = {name: p.origin(name) for name in p.types}
    for dirpath, _, files in os.walk(root):
        if "/generated" in dirpath or "/node_modules" in dirpath or "/." in dirpath:
            continue
        for f in files:
            full = os.path.join(dirpath, f)
            if f.endswith(".sprite.json") and convert_sprite(full, dry):
                changed.append(full)
    for name, t in p.types.items():
        df = t.get("defaults", {})
        path = t.pop("__path")
        before = json.dumps(t, sort_keys=True)
        ox, oy = type_origin[name]
        convert_own(df, ox, oy)
        if json.dumps(t, sort_keys=True) != before:
            save(path, t, dry)
            changed.append(path)
    for dirpath, _, files in os.walk(root):
        if "/generated" in dirpath or "/node_modules" in dirpath or "/." in dirpath:
            continue
        for f in files:
            if not f.endswith(".scene.json"):
                continue
            full = os.path.join(dirpath, f)
            d = load(full)
            objs = d.get("objects", [])
            by_id = {o["id"]: o for o in objs if "id" in o}
            origin_of = {o["id"]: p.origin(o.get("type"), o) for o in objs if "id" in o}
            dirty = False
            for o in objs:
                before = json.dumps(o, sort_keys=True)
                ox, oy = origin_of.get(o.get("id"), (0.0, 0.0))
                convert_own(o, ox, oy)
                par = o.get("parent")
                if par in origin_of:
                    pox, poy = origin_of[par]
                    if pox or poy:
                        o["x"] = num(o.get("x", 0) - pox)
                        o["y"] = num(o.get("y", 0) - poy)
                if json.dumps(o, sort_keys=True) != before:
                    dirty = True
            if dirty:
                save(full, d, dry)
                changed.append(full)
    return changed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for path in convert(sys.argv[1], "--dry" in sys.argv):
        print(path)
