"""Add my carved planks to every wood surface of the chest (works on chest_claude.blend in place).

Run: blender -b chest_claude.blend --python tools/build_wood.py -- maps
Safe to run again: panels are replaced by name, Codex's meshes stay as backups.
"""
import json
import os
import sys

import bpy
import bmesh
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from lid_profile import dense_curve  # noqa: E402

MAPS = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
U = np.array([0.8480481513760686, 0.529919175863294, 0.0])
N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
Z = np.array([0.0, 0.0, 1.0])
panels = json.load(open(os.path.join(MAPS, "wood_panels.json")))
lid = json.load(open(os.path.join(MAPS, "lid_arc.json")))
assert abs(panels["lid"]["H"] - lid["arc"]) < 1e-3, "regenerate the lid maps: arc length changed"


def make_mesh(name, verts, quads, uvs, uvname):
    old = bpy.data.meshes.get(name)
    if old:
        old.name = name + " old"
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
    me.loops.add(quads.size)
    me.loops.foreach_set("vertex_index", quads.astype(np.int32).ravel())
    me.polygons.add(len(quads))
    me.polygons.foreach_set("loop_start", np.arange(0, quads.size, 4, dtype=np.int32))
    try:
        me.polygons.foreach_set("loop_total", np.full(len(quads), 4, dtype=np.int32))
    except Exception:
        pass
    me.update(calc_edges=True)
    uv = me.uv_layers.new(name=uvname)
    uv.uv.foreach_set("vector", uvs.astype(np.float32).ravel())
    me.polygons.foreach_set("use_smooth", np.ones(len(quads), dtype=bool))
    me.validate()
    me.update()
    return me


def load(fname, cs):
    name = "Claude " + fname
    old = bpy.data.images.get(name)
    if old:
        bpy.data.images.remove(old)
    img = bpy.data.images.load(os.path.join(MAPS, fname), check_existing=False)
    img.name = name
    img.colorspace_settings.name = cs
    img.pack()
    return img


def plank_material(name, prefix, uvname):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (250, 0)
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = uvname; uv.location = (-700, 0)

    def tex(img, y, label):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.location = (-400, y); t.label = label
        t.interpolation = "Cubic"
        nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
        return t

    ta = tex(load(prefix + "_albedo.png", "sRGB"), 300, "Albedo")
    tr = tex(load(prefix + "_rough.png", "Non-Color"), 0, "Roughness")
    th = tex(load(prefix + "_height16.png", "Non-Color"), -300, "Height")
    nt.links.new(ta.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
    disp = nt.nodes.new("ShaderNodeDisplacement"); disp.location = (250, -400)
    disp.inputs["Midlevel"].default_value = 1.0
    disp.inputs["Scale"].default_value = 0.08
    nt.links.new(th.outputs["Color"], disp.inputs["Height"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    nt.links.new(disp.outputs["Displacement"], out.inputs["Displacement"])
    m.displacement_method = "BOTH"
    return m


def grid(L, H, step):
    nx, ny = int(round(L / step)), int(round(H / step))
    gx, gy = np.linspace(0, L, nx + 1), np.linspace(0, H, ny + 1)
    GX, GY = np.meshgrid(gx, gy)
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny))
    v00 = (jj * (nx + 1) + ii).ravel()
    quads = np.stack([v00, v00 + 1, v00 + nx + 2, v00 + nx + 1], axis=1)
    return GX.ravel(), GY.ravel(), quads


def finish(obname, mename, verts, quads, gx, gy, L, H, prefix, like):
    uvq = np.stack([np.stack([gx[quads[:, k]] / L, gy[quads[:, k]] / H], axis=1) for k in range(4)], axis=1)
    me = make_mesh(mename, verts, quads, uvq.reshape(-1, 2), "ClaudePlankUV")
    me.materials.append(plank_material("Claude carved planks " + prefix, prefix, "ClaudePlankUV"))
    ob = bpy.data.objects.get(obname)
    if ob is None:
        ob = bpy.data.objects.new(obname, me)
        for c in like.users_collection:
            c.objects.link(ob)
    ob.data = me
    if like.parent:
        ob.parent = like.parent
        ob.matrix_parent_inverse = like.matrix_parent_inverse.copy()
    old = bpy.data.meshes.get(mename + " old")
    if old:
        bpy.data.meshes.remove(old)
    return ob


def flat_panel(obname, prefix, origin, xdir, step, like, clip=None):
    L, H = panels[prefix]["L"], panels[prefix]["H"]
    gx, gy, quads = grid(L, H, step)
    verts = origin[None, :] + xdir[None, :] * gx[:, None] + Z[None, :] * gy[:, None]
    if clip is not None:
        ok = clip(gx, gy)
        quads = quads[ok[quads].all(axis=1)]
        used = np.unique(quads)
        remap = np.full(len(gx), -1, np.int64); remap[used] = np.arange(len(used))
        quads = remap[quads]; verts = verts[used]; gx = gx[used]; gy = gy[used]
    return finish(obname, "Claude " + prefix + " planks", verts, quads, gx, gy, L, H, prefix, like)


body = bpy.data.objects["Master Chest Body Envelope"]
lidob = bpy.data.objects["Lab Chest Barrel Lid Envelope"]
ZB = -2.2175

# front above the approved bottom planks
L = panels["front_upper"]["L"]
flat_panel("Claude Front Upper Planks", "front_upper", U * (-L / 2) + N * 1.6 + Z * (-0.84), U, 0.006, body)
# back, ends
L = panels["back"]["L"]
flat_panel("Claude Back Planks", "back", U * (L / 2) + N * (-1.6) + Z * ZB, -U, 0.012, body)
L = panels["end_a"]["L"]
flat_panel("Claude End Planks A", "end_a", U * 2.55 + N * (L / 2) + Z * ZB, -N, 0.010, body)
flat_panel("Claude End Planks B", "end_b", U * (-2.55) + N * (-L / 2) + Z * ZB, N, 0.010, body)

# lid arch
pts = np.array(lid["pts"])
c, arc, tan = dense_curve(pts)
L, H = panels["lid"]["L"], panels["lid"]["H"]
gx, gy, quads = grid(L, H, 0.008)
pd = np.interp(gy, arc, c[:, 0]); pz = np.interp(gy, arc, c[:, 1])
verts = U[None, :] * (gx - L / 2)[:, None] + N[None, :] * pd[:, None] + Z[None, :] * pz[:, None]
finish("Claude Lid Planks", "Claude lid planks", verts, quads, gx, gy, L, H, "lid", lidob)

# lid end caps, clipped to the arch
zb = float(pts[0, 1]); z_cap0 = 0.381
half = c[c[:, 0] >= 0]
order = np.argsort(half[:, 1])
prof_z, prof_d = half[order, 1], half[order, 0]


def clip(gx, gy):
    zz = z_cap0 + gy
    dd = np.abs(gx - 1.6)
    lim = np.where(zz <= zb, prof_d[0], np.interp(zz, prof_z, prof_d, right=0.0))
    return dd <= lim * 0.999


umax = lid["umax"]
flat_panel("Claude Lid Cap Planks A", "cap_a", U * umax + N * 1.6 + Z * z_cap0, -N, 0.010, lidob, clip)
flat_panel("Claude Lid Cap Planks B", "cap_b", U * (-umax) + N * (-1.6) + Z * z_cap0, N, 0.010, lidob, clip)

# ---- inside faces: my wood, box projected (no carving, bump only) -------------
im = bpy.data.materials.get("Claude carved planks inside") or bpy.data.materials.new("Claude carved planks inside")
im.use_nodes = True
nt = im.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
tc = nt.nodes.new("ShaderNodeTexCoord")
rot = nt.nodes.new("ShaderNodeMapping"); rot.inputs["Rotation"].default_value = (0, 0, -float(np.arctan2(U[1], U[0])))
scl = nt.nodes.new("ShaderNodeMapping"); scl.inputs["Scale"].default_value = (1 / 5.091, 1 / 5.091, 1 / 1.3608)
nt.links.new(tc.outputs["Object"], rot.inputs["Vector"]); nt.links.new(rot.outputs["Vector"], scl.inputs["Vector"])


def btex(img):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.projection = "BOX"; t.projection_blend = 0.1
    nt.links.new(scl.outputs["Vector"], t.inputs["Vector"])
    return t


ta = btex(bpy.data.images["Claude wood_albedo.png"]); tr = btex(bpy.data.images["Claude wood_rough.png"])
th = btex(bpy.data.images["Claude wood_height16.png"])
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.08
nt.links.new(th.outputs["Color"], bump.inputs["Height"])
nt.links.new(ta.outputs["Color"], bsdf.inputs["Base Color"]); nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"]); nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])


def strip(ob, backup_name, drop):
    """Remove the outer faces my panels replace; keep Codex's full mesh as a backup."""
    if backup_name not in bpy.data.meshes:
        bk = ob.data.copy(); bk.name = backup_name; bk.use_fake_user = True
    bm = bmesh.new(); bm.from_mesh(ob.data)
    dead = []
    for f in bm.faces:
        cc = np.array(f.calc_center_median()); nn = np.array(f.normal)
        if drop(cc @ U, cc @ N, cc[2], nn @ U, nn @ N, nn[2]):
            dead.append(f)
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    for i, s in enumerate(ob.material_slots):
        if s.material and s.material.name.startswith("Chest wood"):
            ob.data.materials[i] = im
    return len(dead)


n1 = strip(body, "Codex backup Master Chest Body Envelope",
           lambda u, d, z, nu, nd, nz: (abs(d) > 1.585 or abs(u) > 2.535) and -2.19 < z < 0.30 and abs(nz) < 0.9)
# lid: end caps (and their grooves) plus the outer arch
prof_all_z = np.concatenate([[0.0], prof_z]); prof_all_d = np.concatenate([[prof_d[0]], prof_d])


def lid_drop(u, d, z, nu, nd, nz):
    if abs(u) > 2.56:
        return True
    lim = float(np.interp(z, prof_all_z, prof_all_d, right=0.0))
    radial = nd * np.sign(d) * 0.6 + nz * 0.8 if z > 1.0 else nd * np.sign(d)
    return abs(d) > lim - 0.06 and radial > 0.2 and z > 0.40


n2 = strip(lidob, "Codex backup Lab Chest Barrel Lid Envelope", lid_drop)
bpy.ops.wm.save_mainfile(compress=True)
print("WOOD built; removed faces:", n1, n2, {o.name: len(o.data.vertices) for o in bpy.data.objects if o.name.startswith("Claude ")})
