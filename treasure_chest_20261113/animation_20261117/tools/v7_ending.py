"""Version 7 ending pose: the badge risen out of the open chest under one warm light from above
(owner, 2026-11-18: "how it looks when it is out of the chest and up and there is a light shining
down on it ... look good and cinematic").

Built in its own file, chest_reveal_v7_ending.blend (a copy of chest_reveal_v7.blend), like the dust:
lighting effects stay out of the core reveal file. Run inside Blender; safe to run again, no deletes.

The look:
- One warm spot high above the badge, a little toward the camera so the emblem's face still catches
  it. Its beam is visible in a faint haze that only this light lights, so it reads as a single shaft.
  The badge cuts a shadow into the shaft; the light spills past it into the open chest and pools on
  the floor.
- The stage's general lights dim as the badge arrives, so the room falls dark around the beam; a back
  light outlines the chest and the badge's rim.
- Slow dust motes drift in the beam (lit only where the beam is).
- Everything fades in from frame E0 to E1 (the badge rises from about 116 and settles at 185).
"""
import bpy, bmesh, math
from mathutils import Vector

scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
E0, E1 = globals().get("END_E0", 132), globals().get("END_E1", 186)
FLOOR = -2.455
BADGE = Vector((0.0, 0.0, 5.4))               # badge centre at the ending pose
WARM = (1.0, 0.86, 0.66)
P = dict(spot=globals().get("END_SPOT", 60000.0), spot_size=globals().get("END_SPOT_DEG", 25.2),   # 21 liked, then 10 then 20 percent wider
         haze=globals().get("END_HAZE", 0.018), motes=globals().get("END_MOTES", 1.0))
# ending energy of each existing light (start value is what the file has now)
DIM = dict(globals().get("END_DIM", {"Reveal Key": 0.28, "Reveal Fill": 0.25, "Reveal Top": 0.0, "Reveal Rim Right": 0.45,
                                     "Reveal Rim": 1.15, "Reveal Badge Key": 0.3, "Reveal Badge Rake": 0.8,
                                     "Reveal Badge Rim": 3.0}))


# ---------------------------------------------------------------- the badge's own rim pictures
# Star Ascent (the earlier badge, still in the file) and the app's 3 Days Total coin both name their rim
# pictures Rim_brushed_reference_*.png; on import Blender reused Star Ascent's silver one, so the rim
# showed white instead of the app's champagne brushed metal. Load the coin's own pictures from its USDZ.
import os, tempfile, zipfile
USDZ = os.path.join(os.path.dirname(bpy.data.filepath), "badge", "sprout_badge_mobile.usdz")
tmpd = tempfile.mkdtemp()
with zipfile.ZipFile(USDZ) as z:
    for fn in ("Rim_brushed_reference_color.png", "Rim_brushed_reference_roughness.png", "Rim_glint_reference_roughness.png"):
        z.extract("textures/" + fn, tmpd)
for mn in ("Silver___circumferential_brushed_steel_Mobile_Casing.001", "Shell_bevel.001", "Shell_inner.001"):
    for n in bpy.data.materials[mn].node_tree.nodes:
        if n.bl_idname == "ShaderNodeTexImage" and n.image:
            base = n.image.name.replace("Sprout ", "")
            if base.startswith("Rim_"):
                im = bpy.data.images.get("Sprout " + base)
                if im is None:
                    im = bpy.data.images.load(os.path.join(tmpd, "textures", base))
                    im.name = "Sprout " + base
                    im.pack()
                if "roughness" in base:
                    im.colorspace_settings.name = "Non-Color"
                n.image = im

# The app gives the brushed ring its anisotropy at runtime (found by name); without it the flat rim
# mirrors the badge's soft front lights as one even cream band. Brushed around the ring (tangent
# circling the coin's own z axis), like the app.
cm = bpy.data.materials["Silver___circumferential_brushed_steel_Mobile_Casing.001"]
bsdf = next(n for n in cm.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
tg = cm.node_tree.nodes.get("v7 ring brush") or cm.node_tree.nodes.new("ShaderNodeTangent")
tg.name = "v7 ring brush"
tg.direction_type = "RADIAL"
tg.axis = "Z"
cm.node_tree.links.new(tg.outputs["Tangent"], bsdf.inputs["Tangent"])
bsdf.inputs["Anisotropic"].default_value = globals().get("END_ANISO", 0.7)

# ---------------------------------------------------------------- the light from above
spot = bpy.data.objects["Reveal Overhead Light"]
spot.hide_render = False
spot.hide_viewport = False
spot.parent = None
# above and a little toward the camera. Owner, 2026-11-18: a wider beam leaning onto the chest's front
# was tried and rejected; kept the first look (21 degrees), then 10 percent wider and a touch forward.
CAMDIR = Vector((0.53, -0.848, 0.0))                       # from the chest toward the camera, flat
FWD = globals().get("END_SPOT_FWD", 1.4)   # 1.05 in the version the owner liked, then "a teeny tiny bit" to the front
spot.location = BADGE + CAMDIR * FWD + Vector((0.0, 0.0, globals().get("END_SPOT_UP", 18.5)))   # 17, then raised a little
AIM = BADGE + CAMDIR * globals().get('END_AIM_FWD', 0.35) + Vector((0.0, 0.0, globals().get('END_AIM_DZ', -0.6)))   # the beam moves forward with the light
d = AIM - spot.location
spot.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
L = spot.data
L.type = "SPOT"
L.color = WARM
L.spot_size = math.radians(P["spot_size"])
L.spot_blend = 0.4
L.shadow_soft_size = 0.35
L.use_shadow = True
L.volume_factor = 1.0
L.diffuse_factor = L.specular_factor = 1.0
if L.animation_data:
    L.animation_data_clear()                           # v5 drove it from the FX property: plain keys now
L.energy = 0.0
L.keyframe_insert("energy", frame=E0)
L.energy = P["spot"]
L.keyframe_insert("energy", frame=E1)

# ---------------------------------------------------------------- the room falls dark around the beam
START = {}
for n, k in DIM.items():
    o = bpy.data.objects[n]
    ld = o.data
    base = ld.get("v7_end_base", ld.energy)
    ld["v7_end_base"] = base
    START[n] = base
    if ld.animation_data and ld.animation_data.action:
        ld.animation_data_clear()
    ld.energy = base
    ld.keyframe_insert("energy", frame=E0)
    ld.energy = base * k
    ld.keyframe_insert("energy", frame=E1)
# Only the beam lights the haze. The other lights stop lighting volumes while the badge rises, not
# before: in the dust file they light the landing dust (in the ending file they are already 0).
for o in scn.objects:
    if o.type == "LIGHT" and o is not spot:
        ld = o.data
        vb = ld.get("v7_vol_base", ld.volume_factor)
        ld["v7_vol_base"] = vb
        ld.volume_factor = vb
        ld.keyframe_insert("volume_factor", frame=E0)
        ld.volume_factor = 0.0
        ld.keyframe_insert("volume_factor", frame=E1)
# the studio surroundings dim too: polished metal then mirrors a dark room with bright beam
# highlights instead of a bright studio (the badge's silver rim read as white)
wn = bpy.data.worlds["Reveal World"].node_tree
bg = wn.nodes["Background"]
wbase = wn.get("v7_end_base", bg.inputs["Strength"].default_value) if hasattr(wn, "get") else bg.inputs["Strength"].default_value
wn["v7_end_base"] = wbase
if wn.animation_data:
    wn.animation_data_clear()
bg.inputs["Strength"].default_value = wbase
bg.inputs["Strength"].keyframe_insert("default_value", frame=E0)
bg.inputs["Strength"].default_value = wbase * globals().get("END_WORLD", 0.3)
bg.inputs["Strength"].keyframe_insert("default_value", frame=E1)
# the back light warms a little (the beam's colour carried around the edges)
rim = bpy.data.objects["Reveal Badge Rim"].data
rim.color = (1.0, 0.9, 0.75)

# ---------------------------------------------------------------- a soft front light for the badge only
# Owner: the badge was not well lit (the emerald face read dark under the light from above). A broad
# soft light from the camera's side, linked to the badge alone, so the chest and room stay dark. Low
# specular so the champagne rim does not flood into one white band.
bf = bpy.data.objects.get("Reveal Ending Badge Light")
if bf is None:
    bf = bpy.data.objects.new("Reveal Ending Badge Light", bpy.data.lights.new("Reveal Ending Badge Light", "AREA"))
    FXC.objects.link(bf)
bl = bf.data
bl.type = "AREA"; bl.shape = "DISK"; bl.size = 4.0
bl.color = (1.0, 0.94, 0.86)
bl.specular_factor = globals().get("END_BADGE_SPEC", 0.35)
bl.volume_factor = 0.0
bf.location = BADGE + CAMDIR * 8.0 + Vector((0.0, 0.0, 2.2))
bf.rotation_euler = (BADGE - bf.location).to_track_quat("-Z", "Y").to_euler()
recv = bpy.data.collections.get("Reveal Ending Badge Light Receivers") or bpy.data.collections.new("Reveal Ending Badge Light Receivers")
badge_root = bpy.data.objects["Reveal Badge Model"]
for o in [badge_root] + list(badge_root.children_recursive):
    if o.type == "MESH" and o.name not in recv.objects:
        recv.objects.link(o)
bf.light_linking.receiver_collection = recv
if bl.animation_data:
    bl.animation_data_clear()
bl.energy = 0.0
bl.keyframe_insert("energy", frame=globals().get("END_BADGE_E0", 116))      # the badge starts to rise
bl.energy = globals().get("END_BADGE_LIGHT", 900.0)
bl.keyframe_insert("energy", frame=globals().get("END_BADGE_E1", 150))

# ---------------------------------------------------------------- haze: makes the beam visible
def box_mesh(bm, x0, x1, y0, y1, z0, z1):
    for v in bmesh.ops.create_cube(bm, size=1.0)["verts"]:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))


haze = bpy.data.objects.get("Reveal Ending Haze")
me = bpy.data.meshes.get("Reveal Ending Haze") or bpy.data.meshes.new("Reveal Ending Haze")
# a box along the beam (local -z runs down the beam from the light); the shader keeps haze only
# inside the cone, fading out at its edge, so the room around stays clear and dark
bm = bmesh.new(); box_mesh(bm, -7, 7, -7, 7, -30, -1.0); bm.to_mesh(me); bm.free()
if haze is None:
    haze = bpy.data.objects.new("Reveal Ending Haze", me)
    FXC.objects.link(haze)
haze.data = me
haze.parent = None
bpy.context.view_layer.update()                  # the spot was just moved: its world matrix is stale until updated
haze.matrix_world = spot.matrix_world.copy()     # (a first run in the dust file put the haze at the origin)
haze.display_type = "BOUNDS"
haze.visible_shadow = False
hm = bpy.data.materials.get("Reveal Ending Haze") or bpy.data.materials.new("Reveal Ending Haze")
hm.use_nodes = True
nt = hm.node_tree
nt.nodes.clear()
if nt.animation_data:
    nt.animation_data_clear()
N, Ln = nt.nodes, nt.links.new
out = N.new("ShaderNodeOutputMaterial")
pv = N.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (1.0, 0.95, 0.88, 1)
pv.inputs["Anisotropy"].default_value = 0.55        # forward scattering: the shaft glows toward the camera
tc = N.new("ShaderNodeTexCoord")
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 3.0
mr = N.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.3, 0.7
mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.55, 1.25
dens = N.new("ShaderNodeMath"); dens.operation = "MULTIPLY"; dens.name = "haze density"
dens.inputs[1].default_value = P["haze"]
Ln(tc.outputs["Object"], nz.inputs["Vector"])
Ln(nz.outputs["Fac"], mr.inputs["Value"])
# inside the cone: radius from the beam's axis over the cone radius at that depth
sep = N.new("ShaderNodeSeparateXYZ")
xy = N.new("ShaderNodeCombineXYZ")
ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
depth = N.new("ShaderNodeMath"); depth.operation = "MULTIPLY"; depth.inputs[1].default_value = -math.tan(math.radians(P["spot_size"] / 2))
rn = N.new("ShaderNodeMath"); rn.operation = "DIVIDE"
cone = N.new("ShaderNodeMapRange")
cone.inputs["From Min"].default_value, cone.inputs["From Max"].default_value = 0.45, 1.05
cone.inputs["To Min"].default_value, cone.inputs["To Max"].default_value = 1.0, 0.0
both = N.new("ShaderNodeMath"); both.operation = "MULTIPLY"
Ln(tc.outputs["Object"], sep.inputs[0])
Ln(sep.outputs["X"], xy.inputs["X"]); Ln(sep.outputs["Y"], xy.inputs["Y"])
Ln(xy.outputs[0], ln.inputs[0])
Ln(sep.outputs["Z"], depth.inputs[0])
Ln(ln.outputs["Value"], rn.inputs[0]); Ln(depth.outputs[0], rn.inputs[1])
Ln(rn.outputs[0], cone.inputs["Value"])
Ln(mr.outputs[0], both.inputs[0]); Ln(cone.outputs[0], both.inputs[1])
# only above the chest: the light pours down into it, the chest itself stays crisp
geo = N.new("ShaderNodeNewGeometry")
sepw = N.new("ShaderNodeSeparateXYZ")
above = N.new("ShaderNodeMapRange")
above.inputs["From Min"].default_value, above.inputs["From Max"].default_value = 2.3, 4.2
above.inputs["To Min"].default_value, above.inputs["To Max"].default_value = 0.0, 1.0
all3 = N.new("ShaderNodeMath"); all3.operation = "MULTIPLY"
Ln(geo.outputs["Position"], sepw.inputs[0])
Ln(sepw.outputs["Z"], above.inputs["Value"])
Ln(both.outputs[0], all3.inputs[0]); Ln(above.outputs[0], all3.inputs[1])
Ln(all3.outputs[0], dens.inputs[0])
Ln(dens.outputs[0], pv.inputs["Density"])
Ln(pv.outputs[0], out.inputs["Volume"])
nz.inputs["W"].default_value = 0.0
nz.inputs["W"].keyframe_insert("default_value", frame=1)
nz.inputs["W"].default_value = 0.9                  # the haze drifts slowly
nz.inputs["W"].keyframe_insert("default_value", frame=213)
# the haze comes up with the light (no faint shaft over the landing when other lights still light volumes)
dens.inputs[1].default_value = 0.0
dens.inputs[1].keyframe_insert("default_value", frame=E0)
dens.inputs[1].default_value = P["haze"]
dens.inputs[1].keyframe_insert("default_value", frame=E1)
haze.data.materials.clear()
haze.data.materials.append(hm)
haze.hide_render = False

# ---------------------------------------------------------------- dust motes drifting in the beam
mote_me = bpy.data.meshes.get("Reveal Ending Mote")
if mote_me is None:
    mote_me = bpy.data.meshes.new("Reveal Ending Mote")
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0); bm.to_mesh(mote_me); bm.free()
mote = bpy.data.objects.get("Reveal Ending Mote") or bpy.data.objects.new("Reveal Ending Mote", mote_me)
if mote.name not in FXC.objects:
    FXC.objects.link(mote)
mote.hide_render = True
mote.hide_viewport = True
mm = bpy.data.materials.get("Reveal Ending Mote") or bpy.data.materials.new("Reveal Ending Mote")
mm.use_nodes = True
bs = mm.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value = (0.9, 0.85, 0.75, 1)
bs.inputs["Roughness"].default_value = 0.35
mote_me.materials.clear(); mote_me.materials.append(mm)

em_me = bpy.data.meshes.get("Reveal Ending Mote Volume") or bpy.data.meshes.new("Reveal Ending Mote Volume")
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=3.6, radius2=0.8, depth=12.0)
bm.to_mesh(em_me); bm.free()
em = bpy.data.objects.get("Reveal Ending Mote Volume")
if em is None:
    em = bpy.data.objects.new("Reveal Ending Mote Volume", em_me)
    FXC.objects.link(em)
em.data = em_me
# on the beam's axis, only above the badge (specks over the wood read as noise)
_t = (spot.location.z - 14.6) / (spot.location.z - AIM.z)
em.location = spot.location.lerp(AIM, _t)
em.display_type = "WIRE"
em.show_instancer_for_render = False
em.show_instancer_for_viewport = False
ps_set = bpy.data.particles.get("Reveal Ending Motes") or bpy.data.particles.new("Reveal Ending Motes")
if not em.particle_systems:
    em.modifiers.new("Reveal Ending Motes", "PARTICLE_SYSTEM")
em.particle_systems[0].settings = ps_set
ps_set.count = 0                                   # resets the specks' saved positions (moving the
ps_set.count = int(260 * P["motes"])               # emitter alone kept the old ones)
ps_set.frame_start, ps_set.frame_end = 1, 1
ps_set.lifetime = 400
ps_set.emit_from = "VOLUME"
ps_set.physics_type = "NEWTON"
ps_set.normal_factor = 0.0
ps_set.factor_random = 0.05
ps_set.effector_weights.gravity = 0.0
ps_set.brownian_factor = 0.06                       # slow drift
ps_set.drag_factor = 0.3
ps_set.render_type = "OBJECT"
ps_set.instance_object = mote
ps_set.particle_size = 0.009
ps_set.size_random = 0.8
em.particle_systems[0].seed = 7
em.particle_systems[0].point_cache.frame_start, em.particle_systems[0].point_cache.frame_end = 1, 213
# motes only show once the light is up: the emitter object fades in by its visibility at E0
for f_, h_ in ((1, True), (E0, False)):
    em.hide_render = h_
    em.keyframe_insert("hide_render", frame=f_)

# ---------------------------------------------------------------- volumes in EEVEE and a soft bloom
ee = scn.eevee
ee.volumetric_tile_size = "2"
ee.volumetric_samples = 96
ee.volumetric_sample_distribution = 0.8
ee.use_volumetric_shadows = True
ee.volumetric_shadow_samples = 32
ee.volumetric_end = 45.0
g = [n for n in scn.compositing_node_group.nodes if n.bl_idname == "CompositorNodeGlare"][0]
g.mute = False
g.inputs["Highlights Threshold"].default_value = 1.0
g.inputs["Strength"].default_value = 0.42
g.inputs["Size"].default_value = 0.7
V7_ENDING = dict(spot=P["spot"], haze=P["haze"], start=START)
print("v7 ending", V7_ENDING)
