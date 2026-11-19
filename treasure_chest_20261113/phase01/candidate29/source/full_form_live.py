import bpy,bmesh,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix,Vector,geometry
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate29';C.mkdir(exist_ok=True)
assert 'APPROVED (full form round 2)' in (R/'PLAN.md').read_text()
assert 'APPROVED method round 2' in (P/'REFINEMENT08.md').read_text()
sc=bpy.context.scene
# Regenerate the numbered construction in place and hide any obsolete hardware.
for ob in sc.objects:
 if ob.type=='MESH' and ob.get('full_form'):
  ob['full_form']=False;ob.hide_render=True;ob.hide_set(True)
  if 'allowed_euler' in ob:del ob['allowed_euler']
sc.name='Chest Complete Form Phase 1';D=json.loads((P/'design.json').read_text());yaw=Matrix.Rotation(math.radians(D['yaw_degrees']),3,'Y')
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
 if i==0:
  inv=yaw.inverted();normal=[]
  for v in me.vertices:
   q=inv@Vector((v.co.x,v.co.z,-v.co.y));q.x*=2.55/2.60;q.z*=1.60/1.65;q=yaw@q;v.co=(q.x,-q.z,q.y)
  for n in base['n0']:
   q=inv@Vector((n[0],n[2],-n[1]));q.x*=2.60/2.55;q.z*=1.65/1.60;q.normalize();q=yaw@q;normal.append((q.x,-q.z,q.y))
  me.update();me.normals_split_custom_set(normal)

def loft_faces(count,K=8):
 F=[list(range(K-1,-1,-1)),list(range((count-1)*K,count*K))]
 for k in range(count-1):
  for i in range(K):j=(i+1)%K;F.append([k*K+i,k*K+j,(k+1)*K+j,(k+1)*K+i])
 return F
def finish(bm,name,material,bevel=.03):
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle(0)>math.radians(25)]
 seam_y=.53 if name.startswith('Chest Lid Corner Armor') or name=='Chest Upper Lid Rim' else (.512 if name.startswith('Chest Body Corner Collar') or name=='Chest Body Upper Rim' else None)
 if name.startswith('Chest Body Corner Collar'):seam_y=max(v.co.y for v in bm.verts)
 if seam_y is not None:edges=[e for e in edges if not all(abs(v.co.y-seam_y)<1e-6 for v in e.verts)]
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
def belt(name,y0,y1,outer_x=2.73,outer_z=1.78):
 O=chamfer_rect(outer_x,outer_z,.06);I=chamfer_rect(*( (2.59,1.64,.06) if name=='Chest Upper Lid Rim' else (2.54,1.59,.06)));loops=[np.c_[q[:,0],np.full(8,y),q[:,1]] for y in [y0,y1] for q in [O,I]];V=np.vstack(loops);F=[]
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

hoop_x=[-2.40,-1.20,.85,2.40]
for i,x in enumerate(hoop_x):arch(f'Chest Lid Hoop {i+1}',x,.48)
for sx in (-1,1):arch(f'Chest Broad End Arch {sx}',sx*2.6725,.165,-.40,.08)
lower_rail_bottom=-2.205;lower_rail_top=-1.675;lower_rail_mid=(lower_rail_bottom+lower_rail_top)/2
belt('Chest Upper Lid Rim',.530,.940,2.77,1.84);belt('Chest Body Upper Rim',.150,.512,2.68,1.78);belt('Chest Lower Rim',lower_rail_bottom,lower_rail_top)
for sx in (-1,1):
 for sz in (-1,1):
  x,z=2.60,1.65;q=np.array([[x-.36,z-.06],[x-.06,z-.06],[x-.06,z-.36],[x+.12,z-.36],[x+.12,z+.12],[x-.36,z+.12]])*np.array([sx,sz]);K=len(q);V=np.vstack([np.c_[q[:,0],np.full(K,y),q[:,1]] for y in [-2.16,.49]]);F=[list(range(K-1,-1,-1)),list(range(K,2*K))]
  for i in range(K):j=(i+1)%K;F.append([i,j,K+j,K+i])
  solid(f'Chest Corner Upright {sx} {sz}',V,F,bevel=.03)
  # Forged feet flare below their shoulder. The inner lower edges turn in
  # above the bottom rather than receiving a straight diagonal clip.
  rings=[(-2.455,2.745,1.835,1.855,.945),(-2.425,2.765,1.855,1.845,.935),(-2.355,2.775,1.865,1.8425,.9325),(-2.310,2.775,1.865,1.8375,.9275),(-2.265,2.775,1.865,1.8175,.9075),(-2.220,2.775,1.865,1.805,.895),(-2.160,2.775,1.865,1.800,.890),(-1.740,2.725,1.815,1.825,.915),(-1.695,2.715,1.805,1.840,.930),(-1.525,2.690,1.780,2.080,1.170)]
  V=[]
  for y,ox,oz,ix,iz in rings:
   q=chamfer_rect((ox-ix)/2,(oz-iz)/2,.020)
   V.extend(np.c_[(q[:,0]+(ox+ix)/2)*sx,np.full(8,y),(q[:,1]+(oz+iz)/2)*sz])
  solid(f'Chest Angular Boot {sx} {sz}',V,loft_faces(len(rings)),bevel=.014)
  # A thin folded L plate has two planar outer faces. Its shoulder curve
  # belongs to the silhouette, rather than to a receding pyramid surface.
  ox,oz,ix,iz=2.78,1.88,1.98,1.08;c=.040;t=.11
  def crown_h(dist):
   if dist<=.248:return 1.15
   u=min(1,(dist-.248)/.552)
   return 1.15-.27*(.10*u+.90*u**.85)
  q=[]
  for x in np.linspace(ix,ox-c,12):q.append((x,oz,crown_h(ox-x)))
  for a in np.linspace(math.pi/2,0,8)[1:]:q.append((ox-c+c*math.cos(a),oz-c+c*math.sin(a),1.15))
  for z in np.linspace(oz-c,iz,12)[1:]:q.append((ox,z,crown_h(oz-z)))
  q.append((ox-t,iz,.88))
  for z in np.linspace(iz,oz-t,12)[1:]:q.append((ox-t,z,crown_h(oz-z)))
  for x in np.linspace(ox-t,ix,12)[1:]:q.append((x,oz-t,crown_h(ox-x)))
  q=np.array(q);K=len(q);V=np.vstack([np.c_[sx*q[:,0],np.full(K,.53),sz*q[:,1]],np.c_[sx*q[:,0],q[:,2],sz*q[:,1]]]);F=[]
  for i in range(K):j=(i+1)%K;F.append([i,j,K+j,K+i])
  flat=[Vector((float(x),float(z),0)) for x,z,h in q];idx={tuple(v):i for i,v in enumerate(flat)}
  for tri in geometry.tessellate_polygon([flat]):
   ids=[idx[tuple(v)] if hasattr(v,'__iter__') else int(v) for v in tri];F.append(ids[::-1]);F.append([i+K for i in ids])
  solid(f'Chest Lid Corner Armor {sx} {sz}',V,F,bevel=.035)
  V=[]
  for y,w in [(.02,.64),(.085,.76),(.512,.76)]:
   q=chamfer_rect(w/2,w/2,.025);V.extend(np.c_[q[:,0]+sx*2.38,np.full(8,y),q[:,1]+sz*1.48])
  solid(f'Chest Body Corner Collar {sx} {sz}',V,loft_faces(3),bevel=.025)
box('Chest Central Lock Strap',[-.25,-2.17,1.595],[.25,.49,1.800],bevel=.03)
box('Chest Central Lower Cuff',[-.37,lower_rail_bottom,1.780],[.37,lower_rail_top,2.000],hardware,.028)

def ellipsoid(name,c,r):
 bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=20,v_segments=10,radius=1)
 for v in bm.verts:v.co=np.array(c)+np.array(v.co)*r
 for f in bm.faces:f.smooth=True
 return finish(bm,name,hardware,0)
for i,x in enumerate(hoop_x):ellipsoid(f'Chest Crown Fastener Mass {i+1}',[x,2.70,0],[.10,.07,.10])

def cylinder(name,c,r,length,axis='X'):
 bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=40,radius1=r,radius2=r,depth=length);rot=Matrix.Rotation(math.pi/2,3,'Y') if axis=='X' else Matrix.Identity(3)
 for v in bm.verts:v.co=rot@v.co+Vector(c)
 for f in bm.faces:f.smooth=len(f.verts)==4
 return finish(bm,name,hardware,.02)

q=np.array([[-.64,.53],[.64,.53],[.64,.85],[.43,1.06],[-.43,1.06],[-.64,.85]]);K=len(q);V=np.vstack([np.c_[q,np.full(K,z)] for z in [1.76,1.96]]);F=[list(range(K-1,-1,-1)),list(range(K,2*K))]
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
base_outline=np.array([[-.94,.17],[-.40,.17],[-.28,-.18],[.28,-.18],[.40,.17],[.94,.17],[.94,-.26],[.806,-.34],[.742,-.53],[.742,-1.03],[0,-1.667],[-.742,-1.03],[-.742,-.53],[-.806,-.34],[-.94,-.26]],float)
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
shield_outline=np.array([[-.52,-.050],[-.30,-.31],[.30,-.31],[.52,-.050],[.72,-.25],[.64,-.46],[.64,-1.04],[0,-1.56],[-.64,-1.04],[-.64,-.46],[-.72,-.25]],float)
shield_outline[:,1]+=.205
outer=rounded_poly(shield_outline,.025);inner=rounded_poly(offset_outline(shield_outline,.074),.020)
K=len(outer);V=np.vstack([np.c_[q,np.full(K,z)] for q,z in [(outer,1.975),(outer,2.015),(inner,2.115),(inner,1.975)]]);F=[]
for k in range(4):
 for i in range(K):
  j=(i+1)%K;n=(k+1)%4;F.append([k*K+i,k*K+j,n*K+j,n*K+i])
solid('Chest Lock Border With Bore',V,F,hardware,0)
face=rounded_poly(offset_outline(shield_outline,.068),.020)
shield('Chest Shield Lock Plate With Bore',face,2.020,2.107,.008)
# A swept, closed strap bends in front of the shield and meets the hinge.
def bezier4(q,N):
 t=np.linspace(0,1,N)[:,None];q=np.array(q,float)
 return (1-t)**3*q[0]+3*(1-t)**2*t*q[1]+3*(1-t)*t*t*q[2]+t**3*q[3]
# The broad middle of the latch is straight. Only its bottom returns tightly.
upper=bezier4([[0,.72,2.105],[0,.66,2.17],[0,.62,2.17],[0,.55,2.17]],14)
yy=np.linspace(.55,.085,20);q=np.clip((.23-yy)/.145,0,1);zz=2.17-.030*q*q*(3-2*q);middle=np.c_[np.zeros(len(yy)),yy,zz]
a=np.linspace(0,math.pi,32);curl=np.c_[np.zeros(len(a)),.085-.085*np.sin(a),2.055+.085*np.cos(a)]
end=bezier4([[0,.085,1.97],[0,.13,1.97],[0,.18,1.92],[0,.22,1.90]],12)
curve=np.vstack([upper,middle[1:],curl[1:],end[1:]])
tangent=np.gradient(curve,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None];A=np.array([1,0,0]);out=np.cross(tangent,A);out/=np.linalg.norm(out,axis=1)[:,None];V=[]
w=.2525;h=.055;b=.012;profile=[(-w+b,-h),(w-b,-h),(w,-h+b),(w,h-b),(w-b,h),(-w+b,h),(-w,h-b),(-w,-h+b)];K=len(profile)
for p,n in zip(curve,out):
 for x,z in profile:V.append(p+A*x+n*z)
F=[];S=[]
for i in range(len(curve)-1):
 for j in range(K):F.append([i*K+j,i*K+(j+1)%K,(i+1)*K+(j+1)%K,(i+1)*K+j]);S.append(j not in (2,6))
F.extend([list(range(K-1,-1,-1)),list(range((len(curve)-1)*K,len(curve)*K))]);S.extend([False,False]);solid('Chest Curved Hasp Tongue',V,F,hardware,0,S)

for side in (-1,1):
 V=[];F=[]
 for p,n in zip(curve,out):
  for x,z in [(-.010,.053),(.010,.053),(.013,.057),(.013,.066),(.010,.070),(-.010,.070),(-.013,.066),(-.013,.057)]:V.append(p+A*(side*.2335+x)+n*z)
 for i in range(len(curve)-1):
  for j in range(8):F.append([i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j])
 F.extend([list(range(7,-1,-1)),list(range((len(curve)-1)*8,len(curve)*8))]);solid(f'Chest Hasp Edge Rail {side}',V,F,hardware,.004,True)

handle_z=.26
def handle_hood(name,sx,z0,z1,r=.245):
 V=[];F=[];S=[];N=48
 for a in np.linspace(-math.radians(55),math.pi+math.radians(55),N+1):
  for radius,z in [(.125,z0),(r,z0),(r,z1),(.125,z1)]:V.append([sx*(2.88+radius*math.cos(a)),-.20+radius*math.sin(a),z+handle_z])
 for i in range(N):
  for k in range(4):F.append([i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k]);S.append(k in (1,3))
 F.extend([[3,2,1,0],list(range(N*4,N*4+4))]);S.extend([False,False]);return solid(name,V,F,hardware,.025,S)

for sx in (-1,1):
 cx=sx*2.70;box(f'Chest Handle Mount {sx}',[cx-.07,-.48,-.60+handle_z],[cx+.07,.23,.60+handle_z],frame,.045)
 handle_hood(f'Chest Handle Pivot {sx}',sx,-.31,.31)
 V=[];F=[];normals=[];M=32;grooves=[2.40,math.pi,3.88]
 raw=np.sort(np.r_[np.arange(160)*2*math.pi/160,*[g+np.linspace(-.12,.12,25) for g in grooves]])
 us=[float(raw[0])]
 for u in raw[1:]:
  if u-us[-1]>1e-5:us.append(float(u))
 N=len(us)
 def collar_radius(u):
  left=min(1,max(0,(u-2.32)/.07));right=min(1,max(0,(3.96-u)/.07));fade=left*left*(3-2*left)*right*right*(3-2*right)
  return .1109+.0200*fade
 def groove_depth(u):return sum(.0040*math.exp(-((u-g)/.025)**2) for g in grooves)
 for u in us:
  cr=collar_radius(u);dc=(collar_radius(u+.0001)-collar_radius(u-.0001))/.0002;gr=groove_depth(u);dg=(groove_depth(u+.0001)-groove_depth(u-.0001))/.0002
  for j in range(M):
   v=j*2*math.pi/M;sn=math.sin(v);cs=math.cos(v);w=.60+.40*sn**4;dw=1.60*sn**3*cs;tube=cr-gr*w;ru=dc-dg*w;rv=-gr*dw;cu,su=math.cos(u),math.sin(u);L=math.hypot(.64*cu,.525*su);dL=(.525**2-.64**2)*su*cu/L;ny,nz=.64*cu/L,.525*su/L;dny=(-.64*su*L-.64*cu*dL)/L**2;dnz=(.525*cu*L-.525*su*dL)/L**2
   V.append([sx*2.74290000+tube*sn,-0.74714387+.525*cu+tube*cs*ny,.64*su+tube*cs*nz+handle_z])
   du=np.array([ru*sn,-.525*su+ru*cs*ny+tube*cs*dny,.64*cu+ru*cs*nz+tube*cs*dnz]);dv=np.array([rv*sn+tube*cs,(rv*cs-tube*sn)*ny,(rv*cs-tube*sn)*nz]);n=np.cross(du,dv);assert np.linalg.norm(n)>1e-10;n/=np.linalg.norm(n);q=yaw@Vector(n);normals.append((q.x,-q.z,q.y))
 for i in range(N):
  for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
 ob=solid(f'Chest Solid Ring Handle {sx}',V,F,hardware,0,True);ob.data.normals_split_custom_set([normals[l.vertex_index] for l in ob.data.loops])

def cheek(sx,sz):
 a=np.arange(64)*2*math.pi/64
 outline=np.c_[sx*(2.88+.235*np.cos(a)),-.20+.235*np.sin(a)]
 opening=np.c_[sx*(2.88+.124*np.cos(a)),-.276+.134*np.sin(a)]
 coords=np.vstack([outline,opening]);K0=len(outline);edges=[(i,(i+1)%K0) for i in range(K0)]+[(K0+i,K0+(i+1)%len(opening)) for i in range(len(opening))]
 points,ee,ff,*_=geometry.delaunay_2d_cdt([Vector(p) for p in coords],edges,[list(range(K0))],1,1e-7);points=np.array(points);tri=[list(f) for f in ff if not inside(points[list(f)].mean(0),opening)];K=len(points);zc=handle_z+sz*.313;V=np.vstack([np.c_[points,np.full(K,z)] for z in [zc-.029,zc+.029]]);F=tri+[[i+K for i in f[::-1]] for f in tri];counts={}
 for f in tri:
  for u,v in zip(f,np.roll(f,-1)):
   key=tuple(sorted((int(u),int(v))));counts[key]=counts.get(key,0)+1
 for (u,v),n in counts.items():
  if n==1:F.append([u,v,v+K,u+K])
 solid(f'Chest Handle Rolled Cheek {sx} {sz}',V,F,hardware,.016)
for sx in (-1,1):
 for sz in (-1,1):cheek(sx,sz)

for sx in (-1,1):
 x=sx*1.55;box(f'Chest Rear Hinge Lower {sx}',[x-.28,.12,-1.91],[x+.28,.49,-1.75],frame,.03);box(f'Chest Rear Hinge Upper {sx}',[x-.28,.53,-1.91],[x+.28,.91,-1.75],frame,.03);cylinder(f'Chest Rear Hinge Barrel {sx}',[x,.51,-1.93],.12,.60)
# Closed rolled returns, layered pivots and solid construction fasteners.
obsolete=sc.objects.get('Chest Hasp Rolled Return')
if obsolete:obsolete.hide_render=True;obsolete.hide_set(True);obsolete['full_form']=False
for sx in (-1,1):
 profile=[(.245,.168),(.252,.176),(.26,.184),(.27,.187),(.288,.187),(.296,.181),(.307,.181),(.32,.187),(.33,.187),(.338,.184),(.35,.176),(.36,.168)]
 V=[];F=[];NN=64;normals=[];xx=np.array([p[0] for p in profile]);rr=np.array([p[1] for p in profile]);slopes=np.gradient(rr,xx)
 for (x,r),slope in zip(profile,slopes):
  for j in range(NN):
   a=j*2*math.pi/NN;V.append([sx*x,.64+r*math.cos(a),2+r*math.sin(a)]);n=Vector((-sx*slope,math.cos(a),math.sin(a))).normalized();n=yaw@n;normals.append((n.x,-n.z,n.y))
 for k in range(len(profile)-1):
  for j in range(NN):F.append([k*NN+j,k*NN+(j+1)%NN,(k+1)*NN+(j+1)%NN,(k+1)*NN+j])
 F.extend([list(range(NN-1,-1,-1)),list(range((len(profile)-1)*NN,len(profile)*NN))]);ob=solid(f'Chest Hasp Collar Group {sx}',V,F,hardware,0,[True]*(len(F)-2)+[False,False]);me=ob.data;corner=[]
 for face in me.polygons:
  for li in face.loop_indices:corner.append(normals[me.loops[li].vertex_index] if face.use_smooth else tuple(face.normal))
 me.normals_split_custom_set(corner)
 obsolete=sc.objects.get(f'Chest Hasp Pivot Cap {sx}')
 if obsolete:obsolete.hide_render=True;obsolete.hide_set(True);obsolete['full_form']=False
 for sz in (-1,1):
  handle_hood(f'Chest Handle End Collar {sx} {sz}',sx,sz*.278-.035,sz*.278+.035,.257)
  handle_hood(f'Chest Handle Inner Collar {sx} {sz}',sx,sz*.19-.0225,sz*.19+.0225,.249)
 for k in range(3):
  ob=sc.objects.get(f'Chest Handle Lower Sleeve {sx} {k}')
  if ob:ob.hide_render=True;ob.hide_set(True);ob['full_form']=False

def dome(name,p,n,r=.085):
 principal=name.startswith(('Chest Boot','Chest Upper Corner'));hoop=name.startswith('Chest Hoop Rivet');r=r*1.18 if principal else r;r=r*1.25 if hoop else r;depth=.20 if 'Body Lip' in name or 'Body Cuff' in name else (.65 if r<=.085 or hoop else .58)
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
  bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=40,radius1=r*1.08,radius2=r*1.08,depth=.006)
  for v in bm.verts:v.co=rot@v.co+Vector(p)-n*.004
  for f in bm.faces:f.smooth=len(f.verts)==4
  finish(bm,name+' Seat',hardware,.002)
 return ob
# The outside hoops have sparse studding; the two middle hoops have four
# visible fixing heads, including their crown. Mirror only the unseen half.
for i,x in enumerate(hoop_x):
 angles=[.77,1.40] if i in (0,3) else [.245,.565,1.065,math.pi/2]
 if i in (0,3):angles=[.77,math.pi-.77]
 else:angles=angles[:-1]+[math.pi-a for a in angles[:-1]]
 for k,a in enumerate(angles):
  n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n);p=np.array([x,.53+2.05*math.sin(a),1.65*math.cos(a)])+n*.122;dome(f'Chest Hoop Rivet {i} {k}',p,n,.085)
for sx in (-1,1):
 for sz in (-1,1):
  dome(f'Chest Upper Corner Front Rivet {sx} {sz}',[sx*2.38,.72,sz*1.885],[0,0,sz],.105)
  dome(f'Chest Upper Corner End Rivet {sx} {sz}',[sx*2.785,.72,sz*1.48],[sx,0,0],.095)
  dome(f'Chest Boot Front Rivet {sx} {sz}',[sx*2.30,-2.07,sz*1.862],[0,0,sz],.115)
  dome(f'Chest Boot End Rivet {sx} {sz}',[sx*2.772,-2.07,sz*1.40],[sx,0,0],.105)
for sz in (-1,1):
 for j,(x,y,r) in enumerate([(-1.235,.66,.074),(.981,.65,.074),(1.802,.65,.043),(-1.154,lower_rail_mid,.074),(1.097,lower_rail_mid,.074)]):
  dome(f'Chest Rail Rivet {sz} {j}',[x,y,sz*(1.845 if j<3 else 1.785)],[0,0,sz],r)
 for j,x in enumerate([-1.758,1.402]):dome(f'Chest Body Lip Rivet {sz} {j}',[x,.331,sz*1.785],[0,0,sz],.0375)
for sx in (-1,1):
 for k,y in enumerate([.69,lower_rail_mid]):dome(f'Chest End Rail Rivet {sx} {k}',[sx*(2.775 if k==0 else 2.735),y,.13],[sx,0,0],.074)
 for sz in (-1,1):dome(f'Chest Handle Mount Rivet {sx} {sz}',[sx*2.775,.025,handle_z+sz*.48],[sx,0,0],.062)
for j,(x,y,r) in enumerate([(-.73,-.02,.105),(.73,-.02,.105),(-.43,-.45,.058),(.43,-.45,.058),(-.43,-1.02,.058),(.43,-1.02,.058),(0,-1.31,.058)]):dome(f'Chest Lock Rivet {j}',[x,y+.205,2.0 if j<2 else 2.108],[0,0,1],r)
dome('Chest Lower Strap Rivet',[0,lower_rail_mid,2.005],[0,0,1],.105)
# Faceted studs are separate metal solids with finished backs.
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*2.48;y=(.02-1.525)/2;z=sz*1.770;V=[(x-.10,y,z),(x,y+.22,z),(x+.10,y,z),(x,y-.22,z),(x,y,z+sz*.095),(x,y,z-sz*.025)];F=[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[1,0,5],[2,1,5],[3,2,5],[0,3,5]];solid(f'Chest Upright Diamond {sx} {sz}',V,F,hardware,.008)
# End arch fixing heads sit on the end face, not on the curved hoop surface.
for sx in (-1,1):
 for k,a in enumerate([.78,math.pi-.78]):
  n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n);p=np.array([sx*2.758,.53+2.05*math.sin(a),1.65*math.cos(a)])-n*.160;dome(f'Chest End Arch Rivet {sx} {k}',p,[sx,0,0],.096)
 for sz in (-1,1):
  dome(f'Chest Corner Body Cuff Front Rivet {sx} {sz}',[sx*2.38,.28,sz*1.835],[0,0,sz],.0425)
  dome(f'Chest Corner Body Cuff End Rivet {sx} {sz}',[sx*2.735,.28,sz*1.48],[sx,0,0],.0425)

for sx in (-1,1):
 dome(f'Chest Hasp Pivot Dome {sx}',[sx*.348,.64,2.00],[sx,0,0],.090)
 dome(f'Chest Hasp Mount Fastener {sx}',[sx*.525,.66,1.965],[0,0,1],.075)
 # Folded crown tab crosses the top and descends down the end arch.
 q=[(2.50,2.715),(2.65,2.715)]
 for a in np.linspace(math.pi/2,0,16)[1:]:q.append((2.65+.155*math.cos(a),2.56+.155*math.sin(a)))
 q.extend([(2.805,2.238),(2.735,2.238),(2.735,2.56)])
 for a in np.linspace(0,math.pi/2,16)[1:]:q.append((2.65+.085*math.cos(a),2.56+.085*math.sin(a)))
 q.append((2.50,2.645));q=np.array(q);K=len(q);V=np.vstack([np.c_[sx*q[:,0],q[:,1],np.full(K,z)] for z in [-.152,.152]]);F=[list(range(K-1,-1,-1)),list(range(K,2*K))]
 for i in range(K):j=(i+1)%K;F.append([i,j,K+j,K+i])
 solid(f'Chest End Arch Crown Tab {sx}',V,F,frame,.030)
 dome(f'Chest End Crown Fastener {sx}',[sx*2.808,2.43,0],[sx,0,0],.070)
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
exec(compile((P/'tools/measured_hardware18_live.py').read_text(),'measured_hardware18_live.py','exec'))
exec(compile((P/'tools/arch19_live.py').read_text(),'arch19_live.py','exec'))
exec(compile((P/'tools/tab20_live.py').read_text(),'tab20_live.py','exec'))
HANDLE21_DEFINE_ONLY=True
exec(compile((P/'tools/handle21_live.py').read_text(),'handle21_live.py','exec'))
HANDLE21_DEFINE_ONLY=False
exec(compile((P/'tools/handle24_live.py').read_text(),'handle24_live.py','exec'))
exec(compile((P/'tools/check_thickness24_live.py').read_text(),'check_thickness24_live.py','exec'))
# Correct the slightly tall proportions without expanding the hard turning envelope.
# Always starts from the immutable core and regenerated hardware, never compounds.
for ob in sc.objects:
 if ob.type=='MESH' and ob.get('full_form'):
  me=ob.data;me.update();normals=np.array([n.vector[:] for n in me.corner_normals])
  for v in me.vertices:v.co.z=-2.455+(v.co.z+2.455)*.95
  normals[:,2]/=.95;normals/=np.linalg.norm(normals,axis=1)[:,None];me.update();me.normals_split_custom_set(normals.tolist())
exec(compile((P/'tools/mechanism29_live.py').read_text(),'mechanism26_live.py','exec'))
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
