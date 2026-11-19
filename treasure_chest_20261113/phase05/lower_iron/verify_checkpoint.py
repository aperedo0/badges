import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;proof=json.loads((D/'checkpoint.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];co=np.empty(len(body.data.vertices)*3,np.float32);body.data.vertices.foreach_get('co',co);assert hashlib.sha256(co.tobytes()).hexdigest()==proof['wood_geometry_sha256']
required={}
for scene in bpy.data.scenes:
 for obj in scene.objects:
  if obj.type=='MESH':
   for mat in obj.data.materials:
    if mat and mat.use_nodes:
     for n in mat.node_tree.nodes:
      if n.type=='TEX_IMAGE' and n.image:required[n.image.name]=n.image
  if obj.type=='EMPTY' and getattr(obj,'empty_display_type',None)=='IMAGE' and obj.data:required[obj.data.name]=obj.data
 if scene.world and scene.world.use_nodes:
  for n in scene.world.node_tree.nodes:
   if n.type in ['TEX_IMAGE','TEX_ENVIRONMENT'] and n.image:required[n.image.name]=n.image
assert all(im.packed_file for im in required.values()),[im.name for im in required.values() if not im.packed_file]
assert len([o for o in bpy.data.objects if o.name.startswith('First chest owner reference')])==1
r=dict(restored_in_fresh_Blender=True,wood_geometry_exact=True,required_images_packed=sorted(required),single_reference=True,unused_empty_images=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.name not in required]);(D/'checkpoint_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
o=sc.objects['Lab Chest Lower Rim'];a=np.array([tuple(v.co) for v in o.data.vertices]);from mathutils import Matrix
import math
rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'));local=np.c_[a[:,0],a[:,2],-a[:,1]]@rot;np.savez_compressed(D/'rim_geometry.npz',world=a,local=local,faces=np.array([len(p.vertices) for p in o.data.polygons]));(D/'rim_info.json').write_text(json.dumps(dict(bounds=[local.min(0).tolist(),local.max(0).tolist()],matrix=[list(r) for r in o.matrix_world],uvs=[u.name for u in o.data.uv_layers],smooth=sum(p.use_smooth for p in o.data.polygons)),indent=2))
