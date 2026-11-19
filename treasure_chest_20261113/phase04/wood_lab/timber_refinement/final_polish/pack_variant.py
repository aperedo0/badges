import bpy,sys,json
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;key=sys.argv[sys.argv.index('--')+1];C=W/key
bpy.ops.wm.open_mainfile(filepath=str(W/'AW_depth_hierarchy/master.blend'))
body=bpy.data.scenes['Test plank master'].objects['Master Chest Body Envelope'];slot=next(i for i,m in enumerate(body.data.materials) if m and m.name.startswith('Wood Lab '));mat=body.data.materials[slot].copy();mat.name='Wood Lab '+key;body.data.materials[slot]=mat
for role in ['albedo','roughness','normal']:
 im=bpy.data.images.load(str(C/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();mat.node_tree.nodes['Single plank '+role].image=im
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
print('Saved independent packed candidate',key,flush=True)
