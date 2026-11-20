"""Version 10 lens look (run inside Blender, safe to run again): what a movie camera adds on top of the scene.
- Soft focus behind the chest: the chest and badge stay sharp, the temple behind is a little soft (it stops
  competing with them and reads as far away). Focus follows an empty on the chest.
- Darker corners (vignette) and a gentle grade (cooler shadows, warmer highlights) in the compositor, after the
  glow that was already there. No film grain: it costs a lot in a compressed phone movie.
LENS_FSTOP sets the softness (smaller is softer); VIGNETTE and GRADE set the strength of the other two (0 is off)."""
import bpy
G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
cam = bpy.data.objects["Reveal Camera"]
rootc = bpy.data.objects["Reveal Chest Root"]
f = bpy.data.objects.get("Reveal Focus")
if f is None:
    f = bpy.data.objects.new("Reveal Focus", None)
    bpy.data.collections["Reveal Stage"].objects.link(f)
f.parent = rootc
f.matrix_parent_inverse.identity()
f.location = G("FOCUS_AT", (0.0, -1.0, 5.0))
f.empty_display_size = 0.5
d = cam.data.dof
d.use_dof = G("LENS_DOF", True)
d.focus_object = f
d.aperture_fstop = G("LENS_FSTOP", 0.9)
d.aperture_blades = 0

# ---- compositor: glare (existing) -> vignette -> grade
nt = scn.compositing_node_group
N, L = nt.nodes, nt.links
glare = N["Glare"]
gout = next(n for n in N if n.bl_idname == "NodeGroupOutput")


def node(name, kinds):
    if name in N:
        return N[name]
    last = None
    for k in kinds:
        try:
            nd = N.new(k)
            nd.name = nd.label = name
            return nd
        except Exception as ex:
            last = ex
    raise last


VIG = G("VIGNETTE", 0.5)          # how much darker the far corners get (0 is off)
GRADE = G("GRADE", 1.0)
for stale in ("v10 vignette mask", "v10 vignette blur"):      # from an earlier draft of this script
    if stale in N:
        N.remove(N[stale])
co = node("v10 coordinates", ["CompositorNodeImageCoordinates"])
L.new(glare.outputs["Image"], co.inputs[0])
cen = node("v10 vignette centre", ["ShaderNodeVectorMath"])
cen.operation = "SUBTRACT"
L.new(co.outputs["Normalized"], cen.inputs[0])
cen.inputs[1].default_value = (0.5, 0.47, 0.0)             # a touch above the middle: the badge sits there
dist = node("v10 vignette distance", ["ShaderNodeVectorMath"])
dist.operation = "LENGTH"
L.new(cen.outputs["Vector"], dist.inputs[0])
fall = node("v10 vignette falloff", ["ShaderNodeMapRange"])
fall.interpolation_type = "SMOOTHSTEP"
L.new(dist.outputs["Value"], fall.inputs["Value"])
fall.inputs["From Min"].default_value, fall.inputs["From Max"].default_value = 0.30, 0.72
fall.inputs["To Min"].default_value, fall.inputs["To Max"].default_value = 1.0, 1.0 - VIG
mix = node("v10 vignette", ["ShaderNodeMix"])
mix.data_type = "RGBA"
mix.blend_type = "MULTIPLY"
mix.inputs[0].default_value = 1.0
L.new(glare.outputs["Image"], mix.inputs[6])
L.new(fall.outputs["Result"], mix.inputs[7])
cb = node("v10 grade", ["CompositorNodeColorBalance"])
L.new(mix.outputs[2], cb.inputs[0])
cb.inputs[1].default_value = GRADE
k = 0.0012
cb.inputs[4].default_value = (1.0 - k, 1.0, 1.0 + 1.6 * k, 1.0)     # lift: a breath of blue in the darkest shadows
cb.inputs[6].default_value = (1.0, 1.0, 1.0, 1.0)
cb.inputs[8].default_value = (1.035, 1.0, 0.955, 1.0)               # gain: warmer highlights
L.new(cb.outputs[0], gout.inputs[0])
result = {"dof": d.use_dof, "fstop": d.aperture_fstop, "coords_out": [o.name for o in co.outputs],
          "cb_type": str(cb.inputs[2].default_value), "nodes": [n.name for n in N]}
