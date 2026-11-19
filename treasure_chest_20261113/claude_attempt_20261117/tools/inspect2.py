import bpy, numpy as np, json
o = bpy.data.objects["Master Chest Body Envelope"]
me = o.data
n = len(me.polygons)
mi = np.zeros(n, dtype=np.int32); me.polygons.foreach_get("material_index", mi)
cen = np.zeros(n*3); me.polygons.foreach_get("center", cen); cen = cen.reshape(-1,3)
nor = np.zeros(n*3); me.polygons.foreach_get("normal", nor); nor = nor.reshape(-1,3)
M = np.array(o.matrix_world)
res = {"matrix": M.tolist(), "polys": n}
for i in (0,1):
    c = cen[mi==i]
    if len(c)==0: continue
    w = c @ M[:3,:3].T + M[:3,3]
    res[f"mat{i}"] = {"count": int(len(c)), "local_mn": c.min(0).tolist(), "local_mx": c.max(0).tolist(), "world_mn": w.min(0).tolist(), "world_mx": w.max(0).tolist(), "mean_normal_local": nor[mi==i].mean(0).tolist()}
# uv bounds for mat1 in each uv layer
ls = np.zeros(n, dtype=np.int32); me.polygons.foreach_get("loop_start", ls)
lt = np.zeros(n, dtype=np.int32); me.polygons.foreach_get("loop_total", lt)
loopmat = np.repeat(mi, lt)
for uvl in me.uv_layers:
    uv = np.zeros(len(me.loops)*2); uvl.uv.foreach_get("vector", uv); uv = uv.reshape(-1,2)
    for i in (0,1):
        u = uv[loopmat==i]
        if len(u): res[f"uv_{uvl.name}_mat{i}"] = [u.min(0).tolist(), u.max(0).tolist()]
# local z histogram of face centers where normals face front for body: find plank bands
res["rot"] = list(o.matrix_world.to_euler())
r = bpy.data.objects["Lab Chest Lower Rim"]
res["rim_matrix"] = np.array(r.matrix_world).tolist()
res["rim_rot"] = list(r.matrix_world.to_euler())
vv = np.zeros(len(r.data.vertices)*3); r.data.vertices.foreach_get("co", vv); vv=vv.reshape(-1,3)
res["rim_local_mn"]=vv.min(0).tolist(); res["rim_local_mx"]=vv.max(0).tolist()
for uvl in r.data.uv_layers:
    uv = np.zeros(len(r.data.loops)*2); uvl.uv.foreach_get("vector", uv); uv = uv.reshape(-1,2)
    res["rim_uv_"+uvl.name]=[uv.min(0).tolist(), uv.max(0).tolist()]
res["rim_polys"]=len(r.data.polygons)
res["parents"]={x.name:(x.parent.name if x.parent else None) for x in (o,r)}
json.dump(res, open("inspect2.json","w"), indent=1)
