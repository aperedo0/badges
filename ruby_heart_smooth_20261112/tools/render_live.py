import bpy,math,numpy as np
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_smooth_20261112')
sc=bpy.context.scene;sc.cycles.samples=128
objects=[o for o in sc.objects if o.type=='MESH'];original={o.name:o.matrix_world.copy() for o in objects}
for name,angle in [('front',0),('side_left',60),('back',180),('side_right',-60)]:
 for ob in objects:ob.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@original[ob.name]
 sc.render.filepath=str(R/'candidate01'/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True)
for ob in objects:ob.matrix_world=original[ob.name]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'))
print('Rendered front, back and both sides in the open Blender')
