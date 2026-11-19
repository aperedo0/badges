"""Magic and lighting effects for the Chest Reveal (run inside Blender; safe to run again, no deletes).

Every intensity is driven by a custom property on 'Reveal FX Controls' (keyhole_glow, seam_glow,
interior_glow, beam, flash), so effect timing lives in the animation and effect strength lives
here (the GAIN values).  Effects that sit in the chest are parented to the chest's Shake control
so they move with it; the beam is parented to the chest Root; the flash follows the badge."""
import bpy, math, bmesh
from mathutils import Vector, Matrix

scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
fx = bpy.data.objects["Reveal FX Controls"]
shake = bpy.data.objects["Reveal Chest Shake"]
root = bpy.data.objects["Reveal Chest Root"]
badge = bpy.data.objects["Reveal Badge Root"]
FLOOR = -2.455
GOLD = (1.0, 0.63, 0.22)
GOLD_HOT = (1.0, 0.78, 0.45)

GAIN = dict(keyhole_card=26.0, seam_strip=9.0, keyhole_light=16.0, keyhole_inner=6.0,
            core_seam=3.0, core_interior=1.9, interior_light=150.0, seam_light=70.0,
            spill_light=650.0, beam=0.55, beam_outer=0.16, haze=0.022, flash_light=900.0,
            badge_key=430.0, badge_rake=360.0, badge_rim=230.0, glint=1000.0)
for _p in ("glint",):
    if _p not in fx:
        fx[_p] = 0.0


def drive(owner, path, expr, props, index=-1):
    owner.driver_remove(path, index) if index >= 0 else owner.driver_remove(path)
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for p in props:
        v = d.variables.new()
        v.name = p
        v.type = "SINGLE_PROP"
        v.targets[0].id_type = "OBJECT"
        v.targets[0].id = fx
        v.targets[0].data_path = f'["{p}"]'
    d.expression = expr
    return fc


def put(o, parent, local):
    """parent o to a rig empty and place it at chest-frame coordinates (z from the floor)."""
    o.parent = parent
    o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = local


def mesh_obj(name, build):
    """create the object once; its mesh is rebuilt every run (the old mesh data is released)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me)
        FXC.objects.link(o)
    else:
        old = o.data
        mats = list(old.materials)
        o.data = me
        for m in mats:
            me.materials.append(m)
        if old.users == 0:
            bpy.data.meshes.remove(old)
    return o


def light(name, kind, color, radius=0.1):
    d = bpy.data.lights.get(name) or bpy.data.lights.new(name, kind)
    d.type = kind
    d.color = color
    if kind in ("POINT", "SPOT"):
        d.shadow_soft_size = radius
    d.use_shadow = True
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, d)
        FXC.objects.link(o)
    return o


def emission_mat(name, color, gain, prop_expr, props, extra=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    if extra:
        extra(nt, em, out)
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    drive(em.inputs["Strength"], "default_value", f"{gain}*({prop_expr})", props)
    return m


# ---------------------------------------------------------------- keyhole
# A glowing card inside the lock case, behind the bore (visible only through the keyhole),
# a small light just inside it for the bore walls, and one just in front for the plate.
def card(bm):
    for x, z in ((-0.26, -0.37), (0.26, -0.37), (0.26, -1.06), (-0.26, -1.06)):
        bm.verts.new((x, 0.0, z + 0.70))
    bm.faces.new(bm.verts)
kc = mesh_obj("Reveal Keyhole Glow Card", card)
put(kc, shake, (0.0, -1.985, -0.70 - FLOOR))
def radial(nt, em, out):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.2, 2.2, 2.2)
    mp.inputs["Location"].default_value = (0.0, 0.0, 0.08)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.85, 0.25, 0.03, 1)
    ramp.color_ramp.elements[1].color = (1.0, 0.62, 0.22, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], gr.inputs[0])
    nt.links.new(gr.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
kc.data.materials.clear()
kc.data.materials.append(emission_mat("Reveal Keyhole Glow", GOLD, GAIN["keyhole_card"], "keyhole_glow",
                                      ["keyhole_glow"], radial))
kl = light("Reveal Keyhole Light", "POINT", GOLD, 0.06)
put(kl, shake, (0.0, -2.36, -0.62 - FLOOR))
drive(kl.data, "energy", f"{GAIN['keyhole_light']}*keyhole_glow", ["keyhole_glow"])
ki = light("Reveal Keyhole Inner Light", "POINT", GOLD_HOT, 0.05)
put(ki, shake, (0.0, -2.02, -0.66 - FLOOR))
drive(ki.data, "energy", f"{GAIN['keyhole_inner']}*keyhole_glow", ["keyhole_glow"])

# ---------------------------------------------------------------- inside the chest
# The magic core: a glowing sheet just under the rim (seen through the seam, then pouring out).
def core(bm):
    for x, y in ((-2.45, -1.5), (2.45, -1.5), (2.45, 1.5), (-2.45, 1.5)):
        bm.verts.new((x, y, 0.0))
    bm.faces.new(bm.verts)
co = mesh_obj("Reveal Magic Core", core)
put(co, shake, (0.0, 0.0, -0.25 - FLOOR))
def core_shader(nt, em, out):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9
    nz.inputs["Detail"].default_value = 3
    w = nt.nodes.new("ShaderNodeValue"); w.name = "time"
    drv = w.outputs[0].driver_add("default_value"); drv.driver.expression = "frame/90"
    nz.noise_dimensions = "4D"
    nt.links.new(w.outputs[0], nz.inputs["W"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (1.0, 0.36, 0.05, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (1.0, 0.72, 0.32, 1)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
co.data.materials.clear()
co.data.materials.append(emission_mat("Reveal Magic Core", GOLD, 1.0,
                                      f"{GAIN['core_seam']}*seam_glow + {GAIN['core_interior']}*interior_glow",
                                      ["seam_glow", "interior_glow"], core_shader))
il = light("Reveal Interior Light", "POINT", GOLD, 0.6)
put(il, shake, (0.0, 0.0, -0.35 - FLOOR))
drive(il.data, "energy", f"{GAIN['interior_light']}*interior_glow + {GAIN['seam_light']}*seam_glow",
      ["interior_glow", "seam_glow"])
# Light under the lid: fills the lid's underside and lifts the badge from below as it rises.
sl = light("Reveal Spill Light", "AREA", GOLD_HOT)
sl.data.shape = "RECTANGLE"
sl.data.size, sl.data.size_y = 4.6, 2.8
sl.data.spread = math.radians(70)           # a shaft through the opening, not a flood
put(sl, shake, (0.0, 0.0, 0.30 - FLOOR))
sl.rotation_euler = (math.pi, 0, 0)          # area lights shine down -z: flip to shine up
drive(sl.data, "energy", f"{GAIN['spill_light']}*max(interior_glow-0.6,0)", ["interior_glow"])

# Seam strip: a thin glowing band just inside the lid seam. Hidden by the iron bands while the
# lid is shut; when pressure lifts the lid, it shows as a line of gold light along the seam.
def seam(bm):
    x, y, h = 2.48, 1.52, 0.035
    ring = [(-x, -y), (x, -y), (x, y), (-x, y)]
    lo = [bm.verts.new((a, b, -h)) for a, b in ring]
    hi = [bm.verts.new((a, b, h)) for a, b in ring]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
ss = mesh_obj("Reveal Seam Glow", seam)
put(ss, shake, (0.0, 0.0, 0.372 - FLOOR))
ss.data.materials.clear()
ss.data.materials.append(emission_mat("Reveal Seam Glow", (1.0, 0.6, 0.2), GAIN["seam_strip"], "seam_glow", ["seam_glow"]))
ss.visible_shadow = False

# ---------------------------------------------------------------- light column
# Two soft layers (a narrow core and a wide faint veil), each a flared open cone whose glow fades
# upward, softens toward its silhouette and carries slow drifting vertical streaks and a flicker.
def cone(r0, r1, r2, h=10.0, segs=64):
    def build(bm):
        rings = []
        for z, r in ((0.0, r0), (h * 0.3, r1), (h, r2)):
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / segs), r * 0.62 * math.sin(2 * math.pi * i / segs), z))
                          for i in range(segs)])
        for a_, b_ in zip(rings, rings[1:]):
            for i in range(segs):
                bm.faces.new((a_[i], a_[(i + 1) % segs], b_[(i + 1) % segs], b_[i]))
    return build


def beam_material(name, gain_key, phase, edge_pow, streak_scale):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    add = nt.nodes.new("ShaderNodeAddShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.62, 0.24, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    up = nt.nodes.new("ShaderNodeMapRange")          # strongest at the chest, gone near the top
    up.inputs["From Min"].default_value, up.inputs["From Max"].default_value = 0.0, 9.0
    up.inputs["To Min"].default_value, up.inputs["To Max"].default_value = 1.0, 0.0
    up.interpolation_type = "SMOOTHERSTEP"
    upp = nt.nodes.new("ShaderNodeMath"); upp.operation = "POWER"; upp.inputs[1].default_value = 1.6
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    edge = nt.nodes.new("ShaderNodeMath"); edge.operation = "POWER"; edge.inputs[1].default_value = edge_pow
    streak = nt.nodes.new("ShaderNodeTexNoise"); streak.noise_dimensions = "4D"
    streak.inputs["Scale"].default_value = streak_scale; streak.inputs["Detail"].default_value = 3
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.6, 1.6, 0.1)
    tw = nt.nodes.new("ShaderNodeValue"); tw.name = "time"
    tw.outputs[0].driver_add("default_value").driver.expression = f"frame/55+{phase}"
    sr = nt.nodes.new("ShaderNodeMapRange")
    sr.inputs["From Min"].default_value, sr.inputs["From Max"].default_value = 0.3, 0.72
    sr.inputs["To Min"].default_value, sr.inputs["To Max"].default_value = 0.25, 1.35
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    g = nt.nodes.new("ShaderNodeMath"); g.operation = "MULTIPLY"; g.name = "gain"
    L = nt.links.new
    L(tc.outputs["Object"], sep.inputs[0]); L(sep.outputs["Z"], up.inputs["Value"]); L(up.outputs["Result"], upp.inputs[0])
    L(lw.outputs["Facing"], inv.inputs[1]); L(inv.outputs[0], edge.inputs[0])
    L(tc.outputs["Object"], mp.inputs["Vector"]); L(mp.outputs[0], streak.inputs["Vector"]); L(tw.outputs[0], streak.inputs["W"])
    L(streak.outputs["Fac"], sr.inputs["Value"])
    L(upp.outputs[0], m1.inputs[0]); L(edge.outputs[0], m1.inputs[1])
    L(m1.outputs[0], m2.inputs[0]); L(sr.outputs["Result"], m2.inputs[1])
    L(m2.outputs[0], g.inputs[0]); L(g.outputs[0], em.inputs["Strength"])
    L(tr.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1]); L(add.outputs[0], out.inputs["Surface"])
    # gain with a slow, irregular flicker (sum of two slow waves)
    drive(g.inputs[1], "default_value",
          f"{GAIN[gain_key]}*beam*(1+0.09*sin(frame*0.23+{phase})+0.06*sin(frame*0.61+{2*phase}))", ["beam"])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


for name, shape, gkey, ph, ep, sc in (("Reveal Light Beam", (1.0, 1.35, 2.0), "beam", 0.0, 3.2, 2.6),
                                      ("Reveal Light Beam Outer", (1.6, 2.2, 3.4), "beam_outer", 1.7, 4.5, 1.6)):
    bo = mesh_obj(name, cone(*shape))
    put(bo, root, (0.0, 0.0, 0.35 - FLOOR))
    for poly in bo.data.polygons:
        poly.use_smooth = True
    bo.data.materials.clear()
    bo.data.materials.append(beam_material("Reveal Beam" if gkey == "beam" else "Reveal Beam Outer", gkey, ph, ep, sc))
    bo.visible_shadow = False
    drive(bo, "scale", "0.2+0.8*min(beam,1)", ["beam"], 2)        # grows upward as the lid opens
    for i in (0, 1):
        drive(bo, "scale", "0.8+0.2*min(beam,1)", ["beam"], i)

# Haze above the chest: a thin volume lit only by the lights that come out of the chest, so the
# opening itself shapes a real shaft of light. Studio lights do not light it (volume factor 0).
def box_mesh(bm):
    bmesh.ops.create_cube(bm, size=1.0)
hz = mesh_obj("Reveal Light Haze", box_mesh)
put(hz, root, (0.0, 0.0, 2.9 - FLOOR + 5.0))
hz.scale = (6.6, 4.6, 10.0)
hm = bpy.data.materials.get("Reveal Haze") or bpy.data.materials.new("Reveal Haze")
hm.use_nodes = True
ht = hm.node_tree
ht.nodes.clear()
hout = ht.nodes.new("ShaderNodeOutputMaterial")
pv = ht.nodes.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (1.0, 0.8, 0.55, 1)
pv.inputs["Anisotropy"].default_value = 0.55
htc = ht.nodes.new("ShaderNodeTexCoord")
hn = ht.nodes.new("ShaderNodeTexNoise"); hn.noise_dimensions = "4D"; hn.inputs["Scale"].default_value = 1.4
hw = ht.nodes.new("ShaderNodeValue"); hw.outputs[0].driver_add("default_value").driver.expression = "frame/120"
hr = ht.nodes.new("ShaderNodeMapRange")
hr.inputs["From Min"].default_value, hr.inputs["From Max"].default_value = 0.35, 0.7
hr.inputs["To Min"].default_value, hr.inputs["To Max"].default_value = 0.35, 1.0
hfade = ht.nodes.new("ShaderNodeMapRange")              # thins out with height
hfade.inputs["From Min"].default_value, hfade.inputs["From Max"].default_value = -0.5, 0.5
hfade.inputs["To Min"].default_value, hfade.inputs["To Max"].default_value = 1.0, 0.0
hsep = ht.nodes.new("ShaderNodeSeparateXYZ")
# soft round footprint: zero density at the box sides, so the volume never shows its box
hxy = ht.nodes.new("ShaderNodeCombineXYZ")
hlen = ht.nodes.new("ShaderNodeVectorMath"); hlen.operation = "LENGTH"
hrad = ht.nodes.new("ShaderNodeMapRange")
hrad.inputs["From Min"].default_value, hrad.inputs["From Max"].default_value = 0.12, 0.48
hrad.inputs["To Min"].default_value, hrad.inputs["To Max"].default_value = 1.0, 0.0
hrad.interpolation_type = "SMOOTHERSTEP"
hbot = ht.nodes.new("ShaderNodeMapRange")              # and fades in above the rim
hbot.inputs["From Min"].default_value, hbot.inputs["From Max"].default_value = -0.5, -0.38
hbot.inputs["To Min"].default_value, hbot.inputs["To Max"].default_value = 0.0, 1.0
hm1 = ht.nodes.new("ShaderNodeMath"); hm1.operation = "MULTIPLY"
hm2 = ht.nodes.new("ShaderNodeMath"); hm2.operation = "MULTIPLY"
hm3 = ht.nodes.new("ShaderNodeMath"); hm3.operation = "MULTIPLY"
hd = ht.nodes.new("ShaderNodeMath"); hd.operation = "MULTIPLY"; hd.name = "density"
L = ht.links.new
L(htc.outputs["Generated"], hn.inputs["Vector"]); L(hw.outputs[0], hn.inputs["W"]); L(hn.outputs["Fac"], hr.inputs["Value"])
L(htc.outputs["Object"], hsep.inputs[0]); L(hsep.outputs["Z"], hfade.inputs["Value"]); L(hsep.outputs["Z"], hbot.inputs["Value"])
L(hsep.outputs["X"], hxy.inputs["X"]); L(hsep.outputs["Y"], hxy.inputs["Y"]); L(hxy.outputs[0], hlen.inputs[0])
L(hlen.outputs["Value"], hrad.inputs["Value"])
L(hr.outputs["Result"], hm1.inputs[0]); L(hfade.outputs["Result"], hm1.inputs[1])
L(hm1.outputs[0], hm2.inputs[0]); L(hrad.outputs["Result"], hm2.inputs[1])
L(hm2.outputs[0], hm3.inputs[0]); L(hbot.outputs["Result"], hm3.inputs[1])
L(hm3.outputs[0], hd.inputs[0]); L(hd.outputs[0], pv.inputs["Density"])
L(pv.outputs[0], hout.inputs["Volume"])
drive(hd.inputs[1], "default_value", f"{GAIN['haze']}*min(beam,1.3)", ["beam"])
hz.data.materials.clear()
hz.data.materials.append(hm)
hz.visible_shadow = False
for ln in ("Reveal Key", "Reveal Fill", "Reveal Rim", "Reveal Rim Right", "Reveal Top"):
    lo_ = bpy.data.objects.get(ln)
    if lo_:
        lo_.data.volume_factor = 0.0
e = scn.eevee
e.volumetric_tile_size = "8"
e.volumetric_samples = 48
e.use_volumetric_shadows = True
e.volumetric_start, e.volumetric_end = 5.0, 40.0

# ---------------------------------------------------------------- flash at the badge
flo = light("Reveal Flash Light", "POINT", GOLD_HOT, 1.2)
flo.parent = badge
flo.matrix_parent_inverse = Matrix.Identity(4)
flo.location = (0, -1.2, 0)
drive(flo.data, "energy", f"{GAIN['flash_light']}*flash", ["flash"])

# hero key light for the badge only (light linked), so the silver reads in the final pose
bk = light("Reveal Badge Key", "AREA", (1.0, 0.95, 0.88))
bk.data.size = 2.5
bk.location = (-5.5, -10.0, 9.5)
bk.rotation_euler = (Vector((0, 0, 6.15)) - Vector(bk.location)).to_track_quat("-Z", "Y").to_euler()
bk.data.light_linking if False else None
bk.light_linking.receiver_collection = bpy.data.collections["Reveal Badge"]
drive(bk.data, "energy", f"{GAIN['badge_key']}*min(beam*2,1)", ["beam"])

# raking light from the upper left so the embossed relief reads, and a cool back light that
# separates the badge from the dark (both light linked to the badge only)
for name, loc, col, gkey, size in (("Reveal Badge Rake", (-4.6, -2.2, 8.4), (1.0, 0.93, 0.82), "badge_rake", 1.4),
                                   ("Reveal Badge Rim", (2.8, 4.5, 8.8), (0.7, 0.8, 1.0), "badge_rim", 2.0)):
    lo_ = light(name, "AREA", col)
    lo_.data.size = size
    lo_.location = loc
    lo_.rotation_euler = (Vector((0, 0, 6.15)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    lo_.light_linking.receiver_collection = bpy.data.collections["Reveal Badge"]
    lo_.data.volume_factor = 0.0
    drive(lo_.data, "energy", f"{GAIN[gkey]}*min(beam*2,1)", ["beam"])
bk.data.volume_factor = 0.0
# the glint: a long thin light that sweeps past the badge's face at the climax
gli = light("Reveal Badge Glint", "AREA", (1.0, 0.97, 0.9))
gli.data.shape = "RECTANGLE"
gli.data.size, gli.data.size_y = 0.35, 7.0
gli.data.volume_factor = 0.0
gli.parent = badge
gli.matrix_parent_inverse = Matrix.Identity(4)
gli.location = (-4.5, -3.4, 0.9)
gli.rotation_euler = (0, 0, 0)
gli.constraints.clear()
tt = gli.constraints.new("TRACK_TO")
tt.target = badge
tt.track_axis, tt.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
gli.light_linking.receiver_collection = bpy.data.collections["Reveal Badge"]
drive(gli.data, "energy", f"{GAIN['glint']}*glint", ["glint"])

# badge-only lights cast no shadows (keeps EEVEE's shadow buffer within its pool at the climax)
for _n in ("Reveal Badge Key", "Reveal Badge Rake", "Reveal Badge Rim", "Reveal Badge Glint", "Reveal Flash Light"):
    bpy.data.objects[_n].data.use_shadow = False

# glow-only objects must not cast shadows or block the light that should pass them
for o in (kc, co):
    o.visible_shadow = False

# ---------------------------------------------------------------- bloom (compositor)
ng = scn.compositing_node_group
if ng is None or ng.name != "Reveal Compositor":
    ng = bpy.data.node_groups.get("Reveal Compositor") or bpy.data.node_groups.new("Reveal Compositor", "CompositorNodeTree")
    scn.compositing_node_group = ng
ng.nodes.clear()
for s in list(ng.interface.items_tree):
    ng.interface.remove(s)
ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
rl = ng.nodes.new("CompositorNodeRLayers")
gl = ng.nodes.new("CompositorNodeGlare")
go = ng.nodes.new("NodeGroupOutput")
gl.inputs["Type"].default_value = "Bloom" if "Type" in gl.inputs else None
try:
    gl.inputs["Threshold"].default_value = 1.4
    gl.inputs["Strength"].default_value = 0.28
    gl.inputs["Size"].default_value = 0.6
except Exception as e:
    print("glare inputs", [i.name for i in gl.inputs], e)
ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
ng.links.new(gl.outputs["Image"], go.inputs[0])
scn.render.use_compositing = True
print("fx ok")
