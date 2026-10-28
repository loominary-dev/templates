"""The dapper skeleton as separate parts, each on its bone: the SVG of each part in world pixels (ground y=0, front view),
the bones (base, tip, parent), rendering each part to a PNG with its pivot, and posing the whole from bone turns."""
import math, sys, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skel import bone, limb, B, L
from dino import cr

HIP_Y, KNEE_Y, ANK_Y, TOP = -78, -42, -10, -138
def side_pts(sx):
    return dict(hip=(sx * 12, HIP_Y), knee=(sx * 13, KNEE_Y), ank=(sx * 13, ANK_Y), sh=(sx * 34, TOP + 4), el=(sx * 42, TOP + 31), wr=(sx * 46, TOP + 57))

# Bones: name, parent, base, tip. The root is the pelvis.
BONES = [("Pelvis", None, (0, HIP_Y), (0, HIP_Y - 6)), ("Spine", "Pelvis", (0, HIP_Y - 6), (0, TOP)), ("Head", "Spine", (0, TOP - 2), (0, TOP - 52)),
         ("Hat", "Head", (0, TOP - 52), (0, TOP - 84))]
for side, sx in (("L", -1), ("R", 1)):
    p = side_pts(sx)
    BONES += [("Thigh" + side, "Pelvis", p["hip"], p["knee"]), ("Shin" + side, "Thigh" + side, p["knee"], p["ank"]),
              ("Foot" + side, "Shin" + side, p["ank"], (p["ank"][0] + sx * 18, 0)),
              ("UpperArm" + side, "Spine", p["sh"], p["el"]), ("Forearm" + side, "UpperArm" + side, p["el"], p["wr"])]
BONE = {b[0]: b for b in BONES}

def part_svg(name):
    """One part's SVG in world pixels."""
    if name.startswith(("Thigh", "Shin", "UpperArm")):
        _, _, a, b = BONE[name]
        return bone(a, b, {"Thigh": 11, "Shin": 10, "UpperArm": 9}[name.rstrip("LR")])
    if name.startswith("Forearm"):
        _, _, a, b = BONE[name]; sx = -1 if name.endswith("L") else 1
        out = bone(a, b, 8)
        for k in range(3):
            out += limb((b[0], b[1] + 3), (b[0] + sx * (k - 1) * 4.5, b[1] + 15), 4.2, 3.2, 2)
        return out
    if name.startswith("Foot"):
        sx = -1 if name.endswith("L") else 1; ank = BONE[name][2]
        return '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
            cr([(ank[0] - 8 * sx, -11), (ank[0] + sx * 14, -10), (ank[0] + sx * 19, -3), (ank[0] + sx * 18, 0), (ank[0] - 9 * sx, 0)], tension=0.4), B, L)
    if name == "Pelvis":
        return '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (cr([(-24, HIP_Y - 8), (24, HIP_Y - 8), (18, HIP_Y + 8), (0, HIP_Y + 2), (-18, HIP_Y + 8)], tension=0.4), B, L)
    if name == "Spine":
        out = limb((0, HIP_Y - 6), (0, TOP), 7, 7)
        for k in range(3):
            y = TOP + 8 + k * 12; w = 24 - k * 3
            for s in (1, -1):
                out += '<path d="M 0 %g q %g 3 %g 13" fill="none" stroke="%s" stroke-width="7.4" stroke-linecap="round"/>' % (y, s * w, s * (w - 4), L)
                out += '<path d="M 0 %g q %g 3 %g 13" fill="none" stroke="%s" stroke-width="3.8" stroke-linecap="round"/>' % (y, s * w, s * (w - 4), B)
        out += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (cr([(-34, TOP + 2), (34, TOP + 2), (26, TOP + 8), (-26, TOP + 8)], tension=0.3), B, L)
        y = TOP + 1
        out += '<path d="M 0 %g l -11 -6 l 0 12 Z M 0 %g l 11 -6 l 0 12 Z" fill="#c0392b" stroke="%s" stroke-width="2" stroke-linejoin="round"/><circle cx="0" cy="%g" r="3.4" fill="#a02a1e" stroke="%s" stroke-width="1.6"/>' % (y, y, L, y, L)
        return out
    if name == "Head":
        n = TOP - 2
        out = '<g transform="translate(0 %g)">' % n + limb((0, 0), (0, -8), 7, 7)
        out += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.8" stroke-linejoin="round"/>' % (cr([(-23, -30), (-15, -52), (15, -52), (23, -30), (17, -10), (11, -5), (-11, -5), (-17, -10)], tension=0.5), B, L)
        out += '<ellipse cx="-8.5" cy="-28" rx="6.5" ry="7.5" fill="%s"/><ellipse cx="8.5" cy="-28" rx="6.5" ry="7.5" fill="%s"/><path d="M 0 -19 l -2.6 5 l 5.2 0 Z" fill="%s"/>' % (L, L, L)
        out += "".join('<line x1="%g" y1="-11" x2="%g" y2="-6" stroke="%s" stroke-width="1.6"/>' % (x, x, L) for x in (-6, -2, 2, 6))
        out += '<circle cx="-6.5" cy="-30" r="1.8" fill="#fff"/><circle cx="10.5" cy="-30" r="1.8" fill="#fff"/></g>'
        return out
    if name == "Hat":
        n = TOP - 2
        return ('<g transform="translate(0 %g)"><rect x="-26" y="-55" width="52" height="7" rx="3" fill="#2c2c34" stroke="%s" stroke-width="2.4"/>'
                '<rect x="-16" y="-84" width="32" height="31" rx="3" fill="#2c2c34" stroke="%s" stroke-width="2.4"/>'
                '<rect x="-16" y="-62" width="32" height="6" fill="#c0392b"/></g>') % (n, L, L)
    raise KeyError(name)

DRAW = ["ThighL", "ShinL", "FootL", "ThighR", "ShinR", "FootR", "Pelvis", "Spine", "UpperArmL", "ForearmL", "UpperArmR", "ForearmR", "Head", "Hat"]
SCALE = 2  # pictures at twice the drawn size, shown at half: crisp on high-density screens

def render_parts(outdir, node):
    """Each part to <outdir>/<name>.png, cropped to its pixels; returns {name: {"w","h","x","y"}} where x, y is the world place of the picture's top-left."""
    os.makedirs(outdir, exist_ok=True)
    X0, Y0, WW, HH = -120, -260, 240, 270
    info = {}
    for name in DRAW:
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%d %d %d %d">%s</svg>' % (WW * SCALE, HH * SCALE, X0, Y0, WW, HH, part_svg(name))
        f = os.path.join(outdir, name + ".svg"); open(f, "w").write(svg)
        png = os.path.join(outdir, name + ".full.png")
        subprocess.run([node, os.path.join(os.path.dirname(os.path.abspath(__file__)), "render.mjs"), f, png, "1"], check=True)
        from PIL import Image
        im = Image.open(png); bb = im.getbbox(); im = im.crop(bb); im.save(os.path.join(outdir, name + ".png")); os.remove(png)
        info[name] = {"w": im.width, "h": im.height, "x": X0 + bb[0] / SCALE, "y": Y0 + bb[1] / SCALE}
    json.dump(info, open(os.path.join(outdir, "parts.json"), "w"), indent=1)
    return info

def rest_angle(name):
    _, _, a, b = BONE[name]
    return math.atan2(b[1] - a[1], b[0] - a[0])

def world_poses(turns, offsets=None):
    """Each bone's world base and angle when each bone is turned by turns[name] radians from rest (and its base moved by offsets[name])."""
    offsets = offsets or {}
    out = {}
    for name, parent, base, tip in BONES:
        local_rest = rest_angle(name) - (rest_angle(parent) if parent else 0)
        if parent is None:
            off = offsets.get(name, (0, 0))
            out[name] = ((base[0] + off[0], base[1] + off[1]), rest_angle(name) + turns.get(name, 0))
            continue
        pb, pa = out[parent]
        # The base's place in the parent's rest frame, carried by the parent's present pose.
        _, _, ppb, _ = BONE[parent]
        dx, dy = base[0] - ppb[0], base[1] - ppb[1]
        ra = -rest_angle(parent); lx, ly = dx * math.cos(ra) - dy * math.sin(ra), dx * math.sin(ra) + dy * math.cos(ra)
        off = offsets.get(name, (0, 0)); lx += off[0]; ly += off[1]
        wx, wy = pb[0] + lx * math.cos(pa) - ly * math.sin(pa), pb[1] + lx * math.sin(pa) + ly * math.cos(pa)
        out[name] = ((wx, wy), pa + local_rest + turns.get(name, 0))
    return out
