"""Three jellyfish for the skeletons demo, in the cartoon style: the bell one picture, each tentacle its own."""
import math, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from dino import cr

def ribbon(top, length, width, waves, phase, fill, line, frill=False, taper=0.25, lw=2.4):
    """A hanging tentacle: a wavy band from top down, tapering to the tip."""
    left, right, mid = [], [], []
    n = 16
    for k in range(n + 1):
        t = k / n
        x = top[0] + math.sin(t * waves * math.pi + phase) * 7 * t ** 0.7
        y = top[1] + length * t
        w = width * (1 - (1 - taper) * t)
        if frill: w *= 1 + 0.35 * math.sin(t * 22)
        left.append((x - w / 2, y)); right.append((x + w / 2, y)); mid.append((x, y))
    outline = left + [ (mid[-1][0], mid[-1][1] + width * taper * 0.4) ] + list(reversed(right))
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (cr(outline, tension=0.4), fill, line, lw)

def bell(w, h, fill, line, rim_frill=0, opacity=1.0, extra=""):
    """A dome from -w/2..w/2 wide and h tall above y=0, its rim along y=0 (scalloped when rim_frill)."""
    pts = []
    for k in range(13):
        a = math.pi + math.pi * k / 12
        pts.append((w / 2 * math.cos(a), h * math.sin(a) * (1 if k not in (0, 12) else 1)))
    rim = []
    if rim_frill:
        for k in range(rim_frill * 2 + 1):
            x = w / 2 - w * k / (rim_frill * 2)
            rim.append((x, 6 if k % 2 else 0))
    else:
        rim = [(w / 2, 0), (w * 0.25, 8), (-w * 0.25, 8), (-w / 2, 0)]
    d = cr(pts[:-1] + rim, tension=0.45)
    return '<path d="%s" fill="%s" fill-opacity="%g" stroke="%s" stroke-width="3" stroke-linejoin="round"/>%s' % (d, fill, opacity, line, extra)

def jelly1():
    L, F = "#7a1f4a", "#f48fb1"
    out = ""
    for i, x in enumerate((-46, -30, -12, 12, 30, 46)):
        out += ribbon((x, 4), 120 + (i % 3) * 14, 5, 3, i, "#f7b4cc", L)
    for i, x in enumerate((-16, -6, 6, 16)):
        out += ribbon((x, 2), 90 + (i % 2) * 12, 15, 2, i * 1.3, "#f06d9b", L, frill=True)
    shine = '<path d="M -34 -46 q 10 -18 30 -22" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.7"/>'
    out += bell(116, 72, F, L, rim_frill=6, extra=shine)
    return out

def jelly2():
    L, F = "#2c5a7a", "#a9dcf2"
    out = ""
    for i in range(9):
        x = -52 + i * 13
        out += ribbon((x, 3), 120 + (i * 37 % 40), 4, 2.5, i * 0.9, "#d8f1fb", "#6fa9c6", taper=0.5, lw=1.4)
    rings = "".join('<circle cx="%g" cy="-30" r="11" fill="none" stroke="#e48fb0" stroke-width="5" opacity="0.85"/>' % x for x in (-30, -10, 10, 30))
    shine = '<path d="M -40 -50 q 12 -18 34 -22" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.8"/>'
    out += bell(124, 62, F, L, opacity=0.8, extra=rings + shine)
    return out

def jelly3():
    L, F = "#3d2470", "#a58cf0"
    out = ""
    for i, x in enumerate((-40, -20, 0, 20, 40)):
        out += ribbon((x, 4), 104 + (i % 2) * 22, 17, 2.2, i * 1.1, "#c3b2f7", L, taper=0.35)
    face = ('<ellipse cx="-18" cy="-34" rx="9" ry="11" fill="#fff" stroke="%s" stroke-width="2"/><ellipse cx="18" cy="-34" rx="9" ry="11" fill="#fff" stroke="%s" stroke-width="2"/>'
            '<circle cx="-16" cy="-32" r="5" fill="#1a1a2a"/><circle cx="20" cy="-32" r="5" fill="#1a1a2a"/>'
            '<path d="M -10 -16 q 10 9 20 0" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>'
            '<ellipse cx="-34" cy="-20" rx="7" ry="4" fill="#f4a2c8" opacity="0.8"/><ellipse cx="34" cy="-20" rx="7" ry="4" fill="#f4a2c8" opacity="0.8"/>'
            '<path d="M -40 -58 q 10 -16 30 -20" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.7"/>') % (L, L, L)
    out += bell(116, 84, F, L, extra=face)
    return out

if __name__ == "__main__":
    body = ""
    for i, (fn, name) in enumerate([(jelly1, "1  Frilly"), (jelly2, "2  Moon jelly"), (jelly3, "3  Friendly")]):
        cx = 180 + i * 340
        body += '<g transform="translate(%d 120)">%s</g>' % (cx, fn())
        body += '<text x="%d" y="320" font-family="sans-serif" font-size="20" fill="#333" text-anchor="middle">%s</text>' % (cx, name)
    W, H = 1020, 340
    open(sys.argv[1], "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#e6f1f6"/>%s</svg>' % (W, H, W, H, body))
