assert 'Status: APPROVED (review round 1).' in (P/'handle23/PLAN.md').read_text()
def ring23(sx):
 V=[];F=[];normals=[];M=32;grooves=[2.40,math.pi,3.88]
 raw=np.sort(np.r_[np.arange(160)*2*math.pi/160,*[g+np.linspace(-.12,.12,25) for g in grooves],*[g+np.array([-.024,-.008,0,.008,.024]) for g in grooves],2.15+np.linspace(0,.06,5),4.13-np.linspace(0,.06,5)])
 us=[float(raw[0])]
 for u in raw[1:]:
  if u-us[-1]>1e-5:us.append(float(u))
 N=len(us)
 def radius_and_derivative(u):
  a=(u-2.15)/.06;b=(4.13-u)/.06
  sm=lambda q:0 if q<=0 else 1 if q>=1 else q*q*(3-2*q)
  ds=lambda q:0 if q<=0 or q>=1 else 6*q*(1-q)
  cr=.1109+.0180*sm(a)*sm(b)
  dc=.0180*(ds(a)*sm(b)-sm(a)*ds(b))/.06
  gr=dg=0
  for g in grooves:
   d=abs(u-g)
   if d<=.008:gr+=.009
   elif d<.024:
    q=(d-.008)/.016;gr+=.009*(1-sm(q));dg-=.009*ds(q)/.016*(1 if u>g else -1)
  return cr,dc,gr,dg

 for u in us:
  cr,dc,gr,dg=radius_and_derivative(u)
  for j in range(M):
   v=j*2*math.pi/M;sn=math.sin(v);cs=math.cos(v);w=.60+.40*sn**4;dw=1.60*sn**3*cs;tube=cr-gr*w;ru=dc-dg*w;rv=-gr*dw;cu,su=math.cos(u),math.sin(u);L=math.hypot(.64*cu,.525*su);dL=(.525**2-.64**2)*su*cu/L;ny,nz=.64*cu/L,.525*su/L;dny=(-.64*su*L-.64*cu*dL)/L**2;dnz=(.525*cu*L-.525*su*dL)/L**2
   V.append([sx*2.93000000+tube*sn,-0.74714387+.525*cu+tube*cs*ny,.64*su+tube*cs*nz+handle_z])
   du=np.array([ru*sn,-.525*su+ru*cs*ny+tube*cs*dny,.64*cu+ru*cs*nz+tube*cs*dnz]);dv=np.array([rv*sn+tube*cs,(rv*cs-tube*sn)*ny,(rv*cs-tube*sn)*nz]);n=np.cross(du,dv);assert np.linalg.norm(n)>1e-10;n/=np.linalg.norm(n);q=yaw@Vector(n);normals.append((q.x,-q.z,q.y))
 for i in range(N):
  for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
 ob=solid(f'Chest Solid Ring Handle {sx}',V,F,hardware,0,True);ob.data.normals_split_custom_set([normals[l.vertex_index] for l in ob.data.loops])

def supported_cover23(sx):
 arc=np.array(MP['handle_section_outer'])[:48].copy();arc[:,0]+=.1871
 q=np.vstack([[2.795,arc[0,1]],arc,[2.795,arc[-1,1]]]);qi=offset_outline(q,.012);K=len(q)
 rows=[(handle_z-.310,0,True),(handle_z-.298,0,False)]
 for center in [handle_z-.135,handle_z+.135]:rows.extend([(center+d,w,False) for d,w in [(-.015,0),(-.012,.5),(-.009,1),(.009,1),(.012,.5),(.015,0)]])
 rows.extend([(handle_z+.298,0,False),(handle_z+.310,0,True)]);rows.sort();V=[];F=[];S=[];center=np.array([2.681084921+.1871,-.228049008])
 for z,depth,cap in rows:
  loop=(qi if cap else q).copy()
  for k in range(1,49):
   direction=loop[k]-center;direction/=np.linalg.norm(direction);loop[k]-=direction*depth*.010
  V.extend(np.c_[sx*loop[:,0],loop[:,1],np.full(K,z)])
 for i in range(len(rows)-1):
  for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(True)
 for tri in cap_indices(qi):F.append(tri[::-1]);S.append(False);F.append([(len(rows)-1)*K+j for j in tri]);S.append(False)
 ob=solid(f'Chest Measured Rolled Handle Cover {sx}',V,F,hardware,0,S);ob['allowed_euler']=[0,2];prove_part(ob,'Single supported rolled cover')
 ring=sc.objects[f'Chest Solid Ring Handle {sx}'];rm=ring.data;rm.update();inv=yaw.inverted();norm={}
 for loop in rm.loops:
  if loop.vertex_index not in norm:norm[loop.vertex_index]=rm.corner_normals[loop.index].vector.copy()
 VV=[]
 for i,v in enumerate(rm.vertices):
  q0=inv@Vector((v.co.x,v.co.z,-v.co.y));n=norm[i];n0=inv@Vector((n.x,n.z,-n.y));VV.append(tuple(q0+n0*.012))
 cutter=solid('Actual ring root cutter 23',VV,[list(f.vertices) for f in rm.polygons],hardware,0,True);cutter['allowed_euler']=[0]
 union_handle21(ob,cutter,'Supported rolled cover root opening','DIFFERENCE')
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);wn=ob.modifiers.new('Supported cover curve normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=40;bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 return ob

checks23=[]
for sx in (-1,1):
 ring23(sx)
 plate=box(f'Chest Handle Mount {sx}',[min(sx*2.545,sx*2.810),-.635,-.320],[max(sx*2.545,sx*2.810),.105,1.120],frame,.025)
 cover=supported_cover23(sx) if sx<0 else mirror_cover21()
 for i,z in enumerate([-.202,.916]):dome(f'Chest Handle Mount Rivet {sx} {-1 if i==0 else 1}',[sx*2.815,-.040,z],[sx,0,0],.070)
 ring=sc.objects[f'Chest Solid Ring Handle {sx}'];v=local_vertices(ring);mask=(v[:,1]>=-.635)&(v[:,1]<=.105)&(v[:,2]>=-.320)&(v[:,2]<=1.120);clearance=float((v[mask,0]*sx-2.810).min());assert clearance>=.004
 assert not bvh(ring).overlap(bvh(plate));assert not bvh(ring).overlap(bvh(cover))
 seat=[]
 for y in [-.020,-.200,-.440]:
  for z in [handle_z-.20,handle_z,handle_z+.20]:
   p=yaw@Vector((sx*2.780,y,z));n=yaw@Vector((sx,0,0));p=Vector((p.x,-p.z,p.y));n=Vector((n.x,-n.z,n.y));hit,point,nn,index=cover.ray_cast(p,n);assert hit
   local=yaw.inverted()@Vector((point.x,point.z,-point.y));assert abs(local.x)<=2.810;seat.append(abs(float(local.x)))
 for i,z in enumerate([-.202,.916]):
  p=yaw@Vector((sx*3,-.040,z));n=yaw@Vector((-sx,0,0));p=Vector((p.x,-p.z,p.y));n=Vector((n.x,-n.z,n.y));hit,point,nn,index=plate.ray_cast(p,n);assert hit
  local=yaw.inverted()@Vector((point.x,point.z,-point.y));assert abs(abs(local.x)-2.810)<1e-5
 checks23.append(dict(side=sx,plate_ring_min_gap=clearance,root_clear=True,full_rear_web_seats=seat,heads_seated=True))
(C/'handle_contact.json').write_text(json.dumps(checks23,indent=2));print('Built supported curved covers without rectangular rear notches and softer sleeve shoulders and defined central divisions.')

