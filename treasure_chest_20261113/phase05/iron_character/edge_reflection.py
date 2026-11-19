import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector,Matrix

def add_edge_reflection(sc,D,power=100,neutral=False,side="top",ribbon=None,width=2.4,center=False,level=False):
 obj=sc.objects['Lab Chest Lower Rim'];me=obj.data;co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[co[:,0],co[:,2],-co[:,1]]@R;values=np.empty(len(me.vertices),np.float32);me.attributes['Damaged bevel facet wear'].data.foreach_get('value',values);V=(sc.camera.matrix_world.to_quaternion()@Vector((0,0,1))).normalized();front=Vector((math.sin(math.radians(32)),-math.cos(math.radians(32)),0));normal_matrix=obj.matrix_world.inverted().transposed().to_3x3();ids=np.flatnonzero((values>.20)&(q[:,2]>1.70)&(q[:,1]>-1.81)&(q[:,0]>-2.1)&(q[:,0]<-.35));
 if side=='bottom':ids=np.flatnonzero((q[:,2]>1.72)&(q[:,1]<-2.15)&(q[:,0]>-2.1)&(q[:,0]<-.35))
 ids=sorted(ids,key=lambda i:abs(float(q[i,0])+.68))
 chosen=None;deps=bpy.context.evaluated_depsgraph_get()
 for idx in ids[::max(1,len(ids)//150)]:
  v=me.vertices[int(idx)];P=obj.matrix_world@v.co;N=(normal_matrix@v.normal).normalized()
  if N.dot(V)<.08 or N.dot(front)<.15 or (N.z<.15 if side=='top' else N.z>-.10):continue
  L=(2*N.dot(V)*N-V).normalized()
  if (L.z<.20 if side=='top' else L.z>-.20) or L.dot(front)<.08:continue
  hit=sc.ray_cast(deps,P+N*.008+L*.008,L,distance=2.8 if side=='top' else .55)
  if hit[0]:continue
  chosen=(P,N,L,int(idx));break
 assert chosen,'No unoccluded existing bevel reflection found'
 P,N,L,idx=chosen
 if center:P=P+Vector((math.cos(math.radians(32)),math.sin(math.radians(32)),0))*(-float(q[idx,0]))
 data=bpy.data.lights.new('Iron bevel reflection','AREA');data.energy=power;data.color=(1,1,1) if neutral else (1,.62,.28);data.shape='RECTANGLE';data.size=width;data.size_y=ribbon if ribbon is not None else .20 if side=='top' else .12;light=bpy.data.objects.new('Iron bevel reflection',data);sc.collection.objects.link(light);light.location=P+L*(2.8 if side=='top' else .55);light.rotation_euler=(P-light.location).to_track_quat('-Z','Y').to_euler();
 if center:
  X=Vector((math.cos(math.radians(32)),math.sin(math.radians(32)),0));Z=(L-X*L.dot(X)).normalized() if level else L;X=X if level else (X-L*X.dot(L)).normalized();Y=Z.cross(X).normalized();light.rotation_euler=Matrix((X,Y,Z)).transposed().to_euler()
 data.diffuse_factor=0;data.specular_factor=1;receivers=bpy.data.collections.new('Iron reflection receivers')
 for name in ['Lab Chest Lower Rim','Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:receivers.objects.link(sc.objects[name])
 light.light_linking.receiver_collection=receivers
 result=dict(level=level,side=side,power=power,color=list(data.color),position=list(light.location),rotation=list(light.rotation_euler),size=data.size,size_y=data.size_y,target=list(P),normal=list(N),reflection_direction=list(L),sample_vertex=idx,receivers=[o.name for o in receivers.objects],diffuse_factor=data.diffuse_factor,specular_factor=data.specular_factor);(D/'lighting').mkdir(exist_ok=True);(D/'lighting'/(side+'_edge_'+str(power)+('_neutral' if neutral else '')+'.json')).write_text(json.dumps(result,indent=2));return light
