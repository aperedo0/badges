from pathlib import Path
import sys,math,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'water_match_20261014'))
from blender_live import command
for name,angle in [('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2),('front',0)]:
 command('execute_code',{'code':"from mathutils import Quaternion\nfor a in bpy.context.screen.areas:\n if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),"+str(angle)+")"})
 print(command('get_viewport_screenshot',{'filepath':str(R/json.loads((R/'draft_design.json').read_text())['active_candidate']/'review'/('blender_'+name+'.png')),'max_size':1400}),flush=True)
