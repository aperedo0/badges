from pathlib import Path
import sys,math
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'water_match_20261014'))
from blender_live import command
for name,angle in [('angle',.55),('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2),('front',0)]:
 command('execute_code',{'code':"from mathutils import Quaternion\nfor a in bpy.context.screen.areas:\n if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),"+repr(angle)+")"})
 command('get_viewport_screenshot',{'filepath':str(R/(R/'candidate.txt').read_text().strip()/'review'/('blender_'+name+'.png')),'max_size':1400})
 print(name,flush=True)
