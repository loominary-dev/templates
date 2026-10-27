"""The four characters of the skeletons demo as rigs (rigkit.Rig), with their animations as keyed poses.

- Dinosaur: rigid legs, arms, head and jaw; the body with its neck one mesh, the tail another. Walk and run, the feet
  placed along a stride and the legs solved to them (IK), flat on the ground while planted.
- Tree: the wood one mesh on a branching tree of bones, a sway motor at its foot; each leaf clump on a jiggling bone.
- Jellyfish: the bell a mesh pulsed by deform keys; each tentacle and frilled arm a mesh on a chain of bones with a wave motor.
- Dancer: the dapper skeleton, every bone a rigid picture; idle with a hat tip, and the Charleston.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rigkit import Rig, chain_weigh, nearest_along, norm
import dino as DI
import tree as TR
import tree2 as T2
import jelly as JE
import skel_rig as SR
import skel_anim as SA

# ── the dinosaur ──
# The toe bone, in drawing pixels: how far along the foot it starts, how much it turns from the foot, how long it is.
TOE_AT, TOE_TURN, TOE_LENGTH = 57.2, -0.589, 16.3

def dinosaur(k):
    r = Rig("Dinosaur", k, order_by_z=True)   # the tail behind the body, though its bone comes after the body's
    H, K, A = DI.HIP, DI.KNEE, DI.ANKLE
    r.bone("Hips", None, H, (H[0] + 10, H[1]))
    r.bone("Body", "Hips", H, (46, -136))
    r.bone("Neck1", "Body", (46, -136), (66, -162))
    r.bone("Neck2", "Neck1", (66, -162), (78, -184))
    r.bone("Head", "Neck2", (78, -184), (148, -196))
    r.bone("Jaw", "Head", (80, -186), (140, -182))
    r.bone("Tail1", "Hips", (-40, -124), (-82, -127))
    r.bone("Tail2", "Tail1", (-82, -127), (-120, -122))
    r.bone("Tail3", "Tail2", (-120, -122), (-152, -114))
    for side, o in (("Far", DI.FAR), ("Near", (0, 0))):
        h, kn, a = (DI.off(q, o) for q in (H, K, A))
        r.bone("Thigh" + side, "Hips", h, kn)
        r.bone("Shin" + side, "Thigh" + side, kn, a)
        r.bone("Foot" + side, "Shin" + side, a, (a[0] + 46, o[1] - 4))
        # A toe on each foot: the user drew it on the near foot in the editor (Bone1, 2026-10-22), 57 px along the foot, turned 34° up.
        fb = r.bones["Foot" + side]
        tb = (a[0] + TOE_AT * math.cos(fb.angle), a[1] + TOE_AT * math.sin(fb.angle))
        ta = fb.angle + TOE_TURN
        r.bone("Toe" + side, "Foot" + side, tb, (tb[0] + TOE_LENGTH * math.cos(ta), tb[1] + TOE_LENGTH * math.sin(ta)))
        sh, el, ha = (DI.off(q, o) for q in (DI.SHOULDER, DI.ELBOW, DI.HAND))
        r.bone("UpperArm" + side, "Body", sh, el)
        r.bone("Forearm" + side, "UpperArm" + side, el, ha)
    sv = lambda n: DI.part_svg("D", n)
    spine = [(-75, -126), (-40, -124), (0, -115), (46, -136), (66, -162), (80, -190)]
    r.part("Body", sv("body"), "Body", mesh=(10, 8, chain_weigh(spine, ["Tail1", "Hips", "Body", "Neck1", "Neck2"])), z=0)
    tail = [(-10, -120), (-40, -124), (-82, -127), (-120, -122), (-152, -114)]
    r.part("Tail", sv("tail"), "Tail1", mesh=(14, 4, chain_weigh(tail, ["Hips", "Tail1", "Tail2", "Tail3"])), z=-1)
    r.part("Head", sv("head"), "Head", z=2)
    r.part("Jaw", sv("jaw"), "Jaw", z=1)
    for side, z in (("Far", -3), ("Near", 3)):
        lo = side.lower()
        r.part("Thigh" + side, sv("thigh_" + lo), "Thigh" + side, z=z)
        r.part("Shin" + side, sv("shin_" + lo), "Shin" + side, z=z)
        foot, toe = r.bones["Foot" + side], r.bones["Toe" + side]
        r.part("Foot" + side, sv("foot_" + lo), "Foot" + side, z=z,
               mesh=(8, 4, chain_weigh([foot.base, toe.base, toe.tip], ["Foot" + side, "Toe" + side])))
        r.part("UpperArm" + side, sv("upperarm_" + lo), "UpperArm" + side, z=z + 1)
        r.part("Forearm" + side, sv("forearm_" + lo), "Forearm" + side, z=z + 1)
    return r

# Where the body's weight sits: over the hips. Each foot's sole travels as far in front of it as behind.
COG_X = 0.0

def gait(r, dur, stride, lift, stance, bob, lean, steps=32, run=False, drop=0.0):
    """A loop of keys: each foot planted (flat, sliding back along the ground) for `stance` of the cycle, then lifted and swung
    forward. The middle of the sole (a little ahead of the ankle) passes under the center of gravity at the middle of the stance,
    so the stride reaches as far in front of it as behind."""
    keys = []
    for i in range(steps + 1):
        ph = i / steps
        # `drop` lowers the hips through the whole cycle: a crouch that lets a long stride keep the knees bent.
        turns, off = {}, {"Hips": (0, drop + bob * math.cos(4 * math.pi * ph))}
        turns["Body"] = lean + 0.03 * math.sin(4 * math.pi * ph)
        turns["Neck1"] = -lean * 0.5 - 0.03 * math.sin(4 * math.pi * ph + 0.6)
        turns["Neck2"] = -lean * 0.4
        turns["Head"] = -0.04 * math.sin(4 * math.pi * ph + 1.2)
        turns["Jaw"] = 0.22 + 0.06 * math.sin(4 * math.pi * ph) if run else 0
        for j, tb in enumerate(("Tail1", "Tail2", "Tail3")):
            turns[tb] = (0.07 if run else 0) + (0.05 if run else 0.07) * math.sin(2 * math.pi * (ph - 0.12 * (j + 1)) * 2)
        for side, shift in (("Near", 0.0), ("Far", 0.5)):
            p = (ph + shift) % 1
            rest_ankle = r.bones["Shin" + side].tip
            sole_mid = 20                            # the middle of the sole, ahead of the ankle
            center = COG_X - sole_mid + (rest_ankle[0] - r.bones["Shin" + "Near"].tip[0])
            if p < stance:
                u = p / stance
                dx, dy, tilt = stride / 2 - stride * u, 0.0, 0.0
            else:
                u = (p - stance) / (1 - stance); s = u * u * (3 - 2 * u)
                dx, dy = -stride / 2 + stride * s, -lift * math.sin(math.pi * u)
                tilt = 0.45 * math.sin(math.pi * u)
            target = (center + dx, rest_ankle[1] + dy)
            t1, t2 = r.two_bone(turns, off, "Thigh" + side, "Shin" + side, target, prefer=lambda a, b: a[0] > b[0])
            turns["Thigh" + side], turns["Shin" + side] = t1, t2
            turns["Foot" + side] = r.keep_world_angle(turns, off, "Foot" + side, r.bones["Foot" + side].angle + tilt)
            # The toes curl down as the foot lifts and straighten as it lands.
            turns["Toe" + side] = 0.5 * tilt
            arm = (-0.35 if run else 0) + (0.12 if run else 0.18) * math.sin(2 * math.pi * (ph + shift))
            turns["UpperArm" + side] = arm
            turns["Forearm" + side] = (-0.5 if run else -0.1) + 0.1 * math.sin(2 * math.pi * (ph + shift) + 0.5)
        keys.append((dur * ph, turns, off))
    return keys

def dinosaur_animations(r):
    # Keys 0.05 s apart, on the timeline's grid at a step of 0.05 or finer: 24 to a walk, 12 to a run.
    # The walk strides out a little beyond a stroll; the run goes like a chicken flat out: long quick strides, low and
    # leaning, the feet planted for less than half the cycle.
    return {"walk": (1.2, gait(r, 1.2, 58, 17, 0.6, 3.0, 0.0, steps=24, drop=3)),
            "run": (0.45, gait(r, 0.45, 86, 26, 0.4, 4.0, 0.32, steps=9, run=True, drop=12))}

# ── the tree ──
def tree(k):
    r = Rig("Oak", k)   # not "Tree": the engine has a Tree (the UI list)
    r.bone("Base", None, (0, 0), (0, -10))
    r.bone("Trunk1", "Base", (0, -10), (0, -60), motor="sway", motorAmount=2.5, motorSpeed=0.3)
    r.bone("Trunk2", "Trunk1", (0, -60), (0, -122))
    limbs = [((0, 0), (0, -60), 40, 33), ((0, -60), (0, -122), 33, 26), ((-6, -20), (-34, 6), 20, 13), ((6, -20), (36, 6), 20, 13)]
    segs = [((0, 0), (0, -10), "Base"), ((-6, -20), (-34, 6), "Base"), ((6, -20), (36, 6), "Base"), ((0, -10), (0, -60), "Trunk1"), ((0, -60), (0, -122), "Trunk2")]
    tips = []
    count = [0]
    def branch(parent, p, ang, length, width, depth):
        count[0] += 1
        name = "Branch%d" % count[0]
        a = math.radians(ang)
        q = (p[0] + length * math.cos(a), p[1] + length * math.sin(a))
        r.bone(name, parent, p, q)
        limbs.append((p, q, width, width * 0.62)); segs.append((p, q, name))
        if depth == 0:
            tips.append((name, q, ang)); return
        spread = 26 if depth > 1 else 30
        up, down = (-spread, spread * 0.55) if math.cos(a) > 0 else (-spread * 0.55, spread)
        for d_ang, frac in ((up, 0.72), (down, 0.66)):
            branch(name, q, ang + d_ang, length * frac, width * 0.62, depth - 1)
    for start, ang, L, w in [((0, -100), -150, 94, 17), ((0, -114), -122, 100, 16), ((0, -122), -90, 92, 16), ((0, -114), -58, 100, 16), ((0, -100), -30, 94, 17)]:
        branch("Trunk2", start, ang, L, w, 2 if abs(ang + 90) > 10 else 1)
    def weigh(x, y):
        ws = {}
        for a, b, name in segs:
            vx, vy = b[0] - a[0], b[1] - a[1]
            t = max(0, min(1, ((x - a[0]) * vx + (y - a[1]) * vy) / (vx * vx + vy * vy)))
            d = math.hypot(a[0] + vx * t - x, a[1] + vy * t - y)
            ws[name] = ws.get(name, 0) + 1 / (d + 4) ** 4
        top = sorted(ws.items(), key=lambda kv: -kv[1])[:3]
        return dict(top)
    r.part("Wood", TR.wood(limbs), "Base", mesh=(26, 22, weigh), z=0)
    for i, (name, q, ang) in enumerate(tips):
        rad = T2.SIZES[i % len(T2.SIZES)]
        a = math.radians(ang)
        r.bone("Clump%d" % (i + 1), name, q, (q[0] + rad * math.cos(a), q[1] + rad * math.sin(a)), motor="jiggle", motorAmount=22, motorSpeed=1.1, motorDelay=0.25)
        r.part("Clump%d" % (i + 1), T2.cluster(q, ang, r=rad), "Clump%d" % (i + 1), z=1)
    return r

# ── the jellyfish ──
JELLY_TENTACLES = [(x, 120 + (i % 3) * 14, 5, 3, i, "#f7b4cc", False, 0.25) for i, x in enumerate((-46, -30, -12, 12, 30, 46))]
JELLY_ARMS = [(x, 90 + (i % 2) * 12, 15, 2, i * 1.3, "#f06d9b", True, 0.25) for i, x in enumerate((-16, -6, 6, 16))]

def jellyfish(k):
    r = Rig("Jellyfish", k)
    r.bone("Bell", None, (0, -40), (0, 0))
    L = "#7a1f4a"
    for group, (prefix, items, seg_n, z) in enumerate((("Tentacle", JELLY_TENTACLES, 5, -2), ("Arm", JELLY_ARMS, 4, -1))):
        for i, (x, length, width, waves, phase, fill, frill, taper) in enumerate(items):
            names, pts = [], []
            for s in range(seg_n):
                a, b = (x, 4 + length * s / seg_n), (x, 4 + length * (s + 1) / seg_n)
                nm = "%s%d_%d" % (prefix, i + 1, s + 1)
                extra = dict(motor="wave", motorAmount=11 if prefix == "Tentacle" else 8, motorSpeed=0.42 + 0.06 * i + 0.05 * group, motorDelay=0.2) if s == 0 else {}
                r.bone(nm, "Bell" if s == 0 else names[-1], a, b, **extra)
                names.append(nm); pts.append(a)
            pts.append((x, 4 + length))
            r.part("%s%d" % (prefix, i + 1), JE.ribbon((x, 4), length, width, waves, phase, fill, L, frill=frill, taper=taper), names[0],
                   mesh=(2, 3 * seg_n, chain_weigh(pts, names)), z=z)
    shine = '<path d="M -34 -46 q 10 -18 30 -22" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.7"/>'
    r.part("BellPicture", JE.bell(116, 72, "#f48fb1", L, rim_frill=6, extra=shine), "Bell", mesh=(8, 6, lambda x, y: {"Bell": 1}), z=0)
    return r

def bell_deform(r, squeeze, rise):
    """The bell's points moved: squeezed in toward the middle near the rim, the top rising. In the picture's pixels."""
    p = next(p for p in r.parts if p.name == "BellPicture")
    mesh = r.mesh_of(p)
    vs = []
    for i in range(len(mesh["vertices"]) // 2):
        x, y = r.to_drawing(p, mesh["vertices"][i * 2], mesh["vertices"][i * 2 + 1])
        low = max(0.0, min(1.0, (y + 72) / 72))       # 0 at the top of the dome, 1 at the rim
        vs += [round(-x * squeeze * low * r.k, 2), round((-rise * (1 - low) - squeeze * 8 * low) * r.k, 2)]
    return vs

def jellyfish_animations(r):
    def pulse(dur, bob, squeeze, rise, flare, times):
        """times: (seconds, rise as a share of bob, squeeze as a share), on the timeline's tenth-of-a-second grid."""
        keys, deform = [], []
        for t, rel, sq in times:
            turns, off = {}, {"Bell": (0, bob * rel)}
            # The tentacles' first bones flare out as the bell squeezes, then trail back.
            for name in r.order:
                if name.endswith("_1"):
                    x = r.bones[name].base[0]
                    turns[name] = -flare * sq * (1 if x > 0 else -1) * min(1, abs(x) / 30)
            keys.append((t, turns, off))
            deform.append({"t": round(t, 4), "vs": bell_deform(r, squeeze * sq, rise * sq), "ease": "easeInOut"})
        deform[-1].pop("ease")
        return keys, deform
    drift = ((0, 0.0, 0.0), (0.4, -0.4, 0.6), (0.8, -0.8, 1.0), (1.2, -1.0, 0.4), (1.8, -0.6, 0.0), (2.4, 0.0, 0.0))
    swim = ((0, 0.0, 0.0), (0.2, -0.4, 0.6), (0.3, -0.8, 1.0), (0.5, -1.0, 0.4), (0.7, -0.6, 0.0), (1.0, 0.0, 0.0))
    return {"drift": (2.4,) + pulse(2.4, 10, 0.12, 6, 0.12, drift), "swim": (1.0,) + pulse(1.0, 20, 0.2, 10, 0.17, swim)}

# ── the dancer ──
def dancer(k):
    r = Rig("Dancer", k)
    for name, parent, base, tip in SR.BONES:
        extra = {}
        if name.startswith("Forearm"):
            lo, hi = SA.elbow_range(name[-1])
            # The bone's limits are on its turn under its parent; its rest turn is inside them.
            rest = math.degrees(math.atan2(tip[1] - base[1], tip[0] - base[0]) - SR.rest_angle(parent))
            extra = dict(limitAngles=True, minAngle=round(rest + lo, 2), maxAngle=round(rest + hi, 2))
        r.bone(name, parent, base, tip, **extra)
    for i, name in enumerate(SR.DRAW):
        r.part(name, SR.part_svg(name), name, z=i)
    return r

def dancer_animations(r):
    idle, idur = SA.idle_keys(); ch, cdur = SA.charleston_keys()
    return {"idle": (idur, idle), "charleston": (cdur, ch)}

def oak_animations(r):
    """None: the tree is moved by its motors alone."""
    return {}
