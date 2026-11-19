assert 'Status: APPROVED (review round 1).' in (P/'mechanism31/PLAN.md').read_text()
detent_pocket_center_y=-.177;detent_pocket_segments=192
exec(compile((P/'tools/mechanism30_live.py').read_text(),'mechanism30_live.py','exec'))
# The leaf root and rigid round nose are actual connected geometry.
V=[];F=[];N31=64
for i in range(N31+1):
 s=i/N31;sm=s*s*(3-2*s);der=6*s*(1-s);p=np.array([.300-.200*s,-.145-.029*sm,1.8425]);t=np.array([-.200,-.029*der,0]);t/=np.linalg.norm(t);up=np.array([t[1],-t[0],0])
 for thick,z in [(-.002,-.007),(.002,-.007),(.002,.007),(-.002,.007)]:V.append(p+up*thick+[0,0,z])
for i in range(N31):
 for k in range(4):F.append([i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k])
F.extend([list(range(3,-1,-1)),list(range(N31*4,(N31+1)*4))]);leaf=solid('Chest Compliant Catch Leaf',V,F,hardware,0,True);leaf['allowed_euler']=[2];prove_part(leaf,'Closed detent leaf')
bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=192,radius1=.008,radius2=.008,depth=.019)
for v in bm.verts:v.co+=Vector((.100,-.1785,1.8425))
for f in bm.faces:f.smooth=len(f.verts)==4
nose=finish(bm,'Actual rounded spring nose',hardware,0);union_handle21(leaf,nose,'Spring nose physical leaf attachment');prove_part(leaf,'Connected spring leaf and nose')
anchor=box('Chest Fixed Leaf Clamp',[.290,-.150,1.810],[.320,-.135,1.850],hardware,.001);prove_part(anchor,'Fixed leaf clamp')
leaf['chest_mechanism_rig_part']=True
if leaf.data.shape_keys:leaf.shape_key_clear()
leaf.shape_key_add(name='Basis');deform=leaf.shape_key_add(name='Actual spring lift')
weights=[];base=coords25(leaf)
for i,p in enumerate(base):
 s=np.clip(((.300-p[0])/.200-.10)/.80,0,1);weight=float(s*s*(3-2*s));weights.append(weight);q=yaw@Vector((0,.002*weight,0));deform.data[i].co+=Vector((q.x,-q.z,q.y))
deform.value=0
(C/'spring_geometry.json').write_text(json.dumps(dict(nose_radius=.008,nose_free_center=[.100,-.1785,1.8425],pocket_center=[.100,-.177,1.845],pocket_radius=.010,segments=192,max_shape_lift=.002,fixed_root_vertices=sum(w==0 for w in weights),rigid_tip_vertices=sum(w==1 for w in weights),connected_spring=True,actual_motion_proof_complete=False),indent=2))
exec(compile((P/'tools/rig31_live.py').read_text(),'rig31_live.py','exec'))
if not globals().get('DEFER_CHEST_SAVE',False):bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved real shallow detent leaf, rigid nose and explicit key catch controls. Whole motion proof pending.')
