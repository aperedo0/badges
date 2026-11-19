import bpy, numpy as np, json
res = {}
o = bpy.data.objects["Master Chest Body Envelope"]; me = o.data
nv = len(me.vertices); co = np.zeros(nv*3); me.vertices.foreach_get("co", co); co = co.reshape(-1,3)
n = len(me.polygons)
mi = np.zeros(n, dtype=np.int32); me.polygons.foreach_get("material_index", mi)
lt = np.zeros(n, dtype=np.int32); me.polygons.foreach_get("loop_total", lt)
lv = np.zeros(len(me.loops), dtype=np.int32); me.loops.foreach_get("vertex_index", lv)
loopmat = np.repeat(mi, lt)
v1 = np.unique(lv[loopmat==1]); v0 = np.unique(lv[loopmat==0])
nor = np.zeros(n*3); me.polygons.foreach_get("normal", nor); nor = nor.reshape(-1,3)
area = np.zeros(n); me.polygons.foreach_get("area", area)
N = (nor[mi==1]*area[mi==1,None]).sum(0); N[2]=0; N/=np.linalg.norm(N)
U = np.array([-N[1], N[0], 0.0])
if U[0] < 0: U = -U
p = co[v1]
u = p@U; d = p@N; z = p[:,2]
res["N"]=N.tolist(); res["U"]=U.tolist()
res["plank"] = {"u":[u.min(),u.max()], "z":[z.min(),z.max()], "d_pct": np.percentile(d,[0,1,5,25,50,75,95,99,100]).tolist(), "nverts": int(len(v1))}
# mat0 verts
p0 = co[v0]
res["mat0_verts"] = [[round(float(a),4) for a in (q@U, q@N, q[2])] for q in p0][:400]
res["mat0_n"]=len(v0)
# d profile vs z (median d in z bins) and vs u
zb = np.linspace(z.min(), z.max(), 41); idx = np.digitize(z, zb)
res["d_by_z"] = [[round(float(zb[i-1]),3), round(float(np.median(d[idx==i])),4), round(float(d[idx==i].min()),4), round(float(d[idx==i].max()),4)] for i in range(1,41) if (idx==i).any()]
ub = np.linspace(u.min(), u.max(), 41); idx = np.digitize(u, ub)
res["d_by_u"] = [[round(float(ub[i-1]),3), round(float(np.median(d[idx==i])),4), round(float(d[idx==i].min()),4), round(float(d[idx==i].max()),4)] for i in range(1,41) if (idx==i).any()]
# rim objects
for name in ("Lab Chest Lower Rim", "Chest Lower Rim", "Lab Chest Rail Rivet 1 3", "Lab Chest Rail Rivet 1 4", "Lab Chest Central Lower Cuff", "Lab Chest Upper Lid Rim", "Lab Chest Body Upper Rim"):
    ob = bpy.data.objects.get(name)
    if not ob: res[name]=None; continue
    m = ob.data
    vv = np.zeros(len(m.vertices)*3); m.vertices.foreach_get("co", vv); vv=vv.reshape(-1,3)
    W = np.array(ob.matrix_world); w = vv@W[:3,:3].T + W[:3,3]
    res[name] = {"v": len(m.vertices), "p": len(m.polygons), "u":[float((w@U).min()), float((w@U).max())], "d":[float((w@N).min()), float((w@N).max())], "z":[float(w[:,2].min()), float(w[:,2].max())], "scenes":[s.name for s in ob.users_scene], "mats":[s.material.name for s in ob.material_slots if s.material]}
    if len(m.vertices) < 400:
        res[name]["verts"] = [[round(float(a),4) for a in (q@U, q@N, q[2])] for q in w]
res["names_rim_like"] = [ob.name for ob in bpy.data.objects if "Rim" in ob.name or "Rail" in ob.name][:80]
sc = bpy.data.scenes["Full chest material evaluation"]
ll = {}
for ob in sc.objects:
    if ob.type=='LIGHT':
        rc = ob.light_linking.receiver_collection
        ll[ob.name] = {"recv": rc.name if rc else None, "recv_objs": [(c.name) for c in rc.all_objects] if rc else None, "size": [ob.data.size, getattr(ob.data,'size_y',None)], "shape": ob.data.shape, "rot": list(ob.matrix_world.to_euler()), "spread": ob.data.spread}
res["lights"] = ll
w = sc.world
wn = {}
for nd in w.node_tree.nodes:
    wn[nd.name] = {i.name: (list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked}
res["world"] = wn
res["world_links"] = [(l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name) for l in w.node_tree.links]
res["film_transparent"] = sc.render.film_transparent
json.dump(res, open("inspect3.json","w"), indent=1, default=str)
