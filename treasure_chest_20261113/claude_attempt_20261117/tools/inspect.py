import bpy, json, mathutils
out = {}
sc = bpy.data.scenes["Full chest material evaluation"]
out["scene_objs"] = {}
for o in sc.objects:
    if o.type != 'MESH':
        out["scene_objs"][o.name] = {"type": o.type, "loc": [round(v,3) for v in o.matrix_world.translation], "hide_render": o.hide_render}
        if o.type == 'LIGHT':
            l = o.data
            out["scene_objs"][o.name].update({"ltype": l.type, "energy": l.energy, "color": list(l.color)})
        continue
    bb = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    mn = [round(min(v[i] for v in bb),3) for i in range(3)]
    mx = [round(max(v[i] for v in bb),3) for i in range(3)]
    out["scene_objs"][o.name] = {"v": len(o.data.vertices), "mn": mn, "mx": mx, "mats": [s.material.name if s.material else None for s in o.material_slots],
        "mods": [(m.type, m.name) for m in o.modifiers], "uv": [u.name for u in o.data.uv_layers], "hide_render": o.hide_render, "attrs": [a.name for a in o.data.attributes if not a.name.startswith('.')][:12]}
cam = sc.camera
out["cam"] = {"name": cam.name, "loc": list(cam.matrix_world.translation), "rot": list(cam.matrix_world.to_euler()), "lens": cam.data.lens, "type": cam.data.type, "ortho": cam.data.ortho_scale, "sensor": cam.data.sensor_width}
w = sc.world
out["world_nodes"] = [(n.bl_idname, n.name) for n in w.node_tree.nodes]
out["unit_scale"] = sc.unit_settings.scale_length
out["cycles"] = {"device": sc.cycles.device, "samples": sc.cycles.samples, "denoise": sc.cycles.use_denoising}
def dump_mat(name):
    m = bpy.data.materials[name]
    nodes = []
    for n in m.node_tree.nodes:
        d = {"id": n.bl_idname, "name": n.name, "label": n.label}
        if n.bl_idname == 'ShaderNodeTexImage' and n.image: d["img"] = n.image.name; d["cs"]=n.image.colorspace_settings.name
        if n.bl_idname == 'ShaderNodeBsdfPrincipled':
            d["inputs"] = {i.name: (list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and i.name in ('Base Color','Metallic','Roughness','Specular IOR Level','Coat Weight')}
        if n.bl_idname in ('ShaderNodeNormalMap','ShaderNodeBump','ShaderNodeDisplacement'):
            d["vals"] = {i.name: i.default_value for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and not hasattr(i.default_value,'__len__')}
        nodes.append(d)
    links = [(l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name) for l in m.node_tree.links]
    return {"nodes": nodes, "links": links, "disp": m.displacement_method}
out["wood_mat"] = dump_mat("Wood Lab BC_final_polish")
out["atlas_mat"] = dump_mat("Chest wood shared varied atlas")
json.dump(out, open("inspect.json","w"), indent=1, default=str)
