"""Place elongated photographic strip lights where the two broad flanks can catch them."""
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
root=Path(bpy.data.filepath).parent
scene=bpy.context.scene
def reflector(name,object_name,source_pixel,color,power,width,height):
    from mathutils.geometry import intersect_point_tri_2d
    ob=scene.objects[object_name]
    x=(source_pixel[0]-558)*5.45/1245;z=2.995-(source_pixel[1]-87)*5.45/1245
    matches=[]
    for p in ob.data.polygons:
        if p.normal.y>-.12:continue
        pts=[ob.data.vertices[idx].co for idx in p.vertices]
        if intersect_point_tri_2d(Vector((x,z)),*[Vector((v.x,v.z)) for v in pts]):matches.append(p)
    if not matches:raise ValueError((name,source_pixel))
    face=min(matches,key=lambda f:f.center.y);center=Vector((x,face.center.y,z));normal=face.normal.normalized()
    incident=(center-scene.camera.location).normalized()
    loc=center+incident.reflect(normal)*7
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='RECTANGLE';data.size=width;data.size_y=height
    light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);light.location=loc;light.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
reflector('Crown softbox','Upper_Ruby_Facing',(801,181),(1,.79,.67),780,2.,3.1)
reflector('Lower strip reflection','Lower_Ruby_Facing',(315,1100),(1,.47,.19),610,1.0,3.7)
reflector('Long ruby edge','Upper_Ruby_Facing',(781,354),(1,.27,.095),420,.55,3.)
if globals().get('SAVE_HOURGLASS',False):
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
else:
    scene.render.resolution_percentage=55;scene.cycles.samples=24;scene.render.filepath=str(root/'candidate02/card_test.png')
    bpy.ops.render.render(write_still=True)
