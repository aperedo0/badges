# Runs inside the open Blender. Builds the Ruby Heart (Claude) scene from GEOM_NPZ.
import bpy, numpy as np, mathutils
GEOM_NPZ = '/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/trace/geom_dome4.npz'
SCENE = 'Ruby Heart Claude'
d = np.load(GEOM_NPZ)
sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
bpy.context.window.scene = sc

def to_bl(v):
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]]

def material(name, color, metallic, rough, transmission=0.0, ior=1.45):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    b.inputs['IOR'].default_value = ior
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = transmission
    return m

def build(name, V, N, T, mat, uv=None):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new(name)
    me.from_pydata(to_bl(V).tolist(), [], T.tolist())
    me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    loops = np.array([l.vertex_index for l in me.loops])
    me.normals_split_custom_set(to_bl(N[loops]).tolist())
    if uv is not None:
        lay = me.uv_layers.new(name='st')
        lay.data.foreach_set('uv', uv[loops].ravel().tolist())
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    return ob

gold = material('RH_Gold', (0.95, 0.62, 0.22), 1.0, 0.28)
ruby = material('RH_Ruby', (0.85, 0.02, 0.12), 0.0, 0.03, transmission=0.0, ior=1.77)
build('RH_Frame', d['frame_v'], d['frame_n'], d['frame_t'], gold, d['frame_uv'])
build('RH_Gem', d['gem_v'], d['gem_n'], d['gem_t'], ruby)
print('built', len(d['frame_t']), len(d['gem_t']))
