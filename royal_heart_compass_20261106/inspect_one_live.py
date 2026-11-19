"""Inspect only the current allowed complete Blender scene, without touching held work."""
from pathlib import Path
import sys,math,subprocess
from blender_mcp import command
R=Path(__file__).resolve().parent;slug,mode=sys.argv[1:3]
subprocess.run([sys.executable,str(R/'work_guard.py'),'120','complete live Blender angle inspection',slug],check=True)
assert (R/'active.txt').read_text().strip()==slug
for pose,angle in [('front',0),('side_left',math.pi/2),('back',math.pi),('side_right',math.pi*1.5)]:
 code='import bpy\nfrom mathutils import Quaternion,Vector\nfor area in bpy.context.screen.areas:\n if area.type=="VIEW_3D":\n  s=area.spaces.active\n  s.region_3d.view_rotation=Quaternion((0,1,0),'+str(angle)+')\n  s.region_3d.view_location=Vector((0,.25,0))\n  s.region_3d.view_perspective="ORTHO"\n'
 command('execute_code',{'code':code})
 command('get_viewport_screenshot',{'filepath':str(R/slug/mode/'review'/('blender_'+pose+'.png')),'max_size':1400})
print(slug,mode,'complete Blender views saved',flush=True)
