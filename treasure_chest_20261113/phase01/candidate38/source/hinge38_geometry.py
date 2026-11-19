import bpy,bmesh,numpy as np,math
from pathlib import Path
from mathutils import Matrix,Vector
Y38=np.array(Matrix.Rotation(math.radians(32),3,'Y'));AXIS_Y38=.36175;AXIS_Z38=-1.930

def world38(v):
 a=np.asarray(v)@Y38.T;return np.c_[a[:,0],-a[:,2],a[:,1]]

def local38(v):
 a=np.asarray(v);return np.c_[a[:,0],a[:,2],-a[:,1]]@Y38

def solid38(name,V,F,N,material,real=False):
 V=np.asarray(V,dtype=float);F=[list(f) for f in F];N=[list(n) for n in N]
 volume=0.
 for f in F:
  for j in range(1,len(f)-1):volume+=np.dot(V[f[0]],np.cross(V[f[j]],V[f[j+1]]))/6
 assert abs(volume)>1e-12,(name,'empty input')
 if volume<0:F=[f[::-1] for f in F];N=[n[::-1] for n in N]
 ob=bpy.context.scene.objects.get(name)
 if ob is None:
  me=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
 else:me=ob.data;me.clear_geometry()
 assert ob.parent is None and ob.animation_data is None,(name,'cannot reconstruct moving source')
 me.from_pydata(world38(V).tolist(),[],F);me.update();me.materials.clear();me.materials.append(material)
 flat=[]
 for f,n in zip(me.polygons,N):
  n=world38(np.asarray(n));n/=np.linalg.norm(n,axis=1)[:,None];flat.extend(n.tolist());f.use_smooth=bool(np.max(np.linalg.norm(n-n[0],axis=1))>1e-5)
 me.normals_split_custom_set(flat);ob.matrix_world=Matrix.Identity(4);ob['full_form']=real;ob['development_only']=not real;ob.hide_render=not real;ob.hide_set(not real);return ob

def ring38(name,cx,a,b,material):
 bevel=.003;profile=np.array([(a+bevel,.114,.120),(a,.111,.117),(a,.059,.059),(a+bevel,.055,.055),(b-bevel,.055,.055),(b,.059,.059),(b,.111,.117),(b-bevel,.114,.120)])
 V=[];F=[];N=[];K=64
 for x,ry,rz in profile:
  for j in range(K):u=2*math.pi*j/K;V.append([cx+x,AXIS_Y38+ry*math.cos(u),AXIS_Z38+rz*math.sin(u)])
 for k in range(len(profile)):
  nex=(k+1)%len(profile);delta=profile[nex]-profile[k]
  for j in range(K):
   ids=[k*K+j,k*K+(j+1)%K,nex*K+(j+1)%K,nex*K+j];normals=[]
   for vid in ids:
    row=vid//K;u=2*math.pi*(vid%K)/K;ry,rz=profile[row,1:];ds=np.array([delta[0],delta[1]*math.cos(u),delta[2]*math.sin(u)]);du=np.array([0,-ry*math.sin(u),rz*math.cos(u)]);n=np.cross(ds,du);n/=np.linalg.norm(n);normals.append(n)
   F.append(ids);N.append(normals)
 return solid38(name,V,F,N,material)

def cylinder38(name,cx,a,b,r,material):
 V=[];F=[];N=[];K=64
 for x in (a,b):
  for j in range(K):u=2*math.pi*j/K;V.append([cx+x,AXIS_Y38+r*math.cos(u),AXIS_Z38+r*math.sin(u)])
 F.extend([list(range(K-1,-1,-1)),list(range(K,2*K))]);N.extend([[[-1.,0,0]]*K,[[1.,0,0]]*K])
 for j in range(K):
  ids=[j,(j+1)%K,K+(j+1)%K,K+j];F.append(ids);N.append([[0,math.cos(2*math.pi*(i%K)/K),math.sin(2*math.pi*(i%K)/K)] for i in ids])
 return solid38(name,V,F,N,material)

def pin38(name,cx,material):
 profile=[(-.355,.075),(-.350,.080),(-.320,.080),(-.315,.075),(-.315,.050),(.315,.050),(.315,.075),(.320,.080),(.350,.080),(.355,.075)];K=64;V=[];F=[];N=[]
 for x,r in profile:
  for j in range(K):u=2*math.pi*j/K;V.append([cx+x,AXIS_Y38+r*math.cos(u),AXIS_Z38+r*math.sin(u)])
 F.append(list(range(K-1,-1,-1)));N.append([[-1.,0,0]]*K)
 for k in range(len(profile)-1):
  dx,dr=np.array(profile[k+1])-profile[k]
  for j in range(K):
   ids=[k*K+j,k*K+(j+1)%K,(k+1)*K+(j+1)%K,(k+1)*K+j];F.append(ids);normals=[]
   for vid in ids:
    u=2*math.pi*(vid%K)/K;n=np.array([-dr,dx*math.cos(u),dx*math.sin(u)]);n/=np.linalg.norm(n);normals.append(n)
   N.append(normals)
 F.append(list(range((len(profile)-1)*K,len(profile)*K)));N.append([[1.,0,0]]*K)
 return solid38(name,V,F,N,material,True)

def head38(name,cx,cy,material):
 # Backward facing dome, with a real neck seated inside its hinge plate.
 K=32;angles=np.linspace(0,math.pi/2,9)[:-1];profile=[(-1.895,.018),(-1.909,.018),(-1.909,.035)]+[(-1.909-.020*math.sin(t),.035*math.cos(t)) for t in angles[1:]];V=[];F=[];N=[]
 for z,r in profile:
  for j in range(K):u=2*math.pi*j/K;V.append([cx+r*math.cos(u),cy+r*math.sin(u),z])
 F.append(list(range(K)));N.append([[0,0,1.]]*K)
 for k in range(len(profile)-1):
  for j in range(K):
   ids=[k*K+j,(k+1)*K+j,(k+1)*K+(j+1)%K,k*K+(j+1)%K];normals=[]
   dz,dr=np.array(profile[k+1])-profile[k]
   for vid in ids:
    row=vid//K;u=2*math.pi*(vid%K)/K
    if k>=2:
     z,r=profile[row];n=np.array([math.cos(u)*r/(.035*.035),math.sin(u)*r/(.035*.035),(z+1.915)/(.020*.020)])
    else:n=np.array([-dz*math.cos(u),-dz*math.sin(u),dr])
    n/=np.linalg.norm(n);normals.append(n)
   F.append(ids);N.append(normals)
 tip=len(V);V.append([cx,cy,-1.929]);last=(len(profile)-1)*K
 for j in range(K):
  ids=[last+j,tip,last+(j+1)%K];F.append(ids);ns=[]
  for vid in ids:
   if vid==tip:ns.append([0,0,-1.]);continue
   q=np.array(V[vid])-[cx,cy,-1.909];n=q/np.array([.035**2,.035**2,.020**2]);n/=np.linalg.norm(n);ns.append(n)
  N.append(ns)
 return solid38(name,V,F,N,material,True)

def negative38(d):
 out=d.copy();out['t']=d['t'][:,[0,2,1]];out['tn']=-d['tn'][:,[0,2,1],:];return out

def boolean38(target,operand,operation):
 sc=bpy.context.scene;oldactive=bpy.context.view_layer.objects.active;selected=list(bpy.context.selected_objects)
 try:
  for o in selected:o.select_set(False)
  target.hide_set(False);operand.hide_set(False);target.select_set(True);bpy.context.view_layer.objects.active=target;bpy.context.view_layer.update();mod=target.modifiers.new('Actual hinge running seat38','BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=operand;bpy.ops.object.modifier_apply(modifier=mod.name);repairs=clean36(target.data);proof=topology36(target);return dict(operation=operation,operand=operand.name,repairs=repairs,**proof)
 finally:
  operand.hide_set(True);target.select_set(False)
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=oldactive
