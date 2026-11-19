"""Build a clean enamel badge inside the owner's open Blender (run through the MCP bridge).

Reads the job file named in JOB (a JSON with prep, out_npz, blend, scene, prefix, textures) and:
  * triangulates the prep's points with their ring edges as constraints, so triangles follow every line;
  * samples height and normals from the smooth fields at each vertex;
  * builds separate parts: gold, enamel, side wall, gem (flat star facets), front and back;
  * shows them in a scene named after the badge, next to the mockup, and saves the badge's own .blend;
  * writes the part arrays to out_npz for the USDZ writer.
Existing objects of this scene are updated in place (never deleted: deleting objects closed Blender twice).
"""
import json
import numpy as np
import bpy
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

JOB = json.load(open('/Users/antonioperedo/Desktop/badges/enamel_badges_tools/blender_job.json'))
P = dict(np.load(JOB['prep']))
S, cx_px, top_px = float(P['S']), float(P['cx_px']), float(P['top_px'])
H, W, E0 = int(P['H']), int(P['W']), float(P['E0'])


def bilinear(grid, x, y):
    x = np.clip(x, 0, grid.shape[1] - 1.001); y = np.clip(y, 0, grid.shape[0] - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    return (grid[y0, x0] * (1 - fx) * (1 - fy) + grid[y0, x0 + 1] * fx * (1 - fy)
            + grid[y0 + 1, x0] * (1 - fx) * fy + grid[y0 + 1, x0 + 1] * fx * fy)


def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


# ---------- triangulate along the rings ----------
pts = P['pts']; edges = P['edges']
res = delaunay_2d_cdt([Vector((float(x), float(y))) for x, y in pts], [tuple(map(int, e)) for e in edges], [], 0, 1e-5, True)
V2 = np.array([[v.x, v.y] for v in res[0]])
F = np.array([f for f in res[2] if len(f) == 3])
orig = res[3]                                             # input ids behind each output vertex
out_of = np.full(len(pts), -1)
for k, ids in enumerate(orig):
    for i in ids:
        out_of[i] = k
c = V2[F].mean(1)
inside = bilinear(P['o'], c[:, 0], c[:, 1]) > 0
F = F[inside]
used = np.unique(F); remap = -np.ones(len(V2), int); remap[used] = np.arange(len(used))
V2 = V2[used]; F = remap[F]
outline_ids = remap[out_of[:int(P['n_outline'])]]
outline_ids = outline_ids[outline_ids >= 0]

# heights and normals from the smooth fields
zpx = bilinear(P['z'], V2[:, 0], V2[:, 1])
gx = bilinear(P['gx'], V2[:, 0], V2[:, 1]); gy = bilinear(P['gy'], V2[:, 0], V2[:, 1])
X = (V2[:, 0] - cx_px) * S; Y = 2.995 - (V2[:, 1] - top_px) * S; Z = zpx * S
Vf = np.c_[X, Y, Z]; Nf = unit(np.c_[-gx, gy, np.ones(len(V2))])
UV = np.c_[V2[:, 0] / W, 1 - V2[:, 1] / H]
# winding: counterclockwise seen from +Z
e1 = Vf[F[:, 1]] - Vf[F[:, 0]]; e2 = Vf[F[:, 2]] - Vf[F[:, 0]]
flip = np.cross(e1, e2)[:, 2] < 0; F[flip] = F[flip][:, ::-1]
c = V2[F].mean(1)
is_gold = bilinear(P['s'], c[:, 0], c[:, 1]) > 0
parts = {}


def front_back(F_sel):
    """Front faces and their mirrored back (z flipped, winding reversed), compacted."""
    used = np.unique(F_sel); m = -np.ones(len(Vf), int); m[used] = np.arange(len(used)); n = len(used)
    v = Vf[used]; nn = Nf[used]; uv = UV[used]; f = m[F_sel]
    return (np.vstack([v, v * [1, 1, -1]]), np.vstack([nn, nn * [1, 1, -1]]), np.vstack([uv, uv]),
            np.vstack([f, f[:, ::-1] + n]))


parts['gold'] = front_back(F[is_gold])
parts['enamel'] = front_back(F[~is_gold])

# side wall: front outline to back outline, facing out
ring = Vf[outline_ids]; n = len(ring)
tang = np.roll(ring, -1, 0) - np.roll(ring, 1, 0)
side_n = unit(np.c_[tang[:, 1], -tang[:, 0], np.zeros(n)])
centroid = ring[:, :2].mean(0)
if np.mean(np.sum((ring[:, :2] - centroid) * side_n[:, :2], 1)) < 0:
    side_n = -side_n
sv = np.vstack([ring, ring * [1, 1, -1]]); sn = np.vstack([side_n, side_n]); suv = np.vstack([UV[outline_ids]] * 2)
sf = []
for i in range(n):
    j = (i + 1) % n
    sf += [(i, j, n + j), (i, n + j, n + i)]
sf = np.array(sf)
e1 = sv[sf[:, 1]] - sv[sf[:, 0]]; e2 = sv[sf[:, 2]] - sv[sf[:, 0]]
fn = np.cross(e1, e2); wrong = np.sum(fn * sn[sf[:, 0]], 1) < 0; sf[wrong] = sf[wrong][:, ::-1]
parts['side'] = (sv, sn, suv, sf)

# gem: flat star facets from an apex over the ridge crossing
if 'star_outline' in P:
    tips, corners, ol = P['star_tips'], P['star_corners'], P['star_outline'][:-1]
    apex2 = np.array([P['star_center'][0], (tips[0][1] + tips[2][1]) / 2])
    za, zr = (E0 + 22.0) * S, (E0 + 3.0) * S
    key = [(tuple(t), 'tip') for t in tips] + [(tuple(k), 'corner') for k in corners]
    ang_of = lambda p: np.arctan2(-(p[1] - apex2[1]), p[0] - apex2[0]) % (2 * np.pi)
    marks = sorted([(ang_of(np.array(p)), np.array(p)) for p, _ in key], key=lambda t: t[0])
    oa = np.array([ang_of(p) for p in ol])
    pts_g, zs = [], []
    for k in range(8):
        a0, p0 = marks[k]; a1, p1 = marks[(k + 1) % 8]
        span = (a1 - a0) % (2 * np.pi)
        sel = ((oa - a0) % (2 * np.pi)) < span
        seg = ol[sel]; seg = seg[np.argsort((oa[sel] - a0) % (2 * np.pi))]
        P0 = np.r_[(p0[0] - cx_px) * S, 2.995 - (p0[1] - top_px) * S, zr]
        P1 = np.r_[(p1[0] - cx_px) * S, 2.995 - (p1[1] - top_px) * S, zr]
        A = np.r_[(apex2[0] - cx_px) * S, 2.995 - (apex2[1] - top_px) * S, za]
        nrm = np.cross(P0 - A, P1 - A)
        chain = [p0] + list(seg)
        for q in chain:
            Q = np.r_[(q[0] - cx_px) * S, 2.995 - (q[1] - top_px) * S]
            zq = A[2] - (nrm[0] * (Q[0] - A[0]) + nrm[1] * (Q[1] - A[1])) / nrm[2]
            pts_g.append(np.r_[Q, max(zq, zr * 0.98)])
    ring_g = np.array(pts_g); m = len(ring_g)
    A = np.r_[(apex2[0] - cx_px) * S, 2.995 - (apex2[1] - top_px) * S, za]
    gv = np.vstack([A, ring_g]); gf = np.array([(0, 1 + i, 1 + (i + 1) % m) for i in range(m)])
    e1 = gv[gf[:, 1]] - gv[gf[:, 0]]; e2 = gv[gf[:, 2]] - gv[gf[:, 0]]
    flip = np.cross(e1, e2)[:, 2] < 0; gf[flip] = gf[flip][:, ::-1]
    # flat facets: split vertices per triangle so each facet keeps its own normal
    fv = gv[gf].reshape(-1, 3); fnrm = unit(np.cross(gv[gf[:, 1]] - gv[gf[:, 0]], gv[gf[:, 2]] - gv[gf[:, 0]]))
    fnv = np.repeat(fnrm, 3, 0); ff = np.arange(len(fv)).reshape(-1, 3)
    k = len(fv)
    parts['gem'] = (np.vstack([fv, fv * [1, 1, -1]]), np.vstack([fnv, fnv * [1, 1, -1]]),
                    np.zeros((2 * k, 2)), np.vstack([ff, ff[:, ::-1] + k]))

np.savez_compressed(JOB['out_npz'], **{f'{k}_{a}': v for k, p in parts.items() for a, v in zip(('v', 'n', 'uv', 't'), p)})

# ---------- show it in the open Blender ----------
scene = bpy.data.scenes.get(JOB['scene']) or bpy.data.scenes.new(JOB['scene'])
bpy.context.window.scene = scene


def material(name, setup):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; bs = nt.nodes.get('Principled BSDF')
    setup(m, nt, bs); return m


def img_node(nt, path, colorspace):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True)
    t.image.reload(); t.image.colorspace_settings.name = colorspace; return t


def gold_setup(rough):
    def f(m, nt, bs):
        bs.inputs['Base Color'].default_value = (0.70, 0.31, 0.0, 1); bs.inputs['Metallic'].default_value = 1.0
        bs.inputs['Roughness'].default_value = rough
    return f


def enamel_setup(m, nt, bs):
    if any(n.type == 'TEX_IMAGE' for n in nt.nodes):
        import os
        for n in nt.nodes:
            if n.type == 'TEX_IMAGE':                          # point at this version's textures
                n.image.filepath = os.path.join(JOB['textures'], os.path.basename(n.image.filepath)); n.image.reload()
        return
    tx = JOB['textures']
    col = img_node(nt, tx + '/enamel_color.png', 'sRGB'); nt.links.new(col.outputs['Color'], bs.inputs['Base Color'])
    rou = img_node(nt, tx + '/enamel_rough.png', 'Non-Color'); nt.links.new(rou.outputs['Color'], bs.inputs['Roughness'])
    glo = img_node(nt, tx + '/enamel_glow.png', 'Non-Color'); nt.links.new(glo.outputs['Color'], bs.inputs['Emission Color'])
    bs.inputs['Emission Strength'].default_value = 1.0; bs.inputs['Metallic'].default_value = 0.0


def gem_setup(m, nt, bs):
    bs.inputs['Base Color'].default_value = (0.05, 0.4, 0.85, 1); bs.inputs['Roughness'].default_value = 0.05


pre = JOB['prefix']
mats = {'gold': material(pre + '_Gold', gold_setup(0.26)), 'enamel': material(pre + '_Enamel', enamel_setup),
        'side': material(pre + '_Side', gold_setup(0.5)), 'gem': material('CrestGem_FoilSapphire', gem_setup)}
labels = {'gold': 'Gold walls and rim', 'enamel': 'Enamel', 'side': 'Side wall', 'gem': 'Star gem'}
for key, (v, nrm, uv, f) in parts.items():
    name = f"{JOB['scene']} {labels[key]}"
    ob = bpy.data.objects.get(name)
    me = ob.data if ob else bpy.data.meshes.new(name)
    me.clear_geometry()
    me.from_pydata(v.tolist(), [], f.tolist()); me.update()
    if not me.uv_layers:
        me.uv_layers.new(name='st')
    lu = np.array([l.vertex_index for l in me.loops]); me.uv_layers[0].data.foreach_set('uv', uv[lu].ravel())
    me.normals_split_custom_set_from_vertices([tuple(x) for x in nrm])
    if not me.materials:
        me.materials.append(mats[key])
    if ob is None:
        ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    elif ob.name not in scene.objects:
        scene.collection.objects.link(ob)
# the mockup beside the badge, for comparing in Blender
ref_name = f"{JOB['scene']} mockup"
if ref_name not in bpy.data.objects:
    e = bpy.data.objects.new(ref_name, None); e.empty_display_type = 'IMAGE'
    e.data = bpy.data.images.load(str(P['mockup']), check_existing=True)
    e.empty_display_size = 5.45 * W / (float(P['H']) * 1.0) * (H * S / 5.45)
    e.location = (-6.8, 0.27, 0); scene.collection.objects.link(e)
# stand everything upright in Blender (its Z is up; the app's file is Y up): display only, the data stays Y up
import math
for ob in scene.objects:
    if ob.name.startswith(JOB['scene']):
        ob.rotation_euler = (math.pi / 2, 0, 0)
ref = bpy.data.objects.get(ref_name)
if ref:
    ref.location = (-6.8, 0, 0.27)
bpy.ops.wm.save_as_mainfile(filepath=JOB['blend'])
print('built', {k: len(p[3]) for k, p in parts.items()}, 'saved', JOB['blend'])
