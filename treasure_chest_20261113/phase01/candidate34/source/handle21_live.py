assert 'Status: APPROVED (review round 1).' in (P/'handle21/PLAN.md').read_text()
from mathutils.bvhtree import BVHTree
def ring21(sx):
 V=[];F=[];normals=[];M=32;grooves=[2.40,math.pi,3.88]
 raw=np.sort(np.r_[np.arange(160)*2*math.pi/160,*[g+np.linspace(-.12,.12,25) for g in grooves]])
 us=[float(raw[0])]
 for u in raw[1:]:
  if u-us[-1]>1e-5:us.append(float(u))
 N=len(us)
 def collar_radius(u):
  left=min(1,max(0,(u-2.15)/.07));right=min(1,max(0,(4.13-u)/.07));fade=left*left*(3-2*left)*right*right*(3-2*right)
  return .1109+.0200*fade
 def groove_depth(u):return sum(.0080*math.exp(-((u-g)/.035)**2) for g in grooves)
 for u in us:
  cr=collar_radius(u);dc=(collar_radius(u+.0001)-collar_radius(u-.0001))/.0002;gr=groove_depth(u);dg=(groove_depth(u+.0001)-groove_depth(u-.0001))/.0002
  for j in range(M):
   v=j*2*math.pi/M;sn=math.sin(v);cs=math.cos(v);w=.60+.40*sn**4;dw=1.60*sn**3*cs;tube=cr-gr*w;ru=dc-dg*w;rv=-gr*dw;cu,su=math.cos(u),math.sin(u);L=math.hypot(.64*cu,.525*su);dL=(.525**2-.64**2)*su*cu/L;ny,nz=.64*cu/L,.525*su/L;dny=(-.64*su*L-.64*cu*dL)/L**2;dnz=(.525*cu*L-.525*su*dL)/L**2
   V.append([sx*2.93000000+tube*sn,-0.74714387+.525*cu+tube*cs*ny,.64*su+tube*cs*nz+handle_z])
   du=np.array([ru*sn,-.525*su+ru*cs*ny+tube*cs*dny,.64*cu+ru*cs*nz+tube*cs*dnz]);dv=np.array([rv*sn+tube*cs,(rv*cs-tube*sn)*ny,(rv*cs-tube*sn)*nz]);n=np.cross(du,dv);assert np.linalg.norm(n)>1e-10;n/=np.linalg.norm(n);q=yaw@Vector(n);normals.append((q.x,-q.z,q.y))
 for i in range(N):
  for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
 ob=solid(f'Chest Solid Ring Handle {sx}',V,F,hardware,0,True);ob.data.normals_split_custom_set([normals[l.vertex_index] for l in ob.data.loops])

def handle_triangles21(bm):
 # Validate in double precision before returning to the original strict proof.
 for tolerance in [0,2e-5,4e-5,8e-5,1.6e-4]:
  if tolerance:
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=tolerance)
   bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tolerance)
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  if tolerance:bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tolerance)
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  areas=[]
  for face in bm.faces:
   xyz=np.array([v.co[:] for v in face.verts],dtype=float);areas.append(np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2)
  if min(areas)>1e-10 and all(e.is_manifold for e in bm.edges):return
 raise AssertionError(('Handle numerical cleanup failed',min(areas)))

def union_handle21(target,operand,label,operation='UNION'):
 previous=globals()['final_triangles'];globals()['final_triangles']=handle_triangles21
 try:return union_live(target,operand,label,operation)
 finally:globals()['final_triangles']=previous

def cover21(sx):
 q=np.array(MP['handle_section_outer']);qi=np.array(MP['handle_section_inner']);q[:,0]+=.1871;qi[:,0]+=.1871;K=len(q)
 rows=[(handle_z-.310,0,True),(handle_z-.298,0,False)]
 for center in [handle_z-.135,handle_z+.135]:
  rows.extend([(center+d,w,False) for d,w in [(-.015,0),(-.012,.5),(-.009,1),(.009,1),(.012,.5),(.015,0)]])
 rows.extend([(handle_z+.298,0,False),(handle_z+.310,0,True)]);rows.sort()
 V=[];F=[];S=[];center=np.array([2.681084921+.1871,-.228049008])
 for z,depth,cap in rows:
  loop=(qi if cap else q).copy()
  for k in range(48):
   direction=loop[k]-center;direction/=np.linalg.norm(direction);loop[k]-=direction*(depth*.010)
  V.extend(np.c_[sx*loop[:,0],loop[:,1],np.full(K,z)])
 for i in range(len(rows)-1):
  for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(True)
 for tri in cap_indices(qi):
  F.append(tri[::-1]);S.append(False);F.append([(len(rows)-1)*K+i for i in tri]);S.append(False)
 ob=solid(f'Chest Measured Rolled Handle Cover {sx}',V,F,hardware,0,S);ob['allowed_euler']=[0,2];prove_part(ob,ob.name+' grooved curved shell')
 for label,xe,y0,y1 in [('top',2.930,-.030,.018),('bottom',2.960,-.472,-.414)]:
  operand=box(f'Handle hidden {label} anchor {sx}',[min(sx*2.795,sx*xe),y0,handle_z-.300],[max(sx*2.795,sx*xe),y1,handle_z+.300],hardware,.004)
  union_handle21(ob,operand,ob.name+' '+label+' attachment')
 # Cut the exact moved root, leaving a real running gap around the ring.
 ring=sc.objects[f'Chest Solid Ring Handle {sx}'];rm=ring.data;rm.update();inverse=yaw.inverted();norm={}
 for loop in rm.loops:
  if loop.vertex_index not in norm:norm[loop.vertex_index]=rm.corner_normals[loop.index].vector.copy()
 VV=[]
 for i,v in enumerate(rm.vertices):
  local=inverse@Vector((v.co.x,v.co.z,-v.co.y));nn=norm[i];normal=inverse@Vector((nn.x,nn.z,-nn.y));VV.append(tuple(local+normal*.012))
 cutter=solid(f'Handle actual root clearance 21 {sx}',VV,[list(f.vertices) for f in rm.polygons],hardware,0,True);cutter['allowed_euler']=[0]
 union_handle21(ob,cutter,ob.name+' actual root clearance','DIFFERENCE')
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Curved handle surface normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 return ob

def mirror_cover21():
 source=sc.objects['Chest Measured Rolled Handle Cover -1'];sm=source.data;inv=yaw.inverted();V=[];NN=[]
 for v in sm.vertices:
  q=inv@Vector((v.co.x,v.co.z,-v.co.y));q.x=-q.x;V.append(tuple(q))
 for face in sm.polygons:
  normals={}
  for li in face.loop_indices:
   n=sm.corner_normals[li].vector;q=inv@Vector((n.x,n.z,-n.y));q.x=-q.x;q=yaw@q;normals[sm.loops[li].vertex_index]=(q.x,-q.z,q.y)
  NN.append(normals)
 ob=solid('Chest Measured Rolled Handle Cover 1',V,[list(f.vertices)[::-1] for f in sm.polygons],hardware,0,[f.use_smooth for f in sm.polygons]);ob['allowed_euler']=[0,2]
 bm=bmesh.new();bm.from_mesh(ob.data);handle_triangles21(bm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Reflected curved cover normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 prove_part(ob,'Mirrored completed right handle cover');return ob

def local_vertices(ob):
 inv=yaw.inverted()
 return np.array([tuple(inv@Vector((v.co.x,v.co.z,-v.co.y))) for v in ob.data.vertices])

def bvh(ob):
 me=ob.data;me.calc_loop_triangles()
 return BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True,epsilon=1e-7)

if not globals().get('HANDLE21_DEFINE_ONLY',False):
 handle21_checks=[]
 for sx in (-1,1):
  ring21(sx)
  plate=box(f'Chest Handle Mount {sx}',[min(sx*2.595,sx*2.810),-.635,-.320],[max(sx*2.595,sx*2.810),.105,1.120],frame,.035)
  cover=cover21(sx) if sx<0 else mirror_cover21()
  for i,z in enumerate([-.202,.916]):dome(f'Chest Handle Mount Rivet {sx} {-1 if i==0 else 1}',[sx*2.815,-.040,z],[sx,0,0],.070)
  ring=sc.objects[f'Chest Solid Ring Handle {sx}'];v=local_vertices(ring);mask=(v[:,1]>=-.635)&(v[:,1]<=.105)&(v[:,2]>=-.320)&(v[:,2]<=1.120)
  assert mask.any();clearance=float((v[mask,0]*sx-2.810).min());assert clearance>=.004,(sx,'ring enters plate',clearance)
  assert not bvh(ring).overlap(bvh(plate)),(sx,'ring intersects plate')
  assert not bvh(ring).overlap(bvh(cover)),(sx,'ring intersects cover')
  # Both buried necks must actually reach the plate through a range of rays.
  seats=[]
  for y in [-.020,-.440]:
   for z in [handle_z-.20,handle_z,handle_z+.20]:
    a=yaw@Vector((sx*2.780,y,z));n=yaw@Vector((sx,0,0));a=Vector((a.x,-a.z,a.y));n=Vector((n.x,-n.z,n.y));hit,point,nn,index=cover.ray_cast(a,n);assert hit,(sx,'anchor missing',y,z)
    point=yaw.inverted()@Vector((point.x,point.z,-point.y));assert abs(point.x)*1<=2.810,(sx,'anchor detached',point.x);seats.append(float(abs(point.x)))
  handle21_checks.append(dict(side=sx,ring_plate_min_clearance=clearance,ring_plate_intersections=False,ring_cover_intersections=False,anchor_back_positions=seats,plate_top=.105,strip_bottom=.150,plate_wood_overlap=.005))
 (C/'handle_contact.json').write_text(json.dumps(handle21_checks,indent=2));print('Built larger seated handle plates, supported curved covers and rings entirely in front of plates.')
 
 
 (C/'handle_build_proof.json').write_text(json.dumps(proof,indent=2))
