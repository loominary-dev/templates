"""The dapper skeleton's two animations as keys of bone turns and offsets, posed with small IK solves so the feet stay planted
and the hand meets the hat; and a preview GIF rendered from those same keys."""
import math, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skel_rig as R

def norm(a):
    while a > math.pi: a -= 2 * math.pi
    while a < -math.pi: a += 2 * math.pi
    return a

# How far each elbow and knee may fold from straight, in degrees: an elbow never doubles back on its upper arm.
FOLD_LIMIT = {"Forearm": 85, "Shin": 60}

def two_bone_turns(pose_turns, offsets, upper, lower, target, bend):
    """Turns for `upper` and `lower` so the lower bone's tip reaches target, the joint bending to side `bend` (+1/-1).
    The fold is held within FOLD_LIMIT: past it, the joint stops there and the chain points at the target, the tip falling short."""
    wp = R.world_poses(pose_turns, offsets)
    base, _ = wp[upper]
    l1 = math.dist(R.BONE[upper][2], R.BONE[upper][3]); l2 = math.dist(R.BONE[lower][2], R.BONE[lower][3])
    dx, dy = target[0] - base[0], target[1] - base[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-3)
    limit = math.radians(FOLD_LIMIT.get(lower.rstrip("LR"), 180))
    # The shortest reach the fold allows: the joint at its limit.
    d_min = math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(limit))
    d = max(d, d_min + 1e-3)
    a = math.atan2(dy, dx)
    c1 = max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    w1 = a - bend * math.acos(c1)
    joint = (base[0] + l1 * math.cos(w1), base[1] + l1 * math.sin(w1))
    w2 = math.atan2(target[1] - joint[1], target[0] - joint[0])
    # World angle = parent's world angle + local rest + turn.
    parent = R.BONE[upper][1]
    pa = wp[parent][1] if parent else 0
    up_rest_local = R.rest_angle(upper) - (R.rest_angle(parent) if parent else 0)
    t1 = norm(w1 - pa - up_rest_local)
    lo_rest_local = R.rest_angle(lower) - R.rest_angle(upper)
    t2 = norm(w2 - w1 - lo_rest_local)
    return t1, t2

def plant_feet(turns, offsets, ankles, knee_in=1.0):
    """Leg turns that keep each ankle at its place, knees bending inward (toward the middle)."""
    for side, sx in (("L", -1), ("R", 1)):
        bend = -sx * knee_in  # the left knee goes right, the right knee left: knock-kneed
        t1, t2 = two_bone_turns(turns, offsets, "Thigh" + side, "Shin" + side, ankles[side], bend)
        turns["Thigh" + side], turns["Shin" + side] = t1, t2
        # The foot keeps its own turn in the world: undo what the leg turned.
        wp = R.world_poses(turns, offsets)
        want = R.rest_angle("Foot" + side) + turns.get("_foot" + side, 0)
        turns["Foot" + side] = norm(want - (wp["Foot" + side][1] - turns.get("Foot" + side, 0)))
    for k in [k for k in turns if k.startswith("_")]: del turns[k]
    return turns

ANK = {"L": R.BONE["ShinL"][3], "R": R.BONE["ShinR"][3]}

# Each elbow's range, as the forearm's turn against its upper arm in degrees, for the right arm (the left is mirrored):
# folding in toward the body as far as FOLD_LIMIT, out the other way only a little. The engine's bones get the same limits.
ELBOW_RANGE_R = (-FOLD_LIMIT["Forearm"], 40)

def elbow_range(side):
    lo, hi = ELBOW_RANGE_R
    return (lo, hi) if side == "R" else (-hi, -lo)

def limit_elbows(turns, off):
    """Every key's elbows held in range, however the key was made."""
    for side in "LR":
        rest_local = R.rest_angle("Forearm" + side) - R.rest_angle("UpperArm" + side)
        lo, hi = (math.radians(v) for v in elbow_range(side))
        bend = norm(turns.get("Forearm" + side, 0) + rest_local)
        turns["Forearm" + side] = max(lo, min(hi, bend)) - rest_local
    return turns

def idle_keys():
    keys = []
    hat_rest = R.world_poses({})["Hat"][0]
    for t, breath, nod, tip in [(0, 0, 0, 0), (1.0, 1.6, 0.05, 0), (2.0, 0, 0, 0), (2.4, 0.8, -0.03, 0), (2.6, 1.0, 0.03, 3), (2.8, 1.2, 0.08, 1), (3.2, 1.0, 0.12, 2),
                                (3.6, 0.6, 0.04, 1), (3.8, 0.4, 0.02, 3), (4.0, 0.2, 0, 0), (4.4, 1.6, -0.04, 0), (5.0, 0, 0, 0)]:
        turns, off = {}, {"Pelvis": (0, breath)}
        turns["Spine"] = -0.012 * breath; turns["Head"] = nod
        turns["UpperArmL"] = 0.04 * math.sin(t * 2.4); turns["ForearmL"] = 0.06 * math.sin(t * 2.4 + 1)
        turns["UpperArmR"] = -0.04 * math.sin(t * 2.4); turns["ForearmR"] = -0.06 * math.sin(t * 2.4 + 1)
        plant_feet(turns, off, ANK)
        if tip == 3:
            # On the way up and down: the arm lifts out to the side, the forearm turning up, so the hand never crosses the body.
            turns["UpperArmR"], turns["ForearmR"] = -1.35, -2.05
        elif tip:
            # The skull tilts toward the right hand, which takes the brim's edge; the hat lifts and tilts with it.
            turns["Head"] = nod + (0.28 if tip == 1 else 0.34)
            off["Hat"] = (14 if tip == 2 else 3, 0)        # up along the hat's own bone
            turns["Hat"] = 0.5 if tip == 2 else 0.08
            wp = R.world_poses(turns, off)
            hb, ha = wp["Hat"]; rb = R.BONE["Hat"][2]; dr = ha - R.rest_angle("Hat")
            ex, ey = 27 - rb[0], (R.TOP - 52) - rb[1]          # the brim's right edge, from the hat bone's base, at rest
            brim = (hb[0] + ex * math.cos(dr) - ey * math.sin(dr), hb[1] + ex * math.sin(dr) + ey * math.cos(dr))
            t1, t2 = two_bone_turns(turns, off, "UpperArmR", "ForearmR", (brim[0] + 7, brim[1] + 4), -1)
            turns["UpperArmR"], turns["ForearmR"] = t1, t2
        keys.append((t, limit_elbows(turns, off), off))
    return keys, 5.0

def charleston_keys():
    keys = []
    T = 1.0   # two beats of 0.5 s, keys every 0.25 s: on the timeline's grid at a step of 0.05 or finer
    for i in range(5):
        t = T * i / 4
        down = i % 2 == 1          # down on the off-beats
        swing = 1 if i in (0, 4) else -1 if i == 2 else 0
        phase = [0, 1, 0, -1, 0][i]  # which way the knees and arms swing
        turns, off = {}, {"Pelvis": (2.5 * phase, 3.2 if down else 0)}
        turns["_footL"] = -0.4 * phase if down else 0.25 * swing
        turns["_footR"] = -0.4 * phase if down else -0.25 * swing
        turns["Spine"] = 0.07 * phase; turns["Head"] = -0.12 * phase
        # Arms swing across: one in, one out, crossing on the down beat.
        turns["UpperArmL"] = -0.9 * phase - (0.25 if down else 0); turns["ForearmL"] = -0.5 * phase
        turns["UpperArmR"] = -0.9 * phase + (0.25 if down else 0); turns["ForearmR"] = -0.5 * phase
        ankles = {"L": (ANK["L"][0] + (3 * swing if not down else 0), ANK["L"][1]), "R": (ANK["R"][0] - (3 * swing if not down else 0), ANK["R"][1])}
        plant_feet(turns, off, ankles, knee_in=1.0)
        off["Hat"] = (2 if down else 0, 0)
        keys.append((t, limit_elbows(turns, off), off))
    return keys, T

def sample(keys, dur, t):
    """The pose at time t: smoothstep between the keys either side."""
    t = t % dur
    for k in range(len(keys) - 1):
        t0, a, ao = keys[k]; t1, b, bo = keys[k + 1]
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u)
            names = set(a) | set(b)
            turns = {n: a.get(n, 0) + norm(b.get(n, 0) - a.get(n, 0)) * u for n in names}
            onames = set(ao) | set(bo)
            offs = {n: tuple(ao.get(n, (0, 0))[i] + (bo.get(n, (0, 0))[i] - ao.get(n, (0, 0))[i]) * u for i in (0, 1)) for n in onames}
            return turns, offs
    return keys[-1][1], keys[-1][2]

def blend(p, q, u):
    u = u * u * (3 - 2 * u)
    (ta, oa), (tb, ob) = p, q
    turns = {n: ta.get(n, 0) + norm(tb.get(n, 0) - ta.get(n, 0)) * u for n in set(ta) | set(tb)}
    offs = {n: tuple(oa.get(n, (0, 0))[i] + (ob.get(n, (0, 0))[i] - oa.get(n, (0, 0))[i]) * u for i in (0, 1)) for n in set(oa) | set(ob)}
    return turns, offs

def render(pose, parts_dir, info, scale=1.2, size=(300, 300), origin=(150, 285)):
    from PIL import Image
    turns, offs = pose
    wp = R.world_poses(turns, offs)
    img = Image.new("RGBA", size, (238, 243, 240, 255))
    for name in R.DRAW:
        pic = Image.open(os.path.join(parts_dir, name + ".png"))
        inf = info[name]
        rb = R.BONE[name][2]; ra = R.rest_angle(name)
        (bx, by), ba = wp[name]
        rot = ba - ra
        # Rotate about the bone's base: the base's place in the picture, in drawn pixels.
        px, py = (rb[0] - inf["x"]) * R.SCALE, (rb[1] - inf["y"]) * R.SCALE
        big = Image.new("RGBA", (pic.width * 4 + 400, pic.height * 4 + 400))
        cx, cy = big.width // 2, big.height // 2
        big.paste(pic, (int(cx - px), int(cy - py)))
        big = big.rotate(-math.degrees(rot), resample=Image.BICUBIC, center=(cx, cy))
        big = big.resize((int(big.width * scale / R.SCALE), int(big.height * scale / R.SCALE)), Image.LANCZOS)
        img.alpha_composite(big, (int(origin[0] + bx * scale - cx * scale / R.SCALE), int(origin[1] + by * scale - cy * scale / R.SCALE)))
    return img

if __name__ == "__main__":
    D = os.path.dirname(os.path.abspath(__file__)); parts = os.path.join(D, "skelparts")
    info = json.load(open(os.path.join(parts, "parts.json")))
    idle, idur = idle_keys(); ch, cdur = charleston_keys()
    frames = []
    fps = 20
    # Idle 5 s, blend 0.5 s into the Charleston, dance 3 s, blend back 0.5 s, idle 1 s.
    timeline = []
    for f in range(int(5 * fps)): timeline.append(sample(idle, idur, f / fps))
    for f in range(int(0.5 * fps)):
        u = f / (0.5 * fps); timeline.append(blend(sample(idle, idur, 5 + f / fps), sample(ch, cdur, f / fps), u))
    for f in range(int(3 * fps)): timeline.append(sample(ch, cdur, 0.5 + f / fps))
    for f in range(int(0.5 * fps)):
        u = f / (0.5 * fps); timeline.append(blend(sample(ch, cdur, 3.5 + f / fps), sample(idle, idur, f / fps), u))
    for f in range(int(1 * fps)): timeline.append(sample(idle, idur, 0.5 + f / fps))
    for pose in timeline: frames.append(render(pose, parts, info).convert("P", palette=1, colors=64))
    frames[0].save(os.path.join(D, "skeleton-motion.gif"), save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, disposal=2)
    # A strip of stills for a quick look.
    from PIL import Image
    picks = [0, 50, 55, 63, 72, 100, 112, 117, 122, 127]
    strip = Image.new("RGBA", (300 * 5, 300 * 2))
    for i, k in enumerate(picks): strip.paste(render(timeline[k], parts, info), ((i % 5) * 300, (i // 5) * 300))
    strip.save(os.path.join(D, "skeleton-strip.png"))
    print(len(frames), "frames")
