from pathlib import Path
import sys,math
from pace import work
work(2)
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
sys.path.insert(0,str(ROOT.parent/'water_match_20261014'))
from blender_live import command
(ROOT/'active_badge.txt').write_text(key)
print(command('execute_code',{'code':(ROOT/'build_live.py').read_text()}),flush=True)
for pose,angle in [('angle',.55),('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2),('front',0)]:
 command('execute_code',{'code':"from mathutils import Quaternion\nfor a in bpy.context.screen.areas:\n if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),"+repr(angle)+")"})
 command('get_viewport_screenshot',{'filepath':str(C/'review'/('blender_'+pose+'.png')),'max_size':1400});print(pose,flush=True)
