"""Version 5 lighting, matched to the owner's golden reference image (run inside Blender after
build_fx.py; safe to run again, no deletes).

  Primary light from above: a broad warm champagne spot over the badge (lights the badge, the open
  chest, the haze and the smoke), soft streaked rays fanning down from above the frame (an additive
  card behind the chest), and a warm dark backdrop that glows behind the badge as the light comes up.
  Secondary light inside the chest: the interior lights and the old light column are cut to a faint
  glow (the column was the main light in version 4; now it must not read as a second beam).
  New FX Controls property 'overhead' (0 off, 1 full) drives everything above; the badge's own key,
  rake and rim lights follow it too and turn warm.
"""
import bpy, math
from mathutils import Vector, Matrix

scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
fx = bpy.data.objects["Reveal FX Controls"]
root = bpy.data.objects["Reveal Chest Root"]
if "overhead" not in fx:
    fx["overhead"] = 0.0
    fx.id_properties_ui("overhead").update(min=0.0, soft_max=2.0)
# a new property is only seen by drivers after the depsgraph is rebuilt (else they stay invalid)
fx.update_tag(refresh={"OBJECT"})
bpy.context.view_layer.update()

CHAMPAGNE = (1.0, 0.70, 0.40)
GAIN = dict(spot=globals().get("SPOT_W", 70000.0), rays=globals().get("RAYS", 0.75),
            back=globals().get("BACK", 0.10), back_base=0.010,
            beam=0.13, beam_outer=0.04, interior_light=115.0, seam_light=70.0, spill_light=330.0,
            core_interior=1.1, badge_key=1100.0, badge_rake=450.0, badge_rim=500.0, haze=0.018)


def drive(sock, path, expr, props, index=-1):
    try:
        sock.driver_remove(path, index) if index >= 0 else sock.driver_remove(path)
    except Exception:
        pass
    fc = sock.driver_add(path, index) if index >= 0 else sock.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for p in props:
        v = d.variables.new()
        v.name, v.type = p, "SINGLE_PROP"
        v.targets[0].id_type = "OBJECT"
        v.targets[0].id = fx
        v.targets[0].data_path = f'["{p}"]'
    d.expression = expr
    return fc


def plane(name, x0, x1, z0, z1, parent, loc):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me)
        FXC.objects.link(o)
    else:
        mats = list(o.data.materials)
        old = o.data
        o.data = me
        for m in mats:
            me.materials.append(m)
        if old.users == 0:
            bpy.data.meshes.remove(old)
    o.parent = parent
    o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = loc
    o.visible_shadow = False
    return o


class N:
    def __init__(self, mat):
        mat.use_nodes = True
        self.t = mat.node_tree
        self.t.nodes.clear()

    def n(self, kind, **kw):
        x = self.t.nodes.new(kind)
        for k, v in kw.items():
            setattr(x, k, v)
        return x

    def l(self, a, b):
        self.t.links.new(a, b)

    def m(self, op, a, b=None, clamp=False):
        x = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                x.inputs[i].default_value = v
            else:
                self.l(v, x.inputs[i])
        return x.outputs[0]

    def rng(self, v, a, b, c, d, interp="SMOOTHSTEP"):
        x = self.n("ShaderNodeMapRange", interpolation_type=interp)
        self.l(v, x.inputs[0])
        for i, val in zip((1, 2, 3, 4), (a, b, c, d)):
            x.inputs[i].default_value = val
        return x.outputs[0]


def additive(name, color, build_strength):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    g = N(m)
    out = g.n("ShaderNodeOutputMaterial")
    add = g.n("ShaderNodeAddShader")
    tr = g.n("ShaderNodeBsdfTransparent")
    em = g.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    strength = build_strength(g)
    g.l(strength, em.inputs["Strength"])
    g.l(tr.outputs[0], add.inputs[0]); g.l(em.outputs[0], add.inputs[1]); g.l(add.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    return m


# ---------------------------------------------------------------- the overhead spot
d = bpy.data.lights.get("Reveal Overhead Light") or bpy.data.lights.new("Reveal Overhead Light", "SPOT")
d.type = "SPOT"
d.color = CHAMPAGNE
d.spot_size = math.radians(56)
d.spot_blend = 0.9
d.shadow_soft_size = 3.0
d.use_shadow = True
d.volume_factor = 1.0
sp = bpy.data.objects.get("Reveal Overhead Light") or bpy.data.objects.new("Reveal Overhead Light", d)
if sp.name not in FXC.objects:
    FXC.objects.link(sp)
sp.parent = root
sp.matrix_parent_inverse = Matrix.Identity(4)
sp.location = (0.0, -3.2, 20.0)   # a little in front: the badge's shadow falls behind the chest
sp.rotation_euler = (Vector((0.0, 0.5, 1.5)) - Vector(sp.location)).to_track_quat("-Z", "Y").to_euler()
drive(d, "energy", f"{GAIN['spot']}*overhead", ["overhead"])

# ---------------------------------------------------------------- rays card behind the chest
# local origin = the rays' source above the frame; theta = angle from straight down, r = distance.
APEX_Z = 22.0
rays = plane("Reveal Overhead Rays", -16.0, 16.0, -APEX_Z - 1.0, -0.5, root, (0.0, 6.5, APEX_Z))


def rays_strength(g):
    tc = g.n("ShaderNodeTexCoord")
    sep = g.n("ShaderNodeSeparateXYZ")
    g.l(tc.outputs["Object"], sep.inputs[0])
    x, z = sep.outputs["X"], sep.outputs["Z"]
    th = g.m("ARCTAN2", x, g.m("MULTIPLY", z, -1.0))
    r = g.m("SQRT", g.m("ADD", g.m("MULTIPLY", x, x), g.m("MULTIPLY", z, z)))
    tw = g.n("ShaderNodeValue")
    tw.outputs[0].driver_add("default_value").driver.expression = "frame/140"
    streaks = []
    for k, sc, lo, hi in ((0, 9.0, 0.42, 0.68), (1, 23.0, 0.38, 0.72)):
        nz = g.n("ShaderNodeTexNoise", noise_dimensions="2D")
        nz.inputs["Scale"].default_value = sc
        nz.inputs["Detail"].default_value = 2.0
        cv = g.n("ShaderNodeCombineXYZ")
        g.l(g.m("ADD", th, float(k) * 3.1), cv.inputs["X"])
        g.l(tw.outputs[0], cv.inputs["Y"])
        g.l(cv.outputs[0], nz.inputs["Vector"])
        streaks.append(g.rng(nz.outputs["Fac"], lo, hi, 0.15, 1.0))
    streak = g.m("MULTIPLY", g.m("ADD", streaks[0], 0.35), g.m("ADD", streaks[1], 0.6))
    cone = g.rng(g.m("ABSOLUTE", th), math.radians(5), math.radians(21), 1.0, 0.0)
    fade = g.rng(r, 3.0, 19.0, 1.0, 0.1)
    bottom = g.rng(z, -20.5, -14.0, 0.0, 1.0)     # gone well above the floor: no seam
    fade = g.m("MULTIPLY", fade, bottom)
    top = g.rng(r, 2.0, 5.5, 0.0, 1.0)
    s = g.m("MULTIPLY", g.m("MULTIPLY", g.m("MULTIPLY", streak, cone), fade), top)
    gain = g.n("ShaderNodeMath", operation="MULTIPLY")
    gain.name = "gain"
    g.l(s, gain.inputs[0])
    drive(gain.inputs[1], "default_value", f"{GAIN['rays']}*overhead", ["overhead"])
    return gain.outputs[0]


rays.data.materials.clear()
rays.data.materials.append(additive("Reveal Overhead Rays", (1.0, 0.55, 0.20), rays_strength))

# ---------------------------------------------------------------- warm backdrop
back = plane("Reveal Backdrop", -40.0, 40.0, -2.0, 45.0, root, (0.0, 22.0, 0.0))


def back_strength(g):
    tc = g.n("ShaderNodeTexCoord")
    sep = g.n("ShaderNodeSeparateXYZ")
    g.l(tc.outputs["Object"], sep.inputs[0])
    x, z = sep.outputs["X"], sep.outputs["Z"]
    dz = g.m("SUBTRACT", z, 11.0)
    r = g.m("SQRT", g.m("ADD", g.m("MULTIPLY", g.m("MULTIPLY", x, x), 1.0), g.m("MULTIPLY", g.m("MULTIPLY", dz, dz), 0.55)))
    glow = g.rng(r, 0.0, 26.0, 1.0, 0.0)
    glow = g.m("POWER", glow, 2.2)
    glow = g.m("MULTIPLY", glow, g.rng(z, -1.0, 8.0, 0.15, 1.0))   # darker where it meets the floor
    gain = g.n("ShaderNodeMath", operation="MULTIPLY")
    gain.name = "gain"
    g.l(glow, gain.inputs[0])
    drive(gain.inputs[1], "default_value", f"{GAIN['back']}*overhead", ["overhead"])
    return g.m("ADD", gain.outputs[0], GAIN["back_base"])


bm = bpy.data.materials.get("Reveal Backdrop") or bpy.data.materials.new("Reveal Backdrop")
g = N(bm)
out = g.n("ShaderNodeOutputMaterial")
em = g.n("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.56, 0.26, 1)
g.l(back_strength(g), em.inputs["Strength"])
g.l(em.outputs[0], out.inputs["Surface"])
back.data.materials.clear()
back.data.materials.append(bm)

# ---------------------------------------------------------------- the chest's own light: secondary
for mname, key in (("Reveal Beam", "beam"), ("Reveal Beam Outer", "beam_outer")):
    gnode = bpy.data.materials[mname].node_tree.nodes["gain"]
    for f in gnode.id_data.animation_data.drivers:
        if 'nodes["gain"]' in f.data_path:
            ex = f.driver.expression
            f.driver.expression = f"{GAIN[key]}*" + ex.split("*", 1)[1]
il = bpy.data.objects["Reveal Interior Light"].data
drive(il, "energy", f"{GAIN['interior_light']}*interior_glow + {GAIN['seam_light']}*seam_glow", ["interior_glow", "seam_glow"])
il.volume_factor = 1.0
sl = bpy.data.objects["Reveal Spill Light"].data
drive(sl, "energy", f"{GAIN['spill_light']}*max(interior_glow-0.6,0)", ["interior_glow"])
sl.volume_factor = 0.6
for f in bpy.data.materials["Reveal Magic Core"].node_tree.animation_data.drivers:
    if "*interior_glow" in f.driver.expression:
        f.driver.expression = f.driver.expression.replace("1.9*interior_glow", f"{GAIN['core_interior']}*interior_glow")

# ---------------------------------------------------------------- badge lights follow the overhead light
for name, key, col in (("Reveal Badge Key", "badge_key", (1.0, 0.85, 0.62)),
                       ("Reveal Badge Rake", "badge_rake", (1.0, 0.86, 0.66)),
                       ("Reveal Badge Rim", "badge_rim", (1.0, 0.74, 0.40))):
    ld = bpy.data.objects[name].data
    ld.color = col
    drive(ld, "energy", f"{GAIN[key]}*min(overhead*1.4,1)", ["overhead"])

# haze: lit by the overhead spot now, it follows the overhead light as well as the chest glow
hz = bpy.data.materials["Reveal Haze"]
for f in hz.node_tree.animation_data.drivers:
    if 'nodes["density"]' in f.data_path:
        d_ = f.driver
        if not any(v.name == "overhead" for v in d_.variables):
            v = d_.variables.new(); v.name, v.type = "overhead", "SINGLE_PROP"
            v.targets[0].id_type = "OBJECT"; v.targets[0].id = fx; v.targets[0].data_path = '["overhead"]'
        d_.expression = f"{GAIN['haze']}*max(min(beam,1.3),overhead)"
for _m in ("Reveal Haze", "Reveal Overhead Rays", "Reveal Backdrop"):   # rebuild driver relations
    for _f in bpy.data.materials[_m].node_tree.animation_data.drivers:
        for _v in _f.driver.variables:
            if _v.targets[0].id:
                _v.targets[0].id = fx
bpy.context.view_layer.update()
for _c in (bpy.data.lights, bpy.data.materials):
    for _i in _c:
        for _t in [_i] + ([_i.node_tree] if getattr(_i, "node_tree", None) else []):
            if getattr(_t, "animation_data", None):
                for _f in _t.animation_data.drivers:
                    _f.driver.is_valid = True
# a touch more bloom so the badge rim glows warm like the reference (not a haze over everything)
_gl = next((n for n in scn.compositing_node_group.nodes if n.bl_idname == "CompositorNodeGlare"), None)
if _gl:
    _gl.inputs["Threshold"].default_value = 1.15
    _gl.inputs["Strength"].default_value = 0.34
LIGHT5 = dict(GAIN)
print("v5 light", LIGHT5)
