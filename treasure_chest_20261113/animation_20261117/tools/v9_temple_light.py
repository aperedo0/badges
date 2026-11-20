"""Version 9 temple lighting (run inside Blender after v9_temple_geo.py and v9_temple_mat.py; safe to run again).

The chest, badge, mist and specks keep their approved lights. The temple gets its own warm lights, and
light linking keeps them off the chest and badge (they light only the collection Temple Light Receivers):
- Temple Apse Sun: sun from high above the apse through the slatted opening in its ceiling, so it falls in
  streaks on the apse wall and floor behind the badge (the mockup's rays behind the arch).
- Temple Nave Glow: soft warm light from the bright beam over the chest into the hall: it lights the
  pillars' inner faces, the arches and the far floor, falling off with distance like the mockup.
- Temple Floor Sheen L/R: two warm lights low behind the pillars that the damp flagstones mirror as soft
  bright patches (the mockup's lit floor near the pillar bases).
The dais is lit by the chest's own lights (it sits in the same pool of light as the chest)."""
import bpy, math
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = coll("Temple Light Receivers", TC)
far = ["Temple Pillar Front L", "Temple Pillar Front R", "Temple Pillar Arcade L", "Temple Pillar Arcade R",
       "Temple Pillar Apse L", "Temple Pillar Apse R", "Temple Pillar Cracks", "Temple Apse Arch", "Temple Nave Arch",
       "Temple Arcade Arches", "Temple Walls", "Temple Apse Wall", "Temple Vault", "Temple Floor", "Temple Floor Bed"]
for nm in far + list(G("TEMPLE_EXTRA_RECEIVERS", [])):
    o = bpy.data.objects.get(nm)
    if o and o.name not in RECV.objects:
        RECV.objects.link(o)
RECV.hide_render = False
# the receivers collection only groups objects for linking; keep it out of the view layer's way
for lc in bpy.context.view_layer.layer_collection.children["Reveal"].children["Reveal Temple"].children:
    if lc.collection == RECV:
        lc.exclude = False


def light(name, kind, loc, aim, energy, color, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        ld = bpy.data.lights.new(name, kind)
        o = bpy.data.objects.new(name, ld)
        TC.objects.link(o)
    if o.data.type != kind:
        o.data.type = kind
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    d = Vector(aim) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    o.data.energy = energy
    o.data.color = color
    for k, v in kw.items():
        setattr(o.data, k, v)
    o.light_linking.receiver_collection = RECV
    return o


S = G("TEMPLE_LIGHT_SCALE", 1.0)
FLOOR_Z = G("TEMPLE_FLOOR", -0.55)
WARM = (1.0, 0.76, 0.46)
# sun into the apse through the slatted opening: aimed so the streaks fall on the apse wall above the badge
# Owner, 2026-11-19: the streaks this cast on the apse wall looked like a curtain, "just get rid of that".
# The light through the roof opening is off (kept in the file); a soft, shadowless glow high in the apse
# leaves the wall a plain warm gradient with no edges.
apse = light("Temple Apse Sun", "SPOT", (0.0, 97.0, 84.0), (0.0, 106.0, 28.0), G("APSE_E", 0.0) * S, WARM,
             spot_size=math.radians(30), spot_blend=0.6, shadow_soft_size=2.5, use_shadow=True)
light("Temple Apse Glow", "AREA", (0.0, 96.0, 37.0), (0.0, 104.0, 12.0), G("APSE_GLOW_E", 1500) * S, WARM,
      shape="DISK", size=14.0, use_shadow=False)
# warm light from high over the hall (the same opening the beam comes through): lights the pillars' inner
# faces and capitals, the arches and the floor between them, darker toward the edges and the camera
high = light("Temple High Light", "SPOT", (0.0, 4.0, 40.0), (0.0, 54.0, 6.0), G("HIGH_E", 26000) * S, (1.0, 0.8, 0.58),
             spot_size=math.radians(100), spot_blend=0.5, shadow_soft_size=3.0, use_shadow=True)
glow = light("Temple Nave Glow", "AREA", (0.0, 8.0, 17.0), (0.0, 70.0, 2.0), G("GLOW_E", 1500) * S, (1.0, 0.8, 0.55),
             shape="RECTANGLE", size=10.0, size_y=8.0, use_shadow=True)
for sx, nm in ((-1, "L"), (1, "R")):
    light("Temple Floor Sheen " + nm, "AREA", (sx * 9.0, 80.0, 6.0), (sx * 6.0, 12.0, -0.55), G("SHEEN_E", 1600) * S,
          (1.0, 0.78, 0.5), shape="DISK", size=9.0, use_shadow=True)
# the top of the apse arch catches the light falling past it (mockup: the arch's crown glows where the rays pass)
light("Temple Arch Crown Light", "SPOT", (0.0, 70.0, 66.0), (0.0, 86.0, 36.0), G("CROWN_E", 60000) * S, WARM,
      spot_size=math.radians(18), spot_blend=0.8, shadow_soft_size=1.0, use_shadow=True)
# soft warm light from the front low on the floor and the dais side (they read as dark holes otherwise);
# it reaches only the floor and the dais, never the chest
FRONT = coll("Temple Front Receivers", TC)
for nm in ("Temple Dais Blocks", "Temple Dais Top", "Temple Dais Gold Rings", "Temple Dais Ring Grooves"):
    o = bpy.data.objects.get(nm)
    if o and o.name not in FRONT.objects:
        FRONT.objects.link(o)
ff = light("Temple Front Fill", "AREA", (0.0, -24.0, 5.0), (0.0, 10.0, -0.55), G("FRONT_E", 3000) * S, (1.0, 0.82, 0.6),
           shape="RECTANGLE", size=24.0, size_y=6.0, use_shadow=True)
ff.light_linking.receiver_collection = FRONT
for nm in ("Temple Floor", "Temple Floor Bed"):          # the floor stays out of the front fill (earlier runs put it in)
    o = bpy.data.objects.get(nm)
    if o and o.name in FRONT.objects:
        FRONT.objects.unlink(o)
# the floor between the dais and the pillars: a broad pool from above (floor only)
FLOORS = coll("Temple Floor Receivers", TC)
for nm in ("Temple Floor", "Temple Floor Bed"):
    o = bpy.data.objects.get(nm)
    if o and o.name not in FLOORS.objects:
        FLOORS.objects.link(o)
fl = light("Temple Floor Light", "SPOT", (0.0, 26.0, 44.0), (0.0, 24.0, 0.0), G("FLOOR_E", 20000) * S, (1.0, 0.8, 0.58),
           spot_size=math.radians(92), spot_blend=1.0, shadow_soft_size=4.0, use_shadow=True)
fl.light_linking.receiver_collection = FLOORS
# warm pools of light on the floor (light falling through openings high above)
for nm, x, y, r, e in G("POOLS", [("L", -10.5, 30.0, 6.0, 0.8), ("R", 10.5, 33.0, 6.0, 0.75),
                                  ("LL", -6.8, 6.5, 3.6, 0.35), ("RR", 7.2, 7.5, 3.6, 0.3)]):
    z = 62.0
    pl = light("Temple Floor Pool " + nm, "SPOT", (x + 2.0, y - 6.0, z), (x, y, FLOOR_Z), G("POOL_E", 26000) * e * S,
               (1.0, 0.76, 0.5), spot_size=2 * math.atan(r / z), spot_blend=0.9, shadow_soft_size=2.5, use_shadow=True)
    pl.light_linking.receiver_collection = FLOORS
# warm key on the dais from the upper left (mockup: the dais top glows warm to the left of the chest); it
# reaches only the dais, the chest still casts its shadow into it
dk = light("Temple Dais Key", "SPOT", (-13.0, -9.0, 20.0), (-0.5, 0.5, 0.0), G("DAIS_E", 4000) * S, (1.0, 0.72, 0.44),
           spot_size=math.radians(34), spot_blend=0.7, shadow_soft_size=1.0, use_shadow=True)
dk.light_linking.receiver_collection = FRONT
# warm light raking the front pillars' inner faces (mockup: they catch the light from the middle of the hall)
for sx, nm in ((-1, "L"), (1, "R")):
    rk = light("Temple Pillar Rake " + nm, "SPOT", (sx * 2.0, 26.0, 24.0), (sx * 15.6, 58.0, 14.0), G("RAKE_E", 12000) * S,
               (1.0, 0.78, 0.52), spot_size=math.radians(16), spot_blend=0.8, shadow_soft_size=1.0, use_shadow=True)
    rk.light_linking.receiver_collection = RECV
SCN.eevee.shadow_pool_size = "1024"       # the temple's lights overflowed the 512 MB pool at full size (missing shadows)
vault = bpy.data.objects.get("Temple Vault")
if vault:
    vault.visible_shadow = False          # seen only from below in the opening shots; never blocks the hall's light
result = {"receivers": len(RECV.objects)}
