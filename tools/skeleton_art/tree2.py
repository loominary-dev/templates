"""The branching tree, fuller: a trunk, main branches each splitting in two or three, and leaf clumps at the ends, balanced left and right."""
import math, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from tree import wood, leaf, LINE
from dino import cr

def branch(p, ang, length, width, depth, out_limbs, tips):
    """A branch from p at ang (degrees, 0 = right, -90 = up), splitting until depth runs out."""
    a = math.radians(ang)
    q = (p[0] + length * math.cos(a), p[1] + length * math.sin(a))
    out_limbs.append((p, q, width, width * 0.62))
    if depth == 0:
        tips.append((q, ang)); return
    spread = 26 if depth > 1 else 30
    # Two children, and a third straight on for the outer forks.
    # Forks lean upward: the lower child turns less, so no clump hangs below the crown.
    up, down = (-spread, spread * 0.55) if math.cos(a) > 0 else (-spread * 0.55, spread)
    for d_ang, frac in ((up, 0.72), (down, 0.66)):
        branch(q, ang + d_ang, length * frac, width * 0.62, depth - 1, out_limbs, tips)

def tree():
    limbs, tips = [], []
    # Roots and trunk.
    limbs += [((0, 0), (0, -120), 40, 26), ((-6, -20), (-34, 6), 20, 13), ((6, -20), (36, 6), 20, 13)]
    # Five main branches, mirrored in angle, from the top of the trunk.
    for start, ang, L, w in [((0, -100), -150, 94, 17), ((0, -114), -122, 100, 16), ((0, -122), -90, 92, 16),
                             ((0, -114), -58, 100, 16), ((0, -100), -30, 94, 17)]:
        branch(start, ang, L, w, 2 if abs(ang + 90) > 10 else 1, limbs, tips)
    return limbs, tips

def fan(at, ang, n=6, size=30, greens=("#7cc24e", "#5fae3c")):
    """Leaves spreading from one point around the branch's direction."""
    out = ""
    for k in range(n):
        a = ang + (k - (n - 1) / 2) * (150 / (n - 1))
        out += leaf(at, a, size * (0.85 + 0.15 * (k % 2)), fill=greens[k % 2])
    return out

def cluster(at, ang, r=30, greens=("#7cc24e", "#5fae3c", "#93d164")):
    """A round bunch: leaves pointing out from a center a little beyond the tip, back ones darker."""
    a = math.radians(ang)
    c = (at[0] + r * 0.55 * math.cos(a), at[1] + r * 0.55 * math.sin(a))
    out = ""
    outer = 5 if r < 26 else 6 if r < 33 else 7
    for ring, (count, dist, size, g) in enumerate(((outer, r * 0.6, r * 0.85, greens[1]), (outer - 2, r * 0.3, r * 0.8, greens[0]), (2, 0, r * 0.7, greens[2]))):
        for k in range(count):
            la = k * 360 / count + ring * 20 + ang
            lr = math.radians(la)
            base = (c[0] + dist * 0.4 * math.cos(lr), c[1] + dist * 0.4 * math.sin(lr))
            out += leaf(base, la, size, fill=g)
    return out

# Each clump its own size: a fixed mix, so the tree looks the same every time it is drawn.
SIZES = [30, 24, 36, 27, 33, 22, 35, 28, 25, 34, 31, 23, 37, 26, 29, 32, 24, 35]

if __name__ == "__main__" and "--one" in sys.argv:
    limbs, tips = tree()
    g = wood(limbs)
    for k, (q, ang) in enumerate(tips): g += cluster(q, ang, r=SIZES[k % len(SIZES)])
    W, H = 520, 440
    open(sys.argv[1], "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#eef3f0"/><defs><clipPath id="ground"><rect x="-400" y="-500" width="800" height="500"/></clipPath></defs><g transform="translate(260 400)">%s</g><line x1="20" y1="400" x2="500" y2="400" stroke="#8a8" stroke-width="2"/></svg>' % (W, H, W, H, g))
    sys.exit()
if __name__ == "__main__":
    limbs, tips = tree()
    body = ""
    for i, (fn, name) in enumerate([(fan, "Fan clumps"), (cluster, "Cluster clumps")]):
        cx = 260 + i * 520
        g = wood(limbs)
        for q, ang in tips: g += fn(q, ang)
        body += '<g transform="translate(%d 380)">%s</g>' % (cx, g)
        body += '<line x1="%d" y1="380" x2="%d" y2="380" stroke="#8a8" stroke-width="2"/>' % (cx - 240, cx + 240)
        body += '<text x="%d" y="425" font-family="sans-serif" font-size="20" fill="#333" text-anchor="middle">%s</text>' % (cx, name)
    W, H = 1040, 440
    open(sys.argv[1], "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#eef3f0"/><defs><clipPath id="ground"><rect x="-400" y="-500" width="800" height="500"/></clipPath></defs>%s</svg>' % (W, H, W, H, body))
