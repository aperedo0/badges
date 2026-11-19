"""Verify and finalize only the new, individual editable checkpoint files."""
import bpy,json,hashlib,re,zipfile
from pathlib import Path
from collections import Counter
ROOT=Path('/Users/antonioperedo/Desktop/badges/badge_family_compact_20261106');rows=json.loads((ROOT/'manifest.json').read_text());results=json.loads((ROOT/'results.json').read_text())
bpy.context.preferences.filepaths.save_version=0
for row in rows:
 if results[row['key']]['status']!='validated_candidate':continue
 c=ROOT/'badges'/row['slug']/'candidate01';path=c/'source/model.blend';bpy.ops.wm.open_mainfile(filepath=str(path))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==results[row['key']]['after']['meshes'];triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons);assert triangles==results[row['key']]['after']['triangles']
 with zipfile.ZipFile(c/'model.usdz') as z:expected={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith(('.usd','.usdc','.usda','/'))}
 images={n.image for o in meshes for slot in o.material_slots if slot.material and slot.material.use_nodes for n in slot.material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
 bpy.ops.file.pack_all();evidence=[]
 for im in images:
  assert im.packed_file,('Unpacked image',row['key'],im.name)
  sha=hashlib.sha256(im.packed_file.data).hexdigest();assert sha in expected,('Checkpoint image mismatch',row['key'],im.name,sha);evidence.append(dict(name=im.name,sha256=sha))
 # Remove import suffixes only when the resulting name is unique within this
 # standalone copy. This never loads or changes the live Blender application.
 for ids in [bpy.data.objects,bpy.data.meshes,bpy.data.materials,bpy.data.images]:
  counts=Counter(re.sub(r'\.\d{3}$','',v.name) for v in ids)
  for v in list(ids):
   name=re.sub(r'\.\d{3}$','',v.name)
   if counts[name]==1:v.name=name
 if any('Casing___' in p for p in row['protected_mesh_paths']):assert any(o.name=='Casing___smooth_rounded_outer_edge_mobile_geometry' for o in meshes)
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 sha=hashlib.sha256((c/'model.usdz').read_bytes()).hexdigest();assert sha==results[row['key']]['output_sha256']
 (c/'checkpoint_validation.json').write_text(json.dumps(dict(complete_mesh_count=len(meshes),triangles=triangles,all_used_images_packed_and_match_usdz=True,images=evidence,usdz_unchanged_sha256=sha),indent=2)+'\n');print('CHECKPOINT VERIFIED',row['title'],flush=True)
