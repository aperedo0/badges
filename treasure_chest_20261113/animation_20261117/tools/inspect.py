import bpy, json, sys
from mathutils import Vector
out = {"version": bpy.app.version_string, "scenes": {}}
for s in bpy.data.scenes:
    out["scenes"][s.name] = {"engine": s.render.engine, "fps": s.render.fps, "frames": [s.frame_start, s.frame_end],
        "camera": s.camera.name if s.camera else None, "objects": len(s.objects), "res": [s.render.resolution_x, s.render.resolution_y]}
objs = {}
for o in bpy.data.objects:
    d = {"type": o.type, "parent": o.parent.name if o.parent else None, "ptype": o.parent_type,
         "loc": [round(v,4) for v in o.location], "rot": [round(v,4) for v in o.rotation_euler], "scl": [round(v,4) for v in o.scale],
         "users_scene": [s.name for s in o.users_scene], "hide_render": o.hide_render}
    if o.parent_bone: d["pbone"] = o.parent_bone
    if o.constraints: d["con"] = [(c.type, getattr(c, "target", None) and c.target.name, getattr(c,"subtarget","")) for c in o.constraints]
    if o.modifiers: d["mods"] = [(m.type, m.name) for m in o.modifiers]
    if o.animation_data: d["anim"] = [o.animation_data.action.name if o.animation_data.action else None, len(o.animation_data.drivers)]
    if o.type == "MESH":
        mw = o.matrix_world
        cs = [mw @ Vector(c) for c in o.bound_box]
        d["bb"] = [[round(min(c[i] for c in cs),3) for i in range(3)], [round(max(c[i] for c in cs),3) for i in range(3)]]
        d["verts"] = len(o.data.vertices)
        d["mats"] = [m.name if m else None for m in o.data.materials][:4]
        d["omats"] = [ (s.link, s.material.name if s.material else None) for s in o.material_slots if s.link=="OBJECT"][:2]
    if o.type == "ARMATURE":
        d["bones"] = {b.name: {"parent": b.parent.name if b.parent else None, "head": [round(v,3) for v in b.head_local], "tail": [round(v,3) for v in b.tail_local]} for b in o.data.bones}
    objs[o.name] = d
out["objects"] = objs
out["collections"] = {c.name: {"objs": len(c.objects), "children": [x.name for x in c.children]} for c in bpy.data.collections}
out["actions"] = [a.name for a in bpy.data.actions]
json.dump(out, open(sys.argv[-1], "w"), indent=1)
