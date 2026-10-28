"""Skeleton versions: classic, chibi, dapper. Every bone a hard part on its joint; ground at y=0."""
import math, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from dino import cr, limb_pts
B, L = "#f6f1e3", "#4a4038"

def limb(a, b, wa, wb, lw=2.6, fill=B):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (cr(limb_pts(a, b, wa, wb, 6), tension=0.35), fill, L, lw)

def bone(a, b, w):
    """A cartoon bone: a shaft with two knobs at each end, outline drawn under the fill so knobs and shaft read as one."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); nx, ny = -math.sin(ang) * w * 0.5, math.cos(ang) * w * 0.5
    ends = [(p[0] + dx, p[1] + dy) for p in (a, b) for dx, dy in ((nx, ny), (-nx, -ny))]
    under = "".join('<circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (x, y, w * 0.5 + 1.3, L) for x, y in ends)
    under += limb(a, b, w * 0.62 + 2.6, w * 0.62 + 2.6, 0, L)
    over = "".join('<circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (x, y, w * 0.5 - 1.3, B) for x, y in ends)
    over += '<path d="%s" fill="%s"/>' % (cr(limb_pts(a, b, w * 0.62, w * 0.62, 6), tension=0.35), B)
    return under + over

def skeleton(head=1.0, bw=1.0, legs=1.0, body=1.0, hat=False, tie=False):
    hip_y = -78 * legs; knee_y = -42 * legs; ank_y = -10
    top = hip_y - 60 * body  # shoulders
    out_back, out_front = "", ""
    for sx in (-1, 1):
        hip, knee, ank = (sx * 12, hip_y), (sx * 13, knee_y), (sx * 13, ank_y)
        sh, el = (sx * 34, top + 4), (sx * 42, top + 4 + 27 * body)
        wr = (sx * 46, el[1] + 26 * body)
        # Legs and feet.
        out_back += bone(hip, knee, 11 * bw) + bone(knee, ank, 10 * bw)
        out_back += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
            cr([(ank[0] - 8 * sx, -11), (ank[0] + sx * 14, -10), (ank[0] + sx * 19, -3), (ank[0] + sx * 18, 0), (ank[0] - 9 * sx, 0)], tension=0.4), B, L)
        # Arms, outside the ribs.
        out_front += bone(sh, el, 9 * bw) + bone(el, wr, 8 * bw)
        for k in range(3):
            out_front += limb((wr[0], wr[1] + 3), (wr[0] + sx * (k - 1) * 4.5, wr[1] + 15), 4.2 * bw, 3.2 * bw, 2)
    # Pelvis, spine, ribs, collarbone.
    mid = '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (cr([(-24, hip_y - 8), (24, hip_y - 8), (18, hip_y + 8), (0, hip_y + 2), (-18, hip_y + 8)], tension=0.4), B, L)
    mid += limb((0, hip_y - 6), (0, top), 7, 7)
    for k in range(3):
        y = top + 8 + k * 12 * body
        w = 24 - k * 3
        for s in (1, -1):
            mid += '<path d="M 0 %g q %g 3 %g 13" fill="none" stroke="%s" stroke-width="7.4" stroke-linecap="round"/>' % (y, s * w, s * (w - 4), L)
            mid += '<path d="M 0 %g q %g 3 %g 13" fill="none" stroke="%s" stroke-width="3.8" stroke-linecap="round"/>' % (y, s * w, s * (w - 4), B)
    mid += '<path d="%s" fill="%s" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (cr([(-34, top + 2), (34, top + 2), (26, top + 8), (-26, top + 8)], tension=0.3), B, L)
    if tie:
        y = top + 1
        mid += '<path d="M 0 %g l -11 -6 l 0 12 Z M 0 %g l 11 -6 l 0 12 Z" fill="#c0392b" stroke="%s" stroke-width="2" stroke-linejoin="round"/><circle cx="0" cy="%g" r="3.4" fill="#a02a1e" stroke="%s" stroke-width="1.6"/>' % (y, y, L, y, L)
    # Skull, scaled about the neck.
    neck = top - 2
    s = head
    skull = '<g transform="translate(0 %g) scale(%g)">' % (neck, s)
    skull += limb((0, 0), (0, -8), 7, 7)
    skull += '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (cr([(-23, -30), (-15, -52), (15, -52), (23, -30), (17, -10), (11, -5), (-11, -5), (-17, -10)], tension=0.5), B, L, 2.8 / s)
    skull += '<ellipse cx="-8.5" cy="-28" rx="6.5" ry="7.5" fill="%s"/><ellipse cx="8.5" cy="-28" rx="6.5" ry="7.5" fill="%s"/><path d="M 0 -19 l -2.6 5 l 5.2 0 Z" fill="%s"/>' % (L, L, L)
    skull += "".join('<line x1="%g" y1="-11" x2="%g" y2="-6" stroke="%s" stroke-width="%g"/>' % (x, x, L, 1.6 / s) for x in (-6, -2, 2, 6))
    skull += '<circle cx="-6.5" cy="-30" r="1.8" fill="#fff"/><circle cx="10.5" cy="-30" r="1.8" fill="#fff"/>'
    if hat:
        skull += ('<rect x="-26" y="-55" width="52" height="7" rx="3" fill="#2c2c34" stroke="%s" stroke-width="2.4"/>'
                  '<rect x="-16" y="-84" width="32" height="31" rx="3" fill="#2c2c34" stroke="%s" stroke-width="2.4"/>'
                  '<rect x="-16" y="-62" width="32" height="6" fill="#c0392b"/>') % (L, L)
    skull += "</g>"
    return out_back + mid + out_front + skull

if __name__ == "__main__":
    body = ""
    options = [("1  Classic", dict()), ("2  Chibi", dict(head=1.5, bw=1.3, legs=0.9, body=0.92)), ("3  Dapper", dict(hat=True, tie=True))]
    for i, (name, kw) in enumerate(options):
        cx = 170 + i * 320
        body += '<g transform="translate(%d 290)">%s</g>' % (cx, skeleton(**kw))
        body += '<line x1="%d" y1="290" x2="%d" y2="290" stroke="#8a8" stroke-width="2"/>' % (cx - 120, cx + 120)
        body += '<text x="%d" y="330" font-family="sans-serif" font-size="20" fill="#333" text-anchor="middle">%s</text>' % (cx, name)
    W, H = 960, 350
    open(sys.argv[1], "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#eef3f0"/>%s</svg>' % (W, H, W, H, body))
