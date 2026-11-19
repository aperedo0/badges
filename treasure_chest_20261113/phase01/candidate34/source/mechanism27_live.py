assert 'Status: APPROVED (review round 1).' in (P/'mechanism27/PLAN.md').read_text()
exec(compile((P/'tools/mechanism26_live.py').read_text(),'mechanism26_live.py','exec'))
# The replacement tongue is one swept solid, with integral edge ridges.
upper=bezier4([[0,.39525,2.050],[0,.360,2.120],[0,.300,2.170],[0,.250,2.170]],20)
middle=np.c_[np.zeros(24),np.linspace(.250,-.06575,24),np.full(24,2.170)]
a=np.linspace(0,math.pi/2,32);bend=np.c_[np.zeros(len(a)),-.06575-.08075*np.sin(a),2.085+.085*np.cos(a)]
ret=np.c_[np.zeros(20),np.full(20,-.1465),np.linspace(2.085,1.900,20)]
curve27=np.vstack([upper,middle[1:],bend[1:],ret[1:]])
length27=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve27,axis=0),axis=1))];tangent=np.gradient(curve27,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];out27=np.cross(tangent,[1,0,0]);out27/=np.linalg.norm(out27,axis=1)[:,None]
profile27=np.array([[-.2155,-.055],[.2155,-.055],[.2275,-.043],[.2275,.043],[.2215,.057],[.2185,.070],[.1985,.070],[.1955,.057],[.1905,.055],[-.1905,.055],[-.1955,.057],[-.1985,.070],[-.2185,.070],[-.2215,.057],[-.2275,.043],[-.2275,-.043]])
V=[];F=[];K27=len(profile27);rows27=len(curve27)
for i,(p,n) in enumerate(zip(curve27,out27)):
 blend=np.clip((length27[-1]-length27[i])/(length27[-1]*.25),0,1);blend=blend*blend*(3-2*blend)
 for x,z in profile27:
  if z>.055:z=.055+(z-.055)*blend
  V.append(p+np.array([x,0,0])+n*z)
for i in range(rows27-1):
 for k in range(K27):F.append([i*K27+k,i*K27+(k+1)%K27,(i+1)*K27+(k+1)%K27,(i+1)*K27+k])
F.extend([list(range(K27-1,-1,-1)),list(range((rows27-1)*K27,rows27*K27))])
ob=solid('Chest Curved Hasp Tongue',V,F,hardware,0,[True]*(len(F)-2)+[False,False]);ob['allowed_euler']=[2];me=ob.data;me.update();long_count=(rows27-1)*K27;normal27=[]
for face in me.polygons:
 for li in face.loop_indices:
  if face.index>=long_count:normal27.append(tuple(face.normal));continue
  k=face.index%K27;row=me.loops[li].vertex_index//K27;nn=Vector((0,0,0))
  for rr in [row-1,row]:
   if 0<=rr<rows27-1:nn+=me.polygons[rr*K27+k].normal
  nn.normalize();normal27.append(tuple(nn))
me.normals_split_custom_set(normal27);me.calc_loop_triangles();sv=np.array([v.co[:] for v in me.vertices]);st=[];sn=[]
for tri in me.loop_triangles:
 xyz=sv[list(tri.vertices)]
 if np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2>1e-10:
  st.append(list(tri.vertices));sn.append([me.corner_normals[i].vector[:] for i in tri.loops])
source_tree27=BVHTree.FromPolygons(sv.tolist(),st,all_triangles=True,epsilon=1e-8);st=np.array(st);sn=np.array(sn)
clean_new(ob)
cut25(ob,cylinder25('New lower root pin clearance',(0,.48525,2),.086,.800),'New lower root pin clearance',[2,0])
cut25(ob,cylinder25('New integral tongue retaining bore',(0,-.1465,1.970),.032,.800),'New integral tongue actual retaining bore',[0,-2])
# Restore smooth longitudinal normals after Boolean rewriting; bore walls stay inward.
me=ob.data;me.update();local=coords25(ob);nn=[];bore_faces=0
for face in me.polygons:
 coords=local[list(face.vertices)];bore=None
 for cy,cz,rad in [(.48525,2.,.086),(-.1465,1.970,.032)]:
  if np.max(abs(np.linalg.norm(coords[:,1:]-[cy,cz],axis=1)-rad))<.00002:bore=(cy,cz);break
 if bore is not None:
  bore_faces+=1
  for li in face.loop_indices:
   q=local[me.loops[li].vertex_index];n=yaw@Vector((0,bore[0]-q[1],bore[1]-q[2])).normalized();nn.append((n.x,-n.z,n.y))
 else:
  loc,n,idx,d=source_tree27.find_nearest(face.center);assert idx is not None
  a,b,c=sv[st[idx]];e0=b-a;e1=c-a;d00=np.dot(e0,e0);d01=np.dot(e0,e1);d11=np.dot(e1,e1);den=d00*d11-d01*d01;assert abs(den)>1e-18
  for li in face.loop_indices:
   p=np.array(me.vertices[me.loops[li].vertex_index].co)-a;u=(d11*np.dot(p,e0)-d01*np.dot(p,e1))/den;v=(d00*np.dot(p,e1)-d01*np.dot(p,e0))/den;w=np.clip([1-u-v,u,v],0,1);w/=w.sum();n=w@sn[idx];n/=np.linalg.norm(n);nn.append(tuple(n))
me.normals_split_custom_set(nn);prove_part(ob,'Integral ridged latch final')
for name in ['Chest Hasp Edge Rail -1','Chest Hasp Edge Rail 1']:hide_part(sc.objects[name])
parts=json.loads((C/'mechanism_parts.json').read_text());parts.update(moving_hasp=['Chest Front Hasp Barrel','Chest Curved Hasp Tongue'],stage='Visible sleeve and integral strap saved; continuous release proof pending');(C/'mechanism_parts.json').write_text(json.dumps(parts,indent=2))
(C/'integral_strap.json').write_text(json.dumps(dict(rows=rows27,profile_vertices=K27,integral_ridges=True,old_separate_rails_hidden=True,bore_wall_faces=bore_faces,normal_reconstruction_after_cuts=True,actual_euler_proof=proof[-5:]),indent=2))
if not globals().get('DEFER_CHEST_SAVE',False):bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved exposed center sleeve and single integral ridged strap with final bore and longitudinal normals.')
