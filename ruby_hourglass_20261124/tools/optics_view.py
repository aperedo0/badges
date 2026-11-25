"""Render the established style 2 gem shader in the source's camera and inspect facet samples."""
import bpy, numpy as np, math
from pathlib import Path
from mathutils import Vector
root=Path(bpy.data.filepath).parent
repo=root.parent
scene=bpy.context.scene
scene.cycles.device='CPU';scene.cycles.shading_system=True
scene.cycles.samples=12;scene.cycles.use_denoising=False
cam=scene.camera
cam.location=(0,-23,1.8);cam.rotation_euler=(Vector((0,0,-.55))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32;cam.data.lens=115.;cam.data.shift_y=.13
scene.render.resolution_percentage=65
template=(repo/'camp_owl_mountain_sapphire_20261111/tools/gem_development.osl').read_text()
template=template.replace('1.4576831','3.0').replace('color(8,4.3503597,.2)','color(1.25,16,12)').replace('badge_sapphire_development','hourglass_ruby')
template=template.replace('int findexit(','''float chash(vector p){
 float f=sin(dot(p,vector(127.1,311.7,74.7)))*43758.5453;return f-floor(f);}
float cloudnoise(vector p){
 vector a=vector(floor(p[0]),floor(p[1]),floor(p[2])); vector f=p-a;
 f=vector(f[0]*f[0]*(3-2*f[0]),f[1]*f[1]*(3-2*f[1]),f[2]*f[2]*(3-2*f[2]));
 float x00=mix(chash(a),chash(a+vector(1,0,0)),f[0]),x10=mix(chash(a+vector(0,1,0)),chash(a+vector(1,1,0)),f[0]);
 float x01=mix(chash(a+vector(0,0,1)),chash(a+vector(1,0,1)),f[0]),x11=mix(chash(a+vector(0,1,1)),chash(a+vector(1,1,1)),f[0]);
 return mix(mix(x00,x10,f[1]),mix(x01,x11,f[1]),f[2]);}
float opticaldensity(point b){
 vector p=vector(b[0],b[2],-b[1]);float c=cloudnoise(vector(p[0]*10,p[1]*7,p[2]*12));
 return .28+c*c*2.5+.4*cloudnoise(vector(p[0]*23,p[1]*17,p[2]*19));}
int findexit(''').replace('pos+=dir*distance;','float dens=0; for(int j=0;j<4;j++) dens+=opticaldensity(pos+dir*distance*(j+.5)/4); pos+=dir*distance; distance*=dens*.25;')
template=template.replace('texture(sharpfile,u,v,','texture(sharpfile,u,v,0.0,0.0,0.0,0.0,').replace('texture(tentfile,u,v,','texture(tentfile,u,v,0.0,0.0,0.0,0.0,')
for ob in (scene.objects['Upper_Ruby'],scene.objects['Lower_Ruby']):
    planes={}
    for poly in ob.data.polygons:
        n=poly.normal;d=n.dot(ob.data.vertices[poly.vertices[0]].co)
        planes[tuple(round(v,5) for v in (*n,d))]=(*n,d)
    planes=list(planes.values())
    material=bpy.data.materials.new(ob.name+' native optics');material.use_nodes=True
    tree=material.node_tree;tree.nodes.clear();surf=tree.nodes.new('ShaderNodeOutputMaterial')
    text=template.replace('PLANE_COUNT',str(len(planes))).replace('PLANE_VECTORS',','.join('vector(%.9f,%.9f,%.9f)'%n[:3] for n in planes)).replace('PLANE_OFFSETS',','.join('%.9f'%n[3] for n in planes))
    texture_dir=repo/'ruby_heart_gem_20261113/source'
    text=text.replace('DENSITY_VALUE',str(max(.5,min(8.,1./ob.dimensions.y)))).replace('SHARP_FILE',str(texture_dir/'studio_linear_mip1.exr')).replace('TENT_FILE',str(texture_dir/'studio_linear_mip8.exr'))
    osl=root/scene.get('candidate','candidate01')/(ob.name+'.osl');osl.write_text(text)
    script=tree.nodes.new('ShaderNodeScript');script.mode='EXTERNAL';script.filepath=str(osl);script.update()
    assert 'BSDF' in script.outputs,ob.name
    tree.links.new(script.outputs['BSDF'],surf.inputs['Surface']);ob.data.materials[0]=material
scene.render.filepath=str(root/scene.get('candidate','candidate01')/'optical_front.png')
bpy.ops.render.render(write_still=True)
