"""Build and capture each complete coin through the live Blender connection."""
from pathlib import Path
import json, sys, math
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'water_match_20261014'))
from blender_live import command
manifest=json.loads((R/'family/manifest.json').read_text())
for item in manifest:
    name=item['name'];c=R/'family'/name/'candidate01'
    command('execute_code',{'code':'badge_name='+repr(name)+'\n'+(R/'family_blender.py').read_text()})
    for pose,angle in [('front',0),('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2)]:
        command('execute_code',{'code':"from mathutils import Quaternion\nfor a in bpy.context.screen.areas:\n if a.type=='VIEW_3D':a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),"+repr(angle)+")"})
        command('get_viewport_screenshot',{'filepath':str(c/'review'/('blender_'+pose+'.png')),'max_size':1000})
    print(name+' Blender complete',flush=True)
