"""Three trees for the skeletons demo, in the dinosaur's cartoon style: the wood one picture (outline drawn once round the union of its limbs), leaves separate."""
import math, sys
sys.path.insert(0, sys.argv[2] if len(sys.argv) > 2 else ".")
from dino import cr, limb_pts
LINE, W = "#5a2a10", 3

def wood(limbs, fill="#a8693a", shade="#8b5530"):
    """Limbs (a, b, wa, wb): the outline of their union: every limb stroked thick first, then every fill on top."""
    paths = [cr(limb_pts(a, b, wa, wb, 6), tension=0.35) for a, b, wa, wb in limbs]
    out = "".join('<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (p, LINE, LINE, W * 2) for p in paths)
    out += "".join('<path d="%s" fill="%s"/>' % (p, fill) for p in paths)
    return '<g clip-path="url(#ground)">%s</g>' % out

def leaf(at, ang, size, fill="#7cc24e", vein="#4e8f2e"):
    """A pointed leaf with its stalk at `at`, pointing along ang (degrees)."""
    L, Wd = size, size * 0.45
    pts = [(0, 0), (L * 0.3, -Wd / 2), (L * 0.75, -Wd / 2.6), (L, 0), (L * 0.75, Wd / 2.6), (L * 0.3, Wd / 2)]
    d = cr(pts, tension=0.5)
    return ('<g transform="translate(%g %g) rotate(%g)"><path d="%s" fill="%s" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
            '<path d="M %g 0 L %g 0" stroke="%s" stroke-width="1.6" stroke-linecap="round"/></g>') % (at[0], at[1], ang, d, fill, LINE, L * 0.12, L * 0.82, vein)

def tree1():
    T = [((0, 0), (0, -110), 34, 22), ((0, -100), (-58, -160), 16, 9), ((-34, -134), (-44, -190), 9, 5), ((0, -108), (8, -205), 16, 7),
         ((2, -120), (66, -168), 14, 7), ((42, -150), (88, -150), 7, 4), ((-6, -20), (-30, 4), 18, 12), ((6, -20), (32, 4), 18, 12)]
    out = wood(T)
    for at, ang, sz in [((-58, -160), -150, 42), ((-44, -190), -105, 38), ((8, -205), -80, 42), ((66, -168), -40, 40), ((88, -150), 10, 36),
                        ((-20, -150), -170, 30), ((30, -150), -60, 30)]:
        out += leaf(at, ang, sz)
    return out

def tree2():
    # A palm: the trunk a curve of stacked rings, five fronds from the top.
    out = ""
    pts = [(0, 0), (6, -50), (18, -100), (34, -150), (44, -190)]
    segs = []
    for i in range(len(pts) - 1):
        segs.append((pts[i], pts[i + 1], 30 - i * 4, 26 - i * 4))
    out += wood(segs, fill="#b8803e")
    for i in range(1, 8):
        t = i / 8
        x = 0 + (44 - 0) * t ** 1.3; y = -190 * t
        out += '<path d="M %g %g q 10 4 20 0" stroke="%s" stroke-width="2" fill="none" stroke-linecap="round" transform="translate(-10 0)"/>' % (x, y, LINE)
    top = (44, -192)
    for side, ang, L in [(-1, 5, 120), (-1, 50, 96), (1, 5, 124), (1, 50, 98), (1, 85, 60)]:
        # Out and up, then down to the tip: a spine of three points, the frond widest a third along.
        if side == 0:
            spine = [top, (top[0] + 4, top[1] - 26), (top[0] + 10, top[1] - 46)]
        else:
            r = math.radians(ang)
            spine = [top, (top[0] + side * L * 0.45 * math.cos(r), top[1] - L * 0.35 * math.sin(r) - 22),
                     (top[0] + side * L * math.cos(r), top[1] - L * 0.2 * math.sin(r) + 22)]
        # Sampled along the spine (a quadratic through its middle point), widest a third of the way.
        (x0, y0), (x1, y1), (x2, y2) = spine
        cx, cy = 2 * x1 - (x0 + x2) / 2, 2 * y1 - (y0 + y2) / 2
        q = lambda t: ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x2, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y2)
        left, right, mids = [], [], []
        for k in range(13):
            t = k / 12; px, py = q(t); ax, ay = q(min(1, t + 0.01)); bx, by = q(max(0, t - 0.01))
            nx, ny = -(ay - by), ax - bx; n = math.hypot(nx, ny) or 1
            w = 11 * math.sin(math.pi * min(1, t * 1.3)) ** 0.7 if t < 0.77 else 11 * (1 - t) / 0.23 * 0.75
            left.append((px + nx / n * w, py + ny / n * w)); right.append((px - nx / n * w, py - ny / n * w)); mids.append((px, py))
        outline = left + list(reversed(right))
        out += '<path d="%s" fill="#6fb648" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (cr(outline, tension=0.5), LINE)
        out += '<path d="%s" fill="none" stroke="#4e8f2e" stroke-width="1.8" stroke-linecap="round"/>' % cr(mids, closed=False)
    out += '<circle cx="40" cy="-186" r="7" fill="#8a5a2a" stroke="%s" stroke-width="2"/><circle cx="50" cy="-183" r="6" fill="#8a5a2a" stroke="%s" stroke-width="2"/>' % (LINE, LINE)
    return out

def tree3():
    T = [((0, 0), (0, -120), 36, 24), ((0, -112), (-50, -170), 15, 9), ((-50, -170), (-82, -160), 9, 6), ((0, -112), (54, -172), 15, 9),
         ((54, -172), (86, -160), 9, 6), ((0, -118), (4, -196), 13, 8), ((-6, -18), (-30, 4), 18, 12), ((6, -18), (30, 4), 18, 12)]
    out = ""
    for x0, y0, L in [(-82, -160, 96), (-54, -168, 112), (-22, -150, 80), (4, -196, 120), (30, -158, 86), (58, -170, 110), (86, -160, 94)]:
        strand = [(x0, y0), (x0 - 3, y0 + L * 0.35), (x0 + 1, y0 + L * 0.7), (x0 - 2, y0 + L)]
        out += '<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % (cr(strand, closed=False), LINE)
        out += '<path d="%s" fill="none" stroke="#86b24e" stroke-width="3" stroke-linecap="round"/>' % cr(strand, closed=False)
        for j in range(3):
            lx, ly = strand[j + 1]
            out += leaf((lx, ly), 75 if j % 2 else 105, 20, fill="#9ccc5a")
    return wood(T, fill="#9a6a44") + out

if __name__ == "__main__":
    Wd, Ht = 1260, 330
    body = ""
    for i, (fn, name) in enumerate([(tree1, "1  Branching"), (tree2, "2  Palm"), (tree3, "3  Willow")]):
        cx = 210 + i * 420
        body += '<g transform="translate(%d 270)">%s</g>' % (cx, fn())
        body += '<line x1="%d" y1="270" x2="%d" y2="270" stroke="#8a8" stroke-width="2"/>' % (cx - 180, cx + 180)
        body += '<text x="%d" y="315" font-family="sans-serif" font-size="20" fill="#333" text-anchor="middle">%s</text>' % (cx, name)
    open(sys.argv[1], "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#eef3f0"/><defs><clipPath id="ground"><rect x="-400" y="-400" width="800" height="400"/></clipPath></defs>%s</svg>' % (Wd, Ht, Wd, Ht, body))
