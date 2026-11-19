import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate36';sc=bpy.context.scene
exec(compile((P/'tools/frame36_geometry.py').read_text(),'frame36_geometry.py','exec'))
groups=json.loads((C/'groups.json').read_text());old_manifest=json.loads((C/'before_manifest.json').read_text());source=np.load(C/'source_fields.npz');targets=np.load(C/'normal_targets.npz');stage=json.loads((C/'frame_stage.json').read_text());old35=np.load(P/'candidate35/geometry.npz');old35_meta=json.loads((P/'candidate35/validation.json').read_text())['checks'];old35_index={r['name']:i for i,r in enumerate(old35_meta)};changed={g['target'] for g in groups};hidden={n for g in groups for n in g['operands']};assert len(changed)==2 and len(hidden)==12
for name in hidden:
 o=sc.objects[name];d=capture36(o);assert not o.get('full_form') and o.hide_render and o.hide_get(),(name,'old overlap still visible')
 for key in ('vertex_hash','triangle_hash','normal_hash'):assert d[key]==old_manifest[name][key],(name,'source operand modified')
visible=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(visible)==147
rows=[];allv=[];total=0;packed={};unchanged=0
for i,o in enumerate(visible):
 d=capture36(o);allv.append(d['v']);total+=len(d['t']);assert np.max(abs(np.array(o.matrix_world)-np.eye(4)))<1e-7,(o.name,'rest matrix changed');assert not o.hide_render;app=np.c_[d['v'][:,0],d['v'][:,2],-d['v'][:,1]];packed[f'part{i}_v']=app;packed[f'part{i}_t']=d['t']
 if o.name not in changed:
  for key in ('vertex_hash','triangle_hash','normal_hash'):assert d[key]==old_manifest[o.name][key],(o.name,'unrelated data changed')
  unchanged+=1;rows.append(dict(name=o.name,unchanged=True,triangles=len(d['t'])));continue
 g=next(g for g in groups if g['target']==o.name);proof=topology36(o);assert proof['euler']==g['expected_euler'],(o.name,'wrong openings',proof['euler']);assert len(o.data.materials)==1 and o.data.materials[0] is not None and all(p.material_index==0 for p in o.data.polygons)
 tv=source[o.name+' v'];tt=source[o.name+' t'];tree=BVHTree.FromPolygons(tv.tolist(),tt.tolist(),all_triangles=True,epsilon=0);maximum=0;oldtri=tv[tt];GG=np.cross(oldtri[:,1]-oldtri[:,0],oldtri[:,2]-oldtri[:,0]);GG/=np.linalg.norm(GG,axis=1)[:,None];distance_field=dict(tri=oldtri,geom=GG,index=index36(oldtri))
 for p in np.vstack([d['v'],d['v'][d['t']].mean(1)]):
  hits=near36(distance_field,p,.0008);assert hits,(o.name,'new exterior differs from actual double precision original surface',p.tolist());distance=min(h[3] for h in hits);assert distance<=.0008,(o.name,'new exterior differs',distance);maximum=max(maximum,distance)
 n=d['n'];t=targets[o.name];assert n.shape==t.shape;den=np.linalg.norm(n,axis=1)*np.linalg.norm(t,axis=1);angle=float(np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',n,t)/den,-1,1))).max());assert angle<.75,(o.name,'normal field changed',angle)
 # The union must retain actual volume, including each protruding operand.
 old_parts=[]
 for name in [g['target']]+g['operands']:
  j=old35_index[name];av=old35[f'part{j}_v'];a={'v':np.c_[av[:,0],-av[:,2],av[:,1]],'t':old35[f'part{j}_t']}
  tr=BVHTree.FromPolygons(a['v'].tolist(),a['t'].tolist(),all_triangles=True,epsilon=0);old_parts.append((name,a,tr))
 newtree=BVHTree.FromPolygons(d['v'].tolist(),d['t'].tolist(),all_triangles=True,epsilon=0);witnesses=[]
 for name,a,tr in old_parts[1:]:
  tri=a['v'][a['t']];geom=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);geom/=np.linalg.norm(geom,axis=1)[:,None];found=None
  for k in range(0,len(tri),max(1,len(tri)//200)):
   p=tri[k].mean(0)-geom[k]*.004
   if not inside36(tr,p):continue
   if inside36(old_parts[0][2],p):continue
   if min(float(x[2].find_nearest(Vector(p))[3]) for x in old_parts)<.0005:continue
   assert inside36(newtree,p),(o.name,'hidden operand not really joined',name,p.tolist());found=p.tolist();break
  assert found is not None,(o.name,'no outside witness for operand',name);witnesses.append(dict(operand=name,point=found,inside_union=True,outside_original_band=True))
 rng=np.random.default_rng(3601);low=tv.min(0);high=tv.max(0);tested=0;inside_count=0
 for p in rng.uniform(low,high,(800,3)):
  if min(float(x[2].find_nearest(Vector(p))[3]) for x in old_parts)<.001 or float(newtree.find_nearest(Vector(p))[3])<.001:continue
  was=any(inside36(tr,p) for _,_,tr in old_parts);now=inside36(newtree,p);assert was==now,(o.name,'union membership changed',p.tolist(),was,now);tested+=1;inside_count+=int(now)
 assert tested>500 and inside_count>10,(o.name,'weak membership coverage',tested,inside_count)
 proof.update(name=o.name,maximum_exterior_surface_error=maximum,maximum_normal_encoding_degrees=angle,retained_operand_witnesses=witnesses,membership_samples=tested,inside_samples=inside_count,materials_preserved=True);rows.append(proof)
assert unchanged==145
inventory={'CAVITY35_INVENTORY_OUTPUT':'intrusion_inventory_after.json'};code=(P/'tools/cavity35_inventory_live.py').read_text().replace("C=P/'candidate35'","C=P/'candidate36'");exec(compile(code,'actual_cavity_inventory36.py','exec'),inventory);assert not inventory['rows'],('Frame enters empty cavity',inventory['rows'])
V=np.vstack(allv);app=np.c_[V[:,0],V[:,2],-V[:,1]];turn=float(2*np.linalg.norm(app[:,[0,2]],axis=1).max());assert turn<=6.7 and app[:,1].min()>=-2.895 and app[:,1].max()<=3.015 and total<180000
for rel,sha in json.loads((C/'baseline35_hashes.json').read_text()).items():assert hashlib.sha256((P/'candidate35'/rel).read_bytes()).hexdigest()==sha,'Frozen35 changed '+rel
oldroles=json.loads((P/'candidate35/inspection_ownership.json').read_text())['parts'];roles={o.name:oldroles[o.name] for o in visible};(C/'inspection_ownership.json').write_text(json.dumps(dict(parts=roles,counts={r:list(roles.values()).count(r) for r in ('body','lid','hasp')},purpose='Actual welded frames, same rigid ownership, no lid opening rig yet.'),indent=2)+'\n')
result=dict(phase='continuous metal frames',complete_badge=False,meshes=147,total_triangles=total,bounds=[app.min(0).tolist(),app.max(0).tolist()],maximum_rotational_width=turn,unchanged_meshes=145,hidden_old_frame_parts=sorted(hidden),hardware_intrusions=0,checks=rows,baseline35_files_unchanged=True);(C/'validation.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(C/'geometry.npz',**packed);print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
