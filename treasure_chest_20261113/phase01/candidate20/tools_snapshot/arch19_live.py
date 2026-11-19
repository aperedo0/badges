# Executed in the existing live builder before its single height conversion.
assert 'Status: APPROVED (review round 1).' in (P/'arch19/PLAN.md').read_text()

def cap_indices(poly):
 vv=[Vector((float(x),float(y),0)) for x,y in poly]
 lookup={tuple(v):i for i,v in enumerate(vv)}
 return [[lookup[tuple(v)] if hasattr(v,'__iter__') else int(v) for v in tri] for tri in geometry.tessellate_polygon([vv])]

def ellipse(a):
 p=np.array([0,.53+2.05*math.sin(a),1.65*math.cos(a)])
 n=np.array([0,math.sin(a)/2.05,math.cos(a)/1.65]);n/=np.linalg.norm(n)
 return p,n

def y_at(z,r):
 aa=np.linspace(.9,2.25,2049)
 yy=.53+2.05*np.sin(aa);zz=1.65*np.cos(aa)
 ny=np.sin(aa)/2.05;nz=np.cos(aa)/1.65;l=np.hypot(ny,nz)
 yy+=r*ny/l;zz+=r*nz/l
 return float(np.interp(z,zz[::-1],yy[::-1]))

def continuous_arch(sx):
 q=[[2.160,-.012],[2.550,-.012],[2.550,-.400],[2.730,-.400],[2.755,-.375],[2.755,.095]]
 first=len(q)-1
 for a in np.linspace(0,math.pi/2,13)[1:]:q.append([2.670+.085*math.cos(a),.095+.085*math.sin(a)])
 last=len(q)-1;q.extend([[2.185,.180],[2.160,.155]])
 q=np.array(q);K=len(q);N=128;V=[];F=[]
 for a in np.linspace(0,math.pi,N+1):
  p,n=ellipse(a)
  for x,r in q:V.append([sx*x,p[1]+r*n[1],p[2]+r*n[2]])
 for i in range(N):
  for k in range(K):F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k])
 for tri in cap_indices(q):F.append(tri[::-1]);F.append([N*K+i for i in tri])
 ob=solid(f'Chest Broad End Arch {sx}',V,F,frame,0,[True]*(N*K)+[False]*(len(F)-N*K))
 sign=1 if np.cross(q,np.roll(q,-1,axis=0)).sum()>0 else -1
 normals=[]
 for face in ob.data.polygons:
  if face.index>=N*K:
   normals.extend([tuple(face.normal)]*len(face.loop_indices));continue
  k=face.index%K
  edge=q[(k+1)%K]-q[k];normal2=sign*np.array([edge[1],-edge[0]]);normal2/=np.linalg.norm(normal2)
  for li in face.loop_indices:
   vi=ob.data.loops[li].vertex_index;row,c=divmod(vi,K);a=row*math.pi/N;p,n=ellipse(a)
   if first<=k<last:
    nn=(q[c]-[2.670,.095])/.085
   else:nn=normal2
   normal=yaw@Vector((sx*nn[0],n[1]*nn[1],n[2]*nn[1]));normals.append((normal.x,-normal.z,normal.y))
 ob.data.normals_split_custom_set(normals)
 prove_part(ob,ob.name+' continuous arch and wrapping band')
 ob['arch19_continuous']=True
 hide_part(sc.objects[f'Chest Lid Hoop {1 if sx<0 else 4}'])
 return ob

def crown_strap(sx):
 q=[[2.500,.248],[2.670,.248]]
 for a in np.linspace(math.pi/2,0,17)[1:]:q.append([2.670+.153*math.cos(a),.095+.153*math.sin(a)])
 q.extend([[2.823,-.400],[2.753,-.400],[2.753,.095]])
 inner_start=len(q)-1
 for a in np.linspace(0,math.pi/2,17)[1:]:q.append([2.670+.083*math.cos(a),.095+.083*math.sin(a)])
 q.append([2.500,.178]);q=np.array(q);K=len(q);W=16;V=[];F=[];S=[];contact=[]
 for u in np.linspace(0,1,W+1):
  for x,r in q:
   t=float(np.clip((.095-r)/.495,0,1));z0=-.142*(1-t)-.033*t;z1=.322*(1-t)+.255*t;z=z0+u*(z1-z0)
   V.append([sx*x,y_at(z,r),z])
 for i in range(W):
  for k in range(K):
   F.append([i*K+k,i*K+(k+1)%K,(i+1)*K+(k+1)%K,(i+1)*K+k]);S.append(True)
   contact.append(k>=inner_start or k==inner_start-1)
 for tri in cap_indices(q):
  F.append(tri[::-1]);S.append(False);contact.append(False)
  F.append([W*K+i for i in tri]);S.append(False);contact.append(False)
 # Bevel only exposed edges. Mating surfaces retain the full contact seat.
 bm=bmesh.new();vv=[bm.verts.new(tuple(v)) for v in V];layer=bm.faces.layers.int.new('Contact seat')
 for f,s,c in zip(F,S,contact):
  face=bm.faces.new([vv[i] for i in f]);face.smooth=s;face[layer]=int(c)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle(0)>math.radians(25) and not any(f[layer] for f in e.link_faces)]
 result=bmesh.ops.bevel(bm,geom=edges,offset=.010,segments=3,profile=.5,affect='EDGES',clamp_overlap=True)
 for face in result['faces']:face.smooth=True
 ob=finish(bm,f'Chest End Arch Crown Tab {sx}',frame,0)
 prove_part(ob,ob.name+' fitted crown strap')
 # Test the actual completed underside across the entire draped width.
 checks=[]
 for u in np.linspace(.0001,.9999,17):
  z=-.142+u*.464;y=y_at(z,.180);p=yaw@Vector((sx*2.55,y-.08,z));direction=yaw@Vector((0,1,0));origin=Vector((p.x,-p.z,p.y));direction=Vector((direction.x,-direction.z,direction.y))
  hit,pt,nn,idx=ob.ray_cast(origin,direction)
  assert hit,(ob.name,'missing top underside',u)
  local=yaw.inverted()@Vector((pt.x,pt.z,-pt.y));burial=y-local.y
  assert -.0003<burial<.005,(ob.name,'top contact',u,burial)
  checks.append(float(burial))
 for u in np.linspace(.0001,.9999,17):
  r=-.1525;t=(.095-r)/.495;z0=-.142*(1-t)-.033*t;z1=.322*(1-t)+.255*t;z=z0+u*(z1-z0);y=y_at(z,r)
  p=yaw@Vector((sx*2.70,y,z));n=yaw@Vector((sx,0,0));p=Vector((p.x,-p.z,p.y));n=Vector((n.x,-n.z,n.y));hit,pt,nn,idx=ob.ray_cast(p,n)
  assert hit,(ob.name,'missing hanging underside',u)
  local=yaw.inverted()@Vector((pt.x,pt.z,-pt.y));assert abs(abs(local.x)-2.753)<.001,(ob.name,'face contact',local.x)
 dome(f'Chest End Crown Fastener {sx}',[sx*2.825,y_at(.051,-.1525),.051],[sx,0,0],.083)
 return dict(top_contact_min=min(checks),top_contact_max=max(checks),width_samples=17,face_seated=True,bottom_offset=-.400)

arch19_checks=[]
for sx in (-1,1):
 continuous_arch(sx);arch19_checks.append(dict(side=sx,strap=crown_strap(sx)))
 for k,a in enumerate([.78,math.pi-.78]):
  p,n=ellipse(a);p+=n*(-.140);p[0]=sx*2.758;dome(f'Chest End Arch Rivet {sx} {k}',p,[sx,0,0],.096)
for i in (1,2):arch(f'Chest Lid Hoop {i+1}',hoop_x[i],.48,-.012,.180)
for i,x in enumerate(hoop_x):
 angles=[.77,math.pi-.77] if i in (0,3) else [.245,.565,1.065]+[math.pi-a for a in [.245,.565,1.065]]
 for k,a in enumerate(angles):
  p,n=ellipse(a);p+=n*.182;p[0]=x;dome(f'Chest Hoop Rivet {i} {k}',p,n,.085)
 # Existing crown fixing heads sit on the increased band surface.
 ellipsoid(f'Chest Crown Fastener Mass {i+1}',[x,2.76,0],[.10,.07,.10])
(C/'arch_contact.json').write_text(json.dumps(arch19_checks,indent=2))
print('Built single surface end arches and fitted full depth crown straps; contact sampled across both widths.')
