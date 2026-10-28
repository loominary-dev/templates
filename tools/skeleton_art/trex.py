"""A T-rex for the skeletons demo, as separate SVG parts on one rig: olive with darker stripes, a tan belly and a dark
outline, after the user's reference sheet (2026-10-28). The same parts and bones as the dinosaur (dino.py), so its walk
and run fit it. World pixels: ground at y=0, facing right, standing."""
import math, sys
from dino import cr, limb_pts

# ── the rig (near side; the far side is shifted back and drawn behind) ──
HIP, KNEE, ANKLE, BALL = (0, -118), (22, -74), (-4, -38), (8, -10)
SHOULDER, ELBOW, HAND = (66, -134), (74, -118), (88, -116)
NECK, JAWPIN = (78, -170), (100, -190)
FAR = (20, -2)
def off(p, o): return (p[0] + o[0], p[1] + o[1])

# The spine the body and tail bend along, tail tip to the back of the head.
TAIL = [(-30, -150), (-80, -148), (-130, -140), (-178, -128)]
SPINE = [(-30, -150), (0, -150), (60, -152), (78, -170), (96, -188)]
HEAD_TIP, JAW_TIP = (178, -204), (166, -184)

FILL, FAR_FILL, LINE, BELLY, STRIPE = "#8aa646", "#677f33", "#25261a", "#d1b27a", "#55702a"

def shapes():
    s = {}
    # Body with its neck: a deep chest, the back rising to the shoulders, the neck curving up to the skull.
    s["body"] = [(-54, -150), (-30, -166), (10, -172), (48, -170), (70, -178), (82, -196), (104, -202), (110, -184),
                 (98, -164), (92, -140), (78, -112), (44, -96), (6, -92), (-30, -100), (-56, -122)]
    # Tail: thick at the hips, tapering to a point, held level.
    s["tail"] = [(-20, -160), (-50, -162), (-90, -156), (-140, -146), (-196, -130), (-142, -124), (-90, -118), (-50, -110), (-20, -106)]
    # Skull: a long deep head, brow ridge over the eye, a blunt snout; the upper teeth hang below its edge.
    s["head"] = [(88, -206), (100, -224), (124, -232), (150, -228), (172, -216), (182, -202), (178, -192), (150, -192),
                 (122, -190), (100, -186), (88, -194)]
    # Lower jaw: hinged under the eye, its teeth pointing up.
    s["jaw"] = [(92, -190), (122, -188), (150, -188), (170, -188), (168, -178), (146, -172), (116, -172), (96, -178)]
    for side, o in (("far", FAR), ("near", (0, 0))):
        h, k, a, b = (off(q, o) for q in (HIP, KNEE, ANKLE, BALL))
        # The thigh: a great drumstick, deepest just below the hip.
        s["thigh_" + side] = limb_pts(h, k, 58, 28, steps=7)
        s["shin_" + side] = limb_pts(k, a, 26, 16)
        # Foot: the long metatarsal down to the ball, then three toes along the ground, each with a claw.
        s["foot_" + side] = [(a[0] - 7, a[1] - 1), (a[0] + 7, a[1] - 2), (b[0] + 7, -16), (b[0] + 20, -15), (b[0] + 38, -9),
                             (b[0] + 44, -1), (b[0] + 40, 1), (b[0] + 18, 0), (b[0] - 12, 0), (b[0] - 10, -10)]
        sh, el, ha = (off(q, o) for q in (SHOULDER, ELBOW, HAND))
        s["upperarm_" + side] = limb_pts(sh, el, 12, 9)
        s["forearm_" + side] = limb_pts(el, ha, 9, 7)
    return s

ORDER = ["thigh_far", "shin_far", "foot_far", "upperarm_far", "forearm_far", "tail", "body", "jaw", "head",
         "thigh_near", "shin_near", "foot_near", "upperarm_near", "forearm_near"]
ROUND = {"body", "tail", "head", "jaw"}

def stripes(x0, x1, top, bottom, every, slant, width):
    """Darker bands across the back, slanting back toward the tail."""
    out = ""
    x = x0
    while x < x1:
        out += '<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>' % (
            x, top, x + width, top, x + width - slant, bottom, x - slant, bottom, STRIPE)
        x += every
    return out

def teeth(xs, y, down, size=6):
    d = 1 if down else -1
    return "".join('<path d="M %.1f %.1f l %.1f %.1f l %.1f %.1f Z" fill="#f6efd8" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % (
        x, y, size / 2, d * size * 1.4, size / 2, -d * size * 1.4, LINE) for x in xs)

def claw(x, y, size=6):
    return '<path d="M %.1f %.1f q %.1f %.1f %.1f %.1f q %.1f %.1f %.1f %.1f Z" fill="#3a3324" stroke="%s" stroke-width="1"/>' % (
        x, y, size, 0, size * 1.4, size * 0.9, -size * 0.6, -size * 0.2, -size * 1.4, -size * 0.9, LINE)

def part_svg(key, name):
    """One part of the T-rex, in world pixels. `key` is unused: one style."""
    s = shapes()
    pts = s[name]
    d = cr(pts) if name in ROUND else cr(pts, tension=0.35)
    fill = FAR_FILL if name.endswith("_far") else FILL
    stroke = ' stroke="%s" stroke-width="3" stroke-linejoin="round"' % LINE
    cid = "clipT_" + name
    out = ['<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d), '<path d="%s" fill="%s"/>' % (d, fill)]
    g = '<g clip-path="url(#%s)">' % cid
    far = name.endswith("_far")
    if name == "body":
        g += '<path d="%s" fill="%s"/>' % (cr([(110, -170), (110, -80), (-40, -80), (-50, -104), (0, -106), (52, -118), (84, -150)]), BELLY)
        g += stripes(-40, 70, -180, -128, 22, 10, 9)
    elif name == "tail":
        g += '<path d="%s" fill="%s"/>' % (cr([(-40, -122), (-120, -134), (-200, -128), (-200, -100), (-40, -96)]), BELLY)
        g += stripes(-180, -40, -170, -134, 20, 8, 7)
    elif name == "head":
        g += '<path d="%s" fill="%s"/>' % (cr([(98, -200), (140, -200), (184, -204), (184, -180), (90, -180)]), BELLY)
        g += stripes(96, 130, -240, -214, 14, 6, 5)
    elif name == "jaw":
        g += '<path d="%s" fill="%s"/>' % (cr([(90, -182), (172, -184), (172, -160), (90, -160)]), BELLY)
    elif name.startswith("thigh"):
        h, k = off(HIP, FAR if far else (0, 0)), off(KNEE, FAR if far else (0, 0))
        g += stripes(h[0] - 30, h[0] + 30, h[1] - 30, h[1] + 30, 16, -12, 6).replace(STRIPE, "#4c6324" if far else STRIPE)
    g += "</g>"
    out.append(g)
    if name == "body":
        # No outline where the body lies over the tail: the two read as one, with no seam at the join.
        tail = cr(s["tail"])
        out.append('<mask id="seamT" maskUnits="userSpaceOnUse" x="-400" y="-500" width="800" height="800"><rect x="-400" y="-500" width="800" height="800" fill="#fff"/><path d="%s" fill="#000"/></mask>' % tail)
        out.append('<path d="%s" fill="none"%s mask="url(#seamT)"/>' % (d, stroke))
    else:
        out.append('<path d="%s" fill="none"%s/>' % (d, stroke))
    if name == "head":
        # Brow ridge, eye, nostril, the upper teeth.
        out.append('<path d="M 112 -222 q 12 -8 26 -2" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % LINE)
        out.append('<ellipse cx="124" cy="-213" rx="7" ry="5.5" fill="#f2c230" stroke="%s" stroke-width="2"/>' % LINE)
        out.append('<ellipse cx="125" cy="-213" rx="1.8" ry="4.2" fill="#1a1a14"/>')
        out.append('<ellipse cx="172" cy="-212" rx="3" ry="1.8" fill="%s"/>' % LINE)
        out.append(teeth([120, 130, 140, 150, 160, 168], -191, True))
    if name == "jaw":
        out.append(teeth([124, 134, 144, 154, 162], -186, False, size=5))
    if name.startswith("foot"):
        o = FAR if far else (0, 0)
        b = off(BALL, o)
        for cx, cy in ((b[0] + 40, -6), (b[0] + 30, -3), (b[0] + 19, -2)):
            out.append(claw(cx, cy))
    if name.startswith("forearm"):
        o = FAR if far else (0, 0)
        ha = off(HAND, o)
        out.append(claw(ha[0] + 2, ha[1] - 1, 4) + claw(ha[0], ha[1] + 2, 4))
    return "".join(out)

def single(path, show_joints=False):
    body = "".join(part_svg("T", n) for n in ORDER)
    if show_joints:
        for p in (HIP, KNEE, ANKLE, BALL, SHOULDER, ELBOW, HAND, NECK, JAWPIN):
            body += '<circle cx="%g" cy="%g" r="2.5" fill="#e33"/>' % p
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="300" viewBox="-240 -260 480 300">'
           '<rect x="-240" y="-260" width="480" height="300" fill="#b9d8ef"/><rect x="-240" y="0" width="480" height="40" fill="#7aaa56"/>%s</svg>' % body)
    open(path, "w").write(svg)

if __name__ == "__main__":
    single(sys.argv[1], len(sys.argv) > 2)
