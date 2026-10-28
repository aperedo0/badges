import sys,math,json
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/water_match_20261014')
from blender_live import command
root='/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/candidate04/'
for name,angle in [('angle',.65),('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2),('front',0)]:
 code='from mathutils import Quaternion\nfor a in bpy.context.screen.areas:\n if a.type==\'VIEW_3D\':a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),'+repr(angle)+')'
 command('execute_code',{'code':code})
 print(name,command('get_viewport_screenshot',{'filepath':root+'blender_'+name+'.png','max_size':1400}),flush=True)
