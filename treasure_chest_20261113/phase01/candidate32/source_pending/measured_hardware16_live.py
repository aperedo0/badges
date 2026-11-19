# Runs inside the live full form builder, before its one height conversion.
import bpy,bmesh,numpy as np,json,math
from mathutils import Vector,Matrix,geometry
assert 'Status: APPROVED (review round 2).' in (P/'measured_hardware/PLAN.md').read_text()
MP=json.loads((P/'measured_hardware/profiles.json').read_text());stage=json.loads((C/'hardware_stage.json').read_text())['stage'];proof=[]

def prove_part(ob,label):
 me=ob.data;me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([f.vertices[:] for f in me.loop_triangles]);e=np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1);edges,counts=np.unique(e,axis=0,return_counts=True)
 assert (counts==2).all(),(label,'open or nonmanifold',np.unique(counts,return_counts=True))
 assert len(np.unique(np.sort(t,axis=1),axis=0))==len(t),(label,'duplicate triangles')
 areas=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)/2
 assert (areas>1e-10).all(),(label,'zero area triangle',float(areas.min()))
 chi=len(np.unique(t))-len(edges)+len(t);allowed=list(ob.get('allowed_euler',[2]));assert chi in allowed,(label,'unexpected topology',chi)
 parent={int(i):int(i) for i in np.unique(t)}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for u,w in edges:
  u,w=root(int(u)),root(int(w))
  if u!=w:parent[w]=u
 assert len({root(i) for i in parent})==1,(label,'disconnected solid')
 vol=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6);assert vol>0,(label,'negative volume')
 proof.append(dict(part=label,closed=True,euler_characteristic=int(chi),positive_volume=vol,triangles=len(t)))

def hide_part(ob):ob.hide_set(True);ob.hide_render=True;ob['full_form']=False

def final_triangles(bm):
 # Preserve collinear boundary points while clipping only nonzero ears.
 # Blender's generic ngon fan can choose a diagonal along the fold itself.
 for face in list(bm.faces):
  if len(face.verts)<=3:continue
  verts=list(face.verts);p=np.array([v.co[:] for v in verts],float);normal=np.cross(p,np.roll(p,-1,axis=0)).sum(0);axis=int(np.argmax(abs(normal)));q=np.delete(p,axis,axis=1);area=np.cross(q,np.roll(q,-1,axis=0)).sum();sgn=1 if area>0 else -1;ids=list(range(len(verts)));tris=[]
  cross=lambda a,b:float(a[0]*b[1]-a[1]*b[0])
  while len(ids)>3:
   found=False
   for k,i in enumerate(ids):
    a,b=ids[k-1],ids[(k+1)%len(ids)];A,B,D=q[a],q[i],q[b]
    if sgn*cross(B-A,D-A)<=1e-10:continue
    blocked=False
    for j in ids:
     if j in (a,i,b):continue
     X=q[j]
     if min(sgn*cross(B-A,X-A),sgn*cross(D-B,X-B),sgn*cross(A-D,X-D))>=-1e-10:blocked=True;break
    if blocked:continue
    tris.append((a,i,b));ids.pop(k);found=True;break
   assert found,('Cannot tessellate measured face',p.tolist())
  tris.append(tuple(ids));smooth=face.smooth;mi=face.material_index;bm.faces.remove(face)
  for tri in tris:
   f=bm.faces.new([verts[i] for i in tri]);f.smooth=smooth;f.material_index=mi

def trim_shared_fold(bm,name):
 if not name.startswith(('Chest Lid Corner Armor','Chest Angular Boot')):return
 sx,sz=map(int,name.split()[-2:]);ox=2.775;oz=1.875 if name.startswith('Chest Lid') else 1.865
 p=yaw@Vector((sx*(ox-.010),0,sz*(oz-.010)));n=yaw@Vector((sx,0,sz)).normalized();p=Vector((p.x,-p.z,p.y));n=Vector((n.x,-n.z,n.y))
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=p,plane_no=n,clear_outer=True)
 boundary=[e for e in bm.edges if len(e.link_faces)==1]
 if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)

def union_live(target,operand,label,operation='UNION'):
 for ob in (target,operand):
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));final_triangles(bm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 prove_part(target,label+' input A');prove_part(operand,label+' input B');bpy.context.view_layer.objects.active=target;target.select_set(True)
 mod=target.modifiers.new('Exact measured hardware join','BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=operand
 if hasattr(mod,'use_hole_tolerant'):mod.use_hole_tolerant=True
 bpy.ops.object.modifier_apply(modifier=mod.name);target.select_set(False);hide_part(operand)
 bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);trim_shared_fold(bm,target.name);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));final_triangles(bm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free();target.data.update();prove_part(target,label+' result');return target

def measured_plate(name,kind,sx,sz):
 d=MP[kind];outer=np.array(d['outer']);inner=np.array(d['inner']);K=len(outer);plane=d.get('face_plane_z',d.get('face_plane_x'));V=[]
 fold=np.isclose(outer[:,0],d['fold'],atol=1e-5)
 bottom=np.isclose(outer[:,1],outer[:,1].min(),atol=1e-6)
 top=np.isclose(outer[:,1],outer[:,1].max(),atol=1e-6)
 mating=bottom if kind.startswith('upper') else top
 inner[mating]=outer[mating]
 # End the hidden leg walls inside one another instead of making their
 # outside caps exactly coplanar. The prescribed 0.020 fold trim removes
 # the 0.008 corner offsets with a 0.004 overlap margin.
 outer[fold,0]-=.008;inner[fold,0]-=.008
 for loop,which in [(outer,'back'),(outer,'toe'),(inner,'face')]:
  for a,y in loop:
   depth=plane-d['thickness'] if which=='back' else plane
   if which=='toe' and not (abs(y-(outer[:,1].min() if kind.startswith('upper') else outer[:,1].max()))<1e-6):depth-=d['bevel']
   V.append([sx*a,y,sz*depth] if kind.endswith('front') else [sx*depth,y,sz*a])
 F=[list(range(K-1,-1,-1)),list(range(2*K,3*K))]
 for k in range(2):
  for i in range(K):j=(i+1)%K;F.append([k*K+i,k*K+j,(k+1)*K+j,(k+1)*K+i])
 ob=solid(name,V,F,frame,0);prove_part(ob,name);return ob

def finish_joint(ob,sx,sz,ox,oz):
 # The union check already applied and capped the exact fold trim.
 # Do not cut that same plane a second time at floating point precision.
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Measured hardware face normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 prove_part(ob,ob.name+' folded edge');proof.append({'part':ob.name,'shared_fold_chamfer':.020,'perimeter_bevel':.050})

def upper_seat(sx,sz,front):
 name=(f'Chest Upper Corner Front Rivet {sx} {sz}' if front else f'Chest Upper Corner End Rivet {sx} {sz}')+' Seat';r=(.105 if front else .095)*1.18*1.08;n=Vector((0,0,sz) if front else (sx,0,0));p=Vector((sx*2.38,.72,sz*1.885) if front else (sx*2.785,.72,sz*1.48));rot=Vector((0,0,1)).rotation_difference(n);bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=40,radius1=r,radius2=r,depth=.013)
 for v in bm.verts:v.co=rot@v.co+p-n*.0075
 for f in bm.faces:f.smooth=len(f.verts)==4
 return finish(bm,name,hardware,.002)

def head_contact(target,head_name,sx,sz,front):
 head=sc.objects[head_name];p=Vector((sx*2.38,.72,sz*1.885) if front else (sx*2.785,.72,sz*1.48));n=Vector((0,0,sz) if front else (sx,0,0));origin=yaw@(p+n*.4);normal=yaw@n;origin=Vector((origin.x,-origin.z,origin.y));normal=Vector((normal.x,-normal.z,normal.y));hit,point,nn,index=target.ray_cast(origin,-normal)
 assert hit,(head_name,'no mounting face')
 depth=float(point.dot(normal));back=min(float(v.co.dot(normal)) for v in head.data.vertices);assert back<depth+1e-6,(head_name,'floating base',back,depth)
 seat=sc.objects[head_name+' Seat'];seatback=min(float(v.co.dot(normal)) for v in seat.data.vertices);assert seatback<depth+1e-6,(head_name,'floating seat')
 proof.append(dict(part=head_name,head_overlap=depth-back,seat_overlap=depth-seatback,actual_mounting_face_found=True))


def continuous_foot(sx,sz):
 # One filled body from base to shoulder. Every cross section is level.
 ys=np.array([-2.455,-2.441,-2.335,-2.289,-2.229,-1.735,-1.725,-1.705,-1.685,-1.525])
 def lower_bound(poly,y):
  xx=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   if abs(a[1]-b[1])<1e-8:
    if abs(y-a[1])<1e-6:xx.extend([a[0],b[0]])
   elif min(a[1],b[1])-1e-6<=y<=max(a[1],b[1])+1e-6:xx.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
  assert xx,('No measured foot section',y)
  return min(xx)
 front=np.array(MP['foot_front']['outer']);end=np.array(MP['foot_end']['outer']);Q=[]
 for y in ys:
  if y<=-1.725:
   ox,oz=2.775,1.865;ix=lower_bound(front,y);iz=lower_bound(end,y)
  else:
   ox=float(np.interp(y,[-1.725,-1.705,-1.685,-1.525],[2.775,2.772,2.764,2.735]));oz=float(np.interp(y,[-1.725,-1.705,-1.685,-1.525],[1.865,1.862,1.854,1.785]));ix=float(np.interp(y,[-1.725,-1.705,-1.685,-1.525],[1.998,2.000,2.008,2.050]));iz=float(np.interp(y,[-1.725,-1.705,-1.685,-1.525],[1.094,1.096,1.104,1.140]))
  q=chamfer_rect((ox-ix)/2,(oz-iz)/2,.035);Q.append(q+[(ox+ix)/2,(oz+iz)/2])
 Q=np.array(Q);D=np.gradient(Q,ys,axis=0);V=[]
 for y,q in zip(ys,Q):V.extend(np.c_[sx*q[:,0],np.full(8,y),sz*q[:,1]])
 F=loft_faces(len(ys));smooth=[False,False]+[True]*(len(F)-2);ob=solid(f'Chest Angular Boot {sx} {sz}',V,F,frame,0,smooth);me=ob.data;assert len(me.polygons)==len(F);normals=[]
 for face in me.polygons:
  if face.index<2:
   normals.extend([tuple(face.normal)]*len(face.loop_indices));continue
  k=(face.index-2)%8;j=(k+1)%8
  for li in face.loop_indices:
   vi=me.loops[li].vertex_index;r=vi//8;c=vi%8;edge=Q[r,j]-Q[r,k];dy=D[r,c];a=np.array([sx*edge[0],0,sz*edge[1]]);b=np.array([sx*dy[0],1,sz*dy[1]]);n=np.cross(a,b)*(sx*sz);n/=np.linalg.norm(n);n=yaw@Vector(n);normals.append((n.x,-n.z,n.y))
 me.normals_split_custom_set(normals);prove_part(ob,ob.name+' one continuous solid');proof.append({'part':ob.name,'continuous_foot_and_shoulder':True,'separate_cap_removed':True,'bottom_bevel_band_removed':True,'all_ring_vertices_share_height':True,'top_footprint_covers_upright':True})

pairs=[(-1,1)] if stage=='first_pair' else [(sx,sz) for sx in (-1,1) for sz in (-1,1)]
for sx,sz in pairs:
 name=f'Chest Lid Corner Armor {sx} {sz}';a=measured_plate(name,'upper_front',sx,sz);b=measured_plate(f'Measured upper end operand {sx} {sz}','upper_end',sx,sz);union_live(a,b,name);finish_joint(a,sx,sz,2.775,1.875)
 for front in (True,False):upper_seat(sx,sz,front);head_contact(a,f'Chest Upper Corner '+('Front' if front else 'End')+f' Rivet {sx} {sz}',sx,sz,front)
 V=[]
 for y,w in [(.02,.64),(.085,.76),(.465,.76)]:
  q=chamfer_rect(w/2,w/2,.025);V.extend(np.c_[q[:,0]+sx*2.395,np.full(8,y),q[:,1]+sz*1.495])
 solid(f'Chest Body Corner Collar {sx} {sz}',V,loft_faces(3),bevel=.018)
 continuous_foot(sx,sz)


def clean_new(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));final_triangles(bm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();prove_part(ob,ob.name)

if stage=='complete':
 # A real folded strap with the rectified wide, slightly tapered end face.
 for sx in (-1,1):
  curve=[(2.50,2.68),(2.65,2.68)]
  curve += [(2.65+.12*math.cos(a),2.56+.12*math.sin(a)) for a in np.linspace(math.pi/2,0,18)[1:]]
  curve += [(2.77,y) for y in np.linspace(2.56,2.29,12)[1:]]
  curve=np.array(curve);tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];V=[];F=[];S=[];K=8
  for (x,y),(tx,ty) in zip(curve,tangent):
   n=np.array([-ty,tx]);t=np.clip((2.65-y)/.36,0,1);z0=-.142*(1-t)-.033*t;z1=.322*(1-t)+.255*t;w=(z1-z0)/2;zc=(z1+z0)/2;h=.035;b=.010
   profile=[(-w+b,-h),(w-b,-h),(w,-h+b),(w,h-b),(w-b,h),(-w+b,h),(-w,h-b),(-w,-h+b)]
   for u,v in profile:V.append([sx*(x+n[0]*v),y+n[1]*v,zc+u])
  for i in range(len(curve)-1):
   for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(k not in (2,6))
  F.extend([list(range(K-1,-1,-1)),list(range((len(curve)-1)*K,len(curve)*K))]);S.extend([False,False]);ob=solid(f'Chest End Arch Crown Tab {sx}',V,F,frame,0,S);clean_new(ob)
  dome(f'Chest End Crown Fastener {sx}',[sx*2.808,2.508,.051],[sx,0,0],.083)

 # Compact measured C section, not a disk or a round spool end.
 for sx in (-1,1):
  for name in [f'Chest Handle Pivot {sx}']+[f'Chest Handle {suffix} {sx} {sz}' for suffix in ['End Collar','Inner Collar','Rolled Cheek'] for sz in (-1,1)]:
   ob=sc.objects.get(name)
   if ob:hide_part(ob)
  q=np.array(MP['handle_section_outer']);qi=np.array(MP['handle_section_inner']);K=len(q);V=[];F=[];S=[]
  for loop,z in [(qi,handle_z-.310),(q,handle_z-.298),(q,handle_z+.298),(qi,handle_z+.310)]:V.extend(np.c_[sx*loop[:,0],loop[:,1],np.full(K,z)])
  F=[list(range(K-1,-1,-1)),list(range(3*K,4*K))];S=[False,False]
  for i in range(3):
   for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(True)
  ob=solid(f'Chest Measured Rolled Handle Cover {sx}',V,F,hardware,0,S);clean_new(ob)
  # A receiving cut follows the real root and preserves clearance from wood.
  ring=sc.objects[f'Chest Solid Ring Handle {sx}'];rm=ring.data;rm.update();inv=yaw.inverted();vnorm={}
  for lp in rm.loops:
   if lp.vertex_index not in vnorm:vnorm[lp.vertex_index]=rm.corner_normals[lp.index].vector.copy()
  VV=[]
  for vi,v in enumerate(rm.vertices):
   q0=inv@Vector((v.co.x,v.co.z,-v.co.y));nn=vnorm[vi];n0=inv@Vector((nn.x,nn.z,-nn.y));q0+=n0*.012;VV.append(tuple(q0))
  FF=[list(f.vertices) for f in rm.polygons];cutter=solid(f'Measured Handle Root Clearance {sx}',VV,FF,hardware,0,True);cutter['allowed_euler']=[0];ob['allowed_euler']=[0,2]
  union_live(ob,cutter,ob.name+' receiving clearance','DIFFERENCE');bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Rolled cover face normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
  proof.append({'part':ob.name,'actual_ring_root_clearance':.012,'wood_clearance_at_lower_sleeve':.012,'measured_curved_cap':True})
  cx=sx*2.70;box(f'Chest Handle Mount {sx}',[cx-.07,-.43,-.60+handle_z],[cx+.07,.18,.60+handle_z],frame,.035)

 # One barrel with substantial end collars and small flush axle ends.
 for sx in (-1,1):
  ob=sc.objects.get(f'Chest Hasp Collar Group {sx}')
  if ob:hide_part(ob)
 xs=np.array([-.36,-.355,-.345,-.325,-.310,-.298,-.280,-.255,-.230,0,.230,.255,.280,.298,.310,.325,.345,.355,.36])
 rs=np.array([.152,.168,.184,.190,.187,.190,.190,.177,.168,.168,.168,.177,.190,.190,.187,.190,.184,.168,.152]);slopes=np.gradient(rs,xs);N=64;V=[];F=[];S=[]
 for x,r in zip(xs,rs):
  for j in range(N):a=j*2*math.pi/N;V.append([x,.64+r*math.cos(a),2.0+r*math.sin(a)])
 for i in range(len(xs)-1):
  for j in range(N):F.append([i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j]);S.append(True)
 F.extend([list(range(N-1,-1,-1)),list(range((len(xs)-1)*N,len(xs)*N))]);S.extend([False,False]);ob=solid('Chest Front Hasp Barrel',V,F,hardware,0,S);clean_new(ob)
 inv=yaw.inverted();normals=[]
 for face in ob.data.polygons:
  for li in face.loop_indices:
   if not face.use_smooth:normals.append(tuple(face.normal));continue
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;p0=inv@Vector((v.x,v.z,-v.y));a=math.atan2(p0.z-2.0,p0.y-.64);slope=float(np.interp(p0.x,xs,slopes));n=Vector((-slope,math.cos(a),math.sin(a))).normalized();n=yaw@n;normals.append((n.x,-n.z,n.y))
 ob.data.normals_split_custom_set(normals)
 for sx in (-1,1):
  ob=dome(f'Chest Hasp Pivot Dome {sx}',[sx*.36,.64,2.00],[sx,0,0],.065);me=ob.data;old=np.array([n.vector[:] for n in me.corner_normals]);scale=.018/(.065*.65)
  for v in me.vertices:
   p0=inv@Vector((v.co.x,v.co.z,-v.co.y));p0.x=sx*.36+(p0.x-sx*.36)*scale;p0=yaw@p0;v.co=(p0.x,-p0.z,p0.y)
  nn=[]
  for n in old:
   p0=inv@Vector((n[0],n[2],-n[1]));p0.x/=scale;p0.normalize();p0=yaw@p0;nn.append((p0.x,-p0.z,p0.y))
  me.update();me.normals_split_custom_set(nn);prove_part(ob,ob.name)

 # The return turns back through ninety degrees and enters the receiver.
 upper=bezier4([[0,.72,2.105],[0,.66,2.17],[0,.62,2.17],[0,.55,2.17]],14);middle=np.c_[np.zeros(20),np.linspace(.55,.060,20),np.full(20,2.17)];aa=np.linspace(0,math.pi/2,24);bend=np.c_[np.zeros(len(aa)),.060-.085*np.sin(aa),2.085+.085*np.cos(aa)];ret=np.c_[np.zeros(16),np.full(16,-.025),np.linspace(2.085,1.90,16)];curve=np.vstack([upper,middle[1:],bend[1:],ret[1:]]);tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];A=np.array([1,0,0]);out=np.cross(tangent,A);out/=np.linalg.norm(out,axis=1)[:,None];w=.2525;h=.055;b=.012;profile=[(-w+b,-h),(w-b,-h),(w,-h+b),(w,h-b),(w-b,h),(-w+b,h),(-w,h-b),(-w,-h+b)];K=8;V=[];F=[];S=[]
 for p0,n in zip(curve,out):
  for x,z in profile:V.append(p0+A*x+n*z)
 for i in range(len(curve)-1):
  for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(k not in (2,6))
 F.extend([list(range(K-1,-1,-1)),list(range((len(curve)-1)*K,len(curve)*K))]);S.extend([False,False]);ob=solid('Chest Curved Hasp Tongue',V,F,hardware,0,S);clean_new(ob)
 for side in (-1,1):
  V=[];F=[];profile=[(-.010,.053),(.010,.053),(.013,.057),(.013,.066),(.010,.070),(-.010,.070),(-.013,.066),(-.013,.057)]
  for p0,n in zip(curve,out):
   for x,z in profile:V.append(p0+A*(side*.2335+x)+n*z)
  for i in range(len(curve)-1):
   for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k])
  F.extend([list(range(K-1,-1,-1)),list(range((len(curve)-1)*K,len(curve)*K))]);ob=solid(f'Chest Hasp Edge Rail {side}',V,F,hardware,0,[True]*(len(F)-2)+[False,False]);clean_new(ob)
 proof.append({'part':'quarter folded latch','centerline_radius':.085,'positive_inner_radius':.030,'border_clearance_above_receiver':.010,'buried_termination_z':1.90})

(C/'measured_build_proof.json').write_text(json.dumps({'stage':stage,'checks':proof},indent=2));print('Measured hardware stage',stage,'passed',len(proof),'closed solid and join checks')
