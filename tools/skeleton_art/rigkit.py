"""A rig made from SVG parts: bones in the rest pose (world pixels of the drawing, ground at y=0), pictures on bones (rigid,
drawn as they stand) or meshes bent by several bones, rendered to PNGs at a scale, and written into a demo scene with the
skeleton's animations keyed from poses (turns of bones, offsets of their bases)."""
import math, os, subprocess, json
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NODE = os.environ.get("NODE", "node")

def norm(a):
    while a > math.pi: a -= 2 * math.pi
    while a < -math.pi: a += 2 * math.pi
    return a

class Bone:
    def __init__(self, name, parent, base, tip, **extra):
        self.name, self.parent, self.base, self.tip, self.extra = name, parent, base, tip, extra
        self.angle = math.atan2(tip[1] - base[1], tip[0] - base[0])
        self.length = math.hypot(tip[0] - base[0], tip[1] - base[1])

class Part:
    def __init__(self, name, svg, bone, mesh=None, z=0):
        self.name, self.svg, self.bone, self.mesh, self.z = name, svg, bone, mesh, z

class Rig:
    def __init__(self, name, scale, order_by_z=False):
        """order_by_z: the skeleton draws its pictures by their Z across all its bones (Skeleton.orderPicturesByZ), so a
        picture can go behind one on another bone; otherwise each bone's pictures come with that bone."""
        self.name, self.k, self.order_by_z = name, scale, order_by_z
        self.bones, self.order, self.parts = {}, [], []

    def bone(self, name, parent, base, tip, **extra):
        b = Bone(name, parent, base, tip, **extra)
        self.bones[name] = b; self.order.append(name)
        return b

    def part(self, name, svg, bone, mesh=None, z=0):
        """mesh: None (rigid on `bone`) or (grid columns, grid rows, weigh(x, y) -> {bone: weight}) in drawing pixels."""
        self.parts.append(Part(name, svg, bone, mesh, z))

    # ── geometry ──
    def rest_local(self, b):
        """A bone's place and turn under its parent, in drawing pixels."""
        if b.parent is None: return b.base[0], b.base[1], b.angle
        p = self.bones[b.parent]
        dx, dy = b.base[0] - p.base[0], b.base[1] - p.base[1]
        c, s = math.cos(-p.angle), math.sin(-p.angle)
        return dx * c - dy * s, dx * s + dy * c, b.angle - p.angle

    def world(self, turns=None, offsets=None):
        """Each bone's world base and angle with turns (radians) and offsets (drawing pixels, in the parent's frame)."""
        turns, offsets = turns or {}, offsets or {}
        out = {}
        for name in self.order:
            b = self.bones[name]
            lx, ly, la = self.rest_local(b)
            ox, oy = offsets.get(name, (0, 0)); lx += ox; ly += oy
            if b.parent is None:
                out[name] = ((lx, ly), la + turns.get(name, 0))
            else:
                (px, py), pa = out[b.parent]
                out[name] = ((px + lx * math.cos(pa) - ly * math.sin(pa), py + lx * math.sin(pa) + ly * math.cos(pa)), pa + la + turns.get(name, 0))
        return out

    def two_bone(self, turns, offsets, upper, lower, target, prefer=None, fold_limit=None):
        """Turns for upper and lower so lower's tip reaches target; `prefer(joint_a, joint_b)` picks between the two bends."""
        wp = self.world(turns, offsets)
        base = wp[upper][0]
        l1, l2 = self.bones[upper].length, self.bones[lower].length
        dx, dy = target[0] - base[0], target[1] - base[1]
        d = min(math.hypot(dx, dy), l1 + l2 - 1e-3)
        if fold_limit is not None:
            d = max(d, math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(math.radians(fold_limit))) + 1e-3)
        a = math.atan2(dy, dx)
        c1 = max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
        sols = []
        for bend in (1, -1):
            w1 = a - bend * math.acos(c1)
            joint = (base[0] + l1 * math.cos(w1), base[1] + l1 * math.sin(w1))
            sols.append((w1, joint))
        w1, joint = sols[0] if prefer is None or prefer(sols[0][1], sols[1][1]) else sols[1]
        tip = (base[0] + d * math.cos(a), base[1] + d * math.sin(a))
        w2 = math.atan2(tip[1] - joint[1], tip[0] - joint[0])
        ub, lb = self.bones[upper], self.bones[lower]
        pa = wp[ub.parent][1] if ub.parent else 0
        t1 = norm(w1 - pa - self.rest_local(ub)[2])
        t2 = norm(w2 - w1 - self.rest_local(lb)[2])
        return t1, t2

    def keep_world_angle(self, turns, offsets, name, angle):
        """The turn that leaves bone `name` at world angle `angle` given the rest of the pose."""
        t0 = turns.get(name, 0); wp = self.world(turns, offsets)
        return norm(t0 + angle - wp[name][1])

    # ── pictures ──
    def render(self, outdir):
        """Each part to <outdir>/<Rig><Part>.png at the rig's scale, cropped to its pixels; remembers each picture's world top-left."""
        os.makedirs(outdir, exist_ok=True)
        X0, Y0, W, H = -400, -500, 800, 800   # down to y = 300: the jellyfish hangs below its 0
        k = self.k
        for p in self.parts:
            svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%d %d %d %d"><defs><clipPath id="ground"><rect x="-1000" y="-1000" width="2000" height="1000"/></clipPath></defs>%s</svg>' % (
                W * k, H * k, X0, Y0, W, H, p.svg)
            f = os.path.join(outdir, "_part.svg"); open(f, "w").write(svg)
            png = os.path.join(outdir, self.name + p.name + ".png")
            subprocess.run([NODE, os.path.join(HERE, "render.mjs"), f, png, "1"], check=True)
            im = Image.open(png).convert("RGBA"); bb = im.getbbox(); im = im.crop(bb)
            # Clear edges take their neighbors' color, so filtering draws no dark fringe.
            im = bleed(im); im.save(png)
            p.png, p.size, p.top_left = png, im.size, (X0 + bb[0] / k, Y0 + bb[1] / k)
        os.remove(os.path.join(outdir, "_part.svg"))

    # ── the scene ──
    def objects(self, put, at, type_of, demo):
        """Places the skeleton at `at` (game pixels, the drawing's 0,0) and its bones and pictures; put(name, type, parent, **fields) -> id."""
        k = self.k
        sk = put(self.name + "1", self.name, None, x=at[0], y=at[1], **({"orderPicturesByZ": True} if self.order_by_z else {}))
        ids = {}
        for name in self.order:
            b = self.bones[name]
            lx, ly, la = self.rest_local(b)
            ids[name] = put(name, type_of(b), ids[b.parent] if b.parent else sk,
                            **dict({"x": round(lx * k, 3), "y": round(ly * k, 3), "rotation": round(la, 6), "length": round(b.length * k, 2)}, **b.extra))
        for p in sorted(self.parts, key=lambda p: p.z):
            b = self.bones[p.bone]
            w, h = p.size
            piv = ((b.base[0] - p.top_left[0]) * k / w, (b.base[1] - p.top_left[1]) * k / h)
            fields = dict(pivotNormalized=True, pivotX=round(piv[0], 5), pivotY=round(piv[1], 5), rotation=round(-b.angle, 6), zIndex=p.z)
            if p.mesh: fields["mesh"] = self.mesh_of(p)
            put(self.name + p.name, self.name + p.name, ids[p.bone], **fields)
        return sk, ids

    def mesh_of(self, p):
        cols, rows, weigh = p.mesh
        k = self.k
        w, h = p.size
        im = Image.open(p.png)
        verts, uvs, idx = [], [], []
        for j in range(rows + 1):
            for i in range(cols + 1):
                verts += [round(w * i / cols, 2), round(h * j / rows, 2)]
                uvs += [round(i / cols, 5), round(j / rows, 5)]
        for j in range(rows):
            for i in range(cols):
                x0, y0, x1, y1 = int(w * i / cols), int(h * j / rows), int(w * (i + 1) / cols), int(h * (j + 1) / rows)
                if im.crop((x0, y0, max(x0 + 1, x1), max(y0 + 1, y1))).getbbox() is None: continue
                a = j * (cols + 1) + i
                idx += [a, a + 1, a + cols + 2, a, a + cols + 2, a + cols + 1]
        n = len(verts) // 2
        names = sorted({nm for v in range(n) for nm in weigh(*self.to_drawing(p, verts[v * 2], verts[v * 2 + 1])).keys()})
        weights = {nm: [] for nm in names}
        for v in range(n):
            ws = weigh(*self.to_drawing(p, verts[v * 2], verts[v * 2 + 1]))
            tot = sum(ws.values()) or 1
            for nm in names: weights[nm].append(round(ws.get(nm, 0) / tot, 4))
        binds = []
        for nm in names:
            b = self.bones[nm]
            # The bone in the mesh's frame (its picture's pixels): from the picture's top-left, scaled; its inverse.
            tx, ty = (b.base[0] - p.top_left[0]) * k, (b.base[1] - p.top_left[1]) * k
            c, s = math.cos(b.angle), math.sin(b.angle)
            binds += [round(v, 6) for v in (c, -s, s, c, -(c * tx + s * ty), -(-s * tx + c * ty))]
        return {"vertices": verts, "uvs": uvs, "indices": idx, "bones": names, "binds": binds, "weights": weights, "painted": list(range(n))}

    def to_drawing(self, p, x, y):
        return p.top_left[0] + x / self.k, p.top_left[1] + y / self.k

    # ── animation ──
    def moving(self, keysets, eps=1e-4):
        """(bone, property) pairs that any key of any of these animations moves from the rest pose: the only ones worth a track."""
        out = set()
        for keys in keysets:
            for t, tu, of, *_ in keys:
                for name, v in tu.items():
                    if abs(v) > eps: out.add((name, "rotation"))
                for name, (ox, oy) in of.items():
                    if abs(ox) > eps: out.add((name, "x"))
                    if abs(oy) > eps: out.add((name, "y"))
        return out

    def keyed(self, keys, props, ease="easeInOut"):
        """Tracks for exactly the (bone, property) pairs given, in the skeleton's bone order: what an animator would key."""
        k = self.k
        tracks = []
        for name in self.order:
            for prop in ("x", "y", "rotation"):
                if (name, prop) not in props: continue
                lx, ly, la = self.rest_local(self.bones[name])
                ks = []
                for t, tu, of, *_ in keys:
                    v = {"x": (lx + of.get(name, (0, 0))[0]) * k, "y": (ly + of.get(name, (0, 0))[1]) * k, "rotation": la + tu.get(name, 0)}[prop]
                    k_ = {"t": round(t, 4), "v": round(v, 5)}
                    if ease: k_["ease"] = ease
                    ks.append(k_)
                ks[-1].pop("ease", None)
                tracks.append({"target": name, "property": prop, "keys": ks})
        return tracks

    def tracks(self, keys, bones=None, ease="easeInOut"):
        """Keys [(t, turns, offsets, extra_tracks)] -> the skeleton's tracks: x, y and rotation of each bone named (default: every bone any key moves)."""
        k = self.k
        moved = bones or sorted({n for _, tu, of, *_ in keys for n in list(tu) + list(of)}, key=self.order.index)
        tracks = []
        for name in moved:
            b = self.bones[name]
            lx, ly, la = self.rest_local(b)
            for prop in ("x", "y", "rotation"):
                ks = []
                for t, tu, of, *_ in keys:
                    v = {"x": (lx + of.get(name, (0, 0))[0]) * k, "y": (ly + of.get(name, (0, 0))[1]) * k, "rotation": la + tu.get(name, 0)}[prop]
                    k_ = {"t": round(t, 4), "v": round(v, 5)}
                    if ease: k_["ease"] = ease
                    ks.append(k_)
                ks[-1].pop("ease", None)
                tracks.append({"target": name, "property": prop, "keys": ks})
        return tracks

def bleed(im):
    px = im.load(); w, h = im.size
    for _ in range(2):
        fill = []
        for y in range(h):
            for x in range(w):
                if px[x, y][3] == 0:
                    near = [px[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] > 0]
                    if near: fill.append((x, y, tuple(sum(c[i] for c in near) // len(near) for i in range(3))))
        for x, y, c in fill: px[x, y] = c + (0,)
    return im

def nearest_along(points, x, y):
    """Where (x, y) is nearest along a polyline: segment index + fraction."""
    best, at = None, 0
    for i in range(len(points) - 1):
        (ax, ay), (bx, by) = points[i], points[i + 1]
        vx, vy = bx - ax, by - ay
        t = max(0, min(1, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
        d = (ax + vx * t - x) ** 2 + (ay + vy * t - y) ** 2
        if best is None or d < best: best, at = d, i + t
    return at

def chain_weigh(points, names):
    """Weights for a mesh along a polyline whose segments are the named bones: each bone weighs most at its middle, blending into its neighbors."""
    def weigh(x, y):
        at = nearest_along(points, x, y)
        ws = {}
        for i, nm in enumerate(names):
            w = max(0.0, 1 - abs(at - (i + 0.5)))
            if w > 0: ws[nm] = ws.get(nm, 0) + w
        if not ws: ws[names[0 if at < 1 else -1]] = 1
        return ws
    return weigh
