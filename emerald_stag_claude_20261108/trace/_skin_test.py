import bpy, numpy as np
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
def make(name, verts, rad):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [(i, i + 1) for i in range(len(verts) - 1)], []); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.new('skin', 'SKIN'); ss = ob.modifiers.new('sub', 'SUBSURF'); ss.levels = 2
    for i, v in enumerate(me.skin_vertices[0].data): v.radius = rad; v.use_root = (i == 0)
    return ob
tests = {'vertical': [(0, 0, 0), (0, 0, 1), (0, 0, 2)], 'tilted': [(0, 0, 0), (0.5, 0, 1), (1.0, 0, 2)], 'horizontal': [(0, 0, 0), (1, 0, 0), (2, 0, 0)]}
dg = bpy.context.evaluated_depsgraph_get()
for name, verts in tests.items():
    ob = make(name, verts, (0.1, 0.3)); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh(); co = np.array([v.co for v in me.vertices])
    mid = co[np.abs(co[:, 2] - 1.0) < 0.05] if name != 'horizontal' else co[np.abs(co[:, 0] - 1.0) < 0.05]
    print('SKIN', name, 'extent x', round(float(np.ptp(mid[:, 0])), 3), 'y', round(float(np.ptp(mid[:, 1])), 3), 'z', round(float(np.ptp(mid[:, 2])), 3))
