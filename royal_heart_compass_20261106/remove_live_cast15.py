from pathlib import Path
import bpy
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');C=R/'ruby_crown/candidate15';scene=bpy.context.scene
objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Ruby continuous cast acanthus foundation')];assert len(objects)==4
for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
(R/'active.txt').write_text('ruby_crown');import os;os.environ['BADGE_CANDIDATE']='candidate15'
bpy.data.libraries.write(str(C/'source/ruby_crown.blend'),{scene},compress=True);print('Ruby15 live source saved without the rejected flat cast panels')
