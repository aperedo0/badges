import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_character');sc=bpy.data.scenes['Test plank master'];assert not bpy.app.is_job_running('RENDER')
for im in bpy.data.images:
 if im.source=='FILE' and im.has_data and not im.packed_file:im.pack()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline.blend'),compress=True,copy=True)
def mh(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
o=sc.objects['Lab Chest Lower Rim'];m=o.data.materials[0];nodes=[]
for n in m.node_tree.nodes:
 nodes.append(dict(name=n.name,type=n.bl_idname,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None,inputs={s.name:list(s.default_value) if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value for s in n.inputs if hasattr(s,'default_value') and isinstance(s.default_value,(int,float,str,bool)) or hasattr(s,'default_value') and type(s.default_value).__name__=='bpy_prop_array'}))
proof=dict(file=bpy.data.filepath,baseline=str(D/'baseline.blend'),sha256=hashlib.sha256((D/'baseline.blend').read_bytes()).hexdigest(),iron_geometry=mh(o),iron_mesh=o.data.name,wood_geometry=mh(sc.objects['Master Chest Body Envelope']),material=m.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),nodes=nodes,world=[dict(name=n.name,type=n.bl_idname,inputs={s.name:list(s.default_value) if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value for s in n.inputs if hasattr(s,'default_value') and (isinstance(s.default_value,(int,float,str,bool)) or type(s.default_value).__name__=='bpy_prop_array')}) for n in sc.world.node_tree.nodes],render_running=False)
(D/'checkpoint.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k not in ['nodes','world']}))
