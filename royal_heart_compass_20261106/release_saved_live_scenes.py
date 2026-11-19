"""Release only this run's saved inactive scenes, preserving every file."""
from pathlib import Path
import bpy,json
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');active=bpy.context.scene
prefixes=tuple(x+' complete working scene' for x in ['Amethyst Crown','Ruby Crown','Emerald Crown','Ruby Heart','Ocean Navigator'])
def own(s):return s.name.startswith(prefixes) or s.name.startswith('Current third review ')
remove=[s for s in bpy.data.scenes if s!=active and own(s)];unrelated=[s for s in bpy.data.scenes if not own(s)]
assert (R/'amethyst_crown/candidate06/source/amethyst_crown.blend').is_file()
protected_objects=set(o for s in bpy.data.scenes if s not in remove for o in s.objects)
objects=set(o for s in remove for o in s.objects)-protected_objects
meshes={o.data for o in objects if o.type=='MESH'};materials={m for me in meshes for m in me.materials if m};images={n.image for m in materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
names=[s.name for s in remove]
for s in remove:bpy.data.scenes.remove(s)
for o in objects:bpy.data.objects.remove(o,do_unlink=True)
for me in meshes:
 if me.users==0:bpy.data.meshes.remove(me)
for m in materials:
 if m.users==0:bpy.data.materials.remove(m)
for image in images:
 if image.users==0:bpy.data.images.remove(image)
assert all(s.name in bpy.data.scenes for s in unrelated);assert bpy.context.scene==active
report=dict(removed_only_saved_task_scenes=names,kept_active_scene=active.name,all_unrelated_scenes_preserved=True,unrelated_count=len(unrelated),no_files_deleted=True)
(R/'memory_release_block7.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
