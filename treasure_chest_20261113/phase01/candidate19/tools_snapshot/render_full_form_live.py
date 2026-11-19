import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');OUT=R/'phase01/candidate19';sc=bpy.context.scene
objects=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];original={o.name:o.matrix_world.copy() for o in objects};cam=sc.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy();typ=cam.data.type
poses=json.loads((OUT/'render_queue.json').read_text())
try:
 for name,angle in poses:
  if name=='top':
   cam.data.type='ORTHO';cam.data.ortho_scale=8;cam.location=(0,0,22);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
  else:cam.data.type=typ;cam.location=loc;cam.rotation_euler=rot
  for ob in objects:ob.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@original[ob.name]
  sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
finally:
 for ob in objects:ob.matrix_world=original[ob.name]
 cam.location=loc;cam.rotation_euler=rot;cam.data.type=typ;bpy.context.view_layer.update()
print('Rendered',poses)
