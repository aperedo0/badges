"""Version 12: the mood of the dark start, and calmer fire (owner's third review, 2026-11-20). Run last, after
v12_dust.py; safe to run again.

- Darker start. "I want it to start off darker. I want there to be more mystery about what's behind ... I feel
  like I see too much of the background, especially that top wall ... it's showing way too much ... it's got to
  be revealed." Every light that shows the hall before the chest opens is set here as a pair: its level in the
  dark and its level once the gold light is up. Only the dark levels are lowered; the gold ending is as it was.
  The chest's own lights and the two shafts of night light are not touched.
- Calmer fire. "the light at the end, it twinkles way too fast ... like a third of this current speed."
  Measured in the ending: the torches' light swung on 3 and 8 frame beats (9 and 4 times a second). The
  torches' light, flames, glow, coals and sparks all run at a third of their speed now (`FIRE_SPEED`)."""
import bpy, re

G = globals().get
story = bpy.data.objects["Temple Story"]
OB = bpy.data.objects


def drv(idb, path, expr, **vs):
    try:
        idb.driver_remove(path)
    except Exception:
        pass
    d = idb.driver_add(path).driver
    d.type = "SCRIPTED"
    for nm, tpath in vs.items():
        v = d.variables.new()
        v.name = nm
        v.type = "SINGLE_PROP"
        v.targets[0].id = story
        v.targets[0].data_path = tpath
    d.expression = expr


# name: (in the dark before this change, in the dark now, in the gold light)
LEVELS = G("MOOD_LEVELS", {
    "Temple Moon Key":     (420000.0, 80000.0, 42000.0),      # rakes across the top wall and the arches
    "Temple Cool L":       (10800.0, 4200.0, 8000.0),
    "Temple Cool R":       (10800.0, 4200.0, 8000.0),
    "Temple Cool Top":     (750.0, 300.0, 3000.0),
    "Temple Floor Light":  (5600.0, 4300.0, 7000.0),
    "Temple Back Glow":    (149500.0, 62000.0, 130000.0),     # the haze at the far end of the long hall
    "Temple Back Floor":   (45000.0, 19000.0, 45000.0),
    "Temple Moon Shaft A": (220000.0, 95000.0, 55000.0),      # the faint shafts in the long hall
    "Temple Moon Shaft B": (176000.0, 76000.0, 44000.0),
})
# Owner's next note, same day: "in the beginning, the background can be about 10% brighter, or just a teeny tiny
# bit brighter, like really not much".
LIFT = G("DARK_LIFT", 1.12)
for nm, (_, dark, lit) in LEVELS.items():
    o = OB.get(nm)
    if o is not None:
        dark = dark * LIFT
        drv(o.data, "energy", "%.1f + %.1f * gold" % (dark, lit - dark), gold='["gold"]')

# The chest's front in the dark. "the top is like lit to how I want it. But the bottom half of the chest from the
# front is not lit well. You can't really see it. So I want the entire front of the chest to be lit like the top
# of the chest is." A soft light low in front of the chest, on the chest only, fading as the gold light comes.
root = OB["Reveal Chest Root"]
scn = bpy.data.scenes["Chest Reveal"]
cf = bpy.data.collections.get("Temple Chest Front Receivers")
if cf is None:
    cf = bpy.data.collections.new("Temple Chest Front Receivers")
    bpy.data.collections["Reveal Temple"].children.link(cf)


def below(o):
    for c in o.children:
        yield c
        yield from below(c)


for o in below(OB["Reveal Chest Shake"]):
    if o.type == "MESH" and o.name.startswith(("R ", "Inside", "Reveal Underside")) and o.name not in cf.objects:
        cf.objects.link(o)
fl = OB.get("Temple Chest Front")
if fl is None:
    fl = bpy.data.objects.new("Temple Chest Front", bpy.data.lights.new("Temple Chest Front", "AREA"))
    bpy.data.collections["Reveal Temple"].objects.link(fl)
from mathutils import Vector
fl.parent = root
fl.matrix_parent_inverse.identity()
fl.location = G("FRONT_AT", (0.0, -11.0, 1.2))
fl.rotation_euler = (Vector(G("FRONT_AIM", (0.0, -1.9, 1.5))) - Vector(fl.location)).to_track_quat("-Z", "Y").to_euler()
fl.data.shape = "RECTANGLE"
fl.data.size, fl.data.size_y = 7.0, 3.0
fl.data.color = (1.0, 0.9, 0.78)                 # warm, so the wood keeps its colour (cool white turned it pale)
fl.data.use_shadow = False
fl.data.volume_factor = 0.0
fl.light_linking.receiver_collection = cf
drv(fl.data, "energy", "%.1f * (1.0 - 0.75 * gold)" % G("FRONT_E", 190.0), gold='["gold"]')

# The air itself: the room's even ambient light (the world) is what made the long hall's haze glow pale, so the
# far end showed however low its own lights were set. It starts at about a third and comes up with the gold.
w = bpy.data.scenes["Chest Reveal"].world.node_tree
for layer in w.animation_data.action.layers:
    for st in layer.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                if 'nodes["Background"].inputs[1]' in fc.data_path and len(fc.keyframe_points) == 2:
                    k0, k1 = fc.keyframe_points
                    k0.co.y = k0.handle_left.y = k0.handle_right.y = k1.co.y * G("WORLD_DARK", 0.35) * LIFT
                    fc.update()

# ------------------------------------------------------------------ the fire at a third of its speed
# (The owner had meant the beam of light on the badge, not the torches: "The fire was fine." The fire is back at
# its own speed; the beam is left out of the render, see v12_render.py.)
K = G("FIRE_SPEED", 1.0)
BEATS = (0.83, 1.91)                              # the two beats the torches' light was built with (v11_torches.py)
done = {"lights": 0, "clocks": 0}
for o in OB:
    if o.type == "LIGHT" and o.name.startswith("Temple Torch") and o.data.animation_data:
        for fc in o.data.animation_data.drivers:
            ex = fc.driver.expression
            it = iter(BEATS)
            new = re.sub(r"sin\(frame \* [0-9.]+", lambda m: "sin(frame * %.4f" % (next(it) * K), ex)
            if new != ex:
                fc.driver.expression = new
                done["lights"] += 1
for m in bpy.data.materials:
    if not m.name.startswith("Temple") or not m.node_tree or not m.node_tree.animation_data:
        continue
    if not any(k in m.name for k in ("Flame", "Fire", "Ember", "Coal")):
        continue
    for fc in m.node_tree.animation_data.drivers:
        if re.fullmatch(r"frame / [0-9.]+", fc.driver.expression.strip()):
            fc.driver.expression = "frame / %.1f" % (30.0 / K)
            done["clocks"] += 1
result = {"mood": "ok", **done}
