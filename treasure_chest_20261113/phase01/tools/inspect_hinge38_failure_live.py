import bpy,numpy as np,json
out=[]
for name in ('Chest Rear Hinge Lower -1','Chest Upper Lid Rim'):
 ob=bpy.data.objects[name];m=ob.data;m.calc_loop_triangles();v=np.array([a.co[:] for a in m.vertices]);t=np.array([a.vertices[:] for a in m.loop_triangles]);tri=v[t];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;inds=np.where(area<1e-10)[0];out.append(dict(name=name,small=[dict(area=float(area[i]),vertices=tri[i].tolist(),lengths=np.linalg.norm(tri[i]-np.roll(tri[i],1,axis=0),axis=1).tolist()) for i in inds][:6]))
print(json.dumps(out))
