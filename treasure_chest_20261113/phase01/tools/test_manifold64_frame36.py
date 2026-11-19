import sys,json,time
from pathlib import Path
import numpy as np
sys.path.insert(0,'/private/tmp/chest_manifold_deps')
import manifold3d as m
R=Path(__file__).resolve().parents[2];P=R/'phase01';C=P/'candidate36';old=np.load(P/'candidate35/geometry.npz');rows=json.loads((P/'candidate35/validation.json').read_text())['checks'];lookup={r['name']:i for i,r in enumerate(rows)};groups=json.loads((C/'groups.json').read_text());report={}
for g in groups:
 parts=[];inputs=[]
 for name in [g['target']]+g['operands']:
  i=lookup[name];a=old[f'part{i}_v'];v=np.ascontiguousarray(np.c_[a[:,0],-a[:,2],a[:,1]],dtype=np.float64);t=np.ascontiguousarray(old[f'part{i}_t'],dtype=np.uint64);msh=m.Manifold(m.Mesh64(v,t,face_id=np.arange(len(t),dtype=np.uint64)));assert msh.status()==m.Error.NoError,(name,msh.status());parts.append(msh);inputs.append(dict(name=name,triangles=msh.num_tri(),volume=msh.volume(),tolerance=msh.get_tolerance()))
 start=time.time();union=m.Manifold.batch_boolean(parts,m.OpType.Add);assert union.status()==m.Error.NoError,(g['target'],union.status());out=union.to_mesh64();v=np.array(out.vert_properties[:,:3]);t=np.array(out.tri_verts,dtype=np.int64);edges,counts=np.unique(np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);areas=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)/2
 key='body' if 'Body' in g['target'] else 'lid';np.savez_compressed(C/f'manifold64_{key}.npz',v=v,t=t)
 report[g['target']]=dict(inputs=inputs,seconds=time.time()-start,closed=bool((counts==2).all()),euler=int(len(v)-len(edges)+len(t)),genus=union.genus(),triangles=len(t),vertices=len(v),minimum_area=float(areas.min()),below_old_area_gate=int((areas<=1e-10).sum()),volume=union.volume(),tolerance=union.get_tolerance());(C/'manifold64_test.json').write_text(json.dumps(report,indent=2));print(key,report[g['target']])
