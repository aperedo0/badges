"""Release only superseded in memory scenes created by this badge build.

No filesystem file, simulator, build product, chat or unrelated scene is removed.
The latest complete scene for each of these five badges remains open and saved.
"""
import bpy,json,gc
from pathlib import Path
ROOT=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
rows=json.loads((ROOT/'gallery.json').read_text());old=[];keep=[]
for row in rows:
 assert (ROOT/row['slug']/'candidate06/source'/(row['slug']+'.blend')).is_file()
 prefix=row['name']+' complete working scene'
 scenes=[s for s in bpy.data.scenes if s.name==prefix or s.name.startswith(prefix+'.')]
 if not scenes:continue
 latest=max(scenes,key=lambda s:int(s.name.rsplit('.',1)[-1]) if s.name.rsplit('.',1)[-1].isdigit() else 0)
 keep.append(latest);old.extend(s for s in scenes if s!=latest)
oldset=set(old);objects=set()
for scene in old:
 for ob in scene.objects:
  assert ob.get('export_badge') or ob.type in ['LIGHT','CAMERA'] or (ob.type=='EMPTY' and ob.name.startswith(tuple(row['name'] for row in rows))),ob.name
  if set(ob.users_scene)<=oldset:objects.add(ob)
meshes={ob.data for ob in objects if ob.type=='MESH'};mats={m for me in meshes for m in me.materials if m}
images={node.image for m in mats if m.use_nodes for node in m.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
images|={ob.data for ob in objects if ob.type=='EMPTY' and ob.data and isinstance(ob.data,bpy.types.Image)}
worlds={s.world for s in old if s.world};lightdata={ob.data for ob in objects if ob.type=='LIGHT'};cameradata={ob.data for ob in objects if ob.type=='CAMERA'}
report=dict(retained_scenes=[s.name for s in keep],superseded_scenes=[s.name for s in old],superseded_objects=len(objects),unrelated_scenes_retained=[s.name for s in bpy.data.scenes if s not in oldset and s not in keep])
if bpy.context.window.scene in oldset:bpy.context.window.scene=keep[0]
for scene in old:bpy.data.scenes.remove(scene)
for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
for collection,items in [(bpy.data.meshes,meshes),(bpy.data.materials,mats),(bpy.data.worlds,worlds),(bpy.data.lights,lightdata),(bpy.data.cameras,cameradata)]:
 for item in items:
  item.use_fake_user=False
  if item.users==0:collection.remove(item)
for image in images:
 if str(Path(bpy.path.abspath(image.filepath))).startswith(str(ROOT)):
  image.use_fake_user=False
  if image.users==0:bpy.data.images.remove(image)
gc.collect();(ROOT/'memory_release.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
