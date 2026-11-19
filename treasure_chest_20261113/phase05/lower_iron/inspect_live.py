import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/lower_iron');sc=bpy.data.scenes['Test plank master'];R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));items=[]
for o in sc.objects:
 if o.type!='MESH':continue
 a=np.array([tuple(o.matrix_world@Vector(q)) for q in o.bound_box]);local=np.c_[a[:,0],a[:,2],-a[:,1]]@R
 items.append(dict(name=o.name,bounds=[local.min(0).tolist(),local.max(0).tolist()],vertices=len(o.data.vertices),polygons=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials],modifiers=[dict(name=m.name,type=m.type) for m in o.modifiers]))
proof=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,render_running=bpy.app.is_job_running('RENDER'),scene=sc.name,camera=sc.camera.name,items=items)
(D/'initial_live.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k!='items'}));print(json.dumps([o for o in items if any(k.lower() in o['name'].lower() for k in ['bottom','lower','foot','feet'])]))
