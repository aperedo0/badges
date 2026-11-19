import bpy,bmesh,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix,Vector,geometry
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate08';C.mkdir(exist_ok=True)
assert 'APPROVED (full form round 2)' in (R/'PLAN.md').read_text()
assert 'APPROVED method round 2' in (P/'REFINEMENT08.md').read_text()
sc=bpy.context.scene;sc.name='Chest Complete Form Phase 1';D=json.loads((P/'design.json').read_text());yaw=Matrix.Rotation(math.radians(D['yaw_degrees']),3,'Y')
def mat(name,c):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=0;b.inputs['Roughness'].default_value=.40;return m
frame=mat('Chest rough structural forms',(.13,.13,.13));hardware=mat('Chest rough hardware forms',(.23,.23,.23))
for ob in sc.objects:
 if ob.name.startswith('Guide Foot'):
  ob.hide_render=True;ob.hide_set(True);ob['phase']=0;ob['full_form']=False
for name in ['Chest Body Envelope','Chest Barrel Lid Envelope']:
 ob=sc.objects[name];ob['full_form']=True;ob.hide_render=False;ob.hide_set(False)
base=np.load(P/'core_baseline.npz')
for i,name in enumerate(['Chest Body Envelope','Chest Barrel Lid Envelope']):
 me=sc.objects[name].data
 for v,p in zip(me.vertices,base[f'v{i}']):v.co=p
 me.update();me.normals_split_custom_set(base[f'n{i}'].tolist())
def loft_faces(count,K=8):
 F=[list(range(K-1,-1,-1)),list(range((count-1)*K,count*K))]
 for k in range(count-1):
  for i in range(K):j=(i+1)%K;F.append([k*K+i,k*K+j,(k+1)*K+j,(k+1)*K+i])
 return F
def finish(bm,name,material,bevel=.03):
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle(0)>math.radians(25)]
 if bevel and edges:
  result=bmesh.ops.bevel(bm,geom=edges,offset=bevel,segments=3,profile=.5,affect='EDGES',clamp_overlap=True)
  for f in result['faces']:f.smooth=True
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 for v in bm.verts:
  p=yaw@v.co;v.co=(p.x,-p.z,p.y)
 ob=sc.objects.get(name)
 if ob is None:
  me=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob)
 else:me=ob.data;me.clear_geometry();me.materials.clear()
 bm.to_mesh(me);bm.free();me.update();me.materials.append(material);ob.hide_set(False);ob.hide_render=False
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Broad form normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 ob['phase']=1;ob['full_form']=True;ob['shape_only']=True;return ob

def solid(name,V,F,material=frame,bevel=.03,smooth=False):
 bm=bmesh.new();verts=[bm.verts.new(tuple(v)) for v in V]
 for i,f in enumerate(F):
  face=bm.faces.new([verts[j] for j in f]);face.smooth=bool(smooth[i] if isinstance(smooth,list) else smooth)
 if name.startswith('Chest Angular Boot'):
  y0=min(v.co.y for v in bm.verts);bottom=[v for v in bm.verts if abs(v.co.y-y0)<1e-6];bmesh.ops.bevel(bm,geom=bottom,offset=.075,segments=1,profile=.5,affect='VERTICES',clamp_overlap=True);bevel=.025
 return finish(bm,name,material,bevel)

def box(name,lo,hi,material=frame,bevel=.04):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1);lo,hi=np.array(lo),np.array(hi)
 for v in bm.verts:v.co=lo+(np.array(v.co)+.5)*(hi-lo)
 return finish(bm,name,material,bevel)

def clipped_armor(name,lo,hi):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1);lo,hi=np.array(lo),np.array(hi)
 for v in bm.verts:v.co=lo+(np.array(v.co)+.5)*(hi-lo)
 bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.12,segments=1,profile=.5,affect='EDGES',clamp_overlap=True)
 return finish(bm,name,frame,.015)

def chamfer_rect(x,z,c):return np.array([[x-c,z],[x,z-c],[x,-z+c],[x-c,-z],[-x+c,-z],[-x,-z+c],[-x,z-c],[-x+c,z]])
def belt(name,y0,y1):
 O=chamfer_rect(2.73,1.78,.06);I=chamfer_rect(2.59,1.64,.06);loops=[np.c_[q[:,0],np.full(8,y),q[:,1]] for y in [y0,y1] for q in [O,I]];V=np.vstack(loops);F=[]
 for i in range(8):
  j=(i+1)%8;F.extend([[i,j,16+j,16+i],[8+j,8+i,24+i,24+j],[i,8+i,8+j,j],[16+i,16+j,24+j,24+i]])
 return solid(name,V,F,bevel=.028)

def arch(name,x,width,inner_offset=-.012,outer_offset=.12):
 N=64;V=[]
 for i in range(N+1):
  a=i*math.pi/N;p=np.array([0,.53+2.05*math.sin(a),1.65*math.cos(a)]);n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n)
  for xx,off in [(-width/2,inner_offset),(width/2,inner_offset),(width/2,outer_offset),(-width/2,outer_offset)]:V.append(p+n*off+[x+xx,0,0])
 F=[];S=[]
 for i in range(N):
  for k in range(4):F.append([i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k]);S.append(k in (0,2))
 F.extend([[3,2,1,0],[N*4,N*4+1,N*4+2,N*4+3]]);S.extend([False,False]);return solid(name,V,F,bevel=.025,smooth=S)

for i,x in enumerate([-2.40,-.90,.90,2.40]):arch(f'Chest Lid Hoop {i+1}',x,.48)
for sx in (-1,1):arch(f'Chest Broad End Arch {sx}',sx*2.64,.12,-.24,.08)
belt('Chest Upper Lid Rim',.530,.900);belt('Chest Body Upper Rim',.080,.512);belt('Chest Lower Rim',-2.205,-1.840)
for sx in (-1,1):
 for sz in (-1,1):
  x,z=2.60,1.65;q=np.array([[x-.36,z-.01],[x-.01,z-.01],[x-.01,z-.36],[x+.12,z-.36],[x+.12,z+.12],[x-.36,z+.12]])*np.array([sx,sz]);K=len(q);V=np.vstack([np.c_[q[:,0],np.full(K,y),q[:,1]] for y in [-2.16,.49]]);F=[list(range(K-1,-1,-1)),list(range(K,2*K))]
  for i in range(K):j=(i+1)%K;F.append([i,j,K+j,K+i])
  solid(f'Chest Corner Upright {sx} {sz}',V,F,bevel=.03)
  V=[]
  for y,w,xx,zz in [(-2.455,.88,2.30,1.40),(-2.30,.92,2.30,1.40),(-1.99,.92,2.30,1.40),(-1.69,.62,2.42,1.52)]:
   q=np.array([[w/2,w/2],[w/2,-w/2],[-w/2,-w/2],[-w/2,w/2]]);V.extend(np.c_[q[:,0]+sx*xx,np.full(4,y),q[:,1]+sz*zz])
  F=loft_faces(4,4)
  solid(f'Chest Angular Boot {sx} {sz}',V,F,bevel=.055)
  V=[]
  for y,w,xx,zz in [(.53,.76,2.38,1.48),(.88,.76,2.38,1.48),(1.14,.58,2.42,1.52)]:
   q=chamfer_rect(w/2,w/2,.09);V.extend(np.c_[q[:,0]+sx*xx,np.full(8,y),q[:,1]+sz*zz])
  solid(f'Chest Lid Corner Armor {sx} {sz}',V,loft_faces(3),bevel=.025)
  V=[]
  for y,w in [(.02,.64),(.15,.76),(.512,.76)]:
   q=chamfer_rect(w/2,w/2,.09);V.extend(np.c_[q[:,0]+sx*2.38,np.full(8,y),q[:,1]+sz*1.48])
  solid(f'Chest Body Corner Collar {sx} {sz}',V,loft_faces(3),bevel=.025)
box('Chest Central Lock Strap',[-.25,-2.17,1.645],[.25,.49,1.800],bevel=.03)
box('Chest Central Lower Cuff',[-.37,-2.205,1.780],[.37,-1.675,2.000],hardware,.05)

def ellipsoid(name,c,r):
 bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=20,v_segments=10,radius=1)
 for v in bm.verts:v.co=np.array(c)+np.array(v.co)*r
 for f in bm.faces:f.smooth=True
 return finish(bm,name,hardware,0)
for i,x in enumerate([-2.40,-.90,.90,2.40]):ellipsoid(f'Chest Crown Fastener Mass {i+1}',[x,2.70,0],[.10,.07,.10])

def cylinder(name,c,r,length,axis='X'):
 bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=40,radius1=r,radius2=r,depth=length);rot=Matrix.Rotation(math.pi/2,3,'Y') if axis=='X' else Matrix.Identity(3)
 for v in bm.verts:v.co=rot@v.co+Vector(c)
 for f in bm.faces:f.smooth=len(f.verts)==4
 return finish(bm,name,hardware,.02)

q=np.array([[-.64,.35],[.64,.35],[.64,.85],[.43,1.06],[-.43,1.06],[-.64,.85]]);K=len(q);V=np.vstack([np.c_[q,np.full(K,z)] for z in [1.76,1.96]]);F=[list(range(K-1,-1,-1)),list(range(K,2*K))]
for i in range(K):j=(i+1)%K;F.append([i,j,K+j,K+i])
solid('Chest Hasp Mount',V,F,frame,.025)
cylinder('Chest Front Hasp Barrel',[0,.64,2.00],.168,.72)
obsolete=sc.objects.get('Chest Lock Mounting Shoulder')
if obsolete:obsolete.hide_render=True;obsolete.hide_set(True);obsolete['full_form']=False
# A stepped shield, broad edge and back plate share a real aligned key bore.
def rounded_poly(poly,d=.045):
 poly=np.array(poly,float);out=[]
 for i,p in enumerate(poly):
  u=poly[(i-1)%len(poly)]-p;v=poly[(i+1)%len(poly)]-p;du=min(d,np.linalg.norm(u)*.20);dv=min(d,np.linalg.norm(v)*.20);a=p+u/np.linalg.norm(u)*du;b=p+v/np.linalg.norm(v)*dv
  for t in np.linspace(0,1,5):out.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
 return np.array(out)
base_outline=np.array([[-.94,.17],[-.40,.17],[-.28,-.18],[.28,-.18],[.40,.17],[.94,.17],[.94,-.26],[.79,-.34],[.72,-.53],[.72,-1.03],[0,-1.60],[-.72,-1.03],[-.72,-.53],[-.79,-.34],[-.94,-.26]],float)
base_outline[:,1]+=.205
outer=rounded_poly(base_outline)
r=.165;cy=-.435;neck=.072;start=-math.acos(neck/r);a=np.linspace(start,math.pi-start,36);hole=np.vstack([np.c_[r*np.cos(a),cy+r*np.sin(a)],[[-.140,-.945],[.140,-.945]]])
def inside(p,poly):
 hit=False;j=len(poly)-1
 for i in range(len(poly)):
  a,b=poly[i],poly[j]
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  j=i
 return hit
def shield(name,outline,z0,z1,bevel):
 coords=np.vstack([outline,hole]);edges=[]
 for lo,K in [(0,len(outline)),(len(outline),len(hole))]:edges.extend([(lo+i,lo+(i+1)%K) for i in range(K)])
 points,ee,ff,*rest=geometry.delaunay_2d_cdt([Vector(v) for v in coords],edges,[list(range(len(outline)))],1,1e-7);points=np.array(points);tri=[list(f) for f in ff if not inside(points[list(f)].mean(0),hole)];K=len(points);V=np.vstack([np.c_[points,np.full(K,z)] for z in [z0,z1]]);F=tri+[[(j+K) for j in f[::-1]] for f in tri];counts={}
 for f in tri:
  for aa,bb in zip(f,np.roll(f,-1)):
   key=tuple(sorted((int(aa),int(bb))));counts[key]=counts.get(key,0)+1
 for (aa,bb),n in counts.items():
  if n==1:F.append([aa,bb,bb+K,aa+K])
 return solid(name,V,F,hardware,bevel)
def offset_outline(poly,d):
 area=np.cross(poly,np.roll(poly,-1,axis=0)).sum()/2;out=[]
 for i,p in enumerate(poly):
  u=p-poly[i-1];v=poly[(i+1)%len(poly)]-p;u/=np.linalg.norm(u);v/=np.linalg.norm(v);n0=np.array([-u[1],u[0]])*np.sign(area);n1=np.array([-v[1],v[0]])*np.sign(area);m=n0+n1;m/=np.linalg.norm(m);out.append(p+m*d/np.dot(m,n0))
 return np.array(out)
back=rounded_poly(offset_outline(base_outline,-.025))
shield('Chest Lock Backing With Bore',back,1.88,1.99,.012)
shield_outline=np.array([[-.52,.015],[-.30,-.31],[.30,-.31],[.52,.015],[.72,-.25],[.64,-.46],[.64,-1.04],[0,-1.56],[-.64,-1.04],[-.64,-.46],[-.72,-.25]],float)
shield_outline[:,1]+=.205
outer=rounded_poly(shield_outline,.025);inner=rounded_poly(offset_outline(shield_outline,.060),.020)
K=len(outer);V=np.vstack([np.c_[q,np.full(K,z)] for q,z in [(outer,1.975),(outer,2.015),(inner,2.115),(inner,1.975)]]);F=[]
for k in range(4):
 for i in range(K):
  j=(i+1)%K;n=(k+1)%4;F.append([k*K+i,k*K+j,n*K+j,n*K+i])
solid('Chest Lock Border With Bore',V,F,hardware,0)
face=rounded_poly(offset_outline(shield_outline,.054),.020)
shield('Chest Shield Lock Plate With Bore',face,2.020,2.107,.008)
# A swept, closed strap bends in front of the shield and meets the hinge.
controls=np.array([[0,.64,2.13],[0,.46,2.25],[0,.15,2.15],[0,-.055,2.05]])
t=np.linspace(0,1,28);curve=(1-t[:,None])**3*controls[0]+3*(1-t[:,None])**2*t[:,None]*controls[1]+3*(1-t[:,None])*t[:,None]**2*controls[2]+t[:,None]**3*controls[3]
tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];A=np.array([1,0,0]);out=np.cross(tangent,A);out/=np.linalg.norm(out,axis=1)[:,None];V=[]
for p,n in zip(curve,out):
 for x,z in [(-.255,-.055),(.255,-.055),(.255,.055),(-.255,.055)]:V.append(p+A*x+n*z)
F=[];S=[]
for i in range(len(curve)-1):
 for j in range(4):F.append([i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j]);S.append(j in (0,2))
F.extend([[3,2,1,0],list(range((len(curve)-1)*4,len(curve)*4))]);S.extend([False,False]);solid('Chest Curved Hasp Tongue',V,F,hardware,.022,S)

for side in (-1,1):
 V=[];F=[]
 for p,n in zip(curve,out):
  for x,z in [(-.0125,.054),(.0125,.054),(.0125,.070),(-.0125,.070)]:V.append(p+A*(side*.236+x)+n*z)
 for i in range(len(curve)-1):
  for j in range(4):F.append([i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j])
 F.extend([[3,2,1,0],list(range((len(curve)-1)*4,len(curve)*4))]);solid(f'Chest Hasp Edge Rail {side}',V,F,hardware,.004,True)

def handle_hood(name,sx,z0,z1,r=.230):
 V=[];F=[];S=[];N=48
 for a in np.linspace(-math.pi/8,math.pi+math.pi/8,N+1):
  for radius,z in [(.165,z0),(r,z0),(r,z1),(.165,z1)]:V.append([sx*(2.88+radius*math.cos(a)),-.20+radius*math.sin(a),z])
 for i in range(N):
  for k in range(4):F.append([i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k]);S.append(k in (1,3))
 F.extend([[3,2,1,0],list(range(N*4,N*4+4))]);S.extend([False,False]);return solid(name,V,F,hardware,.012,S)

for sx in (-1,1):
 cx=sx*2.70;clipped_armor(f'Chest Handle Mount {sx}',[cx-.07,-.48,-.56],[cx+.07,.18,.56])
 handle_hood(f'Chest Handle Pivot {sx}',sx,-.31,.31)
 V=[];F=[];normals=[];M=24;grooves=[2.52,math.pi,3.76]
 raw=np.sort(np.r_[np.arange(128)*2*math.pi/128,*[g+np.linspace(-.060,.060,17) for g in grooves]])
 us=[float(raw[0])]
 for u in raw[1:]:
  if u-us[-1]>1e-5:us.append(float(u))
 N=len(us)
 def collar_radius(u):
  left=min(1,max(0,(u-2.28)/.24));right=min(1,max(0,(4.00-u)/.24));fade=left*left*(3-2*left)*right*right*(3-2*right)
  return .126+.017*fade
 def groove_depth(u):return sum(.003*math.exp(-((u-g)/.020)**2) for g in grooves)
 for u in us:
  cr=collar_radius(u);dc=(collar_radius(u+.0001)-collar_radius(u-.0001))/.0002;gr=groove_depth(u);dg=(groove_depth(u+.0001)-groove_depth(u-.0001))/.0002
  for j in range(M):
   v=j*2*math.pi/M;sn=math.sin(v);cs=math.cos(v);w=sn**4;dw=4*sn**3*cs;tube=cr-gr*w;ru=dc-dg*w;rv=-gr*dw;rho=.56+tube*cs
   V.append([sx*2.88+tube*sn,-.77+rho*math.cos(u),rho*math.sin(u)])
   du=np.array([ru*sn,ru*cs*math.cos(u)-rho*math.sin(u),ru*cs*math.sin(u)+rho*math.cos(u)]);dv=np.array([rv*sn+tube*cs,(rv*cs-tube*sn)*math.cos(u),(rv*cs-tube*sn)*math.sin(u)]);n=np.cross(du,dv);assert np.linalg.norm(n)>1e-10;n/=np.linalg.norm(n);q=yaw@Vector(n);normals.append((q.x,-q.z,q.y))
 for i in range(N):
  for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
 ob=solid(f'Chest Solid Ring Handle {sx}',V,F,hardware,0,True);ob.data.normals_split_custom_set([normals[l.vertex_index] for l in ob.data.loops])

for sx in (-1,1):
 x=sx*1.55;box(f'Chest Rear Hinge Lower {sx}',[x-.28,.12,-1.91],[x+.28,.49,-1.75],frame,.03);box(f'Chest Rear Hinge Upper {sx}',[x-.28,.53,-1.91],[x+.28,.91,-1.75],frame,.03);cylinder(f'Chest Rear Hinge Barrel {sx}',[x,.51,-1.93],.12,.60)
# Closed rolled returns, layered pivots and solid construction fasteners.
cylinder('Chest Hasp Rolled Return',[0,-.055,2.05],.078,.47)
for sx in (-1,1):
 cylinder(f'Chest Hasp Barrel Collar {sx}',[sx*.335,.64,2.00],.185,.024)
 cylinder(f'Chest Hasp Inner Collar {sx}',[sx*.280,.64,2.00],.182,.024)
 obsolete=sc.objects.get(f'Chest Hasp Pivot Cap {sx}')
 if obsolete:obsolete.hide_render=True;obsolete.hide_set(True);obsolete['full_form']=False
 for sz in (-1,1):
  handle_hood(f'Chest Handle End Collar {sx} {sz}',sx,sz*.278-.035,sz*.278+.035,.245)
  handle_hood(f'Chest Handle Inner Collar {sx} {sz}',sx,sz*.19-.0225,sz*.19+.0225,.237)
 for k in range(3):
  ob=sc.objects.get(f'Chest Handle Lower Sleeve {sx} {k}')
  if ob:ob.hide_render=True;ob.hide_set(True);ob['full_form']=False

def dome(name,p,n,r=.085):
 principal=name.startswith(('Chest Boot','Chest Upper Corner'));r=r*1.18 if principal else r;depth=.65 if r<=.085 else .52
 n=Vector(n).normalized();rot=Vector((0,0,1)).rotation_difference(n);N=32;L=8;V=[];F=[];normals=[]
 # A closed calotte with a buried flat back and smooth analytical curvature.
 for radius,z in [(r*.98,-.012)]+[(r*math.sin(a),r*depth*math.cos(a)) for a in np.linspace(math.pi/2,math.pi/16,L)]:
  for j in range(N):
   a=j*2*math.pi/N;V.append(rot@Vector((radius*math.cos(a),radius*math.sin(a),z))+Vector(p));q=rot@Vector((radius*math.cos(a)/(r*r),radius*math.sin(a)/(r*r),z/(r*depth)**2));q.normalize();q=yaw@q;normals.append((q.x,-q.z,q.y))
 for k in range(L):
  for j in range(N):F.append([k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j])
 tip=len(V);V.append(rot@Vector((0,0,r*depth))+Vector(p));q=yaw@n;normals.append((q.x,-q.z,q.y))
 for j in range(N):F.append([L*N+j,L*N+(j+1)%N,tip])
 F.append(list(range(N-1,-1,-1)));ob=solid(name,V,F,hardware,0,[True]*(len(F)-1)+[False]);me=ob.data;back=tuple(-v for v in normals[-1]);corner=[None]*len(me.loops)
 for f in me.polygons:
  for li in f.loop_indices:corner[li]=normals[me.loops[li].vertex_index] if f.use_smooth else back
 me.normals_split_custom_set(corner)
 if principal:
  bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=40,radius1=r*1.06,radius2=r*1.06,depth=.009)
  for v in bm.verts:v.co=rot@v.co+Vector(p)-n*.004
  for f in bm.faces:f.smooth=len(f.verts)==4
  finish(bm,name+' Seat',hardware,.002)
 return ob
# Rivets follow the real band surface normals around the entire lid.
for i,x in enumerate([-2.40,-.90,.90,2.40]):
 for k,a in enumerate([.25,.65,1.05,math.pi-1.05,math.pi-.65,math.pi-.25]):
  n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n);p=np.array([x,.53+2.05*math.sin(a),1.65*math.cos(a)])+n*.122;dome(f'Chest Hoop Rivet {i} {k}',p,n,.085)
for sx in (-1,1):
 for sz in (-1,1):
  dome(f'Chest Upper Corner Front Rivet {sx} {sz}',[sx*2.38,.72,sz*1.865],[0,0,sz],.105)
  dome(f'Chest Upper Corner End Rivet {sx} {sz}',[sx*2.765,.72,sz*1.48],[sx,0,0],.095)
  dome(f'Chest Boot Front Rivet {sx} {sz}',[sx*2.30,-2.20,sz*1.865],[0,0,sz],.115)
  dome(f'Chest Boot End Rivet {sx} {sz}',[sx*2.765,-2.20,sz*1.40],[sx,0,0],.105)
for sz in (-1,1):
 for j,x in enumerate([-1.75,-.85,.85,1.75]):
  for k,y in enumerate([.715,-2.025]):dome(f'Chest Rail Rivet {sz} {j} {k}',[x,y,sz*1.785],[0,0,sz],.074)
 for j,x in enumerate([-1.90,-1.00,0,1.00,1.90]):dome(f'Chest Body Lip Rivet {sz} {j}',[x,.28,sz*1.785],[0,0,sz],.045)
for sx in (-1,1):
 for j,z in enumerate([-.80,.80]):
  for k,y in enumerate([.715,-2.025]):dome(f'Chest End Rail Rivet {sx} {j} {k}',[sx*2.735,y,z],[sx,0,0],.074)
 for sz in (-1,1):dome(f'Chest Handle Mount Rivet {sx} {sz}',[sx*2.775,-.06,sz*.43],[sx,0,0],.062)
for j,(x,y,r) in enumerate([(-.73,-.02,.105),(.73,-.02,.105),(-.43,-.45,.058),(.43,-.45,.058),(-.43,-1.02,.058),(.43,-1.02,.058),(0,-1.31,.058)]):dome(f'Chest Lock Rivet {j}',[x,y+.205,2.0 if j<2 else 2.108],[0,0,1],r)
dome('Chest Lower Strap Rivet',[0,-1.96,2.005],[0,0,1],.105)
# Faceted studs are separate metal solids with finished backs.
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*2.48;y=-.93;z=sz*1.795;V=[(x-.10,y,z),(x,y+.22,z),(x+.10,y,z),(x,y-.22,z),(x,y,z+sz*.095),(x,y,z-sz*.025)];F=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[1,0,5],[2,1,5],[3,2,5],[0,3,5]];solid(f'Chest Upright Diamond {sx} {sz}',V,F,hardware,.008)
# End arch fixing heads sit on the end face, not on the curved hoop surface.
for sx in (-1,1):
 for k,a in enumerate([.38,.91,math.pi-.91,math.pi-.38]):
  n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n);p=np.array([sx*2.705,.53+2.05*math.sin(a),1.65*math.cos(a)])-n*.080;dome(f'Chest End Arch Rivet {sx} {k}',p,[sx,0,0],.080)
 for sz in (-1,1):
  dome(f'Chest Corner Body Cuff Front Rivet {sx} {sz}',[sx*2.38,.28,sz*1.865],[0,0,sz],.055)
  dome(f'Chest Corner Body Cuff End Rivet {sx} {sz}',[sx*2.765,.28,sz*1.48],[sx,0,0],.055)

for sx in (-1,1):
 dome(f'Chest Hasp Pivot Dome {sx}',[sx*.365,.64,2.00],[sx,0,0],.090)
 dome(f'Chest Hasp Mount Fastener {sx}',[sx*.525,.66,1.965],[0,0,1],.075)
 cx=sx*2.735;box(f'Chest End Arch Crown Tab {sx}',[cx-.035,2.335,-.105],[cx+.035,2.665,.105],frame,.025)
 dome(f'Chest End Crown Fastener {sx}',[sx*2.777,2.49,0],[sx,0,0],.070)
# Reduce the lock projection while preserving dome shape and real bore alignment.
lock_names={'Chest Lock Backing With Bore','Chest Lock Border With Bore','Chest Shield Lock Plate With Bore'}
inv=yaw.inverted()
for ob in sc.objects:
 if ob.type!='MESH' or not ob.get('full_form'):continue
 me=ob.data
 if ob.name in lock_names:
  old_normals=np.array([n.vector[:] for n in me.corner_normals]);new_normals=[]
  for v in me.vertices:
   p=inv@Vector((v.co.x,v.co.z,-v.co.y));p.z=1.88+(p.z-1.88)*.5;q=yaw@p;v.co=(q.x,-q.z,q.y)
  for n in old_normals:
   q=inv@Vector((n[0],n[2],-n[1]));q.z*=2;q.normalize();q=yaw@q;new_normals.append((q.x,-q.z,q.y))
  me.update();me.normals_split_custom_set(new_normals)
 elif ob.name.startswith('Chest Lock Rivet '):
  j=int(ob.name.split()[-1]);z=2.0 if j<2 else 2.108;d=yaw@Vector((0,0,-.5*(z-1.88)));d=Vector((d.x,-d.z,d.y))
  for v in me.vertices:v.co+=d
  me.update()
# Correct the slightly tall proportions without expanding the hard turning envelope.
# Always starts from the immutable core and regenerated hardware, never compounds.
for ob in sc.objects:
 if ob.type=='MESH' and ob.get('full_form'):
  me=ob.data;me.update();normals=np.array([n.vector[:] for n in me.corner_normals])
  for v in me.vertices:v.co.z=-2.455+(v.co.z+2.455)*.95
  normals[:,2]/=.95;normals/=np.linalg.norm(normals,axis=1)[:,None];me.update();me.normals_split_custom_set(normals.tolist())
# Neutral cyclorama for shape inspection, excluded from all model checks.
floor=sc.objects.get('Development floor')
if floor:
 profile=[(-200,-2.895),(10,-2.895)]+[(10+10*math.sin(a),-2.895+10*(1-math.cos(a))) for a in np.linspace(0,math.pi/2,24)[1:]]+[(20,50)]
 V=[(x,y,z) for x in (-200,200) for y,z in profile];K=len(profile);F=[[i,i+1,K+i+1,K+i] for i in range(K-1)];me=floor.data;me.clear_geometry();me.from_pydata(V,[],F);me.update()
 for f in me.polygons:f.use_smooth=True
 floor.hide_set(False)
for o in sc.objects:
 if o.type in ('LIGHT','CAMERA'):o.hide_set(False)
bpy.context.view_layer.objects.active=None
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Complete chest form built live with closed major hardware, end frames and central strap. No finished textures.')
