# Dynamic demonstration key, excluded from the closed static badge export.
assert 'Status: APPROVED (review round 1).' in (P/'mechanism30/PLAN.md').read_text()
KY30=-.536
key=cylinder25('Chest Removable Crank Key',(0,KY30,(1.900+2.500)/2),.035,2.500-1.900,axis='Z',bevel=.002);key['allowed_euler']=[2]
for name,r,z0,z1 in [('Key guiding pilot',.150,2.030,2.117),('Key actual face stop',.180,2.107,2.135)]:
 part=cylinder25(name,(0,KY30,(z0+z1)/2),r,z1-z0,axis='Z',bevel=.003);union_handle21(key,part,name+' connected')
arm=box('Key actual offset crank arm',[-.028,KY30-.145,1.880],[.028,KY30+.015,1.925],hardware,.002);union_handle21(key,arm,'Key offset arm actual attachment')
bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=192,radius1=.025,radius2=.025,depth=.060)
for v in bm.verts:v.co+=Vector((0,KY30-.140,(1.835+1.895)/2))
for f in bm.faces:f.smooth=len(f.verts)==4
pin=finish(bm,'Removable key actual rear crank',hardware,.001);union_handle21(key,pin,'Removable crank actual arm union')
V=[];F=[];N=96;M=16
for i in range(N):
 u=i*2*math.pi/N;p=np.array([0,KY30+.125*math.sin(u),2.620+.160*math.cos(u)]);t=np.array([0,.125*math.cos(u),-.160*math.sin(u)]);t/=np.linalg.norm(t);n=np.cross(t,[1,0,0]);n/=np.linalg.norm(n)
 for j in range(M):v=j*2*math.pi/M;V.append(p+.020*(np.array([1,0,0])*math.cos(v)+n*math.sin(v)))
for i in range(N):
 for j in range(M):F.append([i*M+j,i*M+(j+1)%M,((i+1)%N)*M+(j+1)%M,((i+1)%N)*M+j])
bow=solid('Key actual open ring bow',V,F,hardware,0,True);bow['allowed_euler']=[0];prove_part(bow,'Key open ring')
key['allowed_euler']=[0,2];union_handle21(key,bow,'Key bow actual shaft union');key['allowed_euler']=[0];prove_part(key,'Complete connected removable key')
key['dynamic_mechanism_only']=True;key['full_form']=False;key.hide_render=True;key.hide_set(True)
(C/'key_geometry.json').write_text(json.dumps(dict(name=key.name,connected=True,closed=True,intended_euler=0,excluded_from_closed_static_export=True,hidden_at_locked_rest=True,actual_crank_segments=192,insertion_test_complete=False,full_turn_test_complete=False,actual_geometry_proof=proof[-1]),indent=2))
stage=json.loads((C/'internal_stage.json').read_text());stage.update(key_built=True,stage='Actual slider, guides and removable crank key saved; spring detent and driven controls pending',remaining=['Real leaf detent and compliant contact','Actual pilot and crank insertion proof','Quarter turn contact controls','Relative motion proof and actual key absent appearance']);(C/'internal_stage.json').write_text(json.dumps(stage,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved real connected removable crank key; hidden at rest and excluded from closed export. Motion tests pending.')
