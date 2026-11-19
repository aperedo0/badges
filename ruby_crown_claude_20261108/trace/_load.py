# Runs inside the open Blender: builds the 'Ruby Crown Claude' scene from GEOM_NPZ.
import bpy, numpy as np
GEOM_NPZ = '/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/candidate11/geometry.npz'
SCENE = 'Ruby Crown Claude'
d = np.load(GEOM_NPZ)
sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
try:
    bpy.context.window.scene = sc
except Exception:
    pass
COLORS = {'gold': ((1.0, 0.55, 0.12), 1.0, 0.28), 'gold_recess': ((0.45, 0.25, 0.06), 1.0, 0.45),
          'velvet': ((0.25, 0.005, 0.02), 0.0, 0.85), 'gold_leaf': ((1.0, 0.62, 0.2), 1.0, 0.36), 'frieze': ((0.05, 0.04, 0.03), 0.0, 0.8), 'ruby': ((0.7, 0.01, 0.06), 0.0, 0.05), 'clear': ((0.9, 0.9, 0.95), 0.0, 0.02)}
def to_bl(v): return np.c_[v[:, 0], -v[:, 2], v[:, 1]]
for ob in [o for o in sc.objects if o.name.startswith('RC_')]:
    bpy.data.objects.remove(ob, do_unlink=True)
for mat, (col, met, rough) in COLORS.items():
    if mat + '_v' not in d.files: continue
    m = bpy.data.materials.get('RC_' + mat) or bpy.data.materials.new('RC_' + mat)
    m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = met; b.inputs['Roughness'].default_value = rough
    V, N, T = d[mat + '_v'], d[mat + '_n'], d[mat + '_t']
    me = bpy.data.meshes.new('RC_' + mat); me.from_pydata(to_bl(V).tolist(), [], T.tolist()); me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    loops = np.array([l.vertex_index for l in me.loops]); me.normals_split_custom_set(to_bl(N[loops]).tolist())
    me.materials.append(m)
    ob = bpy.data.objects.new('RC_' + mat, me); sc.collection.objects.link(ob)
print('crown built', [k for k in d.files if k.endswith('_t')])
