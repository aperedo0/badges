"""Shared helpers for the chest reveal animation (run inside Blender via exec).

Every section of the sequence keys its controllers through `Keys`. Each (section, object)
pair becomes one action named '<NN Section> | <object>' placed as an NLA strip on a track
of the same section name, so a section can later be lifted out and triggered on its own.
Strips hold forward, so a later section continues from where the earlier one stopped.
"""
import bpy, math

SECTIONS = [  # name, first frame, last frame
    ("00 Rest", 1, 1),          # bottom layer: every channel's starting value, held everywhere
    ("01 Landing", 1, 52),
    ("02 Mystery", 46, 92),
    ("03 Unlock", 90, 106),
    ("04 Opening", 104, 140),
    ("05 Badge Reveal", 112, 215),
]
SEC = {n: (a, b) for n, a, b in SECTIONS}
DEG = math.pi / 180


class Keys:
    """keys[(section, object name)][(data_path, index)] = list of key tuples.

    Key tuple: (frame, value) for auto clamped, (frame, value, "CONST") for a held step,
               (frame, value, "LIN") for a straight segment to the next key (baked physics), or
               (frame, value, slope_in, slope_out) for exact Hermite slopes (value units per frame),
               where a slope of None means auto clamped on that side.
    """

    def __init__(self):
        self.k = {}

    def add(self, section, obj, path, index, keys):
        self.k.setdefault((section, obj), {})[(path, index)] = keys


def _clear(obj_names, prefix_sections):
    for name in obj_names:
        o = bpy.data.objects[name]
        ad = o.animation_data
        if ad is None:
            continue
        ad.action = None
        for t in list(ad.nla_tracks):
            if t.name.startswith(tuple(prefix_sections)):
                ad.nla_tracks.remove(t)
    for a in list(bpy.data.actions):
        if a.name.startswith(tuple(prefix_sections)) and a.users == 0:
            bpy.data.actions.remove(a)


def _set_keys(fc, keys):
    fc.keyframe_points.clear()
    keys = sorted(keys, key=lambda k: k[0])
    fc.keyframe_points.add(len(keys))
    for i, k in enumerate(keys):            # index access: keyframe_points reallocates on insert
        kp = fc.keyframe_points[i]
        kp.co = (k[0], k[1])
        mode = k[2] if (len(k) == 3 and isinstance(k[2], str)) else None
        kp.interpolation = {"CONST": "CONSTANT", "LIN": "LINEAR"}.get(mode, "BEZIER")
        kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    fc.update()
    # exact slopes: FREE handles at one third of the neighbouring interval
    for i, k in enumerate(keys):
        if len(k) < 4:
            continue
        kp = fc.keyframe_points[i]
        f, v, sin, sout = k[0], k[1], k[2], k[3]
        hl, hr = tuple(kp.handle_left), tuple(kp.handle_right)
        kp.handle_left_type = kp.handle_right_type = "FREE"
        if sin is not None and i > 0:
            d = (f - keys[i - 1][0]) / 3.0
            hl = (f - d, v - sin * d)
        if sout is not None and i < len(keys) - 1:
            d = (keys[i + 1][0] - f) / 3.0
            hr = (f + d, v + sout * d)
        kp.handle_left, kp.handle_right = hl, hr
    fc.update()


def add_rest(keys):
    """'00 Rest' layer: for every channel, the value of its earliest key in any section."""
    order = {n: i for i, (n, a, b) in enumerate(SECTIONS)}
    first = {}
    for (sec, oname), chans in keys.k.items():
        if sec == "00 Rest":
            continue
        for ch, ks in chans.items():
            k0 = min(ks, key=lambda k: k[0])
            cur = first.get((oname, ch))
            if cur is None or (order[sec], k0[0]) < cur[0]:
                first[(oname, ch)] = ((order[sec], k0[0]), k0[1])
    for (oname, ch), (_, v) in first.items():
        keys.k.setdefault(("00 Rest", oname), {})[ch] = [(1, v)]


def build(keys, sections=None):
    sections = sections or [s[0] for s in SECTIONS]
    objs = sorted({o for (s, o) in keys.k if s in sections})
    _clear(objs, sections)
    order = {n: i for i, (n, a, b) in enumerate(SECTIONS)}
    made = []
    for (sec, oname), chans in sorted(keys.k.items(), key=lambda kv: order[kv[0][0]]):
        if sec not in sections:
            continue
        o = bpy.data.objects[oname]
        act = bpy.data.actions.new(f"{sec} | {oname}")
        act.use_fake_user = False
        slot = act.slots.new(id_type="OBJECT", name=oname)
        layer = act.layers.new("Layer")
        strip = layer.strips.new(type="KEYFRAME")
        cb = strip.channelbags.new(slot)
        for (path, idx), ks in chans.items():
            fc = cb.fcurves.new(path, index=idx)
            _set_keys(fc, ks)
        ad = o.animation_data or o.animation_data_create()
        track = ad.nla_tracks.new()
        track.name = sec
        a0 = min(k[0] for ks in chans.values() for k in ks)
        st = track.strips.new(sec, int(math.floor(a0)), act)
        try:
            st.action_slot = slot
        except Exception:
            pass
        st.extrapolation = "HOLD" if sec == "00 Rest" else "HOLD_FORWARD"
        st.blend_type = "REPLACE"
        st.use_sync_length = False
        made.append(act.name)
    # keep tracks in section order (earliest lowest) on each object
    return made


def markers(scn, items):
    for m in list(scn.timeline_markers):
        scn.timeline_markers.remove(m)
    for name, f in items:
        scn.timeline_markers.new(name, frame=int(f))


def damped(frames0, amp, period, tau, n, phase=0.0):
    """Per frame samples of a decaying oscillation starting at frames0."""
    out = []
    for i in range(n + 1):
        t = i
        out.append((frames0 + i, amp * math.exp(-t / tau) * math.sin(2 * math.pi * t / period + phase)))
    out[-1] = (out[-1][0], 0.0)
    return out
