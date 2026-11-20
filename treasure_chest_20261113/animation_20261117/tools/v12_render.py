"""Version 12: render one piece of the reveal in background Blender. Nothing is saved.
    PIECE=arrival|waiting|reveal|ending OUT=folder PCT=50 SAMPLES=24 blender -b chest_reveal_v12_full.blend --python tools/v12_render.py
ONLY="3,40,118" renders just those output frames (tests). SKIP_DONE=1 resumes.

The story is keyed on the real timeline (tools/v12_story.py). This script adds what a straight playback cannot do:
- arrival: scene frames from the start (-28) to 49, then 46 more frames with the chest held at 49 while the landing dust clears
  and the side rings swing to rest (the chest must be perfectly still before the waiting loop);
- waiting: the chest held at frame 49 for 225 frames (7.5 s), rattling at 0, 2.5 and 5.0 s, each rattle over
  within 24 frames (0.8 s) and different, the keyhole glow breathing on a 75 frame period; the first 75
  frames are a loop of their own (one rattle);
- reveal: scene frames 50 to the story's end (280) with the rings at rest and the landing dust gone;
- ending: scene frames from the story's end on, 90 frames plus 24 to blend into the start
  (temple/tools/loop_join.py). The mist from the chest has played out by then (tools/v12_slow.py).
Held or overridden things never touch the scene's animation: rig parts get delta transforms, the story's
numbers are set after its action is taken off (in this process only)."""
import bpy, os, math, time
from mathutils import Euler

E = os.environ.get
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
PIECE = E("PIECE", "reveal")
out = E("OUT")
os.makedirs(out, exist_ok=True)
r = scn.render
r.resolution_percentage = int(E("PCT", "50"))
r.image_settings.file_format = "PNG"
scn.eevee.taa_render_samples = int(E("SAMPLES", "24"))
if E("VOL_SAMPLES"):
    scn.eevee.volumetric_samples = int(E("VOL_SAMPLES"))
# the same shadow detail as the half size preview: at full size the shadows did not fit in memory any more
scn.eevee.shadow_resolution_scale = min(1.0, 50.0 / float(r.resolution_percentage))
r.dither_intensity = 1.5                          # fine noise against bands in the dark gradients
if E("BLUR") == "0":
    r.use_motion_blur = False
cam = scn.camera.data
px = 0.5 * (cam.sensor_width / cam.lens) / (max(r.resolution_x, r.resolution_y) * r.resolution_percentage / 100.0)
ng = bpy.data.node_groups.get("Reveal Beam Specks")
if ng and "pixel radius" in ng.nodes:
    ng.nodes["pixel radius"].inputs[1].default_value = px

OB = bpy.data.objects
story, shake, lid, hasp = OB["Temple Story"], OB["Reveal Chest Shake"], OB["Reveal Lid Hinge"], OB["Reveal Hasp Pivot"]
rings = [OB["Reveal Ring Pivot L"], OB["Reveal Ring Pivot R"]]
dust = OB["Reveal Dust Domain"]
dust_ds = next(m for m in dust.modifiers if m.type == "FLUID").domain_settings
dust_gain = bpy.data.materials["Reveal Dust Volume"].node_tree.nodes["dust density"].inputs[1]
DUST_BASE = dust_gain.default_value
mist_ds = next(m for m in OB["Reveal Opening Domain"].modifiers if m.type == "FLUID").domain_settings
HOLD = 49
END = int(bpy.data.objects["Temple Story"]["end"])        # the reveal's last frame; the ending loop starts here
F0 = int(bpy.data.objects["Temple Story"]["start"])   # the story starts here (one second of empty temple)
N1 = HOLD - F0 + 1                               # arrival frames that follow the scene one to one
LOOP, FADE, CELL, RATTLE = 90, 24, 75, 24


def rot(o):
    return tuple(o.rotation_euler)


def sample(frames):
    tab = {}
    for f in frames:
        scn.frame_set(f)
        tab[f] = [rot(o) for o in rings]
    return tab


# what the rig does by itself
scn.frame_set(HOLD)
lid49, hasp49 = rot(lid), rot(hasp)
scn.frame_set(117)
lid117 = rot(lid)
scn.frame_set(74)
hasp74 = rot(hasp)
LID_AX = max(range(3), key=lambda i: abs(lid117[i] - lid49[i]))
LID_SIGN = 1.0 if lid117[LID_AX] > lid49[LID_AX] else -1.0            # which way opens
HASP_AX = max(range(3), key=lambda i: abs(hasp74[i] - hasp49[i]))
HASP_SIGN = 1.0 if hasp74[HASP_AX] > hasp49[HASP_AX] else -1.0
RING = sample(range(1, 166))                      # the rings' own swing is over by frame 162
for f_ in range(166, END + 200):
    RING[f_] = RING[165]
REST = RING[165]
RING_AX = [max(range(3), key=lambda i, k=k: max(RING[f][k][i] for f in RING) - min(RING[f][k][i] for f in RING)) for k in range(2)]
print("V12 RIG lid axis", LID_AX, LID_SIGN, "hasp axis", HASP_AX, HASP_SIGN, "ring axes", RING_AX, flush=True)


def smooth(x, a, b):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def bump(k, a, b, amp):
    return amp * math.sin(math.pi * (k - a) / (b - a)) ** 2 if a <= k <= b else 0.0


def rattle(i, one=False):
    """The chest's own small movements at output frame i of the waiting loop: degrees and units, all zero at rest."""
    k = i % CELL
    kind = 0 if one else (i // CELL) % 3
    z = dict(lid=0.0, roll=0.0, yaw=0.0, hop=0.0, hasp=0.0, ring=0.0)
    if k >= RATTLE:
        return z
    w = 1.0 - smooth(k, RATTLE - 7, RATTLE - 1)                      # everything is back at rest before the rattle's last frame
    if kind == 0:                                                    # two knocks
        z["lid"] = bump(k, 0, 9, 0.45) + bump(k, 10, 20, 0.3)
        z["roll"] = 0.5 * math.sin(2 * math.pi * k / 10) * math.exp(-k / 8) * w
        z["hasp"] = 4.0 * math.sin(2 * math.pi * k / 7) * math.exp(-k / 7) * w
        z["ring"] = 5.0 * math.sin(2 * math.pi * k / 12) * math.exp(-k / 9) * w
    elif kind == 1:                                                  # one hard jolt
        z["lid"] = bump(k, 0, 7, 0.75) + bump(k, 8, 15, 0.25) + bump(k, 16, 22, 0.08)
        z["hop"] = bump(k, 0, 8, 0.035)
        z["yaw"] = 0.35 * math.sin(2 * math.pi * k / 9) * math.exp(-k / 6) * w
        z["hasp"] = 6.0 * math.sin(2 * math.pi * k / 8) * math.exp(-k / 7) * w
        z["ring"] = 7.0 * math.sin(2 * math.pi * k / 12) * math.exp(-k / 9) * w
    else:                                                            # a shiver
        z["roll"] = 0.35 * math.sin(2 * math.pi * k / 4) * math.exp(-k / 10) * w
        z["lid"] = 0.2 * abs(math.sin(2 * math.pi * k / 4)) * math.exp(-k / 9) * w
        z["hasp"] = 3.0 * math.sin(2 * math.pi * k / 4) * math.exp(-k / 8) * w
        z["ring"] = 3.0 * math.sin(2 * math.pi * k / 10) * math.exp(-k / 9) * w
    return z


def set_rings(base_frame, want):
    """Make the rings show `want` (a pair of rotations) while the scene sits on base_frame."""
    for o, cur, w in zip(rings, RING[base_frame], want):
        o.delta_rotation_euler = Euler([w[i] - cur[i] for i in range(3)])


def free_story():
    if story.animation_data and story.animation_data.action:
        story.animation_data.action = None


def state(i):
    """Put the scene in the state of output frame i of this piece; returns the scene frame used."""
    for o in (shake, lid, hasp):
        o.delta_rotation_euler = Euler((0, 0, 0))
        o.delta_location = (0, 0, 0)
    dust.hide_render = False
    dust_gain.default_value = DUST_BASE
    dust_ds.cache_frame_offset = 0
    mist_ds.cache_frame_offset = 0
    if PIECE == "arrival":
        if i < N1:
            f = F0 + i
            scn.frame_set(f)
            for o in rings:
                o.delta_rotation_euler = Euler((0, 0, 0))
            return f
        v = 50 + (i - N1)                                           # the tail: only dust and rings move on
        scn.frame_set(HOLD)
        free_story()
        story["dustfall"] = (v - 17) / 30.0
        env = 1.0 - smooth(v, 58, 95)
        set_rings(HOLD, [tuple(REST[k][a] + (RING[v][k][a] - REST[k][a]) * env for a in range(3)) for k in range(2)])
        dust_ds.cache_frame_offset = HOLD - v
        dust_gain.default_value = DUST_BASE * (1.0 - smooth(v, 52, 93))
        return HOLD
    if PIECE in ("waiting", "waiting1"):
        scn.frame_set(HOLD)
        free_story()
        z = rattle(i, PIECE == "waiting1")
        story["dustfall"] = 9.0
        story["keyhole"] = 0.5 + 0.13 * math.sin(2 * math.pi * (i % CELL) / CELL) + 1.6 * z["lid"]
        story["seam"] = min(z["lid"] / 0.4, 1.6)
        d = [0.0, 0.0, 0.0]
        d[LID_AX] = LID_SIGN * math.radians(z["lid"])
        lid.delta_rotation_euler = Euler(d)
        d = [0.0, 0.0, 0.0]
        d[HASP_AX] = HASP_SIGN * math.radians(z["hasp"])
        hasp.delta_rotation_euler = Euler(d)
        shake.delta_rotation_euler = Euler((0.0, math.radians(z["roll"]), math.radians(z["yaw"])))
        shake.delta_location = (0.0, 0.0, z["hop"])
        want = []
        for k in range(2):
            wv = list(REST[k])
            wv[RING_AX[k]] += math.radians(z["ring"]) * (1 if k == 0 else -1)
            want.append(tuple(wv))
        set_rings(HOLD, want)
        dust.hide_render = True
        dust_gain.default_value = 0.0
        return HOLD
    if PIECE == "reveal":
        f = 50 + i
        scn.frame_set(f)
        set_rings(f, REST)
        dust.hide_render = True
        dust_gain.default_value = 0.0
        return f
    f = END + i                                                     # ending
    scn.frame_set(f)
    for o in rings:
        o.delta_rotation_euler = Euler((0, 0, 0))
    dust.hide_render = True
    dust_gain.default_value = 0.0
    return f


if PIECE in ("reveal", "ending"):
    # On the straight timeline the dust shaken from above is still falling at frame 50. In the pieces it finished
    # during the arrival's tail, so it must not come back when the reveal starts (it did, in the first render).
    for layer in story.animation_data.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path == '["dustfall"]':
                        for kp in fc.keyframe_points:
                            kp.co.y = kp.handle_left.y = kp.handle_right.y = 9.0
                        fc.update()

COUNT = {"arrival": N1 + 46, "waiting": 225, "waiting1": 75, "reveal": END - 50 + 1, "ending": LOOP + FADE}[PIECE]
only = [int(x) for x in E("ONLY").split(",")] if E("ONLY") else list(range(COUNT))


def settle():
    """Custom numbers set from here do not tell Blender they changed: say so, so the drivers that read them run."""
    story.update_tag()
    bpy.context.view_layer.update()
t0 = time.time()
for i in only:
    path = os.path.join(out, f"{i:04d}.png")
    if E("SKIP_DONE") and os.path.exists(path):
        continue
    f = state(i)
    settle()
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("V12 FRAME", PIECE, i, "scene", f, round(time.time() - t0, 1), "s", flush=True)
print("V12 DONE", PIECE, len(only), "frames", round(time.time() - t0, 1), "s", flush=True)
