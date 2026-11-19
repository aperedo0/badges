import bpy, json, sys
out={}
for o in bpy.data.objects:
    if not o.name.startswith("Chest Rig") and o.name!="Chest Removable Crank Key": continue
    d={"props": {k: (o[k] if isinstance(o[k],(int,float,str)) else str(o[k])) for k in o.keys()}, "rotmode": o.rotation_mode,
       "mw": [list(map(lambda v: round(v,4), r)) for r in o.matrix_world]}
    if o.animation_data:
        d["drivers"]=[]
        for f in o.animation_data.drivers:
            dr=f.driver
            d["drivers"].append({"path": f.data_path, "idx": f.array_index, "expr": dr.expression,
              "vars": [(v.name, v.type, [(t.id.name if t.id else None, t.data_path, t.transform_type) for t in v.targets]) for v in dr.variables]})
        if o.animation_data.action:
            a=o.animation_data.action
            d["fcurves"]=[]
            try:
                fcs = a.fcurves
            except AttributeError:
                fcs = [fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
            for fc in fcs:
                d["fcurves"].append({"path": fc.data_path, "idx": fc.array_index, "keys": [(round(k.co[0],1), round(k.co[1],4)) for k in fc.keyframe_points]})
    d["children"]=[c.name for c in o.children]
    out[o.name]=d
sc=bpy.data.scenes['Chest Complete Form Phase 1']
out["_markers"]=[(m.name,m.frame) for m in sc.timeline_markers]
json.dump(out, open(sys.argv[-1],"w"), indent=1)
