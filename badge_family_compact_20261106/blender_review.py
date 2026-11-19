from pathlib import Path
import json,sys,math,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'water_match_20261014'))
from blender_live import command
rows=json.loads((ROOT/'manifest.json').read_text());results=json.loads((ROOT/'results.json').read_text())
for row in rows:
 if results[row['key']]['status']!='validated_candidate':continue
 c=ROOT/'badges'/row['slug']/'candidate01'
 if (c/'blender_review.json').exists():continue
 (ROOT/'blender_next.txt').write_text(row['slug']);command('execute_code',{'code':(ROOT/'blender_prepare.py').read_text()})
 for pose,angle in [('front',0),('side_left',math.pi/2),('back',math.pi),('side_right',-math.pi/2),('angle',.55)]:
  code=f'''import math\nfrom mathutils import Quaternion\nfor area in bpy.context.screen.areas:\n if area.type=='VIEW_3D':area.spaces.active.region_3d.view_rotation=Quaternion((0,1,0) if bpy.context.scene["badge_y_up_geometry"] else (0,0,1),{angle}) @ Quaternion((1,0,0),0 if bpy.context.scene["badge_y_up_geometry"] else math.pi/2)\n'''
  command('execute_code',{'code':code});command('get_viewport_screenshot',{'filepath':str(c/('blender_'+pose+'.png')),'max_size':1000})
 (c/'blender_review.json').write_text(json.dumps(dict(complete_scene=True,poses=['front','side_left','back','side_right','angle'],source=str(c/'source/model.blend')),indent=2))
 # Saved working scenes remain on disk. Remove this imported copy from memory.
 command('execute_code',{'code':'''scene=bpy.context.scene\nobjects=list(scene.objects)\nbpy.context.window.scene=next(s for s in bpy.data.scenes if s!=scene)\nbpy.data.scenes.remove(scene)\nfor obj in objects:\n if not any(obj.name in other.objects for other in bpy.data.scenes):bpy.data.objects.remove(obj,do_unlink=True)\n'''})
 print(row['title'],'Blender complete',flush=True)
