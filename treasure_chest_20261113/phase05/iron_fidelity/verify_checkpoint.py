import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;p=json.loads((D/'checkpoint.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master']
for name,expected in [('Lab Chest Lower Rim',p['iron_geometry']),('Master Chest Body Envelope',p['wood_geometry'])]:
 o=sc.objects[name];a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);assert hashlib.sha256(a.tobytes()).hexdigest()==expected
required={}
for scene in bpy.data.scenes:
 for o in scene.objects:
  if o.type=='MESH':
   for m in o.data.materials:
    if m and m.use_nodes:
     for n in m.node_tree.nodes:
      if n.type=='TEX_IMAGE' and n.image:required[n.image.name]=n.image
  if o.type=='EMPTY' and o.empty_display_type=='IMAGE' and o.data:required[o.data.name]=o.data
assert all(im.packed_file for im in required.values());r=dict(fresh_Blender_restore=True,existing_iron_and_wood_exact=True,required_images_packed=sorted(required),reference_single=len([o for o in bpy.data.objects if o.name.startswith('First chest owner reference')])==1);(D/'checkpoint_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
