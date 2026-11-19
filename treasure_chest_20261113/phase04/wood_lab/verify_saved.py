import bpy,json,hashlib,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
# The original editable scene must survive byte equivalent geometry and rig evaluation.
def manifest(sc):
 bpy.context.window.scene=sc;sc.frame_set(0);bpy.context.view_layer.update()
 out={}
 for o in sc.objects:
  d=dict(type=o.type,parent=o.parent.name if o.parent else None,matrix=[list(r) for r in o.matrix_world],hide_render=o.hide_render)
  if o.type=='MESH':
   d.update(vertices=[tuple(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons],material_indices=[f.material_index for f in o.data.polygons],materials=[m.name if m else None for m in o.data.materials])
  if o.animation_data and o.animation_data.action:d['action']=o.animation_data.action.name
  out[o.name]=hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
 mats={m for o in sc.objects if o.type=='MESH' for m in o.data.materials if m and m.use_nodes}
 for m in mats:
  graph=[]
  for node in m.node_tree.nodes:
   values=[]
   for socket in node.inputs:
    if hasattr(socket,'default_value'):
     v=socket.default_value
     try:v=list(v) if not isinstance(v,(str,int,float,bool)) else v
     except TypeError:v=str(v)
     values.append([socket.name,v])
   entry=[node.name,node.type,values]
   if node.type=='TEX_IMAGE' and node.image:
    im=node.image;entry.append([im.colorspace_settings.name,hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else bpy.path.abspath(im.filepath)])
   graph.append(entry)
  links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
  out['material:'+m.name]=hashlib.sha256(json.dumps([graph,links],sort_keys=True).encode()).hexdigest()
 return out
bpy.ops.wm.open_mainfile(filepath=str(P/'baseline_live.blend'));before=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);bpy.ops.wm.open_mainfile(filepath=str(P/'wood_master.blend'));after=manifest(bpy.data.scenes['Chest Complete Form Phase 1']);assert before==after,[n for n in before if before[n]!=after.get(n)]
o=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];m=o.data;edgeids=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('edge_index',edgeids);counts=np.bincount(edgeids,minlength=len(m.edges));assert np.all(counts==2)
proof=dict(original_object_count=sum(not k.startswith('material:') for k in before),all_original_geometry_material_assignments_transforms_parents_and_action_names_preserved=True,original_material_graphs_and_packed_maps_preserved=True,watertight=bool(np.all(counts==2)),reference_shared=bpy.data.scenes['Test plank master'].objects['First chest owner reference'] is bpy.data.scenes['Chest Complete Form Phase 1'].objects['First chest owner reference'],all_final_images_packed=all(n.image and n.image.packed_file for n in bpy.data.materials['Wood Lab H'].node_tree.nodes if n.type=='TEX_IMAGE'),file_sha256=hashlib.sha256((P/'wood_master.blend').read_bytes()).hexdigest())
assert all(v for k,v in proof.items() if isinstance(v,bool));(P/'saved_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
