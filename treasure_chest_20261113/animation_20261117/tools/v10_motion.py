"""Version 10: an ending that keeps moving (owner, 2026-11-19: "there should be some continued movement since
the user will decide when to continue"). Run inside Blender after the other v10 scripts; safe to run again.

What moves after the reveal has finished, all of it slow:
- the beam's haze keeps drifting (its noise carried on past frame 213 at the same speed) and its rays shimmer;
- the specks in the beam, the ground mist and the far wisps already move with time;
- the platform's rings breathe: their glow rises and falls a little, once every LOOP frames.
The mist inside the chest is a baked simulation that ends at frame 213; temple/tools/loop_test.py holds it on
its last frame for a first look. How it should behave in an endless ending is still the owner's call."""
import bpy
G = globals().get
LOOP = G("LOOP_FRAMES", 90)
hm = bpy.data.materials["Reveal Ending Haze"]
ht = hm.node_tree
ad = ht.animation_data
if ad and ad.action:
    for layer in ad.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    if "Noise Texture" in fc.data_path:
                        fc.extrapolation = "LINEAR"
                        for k in fc.keyframe_points:
                            k.interpolation = "LINEAR"
nzr = ht.nodes["v10 ray noise"]
nzr.noise_dimensions = "4D"
try:
    nzr.inputs["W"].driver_remove("default_value")
except Exception:
    pass
d = nzr.inputs["W"].driver_add("default_value").driver
d.type = "SCRIPTED"
d.expression = "frame / %.1f" % G("RAY_SHIMMER", 420.0)
gm = bpy.data.materials["Temple Gold Inlay"]
pb = next(n for n in gm.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
sock = pb.inputs["Emission Strength"]
base = G("RING_GLOW", 0.55)
try:
    sock.driver_remove("default_value")
except Exception:
    pass
d = sock.driver_add("default_value").driver
d.type = "SCRIPTED"
d.expression = "%.3f * (1 + %.2f * sin(frame * %.7f))" % (base, G("RING_BREATH", 0.3), 6.2831853 / LOOP)
result = {"loop": LOOP}
