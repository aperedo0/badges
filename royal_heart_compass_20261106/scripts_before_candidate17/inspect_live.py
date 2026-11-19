from pathlib import Path
import sys,json,math
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/water_match_20261014')
from blender_live import command
root=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
for row in json.loads((root/'gallery.json').read_text()):
 path=root/row['slug']/'candidate16/source'/(row['slug']+'.blend')
 load_code="import bpy\nfrom pathlib import Path\nwith bpy.data.libraries.load("+repr(str(path))+",link=False) as (source,target):target.scenes=[source.scenes[0]]\nscene=target.scenes[0]\nscene.name="+repr('Current third review '+row['slug'])+"\nbpy.context.window.scene=scene\n"
 command('execute_code',{'code':load_code})
 for pose,angle in [('front',0),('side',math.pi/2),('back',math.pi),('other_side',math.pi*1.5)]:
  code="import bpy\nfrom mathutils import Quaternion,Vector\nscene=bpy.data.scenes.get("+repr('Current third review '+row['slug'])+")\nbpy.context.window.scene=scene\nfor a in bpy.context.screen.areas:\n if a.type=='VIEW_3D':\n  a.spaces.active.region_3d.view_rotation=Quaternion((0,1,0),"+str(angle)+")\n  a.spaces.active.region_3d.view_location=Vector((0,.25,0))\n  a.spaces.active.region_3d.view_perspective='ORTHO'\n"
  command('execute_code',{'code':code})
  command('get_viewport_screenshot',{'filepath':str(root/row['slug']/'candidate16/review'/('blender_'+pose+'.png')),'max_size':1100})
 print(row['slug'],'four Blender sides inspected',flush=True)
