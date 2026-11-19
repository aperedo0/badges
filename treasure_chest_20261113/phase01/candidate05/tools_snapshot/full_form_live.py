import bpy,bmesh,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix,Vector,geometry
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate05';C.mkdir(exist_ok=True)
assert 'APPROVED (full form round 2)' in (R/'PLAN.md').read_text()
sc=bpy.context.scene;sc.name='Chest Complete Form Phase 1';D=json.loads((P/'design.json').read_text());yaw=Matrix.Rotation(math.radians(D['yaw_degrees']),3,'Y')
def mat(name,c):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=0;b.inputs['Roughness'].default_value=.40;return m
frame=mat('Chest rough structural forms',(.13,.13,.13));hardware=mat('Chest rough hardware forms',(.23,.23,.23))
for ob in sc.objects:
 if ob.name.startswith('Guide Foot'):
  ob.hide_render=True;ob.hide_set(True);ob['phase']=0;ob['full_form']=False
for name in ['Chest Body Envelope','Chest Barrel Lid Envelope']:
 ob=sc.objects[name];ob['full_form']=True;ob.hide_render=False;ob.hide_set(False)
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
  for y,w,xx,zz in [(-2.455,.92,2.30,1.40),(-1.99,.92,2.30,1.40),(-1.69,.62,2.42,1.52)]:
   q=chamfer_rect(w/2,w/2,.10);V.extend(np.c_[q[:,0]+sx*xx,np.full(8,y),q[:,1]+sz*zz])
  F=[list(range(7,-1,-1)),list(range(16,24))]
  for k in range(2):
   for i in range(8):j=(i+1)%8;F.append([k*8+i,k*8+j,(k+1)*8+j,(k+1)*8+i])
  solid(f'Chest Angular Boot {sx} {sz}',V,F,bevel=.04)
  V=[]
  for y,w,xx,zz in [(.53,.76,2.38,1.48),(.88,.76,2.38,1.48),(1.14,.58,2.42,1.52)]:
   q=chamfer_rect(w/2,w/2,.09);V.extend(np.c_[q[:,0]+sx*xx,np.full(8,y),q[:,1]+sz*zz])
  solid(f'Chest Lid Corner Armor {sx} {sz}',V,F,bevel=.025)
  V=[]
  for y,w in [(.02,.64),(.15,.76),(.512,.76)]:
   q=chamfer_rect(w/2,w/2,.09);V.extend(np.c_[q[:,0]+sx*2.38,np.full(8,y),q[:,1]+sz*1.48])
  solid(f'Chest Body Corner Collar {sx} {sz}',V,F,bevel=.025)
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

clipped_armor('Chest Hasp Mount',[-.49,.36,1.76],[.49,1.02,1.96])
cylinder('Chest Front Hasp Barrel',[0,.64,2.00],.14,.78)
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
outer=rounded_poly(base_outline)
r=.165;cy=-.57;neck=.072;start=-math.acos(neck/r);a=np.linspace(start,math.pi-start,36);hole=np.vstack([np.c_[r*np.cos(a),cy+r*np.sin(a)],[[-.140,-1.08],[.140,-1.08]]])
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
back=rounded_poly(offset_outline(base_outline,-.045));inner=rounded_poly(offset_outline(base_outline,.080))
shield('Chest Lock Backing With Bore',back,1.90,2.015,.012)
# Explicit bevel geometry preserves the broad bevel around the concave outline.
K=len(outer);V=np.vstack([np.c_[q,np.full(K,z)] for q,z in [(outer,2.00),(outer,2.10),(inner,2.22),(inner,2.00)]]);F=[]
for k in range(4):
 for i in range(K):
  j=(i+1)%K;n=(k+1)%4;F.append([k*K+i,k*K+j,n*K+j,n*K+i])
solid('Chest Lock Border With Bore',V,F,hardware,0)
face=rounded_poly(offset_outline(base_outline,.074))
shield('Chest Shield Lock Plate With Bore',face,2.035,2.212,.010)
# A swept, closed strap bends in front of the shield and meets the hinge.
controls=np.array([[0,.64,2.13],[0,.40,2.35],[0,-.06,2.42],[0,-.28,2.28]])
t=np.linspace(0,1,28);curve=(1-t[:,None])**3*controls[0]+3*(1-t[:,None])**2*t[:,None]*controls[1]+3*(1-t[:,None])*t[:,None]**2*controls[2]+t[:,None]**3*controls[3]
tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];A=np.array([1,0,0]);out=np.cross(tangent,A);out/=np.linalg.norm(out,axis=1)[:,None];V=[]
for p,n in zip(curve,out):
 for x,z in [(-.255,-.055),(.255,-.055),(.255,.055),(-.255,.055)]:V.append(p+A*x+n*z)
F=[];S=[]
for i in range(len(curve)-1):
 for j in range(4):F.append([i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j]);S.append(j in (0,2))
F.extend([[3,2,1,0],list(range((len(curve)-1)*4,len(curve)*4))]);S.extend([False,False]);solid('Chest Curved Hasp Tongue',V,F,hardware,.022,S)

for sx in (-1,1):
 cx=sx*2.70;clipped_armor(f'Chest Handle Mount {sx}',[cx-.07,-.48,-.42],[cx+.07,.18,.42])
 cylinder(f'Chest Handle Pivot {sx}',[sx*2.84,-.20,0],.18,.62,'Z')
 V=[];F=[];N=64;M=16
 for i in range(N):
  u=i*2*math.pi/N
  for j in range(M):
   v=j*2*math.pi/M;rho=.56+.126*math.cos(v);V.append([sx*2.88+.126*math.sin(v),-.77+rho*math.cos(u),rho*math.sin(u)])
 for i in range(N):
  for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
 solid(f'Chest Solid Ring Handle {sx}',V,F,hardware,0,True)
for sx in (-1,1):
 x=sx*1.55;box(f'Chest Rear Hinge Lower {sx}',[x-.28,.12,-1.91],[x+.28,.49,-1.75],frame,.03);box(f'Chest Rear Hinge Upper {sx}',[x-.28,.53,-1.91],[x+.28,.91,-1.75],frame,.03);cylinder(f'Chest Rear Hinge Barrel {sx}',[x,.51,-1.93],.12,.60)
# Closed rolled returns, layered pivots and solid construction fasteners.
cylinder('Chest Hasp Rolled Return',[0,-.28,2.285],.080,.515)
for sx in (-1,1):
 cylinder(f'Chest Hasp Barrel Collar {sx}',[sx*.335,.64,2.00],.163,.105)
 cylinder(f'Chest Hasp Pivot Cap {sx}',[sx*.425,.64,2.00],.130,.08)
 for sz in (-1,1):cylinder(f'Chest Handle End Collar {sx} {sz}',[sx*2.84,-.20,sz*.278],.205,.07,'Z')
 # Thick lower handle sleeves are curved closed solids, rather than painted stripes.
 for k,u0 in enumerate([2.60,math.pi,3.68]):
  V=[];F=[];A=6;B=16
  for i,u in enumerate(np.linspace(u0-.11,u0+.11,A)):
   for j in range(B):
    v=j*2*math.pi/B;rho=.56+.148*math.cos(v);V.append([sx*2.88+.148*math.sin(v),-.77+rho*math.cos(u),rho*math.sin(u)])
  for i in range(A-1):
   for j in range(B):F.append([i*B+j,i*B+(j+1)%B,(i+1)*B+(j+1)%B,(i+1)*B+j])
  F.extend([list(range(B-1,-1,-1)),list(range((A-1)*B,A*B))]);solid(f'Chest Handle Lower Sleeve {sx} {k}',V,F,hardware,0,True)

def dome(name,p,n,r=.085):
 n=Vector(n).normalized();rot=Vector((0,0,1)).rotation_difference(n);bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=8,radius=1)
 for v in bm.verts:v.co=rot@Vector((v.co.x*r,v.co.y*r,v.co.z*r*.52))+Vector(p)
 for f in bm.faces:f.smooth=True
 return finish(bm,name,hardware,0)
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
 for sz in (-1,1):dome(f'Chest Handle Mount Rivet {sx} {sz}',[sx*2.775,-.08,sz*.30],[sx,0,0],.062)
for j,(x,y,r) in enumerate([(-.72,-.02,.105),(.72,-.02,.105),(-.49,-.43,.058),(.49,-.43,.058),(-.49,-1.02,.058),(.49,-1.02,.058),(0,-1.34,.058)]):dome(f'Chest Lock Rivet {j}',[x,y,2.24],[0,0,1],r)
dome('Chest Lower Strap Rivet',[0,-1.96,2.005],[0,0,1],.105)
# Faceted studs are separate metal solids with finished backs.
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*2.48;y=-.93;z=sz*1.795;V=[(x-.10,y,z),(x,y+.22,z),(x+.10,y,z),(x,y-.22,z),(x,y,z+sz*.095),(x,y,z-sz*.025)];F=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[1,0,5],[2,1,5],[3,2,5],[0,3,5]];solid(f'Chest Upright Diamond {sx} {sz}',V,F,hardware,.008)
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
