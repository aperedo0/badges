assert 'Status: APPROVED (review round 1).' in (P/'arch20/PLAN.md').read_text()
def crown_strap20(sx):
 q=[]
 for x in np.linspace(2.500,2.560,13):
  t=(x-2.500)/.060;r=.179+(.218-.179)*t*t*(3-2*t);q.append([x,r])
 q.append([2.670,.218])
 for a in np.linspace(math.pi/2,0,17)[1:]:q.append([2.670+.123*math.cos(a),.095+.123*math.sin(a)])
 q.extend([[2.793,-.375],[2.753,-.377],[2.753,.095]])
 inner_start=len(q)-1
 for a in np.linspace(0,math.pi/2,17)[1:]:q.append([2.670+.083*math.cos(a),.095+.083*math.sin(a)])
 q.append([2.500,.178]);q=np.array(q);K=len(q);W=16;V=[];F=[];S=[];contact=[]
 for u in np.linspace(0,1,W+1):
  for x,r in q:
   bottom_r=-.377+.002*float(np.clip((x-2.753)/.040,0,1));t=float(np.clip((.095-r)/(.095-bottom_r),0,1));z0=-.142*(1-t)-.033*t;z1=.322*(1-t)+.255*t;z=z0+u*(z1-z0)
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
  r=-.140;t=(.095-r)/.472;z0=-.142*(1-t)-.033*t;z1=.322*(1-t)+.255*t;z=z0+u*(z1-z0);y=y_at(z,r)
  p=yaw@Vector((sx*2.70,y,z));n=yaw@Vector((sx,0,0));p=Vector((p.x,-p.z,p.y));n=Vector((n.x,-n.z,n.y));hit,pt,nn,idx=ob.ray_cast(p,n)
  assert hit,(ob.name,'missing hanging underside',u)
  local=yaw.inverted()@Vector((pt.x,pt.z,-pt.y));assert abs(abs(local.x)-2.753)<.001,(ob.name,'face contact',local.x)
 dome(f'Chest End Crown Fastener {sx}',[sx*2.795,y_at(.051,-.140),.051],[sx,0,0],.083)
 return dict(top_contact_min=min(checks),top_contact_max=max(checks),width_samples=17,face_seated=True,bottom_front_offset=-.375,bottom_back_offset=-.377)

checks20=[dict(side=sx,strap=crown_strap20(sx)) for sx in (-1,1)]
(C/'crown20_contact.json').write_text(json.dumps(checks20,indent=2))
print('Built compact crown folds with buried tapered return ends and visible inner edge alignment.')

(C/'arch19_intermediate_contact.json').write_text((C/'arch_contact.json').read_text())
(C/'arch_contact.json').write_text(json.dumps(checks20,indent=2))
