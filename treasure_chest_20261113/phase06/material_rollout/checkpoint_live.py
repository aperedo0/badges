import bpy,json,hashlib
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase06/material_rollout');assert not bpy.app.is_job_running('RENDER');assert not bpy.data.is_dirty;source=bpy.data.filepath
required={}
for sc in bpy.data.scenes:
 for o in sc.objects:
  if o.type=='MESH':
   for m in o.data.materials:
    if m and m.use_nodes:
     for n in m.node_tree.nodes:
      if n.type=='TEX_IMAGE' and n.image:required[n.image.name]=n.image
  if o.type=='EMPTY' and o.empty_display_type=='IMAGE' and o.data:required[o.data.name]=o.data
 if sc.world and sc.world.use_nodes:
  for n in sc.world.node_tree.nodes:
   if n.type=='TEX_ENVIRONMENT' and n.image:required[n.image.name]=n.image
assert all(i.packed_file for i in required.values());assert not list(bpy.data.libraries)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline.blend'),compress=True,copy=True)
(D/'checkpoint.json').write_text(json.dumps(dict(source=source,checkpoint=str(D/'baseline.blend'),sha256=hashlib.sha256((D/'baseline.blend').read_bytes()).hexdigest(),all_required_images_packed=True,required_images=sorted(required),owner_scope='Full chest wood and structural iron rollout; decorative hardware unchanged; stop after full chest evaluation'),indent=2));print('Complete packed baseline saved; live scene and layout preserved')
