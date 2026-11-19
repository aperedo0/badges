import bpy,numpy as np,json,sys
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');sc=bpy.context.scene;ob=sc.objects['Ruby Heart gem'];script=next(n for n in ob.data.materials[0].node_tree.nodes if n.bl_idname=='ShaderNodeScript')
s=(R/'optics/ruby_foil.osl').read_text();s=s.replace('output closure color BSDF=0){','int Probe=0,output closure color BSDF=0){')
s=s.replace('float f=fresnelshare(dot(n,-incident),1,1.77);','''if(Probe<5){color val=color(0);if(Probe==0)val=color(incident)*.5+.5;if(Probe==1)val=color(n)*.5+.5;if(Probe==2)val=color(reflect(incident,n))*.5+.5;if(Probe==3)val=lookup(reflect(incident,n),Mip1)/24;if(Probe==4)val=lookup(normalize(vector(-.773,.497,.393)),Mip1)/24;BSDF=emission()*val;return;} float f=fresnelshare(dot(n,-incident),1,1.77);''')
p=R/'optics/probe_variables.osl';p.write_text(s);script.filepath=str(p);script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
sc.cycles.samples=1;sc.cycles.use_denoising=False;sc.render.image_settings.file_format='OPEN_EXR';sc.render.image_settings.color_depth='32'
# Center of an actual upper left facet, projected through the measured native camera.
point=np.array([-1.70507401,1.80190836,.47248688]);eye=np.array([0,1.8,23]);forward=np.array([0,-2.35,-23]);forward/=np.linalg.norm(forward);up=np.cross([1,0,0],forward);up/=np.linalg.norm(up);v=point-eye;depth=v@forward;x=int(603+v[0]/depth*1762.5-300);y=int(633.3-(v@up)/depth*1762.5-300)
results={}
for mode in range(5):
 script.inputs['Probe'].default_value=mode;sc.render.filepath=str(R/'optics'/f'probe_{mode}.exr');bpy.ops.render.render(write_still=True)
 im=bpy.data.images.load(sc.render.filepath,check_existing=False);w,h=im.size;arr=np.array(im.pixels[:]).reshape(h,w,4);results[str(mode)]=arr[h-1-y,x,:3].tolist()
(R/'optics/probes.json').write_text(json.dumps(dict(pixel=[x,y],samples=results),indent=2));print('PROBES',results)
script.filepath=str(R/'optics/ruby_foil.osl');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
sc.cycles.samples=64;sc.cycles.use_denoising=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_depth='8'
