# Runs inside the open Blender: put GEOM_NPZ into the same 'Emerald Stag' scene objects (no deleting), then save.
import bpy, numpy as np
GEOM_NPZ = '__GEOM__'
LIVE = '/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/live/emerald_stag_live.blend'
d = np.load(GEOM_NPZ)
sc = bpy.data.scenes.get('Emerald Stag') or bpy.data.scenes.new('Emerald Stag')
for win in bpy.context.window_manager.windows:
    win.scene = sc
def to_bl(v): return np.c_[v[:, 0], -v[:, 2], v[:, 1]]
updated, created = [], []
for key in d.files:
    if not key.endswith('_v'):
        continue
    mat = key[:-2]
    V, N, T = d[mat + '_v'], d[mat + '_n'], d[mat + '_t']
    ob = sc.objects.get('ES_' + mat)
    if ob is None:
        me = bpy.data.meshes.new('ES_' + mat)
        m = bpy.data.materials.get('ES_' + mat) or bpy.data.materials.new('ES_' + mat)
        me.materials.append(m)
        ob = bpy.data.objects.new('ES_' + mat, me); sc.collection.objects.link(ob); created.append(mat)
    else:
        me = ob.data; updated.append(mat)
    mats = list(me.materials)
    me.clear_geometry()
    me.from_pydata(to_bl(V).tolist(), [], T.tolist()); me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    loops = np.array([l.vertex_index for l in me.loops]); me.normals_split_custom_set(to_bl(N[loops]).tolist())
    if not me.materials and mats:
        for m in mats: me.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=LIVE)
print('updated', updated, 'created', created, 'saved', LIVE)
