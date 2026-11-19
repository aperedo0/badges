import bpy,sys,json,numpy as np,math
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;key=sys.argv[sys.argv.index('--')+1];C=D/key;C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(D/'E_layered/master.blend'));o=bpy.data.scenes['Test plank master'].objects['Lab Chest Lower Rim'];o.data=o.data.copy();
if 'hires' in key:
 for f in o.data.polygons:f.use_smooth=True
 bpy.context.view_layer.objects.active=o;modifier=o.modifiers.new('Resolved secondary displacement grid','SUBSURF');modifier.subdivision_type='SIMPLE';modifier.levels=1;bpy.ops.object.modifier_apply(modifier=modifier.name);o.data.update()
mat=o.data.materials[0].copy();mat.name='Forged iron '+key;o.data.materials[0]=mat;nt=mat.node_tree;old=nt.nodes['Calibrated forging height'];targets=[l.to_socket for l in list(old.outputs['Normal'].links)];uv=next(n for n in nt.nodes if n.type=='UVMAP' and n.uv_map=='LowerIronAtlas');F=D/('relief_planished' if 'planished' in key else 'relief_old' if 'old' in key else 'relief_battered')
def height(name,scale):
 im=bpy.data.images.load(str(F/name),check_existing=False);im.colorspace_settings.name='Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);b=nt.nodes.new('ShaderNodeBump');b.name=name+' independent strength';b.inputs['Strength'].default_value=1;b.inputs['Distance'].default_value=scale;nt.links.new(tex.outputs['Color'],b.inputs['Height']);return b
coarse=height('coarse16.png',.010);fine=height('fine16.png',.004);nt.links.new(coarse.outputs['Normal'],fine.inputs['Normal'])
for target in targets:nt.links.new(fine.outputs['Normal'],target)
if 'displaced' in key:
 me=o.data;co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());normal=np.empty_like(co);me.vertices.foreach_get('normal',normal.ravel());rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[co[:,0],co[:,2],-co[:,1]]@rot;nq=np.c_[normal[:,0],normal[:,2],-normal[:,1]]@rot;f=np.load(F/'fields.npz');h,w=f['coarse'].shape;u=np.where(abs(nq[:,2])>=abs(nq[:,0]),np.where(q[:,2]>=0,q[:,0]+2.73,9.02+2.73-q[:,0]),np.where(q[:,0]>=0,5.46+1.78-q[:,2],14.48+q[:,2]+1.78));xi=np.clip(u/18.04*(w-1),0,w-1);yi=np.clip((-.0-(q[:,1]+2.2175))/.5035*(h-1)+(h-1),0,h-1)
 def sample(a):
  x0=xi.astype(int);y0=yi.astype(int);x1=np.minimum(x0+1,w-1);y1=np.minimum(y0+1,h-1);tx=xi-x0;ty=yi-y0;return a[y0,x0]*(1-tx)*(1-ty)+a[y0,x1]*tx*(1-ty)+a[y1,x0]*(1-tx)*ty+a[y1,x1]*tx*ty
 outer=((q[:,2]>1.70)&(nq[:,2]>.5))|((q[:,2]<-1.70)&(nq[:,2]<-.5))|((q[:,0]>2.65)&(nq[:,0]>.5))|((q[:,0]<-2.65)&(nq[:,0]<-.5));delta=sample(f['coarse'])*outer;new=co+normal*delta[:,None];me.vertices.foreach_set('co',new.astype(np.float32).ravel());
 for face in me.polygons:face.use_smooth=True
 me.update();assert np.max(np.linalg.norm(new-co,axis=1))>1e-5;
 coarse.inputs['Strength'].default_value=0;np.savez_compressed(C/'displacement.npz',before=co,after=new,offset=delta);assert np.isfinite(new).all()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);(C/'design.json').write_text(json.dumps(dict(target=o.name,mesh=o.data.name,material=mat.name,medium_source=F.name,representation='Physical vertex displacement plus complementary fine bump' if 'displaced' in key else 'Separated coarse and fine bump',coarse_scale=.010,fine_scale=.004,geometry_original='displaced' not in key),indent=2));print('Saved independent relief',key,flush=True)
