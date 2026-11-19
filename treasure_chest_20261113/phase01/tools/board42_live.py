import bpy,numpy as np,math,json,hashlib,shutil,time
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';B=P/'candidate41';C=P/'candidate42';PLAN=R/'phase02/boards42';sc=bpy.context.scene
assert 'Status: APPROVED' in (PLAN/'PLAN.md').read_text()
assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty and sc.frame_current==0,'Unknown scene or unsaved changes'
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and not policy['owner_paused_badge_work'] and not policy['material_finish_authorized'] and not policy['wood_grain_authorized']
assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest()==hashlib.sha256((B/'chest.blend').read_bytes()).digest()
exec(compile((P/'tools/frame36_geometry.py').read_text(),'geometry36','exec'));exec(compile((P/'tools/hinge38_geometry.py').read_text(),'geometry38','exec'));C.mkdir(exist_ok=True);D=json.loads((PLAN/'design.json').read_text());targets=['Chest Body Envelope','Chest Barrel Lid Envelope'];objects=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(objects)==155;before={o.name:capture36(o) for o in objects};keybefore=capture36(sc.objects['Chest Removable Crank Key']);sources={n:[before[n]] for n in targets};stages={n:[] for n in targets};specs=[];start=time.time()
base=np.load(B/'geometry.npz');rows=json.loads((B/'validation.json').read_text())['checks']
for i,row in enumerate(rows):
 d=before[row['name']];assert np.array_equal(np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]],base[f'part{i}_v']);assert np.array_equal(d['t'],base[f'part{i}_t'])
frozen={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in B.rglob('*') if f.is_file()};(C/'baseline41_hashes.json').write_text(json.dumps(frozen,indent=2))
# Read only the two original mesh datablocks, without loading the older scene.
uncut={};source_names={n:sc.objects[n].data.name for n in targets}
with bpy.data.libraries.load(str(P/'candidate40/chest.blend'),link=False) as (library,loaded):
 assert all(name in library.meshes for name in source_names.values()),source_names
 loaded.meshes=list(source_names.values())
raw_reference=np.load(B/'wood_before.npz');holders=[]
for name,me in zip(targets,loaded.meshes):
 holder=bpy.data.objects.new('Chest Original Wood Source42 '+name,me);holder['development_only']=True;holder['full_form']=False;holder.hide_render=True;holders.append(holder);d=capture36(holder)
 assert np.array_equal(d['v'],raw_reference[name+' v']) and np.array_equal(d['t'],raw_reference[name+' t']),(name,'not exact original wood')
 uncut[name]=d;mesh36(sc.objects[name],d,sc.objects[name].data.materials[0])
sources={n:[uncut[n]] for n in targets}
np.savez_compressed(C/'wood_before.npz',**{n+' '+k:uncut[n][k] for n in targets for k in ('v','t','tn')})

def prism41(name,p,n,t,along,extent,material):
 p=np.array(p,float);n=np.array(n,float);n/=np.linalg.norm(n);t=np.array(t,float);t/=np.linalg.norm(t);along=np.array(along,float);assert abs(n@t)<1e-10 and abs(n@along)<1e-10 and abs(t@along)<1e-10
 h=D['groove_face_width']/2*(D['groove_depth']+D['cutter_outward'])/D['groove_depth'];profile=[p-D['groove_depth']*n,p+D['cutter_outward']*n-h*t,p+D['cutter_outward']*n+h*t];v=np.array([q+s*extent*along for s in (-1,1) for q in profile]);faces=[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]];normals=[]
 for i,f in enumerate(faces):
  g=np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]);g/=np.linalg.norm(g)
  if np.dot(g,v[f].mean(0)-v.mean(0))<0:faces[i]=f[::-1];g=-g
  normals.append([g.tolist()]*len(f))
 return solid38(name,v,faces,normals,material)

def add41(target,label,p,n,t,along,extent):
 ob=sc.objects[target];cut=prism41('Chest Wood Joint Tool42 '+label,p,n,t,along,extent,ob.data.materials[0]);sources[target].append(negative38(capture36(cut)));stages[target].append(boolean38(ob,cut,'DIFFERENCE'));specs.append(dict(target=target,label=label,p=list(p),n=list(n),t=list(t)));(C/'build_progress.json').write_text(json.dumps(dict(completed=[s['label'] for s in specs],seconds=time.time()-start),indent=2))

for i,y in enumerate(D['body_levels']):
 for side in (-1,1):
  add41(targets[0],f'body front {i} {side}',[0,y,side*1.60],[0,0,side],[0,1,0],[1,0,0],2.35)
  add41(targets[0],f'body end {i} {side}',[side*2.55,y,0],[side,0,0],[0,1,0],[0,0,1],1.40)
for i in range(1,D['roof_staves']):
 a=i*math.pi/D['roof_staves'];p=[0,.38075+1.9475*math.sin(a),1.65*math.cos(a)];n=np.array([0,math.sin(a)/1.9475,math.cos(a)/1.65]);n/=np.linalg.norm(n);t=np.array([0,1.9475*math.cos(a),-1.65*math.sin(a)]);t/=np.linalg.norm(t);add41(targets[1],f'roof {i}',p,n,t,[1,0,0],2.36)
for i,y in enumerate(D['end_levels']):
 for side in (-1,1):add41(targets[1],f'lid end {i} {side}',[side*2.60,y,0],[side,0,0],[0,1,0],[0,0,1],1.80)
normalproof={};after={}
for name in targets:
 ob=sc.objects[name];proof=topology36(ob);assert proof['euler']==2;oldV=uncut[name]['v'];oldT=uncut[name]['t'];oldvol=float(np.einsum('ij,ij->i',oldV[oldT[:,0]],np.cross(oldV[oldT[:,1]],oldV[oldT[:,2]])).sum()/6);removed=oldvol-proof['volume'];assert 0<removed<.03*oldvol,(name,'wrong removed volume',removed,oldvol)
 field=source_field36(sources[name]);tr=transfer36(ob,field);np.savez_compressed(C/(('body' if name==targets[0] else 'lid')+'_normal_targets.npz'),normals=tr.pop('loop_targets'));normalproof[name]=dict(**tr,removed_volume=removed,original_volume=oldvol,proof=proof);after[name]=capture36(ob)

def ray41(d,p,ray):
 tri=local38(d['v'])[d['t']];p=np.asarray(p);ray=np.asarray(ray);E=tri[:,1]-tri[:,0];F=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(ray,F.shape),F);det=np.einsum('ij,ij->i',E,h);ok=abs(det)>1e-13;inv=np.divide(1.,det,out=np.zeros_like(det),where=ok);S=p-tri[:,0];u=np.einsum('ij,ij->i',S,h)*inv;Q=np.cross(S,E);v=Q@ray*inv;distance=np.einsum('ij,ij->i',F,Q)*inv;hit=ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(distance>1e-7);assert hit.any(),('missing surface',p,ray);return float(distance[hit].min())
# Body joint ends stop beneath actual metal posts, avoiding unnecessary corner intersections.
end_cover=[]
for sx in (-1,1):
 for sz in (-1,1):
  post=before[f'Chest Corner Upright {sx} {sz}']
  for y in D['body_levels']:
   for dy in (-.07,0,.07):
    for p,n,kind in [([sx*2.35,y+dy,sz*1.60],[0,0,sz],'front'),([sx*2.55,y+dy,sz*1.40],[sx,0,0],'end')]:
     p=np.array(p,float);n=np.array(n,float);distance=ray41(post,p+.30*n,-n);assert distance<.24,('visible joint termination',sx,sz,y,kind,distance);end_cover.append(dict(side=[sx,sz],y=y+dy,kind=kind,cover=.30-distance))
probes=[]
for s in specs:
 name=s['target'];p=np.array(s['p'],float);n=np.array(s['n'],float);n/=np.linalg.norm(n);t=np.array(s['t'],float);t/=np.linalg.norm(t);old=ray41(uncut[name],p+.08*n,-n);new=ray41(after[name],p+.08*n,-n);depth=new-old;assert abs(depth-.020)<.0015,(s['label'],'depth',depth)
 widths=[]
 for x in np.linspace(-.035,.035,281):
  q=p+x*t+.08*n;delta=ray41(after[name],q,-n)-ray41(uncut[name],q,-n)
  if delta>.00001:widths.append(float(x))
 assert widths;w=max(widths)-min(widths);assert abs(w-.045)<.004,(s['label'],'width',w)
 # The deliberately uncut source fails this same depth requirement.
 assert abs((old-old)-.020)>.0015
 probes.append(dict(label=s['label'],depth=depth,opening_width_above_ten_micrometer_depth=w,uncut_source_rejected=True))
# Actual inner hit surfaces and remaining backing remain intact.
interior=[]
for name,p,n,expected in [(targets[0],[0,1,0],[0,-1,0],3.0175),(targets[1],[0,0,0],[0,1,0],2.14825),(targets[0],[0,-1,0],[1,0,0],2.33),(targets[0],[0,-1,0],[0,0,1],1.38),(targets[1],[0,1,0],[1,0,0],2.38)]:
 a=ray41(uncut[name],p,n);b=ray41(after[name],p,n);assert abs(a-b)<1e-6 and abs(b-expected)<1e-5,(name,'inner surface changed',a,b,expected);interior.append(dict(name=name,origin=p,direction=n,distance=b))
# Retained old surface samples away from the cutter slabs include all interior walls.
retained={}
for name in targets:
 old=uncut[name];current=after[name];tri=old['v'][old['t']];field=source_field36([current]);points=np.vstack([tri.mean(1),old['v']]);matched=0
 for p in points:
  local=local38([p])[0];nearcut=False
  for s in specs:
   if s['target']!=name:continue
   rel=local-np.array(s['p'],float);n=np.array(s['n'],float);n/=np.linalg.norm(n);t=np.array(s['t'],float);t/=np.linalg.norm(t)
   if abs(rel@t)<.07 and -.025<rel@n<.04:nearcut=True;break
  if nearcut:continue
  near=near36(field,p,.0008);assert near,(name,'retained original surface missing',local.tolist());matched+=1
 retained[name]=matched
rows=[];packed={};unchanged=0;whole=[]
for i,ob in enumerate(objects):
 d=capture36(ob);proof=topology36(ob);assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7
 if ob.name not in targets:
  for key in ('vertex_hash','triangle_hash','normal_hash','materials'):assert d[key]==before[ob.name][key],(ob.name,'unrelated change',key)
  unchanged+=1
 rows.append(dict(name=ob.name,changed=ob.name in targets,**proof));whole.append(d['v']);packed[f'part{i}_v']=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];packed[f'part{i}_t']=d['t']
assert unchanged==153
for k in ('vertex_hash','triangle_hash','normal_hash'):assert capture36(sc.objects['Chest Removable Crank Key'])[k]==keybefore[k]
total=sum(x['triangles'] for x in rows);V=np.vstack(whole);app=np.c_[V[:,0],V[:,2],-V[:,1]];turn=float(2*np.linalg.norm(app[:,[0,2]],axis=1).max());assert total<=185000 and turn<=6.7 and app[:,1].min()>=-2.895 and app[:,1].max()<=3.015
for rel,sha in frozen.items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha,rel
np.savez_compressed(C/'geometry.npz',**packed);result=dict(stage='Broader neutral wood planks, motion and visual review pending',complete_badge=False,meshes=155,total_triangles=total,unchanged_meshes=unchanged,roof_staves=D['roof_staves'],body_joints=D['body_levels'],end_joints=D['end_levels'],maximum_rotational_width=turn,checks=rows);(C/'validation.json').write_text(json.dumps(result,indent=2));(C/'board_joint_proof.json').write_text(json.dumps(dict(specs=specs,stages=stages,normal_fields=normalproof,actual_profile_probes=probes,joint_end_cover=end_cover,inner_rays=interior,retained_old_surface_samples=retained,metal_finish_changed=False,wood_grain_added=False,full_motion_pending=True),indent=2));shutil.copy2(B/'inspection_ownership.json',C/'inspection_ownership.json');shutil.copy2(B/'rig_stage.json',C/'rig_stage.json');(C/'source').mkdir(exist_ok=True)
for f in ('board42_live.py','frame36_geometry.py','hinge38_geometry.py'):shutil.copy2(P/'tools'/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
