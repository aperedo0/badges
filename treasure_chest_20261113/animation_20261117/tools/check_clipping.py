"""Clipping checks for the Chest Reveal (run inside Blender). BVH overlaps between moving parts
and the chest body, measured in the chest's own frame (the Shake control), so the body is built
once. Pairs that already touch at rest (frame 45) are listed separately and ignored.
Result: CLIP[name] = ({frame: [(mover, other), ...]}, [rest pairs])."""
import bpy
from mathutils.bvhtree import BVHTree

scn = bpy.data.scenes["Chest Reveal"]
shake = bpy.data.objects["Reveal Chest Shake"]


def tree(name):
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[name].evaluated_get(dg)
    me = o.to_mesh()
    m = shake.matrix_world.inverted() @ o.matrix_world
    t = BVHTree.FromPolygons([m @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    o.to_mesh_clear()
    return t


def coll(*names):
    return [o.name for n in names for o in bpy.data.collections[n].all_objects if o.type == "MESH"]


scn.frame_set(45)
body = coll("Reveal Chest Body")
BODY = {b: tree(b) for b in body}


def check(movers, frames, extra=None):
    scn.frame_set(45)
    others = dict(BODY)
    rest = set()
    for m in movers:
        t = tree(m)
        for b, tb in others.items():
            if t.overlap(tb):
                rest.add((m, b))
    hits = {}
    for f in frames:
        scn.frame_set(f)
        oth = dict(others)
        if extra:
            oth.update({e: tree(e) for e in extra})
        for m in movers:
            t = tree(m)
            for b, tb in oth.items():
                if b != m and (m, b) not in rest and t.overlap(tb):
                    hits.setdefault(f, []).append((m[2:], b[2:]))
    return hits, sorted((a[2:], b[2:]) for a, b in rest)


CLIP = {}
CLIP["rings"] = check(["R Lab Chest Solid Ring Handle -1", "R Lab Chest Solid Ring Handle 1"], range(1, 96))
CLIP["hasp"] = check(["R Lab Chest Curved Hasp Tongue", "R Lab Chest Front Hasp Barrel"],
                     list(range(8, 32)) + list(range(50, 150)),
                     extra=["R Lab Chest " + n for n in ("Key Driven Slider", "Hasp Mount", "Hasp Mount Fastener -1",
                            "Hasp Mount Fastener 1", "Hasp Pivot Dome -1", "Hasp Pivot Dome 1", "Front Hinge Pin",
                            "Fixed Front Hinge Knuckle -1", "Fixed Front Hinge Knuckle 1", "Upper Lid Rim")])
lid = coll("Reveal Chest Lid")
CLIP["lid"] = check(lid, [11, 12, 16, 17, 27, 67, 77, 89, 104, 110, 116, 120, 124, 128, 131, 134, 136, 138, 145])
CLIP["badge"] = check(coll("Reveal Badge"), range(124, 229, 2))
print({k: (len(v[0]), sorted(v[0])[:12], v[1][:8]) for k, v in CLIP.items()})
