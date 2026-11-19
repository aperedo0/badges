import bpy,math
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');C=R/'candidate03';sc=bpy.context.scene;sc.cycles.samples=128
objects=[o for o in sc.objects if o.type=='MESH'];original={o.name:o.matrix_world.copy() for o in objects}
try:
 for name,angle in [('early08',8),('early20',20),('side_left',60),('back',180),('side_right',-60),('front',0)]:
  for ob in objects:ob.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@original[ob.name]
  sc.render.filepath=str(C/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True)
finally:
 for ob in objects:ob.matrix_world=original[ob.name]
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'))
print('Rendered actual optics on complete badge through six views. Front restored.')
