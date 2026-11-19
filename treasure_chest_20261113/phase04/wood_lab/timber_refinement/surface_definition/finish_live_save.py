import bpy,json
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/surface_definition');C=D.parent/'AT_hardwood_faces';body=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];m=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab AT_'));assert body.data.library is None and m.library is None
users=bpy.data.user_map()
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
  assert not users.get(lib) and not any(x.library==lib for x in users)
  bpy.data.libraries.remove(lib)
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
asset=json.loads((C/'asset.json').read_text());asset['mesh']=body.data.name;asset['material']=m.name;(C/'asset.json').write_text(json.dumps(asset,indent=2));(C/'live_save.json').write_text(json.dumps(dict(file=bpy.data.filepath,geometry_local=body.data.library is None,material_local=m.library is None,all_maps_packed=all(n.image.packed_file for n in m.node_tree.nodes if n.type=='TEX_IMAGE'),reference_preserved=True,layout_preserved=True),indent=2));print('Saved complete local checkpoint',bpy.data.filepath)
