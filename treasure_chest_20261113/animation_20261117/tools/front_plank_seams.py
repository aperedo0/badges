"""Visible board seams on the outside front (owner, 2026-11-17: the front around the keyhole should
read as wooden planks like the lid and the reference). The front is already three separate plank
meshes (z 0.25 to 1.28, 1.28 to 1.81, 1.81 to 2.80) but their joints were nearly invisible.

Refined the same day: a thin crack instead of a broad soft band, a quarter round eased edge on each
board that catches light, and soft contact shading beside each joint.

Each plank material gets a groove along its top and bottom edge, measured in real units from the
plank's own UV (v runs bottom to top along z): the existing displacement height is pulled down into a
rounded groove, and the color darkens into the gap. Run inside Blender; safe to run again (removes
its own nodes first). Changes only the three front plank materials, no geometry.
"""
import bpy
import numpy as np

PLANKS = ("R Simple Front Plank01", "R Simple Front Plank02", "R Simple Front Plank03")
GAP = (0.005, 0.016)    # color: a thin dark crack, back to full tone at this distance from the seam
ROUND = 0.04            # rounded (quarter round) board edge width (units)
GROOVE = 0.3            # height at the seam (1 = surface); depth = (1 - GROOVE) * displacement scale
DARK = 0.15             # color in the crack
CONTACT = (0.72, 0.07)  # soft contact shading next to the joint: tone at the seam, width


def plank_height(o):
    M = np.array(o.matrix_parent_inverse)
    co = np.zeros(len(o.data.vertices) * 3)
    o.data.vertices.foreach_get("co", co)
    z = (M @ np.c_[co.reshape(-1, 3), np.ones(len(co) // 3)].T)[2]
    return float(z.max() - z.min())


def seams(o):
    m = o.data.materials[0]
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    for n in [n for n in N if n.name.startswith("Seam ")]:
        N.remove(n)
    bsdf, disp, uvn = N["Principled BSDF"], N["Displacement"], N["UV Map"]
    alb, hgt = N["Image Texture"], N["Image Texture.002"]
    H = plank_height(o)

    def node(kind, name, x, y, **kw):
        n = N.new(kind)
        n.name = n.label = "Seam " + name
        n.location = (x, y)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def math(op, name, a, b, x, y):
        n = node("ShaderNodeMath", name, x, y, operation=op)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    sep = node("ShaderNodeSeparateXYZ", "uv", -900, -700)
    L.new(uvn.outputs["UV"], sep.inputs[0])
    v = sep.outputs["Y"]
    e = math("MULTIPLY", "dist", math("MINIMUM", "edge", v, math("SUBTRACT", "flip", 1.0, v, -700, -760), -500, -700), H, -300, -700)

    def smooth(name, lo, hi, x, y):
        n = node("ShaderNodeMapRange", name, x, y, interpolation_type="SMOOTHSTEP")
        L.new(e, n.inputs[0])
        n.inputs[1].default_value, n.inputs[2].default_value = lo, hi
        return n.outputs[0]

    gap = smooth("gap", GAP[0], GAP[1], -100, -650)
    # quarter round edge: sqrt(t (2 - t)), t = distance / ROUND clamped; steep at the joint, flat after
    t = math("MINIMUM", "round t", math("DIVIDE", "round d", e, ROUND, -300, -850), 1.0, -200, -850)
    rnd = math("SQRT", "round", math("MULTIPLY", "round q", t, math("SUBTRACT", "round 2t", 2.0, t, -150, -900), -100, -850), None, 0, -850)
    contact = smooth("contact", 0.0, CONTACT[1], -100, -550)
    ctone = math("ADD", "contact tone", CONTACT[0], math("MULTIPLY", "contact k", contact, 1.0 - CONTACT[0], 100, -550), 300, -550)
    shade = math("MULTIPLY", "shade c", ctone,
                 math("ADD", "shade", DARK, math("MULTIPLY", "shade k", gap, 1.0 - DARK, 100, -650), 300, -650), 400, -600)
    mix = node("ShaderNodeMix", "color", 500, -300, data_type="RGBA", blend_type="MULTIPLY")
    mix.inputs[0].default_value = 1.0
    L.new(alb.outputs["Color"], mix.inputs[6])
    L.new(shade, mix.inputs[7])
    L.new(mix.outputs[2], bsdf.inputs["Base Color"])
    hb = node("ShaderNodeRGBToBW", "height bw", 100, -950)
    L.new(hgt.outputs["Color"], hb.inputs[0])
    prof = math("ADD", "profile", GROOVE, math("MULTIPLY", "profile k", rnd, 1.0 - GROOVE, 100, -850), 300, -850)
    L.new(math("MULTIPLY", "height", hb.outputs[0], prof, 500, -900), disp.inputs["Height"])
    return round(H, 3)


FRONT_SEAMS = {n: seams(bpy.data.objects[n]) for n in PLANKS}
print("front plank seams", FRONT_SEAMS)
