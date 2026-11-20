"""Version 10 frame: the iPhone shaped picture and a level camera at the end of the reveal.

- Picture 1080 by 2340 (9 by 19.5, the shape of every current iPhone; an older 9 by 16 phone crops top and
  bottom). The lens goes from 35 to 28.72 mm so the width of the view is unchanged (the chest stays the same
  share of the width); the extra height is new picture above and below.
- The pillars looked slanted (owner, 2026-11-19): they are upright, the resting camera looked down 10 degrees.
  The camera now stays level whenever the dolly looks down and the lens shifts down instead (drivers on the
  camera read the dolly's pitch, so the dolly's animation is untouched). While the dolly looks up (the low
  opening shot) nothing changes. END_SHIFT moves the end framing up or down (share of the picture's height).
Run inside Blender; safe to run again."""
import bpy, math
G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
cam = bpy.data.objects["Reveal Camera"]
dolly = bpy.data.objects["Reveal Camera Dolly"]
cd = cam.data
RES = G("FRAME_RES", (1080, 2340))
OFF = G("END_SHIFT", 0.03)
scn.render.resolution_x, scn.render.resolution_y = RES
cd.sensor_fit = "AUTO"
cd.sensor_width = 36.0
cd.lens = 35.0 * 1920.0 / RES[1]


def drive(idb, path, index, expr, with_lens=False):
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except TypeError:
        pass
    fc = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name = "rx"
    v.type = "SINGLE_PROP"
    v.targets[0].id = dolly
    v.targets[0].data_path = "rotation_euler[0]"
    if with_lens:
        k = d.variables.new()
        k.name = "lens"
        k.type = "SINGLE_PROP"
        k.targets[0].id_type = "CAMERA"
        k.targets[0].id = cd
        k.targets[0].data_path = "lens"
    d.expression = expr
    return fc


drive(cam, "rotation_euler", 0, "max(0.0, 1.5707963 - rx)")
drive(cd, "shift_y", -1,
      "-(lens / 36.0) * tan(max(0.0, 1.5707963 - rx)) + %.5f * clamp((1.5707963 - rx) / 0.1745329, 0.0, 1.0)" % OFF,
      with_lens=True)
result = {"res": list(RES), "lens": round(cd.lens, 3)}
