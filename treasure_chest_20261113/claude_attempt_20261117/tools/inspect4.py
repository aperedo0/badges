import bpy, numpy as np, json, mathutils
U = np.array([0.8480481513760686, 0.529919175863294, 0.0]); N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
sc = bpy.data.scenes["Full chest material evaluation"]
res = {"objs": {}}
def udz(w): return np.stack([w@U, w@N, w[:,2]], 1)
for o in sc.objects:
    if o.type != 'MESH': continue
    m = o.data
    vv = np.zeros(len(m.vertices)*3); m.vertices.foreach_get("co", vv); vv = vv.reshape(-1,3)
    W = np.array(o.matrix_world); w = udz(vv@W[:3,:3].T + W[:3,3])
    ident = bool(np.allclose(W, np.eye(4), atol=1e-6))
    res["objs"][o.name] = {"v": len(m.vertices), "p": len(m.polygons), "mn": np.round(w.min(0),3).tolist(), "mx": np.round(w.max(0),3).tolist(),
        "mats": [s.material.name if s.material else None for s in o.material_slots], "ident": ident, "hide": o.hide_render, "parent": o.parent.name if o.parent else None,
        "mods": [md.type for md in o.modifiers]}
for name in ("Master Chest Body Envelope", "Lab Chest Barrel Lid Envelope"):
    o = bpy.data.objects[name]; m = o.data
    vv = np.zeros(len(m.vertices)*3); m.vertices.foreach_get("co", vv); vv = udz(vv.reshape(-1,3))
    n = len(m.polygons)
    nor = np.zeros(n*3); m.polygons.foreach_get("normal", nor); nor = udz(nor.reshape(-1,3))
    cen = np.zeros(n*3); m.polygons.foreach_get("center", cen); cen = udz(cen.reshape(-1,3))
    area = np.zeros(n); m.polygons.foreach_get("area", area)
    mi = np.zeros(n, dtype=np.int32); m.polygons.foreach_get("material_index", mi)
    groups = {}
    for i in range(n):
        key = tuple(np.round(nor[i],1).tolist())
        g = groups.setdefault(key, {"n":0, "area":0.0, "mn":cen[i].copy(), "mx":cen[i].copy(), "mi": set()})
        g["n"]+=1; g["area"]+=area[i]; g["mn"]=np.minimum(g["mn"],cen[i]); g["mx"]=np.maximum(g["mx"],cen[i]); g["mi"].add(int(mi[i]))
    big = sorted(groups.items(), key=lambda kv: -kv[1]["area"])[:40]
    res[name] = [{"normal": k, "n": g["n"], "area": round(g["area"],3), "mn": np.round(g["mn"],3).tolist(), "mx": np.round(g["mx"],3).tolist(), "mi": sorted(g["mi"])} for k,g in big]
    res[name+"_bounds"] = [np.round(vv.min(0),4).tolist(), np.round(vv.max(0),4).tolist()]
    if "Lid" in name:
        # cross-section: unique (d,z) of vertices near max u
        sel = vv[np.abs(vv[:,0]-vv[:,0].max())<1e-3]
        res["lid_section_maxu"] = np.round(sel[np.argsort(np.arctan2(sel[:,2]-0.38, sel[:,1]))],4).tolist()
        res["lid_u_values"] = np.unique(np.round(vv[:,0],3)).tolist()[:60]
        res["lid_uv"] = [u.name for u in m.uv_layers]
json.dump(res, open("inspect4.json","w"), indent=0, default=str)
