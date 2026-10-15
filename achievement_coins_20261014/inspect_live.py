"""Inspect the actual open Blender scenes, without background renders."""
from pathlib import Path
import math,sys
from blender_live import command

TEMP=Path('/tmp/achievement_coins_20261014')
for name in sys.argv[1:] or ['clean','hourglass_teal','hourglass_gold','sunrise','sprout']:
    for label,angle in [('front',0.),('oblique',math.pi/5),('side',math.pi/2),('back',math.pi),('other_side',3*math.pi/2)]:
        code=f'''import bpy,math
from mathutils import Vector,Matrix
bpy.context.window.scene=bpy.data.scenes[{name!r}]
scene=bpy.context.scene
for obj in scene.objects:obj.select_set(False)
reference=scene.objects.get({(name+'_reference')!r})
reference.hide_viewport={label!='front'}
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  r=area.spaces.active.region_3d
  forward=Vector((-math.sin({angle}),0.,-math.cos({angle})))
  right=forward.cross(Vector((0.,1.,0.))).normalized();up=right.cross(forward)
  r.view_rotation=Matrix((right,up,-forward)).transposed().to_quaternion()
  r.view_location=Vector(({ -3.3 if label=='front' else 0. },0.,0.))
  r.view_distance={11 if label=='front' else 7.5}
  r.view_perspective='ORTHO'
'''
        command('execute_code',{'code':code})
        result=command('get_viewport_screenshot',{'filepath':str(TEMP/(name+'_live_'+label+'.png')),'max_size':1400})
        if not result.get('success'):raise RuntimeError(result)
    print('Inspected live '+name,flush=True)
