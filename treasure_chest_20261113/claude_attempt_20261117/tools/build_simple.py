"""Simple style on the whole chest: planks, smoky iron, steel rivets, bronze lock and hasp, brass rings.

Run: blender -b chest_claude.blend --python tools/build_simple.py -- simple/maps chest_simple.blend
"""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rim_mesh import rim_arrays  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
MAPS, OUTBLEND = os.path.abspath(args[0]), os.path.abspath(args[1])
U = np.array([0.8480481513760686, 0.529919175863294, 0.0])
N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
Z = np.array([0.0, 0.0, 1.0])
L, STEP = 5.0910, 0.006
# front planks: name, bottom z, height (must match the maps made by run_simple.sh)
PLANKS = [("plank01", -2.2008, 1.0238), ("plank02", -1.1770, 0.5370), ("plank03", -0.6400, 0.9875)]
IRON_BASE = (0.035, 0.032, 0.030)
BRONZE_BASE = (0.44, 0.264, 0.088)   # a touch darker than step 5 (0.50, 0.30, 0.10)
RING_BASE = (0.62, 0.40, 0.13)
IRON_SCAN = 0.70          # strength of the fine real metal surface on the grey iron (1.0 was step 4)


def load(fname, cs):
    img = bpy.data.images.load(os.path.join(MAPS, fname), check_existing=False)
    img.name = "Simple " + fname
    img.colorspace_settings.name = cs
    img.pack()
    return img


def new_mesh(name, verts, quads, uvs, uvname):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
    me.loops.add(quads.size); me.loops.foreach_set("vertex_index", quads.astype(np.int32).ravel())
    me.polygons.add(len(quads)); me.polygons.foreach_set("loop_start", np.arange(0, quads.size, 4, dtype=np.int32))
    me.update(calc_edges=True)
    me.uv_layers.new(name=uvname).uv.foreach_set("vector", uvs.astype(np.float32).ravel())
    me.polygons.foreach_set("use_smooth", np.ones(len(quads), dtype=bool))
    me.validate(); me.update()
    return me


def image_material(name, uvname, prefix, disp_scale=None, bump_range=None, metal=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = uvname

    def tex(fname, cs):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = load(fname, cs); t.interpolation = "Cubic"
        nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
        return t

    nt.links.new(tex(prefix + "_albedo.png", "sRGB").outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex(prefix + "_rough.png", "Non-Color").outputs["Color"], bsdf.inputs["Roughness"])
    if metal:
        nt.links.new(tex(prefix + "_metal.png", "Non-Color").outputs["Color"], bsdf.inputs["Metallic"])
    th = tex(prefix + "_height16.png", "Non-Color")
    if disp_scale:
        disp = nt.nodes.new("ShaderNodeDisplacement")
        disp.inputs["Midlevel"].default_value = 1.0; disp.inputs["Scale"].default_value = disp_scale
        nt.links.new(th.outputs["Color"], disp.inputs["Height"])
        nt.links.new(disp.outputs["Displacement"], out.inputs["Displacement"])
        m.displacement_method = "BOTH"
    else:
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = bump_range
        nt.links.new(th.outputs["Color"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


# ---- front planks ---------------------------------------------------------------
like = bpy.data.objects["Claude Bottom Planks"]
cols = list(like.users_collection)
for name in ("Claude Bottom Planks", "Claude Front Upper Planks"):
    bpy.data.objects.remove(bpy.data.objects[name])
for pname, z0, H in PLANKS:
    nx, ny = int(round(L / STEP)), int(round(H / STEP))
    gx, gy = np.meshgrid(np.linspace(0, L, nx + 1), np.linspace(0, H, ny + 1))
    gx, gy = gx.ravel(), gy.ravel()
    verts = U[None, :] * (gx - L / 2)[:, None] + N[None, :] * 1.6 + Z[None, :] * (z0 + gy)[:, None]
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny))
    v00 = (jj * (nx + 1) + ii).ravel()
    quads = np.stack([v00, v00 + 1, v00 + nx + 2, v00 + nx + 1], axis=1)
    me = new_mesh("Simple " + pname, verts, quads, np.stack([gx[quads.ravel()] / L, gy[quads.ravel()] / H], 1), "SimplePlankUV")
    me.materials.append(image_material("Simple wood " + pname, "SimplePlankUV", pname, disp_scale=0.06))
    ob = bpy.data.objects.new("Simple Front " + pname.capitalize(), me)
    for c in cols:
        c.objects.link(ob)

# ---- bottom rim (authored maps) ----------------------------------------------------
prof = dict(np.load(os.path.join(MAPS, "rim_profile.npz")))
rv, rq, ruv = rim_arrays(prof, NS=1280, mesh_rows=(8, 8, 24, 8, 4), round_mix=0.5)
rme = new_mesh("Simple lower rim", rv, rq, ruv, "SimpleRimUV")
rme.materials.append(image_material("Simple smoky iron rim", "SimpleRimUV", "rim",
                                    bump_range=float(prof["h_hi"]) - float(prof["h_lo"]), metal=True))
bpy.data.objects["Lab Chest Lower Rim"].data = rme

# ---- the other wood panels: same meshes as before, new simple plank maps ------------
for obname, prefix in (("Claude Back Planks", "back"), ("Claude End Planks A", "end_a"), ("Claude End Planks B", "end_b"),
                       ("Claude Lid Planks", "lid"), ("Claude Lid Cap Planks A", "cap_a"), ("Claude Lid Cap Planks B", "cap_b")):
    bpy.data.objects[obname].data.materials[0] = image_material("Simple wood " + prefix, "ClaudePlankUV", prefix, disp_scale=0.06)
# faces inside the chest: the simple plank, box projected
inside = bpy.data.materials["Claude carved planks inside"]
for n in inside.node_tree.nodes:
    if n.bl_idname == "ShaderNodeTexImage":
        to = n.outputs["Color"].links[0].to_socket.name
        n.image = bpy.data.images["Simple plank02_" + {"Base Color": "albedo", "Roughness": "rough", "Height": "height16"}[to] + ".png"]
    elif n.bl_idname == "ShaderNodeMapping" and abs(n.inputs["Scale"].default_value[0] - 1.0) > 1e-6:
        n.inputs["Scale"].default_value = (1 / 5.091, 1 / 5.091, 1 / 0.537)
    elif n.bl_idname == "ShaderNodeBump":
        n.inputs["Distance"].default_value = 0.06

# ---- metals for any shape: procedural, with a fine real metal surface on top ---------
SCAN_DIR = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/lower_iron/resources/Metal055A"
scan_r = bpy.data.images.load(os.path.join(SCAN_DIR, "Metal055A_1K-PNG_Roughness.png")); scan_r.colorspace_settings.name = "Non-Color"; scan_r.pack()
scan_d = bpy.data.images.load(os.path.join(SCAN_DIR, "Metal055A_1K-PNG_Displacement.png")); scan_d.colorspace_settings.name = "Non-Color"; scan_d.pack()
SCAN_MEAN, SCAN_ROUGH, SCAN_TONE, SCAN_BUMP = 0.274, 1.3, 1.6, 0.03


def add_metal_scan(mat, k=1.0):
    """Fine grayscale detail from ambientCG Metal055A (CC0) on roughness, tone and bump."""
    t = mat.node_tree
    b = next(n for n in t.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    co = t.nodes.new("ShaderNodeTexCoord"); mp = t.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 1.2, 1 / 1.2, 1 / 1.2)
    t.links.new(co.outputs["Object"], mp.inputs["Vector"])

    def box(img):
        n = t.nodes.new("ShaderNodeTexImage"); n.image = img; n.projection = "BOX"; n.projection_blend = 0.25
        t.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n.outputs["Color"]

    def m(op, x, y):
        n = t.nodes.new("ShaderNodeMath"); n.operation = op
        for sock, v in ((n.inputs[0], x), (n.inputs[1], y)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            else:
                t.links.new(v, sock)
        return n.outputs[0]

    d = m("SUBTRACT", box(scan_r), SCAN_MEAN)
    old = b.inputs["Roughness"].links[0].from_socket
    t.links.new(m("ADD", old, m("MULTIPLY", d, SCAN_ROUGH * k)), b.inputs["Roughness"])
    oldc = b.inputs["Base Color"].links[0].from_socket
    sc_ = t.nodes.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"
    t.links.new(oldc, sc_.inputs[0]); t.links.new(m("SUBTRACT", 1.0, m("MULTIPLY", d, SCAN_TONE * k)), sc_.inputs["Scale"])
    t.links.new(sc_.outputs["Vector"], b.inputs["Base Color"])
    oldn = b.inputs["Normal"].links[0].from_socket
    bp = t.nodes.new("ShaderNodeBump"); bp.inputs["Distance"].default_value = SCAN_BUMP * k
    t.links.new(box(scan_d), bp.inputs["Height"]); t.links.new(oldn, bp.inputs["Normal"])
    t.links.new(bp.outputs["Normal"], b.inputs["Normal"])


def piece_metal(name, base, metallic, rough, marks_k=0.17, cloud_k=0.26, bevel=0.03, lift=0.08, tone0=None,
                scan=1.0, cloud_bump=0.009, mark_scale=(7.0, 10.0), mask_scale=(3.5, 3.0), mark_bump=0.003):
    """Smooth metal with faint curvy marks and soft cloudiness, for a mesh of any shape (no UVs needed)."""
    pm = bpy.data.materials.new(name)
    pm.use_nodes = True
    nt = pm.node_tree; nt.nodes.clear()
    Nn, Ln = nt.nodes, nt.links

    def mth(op, a, b=None):
        n = Nn.new("ShaderNodeMath"); n.operation = op
        for sock, v in ((n.inputs[0], a), (n.inputs[1], b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                sock.default_value = v
            else:
                Ln.new(v, sock)
        return n.outputs[0]

    def mrange(v, f0, f1, t0, t1):
        n = Nn.new("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
        Ln.new(v, n.inputs["Value"])
        n.inputs["From Min"].default_value = f0; n.inputs["From Max"].default_value = f1
        n.inputs["To Min"].default_value = t0; n.inputs["To Max"].default_value = t1
        return n.outputs["Result"]

    tc = Nn.new("ShaderNodeTexCoord"); oi = Nn.new("ShaderNodeObjectInfo")
    offs = Nn.new("ShaderNodeVectorMath"); offs.operation = "SCALE"; offs.inputs[0].default_value = (37.0, 53.0, 71.0)
    Ln.new(oi.outputs["Random"], offs.inputs["Scale"])
    pos = Nn.new("ShaderNodeVectorMath"); pos.operation = "ADD"
    Ln.new(tc.outputs["Object"], pos.inputs[0]); Ln.new(offs.outputs["Vector"], pos.inputs[1])

    def noise(scale, detail):
        n = Nn.new("ShaderNodeTexNoise"); Ln.new(pos.outputs["Vector"], n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        return n.outputs["Fac"]

    def line(fac, width):
        d = mth("DIVIDE", mth("SUBTRACT", fac, 0.5), width)
        return mth("EXPONENT", mth("MULTIPLY", mth("MULTIPLY", d, d), -1.0))

    marks = mth("MULTIPLY", line(noise(mark_scale[0], 1.0), 0.012), mrange(noise(mask_scale[0], 1.0), 0.40, 0.60, 0.0, 1.0))
    marks = mth("MAXIMUM", marks, mth("MULTIPLY", mth("MULTIPLY", line(noise(mark_scale[1], 1.0), 0.011), mrange(noise(mask_scale[1], 0.0), 0.50, 0.68, 0.0, 1.0)), 0.7))
    cloud = noise(1.6, 2.0)
    attr = Nn.new("ShaderNodeAttribute"); attr.attribute_name = "claude_wear"      # bevel strips marked earlier
    t0 = (1.10 - 0.5 * cloud_k) if tone0 is None else tone0
    tone = mth("ADD", mth("ADD", mth("ADD", t0, mth("MULTIPLY", marks, marks_k)), mth("MULTIPLY", cloud, cloud_k)),
               mth("MULTIPLY", attr.outputs["Fac"], lift))
    colv = Nn.new("ShaderNodeVectorMath"); colv.operation = "SCALE"; colv.inputs[0].default_value = base
    Ln.new(tone, colv.inputs["Scale"])
    r = mth("SUBTRACT", mth("SUBTRACT", mth("ADD", rough - 0.05, mth("MULTIPLY", cloud, 0.10)), mth("MULTIPLY", marks, 0.3 * marks_k)),
            mth("MULTIPLY", attr.outputs["Fac"], 0.06))
    bump = Nn.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 1.0
    Ln.new(mth("ADD", mth("MULTIPLY", marks, mark_bump * marks_k), mth("MULTIPLY", cloud, cloud_bump * cloud_k)), bump.inputs["Height"])
    if bevel > 0:
        bev = Nn.new("ShaderNodeBevel"); bev.samples = 4; bev.inputs["Radius"].default_value = bevel   # soft edges where none are modelled
        Ln.new(bev.outputs["Normal"], bump.inputs["Normal"])
    bsdf = Nn.new("ShaderNodeBsdfPrincipled"); out = Nn.new("ShaderNodeOutputMaterial")
    Ln.new(colv.outputs["Vector"], bsdf.inputs["Base Color"]); Ln.new(r, bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = metallic
    Ln.new(bump.outputs["Normal"], bsdf.inputs["Normal"]); Ln.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    add_metal_scan(pm, scan)
    return pm


iron = piece_metal("Simple smoky iron pieces", IRON_BASE, 0.30, 0.50, scan=IRON_SCAN, cloud_bump=0.0065)
steel = piece_metal("Simple steel rivet", (0.20, 0.20, 0.205), 1.0, 0.44, marks_k=0.0, cloud_k=0.10, bevel=0.0, lift=0.0)
# brass: smooth satin with faint short curvy engraved marks, no grain
bronze = piece_metal("Simple aged bronze", BRONZE_BASE, 0.88, 0.50, marks_k=0.12, cloud_k=0.07, bevel=0.02, lift=0.0,
                     scan=0.15, cloud_bump=0.0, mark_scale=(15.0, 21.0), mask_scale=(8.0, 7.0), mark_bump=0.004)
ring = piece_metal("Simple brass ring", RING_BASE, 1.0, 0.34, marks_k=0.04, cloud_k=0.10, bevel=0.0, lift=0.0, scan=0.3, cloud_bump=0.0)
add_metal_scan(bpy.data.materials["Simple smoky iron rim"], IRON_SCAN)

BRONZE_KEYS = ("Lock", "Hasp", "Hinge Knuckle", "Hinge Pin", "Leaf Clamp", "Catch Leaf", "Key Driven", "Case Back")
PLAIN = ("Chest rough hardware forms", "Chest rough structural forms", "Claude forged iron knob")
report = {}
sc = bpy.data.scenes["Full chest material evaluation"]
for ob in sc.objects:
    if ob.type != "MESH" or not ob.material_slots:
        continue
    names = [s_.material.name for s_ in ob.material_slots if s_.material]
    n = ob.name
    if names == ["Claude forged iron pieces"]:
        ob.data.materials[0] = iron
        kind = "iron"
    elif names and all(x in PLAIN for x in names):
        if "Rear Hinge" in n:
            mat, kind = (steel, "steel") if "Rivet" in n else (iron, "iron")
        elif any(k in n for k in BRONZE_KEYS):
            mat, kind = bronze, "bronze"
        elif "Solid Ring Handle" in n:
            mat, kind = ring, "brass ring"
        elif any(k in n for k in ("Rivet", "Diamond", "Fastener", "Crown")):
            mat, kind = steel, "steel"
        else:
            mat, kind = iron, "iron"
        for slot in ob.material_slots:
            slot.link = "OBJECT"                      # leave shared meshes alone
            slot.material = mat
    else:
        continue
    report.setdefault(kind, set()).add(n.replace("Lab Chest ", "").rstrip("0123456789 -"))

bpy.ops.wm.save_as_mainfile(filepath=OUTBLEND, compress=True)
for k, v in report.items():
    print("SIMPLE", k, ":", ", ".join(sorted(v)))
