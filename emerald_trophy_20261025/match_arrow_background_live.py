"""Copy the complete arrow green field into a complete trophy working copy."""
from pathlib import Path
import bpy
from mathutils import Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025');C=R/'candidate07'
with bpy.data.libraries.load(str(R/'candidate06/emerald_trophy.blend'),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
scene=loaded.scenes[0];scene.name='Emerald Trophy exact arrow background';bpy.context.window.scene=scene
old_fields=[o for o in scene.objects if o.type=='MESH' and o.visible_get() and any(m and m.name.startswith('Reference_traced_field') for m in o.data.materials)]
assert len(old_fields)==2,[(o.name,[m.name for m in o.data.materials]) for o in old_fields]
with bpy.data.libraries.load(str(R.parent/'emerald_archer_20261023/candidate02/emerald_archer.blend'),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
arrow=loaded.scenes[0]
fields=[o for o in arrow.objects if o.type=='MESH' and o.get('new_emblem') and any(m and m.name.startswith('Archer_field') for m in o.data.materials)]
assert len(fields)==2,[(o.name,[m.name for m in o.data.materials]) for o in fields]
for o in old_fields:bpy.data.objects.remove(o,do_unlink=True)
for src in fields:
 ob=src.copy();ob.data=src.data.copy();ob.name='Exact arrow background '+('back' if src.name.startswith('Back') else 'front');scene.collection.objects.link(ob)
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((1,0,0,0))
bpy.context.window.scene=scene;bpy.data.libraries.write(str(C/'emerald_trophy.blend'),{scene},compress=True)
print('Two complete arrow background meshes and their full material copied into complete trophy')
