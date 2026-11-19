import bpy,sys,json
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;KEY=sys.argv[sys.argv.index('--')+1];F=W/KEY
bpy.ops.wm.open_mainfile(filepath=str(F/'geometry.blend'));body=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];mesh=body.data
mat=next(m for m in mesh.materials if m and m.name.startswith('Wood Lab ')).copy();mat.name='Wood Lab '+KEY
for role in ['albedo','roughness','normal']:
 im=bpy.data.images.load(str(F/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();mat.node_tree.nodes['Single plank '+role].image=im
slot=next(i for i,m in enumerate(mesh.materials) if m and m.name.startswith('Wood Lab '));mesh.materials[slot]=mat

oldpref=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(F/'master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=oldpref
print('Packed editable candidate',KEY,flush=True)
