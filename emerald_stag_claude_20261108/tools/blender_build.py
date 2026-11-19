# Blender: build the Emerald Stag from PARTS.npz + skeleton json, export one npz per material in model space.
# Usage: Blender -b --factory-startup --python blender_build.py -- PARTS.npz OUT.npz OUT.blend
import sys, json
import bpy, bmesh
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
PARTS, OUT, BLEND = argv[0], argv[1], argv[2]
skel = json.load(open(PARTS.replace('.npz', '_skeleton.json')))
parts = np.load(PARTS)

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
sc = bpy.context.scene


def to_bl(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]]


def from_bl(v):
    v = np.asarray(v, float)
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]]


class _Mats(dict):
    def __missing__(self, key):
        return mat(key, (0.5, 0.5, 0.5), 0.0, 0.5)
MATS = _Mats()
def mat(name, col, metal, rough):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    MATS[name] = m
    return m


mat('gold', (1.0, 0.60, 0.22), 1.0, 0.28)
mat('stag', (0.93, 0.80, 0.60), 1.0, 0.34)
mat('leaf', (0.03, 0.30, 0.10), 0.0, 0.25)
mat('petal', (0.85, 0.78, 0.60), 0.0, 0.5)
mat('stamen', (0.9, 0.6, 0.1), 0.0, 0.6)
mat('moss', (0.12, 0.16, 0.03), 0.0, 0.95)
mat('marble', (0.05, 0.12, 0.09), 0.0, 0.3)
mat('emerald', (0.02, 0.5, 0.2), 0.0, 0.05)
mat('antler', (1.0, 0.45, 0.10), 1.0, 0.26)
mat('leaf_light', (0.10, 0.42, 0.22), 0.0, 0.22)
mat('marble_top', (0.12, 0.2, 0.17), 0.0, 0.25)

# numpy parts as Blender meshes
for key in parts.files:
    if not key.endswith('_v'):
        continue
    name = key[:-2]
    V, N, T = parts[name + '_v'], parts[name + '_n'], parts[name + '_t']
    me = bpy.data.meshes.new('P_' + name)
    me.from_pydata(to_bl(V).tolist(), [], T.tolist()); me.update()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    loops = np.array([l.vertex_index for l in me.loops])
    me.normals_split_custom_set(to_bl(N[loops]).tolist())
    if name + '_uv' in parts.files:
        lay = me.uv_layers.new(name='st'); lay.data.foreach_set('uv', parts[name + '_uv'][loops].ravel().tolist())
    me.materials.append(MATS[name])
    ob = bpy.data.objects.new('P_' + name, me); sc.collection.objects.link(ob)


def skin_object(name, chains, material, subsurf=2):
    """chains: list of point lists [x, y, z, r] in model space; chains sharing an exact point join there."""
    verts, edges, radii, index = [], [], [], {}
    for chain in chains:
        prev = None
        for (x, y, z, r) in chain:
            key = (round(x, 5), round(y, 5), round(z, 5))
            if key not in index:
                index[key] = len(verts); verts.append((x, -z, y)); radii.append(r)
            i = index[key]
            if prev is not None and prev != i:
                edges.append((prev, i))
            prev = i
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); me.update()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    mod = ob.modifiers.new('skin', 'SKIN'); mod.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = (r, r)
    # one root per connected piece, or the skin modifier drops the unrooted pieces
    parent = list(range(len(verts)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in edges:
        parent[find(a)] = find(b)
    seen = set()
    for i in range(len(verts)):
        r = find(i)
        if r not in seen:
            seen.add(r); sv[i].use_root = True
    if subsurf:
        ss = ob.modifiers.new('sub', 'SUBSURF'); ss.levels = subsurf; ss.render_levels = subsurf
    me.materials.append(MATS[material])
    return ob


import os
CARVED = bool(os.environ.get('CARVED'))
st = skel['stag']
# connect legs, neck and tail to the spine by inserting their first point as a spine joint
stag_chains = [st['spine'], [st['spine'][-1]] + st['neck'][1:], st['head'], st['tail'],
               st['hind_near'], st['hind_far'], st['fore_raised'], st['fore_down']]
# bridge each limb root to the nearest spine point so the skin is one connected body
spine = np.array([p[:3] for p in st['spine']])
for k in ('tail', 'hind_near', 'hind_far', 'fore_raised', 'fore_down'):
    root = np.array(st[k][0][:3]); j = int(np.argmin(np.linalg.norm(spine - root, axis=1)))
    stag_chains.append([st['spine'][j], st[k][0]])
stag_chains.append([st['neck'][-1], st['head'][0]])
if not CARVED:
    skin_object('S_stag', stag_chains, 'stag', 2)
for i, ear in enumerate([] if CARVED else skel['ears']):
    ob = skin_object(f'S_ear{i}', [ear], 'stag', 2)
    ob.scale = (1, 0.35, 1)  # flatten the ear sideways (Blender y = model -z)
    ob.location = (0, -ear[0][2] * 0.65, 0)
ant = skel['antlers']
# tines attach to the nearest beam point
beams = [ant[0], ant[1]]
chains = list(beams)
for t in ant[2:]:
    root = np.array(t[0][:3])
    best = min(((np.linalg.norm(np.array(p[:3]) - root), p) for b in beams for p in b), key=lambda q: q[0])[1]
    chains.append([best] + t)
if not CARVED:
    skin_object('S_antlers', chains, 'antler', 2)
br = skel['branches']
chains = [br[0]]
for t in br[1:]:
    root = np.array(t[0][:3])
    cands = [p for c in chains for p in c]
    best = min(cands, key=lambda p: np.linalg.norm(np.array(p[:3]) - root))
    chains.append([best] + t if np.linalg.norm(np.array(best[:3]) - root) < 0.25 else t)
skin_object('S_branches', chains, 'gold', 1)

bpy.context.view_layer.update()
# export evaluated meshes grouped by material, deduplicated per (position, normal, uv)
groups = {}
dg = bpy.context.evaluated_depsgraph_get()
for ob in sc.objects:
    if ob.type != 'MESH':
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    M = np.array(ob.matrix_world)
    co = np.array([v.co for v in me.vertices]).reshape(-1, 3)
    co = co @ M[:3, :3].T + M[:3, 3]
    tris = np.array([lt.loops[:] for lt in me.loop_triangles]).reshape(-1, 3)
    loop_v = np.array([l.vertex_index for l in me.loops])
    try:
        ln = np.array([cn.vector for cn in me.corner_normals]).reshape(-1, 3)
    except AttributeError:
        ln = np.array([l.normal for l in me.loops]).reshape(-1, 3)
    Ninv = np.linalg.inv(M[:3, :3]).T
    ln = ln @ Ninv.T; ln /= np.maximum(np.linalg.norm(ln, axis=1, keepdims=True), 1e-12)
    uv = None
    if me.uv_layers:
        uv = np.array([d.uv for d in me.uv_layers[0].data]).reshape(-1, 2)
    matname = me.materials[0].name if me.materials else 'gold'
    P = from_bl(co[loop_v]); Nn = from_bl(ln)
    key = np.c_[np.round(P, 5), np.round(Nn, 3)] if uv is None else np.c_[np.round(P, 5), np.round(Nn, 3), np.round(uv, 5)]
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    Vu = np.zeros((len(uniq), 3)); Nu = np.zeros((len(uniq), 3)); Vu[inv] = P; Nu[inv] = Nn
    g = groups.setdefault(matname, {'v': [], 'n': [], 't': [], 'uv': [], 'has_uv': uv is not None})
    off = sum(len(x) for x in g['v'])
    g['v'].append(Vu); g['n'].append(Nu); g['t'].append(inv[tris] + off)
    if uv is not None:
        UVu = np.zeros((len(uniq), 2)); UVu[inv] = uv; g['uv'].append(UVu)
    ev.to_mesh_clear()
data = {}
for name, g in groups.items():
    data[name + '_v'] = np.vstack(g['v']); data[name + '_n'] = np.vstack(g['n']); data[name + '_t'] = np.vstack(g['t'])
    if g['has_uv'] and len(g['uv']) == len(g['v']):
        data[name + '_uv'] = np.vstack(g['uv'])
allv = np.vstack([data[k] for k in data if k.endswith('_v')])
lift = -2.455 - allv[:, 1].min()
for k in data:
    if k.endswith('_v'):
        data[k] = data[k] + np.array([0, lift, 0])
np.savez(OUT, **data)
allv = np.vstack([data[k] for k in data if k.endswith('_v')])
print('EXPORT', {k[:-2]: len(data[k]) for k in data if k.endswith('_t')}, 'total', sum(len(data[k]) for k in data if k.endswith('_t')),
      'bounds', allv.min(0).round(3).tolist(), allv.max(0).round(3).tolist(), 'lift', round(lift, 4))
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
