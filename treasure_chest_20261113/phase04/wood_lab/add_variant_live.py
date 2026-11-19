import bpy,numpy as np,json,math
from pathlib import Path
from mathutils import Matrix
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');lab=bpy.data.scenes['Wood surface comparison'];key='D';folder='D_hybrid'
assert not lab.objects.get('Lab relief '+key)
mat=bpy.data.materials['Wood Lab B'].copy();mat.name='Wood Lab '+key
for role in ['albedo','roughness','normal']:
 im=bpy.data.images.load(str(P/folder/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();mat.node_tree.nodes['Single plank '+role].image=im
bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Anisotropic'].default_value=.12
body=lab.objects['Lab body B'].copy();body.data=body.data.copy();body.name='Lab body '+key;lab.collection.objects.link(body)
for i,m in enumerate(body.data.materials):
 if m.name=='Wood Lab B':body.data.materials[i]=mat
ob=lab.objects['Lab relief B'].copy();ob.data=ob.data.copy();ob.name='Lab relief '+key;lab.collection.objects.link(ob);ob.data.materials[0]=mat
W,H=ob['grid'];t=np.linspace(0,1,H);Y=np.broadcast_to((-2.1605000495910645+t*1.2980000376701355)[:,None],(H,W));half=2.49114990234375+(2.3499999046325684-2.49114990234375)*t;X=half[:,None]*np.linspace(-1,1,W)[None,:]
a=np.load(P/folder/'surface.npz')['height'];hh,ww=a.shape;u=np.clip((X+2.55)/5.1,0,1)*(ww-1);v=np.clip(1-(Y+2.2175)/1.3775,0,1)*(hh-1);ix=u.astype(int);iy=v.astype(int);fx=u-ix;fy=v-iy
z=a[iy,ix]*(1-fx)*(1-fy)+a[iy,np.minimum(ix+1,ww-1)]*fx*(1-fy)+a[np.minimum(iy+1,hh-1),ix]*(1-fx)*fy+a[np.minimum(iy+1,hh-1),np.minimum(ix+1,ww-1)]*fx*fy
edge=np.minimum.reduce([half[:,None]-abs(X),Y+2.1605000495910645,-.862500011920929-Y]);fade=np.clip(edge/.045,0,1);fade=fade*fade*(3-2*fade);z=z*fade+1.6
q=np.stack([X,Y,z],axis=2).reshape(-1,3)@np.array(Matrix.Rotation(math.radians(32),3,'Y')).T;q=np.c_[q[:,0],-q[:,2],q[:,1]];ob.data.vertices.foreach_set('co',q.ravel());ob.data.update();ob['depth_min']=float(z.min()-1.6)
body.hide_render=ob.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'comparisons.blend'),compress=True)
print('Added D hybrid; originals untouched')
