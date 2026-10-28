"""A dinosaur for the skeletons demo as separate SVG parts on one rig, in three styles.
World pixels: ground at y=0, facing right, standing. Each part is one closed shape; the joints are where bones meet."""
import math, sys, json

def cr(points, closed=True, tension=0.5):
    """A smooth path through points (Catmull-Rom as cubic Beziers)."""
    n = len(points); p = points
    d = "M %.1f %.1f " % p[0]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = p[(i - 1) % n] if closed or i > 0 else p[0]
        p1, p2 = p[i], p[(i + 1) % n]
        p3 = p[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        d += "C %.1f %.1f %.1f %.1f %.1f %.1f " % (c1 + c2 + p2)
    return d + ("Z" if closed else "")

def poly(points): return "M " + " L ".join("%.1f %.1f" % q for q in points) + " Z"

def limb_pts(a, b, wa, wb, steps=5):
    """Outline of a tapered limb from a to b (widths at each end), round at both ends."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); nx, ny = -math.sin(ang), math.cos(ang)
    pts = []
    for k in range(steps + 1):  # around the b end
        t = -math.pi / 2 + math.pi * k / steps
        pts.append((b[0] + wb / 2 * (math.cos(ang + t)), b[1] + wb / 2 * math.sin(ang + t)))
    for k in range(steps + 1):  # around the a end
        t = math.pi / 2 + math.pi * k / steps
        pts.append((a[0] + wa / 2 * (math.cos(ang + t)), a[1] + wa / 2 * math.sin(ang + t)))
    return pts

# ── the rig (near side; the far side is shifted back and drawn behind) ──
HIP, KNEE, ANKLE, BALL = (0, -112), (18, -70), (-6, -38), (6, -9)
SHOULDER, ELBOW, HAND = (56, -122), (68, -104), (82, -108)
NECK, JAWPIN = (78, -176), (80, -186)
FAR = (22, -2)
def off(p, o): return (p[0] + o[0], p[1] + o[1])

def shapes():
    s = {}
    s["body"] = [(-52, -146), (-20, -162), (18, -160), (44, -150), (58, -166), (66, -186), (92, -190), (96, -166), (78, -128),
                 (56, -100), (16, -84), (-28, -88), (-56, -108)]
    s["tail"] = [(-40, -150), (-82, -146), (-122, -132), (-150, -116), (-124, -112), (-86, -108), (-44, -100)]
    s["head"] = [(62, -206), (80, -226), (112, -228), (140, -214), (152, -200), (146, -190), (108, -188), (76, -184), (60, -192)]
    s["jaw"] = [(74, -188), (106, -188), (142, -189), (138, -177), (108, -171), (80, -174)]
    for side, o in (("far", FAR), ("near", (0, 0))):
        h, k, a, b = (off(q, o) for q in (HIP, KNEE, ANKLE, BALL))
        s["thigh_" + side] = limb_pts(h, k, 42, 24)
        s["shin_" + side] = limb_pts(k, a, 20, 13)
        # Foot: the metatarsal from the ankle down to the ball, then toes flat along the ground.
        g = o[1]  # the far foot stands on the same ground
        s["foot_" + side] = [(a[0] - 6, a[1] - 1), (a[0] + 6, a[1] - 1), (b[0] + 6, -15), (b[0] + 18, -16), (b[0] + 36, -9),
                             (b[0] + 40, 0), (b[0] - 12, 0), (b[0] - 10, -10)]
        sh, el, ha = (off(q, o) for q in (SHOULDER, ELBOW, HAND))
        s["upperarm_" + side] = limb_pts(sh, el, 13, 10)
        s["forearm_" + side] = limb_pts(el, ha, 10, 7) + [(ha[0] + 6, ha[1] + 2), (ha[0] + 9, ha[1] + 7), (ha[0] + 3, ha[1] + 4)]
    return s

ORDER = ["thigh_far", "shin_far", "foot_far", "upperarm_far", "forearm_far", "tail", "body", "jaw", "head",
         "thigh_near", "shin_near", "foot_near", "upperarm_near", "forearm_near"]
ROUND = {"body", "tail", "head", "jaw"}  # smooth outlines; limbs are already rounded polygons

STYLES = {
    "A": {"name": "Cartoon", "fill": "#6cc24a", "far": "#4f9a39", "line": "#1f3b1a", "width": 3, "belly": "#f3e6a6", "spot": "#4e9a35", "eye": True, "smooth": True},
    "B": {"name": "Faceted", "fill": "#f08a3c", "far": "#c4672a", "line": "#5a2a10", "width": 2.5, "belly": "#f7c27c", "spot": None, "eye": True, "smooth": False},
    "D": {"name": "Cartoon, orange", "fill": "#f08a3c", "far": "#c4672a", "line": "#5a2a10", "width": 3, "belly": "#f7c27c", "spot": "#d06a24", "eye": True, "smooth": True},
    "C": {"name": "Soft", "fill": "url(#gradC)", "far": "url(#gradCfar)", "line": None, "width": 0, "belly": "#c9c2ff", "spot": "#b3a9ff", "eye": True, "smooth": True},
}

def part_path(name, pts, st):
    if st["smooth"] and name in ROUND: return cr(pts)
    if not st["smooth"]:
        return poly(pts if name not in ROUND else pts)
    return cr(pts, tension=0.35)

def gradient_defs(key):
    if key != "C": return ""
    return ('<linearGradient id="gradC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a69bff"/><stop offset="1" stop-color="#5544c8"/></linearGradient>'
            '<linearGradient id="gradCfar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d72d0"/><stop offset="1" stop-color="#3d3290"/></linearGradient>')

def part_svg(key, name):
    """One part of the dinosaur in style `key`, in world pixels."""
    st = STYLES[key]; s = shapes(); out = []
    d = part_path(name, s[name], st)
    fill = st["far"] if name.endswith("_far") else st["fill"]
    stroke = ' stroke="%s" stroke-width="%g" stroke-linejoin="%s"' % (st["line"], st["width"], "round" if st["smooth"] else "miter") if st["line"] else ""
    cid = "clip%s_%s" % (key, name)
    out.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    out.append('<path d="%s" fill="%s"/>' % (d, fill))
    g = '<g clip-path="url(#%s)">' % cid
    if name == "body":
        belly = [(40, -150), (100, -175), (100, -80), (-30, -80), (-40, -98), (14, -98), (54, -116), (74, -146)]
        g += '<path d="%s" fill="%s"/>' % (cr(belly) if st["smooth"] else poly(belly), st["belly"])
        if st["spot"]:
            for (cx, cy, r) in [(-22, -146, 7), (2, -150, 5), (-38, -134, 5), (22, -144, 4)]:
                g += '<circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (cx, cy, r, st["spot"])
    if name == "tail" and st["spot"]:
        for (cx, cy, r) in [(-70, -138, 5), (-98, -130, 4), (-122, -121, 3)]:
            g += '<circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (cx, cy, r, st["spot"])
    g += "</g>"
    out.append(g)
    if st["line"]:
        if name == "body":
            # No outline where the body lies over the tail: the two read as one, with no seam at the join.
            tail = part_path("tail", s["tail"], st)
            mid = "seam%s" % key
            out.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-400" y="-500" width="800" height="800"><rect x="-400" y="-500" width="800" height="800" fill="#fff"/><path d="%s" fill="#000"/></mask>' % (mid, tail))
            out.append('<path d="%s" fill="none"%s mask="url(#%s)"/>' % (d, stroke, mid))
        elif name == "head":
            # No outline where the head covers the back of the jaw: the mouth line shows only toward the front, where it opens.
            jaw = part_path("jaw", s["jaw"], st)
            mid = "cheek%s" % key
            # Faded in from black (hidden) at the hinge to white (shown) along the mouth, so the line tapers in from nothing.
            out.append('<linearGradient id="%sfade" gradientUnits="userSpaceOnUse" x1="90" y1="0" x2="112" y2="0"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>' % mid)
            out.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-400" y="-500" width="800" height="800"><rect x="-400" y="-500" width="800" height="800" fill="#fff"/><path d="%s" fill="url(#%sfade)"/></mask>' % (mid, jaw, mid))
            out.append('<path d="%s" fill="none"%s mask="url(#%s)"/>' % (d, stroke, mid))
        else:
            out.append('<path d="%s" fill="none"%s/>' % (d, stroke))
    if name == "head":
        out.append('<circle cx="110" cy="-208" r="8" fill="#fff"%s/>' % (' stroke="%s" stroke-width="2"' % st["line"] if st["line"] else ""))
        out.append('<circle cx="112.5" cy="-207.5" r="4" fill="#1a1a2a"/>')
        out.append('<circle cx="142" cy="-204" r="2.2" fill="%s"/>' % (st["line"] or "#3d3290"))
        if key in ("A", "D"):
            for tx in (114, 123, 132):
                out.append('<path d="M %d -188.5 l 3 5 l 3 -5 Z" fill="#fff" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % (tx, st["line"]))
    return gradient_defs(key) + "".join(out)

def svg_dino(key, x0=0, y0=0, show_joints=False):
    out = ['<g transform="translate(%g %g)">' % (x0, y0)] + [part_svg(key, name) for name in ORDER]
    if show_joints:
        for p in (HIP, KNEE, ANKLE, BALL, SHOULDER, ELBOW, HAND, NECK, JAWPIN):
            out.append('<circle cx="%g" cy="%g" r="2.5" fill="#e33"/>' % p)
    out.append("</g>")
    return "", "".join(out)

def single(key, path):
    d, b = svg_dino(key, 200, 270)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="420" height="300" viewBox="0 0 420 300"><rect width="100%%" height="100%%" fill="#eef3f0"/><defs>%s</defs>%s<line x1="10" y1="270" x2="410" y2="270" stroke="#8a8" stroke-width="2"/></svg>' % (d, b)
    open(path, "w").write(svg)

if __name__ == "__main__" and len(sys.argv) > 2:
    single(sys.argv[2], sys.argv[1]); sys.exit()
if __name__ == "__main__":
    W, H = 1260, 330
    defs_all, body_all = "", ""
    for i, key in enumerate("ABC"):
        d, b = svg_dino(key, 230 + i * 410, 270)
        defs_all += d; body_all += b
        body_all += '<text x="%d" y="315" font-family="sans-serif" font-size="20" fill="#333" text-anchor="middle">%s  %s</text>' % (190 + i * 410, key, STYLES[key]["name"])
        body_all += '<line x1="%d" y1="270" x2="%d" y2="270" stroke="#8a8" stroke-width="2"/>' % (20 + i * 410, 380 + i * 410)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#eef3f0"/><defs>%s</defs>%s</svg>' % (W, H, W, H, defs_all, body_all)
    open(sys.argv[1], "w").write(svg)
