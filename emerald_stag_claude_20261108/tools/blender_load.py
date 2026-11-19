# Runs inside the open Blender: builds the 'Ruby Crown Claude' scene from GEOM_NPZ.
import bpy, numpy as np
GEOM_NPZ = '__GEOM__'
SCENE = '__SCENE__'
d = np.load(GEOM_NPZ)
sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
try:
    bpy.context.window.scene = sc
except Exception:
    pass
COLORS = {'gold': ((1.0, 0.42, 0.06), 1.0, 0.27), 'antler': ((1.0, 0.40, 0.05), 1.0, 0.25), 'stag': ((0.86, 0.60, 0.33), 1.0, 0.42), 'leaf': ((0.002, 0.045, 0.018), 0.0, 0.26), 'leaf_light': ((0.02, 0.17, 0.07), 0.0, 0.26), 'petal': ((0.62, 0.52, 0.36), 0.0, 0.45), 'stamen': ((0.85, 0.55, 0.08), 0.0, 0.6), 'moss': ((0.055, 0.075, 0.008), 0.0, 0.95), 'marble': ((0.03, 0.09, 0.07), 0.0, 0.62), 'marble_top': ((0.08, 0.16, 0.13), 0.0, 0.28), 'emerald': ((0.02, 0.5, 0.2), 0.0, 0.05)}
def to_bl(v): return np.c_[v[:, 0], -v[:, 2], v[:, 1]]
# each version gets its own new scene; nothing is deleted (deleting objects crashed the open Blender twice)
for mat, (col, met, rough) in COLORS.items():
    if mat + '_v' not in d.files: continue
    m = bpy.data.materials.get('ES_' + mat) or bpy.data.materials.new('ES_' + mat)
    m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = met; b.inputs['Roughness'].default_value = rough
    V, N, T = d[mat + '_v'], d[mat + '_n'], d[mat + '_t']
    me = bpy.data.meshes.new('ES_' + mat); me.from_pydata(to_bl(V).tolist(), [], T.tolist()); me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    loops = np.array([l.vertex_index for l in me.loops]); me.normals_split_custom_set(to_bl(N[loops]).tolist())
    me.materials.append(m)
    ob = bpy.data.objects.new('ES_' + mat, me); sc.collection.objects.link(ob)
print('crown built', [k for k in d.files if k.endswith('_t')])
