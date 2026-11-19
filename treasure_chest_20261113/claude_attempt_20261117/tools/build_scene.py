"""Build my version of the bottom planks and the lower iron rim into a copy of the chest.

Run: blender -b source_copy.blend --python tools/build_scene.py -- maps chest_claude.blend
Codex's file is never touched. Original meshes stay in the file as backups (fake user).
"""
import os
import sys

import bpy
import bmesh
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
MAPS = os.path.abspath(args[0])
OUTBLEND = os.path.abspath(args[1])

U = np.array([0.8480481513760686, 0.529919175863294, 0.0])
N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
Z = np.array([0.0, 0.0, 1.0])


def make_mesh(name, verts, quads, uvs, uvname):
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


def load(name, cs):
    img = bpy.data.images.load(os.path.join(MAPS, name), check_existing=False)
    img.name = "Claude " + name
    img.colorspace_settings.name = cs
    return img


def pbr_material(name, uvname, albedo, rough, height, mid, scale, metal=None, metallic=0.0):
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

    ta = tex(load(albedo, "sRGB"), 300, "Albedo")
    tr = tex(load(rough, "Non-Color"), 0, "Roughness")
    th = tex(load(height, "Non-Color"), -600, "Height")
    nt.links.new(ta.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
    if metal:
        tm = tex(load(metal, "Non-Color"), -300, "Metallic")
        nt.links.new(tm.outputs["Color"], bsdf.inputs["Metallic"])
    else:
        bsdf.inputs["Metallic"].default_value = metallic
    disp = nt.nodes.new("ShaderNodeDisplacement"); disp.location = (250, -600)
    disp.inputs["Midlevel"].default_value = mid
    disp.inputs["Scale"].default_value = scale
    nt.links.new(th.outputs["Color"], disp.inputs["Height"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    nt.links.new(disp.outputs["Displacement"], out.inputs["Displacement"])
    m.displacement_method = "BOTH"
    return m


# ---------------------------------------------------------------- wood planks
L, HH = 5.0910, 1.3608
NX, NY = 848, 227
gx = np.linspace(0, L, NX + 1)
gy = np.linspace(0, HH, NY + 1)
GX, GY = np.meshgrid(gx, gy)                       # rows = y
verts = (U[None, :] * (GX.ravel() - L / 2)[:, None] + N[None, :] * 1.6
         + Z[None, :] * (-2.2008 + GY.ravel())[:, None])
ii, jj = np.meshgrid(np.arange(NX), np.arange(NY))
v00 = (jj * (NX + 1) + ii).ravel()
quads = np.stack([v00, v00 + 1, v00 + NX + 2, v00 + NX + 1], axis=1)
uvq = np.stack([np.stack([GX.ravel()[quads[:, k]] / L, GY.ravel()[quads[:, k]] / HH], axis=1) for k in range(4)], axis=1)
wood_me = make_mesh("Claude bottom planks", verts, quads, uvq.reshape(-1, 2), "ClaudePlankUV")
wood_mat = pbr_material("Claude carved chestnut planks", "ClaudePlankUV", "wood_albedo.png", "wood_rough.png",
                        "wood_height16.png", 1.0, 0.08)
wood_me.materials.append(wood_mat)
env = bpy.data.objects["Master Chest Body Envelope"]
wood_ob = bpy.data.objects.get("Claude Bottom Planks") or bpy.data.objects.new("Claude Bottom Planks", wood_me)
wood_ob.data = wood_me
for c in env.users_collection:
    if wood_ob.name not in c.objects:
        c.objects.link(wood_ob)

# keep Codex's plank as a backup datablock, then remove its faces from my working envelope
if "Codex backup Master Chest Body Envelope" not in bpy.data.meshes:
    bk = env.data.copy(); bk.name = "Codex backup Master Chest Body Envelope"; bk.use_fake_user = True
    bm = bmesh.new(); bm.from_mesh(env.data)
    idx = [i for i, s in enumerate(env.material_slots) if s.material and s.material.name == "Wood Lab BC_final_polish"][0]
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == idx], context="FACES")
    bm.to_mesh(env.data); bm.free(); env.data.update()

# ---------------------------------------------------------------- iron rim
prof = np.load(os.path.join(MAPS, "iron_profile.npz"))
PERIM = float(prof["perim"]); A, BD, RC = float(prof["A"]), float(prof["BD"]), float(prof["RC"])
n_top, n_tch, n_front, n_bch, n_bot = [int(v) for v in prof["rows"]]
R = n_top + n_tch + n_front + n_bch + n_bot
NS = 2560
ZT, ZB, INNER = -1.7140, -2.2175, -0.186
s = np.arange(NS) / NS * PERIM
Wt = len(prof["at"])
sx = (np.arange(Wt) + 0.5) / Wt * PERIM


def leg(name):
    return np.interp(s, sx, prof[name], period=PERIM)


at, bt, ab, bb = leg("at"), leg("bt"), leg("ab"), leg("bb")

# outer path: position, outward normal, and corner centre data for every s
segs = [("L", (0.0, -BD), (1, 0), (0, -1), A - RC),
        ("A", (A - RC, -BD + RC), -90.0, (1, -1), np.pi * RC / 2),
        ("L", (A, -BD + RC), (0, 1), (1, 0), 2 * (BD - RC)),
        ("A", (A - RC, BD - RC), 0.0, (1, 1), np.pi * RC / 2),
        ("L", (A - RC, BD), (-1, 0), (0, 1), 2 * (A - RC)),
        ("A", (-(A - RC), BD - RC), 90.0, (-1, 1), np.pi * RC / 2),
        ("L", (-A, BD - RC), (0, -1), (-1, 0), 2 * (BD - RC)),
        ("A", (-(A - RC), -BD + RC), 180.0, (-1, -1), np.pi * RC / 2),
        ("L", (-(A - RC), -BD), (1, 0), (0, -1), A - RC)]
P0 = np.zeros((NS, 2)); NRM = np.zeros((NS, 2)); ARC = np.zeros(NS, bool); CEN = np.zeros((NS, 2)); SGN = np.zeros((NS, 2))
acc = 0.0
for kind, p, d, n, ln in segs:
    m = (s >= acc - 1e-9) & (s < acc + ln - 1e-9)
    t = s[m] - acc
    if kind == "L":
        P0[m] = np.array(p)[None, :] + t[:, None] * np.array(d, float)[None, :]
        NRM[m] = np.array(n, float)
    else:
        th = np.deg2rad(d) + t / RC
        nn = np.stack([np.cos(th), np.sin(th)], axis=1)
        P0[m] = np.array(p)[None, :] + RC * nn
        NRM[m] = nn; ARC[m] = True; CEN[m] = np.array(p); SGN[m] = np.array(n, float)
    acc += ln


def offs(o):
    """Path point at offset o (per column array) from the outer surface."""
    pt = P0 + o[:, None] * NRM
    rad = RC + o
    sharp = ARC & (rad < 0)
    pt[sharp] = CEN[sharp] + rad[sharp, None] * SGN[sharp]
    return pt


# mesh rows are coarser than the texture rows; rows_v keeps every mesh row on its texture row
m_top, m_tch, m_front, m_bch, m_bot = 20, 8, 56, 8, 6
rows_o, rows_z, rows_v = [], [], []
for j in range(m_top):
    g = j / m_top; rows_o.append(INNER + g * (-at - INNER)); rows_z.append(np.full(NS, ZT)); rows_v.append(g * n_top)
for j in range(m_tch):
    g = j / m_tch; rows_o.append(-at * (1 - g)); rows_z.append(ZT - bt * g); rows_v.append(n_top + g * n_tch)
for j in range(m_front):
    g = j / m_front; rows_o.append(np.zeros(NS)); rows_z.append((ZT - bt) + g * ((ZB + bb) - (ZT - bt)))
    rows_v.append(n_top + n_tch + g * n_front)
for j in range(m_bch):
    g = j / m_bch; rows_o.append(-ab * g); rows_z.append(ZB + bb * (1 - g)); rows_v.append(n_top + n_tch + n_front + g * n_bch)
for j in range(m_bot):
    g = j / (m_bot - 1); rows_o.append(-ab + g * (INNER + ab)); rows_z.append(np.full(NS, ZB))
    rows_v.append(n_top + n_tch + n_front + n_bch + g * (n_bot - 1))
RT = R                      # texture rows
R = len(rows_o)             # mesh rows
rows_v = np.array(rows_v + [RT]) / RT
rv = np.zeros((R, NS, 3))
for j in range(R):
    p2 = offs(rows_o[j])
    rv[j] = U[None, :] * p2[:, :1] + N[None, :] * p2[:, 1:2] + Z[None, :] * rows_z[j][:, None]
ii, jj = np.meshgrid(np.arange(NS), np.arange(R))
ii = ii.ravel(); jj = jj.ravel()
i1 = (ii + 1) % NS; j1 = (jj + 1) % R
quads = np.stack([jj * NS + ii, jj * NS + i1, j1 * NS + i1, j1 * NS + ii], axis=1)
uvq = np.stack([np.stack([ii / NS, rows_v[jj]], 1), np.stack([(ii + 1) / NS, rows_v[jj]], 1),
                np.stack([(ii + 1) / NS, rows_v[jj + 1]], 1), np.stack([ii / NS, rows_v[jj + 1]], 1)], axis=1)
rim_me = make_mesh("Claude lower rim", rv.reshape(-1, 3), quads, uvq.reshape(-1, 2), "ClaudeRimUV")
h_lo, h_hi = float(prof["h_lo"]), float(prof["h_hi"])
iron_mat = pbr_material("Claude forged iron", "ClaudeRimUV", "iron_albedo.png", "iron_rough.png", "iron_height16.png",
                        -h_lo / (h_hi - h_lo), h_hi - h_lo, metal="iron_metal.png")
rim_me.materials.append(iron_mat)
rim = bpy.data.objects["Lab Chest Lower Rim"]
if rim.data.name != "Claude lower rim":
    rim.data.name = "Codex backup Lab Chest Lower Rim"; rim.data.use_fake_user = True
rim.data = rim_me

# ---------------------------------------------------------------- the two small rim knobs
km = bpy.data.materials.get("Claude forged iron knob") or bpy.data.materials.new("Claude forged iron knob")
km.use_nodes = True
nt = km.node_tree; nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
geo = nt.nodes.new("ShaderNodeNewGeometry")
dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = tuple(N)
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.86; mr.inputs["From Max"].default_value = 0.97
mr.interpolation_type = "SMOOTHSTEP"
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 55.0; nz.inputs["Detail"].default_value = 3.0
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"
mixc.inputs["A"].default_value = (0.045, 0.047, 0.052, 1); mixc.inputs["B"].default_value = (0.32, 0.29, 0.25, 1)
mixr = nt.nodes.new("ShaderNodeMix"); mixr.data_type = "FLOAT"
mixr.inputs["A"].default_value = 0.56; mixr.inputs["B"].default_value = 0.32
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.004
nt.links.new(geo.outputs["Normal"], dot.inputs[0]); nt.links.new(dot.outputs["Value"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], mul.inputs[0]); nt.links.new(nz.outputs["Fac"], mul.inputs[1])
nt.links.new(mul.outputs["Value"], mixc.inputs["Factor"]); nt.links.new(mul.outputs["Value"], mixr.inputs["Factor"])
nt.links.new(mixc.outputs["Result"], bsdf.inputs["Base Color"]); nt.links.new(mixr.outputs["Result"], bsdf.inputs["Roughness"])
nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Metallic"].default_value = 0.9
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
for name in ("Lab Chest Rail Rivet 1 3", "Lab Chest Rail Rivet 1 4"):
    ob = bpy.data.objects[name]
    if ob.data.users > 1:
        ob.data = ob.data.copy()
    ob.data.materials[0] = km

for img in bpy.data.images:
    if img.name.startswith("Claude ") and not img.packed_file:
        img.pack()
bpy.ops.wm.save_as_mainfile(filepath=OUTBLEND, compress=True)
print("saved", OUTBLEND, len(wood_me.vertices), len(rim_me.vertices))
