import bpy,json,hashlib
from pathlib import Path
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab')
s=bpy.context.scene;o=s.objects['Chest Body Envelope']
def geom(q):
 return hashlib.sha256(bytes(str(([tuple(v.co) for v in q.data.vertices],[tuple(p.vertices) for p in q.data.polygons],list(q.matrix_world),q.parent.name if q.parent else None)), 'utf8')).hexdigest()
d=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,scene=s.name,frame=s.frame_current,engine=s.render.engine,cycles_device=s.cycles.device,samples=s.cycles.samples,color=[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure],camera=s.camera.name,objects=[dict(name=q.name,type=q.type,hide=q.hide_render) for q in s.objects if q.type in ['LIGHT','CAMERA','EMPTY']],images=[dict(name=i.name,file=i.filepath,source=i.source,size=list(i.size)) for i in bpy.data.images],materials=[dict(name=m.name,nodes=[dict(name=n.name,type=n.type) for n in m.node_tree.nodes] if m.use_nodes else []) for m in o.data.materials],model_hashes={q.name:geom(q) for q in s.objects if q.type=='MESH' and q.get('full_form')},modifiers=[dict(name=m.name,type=m.type) for m in o.modifiers])
(P/'live_inventory.json').write_text(json.dumps(d,indent=2,default=str))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'baseline_live.blend'),compress=True)
print(json.dumps({k:d[k] for k in ['file','dirty','engine','cycles_device','samples','color','camera','modifiers']}))
