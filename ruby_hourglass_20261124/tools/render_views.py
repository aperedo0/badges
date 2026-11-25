"""Render actual Blender studio views from the saved editable file."""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent
scene=bpy.context.scene
cam=scene.camera
opts=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for name,angle in [('front',0),('early',25),('left',88),('back',180),('right',270)]:
    if opts and name not in opts: continue
    a=math.radians(angle); cam.location=(23*math.sin(a),-23*math.cos(a),1.8)
    cam.rotation_euler=(Vector((0,0,.27))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_percentage=100 if name=='front' else 52
    scene.cycles.samples=40 if name=='front' else 12
    scene.render.filepath=str(root/scene.get('candidate','candidate01')/('studio_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
