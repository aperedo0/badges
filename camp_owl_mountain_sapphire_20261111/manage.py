"""Save and inspect the complete requested badge in the live Blender window."""
from pathlib import Path
import json, sys, subprocess, os
from blender_link import command

R=Path(__file__).resolve().parent
NAMES={'campfire_night':'Campfire Night','amber_owl':'Amber Owl','radiant_mountain':'Radiant Mountain','sapphire_teardrop':'Sapphire Teardrop'}
slug,candidate=sys.argv[1:3];B=R/slug;C=B/candidate
palette=json.loads((B/'palette_base.json').read_text())
if (C/'palette_overrides.json').exists():palette.update(json.loads((C/'palette_overrides.json').read_text()))
if (C/'palette_enamel.json').exists():palette.update(json.loads((C/'palette_enamel.json').read_text()))
(C/'palette.json').write_text(json.dumps(palette,indent=1)+'\n')
job=dict(parts=str(C/'parts.npz'),meta=str(C/'parts.json'),palette=str(C/'palette.json'),root=str(C),blend=str(B/(slug+'.blend')),scene=NAMES[slug],prefix=''.join(NAMES[slug].split()),mockup=str(B/'reference.png'),mockup_width_px=1254)
job_path=Path('/tmp')/('badge_live_job_'+slug+'.json');job_path.write_text(json.dumps(job))
code="import os\nos.environ['BADGE_JOB']="+repr(str(job_path))+"\n"+(R/'tools/build_live.py').read_text()+'''
from mathutils import Quaternion,Vector
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active
  s.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2)
  s.region_3d.view_location=Vector((-3.4,0,.27))
  s.region_3d.view_distance=13
  s.region_3d.view_perspective='ORTHO'
  s.shading.type='MATERIAL'
  s.overlay.show_overlays=True;s.overlay.show_floor=False;s.overlay.show_axis_x=False;s.overlay.show_axis_y=False;s.overlay.show_cursor=False;s.overlay.show_relationship_lines=False
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=JOB['blend'])
'''
print(command('execute_code',dict(code=code)),flush=True)
(C/'blender').mkdir(exist_ok=True)
print(command('get_viewport_screenshot',dict(filepath=str(C/'blender/complete_front.png'),max_size=1600)),flush=True)
for pose,angle in [('side_left',1.05),('back',3.141592653589793),('side_right',-1.05)]:
 code='''import bpy,math
from mathutils import Quaternion,Vector
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active
  s.region_3d.view_rotation=Quaternion((0,0,1),ANGLE) @ Quaternion((1,0,0),math.pi/2)
  s.region_3d.view_location=Vector((0,0,.27));s.region_3d.view_distance=8
'''.replace('ANGLE',str(angle))
 command('execute_code',dict(code=code))
 command('get_viewport_screenshot',dict(filepath=str(C/'blender'/(pose+'.png')),max_size=1400))
command('execute_code',dict(code='''import bpy,math
from mathutils import Quaternion,Vector
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2);s.region_3d.view_location=Vector((-3.4,0,.27));s.region_3d.view_distance=13
bpy.ops.wm.save_as_mainfile(filepath='''+repr(str(B/(slug+'.blend')))+''')
'''))
state=json.loads((R/'progress.json').read_text());state['active_badge']=slug;state['badges'][slug].update(status='Blender inspection',candidate=candidate,blend=str(B/(slug+'.blend')));(R/'progress.json').write_text(json.dumps(state,indent=2)+'\n')
print('Saved complete model, materials, reference and angle views:',slug,candidate,flush=True)
