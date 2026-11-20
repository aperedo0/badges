"""Diagnostic only, never saved: show another of the app's badges in place of the one in the scene, to check
that the temple works behind every badge (owner, 2026-11-19: "ok we can test with another badge").
BADGE_USDZ=/path/to/model.usdz  Chain before tools/v8_render.py."""
import bpy, os
from mathutils import Matrix, Vector
path = os.environ.get("BADGE_USDZ")
if path:
    model = bpy.data.objects["Reveal Badge Model"]
    old = [o for o in model.children_recursive if o.type == "MESH"]
    def bounds(objs):
        lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
        for o in objs:
            for c in o.bound_box:
                p = o.matrix_world @ Vector(c)
                lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
        return lo, hi
    bpy.context.view_layer.update()
    lo0, hi0 = bounds(old)
    before = set(bpy.data.objects)
    bpy.ops.wm.usd_import(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    tops = [o for o in new if o.parent is None or o.parent not in new]
    for o in tops:
        o.parent = model
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = Matrix.Identity(4)
    for o in old:
        o.hide_render = True
    bpy.context.view_layer.update()
    lo1, hi1 = bounds([o for o in new if o.type == "MESH"])
    print("OTHER BADGE", os.path.basename(path), "old size", [round(v, 2) for v in (hi0 - lo0)], "new size", [round(v, 2) for v in (hi1 - lo1)],
          "old centre", [round(v, 2) for v in (hi0 + lo0) / 2], "new centre", [round(v, 2) for v in (hi1 + lo1) / 2])
